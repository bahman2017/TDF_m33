"""Phase 5A: normalized deflection-proxy maps from frozen sky-plane τ."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import yaml

from tdf_m33.lensing.deflection import (
    UNITS_NORMALIZED_PROXY,
    compute_convergence_proxy,
    compute_deflection_magnitude,
    compute_deflection_proxy,
    compute_tau_gradients_sky,
    deflection_summary_stats,
)

FIG_CAVEAT = (
    "Phase 5A: normalized deflection proxy from frozen τ (no lensing fit). "
    "K_τ=1 normalization. D1 baryonic PASS_WITH_CAVEAT. No separate halo. "
    "Not a detection claim; not evidence vs dark matter."
)

REQUIRED_SOURCE_MODEL = "tdf_lowparam_3knot"
BARYONIC_STATUS = "PASS_WITH_CAVEAT"


def load_phase5a_config(config_path: Path) -> dict[str, Any]:
    with config_path.open() as f:
        cfg = yaml.safe_load(f)
    tdf = cfg.get("tdf", {})
    lens = tdf.get("lensing", {})
    lp = tdf.get("low_parameter_model", {})
    repo = config_path.resolve().parents[1]
    source_map = Path(
        lens.get("source_map", "outputs/maps/phase4b_tau_sky_projected_map.npz")
    )
    if not source_map.is_absolute():
        source_map = repo / source_map
    return {
        "enabled": bool(lens.get("enabled", True)),
        "source_map": source_map,
        "source_model": str(lens.get("source_model", REQUIRED_SOURCE_MODEL)),
        "deflection_mode": str(
            lens.get("deflection_mode", "normalized_tau_gradient_proxy")
        ),
        "alpha_tau_scale": float(lens.get("alpha_tau_scale", 1.0)),
        "units": str(lens.get("units", UNITS_NORMALIZED_PROXY)),
        "compare_to_observational_limits": bool(
            lens.get("compare_to_observational_limits", False)
        ),
        "observational_limits_source": lens.get("observational_limits_source"),
        "k_tau": float(lp.get("k_tau", tdf.get("k_tau", 1.0))),
        "figure_dpi": int(cfg.get("plotting", {}).get("figure_dpi", 150)),
        "compute_convergence": bool(lens.get("compute_convergence_proxy", True)),
    }


def load_phase4b_sky_map(npz_path: Path) -> dict[str, Any]:
    if not npz_path.is_file():
        raise FileNotFoundError(f"Phase 4B sky map missing: {npz_path}")
    data = np.load(npz_path, allow_pickle=False)
    for key in ("x_sky_kpc", "y_sky_kpc", "tau_sky"):
        if key not in data:
            raise ValueError(f"{npz_path} missing {key!r}")

    def _scalar(key: str, default: Any = None) -> Any:
        if key not in data:
            return default
        v = data[key]
        if hasattr(v, "item"):
            return v.item()
        return v

    return {
        "x_sky_kpc": data["x_sky_kpc"],
        "y_sky_kpc": data["y_sky_kpc"],
        "tau_sky": data["tau_sky"],
        "source_model": str(_scalar("source_model", REQUIRED_SOURCE_MODEL)),
        "geometry_mode": str(_scalar("geometry_mode", "")),
        "geometry_source": str(_scalar("geometry_source", "")),
        "geometry_reference": str(_scalar("geometry_reference", "")),
        "placeholder_geometry_flag": bool(_scalar("placeholder_geometry_flag", True)),
        "source_map_phase4b": str(_scalar("source_map", npz_path)),
    }


def validate_frozen_inputs(map_data: dict[str, Any], cfg: dict[str, Any]) -> None:
    if map_data["source_model"] != cfg["source_model"]:
        raise ValueError(
            f"source_model {map_data['source_model']!r} != "
            f"expected {cfg['source_model']!r}"
        )
    if map_data["placeholder_geometry_flag"]:
        raise ValueError("placeholder_geometry_flag must be false for Phase 5A")
    if cfg["compare_to_observational_limits"]:
        if not cfg["observational_limits_source"]:
            raise ValueError(
                "compare_to_observational_limits requires "
                "observational_limits_source in docs/data_sources.md"
            )


def build_deflection_products(
    map_data: dict[str, Any],
    cfg: dict[str, Any],
) -> dict[str, Any]:
    grad_x, grad_y = compute_tau_gradients_sky(
        map_data["tau_sky"],
        map_data["x_sky_kpc"],
        map_data["y_sky_kpc"],
    )
    alpha_x, alpha_y = compute_deflection_proxy(
        grad_x, grad_y, alpha_tau_scale=cfg["alpha_tau_scale"]
    )
    alpha_mag = compute_deflection_magnitude(alpha_x, alpha_y)

    out: dict[str, Any] = {
        "grad_tau_x": grad_x,
        "grad_tau_y": grad_y,
        "alpha_x": alpha_x,
        "alpha_y": alpha_y,
        "alpha_magnitude": alpha_mag,
        "convergence_proxy": None,
        "convergence_diagnostics": {
            "convergence_computed": False,
            "convergence_stable": False,
            "reason": "skipped",
        },
    }

    if cfg["compute_convergence"]:
        kappa, diag = compute_convergence_proxy(
            alpha_x, alpha_y, map_data["x_sky_kpc"], map_data["y_sky_kpc"]
        )
        out["convergence_proxy"] = kappa
        out["convergence_diagnostics"] = diag

    out["summary"] = deflection_summary_stats(
        alpha_mag, units=cfg["units"]
    )
    return out


def build_metadata_row(
    cfg: dict[str, Any],
    map_data: dict[str, Any],
    products: dict[str, Any],
) -> pd.DataFrame:
    diag = products["convergence_diagnostics"]
    summary = products["summary"]
    return pd.DataFrame(
        [
            {
                "source_tau_map": str(cfg["source_map"]),
                "source_model": map_data["source_model"],
                "geometry_mode": map_data["geometry_mode"],
                "geometry_source": map_data["geometry_source"],
                "geometry_reference": map_data["geometry_reference"],
                "placeholder_geometry_flag": map_data["placeholder_geometry_flag"],
                "deflection_mode": cfg["deflection_mode"],
                "alpha_tau_scale": cfg["alpha_tau_scale"],
                "units": cfg["units"],
                "k_tau": cfg["k_tau"],
                "baryonic_velocity_status": BARYONIC_STATUS,
                "separate_halo_used": False,
                "lensing_only_fit": False,
                "compare_to_observational_limits": cfg["compare_to_observational_limits"],
                "observational_limits_source": cfg["observational_limits_source"] or "",
                "convergence_computed": diag.get("convergence_computed", False),
                "convergence_stable": diag.get("convergence_stable", False),
                "convergence_note": diag.get("reason", ""),
                "alpha_magnitude_max": summary["alpha_magnitude_max"],
                "alpha_magnitude_median": summary["alpha_magnitude_median"],
                "fraction_pixels_finite": summary["fraction_finite"],
                "note_prediction_scaffold": (
                    "prediction/consistency scaffold only; not observational detection"
                ),
                "note_k_tau": (
                    "K_tau=1 is normalization convention, not physical calibration"
                ),
                "note_no_dm_disproof": "does not claim dark matter is disproven",
            }
        ]
    )


def build_summary_table(products: dict[str, Any], cfg: dict[str, Any]) -> pd.DataFrame:
    rows = [products["summary"]]
    diag = products["convergence_diagnostics"]
    rows.append(
        {
            "metric": "convergence_proxy",
            "units": cfg["units"],
            "convergence_computed": diag.get("convergence_computed"),
            "convergence_stable": diag.get("convergence_stable"),
            "valid_fraction": diag.get("valid_fraction", np.nan),
            "median_abs": diag.get("median_abs_kappa_proxy", np.nan),
            "max_abs": diag.get("max_abs_kappa_proxy", np.nan),
            "note": diag.get("reason", ""),
        }
    )
    return pd.DataFrame(rows)


def write_report(
    path: Path,
    cfg: dict[str, Any],
    map_data: dict[str, Any],
    products: dict[str, Any],
) -> None:
    summary = products["summary"]
    diag = products["convergence_diagnostics"]
    lines = [
        "# Phase 5A — Lensing / deflection prediction (normalized proxy)",
        "",
        "**Scope:** First deflection-proxy maps from the **same frozen** sky-plane τ "
        "map as rotation (Phase 4B). **Not** a lensing fit. **Not** a dark-matter "
        "disproof.",
        "",
        "## Inputs",
        "",
        f"- Sky τ map: `{cfg['source_map']}`",
        f"- source_model: `{map_data['source_model']}`",
        f"- geometry_mode: `{map_data['geometry_mode']}`",
        f"- geometry_source: `{map_data['geometry_source']}`",
        f"- placeholder_geometry_flag: `{map_data['placeholder_geometry_flag']}`",
        "",
        "## Deflection proxy",
        "",
        f"- Mode: `{cfg['deflection_mode']}`",
        f"- α_x = −α_τ_scale ∂τ/∂x_sky, α_y = −α_τ_scale ∂τ/∂y_sky",
        f"- α_τ_scale: **{cfg['alpha_tau_scale']}** (normalization placeholder)",
        f"- Units: **{cfg['units']}**",
        "",
        "## Summary (finite pixels)",
        "",
        f"- |α| max: **{summary['alpha_magnitude_max']:.6g}**",
        f"- |α| median: **{summary['alpha_magnitude_median']:.6g}**",
        f"- Fraction finite: **{summary['fraction_finite']:.4f}**",
        "",
        "## Convergence proxy",
        "",
        f"- Computed: **{diag.get('convergence_computed')}**",
        f"- Stable: **{diag.get('convergence_stable')}**",
        f"- Note: {diag.get('reason', 'n/a')}",
        "",
        "## Caveats",
        "",
        "- Baryonic velocities: D1-derived **PASS_WITH_CAVEAT**.",
        "- K_τ = 1 is a project normalization, not physical lensing calibration.",
        "- **No separate dark-matter halo** in the TDF lensing branch.",
        "- **No lensing-only fit**; τ was fixed from Phase 3C/4B.",
        f"- Observational limit comparison: **{cfg['compare_to_observational_limits']}** "
        f"(source: {cfg['observational_limits_source'] or 'none documented'}).",
        "",
        "## Phase 5B (planned)",
        "",
        "- Physical α_τ calibration when documented.",
        "- Comparison to observational limits once listed in `docs/data_sources.md`.",
        "",
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def save_deflection_npz(
    path: Path,
    map_data: dict[str, Any],
    products: dict[str, Any],
    cfg: dict[str, Any],
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload: dict[str, Any] = {
        "x_sky_kpc": map_data["x_sky_kpc"],
        "y_sky_kpc": map_data["y_sky_kpc"],
        "tau_sky": map_data["tau_sky"],
        "alpha_x": products["alpha_x"],
        "alpha_y": products["alpha_y"],
        "alpha_magnitude": products["alpha_magnitude"],
        "grad_tau_x": products["grad_tau_x"],
        "grad_tau_y": products["grad_tau_y"],
        "units": cfg["units"],
        "alpha_tau_scale": cfg["alpha_tau_scale"],
        "deflection_mode": cfg["deflection_mode"],
        "source_model": map_data["source_model"],
        "geometry_mode": map_data["geometry_mode"],
        "separate_halo_used": False,
    }
    if products["convergence_proxy"] is not None:
        payload["convergence_proxy"] = products["convergence_proxy"]
    np.savez_compressed(path, **payload)


def _extent_xy(x: np.ndarray, y: np.ndarray) -> list[float]:
    return [
        float(np.nanmin(x)),
        float(np.nanmax(x)),
        float(np.nanmin(y)),
        float(np.nanmax(y)),
    ]


def _plot_magnitude(
    map_data: dict[str, Any],
    products: dict[str, Any],
    path: Path,
    dpi: int,
) -> None:
    fig, ax = plt.subplots(figsize=(7, 6))
    im = ax.imshow(
        products["alpha_magnitude"],
        origin="lower",
        extent=_extent_xy(map_data["x_sky_kpc"], map_data["y_sky_kpc"]),
        aspect="equal",
        cmap="magma",
    )
    ax.set_xlabel(r"$x_{\mathrm{sky}}$ [kpc]")
    ax.set_ylabel(r"$y_{\mathrm{sky}}$ [kpc]")
    ax.set_title(r"Phase 5A — $|\alpha|$ (normalized_proxy)")
    plt.colorbar(im, ax=ax, label=r"$|\alpha|$")
    fig.text(0.5, 0.01, FIG_CAVEAT, ha="center", fontsize=6)
    fig.tight_layout(rect=[0, 0.04, 1, 1])
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=dpi)
    plt.close(fig)


def _plot_vectors(
    map_data: dict[str, Any],
    products: dict[str, Any],
    path: Path,
    dpi: int,
) -> None:
    x = map_data["x_sky_kpc"]
    y = map_data["y_sky_kpc"]
    ax_ = products["alpha_x"]
    ay_ = products["alpha_y"]
    step = max(x.shape[0] // 25, 1)
    sl = slice(None, None, step)
    fig, ax = plt.subplots(figsize=(7, 6))
    ax.quiver(
        x[sl, sl],
        y[sl, sl],
        ax_[sl, sl],
        ay_[sl, sl],
        angles="xy",
        scale_units="xy",
    )
    ax.set_xlabel(r"$x_{\mathrm{sky}}$ [kpc]")
    ax.set_ylabel(r"$y_{\mathrm{sky}}$ [kpc]")
    ax.set_title("Phase 5A — deflection proxy vectors (subsampled)")
    ax.set_aspect("equal")
    fig.text(0.5, 0.01, FIG_CAVEAT, ha="center", fontsize=6)
    fig.tight_layout(rect=[0, 0.04, 1, 1])
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=dpi)
    plt.close(fig)


def _plot_convergence(
    map_data: dict[str, Any],
    products: dict[str, Any],
    path: Path,
    dpi: int,
) -> None:
    kappa = products["convergence_proxy"]
    if kappa is None:
        return
    fig, ax = plt.subplots(figsize=(7, 6))
    im = ax.imshow(
        kappa,
        origin="lower",
        extent=_extent_xy(map_data["x_sky_kpc"], map_data["y_sky_kpc"]),
        aspect="equal",
        cmap="RdBu_r",
    )
    ax.set_xlabel(r"$x_{\mathrm{sky}}$ [kpc]")
    ax.set_ylabel(r"$y_{\mathrm{sky}}$ [kpc]")
    stable = products["convergence_diagnostics"].get("convergence_stable", False)
    ax.set_title(
        "Phase 5A — convergence proxy κ"
        + (" (flagged: edge sensitivity)" if not stable else "")
    )
    plt.colorbar(im, ax=ax, label=r"$\kappa$ (normalized_proxy)")
    fig.text(0.5, 0.01, FIG_CAVEAT, ha="center", fontsize=6)
    fig.tight_layout(rect=[0, 0.04, 1, 1])
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=dpi)
    plt.close(fig)


def run_phase5a_lensing_prediction(
    config_path: Path,
    deflection_npz_path: Path,
    metadata_path: Path,
    summary_path: Path,
    report_path: Path,
    fig_magnitude: Path,
    fig_vectors: Path,
    fig_convergence: Path,
) -> tuple[pd.DataFrame, pd.DataFrame, dict[str, Any]]:
    """Run Phase 5A deflection-proxy pipeline."""
    cfg = load_phase5a_config(config_path)
    if not cfg["enabled"]:
        raise ValueError("tdf.lensing.enabled is false")

    map_data = load_phase4b_sky_map(cfg["source_map"])
    validate_frozen_inputs(map_data, cfg)
    products = build_deflection_products(map_data, cfg)

    metadata_df = build_metadata_row(cfg, map_data, products)
    summary_df = build_summary_table(products, cfg)

    for p in (metadata_path, summary_path):
        p.parent.mkdir(parents=True, exist_ok=True)
    metadata_df.to_csv(metadata_path, index=False)
    summary_df.to_csv(summary_path, index=False)

    save_deflection_npz(deflection_npz_path, map_data, products, cfg)
    write_report(report_path, cfg, map_data, products)

    dpi = cfg["figure_dpi"]
    _plot_magnitude(map_data, products, fig_magnitude, dpi)
    _plot_vectors(map_data, products, fig_vectors, dpi)
    if products["convergence_proxy"] is not None:
        _plot_convergence(map_data, products, fig_convergence, dpi)

    return metadata_df, summary_df, products
