# Scripts

Command-line entry points for pipelines (data ingest, fit, plot, lensing) will live here in later phases.

Example (future):

```bash
python scripts/fit_rotation.py --config configs/m33_default.yaml
```

**Phase 1A — validate processed CSV:**

```bash
python scripts/validate_m33_data.py data/processed/m33_rotation_schema_template.csv
```

**Phase 1B — validate sources manifest:**

```bash
python scripts/check_sources_manifest.py data/raw/sources_manifest.yaml
```

**Phase 1C — raw Table 1 template and source audit:**

```bash
python scripts/prepare_corbelli2014_table1_template.py
python scripts/audit_m33_sources.py
```

**Phase 1D-C — extract and validate Corbelli 2014 Table 1 (raw/interim):**

```bash
python scripts/extract_corbelli2014_table1_from_pdf.py   # requires pymupdf; official PDF on disk
python scripts/validate_corbelli2014_table1_raw.py
```

**Phase 1D-D1 — baryonic velocity derivation (interim audit only):**

```bash
python scripts/derive_corbelli2014_baryonic_velocities.py
python scripts/validate_corbelli2014_baryonic_velocity_derivation.py
```

Canonical processed CSV: `python scripts/build_m33_rotation_processed.py` (Phase 1D-D2-B).

**Phase 2A — baryonic-only baseline (no halo/TDF fit):**

```bash
python scripts/run_phase2a_baryonic_only.py
```

**Phase 2B — NFW/Burkert halo baselines (comparison only):**

```bash
python scripts/run_phase2b_halo_baselines.py
```

**Phase 2C — audit Phase 2 comparison and Phase 3 residual readiness:**

```bash
python scripts/run_phase2a_baryonic_only.py   # prerequisite
python scripts/run_phase2b_halo_baselines.py  # prerequisite
python scripts/run_phase2c_model_audit.py
```

**Phase 3A — direct pointwise TDF τ from baryonic Δv² (no smoothing):**

```bash
python scripts/run_phase2c_model_audit.py   # prerequisite
python scripts/run_phase3a_tdf_radial_reconstruction.py
```

**Phase 3B-A — regularized τ-gradient (Gaussian + spline):**

```bash
python scripts/run_phase3a_tdf_radial_reconstruction.py  # prerequisite
python scripts/run_phase3b_tdf_regularized_reconstruction.py
```

**Phase 3C — low-parameter knot τ model (AIC/BIC vs baselines):**

```bash
python scripts/run_phase3c_tdf_lowparam_model.py
```

**Phase 3D — TDF sensitivity / robustness audit:**

```bash
python scripts/run_phase3c_tdf_lowparam_model.py  # prerequisite
python scripts/run_phase3d_tdf_sensitivity.py
```

**Phase 4A — axisymmetric disk-plane 2D τ map (from Phase 3C 3-knot model):**

```bash
python scripts/run_phase3c_tdf_lowparam_model.py  # prerequisite
python scripts/run_phase4a_tdf_2d_map.py
```

**Phase 4B — disk-to-sky τ projection (Corbelli 2014 geometry):**

```bash
python scripts/run_phase4a_tdf_2d_map.py  # prerequisite
python scripts/run_phase4b_tau_projection.py  # uses corbelli2014_tilted_ring_geometry_model_shape.csv
```

**Phase 5A — normalized deflection-proxy from frozen sky τ (no lensing fit):**

```bash
python scripts/run_phase4b_tau_projection.py  # prerequisite
python scripts/run_phase5a_lensing_prediction.py
```

Outputs: `outputs/maps/phase5a_tau_deflection_proxy_map.npz`, metadata/summary tables, report, magnitude/vector/convergence figures. Units: `normalized_proxy`. No separate halo; no observational limit comparison until documented in `docs/data_sources.md`.

**Phase 5B-A — calibration and limits planning audit (no physical conversion):**

```bash
python scripts/run_phase5a_lensing_prediction.py  # prerequisite
python scripts/run_phase5b_lensing_calibration_audit.py
```

Outputs: `outputs/tables/phase5b_lensing_calibration_status.csv`, `outputs/reports/phase5b_lensing_calibration_audit.md`. Plan: `docs/lensing_calibration_and_limits_plan.md`. Physical calibration and observational limits remain disabled in config.

**Phase 5B-B — constraint source review (no comparison):**

```bash
python scripts/run_phase5b_constraint_source_audit.py
```

Outputs: `outputs/tables/phase5b_constraint_source_status.csv`, `outputs/reports/phase5b_constraint_source_audit.md`. Review: `docs/lensing_constraint_source_review.md`. Selected Phase 5C candidate: `lopez_fune_salucci_corbelli_2017` (dynamical mass; not weak lensing).

**Phase 5B-C — acquire López Fune et al. 2017 (selected source):**

```bash
python scripts/audit_lopez_fune_2017_source.py
```

Requires `data/raw/downloads/lopez_fune_salucci_corbelli_2017_m33.pdf` and checksum sidecar. Plan: `docs/lopez_fune_2017_extraction_plan.md`. No comparison tables yet.

**Phase 5C-A — extract dynamical constraints (no comparison):**

```bash
python scripts/validate_lopez_fune_2017_extracted_constraints.py
```

Writes/validates `data/raw/extracted/lopez_fune_2017_dm_profile_raw.csv`, `lopez_fune_2017_halo_parameters_raw.csv`, and audit outputs under `outputs/`.

**Phase 5C-B — upper-bound dynamical consistency (not lensing):**

```bash
python scripts/run_phase5c_upper_bound_consistency.py
```

Compares frozen `tdf_lowparam_3knot` enclosed-mass proxy `M_tau_eff = r v_tau^2 / G` to López Fune 2017 `M_enclosed_23kpc`. Does **not** enable `observational_limits`, fit `alpha_tau_scale`, or convert deflection to arcsec.

**Phase 6A — publication audit (read-only consolidation):**

```bash
python scripts/run_phase6a_publication_audit.py
```

Outputs: `outputs/reports/phase6a_publication_results_summary.md`, key-results and claim-traceability tables, `phase6a_reproducibility_commands.md`. Does not refit models or enable physical lensing calibration.

**Phase 6C — expanded manuscript draft audit:**

```bash
python scripts/run_phase6c_manuscript_draft_audit.py
```

Checks readable draft sections, required metrics, figure paths, bibliography TODO markers. See `docs/manuscript_drafting_notes.md`.

**Phase 6B — manuscript skeleton audit:**

```bash
python scripts/run_phase6b_manuscript_audit.py
```

Checks `paper/m33_tdf_tau_geometry_draft.tex`, `docs/manuscript_*.md`, prohibited claims, and references to existing pipeline outputs. No new numerical results.
