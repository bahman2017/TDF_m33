"""Tests for canonical M33 processed-data schema definitions."""

from pathlib import Path

import pandas as pd

from tdf_m33.data.schema import (
    DEFAULT_SCHEMA,
    OPTIONAL_COLUMNS,
    REQUIRED_COLUMNS,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
SCHEMA_TEMPLATE = (
    REPO_ROOT / "data" / "processed" / "m33_rotation_schema_template.csv"
)


def test_required_columns_defined() -> None:
    assert len(REQUIRED_COLUMNS) >= 10
    assert "r_kpc" in REQUIRED_COLUMNS
    assert "v_obs_kms" in REQUIRED_COLUMNS
    assert "source_id" in REQUIRED_COLUMNS


def test_optional_columns_include_provenance_fields() -> None:
    assert "reference" in OPTIONAL_COLUMNS
    assert "digitized_from_figure" in OPTIONAL_COLUMNS


def test_default_schema_lists_all_required() -> None:
    for col in REQUIRED_COLUMNS:
        assert DEFAULT_SCHEMA.column_is_required(col)


def test_schema_template_csv_has_required_headers() -> None:
    assert SCHEMA_TEMPLATE.is_file()
    df = pd.read_csv(SCHEMA_TEMPLATE)
    for col in REQUIRED_COLUMNS:
        assert col in df.columns, f"Template missing required column: {col}"
    assert len(df) == 0, "Template must not contain fake data rows"
