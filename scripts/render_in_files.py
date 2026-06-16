#!/usr/bin/env python3
"""
Batch render gprMax .in files to PNG geometry visualizations.
Converts one or more .in files to PNG using gprMax rendering.
"""

import sys
from pathlib import Path
import argparse

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.visualization.render import render_geometry_png


def render_in_file(in_path: Path, output_png: Path = None, dpi: int = 150) -> Path:
    """Render a single .in file to PNG."""
    in_path = Path(in_path)

    if not in_path.exists():
        raise FileNotFoundError(f"Input file not found: {in_path}")

    if output_png is None:
        output_png = in_path.with_suffix('.png')
    else:
        output_png = Path(output_png)

    print(f"[RENDER] {in_path.name} -> {output_png.name}...", end=" ", flush=True)

    try:
        png_path = render_geometry_png(in_path, output_png, dpi=dpi)
        print(f"[OK] {png_path.stat().st_size / 1024:.1f} KB")
        return png_path
    except Exception as e:
        print(f"[FAIL] {str(e)[:100]}")
        return None


def main():
    ap = argparse.ArgumentParser(
        description="Batch render gprMax .in files to PNG geometry visualizations",
        epilog="""
Examples:
  # Single file
  python scripts/render_in_files.py output_test/test.in

  # Multiple files
  python scripts/render_in_files.py output_test/*.in

  # With custom output directory
  python scripts/render_in_files.py output_test/antenna_heights/*.in -o output_test/geometry/

  # Custom DPI
  python scripts/render_in_files.py output_test/test.in --dpi 200
        """,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    ap.add_argument(
        "input",
        type=str,
        help="Input .in file(s) to render (glob pattern supported)",
    )
    ap.add_argument(
        "-o", "--output",
        type=Path,
        default=None,
        help="Output directory or file path (auto-detected based on input)",
    )
    ap.add_argument(
        "--dpi",
        type=int,
        default=150,
        help="DPI for rendered PNG (default: 150)",
    )

    args = ap.parse_args()

    # Find input files (support glob patterns)
    input_pattern = Path(args.input)
    if "*" in str(input_pattern):
        # Glob pattern
        parent = Path(input_pattern.parts[0])
        pattern = str(input_pattern.relative_to(parent)) if len(input_pattern.parts) > 1 else str(input_pattern)

        in_files = list(parent.glob(pattern))
        if not in_files:
            print(f"[ERR] No files match pattern: {args.input}")
            return 1
    else:
        # Single file
        in_path = Path(args.input)
        in_files = [in_path] if in_path.exists() else []

        if not in_files:
            print(f"[ERR] Input file not found: {args.input}")
            return 1

    in_files = sorted(in_files)

    print(f"\n{'='*70}")
    print(f"BATCH RENDER .IN FILES TO PNG")
    print(f"{'='*70}")
    print(f"Found {len(in_files)} .in file(s)\n")

    rendered = []
    failed = []

    for in_path in in_files:
        # Determine output path
        if args.output:
            out_path = Path(args.output)
            if out_path.is_dir() or str(out_path).endswith('/'):
                # Output is a directory
                out_dir = out_path
                out_dir.mkdir(parents=True, exist_ok=True)
                output_png = out_dir / in_path.with_suffix('.png').name
            else:
                # Output is a file path
                output_png = out_path
        else:
            # Same directory as input
            output_png = in_path.with_suffix('.png')

        try:
            result = render_in_file(in_path, output_png, dpi=args.dpi)
            if result:
                rendered.append(result)
            else:
                failed.append(in_path)
        except Exception as e:
            print(f"[ERROR] {in_path.name}: {str(e)[:100]}")
            failed.append(in_path)

    # Summary
    print(f"\n{'='*70}")
    print(f"RENDER SUMMARY")
    print(f"{'='*70}")
    print(f"Successfully rendered: {len(rendered)} file(s)")
    print(f"Failed: {len(failed)} file(s)")

    if rendered:
        print(f"\nOutput files:")
        for png in rendered:
            print(f"  {png}")

    if failed:
        print(f"\nFailed files:")
        for f in failed:
            print(f"  {f}")

    print(f"{'='*70}\n")

    return 0 if not failed else 1


if __name__ == "__main__":
    sys.exit(main())
