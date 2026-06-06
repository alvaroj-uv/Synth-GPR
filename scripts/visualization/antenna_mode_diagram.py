#!/usr/bin/env python3
"""
Antenna mode schematic diagram — monostatic vs bistatic.
Called by verify_antenna_mode.py; can also be run standalone.
"""

from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import matplotlib.pyplot as plt


def render_antenna_mode_diagram(output_path: Path, dpi: int = 150) -> Path:
    """Render a monostatic vs bistatic schematic and save to PNG."""
    fig, axes = plt.subplots(1, 2, figsize=(14, 5), dpi=dpi)

    ax = axes[0]
    ax.text(0.5, 0.9, "antenna_mode = 'monostatic'", ha='center', fontsize=12,
            fontweight='bold', transform=ax.transAxes)
    ax.plot([0.5], [0.7], marker='*', markersize=30, color='#1060D0',
            transform=ax.transAxes, label='TX/RX (co-located)')
    ax.text(0.5, 0.5, "TX and RX share same antenna\nSingle position\nOffset = 0.000m",
            ha='center', fontsize=11, transform=ax.transAxes,
            bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.8))
    ax.text(0.5, 0.15, "Used by: Mbubia et al. 2026\nReal railway GPR systems",
            ha='center', fontsize=9, transform=ax.transAxes, style='italic')
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis('off')

    ax = axes[1]
    ax.text(0.5, 0.9, "antenna_mode = 'bistatic'", ha='center', fontsize=12,
            fontweight='bold', transform=ax.transAxes)
    ax.plot([0.35], [0.7], marker='v', markersize=15, color='#E82020',
            transform=ax.transAxes, label='TX')
    ax.plot([0.65], [0.7], marker='^', markersize=15, color='#1060D0',
            transform=ax.transAxes, label='RX')
    ax.text(0.5, 0.5, "Separate TX and RX antennas\nTwo positions\nOffset = 0.050m",
            ha='center', fontsize=11, transform=ax.transAxes,
            bbox=dict(boxstyle='round', facecolor='#FFE8E8', alpha=0.8))
    ax.text(0.5, 0.15, "Used by: Synth-GPR (research)\nCleaner ML training signals",
            ha='center', fontsize=9, transform=ax.transAxes, style='italic')
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis('off')

    fig.suptitle('antenna_mode Parameter Control', fontsize=14, fontweight='bold')
    plt.tight_layout()

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_path, dpi=dpi, bbox_inches='tight')
    plt.close(fig)
    return output_path


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Render antenna mode schematic")
    parser.add_argument("--output", type=Path, default=Path("antenna_mode_verification/antenna_mode_explanation.png"))
    parser.add_argument("--dpi", type=int, default=150)
    args = parser.parse_args()
    out = render_antenna_mode_diagram(args.output, dpi=args.dpi)
    print(f"[OK] {out}")
