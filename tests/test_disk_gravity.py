"""Tests for axisymmetric disk gravity utilities."""

import numpy as np

from tdf_m33.constants import MSUN_PC2_TO_MSUN_KPC2
from tdf_m33.models.disk_gravity import (
    DiskGravityGrid,
    circular_velocity_kms,
    sigma_msun_pc2_to_kpc2,
    stellar_half_thickness_kpc,
)
from tdf_m33.data.corbelli2014_baryonic import sigma_gas_msun_pc2, sigma_h2_msun_pc2


def test_sigma_unit_conversion() -> None:
    assert sigma_msun_pc2_to_kpc2(1.0) == MSUN_PC2_TO_MSUN_KPC2


def test_sigma_h2_formula() -> None:
    assert np.isclose(sigma_h2_msun_pc2(0.0), 10.0)
    assert np.isclose(sigma_h2_msun_pc2(2.2), 10.0 / np.e)


def test_helium_scaling() -> None:
    r = np.array([1.0, 5.0])
    hi = np.array([5.0, 1.0])
    h2 = sigma_h2_msun_pc2(r)
    gas = sigma_gas_msun_pc2(hi, h2)
    assert np.all(gas >= hi)


def test_stellar_half_thickness_endpoints() -> None:
    assert np.isclose(stellar_half_thickness_kpc(0.0), 0.1)
    assert np.isclose(stellar_half_thickness_kpc(23.0), 1.0)


def test_exponential_disk_finite_velocity() -> None:
    """Simple exponential disk should yield finite positive v_c."""
    r_tab = np.linspace(0.5, 15.0, 40)
    sigma = 100.0 * np.exp(-r_tab / 3.0)  # M_sun / pc^2
    grid = DiskGravityGrid(n_radial=80, n_azimuth=36, n_vertical=24)
    v = circular_velocity_kms(
        5.0,
        r_tab,
        sigma,
        h_z_kpc=0.3,
        grid=grid,
    )
    assert np.isfinite(v)
    assert v > 0.0
