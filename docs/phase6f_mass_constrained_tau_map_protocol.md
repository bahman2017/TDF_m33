# Phase 6F — Mass-constrained smooth τ-map reconstruction protocol (M33)

**Status:** Documentation-first design phase (pre-registered protocol).  
**Branch:** `feature/phase6f-mass-constrained-tau-map`  
**Implementation:** Not started in this phase — no code, maps, or benchmark changes.

---

## 1. Purpose

Phase 6F defines the **next scientific step** for the [TDF_m33](https://github.com/bahman2017/TDF_m33) repository: a **pre-registered reconstruction protocol** in which map smoothness and **baryonic mass geometry enter the objective before the τ-map is frozen**, rather than as post-hoc visualization or axisymmetric extension of a low-parameter radial fit.

This document does **not** claim that existing Phase 4/5 τ products are invalid for their stated scope. It clarifies that they are **not** full physical mass-constrained 2D τ-maps and should not be read as such in manuscript or follow-up work.

---

## 2. Why M33 is the correct pilot

M33 is the appropriate **single-galaxy pilot** before any return to multi-galaxy (e.g. SPARC-scale) validation:

| Criterion | M33 status in this repo |
|-----------|-------------------------|
| Single galaxy, controlled scope | One target; documented assumptions in `docs/assumptions_and_limitations.md` |
| Documented rotation curve | `data/processed/m33_rotation.csv` (58 rows; Corbelli et al. 2014 Table 1) |
| Baryonic surface-density / velocity information | D1 disk-gravity derivation; Table 1 \(\Sigma_{\mathrm{HI}}\), \(\Sigma_\*\); PASS_WITH_CAVEAT documented |
| Existing pipeline | Phases 2–3C: baryonic / NFW / Burkert / low-parameter τ; Phase 3D sensitivity |
| Existing 2D scaffold | Phase 4A axisymmetric disk map; Phase 4B disk-to-sky projection (Corbelli 2014 geometry) |
| Deflection scaffold | Phase 5A normalized deflection **proxy** (not calibrated lensing) |
| Claim boundaries | Phase 6A traceability matrix; manuscript audits 6B–6E |

**Rationale:** M33 combines **high-quality radial kinematics**, **published baryonic surface-density models**, and an **end-to-end TDF branch already implemented** — but with a known gap between **axisymmetric τ(R) extension** and a **jointly constrained physical τ(x,y)**. Resolving that gap on one well-documented system is prerequisite to scaling claims.

---

## 3. Taxonomy: four τ representations (do not conflate)

| Object | Symbol / name | What it is in this repo | Mass-constrained? |
|--------|---------------|-------------------------|-------------------|
| Radial τ-profile | \(\tau(r)\) | Phase 3A–3C: \(d\tau/dr\) from \(\Delta v^2\); low-parameter knots | Rotation + smoothness only |
| Axisymmetric disk-plane map | \(\tau(R)\) | Phase 4A: \(\tau_{2\mathrm{D}}(x,y)=\tau_{\mathrm{radial}}(R)\); **not separately fitted** | **No** — radial extension |
| Projected sky map | \(\tau_{\mathrm{sky}}\) | Phase 4B: disk-to-sky using locked inclination/PA | **No** — projection of 4A |
| True mass-constrained map | \(\tau(x,y)\) | **Phase 6F target (future implementation)** | **Yes** — joint rotation + mass geometry + smoothness |

**Critical statement (Phase 6F design):**

> Current Phase 4A/4B maps are **axisymmetric radial extensions** of the Phase 3C low-parameter profile. They are useful for visualization, radial-consistency checks, and normalized deflection-proxy scaffolding. They are **not** full physical mass-constrained 2D τ-maps and must not be described as jointly optimized with baryonic surface-density geometry.

Metadata confirmation: `outputs/tables/phase4a_tau_2d_map_metadata.csv` — `note_axisymmetric_extension`: *"tau_2d(x,y)=tau_radial(R); not separately fitted"*.

---

## 4. Phase 6F scientific question

**Can M33 τ reconstruction jointly satisfy the following without adding a separate dark-matter halo inside the TDF branch?**

1. **Rotation-curve adequacy** — \(v_{\mathrm{obs}}\) fit within pre-registered holdout/tolerance on the Corbelli mask.
2. **Radial consistency** — azimuthally averaged \(\tau_{2\mathrm{D}}\) matches radial \(\tau(r)\) within stated RMSE (extends Phase 4A check with stricter gates).
3. **Bounded \(d\tau/dr\) variation** — no unphysical spikes vs Phase 3D sensitivity bounds.
4. **Mass-geometry alignment** — τ-map morphology not arbitrary relative to HI/stellar surface-density structure (see `L_mass_alignment`).
5. **Map smoothness** — controlled by explicit regularizers, not post-hoc filtering.
6. **Second-channel readiness** — projected map suitable for **future** deflection/lensing comparison only after hard gates pass; still **not** lensing confirmation.

**What this question does not ask:** whether dark matter is absent, whether M33 lensing validates τ-geometry, or whether τ replaces ΛCDM globally.

---

## 5. Pre-registered objective structure

Total loss (conceptual; weights from config in a future implementation phase):

\[
\mathcal{L}_{\mathrm{total}} =
  \mathcal{L}_{\mathrm{rotation}}
  + \lambda_{\mathrm{smooth}} \,\mathcal{L}_{\mathrm{smooth}}
  + \lambda_{\mathrm{curvature}} \,\mathcal{L}_{\mathrm{curvature}}
  + \lambda_{\mathrm{mass}} \,\mathcal{L}_{\mathrm{mass\_alignment}}
  + \lambda_{\mathrm{boundary}} \,\mathcal{L}_{\mathrm{boundary}}
  + \lambda_{\mathrm{sparse}} \,\mathcal{L}_{\mathrm{sparse\_delta\_r}}
\]

| Term | Role (design intent) |
|------|----------------------|
| \(\mathcal{L}_{\mathrm{rotation}}\) | Match \(v_{\mathrm{obs}}\) via TDF velocity law on fit mask |
| \(\mathcal{L}_{\mathrm{smooth}}\) | Penalize high-frequency τ variation (Tikhonov / Sobolev-style) |
| \(\mathcal{L}_{\mathrm{curvature}}\) | Penalize large second radial/azimuthal derivatives |
| \(\mathcal{L}_{\mathrm{mass\_alignment}}\) | Soft alignment of τ structure with baryonic mass geometry (not equating \(\Sigma\) to \(v\)) |
| \(\mathcal{L}_{\mathrm{boundary}}\) | Stable outer/inner τ behavior; no dominant edge artifacts |
| \(\mathcal{L}_{\mathrm{sparse\_delta\_r}}\) | Penalize isolated radial spikes in \(d\tau/dr\) |

**Fixed / bounded parameters (design):** \(K_\tau\) remains convention-bound unless a separate calibration phase is pre-registered; knot count or grid dof capped and reported.

---

## 6. Hard gates before any renewed deflection / lensing step

No Phase 5A-style deflection re-run or lensing comparison may be promoted until **all** gates pass and are logged in `phase6f_m33_decision_gate_report.md` (future artifact):

| Gate | Criterion (to be numerically locked in config) |
|------|-----------------------------------------------|
| G1 Rotation holdout | Holdout RMSE ≤ pre-registered tolerance |
| G2 Radial consistency | Azimuthal mean vs \(\tau(r)\) RMSE ≤ Phase 4A baseline improvement threshold |
| G3 Smoothness | \(\mathcal{L}_{\mathrm{smooth}}\), \(\mathcal{L}_{\mathrm{curvature}}\) below thresholds |
| G4 Inner boundary | No inner-radius jump dominating total \(\mathcal{L}\) |
| G5 Sparse-radius spikes | No single-bin \(d\tau/dr\) spike dominating residual structure |
| G6 Mass-alignment diagnostic | \(\mathcal{L}_{\mathrm{mass}}\) pass + documented HI/stellar weighting |
| G7 Parameter count | Effective dof ≤ pre-registered cap; reported vs NFW/Burkert for context only |
| G8 Claim-boundary checklist | Phase 6A prohibited language absent; deflection still `normalized_proxy` |

Failure of any gate → **stop**; document in decision report; **do not** upgrade lensing language.

---

## 7. Future implementation outputs (not generated in Phase 6F)

| Artifact | Description |
|----------|-------------|
| `outputs/tables/phase6f_m33_tau_profiles.csv` | Radial τ, \(d\tau/dr\), \(v_\tau\) from mass-constrained fit |
| `outputs/tables/phase6f_m33_mass_alignment_metrics.csv` | HI/stellar alignment diagnostics |
| `outputs/tables/phase6f_m33_smoothness_metrics.csv` | Smoothness/curvature/spike metrics |
| `outputs/reports/phase6f_m33_decision_gate_report.md` | Gate pass/fail with claim-control footer |
| `outputs/maps/phase6f_m33_tau_map.npz` | Disk-plane τ grid + metadata |
| `outputs/figures/phase6f_m33_tau_map_mass_overlay.png` | τ contours over baryonic geometry (diagnostic only) |

---

## 8. Relationship to prior phases

| Prior work | Phase 6F stance |
|------------|-----------------|
| Phase 3C low-parameter τ | **Baseline comparator**, not the final 2D map |
| Phase 4A axisymmetric map | **Scaffold**; superseded for physical claims if 6F succeeds |
| Phase 4B projection | **Geometry-locked scaffold**; reuse PA/i only after 6F gates |
| Phase 5A deflection proxy | **Frozen** until 6F gates; remains normalized, not arcsec |
| Phase 5C López Fune check | **Separate** dynamical upper bound; not lensing |
| Phase 6A–6E manuscript | **Unchanged** science; 6F is forward work |

---

## 9. Claim control (mandatory)

- Dark matter is **not** disproven.
- M33 lensing is **not** confirmed by this protocol.
- Normalized deflection proxy is **not** calibrated physical lensing.
- Mass alignment is a **regularizing diagnostic**, not proof that τ equals baryonic mass.
- M33 pilot success does **not** generalize to SPARC without a separate pre-registered program.

Controlled framing (unchanged):

> M33 is used as an intermediate-scale test of whether the missing acceleration inferred from rotation dynamics can be reconstructed as a smooth τ-geometry, and whether the same τ-map produces lensing/deflection predictions consistent with observational limits.

---

## 10. Next steps after Phase 6F design

1. **Phase 6F-impl (future):** ingest 2D baryonic maps per `docs/phase6f_data_requirements_for_physical_tau_map.md`.
2. Implement objective + gates in config-driven modules (new scripts, not retroactive edits to Phase 4A outputs).
3. Run gate report; only then consider deflection-proxy **re-computation** (still not observational lensing).
4. **Phase 7 (conceptual):** SPARC-scale or multi-galaxy extension only after M33 6F gates pass and manuscript addendum is drafted.

See also: `outputs/reports/phase6f_m33_design_summary.md`, `docs/project_plan.md`.
