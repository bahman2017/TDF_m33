"""Tests for Corbelli 2014 Fig. 12 baryonic sanity-check (Phase 1D-D2-A)."""

from pathlib import Path

import pandas as pd
import pytest

from tdf_m33.data.corbelli2014_baryonic import build_baryonic_audit_table, load_table1_raw
from tdf_m33.data.corbelli2014_fig12 import (
    COMPARISON_COLUMNS,
    SPOTCHECK_COLUMNS,
    compare_baryonic_to_fig12,
    load_fig12_spotcheck,
    validate_comparison_df,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
SPOTCHECK_CSV = (
    REPO_ROOT / "data" / "raw" / "extracted" / "corbelli2014_fig12_baryonic_spotcheck.csv"
)
AUDIT_CSV = (
    REPO_ROOT / "outputs" / "tables" / "corbelli2014_baryonic_velocity_derivation_audit.csv"
)
COMPARISON_CSV = (
    REPO_ROOT / "outputs" / "tables" / "corbelli2014_baryonic_fig12_comparison.csv"
)
RAW_CSV = REPO_ROOT / "data" / "raw" / "extracted" / "corbelli2014_table1_raw.csv"
MODEL_READY = REPO_ROOT / "data" / "processed" / "m33_rotation.csv"


def test_spotcheck_csv_columns() -> None:
    assert SPOTCHECK_CSV.is_file()
    df = load_fig12_spotcheck(SPOTCHECK_CSV)
    assert list(df.columns) == list(SPOTCHECK_COLUMNS)
    assert len(df) == 5
    assert set(df["r_kpc"].astype(float)) == {1.0, 5.0, 10.0, 15.0, 20.0}


def test_comparison_produces_residuals_and_status() -> None:
    raw = load_table1_raw(RAW_CSV)
    audit = build_baryonic_audit_table(raw, coarse_grid=True)
    spotcheck = load_fig12_spotcheck(SPOTCHECK_CSV)
    comparison, status, _notes = compare_baryonic_to_fig12(audit, spotcheck)

    assert status in ("PASS", "PASS_WITH_CAVEAT", "REVIEW_REQUIRED")
    assert list(comparison.columns) == list(COMPARISON_COLUMNS)
    assert validate_comparison_df(comparison) == []
    assert "residual_gas_kms" in comparison.columns
    assert "residual_disk_kms" in comparison.columns
    assert comparison["validation_status"].nunique() == 1


def test_comparison_csv_on_disk_if_present() -> None:
    if not COMPARISON_CSV.is_file():
        pytest.skip("run scripts/compare_corbelli2014_baryonic_to_fig12.py first")
    df = pd.read_csv(COMPARISON_CSV)
    assert validate_comparison_df(df) == []
    assert df["validation_status"].iloc[0] in (
        "PASS",
        "PASS_WITH_CAVEAT",
        "REVIEW_REQUIRED",
    )


def test_model_ready_csv_still_absent() -> None:
    assert not MODEL_READY.is_file()
