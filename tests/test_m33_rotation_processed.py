"""Tests for canonical processed M33 rotation CSV (Phase 1D-D2-B)."""

from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from tdf_m33.data.corbelli2014_baryonic import EXPECTED_AUDIT_ROWS
from tdf_m33.data.m33_rotation_processed import (
    DATA_QUALITY_FLAG,
    PROCESSED_NOTES,
    SOURCE_ID,
    build_m33_rotation_processed,
    write_m33_rotation_processed,
)
from tdf_m33.data.schema import REQUIRED_COLUMNS
from tdf_m33.data.validation import validate_m33_dataframe

REPO_ROOT = Path(__file__).resolve().parents[1]
AUDIT_CSV = (
    REPO_ROOT / "outputs" / "tables" / "corbelli2014_baryonic_velocity_derivation_audit.csv"
)
PROCESSED_CSV = REPO_ROOT / "data" / "processed" / "m33_rotation.csv"
TABLE1_RAW = REPO_ROOT / "data" / "raw" / "extracted" / "corbelli2014_table1_raw.csv"
FIG12_CORRECTED = (
    REPO_ROOT
    / "data"
    / "raw"
    / "extracted"
    / "corbelli2014_fig12_baryonic_spotcheck_corrected.csv"
)


def test_build_script_creates_processed_csv(tmp_path: Path) -> None:
    if not AUDIT_CSV.is_file():
        pytest.skip("audit CSV missing")
    out = tmp_path / "m33_rotation.csv"
    df = write_m33_rotation_processed(AUDIT_CSV, out)
    assert out.is_file()
    assert len(df) == EXPECTED_AUDIT_ROWS
    assert validate_m33_dataframe(df) == []


def test_processed_csv_on_disk_if_present() -> None:
    if not PROCESSED_CSV.is_file():
        pytest.skip("run scripts/build_m33_rotation_processed.py")
    df = pd.read_csv(PROCESSED_CSV)
    assert len(df) == 58
    for col in REQUIRED_COLUMNS:
        assert col in df.columns
    assert validate_m33_dataframe(df) == []


def test_v_obs_matches_table1_endpoints() -> None:
    if not PROCESSED_CSV.is_file() or not TABLE1_RAW.is_file():
        pytest.skip("processed or raw Table 1 missing")
    proc = pd.read_csv(PROCESSED_CSV).sort_values("r_kpc")
    raw = pd.read_csv(TABLE1_RAW).sort_values("r_kpc")
    assert proc.iloc[0]["v_obs_kms"] == pytest.approx(raw.iloc[0]["v_rot_kms"])
    assert proc.iloc[-1]["v_obs_kms"] == pytest.approx(raw.iloc[-1]["v_rot_kms"])


def test_baryonic_velocities_from_d1_audit_not_fig12() -> None:
    if not PROCESSED_CSV.is_file() or not AUDIT_CSV.is_file():
        pytest.skip("processed or audit missing")
    proc = pd.read_csv(PROCESSED_CSV).sort_values("r_kpc")
    audit = pd.read_csv(AUDIT_CSV).sort_values("r_kpc")
    assert np.allclose(proc["v_gas_kms"], audit["v_gas_kms"], rtol=1.0e-9)
    assert np.allclose(proc["v_disk_kms"], audit["v_disk_kms"], rtol=1.0e-9)

    if FIG12_CORRECTED.is_file():
        spot = pd.read_csv(FIG12_CORRECTED)
        # Canonical velocities must not match digitized Fig. 12 at inner radii
        r1 = proc.loc[(proc["r_kpc"] - 1.0).abs().idxmin()]
        s1 = spot.loc[spot["r_kpc"] == 1.0].iloc[0]
        assert r1["v_gas_kms"] == pytest.approx(audit.loc[
            (audit["r_kpc"] - 1.0).abs().idxmin(), "v_gas_kms"
        ])
        assert not np.isclose(r1["v_gas_kms"], s1["v_gas_digitized_kms"], rtol=0.05)


def test_v_bulge_zero_and_quality_flag() -> None:
    if not PROCESSED_CSV.is_file():
        pytest.skip("processed CSV missing")
    df = pd.read_csv(PROCESSED_CSV)
    assert np.all(df["v_bulge_kms"] == 0.0)
    assert (df["data_quality_flag"] == DATA_QUALITY_FLAG).all()
    assert "PASS_WITH_CAVEAT" in PROCESSED_NOTES
    assert (df["source_id"] == SOURCE_ID).all()
    assert not np.allclose(df["v_gas_kms"], df["sigma_gas"], rtol=1.0e-3)
    assert not np.allclose(df["v_disk_kms"], df["sigma_star"], rtol=1.0e-3)


def test_build_from_audit_dataframe() -> None:
    audit = pd.read_csv(AUDIT_CSV) if AUDIT_CSV.is_file() else None
    if audit is None:
        pytest.skip("audit missing")
    proc = build_m33_rotation_processed(audit)
    assert proc["notes"].iloc[0] == PROCESSED_NOTES
    assert proc["galaxy_id"].iloc[0] == "M33"
