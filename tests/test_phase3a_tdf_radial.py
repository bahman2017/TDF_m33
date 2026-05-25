"""Tests for Phase 3A direct TDF τ reconstruction pipeline."""

from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from tdf_m33.fitting.phase3a_tdf_radial import (
    load_phase3a_input,
    reconstruct_tdf_radial_direct,
    run_phase3a_tdf_radial,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
CONFIG = REPO_ROOT / "configs" / "m33_default.yaml"
READINESS = REPO_ROOT / "outputs" / "tables" / "phase2c_residual_readiness.csv"
PHASE2A_PROFILE = REPO_ROOT / "outputs" / "tables" / "phase2a_baryonic_only_profile.csv"


@pytest.fixture
def phase3_inputs_available() -> bool:
    return READINESS.is_file() and PHASE2A_PROFILE.is_file()


def test_phase3a_pipeline_outputs(tmp_path: Path, phase3_inputs_available: bool) -> None:
    if not phase3_inputs_available:
        pytest.skip("Phase 2C readiness / Phase 2A profile missing")

    profile, diag = run_phase3a_tdf_radial(
        READINESS,
        CONFIG,
        tmp_path / "recon.csv",
        tmp_path / "diag.csv",
        tmp_path / "grad.png",
        tmp_path / "tau.png",
        tmp_path / "check.png",
        phase2a_profile_path=PHASE2A_PROFILE,
    )

    assert len(profile) == 58
    assert (tmp_path / "recon.csv").is_file()
    assert (tmp_path / "diag.csv").is_file()
    for p in ("grad.png", "tau.png", "check.png"):
        assert (tmp_path / p).is_file()

    cols = set(profile.columns)
    assert "tau_gradient_raw" in cols
    assert "v_tdf_direct_kms" in cols
    assert "nfw" not in "".join(cols).lower()
    assert "burkert" not in "".join(cols).lower()
    assert "tau" in cols or "tau_raw" in cols

    err = profile["reconstruction_error_kms"].to_numpy()
    assert np.max(np.abs(err)) < 1e-9

    v2_rec = profile["v_tau_squared_reconstructed"].to_numpy()
    dv2 = profile["delta_v2_kms2"].to_numpy()
    np.testing.assert_allclose(v2_rec, dv2, rtol=0, atol=1e-9)

    d = diag.iloc[0]
    assert not bool(d["is_fitted_model_comparison"])
    assert not bool(d["aic_bic_meaningful"])
    assert not bool(d["uses_nfw_burkert_residual"])
    assert "identity" in str(d["notes"]).lower()


def test_no_halo_residual_columns(phase3_inputs_available: bool) -> None:
    if not phase3_inputs_available:
        pytest.skip("inputs missing")

    inp = load_phase3a_input(READINESS, None, PHASE2A_PROFILE)
    out = reconstruct_tdf_radial_direct(inp, k_tau=1.0)
    forbidden = [c for c in out.columns if "nfw" in c.lower() or "burkert" in c.lower()]
    assert forbidden == []


def test_delta_v2_preserved_from_readiness(phase3_inputs_available: bool) -> None:
    if not phase3_inputs_available:
        pytest.skip("inputs missing")

    ready = pd.read_csv(READINESS)
    inp = load_phase3a_input(READINESS, None, PHASE2A_PROFILE)
    out = reconstruct_tdf_radial_direct(inp, k_tau=1.0)
    merged = out.merge(ready[["r_kpc", "delta_v2_kms2"]], on="r_kpc")
    assert merged["delta_v2_kms2_x"].equals(merged["delta_v2_kms2_y"]) or np.allclose(
        merged["delta_v2_kms2_x"],
        merged["delta_v2_kms2_y"],
    )
