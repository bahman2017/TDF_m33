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
| `lopez_fune_salucci_corbelli_2017` | López Fune et al. 2017 MNRAS; DOI 10.1093/mnras/stx2742 | **extracted** | Phase 5C-B dynamical upper-bound (raw CSVs) |
| `hi_map_placeholder` | TBD | planned | Optional 2D τ-map |
| `co_map_placeholder` | TBD | planned | Optional CO map |
| `kam_et_al_2018_m33_hi_masses` | Kam et al. 2018 AJ (arXiv 1706.04248) | located | Alternate dynamical candidate |
| `m33_direct_weak_lensing_gap` | Phase 5B-B literature synthesis | documented | Context — no M33 WL map found |
| `corbelli_salucci_2000` | Corbelli & Salucci 2000 MNRAS | located | Superseded dynamical context |
| `mcconnachie_2012_local_group` | McConnachie 2012 AJ | located | LG context only |
| `putman_et_al_2009_m33_tidal` | Putman et al. 2009 tidal H i | located | Outer-disk context |
| `combo17_weak_lensing_statistical` | Parker et al. 2007 COMBO-17 | rejected | Not M33-specific |

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

Input: `phase2c_residual_readiness.csv` \(\Delta v^2\); \(d\tau/dr = \Delta v^2/(r K_\tau)\), default \(K_\tau=1\). **Not** NFW/Burkert residuals. Direct reconstruction is an identity check—not AIC/BIC model comparison (Phase 3C).

### Phase 3B-A — Regularized τ reconstruction (2026-05-24)

**Script:** `python scripts/run_phase3b_tdf_regularized_reconstruction.py`

| Output | Path |
|--------|------|
| Regularized profiles | `outputs/tables/phase3b_tau_regularized_profiles.csv` |
| Diagnostics | `outputs/tables/phase3b_tau_regularization_diagnostics.csv` |
| Figures | `phase3b_tau_gradient_regularized.png`, `phase3b_tau_profile_regularized.png`, `phase3b_tdf_regularized_reconstruction_check.png`, `phase3b_regularization_tradeoff.png` |

Methods: `gaussian_radius_smoothing` (σ_kpc from config), `smoothing_spline` (fixed s). Smoothing parameters not fitted to rotation. **No** AIC/BIC vs NFW yet.

### Phase 3C — Low-parameter knot τ model (2026-05-24)

**Script:** `python scripts/run_phase3c_tdf_lowparam_model.py`

| Output | Path |
|--------|------|
| TDF comparison | `outputs/tables/phase3c_tdf_lowparam_model_comparison.csv` |
| Fit parameters | `outputs/tables/phase3c_tdf_lowparam_fit_parameters.csv` |
| Profiles | `outputs/tables/phase3c_tdf_lowparam_profiles.csv` |
| Combined baselines | `outputs/tables/phase3c_combined_model_comparison.csv` |

k=3,4,5 knot dτ/dr fitted; K_τ=1 fixed. Combined with Phase 2B baryonic/NFW/Burkert. Phase 3A/3B not in AIC/BIC comparison table.

### Phase 3D — Sensitivity audit (2026-05-24)

**Script:** `python scripts/run_phase3d_tdf_sensitivity.py`

| Output | Path |
|--------|------|
| Summary | `outputs/tables/phase3d_tdf_sensitivity_summary.csv` |
| K_τ sweep | `outputs/tables/phase3d_ktau_sweep.csv` |
| Fit-mask | `outputs/tables/phase3d_fitmask_sensitivity.csv` |
| Smoothing σ | `outputs/tables/phase3d_smoothing_sensitivity.csv` |
| Report | `outputs/reports/phase3d_tdf_sensitivity_report.md` |

### Phase 4A — Axisymmetric 2D τ map (2026-05-24)

**Script:** `python scripts/run_phase4a_tdf_2d_map.py` (requires Phase 3C profiles)

| Output | Path |
|--------|------|
| 2D map archive | `outputs/maps/phase4a_tau_2d_map.npz` |
| Radial consistency | `outputs/tables/phase4a_tau_2d_radial_consistency.csv` |
| Metadata | `outputs/tables/phase4a_tau_2d_map_metadata.csv` |
| Figures | `outputs/figures/phase4a_tau_2d_map.png`, `phase4a_tau_gradient_2d_map.png`, `phase4a_tau_2d_radial_consistency.png` |

Source: `tdf_lowparam_3knot` from `phase3c_tdf_lowparam_profiles.csv`. Disk-plane kpc; masked outside radial tabulation. No lensing.

### Phase 4B-A — Disk-to-sky projection (2026-05-24)

**Script:** `python scripts/run_phase4b_tau_projection.py` (requires Phase 4A NPZ)

| Output | Path |
|--------|------|
| Sky-projected map | `outputs/maps/phase4b_tau_sky_projected_map.npz` |
| Metadata | `outputs/tables/phase4b_tau_projection_metadata.csv` |
| Figures | `outputs/figures/phase4b_tau_sky_projected_map.png`, `phase4b_projection_geometry_check.png` |

Geometry: `tdf.projection` in `configs/m33_default.yaml`. Phase 4B-B uses `geometry_mode: radial_tilted_ring` with `data/raw/extracted/corbelli2014_tilted_ring_geometry_model_shape.csv` (digitized from Corbelli et al. 2014 A&A 572 A23 **Fig. 3**, model-shape triangles, **Sect. 4.1**). `placeholder_geometry_flag: false`.

### Phase 5A — Deflection-proxy from frozen sky τ (2026-05-24)

**Script:** `python scripts/run_phase5a_lensing_prediction.py` (requires Phase 4B NPZ)

| Output | Path |
|--------|------|
| Deflection proxy map | `outputs/maps/phase5a_tau_deflection_proxy_map.npz` |
| Metadata | `outputs/tables/phase5a_lensing_prediction_metadata.csv` |
| Summary | `outputs/tables/phase5a_deflection_summary.csv` |
| Report | `outputs/reports/phase5a_lensing_prediction_report.md` |
| Figures | `outputs/figures/phase5a_deflection_magnitude_map.png`, `phase5a_deflection_vector_field.png`, `phase5a_convergence_proxy_map.png` (if stable) |

Source: `outputs/maps/phase4b_tau_sky_projected_map.npz`; `source_model: tdf_lowparam_3knot`; `deflection_mode: normalized_tau_gradient_proxy`; `units: normalized_proxy`. No lensing-only fit; no separate halo. `compare_to_observational_limits: false`.

### Phase 5B-A — Calibration and limits planning audit (2026-05-24)

**Script:** `python scripts/run_phase5b_lensing_calibration_audit.py` (requires Phase 5A metadata)

| Output | Path |
|--------|------|
| Status table | `outputs/tables/phase5b_lensing_calibration_status.csv` |
| Audit report | `outputs/reports/phase5b_lensing_calibration_audit.md` |

Plan: `docs/lensing_calibration_and_limits_plan.md`. Physical calibration and observational comparison remain **disabled** in config until sources below are documented with real files.

### Phase 5B-B — Constraint source review audit (2026-05-24)

**Script:** `python scripts/run_phase5b_constraint_source_audit.py`

| Output | Path |
|--------|------|
| Status table | `outputs/tables/phase5b_constraint_source_status.csv` |
| Audit report | `outputs/reports/phase5b_constraint_source_audit.md` |

Review: `docs/lensing_constraint_source_review.md`. No observational comparison; `observational_limits.enabled: false`.

### Phase 5B-C — López Fune et al. 2017 acquisition (2026-05-24)

**Script:** `python scripts/audit_lopez_fune_2017_source.py`

| Output | Path |
|--------|------|
| Status table | `outputs/tables/phase5b_lopez_fune_source_status.csv` |
| Audit report | `outputs/reports/phase5b_lopez_fune_source_audit.md` |

| Artifact | Path / value |
|----------|----------------|
| PDF (accepted manuscript) | `data/raw/downloads/lopez_fune_salucci_corbelli_2017_m33.pdf` |
| SHA-256 sidecar | `data/raw/downloads/lopez_fune_salucci_corbelli_2017_m33.pdf.sha256` |
| SHA-256 | `753c93a49ff56e4c60ea0eed8fe8c4e85ed9fb59880a4d2b11cc84968609d3b4` |
| Provenance | arXiv [1611.01409](https://arxiv.org/abs/1611.01409); DOI [10.1093/mnras/stx2742](https://doi.org/10.1093/mnras/stx2742) (MNRAS 474, 4010) |
| Extraction plan | `docs/lopez_fune_2017_extraction_plan.md` |
| DM profile (raw) | `data/raw/extracted/lopez_fune_2017_dm_profile_raw.csv` |
| Halo parameters (raw) | `data/raw/extracted/lopez_fune_2017_halo_parameters_raw.csv` |

**Use:** Dynamical halo / enclosed-mass **upper-bound consistency** context for Phase 5C-B — **not** direct lensing, **not** τ or `alpha_tau_scale` tuning. Partial circularity with Corbelli et al. 2014 rotation inputs (see extraction plan).

### Phase 5C-A — López Fune 2017 constraint extraction (2026-05-24)

**Script:** `python scripts/validate_lopez_fune_2017_extracted_constraints.py`

| Output | Path |
|--------|------|
| Extraction audit | `outputs/reports/phase5c_lopez_fune_extraction_audit.md` |
| Status | `outputs/tables/phase5c_lopez_fune_extraction_status.csv` |

No τ comparison. `observational_limits.enabled: false`.

### Phase 5C-B — Upper-bound dynamical consistency (2026-05-24)

**Script:** `python scripts/run_phase5c_upper_bound_consistency.py`

| Output | Path |
|--------|------|
| τ mass proxy profile | `outputs/tables/phase5c_tau_mass_proxy_profile.csv` |
| Consistency summary | `outputs/tables/phase5c_upper_bound_consistency_summary.csv` |
| Report | `outputs/reports/phase5c_upper_bound_consistency_report.md` |
| Figure | `outputs/figures/phase5c_tau_mass_proxy_vs_lopez_fune.png` |

Dynamical scale check only (`M_tau_eff = r v_τ²/G` vs López Fune `M_enclosed_23kpc`). Not weak lensing; deflection remains `normalized_proxy`; `observational_limits.enabled: false`.

### Lensing / deflection constraint registry (Phase 5B-B+)

**Do not invent numerical limits.** Review: `docs/lensing_constraint_source_review.md`. Audit: `python scripts/run_phase5b_constraint_source_audit.py`.

| source_id | Title (short) | Year | DOI / URL | Constraint class | acquisition_status | calibration | upper-bound | context | Phase 5C |
|-----------|---------------|------|-----------|------------------|-------------------|-------------|-------------|---------|----------|
| `corbelli_et_al_2014` | Corbelli et al. 2014 A&A 572 A23 | 2014 | [10.1051/0004-6361/201424033](https://doi.org/10.1051/0004-6361/201424033) | dynamical + rotation (primary) | downloaded | no | no (circular) | yes | no |
| `lopez_fune_salucci_corbelli_2017` | The radial dependence of dark matter distribution in M33 | 2017 | [10.1093/mnras/stx2742](https://doi.org/10.1093/mnras/stx2742) | dynamical halo | **extracted** | no | yes | yes | **5C-B upper-bound compared** |
| `kam_et_al_2018_m33_hi_masses` | Hi Kinematics and Mass Distribution of Messier 33 | 2018 | [10.3847/1538-3881/aa79f3](https://doi.org/10.3847/1538-3881/aa79f3) | dynamical halo | located | no | yes | yes | alternate |
| `corbelli_salucci_2000` | Extended rotation curve and DM halo of M33 | 2000 | [astro-ph/9909252](https://arxiv.org/abs/astro-ph/9909252) | dynamical | located | no | marginal | yes | no (superseded) |
| `mcconnachie_2012_local_group` | Dwarf galaxies in and around the Local Group | 2012 | [10.1088/0004-6256/144/1/4](https://doi.org/10.1088/0004-6256/144/1/4) | Local Group | located | no | no | yes | no |
| `putman_et_al_2009_m33_tidal` | M31–M33 tidal H i (see also McConnachie et al. 2010) | 2009 | literature | tidal / outer disk | located | no | context | yes | no |
| `combo17_weak_lensing_statistical` | COMBO-17 weak lensing of field galaxies | 2007 | [astro-ph/0412615](https://arxiv.org/abs/astro-ph/0412615) | weak lensing (statistical) | rejected | no | no | no | no — not M33 |
| `m33_direct_weak_lensing_gap` | No M33-specific WL map identified (5B-B review) | — | `docs/lensing_constraint_source_review.md` | review synthesis | documented | no | no | yes | no |

**Phase 5C-B (complete):** Enclosed-mass proxy compared to López Fune `M_enclosed_23kpc` at ~23 kpc. `observational_limits.enabled` remains **false**; no arcsec deflection calibration. Physical lensing and weak-lensing comparison remain deferred.

Config keys: `tdf.lensing.observational_limits.limits_source_id` must match a registry row before `enabled: true`.

**Reprojection (G8):** Design in `docs/phase6f_validated_reprojection_design.md` (if merged); implementation blocked.

### Phase 6F public data alternatives (Tier A/B/C audit)

**Audit:** `docs/phase6f_public_data_acquisition_audit.md`  
**Tiers:** `docs/phase6f_data_tiers.md`  
**Registry:** `data/raw/phase6f/manifest/phase6f_public_candidate_registry.yaml`

| Tier | Role | Corbelli G1/G2? |
|------|------|-----------------|
| A | Exact Corbelli 2014 primary FITS | Required for PASS (author request) |
| B | Public pilot (LGLBS HI, S4G IRAC, IRAM CO) | **Cannot PASS** |
| C | Gratier reference / synthetic | Smoke test only |

```bash
python scripts/audit_phase6f_public_data_sources.py
```

**Corbelli 2014 geometry notes (PDF audit):**

- §4.1 + Fig. 3: 11 free tilted rings; i and PA vary with R; model-shape vs model-mean methods (Appendix A).
- Abstract: warp from ~8 kpc; inclination nearly constant; PA rotates ~30° toward M31 at large R.
- Table 1 rotation velocities use tilted-ring deconvolution (not single global i/PA).
- Inner-disk representative global values (not used in radial mode): i≈54°, PA≈22°.

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
