"""Validation for Corbelli et al. 2014 Table 1 raw/interim CSV (Phase 1D-C)."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd

RAW_TABLE1_COLUMNS = [
    "source_id",
    "raw_table_id",
    "row_id",
    "r_kpc",
    "v_rot_kms",
    "v_err_kms",
    "sigma_hi",
    "sigma_h2",
    "sigma_gas",
    "sigma_star",
    "raw_notes",
    "extraction_method",
    "reference",
]

EXPECTED_ROW_COUNT = 58

FIRST_ROW_SPOT_CHECK: dict[str, float] = {
    "r_kpc": 0.24,
    "v_rot_kms": 37.3,
    "v_err_kms": 6.2,
    "sigma_hi": 7.12,
    "sigma_star": 316.59,
}

LAST_ROW_SPOT_CHECK: dict[str, float] = {
    "r_kpc": 22.72,
    "v_rot_kms": 119.6,
    "v_err_kms": 13.4,
    "sigma_hi": 0.07,
    "sigma_star": 0.13,
}

NUMERIC_COLUMNS = ["r_kpc", "v_rot_kms", "v_err_kms", "sigma_hi", "sigma_star"]


def load_corbelli2014_table1_raw(path: str | Path) -> pd.DataFrame:
    """Load the raw Table 1 CSV."""
    return pd.read_csv(path)


def validate_corbelli2014_table1_raw(df: pd.DataFrame) -> list[str]:
    """Return validation error messages; empty list means PASS."""
    errors: list[str] = []

    missing_cols = [c for c in RAW_TABLE1_COLUMNS if c not in df.columns]
    if missing_cols:
        errors.append(f"missing columns: {missing_cols}")
        return errors

    if len(df) != EXPECTED_ROW_COUNT:
        errors.append(f"expected {EXPECTED_ROW_COUNT} rows, got {len(df)}")

    for col in NUMERIC_COLUMNS:
        if not pd.api.types.is_numeric_dtype(df[col]):
            errors.append(f"column {col} is not numeric")
        elif df[col].isna().any():
            errors.append(f"column {col} has null values")

    if len(df) >= 2 and not (df["r_kpc"].diff().dropna() > 0).all():
        errors.append("r_kpc must be strictly increasing")

    if (df["v_rot_kms"] <= 0).any():
        errors.append("v_rot_kms must be > 0 for all rows")
    if (df["v_err_kms"] <= 0).any():
        errors.append("v_err_kms must be > 0 for all rows")
    if (df["sigma_hi"] < 0).any():
        errors.append("sigma_hi must be >= 0 for all rows")
    if (df["sigma_star"] < 0).any():
        errors.append("sigma_star must be >= 0 for all rows")

    for col in ("sigma_h2", "sigma_gas"):
        if pd.to_numeric(df[col], errors="coerce").notna().any():
            errors.append(f"{col} must be empty for Table 1 transcription")

    if df["source_id"].nunique() != 1 or df["source_id"].iloc[0] != "corbelli_et_al_2014":
        errors.append("source_id must be corbelli_et_al_2014 for all rows")
    if df["raw_table_id"].nunique() != 1 or df["raw_table_id"].iloc[0] != "corbelli2014_table1":
        errors.append("raw_table_id must be corbelli2014_table1 for all rows")
    if list(df["row_id"]) != list(range(1, EXPECTED_ROW_COUNT + 1)):
        errors.append("row_id must be 1..58 consecutive")

    if len(df) > 0:
        first = df.iloc[0]
        last = df.iloc[-1]
        for key, expected in FIRST_ROW_SPOT_CHECK.items():
            if abs(float(first[key]) - expected) > 1e-9:
                errors.append(f"first row {key}: expected {expected}, got {first[key]}")
        for key, expected in LAST_ROW_SPOT_CHECK.items():
            if abs(float(last[key]) - expected) > 1e-9:
                errors.append(f"last row {key}: expected {expected}, got {last[key]}")

    return errors


def assert_valid_corbelli2014_table1_raw(df: pd.DataFrame) -> None:
    errors = validate_corbelli2014_table1_raw(df)
    if errors:
        raise ValueError("; ".join(errors))
