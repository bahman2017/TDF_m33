# Manuscript outline — M33 TDF τ-geometry

Skeleton aligned with `paper/m33_tdf_tau_geometry_draft.tex`. Numbers from Phase 6A key-results table unless noted.

---

## Abstract

- **Problem:** Missing acceleration in M33 rotation; test τ-geometry as low-parameter dynamical description.
- **Data:** Corbelli et al. 2014 rotation; D1 baryonic decomposition (caveated).
- **Methods:** Baryonic-only, NFW, Burkert baselines; 3-/5-knot TDF; 2D map; normalized deflection proxy; López Fune upper-bound check.
- **Results:** 3-knot TDF competitive with NFW on AIC; deflection proxy from same τ; López Fune PASS_WITH_CAVEAT.
- **Conclusion:** Intermediate-scale consistency only; no DM disproof; lensing calibration deferred.

---

## 1. Introduction

- M33 as Local Group laboratory; rotation curves and missing acceleration.
- TDF / τ-geometry motivation (time-delay field as dynamical scaffold).
- **Scope:** One galaxy, processed Corbelli pipeline; not cosmological proof.
- **Non-goals:** DM replacement, weak-lensing confirmation, arcsec lensing claims.

---

## 2. Data and provenance

- `data/processed/m33_rotation.csv` (58 radii; Corbelli Table 1).
- Source manifest; extraction log; validation scripts.
- Fit mask 0.4–23 kpc for model comparison (n=56).
- **Table 1:** Data provenance (sources, flags, scripts).

---

## 3. Baryonic decomposition and caveats

- Phase 1D-D1 disk gravity; gas + stellar disk; no separate bulge.
- **PASS_WITH_CAVEAT** on derived baryonic velocities.
- Fig. 12 sanity check not canonical.
- Implications for all downstream fits.

---

## 4. Baseline models

- Baryonic-only diagnostic (RMSE ≈ 58.6 km/s on fit mask).
- NFW (ΛCDM baseline; RMSE ≈ 4.16 km/s; AIC ≈ 68.0).
- Burkert (RMSE ≈ 23.0 km/s; r₀ at upper bound).
- **Figure 1:** Rotation curve + baryonic-only.

---

## 5. TDF radial reconstruction

- Δv² = v_obs² − v_bar²; τ-gradient pathway (Phases 3A–3B context, not fair AIC competitors).
- Direct vs regularized reconstruction (diagnostic).

---

## 6. Low-parameter TDF comparison

- Knot models k=3,4,5; K_τ=1 fixed.
- **Figure 2:** NFW / Burkert / TDF rotation comparison.
- **Figure 3:** τ-gradient and τ-profile (3-knot).
- **Table 2:** Model comparison (RMSE, χ², AIC, BIC).
- 3-knot: RMSE ≈ 3.51 km/s, AIC ≈ 63.0; 5-knot lowest RMSE, higher BIC.

---

## 7. Sensitivity and stability (Phase 3D)

- AIC vs NFW; fit-mask variants; K_τ sweep; smoothing diagnostic.
- **Caveated** stability conclusion.
- Reference: `outputs/reports/phase3d_tdf_sensitivity_report.md`.

---

## 8. 2D τ-map construction

- Phase 4A axisymmetric disk-plane map from frozen 3-knot radial profile.
- Phase 4B sky projection (Corbelli tilted-ring geometry).
- **Figure 4:** 2D τ / sky-projected map.

---

## 9. Deflection proxy and upper-bound consistency

- Phase 5A: normalized deflection proxy from sky τ (no separate halo).
- **Figure 5:** Deflection-proxy magnitude map.
- Phase 5C-B: M_tau_eff vs López Fune M_enclosed_23kpc (PASS_WITH_CAVEAT).
- Not weak lensing; not arcsec calibration.

---

## 10. Limitations

- Single galaxy; derived baryons; K_τ normalization; axisymmetric 2D map.
- Burkert boundary; circularity in López Fune comparison.
- No M33 weak-lensing map.

---

## 11. Future work

- Physical `alpha_tau_scale` / arcsec calibration.
- Independent weak-lensing data.
- Improved baryonic systematics.

---

## 12. Conclusion

- Strongest result: **rotation-dynamics consistency** of low-parameter τ.
- Deflection: **proxy scaffold** only.
- **No** claim that dark matter is disproven or replaced.

---

## Appendix (optional)

- Reproducibility commands: `outputs/reports/phase6a_reproducibility_commands.md`.
- **Table 3:** Claim/caveat summary (from Phase 6A matrix).
