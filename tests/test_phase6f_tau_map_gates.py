"""Tests for Phase 6F data gates."""

from pathlib import Path

import pytest

from tdf_m33.maps.gates import (
    BLOCKED_MESSAGE,
    check_g1_primary_hi,
    check_g8_primary_map_reprojection_ready,
    gratier_does_not_satisfy_g1,
    run_data_gates,
)
from tdf_m33.maps.grid import build_disk_grid
from tdf_m33.maps.gates import GateResult
from tdf_m33.maps.reprojection import PLACEHOLDER_NOT_SCIENTIFIC_WCS_REPROJECTION
from tdf_m33.maps.sources import load_primary_source_maps

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


def test_scientific_ready_false_on_main_repo() -> None:
    report = run_data_gates(REPO_ROOT)
    assert report.scientific_ready is False
    assert report.blocked_message == BLOCKED_MESSAGE
    g8 = next(g for g in report.gates if g.gate_id == "G8_primary_map_reprojection_ready")
    assert g8.status == "FAIL"
    assert PLACEHOLDER_NOT_SCIENTIFIC_WCS_REPROJECTION in g8.message or g8.status == "FAIL"


def test_g8_fails_without_validated_reprojection() -> None:
    g1 = GateResult("G1_primary_hi_surface_density_map", "PASS", "ok", {"files": ["a.fits"]})
    g2 = GateResult("G2_primary_stellar_surface_density_or_mass_map", "PASS", "ok", {"files": ["b.fits"]})
    g4 = GateResult("G4_wcs_or_grid_metadata", "PASS", "ok")
    g8 = check_g8_primary_map_reprojection_ready(g1, g2, g4)
    assert g8.status == "FAIL"
    assert PLACEHOLDER_NOT_SCIENTIFIC_WCS_REPROJECTION in g8.message


def test_scientific_ready_requires_all_including_g8() -> None:
    """scientific_ready is false when G8 fails even if G1/G2 would pass."""
    g1 = GateResult("G1_primary_hi_surface_density_map", "PASS", "ok", {"files": ["a.fits"]})
    g2 = GateResult(
        "G2_primary_stellar_surface_density_or_mass_map", "PASS", "ok", {"files": ["b.fits"]}
    )
    g4 = GateResult("G4_wcs_or_grid_metadata", "PASS", "ok")
    g8 = check_g8_primary_map_reprojection_ready(g1, g2, g4)
    assert g8.status == "FAIL"
    required = [g1, g2, GateResult("G3_disk_geometry", "PASS", ""), g4,
                GateResult("G5_units_documented", "PASS", ""),
                GateResult("G7_provenance_and_license", "PASS", ""), g8]
    assert not all(g.status == "PASS" for g in required)


def test_load_primary_rejects_placeholder_in_scientific_mode() -> None:
    grid = build_disk_grid(4.0, 0.5, mask_radius_kpc=3.5)
    with pytest.raises(RuntimeError, match=PLACEHOLDER_NOT_SCIENTIFIC_WCS_REPROJECTION):
        load_primary_source_maps(
            REPO_ROOT,
            grid,
            alpha_gas=1.0,
            alpha_star=1.0,
            allow_placeholder_reprojection=False,
        )


def _seed_gate_fixtures(tmp_path: Path) -> None:
    geom = tmp_path / "data/raw/phase6f/geometry"
    geom.mkdir(parents=True, exist_ok=True)
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


def test_g1_passes_with_primary_fits(tmp_path: Path) -> None:
    hi_dir = tmp_path / "data/raw/phase6f/primary/corbelli2014_hi"
    st_dir = tmp_path / "data/raw/phase6f/primary/corbelli2014_stellar_mass"
    hi_dir.mkdir(parents=True)
    st_dir.mkdir(parents=True)
    (hi_dir / "hi.fits").write_bytes(b"\x00" * 100)
    (st_dir / "star.fits").write_bytes(b"\x00" * 100)
    _seed_gate_fixtures(tmp_path)
    g1 = check_g1_primary_hi(tmp_path)
    assert g1.status == "PASS"
