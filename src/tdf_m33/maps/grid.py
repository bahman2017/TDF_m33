"""Disk-plane Cartesian grid for Phase 6F (no spherical/halo coordinates)."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class DiskGrid:
    """Disk-plane grid in kpc."""

    x_kpc: np.ndarray
    y_kpc: np.ndarray
    R_kpc: np.ndarray
    phi_rad: np.ndarray
    mask: np.ndarray
    dx_kpc: float
    dy_kpc: float
    center_x_kpc: float
    center_y_kpc: float
    extent_kpc: float

    @property
    def shape(self) -> tuple[int, int]:
        return self.R_kpc.shape

    @property
    def ny(self) -> int:
        return int(self.R_kpc.shape[0])

    @property
    def nx(self) -> int:
        return int(self.R_kpc.shape[1])


def build_disk_grid(
    extent_kpc: float,
    pixel_scale_kpc: float,
    center_x_kpc: float = 0.0,
    center_y_kpc: float = 0.0,
    mask_radius_kpc: float | None = None,
) -> DiskGrid:
    """Build a disk-plane Cartesian grid.

    Parameters
    ----------
    extent_kpc
        Half-width of the square domain in kpc (grid spans [-extent, +extent]).
    pixel_scale_kpc
        Pixel spacing in kpc.
    mask_radius_kpc
        If set, pixels with R > mask_radius_kpc are masked (False in ``mask``).
    """
    if extent_kpc <= 0 or pixel_scale_kpc <= 0:
        raise ValueError("extent_kpc and pixel_scale_kpc must be positive")

    n = int(np.round(2.0 * extent_kpc / pixel_scale_kpc)) + 1
    if n < 3:
        raise ValueError("grid too small; increase extent or decrease pixel scale")

    x_1d = np.linspace(-extent_kpc, extent_kpc, n)
    y_1d = np.linspace(-extent_kpc, extent_kpc, n)
    x_kpc, y_kpc = np.meshgrid(x_1d, y_1d, indexing="xy")
    dx = float(x_1d[1] - x_1d[0]) if n > 1 else pixel_scale_kpc
    dy = float(y_1d[1] - y_1d[0]) if n > 1 else pixel_scale_kpc

    x_shift = x_kpc - center_x_kpc
    y_shift = y_kpc - center_y_kpc
    R_kpc = np.sqrt(x_shift**2 + y_shift**2)
    phi_rad = np.arctan2(y_shift, x_shift)

    mask = np.ones(R_kpc.shape, dtype=bool)
    if mask_radius_kpc is not None:
        mask &= R_kpc <= float(mask_radius_kpc)

    return DiskGrid(
        x_kpc=x_kpc,
        y_kpc=y_kpc,
        R_kpc=R_kpc,
        phi_rad=phi_rad,
        mask=mask,
        dx_kpc=dx,
        dy_kpc=dy,
        center_x_kpc=center_x_kpc,
        center_y_kpc=center_y_kpc,
        extent_kpc=extent_kpc,
    )
