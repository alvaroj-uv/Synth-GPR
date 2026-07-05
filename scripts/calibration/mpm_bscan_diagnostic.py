#!/usr/bin/env python3
"""
Matrix Pencil Method (MPM) applied to a DZT B-scan window.

Decomposes each A-scan in a trace window into damped complex exponentials:
    y(t) = sum_k  R_k * exp((sigma_k + j*omega_k) * t)

Plots:
  1. B-scan (raw amplitude image) of the window
  2. Pole map: arrival time (ns) vs trace index for all extracted poles,
     coloured by damping rate sigma_k — stable horizontal bands = layer reflections
  3. Mean A-scan with Hilbert envelope and detected poles overlaid
  4. Pole-frequency histogram (omega_k / 2pi in MHz) — cluster = dominant mode

Usage:
    python scripts/calibration/mpm_bscan_diagnostic.py \\
        --dzt "D:/Codigo/Data/...DZT" \\
        --center 77000 --half-width 100 \\
        --coda-start 4 --coda-end 20 \\
        --n-poles 6 \\
        --out experiments/calibration/mpm_diagnostic.png
"""

import argparse
import sys
from pathlib import Path

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from scipy.signal import hilbert

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from src.dzt_io import read_dzt_traces

DZT_DT_NS = 50.0 / 511.0   # ≈ 0.0978 ns


# ── Matrix Pencil Method ──────────────────────────────────────────────────────

def matrix_pencil(y: np.ndarray, n_poles: int) -> tuple[np.ndarray, np.ndarray]:
    """
    Estimate n_poles damped complex exponential poles from signal y.

    Returns:
        poles  : complex array (n_poles,), units: 1/sample  (s_k = sigma + j*omega)
        residues: complex array (n_poles,)

    Reference: Sarkar & Pereira, IEEE Antennas & Prop. Mag. 1995.
    """
    N = len(y)
    L = N // 3          # pencil parameter (N/3 is standard heuristic)
    L = max(L, n_poles + 1)
    L = min(L, N - n_poles - 1)

    # Build Hankel data matrix Y (N-L) x (L+1)
    rows = N - L
    Y = np.zeros((rows, L + 1), dtype=complex)
    for i in range(rows):
        Y[i, :] = y[i: i + L + 1]

    Y1 = Y[:, :-1]   # (N-L) x L
    Y2 = Y[:, 1:]    # (N-L) x L

    # Truncated SVD of Y1
    U, s, Vh = np.linalg.svd(Y1, full_matrices=False)
    # Keep n_poles singular values
    U  = U[:, :n_poles]
    s  = s[:n_poles]
    Vh = Vh[:n_poles, :]

    # Generalised eigenvalue problem → poles
    Z = np.diag(1.0 / s) @ U.conj().T @ Y2 @ Vh.conj().T
    poles = np.linalg.eigvals(Z)

    # Residues via least-squares Vandermonde solve
    t = np.arange(N, dtype=float)
    V = np.vstack([poles ** ti for ti in t]).T   # N x n_poles
    residues, _, _, _ = np.linalg.lstsq(V, y.astype(complex), rcond=None)

    return poles, residues


def poles_to_ns(poles: np.ndarray, dt_ns: float) -> tuple[np.ndarray, np.ndarray]:
    """Convert per-sample poles to physical units.

    Returns:
        t_arrival_ns : arrival time estimate = -1 / (sigma_k / dt_ns)  ...
                       more usefully: use Im(log(pole)) for frequency,
                       and the initial phase for arrival time estimate.
        sigma_per_ns : damping rate (negative = decaying)
        freq_mhz     : oscillation frequency
    """
    log_p = np.log(poles + 1e-30)
    sigma_per_ns = log_p.real / dt_ns   # damping rate (1/ns)
    omega_per_ns = log_p.imag / dt_ns   # angular freq (rad/ns)
    freq_mhz = np.abs(omega_per_ns) / (2 * np.pi) * 1e3  # MHz
    return sigma_per_ns, freq_mhz


# ── DZT loading ───────────────────────────────────────────────────────────────

def load_window(dzt_path: str, center: int, half_width: int,
                coda_start_ns: float, coda_end_ns: float):
    """Load a B-scan window and return the coda segment."""
    start = max(0, center - half_width)
    n = 2 * half_width + 1
    traces, meta = read_dzt_traces(Path(dzt_path), start_trace=start, num_traces=n)
    dt = meta.get("sample_interval_ns", DZT_DT_NS)
    t = np.arange(traces.shape[1]) * dt

    # Find DW peak in the mean trace (search first 10 ns)
    mean_trace = traces.mean(axis=0)
    search_end = int(10.0 / dt)
    dw_idx = int(np.argmax(np.abs(mean_trace[:search_end])))
    t_rel = t - t[dw_idx]

    mask = (t_rel >= coda_start_ns) & (t_rel <= coda_end_ns)
    return traces, t_rel, mask, dt, dw_idx


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--dzt", required=True)
    ap.add_argument("--center",     type=int,   default=77000)
    ap.add_argument("--half-width", type=int,   default=100,
                    help="Traces on each side of center (default 100 → 201 traces)")
    ap.add_argument("--coda-start", type=float, default=4.0,
                    help="Coda window start relative to DW peak (ns)")
    ap.add_argument("--coda-end",   type=float, default=20.0)
    ap.add_argument("--n-poles",    type=int,   default=6,
                    help="Number of MPM poles per trace (default 6)")
    ap.add_argument("--out", default="experiments/calibration/mpm_diagnostic.png")
    args = ap.parse_args()

    print(f"Loading DZT window: traces {args.center - args.half_width}"
          f"–{args.center + args.half_width} …")
    traces, t_rel, mask, dt, dw_idx = load_window(
        args.dzt, args.center, args.half_width,
        args.coda_start, args.coda_end
    )
    n_traces, _ = traces.shape
    t_coda = t_rel[mask]
    print(f"  {n_traces} traces, coda window {t_coda[0]:.1f}–{t_coda[-1]:.1f} ns "
          f"({mask.sum()} samples/trace), dt={dt:.4f} ns")

    # ── Run MPM on each trace ─────────────────────────────────────────────────
    print(f"Running MPM ({args.n_poles} poles) on each trace …")
    all_sigma   = np.zeros((n_traces, args.n_poles))
    all_freq    = np.zeros((n_traces, args.n_poles))
    all_amp     = np.zeros((n_traces, args.n_poles))

    for i, trace in enumerate(traces):
        coda = trace[mask].astype(float)
        # Normalise to avoid numerical issues
        scale = np.max(np.abs(coda)) or 1.0
        try:
            poles, residues = matrix_pencil(coda / scale, args.n_poles)
            sigma, freq = poles_to_ns(poles, dt)
        except np.linalg.LinAlgError:
            sigma = np.full(args.n_poles, np.nan)
            freq  = np.full(args.n_poles, np.nan)
            residues = np.zeros(args.n_poles, dtype=complex)

        all_sigma[i]  = sigma
        all_freq[i]   = freq
        all_amp[i]    = np.abs(residues)

    print("  Done.")

    # ── Convert sigma & freq to useful displays ───────────────────────────────
    # Keep only decaying poles (sigma < 0) in a physically reasonable range
    # and frequencies in 50–800 MHz (within GPR band)
    valid = (all_sigma < 0) & (all_freq > 50) & (all_freq < 800)

    trace_idx_v = np.where(valid)[0]
    freq_v      = all_freq[valid]
    sigma_v     = all_sigma[valid]
    amp_v       = all_amp[valid]

    # ── Plot ──────────────────────────────────────────────────────────────────
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    fig.suptitle(f"MPM B-scan diagnostic — trace {args.center} ±{args.half_width}  "
                 f"({args.n_poles} poles, coda {args.coda_start}–{args.coda_end} ns)",
                 fontsize=11)

    # Panel 1: B-scan (full trace, raw amplitude)
    ax = axes[0, 0]
    full_t = t_rel
    clip = np.percentile(np.abs(traces), 98)
    ax.imshow(traces.T, aspect="auto", cmap="RdBu_r", vmin=-clip, vmax=clip,
              extent=[0, n_traces, full_t[-1], full_t[0]])
    ax.axhline(args.coda_start, color="lime",   lw=0.8, ls="--", label="coda start")
    ax.axhline(args.coda_end,   color="lime",   lw=0.8, ls=":",  label="coda end")
    ax.set_xlabel("Trace offset from center")
    ax.set_ylabel("Time rel. DW peak (ns)")
    ax.set_title("B-scan (raw)")
    ax.legend(fontsize=7, loc="upper right")

    # Panel 2: Pole frequency vs trace index (scatter, colour = |sigma|)
    ax = axes[0, 1]
    sc = ax.scatter(trace_idx_v, freq_v,
                    c=np.abs(sigma_v), cmap="plasma_r",
                    s=6, alpha=0.5, vmin=0, vmax=1.5)
    plt.colorbar(sc, ax=ax, label="|σ| (1/ns) — darker = slower decay")
    ax.set_xlabel("Trace offset from center")
    ax.set_ylabel("Pole frequency (MHz)")
    ax.set_title("MPM pole frequencies — horizontal bands = stable reflections")
    ax.set_ylim(50, 800)

    # Panel 3: Mean A-scan + Hilbert envelope + coda window
    ax = axes[1, 0]
    mean_tr = traces.mean(axis=0)
    env_mean = np.abs(hilbert(mean_tr))
    env_mean /= env_mean.max()
    mean_norm = mean_tr / (np.max(np.abs(mean_tr)) or 1)

    ax.plot(full_t, mean_norm,  lw=0.8, color="royalblue", label="Mean trace")
    ax.plot(full_t, env_mean,   lw=1.2, color="tomato",    label="Hilbert envelope")
    ax.axvspan(args.coda_start, args.coda_end, alpha=0.08, color="green")
    ax.axvline(0, color="k", lw=0.5, ls="--")
    ax.set_xlabel("Time rel. DW peak (ns)")
    ax.set_ylabel("Norm. amplitude")
    ax.set_title("Mean A-scan (all traces in window)")
    ax.set_xlim(-2, 26)
    ax.legend(fontsize=8)

    # Panel 4: Histogram of pole frequencies
    ax = axes[1, 1]
    # Weight by amplitude for a weighted histogram
    weights = amp_v / (amp_v.sum() or 1)
    ax.hist(freq_v, bins=60, range=(50, 800), weights=weights,
            color="steelblue", edgecolor="none", alpha=0.8)
    ax.axvline(400, color="tomato", lw=1, ls="--", label="400 MHz (source)")
    ax.set_xlabel("Pole frequency (MHz)")
    ax.set_ylabel("Weighted count (norm. amplitude)")
    ax.set_title("MPM pole frequency distribution (amplitude-weighted)")
    ax.legend(fontsize=8)

    fig.tight_layout()
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, dpi=150)
    plt.close(fig)
    print(f"\nSaved -> {out_path}")

    # ── Text summary ──────────────────────────────────────────────────────────
    print(f"\nValid poles (decaying, 50-800 MHz): {len(freq_v)} / "
          f"{n_traces * args.n_poles} total")
    # Find stable frequency bands: cluster poles by frequency
    if len(freq_v) > 10:
        from scipy.signal import find_peaks
        hist, edges = np.histogram(freq_v, bins=60, range=(50, 800),
                                   weights=amp_v)
        centres = (edges[:-1] + edges[1:]) / 2
        peaks, props = find_peaks(hist, height=hist.max() * 0.1, distance=3)
        print(f"\nDominant frequency clusters (possible reflections):")
        for pk in peaks:
            print(f"  {centres[pk]:.0f} MHz  (rel. height {hist[pk]/hist.max():.2f})")


if __name__ == "__main__":
    main()
