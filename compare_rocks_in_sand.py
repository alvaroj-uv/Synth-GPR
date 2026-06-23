#!/usr/bin/env python3
"""
Compare rocks-in-sand model vs validated single-layer moist model.
"""

import numpy as np
import h5py
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from scipy.interpolate import interp1d
from pathlib import Path
import sys
sys.path.insert(0, str(Path.cwd()))
from src.signal_processing import dewow

# Load models
with h5py.File("moisture_sigma_0.0001.out", 'r') as f:
    validated_sig = -f['rxs/rx1/Ez'][()]
    validated_dt = f.attrs.get('dt', 0.0) * 1e9

with h5py.File("test_rocks_in_sand.out", 'r') as f:
    sand_sig = -f['rxs/rx1/Ez'][()]
    sand_dt = f.attrs.get('dt', 0.0) * 1e9

# Load real
HEADER_SIZE = 128 * 1024
with open("D:/Codigo/Data/PUERTO-LIMACHE_20230726_EFE_V1_PKC000_588_PKF011_020_CENTRO_BRUTO.DZT", 'rb') as f:
    f.seek(HEADER_SIZE + 15000 * 512 * 4)
    real_sig = np.frombuffer(f.read(512 * 4), dtype=np.int32)[2:].astype(float)

real_dt = 50 / 511

# Normalize
validated_sig = validated_sig / np.max(np.abs(validated_sig))
sand_sig = sand_sig / np.max(np.abs(sand_sig))
real_sig = real_sig / np.max(np.abs(real_sig))

# Time arrays
validated_t = np.arange(len(validated_sig)) * validated_dt + 4.0
sand_t = np.arange(len(sand_sig)) * sand_dt + 4.0
real_t = np.arange(len(real_sig)) * real_dt

print("\n" + "="*80)
print("ROCKS-IN-SAND COMPARISON")
print("="*80 + "\n")

# Correlations on common grid (9-35ns)
common_dt = real_dt
t_max = min(validated_t[-1], sand_t[-1], real_t[-1])
tc = np.arange(0, t_max + common_dt, common_dt)

f_validated = interp1d(validated_t, validated_sig, kind='cubic', bounds_error=False, fill_value=0)
f_sand = interp1d(sand_t, sand_sig, kind='cubic', bounds_error=False, fill_value=0)
f_real = interp1d(real_t, real_sig, kind='cubic', bounds_error=False, fill_value=0)

validated_i = f_validated(tc)
sand_i = f_sand(tc)
real_i = f_real(tc)

# Full correlations
r_validated_full = np.corrcoef(validated_i, real_i)[0, 1]
r_sand_full = np.corrcoef(sand_i, real_i)[0, 1]

# Coda correlations
mask_coda = tc >= 9
r_validated_coda = np.corrcoef(validated_i[mask_coda], real_i[mask_coda])[0, 1]
r_sand_coda = np.corrcoef(sand_i[mask_coda], real_i[mask_coda])[0, 1]

print(f"VALIDATED MODEL (Single-layer, moist):")
print(f"  Full: {r_validated_full:+.6f}")
print(f"  Coda (9-35ns): {r_validated_coda:+.6f}\n")

print(f"ROCKS-IN-SAND MODEL (Two-layer):")
print(f"  Full: {r_sand_full:+.6f}")
print(f"  Coda (9-35ns): {r_sand_coda:+.6f}\n")

improvement = r_sand_coda - r_validated_coda
pct_change = 100 * improvement / r_validated_coda

print(f"DIFFERENCE:")
print(f"  Coda improvement: {improvement:+.6f} ({pct_change:+.1f}%)\n")

if abs(improvement) < 0.01:
    verdict = "MARGINAL - Not worth added complexity"
elif improvement > 0.02:
    verdict = "SIGNIFICANT - Consider for production"
else:
    verdict = "MODEST - Validated model still better"

print(f"VERDICT: {verdict}\n")
print("="*80 + "\n")

# Visualization
fig = plt.figure(figsize=(18, 10))
fig.patch.set_facecolor("#0f1117")
gs = gridspec.GridSpec(2, 3, figure=fig, hspace=0.32, wspace=0.3,
                      left=0.07, right=0.96, top=0.93, bottom=0.08)

# Row 1: Both models
ax1 = fig.add_subplot(gs[0, 0])
ax1.set_facecolor("#1a1e2b")
ax1.plot(validated_t[validated_t<=50], validated_sig[validated_t<=50], color="#00ffff", lw=1.5, alpha=0.8, label="Validated (single-layer)")
ax1.axvspan(9, 35, alpha=0.08, color='#ffff00')
ax1.set_ylabel("Amplitude", fontsize=10, color="#c8d0e0", fontweight='bold')
ax1.set_title("Validated Model", fontsize=11, color="#00ffff", fontweight='bold')
ax1.grid(True, color="#2a2f42", alpha=0.2)
ax1.tick_params(colors="#c8d0e0", labelsize=9)
for spine in ax1.spines.values():
    spine.set_color("#2a2f42")
ax1.set_xlim(0, 50)
ax1.legend(fontsize=9, facecolor='#1a1e2b', labelcolor='#c8d0e0', edgecolor='#2a2f42')

ax2 = fig.add_subplot(gs[0, 1])
ax2.set_facecolor("#1a1e2b")
ax2.plot(sand_t[sand_t<=50], sand_sig[sand_t<=50], color="#ff9500", lw=1.5, alpha=0.8, label="Rocks-in-sand (two-layer)")
ax2.axvspan(9, 35, alpha=0.08, color='#ffff00')
ax2.set_ylabel("Amplitude", fontsize=10, color="#c8d0e0", fontweight='bold')
ax2.set_title("Rocks-in-Sand Model", fontsize=11, color="#ff9500", fontweight='bold')
ax2.grid(True, color="#2a2f42", alpha=0.2)
ax2.tick_params(colors="#c8d0e0", labelsize=9)
for spine in ax2.spines.values():
    spine.set_color("#2a2f42")
ax2.set_xlim(0, 50)
ax2.legend(fontsize=9, facecolor='#1a1e2b', labelcolor='#c8d0e0', edgecolor='#2a2f42')

# Overlay
ax3 = fig.add_subplot(gs[0, 2])
ax3.set_facecolor("#1a1e2b")
mask = tc <= 50
ax3.plot(validated_t[validated_t<=50], validated_sig[validated_t<=50], color="#00ffff", lw=2.0, alpha=0.8, label="Validated")
ax3.plot(sand_t[sand_t<=50], sand_sig[sand_t<=50], color="#ff9500", lw=2.0, alpha=0.8, label="Sand")
ax3.axvspan(9, 35, alpha=0.08, color='#ffff00')
ax3.set_ylabel("Amplitude", fontsize=10, color="#c8d0e0", fontweight='bold')
ax3.set_title("Direct Overlay", fontsize=11, color="#c8d0e0", fontweight='bold')
ax3.grid(True, color="#2a2f42", alpha=0.2)
ax3.tick_params(colors="#c8d0e0", labelsize=9)
for spine in ax3.spines.values():
    spine.set_color("#2a2f42")
ax3.set_xlim(0, 50)
ax3.legend(fontsize=9, facecolor='#1a1e2b', labelcolor='#c8d0e0', edgecolor='#2a2f42')

# Row 2: Coda comparisons
ax4 = fig.add_subplot(gs[1, 0])
ax4.set_facecolor("#1a1e2b")
ax4.plot(tc[mask_coda], validated_i[mask_coda], color="#00ffff", lw=2.5, alpha=0.85, label="Validated")
ax4.plot(tc[mask_coda], real_i[mask_coda], color="#ff6b35", lw=2.5, alpha=0.85, label="Real")
ax4.fill_between(tc[mask_coda], validated_i[mask_coda], real_i[mask_coda], alpha=0.1, color='cyan')
ax4.set_xlabel("Time (ns)", fontsize=10, color="#c8d0e0", fontweight='bold')
ax4.set_ylabel("Amplitude", fontsize=10, color="#c8d0e0", fontweight='bold')
ax4.set_title(f"Validated vs Real (r={r_validated_coda:+.4f})", fontsize=11, color="#00ffff", fontweight='bold')
ax4.grid(True, color="#2a2f42", alpha=0.2)
ax4.legend(fontsize=9, facecolor='#1a1e2b', labelcolor='#c8d0e0', edgecolor='#2a2f42')
ax4.tick_params(colors="#c8d0e0", labelsize=9)
for spine in ax4.spines.values():
    spine.set_color("#2a2f42")

ax5 = fig.add_subplot(gs[1, 1])
ax5.set_facecolor("#1a1e2b")
ax5.plot(tc[mask_coda], sand_i[mask_coda], color="#ff9500", lw=2.5, alpha=0.85, label="Sand model")
ax5.plot(tc[mask_coda], real_i[mask_coda], color="#ff6b35", lw=2.5, alpha=0.85, label="Real")
ax5.fill_between(tc[mask_coda], sand_i[mask_coda], real_i[mask_coda], alpha=0.1, color='orange')
ax5.set_xlabel("Time (ns)", fontsize=10, color="#c8d0e0", fontweight='bold')
ax5.set_ylabel("Amplitude", fontsize=10, color="#c8d0e0", fontweight='bold')
ax5.set_title(f"Rocks-in-Sand vs Real (r={r_sand_coda:+.4f})", fontsize=11, color="#ff9500", fontweight='bold')
ax5.grid(True, color="#2a2f42", alpha=0.2)
ax5.legend(fontsize=9, facecolor='#1a1e2b', labelcolor='#c8d0e0', edgecolor='#2a2f42')
ax5.tick_params(colors="#c8d0e0", labelsize=9)
for spine in ax5.spines.values():
    spine.set_color("#2a2f42")

# Summary
ax6 = fig.add_subplot(gs[1, 2])
ax6.axis('off')
ax6.set_facecolor("#0f1117")

summary = f"""
COMPARISON RESULTS

Validated Model (CURRENT):
  • Single 300mm layer
  • sigma = 0.0001 S/m
  • Coda r = {r_validated_coda:+.6f}

Rocks-in-Sand Model (NEW):
  • 150mm ballast + 150mm sand
  • Dual sigma values
  • Coda r = {r_sand_coda:+.6f}

Difference:
  Delta r = {improvement:+.6f}
  Change = {pct_change:+.1f}%

Verdict:
  {verdict}

Recommendation:
  {"STAY with validated" if abs(improvement) < 0.02 else "EXPLORE sand layer"}
"""

ax6.text(0.05, 0.95, summary, transform=ax6.transAxes,
        fontsize=10, verticalalignment='top', fontfamily='monospace',
        bbox=dict(boxstyle='round', facecolor='#1a1e2b', alpha=0.95, edgecolor='#2a2f42', linewidth=2),
        color='#c8d0e0')

fig.suptitle(
    f"Rocks-in-Sand Two-Layer Model vs Validated Single-Layer\n" +
    f"Coda: Validated={r_validated_coda:+.4f} vs Sand={r_sand_coda:+.4f} (diff={improvement:+.4f})",
    color="#c8d0e0", fontsize=13, fontweight='bold', y=0.97
)

png_path = Path("output_test") / "compare_rocks_in_sand.png"
fig.savefig(png_path, dpi=150, bbox_inches='tight', facecolor="#0f1117")
print(f"[SAVE] {png_path}\n")
