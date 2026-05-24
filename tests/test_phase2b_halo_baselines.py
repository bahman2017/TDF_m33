"""Tests for Phase 2B NFW/Burkert halo baseline pipeline."""

from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from tdf_m33.data.m33_dataset import load_m33_rotation_dataset
from tdf_m33.fitting.halo_fit import (
    HaloFitBounds,
    fit_halo,
    fit_radius_mask,
)
from tdf_m33.fitting.phase2b_halo_baselines import run_phase2b_halo_baselines
from tdf_m33.models.baryonic import build_baryonic_profile

REPO_ROOT = Path(__file__).resolve().parents[1]
PROCESSED_CSV = REPO_ROOT / "data" / "processed" / "m33_rotation.csv"
CONFIG = REPO_ROOT / "configs" / "m33_default.yaml"
COMPARISON_CSV = REPO_ROOT / "outputs" / "tables" / "phase2b_model_comparison.csv"


def test_halo_fit_positive_parameters() -> None:
    if not PROCESSED_CSV.is_file():
        pytest.skip("processed CSV missing")
    ds = load_m33_rotation_dataset(PROCESSED_CSV)
    prof = build_baryonic_profile(ds.data)
    r = prof["r_kpc"].to_numpy()
    mask = fit_radius_mask(r)
    for kind in ("nfw", "burkert"):
        fit = fit_halo(
            r,
            prof["v_obs_kms"].to_numpy(),
            prof["v_err_kms"].to_numpy(),
            prof["v_bar_kms"].to_numpy(),
            kind,
            fit_mask=mask,
            bounds=HaloFitBounds(),
        )
        assert fit.rho > 0
        assert fit.scale_kpc > 0
        assert fit.parameter_count == 2
        assert np.all(np.isfinite(fit.v_halo_kms))


def test_phase2b_pipeline_outputs(tmp_path: Path) -> None:
    if not PROCESSED_CSV.is_file():
        pytest.skip("processed CSV missing")

    comparison_df, params_df, profiles_df = run_phase2b_halo_baselines(
        PROCESSED_CSV,
        CONFIG,
        tmp_path / "comparison.csv",
        tmp_path / "params.csv",
        tmp_path / "profiles.csv",
        tmp_path / "rot.png",
        tmp_path / "res.png",
    )

    assert set(comparison_df["model_name"]) == {
        "baryonic_only",
        "nfw",
        "burkert",
    }
    assert int(comparison_df.loc[
        comparison_df["model_name"] == "baryonic_only", "parameter_count"
    ].iloc[0]) == 0
    assert int(comparison_df.loc[
        comparison_df["model_name"] == "nfw", "parameter_count"
    ].iloc[0]) == 2
    assert int(comparison_df.loc[
        comparison_df["model_name"] == "burkert", "parameter_count"
    ].iloc[0]) == 2

    for col in ("aic", "bic", "chi_square", "dof", "n_fit_points"):
        assert col in comparison_df.columns

    assert len(profiles_df) == 58
    assert (profiles_df["source_id"] == "corbelli_et_al_2014").all()
    assert "derived_baryonic" in profiles_df["data_quality_flag"].iloc[0]
    assert "v_model_nfw_kms" in profiles_df.columns
    assert "tau" not in "".join(profiles_df.columns).lower()

    assert len(params_df) == 2
    assert (tmp_path / "rot.png").is_file()


def test_phase2b_artifacts_on_disk_if_present() -> None:
    if not COMPARISON_CSV.is_file():
        pytest.skip("run scripts/run_phase2b_halo_baselines.py")
    df = pd.read_csv(COMPARISON_CSV)
    assert len(df) == 3
    assert "dof" in df.columns
