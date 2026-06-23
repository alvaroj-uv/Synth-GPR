#!/usr/bin/env python3
"""
Compare stratified ballast vs validated single-layer model.
Stratified: Sand (0-0.1m) → Rocks+Sand (0.1-0.2m) → Rocks+Air (0.2-0.3m)
"""

import numpy as np
import h5py
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from scipy.interpolate import interp1d
from pathlib import Path

with h5py.File("moisture_sigma_0.0001.out", 'r') as f:
    validated_sig = -f['rxs/rx1/Ez'][()]
    validated_dt = f.attrs.get('dt', 0.0) * 1e9

with h5py.File("test_stratified_ballast.out", 'r') as f:
    stratified_sig = -f['rxs/rx1/Ez'][()]
    stratified_dt = f.attrs.get('dt', 0.0) * 1e9

HEADER_SIZE = 128 * 1024
with open("D:/Codigo/Data/PUERTO-LIMACHE_20230726_EFE_V1_PKC000_588_PKF011_020_CENTRO_BRUTO.DZT", 'rb') as f:
    f.seek(HEADER_SIZE + 15000 * 512 * 4)
    real_sig = np.frombuffer(f.read(512 * 4), dtype=np.int32)[2:].astype(float)
real_dt = 50 / 511

validated_sig = validated_sig / np.max(np.abs(validated_sig))
stratified_sig = stratified_sig / np.max(np.abs(stratified_sig))
real_sig = real_sig / np.max(np.abs(real_sig))

validated_t = np.arange(len(validated_sig)) * validated_dt + 4.0
stratified_t = np.arange(len(stratified_sig)) * stratified_dt + 4.0
real_t = np.arange(len(real_sig)) * real_dt

print("\n" + "="*80)
print("STRATIFIED BALLAST COMPARISON")
print("="*80 + "\n")
print("Configuration:")
print("  0-0.1m:   SAND (pure)")
print("  0.1-0.2m: ROCKS + SAND (40% porosity)")
print("  0.2-0.3m: ROCKS + AIR (50% porosity)\n")

common_dt = real_dt
t_max = min(validated_t[-1], stratified_t[-1], real_t[-1])
tc = np.arange(0, t_max + common_dt, common_dt)

f_validated = interp1d(validated_t, validated_sig, kind='cubic', bounds_error=False, fill_value=0)
f_stratified = interp1d(stratified_t, stratified_sig, kind='cubic', bounds_error=False, fill_value=0)
f_real = interp1d(real_t, real_sig, kind='cubic', bounds_error=False, fill_value=0)

validated_i = f_validated(tc)
stratified_i = f_stratified(tc)
real_i = f_real(tc)

mask_coda = tc >= 9
r_validated = np.corrcoef(validated_i[mask_coda], real_i[mask_coda])[0, 1]
r_stratified = np.corrcoef(stratified_i[mask_coda], real_i[mask_coda])[0, 1]

print(f"VALIDATED (Single layer):        r = {r_validated:+.6f}")
print(f"STRATIFIED (Sand-Rocks+Sand-Rocks): r = {r_stratified:+.6f}")

delta = r_stratified - r_validated
pct = 100 * delta / r_validated
print(f"Difference:                      {delta:+.6f} ({pct:+.1f}%)\n")

if r_stratified > r_validated - 0.02:
    verdict = "EXCELLENT - Better or equivalent!"
elif r_stratified > 0.55:
    verdict = "VERY GOOD - Close match"
elif r_stratified > 0.4:
    verdict = "GOOD - Meaningful improvement"
else:
    verdict = "WORSE - Not recommended"

print(f"VERDICT: {verdict}\n")
print("="*80 + "\n")

# Visualization
fig = plt.figure(figsize=(20, 10))
fig.patch.set_facecolor("#0f1117")
gs = gridspec.GridSpec(2, 3, figure=fig, hspace=0.35, wspace=0.3,
                      left=0.07, right=0.96, top=0.93, bottom=0.08)

# Full traces
ax1 = fig.add_subplot(gs[0, 0])
ax1.set_facecolor("#1a1e2b")
ax1.plot(validated_t[validated_t<=50], validated_sig[validated_t<=50], color="#00ffff", lw=1.5, alpha=0.8)
ax1.axvspan(9, 35, alpha=0.08, color='#ffff00')
ax1.set_ylabel("Amplitude", fontsize=10, color="#c8d0e0", fontweight='bold')
ax1.set_title("Validated (Single layer)", fontsize=11, color="#00ffff", fontweight='bold')
ax1.grid(True, color="#2a2f42", alpha=0.2)
ax1.tick_params(colors="#c8d0e0", labelsize=9)
for spine in ax1.spines.values():
    spine.set_color("#2a2f42")
ax1.set_xlim(0, 50)

ax2 = fig.add_subplot(gs[0, 1])
ax2.set_facecolor("#1a1e2b")
ax2.plot(stratified_t[stratified_t<=50], stratified_sig[stratified_t<=50], color="#00ff00", lw=1.5, alpha=0.8)
ax2.axvspan(9, 35, alpha=0.08, color='#ffff00')
ax2.set_ylabel("Amplitude", fontsize=10, color="#c8d0e0", fontweight='bold')
ax2.set_title("Stratified (3 layers)", fontsize=11, color="#00ff00", fontweight='bold')
ax2.grid(True, color="#2a2f42", alpha=0.2)
ax2.tick_params(colors="#c8d0e0", labelsize=9)
for spine in ax2.spines.values():
    spine.set_color("#2a2f42")
ax2.set_xlim(0, 50)

ax3 = fig.add_subplot(gs[0, 2])
ax3.set_facecolor("#1a1e2b")
ax3.plot(validated_t[validated_t<=50], validated_sig[validated_t<=50], color="#00ffff", lw=2.0, alpha=0.8, label="Validated")
ax3.plot(stratified_t[stratified_t<=50], stratified_sig[stratified_t<=50], color="#00ff00", lw=2.0, alpha=0.8, label="Stratified")
ax3.axvspan(9, 35, alpha=0.08, color='#ffff00')
ax3.set_ylabel("Amplitude", fontsize=10, color="#c8d0e0", fontweight='bold')
ax3.set_title("Overlay", fontsize=11, color="#c8d0e0", fontweight='bold')
ax3.grid(True, color="#2a2f42", alpha=0.2)
ax3.tick_params(colors="#c8d0e0", labelsize=9)
ax3.legend(fontsize=9, facecolor='#1a1e2b', labelcolor='#c8d0e0', edgecolor='#2a2f42')
for spine in ax3.spines.values():
    spine.set_color("#2a2f42")
ax3.set_xlim(0, 50)

# Coda comparisons
ax4 = fig.add_subplot(gs[1, 0])
ax4.set_facecolor("#1a1e2b")
ax4.plot(tc[mask_coda], validated_i[mask_coda], color="#00ffff", lw=2.5, alpha=0.85, label="Validated")
ax4.plot(tc[mask_coda], real_i[mask_coda], color="#ff6b35", lw=2.5, alpha=0.85, label="Real")
ax4.fill_between(tc[mask_coda], validated_i[mask_coda], real_i[mask_coda], alpha=0.1, color='cyan')
ax4.set_xlabel("Time (ns)", fontsize=10, color="#c8d0e0", fontweight='bold')
ax4.set_ylabel("Amplitude", fontsize=10, color="#c8d0e0", fontweight='bold')
ax4.set_title(f"Validated vs Real (r={r_validated:+.4f})", fontsize=11, color="#00ffff", fontweight='bold')
ax4.grid(True, color="#2a2f42", alpha=0.2)
ax4.legend(fontsize=9, facecolor='#1a1e2b', labelcolor='#c8d0e0', edgecolor='#2a2f42')
ax4.tick_params(colors="#c8d0e0", labelsize=9)
for spine in ax4.spines.values():
    spine.set_color("#2a2f42")

ax5 = fig.add_subplot(gs[1, 1])
ax5.set_facecolor("#1a1e2b")
ax5.plot(tc[mask_coda], stratified_i[mask_coda], color="#00ff00", lw=2.5, alpha=0.85, label="Stratified")
ax5.plot(tc[mask_coda], real_i[mask_coda], color="#ff6b35", lw=2.5, alpha=0.85, label="Real")
ax5.fill_between(tc[mask_coda], stratified_i[mask_coda], real_i[mask_coda], alpha=0.1, color='green')
ax5.set_xlabel("Time (ns)", fontsize=10, color="#c8d0e0", fontweight='bold')
ax5.set_ylabel("Amplitude", fontsize=10, color="#c8d0e0", fontweight='bold')
color = "#00ff00" if r_stratified > r_validated - 0.02 else "#ff0000"
ax5.set_title(f"Stratified vs Real (r={r_stratified:+.4f})", fontsize=11, color=color, fontweight='bold')
ax5.grid(True, color="#2a2f42", alpha=0.2)
ax5.legend(fontsize=9, facecolor='#1a1e2b', labelcolor='#c8d0e0', edgecolor='#2a2f42')
ax5.tick_params(colors="#c8d0e0", labelsize=9)
for spine in ax5.spines.values():
    spine.set_color("#2a2f42")

# Summary
ax6 = fig.add_subplot(gs[1, 2])
ax6.axis('off')
summary = f"""RESULTS

Validated:    {r_validated:+.6f}
Stratified:   {r_stratified:+.6f}
Difference:   {delta:+.6f}
Percent:      {pct:+.1f}%

{verdict}

Stratified Config:
• 0-0.1m: Sand
• 0.1-0.2m: Rocks+Sand
• 0.2-0.3m: Rocks+Air
"""
ax6.text(0.05, 0.95, summary, transform=ax6.transAxes, fontsize=10, verticalalignment='top', fontfamily='monospace',
        bbox=dict(boxstyle='round', facecolor='#1a1e2b', alpha=0.95, edgecolor='#2a2f42', linewidth=2),
        color='#c8d0e0')

fig.suptitle(f"Stratified Ballast: {r_validated:+.4f} vs {r_stratified:+.4f} ({delta:+.4f}, {pct:+.1f}%)",
             color="#c8d0e0", fontsize=14, fontweight='bold')

png_path = Path("output_test") / "compare_stratified_ballast.png"
fig.savefig(png_path, dpi=150, bbox_inches='tight', facecolor="#0f1117")
print(f"[SAVE] {png_path}\n")
