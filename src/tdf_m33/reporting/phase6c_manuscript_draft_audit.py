"""Phase 6C: first readable manuscript draft audit (extends Phase 6B checks)."""

from __future__ import annotations

import re
from pathlib import Path

from tdf_m33.reporting.phase6b_manuscript_audit import (
    FIGURES_MD,
    MANUSCRIPT_TEX,
    _affirmative_forbidden,
    _read,
    audit_manuscript_files,
)

DRAFTING_NOTES_MD = "docs/manuscript_drafting_notes.md"

REQUIRED_SECTIONS = (
    r"\begin{abstract}",
    r"\section{Introduction}",
    r"\section{Data and provenance}",
    r"\section{Baryonic decomposition and caveats}",
    r"\section{Baseline models}",
    r"\section{TDF radial reconstruction}",
    r"\section{Low-parameter TDF comparison}",
    r"\section{Two-dimensional",
    r"\section{Deflection proxy and upper-bound consistency}",
    r"\section{Limitations}",
    r"\section{Future work}",
    r"\section{Conclusion}",
)

# Key metrics from phase6a_key_results_table.csv (allow rounded forms).
REQUIRED_METRIC_SNIPPETS = (
    "58.6",
    "4.16",
    "68.0",
    "72.0",
    "23.0",
    "3.51",
    "63.0",
    "69.0",
    "3.35",
    "76.5",
    "1.12",
    "7.5",
    "6.7",
)

REQUIRED_ALLOWED_PHRASES = (
    "competitive with the nfw",
    "competitive with nfw",
    "normalized deflection",
    "upper-bound consistency",
)

FIGURE_PATH_SNIPPETS = (
    "phase2a_baryonic_only_rotation_curve",
    "phase3c_tdf_lowparam_rotation_comparison",
    "phase3c_tdf_lowparam_tau_gradient",
    "phase4a_tau_2d_map",
    "phase4b_tau_sky_projected_map",
    "phase5a_deflection_magnitude_map",
)

BIB_TODO_MARKERS = ("todo", "placeholder", "verify")


def audit_phase6c_draft(repo: Path) -> list[str]:
    errors = audit_manuscript_files(repo)
    if not (repo / MANUSCRIPT_TEX).is_file():
        return errors

    tex_raw = _read(repo, MANUSCRIPT_TEX)
    tex = tex_raw.lower()

    if not (repo / DRAFTING_NOTES_MD).is_file():
        errors.append(f"missing file: {DRAFTING_NOTES_MD}")

    # Phase 6C: expanded draft markers
    if "phase 6c" not in tex and "first readable draft" not in tex:
        errors.append("manuscript missing Phase 6C draft marker")

    for sec in REQUIRED_SECTIONS:
        if sec.lower() not in tex and sec not in tex_raw:
            # section titles may be split (2D tau line)
            if sec.startswith(r"\section{Two-dimensional") and "two-dimensional" in tex:
                continue
            errors.append(f"missing section pattern: {sec}")

    for metric in REQUIRED_METRIC_SNIPPETS:
        if metric not in tex_raw:
            errors.append(f"missing required metric snippet: {metric!r}")

    if not any(p in tex for p in REQUIRED_ALLOWED_PHRASES):
        errors.append("manuscript missing allowed framing phrase (competitive / deflection / upper-bound)")

    for fig in FIGURE_PATH_SNIPPETS:
        if fig not in tex_raw:
            errors.append(f"missing figure path reference: {fig!r}")

    bib_lower = tex_raw.split(r"\begin{thebibliography}")[-1].lower() if "thebibliography" in tex_raw else ""
    if bib_lower and not any(m in bib_lower for m in BIB_TODO_MARKERS):
        errors.append("bibliography entries must contain TODO/placeholder/verify marker")

    # Minimum length for readable draft (excluding comments)
    body = re.sub(r"%.*", "", tex_raw)
    if len(body) < 12000:
        errors.append(f"manuscript body too short for Phase 6C draft ({len(body)} chars)")

    return errors


def run_phase6c_manuscript_draft_audit(repo: Path | None = None) -> list[str]:
    if repo is None:
        repo = Path(__file__).resolve().parents[3]
    return audit_phase6c_draft(repo)
