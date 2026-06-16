#!/usr/bin/env python3
"""
Step 12: Test frequency variants (380-420 MHz) on direct wave matching.
Find optimal center frequency for field hardware match.
"""

import sys
from pathlib import Path
import numpy as np
import subprocess
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


def compute_correlation(sig1, sig2):
    if len(sig1) != len(sig2):
        min_len = min(len(sig1), len(sig2))
        sig1 = sig1[:min_len]
        sig2 = sig2[:min_len]

    s1 = (sig1 - np.mean(sig1)) / (np.std(sig1) + 1e-10)
    s2 = (sig2 - np.mean(sig2)) / (np.std(sig2) + 1e-10)
    return np.mean(s1 * s2)


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
    import argparse

    ap = argparse.ArgumentParser(description="Test frequency variants for direct wave matching")
    ap.add_argument("real_dzt", type=Path, help="Real .DZT file")
    ap.add_argument("--freqs", nargs="+", type=int, default=[380, 390, 400, 410, 420],
                   help="Frequencies to test (MHz)")
    ap.add_argument("--trace", type=int, default=1000)
    ap.add_argument("--output-dir", type=Path, default=Path("output_test/freq_opt"))
    args = ap.parse_args()

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Load real direct wave
    print("[READ] Real DZT...")
    real_sig, real_t, _ = read_real_dzt(args.real_dzt, trace_idx=args.trace)
    real_dw, real_dw_t, _ = extract_direct_wave(real_sig, real_t, delay_ns=2.77, t_max=12.0)
    real_dw_norm = normalize_peak(real_dw)
    print(f"[OK] Real direct wave: {len(real_dw)} samples\n")

    gprmax_python = str(Path("C:\\Users\\barba\\.conda\\envs\\gprMax\\python.exe"))

    results = []

    for freq_mhz in sorted(args.freqs):
        freq_hz = freq_mhz * 1e6
        config_name = f"freq_{freq_mhz}mhz"
        print(f"[TEST] {freq_mhz} MHz...", end=" ", flush=True)

        # Find TOML file
        toml_file = Path(f"examples/freespace_{freq_mhz}mhz.toml")
        if not toml_file.exists():
            print(f"[SKIP] TOML not found")
            continue

        in_file = output_dir / f"{config_name}.in"
        out_file = output_dir / f"{config_name}.out"

        try:
            # Generate .in
            result = subprocess.run(
                [sys.executable, "scripts/pipeline/generate_in_files.py", str(toml_file), "-o", str(in_file)],
                capture_output=True, text=True, timeout=30, cwd=Path.cwd()
            )
            if result.returncode != 0:
                print(f"[GEN FAIL]")
                continue

            print(f"[IN] ", end="", flush=True)

            # Run gprMax
            result = subprocess.run(
                [gprmax_python, "-m", "gprMax", str(in_file)],
                capture_output=True, text=True, timeout=180
            )
            if result.returncode != 0 or not out_file.exists():
                print(f"[SIM FAIL]")
                continue

            print(f"[SIM] ", end="", flush=True)

            # Extract and compare
            data = read_ascan(out_file, component="Ez")
            syn_sig = data['signal']
            dt_syn = data['dt']
            t_syn = np.arange(len(syn_sig)) * dt_syn * 1e9

            syn_dw, syn_dw_t, success = extract_direct_wave(syn_sig, t_syn, delay_ns=2.77, t_max=12.0)
            if not success:
                print(f"[NO_DW]")
                continue

            # Interpolate to real's time grid
            syn_dw_interp = np.interp(real_dw_t, syn_dw_t, normalize_peak(syn_dw))
            corr = compute_correlation(syn_dw_interp, real_dw_norm)

            results.append({
                'freq_mhz': freq_mhz,
                'freq_hz': freq_hz,
                'correlation': corr,
                'out_file': str(out_file)
            })

            print(f"corr={corr:+.6f}")

        except Exception as e:
            print(f"[ERR] {str(e)[:80]}")
            continue

    # Summary
    print(f"\n{'='*70}")
    print("FREQUENCY SWEEP RESULTS")
    print(f"{'='*70}\n")

    if not results:
        print("[ERR] No successful simulations")
        sys.exit(1)

    results_sorted = sorted(results, key=lambda x: x['correlation'], reverse=True)

    for i, res in enumerate(results_sorted, 1):
        print(f"{i}. {res['freq_mhz']:3d} MHz: {res['correlation']:+.6f}")

    best = results_sorted[0]
    print(f"\n[BEST] {best['freq_mhz']} MHz - Correlation {best['correlation']:+.6f}")

    # Save results
    with open(output_dir / "freq_results.json", 'w') as f:
        json.dump(results_sorted, f, indent=2)

    print(f"\n[SAVE] -> {output_dir / 'freq_results.json'}")


if __name__ == "__main__":
    main()
