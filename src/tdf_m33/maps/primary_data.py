"""Phase 6F primary Corbelli map inventory and validation helpers."""

from __future__ import annotations

import csv
import hashlib
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Literal

PRIMARY_ROOT = "data/raw/phase6f/primary"
PRIMARY_CHECKSUMS = f"{PRIMARY_ROOT}/CHECKSUMS.sha256"

PRIMARY_SUBDIRS: dict[str, tuple[str, str]] = {
    "corbelli2014_hi": (
        "G1_primary_hi_surface_density_map",
        "Corbelli 2014 VLA+GBT HI surface-density map",
    ),
    "corbelli2014_stellar_mass": (
        "G2_primary_stellar_surface_density_or_mass_map",
        "Corbelli 2014 BVIgi stellar surface-density or mass map",
    ),
    "corbelli2014_velocity_field": (
        "supplementary_velocity_field",
        "2D HI velocity field (optional; supports G4 metadata)",
    ),
    "corbelli2014_uncertainty_masks": (
        "G6_mask_or_uncertainty",
        "Uncertainty maps, noise, or masks (supports G6)",
    ),
}

InventoryStatus = Literal[
    "MISSING_DIRECTORY",
    "NO_FITS_FILES",
    "INSPECTED",
    "INSPECT_FAILED",
]


@dataclass
class PrimaryFileRecord:
    filename: str
    relative_path: str
    product_type: str
    gate_contribution: str
    status: InventoryStatus
    shape: str = ""
    has_wcs: str = ""
    bunit: str = ""
    beam_major_arcsec: str = ""
    beam_minor_arcsec: str = ""
    pixel_scale_arcsec: str = ""
    checksum_sha256: str = ""
    notes: str = ""


@dataclass
class PrimaryValidationReport:
    records: list[PrimaryFileRecord] = field(default_factory=list)
    primary_root_exists: bool = False
    n_fits_files: int = 0
    astropy_available: bool = False

    @property
    def complete_for_g1(self) -> bool:
        return any(
            r.product_type == "corbelli2014_hi"
            and r.status == "INSPECTED"
            and r.has_wcs.lower() == "true"
            for r in self.records
        )

    @property
    def complete_for_g2(self) -> bool:
        return any(
            r.product_type == "corbelli2014_stellar_mass" and r.status == "INSPECTED"
            for r in self.records
        )


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _require_astropy() -> Any:
    try:
        from astropy.io import fits
        from astropy.wcs import WCS
    except ImportError as exc:
        raise ImportError(
            "astropy is required for Phase 6F primary map validation. "
            "Install with: python -m pip install astropy"
        ) from exc
    return fits, WCS


def inspect_fits_file(path: Path, repo_root: Path) -> dict[str, Any]:
    """Read FITS metadata with astropy."""
    fits, WCS = _require_astropy()
    rel = str(path.relative_to(repo_root))
    checksum = sha256_file(path)
    info: dict[str, Any] = {
        "filename": path.name,
        "relative_path": rel,
        "checksum_sha256": checksum,
        "status": "INSPECTED",
    }
    try:
        with fits.open(path, memmap=False) as hdul:
            hdu = hdul[0]
            data = hdu.data
            header = hdu.header
            shape = "" if data is None else "x".join(str(s) for s in data.shape)
            info["shape"] = shape
            info["bunit"] = str(header.get("BUNIT", "")).strip()
            info["beam_major_arcsec"] = str(header.get("BMAJ", "")).strip()
            info["beam_minor_arcsec"] = str(header.get("BMIN", "")).strip()
            cdelt = header.get("CDELT1")
            if cdelt not in (None, ""):
                try:
                    info["pixel_scale_arcsec"] = f"{abs(float(cdelt)) * 3600.0:.6g}"
                except (TypeError, ValueError):
                    info["pixel_scale_arcsec"] = ""
            else:
                info["pixel_scale_arcsec"] = ""
            try:
                wcs = WCS(header)
                info["has_wcs"] = str(bool(wcs.has_celestial))
            except Exception:
                info["has_wcs"] = "false"
    except Exception as exc:
        info["status"] = "INSPECT_FAILED"
        info["notes"] = str(exc)
    return info


def scan_primary_data(repo_root: Path, *, require_astropy: bool = True) -> PrimaryValidationReport:
    """Scan primary Corbelli directories and build an inventory."""
    astropy_available = True
    if require_astropy:
        try:
            _require_astropy()
        except ImportError:
            astropy_available = False

    primary_root = repo_root / PRIMARY_ROOT
    records: list[PrimaryFileRecord] = []
    n_fits = 0

    for subdir, (gate_id, description) in PRIMARY_SUBDIRS.items():
        directory = primary_root / subdir
        if not directory.is_dir():
            records.append(
                PrimaryFileRecord(
                    filename="",
                    relative_path=str(directory.relative_to(repo_root)),
                    product_type=subdir,
                    gate_contribution=gate_id,
                    status="MISSING_DIRECTORY",
                    notes=f"Expected directory not present. {description}",
                )
            )
            continue

        fits_files = sorted(
            p
            for p in directory.rglob("*")
            if p.is_file() and p.suffix.lower() in {".fits", ".fit", ".fts"}
        )
        if not fits_files:
            records.append(
                PrimaryFileRecord(
                    filename="",
                    relative_path=str(directory.relative_to(repo_root)),
                    product_type=subdir,
                    gate_contribution=gate_id,
                    status="NO_FITS_FILES",
                    notes=f"Directory exists but contains no FITS files. {description}",
                )
            )
            continue

        for fits_path in fits_files:
            n_fits += 1
            if not astropy_available:
                records.append(
                    PrimaryFileRecord(
                        filename=fits_path.name,
                        relative_path=str(fits_path.relative_to(repo_root)),
                        product_type=subdir,
                        gate_contribution=gate_id,
                        status="INSPECT_FAILED",
                        checksum_sha256=sha256_file(fits_path),
                        notes="astropy not installed; header inspection skipped",
                    )
                )
                continue

            meta = inspect_fits_file(fits_path, repo_root)
            records.append(
                PrimaryFileRecord(
                    filename=meta["filename"],
                    relative_path=meta["relative_path"],
                    product_type=subdir,
                    gate_contribution=gate_id,
                    status=meta["status"],
                    shape=meta.get("shape", ""),
                    has_wcs=meta.get("has_wcs", ""),
                    bunit=meta.get("bunit", ""),
                    beam_major_arcsec=meta.get("beam_major_arcsec", ""),
                    beam_minor_arcsec=meta.get("beam_minor_arcsec", ""),
                    pixel_scale_arcsec=meta.get("pixel_scale_arcsec", ""),
                    checksum_sha256=meta.get("checksum_sha256", ""),
                    notes=meta.get("notes", ""),
                )
            )

    return PrimaryValidationReport(
        records=records,
        primary_root_exists=primary_root.is_dir(),
        n_fits_files=n_fits,
        astropy_available=astropy_available,
    )


def write_primary_inventory_csv(path: Path, report: PrimaryValidationReport) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = list(asdict(PrimaryFileRecord("", "", "", "", "MISSING_DIRECTORY")).keys())
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for record in report.records:
            writer.writerow(asdict(record))


def write_primary_validation_report_md(
    path: Path, report: PrimaryValidationReport, repo_root: Path
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Phase 6F primary data validation report",
        "",
        "**Scope:** Inventory and FITS header inspection for Corbelli 2014 primary products.",
        "**Not a scientific τ-map result.** Strict mode remains blocked until G1, G2, G3, G4, "
        "G5, G7, and G8 pass.",
        "",
        f"- Repository: paths relative to repository root",
        f"- Primary root exists: `{report.primary_root_exists}`",
        f"- FITS files found: `{report.n_fits_files}`",
        f"- astropy available: `{report.astropy_available}`",
        f"- G1-ready (HI + WCS): `{report.complete_for_g1}`",
        f"- G2-ready (stellar): `{report.complete_for_g2}`",
        "",
        "## Inventory",
        "",
    ]
    if not report.records:
        lines.append("_No primary directories scanned._")
    else:
        lines.append(
            "| product_type | filename | status | gate | WCS | BUNIT | checksum |"
        )
        lines.append("|--------------|----------|--------|------|-----|-------|----------|")
        for rec in report.records:
            lines.append(
                f"| {rec.product_type} | {rec.filename or '—'} | {rec.status} | "
                f"{rec.gate_contribution} | {rec.has_wcs or '—'} | {rec.bunit or '—'} | "
                f"{rec.checksum_sha256[:12] + '…' if rec.checksum_sha256 else '—'} |"
            )

    lines.extend(
        [
            "",
            "## Gate implications (current run)",
            "",
            "- **G1:** FAIL until validated HI FITS present under "
            "`data/raw/phase6f/primary/corbelli2014_hi/`.",
            "- **G2:** FAIL until stellar FITS present under "
            "`data/raw/phase6f/primary/corbelli2014_stellar_mass/`.",
            "- **G8:** FAIL until validated WCS-to-disk-plane reprojection is implemented "
            "(see `docs/phase6f_validated_reprojection_design.md`).",
            "",
            "Reference-proxy Gratier 2010 FITS do **not** satisfy G1.",
        ]
    )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def collect_primary_fits_files(repo_root: Path) -> list[Path]:
    primary_root = repo_root / PRIMARY_ROOT
    if not primary_root.is_dir():
        return []
    return sorted(
        p
        for p in primary_root.rglob("*")
        if p.is_file() and p.suffix.lower() in {".fits", ".fit", ".fts"}
    )


def update_primary_checksums(repo_root: Path) -> tuple[Path, int]:
    """Write SHA-256 checksums for primary FITS files. Never modifies raw FITS."""
    primary_root = repo_root / PRIMARY_ROOT
    checksum_path = repo_root / PRIMARY_CHECKSUMS
    primary_root.mkdir(parents=True, exist_ok=True)
    files = collect_primary_fits_files(repo_root)
    lines: list[str] = []
    if not files:
        lines.append(
            "# No primary FITS files present. Add files under "
            "data/raw/phase6f/primary/ and re-run update_phase6f_primary_checksums.py"
        )
    else:
        for path in files:
            rel = path.relative_to(primary_root)
            digest = sha256_file(path)
            lines.append(f"{digest}  {rel.as_posix()}")
    checksum_path.write_text("\n".join(lines) + ("\n" if lines else ""), encoding="utf-8")
    return checksum_path, len(files)
