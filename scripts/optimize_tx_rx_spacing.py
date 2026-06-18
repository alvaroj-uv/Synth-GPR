#!/usr/bin/env python3
"""
Step 9: Optimize TX/RX spacing in free space to match direct pulse.
Antenna moves in air only - vary the separation distance between TX and RX.
"""

import sys
from pathlib import Path
import numpy as np
import subprocess
import json
import tempfile

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
    """Normalize by peak amplitude."""
    peak = np.max(np.abs(signal))
    return signal / peak if peak != 0 else signal


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

    s1 = (sig1 - np.mean(sig1)) / (np.std(sig1) + 1e-10)
    s2 = (sig2 - np.mean(sig2)) / (np.std(sig2) + 1e-10)
    return np.mean(s1 * s2)


def extract_direct_wave(signal, t_ns, delay_ns: float = 2.77, t_max: float = 12.0) -> tuple:
    """Extract direct wave (0-t_max ns)."""
    dt_ns = t_ns[1] - t_ns[0] if len(t_ns) > 1 else 0.01
    signal_delayed = apply_time_delay(signal, dt_ns, delay_ns)
    signal_flipped = signal_delayed * -1
    signal_norm = normalize_peak(signal_flipped)

    idx = (t_ns >= 0) & (t_ns <= t_max)
    if np.sum(idx) < 10:
        return None, None, False

    return signal_norm[idx], t_ns[idx], True


def generate_freespace_toml(tx_rx_spacing: float) -> str:
    """Generate TOML for free-space antenna with specified TX/RX spacing."""
    toml = f"""# Free space antenna optimization
# TX/RX spacing: {tx_rx_spacing*1000:.2f} mm

[sim]
freq_hz = 400e6
domain_x = 0.5
dx = 0.003
antenna_clearance = 0.1
air_buffer = 0.1
time_window = 5.0e-8
tx_rx_spacing = {tx_rx_spacing}
title = "Free Space - TX/RX spacing {tx_rx_spacing*1000:.1f}mm"

[source]
waveform = "ricker"
amplitude = 1.0
polarization = "z"

[[layer]]
name = "air"
thickness = 0.5
"""
    return toml


def run_gprmax_sim(tx_rx_spacing: float, output_dir: Path, gprmax_python: str) -> Path:
    """
    Run single gprMax simulation for given TX/RX spacing.
    Returns: path to .out file or None if failed
    """

    config_name = f"opt_txrx_{tx_rx_spacing*1000:.1f}mm"
    toml_file = output_dir / f"{config_name}.toml"
    in_file = output_dir / f"{config_name}.in"
    out_file = output_dir / f"{config_name}.out"

    try:
        # Write TOML
        toml_content = generate_freespace_toml(tx_rx_spacing)
        with open(toml_file, 'w') as f:
            f.write(toml_content)

        # Generate .in
        result = subprocess.run(
            [sys.executable, "scripts/pipeline/generate_in_files.py", str(toml_file), "-o", str(in_file)],
            capture_output=True, text=True, timeout=30, cwd=Path.cwd()
        )
        if result.returncode != 0:
            return None

        # Run gprMax
        result = subprocess.run(
            [gprmax_python, "-m", "gprMax", str(in_file)],
            capture_output=True, text=True, timeout=120
        )
        if result.returncode != 0 or not out_file.exists():
            return None

        return out_file

    except Exception:
        return None


def main():
    import argparse

    ap = argparse.ArgumentParser(description="Optimize TX/RX spacing in free space")
    ap.add_argument("real_dzt", type=Path, help="Real .DZT file")
    ap.add_argument("--spacing-min", type=float, default=0.03, help="Min TX/RX spacing (m)")
    ap.add_argument("--spacing-max", type=float, default=0.12, help="Max TX/RX spacing (m)")
    ap.add_argument("--spacing-step", type=float, default=0.01, help="Spacing step (m)")
    ap.add_argument("--trace", type=int, default=1000, help="DZT trace index")
    ap.add_argument("--output-dir", type=Path, default=Path("output_test/tx_rx_opt"))
    args = ap.parse_args()

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Load real direct wave
    print("[READ] Real DZT...")
    real_sig, real_t, _ = read_real_dzt(args.real_dzt, trace_idx=args.trace)
    real_dw, real_dw_t, success = extract_direct_wave(real_sig, real_t, delay_ns=2.77, t_max=12.0)

    if not success:
        print("[ERR] Could not extract real direct wave")
        sys.exit(1)

    real_dw_norm = normalize_peak(real_dw)
    print(f"[OK] Real direct wave: {len(real_dw)} samples, 0-{real_dw_t[-1]:.1f} ns")

    # Generate spacing range
    spacings = np.arange(args.spacing_min, args.spacing_max + args.spacing_step, args.spacing_step)

    print(f"\n[SEARCH] Testing {len(spacings)} TX/RX spacings:")
    for s in spacings:
        print(f"  {s*1000:.1f} mm", end="  ")
    print("\n")

    # gprMax Python
    gprmax_python = str(Path("C:\\Users\\barba\\.conda\\envs\\gprMax\\python.exe"))

    results = []
    best_corr = -999
    best_spacing = None

    for i, spacing in enumerate(spacings):
        print(f"[{i+1}/{len(spacings)}] TX/RX {spacing*1000:.1f}mm...", end=" ", flush=True)

        # Run simulation
        out_file = run_gprmax_sim(spacing, output_dir, gprmax_python)
        if out_file is None:
            print("[FAIL]")
            continue

        # Extract and compare
        try:
            data = read_ascan(out_file, component="Ez")
            syn_sig = data['signal']
            dt_syn = data['dt']
            t_syn = np.arange(len(syn_sig)) * dt_syn * 1e9

            syn_dw, syn_dw_t, success = extract_direct_wave(syn_sig, t_syn, delay_ns=2.77, t_max=12.0)
            if not success:
                print("[NO_DW]")
                continue

            # Interpolate to real's grid
            syn_dw_interp = np.interp(real_dw_t, syn_dw_t, normalize_peak(syn_dw))
            corr = compute_correlation(syn_dw_interp, real_dw_norm)

            results.append({
                'spacing_mm': spacing * 1000,
                'spacing_m': spacing,
                'correlation': corr,
                'out_file': str(out_file)
            })

            print(f"corr={corr:+.4f}", flush=True)

            if corr > best_corr:
                best_corr = corr
                best_spacing = spacing
                print(f"       ^^ NEW BEST!")

        except Exception as e:
            print(f"[ERR] {str(e)[:50]}")
            continue

    # Results
    if not results:
        print("\n[ERR] No successful simulations")
        sys.exit(1)

    results_sorted = sorted(results, key=lambda x: x['correlation'], reverse=True)

    print(f"\n{'='*70}")
    print("OPTIMIZATION RESULTS")
    print(f"{'='*70}\n")

    print("Top 5 configurations:")
    for i, res in enumerate(results_sorted[:5], 1):
        print(f"  {i}. TX/RX spacing {res['spacing_mm']:.1f} mm")
        print(f"     Correlation: {res['correlation']:+.6f}")

    if best_spacing:
        print(f"\n[BEST] Optimal TX/RX spacing: {best_spacing*1000:.2f} mm")
        print(f"       Correlation: {best_corr:+.6f}")

        best_result = {
            'spacing_mm': best_spacing * 1000,
            'spacing_m': best_spacing,
            'correlation': best_corr
        }

        with open(output_dir / "BEST_SPACING.json", 'w') as f:
            json.dump(best_result, f, indent=2)

        print(f"\n[SAVE] Best result -> {output_dir / 'BEST_SPACING.json'}")

    # Save all results
    with open(output_dir / "all_results.json", 'w') as f:
        json.dump(results_sorted, f, indent=2)

    print(f"[SAVE] All results -> {output_dir / 'all_results.json'}")

    print(f"\nNext: Use best spacing in optimized gprMax config")


if __name__ == "__main__":
    main()
