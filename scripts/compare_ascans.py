#!/usr/bin/env python3
"""Compare two A-scans: top row scan 1, middle row scan 2, bottom row overlay (time-matched)."""

import sys
from pathlib import Path
import struct
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.data_loader import read_ascan


def read_file(file_path: Path, trace_idx: int = 1000, component: str = "Ez") -> tuple:
    """
    Read A-scan from .out (synthetic) or .DZT (real) file.

    Returns:
        (signal, t_ns, dt_ns, metadata_str)
    """
    suffix = file_path.suffix.upper()

    if suffix == ".OUT":
        # Synthetic gprMax output
        data = read_ascan(file_path, component)
        signal = data['signal']
        dt = data['dt']
        t_ns = np.arange(len(signal)) * dt * 1e9
        meta_str = f"{file_path.stem} ({component})"
        return signal, t_ns, dt * 1e9, meta_str

    elif suffix == ".DZT" or suffix == ".DTZ":
        # Real DZT file (128 KiB header, int32 samples)
        HEADER_SIZE = 128 * 1024
        SAMPLES_PER_TRACE = 512
        BYTES_PER_SAMPLE = 4
        DT_NS = 50 / 511

        with open(file_path, 'rb') as f:
            f.seek(HEADER_SIZE + trace_idx * SAMPLES_PER_TRACE * BYTES_PER_SAMPLE)
            trace_bytes = f.read(SAMPLES_PER_TRACE * BYTES_PER_SAMPLE)
            signal = np.frombuffer(trace_bytes, dtype=np.int32, count=SAMPLES_PER_TRACE)
            signal = signal.astype(np.float64)

        # Drop indices 0-1
        signal = signal[2:]
        t_ns = np.arange(len(signal)) * DT_NS
        meta_str = f"DZT Trace #{trace_idx} — {file_path.stem[:30]}"
        return signal, t_ns, DT_NS, meta_str

    else:
        raise ValueError(f"Unsupported file type: {suffix}")


def plot_waveform(ax, signal, t_ns, title: str, unit: str = "V/m", color: str = "#00d4ff"):
    """Plot a single waveform on given axes."""
    ax.set_facecolor("#1a1e2b")

    # Plot signal
    ax.plot(t_ns, signal, color=color, lw=1.5, alpha=0.95)
    ax.axhline(0, color="#2a2f42", lw=1.0, linestyle='-', alpha=0.7)
    ax.fill_between(t_ns, signal, 0, alpha=0.15, color=color)

    # Find and mark peak
    peak_idx = np.argmax(np.abs(signal))
    peak_time = t_ns[peak_idx]
    peak_amp = signal[peak_idx]
    ax.plot(peak_time, peak_amp, color="#ff6b35", marker='o', markersize=8,
            markeredgewidth=2, markerfacecolor='none', zorder=5)
    ax.annotate(f'{peak_amp:.2e} @ {peak_time:.2f} ns',
                xy=(peak_time, peak_amp),
                xytext=(peak_time + 1, peak_amp * 0.7),
                fontsize=9, color="#ff6b35",
                bbox=dict(boxstyle='round,pad=0.4', facecolor='#1a1e2b',
                         edgecolor='#ff6b35', linewidth=1),
                arrowprops=dict(arrowstyle='->', color='#ff6b35', lw=1))

    # Labels
    ax.set_ylabel(f"Amplitude ({unit})", fontsize=10, color="#c8d0e0", fontweight='bold')
    ax.set_title(title, fontsize=11, color="#c8d0e0", fontweight='bold', pad=10)

    # Grid
    ax.grid(True, color="#2a2f42", lw=0.5, alpha=0.6, linestyle='-')
    ax.set_axisbelow(True)

    # Spines
    for spine in ax.spines.values():
        spine.set_color("#2a2f42")
        spine.set_linewidth(1)

    # Ticks
    ax.tick_params(colors="#c8d0e0", labelsize=9, width=1, length=5)

    # Stats box
    rms = np.sqrt(np.mean(signal**2))
    stats_text = (
        f"Samples: {len(signal):,}\n"
        f"Peak: {np.max(signal):.2e}\n"
        f"RMS: {rms:.2e}"
    )
    ax.text(0.98, 0.97, stats_text, transform=ax.transAxes,
            fontsize=8, verticalalignment='top', horizontalalignment='right',
            bbox=dict(boxstyle='round', facecolor='#1a1e2b', edgecolor=color,
                     linewidth=1, alpha=0.85),
            fontfamily='monospace', color="#c8d0e0")

    return peak_amp


def main():
    import argparse

    ap = argparse.ArgumentParser(
        description="Compare two A-scans: scan1 (top), scan2 (middle), overlay (bottom)")
    ap.add_argument("scan1", type=Path, help="First A-scan file (.out or .DZT)")
    ap.add_argument("scan2", type=Path, help="Second A-scan file (.out or .DZT)")
    ap.add_argument("--trace1", type=int, default=1000,
                    help="Trace index for DZT scan 1 (default: 1000)")
    ap.add_argument("--trace2", type=int, default=1000,
                    help="Trace index for DZT scan 2 (default: 1000)")
    ap.add_argument("--component", default="Ez",
                    help="Field component for synthetic files (default: Ez)")
    ap.add_argument("-o", "--output", type=Path, default=None,
                    help="Output PNG path (default: compare_scan1_scan2.png)")
    args = ap.parse_args()

    # Validate input files
    scan1_path = args.scan1.resolve()
    scan2_path = args.scan2.resolve()

    if not scan1_path.exists():
        print(f"[ERR] Scan 1 not found: {scan1_path}")
        sys.exit(1)
    if not scan2_path.exists():
        print(f"[ERR] Scan 2 not found: {scan2_path}")
        sys.exit(1)

    # Read scans
    print(f"[READ] Scan 1: {scan1_path.name}")
    sig1, t1_ns, dt1_ns, meta1 = read_file(scan1_path, trace_idx=args.trace1,
                                           component=args.component)
    unit1 = "V/m" if scan1_path.suffix.upper() == ".OUT" else "A/D counts"

    print(f"[READ] Scan 2: {scan2_path.name}")
    sig2, t2_ns, dt2_ns, meta2 = read_file(scan2_path, trace_idx=args.trace2,
                                           component=args.component)
    unit2 = "V/m" if scan2_path.suffix.upper() == ".OUT" else "A/D counts"

    # Get common time range (match time axis, no interpolation)
    t_min = max(t1_ns[0], t2_ns[0])
    t_max = min(t1_ns[-1], t2_ns[-1])
    print(f"[MATCH] Time range: {t_min:.2f}–{t_max:.2f} ns (common to both)")

    # Get indices for common time range
    idx1 = (t1_ns >= t_min) & (t1_ns <= t_max)
    idx2 = (t2_ns >= t_min) & (t2_ns <= t_max)

    sig1_matched = sig1[idx1]
    sig2_trimmed = sig2[idx2]
    t_common = t1_ns[idx1]  # Use scan1's time axis

    # Interpolate sig2 to match sig1's time grid (linear interpolation)
    from scipy.interpolate import interp1d
    f_interp = interp1d(t2_ns[idx2], sig2_trimmed, kind='linear',
                       bounds_error=False, fill_value='extrapolate')
    sig2_matched = f_interp(t_common)

    # Create figure (3 rows, 1 column)
    fig = plt.figure(figsize=(16, 12))
    fig.patch.set_facecolor("#0f1117")
    gs = gridspec.GridSpec(3, 1, figure=fig, hspace=0.4,
                           left=0.1, right=0.95, top=0.95, bottom=0.08)

    # Row 1: Scan 1
    ax1 = fig.add_subplot(gs[0])
    peak1 = plot_waveform(ax1, sig1, t1_ns, f"SCAN 1: {meta1}", unit=unit1, color="#00d4ff")
    ax1.set_xlabel("", fontsize=0)  # Hide x-label for non-bottom rows

    # Row 2: Scan 2
    ax2 = fig.add_subplot(gs[1])
    peak2 = plot_waveform(ax2, sig2, t2_ns, f"SCAN 2: {meta2}", unit=unit2, color="#ff6b35")
    ax2.set_xlabel("", fontsize=0)  # Hide x-label for non-bottom rows

    # Row 3: Overlay (time-matched, no transformation)
    ax3 = fig.add_subplot(gs[2])
    ax3.set_facecolor("#1a1e2b")

    # Plot both on common time axis
    ax3.plot(t_common, sig1_matched, color="#00d4ff", lw=1.5, alpha=0.85, label="Scan 1")
    ax3.plot(t_common, sig2_matched, color="#ff6b35", lw=1.3, alpha=0.7, label="Scan 2")
    ax3.axhline(0, color="#2a2f42", lw=1.0, linestyle='-', alpha=0.7)

    # Spines
    for spine in ax3.spines.values():
        spine.set_color("#2a2f42")
        spine.set_linewidth(1)

    # Grid
    ax3.grid(True, color="#2a2f42", lw=0.5, alpha=0.6, linestyle='-')
    ax3.set_axisbelow(True)

    # Labels
    ax3.set_xlabel("Time (ns)", fontsize=11, color="#c8d0e0", fontweight='bold')
    ax3.set_ylabel("Amplitude", fontsize=10, color="#c8d0e0", fontweight='bold')
    ax3.set_title("OVERLAY (Time-Matched, No Transformation)", fontsize=11,
                  color="#c8d0e0", fontweight='bold', pad=10)

    # Ticks
    ax3.tick_params(colors="#c8d0e0", labelsize=9, width=1, length=5)

    # Legend
    ax3.legend(fontsize=10, loc='upper right',
              facecolor='#1a1e2b', labelcolor='#c8d0e0', edgecolor='#2a2f42',
              framealpha=0.9)

    # Stats for overlay
    overlap_samples = len(sig1_matched)
    stats_text = (
        f"Common time: {t_min:.2f}–{t_max:.2f} ns\n"
        f"Overlaid samples: {overlap_samples:,}\n"
        f"Scan1 peak: {peak1:.2e}\n"
        f"Scan2 peak: {peak2:.2e}"
    )
    ax3.text(0.02, 0.97, stats_text, transform=ax3.transAxes,
            fontsize=9, verticalalignment='top', horizontalalignment='left',
            bbox=dict(boxstyle='round', facecolor='#1a1e2b', edgecolor='#80e080',
                     linewidth=1.5, alpha=0.9),
            fontfamily='monospace', color="#c8d0e0")

    # Main title
    fig.suptitle(
        f"A-scan Comparison: Time-Matched Overlay (No Transformation)",
        color="#c8d0e0", fontsize=14, fontweight='bold', y=0.98,
    )

    # Determine output path
    if args.output:
        out_png = args.output.with_suffix('.png')
    else:
        out_png = Path('output_test') / f"compare_{scan1_path.stem}_vs_{scan2_path.stem}.png"

    out_png.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_png, dpi=150, bbox_inches='tight', facecolor="#0f1117")
    plt.close(fig)

    print(f"\n[OK] Comparison saved -> {out_png}")
    print(f"\n{'='*70}")
    print("COMPARISON SUMMARY")
    print(f"{'='*70}")
    print(f"Scan 1: {meta1} ({unit1})")
    print(f"  Peak: {peak1:.4e} @ {t1_ns[np.argmax(np.abs(sig1))]:.2f} ns")
    print(f"  Samples: {len(sig1)}, Time: {t1_ns[-1]:.2f} ns")
    print(f"\nScan 2: {meta2} ({unit2})")
    print(f"  Peak: {peak2:.4e} @ {t2_ns[np.argmax(np.abs(sig2))]:.2f} ns")
    print(f"  Samples: {len(sig2)}, Time: {t2_ns[-1]:.2f} ns")
    print(f"\nOverlay (time-matched):")
    print(f"  Common time: {t_min:.2f}–{t_max:.2f} ns")
    print(f"  Overlaid samples: {overlap_samples:,}")


if __name__ == "__main__":
    main()
