#!/usr/bin/env python3
"""
Step 9: Use metaheuristic (grid search) to optimize RX/TX spacing and antenna parameters
to match the direct pulse in real DZT data.

Strategy:
- Vary TX/RX spacing, antenna height, and other coupling parameters
- For each config, generate gprMax .in file and run simulation
- Extract direct wave (0-12 ns) from synthetic
- Compare correlation with real direct wave
- Track and report best-matching configuration
"""

import sys
from pathlib import Path
import numpy as np
import subprocess
import json
from itertools import product
from scipy.signal import hilbert

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

    signal = signal[2:]  # Drop indices 0-1
    t_ns = np.arange(len(signal)) * DT_NS
    return signal, t_ns, DT_NS


def normalize_peak(signal):
    """Normalize by peak amplitude."""
    peak = np.max(np.abs(signal))
    if peak == 0:
        return signal
    return signal / peak


def apply_time_delay(signal, dt_ns, delay_ns):
    """Apply time delay."""
    delay_samples = int(np.round(delay_ns / dt_ns))
    if delay_samples <= 0:
        return signal
    return np.concatenate([np.zeros(delay_samples), signal[:-delay_samples]])


def compute_correlation(sig1, sig2):
    """Compute normalized cross-correlation."""
    if len(sig1) != len(sig2):
        min_len = min(len(sig1), len(sig2))
        sig1 = sig1[:min_len]
        sig2 = sig2[:min_len]

    sig1_norm = (sig1 - np.mean(sig1)) / (np.std(sig1) + 1e-10)
    sig2_norm = (sig2 - np.mean(sig2)) / (np.std(sig2) + 1e-10)

    return np.mean(sig1_norm * sig2_norm)


def generate_toml_config(tx_rx_spacing: float, antenna_height: float, domain_x: float,
                        freq_hz: float = 400e6, dx: float = 0.003, time_window: float = 5e-8) -> str:
    """
    Generate TOML config for gprMax with specified RX/TX spacing and antenna height.

    Parameters:
    - tx_rx_spacing: distance between TX and RX antennas (meters)
    - antenna_height: antenna clearance above ground (meters)
    - domain_x: domain size in x-direction (meters)
    """

    toml = f"""# Auto-generated optimization config
# TX/RX spacing: {tx_rx_spacing*1000:.2f} mm
# Antenna height: {antenna_height*1000:.2f} mm

[sim]
freq_hz = {freq_hz}
domain_x = {domain_x}
dx = {dx}
antenna_clearance = {antenna_height}
air_buffer = 0.1
time_window = {time_window}
title = "Optimized Antenna Config - spacing={tx_rx_spacing*1000:.1f}mm, height={antenna_height*1000:.1f}mm"

[source]
waveform = "ricker"
amplitude = 1.0
polarization = "z"

# Air layer (free space)
[[layer]]
name = "air"
thickness = 0.5
"""
    return toml


def run_gprmax_simulation(toml_content: str, toml_file: Path, in_file: Path, out_file: Path,
                         gprmax_env: str = "gprMax") -> bool:
    """
    Generate and run gprMax simulation.

    Returns: True if successful, False otherwise
    """

    try:
        # Write TOML
        toml_file.parent.mkdir(parents=True, exist_ok=True)
        with open(toml_file, 'w') as f:
            f.write(toml_content)

        # Generate .in file
        result = subprocess.run(
            [sys.executable, "scripts/pipeline/generate_in_files.py", str(toml_file), "-o", str(in_file)],
            capture_output=True,
            text=True,
            timeout=30
        )

        if result.returncode != 0:
            print(f"  [TOML->IN] Failed: {result.stderr[:200]}")
            return False

        # Run gprMax
        gprmax_python = Path(f"C:\\Users\\barba\\.conda\\envs\\{gprmax_env}\\python.exe")
        if not gprmax_python.exists():
            print(f"  [GPRMAX] Python not found: {gprmax_python}")
            return False

        result = subprocess.run(
            [str(gprmax_python), "-m", "gprMax", str(in_file)],
            capture_output=True,
            text=True,
            timeout=60
        )

        if result.returncode != 0:
            print(f"  [GPRMAX] Simulation failed: {result.stderr[:200]}")
            return False

        if not out_file.exists():
            print(f"  [OUTPUT] File not created: {out_file}")
            return False

        return True

    except subprocess.TimeoutExpired:
        print(f"  [TIMEOUT] Simulation took too long")
        return False
    except Exception as e:
        print(f"  [ERROR] {str(e)[:200]}")
        return False


def extract_direct_wave(signal, t_ns, delay_ns: float = 2.77, t_max: float = 12.0) -> tuple:
    """
    Extract direct wave (0-t_max ns) after applying delay.
    Returns: (direct_wave_signal, time_array, success)
    """

    dt_ns = t_ns[1] - t_ns[0] if len(t_ns) > 1 else 0.01
    signal_delayed = apply_time_delay(signal, dt_ns, delay_ns)
    signal_flipped = signal_delayed * -1
    signal_norm = normalize_peak(signal_flipped)

    idx = (t_ns >= 0) & (t_ns <= t_max)
    if np.sum(idx) < 10:
        return None, None, False

    return signal_norm[idx], t_ns[idx], True


def main():
    import argparse

    ap = argparse.ArgumentParser(description="Step 9: Optimize RX/TX spacing to match direct pulse")
    ap.add_argument("real_dzt", type=Path, help="Real .DZT file")
    ap.add_argument("--tx-rx-range", nargs=2, type=float, default=[0.05, 0.15],
                   help="TX/RX spacing range in meters (min max)")
    ap.add_argument("--tx-rx-step", type=float, default=0.01,
                   help="TX/RX spacing step in meters")
    ap.add_argument("--antenna-height-range", nargs=2, type=float, default=[0.05, 0.15],
                   help="Antenna height range in meters (min max)")
    ap.add_argument("--antenna-height-step", type=float, default=0.01,
                   help="Antenna height step in meters")
    ap.add_argument("--trace", type=int, default=1000, help="DZT trace index")
    ap.add_argument("--output-dir", type=Path, default=Path("output_test/optimization"),
                   help="Output directory for optimization results")
    args = ap.parse_args()

    # Load real DZT direct wave
    print("[READ] Real DZT direct wave...")
    real_sig, real_t, dt_real = read_real_dzt(args.real_dzt, trace_idx=args.trace)

    real_dw, real_dw_t, success = extract_direct_wave(real_sig, real_t, delay_ns=2.77, t_max=12.0)
    if not success:
        print("[ERR] Could not extract real direct wave")
        sys.exit(1)

    real_dw_norm = normalize_peak(real_dw)

    print(f"[OK] Real direct wave: {len(real_dw)} samples, 0-{real_dw_t[-1]:.1f} ns")

    # Define parameter search space
    tx_rx_spacings = np.arange(args.tx_rx_range[0], args.tx_rx_range[1] + args.tx_rx_step, args.tx_rx_step)
    antenna_heights = np.arange(args.antenna_height_range[0], args.antenna_height_range[1] + args.antenna_height_step, args.antenna_height_step)

    print(f"\n[SEARCH] Grid search over {len(tx_rx_spacings)} x {len(antenna_heights)} = {len(tx_rx_spacings) * len(antenna_heights)} configs")
    print(f"  TX/RX spacing: {args.tx_rx_range[0]:.3f} - {args.tx_rx_range[1]:.3f} m (step {args.tx_rx_step:.3f})")
    print(f"  Antenna height: {args.antenna_height_range[0]:.3f} - {args.antenna_height_range[1]:.3f} m (step {args.antenna_height_step:.3f})")

    results = []
    best_corr = -999
    best_config = None

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    for i, (spacing, height) in enumerate(product(tx_rx_spacings, antenna_heights)):
        config_name = f"opt_spacing{spacing*1000:.0f}mm_height{height*1000:.0f}mm"
        print(f"\n[{i+1}/{len(tx_rx_spacings)*len(antenna_heights)}] {config_name}")

        # Generate TOML
        toml_content = generate_toml_config(spacing, height, domain_x=0.5)
        toml_file = output_dir / f"{config_name}.toml"
        in_file = output_dir / f"{config_name}.in"
        out_file = output_dir / f"{config_name}.out"

        # Run simulation
        print(f"  [SIM] Running gprMax...", end=" ", flush=True)
        if not run_gprmax_simulation(toml_content, toml_file, in_file, out_file):
            print("[SKIP]")
            continue

        print("[OK]", flush=True)

        # Extract direct wave
        try:
            data = read_ascan(out_file, component="Ez")
            syn_sig = data['signal']
            dt_syn = data['dt']
            t_syn = np.arange(len(syn_sig)) * dt_syn * 1e9

            syn_dw, syn_dw_t, success = extract_direct_wave(syn_sig, t_syn, delay_ns=2.77, t_max=12.0)
            if not success:
                print(f"  [DW] Could not extract direct wave")
                continue

            # Interpolate to real's time grid for comparison
            syn_dw_interp = np.interp(real_dw_t, syn_dw_t, normalize_peak(syn_dw))
            corr = compute_correlation(syn_dw_interp, real_dw_norm)

            result = {
                'config': config_name,
                'spacing_m': spacing,
                'height_m': height,
                'correlation': corr,
                'out_file': str(out_file)
            }

            results.append(result)

            print(f"  [CORR] {corr:+.6f}", flush=True)

            if corr > best_corr:
                best_corr = corr
                best_config = result
                print(f"  [BEST] New best! (was {best_corr - (corr - best_corr):+.6f})")

        except Exception as e:
            print(f"  [ERR] {str(e)[:100]}")
            continue

    # Summary
    if not results:
        print("\n[ERR] No successful simulations")
        sys.exit(1)

    print(f"\n\n{'='*70}")
    print("OPTIMIZATION RESULTS")
    print(f"{'='*70}")

    # Sort by correlation
    results_sorted = sorted(results, key=lambda x: x['correlation'], reverse=True)

    print(f"\nTop 5 configurations:")
    for i, res in enumerate(results_sorted[:5]):
        print(f"  {i+1}. {res['config']}")
        print(f"     TX/RX spacing: {res['spacing_m']*1000:.2f} mm")
        print(f"     Antenna height: {res['height_m']*1000:.2f} mm")
        print(f"     Correlation: {res['correlation']:+.6f}")

    if best_config:
        print(f"\n[BEST] Optimal configuration:")
        print(f"  {best_config['config']}")
        print(f"  TX/RX spacing: {best_config['spacing_m']*1000:.2f} mm")
        print(f"  Antenna height: {best_config['height_m']*1000:.2f} mm")
        print(f"  Correlation: {best_config['correlation']:+.6f}")

        # Save best config
        best_config_file = output_dir / "BEST_CONFIG.json"
        with open(best_config_file, 'w') as f:
            json.dump(best_config, f, indent=2)

        print(f"\n[SAVE] Best config saved to {best_config_file}")

    # Save all results
    results_file = output_dir / "optimization_results.json"
    with open(results_file, 'w') as f:
        json.dump(results_sorted, f, indent=2)

    print(f"[SAVE] All results saved to {results_file}")


if __name__ == "__main__":
    main()
