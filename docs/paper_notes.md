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
- **No τ-profile reconstructed yet.** Phase 3 uses \(\Delta v^2 = v_{\mathrm{obs}}^2 - v_{\mathrm{bar}}^2\) from Phase 2A only.
- No dark-matter replacement claim at this stage.

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
