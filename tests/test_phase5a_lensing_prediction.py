"""Tests for Phase 5A lensing prediction pipeline."""

from pathlib import Path

import numpy as np
import pytest

from tdf_m33.lensing.phase5a_lensing_prediction import run_phase5a_lensing_prediction

REPO_ROOT = Path(__file__).resolve().parents[1]
CONFIG = REPO_ROOT / "configs" / "m33_default.yaml"
SKY_MAP = REPO_ROOT / "outputs/maps/phase4b_tau_sky_projected_map.npz"


@pytest.fixture
def inputs_available() -> bool:
    return SKY_MAP.is_file()


def test_phase5a_pipeline(tmp_path: Path, inputs_available: bool) -> None:
    if not inputs_available:
        pytest.skip("Phase 4B sky map missing")

    metadata_df, summary_df, products = run_phase5a_lensing_prediction(
        CONFIG,
        tmp_path / "deflection.npz",
        tmp_path / "metadata.csv",
        tmp_path / "summary.csv",
        tmp_path / "report.md",
        tmp_path / "mag.png",
        tmp_path / "vec.png",
        tmp_path / "kappa.png",
    )

    for name in (
        "deflection.npz",
        "metadata.csv",
        "summary.csv",
        "report.md",
        "mag.png",
        "vec.png",
    ):
        assert (tmp_path / name).is_file()

    meta = metadata_df.iloc[0]
    assert meta["source_model"] == "tdf_lowparam_3knot"
    assert bool(meta["placeholder_geometry_flag"]) is False
    assert bool(meta["separate_halo_used"]) is False
    assert bool(meta["lensing_only_fit"]) is False
    assert bool(meta["compare_to_observational_limits"]) is False
    assert meta["units"] == "normalized_proxy"
    assert "no dm" in meta["note_no_dm_disproof"].lower() or "disproven" in meta[
        "note_no_dm_disproof"
    ].lower()

    report = (tmp_path / "report.md").read_text(encoding="utf-8").lower()
    assert "normalized" in report
    assert "no separate" in report or "no separate dark" in report

    loaded = np.load(tmp_path / "deflection.npz")
    assert loaded["alpha_x"].shape == products["alpha_x"].shape
    assert bool(loaded["separate_halo_used"]) is False

    assert not any(tmp_path.glob("*halo_fit*"))


def test_no_observational_comparison_claimed(
    tmp_path: Path, inputs_available: bool
) -> None:
    if not inputs_available:
        pytest.skip("sky map missing")
    metadata_df, _, _ = run_phase5a_lensing_prediction(
        CONFIG,
        tmp_path / "d.npz",
        tmp_path / "m.csv",
        tmp_path / "s.csv",
        tmp_path / "r.md",
        tmp_path / "mag.png",
        tmp_path / "vec.png",
        tmp_path / "kappa.png",
    )
    assert bool(metadata_df.iloc[0]["compare_to_observational_limits"]) is False
