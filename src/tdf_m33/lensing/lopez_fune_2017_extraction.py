"""Extract López Fune et al. 2017 dynamical constraints (Phase 5C-A)."""

from __future__ import annotations

import math
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import yaml

SOURCE_ID = "lopez_fune_salucci_corbelli_2017"
PROFILE_CSV = "data/raw/extracted/lopez_fune_2017_dm_profile_raw.csv"
PARAMS_CSV = "data/raw/extracted/lopez_fune_2017_halo_parameters_raw.csv"

# Fig. 6 black points — visual digitization from PDF page 8 (log-y, linear-x)
FIG6_DIGITIZED: list[tuple[float, float]] = [
    (10.0, 3.5),
    (12.0, 2.3),
    (14.0, 1.6),
    (16.0, 1.2),
    (18.0, 0.9),
    (20.0, 0.7),
    (22.0, 0.6),
]
FIG6_DIGITIZATION_UNCERTAINTY = 0.15  # relative, approximate

LOCAL_BRK_RC_KPC = 9.6
LOCAL_BRK_RHO_C = 12.3e6  # M_sun / kpc^3
LOCAL_NFW_C = 9.5
LOCAL_NFW_M_VIR = 5.4e11  # M_sun
RHO_CRIT_G_CM3 = 9.3e-30
MSUN_G = 1.98847e33
KPC_CM = 3.085677581e21


def rho_burkert(r_kpc: float, rho_c: float, r_c: float) -> float:
    x = r_kpc / r_c
    return rho_c / ((1.0 + x) * (1.0 + x * x))


def _nfw_rho_c_msun_kpc3(c: float, m_vir_msun: float) -> tuple[float, float]:
    """Return (rho_c, r_c) in M_sun/kpc^3 and kpc from virial mass and concentration."""
    rho_crit_msun_kpc3 = RHO_CRIT_G_CM3 * MSUN_G / (KPC_CM**3)
    rho_c = (
        97.2
        * (c**3)
        / (math.log(1.0 + c) - c / (1.0 + c))
        * rho_crit_msun_kpc3
    )
    r_c = (1.0 / c) * ((3.0 / 97.2) * m_vir_msun / (4.0 * math.pi * rho_crit_msun_kpc3)) ** (
        1.0 / 3.0
    )
    return rho_c, r_c


def rho_nfw(r_kpc: float, c: float, m_vir_msun: float) -> float:
    rho_c, r_c = _nfw_rho_c_msun_kpc3(c, m_vir_msun)
    x = r_kpc / r_c
    return rho_c / (x * (1.0 + x) ** 2)


def quoted_halo_parameters() -> pd.DataFrame:
    """Parameters explicitly quoted in López Fune et al. 2017 (MNRAS preprint)."""
    rows: list[dict[str, Any]] = [
        {
            "source_id": SOURCE_ID,
            "model_label": "nfw_global_corbelli2014_cited",
            "parameter_name": "concentration_c",
            "value": 9.5,
            "unit": "dimensionless",
            "quoted_uncertainty": 1.5,
            "page_or_section": "Section 2.2, page 4",
            "reference": "LopezFune2017 Eq.3-8; values from Corbelli et al. 2014 cited",
            "notes": "Global RC fit context; not local density method",
        },
        {
            "source_id": SOURCE_ID,
            "model_label": "nfw_global_corbelli2014_cited",
            "parameter_name": "M_vir",
            "value": 4.3e11,
            "unit": "M_sun",
            "quoted_uncertainty": 1.0e11,
            "page_or_section": "Section 2.2, page 4",
            "reference": "LopezFune2017 Section 2.2",
            "notes": "Global RC fit; Corbelli et al. 2014 cited",
        },
        {
            "source_id": SOURCE_ID,
            "model_label": "burkert_global_rc_fit",
            "parameter_name": "r_c",
            "value": 7.5,
            "unit": "kpc",
            "quoted_uncertainty": np.nan,
            "page_or_section": "Section 2.2, page 5",
            "reference": "LopezFune2017 Section 2.2 BRK global fit",
            "notes": "Global RC fit with synthesis stellar mass 7.2e9 M_sun",
        },
        {
            "source_id": SOURCE_ID,
            "model_label": "burkert_global_rc_fit",
            "parameter_name": "rho_c",
            "value": 18.0e6,
            "unit": "M_sun/kpc^3",
            "quoted_uncertainty": np.nan,
            "page_or_section": "Section 2.2, page 5",
            "reference": "LopezFune2017 Section 2.2",
            "notes": "18.0 x 10^6 M_sun kpc^-3 in paper",
        },
        {
            "source_id": SOURCE_ID,
            "model_label": "burkert_global_rc_fit",
            "parameter_name": "M_star",
            "value": 7.2e9,
            "unit": "M_sun",
            "quoted_uncertainty": np.nan,
            "page_or_section": "Section 2.2, page 5",
            "reference": "LopezFune2017 Section 2.2",
            "notes": "Stellar mass used in global BRK fit",
        },
        {
            "source_id": SOURCE_ID,
            "model_label": "rational_rc_fit",
            "parameter_name": "V0",
            "value": 130.2,
            "unit": "km/s",
            "quoted_uncertainty": 1.0,
            "page_or_section": "Section 3.2, page 6",
            "reference": "LopezFune2017 Eq.18",
            "notes": "Empirical RC fit for local density method",
        },
        {
            "source_id": SOURCE_ID,
            "model_label": "rational_rc_fit",
            "parameter_name": "r0",
            "value": 1.3,
            "unit": "kpc",
            "quoted_uncertainty": 0.1,
            "page_or_section": "Section 3.2, page 6",
            "reference": "LopezFune2017 Eq.18",
            "notes": "",
        },
        {
            "source_id": SOURCE_ID,
            "model_label": "rational_rc_fit",
            "parameter_name": "d",
            "value": 0.12,
            "unit": "dimensionless",
            "quoted_uncertainty": 0.03,
            "page_or_section": "Section 3.2, page 6",
            "reference": "LopezFune2017 Eq.18",
            "notes": "chi2_red=0.75 quoted",
        },
        {
            "source_id": SOURCE_ID,
            "model_label": "burkert_local_density",
            "parameter_name": "r_c",
            "value": 9.6,
            "unit": "kpc",
            "quoted_uncertainty": 0.5,
            "page_or_section": "Section 3.3, page 6-7",
            "reference": "LopezFune2017 Section 3.3",
            "notes": "9.5 <= r <= 22.72 kpc local method",
        },
        {
            "source_id": SOURCE_ID,
            "model_label": "burkert_local_density",
            "parameter_name": "rho_c",
            "value": 12.3e6,
            "unit": "M_sun/kpc^3",
            "quoted_uncertainty": 1.0e6,
            "page_or_section": "Section 3.3, page 6-7",
            "reference": "LopezFune2017 Section 3.3",
            "notes": "12.3 x 10^6 M_sun kpc^-3",
        },
        {
            "source_id": SOURCE_ID,
            "model_label": "burkert_local_density",
            "parameter_name": "M_vir",
            "value": 3.0e11,
            "unit": "M_sun",
            "quoted_uncertainty": 0.8e11,
            "page_or_section": "Section 3.3 / Section 4, page 6-9",
            "reference": "LopezFune2017 Section 3.3 and Conclusions",
            "notes": "Local density estimator BRK fit",
        },
        {
            "source_id": SOURCE_ID,
            "model_label": "nfw_local_density",
            "parameter_name": "concentration_c",
            "value": 9.5,
            "unit": "dimensionless",
            "quoted_uncertainty": 0.7,
            "page_or_section": "Section 3.3, page 7",
            "reference": "LopezFune2017 Section 3.3",
            "notes": "chi2_red=1.0",
        },
        {
            "source_id": SOURCE_ID,
            "model_label": "nfw_local_density",
            "parameter_name": "M_vir",
            "value": 5.4e11,
            "unit": "M_sun",
            "quoted_uncertainty": 0.6e11,
            "page_or_section": "Section 3.3, page 7",
            "reference": "LopezFune2017 Section 3.3",
            "notes": "Local density estimator NFW fit",
        },
        {
            "source_id": SOURCE_ID,
            "model_label": "burkert_local_density",
            "parameter_name": "M_enclosed_23kpc",
            "value": 6.7e10,
            "unit": "M_sun",
            "quoted_uncertainty": 1.2e10,
            "page_or_section": "Section 4 Conclusions, page 9",
            "reference": "LopezFune2017 Conclusions",
            "notes": "BRK halo mass within ~23 kpc; not full virial mass",
        },
        {
            "source_id": SOURCE_ID,
            "model_label": "analysis_range",
            "parameter_name": "r_min_kpc",
            "value": 9.53,
            "unit": "kpc",
            "quoted_uncertainty": np.nan,
            "page_or_section": "Abstract; Section 3.3",
            "reference": "LopezFune2017",
            "notes": "DM-dominated local analysis range lower bound",
        },
        {
            "source_id": SOURCE_ID,
            "model_label": "analysis_range",
            "parameter_name": "r_max_kpc",
            "value": 22.72,
            "unit": "kpc",
            "quoted_uncertainty": np.nan,
            "page_or_section": "Abstract; Section 3.3",
            "reference": "LopezFune2017",
            "notes": "Upper bound of local density analysis",
        },
    ]
    return pd.DataFrame(rows)


def build_dm_profile_table() -> pd.DataFrame:
    """Build profile raw table: Fig. 6 digitization + model curves from quoted params."""
    rows: list[dict[str, Any]] = []
    row_id = 0

    for r_kpc, rho in FIG6_DIGITIZED:
        row_id += 1
        rows.append(
            {
                "source_id": SOURCE_ID,
                "figure_id": "Fig6",
                "row_id": f"fig6_obs_{row_id:02d}",
                "r_kpc": r_kpc,
                "rho_dm_value": rho * 1.0e6,
                "rho_dm_unit": "M_sun/kpc^3",
                "model_label": "observed_effective_dm",
                "extraction_method": "figure_digitization",
                "digitization_uncertainty": FIG6_DIGITIZATION_UNCERTAINTY,
                "reference": "LopezFune2017 Fig.6 page 8; visual digitization from PDF",
                "notes": (
                    "Effective DM density points (black dots); approximate "
                    f"{FIG6_DIGITIZATION_UNCERTAINTY:.0%} relative uncertainty"
                ),
            }
        )

    eval_radii = [9.53, 10.0, 12.0, 14.0, 16.0, 18.0, 20.0, 22.0, 22.72]
    for r_kpc in eval_radii:
        row_id += 1
        rows.append(
            {
                "source_id": SOURCE_ID,
                "figure_id": "Fig6",
                "row_id": f"brk_local_{row_id:02d}",
                "r_kpc": r_kpc,
                "rho_dm_value": rho_burkert(r_kpc, LOCAL_BRK_RHO_C, LOCAL_BRK_RC_KPC),
                "rho_dm_unit": "M_sun/kpc^3",
                "model_label": "burkert_local_fit",
                "extraction_method": "model_evaluated",
                "digitization_uncertainty": np.nan,
                "reference": "LopezFune2017 Section 3.3; Eq.9 with rc=9.6 kpc, rho_c=12.3e6",
                "notes": "BRK curve matching Fig.6 continuous line parameters",
            }
        )
        row_id += 1
        rows.append(
            {
                "source_id": SOURCE_ID,
                "figure_id": "Fig6",
                "row_id": f"nfw_local_{row_id:02d}",
                "r_kpc": r_kpc,
                "rho_dm_value": rho_nfw(r_kpc, LOCAL_NFW_C, LOCAL_NFW_M_VIR),
                "rho_dm_unit": "M_sun/kpc^3",
                "model_label": "nfw_local_fit",
                "extraction_method": "model_evaluated",
                "digitization_uncertainty": np.nan,
                "reference": "LopezFune2017 Section 3.3; Eq.3 with c=9.5, M_vir=5.4e11",
                "notes": "NFW curve matching Fig.6 dashed line parameters",
            }
        )

    return pd.DataFrame(rows)


def write_extracted_tables(repo_root: Path) -> tuple[Path, Path]:
    profile_path = repo_root / PROFILE_CSV
    params_path = repo_root / PARAMS_CSV
    profile_path.parent.mkdir(parents=True, exist_ok=True)
    build_dm_profile_table().to_csv(profile_path, index=False)
    quoted_halo_parameters().to_csv(params_path, index=False)
    return profile_path, params_path


def load_phase5c_config(config_path: Path) -> dict[str, Any]:
    with config_path.open() as f:
        cfg = yaml.safe_load(f)
    lens = cfg.get("tdf", {}).get("lensing", {})
    limits = lens.get("observational_limits", {})
    phys = lens.get("physical_calibration", {})
    return {
        "observational_limits_enabled": bool(limits.get("enabled", False)),
        "output_units": str(phys.get("output_units", "normalized_proxy")),
        "physical_calibration_enabled": bool(phys.get("enabled", False)),
    }


def validate_extracted_constraints(
    repo_root: Path,
    config_path: Path | None = None,
) -> list[str]:
    """Return validation error messages (empty if ok)."""
    errors: list[str] = []
    profile_path = repo_root / PROFILE_CSV
    params_path = repo_root / PARAMS_CSV

    if not profile_path.is_file():
        errors.append(f"missing {PROFILE_CSV}")
    if not params_path.is_file():
        errors.append(f"missing {PARAMS_CSV}")
    if errors:
        return errors

    prof = pd.read_csv(profile_path)
    params = pd.read_csv(params_path)

    for col in (
        "source_id",
        "r_kpc",
        "rho_dm_value",
        "extraction_method",
        "reference",
    ):
        if col not in prof.columns:
            errors.append(f"profile missing column {col!r}")

    forbidden_profile_cols = (
        "tau",
        "alpha_tau",
        "deflection",
        "comparison",
        "chi2_vs_tdf",
    )
    for col in prof.columns:
        if any(tok in col.lower() for tok in forbidden_profile_cols):
            errors.append(f"forbidden profile column {col!r}")

    if (prof["source_id"] != SOURCE_ID).any():
        errors.append("profile source_id must be lopez_fune_salucci_corbelli_2017")
    if (prof["r_kpc"] <= 0).any():
        errors.append("profile r_kpc must be > 0")
    if (prof["rho_dm_value"] <= 0).any():
        errors.append("profile rho_dm_value must be > 0")
    if prof["extraction_method"].isna().any() or (prof["extraction_method"] == "").any():
        errors.append("profile extraction_method must be non-empty")
    if prof["reference"].isna().any() or (prof["reference"] == "").any():
        errors.append("profile reference must be non-empty")

    if (params["source_id"] != SOURCE_ID).any():
        errors.append("parameters source_id mismatch")
    if params["parameter_name"].isna().any():
        errors.append("parameters missing parameter_name")

    if config_path and config_path.is_file():
        cfg = load_phase5c_config(config_path)
        if cfg["observational_limits_enabled"]:
            errors.append("observational_limits.enabled must be false")
        if cfg["physical_calibration_enabled"]:
            errors.append("physical_calibration.enabled must be false")
        if cfg["output_units"] != "normalized_proxy":
            errors.append("output_units must be normalized_proxy")

    for pattern in ("phase5c*comparison*.csv", "lopez_fune*comparison*.csv"):
        if list((repo_root / "outputs").rglob(pattern)):
            errors.append(f"unexpected comparison output matching {pattern}")

    return errors


def build_extraction_status_table(
    profile_df: pd.DataFrame,
    params_df: pd.DataFrame,
) -> pd.DataFrame:
    n_fig6 = int((profile_df["extraction_method"] == "figure_digitization").sum())
    n_model = int((profile_df["extraction_method"] == "model_evaluated").sum())
    rows = [
        {
            "source_id": SOURCE_ID,
            "extracted_artifact": PROFILE_CSV,
            "extraction_status": "extracted",
            "suitability": "upper_bound_dynamical_consistency",
            "limitations": (
                "Fig.6 points approximate; overlaps Corbelli 2014 dynamics; not lensing"
            ),
            "next_phase_use": "Phase 5C-B enclosed-mass / rho consistency only",
            "row_count": len(profile_df),
            "fig6_digitized_rows": n_fig6,
            "model_evaluated_rows": n_model,
        },
        {
            "source_id": SOURCE_ID,
            "extracted_artifact": PARAMS_CSV,
            "extraction_status": "extracted",
            "suitability": "halo_parameter_reference",
            "limitations": "Quoted prose only; no machine tables in paper",
            "next_phase_use": "Phase 5C-B anchor NFW/BRK reference fits",
            "row_count": len(params_df),
            "fig6_digitized_rows": np.nan,
            "model_evaluated_rows": np.nan,
        },
    ]
    return pd.DataFrame(rows)


def write_extraction_audit_report(
    path: Path,
    profile_df: pd.DataFrame,
    params_df: pd.DataFrame,
    status_df: pd.DataFrame,
) -> None:
    n_digit = int((profile_df["extraction_method"] == "figure_digitization").sum())
    n_model = int((profile_df["extraction_method"] == "model_evaluated").sum())
    lines = [
        "# Phase 5C-A — López Fune et al. 2017 extraction audit",
        "",
        "**Scope:** Extraction only. No τ-map comparison. No observational_limits "
        "enabled. Deflection remains `normalized_proxy`.",
        "",
        "## Extracted artifacts",
        "",
        f"- `{PROFILE_CSV}` — **{len(profile_df)}** rows "
        f"({n_digit} Fig.6 digitized, {n_model} model-evaluated BRK/NFW curves)",
        f"- `{PARAMS_CSV}` — **{len(params_df)}** quoted parameters",
        "",
        "## What was extracted",
        "",
        "- **Fig. 6** effective DM density points (7 radii, visual digitization, "
        f"~{FIG6_DIGITIZATION_UNCERTAINTY:.0%} relative uncertainty).",
        "- **BRK / NFW local-fit curves** at 9.53–22.72 kpc from quoted "
        "Section 3.3 parameters (Eq. 9 and NFW Eq. 3).",
        "- **Halo parameters** quoted in Sections 2.2, 3.2, 3.3, and 4 "
        "(global and local methods).",
        "",
        "## What was not extracted",
        "",
        "- Machine-readable publisher tables (none in PDF).",
        "- Full RC point-by-point digitization (Fig. 2).",
        "- Independent weak-lensing maps (unavailable).",
        "- Any τ-map or deflection comparison columns.",
        "",
        "## Method notes",
        "",
        "- Fig. 6 digitization is **approximate** (PDF raster, log-y axis).",
        "- Model curve rows are **not** independent observations; they trace "
        "quoted best-fit parameters.",
        "- Parameters are **quoted directly** from paper text (not fitted here).",
        "",
        "## Circularity warning",
        "",
        "López Fune et al. 2017 uses Corbelli et al. 2014 baryonic and rotation "
        "inputs. This is **dynamical / rotation-based**, not independent weak "
        "lensing. Use for **upper-bound consistency** only; do not tune τ or "
        "`alpha_tau_scale`.",
        "",
        "## Future use (Phase 5C-B)",
        "",
        "Compare enclosed-mass-style proxies at documented radii (e.g. 23 kpc "
        "BRK `M_enclosed_23kpc` = 6.7±1.2×10¹⁰ M☉) against TDF dynamical "
        "scaffold — still no arcsec deflection claim.",
        "",
        "## Parameter summary",
        "",
        f"- Local BRK: r_c = 9.6 kpc, ρ_c = 12.3×10⁶ M☉/kpc³, M_vir = 3.0×10¹¹ M☉",
        f"- Local NFW: c = 9.5, M_vir = 5.4×10¹¹ M☉",
        f"- Analysis range: 9.53 ≤ r ≤ 22.72 kpc",
        "",
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def run_phase5c_lopez_fune_extraction_audit(
    config_path: Path,
    status_csv_path: Path,
    report_path: Path,
    *,
    regenerate: bool = True,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Validate or regenerate extracted tables and write audit outputs."""
    repo_root = config_path.resolve().parents[1]
    if regenerate:
        write_extracted_tables(repo_root)

    errors = validate_extracted_constraints(repo_root, config_path)
    if errors:
        raise ValueError("; ".join(errors))

    profile_df = pd.read_csv(repo_root / PROFILE_CSV)
    params_df = pd.read_csv(repo_root / PARAMS_CSV)
    status_df = build_extraction_status_table(profile_df, params_df)
    status_csv_path.parent.mkdir(parents=True, exist_ok=True)
    status_df.to_csv(status_csv_path, index=False)
    write_extraction_audit_report(report_path, profile_df, params_df, status_df)
    return profile_df, params_df, status_df
