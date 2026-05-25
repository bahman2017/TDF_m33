#!/usr/bin/env python3
"""Phase 3D: TDF low-parameter model sensitivity and robustness audit."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from tdf_m33.fitting.phase3d_tdf_sensitivity import run_phase3d_tdf_sensitivity

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CONFIG = REPO_ROOT / "configs" / "m33_default.yaml"
PROCESSED_CSV = REPO_ROOT / "data" / "processed" / "m33_rotation.csv"
PHASE3C_COMPARISON = REPO_ROOT / "outputs" / "tables" / "phase3c_tdf_lowparam_model_comparison.csv"
PHASE3A_CSV = REPO_ROOT / "outputs" / "tables" / "phase3a_tau_radial_reconstruction.csv"
COMBINED_CSV = REPO_ROOT / "outputs" / "tables" / "phase3c_combined_model_comparison.csv"
SUMMARY_CSV = REPO_ROOT / "outputs" / "tables" / "phase3d_tdf_sensitivity_summary.csv"
KTAU_CSV = REPO_ROOT / "outputs" / "tables" / "phase3d_ktau_sweep.csv"
MASK_CSV = REPO_ROOT / "outputs" / "tables" / "phase3d_fitmask_sensitivity.csv"
SMOOTH_CSV = REPO_ROOT / "outputs" / "tables" / "phase3d_smoothing_sensitivity.csv"
REPORT_MD = REPO_ROOT / "outputs" / "reports" / "phase3d_tdf_sensitivity_report.md"
FIG_PATH = REPO_ROOT / "outputs" / "figures" / "phase3d_tdf_sensitivity_summary.png"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Phase 3D TDF sensitivity audit.")
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--processed", type=Path, default=PROCESSED_CSV)
    parser.add_argument("--phase3c-comparison", type=Path, default=PHASE3C_COMPARISON)
    parser.add_argument("--phase3a", type=Path, default=PHASE3A_CSV)
    parser.add_argument("--combined", type=Path, default=COMBINED_CSV)
    parser.add_argument("--summary", type=Path, default=SUMMARY_CSV)
    parser.add_argument("--ktau", type=Path, default=KTAU_CSV)
    parser.add_argument("--fitmask", type=Path, default=MASK_CSV)
    parser.add_argument("--smoothing", type=Path, default=SMOOTH_CSV)
    parser.add_argument("--report", type=Path, default=REPORT_MD)
    parser.add_argument("--fig", type=Path, default=FIG_PATH)
    args = parser.parse_args(argv)

    try:
        summary_df, ktau_df, mask_df, smooth_df, _ = run_phase3d_tdf_sensitivity(
            args.processed,
            args.config,
            args.phase3c_comparison,
            args.phase3a,
            args.combined,
            args.summary,
            args.ktau,
            args.fitmask,
            args.smoothing,
            args.report,
            args.fig,
        )
    except FileNotFoundError as exc:
        print(f"FAIL: {exc}")
        return 1
    except Exception as exc:
        print(f"FAIL: {exc}")
        return 1

    print("PASS — Phase 3D TDF sensitivity audit")
    print(f"  summary: {args.summary.resolve()}")
    print(f"  K_tau sweep: {args.ktau.resolve()}")
    print(f"  fit-mask: {args.fitmask.resolve()}")
    print(f"  smoothing: {args.smoothing.resolve()}")
    print(f"  report: {args.report.resolve()}")
    print(f"  figure: {args.fig.resolve()}")
    print()
    for _, row in summary_df.iterrows():
        print(f"  {row['check_name']}: {row['value']} ({row['detail']})")
    print()
    print(f"  K_tau values: {sorted(ktau_df['k_tau'].unique())}")
    print(f"  sigma_kpc values: {sorted(smooth_df['sigma_kpc'].unique())}")
    print(f"  fit masks: {', '.join(mask_df['mask_name'].astype(str))}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
