# Project status (TDF–M33 τ-geometry)

Living summary for reviewers. Detailed acceptance criteria: `docs/project_plan.md`.

**Last updated:** Phase 6F non-spherical τ-map engine (strict gates).

---

## Completed through Phase 6E + 6F design/data/source

| Area | Status |
|------|--------|
| Data + provenance | Phases 1A–1D-D2-B complete |
| Baselines (baryonic, NFW, Burkert) | Phase 2 complete |
| Radial TDF (3A–3D) | Complete; 3-knot competitive on AIC/BIC |
| 2D τ scaffold | Phase 4A–4B complete (**axisymmetric extension**) |
| Deflection proxy | Phase 5A complete (**normalized_proxy**) |
| Dynamical upper bound | Phase 5C-B vs López Fune 2017 (**not lensing**) |
| Publication + manuscript | Phases 6A–6E complete |
| Phase 6F design / data / source | Complete (PR #1–#3) |
| Phase 6F engine | Implemented — **scientific τ-map blocked** |

---

## Active: Phase 6F engine (gated implementation)

**Goal:** Non-spherical disk-plane τ field solver with data gates (Kg, κ_τ notation).

**Scientific status:** **BLOCKED** — primary Corbelli 2014 HI + stellar maps missing; **validated WCS reprojection (G8) not implemented**.

**Strict mode:** `build_phase6f_nonspherical_tau_map.py` → `BLOCKED_PENDING_PRIMARY_CORBELLI_MAPS`

Placeholder zoom alignment (`PLACEHOLDER_NOT_SCIENTIFIC_WCS_REPROJECTION`) cannot be used in scientific mode.

**Reference mode:** `--allow-reference-proxy` only; outputs marked `REFERENCE_ONLY_NOT_FOR_SCIENTIFIC_CLAIMS`.

---

## Critical distinction for readers

| Product | Physical mass-constrained τ-map? |
|---------|----------------------------------|
| Phase 4A \(\tau(R)\) disk map | **No** — axisymmetric radial extension |
| Phase 6F engine (blocked) | **Target** — non-spherical disk-plane field |
| Phase 6F reference proxy | **No** — smoke test only |

---

## Claim posture

No dark-matter disproof; no M33 lensing confirmation. Phase 3–5 outputs unchanged.

---

## Next milestone

Acquire primary Corbelli 2014 maps **and** implement validated WCS→disk-plane reprojection (G8) → pass all required gates → scientific Phase 6F build.
