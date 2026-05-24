"""Tests for M33 sources manifest loading and validation."""

from pathlib import Path

import pytest

from tdf_m33.data.manifest import (
    assert_valid_sources_manifest,
    load_sources_manifest,
    validate_sources_manifest,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
MANIFEST_TEMPLATE = REPO_ROOT / "data" / "raw" / "sources_manifest_template.yaml"


def test_manifest_template_loads() -> None:
    manifest = load_sources_manifest(MANIFEST_TEMPLATE)
    assert "sources" in manifest
    assert isinstance(manifest["sources"], list)
    assert len(manifest["sources"]) >= 3


def test_manifest_template_validates() -> None:
    manifest = load_sources_manifest(MANIFEST_TEMPLATE)
    assert validate_sources_manifest(manifest) == []
    assert_valid_sources_manifest(manifest)


def test_duplicate_source_id_fails() -> None:
    manifest = load_sources_manifest(MANIFEST_TEMPLATE)
    dup = dict(manifest["sources"][0])
    manifest = {
        "sources": [manifest["sources"][0], dup],
    }
    errors = validate_sources_manifest(manifest)
    assert any("duplicate source_id" in e for e in errors)


def test_invalid_acquisition_status_fails() -> None:
    manifest = load_sources_manifest(MANIFEST_TEMPLATE)
    bad = dict(manifest["sources"][0])
    bad["acquisition_status"] = "not_a_real_status"
    manifest = {"sources": [bad]}
    errors = validate_sources_manifest(manifest)
    assert any("acquisition_status" in e for e in errors)


def test_missing_required_key_fails() -> None:
    manifest = load_sources_manifest(MANIFEST_TEMPLATE)
    incomplete = {k: v for k, v in manifest["sources"][0].items() if k != "citation_key"}
    manifest = {"sources": [incomplete]}
    errors = validate_sources_manifest(manifest)
    assert any("missing required keys" in e for e in errors)
    with pytest.raises(ValueError, match="citation_key"):
        assert_valid_sources_manifest(manifest)
