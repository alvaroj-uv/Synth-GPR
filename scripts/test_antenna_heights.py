#!/usr/bin/env python3
"""
Test multiple antenna heights to find optimal coupling with real field data.
Sweeps antenna_clearance [0.02-0.6m] → antenna heights [1-30cm].
"""

import sys
from pathlib import Path
import subprocess
import numpy as np
import json
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

sys.path.insert(0, str(Path(__file__).parent.parent))

from scipy.interpolate import interp1d

try:
    from src.data_loader import read_ascan
except ImportError:
    # Fallback: read HDF5 directly
    import h5py
    def read_ascan(path, component='Ez'):
        with h5py.File(path, 'r') as f:
            signal = f['rxs/rx1/' + component][()]
            dt = f.attrs.get('dt', 0.0)
        return {'signal': signal, 'dt': dt}


def read_real_dzt(dzt_path: Path, trace_idx: int = 1000) -> tuple:
    """Read real DZT trace."""
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


def normalize_peak(signal):
    """Normalize by peak amplitude."""
    peak = np.max(np.abs(signal))
    if peak == 0:
        return signal
    return signal / peak


def create_toml_for_height(antenna_clearance: float, output_path: Path) -> None:
    """Create TOML file with specified antenna height."""
    antenna_height_cm = antenna_clearance * 0.5 * 100  # Convert to cm

    toml_content = f"""# Test: Antenna height {antenna_height_cm:.1f} cm
# antenna_clearance = {antenna_clearance}
[sim]
freq_hz = 420e6
domain_x = 0.5
dx = 0.003
antenna_clearance = {antenna_clearance}
air_buffer = 0.1
time_window = 5.0e-8
antenna_mode = "bistatic"
num_receivers = 1
receiver_spacing = 0.03
title = "420 MHz Gaussian Bistatic - Height {antenna_height_cm:.1f}cm"

[source]
waveform = "gaussian"
amplitude = 1.0
polarization = "z"

[[layer]]
name = "air"
thickness = 0.5
"""

    with open(output_path, 'w') as f:
        f.write(toml_content)


def run_simulation(toml_path: Path, out_path: Path) -> bool:
    """Generate .in file and run gprMax."""
    # Generate .in file
    in_path = out_path.with_suffix('.in')
    result = subprocess.run(
        [sys.executable, 'scripts/pipeline/generate_in_files.py', str(toml_path), '-o', str(in_path)],
        capture_output=True, text=True, timeout=30, cwd='.'
    )

    if result.returncode != 0:
        print(f"  [FAIL gen] {result.stderr[:150]}")
        return False

    if not in_path.exists():
        print(f"  [FAIL] .in file not created: {in_path}")
        return False

    # Run gprMax
    gprmax_path = Path.home() / ".conda" / "envs" / "gprMax" / "python.exe"
    result = subprocess.run(
        [str(gprmax_path), '-m', 'gprMax', str(in_path)],
        capture_output=True, text=True, timeout=120
    )

    if result.returncode != 0:
        print(f"  [FAIL gprMax] {result.stderr[:150]}")
        return False

    if not out_path.exists():
        print(f"  [FAIL] .out file not created: {out_path}")
        return False

    return True


def compute_correlation(out_path: Path, real_sig: np.ndarray, real_t: np.ndarray,
                       dt_real: float) -> float:
    """Load synthetic, resample, and compute correlation with real."""
    try:
        data = read_ascan(out_path, 'Ez')
        syn_sig = data['signal']
        syn_dt = data['dt']

        # Polarity flip
        syn_flipped = -syn_sig

        # Resample
        syn_t = np.arange(len(syn_flipped)) * syn_dt
        t_min = 0
        t_max = min(syn_t[-1], real_t[-1])
        t_common = np.arange(int(t_max / dt_real) + 1) * dt_real

        f_syn = interp1d(syn_t, syn_flipped, kind='cubic', bounds_error=False, fill_value=0)
        f_real = interp1d(real_t, real_sig, kind='cubic', bounds_error=False, fill_value=0)

        syn_rs = f_syn(t_common)
        real_rs = f_real(t_common)

        # Normalize
        syn_norm = normalize_peak(syn_rs)
        real_norm = normalize_peak(real_rs)

        # Correlate
        corr = np.corrcoef(syn_norm, real_norm)[0, 1]
        return float(corr)

    except Exception as e:
        print(f"  [ERR] Correlation computation: {str(e)[:100]}")
        return np.nan


def main():
    import argparse

    ap = argparse.ArgumentParser(description="Test multiple antenna heights")
    ap.add_argument("real_dzt", type=Path, help="Real DZT file")
    ap.add_argument("--trace", type=int, default=15000, help="DZT trace index")
    ap.add_argument("-o", "--output", type=Path, default=None, help="Output JSON/PNG")
    args = ap.parse_args()

    if not args.real_dzt.exists():
        print(f"[ERR] Real DZT not found: {args.real_dzt}")
        return 1

    # Load real data once
    print(f"[READ] Real DZT: {args.real_dzt.name} (trace #{args.trace})")
    real_sig, real_t, dt_real = read_real_dzt(args.real_dzt, trace_idx=args.trace)
    real_norm = normalize_peak(real_sig)

    # Test heights
    antenna_clearances = [0.02, 0.05, 0.1, 0.15, 0.2, 0.3, 0.4, 0.6]
    antenna_heights_cm = [ac * 0.5 * 100 for ac in antenna_clearances]

    results = []
    output_dir = Path("output_test/antenna_height_sweep")
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"\n{'='*70}")
    print("ANTENNA HEIGHT SWEEP TEST")
    print(f"{'='*70}")
    print(f"Testing {len(antenna_clearances)} antenna heights...")
    print(f"Heights: {', '.join([f'{h:.1f}cm' for h in antenna_heights_cm])}\n")

    for i, (ac, h_cm) in enumerate(zip(antenna_clearances, antenna_heights_cm), 1):
        print(f"[{i}/{len(antenna_clearances)}] Height {h_cm:.1f}cm (clearance {ac}m)...", end=" ", flush=True)

        # Create TOML
        toml_path = output_dir / f"height_{h_cm:.1f}cm.toml"
        create_toml_for_height(ac, toml_path)

        # Run simulation
        out_path = output_dir / f"height_{h_cm:.1f}cm.out"
        if not run_simulation(toml_path, out_path):
            print("[FAIL]")
            continue

        # Compute correlation
        corr = compute_correlation(out_path, real_norm, real_t, dt_real)

        if np.isnan(corr):
            print("[ERR]")
            continue

        status = "[OK]" if not np.isnan(corr) else "[FAIL]"
        print(f"{status} corr={corr:.6f}")

        results.append({
            'height_cm': h_cm,
            'antenna_clearance': ac,
            'correlation': corr,
            'output': str(out_path)
        })

    if not results:
        print("[FAIL] No results generated")
        return 1

    # Sort by correlation
    results_sorted = sorted(results, key=lambda x: x['correlation'], reverse=True)

    print(f"\n{'='*70}")
    print("RESULTS (sorted by correlation)")
    print(f"{'='*70}")
    print(f"{'Height':<12} {'Clearance':<12} {'Correlation':<15} {'Status':<10}")
    print("-" * 70)

    best_height = results_sorted[0]['height_cm']
    best_corr = results_sorted[0]['correlation']

    for r in results_sorted:
        marker = "***" if abs(r['height_cm'] - best_height) < 0.1 else "   "
        status = "[BEST]" if abs(r['height_cm'] - best_height) < 0.1 else ""
        print(f"{r['height_cm']:>6.1f} cm    {r['antenna_clearance']:>6.3f} m     {r['correlation']:>+10.6f}    {status:<10} {marker}")

    # Save JSON
    json_path = (args.output or Path("output_test")) / "antenna_height_sweep_results.json"
    json_path.parent.mkdir(parents=True, exist_ok=True)

    with open(json_path, 'w') as f:
        json.dump(results_sorted, f, indent=2)

    print(f"\n[SAVE] Results: {json_path}")

    # Plot
    heights = [r['height_cm'] for r in results_sorted]
    corrs = [r['correlation'] for r in results_sorted]

    fig, ax = plt.subplots(figsize=(12, 6))
    fig.patch.set_facecolor("#0f1117")
    ax.set_facecolor("#1a1e2b")

    # Plot scatter
    scatter = ax.scatter(heights, corrs, s=100, c=corrs, cmap='RdYlGn',
                        edgecolors='#c8d0e0', linewidth=2, alpha=0.8)

    # Mark best
    ax.scatter([best_height], [best_corr], s=300, marker='*', color='gold',
              edgecolors='#c8d0e0', linewidth=2, label=f'Best: {best_height:.1f}cm')

    # Lines connecting
    ax.plot(heights, corrs, 'c--', alpha=0.3, linewidth=1)

    ax.axhline(0, color='#2a2f42', linestyle='-', linewidth=0.8, alpha=0.5)
    ax.set_xlabel("Antenna Height (cm)", fontsize=11, color="#c8d0e0", fontweight='bold')
    ax.set_ylabel("Correlation with Real Field GPR", fontsize=11, color="#c8d0e0", fontweight='bold')
    ax.set_title("Antenna Height Optimization (420 MHz Gaussian Bistatic)",
                fontsize=12, color="#c8d0e0", fontweight='bold')

    ax.grid(True, color="#2a2f42", alpha=0.3)
    ax.legend(fontsize=10, facecolor='#1a1e2b', labelcolor='#c8d0e0', edgecolor='#2a2f42')
    ax.tick_params(colors="#c8d0e0")

    for spine in ax.spines.values():
        spine.set_color("#2a2f42")

    cbar = plt.colorbar(scatter, ax=ax)
    cbar.set_label("Correlation", color="#c8d0e0")
    cbar.ax.tick_params(colors="#c8d0e0")

    png_path = json_path.with_stem("antenna_height_sweep").with_suffix('.png')
    fig.savefig(png_path, dpi=150, bbox_inches='tight', facecolor="#0f1117")
    plt.close(fig)

    print(f"[SAVE] Plot: {png_path}")

    print(f"\n{'='*70}")
    print(f"OPTIMAL HEIGHT: {best_height:.1f} cm (clearance: {results_sorted[0]['antenna_clearance']:.3f} m)")
    print(f"CORRELATION: {best_corr:.6f}")
    print(f"{'='*70}\n")

    return 0


if __name__ == "__main__":
    sys.exit(main())
