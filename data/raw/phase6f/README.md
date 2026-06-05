# Phase 6F raw data staging (`data/raw/phase6f/`)

**Purpose:** Verified manifests and **small** reference files for mass-constrained τ-map inputs.

**Not in scope:** τ reconstruction, deflection/lensing runs, or fabricated placeholders.

## Layout

| Path | Role |
|------|------|
| `manifest/phase6f_source_registry.yaml` | Machine-readable source registry |
| `CHECKSUMS.sha256` | SHA-256 for committed files |
| `geometry/` | Tilted-ring geometry (Corbelli 2014 extract) |
| `reference/gratier2010_vla_hi_12sec/` | **Reference-only** VLA HI moment maps (Gratier et al. 2010) |
| `primary/corbelli2014_hi/` | **Primary** Corbelli 2014 VLA+GBT HI Σ (create on receipt) |
| `primary/corbelli2014_stellar_mass/` | **Primary** BVIgi stellar map (create on receipt) |
| `primary/corbelli2014_velocity_field/` | Optional 2D velocity field (create on receipt) |
| `primary/corbelli2014_uncertainty_masks/` | Optional masks/noise (create on receipt) |
| `primary/CHECKSUMS.sha256` | SHA-256 for primary FITS only |

## Primary vs reference

| Tier | Products | In repo? |
|------|----------|----------|
| **Primary (required for 6F-impl)** | Corbelli et al. 2014 VLA+GBT HI Σ map; BVIgi stellar mass Σ map | **No** |
| **Reference (optional cross-check)** | Gratier 2010 VLA-only HI moment FITS | **Yes** (3 files) |
| **Geometry (partial)** | Corbelli 2014 tilted-ring CSV | **Yes** (copy) |

Phase 6F-impl remains **blocked** until primary products are acquired, validated, and gates G1–G8 pass (`docs/phase6f_primary_data_receipt_protocol.md`).

## Validate primary inventory

```bash
python scripts/validate_phase6f_primary_maps.py
python scripts/update_phase6f_primary_checksums.py
```

## Verify checksums

```bash
cd data/raw/phase6f
shasum -a 256 -c CHECKSUMS.sha256
```

## Documentation

- `docs/phase6f_source_manifest.md`
- `docs/phase6f_dataset_access_notes.md`
- `outputs/reports/phase6f_source_acquisition_status.md`
