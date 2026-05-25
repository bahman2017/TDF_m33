#!/usr/bin/env python3
"""Phase 6D: bibliography verification, LaTeX compile, manuscript polish audit."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from tdf_m33.reporting.phase6d_manuscript_polish_audit import (
    BIB_VERIFICATION_MD,
    MANUSCRIPT_TEX,
    POLISH_REPORT_MD,
    run_phase6d_manuscript_polish_audit,
)

REPO_ROOT = Path(__file__).resolve().parents[1]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Phase 6D manuscript polish audit.")
    parser.add_argument("--repo", type=Path, default=REPO_ROOT)
    args = parser.parse_args(argv)

    errors, compile_info = run_phase6d_manuscript_polish_audit(args.repo)
    if errors:
        print("FAIL — Phase 6D manuscript polish audit")
        for err in errors:
            print(f"  - {err}")
        print(f"  report: {(args.repo / POLISH_REPORT_MD).resolve()}")
        return 1

    print("PASS — Phase 6D manuscript polish audit")
    print(f"  manuscript: {(args.repo / MANUSCRIPT_TEX).resolve()}")
    print(f"  bibliography: {(args.repo / BIB_VERIFICATION_MD).resolve()}")
    print(f"  report: {(args.repo / POLISH_REPORT_MD).resolve()}")
    print()
    print(f"  latex_compile: {compile_info.get('status')}")
    print(f"  {compile_info.get('detail', '')}")
    if compile_info.get("pdf"):
        print(f"  pdf: {compile_info['pdf']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
