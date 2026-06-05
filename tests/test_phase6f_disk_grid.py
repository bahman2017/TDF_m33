"""Tests for Phase 6F disk grid."""

import numpy as np

from tdf_m33.maps.grid import build_disk_grid


def test_grid_shapes_and_coordinates() -> None:
    grid = build_disk_grid(extent_kpc=5.0, pixel_scale_kpc=1.0, mask_radius_kpc=4.0)
    assert grid.x_kpc.shape == grid.y_kpc.shape == grid.R_kpc.shape
    assert grid.R_kpc.shape == grid.phi_rad.shape == grid.mask.shape
    r_expected = np.sqrt(grid.x_kpc**2 + grid.y_kpc**2)
    np.testing.assert_allclose(grid.R_kpc, r_expected, rtol=1e-12)
    assert grid.mask.sum() < grid.mask.size


def test_phi_quadrants() -> None:
    grid = build_disk_grid(extent_kpc=2.0, pixel_scale_kpc=0.5)
    assert np.any(grid.phi_rad[grid.y_kpc > 0] > 0)
    assert np.any(grid.phi_rad[grid.y_kpc < 0] < 0)
