#!/usr/bin/env python3
"""Phase 6A: publication-ready results consolidation and claim-control audit."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from tdf_m33.reporting.phase6a_publication_audit import run_phase6a_publication_audit

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CONFIG = REPO_ROOT / "configs" / "m33_default.yaml"
SUMMARY_MD = REPO_ROOT / "outputs" / "reports" / "phase6a_publication_results_summary.md"
KEY_CSV = REPO_ROOT / "outputs" / "tables" / "phase6a_key_results_table.csv"
CLAIM_CSV = REPO_ROOT / "outputs" / "tables" / "phase6a_claim_traceability_matrix.csv"
REPRO_MD = REPO_ROOT / "outputs" / "reports" / "phase6a_reproducibility_commands.md"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Phase 6A: consolidate publication results and claim traceability."
    )
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--summary", type=Path, default=SUMMARY_MD)
    parser.add_argument("--key-results", type=Path, default=KEY_CSV)
    parser.add_argument("--claims", type=Path, default=CLAIM_CSV)
    parser.add_argument("--repro", type=Path, default=REPRO_MD)
    args = parser.parse_args(argv)

    try:
        key_df, claims_df, _ = run_phase6a_publication_audit(
            args.config,
            args.summary,
            args.key_results,
            args.claims,
            args.repro,
        )
    except (FileNotFoundError, ValueError) as exc:
        print(f"FAIL: {exc}")
        return 1

    n_supported = (claims_df["supported_status"] == "supported").sum()
    print("PASS — Phase 6A publication audit")
    print(f"  summary: {args.summary.resolve()}")
    print(f"  key results: {args.key_results.resolve()} ({len(key_df)} rows)")
    print(f"  claim matrix: {args.claims.resolve()} ({len(claims_df)} claims)")
    print(f"  reproducibility: {args.repro.resolve()}")
    print()
    print(f"  supported claims: {n_supported}")
    print(f"  caveated claims: {(claims_df['supported_status'] == 'caveated').sum()}")
    print(f"  future_work claims: {(claims_df['supported_status'] == 'future_work').sum()}")
    t3 = key_df.loc[key_df["result_id"] == "tdf_lowparam_3knot"].iloc[0]
    print(f"  TDF 3-knot RMSE: {t3['rmse_kms']:.3f} km/s; AIC: {t3['aic']:.2f}")
    lopez = key_df.loc[key_df["result_id"] == "phase5c_upper_bound_lopez_fune"].iloc[0]
    print(f"  López Fune status: {lopez['boundary_or_constraint_flag']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
