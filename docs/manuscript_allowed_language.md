# Manuscript allowed and prohibited language

Derived from `outputs/tables/phase6a_claim_traceability_matrix.csv` (Phase 6A). Use this list during drafting and referee response.

## Core framing (required)

M33 is an **intermediate-scale test** of whether missing acceleration inferred from rotation dynamics can be reconstructed as a **smooth, low-parameter τ-geometry**, and whether the **same τ-map** yields **deflection-proxy** predictions **without** a separate halo or lensing-only τ fit.

## Allowed (with stated caveats)

- The **3-knot TDF radial model is competitive with the NFW baseline** on this processed M33 dataset (fit mask 0.4–23 kpc; RMSE ≈ 3.51 km/s; AIC ≈ 63.0 vs NFW AIC ≈ 68.0).
- **Baryonic-only** velocities from the documented D1 derivation do **not** explain the rotation curve on the fit mask (large RMSE/χ²).
- **NFW** is a strong **ΛCDM comparison baseline** (two-parameter halo on D1 baryons); reduced χ² ≈ 1.2.
- **Burkert** is **boundary-limited** here (core radius at upper fit bound ~200 kpc); do not use as a preferred anchor.
- The **same reconstructed τ-map** produces **normalized deflection-proxy** fields **without** adding a separate halo (`normalized_proxy` units; not arcsec).
- A **2D τ-map** was built by **axisymmetric extension** of the frozen radial `tdf_lowparam_3knot` profile (no separate 2D fit).
- The **López Fune et al. 2017** comparison is a **dynamical upper-bound consistency check** (`PASS_WITH_CAVEAT` at ~23 kpc), **not** weak lensing.
- **3-knot ranking** is **stable under default and moderate fit-mask variants**; document **K_τ normalization** degeneracy (Phase 3D).
- **Direct weak-lensing comparison** is **not yet available** for M33 in this repository.
- **Dark matter is not disproven**; NFW remains the ΛCDM reference; TDF addresses rotation-dynamics consistency only.

## Prohibited (must not appear as affirmative claims)

- “Dark matter is disproven.”
- “TDF replaces dark matter.” / “No need for dark matter.”
- “Lensing is confirmed.” / “Observational lensing detection.”
- “M33 proves TDF.” / “TDF outperforms all cosmological models.”
- “The deflection proxy is a physical arcsecond prediction.”
- “Weak lensing confirms/refutes τ deflection.”
- “Burkert falsifies NFW/TDF” (without boundary caveat).
- “2D τ-map independently fits spiral structure.”

## Mandatory caveats (mention in Methods or Limitations)

| Topic | Wording guidance |
|-------|------------------|
| Baryonic velocities | D1-derived; **PASS_WITH_CAVEAT** vs Corbelli Fig. 12; not publisher velocity columns |
| K_τ | **Normalization convention** (=1 in pipeline); not independently calibrated |
| Deflection | **`normalized_proxy`**; Phase 5A scaffold only |
| López Fune | Rotation/dynamics; partial **Corbelli 2014 circularity** |
| Weak lensing | **Future work** (`m33_direct_weak_lensing_gap`) |

## Traceability

Full matrix: `outputs/tables/phase6a_claim_traceability_matrix.csv`  
Audit: `python scripts/run_phase6a_publication_audit.py`
