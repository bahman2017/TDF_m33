"""Phase 6F Tier B public pilot gates (P1–P6), separate from Corbelli G gates."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

from tdf_m33.maps.gates import GateResult, run_data_gates
from tdf_m33.maps.public_pilot_inventory import (
    PUBLIC_PILOT_CLAIM_LABEL,
    PUBLIC_PILOT_REGISTRY,
    load_public_pilot_registry,
    _find_data_files,
)
from tdf_m33.maps.reprojection import VALIDATED_WCS_REPROJECTION_AVAILABLE

# Public-pilot reprojection is a separate implementation track from Corbelli G8.
PUBLIC_PILOT_REPROJECTION_AVAILABLE: bool = False

PUBLIC_PILOT_HI_DIRS = (
    "data/raw/phase6f/public_pilot/hi_lglbs",
    "data/raw/phase6f/public_pilot/hi_koch2018",
)
PUBLIC_PILOT_STELLAR_DIRS = (
    "data/raw/phase6f/public_pilot/stellar_s4g_irac",
    "data/raw/phase6f/public_pilot/stellar_lvl_irac",
)
PUBLIC_PILOT_CO_DIR = "data/raw/phase6f/public_pilot/co_iram_lp006"


@dataclass
class PublicPilotGateReport:
    gates: list[GateResult]
    public_pilot_ready: bool
    claim_label: str = PUBLIC_PILOT_CLAIM_LABEL
    blocked_message: str | None = None

    def to_rows(self) -> list[dict[str, Any]]:
        return [asdict(g) for g in self.gates]


def _has_hi_staged(repo_root: Path) -> tuple[bool, str]:
    for rel in PUBLIC_PILOT_HI_DIRS:
        files = _find_data_files(repo_root / rel)
        if files:
            return True, f"{len(files)} FITS under {rel}"
    return False, "No public HI FITS in hi_lglbs/ or hi_koch2018/"


def _has_irac_staged(repo_root: Path) -> tuple[bool, str]:
    found_36 = found_45 = False
    details: list[str] = []
    for rel in PUBLIC_PILOT_STELLAR_DIRS:
        folder = repo_root / rel
        files = _find_data_files(folder)
        if not files:
            continue
        names = " ".join(f.name.lower() for f in files)
        if "3.6" in names or "i1" in names or "ch1" in names or "36" in names:
            found_36 = True
        if "4.5" in names or "i2" in names or "ch2" in names or "45" in names:
            found_45 = True
        if files:
            details.append(f"{rel}: {len(files)} file(s)")
    if found_36 and found_45:
        return True, "; ".join(details)
    if files := sum(len(_find_data_files(repo_root / r)) for r in PUBLIC_PILOT_STELLAR_DIRS):
        return False, f"{files} IRAC FITS staged but 3.6 and 4.5 µm channels not both identified"
    return False, "No IRAC FITS staged (need 3.6 and 4.5 µm mosaics)"


def _has_co_staged(repo_root: Path) -> tuple[bool, str]:
    files = _find_data_files(repo_root / PUBLIC_PILOT_CO_DIR)
    if files:
        return True, f"{len(files)} FITS under {PUBLIC_PILOT_CO_DIR}"
    return False, "No CO(2-1) FITS in co_iram_lp006/"


def check_p1_public_hi(repo_root: Path) -> GateResult:
    ok, msg = _has_hi_staged(repo_root)
    if ok:
        return GateResult("P1_public_hi_map_available", "PASS", msg)
    return GateResult(
        "P1_public_hi_map_available",
        "PENDING",
        f"{msg}. Manual download required (LGLBS or Koch 2018).",
    )


def check_p2_public_stellar(repo_root: Path) -> GateResult:
    ok, msg = _has_irac_staged(repo_root)
    if ok:
        return GateResult("P2_public_stellar_irac_available", "PASS", msg)
    return GateResult(
        "P2_public_stellar_irac_available",
        "PENDING",
        f"{msg}. IRAC proxy - not Corbelli BVIgi map.",
    )


def check_p3_public_co(repo_root: Path) -> GateResult:
    ok, msg = _has_co_staged(repo_root)
    if ok:
        return GateResult("P3_public_co_or_h2_available", "PASS", msg)
    return GateResult(
        "P3_public_co_or_h2_available",
        "PENDING",
        f"{msg}. IRAM LP006 manual download.",
    )


def check_p4_public_wcs(repo_root: Path, p1: GateResult, p2: GateResult, p3: GateResult) -> GateResult:
    if p1.status != "PASS" and p2.status != "PASS" and p3.status != "PASS":
        return GateResult(
            "P4_public_wcs_metadata_available",
            "PENDING",
            "No staged public pilot maps to verify WCS.",
        )
    try:
        from astropy.io import fits
        from astropy.wcs import WCS
    except ImportError:
        return GateResult(
            "P4_public_wcs_metadata_available",
            "PENDING",
            "astropy required for WCS verification on staged files.",
        )

    checked = 0
    wcs_ok = 0
    for rel in (*PUBLIC_PILOT_HI_DIRS, *PUBLIC_PILOT_STELLAR_DIRS, PUBLIC_PILOT_CO_DIR):
        for path in _find_data_files(repo_root / rel)[:3]:
            checked += 1
            try:
                with fits.open(path, memmap=False) as hdul:
                    wcs = WCS(hdul[0].header)
                    if wcs.has_celestial:
                        wcs_ok += 1
            except Exception:
                pass
    if checked == 0:
        return GateResult("P4_public_wcs_metadata_available", "PENDING", "No files to check.")
    if wcs_ok == checked:
        return GateResult(
            "P4_public_wcs_metadata_available",
            "PASS",
            f"WCS present on {wcs_ok}/{checked} sampled FITS.",
        )
    return GateResult(
        "P4_public_wcs_metadata_available",
        "FAIL",
        f"WCS incomplete: {wcs_ok}/{checked} sampled FITS have celestial WCS.",
    )


def check_p5_public_license(repo_root: Path) -> GateResult:
    reg_path = repo_root / PUBLIC_PILOT_REGISTRY
    if not reg_path.is_file():
        return GateResult(
            "P5_public_license_and_citation_documented",
            "FAIL",
            "Public pilot source registry missing.",
        )
    registry = load_public_pilot_registry(repo_root)
    sources = registry.get("sources", [])
    if not sources:
        return GateResult(
            "P5_public_license_and_citation_documented",
            "FAIL",
            "Registry has no sources.",
        )
    missing_citation = [
        s.get("id") for s in sources if isinstance(s, dict) and not s.get("citation")
    ]
    if missing_citation:
        return GateResult(
            "P5_public_license_and_citation_documented",
            "PARTIAL",
            f"Citations missing for: {missing_citation}",
        )
    return GateResult(
        "P5_public_license_and_citation_documented",
        "PARTIAL",
        "Registry citations and license notes documented; confirm per-file on download.",
        {"registry": str(reg_path.relative_to(repo_root)), "n_sources": len(sources)},
    )


def check_p6_public_reprojection() -> GateResult:
    if PUBLIC_PILOT_REPROJECTION_AVAILABLE and VALIDATED_WCS_REPROJECTION_AVAILABLE:
        return GateResult(
            "P6_public_reprojection_ready",
            "PASS",
            "Validated public-pilot WCS-to-disk-plane reprojection available.",
        )
    return GateResult(
        "P6_public_reprojection_ready",
        "FAIL",
        "Validated public-pilot reprojection not implemented; "
        "PUBLIC_PILOT_REPROJECTION_AVAILABLE=False.",
        {
            "public_pilot_reprojection": PUBLIC_PILOT_REPROJECTION_AVAILABLE,
            "corbelli_g8_flag": VALIDATED_WCS_REPROJECTION_AVAILABLE,
        },
    )


def run_public_pilot_gates(repo_root: Path) -> PublicPilotGateReport:
    """Evaluate P1–P6; independent of Corbelli scientific_ready."""
    p1 = check_p1_public_hi(repo_root)
    p2 = check_p2_public_stellar(repo_root)
    p3 = check_p3_public_co(repo_root)
    p4 = check_p4_public_wcs(repo_root, p1, p2, p3)
    p5 = check_p5_public_license(repo_root)
    p6 = check_p6_public_reprojection()

    gates = [p1, p2, p3, p4, p5, p6]
    required = [p1, p2, p3, p4, p5, p6]
    public_pilot_ready = all(g.status == "PASS" for g in required)

    blocked = None
    if not public_pilot_ready:
        blocked = "PUBLIC_PILOT_NOT_READY_PENDING_DOWNLOADS_OR_REPROJECTION"

    return PublicPilotGateReport(
        gates=gates,
        public_pilot_ready=public_pilot_ready,
        blocked_message=blocked,
    )


def write_public_pilot_gate_csv(path: Path, report: PublicPilotGateReport) -> None:
    import csv

    path.parent.mkdir(parents=True, exist_ok=True)
    rows = report.to_rows()
    if not rows:
        return
    with path.open("w", newline="\n", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)


def write_public_pilot_gate_report_md(path: Path, report: PublicPilotGateReport) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Phase 6F public pilot gate report (P1–P6)",
        "",
        f"**Claim label:** `{report.claim_label}`",
        f"**public_pilot_ready:** `{report.public_pilot_ready}`",
        "",
        "**Not Corbelli 2014 primary reconstruction.** G1/G2/G8 Corbelli gates are separate.",
        "",
        "| Gate | Status | Message |",
        "|------|--------|---------|",
    ]
    for g in report.gates:
        msg = g.message.replace("|", "\\|")[:120]
        lines.append(f"| {g.gate_id} | {g.status} | {msg} |")
    if report.blocked_message:
        lines.extend(["", f"**Blocked:** `{report.blocked_message}`"])
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def tier_b_cannot_pass_corbelli_gates(repo_root: Path) -> bool:
    """True when Corbelli G1/G2 remain FAIL (Tier B must not satisfy primary gates)."""
    report = run_data_gates(repo_root)
    g1 = next(g for g in report.gates if g.gate_id == "G1_primary_hi_surface_density_map")
    g2 = next(
        g for g in report.gates
        if g.gate_id == "G2_primary_stellar_surface_density_or_mass_map"
    )
    return g1.status == "FAIL" and g2.status == "FAIL"
