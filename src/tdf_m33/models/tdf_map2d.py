"""Axisymmetric 2D disk-plane τ maps from radial TDF profiles (Phase 4A)."""

from __future__ import annotations

from typing import Literal

import numpy as np
from scipy.interpolate import RegularGridInterpolator

RadialExtrapolation = Literal["mask"]


def make_disk_plane_grid(
    x_extent_kpc: float,
    y_extent_kpc: float,
    n_pixels: int,
) -> tuple[np.ndarray, np.ndarray]:
    """Build a square disk-plane coordinate mesh in kpc.

    Grid spans [-extent, +extent] along each axis with ``n_pixels`` points per axis.
    """
    if x_extent_kpc <= 0 or y_extent_kpc <= 0:
        raise ValueError("grid extents must be positive")
    if n_pixels < 2:
        raise ValueError("n_pixels must be >= 2")

    x_1d = np.linspace(-x_extent_kpc, x_extent_kpc, n_pixels)
    y_1d = np.linspace(-y_extent_kpc, y_extent_kpc, n_pixels)
    x_grid, y_grid = np.meshgrid(x_1d, y_1d, indexing="xy")
    return x_grid, y_grid


def radial_interpolate_to_grid(
    r_kpc: np.ndarray,
    values_radial: np.ndarray,
    x_grid: np.ndarray,
    y_grid: np.ndarray,
    *,
    radial_extrapolation: RadialExtrapolation = "mask",
) -> np.ndarray:
    """Map a 1D radial field to a 2D disk plane via τ(x, y) = f(R), R = √(x² + y²).

    Values outside the radial sample range are set to NaN when
    ``radial_extrapolation='mask'`` (no silent extrapolation).
    """
    r = np.asarray(r_kpc, dtype=float)
    values = np.asarray(values_radial, dtype=float)
    if r.shape != values.shape:
        raise ValueError("r_kpc and values_radial must have the same shape")
    if r.size < 2:
        raise ValueError("radial profile requires at least two points")

    order = np.argsort(r)
    r_sorted = r[order]
    values_sorted = values[order]
    if np.any(np.diff(r_sorted) <= 0):
        raise ValueError("r_kpc must be strictly increasing after sorting")

    R = np.sqrt(x_grid.astype(float) ** 2 + y_grid.astype(float) ** 2)
    out = np.interp(R.ravel(), r_sorted, values_sorted, left=np.nan, right=np.nan)
    grid = out.reshape(R.shape)

    if radial_extrapolation == "mask":
        outside = (R < r_sorted[0]) | (R > r_sorted[-1])
        grid = grid.astype(float, copy=False)
        grid[outside] = np.nan
        invalid = ~np.isfinite(values_sorted)
        if invalid.any():
            # If radial samples contain NaN, mask the full annulus at those radii.
            for ri, vi in zip(r_sorted, values_sorted):
                if not np.isfinite(vi):
                    grid[np.isclose(R, ri)] = np.nan
    else:
        raise ValueError(f"unsupported radial_extrapolation: {radial_extrapolation!r}")

    return grid


def compute_azimuthal_average_from_map(
    x_grid: np.ndarray,
    y_grid: np.ndarray,
    field_map: np.ndarray,
    r_eval_kpc: np.ndarray,
    *,
    n_theta: int = 128,
) -> np.ndarray:
    """Azimuthally average a 2D field at the requested cylindrical radii.

    Samples ``n_theta`` points on each ring and interpolates the map (disk plane,
    kpc). This is more stable than pixel annuli when the grid spacing exceeds the
    radial sampling step (e.g. Corbelli radii at small R).
    """
    x_1d = x_grid[0, :]
    y_1d = y_grid[:, 0]
    interp = RegularGridInterpolator(
        (y_1d, x_1d),
        field_map.astype(float),
        bounds_error=False,
        fill_value=np.nan,
    )

    r_eval = np.asarray(r_eval_kpc, dtype=float)
    averages = np.full(r_eval.shape, np.nan, dtype=float)
    theta = np.linspace(0.0, 2.0 * np.pi, n_theta, endpoint=False)

    for i, r in enumerate(r_eval):
        if not np.isfinite(r) or r <= 0:
            continue
        x_ring = r * np.cos(theta)
        y_ring = r * np.sin(theta)
        pts = np.column_stack([y_ring, x_ring])
        ring_vals = interp(pts)
        valid = np.isfinite(ring_vals)
        if valid.any():
            averages[i] = float(np.nanmean(ring_vals[valid]))
    return averages


def compare_radial_profile_to_map_average(
    r_kpc: np.ndarray,
    tau_radial: np.ndarray,
    tau_azimuthal_avg: np.ndarray,
) -> dict[str, float | np.ndarray]:
    """Compare input radial τ against azimuthal averages from the 2D map."""
    r = np.asarray(r_kpc, dtype=float)
    tau_in = np.asarray(tau_radial, dtype=float)
    tau_avg = np.asarray(tau_azimuthal_avg, dtype=float)

    valid = np.isfinite(tau_in) & np.isfinite(tau_avg)
    if not valid.any():
        return {
            "r_kpc": r,
            "tau_radial": tau_in,
            "tau_azimuthal_avg": tau_avg,
            "abs_error": np.full_like(r, np.nan),
            "max_abs_error": np.nan,
            "rmse_radial_consistency": np.nan,
            "n_compared": 0,
        }

    err = tau_avg[valid] - tau_in[valid]
    return {
        "r_kpc": r,
        "tau_radial": tau_in,
        "tau_azimuthal_avg": tau_avg,
        "abs_error": np.abs(tau_avg - tau_in),
        "max_abs_error": float(np.nanmax(np.abs(err))),
        "rmse_radial_consistency": float(np.sqrt(np.mean(err**2))),
        "n_compared": int(valid.sum()),
    }
