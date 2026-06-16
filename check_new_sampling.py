#!/usr/bin/env python3
"""Check new 50ns .out files."""
import h5py
from pathlib import Path

configs = [
    ("Ballast (NEW 50ns)", "output_test/ballast_50ns.out"),
    ("Rocks (NEW 50ns)", "output_test/rocks_50ns.out"),
]

print("="*70)
print("NEW SYNTHETIC FILES - SAMPLING VERIFICATION")
print("="*70)
print(f"{'Config':<25} {'Samples':<12} {'dt (ns)':<15} {'Window (ns)':<15}")
print("-"*70)

for name, path in configs:
    p = Path(path)
    if p.exists():
        with h5py.File(p, 'r') as f:
            signal = f['rxs/rx1/Ez'][()]
            dt = f.attrs.get('dt', 0)

        n_samples = len(signal)
        dt_ns = dt * 1e9
        window_ns = n_samples * dt_ns

        status = "[OK]" if window_ns >= 49 else "[BAD]"
        print(f"{name:<25} {n_samples:<12} {dt_ns:<15.6f} {window_ns:<15.2f}  {status}")
    else:
        print(f"{name:<25} FILE NOT FOUND")

print("\n" + "="*70)
print("REAL DATA (for comparison)")
print("="*70)
print(f"{'Real (DZT)':<25} {510:<12} {0.097847:<15.6f} {49.8:<15.2f}")
