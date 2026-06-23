#!/usr/bin/env python3
"""
Final test: SAND at BOTTOM, ROCKS on TOP
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

with h5py.File("test_sand_bottom_rocks_top.out", 'r') as f:
    test_sig = -f['rxs/rx1/Ez'][()]
    test_dt = f.attrs.get('dt', 0.0) * 1e9

HEADER_SIZE = 128 * 1024
with open("D:/Codigo/Data/PUERTO-LIMACHE_20230726_EFE_V1_PKC000_588_PKF011_020_CENTRO_BRUTO.DZT", 'rb') as f:
    f.seek(HEADER_SIZE + 15000 * 512 * 4)
    real_sig = np.frombuffer(f.read(512 * 4), dtype=np.int32)[2:].astype(float)
real_dt = 50 / 511

validated_sig = validated_sig / np.max(np.abs(validated_sig))
test_sig = test_sig / np.max(np.abs(test_sig))
real_sig = real_sig / np.max(np.abs(real_sig))

validated_t = np.arange(len(validated_sig)) * validated_dt + 4.0
test_t = np.arange(len(test_sig)) * test_dt + 4.0
real_t = np.arange(len(real_sig)) * real_dt

print("\n" + "="*80)
print("SAND BOTTOM + ROCKS TOP TEST")
print("="*80 + "\n")

common_dt = real_dt
t_max = min(validated_t[-1], test_t[-1], real_t[-1])
tc = np.arange(0, t_max + common_dt, common_dt)

f_validated = interp1d(validated_t, validated_sig, kind='cubic', bounds_error=False, fill_value=0)
f_test = interp1d(test_t, test_sig, kind='cubic', bounds_error=False, fill_value=0)
f_real = interp1d(real_t, real_sig, kind='cubic', bounds_error=False, fill_value=0)

validated_i = f_validated(tc)
test_i = f_test(tc)
real_i = f_real(tc)

mask_coda = tc >= 9
r_validated = np.corrcoef(validated_i[mask_coda], real_i[mask_coda])[0, 1]
r_test = np.corrcoef(test_i[mask_coda], real_i[mask_coda])[0, 1]

print(f"VALIDATED (Single layer):       r = {r_validated:+.6f}")
print(f"TEST (Sand bottom + rocks top): r = {r_test:+.6f}")
print(f"Difference:                      {r_test - r_validated:+.6f} ({100*(r_test-r_validated)/r_validated:+.1f}%)\n")

if r_test > r_validated - 0.01:
    verdict = "EQUIVALENT - No improvement but not worse"
elif r_test > 0.6:
    verdict = "GOOD - Close to validated"
else:
    verdict = "WORSE - Not recommended"

print(f"VERDICT: {verdict}\n")
print("="*80 + "\n")

fig = plt.figure(figsize=(16, 8))
fig.patch.set_facecolor("#0f1117")
gs = gridspec.GridSpec(1, 2, figure=fig, wspace=0.3, left=0.08, right=0.96, top=0.90, bottom=0.10)

ax1 = fig.add_subplot(gs[0, 0])
ax1.set_facecolor("#1a1e2b")
ax1.plot(tc[mask_coda], validated_i[mask_coda], color="#00ffff", lw=2.5, alpha=0.85, label="Validated")
ax1.plot(tc[mask_coda], real_i[mask_coda], color="#ff6b35", lw=2.5, alpha=0.85, label="Real")
ax1.set_xlabel("Time (ns)", fontsize=12, color="#c8d0e0", fontweight='bold')
ax1.set_ylabel("Amplitude", fontsize=12, color="#c8d0e0", fontweight='bold')
ax1.set_title(f"Validated (r={r_validated:+.4f})", fontsize=13, color="#00ffff", fontweight='bold')
ax1.grid(True, color="#2a2f42", alpha=0.2)
ax1.legend(fontsize=11, facecolor='#1a1e2b', labelcolor='#c8d0e0', edgecolor='#2a2f42')
ax1.tick_params(colors="#c8d0e0", labelsize=10)
for spine in ax1.spines.values():
    spine.set_color("#2a2f42")

ax2 = fig.add_subplot(gs[0, 1])
ax2.set_facecolor("#1a1e2b")
ax2.plot(tc[mask_coda], test_i[mask_coda], color="#ff9500", lw=2.5, alpha=0.85, label="Sand+Rocks")
ax2.plot(tc[mask_coda], real_i[mask_coda], color="#ff6b35", lw=2.5, alpha=0.85, label="Real")
ax2.set_xlabel("Time (ns)", fontsize=12, color="#c8d0e0", fontweight='bold')
ax2.set_ylabel("Amplitude", fontsize=12, color="#c8d0e0", fontweight='bold')
color = "#00ff00" if r_test > r_validated - 0.01 else "#ff0000"
ax2.set_title(f"Sand(bottom)+Rocks(top) (r={r_test:+.4f})", fontsize=13, color=color, fontweight='bold')
ax2.grid(True, color="#2a2f42", alpha=0.2)
ax2.legend(fontsize=11, facecolor='#1a1e2b', labelcolor='#c8d0e0', edgecolor='#2a2f42')
ax2.tick_params(colors="#c8d0e0", labelsize=10)
for spine in ax2.spines.values():
    spine.set_color("#2a2f42")

fig.suptitle(f"Sand BOTTOM + Rocks TOP: {r_validated:+.4f} vs {r_test:+.4f} (delta {r_test-r_validated:+.4f})",
             color="#c8d0e0", fontsize=14, fontweight='bold')

png_path = Path("output_test") / "compare_final_sand_rocks.png"
fig.savefig(png_path, dpi=150, bbox_inches='tight', facecolor="#0f1117")
print(f"[SAVE] {png_path}\n")
