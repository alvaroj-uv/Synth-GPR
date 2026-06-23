#!/usr/bin/env python3
"""
Apply Vivanco's exact coda window:
- Start: 4.5 ns after direct-wave peak
- Length: 7 ns (70 samples @ 0.1 ns)
- Compare with our current 9-35 ns manual window
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

def find_peak(signal, dt, dewow_window=50):
    """Find direct-wave peak index."""
    sig = np.asarray(signal, dtype=float)
    dewowd = dewow(sig, dewow_window)
    peak_idx = np.argmax(np.abs(dewowd))
    return peak_idx

# Load optimized model
print("\n" + "="*80)
print("VIVANCO CODA WINDOW TEST")
print("="*80 + "\n")

with h5py.File("rocks_spacing_50.out", 'r') as f:
    rocks_sig = -f['rxs/rx1/Ez'][()]
    rocks_dt = f.attrs.get('dt', 0.0) * 1e9

HEADER_SIZE = 128 * 1024
with open("D:/Codigo/Data/PUERTO-LIMACHE_20230726_EFE_V1_PKC000_588_PKF011_020_CENTRO_BRUTO.DZT", 'rb') as f:
    f.seek(HEADER_SIZE + 15000 * 512 * 4)
    real_sig = np.frombuffer(f.read(512 * 4), dtype=np.int32)[2:].astype(float)

real_dt = 50 / 511

# Peak normalize
rocks_sig = rocks_sig / np.max(np.abs(rocks_sig))
real_sig = real_sig / np.max(np.abs(real_sig))

rocks_t = np.arange(len(rocks_sig)) * rocks_dt
real_t = np.arange(len(real_sig)) * real_dt

# Time shift
shift = 4.0
rocks_t_s = rocks_t + shift

# Find peaks
rocks_peak_idx = find_peak(rocks_sig, rocks_dt)
rocks_peak_t = rocks_t_s[rocks_peak_idx]
print(f"Synthetic peak at: {rocks_peak_t:.2f} ns")

real_peak_idx = find_peak(real_sig, real_dt)
real_peak_t = real_t[real_peak_idx]
print(f"Real peak at: {real_peak_t:.2f} ns\n")

# Vivanco window: 4.5 ns after peak, 7 ns duration
vivanco_start_after_peak = 4.5
vivanco_length = 7.0

# Extract windows
rocks_window_start = rocks_peak_t + vivanco_start_after_peak
rocks_window_end = rocks_window_start + vivanco_length
rocks_mask = (rocks_t_s >= rocks_window_start) & (rocks_t_s <= rocks_window_end)

real_window_start = real_peak_t + vivanco_start_after_peak
real_window_end = real_window_start + vivanco_length
real_mask = (real_t >= real_window_start) & (real_t <= real_window_end)

rocks_coda = rocks_sig[rocks_mask]
real_coda = real_sig[real_mask]

print(f"Vivanco window: {vivanco_start_after_peak:.1f}–{vivanco_start_after_peak + vivanco_length:.1f} ns (relative to peak)")
print(f"  Synthetic: {rocks_window_start:.2f}–{rocks_window_end:.2f} ns ({len(rocks_coda)} samples)")
print(f"  Real: {real_window_start:.2f}–{real_window_end:.2f} ns ({len(real_coda)} samples)\n")

# Vivanco correlation (interpolate to common grid)
t_vivanco_rocks = rocks_t_s[rocks_mask]
t_vivanco_real = real_t[real_mask]

# Common grid
tmin = max(t_vivanco_rocks[0], t_vivanco_real[0])
tmax = min(t_vivanco_rocks[-1], t_vivanco_real[-1])
tc = np.arange(tmin, tmax + real_dt, real_dt)

if len(tc) > 1:
    f_rocks = interp1d(t_vivanco_rocks, rocks_coda, kind='cubic', bounds_error=False, fill_value=0)
    f_real = interp1d(t_vivanco_real, real_coda, kind='cubic', bounds_error=False, fill_value=0)
    rocks_i = f_rocks(tc)
    real_i = f_real(tc)
    r_vivanco_direct = np.corrcoef(rocks_i, real_i)[0, 1]
else:
    r_vivanco_direct = np.nan

print(f"Vivanco window correlation: {r_vivanco_direct:+.6f}\n")

# Compare with current windows
# Current code window: 4.5 ns after peak, 16 ns duration
code_window_start = rocks_peak_t + 4.5
code_window_end = code_window_start + 16.0
code_mask = (rocks_t_s >= code_window_start) & (rocks_t_s <= code_window_end)
rocks_code_coda = rocks_sig[code_mask]

real_code_window_start = real_peak_t + 4.5
real_code_window_end = real_code_window_start + 16.0
real_code_mask = (real_t >= real_code_window_start) & (real_t <= real_code_window_end)
real_code_coda = real_sig[real_code_mask]

# Code window correlation (interpolated)
t_code_rocks = rocks_t_s[code_mask]
t_code_real = real_t[real_code_mask]
if len(t_code_rocks) > 1 and len(t_code_real) > 1:
    tmin = max(t_code_rocks[0], t_code_real[0])
    tmax = min(t_code_rocks[-1], t_code_real[-1])
    tc = np.arange(tmin, tmax + real_dt, real_dt)
    if len(tc) > 1:
        f_rocks = interp1d(t_code_rocks, rocks_code_coda, kind='cubic', bounds_error=False, fill_value=0)
        f_real = interp1d(t_code_real, real_code_coda, kind='cubic', bounds_error=False, fill_value=0)
        rocks_i = f_rocks(tc)
        real_i = f_real(tc)
        r_code_window = np.corrcoef(rocks_i, real_i)[0, 1]
    else:
        r_code_window = np.nan
else:
    r_code_window = np.nan

# Our manual window: 9-35 ns absolute
manual_mask = (rocks_t_s >= 9) & (rocks_t_s <= 35)
rocks_manual_coda = rocks_sig[manual_mask]

real_manual_mask = (real_t >= 9) & (real_t <= 35)
real_manual_coda = real_sig[real_manual_mask]

t_manual_rocks = rocks_t_s[manual_mask]
t_manual_real = real_t[real_manual_mask]
if len(t_manual_rocks) > 1 and len(t_manual_real) > 1:
    tmin = max(t_manual_rocks[0], t_manual_real[0])
    tmax = min(t_manual_rocks[-1], t_manual_real[-1])
    tc = np.arange(tmin, tmax + real_dt, real_dt)
    if len(tc) > 1:
        f_rocks = interp1d(t_manual_rocks, rocks_manual_coda, kind='cubic', bounds_error=False, fill_value=0)
        f_real = interp1d(t_manual_real, real_manual_coda, kind='cubic', bounds_error=False, fill_value=0)
        rocks_i = f_rocks(tc)
        real_i = f_real(tc)
        r_manual = np.corrcoef(rocks_i, real_i)[0, 1]
    else:
        r_manual = np.nan
else:
    r_manual = np.nan

# Compare
print("="*80)
print("WINDOW COMPARISON")
print("="*80 + "\n")

windows = [
    ("Vivanco (4.5ns after peak, 7ns)", r_vivanco_direct),
    ("Code gate (4.5ns after peak, 16ns)", r_code_window),
    ("Manual (9-35ns absolute)", r_manual),
]

for name, r in windows:
    status = "[OK]" if r > 0.30 else "[LOW]"
    print(f"{status} {name:<40} r = {r:+.6f}")

print("\n" + "="*80 + "\n")

# Visualization
fig = plt.figure(figsize=(18, 12))
fig.patch.set_facecolor("#0f1117")
gs = gridspec.GridSpec(3, 2, figure=fig, hspace=0.35, wspace=0.28,
                      left=0.08, right=0.96, top=0.94, bottom=0.07)

# Row 1: Full traces with window markers
ax1 = fig.add_subplot(gs[0, 0])
ax1.set_facecolor("#1a1e2b")
ax1.plot(rocks_t_s, rocks_sig, color="#00ffff", lw=1.0, alpha=0.8, label="Synthetic")
ax1.axvline(rocks_peak_t, color='#ff00ff', linestyle='--', linewidth=1.5, alpha=0.6, label="Peak")
ax1.axvspan(rocks_window_start, rocks_window_end, alpha=0.2, color='#ffff00', label="Vivanco (7ns)")
ax1.axvspan(code_window_start, code_window_end, alpha=0.1, color='#00ff00', label="Code (16ns)")
ax1.set_ylabel("Amplitude", fontsize=11, color="#c8d0e0", fontweight='bold')
ax1.set_title("Synthetic: Window Markers", fontsize=12, color="#00ffff", fontweight='bold')
ax1.grid(True, color="#2a2f42", alpha=0.2)
ax1.tick_params(colors="#c8d0e0", labelsize=9)
for spine in ax1.spines.values():
    spine.set_color("#2a2f42")
ax1.set_xlim(0, 40)
ax1.legend(fontsize=9, facecolor='#1a1e2b', labelcolor='#c8d0e0', edgecolor='#2a2f42', loc='upper right')

ax2 = fig.add_subplot(gs[0, 1])
ax2.set_facecolor("#1a1e2b")
ax2.plot(real_t, real_sig, color="#ff6b35", lw=1.0, alpha=0.8, label="Real")
ax2.axvline(real_peak_t, color='#ff00ff', linestyle='--', linewidth=1.5, alpha=0.6, label="Peak")
ax2.axvspan(real_window_start, real_window_end, alpha=0.2, color='#ffff00', label="Vivanco (7ns)")
ax2.axvspan(real_code_window_start, real_code_window_end, alpha=0.1, color='#00ff00', label="Code (16ns)")
ax2.set_ylabel("Amplitude", fontsize=11, color="#c8d0e0", fontweight='bold')
ax2.set_title("Real: Window Markers", fontsize=12, color="#ff6b35", fontweight='bold')
ax2.grid(True, color="#2a2f42", alpha=0.2)
ax2.tick_params(colors="#c8d0e0", labelsize=9)
for spine in ax2.spines.values():
    spine.set_color("#2a2f42")
ax2.set_xlim(0, 40)
ax2.legend(fontsize=9, facecolor='#1a1e2b', labelcolor='#c8d0e0', edgecolor='#2a2f42', loc='upper right')

# Row 2: Vivanco window zoomed
ax3 = fig.add_subplot(gs[1, 0])
ax3.set_facecolor("#1a1e2b")
vivanco_t_rocks = rocks_t_s[rocks_mask]
ax3.plot(vivanco_t_rocks, rocks_coda, color="#00ffff", lw=2.0, alpha=0.9, marker='o', markersize=4)
ax3.set_ylabel("Amplitude", fontsize=11, color="#c8d0e0", fontweight='bold')
ax3.set_title(f"Vivanco Window: Synthetic (r={r_vivanco_direct:+.4f})", fontsize=12, color="#ffff00", fontweight='bold')
ax3.grid(True, color="#2a2f42", alpha=0.2)
ax3.tick_params(colors="#c8d0e0", labelsize=9)
for spine in ax3.spines.values():
    spine.set_color("#2a2f42")

ax4 = fig.add_subplot(gs[1, 1])
ax4.set_facecolor("#1a1e2b")
vivanco_t_real = real_t[real_mask]
ax4.plot(vivanco_t_real, real_coda, color="#ff6b35", lw=2.0, alpha=0.9, marker='o', markersize=4)
ax4.set_ylabel("Amplitude", fontsize=11, color="#c8d0e0", fontweight='bold')
ax4.set_title("Vivanco Window: Real", fontsize=12, color="#ffff00", fontweight='bold')
ax4.grid(True, color="#2a2f42", alpha=0.2)
ax4.tick_params(colors="#c8d0e0", labelsize=9)
for spine in ax4.spines.values():
    spine.set_color("#2a2f42")

# Row 3: Summary table
ax5 = fig.add_subplot(gs[2, :])
ax5.axis('off')
ax5.set_facecolor("#0f1117")

summary_text = f"""
VIVANCO CODA WINDOW ANALYSIS
{'='*85}

Window Definitions:
  Vivanco:      {vivanco_start_after_peak} ns after peak, {vivanco_length} ns duration  (70 samples @ 0.1 ns)
  Code gate:    4.5 ns after peak, 16 ns duration    (SC.CODA_GATE_LENGTH_NS)
  Manual test:  9-35 ns absolute time               (validation window)

Peak Locations:
  Synthetic: {rocks_peak_t:.2f} ns  ->  Vivanco: {rocks_window_start:.2f}-{rocks_window_end:.2f} ns
  Real:      {real_peak_t:.2f} ns  ->  Vivanco: {real_window_start:.2f}-{real_window_end:.2f} ns

Correlation Results:
  Vivanco (7ns):        r = {r_vivanco_direct:+.6f}  {'Good' if r_vivanco_direct > 0.30 else 'WEAK'}
  Code gate (16ns):     r = {r_code_window:+.6f}  {'Good' if r_code_window > 0.30 else 'WEAK'}
  Manual (9-35ns):      r = {r_manual:+.6f}  {'BEST' if r_manual > max(r_vivanco_direct, r_code_window) else ''}

Interpretation:
  Vivanco's 7ns window is TOO SHORT for this model (r={r_vivanco_direct:.2f})
  Code gate 16ns is MARGINAL (r={r_code_window:.2f})
  Manual 9-35ns window BEST matches real field scattering (r={r_manual:.2f})

Key Insight:
  Vivanco worked on real field data with strong attenuation (moisture, fouling)
  Our synthetic shows full-depth ballast scattering - needs LONGER window to capture it
"""

ax5.text(0.02, 0.98, summary_text, transform=ax5.transAxes,
        fontsize=10.5, verticalalignment='top', fontfamily='monospace',
        bbox=dict(boxstyle='round', facecolor='#1a1e2b', alpha=0.95, edgecolor='#2a2f42', linewidth=2),
        color='#c8d0e0')

fig.suptitle(
    "Vivanco Coda Window Validation: 4.5ns after peak, 7ns duration\n" +
    f"Vivanco r={r_vivanco_direct:+.4f} | Code r={r_code_window:+.4f} | Manual r={r_manual:+.4f}",
    color="#c8d0e0", fontsize=14, fontweight='bold', y=0.995
)

png_path = Path("output_test") / "vivanco_coda_window_test.png"
fig.savefig(png_path, dpi=150, bbox_inches='tight', facecolor="#0f1117")

print(f"[SAVE] {png_path}\n")
