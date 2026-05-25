#!/usr/bin/env python3
"""Phase 3C: low-parameter knot τ-gradient TDF model comparison."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from tdf_m33.fitting.phase3c_tdf_lowparam import run_phase3c_tdf_lowparam

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CONFIG = REPO_ROOT / "configs" / "m33_default.yaml"
PROCESSED_CSV = REPO_ROOT / "data" / "processed" / "m33_rotation.csv"
PHASE3A_CSV = REPO_ROOT / "outputs" / "tables" / "phase3a_tau_radial_reconstruction.csv"
PHASE2B_COMPARISON = REPO_ROOT / "outputs" / "tables" / "phase2b_model_comparison.csv"
COMPARISON_CSV = REPO_ROOT / "outputs" / "tables" / "phase3c_tdf_lowparam_model_comparison.csv"
PARAMETERS_CSV = REPO_ROOT / "outputs" / "tables" / "phase3c_tdf_lowparam_fit_parameters.csv"
PROFILES_CSV = REPO_ROOT / "outputs" / "tables" / "phase3c_tdf_lowparam_profiles.csv"
COMBINED_CSV = REPO_ROOT / "outputs" / "tables" / "phase3c_combined_model_comparison.csv"
FIG_ROTATION = REPO_ROOT / "outputs" / "figures" / "phase3c_tdf_lowparam_rotation_comparison.png"
FIG_GRADIENT = REPO_ROOT / "outputs" / "figures" / "phase3c_tdf_lowparam_tau_gradient.png"
FIG_RESIDUALS = REPO_ROOT / "outputs" / "figures" / "phase3c_tdf_lowparam_residuals.png"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Phase 3C low-parameter TDF fits.")
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--processed", type=Path, default=PROCESSED_CSV)
    parser.add_argument("--phase3a", type=Path, default=PHASE3A_CSV)
    parser.add_argument("--phase2b-comparison", type=Path, default=PHASE2B_COMPARISON)
    parser.add_argument("--comparison", type=Path, default=COMPARISON_CSV)
    parser.add_argument("--parameters", type=Path, default=PARAMETERS_CSV)
    parser.add_argument("--profiles", type=Path, default=PROFILES_CSV)
    parser.add_argument("--combined", type=Path, default=COMBINED_CSV)
    parser.add_argument("--fig-rotation", type=Path, default=FIG_ROTATION)
    parser.add_argument("--fig-gradient", type=Path, default=FIG_GRADIENT)
    parser.add_argument("--fig-residuals", type=Path, default=FIG_RESIDUALS)
    args = parser.parse_args(argv)

    try:
        comparison_df, params_df, profiles_df, combined_df = run_phase3c_tdf_lowparam(
            args.processed,
            args.config,
            args.comparison,
            args.parameters,
            args.profiles,
            args.combined,
            args.fig_rotation,
            args.fig_gradient,
            args.fig_residuals,
            args.phase2b_comparison,
            phase3a_path=args.phase3a if args.phase3a.is_file() else None,
        )
    except FileNotFoundError as exc:
        print(f"FAIL: {exc}")
        return 1
    except Exception as exc:
        print(f"FAIL: {exc}")
        return 1

    print("PASS — Phase 3C low-parameter TDF models")
    print(f"  comparison: {args.comparison.resolve()}")
    print(f"  parameters: {args.parameters.resolve()}")
    print(f"  profiles: {args.profiles.resolve()} ({len(profiles_df)} rows)")
    print(f"  combined: {args.combined.resolve()} ({len(combined_df)} models)")
    print(f"  figure (rotation): {args.fig_rotation.resolve()}")
    print(f"  figure (gradient): {args.fig_gradient.resolve()}")
    print(f"  figure (residuals): {args.fig_residuals.resolve()}")
    print()
    print("TDF low-parameter metrics (fit mask):")
    for _, row in comparison_df.iterrows():
        print(
            f"  {row['model_name']}: RMSE={row['rmse_kms']:.2f} km/s, "
            f"chi2={row['chi_square']:.1f}, red_chi2={row['reduced_chi_square']:.3f}, "
            f"k={int(row['parameter_count'])}, AIC={row['aic']:.1f}, BIC={row['bic']:.1f}"
        )
    print()
    nfw = combined_df[combined_df["model_name"] == "nfw"].iloc[0]
    print(
        f"  NFW reference: RMSE={nfw['rmse_kms']:.2f} km/s, "
        f"AIC={nfw['aic']:.1f}, BIC={nfw['bic']:.1f}, k=2"
    )
    burk = combined_df[combined_df["model_name"] == "burkert"].iloc[0]
    print(f"  Burkert: RMSE={burk['rmse_kms']:.2f} km/s (r0 bound-limited; see notes)")
    print("  Qualify any TDF vs NFW claim — not a DM disproof.")

    return 0


if __name__ == "__main__":
    sys.exit(main())
