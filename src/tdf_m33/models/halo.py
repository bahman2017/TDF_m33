"""Spherical NFW and Burkert halo models (Phase 2B baselines only)."""

from __future__ import annotations

import numpy as np

from tdf_m33.constants import G_KPC

# Minimum radius [kpc] for v_c = sqrt(G M / r) to avoid division by zero at r=0
_R_MIN_KPC: float = 1.0e-8


def _as_radius_kpc(r_kpc: np.ndarray | float) -> np.ndarray:
    r = np.asarray(r_kpc, dtype=float)
    return np.maximum(r, _R_MIN_KPC)


def nfw_density(
    r_kpc: np.ndarray | float,
    rho_s_msun_kpc3: float,
    r_s_kpc: float,
) -> np.ndarray:
    """NFW density ρ(r) = ρ_s / [(r/r_s)(1 + r/r_s)²] [M☉ kpc⁻³]."""
    r = _as_radius_kpc(r_kpc)
    if rho_s_msun_kpc3 <= 0 or r_s_kpc <= 0:
        raise ValueError("rho_s and r_s must be positive")
    x = r / r_s_kpc
    return rho_s_msun_kpc3 / (x * (1.0 + x) ** 2)


def nfw_mass_enclosed(
    r_kpc: np.ndarray | float,
    rho_s_msun_kpc3: float,
    r_s_kpc: float,
) -> np.ndarray:
    """Enclosed NFW mass M(<r) [M☉]."""
    r = np.asarray(r_kpc, dtype=float)
    if rho_s_msun_kpc3 <= 0 or r_s_kpc <= 0:
        raise ValueError("rho_s and r_s must be positive")
    x = np.maximum(r / r_s_kpc, 0.0)
    # M(<r) = 4π ρ_s r_s³ [ln(1+x) - x/(1+x)]
    mass = (
        4.0
        * np.pi
        * rho_s_msun_kpc3
        * r_s_kpc**3
        * (np.log1p(x) - x / (1.0 + x))
    )
    return np.where(r <= 0, 0.0, mass)


def nfw_velocity(
    r_kpc: np.ndarray | float,
    rho_s_msun_kpc3: float,
    r_s_kpc: float,
) -> np.ndarray:
    """Circular speed from NFW enclosed mass [km/s]."""
    r = _as_radius_kpc(r_kpc)
    m = nfw_mass_enclosed(r, rho_s_msun_kpc3, r_s_kpc)
    v2 = G_KPC * m / r
    return np.sqrt(np.maximum(v2, 0.0))


def burkert_density(
    r_kpc: np.ndarray | float,
    rho0_msun_kpc3: float,
    r0_kpc: float,
) -> np.ndarray:
    """Burkert density ρ(r) = ρ₀ / [(1+r/r₀)(1+(r/r₀)²)] [M☉ kpc⁻³]."""
    r = _as_radius_kpc(r_kpc)
    if rho0_msun_kpc3 <= 0 or r0_kpc <= 0:
        raise ValueError("rho0 and r0 must be positive")
    x = r / r0_kpc
    return rho0_msun_kpc3 / ((1.0 + x) * (1.0 + x**2))


def burkert_mass_enclosed(
    r_kpc: np.ndarray | float,
    rho0_msun_kpc3: float,
    r0_kpc: float,
) -> np.ndarray:
    """Enclosed Burkert mass M(<r) [M☉] (Salucci-style integral)."""
    r = np.asarray(r_kpc, dtype=float)
    if rho0_msun_kpc3 <= 0 or r0_kpc <= 0:
        raise ValueError("rho0 and r0 must be positive")
    x = np.maximum(r / r0_kpc, 0.0)
    # M(<r) = 4π ρ₀ r₀³ [ln(1+x) + arctan(x) - ½ ln(1+x²)]
    inner = np.log1p(x) + np.arctan(x) - 0.5 * np.log1p(x**2)
    mass = 4.0 * np.pi * rho0_msun_kpc3 * r0_kpc**3 * inner
    return np.where(r <= 0, 0.0, mass)


def burkert_velocity(
    r_kpc: np.ndarray | float,
    rho0_msun_kpc3: float,
    r0_kpc: float,
) -> np.ndarray:
    """Circular speed from Burkert enclosed mass [km/s]."""
    r = _as_radius_kpc(r_kpc)
    m = burkert_mass_enclosed(r, rho0_msun_kpc3, r0_kpc)
    v2 = G_KPC * m / r
    return np.sqrt(np.maximum(v2, 0.0))


def combined_velocity(
    r_kpc: np.ndarray | float,
    v_bar_kms: np.ndarray | float,
    v_halo_kms: np.ndarray | float,
) -> np.ndarray:
    """v_model² = v_bar² + v_halo² (km/s)."""
    v2 = np.asarray(v_bar_kms, dtype=float) ** 2 + np.asarray(v_halo_kms, dtype=float) ** 2
    return np.sqrt(np.maximum(v2, 0.0))
