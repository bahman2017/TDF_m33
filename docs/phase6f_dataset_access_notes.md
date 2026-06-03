# Phase 6F — Dataset access notes

**Purpose:** Reproducible or manual acquisition steps for each 2D product. **No fabricated checksums** — SHA-256 recorded only for files actually present under `data/raw/phase6f/`.

**Claim control unchanged:** No τ reconstruction; no deflection; 6F-impl blocked until primary files verified.

---

## 1. Corbelli et al. 2014 — primary HI (VLA+GBT)

### Bibliography

- **Paper:** *A&A* **572**, A23 (2014)
- **DOI:** [10.1051/0004-6361/201424033](https://doi.org/10.1051/0004-6361/201424033)
- **arXiv:** [1409.2665](https://arxiv.org/abs/1409.2665)

### What the paper provides publicly

- Full text, figures, and **Table 1** (rotation curve, 1D Σ_HI, Σ_*) via A&A online data
- Appendices A–B (electronic) — tilted-ring methodology
- **No direct FITS download link** for the combined VLA+GBT datacube on the publisher page (verified 2026-06-03)

### Recommended acquisition path (manual)

1. **Author / collaboration request** — primary channel for Corbelli 2014 combined HI cubes and moment maps used in the dynamical analysis. Corresponding authors from the paper: E. Corbelli (INAF), D. A. Thilker (JHU).
2. **Document receipt:** save email metadata, file names, and SHA-256 in `docs/extraction_log.md` and update `phase6f_source_registry.yaml`.
3. **On ingest:** store under `data/raw/phase6f/primary/corbelli2014_hi/` (directory to be created at acquisition time — **not** pre-created with placeholders).
4. **Validate:** compare azimuthally averaged Σ_HI to Table 1 (`corbelli2014_table1_raw.csv`) within stated tolerance before marking G2 pass.

### Automated download

**Not available** for the Corbelli 2014 VLA+GBT primary product.

### Do not substitute

Gratier et al. (2010) VLA-only FITS in this repo (`reference/gratier2010_vla_hi_12sec/`) lack GBT total-power short spacing. Corbelli 2014 explicitly combines VLA with GBT for the outer disk.

---

## 2. Corbelli et al. 2014 — primary stellar mass (BVIgi)

### Bibliography

Same paper as §1.

### Public availability

- Stellar mass map shown in paper Fig. 2; radial profiles in Fig. 10 / Table 1
- **No public FITS URL** identified on A&A, CDS VizieR (J/A+A/572/A23), or arXiv (2026-06-03 search)

### Recommended acquisition path

1. **Author request** to Corbelli / Thilker for the BVIgi stellar mass surface-density FITS (or equivalent) used in Figs. 2 and 12.
2. Request **WCS**, units (M_⊙ pc⁻²), and mask if applicable.
3. Store under `data/raw/phase6f/primary/corbelli2014_stellar_mass/` when received.
4. **Validate:** radial average vs Table 1 Σ_* columns.

### Automated download

**Not available.**

### Alternative (not primary)

Re-deriving Σ_* from LGS/SDSS mosaics would be a **new reduction**, not the Corbelli 2014 map — out of scope unless explicitly pre-registered.

---

## 3. Corbelli et al. 2014 — HI velocity field

Acquire together with primary HI cube (moment-1) or from tilted-ring pipeline outputs described in Appendix A.

**Automated:** No (same as §1).

---

## 4. Tilted-ring geometry (in repo)

### Canonical extract

`data/raw/extracted/corbelli2014_tilted_ring_geometry_model_shape.csv`

### Phase 6F staging copy

```bash
# Already copied; verify checksum:
cd data/raw/phase6f
shasum -a 256 -c CHECKSUMS.sha256
```

**Provenance:** Digitized from Corbelli 2014 Fig. 3 (model-shape method); documented in Phase 4B metadata.

---

## 5. Gratier et al. 2010 — reference VLA HI (automated)

### Bibliography

- Gratier, P.; et al. 2010, *A&A* **522**, A3
- **DOI:** [10.1051/0004-6361/201014843](https://doi.org/10.1051/0004-6361/201014843)

### Data page

[https://perso.astrophy.u-bordeaux.fr/~pgratier/data/](https://perso.astrophy.u-bordeaux.fr/~pgratier/data/)

**License:** Page states data are free to use with reference to Gratier et al. (2010).

**Note:** FITS moved to `fits/` subdirectory (older bare URLs return 404).

### Reproducible download (12″ products committed)

```bash
mkdir -p data/raw/phase6f/reference/gratier2010_vla_hi_12sec
BASE=https://perso.astrophy.u-bordeaux.fr/~pgratier/data/fits
for f in M33_HI_12sec-area.fits M33_HI_12sec-cent.fits M33_HI_12sec-noise.fits; do
  curl -L -o "data/raw/phase6f/reference/gratier2010_vla_hi_12sec/$f" "$BASE/$f"
done
cd data/raw/phase6f && shasum -a 256 -c CHECKSUMS.sha256
```

### Full archive (optional, not committed)

```bash
curl -L -O https://perso.astrophy.u-bordeaux.fr/~pgratier/data/fits/M33_HI.tar.gz
# ~24 MB gzip; 15 FITS at 12/17/25 arcsec resolutions
```

### Unit / coordinate notes (verified from committed area map)

| Header keyword | Value |
|----------------|-------|
| BUNIT | `T(K)` |
| BMAJ | ~0.00333 deg (~12″) |
| CDELT1/2 | ~0.00111 deg (~4″ pixels) |
| CRVAL1/2 | 23.4625°, 30.6597° (M33) |
| NAXIS1×NAXIS2 | 811 × 1201 |

Convert to N_HI or M_⊙ pc⁻² before entering L_mass (future validation script).

---

## 6. IRAM LP006 — optional CO(2-1) (automated, not committed)

### Bibliography

- Druard, C.; et al. 2014, *A&A* **567**, A118
- **DOI:** [10.1051/0004-6361/201423682](https://doi.org/10.1051/0004-6361/201423682)
- Gratier et al. 2010 (observing strategy)

### Portal

[https://iram-institute.org/science-portal/proposals/lp/completed/lp006-the-complete-co2-1-map-of-m33/](https://iram-institute.org/science-portal/proposals/lp/completed/lp006-the-complete-co2-1-map-of-m33/)

### Direct files (2026-06-03 verified)

| File | Size | URL |
|------|------|-----|
| `ico.fits` | ~3.7 MB | `https://www.iram.fr/ILPA/LP006/ico.fits` |
| `rms.fits` | ~3.7 MB | `https://www.iram.fr/ILPA/LP006/rms.fits` |
| `cube-M33CO2-1-3_HIwin.fits` | ~571 MB | `https://www.iram.fr/ILPA/LP006/cube-M33CO2-1-3_HIwin.fits` |

```bash
# Integrated map only (optional local staging — do not commit without updating CHECKSUMS)
mkdir -p data/raw/phase6f/optional/iram_lp006
curl -L -o data/raw/phase6f/optional/iram_lp006/ico.fits \
  https://www.iram.fr/ILPA/LP006/ico.fits
shasum -a 256 data/raw/phase6f/optional/iram_lp006/ico.fits >> docs/extraction_log.md
```

**License:** IRAM LP archive; cite Druard et al. (2014) and Gratier et al. (2010).

---

## 7. THINGS — not applicable to M33

- **DOI:** [10.1088/0004-6256/136/6/2563](https://doi.org/10.1088/0004-6256/136/6/2563)
- **Archive:** [https://www2.mpia-hd.mpg.de/THINGS/Data.html](https://www2.mpia-hd.mpg.de/THINGS/Data.html)
- **M33:** Not in the 34-galaxy sample — do not attempt THINGS download for this project.

---

## 8. Post-acquisition checklist (primary stack)

When Corbelli primary files arrive:

- [ ] Update `phase6f_source_registry.yaml` (`acquisition_status`, `repo_path`, `sha256`)
- [ ] Append row to `CHECKSUMS.sha256`
- [ ] Log in `docs/extraction_log.md`
- [ ] Re-run gates in `docs/phase6f_data_provenance_checklist.md`
- [ ] Update `outputs/reports/phase6f_source_acquisition_status.md`

**Only then** consider opening Phase 6F-impl branch.

---

## 9. Future script placeholders (not implemented)

```bash
# python scripts/acquire_phase6f_primary_corbelli2014.py  # requires author-provided paths
# python scripts/verify_phase6f_checksums.py --root data/raw/phase6f
# python scripts/validate_phase6f_baryonic_maps.py
```
