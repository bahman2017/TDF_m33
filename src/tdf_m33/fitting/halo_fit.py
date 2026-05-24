"""NFW and Burkert halo fits on the M33 rotation curve (Phase 2B)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

import numpy as np
import pandas as pd
from scipy.optimize import least_squares

from tdf_m33.fitting.metrics import (
    FitMetrics,
    aic_from_chi_square,
    bic_from_chi_square,
    chi_square,
    fit_metrics_to_row,
    rmse,
)
from tdf_m33.models.baryonic import (
    build_baryonic_profile,
    compute_residual_velocity_squared,
)
from tdf_m33.models.halo import (
    burkert_velocity,
    combined_velocity,
    nfw_velocity,
)

HaloKind = Literal["nfw", "burkert"]

# Corbelli et al. 2014 sanity context (not acceptance criteria)
CORBELLI2014_NFW_C_REF = 9.5
CORBELLI2014_NFW_C_ERR = 1.5
CORBELLI2014_NFW_MH_REF_MSUN = 4.3e11
CORBELLI2014_NFW_MH_ERR_MSUN = 1.0e11
CORBELLI2014_BURKERT_R0_REF_KPC = 7.5
CORBELLI2014_BURKERT_RHO0_REF_MSUN_PC3 = 0.018
MSUN_PC3_TO_MSUN_KPC3 = 1.0e6


@dataclass(frozen=True)
class FitRadiusMask:
    """Corbelli 2014 dynamical fitting range."""

    min_kpc: float = 0.4
    max_kpc: float = 23.0

    def mask(self, r_kpc: np.ndarray) -> np.ndarray:
        r = np.asarray(r_kpc, dtype=float)
        return (r >= self.min_kpc) & (r <= self.max_kpc)


@dataclass(frozen=True)
class HaloFitBounds:
    """Log-space bounds for halo density and scale radius."""

    log10_rho_min: float = -3.0
    log10_rho_max: float = 15.0
    log10_scale_radius_min: float = -1.0  # 0.1 kpc
    log10_scale_radius_max: float = 2.301  # ~200 kpc

    def as_bounds(self, kind: HaloKind) -> tuple[np.ndarray, np.ndarray]:
        lo = np.array([self.log10_rho_min, self.log10_scale_radius_min])
        hi = np.array([self.log10_rho_max, self.log10_scale_radius_max])
        return lo, hi


@dataclass(frozen=True)
class HaloFitResult:
    """Best-fit halo parameters and velocities on full radius grid."""

    kind: HaloKind
    log10_rho: float
    log10_scale_kpc: float
    rho: float
    scale_kpc: float
    v_halo_kms: np.ndarray
    v_model_kms: np.ndarray
    success: bool
    cost: float
    message: str
    n_iterations: int

    @property
    def parameter_count(self) -> int:
        return 2


@dataclass(frozen=True)
class ModelComparisonRow:
    """Metrics row for model comparison table."""

    metrics: FitMetrics
    n_fit_points: int
    dof: int
    fit_r_min_kpc: float
    fit_r_max_kpc: float
    n_rows_total: int


def fit_radius_mask(
    r_kpc: np.ndarray,
    fit_min_radius_kpc: float = 0.4,
    fit_max_radius_kpc: float = 23.0,
) -> np.ndarray:
    return FitRadiusMask(fit_min_radius_kpc, fit_max_radius_kpc).mask(r_kpc)


def _halo_v(
    kind: HaloKind,
    r: np.ndarray,
    log10_rho: float,
    log10_scale: float,
) -> np.ndarray:
    rho = 10.0**log10_rho
    scale = 10.0**log10_scale
    if kind == "nfw":
        return nfw_velocity(r, rho, scale)
    return burkert_velocity(r, rho, scale)


def _residuals_velocity(
    log_params: np.ndarray,
    r: np.ndarray,
    v_obs: np.ndarray,
    v_err: np.ndarray,
    v_bar: np.ndarray,
    kind: HaloKind,
) -> np.ndarray:
    v_halo = _halo_v(kind, r, log_params[0], log_params[1])
    v_model = combined_velocity(r, v_bar, v_halo)
    return (v_obs - v_model) / v_err


def fit_halo(
    r_kpc: np.ndarray,
    v_obs_kms: np.ndarray,
    v_err_kms: np.ndarray,
    v_bar_kms: np.ndarray,
    kind: HaloKind,
    *,
    fit_mask: np.ndarray,
    bounds: HaloFitBounds | None = None,
    p0_log: tuple[float, float] | None = None,
) -> HaloFitResult:
    """Weighted least-squares fit of v_model² = v_bar² + v_halo² in velocity space."""
    bounds = bounds or HaloFitBounds()
    r = np.asarray(r_kpc, dtype=float)
    v_obs = np.asarray(v_obs_kms, dtype=float)
    v_err = np.asarray(v_err_kms, dtype=float)
    v_bar = np.asarray(v_bar_kms, dtype=float)

    m = fit_mask
    if m.sum() < 3:
        raise ValueError("need at least 3 fit points in mask")

    if p0_log is None:
        p0_log = (8.0, 0.0) if kind == "nfw" else (7.0, 0.5)

    lo, hi = bounds.as_bounds(kind)

    def fun(p: np.ndarray) -> np.ndarray:
        return _residuals_velocity(p, r[m], v_obs[m], v_err[m], v_bar[m], kind)

    result = least_squares(fun, np.array(p0_log), bounds=(lo, hi))

    log10_rho, log10_scale = float(result.x[0]), float(result.x[1])
    rho = 10.0**log10_rho
    scale = 10.0**log10_scale
    v_halo = _halo_v(kind, r, log10_rho, log10_scale)
    v_model = combined_velocity(r, v_bar, v_halo)

    return HaloFitResult(
        kind=kind,
        log10_rho=log10_rho,
        log10_scale_kpc=log10_scale,
        rho=rho,
        scale_kpc=scale,
        v_halo_kms=v_halo,
        v_model_kms=v_model,
        success=result.success,
        cost=float(result.cost),
        message=result.message,
        n_iterations=int(result.nfev),
    )


def comparison_metrics(
    model_name: str,
    v_obs_kms: np.ndarray,
    v_model_kms: np.ndarray,
    v_err_kms: np.ndarray,
    parameter_count: int,
    *,
    fit_mask: np.ndarray,
    fit_r_min_kpc: float,
    fit_r_max_kpc: float,
    n_rows_total: int,
    residual_v2_kms2: np.ndarray | None = None,
    notes: str = "",
) -> ModelComparisonRow:
    """Compute metrics on fit-masked points only."""
    m = fit_mask
    n_fit = int(m.sum())
    obs = v_obs_kms[m]
    mod = v_model_kms[m]
    err = v_err_kms[m]
    chi2 = chi_square(obs, mod, err)
    dof = n_fit - parameter_count - 1
    if dof <= 0:
        raise ValueError(f"invalid dof for n_fit={n_fit}, k={parameter_count}")

    if residual_v2_kms2 is None:
        rv2 = obs**2 - mod**2
    else:
        rv2 = residual_v2_kms2[m]

    metrics = FitMetrics(
        model_name=model_name,
        n_points=n_fit,
        rmse_kms=rmse(obs, mod),
        chi_square=chi2,
        reduced_chi_square=chi2 / dof,
        parameter_count=parameter_count,
        aic=aic_from_chi_square(chi2, parameter_count),
        bic=bic_from_chi_square(chi2, parameter_count, n_fit),
        n_negative_residual_v2=int(np.sum(rv2 < 0)),
        notes=notes,
    )
    return ModelComparisonRow(
        metrics=metrics,
        n_fit_points=n_fit,
        dof=dof,
        fit_r_min_kpc=fit_r_min_kpc,
        fit_r_max_kpc=fit_r_max_kpc,
        n_rows_total=n_rows_total,
    )


def baryonic_comparison_under_mask(
    profile: pd.DataFrame,
    fit_mask: np.ndarray,
    fit_r_min_kpc: float,
    fit_r_max_kpc: float,
    notes: str,
) -> ModelComparisonRow:
    rv2 = compute_residual_velocity_squared(
        profile["v_obs_kms"], profile["v_bar_kms"]
    )
    return comparison_metrics(
        "baryonic_only",
        profile["v_obs_kms"].to_numpy(),
        profile["v_bar_kms"].to_numpy(),
        profile["v_err_kms"].to_numpy(),
        parameter_count=0,
        fit_mask=fit_mask,
        fit_r_min_kpc=fit_r_min_kpc,
        fit_r_max_kpc=fit_r_max_kpc,
        n_rows_total=len(profile),
        residual_v2_kms2=rv2,
        notes=notes,
    )


def corbelli_reference_notes(kind: HaloKind, fit: HaloFitResult) -> str:
    """Sanity context vs Corbelli 2014 published halo values (not a pass/fail gate)."""
    if kind == "nfw":
        return (
            f"Corbelli 2014 ref (sanity only): c≈{CORBELLI2014_NFW_C_REF}±"
            f"{CORBELLI2014_NFW_C_ERR}, Mh≈{CORBELLI2014_NFW_MH_REF_MSUN:.2e}±"
            f"{CORBELLI2014_NFW_MH_ERR_MSUN:.1e} M_sun; fitted rho_s={fit.rho:.3e} "
            f"M_sun/kpc^3, r_s={fit.scale_kpc:.3f} kpc. D1 baryonic caveat applies."
        )
    rho0_pc3 = fit.rho / MSUN_PC3_TO_MSUN_KPC3
    return (
        f"Corbelli 2014 BVI ref (sanity only): r0≈{CORBELLI2014_BURKERT_R0_REF_KPC} kpc, "
        f"rho0≈{CORBELLI2014_BURKERT_RHO0_REF_MSUN_PC3} M_sun/pc^3; fitted rho0={rho0_pc3:.4f} "
        f"M_sun/pc^3, r0={fit.scale_kpc:.3f} kpc. D1 baryonic caveat applies."
    )


def halo_fit_to_parameter_row(fit: HaloFitResult, notes: str) -> dict[str, object]:
    if fit.kind == "nfw":
        return {
            "model_name": "nfw",
            "log10_rho_s_msun_kpc3": fit.log10_rho,
            "log10_r_s_kpc": fit.log10_scale_kpc,
            "rho_s_msun_kpc3": fit.rho,
            "r_s_kpc": fit.scale_kpc,
            "log10_rho0_msun_kpc3": np.nan,
            "log10_r0_kpc": np.nan,
            "rho0_msun_kpc3": np.nan,
            "r0_kpc": np.nan,
            "fit_success": fit.success,
            "fit_cost": fit.cost,
            "fit_message": fit.message,
            "n_iterations": fit.n_iterations,
            "parameter_count": fit.parameter_count,
            "reference_notes": notes,
        }
    return {
        "model_name": "burkert",
        "log10_rho_s_msun_kpc3": np.nan,
        "log10_r_s_kpc": np.nan,
        "rho_s_msun_kpc3": np.nan,
        "r_s_kpc": np.nan,
        "log10_rho0_msun_kpc3": fit.log10_rho,
        "log10_r0_kpc": fit.log10_scale_kpc,
        "rho0_msun_kpc3": fit.rho,
        "r0_kpc": fit.scale_kpc,
        "fit_success": fit.success,
        "fit_cost": fit.cost,
        "fit_message": fit.message,
        "n_iterations": fit.n_iterations,
        "parameter_count": fit.parameter_count,
        "reference_notes": notes,
    }


def comparison_row_to_dict(row: ModelComparisonRow) -> dict[str, object]:
    d = fit_metrics_to_row(row.metrics)
    d.update(
        {
            "n_fit_points": row.n_fit_points,
            "dof": row.dof,
            "fit_r_min_kpc": row.fit_r_min_kpc,
            "fit_r_max_kpc": row.fit_r_max_kpc,
            "n_rows_total": row.n_rows_total,
        }
    )
    return d


def prepare_phase2b_profile(
    dataset_df: pd.DataFrame,
    nfw: HaloFitResult,
    burkert: HaloFitResult,
    fit_mask: np.ndarray,
) -> pd.DataFrame:
    """Full 58-row profile with halo components and residuals."""
    base = build_baryonic_profile(dataset_df)
    out = pd.DataFrame(
        {
            "galaxy_id": base["galaxy_id"],
            "r_kpc": base["r_kpc"],
            "v_obs_kms": base["v_obs_kms"],
            "v_err_kms": base["v_err_kms"],
            "v_bar_kms": base["v_bar_kms"],
            "v_nfw_halo_kms": nfw.v_halo_kms,
            "v_burkert_halo_kms": burkert.v_halo_kms,
            "v_model_nfw_kms": nfw.v_model_kms,
            "v_model_burkert_kms": burkert.v_model_kms,
            "residual_baryonic_kms": base["v_obs_kms"] - base["v_bar_kms"],
            "residual_nfw_kms": base["v_obs_kms"] - nfw.v_model_kms,
            "residual_burkert_kms": base["v_obs_kms"] - burkert.v_model_kms,
            "fit_mask": fit_mask,
            "source_id": base["source_id"],
            "data_quality_flag": base["data_quality_flag"],
            "notes": base["notes"],
        }
    )
    return out.sort_values("r_kpc").reset_index(drop=True)
