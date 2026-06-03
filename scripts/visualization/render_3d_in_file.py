#!/usr/bin/env python3
"""
Render a 3D gprMax .in file as PNG showing three orthogonal views.

Domain: X (length) × Y (depth/height) × Z (width)

Three views with ALIGNED AXES:
  - TOP: X-Z plane (looking down Y-axis)
  - FRONT: X-Y plane (looking from +Z direction)
  - SIDE: Z-Y plane (looking from +X direction)

All views share Y-axis range for proper scaling relationship.
"""

import re
from pathlib import Path
from dataclasses import dataclass

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import Circle, Rectangle

# Material styles
MATERIAL_COLORS = {
    'free_space': '#F0F4F8',
    'subgrade': '#2F4F4F',
    'formation': '#BDB76B',
    'bal_rock': '#5A5A5A',
    'bal_foul_granular': '#C8A055',
    'bal_foul': '#4B3621',
    'fouling': '#C8A055',
    'antenna': '#404040',
}

MATERIAL_LABELS = {
    'free_space': 'Air',
    'subgrade': 'Subgrade',
    'formation': 'Formation',
    'bal_rock': 'Ballast Rock',
    'bal_foul_granular': 'Fouling',
    'bal_foul': 'Dense Fouling',
    'fouling': 'Fouling',
    'antenna': 'Antenna (GSSI)',
}


@dataclass
class SphereGeom:
    x: float
    y: float
    z: float
    radius: float
    material: str


@dataclass
class BoxGeom:
    x1: float
    y1: float
    z1: float
    x2: float
    y2: float
    z2: float
    material: str


def parse_3d_in_file(path: Path):
    """Parse a 3D gprMax .in file."""
    spheres = []
    boxes = []
    domain = {'x': 0, 'y': 0, 'z': 0}
    metadata = {}
    tx = None
    rx = []

    with open(path, encoding='utf-8', errors='replace') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue

            if line.startswith("##"):
                if ':' in line:
                    key, val = line[2:].split(':', 1)
                    metadata[key.strip()] = val.strip()
                continue

            # Antenna inserted via #python block: the call line does NOT start
            # with '#', so handle it before the '#'-only guard below. Draw a
            # stand-in case box + tx marker from the call args.
            if line.startswith("antenna_like_GSSI"):
                import re as _re
                args = _re.findall(r"-?\d+\.?\d*(?:e-?\d+)?", line.split("(", 1)[1])
                if len(args) >= 3:
                    cx, cy, zs = float(args[0]), float(args[1]), float(args[2])
                    case = (0.300, 0.300, 0.178) if "400" in line else (0.170, 0.108, 0.045)
                    boxes.append(BoxGeom(
                        x1=cx - case[0] / 2, y1=cy - case[1] / 2, z1=zs,
                        x2=cx + case[0] / 2, y2=cy + case[1] / 2, z2=zs + case[2],
                        material="antenna"
                    ))
                    tx = {'x': cx, 'y': cy, 'z': zs}
                continue

            if not line.startswith("#"):
                continue

            tokens = line.split()
            if not tokens:
                continue

            cmd = tokens[0]

            if cmd == "#domain:":
                domain = {'x': float(tokens[1]), 'y': float(tokens[2]), 'z': float(tokens[3])}
            elif cmd == "#sphere:":
                spheres.append(SphereGeom(
                    x=float(tokens[1]), y=float(tokens[2]), z=float(tokens[3]),
                    radius=float(tokens[4]), material=tokens[5]
                ))
            elif cmd == "#box:":
                boxes.append(BoxGeom(
                    x1=float(tokens[1]), y1=float(tokens[2]), z1=float(tokens[3]),
                    x2=float(tokens[4]), y2=float(tokens[5]), z2=float(tokens[6]),
                    material=tokens[7]
                ))
            elif cmd == "#hertzian_dipole:":
                tx = {'x': float(tokens[2]), 'y': float(tokens[3]), 'z': float(tokens[4])}
            elif cmd == "#rx:":
                rx.append({'x': float(tokens[1]), 'y': float(tokens[2]), 'z': float(tokens[3])})

    return {
        'spheres': spheres,
        'boxes': boxes,
        'domain': domain,
        'metadata': metadata,
        'tx': tx,
        'rx': rx,
    }


def render_3d_views(scene_data, title="3D Domain", dpi=150):
    """Render three orthogonal views with proper axis alignment.

    Layout: Single column, three rows
      Row 0: TOP (X-Z plane) - width shows X (2.248m), height shows Z (0.4m)
      Row 1: FRONT (X-Y plane) - width shows X (2.248m), height shows Y (1.15m)
      Row 2: SIDE (Z-Y plane) - width shows Z (0.4m), height shows Y (1.15m)

    Alignment:
      - TOP and FRONT share X-axis (both 0-2.248m horizontally)
      - FRONT and SIDE share Y-axis (both 0-1.15m vertically)
    """
    spheres = scene_data['spheres']
    boxes = scene_data['boxes']
    domain = scene_data['domain']
    tx = scene_data['tx']
    rx = scene_data['rx']

    Dx, Dy, Dz = domain['x'], domain['y'], domain['z']

    # Manual axes placement guarantees true alignment regardless of aspect='equal'.
    # We pick a fixed scale (figure-fraction per metre) so every view uses the same
    # pixels-per-metre. Then TOP and FRONT get identical widths (both span Dx) and
    # FRONT and SIDE get identical heights (both span Dy).
    #
    #   TOP   : X (width Dx) × Z (height Dz)
    #   FRONT : X (width Dx) × Y (height Dy)   <- directly below TOP, X-axes align
    #   SIDE  : Z (width Dz) × Y (height Dy)   <- right of FRONT, Y-axes align

    # Layout budget in inches
    left_margin = 1.0
    right_margin = 0.3
    top_margin = 0.8
    bottom_margin = 1.0
    h_gap = 0.9          # horizontal gap between FRONT and SIDE
    v_gap = 0.9          # vertical gap between TOP and FRONT

    # Choose pixels-per-metre so the widest view (Dx) fits a target width
    target_plot_width = 10.0  # inches for the Dx-wide plots
    ppm = target_plot_width / Dx   # inches per metre (shared by ALL views)

    w_top = w_front = Dx * ppm
    h_top = Dz * ppm
    h_front = h_side = Dy * ppm
    w_side = Dz * ppm

    fig_w = left_margin + w_front + h_gap + w_side + right_margin
    fig_h = bottom_margin + h_front + v_gap + h_top + top_margin

    fig = plt.figure(figsize=(fig_w, fig_h), dpi=dpi)

    # Convert inch coords -> figure fractions for add_axes([l, b, w, h])
    def axes_rect(l_in, b_in, w_in, h_in):
        return [l_in / fig_w, b_in / fig_h, w_in / fig_w, h_in / fig_h]

    # FRONT sits at bottom-left
    front_l = left_margin
    front_b = bottom_margin
    # TOP sits directly above FRONT (same left, same width)
    top_l = left_margin
    top_b = bottom_margin + h_front + v_gap
    # SIDE sits to the right of FRONT (same bottom, same height)
    side_l = left_margin + w_front + h_gap
    side_b = bottom_margin

    # ─────────────────────────────────────────────────────────
    # VIEW 1: TOP (X-Z plane, looking down Y-axis)
    # ─────────────────────────────────────────────────────────
    ax_top = fig.add_axes(axes_rect(top_l, top_b, w_top, h_top))
    ax_top.set_xlim(0, Dx)
    ax_top.set_ylim(0, Dz)
    ax_top.set_xlabel('X (m) - Length', fontsize=10)
    ax_top.set_ylabel('Z (m) - Width', fontsize=10)
    ax_top.set_title('TOP VIEW (X-Z plane, looking down Y)', fontsize=11, fontweight='bold')
    ax_top.grid(True, alpha=0.2, linestyle='--')

    # Draw boxes
    for box in boxes:
        rect = Rectangle((box.x1, box.z1), box.x2 - box.x1, box.z2 - box.z1,
                         facecolor=MATERIAL_COLORS.get(box.material, '#CCCCCC'),
                         edgecolor='black', linewidth=0.5, alpha=0.7)
        ax_top.add_patch(rect)

    # Draw spheres
    for sphere in spheres:
        circle = Circle((sphere.x, sphere.z), sphere.radius,
                       facecolor=MATERIAL_COLORS.get(sphere.material, '#CCCCCC'),
                       edgecolor='black', linewidth=0.5, alpha=0.8)
        ax_top.add_patch(circle)

    # Mark TX/RX
    if tx:
        ax_top.plot(tx['x'], tx['z'], 'r*', markersize=14, label='TX',
                   markeredgecolor='darkred', markeredgewidth=0.5)
    for i, rxr in enumerate(rx):
        ax_top.plot(rxr['x'], rxr['z'], 'b^', markersize=9, label='RX' if i == 0 else '',
                   markeredgecolor='darkblue', markeredgewidth=0.5)
    ax_top.legend(fontsize=10, loc='upper right')

    # ─────────────────────────────────────────────────────────
    # VIEW 2: FRONT (X-Y plane)
    # Left column - shares X-axis with TOP (same width), Y-axis with SIDE (same height)
    # ─────────────────────────────────────────────────────────
    ax_front = fig.add_axes(axes_rect(front_l, front_b, w_front, h_front))
    ax_front.set_xlim(0, Dx)
    ax_front.set_ylim(0, Dy)
    ax_front.set_xlabel('X (m) - Length', fontsize=10)
    ax_front.set_ylabel('Y (m) - Depth', fontsize=10)
    ax_front.set_title('FRONT VIEW (X-Y vertical slice)', fontsize=11, fontweight='bold')
    ax_front.grid(True, alpha=0.2, linestyle='--')

    # Draw boxes (X-Y projection)
    for box in boxes:
        rect = Rectangle((box.x1, box.y1), box.x2 - box.x1, box.y2 - box.y1,
                         facecolor=MATERIAL_COLORS.get(box.material, '#CCCCCC'),
                         edgecolor='black', linewidth=0.5, alpha=0.7)
        ax_front.add_patch(rect)

    # Draw spheres (X-Y projection)
    for sphere in spheres:
        circle = Circle((sphere.x, sphere.y), sphere.radius,
                       facecolor=MATERIAL_COLORS.get(sphere.material, '#CCCCCC'),
                       edgecolor='black', linewidth=0.5, alpha=0.8)
        ax_front.add_patch(circle)

    # Mark TX/RX (X-Y projection)
    if tx:
        ax_front.plot(tx['x'], tx['y'], 'r*', markersize=14, label='TX',
                     markeredgecolor='darkred', markeredgewidth=0.5)
    for i, rxr in enumerate(rx):
        ax_front.plot(rxr['x'], rxr['y'], 'b^', markersize=9, label='RX' if i == 0 else '',
                     markeredgecolor='darkblue', markeredgewidth=0.5)
    ax_front.legend(fontsize=10, loc='upper right')

    # ─────────────────────────────────────────────────────────
    # VIEW 3: SIDE (Z-Y plane)
    # Right column - shares Y-axis with FRONT (same height), proportional width to Z dimension
    # ─────────────────────────────────────────────────────────
    ax_side = fig.add_axes(axes_rect(side_l, side_b, w_side, h_side))
    ax_side.set_xlim(0, Dz)
    ax_side.set_ylim(0, Dy)
    ax_side.set_xlabel('Z (m) - Width', fontsize=10)
    ax_side.set_ylabel('Y (m) - Depth', fontsize=10)
    ax_side.set_title('SIDE VIEW (Z-Y cross-section)', fontsize=11, fontweight='bold')
    ax_side.grid(True, alpha=0.2, linestyle='--')

    # Draw boxes (Z-Y projection)
    for box in boxes:
        rect = Rectangle((box.z1, box.y1), box.z2 - box.z1, box.y2 - box.y1,
                         facecolor=MATERIAL_COLORS.get(box.material, '#CCCCCC'),
                         edgecolor='black', linewidth=0.5, alpha=0.7)
        ax_side.add_patch(rect)

    # Draw spheres (Z-Y projection)
    for sphere in spheres:
        circle = Circle((sphere.z, sphere.y), sphere.radius,
                       facecolor=MATERIAL_COLORS.get(sphere.material, '#CCCCCC'),
                       edgecolor='black', linewidth=0.5, alpha=0.8)
        ax_side.add_patch(circle)

    # Mark TX/RX (Z-Y projection)
    if tx:
        ax_side.plot(tx['z'], tx['y'], 'r*', markersize=14, label='TX',
                    markeredgecolor='darkred', markeredgewidth=0.5)
    for i, rxr in enumerate(rx):
        ax_side.plot(rxr['z'], rxr['y'], 'b^', markersize=9, label='RX' if i == 0 else '',
                    markeredgecolor='darkblue', markeredgewidth=0.5)
    ax_side.legend(fontsize=10, loc='upper right')

    # Overall title
    fig.suptitle(title, fontsize=13, fontweight='bold', y=0.995)

    # Add legend for materials (manual axes => no tight_layout, place via figure coords)
    legend_elements = []
    for mat in ['free_space', 'subgrade', 'formation', 'bal_rock', 'bal_foul_granular']:
        if mat in MATERIAL_COLORS:
            label = MATERIAL_LABELS.get(mat, mat)
            legend_elements.append(mpatches.Patch(facecolor=MATERIAL_COLORS[mat],
                                                  edgecolor='black', label=label))
    fig.legend(handles=legend_elements, loc='lower center', ncol=5, fontsize=9,
              bbox_to_anchor=(0.5, 0.005))

    return fig


def main():
    import argparse
    ap = argparse.ArgumentParser(description="Render a 3D gprMax .in file as PNG")
    ap.add_argument("in_file", type=Path, help="Path to 3D .in file")
    ap.add_argument("-o", "--output", type=Path, default=None, help="Output PNG path")
    ap.add_argument("--dpi", type=int, default=150, help="Output DPI")
    ap.add_argument("--no-show", action="store_true", help="Skip interactive window")

    args = ap.parse_args()

    in_path = args.in_file.resolve()
    if not in_path.exists():
        print(f"Error: File not found: {in_path}")
        return

    print(f"Parsing: {in_path}")
    scene_data = parse_3d_in_file(in_path)

    print(f"  Spheres: {len(scene_data['spheres'])}")
    print(f"  Boxes: {len(scene_data['boxes'])}")
    print(f"  Domain: {scene_data['domain']['x']:.2f} × {scene_data['domain']['y']:.2f} × {scene_data['domain']['z']:.2f} m")

    print(f"Rendering 3D views...")
    title = f"{in_path.stem} - {scene_data['metadata'].get('Lab_Class', '?')} class"
    fig = render_3d_views(scene_data, title=title, dpi=args.dpi)

    out_path = args.output or in_path.with_stem(in_path.stem + "_3d").with_suffix(".png")
    fig.savefig(out_path, dpi=args.dpi, bbox_inches="tight")
    print(f"Saved -> {out_path}")

    if not args.no_show:
        import matplotlib.pyplot as plt
        plt.show()


if __name__ == "__main__":
    main()
