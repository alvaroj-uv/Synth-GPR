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

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import Circle, Rectangle

# Material colors/labels come exclusively from the shared registry in
# .materials (same source as the 2D renderer) so 2D and 3D figures of the
# same scene can never disagree on a material's appearance.
from .materials import get_style

# Materials shown in the 3D figure legend, in display order
_LEGEND_MATERIALS = ['free_space', 'subgrade', 'formation', 'bal_rock', 'bal_foul_granular']


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
                         facecolor=get_style(box.material).color,
                         edgecolor='black', linewidth=0.5, alpha=0.7)
        ax_top.add_patch(rect)

    # Draw spheres
    for sphere in spheres:
        circle = Circle((sphere.x, sphere.z), sphere.radius,
                       facecolor=get_style(sphere.material).color,
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
                         facecolor=get_style(box.material).color,
                         edgecolor='black', linewidth=0.5, alpha=0.7)
        ax_front.add_patch(rect)

    # Draw spheres (X-Y projection)
    for sphere in spheres:
        circle = Circle((sphere.x, sphere.y), sphere.radius,
                       facecolor=get_style(sphere.material).color,
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
                         facecolor=get_style(box.material).color,
                         edgecolor='black', linewidth=0.5, alpha=0.7)
        ax_side.add_patch(rect)

    # Draw spheres (Z-Y projection)
    for sphere in spheres:
        circle = Circle((sphere.z, sphere.y), sphere.radius,
                       facecolor=get_style(sphere.material).color,
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
    for mat in _LEGEND_MATERIALS:
        style = get_style(mat)
        legend_elements.append(mpatches.Patch(facecolor=style.color,
                                              edgecolor='black', label=style.label))
    fig.legend(handles=legend_elements, loc='lower center', ncol=5, fontsize=9,
              bbox_to_anchor=(0.5, 0.005))

    return fig


def render_rocks_3d(
    rocks,
    *,
    boxes=None,
    domain=None,
    bounds=None,
    title="3-D packing",
    color="#8b7355",
    edgecolor="k",
    marker_scale=320.0,
    alpha=0.85,
    box_alpha=0.22,
    dpi=150,
    ax=None,
):
    """Render a 3-D scene — ``Rock`` spheres plus layer slabs — in perspective.

    Complements :func:`render_3d_views`, which draws three orthogonal 2-D
    projections from a parsed ``.in`` scene. This takes packer output directly
    — a list of :class:`~src.rock_model.Rock` with ``z`` set — so a packing can
    be eyeballed before any deck is written. Marker area scales with each
    rock's radius relative to the largest axis span, so the same call looks
    right at any domain size.

    Because a parsed scene's ``#sphere`` objects already expose ``.x/.y/.z/
    .radius``, you can render a whole ``.in`` file in perspective with layer
    boxes via ``render_rocks_3d(scene.spheres, boxes=scene.boxes, domain=...)``.

    Args:
        rocks: iterable of Rock (or scene spheres) with .x/.y/.z/.radius
            (z must be set → sphere). Rocks carry their final scene coordinates.
        boxes: optional iterable of layer slabs to draw as translucent cuboids.
            Each item is either a scene ``Box`` object (``.x1.. .z2`` plus an
            optional ``.material`` for colour) or a tuple
            ``(x1, y1, z1, x2, y2, z2[, color])``.
        domain: optional ``(Dx, Dy, Dz)`` — sets axis limits to the full gprMax
            domain (origin at 0). Takes precedence over ``bounds``.
        bounds: optional PackingBounds for axis limits (uses ``.mins`` /
            ``.lengths``) when ``domain`` is None.
        title: plot title; the sphere count is appended.
        color / edgecolor / alpha: sphere appearance.
        box_alpha: opacity of the layer slabs (kept low so rocks show through).
        marker_scale: visual size constant (scatter point size per unit of
            radius / span). Default reproduces the packing-test look.
        dpi: figure resolution (ignored when ``ax`` is supplied).
        ax: existing 3-D Axes to draw into; a new figure is created if None.

    Returns:
        The matplotlib Figure containing the scene.

    Raises:
        ValueError: if no rock carries a z coordinate (nothing 3-D to draw).
    """
    spheres = [r for r in rocks if getattr(r, "z", None) is not None]
    if not spheres:
        raise ValueError("render_rocks_3d needs 3-D rocks (Rock.z set); got none.")

    xs = np.array([r.x for r in spheres], float)
    ys = np.array([r.y for r in spheres], float)
    zs = np.array([r.z for r in spheres], float)
    rs = np.array([r.radius for r in spheres], float)

    if ax is None:
        fig = plt.figure(figsize=(8, 7), dpi=dpi)
        ax = fig.add_subplot(111, projection="3d")
    else:
        fig = ax.figure

    # Axis limits: full domain > packing bounds > rock extents (radius-padded).
    if domain is not None:
        x_hi, y_hi, z_hi = domain
        x_lo = y_lo = z_lo = 0.0
    elif bounds is not None:
        x_lo, y_lo, z_lo = bounds.mins
        Lx, Ly, Lz = bounds.lengths
        x_hi, y_hi, z_hi = x_lo + Lx, y_lo + Ly, z_lo + Lz
    else:
        x_lo, x_hi = float((xs - rs).min()), float((xs + rs).max())
        y_lo, y_hi = float((ys - rs).min()), float((ys + rs).max())
        z_lo, z_hi = float((zs - rs).min()), float((zs + rs).max())

    # Layer slabs (e.g. subgrade) as translucent cuboids, drawn first so the
    # rocks render on top. Accepts scene Box objects or 6/7-tuples.
    for box in (boxes or []):
        if hasattr(box, "x1"):
            bx = (box.x1, box.y1, box.z1, box.x2, box.y2, box.z2)
            bcol = get_style(box.material).color if getattr(box, "material", None) else "#888888"
        else:
            bx = tuple(box[:6])
            bcol = box[6] if len(box) > 6 else "#888888"
        bx1, by1, bz1, bx2, by2, bz2 = bx
        ax.bar3d(bx1, by1, bz1, bx2 - bx1, by2 - by1, bz2 - bz1,
                 color=bcol, alpha=box_alpha, shade=True,
                 edgecolor=(0, 0, 0, 0.25), linewidth=0.3)

    # Marker area ∝ (radius / largest span)² so screen size tracks physical size
    # and auto-shrinks when the domain is larger.
    L = max(x_hi - x_lo, y_hi - y_lo, z_hi - z_lo) or 1.0
    s = (rs / L * marker_scale) ** 2

    ax.scatter(xs, ys, zs, s=s, c=color, edgecolors=edgecolor,
               linewidths=0.3, alpha=alpha)
    ax.set_xlim(x_lo, x_hi)
    ax.set_ylim(y_lo, y_hi)
    ax.set_zlim(z_lo, z_hi)
    ax.set_xlabel("x (m)")
    ax.set_ylabel("y (m)")
    ax.set_zlabel("z (m)")
    ax.set_title(f"{title} ({len(spheres)} spheres)")
    return fig
