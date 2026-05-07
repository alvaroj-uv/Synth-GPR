from __future__ import annotations
from typing import Optional

import numpy as np
from matplotlib.axes import Axes


def draw_grading_curve(ax: Axes, psd_data: Optional[list]) -> None:
    """
    Draw a geotechnical particle-size distribution curve.

    psd_data: list of [diameter_mm, percent_passing] pairs, as stored in
              SceneData.meta['Lab_PSD'] by LabWorker.
    Adds zone shading (fines / sand / gravel), sieve lines, and a D10/D30/D60
    stats box.
    """
    if not psd_data:
        ax.text(0.5, 0.5, "No PSD data", ha="center", va="center", fontsize=9)
        ax.axis("off")
        return

    points = sorted(psd_data, key=lambda p: p[0])
    sizes_mm = np.array([p[0] for p in points])
    passing  = np.array([p[1] for p in points])

    ax.semilogx(sizes_mm, passing, "b-o", linewidth=2, markersize=5,
                label="Grading curve")

    ax.set_title("Particle Size Distribution", fontweight="bold")
    ax.set_xlabel("Particle diameter (mm)")
    ax.set_ylabel("Percent finer (%)")
    ax.set_ylim(0, 100)
    ax.set_xlim(0.001, 100)
    ax.grid(True, which="major", linestyle="-",  linewidth=0.7, alpha=0.7)
    ax.grid(True, which="minor", linestyle=":",  linewidth=0.4, alpha=0.4)

    # Zone shading
    ax.axvspan(0.001,  0.075, color="#E0E0E0", alpha=0.5)
    ax.axvspan(0.075,  4.75,  color="#FFF9C4", alpha=0.5)
    ax.axvspan(4.75,  100,   color="#FFE0B2", alpha=0.5)
    ax.text(0.005, 5, "Fines",  fontsize=8, color="#666666", rotation=90)
    ax.text(0.2,   5, "Sand",   fontsize=8, color="#666666")
    ax.text(10,    5, "Gravel", fontsize=8, color="#666666")

    # Sieve lines
    ax.axvline(4.75,  color="k", linestyle="--", linewidth=0.8)
    ax.axvline(0.075, color="k", linestyle="--", linewidth=0.8)

    # D-values and uniformity coefficients
    d10 = float(np.interp(10, passing, sizes_mm))
    d30 = float(np.interp(30, passing, sizes_mm))
    d60 = float(np.interp(60, passing, sizes_mm))
    cu  = d60 / d10           if d10 > 0           else 0.0
    cc  = d30**2 / (d10*d60) if d10 * d60 > 0     else 0.0

    stats = (f"$D_{{10}}$ = {d10:.3f} mm\n"
             f"$D_{{30}}$ = {d30:.3f} mm\n"
             f"$D_{{60}}$ = {d60:.3f} mm\n"
             f"$C_u$ = {cu:.2f}\n"
             f"$C_c$ = {cc:.2f}")
    ax.text(0.02, 0.95, stats, transform=ax.transAxes, fontsize=9, va="top",
            bbox=dict(boxstyle="round", facecolor="white", alpha=0.9, edgecolor="gray"))

    ax.legend(loc="lower right", fontsize="small")
