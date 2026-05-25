# Phase 5B-A — Lensing calibration and limits audit

**Scope:** Planning / audit only. No physical lensing detection. No observational comparison in this phase.

## Phase 5A status (frozen τ deflection proxy)

- Source τ map: `/Users/bahmanmasarratbakhsh/TDF_projects/Tdf_m33/outputs/maps/phase4b_tau_sky_projected_map.npz`
- source_model: `tdf_lowparam_3knot`
- geometry_mode: `radial_tilted_ring`
- units: **normalized_proxy**
- alpha_tau_scale: **1.0** (placeholder)
- separate_halo_used: **False**
- lensing_only_fit: **False**
- compare_to_observational_limits: **False**

## Phase 5B-A config (planning)

- physical_calibration.enabled: **False**
- output_units: **normalized_proxy**
- calibration_status: **uncalibrated**
- observational_limits.enabled: **False**
- limits_status: **planned**
- limits_source_id: `none`
- comparison_mode (planned): `upper_bound_consistency`

## Safeguards

- Phase 5A is a **deflection-proxy scaffold** (normalized τ-gradient).
- **Physical calibration is not implemented** (`physical_calibration.enabled: false`).
- **Observational limit comparison is not implemented** (`observational_limits.enabled: false`).
- The **same frozen τ map** from rotation reconstruction is used; no independent halo or lensing-only τ component is introduced.
- **K_τ = 1** remains a normalization convention, not physical lensing calibration.
- This audit makes **no** dark-matter disproof or replacement claim.

## Validation

- All Phase 5A audit checks **PASS**.

## Next phase (5B-B)

Proceed to Phase 5B-B only when calibration and limit sources are documented in docs/lensing_calibration_and_limits_plan.md and docs/data_sources.md

See `docs/lensing_calibration_and_limits_plan.md` and the lensing source registry in `docs/data_sources.md`.
