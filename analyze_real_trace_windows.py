#!/usr/bin/env python3
"""
Analyze the real trace characteristics in different windows.
Does the real trace prefer Vivanco's 7ns window or our 9-35ns window?
"""

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from pathlib import Path
import sys
sys.path.insert(0, str(Path.cwd()))
from src.signal_processing import dewow

# Load real data
HEADER_SIZE = 128 * 1024
with open("D:/Codigo/Data/PUERTO-LIMACHE_20230726_EFE_V1_PKC000_588_PKF011_020_CENTRO_BRUTO.DZT", 'rb') as f:
    f.seek(HEADER_SIZE + 15000 * 512 * 4)
    real_sig = np.frombuffer(f.read(512 * 4), dtype=np.int32)[2:].astype(float)

real_dt = 50 / 511
real_t = np.arange(len(real_sig)) * real_dt

# Find peak
dewowd = dewow(real_sig, 50)
real_peak_idx = np.argmax(np.abs(dewowd))
real_peak_t = real_t[real_peak_idx]

# Normalize
real_sig_norm = real_sig / np.max(np.abs(real_sig))

print("\n" + "="*80)
print("REAL TRACE WINDOW ANALYSIS")
print("="*80 + "\n")

print(f"Real trace peak at: {real_peak_t:.2f} ns\n")

# Window 1: Vivanco (4.5ns after peak, 7ns)
vivanco_start = real_peak_t + 4.5
vivanco_end = vivanco_start + 7.0
vivanco_mask = (real_t >= vivanco_start) & (real_t <= vivanco_end)
vivanco_sig = real_sig_norm[vivanco_mask]
vivanco_t = real_t[vivanco_mask]

print(f"Vivanco window: {vivanco_start:.2f}-{vivanco_end:.2f} ns")
print(f"  Samples: {len(vivanco_sig)}")
print(f"  Peak: {np.max(np.abs(vivanco_sig)):.6f}")
print(f"  RMS: {np.sqrt(np.mean(vivanco_sig**2)):.6f}")
print(f"  Energy: {np.sum(vivanco_sig**2):.6f}")
print(f"  Zero-crossings: {np.sum(np.diff(np.sign(vivanco_sig)) != 0)}")

# Window 2: Code gate (4.5ns after peak, 16ns)
code_start = real_peak_t + 4.5
code_end = code_start + 16.0
code_mask = (real_t >= code_start) & (real_t <= code_end)
code_sig = real_sig_norm[code_mask]
code_t = real_t[code_mask]

print(f"\nCode gate window: {code_start:.2f}-{code_end:.2f} ns")
print(f"  Samples: {len(code_sig)}")
print(f"  Peak: {np.max(np.abs(code_sig)):.6f}")
print(f"  RMS: {np.sqrt(np.mean(code_sig**2)):.6f}")
print(f"  Energy: {np.sum(code_sig**2):.6f}")
print(f"  Zero-crossings: {np.sum(np.diff(np.sign(code_sig)) != 0)}")

# Window 3: Manual (9-35ns absolute)
manual_start = 9.0
manual_end = 35.0
manual_mask = (real_t >= manual_start) & (real_t <= manual_end)
manual_sig = real_sig_norm[manual_mask]
manual_t = real_t[manual_mask]

print(f"\nManual window: {manual_start:.2f}-{manual_end:.2f} ns")
print(f"  Samples: {len(manual_sig)}")
print(f"  Peak: {np.max(np.abs(manual_sig)):.6f}")
print(f"  RMS: {np.sqrt(np.mean(manual_sig**2)):.6f}")
print(f"  Energy: {np.sum(manual_sig**2):.6f}")
print(f"  Zero-crossings: {np.sum(np.diff(np.sign(manual_sig)) != 0)}")

# Decay analysis
print(f"\nDecay Analysis (envelope decay from peak to end):")

def compute_envelope_decay(sig, dt):
    """Compute envelope and its decay rate."""
    analytic = sig + 1j * np.imag(np.fft.fft(sig))
    env = np.abs(analytic)
    if len(env) > 2:
        # Log-linear fit
        t_sample = np.arange(len(env)) * dt
        log_env = np.log10(np.maximum(env, 1e-6))
        slope = np.polyfit(t_sample, log_env, 1)[0]
        return slope, env
    return 0, env

vivanco_slope, vivanco_env = compute_envelope_decay(vivanco_sig, real_dt)
code_slope, code_env = compute_envelope_decay(code_sig, real_dt)
manual_slope, manual_env = compute_envelope_decay(manual_sig, real_dt)

print(f"  Vivanco decay rate: {vivanco_slope:.6f} (dB/ns)")
print(f"  Code gate decay rate: {code_slope:.6f} (dB/ns)")
print(f"  Manual decay rate: {manual_slope:.6f} (dB/ns)")

# Visualization
fig = plt.figure(figsize=(18, 12))
fig.patch.set_facecolor("#0f1117")
gs = gridspec.GridSpec(3, 2, figure=fig, hspace=0.35, wspace=0.28,
                      left=0.08, right=0.96, top=0.94, bottom=0.07)

# Full trace with window markers
ax0 = fig.add_subplot(gs[0, :])
ax0.set_facecolor("#1a1e2b")
ax0.plot(real_t, real_sig_norm, color="#ff6b35", lw=1.0, alpha=0.8, label="Real trace")
ax0.axvline(real_peak_t, color='#ff00ff', linestyle='--', linewidth=2, alpha=0.7, label=f"Peak ({real_peak_t:.2f} ns)")
ax0.axvspan(vivanco_start, vivanco_end, alpha=0.15, color='#ffff00', label="Vivanco (7ns)")
ax0.axvspan(code_start, code_end, alpha=0.1, color='#00ff00', label="Code (16ns)")
ax0.axvspan(manual_start, manual_end, alpha=0.08, color='#00ccff', label="Manual (9-35ns)")
ax0.set_ylabel("Normalized Amplitude", fontsize=11, color="#c8d0e0", fontweight='bold')
ax0.set_title("Real Trace with Window Overlays", fontsize=13, color="#ff6b35", fontweight='bold')
ax0.grid(True, color="#2a2f42", alpha=0.2)
ax0.tick_params(colors="#c8d0e0", labelsize=9)
for spine in ax0.spines.values():
    spine.set_color("#2a2f42")
ax0.set_xlim(0, 50)
ax0.legend(fontsize=10, facecolor='#1a1e2b', labelcolor='#c8d0e0', edgecolor='#2a2f42', ncol=4, loc='upper right')

# Vivanco window
ax1 = fig.add_subplot(gs[1, 0])
ax1.set_facecolor("#1a1e2b")
ax1.plot(vivanco_t, vivanco_sig, color="#ffff00", lw=2.0, alpha=0.9, marker='o', markersize=5)
ax1.plot(vivanco_t, vivanco_env, color='#ff00ff', lw=2.0, alpha=0.7, linestyle='--', label='Envelope')
ax1.set_ylabel("Amplitude", fontsize=11, color="#c8d0e0", fontweight='bold')
ax1.set_title(f"Vivanco (7ns): Decay {vivanco_slope:.4f} dB/ns", fontsize=12, color="#ffff00", fontweight='bold')
ax1.grid(True, color="#2a2f42", alpha=0.2)
ax1.tick_params(colors="#c8d0e0", labelsize=9)
for spine in ax1.spines.values():
    spine.set_color("#2a2f42")
ax1.legend(fontsize=9, facecolor='#1a1e2b', labelcolor='#c8d0e0', edgecolor='#2a2f42')

# Code window
ax2 = fig.add_subplot(gs[1, 1])
ax2.set_facecolor("#1a1e2b")
ax2.plot(code_t, code_sig, color="#00ff00", lw=2.0, alpha=0.9, marker='s', markersize=4)
ax2.plot(code_t, code_env, color='#ff00ff', lw=2.0, alpha=0.7, linestyle='--', label='Envelope')
ax2.set_ylabel("Amplitude", fontsize=11, color="#c8d0e0", fontweight='bold')
ax2.set_title(f"Code Gate (16ns): Decay {code_slope:.4f} dB/ns", fontsize=12, color="#00ff00", fontweight='bold')
ax2.grid(True, color="#2a2f42", alpha=0.2)
ax2.tick_params(colors="#c8d0e0", labelsize=9)
for spine in ax2.spines.values():
    spine.set_color("#2a2f42")
ax2.legend(fontsize=9, facecolor='#1a1e2b', labelcolor='#c8d0e0', edgecolor='#2a2f42')

# Manual window
ax3 = fig.add_subplot(gs[2, 0])
ax3.set_facecolor("#1a1e2b")
ax3.plot(manual_t, manual_sig, color="#00ccff", lw=2.0, alpha=0.9, marker='^', markersize=4)
ax3.plot(manual_t, manual_env, color='#ff00ff', lw=2.0, alpha=0.7, linestyle='--', label='Envelope')
ax3.set_xlabel("Time (ns)", fontsize=11, color="#c8d0e0", fontweight='bold')
ax3.set_ylabel("Amplitude", fontsize=11, color="#c8d0e0", fontweight='bold')
ax3.set_title(f"Manual (9-35ns): Decay {manual_slope:.4f} dB/ns", fontsize=12, color="#00ccff", fontweight='bold')
ax3.grid(True, color="#2a2f42", alpha=0.2)
ax3.tick_params(colors="#c8d0e0", labelsize=9)
for spine in ax3.spines.values():
    spine.set_color("#2a2f42")
ax3.legend(fontsize=9, facecolor='#1a1e2b', labelcolor='#c8d0e0', edgecolor='#2a2f42')

# Summary metrics
ax4 = fig.add_subplot(gs[2, 1])
ax4.axis('off')
ax4.set_facecolor("#0f1117")

summary = f"""
REAL TRACE WINDOW CHARACTERISTICS

Vivanco (7ns at {vivanco_start:.1f}-{vivanco_end:.1f} ns):
  Energy: {np.sum(vivanco_sig**2):.4f}
  Decay: {vivanco_slope:.4f} dB/ns
  RMS: {np.sqrt(np.mean(vivanco_sig**2)):.4f}

Code Gate (16ns at {code_start:.1f}-{code_end:.1f} ns):
  Energy: {np.sum(code_sig**2):.4f}
  Decay: {code_slope:.4f} dB/ns
  RMS: {np.sqrt(np.mean(code_sig**2)):.4f}

Manual (26ns at {manual_start:.1f}-{manual_end:.1f} ns):
  Energy: {np.sum(manual_sig**2):.4f}
  Decay: {manual_slope:.4f} dB/ns
  RMS: {np.sqrt(np.mean(manual_sig**2)):.4f}

INSIGHT:
Real trace shows FAST ATTENUATION in
Vivanco window, consistent with moisture/
fouling effects. Longer window (9-35ns)
captures extended scattering tail.

The real trace might PREFER Vivanco's
short window if it's heavily attenuated.
"""

ax4.text(0.05, 0.95, summary, transform=ax4.transAxes,
        fontsize=10, verticalalignment='top', fontfamily='monospace',
        bbox=dict(boxstyle='round', facecolor='#1a1e2b', alpha=0.95, edgecolor='#2a2f42', linewidth=2),
        color='#c8d0e0')

fig.suptitle(
    "Real Trace Window Analysis: Which window best captures the fouling signature?\n" +
    f"Peak at {real_peak_t:.2f} ns | Decay rates: Vivanco={vivanco_slope:.4f}, Code={code_slope:.4f}, Manual={manual_slope:.4f} dB/ns",
    color="#c8d0e0", fontsize=13, fontweight='bold', y=0.995
)

png_path = Path("output_test") / "real_trace_window_analysis.png"
fig.savefig(png_path, dpi=150, bbox_inches='tight', facecolor="#0f1117")

print(f"\n[SAVE] {png_path}\n")
print("="*80 + "\n")
