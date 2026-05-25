# Phase 3D — TDF sensitivity and robustness audit (M33)

**Scope:** Robustness audit only—not new physical evidence. Baryonic velocities are D1-derived (`PASS_WITH_CAVEAT`). **No lensing** predictions. **No claim** that dark matter is disproven.

Phase 3C is the first fair low-parameter AIC/BIC TDF comparison. Phase 3A (direct) and Phase 3B-A (smoothed) are not formal competitors.

## A. Knot-count stability (Phase 3C)

- Best TDF by **AIC:** `tdf_lowparam_3knot` (NFW AIC ≈ 68.0)
- Best TDF by **BIC:** `tdf_lowparam_3knot` (NFW BIC ≈ 72.0)
- Best TDF by **RMSE:** `tdf_lowparam_5knot`
- 3-knot AIC beats NFW: **True**
- 3-knot BIC beats NFW: **True**

5-knot achieves lowest RMSE/χ² but pays a higher parameter penalty in AIC/BIC.

## B. K_τ normalization sweep

K_τ is a **project-unit normalization**, not an independently calibrated constant. With knot values refit at each K_τ, **v_τ² = r K_τ dτ/dr** can absorb much of the K_τ scaling in the fitted gradient.

- Velocity metrics stable across K_τ (RMSE spread < 1 km/s): **False**
- Knot values scale ≈ 1/K_τ when refit (scale degeneracy): **True**
- Max RMSE spread across sweep: **0.4150 km/s**
- Max χ² spread: **3.01**

- Knot scaling notes: k=3, K_tau=0.5: median knot ratio vs K_tau=1 is 2.000 (expected ~2.000 if scale degeneracy); k=3, K_tau=2.0: median knot ratio vs K_tau=1 is 0.500 (expected ~0.500 if scale degeneracy)

## C. Gaussian smoothing sensitivity (Phase 3B diagnostic)

Not included in formal AIC/BIC. σ_kpc affects spike count, smoothness, and RMSE:

- σ = 0.5 kpc: spikes=0, smoothness=58, RMSE=1.66 km/s, neg v_τ²=0
- σ = 0.75 kpc: spikes=0, smoothness=43, RMSE=2.13 km/s, neg v_τ²=0
- σ = 1.0 kpc: spikes=0, smoothness=27, RMSE=2.48 km/s, neg v_τ²=0
- σ = 1.5 kpc: spikes=0, smoothness=9.1, RMSE=3.00 km/s, neg v_τ²=0

## D. Fit-mask sensitivity (3-knot refit)

- **corbelli_default** (0.4–23.0 kpc, n=56): AIC=63.0, BIC=69.0, RMSE=3.51 km/s
- **stricter_0p5_22p5** (0.5–22.5 kpc, n=54): AIC=62.7, BIC=68.7, RMSE=3.51 km/s
- **stricter_1p0_22p0** (1.0–22.0 kpc, n=50): AIC=70.9, BIC=76.7, RMSE=3.16 km/s

## Stability conclusion

- **3-knot vs NFW on AIC** is the primary fair comparison row; verify fragility via mask and K_τ audits above.
- **Burkert** remains boundary-limited (r₀ ≈ 200 kpc); do not over-interpret.
- **Phase 4** (2D τ-map) should proceed only if radial ranking is acceptably stable under mask variants and K_τ is documented as normalization.
- **Phase 5** lensing consistency remains future work.

## Claim control

Do not state that TDF beats dark matter or replaces NFW without qualification. Rotation-curve comparison on one galaxy with derived baryons is insufficient for cosmological claims.
