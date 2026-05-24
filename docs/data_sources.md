# Data sources and transformations

All M33 inputs and every processing step must be recorded here before use in analysis scripts.

## Rules

**Every transformation** from raw files to processed tables (rebinning, deprojection, mass-to-light scaling, inclination correction, etc.) must have:

1. A dated entry in this document
2. A script reference under `scripts/` or a notebook path
3. Input and output file names under `data/raw/` or `data/processed/`

**No undocumented processed data:** Digitized, downloaded, or transformed values **must not** appear under `data/processed/` without:

- A matching `source_id` in `data/raw/sources_manifest.yaml` (copy from `sources_manifest_template.yaml`)
- A transformation log row below
- Traceability fields in the CSV (`source_id`, `notes`, and optional `reference`, `digitization_method`, etc.)

**Traceability:** Every data row in the canonical processed CSV must use a `source_id` that resolves to an entry in the source manifest or an explicit note in this file.

**Processed-row rule:** No row may appear in `data/processed/m33_rotation.csv` without a valid, documented `source_id` tied to the manifest.

**Digitization / transform rule:** Digitized, downloaded, or transformed values must not enter `data/processed/` without manifest entry, transformation log row, and CSV fields (`notes`, optional `digitization_method`, `reference`) filled as appropriate.

## Source manifest (Phase 1B)

| File | Role |
|------|------|
| `data/raw/sources_manifest_template.yaml` | Versioned template; validates with manifest CLI |
| `data/raw/sources_manifest.yaml` | Active registry (Phase 1C; tracked in git) |

Loader: `tdf_m33.data.manifest` (`load_sources_manifest`, `validate_sources_manifest`).  
CLI: `python scripts/check_sources_manifest.py <path>`

Each manifest entry requires: `source_id`, `title`, `authors`, `year`, `publication`, `data_type`, `planned_use`, `acquisition_status`, `url_or_doi`, `expected_fields`, `extraction_method`, `transformation_notes`, `limitations`, `citation_key`, `notes`.

Allowed `acquisition_status` values: `planned`, `located`, `downloaded`, `digitized`, `processed`, `validated`.  
Do not advance status without a real file and validation (see `docs/data_acquisition_plan.md`).

### Registered literature sources (Phase 1B)

| source_id | Citation | acquisition_status | Role |
|-----------|----------|-------------------|------|
| `corbelli_salucci_2000` | Corbelli & Salucci 2000 | located | Historical \(v_{\mathrm{obs}}\) validation |
| `corbelli_et_al_2014` | Corbelli et al. 2014, A&A 572, A23; DOI [10.1051/0004-6361/201424033](https://doi.org/10.1051/0004-6361/201424033); manuscript `aa24033-14` | downloaded | Primary baryonic + rotation model (PDF Phase 1D-A 2026-05-24) |
| `lopez_fune_salucci_corbelli_2017` | López Fune et al. 2017 | located | NFW/Burkert baselines (Phase 2) |
| `hi_map_placeholder` | TBD | planned | Optional 2D τ-map |
| `co_map_placeholder` | TBD | planned | Optional CO map |
| `lensing_limits_placeholder` | TBD | planned | Phase 5 limits |

Acquisition workflow: `docs/data_acquisition_plan.md`.  
Download/extraction audit: `docs/extraction_log.md`.

## Raw vs model-ready data (Phase 1C)

| Layer | Location | Model-ready? |
|-------|----------|----------------|
| Downloads | `data/raw/downloads/` | No — publisher PDFs, HTML, supplementary files |
| Raw extracted | `data/raw/extracted/` | **No** — interim table columns (`sigma_*`, `v_rot_kms`, etc.); see `corbelli2014_table1_raw.csv` |
| Processed | `data/processed/m33_rotation.csv` | **Yes** — requires real \(v_{\mathrm{obs}}\), \(v_{\mathrm{gas}}\), \(v_{\mathrm{disk}}\), … |

**Surface densities are not baryonic velocities.** Values such as `sigma_hi`, `sigma_gas`, and `sigma_star` in the raw Corbelli et al. 2014 Table 1 template must **not** be copied into `v_gas_kms` or `v_disk_kms` without a documented mass-model derivation (Phase 1D).

### Corbelli et al. 2014 — Table 1 column audit (Phase 1D-B, 2026-05-24)

Audited against `data/raw/downloads/corbelli2014_aa24033_14.pdf`, **page 13 of 18** (table title: *Rotation curve, atomic gas, and stellar mass surface densities across the M 33 disk*). Full mapping in `docs/extraction_log.md` §5.1.

| Published (A&A Table 1) | Unit | Raw template column |
|-------------------------|------|---------------------|
| \(R\) | kpc | `r_kpc` |
| \(V_r\) | km s\(^{-1}\) | `v_rot_kms` |
| \(\sigma_V\) | km s\(^{-1}\) | `v_err_kms` |
| \(\Sigma_{\mathrm{HI}}\) | M\(_\odot\) pc\(^{-2}\) | `sigma_hi` |
| \(\Sigma_\*\) | M\(_\odot\) pc\(^{-2}\) | `sigma_star` |

### Corbelli et al. 2014 — Table 1 raw extraction (Phase 1D-C, 2026-05-24)

**File:** `data/raw/extracted/corbelli2014_table1_raw.csv` (**58 rows**, tracked in git).

Contains **observed rotation** (\(V_r\), \(\sigma_V\)) and **surface densities** (\(\Sigma_{\mathrm{HI}}\), \(\Sigma_\*\)) from A&A 572, A23 Table 1 only. Columns `sigma_h2` and `sigma_gas` are empty. This file is **not** model-ready.

**Gaps (unchanged):** No \(v_{\mathrm{gas}}\), \(v_{\mathrm{disk}}\), or \(v_{\mathrm{bulge}}\) in Table 1. **Warning:** Do **not** map \(\Sigma_{\mathrm{HI}}\) → `v_gas_kms` or \(\Sigma_\*\) → `v_disk_kms`. Baryonic velocity components still require a documented mass-model / dynamical decomposition step (Phase 1D-D) before `data/processed/m33_rotation.csv`.

**Validate raw file:** `python scripts/validate_corbelli2014_table1_raw.py`

`configs/m33_default.yaml` → `processed_data.allow_creation_without_baryonic_velocity_components: false`

Phase 1C intentionally does **not** create `m33_rotation.csv` until Phase 1D provides traceable baryonic velocity components.

## Canonical processed CSV schema

File: `data/processed/m33_rotation.csv` (not committed until real data exist).  
Template (headers only): `data/processed/m33_rotation_schema_template.csv`

| Column | Required | Description |
|--------|----------|-------------|
| `galaxy_id` | yes | Galaxy identifier (e.g. `M33`) |
| `r_kpc` | yes | Galactocentric radius [kpc]; must be > 0 |
| `v_obs_kms` | yes | Observed circular speed [km s⁻¹]; must be > 0 |
| `v_err_kms` | yes* | Uncertainty on `v_obs_kms` [km s⁻¹]; may be null if documented in `notes` |
| `v_gas_kms` | yes | Gas contribution [km s⁻¹]; ≥ 0 |
| `v_disk_kms` | yes | Stellar disk contribution [km s⁻¹]; ≥ 0 |
| `v_bulge_kms` | yes | Bulge contribution [km s⁻¹]; ≥ 0 |
| `source_id` | yes | Key into `data/raw/sources_manifest.yaml` |
| `data_quality_flag` | yes | Quality / selection flag (project-defined strings) |
| `notes` | yes | Free text; document null `v_err_kms` or caveats here |
| `sigma_gas` | no | Gas surface density scale if used |
| `sigma_star` | no | Stellar surface density scale if used |
| `inclination_deg` | no | Inclination at radius or global value |
| `distance_mpc` | no | Distance assumption [Mpc] |
| `original_radius_unit` | no | Unit before conversion to kpc |
| `original_velocity_unit` | no | Unit before conversion to km s⁻¹ |
| `digitized_from_figure` | no | Figure or panel reference if digitized |
| `digitization_method` | no | Tool or procedure used for digitization |
| `reference` | no | Bibliographic shorthand or DOI |

Schema constants in code: `tdf_m33.data.schema`. Validation: `tdf_m33.data.validation` and `scripts/validate_m33_data.py`.

## Planned data sources (ingestion status)

| Dataset | Description | Format | Status | Reference / URL |
|---------|-------------|--------|--------|-----------------|
| Rotation curve | \(v_{\mathrm{obs}}(r)\) vs radius | Canonical CSV | Raw template only (Phase 1C) | Corbelli et al. 2014 (primary); CS2000 (backup) |
| Gas contribution | \(v_{\mathrm{gas}}(r)\) | Canonical CSV | Manifest only | Corbelli et al. 2014 |
| Stellar disk | \(v_{\mathrm{disk}}(r)\) | Canonical CSV | Manifest only | Corbelli et al. 2014 |
| Bulge / spheroid | \(v_{\mathrm{bulge}}(r)\) | Canonical CSV | Schema only | Optional |
| Distance / inclination | Global or per-radius metadata | CSV optional cols | Not set | TBD |
| Lensing / deflection limits | External constraints | TBD | Not ingested | TBD |

## Transformation log

| Date | Input | Operation | Output | Script | Notes |
|------|-------|-----------|--------|--------|-------|
| — | — | — | — | — | No transformations yet (Phase 1C: structure only) |

## Configuration linkage

Paths in `configs/m33_default.yaml`:

- `data_schema` → processed CSV and validation script
- `source_manifest` → template, active manifest, `require_valid_manifest`
- `raw_sources` → downloads, extracted, Table 1 raw template
- `processed_data` → model-ready CSV policy flags
