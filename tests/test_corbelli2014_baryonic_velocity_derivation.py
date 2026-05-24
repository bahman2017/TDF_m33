"""Tests for Corbelli 2014 baryonic velocity derivation audit."""

from pathlib import Path

import numpy as np
import pandas as pd

from tdf_m33.data.corbelli2014_baryonic import (
    EXPECTED_AUDIT_ROWS,
    build_baryonic_audit_table,
    load_table1_raw,
    validate_baryonic_audit_df,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
RAW_CSV = REPO_ROOT / "data" / "raw" / "extracted" / "corbelli2014_table1_raw.csv"
AUDIT_CSV = (
    REPO_ROOT
    / "outputs"
    / "tables"
    / "corbelli2014_baryonic_velocity_derivation_audit.csv"
)
MODEL_READY = REPO_ROOT / "data" / "processed" / "m33_rotation.csv"


def test_build_audit_table_row_count() -> None:
    raw = load_table1_raw(RAW_CSV)
    audit = build_baryonic_audit_table(raw, coarse_grid=True)
    assert len(audit) == EXPECTED_AUDIT_ROWS
    assert validate_baryonic_audit_df(audit) == []


def test_sigma_not_aliased_to_velocity() -> None:
    raw = load_table1_raw(RAW_CSV)
    audit = build_baryonic_audit_table(raw, coarse_grid=True)
    assert not np.allclose(audit["v_gas_kms"], audit["sigma_gas"])
    assert not np.allclose(audit["v_disk_kms"], audit["sigma_star"])


def test_bulge_zero_and_vbar_identity() -> None:
    raw = load_table1_raw(RAW_CSV)
    audit = build_baryonic_audit_table(raw, coarse_grid=True)
    assert np.allclose(audit["v_bulge_kms"], 0.0)
    v2 = audit["v_gas_kms"] ** 2 + audit["v_disk_kms"] ** 2
    assert np.allclose(audit["v_bar_kms"] ** 2, v2, rtol=1.0e-6)


def test_audit_csv_on_disk_if_present() -> None:
    if not AUDIT_CSV.is_file():
        return
    df = pd.read_csv(AUDIT_CSV)
    assert validate_baryonic_audit_df(df) == []


def test_model_ready_csv_still_absent() -> None:
    assert not MODEL_READY.is_file()
