import argparse
import glob
from pathlib import Path

import pandas as pd
from tqdm import tqdm

from src.data_loader import read_gprmax_hdf5
from src.feature_extraction import extract_features

def create_dataset(input_dir: str):
    """
    Reads metadata.csv, loads corresponding .out files, extracts features,
    and saves a merged features.csv.
    """
    input_path = Path(input_dir)
    metadata_path = input_path / "metadata.csv"

    if not metadata_path.exists():
        print(f"[ERROR] metadata.csv not found in {input_dir}")
        return

    print(f"Loading metadata from {metadata_path}...")
    metadata_df = pd.read_csv(metadata_path)

    all_features = []

    print(f"Processing {len(metadata_df)} samples...")

    # Iterate with index to keep track
    for _, row in tqdm(metadata_df.iterrows(), total=len(metadata_df)):
        sample_id = str(row['sample_id']) # Treat ID as string

        # Construct filename.
        # ID is usually sXXXX (e.g. s0000)
        # Check if ID already has .out extension usually not
        filename = f"{sample_id}.out"
        file_path = input_path / filename

        if not file_path.exists():
            # Fallback: maybe ID is just integer 0, need to format s{id:04d}
            try:
                int_id = int(sample_id)
                filename = f"s{int_id:04d}.out"
                file_path = input_path / filename
            except ValueError:
                pass # ID was alphanumeric string

        if not file_path.exists():
            # Try finding by pattern if naming differs
            pattern = str(input_path / f"*{sample_id}*.out")
            matches = glob.glob(pattern)
            if matches:
                file_path = Path(matches[0])
                filename = file_path.name
            else:
                print(f"[WARN] Output file for sample {sample_id} not found. Skipping.")
                continue

        # Load GPR Signal (Ez)
        # We focus on Rx1 Ez usually
        try:
            signal_df = read_gprmax_hdf5(str(file_path), fields=['Ez'])
            if signal_df.empty:
                print(f"[WARN] {filename} is empty or invalid.")
                continue

            # Extract features (takes the first signal col usually rx1_Ez)
            # We assume single Rx for now or take the first one
            cols = [c for c in signal_df.columns if 'Ez' in c]
            if not cols:
                print(f"[WARN] No Ez component in {filename}.")
                continue

            # Use just the relevant columns for feature extraction
            # extract_features expects a DF with 'Time' and signals involved
            # It loops through non-metadata columns.
            target_df = signal_df[['Time', cols[0]]].copy()

            # Extract
            feats_df = extract_features(target_df)

            if feats_df.empty:
                continue

            # Flatten to a dictionary (single row)
            feats_dict = feats_df.iloc[0].to_dict()

            # Add Labels/Keys ONLY
            # We explicitly exclude simulation parameters (moisture, roughness, etc.) to avoiding leakage.
            feats_dict['label_FI_class'] = row['FI_class']  # Note: metadata has FI_class (lowercase c)
            feats_dict['label_pvc'] = row['pvc']
            feats_dict['sample_id'] = sample_id

            all_features.append(feats_dict)

        except Exception as e:
            print(f"[ERROR] Failed processing {filename}: {e}")
            continue

    if not all_features:
        print("No features extracted.")
        return

    # Create master DF
    final_df = pd.DataFrame(all_features)

    # Reorder columns: Labels first
    cols = list(final_df.columns)
    priority_cols = ['label_FI_class', 'label_pvc', 'sample_id']

    # Filter out priority cols that exist
    priority_cols = [c for c in priority_cols if c in cols]
    other_cols = [c for c in cols if c not in priority_cols]

    # Sort other columns alphabetically for consistency? Or keep extraction order?
    # Extraction order is usually logical (Stat -> Hilbert -> FFT -> etc). Keeping it.

    final_df = final_df[priority_cols + other_cols]

    # Save
    output_csv = input_path / "features.csv"
    final_df.to_csv(output_csv, index=False)
    print(f"\n[SUCCESS] Feature dataset saved to: {output_csv}")
    print(f"Total samples: {len(final_df)}")
    print(f"Total features per sample: {len(final_df.columns)}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Create Feature Dataset from GPR simulations")
    parser.add_argument("input_dir", help="Directory containing .out files and metadata.csv")
    args = parser.parse_args()

    create_dataset(args.input_dir)
