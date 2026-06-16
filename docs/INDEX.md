# Synth-GPR Documentation Index

**Last Updated:** 2026-06-16  
**Status:** Current

Navigate by category to find the documentation you need.

---

## 📋 Core Project Documentation

### Getting Started
- [Setup & Installation](setup/README.md) — Installation, prerequisites, environment setup
- [User Guide](setup/USER_GUIDE.md) — Basic workflows and common tasks
- [Troubleshooting](setup/TROUBLESHOOTING.md) — Solutions for common problems

### Project Overview
- [Fouling Documentation](../Fouling.md) — Fouling classes, PVC/FI definitions, geophysical background
- [Project Instructions](../.claude/CLAUDE.md) — Development guidelines and research direction

---

## 🏗️ Architecture & Design

### System Design
- [Generation Process](architecture/GENERATION_PROCESS.md) — Complete synthetic data pipeline
- [Dataset Structure](architecture/DATASET_STRUCTURE.md) — Input/output file formats
- [Output File Placement](architecture/OUTPUT_FILE_PLACEMENT_RULES.md) — Where to save generated files

### GPR Simulation
- [Input File Generation](architecture/IN_FILE_GENERATION.md) — Creating gprMax `.in` files with gpr_commands
- [Rock Loading Guide](architecture/ROCK_LOADING_GUIDE.md) — Reusing rock geometries across frequencies
- [Antenna Calibration](architecture/ANTENNA_CALIBRATION.md) — Taguchi optimization for antenna parameters
- [Antenna Coupling Code](architecture/COUPLING_CODE_EXAMPLES.md) — Code examples for antenna positioning

### Data Organization
- [Single Source of Truth](architecture/SINGLE_SOURCE_OF_TRUTH.md) — File format and consistency
- [IO Consolidation Plan](architecture/IO_CONSOLIDATION_PLAN.md) — Unified data I/O operations

---

## 🔬 Algorithms & Methods

### Rock Packing
- [Packing Algorithms Guide](algorithms/PACKING_ALGORITHMS.md) — 12 algorithms, selection criteria, speed/quality tradeoffs
- [Algorithm Comparison](algorithms/PACKING_STRATEGIES_ANALYSIS.md) — Detailed performance analysis
- [Sphere vs Angular Rocks](algorithms/TRIANGLES_VS_SPHERES.md) — When to use cylinders vs. triangles

### Coordinate Systems
- [Coordinate System Overview](coordinate-systems/COORDINATE_SYSTEM.md) — Domain layout and conventions
- [Coordinate Fix Summary](coordinate-systems/COORDINATE_FIX_SUMMARY.md) — Bug fixes and corrections
- [Visual Diagram](coordinate-systems/VISUAL_COORDINATE_DIAGRAM.md) — ASCII art reference

---

## 📊 Validation & Testing

### Validation
- [Validation Framework](reports/VALIDATION.md) — Testing strategy and metrics
- [Verification Report](reports/VERIFICATION.md) — Current test coverage status
- [FI 2D Verification](FI_2D_VERIFICATION.md) — Literature-backed methods to map 2D virtual-sieve FI to lab FI thresholds

### Waveform Calibration & Validation (2026-06-16)
- [Final Calibration Summary](FINAL_CALIBRATION_SUMMARY.md) — ✅ COMPLETE — Complete validation of 88.76% synthetic-real correlation
- [Waveform Calibration Results](WAVEFORM_CALIBRATION_RESULTS.md) — Detailed 3-parameter optimization (Gaussian, 420 MHz, 30mm bistatic)
- [gprMax Sampling Control](GPRMAX_SAMPLING_CONTROL.md) — dt fundamentals, CFL condition, post-processing resampling workflow

### Analysis & Reports
- [ML Pipeline Workflow](reports/ML_PIPELINE_WORKFLOW.md) — Feature extraction → Training → Evaluation
- [Codebase Structure](reports/CODEBASE_STRUCTURE.md) — Directory organization and module overview
- [CLI Reference](reports/CLI_REFERENCE.md) — Command-line tool documentation
- [Test Files Status](reports/TEST_FILES_STATUS.md) — Test file inventory and coverage

---

## 🔍 Research & Studies

### Antenna Theory
- [Diamanti & Annan (2013)](studies/diamanti.md) — GPR antenna radiation patterns and energy distribution
- [Giannopoulos (2005)](studies/giani.md) — GprMax FDTD modeling fundamentals

### Experimental Notes
- [FDTD Medium Dimension Selection](studies/FDTD%20Medium%20Dimension%20Selection.md) — Domain sizing guidelines (Khosravi Largani et al. 2025)
- [Real Data Methodology](research/REAL_DATA_METHODOLOGY.md) — Acquiring and processing real GPR data
- [Objectives & Hypothesis](research/OBJECTIVES_AND_HYPOTHESIS.md) — Research goals and framework
- [V2 Generation Spec](research/V2_GENERATION_SPEC.md) — Regeneration spec folding in phantom-rock fix, domain-width finding, antenna height, direct-wave subtraction (DRAFT)
- [Experiment Limitations](research/EXPERIMENT_LIMITATIONS.md) — Known constraints and assumptions

### Reference Materials
- [Research References](research/REFERENCES.md) — Complete bibliography
- [LLM Agent Guidelines](research/LLM_AGENT_GUIDELINES.md) — For AI assistants working on codebase

---

## 🛠️ Operations & Scripting

### Workflows
- [Scripts Guide](operations/SCRIPTS_GUIDE.md) — Batch processing and automation
- [Configuration Guide](reports/SMART_CONFIG_GUIDE.md) — Advanced configuration options
- [Todo/Roadmap](operations/TODO.md) — Planned work and milestones

### Agents & Automation
- [Agents Documentation](architecture/AGENTS.md) — Autonomous workers and orchestration

---

## 📦 Archived Documentation

The following documents are kept for historical reference only. **Do not rely on them for current workflows:**

- `docs/archived/` contains 15 superseded documents
  - Most archived docs have been consolidated into active documentation above
  - Only 4 archived files are referenced elsewhere in codebase
  - Safe to ignore unless doing historical analysis

**To remove archived docs:** Clean up requires verification that no external references exist.

---

## Quick Links by Task

### I want to...

**Generate synthetic GPR data:**
→ [Setup/README.md](setup/README.md) → Generation Process → Packing Algorithms Guide

**Run simulations:**
→ [Input File Generation](architecture/IN_FILE_GENERATION.md) → Running Simulations section

**Extract features:**
→ [ML Pipeline Workflow](reports/ML_PIPELINE_WORKFLOW.md)

**Train a classifier:**
→ [ML Pipeline Workflow](reports/ML_PIPELINE_WORKFLOW.md) → Training section

**Understand the project:**
→ [Fouling.md](../Fouling.md) → [Project Instructions](./.claude/CLAUDE.md)

**Fix an antenna issue:**
→ [Antenna Calibration](architecture/ANTENNA_CALIBRATION.md) → [Antenna Coupling](architecture/COUPLING_CODE_EXAMPLES.md)

**Compare rock packing algorithms:**
→ [Packing Algorithms Guide](algorithms/PACKING_ALGORITHMS.md) → Algorithm Comparison

**Troubleshoot problems:**
→ [Troubleshooting Guide](setup/TROUBLESHOOTING.md)

---

## Documentation Maintenance

**Status indicators:**
- ✅ Current — Matches latest codebase (reviewed within last month)
- ⚠️ Stale — Partially outdated, use with caution
- ❌ Archived — Historical only, do not use for new work

All active documentation should be marked **Current** before committing changes.

**To update docs:**
1. Ensure code changes are complete
2. Update relevant `.md` files
3. Run broken link check (see troubleshooting)
4. Update last-modified date at top of file
5. Commit with message: `docs: update [file] to match [code change]`
