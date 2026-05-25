"""Phase 4B-A: project Phase 4A disk-plane τ map to sky-plane coordinates."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import yaml

from tdf_m33.models.tdf_projection import (
    geometry_roundtrip_error_kpc,
    project_tau_map_to_sky_plane,
    resolve_projection_geometry,
)

FIG_CAVEAT = (
    "Phase 4B-A: geometry/projection only. τ field unchanged (no resampling). "
    "Placeholder inclination/PA flagged in metadata when used. "
    "No lensing; no new τ fit. D1 baryonic PASS_WITH_CAVEAT."
)


def load_phase4b_config(config_path: Path) -> dict[str, Any]:
    with config_path.open() as f:
        cfg = yaml.safe_load(f)
    tdf = cfg.get("tdf", {})
    proj = tdf.get("projection", {})
    data = cfg.get("data", {})
    out_root = Path(cfg.get("project", {}).get("output_root", "outputs/"))
    source_map = Path(proj.get("source_map", "outputs/maps/phase4a_tau_2d_map.npz"))
    if not source_map.is_absolute():
        source_map = config_path.resolve().parents[1] / source_map

    inc = proj.get("inclination_deg")
    pa = proj.get("position_angle_deg")
    return {
        "enabled": bool(proj.get("enabled", True)),
        "source_map": source_map,
        "coordinate_frame_in": str(proj.get("coordinate_frame_in", "disk_plane")),
        "coordinate_frame_out": str(proj.get("coordinate_frame_out", "sky_plane")),
        "inclination_deg": None if inc is None else float(inc),
        "position_angle_deg": None if pa is None else float(pa),
        "placeholder_inclination_deg": float(
            proj.get("placeholder_inclination_deg", 56.0)
        ),
        "placeholder_position_angle_deg": float(
            proj.get("placeholder_position_angle_deg", 23.0)
        ),
        "geometry_source": str(
            proj.get("geometry_source", "corbelli_et_al_2014_or_config_placeholder")
        ),
        "allow_placeholder_geometry": bool(proj.get("allow_placeholder_geometry", True)),
        "data_inclination_deg": (
            None
            if data.get("inclination_deg") is None
            else float(data["inclination_deg"])
        ),
        "figure_dpi": int(cfg.get("plotting", {}).get("figure_dpi", 150)),
        "output_root": out_root,
    }


def load_phase4a_map(npz_path: Path) -> dict[str, Any]:
    if not npz_path.is_file():
        raise FileNotFoundError(f"Phase 4A map missing: {npz_path}")
    data = np.load(npz_path, allow_pickle=False)
    required = ("x_kpc", "y_kpc", "tau_2d")
    for key in required:
        if key not in data:
            raise ValueError(f"{npz_path} missing array {key!r}")
    out: dict[str, Any] = {
        "x_disk_kpc": data["x_kpc"],
        "y_disk_kpc": data["y_kpc"],
        "tau_map": data["tau_2d"],
    }
    if "tau_gradient_2d" in data:
        out["tau_gradient_map"] = data["tau_gradient_2d"]
    if "v_tau_kms_2d" in data:
        out["v_tau_map"] = data["v_tau_kms_2d"]
    if "source_model" in data:
        sm = data["source_model"]
        out["source_model"] = str(sm.item() if hasattr(sm, "item") else sm)
    else:
        out["source_model"] = "tdf_lowparam_3knot"
    if "k_tau" in data:
        out["k_tau"] = float(data["k_tau"])
    return out


def build_metadata_row(
    cfg: dict[str, Any],
    map_data: dict[str, Any],
    projected: dict[str, Any],
    *,
    inclination_deg: float,
    position_angle_deg: float,
    placeholder_geometry_flag: bool,
    geometry_resolution: str,
) -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "source_map": str(cfg["source_map"]),
                "source_model": map_data.get("source_model", "tdf_lowparam_3knot"),
                "inclination_deg": inclination_deg,
                "position_angle_deg": position_angle_deg,
                "geometry_source": cfg["geometry_source"],
                "geometry_resolution": geometry_resolution,
                "placeholder_geometry_flag": placeholder_geometry_flag,
                "coordinate_frame_in": cfg["coordinate_frame_in"],
                "coordinate_frame_out": cfg["coordinate_frame_out"],
                "masked_fraction": projected["masked_fraction"],
                "max_roundtrip_error_kpc": projected.get("max_roundtrip_error_kpc"),
                "note_no_lensing": "no lensing prediction yet",
                "note_no_new_tau_fit": "no new tau fit; tau values unchanged at grid indices",
                "note_geometry_only": (
                    "Phase 4B-A is disk-to-sky coordinate projection only; "
                    "prepares map for Phase 5 deflection"
                ),
            }
        ]
    )


def save_projected_npz(
    projected: dict[str, Any],
    map_data: dict[str, Any],
    cfg: dict[str, Any],
    out_path: Path,
    *,
    inclination_deg: float,
    position_angle_deg: float,
    placeholder_geometry_flag: bool,
) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(
        out_path,
        x_disk_kpc=projected["x_disk_kpc"],
        y_disk_kpc=projected["y_disk_kpc"],
        x_sky_kpc=projected["x_sky_kpc"],
        y_sky_kpc=projected["y_sky_kpc"],
        tau_sky=projected["tau_sky"],
        tau_gradient_sky=projected.get("tau_gradient_sky"),
        v_tau_kms_sky=projected.get("v_tau_kms_sky"),
        source_map=str(cfg["source_map"]),
        source_model=map_data.get("source_model", "tdf_lowparam_3knot"),
        inclination_deg=inclination_deg,
        position_angle_deg=position_angle_deg,
        placeholder_geometry_flag=placeholder_geometry_flag,
        coordinate_frame_in=cfg["coordinate_frame_in"],
        coordinate_frame_out=cfg["coordinate_frame_out"],
    )


def _plot_sky_tau(projected: dict[str, Any], out_path: Path, dpi: int) -> None:
    fig, ax = plt.subplots(figsize=(7, 6))
    extent = [
        projected["x_sky_kpc"].min(),
        projected["x_sky_kpc"].max(),
        projected["y_sky_kpc"].min(),
        projected["y_sky_kpc"].max(),
    ]
    im = ax.imshow(
        projected["tau_sky"],
        origin="lower",
        extent=extent,
        aspect="equal",
        cmap="viridis",
    )
    ax.set_xlabel(r"$x_{\mathrm{sky}}$ [kpc]")
    ax.set_ylabel(r"$y_{\mathrm{sky}}$ [kpc]")
    ax.set_title(r"Phase 4B-A — $\tau$ on sky plane (coords projected)")
    plt.colorbar(im, ax=ax, label=r"$\tau$")
    fig.text(0.5, 0.01, FIG_CAVEAT, ha="center", fontsize=6)
    fig.tight_layout(rect=[0, 0.04, 1, 1])
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, dpi=dpi)
    plt.close(fig)


def _plot_geometry_check(
    projected: dict[str, Any],
    inclination_deg: float,
    position_angle_deg: float,
    placeholder_flag: bool,
    out_path: Path,
    dpi: int,
) -> None:
    x_d = projected["x_disk_kpc"]
    y_d = projected["y_disk_kpc"]
    err = geometry_roundtrip_error_kpc(
        x_d, y_d, inclination_deg, position_angle_deg
    )
    finite = np.isfinite(err)
    max_err = float(np.nanmax(err[finite])) if finite.any() else np.nan

    fig, axes = plt.subplots(1, 2, figsize=(10, 4.5))

    R_disk = np.sqrt(x_d**2 + y_d**2)
    axes[0].scatter(
        x_d[finite], y_d[finite], c=R_disk[finite], s=1, cmap="viridis", alpha=0.5
    )
    axes[0].set_xlabel(r"$x_{\mathrm{disk}}$ [kpc]")
    axes[0].set_ylabel(r"$y_{\mathrm{disk}}$ [kpc]")
    axes[0].set_title("Disk plane (input grid)")
    axes[0].set_aspect("equal")

    x_s = projected["x_sky_kpc"]
    y_s = projected["y_sky_kpc"]
    axes[1].scatter(
        x_s[finite], y_s[finite], c=R_disk[finite], s=1, cmap="viridis", alpha=0.5
    )
    axes[1].set_xlabel(r"$x_{\mathrm{sky}}$ [kpc]")
    axes[1].set_ylabel(r"$y_{\mathrm{sky}}$ [kpc]")
    axes[1].set_title("Sky plane (projected coords)")
    axes[1].set_aspect("equal")

    ph = "PLACEHOLDER geometry" if placeholder_flag else "config geometry"
    fig.suptitle(
        f"Phase 4B-A geometry check — i={inclination_deg:.1f}°, "
        f"PA={position_angle_deg:.1f}° ({ph}); max round-trip err={max_err:.2e} kpc",
        fontsize=9,
    )
    fig.text(0.5, 0.01, FIG_CAVEAT, ha="center", fontsize=6)
    fig.tight_layout(rect=[0, 0.06, 1, 0.94])
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, dpi=dpi)
    plt.close(fig)


def run_phase4b_tau_projection(
    config_path: Path,
    metadata_path: Path,
    projected_npz_path: Path,
    fig_sky: Path,
    fig_geometry: Path,
) -> tuple[pd.DataFrame, dict[str, Any]]:
    """Run Phase 4B-A projection pipeline."""
    cfg = load_phase4b_config(config_path)
    if not cfg["enabled"]:
        raise ValueError("tdf.projection.enabled is false")

    map_data = load_phase4a_map(cfg["source_map"])
    inc, pa, placeholder_flag, geom_res = resolve_projection_geometry(
        cfg["inclination_deg"],
        cfg["position_angle_deg"],
        allow_placeholder_geometry=cfg["allow_placeholder_geometry"],
        placeholder_inclination_deg=cfg["placeholder_inclination_deg"],
        placeholder_position_angle_deg=cfg["placeholder_position_angle_deg"],
        data_inclination_deg=cfg["data_inclination_deg"],
    )

    projected = project_tau_map_to_sky_plane(
        map_data["x_disk_kpc"],
        map_data["y_disk_kpc"],
        map_data["tau_map"],
        inc,
        pa,
        tau_gradient_map=map_data.get("tau_gradient_map"),
        v_tau_map=map_data.get("v_tau_map"),
    )

    err = geometry_roundtrip_error_kpc(
        map_data["x_disk_kpc"],
        map_data["y_disk_kpc"],
        inc,
        pa,
    )
    finite = np.isfinite(err)
    projected["max_roundtrip_error_kpc"] = (
        float(np.max(err[finite])) if finite.any() else np.nan
    )

    metadata_df = build_metadata_row(
        cfg,
        map_data,
        projected,
        inclination_deg=inc,
        position_angle_deg=pa,
        placeholder_geometry_flag=placeholder_flag,
        geometry_resolution=geom_res,
    )

    metadata_path.parent.mkdir(parents=True, exist_ok=True)
    metadata_df.to_csv(metadata_path, index=False)

    save_projected_npz(
        projected,
        map_data,
        cfg,
        projected_npz_path,
        inclination_deg=inc,
        position_angle_deg=pa,
        placeholder_geometry_flag=placeholder_flag,
    )

    dpi = cfg["figure_dpi"]
    _plot_sky_tau(projected, fig_sky, dpi)
    _plot_geometry_check(projected, inc, pa, placeholder_flag, fig_geometry, dpi)

    return metadata_df, projected
