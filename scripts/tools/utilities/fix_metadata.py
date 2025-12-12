#!/usr/bin/env python3
"""
Quick fix: Add FI_Class column to metadata.csv based on PVC values
"""
import pandas as pd
import sys

def classify_pvc_to_fi_class(pvc):
    """
    Classify PVC to FI_Class using Selig & Waters ranges.
    
    PVC -> FI conversion (simplified):
    FI ≈ PVC * some_factor (depends on porosity, but we'll use direct mapping)
    
    Classes:
    C:  FI 0-1%    -> PVC ~0-1%
    MC: FI 1-10%   -> PVC ~1-10%
    MF: FI 10-20%  -> PVC ~10-20%
    F:  FI 20-40%  -> PVC ~20-40%
    HF: FI 40-50%  -> PVC ~40-100%
    """
    if pvc < 1.0:
        return 'C'
    elif pvc < 10.0:
        return 'MC'
    elif pvc < 20.0:
        return 'MF'
    elif pvc < 40.0:
        return 'F'
    else:
        return 'HF'

def main():
    if len(sys.argv) < 2:
        print("Usage: python fix_metadata.py <metadata.csv>")
        sys.exit(1)
    
    csv_path = sys.argv[1]
    
    # Read metadata
    df = pd.read_csv(csv_path)
    
    print(f"Loaded {len(df)} rows from {csv_path}")
    print(f"Columns: {list(df.columns)}")
    
    # Check if FI_Class already exists
    if 'FI_Class' in df.columns:
        print("FI_Class column already exists!")
        return
    
    # Check if pvc column exists
    if 'pvc' not in df.columns:
        print("ERROR: 'pvc' column not found in metadata!")
        sys.exit(1)
    
    # Add FI_Class column
    df['FI_Class'] = df['pvc'].apply(classify_pvc_to_fi_class)
    
    # Save back
    df.to_csv(csv_path, index=False)
    
    print(f"\n✅ Added FI_Class column to {csv_path}")
    print(f"\nClass distribution:")
    print(df['FI_Class'].value_counts().sort_index())

if __name__ == '__main__':
    main()
