"""Validation for processed M33 radial rotation-curve tables."""

from __future__ import annotations

import pandas as pd

from tdf_m33.data.schema import (
    BARYONIC_VELOCITY_COLUMNS,
    NULLABLE_POSITIVE_COLUMNS,
    REQUIRED_COLUMNS,
)


def validate_m33_dataframe(df: pd.DataFrame) -> list[str]:
    """Return human-readable validation errors (empty list if valid)."""
    errors: list[str] = []

    missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing:
        errors.append(f"Missing required columns: {', '.join(missing)}")
        return errors

    if len(df) == 0:
        return errors

    errors.extend(_check_non_numeric_values(df))
    errors.extend(_check_positive_radius(df))
    errors.extend(_check_positive_observed_velocity(df))
    errors.extend(_check_velocity_errors(df))
    errors.extend(_check_baryonic_components(df))
    errors.extend(_check_source_ids(df))
    errors.extend(_check_galaxy_ids(df))

    return errors


def assert_valid_m33_dataframe(df: pd.DataFrame) -> None:
    """Raise ValueError if the DataFrame fails M33 processed-data validation."""
    errors = validate_m33_dataframe(df)
    if errors:
        message = "M33 processed data validation failed:\n" + "\n".join(
            f"  - {e}" for e in errors
        )
        raise ValueError(message)


def _check_non_numeric_values(df: pd.DataFrame) -> list[str]:
    errors: list[str] = []
    numeric_cols = [
        c
        for c in ("r_kpc", "v_obs_kms", "v_err_kms", *BARYONIC_VELOCITY_COLUMNS)
        if c in df.columns
    ]
    for col in numeric_cols:
        series = pd.to_numeric(df[col], errors="coerce")
        if col in NULLABLE_POSITIVE_COLUMNS:
            invalid = df[col].notna() & series.isna()
        else:
            invalid = series.isna()
        if invalid.any():
            bad = int(invalid.sum())
            errors.append(f"Column '{col}' has {bad} non-numeric or missing value(s)")
    return errors


def _check_positive_radius(df: pd.DataFrame) -> list[str]:
    r = pd.to_numeric(df["r_kpc"], errors="coerce")
    if (r <= 0).any():
        n = int((r <= 0).sum())
        return [f"Column 'r_kpc' must be positive; {n} row(s) violate this"]
    return []


def _check_positive_observed_velocity(df: pd.DataFrame) -> list[str]:
    v = pd.to_numeric(df["v_obs_kms"], errors="coerce")
    if (v <= 0).any():
        n = int((v <= 0).sum())
        return [f"Column 'v_obs_kms' must be positive; {n} row(s) violate this"]
    return []


def _check_velocity_errors(df: pd.DataFrame) -> list[str]:
    """v_err_kms may be null; when present it must be strictly positive."""
    err = pd.to_numeric(df["v_err_kms"], errors="coerce")
    present = err.notna()
    if present.any() and (err[present] <= 0).any():
        n = int((err[present] <= 0).sum())
        return [
            f"Column 'v_err_kms' must be positive when set; {n} row(s) violate this "
            "(null is allowed if documented in notes/source manifest)"
        ]
    return []


def _check_baryonic_components(df: pd.DataFrame) -> list[str]:
    errors: list[str] = []
    for col in BARYONIC_VELOCITY_COLUMNS:
        v = pd.to_numeric(df[col], errors="coerce")
        if (v < 0).any():
            n = int((v < 0).sum())
            errors.append(
                f"Column '{col}' must be nonnegative (zero allowed); {n} row(s) negative"
            )
    return errors


def _check_source_ids(df: pd.DataFrame) -> list[str]:
    sid = df["source_id"]
    empty = sid.isna() | (sid.astype(str).str.strip() == "")
    if empty.any():
        n = int(empty.sum())
        return [f"Column 'source_id' must be non-empty; {n} row(s) missing or blank"]
    return []


def _check_galaxy_ids(df: pd.DataFrame) -> list[str]:
    gid = df["galaxy_id"]
    empty = gid.isna() | (gid.astype(str).str.strip() == "")
    if empty.any():
        n = int(empty.sum())
        return [f"Column 'galaxy_id' must be non-empty; {n} row(s) missing or blank"]
    return []
