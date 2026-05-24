"""Tests for M33 source file status utilities."""

import tempfile
from pathlib import Path

from tdf_m33.data.source_status import (
    build_source_status_report,
    file_exists,
    sha256_file,
    summarize_source_files,
)


def test_sha256_file_known_content() -> None:
    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        tmp.write(b"phase-1c-test")
        tmp_path = Path(tmp.name)
    try:
        digest = sha256_file(tmp_path)
        assert len(digest) == 64
        assert digest == sha256_file(tmp_path)
    finally:
        tmp_path.unlink(missing_ok=True)


def test_file_exists() -> None:
    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        path = Path(tmp.name)
    try:
        assert file_exists(path)
        assert not file_exists(path.with_name("nonexistent_file_xyz"))
    finally:
        path.unlink(missing_ok=True)


def test_summarize_source_files_empty_directories(tmp_path: Path) -> None:
    download_dir = tmp_path / "downloads"
    extracted_dir = tmp_path / "extracted"
    download_dir.mkdir()
    extracted_dir.mkdir()
    summary = summarize_source_files(download_dir, extracted_dir)
    assert summary["download_dir_exists"] is True
    assert summary["extracted_dir_exists"] is True
    assert summary["download_files"] == []
    assert summary["extracted_files"] == []


def test_build_source_status_report_includes_template_flag(tmp_path: Path) -> None:
    download_dir = tmp_path / "downloads"
    extracted_dir = tmp_path / "extracted"
    download_dir.mkdir()
    extracted_dir.mkdir()
    template = extracted_dir / "corbelli2014_table1_raw_template.csv"
    template.write_text("source_id\n", encoding="utf-8")
    report = build_source_status_report(
        download_dir,
        extracted_dir,
        corbelli2014_table1_template=template,
    )
    assert report["corbelli2014_table1_template_exists"] is True
