"""Lensing and deflection predictions from reconstructed tau-maps (Phase 5)."""

from tdf_m33.lensing.deflection import (
    compute_convergence_proxy,
    compute_deflection_magnitude,
    compute_deflection_proxy,
    compute_tau_gradients_sky,
    deflection_summary_stats,
)
from tdf_m33.lensing.phase5a_lensing_prediction import run_phase5a_lensing_prediction

__all__ = [
    "compute_convergence_proxy",
    "compute_deflection_magnitude",
    "compute_deflection_proxy",
    "compute_tau_gradients_sky",
    "deflection_summary_stats",
    "run_phase5a_lensing_prediction",
]
