#!/usr/bin/env python3
"""Phase 6F: audit public M33 data alternatives (Tier A/B/C registry)."""

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

from tdf_m33.maps.public_data_audit import (
    load_public_candidate_registry,
    run_public_data_audit,
    write_public_candidates_csv,
    write_public_data_audit_report_md,
)

DEFAULT_CSV = REPO_ROOT / "outputs/tables/phase6f/phase6f_public_data_candidates.csv"
DEFAULT_REPORT = REPO_ROOT / "outputs/reports/phase6f/phase6f_public_data_audit_report.md"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Audit public M33 data candidates for Phase 6F (no downloads)."
    )
    parser.add_argument("--repo-root", type=Path, default=REPO_ROOT)
    parser.add_argument("--csv", type=Path, default=DEFAULT_CSV)
    parser.add_argument("--report-md", type=Path, default=DEFAULT_REPORT)
    args = parser.parse_args(argv)

    registry = load_public_candidate_registry(args.repo_root)
    report = run_public_data_audit(args.repo_root)
    write_public_candidates_csv(args.csv, report)
    write_public_data_audit_report_md(args.report_md, report, registry)

    print(f"Candidates: {len(report.candidates)} "
          f"(A={report.tier_a_count}, B={report.tier_b_count}, C={report.tier_c_count})")
    print(f"Corbelli primary FITS publicly found: {report.corbelli_primary_fits_found}")
    print(f"Wrote: {args.csv}")
    print(f"Wrote: {args.report_md}")
    print(
        "Tier B recommended pilot: LGLBS HI v1.0 + Spitzer S4G IRAC + IRAM LP006 CO. "
        "Does not satisfy G1/G2 Corbelli gates."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
