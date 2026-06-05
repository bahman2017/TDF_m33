"""Tests for Phase 6F data gates."""

from pathlib import Path

import pytest

from tdf_m33.maps.gates import (
    BLOCKED_MESSAGE,
    check_g1_primary_hi,
    gratier_does_not_satisfy_g1,
    run_data_gates,
)

REPO_ROOT = Path(__file__).resolve().parents[1]


def test_g1_fails_without_primary_hi() -> None:
    g1 = check_g1_primary_hi(REPO_ROOT)
    assert g1.status == "FAIL"


def test_gratier_does_not_satisfy_primary_gate() -> None:
    if not (REPO_ROOT / "data/raw/phase6f/reference/gratier2010_vla_hi_12sec").is_dir():
        pytest.skip("Gratier reference not present")
    assert gratier_does_not_satisfy_g1(REPO_ROOT) is True


def test_scientific_ready_false_on_main_repo() -> None:
    report = run_data_gates(REPO_ROOT)
    assert report.scientific_ready is False
    assert report.blocked_message == BLOCKED_MESSAGE


def test_g1_passes_with_primary_fits(tmp_path: Path) -> None:
    hi_dir = tmp_path / "data/raw/phase6f/primary/corbelli2014_hi"
    st_dir = tmp_path / "data/raw/phase6f/primary/corbelli2014_stellar_mass"
    hi_dir.mkdir(parents=True)
    st_dir.mkdir(parents=True)
    (hi_dir / "hi.fits").write_bytes(b"\x00" * 100)
    (st_dir / "star.fits").write_bytes(b"\x00" * 100)
    geom = tmp_path / "data/raw/phase6f/geometry"
    geom.mkdir(parents=True)
    src_geom = REPO_ROOT / "data/raw/phase6f/geometry/corbelli2014_tilted_ring_geometry_model_shape.csv"
    if src_geom.is_file():
        (geom / "corbelli2014_tilted_ring_geometry_model_shape.csv").write_text(
            src_geom.read_text()
        )
    manifest = tmp_path / "data/raw/phase6f/manifest"
    manifest.mkdir(parents=True)
    reg = REPO_ROOT / "data/raw/phase6f/manifest/phase6f_source_registry.yaml"
    if reg.is_file():
        (manifest / "phase6f_source_registry.yaml").write_text(reg.read_text())
    notes = tmp_path / "docs"
    notes.mkdir(parents=True)
    for name in ("phase6f_dataset_access_notes.md", "phase6f_data_gate_report_notes.md"):
        src = REPO_ROOT / "docs" / name
        if src.is_file():
            (notes / name).write_text(src.read_text())
    g1 = check_g1_primary_hi(tmp_path)
    assert g1.status == "PASS"
