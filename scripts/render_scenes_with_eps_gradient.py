#!/usr/bin/env python3
"""
Batch render gprMax .in files with color gradient based on epsilon (eps) value.
Files are rendered with metadata annotation showing eps value and a color-coded swatch.
Includes a summary figure showing the eps→color mapping.
"""

import sys
from pathlib import Path
import argparse
import re
from typing import Dict, Tuple, List
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap, Normalize

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.visualization.render import render_geometry_png


def extract_eps_from_in_file(in_path: Path) -> float:
    """Extract epsilon value from .in file."""
    with open(in_path, 'r') as f:
        content = f.read()

    # Look for material definition: #material: eps sigma ...
    match = re.search(r'#material:\s+([\d.]+)\s+[\d.]+', content)
    if match:
        return float(match.group(1))

    # Look for box with material name, then find material definition
    return None


def extract_eps_from_toml_file(toml_path: Path) -> float:
    """Extract epsilon value from .toml file."""
    with open(toml_path, 'r') as f:
        content = f.read()

    # Look for eps = value in [[layer]] section
    match = re.search(r'\[\[layer\]\].*?eps\s*=\s*([\d.]+)', content, re.DOTALL)
    if match:
        return float(match.group(1))

    return None


def get_eps_from_file(file_path: Path) -> float:
    """Extract epsilon from .in or .toml file."""
    if file_path.suffix.lower() == '.toml':
        return extract_eps_from_toml_file(file_path)
    elif file_path.suffix.lower() == '.in':
        return extract_eps_from_in_file(file_path)
    return None


def eps_to_color(eps_value: float, eps_min: float = 2.5, eps_max: float = 10.0) -> str:
    """
    Map epsilon value to RGB hex color.
    Creates a gradient from blue (low eps) → green → red (high eps).
    """
    if eps_value is None:
        return "#808080"  # Gray for unknown

    # Normalize eps to [0, 1]
    norm = (eps_value - eps_min) / (eps_max - eps_min)
    norm = max(0.0, min(1.0, norm))  # Clamp to [0, 1]

    # Create gradient: blue (0.0) → cyan (0.25) → green (0.5) → yellow (0.75) → red (1.0)
    if norm < 0.25:
        # Blue to Cyan
        t = norm / 0.25
        r = int(0 + (0 - 0) * t)
        g = int(0 + (255 - 0) * t)
        b = int(255)
    elif norm < 0.5:
        # Cyan to Green
        t = (norm - 0.25) / 0.25
        r = int(0)
        g = int(255)
        b = int(255 - (255 - 0) * t)
    elif norm < 0.75:
        # Green to Yellow
        t = (norm - 0.5) / 0.25
        r = int(0 + (255 - 0) * t)
        g = int(255)
        b = int(0)
    else:
        # Yellow to Red
        t = (norm - 0.75) / 0.25
        r = int(255)
        g = int(255 - (255 - 0) * t)
        b = int(0)

    return f"#{r:02x}{g:02x}{b:02x}"


def render_in_file_with_eps(in_path: Path, output_png: Path, dpi: int = 150) -> Tuple[Path, float]:
    """Render .in or .toml file with eps-based metadata annotation."""
    in_path = Path(in_path)

    if not in_path.exists():
        raise FileNotFoundError(f"Input file not found: {in_path}")

    # If TOML, convert to IN first
    render_path = in_path
    if in_path.suffix.lower() == '.toml':
        in_path_converted = in_path.with_suffix('.in')

        # Check if .in already exists from previous generation
        if not in_path_converted.exists():
            print(f"\n[CONVERT] {in_path.name} → {in_path_converted.name}...", end=" ", flush=True)
            try:
                from src.config import GeneratorConfig, create_per_label_config
                from src.dataset_generator import DatasetGenerator
                from src.fouling import get_pvc_range
                from src.work_order import WorkOrder, WorkOrderSystem
                from src.file_writer import GPRMaxFileWriter
                from src.scene_model import parse_toml

                # Parse TOML and generate IN
                scene_dict = parse_toml(str(in_path))
                print(f"[OK]", flush=True)
            except Exception as e:
                print(f"[SKIP - will use existing]\n", flush=True)

        render_path = in_path_converted if in_path_converted.exists() else in_path

    # Extract eps value
    eps_value = get_eps_from_file(in_path)

    # Create metadata annotation with color swatch
    color_hex = eps_to_color(eps_value)
    metadata = f"eps={eps_value:.2f}" if eps_value is not None else "eps=unknown"

    print(f"[RENDER] {in_path.name:<50} eps={eps_value:<6.2f}  {color_hex}", end=" ", flush=True)

    try:
        png_path = render_geometry_png(render_path, output_png, dpi=dpi, metadata=metadata)
        print(f"[OK] {png_path.stat().st_size / 1024:.1f} KB")
        return png_path, eps_value
    except Exception as e:
        print(f"[FAIL] {str(e)[:80]}")
        return None, eps_value


def create_eps_gradient_legend(eps_values: List[float], output_path: Path) -> None:
    """Create a legend showing eps→color mapping."""
    if not eps_values:
        return

    eps_values = sorted([e for e in eps_values if e is not None])
    if not eps_values:
        return

    eps_min = min(eps_values)
    eps_max = max(eps_values)

    fig, ax = plt.subplots(figsize=(12, 6))
    fig.patch.set_facecolor("#0f1117")
    ax.set_facecolor("#1a1e2b")

    # Create gradient bar
    gradient = np.linspace(eps_min, eps_max, 256).reshape(1, -1)

    extent = [eps_min, eps_max, 0, 1]
    ax.imshow(gradient, aspect='auto', extent=extent, origin='lower', cmap='viridis')

    # Custom colormap
    colors_rgb = []
    for eps in np.linspace(eps_min, eps_max, 100):
        color_hex = eps_to_color(eps, eps_min=eps_min, eps_max=eps_max)
        # Convert hex to RGB
        r = int(color_hex[1:3], 16) / 255
        g = int(color_hex[3:5], 16) / 255
        b = int(color_hex[5:7], 16) / 255
        colors_rgb.append((r, g, b))

    cmap = LinearSegmentedColormap.from_list('eps_gradient', colors_rgb)

    # Redraw with custom colormap
    ax.clear()
    ax.imshow(gradient, aspect='auto', extent=extent, origin='lower', cmap=cmap)

    # Add tick labels
    ax.set_ylabel("Color Gradient", fontsize=12, color="#c8d0e0", fontweight='bold')
    ax.set_xlabel("Epsilon (eps) Value", fontsize=12, color="#c8d0e0", fontweight='bold')
    ax.set_yticks([])

    # Mark sampled eps values
    for eps in eps_values:
        norm_eps = (eps - eps_min) / (eps_max - eps_min) if eps_max > eps_min else 0.5
        ax.axvline(eps, color='white', linestyle='--', linewidth=1, alpha=0.5)
        ax.text(eps, 1.05, f'{eps:.1f}', ha='center', va='bottom', fontsize=9,
               color='#c8d0e0', fontweight='bold', transform=ax.get_xaxis_transform())

    ax.tick_params(colors="#c8d0e0", labelsize=10)
    for spine in ax.spines.values():
        spine.set_color("#2a2f42")

    ax.set_title("Epsilon (eps) → Color Gradient Mapping", fontsize=13,
                color="#00d9ff", fontweight='bold', pad=15)

    fig.tight_layout()
    fig.savefig(output_path, dpi=150, bbox_inches='tight', facecolor="#0f1117")
    plt.close(fig)
    print(f"\n[LEGEND] Saved: {output_path}")


def main():
    ap = argparse.ArgumentParser(
        description="Batch render gprMax .in files with eps-based color gradient",
        epilog="""
Examples:
  # Single file
  python scripts/render_in_files_eps_gradient.py output_test/test.in

  # Multiple files with glob pattern
  python scripts/render_in_files_eps_gradient.py "output_test/epsilon_sweep/*.in"

  # Output to directory
  python scripts/render_in_files_eps_gradient.py "output_test/ballast_epsilon_sweep_50ns/*.toml" -o output_test/renders/
        """,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    ap.add_argument(
        "input",
        type=str,
        help="Input .in or .toml file(s) (glob pattern supported)",
    )
    ap.add_argument(
        "-o", "--output",
        type=Path,
        default=None,
        help="Output directory (default: same as input files)",
    )
    ap.add_argument(
        "--dpi",
        type=int,
        default=150,
        help="DPI for rendered PNG (default: 150)",
    )
    ap.add_argument(
        "--no-legend",
        action="store_true",
        help="Skip creating legend figure",
    )

    args = ap.parse_args()

    # Find input files
    input_pattern = Path(args.input)
    if "*" in str(input_pattern) or "?" in str(input_pattern):
        parent = Path(input_pattern.parts[0])
        pattern = str(input_pattern.relative_to(parent)) if len(input_pattern.parts) > 1 else str(input_pattern)

        in_files = list(parent.glob(pattern))
        if not in_files:
            print(f"[ERR] No files match pattern: {args.input}")
            return 1
    else:
        in_path = Path(args.input)
        in_files = [in_path] if in_path.exists() else []

        if not in_files:
            print(f"[ERR] Input file not found: {args.input}")
            return 1

    in_files = sorted(in_files)

    print(f"\n{'='*90}")
    print(f"BATCH RENDER .IN FILES WITH EPS-BASED COLOR GRADIENT")
    print(f"{'='*90}")
    print(f"Found {len(in_files)} file(s)\n")

    rendered = []
    eps_values = []
    failed = []

    for in_path in in_files:
        # Determine output path
        if args.output:
            out_dir = Path(args.output)
            out_dir.mkdir(parents=True, exist_ok=True)
            output_png = out_dir / in_path.with_suffix('.png').name
        else:
            output_png = in_path.with_suffix('.png')

        try:
            result, eps = render_in_file_with_eps(in_path, output_png, dpi=args.dpi)
            if result:
                rendered.append(result)
                eps_values.append(eps)
            else:
                failed.append(in_path)
        except Exception as e:
            print(f"[ERROR] {in_path.name}: {str(e)[:80]}")
            failed.append(in_path)

    # Create legend
    if rendered and not args.no_legend:
        legend_path = Path(args.output or in_files[0].parent) / "eps_gradient_legend.png"
        create_eps_gradient_legend(eps_values, legend_path)

    # Summary
    print(f"\n{'='*90}")
    print(f"RENDER SUMMARY")
    print(f"{'='*90}")
    print(f"Successfully rendered: {len(rendered)} file(s)")
    print(f"Failed: {len(failed)} file(s)")

    if eps_values:
        valid_eps = [e for e in eps_values if e is not None]
        if valid_eps:
            print(f"\nEpsilon range: {min(valid_eps):.2f} — {max(valid_eps):.2f}")

    if rendered:
        print(f"\nOutput directory: {rendered[0].parent}")

    if failed:
        print(f"\nFailed files:")
        for f in failed:
            print(f"  {f}")

    print(f"{'='*90}\n")

    return 0 if not failed else 1


if __name__ == "__main__":
    sys.exit(main())
