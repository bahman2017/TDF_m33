#!/usr/bin/env python3
"""Phase 6F: dry-run downloader for Tier B public pilot sources (no credentials, no bulk fetch)."""

from __future__ import annotations

import argparse
import importlib.util
import sys
from pathlib import Path

_bootstrap_path = Path(__file__).resolve().parent / "_bootstrap.py"
_bootstrap_spec = importlib.util.spec_from_file_location("_bootstrap", _bootstrap_path)
if _bootstrap_spec is None or _bootstrap_spec.loader is None:
    raise ImportError(f"Cannot load bootstrap from {_bootstrap_path}")
_bootstrap = importlib.util.module_from_spec(_bootstrap_spec)
_bootstrap_spec.loader.exec_module(_bootstrap)
REPO_ROOT = _bootstrap.REPO_ROOT

from tdf_m33.maps.public_pilot_inventory import (
    PUBLIC_PILOT_CLAIM_LABEL,
    load_public_pilot_registry,
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Dry-run public pilot download planner (default: no network fetch)."
    )
    parser.add_argument("--repo-root", type=Path, default=REPO_ROOT)
    parser.add_argument(
        "--execute",
        action="store_true",
        help="Reserved for future per-source downloads; currently always dry-run.",
    )
    parser.add_argument(
        "--source",
        action="append",
        default=[],
        help="Filter by source id (e.g. s4g_irac_36, iram_lp006_co21_integrated).",
    )
    args = parser.parse_args(argv)

    registry = load_public_pilot_registry(args.repo_root)
    sources = registry.get("sources", [])
    filter_ids = set(args.source) if args.source else None

    print(f"Claim label: {PUBLIC_PILOT_CLAIM_LABEL}")
    print("Mode: dry-run (no files downloaded)")
    if args.execute:
        print("Note: --execute not implemented; use manual protocol in docs.")

    for entry in sources:
        if not isinstance(entry, dict):
            continue
        sid = str(entry.get("id", ""))
        if filter_ids and sid not in filter_ids:
            continue
        print(f"\n[{sid}]")
        print(f"  URL: {entry.get('source_url_or_doi', '')}")
        print(f"  Target: {entry.get('target_folder', '')}")
        print(f"  Login: {entry.get('login_required', 'unknown')}")
        print(f"  Patterns: {entry.get('expected_file_patterns', [])}")
        if entry.get("login_required"):
            print("  -> Manual download required (no credentials in repo).")

    print("\nSee docs/phase6f_public_pilot_download_instructions.md")
    return 0


if __name__ == "__main__":
    sys.exit(main())
