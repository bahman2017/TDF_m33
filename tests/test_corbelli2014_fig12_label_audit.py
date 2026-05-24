"""Tests for Corbelli 2014 Fig. 12 label audit (Phase 1D-D2-A2)."""

from pathlib import Path

import pandas as pd
import pytest

from tdf_m33.data.corbelli2014_baryonic import build_baryonic_audit_table, load_table1_raw
from tdf_m33.data.corbelli2014_fig12 import (
    compare_baryonic_to_fig12,
    load_fig12_spotcheck,
    validate_comparison_df,
)
from tdf_m33.data.corbelli2014_fig12_label_audit import (
    LABEL_AUDIT_COLUMNS,
    build_corrected_spotcheck,
    build_label_audit_table,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
SPOTCHECK_CSV = (
    REPO_ROOT / "data" / "raw" / "extracted" / "corbelli2014_fig12_baryonic_spotcheck.csv"
)
CORRECTED_CSV = (
    REPO_ROOT
    / "data"
    / "raw"
    / "extracted"
    / "corbelli2014_fig12_baryonic_spotcheck_corrected.csv"
)
LABEL_AUDIT_CSV = REPO_ROOT / "outputs" / "tables" / "corbelli2014_fig12_label_audit.csv"
COMPARISON_CORRECTED_CSV = (
    REPO_ROOT / "outputs" / "tables" / "corbelli2014_baryonic_fig12_comparison_corrected.csv"
)
RAW_CSV = REPO_ROOT / "data" / "raw" / "extracted" / "corbelli2014_table1_raw.csv"
MODEL_READY = REPO_ROOT / "data" / "processed" / "m33_rotation.csv"


def test_label_audit_csv_exists_with_recommendation() -> None:
    assert LABEL_AUDIT_CSV.is_file(), "run scripts/audit_corbelli2014_fig12_labels.py"
    df = pd.read_csv(LABEL_AUDIT_CSV)
    assert list(df.columns) == list(LABEL_AUDIT_COLUMNS)
    assert "recommendation" in df.columns
    assert df["recommendation"].astype(str).str.len().gt(10).all()
    assert df["swapped_abs_residual_sum"].sum() < df["old_abs_residual_sum"].sum()


def test_original_labels_likely_swapped() -> None:
    raw = load_table1_raw(RAW_CSV)
    audit = build_baryonic_audit_table(raw, coarse_grid=True)
    spotcheck = load_fig12_spotcheck(SPOTCHECK_CSV)
    _df, verdict, _rec = build_label_audit_table(spotcheck, audit)
    assert verdict == "LIKELY_SWAPPED"


def test_corrected_spotcheck_improves_residuals() -> None:
    if not CORRECTED_CSV.is_file():
        pytest.skip("run audit script first")
    raw = load_table1_raw(RAW_CSV)
    audit = build_baryonic_audit_table(raw, coarse_grid=True)
    corrected = load_fig12_spotcheck(CORRECTED_CSV)
    comparison, status, _notes = compare_baryonic_to_fig12(audit, corrected)
    assert status in ("PASS", "PASS_WITH_CAVEAT", "REVIEW_REQUIRED")
    assert validate_comparison_df(comparison) == []
    assert status in ("PASS", "PASS_WITH_CAVEAT")


def test_corrected_comparison_csv_on_disk() -> None:
    if not COMPARISON_CORRECTED_CSV.is_file():
        pytest.skip("run compare script --corrected")
    df = pd.read_csv(COMPARISON_CORRECTED_CSV)
    assert df["validation_status"].iloc[0] in (
        "PASS",
        "PASS_WITH_CAVEAT",
        "REVIEW_REQUIRED",
    )


def test_model_ready_csv_still_absent() -> None:
    assert not MODEL_READY.is_file()


def test_build_corrected_spotcheck_swaps_columns() -> None:
    old = load_fig12_spotcheck(SPOTCHECK_CSV)
    new = build_corrected_spotcheck(old)
    assert new.loc[0, "v_gas_digitized_kms"] == old.loc[0, "v_disk_digitized_kms"]
    assert new.loc[0, "v_disk_digitized_kms"] == old.loc[0, "v_gas_digitized_kms"]
