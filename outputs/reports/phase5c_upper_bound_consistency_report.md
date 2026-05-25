# Phase 5C-B — Upper-bound dynamical consistency (López Fune 2017)

**Scope:** Enclosed-mass-style scale check only. **Not** weak lensing. **Not** a τ-map or deflection comparison.

## Method

- Same frozen τ branch: `tdf_lowparam_3knot`, fixed `K_tau`, no new fit.
- Effective mass proxy: `M_tau_eff(<r) = r_kpc * v_tau^2 / G` with `G = 4.30091e-06` kpc (km/s)² M☉⁻¹.
- `v_tau^2` from Phase 3C (`v_tau_squared` = r K_τ dτ/dr).
- Reference: López Fune et al. 2017 BRK `M_enclosed_23kpc` = 6.700e+10 ± 1.200e+10 M☉ (dynamical halo, not lensing).

## Result at comparison radius

- Radius used: **22.72** kpc (target 23.00 kpc; nearest_at_max_radius).
- `M_tau_eff`: **7.511e+10** M☉
- López Fune enclosed reference: **6.700e+10** M☉
- Ratio M_tau / M_López: **1.121**
- **Consistency status:** `PASS_WITH_CAVEAT`
- M_tau_eff (7.511e+10 M_sun) <= López Fune upper envelope 7.900e+10 M_sun (M_enclosed_23kpc + 1.0σ uncertainty).

## Guardrails

- Deflection remains **`normalized_proxy`**; no arcsec calibration.
- `observational_limits.enabled` remains **false**.
- No `alpha_tau_scale` fit; no separate halo; no lensing-only τ field.
- **No** observational detection claim; **no** dark-matter replacement claim.

## Circularity

López Fune et al. 2017 uses Corbelli et al. 2014 baryonic/rotation inputs; partial circularity with this TDF branch. Dynamics/rotation-based reference only.

## Artifacts

- Profile: `/Users/bahmanmasarratbakhsh/TDF_projects/Tdf_m33/outputs/tables/phase5c_tau_mass_proxy_profile.csv`
- Summary: `/Users/bahmanmasarratbakhsh/TDF_projects/Tdf_m33/outputs/tables/phase5c_upper_bound_consistency_summary.csv`

## Next phase

Physical lensing calibration and weak-lensing comparison remain deferred. Any arcsec deflection work requires documented calibration, not this dynamical scale check.
