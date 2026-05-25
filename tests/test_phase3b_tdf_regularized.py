"""Tests for Phase 3B-A regularized TDF pipeline."""

from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from tdf_m33.fitting.phase3b_tdf_regularized import run_phase3b_tdf_regularized

REPO_ROOT = Path(__file__).resolve().parents[1]
CONFIG = REPO_ROOT / "configs" / "m33_default.yaml"
PHASE3A = REPO_ROOT / "outputs" / "tables" / "phase3a_tau_radial_reconstruction.csv"


@pytest.fixture
def phase3a_available() -> bool:
    return PHASE3A.is_file()


def test_phase3b_pipeline_outputs(tmp_path: Path, phase3a_available: bool) -> None:
    if not phase3a_available:
        pytest.skip("Phase 3A output missing")

    profiles, diag = run_phase3b_tdf_regularized(
        PHASE3A,
        CONFIG,
        tmp_path / "profiles.csv",
        tmp_path / "diag.csv",
        tmp_path / "grad.png",
        tmp_path / "tau.png",
        tmp_path / "check.png",
        tmp_path / "tradeoff.png",
    )

    assert len(profiles) == 58 * len(diag)
    for name in (
        "profiles.csv",
        "diag.csv",
        "grad.png",
        "tau.png",
        "check.png",
        "tradeoff.png",
    ):
        assert (tmp_path / name).is_file()

    assert "tau_gradient_smooth" in profiles.columns
    assert "negative_vtau2_flag" in profiles.columns
    forbidden = [c for c in profiles.columns if "nfw" in c.lower() or "burkert" in c.lower()]
    assert forbidden == []
    assert "aic_bic_comparison_deferred" in diag.columns
    assert diag["aic_bic_comparison_deferred"].all()
    assert "aic" not in [c.lower() for c in diag.columns if c != "aic_bic_comparison_deferred"]
    assert "smoothness" in "".join(diag.columns).lower()
    assert int(diag["raw_gradient_spike_count"].iloc[0]) >= 0

    for method in diag["method"]:
        mdf = profiles[profiles["regularization_method"] == method]
        assert len(mdf) == 58


def test_smoothing_reduces_or_maintains_spikes(
    tmp_path: Path, phase3a_available: bool
) -> None:
    if not phase3a_available:
        pytest.skip("Phase 3A missing")

    _, diag = run_phase3b_tdf_regularized(
        PHASE3A,
        CONFIG,
        tmp_path / "p.csv",
        tmp_path / "d.csv",
        tmp_path / "g.png",
        tmp_path / "t.png",
        tmp_path / "c.png",
        tmp_path / "tr.png",
    )
    for _, row in diag.iterrows():
        assert int(row["smoothed_gradient_spike_count"]) <= int(
            row["raw_gradient_spike_count"]
        )
