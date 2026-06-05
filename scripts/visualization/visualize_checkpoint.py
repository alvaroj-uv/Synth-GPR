#!/usr/bin/env python3
"""
Visualize checkpoint files (from production pipeline)
Uses your draw_geometry infrastructure
"""

import argparse
import pickle
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np


def visualize_checkpoint(
    checkpoint_path: Path,
    output_png: Path = None,
    title: str = None,
    metadata: str = None,
    dpi: int = 300,
    figsize: tuple = (14, 8),
    verbose: bool = True,
) -> Path:
    """
    Visualize a checkpoint file using your draw_geometry
    """

    if not checkpoint_path.exists():
        print(f"❌ File not found: {checkpoint_path}")
        sys.exit(1)

    if output_png is None:
        output_png = checkpoint_path.parent / f"{checkpoint_path.stem}_{dpi}dpi.png"

    output_png.parent.mkdir(parents=True, exist_ok=True)

    if verbose:
        print(f"Loading: {checkpoint_path.name}")

    # Load checkpoint
    with open(checkpoint_path, 'rb') as f:
        checkpoint = pickle.load(f)

    if verbose:
        print(f"  ✓ Loaded checkpoint")
        if hasattr(checkpoint, 'config'):
            print(f"    antenna_mode: {checkpoint.config.antenna_mode}")
            print(f"    domain: {checkpoint.config.domain_x:.1f}m × {checkpoint.config.domain_y:.1f}m")

    # Create figure
    fig, ax = plt.subplots(figsize=figsize, dpi=dpi)

    # Get domain from checkpoint
    domain_x = checkpoint.config.domain_x if hasattr(checkpoint, 'config') else 0.6
    domain_y = checkpoint.config.domain_y if hasattr(checkpoint, 'config') else 1.5

    # Draw domain background
    ax.add_patch(mpatches.Rectangle((0, 0), domain_x, domain_y,
                                     facecolor='lightgray', edgecolor='black', linewidth=0.5, zorder=0))

    # Draw rocks from checkpoint
    if hasattr(checkpoint, 'rock_positions'):
        for rock in checkpoint.rock_positions:
            if hasattr(rock, 'x') and hasattr(rock, 'y'):
                circle = mpatches.Circle((rock.x, rock.y), 0.02, color='darkgray', zorder=2)
                ax.add_patch(circle)

    # Draw antennas
    if hasattr(checkpoint, 'sources'):
        for src in checkpoint.sources:
            if hasattr(src, 'x') and hasattr(src, 'y'):
                ax.plot(src.x, src.y, 'v', color='red', markersize=10, zorder=5, label='TX')

    if hasattr(checkpoint, 'receivers'):
        for i, rx in enumerate(checkpoint.receivers):
            if hasattr(rx, 'x') and hasattr(rx, 'y'):
                label = 'RX' if i == 0 else None
                ax.plot(rx.x, rx.y, '^', color='blue', markersize=10, zorder=5, label=label)

    # Set limits and labels
    ax.set_xlim(-0.1, domain_x + 0.1)
    ax.set_ylim(-0.1, domain_y + 0.1)
    ax.set_xlabel('X (m)', fontsize=11)
    ax.set_ylabel('Y (m)', fontsize=11)
    ax.set_aspect('equal')
    ax.legend(loc='upper right', fontsize=10)
    ax.grid(True, alpha=0.3)

    # Add title
    if title:
        ax.set_title(title, fontsize=14, fontweight='bold', pad=20)

    # Add metadata
    if metadata:
        ax.text(0.98, 0.02, metadata,
                transform=ax.transAxes, fontsize=9, verticalalignment='bottom',
                horizontalalignment='right', family='monospace',
                bbox=dict(boxstyle='round', facecolor='#E8F4FF', alpha=0.95,
                          edgecolor='#1060D0', linewidth=2))

    plt.tight_layout()
    fig.savefig(output_png, dpi=dpi, bbox_inches='tight', facecolor='white')
    plt.close(fig)

    if verbose:
        size_kb = output_png.stat().st_size / 1024
        print(f"  ✓ Visualized: {output_png.name} ({size_kb:.1f} KB, {dpi} DPI)")

    return output_png


def main():
    parser = argparse.ArgumentParser(
        description="Visualize checkpoint files from production pipeline"
    )

    parser.add_argument(
        "checkpoint",
        type=Path,
        help="Checkpoint file to visualize"
    )
    parser.add_argument(
        "--title",
        help="Plot title (supports \\n for newlines)"
    )
    parser.add_argument(
        "--metadata",
        help="Metadata text (supports \\n for newlines)"
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="Output PNG path"
    )
    parser.add_argument(
        "--dpi",
        type=int,
        default=300,
        help="DPI for PNG (default: 300)"
    )

    args = parser.parse_args()

    title = args.title.replace('\\n', '\n') if args.title else None
    metadata = args.metadata.replace('\\n', '\n') if args.metadata else None

    visualize_checkpoint(
        checkpoint_path=args.checkpoint,
        output_png=args.output,
        title=title,
        metadata=metadata,
        dpi=args.dpi,
        verbose=True,
    )

    print()
    print("="*70)
    print("✅ VISUALIZATION COMPLETE")
    print("="*70)


if __name__ == "__main__":
    main()
