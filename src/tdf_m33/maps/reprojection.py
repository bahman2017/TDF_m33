"""Primary-map WCS-to-disk-plane reprojection status (Phase 6F)."""

from __future__ import annotations

PLACEHOLDER_NOT_SCIENTIFIC_WCS_REPROJECTION = (
    "PLACEHOLDER_NOT_SCIENTIFIC_WCS_REPROJECTION"
)

# Set True only after a validated WCS alignment path is implemented and tested.
VALIDATED_WCS_REPROJECTION_AVAILABLE: bool = False


def is_validated_wcs_reprojection_ready() -> bool:
    """Return True when scientific primary-map reprojection is implemented."""
    return VALIDATED_WCS_REPROJECTION_AVAILABLE
