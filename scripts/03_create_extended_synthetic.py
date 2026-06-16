#!/usr/bin/env python3
"""
Step 3: Create extended synthetic with matched time window.
Output: new .npy file with extended waveform (same time axis as real DZT).
"""

import sys
from pathlib import Path
import numpy as np
import h5py

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.data_loader import read_ascan


def read_synthetic(file_path: Path, component: str = "Ez") -> tuple:
    """Read synthetic .out file."""
    data = read_ascan(file_path, component)
    signal = data['signal']
    dt = data['dt']
    t_ns = np.arange(len(signal)) * dt * 1e9
    return signal, t_ns, dt * 1e9


def read_real_dzt(file_path: Path, trace_idx: int = 1000) -> tuple:
    """Read real DZT file to get duration."""
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


def create_extended_synthetic(syn_sig, syn_t, dt_syn, target_duration_ns):
    """
    Extend synthetic to match target duration.
    Returns: extended_signal, extended_time_array
    """
    current_duration = syn_t[-1] - syn_t[0]
    samples_needed = int(np.round((target_duration_ns - current_duration) / dt_syn))

    if samples_needed > 0:
        # Pad with zeros to match real's duration
        extended_sig = np.concatenate([syn_sig, np.zeros(samples_needed)])
    else:
        extended_sig = syn_sig

    # Create matching time array
    extended_t = np.arange(len(extended_sig)) * dt_syn

    return extended_sig, extended_t


def save_extended_synthetic(signal, time_array, dt_ns, output_path):
    """
    Save extended synthetic in HDF5 format (similar to gprMax .out structure).
    Includes metadata for easy comparison with real data.
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with h5py.File(output_path, 'w') as f:
        # Store the signal
        f.create_dataset('Ez', data=signal, dtype=np.float64)

        # Store time information
        f.create_dataset('Time', data=time_array, dtype=np.float64)

        # Store metadata
        f.attrs['dt'] = dt_ns
        f.attrs['num_samples'] = len(signal)
        f.attrs['duration_ns'] = time_array[-1]
        f.attrs['source'] = 'Extended synthetic (padded with zeros to match real DZT time window)'

        print(f"[SAVE] Extended synthetic saved to {output_path}")
        print(f"  Samples: {len(signal)}")
        print(f"  Duration: {time_array[-1]:.2f} ns")
        print(f"  dt: {dt_ns:.4f} ns/sample")


def save_npy_extended_synthetic(signal, time_array, dt_ns, output_path):
    """
    Also save as NPY for easy numpy loading.
    """
    output_path = Path(output_path).with_suffix('.npy')

    # Create a structured array with signal and time info
    data = np.array([time_array, signal], dtype=object)

    np.save(output_path, data, allow_pickle=True)
    print(f"[SAVE] NPY version saved to {output_path}")


def main():
    import argparse

    ap = argparse.ArgumentParser(description="Step 3: Create extended synthetic with matched time window")
    ap.add_argument("synth", type=Path, help="Original synthetic .out file")
    ap.add_argument("real", type=Path, help="Real .DZT file (used to determine duration)")
    ap.add_argument("--trace", type=int, default=1000, help="DZT trace index (to read duration)")
    ap.add_argument("-o", "--output", type=Path, default=None, help="Output HDF5 file path")
    args = ap.parse_args()

    if not args.synth.exists() or not args.real.exists():
        print("[ERR] Input files not found")
        sys.exit(1)

    print("[READ] Loading original synthetic...")
    syn_sig, syn_t, dt_syn = read_synthetic(args.synth)

    print("[READ] Loading real DZT (to determine target duration)...")
    real_sig, real_t, dt_real = read_real_dzt(args.real, trace_idx=args.trace)

    target_duration = real_t[-1]

    print(f"\n[PROCESS] Extending synthetic to match real duration...")
    print(f"  Original synthetic: {len(syn_sig)} samples, 0-{syn_t[-1]:.1f} ns")
    print(f"  Target duration: 0-{target_duration:.1f} ns")

    extended_sig, extended_t = create_extended_synthetic(syn_sig, syn_t, dt_syn, target_duration)

    print(f"  Extended synthetic: {len(extended_sig)} samples, 0-{extended_t[-1]:.1f} ns")
    print(f"  Samples added: {len(extended_sig) - len(syn_sig)}")

    # Save output
    if args.output:
        out_h5 = Path(args.output).with_suffix('.h5')
    else:
        out_h5 = Path('output_test/extended_synthetic.h5')

    save_extended_synthetic(extended_sig, extended_t, dt_syn, out_h5)
    save_npy_extended_synthetic(extended_sig, extended_t, dt_syn, out_h5)

    print(f"\n{'='*70}")
    print("EXTENDED SYNTHETIC CREATED")
    print(f"{'='*70}")

    print(f"\nOutput files:")
    print(f"  HDF5: {out_h5}")
    print(f"  NPY:  {out_h5.with_suffix('.npy')}")

    print(f"\nMetadata:")
    print(f"  Samples: {len(extended_sig)}")
    print(f"  Duration: 0–{extended_t[-1]:.2f} ns")
    print(f"  dt: {dt_syn:.4f} ns/sample")
    print(f"  Original signal: 0–{syn_t[-1]:.1f} ns")
    print(f"  Padding: {len(extended_sig) - len(syn_sig)} zeros ({extended_t[-1] - syn_t[-1]:.1f} ns)")

    print(f"\nUsage:")
    print(f"  # Load extended synthetic:")
    print(f"  import h5py")
    print(f"  with h5py.File('{out_h5}', 'r') as f:")
    print(f"      syn_sig = f['Ez'][:]")
    print(f"      syn_time = f['Time'][:]")
    print(f"      dt = f.attrs['dt']")

    print(f"\nNext step: Compare extended synthetic vs real on same time axis")


if __name__ == "__main__":
    main()
