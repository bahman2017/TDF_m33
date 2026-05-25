#!/usr/bin/env python3
"""Phase 4A: axisymmetric disk-plane 2D τ map from Phase 3C radial TDF."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from tdf_m33.fitting.phase4a_tdf_2d_map import run_phase4a_tdf_2d_map

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CONFIG = REPO_ROOT / "configs" / "m33_default.yaml"
PROFILES_CSV = REPO_ROOT / "outputs" / "tables" / "phase3c_tdf_lowparam_profiles.csv"
CONSISTENCY_CSV = REPO_ROOT / "outputs" / "tables" / "phase4a_tau_2d_radial_consistency.csv"
METADATA_CSV = REPO_ROOT / "outputs" / "tables" / "phase4a_tau_2d_map_metadata.csv"
MAP_NPZ = REPO_ROOT / "outputs" / "maps" / "phase4a_tau_2d_map.npz"
FIG_TAU = REPO_ROOT / "outputs" / "figures" / "phase4a_tau_2d_map.png"
FIG_GRAD = REPO_ROOT / "outputs" / "figures" / "phase4a_tau_gradient_2d_map.png"
FIG_CONSISTENCY = REPO_ROOT / "outputs" / "figures" / "phase4a_tau_2d_radial_consistency.png"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Phase 4A: axisymmetric 2D disk-plane τ map from Phase 3C."
    )
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--profiles", type=Path, default=PROFILES_CSV)
    parser.add_argument("--consistency", type=Path, default=CONSISTENCY_CSV)
    parser.add_argument("--metadata", type=Path, default=METADATA_CSV)
    parser.add_argument("--map", type=Path, default=MAP_NPZ)
    parser.add_argument("--fig-tau", type=Path, default=FIG_TAU)
    parser.add_argument("--fig-gradient", type=Path, default=FIG_GRAD)
    parser.add_argument("--fig-consistency", type=Path, default=FIG_CONSISTENCY)
    args = parser.parse_args(argv)

    try:
        consistency_df, metadata_df, maps = run_phase4a_tdf_2d_map(
            args.profiles,
            args.config,
            args.consistency,
            args.metadata,
            args.map,
            args.fig_tau,
            args.fig_gradient,
            args.fig_consistency,
        )
    except FileNotFoundError as exc:
        print(f"FAIL: {exc}")
        return 1
    except Exception as exc:
        print(f"FAIL: {exc}")
        return 1

    meta = metadata_df.iloc[0]
    print("PASS — Phase 4A axisymmetric 2D τ map")
    print(f"  source_model: {meta['source_model']}")
    print(f"  map npz: {args.map.resolve()}")
    print(f"  metadata: {args.metadata.resolve()}")
    print(f"  consistency: {args.consistency.resolve()}")
    print(f"  figure tau: {args.fig_tau.resolve()}")
    print(f"  figure gradient: {args.fig_gradient.resolve()}")
    print(f"  figure consistency: {args.fig_consistency.resolve()}")
    print()
    print(f"  grid: {meta['n_pixels']}×{meta['n_pixels']}, "
          f"extent ±{meta['x_extent_kpc']} kpc")
    print(f"  radial range: {meta['min_radius_covered_kpc']:.3f}–"
          f"{meta['max_radius_covered_kpc']:.3f} kpc")
    print(f"  masked grid fraction: {meta['fraction_grid_masked']:.4f}")
    print(f"  max |Δτ| (radial vs az avg): {meta['max_abs_radial_consistency_error']:.6g}")
    print(f"  RMSE radial consistency: {meta['rmse_radial_consistency_error']:.6g}")
    print(f"  n_compared: {int(meta['n_compared'])}")
    print()
    print(f"  {meta['note_axisymmetric_extension']}")
    print(f"  {meta['note_no_lensing']}")
    print(f"  {meta['note_k_tau']}")
    print(f"  {meta['note_baryonic_caveat']}")
    print()
    print("  lensing_tested: false")
    print("  dark_matter_disproven: false")
    print("  separately_fitted_2d_map: false")
    print(f"  rows in consistency table: {len(consistency_df)}")

    _ = maps
    return 0


if __name__ == "__main__":
    sys.exit(main())
