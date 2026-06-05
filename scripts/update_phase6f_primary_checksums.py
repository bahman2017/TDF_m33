#!/usr/bin/env python3
"""Phase 6F: update SHA-256 checksums for primary Corbelli FITS files."""

from __future__ import annotations

import argparse
import importlib.util
import sys
from pathlib import Path

_bootstrap_path = Path(__file__).resolve().parent / "_bootstrap.py"
_bootstrap_spec = importlib.util.spec_from_file_location("_bootstrap", _bootstrap_path)
if _bootstrap_spec is None or _bootstrap_spec.loader is None:
    raise ImportError(f"Cannot load bootstrap from {_bootstrap_path}")
_bootstrap = importlib.util.module_from_spec(_bootstrap_spec)
_bootstrap_spec.loader.exec_module(_bootstrap)
REPO_ROOT = _bootstrap.REPO_ROOT

from tdf_m33.maps.primary_data import update_primary_checksums


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Compute SHA-256 checksums for Phase 6F primary FITS files."
    )
    parser.add_argument("--repo-root", type=Path, default=REPO_ROOT)
    args = parser.parse_args(argv)

    checksum_path, n_files = update_primary_checksums(args.repo_root)
    print(f"Wrote checksums: {checksum_path}")
    print(f"Primary FITS files checksummed: {n_files}")
    if n_files == 0:
        print("No primary FITS present; checksum file documents empty state.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
