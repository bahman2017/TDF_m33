# Project status (TDF–M33 τ-geometry)

Living summary for reviewers. Detailed acceptance criteria: `docs/project_plan.md`.

**Last updated:** Phase 6F public data acquisition audit (Tier A/B/C).

---

## Completed through Phase 6E + 6F design/data/source/engine

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
| Phase 6F engine + bootstrap | Implemented (PR #4/#5) — **scientific τ-map blocked** |
| Phase 6F public data audit | Tier A/B/C documented — **no Tier B ingest yet** |

---

## Active: Phase 6F data acquisition (Tier A preferred; Tier B pilot optional)

**Tier A (preferred):** Exact Corbelli 2014 primary HI + BVIgi stellar FITS — author request; **no direct public FITS found** (audit 2026-05-23).

**Tier B (optional pilot):** LGLBS HI v1.0 + Spitzer S4G IRAC + IRAM LP006 CO — public routes documented; **not Corbelli replication**; cannot PASS G1/G2.

**Scientific status:** **BLOCKED** — G1/G2 primary Corbelli maps missing; G8 validated reprojection not implemented.

**Strict mode:** `BLOCKED_PENDING_PRIMARY_CORBELLI_MAPS`

**Reference mode:** `--allow-reference-proxy` → `REFERENCE_ONLY_NOT_FOR_SCIENTIFIC_CLAIMS`

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
