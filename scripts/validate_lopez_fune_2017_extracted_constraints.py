#!/usr/bin/env python3
"""Phase 5C-A: validate López Fune 2017 extracted constraint tables."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from tdf_m33.lensing.lopez_fune_2017_extraction import (
    PARAMS_CSV,
    PROFILE_CSV,
    run_phase5c_lopez_fune_extraction_audit,
    validate_extracted_constraints,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CONFIG = REPO_ROOT / "configs" / "m33_default.yaml"
STATUS_CSV = REPO_ROOT / "outputs" / "tables" / "phase5c_lopez_fune_extraction_status.csv"
REPORT_MD = REPO_ROOT / "outputs" / "reports" / "phase5c_lopez_fune_extraction_audit.md"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Validate López Fune 2017 extracted constraint CSVs."
    )
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--status", type=Path, default=STATUS_CSV)
    parser.add_argument("--report", type=Path, default=REPORT_MD)
    parser.add_argument(
        "--no-regenerate",
        action="store_true",
        help="Do not regenerate CSVs from quoted/digitized values",
    )
    args = parser.parse_args(argv)

    try:
        if args.no_regenerate:
            errors = validate_extracted_constraints(REPO_ROOT, args.config)
            if errors:
                raise ValueError("; ".join(errors))
            import pandas as pd

            profile_df = pd.read_csv(REPO_ROOT / PROFILE_CSV)
            params_df = pd.read_csv(REPO_ROOT / PARAMS_CSV)
        else:
            profile_df, params_df, _ = run_phase5c_lopez_fune_extraction_audit(
                args.config,
                args.status,
                args.report,
                regenerate=True,
            )
    except (FileNotFoundError, ValueError) as exc:
        print(f"FAIL: {exc}")
        return 1

    print("PASS — López Fune 2017 extracted constraints validation")
    print(f"  profile: {(REPO_ROOT / PROFILE_CSV).resolve()}")
    print(f"  parameters: {(REPO_ROOT / PARAMS_CSV).resolve()}")
    print(f"  status: {args.status.resolve()}")
    print(f"  report: {args.report.resolve()}")
    print()
    print(f"  profile rows: {len(profile_df)}")
    print(f"  parameter rows: {len(params_df)}")
    print(f"  fig6 digitized: {(profile_df['extraction_method'] == 'figure_digitization').sum()}")
    print(f"  model evaluated: {(profile_df['extraction_method'] == 'model_evaluated').sum()}")
    print()
    print("  observational_limits_enabled: false (required)")
    print("  tau_comparison_performed: false")
    print("  physical_arcsec_conversion: false")
    return 0


if __name__ == "__main__":
    sys.exit(main())
