#!/usr/bin/env python3
"""Phase 6F: evaluate data gates for non-spherical tau-map engine."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from tdf_m33.maps.gates import BLOCKED_MESSAGE
from tdf_m33.maps.pipeline import run_gate_check

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CONFIG = REPO_ROOT / "configs" / "phase6f_nonspherical_tau_map.yaml"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Phase 6F data gate checker.")
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--repo-root", type=Path, default=REPO_ROOT)
    args = parser.parse_args(argv)

    report = run_gate_check(args.config, args.repo_root)
    print(f"scientific_ready={report.scientific_ready}")
    for g in report.gates:
        print(f"  {g.gate_id}: {g.status} — {g.message}")

    gate_csv = args.repo_root / "outputs/tables/phase6f/phase6f_data_gate_status.csv"
    gate_md = args.repo_root / "outputs/reports/phase6f/phase6f_tau_map_gate_report.md"
    print(f"\nWrote: {gate_csv}")
    print(f"Wrote: {gate_md}")

    if not report.scientific_ready:
        print(f"\n{BLOCKED_MESSAGE}")
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
