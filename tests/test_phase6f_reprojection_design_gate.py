"""Tests for Phase 6F validated reprojection design scaffold."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pytest

from tdf_m33.maps.gates import BLOCKED_MESSAGE, run_data_gates
from tdf_m33.maps.reprojection import (
    VALIDATED_WCS_REPROJECTION_AVAILABLE,
    compute_reprojection_validation_metrics,
    reproject_fits_to_disk_grid,
    validate_wcs_metadata,
)

REPO_ROOT = Path(__file__).resolve().parents[1]


def test_validated_wcs_reprojection_flag_false() -> None:
    assert VALIDATED_WCS_REPROJECTION_AVAILABLE is False


def test_reproject_fits_to_disk_grid_raises_not_implemented() -> None:
    with pytest.raises(NotImplementedError, match="G8 must remain FAIL"):
        reproject_fits_to_disk_grid(
            REPO_ROOT / "dummy.fits",
            np.array([0.0]),
            np.array([0.0]),
            inclination_deg=54.0,
            position_angle_deg=22.0,
            distance_kpc=840.0,
        )


def test_validate_wcs_metadata_raises_not_implemented() -> None:
    with pytest.raises(NotImplementedError, match="G8 must remain FAIL"):
        validate_wcs_metadata(REPO_ROOT / "dummy.fits")


def test_compute_reprojection_validation_metrics_raises_not_implemented() -> None:
    with pytest.raises(NotImplementedError, match="G8 must remain FAIL"):
        compute_reprojection_validation_metrics(
            np.ones((2, 2)),
            np.ones((2, 2)),
        )


def test_g8_remains_fail_on_main_repo() -> None:
    report = run_data_gates(REPO_ROOT)
    g8 = next(g for g in report.gates if g.gate_id == "G8_primary_map_reprojection_ready")
    assert g8.status == "FAIL"


def test_scientific_ready_remains_false() -> None:
    report = run_data_gates(REPO_ROOT)
    assert report.scientific_ready is False
    assert report.blocked_message == BLOCKED_MESSAGE
