"""Tests for M33 processed-data validation."""

import numpy as np
import pandas as pd
import pytest

from tdf_m33.data.schema import REQUIRED_COLUMNS
from tdf_m33.data.validation import assert_valid_m33_dataframe, validate_m33_dataframe


def _valid_row() -> dict:
    return {
        "galaxy_id": "M33",
        "r_kpc": 5.0,
        "v_obs_kms": 80.0,
        "v_err_kms": 3.0,
        "v_gas_kms": 30.0,
        "v_disk_kms": 50.0,
        "v_bulge_kms": 0.0,
        "source_id": "corbelli_salucci_2000",
        "data_quality_flag": "ok",
        "notes": "synthetic test row",
    }


def _valid_dataframe() -> pd.DataFrame:
    return pd.DataFrame([_valid_row()])


def test_valid_dataframe_passes() -> None:
    df = _valid_dataframe()
    assert validate_m33_dataframe(df) == []
    assert_valid_m33_dataframe(df)


def test_valid_dataframe_allows_null_velocity_error() -> None:
    row = _valid_row()
    row["v_err_kms"] = np.nan
    row["notes"] = "v_err documented as unavailable in source table"
    df = pd.DataFrame([row])
    assert validate_m33_dataframe(df) == []


def test_missing_required_column_fails() -> None:
    df = _valid_dataframe().drop(columns=["source_id"])
    errors = validate_m33_dataframe(df)
    assert any("Missing required columns" in e for e in errors)
    with pytest.raises(ValueError, match="source_id"):
        assert_valid_m33_dataframe(df)


def test_negative_radius_fails() -> None:
    row = _valid_row()
    row["r_kpc"] = -1.0
    df = pd.DataFrame([row])
    errors = validate_m33_dataframe(df)
    assert any("r_kpc" in e and "positive" in e for e in errors)


def test_negative_baryonic_component_fails() -> None:
    row = _valid_row()
    row["v_gas_kms"] = -5.0
    df = pd.DataFrame([row])
    errors = validate_m33_dataframe(df)
    assert any("v_gas_kms" in e and "nonnegative" in e for e in errors)


def test_missing_source_id_fails() -> None:
    row = _valid_row()
    row["source_id"] = ""
    df = pd.DataFrame([row])
    errors = validate_m33_dataframe(df)
    assert any("source_id" in e for e in errors)


def test_empty_dataframe_with_columns_passes() -> None:
    df = pd.DataFrame(columns=list(REQUIRED_COLUMNS))
    assert validate_m33_dataframe(df) == []
