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
import h5py
from pathlib import Path

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
    
    # Create HDF5
    with h5py.File(out_path, 'w') as f:
        # Root Attributes
        f.attrs['dt'] = dt
        f.attrs['Iterations'] = iterations
        f.attrs['Title'] = "Fake Simulation Data"
        f.attrs['gprMax'] = "3.x (Fake)"
        
        # Structure: rxs/rx1/Ez
        grp_rxs = f.create_group('rxs')
        grp_rx1 = grp_rxs.create_group('rx1')
        
        # Attributes for Rx
        grp_rx1.attrs['Name'] = 'rx1'
        grp_rx1.attrs['Position'] = np.array([0.1, 0.1, 0.1])
        
        # Ez Field (Vertical Electric)
        dset_ez = grp_rx1.create_dataset('Ez', data=total_signal)
        dset_ez.attrs['Unit'] = 'V/m'
        
        # Hx Field (Transverse Magnetic) - slightly different phase/amp
        total_signal_h = (sig_direct * 0.8) + (sig_ref1 * -0.3) + (sig_ref2 * 0.1) + noise
        dset_hx = grp_rx1.create_dataset('Hx', data=total_signal_h/377.0) # Approx impedance scaling
        dset_hx.attrs['Unit'] = 'A/m'
        
        # Hy/Ex/Ey/Hz (Zeros or Noise)
        grp_rx1.create_dataset('Hy', data=noise*0.1)
        grp_rx1.create_dataset('Ex', data=noise*0.1)
        grp_rx1.create_dataset('Ey', data=noise*0.1)
        grp_rx1.create_dataset('Hz', data=noise*0.1)

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
