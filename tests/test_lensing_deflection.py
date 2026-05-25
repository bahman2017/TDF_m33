"""Unit tests for deflection-proxy utilities."""

from pathlib import Path

import numpy as np
import pytest

from tdf_m33.lensing.deflection import (
    compute_convergence_proxy,
    compute_deflection_magnitude,
    compute_deflection_proxy,
    compute_tau_gradients_sky,
    deflection_summary_stats,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
SKY_MAP = REPO_ROOT / "outputs/maps/phase4b_tau_sky_projected_map.npz"


def test_gradient_shape_matches_tau() -> None:
    x, y = np.meshgrid(np.linspace(-5, 5, 30), np.linspace(-5, 5, 25))
    tau = x**2 + y**2
    gx, gy = compute_tau_gradients_sky(tau, x, y)
    assert gx.shape == tau.shape
    assert gy.shape == tau.shape


def test_nan_mask_preserved() -> None:
    x, y = np.meshgrid(np.linspace(-2, 2, 10), np.linspace(-2, 2, 10))
    tau = np.ones_like(x)
    tau[3, 3] = np.nan
    gx, gy = compute_tau_gradients_sky(tau, x, y)
    ax, ay = compute_deflection_proxy(gx, gy, alpha_tau_scale=1.0)
    assert np.isnan(gx[3, 3])
    assert np.isnan(ax[3, 3])


def test_deflection_magnitude_finite_inside_valid_region() -> None:
    x, y = np.meshgrid(np.linspace(-10, 10, 50), np.linspace(-10, 10, 50))
    tau = np.exp(-0.01 * (x**2 + y**2))
    gx, gy = compute_tau_gradients_sky(tau, x, y)
    ax, ay = compute_deflection_proxy(gx, gy)
    mag = compute_deflection_magnitude(ax, ay)
    assert np.isfinite(mag).sum() > 1000
    assert float(np.nanmax(mag)) > 0


def test_summary_stats_units() -> None:
    mag = np.array([1.0, 2.0, np.nan])
    s = deflection_summary_stats(mag)
    assert s["units"] == "normalized_proxy"
    assert s["alpha_magnitude_median"] == 1.5


def test_convergence_on_smooth_field() -> None:
    x, y = np.meshgrid(np.linspace(-8, 8, 60), np.linspace(-8, 8, 60))
    tau = np.exp(-0.02 * (x**2 + y**2))
    gx, gy = compute_tau_gradients_sky(tau, x, y)
    ax, ay = compute_deflection_proxy(gx, gy)
    kappa, diag = compute_convergence_proxy(ax, ay, x, y)
    assert diag["convergence_computed"]
    assert np.isfinite(kappa).sum() > 100


def test_real_sky_map_if_available() -> None:
    if not SKY_MAP.is_file():
        pytest.skip("Phase 4B sky map missing")
    data = np.load(SKY_MAP)
    gx, gy = compute_tau_gradients_sky(
        data["tau_sky"], data["x_sky_kpc"], data["y_sky_kpc"]
    )
    ax, ay = compute_deflection_proxy(gx, gy)
    mag = compute_deflection_magnitude(ax, ay)
    finite = np.isfinite(mag)
    assert finite.sum() > 5000
    assert float(np.nanmax(mag[finite])) > 0
