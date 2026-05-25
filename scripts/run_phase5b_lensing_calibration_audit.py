#!/usr/bin/env python3
"""Phase 5B-A: audit Phase 5A deflection proxy; plan physical calibration and limits."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from tdf_m33.lensing.phase5b_calibration_audit import run_phase5b_calibration_audit

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CONFIG = REPO_ROOT / "configs" / "m33_default.yaml"
PHASE5A_METADATA = (
    REPO_ROOT / "outputs" / "tables" / "phase5a_lensing_prediction_metadata.csv"
)
STATUS_CSV = REPO_ROOT / "outputs" / "tables" / "phase5b_lensing_calibration_status.csv"
REPORT_MD = REPO_ROOT / "outputs" / "reports" / "phase5b_lensing_calibration_audit.md"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Phase 5B-A: lensing calibration and limits planning audit."
    )
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--metadata", type=Path, default=PHASE5A_METADATA)
    parser.add_argument("--status", type=Path, default=STATUS_CSV)
    parser.add_argument("--report", type=Path, default=REPORT_MD)
    args = parser.parse_args(argv)

    try:
        status_df, _ = run_phase5b_calibration_audit(
            args.config,
            args.metadata,
            args.status,
            args.report,
        )
    except (FileNotFoundError, ValueError) as exc:
        print(f"FAIL: {exc}")
        return 1

    row = status_df.iloc[0]
    print("PASS — Phase 5B-A lensing calibration / limits planning audit")
    print(f"  status table: {args.status.resolve()}")
    print(f"  report: {args.report.resolve()}")
    print()
    print(f"  phase5a_units: {row['phase5a_units']}")
    print(f"  calibration_status: {row['calibration_status']}")
    print(f"  physical_calibration_enabled: {row['physical_calibration_enabled']}")
    print(f"  observational_limits_enabled: {row['observational_limits_enabled']}")
    print(f"  separate_halo_used: {row['phase5a_separate_halo_used']}")
    print(f"  lensing_only_fit: {row['phase5a_lensing_only_fit']}")
    print()
    print(f"  {row['recommendation']}")
    print()
    print("  physical_lensing_detection_claimed: false")
    print("  observational_comparison_performed: false")
    return 0


if __name__ == "__main__":
    sys.exit(main())
