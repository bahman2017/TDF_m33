"""Phase 6F data gate checker."""

from __future__ import annotations

import hashlib
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Literal

import yaml

GateStatus = Literal["PASS", "FAIL", "PARTIAL", "N/A"]

REFERENCE_ONLY_MARKER = "REFERENCE_ONLY_NOT_FOR_SCIENTIFIC_CLAIMS"
BLOCKED_MESSAGE = "BLOCKED_PENDING_PRIMARY_CORBELLI_MAPS"

PRIMARY_HI_DIR = "data/raw/phase6f/primary/corbelli2014_hi"
PRIMARY_STELLAR_DIR = "data/raw/phase6f/primary/corbelli2014_stellar_mass"
GEOMETRY_CSV = "data/raw/phase6f/geometry/corbelli2014_tilted_ring_geometry_model_shape.csv"
SOURCE_REGISTRY = "data/raw/phase6f/manifest/phase6f_source_registry.yaml"
CHECKSUMS_FILE = "data/raw/phase6f/CHECKSUMS.sha256"
GRATIER_REF_DIR = "data/raw/phase6f/reference/gratier2010_vla_hi_12sec"


@dataclass
class GateResult:
    gate_id: str
    status: GateStatus
    message: str
    details: dict[str, Any] = field(default_factory=dict)


@dataclass
class GateReport:
    gates: list[GateResult]
    scientific_ready: bool
    reference_only: bool = False
    blocked_message: str | None = None

    def to_rows(self) -> list[dict[str, Any]]:
        return [asdict(g) for g in self.gates]


def _find_primary_fits(directory: Path) -> list[Path]:
    if not directory.is_dir():
        return []
    return sorted(
        p for p in directory.iterdir() if p.suffix.lower() in {".fits", ".fit", ".fts"}
    )


def _sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def _load_registry(repo_root: Path) -> dict[str, Any] | None:
    path = repo_root / SOURCE_REGISTRY
    if not path.is_file():
        return None
    with path.open(encoding="utf-8") as f:
        return yaml.safe_load(f)


def check_g1_primary_hi(repo_root: Path) -> GateResult:
    hi_dir = repo_root / PRIMARY_HI_DIR
    files = _find_primary_fits(hi_dir)
    gratier = repo_root / GRATIER_REF_DIR
    gratier_note = ""
    if gratier.is_dir() and any(gratier.glob("*.fits")):
        gratier_note = " Gratier 2010 reference FITS present but do NOT satisfy G1."
    if files:
        return GateResult(
            "G1_primary_hi_surface_density_map",
            "PASS",
            f"Found {len(files)} primary HI FITS under {PRIMARY_HI_DIR}.",
            {"files": [str(f.relative_to(repo_root)) for f in files]},
        )
    return GateResult(
        "G1_primary_hi_surface_density_map",
        "FAIL",
        f"No primary Corbelli 2014 VLA+GBT HI map in {PRIMARY_HI_DIR}.{gratier_note}",
        {"expected_dir": PRIMARY_HI_DIR},
    )


def check_g2_primary_stellar(repo_root: Path) -> GateResult:
    st_dir = repo_root / PRIMARY_STELLAR_DIR
    files = _find_primary_fits(st_dir)
    if files:
        return GateResult(
            "G2_primary_stellar_surface_density_or_mass_map",
            "PASS",
            f"Found {len(files)} primary stellar map FITS under {PRIMARY_STELLAR_DIR}.",
            {"files": [str(f.relative_to(repo_root)) for f in files]},
        )
    return GateResult(
        "G2_primary_stellar_surface_density_or_mass_map",
        "FAIL",
        f"No Corbelli 2014 BVIgi stellar map in {PRIMARY_STELLAR_DIR}.",
        {"expected_dir": PRIMARY_STELLAR_DIR},
    )


def check_g3_geometry(repo_root: Path) -> GateResult:
    path = repo_root / GEOMETRY_CSV
    if not path.is_file():
        return GateResult(
            "G3_disk_geometry",
            "FAIL",
            f"Tilted-ring geometry CSV missing: {GEOMETRY_CSV}",
        )
    try:
        import pandas as pd

        df = pd.read_csv(path)
        required = {"r_kpc", "inclination_deg", "position_angle_deg"}
        missing = required - set(df.columns)
        if missing:
            return GateResult(
                "G3_disk_geometry",
                "FAIL",
                f"Geometry CSV missing columns: {sorted(missing)}",
            )
        return GateResult(
            "G3_disk_geometry",
            "PASS",
            f"Parsed tilted-ring geometry ({len(df)} rings).",
            {"path": GEOMETRY_CSV, "n_rings": len(df)},
        )
    except Exception as exc:
        return GateResult(
            "G3_disk_geometry",
            "FAIL",
            f"Failed to parse geometry CSV: {exc}",
        )


def check_g4_wcs(repo_root: Path, g1: GateResult, g2: GateResult) -> GateResult:
    if g1.status != "PASS" or g2.status != "PASS":
        return GateResult(
            "G4_wcs_or_grid_metadata",
            "FAIL",
            "WCS/grid metadata cannot be verified without primary maps.",
        )
    from tdf_m33.maps.io import read_fits_2d

    meta_ok = True
    details: dict[str, Any] = {}
    for label, gate in [("hi", g1), ("stellar", g2)]:
        for rel in gate.details.get("files", []):
            path = repo_root / rel
            try:
                _, wcs = read_fits_2d(path)
                details[label] = wcs
                if not wcs.get("has_wcs"):
                    meta_ok = False
            except Exception as exc:
                meta_ok = False
                details[label] = {"error": str(exc)}
    if meta_ok:
        return GateResult(
            "G4_wcs_or_grid_metadata",
            "PASS",
            "WCS or documented grid metadata available for primary maps.",
            details,
        )
    return GateResult(
        "G4_wcs_or_grid_metadata",
        "PARTIAL",
        "Primary files present but WCS metadata incomplete.",
        details,
    )


def check_g5_units(repo_root: Path, g1: GateResult, g2: GateResult) -> GateResult:
    units_doc = repo_root / "docs/phase6f_dataset_access_notes.md"
    manifest = repo_root / "docs/phase6f_source_manifest.md"
    if g1.status != "PASS" or g2.status != "PASS":
        if units_doc.is_file() and manifest.is_file():
            return GateResult(
                "G5_units_documented",
                "PARTIAL",
                "Unit documentation exists but primary maps not present to verify headers.",
                {"docs": [str(units_doc.relative_to(repo_root))]},
            )
        return GateResult(
            "G5_units_documented",
            "FAIL",
            "Primary maps missing; units cannot be verified.",
        )
    from tdf_m33.maps.io import read_fits_2d

    units: dict[str, str] = {}
    for label, gate in [("hi", g1), ("stellar", g2)]:
        for rel in gate.details.get("files", []):
            _, wcs = read_fits_2d(repo_root / rel)
            units[label] = str(wcs.get("bunit", "UNKNOWN"))
    if all(u and u != "UNKNOWN" for u in units.values()):
        return GateResult(
            "G5_units_documented",
            "PASS",
            "BUNIT headers documented for primary maps.",
            {"units": units},
        )
    return GateResult(
        "G5_units_documented",
        "PARTIAL",
        "Primary maps present; some BUNIT values missing.",
        {"units": units},
    )


def check_g6_uncertainty(repo_root: Path, g1: GateResult) -> GateResult:
    if g1.status != "PASS":
        return GateResult(
            "G6_mask_or_uncertainty",
            "FAIL",
            "No primary HI map; uncertainty/mask rules not applicable.",
        )
    hi_dir = repo_root / PRIMARY_HI_DIR
    masks = list(hi_dir.glob("*mask*")) + list(hi_dir.glob("*noise*"))
    weight_doc = repo_root / "docs/phase6f_data_gate_report_notes.md"
    if masks:
        return GateResult(
            "G6_mask_or_uncertainty",
            "PASS",
            "Uncertainty or mask companion files found with primary HI.",
            {"files": [m.name for m in masks]},
        )
    if weight_doc.is_file():
        return GateResult(
            "G6_mask_or_uncertainty",
            "PARTIAL",
            "Documented weighting rules exist; no uncertainty map files found.",
        )
    return GateResult(
        "G6_mask_or_uncertainty",
        "FAIL",
        "No uncertainty maps or documented weighting rules for primary HI.",
    )


def check_g7_provenance(repo_root: Path) -> GateResult:
    registry_path = repo_root / SOURCE_REGISTRY
    checksums_path = repo_root / CHECKSUMS_FILE
    access_notes = repo_root / "docs/phase6f_dataset_access_notes.md"
    missing = [
        p for p in (registry_path, access_notes) if not p.is_file()
    ]
    if missing:
        return GateResult(
            "G7_provenance_and_license",
            "FAIL",
            f"Missing provenance files: {[str(m.relative_to(repo_root)) for m in missing]}",
        )
    registry = _load_registry(repo_root)
    if registry is None:
        return GateResult(
            "G7_provenance_and_license",
            "FAIL",
            "Could not load source registry YAML.",
        )
    primary_ids = {
        "corbelli2014_hi_2d_vla_gbt",
        "corbelli2014_stellar_mass_bvigi_2d",
    }
    sources = registry.get("sources", [])
    found = {s.get("source_id") for s in sources if isinstance(s, dict)}
    if not primary_ids.issubset(found):
        return GateResult(
            "G7_provenance_and_license",
            "PARTIAL",
            "Registry missing primary source entries.",
        )
    return GateResult(
        "G7_provenance_and_license",
        "PASS",
        "Source registry, access notes, and citations documented.",
        {
            "registry": str(registry_path.relative_to(repo_root)),
            "checksums_file": str(checksums_path.relative_to(repo_root)),
            "checksums_present": checksums_path.is_file(),
        },
    )


def run_data_gates(
    repo_root: Path,
    *,
    reference_only: bool = False,
) -> GateReport:
    """Evaluate Phase 6F data gates."""
    g1 = check_g1_primary_hi(repo_root)
    g2 = check_g2_primary_stellar(repo_root)
    g3 = check_g3_geometry(repo_root)
    g4 = check_g4_wcs(repo_root, g1, g2)
    g5 = check_g5_units(repo_root, g1, g2)
    g6 = check_g6_uncertainty(repo_root, g1)
    g7 = check_g7_provenance(repo_root)

    gates = [g1, g2, g3, g4, g5, g6, g7]
    required_for_science = [g1, g2, g3, g4, g5, g7]
    scientific_ready = all(g.status == "PASS" for g in required_for_science)

    blocked = None
    if not scientific_ready and not reference_only:
        blocked = BLOCKED_MESSAGE

    return GateReport(
        gates=gates,
        scientific_ready=scientific_ready,
        reference_only=reference_only,
        blocked_message=blocked,
    )


def gratier_does_not_satisfy_g1(repo_root: Path) -> bool:
    """True when only Gratier reference HI exists (not primary Corbelli)."""
    g1 = check_g1_primary_hi(repo_root)
    gratier_dir = repo_root / GRATIER_REF_DIR
    has_gratier = gratier_dir.is_dir() and any(gratier_dir.glob("*.fits"))
    return g1.status == "FAIL" and has_gratier
