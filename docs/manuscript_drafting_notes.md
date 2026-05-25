# Manuscript drafting notes (Phase 6C)

**Draft file:** `paper/m33_tdf_tau_geometry_draft.tex`  
**Audit:** `python scripts/run_phase6c_manuscript_draft_audit.py`

## Sections expanded (Phase 6C)

| Section | Expansion summary |
|---------|-------------------|
| Abstract | Full results narrative; all key metrics; explicit non-claims |
| Introduction | Motivation, scope, single-galaxy framing, non-goals |
| Data and provenance | Subsections on rotation, fit mask, geometry; Table 1 |
| Baryonic caveats | D1 derivation, Fig. 12, implications for fits |
| Baseline models | Subsections for baryonic / NFW / Burkert with metrics |
| TDF radial | Δv² pathway; 3A/3B vs 3C distinction; K_τ convention |
| Low-parameter TDF | Model family, metrics, conservative competitive statement; Figs 2–3; Table 2 |
| Sensitivity | Phase 3D bullets; PASS_WITH_CAVEAT stability |
| 2D τ-map | Phase 4A/4B subsections; axisymmetric caveat; Fig 4 |
| Deflection / López Fune | Phase 5A proxy; Phase 5C-B mass ratio; Fig 5 |
| Limitations | Numbered list (8 items) |
| Future work | Bulleted near-term items |
| Conclusion | Integrated summary with non-claims |
| Reproducibility | Pointer to phase6a commands and audits |

## Numbers used (from `phase6a_key_results_table.csv`)

| Quantity | Value | Source row |
|----------|-------|------------|
| Baryonic RMSE | 58.56 km/s (≈58.6 in prose) | baryonic_only |
| NFW RMSE / AIC / BIC | 4.16 / 68.0 / 72.0 | nfw |
| Burkert RMSE / AIC | 23.02 / 2342 | burkert |
| TDF 3-knot RMSE / AIC / BIC | 3.51 / 63.0 / 69.0 | tdf_lowparam_3knot |
| TDF 5-knot RMSE / AIC / BIC | 3.35 / 66.3 / 76.5 | tdf_lowparam_5knot |
| Phase 3D stability | PASS_WITH_CAVEAT | phase3d_sensitivity_stability |
| M_tau_eff @ 22.72 kpc | 7.51×10¹⁰ M☉ | phase5c_upper_bound |
| M_López enclosed | 6.7×10¹⁰ M☉ | phase5c_upper_bound |
| Ratio | 1.12 | phase5c_upper_bound |
| K_τ RMSE spread | 0.42 km/s | phase3d summary (prose) |

No new fits were run for Phase 6C.

## Claims that remain caveated

- D1 baryonic velocities: **PASS_WITH_CAVEAT** (all rotation comparisons).
- 3-knot vs NFW: **competitive** on this mask only; not cosmological proof.
- Phase 3D stability: **PASS_WITH_CAVEAT** (mask / K_τ qualifiers).
- 2D map: axisymmetric extension, not independent spatial fit.
- Deflection: **normalized_proxy** only; not arcsec; not detection.
- López Fune: dynamical upper bound; Corbelli circularity; **not weak lensing**.
- Weak lensing: **future work**.
- Dark matter disproof: **prohibited** (stated only as negation).

## Citations (Phase 6D)

| Key | Status |
|-----|--------|
| `Corbelli2014` | **Verified** — see `docs/manuscript_bibliography_verification.md` |
| `LopezFune2017` | **Verified** — see `docs/manuscript_bibliography_verification.md` |

Additional references require a new verification row before adding to `.tex`.

## Remaining TODO before journal submission

1. Replace figure placeholders with final PNGs (or copy figures into `paper/figures/`).
2. Add TDF / methodology references only with new verification rows in `manuscript_bibliography_verification.md`.
3. Author list, affiliations, acknowledgments, funding.
4. Run `latexmk -pdf paper/m33_tdf_tau_geometry_draft.tex` after figure copy (Phase 6D audit documents compile status).
4. Journal-specific formatting and word limits.
5. Uncertainty propagation (not in current pipeline tables).
6. Optional: 4-knot row in Table 2 for completeness.
7. Run `latexmk` and fix any LaTeX warnings.
8. Re-run Phase 6A–6C audits after any prose edit.

## Figure paths (optional files)

Figures use `\includefig` — builds without PNGs present. Paths per `docs/manuscript_figures_and_tables.md`.
