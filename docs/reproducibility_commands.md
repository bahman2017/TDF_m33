# Reproducibility commands (TDF–M33)

Canonical command reference. Run from repository root with venv active. Config: `configs/m33_default.yaml`.

A Phase 6A snapshot also lives at `outputs/reports/phase6a_reproducibility_commands.md` (generated alongside publication audit).

---

## Environment

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -e .
python -m pytest -v
```

---

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

---

## Phase 2 — baselines

```bash
python scripts/run_phase2a_baryonic_only.py
python scripts/run_phase2b_halo_baselines.py
python scripts/run_phase2c_model_audit.py
```

---

## Phase 3 — TDF radial pathway

```bash
python scripts/run_phase3a_tdf_radial_reconstruction.py
python scripts/run_phase3b_tdf_regularized_reconstruction.py
python scripts/run_phase3c_tdf_lowparam_model.py
python scripts/run_phase3d_tdf_sensitivity.py
```

---

## Phase 4 — τ maps (axisymmetric scaffold)

```bash
python scripts/run_phase4a_tdf_2d_map.py
python scripts/run_phase4b_tau_projection.py
```

> **Note:** Phase 4A outputs are radial extensions, not mass-constrained τ-maps (`docs/phase6f_mass_constrained_tau_map_protocol.md`).

---

## Phase 5 — deflection proxy and limits

```bash
python scripts/run_phase5a_lensing_prediction.py
python scripts/run_phase5b_lensing_calibration_audit.py
python scripts/run_phase5b_constraint_source_audit.py
python scripts/audit_lopez_fune_2017_source.py
python scripts/validate_lopez_fune_2017_extracted_constraints.py
python scripts/run_phase5c_upper_bound_consistency.py
```

---

## Phase 6A–6E — publication and manuscript

```bash
python scripts/run_phase6a_publication_audit.py
python scripts/run_phase6b_manuscript_audit.py
python scripts/run_phase6c_manuscript_draft_audit.py
python scripts/run_phase6d_manuscript_polish_audit.py
python scripts/run_phase6e_submission_package_audit.py
python scripts/prepare_paper_figures.py
```

---

## Phase 6F — mass-constrained τ-map (design phase)

**Documentation only in Phase 6F design.** No implementation scripts yet.

Design docs:

```bash
# Read-only — no pipeline execution required for design acceptance
cat docs/phase6f_mass_constrained_tau_map_protocol.md
cat docs/phase6f_data_requirements_for_physical_tau_map.md
cat outputs/reports/phase6f_m33_design_summary.md
```

**Future placeholders (not implemented; do not invent outputs):**

```bash
# python scripts/run_phase6f_mass_constrained_tau_map.py
# python scripts/run_phase6f_decision_gate_audit.py
# python scripts/run_phase6f_mass_alignment_diagnostics.py
```

Expected future artifacts (when implemented): see protocol §7 in `docs/phase6f_mass_constrained_tau_map_protocol.md`.

---

## Claim control reminder

Prior phase outputs are **read-only** inputs to audits. Phase 6F design does not refit or overwrite Phases 2–5 maps. Deflection remains `normalized_proxy` until a future gated calibration phase is pre-registered.
