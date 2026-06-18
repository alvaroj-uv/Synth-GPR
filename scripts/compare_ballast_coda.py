#!/usr/bin/env python3
"""
Compare coda response: Ballast layer vs Freespace vs Real field GPR.
Shows how ballast material affects waveform after direct wave (5+ ns window).
"""

import sys
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from scipy.interpolate import interp1d

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.data_loader import read_ascan


def read_synthetic_out(out_path: Path, component: str = "Ez") -> tuple:
    """Read synthetic .out file (HDF5)."""
    data = read_ascan(out_path, component)
    signal = data['signal']
    dt = data['dt']
    t_ns = np.arange(len(signal)) * dt * 1e9
    return signal, t_ns, dt * 1e9


def read_real_dzt(dzt_path: Path, trace_idx: int = 1000) -> tuple:
    """Read real DZT trace."""
    HEADER_SIZE = 128 * 1024
    SAMPLES_PER_TRACE = 512
    BYTES_PER_SAMPLE = 4
    DT_NS = 50 / 511

    with open(dzt_path, 'rb') as f:
        f.seek(HEADER_SIZE + trace_idx * SAMPLES_PER_TRACE * BYTES_PER_SAMPLE)
        trace_bytes = f.read(SAMPLES_PER_TRACE * BYTES_PER_SAMPLE)
        signal = np.frombuffer(trace_bytes, dtype=np.int32, count=SAMPLES_PER_TRACE)
        signal = signal.astype(np.float64)

    signal = signal[2:]  # Drop indices 0-1
    t_ns = np.arange(len(signal)) * DT_NS
    return signal, t_ns, DT_NS


def normalize_peak(signal):
    """Normalize by peak amplitude."""
    peak = np.max(np.abs(signal))
    if peak == 0:
        return signal
    return signal / peak


def main():
    import argparse

    ap = argparse.ArgumentParser(
        description="Compare coda: Ballast vs Freespace vs Real")
    ap.add_argument("ballast_out", type=Path, help="Ballast layer .out file")
    ap.add_argument("freespace_out", type=Path, help="Freespace .out file (reference)")
    ap.add_argument("real_dzt", type=Path, help="Real .DZT file")
    ap.add_argument("--trace", type=int, default=15000, help="DZT trace index")
    ap.add_argument("-o", "--output", type=Path, default=None, help="Output PNG")
    args = ap.parse_args()

    # Validate files
    for f in [args.ballast_out, args.freespace_out, args.real_dzt]:
        if not f.exists():
            print(f"[ERR] File not found: {f}")
            return 1

    print("[READ] Ballast layer: " + args.ballast_out.name)
    ballast_sig, ballast_t, dt_ballast = read_synthetic_out(args.ballast_out)

    print("[READ] Freespace (reference): " + args.freespace_out.name)
    freespace_sig, freespace_t, dt_freespace = read_synthetic_out(args.freespace_out)

    print(f"[READ] Real DZT (trace #{args.trace}): {args.real_dzt.name}")
    real_sig, real_t, dt_real = read_real_dzt(args.real_dzt, trace_idx=args.trace)

    print(f"\nBallast:    {len(ballast_sig)} samples, dt={dt_ballast:.6f} ns")
    print(f"Freespace:  {len(freespace_sig)} samples, dt={dt_freespace:.6f} ns")
    print(f"Real DZT:   {len(real_sig)} samples, dt={dt_real:.6f} ns")

    # ========================================================================
    # POLARITY FLIP & NORMALIZE
    # ========================================================================
    ballast_flipped = normalize_peak(-ballast_sig)
    freespace_flipped = normalize_peak(-freespace_sig)
    real_norm = normalize_peak(real_sig)

    # ========================================================================
    # RESAMPLE TO REAL'S DT
    # ========================================================================
    t_min = 0
    t_max = min(ballast_t[-1], freespace_t[-1], real_t[-1])
    t_common = np.arange(int(t_max / dt_real) + 1) * dt_real

    f_ballast = interp1d(ballast_t, ballast_flipped, kind='cubic', bounds_error=False, fill_value=0)
    f_freespace = interp1d(freespace_t, freespace_flipped, kind='cubic', bounds_error=False, fill_value=0)
    f_real = interp1d(real_t, real_norm, kind='cubic', bounds_error=False, fill_value=0)

    ballast_rs = f_ballast(t_common)
    freespace_rs = f_freespace(t_common)
    real_rs = f_real(t_common)

    # ========================================================================
    # CORRELATIONS
    # ========================================================================
    corr_ballast_vs_real = np.corrcoef(ballast_rs, real_rs)[0, 1]
    corr_freespace_vs_real = np.corrcoef(freespace_rs, real_rs)[0, 1]
    corr_ballast_vs_freespace = np.corrcoef(ballast_rs, freespace_rs)[0, 1]

    print(f"\n[CORR] Ballast vs Real: {corr_ballast_vs_real:.6f}")
    print(f"[CORR] Freespace vs Real: {corr_freespace_vs_real:.6f}")
    print(f"[CORR] Ballast vs Freespace: {corr_ballast_vs_freespace:.6f}")

    # ========================================================================
    # PLOT: 4-row comparison
    # ========================================================================
    fig = plt.figure(figsize=(16, 14))
    fig.patch.set_facecolor("#0f1117")
    gs = gridspec.GridSpec(4, 1, figure=fig, hspace=0.35, left=0.1, right=0.95, top=0.96, bottom=0.06)

    c_ballast = "#00ff88"    # Green
    c_freespace = "#00d9ff"  # Cyan
    c_real = "#ff6b35"       # Orange-red

    # Display window (first 50 ns or full)
    display_max = min(50, t_common[-1])
    mask = t_common <= display_max

    # ========================================================================
    # Row 1: Ballast (with material layer effect)
    # ========================================================================
    ax1 = fig.add_subplot(gs[0])
    ax1.set_facecolor("#1a1e2b")
    ax1.plot(t_common[mask], ballast_rs[mask], color=c_ballast, lw=1.5, alpha=0.85, label="Ballast Layer (Clean, eps=3.45)")
    ax1.axhline(0, color="#2a2f42", lw=0.8, linestyle='-', alpha=0.5)
    ax1.set_ylabel("Amplitude (norm)", fontsize=10, color="#c8d0e0", fontweight='bold')
    ax1.set_title("Row 1: Synthetic with Ballast Layer (0.3m, eps=3.45, sigma=0.0)",
                 fontsize=11, color="#c8d0e0", fontweight='bold', pad=8)
    ax1.grid(True, color="#2a2f42", lw=0.5, alpha=0.4)
    ax1.legend(loc='upper right', fontsize=9, facecolor='#1a1e2b', labelcolor='#c8d0e0', edgecolor='#2a2f42')
    ax1.tick_params(colors="#c8d0e0", labelsize=9)
    for spine in ax1.spines.values():
        spine.set_color("#2a2f42")

    # ========================================================================
    # Row 2: Freespace (reference, no material)
    # ========================================================================
    ax2 = fig.add_subplot(gs[1])
    ax2.set_facecolor("#1a1e2b")
    ax2.plot(t_common[mask], freespace_rs[mask], color=c_freespace, lw=1.5, alpha=0.85, label="Freespace (Reference, eps=1.0)")
    ax2.axhline(0, color="#2a2f42", lw=0.8, linestyle='-', alpha=0.5)
    ax2.set_ylabel("Amplitude (norm)", fontsize=10, color="#c8d0e0", fontweight='bold')
    ax2.set_title("Row 2: Synthetic Freespace (Reference)",
                 fontsize=11, color="#c8d0e0", fontweight='bold', pad=8)
    ax2.grid(True, color="#2a2f42", lw=0.5, alpha=0.4)
    ax2.legend(loc='upper right', fontsize=9, facecolor='#1a1e2b', labelcolor='#c8d0e0', edgecolor='#2a2f42')
    ax2.tick_params(colors="#c8d0e0", labelsize=9)
    for spine in ax2.spines.values():
        spine.set_color("#2a2f42")

    # ========================================================================
    # Row 3: Real field data
    # ========================================================================
    ax3 = fig.add_subplot(gs[2])
    ax3.set_facecolor("#1a1e2b")
    ax3.plot(t_common[mask], real_rs[mask], color=c_real, lw=1.5, alpha=0.85, label="Real Field GPR (Puerto-Limache)")
    ax3.axhline(0, color="#2a2f42", lw=0.8, linestyle='-', alpha=0.5)
    ax3.set_ylabel("Amplitude (norm)", fontsize=10, color="#c8d0e0", fontweight='bold')
    ax3.set_title("Row 3: Real Field Data",
                 fontsize=11, color="#c8d0e0", fontweight='bold', pad=8)
    ax3.grid(True, color="#2a2f42", lw=0.5, alpha=0.4)
    ax3.legend(loc='upper right', fontsize=9, facecolor='#1a1e2b', labelcolor='#c8d0e0', edgecolor='#2a2f42')
    ax3.tick_params(colors="#c8d0e0", labelsize=9)
    for spine in ax3.spines.values():
        spine.set_color("#2a2f42")

    # ========================================================================
    # Row 4: Overlay (Ballast vs Real vs Freespace)
    # ========================================================================
    ax4 = fig.add_subplot(gs[3])
    ax4.set_facecolor("#1a1e2b")
    ax4.plot(t_common[mask], ballast_rs[mask], color=c_ballast, lw=1.5, alpha=0.80, label=f"Ballast vs Real: {corr_ballast_vs_real:.4f}")
    ax4.plot(t_common[mask], freespace_rs[mask], color=c_freespace, lw=1.5, alpha=0.60, label=f"Freespace vs Real: {corr_freespace_vs_real:.4f}", linestyle='--')
    ax4.plot(t_common[mask], real_rs[mask], color=c_real, lw=1.5, alpha=0.80, label="Real (reference)")
    ax4.axhline(0, color="#2a2f42", lw=0.8, linestyle='-', alpha=0.5)
    ax4.set_xlabel("Time (ns)", fontsize=10, color="#c8d0e0", fontweight='bold')
    ax4.set_ylabel("Amplitude (norm)", fontsize=10, color="#c8d0e0", fontweight='bold')
    ax4.set_title("Row 4: Overlay Comparison (Coda Analysis)",
                 fontsize=11, color="#c8d0e0", fontweight='bold', pad=8)
    ax4.grid(True, color="#2a2f42", lw=0.5, alpha=0.4)
    ax4.legend(loc='upper right', fontsize=9, facecolor='#1a1e2b', labelcolor='#c8d0e0', edgecolor='#2a2f42')
    ax4.tick_params(colors="#c8d0e0", labelsize=9)
    for spine in ax4.spines.values():
        spine.set_color("#2a2f42")

    # Main title
    fig.suptitle(
        "Coda Analysis: Ballast Layer vs Freespace vs Real Field GPR\n"
        f"Ballast: eps=3.45, sigma=0.0 | Freespace: eps=1.0 (reference)",
        color="#c8d0e0", fontsize=13, fontweight='bold', y=0.995
    )

    # Save
    if args.output:
        out_png = args.output.with_suffix('.png')
    else:
        out_png = Path('output_test') / "16_ballast_coda_comparison.png"

    out_png.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_png, dpi=150, bbox_inches='tight', facecolor="#0f1117")
    plt.close(fig)

    print(f"\n[OK] Saved: {out_png}")

    # ========================================================================
    # SUMMARY
    # ========================================================================
    print(f"\n{'='*70}")
    print("CODA ANALYSIS SUMMARY")
    print(f"{'='*70}")
    print(f"Ballast correlation vs real: {corr_ballast_vs_real:.6f}")
    print(f"Freespace correlation vs real: {corr_freespace_vs_real:.6f}")
    print(f"Difference: {abs(corr_ballast_vs_real - corr_freespace_vs_real):.6f}")
    print(f"\nInterpretation:")
    if corr_ballast_vs_real > corr_freespace_vs_real:
        improvement = ((corr_ballast_vs_real - corr_freespace_vs_real) / abs(corr_freespace_vs_real) * 100) if corr_freespace_vs_real != 0 else 0
        print(f"  [BALLAST WINS] Material layer IMPROVES match by {improvement:.1f}%")
        print(f"  Ballast adds realistic coda structure matching field response")
    else:
        print(f"  [FREESPACE WINS] Ballast reduces match")
        print(f"  Material eps/sigma may need adjustment (current: 3.45/0.0)")
    print(f"{'='*70}\n")

    return 0


if __name__ == "__main__":
    sys.exit(main())
