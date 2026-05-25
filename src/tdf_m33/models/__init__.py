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
from tdf_m33.models.tdf_radial import (
    compute_tau_gradient,
    compute_v_tau_squared_from_gradient,
    integrate_tau_profile,
)
from tdf_m33.models.tdf_lowparam import (
    knot_interpolated_tau_gradient,
    tdf_velocity_model,
)
from tdf_m33.models.tdf_regularization import (
    gaussian_radius_smoothing,
    smooth_tau_gradient,
    smoothing_spline,
)
from tdf_m33.models.tdf_map2d import (
    compare_radial_profile_to_map_average,
    compute_azimuthal_average_from_map,
    make_disk_plane_grid,
    radial_interpolate_to_grid,
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
    "compute_tau_gradient",
    "compute_v_bar",
    "compute_v_tau_squared_from_gradient",
    "gaussian_radius_smoothing",
    "integrate_tau_profile",
    "knot_interpolated_tau_gradient",
    "nfw_density",
    "tdf_velocity_model",
    "smooth_tau_gradient",
    "smoothing_spline",
    "compare_radial_profile_to_map_average",
    "compute_azimuthal_average_from_map",
    "make_disk_plane_grid",
    "radial_interpolate_to_grid",
    "nfw_mass_enclosed",
    "nfw_velocity",
]
