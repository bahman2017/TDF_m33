# Reproducibility commands (TDF–M33)

Canonical command reference. Run from repository root with venv active. Config: `configs/m33_default.yaml`.

A Phase 6A snapshot also lives at `outputs/reports/phase6a_reproducibility_commands.md` (generated alongside publication audit).

---

## Environment

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -e .   # recommended; not required for Phase 6F scripts below
python -m pytest -v
```

Phase 6F scripts (`run_phase6f_tau_map_gates.py`, `build_phase6f_nonspherical_tau_map.py`,
`plot_phase6f_tau_map_diagnostics.py`) bootstrap `src/` on `sys.path` automatically, so they
can be run directly from the repository root without a prior editable install. Editable install
remains recommended for development and for other scripts in this repository.

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

**Documentation only.** Design merged to `main` (PR #1).

Design docs:

```bash
# Read-only — no pipeline execution required
cat docs/phase6f_mass_constrained_tau_map_protocol.md
cat docs/phase6f_data_requirements_for_physical_tau_map.md
cat outputs/reports/phase6f_m33_design_summary.md
```

---

## Phase 6F-source — verified manifests (current)

**Manifest + reference staging.** Primary Corbelli stack not acquired. No τ reconstruction.

Docs and registry:

```bash
cat docs/phase6f_source_manifest.md
cat docs/phase6f_dataset_access_notes.md
cat outputs/reports/phase6f_source_acquisition_status.md
cat data/raw/phase6f/manifest/phase6f_source_registry.yaml
```

Verify committed checksums:

```bash
cd data/raw/phase6f && shasum -a 256 -c CHECKSUMS.sha256
```

Reproducible reference HI download (Gratier 2010 — **reference only**):

```bash
mkdir -p data/raw/phase6f/reference/gratier2010_vla_hi_12sec
BASE=https://perso.astrophy.u-bordeaux.fr/~pgratier/data/fits
for f in M33_HI_12sec-area.fits M33_HI_12sec-cent.fits M33_HI_12sec-noise.fits; do
  curl -L -o "data/raw/phase6f/reference/gratier2010_vla_hi_12sec/$f" "$BASE/$f"
done
cd data/raw/phase6f && shasum -a 256 -c CHECKSUMS.sha256
```

Optional CO integrated map (not committed; ~3.7 MB):

```bash
# curl -L -o /tmp/ico.fits https://www.iram.fr/ILPA/LP006/ico.fits
```

**Future placeholders (blocked until primary stack verified):**

```bash
# python scripts/acquire_phase6f_primary_corbelli2014.py
# python scripts/verify_phase6f_checksums.py --root data/raw/phase6f
# python scripts/validate_phase6f_baryonic_maps.py
# python scripts/run_phase6f_mass_constrained_tau_map.py
```

---

## Phase 6F-engine — non-spherical disk-plane τ-map (strict gates)

Config: `configs/phase6f_nonspherical_tau_map.yaml`

Direct execution from repository root (no editable install required):

```bash
python scripts/run_phase6f_tau_map_gates.py
python scripts/build_phase6f_nonspherical_tau_map.py
python scripts/plot_phase6f_tau_map_diagnostics.py
```

Expected strict-mode result: exit code 2, `BLOCKED_PENDING_PRIMARY_CORBELLI_MAPS`, gate report at
`outputs/reports/phase6f/phase6f_tau_map_gate_report.md`.

Reference-only smoke test (not for scientific claims):

```bash
python scripts/build_phase6f_nonspherical_tau_map.py --allow-reference-proxy
python scripts/plot_phase6f_tau_map_diagnostics.py --reference-only
```

---

## Phase 6F-data — data acquisition & provenance

**Data-readiness only.** No τ reconstruction, no new maps, no deflection runs.

Readiness docs:

```bash
cat docs/phase6f_data_acquisition_plan.md
cat docs/phase6f_data_provenance_checklist.md
cat outputs/reports/phase6f_data_readiness_report.md
```

**Future acquisition placeholders (not implemented; do not invent files):**

```bash
# python scripts/acquire_corbelli2014_hi_2d_map.py --manifest data/raw/sources_manifest.yaml
# python scripts/acquire_corbelli2014_stellar_mass_2d_map.py --manifest data/raw/sources_manifest.yaml
# python scripts/validate_phase6f_baryonic_maps.py --hi ... --stars ... --geometry ...
# python scripts/run_phase6f_data_readiness_audit.py
```

**Phase 6F-impl placeholders (blocked until data gates pass):**

```bash
# python scripts/run_phase6f_mass_constrained_tau_map.py
# python scripts/run_phase6f_decision_gate_audit.py
# python scripts/run_phase6f_mass_alignment_diagnostics.py
```

Expected future artifacts: protocol §7 in `docs/phase6f_mass_constrained_tau_map_protocol.md`.

---

## Claim control reminder

Prior phase outputs are **read-only** inputs to audits. Phase 6F-data does not refit or overwrite Phases 2–5 maps. Phase 6F-impl is blocked until data readiness gates pass. Deflection remains `normalized_proxy` until a future gated calibration phase is pre-registered.
