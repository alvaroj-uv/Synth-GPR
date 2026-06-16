#!/usr/bin/env python3
"""
Step 1: RAW comparison - synthetic vs real waveforms, no manipulation.
Goal: See what we're working with (units, timing, shape).
"""

import sys
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.data_loader import read_ascan


def read_synthetic(file_path: Path, component: str = "Ez") -> tuple:
    """Read synthetic .out file."""
    data = read_ascan(file_path, component)
    signal = data['signal']
    dt = data['dt']
    t_ns = np.arange(len(signal)) * dt * 1e9
    return signal, t_ns, dt * 1e9


def read_real_dzt(file_path: Path, trace_idx: int = 1000) -> tuple:
    """Read real DZT file."""
    HEADER_SIZE = 128 * 1024
    SAMPLES_PER_TRACE = 512
    BYTES_PER_SAMPLE = 4
    DT_NS = 50 / 511

    with open(file_path, 'rb') as f:
        f.seek(HEADER_SIZE + trace_idx * SAMPLES_PER_TRACE * BYTES_PER_SAMPLE)
        trace_bytes = f.read(SAMPLES_PER_TRACE * BYTES_PER_SAMPLE)
        signal = np.frombuffer(trace_bytes, dtype=np.int32, count=SAMPLES_PER_TRACE)
        signal = signal.astype(np.float64)

    signal = signal[2:]  # Drop indices 0-1
    t_ns = np.arange(len(signal)) * DT_NS
    return signal, t_ns, DT_NS


def plot_raw_comparison(syn_sig, syn_t, dt_syn, real_sig, real_t, dt_real, out_png):
    """
    Create 2-row comparison:
    Row 1: Synthetic (V/m physical units)
    Row 2: Real DZT (A/D counts)
    """

    fig = plt.figure(figsize=(16, 10))
    fig.patch.set_facecolor("#0f1117")
    gs = gridspec.GridSpec(2, 1, figure=fig, hspace=0.3, left=0.1, right=0.95, top=0.95, bottom=0.08)

    # Row 1: Synthetic (raw, physical units V/m)
    ax1 = fig.add_subplot(gs[0])
    ax1.set_facecolor("#1a1e2b")
    ax1.plot(syn_t, syn_sig, color="#00d4ff", lw=1.5, alpha=0.85)
    ax1.axhline(0, color="#2a2f42", lw=0.8, linestyle='-', alpha=0.5)
    ax1.fill_between(syn_t, syn_sig, 0, alpha=0.15, color="#00d4ff")

    ax1.set_ylabel("Amplitude (V/m)", fontsize=11, color="#c8d0e0", fontweight='bold')
    ax1.set_title(f"Row 1: SYNTHETIC gprMax Output (Free Space 400 MHz) - {len(syn_sig)} samples @ dt={dt_syn:.4f} ns",
                 fontsize=11, color="#c8d0e0", fontweight='bold', pad=10)
    ax1.grid(True, color="#2a2f42", lw=0.5, alpha=0.4)
    ax1.tick_params(colors="#c8d0e0", labelsize=9)

    # Statistics box for synthetic
    peak_idx_syn = np.argmax(np.abs(syn_sig))
    stats_syn = f"Peak: {syn_sig[peak_idx_syn]:.2e} V/m @ {syn_t[peak_idx_syn]:.2f} ns\nRMS: {np.sqrt(np.mean(syn_sig**2)):.2e} V/m\nSamples: {len(syn_sig)}"
    ax1.text(0.98, 0.97, stats_syn, transform=ax1.transAxes, fontsize=9,
            verticalalignment='top', horizontalalignment='right',
            bbox=dict(boxstyle='round', facecolor='#1a1e2b', edgecolor='#00d4ff', linewidth=1),
            fontfamily='monospace', color="#c8d0e0")

    for spine in ax1.spines.values():
        spine.set_color("#2a2f42")

    # Row 2: Real DZT (raw, A/D counts)
    ax2 = fig.add_subplot(gs[1])
    ax2.set_facecolor("#1a1e2b")
    ax2.plot(real_t, real_sig, color="#ff6b35", lw=1.5, alpha=0.85)
    ax2.axhline(0, color="#2a2f42", lw=0.8, linestyle='-', alpha=0.5)
    ax2.fill_between(real_t, real_sig, 0, alpha=0.15, color="#ff6b35")

    ax2.set_xlabel("Time (ns)", fontsize=11, color="#c8d0e0", fontweight='bold')
    ax2.set_ylabel("Amplitude (A/D counts)", fontsize=11, color="#c8d0e0", fontweight='bold')
    ax2.set_title(f"Row 2: REAL DZT (Puerto-Limache Field Data) - {len(real_sig)} samples @ dt={dt_real:.4f} ns",
                 fontsize=11, color="#c8d0e0", fontweight='bold', pad=10)
    ax2.grid(True, color="#2a2f42", lw=0.5, alpha=0.4)
    ax2.tick_params(colors="#c8d0e0", labelsize=9)

    # Statistics box for real
    peak_idx_real = np.argmax(np.abs(real_sig))
    stats_real = f"Peak: {real_sig[peak_idx_real]:.2e} counts @ {real_t[peak_idx_real]:.2f} ns\nRMS: {np.sqrt(np.mean(real_sig**2)):.2e} counts\nSamples: {len(real_sig)}"
    ax2.text(0.98, 0.97, stats_real, transform=ax2.transAxes, fontsize=9,
            verticalalignment='top', horizontalalignment='right',
            bbox=dict(boxstyle='round', facecolor='#1a1e2b', edgecolor='#ff6b35', linewidth=1),
            fontfamily='monospace', color="#c8d0e0")

    for spine in ax2.spines.values():
        spine.set_color("#2a2f42")

    # Main title
    fig.suptitle(
        "Step 1: RAW COMPARISON - Synthetic vs Real (No Normalization, No Manipulation)",
        color="#c8d0e0", fontsize=12, fontweight='bold', y=0.98
    )

    out_png.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_png, dpi=150, bbox_inches='tight', facecolor="#0f1117")
    plt.close(fig)

    print(f"\n[OK] Raw comparison saved -> {out_png}")

    return {
        'syn_peak': syn_sig[peak_idx_syn],
        'syn_peak_time': syn_t[peak_idx_syn],
        'real_peak': real_sig[peak_idx_real],
        'real_peak_time': real_t[peak_idx_real],
    }


def main():
    import argparse

    ap = argparse.ArgumentParser(description="Step 1: Raw synthetic vs real comparison")
    ap.add_argument("synth", type=Path, help="Synthetic .out file")
    ap.add_argument("real", type=Path, help="Real .DZT file")
    ap.add_argument("--trace", type=int, default=1000, help="DZT trace index")
    ap.add_argument("-o", "--output", type=Path, default=None, help="Output PNG")
    args = ap.parse_args()

    if not args.synth.exists() or not args.real.exists():
        print("[ERR] Input files not found")
        sys.exit(1)

    print("[READ] Loading files...")
    syn_sig, syn_t, dt_syn = read_synthetic(args.synth)
    real_sig, real_t, dt_real = read_real_dzt(args.real, trace_idx=args.trace)

    print(f"\nSynthetic: {len(syn_sig)} samples, dt={dt_syn:.4f} ns, t_range=[{syn_t[0]:.2f}, {syn_t[-1]:.2f}] ns, Units: V/m")
    print(f"Real DZT:  {len(real_sig)} samples, dt={dt_real:.4f} ns, t_range=[{real_t[0]:.2f}, {real_t[-1]:.2f}] ns, Units: A/D counts")

    out_png = args.output or Path('output_test/01_raw_comparison.png')
    stats = plot_raw_comparison(syn_sig, syn_t, dt_syn, real_sig, real_t, dt_real, out_png)

    print(f"\n{'='*70}")
    print("RAW WAVEFORM STATISTICS")
    print(f"{'='*70}")
    print(f"\nSynthetic (V/m - physical units):")
    print(f"  Peak amplitude: {stats['syn_peak']:.4e} V/m @ {stats['syn_peak_time']:.2f} ns")
    print(f"  Time window: {syn_t[0]:.2f} to {syn_t[-1]:.2f} ns ({syn_t[-1]:.1f} ns total)")
    print(f"  Resolution: {dt_syn:.4f} ns per sample")

    print(f"\nReal DZT (A/D counts - raw hardware counts):")
    print(f"  Peak amplitude: {stats['real_peak']:.4e} counts @ {stats['real_peak_time']:.2f} ns")
    print(f"  Time window: {real_t[0]:.2f} to {real_t[-1]:.2f} ns ({real_t[-1]:.1f} ns total)")
    print(f"  Resolution: {dt_real:.4f} ns per sample")

    print(f"\nObservations:")
    print(f"  • Time offset: {stats['real_peak_time'] - stats['syn_peak_time']:.2f} ns (real is later)")
    print(f"  • Units: Synthetic=V/m (physical), Real=A/D counts (hardware)")
    print(f"  • Sampling: Synthetic is {dt_real/dt_syn:.1f}x finer resolution than real")
    print(f"  • Shape: [Visual inspection from plots needed]")


if __name__ == "__main__":
    main()
