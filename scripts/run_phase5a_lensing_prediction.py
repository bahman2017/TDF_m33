#!/usr/bin/env python3
"""Phase 5A: normalized deflection-proxy maps from frozen sky-plane τ."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from tdf_m33.lensing.phase5a_lensing_prediction import run_phase5a_lensing_prediction

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CONFIG = REPO_ROOT / "configs" / "m33_default.yaml"
DEFLECTION_NPZ = REPO_ROOT / "outputs" / "maps" / "phase5a_tau_deflection_proxy_map.npz"
METADATA_CSV = REPO_ROOT / "outputs" / "tables" / "phase5a_lensing_prediction_metadata.csv"
SUMMARY_CSV = REPO_ROOT / "outputs" / "tables" / "phase5a_deflection_summary.csv"
REPORT_MD = REPO_ROOT / "outputs" / "reports" / "phase5a_lensing_prediction_report.md"
FIG_MAG = REPO_ROOT / "outputs" / "figures" / "phase5a_deflection_magnitude_map.png"
FIG_VEC = REPO_ROOT / "outputs" / "figures" / "phase5a_deflection_vector_field.png"
FIG_KAPPA = REPO_ROOT / "outputs" / "figures" / "phase5a_convergence_proxy_map.png"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Phase 5A: deflection-proxy maps from frozen sky-plane τ."
    )
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--map", type=Path, default=DEFLECTION_NPZ)
    parser.add_argument("--metadata", type=Path, default=METADATA_CSV)
    parser.add_argument("--summary", type=Path, default=SUMMARY_CSV)
    parser.add_argument("--report", type=Path, default=REPORT_MD)
    parser.add_argument("--fig-magnitude", type=Path, default=FIG_MAG)
    parser.add_argument("--fig-vectors", type=Path, default=FIG_VEC)
    parser.add_argument("--fig-convergence", type=Path, default=FIG_KAPPA)
    args = parser.parse_args(argv)

    try:
        metadata_df, summary_df, products = run_phase5a_lensing_prediction(
            args.config,
            args.map,
            args.metadata,
            args.summary,
            args.report,
            args.fig_magnitude,
            args.fig_vectors,
            args.fig_convergence,
        )
    except FileNotFoundError as exc:
        print(f"FAIL: {exc}")
        return 1
    except Exception as exc:
        print(f"FAIL: {exc}")
        return 1

    meta = metadata_df.iloc[0]
    print("PASS — Phase 5A lensing / deflection prediction (normalized proxy)")
    print(f"  deflection map: {args.map.resolve()}")
    print(f"  metadata: {args.metadata.resolve()}")
    print(f"  summary: {args.summary.resolve()}")
    print(f"  report: {args.report.resolve()}")
    print(f"  figure magnitude: {args.fig_magnitude.resolve()}")
    print(f"  figure vectors: {args.fig_vectors.resolve()}")
    if args.fig_convergence.is_file():
        print(f"  figure convergence: {args.fig_convergence.resolve()}")
    print()
    print(f"  source_model: {meta['source_model']}")
    print(f"  geometry_mode: {meta['geometry_mode']}")
    print(f"  placeholder_geometry_flag: {meta['placeholder_geometry_flag']}")
    print(f"  alpha_tau_scale: {meta['alpha_tau_scale']}")
    print(f"  units: {meta['units']}")
    print(f"  |alpha| max (finite): {meta['alpha_magnitude_max']:.6g}")
    print(f"  |alpha| median (finite): {meta['alpha_magnitude_median']:.6g}")
    print(f"  separate_halo_used: {meta['separate_halo_used']}")
    print(f"  lensing_only_fit: {meta['lensing_only_fit']}")
    print(f"  compare_to_observational_limits: {meta['compare_to_observational_limits']}")
    print()
    print(f"  {meta['note_prediction_scaffold']}")
    print(f"  {meta['note_no_dm_disproof']}")
    print()
    print("  observational_detection_claimed: false")
    print("  dark_matter_disproven: false")

    _ = products, summary_df
    return 0


if __name__ == "__main__":
    sys.exit(main())
