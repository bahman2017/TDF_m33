# Phase 6F-source — Acquisition status report

**Report type:** Verified source manifests and selective file staging — **not** τ reconstruction  
**Date:** 2026-06-03  
**Branch:** `feature/phase6f-source-acquisition-manifest`  
**Baseline:** `main` after Phase 6F-data (PR #2)

---

## Executive summary

| Question | Answer |
|----------|--------|
| Primary Corbelli 2014 HI Σ map in repo? | **No** |
| Primary Corbelli 2014 stellar Σ map in repo? | **No** |
| Reference HI FITS committed? | **Yes** — Gratier 2010 VLA 12″ (3 files, checksums verified) |
| Geometry CSV staged? | **Yes** — tilted-ring copy with checksum |
| Phase 6F-impl unblocked? | **No** |
| τ / deflection runs? | **None** |

**Bottom line:** Source manifests and access paths are documented; **primary stack acquisition remains the blocker**.

---

## File inventory (`data/raw/phase6f/`)

| Path | Status | SHA-256 recorded | Primary gate? |
|------|--------|------------------|---------------|
| `geometry/corbelli2014_tilted_ring_geometry_model_shape.csv` | Committed | Yes | Partial (G4) |
| `reference/gratier2010_vla_hi_12sec/M33_HI_12sec-area.fits` | Committed | Yes | **No** (reference) |
| `reference/gratier2010_vla_hi_12sec/M33_HI_12sec-cent.fits` | Committed | Yes | **No** |
| `reference/gratier2010_vla_hi_12sec/M33_HI_12sec-noise.fits` | Committed | Yes | **No** |
| `primary/corbelli2014_hi/` | **Not created** | — | Required |
| `primary/corbelli2014_stellar_mass/` | **Not created** | — | Required |

Verify:

```bash
cd data/raw/phase6f && shasum -a 256 -c CHECKSUMS.sha256
```

---

## Source registry status

Machine-readable: `data/raw/phase6f/manifest/phase6f_source_registry.yaml`

| `source_id` | Tier | `acquisition_status` | Automated download |
|-------------|------|----------------------|--------------------|
| `corbelli2014_hi_2d_vla_gbt` | primary_required | not_acquired | No |
| `corbelli2014_stellar_mass_bvigi_2d` | primary_required | not_acquired | No |
| `corbelli2014_hi_velocity_field_2d` | primary_recommended | not_acquired | No |
| `corbelli2014_tilted_ring_geometry` | geometry_partial | acquired | N/A |
| `gratier2010_vla_hi_12sec_*` (×3) | reference_only | acquired_reference | Yes |
| `iram_lp006_co21_integrated` | optional | not_acquired | Yes (URL live) |
| `things_survey` | reference_not_applicable | n/a | N/A |

Human-readable catalog: `docs/phase6f_source_manifest.md`  
Access procedures: `docs/phase6f_dataset_access_notes.md`

---

## Provenance gate matrix (unchanged blocking)

From `docs/phase6f_data_provenance_checklist.md`:

| Gate | Status after this phase | Notes |
|------|-------------------------|-------|
| G1 Source traceability | **PARTIAL** | Reference FITS + geometry traced; primary missing |
| G2 Unit conversion | **FAIL** | Gratier BUNIT=T(K); primary Σ path undefined |
| G3 Coordinate compatibility | **FAIL** | No aligned primary HI + stellar grid |
| G4 Disk geometry | **PARTIAL** | CSV only |
| G5 Uncertainties | **PARTIAL** | Gratier noise map reference; no primary |
| G6 Reproducible acquisition | **PARTIAL** | Gratier curl documented; primary manual |
| G7 No hand-edited maps | **PASS** | Downloads only; no pixel edits |
| G8 Claim boundaries | **PASS** | No τ / deflection |

**Overall:** **NOT READY** for Phase 6F-impl.

---

## Automated download verification (2026-06-03)

| URL | HTTP | Size | Committed? |
|-----|------|------|------------|
| `…/gratier/data/fits/M33_HI_12sec-area.fits` | 200 | 3.72 MB | Yes |
| `…/gratier/data/fits/M33_HI_12sec-cent.fits` | 200 | 3.72 MB | Yes |
| `…/gratier/data/fits/M33_HI_12sec-noise.fits` | 200 | 3.72 MB | Yes |
| `https://www.iram.fr/ILPA/LP006/ico.fits` | 200 | 3.72 MB | No (optional) |
| `https://www.iram.fr/ILPA/LP006/cube-…fits` | 200 | ~571 MB | No (too large) |
| Legacy Gratier URL without `fits/` | 404 | — | Use `fits/` path |

---

## Next actions (ordered)

1. Request Corbelli 2014 **VLA+GBT** HI and **BVIgi stellar** FITS from authors.  
2. On receipt: ingest under `data/raw/phase6f/primary/`, update registry + CHECKSUMS.  
3. Implement `validate_phase6f_baryonic_maps.py` (future) — radial Table 1 cross-check.  
4. Re-evaluate G1–G6; publish sign-off in this report when primary stack passes.

---

## Claim control

- Phase 4A/4B maps remain axisymmetric scaffolds.  
- Deflection remains `normalized_proxy`.  
- No dark-matter disproof; no M33 lensing confirmation.  
- Gratier reference files do **not** imply mass-constrained τ readiness.
