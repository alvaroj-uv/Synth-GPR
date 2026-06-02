"""
Scatter of coda energy vs Fouling Index (FI) across many samples.

For every .out/.in pair it integrates the Hilbert envelope over the coda
window (the same primitive the feature pipeline uses) and plots that coda
energy against Lab_FI, coloured by Lab_Class. This is the quantitative
counterpart to plot_fouling_classes.py: it tests whether the coda actually
correlates with fouling across the dataset rather than in a single example.

Usage:
    python scripts/visualization/plot_coda_energy_vs_fi.py
    python scripts/visualization/plot_coda_energy_vs_fi.py --dir output/dataset_variants --limit 2000
"""
import sys
import argparse
import re
from pathlib import Path

import h5py
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from src.signal_processing import calculate_instantaneous_attributes

CODA_NS = (6.0, 16.0)  # must match plot_fouling_classes.py
CLASS_COLORS = {
    "MC": "#00d4ff", "F": "#a0e070", "MF": "#ffd166",
    "HF": "#ff6b35", "VHF": "#e070d0",
}


def read_header_meta(in_path: Path) -> dict:
    meta = {}
    with open(in_path, encoding="utf-8", errors="ignore") as fh:
        for line in fh:
            if not line.startswith("#"):
                continue
            m = re.match(r"^##\s+([\w]+):\s+(.+)", line)
            if m:
                meta[m.group(1)] = m.group(2).strip()
    return meta


def coda_energy(out_path: Path, component="Ez"):
    with h5py.File(out_path, "r") as f:
        dt = float(f.attrs["dt"])
        iterations = int(f.attrs["Iterations"])
        rx = f["rxs/rx1"]
        comp = component if component in rx else (
            "Ez" if "Ez" in rx else list(rx.keys())[0])
        signal = rx[comp][:]
    t_ns = np.arange(iterations) * dt * 1e9
    env = calculate_instantaneous_attributes(signal, dt, use_mirroring=True)["envelope"]
    m = (t_ns >= CODA_NS[0]) & (t_ns <= CODA_NS[1])
    return float(np.trapezoid(env[m], t_ns[m]))


def collect(out_dir: Path, component: str, limit: int):
    rows = []  # (fi, coda_E, class)
    pairs = sorted(out_dir.glob("*.in"))
    for in_path in pairs:
        out_path = in_path.with_suffix(".out")
        if not out_path.exists():
            continue
        meta = read_header_meta(in_path)
        try:
            fi = float(meta.get("Lab_FI"))
        except (TypeError, ValueError):
            continue
        cls = meta.get("Lab_Class", "?")
        try:
            ce = coda_energy(out_path, component)
        except Exception:
            continue
        rows.append((fi, ce, cls))
        if limit and len(rows) >= limit:
            break
    return rows


def plot(out_dir: Path, component: str, limit: int) -> Path:
    rows = collect(out_dir, component, limit)
    if not rows:
        sys.exit(f"[!] No usable .out/.in pairs in {out_dir}")
    fi = np.array([r[0] for r in rows])
    ce = np.array([r[1] for r in rows])
    cls = np.array([r[2] for r in rows])

    dark_bg, panel_bg = "#0f1117", "#1a1e2b"
    grid_col, text_col = "#2a2f42", "#c8d0e0"

    fig, ax = plt.subplots(figsize=(10, 6.5))
    fig.patch.set_facecolor(dark_bg)
    ax.set_facecolor(panel_bg)

    for c in sorted(set(cls)):
        mask = cls == c
        ax.scatter(fi[mask], ce[mask], s=14, alpha=0.6,
                   color=CLASS_COLORS.get(c, "#888888"),
                   edgecolors="none", label=f"{c} (n={mask.sum()})")

    # linear trend + Pearson r
    if len(fi) > 2:
        a, b = np.polyfit(fi, ce, 1)
        xs = np.linspace(fi.min(), fi.max(), 100)
        ax.plot(xs, a * xs + b, color="#ffffff", lw=1.4, ls="--",
                label=f"fit: {a:.2f}·FI + {b:.0f}")
        r = np.corrcoef(fi, ce)[0, 1]
        ax.text(0.02, 0.97, f"Pearson r = {r:.3f}   n = {len(fi)}",
                transform=ax.transAxes, color=text_col, fontsize=10,
                va="top", fontfamily="monospace",
                bbox=dict(boxstyle="round,pad=0.35", fc=dark_bg,
                          ec=grid_col, lw=0.8))

    ax.set_xlabel("Fouling Index  Lab_FI (%)", color=text_col, fontsize=10)
    ax.set_ylabel(f"Coda energy  ∫|Hilbert env.| over {CODA_NS[0]:.0f}–{CODA_NS[1]:.0f} ns",
                  color=text_col, fontsize=10)
    ax.set_title(f"Coda energy vs Fouling Index  ({component})",
                 color=text_col, fontsize=12)
    ax.tick_params(colors=text_col, labelsize=8)
    ax.grid(True, color=grid_col, lw=0.4, alpha=0.5)
    for sp in ax.spines.values():
        sp.set_edgecolor(grid_col)
    ax.legend(fontsize=8, facecolor=panel_bg, labelcolor=text_col,
              edgecolor=grid_col, loc="upper right")

    fig.tight_layout()
    out_png = out_dir.parent / f"coda_energy_vs_fi_{component}.png"
    fig.savefig(out_png, dpi=150, bbox_inches="tight", facecolor=dark_bg)
    plt.close(fig)
    print(f"Samples plotted: {len(fi)}")
    print(f"Saved -> {out_png}")
    return out_png


def main():
    ap = argparse.ArgumentParser(description="Coda energy vs FI scatter")
    ap.add_argument("--dir", type=Path, default=Path("output/dataset_variants"))
    ap.add_argument("--component", default="Ez")
    ap.add_argument("--limit", type=int, default=2000,
                    help="Max samples to process (0 = all)")
    args = ap.parse_args()
    plot(args.dir.resolve(), args.component, args.limit)


if __name__ == "__main__":
    main()
