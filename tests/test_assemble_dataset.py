"""T5: dataset assembler — CONFIG_* parsing, label/group derivation, and the
anti-circularity guard (no waveform-feature column may leak eps/sigma/pvc/fi_)."""
import importlib.util
from pathlib import Path

import pytest

_SCRIPT = (Path(__file__).resolve().parent.parent
           / "scripts" / "pipeline" / "assemble_dataset.py")
_spec = importlib.util.spec_from_file_location("assemble_dataset", _SCRIPT)
asm = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(asm)


def test_read_config_mixed_bare_and_config_prefixed_keys():
    # Real generated .in files mix CONFIG_-prefixed replication headers
    # (CONFIG_center_freq_hz, CONFIG_base_seed) with BARE dataset-label headers
    # (Lab_Class, FI_class, pvc) that carry no CONFIG_ prefix at all — confirmed
    # on a real file (experiments/2026-06-22/moisture_sigma_0.0.in). The parser
    # (src.file_reader.parse_metadata_file) must read both, position-independent
    # (headers written AFTER a non-'##' line must still be found), preserving
    # literal key casing (no lowercasing/prefix-stripping).
    # Uses a repo-local temp file to avoid pytest's tmp_path.
    in_file = Path(__file__).parent / "_tmp_assemble_scene.in"
    in_file.write_text(
        "#title: some scene\n"
        "#domain: 0.5 1.5 0.003\n"
        "## Lab_FI: 10.5\n"
        "## Lab_Class: MF\n"
        "## FI_class: MF\n"
        "## pvc: 22.5\n"
        "## CONFIG_center_freq_hz: 4.2e+08\n"
        "## CONFIG_base_seed: 12345\n"
        "## CONFIG_angular_rocks: true\n"
    )
    try:
        cfg = asm._read_config(in_file)
        assert cfg["CONFIG_center_freq_hz"] == 4.2e8
        assert cfg["CONFIG_base_seed"] == 12345 and isinstance(cfg["CONFIG_base_seed"], int)
        assert cfg["Lab_Class"] == "MF"
        assert cfg["FI_class"] == "MF"
        assert cfg["pvc"] == 22.5
        assert cfg["CONFIG_angular_rocks"] is True
    finally:
        in_file.unlink(missing_ok=True)


def test_read_config_missing_file_returns_empty_dict():
    assert asm._read_config(Path(__file__).parent / "_does_not_exist.in") == {}


def test_label_prefers_lab_class_over_fi_class():
    # The actual bug this fixes: FI_class (sampling-time TARGET) and Lab_Class
    # (LabWorker's post-build MEASUREMENT) can legitimately disagree in the
    # legacy pipeline. Lab_Class must always win.
    cfg = {"Lab_Class": "MF", "FI_class": "HF"}
    assert asm._label_from_config(cfg) == "MF"


def test_label_none_without_lab_class_strict_no_fallback():
    # No fallback to FI_class or a pvc-derived estimate: a weaker guess dressed
    # as ground truth is worse than a missing label.
    assert asm._label_from_config({"FI_class": "HF", "pvc": 90.0}) is None
    assert asm._label_from_config({"pvc": 22.5}) is None
    assert asm._label_from_config({}) is None


def test_group_from_config():
    assert asm._group_from_config({"CONFIG_base_seed": 999}, "fallback") == "999"
    assert asm._group_from_config({"CONFIG_actual_seed": 42}, "fallback") == "42"
    assert asm._group_from_config({}, "fallback") == "fallback"


def test_feature_columns_excludes_meta_and_reserved():
    cols = ["hilbert_mean", "coda_x", "meta_eps", "meta_pvc", "label", "domain",
            "group", "fidelity_level", "Signal"]
    assert set(asm.feature_columns(cols)) == {"hilbert_mean", "coda_x"}


def test_anti_circularity_guard():
    clean = ["hilbert_mean", "coda_x", "meta_eps", "meta_sigma", "meta_pvc",
             "label", "domain", "group", "fidelity_level"]
    asm.assert_no_circular_features(clean)              # must not raise
    for leak in (["hilbert_mean", "eps_leak"],
                 ["hilbert_mean", "sigma_x"],
                 ["hilbert_mean", "pvc_frac"],
                 ["fi_class_leak"]):
        with pytest.raises(AssertionError):
            asm.assert_no_circular_features(leak)
