"""Phase 6B: manuscript skeleton and claim-control file audit."""

from __future__ import annotations

from pathlib import Path

MANUSCRIPT_TEX = "paper/m33_tdf_tau_geometry_draft.tex"
PAPER_README = "paper/README.md"
OUTLINE_MD = "docs/manuscript_outline.md"
FIGURES_MD = "docs/manuscript_figures_and_tables.md"
ALLOWED_MD = "docs/manuscript_allowed_language.md"

REQUIRED_OUTPUT_REFS = (
    "outputs/tables/phase6a_key_results_table.csv",
    "outputs/tables/phase6a_claim_traceability_matrix.csv",
    "outputs/reports/phase6a_publication_results_summary.md",
    "outputs/tables/phase3c_combined_model_comparison.csv",
    "outputs/tables/phase3d_tdf_sensitivity_summary.csv",
    "outputs/maps/phase4b_tau_sky_projected_map.npz",
    "outputs/maps/phase5a_tau_deflection_proxy_map.npz",
    "outputs/tables/phase5c_upper_bound_consistency_summary.csv",
)

PROHIBITED_PHRASES = (
    "tdf replaces dark matter",
    "replaces dark matter",
    "lensing is confirmed",
    "m33 proves tdf",
    "physical arcsecond prediction",
    "no need for dark matter",
    "weak lensing comparison complete",
)

PROHIBITED_WITH_NEGATION_CHECK = (
    "dark matter is disproven",
    "dark matter disproven",
)

# Each entry: any one alternative must appear in the manuscript (LaTeX escapes OK).
REQUIRED_CAVEAT_GROUPS: tuple[tuple[str, ...], ...] = (
    ("pass_with_caveat", "pass\\_with\\_caveat", "pass with caveat"),
    ("k_tau", "k_\\tau", "k_τ"),
    ("normalized_proxy", "normalized proxy", "normalized\\_proxy"),
    ("weak lensing", "weak-lensing"),
    ("not disproven", "not disproven"),
)


def _read(repo: Path, rel: str) -> str:
    path = repo / rel
    if not path.is_file():
        raise FileNotFoundError(f"Missing required file: {path}")
    return path.read_text(encoding="utf-8")


def _affirmative_forbidden(text: str, phrase: str) -> bool:
    """True if phrase appears as an affirmative claim (line-level check)."""
    phrase_l = phrase.lower()
    for line in text.splitlines():
        lline = line.lower()
        if phrase_l not in lline:
            continue
        if "prohibited" in lline:
            continue
        if any(
            neg in lline
            for neg in (
                "do not",
                "does not",
                "not claim",
                "not} claim",
                r"\emph{not}",
                "emph{not}",
            )
        ):
            continue
        if "not " in lline and lline.find("not") < lline.find(phrase_l):
            continue
        if "not disproven" in lline:
            continue
        return True
    return False


def audit_manuscript_files(repo: Path) -> list[str]:
    errors: list[str] = []
    required_files = (
        MANUSCRIPT_TEX,
        PAPER_README,
        OUTLINE_MD,
        FIGURES_MD,
        ALLOWED_MD,
    )
    for rel in required_files:
        if not (repo / rel).is_file():
            errors.append(f"missing file: {rel}")

    if errors:
        return errors

    tex_raw = _read(repo, MANUSCRIPT_TEX)
    tex = tex_raw.lower()
    ref_docs = "\n".join(_read(repo, p) for p in (FIGURES_MD, OUTLINE_MD))

    for phrase in PROHIBITED_PHRASES:
        if phrase in tex:
            errors.append(f"prohibited phrase in manuscript: {phrase!r}")

    for phrase in PROHIBITED_WITH_NEGATION_CHECK:
        if _affirmative_forbidden(tex_raw, phrase):
            errors.append(f"prohibited affirmative phrase in manuscript: {phrase!r}")

    for group in REQUIRED_CAVEAT_GROUPS:
        if not any(alt.lower() in tex for alt in group):
            errors.append(f"manuscript missing caveat group: {group!r}")

    for ref in REQUIRED_OUTPUT_REFS:
        if ref not in ref_docs and ref not in tex_raw:
            errors.append(f"required output path not referenced: {ref}")

    # Core framing
    if "intermediate-scale" not in tex and "intermediate scale" not in tex:
        errors.append("manuscript missing intermediate-scale framing")

    return errors


def run_phase6b_manuscript_audit(repo: Path | None = None) -> list[str]:
    if repo is None:
        repo = Path(__file__).resolve().parents[3]
    return audit_manuscript_files(repo)
