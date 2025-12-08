import os
import sys
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).resolve().parents[2]))

import numpy as np
from src.data_loader import read_gprmax_hdf5
from src.feature_extraction import extract_features
try:
    from .plot_utils import save_feature_summary_plot
except ImportError:
    from plot_utils import save_feature_summary_plot

def visualize_single_file(filename, target_signal=None, fields=['E', 'H']):
    """
    Reads a single file, extracts features, and generates the summary plot.
    Args:
        filename: Path to .out file
        target_signal: Specific signal name to plot (e.g. 'rx1_Ez'). If None, plots all.
        fields: Fields to read from file.
    """
    if not os.path.exists(filename):
        print(f"Error: File '{filename}' not found.")
        return

    print(f"--- Processing {filename} ---")

    # 1. Read Data
    df = read_gprmax_hdf5(filename, fields=fields)
    if df.empty:
        print("Error: DataFrame is empty or file could not be read.")
        return

    # 2. Extract Features
    # Determine dt
    dt = 1e-10
    if 'Time' in df.columns and len(df) > 1:
        dt = df['Time'].iloc[1] - df['Time'].iloc[0]
        
    features_df = extract_features(df, dt=dt)
    
    if features_df.empty:
        print("No features extracted.")
        return

    print("\n[Visualizing Features]")
    
    # Filter if target_signal is specified
    if target_signal:
        if target_signal not in features_df['Signal'].values:
            print(f"Warning: Signal '{target_signal}' not found in extracted features.")
            print(f"Available signals: {list(features_df['Signal'].values)}")
            return
        signals_to_plot = [target_signal]
    else:
        signals_to_plot = features_df['Signal'].values

    # Iterate through signals
    for signal_name in signals_to_plot:
        # Check for valid data in original dataframe
        if signal_name not in df.columns:
            print(f"Warning: Signal '{signal_name}' not found in raw data. Skipping.")
            continue
            
        raw_data = df[signal_name].values
        if len(raw_data) == 0:
             print(f"Warning: Signal '{signal_name}' has no data points. Skipping.")
             continue
             
        if np.all(raw_data == 0):
             print(f"Warning: Signal '{signal_name}' contains only zeros. Skipping.")
             continue

        print(f"--- Plotting {signal_name} ---")
        
        # Generate output filename
        base_name = os.path.basename(filename).replace('.out', '')
        output_png = f"{base_name}_{signal_name}_features.png"
        
        save_feature_summary_plot(features_df, df, signal_name, output_filename=output_png)

if __name__ == "__main__":
    # Configuration
    filename = "samples/A_Cle-A_0001.out"
    target_signal = "rx1_Ez" # Set to None to plot all signals, e.g. target_signal = None
    fields = ['E', 'H']
    
    print(f"Running visualization for: {filename}")
    print(f"Target Signal: {target_signal if target_signal else 'All'}")
    
    visualize_single_file(filename, target_signal=target_signal, fields=fields)
