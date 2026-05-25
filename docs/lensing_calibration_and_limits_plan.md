# Lensing calibration and observational limits plan (Phase 5B)

**Status:** Planning / audit only (Phase 5B-A). No physical lensing detection claim. No observational comparison in this phase.

## What Phase 5A computes

From the frozen sky-plane τ map (`outputs/maps/phase4b_tau_sky_projected_map.npz`, source model `tdf_lowparam_3knot`):

\[
\alpha_x = -\alpha_{\tau,\mathrm{scale}}\,\frac{\partial\tau}{\partial x_{\mathrm{sky}}}, \qquad
\alpha_y = -\alpha_{\tau,\mathrm{scale}}\,\frac{\partial\tau}{\partial y_{\mathrm{sky}}}
\]

Gradients use the documented sky grid (kpc). Outputs are stored in `outputs/maps/phase5a_tau_deflection_proxy_map.npz` with optional convergence proxy \(\kappa \approx \tfrac{1}{2}(\partial\alpha_x/\partial x + \partial\alpha_y/\partial y)\).

Phase 5A is a **prediction / consistency scaffold**: the same τ branch reconstructed from M33 rotation dynamics (Phases 3C–4B), not a lensing-only fit.

## Why outputs are `normalized_proxy`, not arcseconds

1. **\(K_\tau = 1\)** in the project config is a **normalization convention** linking rotation residuals to \(d\tau/dr\), not a published physical coupling to lensing deflection in arcsec.
2. **`alpha_tau_scale = 1.0`** in Phase 5A is an explicit placeholder; it must **not** be tuned to match lensing data.
3. **Baryonic velocities** remain D1-derived with status **PASS_WITH_CAVEAT**; geometry uses Corbelli 2014 tilted-ring projection with documented approximations.
4. **No documented M33 deflection/lensing limit table** is ingested yet (see `docs/data_sources.md` registry). Comparing normalized proxies to arcsec limits would be misleading.

Until a traceable calibration chain is documented, all deflection magnitudes are **relative / normalized** units only.

## Role of \(K_\tau\) and `alpha_tau_scale`

| Quantity | Current role | Phase 5B+ requirement |
|----------|--------------|------------------------|
| \(K_\tau\) | Scales \(v_\tau^2 = r K_\tau\, d\tau/dr\) in rotation reconstruction | Physical interpretation and SI/lensing units must be cited from TDF theory or an explicit phenomenological bridge |
| `alpha_tau_scale` | Multiplier on \(-\nabla_{\mathrm{sky}}\tau\) in the deflection proxy | Set from documented physics (not fitted to lensing) |
| Distance / geometry | Corbelli 2014 sky projection | Propagate uncertainties into arcsec scaling |

**Rule:** \(K_\tau\) and `alpha_tau_scale` must not be adjusted to force agreement with weak-lensing or dynamical mass constraints.

## What is needed for physical units

To convert the proxy to physical lensing observables (e.g. deflection angle in arcsec, convergence \(\kappa\), shear), the project must document:

1. **Theoretical link** — How τ (or \(d\tau/dr\)) maps to spacetime / potential / deflection in the TDF framework (manuscript + units).
2. **Calibration anchor** — At least one independent, cited quantity (e.g. enclosed mass at 23 kpc, Local Group constraint) with uncertainty, **or** a stated phenomenological scale factor with explicit assumptions.
3. **Cosmology and distance** — M33 distance, \(H_0\) if needed for \(\Sigma_{\mathrm{crit}}\), and sky-plane geometry already in Phase 4B.
4. **Propagation** — How baryonic PASS_WITH_CAVEAT and τ regularization uncertainty affect deflection maps.
5. **Registry entry** — Each limit or calibration source in `docs/data_sources.md` with `acquisition_status: documented` and file paths before enabling comparison in config.

**Phase 5B-B (future):** Implement conversion only after items 1–5 are satisfied for at least one calibration path.

## Observational limits needed for M33

Planned constraint classes (no numerical limits until sources are added):

| Class | Purpose | Comparison mode |
|-------|---------|-----------------|
| M33 weak-lensing | Direct \(\kappa\), shear, or mass maps | Upper-bound or profile consistency |
| Local Group / M33 dynamical mass | Enclosed mass vs radius | Enclosed-mass consistency |
| Stellar streams / satellites | Outer halo / perturbation bounds | Upper-bound where applicable |
| Upper-bound consistency checks | Non-detection or limit papers | One-sided tests only |
| Future direct deflection / lensing | Time-delay, strong lensing, etc. | As documented |

All comparisons must use `comparison_mode: upper_bound_consistency` unless a full likelihood with documented uncertainties is added.

## What this phase does **not** do

- Convert `normalized_proxy` to arcsec or physical \(\kappa\).
- Fit `alpha_tau_scale` to observations.
- Add a separate dark-matter halo or lensing-only τ field in the TDF branch.
- Claim dark matter is replaced or disproven.
- Compare to observational limits without a registered source in `docs/data_sources.md`.

## Selected source acquisition (Phase 5B-C)

**`lopez_fune_salucci_corbelli_2017`** — PDF at `data/raw/downloads/lopez_fune_salucci_corbelli_2017_m33.pdf` (arXiv 1611.01409 accepted manuscript); SHA-256 sidecar committed; extraction plan in `docs/lopez_fune_2017_extraction_plan.md`. Registry status: **documented**. Comparison still **disabled**.

## Next steps (Phase 5C)

1. Digitize Fig. 6 / transcribe NFW–Burkert parameters → `data/raw/extracted/lopez_fune_2017_*.csv`.
2. Run upper-bound enclosed-mass consistency (not arcsec deflection; not τ tuning).
3. Physical calibration (`alpha_tau_scale` physical units) remains separate and undocumented.
4. Do **not** enable `observational_limits` until extracted tables are reviewed.
