"""Baryonic, dark-matter baseline, and TDF model components (Phases 2–3)."""

from tdf_m33.models.baryonic import (
    build_baryonic_profile,
    compute_residual_acceleration,
    compute_residual_velocity_squared,
    compute_v_bar,
)
from tdf_m33.models.disk_gravity import (
    DiskGravityGrid,
    circular_velocity_kms,
    circular_velocity_curve_kms,
)

__all__ = [
    "DiskGravityGrid",
    "build_baryonic_profile",
    "circular_velocity_kms",
    "circular_velocity_curve_kms",
    "compute_residual_acceleration",
    "compute_residual_velocity_squared",
    "compute_v_bar",
]
