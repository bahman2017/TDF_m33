#!/usr/bin/env python3
"""Audit M33 source manifest, directories, and Phase 1C raw extraction structure."""

from __future__ import annotations

import sys
from pathlib import Path

from tdf_m33.data.manifest import (
    assert_valid_sources_manifest,
    load_sources_manifest,
    validate_sources_manifest,
)
from tdf_m33.data.source_status import build_source_status_report

REPO_ROOT = Path(__file__).resolve().parents[1]
ACTIVE_MANIFEST = REPO_ROOT / "data" / "raw" / "sources_manifest.yaml"
TEMPLATE_MANIFEST = REPO_ROOT / "data" / "raw" / "sources_manifest_template.yaml"
DOWNLOADS_DIR = REPO_ROOT / "data" / "raw" / "downloads"
EXTRACTED_DIR = REPO_ROOT / "data" / "raw" / "extracted"
TABLE1_TEMPLATE = EXTRACTED_DIR / "corbelli2014_table1_raw_template.csv"


def _resolve_manifest() -> Path:
    if ACTIVE_MANIFEST.is_file():
        return ACTIVE_MANIFEST
    return TEMPLATE_MANIFEST


def main() -> int:
    manifest_path = _resolve_manifest()
    errors: list[str] = []

    print("M33 source audit (Phase 1C)")
    print(f"  manifest: {manifest_path}")

    if not manifest_path.is_file():
        print("FAIL: no sources manifest found")
        return 1

    try:
        manifest = load_sources_manifest(manifest_path)
    except Exception as exc:
        print(f"FAIL: could not load manifest: {exc}")
        return 1

    validation_errors = validate_sources_manifest(manifest)
    if validation_errors:
        print("FAIL: manifest validation")
        for msg in validation_errors:
            print(f"  - {msg}")
        return 1

    assert_valid_sources_manifest(manifest)

    print("\nSources:")
    for entry in manifest["sources"]:
        sid = entry["source_id"]
        status = entry["acquisition_status"]
        print(f"  - {sid}: {status}")

    for label, path in (
        ("downloads_dir", DOWNLOADS_DIR),
        ("extracted_dir", EXTRACTED_DIR),
    ):
        ok = path.is_dir()
        print(f"\n{label}: {path} ({'exists' if ok else 'MISSING'})")
        if not ok:
            errors.append(f"Missing directory: {path}")

    print(f"\ncorbelli2014_table1_raw_template: {TABLE1_TEMPLATE}")
    if TABLE1_TEMPLATE.is_file():
        print("  status: exists")
    else:
        print("  status: MISSING")
        errors.append(f"Missing raw template: {TABLE1_TEMPLATE}")

    report = build_source_status_report(
        DOWNLOADS_DIR,
        EXTRACTED_DIR,
        corbelli2014_table1_template=TABLE1_TEMPLATE,
    )
    n_dl = len(report["download_files"])
    n_ex = len(report["extracted_files"])
    print(f"\nLocal data files (excluding README): downloads={n_dl}, extracted={n_ex}")
    for item in report["download_files"]:
        print(f"  download: {item['path']} ({item['size_bytes']} bytes)")
    for item in report["extracted_files"]:
        if item["path"] != "corbelli2014_table1_raw_template.csv":
            print(f"  extracted: {item['path']} ({item['size_bytes']} bytes)")

    model_ready = REPO_ROOT / "data" / "processed" / "m33_rotation.csv"
    print(f"\nmodel-ready CSV: {model_ready}")
    if model_ready.is_file():
        print("  WARNING: m33_rotation.csv exists — should not be created prematurely in Phase 1C")
        errors.append("Model-ready m33_rotation.csv must not exist until Phase 1D")
    else:
        print("  status: not created (expected)")

    if errors:
        print("\nFAIL")
        for msg in errors:
            print(f"  - {msg}")
        return 1

    print("\nPASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
