"""TDF radial τ-gradient smoothing / regularization (Phase 3B-A)."""

from __future__ import annotations

from typing import Literal

import numpy as np
from scipy.interpolate import UnivariateSpline

from tdf_m33.models.tdf_radial import validate_radius_grid

SmoothingMethod = Literal["gaussian_radius_smoothing", "smoothing_spline"]

_GRADIENT_SPIKE_FACTOR = 3.0
_GRADIENT_SPIKE_MIN = 1.0e3
_VTAU2_EPS = 1.0e-6


def gaussian_radius_smoothing(
    r_kpc: np.ndarray | float,
    tau_gradient: np.ndarray | float,
    sigma_kpc: float,
) -> np.ndarray:
    """
    Gaussian kernel smoothing over physical radius [kpc].

    Handles uneven radial spacing via distance-weighted average at each point.
    """
    r = validate_radius_grid(r_kpc)
    y = np.asarray(tau_gradient, dtype=float)
    if y.shape != r.shape:
        raise ValueError("tau_gradient must match r_kpc shape")
    sigma = float(sigma_kpc)
    if sigma <= 0:
        raise ValueError(f"gaussian_sigma_kpc must be positive; got {sigma_kpc}")

    out = np.empty_like(y)
    for i, ri in enumerate(r):
        w = np.exp(-0.5 * ((r - ri) / sigma) ** 2)
        wsum = w.sum()
        out[i] = float(np.dot(w, y) / wsum) if wsum > 0 else y[i]
    return out


def _default_spline_smoothing_factor(y: np.ndarray) -> float:
    """Documented fallback when config spline_smoothing_factor is null."""
    n = len(y)
    var = float(np.var(y))
    return max(n * var * 100.0, 1.0)


def smoothing_spline(
    r_kpc: np.ndarray | float,
    tau_gradient: np.ndarray | float,
    smoothing_factor: float | None,
) -> np.ndarray:
    """
    Smoothing spline of τ-gradient vs radius (scipy UnivariateSpline).

    ``smoothing_factor`` is the spline ``s`` parameter (not auto-tuned to data fit).
    """
    r = validate_radius_grid(r_kpc)
    y = np.asarray(tau_gradient, dtype=float)
    if y.shape != r.shape:
        raise ValueError("tau_gradient must match r_kpc shape")
    if len(r) < 4:
        raise ValueError("smoothing_spline requires at least 4 radius points")

    s = float(smoothing_factor) if smoothing_factor is not None else _default_spline_smoothing_factor(y)
    if s < 0:
        raise ValueError(f"spline smoothing_factor must be non-negative; got {s}")

    k = min(3, len(r) - 1)
    spl = UnivariateSpline(r, y, s=s, k=k)
    return spl(r)


def smooth_tau_gradient(
    r_kpc: np.ndarray,
    tau_gradient_raw: np.ndarray,
    method: SmoothingMethod,
    *,
    gaussian_sigma_kpc: float = 0.75,
    spline_smoothing_factor: float | None = None,
) -> np.ndarray:
    """Dispatch to configured smoothing method."""
    if method == "gaussian_radius_smoothing":
        return gaussian_radius_smoothing(r_kpc, tau_gradient_raw, gaussian_sigma_kpc)
    if method == "smoothing_spline":
        return smoothing_spline(r_kpc, tau_gradient_raw, spline_smoothing_factor)
    raise ValueError(f"Unknown smoothing method: {method}")


def gradient_smoothness_metric(r_kpc: np.ndarray, tau_gradient: np.ndarray) -> float:
    """Median |d²τ/dr²| — lower is smoother."""
    r = validate_radius_grid(r_kpc)
    g = np.asarray(tau_gradient, dtype=float)
    d1 = np.gradient(g, r)
    d2 = np.gradient(d1, r)
    return float(np.nanmedian(np.abs(d2)))


def count_tau_gradient_spikes(
    r_kpc: np.ndarray,
    tau_gradient: np.ndarray,
    spike_threshold_factor: float = _GRADIENT_SPIKE_FACTOR,
    min_threshold: float = _GRADIENT_SPIKE_MIN,
) -> tuple[int, np.ndarray]:
    """Heuristic spike count on |d(dτ/dr)/dr|."""
    r = validate_radius_grid(r_kpc)
    g = np.asarray(tau_gradient, dtype=float)
    d1 = np.gradient(g, r)
    abs_d1 = np.abs(d1)
    med = float(np.nanmedian(abs_d1)) if np.any(np.isfinite(abs_d1)) else 0.0
    thresh = max(spike_threshold_factor * med, min_threshold) if med > 0 else min_threshold
    mask = abs_d1 > thresh
    return int(np.sum(mask)), mask


def flag_negative_vtau_squared(v_tau_squared: np.ndarray) -> np.ndarray:
    """True where r K_τ dτ/dr < 0 (not clipped)."""
    v2 = np.asarray(v_tau_squared, dtype=float)
    return v2 < -_VTAU2_EPS
