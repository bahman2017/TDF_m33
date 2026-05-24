#!/usr/bin/env python3
"""Validate a processed M33 CSV against the canonical schema."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from tdf_m33.data.io import load_m33_processed_csv
from tdf_m33.data.validation import validate_m33_dataframe


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Validate processed M33 radial data CSV (canonical schema)."
    )
    parser.add_argument(
        "csv_path",
        type=Path,
        help="Path to processed M33 CSV (e.g. data/processed/m33_rotation.csv)",
    )
    args = parser.parse_args(argv)

    path = args.csv_path
    if not path.is_file():
        print(f"FAIL: file not found: {path}")
        return 1

    try:
        df = load_m33_processed_csv(path)
    except Exception as exc:
        print(f"FAIL: could not load CSV: {exc}")
        return 1

    errors = validate_m33_dataframe(df)
    if errors:
        print("FAIL")
        for msg in errors:
            print(f"  - {msg}")
        return 1

    n_rows = len(df)
    print("PASS")
    print(f"  file: {path.resolve()}")
    print(f"  rows: {n_rows} (structural validation only when empty)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
