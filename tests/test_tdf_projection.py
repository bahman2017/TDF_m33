"""Unit tests for disk-to-sky τ projection geometry."""

import numpy as np
import pytest

from tdf_m33.models.tdf_projection import (
    deproject_sky_to_disk_coordinates,
    project_disk_to_sky_coordinates,
    project_tau_map_to_sky_plane,
    resolve_projection_geometry,
)


def test_projection_preserves_shape() -> None:
    x = np.linspace(-5, 5, 20)
    y = np.linspace(-5, 5, 15)
    xg, yg = np.meshgrid(x, y)
    tau = np.ones_like(xg)
    out = project_tau_map_to_sky_plane(xg, yg, tau, 56.0, 23.0)
    assert out["tau_sky"].shape == tau.shape
    assert out["x_sky_kpc"].shape == xg.shape


def test_masked_values_remain_masked() -> None:
    xg, yg = np.meshgrid(np.linspace(-3, 3, 10), np.linspace(-3, 3, 10))
    tau = np.ones_like(xg)
    tau[0, 0] = np.nan
    tau[2, 4] = np.nan
    out = project_tau_map_to_sky_plane(xg, yg, tau, 45.0, 0.0)
    assert np.isnan(out["tau_sky"][0, 0])
    assert np.isnan(out["tau_sky"][2, 4])
    assert np.isfinite(out["tau_sky"][5, 5])


def test_roundtrip_disk_sky_disk() -> None:
    xg, yg = np.meshgrid(np.linspace(-10, 10, 50), np.linspace(-10, 10, 50))
    x_s, y_s = project_disk_to_sky_coordinates(xg, yg, 56.0, 23.0)
    x_b, y_b = deproject_sky_to_disk_coordinates(x_s, y_s, 56.0, 23.0)
    np.testing.assert_allclose(x_b, xg, rtol=0, atol=1e-10)
    np.testing.assert_allclose(y_b, yg, rtol=0, atol=1e-10)


def test_placeholder_geometry_flagged() -> None:
    inc, pa, flag, res = resolve_projection_geometry(
        None,
        None,
        allow_placeholder_geometry=True,
        placeholder_inclination_deg=56.0,
        placeholder_position_angle_deg=23.0,
    )
    assert flag is True
    assert inc == 56.0
    assert pa == 23.0
    assert "placeholder" in res


def test_explicit_geometry_not_placeholder() -> None:
    _, _, flag, res = resolve_projection_geometry(30.0, 10.0, allow_placeholder_geometry=True)
    assert flag is False
    assert res == "config_explicit"


def test_placeholder_disallowed_raises() -> None:
    with pytest.raises(ValueError, match="allow_placeholder_geometry"):
        resolve_projection_geometry(None, None, allow_placeholder_geometry=False)
