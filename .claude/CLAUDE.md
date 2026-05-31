# Environment

## Python (machine: ajmpc only)

Python is installed via Miniconda at `C:\Users\barba\miniconda3`.
Use `C:\Users\barba\miniconda3\python.exe` as the interpreter on this machine.

# Development Guidelines

## Code Review Before Creating New Scripts

**Always check existing code first** before writing new scripts or functions:
1. Search for similar functionality in existing files (use Grep/Glob)
2. Review existing implementations to understand patterns and conventions
3. Check if code can be reused, extended, or modified rather than recreated
4. Only write new scripts when existing code doesn't serve the purpose or when extending existing patterns

This prevents duplication and maintains consistency across the codebase.

# Research Direction

## Core Novelty: Waveform-Only Features

**The key innovation of this project is predicting fouling class from GPR Ez waveform features alone** — without relying on metadata (material composition, density, moisture, etc.).

**Why this matters:**
- Metadata is derived from lab measurements or simulation inputs, making it unavailable in real-world GPR deployments
- Waveform features (572-dimensional: time-domain, Hilbert, frequency, STFT, grid) are extracted directly from the received signal
- The goal is to develop a classifier that works on field data where only the Ez A-scan is available

**Training approach:**
- Primary model: RF trained on **waveform features only** (no metadata)
- Baseline: 0.7083 balanced accuracy on 30k samples with 572 waveform features
- Metadata can be used for validation/analysis but **should not be features in the production model**

**When adding features or changing the pipeline:**
- Prioritize waveform feature engineering (signal processing, wavelets, time-frequency, statistical moments)
- Avoid adding metadata columns as features — they defeat the research goal
- If metadata is needed, use it for stratification, analysis, or post-hoc validation only
- Focus on improving the core 572 waveform features or developing new signal-based features
