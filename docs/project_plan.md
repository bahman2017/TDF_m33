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

## Phase 3B-A: τ-gradient smoothing / regularization

**Goal:** Smooth raw \(d\tau/dr\) from Phase 3A (Gaussian and spline methods) while preserving baryonic \(\Delta v^2\) structure; no AIC/BIC yet.

**Deliverables:**

- `tdf_m33.models.tdf_regularization`, `scripts/run_phase3b_tdf_regularized_reconstruction.py`
- `outputs/tables/phase3b_tau_regularized_profiles.csv`, `phase3b_tau_regularization_diagnostics.csv`
- Regularized gradient/profile and tradeoff figures

**Acceptance criteria:**

- [x] Gaussian (σ_kpc) and spline (fixed s) from config; not tuned to minimize RMSE
- [x] Raw and smoothed τ both available; negative \(v_\tau^2\) flagged not clipped
- [x] Spike/smoothness metrics before vs after; AIC/BIC deferred to Phase 3C

**Status:** Complete.

---

## Phase 3C: Low-parameter knot τ-gradient model comparison

**Goal:** Fairer TDF comparison vs NFW/Burkert using k=3,4,5 fitted knot values (K_τ fixed).

**Deliverables:**

- `tdf_m33.models.tdf_lowparam`, `scripts/run_phase3c_tdf_lowparam_model.py`
- `phase3c_tdf_lowparam_*` tables, `phase3c_combined_model_comparison.csv`, figures

**Acceptance criteria:**

- [x] Fit on Corbelli mask 0.4–23 kpc; v_model² = v_bar² + r K_τ dτ/dr
- [x] AIC/BIC for low-parameter TDF only (3A/3B not in formal comparison)
- [x] Combined table with baryonic, NFW, Burkert, TDF knot models; Burkert boundary preserved

**Status:** Complete.

---

## Phase 3D: TDF sensitivity and robustness audit

**Goal:** Knot-count, K_τ, smoothing σ, and fit-mask stability before 2D τ or lensing.

**Deliverables:**

- `tdf_m33.fitting.phase3d_tdf_sensitivity`, `scripts/run_phase3d_tdf_sensitivity.py`
- `phase3d_*` tables, `phase3d_tdf_sensitivity_report.md`, summary figure

**Acceptance criteria:**

- [x] K_τ sweep documented as normalization / scale degeneracy audit
- [x] Phase 3C knot ranking vs NFW; fit-mask variants for 3-knot
- [x] Gaussian σ diagnostic from Phase 3B; no lensing; no DM disproof claim

**Status:** Complete.

---

## Phase 4A: Axisymmetric disk-plane 2D τ map

**Goal:** Extend the validated Phase 3C radial τ model to a controlled 2D disk-plane map before morphology or lensing.

**Deliverables:**

- `tdf_m33.models.tdf_map2d`, `tdf_m33.fitting.phase4a_tdf_2d_map`, `scripts/run_phase4a_tdf_2d_map.py`
- `phase4a_tau_2d_map.npz`, consistency/metadata tables, summary figures

**Acceptance criteria:**

- [x] τ₂D(x,y)=τ_rad(R) from `tdf_lowparam_3knot`; K_τ=1 fixed; no new parameters
- [x] Outside radial range masked; azimuthal average consistency reported
- [x] No lensing; no NFW/Burkert residuals; baryonic/K_τ caveats preserved

**Status:** Complete.

---

## Phase 4B-A: Disk-to-sky τ projection (geometry only)

**Goal:** Project the Phase 4A disk-plane τ map to documented sky-plane coordinates for future lensing—without changing τ values or fitting new parameters.

**Deliverables:**

- `tdf_m33.models.tdf_projection`, `tdf_m33.fitting.phase4b_tau_projection`, `scripts/run_phase4b_tau_projection.py`
- `phase4b_tau_sky_projected_map.npz`, projection metadata, geometry check figures

**Acceptance criteria:**

- [x] Inclination/PA from config (placeholders flagged when null)
- [x] τ array unchanged at grid indices; masked regions preserved
- [x] No lensing; no morphology; no new τ fit

**Status:** Complete.

---

## Phase 4B-B: Lock Corbelli 2014 projection geometry

**Goal:** Replace placeholder i/PA with documented Corbelli et al. 2014 tilted-ring geometry before lensing.

**Deliverables:**

- `corbelli2014_tilted_ring_geometry_model_shape.csv` (Fig. 3 model-shape digitization)
- Radial `i(R)`, `PA(R)` projection in `tdf_projection`; metadata flags `placeholder_geometry_flag: false`

**Acceptance criteria:**

- [x] Geometry from Corbelli 2014 §4.1 / Fig. 3 (model-shape), not config ballpark placeholders
- [x] `geometry_mode: radial_tilted_ring` with traceable ring table
- [x] Global inner-disk reference values documented (54°, 22°) for comparison only
- [x] No lensing; τ values unchanged

**Status:** Complete.

---

## Phase 4B+ (planned)

**Phase 4B+ (optional):** morphology-aware or non-axisymmetric τ extensions after projection review.

---

## Phase 5A: Normalized deflection-proxy from frozen sky τ

**Goal:** First lensing/deflection **prediction scaffold** from the same frozen Phase 4B sky-plane τ map used for rotation—without fitting lensing data or adding a separate halo.

**Deliverables:**

- `src/tdf_m33/lensing/deflection.py` — τ gradients, α proxy, |α|, optional κ proxy
- `src/tdf_m33/lensing/phase5a_lensing_prediction.py` + `scripts/run_phase5a_lensing_prediction.py`
- `outputs/maps/phase5a_tau_deflection_proxy_map.npz`
- Metadata, summary, report, magnitude/vector/convergence figures

**Model:** α_x = −α_τ_scale ∂τ/∂x_sky, α_y = −α_τ_scale ∂τ/∂y_sky with `alpha_tau_scale = 1.0` and `units = normalized_proxy`.

**Acceptance criteria:**

- [x] Source map: `phase4b_tau_sky_projected_map.npz`; `source_model = tdf_lowparam_3knot`
- [x] `placeholder_geometry_flag = false`; `geometry_mode = radial_tilted_ring`
- [x] No separate halo; no lensing-only fit; no observational limit comparison (none documented in `data_sources.md`)
- [x] Baryonic PASS_WITH_CAVEAT and K_τ normalization caveats in metadata/report
- [x] Results labeled prediction/consistency scaffold only; no dark-matter disproof claim

**Status:** Complete.

**Phase 5B (planned):** Physical α_τ calibration; observational limits once documented in `docs/data_sources.md`.

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

**Goal:** Predict lensing/deflection signatures from the τ-map reconstructed in Phases 3–4; compare to observational limits only when documented.

**Phase 5A (complete):** Normalized deflection-proxy maps from frozen sky τ (see section above).

**Phase 5B (planned):** Physical calibration and limit comparison when sources exist in `docs/data_sources.md`.

**Acceptance criteria (5A):**

- [x] No additional halo dof in the TDF lensing pathway
- [x] Results labeled prediction/consistency; `normalized_proxy` units
- [ ] Observational limits from `docs/data_sources.md` (Phase 5B)
- [x] Discussion aligns with `docs/assumptions_and_limitations.md`

---

## Cross-cutting requirements

- All science parameters in YAML config, not hard-coded in library code.
- Every data transformation documented in `docs/data_sources.md`.
- Conservative language in README, docs, and paper notes at all phases.
