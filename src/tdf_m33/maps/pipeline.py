"""Phase 6F pipeline orchestration."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd

from tdf_m33.maps.diagnostics import (
    compute_tau_diagnostics,
    diagnostics_to_dataframe,
    rotation_consistency_diagnostic,
)
from tdf_m33.maps.gates import (
    BLOCKED_MESSAGE,
    REFERENCE_ONLY_MARKER,
    GateReport,
    run_data_gates,
)
from tdf_m33.maps.geometry import build_geometry_fields, geometry_validation_diagnostics
from tdf_m33.maps.grid import build_disk_grid
from tdf_m33.maps.io import (
    load_phase6f_config,
    save_tau_map_npz,
    write_gate_status_csv,
    write_markdown_report,
)
from tdf_m33.maps.solver import solve_tau_field
from tdf_m33.maps.sources import (
    build_reference_proxy_maps,
    build_synthetic_fixture_maps,
    load_primary_source_maps,
)
from tdf_m33.maps.tau_field import TauFieldResult


def _resolve_repo_root(cfg: dict[str, Any], repo_root: Path | None) -> Path:
    if repo_root is not None:
        return repo_root
    p = cfg.get("paths", {}).get("repo_root")
    if p:
        return Path(p)
    return Path(__file__).resolve().parents[3]


def write_gate_reports(report: GateReport, cfg: dict[str, Any], repo_root: Path) -> None:
    out = cfg["outputs"]
    rows = []
    for g in report.gates:
        rows.append(
            {
                "gate_id": g.gate_id,
                "status": g.status,
                "message": g.message,
            }
        )
    write_gate_status_csv(rows, repo_root / out["gate_status_csv"])

    lines = [
        "# Phase 6F tau-map data gate report",
        "",
        f"**scientific_ready:** `{report.scientific_ready}`",
        f"**reference_only:** `{report.reference_only}`",
        "",
    ]
    if report.blocked_message:
        lines.append(f"**blocked_message:** `{report.blocked_message}`")
        lines.append("")
    lines.append("## Gates")
    lines.append("")
    for g in report.gates:
        lines.append(f"- **{g.gate_id}**: `{g.status}` — {g.message}")
    lines.extend(
        [
            "",
            "## Claim control",
            "",
            "Phase 6F-impl scientific tau-map reconstruction requires primary Corbelli 2014 "
            "VLA+GBT HI and BVIgi stellar maps. Gratier 2010 reference FITS do not satisfy G1.",
            "",
            "No dark-matter-disproof or lensing-confirmation claim is made by this report.",
        ]
    )
    write_markdown_report(lines, repo_root / out["gate_report_md"])


def run_gate_check(
    config_path: Path,
    repo_root: Path | None = None,
    *,
    reference_only: bool = False,
) -> GateReport:
    cfg = load_phase6f_config(config_path)
    root = _resolve_repo_root(cfg, repo_root)
    report = run_data_gates(root, reference_only=reference_only)
    write_gate_reports(report, cfg, root)
    return report


def build_tau_map(
    config_path: Path,
    repo_root: Path | None = None,
    *,
    allow_reference_proxy: bool = False,
    use_synthetic_fixture: bool = False,
) -> tuple[GateReport, TauFieldResult | None]:
    cfg = load_phase6f_config(config_path)
    root = _resolve_repo_root(cfg, repo_root)
    report = run_data_gates(root, reference_only=allow_reference_proxy)
    write_gate_reports(report, cfg, root)

    if not report.scientific_ready and not allow_reference_proxy:
        blocked_lines = [
            "# Phase 6F tau-map run report",
            "",
            "Phase 6F scientific tau-map reconstruction is blocked pending primary "
            "Corbelli 2014 VLA+GBT HI and BVIgi stellar maps.",
            "",
            f"**Status:** `{BLOCKED_MESSAGE}`",
            "",
            "No scientific tau-map outputs were generated.",
        ]
        write_markdown_report(blocked_lines, root / cfg["outputs"]["run_report_md"])
        return report, None

    grid_cfg = cfg["grid"]
    if allow_reference_proxy and not report.scientific_ready:
        rp = cfg.get("reference_proxy", {})
        grid_cfg = {
            **grid_cfg,
            "extent_kpc": rp.get("grid_extent_kpc", grid_cfg["extent_kpc"]),
            "pixel_scale_kpc": rp.get("pixel_scale_kpc", grid_cfg["pixel_scale_kpc"]),
        }

    grid = build_disk_grid(
        extent_kpc=float(grid_cfg["extent_kpc"]),
        pixel_scale_kpc=float(grid_cfg["pixel_scale_kpc"]),
        center_x_kpc=float(grid_cfg.get("center_x_kpc", 0.0)),
        center_y_kpc=float(grid_cfg.get("center_y_kpc", 0.0)),
        mask_radius_kpc=float(grid_cfg["mask_radius_kpc"]),
    )

    geom_path = root / cfg["paths"]["geometry_csv"]
    geom_fields = build_geometry_fields(grid.R_kpc, geom_path)
    geom_diag = geometry_validation_diagnostics(geom_fields, grid.mask)

    field = cfg["field"]
    if report.scientific_ready:
        sources = load_primary_source_maps(
            root,
            grid,
            alpha_gas=float(field["alpha_gas"]),
            alpha_star=float(field["alpha_star"]),
            helium_factor=float(field.get("helium_factor", 1.33)),
        )
        mode = "scientific"
        marker = None
    elif use_synthetic_fixture:
        sources = build_synthetic_fixture_maps(
            grid,
            alpha_gas=float(field["alpha_gas"]),
            alpha_star=float(field["alpha_star"]),
        )
        mode = "reference_proxy"
        marker = REFERENCE_ONLY_MARKER
    else:
        sources = build_reference_proxy_maps(
            root,
            grid,
            alpha_gas=float(field["alpha_gas"]),
            alpha_star=float(field["alpha_star"]),
            use_gratier_hi=bool(cfg.get("reference_proxy", {}).get("use_gratier_hi", True)),
        )
        mode = "reference_proxy"
        marker = REFERENCE_ONLY_MARKER

    j = np_where_finite_sources(sources.j_tau, grid.mask)
    tau, solver_diag = solve_tau_field(
        j,
        grid.mask,
        grid.dx_kpc,
        grid.dy_kpc,
        kappa_tau=float(field["kappa_tau"]),
        m_tau=float(field["m_tau"]),
        boundary_condition=field.get("boundary_condition", "dirichlet"),
    )

    result = TauFieldResult(
        tau=tau,
        grid=grid,
        sources=sources,
        solver_diagnostics=solver_diag,
        mode=mode,
        marker=marker,
        metadata={"geometry": geom_diag, "config_phase": cfg.get("phase")},
    )

    Kg = float(field["Kg"])
    diag = compute_tau_diagnostics(result, Kg=Kg)
    diag_df = diagnostics_to_dataframe(diag, marker=marker)
    diag_path = root / cfg["outputs"]["diagnostics_csv"]
    diag_path.parent.mkdir(parents=True, exist_ok=True)
    diag_df.to_csv(diag_path, index=False)

    rot_path = root / cfg["paths"]["rotation_csv"]
    radial_df, radial_summary = rotation_consistency_diagnostic(
        grid,
        diag.g_tau_R,
        rot_path,
        Kg=Kg,
        blocked=not report.scientific_ready,
    )
    radial_csv = root / cfg["outputs"]["radial_consistency_csv"]
    if len(radial_df):
        radial_df.to_csv(radial_csv, index=False)
    elif not report.scientific_ready:
        pd.DataFrame([{"status": "blocked", "message": "Primary maps missing"}]).to_csv(
            radial_csv, index=False
        )

    npz_path = root / cfg["outputs"]["tau_map_npz"]
    save_tau_map_npz(
        npz_path,
        {
            "tau": tau,
            "x_kpc": grid.x_kpc,
            "y_kpc": grid.y_kpc,
            "R_kpc": grid.R_kpc,
            "j_tau": sources.j_tau,
        },
        {"mode": mode, "marker": marker, "solver": solver_diag.__dict__},
        reference_only=marker is not None,
    )

    run_lines = _run_report_lines(report, result, solver_diag, radial_summary, marker)
    write_markdown_report(run_lines, root / cfg["outputs"]["run_report_md"])
    return report, result


def np_where_finite_sources(j_tau, mask):
    import numpy as np

    j = np.where(mask, np.nan_to_num(j_tau, nan=0.0), 0.0)
    return j


def _run_report_lines(report, result, solver_diag, radial_summary, marker):
    lines = [
        "# Phase 6F tau-map run report",
        "",
    ]
    if marker:
        lines.append(f"**{REFERENCE_ONLY_MARKER}**")
        lines.append("")
        lines.append(
            "This run used reference proxy maps. It is NOT a real M33 Phase 6F scientific tau-map."
        )
    else:
        lines.append("**Scientific mode** — primary Corbelli maps satisfied gates.")
    lines.append("")
    lines.append(f"- scientific_ready: `{report.scientific_ready}`")
    lines.append(f"- mode: `{result.mode}`")
    lines.append(f"- solver residual norm: `{solver_diag.residual_norm:.6g}`")
    lines.append(f"- finite tau fraction: `{solver_diag.finite_fraction:.4f}`")
    if radial_summary.get("status") == "blocked":
        lines.append("- radial consistency: **blocked** (primary maps missing)")
    elif "rmse" in radial_summary:
        lines.append(f"- radial consistency RMSE: `{radial_summary['rmse']:.6g}`")
    lines.extend(
        [
            "",
            "## Claim control",
            "",
            "No dark-matter-disproof or M33 lensing-confirmation claim.",
            "Phase 4A remains an axisymmetric scaffold, not this non-spherical engine output.",
        ]
    )
    return lines
