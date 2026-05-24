"""Corbelli et al. 2014 baryonic surface-density and velocity derivation helpers."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

from tdf_m33.constants import (
    CORBELLI2014_GAS_HALF_THICKNESS_KPC,
    CORBELLI2014_HELIUM_FACTOR,
    CORBELLI2014_SIGMA_H2_NORM,
    CORBELLI2014_SIGMA_H2_SCALE_KPC,
)
from tdf_m33.models.disk_gravity import (
    circular_velocity_curve_kms,
    stellar_half_thickness_kpc,
)

DERIVATION_METHOD = "axisymmetric_disk_gravity_exponential_vertical"
DERIVATION_NOTES = (
    "Phase 1D-D1 interim audit: Sigma_gas=1.33*(Sigma_HI+Sigma_H2), Sigma_H2=10*exp(-R/2.2); "
    "v_gas/v_disk from numerical midplane disk gravity (exponential vertical profile); "
    "gas h_z=0.5 kpc; stellar h_z flares 0.1–1.0 kpc at R=23 kpc; v_bulge=0; not model-ready CSV."
)

AUDIT_COLUMNS = [
    "source_id",
    "r_kpc",
    "v_obs_kms",
    "v_err_kms",
    "sigma_hi",
    "sigma_h2",
    "sigma_gas",
    "sigma_star",
    "v_gas_kms",
    "v_disk_kms",
    "v_bulge_kms",
    "v_bar_kms",
    "derivation_method",
    "derivation_notes",
]

EXPECTED_AUDIT_ROWS = 58


def sigma_h2_msun_pc2(r_kpc: np.ndarray | float) -> np.ndarray:
    """Molecular gas surface density per Corbelli et al. 2014 Sect. 2.2 (M_sun pc^-2)."""
    r = np.asarray(r_kpc, dtype=float)
    return CORBELLI2014_SIGMA_H2_NORM * np.exp(-r / CORBELLI2014_SIGMA_H2_SCALE_KPC)


def sigma_gas_msun_pc2(sigma_hi: np.ndarray, sigma_h2: np.ndarray) -> np.ndarray:
    """Total gas surface density including helium (M_sun pc^-2)."""
    return CORBELLI2014_HELIUM_FACTOR * (np.asarray(sigma_hi, dtype=float) + np.asarray(sigma_h2, dtype=float))


def load_table1_raw(path: str | Path) -> pd.DataFrame:
    return pd.read_csv(path)


def build_baryonic_audit_table(
    raw_df: pd.DataFrame,
    *,
    coarse_grid: bool = False,
) -> pd.DataFrame:
    """Derive interim baryonic velocities from Table 1 surface densities."""
    from tdf_m33.models.disk_gravity import DiskGravityGrid

    r = raw_df["r_kpc"].to_numpy(dtype=float)
    sigma_hi = raw_df["sigma_hi"].to_numpy(dtype=float)
    sigma_h2 = sigma_h2_msun_pc2(r)
    sigma_gas = sigma_gas_msun_pc2(sigma_hi, sigma_h2)
    sigma_star = raw_df["sigma_star"].to_numpy(dtype=float)

    grid = DiskGravityGrid(
        n_radial=120 if coarse_grid else 240,
        n_azimuth=36 if coarse_grid else 72,
        n_vertical=24 if coarse_grid else 48,
    )

    v_gas = circular_velocity_curve_kms(
        r,
        r,
        sigma_gas,
        CORBELLI2014_GAS_HALF_THICKNESS_KPC,
        grid=grid,
    )
    v_disk = circular_velocity_curve_kms(
        r,
        r,
        sigma_star,
        stellar_half_thickness_kpc,
        grid=grid,
    )
    v_bulge = np.zeros_like(r)
    v_bar = np.sqrt(v_gas**2 + v_disk**2 + v_bulge**2)

    return pd.DataFrame(
        {
            "source_id": raw_df["source_id"],
            "r_kpc": r,
            "v_obs_kms": raw_df["v_rot_kms"].to_numpy(dtype=float),
            "v_err_kms": raw_df["v_err_kms"].to_numpy(dtype=float),
            "sigma_hi": sigma_hi,
            "sigma_h2": sigma_h2,
            "sigma_gas": sigma_gas,
            "sigma_star": sigma_star,
            "v_gas_kms": v_gas,
            "v_disk_kms": v_disk,
            "v_bulge_kms": v_bulge,
            "v_bar_kms": v_bar,
            "derivation_method": DERIVATION_METHOD,
            "derivation_notes": DERIVATION_NOTES,
        }
    )


def validate_baryonic_audit_df(df: pd.DataFrame) -> list[str]:
    """Return validation error messages for the interim audit table."""
    errors: list[str] = []

    if len(df) != EXPECTED_AUDIT_ROWS:
        errors.append(f"expected {EXPECTED_AUDIT_ROWS} rows, got {len(df)}")

    missing = [c for c in AUDIT_COLUMNS if c not in df.columns]
    if missing:
        errors.append(f"missing columns: {missing}")
        return errors

    if not (df["r_kpc"].diff().dropna() > 0).all():
        errors.append("r_kpc must be strictly increasing")

    for col in ("sigma_h2", "sigma_gas", "v_gas_kms", "v_disk_kms", "v_bar_kms"):
        if (df[col] < 0).any():
            errors.append(f"{col} must be >= 0")

    if (df["sigma_gas"] < df["sigma_hi"] - 1.0e-9).any():
        errors.append("sigma_gas must be >= sigma_hi (H2 + helium)")

    if not np.allclose(df["v_bulge_kms"], 0.0):
        errors.append("v_bulge_kms must be 0 for all rows")

    if np.allclose(df["v_gas_kms"], df["sigma_gas"]):
        errors.append("v_gas_kms must not be identical to sigma_gas")
    if np.allclose(df["v_disk_kms"], df["sigma_star"]):
        errors.append("v_disk_kms must not be identical to sigma_star")

    v_bar_sq = df["v_gas_kms"] ** 2 + df["v_disk_kms"] ** 2 + df["v_bulge_kms"] ** 2
    if not np.allclose(df["v_bar_kms"] ** 2, v_bar_sq, rtol=1.0e-6, atol=1.0e-4):
        errors.append("v_bar_kms^2 must equal sum of squared components")

    return errors
