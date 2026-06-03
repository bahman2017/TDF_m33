# Phase 6F — Source manifest (2D τ-map inputs)

**Status:** Source acquisition and verified manifests — **not** τ reconstruction.

**Registry (machine-readable):** `data/raw/phase6f/manifest/phase6f_source_registry.yaml`

**Checksums (committed files):** `data/raw/phase6f/CHECKSUMS.sha256`

**Impl blocked:** `primary_stack_ready: false` until Corbelli 2014 **primary** HI + stellar maps are acquired and gates pass.

---

## 1. Tier definitions

| Tier | Meaning | Satisfies 6F-impl minimum? |
|------|---------|------------------------------|
| `primary_required` | Must acquire for mass-constrained τ-map | Required |
| `primary_recommended` | Strongly advised (velocity field) | Recommended |
| `geometry_partial` | Disk orientation; in repo but incomplete for 2D | Partial |
| `reference_only` | Real data for validation scripts; **not** primary stack | No |
| `optional` | CO / H₂ if molecular term added | Optional |
| `reference_not_applicable` | Catalogued; not usable for M33 | No |

---

## 2. Primary stack (NOT in repo)

### 2.1 Corbelli et al. 2014 — VLA+GBT HI surface-density map

| Field | Value |
|-------|-------|
| **Paper** | Corbelli, E.; Thilker, D. A.; Zschaechner, L.; et al. 2014, *A&A* **572**, A23 |
| **DOI** | [10.1051/0004-6361/201424033](https://doi.org/10.1051/0004-6361/201424033) |
| **URL** | [A&A full text](https://www.aanda.org/articles/aa/full_html/2014/12/aa24033-14/aa24033-14.html) |
| **VizieR** | J/A+A/572/A23 (tables; **no** public 2D FITS map identified) |
| **`source_id`** | `corbelli2014_hi_2d_vla_gbt` |
| **Data product** | Combined VLA + GBT 21 cm HI datacube / moment-0 Σ_HI |
| **Expected file name** | Author-dependent (FITS cube or moment map) |
| **Format** | FITS (+ WCS) |
| **Units** | N_HI or M_⊙ pc⁻² (confirm on receipt) |
| **Coordinates** | Equatorial WCS |
| **Resolution** | ~20″ (VLA) + ~130″ (GBT) merged per paper |
| **Coverage** | Full M33 HI disk (~23 kpc) |
| **Uncertainty** | Noise / rms from reduction |
| **License / access** | A&A; 2D products **not** linked on publisher site |
| **Download** | Manual / author request |
| **Automated** | **No** |
| **Repo status** | `not_acquired` |
| **Usability** | **Primary target** — needs conversion to repo Σ standard |

### 2.2 Corbelli et al. 2014 — BVIgi stellar mass map

| Field | Value |
|-------|-------|
| **`source_id`** | `corbelli2014_stellar_mass_bvigi_2d` |
| **Data product** | 2D stellar mass surface density (pixel-SED; LGS + SDSS + outer Spitzer/deep fields) |
| **Expected file name** | Not published under fixed public name |
| **Format** | FITS or author array |
| **Units** | M_⊙ pc⁻² |
| **Coordinates** | Analysis grid aligned with HI (confirm on receipt) |
| **Resolution** | Optical mosaic pixel scale (arcsec; Sect. 3.1) |
| **Coverage** | Optical disk + extrapolated outer disk |
| **Uncertainty** | ~0.06–0.1 dex random (paper); rarely a per-pixel FITS |
| **License / access** | **No public URL found** — contact authors |
| **Download** | Author request (Corbelli / Thilker) |
| **Automated** | **No** |
| **Repo status** | `not_acquired` |
| **Usability** | **Primary target** — 1D Table 1 **not** a substitute |

### 2.3 Corbelli et al. 2014 — HI velocity field (recommended)

| Field | Value |
|-------|-------|
| **`source_id`** | `corbelli2014_hi_velocity_field_2d` |
| **Data product** | Moment-1 / tilted-ring 2D velocity |
| **Format** | FITS |
| **Units** | km s⁻¹ |
| **Download** | Same channel as primary HI |
| **Automated** | **No** |
| **Repo status** | `not_acquired` |

---

## 3. Geometry (partial — in repo)

### Corbelli 2014 tilted-ring model-shape

| Field | Value |
|-------|-------|
| **`source_id`** | `corbelli2014_tilted_ring_geometry` |
| **File** | `data/raw/phase6f/geometry/corbelli2014_tilted_ring_geometry_model_shape.csv` |
| **Format** | CSV |
| **Units** | deg; kpc |
| **Coverage** | 12 rings, 0.8–23 kpc |
| **SHA-256** | `7060a0ea…0fc1c` (see CHECKSUMS) |
| **License** | Published figure extract; same paper DOI |
| **Download** | Copied from `data/raw/extracted/` (canonical) |
| **Automated** | N/A (in-repo) |
| **Usability** | **Direct** for radial geometry; **needs** 2D extension with map WCS |

---

## 4. Reference HI (in repo — does NOT unblock 6F-impl)

### Gratier et al. 2010 — VLA-only HI @ 12″

Corbelli 2014 states their cubes combine VLA with GBT total power; Gratier et al. (2010) is an **independent VLA-only** reduction. Committed for provenance practice and future validation scripts only.

| `source_id` | File | Size | SHA-256 (prefix) | Automated curl |
|-------------|------|------|------------------|--------------|
| `gratier2010_vla_hi_12sec_area` | `M33_HI_12sec-area.fits` | 3.72 MB | `c5e7a8d2…` | Yes |
| `gratier2010_vla_hi_12sec_cent` | `M33_HI_12sec-cent.fits` | 3.72 MB | `181d76d1…` | Yes |
| `gratier2010_vla_hi_12sec_noise` | `M33_HI_12sec-noise.fits` | 3.72 MB | `2e2b186b…` | Yes |

**Verified header (area map):** BUNIT=`T(K)`; BMAJ≈12″; CDELT≈4″; 811×1201; CRVAL (23.46°, 30.66°).

**DOI:** [10.1051/0004-6361/201014843](https://doi.org/10.1051/0004-6361/201014843)

**License note:** [Gratier data page](https://perso.astrophy.u-bordeaux.fr/~pgratier/data/) — free use with citation.

**Full tarball (not committed):** `M33_HI.tar.gz` (~24 MB, 15 FITS) — `https://perso.astrophy.u-bordeaux.fr/~pgratier/data/fits/M33_HI.tar.gz`

---

## 5. Optional CO (not in repo)

### IRAM LP006 — Druard et al. 2014 CO(2-1)

| Field | Value |
|-------|-------|
| **`source_id`** | `iram_lp006_co21_integrated` |
| **DOI** | [10.1051/0004-6361/201423682](https://doi.org/10.1051/0004-6361/201423682) |
| **Portal** | [IRAM LP006](https://iram-institute.org/science-portal/proposals/lp/completed/lp006-the-complete-co2-1-map-of-m33/) |
| **Files** | `ico.fits` (3.7 MB), `rms.fits` (3.7 MB), `cube-M33CO2-1-3_HIwin.fits` (~571 MB) |
| **URL base** | `https://www.iram.fr/ILPA/LP006/` |
| **Units** | K km s⁻¹ (T_a*); convert per paper |
| **Resolution** | 12″ |
| **Coverage** | R < 7 kpc |
| **Automated** | **Yes** (wget/curl) |
| **Repo status** | `not_acquired` (large cube not committed) |

---

## 6. Reference-only / N/A

| Source | DOI | M33 usable? | Notes |
|--------|-----|-------------|-------|
| THINGS (Walter et al. 2008) | [10.1088/0004-6256/136/6/2563](https://doi.org/10.1088/0004-6256/136/6/2563) | **No** | M33 not in sample |
| Little THINGS (Hunter et al. 2012) | [10.1088/0004-6256/144/5/134](https://doi.org/10.1088/0004-6256/144/5/134) | **Verify** | Subset of THINGS galaxies |
| Kam et al. 2017 JVLA+GBT | [10.3847/1538-3881/aa79f3](https://doi.org/10.3847/1538-3881/aa79f3) | Reference | Later HI kinematics; different science goal |

---

## 7. Acquisition summary

| Category | Acquired | Primary gate |
|----------|----------|--------------|
| Corbelli VLA+GBT HI Σ | No | **Blocks 6F-impl** |
| Corbelli BVIgi stellar Σ | No | **Blocks 6F-impl** |
| Corbelli velocity 2D | No | Recommended |
| Tilted-ring geometry | Yes (CSV) | Partial |
| Gratier VLA HI reference | Yes (3 FITS) | Does not satisfy |
| IRAM CO integrated | No | Optional |

See `outputs/reports/phase6f_source_acquisition_status.md` for gate matrix.

---

## 8. Related documents

| Document | Role |
|----------|------|
| `docs/phase6f_dataset_access_notes.md` | Step-by-step download / contact instructions |
| `docs/phase6f_data_provenance_checklist.md` | Gates G1–G8 |
| `docs/phase6f_data_acquisition_plan.md` | Prior phase catalog |
