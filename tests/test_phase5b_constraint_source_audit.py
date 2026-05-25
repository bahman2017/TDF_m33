"""Tests for Phase 5B-B constraint source review audit."""

from pathlib import Path

import pytest
import yaml

from tdf_m33.lensing.phase5b_constraint_source_audit import (
    run_phase5b_constraint_source_audit,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
CONFIG = REPO_ROOT / "configs" / "m33_default.yaml"
REVIEW_DOC = REPO_ROOT / "docs" / "lensing_constraint_source_review.md"

FORBIDDEN_AFFIRMATIVE = (
    "dark matter disproven: true",
    "no need for dark matter",
    "replaces dark matter",
)


@pytest.fixture
def review_doc_available() -> bool:
    return REVIEW_DOC.is_file()


def test_source_review_doc_exists() -> None:
    assert REVIEW_DOC.is_file()
    text = REVIEW_DOC.read_text(encoding="utf-8").lower()
    assert "normalized_proxy" in text or "normalized" in text
    assert "no observational comparison" in text or "not" in text


def test_phase5bb_audit_outputs(tmp_path: Path, review_doc_available: bool) -> None:
    if not review_doc_available:
        pytest.skip("source review doc missing")

    status_df = run_phase5b_constraint_source_audit(
        CONFIG,
        tmp_path / "status.csv",
        tmp_path / "report.md",
    )
    assert (tmp_path / "status.csv").is_file()
    assert (tmp_path / "report.md").is_file()

    row = status_df.iloc[0]
    assert row["output_units"] == "normalized_proxy"
    assert bool(row["observational_limits_enabled"]) is False
    assert bool(row["physical_calibration_enabled"]) is False
    assert bool(row["numerical_comparison_performed"]) is False
    assert bool(row["physical_conversion_performed"]) is False
    assert bool(row["alpha_tau_scale_fitted"]) is False
    assert bool(row["separate_halo_introduced"]) is False
    assert bool(row["lensing_only_tau_fit"]) is False
    assert row["selected_source_id"] == "lopez_fune_salucci_corbelli_2017"

    report = (tmp_path / "report.md").read_text(encoding="utf-8").lower()
    for phrase in FORBIDDEN_AFFIRMATIVE:
        assert phrase not in report


def test_config_limits_disabled() -> None:
    with CONFIG.open() as f:
        cfg = yaml.safe_load(f)
    limits = cfg["tdf"]["lensing"]["observational_limits"]
    assert limits["enabled"] is False
    assert limits["status"] in ("source_review_complete", "source_documented")
    assert "lopez_fune_salucci_corbelli_2017" in limits["candidate_source_ids"]
