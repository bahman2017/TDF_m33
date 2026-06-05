#!/usr/bin/env python3
"""Phase 6F: validate primary Corbelli 2014 map inventory and FITS metadata."""

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

from tdf_m33.maps.primary_data import (
    scan_primary_data,
    write_primary_inventory_csv,
    write_primary_validation_report_md,
)

DEFAULT_INVENTORY = REPO_ROOT / "outputs/tables/phase6f/phase6f_primary_data_inventory.csv"
DEFAULT_REPORT = REPO_ROOT / "outputs/reports/phase6f/phase6f_primary_data_validation_report.md"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Validate Phase 6F primary Corbelli map inventory."
    )
    parser.add_argument("--repo-root", type=Path, default=REPO_ROOT)
    parser.add_argument("--inventory-csv", type=Path, default=DEFAULT_INVENTORY)
    parser.add_argument("--report-md", type=Path, default=DEFAULT_REPORT)
    args = parser.parse_args(argv)

    try:
        report = scan_primary_data(args.repo_root, require_astropy=True)
    except ImportError as exc:
        print(str(exc), file=sys.stderr)
        return 1

    write_primary_inventory_csv(args.inventory_csv, report)
    write_primary_validation_report_md(args.report_md, report, args.repo_root)

    print(f"Primary FITS files found: {report.n_fits_files}")
    print(f"Wrote inventory: {args.inventory_csv}")
    print(f"Wrote report: {args.report_md}")
    if report.n_fits_files == 0:
        print(
            "Primary Corbelli maps missing or incomplete. "
            "G1/G2 remain FAIL; scientific tau-map blocked."
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
