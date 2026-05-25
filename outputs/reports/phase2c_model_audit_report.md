# Phase 2C — Model comparison audit (M33)

**Scope:** Audit and consolidation of Phase 2A (baryonic-only) and Phase 2B (NFW/Burkert halo baselines). **No TDF τ reconstruction has been performed.**

## Fit mask (Phase 2B metrics)

- Range: **0.4 ≤ R ≤ 23.0 kpc**
- Points in mask: **56 / 58**

## Baryonic velocities (mandatory caveat)

- Components are **D1-derived** from Corbelli et al. 2014 Table 1 surface densities.
- `data_quality_flag`: **derived_baryonic_velocity_pass_with_caveat**
- Fig. 12 digitization is sanity-check only, not canonical velocities.

## Model summaries (fit-masked, Phase 2B comparison table)

### baryonic_only

- RMSE: 58.56 km/s
- χ²: 20095.9, reduced χ²: 365.380
- k: 0, AIC: 20095.9, BIC: 20095.9
- Negative Δv² (halo-model residuals): 0

### nfw

- RMSE: 4.16 km/s
- χ²: 64.0, reduced χ²: 1.207
- k: 2, AIC: 68.0, BIC: 72.0
- Negative Δv² (halo-model residuals): 21

### burkert

- RMSE: 23.02 km/s
- χ²: 2337.9, reduced χ²: 44.112
- k: 2, AIC: 2341.9, BIC: 2346.0
- Negative Δv² (halo-model residuals): 20

## Phase 2A full-grid baryonic baseline (58 rows)

- RMSE: 57.62 km/s (all radii)
- χ²: 20111.1, reduced χ²: 352.827
- Negative baryonic Δv²: 0

## NFW halo sanity (comparison baseline, not TDF)

- Fitted ρ_s = 6.3082e+06 M☉/kpc³, r_s = 13.201 kpc
- Approx. c = r_s/R_max ≈ 0.57 (R_max = 23.0 kpc; not virial)
- M(<23.0 kpc) ≈ 6.811e+10 M☉ (enclosed mass at fit outer radius; not M_vir)
- Corbelli 2014 sanity ref: c ≈ 9.5, M_h ≈ 4.30e+11 M☉ (not acceptance criteria)

**v_halo at selected radii [km/s]:**
- R = 5.0 kpc: 85.38
- R = 10.0 kpc: 102.09
- R = 15.0 kpc: 108.99
- R = 23.0 kpc: 112.85

NFW reduced χ² ≈ 1 on the fit mask is expected for a standard halo fit; this does **not** validate TDF or disprove dark matter.

## Burkert halo sanity

- Fitted ρ₀ = 1.7642e+03 M☉/kpc³ = **0.0018 M☉/pc³**
- Fitted r₀ = **199.986 kpc**
- Corbelli 2014 BVI sanity ref: r₀ ≈ 7.5 kpc, ρ₀ ≈ 0.018 M☉/pc³

### ⚠ Burkert boundary warning

Burkert **r₀ hit the upper fit bound (~200 kpc)**. The fit is **poorly constrained** and **not publication-stable** for direct comparison to Corbelli BVI parameters. Do not over-interpret Burkert metrics vs NFW.


## Phase 3 prerequisite (τ reconstruction)

- Use **baryonic residual only**: Δv² = v_obs² − v_bar² from Phase 2A profile.
- Do **not** use NFW/Burkert-subtracted residuals for TDF τ-gradient work.
- **No τ-profile, K_τ fit, 2D τ-map, or lensing outputs exist yet.**

## Residual readiness (Phase 2A Δv²)

- Points: 58
- Negative Δv²: 0
- All Δv² positive: **True**
- Obvious gradient spikes (heuristic): 9
- Phase 3 smoothing/regularization likely needed: **True**

## Claim control

- Phase 2 = **comparison baselines only** (baryonic, NFW, Burkert).
- No dark-matter replacement or disproof claim is supported at this stage.
