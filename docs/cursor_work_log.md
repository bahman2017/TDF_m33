# Cursor work log (TDF_m33)

Chronological notes for agent/human handoff. Not a substitute for `docs/project_plan.md`.

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
