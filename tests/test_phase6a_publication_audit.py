"""Tests for Phase 6A publication audit."""

from pathlib import Path

import pandas as pd
import pytest
import yaml

from tdf_m33.reporting.phase6a_publication_audit import (
    FORBIDDEN_REPORT_PHRASES,
    run_phase6a_publication_audit,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
CONFIG = REPO_ROOT / "configs" / "m33_default.yaml"
SUMMARY_MD = REPO_ROOT / "outputs" / "reports" / "phase6a_publication_results_summary.md"
KEY_CSV = REPO_ROOT / "outputs" / "tables" / "phase6a_key_results_table.csv"
CLAIM_CSV = REPO_ROOT / "outputs" / "tables" / "phase6a_claim_traceability_matrix.csv"
REPRO_MD = REPO_ROOT / "outputs" / "reports" / "phase6a_reproducibility_commands.md"

REQUIRED_CLAIM_SNIPPETS = (
    "baryons alone",
    "NFW",
    "Burkert",
    "3-knot TDF",
    "sensitivity",
    "2D",
    "normalized deflection",
    "López Fune",
    "weak-lensing",
    "Dark matter is not disproven",
)


@pytest.fixture(scope="module")
def phase6a_outputs() -> tuple[pd.DataFrame, pd.DataFrame]:
    key_df, claims_df, _ = run_phase6a_publication_audit(
        CONFIG,
        SUMMARY_MD,
        KEY_CSV,
        CLAIM_CSV,
        REPRO_MD,
    )
    return key_df, claims_df


def test_key_results_table_created(phase6a_outputs: tuple[pd.DataFrame, pd.DataFrame]) -> None:
    assert KEY_CSV.is_file()
    key_df, _ = phase6a_outputs
    assert len(key_df) >= 7
    for model in (
        "baryonic_only",
        "nfw",
        "burkert",
        "tdf_lowparam_3knot",
        "tdf_lowparam_5knot",
    ):
        assert model in key_df["result_id"].values


def test_claim_matrix_created(phase6a_outputs: tuple[pd.DataFrame, pd.DataFrame]) -> None:
    assert CLAIM_CSV.is_file()
    _, claims_df = phase6a_outputs
    assert len(claims_df) == 10
    for col in (
        "claim_text",
        "supported_status",
        "supporting_output",
        "caveat",
        "allowed_language",
        "prohibited_language",
    ):
        assert col in claims_df.columns
    assert set(claims_df["supported_status"].unique()) <= {
        "supported",
        "caveated",
        "future_work",
        "prohibited",
    }


def test_required_claim_categories(phase6a_outputs: tuple[pd.DataFrame, pd.DataFrame]) -> None:
    _, claims_df = phase6a_outputs
    text = " ".join(claims_df["claim_text"].astype(str)).lower()
    for snippet in REQUIRED_CLAIM_SNIPPETS:
        assert snippet.lower() in text


def test_reports_created() -> None:
    assert SUMMARY_MD.is_file()
    assert REPRO_MD.is_file()
    repro = REPRO_MD.read_text(encoding="utf-8")
    assert "run_phase3c_tdf_lowparam_model.py" in repro
    assert "run_phase5c_upper_bound_consistency.py" in repro


def test_prohibited_language_absent_from_reports() -> None:
    summary = SUMMARY_MD.read_text(encoding="utf-8").lower()
    repro = REPRO_MD.read_text(encoding="utf-8").lower()
    for phrase in FORBIDDEN_REPORT_PHRASES:
        assert phrase not in summary
        assert phrase not in repro
    assert "not disproven" in summary or "not** disproven" in summary


def test_key_results_reference_phase_outputs(phase6a_outputs: tuple[pd.DataFrame, pd.DataFrame]) -> None:
    key_df, _ = phase6a_outputs
    assert "phase3c_combined_model_comparison.csv" in key_df["supporting_output"].iloc[0]
    lopez = key_df.loc[key_df["result_id"] == "phase5c_upper_bound_lopez_fune"].iloc[0]
    assert lopez["boundary_or_constraint_flag"] == "PASS_WITH_CAVEAT"


def test_config_physical_calibration_disabled() -> None:
    with CONFIG.open() as f:
        cfg = yaml.safe_load(f)
    assert cfg["tdf"]["lensing"]["physical_calibration"]["enabled"] is False
