#!/usr/bin/env python3
"""
Resample 10layer_eps_sweep.out to 50ns duration (pad with zeros).
"""

import sys
from pathlib import Path
import h5py
import numpy as np


def read_synthetic_out(out_path: Path):
    """Read gprMax .out file."""
    with h5py.File(out_path, 'r') as f:
        signal = f['rxs/rx1/Ez'][()]
        dt = f.attrs.get('dt', 0.0)
    return signal, dt


def extend_signal_with_zeros(signal: np.ndarray, current_duration_ns: float,
                            target_duration_ns: float, dt_ns: float):
    """Extend signal with zeros to reach target duration."""
    current_samples = len(signal)
    target_samples = int(np.round(target_duration_ns / dt_ns))

    padding_samples = target_samples - current_samples

    print(f"Current samples: {current_samples} ({current_duration_ns:.2f} ns)")
    print(f"Target samples: {target_samples} ({target_duration_ns:.2f} ns)")
    print(f"Padding with {padding_samples} zeros\n")

    extended = np.concatenate([signal, np.zeros(padding_samples)])

    return extended[:target_samples]  # Ensure exact target length


def write_extended_out(input_path: Path, output_path: Path, extended_signal: np.ndarray, dt: float):
    """Write extended signal to new HDF5 .out file."""
    import shutil

    # Copy file as-is first
    shutil.copy2(input_path, output_path)

    # Now modify just the Ez dataset
    with h5py.File(output_path, 'r+') as f:
        # Replace Ez dataset
        ez_dataset = f['rxs/rx1/Ez']
        old_data = ez_dataset[()]

        # Delete and recreate
        del f['rxs/rx1/Ez']
        f['rxs/rx1'].create_dataset('Ez', data=extended_signal, dtype=old_data.dtype)


def main():
    print("\n" + "="*80)
    print("RESAMPLE 10LAYER_EPS_SWEEP.OUT TO 50NS")
    print("="*80 + "\n")

    input_path = Path("10layer_eps_sweep.out")
    output_path = Path("10layer_eps_sweep_50ns.out")

    # Read original
    signal, dt = read_synthetic_out(input_path)
    dt_ns = dt * 1e9

    print(f"[READ] {input_path.name}")
    print(f"  Samples: {len(signal)}")
    print(f"  dt: {dt_ns:.6f} ns")
    print(f"  Duration: {(len(signal)-1)*dt_ns:.2f} ns\n")

    # Extend to 50ns
    current_duration = (len(signal) - 1) * dt_ns
    target_duration = 50.0

    extended_signal = extend_signal_with_zeros(signal, current_duration,
                                              target_duration, dt_ns)

    # Write new file
    write_extended_out(input_path, output_path, extended_signal, dt)

    # Verify
    signal_verify, dt_verify = read_synthetic_out(output_path)
    dt_verify_ns = dt_verify * 1e9

    print(f"[WRITE] {output_path.name}")
    print(f"  Samples: {len(signal_verify)}")
    print(f"  dt: {dt_verify_ns:.6f} ns")
    print(f"  Duration: {(len(signal_verify)-1)*dt_verify_ns:.2f} ns\n")

    print("="*80)
    print(f"Resampling complete: {output_path}")
    print("="*80 + "\n")

    return 0


if __name__ == "__main__":
    sys.exit(main())
