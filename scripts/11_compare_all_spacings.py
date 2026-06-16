#!/usr/bin/env python3
"""
Step 11: Compare all 8 TX/RX spacing variants side-by-side.
Visualize direct wave correlation across the grid search.
"""

import sys
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import json

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.data_loader import read_ascan


def read_real_dzt(file_path: Path, trace_idx: int = 1000) -> tuple:
    """Read real DZT file."""
    HEADER_SIZE = 128 * 1024
    SAMPLES_PER_TRACE = 512
    BYTES_PER_SAMPLE = 4
    DT_NS = 50 / 511

    with open(file_path, 'rb') as f:
        f.seek(HEADER_SIZE + trace_idx * SAMPLES_PER_TRACE * BYTES_PER_SAMPLE)
        trace_bytes = f.read(SAMPLES_PER_TRACE * BYTES_PER_SAMPLE)
        signal = np.frombuffer(trace_bytes, dtype=np.int32, count=SAMPLES_PER_TRACE)
        signal = signal.astype(np.float64)

    signal = signal[2:]
    t_ns = np.arange(len(signal)) * DT_NS
    return signal, t_ns, DT_NS


def normalize_peak(signal):
    peak = np.max(np.abs(signal))
    return signal / peak if peak != 0 else signal


def apply_time_delay(signal, dt_ns, delay_ns):
    delay_samples = int(np.round(delay_ns / dt_ns))
    if delay_samples <= 0:
        return signal
    return np.concatenate([np.zeros(delay_samples), signal[:-delay_samples]])


def extract_direct_wave(signal, t_ns, delay_ns: float = 2.77, t_max: float = 12.0) -> tuple:
    dt_ns = t_ns[1] - t_ns[0] if len(t_ns) > 1 else 0.01
    signal_delayed = apply_time_delay(signal, dt_ns, delay_ns)
    signal_flipped = signal_delayed * -1
    signal_norm = normalize_peak(signal_flipped)

    idx = (t_ns >= 0) & (t_ns <= t_max)
    if np.sum(idx) < 10:
        return None, None, False

    return signal_norm[idx], t_ns[idx], True


def main():
    out_dir = Path("output_test/spacing_opt")
    real_dzt = Path("D:/Codigo/Data/PUERTO-LIMACHE_20230726_EFE_V1_PKC000_588_PKF011_020_CENTRO_BRUTO.DZT")

    # Load real direct wave
    print("[READ] Real DZT...")
    real_sig, real_t, _ = read_real_dzt(real_dzt, trace_idx=1000)
    real_dw, real_dw_t, _ = extract_direct_wave(real_sig, real_t, delay_ns=2.77, t_max=12.0)
    real_dw_norm = normalize_peak(real_dw)
    print(f"[OK] Real direct wave: {len(real_dw)} samples\n")

    # Load all spacing results
    results_file = out_dir / "spacing_results.json"
    with open(results_file) as f:
        results = json.load(f)

    # Extract synthetic direct waves from all .out files
    spacings = []
    correlations = []
    synthetics = []

    for res in results:
        spacing_mm = res['spacing_mm']
        out_file = Path(res['out_file'])

        if not out_file.exists():
            print(f"[SKIP] {spacing_mm:.0f}mm - .out file not found")
            continue

        try:
            data = read_ascan(out_file, component="Ez")
            syn_sig = data['signal']
            dt_syn = data['dt']
            t_syn = np.arange(len(syn_sig)) * dt_syn * 1e9

            syn_dw, syn_dw_t, success = extract_direct_wave(syn_sig, t_syn, delay_ns=2.77, t_max=12.0)
            if not success:
                continue

            syn_dw_norm = normalize_peak(syn_dw)
            syn_dw_interp = np.interp(real_dw_t, syn_dw_t, syn_dw_norm)

            corr = np.mean((syn_dw_interp - real_dw_norm) ** 2)  # Use normalized correlation
            s1 = (syn_dw_interp - np.mean(syn_dw_interp)) / (np.std(syn_dw_interp) + 1e-10)
            s2 = (real_dw_norm - np.mean(real_dw_norm)) / (np.std(real_dw_norm) + 1e-10)
            corr = np.mean(s1 * s2)

            spacings.append(spacing_mm)
            correlations.append(corr)
            synthetics.append((syn_dw_norm, syn_dw_t))

            print(f"[OK] {spacing_mm:3.0f}mm: corr={corr:+.6f}")

        except Exception as e:
            print(f"[ERR] {spacing_mm:.0f}mm: {str(e)[:60]}")

    if not spacings:
        print("[ERR] No results to plot")
        sys.exit(1)

    # Create comprehensive comparison figure
    import matplotlib.gridspec as gridspec
    fig = plt.figure(figsize=(20, 14))
    fig.patch.set_facecolor("#0f1117")
    gs = gridspec.GridSpec(4, 4, figure=fig, hspace=0.35, wspace=0.3)

    # Top: Correlation curve (spans top row)
    ax_curve = fig.add_subplot(gs[0, :])
    ax_curve.set_facecolor("#1a1e2b")
    ax_curve.plot(spacings, correlations, 'o-', color="#00ff88", lw=2.5, markersize=8, markeredgewidth=1, markeredgecolor="#c8d0e0")
    best_idx = np.argmax(correlations)
    ax_curve.plot(spacings[best_idx], correlations[best_idx], '*', color="#ffff00", markersize=25, markeredgewidth=2, markeredgecolor="#ff6b35")
    ax_curve.axhline(0, color="#2a2f42", lw=0.8, linestyle='-', alpha=0.3)
    ax_curve.grid(True, color="#2a2f42", lw=0.5, alpha=0.4)
    ax_curve.set_xlabel("TX/RX Spacing (mm)", fontsize=11, color="#c8d0e0", fontweight='bold')
    ax_curve.set_ylabel("Direct Wave Correlation", fontsize=11, color="#c8d0e0", fontweight='bold')
    ax_curve.set_title("Grid Search: TX/RX Spacing Optimization", fontsize=12, color="#c8d0e0", fontweight='bold')
    ax_curve.tick_params(colors="#c8d0e0", labelsize=9)
    for spine in ax_curve.spines.values():
        spine.set_color("#2a2f42")

    # Middle & Bottom: Direct wave waveforms for each spacing
    c_syn = "#00ff88"
    c_real = "#ff6b35"

    for i, (spacing_mm, corr, (syn_dw_norm, syn_dw_t)) in enumerate(zip(spacings, correlations, synthetics)):
        row = (i // 4) + 1
        col = i % 4
        ax = fig.add_subplot(gs[row, col])
        ax.set_facecolor("#1a1e2b")

        t_min, t_max = 0, 12
        idx_syn = (syn_dw_t >= t_min) & (syn_dw_t <= t_max)
        idx_real = (real_dw_t >= t_min) & (real_dw_t <= t_max)

        ax.plot(syn_dw_t[idx_syn], syn_dw_norm[idx_syn], color=c_syn, lw=2, alpha=0.85, label="Synthetic")
        ax.plot(real_dw_t[idx_real], real_dw_norm[idx_real], color=c_real, lw=2, alpha=0.75, label="Real")
        ax.axhline(0, color="#2a2f42", lw=0.8, linestyle='-', alpha=0.5)

        is_best = (spacing_mm == spacings[best_idx])
        title_color = "#ffff00" if is_best else "#c8d0e0"
        title_weight = "bold" if is_best else "normal"
        ax.set_title(f"{spacing_mm:.0f}mm (corr={corr:+.4f}){'  BEST' if is_best else ''}",
                    fontsize=10, color=title_color, fontweight=title_weight)

        ax.set_xlabel("Time (ns)", fontsize=9, color="#c8d0e0")
        ax.set_ylabel("Normalized Amplitude", fontsize=9, color="#c8d0e0")
        ax.grid(True, color="#2a2f42", lw=0.5, alpha=0.4)
        ax.set_xlim([t_min, t_max])
        ax.tick_params(colors="#c8d0e0", labelsize=8)

        if i == 0:
            ax.legend(loc='upper right', fontsize=9, facecolor='#1a1e2b', labelcolor='#c8d0e0', edgecolor='#2a2f42')

        for spine in ax.spines.values():
            spine.set_color("#2a2f42")

    fig.suptitle(
        f"Step 11: All 8 TX/RX Spacing Variants - Grid Search Results (Best: {spacings[best_idx]:.0f}mm @ {correlations[best_idx]:+.4f})",
        color="#c8d0e0", fontsize=13, fontweight='bold', y=0.98
    )

    out_png = Path("output_test/11_all_spacings_comparison.png")
    fig.savefig(out_png, dpi=150, bbox_inches='tight', facecolor="#0f1117")
    plt.close(fig)

    print(f"\n{'='*70}")
    print("GRID SEARCH SUMMARY")
    print(f"{'='*70}\n")

    for spacing_mm, corr in sorted(zip(spacings, correlations), key=lambda x: x[1], reverse=True):
        best_mark = " <-- BEST" if spacing_mm == spacings[best_idx] else ""
        print(f"  {spacing_mm:3.0f}mm: {corr:+.6f}{best_mark}")

    print(f"\n[BEST] Optimal spacing: {spacings[best_idx]:.0f}mm")
    print(f"       Correlation: {correlations[best_idx]:+.6f}")
    print(f"\n[SAVE] Comparison -> {out_png}")


if __name__ == "__main__":
    main()
