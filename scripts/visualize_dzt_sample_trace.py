#!/usr/bin/env python3
"""Visualize a real DZT trace, optionally overlaid with an aligned synthetic.

Usage:
    # real trace only
    python scripts/visualize_dzt_sample_trace.py [DZT] [TRACE_IDX] [OUT_PNG]

    # overlay synthetic
    python scripts/visualize_dzt_sample_trace.py [DZT] [TRACE_IDX] [OUT_PNG] --syn path/to/sim.out

    # de-ringed real (subtract coherent mean from 2000-trace subset) + synthetic
    python scripts/visualize_dzt_sample_trace.py [DZT] [TRACE_IDX] [OUT_PNG] --syn path/to/sim.out --deringed

    # apply GSSI hardware bandpass filter (100-800 MHz) to synthetic before comparison
    python scripts/visualize_dzt_sample_trace.py [DZT] [TRACE_IDX] [OUT_PNG] --syn path/to/sim.out --bpf

    # wavelet substitution: replace synthetic source wavelet with real GSSI antenna wavelet
    python scripts/visualize_dzt_sample_trace.py [DZT] [TRACE_IDX] [OUT_PNG] --syn path/to/sim.out --wavelet-sub

Alignment pipeline applied to synthetic:
    1. Flip polarity  (gprMax Ez vs GSSI hardware convention)
    2. [--bpf] Apply 100-800 MHz Butterworth BPF at synthetic fs (mimics GSSI hardware filter)
    3. +4.0 ns shift  (hardware cable / filter delay)
    4. Resample to real dt  (synthetic ~0.007 ns  →  real ~0.098 ns)
    5. [--wavelet-sub] Replace synthetic wavelet with real GSSI wavelet via Wiener filter
    6. Peak-normalize both
"""

import sys
import argparse
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import interp1d
from scipy.signal import butter, filtfilt
import numpy.fft as _fft

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.dzt_io import read_dzt_traces
from src.data_loader import read_ascan

# ── constants ────────────────────────────────────────────────────────────────
_DZT_DEFAULT = (
    "D:/Codigo/Data/"
    "PUERTO-LIMACHE_20230726_EFE_V1_PKC000_588_PKF011_020_CENTRO_BRUTO.DZT"
)
_SHIFT_NS = 4.0   # validated hardware delay offset


def _peak_normalize(sig):
    pk = np.max(np.abs(sig))
    return sig / pk if pk > 0 else sig


def _wavelet_sub(syn_aligned, mean_on_common, dt_ns,
                 dw_lo_ns=3.5, dw_hi_ns=9.0, alpha=1e-2):
    """Replace the synthetic source wavelet with the real GSSI antenna wavelet.

    Both signals are already at the same dt (real dt, on t_common).
    The direct-wave window [dw_lo_ns, dw_hi_ns] captures the wavelet before
    the first ground reflection (~9 ns) arrives.

    H_correction(ω) = W_real(ω) / W_syn(ω)   (Wiener regularised)
    syn_corrected    = IFFT( FFT(syn) * H_correction )
    """
    i0 = int(dw_lo_ns / dt_ns)
    i1 = int(dw_hi_ns / dt_ns)
    n_dw = i1 - i0

    taper = np.hanning(n_dw)
    w_syn  = syn_aligned[i0:i1]  * taper
    w_real = mean_on_common[i0:i1] * taper

    n_fft = 4 * len(syn_aligned)
    W_syn  = _fft.rfft(w_syn,  n=n_fft)
    W_real = _fft.rfft(w_real, n=n_fft)

    pwr = np.abs(W_syn)**2
    H   = W_real * np.conj(W_syn) / (pwr + alpha * pwr.max())

    S_corr = _fft.rfft(syn_aligned, n=n_fft) * H
    return _fft.irfft(S_corr, n=n_fft)[:len(syn_aligned)]


def _apply_bpf(sig, dt_ns, flo_hz=100e6, fhi_hz=800e6, order=4):
    """Zero-phase Butterworth bandpass filter matching the GSSI hardware filter."""
    fs_hz = 1.0 / (dt_ns * 1e-9)
    nyq   = fs_hz / 2.0
    lo    = flo_hz / nyq
    hi    = min(fhi_hz / nyq, 0.999)
    b, a  = butter(order, [lo, hi], btype="bandpass")
    return filtfilt(b, a, sig)


# ── alignment helper ─────────────────────────────────────────────────────────
def _align_synthetic(syn_path, real_t, real_sig, dt_ns, mean_trace, do_bpf, do_wavelet_sub):
    """Load a gprMax .out, apply the standard alignment pipeline, return normalised traces.

    Returns (t_common, syn_norm, real_norm, r, dt_syn_ns).
    """
    d       = read_ascan(Path(syn_path), component="Ez")
    syn_raw = d["signal"]
    dt_syn  = d["dt"] * 1e9                              # s → ns
    syn_t   = np.arange(len(syn_raw)) * dt_syn

    syn_flip = -syn_raw
    if do_bpf:
        syn_flip = _apply_bpf(syn_flip, dt_syn)

    shift_samples = int(np.round(_SHIFT_NS / dt_syn))
    syn_shifted   = np.concatenate([np.zeros(shift_samples), syn_flip])[:len(syn_flip)]

    t_end    = min(syn_t[-1], real_t[-1])
    t_common = np.arange(0, t_end, dt_ns)
    syn_rs   = interp1d(syn_t, syn_shifted, kind="cubic",
                        bounds_error=False, fill_value=0.0)(t_common)
    real_rs  = interp1d(real_t, real_sig,   kind="cubic",
                        bounds_error=False, fill_value=0.0)(t_common)

    if do_wavelet_sub and mean_trace is not None:
        mean_on_common = interp1d(real_t, mean_trace, kind="cubic",
                                  bounds_error=False, fill_value=0.0)(t_common)
        syn_rs = _wavelet_sub(syn_rs, mean_on_common, dt_ns)

    syn_norm  = _peak_normalize(syn_rs)
    real_norm = _peak_normalize(real_rs)
    r = np.corrcoef(syn_norm, real_norm)[0, 1]
    return t_common, syn_norm, real_norm, r, dt_syn


# ── args ─────────────────────────────────────────────────────────────────────
ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
ap.add_argument("dzt",       nargs="?", default=_DZT_DEFAULT)
ap.add_argument("trace_idx", nargs="?", type=int, default=15000)
ap.add_argument("output",    nargs="?", default=None)
ap.add_argument("--syn",      default=None, help="gprMax .out file to overlay")
ap.add_argument("--syn2",     default=None, help="second gprMax .out file for side-by-side comparison")
ap.add_argument("--deringed", action="store_true",
                help="subtract coherent mean (2000-trace sample) before plotting")
ap.add_argument("--bpf",         action="store_true",
                help="apply GSSI hardware bandpass (100-800 MHz) to synthetic before comparison")
ap.add_argument("--wavelet-sub", action="store_true",
                help="replace synthetic source wavelet with real GSSI antenna wavelet via Wiener filter")
args = ap.parse_args()

dzt_path  = Path(args.dzt)
trace_idx = args.trace_idx
out_dir   = Path("output_test")
out_dir.mkdir(parents=True, exist_ok=True)
output_file = Path(args.output) if args.output else out_dir / f"dzt_trace_{trace_idx}.png"

# ── real trace ───────────────────────────────────────────────────────────────
traces, meta = read_dzt_traces(dzt_path, start_trace=trace_idx, num_traces=1)
real_sig  = traces[0]
dt_ns     = meta["sample_interval_ns"]
real_t    = np.arange(len(real_sig)) * dt_ns
n_total   = meta["num_traces_in_file"]

print(f"[DZT] {dzt_path.name}  trace #{trace_idx:,} of {n_total:,}")
print(f"      {len(real_sig)} samples  dt={dt_ns:.6f} ns  window={real_t[-1]:.1f} ns")

mean_trace = None
if args.deringed or args.wavelet_sub:
    # Compute coherent mean from 2000 evenly-spaced traces
    n_avg = 2000
    indices = np.linspace(0, n_total - 1, n_avg, dtype=int)
    all_traces, _ = read_dzt_traces(dzt_path, start_trace=0, num_traces=n_total)
    mean_trace = all_traces[indices].mean(axis=0)
    print(f"[MEAN]   computed mean of {n_avg} evenly-spaced traces")

if args.deringed:
    pk_real = np.max(np.abs(real_sig))
    pk_mean = np.max(np.abs(mean_trace))
    mean_scaled = mean_trace * (pk_real / pk_mean) if pk_mean > 0 else mean_trace
    real_sig = real_sig - mean_scaled
    print(f"[DERING] subtracted mean — residual peak = {np.max(np.abs(real_sig)):.1f} counts")

# ── plot ─────────────────────────────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(12, 4))

bpf_tag = "+BPF(100-800MHz)" if args.bpf else ""
ws_tag  = "+WavSub"          if args.wavelet_sub else ""

if args.syn:
    t_common, syn_norm, real_norm, r, dt_syn = _align_synthetic(
        args.syn, real_t, real_sig, dt_ns, mean_trace,
        args.bpf, args.wavelet_sub)
    syn_path = Path(args.syn)
    print(f"[SYN1] {syn_path.name}  dt={dt_syn:.6f} ns  r={r:.4f}")

    real_label = f"Real DZT {'(de-ringed) ' if args.deringed else ''}(trace #{trace_idx:,})"
    ax.plot(t_common, real_norm, "b-", lw=1.1, label=real_label, zorder=3)
    ax.plot(t_common, syn_norm,  "r-", lw=0.9, alpha=0.85,
            label=f"{syn_path.name}  (flip{bpf_tag}{ws_tag})  r={r:.3f}")

    if args.syn2:
        t_c2, syn2_norm, _, r2, dt_syn2 = _align_synthetic(
            args.syn2, real_t, real_sig, dt_ns, mean_trace,
            args.bpf, args.wavelet_sub)
        syn2_path = Path(args.syn2)
        print(f"[SYN2] {syn2_path.name}  dt={dt_syn2:.6f} ns  r={r2:.4f}")
        ax.plot(t_c2, syn2_norm, color="darkorange", lw=0.9, alpha=0.85,
                label=f"{syn2_path.name}  (flip{bpf_tag}{ws_tag})  r={r2:.3f}")

        ax.set_title(
            f"Real vs Synthetic comparison — trace #{trace_idx:,}\n"
            f"{syn_path.name}  r={r:.3f}    |    "
            f"{syn2_path.name}  r={r2:.3f}"
        )
    else:
        tags_list = (["[de-ringed]"] if args.deringed else []) + \
                    (["[BPF]"] if args.bpf else []) + \
                    (["[WavSub]"] if args.wavelet_sub else [])
        tag_str = ("  " + "  ".join(tags_list)) if tags_list else ""
        ax.set_title(
            f"Real vs Synthetic{tag_str} — {syn_path.name}\n"
            f"trace #{trace_idx:,}  |  Pearson r = {r:.4f}"
        )

    ax.set_ylabel("Normalized amplitude")
else:
    ax.plot(real_t, real_sig, "b-", lw=0.8)
    ax.set_ylabel("A/D counts")
    dering_tag = " (de-ringed)" if args.deringed else ""
    ax.set_title(f"Real GPR A-scan{dering_tag} — {dzt_path.name}  trace #{trace_idx:,}")

ax.set_xlabel("Time (ns)")
ax.grid(alpha=0.3)
ax.legend()
fig.tight_layout()
fig.savefig(output_file, dpi=150, bbox_inches="tight")
print(f"[OK]  Saved: {output_file}")
plt.close()
