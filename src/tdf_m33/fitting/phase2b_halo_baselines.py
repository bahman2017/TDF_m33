"""Phase 2B NFW and Burkert halo baseline pipeline."""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import yaml

from tdf_m33.data.m33_dataset import load_m33_rotation_dataset
from tdf_m33.fitting.halo_fit import (
    HaloFitBounds,
    baryonic_comparison_under_mask,
    comparison_row_to_dict,
    corbelli_reference_notes,
    fit_halo,
    fit_radius_mask,
    halo_fit_to_parameter_row,
    prepare_phase2b_profile,
    comparison_metrics,
)

FIG_CAVEAT = (
    "Baryonic velocities derived (D1); PASS_WITH_CAVEAT. Halo fits are ΛCDM "
    "comparison baselines only—not TDF. Fit range 0.4–23 kpc (Corbelli 2014)."
)

BARYONIC_NOTES = (
    "Baryonic-only row recomputed on fit mask 0.4–23 kpc for fair comparison "
    "with NFW/Burkert (k=0; D1-derived components)."
)


def load_halo_fit_config(config_path: Path) -> dict:
    with config_path.open() as f:
        cfg = yaml.safe_load(f)
    return cfg.get("halo_fitting", {})


def run_phase2b_halo_baselines(
    processed_path: Path,
    config_path: Path,
    comparison_path: Path,
    parameters_path: Path,
    profiles_path: Path,
    fig_rotation: Path,
    fig_residual: Path,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Run NFW/Burkert fits and write Phase 2B outputs."""
    hf = load_halo_fit_config(config_path)
    fit_min = float(hf.get("fit_min_radius_kpc", 0.4))
    fit_max = float(hf.get("fit_max_radius_kpc", 23.0))
    bounds_cfg = hf.get("bounds", {})
    bounds = HaloFitBounds(
        log10_rho_min=float(bounds_cfg.get("log10_rho_min", -3.0)),
        log10_rho_max=float(bounds_cfg.get("log10_rho_max", 15.0)),
        log10_scale_radius_min=float(bounds_cfg.get("log10_scale_radius_min", -1.0)),
        log10_scale_radius_max=float(bounds_cfg.get("log10_scale_radius_max", 2.301)),
    )

    dataset = load_m33_rotation_dataset(processed_path)
    df = dataset.data.sort_values("r_kpc").reset_index(drop=True)
    r = df["r_kpc"].to_numpy()
    mask = fit_radius_mask(r, fit_min, fit_max)

    from tdf_m33.models.baryonic import build_baryonic_profile

    prof = build_baryonic_profile(df)
    v_bar = prof["v_bar_kms"].to_numpy()
    v_obs = prof["v_obs_kms"].to_numpy()
    v_err = prof["v_err_kms"].to_numpy()

    nfw_p0 = (
        float(hf.get("nfw_p0_log10_rho", 8.0)),
        float(hf.get("nfw_p0_log10_r_s", 0.0)),
    )
    burk_p0 = (
        float(hf.get("burkert_p0_log10_rho", 7.0)),
        float(hf.get("burkert_p0_log10_r0", 0.5)),
    )
    nfw = fit_halo(
        r, v_obs, v_err, v_bar, "nfw", fit_mask=mask, bounds=bounds, p0_log=nfw_p0
    )
    burkert = fit_halo(
        r,
        v_obs,
        v_err,
        v_bar,
        "burkert",
        fit_mask=mask,
        bounds=bounds,
        p0_log=burk_p0,
    )

    bary_row = baryonic_comparison_under_mask(
        prof, mask, fit_min, fit_max, BARYONIC_NOTES
    )
    nfw_row = comparison_metrics(
        "nfw",
        v_obs,
        nfw.v_model_kms,
        v_err,
        nfw.parameter_count,
        fit_mask=mask,
        fit_r_min_kpc=fit_min,
        fit_r_max_kpc=fit_max,
        n_rows_total=len(df),
        notes=corbelli_reference_notes("nfw", nfw),
    )
    burk_row = comparison_metrics(
        "burkert",
        v_obs,
        burkert.v_model_kms,
        v_err,
        burkert.parameter_count,
        fit_mask=mask,
        fit_r_min_kpc=fit_min,
        fit_r_max_kpc=fit_max,
        n_rows_total=len(df),
        notes=corbelli_reference_notes("burkert", burkert),
    )

    comparison_df = pd.DataFrame(
        [
            comparison_row_to_dict(bary_row),
            comparison_row_to_dict(nfw_row),
            comparison_row_to_dict(burk_row),
        ]
    )

    params_df = pd.DataFrame(
        [
            halo_fit_to_parameter_row(nfw, corbelli_reference_notes("nfw", nfw)),
            halo_fit_to_parameter_row(burkert, corbelli_reference_notes("burkert", burkert)),
        ]
    )

    profiles_df = prepare_phase2b_profile(df, nfw, burkert, mask)

    for p in (comparison_path, parameters_path, profiles_path):
        p.parent.mkdir(parents=True, exist_ok=True)
    comparison_df.to_csv(comparison_path, index=False)
    params_df.to_csv(parameters_path, index=False)
    profiles_df.to_csv(profiles_path, index=False)

    _plot_rotation_comparison(profiles_df, fig_rotation)
    _plot_residual_comparison(profiles_df, fig_residual)

    return comparison_df, params_df, profiles_df


def _plot_rotation_comparison(profile: pd.DataFrame, out_path: Path) -> None:
    r = profile["r_kpc"]
    m = profile["fit_mask"].astype(bool)
    fig, ax = plt.subplots(figsize=(9, 5))
    ax.errorbar(
        r,
        profile["v_obs_kms"],
        yerr=profile["v_err_kms"],
        fmt="k^",
        ms=4,
        capsize=2,
        label=r"$v_{\mathrm{obs}}$",
        zorder=4,
    )
    ax.plot(r, profile["v_bar_kms"], "--", color="C0", lw=1.2, label="baryonic only")
    ax.plot(r, profile["v_model_nfw_kms"], "-", color="C1", lw=1.5, label="baryons + NFW")
    ax.plot(
        r,
        profile["v_model_burkert_kms"],
        "-",
        color="C2",
        lw=1.5,
        label="baryons + Burkert",
    )
    ax.axvspan(
        profile.loc[m, "r_kpc"].min(),
        profile.loc[m, "r_kpc"].max(),
        alpha=0.08,
        color="gray",
        label="fit range",
    )
    ax.set_xlabel(r"$R$ [kpc]")
    ax.set_ylabel(r"$V$ [km s$^{-1}$]")
    ax.set_title("M33 rotation models — Phase 2B halo baselines")
    ax.legend(loc="lower right", fontsize=7)
    ax.grid(True, alpha=0.3)
    fig.text(0.5, 0.01, FIG_CAVEAT, ha="center", fontsize=6.5)
    fig.tight_layout(rect=[0, 0.04, 1, 1])
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, dpi=150)
    plt.close(fig)


def _plot_residual_comparison(profile: pd.DataFrame, out_path: Path) -> None:
    r = profile["r_kpc"]
    fig, ax = plt.subplots(figsize=(9, 4.5))
    ax.axhline(0, color="0.5", lw=0.8)
    ax.plot(r, profile["residual_baryonic_kms"], "o-", ms=3, label="baryonic only", alpha=0.8)
    ax.plot(r, profile["residual_nfw_kms"], "o-", ms=3, label="NFW", alpha=0.8)
    ax.plot(r, profile["residual_burkert_kms"], "o-", ms=3, label="Burkert", alpha=0.8)
    ax.set_xlabel(r"$R$ [kpc]")
    ax.set_ylabel(r"$v_{\mathrm{obs}} - v_{\mathrm{model}}$ [km s$^{-1}$]")
    ax.set_title("Velocity residuals — Phase 2B")
    ax.legend(loc="best", fontsize=8)
    ax.grid(True, alpha=0.3)
    fig.text(0.5, 0.01, FIG_CAVEAT, ha="center", fontsize=6.5)
    fig.tight_layout(rect=[0, 0.04, 1, 1])
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, dpi=150)
    plt.close(fig)
