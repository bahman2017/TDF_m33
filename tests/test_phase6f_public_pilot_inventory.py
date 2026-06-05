"""Tests for Phase 6F public pilot inventory and checksums."""

from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

from tdf_m33.maps.public_pilot_inventory import (
    PUBLIC_PILOT_CLAIM_LABEL,
    inspect_fits_file,
    is_public_pilot_fits_file,
    public_pilot_fits_extension,
    scan_public_pilot_inventory,
    sha256_file,
    update_public_pilot_checksums,
    write_public_pilot_file_inventory_csv,
)
from tdf_m33.maps.public_pilot_gates import run_public_pilot_gates
from tdf_m33.maps.gates import run_data_gates

REPO_ROOT = Path(__file__).resolve().parents[1]
INVENTORY_SCRIPT = REPO_ROOT / "scripts/inventory_phase6f_public_pilot_data.py"


def test_empty_public_pilot_folders_pending_download() -> None:
    report = scan_public_pilot_inventory(REPO_ROOT)
    assert report.claim_label == PUBLIC_PILOT_CLAIM_LABEL
    assert report.total_staged_files == 0
    assert all(r.status in {"PENDING_DOWNLOAD", "EMPTY_FOLDER"} for r in report.rows if r.n_files == 0)


def test_staged_fixture_in_tmp_path(tmp_path: Path) -> None:
    registry_dir = tmp_path / "data/raw/phase6f/public_pilot/manifest"
    registry_dir.mkdir(parents=True)
    reg_src = REPO_ROOT / "data/raw/phase6f/public_pilot/manifest/phase6f_public_pilot_source_registry.yaml"
    (registry_dir / "phase6f_public_pilot_source_registry.yaml").write_text(
        reg_src.read_text(encoding="utf-8")
    )
    co_dir = tmp_path / "data/raw/phase6f/public_pilot/co_iram_lp006"
    co_dir.mkdir(parents=True)
    (co_dir / "co_int.fits").write_bytes(b"\x00" * 64)

    report = scan_public_pilot_inventory(tmp_path)
    co_rows = [r for r in report.rows if r.source_id.startswith("iram_lp006")]
    assert any(r.status == "STAGED" and r.n_files >= 1 for r in co_rows)


def test_checksum_empty_state(tmp_path: Path) -> None:
    registry_dir = tmp_path / "data/raw/phase6f/public_pilot/manifest"
    registry_dir.mkdir(parents=True)
    reg_src = REPO_ROOT / "data/raw/phase6f/public_pilot/manifest/phase6f_public_pilot_source_registry.yaml"
    (registry_dir / "phase6f_public_pilot_source_registry.yaml").write_text(
        reg_src.read_text(encoding="utf-8")
    )
    path, n = update_public_pilot_checksums(tmp_path)
    assert n == 0
    assert "No public pilot FITS" in path.read_text(encoding="utf-8")


def test_checksum_small_fixture(tmp_path: Path) -> None:
    astropy = pytest.importorskip("astropy")
    from astropy.io import fits
    import numpy as np

    registry_dir = tmp_path / "data/raw/phase6f/public_pilot/manifest"
    registry_dir.mkdir(parents=True)
    reg_src = REPO_ROOT / "data/raw/phase6f/public_pilot/manifest/phase6f_public_pilot_source_registry.yaml"
    (registry_dir / "phase6f_public_pilot_source_registry.yaml").write_text(
        reg_src.read_text(encoding="utf-8")
    )
    co_dir = tmp_path / "data/raw/phase6f/public_pilot/co_iram_lp006"
    co_dir.mkdir(parents=True)
    fits_path = co_dir / "test_co.fits"
    hdu = fits.PrimaryHDU(np.ones((2, 2), dtype=np.float32))
    hdu.writeto(fits_path, overwrite=True)

    path, n = update_public_pilot_checksums(tmp_path)
    assert n == 1
    assert sha256_file(fits_path) in path.read_text(encoding="utf-8")


def test_inventory_script_exits_zero() -> None:
    spec = importlib.util.spec_from_file_location("inv", INVENTORY_SCRIPT)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    assert mod.main([]) == 0


def test_inspect_fits_header_fields(tmp_path: Path) -> None:
    astropy = pytest.importorskip("astropy")
    from astropy.io import fits
    import numpy as np

    registry_dir = tmp_path / "data/raw/phase6f/public_pilot/manifest"
    registry_dir.mkdir(parents=True)
    reg_src = REPO_ROOT / "data/raw/phase6f/public_pilot/manifest/phase6f_public_pilot_source_registry.yaml"
    (registry_dir / "phase6f_public_pilot_source_registry.yaml").write_text(
        reg_src.read_text(encoding="utf-8")
    )
    co_dir = tmp_path / "data/raw/phase6f/public_pilot/co_iram_lp006"
    co_dir.mkdir(parents=True)
    fits_path = co_dir / "m33_co_int.fits"
    hdu = fits.PrimaryHDU(np.ones((4, 4), dtype=np.float32))
    hdu.header["BUNIT"] = "K km/s"
    hdu.header["CTYPE1"] = "RA---TAN"
    hdu.header["CTYPE2"] = "DEC--TAN"
    hdu.header["CDELT1"] = -0.0001
    hdu.header["CDELT2"] = 0.0001
    hdu.header["CRVAL1"] = 23.5
    hdu.header["CRVAL2"] = 30.5
    hdu.header["CRPIX1"] = 2.0
    hdu.header["CRPIX2"] = 2.0
    hdu.header["BMAJ"] = 12.0
    hdu.header["BMIN"] = 8.0
    hdu.header["BPA"] = 45.0
    hdu.writeto(fits_path, overwrite=True)

    rec = inspect_fits_file(
        fits_path,
        tmp_path,
        source_id="iram_lp006_co21_integrated",
        product_type="co21_integrated_intensity",
        target_folder="data/raw/phase6f/public_pilot/co_iram_lp006",
    )
    assert rec.bunit == "K km/s"
    assert rec.ctype1.startswith("RA")
    assert rec.bmaj_arcsec == "12.0"
    assert rec.inspect_status == "INSPECTED"
    assert rec.header_read_status == "ok"
    assert rec.compressed == "false"
    assert rec.original_extension == ".fits"


def test_public_pilot_fits_extension_case_insensitive(tmp_path: Path) -> None:
    assert public_pilot_fits_extension(Path("M33.FITS.GZ")) == ".fits.gz"
    fts_path = tmp_path / "x.FTS"
    fts_path.touch()
    assert is_public_pilot_fits_file(fts_path)


def test_compressed_fits_gz_fixture(tmp_path: Path) -> None:
    astropy = pytest.importorskip("astropy")
    from astropy.io import fits
    import gzip
    import numpy as np

    registry_dir = tmp_path / "data/raw/phase6f/public_pilot/manifest"
    registry_dir.mkdir(parents=True)
    reg_src = REPO_ROOT / "data/raw/phase6f/public_pilot/manifest/phase6f_public_pilot_source_registry.yaml"
    (registry_dir / "phase6f_public_pilot_source_registry.yaml").write_text(
        reg_src.read_text(encoding="utf-8")
    )
    co_dir = tmp_path / "data/raw/phase6f/public_pilot/co_iram_lp006"
    co_dir.mkdir(parents=True)
    gz_path = co_dir / "m33_co_int.fits.gz"
    hdu = fits.PrimaryHDU(np.ones((3, 3), dtype=np.float32))
    hdu.header["BUNIT"] = "K km/s"
    hdu.header["CTYPE1"] = "RA---TAN"
    hdu.header["CTYPE2"] = "DEC--TAN"
    hdu.header["CRVAL1"] = 23.5
    hdu.header["CRVAL2"] = 30.5
    hdu.header["CRPIX1"] = 2.0
    hdu.header["CRPIX2"] = 2.0
    with gzip.open(gz_path, "wb") as handle:
        hdu.writeto(handle)

    report = scan_public_pilot_inventory(tmp_path)
    assert report.total_staged_files == 1
    assert report.claim_label == PUBLIC_PILOT_CLAIM_LABEL
    rec = report.file_records[0]
    assert rec.compressed == "true"
    assert rec.original_extension == ".fits"
    assert rec.header_read_status == "ok"
    assert rec.extension == ".fits.gz"

    checksum_path, n = update_public_pilot_checksums(tmp_path)
    assert n == 1
    assert sha256_file(gz_path) in checksum_path.read_text(encoding="utf-8")

    csv_path = tmp_path / "file_inventory.csv"
    write_public_pilot_file_inventory_csv(csv_path, report)
    csv_text = csv_path.read_text(encoding="utf-8")
    assert "compressed" in csv_text
    assert PUBLIC_PILOT_CLAIM_LABEL in csv_text

    p_report = run_public_pilot_gates(tmp_path)
    p6 = next(g for g in p_report.gates if g.gate_id == "P6_public_reprojection_ready")
    assert p6.status == "FAIL"

    g_report = run_data_gates(tmp_path)
    g1 = next(g for g in g_report.gates if g.gate_id == "G1_primary_hi_surface_density_map")
    g2 = next(
        g for g in g_report.gates
        if g.gate_id == "G2_primary_stellar_surface_density_or_mass_map"
    )
    g8 = next(g for g in g_report.gates if g.gate_id == "G8_primary_map_reprojection_ready")
    assert g1.status == "FAIL"
    assert g2.status == "FAIL"
    assert g8.status == "FAIL"


def test_compressed_fits_gz_header_read_failed(tmp_path: Path) -> None:
    registry_dir = tmp_path / "data/raw/phase6f/public_pilot/manifest"
    registry_dir.mkdir(parents=True)
    reg_src = REPO_ROOT / "data/raw/phase6f/public_pilot/manifest/phase6f_public_pilot_source_registry.yaml"
    (registry_dir / "phase6f_public_pilot_source_registry.yaml").write_text(
        reg_src.read_text(encoding="utf-8")
    )
    co_dir = tmp_path / "data/raw/phase6f/public_pilot/co_iram_lp006"
    co_dir.mkdir(parents=True)
    gz_path = co_dir / "bad.fits.gz"
    gz_path.write_bytes(b"not a fits file")

    report = scan_public_pilot_inventory(tmp_path)
    assert report.total_staged_files == 1
    rec = report.file_records[0]
    assert rec.compressed == "true"
    assert rec.header_read_status == "failed"
