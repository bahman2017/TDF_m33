#!/usr/bin/env python3
"""Phase 6F: evaluate Tier B public pilot gates P1–P6 (separate from Corbelli G gates)."""

from __future__ import annotations

import argparse
import importlib.util
import sys
from pathlib import Path

_bootstrap_path = Path(__file__).resolve().parent / "_bootstrap.py"
_bootstrap_spec = importlib.util.spec_from_file_location("_bootstrap", _bootstrap_path)
if _bootstrap_spec is None or _bootstrap_spec.loader is None:
    raise ImportError(f"Cannot load bootstrap from {_bootstrap_path}")
_bootstrap = importlib.util.module_from_spec(_bootstrap_spec)
_bootstrap_spec.loader.exec_module(_bootstrap)
REPO_ROOT = _bootstrap.REPO_ROOT

from tdf_m33.maps.public_pilot_gates import (
    PUBLIC_PILOT_CLAIM_LABEL,
    run_public_pilot_gates,
    write_public_pilot_gate_csv,
    write_public_pilot_gate_report_md,
)

DEFAULT_CSV = REPO_ROOT / "outputs/tables/phase6f/phase6f_public_pilot_gate_status.csv"
DEFAULT_REPORT = REPO_ROOT / "outputs/reports/phase6f/phase6f_public_pilot_gate_report.md"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Phase 6F public pilot gate checker (P1–P6).")
    parser.add_argument("--repo-root", type=Path, default=REPO_ROOT)
    parser.add_argument("--csv", type=Path, default=DEFAULT_CSV)
    parser.add_argument("--report-md", type=Path, default=DEFAULT_REPORT)
    args = parser.parse_args(argv)

    report = run_public_pilot_gates(args.repo_root)
    print(f"public_pilot_ready={report.public_pilot_ready}")
    print(f"claim_label={PUBLIC_PILOT_CLAIM_LABEL}")
    for g in report.gates:
        print(f"  {g.gate_id}: {g.status} — {g.message}")

    write_public_pilot_gate_csv(args.csv, report)
    write_public_pilot_gate_report_md(args.report_md, report)
    print(f"\nWrote: {args.csv}")
    print(f"Wrote: {args.report_md}")

    if not report.public_pilot_ready:
        if report.blocked_message:
            print(f"\n{report.blocked_message}")
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
