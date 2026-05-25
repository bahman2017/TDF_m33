"""Phase 3B-A: smoothed / regularized TDF τ-gradient reconstruction."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import yaml

from tdf_m33.fitting.halo_fit import FitRadiusMask
from tdf_m33.models.tdf_radial import (
    compute_v_tau_squared_from_gradient,
    integrate_tau_profile,
    validate_k_tau,
)
from tdf_m33.models.tdf_regularization import (
    SmoothingMethod,
    count_tau_gradient_spikes,
    flag_negative_vtau_squared,
    gradient_smoothness_metric,
    smooth_tau_gradient,
)

FIG_CAVEAT = (
    "Phase 3B-A: regularized τ from baryonic Δv² (D1 PASS_WITH_CAVEAT). "
    "Smoothing is regularization, not evidence vs NFW. K_τ=1 normalization. No lensing."
)

DIAG_NOTES = (
    "Regularized τ-gradient is not an independent halo fit. Smoothing parameters "
    "are fixed from config (not fitted to rotation). AIC/BIC comparison deferred "
    "to Phase 3C low-parameter / effective-DOF treatment."
)

EFFECTIVE_COMPLEXITY = {
    "gaussian_radius_smoothing": (
        "Fixed σ_kpc from config; not fitted. Effective DOF not reduced to a "
        "small parameter count — formal comparison deferred to Phase 3C."
    ),
    "smoothing_spline": (
        "Fixed spline s from config (or documented variance fallback); not fitted. "
        "Formal model comparison deferred to Phase 3C."
    ),
}


def load_tdf_regularization_config(config_path: Path) -> dict[str, Any]:
    with config_path.open() as f:
        cfg = yaml.safe_load(f)
    tdf = cfg.get("tdf", {})
    reg = tdf.get("regularization", {})
    hf = cfg.get("halo_fitting", {})
    methods = reg.get("compare_methods", ["gaussian_radius_smoothing"])
    return {
        "k_tau": float(tdf.get("k_tau", 1.0)),
        "tau0": float(tdf.get("tau0", 0.0)),
        "input_residual": str(tdf.get("input_residual", "baryonic_only_delta_v2")),
        "use_fit_mask_for_summary": bool(tdf.get("use_fit_mask_for_summary", True)),
        "regularization_enabled": bool(reg.get("enabled", True)),
        "default_method": str(reg.get("default_method", "gaussian_radius_smoothing")),
        "gaussian_sigma_kpc": float(reg.get("gaussian_sigma_kpc", 0.75)),
        "spline_smoothing_factor": reg.get("spline_smoothing_factor"),
        "preserve_positive_vtau2": bool(reg.get("preserve_positive_vtau2", True)),
        "compare_methods": [str(m) for m in methods],
        "fit_min_radius_kpc": float(hf.get("fit_min_radius_kpc", 0.4)),
        "fit_max_radius_kpc": float(hf.get("fit_max_radius_kpc", 23.0)),
        "figure_dpi": int(cfg.get("plotting", {}).get("figure_dpi", 150)),
    }


def load_phase3a_reconstruction(path: Path) -> pd.DataFrame:
    if not path.is_file():
        raise FileNotFoundError(f"Phase 3A table missing: {path}")
    df = pd.read_csv(path).sort_values("r_kpc").reset_index(drop=True)
    required = {
        "r_kpc",
        "tau_gradient_raw",
        "delta_v2_kms2",
        "v_obs_kms",
        "v_err_kms",
        "v_bar_kms",
    }
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"Phase 3A CSV missing columns: {missing}")
    return df


def _reconstruct_from_smoothed_gradient(
    base: pd.DataFrame,
    method: SmoothingMethod,
    tau_gradient_smooth: np.ndarray,
    cfg: dict[str, Any],
) -> pd.DataFrame:
    k_tau = validate_k_tau(cfg["k_tau"])
    tau0 = cfg["tau0"]
    r = base["r_kpc"].to_numpy(dtype=float)
    v_bar = base["v_bar_kms"].to_numpy(dtype=float)
    v_obs = base["v_obs_kms"].to_numpy(dtype=float)

    v_tau2 = compute_v_tau_squared_from_gradient(r, tau_gradient_smooth, k_tau)
    neg_vtau2 = flag_negative_vtau_squared(v_tau2)
    tau_smooth = integrate_tau_profile(r, tau_gradient_smooth, tau0=tau0)

    v_tau = np.full_like(v_tau2, np.nan)
    v_tdf = np.full_like(v_tau2, np.nan)
    pos_v2 = v_tau2 >= 0
    v_tau[pos_v2] = np.sqrt(v_tau2[pos_v2])
    sum_sq = v_bar**2 + v_tau2
    pos_sum = sum_sq >= 0
    v_tdf[pos_sum] = np.sqrt(sum_sq[pos_sum])

    residual = v_tdf - v_obs
    residual = np.where(np.isfinite(v_tdf), residual, np.nan)

    out = base.copy()
    out["regularization_method"] = method
    out["tau_gradient_smooth"] = tau_gradient_smooth
    out["tau_smooth"] = tau_smooth
    out["v_tau_squared_smooth"] = v_tau2
    out["negative_vtau2_flag"] = neg_vtau2
    out["v_tau_smooth_kms"] = v_tau
    out["v_tdf_smooth_kms"] = v_tdf
    out["residual_smooth_kms"] = residual
    return out


def build_regularized_profiles(
    phase3a_df: pd.DataFrame,
    cfg: dict[str, Any],
) -> pd.DataFrame:
    """Long-format profiles: one block per smoothing method."""
    r = phase3a_df["r_kpc"].to_numpy(dtype=float)
    grad_raw = phase3a_df["tau_gradient_raw"].to_numpy(dtype=float)
    frames: list[pd.DataFrame] = []

    for method in cfg["compare_methods"]:
        if method not in ("gaussian_radius_smoothing", "smoothing_spline"):
            raise ValueError(f"Unsupported compare_methods entry: {method}")
        grad_smooth = smooth_tau_gradient(
            r,
            grad_raw,
            method,  # type: ignore[arg-type]
            gaussian_sigma_kpc=cfg["gaussian_sigma_kpc"],
            spline_smoothing_factor=cfg["spline_smoothing_factor"],
        )
        frames.append(
            _reconstruct_from_smoothed_gradient(
                phase3a_df,
                method,  # type: ignore[arg-type]
                grad_smooth,
                cfg,
            )
        )

    return pd.concat(frames, ignore_index=True)


def _rmse_on_mask(
    err: np.ndarray,
    r_kpc: np.ndarray,
    cfg: dict[str, Any],
) -> tuple[float, float]:
    mask = np.isfinite(err)
    if cfg["use_fit_mask_for_summary"]:
        fit = FitRadiusMask(cfg["fit_min_radius_kpc"], cfg["fit_max_radius_kpc"])
        mask &= fit.mask(r_kpc)
    e = err[mask]
    if e.size == 0:
        return float("nan"), float("nan")
    return float(np.sqrt(np.mean(e**2))), float(np.max(np.abs(e)))


def build_method_diagnostics(
    phase3a_df: pd.DataFrame,
    method_df: pd.DataFrame,
    method: str,
    cfg: dict[str, Any],
) -> dict[str, Any]:
    r = phase3a_df["r_kpc"].to_numpy(dtype=float)
    grad_raw = phase3a_df["tau_gradient_raw"].to_numpy(dtype=float)
    grad_smooth = method_df["tau_gradient_smooth"].to_numpy(dtype=float)
    dv2 = phase3a_df["delta_v2_kms2"].to_numpy(dtype=float)

    raw_spikes, _ = count_tau_gradient_spikes(r, grad_raw)
    smooth_spikes, _ = count_tau_gradient_spikes(r, grad_smooth)
    raw_smooth = gradient_smoothness_metric(r, grad_raw)
    sm_smooth = gradient_smoothness_metric(r, grad_smooth)

    err = method_df["residual_smooth_kms"].to_numpy(dtype=float)
    rmse, max_abs = _rmse_on_mask(err, r, cfg)

    if method == "gaussian_radius_smoothing":
        smooth_param = f"sigma_kpc={cfg['gaussian_sigma_kpc']}"
    else:
        s = cfg["spline_smoothing_factor"]
        smooth_param = f"spline_s={s if s is not None else 'variance_fallback'}"

    return {
        "method": method,
        "k_tau": cfg["k_tau"],
        "tau0": cfg["tau0"],
        "smoothing_parameters": smooth_param,
        "n_rows": len(method_df),
        "n_negative_raw_delta_v2": int(np.sum(dv2 < -1.0e-6)),
        "n_negative_smoothed_vtau2": int(method_df["negative_vtau2_flag"].sum()),
        "raw_gradient_spike_count": raw_spikes,
        "smoothed_gradient_spike_count": smooth_spikes,
        "raw_gradient_smoothness_metric": raw_smooth,
        "smoothed_gradient_smoothness_metric": sm_smooth,
        "reconstruction_rmse_smooth_kms": rmse,
        "max_abs_reconstruction_error_smooth_kms": max_abs,
        "is_independent_halo_fit": False,
        "aic_bic_comparison_deferred": True,
        "effective_complexity_note": EFFECTIVE_COMPLEXITY.get(method, ""),
        "notes": DIAG_NOTES,
        "preserve_positive_vtau2_check": cfg["preserve_positive_vtau2"],
    }


def build_diagnostics_table(
    phase3a_df: pd.DataFrame,
    profiles: pd.DataFrame,
    cfg: dict[str, Any],
) -> pd.DataFrame:
    rows = []
    for method in cfg["compare_methods"]:
        mdf = profiles[profiles["regularization_method"] == method]
        rows.append(build_method_diagnostics(phase3a_df, mdf, method, cfg))
    return pd.DataFrame(rows)


def _plot_gradient_comparison(
    phase3a_df: pd.DataFrame,
    profiles: pd.DataFrame,
    out_path: Path,
    dpi: int,
) -> None:
    r = phase3a_df["r_kpc"]
    fig, ax = plt.subplots(figsize=(9, 5))
    ax.plot(r, phase3a_df["tau_gradient_raw"], "k-", alpha=0.4, lw=1, label=r"$d\tau/dr$ raw")
    colors = {"gaussian_radius_smoothing": "C0", "smoothing_spline": "C1"}
    for method in profiles["regularization_method"].unique():
        mdf = profiles[profiles["regularization_method"] == method]
        ax.plot(
            mdf["r_kpc"],
            mdf["tau_gradient_smooth"],
            color=colors.get(method, "C2"),
            lw=1.8,
            label=f"{method}",
        )
    ax.set_xlabel(r"$R$ [kpc]")
    ax.set_ylabel(r"$d\tau/dr$")
    ax.set_title("Phase 3B-A — regularized τ gradient")
    ax.legend(fontsize=7)
    ax.grid(True, alpha=0.3)
    fig.text(0.5, 0.01, FIG_CAVEAT, ha="center", fontsize=7)
    fig.tight_layout(rect=[0, 0.04, 1, 1])
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, dpi=dpi)
    plt.close(fig)


def _plot_tau_profiles(profiles: pd.DataFrame, out_path: Path, dpi: int) -> None:
    fig, ax = plt.subplots(figsize=(9, 5))
    for method in profiles["regularization_method"].unique():
        mdf = profiles[profiles["regularization_method"] == method]
        ax.plot(mdf["r_kpc"], mdf["tau_smooth"], lw=1.8, label=method)
    ax.set_xlabel(r"$R$ [kpc]")
    ax.set_ylabel(r"$\tau(r)$")
    ax.set_title("Phase 3B-A — integrated τ (smoothed gradients)")
    ax.legend(fontsize=7)
    ax.grid(True, alpha=0.3)
    fig.text(0.5, 0.01, FIG_CAVEAT, ha="center", fontsize=7)
    fig.tight_layout(rect=[0, 0.04, 1, 1])
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, dpi=dpi)
    plt.close(fig)


def _plot_reconstruction_check(
    phase3a_df: pd.DataFrame,
    profiles: pd.DataFrame,
    out_path: Path,
    dpi: int,
) -> None:
    r = phase3a_df["r_kpc"]
    fig, ax = plt.subplots(figsize=(9, 5))
    ax.errorbar(
        r,
        phase3a_df["v_obs_kms"],
        yerr=phase3a_df["v_err_kms"],
        fmt="k^",
        ms=4,
        capsize=2,
        label=r"$v_{\mathrm{obs}}$",
        zorder=5,
    )
    ax.plot(r, phase3a_df["v_bar_kms"], "b--", lw=1, label=r"$v_{\mathrm{bar}}$")
    for method in profiles["regularization_method"].unique():
        mdf = profiles[profiles["regularization_method"] == method]
        ax.plot(mdf["r_kpc"], mdf["v_tdf_smooth_kms"], lw=1.8, label=f"TDF ({method})")
    ax.set_xlabel(r"$R$ [kpc]")
    ax.set_ylabel(r"$V$ [km s$^{-1}$]")
    ax.set_title("Phase 3B-A — regularized TDF vs observed")
    ax.legend(fontsize=6, loc="lower right")
    ax.grid(True, alpha=0.3)
    fig.text(0.5, 0.01, FIG_CAVEAT, ha="center", fontsize=7)
    fig.tight_layout(rect=[0, 0.04, 1, 1])
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, dpi=dpi)
    plt.close(fig)


def _plot_tradeoff(diag: pd.DataFrame, out_path: Path, dpi: int) -> None:
    fig, ax1 = plt.subplots(figsize=(7, 4.5))
    methods = diag["method"].tolist()
    x = np.arange(len(methods))
    w = 0.35
    ax1.bar(x - w / 2, diag["raw_gradient_spike_count"], w, label="raw spikes", color="gray")
    ax1.bar(
        x + w / 2,
        diag["smoothed_gradient_spike_count"],
        w,
        label="smoothed spikes",
        color="C0",
    )
    ax1.set_xticks(x)
    ax1.set_xticklabels(methods, rotation=15, ha="right", fontsize=8)
    ax1.set_ylabel("Gradient spike count")
    ax1.legend(fontsize=8)
    ax2 = ax1.twinx()
    ax2.plot(
        x,
        diag["reconstruction_rmse_smooth_kms"],
        "ro-",
        label="RMSE vs obs",
    )
    ax2.set_ylabel("RMSE [km/s]")
    ax1.set_title("Phase 3B-A — regularization tradeoff")
    fig.text(0.5, 0.01, FIG_CAVEAT, ha="center", fontsize=7)
    fig.tight_layout(rect=[0, 0.04, 1, 1])
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, dpi=dpi)
    plt.close(fig)


def run_phase3b_tdf_regularized(
    phase3a_path: Path,
    config_path: Path,
    profiles_path: Path,
    diagnostics_path: Path,
    fig_gradient: Path,
    fig_tau: Path,
    fig_check: Path,
    fig_tradeoff: Path,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Run Phase 3B-A and write tables and figures."""
    cfg = load_tdf_regularization_config(config_path)
    if not cfg["regularization_enabled"]:
        raise ValueError("tdf.regularization.enabled is false; enable for Phase 3B-A")

    if cfg["input_residual"] != "baryonic_only_delta_v2":
        raise ValueError(
            f"Phase 3B requires baryonic_only_delta_v2; got {cfg['input_residual']}"
        )

    phase3a_df = load_phase3a_reconstruction(phase3a_path)
    profiles = build_regularized_profiles(phase3a_df, cfg)
    diag = build_diagnostics_table(phase3a_df, profiles, cfg)

    profiles_path.parent.mkdir(parents=True, exist_ok=True)
    profiles.to_csv(profiles_path, index=False)
    diagnostics_path.parent.mkdir(parents=True, exist_ok=True)
    diag.to_csv(diagnostics_path, index=False)

    dpi = cfg["figure_dpi"]
    _plot_gradient_comparison(phase3a_df, profiles, fig_gradient, dpi)
    _plot_tau_profiles(profiles, fig_tau, dpi)
    _plot_reconstruction_check(phase3a_df, profiles, fig_check, dpi)
    _plot_tradeoff(diag, fig_tradeoff, dpi)

    return profiles, diag
