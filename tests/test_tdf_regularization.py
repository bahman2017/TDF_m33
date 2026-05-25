"""Tests for TDF τ-gradient regularization."""

import numpy as np
import pytest

from tdf_m33.models.tdf_radial import integrate_tau_profile, validate_k_tau
from tdf_m33.models.tdf_regularization import (
    count_tau_gradient_spikes,
    flag_negative_vtau_squared,
    gaussian_radius_smoothing,
    gradient_smoothness_metric,
    smooth_tau_gradient,
)
from tdf_m33.models.tdf_radial import compute_v_tau_squared_from_gradient


def test_gaussian_smoothing_length_and_finite() -> None:
    r = np.linspace(0.5, 25.0, 58)
    g = 1000.0 + 50.0 * np.sin(r) + np.random.default_rng(0).normal(0, 200, size=58)
    out = gaussian_radius_smoothing(r, g, sigma_kpc=1.0)
    assert len(out) == len(r)
    assert np.all(np.isfinite(out))


def test_gaussian_reduces_spikes_on_noisy_input() -> None:
    r = np.linspace(0.5, 25.0, 40)
    g = np.linspace(500, 1500, len(r))
    g[10] += 8000.0
    g[20] -= 6000.0
    raw_n, _ = count_tau_gradient_spikes(r, g)
    smooth = gaussian_radius_smoothing(r, g, sigma_kpc=1.5)
    smooth_n, _ = count_tau_gradient_spikes(r, smooth)
    assert smooth_n <= raw_n


def test_smoothed_tau_integrates_from_tau0() -> None:
    r = np.array([1.0, 2.0, 4.0, 8.0])
    g = np.array([10.0, 10.0, 10.0, 10.0])
    tau = integrate_tau_profile(r, g, tau0=0.0)
    assert tau[0] == pytest.approx(0.0)
    tau3 = integrate_tau_profile(r, g, tau0=3.0)
    assert tau3[0] == pytest.approx(3.0)


def test_v_tau_squared_smooth_formula() -> None:
    r = np.linspace(1.0, 20.0, 20)
    g = smooth_tau_gradient(r, 1000.0 / r, "gaussian_radius_smoothing", gaussian_sigma_kpc=0.5)
    k = validate_k_tau(1.0)
    v2 = compute_v_tau_squared_from_gradient(r, g, k)
    np.testing.assert_allclose(v2, r * k * g, rtol=0, atol=1e-12)


def test_negative_vtau2_flagged_not_hidden() -> None:
    v2 = np.array([100.0, -10.0, 0.0])
    flags = flag_negative_vtau_squared(v2)
    assert flags.tolist() == [False, True, False]
