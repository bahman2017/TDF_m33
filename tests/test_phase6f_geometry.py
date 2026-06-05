"""Tests for Phase 6F geometry utilities."""

from pathlib import Path

import numpy as np
import pytest

from tdf_m33.maps.geometry import (
    build_geometry_fields,
    interpolate_disk_geometry,
    load_tilted_ring_geometry,
)
from tdf_m33.maps.grid import build_disk_grid

REPO_ROOT = Path(__file__).resolve().parents[1]
GEOM = REPO_ROOT / "data/raw/phase6f/geometry/corbelli2014_tilted_ring_geometry_model_shape.csv"


def test_load_and_interpolate_geometry() -> None:
    if not GEOM.is_file():
        pytest.skip("geometry CSV missing")
    table = load_tilted_ring_geometry(GEOM)
    grid = build_disk_grid(5.0, 0.5, mask_radius_kpc=4.5)
    i_deg, pa_deg = interpolate_disk_geometry(grid.R_kpc, table)
    sel = grid.mask & (grid.R_kpc >= table["r_kpc"].min()) & (grid.R_kpc <= table["r_kpc"].max())
    assert np.all(np.isfinite(i_deg[sel]))
    assert np.all(np.isfinite(pa_deg[sel]))


def test_build_geometry_fields() -> None:
    if not GEOM.is_file():
        pytest.skip("geometry CSV missing")
    grid = build_disk_grid(5.0, 0.5, mask_radius_kpc=4.0)
    fields = build_geometry_fields(grid.R_kpc, GEOM)
    assert fields.inclination_deg.shape == grid.shape
