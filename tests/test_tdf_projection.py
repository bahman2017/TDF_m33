"""Unit tests for disk-to-sky τ projection geometry."""

import numpy as np
import pytest

from tdf_m33.models.tdf_projection import (
    ProjectionGeometry,
    deproject_sky_to_disk_coordinates,
    interpolate_ring_geometry,
    project_disk_to_sky_coordinates,
    project_tau_map_to_sky_plane,
    resolve_projection_geometry,
)

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
RING_TABLE = (
    REPO_ROOT / "data/raw/extracted/corbelli2014_tilted_ring_geometry_model_shape.csv"
)


def test_projection_preserves_shape() -> None:
    x = np.linspace(-5, 5, 20)
    y = np.linspace(-5, 5, 15)
    xg, yg = np.meshgrid(x, y)
    tau = np.ones_like(xg)
    geom = resolve_projection_geometry(45.0, 10.0, geometry_mode="global_approximation")
    out = project_tau_map_to_sky_plane(xg, yg, tau, geom)
    assert out["tau_sky"].shape == tau.shape
    assert out["x_sky_kpc"].shape == xg.shape


def test_masked_values_remain_masked() -> None:
    xg, yg = np.meshgrid(np.linspace(-3, 3, 10), np.linspace(-3, 3, 10))
    tau = np.ones_like(xg)
    tau[0, 0] = np.nan
    geom = resolve_projection_geometry(45.0, 0.0, geometry_mode="global_approximation")
    out = project_tau_map_to_sky_plane(xg, yg, tau, geom)
    assert np.isnan(out["tau_sky"][0, 0])
    assert np.isfinite(out["tau_sky"][5, 5])


def test_roundtrip_disk_sky_disk_global() -> None:
    from tdf_m33.models.tdf_projection import geometry_roundtrip_error_kpc

    xg, yg = np.meshgrid(np.linspace(-10, 10, 50), np.linspace(-10, 10, 50))
    geom = resolve_projection_geometry(56.0, 23.0, geometry_mode="global_approximation")
    err = geometry_roundtrip_error_kpc(xg, yg, geom)
    assert float(np.nanmax(err)) < 1e-9


def test_radial_geometry_from_corbelli_table() -> None:
    if not RING_TABLE.is_file():
        pytest.skip("Corbelli geometry table missing")
    geom = resolve_projection_geometry(
        None,
        None,
        geometry_mode="radial_tilted_ring",
        tilted_ring_table=RING_TABLE,
        allow_placeholder_geometry=False,
    )
    assert geom.is_radial
    assert geom.placeholder_geometry_flag is False
    assert len(geom.r_ring_kpc) == 12


def test_radial_interpolation_masks_outside_ring_range() -> None:
    if not RING_TABLE.is_file():
        pytest.skip("table missing")
    geom = resolve_projection_geometry(
        None,
        None,
        geometry_mode="radial_tilted_ring",
        tilted_ring_table=RING_TABLE,
        allow_placeholder_geometry=False,
    )
    vals = interpolate_ring_geometry(
        np.array([0.1, 5.0, 25.0]),
        geom.r_ring_kpc,
        geom.inclination_ring_deg,
    )
    assert np.isnan(vals[0])
    assert np.isfinite(vals[1])
    assert np.isnan(vals[2])


def test_placeholder_disallowed_raises() -> None:
    with pytest.raises(ValueError, match="placeholders disabled"):
        resolve_projection_geometry(
            None,
            None,
            allow_placeholder_geometry=False,
        )


def test_radial_roundtrip_finite_inside_rings() -> None:
    from tdf_m33.models.tdf_projection import geometry_roundtrip_error_kpc

    if not RING_TABLE.is_file():
        pytest.skip("table missing")
    geom = resolve_projection_geometry(
        None,
        None,
        geometry_mode="radial_tilted_ring",
        tilted_ring_table=RING_TABLE,
        allow_placeholder_geometry=False,
    )
    xg, yg = np.meshgrid(np.linspace(-15, 15, 40), np.linspace(-15, 15, 40))
    err = geometry_roundtrip_error_kpc(xg, yg, geom)
    r = np.sqrt(xg**2 + yg**2)
    inside = (r >= geom.r_ring_kpc.min()) & (r <= geom.r_ring_kpc.max())
    assert float(np.nanmax(err[inside])) < 1e-9
