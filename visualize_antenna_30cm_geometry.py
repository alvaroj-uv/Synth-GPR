#!/usr/bin/env python3
"""
Visualize the 30cm antenna height geometry configuration.
"""

import sys
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as patches


def main():
    # Domain dimensions
    domain_x = 0.5  # m
    domain_y = 0.65  # m
    domain_z = 0.003  # m (2D extruded)

    # Layers
    air_bottom = (0.0, 0.05)      # 50 mm
    ballast = (0.05, 0.35)        # 300 mm
    air_top = (0.35, 0.65)        # 300 mm

    # Antenna
    tx_x = 0.25
    antenna_y = 0.65
    rx_x = 0.28
    antenna_z = 0.0015

    # Create figure
    fig, ax = plt.subplots(figsize=(16, 10))
    fig.patch.set_facecolor("#0f1117")
    ax.set_facecolor("#1a1e2b")

    # Draw domain boundary
    domain_rect = patches.Rectangle((0, 0), domain_x, domain_y,
                                    linewidth=3, edgecolor='#ffffff',
                                    facecolor='none', linestyle='--', alpha=0.5)
    ax.add_patch(domain_rect)

    # Draw layers
    # Air bottom
    air_bottom_rect = patches.Rectangle((0, air_bottom[0]), domain_x,
                                       air_bottom[1] - air_bottom[0],
                                       facecolor='#87ceeb', alpha=0.3,
                                       edgecolor='#00d9ff', linewidth=2)
    ax.add_patch(air_bottom_rect)
    ax.text(domain_x/2, (air_bottom[0] + air_bottom[1])/2,
           f'AIR\n{(air_bottom[1]-air_bottom[0])*1000:.0f}mm',
           ha='center', va='center', fontsize=12, color='#00d9ff', fontweight='bold',
           bbox=dict(boxstyle='round', facecolor='#1a1e2b', alpha=0.8))

    # Ballast
    ballast_rect = patches.Rectangle((0, ballast[0]), domain_x,
                                    ballast[1] - ballast[0],
                                    facecolor='#8b7355', alpha=0.5,
                                    edgecolor='#d4a574', linewidth=2)
    ax.add_patch(ballast_rect)
    ax.text(domain_x/2, (ballast[0] + ballast[1])/2,
           f'CLEAN BALLAST\neps=5.1\n{(ballast[1]-ballast[0])*1000:.0f}mm',
           ha='center', va='center', fontsize=12, color='#d4a574', fontweight='bold',
           bbox=dict(boxstyle='round', facecolor='#1a1e2b', alpha=0.8))

    # Air top
    air_top_rect = patches.Rectangle((0, air_top[0]), domain_x,
                                    air_top[1] - air_top[0],
                                    facecolor='#87ceeb', alpha=0.3,
                                    edgecolor='#00d9ff', linewidth=2)
    ax.add_patch(air_top_rect)
    ax.text(domain_x/2, (air_top[0] + air_top[1])/2,
           f'AIR\n{(air_top[1]-air_top[0])*1000:.0f}mm\n(ANTENNA GAP)',
           ha='center', va='center', fontsize=12, color='#00d9ff', fontweight='bold',
           bbox=dict(boxstyle='round', facecolor='#1a1e2b', alpha=0.8))

    # Draw surface line
    ax.axhline(ballast[1], color='#ffff00', linestyle='--', linewidth=2.5, alpha=0.7)
    ax.text(-0.02, ballast[1], f'Surface\ny={ballast[1]:.2f}m',
           ha='right', va='center', fontsize=10, color='#ffff00', fontweight='bold',
           bbox=dict(boxstyle='round', facecolor='#1a1e2b', alpha=0.8))

    # Draw antenna (TX)
    ax.scatter([tx_x], [antenna_y], color='#ff0000', s=400, marker='^',
              edgecolor='white', linewidth=2.5, zorder=10, label='TX')
    ax.text(tx_x, antenna_y + 0.03, f'TX\n({tx_x:.2f}, {antenna_y:.2f})',
           ha='center', va='bottom', fontsize=10, color='#ff0000', fontweight='bold',
           bbox=dict(boxstyle='round', facecolor='#1a1e2b', edgecolor='#ff0000'))

    # Draw antenna (RX)
    ax.scatter([rx_x], [antenna_y], color='#00ff00', s=400, marker='v',
              edgecolor='white', linewidth=2.5, zorder=10, label='RX')
    ax.text(rx_x, antenna_y + 0.03, f'RX\n({rx_x:.2f}, {antenna_y:.2f})',
           ha='center', va='bottom', fontsize=10, color='#00ff00', fontweight='bold',
           bbox=dict(boxstyle='round', facecolor='#1a1e2b', edgecolor='#00ff00'))

    # Draw antenna height indicator
    ax.plot([tx_x - 0.02, tx_x - 0.02], [ballast[1], antenna_y],
           color='#ff00ff', linewidth=3, linestyle=':', alpha=0.8)
    antenna_height_m = antenna_y - ballast[1]
    antenna_height_cm = antenna_height_m * 100
    ax.text(tx_x - 0.05, (ballast[1] + antenna_y) / 2,
           f'Height\n{antenna_height_cm:.0f}cm',
           ha='right', va='center', fontsize=11, color='#ff00ff', fontweight='bold',
           bbox=dict(boxstyle='round', facecolor='#1a1e2b', edgecolor='#ff00ff', linewidth=2))

    # Draw bistatic spacing indicator
    ax.annotate('', xy=(rx_x, antenna_y - 0.05), xytext=(tx_x, antenna_y - 0.05),
               arrowprops=dict(arrowstyle='<->', color='#ffff00', lw=2.5))
    bistatic_mm = (rx_x - tx_x) * 1000
    ax.text((tx_x + rx_x) / 2, antenna_y - 0.08,
           f'Bistatic spacing\n{bistatic_mm:.0f}mm',
           ha='center', va='top', fontsize=10, color='#ffff00', fontweight='bold',
           bbox=dict(boxstyle='round', facecolor='#1a1e2b', edgecolor='#ffff00', linewidth=1.5))

    # Domain dimensions annotation
    ax.text(domain_x / 2, -0.08, f'Domain X: {domain_x}m',
           ha='center', va='top', fontsize=10, color='#c8d0e0', fontweight='bold')
    ax.text(-0.02, domain_y / 2, f'Domain Y: {domain_y}m',
           ha='right', va='center', fontsize=10, color='#c8d0e0', fontweight='bold',
           rotation=90)

    # Grid lines
    ax.grid(True, color='#2a2f42', alpha=0.3, linestyle='-', linewidth=0.5)

    # Labels and formatting
    ax.set_xlabel("X (meters)", fontsize=12, color="#c8d0e0", fontweight='bold')
    ax.set_ylabel("Y (meters)", fontsize=12, color="#c8d0e0", fontweight='bold')
    ax.set_title("Geometry Configuration: Clean Ballast + 30cm Antenna Height\n" +
                "420MHz Bistatic GPR Configuration",
                fontsize=14, color="#00d9ff", fontweight='bold', pad=20)

    ax.set_xlim(-0.08, domain_x + 0.02)
    ax.set_ylim(-0.12, domain_y + 0.05)
    ax.set_aspect('equal')

    ax.tick_params(colors="#c8d0e0", labelsize=10)
    for spine in ax.spines.values():
        spine.set_color("#2a2f42")

    # Legend
    ax.legend(fontsize=11, facecolor='#1a1e2b', labelcolor='#c8d0e0',
             edgecolor='#2a2f42', loc='upper left')

    # Save
    png_path = Path("output_test") / "antenna_30cm_geometry.png"
    fig.savefig(png_path, dpi=150, bbox_inches='tight', facecolor="#0f1117")
    print(f"[SAVE] {png_path}\n")

    # Print summary
    print("="*80)
    print("GEOMETRY CONFIGURATION SUMMARY")
    print("="*80 + "\n")

    print("Domain:")
    print(f"  X: {domain_x} m (scan width)")
    print(f"  Y: {domain_y} m (air + subsurface + antenna gap)")
    print(f"  Z: {domain_z} m (2D, extruded)\n")

    print("Layers (bottom to top):")
    print(f"  Air (bottom):     y=[{air_bottom[0]:.2f}, {air_bottom[1]:.2f}] m  ({(air_bottom[1]-air_bottom[0])*1000:.0f} mm)")
    print(f"  Clean Ballast:    y=[{ballast[0]:.2f}, {ballast[1]:.2f}] m  ({(ballast[1]-ballast[0])*1000:.0f} mm)  eps=5.1")
    print(f"  Air (top):        y=[{air_top[0]:.2f}, {air_top[1]:.2f}] m  ({(air_top[1]-air_top[0])*1000:.0f} mm)\n")

    print("Antenna Configuration:")
    print(f"  TX position:      x={tx_x} m, y={antenna_y} m, z={antenna_z} m")
    print(f"  RX position:      x={rx_x} m, y={antenna_y} m, z={antenna_z} m")
    print(f"  Antenna height:   {(antenna_y - ballast[1])*100:.0f} cm above surface")
    print(f"  Bistatic spacing: {(rx_x - tx_x)*1000:.0f} mm")
    print(f"  Frequency:        420 MHz (Gaussian source)\n")

    print("Simulation Parameters:")
    print(f"  Time window:      50 ns")
    print(f"  Grid spacing:     dx=dy=dz=3.0 mm")
    print(f"  Material count:   1 (clean_ballast)")
    print()

    return 0


if __name__ == "__main__":
    sys.exit(main())
