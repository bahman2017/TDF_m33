"""Phase 3A: direct pointwise TDF τ-gradient reconstruction from baryonic Δv²."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import yaml

from tdf_m33.data.m33_dataset import load_m33_rotation_dataset
from tdf_m33.fitting.halo_fit import FitRadiusMask
from tdf_m33.models.baryonic import build_baryonic_profile
from tdf_m33.models.tdf_radial import (
    compute_tau_gradient,
    compute_v_tau_squared_from_gradient,
    count_gradient_spikes,
    delta_v2_sign_flags,
    integrate_tau_profile,
)

FIG_CAVEAT = (
    "Phase 3A: direct pointwise τ from baryonic Δv² (D1 PASS_WITH_CAVEAT). "
    "Not smoothed; not a halo fit. K_τ=1 is normalization only. No lensing."
)

DIAGNOSTICS_NOTES = (
    "Direct pointwise reconstruction: v_tdf = sqrt(v_bar² + r K_τ dτ/dr) with "
    "dτ/dr = Δv²/(r K_τ) and Δv² = v_obs² − v_bar². This is an algebraic identity "
    "check, not an independent predictive fit. AIC/BIC are not meaningful here; "
    "formal model comparison deferred to Phase 3B/3C regularized τ models."
)


def load_tdf_config(config_path: Path) -> dict[str, Any]:
    with config_path.open() as f:
        cfg = yaml.safe_load(f)
    tdf = cfg.get("tdf", {})
    hf = cfg.get("halo_fitting", {})
    return {
        "k_tau": float(tdf.get("k_tau", 1.0)),
        "tau0": float(tdf.get("tau0", 0.0)),
        "reconstruction_mode": str(tdf.get("reconstruction_mode", "direct_pointwise")),
        "input_residual": str(tdf.get("input_residual", "baryonic_only_delta_v2")),
        "use_fit_mask_for_summary": bool(tdf.get("use_fit_mask_for_summary", True)),
        "fit_min_radius_kpc": float(hf.get("fit_min_radius_kpc", 0.4)),
        "fit_max_radius_kpc": float(hf.get("fit_max_radius_kpc", 23.0)),
        "figure_dpi": int(cfg.get("plotting", {}).get("figure_dpi", 150)),
    }


def load_phase3a_input(
    readiness_path: Path,
    processed_path: Path | None,
    phase2a_profile_path: Path | None,
) -> pd.DataFrame:
    """
    Build input table with baryonic Δv² and kinematics.

    Prefers phase2c_residual_readiness.csv for Δv²; merges v_obs/v_bar from
    phase2a profile or recomputes from processed CSV.
    """
    if not readiness_path.is_file():
        raise FileNotFoundError(f"Residual readiness table missing: {readiness_path}")

    ready = pd.read_csv(readiness_path).sort_values("r_kpc")

    if phase2a_profile_path is not None and phase2a_profile_path.is_file():
        p2a = pd.read_csv(phase2a_profile_path).sort_values("r_kpc")
        kin_cols = [
            "r_kpc",
            "v_obs_kms",
            "v_err_kms",
            "v_bar_kms",
            "galaxy_id",
            "source_id",
            "data_quality_flag",
            "notes",
        ]
        kin = p2a[[c for c in kin_cols if c in p2a.columns]]
        merged = ready.merge(kin, on="r_kpc", how="left")
        if "residual_v2_kms2" in p2a.columns:
            p2a_dv2 = (
                p2a.sort_values("r_kpc")
                .set_index("r_kpc")["residual_v2_kms2"]
                .reindex(merged["r_kpc"])
                .to_numpy()
            )
            if not np.allclose(
                merged["delta_v2_kms2"].to_numpy(),
                p2a_dv2,
                rtol=0,
                atol=1e-6,
            ):
                raise ValueError(
                    "delta_v2_kms2 in readiness CSV disagrees with Phase 2A profile"
                )
    elif processed_path is not None and processed_path.is_file():
        ds = load_m33_rotation_dataset(processed_path)
        prof = build_baryonic_profile(ds.data).sort_values("r_kpc")
        merged = ready.merge(
            prof[
                [
                    "r_kpc",
                    "v_obs_kms",
                    "v_err_kms",
                    "v_bar_kms",
                    "residual_v2_kms2",
                    "galaxy_id",
                    "source_id",
                    "data_quality_flag",
                    "notes",
                ]
            ],
            on="r_kpc",
            how="left",
        )
        if not np.allclose(
            merged["delta_v2_kms2"].to_numpy(),
            merged["residual_v2_kms2"].to_numpy(),
            rtol=0,
            atol=1e-6,
        ):
            raise ValueError("Recomputed Δv² disagrees with readiness table")
    else:
        raise FileNotFoundError(
            "Need phase2a profile or processed CSV to attach v_obs and v_bar"
        )

    for col in ("v_obs_kms", "v_bar_kms"):
        if merged[col].isna().any():
            raise ValueError(f"Missing kinematic column after merge: {col}")

    return merged.sort_values("r_kpc").reset_index(drop=True)


def reconstruct_tdf_radial_direct(
    df: pd.DataFrame,
    k_tau: float,
    tau0: float = 0.0,
) -> pd.DataFrame:
    """Pointwise τ gradient, profile, and direct TDF velocity reconstruction."""
    r = df["r_kpc"].to_numpy(dtype=float)
    dv2 = df["delta_v2_kms2"].to_numpy(dtype=float)
    v_bar = df["v_bar_kms"].to_numpy(dtype=float)

    tau_grad = compute_tau_gradient(r, dv2, k_tau)
    tau_raw = integrate_tau_profile(r, tau_grad, tau0=tau0)
    v_tau2 = compute_v_tau_squared_from_gradient(r, tau_grad, k_tau)
    v_tau = np.sqrt(np.maximum(v_tau2, 0.0))
    v_tdf = np.sqrt(np.maximum(v_bar**2 + v_tau2, 0.0))
    v_obs = df["v_obs_kms"].to_numpy(dtype=float)
    recon_err = v_tdf - v_obs

    sign_flags = delta_v2_sign_flags(dv2)
    n_spikes, spike_mask = count_gradient_spikes(r, dv2)

    out = df.copy()
    out["delta_v2_sign_flag"] = sign_flags
    out["tau_gradient_raw"] = tau_grad
    out["tau_raw"] = tau_raw
    out["v_tau_squared_reconstructed"] = v_tau2
    out["v_tau_kms"] = v_tau
    out["v_tdf_direct_kms"] = v_tdf
    out["reconstruction_error_kms"] = recon_err
    out["gradient_spike_flag"] = spike_mask
    out["k_tau_used"] = k_tau
    out["tau0_used"] = tau0
    out.attrs["gradient_spike_count"] = n_spikes
    return out


def build_diagnostics(
    profile: pd.DataFrame,
    cfg: dict[str, Any],
) -> pd.DataFrame:
    """Single-row diagnostics for Phase 3A direct reconstruction."""
    err = profile["reconstruction_error_kms"].to_numpy(dtype=float)
    dv2 = profile["delta_v2_kms2"].to_numpy(dtype=float)
    n_neg = int(np.sum(dv2 < -1.0e-6))
    n_spikes = int(profile.attrs.get("gradient_spike_count", profile["gradient_spike_flag"].sum()))

    mask = np.ones(len(profile), dtype=bool)
    if cfg["use_fit_mask_for_summary"]:
        fit_mask = FitRadiusMask(
            cfg["fit_min_radius_kpc"],
            cfg["fit_max_radius_kpc"],
        )
        mask = fit_mask.mask(profile["r_kpc"].to_numpy())

    err_m = err[mask]
    rmse = float(np.sqrt(np.mean(err_m**2))) if err_m.size else float("nan")
    max_abs = float(np.max(np.abs(err_m))) if err_m.size else float("nan")

    row = {
        "k_tau": cfg["k_tau"],
        "tau0": cfg["tau0"],
        "reconstruction_mode": cfg["reconstruction_mode"],
        "input_residual": cfg["input_residual"],
        "n_rows": len(profile),
        "n_fit_mask_rows": int(mask.sum()) if cfg["use_fit_mask_for_summary"] else len(profile),
        "fit_r_min_kpc": cfg["fit_min_radius_kpc"] if cfg["use_fit_mask_for_summary"] else np.nan,
        "fit_r_max_kpc": cfg["fit_max_radius_kpc"] if cfg["use_fit_mask_for_summary"] else np.nan,
        "n_negative_delta_v2": n_neg,
        "max_abs_reconstruction_error_kms": max_abs,
        "rmse_reconstruction_error_kms": rmse,
        "gradient_spike_count": n_spikes,
        "is_fitted_model_comparison": False,
        "aic_bic_meaningful": False,
        "uses_nfw_burkert_residual": False,
        "tau_smoothing_applied": False,
        "notes": DIAGNOSTICS_NOTES,
        "smoothness_warning": (
            f"{n_spikes} gradient spikes on raw Δv²; Phase 3B smoothing/regularization "
            "recommended before interpreting τ(r)."
            if n_spikes > 0
            else "No heuristic spikes; still unsmoothed pointwise τ."
        ),
    }
    return pd.DataFrame([row])


def _plot_tau_gradient(profile: pd.DataFrame, out_path: Path, dpi: int) -> None:
    r = profile["r_kpc"]
    fig, ax = plt.subplots(figsize=(8, 4.5))
    ax.plot(r, profile["tau_gradient_raw"], "C1-", lw=1.5, label=r"$d\tau/dr$ (raw)")
    ax.axhline(0, color="gray", ls="--", lw=0.8)
    spikes = profile["gradient_spike_flag"]
    if spikes.any():
        ax.scatter(
            r[spikes],
            profile.loc[spikes, "tau_gradient_raw"],
            c="red",
            s=30,
            zorder=5,
            label="Δv² gradient spike",
        )
    ax.set_xlabel(r"$R$ [kpc]")
    ax.set_ylabel(r"$d\tau/dr$ [project units]")
    ax.set_title("Phase 3A — raw τ gradient (unsmoothed)")
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.3)
    fig.text(0.5, 0.01, FIG_CAVEAT, ha="center", fontsize=7)
    fig.tight_layout(rect=[0, 0.04, 1, 1])
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, dpi=dpi)
    plt.close(fig)


def _plot_tau_profile(profile: pd.DataFrame, out_path: Path, dpi: int) -> None:
    r = profile["r_kpc"]
    fig, ax = plt.subplots(figsize=(8, 4.5))
    ax.plot(r, profile["tau_raw"], "C4-", lw=1.5, label=r"$\tau(r)$, $\tau(r_{\min})=0$")
    ax.set_xlabel(r"$R$ [kpc]")
    ax.set_ylabel(r"$\tau$ [arb. offset]")
    ax.set_title("Phase 3A — integrated τ profile (additive offset arbitrary)")
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.3)
    fig.text(0.5, 0.01, FIG_CAVEAT, ha="center", fontsize=7)
    fig.tight_layout(rect=[0, 0.04, 1, 1])
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, dpi=dpi)
    plt.close(fig)


def _plot_reconstruction_check(profile: pd.DataFrame, out_path: Path, dpi: int) -> None:
    r = profile["r_kpc"]
    fig, ax = plt.subplots(figsize=(8, 5))
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
    ax.plot(r, profile["v_bar_kms"], "b--", label=r"$v_{\mathrm{bar}}$ (D1)")
    ax.plot(r, profile["v_tdf_direct_kms"], "g-", lw=1.8, label=r"$v_{\mathrm{TDF,direct}}$")
    ax.set_xlabel(r"$R$ [kpc]")
    ax.set_ylabel(r"$V$ [km s$^{-1}$]")
    ax.set_title("Phase 3A — direct TDF reconstruction check")
    ax.legend(loc="lower right", fontsize=8)
    ax.grid(True, alpha=0.3)
    inset = ax.inset_axes([0.55, 0.55, 0.42, 0.38])
    inset.plot(r, profile["reconstruction_error_kms"], "r-", lw=1)
    inset.axhline(0, color="gray", ls="--", lw=0.6)
    inset.set_ylabel(r"$\Delta v$ [km/s]", fontsize=7)
    inset.set_xlabel(r"$R$ [kpc]", fontsize=7)
    inset.tick_params(labelsize=6)
    inset.set_title("recon. error", fontsize=7)
    fig.text(0.5, 0.01, FIG_CAVEAT, ha="center", fontsize=7)
    fig.tight_layout(rect=[0, 0.04, 1, 1])
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, dpi=dpi)
    plt.close(fig)


def run_phase3a_tdf_radial(
    readiness_path: Path,
    config_path: Path,
    reconstruction_path: Path,
    diagnostics_path: Path,
    fig_gradient: Path,
    fig_tau: Path,
    fig_check: Path,
    processed_path: Path | None = None,
    phase2a_profile_path: Path | None = None,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Run Phase 3A pipeline and write outputs."""
    cfg = load_tdf_config(config_path)
    if cfg["input_residual"] != "baryonic_only_delta_v2":
        raise ValueError(
            f"Phase 3A requires baryonic_only_delta_v2 input; got {cfg['input_residual']}"
        )

    inp = load_phase3a_input(readiness_path, processed_path, phase2a_profile_path)
    profile = reconstruct_tdf_radial_direct(inp, cfg["k_tau"], tau0=cfg["tau0"])
    diag = build_diagnostics(profile, cfg)

    reconstruction_path.parent.mkdir(parents=True, exist_ok=True)
    profile.to_csv(reconstruction_path, index=False)
    diagnostics_path.parent.mkdir(parents=True, exist_ok=True)
    diag.to_csv(diagnostics_path, index=False)

    dpi = cfg["figure_dpi"]
    _plot_tau_gradient(profile, fig_gradient, dpi)
    _plot_tau_profile(profile, fig_tau, dpi)
    _plot_reconstruction_check(profile, fig_check, dpi)

    return profile, diag
