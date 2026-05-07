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


@dataclass
class SignalPanelConfig:
    dewow: bool = True
    gain_type: Optional[str] = None
    gain_alpha: float = 1.0
    components: list = field(default_factory=lambda: ["Ez"])
    receivers: Optional[list] = None
    amplitude_threshold: float = 1e-9


def filter_signals(signals: dict, cfg: SignalPanelConfig) -> dict:
    """Drop signals below threshold and outside component/receiver filters."""
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
    """Apply dewow/gain/time-zero to each signal. Returns signals unchanged if unavailable."""
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
    """Wiggle A-scan traces. H-field signals drawn dashed on the same axis."""
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
