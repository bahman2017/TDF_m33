# Phase 5C-A — López Fune et al. 2017 extraction audit

**Scope:** Extraction only. No τ-map comparison. No observational_limits enabled. Deflection remains `normalized_proxy`.

## Extracted artifacts

- `data/raw/extracted/lopez_fune_2017_dm_profile_raw.csv` — **25** rows (7 Fig.6 digitized, 18 model-evaluated BRK/NFW curves)
- `data/raw/extracted/lopez_fune_2017_halo_parameters_raw.csv` — **16** quoted parameters

## What was extracted

- **Fig. 6** effective DM density points (7 radii, visual digitization, ~15% relative uncertainty).
- **BRK / NFW local-fit curves** at 9.53–22.72 kpc from quoted Section 3.3 parameters (Eq. 9 and NFW Eq. 3).
- **Halo parameters** quoted in Sections 2.2, 3.2, 3.3, and 4 (global and local methods).

## What was not extracted

- Machine-readable publisher tables (none in PDF).
- Full RC point-by-point digitization (Fig. 2).
- Independent weak-lensing maps (unavailable).
- Any τ-map or deflection comparison columns.

## Method notes

- Fig. 6 digitization is **approximate** (PDF raster, log-y axis).
- Model curve rows are **not** independent observations; they trace quoted best-fit parameters.
- Parameters are **quoted directly** from paper text (not fitted here).

## Circularity warning

López Fune et al. 2017 uses Corbelli et al. 2014 baryonic and rotation inputs. This is **dynamical / rotation-based**, not independent weak lensing. Use for **upper-bound consistency** only; do not tune τ or `alpha_tau_scale`.

## Future use (Phase 5C-B)

Compare enclosed-mass-style proxies at documented radii (e.g. 23 kpc BRK `M_enclosed_23kpc` = 6.7±1.2×10¹⁰ M☉) against TDF dynamical scaffold — still no arcsec deflection claim.

## Parameter summary

- Local BRK: r_c = 9.6 kpc, ρ_c = 12.3×10⁶ M☉/kpc³, M_vir = 3.0×10¹¹ M☉
- Local NFW: c = 9.5, M_vir = 5.4×10¹¹ M☉
- Analysis range: 9.53 ≤ r ≤ 22.72 kpc
