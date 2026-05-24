"""Placeholder tests for core TDF algebraic identities (Phase 0).

Full model implementation is deferred to Phase 3.
"""

import numpy as np
import pytest


def v_tau_squared(r: np.ndarray, k_tau: float, d_tau_dr: np.ndarray) -> np.ndarray:
    """v_tau^2(r) = r * K_tau * d tau/dr."""
    return r * k_tau * d_tau_dr


def d_tau_dr_from_residual(
    r: np.ndarray, residual_v_squared: np.ndarray, k_tau: float
) -> np.ndarray:
    """d tau/dr = [v_obs^2 - v_bar^2] / (r * K_tau)."""
    return residual_v_squared / (r * k_tau)


class TestCoreEquationsPlaceholder:
    def test_v_tau_squared_identity(self) -> None:
        r = np.array([1.0, 2.0, 5.0])
        k_tau = 1.5
        d_tau_dr = np.array([0.1, 0.05, 0.02])
        expected = r * k_tau * d_tau_dr
        np.testing.assert_allclose(v_tau_squared(r, k_tau, d_tau_dr), expected)

    def test_d_tau_dr_from_residual_roundtrip(self) -> None:
        r = np.array([1.0, 2.0, 4.0])
        k_tau = 2.0
        v_obs_sq = np.array([100.0, 80.0, 60.0])
        v_bar_sq = np.array([40.0, 30.0, 20.0])
        residual = v_obs_sq - v_bar_sq
        gradient = d_tau_dr_from_residual(r, residual, k_tau)
        reconstructed = v_tau_squared(r, k_tau, gradient)
        np.testing.assert_allclose(reconstructed, residual)

    def test_zero_residual_gives_zero_gradient(self) -> None:
        r = np.array([3.0])
        k_tau = 1.0
        residual = np.array([0.0])
        np.testing.assert_allclose(
            d_tau_dr_from_residual(r, residual, k_tau), np.array([0.0])
        )

    def test_k_tau_zero_is_invalid_for_inversion(self) -> None:
        """K_tau = 0 is undefined; implementation must guard before Phase 3."""
        r = np.array([1.0])
        residual = np.array([1.0])
        with pytest.warns(RuntimeWarning, match="divide"):
            result = d_tau_dr_from_residual(r, residual, 0.0)
        assert np.isinf(result).all()
