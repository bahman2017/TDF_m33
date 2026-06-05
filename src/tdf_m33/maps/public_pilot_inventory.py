"""Phase 6F Tier B public pilot data inventory and checksum helpers."""

from __future__ import annotations

import csv
import hashlib
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Literal

import yaml

PUBLIC_PILOT_ROOT = "data/raw/phase6f/public_pilot"
PUBLIC_PILOT_REGISTRY = (
    "data/raw/phase6f/public_pilot/manifest/phase6f_public_pilot_source_registry.yaml"
)
PUBLIC_PILOT_CHECKSUMS = f"{PUBLIC_PILOT_ROOT}/manifest/CHECKSUMS.sha256"
PUBLIC_PILOT_CLAIM_LABEL = "PUBLIC_DATA_PILOT_NOT_CORBELLI_PRIMARY"
INVENTORY_REPORT_REL = "outputs/reports/phase6f/phase6f_public_pilot_inventory_report.md"
FILES_CSV_REL = "outputs/tables/phase6f/phase6f_public_pilot_file_inventory.csv"
SUMMARY_CSV_REL = "outputs/tables/phase6f/phase6f_public_pilot_inventory.csv"

# Longest-first matching for double suffixes (.fits.gz).
PUBLIC_PILOT_FITS_EXTENSIONS: tuple[str, ...] = (
    ".fits.gz",
    ".fit.gz",
    ".fts.gz",
    ".fits",
    ".fit",
    ".fts",
)
PUBLIC_PILOT_FITS_EXTENSIONS_LOWER: frozenset[str] = frozenset(
    e.lower() for e in PUBLIC_PILOT_FITS_EXTENSIONS
)
# Backward-compatible alias for tests/docs referencing uncompressed suffixes only.
FITS_SUFFIXES = {".fits", ".fit", ".fts"}

InventoryStatus = Literal["PENDING_DOWNLOAD", "STAGED", "EMPTY_FOLDER", "BLOCKED"]

IRAC_36_HINTS = ("3.6", "i1", "ch1", "_36", "36um", "3_6")
IRAC_45_HINTS = ("4.5", "i2", "ch2", "_45", "45um", "4_5")


@dataclass
class PublicPilotInventoryRow:
    source_id: str
    target_folder: str
    product_type: str
    status: InventoryStatus
    n_files: int
    filenames: str
    claim_label: str
    registry_status: str
    notes: str = ""


@dataclass
class FitsFileRecord:
    relative_path: str
    source_id: str
    product_type: str
    target_folder: str
    filename: str
    size_bytes: int
    extension: str
    checksum_sha256: str
    claim_label: str
    naxis: str = ""
    shape: str = ""
    bunit: str = ""
    ctype1: str = ""
    ctype2: str = ""
    ctype3: str = ""
    cdelt1: str = ""
    cdelt2: str = ""
    crval1: str = ""
    crval2: str = ""
    crpix1: str = ""
    crpix2: str = ""
    bmaj_arcsec: str = ""
    bmin_arcsec: str = ""
    bpa_deg: str = ""
    restfrq_hz: str = ""
    has_wcs: str = ""
    compressed: str = "false"
    original_extension: str = ""
    header_read_status: str = ""
    inspect_status: str = ""
    inspect_notes: str = ""
    irac_channel: str = ""


@dataclass
class PublicPilotInventoryReport:
    rows: list[PublicPilotInventoryRow] = field(default_factory=list)
    file_records: list[FitsFileRecord] = field(default_factory=list)
    total_staged_files: int = 0
    claim_label: str = PUBLIC_PILOT_CLAIM_LABEL
    raw_files_committed: bool = False


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_public_pilot_registry(repo_root: Path) -> dict[str, Any]:
    path = repo_root / PUBLIC_PILOT_REGISTRY
    if not path.is_file():
        raise FileNotFoundError(f"Missing public pilot registry: {path}")
    with path.open(encoding="utf-8") as handle:
        data = yaml.safe_load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"Invalid registry at {path}")
    return data


def _patch_last_inventory_validation(repo_root: Path, report: PublicPilotInventoryReport) -> None:
    """Update last_inventory_validation block without reformatting the registry YAML."""
    path = repo_root / PUBLIC_PILOT_REGISTRY
    text = path.read_text(encoding="utf-8")
    block = (
        "last_inventory_validation:\n"
        f"  total_staged_fits: {report.total_staged_files}\n"
        f"  claim_label: {PUBLIC_PILOT_CLAIM_LABEL}\n"
        f"  raw_fits_committed_to_git: {str(report.raw_files_committed).lower()}\n"
    )
    if "last_inventory_validation:" in text:
        import re

        text = re.sub(
            r"last_inventory_validation:\n(?:  .+\n)+",
            block,
            text,
            count=1,
        )
    else:
        text = text.rstrip() + "\n\n" + block
    path.write_text(text, encoding="utf-8")


def _folder_to_source_ids(registry: dict[str, Any]) -> dict[str, list[str]]:
    mapping: dict[str, list[str]] = {}
    for entry in registry.get("sources", []):
        if not isinstance(entry, dict):
            continue
        folder = str(entry.get("target_folder", ""))
        mapping.setdefault(folder, []).append(str(entry.get("id", "")))
    return mapping


def _infer_irac_channel(filename: str) -> str:
    lower = filename.lower()
    if any(h in lower for h in IRAC_36_HINTS):
        return "3.6um"
    if any(h in lower for h in IRAC_45_HINTS):
        return "4.5um"
    return ""


def public_pilot_fits_extension(path: Path) -> str:
    """Return normalized extension (.fits, .fits.gz, etc.) or empty if not a pilot FITS file."""
    name = path.name.lower()
    for ext in PUBLIC_PILOT_FITS_EXTENSIONS:
        if name.endswith(ext):
            return ext
    return ""


def is_public_pilot_fits_file(path: Path) -> bool:
    if not path.is_file() or path.name == ".gitkeep":
        return False
    return bool(public_pilot_fits_extension(path))


def _header_val(header: Any, key: str) -> str:
    if key not in header:
        return ""
    val = header[key]
    return str(val).strip()


def inspect_fits_file(
    path: Path,
    repo_root: Path,
    *,
    source_id: str,
    product_type: str,
    target_folder: str,
) -> FitsFileRecord:
    rel = path.relative_to(repo_root)
    size = path.stat().st_size
    ext = public_pilot_fits_extension(path)
    compressed = ext.endswith(".gz")
    original_ext = ext[:-3] if compressed else ext
    record = FitsFileRecord(
        relative_path=str(rel),
        source_id=source_id,
        product_type=product_type,
        target_folder=target_folder,
        filename=path.name,
        size_bytes=size,
        extension=ext,
        checksum_sha256=sha256_file(path),
        claim_label=PUBLIC_PILOT_CLAIM_LABEL,
        compressed=str(compressed).lower(),
        original_extension=original_ext,
        irac_channel=_infer_irac_channel(path.name),
    )
    try:
        from astropy.io import fits
        from astropy.wcs import WCS

        with fits.open(path, memmap=False) as hdul:
            hdu = hdul[0]
            header = hdu.header
            data = hdu.data
            record.naxis = str(header.get("NAXIS", ""))
            if data is not None:
                record.shape = "x".join(str(s) for s in data.shape)
            record.bunit = _header_val(header, "BUNIT")
            record.ctype1 = _header_val(header, "CTYPE1")
            record.ctype2 = _header_val(header, "CTYPE2")
            record.ctype3 = _header_val(header, "CTYPE3")
            record.cdelt1 = _header_val(header, "CDELT1")
            record.cdelt2 = _header_val(header, "CDELT2")
            record.crval1 = _header_val(header, "CRVAL1")
            record.crval2 = _header_val(header, "CRVAL2")
            record.crpix1 = _header_val(header, "CRPIX1")
            record.crpix2 = _header_val(header, "CRPIX2")
            record.bmaj_arcsec = _header_val(header, "BMAJ")
            record.bmin_arcsec = _header_val(header, "BMIN")
            record.bpa_deg = _header_val(header, "BPA")
            record.restfrq_hz = _header_val(header, "RESTFRQ")
            try:
                wcs = WCS(header)
                record.has_wcs = str(bool(wcs.has_celestial))
            except Exception as exc:
                record.has_wcs = "false"
                record.inspect_notes = f"WCS parse: {exc}"
            record.inspect_status = "INSPECTED"
            record.header_read_status = "ok"
    except ImportError:
        record.inspect_status = "NO_ASTROPY"
        record.header_read_status = "no_astropy"
        record.inspect_notes = "astropy required for FITS header inspection"
    except Exception as exc:
        record.inspect_status = "INSPECT_FAILED"
        record.header_read_status = "failed"
        record.inspect_notes = str(exc)
    return record


def _find_data_files(directory: Path) -> list[Path]:
    if not directory.is_dir():
        return []
    return sorted(p for p in directory.rglob("*") if is_public_pilot_fits_file(p))


def scan_public_pilot_files(repo_root: Path) -> list[FitsFileRecord]:
    registry = load_public_pilot_registry(repo_root)
    folder_map = _folder_to_source_ids(registry)
    records: list[FitsFileRecord] = []
    for folder_rel, source_ids in folder_map.items():
        folder = repo_root / folder_rel
        primary_id = source_ids[0] if source_ids else ""
        entry = next(
            (
                e
                for e in registry.get("sources", [])
                if isinstance(e, dict) and e.get("id") == primary_id
            ),
            {},
        )
        product_type = str(entry.get("product_type", "")) if isinstance(entry, dict) else ""
        for fits_path in _find_data_files(folder):
            records.append(
                inspect_fits_file(
                    fits_path,
                    repo_root,
                    source_id=primary_id,
                    product_type=product_type,
                    target_folder=folder_rel,
                )
            )
    return records


def scan_public_pilot_inventory(repo_root: Path) -> PublicPilotInventoryReport:
    registry = load_public_pilot_registry(repo_root)
    file_records = scan_public_pilot_files(repo_root)
    files_by_folder: dict[str, list[FitsFileRecord]] = {}
    for rec in file_records:
        files_by_folder.setdefault(rec.target_folder, []).append(rec)

    rows: list[PublicPilotInventoryRow] = []
    total_files = len(file_records)

    for entry in registry.get("sources", []):
        if not isinstance(entry, dict):
            continue
        source_id = str(entry.get("id", ""))
        rel_folder = str(entry.get("target_folder", ""))
        folder_files = files_by_folder.get(rel_folder, [])
        reg_status = str(entry.get("status", "pending_download"))

        if reg_status == "blocked":
            inv_status: InventoryStatus = "BLOCKED"
        elif not (repo_root / rel_folder).is_dir():
            inv_status = "PENDING_DOWNLOAD"
        elif not folder_files:
            inv_status = "PENDING_DOWNLOAD"
        else:
            inv_status = "STAGED"

        rows.append(
            PublicPilotInventoryRow(
                source_id=source_id,
                target_folder=rel_folder,
                product_type=str(entry.get("product_type", "")),
                status=inv_status,
                n_files=len(folder_files),
                filenames="; ".join(f.filename for f in folder_files[:5])
                + ("; ..." if len(folder_files) > 5 else ""),
                claim_label=str(entry.get("claim_label", PUBLIC_PILOT_CLAIM_LABEL)),
                registry_status=reg_status,
                notes=str(entry.get("notes", "")),
            )
        )

    return PublicPilotInventoryReport(
        rows=rows,
        file_records=file_records,
        total_staged_files=total_files,
        raw_files_committed=False,
    )


def update_registry_from_inventory(
    repo_root: Path, report: PublicPilotInventoryReport
) -> None:
    """Patch last_inventory_validation; per-source staged fields updated when FITS exist."""
    _patch_last_inventory_validation(repo_root, report)
    if report.total_staged_files == 0:
        return
    # Full per-source YAML updates when files are staged (future PRs with FITS on disk).


def write_public_pilot_inventory_csv(path: Path, report: PublicPilotInventoryReport) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = list(asdict(PublicPilotInventoryRow("", "", "", "PENDING_DOWNLOAD", 0, "", "", "")).keys())
    with path.open("w", newline="\n", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in report.rows:
            writer.writerow(asdict(row))


def write_public_pilot_file_inventory_csv(
    path: Path, report: PublicPilotInventoryReport
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not report.file_records:
        fieldnames = list(
            asdict(
                FitsFileRecord(
                    "", "", "", "", "", 0, "", "", PUBLIC_PILOT_CLAIM_LABEL
                )
            ).keys()
        )
        with path.open("w", newline="\n", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=fieldnames)
            writer.writeheader()
        return
    fieldnames = list(asdict(report.file_records[0]).keys())
    with path.open("w", newline="\n", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for rec in report.file_records:
            writer.writerow(asdict(rec))


def write_public_pilot_inventory_report_md(
    path: Path, report: PublicPilotInventoryReport, repo_root: Path
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Phase 6F public pilot inventory report",
        "",
        f"**Claim label:** `{report.claim_label}`",
        f"**Total staged FITS files:** `{report.total_staged_files}`",
        f"**Raw FITS committed to git:** `{report.raw_files_committed}`",
        "",
        "**Not Corbelli 2014 primary data.** Strict Corbelli G1/G2/G8 remain independent.",
        "",
        "## Source summary",
        "",
        "| source_id | folder | status | n_files | registry_status |",
        "|-----------|--------|--------|---------|-----------------|",
    ]
    for row in report.rows:
        lines.append(
            f"| {row.source_id} | `{row.target_folder}` | {row.status} | "
            f"{row.n_files} | {row.registry_status} |"
        )

    if report.file_records:
        lines.extend(
            [
                "",
                "## Staged file detail",
                "",
                "| file | size_B | compressed | header | WCS | BUNIT | checksum |",
                "|------|--------|------------|--------|-----|-------|----------|",
            ]
        )
        for rec in report.file_records:
            lines.append(
                f"| `{rec.filename}` | {rec.size_bytes} | {rec.compressed} | "
                f"{rec.header_read_status or '-'} | {rec.has_wcs} | "
                f"{rec.bunit or '-'} | {rec.checksum_sha256[:12]}... |"
            )
    else:
        lines.extend(
            [
                "",
                "## Staged file detail",
                "",
                "No FITS files staged locally. Follow manual download priority:",
                "",
                "1. IRAM LP006 CO(2-1) -> `data/raw/phase6f/public_pilot/co_iram_lp006/`",
                "2. Spitzer S4G/LVL IRAC 3.6 + 4.5 um -> `stellar_s4g_irac/` or `stellar_lvl_irac/`",
                "3. LGLBS HI v1.0 -> `hi_lglbs/` (CADC login)",
                "",
                "See `docs/phase6f_public_pilot_download_instructions.md`.",
            ]
        )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def collect_public_pilot_fits(repo_root: Path) -> list[Path]:
    root = repo_root / PUBLIC_PILOT_ROOT
    if not root.is_dir():
        return []
    manifest = root / "manifest"
    files: list[Path] = []
    for path in root.rglob("*"):
        if manifest in path.parents or not is_public_pilot_fits_file(path):
            continue
        files.append(path)
    return sorted(files)


def update_public_pilot_checksums(repo_root: Path) -> tuple[Path, int]:
    """Write SHA-256 for staged public pilot FITS (.fits and .fits.gz). Never modifies raw files."""
    checksum_path = repo_root / PUBLIC_PILOT_CHECKSUMS
    checksum_path.parent.mkdir(parents=True, exist_ok=True)
    root = repo_root / PUBLIC_PILOT_ROOT
    files = collect_public_pilot_fits(repo_root)
    lines: list[str] = []
    if not files:
        lines.append(
            "# No public pilot FITS staged. See docs/phase6f_public_pilot_download_instructions.md"
        )
    else:
        for path in files:
            rel = path.relative_to(root)
            lines.append(f"{sha256_file(path)}  {rel.as_posix()}")
    checksum_path.write_text("\n".join(lines) + ("\n" if lines else ""), encoding="utf-8")
    return checksum_path, len(files)


def irac_channels_present(file_records: list[FitsFileRecord]) -> tuple[bool, bool]:
    found_36 = found_45 = False
    for rec in file_records:
        if rec.irac_channel == "3.6um":
            found_36 = True
        if rec.irac_channel == "4.5um":
            found_45 = True
        if not rec.irac_channel and rec.target_folder.endswith("stellar_s4g_irac"):
            lower = rec.filename.lower()
            if any(h in lower for h in IRAC_36_HINTS):
                found_36 = True
            if any(h in lower for h in IRAC_45_HINTS):
                found_45 = True
    return found_36, found_45


def hi_files_with_metadata(file_records: list[FitsFileRecord]) -> list[FitsFileRecord]:
    hi_folders = (
        "data/raw/phase6f/public_pilot/hi_lglbs",
        "data/raw/phase6f/public_pilot/hi_koch2018",
    )
    return [
        r
        for r in file_records
        if r.target_folder in hi_folders and r.has_wcs == "true"
    ]


def co_files_with_metadata(file_records: list[FitsFileRecord]) -> list[FitsFileRecord]:
    return [
        r
        for r in file_records
        if r.target_folder == "data/raw/phase6f/public_pilot/co_iram_lp006"
        and r.inspect_status == "INSPECTED"
    ]
