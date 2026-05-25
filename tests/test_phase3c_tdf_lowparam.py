"""Tests for Phase 3C low-parameter TDF pipeline."""

from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from tdf_m33.fitting.phase3c_tdf_lowparam import (
    build_combined_comparison,
    fit_lowparam_knot_model,
    load_phase3c_config,
    run_phase3c_tdf_lowparam,
)
from tdf_m33.fitting.halo_fit import fit_radius_mask

REPO_ROOT = Path(__file__).resolve().parents[1]
CONFIG = REPO_ROOT / "configs" / "m33_default.yaml"
PROCESSED = REPO_ROOT / "data" / "processed" / "m33_rotation.csv"
PHASE3A = REPO_ROOT / "outputs" / "tables" / "phase3a_tau_radial_reconstruction.csv"
PHASE2B = REPO_ROOT / "outputs" / "tables" / "phase2b_model_comparison.csv"


@pytest.fixture
def inputs_available() -> bool:
    return PROCESSED.is_file() and PHASE2B.is_file()


def test_phase3c_pipeline(tmp_path: Path, inputs_available: bool) -> None:
    if not inputs_available:
        pytest.skip("processed CSV or Phase 2B comparison missing")

    comparison_df, params_df, profiles_df, combined_df = run_phase3c_tdf_lowparam(
        PROCESSED,
        CONFIG,
        tmp_path / "comparison.csv",
        tmp_path / "params.csv",
        tmp_path / "profiles.csv",
        tmp_path / "combined.csv",
        tmp_path / "rot.png",
        tmp_path / "grad.png",
        tmp_path / "res.png",
        PHASE2B,
        phase3a_path=PHASE3A if PHASE3A.is_file() else None,
    )

    for name in ("comparison.csv", "params.csv", "profiles.csv", "combined.csv"):
        assert (tmp_path / name).is_file()
    for name in ("rot.png", "grad.png", "res.png"):
        assert (tmp_path / name).is_file()

    assert set(comparison_df["model_name"]) == {
        "tdf_lowparam_3knot",
        "tdf_lowparam_4knot",
        "tdf_lowparam_5knot",
    }
    for col in ("aic", "bic", "chi_square", "parameter_count"):
        assert col in comparison_df.columns

    assert (comparison_df["parameter_count"] == comparison_df["model_name"].str.extract(
        r"(\d+)knot"
    )[0].astype(int)).all()

    models = set(combined_df["model_name"])
    assert {"baryonic_only", "nfw", "burkert"}.issubset(models)
    assert "tdf_lowparam_4knot" in models
    assert "burkert" in combined_df["model_name"].values
    burk = combined_df[combined_df["model_name"] == "burkert"].iloc[0]
    assert "burkert" in str(burk["notes"]).lower() or "BVI" in str(burk["notes"])

    assert "lensing" not in "".join(profiles_df.columns).lower()
    assert len(profiles_df) == 58 * 3


def test_fit_finite_velocities(inputs_available: bool) -> None:
    if not inputs_available:
        pytest.skip("inputs missing")

    from tdf_m33.data.m33_dataset import load_m33_rotation_dataset
    from tdf_m33.models.baryonic import build_baryonic_profile

    cfg = load_phase3c_config(CONFIG)
    ds = load_m33_rotation_dataset(PROCESSED)
    prof = build_baryonic_profile(ds.data.sort_values("r_kpc"))
    r = prof["r_kpc"].to_numpy()
    mask = fit_radius_mask(r, cfg["fit_min_radius_kpc"], cfg["fit_max_radius_kpc"])
    fit = fit_lowparam_knot_model(
        r,
        prof["v_obs_kms"].to_numpy(),
        prof["v_err_kms"].to_numpy(),
        prof["v_bar_kms"].to_numpy(),
        4,
        cfg,
        fit_mask=mask,
        phase3a_path=PHASE3A if PHASE3A.is_file() else None,
    )
    assert fit.parameter_count == 4
    assert np.all(np.isfinite(fit.v_model_kms[mask]))
    assert np.all(fit.v_model_kms[mask] > 0)


def test_combined_has_aic_bic() -> None:
    if not PHASE2B.is_file():
        pytest.skip("phase2b missing")
    p2 = pd.read_csv(PHASE2B)
    tdf_row = {
        "model_name": "tdf_lowparam_4knot",
        "n_points": 56,
        "rmse_kms": 1.0,
        "chi_square": 10.0,
        "reduced_chi_square": 0.2,
        "parameter_count": 4,
        "aic": 18.0,
        "bic": 25.0,
        "n_negative_residual_v2": 0,
        "notes": "test",
        "n_fit_points": 56,
        "dof": 51,
        "fit_r_min_kpc": 0.4,
        "fit_r_max_kpc": 23.0,
        "n_rows_total": 58,
    }
    combined = build_combined_comparison(p2, [tdf_row])
    assert "aic" in combined.columns
    assert "tdf_lowparam_4knot" in combined["model_name"].values
