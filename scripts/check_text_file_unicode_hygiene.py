#!/usr/bin/env python3
"""Scan repository text files for hidden/bidirectional Unicode control characters."""

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

from tdf_m33.text_unicode_hygiene import scan_repository


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Fail if hidden/bidi Unicode controls are present in text files."
    )
    parser.add_argument("--repo-root", type=Path, default=REPO_ROOT)
    args = parser.parse_args(argv)

    issues = scan_repository(args.repo_root)
    if not issues:
        print(f"Unicode hygiene OK ({args.repo_root})")
        return 0

    print(f"Found {len(issues)} forbidden Unicode control(s):", file=sys.stderr)
    for issue in issues:
        rel = issue.path.relative_to(args.repo_root)
        print(
            f"  {rel}:{issue.line}:{issue.column}: "
            f"U+{issue.codepoint:04X} {issue.name}",
            file=sys.stderr,
        )
    return 1


if __name__ == "__main__":
    sys.exit(main())
