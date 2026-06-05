"""Tests for Phase 6F public pilot inventory and checksums."""

from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

from tdf_m33.maps.public_pilot_inventory import (
    PUBLIC_PILOT_CLAIM_LABEL,
    scan_public_pilot_inventory,
    sha256_file,
    update_public_pilot_checksums,
)

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
