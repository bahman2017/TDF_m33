"""Tests for Phase 4B τ projection pipeline."""

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
RING_TABLE = (
    REPO_ROOT / "data/raw/extracted/corbelli2014_tilted_ring_geometry_model_shape.csv"
)


@pytest.fixture
def phase4a_available() -> bool:
    return PHASE4A_MAP.is_file() and RING_TABLE.is_file()


def test_config_reads_corbelli_geometry() -> None:
    cfg = load_phase4b_config(CONFIG)
    assert cfg["geometry_mode"] == "radial_tilted_ring"
    assert cfg["geometry_source"] == "corbelli_et_al_2014"
    assert cfg["allow_placeholder_geometry"] is False
    assert cfg["tilted_ring_table"] == RING_TABLE


def test_phase4b_pipeline(tmp_path: Path, phase4a_available: bool) -> None:
    if not phase4a_available:
        pytest.skip("Phase 4A map or geometry table missing")

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
    assert bool(meta["placeholder_geometry_flag"]) is False
    assert meta["geometry_mode"] == "radial_tilted_ring"
    assert "corbelli" in meta["geometry_source"].lower()
    assert meta["n_tilted_rings"] == 12
    assert "no lensing" in meta["note_no_lensing"].lower()
    assert projected["tau_sky"].shape == projected["x_sky_kpc"].shape

    loaded = np.load(tmp_path / "map.npz")
    assert loaded["geometry_mode"] == "radial_tilted_ring"
    assert bool(loaded["placeholder_geometry_flag"]) is False
    assert "r_ring_kpc" in loaded

    assert not any(tmp_path.glob("*lensing*"))


def test_tau_unchanged_under_projection(tmp_path: Path, phase4a_available: bool) -> None:
    if not phase4a_available:
        pytest.skip("inputs missing")

    _, projected = run_phase4b_tau_projection(
        CONFIG,
        tmp_path / "metadata.csv",
        tmp_path / "map.npz",
        tmp_path / "sky.png",
        tmp_path / "geom.png",
    )
    src = np.load(PHASE4A_MAP)
    both = np.isfinite(projected["tau_sky"]) & np.isfinite(src["tau_2d"])
    assert both.sum() > 1000
    np.testing.assert_array_equal(
        projected["tau_sky"][both],
        src["tau_2d"][both],
        err_msg="projection must not alter tau where geometry is defined",
    )
    # Additional NaNs allowed where R is outside Corbelli Fig. 3 ring tabulation
    assert np.mean(~np.isfinite(projected["tau_sky"])) >= np.mean(~np.isfinite(src["tau_2d"]))
