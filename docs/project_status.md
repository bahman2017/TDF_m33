# Project status (TDF–M33 τ-geometry)

Living summary for reviewers. Detailed acceptance criteria: `docs/project_plan.md`.

**Last updated:** Phase 6F first Tier B public pilot batch validation (no local FITS staged).

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
| Phase 6F public data audit | Tier A/B/C documented (PR #7) |
| Phase 6F public pilot staging | Folders + P1–P6 gates; **first-batch validated, 0 FITS staged** |

---

## Active: Phase 6F data acquisition (Tier A preferred; Tier B pilot optional)

**Tier A (preferred):** Exact Corbelli 2014 primary HI + BVIgi stellar FITS — author request; **no direct public FITS found** (audit 2026-05-23).

**Tier B (optional pilot):** Staging under `data/raw/phase6f/public_pilot/`; manual download protocol in `docs/phase6f_public_pilot_download_instructions.md`. P1–P6 gates via `run_phase6f_public_pilot_gates.py`. **Cannot PASS G1/G2.** Label: `PUBLIC_DATA_PILOT_NOT_CORBELLI_PRIMARY`.

**Tier B staged products (local):** none as of first-batch validation. Remaining downloads: IRAM LP006 CO, S4G/LVL IRAC 3.6+4.5 µm, LGLBS HI (or Koch 2018 alternative).

**Public pilot gates:** P1–P4 PENDING, P5 PASS, P6 FAIL, `public_pilot_ready=False`. No scientific τ-map from Tier B until P6 validated reprojection and P1–P5 pass.

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
