# Phase 6A — Publication results summary (M33 TDF)

**Purpose:** Consolidate supported results, caveats, and future work for manuscript drafting. This report does not refit models or change prior numerical outputs.

## Strongest supported result

The strongest current result is **rotation-dynamics consistency** of a **low-parameter 3-knot τ-gradient model** (`tdf_lowparam_3knot`) on the Corbelli 2014 rotation curve with D1-derived baryonic components: RMSE ≈ 3.51 km/s, AIC ≈ 63.0, BIC ≈ 69.0 on the 0.4–23 kpc fit mask (n=56), competitive with NFW (AIC ≈ 68.0).

## Key quantitative results (fit mask 0.4–23 kpc)

| Model | RMSE [km/s] | χ² | AIC | BIC | Notes |
|-------|-------------|-----|-----|-----|-------|
| Baryonic only | 58.56 | 20096 | 20096 | 20096 | No halo/TDF |
| NFW (ΛCDM baseline) | 4.16 | 64.0 | 68.0 | 72.0 | 2-parameter halo |
| Burkert | 23.02 | 2338 | 2342 | 2346 | r0_at_upper_bound |
| TDF 3-knot | 3.51 | 57.0 | 63.0 | 69.0 | K_τ=1 fixed |
| TDF 5-knot | 3.35 | 56.3 | 66.3 | 76.5 | Lowest RMSE; higher BIC penalty |

## Phase 3D stability (summary)

3-knot TDF beats NFW on AIC/BIC at default fit mask (0.4–23 kpc); fit-mask variants keep 3-knot competitive except stricter 1.0–22.0 kpc mask; K_tau sweep shows expected scale degeneracy with max RMSE spread 0.42 km/s. Qualify: rotation-only; D1-derived baryons PASS_WITH_CAVEAT.

## Lensing and external constraints

- **Deflection:** `normalized_proxy` only (Phase 5A); **no** arcsec calibration.
- **López Fune 2017:** dynamical upper-bound consistency — **PASS_WITH_CAVEAT** (M_tau/M_López ≈ 1.12 at 22.7 kpc); **not** weak lensing.
- **Weak lensing:** not available (`m33_direct_weak_lensing_gap`).

## Claim control snapshot

- Supported: 7
- Caveated: 1
- Future work: 1
- Prohibited affirmative claims: 1 (must not appear in manuscript)

Full matrix: `outputs/tables/phase6a_claim_traceability_matrix.csv`.

## What remains future work

1. Physical `alpha_tau_scale` / arcsec lensing calibration.
2. Independent M33 weak-lensing comparison.
3. Improved baryonic velocity systematics beyond D1 PASS_WITH_CAVEAT.

## Explicit non-claims

- Dark matter is **not** disproven or replaced.
- Phase 5A deflection is a **prediction scaffold**, not observational detection.
- López Fune comparison is **dynamical scale consistency**, not τ-lensing validation.

## Artifacts

- Key results: `outputs/tables/phase6a_key_results_table.csv`
- Claim traceability: `outputs/tables/phase6a_claim_traceability_matrix.csv`
- Reproducibility: `outputs/reports/phase6a_reproducibility_commands.md`
