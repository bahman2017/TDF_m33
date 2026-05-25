#!/usr/bin/env python3
"""Phase 3B-A: smoothed / regularized TDF τ-gradient reconstruction."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from tdf_m33.fitting.phase3b_tdf_regularized import run_phase3b_tdf_regularized

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CONFIG = REPO_ROOT / "configs" / "m33_default.yaml"
PHASE3A_CSV = REPO_ROOT / "outputs" / "tables" / "phase3a_tau_radial_reconstruction.csv"
PROFILES_CSV = REPO_ROOT / "outputs" / "tables" / "phase3b_tau_regularized_profiles.csv"
DIAGNOSTICS_CSV = REPO_ROOT / "outputs" / "tables" / "phase3b_tau_regularization_diagnostics.csv"
FIG_GRADIENT = REPO_ROOT / "outputs" / "figures" / "phase3b_tau_gradient_regularized.png"
FIG_TAU = REPO_ROOT / "outputs" / "figures" / "phase3b_tau_profile_regularized.png"
FIG_CHECK = REPO_ROOT / "outputs" / "figures" / "phase3b_tdf_regularized_reconstruction_check.png"
FIG_TRADEOFF = REPO_ROOT / "outputs" / "figures" / "phase3b_regularization_tradeoff.png"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Phase 3B-A regularized TDF τ reconstruction.")
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--phase3a", type=Path, default=PHASE3A_CSV)
    parser.add_argument("--profiles", type=Path, default=PROFILES_CSV)
    parser.add_argument("--diagnostics", type=Path, default=DIAGNOSTICS_CSV)
    parser.add_argument("--fig-gradient", type=Path, default=FIG_GRADIENT)
    parser.add_argument("--fig-tau", type=Path, default=FIG_TAU)
    parser.add_argument("--fig-check", type=Path, default=FIG_CHECK)
    parser.add_argument("--fig-tradeoff", type=Path, default=FIG_TRADEOFF)
    args = parser.parse_args(argv)

    try:
        profiles, diag = run_phase3b_tdf_regularized(
            args.phase3a,
            args.config,
            args.profiles,
            args.diagnostics,
            args.fig_gradient,
            args.fig_tau,
            args.fig_check,
            args.fig_tradeoff,
        )
    except FileNotFoundError as exc:
        print(f"FAIL: {exc}")
        print("Run Phase 3A first.")
        return 1
    except Exception as exc:
        print(f"FAIL: {exc}")
        return 1

    print("PASS — Phase 3B-A regularized TDF τ reconstruction")
    print(f"  profiles: {args.profiles.resolve()} ({len(profiles)} rows)")
    print(f"  diagnostics: {args.diagnostics.resolve()}")
    print(f"  figure (gradient): {args.fig_gradient.resolve()}")
    print(f"  figure (tau): {args.fig_tau.resolve()}")
    print(f"  figure (check): {args.fig_check.resolve()}")
    print(f"  figure (tradeoff): {args.fig_tradeoff.resolve()}")
    print()
    for _, row in diag.iterrows():
        print(f"  method: {row['method']}")
        print(f"    smoothing: {row['smoothing_parameters']}")
        print(
            f"    spikes raw→smooth: {int(row['raw_gradient_spike_count'])}"
            f" → {int(row['smoothed_gradient_spike_count'])}"
        )
        print(
            f"    smoothness raw→smooth: {row['raw_gradient_smoothness_metric']:.3g}"
            f" → {row['smoothed_gradient_smoothness_metric']:.3g}"
        )
        print(f"    RMSE vs obs: {row['reconstruction_rmse_smooth_kms']:.2f} km/s")
        print(f"    n_negative_smoothed_vtau2: {int(row['n_negative_smoothed_vtau2'])}")
    print("  AIC/BIC comparison: deferred (Phase 3C)")

    return 0


if __name__ == "__main__":
    sys.exit(main())
