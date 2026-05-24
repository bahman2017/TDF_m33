"""Parameter fitting and model comparison (Phase 2–3)."""

from tdf_m33.fitting.metrics import FitMetrics, baryonic_only_metrics
from tdf_m33.fitting.phase2a_baryonic import run_phase2a_baryonic_only
from tdf_m33.fitting.phase2b_halo_baselines import run_phase2b_halo_baselines

__all__ = [
    "FitMetrics",
    "baryonic_only_metrics",
    "run_phase2a_baryonic_only",
    "run_phase2b_halo_baselines",
]
