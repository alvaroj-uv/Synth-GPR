#!/usr/bin/env python3
"""
Compare A-scan statistics across multiple gprMax .out simulation files.

Reads a manifest.json (produced by create_material_variants.py) alongside
the corresponding .out files, then computes per-waveform statistics and
generates a comparison report + plots.

Usage:
    python compare_simulations.py sweep_output/ --out report.png
"""

import argparse
import json
import sys
from pathlib import Path

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import h5py


def load_ascan(out_path: Path):
    """Load Ez A-scan from gprMax .out HDF5 file. Returns (t_ns, ez) or (None, None)."""
    if not out_path.exists():
        return None, None
    with h5py.File(out_path, "r") as f:
        dt  = float(f.attrs["dt"])
        ez  = f["rxs"]["rx1"]["Ez"][:]
        t   = np.arange(len(ez)) * dt * 1e9
    return t, ez


def waveform_stats(t_ns, ez):
    """Compute key statistics from an A-scan waveform."""
    if ez is None:
        return {}
    peak_idx    = np.argmax(np.abs(ez))
    energy      = np.sum(ez ** 2)
    rms         = np.sqrt(np.mean(ez ** 2))
    # First significant reflection: first peak after 1 ns
    mask        = t_ns > 1.0
    if mask.any():
        first_peak_t = t_ns[mask][np.argmax(np.abs(ez[mask]))]
    else:
        first_peak_t = float(t_ns[peak_idx])

    return {
        "peak_amplitude_Vm":  float(np.max(np.abs(ez))),
        "peak_time_ns":       float(t_ns[peak_idx]),
        "first_reflection_ns":float(first_peak_t),
        "rms_Vm":             float(rms),
        "energy_V2s":         float(energy),
        "signal_duration_ns": float(t_ns[-1]),
        "samples":            int(len(ez)),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("sweep_dir", type=Path, help="Directory with manifest.json and .out files")
    parser.add_argument("--out", type=Path, default=None,
                        help="Output PNG for comparison report (default: sweep_dir/comparison.png)")
    args = parser.parse_args()

    manifest_path = args.sweep_dir / "manifest.json"
    if not manifest_path.exists():
        print(f"ERROR: manifest.json not found in {args.sweep_dir}")
        sys.exit(1)

    manifest = json.loads(manifest_path.read_text())
    loaded_manifest = manifest   # keep reference for direct wave removal section
    out_png   = args.out or args.sweep_dir / "comparison.png"

    print("=" * 70)
    print("SIMULATION COMPARISON REPORT")
    print("=" * 70)
    print()

    results = []
    for entry in manifest:
        in_path  = Path(entry["in_file"])
        out_path = in_path.with_suffix(".out")
        t, ez    = load_ascan(out_path)
        stats    = waveform_stats(t, ez) if ez is not None else {}
        entry["stats"] = stats
        entry["t_ns"]  = t.tolist() if t is not None else None
        entry["ez"]    = ez.tolist() if ez is not None else None
        entry["ran"]   = ez is not None

        status = "OK" if entry["ran"] else "MISSING"
        print(f"  [{entry['index']:02d}] {entry['label']:20s}  [{status}]")
        if entry["ran"]:
            s = stats
            print(f"        Peak: {s['peak_amplitude_Vm']:8.1f} V/m  @ {s['peak_time_ns']:.2f} ns")
            print(f"        RMS:  {s['rms_Vm']:8.1f} V/m    Energy: {s['energy_V2s']:.3e} V²s")
            print(f"        1st reflection: {s['first_reflection_ns']:.2f} ns")
        print()
        results.append(entry)

    ran = [r for r in results if r["ran"]]
    if not ran:
        print("No simulation outputs found. Run gprMax first.")
        sys.exit(1)

    # ── Direct wave removal: three methods (Wang 2017 + Liu 2017) ────────────
    #
    # Method 1: Time gating (Wang §2.2, Li [2])
    #   Zero samples before t_gate = 2*antenna_height/c + 1/f_center
    #   (two-way travel through air + pulse half-width)
    #   Deterministic — works on a single trace without needing other traces.
    #
    # Method 2: Background subtraction (Wang Eq.19–24)
    #   Direct wave r(x,t) = r1(t)*r2(x) — separable.
    #   All traces share same geometry → r2(x) identical → subtract mean = remove r1*r2.
    #   Equivalent to Li (2004) adaptive interference canceling cited in Wang §1.
    #   Requires multiple traces (not valid for a single isolated A-scan).
    #
    # We apply both and show both in the report.

    import sys as _sys; _sys.path.insert(0, str(Path(__file__).parent.parent.parent))
    from src.signal_processing import (
        time_gate, mean_trace, background_subtraction, svd_remove_direct_wave
    )

    C       = 3e8
    air_gap = 0.3    # m above ballast surface
    f_0     = 400e6  # Hz
    all_ez  = np.array([r["ez"] for r in ran], dtype=float)  # (N, samples)
    t_ns_arr = np.array(ran[0]["t_ns"])
    dt_s    = float(t_ns_arr[1] - t_ns_arr[0]) * 1e-9

    # Method 1: time gate (Wang §2.2) — single trace
    t_gate_ns = (2 * air_gap / C + 1.0 / f_0) * 1e9
    gated_ez  = np.array([time_gate(ez, dt_s, t_gate_ns) for ez in all_ez])

    # Method 2: background subtraction (Wang Eq.19-24) — mean across traces
    bg_ez     = mean_trace(all_ez)
    resid_ez  = all_ez - bg_ez

    # Method 3: SVD direct wave removal (Liu §3.2) — zero first singular value
    svd_ez    = svd_remove_direct_wave(all_ez)  # (N, samples)

    def _make_stats(arr, t, ref_rms):
        peak_idx = np.argmax(np.abs(arr))
        snr      = 20 * np.log10((np.max(np.abs(arr)) + 1e-12) / (ref_rms + 1e-12))
        return {
            "peak_amplitude_Vm": float(np.max(np.abs(arr))),
            "peak_time_ns":      float(t[peak_idx]),
            "rms_Vm":            float(np.sqrt(np.mean(arr**2))),
            "snr_db":            float(snr),
        }

    ref_rms = float(np.sqrt(np.mean(bg_ez**2)))

    for i, r in enumerate(ran):
        t = np.array(r["t_ns"])
        r["gated"]      = gated_ez[i].tolist()
        r["residual"]   = resid_ez[i].tolist()
        r["svd"]        = svd_ez[i].tolist()
        r["gate_stats"] = _make_stats(gated_ez[i],  t, ref_rms)
        r["res_stats"]  = _make_stats(resid_ez[i],  t, ref_rms)
        r["svd_stats"]  = _make_stats(svd_ez[i],    t, ref_rms)

    print(f"\n--- Method 1: Time gate (Wang §2.2)  t_gate={t_gate_ns:.1f}ns ---")
    print(f"  {'Label':20s}  {'Peak (V/m)':>12}  {'@t (ns)':>8}  {'RMS':>8}")
    for r in ran:
        s = r["gate_stats"]
        print(f"  {r['label']:20s}  {s['peak_amplitude_Vm']:12.2f}  {s['peak_time_ns']:8.2f}  {s['rms_Vm']:8.3f}")

    print(f"\n--- Method 2: Background subtraction (Wang Eq.19-24, mean removed) ---")
    print(f"  {'Label':20s}  {'Peak (V/m)':>12}  {'@t (ns)':>8}  {'RMS':>8}  {'SNR (dB)':>9}")
    for r in ran:
        s = r["res_stats"]
        print(f"  {r['label']:20s}  {s['peak_amplitude_Vm']:12.3f}  {s['peak_time_ns']:8.2f}  {s['rms_Vm']:8.3f}  {s['snr_db']:9.1f}")

    print(f"\n--- Method 3: SVD sv1=0 (Liu §3.2, zero first singular value) ---")
    print(f"  {'Label':20s}  {'Peak (V/m)':>12}  {'@t (ns)':>8}  {'RMS':>8}  {'SNR (dB)':>9}")
    for r in ran:
        s = r["svd_stats"]
        print(f"  {r['label']:20s}  {s['peak_amplitude_Vm']:12.3f}  {s['peak_time_ns']:8.2f}  {s['rms_Vm']:8.3f}  {s['snr_db']:9.1f}")

    # ── Figures: 4×3 grid — raw + 3 direct-wave removal methods ─────────────
    cmap   = plt.cm.viridis(np.linspace(0, 1, len(ran)))
    labels = [r["label"] for r in ran]
    t_ref  = np.array(ran[0]["t_ns"])

    fig, axes = plt.subplots(4, 3, figsize=(20, 22), dpi=130)
    fig.suptitle(
        "Material Permittivity Sweep — Direct Wave Removal Comparison\n"
        "Method 1: Time gate (Wang §2.2)  |  "
        "Method 2: Background subtraction (Wang Eq.19-24)  |  "
        "Method 3: SVD sv1=0 (Liu §3.2)",
        fontsize=11, fontweight="bold"
    )

    def _plot_traces(ax, key, title, ylabel="Ez (V/m)", xlim=None, vline=None):
        for i, r in enumerate(ran):
            y = np.array(r[key])
            x = t_ref[:len(y)]
            if xlim:
                mask = x <= xlim; ax.plot(x[mask], y[mask], lw=0.8, color=cmap[i], label=r["label"])
            else:
                ax.plot(x, y, lw=0.7, color=cmap[i], label=r["label"])
        if vline:
            ax.axvline(vline, color="red", lw=1.5, ls="--", label=f"gate {vline:.1f}ns")
        ax.set_title(title, fontweight="bold", fontsize=9)
        ax.set_xlabel("Time (ns)"); ax.set_ylabel(ylabel)
        ax.axhline(0, color="k", lw=0.3); ax.grid(True, alpha=0.2)
        ax.legend(fontsize=5, ncol=2)

    def _plot_bar(ax, key_stats, stat_key, title, xlabel):
        vals = [r[key_stats][stat_key] for r in ran]
        bars = ax.barh(range(len(ran)), vals, color=cmap)
        ax.set_yticks(range(len(ran))); ax.set_yticklabels(labels, fontsize=8)
        ax.set_title(title, fontweight="bold", fontsize=9)
        ax.set_xlabel(xlabel); ax.grid(True, alpha=0.2, axis="x")
        for bar, val in zip(bars, vals):
            ax.text(max(val * 0.02, 0.01), bar.get_y() + bar.get_height()/2,
                    f"{val:.2f}", va="center", fontsize=7)

    # ── Row 0: Raw ──────────────────────────────────────────────────────────
    _plot_traces(axes[0, 0], "ez", "Raw A-Scans (direct wave dominates)")
    _plot_traces(axes[0, 1], "ez", f"Zoom 0-15ns (gate={t_gate_ns:.1f}ns)", xlim=15, vline=t_gate_ns)
    ax = axes[0, 2]
    ax.plot(t_ref, bg_ez, "k-", lw=1.2, label="Mean (direct wave)")
    ax.fill_between(t_ref, bg_ez - np.std(all_ez, axis=0),
                           bg_ez + np.std(all_ez, axis=0), alpha=0.2, color="blue", label="±1 std")
    ax.set_title("Removed Common Mode (Methods 2 & 3)", fontweight="bold", fontsize=9)
    ax.set_xlabel("Time (ns)"); ax.set_ylabel("Ez (V/m)")
    ax.axhline(0, color="k", lw=0.3); ax.grid(True, alpha=0.2); ax.legend(fontsize=8)

    # ── Row 1: Method 1 — Time gate ─────────────────────────────────────────
    _plot_traces(axes[1, 0], "gated", f"Method 1: Time gate (Wang §2.2, t>{t_gate_ns:.1f}ns)")
    _plot_bar(axes[1, 1], "gate_stats", "peak_amplitude_Vm", "Method 1: Peak amplitude (V/m)", "Peak |Ez| (V/m)")
    _plot_bar(axes[1, 2], "gate_stats", "rms_Vm",            "Method 1: RMS (V/m)",            "RMS (V/m)")

    # ── Row 2: Method 2 — Background subtraction ────────────────────────────
    _plot_traces(axes[2, 0], "residual", "Method 2: Background subtraction (Wang Eq.19-24)")
    _plot_bar(axes[2, 1], "res_stats",  "peak_amplitude_Vm", "Method 2: Peak amplitude (V/m)", "Peak |Ez| (V/m)")
    _plot_bar(axes[2, 2], "res_stats",  "rms_Vm",            "Method 2: RMS (V/m)",            "RMS (V/m)")

    # ── Row 3: Method 3 — SVD ───────────────────────────────────────────────
    _plot_traces(axes[3, 0], "svd", "Method 3: SVD sv1=0 (Liu §3.2)")
    _plot_bar(axes[3, 1], "svd_stats",  "peak_amplitude_Vm", "Method 3: Peak amplitude (V/m)", "Peak |Ez| (V/m)")
    _plot_bar(axes[3, 2], "svd_stats",  "rms_Vm",            "Method 3: RMS (V/m)",            "RMS (V/m)")

    plt.tight_layout()
    plt.savefig(out_png, dpi=130, bbox_inches="tight")
    print(f"\nComparison report saved: {out_png}")

    # ── Delta table: all three methods ───────────────────────────────────────
    print()
    print("DELTA TABLE vs. baseline (dry_clean), all three DW removal methods:")
    print()
    header = f"  {'Label':20s}  {'Gate Peak%':>10}  {'BgSub Peak%':>11}  {'SVD Peak%':>10}  {'SVD SNR':>8}"
    print(header)
    print("  " + "-" * 68)
    bp_g = ran[0]["gate_stats"]["peak_amplitude_Vm"]
    bp_r = ran[0]["res_stats"]["peak_amplitude_Vm"]
    bp_s = ran[0]["svd_stats"]["peak_amplitude_Vm"]
    for r in ran:
        dg = (r["gate_stats"]["peak_amplitude_Vm"] - bp_g) / (bp_g + 1e-12) * 100
        dr = (r["res_stats"]["peak_amplitude_Vm"]  - bp_r) / (bp_r + 1e-12) * 100
        ds = (r["svd_stats"]["peak_amplitude_Vm"]  - bp_s) / (bp_s + 1e-12) * 100
        sn = r["svd_stats"]["snr_db"]
        print(f"  {r['label']:20s}  {dg:+9.1f}%  {dr:+10.1f}%  {ds:+9.1f}%  {sn:+7.1f}dB")

    print()
    print("=" * 70)


if __name__ == "__main__":
    main()
