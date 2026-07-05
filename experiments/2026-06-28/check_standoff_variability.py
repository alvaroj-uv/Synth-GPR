"""Quick check: how much does direct-wave arrival time vary across EFE corpus?

Loads a sample of EFE DZTs, picks the first-peak sample index, converts to
standoff h = t*c/2, and prints the distribution statistics.
"""
import sys
from pathlib import Path
import numpy as np
import struct

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

DATA = Path("D:/Codigo/Data")
C = 3e8  # m/s
DT_S = 50e-9 / 511  # real DZT dt

HEADER_BYTES = 128 * 1024   # 128 KiB header
N_SAMP = 512
BYTES_PER_SAMP = 4  # int32


def load_dzt_traces(dzt_path, max_traces=2000):
    size = dzt_path.stat().st_size
    n_traces = (size - HEADER_BYTES) // (N_SAMP * BYTES_PER_SAMP)
    n_read = min(n_traces, max_traces)
    with open(dzt_path, 'rb') as f:
        f.seek(HEADER_BYTES)
        raw = f.read(n_read * N_SAMP * BYTES_PER_SAMP)
    arr = np.frombuffer(raw, dtype=np.int32).reshape(n_read, N_SAMP)
    return arr[:, 2:].astype(float)  # drop indices 0-1


def pick_direct_wave(traces, search_end_ns=6.0):
    search_samp = int(search_end_ns / (DT_S * 1e9))
    early = traces[:, :search_samp]
    peak_idx = np.argmax(np.abs(early), axis=1)
    return peak_idx


dzts = sorted(DATA.glob("**/*.DZT"))[:3]
if not dzts:
    print("No DZT files found in D:/Codigo/Data")
    sys.exit(1)

all_peaks = []
for dzt in dzts:
    traces = load_dzt_traces(dzt, max_traces=2000)
    peaks = pick_direct_wave(traces)
    all_peaks.extend(peaks.tolist())
    t_ns = np.array(peaks) * DT_S * 1e9
    h_m = t_ns * 1e-9 * C / 2
    print(f"{dzt.name}: n={len(peaks)}  peak_idx {peaks.min()}-{peaks.max()}"
          f"  t={t_ns.min():.2f}-{t_ns.max():.2f} ns"
          f"  h={h_m.min()*100:.1f}-{h_m.max()*100:.1f} cm")

all_peaks = np.array(all_peaks)
t_all = all_peaks * DT_S * 1e9
h_all = t_all * 1e-9 * C / 2

print(f"\nAll {len(all_peaks)} traces:")
print(f"  Peak index:  mean={all_peaks.mean():.1f}  std={all_peaks.std():.1f}"
      f"  range [{all_peaks.min()}, {all_peaks.max()}]")
print(f"  Arrival:     mean={t_all.mean():.2f} ns  std={t_all.std():.2f} ns")
print(f"  Standoff h:  mean={h_all.mean()*100:.1f} cm  std={h_all.std()*100:.1f} cm"
      f"  range [{h_all.min()*100:.1f}, {h_all.max()*100:.1f}] cm")
