"""
Visualize a gprMax .out file as an A-scan with frequency spectrum.

Usage:
    python scripts/visualization/visualize_ascan.py output_test/angular_rocks_400MHz.out
    python scripts/visualization/visualize_ascan.py output_test/angular_rocks_400MHz.out --component Ez
"""
import sys
import argparse
from pathlib import Path

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
from src.data_loader import read_ascan
from src.signal_processing import compute_padded_spectrum
from src.file_reader import parse_metadata_file


def read_header_meta(in_path: Path) -> dict:
    """Extract ## comment metadata from the companion .in file (shared parser)."""
    if not in_path.exists():
        return {}
    return parse_metadata_file(in_path)


def visualize_ascan(out_path: Path, component: str = "Ez") -> Path:
    out_path = out_path.resolve()
    in_path  = out_path.with_suffix(".in")

    # --- Read A-scan trace (shared reader; handles B-scan trace selection) ---
    data = read_ascan(out_path, component)
    if data["component"] != component:
        print(f"[!] Component '{component}' not found. Available: {data['available']}")
    component  = data["component"]
    signal     = data["signal"]
    dt         = data["dt"]
    iterations = data["iterations"]
    rx_pos     = data["rx_pos"]
    ascan_idx  = data["ascan_idx"]
    t_ns       = data["t_ns"]    # time axis in nanoseconds

    # --- Frequency spectrum (shared padded-rFFT + peak) ---
    freqs, spectrum, peak_hz = compute_padded_spectrum(signal, dt)
    freq_ghz = freqs / 1e9
    peak_ghz = peak_hz / 1e9

    # --- Metadata from .in ---
    meta = read_header_meta(in_path)
    pvc       = meta.get("pvc", "?")
    fi_class  = meta.get("FI_class", "?")
    lab_class = meta.get("Lab_Class", "?")
    lab_fi    = meta.get("Lab_FI", "?")
    moisture  = meta.get("moisture", "?")
    bal_bot   = float(meta.get("ballast_bottom_y", 0))
    bal_top   = float(meta.get("ballast_top_y",   0))
    bulk_eps  = meta.get("Lab_bulk_eps", "?")
    surface_R = meta.get("Lab_surface_R", "?")
    clean_mm  = meta.get("Lab_clean_ballast_mm", "?")

    # two-way travel time to ballast interfaces (ns)
    c = 3e8
    eps_approx = 3.3   # typical dry ballast
    v = c / np.sqrt(eps_approx)
    tt_top = 2 * bal_top / v * 1e9
    tt_bot = 2 * bal_bot / v * 1e9

    # --- Figure layout ---
    fig = plt.figure(figsize=(12, 7))
    fig.patch.set_facecolor("#0f1117")
    gs = gridspec.GridSpec(2, 2, figure=fig, hspace=0.45, wspace=0.32,
                           left=0.07, right=0.97, top=0.88, bottom=0.10)

    dark_bg   = "#0f1117"
    panel_bg  = "#1a1e2b"
    accent    = "#00d4ff"
    accent2   = "#ff6b35"
    grid_col  = "#2a2f42"
    text_col  = "#c8d0e0"

    # --- Panel 1: Full A-scan ---
    ax1 = fig.add_subplot(gs[0, :])
    ax1.set_facecolor(panel_bg)
    ax1.plot(t_ns, signal, color=accent, lw=0.9, alpha=0.92)
    ax1.axhline(0, color=grid_col, lw=0.5)

    # mark ballast interfaces (approximate)
    for tt, lbl, col in [(tt_top, f"ballast top ~{bal_top:.2f} m", "#a0e070"),
                          (tt_bot, f"ballast bot ~{bal_bot:.2f} m", "#e07050")]:
        if 0 < tt < t_ns[-1]:
            ax1.axvline(tt, color=col, lw=1.0, ls="--", alpha=0.7)
            ax1.text(tt + 0.05, ax1.get_ylim()[1] * 0.92 if ax1.get_ylim()[1] != 0 else 1,
                     lbl, color=col, fontsize=7.5, va="top")

    ax1.set_xlabel("Two-way travel time  (ns)", color=text_col, fontsize=9)
    ax1.set_ylabel(f"{component}  (V/m)", color=text_col, fontsize=9)
    ax1.set_title(f"A-scan — {component}  |  {out_path.name}", color=text_col, fontsize=10)
    ax1.tick_params(colors=text_col, labelsize=8)
    for spine in ax1.spines.values():
        spine.set_edgecolor(grid_col)
    ax1.grid(True, color=grid_col, lw=0.5, alpha=0.6)

    # --- Panel 2: Frequency spectrum ---
    ax2 = fig.add_subplot(gs[1, 0])
    ax2.set_facecolor(panel_bg)
    fmax = min(2.0, freq_ghz[-1])
    mask = freq_ghz <= fmax
    ax2.fill_between(freq_ghz[mask], spectrum[mask], alpha=0.35, color=accent)
    ax2.plot(freq_ghz[mask], spectrum[mask], color=accent, lw=1.0)
    ax2.axvline(peak_ghz, color=accent2, lw=1.2, ls="--", label=f"peak {peak_ghz:.3f} GHz")
    ax2.axvline(0.4, color="#80e080", lw=1.0, ls=":", alpha=0.8, label="400 MHz")
    ax2.set_xlabel("Frequency  (GHz)", color=text_col, fontsize=9)
    ax2.set_ylabel("Amplitude", color=text_col, fontsize=9)
    ax2.set_title("Frequency Spectrum", color=text_col, fontsize=10)
    ax2.tick_params(colors=text_col, labelsize=8)
    ax2.legend(fontsize=8, facecolor=panel_bg, labelcolor=text_col, edgecolor=grid_col)
    for spine in ax2.spines.values():
        spine.set_edgecolor(grid_col)
    ax2.grid(True, color=grid_col, lw=0.5, alpha=0.6)

    # --- Panel 3: Metadata card ---
    ax3 = fig.add_subplot(gs[1, 1])
    ax3.set_facecolor(panel_bg)
    ax3.axis("off")
    for spine in ax3.spines.values():
        spine.set_edgecolor(grid_col)

    # rx Position attr is absent in some .out files (e.g. PINN4GPR) -> guard.
    if rx_pos[0] is not None and rx_pos[1] is not None:
        rx_str = f"Rx @ ({rx_pos[0]:.3f}, {rx_pos[1]:.3f}) m"
    else:
        rx_str = "Rx position n/a"
    if ascan_idx is not None:
        rx_str += f"  [B-scan trace {ascan_idx}]"

    lines = [
        ("Scenario", out_path.stem),
        ("Antenna", rx_str),
        ("dt", f"{dt*1e12:.1f} ps  |  {iterations} steps"),
        ("─" * 28, ""),
        ("PVC input",   f"{pvc}%"),
        ("Moisture",    f"{moisture}"),
        ("FI class (target)",  fi_class),
        ("Lab FI",      f"{lab_fi}%  [{lab_class}]"),
        ("─" * 28, ""),
        ("bulk eps (CRIM)", str(bulk_eps)),
        ("surface R",   str(surface_R)),
        ("clean ballast", f"{clean_mm} mm"),
        ("─" * 28, ""),
        ("Peak freq",   f"{peak_ghz:.3f} GHz"),
    ]

    y = 0.97
    for key, val in lines:
        if key.startswith("─"):
            ax3.plot([0.02, 0.98], [y - 0.01, y - 0.01], color=grid_col, lw=0.5,
                     transform=ax3.transAxes, clip_on=False)
            y -= 0.04
            continue
        ax3.text(0.03, y, f"{key}:", transform=ax3.transAxes,
                 color="#80a0c0", fontsize=8.5, va="top", fontfamily="monospace")
        ax3.text(0.48, y, val, transform=ax3.transAxes,
                 color=text_col, fontsize=8.5, va="top", fontfamily="monospace")
        y -= 0.072

    # --- Main title ---
    fig.suptitle(
        f"gprMax A-scan  |  {out_path.stem}  |  PVC={pvc}%  FI={lab_fi}% [{lab_class}]",
        color=text_col, fontsize=11, y=0.96,
    )

    out_png = out_path.with_name(out_path.stem + "_ascan.png")
    fig.savefig(out_png, dpi=150, bbox_inches="tight", facecolor=dark_bg)
    plt.close(fig)
    print(f"Saved -> {out_png}")
    return out_png


def main():
    ap = argparse.ArgumentParser(description="Visualize gprMax .out A-scan")
    ap.add_argument("out_file", type=Path, help="Path to .out file")
    ap.add_argument("--component", default="Ez",
                    help="Field component to plot (default: Ez)")
    args = ap.parse_args()
    visualize_ascan(args.out_file.resolve(), component=args.component)


if __name__ == "__main__":
    main()
