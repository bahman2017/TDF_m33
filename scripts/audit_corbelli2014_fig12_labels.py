#!/usr/bin/env python3
"""Audit Corbelli 2014 Fig. 12 gas/stellar label assignment (Phase 1D-D2-A2)."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import pandas as pd

from tdf_m33.data.corbelli2014_fig12 import load_fig12_spotcheck
from tdf_m33.data.corbelli2014_fig12_label_audit import (
    build_corrected_spotcheck,
    build_label_audit_table,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_AUDIT = (
    REPO_ROOT / "outputs" / "tables" / "corbelli2014_baryonic_velocity_derivation_audit.csv"
)
DEFAULT_SPOTCHECK = (
    REPO_ROOT
    / "data"
    / "raw"
    / "extracted"
    / "corbelli2014_fig12_baryonic_spotcheck.csv"
)
DEFAULT_LABEL_AUDIT = (
    REPO_ROOT / "outputs" / "tables" / "corbelli2014_fig12_label_audit.csv"
)
DEFAULT_CORRECTED = (
    REPO_ROOT
    / "data"
    / "raw"
    / "extracted"
    / "corbelli2014_fig12_baryonic_spotcheck_corrected.csv"
)
MODEL_READY = REPO_ROOT / "data" / "processed" / "m33_rotation.csv"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Audit Fig. 12 gas/stellar label assignment.")
    parser.add_argument("--audit", type=Path, default=DEFAULT_AUDIT)
    parser.add_argument("--spotcheck", type=Path, default=DEFAULT_SPOTCHECK)
    parser.add_argument("--output", type=Path, default=DEFAULT_LABEL_AUDIT)
    parser.add_argument(
        "--write-corrected",
        type=Path,
        default=DEFAULT_CORRECTED,
        help="Write corrected spot-check CSV (does not overwrite original)",
    )
    args = parser.parse_args(argv)

    for label, path in (("audit", args.audit), ("spotcheck", args.spotcheck)):
        if not path.is_file():
            print(f"FAIL: {label} not found: {path}")
            return 1

    audit = pd.read_csv(args.audit)
    spotcheck = load_fig12_spotcheck(args.spotcheck)
    label_df, verdict, rec = build_label_audit_table(spotcheck, audit)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    label_df.to_csv(args.output, index=False)

    corrected = build_corrected_spotcheck(spotcheck)
    args.write_corrected.parent.mkdir(parents=True, exist_ok=True)
    corrected.to_csv(args.write_corrected, index=False)

    print(verdict)
    print(f"  recommendation: {rec}")
    print(f"  label audit: {args.output.resolve()}")
    print(f"  corrected spot-check: {args.write_corrected.resolve()}")
    print(f"  model-ready CSV: {'present' if MODEL_READY.is_file() else 'absent'}")
    print()
    print("Residual sum |Δv_gas|+|Δv_disk| (km/s):")
    for _, row in label_df.iterrows():
        print(
            f"  R={row.r_kpc:.0f}: old={row.old_abs_residual_sum:.1f} "
            f"swapped={row.swapped_abs_residual_sum:.1f}"
        )

    return 0


if __name__ == "__main__":
    sys.exit(main())
