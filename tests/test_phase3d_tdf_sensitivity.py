"""Tests for Phase 3D TDF sensitivity audit."""

from pathlib import Path

import pandas as pd
import pytest

from tdf_m33.fitting.phase3d_tdf_sensitivity import run_phase3d_tdf_sensitivity

REPO_ROOT = Path(__file__).resolve().parents[1]
CONFIG = REPO_ROOT / "configs" / "m33_default.yaml"
PROCESSED = REPO_ROOT / "data" / "processed" / "m33_rotation.csv"
PHASE3C = REPO_ROOT / "outputs" / "tables" / "phase3c_tdf_lowparam_model_comparison.csv"
PHASE3A = REPO_ROOT / "outputs" / "tables" / "phase3a_tau_radial_reconstruction.csv"
COMBINED = REPO_ROOT / "outputs" / "tables" / "phase3c_combined_model_comparison.csv"


@pytest.fixture
def inputs_available() -> bool:
    return all(
        p.is_file()
        for p in (PROCESSED, PHASE3C, PHASE3A, COMBINED)
    )


def test_phase3d_outputs(tmp_path: Path, inputs_available: bool) -> None:
    if not inputs_available:
        pytest.skip("Phase 3 prerequisites missing")

    summary_df, ktau_df, mask_df, smooth_df, _ = run_phase3d_tdf_sensitivity(
        PROCESSED,
        CONFIG,
        PHASE3C,
        PHASE3A,
        COMBINED,
        tmp_path / "summary.csv",
        tmp_path / "ktau.csv",
        tmp_path / "mask.csv",
        tmp_path / "smooth.csv",
        tmp_path / "report.md",
        tmp_path / "fig.png",
    )

    assert (tmp_path / "summary.csv").is_file()
    assert (tmp_path / "ktau.csv").is_file()
    assert (tmp_path / "mask.csv").is_file()
    assert (tmp_path / "smooth.csv").is_file()
    assert (tmp_path / "report.md").is_file()
    assert (tmp_path / "fig.png").is_file()

    report = (tmp_path / "report.md").read_text(encoding="utf-8").lower()
    assert "no lensing" in report or "not lensing" in report
    assert summary_df[summary_df["check_name"] == "dark_matter_disproven"]["value"].iloc[0] == "false"
    assert "pass_with_caveat" in report or "pass_with" in report

    assert set(ktau_df["k_tau"].tolist()) == {0.5, 1.0, 2.0}
    assert set(smooth_df["sigma_kpc"].tolist()) == {0.5, 0.75, 1.0, 1.5}
    assert len(mask_df) >= 3
    assert "corbelli_default" in mask_df["mask_name"].values

    combined = pd.read_csv(COMBINED)
    assert "nfw" in combined["model_name"].values

    assert "best_tdf_by_aic" in summary_df["check_name"].values


def test_no_2d_or_lensing_outputs(tmp_path: Path, inputs_available: bool) -> None:
    if not inputs_available:
        pytest.skip("inputs missing")

    run_phase3d_tdf_sensitivity(
        PROCESSED,
        CONFIG,
        PHASE3C,
        PHASE3A,
        COMBINED,
        tmp_path / "summary.csv",
        tmp_path / "ktau.csv",
        tmp_path / "mask.csv",
        tmp_path / "smooth.csv",
        tmp_path / "report.md",
        tmp_path / "fig.png",
    )
    for f in tmp_path.iterdir():
        name = f.name.lower()
        assert "lensing" not in name
        assert "2d" not in name or "sensitivity" in name
