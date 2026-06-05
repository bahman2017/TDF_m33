"""Tests for Phase 6F public data acquisition audit."""

from __future__ import annotations

import csv
import importlib.util
from pathlib import Path

import pytest

from tdf_m33.maps.gates import BLOCKED_MESSAGE, run_data_gates
from tdf_m33.maps.public_data_audit import (
    load_public_candidate_registry,
    run_public_data_audit,
    write_public_candidates_csv,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
AUDIT_SCRIPT = REPO_ROOT / "scripts" / "audit_phase6f_public_data_sources.py"
REGISTRY = REPO_ROOT / "data/raw/phase6f/manifest/phase6f_public_candidate_registry.yaml"


def test_registry_loads() -> None:
    registry = load_public_candidate_registry(REPO_ROOT)
    assert "candidates" in registry
    assert len(registry["candidates"]) >= 10


def test_no_candidate_marks_corbelli_primary_gate_without_tier_a_fits() -> None:
    report = run_public_data_audit(REPO_ROOT)
    tier_b_pass_g1 = [
        r
        for r in report.candidates
        if r.can_satisfy_primary_corbelli_gate and not r.tier.upper().startswith("TIER_A")
    ]
    assert tier_b_pass_g1 == []
    direct_public_corbelli_fits = [
        r
        for r in report.candidates
        if r.tier.upper().startswith("TIER_A")
        and "fits" in r.expected_file_type.lower()
        and r.download_status in {"available_public", "direct_download"}
    ]
    assert direct_public_corbelli_fits == []
    assert report.corbelli_primary_fits_found is False


def test_tier_b_candidates_exist_for_pilot() -> None:
    report = run_public_data_audit(REPO_ROOT)
    assert report.tier_b_count >= 5
    pilot_ready = [r for r in report.candidates if r.can_satisfy_public_pilot_gate]
    assert len(pilot_ready) >= 4
    ids = {r.id for r in pilot_ready}
    assert "lglbs_hi_v1_canfar" in ids
    assert "spitzer_s4g_irac_m33" in ids
    assert "iram_lp006_co21_m33" in ids


def test_write_candidates_csv(tmp_path: Path) -> None:
    report = run_public_data_audit(REPO_ROOT)
    out = tmp_path / "candidates.csv"
    write_public_candidates_csv(out, report)
    with out.open(encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    assert len(rows) == len(report.candidates)
    assert all(r["can_satisfy_primary_corbelli_gate"] in {"True", "False"} for r in rows)


def test_audit_script_runs_without_download() -> None:
    spec = importlib.util.spec_from_file_location("audit_public", AUDIT_SCRIPT)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    assert module.main([]) == 0


def test_strict_corbelli_gates_remain_blocked() -> None:
    report = run_data_gates(REPO_ROOT)
    assert report.scientific_ready is False
    assert report.blocked_message == BLOCKED_MESSAGE
    g1 = next(g for g in report.gates if g.gate_id == "G1_primary_hi_surface_density_map")
    g2 = next(
        g for g in report.gates if g.gate_id == "G2_primary_stellar_surface_density_or_mass_map"
    )
    g8 = next(g for g in report.gates if g.gate_id == "G8_primary_map_reprojection_ready")
    assert g1.status == "FAIL"
    assert g2.status == "FAIL"
    assert g8.status == "FAIL"
