#!/usr/bin/env python3
"""
Generate Fake gprMax Output (.out) HDF5 files for testing visualization tools.

Usage:
    python generate_fake_output.py <input_file.in> [options]

This script creates a corresponding .out file with synthesized signals (Ricker wavelet + noise).
"""
import sys
import argparse
import numpy as np
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
from src.data_loader import write_rx_out

def ricker(f, length, dt, peak_time):
    """Generate a Ricker wavelet."""
    t = np.arange(length) * dt
    y = (1.0 - 2.0 * (np.pi**2) * (f**2) * ((t - peak_time)**2)) * \
        np.exp(-(np.pi**2) * (f**2) * ((t - peak_time)**2))
    return y

def generate_fake_output(input_file: str, dt=1e-10, iterations=1000, freq=400e6):
    in_path = Path(input_file)
    out_path = in_path.with_suffix('.out')
    
    print(f"Generating fake output: {out_path}")
    print(f"  dt={dt}, iterations={iterations}, freq={freq/1e6}MHz")
    
    # Time vector
    t = np.arange(iterations) * dt
    
    # Generate Synthetic Signals
    
    # 1. Direct Wave (Early, Strong)
    sig_direct = ricker(freq, iterations, dt, 3e-9) * 1.5
    
    # 2. Reflection 1 (Ballast Top)
    sig_ref1 = ricker(freq, iterations, dt, 5e-9) * 0.4
    
    # 3. Reflection 2 (Fouling/Bottom)
    sig_ref2 = ricker(freq, iterations, dt, 8e-9) * -0.2
    
    # Combined Signal + Noise
    noise = np.random.normal(0, 0.02, iterations)
    total_signal = sig_direct + sig_ref1 + sig_ref2 + noise

    # Hx (Transverse Magnetic) - slightly different phase/amp, impedance-scaled
    total_signal_h = (sig_direct * 0.8) + (sig_ref1 * -0.3) + (sig_ref2 * 0.1) + noise

    # Structure: rxs/rx1/{Ez,Hx,...} written via the canonical .out writer.
    traces = {
        'Ez': total_signal,
        'Hx': total_signal_h / 377.0,   # approx impedance scaling
        'Hy': noise * 0.1,
        'Ex': noise * 0.1,
        'Ey': noise * 0.1,
        'Hz': noise * 0.1,
    }
    write_rx_out(out_path, traces, dt=dt, position=(0.1, 0.1, 0.1),
                 title="Fake Simulation Data", gprmax="3.x (Fake)")

    print("Done.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("input_file", help="Path to input .in file")
    parser.add_argument("--freq", type=float, default=400e6, help="Center frequency (Hz)")
    parser.add_argument("--iter", type=int, default=1500, help="Number of iterations")
    
    args = parser.parse_args()
    
    if not Path(args.input_file).exists():
        print(f"Error: Input file {args.input_file} not found.")
        sys.exit(1)
        
    generate_fake_output(args.input_file, freq=args.freq, iterations=args.iter)
