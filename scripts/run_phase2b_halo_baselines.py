#!/usr/bin/env python3
"""Phase 2B: NFW and Burkert halo baseline fits on canonical M33 rotation data."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from tdf_m33.fitting.phase2b_halo_baselines import run_phase2b_halo_baselines

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PROCESSED = REPO_ROOT / "data" / "processed" / "m33_rotation.csv"
DEFAULT_CONFIG = REPO_ROOT / "configs" / "m33_default.yaml"
COMPARISON_CSV = REPO_ROOT / "outputs" / "tables" / "phase2b_model_comparison.csv"
PARAMETERS_CSV = REPO_ROOT / "outputs" / "tables" / "phase2b_halo_fit_parameters.csv"
PROFILES_CSV = REPO_ROOT / "outputs" / "tables" / "phase2b_rotation_profiles.csv"
FIG_ROTATION = REPO_ROOT / "outputs" / "figures" / "phase2b_rotation_curve_comparison.png"
FIG_RESIDUAL = REPO_ROOT / "outputs" / "figures" / "phase2b_residuals_comparison.png"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Phase 2B NFW/Burkert halo baselines.")
    parser.add_argument("--input", type=Path, default=DEFAULT_PROCESSED)
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--comparison", type=Path, default=COMPARISON_CSV)
    parser.add_argument("--parameters", type=Path, default=PARAMETERS_CSV)
    parser.add_argument("--profiles", type=Path, default=PROFILES_CSV)
    parser.add_argument("--fig-rotation", type=Path, default=FIG_ROTATION)
    parser.add_argument("--fig-residual", type=Path, default=FIG_RESIDUAL)
    args = parser.parse_args(argv)

    if not args.input.is_file():
        print(f"FAIL: processed CSV not found: {args.input}")
        return 1

    try:
        comparison_df, params_df, profiles_df = run_phase2b_halo_baselines(
            args.input,
            args.config,
            args.comparison,
            args.parameters,
            args.profiles,
            args.fig_rotation,
            args.fig_residual,
        )
    except Exception as exc:
        print(f"FAIL: {exc}")
        return 1

    nfw_p = params_df[params_df["model_name"] == "nfw"].iloc[0]
    bur_p = params_df[params_df["model_name"] == "burkert"].iloc[0]

    print("PASS — Phase 2B halo baselines")
    print(f"  comparison: {args.comparison.resolve()}")
    print(f"  parameters: {args.parameters.resolve()}")
    print(f"  profiles: {args.profiles.resolve()} ({len(profiles_df)} rows)")
    print(f"  figure (rotation): {args.fig_rotation.resolve()}")
    print(f"  figure (residuals): {args.fig_residual.resolve()}")
    print()
    print("Model comparison (fit-masked metrics):")
    for _, row in comparison_df.iterrows():
        print(
            f"  {row['model_name']}: RMSE={row['rmse_kms']:.2f} km/s, "
            f"chi2={row['chi_square']:.1f}, red_chi2={row['reduced_chi_square']:.3f}, "
            f"k={int(row['parameter_count'])}, n_fit={int(row['n_fit_points'])}, "
            f"dof={int(row['dof'])}"
        )
    print()
    print(
        f"  fit mask: {comparison_df['fit_r_min_kpc'].iloc[0]}–"
        f"{comparison_df['fit_r_max_kpc'].iloc[0]} kpc "
        f"({int(comparison_df['n_fit_points'].iloc[0])} of "
        f"{int(comparison_df['n_rows_total'].iloc[0])} rows)"
    )
    print()
    print("Best-fit NFW:")
    print(f"  rho_s = {nfw_p['rho_s_msun_kpc3']:.4e} M_sun/kpc^3, r_s = {nfw_p['r_s_kpc']:.3f} kpc")
    print(f"  success={nfw_p['fit_success']}, cost={nfw_p['fit_cost']:.4g}")
    print("Best-fit Burkert:")
    print(f"  rho0 = {bur_p['rho0_msun_kpc3']:.4e} M_sun/kpc^3, r0 = {bur_p['r0_kpc']:.3f} kpc")
    print(f"  success={bur_p['fit_success']}, cost={bur_p['fit_cost']:.4g}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
