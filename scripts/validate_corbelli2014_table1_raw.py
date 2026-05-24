#!/usr/bin/env python3
"""Validate Corbelli et al. 2014 Table 1 raw/interim CSV."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from tdf_m33.data.corbelli2014_table1_raw import (
    load_corbelli2014_table1_raw,
    validate_corbelli2014_table1_raw,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CSV = REPO_ROOT / "data" / "raw" / "extracted" / "corbelli2014_table1_raw.csv"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Validate Corbelli 2014 Table 1 raw CSV (Phase 1D-C)."
    )
    parser.add_argument(
        "csv_path",
        type=Path,
        nargs="?",
        default=DEFAULT_CSV,
        help="Path to corbelli2014_table1_raw.csv",
    )
    args = parser.parse_args(argv)

    path = args.csv_path
    if not path.is_file():
        print(f"FAIL: file not found: {path}")
        return 1

    try:
        df = load_corbelli2014_table1_raw(path)
    except Exception as exc:
        print(f"FAIL: could not load CSV: {exc}")
        return 1

    errors = validate_corbelli2014_table1_raw(df)
    if errors:
        print("FAIL")
        for msg in errors:
            print(f"  - {msg}")
        return 1

    print("PASS")
    print(f"  file: {path.resolve()}")
    print(f"  rows: {len(df)}")
    first = df.iloc[0]
    last = df.iloc[-1]
    print(
        f"  first: R={first['r_kpc']}, Vr={first['v_rot_kms']}, "
        f"sigma_V={first['v_err_kms']}, Sigma_HI={first['sigma_hi']}, "
        f"Sigma_star={first['sigma_star']}"
    )
    print(
        f"  last: R={last['r_kpc']}, Vr={last['v_rot_kms']}, "
        f"sigma_V={last['v_err_kms']}, Sigma_HI={last['sigma_hi']}, "
        f"Sigma_star={last['sigma_star']}"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
