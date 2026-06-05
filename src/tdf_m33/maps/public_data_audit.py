"""Phase 6F public M33 data candidate registry audit (Tier A/B/C)."""

from __future__ import annotations

import csv
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

import yaml

PUBLIC_CANDIDATE_REGISTRY = (
    "data/raw/phase6f/manifest/phase6f_public_candidate_registry.yaml"
)

CSV_COLUMNS = [
    "id",
    "tier",
    "product_type",
    "source_name",
    "citation",
    "url_or_doi",
    "access_status",
    "license_or_usage_note",
    "download_status",
    "expected_file_type",
    "expected_units",
    "login_required",
    "suitable_for",
    "can_satisfy_primary_corbelli_gate",
    "can_satisfy_public_pilot_gate",
    "notes",
]


@dataclass
class PublicCandidateRow:
    id: str
    tier: str
    product_type: str
    source_name: str
    citation: str
    url_or_doi: str
    access_status: str
    license_or_usage_note: str
    download_status: str
    expected_file_type: str = ""
    expected_units: str = ""
    login_required: str = "unknown"
    suitable_for: str = ""
    can_satisfy_primary_corbelli_gate: bool = False
    can_satisfy_public_pilot_gate: bool = False
    notes: str = ""


@dataclass
class PublicDataAuditReport:
    candidates: list[PublicCandidateRow] = field(default_factory=list)
    tier_a_count: int = 0
    tier_b_count: int = 0
    tier_c_count: int = 0
    corbelli_primary_fits_found: bool = False
    corbelli_primary_fits_notes: str = ""


def load_public_candidate_registry(repo_root: Path) -> dict[str, Any]:
    path = repo_root / PUBLIC_CANDIDATE_REGISTRY
    if not path.is_file():
        raise FileNotFoundError(f"Missing public candidate registry: {path}")
    with path.open(encoding="utf-8") as handle:
        data = yaml.safe_load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"Invalid registry YAML at {path}")
    return data


def _parse_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.strip().lower() in {"true", "yes", "1"}
    return bool(value)


def registry_to_rows(registry: dict[str, Any]) -> list[PublicCandidateRow]:
    rows: list[PublicCandidateRow] = []
    for entry in registry.get("candidates", []):
        if not isinstance(entry, dict):
            continue
        rows.append(
            PublicCandidateRow(
                id=str(entry.get("id", "")),
                tier=str(entry.get("tier", "")),
                product_type=str(entry.get("product_type", "")),
                source_name=str(entry.get("source_name", "")),
                citation=str(entry.get("citation", "")),
                url_or_doi=str(entry.get("url_or_doi", "")),
                access_status=str(entry.get("access_status", "")),
                license_or_usage_note=str(entry.get("license_or_usage_note", "")),
                download_status=str(entry.get("download_status", "")),
                expected_file_type=str(entry.get("expected_file_type", "")),
                expected_units=str(entry.get("expected_units", "")),
                login_required=str(entry.get("login_required", "unknown")),
                suitable_for=str(entry.get("suitable_for", "")),
                can_satisfy_primary_corbelli_gate=_parse_bool(
                    entry.get("can_satisfy_primary_corbelli_gate", False)
                ),
                can_satisfy_public_pilot_gate=_parse_bool(
                    entry.get("can_satisfy_public_pilot_gate", False)
                ),
                notes=str(entry.get("notes", "")),
            )
        )
    return rows


def run_public_data_audit(repo_root: Path) -> PublicDataAuditReport:
    registry = load_public_candidate_registry(repo_root)
    rows = registry_to_rows(registry)
    tier_a = sum(1 for r in rows if r.tier.upper().startswith("TIER_A"))
    tier_b = sum(1 for r in rows if r.tier.upper().startswith("TIER_B"))
    tier_c = sum(1 for r in rows if r.tier.upper().startswith("TIER_C"))

    corbelli_fits = [
        r
        for r in rows
        if r.tier.upper().startswith("TIER_A")
        and "fits" in r.expected_file_type.lower()
        and r.download_status.lower() in {"available_public", "direct_download"}
    ]
    if corbelli_fits:
        found = True
        notes = "; ".join(f"{r.id}: {r.download_status}" for r in corbelli_fits)
    else:
        found = False
        notes = (
            "No Tier A Corbelli 2014 primary HI or BVIgi stellar FITS identified as "
            "direct public download. Table-only / author-request routes remain."
        )

    return PublicDataAuditReport(
        candidates=rows,
        tier_a_count=tier_a,
        tier_b_count=tier_b,
        tier_c_count=tier_c,
        corbelli_primary_fits_found=found,
        corbelli_primary_fits_notes=notes,
    )


def write_public_candidates_csv(path: Path, report: PublicDataAuditReport) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=CSV_COLUMNS)
        writer.writeheader()
        for row in report.candidates:
            payload = asdict(row)
            payload["can_satisfy_primary_corbelli_gate"] = str(
                payload["can_satisfy_primary_corbelli_gate"]
            )
            payload["can_satisfy_public_pilot_gate"] = str(
                payload["can_satisfy_public_pilot_gate"]
            )
            writer.writerow(payload)


def write_public_data_audit_report_md(
    path: Path, report: PublicDataAuditReport, registry: dict[str, Any]
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    audit_date = registry.get("audit_date", "unknown")
    prepared_by = registry.get("prepared_by", "phase6f-public-data-acquisition-audit")

    lines = [
        "# Phase 6F public M33 data acquisition audit",
        "",
        f"- Audit date (registry): `{audit_date}`",
        f"- Prepared by: `{prepared_by}`",
        f"- Candidates catalogued: `{len(report.candidates)}`",
        f"- Tier A: `{report.tier_a_count}` | Tier B: `{report.tier_b_count}` | "
        f"Tier C: `{report.tier_c_count}`",
        "",
        "**Claim control:** Tier B products are **not** exact Corbelli 2014 primary maps. "
        "They cannot PASS G1/G2 Corbelli gates. Strict Corbelli scientific Phase 6F "
        "remains blocked.",
        "",
        "## Exact Corbelli 2014 primary FITS (Tier A)",
        "",
        f"- Direct public Corbelli primary FITS found: **`{report.corbelli_primary_fits_found}`**",
        f"- Notes: {report.corbelli_primary_fits_notes}",
        "",
        "## Recommended fastest Tier B public pilot path",
        "",
        "1. **HI:** LGLBS HI Data Release v1.0 (CANFAR) — wide-field 21 cm products for M33 "
        "(login required; not Corbelli reduction).",
        "2. **Stellar proxy:** Spitzer S4G or LVL IRAC 3.6 + 4.5 µm mosaics (IRSA) → "
        "derive M_* surface density via documented M/L prescription (Querejeta/Meidt-style).",
        "3. **H2/CO:** IRAM LP006 CO(2-1) integrated map / cube (`https://www.iram.fr/ILPA/LP006/`).",
        "4. **Future pilot gates P1–P6** (documented only; not active in strict Corbelli pipeline).",
        "",
        "## Candidate summary",
        "",
        "| id | tier | product | download_status | Corbelli G1/G2? | public pilot? |",
        "|----|------|---------|-----------------|-----------------|---------------|",
    ]
    for row in report.candidates:
        lines.append(
            f"| {row.id} | {row.tier} | {row.product_type} | {row.download_status} | "
            f"{row.can_satisfy_primary_corbelli_gate} | {row.can_satisfy_public_pilot_gate} |"
        )

    lines.extend(
        [
            "",
            "## Future public pilot gates (diagnostic only; not active)",
            "",
            "| Gate | Description |",
            "|------|-------------|",
            "| P1_public_hi_map_available | Public HI moment map or cube staged |",
            "| P2_public_stellar_mass_proxy_available | IRAC-derived stellar mass proxy map |",
            "| P3_public_h2_or_co_available | CO(2-1) or H2 proxy map staged |",
            "| P4_public_wcs_metadata_available | WCS/units verified on Tier B products |",
            "| P5_public_license_and_citation_documented | License + citations recorded |",
            "| P6_public_reprojection_ready | Validated reprojection for Tier B grid |",
            "",
            "See `docs/phase6f_data_tiers.md` and `docs/phase6f_public_pilot_limitations.md`.",
        ]
    )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
