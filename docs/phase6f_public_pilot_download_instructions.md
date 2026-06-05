# Phase 6F - Public pilot manual download instructions (Tier B)

**Claim label (all products):** `PUBLIC_DATA_PILOT_NOT_CORBELLI_PRIMARY`

**Not Corbelli 2014 primary data.** These downloads cannot PASS G1/G2 Corbelli gates.

After each download:

```bash
python scripts/update_phase6f_public_pilot_checksums.py
python scripts/inventory_phase6f_public_pilot_data.py
python scripts/run_phase6f_public_pilot_gates.py
```

Never commit multi-GB cubes unless explicitly license-safe and repo-size approved.

---

## First-batch validation status (2026-05-23)

| Product | Staged locally | Registry status |
|---------|----------------|-----------------|
| IRAM LP006 CO(2-1) | **No** | `pending_download` |
| S4G / LVL IRAC 3.6 + 4.5 µm | **No** | `pending_download` |
| LGLBS HI v1.0 | **No** | `pending_download` |
| Koch 2018 HI | **No** | `pending_download` |

**Raw FITS in git:** none (checksums and inventory reports only).

After staging files under the target folders below, re-run inventory and gates. P1–P3 move to **PASS** only when FITS are present and header inspection confirms WCS (and IRAC channels for P2). P6 stays **FAIL** until validated public-pilot reprojection exists.

---

## Recommended download order

1. **IRAM LP006 CO(2-1)** -  smallest public FITS set, no login  
2. **Spitzer S4G IRAC** -  3.6 + 4.5 µm mosaics via IRSA (no login)  
3. **LGLBS HI v1.0** -  CANFAR (CADC login)  
4. **Koch 2018 HI** -  optional if rebuilding from GitHub scripts  

---

## A. LGLBS HI v1.0 / CANFAR

**Registry id:** `lglbs_hi_v1_moment0`, `lglbs_hi_v1_moment1`  
**Target folder:** `data/raw/phase6f/public_pilot/hi_lglbs/`

### Access

- Portal: https://www.lglbs.org/data  
- Data release: https://www.canfar.net/storage/vault/list/LGLBS/RELEASES/LGLBS-HI-v1.0  
- **CADC account required** -  request at https://www.canfar.net/ (no credentials in this repo)

### Expected products

| Product | Use | Typical pattern |
|---------|-----|-----------------|
| HI datacube | Full spectral stack | `*cube*.fits` |
| Moment-0 | Surface density / column proxy | `*mom0*`, `*int*` |
| Moment-1 | Velocity field | `*mom1*`, `*vel*` |
| Mask / noise | Optional uncertainty | `*mask*`, `*rms*`, `*noise*` |

### Units

Confirm `BUNIT` in FITS header (column density N_HI or brightness temperature).

### Citation

Koch et al. 2025, ApJS, 279, 35 -  https://doi.org/10.3847/1538-4365/ade0ad

### Notes

- Not the Corbelli 2014 VLA+GBT merged HI map.  
- Do not place files under `primary/corbelli2014_hi/`.

---

## B. Koch et al. 2018 HI (alternative)

**Registry id:** `koch2018_hi_products`  
**Target folder:** `data/raw/phase6f/public_pilot/hi_koch2018/`

### Access

- Scripts: https://github.com/e-koch/VLA_Lband (folder `14B-088/HI`)  
- Requires re-running reduction/imaging to produce FITS (high effort)

### Expected products

- HI cube, moment maps in Kelvin / K km/s per Koch et al. 2018, MNRAS 479, 2505

### Citation

Koch et al. 2018 -  https://ui.adsabs.harvard.edu/abs/2018MNRAS.479.2505K/abstract

---

## C. Spitzer S4G / LVL IRAC (stellar mass proxy)

**Registry ids:** `s4g_irac_36`, `s4g_irac_45`, `lvl_irac_36_45`  
**Target folders:**

- `data/raw/phase6f/public_pilot/stellar_s4g_irac/` (preferred)  
- `data/raw/phase6f/public_pilot/stellar_lvl_irac/` (fallback)

### Access

- S4G: https://irsa.ipac.caltech.edu/data/SPITZER/S4G/ -  search **M33**  
- LVL: https://irsa.ipac.caltech.edu/data/SPITZER/LVL/  
- **No login** for IRSA Atlas downloads

### Expected products

| Channel | Wavelength | Filename hints |
|---------|------------|----------------|
| IRAC ch1 | 3.6 µm | `*i1*`, `*ch1*`, `*3.6*`, `*maic.fits` |
| IRAC ch2 | 4.5 µm | `*i2*`, `*ch2*`, `*4.5*`, `*maic.fits` |

### Derivation (future PR)

Convert MJy/sr → stellar mass surface density using a **documented M/L prescription**  
(Querejeta et al. 2015; Meidt et al. 2014 style). This is **not** the Corbelli BVIgi pixel-SED map.

### Citations

- S4G: Sheth et al. 2010; Querejeta et al. 2015; dataset DOI 10.26131/IRSA425  
- LVL: Dale et al. 2009, ApJ, 703, 517

---

## D. IRAM LP006 CO(2-1)

**Registry ids:** `iram_lp006_co21_integrated`, `iram_lp006_co21_cube`  
**Target folder:** `data/raw/phase6f/public_pilot/co_iram_lp006/`

### Access

- Archive: https://www.iram.fr/ILPA/LP006/  
- Program page: https://iram-institute.org/science-portal/proposals/lp/completed/lp006-the-complete-co2-1-map-of-m33/  
- **No login** for public archive download

### Expected products

| Product | Resolution | Units |
|---------|------------|-------|
| Integrated CO(2-1) map | 12″ | K km/s (main-beam Tb integral) |
| CO(2-1) datacube | 12″, 2.6 km/s channels | K (large file) |

### H2 proxy

Use documented X_CO conversion; record assumptions in extraction log. Supports P3 only.

### Citation

Druard et al. 2014, A&A, 567, A118; Gratier et al. 2010

---

## Dry-run download planner

```bash
python scripts/download_phase6f_public_pilot_sources.py
python scripts/download_phase6f_public_pilot_sources.py --source iram_lp006_co21_integrated
```

Default is **dry-run only** -  prints URLs and target paths, no network fetch.

---

## Related documents

- `data/raw/phase6f/public_pilot/manifest/phase6f_public_pilot_source_registry.yaml`
- `docs/phase6f_public_pilot_limitations.md`
- `docs/phase6f_data_tiers.md`
