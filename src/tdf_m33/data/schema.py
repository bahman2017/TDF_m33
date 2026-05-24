"""Canonical schema for processed M33 radial rotation-curve tables."""

from dataclasses import dataclass

# Required columns in every processed M33 CSV (see docs/data_sources.md)
REQUIRED_COLUMNS: tuple[str, ...] = (
    "galaxy_id",
    "r_kpc",
    "v_obs_kms",
    "v_err_kms",
    "v_gas_kms",
    "v_disk_kms",
    "v_bulge_kms",
    "source_id",
    "data_quality_flag",
    "notes",
)

OPTIONAL_COLUMNS: tuple[str, ...] = (
    "sigma_gas",
    "sigma_star",
    "inclination_deg",
    "distance_mpc",
    "original_radius_unit",
    "original_velocity_unit",
    "digitized_from_figure",
    "digitization_method",
    "reference",
)

# Columns validated as numeric when present (required or optional)
NUMERIC_COLUMNS: tuple[str, ...] = (
    "r_kpc",
    "v_obs_kms",
    "v_err_kms",
    "v_gas_kms",
    "v_disk_kms",
    "v_bulge_kms",
    "sigma_gas",
    "sigma_star",
    "inclination_deg",
    "distance_mpc",
)

# Baryonic velocity components: may be zero, must not be negative
BARYONIC_VELOCITY_COLUMNS: tuple[str, ...] = (
    "v_gas_kms",
    "v_disk_kms",
    "v_bulge_kms",
)

# v_err_kms may be null if documented; see validation.NULLABLE_POSITIVE_COLUMNS
NULLABLE_POSITIVE_COLUMNS: tuple[str, ...] = ("v_err_kms",)

ALL_COLUMNS: tuple[str, ...] = REQUIRED_COLUMNS + OPTIONAL_COLUMNS


@dataclass(frozen=True)
class M33DataSchema:
    """Metadata for the canonical processed M33 radial table."""

    required_columns: tuple[str, ...] = REQUIRED_COLUMNS
    optional_columns: tuple[str, ...] = OPTIONAL_COLUMNS
    numeric_columns: tuple[str, ...] = NUMERIC_COLUMNS

    @property
    def all_columns(self) -> tuple[str, ...]:
        return self.required_columns + self.optional_columns

    def column_is_required(self, name: str) -> bool:
        return name in self.required_columns

    def column_is_numeric(self, name: str) -> bool:
        return name in self.numeric_columns


DEFAULT_SCHEMA = M33DataSchema()
