"""Tests for repository Unicode hygiene scanner."""

from __future__ import annotations

from pathlib import Path

from tdf_m33.text_unicode_hygiene import (
    FORBIDDEN_CODEPOINTS,
    normalize_text_content,
    scan_repository,
    scan_text_file,
)

REPO_ROOT = Path(__file__).resolve().parents[1]


def test_repository_has_no_forbidden_unicode_controls() -> None:
    issues = scan_repository(REPO_ROOT)
    assert issues == [], "\n".join(
        f"{i.path}:{i.line}: U+{i.codepoint:04X} {i.name}" for i in issues
    )


def test_scan_detects_zero_width_space(tmp_path: Path) -> None:
    bad = tmp_path / "bad.txt"
    bad.write_text("hello\u200bworld\n", encoding="utf-8")
    issues = scan_text_file(bad)
    assert len(issues) == 1
    assert issues[0].codepoint == 0x200B


def test_normalize_strips_controls() -> None:
    text = "a\u200bb\r\nc"
    out = normalize_text_content(text)
    assert "\u200b" not in out
    assert out == "ab\nc"


def test_forbidden_set_matches_spec() -> None:
    assert 0x202A in FORBIDDEN_CODEPOINTS
    assert 0x2069 in FORBIDDEN_CODEPOINTS
    assert 0x200E in FORBIDDEN_CODEPOINTS
    assert 0x00B5 not in FORBIDDEN_CODEPOINTS  # micro sign allowed
