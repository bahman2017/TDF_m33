#!/usr/bin/env python3
"""Phase 4B-A: project Phase 4A disk-plane τ map to sky-plane coordinates."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from tdf_m33.fitting.phase4b_tau_projection import run_phase4b_tau_projection

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CONFIG = REPO_ROOT / "configs" / "m33_default.yaml"
METADATA_CSV = REPO_ROOT / "outputs" / "tables" / "phase4b_tau_projection_metadata.csv"
PROJECTED_NPZ = REPO_ROOT / "outputs" / "maps" / "phase4b_tau_sky_projected_map.npz"
FIG_SKY = REPO_ROOT / "outputs" / "figures" / "phase4b_tau_sky_projected_map.png"
FIG_GEOM = REPO_ROOT / "outputs" / "figures" / "phase4b_projection_geometry_check.png"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Phase 4B-A: disk-to-sky τ map projection (geometry only)."
    )
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--metadata", type=Path, default=METADATA_CSV)
    parser.add_argument("--map", type=Path, default=PROJECTED_NPZ)
    parser.add_argument("--fig-sky", type=Path, default=FIG_SKY)
    parser.add_argument("--fig-geometry", type=Path, default=FIG_GEOM)
    args = parser.parse_args(argv)

    try:
        metadata_df, projected = run_phase4b_tau_projection(
            args.config,
            args.metadata,
            args.map,
            args.fig_sky,
            args.fig_geometry,
        )
    except FileNotFoundError as exc:
        print(f"FAIL: {exc}")
        return 1
    except Exception as exc:
        print(f"FAIL: {exc}")
        return 1

    meta = metadata_df.iloc[0]
    print("PASS — Phase 4B disk-to-sky τ projection")
    print(f"  source_map: {meta['source_map']}")
    print(f"  source_model: {meta['source_model']}")
    print(f"  projected map: {args.map.resolve()}")
    print(f"  metadata: {args.metadata.resolve()}")
    print(f"  figure sky: {args.fig_sky.resolve()}")
    print(f"  figure geometry: {args.fig_geometry.resolve()}")
    print()
    print(f"  geometry_mode: {meta['geometry_mode']}")
    print(f"  geometry_source: {meta['geometry_source']}")
    print(f"  geometry_reference: {meta['geometry_reference']}")
    print(f"  geometry_resolution: {meta['geometry_resolution']}")
    print(f"  placeholder_geometry_flag: {meta['placeholder_geometry_flag']}")
    print(f"  tilted_ring_method: {meta['tilted_ring_method']}")
    print(f"  n_tilted_rings: {int(meta['n_tilted_rings'])}")
    print(
        f"  i ring range: {meta['inclination_min_deg']:.1f}–"
        f"{meta['inclination_max_deg']:.1f} deg"
    )
    print(
        f"  PA ring range: {meta['position_angle_min_deg']:.1f}–"
        f"{meta['position_angle_max_deg']:.1f} deg"
    )
    if meta["geometry_mode"] == "global_approximation":
        print(f"  inclination_deg: {meta['inclination_deg']}")
        print(f"  position_angle_deg: {meta['position_angle_deg']}")
    print(f"  masked_fraction: {meta['masked_fraction']:.4f}")
    print(f"  max_roundtrip_error_kpc: {meta['max_roundtrip_error_kpc']}")
    print()
    print(f"  {meta['note_geometry_only']}")
    print(f"  {meta['note_no_lensing']}")
    print(f"  {meta['note_no_new_tau_fit']}")
    print()
    print("  lensing_tested: false")
    print("  dark_matter_disproven: false")
    print("  new_tau_parameters_fitted: false")
    print(f"  tau array shape: {projected['tau_sky'].shape}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
