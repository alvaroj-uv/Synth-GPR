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
from scipy.signal import hilbert, find_peaks, spectrogram
from scipy.stats import skew, kurtosis

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
from src.data_loader import read_ascan
from src.signal_processing import compute_padded_spectrum
from src.file_reader import parse_metadata_file
from src.constants import SC


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

    # --- Frequency spectrum (computed from gated signal, after direct wave) ---
    # Will be computed after gating below

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

    # Extract antenna position and ballast bounds from metadata
    import re
    antenna_y = None
    subsurface_top = None
    ballast_top_y = None

    # Parse "Antenna position" = "y=0.800 m (above surface at 0.550 m)"
    antenna_line = meta.get("Antenna position", None)
    if antenna_line:
        try:
            match = re.search(r'y=([\d.]+)', antenna_line)
            if match:
                antenna_y = float(match.group(1))
        except:
            pass

    # Parse "Subsurface top" = "0.550 m    Total rocks: 216"
    subsurface_line = meta.get("Subsurface top", None)
    if subsurface_line:
        try:
            match = re.search(r'^([\d.]+)', subsurface_line)
            if match:
                subsurface_top = float(match.group(1))
        except:
            pass

    # Parse "Ballast layer" = "y=[0.300, 0.550] m  (packed rocks)"
    ballast_line = meta.get("Ballast layer", None)
    if ballast_line:
        try:
            match = re.search(r'y=\[([\d.]+),\s*([\d.]+)\]', ballast_line)
            if match:
                ballast_bottom_y = float(match.group(1))
                ballast_top_y = float(match.group(2))
        except:
            pass

    # Calculate direct wave arrival time
    if antenna_y and subsurface_top:
        antenna_height_above_surface = antenna_y - subsurface_top
        if antenna_height_above_surface > 0:
            direct_wave_time_ns = 2 * antenna_height_above_surface / c * 1e9
        else:
            direct_wave_time_ns = 1.5  # fallback
    else:
        direct_wave_time_ns = 1.5  # fallback to 1.5 ns

    # Surface reflection arrives at ballast top (use extracted ballast_top_y if available)
    if ballast_top_y:
        v = c / np.sqrt(eps_approx)
        surface_reflection_time_ns = 2 * ballast_top_y / v * 1e9
    else:
        surface_reflection_time_ns = tt_top if bal_top > 0 else 1.5

    # --- Figure layout: 6-panel comprehensive analysis ---
    fig = plt.figure(figsize=(18, 10))
    fig.patch.set_facecolor("#0f1117")
    gs = gridspec.GridSpec(3, 4, figure=fig, hspace=0.35, wspace=0.3,
                           left=0.06, right=0.98, top=0.92, bottom=0.08)

    dark_bg   = "#0f1117"
    panel_bg  = "#1a1e2b"
    accent    = "#00d4ff"
    accent2   = "#ff6b35"
    accent3   = "#80e080"
    grid_col  = "#2a2f42"
    text_col  = "#c8d0e0"

    # Gate signal to start after surface reflection (per Rojas-Vivanco: direct wave + 30 samples = surface)
    idx_after_surface = t_ns >= surface_reflection_time_ns
    signal_gated = signal.copy()
    signal_gated[~idx_after_surface] = 0  # Zero out pre-surface region
    t_ns_gated = t_ns[idx_after_surface]
    signal_gated_trimmed = signal_gated[idx_after_surface]

    # Coda/ballast gate window
    coda_win_ns = SC.CODA_WINDOW_NS  # (6.0, 16.0)

    # Approximate direct wave pulse width
    direct_wave_width = max(0.2, direct_wave_time_ns * 0.3)

    # --- Panel 1: Full A-scan (after direct wave, top row, span 3 cols) ---
    ax1 = fig.add_subplot(gs[0, :])
    ax1.set_facecolor(panel_bg)
    ax1.plot(t_ns_gated, signal_gated_trimmed, color=accent, lw=0.8, alpha=0.92)
    ax1.axhline(0, color=grid_col, lw=0.5)

    # Annotate physical features (relative to gated time axis)
    ax1.axvline(surface_reflection_time_ns, color=accent2, lw=2.0, linestyle='--', alpha=0.8, label=f'Surface reflection ({surface_reflection_time_ns:.2f}ns)')
    ax1.axvline(coda_win_ns[0], color='#ffd700', lw=1.5, linestyle=':', alpha=0.6, label=f'Ballast gate ({coda_win_ns[0]:.1f}-{coda_win_ns[1]:.1f}ns)')
    ax1.axvline(coda_win_ns[1], color='#ffd700', lw=1.5, linestyle=':', alpha=0.6)
    ax1.text(surface_reflection_time_ns+0.2, ax1.get_ylim()[1]*0.85, 'Surface', color=accent2, fontsize=8, fontweight='bold')
    ax1.text((coda_win_ns[0]+coda_win_ns[1])/2, ax1.get_ylim()[1]*0.75, 'Ballast\nGate', color='#ffd700', fontsize=7, fontweight='bold', ha='center')

    for spine in ax1.spines.values():
        spine.set_edgecolor(grid_col)
    ax1.set_xlabel("Time (ns)", color=text_col, fontsize=9)
    ax1.set_ylabel(f"{component} (V/m)", color=text_col, fontsize=9)
    ax1.set_title(f"A-scan (after direct wave {direct_wave_time_ns:.2f}ns) — {component}  [Surface reflection {surface_reflection_time_ns:.2f}ns | Ballast gate {coda_win_ns[0]:.1f}-{coda_win_ns[1]:.1f}ns]",
                  color=text_col, fontsize=10, fontweight='bold')
    ax1.tick_params(colors=text_col, labelsize=8)
    ax1.grid(True, color=grid_col, lw=0.5, alpha=0.6)
    ax1.legend(fontsize=8, facecolor=panel_bg, labelcolor=text_col, edgecolor=grid_col, loc='upper right')

    # --- Panel 2: Zoom on surface-to-ballast gate transition (post-DW) ---
    ax2 = fig.add_subplot(gs[1, 0])
    ax2.set_facecolor(panel_bg)
    # Show region from surface reflection to mid-ballast gate
    idx_zoom = (t_ns_gated >= surface_reflection_time_ns) & (t_ns_gated <= (coda_win_ns[0] + coda_win_ns[1])/2)
    if idx_zoom.any():
        ax2.plot(t_ns_gated[idx_zoom], signal_gated_trimmed[idx_zoom], color=accent, lw=1.0)

    # Mark surface reflection and ballast gate regions
    ax2.axvline(surface_reflection_time_ns, color=accent2, lw=1.5, linestyle='--', alpha=0.7)
    ax2.axvline(coda_win_ns[0], color='#ffd700', lw=1.5, linestyle=':', alpha=0.6)
    ax2.text(surface_reflection_time_ns+0.05, ax2.get_ylim()[1]*0.8, 'Surface', color=accent2, fontsize=7, fontweight='bold')
    ax2.text(coda_win_ns[0]+0.1, ax2.get_ylim()[1]*0.6, 'Ballast\ngate', color='#ffd700', fontsize=7, fontweight='bold')

    # Mark peaks in this window
    if idx_zoom.any():
        peaks, props = find_peaks(np.abs(signal_gated_trimmed[idx_zoom]), height=np.std(signal_gated_trimmed)*1.5)
        if len(peaks) > 0:
            peak_times = t_ns_gated[idx_zoom][peaks]
            peak_vals = signal_gated_trimmed[idx_zoom][peaks]
            ax2.plot(peak_times, peak_vals, color=accent2, marker='*', markersize=10, linestyle='none')
    for spine in ax2.spines.values():
        spine.set_edgecolor(grid_col)
    ax2.set_xlabel("Time (ns)", color=text_col, fontsize=8)
    ax2.set_ylabel(f"{component} (V/m)", color=text_col, fontsize=8)
    ax2.set_title(f"Transition Zone ({surface_reflection_time_ns:.2f}-{coda_win_ns[0]:.1f} ns)", color=text_col, fontsize=9)
    ax2.tick_params(colors=text_col, labelsize=7)
    ax2.grid(True, color=grid_col, lw=0.4, alpha=0.5)

    # --- Panel 2b: Ballast/Coda Window (6-16 ns, fouling-sensitive) ---
    ax2b = fig.add_subplot(gs[1, 2])
    ax2b.set_facecolor(panel_bg)
    idx_coda = (t_ns >= coda_win_ns[0]) & (t_ns <= coda_win_ns[1])
    if idx_coda.any():
        ax2b.plot(t_ns[idx_coda], signal[idx_coda], color=accent, lw=1.5)
        # Mark peaks in coda window
        peaks_coda, _ = find_peaks(np.abs(signal[idx_coda]), height=np.std(signal)*1.5)
        if len(peaks_coda) > 0:
            peak_times_coda = t_ns[idx_coda][peaks_coda]
            peak_vals_coda = signal[idx_coda][peaks_coda]
            ax2b.plot(peak_times_coda, peak_vals_coda, color=accent2, marker='o', markersize=6, linestyle='none')
    for spine in ax2b.spines.values():
        spine.set_edgecolor(grid_col)
    ax2b.set_xlabel("Time (ns)", color=text_col, fontsize=8)
    ax2b.set_ylabel(f"{component} (V/m)", color=text_col, fontsize=8)
    ax2b.set_title(f"Ballast/Coda Gate ({coda_win_ns[0]:.1f}-{coda_win_ns[1]:.1f} ns)", color=accent2, fontsize=9, fontweight='bold')
    ax2b.tick_params(colors=text_col, labelsize=7)
    ax2b.grid(True, color=grid_col, lw=0.4, alpha=0.5)

    # --- Frequency spectrum (computed from gated signal, after direct wave) ---
    freqs, spectrum, peak_hz = compute_padded_spectrum(signal_gated_trimmed, dt)
    freq_ghz = freqs / 1e9
    peak_ghz = peak_hz / 1e9

    # --- Panel 3: Hilbert envelope (Rojas-Vivanco methodology) ---
    ax3 = fig.add_subplot(gs[1, 1])
    ax3.set_facecolor(panel_bg)
    # Per Rojas-Vivanco: normalize post-DW signal to max value THEN compute Hilbert
    signal_max = np.max(np.abs(signal_gated_trimmed))
    if signal_max > 0:
        signal_normalized = signal_gated_trimmed / signal_max  # Normalize to [0, 1]
    else:
        signal_normalized = signal_gated_trimmed.copy()
    # Compute Hilbert transform on CLEAN, NORMALIZED, post-DW-only signal
    analytic = hilbert(signal_normalized)
    envelope = np.abs(analytic)
    # Plot normalized signal with envelope
    ax3.plot(t_ns_gated, signal_normalized, color=accent, lw=0.5, alpha=0.6, label='Signal (normalized)')
    ax3.plot(t_ns_gated, envelope, color=accent2, lw=1.2, label='Envelope (Hilbert)')
    ax3.plot(t_ns_gated, -envelope, color=accent2, lw=0.8, linestyle='--', alpha=0.5)
    for spine in ax3.spines.values():
        spine.set_edgecolor(grid_col)
    ax3.set_xlabel(f"Time (ns, from {direct_wave_time_ns:.2f}ns)", color=text_col, fontsize=8)
    ax3.set_ylabel("Amplitude (V/m)", color=text_col, fontsize=8)
    ax3.set_title(f"Hilbert Envelope (post-DW only, {len(signal_gated_trimmed)} samples)", color=text_col, fontsize=9)
    # Set x-axis limits to match actual data (post-DW only)
    if len(t_ns_gated) > 0:
        ax3.set_xlim(t_ns_gated[0], t_ns_gated[-1])
    ax3.tick_params(colors=text_col, labelsize=7)
    ax3.legend(fontsize=7, facecolor=panel_bg, labelcolor=text_col, edgecolor=grid_col, loc='upper right')
    ax3.grid(True, color=grid_col, lw=0.4, alpha=0.5)

    # --- Panel 4: Frequency spectrum (log scale) ---
    ax4 = fig.add_subplot(gs[1, 3])
    ax4.set_facecolor(panel_bg)
    fmax = min(3.0, freq_ghz[-1])
    mask = freq_ghz <= fmax
    ax4.semilogy(freq_ghz[mask], spectrum[mask], color=accent, lw=1.0)
    ax4.fill_between(freq_ghz[mask], spectrum[mask], alpha=0.2, color=accent)
    ax4.axvline(peak_ghz, color=accent2, lw=1.2, ls='--', label=f'{peak_ghz:.2f} GHz')
    for spine in ax4.spines.values():
        spine.set_edgecolor(grid_col)
    ax4.set_xlabel("Frequency (GHz)", color=text_col, fontsize=8)
    ax4.set_ylabel("Magnitude", color=text_col, fontsize=8)
    ax4.set_title("Frequency Spectrum (log)", color=text_col, fontsize=9)
    ax4.tick_params(colors=text_col, labelsize=7)
    ax4.legend(fontsize=7, facecolor=panel_bg, labelcolor=text_col, edgecolor=grid_col)
    ax4.grid(True, color=grid_col, lw=0.4, alpha=0.5, which='both')

    # --- Panel 5: Spectrogram (from gated signal, after direct wave) ---
    ax5 = fig.add_subplot(gs[2, :3])
    ax5.set_facecolor(panel_bg)
    f, t_spec, Sxx = spectrogram(signal_gated_trimmed, fs=1/dt, nperseg=512, noverlap=256)
    t_spec = t_spec + direct_wave_time_ns  # Shift time axis to match gated window
    pcm = ax5.pcolormesh(t_spec*1e9, f/1e9, 10*np.log10(Sxx+1e-12), shading='auto', cmap='viridis')
    ax5.set_ylabel("Frequency (GHz)", color=text_col, fontsize=8)
    ax5.set_xlabel("Time (ns)", color=text_col, fontsize=8)
    ax5.set_title("Spectrogram (Time-Frequency)", color=text_col, fontsize=9)
    ax5.tick_params(colors=text_col, labelsize=7)
    ax5.set_ylim([0, 3])
    cbar = plt.colorbar(pcm, ax=ax5, label='Power (dB)')
    cbar.set_label('Power (dB)', color=text_col, fontsize=8)
    cbar.ax.tick_params(colors=text_col, labelsize=7)

    # --- Panel 6: Statistics & Metadata ---
    ax6 = fig.add_subplot(gs[2, 3])
    ax6.set_facecolor(panel_bg)
    ax6.axis("off")
    for spine in ax6.spines.values():
        spine.set_edgecolor(grid_col)

    # Build statistics text (from gated signal, after direct wave)
    rms = np.sqrt(np.mean(signal_gated_trimmed**2))
    peaks_gated, _ = find_peaks(np.abs(signal_gated_trimmed), height=np.std(signal_gated_trimmed)*2)
    n_peaks = len(peaks_gated)

    if rx_pos[0] is not None and rx_pos[1] is not None:
        rx_str = f"({rx_pos[0]:.3f}, {rx_pos[1]:.3f}) m"
    else:
        rx_str = "n/a"

    stats_lines = [
        ("TIMING (computed)", ""),
        ("Direct wave", f"0.0-{direct_wave_time_ns:.2f} ns"),
        ("Surface hit", f"~{surface_reflection_time_ns:.2f} ns"),
        ("Ballast gate", f"{coda_win_ns[0]:.1f}-{coda_win_ns[1]:.1f} ns"),
        ("─" * 25, ""),
        ("SIGNAL METRICS (post-DW)", ""),
        ("Duration", f"{t_ns_gated[-1]:.2f} ns"),
        ("Samples", f"{len(signal_gated_trimmed):,}"),
        ("Peak", f"{np.max(signal_gated_trimmed):.0f} V/m"),
        ("RMS", f"{rms:.0f} V/m"),
        ("Peaks found", f"{n_peaks}"),
        ("─" * 25, ""),
        ("FREQUENCY", ""),
        ("Dom. Freq", f"{peak_ghz:.2f} GHz"),
        ("BW est.", "~1-2 GHz"),
        ("─" * 25, ""),
        ("METADATA", ""),
        ("File", out_path.stem[:15]),
        ("PVC", f"{pvc}%"),
        ("Lab FI", f"{lab_fi}% [{lab_class}]"),
    ]

    y = 0.98
    for key, val in stats_lines:
        if key.startswith("SIGNAL") or key.startswith("─"):
            if key.startswith("SIGNAL"):
                ax6.text(0.05, y, key, transform=ax6.transAxes,
                        color=accent2, fontsize=8, fontweight='bold', va="top", fontfamily="monospace")
            y -= 0.05
            continue
        ax6.text(0.05, y, f"{key}", transform=ax6.transAxes,
                color="#80a0c0", fontsize=7.5, va="top", fontfamily="monospace")
        ax6.text(0.65, y, val, transform=ax6.transAxes,
                color=text_col, fontsize=7.5, va="top", fontfamily="monospace", ha="right")
        y -= 0.052

    # --- Main title ---
    fig.suptitle(
        f"gprMax A-scan — Comprehensive Analysis  |  {out_path.stem}  |  PVC={pvc}%  FI={lab_fi}% [{lab_class}]",
        color=text_col, fontsize=12, fontweight='bold', y=0.965,
    )

    out_png = out_path.with_name(out_path.stem + "_ascan_analysis.png")
    fig.savefig(out_png, dpi=150, bbox_inches="tight", facecolor=dark_bg)
    plt.close(fig)
    print(f"[OK] Comprehensive A-scan analysis saved -> {out_png}")
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
