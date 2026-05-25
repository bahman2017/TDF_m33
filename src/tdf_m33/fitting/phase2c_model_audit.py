"""Phase 2C: audit and consolidate Phase 2A/2B model comparison before TDF τ work."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import yaml

from tdf_m33.fitting.halo_fit import (
    CORBELLI2014_BURKERT_R0_REF_KPC,
    CORBELLI2014_BURKERT_RHO0_REF_MSUN_PC3,
    CORBELLI2014_NFW_C_REF,
    CORBELLI2014_NFW_MH_REF_MSUN,
    MSUN_PC3_TO_MSUN_KPC3,
)
from tdf_m33.models.halo import nfw_mass_enclosed, nfw_velocity

MSUN_KPC3_TO_MSUN_PC3 = 1.0 / MSUN_PC3_TO_MSUN_KPC3
R0_UPPER_BOUND_KPC = 200.0
R0_BOUND_TOLERANCE_KPC = 0.5
NFW_DIAGNOSTIC_RADII_KPC = (5.0, 10.0, 15.0, 23.0)


def _load_halo_bounds(config_path: Path | None) -> dict[str, float]:
    if config_path is None or not config_path.is_file():
        return {"log10_scale_radius_max": 2.301}
    with config_path.open() as f:
        cfg = yaml.safe_load(f)
    bounds = cfg.get("halo_fitting", {}).get("bounds", {})
    return {
        "log10_scale_radius_max": float(bounds.get("log10_scale_radius_max", 2.301)),
    }


def burkert_at_upper_r0_bound(r0_kpc: float, log10_r0_max: float) -> bool:
    """True when r0 is at or essentially at the configured upper bound (~200 kpc)."""
    r_max = 10.0 ** log10_r0_max
    return r0_kpc >= min(r_max, R0_UPPER_BOUND_KPC) - R0_BOUND_TOLERANCE_KPC


def build_audit_summary(
    comparison_df: pd.DataFrame,
    params_df: pd.DataFrame,
    phase2a_metrics_df: pd.DataFrame,
    config_path: Path | None = None,
) -> pd.DataFrame:
    """One row per model with consolidated metrics and audit flags."""
    bounds = _load_halo_bounds(config_path)
    log10_r0_max = bounds["log10_scale_radius_max"]

    nfw_row = params_df[params_df["model_name"] == "nfw"].iloc[0]
    bur_row = params_df[params_df["model_name"] == "burkert"].iloc[0]

    rho_s = float(nfw_row["rho_s_msun_kpc3"])
    r_s = float(nfw_row["r_s_kpc"])
    rho0_kpc3 = float(bur_row["rho0_msun_kpc3"])
    r0 = float(bur_row["r0_kpc"])
    rho0_pc3 = rho0_kpc3 * MSUN_KPC3_TO_MSUN_PC3

    m_nfw_23 = float(nfw_mass_enclosed(23.0, rho_s, r_s))
    nfw_c_approx = r_s / 23.0 if 23.0 > 0 else np.nan
    burkert_bound = burkert_at_upper_r0_bound(r0, log10_r0_max)
    burkert_r0_mismatch = abs(r0 - CORBELLI2014_BURKERT_R0_REF_KPC) > 5.0
    burkert_rho_mismatch = (
        abs(rho0_pc3 - CORBELLI2014_BURKERT_RHO0_REF_MSUN_PC3)
        > 0.005 * CORBELLI2014_BURKERT_RHO0_REF_MSUN_PC3
    )
    burkert_unstable = burkert_bound or (burkert_r0_mismatch and burkert_rho_mismatch)

    rows: list[dict[str, Any]] = []
    for _, comp in comparison_df.iterrows():
        name = str(comp["model_name"])
        row: dict[str, Any] = {
            "model_name": name,
            "fit_r_min_kpc": comp["fit_r_min_kpc"],
            "fit_r_max_kpc": comp["fit_r_max_kpc"],
            "n_fit_points": int(comp["n_fit_points"]),
            "n_rows_total": int(comp["n_rows_total"]),
            "rmse_kms": comp["rmse_kms"],
            "chi_square": comp["chi_square"],
            "reduced_chi_square": comp["reduced_chi_square"],
            "parameter_count": int(comp["parameter_count"]),
            "aic": comp["aic"],
            "bic": comp["bic"],
            "n_negative_residual_v2": int(comp["n_negative_residual_v2"]),
            "is_tdf_model": False,
            "tau_reconstruction_performed": False,
            "phase2_scope": "comparison_baseline_only",
            "baryonic_derivation_caveat": (
                "derived_baryonic_velocity_pass_with_caveat (Phase 1D-D1)"
            ),
        }
        if name == "nfw":
            row.update(
                {
                    "rho_s_msun_kpc3": rho_s,
                    "r_s_kpc": r_s,
                    "nfw_M_enclosed_23kpc_msun": m_nfw_23,
                    "nfw_c_approx_at_23kpc": nfw_c_approx,
                    "corbelli2014_c_ref": CORBELLI2014_NFW_C_REF,
                    "corbelli2014_Mh_ref_msun": CORBELLI2014_NFW_MH_REF_MSUN,
                    "nfw_is_lcdm_baseline_not_tdf": True,
                    "interpretation_note": (
                        "NFW fit is a ΛCDM comparison baseline on D1-derived baryons; "
                        "not a TDF result. Reduced χ²≈1 does not validate TDF or rule out DM."
                    ),
                    "burkert_at_r0_upper_bound": False,
                    "burkert_publication_stable": np.nan,
                }
            )
        elif name == "burkert":
            row.update(
                {
                    "rho0_msun_kpc3": rho0_kpc3,
                    "rho0_msun_pc3": rho0_pc3,
                    "r0_kpc": r0,
                    "corbelli2014_r0_ref_kpc": CORBELLI2014_BURKERT_R0_REF_KPC,
                    "corbelli2014_rho0_ref_msun_pc3": CORBELLI2014_BURKERT_RHO0_REF_MSUN_PC3,
                    "burkert_at_r0_upper_bound": burkert_bound,
                    "burkert_r0_mismatch_vs_corbelli": burkert_r0_mismatch,
                    "burkert_rho0_mismatch_vs_corbelli": burkert_rho_mismatch,
                    "burkert_publication_stable": not burkert_unstable,
                    "interpretation_note": (
                        "Burkert r0 at upper fit bound (~200 kpc); poorly constrained on "
                        "D1 baryonic curve—do not over-interpret vs Corbelli BVI reference."
                        if burkert_bound
                        else "Burkert differs from Corbelli BVI reference; D1 baryonic caveat applies."
                    ),
                }
            )
        else:
            p2a = phase2a_metrics_df.iloc[0]
            row.update(
                {
                    "phase2a_full_grid_rmse_kms": p2a["rmse_kms"],
                    "phase2a_full_grid_n_points": int(p2a["n_points"]),
                    "interpretation_note": (
                        "Baryonic-only: large χ² expected (missing halo). "
                        "Phase 3 uses Δv²=v_obs²−v_bar² from Phase 2A, not halo-subtracted."
                    ),
                    "burkert_at_r0_upper_bound": False,
                    "burkert_publication_stable": np.nan,
                }
            )
        rows.append(row)

    return pd.DataFrame(rows)


def build_residual_readiness(profile_2a: pd.DataFrame) -> tuple[pd.DataFrame, dict[str, Any]]:
    """Phase 3 readiness diagnostics from Phase 2A baryonic residual Δv²."""
    df = profile_2a.sort_values("r_kpc").copy()
    r = df["r_kpc"].to_numpy(dtype=float)
    delta_v2 = df["residual_v2_kms2"].to_numpy(dtype=float)

    eps = 1.0e-6
    sign_flag = np.where(
        delta_v2 > eps,
        "positive",
        np.where(delta_v2 < -eps, "negative", "zero"),
    )

    with np.errstate(divide="ignore", invalid="ignore"):
        accel_proxy = np.where(r > 0, delta_v2 / r, np.nan)

    d1 = np.gradient(delta_v2, r)
    d2 = np.gradient(d1, r)
    smoothness = np.abs(d2)

    abs_d1 = np.abs(d1)
    med_d1 = float(np.nanmedian(abs_d1)) if np.any(np.isfinite(abs_d1)) else 0.0
    spike_threshold = max(3.0 * med_d1, 1.0e3) if med_d1 > 0 else 1.0e3
    spike_mask = abs_d1 > spike_threshold

    out = pd.DataFrame(
        {
            "galaxy_id": df["galaxy_id"],
            "r_kpc": r,
            "delta_v2_kms2": delta_v2,
            "missing_acceleration_proxy": accel_proxy,
            "sign_flag": sign_flag,
            "d_delta_v2_dr_kms2_per_kpc": d1,
            "smoothness_proxy_d2_delta_v2_dr2": smoothness,
            "residual_spike_flag": spike_mask,
            "source_id": df["source_id"],
            "data_quality_flag": df["data_quality_flag"],
            "notes": df["notes"],
        }
    )

    n_neg = int(np.sum(delta_v2 < -eps))
    n_spikes = int(np.sum(spike_mask))
    all_positive = n_neg == 0
    summary = {
        "n_points": len(out),
        "n_negative_delta_v2": n_neg,
        "all_delta_v2_positive": all_positive,
        "n_residual_spikes": n_spikes,
        "max_abs_d_delta_v2_dr": float(np.nanmax(abs_d1)),
        "median_smoothness_proxy": float(np.nanmedian(smoothness)),
        "phase3_regularization_likely": n_spikes > 0 or not all_positive,
        "phase3_input_residual": "delta_v2 = v_obs^2 - v_bar^2 (Phase 2A, not NFW/Burkert)",
    }
    return out, summary


def _nfw_halo_diagnostics(rho_s: float, r_s: float) -> dict[str, float]:
    diag: dict[str, float] = {
        "nfw_M_enclosed_23kpc_msun": float(nfw_mass_enclosed(23.0, rho_s, r_s)),
    }
    for rk in NFW_DIAGNOSTIC_RADII_KPC:
        diag[f"nfw_v_halo_{int(rk)}kpc_kms"] = float(nfw_velocity(rk, rho_s, r_s))
    return diag


def render_audit_report(
    summary_df: pd.DataFrame,
    comparison_df: pd.DataFrame,
    params_df: pd.DataFrame,
    residual_summary: dict[str, Any],
    phase2a_metrics_df: pd.DataFrame,
) -> str:
    """Markdown audit report for Phase 2C."""
    fit_min = float(comparison_df["fit_r_min_kpc"].iloc[0])
    fit_max = float(comparison_df["fit_r_max_kpc"].iloc[0])
    n_fit = int(comparison_df["n_fit_points"].iloc[0])
    n_total = int(comparison_df["n_rows_total"].iloc[0])

    nfw_p = params_df[params_df["model_name"] == "nfw"].iloc[0]
    bur_p = params_df[params_df["model_name"] == "burkert"].iloc[0]
    rho_s = float(nfw_p["rho_s_msun_kpc3"])
    r_s = float(nfw_p["r_s_kpc"])
    rho0_pc3 = float(bur_p["rho0_msun_kpc3"]) * MSUN_KPC3_TO_MSUN_PC3
    r0 = float(bur_p["r0_kpc"])
    nfw_diag = _nfw_halo_diagnostics(rho_s, r_s)

    burkert_bound = bool(
        summary_df.loc[summary_df["model_name"] == "burkert", "burkert_at_r0_upper_bound"].iloc[0]
    )

    lines = [
        "# Phase 2C — Model comparison audit (M33)",
        "",
        "**Scope:** Audit and consolidation of Phase 2A (baryonic-only) and Phase 2B "
        "(NFW/Burkert halo baselines). **No TDF τ reconstruction has been performed.**",
        "",
        "## Fit mask (Phase 2B metrics)",
        "",
        f"- Range: **{fit_min} ≤ R ≤ {fit_max} kpc**",
        f"- Points in mask: **{n_fit} / {n_total}**",
        "",
        "## Baryonic velocities (mandatory caveat)",
        "",
        "- Components are **D1-derived** from Corbelli et al. 2014 Table 1 surface densities.",
        "- `data_quality_flag`: **derived_baryonic_velocity_pass_with_caveat**",
        "- Fig. 12 digitization is sanity-check only, not canonical velocities.",
        "",
        "## Model summaries (fit-masked, Phase 2B comparison table)",
        "",
    ]

    for _, row in comparison_df.iterrows():
        lines.append(
            f"### {row['model_name']}\n\n"
            f"- RMSE: {row['rmse_kms']:.2f} km/s\n"
            f"- χ²: {row['chi_square']:.1f}, reduced χ²: {row['reduced_chi_square']:.3f}\n"
            f"- k: {int(row['parameter_count'])}, AIC: {row['aic']:.1f}, BIC: {row['bic']:.1f}\n"
            f"- Negative Δv² (halo-model residuals): {int(row['n_negative_residual_v2'])}\n"
        )

    p2a = phase2a_metrics_df.iloc[0]
    lines.extend(
        [
            "## Phase 2A full-grid baryonic baseline (58 rows)",
            "",
            f"- RMSE: {p2a['rmse_kms']:.2f} km/s (all radii)",
            f"- χ²: {p2a['chi_square']:.1f}, reduced χ²: {p2a['reduced_chi_square']:.3f}",
            f"- Negative baryonic Δv²: {int(p2a['n_negative_residual_v2'])}",
            "",
            "## NFW halo sanity (comparison baseline, not TDF)",
            "",
            f"- Fitted ρ_s = {rho_s:.4e} M☉/kpc³, r_s = {r_s:.3f} kpc",
            f"- Approx. c = r_s/R_max ≈ {r_s / fit_max:.2f} (R_max = {fit_max} kpc; not virial)",
            f"- M(<{fit_max} kpc) ≈ {nfw_diag['nfw_M_enclosed_23kpc_msun']:.3e} M☉ "
            "(enclosed mass at fit outer radius; not M_vir)",
            f"- Corbelli 2014 sanity ref: c ≈ {CORBELLI2014_NFW_C_REF}, "
            f"M_h ≈ {CORBELLI2014_NFW_MH_REF_MSUN:.2e} M☉ (not acceptance criteria)",
            "",
            "**v_halo at selected radii [km/s]:**",
        ]
    )
    for rk in NFW_DIAGNOSTIC_RADII_KPC:
        key = f"nfw_v_halo_{int(rk)}kpc_kms"
        lines.append(f"- R = {rk} kpc: {nfw_diag[key]:.2f}")
    lines.extend(
        [
            "",
            "NFW reduced χ² ≈ 1 on the fit mask is expected for a standard halo fit; "
            "this does **not** validate TDF or disprove dark matter.",
            "",
            "## Burkert halo sanity",
            "",
            f"- Fitted ρ₀ = {float(bur_p['rho0_msun_kpc3']):.4e} M☉/kpc³ "
            f"= **{rho0_pc3:.4f} M☉/pc³**",
            f"- Fitted r₀ = **{r0:.3f} kpc**",
            f"- Corbelli 2014 BVI sanity ref: r₀ ≈ {CORBELLI2014_BURKERT_R0_REF_KPC} kpc, "
            f"ρ₀ ≈ {CORBELLI2014_BURKERT_RHO0_REF_MSUN_PC3} M☉/pc³",
            "",
        ]
    )
    if burkert_bound:
        lines.append(
            "### ⚠ Burkert boundary warning\n\n"
            "Burkert **r₀ hit the upper fit bound (~200 kpc)**. The fit is "
            "**poorly constrained** and **not publication-stable** for direct comparison "
            "to Corbelli BVI parameters. Do not over-interpret Burkert metrics vs NFW.\n"
        )
    else:
        lines.append(
            "Burkert parameters differ from Corbelli reference; interpret with D1 baryonic caveat.\n"
        )

    lines.extend(
        [
            "",
            "## Phase 3 prerequisite (τ reconstruction)",
            "",
            "- Use **baryonic residual only**: Δv² = v_obs² − v_bar² from Phase 2A profile.",
            "- Do **not** use NFW/Burkert-subtracted residuals for TDF τ-gradient work.",
            "- **No τ-profile, K_τ fit, 2D τ-map, or lensing outputs exist yet.**",
            "",
            "## Residual readiness (Phase 2A Δv²)",
            "",
            f"- Points: {residual_summary['n_points']}",
            f"- Negative Δv²: {residual_summary['n_negative_delta_v2']}",
            f"- All Δv² positive: **{residual_summary['all_delta_v2_positive']}**",
            f"- Obvious gradient spikes (heuristic): {residual_summary['n_residual_spikes']}",
            f"- Phase 3 smoothing/regularization likely needed: "
            f"**{residual_summary['phase3_regularization_likely']}**",
            "",
            "## Claim control",
            "",
            "- Phase 2 = **comparison baselines only** (baryonic, NFW, Burkert).",
            "- No dark-matter replacement or disproof claim is supported at this stage.",
            "",
        ]
    )
    return "\n".join(lines)


def plot_phase2c_summary(
    profiles_2b: pd.DataFrame,
    readiness_df: pd.DataFrame,
    out_path: Path,
    dpi: int = 150,
) -> None:
    """Rotation curves + TDF input Δv² inset."""
    fig, ax = plt.subplots(figsize=(9, 5.5))
    r = profiles_2b["r_kpc"].to_numpy()
    ax.errorbar(
        r,
        profiles_2b["v_obs_kms"],
        yerr=profiles_2b["v_err_kms"],
        fmt="ko",
        ms=4,
        capsize=2,
        label=r"$v_{\mathrm{obs}}$",
        zorder=5,
    )
    ax.plot(r, profiles_2b["v_bar_kms"], "b--", label=r"$v_{\mathrm{bar}}$ (D1)")
    ax.plot(r, profiles_2b["v_model_nfw_kms"], "g-", label="NFW + baryons")
    ax.plot(r, profiles_2b["v_model_burkert_kms"], "m:", label="Burkert + baryons")
    ax.set_xlabel("R [kpc]")
    ax.set_ylabel("v [km/s]")
    ax.set_title("Phase 2C audit: rotation baselines (58 radii)")
    ax.legend(loc="lower right", fontsize=8)
    ax.grid(True, alpha=0.3)

    ax2 = ax.inset_axes([0.52, 0.52, 0.45, 0.42])
    r2 = readiness_df["r_kpc"].to_numpy()
    dv2 = readiness_df["delta_v2_kms2"].to_numpy()
    ax2.plot(r2, dv2, "c-", lw=1.5)
    ax2.axhline(0, color="gray", ls="--", lw=0.8)
    ax2.set_xlabel("R [kpc]", fontsize=7)
    ax2.set_ylabel(r"$\Delta v^2$ [km²/s²]", fontsize=7)
    ax2.set_title("TDF input (Phase 2A)", fontsize=8)
    ax2.tick_params(labelsize=7)
    ax2.grid(True, alpha=0.25)

    fig.text(
        0.5,
        0.01,
        "Baryonic: PASS_WITH_CAVEAT. NFW/Burkert: ΛCDM baselines only. "
        "Burkert r₀ may be bound-limited.",
        ha="center",
        fontsize=7,
        color="dimgray",
    )
    fig.tight_layout(rect=[0, 0.03, 1, 1])
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, dpi=dpi)
    plt.close(fig)


def run_phase2c_model_audit(
    phase2a_metrics_path: Path,
    phase2a_profile_path: Path,
    phase2b_comparison_path: Path,
    phase2b_parameters_path: Path,
    phase2b_profiles_path: Path,
    summary_out: Path,
    report_out: Path,
    readiness_out: Path,
    fig_out: Path | None = None,
    config_path: Path | None = None,
) -> tuple[pd.DataFrame, pd.DataFrame, str]:
    """Run Phase 2C audit; write tables, report, and optional figure."""
    for p in (
        phase2a_metrics_path,
        phase2a_profile_path,
        phase2b_comparison_path,
        phase2b_parameters_path,
        phase2b_profiles_path,
    ):
        if not p.is_file():
            raise FileNotFoundError(f"Required input missing: {p}")

    metrics_2a = pd.read_csv(phase2a_metrics_path)
    profile_2a = pd.read_csv(phase2a_profile_path)
    comparison = pd.read_csv(phase2b_comparison_path)
    params = pd.read_csv(phase2b_parameters_path)
    profiles_2b = pd.read_csv(phase2b_profiles_path)

    summary_df = build_audit_summary(comparison, params, metrics_2a, config_path)
    readiness_df, residual_summary = build_residual_readiness(profile_2a)
    report_md = render_audit_report(
        summary_df, comparison, params, residual_summary, metrics_2a
    )

    summary_out.parent.mkdir(parents=True, exist_ok=True)
    readiness_out.parent.mkdir(parents=True, exist_ok=True)
    report_out.parent.mkdir(parents=True, exist_ok=True)

    summary_df.to_csv(summary_out, index=False)
    readiness_df.to_csv(readiness_out, index=False)
    report_out.write_text(report_md, encoding="utf-8")

    if fig_out is not None:
        plot_phase2c_summary(profiles_2b, readiness_df, fig_out)

    return summary_df, readiness_df, report_md
