"""Tests for Phase 6F primary data validation tooling."""

from __future__ import annotations

import csv
import importlib.util
from pathlib import Path

import pytest

from tdf_m33.maps.primary_data import (
    PRIMARY_CHECKSUMS,
    scan_primary_data,
    sha256_file,
    update_primary_checksums,
    write_primary_inventory_csv,
    write_primary_validation_report_md,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
VALIDATE_SCRIPT = REPO_ROOT / "scripts" / "validate_phase6f_primary_maps.py"
CHECKSUM_SCRIPT = REPO_ROOT / "scripts" / "update_phase6f_primary_checksums.py"


def test_scan_handles_missing_primary_folders_gracefully(tmp_path: Path) -> None:
    report = scan_primary_data(tmp_path, require_astropy=False)
    assert report.n_fits_files == 0
    assert report.primary_root_exists is False
    assert any(r.status == "MISSING_DIRECTORY" for r in report.records)
    assert len(report.records) == 4


def test_inventory_and_report_written(tmp_path: Path) -> None:
    report = scan_primary_data(tmp_path, require_astropy=False)
    inventory = tmp_path / "outputs/tables/phase6f/phase6f_primary_data_inventory.csv"
    md_report = tmp_path / "outputs/reports/phase6f/phase6f_primary_data_validation_report.md"
    write_primary_inventory_csv(inventory, report)
    write_primary_validation_report_md(md_report, report, tmp_path)
    assert inventory.is_file()
    assert md_report.is_file()
    with inventory.open(encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    assert len(rows) >= 4


def test_checksum_helper_checksums_fixture_file(tmp_path: Path) -> None:
    primary = tmp_path / "data/raw/phase6f/primary/corbelli2014_hi"
    primary.mkdir(parents=True)
    fixture = primary / "fixture.txt"
    payload = b"phase6f-primary-checksum-fixture"
    fixture.write_bytes(payload)
    digest = sha256_file(fixture)
    assert len(digest) == 64

    checksum_path, n_files = update_primary_checksums(tmp_path)
    assert checksum_path == tmp_path / PRIMARY_CHECKSUMS
    assert n_files == 0
    text = checksum_path.read_text(encoding="utf-8")
    assert "No primary FITS files present" in text


def test_checksum_helper_checksums_fits_fixture(tmp_path: Path) -> None:
    astropy = pytest.importorskip("astropy")
    from astropy.io import fits
    import numpy as np

    primary = tmp_path / "data/raw/phase6f/primary/corbelli2014_hi"
    primary.mkdir(parents=True)
    data = np.ones((4, 4), dtype=np.float32)
    fits_path = primary / "test_hi.fits"
    hdu = fits.PrimaryHDU(data)
    hdu.header["BUNIT"] = "solMass/pc**2"
    hdu.writeto(fits_path, overwrite=True)

    checksum_path, n_files = update_primary_checksums(tmp_path)
    assert n_files == 1
    lines = [ln for ln in checksum_path.read_text(encoding="utf-8").splitlines() if ln.strip()]
    assert len(lines) == 1
    assert "test_hi.fits" in lines[0]


def test_validate_script_runs_from_repo_root() -> None:
    spec = importlib.util.spec_from_file_location("validate_phase6f", VALIDATE_SCRIPT)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    try:
        code = module.main([])
    except ImportError:
        pytest.skip("astropy not installed")
    assert code == 0


def test_checksum_script_runs_from_repo_root() -> None:
    spec = importlib.util.spec_from_file_location("update_checksums", CHECKSUM_SCRIPT)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    assert module.main([]) == 0


def test_main_repo_primary_scan_reports_missing() -> None:
    try:
        report = scan_primary_data(REPO_ROOT, require_astropy=True)
    except ImportError:
        report = scan_primary_data(REPO_ROOT, require_astropy=False)
    assert report.n_fits_files == 0
    assert not report.complete_for_g1
    assert not report.complete_for_g2
