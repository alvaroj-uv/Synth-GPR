#!/usr/bin/env python3
"""
Phase 3 guardrails for the dataset (feature parquet) I/O layer
(src.dataset_io). See docs/architecture/IO_CONSOLIDATION_PLAN.md.
"""

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.dataset_io import load_features, save_dataset


@pytest.fixture
def df():
    return pd.DataFrame({
        "sample_id": np.arange(20),
        "label": (["C", "MC", "MF", "F", "HF"] * 4),
        "feat_0": np.random.default_rng(0).standard_normal(20).astype("float32"),
        "feat_1": np.random.default_rng(1).standard_normal(20).astype("float32"),
    })


class TestRoundTrip:
    def test_save_then_load_all_columns(self, df, tmp_path):
        p = tmp_path / "d.parquet"
        save_dataset(df, p)
        back = load_features(p)
        pd.testing.assert_frame_equal(back, df)

    def test_no_index_written_by_default(self, df, tmp_path):
        p = tmp_path / "d.parquet"
        save_dataset(df, p)
        back = load_features(p)
        # default RangeIndex, i.e. the frame's index was not persisted as a column
        assert "__index_level_0__" not in back.columns
        assert list(back.columns) == list(df.columns)

    def test_column_projection(self, df, tmp_path):
        p = tmp_path / "d.parquet"
        save_dataset(df, p)
        proj = load_features(p, columns=["sample_id", "label"])
        assert list(proj.columns) == ["sample_id", "label"]
        assert len(proj) == len(df)

    def test_dtypes_preserved(self, df, tmp_path):
        p = tmp_path / "d.parquet"
        save_dataset(df, p)
        back = load_features(p)
        assert back["feat_0"].dtype == np.float32


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
