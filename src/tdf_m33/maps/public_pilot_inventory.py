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

FITS_SUFFIXES = {".fits", ".fit", ".fts"}

InventoryStatus = Literal["PENDING_DOWNLOAD", "STAGED", "EMPTY_FOLDER", "BLOCKED"]


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
class PublicPilotInventoryReport:
    rows: list[PublicPilotInventoryRow] = field(default_factory=list)
    total_staged_files: int = 0
    claim_label: str = PUBLIC_PILOT_CLAIM_LABEL


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


def _find_data_files(directory: Path) -> list[Path]:
    if not directory.is_dir():
        return []
    return sorted(
        p
        for p in directory.rglob("*")
        if p.is_file()
        and p.suffix.lower() in FITS_SUFFIXES
        and p.name != ".gitkeep"
    )


def scan_public_pilot_inventory(repo_root: Path) -> PublicPilotInventoryReport:
    registry = load_public_pilot_registry(repo_root)
    rows: list[PublicPilotInventoryRow] = []
    total_files = 0

    for entry in registry.get("sources", []):
        if not isinstance(entry, dict):
            continue
        source_id = str(entry.get("id", ""))
        rel_folder = str(entry.get("target_folder", ""))
        folder = repo_root / rel_folder
        files = _find_data_files(folder)
        reg_status = str(entry.get("status", "pending_download"))

        if reg_status == "blocked":
            inv_status: InventoryStatus = "BLOCKED"
        elif not folder.is_dir():
            inv_status = "PENDING_DOWNLOAD"
        elif not files:
            inv_status = "PENDING_DOWNLOAD" if reg_status == "pending_download" else "EMPTY_FOLDER"
        else:
            inv_status = "STAGED"
            total_files += len(files)

        rows.append(
            PublicPilotInventoryRow(
                source_id=source_id,
                target_folder=rel_folder,
                product_type=str(entry.get("product_type", "")),
                status=inv_status,
                n_files=len(files),
                filenames="; ".join(f.name for f in files[:5])
                + ("; ..." if len(files) > 5 else ""),
                claim_label=str(entry.get("claim_label", PUBLIC_PILOT_CLAIM_LABEL)),
                registry_status=reg_status,
                notes=str(entry.get("notes", "")),
            )
        )

    return PublicPilotInventoryReport(
        rows=rows,
        total_staged_files=total_files,
    )


def write_public_pilot_inventory_csv(path: Path, report: PublicPilotInventoryReport) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = list(asdict(PublicPilotInventoryRow("", "", "", "PENDING_DOWNLOAD", 0, "", "", "")).keys())
    with path.open("w", newline="\n", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in report.rows:
            writer.writerow(asdict(row))


def write_public_pilot_inventory_report_md(
    path: Path, report: PublicPilotInventoryReport
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Phase 6F public pilot inventory report",
        "",
        f"**Claim label:** `{report.claim_label}`",
        f"**Total staged FITS files:** `{report.total_staged_files}`",
        "",
        "**Not Corbelli 2014 primary data.** Strict Corbelli G1/G2/G8 remain independent.",
        "",
        "| source_id | folder | status | n_files | registry_status |",
        "|-----------|--------|--------|---------|-----------------|",
    ]
    for row in report.rows:
        lines.append(
            f"| {row.source_id} | `{row.target_folder}` | {row.status} | "
            f"{row.n_files} | {row.registry_status} |"
        )
    if report.total_staged_files == 0:
        lines.extend(
            [
                "",
                "All sources **pending_download**. Follow "
                "`docs/phase6f_public_pilot_download_instructions.md`.",
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
        if not path.is_file() or path.suffix.lower() not in FITS_SUFFIXES:
            continue
        if manifest in path.parents:
            continue
        files.append(path)
    return sorted(files)


def update_public_pilot_checksums(repo_root: Path) -> tuple[Path, int]:
    """Write SHA-256 for staged public pilot FITS. Never modifies raw files."""
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
