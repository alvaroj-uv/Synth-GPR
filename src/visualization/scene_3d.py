"""
3D scene rendering: three orthogonal views of a 3D gprMax .in file.

Domain: X (length) × Y (depth/height) × Z (width)

Three views with ALIGNED AXES:
  - TOP: X-Z plane (looking down Y-axis)
  - FRONT: X-Y plane (looking from +Z direction)
  - SIDE: Z-Y plane (looking from +X direction)

All views share Y-axis range for proper scaling relationship.
"""

from __future__ import annotations

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


def render_3d_views(scene, title="3D Domain", dpi=150):
    """Render three orthogonal views with proper axis alignment.

    Layout: Single column, three rows
      Row 0: TOP (X-Z plane) - width shows X (2.248m), height shows Z (0.4m)
      Row 1: FRONT (X-Y plane) - width shows X (2.248m), height shows Y (1.15m)
      Row 2: SIDE (Z-Y plane) - width shows Z (0.4m), height shows Y (1.15m)

    Alignment:
      - TOP and FRONT share X-axis (both 0-2.248m horizontally)
      - FRONT and SIDE share Y-axis (both 0-1.15m vertically)
    """
    spheres = scene.spheres
    boxes = scene.boxes
    tx = scene.tx
    rx = scene.receivers

    Dx, Dy, Dz = scene.domain_x, scene.domain_y, scene.domain_z

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
        ax_top.plot(tx.x, tx.z, 'r*', markersize=14, label='TX',
                   markeredgecolor='darkred', markeredgewidth=0.5)
    for i, rxr in enumerate(rx):
        ax_top.plot(rxr.x, rxr.z, 'b^', markersize=9, label='RX' if i == 0 else '',
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
        ax_front.plot(tx.x, tx.y, 'r*', markersize=14, label='TX',
                     markeredgecolor='darkred', markeredgewidth=0.5)
    for i, rxr in enumerate(rx):
        ax_front.plot(rxr.x, rxr.y, 'b^', markersize=9, label='RX' if i == 0 else '',
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
        ax_side.plot(tx.z, tx.y, 'r*', markersize=14, label='TX',
                    markeredgecolor='darkred', markeredgewidth=0.5)
    for i, rxr in enumerate(rx):
        ax_side.plot(rxr.z, rxr.y, 'b^', markersize=9, label='RX' if i == 0 else '',
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
