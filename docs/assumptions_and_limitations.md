# Assumptions and limitations

Explicit scope control for reviewers and future paper text.

## Scientific scope

- **Galaxy:** M33 only in this repository; generalization to other galaxies is out of scope unless stated otherwise.
- **Primary observable (early phases):** Rotation curve / circular speed as a function of radius.
- **TDF pathway:** Missing support parameterized as τ-geometry; halo baselines are separate comparative models.

## Assumptions (to be refined per phase)

| Topic | Phase | Assumption (initial) |
|-------|-------|----------------------|
| Axisymmetry | 2–3 | Rotation curve interpreted in axisymmetric approximation unless 2D map (Phase 4) states otherwise |
| Baryonic mass models | 2 | Mass-to-light and gas scaling documented in `data_sources.md` |
| Baryonic velocities (Phase 2A) | 2A | \(v_{\mathrm{gas}}\), \(v_{\mathrm{disk}}\) from Phase 1D-D1 derivation (`derived_baryonic_velocity_pass_with_caveat`); not published Corbelli velocity columns; Fig. 12 sanity check PASS_WITH_CAVEAT |
| Phase 2A scope | 2A | Baryonic-only diagnostic only—no halo or TDF conclusion from RMSE/χ² alone |
| Halo baselines (Phase 2B) | 2B | NFW/Burkert are ΛCDM comparison models on \(0.4 \le R \le 23\) kpc; not TDF; do not imply DM is ruled out |
| AIC/BIC (Phase 2B) | 2B | χ² + 2k and χ² + k ln n with k=0,2; baryonic components fixed from D1 |
| Phase 2C audit | 2C | Consolidates 2A/2B; Burkert r₀ often bound-limited (~200 kpc)—not publication-stable vs Corbelli; NFW good fit is ΛCDM baseline only |
| Phase 3 τ input | 3 | \(\Delta v^2 = v_{\mathrm{obs}}^2 - v_{\mathrm{bar}}^2\) from Phase 2A only—not NFW/Burkert residuals |
| Phase 3A direct τ | 3A | Pointwise \(d\tau/dr=\Delta v^2/(rK_\tau)\); \(K_\tau=1\) is project-unit normalization; \(\tau\) offset arbitrary; identity check not AIC/BIC competitor |
| \(K_\tau\) | 3B+ | Physical calibration and fitting deferred; sensitivity analysis planned |
| τ smoothness | 3B | Regularization required for stable \(d\tau/dr\) (9 raw spikes in Phase 2C) |
| 2D τ-map | 4 | Optional; may impose additional symmetry |
| Lensing geometry | 5 | Line-of-sight and thin-lens approximations as documented in lensing module |

## Limitations

1. **M33 lensing signal may be weak.** Observational limits may be loose compared to rotation constraints; lensing tests are often **upper-bound consistency** checks, not high-precision confirmations.

2. **This is not a proof that dark matter does not exist.** Successful τ reconstruction on M33 would show internal consistency of the TDF parameterization on this system, compared against standard halo fits—not a global falsification of dark matter.

3. **Rotation-curve reconstruction alone is not enough.** A good τ fit to \(v_{\mathrm{obs}}\) does not uniquely establish the correct microphysics or replace independent probes (lensing, satellites, cosmology, etc.).

4. **Lensing stage = prediction / consistency unless direct data are available.** Unless explicit lensing measurements are ingested and modeled jointly, Phase 5 outputs are **predictions** to be compared to limits, not standalone detections of τ.

5. **Degeneracies.** Baryonic mass-to-light, distance, inclination, and τ regularization can trade off; fits must report uncertainties and degeneracy directions where possible.

6. **Phase 0 code.** No scientific results are produced until later phases; documentation may precede implementation.

7. **Phase 2A baryonic baseline.** Large χ² for baryonic-only vs \(v_{\mathrm{obs}}\) reflects missing halo support, not a validated TDF or anti-DM claim. Negative \(\Delta v^2\) at some radii (if present) are reported unclipped and do not imply baryons exceed observed speeds globally.

8. **Phase 2B halo fits.** Better NFW/Burkert χ² vs baryonic-only is expected for a disk galaxy in ΛCDM; this does **not** validate TDF or disprove dark matter. Corbelli et al. 2014 published halo parameters are sanity references only—D1 baryonic caveat applies.

9. **Phase 2C audit.** NFW performs well on the processed dataset (reduced χ² ≈ 1 on the fit mask); Burkert is **boundary-limited** (r₀ at upper bound) and should not be over-interpreted. Phase 3 uses baryonic \(\Delta v^2\) only; smoothing/regularization may be needed depending on residual gradient diagnostics.

10. **Phase 3A direct τ.** Raw \(d\tau/dr\) and \(\tau(r)\) are reconstructed algebraically from baryonic residuals—**not** a new fitted halo model. Reconstruction error \(\approx 0\) is an identity check. No lensing predictions. No dark-matter disproof claim. Phase 3B should smooth the gradient before interpretive or comparative claims.

## Claim control (mandatory framing)

Use language equivalent to:

> M33 is used as an intermediate-scale test of whether the missing acceleration inferred from rotation dynamics can be reconstructed as a smooth τ-geometry, and whether the same τ-map produces lensing/deflection predictions consistent with observational limits.

Avoid: “dark matter disproven,” “no need for dark matter,” or universal statements from a single galaxy.

## Review checklist before publication

- [ ] All data sources and transforms in `data_sources.md`
- [ ] Halo baselines and TDF models in same comparison framework
- [ ] Lensing section labeled prediction vs inference
- [ ] Limitations section referenced in manuscript discussion
