#!/usr/bin/env python3
"""Phase 5B-C: audit López Fune et al. 2017 PDF acquisition and extraction plan."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from tdf_m33.lensing.phase5bc_lopez_fune_source_audit import (
    run_phase5bc_lopez_fune_source_audit,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CONFIG = REPO_ROOT / "configs" / "m33_default.yaml"
STATUS_CSV = REPO_ROOT / "outputs" / "tables" / "phase5b_lopez_fune_source_status.csv"
REPORT_MD = REPO_ROOT / "outputs" / "reports" / "phase5b_lopez_fune_source_audit.md"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Phase 5B-C: López Fune 2017 source audit.")
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--status", type=Path, default=STATUS_CSV)
    parser.add_argument("--report", type=Path, default=REPORT_MD)
    args = parser.parse_args(argv)

    try:
        status_df = run_phase5bc_lopez_fune_source_audit(
            args.config, args.status, args.report
        )
    except (FileNotFoundError, ValueError) as exc:
        print(f"FAIL: {exc}")
        return 1

    row = status_df.iloc[0]
    print("PASS — Phase 5B-C López Fune et al. 2017 source acquisition audit")
    print(f"  PDF: {row['pdf_path']}")
    print(f"  SHA-256: {row['sha256']}")
    print(f"  extraction plan: {row['extraction_plan_path']}")
    print(f"  status table: {args.status.resolve()}")
    print(f"  report: {args.report.resolve()}")
    print()
    print(f"  acquisition_status: {row['acquisition_status']}")
    print(f"  observational_limits_enabled: {row['observational_limits_enabled']}")
    print(f"  numerical_comparison_performed: {row['numerical_comparison_performed']}")
    print()
    print(f"  {row['recommendation']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
