"""Tests for Phase 6F public pilot gates P1–P6."""

from __future__ import annotations

from pathlib import Path

import pytest

from tdf_m33.maps.gates import BLOCKED_MESSAGE, run_data_gates
from tdf_m33.maps.public_pilot_gates import (
    PUBLIC_PILOT_CLAIM_LABEL,
    PUBLIC_PILOT_REPROJECTION_AVAILABLE,
    check_p6_public_reprojection,
    run_public_pilot_gates,
    tier_b_cannot_pass_corbelli_gates,
)
from tdf_m33.maps.public_pilot_inventory import PUBLIC_PILOT_CLAIM_LABEL as INV_LABEL

REPO_ROOT = Path(__file__).resolve().parents[1]


def test_claim_label_constant() -> None:
    assert PUBLIC_PILOT_CLAIM_LABEL == INV_LABEL
    assert "NOT_CORBELLI" in PUBLIC_PILOT_CLAIM_LABEL


def test_p_gates_independent_from_g_gates() -> None:
    p_report = run_public_pilot_gates(REPO_ROOT)
    g_report = run_data_gates(REPO_ROOT)
    assert p_report.public_pilot_ready is False
    assert g_report.scientific_ready is False
    p_ids = {g.gate_id for g in p_report.gates}
    g_ids = {g.gate_id for g in g_report.gates}
    assert not p_ids.intersection(g_ids)


def test_p6_fails_until_reprojection_implemented() -> None:
    assert PUBLIC_PILOT_REPROJECTION_AVAILABLE is False
    p6 = check_p6_public_reprojection()
    assert p6.status == "FAIL"


def test_public_pilot_gates_mostly_pending_on_main() -> None:
    report = run_public_pilot_gates(REPO_ROOT)
    p1 = next(g for g in report.gates if g.gate_id == "P1_public_hi_map_available")
    p2 = next(g for g in report.gates if g.gate_id == "P2_public_stellar_irac_available")
    p3 = next(g for g in report.gates if g.gate_id == "P3_public_co_or_h2_available")
    p6 = next(g for g in report.gates if g.gate_id == "P6_public_reprojection_ready")
    assert p1.status == "PENDING"
    assert p2.status == "PENDING"
    assert p3.status == "PENDING"
    assert p6.status == "FAIL"


def test_tier_b_cannot_pass_corbelli_g1_g2() -> None:
    assert tier_b_cannot_pass_corbelli_gates(REPO_ROOT) is True
    g = run_data_gates(REPO_ROOT)
    assert g.blocked_message == BLOCKED_MESSAGE


def test_registry_entries_never_satisfy_corbelli_gate() -> None:
    import yaml

    path = REPO_ROOT / "data/raw/phase6f/public_pilot/manifest/phase6f_public_pilot_source_registry.yaml"
    with path.open(encoding="utf-8") as handle:
        reg = yaml.safe_load(handle)
    for entry in reg.get("sources", []):
        assert entry.get("can_satisfy_primary_corbelli_gate") is False
        assert entry.get("claim_label") == PUBLIC_PILOT_CLAIM_LABEL
