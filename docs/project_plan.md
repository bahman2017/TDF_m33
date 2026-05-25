# Project plan: TDF–M33 τ-geometry

Phased roadmap for the computational companion. Each phase has explicit acceptance criteria before moving on.

---

## Phase 0: Repository scaffold

**Goal:** Publication-ready repository layout, documentation skeleton, configuration skeleton, and minimal tests—no scientific models.

**Deliverables:**

- Package layout under `src/tdf_m33/`
- `docs/`, `configs/`, `data/`, `outputs/`, `scripts/`, `tests/`
- `README.md`, `pyproject.toml`, `.gitignore`
- Placeholder tests for imports and core equation algebra

**Acceptance criteria:**

- [x] `python -m pip install -e .` succeeds
- [x] `python -m pytest` passes
- [x] Core equations appear in `docs/theory_summary.md` and README
- [x] No unsupported claims about disproving dark matter
- [x] `configs/m33_default.yaml` contains all required sections with placeholders only

**Status:** Complete.

---

## Phase 1A: M33 data schema, provenance registry, and validation

**Goal:** Define the canonical processed CSV schema, source manifest template, and validation layer—no real data download or digitization.

**Deliverables:**

- `tdf_m33.data.schema`, `io`, `validation`
- `data/processed/m33_rotation_schema_template.csv` (headers only)
- `data/raw/sources_manifest_template.yaml`
- `scripts/validate_m33_data.py`
- Documentation updates in `docs/data_sources.md` and README

**Acceptance criteria:**

- [x] Required and optional columns documented and defined in code
- [x] CSV template has correct headers and no fake data rows
- [x] `validate_m33_dataframe` catches missing columns, bad signs, empty `source_id`
- [x] Empty template passes structural validation
- [x] Provenance template lists planned literature sources with `acquisition_status: not_downloaded`
- [x] Unit tests for schema and validation pass

**Status:** Complete.

---

## Phase 1B: Source registry, manifest loader, and acquisition plan

**Goal:** Define literature sources, structured provenance manifest, validation CLI, and acquisition plan—no numerical ingestion.

**Deliverables:**

- `tdf_m33.data.manifest` and `scripts/check_sources_manifest.py`
- Updated `data/raw/sources_manifest_template.yaml` with full metadata fields
- `docs/data_acquisition_plan.md`
- Tests in `tests/test_manifest.py`

**Acceptance criteria:**

- [x] Manifest loader loads and validates template YAML
- [x] Template manifest validates (PASS from CLI)
- [x] `docs/data_acquisition_plan.md` documents sources, extraction, and Phase 1C checklist
- [x] No fake or real numerical data in `data/processed/`
- [x] Unit tests for manifest pass

**Status:** Complete.

---

## Phase 1C: Official source acquisition and raw extraction audit

**Goal:** Prepare download/extracted layout, active manifest, raw Table 1 template, source audit tooling, and extraction log—**no model-ready processed CSV**.

**Deliverables:**

- `data/raw/sources_manifest.yaml` (active registry)
- `data/raw/downloads/`, `data/raw/extracted/` with READMEs
- `corbelli2014_table1_raw_template.csv` (headers only)
- `tdf_m33.data.source_status`, `scripts/audit_m33_sources.py`, `scripts/prepare_corbelli2014_table1_template.py`
- `docs/extraction_log.md`

**Acceptance criteria:**

- [x] Active manifest exists and validates
- [x] Raw download/extracted directories exist
- [x] Raw Table 1 template exists with no fake rows
- [x] `scripts/audit_m33_sources.py` passes
- [x] `data/processed/m33_rotation.csv` **not** created prematurely
- [x] Documentation separates raw/interim from model-ready data
- [x] Tests pass

**Status:** Complete.

---

## Phase 1D: Baryonic velocity derivation and model-ready ingestion

**Goal:** Extract real Table 1 rows, derive or source \(v_{\mathrm{gas}}\), \(v_{\mathrm{disk}}\) where needed, build validated `m33_rotation.csv`.

**Deliverables:**

- Populated `data/raw/extracted/corbelli2014_table1_raw.csv` (real rows only)
- Derivation pipeline documented in `docs/data_sources.md` and `docs/extraction_log.md`
- `data/processed/m33_rotation.csv` passing schema validation
- Updated `acquisition_status` through `processed` / `validated` as justified

**Acceptance criteria:**

- [x] Official PDF/tables acquired and checksums recorded
- [x] No surface density passed off as baryonic velocity without derivation
- [x] All processed rows traceable via `source_id`
- [x] Manifest and CSV validation CLIs pass
- [x] No fake data rows

**Status:** Complete (through Phase 1D-D2-B).

---

## Phase 2A: Baryonic-only baseline diagnostics

**Goal:** Establish fixed baryonic-only residuals and metrics on the canonical 58-point grid—**not** a halo fit.

**Deliverables:**

- `tdf_m33.data.m33_dataset`, `tdf_m33.models.baryonic`, `tdf_m33.fitting.metrics`
- `scripts/run_phase2a_baryonic_only.py`
- `outputs/tables/phase2a_baryonic_only_{metrics,profile}.csv`
- Residual figures in `outputs/figures/`

**Acceptance criteria:**

- [x] Load and validate `m33_rotation.csv` (58 rows)
- [x] Recompute \(v_{\mathrm{bar}}\), \(\Delta v^2 = v_{\mathrm{obs}}^2 - v_{\mathrm{bar}}^2\) without clipping
- [x] Export RMSE / χ² with `parameter_count = 0` (fixed derived baryonic)
- [x] Document PASS_WITH_CAVEAT on derived baryonic velocities
- [x] No NFW, Burkert, or TDF in this phase

**Status:** Complete.

---

## Phase 2B: NFW + Burkert halo baselines

**Goal:** Standard ΛCDM comparison baselines: \(v_{\mathrm{model}}^2 = v_{\mathrm{bar}}^2 + v_{\mathrm{halo}}^2\) on Corbelli fit range \(0.4 \le R \le 23\) kpc.

**Deliverables:**

- `tdf_m33.models.halo`, `tdf_m33.fitting.halo_fit`, `scripts/run_phase2b_halo_baselines.py`
- `outputs/tables/phase2b_model_comparison.csv`, `phase2b_halo_fit_parameters.csv`, `phase2b_rotation_profiles.csv`
- Comparison figures in `outputs/figures/`

**Acceptance criteria:**

- [x] NFW and Burkert fits from `configs/m33_default.yaml` bounds and fit mask
- [x] Model comparison with baryonic_only (k=0), NFW (k=2), Burkert (k=2); AIC/BIC on masked points
- [x] Full 58-row profile table; metrics use fit mask only
- [x] Corbelli 2014 reference values reported as sanity context only
- [x] No TDF τ reconstruction

**Status:** Complete.

---

## Phase 2C: Model comparison audit and Phase 3 readiness

**Goal:** Consolidate Phase 2A/2B results, document Burkert boundary limits, and export baryonic \(\Delta v^2\) readiness for TDF Phase 3.

**Deliverables:**

- `tdf_m33.fitting.phase2c_model_audit`, `scripts/run_phase2c_model_audit.py`
- `outputs/tables/phase2c_model_audit_summary.csv`, `phase2c_residual_readiness.csv`
- `outputs/reports/phase2c_model_audit_report.md`
- Optional `outputs/figures/phase2c_model_audit_summary.png`

**Acceptance criteria:**

- [x] Reads Phase 2A/2B tables; no TDF τ reconstruction
- [x] Fit mask 0.4–23 kpc (56/58) documented; Burkert r₀ bound flagged
- [x] NFW documented as ΛCDM baseline only; D1 baryonic PASS_WITH_CAVEAT preserved
- [x] Phase 3 input fixed to \(\Delta v^2 = v_{\mathrm{obs}}^2 - v_{\mathrm{bar}}^2\) (Phase 2A)
- [x] Residual smoothness / spike diagnostics for regularization planning

**Status:** Complete.

---

## Phase 3A: Direct pointwise τ-gradient reconstruction

**Goal:** Algebraic τ reconstruction from baryonic \(\Delta v^2\) only—no smoothing, fitting, or AIC/BIC comparison yet.

**Prerequisite:** `phase2c_residual_readiness.csv` / Phase 2A \(\Delta v^2 = v_{\mathrm{obs}}^2 - v_{\mathrm{bar}}^2\).

**Deliverables:**

- `tdf_m33.models.tdf_radial`, `scripts/run_phase3a_tdf_radial_reconstruction.py`
- `outputs/tables/phase3a_tau_radial_reconstruction.csv`, `phase3a_tau_reconstruction_diagnostics.csv`
- Raw τ gradient/profile and direct reconstruction-check figures

**Acceptance criteria:**

- [x] \(d\tau/dr = \Delta v^2/(r K_\tau)\); \(K_\tau=1\) normalization documented
- [x] Identity check: \(v_{\mathrm{TDF,direct}} \approx v_{\mathrm{obs}}\) (not a new halo fit)
- [x] No NFW/Burkert residuals; no lensing; negative \(\Delta v^2\) flagged not clipped
- [x] AIC/BIC comparison deferred to Phase 3B/3C

**Status:** Complete.

---

## Phase 3B: τ smoothing / regularization (planned)

**Goal:** Stabilize \(d\tau/dr\) and low-parameter \(\tau(r)\) for interpretable profiles and formal model comparison.

**Acceptance criteria:**

- [ ] Smoothing or regularization documented; spike mitigation vs Phase 3A raw gradient
- [ ] Eligible for comparison metrics alongside Phase 2 baselines

---

## Phase 3 (overview): τ-gradient and radial τ-profile

**Goal:** Full TDF radial pathway from rotation residuals without an independent halo in the TDF branch.

**Remaining (3B+):** Regularized τ models, \(K_\tau\) sensitivity, comparison table with Phase 2 baselines.

---

## Phase 4: 2D τ-map visualization (optional)

**Goal:** Extend radial τ to a smooth 2D τ-map for spatial interpretation.

**Deliverables:**

- 2D grid or parametric τ-map in `tdf_m33.models` / `tdf_m33.plotting`
- Consistency check: azimuthally averaged 2D map matches radial Phase 3 profile within tolerance

**Acceptance criteria:**

- [ ] 2D map visualization in `outputs/figures/`
- [ ] Documentation of symmetries and assumptions (axisymmetry, etc.)
- [ ] Phase 3 radial results remain reproducible when 2D mode is disabled

---

## Phase 5: Lensing / deflection prediction from the same τ-map

**Goal:** Predict lensing/deflection signatures from the τ-map reconstructed in Phases 3–4 and compare to observational limits.

**Deliverables:**

- `tdf_m33.lensing` prediction module using the **same** τ as rotation
- Consistency report in `outputs/reports/`

**Acceptance criteria:**

- [ ] No additional halo dof added in the TDF lensing pathway
- [ ] Results labeled as prediction/consistency unless direct lensing data are used
- [ ] Limits and uncertainties from `docs/data_sources.md` applied correctly
- [ ] Discussion in outputs aligns with `docs/assumptions_and_limitations.md`

---

## Cross-cutting requirements

- All science parameters in YAML config, not hard-coded in library code.
- Every data transformation documented in `docs/data_sources.md`.
- Conservative language in README, docs, and paper notes at all phases.
