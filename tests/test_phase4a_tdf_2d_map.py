"""Tests for Phase 4A 2D τ map pipeline."""

from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from tdf_m33.fitting.phase4a_tdf_2d_map import (
    SOURCE_MODEL_DEFAULT,
    load_phase3c_radial_profile,
    run_phase4a_tdf_2d_map,
)
from tdf_m33.models.tdf_map2d import make_disk_plane_grid

REPO_ROOT = Path(__file__).resolve().parents[1]
CONFIG = REPO_ROOT / "configs" / "m33_default.yaml"
PROFILES = REPO_ROOT / "outputs" / "tables" / "phase3c_tdf_lowparam_profiles.csv"


@pytest.fixture
def profiles_available() -> bool:
    return PROFILES.is_file()


def test_source_model_is_3knot(profiles_available: bool) -> None:
    if not profiles_available:
        pytest.skip("Phase 3C profiles missing")
    df = load_phase3c_radial_profile(PROFILES, SOURCE_MODEL_DEFAULT)
    assert (df["model_name"] == "tdf_lowparam_3knot").all()
    assert len(df) >= 50


def test_phase4a_pipeline(tmp_path: Path, profiles_available: bool) -> None:
    if not profiles_available:
        pytest.skip("Phase 3C profiles missing")

    consistency_df, metadata_df, maps = run_phase4a_tdf_2d_map(
        PROFILES,
        CONFIG,
        tmp_path / "consistency.csv",
        tmp_path / "metadata.csv",
        tmp_path / "map.npz",
        tmp_path / "tau.png",
        tmp_path / "grad.png",
        tmp_path / "consistency.png",
    )

    for name in (
        "consistency.csv",
        "metadata.csv",
        "map.npz",
        "tau.png",
        "grad.png",
        "consistency.png",
    ):
        assert (tmp_path / name).is_file()

    meta = metadata_df.iloc[0]
    assert meta["source_model"] == "tdf_lowparam_3knot"
    assert meta["k_tau"] == pytest.approx(1.0)
    assert "no lensing" in meta["note_no_lensing"].lower()
    assert "axisymmetric" in meta["note_axisymmetric_extension"].lower()

    assert maps["tau_map"].shape == (300, 300)
    assert maps["masked_fraction"] > 0.0
    assert meta["max_abs_radial_consistency_error"] < 50.0
    assert meta["rmse_radial_consistency_error"] < 10.0

    valid = np.isfinite(consistency_df["tau_radial"]) & np.isfinite(
        consistency_df["tau_azimuthal_avg"]
    )
    assert valid.sum() >= 40

    # No lensing outputs
    assert not any(tmp_path.glob("*lensing*"))


def test_no_halo_residual_columns_used(profiles_available: bool) -> None:
    if not profiles_available:
        pytest.skip("profiles missing")
    df = load_phase3c_radial_profile(PROFILES, SOURCE_MODEL_DEFAULT)
    forbidden = {"v_nfw", "v_burkert", "residual_nfw", "halo"}
    cols = {c.lower() for c in df.columns}
    assert not any(any(f in c for f in forbidden) for c in cols)
    assert "delta_v2_kms2" in df.columns


def test_grid_config_matches_config(profiles_available: bool) -> None:
    if not profiles_available:
        pytest.skip("profiles missing")
    from tdf_m33.fitting.phase4a_tdf_2d_map import load_phase4a_config

    cfg = load_phase4a_config(CONFIG)
    x, y = make_disk_plane_grid(
        cfg["x_extent_kpc"], cfg["y_extent_kpc"], cfg["n_pixels"]
    )
    assert x.shape == (cfg["n_pixels"], cfg["n_pixels"])
