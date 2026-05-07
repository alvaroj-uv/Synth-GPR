"""
Render a gprMax .in file as a 2-D cross-section PNG.

Usage:
    python scripts/visualization/render_in_file.py output/test_mc/s_0001.in
    python scripts/visualization/render_in_file.py output/test_mc/s_0001.in --out custom.png --dpi 200
"""

import sys
import argparse
from pathlib import Path

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import Rectangle, Circle

# ── colour palette ────────────────────────────────────────────────────────────
COLORS = {
    "free_space":        "#F0F4F8",   # very light blue-white (air)
    "subgrade":          "#7D6244",   # earthy mid-brown
    "formation":         "#B8956A",   # lighter tan
    "bal_rock":          "#5A5A5A",   # granite grey
    "bal_foul_granular": "#C8A055",   # sandy-clay amber
}

LABELS = {
    "free_space":        "Air",
    "subgrade":          "Subgrade",
    "formation":         "Formation",
    "bal_rock":          "Ballast Rock",
    "bal_foul_granular": "Fouling",
}

LEGEND_ORDER = ["subgrade", "formation", "bal_rock", "bal_foul_granular"]


# ── parser ────────────────────────────────────────────────────────────────────
def parse_in_file(path: Path) -> dict:
    domain = None
    boxes, cylinders, dipoles, rxs = [], [], [], []
    meta = {}

    with open(path) as fh:
        for raw in fh:
            line = raw.strip()

            if line.startswith("## ") and ":" in line:
                # header metadata comment
                key, _, val = line[3:].partition(":")
                meta[key.strip()] = val.strip()
                continue

            if not line.startswith("#"):
                continue

            tokens = line.split()
            cmd = tokens[0]

            if cmd == "#domain:":
                domain = (float(tokens[1]), float(tokens[2]), float(tokens[3]))

            elif cmd == "#box:":
                boxes.append(dict(
                    x1=float(tokens[1]), y1=float(tokens[2]),
                    x2=float(tokens[4]), y2=float(tokens[5]),
                    material=tokens[7],
                ))

            elif cmd == "#cylinder:":
                # #cylinder: x1 y1 z1 x2 y2 z2 radius material
                # z-aligned cylinders: x1==x2, y1==y2
                cylinders.append(dict(
                    x=float(tokens[1]), y=float(tokens[2]),
                    radius=float(tokens[7]),
                    material=tokens[8],
                ))

            elif cmd == "#hertzian_dipole:":
                # #hertzian_dipole: pol x y z waveform
                dipoles.append(dict(x=float(tokens[2]), y=float(tokens[3])))

            elif cmd == "#rx:":
                rxs.append(dict(x=float(tokens[1]), y=float(tokens[2])))

    if domain is None:
        raise ValueError(f"No #domain command found in {path}")

    return dict(domain=domain, boxes=boxes, cylinders=cylinders,
                dipoles=dipoles, rxs=rxs, meta=meta)


# ── renderer ──────────────────────────────────────────────────────────────────
def render(data: dict, in_path: Path, out_path: Path, dpi: int = 150):
    dx, dy, _ = data["domain"]
    boxes     = data["boxes"]
    cylinders = data["cylinders"]
    dipoles   = data["dipoles"]
    rxs       = data["rxs"]
    meta      = data["meta"]

    aspect = dy / dx                         # tall/narrow for a typical scene
    fig_w  = 6.0
    fig_h  = min(fig_w * aspect * 0.75, 14) # cap height so it fits on screen
    fig, ax = plt.subplots(figsize=(fig_w, fig_h), dpi=dpi)

    # background (air)
    ax.set_facecolor(COLORS["free_space"])

    # ── geometry (painter's order: first placed = lowest priority) ──
    seen = set()
    for box in boxes:
        mat   = box["material"]
        color = COLORS.get(mat, "#CCCCCC")
        rect  = Rectangle(
            (box["x1"], box["y1"]),
            box["x2"] - box["x1"],
            box["y2"] - box["y1"],
            facecolor=color, edgecolor="none", zorder=1,
        )
        ax.add_patch(rect)
        seen.add(mat)

    for cyl in cylinders:
        mat    = cyl["material"]
        color  = COLORS.get(mat, "#AAAAAA")
        circle = Circle(
            (cyl["x"], cyl["y"]), cyl["radius"],
            facecolor=color, edgecolor="#333333", linewidth=0.25, zorder=2,
        )
        ax.add_patch(circle)
        seen.add(mat)

    # ── antennas ──────────────────────────────────────────────────────
    for d in dipoles:
        ax.plot(d["x"], d["y"], marker="v", color="#E82020",
                markersize=7, zorder=5, linestyle="none", label="TX")
    for r in rxs:
        ax.plot(r["x"], r["y"], marker="^", color="#1060D0",
                markersize=7, zorder=5, linestyle="none", label="RX")

    # ── layer boundary lines ──────────────────────────────────────────
    # Infer boundaries from box edges
    boundary_ys = set()
    for box in boxes:
        if box["material"] in ("subgrade", "formation", "bal_foul_granular"):
            boundary_ys.add(round(box["y1"], 6))
            boundary_ys.add(round(box["y2"], 6))
    for y in sorted(boundary_ys):
        if 0 < y < dy:
            ax.axhline(y, color="#AAAAAA", linewidth=0.6, linestyle="--", zorder=0)

    # ── legend ────────────────────────────────────────────────────────
    patches = []
    for mat in LEGEND_ORDER:
        if mat in seen:
            patches.append(mpatches.Patch(
                facecolor=COLORS[mat], edgecolor="#555555",
                linewidth=0.5, label=LABELS.get(mat, mat),
            ))
    if dipoles:
        patches.append(plt.Line2D([0], [0], marker="v", color="#E82020",
                                  markersize=7, linestyle="none", label="TX"))
    if rxs:
        patches.append(plt.Line2D([0], [0], marker="^", color="#1060D0",
                                  markersize=7, linestyle="none", label="RX"))
    ax.legend(handles=patches, loc="upper right", fontsize=7, framealpha=0.85)

    # ── metadata annotation ───────────────────────────────────────────
    info_lines = []
    for key in ("pvc", "mc_pvc_measured", "Lab_FI", "Lab_Class", "rock_count"):
        if key in meta:
            label = {
                "pvc":             "PVC requested",
                "mc_pvc_measured": "PVC measured (MC)",
                "Lab_FI":          "Lab FI",
                "Lab_Class":       "Class",
                "rock_count":      "Rocks",
            }.get(key, key)
            info_lines.append(f"{label}: {meta[key]}")
    if info_lines:
        ax.text(0.01, 0.99, "\n".join(info_lines),
                transform=ax.transAxes, fontsize=7, va="top",
                bbox=dict(boxstyle="round,pad=0.3", facecolor="white", alpha=0.8))

    # ── axes ──────────────────────────────────────────────────────────
    ax.set_xlim(0, dx)
    ax.set_ylim(0, dy)
    ax.set_xlabel("x (m)", fontsize=9)
    ax.set_ylabel("y (m)", fontsize=9)
    ax.set_title(in_path.stem, fontsize=10, fontweight="bold")
    ax.set_aspect("equal")
    ax.tick_params(labelsize=8)
    ax.grid(visible=True, alpha=0.15, linewidth=0.4)

    fig.tight_layout()
    fig.savefig(out_path, dpi=dpi, bbox_inches="tight")
    print(f"Saved → {out_path}")
    return fig


# ── CLI ───────────────────────────────────────────────────────────────────────
def main():
    ap = argparse.ArgumentParser(description="Render a gprMax .in file as PNG")
    ap.add_argument("in_file", type=Path, help="Path to the .in file")
    ap.add_argument("--out",   type=Path, default=None,
                    help="Output PNG path (default: same dir as .in file)")
    ap.add_argument("--dpi",   type=int,  default=150)
    args = ap.parse_args()

    in_path  = args.in_file.resolve()
    out_path = args.out or in_path.with_suffix(".png")

    data = parse_in_file(in_path)
    render(data, in_path, out_path, dpi=args.dpi)


if __name__ == "__main__":
    main()
