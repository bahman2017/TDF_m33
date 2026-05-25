#!/usr/bin/env python3
"""Phase 3A: direct pointwise TDF τ-gradient reconstruction from baryonic Δv²."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from tdf_m33.fitting.phase3a_tdf_radial import run_phase3a_tdf_radial

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CONFIG = REPO_ROOT / "configs" / "m33_default.yaml"
READINESS_CSV = REPO_ROOT / "outputs" / "tables" / "phase2c_residual_readiness.csv"
PHASE2A_PROFILE = REPO_ROOT / "outputs" / "tables" / "phase2a_baryonic_only_profile.csv"
PROCESSED_CSV = REPO_ROOT / "data" / "processed" / "m33_rotation.csv"
RECONSTRUCTION_CSV = REPO_ROOT / "outputs" / "tables" / "phase3a_tau_radial_reconstruction.csv"
DIAGNOSTICS_CSV = REPO_ROOT / "outputs" / "tables" / "phase3a_tau_reconstruction_diagnostics.csv"
FIG_GRADIENT = REPO_ROOT / "outputs" / "figures" / "phase3a_tau_gradient_raw.png"
FIG_TAU = REPO_ROOT / "outputs" / "figures" / "phase3a_tau_profile_raw.png"
FIG_CHECK = REPO_ROOT / "outputs" / "figures" / "phase3a_tdf_direct_reconstruction_check.png"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Phase 3A direct TDF τ reconstruction (baryonic Δv² only)."
    )
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--readiness", type=Path, default=READINESS_CSV)
    parser.add_argument("--phase2a-profile", type=Path, default=PHASE2A_PROFILE)
    parser.add_argument("--processed", type=Path, default=PROCESSED_CSV)
    parser.add_argument("--reconstruction", type=Path, default=RECONSTRUCTION_CSV)
    parser.add_argument("--diagnostics", type=Path, default=DIAGNOSTICS_CSV)
    parser.add_argument("--fig-gradient", type=Path, default=FIG_GRADIENT)
    parser.add_argument("--fig-tau", type=Path, default=FIG_TAU)
    parser.add_argument("--fig-check", type=Path, default=FIG_CHECK)
    args = parser.parse_args(argv)

    try:
        profile, diag = run_phase3a_tdf_radial(
            args.readiness,
            args.config,
            args.reconstruction,
            args.diagnostics,
            args.fig_gradient,
            args.fig_tau,
            args.fig_check,
            processed_path=args.processed,
            phase2a_profile_path=args.phase2a_profile,
        )
    except FileNotFoundError as exc:
        print(f"FAIL: {exc}")
        print("Run Phase 2A/2C first (phase2c_residual_readiness.csv).")
        return 1
    except Exception as exc:
        print(f"FAIL: {exc}")
        return 1

    d = diag.iloc[0]
    print("PASS — Phase 3A direct TDF τ reconstruction")
    print(f"  reconstruction: {args.reconstruction.resolve()}")
    print(f"  diagnostics: {args.diagnostics.resolve()}")
    print(f"  figure (gradient): {args.fig_gradient.resolve()}")
    print(f"  figure (tau): {args.fig_tau.resolve()}")
    print(f"  figure (check): {args.fig_check.resolve()}")
    print()
    print(f"  k_tau: {d['k_tau']}")
    print(f"  tau0: {d['tau0']}")
    print(f"  rows: {int(d['n_rows'])}")
    print(f"  n_negative_delta_v2: {int(d['n_negative_delta_v2'])}")
    print(f"  max |recon error|: {d['max_abs_reconstruction_error_kms']:.3e} km/s")
    print(f"  RMSE recon error: {d['rmse_reconstruction_error_kms']:.3e} km/s")
    print(f"  gradient spikes: {int(d['gradient_spike_count'])}")
    print(f"  {d['smoothness_warning']}")
    print("  identity check only — not AIC/BIC model comparison")

    return 0


if __name__ == "__main__":
    sys.exit(main())
