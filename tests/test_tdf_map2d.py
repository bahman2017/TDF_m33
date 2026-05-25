"""Unit tests for axisymmetric 2D τ map utilities."""

import numpy as np
import pytest

from tdf_m33.models.tdf_map2d import (
    compare_radial_profile_to_map_average,
    compute_azimuthal_average_from_map,
    make_disk_plane_grid,
    radial_interpolate_to_grid,
)


def test_disk_plane_grid_shape() -> None:
    x, y = make_disk_plane_grid(10.0, 10.0, 50)
    assert x.shape == (50, 50)
    assert y.shape == (50, 50)
    assert x.min() == pytest.approx(-10.0)
    assert x.max() == pytest.approx(10.0)


def test_radial_interpolation_finite_inside_range() -> None:
    r = np.array([1.0, 5.0, 10.0])
    tau = np.array([0.0, 100.0, 500.0])
    x, y = make_disk_plane_grid(12.0, 12.0, 80)
    grid = radial_interpolate_to_grid(r, tau, x, y)
    R = np.sqrt(x**2 + y**2)
    inside = (R >= 1.0) & (R <= 10.0)
    assert np.all(np.isfinite(grid[inside]))


def test_outside_radius_masked() -> None:
    r = np.array([2.0, 8.0])
    tau = np.array([10.0, 20.0])
    x, y = make_disk_plane_grid(15.0, 15.0, 60)
    grid = radial_interpolate_to_grid(r, tau, x, y)
    R = np.sqrt(x**2 + y**2)
    assert np.all(np.isnan(grid[R < 2.0]))
    assert np.all(np.isnan(grid[R > 8.0]))


def test_azimuthal_average_recovers_radial_profile() -> None:
    r = np.linspace(1.0, 10.0, 40)
    tau = 50.0 * r**1.2
    x, y = make_disk_plane_grid(12.0, 12.0, 120)
    grid = radial_interpolate_to_grid(r, tau, x, y)
    avg = compute_azimuthal_average_from_map(x, y, grid, r)
    valid = np.isfinite(avg)
    assert valid.sum() >= 30
    np.testing.assert_allclose(avg[valid], tau[valid], rtol=0.05, atol=5.0)


def test_compare_radial_consistency_near_zero_for_axisymmetric() -> None:
    r = np.linspace(1.0, 10.0, 30)
    tau = 100.0 + 20.0 * r
    x, y = make_disk_plane_grid(11.0, 11.0, 100)
    grid = radial_interpolate_to_grid(r, tau, x, y)
    avg = compute_azimuthal_average_from_map(x, y, grid, r)
    result = compare_radial_profile_to_map_average(r, tau, avg)
    assert result["max_abs_error"] < 5.0
    assert result["rmse_radial_consistency"] < 2.0
