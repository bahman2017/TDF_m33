"""Tests for Phase 6C expanded manuscript draft audit."""

from pathlib import Path

import pytest

from tdf_m33.reporting.phase6c_manuscript_draft_audit import (
    DRAFTING_NOTES_MD,
    MANUSCRIPT_TEX,
    REQUIRED_METRIC_SNIPPETS,
    run_phase6c_manuscript_draft_audit,
)

REPO_ROOT = Path(__file__).resolve().parents[1]

PROHIBITED = (
    "tdf replaces dark matter",
    "lensing is confirmed",
    "m33 proves tdf",
    "physical arcsecond prediction",
)


@pytest.fixture(scope="module")
def audit_errors() -> list[str]:
    return run_phase6c_manuscript_draft_audit(REPO_ROOT)


def test_phase6c_audit_passes(audit_errors: list[str]) -> None:
    assert audit_errors == [], audit_errors


def test_drafting_notes_exist() -> None:
    assert (REPO_ROOT / DRAFTING_NOTES_MD).is_file()


def test_manuscript_has_metrics() -> None:
    tex = (REPO_ROOT / MANUSCRIPT_TEX).read_text(encoding="utf-8")
    for m in REQUIRED_METRIC_SNIPPETS:
        assert m in tex


def test_prohibited_absent() -> None:
    from tdf_m33.reporting.phase6b_manuscript_audit import _affirmative_forbidden

    tex = (REPO_ROOT / MANUSCRIPT_TEX).read_text(encoding="utf-8")
    for phrase in PROHIBITED:
        assert not _affirmative_forbidden(tex, phrase), phrase


def test_caveats_in_manuscript() -> None:
    tex = (REPO_ROOT / MANUSCRIPT_TEX).read_text(encoding="utf-8").lower()
    assert "pass_with_caveat" in tex or "pass\\_with\\_caveat" in tex
    assert "normalized" in tex
    assert "weak lensing" in tex or "weak-lensing" in tex
    assert "not disproven" in tex


def test_figure_paths_referenced() -> None:
    tex = (REPO_ROOT / MANUSCRIPT_TEX).read_text(encoding="utf-8")
    assert "phase5a_deflection_magnitude_map" in tex
    assert "phase4b_tau_sky_projected_map" in tex


def test_bibliography_verified_or_todo() -> None:
    tex = (REPO_ROOT / MANUSCRIPT_TEX).read_text(encoding="utf-8").lower()
    assert "10.1051/0004-6361/201424033" in tex
    assert "10.1093/mnras/stx2742" in tex
