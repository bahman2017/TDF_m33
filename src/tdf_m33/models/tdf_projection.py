"""Disk-to-sky coordinate projection for τ maps (Phase 4B)."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Literal

import numpy as np
import pandas as pd

# Legacy ballpark placeholders (Phase 4B-A only; not Corbelli Table 1).
DEFAULT_PLACEHOLDER_INCLINATION_DEG = 56.0
DEFAULT_PLACEHOLDER_POSITION_ANGLE_DEG = 23.0

GeometryMode = Literal["global_approximation", "radial_tilted_ring"]


@dataclass(frozen=True)
class ProjectionGeometry:
    """Resolved disk-to-sky projection geometry."""

    geometry_mode: GeometryMode
    geometry_source: str
    geometry_reference: str
    placeholder_geometry_flag: bool
    geometry_resolution: str
    inclination_deg: float | None
    position_angle_deg: float | None
    r_ring_kpc: np.ndarray | None
    inclination_ring_deg: np.ndarray | None
    position_angle_ring_deg: np.ndarray | None
    tilted_ring_method: str | None = None

    @property
    def is_radial(self) -> bool:
        return self.geometry_mode == "radial_tilted_ring"


def _as_array(x: np.ndarray | float) -> np.ndarray:
    return np.asarray(x, dtype=float)


def load_tilted_ring_geometry_table(path: Path) -> pd.DataFrame:
    """Load Corbelli et al. 2014 tilted-ring i(R), PA(R) table."""
    if not path.is_file():
        raise FileNotFoundError(f"tilted-ring geometry table missing: {path}")
    df = pd.read_csv(path)
    required = {"r_kpc", "inclination_deg", "position_angle_deg"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"{path} missing columns: {sorted(missing)}")
    return df.sort_values("r_kpc").reset_index(drop=True)


def interpolate_ring_geometry(
    r_eval_kpc: np.ndarray,
    r_ring_kpc: np.ndarray,
    values_ring: np.ndarray,
) -> np.ndarray:
    """Linear interpolation of ring geometry; outside range → NaN."""
    r_ring = np.asarray(r_ring_kpc, dtype=float)
    values = np.asarray(values_ring, dtype=float)
    r_eval = np.asarray(r_eval_kpc, dtype=float)
    if r_ring.size < 2:
        raise ValueError("tilted-ring table requires at least two radii")
    order = np.argsort(r_ring)
    r_sorted = r_ring[order]
    v_sorted = values[order]
    out = np.interp(r_eval, r_sorted, v_sorted, left=np.nan, right=np.nan)
    outside = (r_eval < r_sorted[0]) | (r_eval > r_sorted[-1])
    out = out.astype(float, copy=False)
    out[outside] = np.nan
    return out


def project_disk_to_sky_coordinates(
    x_disk: np.ndarray,
    y_disk: np.ndarray,
    inclination_deg: float | np.ndarray,
    position_angle_deg: float | np.ndarray,
) -> tuple[np.ndarray, np.ndarray]:
    """Project disk-plane coordinates (kpc) to sky-plane coordinates (kpc).

    Thin-disk convention (geometry preparation only):

    - Disk major axis along ``x_disk``; ``y_disk`` is in-plane minor axis.
    - ``inclination_deg`` is the angle between the line of sight and the disk normal
      (0° = face-on, 90° = edge-on). Major-axis foreshortening: ``x_disk * cos(i)``.
    - ``position_angle_deg`` rotates the projected disk onto the sky (degrees,
      counterclockwise from +x_disk toward +y_disk in the sky plane).

    Scalar or per-pixel ``inclination_deg`` / ``position_angle_deg`` are supported
    (radial tilted-ring geometry uses per-pixel values).
    """
    x_disk = _as_array(x_disk)
    y_disk = _as_array(y_disk)
    i_deg = np.broadcast_to(_as_array(inclination_deg), x_disk.shape).astype(float)
    pa_deg = np.broadcast_to(_as_array(position_angle_deg), x_disk.shape).astype(float)

    i_rad = np.deg2rad(i_deg)
    pa_rad = np.deg2rad(pa_deg)
    cos_i = np.cos(i_rad)
    if np.any(np.abs(cos_i) < 1.0e-6):
        raise ValueError("inclination too close to 90° for deprojection stability")

    x_major = x_disk * cos_i
    y_minor = y_disk
    x_sky = x_major * np.cos(pa_rad) - y_minor * np.sin(pa_rad)
    y_sky = x_major * np.sin(pa_rad) + y_minor * np.cos(pa_rad)
    return x_sky, y_sky


def deproject_sky_to_disk_coordinates(
    x_sky: np.ndarray,
    y_sky: np.ndarray,
    inclination_deg: float | np.ndarray,
    position_angle_deg: float | np.ndarray,
) -> tuple[np.ndarray, np.ndarray]:
    """Inverse of :func:`project_disk_to_sky_coordinates` (same conventions)."""
    x_sky = _as_array(x_sky)
    y_sky = _as_array(y_sky)
    i_deg = np.broadcast_to(_as_array(inclination_deg), x_sky.shape).astype(float)
    pa_deg = np.broadcast_to(_as_array(position_angle_deg), x_sky.shape).astype(float)

    i_rad = np.deg2rad(i_deg)
    pa_rad = np.deg2rad(pa_deg)
    cos_i = np.cos(i_rad)
    if np.any(np.abs(cos_i) < 1.0e-6):
        raise ValueError("inclination too close to 90° for deprojection stability")

    x_major = x_sky * np.cos(pa_rad) + y_sky * np.sin(pa_rad)
    y_minor = -x_sky * np.sin(pa_rad) + y_sky * np.cos(pa_rad)
    x_disk = x_major / cos_i
    y_disk = y_minor
    return x_disk, y_disk


def resolve_projection_geometry(
    inclination_deg: float | None,
    position_angle_deg: float | None,
    *,
    geometry_mode: GeometryMode = "global_approximation",
    geometry_source: str = "corbelli_et_al_2014",
    geometry_reference: str = "",
    tilted_ring_table: Path | None = None,
    tilted_ring_method: str = "model_shape",
    allow_placeholder_geometry: bool = False,
    placeholder_inclination_deg: float = DEFAULT_PLACEHOLDER_INCLINATION_DEG,
    placeholder_position_angle_deg: float = DEFAULT_PLACEHOLDER_POSITION_ANGLE_DEG,
    data_inclination_deg: float | None = None,
    global_reference_inclination_deg: float | None = None,
    global_reference_position_angle_deg: float | None = None,
) -> ProjectionGeometry:
    """Resolve projection geometry from config (Phase 4B-B)."""
    ref = geometry_reference or (
        "Corbelli et al. 2014 A&A 572 A23 Sect. 4.1 Fig. 3 (tilted-ring geometry)"
    )

    if geometry_mode == "radial_tilted_ring":
        if tilted_ring_table is None:
            raise ValueError("tilted_ring_table required for radial_tilted_ring mode")
        table = load_tilted_ring_geometry_table(tilted_ring_table)
        if tilted_ring_method:
            sub = table[table.get("method", table.iloc[:, 0]) == tilted_ring_method]
            if len(sub) >= 2:
                table = sub
        return ProjectionGeometry(
            geometry_mode="radial_tilted_ring",
            geometry_source=geometry_source,
            geometry_reference=ref,
            placeholder_geometry_flag=False,
            geometry_resolution="corbelli2014_fig3_tilted_ring_table",
            inclination_deg=None,
            position_angle_deg=None,
            r_ring_kpc=table["r_kpc"].to_numpy(dtype=float),
            inclination_ring_deg=table["inclination_deg"].to_numpy(dtype=float),
            position_angle_ring_deg=table["position_angle_deg"].to_numpy(dtype=float),
            tilted_ring_method=tilted_ring_method,
        )

    if geometry_mode != "global_approximation":
        raise ValueError(f"unsupported geometry_mode: {geometry_mode!r}")

    inc = inclination_deg
    pa = position_angle_deg
    if inc is None and data_inclination_deg is not None:
        inc = data_inclination_deg

    if inc is not None and pa is not None:
        return ProjectionGeometry(
            geometry_mode="global_approximation",
            geometry_source=geometry_source,
            geometry_reference=ref,
            placeholder_geometry_flag=False,
            geometry_resolution="config_explicit_global",
            inclination_deg=float(inc),
            position_angle_deg=float(pa),
            r_ring_kpc=None,
            inclination_ring_deg=None,
            position_angle_ring_deg=None,
        )

    if (
        global_reference_inclination_deg is not None
        and global_reference_position_angle_deg is not None
    ):
        return ProjectionGeometry(
            geometry_mode="global_approximation",
            geometry_source=geometry_source,
            geometry_reference=(
                ref
                + "; inner-disk representative i/PA from Fig. 3 (global approximation)"
            ),
            placeholder_geometry_flag=False,
            geometry_resolution="corbelli2014_fig3_global_reference",
            inclination_deg=float(global_reference_inclination_deg),
            position_angle_deg=float(global_reference_position_angle_deg),
            r_ring_kpc=None,
            inclination_ring_deg=None,
            position_angle_ring_deg=None,
        )

    if not allow_placeholder_geometry:
        raise ValueError(
            "projection geometry unresolved: set inclination/PA, global_reference, "
            "or radial_tilted_ring table; placeholders disabled"
        )

    return ProjectionGeometry(
        geometry_mode="global_approximation",
        geometry_source=geometry_source,
        geometry_reference=ref + " (config placeholder ballpark)",
        placeholder_geometry_flag=True,
        geometry_resolution="config_placeholder_ballpark",
        inclination_deg=float(placeholder_inclination_deg),
        position_angle_deg=float(placeholder_position_angle_deg),
        r_ring_kpc=None,
        inclination_ring_deg=None,
        position_angle_ring_deg=None,
    )


def geometry_fields_on_disk_plane(
    x_disk: np.ndarray,
    y_disk: np.ndarray,
    geom: ProjectionGeometry,
) -> tuple[np.ndarray, np.ndarray]:
    """Return per-pixel inclination and PA arrays for a disk-plane grid."""
    if geom.is_radial:
        assert geom.r_ring_kpc is not None
        assert geom.inclination_ring_deg is not None
        assert geom.position_angle_ring_deg is not None
        r = np.sqrt(_as_array(x_disk) ** 2 + _as_array(y_disk) ** 2)
        i_map = interpolate_ring_geometry(
            r, geom.r_ring_kpc, geom.inclination_ring_deg
        )
        pa_map = interpolate_ring_geometry(
            r, geom.r_ring_kpc, geom.position_angle_ring_deg
        )
        return i_map, pa_map
    if geom.inclination_deg is None or geom.position_angle_deg is None:
        raise ValueError("global geometry missing inclination or position angle")
    return geom.inclination_deg, geom.position_angle_deg


def project_tau_map_to_sky_plane(
    x_disk_kpc: np.ndarray,
    y_disk_kpc: np.ndarray,
    tau_map: np.ndarray,
    geometry: ProjectionGeometry,
    *,
    tau_gradient_map: np.ndarray | None = None,
    v_tau_map: np.ndarray | None = None,
) -> dict[str, Any]:
    """Project a disk-plane τ map to sky-plane coordinates without resampling τ."""
    i_field, pa_field = geometry_fields_on_disk_plane(
        x_disk_kpc, y_disk_kpc, geometry
    )
    x_sky, y_sky = project_disk_to_sky_coordinates(
        x_disk_kpc, y_disk_kpc, i_field, pa_field
    )
    tau_sky = np.array(tau_map, dtype=float, copy=True)
    invalid_geom = ~np.isfinite(i_field) | ~np.isfinite(pa_field)
    tau_sky[invalid_geom] = np.nan

    out: dict[str, Any] = {
        "x_disk_kpc": x_disk_kpc,
        "y_disk_kpc": y_disk_kpc,
        "x_sky_kpc": x_sky,
        "y_sky_kpc": y_sky,
        "tau_sky": tau_sky,
        "inclination_field_deg": i_field,
        "position_angle_field_deg": pa_field,
        "geometry": geometry,
        "masked_fraction": float(np.mean(~np.isfinite(tau_sky))),
    }
    if tau_gradient_map is not None:
        g = np.array(tau_gradient_map, dtype=float, copy=True)
        g[invalid_geom] = np.nan
        out["tau_gradient_sky"] = g
    if v_tau_map is not None:
        v = np.array(v_tau_map, dtype=float, copy=True)
        v[invalid_geom] = np.nan
        out["v_tau_kms_sky"] = v
    return out


def geometry_roundtrip_error_kpc(
    x_disk: np.ndarray,
    y_disk: np.ndarray,
    geometry: ProjectionGeometry,
) -> np.ndarray:
    """|Δ| after disk → sky → disk round trip (finite pixels only)."""
    i_field, pa_field = geometry_fields_on_disk_plane(x_disk, y_disk, geometry)
    x_sky, y_sky = project_disk_to_sky_coordinates(
        x_disk, y_disk, i_field, pa_field
    )
    x_back, y_back = deproject_sky_to_disk_coordinates(
        x_sky, y_sky, i_field, pa_field
    )
    return np.hypot(x_back - x_disk, y_back - y_disk)
