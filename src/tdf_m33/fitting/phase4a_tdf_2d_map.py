"""Phase 4A: axisymmetric disk-plane 2D τ map from Phase 3C radial TDF."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import yaml

from tdf_m33.models.tdf_map2d import (
    compare_radial_profile_to_map_average,
    compute_azimuthal_average_from_map,
    make_disk_plane_grid,
    radial_interpolate_to_grid,
)

FIG_CAVEAT = (
    "Phase 4A: axisymmetric disk-plane τ extension of Phase 3C radial model only. "
    "K_τ=1 normalization. D1 baryonic PASS_WITH_CAVEAT. Not a separately fitted map. "
    "No lensing; no morphology or spiral structure yet."
)

SOURCE_MODEL_DEFAULT = "tdf_lowparam_3knot"


def load_phase4a_config(config_path: Path) -> dict[str, Any]:
    with config_path.open() as f:
        cfg = yaml.safe_load(f)
    tdf = cfg.get("tdf", {})
    m2d = tdf.get("map2d", {})
    lp = tdf.get("low_parameter_model", {})
    return {
        "enabled": bool(m2d.get("enabled", True)),
        "source_model": str(m2d.get("source_model", SOURCE_MODEL_DEFAULT)),
        "coordinate_frame": str(m2d.get("coordinate_frame", "disk_plane")),
        "x_extent_kpc": float(m2d.get("x_extent_kpc", 25.0)),
        "y_extent_kpc": float(m2d.get("y_extent_kpc", 25.0)),
        "n_pixels": int(m2d.get("n_pixels", 300)),
        "radial_extrapolation": str(m2d.get("radial_extrapolation", "mask")),
        "azimuthal_check_bins": int(m2d.get("azimuthal_check_bins", 58)),
        "k_tau": float(lp.get("k_tau", tdf.get("k_tau", 1.0))),
        "figure_dpi": int(cfg.get("plotting", {}).get("figure_dpi", 150)),
    }


def load_phase3c_radial_profile(
    profiles_path: Path,
    source_model: str,
) -> pd.DataFrame:
    """Load sorted radial τ profile for the requested Phase 3C model."""
    if not profiles_path.is_file():
        raise FileNotFoundError(f"Phase 3C profiles missing: {profiles_path}")

    df = pd.read_csv(profiles_path)
    sub = df[df["model_name"] == source_model].copy()
    if sub.empty:
        available = sorted(df["model_name"].unique())
        raise ValueError(
            f"source_model {source_model!r} not in {profiles_path}; "
            f"available: {available}"
        )
    return sub.sort_values("r_kpc").reset_index(drop=True)


def build_phase4a_maps(
    profile: pd.DataFrame,
    cfg: dict[str, Any],
) -> dict[str, Any]:
    """Construct 2D τ, dτ/dr, and v_τ maps and consistency diagnostics."""
    if cfg["radial_extrapolation"] != "mask":
        raise ValueError("Phase 4A supports radial_extrapolation='mask' only")

    r_kpc = profile["r_kpc"].to_numpy(dtype=float)
    tau_radial = profile["tau_profile_model"].to_numpy(dtype=float)
    tau_gradient = profile["tau_gradient_model"].to_numpy(dtype=float)
    v_tau_kms = profile["v_tau_kms"].to_numpy(dtype=float)

    x_grid, y_grid = make_disk_plane_grid(
        cfg["x_extent_kpc"],
        cfg["y_extent_kpc"],
        cfg["n_pixels"],
    )
    extrap = "mask"
    tau_map = radial_interpolate_to_grid(
        r_kpc, tau_radial, x_grid, y_grid, radial_extrapolation=extrap
    )
    grad_map = radial_interpolate_to_grid(
        r_kpc, tau_gradient, x_grid, y_grid, radial_extrapolation=extrap
    )
    v_tau_map = radial_interpolate_to_grid(
        r_kpc, v_tau_kms, x_grid, y_grid, radial_extrapolation=extrap
    )

    r_min = float(np.nanmin(r_kpc))
    r_max = float(np.nanmax(r_kpc))
    masked_fraction = float(np.mean(~np.isfinite(tau_map)))

    tau_az_avg = compute_azimuthal_average_from_map(
        x_grid, y_grid, tau_map, r_kpc
    )
    consistency = compare_radial_profile_to_map_average(
        r_kpc, tau_radial, tau_az_avg
    )

    return {
        "x_grid": x_grid,
        "y_grid": y_grid,
        "tau_map": tau_map,
        "tau_gradient_map": grad_map,
        "v_tau_map": v_tau_map,
        "r_kpc": r_kpc,
        "tau_radial": tau_radial,
        "tau_gradient_radial": tau_gradient,
        "v_tau_radial": v_tau_kms,
        "tau_azimuthal_avg": tau_az_avg,
        "consistency": consistency,
        "r_min_kpc": r_min,
        "r_max_kpc": r_max,
        "masked_fraction": masked_fraction,
        "k_tau": cfg["k_tau"],
        "source_model": cfg["source_model"],
    }


def build_consistency_table(maps: dict[str, Any]) -> pd.DataFrame:
    c = maps["consistency"]
    return pd.DataFrame(
        {
            "r_kpc": c["r_kpc"],
            "tau_radial": c["tau_radial"],
            "tau_azimuthal_avg": c["tau_azimuthal_avg"],
            "abs_error": c["abs_error"],
        }
    )


def build_metadata_row(maps: dict[str, Any], cfg: dict[str, Any]) -> pd.DataFrame:
    c = maps["consistency"]
    return pd.DataFrame(
        [
            {
                "source_model": cfg["source_model"],
                "k_tau": cfg["k_tau"],
                "x_extent_kpc": cfg["x_extent_kpc"],
                "y_extent_kpc": cfg["y_extent_kpc"],
                "n_pixels": cfg["n_pixels"],
                "coordinate_frame": cfg["coordinate_frame"],
                "radial_extrapolation": cfg["radial_extrapolation"],
                "max_radius_covered_kpc": maps["r_max_kpc"],
                "min_radius_covered_kpc": maps["r_min_kpc"],
                "fraction_grid_masked": maps["masked_fraction"],
                "max_abs_radial_consistency_error": c["max_abs_error"],
                "rmse_radial_consistency_error": c["rmse_radial_consistency"],
                "n_compared": c["n_compared"],
                "note_axisymmetric_extension": (
                    "axisymmetric disk-plane extension only; "
                    "tau_2d(x,y)=tau_radial(R); not separately fitted"
                ),
                "note_no_lensing": "no lensing prediction yet",
                "note_baryonic_caveat": (
                    "baryonic velocities PASS_WITH_CAVEAT (Phase 1D-D1 derived)"
                ),
                "note_k_tau": "K_tau=1 is normalization convention, not physical calibration",
            }
        ]
    )


def save_map_npz(maps: dict[str, Any], cfg: dict[str, Any], out_path: Path) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(
        out_path,
        x_kpc=maps["x_grid"],
        y_kpc=maps["y_grid"],
        tau_2d=maps["tau_map"],
        tau_gradient_2d=maps["tau_gradient_map"],
        v_tau_kms_2d=maps["v_tau_map"],
        r_kpc_radial=maps["r_kpc"],
        tau_radial=maps["tau_radial"],
        tau_gradient_radial=maps["tau_gradient_radial"],
        v_tau_kms_radial=maps["v_tau_radial"],
        source_model=cfg["source_model"],
        k_tau=cfg["k_tau"],
        coordinate_frame=cfg["coordinate_frame"],
        radial_extrapolation=cfg["radial_extrapolation"],
    )


def _plot_tau_map(
    maps: dict[str, Any],
    out_path: Path,
    dpi: int,
) -> None:
    fig, ax = plt.subplots(figsize=(7, 6))
    extent = [
        maps["x_grid"].min(),
        maps["x_grid"].max(),
        maps["y_grid"].min(),
        maps["y_grid"].max(),
    ]
    im = ax.imshow(
        maps["tau_map"],
        origin="lower",
        extent=extent,
        aspect="equal",
        cmap="viridis",
    )
    ax.set_xlabel(r"$x$ [kpc] (disk plane)")
    ax.set_ylabel(r"$y$ [kpc] (disk plane)")
    ax.set_title(r"Phase 4A — $\tau_{2\mathrm{D}}(x,y)=\tau_{\mathrm{rad}}(R)$")
    plt.colorbar(im, ax=ax, label=r"$\tau$")
    fig.text(0.5, 0.01, FIG_CAVEAT, ha="center", fontsize=6)
    fig.tight_layout(rect=[0, 0.04, 1, 1])
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, dpi=dpi)
    plt.close(fig)


def _plot_tau_gradient_map(
    maps: dict[str, Any],
    out_path: Path,
    dpi: int,
) -> None:
    fig, ax = plt.subplots(figsize=(7, 6))
    extent = [
        maps["x_grid"].min(),
        maps["x_grid"].max(),
        maps["y_grid"].min(),
        maps["y_grid"].max(),
    ]
    im = ax.imshow(
        maps["tau_gradient_map"],
        origin="lower",
        extent=extent,
        aspect="equal",
        cmap="plasma",
    )
    ax.set_xlabel(r"$x$ [kpc] (disk plane)")
    ax.set_ylabel(r"$y$ [kpc] (disk plane)")
    ax.set_title(r"Phase 4A — $d\tau/dr$ on disk plane (axisymmetric)")
    plt.colorbar(im, ax=ax, label=r"$d\tau/dr$")
    fig.text(0.5, 0.01, FIG_CAVEAT, ha="center", fontsize=6)
    fig.tight_layout(rect=[0, 0.04, 1, 1])
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, dpi=dpi)
    plt.close(fig)


def _plot_radial_consistency(
    consistency_df: pd.DataFrame,
    maps: dict[str, Any],
    out_path: Path,
    dpi: int,
) -> None:
    fig, ax = plt.subplots(figsize=(8, 4.5))
    valid = np.isfinite(consistency_df["tau_radial"]) & np.isfinite(
        consistency_df["tau_azimuthal_avg"]
    )
    sub = consistency_df[valid]
    ax.plot(sub["r_kpc"], sub["tau_radial"], "o-", label=r"$\tau_{\mathrm{rad}}$ (3C)")
    ax.plot(
        sub["r_kpc"],
        sub["tau_azimuthal_avg"],
        "s--",
        label=r"azimuthal avg from 2D map",
        ms=4,
    )
    ax.set_xlabel(r"$R$ [kpc]")
    ax.set_ylabel(r"$\tau$")
    ax.set_title("Phase 4A — radial consistency check")
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.3)
    c = maps["consistency"]
    ax.text(
        0.02,
        0.02,
        f"max |Δτ| = {c['max_abs_error']:.4g}\n"
        f"RMSE = {c['rmse_radial_consistency']:.4g}",
        transform=ax.transAxes,
        fontsize=8,
        va="bottom",
    )
    fig.text(0.5, 0.01, FIG_CAVEAT, ha="center", fontsize=6)
    fig.tight_layout(rect=[0, 0.04, 1, 1])
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, dpi=dpi)
    plt.close(fig)


def run_phase4a_tdf_2d_map(
    profiles_path: Path,
    config_path: Path,
    consistency_path: Path,
    metadata_path: Path,
    map_npz_path: Path,
    fig_tau: Path,
    fig_gradient: Path,
    fig_consistency: Path,
) -> tuple[pd.DataFrame, pd.DataFrame, dict[str, Any]]:
    """Run Phase 4A: build 2D maps and export tables/figures."""
    cfg = load_phase4a_config(config_path)
    if not cfg["enabled"]:
        raise ValueError("tdf.map2d.enabled is false")

    profile = load_phase3c_radial_profile(profiles_path, cfg["source_model"])
    maps = build_phase4a_maps(profile, cfg)

    consistency_df = build_consistency_table(maps)
    metadata_df = build_metadata_row(maps, cfg)

    for p in (consistency_path, metadata_path):
        p.parent.mkdir(parents=True, exist_ok=True)
    consistency_df.to_csv(consistency_path, index=False)
    metadata_df.to_csv(metadata_path, index=False)

    save_map_npz(maps, cfg, map_npz_path)

    dpi = cfg["figure_dpi"]
    _plot_tau_map(maps, fig_tau, dpi)
    _plot_tau_gradient_map(maps, fig_gradient, dpi)
    _plot_radial_consistency(consistency_df, maps, fig_consistency, dpi)

    return consistency_df, metadata_df, maps
