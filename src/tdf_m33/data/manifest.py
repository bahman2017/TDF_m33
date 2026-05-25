"""Load and validate M33 literature source manifests (YAML provenance registry)."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

REQUIRED_SOURCE_KEYS: tuple[str, ...] = (
    "source_id",
    "title",
    "authors",
    "year",
    "publication",
    "data_type",
    "planned_use",
    "acquisition_status",
    "url_or_doi",
    "expected_fields",
    "extraction_method",
    "transformation_notes",
    "limitations",
    "citation_key",
    "notes",
)

ALLOWED_ACQUISITION_STATUS: frozenset[str] = frozenset(
    {
        "planned",
        "located",
        "downloaded",
        "documented",  # PDF + checksum + citation; extraction pending
        "digitized",
        "processed",
        "validated",
    }
)


def load_sources_manifest(path: str | Path) -> dict[str, Any]:
    """Load a sources manifest YAML file and return the parsed dictionary."""
    path = Path(path)
    if not path.is_file():
        raise FileNotFoundError(f"Sources manifest not found: {path}")
    with path.open(encoding="utf-8") as fh:
        data = yaml.safe_load(fh)
    if data is None:
        raise ValueError(f"Sources manifest is empty: {path}")
    if not isinstance(data, dict):
        raise ValueError(f"Sources manifest root must be a mapping: {path}")
    return data


def validate_sources_manifest(manifest: dict[str, Any]) -> list[str]:
    """Return human-readable validation errors (empty list if valid)."""
    errors: list[str] = []

    if "sources" not in manifest:
        errors.append("Missing top-level key 'sources'")
        return errors

    sources = manifest["sources"]
    if not isinstance(sources, list):
        errors.append("Top-level 'sources' must be a list")
        return errors

    seen_ids: set[str] = set()

    for index, entry in enumerate(sources):
        prefix = f"sources[{index}]"
        if not isinstance(entry, dict):
            errors.append(f"{prefix}: each source must be a mapping")
            continue

        missing = [k for k in REQUIRED_SOURCE_KEYS if k not in entry]
        if missing:
            errors.append(f"{prefix}: missing required keys: {', '.join(missing)}")
            continue

        source_id = entry["source_id"]
        if not isinstance(source_id, str) or not source_id.strip():
            errors.append(f"{prefix}: source_id must be a non-empty string")
        elif source_id in seen_ids:
            errors.append(f"{prefix}: duplicate source_id '{source_id}'")
        else:
            seen_ids.add(source_id)

        planned_use = entry["planned_use"]
        if not isinstance(planned_use, str) or not planned_use.strip():
            errors.append(f"{prefix} ({source_id}): planned_use must be non-empty")

        status = entry["acquisition_status"]
        if status not in ALLOWED_ACQUISITION_STATUS:
            errors.append(
                f"{prefix} ({source_id}): acquisition_status '{status}' not in "
                f"{sorted(ALLOWED_ACQUISITION_STATUS)}"
            )

        expected_fields = entry["expected_fields"]
        if not isinstance(expected_fields, list):
            errors.append(
                f"{prefix} ({source_id}): expected_fields must be a list"
            )
        elif not all(isinstance(f, str) for f in expected_fields):
            errors.append(
                f"{prefix} ({source_id}): expected_fields must contain only strings"
            )

    return errors


def assert_valid_sources_manifest(manifest: dict[str, Any]) -> None:
    """Raise ValueError if the manifest fails validation."""
    errors = validate_sources_manifest(manifest)
    if errors:
        message = "Sources manifest validation failed:\n" + "\n".join(
            f"  - {e}" for e in errors
        )
        raise ValueError(message)
