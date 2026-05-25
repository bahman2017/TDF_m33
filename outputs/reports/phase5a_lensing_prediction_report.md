# Phase 5A — Lensing / deflection prediction (normalized proxy)

**Scope:** First deflection-proxy maps from the **same frozen** sky-plane τ map as rotation (Phase 4B). **Not** a lensing fit. **Not** a dark-matter disproof.

## Inputs

- Sky τ map: `/Users/bahmanmasarratbakhsh/TDF_projects/Tdf_m33/outputs/maps/phase4b_tau_sky_projected_map.npz`
- source_model: `tdf_lowparam_3knot`
- geometry_mode: `radial_tilted_ring`
- geometry_source: `corbelli_et_al_2014`
- placeholder_geometry_flag: `False`

## Deflection proxy

- Mode: `normalized_tau_gradient_proxy`
- α_x = −α_τ_scale ∂τ/∂x_sky, α_y = −α_τ_scale ∂τ/∂y_sky
- α_τ_scale: **1.0** (normalization placeholder)
- Units: **normalized_proxy**

## Summary (finite pixels)

- |α| max: **3103.95**
- |α| median: **1073.51**
- Fraction finite: **0.6349**

## Convergence proxy

- Computed: **True**
- Stable: **True**
- Note: ok

## Caveats

- Baryonic velocities: D1-derived **PASS_WITH_CAVEAT**.
- K_τ = 1 is a project normalization, not physical lensing calibration.
- **No separate dark-matter halo** in the TDF lensing branch.
- **No lensing-only fit**; τ was fixed from Phase 3C/4B.
- Observational limit comparison: **False** (source: none documented).

## Phase 5B (planned)

- Physical α_τ calibration when documented.
- Comparison to observational limits once listed in `docs/data_sources.md`.
