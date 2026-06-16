#!/usr/bin/env python3
"""
Ballast epsilon sweep with proper 50ns window.
Test epsilon values to find optimal material permittivity.
Uses direct wave alignment and full coda comparison.
"""

import sys
from pathlib import Path
import subprocess
import numpy as np
import json
import h5py
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy.interpolate import interp1d


def read_real_dzt(dzt_path: Path, trace_idx: int = 15000) -> tuple:
    """Read and cache real DZT trace."""
    HEADER_SIZE = 128 * 1024
    SAMPLES_PER_TRACE = 512
    BYTES_PER_SAMPLE = 4
    DT_NS = 50 / 511

    with open(dzt_path, 'rb') as f:
        f.seek(HEADER_SIZE + trace_idx * SAMPLES_PER_TRACE * BYTES_PER_SAMPLE)
        trace_bytes = f.read(SAMPLES_PER_TRACE * BYTES_PER_SAMPLE)
        signal = np.frombuffer(trace_bytes, dtype=np.int32, count=SAMPLES_PER_TRACE)
        signal = signal.astype(np.float64)

    signal = signal[2:]  # Drop indices 0-1
    t_ns = np.arange(len(signal)) * DT_NS
    return signal, t_ns, DT_NS


def read_synthetic_out(out_path: Path) -> tuple:
    """Read synthetic .out file."""
    with h5py.File(out_path, 'r') as f:
        signal = f['rxs/rx1/Ez'][()]
        dt = f.attrs.get('dt', 0.0)
    t_ns = np.arange(len(signal)) * dt * 1e9
    return signal, t_ns, dt * 1e9


def normalize_peak(signal):
    """Normalize by peak amplitude."""
    peak = np.max(np.abs(signal))
    if peak == 0:
        return signal
    return signal / peak


def find_direct_wave_peak(signal: np.ndarray, search_end_idx: int = None) -> int:
    """Find the peak index of the direct wave."""
    if search_end_idx is None:
        search_end_idx = len(signal)
    search_region = signal[:search_end_idx]
    return np.argmax(np.abs(search_region))


def align_and_correlate(syn_sig: np.ndarray, syn_t: np.ndarray, dt_syn: float,
                       real_sig: np.ndarray, real_t: np.ndarray, dt_real: float) -> float:
    """Align direct waves and compute correlation."""
    syn_flipped = -syn_sig

    search_ns = 20
    search_idx_syn = int(search_ns / dt_syn)
    search_idx_real = int(search_ns / dt_real)

    peak_idx_syn = find_direct_wave_peak(syn_flipped, min(search_idx_syn, len(syn_flipped)))
    peak_idx_real = find_direct_wave_peak(real_sig, min(search_idx_real, len(real_sig)))

    peak_time_syn = syn_t[peak_idx_syn]
    peak_time_real = real_t[peak_idx_real]

    time_shift_ns = peak_time_real - peak_time_syn
    syn_t_shifted = syn_t + time_shift_ns

    # Resample to common dt
    t_min = max(syn_t_shifted[0], real_t[0])
    t_max = min(syn_t_shifted[-1], real_t[-1])
    t_common = np.arange(int((t_max - t_min) / dt_real) + 1) * dt_real + t_min

    f_syn = interp1d(syn_t_shifted, syn_flipped, kind='cubic', bounds_error=False, fill_value=0)
    f_real = interp1d(real_t, real_sig, kind='cubic', bounds_error=False, fill_value=0)

    syn_common = f_syn(t_common)
    real_common = f_real(t_common)

    syn_norm = normalize_peak(syn_common)
    real_norm = normalize_peak(real_common)

    try:
        corr = np.corrcoef(syn_norm, real_norm)[0, 1]
        return float(corr)
    except:
        return np.nan


def create_ballast_toml(eps: float, output_path: Path) -> None:
    """Create TOML file with specified epsilon."""
    content = f"""# Ballast layer - Epsilon sweep (50ns window)
[job]
render = false

[sim]
freq_hz = 420e6
domain_x = 0.5
dx = 0.003
antenna_clearance = 0.05
air_buffer = 0.1
time_window = 5.0e-8
antenna_mode = "bistatic"
num_receivers = 1
receiver_spacing = 0.03
title = "420 MHz Ballast eps={eps}"

[source]
waveform = "gaussian"
amplitude = 1.0
polarization = "z"

[[layer]]
name = "air"
thickness = 0.05

[[layer]]
name = "ballast"
thickness = 0.3
eps = {eps}
sigma = 0.0
"""

    with open(output_path, 'w') as f:
        f.write(content)


def run_simulation(toml_path: Path, out_path: Path) -> bool:
    """Generate .in and run gprMax."""
    in_path = out_path.with_suffix('.in')

    # Generate .in
    result = subprocess.run(
        [sys.executable, 'scripts/pipeline/generate_in_files.py', str(toml_path), '-o', str(in_path)],
        capture_output=True, text=True, timeout=30
    )

    if result.returncode != 0:
        return False

    # Run gprMax
    gprmax_path = Path.home() / ".conda" / "envs" / "gprMax" / "python.exe"
    result = subprocess.run(
        [str(gprmax_path), '-m', 'gprMax', str(in_path)],
        capture_output=True, text=True, timeout=120
    )

    return result.returncode == 0 and out_path.exists()


def main():
    # Load real trace once
    dzt_path = Path("D:/Codigo/Data/PUERTO-LIMACHE_20230726_EFE_V1_PKC000_588_PKF011_020_CENTRO_BRUTO.DZT")
    print(f"[LOAD] Real trace: {dzt_path.name} (trace #15000)")
    real_sig, real_t, dt_real = read_real_dzt(dzt_path, trace_idx=15000)

    # Epsilon values to test - broader range for 50ns window
    epsilon_values = np.arange(2.5, 6.1, 0.2)
    epsilon_values = np.round(epsilon_values, 1)

    work_dir = Path("output_test/ballast_epsilon_sweep_50ns")
    work_dir.mkdir(parents=True, exist_ok=True)

    print(f"\n{'='*70}")
    print("BALLAST EPSILON SWEEP (50ns window, full coda)")
    print(f"{'='*70}")
    print(f"Testing {len(epsilon_values)} epsilon values: {epsilon_values[0]:.1f} to {epsilon_values[-1]:.1f}\n")

    results = []

    print(f"{'Epsilon':<10} {'Status':<15} {'Correlation':<15}")
    print("-" * 70)

    for eps in epsilon_values:
        print(f"{eps:<10.1f}", end=" ", flush=True)

        # Create TOML
        toml_path = work_dir / f"ballast_eps_{eps:.1f}.toml"
        create_ballast_toml(eps, toml_path)

        # Run simulation
        out_path = work_dir / f"ballast_eps_{eps:.1f}.out"
        if not run_simulation(toml_path, out_path):
            print("[FAIL]")
            continue

        # Compute correlation
        try:
            syn_sig, syn_t, dt_syn = read_synthetic_out(out_path)
            corr = align_and_correlate(syn_sig, syn_t, dt_syn, real_sig, real_t, dt_real)

            if np.isnan(corr):
                print("[ERR]")
            else:
                print(f"[OK]         {corr:>+10.6f}")
                results.append({'eps': eps, 'corr': corr})

        except Exception as e:
            print(f"[ERR] {str(e)[:30]}")

    if not results:
        print("[FAIL] No valid results")
        return 1

    # Sort and display
    results_sorted = sorted(results, key=lambda x: x['corr'], reverse=True)

    print(f"\n{'='*70}")
    print("RESULTS (sorted by correlation)")
    print(f"{'='*70}\n")

    print(f"{'Rank':<6} {'Epsilon':<12} {'Correlation':<15} {'Status'}")
    print("-" * 70)

    best_eps = results_sorted[0]['eps']
    best_corr = results_sorted[0]['corr']

    for i, r in enumerate(results_sorted, 1):
        marker = "[BEST]" if abs(r['eps'] - best_eps) < 0.01 else ""
        print(f"{i:<6} {r['eps']:<12.1f} {r['corr']:>+10.6f}       {marker}")

    print(f"\n{'='*70}")
    print(f"OPTIMAL EPSILON: {best_eps:.1f}")
    print(f"BEST CORRELATION: {best_corr:.6f}")
    print(f"{'='*70}\n")

    # Save results
    json_path = work_dir / "epsilon_sweep_results.json"
    with open(json_path, 'w') as f:
        json.dump(results_sorted, f, indent=2)

    print(f"[SAVE] {json_path}")

    # Plot
    fig, ax = plt.subplots(figsize=(14, 7))
    fig.patch.set_facecolor("#0f1117")
    ax.set_facecolor("#1a1e2b")

    eps_vals = [r['eps'] for r in results_sorted]
    corr_vals = [r['corr'] for r in results_sorted]

    # Scatter with color gradient
    scatter = ax.scatter(eps_vals, corr_vals, s=180, c=corr_vals, cmap='RdYlGn',
                        edgecolors='#c8d0e0', linewidth=2, alpha=0.85,
                        vmin=min(corr_vals)-0.01, vmax=max(corr_vals)+0.01)

    # Mark best
    ax.scatter([best_eps], [best_corr], s=500, marker='*', color='gold',
              edgecolors='white', linewidth=2, label=f'Best: eps={best_eps:.1f}', zorder=5)

    # Connect with line
    eps_sorted = sorted(eps_vals)
    corr_at_sorted = [next(r['corr'] for r in results_sorted if r['eps'] == e) for e in eps_sorted]
    ax.plot(eps_sorted, corr_at_sorted, 'c--', alpha=0.5, linewidth=2, label='Trend')

    # Reference line
    ax.axhline(0.9129, color='#ff6b35', linestyle=':', linewidth=1.5, alpha=0.6,
               label='Previous best (eps=3.45, 10ns window)')

    ax.set_xlabel("Epsilon (Ballast Permittivity)", fontsize=12, color="#c8d0e0", fontweight='bold')
    ax.set_ylabel("Correlation with Real Field GPR", fontsize=12, color="#c8d0e0", fontweight='bold')
    ax.set_title("Ballast Epsilon Optimization (420 MHz, 50ns window, full coda)",
                fontsize=13, color="#c8d0e0", fontweight='bold')

    ax.set_ylim([0.88, 0.93])
    ax.grid(True, color="#2a2f42", alpha=0.3, linestyle='--')
    ax.legend(fontsize=11, facecolor='#1a1e2b', labelcolor='#c8d0e0',
              edgecolor='#2a2f42', loc='lower right')
    ax.tick_params(colors="#c8d0e0", labelsize=10)

    for spine in ax.spines.values():
        spine.set_color("#2a2f42")
        spine.set_linewidth(1.5)

    cbar = plt.colorbar(scatter, ax=ax)
    cbar.set_label("Correlation", color="#c8d0e0", fontsize=10)
    cbar.ax.tick_params(colors="#c8d0e0")

    png_path = work_dir / "ballast_epsilon_sweep.png"
    fig.savefig(png_path, dpi=150, bbox_inches='tight', facecolor="#0f1117")
    print(f"[SAVE] {png_path}\n")

    return 0


if __name__ == "__main__":
    sys.exit(main())
