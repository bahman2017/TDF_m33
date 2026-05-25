"""Tests for Phase 6E submission package audit."""

from __future__ import annotations

import hashlib
import importlib.util
from pathlib import Path

import pytest

from tdf_m33.reporting.phase6e_submission_package_audit import (
    MANUSCRIPT_TEX,
    SUBMISSION_CHECKLIST_MD,
    SUBMISSION_REPORT_MD,
    run_phase6e_submission_package_audit,
)

REPO_ROOT = Path(__file__).resolve().parents[1]


def _load_prepare_paper_figures():
    path = REPO_ROOT / "scripts" / "prepare_paper_figures.py"
    spec = importlib.util.spec_from_file_location("prepare_paper_figures", path)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def submission_result() -> tuple[list[str], dict]:
    return run_phase6e_submission_package_audit(REPO_ROOT)


def test_submission_checklist_exists() -> None:
    path = REPO_ROOT / SUBMISSION_CHECKLIST_MD
    assert path.is_file()
    text = path.read_text(encoding="utf-8")
    assert "Author" in text or "author" in text.lower()
    assert "Prohibited" in text or "prohibited" in text.lower()
    assert "PASS_WITH_CAVEAT" in text or "pass_with_caveat" in text.lower()


def test_submission_audit_passes(submission_result: tuple[list[str], dict]) -> None:
    errors, _ = submission_result
    assert errors == [], errors


def test_submission_report_written(submission_result: tuple[list[str], dict]) -> None:
    assert (REPO_ROOT / SUBMISSION_REPORT_MD).is_file()
    report = (REPO_ROOT / SUBMISSION_REPORT_MD).read_text(encoding="utf-8")
    assert "Phase 6E" in report
    _, meta = submission_result
    assert meta.get("compile", {}).get("status") in ("pass", "skipped", "fail")


def test_no_prohibited_affirmative_claims_in_manuscript() -> None:
    from tdf_m33.reporting.phase6b_manuscript_audit import _affirmative_forbidden

    tex = (REPO_ROOT / MANUSCRIPT_TEX).read_text(encoding="utf-8")
    for phrase in (
        "tdf replaces dark matter",
        "lensing is confirmed",
        "m33 proves tdf",
        "dark matter is disproven",
    ):
        assert not _affirmative_forbidden(tex, phrase), phrase


def test_data_and_code_availability_section() -> None:
    tex = (REPO_ROOT / MANUSCRIPT_TEX).read_text(encoding="utf-8").lower()
    assert "data and code availability" in tex
    assert "phase6a_reproducibility_commands" in tex or "reproducibility" in tex


def test_required_caveats_present() -> None:
    from tdf_m33.reporting.phase6b_manuscript_audit import REQUIRED_CAVEAT_GROUPS

    tex = (REPO_ROOT / MANUSCRIPT_TEX).read_text(encoding="utf-8").lower()
    for group in REQUIRED_CAVEAT_GROUPS:
        assert any(alt.lower() in tex for alt in group), f"missing caveat group: {group!r}"


def test_acknowledgments_placeholder() -> None:
    tex = (REPO_ROOT / MANUSCRIPT_TEX).read_text(encoding="utf-8").lower()
    assert "acknowledgments" in tex
    assert "placeholder" in tex or "todo" in tex


def test_figure_packaging_does_not_alter_sources(tmp_path: Path) -> None:
    """Copy-only packaging must preserve byte-identical PNGs under outputs/figures/."""
    mod = _load_prepare_paper_figures()
    FIGURE_MAP = mod.FIGURE_MAP
    prepare_paper_figures = mod.prepare_paper_figures

    src_root = tmp_path / "outputs" / "figures"
    src_root.mkdir(parents=True)
    for dest_name, pipeline_name in FIGURE_MAP.items():
        payload = f"fake-png-{pipeline_name}".encode()
        (src_root / pipeline_name).write_bytes(payload)

    copied, missing = prepare_paper_figures(tmp_path, dry_run=False)
    assert not missing
    assert copied

    for dest_name, pipeline_name in FIGURE_MAP.items():
        src = src_root / pipeline_name
        dest = tmp_path / "paper" / "figures" / dest_name
        assert dest.is_file()

        def digest(p: Path) -> str:
            return hashlib.sha256(p.read_bytes()).hexdigest()

        assert digest(src) == digest(dest)
        assert src.stat().st_mtime == dest.stat().st_mtime or digest(src) == digest(dest)
