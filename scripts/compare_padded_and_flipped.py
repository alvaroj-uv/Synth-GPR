#!/usr/bin/env python3
"""
Compare: Padded synthetic (original) vs Padded+Flipped synthetic vs Real DZT.
Now that time is aligned, test if flipping reveals polarity/phase match.
"""

import sys
from pathlib import Path
import struct
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


def find_first_significant_point(signal, threshold_pct=10):
    """Find index where signal first exceeds threshold of max amplitude."""
    max_amp = np.max(np.abs(signal))
    threshold = max_amp * (threshold_pct / 100.0)
    above_threshold = np.where(np.abs(signal) > threshold)[0]
    if len(above_threshold) > 0:
        return above_threshold[0]
    return 0


def normalize_peak(signal):
    """Normalize by peak amplitude."""
    peak = np.max(np.abs(signal))
    if peak == 0:
        return signal
    return signal / peak


def pad_synthetic(syn_sig, dt_syn_ns, pad_ns):
    """Pad synthetic with zeros at the beginning."""
    n_pad_samples = int(np.round(pad_ns / dt_syn_ns))
    pad_array = np.zeros(n_pad_samples)
    padded_sig = np.concatenate([pad_array, syn_sig])
    t_min = -n_pad_samples * dt_syn_ns
    padded_t = np.arange(len(padded_sig)) * dt_syn_ns + t_min
    return padded_sig, padded_t


def plot_comparison(syn_sig, syn_t, real_sig, real_t, pad_ns, dt_syn, out_png):
    """
    Create 3-row comparison:
    Row 1: Padded synthetic (not flipped) vs Real
    Row 2: Padded synthetic (FLIPPED) vs Real
    Row 3: Overlay flipped vs real
    """

    # Pad synthetic
    syn_padded, syn_t_padded = pad_synthetic(syn_sig, dt_syn, pad_ns)

    # Normalize
    syn_padded_norm = normalize_peak(syn_padded)
    real_norm = normalize_peak(real_sig)

    # Flip padded synthetic (mirror signal)
    syn_padded_flipped = syn_padded_norm[::-1]
    syn_t_flipped = syn_t_padded[::-1]
    # Adjust time axis after flip so it stays positive
    syn_t_flipped = syn_t_flipped - syn_t_flipped[0]

    # Create figure
    fig = plt.figure(figsize=(16, 13))
    fig.patch.set_facecolor("#0f1117")
    gs = gridspec.GridSpec(3, 1, figure=fig, hspace=0.35, left=0.1, right=0.95, top=0.96, bottom=0.06)

    c_pad = "#00ff88"
    c_flip = "#ffaa00"
    c_real = "#ff6b35"

    # Row 1: Padded (not flipped) vs Real
    ax1 = fig.add_subplot(gs[0])
    ax1.set_facecolor("#1a1e2b")
    ax1.plot(syn_t_padded, syn_padded_norm, color=c_pad, lw=1.5, alpha=0.85, label="Synthetic (padded, NOT flipped)")
    ax1.plot(real_t, real_norm, color=c_real, lw=1.5, alpha=0.7, label="Real DZT")
    ax1.axhline(0, color="#2a2f42", lw=0.8, linestyle='-', alpha=0.5)
    ax1.set_ylabel("Normalized Amplitude", fontsize=10, color="#c8d0e0", fontweight='bold')
    ax1.set_title("Row 1: Padded Synthetic (Original) vs Real",
                 fontsize=11, color="#c8d0e0", fontweight='bold', pad=8)
    ax1.grid(True, color="#2a2f42", lw=0.5, alpha=0.4)
    ax1.legend(loc='upper right', fontsize=9, facecolor='#1a1e2b', labelcolor='#c8d0e0', edgecolor='#2a2f42')
    ax1.set_xlim([0, 30])
    ax1.tick_params(colors="#c8d0e0", labelsize=9)
    for spine in ax1.spines.values():
        spine.set_color("#2a2f42")

    # Row 2: Padded+Flipped vs Real
    ax2 = fig.add_subplot(gs[1])
    ax2.set_facecolor("#1a1e2b")
    ax2.plot(syn_t_flipped, syn_padded_flipped, color=c_flip, lw=1.5, alpha=0.85, label="Synthetic (padded + FLIPPED)")
    ax2.plot(real_t, real_norm, color=c_real, lw=1.5, alpha=0.7, label="Real DZT")
    ax2.axhline(0, color="#2a2f42", lw=0.8, linestyle='-', alpha=0.5)
    ax2.set_ylabel("Normalized Amplitude", fontsize=10, color="#c8d0e0", fontweight='bold')
    ax2.set_title("Row 2: Padded Synthetic FLIPPED (Time-Reversed) vs Real",
                 fontsize=11, color="#c8d0e0", fontweight='bold', pad=8)
    ax2.grid(True, color="#2a2f42", lw=0.5, alpha=0.4)
    ax2.legend(loc='upper right', fontsize=9, facecolor='#1a1e2b', labelcolor='#c8d0e0', edgecolor='#2a2f42')
    ax2.set_xlim([0, 30])
    ax2.tick_params(colors="#c8d0e0", labelsize=9)
    for spine in ax2.spines.values():
        spine.set_color("#2a2f42")

    # Row 3: Overlay flipped vs real on common time grid
    ax3 = fig.add_subplot(gs[2])
    ax3.set_facecolor("#1a1e2b")

    # Find common time range
    t_min = max(0, real_t[0])  # Flipped time starts at 0
    t_max = min(np.max(syn_t_flipped), np.max(real_t))
    t_common = np.linspace(t_min, t_max, 800)

    # Interpolate to common grid
    f_flip = interp1d(syn_t_flipped, syn_padded_flipped, kind='linear', bounds_error=False, fill_value=0)
    f_real = interp1d(real_t, real_norm, kind='linear', bounds_error=False, fill_value=0)

    flip_interp = f_flip(t_common)
    real_interp = f_real(t_common)

    ax3.plot(t_common, flip_interp, color=c_flip, lw=1.5, alpha=0.85, label="Synthetic (flipped)")
    ax3.plot(t_common, real_interp, color=c_real, lw=1.5, alpha=0.7, label="Real DZT")
    ax3.fill_between(t_common, flip_interp, real_interp, alpha=0.2, color="yellow",
                    label="Waveform difference")
    ax3.axhline(0, color="#2a2f42", lw=0.8, linestyle='-', alpha=0.5)

    # Compute correlation to quantify match
    # Normalize both to [-1, 1]
    flip_norm_01 = (flip_interp - np.min(flip_interp)) / (np.max(flip_interp) - np.min(flip_interp) + 1e-12)
    real_norm_01 = (real_interp - np.min(real_interp)) / (np.max(real_interp) - np.min(real_interp) + 1e-12)
    correlation = np.corrcoef(flip_norm_01, real_norm_01)[0, 1]

    ax3.set_xlabel("Time (ns)", fontsize=10, color="#c8d0e0", fontweight='bold')
    ax3.set_ylabel("Normalized Amplitude", fontsize=10, color="#c8d0e0", fontweight='bold')
    ax3.set_title(f"Row 3: Overlay Flipped vs Real (Correlation: {correlation:.3f})",
                 fontsize=11, color="#c8d0e0", fontweight='bold', pad=8)
    ax3.grid(True, color="#2a2f42", lw=0.5, alpha=0.4)
    ax3.legend(loc='upper right', fontsize=9, facecolor='#1a1e2b', labelcolor='#c8d0e0', edgecolor='#2a2f42')
    ax3.set_xlim([0, 30])
    ax3.tick_params(colors="#c8d0e0", labelsize=9)
    for spine in ax3.spines.values():
        spine.set_color("#2a2f42")

    # Main title
    fig.suptitle(
        f"Padded Synthetic: Original vs Flipped vs Real (Delay: +{pad_ns:.2f} ns)",
        color="#c8d0e0", fontsize=13, fontweight='bold', y=0.995
    )

    # Save
    out_png.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_png, dpi=150, bbox_inches='tight', facecolor="#0f1117")
    plt.close(fig)

    print(f"\n[OK] Padded+flipped comparison saved -> {out_png}")
    print(f"\nCorrelation (flipped vs real): {correlation:.4f}")

    return correlation


def main():
    import argparse

    ap = argparse.ArgumentParser(
        description="Compare padded synthetic (original and flipped) vs real DZT")
    ap.add_argument("synth", type=Path, help="Synthetic .out file")
    ap.add_argument("real", type=Path, help="Real .DZT file")
    ap.add_argument("--trace", type=int, default=1000, help="DZT trace index")
    ap.add_argument("--delay", type=float, default=None,
                   help="Padding delay (ns). If None, auto-detect from first significant point")
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

    print(f"\nSynthetic: {len(syn_sig)} samples, dt={dt_syn:.4f} ns")
    print(f"Real DZT:  {len(real_sig)} samples, dt={dt_real:.4f} ns")

    # Determine padding
    if args.delay is None:
        syn_first_idx = find_first_significant_point(syn_sig, threshold_pct=10)
        real_first_idx = find_first_significant_point(real_sig, threshold_pct=10)
        pad_ns = real_t[real_first_idx] - syn_t[syn_first_idx]
        print(f"\n[AUTO] Detected delay: {pad_ns:.2f} ns")
    else:
        pad_ns = args.delay
        print(f"\n[USER] Using specified delay: {pad_ns:.2f} ns")

    # Plot
    if args.output:
        out_png = args.output.with_suffix('.png')
    else:
        out_png = Path('output_test') / f"pad_flip_{args.synth.stem}.png"

    corr = plot_comparison(syn_sig, syn_t, real_sig, real_t, pad_ns, dt_syn, out_png)

    print(f"\n{'='*70}")
    print("ANALYSIS: PADDED + FLIPPED SYNTHETIC VS REAL")
    print(f"{'='*70}")
    print(f"Padding: {pad_ns:.2f} ns (absorbs system delay)")
    print(f"Flipping: Time-reversal of padded signal")
    print(f"\nCorrelation (flipped vs real): {corr:.4f}")
    print(f"\nInterpretation:")
    if corr > 0.7:
        print(f"  [GOOD] High correlation - flipped shape matches real reasonably well")
        print(f"  Suggests: Synthetic and real have similar structure after time-alignment")
    elif corr > 0.5:
        print(f"  [MEDIUM] Moderate correlation - partial shape match")
        print(f"  Suggests: Some structural similarity but also differences")
    else:
        print(f"  [LOW] Low correlation - flipped shape does NOT match real")
        print(f"  Suggests: Fundamental difference in waveform structure (damping, etc.)")
    print(f"\nNext step: Extract waveform features from both signals for training")


if __name__ == "__main__":
    main()
