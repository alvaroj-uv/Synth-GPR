#!/usr/bin/env python3
"""
Visualize expected signal differences between monostatic and bistatic
Creates schematic showing coupling vs clean signal
"""

from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt

output_dir = Path("antenna_experiment")
output_dir.mkdir(exist_ok=True)

print("=" * 80)
print("ANTENNA MODE SIGNAL COMPARISON")
print("Expected .out signal differences")
print("=" * 80)

# Create time axis (0-10ns for 400MHz ~ 3m in air)
t = np.linspace(0, 10e-9, 1000)

# Create Ricker wavelet at 400MHz
freq = 400e6
t0 = 1.5e-9  # Pulse center

def ricker(t, f0, t0):
    """Ricker wavelet source"""
    return (1 - 2 * (np.pi * f0 * (t - t0))**2) * np.exp(-(np.pi * f0 * (t - t0))**2)

# 1. Monostatic signal (direct coupling + subsurface)
print("\n1. MONOSTATIC Signal Characteristics")
print("   • TX and RX co-located (same antenna)")
print("   • Direct electromagnetic coupling at T=0")
print("   • Strong early reflections")
print("   • Subsurface signals buried in coupling noise")

# Monostatic includes direct coupling
tx_pulse = ricker(t, freq, t0)
# Early reflection (direct path, high amplitude)
early_refl = 0.8 * ricker(t, freq, 2.5e-9)
# Subsurface reflection (delayed, noisy)
subsurface = 0.3 * ricker(t, freq, 5e-9) + 0.05 * np.random.randn(len(t))

mono_signal = tx_pulse + early_refl + subsurface

# 2. Bistatic signal (no coupling, clean)
print("\n2. BISTATIC Signal Characteristics")
print("   • TX and RX separated by 5cm")
print("   • No direct electromagnetic coupling")
print("   • Delayed signal arrival (no coupling)")
print("   • Clean subsurface reflections")

# Bistatic: Same TX, but RX is 5cm away = ~1.3ns delay
bi_tx_pulse = ricker(t, freq, t0 + 1.3e-9)  # Delayed arrival
# Same subsurface reflection
bi_subsurface = 0.3 * ricker(t, freq, 5e-9) + 0.05 * np.random.randn(len(t))

bi_signal = bi_tx_pulse + bi_subsurface

# 3. Plot comparison
fig, axes = plt.subplots(3, 1, figsize=(14, 10), dpi=150)

# Monostatic
ax = axes[0]
ax.plot(t * 1e9, mono_signal, 'b-', linewidth=1.5, label='Received signal')
ax.axvspan(0, 2, alpha=0.2, color='red', label='TX/RX coupling')
ax.axvspan(4.5, 6, alpha=0.2, color='green', label='Subsurface reflection')
ax.set_xlabel('Time (ns)', fontsize=11)
ax.set_ylabel('Amplitude (V)', fontsize=11)
ax.set_title('MONOSTATIC Configuration\nHigh coupling noise + subsurface signal mixed together',
             fontsize=12, fontweight='bold', color='#1060D0')
ax.legend(loc='upper right', fontsize=10)
ax.grid(True, alpha=0.3)
ax.set_xlim([0, 10])

# Bistatic
ax = axes[1]
ax.plot(t * 1e9, bi_signal, 'r-', linewidth=1.5, label='Received signal')
ax.axvspan(1.3, 3.3, alpha=0.2, color='gray', label='Delayed signal arrival')
ax.axvspan(4.5, 6, alpha=0.2, color='green', label='Subsurface reflection')
ax.set_xlabel('Time (ns)', fontsize=11)
ax.set_ylabel('Amplitude (V)', fontsize=11)
ax.set_title('BISTATIC Configuration\nClean signal with no coupling noise',
             fontsize=12, fontweight='bold', color='#E82020')
ax.legend(loc='upper right', fontsize=10)
ax.grid(True, alpha=0.3)
ax.set_xlim([0, 10])

# Difference (monostatic - bistatic)
ax = axes[2]
diff = mono_signal - bi_signal
ax.plot(t * 1e9, diff, 'purple', linewidth=1.5, label='Monostatic - Bistatic')
ax.axhline(0, color='black', linestyle='--', alpha=0.5)
ax.axvspan(0, 2, alpha=0.2, color='red', label='Coupling difference')
ax.set_xlabel('Time (ns)', fontsize=11)
ax.set_ylabel('Amplitude Difference (V)', fontsize=11)
ax.set_title('Signal Difference (What gprMax .out will show)',
             fontsize=12, fontweight='bold')
ax.legend(loc='upper right', fontsize=10)
ax.grid(True, alpha=0.3)
ax.set_xlim([0, 10])

fig.suptitle('Expected .out Signal Comparison: Monostatic vs Bistatic (400MHz GPR)',
             fontsize=14, fontweight='bold', y=0.995)
plt.tight_layout()

signal_png = output_dir / "antenna_signal_comparison.png"
fig.savefig(signal_png, dpi=150, bbox_inches='tight', facecolor='white')
print(f"\n✓ Signal comparison PNG: {signal_png}")
print(f"  Size: {signal_png.stat().st_size / 1024:.1f} KB")
plt.close(fig)

# 4. Create impact matrix
print("\n3. CREATING IMPACT MATRIX")
fig, ax = plt.subplots(figsize=(12, 6), dpi=150)

# Impact comparison
aspects = [
    'TX-RX Coupling',
    'Signal Noise',
    'Early Artifacts',
    'Subsurface Clarity',
    'ML Training Quality',
    'Real Railway Match'
]

mono_scores = [10, 8, 9, 3, 4, 9]  # Monostatic scores (high coupling = bad for ML, good for real)
bi_scores = [0, 2, 1, 9, 9, 3]      # Bistatic scores (no coupling = good for ML, bad for real)

x = np.arange(len(aspects))
width = 0.35

bars1 = ax.barh(x - width/2, mono_scores, width, label='MONOSTATIC', color='#1060D0', alpha=0.8)
bars2 = ax.barh(x + width/2, bi_scores, width, label='BISTATIC', color='#E82020', alpha=0.8)

# Add value labels
for bars in [bars1, bars2]:
    for bar in bars:
        width_val = bar.get_width()
        ax.text(width_val + 0.2, bar.get_y() + bar.get_height()/2,
                f'{int(width_val)}', ha='left', va='center', fontsize=9)

ax.set_xlabel('Impact Score (0=None, 10=Strong)', fontsize=11)
ax.set_title('Antenna Configuration Impact Analysis',
             fontsize=13, fontweight='bold')
ax.set_yticks(x)
ax.set_yticklabels(aspects, fontsize=11)
ax.legend(loc='lower right', fontsize=11)
ax.set_xlim([0, 12])
ax.grid(True, alpha=0.3, axis='x')

# Add annotations
ax.text(0.5, -1.2, 'MONOSTATIC: Better for real railway (Mbubia standard) but higher noise',
        fontsize=10, style='italic', bbox=dict(boxstyle='round', facecolor='#E8F4FF', alpha=0.8))
ax.text(5.5, -1.2, 'BISTATIC: Better for ML training (cleaner signals) but less realistic',
        fontsize=10, style='italic', bbox=dict(boxstyle='round', facecolor='#FFE8E8', alpha=0.8))

plt.tight_layout()

impact_png = output_dir / "antenna_impact_matrix.png"
fig.savefig(impact_png, dpi=150, bbox_inches='tight', facecolor='white')
print(f"✓ Impact matrix PNG: {impact_png}")
print(f"  Size: {impact_png.stat().st_size / 1024:.1f} KB")
plt.close(fig)

print("\n" + "=" * 80)
print("SUMMARY")
print("=" * 80)
print(f"\nGenerated visualizations in: {output_dir.absolute()}")
print(f"  📊 antenna_signal_comparison.png")
print(f"  📊 antenna_impact_matrix.png")

print(f"\nKey Insights:")
print(f"  1. antenna_mode parameter controls TX-RX position")
print(f"  2. Monostatic (0.000m spacing):")
print(f"     - Direct TX-RX coupling artifacts")
print(f"     - Matches real railway GPR (Mbubia standard)")
print(f"     - Higher noise, harder for ML")
print(f"  3. Bistatic (0.050m spacing):")
print(f"     - No coupling, cleaner subsurface signals")
print(f"     - Better for ML training")
print(f"     - Less realistic for railway deployment")

print(f"\nNext steps:")
print(f"  1. Run gprMax on both .in files")
print(f"  2. Load .out files and extract A-scans")
print(f"  3. Compare time-domain signals")
print(f"  4. Compare frequency spectra")
print(f"  5. Quantify coupling effects (coupling loss in dB)")
