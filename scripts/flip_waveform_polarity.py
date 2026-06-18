#!/usr/bin/env python3
"""
Compare Gaussian waveform with and without polarity flip.
Overlay original vs flipped to find best match.
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


def read_real_dzt(file_path: Path, trace_idx: int = 1000) -> tuple:
    HEADER_SIZE = 128 * 1024
    SAMPLES_PER_TRACE = 512
    BYTES_PER_SAMPLE = 4
    DT_NS = 50 / 511

    with open(file_path, 'rb') as f:
        f.seek(HEADER_SIZE + trace_idx * SAMPLES_PER_TRACE * BYTES_PER_SAMPLE)
        trace_bytes = f.read(SAMPLES_PER_TRACE * BYTES_PER_SAMPLE)
        signal = np.frombuffer(trace_bytes, dtype=np.int32, count=SAMPLES_PER_TRACE)
        signal = signal.astype(np.float64)

    signal = signal[2:]
    t_ns = np.arange(len(signal)) * DT_NS
    return signal, t_ns, DT_NS


def normalize_peak(signal):
    peak = np.max(np.abs(signal))
    return signal / peak if peak != 0 else signal


def apply_time_delay(signal, dt_ns, delay_ns):
    delay_samples = int(np.round(delay_ns / dt_ns))
    if delay_samples <= 0:
        return signal
    return np.concatenate([np.zeros(delay_samples), signal[:-delay_samples]])


def compute_correlation(sig1, sig2):
    if len(sig1) != len(sig2):
        min_len = min(len(sig1), len(sig2))
        sig1 = sig1[:min_len]
        sig2 = sig2[:min_len]

    s1 = (sig1 - np.mean(sig1)) / (np.std(sig1) + 1e-10)
    s2 = (sig2 - np.mean(sig2)) / (np.std(sig2) + 1e-10)
    return np.mean(s1 * s2)


def extract_direct_wave(signal, t_ns, delay_ns=2.77, t_max=12.0):
    dt_ns = t_ns[1] - t_ns[0] if len(t_ns) > 1 else 0.01
    signal_delayed = apply_time_delay(signal, dt_ns, delay_ns)
    signal_flipped = signal_delayed * -1
    signal_norm = normalize_peak(signal_flipped)

    idx = (t_ns >= 0) & (t_ns <= t_max)
    if np.sum(idx) < 10:
        return None, None, False

    return signal_norm[idx], t_ns[idx], True


# Load real DZT
print("[READ] Real DZT...")
real_dzt = Path("D:/Codigo/Data/PUERTO-LIMACHE_20230726_EFE_V1_PKC000_588_PKF011_020_CENTRO_BRUTO.DZT")
real_sig, real_t, _ = read_real_dzt(real_dzt, trace_idx=1000)
real_dw, real_dw_t, _ = extract_direct_wave(real_sig, real_t, delay_ns=2.77)
real_dw_norm = normalize_peak(real_dw)

# Load Gaussian synthetic
print("[READ] Gaussian synthetic...")
out_file = Path("output_test/waveform_opt/waveform_gaussian.out")
data = read_ascan(out_file, component="Ez")
syn_sig = data['signal']
dt_syn = data['dt']
t_syn = np.arange(len(syn_sig)) * dt_syn * 1e9

syn_dw, syn_dw_t, _ = extract_direct_wave(syn_sig, t_syn, delay_ns=2.77)
syn_dw_norm = normalize_peak(syn_dw)

# Create polarity-flipped version
syn_dw_flipped = syn_dw_norm * -1

# Compute correlations
corr_original = compute_correlation(syn_dw_norm, real_dw_norm)
corr_flipped = compute_correlation(syn_dw_flipped, real_dw_norm)

print(f"[CORR] Original: {corr_original:+.6f}")
print(f"[CORR] Flipped:  {corr_flipped:+.6f}")
print(f"[DELTA] Difference: {corr_flipped - corr_original:+.6f}\n")

# Create comparison figure
fig = plt.figure(figsize=(18, 12))
fig.patch.set_facecolor("#0f1117")
gs = gridspec.GridSpec(3, 2, figure=fig, hspace=0.35, wspace=0.3)

c_syn = "#00ff88"
c_real = "#ff6b35"

# Row 1: Original overlay
ax1 = fig.add_subplot(gs[0, :])
ax1.set_facecolor("#1a1e2b")

t_min, t_max = 0, 12
idx_syn = (syn_dw_t >= t_min) & (syn_dw_t <= t_max)
idx_real = (real_dw_t >= t_min) & (real_dw_t <= t_max)

ax1.plot(syn_dw_t[idx_syn], syn_dw_norm[idx_syn], color=c_syn, lw=3, alpha=0.85,
        label="Gaussian Synthetic (original)")
ax1.plot(real_dw_t[idx_real], real_dw_norm[idx_real], color=c_real, lw=3, alpha=0.8,
        label="Real DZT")
ax1.axhline(0, color="#2a2f42", lw=0.8, linestyle='-', alpha=0.5)
ax1.fill_between(syn_dw_t[idx_syn], syn_dw_norm[idx_syn], 0, alpha=0.1, color=c_syn)
ax1.fill_between(real_dw_t[idx_real], real_dw_norm[idx_real], 0, alpha=0.1, color=c_real)

ax1.set_ylabel("Normalized Amplitude", fontsize=11, color="#c8d0e0", fontweight='bold')
ax1.set_title(f"ORIGINAL POLARITY - Correlation: {corr_original:+.6f}",
             fontsize=12, color="#c8d0e0", fontweight='bold')
ax1.grid(True, color="#2a2f42", lw=0.5, alpha=0.4)
ax1.legend(fontsize=11, facecolor='#1a1e2b', labelcolor='#c8d0e0', edgecolor='#2a2f42', loc='upper right')
ax1.tick_params(colors="#c8d0e0", labelsize=9)
ax1.set_xlim([t_min, t_max])

for spine in ax1.spines.values():
    spine.set_color("#2a2f42")

# Row 2: Flipped overlay
ax2 = fig.add_subplot(gs[1, :])
ax2.set_facecolor("#1a1e2b")

ax2.plot(syn_dw_t[idx_syn], syn_dw_flipped[idx_syn], color="#ff00ff", lw=3, alpha=0.85,
        label="Gaussian Synthetic (polarity flipped)")
ax2.plot(real_dw_t[idx_real], real_dw_norm[idx_real], color=c_real, lw=3, alpha=0.8,
        label="Real DZT")
ax2.axhline(0, color="#2a2f42", lw=0.8, linestyle='-', alpha=0.5)
ax2.fill_between(syn_dw_t[idx_syn], syn_dw_flipped[idx_syn], 0, alpha=0.1, color="#ff00ff")
ax2.fill_between(real_dw_t[idx_real], real_dw_norm[idx_real], 0, alpha=0.1, color=c_real)

title_color = "#ffff00" if corr_flipped > corr_original else "#c8d0e0"
title_weight = "bold" if corr_flipped > corr_original else "normal"
best_marker = " [BETTER!]" if corr_flipped > corr_original else ""

ax2.set_ylabel("Normalized Amplitude", fontsize=11, color="#c8d0e0", fontweight='bold')
ax2.set_title(f"FLIPPED POLARITY - Correlation: {corr_flipped:+.6f}{best_marker}",
             fontsize=12, color=title_color, fontweight=title_weight)
ax2.grid(True, color="#2a2f42", lw=0.5, alpha=0.4)
ax2.legend(fontsize=11, facecolor='#1a1e2b', labelcolor='#c8d0e0', edgecolor='#2a2f42', loc='upper right')
ax2.tick_params(colors="#c8d0e0", labelsize=9)
ax2.set_xlim([t_min, t_max])

for spine in ax2.spines.values():
    spine.set_color("#2a2f42")

# Row 3: Comparison bars
ax3 = fig.add_subplot(gs[2, :])
ax3.set_facecolor("#1a1e2b")

configs = ["Original\nPolarity", "Flipped\nPolarity"]
correlations = [corr_original, corr_flipped]
colors = [c_syn, "#ff00ff"]

bars = ax3.bar(configs, correlations, color=colors, edgecolor="#c8d0e0",
              linewidth=2.5, alpha=0.85, width=0.5)

ax3.axhline(0, color="#2a2f42", lw=1.5, linestyle='-', alpha=0.6)
ax3.grid(True, axis='y', color="#2a2f42", lw=0.5, alpha=0.4)

ax3.set_ylabel("Direct Wave Correlation", fontsize=11, color="#c8d0e0", fontweight='bold')
ax3.set_title("Polarity Comparison",
             fontsize=12, color="#c8d0e0", fontweight='bold')
ax3.tick_params(colors="#c8d0e0", labelsize=10)

# Add value labels
for bar, corr in zip(bars, correlations):
    height = bar.get_height()
    ax3.text(bar.get_x() + bar.get_width()/2., height,
            f'{corr:+.6f}', ha='center', va='bottom' if height > 0 else 'top',
            fontsize=12, color="#c8d0e0", fontweight='bold',
            bbox=dict(boxstyle='round,pad=0.6', facecolor='#0f1117',
            edgecolor='#c8d0e0', alpha=0.9))

# Highlight best
best_idx = np.argmax(correlations)
bars[best_idx].set_edgecolor("#ffff00")
bars[best_idx].set_linewidth(3.5)

for spine in ax3.spines.values():
    spine.set_color("#2a2f42")

fig.suptitle(
    "Polarity Analysis: Original vs Flipped (Gaussian, 420 MHz, Bistatic 30mm)",
    color="#c8d0e0", fontsize=14, fontweight='bold', y=0.98
)

out_png = Path("output_test/13c_polarity_comparison.png")
fig.savefig(out_png, dpi=150, bbox_inches='tight', facecolor="#0f1117")
plt.close(fig)

print(f"{'='*70}")
print("POLARITY ANALYSIS RESULTS")
print(f"{'='*70}\n")

print(f"Original polarity:  {corr_original:+.6f}")
print(f"Flipped polarity:   {corr_flipped:+.6f}")

if corr_flipped > corr_original:
    print(f"\n[RESULT] FLIPPED POLARITY IS BETTER!")
    print(f"         Improvement: {corr_flipped - corr_original:+.6f}")
else:
    print(f"\n[RESULT] Original polarity is better")
    print(f"         Flipped is worse by: {corr_original - corr_flipped:.6f}")

print(f"\n[SAVE] Polarity comparison -> {out_png}")
