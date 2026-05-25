"""Phase 5C-B: dynamical upper-bound consistency (enclosed-mass proxy vs López Fune 2017)."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import yaml

from tdf_m33.constants import G_KPC
from tdf_m33.lensing.lopez_fune_2017_extraction import PARAMS_CSV, SOURCE_ID

REQUIRED_SOURCE_MODEL = "tdf_lowparam_3knot"
DEFAULT_PROFILES_CSV = "outputs/tables/phase3c_tdf_lowparam_profiles.csv"
DEFAULT_PARAMS_CSV = PARAMS_CSV
DEFAULT_TARGET_RADIUS_KPC = 23.0
LOPEZ_MODEL_LABEL = "burkert_local_density"
LOPEZ_PARAM_NAME = "M_enclosed_23kpc"

FIG_CAVEAT = (
    "Phase 5C-B: effective Newtonian-equivalent τ mass proxy vs López Fune 2017 "
    "dynamical upper bound — not weak lensing; not DM replacement; normalized_proxy deflection unchanged."
)

CIRCULARITY_NOTE = (
    "López Fune et al. 2017 uses Corbelli et al. 2014 baryonic/rotation inputs; "
    "partial circularity with this TDF branch. Dynamics/rotation-based reference only."
)


def load_phase5c_config(config_path: Path) -> dict[str, Any]:
    with config_path.open() as f:
        cfg = yaml.safe_load(f)
    tdf = cfg.get("tdf", {})
    lens = tdf.get("lensing", {})
    lp = tdf.get("low_parameter_model", {})
    limits = lens.get("observational_limits", {})
    repo = config_path.resolve().parents[1]
    profiles = Path(lens.get("phase3c_profiles_csv", DEFAULT_PROFILES_CSV))
    if not profiles.is_absolute():
        profiles = repo / profiles
    params_csv = Path(limits.get("lopez_fune_2017", {}).get("parameters_csv", DEFAULT_PARAMS_CSV))
    if not params_csv.is_absolute():
        params_csv = repo / params_csv
    return {
        "repo_root": repo,
        "source_model": str(lens.get("source_model", REQUIRED_SOURCE_MODEL)),
        "k_tau": float(lp.get("k_tau", tdf.get("k_tau", 1.0))),
        "profiles_csv": profiles,
        "params_csv": params_csv,
        "observational_limits_enabled": bool(limits.get("enabled", False)),
        "units": str(lens.get("units", "normalized_proxy")),
        "physical_calibration_enabled": bool(
            lens.get("physical_calibration", {}).get("enabled", False)
        ),
        "target_radius_kpc": float(
            limits.get("upper_bound_target_radius_kpc", DEFAULT_TARGET_RADIUS_KPC)
        ),
        "figure_dpi": int(cfg.get("plotting", {}).get("figure_dpi", 150)),
    }


def compute_effective_tau_mass_proxy(
    r_kpc: np.ndarray,
    v_tau_squared_kms2: np.ndarray,
    *,
    g_kpc: float = G_KPC,
) -> np.ndarray:
    """Newtonian-equivalent enclosed mass proxy M_eff(<r) = r v_tau^2 / G (not DM mass)."""
    r = np.asarray(r_kpc, dtype=float)
    v2 = np.asarray(v_tau_squared_kms2, dtype=float)
    if r.shape != v2.shape:
        raise ValueError("r_kpc and v_tau_squared_kms2 must have the same shape")
    if np.any(r <= 0):
        raise ValueError("r_kpc must be positive for mass proxy")
    return r * v2 / g_kpc


def load_phase3c_tdf_profile(
    profiles_csv: Path,
    *,
    source_model: str = REQUIRED_SOURCE_MODEL,
) -> pd.DataFrame:
    if not profiles_csv.is_file():
        raise FileNotFoundError(f"Phase 3C profiles missing: {profiles_csv}")
    df = pd.read_csv(profiles_csv)
    sub = df[df["model_name"] == source_model].copy()
    if sub.empty:
        raise ValueError(f"No rows for model_name={source_model!r} in {profiles_csv}")
    sub = sub.sort_values("r_kpc").reset_index(drop=True)
    return sub


def select_mass_at_radius(
    profile: pd.DataFrame,
    target_r_kpc: float,
) -> dict[str, float]:
    """Interpolate M_tau_eff to target_r; clamp to max r if target exceeds data."""
    r = profile["r_kpc"].to_numpy(dtype=float)
    m = profile["M_tau_eff_msun"].to_numpy(dtype=float)
    r_max = float(r.max())
    if target_r_kpc > r_max:
        idx = int(np.argmax(r))
        return {
            "radius_used_kpc": r_max,
            "M_tau_eff_msun": float(m[idx]),
            "interpolation_method": "nearest_at_max_radius",
            "target_radius_kpc": target_r_kpc,
        }
    m_at = float(np.interp(target_r_kpc, r, m))
    return {
        "radius_used_kpc": target_r_kpc,
        "M_tau_eff_msun": m_at,
        "interpolation_method": "linear",
        "target_radius_kpc": target_r_kpc,
    }


def load_lopez_fune_enclosed_mass_constraint(
    params_csv: Path,
    *,
    source_id: str = SOURCE_ID,
    model_label: str = LOPEZ_MODEL_LABEL,
    parameter_name: str = LOPEZ_PARAM_NAME,
) -> dict[str, Any]:
    if not params_csv.is_file():
        raise FileNotFoundError(f"López Fune parameters CSV missing: {params_csv}")
    df = pd.read_csv(params_csv)
    mask = (
        (df["source_id"] == source_id)
        & (df["model_label"] == model_label)
        & (df["parameter_name"] == parameter_name)
    )
    rows = df.loc[mask]
    if len(rows) != 1:
        raise ValueError(
            f"Expected one {parameter_name!r} row for {source_id}/{model_label}, "
            f"found {len(rows)}"
        )
    row = rows.iloc[0]
    unc = row.get("quoted_uncertainty")
    unc_f = float(unc) if pd.notna(unc) and str(unc).strip() != "" else np.nan
    return {
        "source_id": source_id,
        "model_label": model_label,
        "parameter_name": parameter_name,
        "M_lopez_enclosed_msun": float(row["value"]),
        "M_lopez_uncertainty_msun": unc_f,
        "unit": str(row["unit"]),
        "page_or_section": str(row.get("page_or_section", "")),
        "reference": str(row.get("reference", "")),
        "notes": str(row.get("notes", "")),
    }


def compare_tau_mass_proxy_to_upper_bound(
    m_tau_msun: float,
    m_lopez_msun: float,
    m_lopez_uncertainty_msun: float,
    *,
    tolerance_sigma: float = 1.0,
) -> dict[str, Any]:
    """Conservative check: PASS_WITH_CAVEAT if M_tau <= M_lopez + sigma*uncertainty."""
    ratio = m_tau_msun / m_lopez_msun if m_lopez_msun > 0 else np.nan
    if np.isfinite(m_lopez_uncertainty_msun) and m_lopez_uncertainty_msun > 0:
        upper_envelope = m_lopez_msun + tolerance_sigma * m_lopez_uncertainty_msun
        sigma_excess = (m_tau_msun - m_lopez_msun) / m_lopez_uncertainty_msun
    else:
        upper_envelope = m_lopez_msun
        sigma_excess = np.nan
    if m_tau_msun <= upper_envelope:
        status = "PASS_WITH_CAVEAT"
        rationale = (
            f"M_tau_eff ({m_tau_msun:.3e} M_sun) <= López Fune upper envelope "
            f"{upper_envelope:.3e} M_sun (M_enclosed_23kpc + {tolerance_sigma}σ uncertainty)."
        )
    else:
        status = "REVIEW_REQUIRED"
        rationale = (
            f"M_tau_eff ({m_tau_msun:.3e} M_sun) exceeds López Fune upper envelope "
            f"{upper_envelope:.3e} M_sun; scale consistency needs review."
        )
    return {
        "ratio_tau_to_lopez": ratio,
        "upper_envelope_msun": upper_envelope,
        "sigma_excess": sigma_excess,
        "consistency_status": status,
        "consistency_rationale": rationale,
        "tolerance_sigma": tolerance_sigma,
    }


def build_tau_mass_proxy_profile(
    phase3c: pd.DataFrame,
    *,
    source_model: str,
    g_kpc: float = G_KPC,
) -> pd.DataFrame:
    r = phase3c["r_kpc"].to_numpy(dtype=float)
    v2 = phase3c["v_tau_squared"].to_numpy(dtype=float)
    m_eff = compute_effective_tau_mass_proxy(r, v2, g_kpc=g_kpc)
    out = pd.DataFrame(
        {
            "source_model": source_model,
            "r_kpc": r,
            "v_tau_squared_kms2": v2,
            "v_tau_kms": phase3c["v_tau_kms"].to_numpy(dtype=float),
            "k_tau": phase3c["k_tau"].to_numpy(dtype=float),
            "M_tau_eff_msun": m_eff,
            "mass_proxy_label": "newtonian_equivalent_tau_enclosed_proxy",
            "G_kpc_kms2_per_msun": g_kpc,
            "formula": "M_tau_eff = r_kpc * v_tau_squared / G",
            "notes": (
                "Not dark matter mass; effective circular-dynamical proxy from frozen "
                "Phase 3C τ branch for upper-bound consistency only."
            ),
        }
    )
    return out


def build_summary_row(
    cfg: dict[str, Any],
    at_radius: dict[str, float],
    lopez: dict[str, Any],
    comparison: dict[str, Any],
) -> pd.DataFrame:
    row = {
        "source_model": cfg["source_model"],
        "comparison_source_id": lopez["source_id"],
        "radius_target_kpc": at_radius["target_radius_kpc"],
        "radius_used_kpc": at_radius["radius_used_kpc"],
        "interpolation_method": at_radius["interpolation_method"],
        "M_tau_eff_msun": at_radius["M_tau_eff_msun"],
        "M_lopez_enclosed_msun": lopez["M_lopez_enclosed_msun"],
        "M_lopez_uncertainty_msun": lopez["M_lopez_uncertainty_msun"],
        "ratio_tau_to_lopez": comparison["ratio_tau_to_lopez"],
        "upper_envelope_msun": comparison["upper_envelope_msun"],
        "sigma_excess": comparison["sigma_excess"],
        "consistency_status": comparison["consistency_status"],
        "consistency_rationale": comparison["consistency_rationale"],
        "circularity_note": CIRCULARITY_NOTE,
        "not_direct_lensing_flag": True,
        "normalized_proxy_deflection_flag": True,
        "observational_limits_enabled": cfg["observational_limits_enabled"],
        "physical_calibration_enabled": cfg["physical_calibration_enabled"],
        "separate_halo_used": False,
        "lensing_only_fit": False,
        "alpha_tau_scale_fitted": False,
        "k_tau": cfg["k_tau"],
        "lopez_parameter": lopez["parameter_name"],
        "lopez_model_label": lopez["model_label"],
    }
    return pd.DataFrame([row])


def write_upper_bound_report(
    report_path: Path,
    summary: pd.DataFrame,
    *,
    profile_path: Path,
    summary_path: Path,
    lopez: dict[str, Any],
) -> None:
    s = summary.iloc[0]
    lines = [
        "# Phase 5C-B — Upper-bound dynamical consistency (López Fune 2017)",
        "",
        "**Scope:** Enclosed-mass-style scale check only. **Not** weak lensing. "
        "**Not** a τ-map or deflection comparison.",
        "",
        "## Method",
        "",
        "- Same frozen τ branch: `tdf_lowparam_3knot`, fixed `K_tau`, no new fit.",
        "- Effective mass proxy: `M_tau_eff(<r) = r_kpc * v_tau^2 / G` with "
        f"`G = {G_KPC:.6g}` kpc (km/s)² M☉⁻¹.",
        "- `v_tau^2` from Phase 3C (`v_tau_squared` = r K_τ dτ/dr).",
        "- Reference: López Fune et al. 2017 BRK `M_enclosed_23kpc` "
        f"= {lopez['M_lopez_enclosed_msun']:.3e} ± "
        f"{lopez['M_lopez_uncertainty_msun']:.3e} M☉ (dynamical halo, not lensing).",
        "",
        "## Result at comparison radius",
        "",
        f"- Radius used: **{s['radius_used_kpc']:.2f}** kpc "
        f"(target {s['radius_target_kpc']:.2f} kpc; {s['interpolation_method']}).",
        f"- `M_tau_eff`: **{s['M_tau_eff_msun']:.3e}** M☉",
        f"- López Fune enclosed reference: **{s['M_lopez_enclosed_msun']:.3e}** M☉",
        f"- Ratio M_tau / M_López: **{s['ratio_tau_to_lopez']:.3f}**",
        f"- **Consistency status:** `{s['consistency_status']}`",
        f"- {s['consistency_rationale']}",
        "",
        "## Guardrails",
        "",
        "- Deflection remains **`normalized_proxy`**; no arcsec calibration.",
        "- `observational_limits.enabled` remains **false**.",
        "- No `alpha_tau_scale` fit; no separate halo; no lensing-only τ field.",
        "- **No** observational detection claim; **no** dark-matter replacement claim.",
        "",
        "## Circularity",
        "",
        CIRCULARITY_NOTE,
        "",
        "## Artifacts",
        "",
        f"- Profile: `{profile_path}`",
        f"- Summary: `{summary_path}`",
        "",
        "## Next phase",
        "",
        "Physical lensing calibration and weak-lensing comparison remain deferred. "
        "Any arcsec deflection work requires documented calibration, not this dynamical scale check.",
        "",
    ]
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text("\n".join(lines), encoding="utf-8")


def plot_mass_proxy_comparison(
    profile_df: pd.DataFrame,
    lopez: dict[str, Any],
    summary: pd.DataFrame,
    fig_path: Path,
    *,
    dpi: int = 150,
) -> None:
    s = summary.iloc[0]
    r = profile_df["r_kpc"].to_numpy(dtype=float)
    m = profile_df["M_tau_eff_msun"].to_numpy(dtype=float) / 1e10
    m_lo = lopez["M_lopez_enclosed_msun"] / 1e10
    m_hi = (lopez["M_lopez_enclosed_msun"] + lopez["M_lopez_uncertainty_msun"]) / 1e10
    m_lo_band = (lopez["M_lopez_enclosed_msun"] - lopez["M_lopez_uncertainty_msun"]) / 1e10

    fig, ax = plt.subplots(figsize=(7, 4.5))
    ax.plot(r, m, "b-", lw=1.5, label=r"$M_{\tau,\mathrm{eff}}(<r)$ proxy")
    ax.axhline(m_lo, color="crimson", ls="--", lw=1.2, label="López Fune M_enclosed (~23 kpc)")
    ax.fill_between(
        [r.min(), r.max()],
        m_lo_band,
        m_hi,
        color="crimson",
        alpha=0.15,
        label="López Fune ±1σ envelope",
    )
    ax.axvline(s["radius_used_kpc"], color="gray", ls=":", lw=1)
    ax.scatter(
        [s["radius_used_kpc"]],
        [s["M_tau_eff_msun"] / 1e10],
        c="blue",
        s=40,
        zorder=5,
        label=f"comparison @ {s['radius_used_kpc']:.2f} kpc",
    )
    ax.set_xlabel("r [kpc]")
    ax.set_ylabel(r"Mass [$10^{10}\,M_\odot$]")
    ax.set_title("Phase 5C-B: τ mass proxy vs López Fune dynamical upper bound")
    ax.legend(loc="best", fontsize=8)
    ax.grid(True, alpha=0.3)
    fig.text(0.5, 0.01, FIG_CAVEAT, ha="center", fontsize=6)
    fig.tight_layout(rect=[0, 0.04, 1, 1])
    fig_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(fig_path, dpi=dpi, bbox_inches="tight")
    plt.close(fig)


def run_phase5c_upper_bound_consistency(
    config_path: Path,
    profile_out: Path,
    summary_out: Path,
    report_out: Path,
    fig_out: Path,
) -> tuple[pd.DataFrame, pd.DataFrame, dict[str, Path]]:
    cfg = load_phase5c_config(config_path)
    if cfg["observational_limits_enabled"]:
        raise ValueError("observational_limits.enabled must remain false for Phase 5C-B")
    if cfg["physical_calibration_enabled"]:
        raise ValueError("physical_calibration.enabled must remain false for Phase 5C-B")
    if cfg["source_model"] != REQUIRED_SOURCE_MODEL:
        raise ValueError(f"source_model must be {REQUIRED_SOURCE_MODEL!r}")

    phase3c = load_phase3c_tdf_profile(cfg["profiles_csv"], source_model=cfg["source_model"])
    profile_df = build_tau_mass_proxy_profile(phase3c, source_model=cfg["source_model"])
    profile_out.parent.mkdir(parents=True, exist_ok=True)
    profile_df.to_csv(profile_out, index=False)

    lopez = load_lopez_fune_enclosed_mass_constraint(cfg["params_csv"])
    at_radius = select_mass_at_radius(profile_df, cfg["target_radius_kpc"])
    comparison = compare_tau_mass_proxy_to_upper_bound(
        at_radius["M_tau_eff_msun"],
        lopez["M_lopez_enclosed_msun"],
        lopez["M_lopez_uncertainty_msun"],
    )
    summary_df = build_summary_row(cfg, at_radius, lopez, comparison)
    summary_out.parent.mkdir(parents=True, exist_ok=True)
    summary_df.to_csv(summary_out, index=False)

    write_upper_bound_report(
        report_out,
        summary_df,
        profile_path=profile_out,
        summary_path=summary_out,
        lopez=lopez,
    )

    plot_mass_proxy_comparison(profile_df, lopez, summary_df, fig_out, dpi=cfg["figure_dpi"])

    products = {
        "profile_csv": profile_out,
        "summary_csv": summary_out,
        "report_md": report_out,
        "figure_png": fig_out,
    }
    return profile_df, summary_df, products
