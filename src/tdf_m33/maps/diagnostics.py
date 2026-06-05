"""Diagnostics for Phase 6F disk-plane tau field."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from tdf_m33.maps.grid import DiskGrid
from tdf_m33.maps.tau_field import TauFieldResult


@dataclass(frozen=True)
class TauFieldDiagnostics:
    tau_min: float
    tau_max: float
    tau_median: float
    finite_fraction: float
    grad_tau_x: np.ndarray
    grad_tau_y: np.ndarray
    g_tau_x: np.ndarray
    g_tau_y: np.ndarray
    g_tau_mag: np.ndarray
    g_tau_R: np.ndarray
    azimuthal_asymmetry: float
    gradient_smoothness: float
    laplacian_roughness: float
    boundary_growth: float
    source_tau_morphology_correlation: float


def _central_gradients(field: np.ndarray, dx: float, dy: float) -> tuple[np.ndarray, np.ndarray]:
    gx = np.full_like(field, np.nan)
    gy = np.full_like(field, np.nan)
    gx[:, 1:-1] = (field[:, 2:] - field[:, :-2]) / (2.0 * dx)
    gy[1:-1, :] = (field[2:, :] - field[:-2, :]) / (2.0 * dy)
    return gx, gy


def _laplacian(field: np.ndarray, dx: float, dy: float) -> np.ndarray:
    lap = np.full_like(field, np.nan)
    lap[1:-1, 1:-1] = (
        (field[2:, 1:-1] + field[:-2, 1:-1] - 2.0 * field[1:-1, 1:-1]) / dx**2
        + (field[1:-1, 2:] + field[1:-1, :-2] - 2.0 * field[1:-1, 1:-1]) / dy**2
    )
    return lap


def compute_tau_diagnostics(
    result: TauFieldResult,
    *,
    Kg: float,
) -> TauFieldDiagnostics:
    """Compute gradient, acceleration, and morphology diagnostics."""
    grid = result.grid
    tau = result.tau
    mask = grid.mask
    dx, dy = grid.dx_kpc, grid.dy_kpc

    grad_x, grad_y = _central_gradients(tau, dx, dy)
    g_x = -Kg * grad_x
    g_y = -Kg * grad_y
    g_mag = np.sqrt(g_x**2 + g_y**2)

    cos_phi = np.cos(grid.phi_rad)
    sin_phi = np.sin(grid.phi_rad)
    g_R = g_x * cos_phi + g_y * sin_phi

    tau_m = tau[mask]
    finite = np.isfinite(tau_m)
    azimuthal_asymmetry = _azimuthal_asymmetry(tau, grid)

    lap = _laplacian(tau, dx, dy)
    lap_vals = lap[mask & np.isfinite(lap)]
    grad_vals = np.sqrt(grad_x[mask] ** 2 + grad_y[mask] ** 2)
    grad_vals = grad_vals[np.isfinite(grad_vals)]

    boundary_growth = _boundary_growth(tau, mask)
    morph_corr = _morphology_correlation(tau, result.sources.j_tau, mask)

    return TauFieldDiagnostics(
        tau_min=float(np.nanmin(tau_m)) if finite.any() else np.nan,
        tau_max=float(np.nanmax(tau_m)) if finite.any() else np.nan,
        tau_median=float(np.nanmedian(tau_m)) if finite.any() else np.nan,
        finite_fraction=float(np.mean(finite)) if mask.any() else 0.0,
        grad_tau_x=grad_x,
        grad_tau_y=grad_y,
        g_tau_x=g_x,
        g_tau_y=g_y,
        g_tau_mag=g_mag,
        g_tau_R=g_R,
        azimuthal_asymmetry=azimuthal_asymmetry,
        gradient_smoothness=float(np.nanstd(grad_vals)) if grad_vals.size else np.nan,
        laplacian_roughness=float(np.nanstd(lap_vals)) if lap_vals.size else np.nan,
        boundary_growth=boundary_growth,
        source_tau_morphology_correlation=morph_corr,
    )


def _azimuthal_asymmetry(tau: np.ndarray, grid: DiskGrid) -> float:
    """Measure m=2 azimuthal variation in annular bins."""
    mask = grid.mask & np.isfinite(tau)
    if not np.any(mask):
        return np.nan
    r = grid.R_kpc[mask]
    phi = grid.phi_rad[mask]
    t = tau[mask]
    r_bins = np.linspace(np.nanmin(r), np.nanmax(r), 8)
    amps: list[float] = []
    for i in range(len(r_bins) - 1):
        sel = (r >= r_bins[i]) & (r < r_bins[i + 1])
        if sel.sum() < 8:
            continue
        tt = t[sel]
        pp = phi[sel]
        a2 = np.abs(np.mean(tt * np.exp(2j * pp))) / (np.mean(np.abs(tt)) + 1e-12)
        amps.append(float(a2))
    return float(np.mean(amps)) if amps else np.nan


def _boundary_growth(tau: np.ndarray, mask: np.ndarray) -> float:
    """Ratio of boundary to interior |tau| median."""
    interior = mask.copy()
    interior[0, :] = False
    interior[-1, :] = False
    interior[:, 0] = False
    interior[:, -1] = False
    boundary = mask & ~interior
    if not boundary.any() or not interior.any():
        return np.nan
    b_med = float(np.nanmedian(np.abs(tau[boundary])))
    i_med = float(np.nanmedian(np.abs(tau[interior])))
    return b_med / (i_med + 1e-12)


def _morphology_correlation(tau: np.ndarray, source: np.ndarray, mask: np.ndarray) -> float:
    sel = mask & np.isfinite(tau) & np.isfinite(source)
    if sel.sum() < 10:
        return np.nan
    a = tau[sel].ravel()
    b = source[sel].ravel()
    if np.std(a) < 1e-15 or np.std(b) < 1e-15:
        return np.nan
    return float(np.corrcoef(a, b)[0, 1])


def diagnostics_to_dataframe(diag: TauFieldDiagnostics, *, marker: str | None = None) -> pd.DataFrame:
    row = {
        "tau_min": diag.tau_min,
        "tau_max": diag.tau_max,
        "tau_median": diag.tau_median,
        "finite_fraction": diag.finite_fraction,
        "azimuthal_asymmetry": diag.azimuthal_asymmetry,
        "gradient_smoothness": diag.gradient_smoothness,
        "laplacian_roughness": diag.laplacian_roughness,
        "boundary_growth": diag.boundary_growth,
        "source_tau_morphology_correlation": diag.source_tau_morphology_correlation,
    }
    if marker:
        row["marker"] = marker
    return pd.DataFrame([row])


def rotation_consistency_diagnostic(
    grid: DiskGrid,
    g_tau_R: np.ndarray,
    rotation_csv: Any,
    *,
    Kg: float,
    blocked: bool = False,
) -> tuple[pd.DataFrame, dict[str, Any]]:
    """Compare radial average g_tau_R to missing acceleration from rotation curve."""
    if blocked:
        return pd.DataFrame(), {"status": "blocked", "message": "Primary maps missing"}

    if isinstance(rotation_csv, (str, Path)):
        rotation_csv = pd.read_csv(rotation_csv)

    r_obs = rotation_csv["r_kpc"].to_numpy(dtype=float)
    v_obs = rotation_csv["v_obs_kms"].to_numpy(dtype=float)
    v_bar = rotation_csv["v_gas_kms"].to_numpy(dtype=float) + rotation_csv["v_disk_kms"].to_numpy(
        dtype=float
    )
    v_err = rotation_csv.get("v_err_kms", pd.Series(np.ones_like(v_obs))).to_numpy(dtype=float)

    # Missing acceleration proxy: Delta v^2 / r in km^2/s^2/kpc (diagnostic units)
    delta_v2 = v_obs**2 - v_bar**2
    g_missing = delta_v2 / np.maximum(r_obs, 1e-6)

    # Bin g_tau_R on grid
    r_bins = np.linspace(0.5, grid.extent_kpc * 0.95, 20)
    rows: list[dict[str, Any]] = []
    for i in range(len(r_bins) - 1):
        sel = (
            grid.mask
            & (grid.R_kpc >= r_bins[i])
            & (grid.R_kpc < r_bins[i + 1])
            & np.isfinite(g_tau_R)
        )
        if not np.any(sel):
            continue
        r_mid = 0.5 * (r_bins[i] + r_bins[i + 1])
        g_bin = float(np.nanmean(g_tau_R[sel]))
        g_interp = float(np.interp(r_mid, r_obs, g_missing))
        rows.append(
            {
                "r_kpc": r_mid,
                "g_tau_R_mean": g_bin,
                "g_missing_proxy": g_interp,
                "n_pixels": int(sel.sum()),
            }
        )

    df = pd.DataFrame(rows)
    summary: dict[str, Any] = {"status": "ok", "Kg": Kg}
    if len(df) > 1:
        diff = df["g_tau_R_mean"] - df["g_missing_proxy"]
        summary["rmse"] = float(np.sqrt(np.mean(diff**2)))
        summary["chi2_reduced"] = float(np.sum((diff / (df["g_missing_proxy"].abs() + 1e-6)) ** 2) / len(df))
    return df, summary
