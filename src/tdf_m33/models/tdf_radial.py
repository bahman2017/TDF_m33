"""TDF radial τ-gradient and profile reconstruction (Phase 3A direct pointwise)."""

from __future__ import annotations

import numpy as np
from scipy.integrate import cumulative_trapezoid

_R_EPS = 1.0e-12
_DELTA_V2_EPS = 1.0e-6


def validate_k_tau(k_tau: float) -> float:
    """Require positive coupling constant (project-unit normalization in Phase 3A)."""
    k = float(k_tau)
    if k <= 0:
        raise ValueError(f"k_tau must be positive; got {k_tau}")
    return k


def validate_radius_grid(r_kpc: np.ndarray | float) -> np.ndarray:
    """Require strictly positive, strictly increasing radii [kpc]."""
    r = np.asarray(r_kpc, dtype=float)
    if r.ndim != 1:
        raise ValueError("r_kpc must be a 1D array")
    if np.any(r <= 0):
        raise ValueError("all radii must be positive")
    if np.any(np.diff(r) <= 0):
        raise ValueError("r_kpc must be strictly increasing")
    return r


def delta_v2_sign_flags(delta_v2_kms2: np.ndarray) -> np.ndarray:
    """Classify Δv² sign without clipping."""
    dv2 = np.asarray(delta_v2_kms2, dtype=float)
    return np.where(
        dv2 > _DELTA_V2_EPS,
        "positive",
        np.where(dv2 < -_DELTA_V2_EPS, "negative", "zero"),
    )


def compute_tau_gradient(
    r_kpc: np.ndarray | float,
    delta_v2_kms2: np.ndarray | float,
    k_tau: float,
) -> np.ndarray:
    """
    Pointwise τ-gradient: dτ/dr = Δv² / (r K_τ).

    Δv² is not clipped; negative values are preserved.
    """
    r = validate_radius_grid(r_kpc)
    k = validate_k_tau(k_tau)
    dv2 = np.asarray(delta_v2_kms2, dtype=float)
    if dv2.shape != r.shape:
        raise ValueError("delta_v2_kms2 must match r_kpc shape")
    return dv2 / (r * k)


def compute_v_tau_squared_from_gradient(
    r_kpc: np.ndarray | float,
    tau_gradient: np.ndarray | float,
    k_tau: float,
) -> np.ndarray:
    """v_τ² = r K_τ dτ/dr (identity check against Δv²)."""
    r = validate_radius_grid(r_kpc)
    k = validate_k_tau(k_tau)
    grad = np.asarray(tau_gradient, dtype=float)
    if grad.shape != r.shape:
        raise ValueError("tau_gradient must match r_kpc shape")
    return r * k * grad


def integrate_tau_profile(
    r_kpc: np.ndarray | float,
    tau_gradient: np.ndarray | float,
    tau0: float = 0.0,
) -> np.ndarray:
    """
    Cumulative trapezoidal integration of dτ/dr.

    τ(r_min) = tau0 by construction. τ has an arbitrary additive offset; only
    gradients and differences derived from dτ/dr are physically anchored in Phase 3A.
    """
    r = validate_radius_grid(r_kpc)
    grad = np.asarray(tau_gradient, dtype=float)
    if grad.shape != r.shape:
        raise ValueError("tau_gradient must match r_kpc shape")
    # ∫_{r_0}^{r_i} (dτ/dr) dr; first point equals tau0
    integral = cumulative_trapezoid(grad, r, initial=0.0)
    return float(tau0) + integral


def count_gradient_spikes(
    r_kpc: np.ndarray,
    delta_v2_kms2: np.ndarray,
    spike_threshold_factor: float = 3.0,
    min_threshold: float = 1.0e3,
) -> tuple[int, np.ndarray]:
    """
    Heuristic spike count on |d(Δv²)/dr| (same logic as Phase 2C readiness).
    """
    r = validate_radius_grid(r_kpc)
    dv2 = np.asarray(delta_v2_kms2, dtype=float)
    d1 = np.gradient(dv2, r)
    abs_d1 = np.abs(d1)
    med = float(np.nanmedian(abs_d1)) if np.any(np.isfinite(abs_d1)) else 0.0
    thresh = max(spike_threshold_factor * med, min_threshold) if med > 0 else min_threshold
    mask = abs_d1 > thresh
    return int(np.sum(mask)), mask
