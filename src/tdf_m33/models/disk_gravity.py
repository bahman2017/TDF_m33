"""Axisymmetric finite-thickness disk circular velocity (numerical midplane gravity)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

import numpy as np

from tdf_m33.constants import G_KPC, MSUN_PC2_TO_MSUN_KPC2


def sigma_msun_pc2_to_kpc2(sigma_pc2: np.ndarray | float) -> np.ndarray | float:
    """Convert surface density from M_sun pc^-2 to M_sun kpc^-2."""
    return np.asarray(sigma_pc2, dtype=float) * MSUN_PC2_TO_MSUN_KPC2


def vertical_volume_density(
    sigma_kpc2: float,
    z_kpc: np.ndarray,
    h_z_kpc: float,
) -> np.ndarray:
    """
    Exponential vertical profile normalised to integrate to Sigma along z:

    rho(R, z) = Sigma(R) / (2 h_z) * exp(-|z| / h_z).
    """
    h_z = max(float(h_z_kpc), 1.0e-6)
    return sigma_kpc2 / (2.0 * h_z) * np.exp(-np.abs(z_kpc) / h_z)


@dataclass(frozen=True)
class DiskGravityGrid:
    """Quadrature resolution for midplane radial acceleration integration."""

    n_radial: int = 240
    n_azimuth: int = 72
    n_vertical: int = 48
    z_span_h_z: float = 10.0
    r_max_pad: float = 1.05
    softening_kpc: float = 0.02


def _sigma_at_radius(
    r_kpc: np.ndarray,
    r_tab_kpc: np.ndarray,
    sigma_tab_kpc2: np.ndarray,
) -> np.ndarray:
    """Linear interpolation of Sigma(R) on the integration grid (M_sun kpc^-2)."""
    return np.interp(
        r_kpc,
        r_tab_kpc,
        sigma_tab_kpc2,
        left=float(sigma_tab_kpc2[0]),
        right=float(sigma_tab_kpc2[-1]),
    )


def radial_acceleration_midplane(
    r_eval_kpc: float,
    r_tab_kpc: np.ndarray,
    sigma_tab_msun_pc2: np.ndarray,
    h_z_kpc: float | Callable[[np.ndarray], np.ndarray],
    *,
    grid: DiskGravityGrid | None = None,
) -> float:
    """
    Inward radial acceleration g_R at cylindrical radius r_eval in the disk midplane (z=0).

    Integrates over azimuthally symmetric surface density Sigma(R') with vertical
    exponential stratification. Observer at (R, 0, 0); source elements at
    (R' cos(phi), R' sin(phi), z).
    """
    grid = grid or DiskGravityGrid()
    r_tab = np.asarray(r_tab_kpc, dtype=float)
    sigma_kpc2 = sigma_msun_pc2_to_kpc2(np.asarray(sigma_tab_msun_pc2, dtype=float))

    r_max = float(r_tab[-1]) * grid.r_max_pad
    dr = r_max / grid.n_radial
    dphi = 2.0 * np.pi / grid.n_azimuth

    rp = (np.arange(grid.n_radial, dtype=float) + 0.5) * dr
    phi = (np.arange(grid.n_azimuth, dtype=float) + 0.5) * dphi

    if callable(h_z_kpc):
        hz_rp = np.maximum(h_z_kpc(rp), 1.0e-6)
    else:
        hz_rp = np.full_like(rp, max(float(h_z_kpc), 1.0e-6))

    sigma_rp = _sigma_at_radius(rp, r_tab, sigma_kpc2)

    g_in = 0.0
    cos_phi = np.cos(phi)
    sin_phi = np.sin(phi)

    for i, r_p in enumerate(rp):
        hz = float(hz_rp[i])
        sig = float(sigma_rp[i])
        z_lim = grid.z_span_h_z * hz
        dz = (2.0 * z_lim) / grid.n_vertical
        z_centers = (np.arange(grid.n_vertical, dtype=float) + 0.5) * dz - z_lim

        rho_z = vertical_volume_density(sig, z_centers, hz)
        dV = r_p * dr * dphi * dz

        x_src = r_p * cos_phi
        y_src = r_p * sin_phi
        dx = r_eval_kpc - x_src
        dy = -y_src
        r3 = (dx * dx + dy * dy + z_centers[:, None] ** 2 + grid.softening_kpc**2) ** 1.5

        # Inward (toward galactic centre) acceleration at r_eval.
        g_in += float(G_KPC * np.sum(rho_z[:, None] * dV * dx / r3))

    return g_in


def circular_velocity_kms(
    r_eval_kpc: float,
    r_tab_kpc: np.ndarray,
    sigma_tab_msun_pc2: np.ndarray,
    h_z_kpc: float | Callable[[np.ndarray], np.ndarray],
    *,
    grid: DiskGravityGrid | None = None,
) -> float:
    """Circular speed v_c = sqrt(R * g_inward) from midplane disk gravity (km/s)."""
    g_in = radial_acceleration_midplane(
        r_eval_kpc,
        r_tab_kpc,
        sigma_tab_msun_pc2,
        h_z_kpc,
        grid=grid,
    )
    if g_in <= 0.0 or r_eval_kpc <= 0.0:
        return 0.0
    return float(np.sqrt(r_eval_kpc * g_in))


def circular_velocity_curve_kms(
    r_eval_kpc: np.ndarray,
    r_tab_kpc: np.ndarray,
    sigma_tab_msun_pc2: np.ndarray,
    h_z_kpc: float | Callable[[np.ndarray], np.ndarray],
    *,
    grid: DiskGravityGrid | None = None,
) -> np.ndarray:
    """Compute v_c(R) for an array of evaluation radii."""
    return np.array(
        [
            circular_velocity_kms(
                float(r),
                r_tab_kpc,
                sigma_tab_msun_pc2,
                h_z_kpc,
                grid=grid,
            )
            for r in r_eval_kpc
        ],
        dtype=float,
    )


def stellar_half_thickness_kpc(r_kpc: np.ndarray | float) -> np.ndarray:
    """Corbelli et al. 2014 flaring stellar disk: 0.1 kpc at centre to 1 kpc at 23 kpc."""
    from tdf_m33.constants import (
        CORBELLI2014_STELLAR_HZ_CENTER_KPC,
        CORBELLI2014_STELLAR_HZ_OUTER_KPC,
        CORBELLI2014_STELLAR_HZ_REF_RADIUS_KPC,
    )

    r = np.asarray(r_kpc, dtype=float)
    slope = (
        CORBELLI2014_STELLAR_HZ_OUTER_KPC - CORBELLI2014_STELLAR_HZ_CENTER_KPC
    ) / CORBELLI2014_STELLAR_HZ_REF_RADIUS_KPC
    return CORBELLI2014_STELLAR_HZ_CENTER_KPC + slope * r
