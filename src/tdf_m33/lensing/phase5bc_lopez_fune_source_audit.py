"""Phase 5B-C: López Fune et al. 2017 source acquisition and extraction audit."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd
import yaml

from tdf_m33.data.source_status import sha256_file

SOURCE_ID = "lopez_fune_salucci_corbelli_2017"
PDF_REL = "data/raw/downloads/lopez_fune_salucci_corbelli_2017_m33.pdf"
SHA_REL = "data/raw/downloads/lopez_fune_salucci_corbelli_2017_m33.pdf.sha256"
EXTRACTION_PLAN_REL = "docs/lopez_fune_2017_extraction_plan.md"
REGISTRY_MARKER = "lopez_fune_salucci_corbelli_2017"
FORBIDDEN_COMPARISON_GLOBS = (
    "phase5c_*comparison*.csv",
    "phase5c_*limits*.csv",
    "lopez_fune_*comparison*.csv",
)


def _repo_root(config_path: Path) -> Path:
    return config_path.resolve().parents[1]


def load_phase5bc_config(config_path: Path) -> dict[str, Any]:
    with config_path.open() as f:
        cfg = yaml.safe_load(f)
    lens = cfg.get("tdf", {}).get("lensing", {})
    limits = lens.get("observational_limits", {})
    src = limits.get("lopez_fune_2017", {})
    phys = lens.get("physical_calibration", {})
    return {
        "observational_limits_enabled": bool(limits.get("enabled", False)),
        "limits_status": str(limits.get("status", "")),
        "selected_source_id": limits.get("selected_source_id"),
        "physical_calibration_enabled": bool(phys.get("enabled", False)),
        "output_units": str(phys.get("output_units", "normalized_proxy")),
        "source_acquisition_status": str(src.get("acquisition_status", "located")),
        "pdf_path": str(src.get("pdf_path", PDF_REL)),
        "checksum_path": str(src.get("checksum_path", SHA_REL)),
    }


def verify_pdf_and_checksum(repo_root: Path, cfg: dict[str, Any]) -> tuple[bool, str, str]:
    pdf_path = repo_root / cfg["pdf_path"]
    sha_path = repo_root / cfg["checksum_path"]
    if not pdf_path.is_file():
        raise FileNotFoundError(f"PDF missing: {pdf_path}")
    if not sha_path.is_file():
        raise FileNotFoundError(f"checksum sidecar missing: {sha_path}")
    expected_line = sha_path.read_text(encoding="utf-8").strip().split()[0]
    actual = sha256_file(pdf_path)
    if expected_line != actual:
        raise ValueError(
            f"SHA-256 mismatch for {pdf_path.name}: "
            f"sidecar={expected_line[:16]}... computed={actual[:16]}..."
        )
    return True, str(pdf_path), actual


def verify_extraction_plan(repo_root: Path) -> None:
    plan = repo_root / EXTRACTION_PLAN_REL
    if not plan.is_file():
        raise FileNotFoundError(f"extraction plan missing: {plan}")


def verify_registry_documented(repo_root: Path) -> None:
    data_sources = repo_root / "docs" / "data_sources.md"
    text = data_sources.read_text(encoding="utf-8")
    if REGISTRY_MARKER not in text:
        raise ValueError(f"{REGISTRY_MARKER} missing from data_sources.md")
    chunk = text.split(REGISTRY_MARKER, 1)[1][:1200]
    if "documented" not in chunk.lower():
        raise ValueError(
            f"{REGISTRY_MARKER} not marked documented in data_sources.md"
        )


def verify_no_comparison_tables(repo_root: Path) -> None:
    for pattern in FORBIDDEN_COMPARISON_GLOBS:
        hits = list(repo_root.glob(f"outputs/tables/{pattern}"))
        if hits:
            raise ValueError(f"comparison table must not exist yet: {hits[0]}")


def build_status_row(
    cfg: dict[str, Any],
    *,
    pdf_path: str,
    sha256_hex: str,
    repo_root: Path,
) -> dict[str, Any]:
    return {
        "phase": "5B-C",
        "audit_type": "lopez_fune_2017_source_acquisition",
        "source_id": SOURCE_ID,
        "pdf_path": pdf_path,
        "checksum_path": str(repo_root / cfg["checksum_path"]),
        "sha256": sha256_hex,
        "extraction_plan_path": str(repo_root / EXTRACTION_PLAN_REL),
        "acquisition_status": "documented",
        "observational_limits_enabled": cfg["observational_limits_enabled"],
        "limits_status": cfg["limits_status"],
        "selected_source_id": cfg["selected_source_id"] or "",
        "physical_calibration_enabled": cfg["physical_calibration_enabled"],
        "output_units": cfg["output_units"],
        "numerical_comparison_performed": False,
        "comparison_tables_created": False,
        "physical_arcsec_conversion": False,
        "alpha_tau_scale_fitted": False,
        "direct_lensing_measurement": False,
        "circularity_note": (
            "Dynamics/rotation-based; overlaps Corbelli 2014 inputs; "
            "not independent lensing"
        ),
        "recommendation": (
            "Phase 5C: digitize Fig. 6 / transcribe NFW-BRK parameters to "
            "data/raw/extracted/; then upper_bound_consistency on enclosed "
            "mass only; keep normalized_proxy deflection"
        ),
    }


def write_audit_report(
    path: Path,
    status_row: dict[str, Any],
    cfg: dict[str, Any],
) -> None:
    lines = [
        "# Phase 5B-C — López Fune et al. 2017 source acquisition audit",
        "",
        "**Scope:** PDF acquisition and extraction planning only. "
        "No observational comparison. No numerical limit tables.",
        "",
        "## Source",
        "",
        f"- source_id: `{SOURCE_ID}`",
        f"- PDF: `{status_row['pdf_path']}`",
        f"- SHA-256: `{status_row['sha256']}`",
        f"- Checksum file: `{status_row['checksum_path']}`",
        f"- Extraction plan: `{status_row['extraction_plan_path']}`",
        f"- acquisition_status: **{status_row['acquisition_status']}**",
        "",
        "## Safeguards",
        "",
        f"- observational_limits.enabled: **{cfg['observational_limits_enabled']}**",
        f"- output_units: **{cfg['output_units']}**",
        "- No Phase 5C comparison tables created.",
        "- No `alpha_tau_scale` fitting; no arcsec conversion.",
        "- Not a direct lensing measurement; not a dark-matter disproof.",
        f"- Circularity: {status_row['circularity_note']}",
        "",
        "## Next phase (5C)",
        "",
        status_row["recommendation"],
        "",
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def run_phase5bc_lopez_fune_source_audit(
    config_path: Path,
    status_csv_path: Path,
    report_path: Path,
) -> pd.DataFrame:
    """Run Phase 5B-C acquisition audit."""
    repo_root = _repo_root(config_path)
    cfg = load_phase5bc_config(config_path)

    if cfg["observational_limits_enabled"]:
        raise ValueError("observational_limits.enabled must remain false")
    if cfg["physical_calibration_enabled"]:
        raise ValueError("physical_calibration.enabled must remain false")
    if cfg["selected_source_id"] != SOURCE_ID:
        raise ValueError(f"selected_source_id must be {SOURCE_ID!r}")
    if cfg["output_units"] != "normalized_proxy":
        raise ValueError("output_units must remain normalized_proxy")

    verify_extraction_plan(repo_root)
    ok, pdf_path, digest = verify_pdf_and_checksum(repo_root, cfg)
    assert ok
    verify_registry_documented(repo_root)
    verify_no_comparison_tables(repo_root)

    status_row = build_status_row(cfg, pdf_path=pdf_path, sha256_hex=digest, repo_root=repo_root)
    status_df = pd.DataFrame([status_row])
    status_csv_path.parent.mkdir(parents=True, exist_ok=True)
    status_df.to_csv(status_csv_path, index=False)
    write_audit_report(report_path, status_row, cfg)
    return status_df
