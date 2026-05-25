"""Tests for Phase 2C model comparison audit."""

from pathlib import Path

import pandas as pd
import pytest

from tdf_m33.fitting.phase2c_model_audit import (
    build_audit_summary,
    build_residual_readiness,
    burkert_at_upper_r0_bound,
    run_phase2c_model_audit,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
PHASE2A_METRICS = REPO_ROOT / "outputs" / "tables" / "phase2a_baryonic_only_metrics.csv"
PHASE2A_PROFILE = REPO_ROOT / "outputs" / "tables" / "phase2a_baryonic_only_profile.csv"
PHASE2B_COMPARISON = REPO_ROOT / "outputs" / "tables" / "phase2b_model_comparison.csv"
PHASE2B_PARAMETERS = REPO_ROOT / "outputs" / "tables" / "phase2b_halo_fit_parameters.csv"
PHASE2B_PROFILES = REPO_ROOT / "outputs" / "tables" / "phase2b_rotation_profiles.csv"
CONFIG = REPO_ROOT / "configs" / "m33_default.yaml"


@pytest.fixture
def phase2_inputs_available() -> bool:
    paths = (
        PHASE2A_METRICS,
        PHASE2A_PROFILE,
        PHASE2B_COMPARISON,
        PHASE2B_PARAMETERS,
        PHASE2B_PROFILES,
    )
    return all(p.is_file() for p in paths)


def test_burkert_boundary_flag() -> None:
    assert burkert_at_upper_r0_bound(199.99, 2.301) is True
    assert burkert_at_upper_r0_bound(7.5, 2.301) is False


def test_phase2c_audit_outputs(tmp_path: Path, phase2_inputs_available: bool) -> None:
    if not phase2_inputs_available:
        pytest.skip("Phase 2A/2B outputs missing; run phase2 scripts first")

    summary_df, readiness_df, report_md = run_phase2c_model_audit(
        PHASE2A_METRICS,
        PHASE2A_PROFILE,
        PHASE2B_COMPARISON,
        PHASE2B_PARAMETERS,
        PHASE2B_PROFILES,
        tmp_path / "summary.csv",
        tmp_path / "report.md",
        tmp_path / "readiness.csv",
        fig_out=tmp_path / "fig.png",
        config_path=CONFIG,
    )

    assert (tmp_path / "report.md").is_file()
    assert "reconstruction" in report_md.lower() and "TDF" in report_md
    assert "Burkert" in report_md
    assert "PASS_WITH_CAVEAT" in report_md or "pass_with_caveat" in report_md.lower()

    assert set(summary_df["model_name"]) == {"baryonic_only", "nfw", "burkert"}
    bur = summary_df[summary_df["model_name"] == "burkert"].iloc[0]
    assert bool(bur["burkert_at_r0_upper_bound"]) is True
    assert summary_df["tau_reconstruction_performed"].eq(False).all()
    assert summary_df["is_tdf_model"].eq(False).all()

    assert len(readiness_df) == 58
    assert "delta_v2_kms2" in readiness_df.columns
    assert "tau" not in "".join(readiness_df.columns).lower()

    profile_2a = pd.read_csv(PHASE2A_PROFILE)
    merged = readiness_df.merge(
        profile_2a[["r_kpc", "residual_v2_kms2"]],
        on="r_kpc",
        how="left",
    )
    assert merged["delta_v2_kms2"].equals(merged["residual_v2_kms2"])

    assert (tmp_path / "fig.png").is_file()
    assert not (tmp_path / "lensing").exists()


def test_audit_summary_columns(phase2_inputs_available: bool) -> None:
    if not phase2_inputs_available:
        pytest.skip("Phase 2A/2B outputs missing")

    comparison = pd.read_csv(PHASE2B_COMPARISON)
    params = pd.read_csv(PHASE2B_PARAMETERS)
    metrics_2a = pd.read_csv(PHASE2A_METRICS)

    summary = build_audit_summary(comparison, params, metrics_2a, CONFIG)
    assert "aic" in summary.columns
    assert "burkert_at_r0_upper_bound" in summary.columns
    nfw = summary[summary["model_name"] == "nfw"].iloc[0]
    assert nfw["nfw_is_lcdm_baseline_not_tdf"] is True


def test_residual_readiness_from_phase2a(phase2_inputs_available: bool) -> None:
    if not phase2_inputs_available:
        pytest.skip("Phase 2A profile missing")

    profile = pd.read_csv(PHASE2A_PROFILE)
    readiness, summary = build_residual_readiness(profile)
    assert len(readiness) == 58
    assert summary["all_delta_v2_positive"] is True
    assert summary["n_negative_delta_v2"] == 0
    assert "phase3_input_residual" in summary
