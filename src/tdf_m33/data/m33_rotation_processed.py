"""Build canonical processed M33 rotation curve from Corbelli 2014 D1 audit (Phase 1D-D2-B)."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from tdf_m33.data.schema import ALL_COLUMNS

GALAXY_ID = "M33"
SOURCE_ID = "corbelli_et_al_2014"
EXPECTED_ROW_COUNT = 58
DATA_QUALITY_FLAG = "derived_baryonic_velocity_pass_with_caveat"
REFERENCE = "Corbelli et al. 2014, A&A 572, A23; DOI 10.1051/0004-6361/201424033"

PROCESSED_NOTES = (
    "Observed rotation from Corbelli et al. 2014 Table 1. Baryonic velocity components "
    "derived from Table 1 surface densities using Phase 1D-D1 axisymmetric disk-gravity "
    "calculation. Fig. 12 corrected sanity check status: PASS_WITH_CAVEAT; stellar disk "
    "offset ~7-10 km/s at some spot-check radii. Fig. 12 digitization is not used as "
    "canonical data. Bulge set to zero following Corbelli et al. 2014 no-separate-bulge "
    "treatment."
)


def build_m33_rotation_processed(audit: pd.DataFrame) -> pd.DataFrame:
    """
    Map D1 baryonic audit rows to canonical processed schema.

    Does not read Fig. 12 digitized spot-check files.
    """
    required_audit = {
        "r_kpc",
        "v_obs_kms",
        "v_err_kms",
        "v_gas_kms",
        "v_disk_kms",
        "sigma_gas",
        "sigma_star",
    }
    missing = required_audit - set(audit.columns)
    if missing:
        raise ValueError(f"audit CSV missing columns: {sorted(missing)}")

    out = pd.DataFrame(
        {
            "galaxy_id": GALAXY_ID,
            "r_kpc": audit["r_kpc"].astype(float),
            "v_obs_kms": audit["v_obs_kms"].astype(float),
            "v_err_kms": audit["v_err_kms"].astype(float),
            "v_gas_kms": audit["v_gas_kms"].astype(float),
            "v_disk_kms": audit["v_disk_kms"].astype(float),
            "v_bulge_kms": 0.0,
            "source_id": SOURCE_ID,
            "data_quality_flag": DATA_QUALITY_FLAG,
            "notes": PROCESSED_NOTES,
            "sigma_gas": audit["sigma_gas"].astype(float),
            "sigma_star": audit["sigma_star"].astype(float),
            "inclination_deg": pd.NA,
            "distance_mpc": pd.NA,
            "original_radius_unit": "kpc",
            "original_velocity_unit": "km s^-1",
            "digitized_from_figure": pd.NA,
            "digitization_method": pd.NA,
            "reference": REFERENCE,
        }
    )

    # Column order matches schema template
    cols = [c for c in ALL_COLUMNS if c in out.columns]
    return out[cols]


def write_m33_rotation_processed(
    audit_path: Path,
    output_path: Path,
) -> pd.DataFrame:
    """Load audit CSV and write canonical processed M33 rotation table."""
    audit = pd.read_csv(audit_path)
    processed = build_m33_rotation_processed(audit)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    processed.to_csv(output_path, index=False)
    return processed
