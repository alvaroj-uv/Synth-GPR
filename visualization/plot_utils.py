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

    # Create figure with a grid layout (4 rows)
    fig = plt.figure(figsize=(16, 20))
    gs = fig.add_gridspec(4, 3)

    # --- 0. Waveforms (Top Row) ---
    ax_wave = fig.add_subplot(gs[0, :])
    
    if signal_name in original_df.columns and 'Time' in original_df.columns:
        time = original_df['Time'].values
        raw_signal = original_df[signal_name].values
        
        # Calculate dt
        dt = time[1] - time[0] if len(time) > 1 else 1e-10
        
        # Process Signal
        treated_signal, start_idx = preprocess_signal(raw_signal, dt)
        
        # Adjust time axis for treated signal
        treated_time = np.arange(len(treated_signal)) * dt
        
        # Calculate Analytical Signal (Envelope) of the TREATED signal
        analytic_signal = hilbert(treated_signal)
        amplitude_envelope = np.abs(analytic_signal)
        
        # Plot Raw Signal (Normalized)
        raw_norm = raw_signal / np.max(np.abs(raw_signal)) if np.max(np.abs(raw_signal)) > 0 else raw_signal
        
        # Plotting with Time on Y-axis (Inverted) and Amplitude on X-axis
        # Raw Signal (Gray)
        ax_wave.plot(raw_norm, time, label='Raw Signal (Normalized)', color='gray', alpha=0.5)
        
        # Treated Signal (Blue)
        ax_wave.plot(treated_signal, treated_time, label='Treated Signal', color='blue', linewidth=0.8)
        
        # Analytical Signal (Red)
        ax_wave.plot(amplitude_envelope, treated_time, label='Analytical Signal (Envelope)', color='red', linestyle='-', linewidth=2.0)
        
        ax_wave.set_title(f'{signal_name} - Waveforms (Rotated)')
        ax_wave.set_ylabel('Time (s) [Inverted]')
        ax_wave.set_xlabel('Normalized Amplitude')
        ax_wave.invert_yaxis() # Depth/Time increases downwards
        ax_wave.legend()
        ax_wave.grid(True)
        
        # --- 4. Fourier Spectrum (Bottom Row) ---
        # Calculate Spectrum of Treated Signal
        fft_vals = np.fft.fft(treated_signal)
        fft_spectrum = np.abs(fft_vals)
        freqs = np.fft.fftfreq(len(treated_signal), d=dt)
        
        # Keep positive frequencies
        pos_mask = freqs >= 0
        fft_spectrum = fft_spectrum[pos_mask]
        freqs = freqs[pos_mask]
        
        # Plot Spectrum
        ax_fft = fig.add_subplot(gs[3, :])
        ax_fft.plot(freqs / 1e6, fft_spectrum, color='purple') # Freq in MHz
        ax_fft.set_title(f'{signal_name} - Fourier Spectrum (Treated Signal)')
        ax_fft.set_xlabel('Frequency (MHz)')
        ax_fft.set_ylabel('Magnitude')
        ax_fft.set_xlim(0, 2000) # Limit to reasonable range (e.g., 2 GHz)
        ax_fft.grid(True)
        
    else:
        ax_wave.text(0.5, 0.5, "Waveform data not available", ha='center', va='center')

    # --- 1. Scalar Features (Row 1, Left) ---
    ax_scalar = fig.add_subplot(gs[1, 0])
    features_to_plot = ['root_mean_square', 'standard_deviation', 'skewness', 'kurtosis_value', 'crest_factor', 'spectral_entropy', 'spectral_flatness']
    values = []
    labels = []
    for feat in features_to_plot:
        if feat in row.columns:
            values.append(row[feat].values[0])
            labels.append(feat)
    
    if values:
        ax_scalar.bar(labels, values, color='skyblue')
        ax_scalar.set_title(f'Key Scalar Features')
        ax_scalar.set_xticks(range(len(labels)))
        ax_scalar.set_xticklabels(labels, rotation=45, ha='right')
        ax_scalar.set_ylabel('Value')
        ax_scalar.grid(axis='y', linestyle='--', alpha=0.7)

    # --- 2. Slice Statistics (Row 1, Center & Right) ---
    ax_slice = fig.add_subplot(gs[1, 1:])
    means = []
    stds = []
    for i in range(14):
        col_mean = f'stat_slice_{i}_mean'
        col_std = f'stat_slice_{i}_std'
        if col_mean in row.columns:
            means.append(row[col_mean].values[0])
        if col_std in row.columns:
            stds.append(row[col_std].values[0])
            
    if means:
        ax_slice.plot(range(14), means, marker='o', label='Mean')
        ax_slice.plot(range(14), stds, marker='x', linestyle='--', label='Std Dev')
        ax_slice.set_title(f'Slice Statistics (14 Slices)')
        ax_slice.set_xlabel('Slice Index')
        ax_slice.set_ylabel('Amplitude')
        ax_slice.legend()
        ax_slice.grid(True)

    # --- 3. Grid Features (Row 2) ---
    # Extract grid data
    grid_time = np.zeros((16, 10))
    grid_hilbert = np.zeros((16, 10))
    for i in range(16):
        for j in range(10):
            col_time = f'grid_signal_time_{i}_{j}'
            col_hilbert = f'grid_hilbert_envelope_{i}_{j}'
            if col_time in row.columns:
                grid_time[i, j] = row[col_time].values[0]
            if col_hilbert in row.columns:
                grid_hilbert[i, j] = row[col_hilbert].values[0]

    # Time Domain Grid
    ax_grid_time = fig.add_subplot(gs[2, 0])
    im1 = ax_grid_time.imshow(grid_time, cmap='viridis', aspect='auto')
    ax_grid_time.set_title(f'Time Domain Grid (16x10)')
    fig.colorbar(im1, ax=ax_grid_time)

    # Hilbert Envelope Grid
    ax_grid_hilbert = fig.add_subplot(gs[2, 1])
    im2 = ax_grid_hilbert.imshow(grid_hilbert, cmap='plasma', aspect='auto')
    ax_grid_hilbert.set_title(f'Hilbert Envelope Grid (16x10)')
    fig.colorbar(im2, ax=ax_grid_hilbert)
    
    # Info Text
    ax_info = fig.add_subplot(gs[2, 2])
    ax_info.axis('off')
    info_text = f"Signal: {signal_name}\n"
    info_text += f"Mean: {row['mean'].values[0]:.4e}\n"
    info_text += f"RMS: {row['root_mean_square'].values[0]:.4e}\n"
    info_text += f"Max: {row['peak_max'].values[0]:.4e}\n"
    info_text += f"Min: {row['peak_min'].values[0]:.4e}\n"
    ax_info.text(0.1, 0.5, info_text, fontsize=12, va='center')

    plt.suptitle(f'Feature Extraction Summary: {signal_name}', fontsize=16)
    plt.tight_layout(rect=[0, 0.03, 1, 0.95])
    
    if output_filename:
        plt.savefig(output_filename)
        print(f"[Plotting] Saved summary plot to: {output_filename}")
    else:
        plt.show()
    
    plt.close(fig) # Close the figure to free memory

def plot_set(signals_list, x_axis, title, xlabel, ylabel, output_filename, color_mean='red'):
    """
    Plots a set of signals in gray and their mean in color.
    """
    if not signals_list:
        print(f"No data for {title}")
        return

    plt.figure(figsize=(10, 6))
    
    # Determine max length to align/pad
    max_len = max(len(s) for s in signals_list)
    
    stacked = np.zeros((len(signals_list), max_len)) * np.nan
    
    for i, s in enumerate(signals_list):
        length = len(s)
        stacked[i, :length] = s
        
        # Plot individual trace
        # Construct x_axis for this trace
        if x_axis is not None and len(x_axis) >= length:
            x = x_axis[:length]
        else:
            # Create dummy x
            x = np.arange(length)
            
        plt.plot(x, s, color='gray', alpha=0.1, linewidth=0.5)

    # Calculate Mean ignoring NaNs
    mean_signal = np.nanmean(stacked, axis=0)
    
    # Plot Mean
    if x_axis is not None and len(x_axis) >= max_len:
        x_mean = x_axis[:max_len]
    else:
        x_mean = np.arange(max_len)
        
    plt.plot(x_mean, mean_signal, color=color_mean, linewidth=2, label='Average')
    
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(output_filename)
    print(f"Saved {output_filename}")
    plt.close()
