"""T9: packing verifier — three controls before a generated scene is trusted.

(1) GEOMETRY (no simulation): achieved rock area fraction vs target, and achieved
    grading (virtual sieve, % passing) vs the target curve as a KS distance.
(2) COHERENT (needs a 2-D .out): the bulk eps that EMERGES from the surface->base
    reflection travel time vs the eps CRIM predicts for the same volume fractions
    (physics.crim_bulk_eps). If a homogeneous slab of known eps is simulated, the
    emergent eps must recover it — that is the calibration anchor.
(3) INCOHERENT (needs a 2-D .out + a real trace): envelope-decay alpha and coda
    spectral distance vs a real trace (reuses src.sim_real_comparison, T6).

verify_scene() folds the controls into a {PASS, ADJUST, REJECT} verdict + metrics,
and fidelity_headers() renders them as ``## CONFIG_fidelity_*`` lines for the .in.

Emergent eps uses Sussmann (2000) Eq.1 inverted: d = c * t_oneway / sqrt(eps)
=> eps = (c * t_oneway / d)^2, with t_oneway = dt_twoway / 2.
"""
import numpy as np

from .reflector_picking import pick_reflector
from .physics import crim_bulk_eps  # noqa: F401 — re-exported for callers/tests

_C = 299_792_458.0  # speed of light, m/s


# --------------------------------------------------------------------------- #
# Control 2 — coherent (emergent eps from timing)
# --------------------------------------------------------------------------- #
def emergent_eps_from_timing(signal, dt, thickness_m, **pick_kw):
    """Bulk eps recovered from the surface->base two-way travel time.

    Returns (eps, pick_dict). eps is NaN if no reflector was picked.
    """
    pick = pick_reflector(np.asarray(signal, float), dt, **pick_kw)
    twt_ns = pick.get("dt_twoway_ns", np.nan)
    if not pick.get("found", False) or not np.isfinite(twt_ns):
        return float("nan"), pick
    t_oneway_s = (twt_ns / 2.0) * 1e-9
    eps = (_C * t_oneway_s / thickness_m) ** 2
    return float(eps), pick


def verify_effective_eps(signal, dt, expected_eps, thickness_m, tol=0.05, **pick_kw):
    """Control 2: emergent eps (from timing) vs expected (e.g. CRIM). PASS <= tol."""
    eps, pick = emergent_eps_from_timing(signal, dt, thickness_m, **pick_kw)
    rel = abs(eps - expected_eps) / expected_eps if np.isfinite(eps) else float("inf")
    return {
        "emergent_eps": eps,
        "expected_eps": float(expected_eps),
        "rel_error": rel,
        "dt_twoway_ns": float(pick.get("dt_twoway_ns", np.nan)),
        "found": bool(pick.get("found", False)),
        "pass": bool(rel <= tol),
    }


# --------------------------------------------------------------------------- #
# Control 1 — geometry (no simulation)
# --------------------------------------------------------------------------- #
def verify_geometry(achieved_fill, target_fill, achieved_sieve_pct=None,
                    target_sieve_pct=None, fill_tol=0.05, grading_ks_tol=10.0):
    """Control 1 (no sim): area-fraction and grading vs target.

    grading is compared as a KS distance = max |achieved - target| over the
    %-passing sieve curve (both arrays aligned on the same sieve sizes).
    """
    fill_err = abs(float(achieved_fill) - float(target_fill))
    out = {
        "achieved_fill": float(achieved_fill),
        "target_fill": float(target_fill),
        "fill_error": fill_err,
        "fill_pass": bool(fill_err <= fill_tol),
    }
    if achieved_sieve_pct is not None and target_sieve_pct is not None:
        a = np.asarray(achieved_sieve_pct, float)
        t = np.asarray(target_sieve_pct, float)
        ks = float(np.max(np.abs(a - t)))
        out["grading_ks_pct"] = ks
        out["grading_pass"] = bool(ks <= grading_ks_tol)
    return out


# --------------------------------------------------------------------------- #
# Control 3 — incoherent (coda vs real)
# --------------------------------------------------------------------------- #
def verify_incoherent(sim_signal, sim_dt, real_signal, real_dt,
                      alpha_window_ns=(4.0, 18.0), band=None):
    """Control 3: envelope-decay alpha and coda spectral distance vs a real trace
    (reuses the canonical T6 metrics). Lower spectral distance / closer alpha =
    better; returns the raw numbers for the orchestrator to threshold."""
    from .sim_real_comparison import envelope_alpha, spectral_distance
    a_sim = envelope_alpha(sim_signal, sim_dt, alpha_window_ns[0], alpha_window_ns[1], band=band)
    a_real = envelope_alpha(real_signal, real_dt, alpha_window_ns[0], alpha_window_ns[1], band=band)
    dist = spectral_distance(sim_signal, sim_dt, real_signal, real_dt, band=band)
    return {
        "alpha_sim_per_ns": a_sim,
        "alpha_real_per_ns": a_real,
        "alpha_abs_diff": abs(a_sim - a_real),
        "spectral_distance_hz": dist,
    }


# --------------------------------------------------------------------------- #
# Orchestrator + fidelity headers
# --------------------------------------------------------------------------- #
def verify_scene(geometry=None, coherent=None, incoherent=None,
                 alpha_tol_per_ns=0.05):
    """Fold the available controls into a {PASS, ADJUST, REJECT} verdict.

    - REJECT if the coherent control fails (emergent eps far from CRIM) — the
      scene does not represent the intended material.
    - ADJUST if geometry is off but the coherent control passes (fixable by
      re-packing to the target fill/grading).
    - PASS if every provided control passes.
    Controls set to None are skipped.
    """
    reasons = []
    if coherent is not None and not coherent.get("pass", False):
        reasons.append(f"coherent: emergent eps {coherent.get('emergent_eps'):.2f} "
                       f"vs CRIM {coherent.get('expected_eps'):.2f} "
                       f"(rel {coherent.get('rel_error'):.2%})")
        return {"verdict": "REJECT", "reasons": reasons,
                "geometry": geometry, "coherent": coherent, "incoherent": incoherent}

    geom_ok = geometry is None or (geometry.get("fill_pass", True)
                                   and geometry.get("grading_pass", True))
    if not geom_ok:
        reasons.append(f"geometry: fill {geometry.get('achieved_fill'):.3f} vs "
                       f"target {geometry.get('target_fill'):.3f}")
        verdict = "ADJUST"
    else:
        verdict = "PASS"

    if incoherent is not None and np.isfinite(incoherent.get("alpha_abs_diff", np.nan)):
        if incoherent["alpha_abs_diff"] > alpha_tol_per_ns and verdict == "PASS":
            verdict = "ADJUST"
            reasons.append(f"incoherent: |alpha_sim - alpha_real| "
                           f"{incoherent['alpha_abs_diff']:.3f}/ns")

    return {"verdict": verdict, "reasons": reasons,
            "geometry": geometry, "coherent": coherent, "incoherent": incoherent}


def fidelity_headers(result):
    """Render a verify_scene() result as ``## CONFIG_fidelity_*`` lines for the .in."""
    lines = [f"## CONFIG_fidelity_verdict: {result.get('verdict', 'UNKNOWN')}"]
    g, c = result.get("geometry"), result.get("coherent")
    if g is not None:
        lines.append(f"## CONFIG_fidelity_fill: {g.get('achieved_fill', float('nan')):g}")
        if "grading_ks_pct" in g:
            lines.append(f"## CONFIG_fidelity_grading_ks_pct: {g['grading_ks_pct']:g}")
    if c is not None:
        lines.append(f"## CONFIG_fidelity_emergent_eps: {c.get('emergent_eps', float('nan')):g}")
        lines.append(f"## CONFIG_fidelity_eps_rel_error: {c.get('rel_error', float('nan')):g}")
    return lines


# --------------------------------------------------------------------------- #
# 2-D area-fraction -> emergent-eps calibration map (monotonic search)
# --------------------------------------------------------------------------- #
def calibrate_fill_for_eps(target_eps, run_and_measure, fill_lo=0.10, fill_hi=0.50,
                           tol=0.03, max_iter=8):
    """Find the 2-D area fill whose EMERGENT eps matches target_eps (e.g. the CRIM
    3-D value), by monotonic bisection. ``run_and_measure(fill) -> emergent_eps``
    is a caller-supplied closure that packs at ``fill``, runs a 2-D sim, and
    returns the emergent eps (this is the expensive, gprMax part — kept out of
    this module so it stays unit-testable and cache-friendly).

    Returns (best_fill, emergent_eps, n_iter). Assumes emergent eps increases with
    fill (denser packing -> higher bulk eps).
    """
    lo, hi = fill_lo, fill_hi
    best_fill, best_eps = None, None
    for i in range(1, max_iter + 1):
        mid = 0.5 * (lo + hi)
        eps = float(run_and_measure(mid))
        best_fill, best_eps = mid, eps
        if abs(eps - target_eps) / target_eps <= tol:
            return best_fill, best_eps, i
        if eps < target_eps:
            lo = mid          # too sparse -> need denser
        else:
            hi = mid
    return best_fill, best_eps, max_iter
