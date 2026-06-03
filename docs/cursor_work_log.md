# Cursor work log (TDF_m33)

Chronological notes for agent/human handoff. Not a substitute for `docs/project_plan.md`.

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
