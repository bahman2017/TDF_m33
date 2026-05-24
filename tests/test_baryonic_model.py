"""Tests for baryonic-only model helpers."""

import numpy as np
import pandas as pd
import pytest

from tdf_m33.models.baryonic import (
    build_baryonic_profile,
    compute_residual_acceleration,
    compute_residual_velocity_squared,
    compute_v_bar,
    count_negative_residual_v2,
)


def test_v_bar_quadrature_identity() -> None:
    v_gas = np.array([10.0, 20.0])
    v_disk = np.array([30.0, 40.0])
    v_bulge = np.array([0.0, 5.0])
    v_bar = compute_v_bar(v_gas, v_disk, v_bulge)
    expected = np.sqrt(v_gas**2 + v_disk**2 + v_bulge**2)
    assert np.allclose(v_bar, expected)


def test_residual_v2_formula() -> None:
    v_obs = np.array([100.0, 50.0])
    v_bar = np.array([60.0, 70.0])
    rv2 = compute_residual_velocity_squared(v_obs, v_bar)
    assert np.allclose(rv2, v_obs**2 - v_bar**2)


def test_no_silent_clipping_of_negative_residuals() -> None:
    rv2 = compute_residual_velocity_squared(40.0, 50.0)
    assert rv2 < 0
    assert count_negative_residual_v2(np.array([rv2, 100.0])) == 1


def test_residual_acceleration_proxy() -> None:
    r = 5.0
    v_obs, v_bar = 100.0, 60.0
    a = compute_residual_acceleration(r, v_obs, v_bar)
    assert a == pytest.approx((v_obs**2 - v_bar**2) / r)


def test_build_baryonic_profile_preserves_provenance() -> None:
    df = pd.DataFrame(
        {
            "galaxy_id": ["M33"],
            "r_kpc": [5.0],
            "v_obs_kms": [100.0],
            "v_err_kms": [2.0],
            "v_gas_kms": [30.0],
            "v_disk_kms": [50.0],
            "v_bulge_kms": [0.0],
            "source_id": ["corbelli_et_al_2014"],
            "data_quality_flag": ["derived_baryonic_velocity_pass_with_caveat"],
            "notes": ["test row"],
        }
    )
    out = build_baryonic_profile(df)
    assert "v_bar_kms" in out.columns
    assert out["source_id"].iloc[0] == "corbelli_et_al_2014"
    assert "PASS_WITH_CAVEAT" in out["notes"].iloc[0] or out["notes"].iloc[0] == "test row"


def test_residual_acceleration_requires_positive_radius() -> None:
    with pytest.raises(ValueError, match="positive"):
        compute_residual_acceleration(0.0, 100.0, 50.0)
