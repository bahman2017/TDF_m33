"""Disk-to-sky coordinate projection for τ maps (Phase 4B-A)."""

from __future__ import annotations

from typing import Any

import numpy as np

# Documented ballpark placeholders when config values are null (not from Corbelli Table 1).
DEFAULT_PLACEHOLDER_INCLINATION_DEG = 56.0
DEFAULT_PLACEHOLDER_POSITION_ANGLE_DEG = 23.0


def _as_array(x: np.ndarray | float) -> np.ndarray:
    return np.asarray(x, dtype=float)


def project_disk_to_sky_coordinates(
    x_disk: np.ndarray,
    y_disk: np.ndarray,
    inclination_deg: float,
    position_angle_deg: float,
) -> tuple[np.ndarray, np.ndarray]:
    """Project disk-plane coordinates (kpc) to sky-plane coordinates (kpc).

    Thin-disk convention (geometry preparation only):

    - Disk major axis along ``x_disk``; ``y_disk`` is in-plane minor axis.
    - ``inclination_deg`` is the angle between the line of sight and the disk normal
      (0° = face-on, 90° = edge-on). Major-axis foreshortening: ``x_disk * cos(i)``.
    - ``position_angle_deg`` rotates the projected disk onto the sky (degrees,
      counterclockwise from +x_disk toward +y_disk in the sky plane).

    This is a coordinate relabeling step; τ values are not resampled here.
    """
    i_rad = np.deg2rad(inclination_deg)
    pa_rad = np.deg2rad(position_angle_deg)
    cos_i = np.cos(i_rad)
    if abs(cos_i) < 1.0e-6:
        raise ValueError("inclination too close to 90° for deprojection stability")

    x_disk = _as_array(x_disk)
    y_disk = _as_array(y_disk)
    x_major = x_disk * cos_i
    y_minor = y_disk
    x_sky = x_major * np.cos(pa_rad) - y_minor * np.sin(pa_rad)
    y_sky = x_major * np.sin(pa_rad) + y_minor * np.cos(pa_rad)
    return x_sky, y_sky


def deproject_sky_to_disk_coordinates(
    x_sky: np.ndarray,
    y_sky: np.ndarray,
    inclination_deg: float,
    position_angle_deg: float,
) -> tuple[np.ndarray, np.ndarray]:
    """Inverse of :func:`project_disk_to_sky_coordinates` (same conventions)."""
    i_rad = np.deg2rad(inclination_deg)
    pa_rad = np.deg2rad(position_angle_deg)
    cos_i = np.cos(i_rad)
    if abs(cos_i) < 1.0e-6:
        raise ValueError("inclination too close to 90° for deprojection stability")

    x_sky = _as_array(x_sky)
    y_sky = _as_array(y_sky)
    x_major = x_sky * np.cos(pa_rad) + y_sky * np.sin(pa_rad)
    y_minor = -x_sky * np.sin(pa_rad) + y_sky * np.cos(pa_rad)
    x_disk = x_major / cos_i
    y_disk = y_minor
    return x_disk, y_disk


def resolve_projection_geometry(
    inclination_deg: float | None,
    position_angle_deg: float | None,
    *,
    allow_placeholder_geometry: bool,
    placeholder_inclination_deg: float = DEFAULT_PLACEHOLDER_INCLINATION_DEG,
    placeholder_position_angle_deg: float = DEFAULT_PLACEHOLDER_POSITION_ANGLE_DEG,
    data_inclination_deg: float | None = None,
) -> tuple[float, float, bool, str]:
    """Return (i, PA, placeholder_flag, geometry_source_note)."""
    if inclination_deg is not None and position_angle_deg is not None:
        return (
            float(inclination_deg),
            float(position_angle_deg),
            False,
            "config_explicit",
        )

    if inclination_deg is None and data_inclination_deg is not None:
        inclination_deg = data_inclination_deg

    if inclination_deg is not None and position_angle_deg is not None:
        return (
            float(inclination_deg),
            float(position_angle_deg),
            False,
            "data_or_config",
        )

    if not allow_placeholder_geometry:
        raise ValueError(
            "inclination_deg and/or position_angle_deg are null and "
            "allow_placeholder_geometry is false"
        )

    return (
        float(placeholder_inclination_deg),
        float(placeholder_position_angle_deg),
        True,
        "config_placeholder_ballpark",
    )


def project_tau_map_to_sky_plane(
    x_disk_kpc: np.ndarray,
    y_disk_kpc: np.ndarray,
    tau_map: np.ndarray,
    inclination_deg: float,
    position_angle_deg: float,
    *,
    tau_gradient_map: np.ndarray | None = None,
    v_tau_map: np.ndarray | None = None,
) -> dict[str, Any]:
    """Project a disk-plane τ map to sky-plane coordinates without resampling τ.

    τ (and optional companion fields) keep the same array indices; only coordinate
    arrays are transformed. Masked/NaN τ values remain NaN.
    """
    x_sky, y_sky = project_disk_to_sky_coordinates(
        x_disk_kpc, y_disk_kpc, inclination_deg, position_angle_deg
    )
    tau_sky = np.array(tau_map, dtype=float, copy=True)
    out: dict[str, Any] = {
        "x_disk_kpc": x_disk_kpc,
        "y_disk_kpc": y_disk_kpc,
        "x_sky_kpc": x_sky,
        "y_sky_kpc": y_sky,
        "tau_sky": tau_sky,
        "inclination_deg": inclination_deg,
        "position_angle_deg": position_angle_deg,
        "masked_fraction": float(np.mean(~np.isfinite(tau_sky))),
    }
    if tau_gradient_map is not None:
        out["tau_gradient_sky"] = np.array(tau_gradient_map, dtype=float, copy=True)
    if v_tau_map is not None:
        out["v_tau_kms_sky"] = np.array(v_tau_map, dtype=float, copy=True)
    return out


def geometry_roundtrip_error_kpc(
    x_disk: np.ndarray,
    y_disk: np.ndarray,
    inclination_deg: float,
    position_angle_deg: float,
) -> np.ndarray:
    """|Δ| after disk → sky → disk round trip (finite pixels only)."""
    x_sky, y_sky = project_disk_to_sky_coordinates(
        x_disk, y_disk, inclination_deg, position_angle_deg
    )
    x_back, y_back = deproject_sky_to_disk_coordinates(
        x_sky, y_sky, inclination_deg, position_angle_deg
    )
    err = np.hypot(x_back - x_disk, y_back - y_disk)
    return err
