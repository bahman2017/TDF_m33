"""Tests for Phase 6D manuscript polish audit."""

from pathlib import Path

import pytest

from tdf_m33.reporting.phase6d_manuscript_polish_audit import (
    BIB_VERIFICATION_MD,
    MANUSCRIPT_TEX,
    POLISH_REPORT_MD,
    VERIFIED_DOIS,
    run_phase6d_manuscript_polish_audit,
)

REPO_ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture(scope="module")
def polish_result() -> tuple[list[str], dict[str, str]]:
    return run_phase6d_manuscript_polish_audit(REPO_ROOT)


def test_bibliography_verification_doc_exists() -> None:
    assert (REPO_ROOT / BIB_VERIFICATION_MD).is_file()
    text = (REPO_ROOT / BIB_VERIFICATION_MD).read_text(encoding="utf-8")
    assert "verified" in text.lower()
    assert "Corbelli2014" in text
    assert "LopezFune2017" in text


def test_polish_audit_passes(polish_result: tuple[list[str], dict[str, str]]) -> None:
    errors, _ = polish_result
    assert errors == [], errors


def test_verified_dois_in_manuscript() -> None:
    tex = (REPO_ROOT / MANUSCRIPT_TEX).read_text(encoding="utf-8")
    for doi in VERIFIED_DOIS:
        assert doi in tex


def test_no_bibliography_placeholders() -> None:
    tex = (REPO_ROOT / MANUSCRIPT_TEX).read_text(encoding="utf-8").lower()
    bib = tex.split(r"\begin{thebibliography}")[-1]
    assert "placeholder; verify" not in bib


def test_polish_report_written(polish_result: tuple[list[str], dict[str, str]]) -> None:
    assert (REPO_ROOT / POLISH_REPORT_MD).is_file()
    report = (REPO_ROOT / POLISH_REPORT_MD).read_text(encoding="utf-8")
    assert "Phase 6D" in report
    _, compile_info = polish_result
    assert compile_info["status"] in ("pass", "skipped", "fail")
