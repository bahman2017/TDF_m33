"""Phase 3C: low-parameter knot τ-gradient fits and model comparison."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import yaml
from scipy.optimize import least_squares

from tdf_m33.data.m33_dataset import load_m33_rotation_dataset
from tdf_m33.fitting.halo_fit import (
    FitRadiusMask,
    comparison_metrics,
    comparison_row_to_dict,
    fit_radius_mask,
)
from tdf_m33.models.baryonic import (
    build_baryonic_profile,
    compute_residual_velocity_squared,
)
from tdf_m33.models.tdf_lowparam import (
    knot_interpolated_tau_gradient,
    knot_radii_quantile_fit_mask,
    tdf_velocity_model,
)
from tdf_m33.models.tdf_radial import compute_tau_gradient, integrate_tau_profile

FIG_CAVEAT = (
    "Phase 3C: low-parameter TDF knot model (K_τ fixed). D1 baryonic PASS_WITH_CAVEAT. "
    "Not lensing; not a DM disproof. Burkert may be bound-limited."
)

TDF_NOTES_TEMPLATE = (
    "Low-parameter τ-gradient knot model (k={k} knot values fitted; K_τ={k_tau} fixed). "
    "Baryonic Δv² input only. D1-derived baryonic PASS_WITH_CAVEAT. "
    "Not a lensing test; no 2D τ map. Phase 3A/3B are reconstruction/regularization, "
    "not fair AIC/BIC competitors."
)


@dataclass(frozen=True)
class LowParamFitResult:
    """Best-fit knot τ-gradient model."""

    model_name: str
    knot_count: int
    knot_radii_kpc: np.ndarray
    knot_values: np.ndarray
    k_tau: float
    tau_gradient: np.ndarray
    tau_profile: np.ndarray
    v_model_kms: np.ndarray
    v_tau_squared: np.ndarray
    negative_vtau2_flag: np.ndarray
    success: bool
    cost: float
    message: str
    n_iterations: int

    @property
    def parameter_count(self) -> int:
        return self.knot_count


def load_phase3c_config(config_path: Path) -> dict[str, Any]:
    with config_path.open() as f:
        cfg = yaml.safe_load(f)
    tdf = cfg.get("tdf", {})
    lp = tdf.get("low_parameter_model", {})
    return {
        "k_tau": float(lp.get("k_tau", tdf.get("k_tau", 1.0))),
        "tau0": float(tdf.get("tau0", 0.0)),
        "enabled": bool(lp.get("enabled", True)),
        "default_model": str(lp.get("default_model", "knot_tau_gradient")),
        "knot_count": int(lp.get("knot_count", 4)),
        "knot_strategy": str(lp.get("knot_strategy", "quantile_radius_fit_mask")),
        "enforce_nonnegative_vtau2": bool(lp.get("enforce_nonnegative_vtau2", True)),
        "fit_min_radius_kpc": float(lp.get("fit_min_radius_kpc", 0.4)),
        "fit_max_radius_kpc": float(lp.get("fit_max_radius_kpc", 23.0)),
        "compare_knot_counts": [int(k) for k in lp.get("compare_knot_counts", [3, 4, 5])],
        "figure_dpi": int(cfg.get("plotting", {}).get("figure_dpi", 150)),
        "gradient_upper_bound": 1.0e5,
    }


def _initial_knot_values(
    r: np.ndarray,
    knot_r: np.ndarray,
    v_obs: np.ndarray,
    v_bar: np.ndarray,
    k_tau: float,
    phase3a_path: Path | None,
) -> np.ndarray:
    """Starting knot dτ/dr from Phase 3A raw gradient or baryonic Δv²."""
    if phase3a_path is not None and phase3a_path.is_file():
        p3a = pd.read_csv(phase3a_path).sort_values("r_kpc")
        raw = np.interp(
            knot_r,
            p3a["r_kpc"].to_numpy(),
            p3a["tau_gradient_raw"].to_numpy(),
        )
        return np.maximum(raw, 1.0)

    dv2 = v_obs**2 - v_bar**2
    full_grad = compute_tau_gradient(r, dv2, k_tau)
    return np.maximum(np.interp(knot_r, r, full_grad), 1.0)


def fit_lowparam_knot_model(
    r_kpc: np.ndarray,
    v_obs_kms: np.ndarray,
    v_err_kms: np.ndarray,
    v_bar_kms: np.ndarray,
    knot_count: int,
    cfg: dict[str, Any],
    *,
    fit_mask: np.ndarray,
    phase3a_path: Path | None = None,
) -> LowParamFitResult:
    """Weighted least-squares fit of knot dτ/dr values."""
    r = np.asarray(r_kpc, dtype=float)
    v_obs = np.asarray(v_obs_kms, dtype=float)
    v_err = np.asarray(v_err_kms, dtype=float)
    v_bar = np.asarray(v_bar_kms, dtype=float)
    k_tau = cfg["k_tau"]
    m = fit_mask

    knot_r = knot_radii_quantile_fit_mask(
        r,
        m,
        knot_count,
        cfg["fit_min_radius_kpc"],
        cfg["fit_max_radius_kpc"],
    )
    p0 = _initial_knot_values(r, knot_r, v_obs, v_bar, k_tau, phase3a_path)

    lo = 0.0 if cfg["enforce_nonnegative_vtau2"] else -cfg["gradient_upper_bound"]
    hi = cfg["gradient_upper_bound"]
    bounds = (np.full(knot_count, lo), np.full(knot_count, hi))

    def fun(p: np.ndarray) -> np.ndarray:
        grad = knot_interpolated_tau_gradient(r[m], knot_r, p)
        v_mod, _, _ = tdf_velocity_model(v_bar[m], r[m], grad, k_tau)
        bad = ~np.isfinite(v_mod)
        if np.any(bad):
            return np.full(int(m.sum()), 1.0e6)
        return (v_obs[m] - v_mod) / v_err[m]

    result = least_squares(fun, p0, bounds=bounds)

    knot_vals = result.x
    grad_full = knot_interpolated_tau_gradient(r, knot_r, knot_vals)
    v_mod, v_tau2, neg = tdf_velocity_model(v_bar, r, grad_full, k_tau)
    tau_prof = integrate_tau_profile(r, grad_full, tau0=cfg["tau0"])

    name = f"tdf_lowparam_{knot_count}knot"
    return LowParamFitResult(
        model_name=name,
        knot_count=knot_count,
        knot_radii_kpc=knot_r,
        knot_values=knot_vals,
        k_tau=k_tau,
        tau_gradient=grad_full,
        tau_profile=tau_prof,
        v_model_kms=v_mod,
        v_tau_squared=v_tau2,
        negative_vtau2_flag=neg,
        success=result.success,
        cost=float(result.cost),
        message=result.message,
        n_iterations=int(result.nfev),
    )


def build_profile_table(
    base: pd.DataFrame,
    fit: LowParamFitResult,
    fit_mask: np.ndarray,
) -> pd.DataFrame:
    """58-row profile for one low-parameter model."""
    rv2 = compute_residual_velocity_squared(
        base["v_obs_kms"], fit.v_model_kms
    )
    return pd.DataFrame(
        {
            "galaxy_id": base["galaxy_id"],
            "r_kpc": base["r_kpc"],
            "v_obs_kms": base["v_obs_kms"],
            "v_err_kms": base["v_err_kms"],
            "v_bar_kms": base["v_bar_kms"],
            "delta_v2_kms2": base.get(
                "residual_v2_kms2",
                compute_residual_velocity_squared(
                    base["v_obs_kms"], base["v_bar_kms"]
                ),
            ),
            "model_name": fit.model_name,
            "knot_count": fit.knot_count,
            "k_tau": fit.k_tau,
            "tau_gradient_model": fit.tau_gradient,
            "tau_profile_model": fit.tau_profile,
            "v_tau_squared": fit.v_tau_squared,
            "negative_vtau2_flag": fit.negative_vtau2_flag,
            "v_tau_kms": np.where(
                fit.v_tau_squared >= 0,
                np.sqrt(np.maximum(fit.v_tau_squared, 0)),
                np.nan,
            ),
            "v_model_kms": fit.v_model_kms,
            "residual_kms": base["v_obs_kms"] - fit.v_model_kms,
            "residual_v2_kms2": rv2,
            "fit_mask": fit_mask,
            "source_id": base["source_id"],
            "data_quality_flag": base["data_quality_flag"],
            "notes": base["notes"],
        }
    )


def fit_result_to_parameter_row(fit: LowParamFitResult) -> dict[str, object]:
    return {
        "model_name": fit.model_name,
        "knot_count": fit.knot_count,
        "k_tau": fit.k_tau,
        "knot_radii_kpc": ";".join(f"{x:.6g}" for x in fit.knot_radii_kpc),
        "knot_gradient_values": ";".join(f"{x:.6g}" for x in fit.knot_values),
        "parameter_count": fit.parameter_count,
        "fit_success": fit.success,
        "fit_cost": fit.cost,
        "fit_message": fit.message,
        "n_iterations": fit.n_iterations,
        "n_negative_vtau2": int(fit.negative_vtau2_flag.sum()),
        "notes": TDF_NOTES_TEMPLATE.format(k=fit.knot_count, k_tau=fit.k_tau),
    }


def load_phase2_baseline_comparison(path: Path) -> pd.DataFrame:
    if not path.is_file():
        raise FileNotFoundError(f"Phase 2B comparison missing: {path}")
    return pd.read_csv(path)


def build_combined_comparison(
    phase2b_comparison: pd.DataFrame,
    tdf_rows: list[dict[str, object]],
) -> pd.DataFrame:
    """Merge Phase 2B baselines with Phase 3C TDF low-parameter rows."""
    base_cols = [
        "model_name",
        "n_points",
        "rmse_kms",
        "chi_square",
        "reduced_chi_square",
        "parameter_count",
        "aic",
        "bic",
        "n_negative_residual_v2",
        "notes",
        "n_fit_points",
        "dof",
        "fit_r_min_kpc",
        "fit_r_max_kpc",
        "n_rows_total",
    ]
    phase2 = phase2b_comparison[base_cols].copy()
    phase2["model_family"] = phase2["model_name"].map(
        {
            "baryonic_only": "baryonic",
            "nfw": "halo_baseline",
            "burkert": "halo_baseline",
        }
    ).fillna("baseline")
    tdf_df = pd.DataFrame(tdf_rows)
    for c in base_cols:
        if c not in tdf_df.columns:
            tdf_df[c] = np.nan
    tdf_df["model_family"] = "tdf_lowparam"
    if "burkert" in phase2["model_name"].values:
        burk_note = phase2.loc[phase2["model_name"] == "burkert", "notes"].iloc[0]
        if "bound" not in burk_note.lower() and "200" not in burk_note:
            phase2.loc[phase2["model_name"] == "burkert", "notes"] = (
                burk_note + " Burkert r0 often at upper bound (~200 kpc)."
            )
    return pd.concat([phase2[base_cols + ["model_family"]], tdf_df[base_cols + ["model_family"]]], ignore_index=True)


def _plot_rotation(
    prof: pd.DataFrame,
    profiles: pd.DataFrame,
    default_name: str,
    out_path: Path,
    dpi: int,
) -> None:
    r = prof["r_kpc"]
    fig, ax = plt.subplots(figsize=(9, 5))
    ax.errorbar(
        r,
        prof["v_obs_kms"],
        yerr=prof["v_err_kms"],
        fmt="k^",
        ms=4,
        capsize=2,
        label=r"$v_{\mathrm{obs}}$",
        zorder=5,
    )
    ax.plot(r, prof["v_bar_kms"], "b--", lw=1, label=r"$v_{\mathrm{bar}}$")
    mdf = profiles[profiles["model_name"] == default_name]
    ax.plot(r, mdf["v_model_kms"], "g-", lw=2, label=default_name)
    for name in profiles["model_name"].unique():
        if name == default_name:
            continue
        sub = profiles[profiles["model_name"] == name]
        ax.plot(sub["r_kpc"], sub["v_model_kms"], lw=1, alpha=0.5, label=name)
    ax.set_xlabel(r"$R$ [kpc]")
    ax.set_ylabel(r"$V$ [km s$^{-1}$]")
    ax.set_title("Phase 3C — rotation curves (low-parameter TDF)")
    ax.legend(fontsize=6, loc="lower right")
    ax.grid(True, alpha=0.3)
    fig.text(0.5, 0.01, FIG_CAVEAT, ha="center", fontsize=7)
    fig.tight_layout(rect=[0, 0.04, 1, 1])
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, dpi=dpi)
    plt.close(fig)


def _plot_tau_gradients(
    phase3a_path: Path | None,
    profiles: pd.DataFrame,
    out_path: Path,
    dpi: int,
) -> None:
    r = profiles["r_kpc"].unique()
    r = np.sort(r)
    fig, ax = plt.subplots(figsize=(9, 5))
    if phase3a_path is not None and phase3a_path.is_file():
        p3a = pd.read_csv(phase3a_path).sort_values("r_kpc")
        ax.plot(
            p3a["r_kpc"],
            p3a["tau_gradient_raw"],
            "k-",
            alpha=0.35,
            lw=1,
            label=r"$d\tau/dr$ raw (3A)",
        )
    for name in sorted(profiles["model_name"].unique()):
        sub = profiles[profiles["model_name"] == name].sort_values("r_kpc")
        ax.plot(sub["r_kpc"], sub["tau_gradient_model"], lw=1.8, label=name)
    ax.set_xlabel(r"$R$ [kpc]")
    ax.set_ylabel(r"$d\tau/dr$")
    ax.set_title("Phase 3C — knot τ gradients")
    ax.legend(fontsize=7)
    ax.grid(True, alpha=0.3)
    fig.text(0.5, 0.01, FIG_CAVEAT, ha="center", fontsize=7)
    fig.tight_layout(rect=[0, 0.04, 1, 1])
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, dpi=dpi)
    plt.close(fig)


def _plot_residuals(profiles: pd.DataFrame, out_path: Path, dpi: int) -> None:
    fig, ax = plt.subplots(figsize=(9, 4.5))
    for name in sorted(profiles["model_name"].unique()):
        sub = profiles[profiles["model_name"] == name].sort_values("r_kpc")
        ax.plot(sub["r_kpc"], sub["residual_kms"], lw=1.5, label=name)
    ax.axhline(0, color="gray", ls="--", lw=0.8)
    ax.set_xlabel(r"$R$ [kpc]")
    ax.set_ylabel(r"$v_{\mathrm{obs}} - v_{\mathrm{model}}$ [km/s]")
    ax.set_title("Phase 3C — velocity residuals")
    ax.legend(fontsize=7)
    ax.grid(True, alpha=0.3)
    fig.text(0.5, 0.01, FIG_CAVEAT, ha="center", fontsize=7)
    fig.tight_layout(rect=[0, 0.04, 1, 1])
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, dpi=dpi)
    plt.close(fig)


def run_phase3c_tdf_lowparam(
    processed_path: Path,
    config_path: Path,
    comparison_path: Path,
    parameters_path: Path,
    profiles_path: Path,
    combined_path: Path,
    fig_rotation: Path,
    fig_gradient: Path,
    fig_residuals: Path,
    phase2b_comparison_path: Path,
    phase3a_path: Path | None = None,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Run Phase 3C pipeline."""
    cfg = load_phase3c_config(config_path)
    if not cfg["enabled"]:
        raise ValueError("tdf.low_parameter_model.enabled is false")

    ds = load_m33_rotation_dataset(processed_path)
    df = ds.data.sort_values("r_kpc").reset_index(drop=True)
    prof = build_baryonic_profile(df)
    r = prof["r_kpc"].to_numpy()
    mask = fit_radius_mask(
        r, cfg["fit_min_radius_kpc"], cfg["fit_max_radius_kpc"]
    )
    prof["residual_v2_kms2"] = compute_residual_velocity_squared(
        prof["v_obs_kms"], prof["v_bar_kms"]
    )

    v_obs = prof["v_obs_kms"].to_numpy()
    v_err = prof["v_err_kms"].to_numpy()
    v_bar = prof["v_bar_kms"].to_numpy()

    fits: list[LowParamFitResult] = []
    comp_rows: list[dict[str, object]] = []
    profile_frames: list[pd.DataFrame] = []

    for k in cfg["compare_knot_counts"]:
        fit = fit_lowparam_knot_model(
            r,
            v_obs,
            v_err,
            v_bar,
            k,
            cfg,
            fit_mask=mask,
            phase3a_path=phase3a_path,
        )
        fits.append(fit)
        notes = TDF_NOTES_TEMPLATE.format(k=k, k_tau=cfg["k_tau"])
        row = comparison_metrics(
            fit.model_name,
            v_obs,
            fit.v_model_kms,
            v_err,
            fit.parameter_count,
            fit_mask=mask,
            fit_r_min_kpc=cfg["fit_min_radius_kpc"],
            fit_r_max_kpc=cfg["fit_max_radius_kpc"],
            n_rows_total=len(prof),
            residual_v2_kms2=compute_residual_velocity_squared(
                v_obs, fit.v_model_kms
            ),
            notes=notes,
        )
        comp_rows.append(comparison_row_to_dict(row))
        profile_frames.append(build_profile_table(prof, fit, mask))

    comparison_df = pd.DataFrame(comp_rows)
    params_df = pd.DataFrame([fit_result_to_parameter_row(f) for f in fits])
    profiles_df = pd.concat(profile_frames, ignore_index=True)

    phase2b = load_phase2_baseline_comparison(phase2b_comparison_path)
    combined_df = build_combined_comparison(phase2b, comp_rows)

    for p in (comparison_path, parameters_path, profiles_path, combined_path):
        p.parent.mkdir(parents=True, exist_ok=True)
    comparison_df.to_csv(comparison_path, index=False)
    params_df.to_csv(parameters_path, index=False)
    profiles_df.to_csv(profiles_path, index=False)
    combined_df.to_csv(combined_path, index=False)

    dpi = cfg["figure_dpi"]
    default_name = f"tdf_lowparam_{cfg['knot_count']}knot"
    _plot_rotation(prof, profiles_df, default_name, fig_rotation, dpi)
    _plot_tau_gradients(phase3a_path, profiles_df, fig_gradient, dpi)
    _plot_residuals(profiles_df, fig_residuals, dpi)

    return comparison_df, params_df, profiles_df, combined_df
