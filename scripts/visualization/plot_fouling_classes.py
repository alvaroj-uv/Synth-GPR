"""
Plot one representative GPR A-scan per fouling class, stacked vertically
(one row per class — NOT overlaid).

Each row shows three panels:
    [ scene geometry (rocks) ]  [ full A-scan ]  [ coda zoom ]

Classes are ordered by severity (clean -> heavy fouling). Discovers classes
from companion .in files (## Lab_Class:), picks one .out example per class.

Usage:
    python scripts/visualization/plot_fouling_classes.py
    python scripts/visualization/plot_fouling_classes.py --dir output/dataset_variants --component Ez
    python scripts/visualization/plot_fouling_classes.py --class-field FI_class
"""
import sys
import argparse
import re
from pathlib import Path

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from src.visualization.drawing import draw_geometry
from src.visualization.parser import parse_in_file
from src.signal_processing import calculate_instantaneous_attributes
from src.data_loader import read_ascan as _read_ascan_out


# Severity ordering low -> high fouling (used when class labels match)
SEVERITY_ORDER = ["MC", "CL", "CF", "F", "MF", "M", "F2", "HF", "VHF"]

# coda window (ns) — region past the direct pulse where classes differ
CODA_NS = (6.0, 16.0)


def read_header_meta(in_path: Path) -> dict:
    """Extract '## key: value' comment metadata from a gprMax .in file."""
    meta = {}
    if not in_path.exists():
        return meta
    with open(in_path, encoding="utf-8", errors="ignore") as fh:
        for line in fh:
            if not line.startswith("#"):
                continue
            m = re.match(r"^##\s+([\w]+):\s+(.+)", line)
            if m:
                meta[m.group(1)] = m.group(2).strip()
    return meta


def pick_examples(out_dir: Path, class_field: str) -> dict:
    """Return {class_label: out_path} with one representative .out per class."""
    examples = {}
    for in_path in sorted(out_dir.glob("*.in")):
        out_path = in_path.with_suffix(".out")
        if not out_path.exists():
            continue
        meta = read_header_meta(in_path)
        label = meta.get(class_field)
        if label and label not in examples:
            examples[label] = out_path
    return examples


def read_ascan(out_path: Path, component: str):
    """Return (t_ns, signal, used_component, dt) for rx1."""
    d = _read_ascan_out(out_path, component)
    return d["t_ns"], d["signal"], d["component"], d["dt"]


def _focus_on_ballast(ax, scene, pad_frac=0.06):
    """Remove the material legend / meta text and crop the y-axis to the
    ballast layer so the rocks fill the mini panel."""
    # Drop the legend draw_geometry added.
    leg = ax.get_legend()
    if leg is not None:
        leg.remove()
    # Drop free-floating annotation text (meta card) but keep patches/lines.
    for txt in list(ax.texts):
        txt.remove()

    b_bot = scene.meta.get("ballast_bottom_y")
    b_top = scene.meta.get("ballast_top_y")
    if b_bot is not None and b_top is not None:
        b_bot, b_top = float(b_bot), float(b_top)
        pad = (b_top - b_bot) * pad_frac
        ax.set_ylim(b_bot - pad, b_top + pad)
        # keep aspect honest: equal would force a huge x-range, so relax it
        ax.set_aspect("auto")


def order_labels(labels, class_field):
    if class_field == "Lab_Class" or class_field == "FI_class":
        ranked = [l for l in SEVERITY_ORDER if l in labels]
        rest = sorted(l for l in labels if l not in ranked)
        return ranked + rest
    return sorted(labels)


def plot_classes(out_dir: Path, component: str, class_field: str) -> Path:
    examples = pick_examples(out_dir, class_field)
    if not examples:
        sys.exit(f"[!] No .out/.in pairs with '{class_field}' found in {out_dir}")
    labels = order_labels(list(examples.keys()), class_field)

    # --- style (matches visualize_ascan.py) ---
    dark_bg, panel_bg = "#0f1117", "#1a1e2b"
    grid_col, text_col = "#2a2f42", "#c8d0e0"
    palette = ["#00d4ff", "#a0e070", "#ffd166", "#ff9e35",
               "#ff6b35", "#e070d0", "#80a0ff"]

    n = len(labels)
    fig = plt.figure(figsize=(13, 2.2 * n + 1))
    fig.patch.set_facecolor(dark_bg)
    # cols: geometry (narrow) | full A-scan (wide) | coda zoom (medium)
    gs = fig.add_gridspec(n, 3, width_ratios=[1.0, 2.4, 1.6],
                          hspace=0.45, wspace=0.22,
                          left=0.05, right=0.985, top=0.93, bottom=0.07)

    used_comp = component
    for i, label in enumerate(labels):
        out_path = examples[label]
        in_path = out_path.with_suffix(".in")
        t_ns, signal, used_comp, dt = read_ascan(out_path, component)
        # Hilbert envelope — same primitive the feature pipeline uses
        envelope = calculate_instantaneous_attributes(
            signal, dt, use_mirroring=True)["envelope"]
        col = palette[i % len(palette)]
        meta = read_header_meta(in_path)
        fi, pvc = meta.get("Lab_FI", "?"), meta.get("pvc", "?")

        # --- col 0: scene geometry (rocks) ---
        ax_g = fig.add_subplot(gs[i, 0])
        try:
            scene = parse_in_file(in_path)
            draw_geometry(ax_g, scene)
            _focus_on_ballast(ax_g, scene)
        except Exception as e:  # rendering is best-effort
            ax_g.text(0.5, 0.5, f"geom n/a\n{e}", ha="center", va="center",
                      color=text_col, fontsize=6, transform=ax_g.transAxes)
        ax_g.set_facecolor(panel_bg)
        ax_g.set_title("ballast", color=text_col, fontsize=7, pad=2)
        ax_g.set_xlabel(""); ax_g.set_ylabel("")
        ax_g.tick_params(colors=text_col, labelsize=5)
        for sp in ax_g.spines.values():
            sp.set_edgecolor(col)
            sp.set_linewidth(1.2)

        # --- col 1: full A-scan ---
        ax_f = fig.add_subplot(gs[i, 1])
        ax_f.set_facecolor(panel_bg)
        ax_f.plot(t_ns, signal, color=col, lw=0.9)
        ax_f.axhline(0, color=grid_col, lw=0.5)
        ax_f.axvspan(*CODA_NS, color="#ffffff", alpha=0.05)  # mark zoom window
        ax_f.set_ylabel(f"{used_comp} (V/m)", color=text_col, fontsize=8)
        ax_f.tick_params(colors=text_col, labelsize=7)
        ax_f.grid(True, color=grid_col, lw=0.4, alpha=0.5)
        for sp in ax_f.spines.values():
            sp.set_edgecolor(grid_col)
        ax_f.text(0.012, 0.92,
                  f"{class_field}={label}   FI={fi}%   PVC={pvc}%   ({out_path.stem})",
                  transform=ax_f.transAxes, color=col, fontsize=8.5,
                  va="top", ha="left", fontfamily="monospace",
                  bbox=dict(boxstyle="round,pad=0.3", fc=dark_bg, ec=col, lw=0.8))

        # --- col 2: coda zoom with Hilbert envelope ---
        ax_z = fig.add_subplot(gs[i, 2])
        ax_z.set_facecolor(panel_bg)
        m = (t_ns >= CODA_NS[0]) & (t_ns <= CODA_NS[1])
        ax_z.plot(t_ns[m], signal[m], color=col, lw=0.9, alpha=0.55,
                  label="raw")
        # envelope (and its mirror) traces the energy decay the model sees
        ax_z.fill_between(t_ns[m], envelope[m], color="#ffffff", alpha=0.10)
        ax_z.plot(t_ns[m],  envelope[m], color="#ffffff", lw=1.3,
                  label="Hilbert env.")
        ax_z.plot(t_ns[m], -envelope[m], color="#ffffff", lw=0.7, alpha=0.5)
        ax_z.axhline(0, color=grid_col, lw=0.5)
        # coda energy = integral of envelope over the window (model-relevant)
        coda_energy = float(np.trapezoid(envelope[m], t_ns[m]))
        ax_z.text(0.97, 0.06, f"coda E = {coda_energy:.1f}",
                  transform=ax_z.transAxes, color="#ffffff", fontsize=7,
                  ha="right", va="bottom", fontfamily="monospace",
                  bbox=dict(boxstyle="round,pad=0.25", fc=dark_bg,
                            ec="#ffffff", lw=0.6, alpha=0.7))
        ax_z.tick_params(colors=text_col, labelsize=7)
        ax_z.grid(True, color=grid_col, lw=0.4, alpha=0.5)
        for sp in ax_z.spines.values():
            sp.set_edgecolor(grid_col)
        ax_z.set_title(f"coda zoom {CODA_NS[0]:.0f}-{CODA_NS[1]:.0f} ns  +Hilbert env.",
                       color=text_col, fontsize=7, pad=2)
        if i == 0:
            ax_z.legend(fontsize=6, facecolor=panel_bg, labelcolor=text_col,
                        edgecolor=grid_col, loc="upper left")

        if i == n - 1:
            ax_f.set_xlabel("Two-way travel time (ns)", color=text_col, fontsize=9)
            ax_z.set_xlabel("ns", color=text_col, fontsize=8)

    fig.suptitle(
        f"GPR A-scans by fouling class ({used_comp}) — ordered by severity | one example per {class_field}",
        color=text_col, fontsize=12, y=0.975)

    out_png = out_dir.parent / f"fouling_classes_{class_field}_{used_comp}.png"
    fig.savefig(out_png, dpi=150, bbox_inches="tight", facecolor=dark_bg)
    plt.close(fig)
    print(f"Found classes (ordered): {labels}")
    print(f"Saved -> {out_png}")
    return out_png


def main():
    ap = argparse.ArgumentParser(description="Stacked A-scans + scene per fouling class")
    ap.add_argument("--dir", type=Path, default=Path("output/dataset_variants"))
    ap.add_argument("--component", default="Ez")
    ap.add_argument("--class-field", default="Lab_Class",
                    help="Header field for class (e.g. Lab_Class, FI_class)")
    args = ap.parse_args()
    plot_classes(args.dir.resolve(), args.component, args.class_field)


if __name__ == "__main__":
    main()
