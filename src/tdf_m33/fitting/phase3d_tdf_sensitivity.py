"""Phase 3D: sensitivity and robustness audit for low-parameter TDF models."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import yaml

from tdf_m33.data.m33_dataset import load_m33_rotation_dataset
from tdf_m33.fitting.halo_fit import comparison_metrics, fit_radius_mask
from tdf_m33.fitting.phase3c_tdf_lowparam import (
    fit_lowparam_knot_model,
    load_phase3c_config,
)
from tdf_m33.models.baryonic import build_baryonic_profile
from tdf_m33.models.tdf_lowparam import tdf_velocity_model
from tdf_m33.models.tdf_regularization import (
    count_tau_gradient_spikes,
    gaussian_radius_smoothing,
    gradient_smoothness_metric,
)

FIG_CAVEAT = (
    "Phase 3D robustness audit only. K_τ is normalization. D1 PASS_WITH_CAVEAT. "
    "No lensing. Not a dark-matter disproof."
)

KNOT_SCALE_RTOL = 0.15


def load_phase3d_config(config_path: Path) -> dict[str, Any]:
    with config_path.open() as f:
        cfg = yaml.safe_load(f)
    tdf = cfg.get("tdf", {})
    sens = tdf.get("sensitivity", {})
    lp = tdf.get("low_parameter_model", {})
    return {
        "k_tau_values": [float(x) for x in sens.get("k_tau_values", [0.5, 1.0, 2.0])],
        "k_tau_sweep_knot_counts": [int(k) for k in sens.get("k_tau_sweep_knot_counts", [3, 4])],
        "gaussian_sigma_values_kpc": [
            float(x) for x in sens.get("gaussian_sigma_values_kpc", [0.5, 0.75, 1.0, 1.5])
        ],
        "fit_mask_variants": sens.get(
            "fit_mask_variants",
            [
                {"name": "corbelli_default", "min_kpc": 0.4, "max_kpc": 23.0},
                {"name": "stricter_0p5_22p5", "min_kpc": 0.5, "max_kpc": 22.5},
                {"name": "stricter_1p0_22p0", "min_kpc": 1.0, "max_kpc": 22.0},
            ],
        ),
        "fitmask_knot_count": int(sens.get("fitmask_knot_count", 3)),
        "default_fit_min_kpc": float(lp.get("fit_min_radius_kpc", 0.4)),
        "default_fit_max_kpc": float(lp.get("fit_max_radius_kpc", 23.0)),
        "tau0": float(tdf.get("tau0", 0.0)),
        "enforce_nonnegative_vtau2": bool(lp.get("enforce_nonnegative_vtau2", True)),
        "gradient_upper_bound": 1.0e5,
        "figure_dpi": int(cfg.get("plotting", {}).get("figure_dpi", 150)),
    }


def _fit_cfg(
    base: dict[str, Any],
    *,
    k_tau: float | None = None,
    fit_min: float | None = None,
    fit_max: float | None = None,
) -> dict[str, Any]:
    c = dict(base)
    if k_tau is not None:
        c["k_tau"] = k_tau
    if fit_min is not None:
        c["fit_min_radius_kpc"] = fit_min
    if fit_max is not None:
        c["fit_max_radius_kpc"] = fit_max
    return c


def metrics_from_arrays(
    model_name: str,
    v_obs: np.ndarray,
    v_model: np.ndarray,
    v_err: np.ndarray,
    mask: np.ndarray,
    k: int,
    k_tau: float,
    fit_min: float,
    fit_max: float,
    n_rows: int,
    *,
    knot_values: np.ndarray | None = None,
    extra: dict[str, Any] | None = None,
) -> dict[str, Any]:
    row = comparison_metrics(
        model_name,
        v_obs,
        v_model,
        v_err,
        k,
        fit_mask=mask,
        fit_r_min_kpc=fit_min,
        fit_r_max_kpc=fit_max,
        n_rows_total=n_rows,
    )
    m = row.metrics
    out: dict[str, Any] = {
        "model_name": model_name,
        "k_tau": k_tau,
        "parameter_count": k,
        "n_fit_points": row.n_fit_points,
        "dof": row.dof,
        "fit_r_min_kpc": fit_min,
        "fit_r_max_kpc": fit_max,
        "rmse_kms": m.rmse_kms,
        "chi_square": m.chi_square,
        "reduced_chi_square": m.reduced_chi_square,
        "aic": m.aic,
        "bic": m.bic,
        "n_negative_residual_v2": m.n_negative_residual_v2,
    }
    if knot_values is not None:
        out["knot_gradient_values"] = ";".join(f"{x:.6g}" for x in knot_values)
    if extra:
        out.update(extra)
    return out


def audit_knot_count_stability(
    phase3c_comparison_path: Path,
    combined_path: Path,
) -> tuple[pd.DataFrame, dict[str, Any]]:
    """Rank Phase 3C knot models; compare to NFW."""
    p3c = pd.read_csv(phase3c_comparison_path)
    combined = pd.read_csv(combined_path)
    nfw = combined[combined["model_name"] == "nfw"].iloc[0]

    tdf = p3c[p3c["model_name"].str.startswith("tdf_lowparam")].copy()
    best_aic = tdf.loc[tdf["aic"].idxmin()]
    best_bic = tdf.loc[tdf["bic"].idxmin()]
    best_rmse = tdf.loc[tdf["rmse_kms"].idxmin()]

    rows: list[dict[str, Any]] = []
    for _, r in tdf.iterrows():
        rows.append(
            {
                "audit_type": "knot_count_stability",
                "model_name": r["model_name"],
                "parameter_count": int(r["parameter_count"]),
                "rmse_kms": r["rmse_kms"],
                "chi_square": r["chi_square"],
                "aic": r["aic"],
                "bic": r["bic"],
                "best_by_aic": r["model_name"] == best_aic["model_name"],
                "best_by_bic": r["model_name"] == best_bic["model_name"],
                "best_by_rmse": r["model_name"] == best_rmse["model_name"],
                "nfw_aic": float(nfw["aic"]),
                "nfw_bic": float(nfw["bic"]),
                "nfw_rmse_kms": float(nfw["rmse_kms"]),
                "tdf_aic_beats_nfw": r["aic"] < nfw["aic"],
                "tdf_bic_beats_nfw": r["bic"] < nfw["bic"],
                "notes": "Phase 3C knot-count comparison on Corbelli mask; not DM disproof.",
            }
        )

    meta = {
        "best_tdf_aic_model": best_aic["model_name"],
        "best_tdf_bic_model": best_bic["model_name"],
        "best_tdf_rmse_model": best_rmse["model_name"],
        "nfw_aic": float(nfw["aic"]),
        "nfw_bic": float(nfw["bic"]),
        "three_knot_aic_beats_nfw": bool(
            tdf[tdf["model_name"] == "tdf_lowparam_3knot"]["aic"].iloc[0] < nfw["aic"]
        ),
        "three_knot_bic_beats_nfw": bool(
            tdf[tdf["model_name"] == "tdf_lowparam_3knot"]["bic"].iloc[0] < nfw["bic"]
        ),
    }
    return pd.DataFrame(rows), meta


def audit_k_tau_sweep(
    prof: pd.DataFrame,
    r: np.ndarray,
    v_obs: np.ndarray,
    v_err: np.ndarray,
    v_bar: np.ndarray,
    mask_default: np.ndarray,
    cfg3c: dict[str, Any],
    cfg3d: dict[str, Any],
    phase3a_path: Path | None,
) -> tuple[pd.DataFrame, dict[str, Any]]:
    """Refit 3- and 4-knot models at multiple K_τ values."""
    rows: list[dict[str, Any]] = []
    fits_by_key: dict[tuple[int, float], Any] = {}

    fit_min = cfg3d["default_fit_min_kpc"]
    fit_max = cfg3d["default_fit_max_kpc"]
    n_rows = len(prof)

    for k_tau in cfg3d["k_tau_values"]:
        for knot_count in cfg3d["k_tau_sweep_knot_counts"]:
            fcfg = _fit_cfg(
                cfg3c,
                k_tau=k_tau,
                fit_min=fit_min,
                fit_max=fit_max,
            )
            # phase3a_path=None → Δv²/(r K_τ) initial guess at each K_τ
            fit = fit_lowparam_knot_model(
                r,
                v_obs,
                v_err,
                v_bar,
                knot_count,
                fcfg,
                fit_mask=mask_default,
                phase3a_path=None,
            )
            fits_by_key[(knot_count, k_tau)] = fit
            rows.append(
                metrics_from_arrays(
                    f"tdf_lowparam_{knot_count}knot_k{k_tau:g}",
                    v_obs,
                    fit.v_model_kms,
                    v_err,
                    mask_default,
                    knot_count,
                    k_tau,
                    fit_min,
                    fit_max,
                    n_rows,
                    knot_values=fit.knot_values,
                    extra={
                        "audit_type": "k_tau_sweep",
                        "knot_count": knot_count,
                        "notes": "K_τ normalization sweep; velocity metrics test scale degeneracy.",
                    },
                )
            )

    # Scale-degeneracy diagnostics: compare metrics at k=1 vs others
    rmse_vals = [row["rmse_kms"] for row in rows]
    chi2_vals = [row["chi_square"] for row in rows]
    max_rmse_spread = float(np.max(rmse_vals) - np.min(rmse_vals))
    max_chi2_spread = float(np.max(chi2_vals) - np.min(chi2_vals))
    velocity_metrics_stable = max_rmse_spread < 1.0 and max_chi2_spread < 2.0

    scale_checks: list[str] = []
    knot_scaling_matches: list[bool] = []
    ref_fit = fits_by_key.get((3, 1.0))
    for k_tau in cfg3d["k_tau_values"]:
        if k_tau == 1.0:
            continue
        f = fits_by_key[(3, k_tau)]
        if ref_fit is not None:
            ratio = f.knot_values / ref_fit.knot_values
            med_ratio = float(np.median(ratio))
            expected = 1.0 / k_tau
            knot_scaling_matches.append(
                abs(med_ratio - expected) < KNOT_SCALE_RTOL * expected + 0.05
            )
            scale_checks.append(
                f"k=3, K_tau={k_tau}: median knot ratio vs K_tau=1 is {med_ratio:.3f} "
                f"(expected ~{expected:.3f} if scale degeneracy)"
            )

    meta = {
        "velocity_metrics_stable": velocity_metrics_stable,
        "max_rmse_spread_kms": max_rmse_spread,
        "max_chi2_spread": max_chi2_spread,
        "k_tau_knot_scaling_degeneracy": all(knot_scaling_matches)
        if knot_scaling_matches
        else False,
        "scale_ratio_notes": "; ".join(scale_checks),
    }
    return pd.DataFrame(rows), meta


def audit_smoothing_sensitivity(
    phase3a_df: pd.DataFrame,
    cfg3d: dict[str, Any],
) -> pd.DataFrame:
    """Gaussian σ sweep on Phase 3A raw gradient (diagnostic only)."""
    r = phase3a_df["r_kpc"].to_numpy(dtype=float)
    grad_raw = phase3a_df["tau_gradient_raw"].to_numpy(dtype=float)
    v_obs = phase3a_df["v_obs_kms"].to_numpy(dtype=float)
    v_bar = phase3a_df["v_bar_kms"].to_numpy(dtype=float)
    k_tau = 1.0
    mask = fit_radius_mask(
        r, cfg3d["default_fit_min_kpc"], cfg3d["default_fit_max_kpc"]
    )

    rows: list[dict[str, Any]] = []
    for sigma in cfg3d["gaussian_sigma_values_kpc"]:
        grad_s = gaussian_radius_smoothing(r, grad_raw, sigma)
        v_mod, v_tau2, neg = tdf_velocity_model(v_bar, r, grad_s, k_tau)
        spikes, _ = count_tau_gradient_spikes(r, grad_s)
        err = v_mod - v_obs
        err_m = err[mask & np.isfinite(v_mod)]
        rows.append(
            {
                "audit_type": "gaussian_smoothing",
                "sigma_kpc": sigma,
                "k_tau": k_tau,
                "gradient_spike_count": spikes,
                "gradient_smoothness_metric": gradient_smoothness_metric(r, grad_s),
                "reconstruction_rmse_kms": float(np.sqrt(np.mean(err_m**2))),
                "n_negative_vtau2": int(neg.sum()),
                "notes": "Phase 3B diagnostic; not AIC/BIC formal comparison.",
            }
        )
    return pd.DataFrame(rows)


def audit_fitmask_sensitivity(
    prof: pd.DataFrame,
    r: np.ndarray,
    v_obs: np.ndarray,
    v_err: np.ndarray,
    v_bar: np.ndarray,
    cfg3c: dict[str, Any],
    cfg3d: dict[str, Any],
    phase3a_path: Path | None,
) -> pd.DataFrame:
    """Refit 3-knot model under alternate fit masks."""
    rows: list[dict[str, Any]] = []
    knot_count = cfg3d["fitmask_knot_count"]
    n_rows = len(prof)

    for variant in cfg3d["fit_mask_variants"]:
        name = str(variant["name"])
        fit_min = float(variant["min_kpc"])
        fit_max = float(variant["max_kpc"])
        mask = fit_radius_mask(r, fit_min, fit_max)
        fcfg = _fit_cfg(cfg3c, fit_min=fit_min, fit_max=fit_max)
        fit = fit_lowparam_knot_model(
            r,
            v_obs,
            v_err,
            v_bar,
            knot_count,
            fcfg,
            fit_mask=mask,
            phase3a_path=phase3a_path,
        )
        rows.append(
            metrics_from_arrays(
                f"tdf_lowparam_{knot_count}knot_{name}",
                v_obs,
                fit.v_model_kms,
                v_err,
                mask,
                knot_count,
                fcfg["k_tau"],
                fit_min,
                fit_max,
                n_rows,
                knot_values=fit.knot_values,
                extra={
                    "audit_type": "fit_mask_sensitivity",
                    "mask_name": name,
                    "n_fit_points": int(mask.sum()),
                    "notes": "3-knot refit under alternate mask; ranking stability check.",
                },
            )
        )
    return pd.DataFrame(rows)


def build_sensitivity_summary(
    knot_df: pd.DataFrame,
    ktau_df: pd.DataFrame,
    smooth_df: pd.DataFrame,
    mask_df: pd.DataFrame,
    knot_meta: dict[str, Any],
    ktau_meta: dict[str, Any],
    combined_path: Path,
) -> pd.DataFrame:
    """High-level summary rows for all audits."""
    nfw = pd.read_csv(combined_path)
    nfw_row = nfw[nfw["model_name"] == "nfw"].iloc[0]
    rows: list[dict[str, Any]] = [
        {
            "audit_type": "summary",
            "check_name": "best_tdf_by_aic",
            "value": knot_meta["best_tdf_aic_model"],
            "detail": f"NFW AIC={nfw_row['aic']:.2f}",
        },
        {
            "audit_type": "summary",
            "check_name": "best_tdf_by_bic",
            "value": knot_meta["best_tdf_bic_model"],
            "detail": f"NFW BIC={nfw_row['bic']:.2f}",
        },
        {
            "audit_type": "summary",
            "check_name": "tdf_3knot_aic_beats_nfw",
            "value": str(knot_meta["three_knot_aic_beats_nfw"]),
            "detail": "Qualify: rotation-only; D1 baryonic caveat.",
        },
        {
            "audit_type": "summary",
            "check_name": "k_tau_velocity_metrics_stable",
            "value": str(ktau_meta["velocity_metrics_stable"]),
            "detail": f"max RMSE spread={ktau_meta['max_rmse_spread_kms']:.4f} km/s across sweep",
        },
        {
            "audit_type": "summary",
            "check_name": "k_tau_knot_scaling_degeneracy",
            "value": str(ktau_meta["k_tau_knot_scaling_degeneracy"]),
            "detail": ktau_meta.get("scale_ratio_notes", ""),
        },
        {
            "audit_type": "summary",
            "check_name": "smoothing_sigma_range_rmse",
            "value": f"{smooth_df['reconstruction_rmse_kms'].min():.2f}–{smooth_df['reconstruction_rmse_kms'].max():.2f} km/s",
            "detail": "Diagnostic only; not AIC/BIC.",
        },
        {
            "audit_type": "summary",
            "check_name": "fitmask_3knot_aic_range",
            "value": f"{mask_df['aic'].min():.1f}–{mask_df['aic'].max():.1f}",
            "detail": "Mask names: " + ", ".join(mask_df["mask_name"].astype(str)),
        },
        {
            "audit_type": "summary",
            "check_name": "lensing_tested",
            "value": "false",
            "detail": "Rotation dynamics only.",
        },
        {
            "audit_type": "summary",
            "check_name": "dark_matter_disproven",
            "value": "false",
            "detail": "Robustness audit only; NFW remains ΛCDM reference.",
        },
    ]
    return pd.DataFrame(rows)


def render_sensitivity_report(
    knot_meta: dict[str, Any],
    ktau_meta: dict[str, Any],
    knot_df: pd.DataFrame,
    ktau_df: pd.DataFrame,
    smooth_df: pd.DataFrame,
    mask_df: pd.DataFrame,
    summary_df: pd.DataFrame,
) -> str:
    """Markdown report for Phase 3D."""
    lines = [
        "# Phase 3D — TDF sensitivity and robustness audit (M33)",
        "",
        "**Scope:** Robustness audit only—not new physical evidence. "
        "Baryonic velocities are D1-derived (`PASS_WITH_CAVEAT`). "
        "**No lensing** predictions. **No claim** that dark matter is disproven.",
        "",
        "Phase 3C is the first fair low-parameter AIC/BIC TDF comparison. "
        "Phase 3A (direct) and Phase 3B-A (smoothed) are not formal competitors.",
        "",
        "## A. Knot-count stability (Phase 3C)",
        "",
        f"- Best TDF by **AIC:** `{knot_meta['best_tdf_aic_model']}` "
        f"(NFW AIC ≈ {knot_meta['nfw_aic']:.1f})",
        f"- Best TDF by **BIC:** `{knot_meta['best_tdf_bic_model']}` "
        f"(NFW BIC ≈ {knot_meta['nfw_bic']:.1f})",
        f"- Best TDF by **RMSE:** `{knot_meta['best_tdf_rmse_model']}`",
        f"- 3-knot AIC beats NFW: **{knot_meta['three_knot_aic_beats_nfw']}**",
        f"- 3-knot BIC beats NFW: **{knot_meta['three_knot_bic_beats_nfw']}**",
        "",
        "5-knot achieves lowest RMSE/χ² but pays a higher parameter penalty in AIC/BIC.",
        "",
        "## B. K_τ normalization sweep",
        "",
        "K_τ is a **project-unit normalization**, not an independently calibrated constant. "
        "With knot values refit at each K_τ, **v_τ² = r K_τ dτ/dr** can absorb much of the "
        "K_τ scaling in the fitted gradient.",
        "",
        f"- Velocity metrics stable across K_τ (RMSE spread < 1 km/s): "
        f"**{ktau_meta['velocity_metrics_stable']}**",
        f"- Knot values scale ≈ 1/K_τ when refit (scale degeneracy): "
        f"**{ktau_meta['k_tau_knot_scaling_degeneracy']}**",
        f"- Max RMSE spread across sweep: **{ktau_meta['max_rmse_spread_kms']:.4f} km/s**",
        f"- Max χ² spread: **{ktau_meta['max_chi2_spread']:.2f}**",
        "",
    ]
    if ktau_meta.get("scale_ratio_notes"):
        lines.append(f"- Knot scaling notes: {ktau_meta['scale_ratio_notes']}")
    lines.extend(
        [
            "",
            "## C. Gaussian smoothing sensitivity (Phase 3B diagnostic)",
            "",
            "Not included in formal AIC/BIC. σ_kpc affects spike count, smoothness, and RMSE:",
            "",
        ]
    )
    for _, row in smooth_df.iterrows():
        lines.append(
            f"- σ = {row['sigma_kpc']} kpc: spikes={int(row['gradient_spike_count'])}, "
            f"smoothness={row['gradient_smoothness_metric']:.2g}, "
            f"RMSE={row['reconstruction_rmse_kms']:.2f} km/s, "
            f"neg v_τ²={int(row['n_negative_vtau2'])}"
        )
    lines.extend(
        [
            "",
            "## D. Fit-mask sensitivity (3-knot refit)",
            "",
        ]
    )
    for _, row in mask_df.iterrows():
        lines.append(
            f"- **{row['mask_name']}** ({row['fit_r_min_kpc']}–{row['fit_r_max_kpc']} kpc, "
            f"n={int(row['n_fit_points'])}): AIC={row['aic']:.1f}, BIC={row['bic']:.1f}, "
            f"RMSE={row['rmse_kms']:.2f} km/s"
        )
    lines.extend(
        [
            "",
            "## Stability conclusion",
            "",
            "- **3-knot vs NFW on AIC** is the primary fair comparison row; verify fragility "
            "via mask and K_τ audits above.",
            "- **Burkert** remains boundary-limited (r₀ ≈ 200 kpc); do not over-interpret.",
            "- **Phase 4** (2D τ-map) should proceed only if radial ranking is acceptably "
            "stable under mask variants and K_τ is documented as normalization.",
            "- **Phase 5** lensing consistency remains future work.",
            "",
            "## Claim control",
            "",
            "Do not state that TDF beats dark matter or replaces NFW without qualification. "
            "Rotation-curve comparison on one galaxy with derived baryons is insufficient "
            "for cosmological claims.",
            "",
        ]
    )
    return "\n".join(lines)


def _plot_sensitivity_summary(
    knot_df: pd.DataFrame,
    ktau_df: pd.DataFrame,
    smooth_df: pd.DataFrame,
    mask_df: pd.DataFrame,
    combined_path: Path,
    out_path: Path,
    dpi: int,
) -> None:
    combined = pd.read_csv(combined_path)
    fig, axes = plt.subplots(2, 2, figsize=(10, 8))

    # AIC comparison TDF + NFW
    ax = axes[0, 0]
    plot_models = combined[
        combined["model_name"].isin(
            [
                "nfw",
                "tdf_lowparam_3knot",
                "tdf_lowparam_4knot",
                "tdf_lowparam_5knot",
            ]
        )
    ]
    ax.bar(plot_models["model_name"], plot_models["aic"], color="steelblue")
    ax.set_ylabel("AIC")
    ax.set_title("AIC on fit mask")
    ax.tick_params(axis="x", rotation=25, labelsize=7)

    # K_tau RMSE 3-knot
    ax = axes[0, 1]
    k3 = ktau_df[ktau_df["knot_count"] == 3]
    ax.plot(k3["k_tau"], k3["rmse_kms"], "o-", label="3-knot")
    k4 = ktau_df[ktau_df["knot_count"] == 4]
    ax.plot(k4["k_tau"], k4["rmse_kms"], "s--", label="4-knot")
    ax.set_xlabel(r"$K_\tau$")
    ax.set_ylabel("RMSE [km/s]")
    ax.set_title(r"$K_\tau$ sweep (velocity metrics)")
    ax.legend(fontsize=8)

    # Smoothing
    ax = axes[1, 0]
    ax.plot(
        smooth_df["sigma_kpc"],
        smooth_df["reconstruction_rmse_kms"],
        "o-",
        color="C2",
    )
    ax.set_xlabel(r"$\sigma$ [kpc]")
    ax.set_ylabel("RMSE [km/s]")
    ax.set_title("Gaussian σ (diagnostic)")

    # Fit mask AIC
    ax = axes[1, 1]
    ax.bar(mask_df["mask_name"].astype(str), mask_df["aic"], color="C4")
    ax.set_ylabel("AIC")
    ax.set_title("3-knot fit-mask sensitivity")
    ax.tick_params(axis="x", rotation=20, labelsize=7)

    fig.suptitle("Phase 3D — TDF sensitivity audit", fontsize=11)
    fig.text(0.5, 0.01, FIG_CAVEAT, ha="center", fontsize=7)
    fig.tight_layout(rect=[0, 0.03, 1, 0.96])
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, dpi=dpi)
    plt.close(fig)


def run_phase3d_tdf_sensitivity(
    processed_path: Path,
    config_path: Path,
    phase3c_comparison_path: Path,
    phase3a_path: Path,
    combined_path: Path,
    summary_path: Path,
    ktau_path: Path,
    mask_path: Path,
    smooth_path: Path,
    report_path: Path,
    fig_path: Path,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Run all Phase 3D audits and write outputs."""
    cfg3d = load_phase3d_config(config_path)
    cfg3c = load_phase3c_config(config_path)

    ds = load_m33_rotation_dataset(processed_path)
    prof = build_baryonic_profile(ds.data.sort_values("r_kpc"))
    r = prof["r_kpc"].to_numpy(dtype=float)
    v_obs = prof["v_obs_kms"].to_numpy(dtype=float)
    v_err = prof["v_err_kms"].to_numpy(dtype=float)
    v_bar = prof["v_bar_kms"].to_numpy(dtype=float)
    mask_default = fit_radius_mask(
        r, cfg3d["default_fit_min_kpc"], cfg3d["default_fit_max_kpc"]
    )

    p3a = pd.read_csv(phase3a_path).sort_values("r_kpc")

    knot_df, knot_meta = audit_knot_count_stability(
        phase3c_comparison_path, combined_path
    )
    ktau_df, ktau_meta = audit_k_tau_sweep(
        prof,
        r,
        v_obs,
        v_err,
        v_bar,
        mask_default,
        cfg3c,
        cfg3d,
        phase3a_path if phase3a_path.is_file() else None,
    )
    smooth_df = audit_smoothing_sensitivity(p3a, cfg3d)
    mask_df = audit_fitmask_sensitivity(
        prof,
        r,
        v_obs,
        v_err,
        v_bar,
        cfg3c,
        cfg3d,
        phase3a_path if phase3a_path.is_file() else None,
    )
    summary_df = build_sensitivity_summary(
        knot_df, ktau_df, smooth_df, mask_df, knot_meta, ktau_meta, combined_path
    )
    report_md = render_sensitivity_report(
        knot_meta, ktau_meta, knot_df, ktau_df, smooth_df, mask_df, summary_df
    )

    for p in (summary_path, ktau_path, mask_path, smooth_path, report_path):
        p.parent.mkdir(parents=True, exist_ok=True)
    summary_df.to_csv(summary_path, index=False)
    ktau_df.to_csv(ktau_path, index=False)
    mask_df.to_csv(mask_path, index=False)
    smooth_df.to_csv(smooth_path, index=False)
    report_path.write_text(report_md, encoding="utf-8")

    _plot_sensitivity_summary(
        knot_df, ktau_df, smooth_df, mask_df, combined_path, fig_path, cfg3d["figure_dpi"]
    )

    return summary_df, ktau_df, mask_df, smooth_df, knot_df
