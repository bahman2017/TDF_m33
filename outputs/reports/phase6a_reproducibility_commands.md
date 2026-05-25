# Phase 6A — Reproducibility commands (M33 TDF pipeline)

Run from repository root with project venv active. Config: `configs/m33_default.yaml`.

## Data and validation

```bash
python scripts/prepare_corbelli2014_table1_template.py
python scripts/extract_corbelli2014_table1_from_pdf.py
python scripts/validate_corbelli2014_table1_raw.py
python scripts/derive_corbelli2014_baryonic_velocities.py
python scripts/validate_corbelli2014_baryonic_velocity_derivation.py
python scripts/build_m33_rotation_processed.py
python scripts/validate_m33_data.py data/processed/m33_rotation.csv
python scripts/check_sources_manifest.py data/raw/sources_manifest.yaml
python scripts/audit_m33_sources.py
```

## Phase 2 — baselines

```bash
python scripts/run_phase2a_baryonic_only.py
python scripts/run_phase2b_halo_baselines.py
python scripts/run_phase2c_model_audit.py
```

## Phase 3 — TDF radial pathway

```bash
python scripts/run_phase3a_tdf_radial_reconstruction.py
python scripts/run_phase3b_tdf_regularized_reconstruction.py
python scripts/run_phase3c_tdf_lowparam_model.py
python scripts/run_phase3d_tdf_sensitivity.py
```

## Phase 4 — τ maps

```bash
python scripts/run_phase4a_tdf_2d_map.py
python scripts/run_phase4b_tau_projection.py
```

## Phase 5 — lensing scaffold and limits

```bash
python scripts/run_phase5a_lensing_prediction.py
python scripts/run_phase5b_lensing_calibration_audit.py
python scripts/run_phase5b_constraint_source_audit.py
python scripts/audit_lopez_fune_2017_source.py
python scripts/validate_lopez_fune_2017_extracted_constraints.py
python scripts/run_phase5c_upper_bound_consistency.py
```

## Phase 6A — publication audit

```bash
python scripts/run_phase6a_publication_audit.py
```

**Note:** Prior numerical outputs are read-only inputs to Phase 6A; the audit does not refit models.
