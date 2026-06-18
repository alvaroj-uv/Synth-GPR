#!/usr/bin/env python3
"""
Step 2: Match time windows between synthetic and real.
Goal: Both waveforms on same time axis for fair comparison.
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


def extend_synthetic(syn_sig, syn_t, dt_syn, target_duration_ns):
    """
    Extend synthetic with zeros to match target duration.
    """
    current_duration = syn_t[-1] - syn_t[0]
    samples_needed = int(np.round((target_duration_ns - current_duration) / dt_syn))

    if samples_needed > 0:
        # Add zeros to the end
        extended_sig = np.concatenate([syn_sig, np.zeros(samples_needed)])
        extended_t = np.arange(len(extended_sig)) * dt_syn
    else:
        extended_sig = syn_sig
        extended_t = syn_t

    return extended_sig, extended_t


def plot_time_match(syn_sig, syn_t, dt_syn, real_sig, real_t, dt_real, out_png):
    """
    Create 3-row comparison:
    Row 1: Original (mismatched time windows)
    Row 2: Extended synthetic (matched time windows)
    Row 3: Direct overlay comparison
    """

    # Extend synthetic to match real's duration
    target_duration = real_t[-1]
    syn_extended, syn_t_extended = extend_synthetic(syn_sig, syn_t, dt_syn, target_duration)

    fig = plt.figure(figsize=(16, 12))
    fig.patch.set_facecolor("#0f1117")
    gs = gridspec.GridSpec(3, 1, figure=fig, hspace=0.35, left=0.1, right=0.95, top=0.95, bottom=0.08)

    c_syn = "#00d4ff"
    c_ext = "#00ff88"
    c_real = "#ff6b35"

    # Row 1: Original windows (mismatched)
    ax1 = fig.add_subplot(gs[0])
    ax1.set_facecolor("#1a1e2b")

    ax1_twin = ax1.twinx()

    # Plot on separate y-axes to show scale difference
    ax1.plot(syn_t, syn_sig, color=c_syn, lw=2, alpha=0.85, label=f"Synthetic (V/m)")
    ax1.set_ylabel("Synthetic (V/m)", fontsize=10, color=c_syn, fontweight='bold')
    ax1.tick_params(axis='y', labelcolor=c_syn)

    ax1_twin.plot(real_t, real_sig, color=c_real, lw=2, alpha=0.75, label=f"Real (counts)")
    ax1_twin.set_ylabel("Real DZT (A/D counts)", fontsize=10, color=c_real, fontweight='bold')
    ax1_twin.tick_params(axis='y', labelcolor=c_real)

    ax1.axhline(0, color="#2a2f42", lw=0.8, linestyle='-', alpha=0.3)
    ax1.axvline(syn_t[-1], color=c_syn, lw=1.5, linestyle='--', alpha=0.5, label=f"Syn end: {syn_t[-1]:.1f} ns")
    ax1.axvline(real_t[-1], color=c_real, lw=1.5, linestyle='--', alpha=0.5, label=f"Real end: {real_t[-1]:.1f} ns")

    ax1.set_xlabel("Time (ns)", fontsize=10, color="#c8d0e0", fontweight='bold')
    ax1.set_title(f"Row 1: ORIGINAL - Mismatched Time Windows (Syn: 0-{syn_t[-1]:.1f}ns vs Real: 0-{real_t[-1]:.1f}ns)",
                 fontsize=11, color="#c8d0e0", fontweight='bold', pad=10)
    ax1.grid(True, color="#2a2f42", lw=0.5, alpha=0.4)
    ax1.legend(loc='upper left', fontsize=9, facecolor='#1a1e2b', labelcolor='#c8d0e0', edgecolor='#2a2f42')

    for spine in ax1.spines.values():
        spine.set_color("#2a2f42")
    for spine in ax1_twin.spines.values():
        spine.set_color("#2a2f42")

    # Row 2: Extended synthetic (matched windows)
    ax2 = fig.add_subplot(gs[1])
    ax2.set_facecolor("#1a1e2b")

    ax2.plot(syn_t_extended, syn_extended, color=c_ext, lw=1.8, alpha=0.85, label="Synthetic (extended)")
    ax2.axhline(0, color="#2a2f42", lw=0.8, linestyle='-', alpha=0.3)
    ax2.axvline(syn_t[-1], color=c_syn, lw=1.2, linestyle='--', alpha=0.6, label="Original end")

    ax2.set_ylabel("Amplitude (V/m)", fontsize=10, color="#c8d0e0", fontweight='bold')
    ax2.set_title(f"Row 2: Extended Synthetic - Added {len(syn_extended) - len(syn_sig)} zeros to reach {syn_t_extended[-1]:.1f} ns",
                 fontsize=11, color="#c8d0e0", fontweight='bold', pad=10)
    ax2.grid(True, color="#2a2f42", lw=0.5, alpha=0.4)
    ax2.legend(loc='upper right', fontsize=9, facecolor='#1a1e2b', labelcolor='#c8d0e0', edgecolor='#2a2f42')
    ax2.tick_params(colors="#c8d0e0", labelsize=9)

    for spine in ax2.spines.values():
        spine.set_color("#2a2f42")

    # Row 3: Overlay with matched windows
    ax3 = fig.add_subplot(gs[2])
    ax3.set_facecolor("#1a1e2b")

    # Normalize for visual comparison (different units)
    syn_extended_norm = syn_extended / np.max(np.abs(syn_extended))
    real_norm = real_sig / np.max(np.abs(real_sig))

    ax3.plot(syn_t_extended, syn_extended_norm, color=c_ext, lw=1.8, alpha=0.85, label="Synthetic (normalized)")
    ax3.plot(real_t, real_norm, color=c_real, lw=1.8, alpha=0.75, label="Real DZT (normalized)")
    ax3.axhline(0, color="#2a2f42", lw=0.8, linestyle='-', alpha=0.3)

    ax3.set_xlabel("Time (ns)", fontsize=10, color="#c8d0e0", fontweight='bold')
    ax3.set_ylabel("Normalized Amplitude", fontsize=10, color="#c8d0e0", fontweight='bold')
    ax3.set_title(f"Row 3: MATCHED TIME WINDOWS - Both on same axis (normalized for visibility)",
                 fontsize=11, color="#c8d0e0", fontweight='bold', pad=10)
    ax3.grid(True, color="#2a2f42", lw=0.5, alpha=0.4)
    ax3.legend(loc='upper right', fontsize=9, facecolor='#1a1e2b', labelcolor='#c8d0e0', edgecolor='#2a2f42')
    ax3.tick_params(colors="#c8d0e0", labelsize=9)

    for spine in ax3.spines.values():
        spine.set_color("#2a2f42")

    # Main title
    fig.suptitle(
        "Step 2: Match Time Windows - Extend Synthetic to Match Real Duration",
        color="#c8d0e0", fontsize=12, fontweight='bold', y=0.98
    )

    out_png.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_png, dpi=150, bbox_inches='tight', facecolor="#0f1117")
    plt.close(fig)

    print(f"\n[OK] Time-matched comparison saved -> {out_png}")

    return {
        'original_duration_syn': syn_t[-1],
        'target_duration': real_t[-1],
        'extended_duration_syn': syn_t_extended[-1],
        'samples_added': len(syn_extended) - len(syn_sig),
    }


def main():
    import argparse

    ap = argparse.ArgumentParser(description="Step 2: Match time windows")
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

    out_png = args.output or Path('output_test/02_match_time_window.png')
    metrics = plot_time_match(syn_sig, syn_t, dt_syn, real_sig, real_t, dt_real, out_png)

    print(f"\n{'='*70}")
    print("TIME WINDOW ANALYSIS")
    print(f"{'='*70}")

    print(f"\nOriginal windows:")
    print(f"  Synthetic: 0 to {metrics['original_duration_syn']:.1f} ns ({syn_sig.shape[0]} samples @ {dt_syn:.4f} ns/sample)")
    print(f"  Real DZT:  0 to {metrics['target_duration']:.1f} ns ({real_sig.shape[0]} samples @ {dt_real:.4f} ns/sample)")
    print(f"  Mismatch:  {metrics['target_duration'] - metrics['original_duration_syn']:.1f} ns")

    print(f"\nExtended synthetic:")
    print(f"  New duration: 0 to {metrics['extended_duration_syn']:.1f} ns")
    print(f"  Samples added: {metrics['samples_added']} zeros")
    print(f"  Total samples: {len(syn_sig) + metrics['samples_added']}")

    print(f"\nNow both waveforms are on the SAME time axis (0-{metrics['target_duration']:.1f} ns)")
    print(f"Ready for shape comparison in next step.")


if __name__ == "__main__":
    main()
