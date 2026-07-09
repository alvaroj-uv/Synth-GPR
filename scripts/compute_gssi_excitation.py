#!/usr/bin/env python3
"""Compute the GSSI 400-MHz calibrated antenna excitation for gprMax.

Reads the DZT mean trace (hardware response W_real) and a gprMax free-space
or direct-wave simulation (W_sim), computes a Wiener correction filter, and
applies it to the gprMax Gaussian source current I_g to produce a calibrated
I_cal(t) that bakes the real GSSI hardware response into every simulation.

Linearity argument
------------------
    gprMax run with I_g   →  received = W_sim (known from .out file)
    gprMax run with I_cal →  received = W_real (desired)
    ⟹ I_cal = I_g × H_correction        (in frequency domain)
       H_correction(ω) = W_real(ω) · W_sim*(ω) / (|W_sim|² + α·max)

Outputs
-------
    {out_dir}/gssi_excitation.txt   — gprMax #excitation_file (time + amplitude)
    {out_dir}/H_correction.npy      — Wiener filter for post-processing (complex)
    {out_dir}/calibration_diag.png  — four-panel verification plot

Usage
-----
    python scripts/compute_gssi_excitation.py \\
        --syn  coda_depth_020cm.out \\
        --out  calibration/

gprMax .in file integration:
    # Remove the #waveform line.  Add:
    #excitation_file: calibration/gssi_excitation.txt
    # Change the #hertzian_dipole waveform ID to match:
    #hertzian_dipole: z <x> <y> <z> gssi_420mhz
"""

import sys
import argparse
from pathlib import Path

import numpy as np
import numpy.fft as _fft
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy.interpolate import interp1d

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.dzt_io import read_dzt_traces
from src.data_loader import read_ascan

# ── defaults ──────────────────────────────────────────────────────────────────
_DZT_DEFAULT = (
    "D:/Codigo/Data/"
    "PUERTO-LIMACHE_20230726_EFE_V1_PKC000_588_PKF011_020_CENTRO_BRUTO.DZT"
)
_SYN_DEFAULT = "coda_depth_020cm.out"

# Alignment (validated in visualize_dzt_sample_trace.py)
_SHIFT_NS  = 4.0   # hardware cable + filter delay offset
_DW_LO_NS  = 3.5   # direct-wave window start (ns, in aligned time)
_DW_HI_NS  = 9.0   # direct-wave window end   (ns, in aligned time)
_ALPHA     = 1e-2  # Wiener regularisation
_N_AVG     = 2000  # number of DZT traces to average for W_real


# ── gprMax Gaussian source current ────────────────────────────────────────────
def _gprmax_gaussian(t_s: np.ndarray, freq_hz: float) -> np.ndarray:
    """gprMax 'gaussian' waveform (unit amplitude).

    Exact formula from gprMax/waveforms.py (Big Smoke v3):
        chi  = 1 / freq
        zeta = 2 * pi^2 * freq^2
        I(t) = exp(-zeta * (t - chi)^2)
    """
    chi  = 1.0 / freq_hz
    zeta = 2.0 * np.pi**2 * freq_hz**2
    return np.exp(-zeta * (t_s - chi)**2)


# ── Wiener correction filter ───────────────────────────────────────────────────
def _wiener(w_real: np.ndarray, w_sim: np.ndarray,
            n_fft: int, alpha: float) -> np.ndarray:
    """H(ω) = W_real · W_sim* / (|W_sim|² + α · max|W_sim|²)."""
    W_r = _fft.rfft(w_real, n=n_fft)
    W_s = _fft.rfft(w_sim,  n=n_fft)
    pwr = np.abs(W_s)**2
    return W_r * np.conj(W_s) / (pwr + alpha * pwr.max())


# ── main ──────────────────────────────────────────────────────────────────────
def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--dzt",  default=_DZT_DEFAULT, help="DZT file (real field data)")
    ap.add_argument("--syn",  default=_SYN_DEFAULT,
                    help="gprMax .out file used as W_sim reference")
    ap.add_argument("--freq", type=float, default=420e6,
                    help="Source frequency Hz (default: 420e6)")
    ap.add_argument("--out",  default="calibration",
                    help="Output directory (created if absent)")
    ap.add_argument("--id",   default=None, dest="wf_id",
                    help="Waveform column ID (default: gssi_{N}mhz)")
    args = ap.parse_args()

    freq_hz  = args.freq
    out_dir  = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)
    dzt_path = Path(args.dzt)
    syn_path = Path(args.syn)
    wf_id    = args.wf_id or f"gssi_{int(freq_hz / 1e6)}mhz"

    # ── 1. load DZT mean trace (W_real) ──────────────────────────────────────
    print(f"[DZT] {dzt_path.name}")
    _traces_meta, meta0 = read_dzt_traces(dzt_path, start_trace=0, num_traces=1)
    n_total   = meta0["num_traces_in_file"]
    dt_real_ns = meta0["sample_interval_ns"]

    print(f"      Loading all {n_total:,} traces for mean…")
    all_traces, _ = read_dzt_traces(dzt_path, start_trace=0, num_traces=n_total)
    indices    = np.linspace(0, n_total - 1, _N_AVG, dtype=int)
    mean_trace = all_traces[indices].mean(axis=0)
    real_t     = np.arange(len(mean_trace)) * dt_real_ns

    print(f"      mean of {_N_AVG}  |  dt={dt_real_ns:.5f} ns  |  "
          f"window={real_t[-1]:.1f} ns")

    # ── 2. load gprMax simulation (W_sim) ────────────────────────────────────
    print(f"[SYN] {syn_path}")
    d       = read_ascan(syn_path, component="Ez")
    syn_raw = d["signal"]
    dt_syn  = d["dt"] * 1e9          # s → ns
    syn_t   = np.arange(len(syn_raw)) * dt_syn

    print(f"      {len(syn_raw)} samples  dt={dt_syn:.6f} ns")

    # ── 3. align W_sim → common time grid at dt_real ─────────────────────────
    syn_flip = -syn_raw   # flip polarity

    shift_samp  = int(np.round(_SHIFT_NS / dt_syn))
    syn_shifted = np.concatenate([np.zeros(shift_samp), syn_flip])[:len(syn_flip)]

    t_end    = min(syn_t[-1], real_t[-1])
    t_common = np.arange(0, t_end, dt_real_ns)
    n_common = len(t_common)

    syn_on_common  = interp1d(syn_t, syn_shifted, kind="cubic",
                              bounds_error=False, fill_value=0.0)(t_common)
    real_on_common = interp1d(real_t, mean_trace,  kind="cubic",
                              bounds_error=False, fill_value=0.0)(t_common)

    # ── 4. direct-wave windows ────────────────────────────────────────────────
    i0    = int(_DW_LO_NS / dt_real_ns)
    i1    = int(_DW_HI_NS / dt_real_ns)
    taper = np.hanning(i1 - i0)

    w_sim  = syn_on_common[i0:i1]  * taper
    w_real = real_on_common[i0:i1] * taper

    n_fft = 4 * n_common   # zero-pad for spectral resolution

    # ── 5. Wiener correction filter ───────────────────────────────────────────
    H = _wiener(w_real, w_sim, n_fft, _ALPHA)

    freqs_MHz = _fft.rfftfreq(n_fft, d=dt_real_ns * 1e-9) / 1e6
    band_mask = (freqs_MHz >= 100) & (freqs_MHz <= 800)
    print(f"[H]   Wiener filter computed  |  "
          f"|H| in 100-800 MHz: {np.abs(H[band_mask]).mean():.3f} +/- "
          f"{np.abs(H[band_mask]).std():.3f}")

    # ── 6. gprMax Gaussian source current I_g at dt_real ─────────────────────
    t_excit_s  = t_common * 1e-9         # ns → s
    I_g        = _gprmax_gaussian(t_excit_s, freq_hz)

    chi_ns  = 1.0 / freq_hz * 1e9
    sig_ps  = 1e12 / (2.0 * np.pi * freq_hz)
    print(f"[I_g] gaussian  peak at chi = {chi_ns:.3f} ns  "
          f"sigma ~ {sig_ps:.0f} ps  (f = {freq_hz/1e6:.0f} MHz)")

    # ── 7. calibrated source: I_cal = IFFT( FFT(I_g) × H ) ──────────────────
    I_g_fft   = _fft.rfft(I_g, n=n_fft)
    I_cal_raw = _fft.irfft(I_g_fft * H, n=n_fft)[:n_common]

    # Peak-normalise to unit amplitude (gprMax #hertzian_dipole amplitude
    # controls absolute scaling; we embed shape only)
    pk    = np.max(np.abs(I_cal_raw))
    I_cal = I_cal_raw / pk

    peak_idx = np.argmax(np.abs(I_cal))
    print(f"[I_cal] calibrated source peak at {t_common[peak_idx]:.2f} ns  "
          f"(pre-norm pk = {pk:.4g})")

    # ── 8. write gprMax excitation file ──────────────────────────────────────
    # gprMax evaluates at t + 0.5*dt_syn (half-step), which can fall slightly
    # beyond the nominal time window.  Append zero-amplitude samples up to
    # 1.05 × the DZT window to ensure the interpolator never goes out of range.
    t_max_s    = t_excit_s[-1] * 1.05
    n_extra    = int(np.ceil((t_max_s - t_excit_s[-1]) / (dt_real_ns * 1e-9))) + 1
    t_extra    = t_excit_s[-1] + np.arange(1, n_extra + 1) * dt_real_ns * 1e-9
    excit_path = out_dir / "gssi_excitation.txt"
    with open(excit_path, "w") as f:
        f.write(f"time {wf_id}\n")
        for t_s, amp in zip(t_excit_s, I_cal):
            f.write(f"{t_s:.10e} {amp:.8e}\n")
        for t_s in t_extra:
            f.write(f"{t_s:.10e} 0.00000000e+00\n")

    print(f"[OUT] {excit_path}")
    print(f"      {len(I_cal)} lines  |  dt = {dt_real_ns:.5f} ns  |  "
          f"waveform ID: '{wf_id}'")

    # ── 9. save H_correction for post-processing ──────────────────────────────
    H_path = out_dir / "H_correction.npy"
    np.save(H_path, H)
    print(f"[OUT] {H_path}")

    # ── 10. diagnostic plot ───────────────────────────────────────────────────
    # Verify: apply H to the full aligned synthetic → should match real
    S_corr = _fft.irfft(_fft.rfft(syn_on_common, n=n_fft) * H, n=n_fft)[:n_common]
    pk_r   = np.max(np.abs(real_on_common)); pk_s = np.max(np.abs(syn_on_common))
    real_n = real_on_common / pk_r
    syn_n  = syn_on_common  / pk_s
    corr_n = S_corr / np.max(np.abs(S_corr))
    I_g_n  = I_g    / np.max(np.abs(I_g))

    r_before = np.corrcoef(syn_n,   real_n)[0, 1]
    r_after  = np.corrcoef(corr_n,  real_n)[0, 1]

    fig, axes = plt.subplots(2, 2, figsize=(14, 9))

    ax = axes[0, 0]
    ax.plot(t_common, real_n, "b-",  lw=0.8, label="W_real  (DZT mean trace)")
    ax.plot(t_common, syn_n,  "r-",  lw=0.8, alpha=0.75,
            label=f"W_sim   (gprMax Gaussian)  r = {r_before:.3f}")
    ax.axvspan(_DW_LO_NS, _DW_HI_NS, alpha=0.12, color="green",
               label="Direct-wave window")
    ax.set_title("Before calibration")
    ax.legend(fontsize=8); ax.set_xlabel("Time (ns)")

    ax = axes[0, 1]
    ax.plot(t_common, real_n,  "b-", lw=0.8, label="W_real  (DZT mean trace)")
    ax.plot(t_common, corr_n,  "r-", lw=0.8, alpha=0.75,
            label=f"W_sim × H_correction  r = {r_after:.3f}")
    ax.set_title(f"After calibration  (Δr = {r_after - r_before:+.3f})")
    ax.legend(fontsize=8); ax.set_xlabel("Time (ns)")

    ax = axes[1, 0]
    ax.semilogy(freqs_MHz, np.abs(H), "k-", lw=0.8, label="|H(f)|")
    ax.axvline(100, color="steelblue",  ls="--", lw=0.8, label="100 MHz")
    ax.axvline(800, color="steelblue",  ls=":",  lw=0.8, label="800 MHz")
    ax.set_xlim(0, 2000)
    ax.set_title("H_correction magnitude spectrum")
    ax.set_xlabel("Frequency (MHz)"); ax.legend(fontsize=8)

    ax = axes[1, 1]
    ax.plot(t_common, I_g_n,  "g-",  lw=0.9,
            label=f"I_g   (gprMax Gaussian  {freq_hz/1e6:.0f} MHz)")
    ax.plot(t_common, I_cal,  "k-",  lw=0.9, label="I_cal  (calibrated source)")
    ax.set_xlim(0, 20)
    ax.set_title("Source waveforms  →  excitation file")
    ax.set_xlabel("Time (ns)"); ax.legend(fontsize=8)

    fig.suptitle(
        f"GSSI Antenna Calibration\n"
        f"DZT: {dzt_path.name}   SYN: {syn_path.name}\n"
        f"r (Gaussian → real): {r_before:.3f}  →  {r_after:.3f}  "
        f"after wavelet substitution"
    )
    fig.tight_layout()
    diag_path = out_dir / "calibration_diag.png"
    fig.savefig(diag_path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"[OUT] {diag_path}")

    # ── usage instructions ────────────────────────────────────────────────────
    excit_abs = excit_path.resolve()
    print()
    print("--- gprMax .in file integration ------------------------------------")
    print(f"  1. Remove:   #waveform: gaussian 1.0 {freq_hz:.3e} <any_id>")
    print(f"  2. Add:      #excitation_file: {excit_abs}")
    print(f"  3. Replace:  #hertzian_dipole: z <x> <y> <z> {wf_id}")
    print()
    print("--- TOML (via [[command]] passthrough) -----------------------------")
    print(f'  [[command]]')
    print(f'  raw = "#excitation_file: {excit_abs}"')
    print()
    print(f"  And in [source] remove waveform = \"gaussian\" or set excitation mode.")
    print()
    print(f"Pearson r:  before = {r_before:.4f}   after = {r_after:.4f}")


if __name__ == "__main__":
    main()
