import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import hilbert
from src.signal_processing import preprocess_signal


def save_feature_summary_plot(features_df, original_df, signal_name, output_filename=None):
    """
    Generates a summary plot with waveforms, scalar, slice, grid features, and Fourier spectrum.
    Saves it as a PNG.
    """
    row = features_df[features_df['Signal'] == signal_name]
    if row.empty:
        print(f"Signal '{signal_name}' not found in DataFrame.")
        return

    fig = plt.figure(figsize=(16, 20))
    gs = fig.add_gridspec(4, 3)

    # --- 0. Waveforms (Top Row) ---
    ax_wave = fig.add_subplot(gs[0, :])
    ax_fft  = fig.add_subplot(gs[3, :])   # always created; filled below if data available

    has_waveform = signal_name in original_df.columns and 'Time' in original_df.columns
    if has_waveform:
        time       = original_df['Time'].values
        raw_signal = original_df[signal_name].values

        dt = time[1] - time[0] if len(time) > 1 else 1e-10

        treated_signal, _ = preprocess_signal(raw_signal, dt)
        treated_time      = np.arange(len(treated_signal)) * dt

        amplitude_envelope = np.abs(hilbert(treated_signal))

        raw_norm = raw_signal / np.max(np.abs(raw_signal)) if np.max(np.abs(raw_signal)) > 0 else raw_signal

        ax_wave.plot(raw_norm,           time,         label='Raw Signal (Normalized)', color='gray', alpha=0.5)
        ax_wave.plot(treated_signal,     treated_time, label='Treated Signal',           color='blue', linewidth=0.8)
        ax_wave.plot(amplitude_envelope, treated_time, label='Analytical Signal (Envelope)',
                     color='red', linewidth=2.0)
        ax_wave.set_title(f'{signal_name} - Waveforms (Rotated)')
        ax_wave.set_ylabel('Time (s) [Inverted]')
        ax_wave.set_xlabel('Normalized Amplitude')
        ax_wave.invert_yaxis()
        ax_wave.legend()
        ax_wave.grid(True)

        fft_vals    = np.fft.fft(treated_signal)
        fft_spectrum = np.abs(fft_vals)
        freqs        = np.fft.fftfreq(len(treated_signal), d=dt)
        pos_mask     = freqs >= 0
        ax_fft.plot(freqs[pos_mask] / 1e6, fft_spectrum[pos_mask], color='purple')
        ax_fft.set_title(f'{signal_name} - Fourier Spectrum (Treated Signal)')
        ax_fft.set_xlabel('Frequency (MHz)')
        ax_fft.set_ylabel('Magnitude')
        ax_fft.set_xlim(0, 2000)
        ax_fft.grid(True)
    else:
        ax_wave.text(0.5, 0.5, "Waveform data not available", ha='center', va='center')
        ax_fft.text(0.5, 0.5, "Spectrum not available",      ha='center', va='center')

    # --- 1. Scalar Features (Row 1, Left) ---
    ax_scalar = fig.add_subplot(gs[1, 0])
    scalar_keys = ['root_mean_square', 'standard_deviation', 'skewness',
                   'kurtosis_value', 'crest_factor', 'spectral_entropy', 'spectral_flatness']
    values = [(k, float(row[k].values[0])) for k in scalar_keys if k in row.columns]
    if values:
        labels, vals = zip(*values)
        ax_scalar.bar(labels, vals, color='skyblue')
        ax_scalar.set_title('Key Scalar Features')
        ax_scalar.set_xticks(range(len(labels)))
        ax_scalar.set_xticklabels(labels, rotation=45, ha='right')
        ax_scalar.set_ylabel('Value')
        ax_scalar.grid(axis='y', linestyle='--', alpha=0.7)

    # --- 2. Slice Statistics (Row 1, Center & Right) ---
    ax_slice = fig.add_subplot(gs[1, 1:])
    n_slices = sum(1 for i in range(100) if f'stat_slice_{i}_mean' in row.columns)
    means = [float(row[f'stat_slice_{i}_mean'].values[0]) for i in range(n_slices)]
    stds  = [float(row[f'stat_slice_{i}_std' ].values[0]) for i in range(n_slices)
             if f'stat_slice_{i}_std' in row.columns]
    if means:
        ax_slice.plot(range(len(means)), means, marker='o', label='Mean')
        if stds:
            ax_slice.plot(range(len(stds)), stds, marker='x', linestyle='--', label='Std Dev')
        ax_slice.set_title(f'Slice Statistics ({n_slices} slices)')
        ax_slice.set_xlabel('Slice Index')
        ax_slice.set_ylabel('Amplitude')
        ax_slice.legend()
        ax_slice.grid(True)

    # --- 3. Grid Features (Row 2) ---
    n_rows = sum(1 for i in range(100) if f'grid_signal_time_{i}_0' in row.columns)
    n_cols = sum(1 for j in range(100) if f'grid_signal_time_0_{j}' in row.columns)

    grid_time    = np.zeros((n_rows, n_cols))
    grid_hilbert = np.zeros((n_rows, n_cols))
    for i in range(n_rows):
        for j in range(n_cols):
            ct = f'grid_signal_time_{i}_{j}'
            ch = f'grid_hilbert_envelope_{i}_{j}'
            if ct in row.columns:
                grid_time[i, j]    = float(row[ct].values[0])
            if ch in row.columns:
                grid_hilbert[i, j] = float(row[ch].values[0])

    ax_grid_time = fig.add_subplot(gs[2, 0])
    im1 = ax_grid_time.imshow(grid_time, cmap='viridis', aspect='auto')
    ax_grid_time.set_title(f'Time Domain Grid ({n_rows}×{n_cols})')
    fig.colorbar(im1, ax=ax_grid_time)

    ax_grid_hilbert = fig.add_subplot(gs[2, 1])
    im2 = ax_grid_hilbert.imshow(grid_hilbert, cmap='plasma', aspect='auto')
    ax_grid_hilbert.set_title(f'Hilbert Envelope Grid ({n_rows}×{n_cols})')
    fig.colorbar(im2, ax=ax_grid_hilbert)

    ax_info = fig.add_subplot(gs[2, 2])
    ax_info.axis('off')
    info_keys = {'mean': 'Mean', 'root_mean_square': 'RMS',
                 'peak_max': 'Max', 'peak_min': 'Min'}
    info_lines = [f"Signal: {signal_name}"]
    for col, label in info_keys.items():
        if col in row.columns:
            info_lines.append(f"{label}: {float(row[col].values[0]):.4e}")
    ax_info.text(0.1, 0.5, "\n".join(info_lines), fontsize=12, va='center')

    plt.suptitle(f'Feature Extraction Summary: {signal_name}', fontsize=16)
    plt.tight_layout(rect=[0, 0.03, 1, 0.95])

    if output_filename:
        plt.savefig(output_filename)
        print(f"[Plotting] Saved summary plot to: {output_filename}")
    else:
        plt.show()

    plt.close(fig)


def plot_set(signals_list, x_axis, title, xlabel, ylabel, output_filename, color_mean='red'):
    """
    Plots a set of signals in gray and their mean in color.
    """
    if not signals_list:
        print(f"No data for {title}")
        return

    fig, ax = plt.subplots(figsize=(10, 6))

    max_len = max(len(s) for s in signals_list)
    stacked = np.full((len(signals_list), max_len), np.nan)

    for i, s in enumerate(signals_list):
        length = len(s)
        stacked[i, :length] = s
        x = x_axis[:length] if x_axis is not None and len(x_axis) >= length else np.arange(length)
        ax.plot(x, s, color='gray', alpha=0.1, linewidth=0.5)

    mean_signal = np.nanmean(stacked, axis=0)
    x_mean = x_axis[:max_len] if x_axis is not None and len(x_axis) >= max_len else np.arange(max_len)
    ax.plot(x_mean, mean_signal, color=color_mean, linewidth=2, label='Average')

    ax.set_title(title)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.legend()
    ax.grid(True)
    fig.tight_layout()
    fig.savefig(output_filename)
    print(f"Saved {output_filename}")
    plt.close(fig)
