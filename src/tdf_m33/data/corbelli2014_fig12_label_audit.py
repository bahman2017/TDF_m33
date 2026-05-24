"""Fig. 12 gas/stellar label audit (Phase 1D-D2-A2)."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
from scipy.interpolate import interp1d

LABEL_AUDIT_COLUMNS = (
    "r_kpc",
    "old_v_gas_digitized_kms",
    "old_v_disk_digitized_kms",
    "swapped_v_gas_digitized_kms",
    "swapped_v_disk_digitized_kms",
    "derived_v_gas_kms",
    "derived_v_disk_kms",
    "old_abs_residual_sum",
    "swapped_abs_residual_sum",
    "physical_consistency_note",
    "recommendation",
)

# Corbelli et al. 2014 Fig. 12 caption (PDF p. 12): red and blue show gas and stellar
# respectively → red = gas, blue = stellar (online version).
CAPTION_COLOR_GAS = "red"
CAPTION_COLOR_STELLAR = "blue"
INNER_STELLAR_DOMINANCE_R_KPC = 7.0


def _interpolate_derived(audit: pd.DataFrame, radii: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    r = audit["r_kpc"].to_numpy(dtype=float)
    order = np.argsort(r)
    r = r[order]
    v_gas = audit["v_gas_kms"].to_numpy(dtype=float)[order]
    v_disk = audit["v_disk_kms"].to_numpy(dtype=float)[order]
    fg = interp1d(r, v_gas, kind="linear", bounds_error=False, fill_value=np.nan)
    fd = interp1d(r, v_disk, kind="linear", bounds_error=False, fill_value=np.nan)
    return fg(radii), fd(radii)


def _residual_sums(
    v_gas_d: np.ndarray,
    v_disk_d: np.ndarray,
    v_gas_ref: np.ndarray,
    v_disk_ref: np.ndarray,
) -> np.ndarray:
    res_g = v_gas_d - v_gas_ref
    res_d = v_disk_d - v_disk_ref
    return np.abs(res_g) + np.abs(res_d)


def build_label_audit_table(
    spotcheck: pd.DataFrame,
    audit: pd.DataFrame,
) -> tuple[pd.DataFrame, str, str]:
    """
    Compare original vs swapped gas/disk digitization against D1 derived values.

    Returns audit table, overall label verdict, and recommendation text.
    """
    radii = spotcheck["r_kpc"].to_numpy(dtype=float)
    old_gas = spotcheck["v_gas_digitized_kms"].to_numpy(dtype=float)
    old_disk = spotcheck["v_disk_digitized_kms"].to_numpy(dtype=float)
    swapped_gas = old_disk.copy()
    swapped_disk = old_gas.copy()

    v_gas_d, v_disk_d = _interpolate_derived(audit, radii)
    old_sum = _residual_sums(v_gas_d, v_disk_d, old_gas, old_disk)
    swapped_sum = _residual_sums(v_gas_d, v_disk_d, swapped_gas, swapped_disk)

    rows: list[dict[str, object]] = []
    for i, r in enumerate(radii):
        inner = r < INNER_STELLAR_DOMINANCE_R_KPC
        old_dom = "gas>disk" if old_gas[i] > old_disk[i] else "disk>=gas"
        swap_dom = "disk>gas" if swapped_disk[i] > swapped_gas[i] else "gas>=disk"
        if inner:
            phys_old = (
                f"R={r:.0f}<7: original has {old_dom} (inconsistent with "
                "§5/§6: stars dominate potential inside 7 kpc)."
            )
            phys_swap = (
                f"R={r:.0f}<7: swapped has {swap_dom} "
                f"({'OK' if swapped_disk[i] > swapped_gas[i] else 'check'} vs paper text)."
            )
            phys = f"{phys_old} {phys_swap}"
        else:
            phys = (
                f"R={r:.0f}>=7: comparable gas/star contributions expected; "
                f"original {old_dom}, swapped {swap_dom}."
            )
        rows.append(
            {
                "r_kpc": r,
                "old_v_gas_digitized_kms": old_gas[i],
                "old_v_disk_digitized_kms": old_disk[i],
                "swapped_v_gas_digitized_kms": swapped_gas[i],
                "swapped_v_disk_digitized_kms": swapped_disk[i],
                "derived_v_gas_kms": v_gas_d[i],
                "derived_v_disk_kms": v_disk_d[i],
                "old_abs_residual_sum": old_sum[i],
                "swapped_abs_residual_sum": swapped_sum[i],
                "physical_consistency_note": phys,
                "recommendation": "",
            }
        )

    df = pd.DataFrame(rows, columns=list(LABEL_AUDIT_COLUMNS))
    old_total = float(old_sum.sum())
    swap_total = float(swapped_sum.sum())
    inner_mask = radii < INNER_STELLAR_DOMINANCE_R_KPC
    old_inner_stellar_ok = bool(np.all(old_disk[inner_mask] > old_gas[inner_mask]))
    swap_inner_stellar_ok = bool(np.all(swapped_disk[inner_mask] > swapped_gas[inner_mask]))

    if swap_total < old_total * 0.6 and swap_inner_stellar_ok:
        verdict = "LIKELY_SWAPPED"
        rec = (
            "Original spot-check likely swapped gas/stellar labels: caption assigns "
            f"{CAPTION_COLOR_GAS}=gas and {CAPTION_COLOR_STELLAR}=stellar; high inner "
            "curve is blue (stellar). Use corbelli2014_fig12_baryonic_spotcheck_corrected.csv."
        )
    elif swap_total < old_total:
        verdict = "POSSIBLY_SWAPPED"
        rec = (
            "Swapping labels reduces residuals but inner-disk physics check is mixed; "
            "prefer corrected spot-check with explicit caveat."
        )
    else:
        verdict = "NOT_SWAPPED_OR_AMBIGUOUS"
        rec = (
            "Label swap does not clearly improve agreement; treat Fig. 12 digitization "
            "as too ambiguous for calibration."
        )

    df["recommendation"] = rec
    return df, verdict, rec


def build_corrected_spotcheck(spotcheck: pd.DataFrame) -> pd.DataFrame:
    """Build corrected spot-check by swapping gas/disk columns (caption-based fix)."""
    out = spotcheck.copy()
    out["v_gas_digitized_kms"] = spotcheck["v_disk_digitized_kms"].values
    out["v_disk_digitized_kms"] = spotcheck["v_gas_digitized_kms"].values
    out["figure_id"] = "fig12_bottom_bvigi_label_corrected"
    out["digitization_method"] = (
        "visual_from_pdf_fig12_bottom_panel_bvigi_label_corrected"
    )
    out["notes"] = (
        "Phase 1D-D2-A2: gas/disk columns swapped vs D2-A file. "
        "Corbelli 2014 Fig. 12 caption: red=gas, blue=stellar (online); "
        "D2-A incorrectly assigned the higher inner blue curve to gas. "
        "Supersedes corbelli2014_fig12_baryonic_spotcheck.csv for comparisons only."
    )
    return out
