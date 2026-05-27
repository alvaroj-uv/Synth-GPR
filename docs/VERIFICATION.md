# Verification Checklist

Use this guide to verify that each step of the pipeline represents a success state.

## 0. Environment Health Check
Before running anything, ensure your terminal is ready.

*   [ ] **Command**: `conda list`
*   [ ] **Verify**: Look for `gprMax` in the output or ensure the active environment corresponds to `gprMax` dependencies (numpy, h5py, etc.).
*   [ ] **Test**: Run `python -c "import gprMax; print('gprMax OK')"`
    *   *Success*: Prints "gprMax OK".
    *   *Error*: `ModuleNotFoundError` -> You forgot `conda activate gprMax` (or `conda run -n gprMax ...`).

---

## 1. Generation Verification
**Goal**: Create valid `.in` geometry files.

*   **Command**:
    ```bash
    python scripts/main/generate_in_files.py test_gen --mode batch --labels CL -n 5
    ```
*   **Checklist**:
    1.  [ ] **Console Output**: Should say "Generated 5 samples". No "traceback" errors.
    2.  [ ] **File Existence**: Open `test_gen/`. Do you see `s_1000.in` to `s_1004.in`?
    3.  [ ] **File Content**: Open `s_1000.in` in a text editor.
        *   Does it end with `#rx: ...`?
        *   Does it contain material definitions (`#material: ...`)?
        *   **Critical**: Are there thousands of `#cylinder` commands (if Granular)?
    4.  [ ] **Metadata**: Is there a `metadata_CL.csv` file? Open it. Does it list the filenames and PVC values?

---

## 2. Simulation Verification
**Goal**: Run FDTD simulation and create `.out` files.

*   **Command**:
    ```bash
    python -m gprMax test_gen/s_1000.in -n 1
    ```
*   **Checklist**:
    1.  [ ] **Console Output**: GprMax should print its logo and a progress bar.
    2.  [ ] **Success Message**: "Simulation completed in X seconds".
    3.  [ ] **File Existence**: Check `test_gen/`. Do you see `s_1000.out`?
    4.  [ ] **File Size**: The `.out` file should be approx 40-50 KB (for 1000 iterations). If it is 0 KB, the simulation crashed silently.
    5.  [ ] **Common Errors**:
        *   `UnicodeEncodeError`: Ignore if file exists (Windows console display issue).
        *   `MemoryError`: Domain too large (check config).

---

## 3. Extraction Verification
**Goal**: Convert valid HDF5 outputs to a CSV dataset.

*   **Command**:
    ```bash
    python scripts/main/extract_features.py test_gen -o features_test.csv
    ```
*   **Checklist**:
    1.  [ ] **Console Output**: "Processing s_1000.out... Done".
    2.  [ ] **Output File**: `features_test.csv` should exist.
    3.  [ ] **Data Integrity**: Open the CSV in Excel/Notepad.
        *   Are there headers? (`mean`, `max`, `fft_peak`...)
        *   Are there 5 rows of data (plus header)?
        *   Are the values numeric (not `NaN` or `inf`)?

---

## 4. Visual Verification (The "Smell Test")
**Goal**: Ensure the data "looks" right physically.

*   **Command**:
    ```bash
    python scripts/tools/visualization/visualize_gprmax_blueprint.py test_gen/s_1000.in
    ```
*   **Checklist**:
    1.  [ ] **Geometry Window**:
        *   Are the rocks (circles) contained within the ballast box?
        *   Is the Subgrade below the Ballast?
    2.  [ ] **Signal Window**:
        *   Is there a signal pulse? (A flat line means the source didn't fire or everything is absorbing).
        *   Does the Envelope (Red) look reasonable?

---

## Troubleshooting Guide

| Issue | Likely Cause | Solution |
| :--- | :--- | :--- |
| `ModuleNotFoundError: No module named 'src'` | Running from wrong folder. | Always run from `d:\Codigo\Synth-GPR` (Root). |
| `gprMax' is not recognized` | Environment not active. | Run `conda activate gprMax`. |
| `.in` file has 0 bytes | Generator crashed. | Check console logs for "Permission denied" or logic errors. |
| `.out` file is missing | Simulation didn't run. | Check path to `.in` file. Linux/Windows slash issues? |
| CSV features are all NaN | Bad signal data. | Check if `.out` file is valid using the Blueprint tool. |
