# Project status (TDF–M33 τ-geometry)

Living summary for reviewers. Detailed acceptance criteria: `docs/project_plan.md`.

**Last updated:** Phase 6F design (documentation-only).

---

## Completed through Phase 6E

| Area | Status |
|------|--------|
| Data + provenance | Phases 1A–1D-D2-B complete |
| Baselines (baryonic, NFW, Burkert) | Phase 2 complete |
| Radial TDF (3A–3D) | Complete; 3-knot competitive on AIC/BIC |
| 2D τ scaffold | Phase 4A–4B complete (**axisymmetric extension**) |
| Deflection proxy | Phase 5A complete (**normalized_proxy**) |
| Dynamical upper bound | Phase 5C-B vs López Fune 2017 (**not lensing**) |
| Publication + manuscript | Phases 6A–6E complete |

---

## Active: Phase 6F (design)

**Goal:** Pre-register mass-constrained smooth τ-map reconstruction protocol for M33.

**Deliverables (this phase):**

- `docs/phase6f_mass_constrained_tau_map_protocol.md`
- `docs/phase6f_data_requirements_for_physical_tau_map.md`
- `outputs/reports/phase6f_m33_design_summary.md`

**Not in scope:** Code changes, new maps, new benchmark numbers, deflection re-runs.

---

## Critical distinction for readers

| Product | Physical mass-constrained τ-map? |
|---------|----------------------------------|
| Phase 3C \(\tau(r)\) | No — radial, rotation-driven |
| Phase 4A \(\tau(R)\) disk map | **No** — \(\tau_{2\mathrm{D}}=\tau_{\mathrm{radial}}(R)\) |
| Phase 4B sky projection | No — projection of 4A |
| Phase 6F (future impl) | **Target** — joint rotation + mass geometry + smoothness |

---

## Claim posture

Conservative framing maintained. See `docs/manuscript_allowed_language.md` and Phase 6A claim matrix.

---

## Next milestone

Phase 6F-impl: ingest 2D baryonic maps, implement gated objective, emit `phase6f_*` artifacts.
