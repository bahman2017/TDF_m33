# Theory summary: rotation residuals and τ-geometry

Conservative summary of the Time-Delay Field (TDF) relations used in this project. Notation matches the planned implementation; unit conventions will be fixed when data are ingested (Phase 1).

## Observed rotation and decomposition

The observed circular speed squared is decomposed into baryonic and τ-linked contributions:

\[
v_{\mathrm{obs}}^2(r) = v_{\mathrm{bar}}^2(r) + v_\tau^2(r)
\]

Here \(v_{\mathrm{bar}}(r)\) is the Newtonian (or specified baryonic) prediction from gas, disk, and optional bulge components. The term \(v_\tau(r)\) encodes the effective support associated with the τ-field in the TDF pathway.

## Core TDF radial relation

The τ-gradient is related to \(v_\tau\) through a coupling constant \(K_\tau\) (dimensions and value set by the TDF framework and documented configuration):

\[
v_\tau^2(r) = r\, K_\tau \,\frac{d\tau}{dr}
\]

Inverting for the gradient when rotation data and \(v_{\mathrm{bar}}\) are known:

\[
\frac{d\tau}{dr} = \frac{v_{\mathrm{obs}}^2(r) - v_{\mathrm{bar}}^2(r)}{r\, K_\tau}
\]

The **residual** \(v_{\mathrm{obs}}^2 - v_{\mathrm{bar}}^2\) is therefore mapped to a radial τ-gradient; integrating \(d\tau/dr\) (with chosen boundary conditions and smoothness priors) yields a radial profile \(\tau(r)\).

## Residual acceleration to τ-gradient mapping

Define the squared residual velocity

\[
\Delta v^2(r) \equiv v_{\mathrm{obs}}^2(r) - v_{\mathrm{bar}}^2(r) \approx v_\tau^2(r)
\]

when the decomposition is adequate. Then

\[
\frac{d\tau}{dr} = \frac{\Delta v^2(r)}{r\, K_\tau}.
\]

Interpretation (careful):

- Where baryons alone underpredict \(v_{\mathrm{obs}}\), \(\Delta v^2 > 0\) and the reconstructed \(d\tau/dr\) has a sign and magnitude set by \(K_\tau\) and radius.
- This is a **reparameterization** of the missing dynamical support in the TDF branch, not by itself a proof of any specific microphysical origin.

Regularization (smooth splines, bounded gradients, etc.) will be stated in Phase 3B documentation; unregularized pointwise inversion is generally ill-posed.

## Phase 3A implementation (direct pointwise)

Phase 3A applies the inversion algebraically at each radius on the canonical grid:

- Input: \(\Delta v^2 = v_{\mathrm{obs}}^2 - v_{\mathrm{bar}}^2\) from Phase 2A (baryonic-only; not NFW/Burkert-subtracted).
- \(d\tau/dr = \Delta v^2 / (r\, K_\tau)\) with default \(K_\tau = 1\) as a **project-unit normalization** (not a fitted physical constant in 3A).
- \(\tau(r)\) from cumulative trapezoidal integration with \(\tau(r_{\min}) = 0\); **additive offset of \(\tau\) is arbitrary**.
- \(v_{\mathrm{TDF,direct}} = \sqrt{v_{\mathrm{bar}}^2 + r K_\tau\, d\tau/dr}\) is an **identity check** (reconstruction error \(\approx 0\) numerically), not a new halo fit or AIC/BIC competitor.
- Raw \(d\tau/dr\) inherits spikes from \(\Delta v^2\); Phase 3B will add smoothing/regularization.

## Reconstruction from rotation, use for lensing

**Step 1 (rotation):** Using \(v_{\mathrm{obs}}(r)\) and a documented \(v_{\mathrm{bar}}(r)\), infer \(d\tau/dr\) and \(\tau(r)\) (or a 2D \(\tau\) map in Phase 4) subject to smoothness and config choices.

**Step 2 (lensing / deflection):** The **same** τ-field enters lensing/deflection predictions in `tdf_m33.lensing` without introducing a separate dark matter halo in the TDF pathway. Comparisons to observational limits are **consistency checks** on a single τ-map hypothesis.

This does **not** imply that dark matter is absent in nature; halo models (NFW, Burkert) remain explicit baselines in Phase 2.

## Relation to baselines

| Approach | Extra degrees of freedom in missing-acceleration slot |
|----------|------------------------------------------------------|
| Baryonic-only | None (often insufficient) |
| NFW / Burkert | Halo mass, scale, concentration (etc.) |
| TDF τ-profile | Smooth τ (and \(K_\tau\)) subject to regularization |

Model comparison will use quantitative metrics (e.g. χ², AIC/BIC where appropriate) documented in Phase 2–3 reports.

## References and framework notes

- Full TDF theoretical references will be added when the manuscript bibliography is fixed.
- \(K_\tau\) physical interpretation and units will be locked when connecting to lensing (Phase 5).
