"""Tests for Corbelli et al. 2014 Table 1 raw CSV (Phase 1D-C)."""

from pathlib import Path

import pandas as pd

from tdf_m33.data.corbelli2014_table1_raw import (
    EXPECTED_ROW_COUNT,
    FIRST_ROW_SPOT_CHECK,
    LAST_ROW_SPOT_CHECK,
    RAW_TABLE1_COLUMNS,
    assert_valid_corbelli2014_table1_raw,
    load_corbelli2014_table1_raw,
    validate_corbelli2014_table1_raw,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
RAW_CSV = REPO_ROOT / "data" / "raw" / "extracted" / "corbelli2014_table1_raw.csv"
MODEL_READY = REPO_ROOT / "data" / "processed" / "m33_rotation.csv"


def test_raw_table1_csv_exists() -> None:
    assert RAW_CSV.is_file()


def test_raw_table1_validates() -> None:
    df = load_corbelli2014_table1_raw(RAW_CSV)
    assert validate_corbelli2014_table1_raw(df) == []
    assert_valid_corbelli2014_table1_raw(df)


def test_raw_table1_row_count_and_spot_checks() -> None:
    df = load_corbelli2014_table1_raw(RAW_CSV)
    assert len(df) == EXPECTED_ROW_COUNT
    for key, val in FIRST_ROW_SPOT_CHECK.items():
        assert float(df.iloc[0][key]) == val
    for key, val in LAST_ROW_SPOT_CHECK.items():
        assert float(df.iloc[-1][key]) == val


def test_raw_table1_r_kpc_strictly_increasing() -> None:
    df = load_corbelli2014_table1_raw(RAW_CSV)
    assert (df["r_kpc"].diff().dropna() > 0).all()


def test_raw_table1_columns_match_template() -> None:
    df = pd.read_csv(RAW_CSV, nrows=0)
    for col in RAW_TABLE1_COLUMNS:
        assert col in df.columns


def test_model_ready_csv_valid_when_present() -> None:
    if not MODEL_READY.is_file():
        return
    from tdf_m33.data.io import load_m33_processed_csv
    from tdf_m33.data.validation import validate_m33_dataframe

    df = load_m33_processed_csv(MODEL_READY)
    assert validate_m33_dataframe(df) == []
