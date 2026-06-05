#!/usr/bin/env python3
"""Phase 6F: inventory staged Tier B public pilot data."""

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

from tdf_m33.maps.public_pilot_inventory import (
    PUBLIC_PILOT_CLAIM_LABEL,
    scan_public_pilot_inventory,
    write_public_pilot_inventory_csv,
    write_public_pilot_inventory_report_md,
)

DEFAULT_CSV = REPO_ROOT / "outputs/tables/phase6f/phase6f_public_pilot_inventory.csv"
DEFAULT_REPORT = REPO_ROOT / "outputs/reports/phase6f/phase6f_public_pilot_inventory_report.md"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Inventory Phase 6F public pilot staging.")
    parser.add_argument("--repo-root", type=Path, default=REPO_ROOT)
    parser.add_argument("--csv", type=Path, default=DEFAULT_CSV)
    parser.add_argument("--report-md", type=Path, default=DEFAULT_REPORT)
    args = parser.parse_args(argv)

    report = scan_public_pilot_inventory(args.repo_root)
    write_public_pilot_inventory_csv(args.csv, report)
    write_public_pilot_inventory_report_md(args.report_md, report)

    print(f"Claim label: {PUBLIC_PILOT_CLAIM_LABEL}")
    print(f"Staged FITS files: {report.total_staged_files}")
    print(f"Wrote: {args.csv}")
    print(f"Wrote: {args.report_md}")
    if report.total_staged_files == 0:
        print("All sources pending_download - see docs/phase6f_public_pilot_download_instructions.md")
    return 0


if __name__ == "__main__":
    sys.exit(main())
