#!/usr/bin/env python3
"""
Publication-Quality Figure Export Demo

This example shows how to generate professional, print-ready figures
suitable for journals, conferences, and presentations.
"""

from pathlib import Path
from src.visualization.publication_figures import (
    PublicationFigureGenerator,
    apply_publication_style,
    export_scene_as_pdf,
    export_scene_as_svg,
)
from src.visualization.scene import parse_in_file


def demo_basic_export():
    """Demo 1: Export a single scene as PNG (default)"""
    print("\n" + "="*70)
    print("DEMO 1: Basic High-Quality PNG Export")
    print("="*70)

    in_path = Path("sample_data/sample_scene.in")
    if not in_path.exists():
        print(f"❌ Sample file not found: {in_path}")
        print("   Please provide a valid .in file")
        return

    output_dir = Path("output/publication_figures")
    output_dir.mkdir(parents=True, exist_ok=True)

    # Parse the scene
    scene = parse_in_file(in_path)
    print(f"✓ Parsed scene: {in_path.stem}")
    print(f"  Domain: {scene.domain_x:.3f}m × {scene.domain_y:.3f}m")
    print(f"  Rocks: {len(scene.triangles)}")
    print(f"  Metadata: {dict(scene.meta)}")

    # Save as high-quality PNG
    output_path = output_dir / f"{in_path.stem}_publication.png"
    result = PublicationFigureGenerator.save_scene_cross_section(
        scene,
        output_path,
        title=f"Scene: {in_path.stem}",
        dpi=300,  # 300 DPI for printing
    )

    print(f"✓ Saved publication PNG: {result}")
    print(f"  Size: {result.stat().st_size / 1024:.1f} KB")
    return result


def demo_vector_export():
    """Demo 2: Export as PDF and SVG (vector formats)"""
    print("\n" + "="*70)
    print("DEMO 2: Vector Format Export (PDF & SVG)")
    print("="*70)

    in_path = Path("sample_data/sample_scene.in")
    if not in_path.exists():
        print(f"❌ Sample file not found: {in_path}")
        return

    output_dir = Path("output/publication_figures")
    output_dir.mkdir(parents=True, exist_ok=True)

    # Export as PDF (ideal for documents)
    pdf_path = export_scene_as_pdf(in_path, output_dir / f"{in_path.stem}.pdf")
    print(f"✓ PDF export: {pdf_path}")
    print(f"  Size: {pdf_path.stat().st_size / 1024:.1f} KB")
    print(f"  ℹ️  PDF is scalable, editable in Adobe Illustrator")

    # Export as SVG (editable in vector editors)
    svg_path = export_scene_as_svg(in_path, output_dir / f"{in_path.stem}.svg")
    print(f"✓ SVG export: {svg_path}")
    print(f"  Size: {svg_path.stat().st_size / 1024:.1f} KB")
    print(f"  ℹ️  SVG is editable in Inkscape, Illustrator, etc.")

    return pdf_path, svg_path


def demo_comparison_figures():
    """Demo 3: Create comparison figures (side-by-side)"""
    print("\n" + "="*70)
    print("DEMO 3: Comparison Figures (Multiple Scenes)")
    print("="*70)

    # Find sample files (if available)
    sample_dir = Path("sample_data")
    if not sample_dir.exists():
        print(f"❌ Sample directory not found: {sample_dir}")
        print("   To create comparisons, provide multiple .in files")
        return

    in_files = list(sample_dir.glob("*.in"))[:3]  # Use up to 3 files

    if not in_files:
        print("❌ No .in files found in sample_data/")
        return

    print(f"Found {len(in_files)} sample files")

    output_dir = Path("output/publication_figures")
    output_dir.mkdir(parents=True, exist_ok=True)

    results = PublicationFigureGenerator.save_comparison_figures(
        in_files,
        output_dir / "comparisons",
        dpi=300,
    )

    print(f"✓ Generated {len(results)} comparison figure(s)")
    for result in results:
        print(f"  → {result}")


def demo_grid_layout():
    """Demo 4: Create grid layout of multiple scenes"""
    print("\n" + "="*70)
    print("DEMO 4: Grid Layout (Dataset Overview)")
    print("="*70)

    sample_dir = Path("sample_data")
    in_files = list(sample_dir.glob("*.in"))[:6]  # Use up to 6 files

    if len(in_files) < 2:
        print("⚠️  Need at least 2 sample files for grid demo")
        return

    print(f"Creating grid layout with {len(in_files)} scenes...")

    output_dir = Path("output/publication_figures")
    output_dir.mkdir(parents=True, exist_ok=True)

    result = PublicationFigureGenerator.save_grid_layout(
        in_files,
        output_dir / "grid_layout_3x2.png",
        ncols=3,
        dpi=300,
    )

    print(f"✓ Grid layout saved: {result}")
    print(f"  Size: {result.stat().st_size / 1024:.1f} KB")


def demo_publication_style():
    """Demo 5: Apply professional style settings"""
    print("\n" + "="*70)
    print("DEMO 5: Professional Style Settings")
    print("="*70)

    apply_publication_style()
    print("✓ Applied publication-quality matplotlib style")
    print("  Features:")
    print("  - Professional fonts (Helvetica/Arial)")
    print("  - Optimal font sizes for readability")
    print("  - High-quality line styles")
    print("  - Proper spacing and proportions")
    print("")
    print("  These settings are automatically applied when you:")
    print("  - Call PublicationFigureGenerator methods")
    print("  - Use export_scene_as_pdf/svg functions")


def main():
    """Run all demos"""
    print("\n" + "█" * 70)
    print("█  PUBLICATION-QUALITY FIGURE EXPORT - DEMO")
    print("█" * 70)

    try:
        demo_publication_style()
        demo_basic_export()
        demo_vector_export()
        demo_comparison_figures()
        demo_grid_layout()

        print("\n" + "="*70)
        print("✓ ALL DEMOS COMPLETED SUCCESSFULLY!")
        print("="*70)
        print("\nGenerated figures in: output/publication_figures/")
        print("\nNext steps:")
        print("  1. Review the generated figures")
        print("  2. Open PDF/SVG in your preferred editor")
        print("  3. Use PNG versions for presentations/web")
        print("  4. Customize titles, sizes, and styles as needed")
        print("")

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
