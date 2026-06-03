# Phase 6F-data — Data acquisition plan (M33 physical τ-map inputs)

**Status:** Data-readiness phase only — **no τ reconstruction**, **no new maps**, **no deflection/lensing runs**.

**Branch:** `feature/phase6f-data-acquisition-provenance`

**Prerequisites satisfied:** Phase 6F design merged to `main` (PR #1, merge `27ab3d61`).

**Blocks:** Phase 6F-impl (mass-constrained τ reconstruction) until all gates in `docs/phase6f_data_provenance_checklist.md` pass.

---

## 1. Purpose

Catalog external 2D baryonic and geometry products needed to implement the pre-registered protocol in `docs/phase6f_mass_constrained_tau_map_protocol.md`. This phase **documents** sources, units, coordinates, acquisition paths, and readiness gates. It does **not** download cubes, fabricate pixels, or run fit scripts.

**Claim posture unchanged:** Phase 4A/4B maps remain axisymmetric scaffolds; deflection remains `normalized_proxy`; no DM disproof; no M33 lensing confirmation.

---

## 2. Required data products (minimum set)

| Category | Role in Phase 6F-impl | In repo today? |
|----------|----------------------|--------------|
| **2D HI surface-density map** \(\Sigma_{\mathrm{HI}}(x,y)\) | Gas mass geometry; \(\mathcal{L}_{\mathrm{mass}}\) | **No** — 1D Table 1 averages only |
| **Stellar surface-brightness or mass map** \(\Sigma_*(x,y)\) | Disk geometry; \(\mathcal{L}_{\mathrm{mass}}\) | **No** — 1D \(\Sigma_*\) in Table 1 |
| **Inclination / PA / tilted-ring geometry** | Deprojection, \(R(x,y)\), sky projection | **Partial** — radial tilted-ring CSV + Phase 4B locked ranges |
| **Uncertainty maps** | Weighting rotation and mass terms | **Partial** — radial \(v_{\mathrm{err}}\) only |
| **2D velocity field** (recommended) | Azimuthal checks; holdout design | **No** |
| **CO / H₂ map** (optional) | Molecular gas geometry | **No** |

See `docs/phase6f_data_requirements_for_physical_tau_map.md` for scientific rationale.

---

## 3. Candidate datasets (catalog)

### 3.1 Primary — Corbelli et al. 2014 (recommended default stack)

| Field | Value |
|-------|-------|
| **Source paper** | Corbelli, E.; Thilker, D. A.; Zschaechner, L.; et al. 2014, *A&A* **572**, A23 |
| **DOI** | [10.1051/0004-6361/201424033](https://doi.org/10.1051/0004-6361/201424033) |
| **arXiv** | [1409.2665](https://arxiv.org/abs/1409.2665) |
| **Archive / access** | A&A article + online data (tables, figures); author HI products cited in paper (VLA+GBT); PDF in repo: `data/raw/downloads/corbelli2014_aa24033_14.pdf` |
| **Repo extracts (1D / geometry)** | `data/raw/extracted/corbelli2014_table1_raw.csv`; `data/raw/extracted/corbelli2014_tilted_ring_geometry_model_shape.csv`; `data/processed/m33_rotation.csv` |

#### 3.1a Corbelli 2014 — VLA+GBT HI moment-0 (2D \(\Sigma_{\mathrm{HI}}\))

| Attribute | Detail |
|-----------|--------|
| **Data product type** | HI column-density / surface-density map (moment-0); associated cubes at ~20″ and ~130″ resolution per paper |
| **Units** | Typically \(M_\odot\,\mathrm{pc}^{-2}\) or equivalent HI mass surface density; confirm from FITS header or table caption |
| **Coordinate system** | Equatorial (RA/Dec) or galactic; WCS in FITS if cube/map obtained |
| **Angular resolution** | ~20″ (VLA-dominated inner) and ~130″ (GBT-dominated outer) — **two products**; pick one primary + document merge policy |
| **Spatial coverage** | M33 disk to \(\gtrsim 23\,\mathrm{kpc}\) (paper Table 1 / Fig. 3 context) |
| **Uncertainty** | Beam / noise maps often in cube products; not in repo |
| **License / access** | A&A article; data may require author request or CDS/VizieR — **verify before download** |
| **Usability** | **Needs conversion** — not in repo; must register `source_id`, checksum, WCS alignment to Phase 4B grid |

#### 3.1b Corbelli 2014 — BVIgi stellar mass surface-density map

| Attribute | Detail |
|-----------|--------|
| **Data product type** | 2D stellar mass surface density from multi-band SBF + population synthesis (paper Sect. 3–4) |
| **Units** | \(M_\odot\,\mathrm{pc}^{-2}\) (paper convention) |
| **Coordinate system** | Same as HI products when from same reduction |
| **Angular resolution** | Matched to stellar mass analysis scale in paper (~arcsec; confirm from figure caption) |
| **Spatial coverage** | M33 disk; compare to HI mask |
| **Uncertainty** | Population-synthesis and distance uncertainties — often not a per-pixel map |
| **License / access** | Same as 3.1a |
| **Usability** | **Needs conversion** — 1D \(\Sigma_*\) in Table 1 is **not** a substitute |

#### 3.1c Corbelli 2014 — HI velocity field (moment-1)

| Attribute | Detail |
|-----------|--------|
| **Data product type** | 2D line-of-sight velocity field from tilted-ring / cube analysis |
| **Units** | km s\(^{-1}\) (heliocentric or barycentric — document) |
| **Coordinate system** | As HI maps |
| **Angular resolution** | Same beam family as moment-0 |
| **Spatial coverage** | HI-detected disk |
| **Uncertainty** | Moment-1 error maps sometimes available from cubes |
| **License / access** | Same as 3.1a |
| **Usability** | **Needs conversion** — strongly recommended for 6F-impl holdout design |

#### 3.1d Corbelli 2014 — Tilted-ring / warp geometry (partially in repo)

| Attribute | Detail |
|-----------|--------|
| **Data product type** | Radial tilted-ring model: \(i(R)\), PA\((R)\), center, systemic \(v\) |
| **Units** | deg (angles); kpc (radii); km s\(^{-1}\) |
| **Coordinate system** | Disk-plane / model-centric radii |
| **Angular resolution** | 12 rings, 0.8–23 kpc in repo extract |
| **Spatial coverage** | Radial model; warp noted in paper Sect. 4.1 |
| **Uncertainty** | Ranges in Phase 4B metadata: \(i \in [49°,57°]\), PA \(\in [-16°,23°]\) (global envelope; per-ring in CSV) |
| **License / access** | Extracted from published figure/table — documented in manifest |
| **Usability** | **Partially direct** — `corbelli2014_tilted_ring_geometry_model_shape.csv`; **needs extension** to 2D grid + WCS for mass maps |

**Phase 4B reference:** `outputs/tables/phase4b_tau_projection_metadata.csv` — geometry locked for **existing** axisymmetric map only; does not certify 2D mass-map alignment.

---

### 3.2 Reference / cross-check — THINGS (Walter et al. 2008)

| Field | Value |
|-------|-------|
| **Source paper** | Walter, F.; Brinks, E.; de Blok, W. J. G.; et al. 2008, *AJ* **136**, 2563 |
| **DOI** | [10.1088/0004-6256/136/6/2563](https://doi.org/10.1088/0004-6256/136/6/2563) |
| **Data product type** | THINGS HI data release — cubes, moment maps, rotation curves |
| **Units** | Jy/beam, km s\(^{-1}\), or \(M_\odot\,\mathrm{pc}^{-2}\) after conversion |
| **Coordinate system** | Equatorial WCS in FITS |
| **Angular resolution** | ~5–10″ (galaxy-dependent; M33 included) |
| **Spatial coverage** | M33 in sample |
| **Uncertainty** | Noise / rms in cubes |
| **License / access** | Public THINGS release (NRAO/IRAM pages; confirm current mirror) |
| **Usability** | **Reference / optional primary** — use only if beam and flux calibration traceability to Corbelli 2014 is documented; **not** mixed silently with Corbelli maps |

---

### 3.3 Reference / cross-check — Little THINGS (Hunter et al. 2012)

| Field | Value |
|-------|-------|
| **Source paper** | Hunter, D. A.; Elmegreen, B. G.; Baker, A. J.; et al. 2012, *AJ* **144**, 134 |
| **DOI** | [10.1088/0004-6256/144/5/134](https://doi.org/10.1088/0004-6256/144/5/134) |
| **Data product type** | Higher-resolution HI for subset of THINGS galaxies |
| **Units** | As THINGS family |
| **Coordinate system** | FITS WCS |
| **Angular resolution** | Finer than THINGS where available (**verify M33 inclusion**) |
| **Spatial coverage** | Subset of THINGS |
| **Uncertainty** | Cube noise |
| **License / access** | Public release |
| **Usability** | **Reference only** unless M33 product confirmed and acquisition logged |

---

### 3.4 Optional — CO / molecular gas

#### Gratier et al. 2010 (FCRAO / IRAM M33 CO)

| Field | Value |
|-------|-------|
| **Source paper** | Gratier, P.; et al. 2010, *A&A* **522**, A3 (and related M33 CO papers cited in Corbelli 2014) |
| **DOI** | [10.1051/0004-6361/201014843](https://doi.org/10.1051/0004-6361/201014843) |
| **Data product type** | CO(1–0) / CO(2–1) intensity or \(H_2\) surface density maps |
| **Units** | K km s\(^{-1}\) pc\(^{-2}\) or \(M_\odot\,\mathrm{pc}^{-2}\) via \(X_{\mathrm{CO}}\) |
| **Coordinate system** | Equatorial / galactic — confirm per file |
| **Angular resolution** | FCRAO ~45″; IRAM finer where mapped |
| **Spatial coverage** | Inner/mid disk (CO-bright regions) |
| **Uncertainty** | Often not per-pixel |
| **License / access** | Journal + data releases |
| **Usability** | **Optional** — Phase 6F minimum set does **not** require CO; if used, document \(X_{\mathrm{CO}}\) and alignment |

#### HERACLES-style CO surveys

| Field | Value |
|-------|-------|
| **Source paper** | Leroy, A. K.; et al. 2009, *AJ* **137**, 4670 (HERACLES) |
| **DOI** | [10.1088/0004-6256/137/6/4670](https://doi.org/10.1088/0004-6256/137/6/4670) |
| **Data product type** | CO(3–2) / \(H_2\) for nearby galaxies |
| **Usability** | **Reference only** for M33 unless verified product exists in release |

---

### 3.5 In-repo products (not substitutes for 2D maps)

| Product | Path | Usability for 6F-impl |
|---------|------|------------------------|
| Radial rotation + baryonic columns | `data/processed/m33_rotation.csv` | **Direct** for \(\mathcal{L}_{\mathrm{rotation}}\) radial term |
| Table 1 raw | `data/raw/extracted/corbelli2014_table1_raw.csv` | **Reference** — 1D \(\Sigma_{\mathrm{HI}}\), \(\Sigma_*\) |
| Tilted-ring CSV | `data/raw/extracted/corbelli2014_tilted_ring_geometry_model_shape.csv` | **Direct** (geometry); extend to 2D |
| Phase 4A τ map | `outputs/maps/phase4a_tau_2d_map.npz` | **Read-only baseline** — not mass-constrained |
| Phase 4B sky τ | Phase 4B outputs | **Read-only** — no re-fit in 6F-data |
| López Fune 2017 extracts | `data/raw/extracted/lopez_fune_*` | **Comparison only** — not τ input |

---

## 4. Acquisition strategy (ordered)

1. **Confirm primary stack:** Corbelli et al. 2014 2D HI + stellar mass (+ velocity field if available) from official channels (A&A, CDS, or documented author archive).
2. **Record provenance before any processing:** URL, retrieval date, checksum, file size, license note → `data/raw/sources_manifest.yaml` + `docs/data_sources.md`.
3. **Geometry lock:** Reconcile tilted-ring CSV with map WCS; document distance \(D=840\,\mathrm{kpc}\) (Corbelli 2014 assumption) and any updates.
4. **Unit conversion path:** Document FITS BUNIT → \(M_\odot\,\mathrm{pc}^{-2}\); velocity units; mask definitions.
5. **Cross-check (optional):** THINGS moment-0 vs Corbelli HI — **comparison report only**, not merged without gate sign-off.
6. **CO (optional):** Acquire only if Phase 6F-impl scope explicitly adds molecular term.

**No step in this list runs τ reconstruction or deflection scripts.**

---

## 5. Planned manifest `source_id`s (register when files exist)

| `source_id` | Status | Notes |
|-------------|--------|-------|
| `corbelli2014_hi_2d_map` | planned | Primary HI \(\Sigma\) map |
| `corbelli2014_stellar_mass_2d_map` | planned | Primary \(\Sigma_*\) map |
| `corbelli2014_hi_velocity_field_2d` | planned | Recommended moment-1 |
| `corbelli2014_hi_cube_20as` | planned | Optional cube provenance |
| `corbelli2014_hi_cube_130as` | planned | Optional outer-disk cube |
| `things_m33_hi_reference` | planned | Cross-check only |
| `gratier2010_m33_co_optional` | planned | Optional CO |

Do **not** mark `acquisition_status: processed` until checksum + validation scripts pass.

---

## 6. Future command placeholders (not implemented)

```bash
# Phase 6F-data — acquisition (future; no scripts in this phase)
# python scripts/acquire_corbelli2014_hi_2d_map.py --manifest data/raw/sources_manifest.yaml
# python scripts/acquire_corbelli2014_stellar_mass_2d_map.py --manifest data/raw/sources_manifest.yaml
# python scripts/validate_phase6f_baryonic_maps.py --hi ... --stars ... --geometry ...
# python scripts/run_phase6f_data_readiness_audit.py

# Phase 6F-impl — blocked until checklist gates pass
# python scripts/run_phase6f_mass_constrained_tau_map.py
# python scripts/run_phase6f_decision_gate_audit.py
```

---

## 7. Related documents

| Document | Role |
|----------|------|
| `docs/phase6f_data_provenance_checklist.md` | Pass/fail gates |
| `outputs/reports/phase6f_data_readiness_report.md` | Executive readiness snapshot |
| `docs/phase6f_data_requirements_for_physical_tau_map.md` | Scientific requirements |
| `docs/phase6f_mass_constrained_tau_map_protocol.md` | Fit protocol (6F-impl) |

---

## 8. Explicit non-goals (this phase)

- Implement \(\mathcal{L}_{\mathrm{total}}\) or τ reconstruction
- Generate `phase6f_*` τ maps or figures
- Run Phase 5A deflection or lensing proxies on new data
- Modify Phase 3–5 numerical outputs or `src/` model code
- Weaken claim boundaries in manuscript or audits
