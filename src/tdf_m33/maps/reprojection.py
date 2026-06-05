"""Primary-map WCS-to-disk-plane reprojection status (Phase 6F)."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np

PLACEHOLDER_NOT_SCIENTIFIC_WCS_REPROJECTION = (
    "PLACEHOLDER_NOT_SCIENTIFIC_WCS_REPROJECTION"
)

_NOT_IMPLEMENTED_MSG = (
    "Validated WCS-to-disk-plane reprojection is not implemented yet; "
    "G8 must remain FAIL."
)

# Set True only after a validated WCS alignment path is implemented and tested.
VALIDATED_WCS_REPROJECTION_AVAILABLE: bool = False


def is_validated_wcs_reprojection_ready() -> bool:
    """Return True when scientific primary-map reprojection is implemented."""
    return VALIDATED_WCS_REPROJECTION_AVAILABLE


def validate_wcs_metadata(
    fits_path: Path,
    *,
    expected_center: tuple[float, float] | None = None,
) -> dict[str, Any]:
    """Validate WCS and grid metadata for a primary FITS map."""
    raise NotImplementedError(_NOT_IMPLEMENTED_MSG)


def reproject_fits_to_disk_grid(
    fits_path: Path,
    disk_x_kpc: np.ndarray,
    disk_y_kpc: np.ndarray,
    *,
    inclination_deg: float,
    position_angle_deg: float,
    distance_kpc: float,
) -> tuple[np.ndarray, dict[str, Any]]:
    """Reproject a sky-plane FITS map onto the Phase 6F disk-plane grid."""
    raise NotImplementedError(_NOT_IMPLEMENTED_MSG)


def compute_reprojection_validation_metrics(
    source_map: np.ndarray,
    reprojected_map: np.ndarray,
    *,
    radial_profile_reference: np.ndarray | None = None,
) -> dict[str, Any]:
    """Compute flux conservation and radial-profile consistency metrics."""
    raise NotImplementedError(_NOT_IMPLEMENTED_MSG)
