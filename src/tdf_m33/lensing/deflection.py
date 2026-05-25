"""Deflection-proxy maps from sky-plane τ (Phase 5A)."""

from __future__ import annotations

from typing import Any

import numpy as np

UNITS_NORMALIZED_PROXY = "normalized_proxy"


def _spacing_1d(coord_1d: np.ndarray) -> float:
    vals = np.unique(np.sort(coord_1d[np.isfinite(coord_1d)]))
    diffs = np.diff(vals)
    positive = diffs[diffs > 0]
    if positive.size == 0:
        raise ValueError("cannot infer grid spacing from coordinates")
    return float(np.median(positive))


def _spacing_from_mesh(coord_2d: np.ndarray, *, axis: str) -> float:
    """Infer uniform grid spacing when mask leaves edge rows/columns empty.

    axis ``'x'``: spacing along columns (use first row with ≥3 finite x).
    axis ``'y'``: spacing along rows (use first column with ≥3 finite y).
    """
    grid = np.asarray(coord_2d, dtype=float)
    if axis == "x":
        for i in range(grid.shape[0]):
            if np.isfinite(grid[i, :]).sum() >= 3:
                return _spacing_1d(grid[i, :])
    elif axis == "y":
        for j in range(grid.shape[1]):
            if np.isfinite(grid[:, j]).sum() >= 3:
                return _spacing_1d(grid[:, j])
    else:
        raise ValueError(f"axis must be 'x' or 'y', got {axis!r}")
    raise ValueError("cannot infer grid spacing from coordinates")


def compute_tau_gradients_sky(
    tau_map: np.ndarray,
    x_sky_kpc: np.ndarray,
    y_sky_kpc: np.ndarray,
) -> tuple[np.ndarray, np.ndarray]:
    """Compute ∂τ/∂x and ∂τ/∂y on the sky-plane grid (kpc⁻¹ × τ units).

    Uses ``numpy.gradient`` on the structured mesh; NaN τ values propagate to NaN
    gradients. No extrapolation outside the finite map support.
    """
    tau = np.asarray(tau_map, dtype=float)
    x = np.asarray(x_sky_kpc, dtype=float)
    y = np.asarray(y_sky_kpc, dtype=float)
    if tau.shape != x.shape or tau.shape != y.shape:
        raise ValueError("tau_map, x_sky_kpc, and y_sky_kpc must share shape")

    dx = _spacing_from_mesh(x, axis="x")
    dy = _spacing_from_mesh(y, axis="y")
    grad_y, grad_x = np.gradient(tau, dy, dx, edge_order=1)
    invalid = ~np.isfinite(tau)
    if invalid.any():
        grad_x = grad_x.astype(float, copy=False)
        grad_y = grad_y.astype(float, copy=False)
        grad_x[invalid] = np.nan
        grad_y[invalid] = np.nan
    return grad_x, grad_y


def compute_deflection_proxy(
    grad_tau_x: np.ndarray,
    grad_tau_y: np.ndarray,
    *,
    alpha_tau_scale: float = 1.0,
) -> tuple[np.ndarray, np.ndarray]:
    """Normalized deflection proxy: α_x = -scale ∂τ/∂x, α_y = -scale ∂τ/∂y."""
    scale = float(alpha_tau_scale)
    alpha_x = -scale * np.asarray(grad_tau_x, dtype=float)
    alpha_y = -scale * np.asarray(grad_tau_y, dtype=float)
    return alpha_x, alpha_y


def compute_deflection_magnitude(
    alpha_x: np.ndarray,
    alpha_y: np.ndarray,
) -> np.ndarray:
    """|α| from proxy components (normalized_proxy units)."""
    return np.hypot(np.asarray(alpha_x, dtype=float), np.asarray(alpha_y, dtype=float))


def compute_convergence_proxy(
    alpha_x: np.ndarray,
    alpha_y: np.ndarray,
    x_sky_kpc: np.ndarray,
    y_sky_kpc: np.ndarray,
) -> tuple[np.ndarray, dict[str, Any]]:
    """Thin-lens-style convergence proxy κ ≈ ½ (∂α_x/∂x + ∂α_y/∂y).

    Returns (kappa_map, diagnostics). Unstable or unsupported pixels are NaN.
    """
    alpha_x = np.asarray(alpha_x, dtype=float)
    alpha_y = np.asarray(alpha_y, dtype=float)
    x = np.asarray(x_sky_kpc, dtype=float)
    y = np.asarray(y_sky_kpc, dtype=float)
    dx = _spacing_from_mesh(x, axis="x")
    dy = _spacing_from_mesh(y, axis="y")

    dalpha_y_dx, dalpha_x_dx = np.gradient(alpha_x, dy, dx, edge_order=1)
    dalpha_y_dy, dalpha_x_dy = np.gradient(alpha_y, dy, dx, edge_order=1)
    kappa = 0.5 * (dalpha_x_dx + dalpha_y_dy)

    finite = np.isfinite(kappa)
    valid_frac = float(finite.mean()) if kappa.size else 0.0
    if valid_frac < 0.05:
        kappa[:] = np.nan
        return kappa, {
            "convergence_computed": False,
            "convergence_stable": False,
            "reason": "insufficient finite convergence pixels",
            "valid_fraction": valid_frac,
        }

    vals = kappa[finite]
    median_abs = float(np.median(np.abs(vals)))
    max_abs = float(np.max(np.abs(vals)))
    unstable = max_abs > 100.0 * max(median_abs, 1.0e-12)
    diagnostics = {
        "convergence_computed": True,
        "convergence_stable": not unstable,
        "valid_fraction": valid_frac,
        "median_abs_kappa_proxy": median_abs,
        "max_abs_kappa_proxy": max_abs,
        "reason": (
            "edge gradients amplify second derivatives; interpret with caution"
            if unstable
            else "ok"
        ),
    }
    if unstable:
        # Mask extreme outliers (typically grid edges); keep moderate interior
        cap = 50.0 * median_abs
        kappa[np.abs(kappa) > cap] = np.nan
    return kappa, diagnostics


def deflection_summary_stats(
    alpha_magnitude: np.ndarray,
    *,
    units: str = UNITS_NORMALIZED_PROXY,
) -> dict[str, float | str | int]:
    """Summary statistics over finite deflection-proxy pixels."""
    mag = np.asarray(alpha_magnitude, dtype=float)
    finite = np.isfinite(mag)
    n_total = int(mag.size)
    n_finite = int(finite.sum())
    if n_finite == 0:
        return {
            "units": units,
            "n_pixels_total": n_total,
            "n_pixels_finite": 0,
            "fraction_finite": 0.0,
            "alpha_magnitude_max": np.nan,
            "alpha_magnitude_median": np.nan,
            "alpha_magnitude_mean": np.nan,
        }
    vals = mag[finite]
    return {
        "units": units,
        "n_pixels_total": n_total,
        "n_pixels_finite": n_finite,
        "fraction_finite": float(n_finite / n_total),
        "alpha_magnitude_max": float(np.max(vals)),
        "alpha_magnitude_median": float(np.median(vals)),
        "alpha_magnitude_mean": float(np.mean(vals)),
    }
