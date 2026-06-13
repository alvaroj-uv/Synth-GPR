#!/usr/bin/env python3
"""
Bayesian Optimization calibration — round 3.

Warm-starts from the 150 LHS evaluations (dzt_calib_geo) and uses a Gaussian
Process surrogate to intelligently explore the 7D geometry parameter space.

Rationale: LHS is space-filling but wastes evaluations in bad regions. BO
concentrates evaluations near the current best, progressively refining the
surrogate until the acquisition function (Expected Improvement) finds no
further gain.

Same physics as dzt_calib_geo.py:
  - Pinned bulk permittivities (clean=3.45, fouled=11.3) via sqrt-CRIM
  - Rock eps co-solved from clean porosity
  - Fines matrix via Peplinski (water solved from CRIM target)
  - H(f) system response correction
  - Real-dt resampling
  - Fitness = RMS z-score on 8 coda/attenuation features

Stages:
    python scripts/experiments/dzt_calib_bayesopt.py --warmstart   # load LHS history
    python scripts/experiments/dzt_calib_bayesopt.py --iterate N   # run N BO iterations
    python scripts/experiments/dzt_calib_bayesopt.py --analyze     # results summary
"""

import argparse
import importlib.util
import json
import subprocess
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT))

# Import the geo calibration module for its build_candidate, pinned solves, etc.
_spec_geo = importlib.util.spec_from_file_location(
    "dzt_calib_geo", ROOT / "scripts" / "experiments" / "dzt_calib_geo.py")
geo = importlib.util.module_from_spec(_spec_geo)
_spec_geo.loader.exec_module(geo)

# Import the POC module for load_out, resample, system response, features
_spec_poc = importlib.util.spec_from_file_location(
    "dzt_calib_poc", ROOT / "scripts" / "experiments" / "dzt_calib_poc.py")
poc = importlib.util.module_from_spec(_spec_poc)
_spec_poc.loader.exec_module(poc)

OUT_DIR = ROOT / "output" / "dzt_calib_bayesopt"
SIM_DIR = Path("D:/gprMax/user_models/dzt_calib_geo")  # reuse same sim dir

# Same parameter space as geo (7D)
PARAM_NAMES = list(geo.PARAM_SPACE.keys())
PARAM_BOUNDS = [(lo, hi) for lo, hi, _ in geo.PARAM_SPACE.values()]

# Template seeds — use same 5 seeds for per-candidate averaging
TEMPLATE_SEEDS = geo.TEMPLATE_SEEDS

# BO configuration — mutable dict so CLI overrides work without global decl issues
BO_SEED = 42
BO_CFG = {
    "kappa": 1.96,       # UCB exploration weight; lower = more exploitation
    "xi": 0.01,          # EI/PI jitter for exploration
    "acq_func": "EI",    # "EI" (Expected Improvement) or "LCB" (Lower Confidence Bound)
}
N_INITIAL_RANDOM = 0  # 0 because we warm-start from LHS


def load_target():
    """Load the real target features and spread (from POC output)."""
    tgt = json.loads((poc.OUT_DIR / "target_features.json").read_text())
    feats = list(tgt["features"].keys())
    t_vec = np.array([tgt["features"][k] for k in feats])
    s_vec = np.array([tgt["spread_mad"][k] for k in feats])
    return feats, t_vec, s_vec


def evaluate_candidate(cand_name: str, params: dict, feats: list,
                       t_vec: np.ndarray, s_vec: np.ndarray,
                       run_sim: bool = True) -> float:
    """Build, run, and evaluate a single BO candidate (averaged over template seeds).

    Returns the fitness (RMS z-score), or np.inf on failure.
    """
    fitness_values = []

    for si, seed in enumerate(TEMPLATE_SEEDS):
        sim_name = f"{cand_name}_s{si}"
        in_path = SIM_DIR / f"{sim_name}.in"
        out_path = SIM_DIR / f"{sim_name}.out"

        # Build the .in file
        tpl_path = SIM_DIR / f"tpl_{seed}.in"
        if not tpl_path.exists():
            print(f"  [WARN] template tpl_{seed}.in missing, skipping seed {si}")
            continue

        try:
            meta = geo.build_candidate(
                tpl_path, in_path, params,
                cand_seed=seed * 1000 + int(cand_name.replace("bo", "")))
        except Exception as e:
            print(f"  [WARN] build_candidate failed for {sim_name}: {e}")
            continue

        # Run gprMax if needed
        if run_sim and not out_path.exists():
            res = subprocess.run(
                [poc.GPRMAX_PY, "-m", "gprMax", str(in_path), "-n", "1"],
                capture_output=True, text=True, cwd=str(SIM_DIR))
            if not out_path.exists():
                print(f"  [FAIL] {sim_name}: gprMax did not produce output")
                if res.stderr:
                    print(f"         {res.stderr[-200:]}")
                continue

        if not out_path.exists():
            continue

        # Extract features and compute fitness
        try:
            ez, dt = poc.load_out(out_path)
            sig, dt_rs = poc.resample_to_real(ez, dt)
            sig = poc.apply_system_response(sig, dt_rs)
            fdict = poc.extract_fitness_feats(poc.prep_trace(sig), dt_rs, sim_name)
            if set(feats) - set(fdict):
                continue
            z = (np.array([fdict[k] for k in feats]) - t_vec) / s_vec
            fitness_values.append(float(np.sqrt(np.mean(z ** 2))))
        except Exception as e:
            print(f"  [WARN] feature extraction failed for {sim_name}: {e}")
            continue

    if not fitness_values:
        return np.inf

    return float(np.mean(fitness_values))


# ---------------------------------------------------------------- warm-start
def warmstart() -> None:
    """Load the existing LHS results from geo and format for BO warm-start."""
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    agg_path = geo.OUT_DIR / "geo_results_agg.csv"
    if not agg_path.exists():
        print(f"[ERROR] No LHS results at {agg_path}. Run dzt_calib_geo --analyze first.")
        return

    agg = pd.read_csv(agg_path)
    # The agg file has 'cand' as index after groupby; handle both cases
    if "cand" not in agg.columns:
        agg = agg.reset_index()

    rows = []
    for _, r in agg.iterrows():
        row = {"cand": r["cand"], "source": "lhs"}
        for p in PARAM_NAMES:
            row[p] = float(r[p])
        row["fitness"] = float(r["fitness"])
        rows.append(row)

    df = pd.DataFrame(rows)
    df.to_csv(OUT_DIR / "bo_history.csv", index=False)

    print(f"Warm-start: loaded {len(df)} LHS evaluations from geo sweep")
    print(f"  Best LHS fitness: {df['fitness'].min():.4f} ({df.loc[df['fitness'].idxmin(), 'cand']})")
    print(f"  Mean fitness: {df['fitness'].mean():.2f}")
    print(f"  Parameter bounds:")
    for name, (lo, hi) in zip(PARAM_NAMES, PARAM_BOUNDS):
        print(f"    {name:12s}: [{lo:.3f}, {hi:.3f}]")
    print(f"\nHistory saved to {OUT_DIR / 'bo_history.csv'}")


# ---------------------------------------------------------------- BO iterate
def iterate(n_iter: int) -> None:
    """Run n_iter Bayesian Optimization iterations."""
    from skopt import Optimizer
    from skopt.space import Real

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    hist_path = OUT_DIR / "bo_history.csv"
    if not hist_path.exists():
        print("[ERROR] No bo_history.csv. Run --warmstart first.")
        return

    history = pd.read_csv(hist_path)
    feats, t_vec, s_vec = load_target()

    # Build the search space
    space = [Real(lo, hi, name=name) for name, (lo, hi) in zip(PARAM_NAMES, PARAM_BOUNDS)]

    # Create optimizer with a Matérn 5/2 GP
    opt = Optimizer(
        dimensions=space,
        base_estimator="GP",         # Gaussian Process with Matérn kernel
        acq_func=BO_CFG["acq_func"],
        acq_func_kwargs={"xi": BO_CFG["xi"], "kappa": BO_CFG["kappa"]},
        n_initial_points=0,          # we warm-start, no random points
        random_state=BO_SEED,
    )

    # Tell the optimizer about all previous evaluations
    X_init = history[PARAM_NAMES].values.tolist()
    y_init = history["fitness"].values.tolist()
    opt.tell(X_init, y_init)

    best_so_far = min(y_init)
    bo_start_idx = len(history)
    print(f"\nBO starting from {len(history)} evaluations, best={best_so_far:.4f}")
    print(f"Running {n_iter} BO iterations (each = 5 gprMax sims)...\n")

    t0 = time.time()
    new_rows = []

    for i in range(n_iter):
        # Ask the GP for the next point to evaluate
        x_next = opt.ask()
        params = {name: float(val) for name, val in zip(PARAM_NAMES, x_next)}
        cand_name = f"bo{bo_start_idx + i:03d}"

        print(f"[BO iter {i+1}/{n_iter}] {cand_name}: "
              f"h_clean={params['h_clean']:.3f} h_foul={params['h_foul']:.3f} "
              f"rf_fouled={params['rf_fouled']:.3f} frac_dim={params['frac_dim']:.2f} "
              f"rough_amp={params['rough_amp']:.4f} trans_th={params['trans_th']:.3f} "
              f"clean_phi={params['clean_phi']:.3f}")

        fitness = evaluate_candidate(cand_name, params, feats, t_vec, s_vec)

        # Tell the optimizer the result
        opt.tell([x_next], [fitness])

        marker = ""
        if fitness < best_so_far:
            best_so_far = fitness
            marker = " ** NEW BEST **"
        elapsed = time.time() - t0
        eta = elapsed / (i + 1) * (n_iter - i - 1)
        print(f"  -> fitness={fitness:.4f}{marker}  "
              f"(best={best_so_far:.4f}, {elapsed/60:.1f}min, ETA {eta/60:.0f}min)\n")

        row = {"cand": cand_name, "source": "bo", **params, "fitness": fitness}
        new_rows.append(row)

        # Save incrementally in case of interruption
        updated = pd.concat([history, pd.DataFrame(new_rows)], ignore_index=True)
        updated.to_csv(hist_path, index=False)

    print(f"\n{'='*60}")
    print(f"BO complete: {n_iter} iterations in {(time.time()-t0)/60:.1f} min")
    print(f"Best fitness: {best_so_far:.4f}")

    # Show the GP's predicted optimum
    result = opt.get_result()
    print(f"\nGP-predicted optimum (acquisition minimum):")
    for name, val in zip(PARAM_NAMES, result.x):
        print(f"  {name:12s}: {val:.4f}")
    print(f"  GP-predicted fitness: {result.fun:.4f}")

    # Save the GP model for later analysis
    import pickle
    with open(OUT_DIR / "bo_optimizer.pkl", "wb") as f:
        pickle.dump(opt, f)
    print(f"\nOptimizer state saved to {OUT_DIR / 'bo_optimizer.pkl'}")


# ---------------------------------------------------------------- analyze
def analyze() -> None:
    """Analyze the full BO history and compare to LHS baseline."""
    hist_path = OUT_DIR / "bo_history.csv"
    if not hist_path.exists():
        print("[ERROR] No bo_history.csv found.")
        return

    history = pd.read_csv(hist_path)
    feats, t_vec, s_vec = load_target()

    lhs_df = history[history["source"] == "lhs"]
    bo_df = history[history["source"] == "bo"]

    print(f"{'='*72}")
    print(f"Bayesian Optimization Calibration — Analysis")
    print(f"{'='*72}")
    print(f"\nTotal evaluations: {len(history)} (LHS: {len(lhs_df)}, BO: {len(bo_df)})")

    # Overall best
    best_idx = history["fitness"].idxmin()
    best = history.iloc[best_idx]
    print(f"\nOverall best: {best['cand']} (source={best['source']}, fitness={best['fitness']:.4f})")
    for p in PARAM_NAMES:
        print(f"  {p:12s}: {best[p]:.4f}")

    # Best from each source
    if len(lhs_df) > 0:
        lhs_best = lhs_df.loc[lhs_df["fitness"].idxmin()]
        print(f"\nBest LHS:  {lhs_best['cand']} fitness={lhs_best['fitness']:.4f}")
    if len(bo_df) > 0:
        bo_best = bo_df.loc[bo_df["fitness"].idxmin()]
        print(f"Best BO:   {bo_best['cand']} fitness={bo_best['fitness']:.4f}")
        improvement = ((lhs_best['fitness'] - bo_best['fitness']) / lhs_best['fitness']) * 100
        print(f"BO improvement over LHS: {improvement:+.1f}%")

    # Convergence trace
    cummin = history["fitness"].cummin()
    print(f"\nConvergence trace (cumulative best):")
    milestones = [0, 10, 30, 50, 100, len(history)-1]
    for m in milestones:
        if m < len(cummin):
            src = history.iloc[m]["source"]
            print(f"  eval {m+1:3d}: best={cummin.iloc[m]:.4f} (source={src})")

    # Per-feature z-scores for the overall best
    print(f"\nPer-feature analysis for best candidate ({best['cand']}):")
    best_params = {p: float(best[p]) for p in PARAM_NAMES}

    # Re-evaluate features for the best candidate (load from sim outputs)
    all_z = []
    for si, seed in enumerate(TEMPLATE_SEEDS):
        sim_name = f"{best['cand']}_s{si}"
        out_path = SIM_DIR / f"{sim_name}.out"
        if not out_path.exists():
            continue
        try:
            ez, dt = poc.load_out(out_path)
            sig, dt_rs = poc.resample_to_real(ez, dt)
            sig = poc.apply_system_response(sig, dt_rs)
            fdict = poc.extract_fitness_feats(poc.prep_trace(sig), dt_rs, sim_name)
            z = np.array([(fdict[k] - t_vec[j]) / s_vec[j]
                          for j, k in enumerate(feats) if k in fdict])
            all_z.append(z)
        except Exception:
            continue

    if all_z:
        z_mean = np.mean(all_z, axis=0)
        z_std = np.std(all_z, axis=0)
        for j, k in enumerate(feats):
            status = "[OK]" if abs(z_mean[j]) < 2.0 else "[X]"
            print(f"  {status} {k:30s} z={z_mean[j]:+6.2f} +/- {z_std[j]:.2f}")
        n_good = sum(abs(z) < 2.0 for z in z_mean)
        print(f"\n  {n_good}/{len(feats)} features within ±2σ of target")

    # Parameter sensitivity from GP model
    gp_path = OUT_DIR / "bo_optimizer.pkl"
    if gp_path.exists():
        import pickle
        with open(gp_path, "rb") as f:
            opt = pickle.load(f)
        if hasattr(opt, 'models') and opt.models:
            model = opt.models[-1]
            if hasattr(model, 'kernel_'):
                print(f"\nGP kernel: {model.kernel_}")
            # Compute parameter importance via GP lengthscales
            try:
                ls = np.exp(model.kernel_.theta[:len(PARAM_NAMES)])
                importance = 1.0 / ls
                importance = importance / importance.sum()
                print(f"\nGP lengthscale-based importance:")
                for name, imp in sorted(zip(PARAM_NAMES, importance),
                                        key=lambda x: -x[1]):
                    bar = "#" * int(imp * 40)
                    print(f"  {name:12s}: {imp:.3f} {bar}")
            except Exception:
                pass

    # Save analysis summary
    summary = {
        "total_evaluations": int(len(history)),
        "lhs_evaluations": int(len(lhs_df)),
        "bo_evaluations": int(len(bo_df)),
        "best_candidate": str(best["cand"]),
        "best_fitness": float(best["fitness"]),
        "best_source": str(best["source"]),
        "best_params": best_params,
    }
    (OUT_DIR / "bo_summary.json").write_text(json.dumps(summary, indent=2))
    print(f"\nSummary saved to {OUT_DIR / 'bo_summary.json'}")


# ------------------------------------------------------------------- main
def main():
    ap = argparse.ArgumentParser(
        description="Bayesian Optimization calibration (warm-start from LHS)")
    ap.add_argument("--warmstart", action="store_true",
                    help="Load LHS history into BO format")
    ap.add_argument("--iterate", type=int, metavar="N",
                    help="Run N BO iterations")
    ap.add_argument("--analyze", action="store_true",
                    help="Analyze results and compare to LHS")
    ap.add_argument("--acq", choices=["EI", "LCB", "PI"], default=BO_CFG["acq_func"],
                    help=f"Acquisition function (default: {BO_CFG['acq_func']})")
    ap.add_argument("--kappa", type=float, default=BO_CFG["kappa"],
                    help=f"LCB exploration weight (default: {BO_CFG['kappa']})")
    ap.add_argument("--xi", type=float, default=BO_CFG["xi"],
                    help=f"EI/PI jitter (default: {BO_CFG['xi']})")
    a = ap.parse_args()

    BO_CFG["acq_func"] = a.acq
    BO_CFG["kappa"] = a.kappa
    BO_CFG["xi"] = a.xi

    if a.warmstart:
        warmstart()
    elif a.iterate:
        iterate(a.iterate)
    elif a.analyze:
        analyze()
    else:
        print("Usage:")
        print("  --warmstart          Load LHS results")
        print("  --iterate N          Run N BO iterations")
        print("  --analyze            Results summary")
        print("  --acq EI|LCB|PI     Acquisition function")
        print("  --kappa 1.96        LCB exploration weight")
        print("  --xi 0.01           EI/PI jitter")


if __name__ == "__main__":
    main()
