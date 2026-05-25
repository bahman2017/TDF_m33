"""Tests for Phase 5C-A López Fune 2017 constraint extraction."""

from pathlib import Path

import pandas as pd
import pytest
import yaml

from tdf_m33.lensing.lopez_fune_2017_extraction import (
    PARAMS_CSV,
    PROFILE_CSV,
    SOURCE_ID,
    run_phase5c_lopez_fune_extraction_audit,
    validate_extracted_constraints,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
CONFIG = REPO_ROOT / "configs" / "m33_default.yaml"

FORBIDDEN_AFFIRMATIVE = (
    "dark matter disproven: true",
    "no need for dark matter",
    "replaces dark matter",
)


@pytest.fixture(scope="module")
def extracted_tables(tmp_path_factory: pytest.TempPathFactory) -> tuple[Path, Path]:
    tmp = tmp_path_factory.mktemp("lopez_extract")
    profile_df, params_df, _ = run_phase5c_lopez_fune_extraction_audit(
        CONFIG,
        tmp / "status.csv",
        tmp / "report.md",
        regenerate=True,
    )
    # Tables written to repo paths by regenerate — use repo paths
    return REPO_ROOT / PROFILE_CSV, REPO_ROOT / PARAMS_CSV


def test_extracted_files_exist(extracted_tables: tuple[Path, Path]) -> None:
    profile_path, params_path = extracted_tables
    assert profile_path.is_file()
    assert params_path.is_file()


def test_validation_passes(extracted_tables: tuple[Path, Path]) -> None:
    errors = validate_extracted_constraints(REPO_ROOT, CONFIG)
    assert errors == []


def test_profile_schema(extracted_tables: tuple[Path, Path]) -> None:
    profile_path, _ = extracted_tables
    df = pd.read_csv(profile_path)
    assert (df["source_id"] == SOURCE_ID).all()
    assert (df["r_kpc"] > 0).all()
    assert (df["rho_dm_value"] > 0).all()
    assert df["extraction_method"].notna().all()
    assert df["reference"].notna().all()
    assert "comparison" not in " ".join(df.columns).lower()


def test_config_safeguards() -> None:
    with CONFIG.open() as f:
        cfg = yaml.safe_load(f)
    limits = cfg["tdf"]["lensing"]["observational_limits"]
    assert limits["enabled"] is False
    phys = cfg["tdf"]["lensing"]["physical_calibration"]
    assert phys["enabled"] is False
    assert phys["output_units"] == "normalized_proxy"


def test_audit_report_no_forbidden_claims(tmp_path_factory: pytest.TempPathFactory) -> None:
    tmp = tmp_path_factory.mktemp("lopez_audit")
    _, _, _ = run_phase5c_lopez_fune_extraction_audit(
        CONFIG, tmp / "s.csv", tmp / "report.md", regenerate=False
    )
    report = (tmp / "report.md").read_text(encoding="utf-8").lower()
    for phrase in FORBIDDEN_AFFIRMATIVE:
        assert phrase not in report
    assert "normalized_proxy" in report
    assert "no τ-map comparison" in report or "no tau-map comparison" in report
