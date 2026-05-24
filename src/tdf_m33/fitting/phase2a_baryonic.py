"""Phase 2A baryonic-only baseline pipeline."""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

from tdf_m33.data.m33_dataset import load_m33_rotation_dataset
from tdf_m33.fitting.metrics import baryonic_only_metrics, fit_metrics_to_row
from tdf_m33.models.baryonic import build_baryonic_profile, summarize_negative_residuals

BARYONIC_ONLY_NOTES = (
    "Phase 2A baryonic-only baseline: v_gas/v_disk from Phase 1D-D1 derivation "
    "(not published Corbelli velocity columns). data_quality_flag "
    "derived_baryonic_velocity_pass_with_caveat. No halo or TDF terms. "
    "parameter_count=0 (components fixed, not fitted in Phase 2A)."
)

FIG_CAVEAT = (
    "Baryonic components are derived (D1 disk gravity), not tabulated in Corbelli "
    "2014 Table 1; PASS_WITH_CAVEAT vs Fig. 12. Not a halo fit."
)


def _plot_rotation_curve(profile: pd.DataFrame, out_path: Path) -> None:
    r = profile["r_kpc"]
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.errorbar(
        r,
        profile["v_obs_kms"],
        yerr=profile["v_err_kms"],
        fmt="k^",
        ms=4,
        capsize=2,
        label=r"$v_{\mathrm{obs}}$ (Table 1)",
        zorder=3,
    )
    ax.plot(
        r,
        profile["v_bar_kms"],
        color="C0",
        lw=1.8,
        label=r"$v_{\mathrm{bar}}$ (recomputed)",
    )
    ax.plot(
        r,
        profile["v_gas_kms"],
        "--",
        color="C2",
        lw=1,
        alpha=0.8,
        label=r"$v_{\mathrm{gas}}$ (derived)",
    )
    ax.plot(
        r,
        profile["v_disk_kms"],
        "--",
        color="C3",
        lw=1,
        alpha=0.8,
        label=r"$v_{\mathrm{disk}}$ (derived)",
    )
    ax.set_xlabel(r"$R$ [kpc]")
    ax.set_ylabel(r"$V$ [km s$^{-1}$]")
    ax.set_title("M33 rotation curve — baryonic-only baseline (Phase 2A)")
    ax.legend(loc="lower right", fontsize=8)
    ax.grid(True, alpha=0.3)
    fig.text(0.5, 0.01, FIG_CAVEAT, ha="center", fontsize=7, wrap=True)
    fig.tight_layout(rect=[0, 0.04, 1, 1])
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, dpi=150)
    plt.close(fig)


def _plot_residual_v2(profile: pd.DataFrame, out_path: Path) -> None:
    r = profile["r_kpc"]
    rv2 = profile["residual_v2_kms2"]
    fig, ax = plt.subplots(figsize=(8, 4.5))
    ax.axhline(0, color="0.5", lw=0.8)
    ax.plot(r, rv2, "o-", color="C4", ms=4, lw=1.2)
    neg = rv2 < 0
    if neg.any():
        ax.plot(r[neg], rv2[neg], "v", color="C1", ms=6, label="Δv² < 0 (unclipped)")
    ax.set_xlabel(r"$R$ [kpc]")
    ax.set_ylabel(r"$v_{\mathrm{obs}}^2 - v_{\mathrm{bar}}^2$ [(km s$^{-1}$)$^2$]")
    ax.set_title(r"Residual squared velocity — missing support proxy (Phase 2A)")
    if neg.any():
        ax.legend(loc="best", fontsize=8)
    ax.grid(True, alpha=0.3)
    fig.text(0.5, 0.01, FIG_CAVEAT, ha="center", fontsize=7, wrap=True)
    fig.tight_layout(rect=[0, 0.04, 1, 1])
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, dpi=150)
    plt.close(fig)


def run_phase2a_baryonic_only(
    processed_path: Path,
    metrics_path: Path,
    profile_path: Path,
    fig_rotation: Path,
    fig_residual: Path,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Execute Phase 2A pipeline; return (metrics_df, profile_df)."""
    dataset = load_m33_rotation_dataset(processed_path)
    profile = build_baryonic_profile(dataset.data)

    keep_cols = [
        "galaxy_id",
        "r_kpc",
        "v_obs_kms",
        "v_err_kms",
        "v_gas_kms",
        "v_disk_kms",
        "v_bulge_kms",
        "v_bar_kms",
        "residual_v2_kms2",
        "residual_accel_proxy_kms2_per_kpc",
        "source_id",
        "data_quality_flag",
        "notes",
    ]
    profile_out = profile[keep_cols].sort_values("r_kpc").reset_index(drop=True)

    metrics = baryonic_only_metrics(
        profile_out["v_obs_kms"].to_numpy(),
        profile_out["v_bar_kms"].to_numpy(),
        profile_out["v_err_kms"].to_numpy(),
        profile_out["residual_v2_kms2"].to_numpy(),
        notes=BARYONIC_ONLY_NOTES,
    )
    metrics_df = pd.DataFrame([fit_metrics_to_row(metrics)])

    metrics_path.parent.mkdir(parents=True, exist_ok=True)
    metrics_df.to_csv(metrics_path, index=False)
    profile_out.to_csv(profile_path, index=False)

    _plot_rotation_curve(profile_out, fig_rotation)
    _plot_residual_v2(profile_out, fig_residual)

    return metrics_df, profile_out
