#!/usr/bin/env python3
"""Derive interim Corbelli 2014 baryonic velocities (Phase 1D-D1 audit table)."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from tdf_m33.data.corbelli2014_baryonic import (
    build_baryonic_audit_table,
    load_table1_raw,
    validate_baryonic_audit_df,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_RAW = REPO_ROOT / "data" / "raw" / "extracted" / "corbelli2014_table1_raw.csv"
DEFAULT_OUTPUT = (
    REPO_ROOT / "outputs" / "tables" / "corbelli2014_baryonic_velocity_derivation_audit.csv"
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Derive Corbelli 2014 baryonic velocities to interim audit CSV."
    )
    parser.add_argument("--raw", type=Path, default=DEFAULT_RAW, help="Table 1 raw CSV")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT, help="Audit CSV path")
    parser.add_argument(
        "--coarse-grid",
        action="store_true",
        help="Use coarser quadrature (faster, for smoke tests only)",
    )
    args = parser.parse_args(argv)

    if not args.raw.is_file():
        print(f"FAIL: raw Table 1 not found: {args.raw}")
        return 1

    raw_df = load_table1_raw(args.raw)
    audit_df = build_baryonic_audit_table(raw_df, coarse_grid=args.coarse_grid)

    errors = validate_baryonic_audit_df(audit_df)
    if errors:
        print("FAIL: audit validation")
        for msg in errors:
            print(f"  - {msg}")
        return 1

    args.output.parent.mkdir(parents=True, exist_ok=True)
    audit_df.to_csv(args.output, index=False)

    first = audit_df.iloc[0]
    last = audit_df.iloc[-1]
    print("PASS")
    print(f"  output: {args.output.resolve()}")
    print(f"  rows: {len(audit_df)}")
    print(
        f"  first: R={first['r_kpc']}, v_gas={first['v_gas_kms']:.2f}, "
        f"v_disk={first['v_disk_kms']:.2f}, v_bar={first['v_bar_kms']:.2f}"
    )
    print(
        f"  last: R={last['r_kpc']}, v_gas={last['v_gas_kms']:.2f}, "
        f"v_disk={last['v_disk_kms']:.2f}, v_bar={last['v_bar_kms']:.2f}"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
