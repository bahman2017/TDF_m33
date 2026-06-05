#!/usr/bin/env python3
"""Phase 6F: diagnostic figures for tau-map engine."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from tdf_m33.maps.gates import REFERENCE_ONLY_MARKER, run_data_gates
from tdf_m33.maps.io import load_phase6f_config

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CONFIG = REPO_ROOT / "configs" / "phase6f_nonspherical_tau_map.yaml"

REF_TITLE_SUFFIX = (
    "REFERENCE ONLY — PRIMARY CORBELLI 2014 MAPS NOT ACQUIRED"
)


def plot_gate_matrix(report, out_path: Path) -> None:
    gates = report.gates
    ids = [g.gate_id.replace("_", "\n") for g in gates]
    status_map = {"PASS": 1, "PARTIAL": 0.5, "FAIL": 0, "N/A": -0.1}
    vals = [status_map.get(g.status, 0) for g in gates]
    colors = ["#2ca02c" if v == 1 else "#ff7f0e" if v == 0.5 else "#d62728" for v in vals]

    fig, ax = plt.subplots(figsize=(10, 4))
    ax.barh(ids, vals, color=colors)
    ax.set_xlim(-0.2, 1.2)
    ax.set_xlabel("Gate status (1=PASS, 0.5=PARTIAL, 0=FAIL)")
    ax.set_title("Phase 6F data gate matrix")
    fig.tight_layout()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, dpi=120)
    plt.close(fig)


def _title(base: str, reference_only: bool) -> str:
    if reference_only:
        return f"{base}\n{REF_TITLE_SUFFIX}"
    return base


def plot_source_map(npz_path: Path, out_path: Path, reference_only: bool) -> None:
    if not npz_path.is_file():
        return
    data = np.load(npz_path)
    j = data["j_tau"]
    fig, ax = plt.subplots(figsize=(6, 5))
    im = ax.imshow(j, origin="lower", cmap="viridis")
    ax.set_title(_title("Baryonic source J_tau", reference_only))
    fig.colorbar(im, ax=ax, fraction=0.046)
    fig.tight_layout()
    fig.savefig(out_path, dpi=120)
    plt.close(fig)


def plot_tau_map(npz_path: Path, out_path: Path, reference_only: bool) -> None:
    if not npz_path.is_file():
        return
    data = np.load(npz_path)
    tau = data["tau"]
    fig, ax = plt.subplots(figsize=(6, 5))
    im = ax.imshow(tau, origin="lower", cmap="magma")
    ax.set_title(_title("Disk-plane tau map", reference_only))
    fig.colorbar(im, ax=ax, fraction=0.046)
    fig.tight_layout()
    fig.savefig(out_path, dpi=120)
    plt.close(fig)


def plot_radial_consistency(csv_path: Path, out_path: Path, reference_only: bool) -> None:
    if not csv_path.is_file():
        return
    df = pd.read_csv(csv_path)
    if "r_kpc" not in df.columns or df.empty or "status" in df.columns:
        return
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.plot(df["r_kpc"], df["g_tau_R_mean"], label="g_tau_R (binned)")
    ax.plot(df["r_kpc"], df["g_missing_proxy"], "--", label="missing accel proxy")
    ax.legend()
    ax.set_xlabel("R [kpc]")
    ax.set_title(_title("Radial acceleration consistency", reference_only))
    fig.tight_layout()
    fig.savefig(out_path, dpi=120)
    plt.close(fig)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Phase 6F tau-map diagnostic plots.")
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--repo-root", type=Path, default=REPO_ROOT)
    parser.add_argument("--reference-only", action="store_true")
    args = parser.parse_args(argv)

    cfg = load_phase6f_config(args.config)
    fig_dir = args.repo_root / cfg["outputs"]["figures_dir"]
    report = run_data_gates(args.repo_root, reference_only=args.reference_only)
    ref = args.reference_only or not report.scientific_ready

    plot_gate_matrix(report, fig_dir / "phase6f_data_gate_matrix.png")

    npz = args.repo_root / cfg["outputs"]["tau_map_npz"]
    if npz.is_file():
        plot_source_map(npz, fig_dir / "phase6f_baryonic_source_map.png", ref)
        plot_tau_map(npz, fig_dir / "phase6f_tau_map_disk_plane.png", ref)
        if ref:
            for p in fig_dir.glob("phase6f_*.png"):
                pass  # titles already marked

    radial = args.repo_root / cfg["outputs"]["radial_consistency_csv"]
    plot_radial_consistency(
        radial, fig_dir / "phase6f_radial_acceleration_consistency.png", ref
    )

    print(f"Figures written to {fig_dir}")
    if ref:
        print(REFERENCE_ONLY_MARKER)
    return 0


if __name__ == "__main__":
    sys.exit(main())
