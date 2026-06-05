"""Tests for Phase 6F tau field diagnostics and blocked build."""

from pathlib import Path

import numpy as np
import pytest

from tdf_m33.maps.diagnostics import compute_tau_diagnostics
from tdf_m33.maps.gates import BLOCKED_MESSAGE, REFERENCE_ONLY_MARKER
from tdf_m33.maps.grid import build_disk_grid
from tdf_m33.maps.pipeline import build_tau_map
from tdf_m33.maps.solver import solve_tau_field
from tdf_m33.maps.sources import build_synthetic_fixture_maps
from tdf_m33.maps.tau_field import TauFieldResult

REPO_ROOT = Path(__file__).resolve().parents[1]
CONFIG = REPO_ROOT / "configs" / "phase6f_nonspherical_tau_map.yaml"


def test_diagnostics_shapes_and_finite() -> None:
    grid = build_disk_grid(4.0, 0.5, mask_radius_kpc=3.5)
    sources = build_synthetic_fixture_maps(grid, alpha_gas=1.0, alpha_star=1.0)
    j = np.where(grid.mask, np.nan_to_num(sources.j_tau, nan=0.0), 0.0)
    tau, diag_s = solve_tau_field(
        j, grid.mask, grid.dx_kpc, grid.dy_kpc, kappa_tau=1.0, m_tau=0.05
    )
    result = TauFieldResult(
        tau=tau,
        grid=grid,
        sources=sources,
        solver_diagnostics=diag_s,
        mode="reference_proxy",
        marker=REFERENCE_ONLY_MARKER,
        metadata={},
    )
    diag = compute_tau_diagnostics(result, Kg=1.0)
    assert diag.grad_tau_x.shape == grid.shape
    assert diag.g_tau_mag.shape == grid.shape
    assert np.isfinite(diag.azimuthal_asymmetry)
    assert diag.finite_fraction > 0.9


def test_blocked_mode_no_scientific_map(tmp_path: Path) -> None:
    if not CONFIG.is_file():
        pytest.skip("config missing")
    cfg = CONFIG.read_text()
    local_cfg = tmp_path / "phase6f.yaml"
    local_cfg.write_text(cfg)
    report, result = build_tau_map(local_cfg, tmp_path, allow_reference_proxy=False)
    assert result is None
    assert report.scientific_ready is False
    run_report = tmp_path / "outputs/reports/phase6f/phase6f_tau_map_run_report.md"
    assert run_report.is_file()
    text = run_report.read_text()
    assert "blocked" in text.lower()
    assert "Corbelli 2014" in text


def test_reference_proxy_marks_outputs(tmp_path: Path) -> None:
    if not CONFIG.is_file():
        pytest.skip("config missing")
    geom_src = REPO_ROOT / "data/raw/phase6f/geometry/corbelli2014_tilted_ring_geometry_model_shape.csv"
    if not geom_src.is_file():
        pytest.skip("geometry missing")
    geom_dst = tmp_path / "data/raw/phase6f/geometry/corbelli2014_tilted_ring_geometry_model_shape.csv"
    geom_dst.parent.mkdir(parents=True, exist_ok=True)
    geom_dst.write_text(geom_src.read_text())
    rot = tmp_path / "data/processed/m33_rotation.csv"
    rot.parent.mkdir(parents=True, exist_ok=True)
    src_rot = REPO_ROOT / "data/processed/m33_rotation.csv"
    if src_rot.is_file():
        rot.write_text(src_rot.read_text())
    manifest = tmp_path / "data/raw/phase6f/manifest/phase6f_source_registry.yaml"
    manifest.parent.mkdir(parents=True, exist_ok=True)
    reg = REPO_ROOT / "data/raw/phase6f/manifest/phase6f_source_registry.yaml"
    manifest.write_text(reg.read_text())
    notes = tmp_path / "docs/phase6f_dataset_access_notes.md"
    notes.parent.mkdir(parents=True, exist_ok=True)
    notes.write_text("# notes")
    gate_notes = tmp_path / "docs/phase6f_data_gate_report_notes.md"
    gate_notes.write_text("# gate notes")
    cfg_text = CONFIG.read_text().replace(
        "data/processed/m33_rotation.csv",
        str(rot.relative_to(tmp_path)) if rot.is_file() else "data/processed/m33_rotation.csv",
    )
    local_cfg = tmp_path / "phase6f.yaml"
    local_cfg.write_text(cfg_text)
    report, result = build_tau_map(local_cfg, tmp_path, allow_reference_proxy=True)
    assert result is not None
    assert result.marker == REFERENCE_ONLY_MARKER
    npz = tmp_path / "outputs/maps/phase6f/phase6f_tau_map_disk_plane.npz"
    assert npz.is_file()
