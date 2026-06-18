#!/usr/bin/env python3
"""
Polarity-flipped synthetic vs real with peak alignment and padding.
Uses optimized 420 MHz Gaussian bistatic 30mm synthetic.
Flips polarity (multiply by -1), aligns peaks, pads to match.
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


def plot_polarity_flip_alignment(syn_sig, syn_t, real_sig, real_t, dt_syn_ns, out_png):
    """
    Create 3-row comparison with polarity flip and peak alignment:
    Row 1: Synthetic (polarity flipped)
    Row 2: Real (DZT)
    Row 3: Overlay with peak alignment
    """

    # Step 1: Apply polarity flip (multiply by -1)
    syn_flipped = -syn_sig

    # Step 2: Find peaks
    peak_idx_syn = np.argmax(np.abs(syn_flipped))
    peak_idx_real = np.argmax(np.abs(real_sig))
    peak_time_syn = syn_t[peak_idx_syn]
    peak_time_real = real_t[peak_idx_real]

    print(f"[OK] Peak synthetic: idx={peak_idx_syn} t={peak_time_syn:.3f} ns")
    print(f"[OK] Peak real:     idx={peak_idx_real} t={peak_time_real:.3f} ns")

    # Step 3: Calculate shift to align peaks
    time_shift_ns = peak_time_real - peak_time_syn
    shift_samples_real = int(round(time_shift_ns / (real_t[1] - real_t[0])))

    print(f"[OK] Time shift: {time_shift_ns:.3f} ns = {shift_samples_real} real samples")

    # Step 4: Pad real to align
    if shift_samples_real > 0:
        real_aligned = np.concatenate([np.zeros(shift_samples_real), real_sig])
    else:
        real_aligned = real_sig[-shift_samples_real:] if shift_samples_real < 0 else real_sig

    # Step 5: Pad to same length
    max_len = max(len(syn_flipped), len(real_aligned))
    syn_padded = np.pad(syn_flipped, (0, max_len - len(syn_flipped)), mode='constant')
    real_padded = np.pad(real_aligned, (0, max_len - len(real_aligned)), mode='constant')

    # Use real dt as reference
    dt_real_ns = real_t[1] - real_t[0] if len(real_t) > 1 else 0.0978
    t_common = np.arange(max_len) * dt_real_ns

    # Step 6: Normalize
    syn_norm = normalize_peak(syn_padded)
    real_norm = normalize_peak(real_padded)

    # Step 7: Compute correlation
    corr = np.corrcoef(syn_norm, real_norm)[0, 1]
    print(f"[OK] Normalized correlation: {corr:.6f}")

    # ========================================================================
    # PLOT: 3-row figure
    # ========================================================================
    fig = plt.figure(figsize=(16, 12))
    fig.patch.set_facecolor("#0f1117")
    gs = gridspec.GridSpec(3, 1, figure=fig, hspace=0.35, left=0.1, right=0.95, top=0.96, bottom=0.06)

    c_syn = "#00d9ff"   # Cyan
    c_real = "#ff6b35"  # Orange-red
    c_overlay = "#ffaa00"  # Orange

    # ========================================================================
    # Row 1: Synthetic (polarity flipped)
    # ========================================================================
    ax1 = fig.add_subplot(gs[0])
    ax1.set_facecolor("#1a1e2b")
    ax1.plot(t_common[:len(syn_norm)], syn_norm, color=c_syn, lw=1.5, alpha=0.85, label="Synthetic (420 MHz, polarity flipped)")
    ax1.axvline(t_common[peak_idx_syn], color='red', linestyle='--', alpha=0.7, linewidth=2, label=f"Peak @ {peak_time_syn:.2f} ns")
    ax1.axhline(0, color="#2a2f42", lw=0.8, linestyle='-', alpha=0.5)
    ax1.set_ylabel("Normalized Amplitude", fontsize=10, color="#c8d0e0", fontweight='bold')
    ax1.set_title("Row 1: Synthetic (420 MHz Gaussian, Polarity Flipped)",
                 fontsize=11, color="#c8d0e0", fontweight='bold', pad=8)
    ax1.grid(True, color="#2a2f42", lw=0.5, alpha=0.4)
    ax1.legend(loc='upper right', fontsize=9, facecolor='#1a1e2b', labelcolor='#c8d0e0', edgecolor='#2a2f42')
    ax1.set_xlim([0, min(50, t_common[-1])])
    ax1.tick_params(colors="#c8d0e0", labelsize=9)
    for spine in ax1.spines.values():
        spine.set_color("#2a2f42")

    # ========================================================================
    # Row 2: Real (shifted to align peak)
    # ========================================================================
    ax2 = fig.add_subplot(gs[1])
    ax2.set_facecolor("#1a1e2b")
    ax2.plot(t_common[:len(real_norm)], real_norm, color=c_real, lw=1.5, alpha=0.85, label="Real (Puerto-Limache DZT)")
    aligned_peak_time = peak_time_real  # Already aligned in time
    ax2.axvline(t_common[peak_idx_real + shift_samples_real], color='red', linestyle='--', alpha=0.7, linewidth=2, label=f"Peak @ {peak_time_real:.2f} ns")
    ax2.axhline(0, color="#2a2f42", lw=0.8, linestyle='-', alpha=0.5)
    ax2.set_ylabel("Normalized Amplitude", fontsize=10, color="#c8d0e0", fontweight='bold')
    ax2.set_title("Row 2: Real (Shifted to Align Peak)",
                 fontsize=11, color="#c8d0e0", fontweight='bold', pad=8)
    ax2.grid(True, color="#2a2f42", lw=0.5, alpha=0.4)
    ax2.legend(loc='upper right', fontsize=9, facecolor='#1a1e2b', labelcolor='#c8d0e0', edgecolor='#2a2f42')
    ax2.set_xlim([0, min(50, t_common[-1])])
    ax2.tick_params(colors="#c8d0e0", labelsize=9)
    for spine in ax2.spines.values():
        spine.set_color("#2a2f42")

    # ========================================================================
    # Row 3: Overlay
    # ========================================================================
    ax3 = fig.add_subplot(gs[2])
    ax3.set_facecolor("#1a1e2b")
    ax3.plot(t_common, syn_norm, color=c_syn, lw=1.5, alpha=0.85, label="Synthetic (flipped)")
    ax3.plot(t_common, real_norm, color=c_real, lw=1.5, alpha=0.85, label="Real (aligned)")
    ax3.fill_between(t_common, syn_norm, real_norm, alpha=0.15, color="yellow", label="Waveform difference")
    ax3.axhline(0, color="#2a2f42", lw=0.8, linestyle='-', alpha=0.5)
    ax3.set_xlabel("Time (ns)", fontsize=10, color="#c8d0e0", fontweight='bold')
    ax3.set_ylabel("Normalized Amplitude", fontsize=10, color="#c8d0e0", fontweight='bold')
    ax3.set_title(f"Row 3: Overlay Comparison (Correlation: {corr:.4f})",
                 fontsize=11, color="#c8d0e0", fontweight='bold', pad=8)
    ax3.grid(True, color="#2a2f42", lw=0.5, alpha=0.4)
    ax3.legend(loc='upper right', fontsize=9, facecolor='#1a1e2b', labelcolor='#c8d0e0', edgecolor='#2a2f42')
    ax3.set_xlim([0, min(50, t_common[-1])])
    ax3.tick_params(colors="#c8d0e0", labelsize=9)
    for spine in ax3.spines.values():
        spine.set_color("#2a2f42")

    # Main title
    fig.suptitle(
        "Polarity-Flipped Synthetic vs Real: Peak-Aligned Comparison\n"
        f"420 MHz Gaussian Bistatic 30mm | Time Shift: {time_shift_ns:.3f} ns",
        color="#c8d0e0", fontsize=13, fontweight='bold', y=0.995
    )

    # Save
    out_png.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_png, dpi=150, bbox_inches='tight', facecolor="#0f1117")
    plt.close(fig)

    print(f"[OK] Saved: {out_png}")

    return corr, time_shift_ns


def main():
    import argparse

    ap = argparse.ArgumentParser(
        description="Polarity-flipped synthetic vs real with peak alignment")
    ap.add_argument("synth", type=Path, help="Synthetic .out file (420 MHz optimized)")
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

    print(f"\nSynthetic: {len(syn_sig)} samples, dt={dt_syn:.6f} ns")
    print(f"Real DZT:  {len(real_sig)} samples, dt={dt_real:.6f} ns")

    # Plot
    if args.output:
        out_png = args.output.with_suffix('.png')
    else:
        out_png = Path('output_test') / f"14_polarity_flip_peak_align.png"

    corr, time_shift_ns = plot_polarity_flip_alignment(syn_sig, syn_t, real_sig, real_t, dt_syn, out_png)

    print(f"\n{'='*70}")
    print("POLARITY-FLIP PEAK-ALIGNMENT ANALYSIS")
    print(f"{'='*70}")
    print(f"Configuration: 420 MHz Gaussian Bistatic 30mm")
    print(f"Polarity fix: Multiply synthetic by -1")
    print(f"Peak alignment: Shift real by {time_shift_ns:.3f} ns")
    print(f"Normalized correlation: {corr:.6f}")
    print(f"\nInterpretation:")
    if corr > 0.7:
        print(f"  [SUCCESS] High correlation - polarity flip + peak alignment works well!")
        print(f"  Synthetic and real waveforms are substantially aligned.")
    elif corr > 0.5:
        print(f"  [PARTIAL] Moderate correlation - reasonable but room for improvement")
    else:
        print(f"  [LOW] Low correlation - fundamental shape difference persists")
        print(f"  Issue is likely coda structure, not polarity or time-shift")
    print(f"{'='*70}")


if __name__ == "__main__":
    main()
