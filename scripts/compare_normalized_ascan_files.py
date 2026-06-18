#!/usr/bin/env python3
"""
Compare normalized synthetic vs real A-scans.
Eliminates unit/calibration issues — focus on waveform shape equivalence.
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
        meta_str = f"{file_path.stem} (synthetic)"
        return signal, t_ns, dt * 1e9, meta_str

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
        meta_str = f"DZT Trace #{trace_idx} (real)"
        return signal, t_ns, DT_NS, meta_str

    else:
        raise ValueError(f"Unsupported file type: {suffix}")


def normalize_peak(signal):
    """Normalize by peak amplitude."""
    peak = np.max(np.abs(signal))
    if peak == 0:
        return signal
    return signal / peak


def normalize_rms(signal):
    """Normalize by RMS amplitude."""
    rms = np.sqrt(np.mean(signal**2))
    if rms == 0:
        return signal
    return signal / rms


def normalize_minmax(signal):
    """Normalize to [-1, 1] range."""
    minval = np.min(signal)
    maxval = np.max(signal)
    if maxval == minval:
        return signal
    return 2.0 * (signal - minval) / (maxval - minval) - 1.0


def hilbert_envelope(signal):
    """Compute Hilbert envelope (instantaneous amplitude)."""
    from scipy.signal import hilbert
    analytic = hilbert(signal)
    return np.abs(analytic)


def compute_spectrum(signal, dt_ns):
    """Compute frequency spectrum (dB)."""
    fs = 1.0 / (dt_ns * 1e-9)  # Sampling frequency in Hz
    freqs = np.fft.rfftfreq(len(signal), dt_ns * 1e-9)
    fft = np.fft.rfft(signal)
    power = np.abs(fft)
    power_db = 20 * np.log10(power + 1e-12)
    return freqs / 1e6, power_db  # Frequency in MHz


def plot_normalized_comparison(syn_sig, syn_t, real_sig, real_t, dt_syn_ns, dt_real_ns, out_png):
    """Create 4-row comparison: peak-norm, RMS-norm, envelope, spectrum."""

    # Normalize
    syn_peak = normalize_peak(syn_sig)
    real_peak = normalize_peak(real_sig)

    syn_rms = normalize_rms(syn_sig)
    real_rms = normalize_rms(real_sig)

    syn_env = hilbert_envelope(syn_sig)
    real_env = hilbert_envelope(real_sig)
    syn_env_norm = normalize_peak(syn_env)
    real_env_norm = normalize_peak(real_env)

    syn_freq, syn_power = compute_spectrum(syn_sig, dt_syn_ns)
    real_freq, real_power = compute_spectrum(real_sig, dt_real_ns)

    # Match time axes
    t_min = max(syn_t[0], real_t[0])
    t_max = min(syn_t[-1], real_t[-1])
    idx_syn = (syn_t >= t_min) & (syn_t <= t_max)
    idx_real = (real_t >= t_min) & (real_t <= t_max)

    t_common = syn_t[idx_syn]
    syn_matched = syn_peak[idx_syn]
    real_interp = interp1d(real_t[idx_real], real_peak[idx_real], kind='linear',
                          bounds_error=False, fill_value='extrapolate')
    real_matched = real_interp(t_common)

    # Create figure
    fig = plt.figure(figsize=(16, 14))
    fig.patch.set_facecolor("#0f1117")
    gs = gridspec.GridSpec(4, 1, figure=fig, hspace=0.35, left=0.1, right=0.95, top=0.96, bottom=0.06)

    # Color scheme
    c_syn = "#00d4ff"
    c_real = "#ff6b35"

    # Row 1: Peak-normalized waveforms
    ax1 = fig.add_subplot(gs[0])
    ax1.set_facecolor("#1a1e2b")
    ax1.plot(syn_t, syn_peak, color=c_syn, lw=1.5, alpha=0.8, label="Synthetic (peak-normalized)")
    ax1.plot(real_t, real_peak, color=c_real, lw=1.5, alpha=0.7, label="Real DZT (peak-normalized)")
    ax1.axhline(0, color="#2a2f42", lw=0.8, linestyle='-', alpha=0.5)
    ax1.set_ylabel("Normalized Amplitude", fontsize=10, color="#c8d0e0", fontweight='bold')
    ax1.set_title("Row 1: Peak-Normalized Waveforms", fontsize=11, color="#c8d0e0", fontweight='bold', pad=8)
    ax1.grid(True, color="#2a2f42", lw=0.5, alpha=0.4)
    ax1.legend(loc='upper right', fontsize=9, facecolor='#1a1e2b', labelcolor='#c8d0e0', edgecolor='#2a2f42')
    ax1.tick_params(colors="#c8d0e0", labelsize=9)
    for spine in ax1.spines.values():
        spine.set_color("#2a2f42")

    # Row 2: RMS-normalized waveforms
    ax2 = fig.add_subplot(gs[1])
    ax2.set_facecolor("#1a1e2b")
    ax2.plot(syn_t, syn_rms, color=c_syn, lw=1.5, alpha=0.8, label="Synthetic (RMS-normalized)")
    ax2.plot(real_t, real_rms, color=c_real, lw=1.5, alpha=0.7, label="Real DZT (RMS-normalized)")
    ax2.axhline(0, color="#2a2f42", lw=0.8, linestyle='-', alpha=0.5)
    ax2.set_ylabel("Normalized Amplitude", fontsize=10, color="#c8d0e0", fontweight='bold')
    ax2.set_title("Row 2: RMS-Normalized Waveforms", fontsize=11, color="#c8d0e0", fontweight='bold', pad=8)
    ax2.grid(True, color="#2a2f42", lw=0.5, alpha=0.4)
    ax2.legend(loc='upper right', fontsize=9, facecolor='#1a1e2b', labelcolor='#c8d0e0', edgecolor='#2a2f42')
    ax2.tick_params(colors="#c8d0e0", labelsize=9)
    for spine in ax2.spines.values():
        spine.set_color("#2a2f42")

    # Row 3: Hilbert envelope (normalized)
    ax3 = fig.add_subplot(gs[2])
    ax3.set_facecolor("#1a1e2b")
    ax3.plot(syn_t, syn_env_norm, color=c_syn, lw=1.5, alpha=0.8, label="Synthetic envelope")
    ax3.plot(real_t, real_env_norm, color=c_real, lw=1.5, alpha=0.7, label="Real DZT envelope")
    ax3.axhline(0, color="#2a2f42", lw=0.8, linestyle='-', alpha=0.5)
    ax3.set_ylabel("Normalized Envelope", fontsize=10, color="#c8d0e0", fontweight='bold')
    ax3.set_title("Row 3: Hilbert Envelope Comparison", fontsize=11, color="#c8d0e0", fontweight='bold', pad=8)
    ax3.grid(True, color="#2a2f42", lw=0.5, alpha=0.4)
    ax3.legend(loc='upper right', fontsize=9, facecolor='#1a1e2b', labelcolor='#c8d0e0', edgecolor='#2a2f42')
    ax3.tick_params(colors="#c8d0e0", labelsize=9)
    for spine in ax3.spines.values():
        spine.set_color("#2a2f42")

    # Row 4: Frequency spectrum (dB, log scale)
    ax4 = fig.add_subplot(gs[3])
    ax4.set_facecolor("#1a1e2b")
    ax4.semilogy(syn_freq, np.maximum(syn_power, 1e-10), color=c_syn, lw=1.5, alpha=0.8, label="Synthetic spectrum")
    ax4.semilogy(real_freq, np.maximum(real_power, 1e-10), color=c_real, lw=1.5, alpha=0.7, label="Real DZT spectrum")
    ax4.set_xlabel("Frequency (MHz)", fontsize=10, color="#c8d0e0", fontweight='bold')
    ax4.set_ylabel("Power (dB)", fontsize=10, color="#c8d0e0", fontweight='bold')
    ax4.set_title("Row 4: Frequency Spectrum (log scale)", fontsize=11, color="#c8d0e0", fontweight='bold', pad=8)
    ax4.grid(True, which='both', color="#2a2f42", lw=0.5, alpha=0.4)
    ax4.legend(loc='upper right', fontsize=9, facecolor='#1a1e2b', labelcolor='#c8d0e0', edgecolor='#2a2f42')
    ax4.tick_params(colors="#c8d0e0", labelsize=9)
    for spine in ax4.spines.values():
        spine.set_color("#2a2f42")

    # Main title
    fig.suptitle(
        "Normalized Waveform Comparison: Synthetic (V/m) vs Real DZT (A/D counts)",
        color="#c8d0e0", fontsize=13, fontweight='bold', y=0.995
    )

    # Save
    out_png.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_png, dpi=150, bbox_inches='tight', facecolor="#0f1117")
    plt.close(fig)

    print(f"\n[OK] Normalized comparison saved -> {out_png}")


def main():
    import argparse

    ap = argparse.ArgumentParser(
        description="Compare normalized synthetic and real A-scans (eliminates unit calibration)")
    ap.add_argument("synth", type=Path, help="Synthetic .out file")
    ap.add_argument("real", type=Path, help="Real .DZT file")
    ap.add_argument("--trace", type=int, default=1000, help="DZT trace index (default: 1000)")
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
    syn_sig, syn_t, dt_syn, meta_syn = read_file(args.synth)

    print(f"[READ] Real DZT (trace #{args.trace}): {args.real.name}")
    real_sig, real_t, dt_real, meta_real = read_file(args.real, trace_idx=args.trace)

    print(f"\nSynthetic: {len(syn_sig)} samples, dt={dt_syn:.4f} ns, t_max={syn_t[-1]:.2f} ns")
    print(f"Real DZT:  {len(real_sig)} samples, dt={dt_real:.4f} ns, t_max={real_t[-1]:.2f} ns")
    print(f"Synthetic peak: {np.max(np.abs(syn_sig)):.4e}")
    print(f"Real DZT peak:  {np.max(np.abs(real_sig)):.4e}")

    # Plot
    if args.output:
        out_png = args.output.with_suffix('.png')
    else:
        out_png = Path('output_test') / f"normalized_compare_{args.synth.stem}_vs_{args.real.stem}.png"

    plot_normalized_comparison(syn_sig, syn_t, real_sig, real_t, dt_syn, dt_real, out_png)

    print(f"\n{'='*70}")
    print("NORMALIZED COMPARISON SUMMARY")
    print(f"{'='*70}")
    print(f"Synthetic: {meta_syn}")
    print(f"Real DZT:  {meta_real}")
    print(f"\nNormalization methods applied:")
    print(f"  • Peak normalization: divide by max(|signal|)")
    print(f"  • RMS normalization: divide by sqrt(mean(signal^2))")
    print(f"  • Envelope: Hilbert transform instantaneous amplitude")
    print(f"  • Spectrum: FFT power spectrum (dB scale)")
    print(f"\nKey question: Do the waveforms match after normalization?")
    print(f"  [YES] synthetic and real measure same physics (unit issue only)")
    print(f"  [NO] fundamental difference in signal structure (physics issue)")


if __name__ == "__main__":
    main()
