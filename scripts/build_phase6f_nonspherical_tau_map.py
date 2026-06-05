#!/usr/bin/env python3
"""Phase 6F: build non-spherical disk-plane tau-map (strict or reference-proxy)."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from tdf_m33.maps.gates import BLOCKED_MESSAGE
from tdf_m33.maps.pipeline import build_tau_map

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CONFIG = REPO_ROOT / "configs" / "phase6f_nonspherical_tau_map.yaml"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Phase 6F non-spherical disk-plane tau-map builder."
    )
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--repo-root", type=Path, default=REPO_ROOT)
    parser.add_argument(
        "--allow-reference-proxy",
        action="store_true",
        help="Run reference-only diagnostic (not for scientific claims).",
    )
    args = parser.parse_args(argv)

    report, result = build_tau_map(
        args.config,
        args.repo_root,
        allow_reference_proxy=args.allow_reference_proxy,
    )

    if result is None:
        print(BLOCKED_MESSAGE)
        print(
            "Phase 6F scientific tau-map reconstruction is blocked pending primary "
            "Corbelli 2014 VLA+GBT HI and BVIgi stellar maps."
        )
        gate_md = args.repo_root / "outputs/reports/phase6f/phase6f_tau_map_gate_report.md"
        print(f"Gate report: {gate_md}")
        return 2

    print(f"Mode: {result.mode}")
    if result.marker:
        print(result.marker)
    print(f"Solver residual: {result.solver_diagnostics.residual_norm:.6g}")
    npz = args.repo_root / "outputs/maps/phase6f/phase6f_tau_map_disk_plane.npz"
    print(f"Wrote map: {npz}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
