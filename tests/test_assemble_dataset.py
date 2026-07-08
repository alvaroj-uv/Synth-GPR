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


def test_read_config_position_independent():
    # CONFIG headers written AFTER non-'##' lines must still be found (the
    # canonical file_reader parser stops at the first non-'##' line and misses
    # them). Uses a repo-local temp file to avoid pytest's tmp_path.
    in_file = Path(__file__).parent / "_tmp_assemble_scene.in"
    in_file.write_text(
        "#title: some scene\n"
        "#domain: 0.5 1.5 0.003\n"
        "## CONFIG_center_freq_hz: 4.2e+08\n"
        "## CONFIG_base_seed: 12345\n"
        "## CONFIG_pvc_sampled: 22.5\n"
        "## CONFIG_angular_rocks: True\n"
    )
    try:
        cfg = asm._read_config(in_file)
        assert cfg["center_freq_hz"] == 4.2e8
        assert cfg["base_seed"] == 12345 and isinstance(cfg["base_seed"], int)
        assert cfg["pvc_sampled"] == 22.5
        assert cfg["angular_rocks"] is True
    finally:
        in_file.unlink(missing_ok=True)


def test_label_and_group_from_config():
    cfg = {"pvc_sampled": 22.5, "base_seed": 999}
    assert asm._label_from_config(cfg) is not None      # pvc -> FI -> class
    assert asm._label_from_config({}) is None
    assert asm._group_from_config(cfg, "fallback") == "999"
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
