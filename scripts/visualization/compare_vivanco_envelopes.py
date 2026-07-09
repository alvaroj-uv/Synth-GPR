#!/usr/bin/env python3
"""Compare Vivanco Hilbert envelopes across synthetic scenarios and real DZT.

Produces a single plot with the final-step Hilbert envelope (step 7) from the
Vivanco pipeline for each input, so coda energy differences are visible.

Usage:
    python scripts/visualization/compare_vivanco_envelopes.py

Or with custom files:
    python scripts/visualization/compare_vivanco_envelopes.py \\
        --syn coda_depth_020cm.out:"Homogeneous (Gaussian)" \\
        --syn coda_v7_highphi_excit.out:"V7 hi-phi+excit" \\
        --dzt D:/Codigo/Data/FILE.DZT:15000:"Real DZT" \\
        --out output_test/coda_comparison.png
"""

import sys
import argparse
from pathlib import Path

import numpy as np
import h5py
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from scripts.process_signal_vivanco_method import VivancoPipeline, read_dzt_file

_ALIGN_SHIFT_NS = 4.0   # hardware delay applied to all gprMax .out files
_WINDOW_NS      = 30.0  # coda comparison window (after DW elimination)

_DEFAULT_DZT = (
    "D:/Codigo/Data/"
    "PUERTO-LIMACHE_20230726_EFE_V1_PKC000_588_PKF011_020_CENTRO_BRUTO.DZT"
)
_DEFAULT_DZT_TRACE = 15000

_DEFAULT_SYNTHETICS = [
    ("coda_depth_020cm.out",      "Homogeneous  (Gaussian)"),
    ("coda_depth_020cm_excit.out","Homogeneous  (Excitation)"),
    ("coda_v4.out",               "V4  large rocks (Gaussian)"),
    ("coda_v7_highphi_excit.out", "V7  phi~0.40 + Excitation"),
]

_COLORS = ["steelblue", "darkorange", "seagreen", "crimson", "purple", "saddlebrown"]


def _load_synthetic(path: Path, align_shift_ns: float = _ALIGN_SHIFT_NS,
                    component: str = "Ez"):
    with h5py.File(path, "r") as f:
        # fall back to first available component if requested one is absent
        available = list(f["rxs/rx1"].keys())
        comp = component if component in available else available[0]
        signal = f[f"rxs/rx1/{comp}"][()]
        dt     = float(f.attrs.get("dt", 0.0))
    dt_ns  = dt * 1e9
    if comp == "Ez":
        signal = -signal   # gprMax Ez polarity convention
    pad    = int(round(align_shift_ns / dt_ns))
    signal = np.concatenate([np.zeros(pad), signal])
    return signal, dt_ns


def _vivanco_envelope(signal: np.ndarray, dt_ns: float, window_ns: float = _WINDOW_NS,
                      bandpass_low_hz: float = 150e6, bandpass_high_hz: float = 800e6):
    pipe   = VivancoPipeline(dt_ns=dt_ns)
    result = pipe.process_single_trace(signal, window_length_ns=window_ns,
                                       bandpass_low_hz=bandpass_low_hz,
                                       bandpass_high_hz=bandpass_high_hz)
    env    = result["signal_envelope"]
    t      = np.arange(len(env)) * dt_ns
    return t, env


def _dzt_mean_envelope(dzt_path: Path, trace_idx: int, n_avg: int = 500,
                       window_ns: float = _WINDOW_NS):
    from src.dzt_io import read_dzt_traces
    _, meta   = read_dzt_traces(dzt_path, start_trace=0, num_traces=1)
    n_total   = meta["num_traces_in_file"]
    dt_ns     = meta["sample_interval_ns"]

    # Envelope of the selected single trace
    traces, _ = read_dzt_traces(dzt_path, start_trace=trace_idx, num_traces=1)
    sig       = traces[0].astype(float)
    pipe      = VivancoPipeline(dt_ns=dt_ns)
    result    = pipe.process_single_trace(sig, window_length_ns=window_ns)
    env_single = result["signal_envelope"]
    t = np.arange(len(env_single)) * dt_ns
    return t, env_single, dt_ns, n_total


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--syn",  action="append", default=None,
                    metavar="PATH:LABEL[:LOW_MHZ:HIGH_MHZ]",
                    help="Synthetic .out file with label and optional per-signal bandpass "
                         "(colon-separated). Can be repeated. Default: 4 coda scenarios.")
    ap.add_argument("--freq-band", default="150:800",
                    metavar="LOW_MHZ:HIGH_MHZ",
                    help="Global bandpass fallback in MHz (default: 150:800)")
    ap.add_argument("--dzt",  default=None,
                    metavar="PATH:TRACE:LABEL",
                    help="Real DZT file with trace index and label.")
    ap.add_argument("--no-dzt", action="store_true", help="Skip DZT overlay.")
    ap.add_argument("--window", type=float, default=_WINDOW_NS,
                    help=f"Coda window length in ns (default {_WINDOW_NS})")
    ap.add_argument("--component", default="Ez",
                    help="Field component to read from .out files (default: Ez; use Ey for 3D GSSI)")
    ap.add_argument("--no-shift", action="store_true",
                    help="Skip the 4 ns pre-padding (for 3D GSSI sims whose timing is physical)")
    ap.add_argument("--out", default="output_test/vivanco_coda_comparison.png",
                    help="Output PNG path")
    args = ap.parse_args()

    window_ns = args.window

    # Parse global freq-band fallback
    _gband = args.freq_band.split(":")
    global_low_hz  = float(_gband[0]) * 1e6
    global_high_hz = float(_gband[1]) * 1e6

    # --- build synthetic list: (path, label, low_hz, high_hz) ---
    if args.syn:
        synthetics = []
        for item in args.syn:
            parts = item.split(":")
            path  = parts[0]
            label = parts[1] if len(parts) > 1 else Path(parts[0]).stem
            low   = float(parts[2]) * 1e6 if len(parts) > 2 else global_low_hz
            high  = float(parts[3]) * 1e6 if len(parts) > 3 else global_high_hz
            synthetics.append((path, label, low, high))
    else:
        synthetics = [(p, l, global_low_hz, global_high_hz) for p, l in _DEFAULT_SYNTHETICS]

    # --- build DZT spec ---
    dzt_path, dzt_trace, dzt_label = None, _DEFAULT_DZT_TRACE, "Real DZT"
    if not args.no_dzt:
        if args.dzt:
            # Split on '|' first; fall back to ':' while preserving Windows drive letters
            if "|" in args.dzt:
                parts = args.dzt.split("|")
            else:
                # Split carefully: drive letter "X:" must not be treated as separator
                import re
                parts = re.split(r":(?!\d*[\\/])", args.dzt)
                # re-join drive letter if it was split off (single-char first part)
                if len(parts) > 1 and len(parts[0]) == 1:
                    parts = [parts[0] + ":" + parts[1]] + parts[2:]
            dzt_path  = Path(parts[0])
            dzt_trace = int(parts[1]) if len(parts) > 1 else _DEFAULT_DZT_TRACE
            dzt_label = parts[2]      if len(parts) > 2 else "Real DZT"
        else:
            dzt_path = Path(_DEFAULT_DZT)

    # --- plot ---
    fig, ax = plt.subplots(figsize=(12, 5))
    color_idx = 0

    if dzt_path and dzt_path.exists():
        print(f"[DZT] {dzt_path.name}  trace #{dzt_trace}")
        t_dzt, env_dzt, dt_dzt, n_total = _dzt_mean_envelope(dzt_path, dzt_trace, window_ns=window_ns)
        ax.plot(t_dzt, env_dzt, color="navy", lw=1.8, label=f"{dzt_label} (trace #{dzt_trace:,})")
        color_idx += 1
    elif dzt_path:
        print(f"[WARN] DZT not found: {dzt_path}")

    shift_ns = 0.0 if args.no_shift else _ALIGN_SHIFT_NS
    colors = plt.cm.plasma(np.linspace(0.1, 0.9, max(len(synthetics), 1)))
    for i, (out_path_str, label, low_hz, high_hz) in enumerate(synthetics):
        out_path = Path(out_path_str)
        if not out_path.exists():
            print(f"[SKIP] {out_path} not found")
            continue
        band_tag = f"{low_hz/1e6:.0f}–{high_hz/1e6:.0f} MHz"
        print(f"[SYN]  {out_path.name}  ({label})  bandpass={band_tag}")
        signal, dt_ns = _load_synthetic(out_path, align_shift_ns=shift_ns,
                                        component=args.component)
        t, env = _vivanco_envelope(signal, dt_ns, window_ns=window_ns,
                                   bandpass_low_hz=low_hz, bandpass_high_hz=high_hz)
        color = colors[i] if len(synthetics) > len(_COLORS) else _COLORS[i % len(_COLORS)]
        ax.plot(t, env, color=color, lw=1.2, alpha=0.9, label=f"{label}  [{band_tag}]")

    ax.set_xlabel("Time after DW elimination (ns)")
    ax.set_ylabel("Hilbert envelope amplitude (normalised)")
    ax.set_title(
        f"Vivanco coda comparison — Hilbert envelope step 7\n"
        f"window = {window_ns:.0f} ns after direct-wave cut"
    )
    ax.legend(fontsize=9)
    ax.grid(alpha=0.3)
    fig.tight_layout()

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"[OK]  Saved: {out_path}")


if __name__ == "__main__":
    main()
