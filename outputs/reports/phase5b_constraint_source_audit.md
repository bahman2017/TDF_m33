# Phase 5B-B — Constraint source review audit

**Scope:** Source registration and planning only. No observational comparison. No physical lensing claim.

## Documents

- Source review: `/Users/bahmanmasarratbakhsh/TDF_projects/Tdf_m33/docs/lensing_constraint_source_review.md`
- Calibration plan: `/Users/bahmanmasarratbakhsh/TDF_projects/Tdf_m33/docs/lensing_calibration_and_limits_plan.md`
- Registry: `docs/data_sources.md`

## Config (unchanged safeguards)

- observational_limits.enabled: **False**
- limits.status: **source_documented**
- selected_source_id (Phase 5C candidate): `lopez_fune_salucci_corbelli_2017`
- candidate_source_ids: `lopez_fune_salucci_corbelli_2017, kam_et_al_2018_m33_hi_masses, m33_direct_weak_lensing_gap`
- physical_calibration.enabled: **False**
- output_units: **normalized_proxy**

## Phase 5A / TDF branch

- Same frozen τ map (`tdf_lowparam_3knot`); no lensing-only fit.
- No separate dark-matter halo in the TDF lensing pathway.
- No `alpha_tau_scale` fitting to observations.
- No numeric limit comparison output in this phase.

## Weak lensing finding

No M33-specific direct weak-lensing constraint source was registered for comparison. See `m33_direct_weak_lensing_gap` in the registry.

## Validation

- All Phase 5B-B checks **PASS**.

## Next phase (5C)

Phase 5C: extract cited dynamical tables for selected_source_id (lopez_fune_salucci_corbelli_2017); compare enclosed-mass metrics only (upper_bound_consistency); keep deflection in normalized_proxy until physical calibration is documented
