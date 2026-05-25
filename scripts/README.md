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

**Phase 4B-A — disk-to-sky τ projection (geometry only):**

```bash
python scripts/run_phase4a_tdf_2d_map.py  # prerequisite
python scripts/run_phase4b_tau_projection.py
```
