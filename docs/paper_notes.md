# Paper notes (draft)

Working notes for manuscript preparation. Not for publication without revision.

## Possible title options

1. *Reconstructing M33’s Missing Acceleration as a Time-Delay Field: Rotation Dynamics and Lensing Consistency*
2. *τ-Geometry on Intermediate Scales: A Rotation-Curve and Lensing Test in M33*
3. *M33 as a Laboratory for TDF τ-Maps Without an Independent Halo Degree of Freedom*
4. *From Rotation Residuals to τ-Gradients: Constraining Time-Delay Geometry in the Triangulum Galaxy*

## Controlled claim language (draft)

**Abstract / conclusion framing:**

M33 is used as an intermediate-scale test of whether the missing acceleration inferred from rotation dynamics can be reconstructed as a smooth τ-geometry, and whether the same τ-map produces lensing/deflection predictions consistent with observational limits.

**Avoid:**

- Claims that dark matter is ruled out or unnecessary in general.
- Presenting rotation-only τ fits as definitive evidence for TDF over ΛCDM.

**Emphasize:**

- Comparative baselines (baryonic-only, NFW, Burkert).
- Single τ-map hypothesis linking rotation and lensing predictions.
- Explicit limitations when lensing data are weak or limit-based only.

**Phase 2 status (2026-05-24, Phase 2C audit):**

- Baryonic-only: large RMSE/χ² (expected; missing halo).
- NFW: good fit on fit mask (reduced χ² ≈ 1.2)—**ΛCDM comparison baseline**, not TDF.
- Burkert: poor fit; r₀ at upper bound (~200 kpc)—**do not over-interpret** vs Corbelli BVI reference.
- Baryonic velocities: D1-derived, `PASS_WITH_CAVEAT`.
- **Phase 3A (2026-05-24):** Raw \(d\tau/dr\) and \(\tau(r)\) from baryonic \(\Delta v^2\) with \(K_\tau=1\) normalization; direct reconstruction matches \(v_{\mathrm{obs}}\) by construction (identity check).
- **Not** a fair AIC/BIC competitor to NFW until Phase 3B regularization.
- **Phase 3B-A:** Gaussian (σ=0.75 kpc) and spline smoothing of raw \(d\tau/dr\); tradeoff vs \(v_{\mathrm{obs}}\) documented—not a claim that TDF beats NFW.
- **Phase 3C:** Low-parameter knot τ models (k=3,4,5) with AIC/BIC vs NFW/Burkert on fit mask; K_τ fixed. 3A/3B not formal competitors.
- **Phase 3D:** Robustness audit (K_τ, mask, smoothing σ); K_τ is normalization.
- **Phase 4A:** First 2D disk-plane τ map: axisymmetric τ₂D(x,y)=τ_rad(R) from `tdf_lowparam_3knot`; not separately fitted; not final physical map.
- **Phase 4B:** Disk-to-sky coordinate projection only; τ field unchanged; prepares Phase 5 deflection.
- **Phase 4B-B:** Corbelli 2014 Fig. 3 model-shape tilted-ring i(R), PA(R) locked; placeholders removed. Warped disk—global i/PA is approximation only.
- **Phase 5A:** Normalized deflection-proxy maps from frozen sky τ (α ∝ −∇τ); no lensing fit; no separate halo; `normalized_proxy` units; not a detection claim.
- **Phase 5B-A:** Calibration and observational-limits **planning only**; no physical units; no limit comparison; see `docs/lensing_calibration_and_limits_plan.md`.
- **Phase 5B-B:** Constraint **source review only**; candidates registered (López Fune et al. 2017 selected for future dynamical check); no M33 weak-lensing map found; see `docs/lensing_constraint_source_review.md`.
- **Phase 5B-C:** López Fune et al. 2017 PDF acquired + extraction plan; **documented** in registry.
- **Phase 5C-A:** Raw DM profile + halo parameter tables extracted; no τ comparison.
- **Phase 5C-B:** Enclosed-mass proxy vs López Fune `M_enclosed_23kpc` — dynamical upper-bound scale check only; deflection still `normalized_proxy`.
- **Phase 6A:** Publication summary + claim matrix (`phase6a_*`). Lead with 3-knot τ rotation fit; caveate lensing and López Fune; no DM disproof.
- **Phase 6B:** LaTeX draft skeleton in `paper/`; figures/tables map in `docs/manuscript_figures_and_tables.md`; allowed language in `docs/manuscript_allowed_language.md`.
- No gas morphology, spiral structure, or non-axisymmetric regularization yet.
- Qualify any TDF vs NFW comparison — not a DM disproof.
- Physical lensing units deferred; observational comparison deferred to Phase 5C after table extraction for selected source.

## Planned figures

| Fig. | Content | Phase |
|------|---------|-------|
| 1 | M33 data schematic / radius–velocity data | 1 |
| 2 | Rotation curve: \(v_{\mathrm{obs}}\), \(v_{\mathrm{bar}}\), baselines | 2 |
| 3 | Residual \(\Delta v^2\) and halo vs baryonic comparison | 2 |
| 4 | \(d\tau/dr\) and radial \(\tau(r)\) profile | 3 |
| 5 | Composite fit: \(v_{\mathrm{bar}} + v_\tau\) vs \(v_{\mathrm{obs}}\) | 3 |
| 6 | (Optional) 2D τ-map | 4 |
| 7 | Lensing / deflection prediction vs observational limits | 5 |

## Planned tables

| Table | Content | Phase |
|-------|---------|-------|
| I | Data sources and assumptions | 1 |
| II | Best-fit parameters: baryonic-only, NFW, Burkert | 2 |
| III | TDF τ-profile parameters and goodness-of-fit | 3 |
| IV | Model comparison metrics (χ², AIC/BIC, etc.) | 2–3 |
| V | Lensing consistency summary | 5 |

## Repository citation

Plan to add `CITATION.cff` and Zenodo DOI at release; reference this codebase version in the paper methods section.
