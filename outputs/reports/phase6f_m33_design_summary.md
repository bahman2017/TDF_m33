# Phase 6F — M33 mass-constrained τ-map design summary

**Date:** 2026-05-24  
**Phase type:** Documentation-first scientific design (no implementation)  
**Branch:** `feature/phase6f-mass-constrained-tau-map`

---

## Executive summary

The TDF_m33 repository has completed rotation dynamics, halo baselines, low-parameter radial τ, an **axisymmetric 2D extension**, disk-to-sky projection, and a **normalized deflection proxy** (Phases 2–6E). Phase 6F defines the **next pre-registered step**: reconstruct a **smooth, mass-geometry-aware disk-plane τ-map** whose regularization enters **before** freezing the map — not as post-hoc smoothing of a radial profile.

**Current Phase 4/5 maps are not full physical mass-constrained τ-maps.** Phase 4A explicitly sets \(\tau_{2\mathrm{D}}(x,y)=\tau_{\mathrm{radial}}(R)\) without separate 2D fitting.

---

## Why M33 first

- Single, deeply documented galaxy
- Canonical rotation curve + D1 baryonic velocities (with stated caveats)
- Full TDF vs NFW/Burkert comparison already in repo
- Existing projection and deflection **scaffold** for second-channel **readiness** testing after gates
- Conservative claim infrastructure (Phase 6A traceability, manuscript audits)

Multi-galaxy SPARC-scale validation is **out of scope** until M33 Phase 6F gates are defined and (in a later phase) passed.

---

## Scientific question (Phase 6F)

Can M33 τ reconstruction **jointly** satisfy rotation adequacy, radial consistency, bounded \(d\tau/dr\), mass-geometry alignment, and smoothness — **without a separate dark-matter halo in the TDF branch** — while remaining ready for a **future** deflection comparison only after hard gates?

**Not asked:** DM disproof; lensing detection; universal ΛCDM replacement.

---

## Objective structure (pre-registered)

\[
\mathcal{L}_{\mathrm{total}} =
  \mathcal{L}_{\mathrm{rotation}}
  + \lambda_{\mathrm{smooth}} \mathcal{L}_{\mathrm{smooth}}
  + \lambda_{\mathrm{curvature}} \mathcal{L}_{\mathrm{curvature}}
  + \lambda_{\mathrm{mass}} \mathcal{L}_{\mathrm{mass\_alignment}}
  + \lambda_{\mathrm{boundary}} \mathcal{L}_{\mathrm{boundary}}
  + \lambda_{\mathrm{sparse}} \mathcal{L}_{\mathrm{sparse\_delta\_r}}
\]

Weights and numeric thresholds → future `configs/` section (not set in design phase).

---

## Hard gates (before deflection re-run)

1. Rotation holdout tolerance  
2. Radial consistency tolerance  
3. Smoothness / curvature thresholds  
4. No inner-boundary jump dominance  
5. No sparse-radius spike dominance  
6. Mass-alignment diagnostic pass  
7. Parameter count controlled  
8. Claim-boundary checklist passed  

---

## Data gaps (see requirements doc)

Minimum missing inputs for implementation:

- 2D HI \(\Sigma_{\mathrm{HI}}(x,y)\)
- 2D stellar \(\Sigma_\*(x,y)\) or mass map
- Full inclination / PA / warp grid alignment
- Uncertainty / mask maps

**Not in repo today as 2D products** — only radial Table 1 and Phase 4A radial extension.

---

## Future outputs (not created in Phase 6F design)

| File | Role |
|------|------|
| `phase6f_m33_tau_profiles.csv` | Radial diagnostics from constrained fit |
| `phase6f_m33_mass_alignment_metrics.csv` | Geometry alignment |
| `phase6f_m33_smoothness_metrics.csv` | Regularization metrics |
| `phase6f_m33_decision_gate_report.md` | Pass/fail gates |
| `phase6f_m33_tau_map.npz` | Disk-plane map |
| `phase6f_m33_tau_map_mass_overlay.png` | Diagnostic overlay |

---

## Claim boundaries (unchanged)

| Statement | Status |
|-----------|--------|
| Dark matter disproven | **Prohibited** |
| M33 lensing confirms τ | **Prohibited** |
| Deflection proxy = physical lensing | **Prohibited** |
| Phase 4A map = mass-constrained τ | **Prohibited** |
| M33 intermediate τ test | **Supported framing** |
| Low-parameter τ rotation fit | **Supported (Phase 3C)** |
| Normalized deflection scaffold | **Caveated (Phase 5A)** |

---

## Documentation artifacts (this phase)

| Document | Path |
|----------|------|
| Protocol | `docs/phase6f_mass_constrained_tau_map_protocol.md` |
| Data requirements | `docs/phase6f_data_requirements_for_physical_tau_map.md` |
| This summary | `outputs/reports/phase6f_m33_design_summary.md` |

---

## Reproducibility (Phase 6F design)

No new pipeline scripts are run in this phase. Existing pipeline commands remain in `docs/reproducibility_commands.md` and `outputs/reports/phase6a_reproducibility_commands.md`.

**Phase 6F implementation placeholders (future):**

```bash
# NOT RUN in Phase 6F design — placeholders only
# python scripts/run_phase6f_mass_constrained_tau_map.py
# python scripts/run_phase6f_decision_gate_audit.py
```

---

## Recommended next phase

**Phase 6F-impl:** Acquire 2D baryonic maps → implement objective + gates → emit future artifacts → **only then** consider recomputing deflection proxy under unchanged normalized units.
