#!/usr/bin/env python3
"""
Vivanco Signal Processing Pipeline
Implements complete signal treatment from Rojas-Vivanco 2025 paper:
1. Direct wave normalization
2. DC-Shift removal (zero-mean centering)
3. Direct wave elimination (time zero + 30-sample shift)
4. Bandpass filter (150-800 MHz)
5. Signal truncation (window of interest)
6. BGR filter (Background Removal, 1000-signal window)
7. Analytic envelope (Hilbert transform)
"""

import sys
from pathlib import Path
from typing import Tuple
import numpy as np
import h5py
from scipy.signal import hilbert, butter, sosfilt, sosfilt_zi, find_peaks
from scipy.interpolate import interp1d


class VivancoPipeline:
    """Complete Vivanco signal processing pipeline."""

    def __init__(self, dt_ns: float, fs_hz: float = None):
        """
        Initialize pipeline with temporal parameters.

        Args:
            dt_ns: Sampling interval in nanoseconds
            fs_hz: Sampling frequency in Hz (computed from dt_ns if not provided)
        """
        self.dt_ns = dt_ns
        self.dt_s = dt_ns * 1e-9
        self.fs_hz = fs_hz if fs_hz is not None else (1.0 / self.dt_s)

    # ========================================================================
    # STEP 1: DIRECT WAVE NORMALIZATION
    # ========================================================================

    def normalize_by_direct_wave(self, signal: np.ndarray,
                                 search_end_idx: int = None) -> Tuple[np.ndarray, int]:
        """
        Normalize signal by the amplitude of the direct wave.

        Returns:
            Normalized signal, peak index of direct wave
        """
        if search_end_idx is None:
            search_end_idx = min(len(signal), int(20 / self.dt_ns))  # First 20 ns

        search_region = signal[:search_end_idx]
        peak_idx = np.argmax(np.abs(search_region))
        peak_amplitude = np.abs(signal[peak_idx])

        if peak_amplitude == 0:
            return signal, peak_idx

        normalized = signal / peak_amplitude
        return normalized, peak_idx

    # ========================================================================
    # STEP 2: DC-SHIFT REMOVAL (ZERO-MEAN CENTERING)
    # ========================================================================

    def remove_dc_shift(self, signal: np.ndarray) -> np.ndarray:
        """Remove DC component by subtracting mean."""
        return signal - np.mean(signal)

    # ========================================================================
    # STEP 3: DIRECT WAVE ELIMINATION
    # ========================================================================

    def eliminate_direct_wave(self, signal: np.ndarray, peak_idx: int,
                             shift_time_ns: float = 4.0) -> Tuple[np.ndarray, int]:
        """
        Eliminate direct wave by:
        1. Setting time zero at direct wave peak
        2. Applying time-based shift (travel time from antenna to surface)

        Args:
            signal: Input signal
            peak_idx: Index of direct wave peak
            shift_time_ns: Time shift in nanoseconds (default 3.0 ns for real data)
                          Automatically scaled for synthetic data with different dt

        Returns:
            Signal with direct wave removed, new start index
        """
        # Convert time shift to samples based on actual dt
        shift_samples = int(round(shift_time_ns / self.dt_ns))

        # New time zero at direct wave peak + shift
        new_start_idx = peak_idx + shift_samples

        if new_start_idx >= len(signal):
            raise ValueError(f"Shift {shift_time_ns} ns ({shift_samples} samples) beyond signal end")

        # Truncate signal starting from new time zero
        processed = signal[new_start_idx:]

        return processed, new_start_idx

    # ========================================================================
    # STEP 4: BANDPASS FILTER (150-800 MHz)
    # ========================================================================

    def apply_bandpass_filter(self, signal: np.ndarray,
                             freq_low: float = 150e6,
                             freq_high: float = 800e6,
                             order: int = 4) -> np.ndarray:
        """
        Apply Butterworth bandpass filter (150-800 MHz).
        Uses second-order sections (SOS) for numerical stability.

        Args:
            signal: Input signal
            freq_low: Lower cutoff frequency (Hz)
            freq_high: Upper cutoff frequency (Hz)
            order: Filter order

        Returns:
            Filtered signal
        """
        nyquist = self.fs_hz / 2

        # Normalize frequencies to Nyquist
        if freq_high > nyquist:
            print(f"[WARN] High freq {freq_high/1e6:.0f} MHz exceeds Nyquist "
                  f"{nyquist/1e6:.1f} MHz - capping")
            freq_high = nyquist * 0.99

        normalized_low = freq_low / nyquist
        normalized_high = freq_high / nyquist

        # Design filter (using SOS for stability)
        sos = butter(order, [normalized_low, normalized_high], btype='band',
                    output='sos')

        # Apply forward-backward filter using SOS (more stable than ba)
        filtered = np.zeros_like(signal)

        # Forward pass
        zi = sosfilt_zi(sos)
        filtered, _ = sosfilt(sos, signal, zi=zi*signal[0])

        # Backward pass for zero-phase
        filtered, _ = sosfilt(sos, filtered[::-1], zi=zi*filtered[0])
        filtered = filtered[::-1]

        return filtered

    # ========================================================================
    # STEP 5: SIGNAL TRUNCATION
    # ========================================================================

    def truncate_signal(self, signal: np.ndarray, window_length_ns: float = 50) -> np.ndarray:
        """
        Truncate signal to window of interest.

        Args:
            signal: Input signal
            window_length_ns: Length of window in nanoseconds

        Returns:
            Truncated signal
        """
        num_samples = int(window_length_ns / self.dt_ns) + 1
        num_samples = min(num_samples, len(signal))

        return signal[:num_samples]

    # ========================================================================
    # STEP 6: BGR FILTER (BACKGROUND REMOVAL)
    # ========================================================================

    def apply_bgr_filter(self, signals_2d: np.ndarray, window_size: int = 1000) -> np.ndarray:
        """
        Apply Background Removal (BGR) filter with moving window.
        Removes background noise by subtracting moving average across traces.

        Args:
            signals_2d: 2D array [n_traces, n_samples]
            window_size: Moving window size (number of traces)

        Returns:
            BGR-filtered signals [n_traces, n_samples]
        """
        n_traces, n_samples = signals_2d.shape

        bgr_output = np.zeros_like(signals_2d)

        for i in range(n_traces):
            # Define window boundaries
            start_idx = max(0, i - window_size // 2)
            end_idx = min(n_traces, i + window_size // 2 + 1)

            # Compute moving average (background)
            background = np.mean(signals_2d[start_idx:end_idx, :], axis=0)

            # Subtract background
            bgr_output[i, :] = signals_2d[i, :] - background

        return bgr_output

    # ========================================================================
    # STEP 7: ANALYTIC ENVELOPE (HILBERT TRANSFORM)
    # ========================================================================

    def compute_analytic_envelope(self, signal: np.ndarray) -> np.ndarray:
        """
        Compute analytic envelope using Hilbert transform.
        Signal must be normalized by maximum before this step.

        Args:
            signal: Input signal (normalized by maximum)

        Returns:
            Analytic envelope (amplitude of analytic signal)
        """
        # Compute analytic signal via Hilbert transform
        analytic_signal = hilbert(signal)

        # Extract envelope (magnitude)
        envelope = np.abs(analytic_signal)

        return envelope

    # ========================================================================
    # COMPLETE PIPELINE
    # ========================================================================

    def process_single_trace(self, signal: np.ndarray,
                            normalize_direct_wave: bool = True,
                            remove_dc: bool = True,
                            eliminate_dw: bool = True,
                            apply_bandpass: bool = True,
                            compute_envelope: bool = True,
                            window_length_ns: float = 50,
                            bandpass_low_hz: float = 150e6,
                            bandpass_high_hz: float = 800e6) -> dict:
        """
        Process a single A-scan trace through complete pipeline.

        Returns dict with:
            - 'signal_norm': After direct wave normalization
            - 'signal_no_dc': After DC removal
            - 'signal_no_dw': After direct wave elimination
            - 'signal_filtered': After bandpass filter
            - 'signal_truncated': After truncation
            - 'signal_envelope': Final analytic envelope
            - 'direct_wave_peak_idx': Index of direct wave peak
            - 'dw_eliminated_idx': Start index after DW elimination
        """
        results = {'original': signal.copy()}
        current_signal = signal.copy()

        # Step 1: Direct wave normalization
        if normalize_direct_wave:
            current_signal, dw_peak_idx = self.normalize_by_direct_wave(current_signal)
            results['signal_norm'] = current_signal.copy()
            results['direct_wave_peak_idx'] = dw_peak_idx
        else:
            dw_peak_idx = 0
            results['direct_wave_peak_idx'] = dw_peak_idx

        # Step 2: DC-Shift removal
        if remove_dc:
            current_signal = self.remove_dc_shift(current_signal)
            results['signal_no_dc'] = current_signal.copy()

        # Step 3: Direct wave elimination
        if eliminate_dw:
            current_signal, dw_elim_idx = self.eliminate_direct_wave(
                current_signal, dw_peak_idx, shift_time_ns=3.0
            )
            results['signal_no_dw'] = current_signal.copy()
            results['dw_eliminated_idx'] = dw_elim_idx

        # Step 4: Bandpass filter
        if apply_bandpass:
            current_signal = self.apply_bandpass_filter(
                current_signal, freq_low=bandpass_low_hz, freq_high=bandpass_high_hz
            )
            results['signal_filtered'] = current_signal.copy()
            results['bandpass_low_hz']  = bandpass_low_hz
            results['bandpass_high_hz'] = bandpass_high_hz

        # Step 5: Truncation
        current_signal = self.truncate_signal(current_signal, window_length_ns)
        results['signal_truncated'] = current_signal.copy()

        # Step 6: Normalization by maximum (required for envelope)
        max_val = np.max(np.abs(current_signal))
        if max_val > 0:
            current_signal = current_signal / max_val

        # Step 7: Analytic envelope
        if compute_envelope:
            current_signal = self.compute_analytic_envelope(current_signal)
            results['signal_envelope'] = current_signal.copy()

        results['processed'] = current_signal

        return results

    def process_multiple_traces(self, signals_2d: np.ndarray,
                               apply_bgr: bool = True,
                               bgr_window: int = 1000,
                               window_length_ns: float = 50) -> np.ndarray:
        """
        Process multiple traces with BGR filtering.

        Args:
            signals_2d: 2D array [n_traces, n_samples]
            apply_bgr: Whether to apply BGR filter
            bgr_window: BGR moving window size
            window_length_ns: Truncation window length

        Returns:
            Processed traces [n_traces, n_samples]
        """
        n_traces, _ = signals_2d.shape
        processed_traces = []

        print(f"Processing {n_traces} traces...")

        for i in range(n_traces):
            if (i + 1) % max(1, n_traces // 10) == 0:
                print(f"  {i+1}/{n_traces} ({100*(i+1)/n_traces:.0f}%)")

            result = self.process_single_trace(
                signals_2d[i, :],
                window_length_ns=window_length_ns
            )
            processed_traces.append(result['processed'])

        processed_2d = np.array(processed_traces)

        # Step 6: BGR filter (if requested)
        if apply_bgr:
            print(f"Applying BGR filter (window={bgr_window} traces)...")
            processed_2d = self.apply_bgr_filter(processed_2d, window_size=bgr_window)

        return processed_2d


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def read_dzt_file(dzt_path: Path, max_traces: int = None) -> Tuple[np.ndarray, float]:
    """
    Read GSSI DZT file.

    Returns:
        2D array [n_traces, n_samples], sampling interval dt_ns
    """
    HEADER_SIZE = 128 * 1024
    SAMPLES_PER_TRACE = 512
    BYTES_PER_SAMPLE = 4
    DT_NS = 50 / 511  # GSSI standard

    file_size = dzt_path.stat().st_size
    n_traces = (file_size - HEADER_SIZE) // (SAMPLES_PER_TRACE * BYTES_PER_SAMPLE)

    if max_traces is not None:
        n_traces = min(n_traces, max_traces)

    print(f"[READ] DZT file: {dzt_path.name}")
    print(f"  Traces: {n_traces}")
    print(f"  Samples/trace: {SAMPLES_PER_TRACE}")
    print(f"  dt: {DT_NS:.6f} ns")

    traces = np.zeros((n_traces, SAMPLES_PER_TRACE - 2), dtype=np.float64)

    with open(dzt_path, 'rb') as f:
        for i in range(n_traces):
            f.seek(HEADER_SIZE + i * SAMPLES_PER_TRACE * BYTES_PER_SAMPLE)
            trace_bytes = f.read(SAMPLES_PER_TRACE * BYTES_PER_SAMPLE)
            trace = np.frombuffer(trace_bytes, dtype=np.int32, count=SAMPLES_PER_TRACE)
            traces[i, :] = trace[2:].astype(np.float64)  # Drop indices 0-1

    return traces, DT_NS


def read_synthetic_file(out_path: Path) -> Tuple[np.ndarray, float]:
    """
    Read gprMax .out file (single trace).

    Returns:
        1D array [n_samples], sampling interval dt_ns
    """
    print(f"[READ] Synthetic .out file: {out_path.name}")

    with h5py.File(out_path, 'r') as f:
        signal = f['rxs/rx1/Ez'][()]
        dt = f.attrs.get('dt', 0.0)

    dt_ns = dt * 1e9
    print(f"  Samples: {len(signal)}")
    print(f"  dt: {dt_ns:.6f} ns")

    return signal, dt_ns


# ============================================================================
# MAIN USAGE EXAMPLE
# ============================================================================

def main():
    import argparse

    ap = argparse.ArgumentParser(
        description="Vivanco Signal Processing Pipeline",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Process DZT file (first 100 traces)
  python scripts/proceso_senal_vivanco.py D:/Codigo/Data/PUERTO-LIMACHE*.DZT --max-traces 100

  # Process synthetic .out file
  python scripts/proceso_senal_vivanco.py output_test/ballast_eps51_optimized.out
        """
    )

    ap.add_argument("input_file", type=Path, help="Input file (DZT or .out)")
    ap.add_argument("--max-traces", type=int, default=None, help="Max traces to process (DZT only)")
    ap.add_argument("--no-bgr", action="store_true", help="Skip BGR filter")
    ap.add_argument("--bgr-window", type=int, default=1000, help="BGR window size")
    ap.add_argument("--window-length", type=float, default=50, help="Truncation window (ns)")
    ap.add_argument("--plot", action="store_true",
                    help="Plot pipeline stages for one sample trace")
    ap.add_argument("--plot-trace", type=int, default=None,
                    help="Which trace index to use for --plot (default: middle of loaded set)")
    ap.add_argument("--align-shift", type=float, default=0.0,
                    help="Pre-shift synthetic by N ns before pipeline (e.g. 4.0 to match DZT "
                         "hardware timing). Also flips polarity for gprMax Ez convention.")
    ap.add_argument("--freq-band", default="150:800",
                    metavar="LOW_MHZ:HIGH_MHZ",
                    help="Bandpass filter cutoffs in MHz (default: 150:800)")
    ap.add_argument("-o", "--output", type=Path, default=None, help="Output NPZ file")

    args = ap.parse_args()

    # Parse freq-band
    _band_parts = args.freq_band.split(":")
    freq_low_hz  = float(_band_parts[0]) * 1e6
    freq_high_hz = float(_band_parts[1]) * 1e6

    # Read input file
    if args.input_file.suffix.lower() == '.dzt':
        signals, dt_ns = read_dzt_file(args.input_file, max_traces=args.max_traces)
        is_multiple = True
    elif args.input_file.suffix.lower() == '.out':
        signal, dt_ns = read_synthetic_file(args.input_file)
        # Apply hardware alignment: flip polarity + prepend zeros for cable delay
        if args.align_shift > 0.0:
            signal = -signal  # gprMax Ez polarity convention
            pad = int(round(args.align_shift / dt_ns))
            signal = np.concatenate([np.zeros(pad), signal])
            print(f"  [align] flipped polarity + prepended {pad} zeros ({args.align_shift} ns)")
        signals = signal.reshape(1, -1)
        is_multiple = False
    else:
        print(f"[ERR] Unknown file type: {args.input_file.suffix}")
        return 1

    pipeline = VivancoPipeline(dt_ns=dt_ns)

    print(f"\n{'='*70}")
    print("VIVANCO SIGNAL PROCESSING PIPELINE")
    print(f"{'='*70}\n")

    # Process
    if is_multiple:
        processed = pipeline.process_multiple_traces(
            signals,
            apply_bgr=not args.no_bgr,
            bgr_window=args.bgr_window,
            window_length_ns=args.window_length
        )
    else:
        result = pipeline.process_single_trace(
            signals[0, :],
            window_length_ns=args.window_length,
            bandpass_low_hz=freq_low_hz,
            bandpass_high_hz=freq_high_hz,
        )
        processed = result['processed'].reshape(1, -1)

    print(f"\n{'='*70}")
    print("PROCESSING COMPLETE")
    print(f"{'='*70}")
    print(f"Output shape: {processed.shape}")

    # Save if requested
    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        np.savez(output_path, processed=processed, dt_ns=dt_ns)
        print(f"[SAVE] {output_path}\n")

    # Plot pipeline stages for one sample trace
    if args.plot:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt

        plot_idx = args.plot_trace if args.plot_trace is not None else len(signals) // 2
        plot_idx = min(plot_idx, len(signals) - 1)
        print(f"[PLOT] Generating pipeline stages for trace #{plot_idx}")

        stages = pipeline.process_single_trace(
            signals[plot_idx, :],
            window_length_ns=args.window_length,
            bandpass_low_hz=freq_low_hz,
            bandpass_high_hz=freq_high_hz,
        )

        # Build time axes
        t_raw  = np.arange(len(stages['original']))   * dt_ns
        t_nodw = np.arange(len(stages['signal_no_dw'])) * dt_ns
        t_filt = np.arange(len(stages.get('signal_filtered',
                                           stages['signal_no_dw']))) * dt_ns
        t_proc = np.arange(len(processed[plot_idx])) * dt_ns

        fig, axes = plt.subplots(4, 1, figsize=(12, 11), sharex=False)

        # Panel 1 — raw trace
        ax = axes[0]
        ax.plot(t_raw, stages['original'], lw=0.7, color="steelblue")
        dw_t = stages['direct_wave_peak_idx'] * dt_ns
        ax.axvline(dw_t, color="red", ls="--", lw=0.8,
                   label=f"DW peak @ {dw_t:.1f} ns")
        ax.set_title("Step 0 — Raw A-scan (A/D counts)")
        ax.legend(fontsize=8); ax.set_ylabel("Counts")

        # Panel 2 — after norm + DC removal + DW elimination
        ax = axes[1]
        ax.plot(t_nodw, stages['signal_no_dw'], lw=0.7, color="darkorange")
        ax.set_title("Steps 1-3 — Normalised, DC-removed, direct wave cut "
                     f"(start index {stages['dw_eliminated_idx']})")
        ax.set_ylabel("Normalised amplitude")

        # Panel 3 — after bandpass
        ax = axes[2]
        sig_filt = stages.get('signal_filtered', stages['signal_no_dw'])
        ax.plot(t_filt, sig_filt, lw=0.7, color="seagreen")
        ax.set_title(f"Step 4 — Bandpass {freq_low_hz/1e6:.0f}–{freq_high_hz/1e6:.0f} MHz")
        ax.set_ylabel("Normalised amplitude")

        # Panel 4 — final output (after BGR if applied, then envelope)
        ax = axes[3]
        ax.plot(t_proc, processed[plot_idx], lw=0.8, color="crimson")
        bgr_tag = f" + BGR(w={args.bgr_window})" if not args.no_bgr and is_multiple else " (no BGR)"
        ax.set_title(f"Steps 5-7 — Truncated{bgr_tag} + Hilbert envelope (final)")
        ax.set_xlabel("Time (ns)"); ax.set_ylabel("Envelope amplitude")

        for ax in axes:
            ax.grid(alpha=0.3)

        n_loaded = len(signals)
        bgr_status = f"BGR w={args.bgr_window}" if not args.no_bgr and is_multiple else "BGR skipped"
        fig.suptitle(
            f"Vivanco pipeline — {args.input_file.name}\n"
            f"trace #{plot_idx} of {n_loaded}  |  dt={dt_ns:.4f} ns  |  {bgr_status}",
            fontsize=11
        )
        fig.tight_layout()

        out_dir = Path("output_test")
        out_dir.mkdir(exist_ok=True)
        plot_path = out_dir / f"vivanco_pipeline_{args.input_file.stem}_t{plot_idx}.png"
        fig.savefig(plot_path, dpi=150, bbox_inches="tight")
        plt.close()
        print(f"[PLOT] Saved: {plot_path}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
