#!/usr/bin/env python3
"""Validate Corbelli 2014 baryonic velocity derivation audit CSV."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from tdf_m33.data.corbelli2014_baryonic import validate_baryonic_audit_df

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_AUDIT = (
    REPO_ROOT / "outputs" / "tables" / "corbelli2014_baryonic_velocity_derivation_audit.csv"
)
MODEL_READY = REPO_ROOT / "data" / "processed" / "m33_rotation.csv"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Validate Corbelli 2014 baryonic derivation audit table."
    )
    parser.add_argument(
        "csv_path",
        type=Path,
        nargs="?",
        default=DEFAULT_AUDIT,
        help="Path to audit CSV",
    )
    args = parser.parse_args(argv)

    path = args.csv_path
    if not path.is_file():
        print(f"FAIL: file not found: {path}")
        return 1

    import pandas as pd

    df = pd.read_csv(path)
    errors = validate_baryonic_audit_df(df)
    if errors:
        print("FAIL")
        for msg in errors:
            print(f"  - {msg}")
        return 1

    print("PASS")
    print(f"  file: {path.resolve()}")
    print(f"  rows: {len(df)}")
    if MODEL_READY.is_file():
        print(f"  model-ready CSV present: {MODEL_READY}")
    else:
        print(f"  model-ready CSV absent: {MODEL_READY}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
