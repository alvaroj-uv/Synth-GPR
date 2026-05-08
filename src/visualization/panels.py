from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional

import numpy as np
from matplotlib.axes import Axes

try:
    from src.signal_processing import (
        preprocess_signal,
        calculate_instantaneous_attributes,
        compute_spectrogram,
    )
    HAS_SIGNAL = True
except ImportError:
    HAS_SIGNAL = False

_COLORS = ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd", "#8c564b"]


# ── Signal panels ─────────────────────────────────────────────────────────────

@dataclass
class SignalPanelConfig:
    dewow: bool = True
    gain_type: Optional[str] = None
    gain_alpha: float = 1.0
    components: list = field(default_factory=lambda: ["Ez"])
    receivers: Optional[list] = None
    amplitude_threshold: float = 1e-9


def filter_signals(signals: dict, cfg: SignalPanelConfig) -> dict:
    out = {}
    for name, sig in signals.items():
        if np.max(np.abs(sig)) < cfg.amplitude_threshold:
            continue
        parts = name.split("_")
        if len(parts) >= 2:
            rx_name, comp = parts[0], parts[1]
            if cfg.components and comp not in cfg.components:
                continue
            if cfg.receivers and rx_name not in cfg.receivers:
                continue
        out[name] = sig
    return out


def preprocess_signals(signals: dict, dt: float, cfg: SignalPanelConfig) -> dict:
    if not HAS_SIGNAL or not signals:
        return signals
    out = {}
    for name, sig in signals.items():
        psig, _ = preprocess_signal(
            sig, dt,
            use_dewow=cfg.dewow,
            use_gain=bool(cfg.gain_type),
            gain_params={"type": cfg.gain_type, "alpha": cfg.gain_alpha},
            use_time_zero=True,
        )
        out[name] = psig
    return out


def strongest_signal(signals: dict) -> Optional[np.ndarray]:
    if not signals:
        return None
    return max(signals.values(), key=lambda s: np.max(np.abs(s)))


def draw_ascan(ax: Axes, signals: dict, time_ns: np.ndarray, title: str = "A-scan") -> None:
    """Wiggle A-scan traces. H-field signals drawn dashed."""
    if not signals:
        ax.text(0.5, 0.5, "No signals", ha="center", va="center")
        ax.axis("off")
        return
    for i, (name, sig) in enumerate(signals.items()):
        color = _COLORS[i % len(_COLORS)]
        ls = "--" if name.startswith("H") else "-"
        t = time_ns[:len(sig)]
        ax.plot(t, sig, label=name, color=color, linestyle=ls, linewidth=1.0)
        if ls == "-":
            ax.fill_between(t, sig, 0, where=(sig > 0), color=color,
                            alpha=0.2, interpolate=True)
    ax.axvline(0, color="black", linestyle=":", linewidth=0.8, alpha=0.6)
    ax.set_title(title)
    ax.set_xlabel("Time [ns]")
    ax.grid(True, alpha=0.3)
    ax.legend(loc="upper right", fontsize="small")


def draw_envelope(ax: Axes, signal: np.ndarray, time_ns: np.ndarray,
                  dt: float, title: str = "Envelope / Phase") -> None:
    """Envelope (orange) + cosine phase (grey fill) on a twin axis."""
    if not HAS_SIGNAL or signal is None:
        ax.text(0.5, 0.5, "Unavailable", ha="center", va="center")
        ax.axis("off")
        return
    attrs = calculate_instantaneous_attributes(signal, dt)
    t = time_ns[:len(signal)]
    ax_phase = ax.twinx()
    ax_phase.fill_between(t, attrs["cosine_phase"], color="gray", alpha=0.15,
                          label="Cos phase")
    ax_phase.set_ylim(-1.5, 1.5)
    ax_phase.set_yticks([])
    ax.plot(t, attrs["envelope"], color="orange", linewidth=1.5, label="Envelope")
    ax.set_title(title)
    ax.set_xlabel("Time [ns]")
    ax.grid(True, alpha=0.3)
    h1, l1 = ax.get_legend_handles_labels()
    h2, l2 = ax_phase.get_legend_handles_labels()
    ax.legend(h1 + h2, l1 + l2, loc="upper right", fontsize="small")


def draw_spectrogram(ax: Axes, signal: np.ndarray, dt: float) -> None:
    """Time-frequency spectrogram (inferno colormap, dB scale)."""
    if not HAS_SIGNAL or signal is None:
        ax.text(0.5, 0.5, "Unavailable", ha="center", va="center")
        ax.axis("off")
        return
    fs = 1.0 / dt
    f, t_spec, Sxx = compute_spectrogram(signal, fs=fs, nperseg=128, noverlap=96)
    ax.pcolormesh(t_spec * 1e9, f / 1e6, 10 * np.log10(Sxx + 1e-12),
                  cmap="inferno", shading="gouraud")
    ax.set_title("Spectrogram")
    ax.set_xlabel("Time [ns]")
    ax.set_ylabel("Frequency [MHz]")
    ax.set_ylim(0, 1200)
    ax.grid(True, alpha=0.3, linestyle=":")


# ── Grading curve ─────────────────────────────────────────────────────────────

def draw_grading_curve(ax: Axes, psd_data: Optional[list]) -> None:
    """Geotechnical particle-size distribution curve.

    psd_data: list of [diameter_mm, percent_passing] pairs from SceneData.meta['Lab_PSD'].
    """
    if not psd_data:
        ax.text(0.5, 0.5, "No PSD data", ha="center", va="center", fontsize=9)
        ax.axis("off")
        return

    points = sorted(psd_data, key=lambda p: p[0])
    sizes_mm = np.array([p[0] for p in points])
    passing  = np.array([p[1] for p in points])

    ax.semilogx(sizes_mm, passing, "b-o", linewidth=2, markersize=5,
                label="Grading curve")
    ax.set_title("Particle Size Distribution", fontweight="bold")
    ax.set_xlabel("Particle diameter (mm)")
    ax.set_ylabel("Percent finer (%)")
    ax.set_ylim(0, 100)
    ax.set_xlim(0.001, 100)
    ax.grid(True, which="major", linestyle="-",  linewidth=0.7, alpha=0.7)
    ax.grid(True, which="minor", linestyle=":",  linewidth=0.4, alpha=0.4)

    ax.axvspan(0.001,  0.075, color="#E0E0E0", alpha=0.5)
    ax.axvspan(0.075,  4.75,  color="#FFF9C4", alpha=0.5)
    ax.axvspan(4.75,  100,   color="#FFE0B2", alpha=0.5)
    ax.text(0.005, 5, "Fines",  fontsize=8, color="#666666", rotation=90)
    ax.text(0.2,   5, "Sand",   fontsize=8, color="#666666")
    ax.text(10,    5, "Gravel", fontsize=8, color="#666666")

    ax.axvline(4.75,  color="k", linestyle="--", linewidth=0.8)
    ax.axvline(0.075, color="k", linestyle="--", linewidth=0.8)

    d10 = float(np.interp(10, passing, sizes_mm))
    d30 = float(np.interp(30, passing, sizes_mm))
    d60 = float(np.interp(60, passing, sizes_mm))
    cu  = d60 / d10           if d10 > 0       else 0.0
    cc  = d30**2 / (d10*d60) if d10 * d60 > 0 else 0.0

    stats = (f"$D_{{10}}$ = {d10:.3f} mm\n"
             f"$D_{{30}}$ = {d30:.3f} mm\n"
             f"$D_{{60}}$ = {d60:.3f} mm\n"
             f"$C_u$ = {cu:.2f}\n"
             f"$C_c$ = {cc:.2f}")
    ax.text(0.02, 0.95, stats, transform=ax.transAxes, fontsize=9, va="top",
            bbox=dict(boxstyle="round", facecolor="white", alpha=0.9, edgecolor="gray"))
    ax.legend(loc="lower right", fontsize="small")
