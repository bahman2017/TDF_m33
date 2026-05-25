#!/usr/bin/env python3
"""Phase 6C: audit expanded manuscript draft (readable first draft)."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from tdf_m33.reporting.phase6c_manuscript_draft_audit import (
    DRAFTING_NOTES_MD,
    MANUSCRIPT_TEX,
    run_phase6c_manuscript_draft_audit,
)

REPO_ROOT = Path(__file__).resolve().parents[1]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Phase 6C manuscript draft audit.")
    parser.add_argument("--repo", type=Path, default=REPO_ROOT)
    args = parser.parse_args(argv)

    errors = run_phase6c_manuscript_draft_audit(args.repo)
    if errors:
        print("FAIL — Phase 6C manuscript draft audit")
        for err in errors:
            print(f"  - {err}")
        return 1

    print("PASS — Phase 6C manuscript draft audit")
    print(f"  manuscript: {(args.repo / MANUSCRIPT_TEX).resolve()}")
    print(f"  drafting notes: {(args.repo / DRAFTING_NOTES_MD).resolve()}")
    print()
    print("  prohibited claims: absent")
    print("  required metrics and caveats: present")
    print("  figure paths: referenced")
    print("  bibliography: TODO/placeholder marked")
    return 0


if __name__ == "__main__":
    sys.exit(main())
