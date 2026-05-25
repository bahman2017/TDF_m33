"""Tests for Phase 5B-C López Fune et al. 2017 source acquisition audit."""

from pathlib import Path

import pytest
import yaml

from tdf_m33.lensing.phase5bc_lopez_fune_source_audit import (
    run_phase5bc_lopez_fune_source_audit,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
CONFIG = REPO_ROOT / "configs" / "m33_default.yaml"
PDF = REPO_ROOT / "data/raw/downloads/lopez_fune_salucci_corbelli_2017_m33.pdf"
PLAN = REPO_ROOT / "docs/lopez_fune_2017_extraction_plan.md"

FORBIDDEN_AFFIRMATIVE = (
    "dark matter disproven: true",
    "no need for dark matter",
    "replaces dark matter",
)


@pytest.fixture
def pdf_available() -> bool:
    return PDF.is_file()


def test_lopez_fune_audit_outputs(tmp_path: Path, pdf_available: bool) -> None:
    if not pdf_available:
        pytest.skip("López Fune 2017 PDF not acquired locally")

    status_df = run_phase5bc_lopez_fune_source_audit(
        CONFIG,
        tmp_path / "status.csv",
        tmp_path / "report.md",
    )
    assert (tmp_path / "status.csv").is_file()
    assert (tmp_path / "report.md").is_file()

    row = status_df.iloc[0]
    assert row["acquisition_status"] == "documented"
    assert bool(row["observational_limits_enabled"]) is False
    assert bool(row["numerical_comparison_performed"]) is False
    assert bool(row["physical_arcsec_conversion"]) is False
    assert bool(row["alpha_tau_scale_fitted"]) is False
    assert bool(row["direct_lensing_measurement"]) is False
    assert len(row["sha256"]) == 64

    report = (tmp_path / "report.md").read_text(encoding="utf-8").lower()
    for phrase in FORBIDDEN_AFFIRMATIVE:
        assert phrase not in report
    assert "arcsec" not in report or "no arcsec" in report or "not" in report


def test_extraction_plan_exists() -> None:
    assert PLAN.is_file()
    text = PLAN.read_text(encoding="utf-8")
    assert "Fig. 6" in text or "Figure 6" in text
    assert "circularity" in text.lower()


def test_config_limits_still_disabled() -> None:
    with CONFIG.open() as f:
        cfg = yaml.safe_load(f)
    limits = cfg["tdf"]["lensing"]["observational_limits"]
    assert limits["enabled"] is False
    assert limits["lopez_fune_2017"]["acquisition_status"] == "documented"
