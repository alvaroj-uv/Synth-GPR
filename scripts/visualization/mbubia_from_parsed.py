#!/usr/bin/env python3
"""
Mbubia Scene Visualizer (from parsed .in files)
Reuses existing visualization infrastructure
Fully parameterized - no hardcoding
"""

import argparse
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.visualization.scene import parse_in_file, draw_geometry
from src.visualization.publication_figures import PublicationFigureGenerator
import matplotlib.pyplot as plt


def visualize_mbubia_scene(
    in_file: Path,
    fouling_label: str = "fouled",
    frequency_ghz: float = 1.4,
    output_dir: Path = None,
    dpi: int = 300,
    verbose: bool = True,
) -> Path:
    """
    Visualize a Mbubia-style scene from .in file
    Reuses existing draw_geometry infrastructure
    """

    if not in_file.exists():
        print(f"❌ File not found: {in_file}")
        sys.exit(1)

    if output_dir is None:
        output_dir = in_file.parent

    output_dir.mkdir(parents=True, exist_ok=True)

    if verbose:
        print(f"\nVisualizing: {in_file.name}")

    # Parse the scene
    scene = parse_in_file(in_file)

    # Fix monostatic antenna: RX at same X as TX
    if scene.tx and scene.receivers:
        for rx in scene.receivers:
            rx.x = scene.tx.x

    if verbose:
        print(f"  ✓ Parsed: {scene.domain_x:.1f}m × {scene.domain_y:.1f}m")
        print(f"  ✓ Antenna: TX @ {scene.tx.x:.3f}m, RX @ {rx.x:.3f}m (offset=0.000m)")

    # Create visualization
    fig, ax = plt.subplots(figsize=(14, 8), dpi=dpi)

    # Draw using existing infrastructure
    draw_geometry(ax, scene)

    # Mbubia branding
    fouling_titles = {
        "clean": "Clean Ballast (Rb-f < 2%)",
        "fouled": "Fouled Ballast (Rb-f 2-18%)",
        "highly_fouled": "Highly Fouled Ballast (Rb-f ≥ 55%)",
    }

    title = f"Mbubia-Style Scene - {fouling_titles.get(fouling_label, fouling_label)}\n"
    title += f"{frequency_ghz:.1f} GHz, Monostatic Antenna (Real Railway Standard)"
    ax.set_title(title, fontsize=14, fontweight='bold', pad=20)

    # Metadata
    metadata = (
        f"Reference: Mbubia et al. 2026\n"
        f"Frequency: {frequency_ghz:.1f} GHz\n"
        f"Antenna: Monostatic (TX/RX co-located)\n"
        f"Domain: {scene.domain_x:.1f}m × {scene.domain_y:.2f}m\n"
        f"\n"
        f"Fouling Class: {fouling_label.upper()}\n"
        f"Ballast Fouling Index (Rb-f):\n"
        f"  Clean: < 2%\n"
        f"  Fouled: 2-18%\n"
        f"  Highly fouled: ≥ 55%"
    )

    ax.text(0.98, 0.02, metadata,
            transform=ax.transAxes, fontsize=9, verticalalignment='bottom',
            horizontalalignment='right', family='monospace',
            bbox=dict(boxstyle='round', facecolor='#E8F4FF', alpha=0.95,
                      edgecolor='#1060D0', linewidth=2))

    plt.tight_layout()

    # Save
    stem = in_file.stem
    png_path = output_dir / f"{stem}_{dpi}dpi.png"
    fig.savefig(png_path, dpi=dpi, bbox_inches='tight', facecolor='white')
    plt.close(fig)

    if verbose:
        size_kb = png_path.stat().st_size / 1024
        print(f"  ✓ Saved: {png_path.name} ({size_kb:.1f} KB, {dpi} DPI)")

    return png_path


def main():
    parser = argparse.ArgumentParser(
        description="Visualize Mbubia-style scenes from .in files"
    )

    parser.add_argument(
        "in_files",
        nargs="+",
        type=Path,
        help=".in file(s) to visualize"
    )
    parser.add_argument(
        "--fouling",
        choices=["clean", "fouled", "highly_fouled"],
        default="fouled",
        help="Fouling label for metadata (default: fouled)"
    )
    parser.add_argument(
        "--frequency",
        type=float,
        default=1.4,
        help="Frequency in GHz (default: 1.4)"
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="Output directory (default: same as input)"
    )
    parser.add_argument(
        "--dpi",
        type=int,
        default=300,
        help="DPI for PNG (default: 300)"
    )

    args = parser.parse_args()

    print("="*80)
    print("VISUALIZING MBUBIA-STYLE SCENES")
    print("="*80)

    for in_file in args.in_files:
        # Infer fouling level from filename
        filename = in_file.stem.lower()
        if "clean" in filename:
            fouling = "clean"
        elif "highly" in filename or "highly_fouled" in filename:
            fouling = "highly_fouled"
        else:
            fouling = args.fouling

        visualize_mbubia_scene(
            in_file=in_file,
            fouling_label=fouling,
            frequency_ghz=args.frequency,
            output_dir=args.output,
            dpi=args.dpi,
            verbose=True,
        )

    print("\n" + "="*80)
    print("✅ VISUALIZATION COMPLETE")
    print("="*80)


if __name__ == "__main__":
    main()
