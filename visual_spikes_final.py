#!/usr/bin/env python3
"""
Visual: Homogeneous vs Layered (spike-generating) model vs real data.
Focus on coda window to show spike structure.
"""

import numpy as np
import h5py
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from scipy.interpolate import interp1d
from pathlib import Path

# Load signals
with h5py.File("start_fresh_reduced.out", 'r') as f:
    homo_sig = -f['rxs/rx1/Ez'][()]
    homo_dt = f.attrs.get('dt', 0.0) * 1e9

with h5py.File("start_fresh_fouled_layered.out", 'r') as f:
    layered_sig = -f['rxs/rx1/Ez'][()]
    layered_dt = f.attrs.get('dt', 0.0) * 1e9

HEADER_SIZE = 128 * 1024
with open("D:/Codigo/Data/PUERTO-LIMACHE_20230726_EFE_V1_PKC000_588_PKF011_020_CENTRO_BRUTO.DZT", 'rb') as f:
    f.seek(HEADER_SIZE + 15000 * 512 * 4)
    real_sig = np.frombuffer(f.read(512 * 4), dtype=np.int32)[2:].astype(float)

real_dt = 50 / 511

homo_t = np.arange(len(homo_sig)) * homo_dt
layered_t = np.arange(len(layered_sig)) * layered_dt
real_t = np.arange(len(real_sig)) * real_dt

print("\n" + "="*80)
print("SPIKE STRUCTURE COMPARISON")
print("="*80 + "\n")

# Time shift
shift_ns = 4.0
homo_t_shifted = homo_t + shift_ns
layered_t_shifted = layered_t + shift_ns

common_dt = real_dt
t_max = min(homo_t_shifted[-1], real_t[-1])
t_common = np.arange(0, t_max + common_dt, common_dt)

f_homo = interp1d(homo_t_shifted, homo_sig, kind='cubic', bounds_error=False, fill_value=0)
f_layered = interp1d(layered_t_shifted, layered_sig, kind='cubic', bounds_error=False, fill_value=0)
f_real = interp1d(real_t, real_sig, kind='cubic', bounds_error=False, fill_value=0)

homo_interp = f_homo(t_common)
layered_interp = f_layered(t_common)
real_interp = f_real(t_common)

homo_norm = homo_interp / np.max(np.abs(homo_interp))
layered_norm = layered_interp / np.max(np.abs(layered_interp))
real_norm = real_interp / np.max(np.abs(real_interp))

# Correlations for coda
mask_coda = t_common >= 9.0
corr_homo_coda = np.corrcoef(homo_norm[mask_coda], real_norm[mask_coda])[0, 1]
corr_layered_coda = np.corrcoef(layered_norm[mask_coda], real_norm[mask_coda])[0, 1]

# Create visualization
fig = plt.figure(figsize=(18, 10))
fig.patch.set_facecolor("#0f1117")
gs = gridspec.GridSpec(2, 3, figure=fig, hspace=0.32, wspace=0.3,
                      left=0.07, right=0.96, top=0.93, bottom=0.10)

# ===== FULL TRACES =====
ax1 = fig.add_subplot(gs[0, 0])
ax1.set_facecolor("#1a1e2b")
ax1.plot(homo_t_shifted, homo_sig, color="#00ff00", lw=0.7, alpha=0.8)
ax1.axvline(9, color='#ffff00', linestyle='--', alpha=0.5, linewidth=1.5)
ax1.set_ylabel("Amplitude (V/m)", fontsize=10, color="#c8d0e0", fontweight='bold')
ax1.set_title("Homogeneous (eps=5.1)", fontsize=11, color="#00ff00", fontweight='bold')
ax1.grid(True, color="#2a2f42", alpha=0.2)
ax1.tick_params(colors="#c8d0e0", labelsize=9)
for spine in ax1.spines.values():
    spine.set_color("#2a2f42")
ax1.set_xlim(0, 50)

ax2 = fig.add_subplot(gs[0, 1])
ax2.set_facecolor("#1a1e2b")
ax2.plot(real_t, real_sig, color="#ff6b35", lw=0.7, alpha=0.8)
ax2.axvline(9, color='#ffff00', linestyle='--', alpha=0.5, linewidth=1.5)
ax2.set_ylabel("Amplitude (A/D counts)", fontsize=10, color="#c8d0e0", fontweight='bold')
ax2.set_title("Real Data (Puerto-Limache #15000)", fontsize=11, color="#ff6b35", fontweight='bold')
ax2.grid(True, color="#2a2f42", alpha=0.2)
ax2.tick_params(colors="#c8d0e0", labelsize=9)
for spine in ax2.spines.values():
    spine.set_color("#2a2f42")
ax2.set_xlim(0, 50)

ax3 = fig.add_subplot(gs[0, 2])
ax3.set_facecolor("#1a1e2b")
ax3.plot(layered_t_shifted, layered_sig, color="#ff00ff", lw=0.7, alpha=0.8)
ax3.axvline(9, color='#ffff00', linestyle='--', alpha=0.5, linewidth=1.5)
ax3.set_ylabel("Amplitude (V/m)", fontsize=10, color="#c8d0e0", fontweight='bold')
ax3.set_title("Layered (5.1 + 8.5)", fontsize=11, color="#ff00ff", fontweight='bold')
ax3.grid(True, color="#2a2f42", alpha=0.2)
ax3.tick_params(colors="#c8d0e0", labelsize=9)
for spine in ax3.spines.values():
    spine.set_color("#2a2f42")
ax3.set_xlim(0, 50)

# ===== CODA ZOOMED (9-35 ns) =====
coda_start, coda_end = 9, 35

ax4 = fig.add_subplot(gs[1, 0])
ax4.set_facecolor("#1a1e2b")
mask_coda_homo = (homo_t_shifted >= coda_start) & (homo_t_shifted <= coda_end)
ax4.plot(homo_t_shifted[mask_coda_homo], homo_sig[mask_coda_homo], color="#00ff00", lw=1.5, alpha=0.9)
ax4.set_xlabel("Time (ns)", fontsize=10, color="#c8d0e0", fontweight='bold')
ax4.set_ylabel("Amplitude", fontsize=10, color="#c8d0e0", fontweight='bold')
ax4.set_title("Coda: Homogeneous", fontsize=11, color="#00ff00", fontweight='bold')
ax4.grid(True, color="#2a2f42", alpha=0.2)
ax4.tick_params(colors="#c8d0e0", labelsize=9)
for spine in ax4.spines.values():
    spine.set_color("#2a2f42")

ax5 = fig.add_subplot(gs[1, 1])
ax5.set_facecolor("#1a1e2b")
mask_coda_real = (real_t >= coda_start) & (real_t <= coda_end)
ax5.plot(real_t[mask_coda_real], real_sig[mask_coda_real], color="#ff6b35", lw=1.5, alpha=0.9)
ax5.set_xlabel("Time (ns)", fontsize=10, color="#c8d0e0", fontweight='bold')
ax5.set_ylabel("Amplitude", fontsize=10, color="#c8d0e0", fontweight='bold')
ax5.set_title("Coda: Real Data", fontsize=11, color="#ff6b35", fontweight='bold')
ax5.grid(True, color="#2a2f42", alpha=0.2)
ax5.tick_params(colors="#c8d0e0", labelsize=9)
for spine in ax5.spines.values():
    spine.set_color("#2a2f42")

ax6 = fig.add_subplot(gs[1, 2])
ax6.set_facecolor("#1a1e2b")
mask_coda_layered = (layered_t_shifted >= coda_start) & (layered_t_shifted <= coda_end)
ax6.plot(layered_t_shifted[mask_coda_layered], layered_sig[mask_coda_layered], color="#ff00ff", lw=1.5, alpha=0.9)
ax6.set_xlabel("Time (ns)", fontsize=10, color="#c8d0e0", fontweight='bold')
ax6.set_ylabel("Amplitude", fontsize=10, color="#c8d0e0", fontweight='bold')
ax6.set_title("Coda: Layered (spikes)", fontsize=11, color="#ff00ff", fontweight='bold')
ax6.grid(True, color="#2a2f42", alpha=0.2)
ax6.tick_params(colors="#c8d0e0", labelsize=9)
for spine in ax6.spines.values():
    spine.set_color("#2a2f42")

# Main title
fig.suptitle(
    "Coda Spike Generation: Homogeneous vs Layered Model\n" +
    f"Coda (9-35ns) Correlations: Homo={corr_homo_coda:+.4f}  Layered={corr_layered_coda:+.4f}",
    color="#c8d0e0", fontsize=13, fontweight='bold', y=0.98
)

png_path = Path("output_test") / "visual_coda_spikes_comparison.png"
fig.savefig(png_path, dpi=150, bbox_inches='tight', facecolor="#0f1117")

print(f"[SAVE] {png_path}\n")
print(f"Homogeneous model coda correlation: {corr_homo_coda:+.6f}")
print(f"Layered model coda correlation: {corr_layered_coda:+.6f}")
print(f"Improvement: {corr_layered_coda - corr_homo_coda:+.6f}\n")
print(f"Layered model adds structural detail via layer interface")
print(f"This simulates the effect of fouled layer creating scattering\n")
print("="*80 + "\n")
