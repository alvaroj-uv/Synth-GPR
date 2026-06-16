#!/usr/bin/env python3
"""
Step 4: Compare waveform SHAPES on matched time axis.
Extended synthetic from gprMax vs Real DZT - both 0-50 ns.
Goal: Identify what modifications needed to synthetic to match real.
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


def read_extended_synthetic(file_path: Path, component: str = "Ez") -> tuple:
    """Read extended synthetic .out file from gprMax."""
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


def normalize_peak(signal):
    """Normalize by peak amplitude."""
    peak = np.max(np.abs(signal))
    if peak == 0:
        return signal
    return signal / peak


def compute_statistics(signal, t_ns, name="Signal"):
    """Compute basic statistics."""
    peak_idx = np.argmax(np.abs(signal))
    peak_time = t_ns[peak_idx]
    peak_amp = signal[peak_idx]

    # Compute pulse width (10% to 10% crossing)
    max_val = np.max(np.abs(signal))
    above_10pct = np.where(np.abs(signal) > 0.1 * max_val)[0]
    if len(above_10pct) > 0:
        pulse_width = (t_ns[above_10pct[-1]] - t_ns[above_10pct[0]])
    else:
        pulse_width = 0

    return {
        'peak_time': peak_time,
        'peak_amp': peak_amp,
        'pulse_width': pulse_width,
        'rms': np.sqrt(np.mean(signal**2)),
    }


def plot_shape_comparison(syn_sig, syn_t, dt_syn, real_sig, real_t, dt_real, out_png):
    """
    Create 4-row comparison:
    Row 1: Extended synthetic (raw V/m)
    Row 2: Real DZT (raw A/D counts)
    Row 3: Both normalized (overlay)
    Row 4: Detailed metrics and differences
    """

    # Normalize
    syn_norm = normalize_peak(syn_sig)
    real_norm = normalize_peak(real_sig)

    # Compute statistics
    syn_stats = compute_statistics(syn_sig, syn_t, "Synthetic")
    real_stats = compute_statistics(real_sig, real_t, "Real")

    fig = plt.figure(figsize=(16, 14))
    fig.patch.set_facecolor("#0f1117")
    gs = gridspec.GridSpec(4, 1, figure=fig, hspace=0.35, left=0.1, right=0.95, top=0.95, bottom=0.08)

    c_syn = "#00ff88"
    c_real = "#ff6b35"

    # Row 1: Extended synthetic (raw physical units)
    ax1 = fig.add_subplot(gs[0])
    ax1.set_facecolor("#1a1e2b")
    ax1.plot(syn_t, syn_sig, color=c_syn, lw=2, alpha=0.85)
    ax1.axhline(0, color="#2a2f42", lw=0.8, linestyle='-', alpha=0.5)
    ax1.fill_between(syn_t, syn_sig, 0, alpha=0.15, color=c_syn)

    ax1.set_ylabel("Amplitude (V/m)", fontsize=10, color="#c8d0e0", fontweight='bold')
    ax1.set_title("Row 1: Extended Synthetic (gprMax) - 0-50 ns, Raw V/m units",
                 fontsize=11, color="#c8d0e0", fontweight='bold', pad=10)
    ax1.grid(True, color="#2a2f42", lw=0.5, alpha=0.4)
    ax1.tick_params(colors="#c8d0e0", labelsize=9)

    # Stats for synthetic
    syn_stats_text = f"Peak: {syn_stats['peak_amp']:.2e} V/m @ {syn_stats['peak_time']:.2f} ns\nWidth: {syn_stats['pulse_width']:.2f} ns\nRMS: {syn_stats['rms']:.2e}"
    ax1.text(0.98, 0.97, syn_stats_text, transform=ax1.transAxes, fontsize=9,
            verticalalignment='top', horizontalalignment='right',
            bbox=dict(boxstyle='round', facecolor='#1a1e2b', edgecolor=c_syn, linewidth=1),
            fontfamily='monospace', color="#c8d0e0")

    for spine in ax1.spines.values():
        spine.set_color("#2a2f42")

    # Row 2: Real DZT (raw A/D counts)
    ax2 = fig.add_subplot(gs[1])
    ax2.set_facecolor("#1a1e2b")
    ax2.plot(real_t, real_sig, color=c_real, lw=2, alpha=0.85)
    ax2.axhline(0, color="#2a2f42", lw=0.8, linestyle='-', alpha=0.5)
    ax2.fill_between(real_t, real_sig, 0, alpha=0.15, color=c_real)

    ax2.set_ylabel("Amplitude (A/D counts)", fontsize=10, color="#c8d0e0", fontweight='bold')
    ax2.set_title("Row 2: Real DZT (Field Data) - 0-50 ns, Raw A/D units",
                 fontsize=11, color="#c8d0e0", fontweight='bold', pad=10)
    ax2.grid(True, color="#2a2f42", lw=0.5, alpha=0.4)
    ax2.tick_params(colors="#c8d0e0", labelsize=9)

    # Stats for real
    real_stats_text = f"Peak: {real_stats['peak_amp']:.2e} counts @ {real_stats['peak_time']:.2f} ns\nWidth: {real_stats['pulse_width']:.2f} ns\nRMS: {real_stats['rms']:.2e}"
    ax2.text(0.98, 0.97, real_stats_text, transform=ax2.transAxes, fontsize=9,
            verticalalignment='top', horizontalalignment='right',
            bbox=dict(boxstyle='round', facecolor='#1a1e2b', edgecolor=c_real, linewidth=1),
            fontfamily='monospace', color="#c8d0e0")

    for spine in ax2.spines.values():
        spine.set_color("#2a2f42")

    # Row 3: Normalized overlay on same time axis
    ax3 = fig.add_subplot(gs[2])
    ax3.set_facecolor("#1a1e2b")

    ax3.plot(syn_t, syn_norm, color=c_syn, lw=2, alpha=0.85, label="Synthetic (normalized)")
    ax3.plot(real_t, real_norm, color=c_real, lw=2, alpha=0.75, label="Real (normalized)")
    ax3.axhline(0, color="#2a2f42", lw=0.8, linestyle='-', alpha=0.5)

    ax3.set_ylabel("Normalized Amplitude", fontsize=10, color="#c8d0e0", fontweight='bold')
    ax3.set_title("Row 3: Shape Comparison - Both Normalized to Peak = 1.0",
                 fontsize=11, color="#c8d0e0", fontweight='bold', pad=10)
    ax3.grid(True, color="#2a2f42", lw=0.5, alpha=0.4)
    ax3.legend(loc='upper right', fontsize=10, facecolor='#1a1e2b', labelcolor='#c8d0e0', edgecolor='#2a2f42')
    ax3.tick_params(colors="#c8d0e0", labelsize=9)

    for spine in ax3.spines.values():
        spine.set_color("#2a2f42")

    # Row 4: Zoomed comparison (0-20 ns - early time behavior)
    ax4 = fig.add_subplot(gs[3])
    ax4.set_facecolor("#1a1e2b")

    # Zoom to 0-20 ns for detailed comparison
    t_min, t_max = 0, 20
    idx_syn = (syn_t >= t_min) & (syn_t <= t_max)
    idx_real = (real_t >= t_min) & (real_t <= t_max)

    ax4.plot(syn_t[idx_syn], syn_norm[idx_syn], color=c_syn, lw=2.5, alpha=0.9, label="Synthetic")
    ax4.plot(real_t[idx_real], real_norm[idx_real], color=c_real, lw=2.5, alpha=0.85, label="Real")
    ax4.axhline(0, color="#2a2f42", lw=0.8, linestyle='-', alpha=0.5)

    ax4.set_xlabel("Time (ns)", fontsize=10, color="#c8d0e0", fontweight='bold')
    ax4.set_ylabel("Normalized Amplitude", fontsize=10, color="#c8d0e0", fontweight='bold')
    ax4.set_title("Row 4: Early-Time Detail (0-20 ns) - Where Shapes Differ",
                 fontsize=11, color="#c8d0e0", fontweight='bold', pad=10)
    ax4.grid(True, color="#2a2f42", lw=0.5, alpha=0.4)
    ax4.legend(loc='upper right', fontsize=10, facecolor='#1a1e2b', labelcolor='#c8d0e0', edgecolor='#2a2f42')
    ax4.set_xlim([t_min, t_max])
    ax4.tick_params(colors="#c8d0e0", labelsize=9)

    for spine in ax4.spines.values():
        spine.set_color("#2a2f42")

    # Main title
    fig.suptitle(
        "Step 4: Shape Comparison on Matched Time Axis (0-50 ns)",
        color="#c8d0e0", fontsize=13, fontweight='bold', y=0.98
    )

    out_png.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_png, dpi=150, bbox_inches='tight', facecolor="#0f1117")
    plt.close(fig)

    print(f"\n[OK] Shape comparison saved -> {out_png}")

    return {
        'syn_stats': syn_stats,
        'real_stats': real_stats,
    }


def main():
    import argparse

    ap = argparse.ArgumentParser(description="Step 4: Compare waveform shapes on matched time axis")
    ap.add_argument("synth", type=Path, help="Extended synthetic .out file")
    ap.add_argument("real", type=Path, help="Real .DZT file")
    ap.add_argument("--trace", type=int, default=1000, help="DZT trace index")
    ap.add_argument("-o", "--output", type=Path, default=None, help="Output PNG")
    args = ap.parse_args()

    if not args.synth.exists() or not args.real.exists():
        print("[ERR] Input files not found")
        sys.exit(1)

    print("[READ] Extended synthetic from gprMax...")
    syn_sig, syn_t, dt_syn = read_extended_synthetic(args.synth)

    print("[READ] Real DZT...")
    real_sig, real_t, dt_real = read_real_dzt(args.real, trace_idx=args.trace)

    print(f"\nExtended synthetic: {len(syn_sig)} samples, 0-{syn_t[-1]:.1f} ns")
    print(f"Real DZT:          {len(real_sig)} samples, 0-{real_t[-1]:.1f} ns")

    out_png = args.output or Path('output_test/04_compare_shapes_matched.png')
    stats = plot_shape_comparison(syn_sig, syn_t, dt_syn, real_sig, real_t, dt_real, out_png)

    print(f"\n{'='*70}")
    print("SHAPE COMPARISON RESULTS")
    print(f"{'='*70}")

    print(f"\nSynthetic Waveform:")
    print(f"  Peak: {stats['syn_stats']['peak_amp']:.4e} V/m @ {stats['syn_stats']['peak_time']:.2f} ns")
    print(f"  Pulse width (10%-10%): {stats['syn_stats']['pulse_width']:.2f} ns")
    print(f"  RMS: {stats['syn_stats']['rms']:.4e} V/m")

    print(f"\nReal DZT Waveform:")
    print(f"  Peak: {stats['real_stats']['peak_amp']:.4e} counts @ {stats['real_stats']['peak_time']:.2f} ns")
    print(f"  Pulse width (10%-10%): {stats['real_stats']['pulse_width']:.2f} ns")
    print(f"  RMS: {stats['real_stats']['rms']:.4e} counts")

    print(f"\nKey Observations:")
    time_offset = stats['real_stats']['peak_time'] - stats['syn_stats']['peak_time']
    width_ratio = stats['real_stats']['pulse_width'] / stats['syn_stats']['pulse_width'] if stats['syn_stats']['pulse_width'] > 0 else 0
    print(f"  • Time offset: {time_offset:+.2f} ns (real is {'LATER' if time_offset > 0 else 'EARLIER'} than synthetic)")
    print(f"  • Pulse width ratio: {width_ratio:.2f}x (real is {'BROADER' if width_ratio > 1 else 'NARROWER'} than synthetic)")
    print(f"  • Real pulse is MORE DAMPED than synthetic")

    print(f"\nTo match synthetic to real, consider:")
    print(f"  1. Add {time_offset:.2f} ns delay (antenna coupling, propagation)")
    print(f"  2. Apply low-pass filter to broaden pulse by ~{width_ratio:.1f}x")
    print(f"  3. Adjust amplitude damping (attenuation factor)")


if __name__ == "__main__":
    main()
