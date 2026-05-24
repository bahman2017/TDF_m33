"""Goodness-of-fit metrics for rotation-curve models (Phase 2+)."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class FitMetrics:
    """Summary metrics for a rotation-curve model."""

    model_name: str
    n_points: int
    rmse_kms: float
    chi_square: float
    reduced_chi_square: float
    parameter_count: int
    aic: float
    bic: float
    n_negative_residual_v2: int
    notes: str


def rmse(v_obs_kms: np.ndarray, v_model_kms: np.ndarray) -> float:
    """Root mean square error in km/s."""
    obs = np.asarray(v_obs_kms, dtype=float)
    mod = np.asarray(v_model_kms, dtype=float)
    return float(np.sqrt(np.mean((obs - mod) ** 2)))


def chi_square(
    v_obs_kms: np.ndarray,
    v_model_kms: np.ndarray,
    v_err_kms: np.ndarray,
) -> float:
    """χ² = Σ ((v_obs - v_model) / σ_v)² with σ_v > 0."""
    obs = np.asarray(v_obs_kms, dtype=float)
    mod = np.asarray(v_model_kms, dtype=float)
    err = np.asarray(v_err_kms, dtype=float)
    if np.any(err <= 0):
        raise ValueError("v_err_kms must be positive for chi-square")
    resid = obs - mod
    return float(np.sum((resid / err) ** 2))


def reduced_chi_square(chi2: float, n_points: int, parameter_count: int) -> float:
    """
    Reduced χ² = χ² / dof with dof = n - k.

    For k=0 (fixed model), dof = n - 1 (no intercept fitted).
    """
    dof = n_points - parameter_count - 1
    if dof <= 0:
        raise ValueError(
            f"non-positive degrees of freedom: n={n_points}, k={parameter_count}"
        )
    return chi2 / dof


def aic_from_chi_square(chi2: float, parameter_count: int) -> float:
    """
    AIC ≈ χ² + 2k for Gaussian errors with χ² = -2 ln L (up to constant).

    For k=0 this equals χ²; documented for comparison with future halo fits.
    """
    return chi2 + 2.0 * parameter_count


def bic_from_chi_square(chi2: float, parameter_count: int, n_points: int) -> float:
    """BIC ≈ χ² + k ln(n) under the same Gaussian χ² convention."""
    return chi2 + parameter_count * np.log(n_points)


def baryonic_only_metrics(
    v_obs_kms: np.ndarray,
    v_bar_kms: np.ndarray,
    v_err_kms: np.ndarray,
    residual_v2_kms2: np.ndarray,
    *,
    model_name: str = "baryonic_only",
    parameter_count: int = 0,
    notes: str = "",
) -> FitMetrics:
    """
    Metrics for fixed baryonic model (no fitted parameters).

    parameter_count=0: components fixed from Phase 1D-D1 derivation, not fit here.
    """
    n = len(v_obs_kms)
    chi2 = chi_square(v_obs_kms, v_bar_kms, v_err_kms)
    return FitMetrics(
        model_name=model_name,
        n_points=n,
        rmse_kms=rmse(v_obs_kms, v_bar_kms),
        chi_square=chi2,
        reduced_chi_square=reduced_chi_square(chi2, n, parameter_count),
        parameter_count=parameter_count,
        aic=aic_from_chi_square(chi2, parameter_count),
        bic=bic_from_chi_square(chi2, parameter_count, n),
        n_negative_residual_v2=int(np.sum(np.asarray(residual_v2_kms2, dtype=float) < 0)),
        notes=notes,
    )


def fit_metrics_to_row(metrics: FitMetrics) -> dict[str, object]:
    """Single-row dict for CSV export."""
    return {
        "model_name": metrics.model_name,
        "n_points": metrics.n_points,
        "rmse_kms": metrics.rmse_kms,
        "chi_square": metrics.chi_square,
        "reduced_chi_square": metrics.reduced_chi_square,
        "parameter_count": metrics.parameter_count,
        "aic": metrics.aic,
        "bic": metrics.bic,
        "n_negative_residual_v2": metrics.n_negative_residual_v2,
        "notes": metrics.notes,
    }
