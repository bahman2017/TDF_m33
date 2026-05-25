# Manuscript figures and tables — output mapping

Each entry links an existing pipeline artifact to a manuscript element. **Do not** treat figures as new results; regenerate only via listed commands.

---

## Figure 1 — M33 rotation curve and baryonic-only model

| Field | Value |
|-------|-------|
| **Title** | Observed M33 rotation curve and baryonic-only baseline |
| **Output path** | `outputs/figures/phase2a_baryonic_only_rotation_curve.png` |
| **Also** | `outputs/tables/phase2a_baryonic_only_metrics.csv` |
| **Command** | `python scripts/run_phase2a_baryonic_only.py` |
| **Claim supported** | Baryons alone do not explain rotation on the processed dataset |
| **Caveat** | D1-derived \(v_{\mathrm{gas}}\), \(v_{\mathrm{disk}}\); PASS_WITH_CAVEAT |

---

## Figure 2 — NFW / Burkert / TDF rotation comparison

| Field | Value |
|-------|-------|
| **Title** | Rotation-curve comparison: NFW, Burkert, and low-parameter TDF models |
| **Output path** | `outputs/figures/phase3c_tdf_lowparam_rotation_comparison.png` |
| **Also** | `outputs/tables/phase3c_combined_model_comparison.csv` |
| **Command** | `python scripts/run_phase2b_halo_baselines.py` then `python scripts/run_phase3c_tdf_lowparam_model.py` |
| **Claim supported** | 3-knot TDF competitive with NFW on fit mask |
| **Caveat** | Burkert boundary-limited; NFW is ΛCDM baseline only; fair mask 0.4–23 kpc |

---

## Figure 3 — τ-gradient and τ-profile (3-knot)

| Field | Value |
|-------|-------|
| **Title** | Reconstructed τ-gradient and τ-profile for `tdf_lowparam_3knot` |
| **Output path** | `outputs/figures/phase3c_tdf_lowparam_tau_gradient.png` |
| **Also** | `outputs/figures/phase3c_tdf_lowparam_residuals.png`; `outputs/tables/phase3c_tdf_lowparam_profiles.csv` |
| **Command** | `python scripts/run_phase3c_tdf_lowparam_model.py` |
| **Claim supported** | Low-parameter τ describes missing-acceleration proxy in radius |
| **Caveat** | K_τ=1 normalization; not independent halo |

---

## Figure 4 — 2D τ-map and sky-projected map

| Field | Value |
|-------|-------|
| **Title** | Axisymmetric 2D τ-map and sky-plane projection |
| **Output path** | `outputs/figures/phase4a_tau_2d_map.png`; `outputs/figures/phase4b_tau_sky_projected_map.png` |
| **Also** | `outputs/maps/phase4a_tau_2d_map.npz`; `outputs/maps/phase4b_tau_sky_projected_map.npz` |
| **Command** | `python scripts/run_phase4a_tdf_2d_map.py`; `python scripts/run_phase4b_tau_projection.py` |
| **Claim supported** | 2D τ-map from frozen radial TDF model |
| **Caveat** | τ₂D(x,y)=τ_radial(R); no separate 2D fit; Corbelli geometry approximations |

---

## Figure 5 — Normalized deflection-proxy map

| Field | Value |
|-------|-------|
| **Title** | Normalized deflection-proxy from frozen sky-plane τ-map |
| **Output path** | `outputs/figures/phase5a_deflection_magnitude_map.png` |
| **Also** | `outputs/maps/phase5a_tau_deflection_proxy_map.npz`; `outputs/tables/phase5a_lensing_prediction_metadata.csv` |
| **Command** | `python scripts/run_phase5a_lensing_prediction.py` |
| **Claim supported** | Same τ-map yields deflection-proxy without separate halo |
| **Caveat** | `normalized_proxy` only; not arcsec; not observational detection |

---

## Table 1 — Data provenance

| Field | Value |
|-------|-------|
| **Title** | M33 data sources, processing flags, and validation |
| **Output path** | `data/processed/m33_rotation.csv`; `data/raw/sources_manifest.yaml`; `docs/data_sources.md` |
| **Command** | `python scripts/build_m33_rotation_processed.py`; `python scripts/validate_m33_data.py data/processed/m33_rotation.csv` |
| **Claim supported** | Traceable Corbelli 2014-based processed rotation table |
| **Caveat** | Baryonic velocities derived, not publisher columns |

---

## Table 2 — Model comparison

| Field | Value |
|-------|-------|
| **Title** | Rotation-fit metrics on 0.4–23 kpc mask |
| **Output path** | `outputs/tables/phase3c_combined_model_comparison.csv`; `outputs/tables/phase6a_key_results_table.csv` |
| **Command** | `python scripts/run_phase3c_tdf_lowparam_model.py`; `python scripts/run_phase6a_publication_audit.py` |
| **Claim supported** | Quantitative comparison baryonic / NFW / Burkert / TDF |
| **Caveat** | Phase 3A/3B not fair AIC competitors; D1 baryonic caveat |

---

## Table 3 — Claim and caveat summary

| Field | Value |
|-------|-------|
| **Title** | Supported claims, caveats, and prohibited language |
| **Output path** | `outputs/tables/phase6a_claim_traceability_matrix.csv`; `docs/manuscript_allowed_language.md` |
| **Command** | `python scripts/run_phase6a_publication_audit.py` |
| **Claim supported** | Manuscript claim control |
| **Caveat** | Prohibited row blocks DM-disproof language |

---

## Supplementary — Sensitivity and upper-bound

| Element | Output path | Command |
|---------|-------------|---------|
| Phase 3D summary | `outputs/tables/phase3d_tdf_sensitivity_summary.csv` | `python scripts/run_phase3d_tdf_sensitivity.py` |
| Publication summary | `outputs/reports/phase6a_publication_results_summary.md` | `python scripts/run_phase6a_publication_audit.py` |
| López Fune consistency | `outputs/tables/phase5c_upper_bound_consistency_summary.csv` | `python scripts/run_phase5c_upper_bound_consistency.py` |
