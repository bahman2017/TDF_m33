"""Phase 6A: publication-ready results consolidation and claim-control audit."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd
import yaml

REPO_REL = Path(".")

# Existing pipeline outputs (read-only; do not recompute science)
PATHS = {
    "phase3c_combined": "outputs/tables/phase3c_combined_model_comparison.csv",
    "phase2c_audit": "outputs/tables/phase2c_model_audit_summary.csv",
    "phase3d_summary": "outputs/tables/phase3d_tdf_sensitivity_summary.csv",
    "phase5c_summary": "outputs/tables/phase5c_upper_bound_consistency_summary.csv",
    "phase5a_metadata": "outputs/tables/phase5a_lensing_prediction_metadata.csv",
    "phase4a_metadata": "outputs/tables/phase4a_tau_2d_map_metadata.csv",
    "phase4b_metadata": "outputs/tables/phase4b_tau_projection_metadata.csv",
}

SUMMARY_MD = "outputs/reports/phase6a_publication_results_summary.md"
KEY_RESULTS_CSV = "outputs/tables/phase6a_key_results_table.csv"
CLAIM_MATRIX_CSV = "outputs/tables/phase6a_claim_traceability_matrix.csv"
REPRO_MD = "outputs/reports/phase6a_reproducibility_commands.md"

FORBIDDEN_REPORT_PHRASES = (
    "dark matter disproven: true",
    "no need for dark matter",
    "replaces dark matter",
    "observational detection claimed",
    "weak lensing comparison complete",
)

PHASE3D_STABILITY_CONCLUSION = (
    "3-knot TDF beats NFW on AIC/BIC at default fit mask (0.4–23 kpc); "
    "fit-mask variants keep 3-knot competitive except stricter 1.0–22.0 kpc mask; "
    "K_tau sweep shows expected scale degeneracy with max RMSE spread 0.42 km/s. "
    "Qualify: rotation-only; D1-derived baryons PASS_WITH_CAVEAT."
)


def _repo_root(config_path: Path) -> Path:
    return config_path.resolve().parents[1]


def _resolve(repo: Path, rel: str) -> Path:
    p = Path(rel)
    return p if p.is_absolute() else repo / p


def _require_csv(repo: Path, key: str) -> pd.DataFrame:
    path = _resolve(repo, PATHS[key])
    if not path.is_file():
        raise FileNotFoundError(f"Missing required output for Phase 6A: {path}")
    return pd.read_csv(path)


def _row_from_combined(
    combined: pd.DataFrame, model_name: str, *, extra: dict[str, Any] | None = None
) -> dict[str, Any]:
    sub = combined.loc[combined["model_name"] == model_name]
    if sub.empty:
        raise ValueError(f"model {model_name!r} not in combined comparison table")
    r = sub.iloc[0]
    row: dict[str, Any] = {
        "result_id": model_name,
        "category": str(r.get("model_family", "")),
        "model_name": model_name,
        "n_fit_points": int(r["n_fit_points"]),
        "fit_r_min_kpc": float(r["fit_r_min_kpc"]),
        "fit_r_max_kpc": float(r["fit_r_max_kpc"]),
        "rmse_kms": float(r["rmse_kms"]),
        "chi_square": float(r["chi_square"]),
        "reduced_chi_square": float(r["reduced_chi_square"]),
        "aic": float(r["aic"]),
        "bic": float(r["bic"]),
        "parameter_count": int(r["parameter_count"]),
        "boundary_or_constraint_flag": "",
        "supporting_output": PATHS["phase3c_combined"],
        "notes": str(r.get("notes", ""))[:500],
    }
    if extra:
        row.update(extra)
    return row


def build_key_results_table(repo: Path) -> pd.DataFrame:
    combined = _require_csv(repo, "phase3c_combined")
    audit = _require_csv(repo, "phase2c_audit")
    sens = _require_csv(repo, "phase3d_summary")
    lopez = _require_csv(repo, "phase5c_summary")

    rows: list[dict[str, Any]] = []

    rows.append(_row_from_combined(combined, "baryonic_only"))

    nfw_row = _row_from_combined(combined, "nfw")
    nfw_audit = audit.loc[audit["model_name"] == "nfw"].iloc[0]
    nfw_row["boundary_or_constraint_flag"] = "lcdm_baseline"
    nfw_row["notes"] = (
        f"{nfw_row['notes']} | nfw_is_lcdm_baseline={nfw_audit.get('nfw_is_lcdm_baseline_not_tdf', True)}"
    )
    rows.append(nfw_row)

    brk = audit.loc[audit["model_name"] == "burkert"].iloc[0]
    brk_row = _row_from_combined(combined, "burkert")
    brk_row["boundary_or_constraint_flag"] = (
        "r0_at_upper_bound"
        if bool(brk.get("burkert_at_r0_upper_bound"))
        else ""
    )
    brk_row["notes"] = (
        f"{brk_row['notes']} | burkert_publication_stable="
        f"{brk.get('burkert_publication_stable', False)}"
    )
    rows.append(brk_row)

    rows.append(_row_from_combined(combined, "tdf_lowparam_3knot"))
    rows.append(_row_from_combined(combined, "tdf_lowparam_5knot"))

    beats_nfw = sens.loc[sens["check_name"] == "tdf_3knot_aic_beats_nfw", "value"]
    best_aic = sens.loc[sens["check_name"] == "best_tdf_by_aic", "value"].iloc[0]
    k_stable = sens.loc[sens["check_name"] == "k_tau_velocity_metrics_stable", "value"].iloc[0]
    dm_disproven = sens.loc[sens["check_name"] == "dark_matter_disproven", "value"].iloc[0]

    rows.append(
        {
            "result_id": "phase3d_sensitivity_stability",
            "category": "robustness_audit",
            "model_name": "tdf_lowparam_3knot",
            "n_fit_points": "",
            "fit_r_min_kpc": "",
            "fit_r_max_kpc": "",
            "rmse_kms": "",
            "chi_square": "",
            "reduced_chi_square": "",
            "aic": "",
            "bic": "",
            "parameter_count": "",
            "boundary_or_constraint_flag": "PASS_WITH_CAVEAT",
            "supporting_output": PATHS["phase3d_summary"],
            "notes": PHASE3D_STABILITY_CONCLUSION,
            "phase3d_best_tdf_by_aic": str(best_aic),
            "phase3d_3knot_aic_beats_nfw": str(beats_nfw.iloc[0] if len(beats_nfw) else ""),
            "phase3d_k_tau_rmse_stable_flag": str(k_stable),
            "phase3d_dark_matter_disproven": str(dm_disproven),
        }
    )

    s = lopez.iloc[0]
    rows.append(
        {
            "result_id": "phase5c_upper_bound_lopez_fune",
            "category": "dynamical_upper_bound",
            "model_name": str(s["source_model"]),
            "n_fit_points": "",
            "fit_r_min_kpc": float(s["radius_used_kpc"]),
            "fit_r_max_kpc": float(s["radius_target_kpc"]),
            "rmse_kms": "",
            "chi_square": "",
            "reduced_chi_square": "",
            "aic": "",
            "bic": "",
            "parameter_count": "",
            "boundary_or_constraint_flag": str(s["consistency_status"]),
            "supporting_output": PATHS["phase5c_summary"],
            "notes": str(s["consistency_rationale"]),
            "M_tau_eff_msun": float(s["M_tau_eff_msun"]),
            "M_lopez_enclosed_msun": float(s["M_lopez_enclosed_msun"]),
            "ratio_tau_to_lopez": float(s["ratio_tau_to_lopez"]),
        }
    )

    return pd.DataFrame(rows)


def build_claim_traceability_matrix(repo: Path) -> pd.DataFrame:
    meta4a = _require_csv(repo, "phase4a_metadata")
    meta5a = _require_csv(repo, "phase5a_metadata")
    lopez = _require_csv(repo, "phase5c_summary")
    lopez_status = str(lopez.iloc[0]["consistency_status"])

    claims: list[dict[str, str]] = [
        {
            "claim_text": "M33 baryons alone do not explain the rotation curve",
            "supported_status": "supported",
            "supporting_output": PATHS["phase3c_combined"],
            "caveat": "D1-derived baryonic velocities PASS_WITH_CAVEAT; fit mask 0.4–23 kpc.",
            "allowed_language": "Baryonic-only baseline has large RMSE/χ² vs observed rotation on the fit mask.",
            "prohibited_language": "Baryons are ruled out as the sole mass component without caveat on derived velocities.",
        },
        {
            "claim_text": "NFW is a strong ΛCDM baseline",
            "supported_status": "supported",
            "supporting_output": PATHS["phase3c_combined"],
            "caveat": "Two-parameter halo on D1 baryons; reference comparison not TDF validation.",
            "allowed_language": "NFW achieves reduced χ²≈1.2 and competitive AIC/BIC vs low-parameter TDF on this dataset.",
            "prohibited_language": "NFW proves ΛCDM or disproves TDF.",
        },
        {
            "claim_text": "Burkert is boundary-limited in this processed dataset",
            "supported_status": "supported",
            "supporting_output": PATHS["phase2c_audit"],
            "caveat": "r₀ at upper fit bound (~200 kpc); poor match to Corbelli BVI reference scale.",
            "allowed_language": "Burkert fit hits r₀ upper bound; high RMSE; not a stable publication anchor here.",
            "prohibited_language": "Burkert is falsified or preferred over NFW/TDF without boundary caveat.",
        },
        {
            "claim_text": "A 3-knot TDF radial model fits M33 rotation residuals competitively",
            "supported_status": "supported",
            "supporting_output": PATHS["phase3c_combined"],
            "caveat": "Rotation-only; K_τ=1 normalization; D1 baryonic caveat; not lensing evidence.",
            "allowed_language": "tdf_lowparam_3knot RMSE/AIC/BIC competitive with NFW on fit mask (see key results table).",
            "prohibited_language": "TDF replaces dark matter or outperforms all cosmological models.",
        },
        {
            "claim_text": "The 3-knot TDF advantage is stable under tested sensitivity checks",
            "supported_status": "caveated",
            "supporting_output": PATHS["phase3d_summary"],
            "caveat": "Beats NFW on AIC at default mask; mask/K_τ audits show qualifiers (see Phase 3D report).",
            "allowed_language": "3-knot ranking stable under default and moderate mask variants; document K_τ degeneracy.",
            "prohibited_language": "TDF is robust to all systematics or independent of baryonic derivation.",
        },
        {
            "claim_text": "A 2D τ-map was generated from the radial TDF model",
            "supported_status": "supported",
            "supporting_output": PATHS["phase4a_metadata"],
            "caveat": "Axisymmetric disk-plane extension τ_2d(x,y)=τ_radial(R); no separate 2D fit.",
            "allowed_language": "Phase 4A map from frozen tdf_lowparam_3knot radial profile.",
            "prohibited_language": "2D τ-map is an independent spatial fit or traces spiral arms.",
        },
        {
            "claim_text": "A normalized deflection proxy was generated from the same frozen τ-map",
            "supported_status": "supported",
            "supporting_output": PATHS["phase5a_metadata"],
            "caveat": f"units={meta5a.iloc[0].get('units', 'normalized_proxy')}; no arcsec calibration.",
            "allowed_language": "Phase 5A deflection-proxy maps from sky-projected τ; prediction scaffold only.",
            "prohibited_language": "Measured lensing deflection or convergence in arcsec.",
        },
        {
            "claim_text": "López Fune upper-bound consistency is PASS_WITH_CAVEAT",
            "supported_status": "supported" if lopez_status == "PASS_WITH_CAVEAT" else "caveated",
            "supporting_output": PATHS["phase5c_summary"],
            "caveat": "Dynamics/rotation-based M_enclosed reference; partial Corbelli circularity; not lensing.",
            "allowed_language": f"M_tau_eff proxy within López Fune 1σ envelope at ~23 kpc ({lopez_status}).",
            "prohibited_language": "τ mass equals observed DM or confirms TDF lensing.",
        },
        {
            "claim_text": "Direct weak-lensing comparison is not yet available",
            "supported_status": "future_work",
            "supporting_output": "docs/lensing_constraint_source_review.md",
            "caveat": "m33_direct_weak_lensing_gap documented in Phase 5B-B review.",
            "allowed_language": "No M33-specific weak-lensing map in repo; comparison deferred.",
            "prohibited_language": "Weak lensing confirms or refutes τ deflection.",
        },
        {
            "claim_text": "Dark matter is not disproven",
            "supported_status": "prohibited",
            "supporting_output": PATHS["phase3d_summary"],
            "caveat": "NFW remains ΛCDM reference; TDF is rotation-dynamics consistency only.",
            "allowed_language": "Pipeline does not claim DM replacement; halo baselines retained for context.",
            "prohibited_language": "Dark matter disproven; no need for dark matter; TDF replaces dark matter.",
        },
    ]
    _ = meta4a  # loaded to verify artifact exists
    return pd.DataFrame(claims)


def build_reproducibility_commands_md() -> str:
    lines = [
        "# Phase 6A — Reproducibility commands (M33 TDF pipeline)",
        "",
        "Run from repository root with project venv active. Config: `configs/m33_default.yaml`.",
        "",
        "## Data and validation",
        "",
        "```bash",
        "python scripts/prepare_corbelli2014_table1_template.py",
        "python scripts/extract_corbelli2014_table1_from_pdf.py",
        "python scripts/validate_corbelli2014_table1_raw.py",
        "python scripts/derive_corbelli2014_baryonic_velocities.py",
        "python scripts/validate_corbelli2014_baryonic_velocity_derivation.py",
        "python scripts/build_m33_rotation_processed.py",
        "python scripts/validate_m33_data.py data/processed/m33_rotation.csv",
        "python scripts/check_sources_manifest.py data/raw/sources_manifest.yaml",
        "python scripts/audit_m33_sources.py",
        "```",
        "",
        "## Phase 2 — baselines",
        "",
        "```bash",
        "python scripts/run_phase2a_baryonic_only.py",
        "python scripts/run_phase2b_halo_baselines.py",
        "python scripts/run_phase2c_model_audit.py",
        "```",
        "",
        "## Phase 3 — TDF radial pathway",
        "",
        "```bash",
        "python scripts/run_phase3a_tdf_radial_reconstruction.py",
        "python scripts/run_phase3b_tdf_regularized_reconstruction.py",
        "python scripts/run_phase3c_tdf_lowparam_model.py",
        "python scripts/run_phase3d_tdf_sensitivity.py",
        "```",
        "",
        "## Phase 4 — τ maps",
        "",
        "```bash",
        "python scripts/run_phase4a_tdf_2d_map.py",
        "python scripts/run_phase4b_tau_projection.py",
        "```",
        "",
        "## Phase 5 — lensing scaffold and limits",
        "",
        "```bash",
        "python scripts/run_phase5a_lensing_prediction.py",
        "python scripts/run_phase5b_lensing_calibration_audit.py",
        "python scripts/run_phase5b_constraint_source_audit.py",
        "python scripts/audit_lopez_fune_2017_source.py",
        "python scripts/validate_lopez_fune_2017_extracted_constraints.py",
        "python scripts/run_phase5c_upper_bound_consistency.py",
        "```",
        "",
        "## Phase 6A — publication audit",
        "",
        "```bash",
        "python scripts/run_phase6a_publication_audit.py",
        "```",
        "",
        "**Note:** Prior numerical outputs are read-only inputs to Phase 6A; the audit does not refit models.",
        "",
    ]
    return "\n".join(lines)


def build_publication_summary_md(
    key_results: pd.DataFrame,
    claims: pd.DataFrame,
    repo: Path,
) -> str:
    brk = key_results.loc[key_results["result_id"] == "burkert"].iloc[0]
    nfw = key_results.loc[key_results["result_id"] == "nfw"].iloc[0]
    t3 = key_results.loc[key_results["result_id"] == "tdf_lowparam_3knot"].iloc[0]
    t5 = key_results.loc[key_results["result_id"] == "tdf_lowparam_5knot"].iloc[0]
    bar = key_results.loc[key_results["result_id"] == "baryonic_only"].iloc[0]
    lopez = key_results.loc[key_results["result_id"] == "phase5c_upper_bound_lopez_fune"].iloc[0]

    n_supported = (claims["supported_status"] == "supported").sum()
    n_caveated = (claims["supported_status"] == "caveated").sum()
    n_future = (claims["supported_status"] == "future_work").sum()

    lines = [
        "# Phase 6A — Publication results summary (M33 TDF)",
        "",
        "**Purpose:** Consolidate supported results, caveats, and future work for manuscript drafting. "
        "This report does not refit models or change prior numerical outputs.",
        "",
        "## Strongest supported result",
        "",
        "The strongest current result is **rotation-dynamics consistency** of a **low-parameter "
        "3-knot τ-gradient model** (`tdf_lowparam_3knot`) on the Corbelli 2014 rotation curve with "
        "D1-derived baryonic components: RMSE ≈ {:.2f} km/s, AIC ≈ {:.1f}, BIC ≈ {:.1f} on the "
        "0.4–23 kpc fit mask (n={}), competitive with NFW (AIC ≈ {:.1f}).".format(
            t3["rmse_kms"],
            t3["aic"],
            t3["bic"],
            int(t3["n_fit_points"]),
            nfw["aic"],
        ),
        "",
        "## Key quantitative results (fit mask 0.4–23 kpc)",
        "",
        "| Model | RMSE [km/s] | χ² | AIC | BIC | Notes |",
        "|-------|-------------|-----|-----|-----|-------|",
        "| Baryonic only | {:.2f} | {:.0f} | {:.0f} | {:.0f} | No halo/TDF |".format(
            bar["rmse_kms"],
            bar["chi_square"],
            bar["aic"],
            bar["bic"],
        ),
        "| NFW (ΛCDM baseline) | {:.2f} | {:.1f} | {:.1f} | {:.1f} | 2-parameter halo |".format(
            nfw["rmse_kms"],
            nfw["chi_square"],
            nfw["aic"],
            nfw["bic"],
        ),
        "| Burkert | {:.2f} | {:.0f} | {:.0f} | {:.0f} | {} |".format(
            brk["rmse_kms"],
            brk["chi_square"],
            brk["aic"],
            brk["bic"],
            brk["boundary_or_constraint_flag"] or "see audit",
        ),
        "| TDF 3-knot | {:.2f} | {:.1f} | {:.1f} | {:.1f} | K_τ=1 fixed |".format(
            t3["rmse_kms"],
            t3["chi_square"],
            t3["aic"],
            t3["bic"],
        ),
        "| TDF 5-knot | {:.2f} | {:.1f} | {:.1f} | {:.1f} | Lowest RMSE; higher BIC penalty |".format(
            t5["rmse_kms"],
            t5["chi_square"],
            t5["aic"],
            t5["bic"],
        ),
        "",
        "## Phase 3D stability (summary)",
        "",
        PHASE3D_STABILITY_CONCLUSION,
        "",
        "## Lensing and external constraints",
        "",
        "- **Deflection:** `normalized_proxy` only (Phase 5A); **no** arcsec calibration.",
        "- **López Fune 2017:** dynamical upper-bound consistency — **{}** "
        "(M_tau/M_López ≈ {:.2f} at {:.1f} kpc); **not** weak lensing.".format(
            lopez["boundary_or_constraint_flag"],
            lopez["ratio_tau_to_lopez"],
            lopez["fit_r_min_kpc"],
        ),
        "- **Weak lensing:** not available (`m33_direct_weak_lensing_gap`).",
        "",
        "## Claim control snapshot",
        "",
        f"- Supported: {n_supported}",
        f"- Caveated: {n_caveated}",
        f"- Future work: {n_future}",
        f"- Prohibited affirmative claims: {(claims['supported_status'] == 'prohibited').sum()} "
        "(must not appear in manuscript)",
        "",
        "Full matrix: `{}`.".format(CLAIM_MATRIX_CSV),
        "",
        "## What remains future work",
        "",
        "1. Physical `alpha_tau_scale` / arcsec lensing calibration.",
        "2. Independent M33 weak-lensing comparison.",
        "3. Improved baryonic velocity systematics beyond D1 PASS_WITH_CAVEAT.",
        "",
        "## Explicit non-claims",
        "",
        "- Dark matter is **not** disproven or replaced.",
        "- Phase 5A deflection is a **prediction scaffold**, not observational detection.",
        "- López Fune comparison is **dynamical scale consistency**, not τ-lensing validation.",
        "",
        "## Artifacts",
        "",
        f"- Key results: `{KEY_RESULTS_CSV}`",
        f"- Claim traceability: `{CLAIM_MATRIX_CSV}`",
        f"- Reproducibility: `{REPRO_MD}`",
        "",
    ]
    return "\n".join(lines)


def validate_reports_text(text: str) -> list[str]:
    errors: list[str] = []
    lower = text.lower()
    for phrase in FORBIDDEN_REPORT_PHRASES:
        if phrase in lower:
            errors.append(f"forbidden phrase in report: {phrase!r}")
    return errors


def run_phase6a_publication_audit(
    config_path: Path,
    summary_md: Path,
    key_results_csv: Path,
    claim_matrix_csv: Path,
    repro_md: Path,
) -> tuple[pd.DataFrame, pd.DataFrame, dict[str, Path]]:
    repo = _repo_root(config_path)
    with config_path.open() as f:
        cfg = yaml.safe_load(f)
    if cfg.get("tdf", {}).get("lensing", {}).get("physical_calibration", {}).get("enabled"):
        raise ValueError("physical_calibration.enabled must be false for Phase 6A audit")

    key_df = build_key_results_table(repo)
    claims_df = build_claim_traceability_matrix(repo)
    summary_text = build_publication_summary_md(key_df, claims_df, repo)
    repro_text = build_reproducibility_commands_md()

    for label, text in (
        ("summary", summary_text),
        ("reproducibility", repro_text),
    ):
        errs = validate_reports_text(text)
        if errs:
            raise ValueError(f"{label} report: " + "; ".join(errs))

    summary_md.parent.mkdir(parents=True, exist_ok=True)
    key_results_csv.parent.mkdir(parents=True, exist_ok=True)
    claim_matrix_csv.parent.mkdir(parents=True, exist_ok=True)

    summary_md.write_text(summary_text, encoding="utf-8")
    key_df.to_csv(key_results_csv, index=False)
    claims_df.to_csv(claim_matrix_csv, index=False)
    repro_md.write_text(repro_text, encoding="utf-8")

    products = {
        "summary_md": summary_md,
        "key_results_csv": key_results_csv,
        "claim_matrix_csv": claim_matrix_csv,
        "repro_md": repro_md,
    }
    return key_df, claims_df, products
