"""Baryonic source map construction for Phase 6F."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Literal

import numpy as np

from tdf_m33.constants import CORBELLI2014_HELIUM_FACTOR
from tdf_m33.maps.gates import REFERENCE_ONLY_MARKER
from tdf_m33.maps.grid import DiskGrid
from tdf_m33.maps.io import read_fits_2d

SourceMode = Literal["scientific", "reference_proxy"]


@dataclass(frozen=True)
class BaryonicSourceMaps:
    """Disk-plane baryonic surface densities and source term J_tau."""

    sigma_hi: np.ndarray
    sigma_h2: np.ndarray
    sigma_gas: np.ndarray
    sigma_star: np.ndarray
    sigma_b: np.ndarray
    j_tau: np.ndarray
    mode: SourceMode
    marker: str | None
    metadata: dict[str, Any]


def _masked_array_like(grid: DiskGrid, fill: float = 0.0) -> np.ndarray:
    arr = np.full(grid.shape, fill, dtype=float)
    arr[~grid.mask] = np.nan
    return arr


def build_j_tau(
    sigma_gas: np.ndarray,
    sigma_star: np.ndarray,
    alpha_gas: float,
    alpha_star: float,
) -> np.ndarray:
    """J_tau = alpha_gas * Sigma_gas + alpha_star * Sigma_star."""
    return alpha_gas * sigma_gas + alpha_star * sigma_star


def build_total_gas(
    sigma_hi: np.ndarray,
    sigma_h2: np.ndarray,
    helium_factor: float = CORBELLI2014_HELIUM_FACTOR,
) -> np.ndarray:
    """Sigma_gas = helium_factor * (Sigma_HI + Sigma_H2)."""
    return helium_factor * (sigma_hi + sigma_h2)


def load_primary_source_maps(
    repo_root: Path,
    grid: DiskGrid,
    *,
    alpha_gas: float,
    alpha_star: float,
    helium_factor: float = CORBELLI2014_HELIUM_FACTOR,
    h2_path: Path | None = None,
) -> BaryonicSourceMaps:
    """Load primary Corbelli maps from data/raw/phase6f/primary/."""
    hi_dir = repo_root / "data/raw/phase6f/primary/corbelli2014_hi"
    st_dir = repo_root / "data/raw/phase6f/primary/corbelli2014_stellar_mass"
    hi_files = sorted(hi_dir.glob("*.fits"))
    st_files = sorted(st_dir.glob("*.fits"))
    if not hi_files or not st_files:
        raise FileNotFoundError("Primary Corbelli FITS maps not found")

    sigma_hi, hi_meta = _resample_primary_to_grid(read_fits_2d(hi_files[0])[0], grid)
    sigma_star, st_meta = _resample_primary_to_grid(read_fits_2d(st_files[0])[0], grid)

    sigma_h2 = np.zeros_like(sigma_hi)
    if h2_path is not None and h2_path.is_file():
        sigma_h2, _ = _resample_primary_to_grid(read_fits_2d(h2_path)[0], grid)

    sigma_gas = build_total_gas(sigma_hi, sigma_h2, helium_factor)
    sigma_b = sigma_gas + sigma_star
    j_tau = build_j_tau(sigma_gas, sigma_star, alpha_gas, alpha_star)

    return BaryonicSourceMaps(
        sigma_hi=sigma_hi,
        sigma_h2=sigma_h2,
        sigma_gas=sigma_gas,
        sigma_star=sigma_star,
        sigma_b=sigma_b,
        j_tau=j_tau,
        mode="scientific",
        marker=None,
        metadata={"hi": hi_meta, "stellar": st_meta, "hi_file": str(hi_files[0])},
    )


def _resample_primary_to_grid(
    data: np.ndarray,
    grid: DiskGrid,
) -> tuple[np.ndarray, dict[str, Any]]:
    """Nearest-neighbor resample a 2D array to the disk grid (placeholder alignment).

    Full WCS alignment deferred until primary Corbelli products include documented grids.
    """
    from scipy.ndimage import zoom

    ny, nx = grid.shape
    sy, sx = data.shape
    zy = ny / sy
    zx = nx / sx
    resampled = zoom(data, (zy, zx), order=1)
    if resampled.shape != grid.shape:
        resampled = resampled[:ny, :nx]
    out = _masked_array_like(grid, fill=np.nan)
    out[grid.mask] = resampled[grid.mask]
    return out, {"resample": "scipy.ndimage.zoom", "source_shape": data.shape}


def build_reference_proxy_maps(
    repo_root: Path,
    grid: DiskGrid,
    *,
    alpha_gas: float,
    alpha_star: float,
    helium_factor: float = CORBELLI2014_HELIUM_FACTOR,
    use_gratier_hi: bool = True,
) -> BaryonicSourceMaps:
    """Build reference-only proxy source maps for smoke tests."""
    marker = REFERENCE_ONLY_MARKER

    if use_gratier_hi:
        gratier_path = (
            repo_root
            / "data/raw/phase6f/reference/gratier2010_vla_hi_12sec/M33_HI_12sec-area.fits"
        )
        if gratier_path.is_file():
            raw, wcs = read_fits_2d(gratier_path)
            sigma_hi, _ = _resample_primary_to_grid(raw, grid)
            # Proxy conversion: proportional to T(K) — NOT physical Sigma_HI
            sigma_hi = np.where(grid.mask, np.maximum(sigma_hi, 0.0) * 1e-3, np.nan)
            hi_note = "Gratier2010_VLA_TK_proxy"
        else:
            sigma_hi = _synthetic_hi(grid)
            hi_note = "synthetic_gaussian_HI"
    else:
        sigma_hi = _synthetic_hi(grid)
        hi_note = "synthetic_gaussian_HI"

    sigma_h2 = np.zeros_like(sigma_hi)
    sigma_star = _synthetic_stellar_disk(grid)
    sigma_gas = build_total_gas(sigma_hi, sigma_h2, helium_factor)
    sigma_b = sigma_gas + sigma_star
    j_tau = build_j_tau(sigma_gas, sigma_star, alpha_gas, alpha_star)

    return BaryonicSourceMaps(
        sigma_hi=sigma_hi,
        sigma_h2=sigma_h2,
        sigma_gas=sigma_gas,
        sigma_star=sigma_star,
        sigma_b=sigma_b,
        j_tau=j_tau,
        mode="reference_proxy",
        marker=marker,
        metadata={
            "marker": marker,
            "hi_source": hi_note,
            "stellar_source": "synthetic_exponential_reference_proxy",
            "not_primary_corbelli": True,
        },
    )


def build_synthetic_fixture_maps(
    grid: DiskGrid,
    *,
    alpha_gas: float,
    alpha_star: float,
    helium_factor: float = CORBELLI2014_HELIUM_FACTOR,
) -> BaryonicSourceMaps:
    """Pure synthetic fixture for unit tests."""
    sigma_hi = _synthetic_hi(grid)
    sigma_h2 = np.zeros_like(sigma_hi)
    sigma_star = _synthetic_stellar_disk(grid)
    sigma_gas = build_total_gas(sigma_hi, sigma_h2, helium_factor)
    sigma_b = sigma_gas + sigma_star
    j_tau = build_j_tau(sigma_gas, sigma_star, alpha_gas, alpha_star)
    return BaryonicSourceMaps(
        sigma_hi=sigma_hi,
        sigma_h2=sigma_h2,
        sigma_gas=sigma_gas,
        sigma_star=sigma_star,
        sigma_b=sigma_b,
        j_tau=j_tau,
        mode="reference_proxy",
        marker=REFERENCE_ONLY_MARKER,
        metadata={"source": "synthetic_fixture"},
    )


def _synthetic_hi(grid: DiskGrid) -> np.ndarray:
    """Reference-only smooth HI proxy with mild azimuthal asymmetry."""
    r = grid.R_kpc
    base = 50.0 * np.exp(-r / 4.0)
    asym = 1.0 + 0.15 * np.cos(2.0 * grid.phi_rad)
    out = np.where(grid.mask, base * asym, np.nan)
    return out


def _synthetic_stellar_disk(grid: DiskGrid) -> np.ndarray:
    """Reference-only exponential stellar disk proxy."""
    r = grid.R_kpc
    out = np.where(grid.mask, 200.0 * np.exp(-r / 3.0), np.nan)
    return out
