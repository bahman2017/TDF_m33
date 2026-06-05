"""Tests for Phase 6F tau field solver."""

import numpy as np

from tdf_m33.maps.grid import build_disk_grid
from tdf_m33.maps.solver import solve_tau_field


def test_solver_finite_tau_gaussian_source() -> None:
    grid = build_disk_grid(extent_kpc=4.0, pixel_scale_kpc=0.5, mask_radius_kpc=3.5)
    r2 = grid.R_kpc**2
    j = np.exp(-r2 / 2.0)
    j = np.where(grid.mask, j, 0.0)
    tau, diag = solve_tau_field(
        j,
        grid.mask,
        grid.dx_kpc,
        grid.dy_kpc,
        kappa_tau=1.0,
        m_tau=0.1,
        boundary_condition="dirichlet",
    )
    assert np.all(np.isfinite(tau[grid.mask]))
    assert diag.finite_fraction > 0.99
    assert diag.residual_norm < 1e-2


def test_neumann_boundary_runs() -> None:
    grid = build_disk_grid(extent_kpc=3.0, pixel_scale_kpc=0.5, mask_radius_kpc=2.5)
    j = np.ones(grid.shape) * grid.mask
    tau, diag = solve_tau_field(
        j,
        grid.mask,
        grid.dx_kpc,
        grid.dy_kpc,
        kappa_tau=1.0,
        m_tau=0.0,
        boundary_condition="neumann",
    )
    assert np.all(np.isfinite(tau[grid.mask]))
