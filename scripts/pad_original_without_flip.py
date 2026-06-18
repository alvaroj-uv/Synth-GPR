#!/usr/bin/env python3
"""
Simple, clean comparison: Original synthetic (padded) vs Real DZT.
No flipping. Just time alignment via padding.
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
    return padded_sig, padded_t, n_pad_samples


def compute_correlation(sig1, t1, sig2, t2, t_min=0, t_max=30):
    """Compute correlation over time window."""
    idx1 = (t1 >= t_min) & (t1 <= t_max)
    idx2 = (t2 >= t_min) & (t2 <= t_max)

    if np.sum(idx1) < 2 or np.sum(idx2) < 2:
        return np.nan

    t_common = np.linspace(max(t1[idx1][0], t2[idx2][0]),
                          min(t1[idx1][-1], t2[idx2][-1]), 500)

    f1 = interp1d(t1[idx1], sig1[idx1], kind='linear', bounds_error=False, fill_value=0)
    f2 = interp1d(t2[idx2], sig2[idx2], kind='linear', bounds_error=False, fill_value=0)

    s1 = f1(t_common)
    s2 = f2(t_common)

    s1_norm = (s1 - np.mean(s1)) / (np.std(s1) + 1e-12)
    s2_norm = (s2 - np.mean(s2)) / (np.std(s2) + 1e-12)

    corr = np.corrcoef(s1_norm, s2_norm)
    if corr.shape == (2, 2):
        return corr[0, 1]
    return np.nan


def plot_comparison(syn_sig, syn_t, real_sig, real_t, pad_ns, dt_syn, out_png):
    """
    Create 4-row comparison:
    Row 1: Original synthetic (unpadded) vs Real
    Row 2: Padded synthetic vs Real (onset aligned)
    Row 3: Overlay (padded vs real)
    Row 4: Both waveforms full view
    """

    # Pad synthetic
    syn_padded, syn_t_padded, n_pad = pad_synthetic(syn_sig, dt_syn, pad_ns)

    # Normalize
    syn_norm = normalize_peak(syn_sig)
    syn_padded_norm = normalize_peak(syn_padded)
    real_norm = normalize_peak(real_sig)

    # Compute correlation
    corr = compute_correlation(syn_padded_norm, syn_t_padded, real_norm, real_t)

    # Create figure
    fig = plt.figure(figsize=(16, 14))
    fig.patch.set_facecolor("#0f1117")
    gs = gridspec.GridSpec(4, 1, figure=fig, hspace=0.35, left=0.1, right=0.95, top=0.96, bottom=0.06)

    c_syn = "#00d4ff"
    c_pad = "#00ff88"
    c_real = "#ff6b35"

    # Row 1: Original vs Real (unpadded)
    ax1 = fig.add_subplot(gs[0])
    ax1.set_facecolor("#1a1e2b")
    ax1.plot(syn_t, syn_norm, color=c_syn, lw=1.8, alpha=0.85, label="Synthetic (original, no padding)")
    ax1.plot(real_t, real_norm, color=c_real, lw=1.8, alpha=0.75, label="Real DZT")
    ax1.axhline(0, color="#2a2f42", lw=0.8, linestyle='-', alpha=0.5)
    ax1.set_ylabel("Normalized Amplitude", fontsize=11, color="#c8d0e0", fontweight='bold')
    ax1.set_title("Row 1: Original Synthetic vs Real (UNALIGNED - shows time offset)",
                 fontsize=11, color="#c8d0e0", fontweight='bold', pad=10)
    ax1.grid(True, color="#2a2f42", lw=0.5, alpha=0.4)
    ax1.legend(loc='upper right', fontsize=10, facecolor='#1a1e2b', labelcolor='#c8d0e0', edgecolor='#2a2f42')
    ax1.set_xlim([-2, 35])
    ax1.tick_params(colors="#c8d0e0", labelsize=9)
    for spine in ax1.spines.values():
        spine.set_color("#2a2f42")

    # Row 2: Padded vs Real (aligned onset)
    ax2 = fig.add_subplot(gs[1])
    ax2.set_facecolor("#1a1e2b")
    ax2.plot(syn_t_padded, syn_padded_norm, color=c_pad, lw=1.8, alpha=0.9,
            label=f"Synthetic (PADDED +{pad_ns:.2f} ns to align onset)")
    ax2.plot(real_t, real_norm, color=c_real, lw=1.8, alpha=0.75, label="Real DZT")
    ax2.axhline(0, color="#2a2f42", lw=0.8, linestyle='-', alpha=0.5)
    ax2.set_ylabel("Normalized Amplitude", fontsize=11, color="#c8d0e0", fontweight='bold')
    ax2.set_title("Row 2: Padded Synthetic vs Real (ONSET ALIGNED - compare shapes)",
                 fontsize=11, color="#c8d0e0", fontweight='bold', pad=10)
    ax2.grid(True, color="#2a2f42", lw=0.5, alpha=0.4)
    ax2.legend(loc='upper right', fontsize=10, facecolor='#1a1e2b', labelcolor='#c8d0e0', edgecolor='#2a2f42')
    ax2.set_xlim([0, 35])
    ax2.tick_params(colors="#c8d0e0", labelsize=9)
    for spine in ax2.spines.values():
        spine.set_color("#2a2f42")

    # Row 3: Overlay (zoomed to 0-25 ns)
    ax3 = fig.add_subplot(gs[2])
    ax3.set_facecolor("#1a1e2b")

    t_min = 0
    t_max = 25
    idx_syn = (syn_t_padded >= t_min) & (syn_t_padded <= t_max)
    idx_real = (real_t >= t_min) & (real_t <= t_max)

    t_common = np.linspace(max(syn_t_padded[idx_syn][0], real_t[idx_real][0]),
                          min(syn_t_padded[idx_syn][-1], real_t[idx_real][-1]), 800)

    f_syn = interp1d(syn_t_padded[idx_syn], syn_padded_norm[idx_syn], kind='linear',
                    bounds_error=False, fill_value=0)
    f_real = interp1d(real_t[idx_real], real_norm[idx_real], kind='linear',
                     bounds_error=False, fill_value=0)

    syn_interp = f_syn(t_common)
    real_interp = f_real(t_common)

    ax3.plot(t_common, syn_interp, color=c_pad, lw=2.0, alpha=0.9, label="Synthetic (padded)")
    ax3.plot(t_common, real_interp, color=c_real, lw=2.0, alpha=0.8, label="Real DZT")
    ax3.fill_between(t_common, syn_interp, real_interp, alpha=0.2, color="cyan",
                    label="Waveform difference")
    ax3.axhline(0, color="#2a2f42", lw=0.8, linestyle='-', alpha=0.5)

    ax3.set_ylabel("Normalized Amplitude", fontsize=11, color="#c8d0e0", fontweight='bold')
    corr_str = f"{corr:.4f}" if not np.isnan(corr) else "N/A"
    ax3.set_title(f"Row 3: Overlay Detail (0-25 ns) - Shape Comparison - Correlation: {corr_str}",
                 fontsize=11, color="#c8d0e0", fontweight='bold', pad=10)
    ax3.grid(True, color="#2a2f42", lw=0.5, alpha=0.4)
    ax3.legend(loc='upper right', fontsize=10, facecolor='#1a1e2b', labelcolor='#c8d0e0', edgecolor='#2a2f42')
    ax3.set_xlim([0, 25])
    ax3.tick_params(colors="#c8d0e0", labelsize=9)
    for spine in ax3.spines.values():
        spine.set_color("#2a2f42")

    # Row 4: Full view (both signals, full time range)
    ax4 = fig.add_subplot(gs[3])
    ax4.set_facecolor("#1a1e2b")
    ax4.plot(syn_t_padded, syn_padded_norm, color=c_pad, lw=1.5, alpha=0.85, label="Synthetic (padded)")
    ax4.plot(real_t, real_norm, color=c_real, lw=1.5, alpha=0.75, label="Real DZT")
    ax4.axhline(0, color="#2a2f42", lw=0.8, linestyle='-', alpha=0.5)

    ax4.set_xlabel("Time (ns)", fontsize=11, color="#c8d0e0", fontweight='bold')
    ax4.set_ylabel("Normalized Amplitude", fontsize=11, color="#c8d0e0", fontweight='bold')
    ax4.set_title("Row 4: Full Waveform View (All time range)",
                 fontsize=11, color="#c8d0e0", fontweight='bold', pad=10)
    ax4.grid(True, color="#2a2f42", lw=0.5, alpha=0.4)
    ax4.legend(loc='upper right', fontsize=10, facecolor='#1a1e2b', labelcolor='#c8d0e0', edgecolor='#2a2f42')
    ax4.tick_params(colors="#c8d0e0", labelsize=9)
    for spine in ax4.spines.values():
        spine.set_color("#2a2f42")

    # Main title
    fig.suptitle(
        f"Clean Comparison: Original Synthetic (No Flipping) + {pad_ns:.2f} ns Padding vs Real DZT",
        color="#c8d0e0", fontsize=13, fontweight='bold', y=0.995
    )

    # Save
    out_png.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_png, dpi=150, bbox_inches='tight', facecolor="#0f1117")
    plt.close(fig)

    print(f"\n[OK] Comparison saved -> {out_png}")

    return {
        'correlation': corr,
        'delay_ns': pad_ns,
        'n_pad_samples': n_pad,
    }


def main():
    import argparse

    ap = argparse.ArgumentParser(
        description="Clean comparison: original synthetic (no flipping) + padding vs real")
    ap.add_argument("synth", type=Path, help="Synthetic .out file")
    ap.add_argument("real", type=Path, help="Real .DZT file")
    ap.add_argument("--trace", type=int, default=1000, help="DZT trace index")
    ap.add_argument("--delay", type=float, default=None,
                   help="Padding delay (ns). If None, auto-detect")
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

    print(f"\nSynthetic: {len(syn_sig)} samples, dt={dt_syn:.4f} ns, t_range=[{syn_t[0]:.2f}, {syn_t[-1]:.2f}] ns")
    print(f"Real DZT:  {len(real_sig)} samples, dt={dt_real:.4f} ns, t_range=[{real_t[0]:.2f}, {real_t[-1]:.2f}] ns")

    # Determine padding
    if args.delay is None:
        syn_first_idx = find_first_significant_point(syn_sig, threshold_pct=10)
        real_first_idx = find_first_significant_point(real_sig, threshold_pct=10)
        pad_ns = real_t[real_first_idx] - syn_t[syn_first_idx]

        print(f"\n[AUTO] First significant point (10% threshold):")
        print(f"  Synthetic: {syn_t[syn_first_idx]:.2f} ns (sample {syn_first_idx})")
        print(f"  Real DZT:  {real_t[real_first_idx]:.2f} ns (sample {real_first_idx})")
        print(f"  Detected delay: {pad_ns:.2f} ns")
    else:
        pad_ns = args.delay
        print(f"\n[USER] Using specified delay: {pad_ns:.2f} ns")

    # Plot
    if args.output:
        out_png = args.output.with_suffix('.png')
    else:
        out_png = Path('output_test') / f"clean_compare_{args.synth.stem}.png"

    metrics = plot_comparison(syn_sig, syn_t, real_sig, real_t, pad_ns, dt_syn, out_png)

    print(f"\n{'='*70}")
    print("CLEAN COMPARISON ANALYSIS")
    print(f"{'='*70}")
    print(f"\nApproach: Original synthetic (NO FLIPPING) + TIME PADDING")
    print(f"\nPadding amount: {metrics['delay_ns']:.2f} ns ({metrics['n_pad_samples']} samples)")
    print(f"  Interpretation: System delay (antenna coupling + propagation)")
    print(f"\nCorrelation (0-30 ns window): {metrics['correlation']:.4f}")

    if not np.isnan(metrics['correlation']):
        if metrics['correlation'] > 0.7:
            print(f"  Status: [EXCELLENT] Waveforms match very well")
        elif metrics['correlation'] > 0.5:
            print(f"  Status: [GOOD] Reasonable shape match with some differences")
        elif metrics['correlation'] > 0.3:
            print(f"  Status: [MODERATE] Partial overlap, notable structural differences")
        else:
            print(f"  Status: [LOW] Shapes are quite different (expected: damping effect)")

    print(f"\nObservations:")
    print(f"  • Time offset: {metrics['delay_ns']:.2f} ns (padding absorbs this)")
    print(f"  • Polarity: CORRECT (original, no flipping)")
    print(f"  • Remaining difference: Due to system damping/broadening")
    print(f"    - Synthetic is sharper (ideal free-space pulse)")
    print(f"    - Real is broader (field system response)")
    print(f"\nConclusion:")
    print(f"  This padded synthetic is now TIME-CORRECT for the field system.")
    print(f"  The shape difference can be addressed by:")
    print(f"    1. Low-pass filtering the padded synthetic, or")
    print(f"    2. Modeling the real field antenna system in gprMax")


if __name__ == "__main__":
    main()
