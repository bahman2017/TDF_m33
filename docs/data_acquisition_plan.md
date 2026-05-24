# M33 data acquisition plan

## 1. Purpose

This document controls **how real M33 data enter the repository**. It complements:

- `data/raw/sources_manifest_template.yaml` — machine-readable provenance registry
- `docs/data_sources.md` — human-readable transformation log and schema
- `data/processed/m33_rotation_schema_template.csv` — canonical column definitions

No numerical M33 values are stored in the repo until Phase 1C (ingestion) completes the readiness checklist at the end of this document. Phase 1B defines **which sources**, **which fields**, and **how extraction and transformation must be documented**—not the data themselves.

Every future row in `data/processed/m33_rotation.csv` must be traceable via `source_id`, extraction method, transformation notes, uncertainty handling, and an entry in `docs/data_sources.md`.

---

## 2. Source ranking

| Priority | Source | Role |
|----------|--------|------|
| **Primary** | Corbelli et al. 2014 (A&A 572, A23; DOI `10.1051/0004-6361/201424033`; manuscript `aa24033-14`) | Modern HI/gas mapping, tilted-ring \(v_{\mathrm{obs}}\), stellar mass surface density, baryonic \(v_{\mathrm{gas}}\), \(v_{\mathrm{disk}}\) (and bulge if tabulated) |
| **Baseline** | López Fune, Salucci & Corbelli 2017 | NFW/Burkert halo parameters, extended radial coverage, DM density comparison, decomposition cross-check for Phase 2 |
| **Validation** | Corbelli & Salucci 2000 | Historical 21-cm rotation curve; rising outer disk; independent check of \(v_{\mathrm{obs}}(r)\) |
| **Optional later** | HI/CO map placeholders | Phase 4 2D τ-map; FITS or survey products TBD |
| **Optional later** | Lensing limits placeholder | Phase 5 prediction vs limits |

**Why Corbelli et al. 2014 is primary:** *Dynamical signatures of a ΛCDM-halo and the distribution of the baryons in M33* ([doi.org/10.1051/0004-6361/201424033](https://doi.org/10.1051/0004-6361/201424033)) provides the most complete modern baryonic and kinematic picture of M33 for building \(v_{\mathrm{bar}}\) and the observed rotation curve on a consistent tilted-ring framework. Official PDF: save publisher file `aa24033-14.pdf` as `data/raw/downloads/corbelli2014_aa24033_14.pdf` (see `docs/extraction_log.md`).

**Why López Fune et al. 2017 is next:** It supplies standardized NFW/Burkert halo fits and an extended radial domain for **comparison baselines**, not as the TDF τ input.

**Why Corbelli & Salucci 2000 remains:** It anchors the classic outer rotation-curve rise and offers an independent legacy dataset for validation after ingestion.

---

## 3. Data components needed

| Component | Preferred source | Backup source | Extraction method | Documentation requirement |
|-----------|------------------|---------------|-------------------|---------------------------|
| `r_kpc` | corbelli_et_al_2014 | corbelli_salucci_2000 | Published radius column or derived from tilted-ring model; convert to kpc | Log distance assumption and radius definition in `data_sources.md` |
| `v_obs_kms` | corbelli_et_al_2014 | corbelli_salucci_2000 | Table or supplementary data; digitize only if no table | Cite figure/table ID; document tracer (HI) |
| `v_err_kms` | corbelli_et_al_2014 | corbelli_salucci_2000 | Published errors or propagated from cube | If null, explain in row `notes` |
| `v_gas_kms` | corbelli_et_al_2014 | lopez_fune_salucci_corbelli_2017 | Baryonic decomposition table | Document HI/H₂ treatment |
| `v_disk_kms` | corbelli_et_al_2014 | lopez_fune_salucci_corbelli_2017 | Stellar disk model velocity | Document \(M/L\) and profile |
| `v_bulge_kms` | corbelli_et_al_2014 | lopez_fune_salucci_corbelli_2017 | Bulge term if present; else 0 with note | State if bulge negligible |
| `inclination_deg` | corbelli_et_al_2014 | — | Global or per-radius from paper | Single convention per processed file |
| `distance_mpc` | corbelli_et_al_2014 | — | Published distance scale | Record systematic if varied |
| `source_id` | (manifest) | — | Must match `sources_manifest.yaml` | One primary `source_id` per row or documented mix |
| `notes` | — | — | Free text | Interpolation, merges, caveats |

---

## 4. Extraction policy

1. **Prefer machine-readable tables** or author supplementary data with explicit columns.
2. **Digitize figures only** when no table exists; record software (e.g. WebPlotDigitizer), figure panel, axis units, sampling density, and estimated digitization uncertainty in `digitization_method` / `notes`.
3. **Never mix sources** on the same radius grid without documenting interpolation method, grid choice, and potential double-counting of baryonic components.
4. **No fake data rows** — the processed CSV must not contain placeholder or invented velocities.
5. **One manifest entry per literature product** used; update `acquisition_status` only when real files exist.

---

## 5. Transformation policy

| Operation | Requirement |
|-----------|-------------|
| Unit conversions | Document factors (e.g. arcsec → kpc via distance); store `original_*_unit` columns when non-trivial |
| Distance rescaling | If distance updated relative to source paper, rescale radii and masses consistently and log old vs new |
| Radius-grid interpolation | Use documented spline or linear method; do not extrapolate beyond source range without flagging in `data_quality_flag` |
| Uncertainty propagation | Document whether errors are combined in quadrature or taken from source only |
| Baryonic velocity convention | State whether components are quadrature-summed for \(v_{\mathrm{bar}}\) in Phase 2; keep \(v_{\mathrm{gas}}\), \(v_{\mathrm{disk}}\), \(v_{\mathrm{bulge}}\) separate in CSV |

All transforms get a dated row in `docs/data_sources.md` transformation log with script path.

---

## 6. Readiness checklist for Phase 1C

Before committing `data/processed/m33_rotation.csv`:

- [ ] Exact source pages/tables identified for each component (table or figure number recorded)
- [ ] `source_id` mapping complete for every planned row
- [ ] Extraction method selected and recorded in manifest (`extraction_method` field)
- [ ] Raw files or download instructions added under `data/raw/` (with README note if large files are external)
- [ ] `data/raw/sources_manifest.yaml` copied from template and updated (`acquisition_status` ≥ `downloaded` only when files exist)
- [ ] `docs/data_sources.md` transformation log updated
- [ ] `python scripts/check_sources_manifest.py data/raw/sources_manifest.yaml` → PASS
- [ ] `python scripts/validate_m33_data.py data/processed/m33_rotation.csv` → PASS

---

## Related commands

```bash
python scripts/check_sources_manifest.py data/raw/sources_manifest_template.yaml
python scripts/validate_m33_data.py data/processed/m33_rotation_schema_template.csv
```
