"""Phase 1C repository structure and active manifest tests."""

from pathlib import Path

import pandas as pd

from tdf_m33.data.manifest import assert_valid_sources_manifest, load_sources_manifest

REPO_ROOT = Path(__file__).resolve().parents[1]

EXPECTED_RAW_TABLE1_COLUMNS = [
    "source_id",
    "raw_table_id",
    "row_id",
    "r_kpc",
    "v_rot_kms",
    "v_err_kms",
    "sigma_hi",
    "sigma_h2",
    "sigma_gas",
    "sigma_star",
    "raw_notes",
    "extraction_method",
    "reference",
]
ACTIVE_MANIFEST = REPO_ROOT / "data" / "raw" / "sources_manifest.yaml"
TABLE1_TEMPLATE = (
    REPO_ROOT / "data" / "raw" / "extracted" / "corbelli2014_table1_raw_template.csv"
)


def test_active_manifest_exists_and_validates() -> None:
    assert ACTIVE_MANIFEST.is_file()
    manifest = load_sources_manifest(ACTIVE_MANIFEST)
    assert_valid_sources_manifest(manifest)


def test_raw_table1_template_headers() -> None:
    assert TABLE1_TEMPLATE.is_file()
    df = pd.read_csv(TABLE1_TEMPLATE)
    assert len(df) == 0
    for col in EXPECTED_RAW_TABLE1_COLUMNS:
        assert col in df.columns


def test_phase1c_directories_exist() -> None:
    assert (REPO_ROOT / "data" / "raw" / "downloads").is_dir()
    assert (REPO_ROOT / "data" / "raw" / "extracted").is_dir()


def test_model_ready_csv_not_created() -> None:
    model_ready = REPO_ROOT / "data" / "processed" / "m33_rotation.csv"
    assert not model_ready.is_file()
