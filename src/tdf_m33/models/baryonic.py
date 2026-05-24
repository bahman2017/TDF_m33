"""Baryonic-only rotation-curve helpers (Phase 2A; no halo or TDF)."""

from __future__ import annotations

import numpy as np
import pandas as pd


def compute_v_bar(
    v_gas_kms: np.ndarray | float,
    v_disk_kms: np.ndarray | float,
    v_bulge_kms: np.ndarray | float,
) -> np.ndarray:
    """
    Baryonic circular speed: v_bar^2 = v_gas^2 + v_disk^2 + v_bulge^2.

    Returns v_bar in km/s (non-negative by construction from squares).
    """
    v2 = (
        np.asarray(v_gas_kms, dtype=float) ** 2
        + np.asarray(v_disk_kms, dtype=float) ** 2
        + np.asarray(v_bulge_kms, dtype=float) ** 2
    )
    if np.any(v2 < 0):
        raise ValueError("negative v_bar^2 from component squares")
    return np.sqrt(v2)


def compute_residual_velocity_squared(
    v_obs_kms: np.ndarray | float,
    v_bar_kms: np.ndarray | float,
) -> np.ndarray:
    """
    Δv^2 = v_obs^2 - v_bar^2 (km/s)^2.

    Negative values are retained (not clipped); callers report counts.
    """
    v_obs = np.asarray(v_obs_kms, dtype=float)
    v_bar = np.asarray(v_bar_kms, dtype=float)
    return v_obs**2 - v_bar**2


def compute_residual_acceleration(
    r_kpc: np.ndarray | float,
    v_obs_kms: np.ndarray | float,
    v_bar_kms: np.ndarray | float,
) -> np.ndarray:
    """
    Missing-acceleration proxy: (v_obs^2 - v_bar^2) / r in (km/s)^2 / kpc.

    Equivalent to residual_v2 / r; used before TDF K_tau mapping (Phase 3).
    """
    r = np.asarray(r_kpc, dtype=float)
    if np.any(r <= 0):
        raise ValueError("r_kpc must be positive for residual acceleration proxy")
    residual_v2 = compute_residual_velocity_squared(v_obs_kms, v_bar_kms)
    return residual_v2 / r


def count_negative_residual_v2(residual_v2: np.ndarray) -> int:
    """Number of radii where v_obs^2 < v_bar^2 (unclipped)."""
    return int(np.sum(np.asarray(residual_v2, dtype=float) < 0))


def summarize_negative_residuals(
    r_kpc: np.ndarray,
    residual_v2: np.ndarray,
) -> list[str]:
    """Human-readable lines for negative Δv^2 points."""
    r = np.asarray(r_kpc, dtype=float)
    rv2 = np.asarray(residual_v2, dtype=float)
    neg = rv2 < 0
    if not neg.any():
        return []
    lines = []
    for i in np.where(neg)[0]:
        lines.append(
            f"R={r[i]:.2f} kpc: residual_v2={rv2[i]:.1f} (km/s)^2 (v_bar > v_obs)"
        )
    return lines


def build_baryonic_profile(
    df: pd.DataFrame,
    *,
    recompute_v_bar: bool = True,
) -> pd.DataFrame:
    """Attach v_bar, residual_v2, and residual acceleration proxy to rotation table."""
    out = df.copy()
    if recompute_v_bar:
        out["v_bar_kms"] = compute_v_bar(
            out["v_gas_kms"], out["v_disk_kms"], out["v_bulge_kms"]
        )
    out["residual_v2_kms2"] = compute_residual_velocity_squared(
        out["v_obs_kms"], out["v_bar_kms"]
    )
    out["residual_accel_proxy_kms2_per_kpc"] = compute_residual_acceleration(
        out["r_kpc"], out["v_obs_kms"], out["v_bar_kms"]
    )
    return out
