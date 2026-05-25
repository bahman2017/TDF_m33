#!/usr/bin/env python3
"""Phase 5B-B: register candidate M33 constraint sources (review only)."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from tdf_m33.lensing.phase5b_constraint_source_audit import (
    run_phase5b_constraint_source_audit,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CONFIG = REPO_ROOT / "configs" / "m33_default.yaml"
STATUS_CSV = REPO_ROOT / "outputs" / "tables" / "phase5b_constraint_source_status.csv"
REPORT_MD = REPO_ROOT / "outputs" / "reports" / "phase5b_constraint_source_audit.md"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Phase 5B-B: M33 constraint source review audit."
    )
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--status", type=Path, default=STATUS_CSV)
    parser.add_argument("--report", type=Path, default=REPORT_MD)
    args = parser.parse_args(argv)

    try:
        status_df = run_phase5b_constraint_source_audit(
            args.config, args.status, args.report
        )
    except (FileNotFoundError, ValueError) as exc:
        print(f"FAIL: {exc}")
        return 1

    row = status_df.iloc[0]
    print("PASS — Phase 5B-B constraint source review audit")
    print(f"  status table: {args.status.resolve()}")
    print(f"  report: {args.report.resolve()}")
    print()
    print(f"  limits_status: {row['limits_status']}")
    print(f"  selected_source_id: {row['selected_source_id']}")
    print(f"  candidate_source_ids: {row['candidate_source_ids']}")
    print(f"  observational_limits_enabled: {row['observational_limits_enabled']}")
    print(f"  output_units: {row['output_units']}")
    print()
    print(f"  {row['recommendation']}")
    print()
    print("  observational_comparison_performed: false")
    print("  physical_lensing_detection_claimed: false")
    return 0


if __name__ == "__main__":
    sys.exit(main())
