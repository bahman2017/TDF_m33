"""Tests for Phase 4B-A τ projection pipeline."""

from pathlib import Path

import numpy as np
import pytest

from tdf_m33.fitting.phase4b_tau_projection import (
    load_phase4b_config,
    run_phase4b_tau_projection,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
CONFIG = REPO_ROOT / "configs" / "m33_default.yaml"
PHASE4A_MAP = REPO_ROOT / "outputs" / "maps" / "phase4a_tau_2d_map.npz"


@pytest.fixture
def phase4a_available() -> bool:
    return PHASE4A_MAP.is_file()


def test_config_reads_projection_section() -> None:
    cfg = load_phase4b_config(CONFIG)
    assert cfg["coordinate_frame_in"] == "disk_plane"
    assert cfg["coordinate_frame_out"] == "sky_plane"
    assert cfg["allow_placeholder_geometry"] is True
    assert cfg["inclination_deg"] is None
    assert cfg["placeholder_inclination_deg"] == pytest.approx(56.0)


def test_phase4b_pipeline(tmp_path: Path, phase4a_available: bool) -> None:
    if not phase4a_available:
        pytest.skip("Phase 4A map missing")

    metadata_df, projected = run_phase4b_tau_projection(
        CONFIG,
        tmp_path / "metadata.csv",
        tmp_path / "map.npz",
        tmp_path / "sky.png",
        tmp_path / "geom.png",
    )

    for name in ("metadata.csv", "map.npz", "sky.png", "geom.png"):
        assert (tmp_path / name).is_file()

    meta = metadata_df.iloc[0]
    assert meta["source_model"] == "tdf_lowparam_3knot"
    assert meta["placeholder_geometry_flag"] in (True, False)
    assert "no lensing" in meta["note_no_lensing"].lower()
    assert "no new tau fit" in meta["note_no_new_tau_fit"].lower()
    assert projected["tau_sky"].shape == projected["x_sky_kpc"].shape

    loaded = np.load(tmp_path / "map.npz")
    assert loaded["tau_sky"].shape == projected["tau_sky"].shape
    assert np.array_equal(
        np.isnan(loaded["tau_sky"]),
        np.isnan(projected["tau_sky"]),
    )

    assert not any(tmp_path.glob("*lensing*"))


def test_tau_unchanged_under_projection(tmp_path: Path, phase4a_available: bool) -> None:
    if not phase4a_available:
        pytest.skip("Phase 4A map missing")

    _, projected = run_phase4b_tau_projection(
        CONFIG,
        tmp_path / "metadata.csv",
        tmp_path / "map.npz",
        tmp_path / "sky.png",
        tmp_path / "geom.png",
    )
    src = np.load(PHASE4A_MAP)
    np.testing.assert_array_equal(
        projected["tau_sky"],
        src["tau_2d"],
        err_msg="projection must not resample or alter tau values",
    )
