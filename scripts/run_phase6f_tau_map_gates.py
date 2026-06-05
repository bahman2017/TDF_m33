#!/usr/bin/env python3
"""Phase 6F: evaluate data gates for non-spherical tau-map engine."""

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

from tdf_m33.maps.gates import BLOCKED_MESSAGE
from tdf_m33.maps.pipeline import run_gate_check
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
