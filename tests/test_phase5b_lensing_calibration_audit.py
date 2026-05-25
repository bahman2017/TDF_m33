"""Tests for Phase 5B-A calibration and limits planning audit."""

from pathlib import Path

import pandas as pd
import pytest
import yaml

from tdf_m33.lensing.phase5b_calibration_audit import run_phase5b_calibration_audit

REPO_ROOT = Path(__file__).resolve().parents[1]
CONFIG = REPO_ROOT / "configs" / "m33_default.yaml"
PHASE5A_METADATA = (
    REPO_ROOT / "outputs" / "tables" / "phase5a_lensing_prediction_metadata.csv"
)

FORBIDDEN_AFFIRMATIVE = (
    "dark matter disproven: true",
    "no need for dark matter",
    "replaces dark matter",
    "dark matter has been ruled out",
)


@pytest.fixture
def metadata_available() -> bool:
    return PHASE5A_METADATA.is_file()


def test_phase5b_audit_outputs(tmp_path: Path, metadata_available: bool) -> None:
    if not metadata_available:
        pytest.skip("Phase 5A metadata missing")

    status_df, _ = run_phase5b_calibration_audit(
        CONFIG,
        PHASE5A_METADATA,
        tmp_path / "status.csv",
        tmp_path / "report.md",
    )
    assert (tmp_path / "status.csv").is_file()
    assert (tmp_path / "report.md").is_file()

    row = status_df.iloc[0]
    assert row["phase5a_units"] == "normalized_proxy"
    assert bool(row["physical_calibration_enabled"]) is False
    assert bool(row["observational_limits_enabled"]) is False
    assert bool(row["phase5a_lensing_only_fit"]) is False
    assert bool(row["phase5a_separate_halo_used"]) is False
    assert bool(row["independent_halo_introduced"]) is False
    assert bool(row["lensing_only_tau_fit"]) is False
    assert bool(row["physical_lensing_detection_claimed"]) is False
    assert bool(row["dark_matter_disproven_claimed"]) is False

    report = (tmp_path / "report.md").read_text(encoding="utf-8").lower()
    for phrase in FORBIDDEN_AFFIRMATIVE:
        assert phrase not in report
    assert "not implemented" in report or "not yet" in report
    assert "normalized" in report


def test_config_physical_calibration_disabled() -> None:
    with CONFIG.open() as f:
        cfg = yaml.safe_load(f)
    phys = cfg["tdf"]["lensing"]["physical_calibration"]
    limits = cfg["tdf"]["lensing"]["observational_limits"]
    assert phys["enabled"] is False
    assert limits["enabled"] is False
    assert phys["output_units"] == "normalized_proxy"
    assert phys["calibration_status"] == "uncalibrated"


def test_audit_rejects_bad_metadata(tmp_path: Path) -> None:
    bad = pd.DataFrame(
        [
            {
                "source_tau_map": "x",
                "source_model": "tdf_lowparam_3knot",
                "geometry_mode": "radial_tilted_ring",
                "geometry_source": "",
                "geometry_reference": "",
                "placeholder_geometry_flag": False,
                "deflection_mode": "normalized_tau_gradient_proxy",
                "alpha_tau_scale": 1.0,
                "units": "arcsec",
                "k_tau": 1.0,
                "baryonic_velocity_status": "PASS_WITH_CAVEAT",
                "separate_halo_used": False,
                "lensing_only_fit": False,
                "compare_to_observational_limits": False,
                "observational_limits_source": "",
                "convergence_computed": True,
                "convergence_stable": True,
                "convergence_note": "",
                "alpha_magnitude_max": 1.0,
                "alpha_magnitude_median": 1.0,
                "fraction_pixels_finite": 1.0,
                "note_prediction_scaffold": "",
                "note_k_tau": "",
                "note_no_dm_disproof": "",
            }
        ]
    )
    meta_path = tmp_path / "bad_meta.csv"
    bad.to_csv(meta_path, index=False)
    with pytest.raises(ValueError, match="units"):
        run_phase5b_calibration_audit(
            CONFIG, meta_path, tmp_path / "s.csv", tmp_path / "r.md"
        )
