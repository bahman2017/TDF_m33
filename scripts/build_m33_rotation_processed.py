#!/usr/bin/env python3
"""Build canonical processed M33 rotation CSV from D1 baryonic audit (Phase 1D-D2-B)."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from tdf_m33.data.m33_rotation_processed import write_m33_rotation_processed
from tdf_m33.data.validation import assert_valid_m33_dataframe

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_AUDIT = (
    REPO_ROOT / "outputs" / "tables" / "corbelli2014_baryonic_velocity_derivation_audit.csv"
)
DEFAULT_OUTPUT = REPO_ROOT / "data" / "processed" / "m33_rotation.csv"

# Explicitly not used as velocity sources (documented superseded / validation only)
FIG12_SPOTCHECK_SUPERSEDED = (
    REPO_ROOT
    / "data"
    / "raw"
    / "extracted"
    / "corbelli2014_fig12_baryonic_spotcheck.csv"
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Build data/processed/m33_rotation.csv from D1 audit table."
    )
    parser.add_argument("--audit", type=Path, default=DEFAULT_AUDIT)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args(argv)

    if not args.audit.is_file():
        print(f"FAIL: audit table not found: {args.audit}")
        return 1

    if args.audit.resolve() == FIG12_SPOTCHECK_SUPERSEDED.resolve():
        print("FAIL: must not use superseded Fig. 12 spot-check as build input")
        return 1

    try:
        df = write_m33_rotation_processed(args.audit, args.output)
        assert_valid_m33_dataframe(df)
    except Exception as exc:
        print(f"FAIL: {exc}")
        return 1

    first = df.iloc[0]
    last = df.iloc[-1]
    print("PASS")
    print(f"  output: {args.output.resolve()}")
    print(f"  rows: {len(df)}")
    print(
        f"  first: R={first.r_kpc}, v_obs={first.v_obs_kms}, "
        f"v_gas={first.v_gas_kms:.2f}, v_disk={first.v_disk_kms:.2f}"
    )
    print(
        f"  last: R={last.r_kpc}, v_obs={last.v_obs_kms}, "
        f"v_gas={last.v_gas_kms:.2f}, v_disk={last.v_disk_kms:.2f}"
    )
    print(f"  data_quality_flag: {first.data_quality_flag}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
