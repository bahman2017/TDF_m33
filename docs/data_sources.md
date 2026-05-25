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

**Baryonic velocity derivation (Phase 1D-D1):** Interim audit table  
`outputs/tables/corbelli2014_baryonic_velocity_derivation_audit.csv` — axisymmetric disk-gravity derivation from Table 1 \(\Sigma\) profiles (see **`docs/baryonic_velocity_derivation_plan.md`**). Contains \(v_{\mathrm{gas}}\), \(v_{\mathrm{disk}}\), \(v_{\mathrm{bar}}\); **not** the canonical processed file. Regenerate: `python scripts/derive_corbelli2014_baryonic_velocities.py`; validate: `python scripts/validate_corbelli2014_baryonic_velocity_derivation.py`.

**Fig. 12 sanity-check (Phase 1D-D2-A / D2-A2):** Validation only — not canonical. Corrected comparison: **PASS_WITH_CAVEAT**. See `docs/baryonic_velocity_derivation_plan.md` §8–8.1.

### Corbelli et al. 2014 — canonical processed rotation (Phase 1D-D2-B, 2026-05-24)

**File:** `data/processed/m33_rotation.csv` (**58 rows**, tracked in git).

| Field | Provenance |
|-------|------------|
| `v_obs_kms`, `v_err_kms` | Corbelli 2014 Table 1 adopted \(V_r\), \(\sigma_V\) |
| `v_gas_kms`, `v_disk_kms` | Phase 1D-D1 axisymmetric disk-gravity derivation from Table 1 \(\Sigma\) (+ H\(_2\)/He formula) |
| `v_bulge_kms` | 0 (no separate bulge per paper) |
| `sigma_gas`, `sigma_star` | Derived/tabuluated surface densities from audit (not velocities) |
| `data_quality_flag` | `derived_baryonic_velocity_pass_with_caveat` |
| `notes` | Documents Fig. 12 PASS_WITH_CAVEAT and that digitization is not canonical |

**Build:** `python scripts/build_m33_rotation_processed.py`  
**Validate:** `python scripts/validate_m33_data.py data/processed/m33_rotation.csv`

**Caveats for Phase 2/3:** Baryonic velocities are derived, not published table columns; D1 ≠ Casertano (1983); possible ~7–10 km s\(^{-1}\) stellar offset vs Fig. 12 at some radii. This file does **not** contain halo or TDF components.

### Phase 2A — baryonic-only baseline (2026-05-24)

**Script:** `python scripts/run_phase2a_baryonic_only.py`

| Output | Path |
|--------|------|
| Metrics | `outputs/tables/phase2a_baryonic_only_metrics.csv` |
| Radial profile | `outputs/tables/phase2a_baryonic_only_profile.csv` |
| Figures | `outputs/figures/phase2a_baryonic_only_rotation_curve.png`, `phase2a_residual_velocity_squared.png` |

**Scope:** Diagnostic only—recomputes \(v_{\mathrm{bar}}\) from processed components, \(\Delta v^2 = v_{\mathrm{obs}}^2 - v_{\mathrm{bar}}^2\), and acceleration proxy \(\Delta v^2/r\). **`parameter_count = 0`** (baryonic components fixed from D1, not fitted). AIC/BIC use χ² + 2k and χ² + k ln n with k=0 for comparison with future halo fits. **Not** an NFW/Burkert fit; **not** a TDF result. Loader: `tdf_m33.data.m33_dataset.load_m33_rotation_dataset`.

### Phase 2B — NFW and Burkert halo baselines (2026-05-24)

**Script:** `python scripts/run_phase2b_halo_baselines.py`

| Output | Path |
|--------|------|
| Model comparison | `outputs/tables/phase2b_model_comparison.csv` |
| Halo parameters | `outputs/tables/phase2b_halo_fit_parameters.csv` |
| Full profiles (58 rows) | `outputs/tables/phase2b_rotation_profiles.csv` |
| Figures | `outputs/figures/phase2b_rotation_curve_comparison.png`, `phase2b_residuals_comparison.png` |

**Fit mask (default):** \(0.4 \le R \le 23\) kpc (Corbelli 2014 dynamical range); all 58 radii retained in profile CSV with `fit_mask` column. Metrics computed on masked points only.

**Models:** `v_model² = v_bar² + v_halo²`; NFW and Burkert k=2; baryonic_only k=0 (recomputed on same mask). **Not TDF.** Phase 3 uses Phase 2A baryonic \(\Delta v^2\), not halo-subtracted residuals.

### Phase 2C — Model comparison audit (2026-05-24)

**Script:** `python scripts/run_phase2c_model_audit.py` (requires Phase 2A and 2B outputs)

| Output | Path |
|--------|------|
| Audit summary | `outputs/tables/phase2c_model_audit_summary.csv` |
| Phase 3 residual readiness | `outputs/tables/phase2c_residual_readiness.csv` |
| Report | `outputs/reports/phase2c_model_audit_report.md` |
| Figure (optional) | `outputs/figures/phase2c_model_audit_summary.png` |

Consolidates fit-mask metrics, Burkert r₀ boundary flag, NFW enclosed-mass sanity at 23 kpc, and Phase 2A \(\Delta v^2\) smoothness for τ reconstruction planning. **No τ columns or lensing outputs.**

### Phase 3A — Direct τ reconstruction (2026-05-24)

**Script:** `python scripts/run_phase3a_tdf_radial_reconstruction.py`

| Output | Path |
|--------|------|
| Radial reconstruction | `outputs/tables/phase3a_tau_radial_reconstruction.csv` |
| Diagnostics | `outputs/tables/phase3a_tau_reconstruction_diagnostics.csv` |
| Figures | `phase3a_tau_gradient_raw.png`, `phase3a_tau_profile_raw.png`, `phase3a_tdf_direct_reconstruction_check.png` |

Input: `phase2c_residual_readiness.csv` \(\Delta v^2\); \(d\tau/dr = \Delta v^2/(r K_\tau)\), default \(K_\tau=1\). **Not** NFW/Burkert residuals. Direct reconstruction is an identity check—not AIC/BIC model comparison (Phase 3B).

## Canonical processed CSV schema

File: `data/processed/m33_rotation.csv` (canonical processed table, Phase 1D-D2-B).  
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
