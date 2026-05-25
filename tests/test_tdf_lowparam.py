"""Tests for low-parameter knot τ-gradient models."""

import numpy as np
import pytest

from tdf_m33.models.tdf_lowparam import (
    knot_interpolated_tau_gradient,
    knot_radii_quantile_fit_mask,
    tdf_velocity_model,
)


def test_knot_interpolation_length_and_finite() -> None:
    r = np.linspace(0.5, 20.0, 30)
    knots_r = np.array([0.5, 5.0, 12.0, 20.0])
    knots_v = np.array([100.0, 200.0, 150.0, 80.0])
    g = knot_interpolated_tau_gradient(r, knots_r, knots_v)
    assert len(g) == len(r)
    assert np.all(np.isfinite(g))


def test_velocity_reconstruction_formula() -> None:
    r = np.array([1.0, 2.0, 5.0])
    v_bar = np.array([10.0, 20.0, 30.0])
    grad = np.array([50.0, 40.0, 30.0])
    k = 1.0
    v_mod, v_tau2, neg = tdf_velocity_model(v_bar, r, grad, k)
    np.testing.assert_allclose(v_tau2, r * k * grad)
    expected = np.sqrt(v_bar**2 + v_tau2)
    np.testing.assert_allclose(v_mod, expected, rtol=0, atol=1e-12)
    assert not neg.any()


def test_knot_radii_within_fit_mask() -> None:
    r = np.linspace(0.24, 25.0, 58)
    mask = (r >= 0.4) & (r <= 23.0)
    knots = knot_radii_quantile_fit_mask(r, mask, 4, 0.4, 23.0)
    assert knots[0] >= 0.4 - 1e-9
    assert knots[-1] <= 23.0 + 1e-9
    assert len(knots) == 4


def test_negative_vtau2_flagged() -> None:
    r = np.array([1.0, 2.0])
    v_bar = np.array([10.0, 10.0])
    grad = np.array([-1.0, 50.0])
    _, _, neg = tdf_velocity_model(v_bar, r, grad, 1.0)
    assert neg[0]
    assert not neg[1]
