"""Parameter fitting and model comparison (Phase 2–3)."""

from tdf_m33.fitting.metrics import FitMetrics, baryonic_only_metrics
from tdf_m33.fitting.phase2a_baryonic import run_phase2a_baryonic_only
from tdf_m33.fitting.phase2b_halo_baselines import run_phase2b_halo_baselines
from tdf_m33.fitting.phase2c_model_audit import run_phase2c_model_audit
from tdf_m33.fitting.phase3a_tdf_radial import run_phase3a_tdf_radial
from tdf_m33.fitting.phase3b_tdf_regularized import run_phase3b_tdf_regularized
from tdf_m33.fitting.phase3c_tdf_lowparam import run_phase3c_tdf_lowparam
from tdf_m33.fitting.phase3d_tdf_sensitivity import run_phase3d_tdf_sensitivity
from tdf_m33.fitting.phase4a_tdf_2d_map import run_phase4a_tdf_2d_map
from tdf_m33.fitting.phase4b_tau_projection import run_phase4b_tau_projection

__all__ = [
    "FitMetrics",
    "baryonic_only_metrics",
    "run_phase2a_baryonic_only",
    "run_phase2b_halo_baselines",
    "run_phase2c_model_audit",
    "run_phase3a_tdf_radial",
    "run_phase3b_tdf_regularized",
    "run_phase3c_tdf_lowparam",
    "run_phase3d_tdf_sensitivity",
    "run_phase4a_tdf_2d_map",
    "run_phase4b_tau_projection",
]
