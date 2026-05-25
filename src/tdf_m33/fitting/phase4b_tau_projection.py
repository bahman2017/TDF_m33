"""Phase 4B: project Phase 4A disk-plane τ map to sky-plane coordinates."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import yaml

from tdf_m33.models.tdf_projection import (
    ProjectionGeometry,
    geometry_roundtrip_error_kpc,
    project_tau_map_to_sky_plane,
    resolve_projection_geometry,
)

FIG_CAVEAT = (
    "Phase 4B: geometry/projection only. τ unchanged (no resampling). "
    "Corbelli 2014 tilted-ring i(R), PA(R) or documented global approximation. "
    "No lensing; no new τ fit. D1 baryonic PASS_WITH_CAVEAT."
)


def load_phase4b_config(config_path: Path) -> dict[str, Any]:
    with config_path.open() as f:
        cfg = yaml.safe_load(f)
    tdf = cfg.get("tdf", {})
    proj = tdf.get("projection", {})
    data = cfg.get("data", {})
    repo = config_path.resolve().parents[1]
    source_map = Path(proj.get("source_map", "outputs/maps/phase4a_tau_2d_map.npz"))
    if not source_map.is_absolute():
        source_map = repo / source_map

    ring_table = proj.get("tilted_ring_table")
    ring_path = None
    if ring_table:
        ring_path = Path(ring_table)
        if not ring_path.is_absolute():
            ring_path = repo / ring_path

    inc = proj.get("inclination_deg")
    pa = proj.get("position_angle_deg")
    return {
        "enabled": bool(proj.get("enabled", True)),
        "source_map": source_map,
        "coordinate_frame_in": str(proj.get("coordinate_frame_in", "disk_plane")),
        "coordinate_frame_out": str(proj.get("coordinate_frame_out", "sky_plane")),
        "geometry_mode": str(proj.get("geometry_mode", "global_approximation")),
        "geometry_source": str(proj.get("geometry_source", "corbelli_et_al_2014")),
        "geometry_reference": str(proj.get("geometry_reference", "")),
        "tilted_ring_table": ring_path,
        "tilted_ring_method": str(proj.get("tilted_ring_method", "model_shape")),
        "inclination_deg": None if inc is None else float(inc),
        "position_angle_deg": None if pa is None else float(pa),
        "global_reference_inclination_deg": (
            None
            if proj.get("global_reference_inclination_deg") is None
            else float(proj["global_reference_inclination_deg"])
        ),
        "global_reference_position_angle_deg": (
            None
            if proj.get("global_reference_position_angle_deg") is None
            else float(proj["global_reference_position_angle_deg"])
        ),
        "placeholder_inclination_deg": float(
            proj.get("placeholder_inclination_deg", 56.0)
        ),
        "placeholder_position_angle_deg": float(
            proj.get("placeholder_position_angle_deg", 23.0)
        ),
        "allow_placeholder_geometry": bool(proj.get("allow_placeholder_geometry", False)),
        "data_inclination_deg": (
            None
            if data.get("inclination_deg") is None
            else float(data["inclination_deg"])
        ),
        "figure_dpi": int(cfg.get("plotting", {}).get("figure_dpi", 150)),
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


def _geometry_summary_strings(geom: ProjectionGeometry) -> dict[str, Any]:
    if geom.is_radial:
        return {
            "inclination_deg": np.nan,
            "position_angle_deg": np.nan,
            "inclination_min_deg": float(np.nanmin(geom.inclination_ring_deg)),
            "inclination_max_deg": float(np.nanmax(geom.inclination_ring_deg)),
            "position_angle_min_deg": float(np.nanmin(geom.position_angle_ring_deg)),
            "position_angle_max_deg": float(np.nanmax(geom.position_angle_ring_deg)),
            "n_tilted_rings": int(len(geom.r_ring_kpc)),
            "tilted_ring_r_min_kpc": float(np.min(geom.r_ring_kpc)),
            "tilted_ring_r_max_kpc": float(np.max(geom.r_ring_kpc)),
        }
    return {
        "inclination_deg": geom.inclination_deg,
        "position_angle_deg": geom.position_angle_deg,
        "inclination_min_deg": geom.inclination_deg,
        "inclination_max_deg": geom.inclination_deg,
        "position_angle_min_deg": geom.position_angle_deg,
        "position_angle_max_deg": geom.position_angle_deg,
        "n_tilted_rings": 0,
        "tilted_ring_r_min_kpc": np.nan,
        "tilted_ring_r_max_kpc": np.nan,
    }


def build_metadata_row(
    cfg: dict[str, Any],
    map_data: dict[str, Any],
    projected: dict[str, Any],
    geom: ProjectionGeometry,
) -> pd.DataFrame:
    summary = _geometry_summary_strings(geom)
    return pd.DataFrame(
        [
            {
                "source_map": str(cfg["source_map"]),
                "source_model": map_data.get("source_model", "tdf_lowparam_3knot"),
                "geometry_mode": geom.geometry_mode,
                "geometry_source": geom.geometry_source,
                "geometry_reference": geom.geometry_reference,
                "geometry_resolution": geom.geometry_resolution,
                "tilted_ring_method": geom.tilted_ring_method or "",
                "tilted_ring_table": (
                    str(cfg["tilted_ring_table"]) if cfg.get("tilted_ring_table") else ""
                ),
                "placeholder_geometry_flag": geom.placeholder_geometry_flag,
                "coordinate_frame_in": cfg["coordinate_frame_in"],
                "coordinate_frame_out": cfg["coordinate_frame_out"],
                "inclination_deg": summary["inclination_deg"],
                "position_angle_deg": summary["position_angle_deg"],
                "inclination_min_deg": summary["inclination_min_deg"],
                "inclination_max_deg": summary["inclination_max_deg"],
                "position_angle_min_deg": summary["position_angle_min_deg"],
                "position_angle_max_deg": summary["position_angle_max_deg"],
                "n_tilted_rings": summary["n_tilted_rings"],
                "tilted_ring_r_min_kpc": summary["tilted_ring_r_min_kpc"],
                "tilted_ring_r_max_kpc": summary["tilted_ring_r_max_kpc"],
                "masked_fraction": projected["masked_fraction"],
                "max_roundtrip_error_kpc": projected.get("max_roundtrip_error_kpc"),
                "note_no_lensing": "no lensing prediction yet",
                "note_no_new_tau_fit": "no new tau fit; tau values unchanged at grid indices",
                "note_geometry_only": (
                    "Phase 4B disk-to-sky projection; prepares map for Phase 5 deflection"
                ),
                "note_warp_approximation": (
                    "M33 disk is warped (Corbelli 2014 Sect. 4.1); "
                    "radial tilted-ring preferred over single global i/PA"
                ),
            }
        ]
    )


def save_projected_npz(
    projected: dict[str, Any],
    map_data: dict[str, Any],
    cfg: dict[str, Any],
    geom: ProjectionGeometry,
    out_path: Path,
) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    payload: dict[str, Any] = {
        "x_disk_kpc": projected["x_disk_kpc"],
        "y_disk_kpc": projected["y_disk_kpc"],
        "x_sky_kpc": projected["x_sky_kpc"],
        "y_sky_kpc": projected["y_sky_kpc"],
        "tau_sky": projected["tau_sky"],
        "inclination_field_deg": projected.get("inclination_field_deg"),
        "position_angle_field_deg": projected.get("position_angle_field_deg"),
        "source_map": str(cfg["source_map"]),
        "source_model": map_data.get("source_model", "tdf_lowparam_3knot"),
        "geometry_mode": geom.geometry_mode,
        "geometry_source": geom.geometry_source,
        "geometry_reference": geom.geometry_reference,
        "placeholder_geometry_flag": geom.placeholder_geometry_flag,
        "coordinate_frame_in": cfg["coordinate_frame_in"],
        "coordinate_frame_out": cfg["coordinate_frame_out"],
    }
    if projected.get("tau_gradient_sky") is not None:
        payload["tau_gradient_sky"] = projected["tau_gradient_sky"]
    if projected.get("v_tau_kms_sky") is not None:
        payload["v_tau_kms_sky"] = projected["v_tau_kms_sky"]
    if geom.is_radial:
        payload["r_ring_kpc"] = geom.r_ring_kpc
        payload["inclination_ring_deg"] = geom.inclination_ring_deg
        payload["position_angle_ring_deg"] = geom.position_angle_ring_deg
    else:
        payload["inclination_deg"] = geom.inclination_deg
        payload["position_angle_deg"] = geom.position_angle_deg
    np.savez_compressed(out_path, **payload)


def _plot_sky_tau(
    projected: dict[str, Any],
    geom: ProjectionGeometry,
    out_path: Path,
    dpi: int,
) -> None:
    fig, ax = plt.subplots(figsize=(7, 6))
    extent = [
        float(np.nanmin(projected["x_sky_kpc"])),
        float(np.nanmax(projected["x_sky_kpc"])),
        float(np.nanmin(projected["y_sky_kpc"])),
        float(np.nanmax(projected["y_sky_kpc"])),
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
    mode = geom.geometry_mode.replace("_", " ")
    ax.set_title(rf"Phase 4B — $\tau$ on sky plane ({mode})")
    plt.colorbar(im, ax=ax, label=r"$\tau$")
    fig.text(0.5, 0.01, FIG_CAVEAT, ha="center", fontsize=6)
    fig.tight_layout(rect=[0, 0.04, 1, 1])
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, dpi=dpi)
    plt.close(fig)


def _plot_geometry_check(
    projected: dict[str, Any],
    geom: ProjectionGeometry,
    out_path: Path,
    dpi: int,
) -> None:
    x_d = projected["x_disk_kpc"]
    y_d = projected["y_disk_kpc"]
    err = geometry_roundtrip_error_kpc(x_d, y_d, geom)
    finite = np.isfinite(err)
    max_err = float(np.nanmax(err[finite])) if finite.any() else np.nan

    fig, axes = plt.subplots(1, 3, figsize=(12, 4.2))

    R_disk = np.sqrt(x_d**2 + y_d**2)
    axes[0].scatter(
        x_d[finite], y_d[finite], c=R_disk[finite], s=1, cmap="viridis", alpha=0.5
    )
    axes[0].set_xlabel(r"$x_{\mathrm{disk}}$ [kpc]")
    axes[0].set_ylabel(r"$y_{\mathrm{disk}}$ [kpc]")
    axes[0].set_title("Disk plane")
    axes[0].set_aspect("equal")

    x_s = projected["x_sky_kpc"]
    y_s = projected["y_sky_kpc"]
    axes[1].scatter(
        x_s[finite], y_s[finite], c=R_disk[finite], s=1, cmap="viridis", alpha=0.5
    )
    axes[1].set_xlabel(r"$x_{\mathrm{sky}}$ [kpc]")
    axes[1].set_ylabel(r"$y_{\mathrm{sky}}$ [kpc]")
    axes[1].set_title("Sky plane (projected)")
    axes[1].set_aspect("equal")

    if geom.is_radial and geom.r_ring_kpc is not None:
        axes[2].plot(
            geom.r_ring_kpc,
            geom.inclination_ring_deg,
            "o-",
            label=r"$i(R)$",
            ms=4,
        )
        ax2 = axes[2].twinx()
        ax2.plot(
            geom.r_ring_kpc,
            geom.position_angle_ring_deg,
            "s--",
            color="C1",
            label=r"PA$(R)$",
            ms=4,
        )
        axes[2].set_xlabel(r"$R$ [kpc]")
        axes[2].set_ylabel(r"$i$ [deg]")
        ax2.set_ylabel(r"PA [deg]")
        axes[2].set_title("Corbelli 2014 Fig. 3 (model-shape)")
        axes[2].legend(loc="upper right", fontsize=7)
        ax2.legend(loc="lower right", fontsize=7)
    else:
        axes[2].axis("off")
        axes[2].text(
            0.5,
            0.5,
            f"Global geometry\n$i={geom.inclination_deg:.1f}°$\n"
            f"PA={geom.position_angle_deg:.1f}°$",
            ha="center",
            va="center",
            fontsize=11,
        )

    ph = "PLACEHOLDER" if geom.placeholder_geometry_flag else "Corbelli 2014"
    fig.suptitle(
        f"Phase 4B geometry — {geom.geometry_mode} ({ph}); "
        f"max round-trip err={max_err:.2e} kpc",
        fontsize=9,
    )
    fig.text(0.5, 0.01, FIG_CAVEAT, ha="center", fontsize=6)
    fig.tight_layout(rect=[0, 0.06, 1, 0.92])
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
    """Run Phase 4B projection pipeline."""
    cfg = load_phase4b_config(config_path)
    if not cfg["enabled"]:
        raise ValueError("tdf.projection.enabled is false")

    map_data = load_phase4a_map(cfg["source_map"])
    geom = resolve_projection_geometry(
        cfg["inclination_deg"],
        cfg["position_angle_deg"],
        geometry_mode=cfg["geometry_mode"],  # type: ignore[arg-type]
        geometry_source=cfg["geometry_source"],
        geometry_reference=cfg["geometry_reference"],
        tilted_ring_table=cfg.get("tilted_ring_table"),
        tilted_ring_method=cfg["tilted_ring_method"],
        allow_placeholder_geometry=cfg["allow_placeholder_geometry"],
        placeholder_inclination_deg=cfg["placeholder_inclination_deg"],
        placeholder_position_angle_deg=cfg["placeholder_position_angle_deg"],
        data_inclination_deg=cfg["data_inclination_deg"],
        global_reference_inclination_deg=cfg.get("global_reference_inclination_deg"),
        global_reference_position_angle_deg=cfg.get(
            "global_reference_position_angle_deg"
        ),
    )

    projected = project_tau_map_to_sky_plane(
        map_data["x_disk_kpc"],
        map_data["y_disk_kpc"],
        map_data["tau_map"],
        geom,
        tau_gradient_map=map_data.get("tau_gradient_map"),
        v_tau_map=map_data.get("v_tau_map"),
    )

    err = geometry_roundtrip_error_kpc(
        map_data["x_disk_kpc"],
        map_data["y_disk_kpc"],
        geom,
    )
    finite = np.isfinite(err)
    projected["max_roundtrip_error_kpc"] = (
        float(np.max(err[finite])) if finite.any() else np.nan
    )

    metadata_df = build_metadata_row(cfg, map_data, projected, geom)
    metadata_path.parent.mkdir(parents=True, exist_ok=True)
    metadata_df.to_csv(metadata_path, index=False)

    save_projected_npz(projected, map_data, cfg, geom, projected_npz_path)

    dpi = cfg["figure_dpi"]
    _plot_sky_tau(projected, geom, fig_sky, dpi)
    _plot_geometry_check(projected, geom, fig_geometry, dpi)

    return metadata_df, projected
