#!/usr/bin/env python3
"""Phase 5C-B: enclosed-mass upper-bound consistency vs López Fune 2017."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from tdf_m33.lensing.phase5c_upper_bound_consistency import (
    run_phase5c_upper_bound_consistency,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CONFIG = REPO_ROOT / "configs" / "m33_default.yaml"
PROFILE_CSV = REPO_ROOT / "outputs" / "tables" / "phase5c_tau_mass_proxy_profile.csv"
SUMMARY_CSV = REPO_ROOT / "outputs" / "tables" / "phase5c_upper_bound_consistency_summary.csv"
REPORT_MD = REPO_ROOT / "outputs" / "reports" / "phase5c_upper_bound_consistency_report.md"
FIG_PNG = REPO_ROOT / "outputs" / "figures" / "phase5c_tau_mass_proxy_vs_lopez_fune.png"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Phase 5C-B: τ enclosed-mass proxy vs López Fune dynamical upper bound."
    )
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--profile", type=Path, default=PROFILE_CSV)
    parser.add_argument("--summary", type=Path, default=SUMMARY_CSV)
    parser.add_argument("--report", type=Path, default=REPORT_MD)
    parser.add_argument("--fig", type=Path, default=FIG_PNG)
    args = parser.parse_args(argv)

    try:
        profile_df, summary_df, _ = run_phase5c_upper_bound_consistency(
            args.config,
            args.profile,
            args.summary,
            args.report,
            args.fig,
        )
    except (FileNotFoundError, ValueError) as exc:
        print(f"FAIL: {exc}")
        return 1

    s = summary_df.iloc[0]
    print("PASS — Phase 5C-B upper-bound dynamical consistency")
    print(f"  profile: {args.profile.resolve()}")
    print(f"  summary: {args.summary.resolve()}")
    print(f"  report: {args.report.resolve()}")
    print(f"  figure: {args.fig.resolve()}")
    print()
    print(f"  source_model: {s['source_model']}")
    print(f"  radius_used_kpc: {s['radius_used_kpc']:.2f}")
    print(f"  M_tau_eff_msun: {s['M_tau_eff_msun']:.4e}")
    print(f"  M_lopez_enclosed_msun: {s['M_lopez_enclosed_msun']:.4e}")
    print(f"  M_lopez_uncertainty_msun: {s['M_lopez_uncertainty_msun']:.4e}")
    print(f"  ratio_tau_to_lopez: {s['ratio_tau_to_lopez']:.4f}")
    print(f"  consistency_status: {s['consistency_status']}")
    print()
    print(f"  profile radii: {len(profile_df)}")
    print(f"  observational_limits_enabled: {s['observational_limits_enabled']}")
    print(f"  not_direct_lensing_flag: {s['not_direct_lensing_flag']}")
    print(f"  separate_halo_used: {s['separate_halo_used']}")
    print(f"  lensing_only_fit: {s['lensing_only_fit']}")
    print()
    print(f"  {s['consistency_rationale']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
