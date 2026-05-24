"""Validation for processed M33 radial rotation-curve tables."""

from __future__ import annotations

import numpy as np
import pandas as pd

from tdf_m33.data.schema import (
    BARYONIC_VELOCITY_COLUMNS,
    NULLABLE_POSITIVE_COLUMNS,
    REQUIRED_COLUMNS,
)

CORBELLI_2014_SOURCE_ID = "corbelli_et_al_2014"
CORBELLI_2014_ROW_COUNT = 58
CORBELLI_PROCESSED_QUALITY_FLAG = "derived_baryonic_velocity_pass_with_caveat"


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
    errors.extend(_check_corbelli_processed_contract(df))

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


def _check_corbelli_processed_contract(df: pd.DataFrame) -> list[str]:
    """Extra checks for Corbelli 2014 canonical processed CSV (Phase 1D-D2-B)."""
    if len(df) == 0:
        return []

    sid = df["source_id"].astype(str).str.strip()
    if not (sid == CORBELLI_2014_SOURCE_ID).all():
        return []

    errors: list[str] = []
    if len(df) != CORBELLI_2014_ROW_COUNT:
        errors.append(
            f"Corbelli 2014 processed table expected {CORBELLI_2014_ROW_COUNT} rows, "
            f"got {len(df)}"
        )

    v_bulge = pd.to_numeric(df["v_bulge_kms"], errors="coerce")
    if not np.allclose(v_bulge, 0.0, atol=0.0, rtol=0.0):
        n = int((v_bulge != 0).sum())
        errors.append(f"v_bulge_kms must be exactly 0 for all rows; {n} nonzero")

    if "sigma_gas" in df.columns and "v_gas_kms" in df.columns:
        sg = pd.to_numeric(df["sigma_gas"], errors="coerce")
        vg = pd.to_numeric(df["v_gas_kms"], errors="coerce")
        if sg.notna().any() and vg.notna().any() and np.allclose(sg, vg, rtol=1.0e-6):
            errors.append(
                "v_gas_kms must not be aliased to sigma_gas (surface density ≠ velocity)"
            )

    if "sigma_star" in df.columns and "v_disk_kms" in df.columns:
        ss = pd.to_numeric(df["sigma_star"], errors="coerce")
        vd = pd.to_numeric(df["v_disk_kms"], errors="coerce")
        if ss.notna().any() and vd.notna().any() and np.allclose(ss, vd, rtol=1.0e-6):
            errors.append(
                "v_disk_kms must not be aliased to sigma_star (surface density ≠ velocity)"
            )

    if "data_quality_flag" in df.columns:
        flags = df["data_quality_flag"].astype(str).str.strip()
        if not (flags == CORBELLI_PROCESSED_QUALITY_FLAG).all():
            errors.append(
                f"data_quality_flag must be '{CORBELLI_PROCESSED_QUALITY_FLAG}' "
                "for all Corbelli processed rows"
            )

    return errors
