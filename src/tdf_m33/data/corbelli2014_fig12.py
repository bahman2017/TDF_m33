"""Corbelli 2014 Fig. 12 baryonic sanity-check (Phase 1D-D2-A, validation only)."""

from __future__ import annotations

from pathlib import Path
from typing import Literal

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.interpolate import interp1d

SPOTCHECK_COLUMNS = (
    "source_id",
    "figure_id",
    "r_kpc",
    "v_gas_digitized_kms",
    "v_disk_digitized_kms",
    "digitization_method",
    "digitization_uncertainty_kms",
    "notes",
)

COMPARISON_COLUMNS = (
    "source_id",
    "figure_id",
    "r_kpc",
    "v_gas_digitized_kms",
    "v_disk_digitized_kms",
    "v_gas_derived_kms",
    "v_disk_derived_kms",
    "residual_gas_kms",
    "residual_disk_kms",
    "digitization_uncertainty_kms",
    "gas_within_tolerance",
    "disk_within_tolerance",
    "validation_status",
    "validation_notes",
)

# Acceptance thresholds (km/s) — documented in docs/baryonic_velocity_derivation_plan.md
TOLERANCE_KMS = 8.0
REVIEW_THRESHOLD_KMS = 10.0

ValidationStatus = Literal["PASS", "PASS_WITH_CAVEAT", "REVIEW_REQUIRED"]


def load_fig12_spotcheck(path: Path) -> pd.DataFrame:
    """Load manual Fig. 12 spot-check CSV."""
    df = pd.read_csv(path)
    missing = [c for c in SPOTCHECK_COLUMNS if c not in df.columns]
    if missing:
        raise ValueError(f"spot-check CSV missing columns: {missing}")
    if df.empty:
        raise ValueError("spot-check CSV is empty")
    return df


def _interpolate_audit(
    audit: pd.DataFrame, radii: np.ndarray
) -> tuple[np.ndarray, np.ndarray]:
    r = audit["r_kpc"].to_numpy(dtype=float)
    order = np.argsort(r)
    r, v_gas, v_disk = r[order], audit["v_gas_kms"].to_numpy()[order], audit[
        "v_disk_kms"
    ].to_numpy()[order]
    fg = interp1d(r, v_gas, kind="linear", bounds_error=False, fill_value=np.nan)
    fd = interp1d(r, v_disk, kind="linear", bounds_error=False, fill_value=np.nan)
    return fg(radii), fd(radii)


def compare_baryonic_to_fig12(
    audit: pd.DataFrame,
    spotcheck: pd.DataFrame,
) -> tuple[pd.DataFrame, ValidationStatus, str]:
    """
    Compare D1 derived v_gas / v_disk to digitized Fig. 12 spot points.

    Residuals: derived - digitized (km/s).
    """
    radii = spotcheck["r_kpc"].to_numpy(dtype=float)
    v_gas_d, v_disk_d = _interpolate_audit(audit, radii)

    unc = spotcheck["digitization_uncertainty_kms"].to_numpy(dtype=float)
    tol = np.maximum(unc, TOLERANCE_KMS)

    res_gas = v_gas_d - spotcheck["v_gas_digitized_kms"].to_numpy(dtype=float)
    res_disk = v_disk_d - spotcheck["v_disk_digitized_kms"].to_numpy(dtype=float)

    gas_ok = np.abs(res_gas) <= tol
    disk_ok = np.abs(res_disk) <= tol

    n = len(radii)
    n_gas_ok = int(gas_ok.sum())
    n_disk_ok = int(disk_ok.sum())
    med_gas = float(np.nanmedian(np.abs(res_gas)))
    med_disk = float(np.nanmedian(np.abs(res_disk)))
    max_gas = float(np.nanmax(np.abs(res_gas)))
    max_disk = float(np.nanmax(np.abs(res_disk)))

    mostly_ok = n_gas_ok >= n - 1 and n_disk_ok >= n - 1
    systematic = (
        med_gas > REVIEW_THRESHOLD_KMS
        or med_disk > REVIEW_THRESHOLD_KMS
        or max_gas > REVIEW_THRESHOLD_KMS + 5
        or max_disk > REVIEW_THRESHOLD_KMS + 5
    )

    if mostly_ok and not systematic:
        status: ValidationStatus = "PASS"
        notes = (
            "Derived D1 baryonic velocities agree with Fig. 12 spot-check within "
            f"±{TOLERANCE_KMS:.0f} km/s (or digitization uncertainty). "
            "Caveat: Fig. 12 is visual digitization; D1 remains primary."
        )
    elif mostly_ok or (n_gas_ok >= n - 1 and med_gas <= TOLERANCE_KMS and med_disk <= 12):
        status = "PASS_WITH_CAVEAT"
        notes = (
            f"Mostly within tolerance (gas {n_gas_ok}/{n}, disk {n_disk_ok}/{n}); "
            f"median |Δv_gas|={med_gas:.1f}, |Δv_disk|={med_disk:.1f} km/s. "
            "Fig. 12 is low-precision sanity check; D1 ≠ Casertano (1983). "
            "See label audit if corrected spot-check used."
        )
    else:
        status = "REVIEW_REQUIRED"
        notes = (
            f"Systematic offset vs Fig. 12: median |Δv_gas|={med_gas:.1f} km/s, "
            f"|Δv_disk|={med_disk:.1f} km/s; "
            f"{n - n_gas_ok}/{n} gas and {n - n_disk_ok}/{n} disk points exceed "
            f"{TOLERANCE_KMS:.0f} km/s tolerance. "
            "Do not tune D1 silently; document before m33_rotation.csv."
        )

    comparison = pd.DataFrame(
        {
            "source_id": spotcheck["source_id"],
            "figure_id": spotcheck["figure_id"],
            "r_kpc": radii,
            "v_gas_digitized_kms": spotcheck["v_gas_digitized_kms"],
            "v_disk_digitized_kms": spotcheck["v_disk_digitized_kms"],
            "v_gas_derived_kms": v_gas_d,
            "v_disk_derived_kms": v_disk_d,
            "residual_gas_kms": res_gas,
            "residual_disk_kms": res_disk,
            "digitization_uncertainty_kms": unc,
            "gas_within_tolerance": gas_ok,
            "disk_within_tolerance": disk_ok,
            "validation_status": status,
            "validation_notes": notes,
        }
    )
    return comparison, status, notes


def plot_fig12_sanity_check(
    audit: pd.DataFrame,
    spotcheck: pd.DataFrame,
    comparison: pd.DataFrame,
    out_path: Path,
) -> None:
    """Overlay D1 derived curves and Fig. 12 digitized spot points."""
    fig, axes = plt.subplots(1, 2, figsize=(10, 4), sharex=True)
    r = audit["r_kpc"].to_numpy(dtype=float)

    panels = (
        (axes[0], "v_gas_kms", "v_gas_digitized_kms", r"$v_{\mathrm{gas}}$ [km s$^{-1}$]"),
        (axes[1], "v_disk_kms", "v_disk_digitized_kms", r"$v_{\mathrm{disk}}$ [km s$^{-1}$]"),
    )
    for ax, col_der, col_dig, ylab in panels:
        ax.plot(r, audit[col_der], color="0.35", lw=1.2, label="D1 derived (audit)")
        ax.scatter(
            spotcheck["r_kpc"],
            spotcheck[col_dig],
            c="C1",
            s=55,
            zorder=3,
            label="Fig. 12 digitized (spot-check)",
        )
        ax.set_ylabel(ylab)
        ax.set_xlabel(r"$R$ [kpc]")
        ax.legend(loc="best", fontsize=8)
        ax.grid(True, alpha=0.3)

    status = comparison["validation_status"].iloc[0]
    fig.suptitle(
        f"Corbelli 2014 Fig. 12 baryonic sanity-check — {status}",
        fontsize=11,
    )
    fig.tight_layout()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, dpi=150)
    plt.close(fig)


def validate_comparison_df(df: pd.DataFrame) -> list[str]:
    """Return validation error messages for comparison table."""
    errors: list[str] = []
    missing = [c for c in COMPARISON_COLUMNS if c not in df.columns]
    if missing:
        errors.append(f"missing columns: {missing}")
        return errors
    status = df["validation_status"].unique()
    allowed = ("PASS", "PASS_WITH_CAVEAT", "REVIEW_REQUIRED")
    if len(status) != 1 or status[0] not in allowed:
        errors.append(f"invalid validation_status: {status.tolist()}")
    for col in ("residual_gas_kms", "residual_disk_kms"):
        if df[col].isna().any():
            errors.append(f"NaN in {col}")
    return errors
