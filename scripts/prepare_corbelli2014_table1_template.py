#!/usr/bin/env python3
"""Create header-only raw Table 1 extraction template for Corbelli et al. 2014."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = (
    REPO_ROOT / "data" / "raw" / "extracted" / "corbelli2014_table1_raw_template.csv"
)

# Raw/interim columns — not the model-ready processed schema
RAW_TABLE1_COLUMNS = [
    "source_id",
    "raw_table_id",
    "row_id",
    "r_kpc",
    "v_rot_kms",
    "v_err_kms",
    "sigma_hi",
    "sigma_h2",
    "sigma_gas",
    "sigma_star",
    "raw_notes",
    "extraction_method",
    "reference",
]


def write_template(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    header = ",".join(RAW_TABLE1_COLUMNS)
    path.write_text(header + "\n", encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Create Corbelli et al. 2014 Table 1 raw CSV template (headers only)."
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT,
        help="Output CSV path",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite existing template",
    )
    args = parser.parse_args(argv)

    out = args.output
    if out.exists() and not args.force:
        print(f"Template already exists (use --force to overwrite): {out}")
        return 0

    write_template(out)
    print(out.resolve())
    return 0


if __name__ == "__main__":
    sys.exit(main())
