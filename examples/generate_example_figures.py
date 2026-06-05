#!/usr/bin/env python3
"""
Generate example publication figures from actual .in files
"""

from pathlib import Path
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.visualization.publication_figures import (
    PublicationFigureGenerator,
    apply_publication_style,
    export_scene_as_pdf,
)
from src.visualization.scene import parse_in_file

def main():
    print("\n" + "="*80)
    print("GENERATING EXAMPLE PUBLICATION FIGURES")
    print("="*80 + "\n")

    # Create output directory
    output_dir = Path("example_figures")
    output_dir.mkdir(exist_ok=True)
    print(f"📁 Output directory: {output_dir.absolute()}\n")

    # Apply professional style
    apply_publication_style()
    print("✓ Applied professional matplotlib style\n")

    # Find sample .in files
    sample_files = list(Path("test_output").glob("*.in"))[:3]

    if not sample_files:
        print("❌ No .in files found in test_output/")
        return

    print(f"📄 Found {len(sample_files)} sample files:\n")

    # Generate figures for each sample
    for idx, in_file in enumerate(sample_files, 1):
        print(f"\n{idx}. Processing: {in_file.name}")
        print("   " + "─" * 76)

        try:
            # Parse the scene
            scene = parse_in_file(in_file)
            print(f"   ✓ Parsed scene")
            print(f"     • Domain: {scene.domain_x:.3f}m × {scene.domain_y:.3f}m")
            print(f"     • Rocks (triangles): {len(scene.triangles)}")
            print(f"     • Boxes: {len(scene.boxes)}")
            if scene.tx:
                print(f"     • TX position: ({scene.tx.x:.3f}, {scene.tx.y:.3f})")
            if scene.receivers:
                print(f"     • RX count: {len(scene.receivers)}")
            print(f"     • Metadata keys: {list(scene.meta.keys())}")

            # EXAMPLE 1: High-quality PNG (300 DPI - for printing)
            png_path = output_dir / f"{in_file.stem}_publication_300dpi.png"
            result = PublicationFigureGenerator.save_scene_cross_section(
                scene,
                output_path=png_path,
                title=f"Scene: {in_file.stem}\n(Publication Quality - 300 DPI)",
                dpi=300
            )
            print(f"   ✓ PNG (300 DPI): {png_path.name}")
            print(f"     • Size: {result.stat().st_size / 1024:.1f} KB")

            # EXAMPLE 2: Screen quality PNG (150 DPI)
            png_screen_path = output_dir / f"{in_file.stem}_screen_150dpi.png"
            result = PublicationFigureGenerator.save_scene_cross_section(
                scene,
                output_path=png_screen_path,
                title=f"Scene: {in_file.stem}\n(Screen Quality - 150 DPI)",
                dpi=150
            )
            print(f"   ✓ PNG (150 DPI): {png_screen_path.name}")
            print(f"     • Size: {result.stat().st_size / 1024:.1f} KB")

            # EXAMPLE 3: PDF (Vector - for documents)
            pdf_path = output_dir / f"{in_file.stem}_publication.pdf"
            result = export_scene_as_pdf(in_file, pdf_path)
            print(f"   ✓ PDF (Vector): {pdf_path.name}")
            print(f"     • Size: {result.stat().st_size / 1024:.1f} KB")
            print(f"     • ℹ️  Editable in Adobe Illustrator")

        except Exception as e:
            print(f"   ❌ Error: {e}")
            import traceback
            traceback.print_exc()

    # EXAMPLE 4: Comparison figure (side-by-side)
    if len(sample_files) >= 2:
        print(f"\n\n4. Creating COMPARISON FIGURE (side-by-side)")
        print("   " + "─" * 76)

        try:
            comparison_path = output_dir / "comparison_all_scenes.png"
            results = PublicationFigureGenerator.save_comparison_figures(
                sample_files,
                output_dir=output_dir.parent / "comparisons",
                dpi=300
            )
            print(f"   ✓ Comparison figure created: {results[0].name}")
            print(f"     • Size: {results[0].stat().st_size / 1024:.1f} KB")
            print(f"     • Shows {len(sample_files)} scenes side-by-side")
        except Exception as e:
            print(f"   ❌ Error: {e}")

    # Summary
    print("\n\n" + "="*80)
    print("SUMMARY")
    print("="*80)

    total_files = len(list(output_dir.glob("*")))
    total_size = sum(f.stat().st_size for f in output_dir.glob("*")) / (1024 * 1024)

    print(f"\n✅ Generated {total_files} example figures")
    print(f"📊 Total size: {total_size:.2f} MB")
    print(f"📁 Location: {output_dir.absolute()}\n")

    print("What's included:")
    print("  • PNG at 300 DPI (for printing/journals)")
    print("  • PNG at 150 DPI (for presentations/web)")
    print("  • PDF (vector format, editable)")
    print("  • Comparison figure (side-by-side scenes)")
    print("  • All with professional styling and metadata\n")

    print("Next steps:")
    print("  1. Open the output_dir folder to view the figures")
    print("  2. Try opening PDF in Adobe Illustrator")
    print("  3. Use PNG figures in your presentations")
    print("  4. Customize titles and sizes as needed\n")

if __name__ == "__main__":
    main()
