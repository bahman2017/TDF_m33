"""Low-parameter knot τ-gradient models for Phase 3C comparison."""

from __future__ import annotations

import numpy as np

from tdf_m33.models.tdf_radial import validate_k_tau, validate_radius_grid

_VTAU2_EPS = 1.0e-6


def knot_radii_quantile_fit_mask(
    r_kpc: np.ndarray,
    fit_mask: np.ndarray,
    knot_count: int,
    fit_min_radius_kpc: float,
    fit_max_radius_kpc: float,
) -> np.ndarray:
    """
    Place ``knot_count`` knot radii at quantiles of masked radii.

    Knots lie within the Corbelli fit mask range and bracket the masked sample.
    """
    if knot_count < 2:
        raise ValueError("knot_count must be at least 2")
    r = np.asarray(r_kpc, dtype=float)
    m = np.asarray(fit_mask, dtype=bool)
    r_fit = r[m]
    if r_fit.size < knot_count:
        raise ValueError(
            f"need at least {knot_count} masked radii; got {r_fit.size}"
        )
    r_lo = max(float(r_fit.min()), fit_min_radius_kpc)
    r_hi = min(float(r_fit.max()), fit_max_radius_kpc)
    q = np.linspace(0.0, 1.0, knot_count)
    knots = np.quantile(r_fit, q)
    knots[0] = r_lo
    knots[-1] = r_hi
    knots = np.unique(knots)
    if knots.size < knot_count:
        knots = np.linspace(r_lo, r_hi, knot_count)
    validate_radius_grid(knots)
    if knots[0] < fit_min_radius_kpc - 1e-9 or knots[-1] > fit_max_radius_kpc + 1e-9:
        raise ValueError("knot radii must lie within fit mask bounds")
    return knots


def knot_interpolated_tau_gradient(
    r_kpc: np.ndarray | float,
    knot_radii_kpc: np.ndarray,
    knot_values: np.ndarray,
) -> np.ndarray:
    """
    Piecewise-linear dτ/dr from knot values (uneven spacing in r).

    Extrapolation at r < min(knot) or r > max(knot) uses endpoint knot values.
    """
    r = validate_radius_grid(r_kpc)
    knots_r = validate_radius_grid(np.asarray(knot_radii_kpc, dtype=float))
    vals = np.asarray(knot_values, dtype=float)
    if vals.shape != knots_r.shape:
        raise ValueError("knot_values must match knot_radii_kpc length")
    return np.interp(r, knots_r, vals, left=vals[0], right=vals[-1])


def tau_velocity_squared_from_gradient(
    r_kpc: np.ndarray | float,
    tau_gradient: np.ndarray | float,
    k_tau: float,
) -> np.ndarray:
    """v_τ² = r K_τ dτ/dr (unclipped)."""
    from tdf_m33.models.tdf_radial import compute_v_tau_squared_from_gradient

    return compute_v_tau_squared_from_gradient(r_kpc, tau_gradient, k_tau)


def flag_negative_vtau_squared(v_tau_squared: np.ndarray) -> np.ndarray:
    """True where v_τ² < 0."""
    v2 = np.asarray(v_tau_squared, dtype=float)
    return v2 < -_VTAU2_EPS


def tdf_velocity_model(
    v_bar_kms: np.ndarray | float,
    r_kpc: np.ndarray | float,
    tau_gradient: np.ndarray | float,
    k_tau: float,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    TDF model speed and components.

    Returns (v_model_kms, v_tau_squared, negative_vtau2_flag).
    v_model = sqrt(v_bar² + v_τ²) where the sum is non-negative; NaN if negative sum.
    """
    r = validate_radius_grid(r_kpc)
    k = validate_k_tau(k_tau)
    v_bar = np.asarray(v_bar_kms, dtype=float)
    grad = np.asarray(tau_gradient, dtype=float)
    if v_bar.shape != r.shape or grad.shape != r.shape:
        raise ValueError("v_bar, tau_gradient, and r_kpc must have the same shape")

    v_tau2 = r * k * grad
    neg_flag = flag_negative_vtau_squared(v_tau2)
    sum_sq = v_bar**2 + v_tau2
    v_model = np.full_like(sum_sq, np.nan)
    ok = sum_sq >= 0
    v_model[ok] = np.sqrt(sum_sq[ok])
    return v_model, v_tau2, neg_flag
