from pathlib import Path

def validate_dataset(folder_path):
    print(f"Validating dataset in: {folder_path}")
    folder = Path(folder_path)
    
    if not folder.exists():
        print("Folder does not exist.")
        return False
        
    in_files = set(f.stem for f in folder.glob("*.in"))
    out_files = set(f.stem for f in folder.glob("*.out"))
    
    # Check intersection
    common = in_files.intersection(out_files)
    missing_out = in_files - out_files
    missing_in = out_files - in_files
    
    print(f"Total .in files: {len(in_files)}")
    print(f"Total .out files: {len(out_files)}")
    print(f"Matched pairs: {len(common)}")
    
    if missing_out:
        print(f"\n[ERROR] Found {len(missing_out)} .in files with MISSING .out files:")
        for f in list(missing_out)[:10]:
            print(f"  - {f}.in")
        if len(missing_out) > 10: print("  ...")
        
    if missing_in:
        print(f"\n[ERROR] Found {len(missing_in)} .out files with MISSING .in files:")
        for f in list(missing_in)[:10]:
            print(f"  - {f}.out")
        if len(missing_in) > 10: print("  ...")
        
    if not missing_out and not missing_in:
        print("\n[SUCCESS] PERFECT MATCH. Every .in file has a corresponding .out file.")
        return True
    else:
        print("\n[FAILED] Dataset is incomplete or inconsistent.")
        return False

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("folder", help="Folder to validate")
    args = parser.parse_args()
    
    validate_dataset(args.folder)
