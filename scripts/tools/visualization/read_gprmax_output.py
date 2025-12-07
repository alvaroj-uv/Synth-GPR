import sys
from pathlib import Path
# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

import warnings
from src.data_loader import read_gprmax_hdf5 as _read_gprmax_hdf5
from src.feature_extraction import extract_features as _extract_features
from visualization.plot_utils import save_feature_summary_plot as _save_feature_summary_plot
from src.signal_processing import preprocess_signal as _preprocess_signal

# Re-export functions for backward compatibility
read_gprmax_hdf5 = _read_gprmax_hdf5
extract_features = _extract_features
save_feature_summary_plot = _save_feature_summary_plot
preprocess_signal = _preprocess_signal

def visualize_features(filename, fields=['E']):
    """
    Deprecated: Use visualize_single_file.py instead.
    """
    warnings.warn("visualize_features is deprecated. Use visualize_single_file.py instead.", DeprecationWarning)
    import os
    # We can try to replicate logic or just point to new script usage
    # Replicating logic for now to keep it working if called
    df = read_gprmax_hdf5(filename, fields=fields)
    if df.empty: return

    dt = 1e-10
    if 'Time' in df.columns and len(df) > 1:
        dt = df['Time'].iloc[1] - df['Time'].iloc[0]
        
    features_df = extract_features(df, dt=dt)
    if features_df.empty: return

    for index, row in features_df.iterrows():
        signal_name = row['Signal']
        base_name = os.path.basename(filename).replace('.out', '')
        output_png = f"{base_name}_{signal_name}_features.png"
        save_feature_summary_plot(features_df, df, signal_name, output_filename=output_png)


