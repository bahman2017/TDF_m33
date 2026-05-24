#!/usr/bin/env python3
"""Validate an M33 sources manifest YAML file."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from tdf_m33.data.manifest import load_sources_manifest, validate_sources_manifest


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Validate M33 literature source manifest (provenance registry)."
    )
    parser.add_argument(
        "manifest_path",
        type=Path,
        help="Path to sources manifest YAML (e.g. data/raw/sources_manifest_template.yaml)",
    )
    args = parser.parse_args(argv)

    path = args.manifest_path
    if not path.is_file():
        print(f"FAIL: file not found: {path}")
        return 1

    try:
        manifest = load_sources_manifest(path)
    except Exception as exc:
        print(f"FAIL: could not load manifest: {exc}")
        return 1

    errors = validate_sources_manifest(manifest)
    if errors:
        print("FAIL")
        for msg in errors:
            print(f"  - {msg}")
        return 1

    n_sources = len(manifest.get("sources", []))
    print("PASS")
    print(f"  file: {path.resolve()}")
    print(f"  sources: {n_sources}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
