"""Baryonic, dark-matter baseline, and TDF model components (Phases 2–3)."""

from tdf_m33.models.baryonic import (
    build_baryonic_profile,
    compute_residual_acceleration,
    compute_residual_velocity_squared,
    compute_v_bar,
)
from tdf_m33.models.halo import (
    burkert_density,
    burkert_mass_enclosed,
    burkert_velocity,
    combined_velocity,
    nfw_density,
    nfw_mass_enclosed,
    nfw_velocity,
)
from tdf_m33.models.disk_gravity import (
    DiskGravityGrid,
    circular_velocity_kms,
    circular_velocity_curve_kms,
)

__all__ = [
    "DiskGravityGrid",
    "burkert_density",
    "burkert_mass_enclosed",
    "burkert_velocity",
    "build_baryonic_profile",
    "combined_velocity",
    "circular_velocity_kms",
    "circular_velocity_curve_kms",
    "compute_residual_acceleration",
    "compute_residual_velocity_squared",
    "compute_v_bar",
    "nfw_density",
    "nfw_mass_enclosed",
    "nfw_velocity",
]
