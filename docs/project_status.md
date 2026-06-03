# Project status (TDF–M33 τ-geometry)

Living summary for reviewers. Detailed acceptance criteria: `docs/project_plan.md`.

**Last updated:** Phase 6F-source (verified manifests + reference staging).

---

## Completed through Phase 6E + 6F design + 6F-data

| Area | Status |
|------|--------|
| Data + provenance | Phases 1A–1D-D2-B complete |
| Baselines (baryonic, NFW, Burkert) | Phase 2 complete |
| Radial TDF (3A–3D) | Complete; 3-knot competitive on AIC/BIC |
| 2D τ scaffold | Phase 4A–4B complete (**axisymmetric extension**) |
| Deflection proxy | Phase 5A complete (**normalized_proxy**) |
| Dynamical upper bound | Phase 5C-B vs López Fune 2017 (**not lensing**) |
| Publication + manuscript | Phases 6A–6E complete |
| Phase 6F design | Complete (PR #1) |
| Phase 6F-data | Complete (PR #2) — acquisition plan & gates |

---

## Active: Phase 6F-source (verified manifests)

**Goal:** Document authoritative 2D data sources; stage small verified reference files; record checksums.

**Type:** Provenance and selective download — **no** τ reconstruction, **no** deflection, **no** `src/` or Phase 3–5 output changes.

**Deliverables:**

- `docs/phase6f_source_manifest.md`
- `docs/phase6f_dataset_access_notes.md`
- `outputs/reports/phase6f_source_acquisition_status.md`
- `data/raw/phase6f/manifest/phase6f_source_registry.yaml`
- Reference Gratier 2010 VLA HI FITS (3 files) + geometry CSV copy with `CHECKSUMS.sha256`

**Primary stack:** Corbelli 2014 VLA+GBT HI and BVIgi stellar maps — **not acquired**.

**Gate status:** **NOT READY** for Phase 6F-impl.

---

## Critical distinction for readers

| Product | Physical mass-constrained τ-map? |
|---------|----------------------------------|
| Phase 3C \(\tau(r)\) | No — radial, rotation-driven |
| Phase 4A \(\tau(R)\) disk map | **No** — \(\tau_{2\mathrm{D}}=\tau_{\mathrm{radial}}(R)\) |
| Phase 4B sky projection | No — projection of 4A |
| Phase 6F-source reference HI | No — VLA-only cross-check, not primary stack |
| Phase 6F-impl (future) | **Target** — joint rotation + mass geometry + smoothness |

---

## Claim posture

Conservative framing maintained. Reference FITS do not weaken claim boundaries.

---

## Next milestone

1. Obtain Corbelli 2014 **primary** HI + stellar FITS (author request).  
2. Update registry, checksums, pass G1–G6.  
3. **Then** Phase 6F-impl.
