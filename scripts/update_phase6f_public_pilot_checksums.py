#!/usr/bin/env python3
"""Phase 6F: SHA-256 checksums for staged public pilot FITS (read-only on raw files)."""

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

from tdf_m33.maps.public_pilot_inventory import update_public_pilot_checksums


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Update checksums for public pilot FITS files."
    )
    parser.add_argument("--repo-root", type=Path, default=REPO_ROOT)
    args = parser.parse_args(argv)

    checksum_path, n_files = update_public_pilot_checksums(args.repo_root)
    print(f"Wrote: {checksum_path}")
    print(f"Checksummed FITS files: {n_files}")
    if n_files == 0:
        print("No staged FITS; checksum file documents empty state.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
