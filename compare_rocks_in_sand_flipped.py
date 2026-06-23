#!/usr/bin/env python3
"""
Compare flipped rocks-in-sand (correct layer order) vs validated model.
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

# Load models
with h5py.File("moisture_sigma_0.0001.out", 'r') as f:
    validated_sig = -f['rxs/rx1/Ez'][()]
    validated_dt = f.attrs.get('dt', 0.0) * 1e9

with h5py.File("test_rocks_in_sand_flipped.out", 'r') as f:
    flipped_sig = -f['rxs/rx1/Ez'][()]
    flipped_dt = f.attrs.get('dt', 0.0) * 1e9

# Load real
HEADER_SIZE = 128 * 1024
with open("D:/Codigo/Data/PUERTO-LIMACHE_20230726_EFE_V1_PKC000_588_PKF011_020_CENTRO_BRUTO.DZT", 'rb') as f:
    f.seek(HEADER_SIZE + 15000 * 512 * 4)
    real_sig = np.frombuffer(f.read(512 * 4), dtype=np.int32)[2:].astype(float)

real_dt = 50 / 511

# Normalize
validated_sig = validated_sig / np.max(np.abs(validated_sig))
flipped_sig = flipped_sig / np.max(np.abs(flipped_sig))
real_sig = real_sig / np.max(np.abs(real_sig))

# Time arrays
validated_t = np.arange(len(validated_sig)) * validated_dt + 4.0
flipped_t = np.arange(len(flipped_sig)) * flipped_dt + 4.0
real_t = np.arange(len(real_sig)) * real_dt

print("\n" + "="*80)
print("FLIPPED ROCKS-IN-SAND COMPARISON")
print("="*80 + "\n")

# Correlations on common grid
common_dt = real_dt
t_max = min(validated_t[-1], flipped_t[-1], real_t[-1])
tc = np.arange(0, t_max + common_dt, common_dt)

f_validated = interp1d(validated_t, validated_sig, kind='cubic', bounds_error=False, fill_value=0)
f_flipped = interp1d(flipped_t, flipped_sig, kind='cubic', bounds_error=False, fill_value=0)
f_real = interp1d(real_t, real_sig, kind='cubic', bounds_error=False, fill_value=0)

validated_i = f_validated(tc)
flipped_i = f_flipped(tc)
real_i = f_real(tc)

# Coda correlations
mask_coda = tc >= 9
r_validated_coda = np.corrcoef(validated_i[mask_coda], real_i[mask_coda])[0, 1]
r_flipped_coda = np.corrcoef(flipped_i[mask_coda], real_i[mask_coda])[0, 1]

print(f"VALIDATED MODEL (Single-layer, moist):")
print(f"  Coda (9-35ns): {r_validated_coda:+.6f}\n")

print(f"FLIPPED ROCKS-IN-SAND MODEL (Top rocks, bottom sand):")
print(f"  Coda (9-35ns): {r_flipped_coda:+.6f}\n")

improvement = r_flipped_coda - r_validated_coda
pct_change = 100 * improvement / r_validated_coda

print(f"DIFFERENCE:")
print(f"  Coda: {improvement:+.6f} ({pct_change:+.1f}%)\n")

if improvement > 0.02:
    verdict = "SIGNIFICANT IMPROVEMENT - Worth exploring"
elif improvement > -0.01:
    verdict = "EQUIVALENT - No real advantage"
else:
    verdict = "WORSE - Validated model still better"

print(f"VERDICT: {verdict}\n")
print("="*80 + "\n")

# Visualization
fig = plt.figure(figsize=(18, 10))
fig.patch.set_facecolor("#0f1117")
gs = gridspec.GridSpec(2, 2, figure=fig, hspace=0.35, wspace=0.3,
                      left=0.08, right=0.96, top=0.93, bottom=0.08)

# Full traces
ax1 = fig.add_subplot(gs[0, 0])
ax1.set_facecolor("#1a1e2b")
ax1.plot(validated_t[validated_t<=50], validated_sig[validated_t<=50], color="#00ffff", lw=1.5, alpha=0.8)
ax1.axvspan(9, 35, alpha=0.08, color='#ffff00')
ax1.set_ylabel("Amplitude", fontsize=11, color="#c8d0e0", fontweight='bold')
ax1.set_title("Validated (Single-layer)", fontsize=12, color="#00ffff", fontweight='bold')
ax1.grid(True, color="#2a2f42", alpha=0.2)
ax1.tick_params(colors="#c8d0e0", labelsize=9)
for spine in ax1.spines.values():
    spine.set_color("#2a2f42")
ax1.set_xlim(0, 50)

ax2 = fig.add_subplot(gs[0, 1])
ax2.set_facecolor("#1a1e2b")
ax2.plot(flipped_t[flipped_t<=50], flipped_sig[flipped_t<=50], color="#ff9500", lw=1.5, alpha=0.8)
ax2.axvspan(9, 35, alpha=0.08, color='#ffff00')
ax2.set_ylabel("Amplitude", fontsize=11, color="#c8d0e0", fontweight='bold')
ax2.set_title("Flipped Rocks-in-Sand (Top rocks, bottom sand)", fontsize=12, color="#ff9500", fontweight='bold')
ax2.grid(True, color="#2a2f42", alpha=0.2)
ax2.tick_params(colors="#c8d0e0", labelsize=9)
for spine in ax2.spines.values():
    spine.set_color("#2a2f42")
ax2.set_xlim(0, 50)

# Coda comparisons
ax3 = fig.add_subplot(gs[1, 0])
ax3.set_facecolor("#1a1e2b")
ax3.plot(tc[mask_coda], validated_i[mask_coda], color="#00ffff", lw=2.5, alpha=0.85, label="Validated")
ax3.plot(tc[mask_coda], real_i[mask_coda], color="#ff6b35", lw=2.5, alpha=0.85, label="Real")
ax3.set_xlabel("Time (ns)", fontsize=11, color="#c8d0e0", fontweight='bold')
ax3.set_ylabel("Amplitude", fontsize=11, color="#c8d0e0", fontweight='bold')
ax3.set_title(f"Validated vs Real (r={r_validated_coda:+.4f})", fontsize=12, color="#00ffff", fontweight='bold')
ax3.grid(True, color="#2a2f42", alpha=0.2)
ax3.legend(fontsize=10, facecolor='#1a1e2b', labelcolor='#c8d0e0', edgecolor='#2a2f42')
ax3.tick_params(colors="#c8d0e0", labelsize=9)
for spine in ax3.spines.values():
    spine.set_color("#2a2f42")

ax4 = fig.add_subplot(gs[1, 1])
ax4.set_facecolor("#1a1e2b")
ax4.plot(tc[mask_coda], flipped_i[mask_coda], color="#ff9500", lw=2.5, alpha=0.85, label="Flipped")
ax4.plot(tc[mask_coda], real_i[mask_coda], color="#ff6b35", lw=2.5, alpha=0.85, label="Real")
ax4.set_xlabel("Time (ns)", fontsize=11, color="#c8d0e0", fontweight='bold')
ax4.set_ylabel("Amplitude", fontsize=11, color="#c8d0e0", fontweight='bold')
status_color = "#00ff00" if improvement > 0 else "#ff0000"
ax4.set_title(f"Flipped vs Real (r={r_flipped_coda:+.4f}) [{improvement:+.4f}]", fontsize=12, color=status_color, fontweight='bold')
ax4.grid(True, color="#2a2f42", alpha=0.2)
ax4.legend(fontsize=10, facecolor='#1a1e2b', labelcolor='#c8d0e0', edgecolor='#2a2f42')
ax4.tick_params(colors="#c8d0e0", labelsize=9)
for spine in ax4.spines.values():
    spine.set_color("#2a2f42")

fig.suptitle(
    f"Layer Order Test: Does putting rocks on top improve the match?\n" +
    f"Validated={r_validated_coda:+.4f} vs Flipped={r_flipped_coda:+.4f} (diff={improvement:+.4f}, {pct_change:+.1f}%)",
    color="#c8d0e0", fontsize=13, fontweight='bold', y=0.97
)

png_path = Path("output_test") / "compare_rocks_in_sand_flipped.png"
fig.savefig(png_path, dpi=150, bbox_inches='tight', facecolor="#0f1117")
print(f"[SAVE] {png_path}\n")
