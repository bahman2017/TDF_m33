"""M33 disk geometry utilities for Phase 6F."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from tdf_m33.models.tdf_projection import (
    deproject_sky_to_disk_coordinates,
    interpolate_ring_geometry,
    load_tilted_ring_geometry_table,
    project_disk_to_sky_coordinates,
)


@dataclass(frozen=True)
class DiskGeometryFields:
    """Per-pixel disk geometry on a grid."""

    inclination_deg: np.ndarray
    position_angle_deg: np.ndarray
    r_ring_kpc: np.ndarray
    ring_table_path: Path


def load_tilted_ring_geometry(path: Path) -> pd.DataFrame:
    """Load Corbelli 2014 tilted-ring CSV."""
    return load_tilted_ring_geometry_table(path)


def interpolate_disk_geometry(
    R_kpc: np.ndarray,
    ring_table: pd.DataFrame,
) -> tuple[np.ndarray, np.ndarray]:
    """Interpolate inclination and PA as functions of galactocentric radius."""
    r_ring = ring_table["r_kpc"].to_numpy(dtype=float)
    i_ring = ring_table["inclination_deg"].to_numpy(dtype=float)
    pa_ring = ring_table["position_angle_deg"].to_numpy(dtype=float)
    i_deg = interpolate_ring_geometry(R_kpc, r_ring, i_ring)
    pa_deg = interpolate_ring_geometry(R_kpc, r_ring, pa_ring)
    return i_deg, pa_deg


def build_geometry_fields(
    R_kpc: np.ndarray,
    ring_table_path: Path,
) -> DiskGeometryFields:
    """Build inclination and PA fields on a disk grid."""
    table = load_tilted_ring_geometry(ring_table_path)
    i_deg, pa_deg = interpolate_disk_geometry(R_kpc, table)
    return DiskGeometryFields(
        inclination_deg=i_deg,
        position_angle_deg=pa_deg,
        r_ring_kpc=table["r_kpc"].to_numpy(dtype=float),
        ring_table_path=ring_table_path,
    )


def project_grid_disk_to_sky(
    x_disk_kpc: np.ndarray,
    y_disk_kpc: np.ndarray,
    inclination_deg: np.ndarray,
    position_angle_deg: np.ndarray,
) -> tuple[np.ndarray, np.ndarray]:
    """Project disk-plane coordinates to sky plane."""
    return project_disk_to_sky_coordinates(
        x_disk_kpc, y_disk_kpc, inclination_deg, position_angle_deg
    )


def deproject_grid_sky_to_disk(
    x_sky_kpc: np.ndarray,
    y_sky_kpc: np.ndarray,
    inclination_deg: np.ndarray,
    position_angle_deg: np.ndarray,
) -> tuple[np.ndarray, np.ndarray]:
    """Deproject sky-plane coordinates to disk plane."""
    return deproject_sky_to_disk_coordinates(
        x_sky_kpc, y_sky_kpc, inclination_deg, position_angle_deg
    )


def geometry_validation_diagnostics(
    fields: DiskGeometryFields,
    mask: np.ndarray,
) -> dict[str, Any]:
    """Summarize geometry field validity inside the active mask."""
    i = fields.inclination_deg[mask]
    pa = fields.position_angle_deg[mask]
    finite_i = np.isfinite(i)
    finite_pa = np.isfinite(pa)
    return {
        "n_masked_pixels": int(mask.sum()),
        "fraction_finite_inclination": float(np.mean(finite_i)) if mask.any() else 0.0,
        "fraction_finite_position_angle": float(np.mean(finite_pa)) if mask.any() else 0.0,
        "inclination_min_deg": float(np.nanmin(i)) if finite_i.any() else np.nan,
        "inclination_max_deg": float(np.nanmax(i)) if finite_i.any() else np.nan,
        "position_angle_min_deg": float(np.nanmin(pa)) if finite_pa.any() else np.nan,
        "position_angle_max_deg": float(np.nanmax(pa)) if finite_pa.any() else np.nan,
        "ring_table": str(fields.ring_table_path),
        "n_rings": int(fields.r_ring_kpc.size),
    }
