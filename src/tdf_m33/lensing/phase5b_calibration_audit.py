"""Phase 5B-A: calibration and observational-limits planning audit."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd
import yaml

REQUIRED_UNITS = "normalized_proxy"
PHASE5A_METADATA_DEFAULT = "outputs/tables/phase5a_lensing_prediction_metadata.csv"


def load_phase5b_config(config_path: Path) -> dict[str, Any]:
    with config_path.open() as f:
        cfg = yaml.safe_load(f)
    lens = cfg.get("tdf", {}).get("lensing", {})
    phys = lens.get("physical_calibration", {})
    limits = lens.get("observational_limits", {})
    return {
        "physical_calibration_enabled": bool(phys.get("enabled", False)),
        "alpha_tau_scale_physical": phys.get("alpha_tau_scale_physical"),
        "output_units": str(phys.get("output_units", REQUIRED_UNITS)),
        "calibration_status": str(phys.get("calibration_status", "uncalibrated")),
        "calibration_notes": str(phys.get("calibration_notes", "")),
        "observational_limits_enabled": bool(limits.get("enabled", False)),
        "limits_source_id": limits.get("limits_source_id"),
        "comparison_mode": str(limits.get("comparison_mode", "upper_bound_consistency")),
        "limits_status": str(limits.get("status", "planned")),
        "phase5a_compare_limits": bool(lens.get("compare_to_observational_limits", False)),
    }


def load_phase5a_metadata(metadata_path: Path) -> pd.Series:
    if not metadata_path.is_file():
        raise FileNotFoundError(f"Phase 5A metadata missing: {metadata_path}")
    df = pd.read_csv(metadata_path)
    if df.empty:
        raise ValueError(f"Phase 5A metadata empty: {metadata_path}")
    return df.iloc[0]


def build_calibration_status_row(
    phase5a: pd.Series,
    cfg: dict[str, Any],
    *,
    metadata_path: Path,
) -> dict[str, Any]:
    return {
        "phase": "5B-A",
        "audit_type": "calibration_and_limits_planning",
        "phase5a_metadata_path": str(metadata_path),
        "phase5a_units": str(phase5a["units"]),
        "phase5a_source_model": str(phase5a["source_model"]),
        "phase5a_alpha_tau_scale": float(phase5a["alpha_tau_scale"]),
        "phase5a_separate_halo_used": bool(phase5a["separate_halo_used"]),
        "phase5a_lensing_only_fit": bool(phase5a["lensing_only_fit"]),
        "phase5a_compare_to_observational_limits": bool(
            phase5a["compare_to_observational_limits"]
        ),
        "physical_calibration_enabled": cfg["physical_calibration_enabled"],
        "output_units": cfg["output_units"],
        "calibration_status": cfg["calibration_status"],
        "observational_limits_enabled": cfg["observational_limits_enabled"],
        "limits_source_id": cfg["limits_source_id"] or "",
        "limits_status": cfg["limits_status"],
        "comparison_mode": cfg["comparison_mode"],
        "same_frozen_tau_map": True,
        "independent_halo_introduced": False,
        "lensing_only_tau_fit": False,
        "physical_lensing_detection_claimed": False,
        "dark_matter_disproven_claimed": False,
        "recommendation": (
            "Proceed to Phase 5B-B only when calibration and limit sources are "
            "documented in docs/lensing_calibration_and_limits_plan.md and "
            "docs/data_sources.md"
        ),
    }


def validate_phase5a_for_audit(phase5a: pd.Series) -> list[str]:
    """Return list of validation failures (empty if ok)."""
    failures: list[str] = []
    if str(phase5a["units"]) != REQUIRED_UNITS:
        failures.append(f"units must be {REQUIRED_UNITS!r}, got {phase5a['units']!r}")
    if bool(phase5a["separate_halo_used"]):
        failures.append("separate_halo_used must be false")
    if bool(phase5a["lensing_only_fit"]):
        failures.append("lensing_only_fit must be false")
    if bool(phase5a["compare_to_observational_limits"]):
        failures.append("compare_to_observational_limits must be false")
    if str(phase5a["source_model"]) != "tdf_lowparam_3knot":
        failures.append("source_model must be tdf_lowparam_3knot")
    return failures


def write_audit_report(
    path: Path,
    phase5a: pd.Series,
    cfg: dict[str, Any],
    status_row: dict[str, Any],
    failures: list[str],
) -> None:
    lines = [
        "# Phase 5B-A — Lensing calibration and limits audit",
        "",
        "**Scope:** Planning / audit only. No physical lensing detection. "
        "No observational comparison in this phase.",
        "",
        "## Phase 5A status (frozen τ deflection proxy)",
        "",
        f"- Source τ map: `{phase5a['source_tau_map']}`",
        f"- source_model: `{phase5a['source_model']}`",
        f"- geometry_mode: `{phase5a['geometry_mode']}`",
        f"- units: **{phase5a['units']}**",
        f"- alpha_tau_scale: **{phase5a['alpha_tau_scale']}** (placeholder)",
        f"- separate_halo_used: **{bool(phase5a['separate_halo_used'])}**",
        f"- lensing_only_fit: **{bool(phase5a['lensing_only_fit'])}**",
        f"- compare_to_observational_limits: "
        f"**{bool(phase5a['compare_to_observational_limits'])}**",
        "",
        "## Phase 5B-A config (planning)",
        "",
        f"- physical_calibration.enabled: **{cfg['physical_calibration_enabled']}**",
        f"- output_units: **{cfg['output_units']}**",
        f"- calibration_status: **{cfg['calibration_status']}**",
        f"- observational_limits.enabled: **{cfg['observational_limits_enabled']}**",
        f"- limits_status: **{cfg['limits_status']}**",
        f"- limits_source_id: `{cfg['limits_source_id'] or 'none'}`",
        f"- comparison_mode (planned): `{cfg['comparison_mode']}`",
        "",
        "## Safeguards",
        "",
        "- Phase 5A is a **deflection-proxy scaffold** (normalized τ-gradient).",
        "- **Physical calibration is not implemented** (`physical_calibration.enabled: false`).",
        "- **Observational limit comparison is not implemented** "
        "(`observational_limits.enabled: false`).",
        "- The **same frozen τ map** from rotation reconstruction is used; "
        "no independent halo or lensing-only τ component is introduced.",
        "- **K_τ = 1** remains a normalization convention, not physical lensing calibration.",
        "- This audit makes **no** dark-matter disproof or replacement claim.",
        "",
        "## Validation",
        "",
    ]
    if failures:
        lines.append("**FAILURES:**")
        for f in failures:
            lines.append(f"- {f}")
    else:
        lines.append("- All Phase 5A audit checks **PASS**.")
    lines.extend(
        [
            "",
            "## Next phase (5B-B)",
            "",
            status_row["recommendation"],
            "",
            "See `docs/lensing_calibration_and_limits_plan.md` and the lensing "
            "source registry in `docs/data_sources.md`.",
            "",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def run_phase5b_calibration_audit(
    config_path: Path,
    phase5a_metadata_path: Path,
    status_csv_path: Path,
    report_path: Path,
) -> tuple[pd.DataFrame, list[str]]:
    """Run Phase 5B-A audit; raises if Phase 5A checks fail."""
    cfg = load_phase5b_config(config_path)
    phase5a = load_phase5a_metadata(phase5a_metadata_path)
    failures = validate_phase5a_for_audit(phase5a)
    if failures:
        raise ValueError("; ".join(failures))

    if cfg["physical_calibration_enabled"]:
        raise ValueError("physical_calibration.enabled must be false in Phase 5B-A")
    if cfg["observational_limits_enabled"]:
        raise ValueError("observational_limits.enabled must be false in Phase 5B-A")
    if cfg["output_units"] != REQUIRED_UNITS:
        raise ValueError(f"output_units must remain {REQUIRED_UNITS!r}")

    status_row = build_calibration_status_row(
        phase5a, cfg, metadata_path=phase5a_metadata_path
    )
    status_df = pd.DataFrame([status_row])
    status_csv_path.parent.mkdir(parents=True, exist_ok=True)
    status_df.to_csv(status_csv_path, index=False)
    write_audit_report(report_path, phase5a, cfg, status_row, failures)
    return status_df, failures
