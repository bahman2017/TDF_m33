"""Tests for TDF radial τ-gradient module."""

import numpy as np
import pytest

from tdf_m33.models.tdf_radial import (
    compute_tau_gradient,
    compute_v_tau_squared_from_gradient,
    integrate_tau_profile,
    validate_k_tau,
    validate_radius_grid,
)


def test_tau_gradient_formula() -> None:
    r = np.array([1.0, 2.0, 5.0])
    dv2 = np.array([100.0, 200.0, 500.0])
    k = 2.0
    grad = compute_tau_gradient(r, dv2, k)
    np.testing.assert_allclose(grad, dv2 / (r * k))


def test_v_tau_squared_reconstruction_matches_delta_v2() -> None:
    r = np.linspace(0.5, 20.0, 40)
    dv2 = 50.0 + 10.0 * r + np.sin(r)
    k = 1.0
    grad = compute_tau_gradient(r, dv2, k)
    v2 = compute_v_tau_squared_from_gradient(r, grad, k)
    np.testing.assert_allclose(v2, dv2, rtol=0, atol=1e-12)


def test_tau_integration_tau0_at_first_radius() -> None:
    r = np.array([1.0, 2.0, 4.0, 8.0])
    grad = np.ones_like(r)
    tau = integrate_tau_profile(r, grad, tau0=0.0)
    assert tau[0] == pytest.approx(0.0)
    tau5 = integrate_tau_profile(r, grad, tau0=5.0)
    assert tau5[0] == pytest.approx(5.0)


def test_k_tau_nonpositive_raises() -> None:
    with pytest.raises(ValueError, match="k_tau must be positive"):
        validate_k_tau(0.0)
    with pytest.raises(ValueError, match="k_tau must be positive"):
        validate_k_tau(-1.0)


def test_non_increasing_radius_raises() -> None:
    with pytest.raises(ValueError, match="strictly increasing"):
        validate_radius_grid(np.array([1.0, 2.0, 2.0, 3.0]))
    with pytest.raises(ValueError, match="positive"):
        validate_radius_grid(np.array([1.0, -0.1, 2.0]))
