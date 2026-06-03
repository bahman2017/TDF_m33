# Project status (TDF–M33 τ-geometry)

Living summary for reviewers. Detailed acceptance criteria: `docs/project_plan.md`.

**Last updated:** Phase 6F-data (data acquisition & provenance — documentation only).

---

## Completed through Phase 6E + 6F design

| Area | Status |
|------|--------|
| Data + provenance | Phases 1A–1D-D2-B complete |
| Baselines (baryonic, NFW, Burkert) | Phase 2 complete |
| Radial TDF (3A–3D) | Complete; 3-knot competitive on AIC/BIC |
| 2D τ scaffold | Phase 4A–4B complete (**axisymmetric extension**) |
| Deflection proxy | Phase 5A complete (**normalized_proxy**) |
| Dynamical upper bound | Phase 5C-B vs López Fune 2017 (**not lensing**) |
| Publication + manuscript | Phases 6A–6E complete |
| Phase 6F design | Complete (PR #1 → `main` @ `27ab3d61`) |

---

## Active: Phase 6F-data (data readiness)

**Goal:** Catalog external 2D baryonic/geometry products and define provenance gates for mass-constrained τ-map implementation.

**Type:** Documentation only — **no** τ reconstruction, **no** new maps, **no** deflection/lensing runs, **no** changes to Phase 3–5 outputs or `src/`.

**Deliverables (this phase):**

- `docs/phase6f_data_acquisition_plan.md`
- `docs/phase6f_data_provenance_checklist.md`
- `outputs/reports/phase6f_data_readiness_report.md`

**Gate status:** **NOT READY** for Phase 6F-impl (2D HI and stellar maps not in repo).

---

## Critical distinction for readers

| Product | Physical mass-constrained τ-map? |
|---------|----------------------------------|
| Phase 3C \(\tau(r)\) | No — radial, rotation-driven |
| Phase 4A \(\tau(R)\) disk map | **No** — \(\tau_{2\mathrm{D}}=\tau_{\mathrm{radial}}(R)\) |
| Phase 4B sky projection | No — projection of 4A |
| Phase 6F-data | No — provenance catalog only |
| Phase 6F-impl (future) | **Target** — joint rotation + mass geometry + smoothness |

---

## Claim posture

Conservative framing maintained. See `docs/manuscript_allowed_language.md` and Phase 6A claim matrix. Phase 6F-data does not weaken boundaries.

---

## Next milestone

1. Acquire Corbelli et al. 2014 2D HI + stellar mass maps (see acquisition plan).  
2. Pass gates G1–G7 in provenance checklist.  
3. **Then** Phase 6F-impl: implement gated objective and emit `phase6f_*` artifacts.
