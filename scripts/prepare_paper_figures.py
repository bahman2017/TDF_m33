#!/usr/bin/env python3
"""Copy pipeline figure PNGs into paper/figures/ for submission packaging (no content changes)."""

from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
OUTPUTS_FIGURES = REPO_ROOT / "outputs" / "figures"
PAPER_FIGURES = REPO_ROOT / "paper" / "figures"

# Manuscript figure name -> pipeline source filename (under outputs/figures/)
FIGURE_MAP: dict[str, str] = {
    "fig1_rotation_baryonic.png": "phase2a_baryonic_only_rotation_curve.png",
    "fig2_model_comparison.png": "phase3c_tdf_lowparam_rotation_comparison.png",
    "fig3_tau_gradient.png": "phase3c_tdf_lowparam_tau_gradient.png",
    "fig4_tau_map.png": "phase4b_tau_sky_projected_map.png",
    "fig4_tau_map_disk.png": "phase4a_tau_2d_map.png",
    "fig4_tau_map_sky.png": "phase4b_tau_sky_projected_map.png",
    "fig5_deflection_proxy.png": "phase5a_deflection_magnitude_map.png",
}


def prepare_paper_figures(
    repo: Path,
    *,
    dry_run: bool = False,
) -> tuple[list[str], list[str]]:
    """Return (copied_names, missing_sources)."""
    dest_dir = repo / "paper" / "figures"
    src_root = repo / "outputs" / "figures"
    copied: list[str] = []
    missing: list[str] = []

    if not dry_run:
        dest_dir.mkdir(parents=True, exist_ok=True)

    lines = [
        "# Paper figures (Phase 6E packaging)",
        "",
        "Copies of pipeline PNGs for journal submission. **Content is unchanged** — "
        "sources remain under `outputs/figures/`.",
        "",
        "| Manuscript file | Pipeline source |",
        "|-----------------|-----------------|",
    ]

    for dest_name, src_name in FIGURE_MAP.items():
        src = src_root / src_name
        dest = dest_dir / dest_name
        lines.append(f"| `{dest_name}` | `outputs/figures/{src_name}` |")
        if not src.is_file():
            missing.append(src_name)
            continue
        if not dry_run:
            shutil.copy2(src, dest)
        copied.append(dest_name)

    lines.extend(
        [
            "",
            "Regenerate pipeline figures with the commands in "
            "`docs/manuscript_figures_and_tables.md`, then re-run:",
            "",
            "```bash",
            "python scripts/prepare_paper_figures.py",
            "```",
            "",
            "Primary single-panel alias for Fig.~4 in some layouts: `fig4_tau_map_sky.png`.",
            "",
        ]
    )

    readme = dest_dir / "README.md"
    if not dry_run:
        readme.write_text("\n".join(lines), encoding="utf-8")

    return copied, missing


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Copy figures to paper/figures/.")
    parser.add_argument("--repo", type=Path, default=REPO_ROOT)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args(argv)

    copied, missing = prepare_paper_figures(args.repo, dry_run=args.dry_run)
    print("PASS — prepare paper figures (copy only)")
    print(f"  destination: {(args.repo / 'paper' / 'figures').resolve()}")
    print(f"  copied: {len(copied)}")
    for name in copied:
        print(f"    - {name}")
    if missing:
        print(f"  missing sources: {len(missing)}")
        for name in missing:
            print(f"    - outputs/figures/{name}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
