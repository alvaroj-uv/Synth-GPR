#!/usr/bin/env python3
"""Plot frequency sweep results."""

import json
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

results_file = Path("output_test/freq_opt/freq_results.json")

with open(results_file) as f:
    results = json.load(f)

freqs = [r['freq_mhz'] for r in results]
corrs = [r['correlation'] for r in results]

# Sort by frequency for plotting
sorted_data = sorted(zip(freqs, corrs))
freqs_sorted, corrs_sorted = zip(*sorted_data)

fig, ax = plt.subplots(figsize=(14, 8))
fig.patch.set_facecolor("#0f1117")
ax.set_facecolor("#1a1e2b")

# Plot curve
ax.plot(freqs_sorted, corrs_sorted, 'o-', color="#00ff88", lw=3, markersize=10,
        markeredgewidth=2, markeredgecolor="#c8d0e0", label="Direct Wave Correlation")

# Mark best
best_idx = np.argmax(corrs)
best_freq = freqs[best_idx]
best_corr = corrs[best_idx]
ax.plot(best_freq, best_corr, '*', color="#ffff00", markersize=30,
        markeredgewidth=2, markeredgecolor="#ff6b35", label=f"Best: {best_freq} MHz")

# Mark nominal
ax.axvline(400, color="#ff6b35", lw=2, linestyle='--', alpha=0.6, label="GSSI Nominal (400 MHz)")

ax.axhline(0, color="#2a2f42", lw=0.8, linestyle='-', alpha=0.3)
ax.grid(True, color="#2a2f42", lw=0.5, alpha=0.4)

ax.set_xlabel("Center Frequency (MHz)", fontsize=13, color="#c8d0e0", fontweight='bold')
ax.set_ylabel("Direct Wave Correlation", fontsize=13, color="#c8d0e0", fontweight='bold')
ax.set_title("Frequency Sweep: Direct Wave Matching (Free Space, Bistatic 30mm)",
            fontsize=14, color="#c8d0e0", fontweight='bold', pad=20)
ax.tick_params(colors="#c8d0e0", labelsize=11)
ax.legend(fontsize=11, facecolor='#1a1e2b', labelcolor='#c8d0e0',
         edgecolor='#2a2f42', loc='lower right')

for spine in ax.spines.values():
    spine.set_color("#2a2f42")

# Add annotations
for freq, corr in zip(freqs_sorted, corrs_sorted):
    ax.text(freq, corr + 0.003, f'{corr:.5f}', ha='center', fontsize=9,
           color="#c8d0e0", bbox=dict(boxstyle='round,pad=0.3', facecolor='#0f1117',
           edgecolor='#2a2f42', alpha=0.7))

fig.tight_layout()
fig.savefig("output_test/12_frequency_sweep.png", dpi=150, bbox_inches='tight',
           facecolor="#0f1117")
plt.close(fig)

print(f"\n[SAVE] Frequency sweep plot -> output_test/12_frequency_sweep.png")

# Print summary
print(f"\n{'='*70}")
print("FREQUENCY SWEEP SUMMARY")
print(f"{'='*70}\n")
print(f"Optimal frequency:  {best_freq} MHz")
print(f"Improvement vs 400 MHz: {((corrs[np.argmin(np.abs(np.array(freqs) - 400))]) - best_corr):.6f}")
print(f"\nFrequency progression:")
for freq, corr in sorted_data:
    marker = " [BEST]" if freq == best_freq else ""
    marker += " [NOMINAL]" if freq == 400 else ""
    print(f"  {freq:3d} MHz: {corr:+.6f}{marker}")
