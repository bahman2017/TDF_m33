#!/usr/bin/env python3
"""Phase 6E: journal-neutral submission package audit."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from tdf_m33.reporting.phase6e_submission_package_audit import (
    BIB_VERIFICATION_MD,
    MANUSCRIPT_TEX,
    SUBMISSION_CHECKLIST_MD,
    SUBMISSION_REPORT_MD,
    run_phase6e_submission_package_audit,
)

REPO_ROOT = Path(__file__).resolve().parents[1]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Phase 6E submission package audit.")
    parser.add_argument("--repo", type=Path, default=REPO_ROOT)
    args = parser.parse_args(argv)

    errors, meta = run_phase6e_submission_package_audit(args.repo)
    if errors:
        print("FAIL — Phase 6E submission package audit")
        for err in errors:
            print(f"  - {err}")
        print(f"  report: {(args.repo / SUBMISSION_REPORT_MD).resolve()}")
        return 1

    print("PASS — Phase 6E submission package audit")
    print(f"  manuscript: {(args.repo / MANUSCRIPT_TEX).resolve()}")
    print(f"  checklist: {(args.repo / SUBMISSION_CHECKLIST_MD).resolve()}")
    print(f"  bibliography: {(args.repo / BIB_VERIFICATION_MD).resolve()}")
    print(f"  report: {(args.repo / SUBMISSION_REPORT_MD).resolve()}")
    compile_info = meta.get("compile", {})
    if isinstance(compile_info, dict):
        print()
        print(f"  latex_compile: {compile_info.get('status')}")
        print(f"  {compile_info.get('detail', '')}")
        if compile_info.get("pdf"):
            print(f"  pdf: {compile_info['pdf']}")
    fig_status = meta.get("figure_status", {})
    if fig_status:
        print()
        print("  figure_packaging:")
        for k, v in sorted(fig_status.items()):
            print(f"    {k}: {v}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
