"""Tests for Phase 2A baryonic-only baseline pipeline."""

from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from tdf_m33.data.m33_dataset import load_m33_rotation_dataset
from tdf_m33.data.validation import CORBELLI_PROCESSED_QUALITY_FLAG
from tdf_m33.fitting.metrics import baryonic_only_metrics
from tdf_m33.models.baryonic import compute_v_bar

REPO_ROOT = Path(__file__).resolve().parents[1]
PROCESSED_CSV = REPO_ROOT / "data" / "processed" / "m33_rotation.csv"
METRICS_CSV = REPO_ROOT / "outputs" / "tables" / "phase2a_baryonic_only_metrics.csv"
PROFILE_CSV = REPO_ROOT / "outputs" / "tables" / "phase2a_baryonic_only_profile.csv"
FIG_ROTATION = REPO_ROOT / "outputs" / "figures" / "phase2a_baryonic_only_rotation_curve.png"
FIG_RESIDUAL = REPO_ROOT / "outputs" / "figures" / "phase2a_residual_velocity_squared.png"


def test_loader_returns_58_rows() -> None:
    if not PROCESSED_CSV.is_file():
        pytest.skip("canonical processed CSV missing")
    ds = load_m33_rotation_dataset(PROCESSED_CSV)
    assert ds.n_rows == 58
    assert (ds.data["source_id"] == "corbelli_et_al_2014").all()
    assert (ds.data["data_quality_flag"] == CORBELLI_PROCESSED_QUALITY_FLAG).all()


def test_baryonic_only_parameter_count_zero() -> None:
    if not PROCESSED_CSV.is_file():
        pytest.skip("processed CSV missing")
    ds = load_m33_rotation_dataset(PROCESSED_CSV)
    v_bar = compute_v_bar(
        ds.data["v_gas_kms"], ds.data["v_disk_kms"], ds.data["v_bulge_kms"]
    )
    rv2 = ds.data["v_obs_kms"].to_numpy() ** 2 - v_bar**2
    m = baryonic_only_metrics(
        ds.data["v_obs_kms"].to_numpy(),
        v_bar,
        ds.data["v_err_kms"].to_numpy(),
        rv2,
    )
    assert m.parameter_count == 0
    assert m.aic == pytest.approx(m.chi_square)
    assert m.bic == pytest.approx(m.chi_square)


def test_phase2a_script_outputs(tmp_path: Path) -> None:
    if not PROCESSED_CSV.is_file():
        pytest.skip("processed CSV missing")

    from tdf_m33.fitting.phase2a_baryonic import run_phase2a_baryonic_only

    metrics_path = tmp_path / "metrics.csv"
    profile_path = tmp_path / "profile.csv"
    fig_rot = tmp_path / "rot.png"
    fig_res = tmp_path / "res.png"

    metrics_df, profile_df = run_phase2a_baryonic_only(
        PROCESSED_CSV,
        metrics_path,
        profile_path,
        fig_rot,
        fig_res,
    )

    assert len(profile_df) == 58
    assert metrics_path.is_file()
    assert profile_path.is_file()
    assert fig_rot.is_file()
    assert fig_res.is_file()

    assert "residual_v2_kms2" in profile_df.columns
    assert "source_id" in profile_df.columns
    assert "notes" in profile_df.columns
    assert (profile_df["source_id"] == "corbelli_et_al_2014").all()
    assert metrics_df.iloc[0]["parameter_count"] == 0

    v_bar = compute_v_bar(
        profile_df["v_gas_kms"],
        profile_df["v_disk_kms"],
        profile_df["v_bulge_kms"],
    )
    assert np.allclose(profile_df["v_bar_kms"], v_bar)


def test_phase2a_artifacts_on_disk_if_present() -> None:
    if not METRICS_CSV.is_file():
        pytest.skip("run scripts/run_phase2a_baryonic_only.py")
    metrics = pd.read_csv(METRICS_CSV)
    profile = pd.read_csv(PROFILE_CSV)
    assert len(metrics) == 1
    assert len(profile) == 58
    assert FIG_ROTATION.is_file()
    assert FIG_RESIDUAL.is_file()
    assert int(metrics.iloc[0]["parameter_count"]) == 0
