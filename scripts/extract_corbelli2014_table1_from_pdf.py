#!/usr/bin/env python3
"""Extract Corbelli et al. 2014 Table 1 from the official PDF into raw/interim CSV."""

from __future__ import annotations

import argparse
import csv
import re
import sys
from pathlib import Path

try:
    import fitz  # PyMuPDF
except ImportError as exc:
    raise SystemExit("PyMuPDF required: pip install pymupdf") from exc

from tdf_m33.data.corbelli2014_table1_raw import (
    RAW_TABLE1_COLUMNS,
    assert_valid_corbelli2014_table1_raw,
    load_corbelli2014_table1_raw,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PDF = REPO_ROOT / "data" / "raw" / "downloads" / "corbelli2014_aa24033_14.pdf"
DEFAULT_OUTPUT = REPO_ROOT / "data" / "raw" / "extracted" / "corbelli2014_table1_raw.csv"

RAW_NOTES = (
    "Raw Table 1 transcription; surface densities only; not model-ready baryonic velocities"
)
REFERENCE = "Corbelli et al. 2014, A&A 572, A23, Table 1"
EXTRACTION_METHOD = "manual_from_pdf_table1"
TABLE1_PDF_PAGE_INDEX = 12  # page 13 of 18 (0-based)


def parse_table1_from_pdf(pdf_path: Path) -> list[tuple[float, float, float, float, float]]:
    """Parse 58 five-column rows from PDF Table 1."""
    doc = fitz.open(pdf_path)
    if doc.page_count <= TABLE1_PDF_PAGE_INDEX:
        doc.close()
        raise ValueError(f"PDF has fewer than {TABLE1_PDF_PAGE_INDEX + 1} pages")
    lines = [line.strip() for line in doc[TABLE1_PDF_PAGE_INDEX].get_text().splitlines()]
    doc.close()

    if "0.24" not in lines:
        raise ValueError("Table 1 start marker 0.24 not found on expected PDF page")
    start = lines.index("0.24")
    vals: list[str] = []
    for line in lines[start:]:
        if line.startswith("Donato"):
            break
        if re.fullmatch(r"[\d.]+", line):
            vals.append(line)

    if len(vals) != 58 * 5:
        raise ValueError(f"expected 290 numeric tokens, got {len(vals)}")

    rows: list[tuple[float, float, float, float, float]] = []
    for i in range(58):
        r, vr, sv, shi, sstar = vals[i * 5 : (i + 1) * 5]
        rows.append((float(r), float(vr), float(sv), float(shi), float(sstar)))
    return rows


def write_raw_csv(path: Path, rows: list[tuple[float, float, float, float, float]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=RAW_TABLE1_COLUMNS)
        writer.writeheader()
        for i, (r, vr, sv, shi, sstar) in enumerate(rows, start=1):
            writer.writerow(
                {
                    "source_id": "corbelli_et_al_2014",
                    "raw_table_id": "corbelli2014_table1",
                    "row_id": i,
                    "r_kpc": r,
                    "v_rot_kms": vr,
                    "v_err_kms": sv,
                    "sigma_hi": shi,
                    "sigma_h2": "",
                    "sigma_gas": "",
                    "sigma_star": sstar,
                    "raw_notes": RAW_NOTES,
                    "extraction_method": EXTRACTION_METHOD,
                    "reference": REFERENCE,
                }
            )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Extract Corbelli 2014 Table 1 to raw CSV.")
    parser.add_argument("--pdf", type=Path, default=DEFAULT_PDF, help="Official A&A PDF path")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT, help="Output CSV path")
    parser.add_argument("--force", action="store_true", help="Overwrite existing output")
    args = parser.parse_args(argv)

    if not args.pdf.is_file():
        print(f"FAIL: PDF not found: {args.pdf}")
        return 1
    if args.output.exists() and not args.force:
        print(f"Output exists (use --force): {args.output}")
        return 0

    rows = parse_table1_from_pdf(args.pdf)
    write_raw_csv(args.output, rows)
    df = load_corbelli2014_table1_raw(args.output)
    assert_valid_corbelli2014_table1_raw(df)
    print(f"PASS: wrote {len(df)} rows to {args.output.resolve()}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
