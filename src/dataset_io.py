"""
Dataset (feature parquet) I/O — the single place that reads and writes the
project's feature/label datasets.

Centralizes the parquet engine/compression options and gives the pipeline one
chokepoint where schema/dtype/column contracts can later be enforced without
touching every script. See docs/architecture/IO_CONSOLIDATION_PLAN.md.
"""

from typing import Optional, Sequence

import pandas as pd

# Project-standard write options (matches the dominant build_parquet settings).
_ENGINE = "pyarrow"
_COMPRESSION = "snappy"


def load_features(path, columns: Optional[Sequence[str]] = None) -> pd.DataFrame:
    """
    Load a feature/label dataset parquet.

    Args:
        path: Path to the .parquet file.
        columns: Optional subset of columns to read (column projection); None
            reads all columns.

    Returns:
        The dataset as a DataFrame.
    """
    return pd.read_parquet(path, columns=list(columns) if columns is not None else None)


def save_dataset(df: pd.DataFrame, path, index: bool = False,
                 compression: str = _COMPRESSION) -> None:
    """
    Write a feature/label dataset parquet with the project's standard options
    (pyarrow engine, snappy compression, no index by default).

    Args:
        df: DataFrame to write.
        path: Output .parquet path.
        index: Whether to write the DataFrame index (default False).
        compression: Parquet compression codec (default "snappy").
    """
    df.to_parquet(path, index=index, engine=_ENGINE, compression=compression)
