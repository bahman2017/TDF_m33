#!/usr/bin/env python3
"""Phase 2A: baryonic-only baseline diagnostics on canonical M33 rotation data."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from tdf_m33.fitting.phase2a_baryonic import run_phase2a_baryonic_only
from tdf_m33.models.baryonic import summarize_negative_residuals

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PROCESSED = REPO_ROOT / "data" / "processed" / "m33_rotation.csv"
METRICS_CSV = REPO_ROOT / "outputs" / "tables" / "phase2a_baryonic_only_metrics.csv"
PROFILE_CSV = REPO_ROOT / "outputs" / "tables" / "phase2a_baryonic_only_profile.csv"
FIG_ROTATION = REPO_ROOT / "outputs" / "figures" / "phase2a_baryonic_only_rotation_curve.png"
FIG_RESIDUAL = REPO_ROOT / "outputs" / "figures" / "phase2a_residual_velocity_squared.png"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Phase 2A baryonic-only baseline.")
    parser.add_argument("--input", type=Path, default=DEFAULT_PROCESSED)
    parser.add_argument("--metrics", type=Path, default=METRICS_CSV)
    parser.add_argument("--profile", type=Path, default=PROFILE_CSV)
    parser.add_argument("--fig-rotation", type=Path, default=FIG_ROTATION)
    parser.add_argument("--fig-residual", type=Path, default=FIG_RESIDUAL)
    args = parser.parse_args(argv)

    if not args.input.is_file():
        print(f"FAIL: processed CSV not found: {args.input}")
        return 1

    try:
        metrics_df, profile_df = run_phase2a_baryonic_only(
            args.input,
            args.metrics,
            args.profile,
            args.fig_rotation,
            args.fig_residual,
        )
    except Exception as exc:
        print(f"FAIL: {exc}")
        return 1

    row = metrics_df.iloc[0]
    n_neg = int(row["n_negative_residual_v2"])
    print("PASS — Phase 2A baryonic-only baseline")
    print(f"  metrics: {args.metrics.resolve()}")
    print(f"  profile: {args.profile.resolve()} ({len(profile_df)} rows)")
    print(f"  figure (rotation): {args.fig_rotation.resolve()}")
    print(f"  figure (residual): {args.fig_residual.resolve()}")
    print(f"  RMSE: {row['rmse_kms']:.2f} km/s")
    print(f"  chi-square: {row['chi_square']:.2f}")
    print(f"  reduced chi-square: {row['reduced_chi_square']:.3f}")
    print(f"  parameter_count: {int(row['parameter_count'])} (fixed baryonic, not fitted)")
    print(f"  AIC (χ²+2k): {row['aic']:.2f}")
    print(f"  BIC (χ²+k ln n): {row['bic']:.2f}")
    print(f"  negative residual_v2 points: {n_neg}")

    if n_neg > 0:
        rv2 = profile_df["residual_v2_kms2"].to_numpy()
        r = profile_df["r_kpc"].to_numpy()
        for line in summarize_negative_residuals(r, rv2):
            print(f"    {line}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
