#!/usr/bin/env python3
"""
Convert TOML→IN, then batch render with eps-based color gradient.
"""

import sys
from pathlib import Path
import argparse
import subprocess
import re
from typing import List
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.visualization.render import render_geometry_png


def extract_eps_from_toml_file(toml_path: Path) -> float:
    """Extract epsilon value from .toml file."""
    with open(toml_path, 'r') as f:
        content = f.read()

    match = re.search(r'\[\[layer\]\].*?eps\s*=\s*([\d.]+)', content, re.DOTALL)
    if match:
        return float(match.group(1))
    return None


def convert_toml_to_in(toml_path: Path, out_dir: Path = None) -> Path:
    """Convert TOML to IN using generate_in_files.py."""
    toml_path = Path(toml_path)

    if out_dir is None:
        out_dir = toml_path.parent

    out_dir.mkdir(parents=True, exist_ok=True)
    in_path = out_dir / toml_path.with_suffix('.in').name

    print(f"  [GEN]  {toml_path.name:<45} -> {in_path.name}...", end=" ", flush=True)

    try:
        result = subprocess.run(
            [
                sys.executable,
                "scripts/pipeline/generate_in_files.py",
                str(toml_path),
                "-o", str(in_path)
            ],
            capture_output=True,
            text=True,
            timeout=30
        )

        if result.returncode == 0 and in_path.exists():
            print(f"[OK]")
            return in_path
        else:
            print(f"[FAIL]")
            if result.stderr:
                print(f"      Error: {result.stderr[:100]}")
            return None
    except Exception as e:
        print(f"[ERROR] {str(e)[:80]}")
        return None


def eps_to_color(eps_value: float, eps_min: float = 2.5, eps_max: float = 10.0) -> str:
    """Map epsilon to color (blue → green → red)."""
    if eps_value is None:
        return "#808080"

    norm = (eps_value - eps_min) / (eps_max - eps_min)
    norm = max(0.0, min(1.0, norm))

    if norm < 0.25:
        t = norm / 0.25
        r, g, b = int(0), int(0 + 255 * t), 255
    elif norm < 0.5:
        t = (norm - 0.25) / 0.25
        r, g, b = int(0), 255, int(255 - 255 * t)
    elif norm < 0.75:
        t = (norm - 0.5) / 0.25
        r, g, b = int(0 + 255 * t), 255, 0
    else:
        t = (norm - 0.75) / 0.25
        r, g, b = 255, int(255 - 255 * t), 0

    return f"#{r:02x}{g:02x}{b:02x}"


def render_in_with_eps(in_path: Path, output_png: Path, eps_value: float, dpi: int = 150) -> Path:
    """Render IN file with eps metadata."""
    color_hex = eps_to_color(eps_value)
    metadata = f"eps={eps_value:.2f}" if eps_value is not None else "eps=unknown"

    print(f"  [RENDER] {in_path.name:<43} eps={eps_value:<6.2f}  {color_hex}", end=" ", flush=True)

    try:
        png_path = render_geometry_png(in_path, output_png, dpi=dpi, metadata=metadata)
        size_kb = png_path.stat().st_size / 1024
        print(f"[OK] {size_kb:.1f} KB")
        return png_path
    except Exception as e:
        print(f"[FAIL] {str(e)[:60]}")
        return None


def create_eps_gradient_legend(eps_values: List[float], output_path: Path) -> None:
    """Create legend showing eps→color mapping."""
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

    gradient = np.linspace(eps_min, eps_max, 256).reshape(1, -1)

    colors_rgb = []
    for eps in np.linspace(eps_min, eps_max, 100):
        color_hex = eps_to_color(eps, eps_min=eps_min, eps_max=eps_max)
        r = int(color_hex[1:3], 16) / 255
        g = int(color_hex[3:5], 16) / 255
        b = int(color_hex[5:7], 16) / 255
        colors_rgb.append((r, g, b))

    cmap = LinearSegmentedColormap.from_list('eps_gradient', colors_rgb)
    extent = [eps_min, eps_max, 0, 1]
    ax.imshow(gradient, aspect='auto', extent=extent, origin='lower', cmap=cmap)

    for eps in eps_values:
        norm_eps = (eps - eps_min) / (eps_max - eps_min) if eps_max > eps_min else 0.5
        ax.axvline(eps, color='white', linestyle='--', linewidth=1, alpha=0.5)
        ax.text(eps, 1.05, f'{eps:.1f}', ha='center', va='bottom', fontsize=9,
               color='#c8d0e0', fontweight='bold', transform=ax.get_xaxis_transform())

    ax.set_ylabel("Color Gradient", fontsize=12, color="#c8d0e0", fontweight='bold')
    ax.set_xlabel("Epsilon (eps) Value", fontsize=12, color="#c8d0e0", fontweight='bold')
    ax.set_yticks([])
    ax.tick_params(colors="#c8d0e0", labelsize=10)

    for spine in ax.spines.values():
        spine.set_color("#2a2f42")

    ax.set_title("Epsilon (eps) → Color Gradient Mapping", fontsize=13,
                color="#00d9ff", fontweight='bold', pad=15)

    fig.tight_layout()
    fig.savefig(output_path, dpi=150, bbox_inches='tight', facecolor="#0f1117")
    plt.close(fig)
    print(f"  [LEGEND] {output_path.name}")


def main():
    ap = argparse.ArgumentParser(
        description="Convert TOML→IN, then render with eps-based color gradient",
        epilog="""
Examples:
  # Epsilon sweep
  python scripts/render_toml_with_eps_gradient.py "output_test/ballast_epsilon_sweep_50ns/*.toml" -o renders/

  # Single file
  python scripts/render_toml_with_eps_gradient.py output_test/ballast_eps51_antenna_30cm.toml
        """,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    ap.add_argument("input", type=str, help="Input .toml file(s) (glob pattern supported)")
    ap.add_argument("-o", "--output", type=Path, default=None, help="Output directory")
    ap.add_argument("--dpi", type=int, default=120, help="DPI for PNG")
    ap.add_argument("--no-legend", action="store_true", help="Skip legend figure")
    ap.add_argument("--no-convert", action="store_true", help="Skip TOML→IN conversion (use existing .in files)")

    args = ap.parse_args()

    # Find TOML files
    input_pattern = Path(args.input)
    if "*" in str(input_pattern) or "?" in str(input_pattern):
        parent = Path(input_pattern.parts[0])
        pattern = str(input_pattern.relative_to(parent)) if len(input_pattern.parts) > 1 else str(input_pattern)
        toml_files = list(parent.glob(pattern))
        if not toml_files:
            print(f"[ERR] No files match: {args.input}")
            return 1
    else:
        toml_path = Path(args.input)
        toml_files = [toml_path] if toml_path.exists() else []
        if not toml_files:
            print(f"[ERR] File not found: {args.input}")
            return 1

    toml_files = sorted(toml_files)
    out_dir = Path(args.output) if args.output else toml_files[0].parent

    print(f"\n{'='*90}")
    print(f"TOML -> IN -> RENDER WITH EPS-BASED COLOR GRADIENT")
    print(f"{'='*90}")
    print(f"Found {len(toml_files)} TOML file(s)\n")

    # Phase 1: Convert TOML -> IN
    if not args.no_convert:
        print(f"{'='*90}")
        print(f"PHASE 1: CONVERT TOML -> IN")
        print(f"{'='*90}\n")

        in_files = []
        for toml_path in toml_files:
            in_path = convert_toml_to_in(toml_path, out_dir=out_dir)
            if in_path:
                in_files.append(in_path)

        print()
    else:
        # Use existing .in files
        in_files = [f.with_suffix('.in') for f in toml_files if f.with_suffix('.in').exists()]

    if not in_files:
        print("[ERR] No .in files generated or found")
        return 1

    # Phase 2: Render with eps gradient
    print(f"{'='*90}")
    print(f"PHASE 2: RENDER WITH EPS-BASED COLOR GRADIENT")
    print(f"{'='*90}\n")

    rendered = []
    eps_values = []

    for in_path, toml_path in zip(in_files, toml_files):
        eps_value = extract_eps_from_toml_file(toml_path)
        output_png = out_dir / in_path.with_suffix('.png').name

        png_path = render_in_with_eps(in_path, output_png, eps_value, dpi=args.dpi)
        if png_path:
            rendered.append(png_path)
            eps_values.append(eps_value)

    # Create legend
    if rendered and not args.no_legend:
        print()
        legend_path = out_dir / "eps_gradient_legend.png"
        create_eps_gradient_legend(eps_values, legend_path)

    # Summary
    print(f"\n{'='*90}")
    print(f"SUMMARY")
    print(f"{'='*90}")
    print(f"Converted TOML: {len([f for f in in_files if f.exists()])}")
    print(f"Rendered PNG: {len(rendered)}")
    if eps_values:
        valid_eps = [e for e in eps_values if e is not None]
        if valid_eps:
            print(f"Epsilon range: {min(valid_eps):.2f} — {max(valid_eps):.2f}")
    print(f"Output directory: {out_dir}")
    print(f"{'='*90}\n")

    return 0


if __name__ == "__main__":
    sys.exit(main())
