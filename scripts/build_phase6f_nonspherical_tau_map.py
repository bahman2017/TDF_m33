#!/usr/bin/env python3
"""Phase 6F: build non-spherical disk-plane tau-map (strict or reference-proxy)."""

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
from tdf_m33.maps.pipeline import build_tau_map
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
            "Phase 6F scientific tau-map reconstruction is blocked: primary Corbelli 2014 "
            "maps missing and/or validated WCS reprojection (G8) not implemented."
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
