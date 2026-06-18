#!/usr/bin/env python3
"""
Match time axes: Resample synthetic to real's dt, align to same time window.
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


def read_file(file_path: Path, trace_idx: int = 1000, component: str = "Ez") -> tuple:
    """Read A-scan from .out (synthetic) or .DZT (real) file."""
    suffix = file_path.suffix.upper()

    if suffix == ".OUT":
        data = read_ascan(file_path, component)
        signal = data['signal']
        dt = data['dt']
        t_ns = np.arange(len(signal)) * dt * 1e9
        return signal, t_ns, dt * 1e9

    elif suffix == ".DZT" or suffix == ".DTZ":
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

    else:
        raise ValueError(f"Unsupported file type: {suffix}")


def normalize_peak(signal):
    """Normalize by peak amplitude."""
    peak = np.max(np.abs(signal))
    if peak == 0:
        return signal
    return signal / peak


def match_timeline(syn_sig, syn_t, real_sig, real_t, dt_syn_ns, dt_real_ns, out_png):
    """
    Match time axes:
    1. Apply polarity flip to synthetic
    2. Find peaks
    3. Resample synthetic to real's dt
    4. Align peaks on common timeline
    5. Pad/trim to same length
    """

    # Step 1: Polarity flip
    syn_flipped = -syn_sig

    # Step 2: Find peaks
    peak_idx_syn = np.argmax(np.abs(syn_flipped))
    peak_idx_real = np.argmax(np.abs(real_sig))
    peak_time_syn = syn_t[peak_idx_syn]
    peak_time_real = real_t[peak_idx_real]

    print(f"[OK] Peak synthetic: idx={peak_idx_syn} t={peak_time_syn:.3f} ns")
    print(f"[OK] Peak real:     idx={peak_idx_real} t={peak_time_real:.3f} ns")

    # Step 3: Resample synthetic to real's dt
    # Create interpolation function on synthetic's original time grid
    f_syn = interp1d(syn_t, syn_flipped, kind='cubic', bounds_error=False, fill_value=0)

    # New time grid: use real's dt, but span from synthetic start to end
    t_min = min(syn_t[0], real_t[0])
    t_max = max(syn_t[-1], real_t[-1])
    t_resampled = np.arange(int((t_max - t_min) / dt_real_ns) + 1) * dt_real_ns + t_min

    syn_resampled = f_syn(t_resampled)

    print(f"\n[OK] Resampled synthetic:")
    print(f"     Original: {len(syn_flipped)} samples, dt={dt_syn_ns:.6f} ns")
    print(f"     Resampled: {len(syn_resampled)} samples, dt={dt_real_ns:.6f} ns")
    print(f"     Time span: [{t_min:.3f}, {t_max:.3f}] ns")

    # Step 4: Find peaks on resampled timeline
    peak_idx_syn_rs = np.argmax(np.abs(syn_resampled))
    peak_time_syn_rs = t_resampled[peak_idx_syn_rs]

    # Find corresponding index in real on resampled timeline
    t_real_on_rs = real_t + (t_resampled[0] - real_t[0])  # Shift real to same reference
    peak_idx_real_on_rs = peak_idx_real  # Index stays same, just shifted timeline
    peak_time_real_on_rs = peak_time_real

    time_diff = peak_time_real_on_rs - peak_time_syn_rs
    shift_samples = int(round(time_diff / dt_real_ns))

    print(f"\n[OK] Peak alignment on resampled timeline:")
    print(f"     Synthetic peak: idx={peak_idx_syn_rs} t={peak_time_syn_rs:.3f} ns")
    print(f"     Real peak:      idx={peak_idx_real_on_rs} t={peak_time_real_on_rs:.3f} ns")
    print(f"     Time difference: {time_diff:.3f} ns = {shift_samples} samples")

    # Step 5: Align peaks by padding
    if shift_samples > 0:
        # Real is later, pad synthetic at beginning
        syn_aligned = np.concatenate([np.zeros(shift_samples), syn_resampled])
        real_aligned = real_sig
    else:
        # Synthetic is later, pad real at beginning
        syn_aligned = syn_resampled
        real_aligned = np.concatenate([np.zeros(-shift_samples), real_sig])

    # Pad both to same length
    max_len = max(len(syn_aligned), len(real_aligned))
    syn_padded = np.pad(syn_aligned, (0, max_len - len(syn_aligned)), mode='constant')
    real_padded = np.pad(real_aligned, (0, max_len - len(real_aligned)), mode='constant')

    # Create final common timeline (use real's dt)
    t_final = np.arange(max_len) * dt_real_ns

    # Step 6: Normalize
    syn_norm = normalize_peak(syn_padded)
    real_norm = normalize_peak(real_padded)

    # Step 7: Compute correlation
    corr = np.corrcoef(syn_norm, real_norm)[0, 1]
    print(f"\n[OK] Normalized correlation: {corr:.6f}")

    # ========================================================================
    # PLOT: 3-row figure
    # ========================================================================
    fig = plt.figure(figsize=(16, 12))
    fig.patch.set_facecolor("#0f1117")
    gs = gridspec.GridSpec(3, 1, figure=fig, hspace=0.35, left=0.1, right=0.95, top=0.96, bottom=0.06)

    c_syn = "#00d9ff"   # Cyan
    c_real = "#ff6b35"  # Orange-red

    # Window for display (first 50 ns or full, whichever is smaller)
    display_ns = min(50, t_final[-1])
    mask = t_final <= display_ns

    # ========================================================================
    # Row 1: Synthetic (resampled, flipped, aligned)
    # ========================================================================
    ax1 = fig.add_subplot(gs[0])
    ax1.set_facecolor("#1a1e2b")
    ax1.plot(t_final[mask], syn_norm[mask], color=c_syn, lw=1.5, alpha=0.85, label="Synthetic (420 MHz, resampled to real dt)")
    ax1.axhline(0, color="#2a2f42", lw=0.8, linestyle='-', alpha=0.5)
    ax1.set_ylabel("Normalized Amplitude", fontsize=10, color="#c8d0e0", fontweight='bold')
    ax1.set_title(f"Row 1: Synthetic (Resampled to dt={dt_real_ns:.6f} ns, Polarity Flipped)",
                 fontsize=11, color="#c8d0e0", fontweight='bold', pad=8)
    ax1.grid(True, color="#2a2f42", lw=0.5, alpha=0.4)
    ax1.legend(loc='upper right', fontsize=9, facecolor='#1a1e2b', labelcolor='#c8d0e0', edgecolor='#2a2f42')
    ax1.tick_params(colors="#c8d0e0", labelsize=9)
    for spine in ax1.spines.values():
        spine.set_color("#2a2f42")

    # ========================================================================
    # Row 2: Real
    # ========================================================================
    ax2 = fig.add_subplot(gs[1])
    ax2.set_facecolor("#1a1e2b")
    ax2.plot(t_final[mask], real_norm[mask], color=c_real, lw=1.5, alpha=0.85, label="Real (Puerto-Limache DZT)")
    ax2.axhline(0, color="#2a2f42", lw=0.8, linestyle='-', alpha=0.5)
    ax2.set_ylabel("Normalized Amplitude", fontsize=10, color="#c8d0e0", fontweight='bold')
    ax2.set_title(f"Row 2: Real (dt={dt_real_ns:.6f} ns, Peak-Aligned with Synthetic)",
                 fontsize=11, color="#c8d0e0", fontweight='bold', pad=8)
    ax2.grid(True, color="#2a2f42", lw=0.5, alpha=0.4)
    ax2.legend(loc='upper right', fontsize=9, facecolor='#1a1e2b', labelcolor='#c8d0e0', edgecolor='#2a2f42')
    ax2.tick_params(colors="#c8d0e0", labelsize=9)
    for spine in ax2.spines.values():
        spine.set_color("#2a2f42")

    # ========================================================================
    # Row 3: Overlay
    # ========================================================================
    ax3 = fig.add_subplot(gs[2])
    ax3.set_facecolor("#1a1e2b")
    ax3.plot(t_final[mask], syn_norm[mask], color=c_syn, lw=1.5, alpha=0.85, label="Synthetic")
    ax3.plot(t_final[mask], real_norm[mask], color=c_real, lw=1.5, alpha=0.85, label="Real")
    ax3.fill_between(t_final[mask], syn_norm[mask], real_norm[mask], alpha=0.15, color="yellow", label="Difference")
    ax3.axhline(0, color="#2a2f42", lw=0.8, linestyle='-', alpha=0.5)
    ax3.set_xlabel("Time (ns)", fontsize=10, color="#c8d0e0", fontweight='bold')
    ax3.set_ylabel("Normalized Amplitude", fontsize=10, color="#c8d0e0", fontweight='bold')
    ax3.set_title(f"Row 3: Overlay (Matched Timeline, Correlation: {corr:.6f})",
                 fontsize=11, color="#c8d0e0", fontweight='bold', pad=8)
    ax3.grid(True, color="#2a2f42", lw=0.5, alpha=0.4)
    ax3.legend(loc='upper right', fontsize=9, facecolor='#1a1e2b', labelcolor='#c8d0e0', edgecolor='#2a2f42')
    ax3.tick_params(colors="#c8d0e0", labelsize=9)
    for spine in ax3.spines.values():
        spine.set_color("#2a2f42")

    # Main title
    fig.suptitle(
        "Matched Timeline: Synthetic Resampled to Real's dt\n"
        f"420 MHz Gaussian Bistatic 30mm | Polarity Flipped | Peaks Aligned",
        color="#c8d0e0", fontsize=13, fontweight='bold', y=0.995
    )

    # Save
    out_png.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_png, dpi=150, bbox_inches='tight', facecolor="#0f1117")
    plt.close(fig)

    print(f"\n[OK] Saved: {out_png}")

    # ========================================================================
    # FULL WINDOW FIGURE
    # ========================================================================
    fig2, axes = plt.subplots(2, 1, figsize=(16, 10))
    fig2.patch.set_facecolor("#0f1117")

    for ax in axes:
        ax.set_facecolor("#1a1e2b")
        ax.grid(True, color="#2a2f42", lw=0.5, alpha=0.4)
        ax.tick_params(colors="#c8d0e0", labelsize=9)
        for spine in ax.spines.values():
            spine.set_color("#2a2f42")

    # Full window
    axes[0].plot(t_final, syn_norm, color=c_syn, lw=1.0, alpha=0.85, label="Synthetic (resampled)")
    axes[0].axhline(0, color="#2a2f42", lw=0.8, linestyle='-', alpha=0.5)
    axes[0].set_ylabel("Normalized Amplitude", fontsize=10, color="#c8d0e0", fontweight='bold')
    axes[0].set_title("Full Window: Synthetic (Resampled to Real's dt)", fontsize=11, color="#c8d0e0", fontweight='bold')
    axes[0].legend(loc='upper right', fontsize=9, facecolor='#1a1e2b', labelcolor='#c8d0e0', edgecolor='#2a2f42')

    axes[1].plot(t_final, real_norm, color=c_real, lw=1.0, alpha=0.85, label="Real (DZT)")
    axes[1].axhline(0, color="#2a2f42", lw=0.8, linestyle='-', alpha=0.5)
    axes[1].set_xlabel("Time (ns)", fontsize=10, color="#c8d0e0", fontweight='bold')
    axes[1].set_ylabel("Normalized Amplitude", fontsize=10, color="#c8d0e0", fontweight='bold')
    axes[1].set_title("Full Window: Real (Peak-Aligned with Synthetic)", fontsize=11, color="#c8d0e0", fontweight='bold')
    axes[1].legend(loc='upper right', fontsize=9, facecolor='#1a1e2b', labelcolor='#c8d0e0', edgecolor='#2a2f42')

    fig2.suptitle(
        f"Matched Timeline - Full Window | Correlation: {corr:.6f}",
        color="#c8d0e0", fontsize=12, fontweight='bold', y=0.995
    )

    out_png_full = out_png.parent / (out_png.stem + "_fullwindow.png")
    fig2.savefig(out_png_full, dpi=150, bbox_inches='tight', facecolor="#0f1117")
    plt.close(fig2)

    print(f"[OK] Saved: {out_png_full}")

    return corr, time_diff, shift_samples


def main():
    import argparse

    ap = argparse.ArgumentParser(
        description="Match time axes: resample synthetic to real's dt, align peaks")
    ap.add_argument("synth", type=Path, help="Synthetic .out file")
    ap.add_argument("real", type=Path, help="Real .DZT file")
    ap.add_argument("--trace", type=int, default=1000, help="DZT trace index")
    ap.add_argument("-o", "--output", type=Path, default=None, help="Output PNG path")
    args = ap.parse_args()

    # Validate
    if not args.synth.exists():
        print(f"[ERR] Synthetic file not found: {args.synth}")
        sys.exit(1)
    if not args.real.exists():
        print(f"[ERR] Real file not found: {args.real}")
        sys.exit(1)

    # Load
    print(f"[READ] Synthetic: {args.synth.name}")
    syn_sig, syn_t, dt_syn = read_file(args.synth)

    print(f"[READ] Real DZT (trace #{args.trace}): {args.real.name}")
    real_sig, real_t, dt_real = read_file(args.real, trace_idx=args.trace)

    print(f"\nBefore resampling:")
    print(f"  Synthetic: {len(syn_sig)} samples, dt={dt_syn:.6f} ns, span=[{syn_t[0]:.3f}, {syn_t[-1]:.3f}] ns")
    print(f"  Real DZT:  {len(real_sig)} samples, dt={dt_real:.6f} ns, span=[{real_t[0]:.3f}, {real_t[-1]:.3f}] ns")

    # Process
    if args.output:
        out_png = args.output.with_suffix('.png')
    else:
        out_png = Path('output_test') / f"15_match_timeline.png"

    corr, time_diff, shift_samples = match_timeline(syn_sig, syn_t, real_sig, real_t, dt_syn, dt_real, out_png)

    print(f"\n{'='*70}")
    print("MATCHED TIMELINE ANALYSIS")
    print(f"{'='*70}")
    print(f"Configuration: 420 MHz Gaussian Bistatic 30mm")
    print(f"Polarity fix: Multiply synthetic by -1")
    print(f"Resampling: Synthetic {dt_syn:.6f} ns -> {dt_real:.6f} ns (real's dt)")
    print(f"Peak shift: {time_diff:.3f} ns ({shift_samples} samples)")
    print(f"Normalized correlation: {corr:.6f}")
    print(f"{'='*70}")


if __name__ == "__main__":
    main()
