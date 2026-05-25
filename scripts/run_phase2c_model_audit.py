#!/usr/bin/env python3
"""Phase 2C: audit and consolidate Phase 2A/2B model comparison before TDF τ work."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from tdf_m33.fitting.phase2c_model_audit import run_phase2c_model_audit

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CONFIG = REPO_ROOT / "configs" / "m33_default.yaml"
PHASE2A_METRICS = REPO_ROOT / "outputs" / "tables" / "phase2a_baryonic_only_metrics.csv"
PHASE2A_PROFILE = REPO_ROOT / "outputs" / "tables" / "phase2a_baryonic_only_profile.csv"
PHASE2B_COMPARISON = REPO_ROOT / "outputs" / "tables" / "phase2b_model_comparison.csv"
PHASE2B_PARAMETERS = REPO_ROOT / "outputs" / "tables" / "phase2b_halo_fit_parameters.csv"
PHASE2B_PROFILES = REPO_ROOT / "outputs" / "tables" / "phase2b_rotation_profiles.csv"
SUMMARY_CSV = REPO_ROOT / "outputs" / "tables" / "phase2c_model_audit_summary.csv"
READINESS_CSV = REPO_ROOT / "outputs" / "tables" / "phase2c_residual_readiness.csv"
REPORT_MD = REPO_ROOT / "outputs" / "reports" / "phase2c_model_audit_report.md"
FIG_SUMMARY = REPO_ROOT / "outputs" / "figures" / "phase2c_model_audit_summary.png"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Phase 2C model comparison audit.")
    parser.add_argument("--phase2a-metrics", type=Path, default=PHASE2A_METRICS)
    parser.add_argument("--phase2a-profile", type=Path, default=PHASE2A_PROFILE)
    parser.add_argument("--phase2b-comparison", type=Path, default=PHASE2B_COMPARISON)
    parser.add_argument("--phase2b-parameters", type=Path, default=PHASE2B_PARAMETERS)
    parser.add_argument("--phase2b-profiles", type=Path, default=PHASE2B_PROFILES)
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--summary", type=Path, default=SUMMARY_CSV)
    parser.add_argument("--readiness", type=Path, default=READINESS_CSV)
    parser.add_argument("--report", type=Path, default=REPORT_MD)
    parser.add_argument("--fig", type=Path, default=FIG_SUMMARY)
    parser.add_argument("--no-figure", action="store_true")
    args = parser.parse_args(argv)

    try:
        summary_df, readiness_df, _ = run_phase2c_model_audit(
            args.phase2a_metrics,
            args.phase2a_profile,
            args.phase2b_comparison,
            args.phase2b_parameters,
            args.phase2b_profiles,
            args.summary,
            args.report,
            args.readiness,
            fig_out=None if args.no_figure else args.fig,
            config_path=args.config,
        )
    except FileNotFoundError as exc:
        print(f"FAIL: {exc}")
        print("Run Phase 2A and 2B scripts first.")
        return 1
    except Exception as exc:
        print(f"FAIL: {exc}")
        return 1

    bur = summary_df[summary_df["model_name"] == "burkert"].iloc[0]
    n_neg = int((readiness_df["sign_flag"] == "negative").sum())
    n_spikes = int(readiness_df["residual_spike_flag"].sum())

    print("PASS — Phase 2C model audit")
    print(f"  summary: {args.summary.resolve()}")
    print(f"  report: {args.report.resolve()}")
    print(f"  readiness: {args.readiness.resolve()} ({len(readiness_df)} rows)")
    if not args.no_figure:
        print(f"  figure: {args.fig.resolve()}")
    print()
    print("Models audited:", ", ".join(summary_df["model_name"].tolist()))
    print(
        f"  fit mask: {bur['fit_r_min_kpc']}–{bur['fit_r_max_kpc']} kpc "
        f"({int(bur['n_fit_points'])}/{int(bur['n_rows_total'])} points)"
    )
    print(f"  Burkert at r0 upper bound: {bool(bur['burkert_at_r0_upper_bound'])}")
    print(f"  Phase 2A Δv² negative points: {n_neg}")
    print(f"  Phase 2A residual spikes (heuristic): {n_spikes}")
    print("  τ reconstruction performed: False")
    print("  Phase 3 input: delta_v2 = v_obs^2 - v_bar^2 (Phase 2A only)")

    return 0


if __name__ == "__main__":
    sys.exit(main())
