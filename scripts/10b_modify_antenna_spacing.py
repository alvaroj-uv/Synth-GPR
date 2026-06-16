#!/usr/bin/env python3
"""
Step 10b: Directly modify antenna spacing in .in files by changing RX position.
"""

import sys
from pathlib import Path
import re
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


def create_modified_in_file(base_in: Path, tx_x: float, rx_x: float, output_in: Path):
    """
    Modify TX and RX positions in .in file.
    """
    with open(base_in, 'r') as f:
        content = f.read()

    # Pattern: #hertzian_dipole: z TX_X TX_Y TX_Z waveform
    # and #receiver: RX_Z RX_X RX_Y (possibly)

    # Find existing coordinates
    hertz_pattern = r'#hertzian_dipole:\s+z\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)\s+'
    match = re.search(hertz_pattern, content)
    if not match:
        return False

    old_tx_x, tx_y, tx_z = float(match.group(1)), float(match.group(2)), float(match.group(3))

    # Replace TX position
    content = re.sub(
        hertz_pattern,
        f'#hertzian_dipole: z {tx_x} {tx_y} {tx_z} ',
        content
    )

    # Find and replace receiver (if exists) - look for #rx lines
    # Pattern: #rx: RX_X RX_Y RX_Z (format: X Y Z coordinates)
    rx_pattern = r'(#rx:\s+)([\d.]+)\s+([\d.]+)\s+([\d.]+)'
    if re.search(rx_pattern, content):
        replacement = f'#rx: {rx_x} {tx_y} {tx_z}'
        content = re.sub(rx_pattern, replacement, content)
    else:
        # Add receiver command if not present
        # Find insertion point (after waveform definition)
        waveform_pattern = r'(#waveform:.*\n)'
        if re.search(waveform_pattern, content):
            insert_point = re.search(waveform_pattern, content).end()
            receiver_cmd = f'#rx: {tx_z} {rx_x} {tx_y}\n'
            content = content[:insert_point] + receiver_cmd + content[insert_point:]

    # Write modified file
    with open(output_in, 'w') as f:
        f.write(content)

    return True


def main():
    import argparse

    ap = argparse.ArgumentParser(description="Test different TX/RX spacings by modifying .in files")
    ap.add_argument("real_dzt", type=Path, help="Real .DZT file")
    ap.add_argument("--base-toml", type=Path, default=Path("examples/freespace_400mhz_extended.toml"),
                   help="Base TOML config")
    ap.add_argument("--spacings", nargs="+", type=float,
                   default=[0.04, 0.05, 0.06, 0.07, 0.08, 0.10],
                   help="TX/RX spacings in meters")
    ap.add_argument("--trace", type=int, default=1000)
    ap.add_argument("--output-dir", type=Path, default=Path("output_test/spacing_test"))
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
    print(f"[OK] Real direct wave: {len(real_dw)} samples, 0-{real_dw_t[-1]:.1f} ns\n")

    # Generate base .in file
    base_config_name = args.base_toml.stem
    base_in = output_dir / f"{base_config_name}_base.in"

    print(f"[GENERATE] Creating base .in from {args.base_toml.name}...")
    result = subprocess.run(
        [sys.executable, "scripts/pipeline/generate_in_files.py", str(args.base_toml), "-o", str(base_in)],
        capture_output=True, text=True, timeout=30, cwd=Path.cwd()
    )

    if result.returncode != 0:
        print(f"[ERR] Failed to generate base .in: {result.stderr[:200]}")
        sys.exit(1)

    print(f"[OK] Base .in created\n")

    gprmax_python = str(Path("C:\\Users\\barba\\.conda\\envs\\gprMax\\python.exe"))

    results = []

    # TX is at center (0.25m), RX moves
    tx_x = 0.25

    for spacing_m in args.spacings:
        rx_x = tx_x + spacing_m
        config_name = f"spacing_{spacing_m*1000:.0f}mm"
        print(f"[TEST] {config_name} (RX @ {rx_x:.3f}m)...", end=" ", flush=True)

        modified_in = output_dir / f"{config_name}.in"
        out_file = output_dir / f"{config_name}.out"

        # Create modified .in with new antenna positions
        if not create_modified_in_file(base_in, tx_x, rx_x, modified_in):
            print("[MODIFY FAIL]")
            continue

        # Run gprMax
        try:
            result = subprocess.run(
                [gprmax_python, "-m", "gprMax", str(modified_in)],
                capture_output=True, text=True, timeout=180
            )

            if result.returncode != 0 or not out_file.exists():
                print(f"[GPRMAX FAIL]")
                continue

            print("[SIM] ", end="", flush=True)

            # Extract and compare
            data = read_ascan(out_file, component="Ez")
            syn_sig = data['signal']
            dt_syn = data['dt']
            t_syn = np.arange(len(syn_sig)) * dt_syn * 1e9

            syn_dw, syn_dw_t, success = extract_direct_wave(syn_sig, t_syn, delay_ns=2.77, t_max=12.0)
            if not success:
                print("[NO_DW]")
                continue

            syn_dw_interp = np.interp(real_dw_t, syn_dw_t, normalize_peak(syn_dw))
            corr = compute_correlation(syn_dw_interp, real_dw_norm)

            results.append({
                'spacing_mm': spacing_m * 1000,
                'spacing_m': spacing_m,
                'correlation': corr,
                'out_file': str(out_file)
            })

            print(f"corr={corr:+.6f}")

        except Exception as e:
            print(f"[ERR] {str(e)[:80]}")
            continue

    # Summary
    print(f"\n{'='*70}")
    print("TX/RX SPACING OPTIMIZATION RESULTS")
    print(f"{'='*70}\n")

    if not results:
        print("[ERR] No successful simulations")
        sys.exit(1)

    results_sorted = sorted(results, key=lambda x: x['correlation'], reverse=True)

    for i, res in enumerate(results_sorted, 1):
        print(f"{i}. Spacing {res['spacing_mm']:.0f} mm")
        print(f"   Correlation: {res['correlation']:+.6f}")

    best = results_sorted[0]
    print(f"\n[BEST] {best['spacing_mm']:.0f} mm - Correlation {best['correlation']:+.6f}")

    with open(output_dir / "spacing_results.json", 'w') as f:
        json.dump(results_sorted, f, indent=2)

    print(f"\n[SAVE] -> {output_dir / 'spacing_results.json'}")


if __name__ == "__main__":
    main()
