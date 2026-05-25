#!/usr/bin/env python3
"""Phase 6B: audit manuscript skeleton files and claim-safe language."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from tdf_m33.reporting.phase6b_manuscript_audit import (
    ALLOWED_MD,
    FIGURES_MD,
    MANUSCRIPT_TEX,
    OUTLINE_MD,
    PAPER_README,
    run_phase6b_manuscript_audit,
)

REPO_ROOT = Path(__file__).resolve().parents[1]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Phase 6B manuscript skeleton audit.")
    parser.add_argument("--repo", type=Path, default=REPO_ROOT)
    args = parser.parse_args(argv)

    errors = run_phase6b_manuscript_audit(args.repo)
    if errors:
        print("FAIL — Phase 6B manuscript audit")
        for err in errors:
            print(f"  - {err}")
        return 1

    print("PASS — Phase 6B manuscript audit")
    print(f"  manuscript: {(args.repo / MANUSCRIPT_TEX).resolve()}")
    print(f"  paper readme: {(args.repo / PAPER_README).resolve()}")
    print(f"  outline: {(args.repo / OUTLINE_MD).resolve()}")
    print(f"  figures/tables map: {(args.repo / FIGURES_MD).resolve()}")
    print(f"  allowed language: {(args.repo / ALLOWED_MD).resolve()}")
    print()
    print("  prohibited affirmative claims: absent")
    print("  required caveats: present in manuscript")
    print("  required pipeline outputs: referenced in docs")
    return 0


if __name__ == "__main__":
    sys.exit(main())
