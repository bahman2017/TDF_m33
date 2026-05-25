"""Tests for Phase 5C-B upper-bound dynamical consistency."""

from pathlib import Path

import numpy as np
import pandas as pd
import pytest
import yaml

from tdf_m33.constants import G_KPC
from tdf_m33.lensing.phase5c_upper_bound_consistency import (
    compare_tau_mass_proxy_to_upper_bound,
    compute_effective_tau_mass_proxy,
    load_lopez_fune_enclosed_mass_constraint,
    run_phase5c_upper_bound_consistency,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
CONFIG = REPO_ROOT / "configs" / "m33_default.yaml"
PARAMS_CSV = REPO_ROOT / "data/raw/extracted/lopez_fune_2017_halo_parameters_raw.csv"
PROFILE_OUT = REPO_ROOT / "outputs/tables/phase5c_tau_mass_proxy_profile.csv"
SUMMARY_OUT = REPO_ROOT / "outputs/tables/phase5c_upper_bound_consistency_summary.csv"
REPORT_OUT = REPO_ROOT / "outputs/reports/phase5c_upper_bound_consistency_report.md"
FIG_OUT = REPO_ROOT / "outputs/figures/phase5c_tau_mass_proxy_vs_lopez_fune.png"

FORBIDDEN_AFFIRMATIVE = (
    "dark matter disproven: true",
    "no need for dark matter",
    "replaces dark matter",
    "observational detection",
)


@pytest.fixture(scope="module")
def phase5c_outputs() -> tuple[pd.DataFrame, pd.DataFrame]:
    profile_df, summary_df, _ = run_phase5c_upper_bound_consistency(
        CONFIG,
        PROFILE_OUT,
        SUMMARY_OUT,
        REPORT_OUT,
        FIG_OUT,
    )
    return profile_df, summary_df


def test_mass_proxy_formula() -> None:
    r = np.array([10.0, 23.0])
    v2 = np.array([100.0, 144.0])
    m = compute_effective_tau_mass_proxy(r, v2)
    expected = r * v2 / G_KPC
    np.testing.assert_allclose(m, expected)


def test_lopez_constraint_loads() -> None:
    lopez = load_lopez_fune_enclosed_mass_constraint(PARAMS_CSV)
    assert lopez["M_lopez_enclosed_msun"] == pytest.approx(6.7e10, rel=1e-3)
    assert lopez["M_lopez_uncertainty_msun"] == pytest.approx(1.2e10, rel=1e-3)


def test_compare_pass_within_envelope() -> None:
    comp = compare_tau_mass_proxy_to_upper_bound(6.5e10, 6.7e10, 1.2e10)
    assert comp["consistency_status"] == "PASS_WITH_CAVEAT"


def test_compare_review_above_envelope() -> None:
    comp = compare_tau_mass_proxy_to_upper_bound(9.0e10, 6.7e10, 1.2e10)
    assert comp["consistency_status"] == "REVIEW_REQUIRED"


def test_outputs_created(phase5c_outputs: tuple[pd.DataFrame, pd.DataFrame]) -> None:
    assert PROFILE_OUT.is_file()
    assert SUMMARY_OUT.is_file()
    assert REPORT_OUT.is_file()
    assert FIG_OUT.is_file()
    profile_df, summary_df = phase5c_outputs
    assert len(profile_df) >= 50
    assert len(summary_df) == 1


def test_summary_flags(phase5c_outputs: tuple[pd.DataFrame, pd.DataFrame]) -> None:
    _, summary_df = phase5c_outputs
    s = summary_df.iloc[0]
    assert s["source_model"] == "tdf_lowparam_3knot"
    assert bool(s["separate_halo_used"]) is False
    assert bool(s["lensing_only_fit"]) is False
    assert bool(s["not_direct_lensing_flag"]) is True
    assert bool(s["normalized_proxy_deflection_flag"]) is True
    assert bool(s["alpha_tau_scale_fitted"]) is False
    assert s["consistency_status"] in ("PASS_WITH_CAVEAT", "REVIEW_REQUIRED")


def test_config_safeguards() -> None:
    with CONFIG.open() as f:
        cfg = yaml.safe_load(f)
    limits = cfg["tdf"]["lensing"]["observational_limits"]
    assert limits["enabled"] is False
    phys = cfg["tdf"]["lensing"]["physical_calibration"]
    assert phys["enabled"] is False
    assert phys["output_units"] == "normalized_proxy"


def test_report_no_forbidden_claims() -> None:
    report = REPORT_OUT.read_text(encoding="utf-8").lower()
    for phrase in FORBIDDEN_AFFIRMATIVE:
        if phrase == "observational detection":
            assert "no observational detection" in report or "not" in report
        else:
            assert phrase not in report
    assert "normalized_proxy" in report
    assert "arcsec" not in report or "no arcsec" in report


def test_no_lensing_calibration_columns(phase5c_outputs: tuple[pd.DataFrame, pd.DataFrame]) -> None:
    _, summary_df = phase5c_outputs
    cols = " ".join(summary_df.columns).lower()
    assert "deflection_arcsec" not in cols
    assert "tau_deflection_comparison" not in cols
    assert bool(summary_df.iloc[0]["alpha_tau_scale_fitted"]) is False
