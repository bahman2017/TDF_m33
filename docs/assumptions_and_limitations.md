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
| Phase 3B-A regularization | 3B-A | Gaussian/spline smoothing of \(d\tau/dr\); parameters fixed in config—not fitted; not evidence vs NFW by itself |
| Phase 3C low-parameter TDF | 3C | k knot dτ/dr values fitted; K_τ fixed; first fair AIC/BIC row for TDF; 3A/3B excluded from formal comparison |
| Phase 3D sensitivity | 3D | Robustness audit only; K_τ sweep tests scale degeneracy; not independent physical calibration |
| Phase 4A 2D τ-map | 4A | Axisymmetric disk-plane extension τ₂D(x,y)=τ_rad(R) from Phase 3C; not separately fitted |
| Phase 4B projection | 4B | Disk→sky coordinate transform only; τ unchanged; Corbelli 2014 Fig. 3 model-shape i(R), PA(R) |
| Phase 4B-B geometry lock | 4B-B | Placeholder i/PA removed; radial tilted-ring preferred over global single i/PA (warped disk) |
| τ smoothness | 3B-A | Raw spikes reduced; interpretive claims still require Phase 3C comparison |
| 2D τ-map (morphology) | 4B+ | Gas/spiral/non-axisymmetric structure not yet included |
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

10. **Phase 3A direct τ.** Raw \(d\tau/dr\) and \(\tau(r)\) are reconstructed algebraically from baryonic residuals—**not** a new fitted halo model. Reconstruction error \(\approx 0\) is an identity check. No lensing predictions. No dark-matter disproof claim.

11. **Phase 3B-A smoothed τ.** Smoothing reduces gradient spikes but introduces reconstruction RMSE vs \(v_{\mathrm{obs}}\). This is a **regularization step**, not proof that TDF outperforms NFW. Raw Phase 3A profiles remain available. AIC/BIC comparison requires Phase 3C.

12. **Phase 3C low-parameter TDF.** Knot models (k=3,4,5) enable AIC/BIC vs NFW (k=2). Better AIC alone does not disprove DM or validate TDF microphysics. No lensing. Baryonic PASS_WITH_CAVEAT unchanged.

13. **Phase 3D sensitivity.** K_τ refits mostly rescale knot gradients; velocity metrics often nearly unchanged—normalization audit, not new evidence. Phase 4 (2D τ) only after reviewing mask/K_τ stability.

14. **Phase 4A 2D τ-map.** First spatial extension: axisymmetric disk-plane map from `tdf_lowparam_3knot` radial profile only. No new parameters, no lensing, no gas morphology or spiral arms. Not the final physical τ map. Baryonic PASS_WITH_CAVEAT and K_τ=1 normalization unchanged.

15. **Phase 4B projection.** Geometry preparation only: sky-plane coordinates from inclination/PA. Does not alter τ values or Phase 3C radial model. No lensing yet.

16. **Phase 4B-B geometry lock.** Adopted geometry from Corbelli et al. 2014 §4.1 Fig. 3 (model-shape tilted rings, 11 radii). M33 is warped; a single global i/PA is an approximation—radial mode is preferred. Digitized ring values are traceable but not machine tables in the paper PDF. Inner-disk global reference (i≈54°, PA≈22°) documented for comparison. Not a final observational lensing prediction.

17. **Phase 5A deflection proxy.** Uses the **same frozen** sky τ as rotation (Phase 4B). Deflection is a normalized gradient proxy (`alpha_tau_scale=1`); not tuned to lensing data. **No separate dark-matter halo** in the TDF lensing branch. **No lensing-only fit.** Convergence proxy is illustrative and may be edge-unstable. **No observational limit comparison** until a source is listed in `data_sources.md`. This is a prediction/consistency scaffold only—not evidence that dark matter is disproven.

18. **Phase 5B-A calibration/limits planning.** Documents requirements for physical units and M33 constraints (`docs/lensing_calibration_and_limits_plan.md`). **No arcsec conversion**, **no observational comparison**, **no fitting** of `alpha_tau_scale` or a lensing-only τ field. Config keeps `physical_calibration.enabled: false` and `observational_limits.enabled: false`. Future Phase 5B-B/5C may add physical units or upper-bound checks only when sources are registered with real files.

19. **Phase 5B-B constraint source review.** Registers candidate literature (`docs/lensing_constraint_source_review.md`, `docs/data_sources.md` registry). **No M33-specific weak-lensing map** identified for direct deflection comparison. Selected Phase 5C candidate: López Fune et al. 2017 (dynamical enclosed-mass / halo profile, `located` not `documented` until tables extracted). **No numeric limits** in repo tables; comparison still disabled.

20. **Phase 5B-C López Fune 2017 acquisition.** PDF (arXiv accepted manuscript) and SHA-256 recorded; extraction plan identifies figure-based quantities (no machine tables). **Not** direct lensing; **not** for τ or `alpha_tau_scale` tuning; circularity with Corbelli 2014 inputs documented. Comparison remains disabled.

## Claim control (mandatory framing)

Use language equivalent to:

> M33 is used as an intermediate-scale test of whether the missing acceleration inferred from rotation dynamics can be reconstructed as a smooth τ-geometry, and whether the same τ-map produces lensing/deflection predictions consistent with observational limits.

Avoid: “dark matter disproven,” “no need for dark matter,” or universal statements from a single galaxy.

## Review checklist before publication

- [ ] All data sources and transforms in `data_sources.md`
- [ ] Halo baselines and TDF models in same comparison framework
- [ ] Lensing section labeled prediction vs inference
- [ ] Limitations section referenced in manuscript discussion
