"""Tests for Phase 6B manuscript skeleton audit."""

from pathlib import Path

import pytest

from tdf_m33.reporting.phase6b_manuscript_audit import (
    MANUSCRIPT_TEX,
    REQUIRED_OUTPUT_REFS,
    run_phase6b_manuscript_audit,
)

REPO_ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture(scope="module")
def audit_errors() -> list[str]:
    return run_phase6b_manuscript_audit(REPO_ROOT)


def test_manuscript_files_exist() -> None:
    for rel in (
        MANUSCRIPT_TEX,
        "paper/README.md",
        "docs/manuscript_outline.md",
        "docs/manuscript_figures_and_tables.md",
        "docs/manuscript_allowed_language.md",
    ):
        assert (REPO_ROOT / rel).is_file(), rel


def test_audit_passes(audit_errors: list[str]) -> None:
    assert audit_errors == [], audit_errors


def test_prohibited_claims_absent() -> None:
    from tdf_m33.reporting.phase6b_manuscript_audit import _affirmative_forbidden

    tex = (REPO_ROOT / MANUSCRIPT_TEX).read_text(encoding="utf-8")
    for phrase in (
        "tdf replaces dark matter",
        "lensing is confirmed",
        "m33 proves tdf",
        "no need for dark matter",
    ):
        assert not _affirmative_forbidden(tex, phrase), phrase


def test_required_output_paths_referenced() -> None:
    fig_doc = (REPO_ROOT / "docs/manuscript_figures_and_tables.md").read_text(
        encoding="utf-8"
    )
    for ref in REQUIRED_OUTPUT_REFS:
        assert ref in fig_doc or ref in (
            REPO_ROOT / MANUSCRIPT_TEX
        ).read_text(encoding="utf-8")


def test_manuscript_caveats_present() -> None:
    tex = (REPO_ROOT / MANUSCRIPT_TEX).read_text(encoding="utf-8").lower()
    assert "pass_with_caveat" in tex or "pass\\_with\\_caveat" in tex
    assert "k_tau" in tex or "k_\\tau" in tex
    assert "normalized" in tex
    assert "weak lensing" in tex or "weak-lensing" in tex
    assert "not disproven" in tex
