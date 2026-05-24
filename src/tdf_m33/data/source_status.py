"""Filesystem utilities for M33 raw source acquisition audit (Phase 1C)."""

from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any


def sha256_file(path: str | Path) -> str:
    """Return the SHA-256 hex digest of a file."""
    path = Path(path)
    digest = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def file_exists(path: str | Path) -> bool:
    """Return True if path exists and is a regular file."""
    return Path(path).is_file()


def summarize_source_files(
    download_dir: str | Path,
    extracted_dir: str | Path,
) -> dict[str, Any]:
    """Summarize regular files under download and extracted directories."""
    download_dir = Path(download_dir)
    extracted_dir = Path(extracted_dir)

    def _list_files(root: Path) -> list[dict[str, Any]]:
        if not root.is_dir():
            return []
        files: list[dict[str, Any]] = []
        for path in sorted(root.rglob("*")):
            if path.is_file() and path.name != "README.md":
                files.append(
                    {
                        "path": str(path.relative_to(root)),
                        "size_bytes": path.stat().st_size,
                    }
                )
        return files

    return {
        "download_dir": str(download_dir),
        "download_dir_exists": download_dir.is_dir(),
        "download_files": _list_files(download_dir),
        "extracted_dir": str(extracted_dir),
        "extracted_dir_exists": extracted_dir.is_dir(),
        "extracted_files": _list_files(extracted_dir),
    }


def build_source_status_report(
    download_dir: str | Path,
    extracted_dir: str | Path,
    *,
    corbelli2014_table1_template: str | Path | None = None,
) -> dict[str, Any]:
    """Build a combined status report for source audit tooling."""
    report = summarize_source_files(download_dir, extracted_dir)
    if corbelli2014_table1_template is not None:
        template = Path(corbelli2014_table1_template)
        report["corbelli2014_table1_template"] = str(template)
        report["corbelli2014_table1_template_exists"] = template.is_file()
    return report
