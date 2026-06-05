#!/usr/bin/env python3
"""
Generic Scene Renderer
Visualizes any .in file with parameterized metadata and styling
Reuses existing draw_geometry infrastructure
"""

import argparse
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.visualization.scene import parse_in_file, draw_geometry
import matplotlib.pyplot as plt


def render_scene(
    in_file: Path,
    output_png: Path = None,
    title: str = None,
    metadata: str = None,
    dpi: int = 300,
    figsize: tuple = (14, 8),
    verbose: bool = True,
) -> Path:
    """
    Render a scene from .in file with custom metadata

    Args:
        in_file: Path to .in file
        output_png: Output PNG path (default: same as input with .png extension)
        title: Title for the plot
        metadata: Text for metadata box (right-aligned)
        dpi: DPI for PNG output
        figsize: Figure size (width, height)
        verbose: Print progress

    Returns:
        Path to generated PNG
    """

    if not in_file.exists():
        print(f"❌ File not found: {in_file}")
        sys.exit(1)

    # Default output path
    if output_png is None:
        output_png = in_file.parent / f"{in_file.stem}_{dpi}dpi.png"

    output_png.parent.mkdir(parents=True, exist_ok=True)

    if verbose:
        print(f"Rendering: {in_file.name}")

    # Parse scene
    scene = parse_in_file(in_file)

    # Fix monostatic: co-locate RX with TX (if both exist)
    if scene.tx and scene.receivers:
        for rx in scene.receivers:
            rx.x = scene.tx.x

    if verbose:
        print(f"  ✓ Parsed: {scene.domain_x:.1f}m × {scene.domain_y:.1f}m")
        if scene.tx:
            print(f"  ✓ Antenna: TX @ {scene.tx.x:.3f}m, RX @ {scene.receivers[0].x if scene.receivers else 'none':.3f}m")

    # Create figure
    fig, ax = plt.subplots(figsize=figsize, dpi=dpi)
    draw_geometry(ax, scene)

    # Add title if provided
    if title:
        ax.set_title(title, fontsize=14, fontweight='bold', pad=20)

    # Add metadata box if provided
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
        print(f"  ✓ Saved: {output_png.name} ({size_kb:.1f} KB, {dpi} DPI)")

    return output_png


def main():
    parser = argparse.ArgumentParser(
        description="Generic scene renderer - visualize .in files with custom metadata",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:

  # Render with default metadata
  python render_scene.py scene.in

  # Render with custom title and metadata
  python render_scene.py scene.in \
    --title "My Scene" \
    --metadata "Custom metadata text here"

  # Mbubia-style rendering (parameterized!)
  python render_scene.py scene.in \
    --title "Mbubia-Style Scene - Clean Ballast\\n1.4 GHz, Monostatic Antenna" \
    --metadata "Reference: Mbubia et al. 2026\\nFrequency: 1.4 GHz\\nAntenna: Monostatic (TX/RX co-located)" \
    --dpi 300 \
    --output results/mbubia/

  # Batch render multiple files
  for file in *.in; do
    python render_scene.py "$file" --dpi 300 --output results/
  done
        """)

    parser.add_argument(
        "in_file",
        type=Path,
        help=".in file to render"
    )
    parser.add_argument(
        "--title",
        help="Plot title (supports \\n for newlines)"
    )
    parser.add_argument(
        "--metadata",
        help="Metadata text for box (supports \\n for newlines)"
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="Output PNG path or directory"
    )
    parser.add_argument(
        "--dpi",
        type=int,
        default=300,
        help="DPI for PNG (default: 300)"
    )
    parser.add_argument(
        "--width",
        type=float,
        default=14,
        help="Figure width in inches (default: 14)"
    )
    parser.add_argument(
        "--height",
        type=float,
        default=8,
        help="Figure height in inches (default: 8)"
    )

    args = parser.parse_args()

    # Handle output path
    output_png = args.output
    if output_png:
        # If output is a directory (or will be), use it as output dir
        if str(output_png).endswith('/') or (output_png.exists() and output_png.is_dir()):
            output_png = output_png / f"{args.in_file.stem}_{args.dpi}dpi.png"
        elif not output_png.suffix:  # No file extension, treat as directory
            output_png = output_png / f"{args.in_file.stem}_{args.dpi}dpi.png"

    # Process escape sequences in title and metadata
    title = args.title.replace('\\n', '\n') if args.title else None
    metadata = args.metadata.replace('\\n', '\n') if args.metadata else None

    render_scene(
        in_file=args.in_file,
        output_png=output_png,
        title=title,
        metadata=metadata,
        dpi=args.dpi,
        figsize=(args.width, args.height),
        verbose=True,
    )

    print()
    print("=" * 70)
    print("✅ RENDERING COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    main()
