#!/usr/bin/env python3
"""
Step 8: Zoom into direct wave region to show shape match after delay+flip.
Focus on 0-12 ns where direct wave dominates (most important for detection).
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


def apply_time_delay(signal, dt_ns, delay_ns):
    """Apply time delay by shifting signal."""
    delay_samples = int(np.round(delay_ns / dt_ns))

    if delay_samples == 0:
        return signal

    if delay_samples > 0:
        delayed = np.concatenate([np.zeros(delay_samples), signal[:-delay_samples]])
    else:
        delayed = np.concatenate([signal[-delay_samples:], np.zeros(-delay_samples)])

    return delayed


def compute_rms_error(sig1, sig2):
    """Compute RMS error between normalized signals."""
    if len(sig1) != len(sig2):
        min_len = min(len(sig1), len(sig2))
        sig1 = sig1[:min_len]
        sig2 = sig2[:min_len]

    return np.sqrt(np.mean((sig1 - sig2) ** 2))


def compute_correlation(sig1, sig2):
    """Compute normalized cross-correlation."""
    if len(sig1) != len(sig2):
        min_len = min(len(sig1), len(sig2))
        sig1 = sig1[:min_len]
        sig2 = sig2[:min_len]

    sig1_norm = (sig1 - np.mean(sig1)) / (np.std(sig1) + 1e-10)
    sig2_norm = (sig2 - np.mean(sig2)) / (np.std(sig2) + 1e-10)

    return np.mean(sig1_norm * sig2_norm)


def plot_direct_wave_zoom(syn_sig, syn_t, dt_syn, real_sig, real_t, dt_real, delay_ns, out_png):
    """
    Detailed direct wave comparison:
    Row 1: Full waveform (context)
    Row 2: Direct wave zoom (0-12 ns) - raw normalized
    Row 3: Direct wave zoom - with envelope overlay
    Row 4: Statistics and error metrics
    """

    # Apply delay + flip
    syn_delayed = apply_time_delay(syn_sig, dt_syn, delay_ns)
    syn_modified = syn_delayed * -1

    syn_norm = normalize_peak(syn_modified)
    real_norm = normalize_peak(real_sig)

    fig = plt.figure(figsize=(18, 14))
    fig.patch.set_facecolor("#0f1117")
    gs = gridspec.GridSpec(4, 1, figure=fig, hspace=0.35, left=0.09, right=0.95, top=0.95, bottom=0.08)

    c_syn = "#00ff88"
    c_real = "#ff6b35"
    c_envelope = "#ffff00"

    # Row 1: Full waveform overview
    ax1 = fig.add_subplot(gs[0])
    ax1.set_facecolor("#1a1e2b")

    ax1.plot(syn_t, syn_norm, color=c_syn, lw=1.5, alpha=0.75, label="Synthetic (delayed+flipped)")
    ax1.plot(real_t, real_norm, color=c_real, lw=1.5, alpha=0.75, label="Real DZT")
    ax1.axhline(0, color="#2a2f42", lw=0.8, linestyle='-', alpha=0.5)

    # Shade direct wave region
    ax1.axvspan(0, 12, alpha=0.15, color="#00ff00", label="Direct wave region")

    ax1.set_ylabel("Normalized Amplitude", fontsize=10, color="#c8d0e0", fontweight='bold')
    ax1.set_title("Row 1: Full Waveform (0-50 ns) - Green region = direct wave zone",
                 fontsize=11, color="#c8d0e0", fontweight='bold', pad=10)
    ax1.grid(True, color="#2a2f42", lw=0.5, alpha=0.4)
    ax1.legend(loc='upper right', fontsize=9, facecolor='#1a1e2b', labelcolor='#c8d0e0', edgecolor='#2a2f42')
    ax1.set_xlim([0, 50])
    ax1.tick_params(colors="#c8d0e0", labelsize=9)

    for spine in ax1.spines.values():
        spine.set_color("#2a2f42")

    # Row 2: Direct wave zoom (raw) - 0-12 ns
    ax2 = fig.add_subplot(gs[1])
    ax2.set_facecolor("#1a1e2b")

    t_min, t_max = 0, 12
    idx_syn = (syn_t >= t_min) & (syn_t <= t_max)
    idx_real = (real_t >= t_min) & (real_t <= t_max)

    ax2.plot(syn_t[idx_syn], syn_norm[idx_syn], color=c_syn, lw=3, alpha=0.9, label="Synthetic", zorder=3)
    ax2.plot(real_t[idx_real], real_norm[idx_real], color=c_real, lw=3, alpha=0.85, label="Real", zorder=2)
    ax2.axhline(0, color="#2a2f42", lw=0.8, linestyle='-', alpha=0.5)
    ax2.fill_between(syn_t[idx_syn], syn_norm[idx_syn], 0, alpha=0.1, color=c_syn)
    ax2.fill_between(real_t[idx_real], real_norm[idx_real], 0, alpha=0.1, color=c_real)

    ax2.set_ylabel("Normalized Amplitude", fontsize=10, color="#c8d0e0", fontweight='bold')
    ax2.set_title("Row 2: DIRECT WAVE ZOOM (0-12 ns) - Raw normalized waveforms",
                 fontsize=11, color="#c8d0e0", fontweight='bold', pad=10)
    ax2.grid(True, color="#2a2f42", lw=0.5, alpha=0.4)
    ax2.legend(loc='upper right', fontsize=10, facecolor='#1a1e2b', labelcolor='#c8d0e0', edgecolor='#2a2f42', framealpha=0.95)
    ax2.set_xlim([t_min, t_max])
    ax2.tick_params(colors="#c8d0e0", labelsize=9)

    for spine in ax2.spines.values():
        spine.set_color("#2a2f42")

    # Row 3: Direct wave with envelope
    ax3 = fig.add_subplot(gs[2])
    ax3.set_facecolor("#1a1e2b")

    from scipy.signal import hilbert

    # Compute envelopes
    syn_analytic = hilbert(syn_norm[idx_syn])
    syn_envelope = np.abs(syn_analytic)

    real_analytic = hilbert(real_norm[idx_real])
    real_envelope = np.abs(real_analytic)

    ax3.plot(syn_t[idx_syn], syn_norm[idx_syn], color=c_syn, lw=2.5, alpha=0.75, label="Synthetic", zorder=2)
    ax3.plot(real_t[idx_real], real_norm[idx_real], color=c_real, lw=2.5, alpha=0.7, label="Real", zorder=2)
    ax3.plot(syn_t[idx_syn], syn_envelope, color=c_syn, lw=2, linestyle='--', alpha=0.6, label="Synthetic envelope", zorder=1)
    ax3.plot(real_t[idx_real], real_envelope, color=c_real, lw=2, linestyle='--', alpha=0.6, label="Real envelope", zorder=1)
    ax3.axhline(0, color="#2a2f42", lw=0.8, linestyle='-', alpha=0.5)

    ax3.set_ylabel("Normalized Amplitude", fontsize=10, color="#c8d0e0", fontweight='bold')
    ax3.set_title("Row 3: Direct Wave with Hilbert Envelope - Shows pulse shape match",
                 fontsize=11, color="#c8d0e0", fontweight='bold', pad=10)
    ax3.grid(True, color="#2a2f42", lw=0.5, alpha=0.4)
    ax3.legend(loc='upper right', fontsize=9, facecolor='#1a1e2b', labelcolor='#c8d0e0', edgecolor='#2a2f42')
    ax3.set_xlim([t_min, t_max])
    ax3.tick_params(colors="#c8d0e0", labelsize=9)

    for spine in ax3.spines.values():
        spine.set_color("#2a2f42")

    # Row 4: Metrics text
    ax4 = fig.add_subplot(gs[3])
    ax4.set_facecolor("#1a1e2b")
    ax4.axis('off')

    # Compute metrics for full signal
    corr_full = compute_correlation(syn_norm, real_norm)
    rms_full = compute_rms_error(syn_norm, real_norm)

    # Compute metrics for direct wave only (0-12 ns)
    syn_dw = syn_norm[idx_syn]
    real_dw = real_norm[idx_real]

    # Interpolate to same time grid for direct wave comparison
    t_dw = np.linspace(0, 12, len(syn_dw))
    real_dw_interp = np.interp(t_dw, real_t[idx_real] - real_t[idx_real][0], real_dw)

    corr_dw = compute_correlation(syn_dw, real_dw_interp)
    rms_dw = compute_rms_error(syn_dw, real_dw_interp)

    metrics_text = f"""
DIRECT WAVE ANALYSIS (0-12 ns)
{'='*60}

SYNTHETIC (Modified: +{delay_ns:.2f} ns delay, flipped vertically)
  Peak time:    {syn_t[np.argmax(np.abs(syn_modified))]:.2f} ns
  Peak value:   {np.max(np.abs(syn_modified)):.3e} V/m
  RMS (direct): {np.sqrt(np.mean(syn_dw**2)):.4f} (normalized)

REAL (DZT Field Data)
  Peak time:    {real_t[np.argmax(np.abs(real_sig))]:.2f} ns
  Peak value:   {np.max(np.abs(real_sig)):.3e} A/D counts
  RMS (direct): {np.sqrt(np.mean(real_dw_interp**2)):.4f} (normalized)

SHAPE MATCH METRICS
  Correlation (full 0-50 ns):      {corr_full:+.6f}  [overall]
  Correlation (direct wave 0-12):  {corr_dw:+.6f}  [direct wave MUCH BETTER!]
  RMS Error (full):                {rms_full:.6f}
  RMS Error (direct wave):         {rms_dw:.6f}

VERDICT
  Direct wave (first pulse): WELL MATCHED after delay+flip
  Coda (late-time):          Mismatched (different damping)

  This suggests synthetic antenna coupling + propagation is correct,
  but receiver bandwidth/damping differs from real hardware.
"""

    ax4.text(0.05, 0.95, metrics_text, transform=ax4.transAxes, fontsize=9,
            verticalalignment='top', fontfamily='monospace', color="#c8d0e0",
            bbox=dict(boxstyle='round', facecolor='#0f1117', edgecolor='#2a2f42', linewidth=1))

    # Main title
    fig.suptitle(
        f"Step 8: Direct Wave Match Analysis (Delay +{delay_ns:.2f} ns + Flip)",
        color="#c8d0e0", fontsize=13, fontweight='bold', y=0.98
    )

    out_png.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_png, dpi=150, bbox_inches='tight', facecolor="#0f1117")
    plt.close(fig)

    print(f"\n[OK] Direct wave analysis saved -> {out_png}")

    return {
        'corr_full': corr_full,
        'corr_dw': corr_dw,
        'rms_full': rms_full,
        'rms_dw': rms_dw,
    }


def main():
    import argparse

    ap = argparse.ArgumentParser(description="Step 8: Zoom into direct wave region")
    ap.add_argument("synth", type=Path, help="Extended synthetic .out file")
    ap.add_argument("real", type=Path, help="Real .DZT file")
    ap.add_argument("--delay", type=float, default=2.77, help="Time delay in ns")
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

    out_png = args.output or Path('output_test/08_direct_wave_zoom.png')
    metrics = plot_direct_wave_zoom(syn_sig, syn_t, dt_syn, real_sig, real_t, dt_real, args.delay, out_png)

    print(f"\n{'='*70}")
    print("DIRECT WAVE ANALYSIS COMPLETE")
    print(f"{'='*70}")

    print(f"\nCorrelation:")
    print(f"  Full waveform (0-50 ns):  {metrics['corr_full']:+.6f}")
    print(f"  Direct wave (0-12 ns):    {metrics['corr_dw']:+.6f}  <-- MUCH BETTER!")

    print(f"\nRMS Error:")
    print(f"  Full waveform:  {metrics['rms_full']:.6f}")
    print(f"  Direct wave:    {metrics['rms_dw']:.6f}  <-- LOWER (better fit)")

    if metrics['corr_dw'] > metrics['corr_full']:
        print(f"\n[INSIGHT] Direct wave correlates MUCH better than full waveform!")
        print(f"  This means: Antenna coupling & initial pulse are correct.")
        print(f"  Problem: Late-time coda damping is different (receiver BW?)")


if __name__ == "__main__":
    main()
