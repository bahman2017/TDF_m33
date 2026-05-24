"""Tests for NFW and Burkert halo models."""

import numpy as np
import pytest

from tdf_m33.models.baryonic import compute_v_bar
from tdf_m33.models.halo import (
    burkert_mass_enclosed,
    burkert_velocity,
    combined_velocity,
    nfw_mass_enclosed,
    nfw_velocity,
)


def test_nfw_velocity_finite_nonnegative() -> None:
    r = np.linspace(0.01, 30.0, 50)
    v = nfw_velocity(r, rho_s_msun_kpc3=1e7, r_s_kpc=5.0)
    assert np.all(np.isfinite(v))
    assert np.all(v >= 0)


def test_burkert_velocity_finite_nonnegative() -> None:
    r = np.linspace(0.01, 30.0, 50)
    v = burkert_velocity(r, rho0_msun_kpc3=1e7, r0_kpc=7.5)
    assert np.all(np.isfinite(v))
    assert np.all(v >= 0)


def test_halo_mass_enclosed_increases() -> None:
    r = np.array([1.0, 5.0, 10.0, 20.0])
    m_nfw = nfw_mass_enclosed(r, 1e7, 5.0)
    m_bur = burkert_mass_enclosed(r, 1e7, 7.5)
    assert np.all(np.diff(m_nfw) > 0)
    assert np.all(np.diff(m_bur) > 0)


def test_combined_velocity_quadrature() -> None:
    r = np.array([1.0, 5.0, 10.0])
    v_bar = np.array([20.0, 50.0, 60.0])
    v_halo = nfw_velocity(r, 1e7, 5.0)
    v_model = combined_velocity(r, v_bar, v_halo)
    expected = np.sqrt(v_bar**2 + v_halo**2)
    assert np.allclose(v_model, expected)


def test_v_model_matches_bar_plus_halo_components() -> None:
    v_gas = np.array([10.0, 30.0])
    v_disk = np.array([40.0, 50.0])
    v_bulge = np.array([0.0, 0.0])
    v_bar = compute_v_bar(v_gas, v_disk, v_bulge)
    r = np.array([5.0, 15.0])
    v_halo = burkert_velocity(r, 5e6, 8.0)
    v_tot = combined_velocity(r, v_bar, v_halo)
    assert np.all(v_tot >= v_bar)
