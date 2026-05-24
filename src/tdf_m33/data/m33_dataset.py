"""Canonical M33 processed rotation dataset loader (Phase 2+)."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import pandas as pd

from tdf_m33.data.io import load_m33_processed_csv
from tdf_m33.data.validation import (
    CORBELLI_2014_ROW_COUNT,
    assert_valid_m33_dataframe,
)

DEFAULT_PROCESSED_PATH = Path("data/processed/m33_rotation.csv")

PROVENANCE_COLUMNS = ("source_id", "data_quality_flag", "notes")


@dataclass(frozen=True)
class M33RotationDataset:
    """Validated canonical M33 rotation table with provenance fields."""

    data: pd.DataFrame
    path: Path

    @property
    def n_rows(self) -> int:
        return len(self.data)

    def provenance(self) -> pd.DataFrame:
        """Per-row source_id, data_quality_flag, and notes."""
        return self.data[list(PROVENANCE_COLUMNS)].copy()


def load_m33_rotation_dataset(
    path: str | Path | None = None,
    *,
    repo_root: Path | None = None,
) -> M33RotationDataset:
    """
    Load and validate ``data/processed/m33_rotation.csv``.

    Preserves scientific columns and provenance; does not modify velocities.
    """
    if path is None:
        base = repo_root or Path.cwd()
        path = base / DEFAULT_PROCESSED_PATH
    path = Path(path)
    df = load_m33_processed_csv(path)
    assert_valid_m33_dataframe(df)
    if len(df) != CORBELLI_2014_ROW_COUNT:
        raise ValueError(
            f"expected {CORBELLI_2014_ROW_COUNT} rows in canonical dataset, got {len(df)}"
        )
    return M33RotationDataset(data=df, path=path.resolve())
