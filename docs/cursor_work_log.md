# Cursor work log (TDF_m33)

Chronological notes for agent/human handoff. Not a substitute for `docs/project_plan.md`.

---

## 2026-05-23 — Unicode hygiene for public pilot text files

**Patch:** Added `check_text_file_unicode_hygiene.py`; normalized LF and removed em-dash
from machine-readable Tier B staging files. No gate or scientific logic changes.

---

## 2026-05-23 — Phase 6F public pilot source staging

**Branch:** `feature/phase6f-public-pilot-source-staging`

**Added:** `public_pilot/` folder layout, source registry, P1–P6 gate checker, inventory/checksum
scripts, dry-run downloader, download instructions.

**Unchanged:** Corbelli G1/G2/G8 FAIL, strict mode blocked, no scientific τ-map, no lensing.

---

## 2026-05-23 — Phase 6F public data acquisition audit

**Branch:** `feature/phase6f-public-data-acquisition-audit`

**Added:** Tier A/B/C policy docs, public candidate YAML registry, audit script, tests.

**Finding:** No exact Corbelli 2014 primary HI/BVIgi FITS on public archives (2026-05-23).
Fastest Tier B pilot: LGLBS HI v1.0 + Spitzer S4G IRAC + IRAM LP006 CO.

**Unchanged:** G1/G2/G8 FAIL, strict Corbelli mode blocked, no scientific τ-map claim.
Tier B cannot PASS Corbelli primary gates.

---

## 2026-05-23 — Phase 6F script import bootstrap (PR #5 hotfix)

**Branch:** `feature/phase6f-nonspherical-disk-tau-map-engine`

**Fix:** Added `scripts/_bootstrap.py` and wired Phase 6F scripts to insert `src/` on
`sys.path` before importing `tdf_m33`, so direct execution from repo root works without
prior `pip install -e .`.

**Unchanged:** G1–G8 gate logic, G8 validated reprojection requirement, strict-mode block
(`BLOCKED_PENDING_PRIMARY_CORBELLI_MAPS`), reference-proxy marking
(`REFERENCE_ONLY_NOT_FOR_SCIENTIFIC_CLAIMS`).

---

## 2026-06-03 — PR #4 review fix: G8 reprojection gate

**Patch:** Added G8_primary_map_reprojection_ready; blocked scientific mode on placeholder zoom; Neumann BC disabled (NotImplementedError).

**scientific_ready** now requires G1, G2, G3, G4, G5, G7, G8 (G6 diagnostic only).

---

## 2026-06-03 — Phase 6F non-spherical τ-map engine

**Branch:** `feature/phase6f-nonspherical-disk-tau-map-engine`

**Task:** Disk-plane field solver with G1–G7 data gates; Kg / kappa_tau notation.

**Created:** `src/tdf_m33/maps/*`, scripts, config, tests, `docs/phase6f_nonspherical_tau_map_engine.md`

**Strict mode:** blocked until primary Corbelli HI + stellar FITS acquired.

**Not done:** scientific τ-map claims, deflection re-runs, Phase 3–5 output changes.

---

## 2026-06-03 — Phase 6F-source (verified manifests)

**Branch:** `feature/phase6f-source-acquisition-manifest`

**Task:** Authoritative source manifests, access notes, checksum-verified staging for 2D τ inputs.

**Created:**

- `docs/phase6f_source_manifest.md`
- `docs/phase6f_dataset_access_notes.md`
- `outputs/reports/phase6f_source_acquisition_status.md`
- `data/raw/phase6f/manifest/phase6f_source_registry.yaml`
- `data/raw/phase6f/CHECKSUMS.sha256`

**Staged (small, license-allowed):**

- Gratier 2010 VLA HI 12″ reference FITS (area, cent, noise) — **not** primary Corbelli VLA+GBT stack
- Corbelli 2014 tilted-ring geometry CSV copy

**Explicitly not done:**

- No Corbelli 2014 primary HI / stellar FITS (author request required)
- No τ reconstruction, deflection, or model changes
- No fabricated checksums for absent files

**Next handoff:** Author acquisition of Corbelli primary products → update registry → pass G1–G6.

---

## 2026-05-24 — Phase 6F-data (data acquisition & provenance)

**Branch:** `feature/phase6f-data-acquisition-provenance`

**Task:** Catalog external 2D products for physical M33 τ-map; define provenance gates; block 6F-impl until ready.

**Created:**

- `docs/phase6f_data_acquisition_plan.md`
- `docs/phase6f_data_provenance_checklist.md`
- `outputs/reports/phase6f_data_readiness_report.md`

**Updated:**

- `README.md`, `docs/project_status.md`, `docs/roadmap.md`, `docs/reproducibility_commands.md`

**Explicitly not done:**

- No τ reconstruction or `phase6f_*` map outputs
- No deflection/lensing proxy runs
- No changes to `src/`, benchmarks, Phase 3–5 numerical results
- No fabricated downloads or 2D pixel maps

**Gate snapshot:** G1–G3, G6 FAIL (2D maps absent); G4–G5 PARTIAL; G7–G8 PASS.

**Next handoff:** Acquire Corbelli 2014 2D HI + stellar products; pass checklist → Phase 6F-impl.

---

## 2026-05-24 — Phase 6F design (documentation-first)

**Branch:** `feature/phase6f-mass-constrained-tau-map`

**Task:** Define pre-registered protocol for mass-constrained smooth M33 τ-map reconstruction.

**Created:**

- `docs/phase6f_mass_constrained_tau_map_protocol.md`
- `docs/phase6f_data_requirements_for_physical_tau_map.md`
- `outputs/reports/phase6f_m33_design_summary.md`
- `docs/project_status.md`, `docs/roadmap.md`, `docs/reproducibility_commands.md` (canonical repro doc)

**Updated:**

- `README.md` — Phase 6F status
- `docs/project_plan.md` — Phase 6F section

**Explicitly not done:**

- No changes to `src/`, maps, tables, figures, benchmarks
- No new scientific numbers
- No Phase 6F pipeline scripts executed

**Rationale captured:** Phase 4A metadata documents axisymmetric radial extension only; Phase 6F must joint-fit smoothness + baryonic geometry before freezing τ for any renewed deflection step.

**Next handoff:** Phase 6F-impl — acquire 2D HI/stellar maps per data requirements doc.

---

## Prior work (summary)

Phases 0–6E implemented and audited on `main` per README status table. See `outputs/reports/phase6a_publication_results_summary.md` for supported results snapshot.
