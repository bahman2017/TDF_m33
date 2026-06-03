# Phase 6F-data — Data readiness report (M33)

**Report type:** Data acquisition and provenance — **not** τ reconstruction  
**Date:** 2026-05-24  
**Branch:** `feature/phase6f-data-acquisition-provenance`  
**Design baseline:** `main` @ `27ab3d61` (Phase 6F design, PR #1)

---

## Executive summary

Phase 6F-data catalogs external products needed for a **physical mass-constrained** M33 \(\tau(x,y)\) map and defines provenance gates for Phase 6F-impl. **This phase is data-readiness only.**

| Question | Answer |
|----------|--------|
| Are 2D HI and stellar mass maps in the repo? | **No** |
| Is radial rotation + geometry available? | **Yes** (partial) |
| Can Phase 6F-impl start? | **No** — gates G1–G3, G6 fail |
| Were τ maps generated? | **No** |
| Were deflection/lensing steps run? | **No** |
| Were Phase 3–5 outputs modified? | **No** |

**Recommendation:** Proceed with controlled acquisition of Corbelli et al. 2014 2D products per `docs/phase6f_data_acquisition_plan.md` before opening Phase 6F-impl.

---

## What exists today (sufficient / insufficient)

| Input | Location | 6F physical τ-map ready? |
|-------|----------|--------------------------|
| \(v_{\mathrm{obs}}(r)\), \(v_{\mathrm{err}}\) | `data/processed/m33_rotation.csv` | Necessary ✓ |
| \(v_{\mathrm{gas}}(r)\), \(v_{\mathrm{disk}}(r)\) | same (D1 derived) | Necessary ✓; not 2D geometry |
| 1D \(\Sigma_{\mathrm{HI}}(r)\), \(\Sigma_*(r)\) | `corbelli2014_table1_raw.csv` | **Insufficient** as 2D proxy |
| Tilted-ring geometry | `corbelli2014_tilted_ring_geometry_model_shape.csv` | Partial ✓ |
| Phase 4B PA / \(i\) envelope | `phase4b_tau_projection_metadata.csv` | For **existing** τ scaffold only |
| 2D HI map | — | **Missing** |
| 2D stellar mass map | — | **Missing** |
| 2D velocity field | — | **Missing** (recommended) |
| CO / H₂ map | — | Optional; not required for minimum set |

---

## Gate status snapshot

See full criteria: `docs/phase6f_data_provenance_checklist.md`.

| Gate | Status | Blocker |
|------|--------|---------|
| G1 Source traceability | FAIL | No 2D raw files |
| G2 Unit conversion | FAIL | No FITS to validate |
| G3 Coordinate compatibility | FAIL | No common grid |
| G4 Disk geometry | PARTIAL | Radial rings only |
| G5 Uncertainties | PARTIAL | Radial \(v_{\mathrm{err}}\) only |
| G6 Reproducible acquisition | FAIL | Documented plan only |
| G7 No hand-edited maps | PASS | No 2D maps present |
| G8 Claim boundaries | PASS | No τ/deflection in this phase |

**Overall:** **NOT READY** for Phase 6F-impl.

---

## Primary acquisition target (recommended)

**Corbelli et al. 2014** — *A&A* **572**, A23  
DOI: [10.1051/0004-6361/201424033](https://doi.org/10.1051/0004-6361/201424033)

Priority files (not yet in repository):

1. VLA+GBT HI surface-density map (moment-0) — document 20″ vs 130″ choice  
2. BVIgi stellar mass surface-density map  
3. HI velocity field (moment-1) — recommended  
4. Confirm alignment with existing tilted-ring extract  

Secondary references: THINGS, Little THINGS (cross-check only); Gratier et al. CO (optional).

---

## Claim control (unchanged)

- Phase **4A/4B** products remain **axisymmetric radial extensions**, not mass-constrained physical τ-maps.
- Phase **5A** deflection remains **`normalized_proxy`** — not calibrated lensing.
- Phase **5C-B** López Fune comparison is **dynamical upper bound only**.
- **Dark matter is not disproven.** No M33 lensing detection claim.
- Phase 6F-data introduces **no new scientific numbers**.

---

## Uncertainty handling plan (draft — activates with data)

| Term | Source | Status |
|------|--------|--------|
| \(\mathcal{L}_{\mathrm{rotation}}\) radial | `v_err_kms` in processed CSV | Available |
| \(\mathcal{L}_{\mathrm{rotation}}\) 2D | Moment-1 / ring errors | Pending acquisition |
| \(\mathcal{L}_{\mathrm{mass}}\) HI | Beam noise / rms map from cube | Pending |
| \(\mathcal{L}_{\mathrm{mass}}\) stars | Synthesis uncertainty or conservative weight | Pending |
| Correlated errors | Document beam coupling | Pending analysis |

---

## Next actions (ordered; not executed in 6F-data)

1. Obtain Corbelli 2014 2D FITS/maps via official archive; log checksums.  
2. Register manifest IDs: `corbelli2014_hi_2d_map`, `corbelli2014_stellar_mass_2d_map`.  
3. Implement validation placeholders (`validate_phase6f_baryonic_maps.py` — future).  
4. Re-run checklist; update this report to PASS when evidence exists.  
5. Only then branch Phase 6F-impl and implement protocol in `docs/phase6f_mass_constrained_tau_map_protocol.md`.

**Do not** run `# python scripts/run_phase6f_mass_constrained_tau_map.py` until sign-off.

---

## Document index

| File | Purpose |
|------|---------|
| `docs/phase6f_data_acquisition_plan.md` | Full candidate catalog |
| `docs/phase6f_data_provenance_checklist.md` | Gate definitions |
| `docs/phase6f_data_requirements_for_physical_tau_map.md` | Scientific requirements |
| `docs/phase6f_mass_constrained_tau_map_protocol.md` | Fit protocol (blocked) |
