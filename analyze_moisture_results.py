#!/usr/bin/env python3
"""
Analyze moisture sweep results: find optimal sigma to match real trace.
"""

import numpy as np
import h5py
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from scipy.interpolate import interp1d
from pathlib import Path
import sys
sys.path.insert(0, str(Path.cwd()))
from src.signal_processing import dewow

# Real trace
HEADER_SIZE = 128 * 1024
with open("D:/Codigo/Data/PUERTO-LIMACHE_20230726_EFE_V1_PKC000_588_PKF011_020_CENTRO_BRUTO.DZT", 'rb') as f:
    f.seek(HEADER_SIZE + 15000 * 512 * 4)
    real_sig = np.frombuffer(f.read(512 * 4), dtype=np.int32)[2:].astype(float)

real_dt = 50 / 511
real_t = np.arange(len(real_sig)) * real_dt

dewowd = dewow(real_sig, 50)
real_peak_idx = np.argmax(np.abs(dewowd))
real_peak_t = real_t[real_peak_idx]
real_sig_norm = real_sig / np.max(np.abs(real_sig))

# Real decay in first 7ns (Vivanco window)
real_window_start = real_peak_t + 4.5
real_window_end = real_window_start + 7.0
real_mask = (real_t >= real_window_start) & (real_t <= real_window_end)
real_window = real_sig_norm[real_mask]

analytic = real_window + 1j * np.imag(np.fft.fft(real_window))
real_env = np.abs(analytic)
log_env = np.log10(np.maximum(real_env, 1e-6))
t_sample = np.arange(len(real_window)) * real_dt * 1e-9
real_decay = np.polyfit(t_sample * 1e9, log_env, 1)[0]

print("\n" + "="*80)
print("MOISTURE SWEEP ANALYSIS")
print("="*80 + "\n")
print(f"Target decay rate (real trace): {real_decay:+.6f} dB/ns\n")

sigma_values = [0.0, 0.0001, 0.0005, 0.001, 0.005]
results = []

for sigma in sigma_values:
    out_path = f"moisture_sigma_{sigma}.out"
    if not Path(out_path).exists():
        print(f"[SKIP] {out_path} not found")
        continue

    with h5py.File(out_path, 'r') as f:
        syn_sig = -f['rxs/rx1/Ez'][()]
        syn_dt = f.attrs.get('dt', 0) * 1e9

    # Time shift
    shift = 4.0
    syn_t = np.arange(len(syn_sig)) * syn_dt + shift
    syn_sig_norm = syn_sig / np.max(np.abs(syn_sig))

    # Peak
    dewowd_syn = dewow(syn_sig, 50)
    syn_peak_idx = np.argmax(np.abs(dewowd_syn))
    syn_peak_t = syn_t[syn_peak_idx]

    # Vivanco window decay
    syn_window_start = syn_peak_t + 4.5
    syn_window_end = syn_window_start + 7.0
    syn_mask = (syn_t >= syn_window_start) & (syn_t <= syn_window_end)
    syn_window = syn_sig_norm[syn_mask]

    analytic_syn = syn_window + 1j * np.imag(np.fft.fft(syn_window))
    syn_env = np.abs(analytic_syn)
    log_env_syn = np.log10(np.maximum(syn_env, 1e-6))
    t_sample_syn = np.arange(len(syn_window)) * syn_dt * 1e-9
    syn_decay = np.polyfit(t_sample_syn * 1e9, log_env_syn, 1)[0]

    decay_diff = abs(syn_decay - real_decay)

    # Full and coda correlation (9-35ns)
    common_dt = real_dt
    t_max = min(syn_t[-1], real_t[-1])
    tc = np.arange(0, t_max + common_dt, common_dt)

    f_syn = interp1d(syn_t, syn_sig_norm, kind='cubic', bounds_error=False, fill_value=0)
    f_real = interp1d(real_t, real_sig_norm, kind='cubic', bounds_error=False, fill_value=0)

    syn_i = f_syn(tc)
    real_i = f_real(tc)

    r_full = np.corrcoef(syn_i, real_i)[0, 1]

    mask_coda = tc >= 9
    r_coda = np.corrcoef(syn_i[mask_coda], real_i[mask_coda])[0, 1]

    results.append({
        'sigma': sigma,
        'syn_decay': syn_decay,
        'decay_diff': decay_diff,
        'r_full': r_full,
        'r_coda': r_coda,
        'syn_peak_t': syn_peak_t,
        'syn_sig_norm': syn_sig_norm,
        'syn_t': syn_t
    })

    print(f"sigma = {sigma:.4f} S/m:")
    print(f"  Decay: {syn_decay:+.6f} dB/ns (diff: {decay_diff:.6f})")
    print(f"  Full r: {r_full:+.6f}")
    print(f"  Coda r: {r_coda:+.6f}\n")

# Summarize
print("="*80)
print("SUMMARY")
print("="*80 + "\n")

if results:
    best_decay = min(results, key=lambda x: x['decay_diff'])
    best_coda = max(results, key=lambda x: x['r_coda'])

    print(f"Best decay match (target: {real_decay:.6f} dB/ns):")
    print(f"  sigma = {best_decay['sigma']:.4f} S/m")
    print(f"  Achieved: {best_decay['syn_decay']:+.6f} dB/ns (diff: {best_decay['decay_diff']:.6f})")
    print(f"  Coda r = {best_decay['r_coda']:+.6f}\n")

    print(f"Best coda correlation:")
    print(f"  sigma = {best_coda['sigma']:.4f} S/m")
    print(f"  Decay: {best_coda['syn_decay']:+.6f} dB/ns (diff from target: {best_coda['decay_diff']:.6f})")
    print(f"  Coda r = {best_coda['r_coda']:+.6f}\n")

    # Visualization
    fig = plt.figure(figsize=(18, 10))
    fig.patch.set_facecolor("#0f1117")
    gs = gridspec.GridSpec(2, 3, figure=fig, hspace=0.3, wspace=0.3,
                          left=0.07, right=0.96, top=0.93, bottom=0.08)

    # Row 1: Sample traces for key sigma values
    for idx, r in enumerate(results[:3]):
        ax = fig.add_subplot(gs[0, idx])
        ax.set_facecolor("#1a1e2b")

        peak_t = r['syn_peak_t']
        window_start = peak_t + 4.5
        window_end = window_start + 7.0

        full_mask = (r['syn_t'] >= 0) & (r['syn_t'] <= 35)
        ax.plot(r['syn_t'][full_mask], r['syn_sig_norm'][full_mask], color="#00ffff", lw=1.0, alpha=0.8)
        ax.axvspan(window_start, window_end, alpha=0.2, color='#ffff00')
        ax.axvline(peak_t, color='#ff00ff', linestyle='--', linewidth=1.5, alpha=0.6)

        ax.set_ylabel("Amplitude", fontsize=10, color="#c8d0e0", fontweight='bold')
        ax.set_title(f"sigma={r['sigma']:.4f}: Decay={r['syn_decay']:+.4f} dB/ns",
                    fontsize=11, color="#00ffff", fontweight='bold')
        ax.grid(True, color="#2a2f42", alpha=0.2)
        ax.tick_params(colors="#c8d0e0", labelsize=8)
        for spine in ax.spines.values():
            spine.set_color("#2a2f42")
        ax.set_xlim(0, 35)

    # Row 2: Metrics
    ax_decay = fig.add_subplot(gs[1, 0])
    ax_decay.set_facecolor("#1a1e2b")
    sigmas = [r['sigma'] for r in results]
    decays = [r['syn_decay'] for r in results]
    ax_decay.plot(sigmas, decays, marker='o', color='#ffff00', lw=2.0, markersize=8, label='Synthetic')
    ax_decay.axhline(real_decay, color='#ff6b35', linestyle='--', lw=2.0, label='Real target')
    ax_decay.set_xlabel("Sigma (S/m)", fontsize=10, color="#c8d0e0", fontweight='bold')
    ax_decay.set_ylabel("Decay Rate (dB/ns)", fontsize=10, color="#c8d0e0", fontweight='bold')
    ax_decay.set_title("Decay Rate vs Conductivity", fontsize=11, color="#ffff00", fontweight='bold')
    ax_decay.set_xscale('log')
    ax_decay.grid(True, color="#2a2f42", alpha=0.2)
    ax_decay.tick_params(colors="#c8d0e0", labelsize=9)
    ax_decay.legend(fontsize=9, facecolor='#1a1e2b', labelcolor='#c8d0e0', edgecolor='#2a2f42')
    for spine in ax_decay.spines.values():
        spine.set_color("#2a2f42")

    ax_coda = fig.add_subplot(gs[1, 1])
    ax_coda.set_facecolor("#1a1e2b")
    coda_rs = [r['r_coda'] for r in results]
    ax_coda.plot(sigmas, coda_rs, marker='s', color='#00ff00', lw=2.0, markersize=8, label='Coda r')
    ax_coda.axhline(best_coda['r_coda'], color='#ff00ff', linestyle='--', lw=1.5, alpha=0.6)
    ax_coda.set_xlabel("Sigma (S/m)", fontsize=10, color="#c8d0e0", fontweight='bold')
    ax_coda.set_ylabel("Coda Correlation (r)", fontsize=10, color="#c8d0e0", fontweight='bold')
    ax_coda.set_title("Coda Correlation vs Conductivity", fontsize=11, color="#00ff00", fontweight='bold')
    ax_coda.set_xscale('log')
    ax_coda.grid(True, color="#2a2f42", alpha=0.2)
    ax_coda.tick_params(colors="#c8d0e0", labelsize=9)
    ax_coda.legend(fontsize=9, facecolor='#1a1e2b', labelcolor='#c8d0e0', edgecolor='#2a2f42')
    for spine in ax_coda.spines.values():
        spine.set_color("#2a2f42")

    ax_table = fig.add_subplot(gs[1, 2])
    ax_table.axis('off')
    ax_table.set_facecolor("#0f1117")

    table_text = f"""OPTIMAL CONDUCTIVITY

Real Trace Target:
  Decay: {real_decay:+.6f} dB/ns
  Peak-relative window:
    Start: {real_peak_t+4.5:.2f} ns
    Duration: 7 ns

Best Match (Decay):
  sigma: {best_decay['sigma']:.4f} S/m
  Decay: {best_decay['syn_decay']:+.6f} dB/ns
  Diff: {best_decay['decay_diff']:.6f}
  Coda r: {best_decay['r_coda']:+.6f}

Best Match (Correlation):
  sigma: {best_coda['sigma']:.4f} S/m
  Decay: {best_coda['syn_decay']:+.6f} dB/ns
  Coda r: {best_coda['r_coda']:+.6f}

RECOMMENDATION:
Use sigma = {best_coda['sigma']:.4f} S/m
for production dataset
"""

    ax_table.text(0.05, 0.95, table_text, transform=ax_table.transAxes,
            fontsize=10, verticalalignment='top', fontfamily='monospace',
            bbox=dict(boxstyle='round', facecolor='#1a1e2b', alpha=0.95, edgecolor='#2a2f42', linewidth=2),
            color='#c8d0e0')

    fig.suptitle(
        "Moisture Sweep: Optimal Conductivity to Match Real Field Attenuation\n" +
        f"Real decay: {real_decay:+.6f} dB/ns | Best synthetic: {best_decay['syn_decay']:+.6f} dB/ns @ sigma={best_decay['sigma']:.0e}",
        color="#c8d0e0", fontsize=13, fontweight='bold', y=0.98
    )

    png_path = Path("output_test") / "moisture_sweep_analysis.png"
    fig.savefig(png_path, dpi=150, bbox_inches='tight', facecolor="#0f1117")
    print(f"[SAVE] {png_path}\n")

print("="*80 + "\n")
