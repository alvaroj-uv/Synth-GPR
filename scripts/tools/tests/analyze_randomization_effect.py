import pandas as pd
import numpy as np
import os

# Path to the features file
csv_path = r"d:\Codigo\Synth-Data\Tests\PipelineTest\features_test.csv"

def analyze_randomization(csv_path):
    if not os.path.exists(csv_path):
        print(f"Error: File not found: {csv_path}")
        return

    print(f"Analyzing features from: {csv_path}")
    df = pd.read_csv(csv_path)
    
    # Extract base ID (s_XXXXX) from filename
    # Filenames are like s_40000.in, s_40000_r1.in
    # We want to group by 's_40000'
    df['base_id'] = df['Filename'].apply(lambda x: x.split('_r')[0].replace('.out', '').replace('.in', ''))
    
    # Feature columns to check (exclude metadata)
    metadata_cols = ['Filename', 'Label', 'Signal', 'base_id']
    feature_cols = [c for c in df.columns if c not in metadata_cols]
    
    # Select a few key features for display
    # actual columns: mean, root_mean_square, peak_max, skewness, kurtosis_value
    key_features = ['root_mean_square', 'peak_max', 'skewness', 'kurtosis_value']
    key_features = [f for f in key_features if f in feature_cols]
    
    print("\n--- Randomization Analysis ---")
    
    grouped = df.groupby('base_id')
    
    for base_id, group in grouped:
        print(f"\nSample ID: {base_id} (count: {len(group)})")
        
        # Check if features vary
        variations = {}
        for feat in key_features:
            values = group[feat].values
            std_dev = np.std(values)
            mean_val = np.mean(values)
            pct_var = (std_dev / mean_val * 100) if mean_val != 0 else 0
            
            variations[feat] = {
                'std': std_dev,
                'pct': pct_var,
                'vals': values
            }
            
            status = "[CHANGED]" if std_dev > 1e-6 else "[SAME]"
            print(f"  {feat:10} : {status} {values} (Var: {pct_var:.2f}%)")
            
    print("\nanalysis complete.")

if __name__ == "__main__":
    analyze_randomization(csv_path)
