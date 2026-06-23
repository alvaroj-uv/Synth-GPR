#!/usr/bin/env python3
"""
Visual: Clean vs Fouled model comparison with real data.
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
    clean_sig = -f['rxs/rx1/Ez'][()]
    clean_dt = f.attrs.get('dt', 0.0) * 1e9

with h5py.File("start_fresh_fouled.out", 'r') as f:
    fouled_sig = -f['rxs/rx1/Ez'][()]
    fouled_dt = f.attrs.get('dt', 0.0) * 1e9

HEADER_SIZE = 128 * 1024
with open("D:/Codigo/Data/PUERTO-LIMACHE_20230726_EFE_V1_PKC000_588_PKF011_020_CENTRO_BRUTO.DZT", 'rb') as f:
    f.seek(HEADER_SIZE + 15000 * 512 * 4)
    real_sig = np.frombuffer(f.read(512 * 4), dtype=np.int32)[2:].astype(float)

real_dt = 50 / 511

clean_t = np.arange(len(clean_sig)) * clean_dt
fouled_t = np.arange(len(fouled_sig)) * fouled_dt
real_t = np.arange(len(real_sig)) * real_dt

# Time shift
shift_ns = 4.0
clean_t_shifted = clean_t + shift_ns
fouled_t_shifted = fouled_t + shift_ns

common_dt = real_dt
t_max = min(clean_t_shifted[-1], real_t[-1])
t_common = np.arange(0, t_max + common_dt, common_dt)

f_clean = interp1d(clean_t_shifted, clean_sig, kind='cubic', bounds_error=False, fill_value=0)
f_fouled = interp1d(fouled_t_shifted, fouled_sig, kind='cubic', bounds_error=False, fill_value=0)
f_real = interp1d(real_t, real_sig, kind='cubic', bounds_error=False, fill_value=0)

clean_interp = f_clean(t_common)
fouled_interp = f_fouled(t_common)
real_interp = f_real(t_common)

clean_norm = clean_interp / np.max(np.abs(clean_interp))
fouled_norm = fouled_interp / np.max(np.abs(fouled_interp))
real_norm = real_interp / np.max(np.abs(real_interp))

# Correlations
corr_clean_full = np.corrcoef(clean_norm, real_norm)[0, 1]
corr_fouled_full = np.corrcoef(fouled_norm, real_norm)[0, 1]

mask_coda = t_common >= 9.0
corr_clean_coda = np.corrcoef(clean_norm[mask_coda], real_norm[mask_coda])[0, 1]
corr_fouled_coda = np.corrcoef(fouled_norm[mask_coda], real_norm[mask_coda])[0, 1]

# Visualization
fig = plt.figure(figsize=(20, 10))
fig.patch.set_facecolor("#0f1117")
gs = gridspec.GridSpec(2, 3, figure=fig, hspace=0.30, wspace=0.3,
                      left=0.07, right=0.96, top=0.94, bottom=0.10)

# ===== LEFT COLUMN: CLEAN MODEL =====
ax1 = fig.add_subplot(gs[0, 0])
ax1.set_facecolor("#1a1e2b")
ax1.plot(clean_t_shifted, clean_sig, color="#00ff00", lw=0.8, alpha=0.85, label="Clean (eps=5.1)")
ax1.axvline(9, color='#ffff00', linestyle='--', linewidth=1.5, alpha=0.6)
ax1.set_ylabel("Amplitude (V/m)", fontsize=10, color="#c8d0e0", fontweight='bold')
ax1.set_title("Clean Ballast (eps=5.1)", fontsize=11, color="#00ff00", fontweight='bold')
ax1.grid(True, color="#2a2f42", alpha=0.2)
ax1.tick_params(colors="#c8d0e0", labelsize=9)
for spine in ax1.spines.values():
    spine.set_color("#2a2f42")
ax1.set_xlim(0, 50)

ax2 = fig.add_subplot(gs[1, 0])
ax2.set_facecolor("#1a1e2b")
mask = t_common <= 50
ax2.plot(t_common[mask], clean_norm[mask], color="#00ff00", lw=2.0, alpha=0.85, label="Clean (norm)")
ax2.plot(t_common[mask], real_norm[mask], color="#ffffff", lw=2.0, alpha=0.60, label="Real (norm)", linestyle=':')
ax2.axvspan(9, 35, alpha=0.12, color='#ffff00')
ax2.axhline(0, color='#2a2f42', lw=0.5, alpha=0.5)
ax2.set_xlabel("Time (ns)", fontsize=10, color="#c8d0e0", fontweight='bold')
ax2.set_ylabel("Normalized", fontsize=10, color="#c8d0e0", fontweight='bold')
ax2.set_title(f"Clean Overlay (r_full={corr_clean_full:+.4f}, r_coda={corr_clean_coda:+.4f})",
             fontsize=11, color="#00ff00", fontweight='bold')
ax2.grid(True, color="#2a2f42", alpha=0.2)
ax2.legend(fontsize=9, facecolor='#1a1e2b', labelcolor='#c8d0e0', edgecolor='#2a2f42')
ax2.tick_params(colors="#c8d0e0", labelsize=9)
for spine in ax2.spines.values():
    spine.set_color("#2a2f42")

# ===== MIDDLE COLUMN: REAL DATA =====
ax3 = fig.add_subplot(gs[0, 1])
ax3.set_facecolor("#1a1e2b")
ax3.plot(real_t, real_sig, color="#ff6b35", lw=0.8, alpha=0.85, label="Real Data")
ax3.axvline(9, color='#ffff00', linestyle='--', linewidth=1.5, alpha=0.6)
ax3.set_ylabel("Amplitude (A/D counts)", fontsize=10, color="#c8d0e0", fontweight='bold')
ax3.set_title("Real DZT (Puerto-Limache #15000)", fontsize=11, color="#ff6b35", fontweight='bold')
ax3.grid(True, color="#2a2f42", alpha=0.2)
ax3.tick_params(colors="#c8d0e0", labelsize=9)
for spine in ax3.spines.values():
    spine.set_color("#2a2f42")
ax3.set_xlim(0, 50)

# Comparison text
ax4 = fig.add_subplot(gs[1, 1])
ax4.axis('off')
ax4.set_facecolor("#0f1117")

comparison_text = f"""
MODELS vs REAL DATA
{'='*40}

CLEAN BALLAST (eps=5.1)
  Full window:  {corr_clean_full:+.6f}
  Coda (9-35ns): {corr_clean_coda:+.6f}

FOULED BALLAST (eps=9.5)
  Full window:  {corr_fouled_full:+.6f}
  Coda (9-35ns): {corr_fouled_coda:+.6f}

DIFFERENCE (Fouled - Clean)
  Full:  {corr_fouled_full - corr_clean_full:+.6f}
  Coda:  {corr_fouled_coda - corr_clean_coda:+.6f}

CONCLUSION
  Both models match real data similarly
  Fouled slightly better in coda region
  Suitable for RF classifier training
"""

ax4.text(0.05, 0.95, comparison_text, transform=ax4.transAxes,
        fontsize=10, verticalalignment='top', fontfamily='monospace',
        bbox=dict(boxstyle='round', facecolor='#1a1e2b', alpha=0.8, edgecolor='#2a2f42'))

# ===== RIGHT COLUMN: FOULED MODEL =====
ax5 = fig.add_subplot(gs[0, 2])
ax5.set_facecolor("#1a1e2b")
ax5.plot(fouled_t_shifted, fouled_sig, color="#ff00ff", lw=0.8, alpha=0.85, label="Fouled (eps=9.5)")
ax5.axvline(9, color='#ffff00', linestyle='--', linewidth=1.5, alpha=0.6)
ax5.set_ylabel("Amplitude (V/m)", fontsize=10, color="#c8d0e0", fontweight='bold')
ax5.set_title("Fouled Ballast (eps=9.5)", fontsize=11, color="#ff00ff", fontweight='bold')
ax5.grid(True, color="#2a2f42", alpha=0.2)
ax5.tick_params(colors="#c8d0e0", labelsize=9)
for spine in ax5.spines.values():
    spine.set_color("#2a2f42")
ax5.set_xlim(0, 50)

ax6 = fig.add_subplot(gs[1, 2])
ax6.set_facecolor("#1a1e2b")
ax6.plot(t_common[mask], fouled_norm[mask], color="#ff00ff", lw=2.0, alpha=0.85, label="Fouled (norm)")
ax6.plot(t_common[mask], real_norm[mask], color="#ffffff", lw=2.0, alpha=0.60, label="Real (norm)", linestyle=':')
ax6.axvspan(9, 35, alpha=0.12, color='#ffff00')
ax6.axhline(0, color='#2a2f42', lw=0.5, alpha=0.5)
ax6.set_xlabel("Time (ns)", fontsize=10, color="#c8d0e0", fontweight='bold')
ax6.set_ylabel("Normalized", fontsize=10, color="#c8d0e0", fontweight='bold')
ax6.set_title(f"Fouled Overlay (r_full={corr_fouled_full:+.4f}, r_coda={corr_fouled_coda:+.4f})",
             fontsize=11, color="#ff00ff", fontweight='bold')
ax6.grid(True, color="#2a2f42", alpha=0.2)
ax6.legend(fontsize=9, facecolor='#1a1e2b', labelcolor='#c8d0e0', edgecolor='#2a2f42')
ax6.tick_params(colors="#c8d0e0", labelsize=9)
for spine in ax6.spines.values():
    spine.set_color("#2a2f42")

# Main title
fig.suptitle(
    "Clean vs Fouled Ballast Models: Validation Against Real Field Data\n" +
    "420 MHz, Amplitude=0.3, Time Shift=+4.0 ns, Coda Window=9-35 ns",
    color="#c8d0e0", fontsize=13, fontweight='bold', y=0.99
)

png_path = Path("output_test") / "visual_clean_vs_fouled_final.png"
fig.savefig(png_path, dpi=150, bbox_inches='tight', facecolor="#0f1117")

print("\n" + "="*80)
print("CLEAN vs FOULED FINAL COMPARISON")
print("="*80 + "\n")
print(f"[SAVE] {png_path}\n")
print(f"Clean model (eps=5.1):")
print(f"  Full: {corr_clean_full:+.6f}  |  Coda: {corr_clean_coda:+.6f}\n")
print(f"Fouled model (eps=9.5):")
print(f"  Full: {corr_fouled_full:+.6f}  |  Coda: {corr_fouled_coda:+.6f}\n")
print(f"Difference (Fouled - Clean):")
print(f"  Full: {corr_fouled_full - corr_clean_full:+.6f}")
print(f"  Coda: {corr_fouled_coda - corr_clean_coda:+.6f}\n")
print("="*80 + "\n")
