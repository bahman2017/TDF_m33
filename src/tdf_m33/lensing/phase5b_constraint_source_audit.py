"""Phase 5B-B: observational constraint source review audit."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd
import yaml

REQUIRED_UNITS = "normalized_proxy"
SOURCE_REVIEW_DOC = "docs/lensing_calibration_and_limits_plan.md"
CONSTRAINT_REVIEW_DOC = "docs/lensing_constraint_source_review.md"
DATA_SOURCES_DOC = "docs/data_sources.md"

# Registry source_ids that must appear in data_sources.md (Phase 5B-B)
REQUIRED_REGISTRY_SOURCE_IDS = (
    "lopez_fune_salucci_corbelli_2017",
    "kam_et_al_2018_m33_hi_masses",
    "m33_direct_weak_lensing_gap",
    "corbelli_et_al_2014",
    "combo17_weak_lensing_statistical",
)


def load_phase5bb_config(config_path: Path) -> dict[str, Any]:
    with config_path.open() as f:
        cfg = yaml.safe_load(f)
    lens = cfg.get("tdf", {}).get("lensing", {})
    limits = lens.get("observational_limits", {})
    phys = lens.get("physical_calibration", {})
    return {
        "observational_limits_enabled": bool(limits.get("enabled", False)),
        "limits_status": str(limits.get("status", "planned")),
        "candidate_source_ids": list(limits.get("candidate_source_ids", [])),
        "selected_source_id": limits.get("selected_source_id"),
        "limits_source_id": limits.get("limits_source_id"),
        "physical_calibration_enabled": bool(phys.get("enabled", False)),
        "output_units": str(phys.get("output_units", REQUIRED_UNITS)),
        "compare_to_observational_limits": bool(lens.get("compare_to_observational_limits", False)),
    }


def _repo_root_from_config(config_path: Path) -> Path:
    return config_path.resolve().parents[1]


def verify_review_documents(repo_root: Path) -> list[str]:
    failures: list[str] = []
    for rel in (CONSTRAINT_REVIEW_DOC, "docs/lensing_calibration_and_limits_plan.md"):
        if not (repo_root / rel).is_file():
            failures.append(f"missing required doc: {rel}")
    return failures


def verify_registry_in_data_sources(repo_root: Path) -> list[str]:
    path = repo_root / DATA_SOURCES_DOC
    if not path.is_file():
        return [f"missing {DATA_SOURCES_DOC}"]
    text = path.read_text(encoding="utf-8")
    failures: list[str] = []
    if "Lensing / deflection constraint registry" not in text:
        failures.append("data_sources.md missing lensing registry section")
    for sid in REQUIRED_REGISTRY_SOURCE_IDS:
        if f"`{sid}`" not in text:
            failures.append(f"registry missing source_id {sid!r}")
    return failures


def build_constraint_source_status_row(
    cfg: dict[str, Any],
    *,
    repo_root: Path,
) -> dict[str, Any]:
    return {
        "phase": "5B-B",
        "audit_type": "constraint_source_review",
        "source_review_doc": str(repo_root / CONSTRAINT_REVIEW_DOC),
        "calibration_plan_doc": str(repo_root / SOURCE_REVIEW_DOC),
        "observational_limits_enabled": cfg["observational_limits_enabled"],
        "limits_status": cfg["limits_status"],
        "candidate_source_ids": ";".join(cfg["candidate_source_ids"]),
        "selected_source_id": cfg["selected_source_id"] or "",
        "limits_source_id": cfg["limits_source_id"] or "",
        "physical_calibration_enabled": cfg["physical_calibration_enabled"],
        "output_units": cfg["output_units"],
        "numerical_comparison_performed": False,
        "physical_conversion_performed": False,
        "alpha_tau_scale_fitted": False,
        "separate_halo_introduced": False,
        "lensing_only_tau_fit": False,
        "phase5c_ready_any_source": bool(cfg["selected_source_id"]),
        "recommendation": (
            "Phase 5C: extract cited dynamical tables for selected_source_id "
            f"({cfg['selected_source_id'] or 'none'}); compare enclosed-mass "
            "metrics only (upper_bound_consistency); keep deflection in "
            "normalized_proxy until physical calibration is documented"
        ),
    }


def write_constraint_audit_report(
    path: Path,
    cfg: dict[str, Any],
    status_row: dict[str, Any],
    failures: list[str],
) -> None:
    lines = [
        "# Phase 5B-B — Constraint source review audit",
        "",
        "**Scope:** Source registration and planning only. No observational comparison. "
        "No physical lensing claim.",
        "",
        "## Documents",
        "",
        f"- Source review: `{status_row['source_review_doc']}`",
        f"- Calibration plan: `{status_row['calibration_plan_doc']}`",
        f"- Registry: `{DATA_SOURCES_DOC}`",
        "",
        "## Config (unchanged safeguards)",
        "",
        f"- observational_limits.enabled: **{cfg['observational_limits_enabled']}**",
        f"- limits.status: **{cfg['limits_status']}**",
        f"- selected_source_id (Phase 5C candidate): "
        f"`{cfg['selected_source_id'] or 'none'}`",
        f"- candidate_source_ids: `{', '.join(cfg['candidate_source_ids']) or 'none'}`",
        f"- physical_calibration.enabled: **{cfg['physical_calibration_enabled']}**",
        f"- output_units: **{cfg['output_units']}**",
        "",
        "## Phase 5A / TDF branch",
        "",
        "- Same frozen τ map (`tdf_lowparam_3knot`); no lensing-only fit.",
        "- No separate dark-matter halo in the TDF lensing pathway.",
        "- No `alpha_tau_scale` fitting to observations.",
        "- No numeric limit comparison output in this phase.",
        "",
        "## Weak lensing finding",
        "",
        "No M33-specific direct weak-lensing constraint source was registered for "
        "comparison. See `m33_direct_weak_lensing_gap` in the registry.",
        "",
        "## Validation",
        "",
    ]
    if failures:
        lines.append("**FAILURES:**")
        for f in failures:
            lines.append(f"- {f}")
    else:
        lines.append("- All Phase 5B-B checks **PASS**.")
    lines.extend(
        [
            "",
            "## Next phase (5C)",
            "",
            status_row["recommendation"],
            "",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def run_phase5b_constraint_source_audit(
    config_path: Path,
    status_csv_path: Path,
    report_path: Path,
) -> pd.DataFrame:
    """Run Phase 5B-B source-review audit."""
    repo_root = _repo_root_from_config(config_path)
    cfg = load_phase5bb_config(config_path)

    failures = verify_review_documents(repo_root)
    failures.extend(verify_registry_in_data_sources(repo_root))

    if cfg["observational_limits_enabled"]:
        failures.append("observational_limits.enabled must remain false in Phase 5B-B")
    if cfg["physical_calibration_enabled"]:
        failures.append("physical_calibration.enabled must remain false in Phase 5B-B")
    if cfg["output_units"] != REQUIRED_UNITS:
        failures.append(f"output_units must be {REQUIRED_UNITS!r}")
    if cfg["compare_to_observational_limits"]:
        failures.append("compare_to_observational_limits must be false")
    if not cfg["candidate_source_ids"]:
        failures.append("candidate_source_ids must be non-empty")

    if failures:
        raise ValueError("; ".join(failures))

    status_row = build_constraint_source_status_row(cfg, repo_root=repo_root)
    status_df = pd.DataFrame([status_row])
    status_csv_path.parent.mkdir(parents=True, exist_ok=True)
    status_df.to_csv(status_csv_path, index=False)
    write_constraint_audit_report(report_path, cfg, status_row, failures)
    return status_df
