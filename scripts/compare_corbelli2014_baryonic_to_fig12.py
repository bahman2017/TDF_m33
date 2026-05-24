#!/usr/bin/env python3
"""Compare D1 baryonic velocities to Corbelli 2014 Fig. 12 spot-check (Phase 1D-D2-A)."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import pandas as pd

from tdf_m33.data.corbelli2014_fig12 import (
    compare_baryonic_to_fig12,
    load_fig12_spotcheck,
    plot_fig12_sanity_check,
    validate_comparison_df,
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
DEFAULT_SPOTCHECK_CORRECTED = (
    REPO_ROOT
    / "data"
    / "raw"
    / "extracted"
    / "corbelli2014_fig12_baryonic_spotcheck_corrected.csv"
)
DEFAULT_COMPARISON = (
    REPO_ROOT / "outputs" / "tables" / "corbelli2014_baryonic_fig12_comparison.csv"
)
DEFAULT_COMPARISON_CORRECTED = (
    REPO_ROOT
    / "outputs"
    / "tables"
    / "corbelli2014_baryonic_fig12_comparison_corrected.csv"
)
DEFAULT_FIGURE = (
    REPO_ROOT / "outputs" / "figures" / "corbelli2014_baryonic_fig12_sanity_check.png"
)
DEFAULT_FIGURE_CORRECTED = (
    REPO_ROOT
    / "outputs"
    / "figures"
    / "corbelli2014_baryonic_fig12_sanity_check_corrected.png"
)
MODEL_READY = REPO_ROOT / "data" / "processed" / "m33_rotation.csv"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Sanity-check D1 baryonic velocities against Fig. 12 digitization."
    )
    parser.add_argument("--audit", type=Path, default=DEFAULT_AUDIT)
    parser.add_argument("--spotcheck", type=Path, default=None)
    parser.add_argument("--output", type=Path, default=None)
    parser.add_argument("--figure", type=Path, default=None)
    parser.add_argument(
        "--corrected",
        action="store_true",
        help="Use label-corrected spot-check CSV and corrected output paths",
    )
    args = parser.parse_args(argv)

    if args.corrected:
        args.spotcheck = args.spotcheck or DEFAULT_SPOTCHECK_CORRECTED
        args.output = args.output or DEFAULT_COMPARISON_CORRECTED
        args.figure = args.figure or DEFAULT_FIGURE_CORRECTED
    else:
        args.spotcheck = args.spotcheck or DEFAULT_SPOTCHECK
        args.output = args.output or DEFAULT_COMPARISON
        args.figure = args.figure or DEFAULT_FIGURE

    for label, path in (("audit", args.audit), ("spotcheck", args.spotcheck)):
        if not path.is_file():
            print(f"FAIL: {label} not found: {path}")
            return 1

    audit = pd.read_csv(args.audit)
    spotcheck = load_fig12_spotcheck(args.spotcheck)
    comparison, status, notes = compare_baryonic_to_fig12(audit, spotcheck)

    errors = validate_comparison_df(comparison)
    if errors:
        print("FAIL: comparison table invalid")
        for msg in errors:
            print(f"  - {msg}")
        return 1

    args.output.parent.mkdir(parents=True, exist_ok=True)
    comparison.to_csv(args.output, index=False)
    plot_fig12_sanity_check(audit, spotcheck, comparison, args.figure)

    print(status)
    print(f"  notes: {notes}")
    print(f"  comparison: {args.output.resolve()}")
    print(f"  figure: {args.figure.resolve()}")
    print(f"  model-ready CSV: {'present' if MODEL_READY.is_file() else 'absent'}")
    print()
    print("Residual summary (derived - digitized) [km/s]:")
    for _, row in comparison.iterrows():
        print(
            f"  R={row.r_kpc:.0f} kpc: "
            f"Δv_gas={row.residual_gas_kms:+.1f}, "
            f"Δv_disk={row.residual_disk_kms:+.1f}"
        )

    if status in ("PASS", "PASS_WITH_CAVEAT"):
        return 0
    return 2


if __name__ == "__main__":
    sys.exit(main())
