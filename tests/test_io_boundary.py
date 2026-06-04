#!/usr/bin/env python3
"""
Phase 4 — architectural fitness functions that lock in the I/O boundary built in
Phases 1–2 (see docs/architecture/IO_CONSOLIDATION_PLAN.md).

Scripts must go through the specialized `src` abstractions:
  * `.out` HDF5  -> src.data_loader (read_ascan / read_rx_traces / write_rx_out)
  * `.in` files  -> src.visualization.scene.parse_in_file
                    + src.file_reader.parse_metadata_comments

These tests fail if a script reaches around those abstractions, so new code
can't silently regress the boundary.
"""

import re
from pathlib import Path

import pytest

SCRIPTS = Path(__file__).parent.parent / "scripts"


def _py_files():
    return sorted(SCRIPTS.rglob("*.py"))


def _rel(p: Path) -> str:
    return p.relative_to(SCRIPTS).as_posix()


# ── Phase 1 lock: no raw h5py in scripts ──────────────────────────────────────
# analyze_dataset_structure.py is the one sanctioned exception: it is an HDF5
# *structure introspection* diagnostic (walks raw groups/datasets) and counts
# unique raw-string .in metadata values into sets — needs neither signal reader.
H5PY_WHITELIST = {"analysis/analyze_dataset_structure.py"}


def test_no_raw_h5py_in_scripts():
    offenders = [
        _rel(p) for p in _py_files()
        if _rel(p) not in H5PY_WHITELIST and re.search(r"\bh5py\b", p.read_text(encoding="utf-8", errors="replace"))
    ]
    assert not offenders, (
        "Scripts must read/write .out via src.data_loader, not raw h5py:\n  "
        + "\n  ".join(offenders)
    )


# ── Phase 2 lock: the duplicate 3D .in parser must not come back ───────────────
def test_parse_3d_in_file_not_reintroduced():
    offenders = [
        _rel(p) for p in _py_files()
        if "def parse_3d_in_file" in p.read_text(encoding="utf-8", errors="replace")
    ]
    assert not offenders, (
        "3D .in parsing is unified in src.visualization.scene.parse_in_file; "
        "do not reintroduce parse_3d_in_file:\n  " + "\n  ".join(offenders)
    )


# ── Phase 3 ratchet: parquet I/O may shrink but not grow ──────────────────────
# Phase 3 will route these through a src dataset-IO module. Until then, this
# ratchet prevents NEW scripts from hand-rolling parquet I/O. As Phase 3 migrates
# files, they simply drop out of the offender set (subset still holds), and the
# baseline can be trimmed.
PARQUET_BASELINE = {
    "analysis/domain_adapt.py",
    "analysis/rock_vs_homog_rigorous.py",
    "analysis/sim2real_gap.py",
    "analysis/sim2real_regularized.py",
    "analysis/validate_real.py",
    "experiments/homog_debye_slope.py",
    "experiments/peplinski_slope.py",
    "experiments/phantom_domain_shift.py",
    "experiments/phantom_recovery_stage1.py",
    "pipeline/build_parquet.py",
    "pipeline/build_parquet_coda_aligned.py",
    "pipeline/build_parquet_merged.py",
    "pipeline/train_rf.py",
    "pipeline/train_rf_ldcp_fi_est.py",
    "pipeline/train_rf_waveform_only.py",
    "pipeline/train_rf_waveform_only_grouped.py",
}


def test_parquet_usage_does_not_grow():
    current = {
        _rel(p) for p in _py_files()
        if re.search(r"\b(read_parquet|to_parquet)\b", p.read_text(encoding="utf-8", errors="replace"))
    }
    new = current - PARQUET_BASELINE
    assert not new, (
        "New scripts must use the src dataset-IO layer (Phase 3), not raw "
        "pd.read_parquet/to_parquet:\n  " + "\n  ".join(sorted(new))
    )


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
