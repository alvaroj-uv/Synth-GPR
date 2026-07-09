"""
hypothesis_harness.py — Evaluation backbone for the Synth-GPR sim-to-real thesis.

This module is the missing ML/evaluation layer. It does NOT train a "best"
classifier; it is a *measurement instrument* for the three hypotheses:

    H1  proportion of synthetic data  (two-arm: substitution vs. additive)
    H2  physical causes of the shift  (feeds a sensitivity study; distances here)
    H3  descriptor-family robustness  (time vs. freq vs. time-frequency)

The four validity guards are invariants of the code, not comments:

    (1) Spatial leakage        -> ALL splits are GroupKFold over `group`
                                  (track segment for real, scene/seed id for sim).
                                  There is no code path that splits by row.
    (2) Circularity            -> the harness refuses to run if a feature column
                                  equals a raw material parameter (eps/sigma/pvc).
                                  Labels must come from the deterioration cause,
                                  features from the waveform. See _guard_no_param_leak.
    (3) Capacity confound (H3) -> families are compared at EQUAL effective
                                  dimensionality (PCA to a common k) with the SAME
                                  downstream classifier. See evaluate_families.
    (4) Substitution confound  -> H1 exposes both arms explicitly so a drop at
                                  constant N ("real is scarce") is never misread as
                                  "synthetic contaminates". See h1_mixing_curve.

Metric: macro one-vs-rest ROC-AUC. Chosen because RF/XGBoost scores are poorly
calibrated by default and AUC is immune to miscalibration and to the cross-domain
calibration shift that would otherwise contaminate H2.

Expected input: a single tidy table (parquet/csv) with columns
    <feature columns...> | label | domain | group | fidelity_level | <acq params...>
where domain in {"real","sim"}, group is the leakage-safe grouping key, and
label is the fouling class (CL/MC/MF/F/HF). Build this with the assembler
(step 1 of the plan); this harness consumes it.
"""
from __future__ import annotations

import warnings
from dataclasses import dataclass, field

import numpy as np
import pandas as pd
from sklearn.decomposition import PCA
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import GroupKFold
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

# ---------------------------------------------------------------------------
# Descriptor families — matched to the ACTUAL feature keys in
# src/feature_extraction.py. Time-domain stats are UNPREFIXED, so they need an
# explicit allowlist; matching on a prefix like "mean" would wrongly swallow
# the frequency feature "mean_frequency". This is the trap the code prevents.
# ---------------------------------------------------------------------------
TIME_KEYS = {
    "mean", "root_mean_square", "standard_deviation", "median", "skewness",
    "kurtosis_value", "peak_max", "peak_min", "peak_count", "peak_mean_height",
    "crest_factor", "number_zeros", "area_signal", "second_derivative",
}
# Hilbert is an envelope descriptor: temporal in nature. Kept as its own family
# so H3 can report it separately (envelope is the first robustness rung).
HILBERT_PREFIXES = ("hilbert_", "area_hilbert")
FREQ_KEYS = {
    "area_fourier", "bandwidth", "dominant_energy_fraction", "dominant_frequency",
    "fourier_peak_max", "fourier_standard_deviation", "high_low_energy_ratio",
    "high_mid_energy_ratio", "mean_frequency", "median_frequency",
    "mid_low_energy_ratio", "spectral_entropy", "spectral_flatness",
    "spectral_kurtosis", "spectral_rolloff", "spectral_skewness", "spectral_slope",
}
STFT_PREFIXES = ("stft_", "att_band_", "energy_", "att_")
# Legacy grid/slice blocks are amplitude images of the direct pulse. Excluded
# from H3 by default (they are neither cleanly temporal nor time-frequency and
# leak acquisition-specific direct-wave shape). Opt in explicitly if needed.
LEGACY_PREFIXES = ("grid_", "slice_", "decile_")

RESERVED = {"label", "domain", "group", "fidelity_level"}
# Any column whose name matches these is a raw medium/deterioration parameter and
# must NOT be used as a feature (circularity guard).
PARAM_TOKENS = ("eps", "epsilon", "permittiv", "sigma", "conduct", "pvc", "fi_",
                "fouling_index", "moisture", "theta_")


def assign_families(columns) -> dict[str, list[str]]:
    """Partition feature columns into descriptor families, validating coverage."""
    fam: dict[str, list[str]] = {"time": [], "hilbert": [], "freq": [],
                                 "timefreq": [], "legacy": [], "unassigned": []}
    for c in columns:
        if c in RESERVED:
            continue
        if c in TIME_KEYS:
            fam["time"].append(c)
        elif c.startswith(HILBERT_PREFIXES):
            fam["hilbert"].append(c)
        elif c in FREQ_KEYS:
            fam["freq"].append(c)
        elif c.startswith(STFT_PREFIXES):
            fam["timefreq"].append(c)
        elif c.startswith(LEGACY_PREFIXES):
            fam["legacy"].append(c)
        else:
            fam["unassigned"].append(c)
    if fam["unassigned"]:
        warnings.warn(
            f"{len(fam['unassigned'])} columns not assigned to any family "
            f"(first few: {fam['unassigned'][:5]}). Update the family map before "
            "trusting H3 — silent misassignment is exactly the capacity confound.",
            stacklevel=2,
        )
    return fam


def _guard_no_param_leak(feature_cols) -> None:
    """Circularity guard: refuse to treat raw medium parameters as features."""
    offenders = [c for c in feature_cols
                 if any(tok in c.lower() for tok in PARAM_TOKENS)]
    if offenders:
        raise ValueError(
            "Circularity guard tripped. These look like raw medium/deterioration "
            f"parameters, not waveform features: {offenders}. If the label is a "
            "function of these, the classifier would be reading the answer. Drop "
            "them, or if you deliberately want 'inverted parameters as descriptors' "
            "(the max-physical rung of H3), pass them through a separate inversion "
            "step so they come from the waveform, not the ground truth."
        )


def _make_clf(random_state: int) -> RandomForestClassifier:
    # Deliberate: a stable, well-understood classifier as a measurement platform,
    # not a tuned champion. Swap for XGBoost by editing here only — the harness
    # contract (fit/predict_proba) is identical.
    return RandomForestClassifier(
        n_estimators=400, max_features="sqrt", class_weight="balanced",
        n_jobs=-1, random_state=random_state,
    )


def _macro_auc(y_true, proba, classes) -> float:
    # One-vs-rest macro AUC; robust to class imbalance and to miscalibration.
    try:
        return roc_auc_score(
            pd.get_dummies(pd.Categorical(y_true, categories=classes)).values,
            proba, average="macro", multi_class="ovr",
        )
    except ValueError:
        return np.nan  # a fold missing a class; caller aggregates with nanmean


@dataclass
class EvalResult:
    label: str
    auc_mean: float
    auc_std: float
    n_dims: int
    per_fold: list[float] = field(default_factory=list)


def _cv_auc(X, y, groups, n_dims=None, n_splits=5, seed=0) -> EvalResult:
    """GroupKFold AUC. If n_dims is set, PCA-reduce to that many dims first
    (capacity matching for H3). The scaler+PCA are fit INSIDE each fold to avoid
    leakage across the split."""
    classes = sorted(pd.unique(y))
    gkf = GroupKFold(n_splits=n_splits)
    aucs = []
    for tr, te in gkf.split(X, y, groups):
        steps = [("scale", StandardScaler())]
        if n_dims is not None and n_dims < X.shape[1]:
            steps.append(("pca", PCA(n_components=n_dims, random_state=seed)))
        steps.append(("clf", _make_clf(seed)))
        pipe = Pipeline(steps)
        pipe.fit(X[tr], y[tr])
        proba = pipe.predict_proba(X[te])
        aucs.append(_macro_auc(y[te], proba, pipe.classes_))
    a = np.array(aucs, float)
    return EvalResult("", float(np.nanmean(a)), float(np.nanstd(a)),
                      X.shape[1] if n_dims is None else min(n_dims, X.shape[1]),
                      a.tolist())


# ---------------------------------------------------------------------------
# H3 — descriptor families at equal effective dimensionality
# ---------------------------------------------------------------------------
def evaluate_families(df: pd.DataFrame, families=("time", "hilbert", "freq", "timefreq"),
                      match_dims=True, n_splits=5, seed=0) -> pd.DataFrame:
    """Compare descriptor families with capacity matched (guard 3) and leakage-safe
    splits (guard 1). Reports in-domain AUC and the TSTR robustness R side by side —
    a family can be invariant yet uninformative, so both are shown."""
    fam_cols = assign_families(df.columns)
    chosen = {f: fam_cols[f] for f in families}
    for cols in chosen.values():
        _guard_no_param_leak(cols)
    common_k = min(len(c) for c in chosen.values()) if match_dims else None

    rows = []
    for fam, cols in chosen.items():
        Xr = df.loc[df.domain == "real", cols].to_numpy(float)
        yr = df.loc[df.domain == "real", "label"].to_numpy()
        gr = df.loc[df.domain == "real", "group"].to_numpy()
        indom = _cv_auc(Xr, yr, gr, n_dims=common_k, n_splits=n_splits, seed=seed)
        tstr = robustness_R(df, cols, n_dims=common_k, seed=seed)
        rows.append({
            "family": fam, "n_raw_dims": len(cols), "eval_dims": indom.n_dims,
            "auc_in_domain": round(indom.auc_mean, 4),
            "auc_tstr": round(tstr["auc_tstr"], 4),
            "robustness_R": round(tstr["R"], 4),
        })
    out = pd.DataFrame(rows).sort_values("robustness_R")
    return out.reset_index(drop=True)


def robustness_R(df: pd.DataFrame, cols, n_dims=None, n_splits=5, seed=0) -> dict:
    """R = (in-domain AUC - TSTR AUC) / in-domain AUC. Lower |R| = more shift-robust.
    in-domain: train & test on real (GroupKFold). TSTR: train on ALL sim, test on real."""
    _guard_no_param_leak(cols)
    real = df.domain == "real"
    Xr, yr, gr = (df.loc[real, cols].to_numpy(float),
                  df.loc[real, "label"].to_numpy(), df.loc[real, "group"].to_numpy())
    indom = _cv_auc(Xr, yr, gr, n_dims=n_dims, n_splits=n_splits, seed=seed).auc_mean

    Xs = df.loc[~real, cols].to_numpy(float)
    ys = df.loc[~real, "label"].to_numpy()
    steps = [("scale", StandardScaler())]
    if n_dims is not None and n_dims < Xs.shape[1]:
        steps.append(("pca", PCA(n_components=n_dims, random_state=seed)))
    steps.append(("clf", _make_clf(seed)))
    pipe = Pipeline(steps).fit(Xs, ys)
    tstr = _macro_auc(yr, pipe.predict_proba(Xr), pipe.classes_)
    R = (indom - tstr) / indom if indom and not np.isnan(indom) else np.nan
    return {"auc_in_domain": indom, "auc_tstr": tstr, "R": R}


# ---------------------------------------------------------------------------
# H1 — proportion of synthetic data, BOTH arms (guard 4)
# ---------------------------------------------------------------------------
def h1_mixing_curve(df: pd.DataFrame, feature_cols, ps_grid=(0.0, 0.25, 0.5, 0.75, 1.0),
                    arm="constant_volume", n_total=None, n_real_fixed=None,
                    n_repeats=5, n_splits=5, seed=0) -> pd.DataFrame:
    """Sweep p_s = fraction of synthetic in the TRAINING set; always TEST on held-out
    REAL folds (GroupKFold). Two arms make the substitution vs. addition effect
    separable:
        arm='constant_volume' : total training size fixed at n_total; raising p_s
                                 REMOVES real -> measures substitution.
        arm='additive'        : real count fixed at n_real_fixed; synthetic ADDED
                                 -> p_s rises because the total grows.
    Repeats with reshuffled subsamples give CIs so a claimed interior optimum p_s*
    can be shown to exceed noise, not assumed."""
    _guard_no_param_leak(feature_cols)
    real = df[df.domain == "real"].reset_index(drop=True)
    sim = df[df.domain == "sim"].reset_index(drop=True)
    rng = np.random.default_rng(seed)
    gkf = GroupKFold(n_splits=n_splits)
    rows = []
    real_groups = real.group.to_numpy()

    for rep in range(n_repeats):
        for tr_idx, te_idx in gkf.split(real, real.label, real_groups):
            real_tr, real_te = real.iloc[tr_idx], real.iloc[te_idx]
            for ps in ps_grid:
                if arm == "constant_volume":
                    assert n_total, "n_total required for constant_volume arm"
                    n_sim = int(round(ps * n_total))
                    n_r = n_total - n_sim
                    r_take = real_tr.sample(min(n_r, len(real_tr)),
                                            random_state=int(rng.integers(1e9)))
                    s_take = sim.sample(min(n_sim, len(sim)),
                                        random_state=int(rng.integers(1e9)))
                elif arm == "additive":
                    assert n_real_fixed, "n_real_fixed required for additive arm"
                    r_take = real_tr.sample(min(n_real_fixed, len(real_tr)),
                                            random_state=int(rng.integers(1e9)))
                    # ps = n_sim/(n_sim+n_real) -> n_sim = n_real*ps/(1-ps)
                    n_sim = 0 if ps >= 1 else int(round(len(r_take) * ps / (1 - ps)))
                    s_take = sim.sample(min(n_sim, len(sim)),
                                        random_state=int(rng.integers(1e9)))
                else:
                    raise ValueError(arm)

                train = pd.concat([r_take, s_take], ignore_index=True)
                if train.label.nunique() < 2:
                    continue
                pipe = Pipeline([("scale", StandardScaler()), ("clf", _make_clf(seed))])
                pipe.fit(train[feature_cols].to_numpy(float), train.label.to_numpy())
                auc = _macro_auc(real_te.label.to_numpy(),
                                 pipe.predict_proba(real_te[feature_cols].to_numpy(float)),
                                 pipe.classes_)
                rows.append({"arm": arm, "p_s": ps, "repeat": rep, "auc": auc,
                             "n_train": len(train)})
    res = pd.DataFrame(rows)
    summ = (res.groupby(["arm", "p_s"])["auc"]
            .agg(auc_mean="mean", auc_std="std", n="count").reset_index())
    return summ


if __name__ == "__main__":
    # Smoke test on synthetic random data documenting the expected schema.
    rng = np.random.default_rng(0)
    n = 600
    demo = pd.DataFrame({
        **{k: rng.normal(size=n) for k in list(TIME_KEYS)[:6]},
        **{f"hilbert_{i}": rng.normal(size=n) for i in range(6)},
        **{k: rng.normal(size=n) for k in list(FREQ_KEYS)[:6]},
        **{f"stft_{i}": rng.normal(size=n) for i in range(6)},
        "label": rng.choice(list("ABCDE"), n),
        "domain": rng.choice(["real", "sim"], n, p=[0.4, 0.6]),
        "group": rng.integers(0, 40, n),          # 40 track segments / scenes
        "fidelity_level": 4,
    })
    print("Families:", {k: len(v) for k, v in assign_families(demo.columns).items()})
    print("\nH3 (random data -> AUC~0.5, R~0):")
    print(evaluate_families(demo))
