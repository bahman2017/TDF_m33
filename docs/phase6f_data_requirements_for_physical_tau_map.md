# Phase 6F — Data requirements for a physical mass-constrained τ-map (M33)

**Status:** Requirements specification only. No new data ingested in the design phase.

This document lists inputs needed to move from **axisymmetric radial τ extension** (Phase 4A) to a **mass-constrained disk-plane τ(x,y)** (Phase 6F implementation, future).

---

## 1. What the current pipeline already has

| Data product | Location / source | Sufficient for mass-constrained 2D τ? |
|--------------|-------------------|--------------------------------------|
| Radial \(v_{\mathrm{obs}}\), \(v_{\mathrm{err}}\) | `data/processed/m33_rotation.csv` | **Necessary**; not sufficient alone |
| Radial \(v_{\mathrm{gas}}\), \(v_{\mathrm{disk}}\) (D1 derived) | same | **Necessary** for rotation term; **not** 2D geometry |
| Radial \(\Sigma_{\mathrm{HI}}\), \(\Sigma_\*\) (Table 1) | raw/extracted Corbelli 2014 | **1D**; useful priors, not full map |
| Low-parameter \(\tau(r)\) | Phase 3C outputs | **Baseline**, not target map |
| Axisymmetric \(\tau(R)\) | Phase 4A NPZ | **Not** mass-constrained |
| Disk geometry (PA, \(i\)) | Phase 4B / tilted-ring extract | **Necessary** for projection |
| López Fune dynamical tables | extracted CSVs | **Comparison only**; not τ input |

---

## 2. Missing inputs for a true τ-map

### 2.1 Required (minimum set)

| Requirement | Purpose | Preferred source | Current gap |
|-------------|---------|------------------|-------------|
| **2D HI surface-density map** \(\Sigma_{\mathrm{HI}}(x,y)\) | Gas mass geometry; \(\mathcal{L}_{\mathrm{mass}}\) | Corbelli et al. 2014 VLA+GBT products; THINGS/Little THINGS if documented | Repo has **1D** Table 1 averages only |
| **Stellar mass / surface-brightness map** \(\Sigma_\*(x,y)\) | Disk geometry; \(\mathcal{L}_{\mathrm{mass}}\) | Corbelli et al. 2014 BVIgi synthesis map | **1D** \(\Sigma_\*\) in Table 1; full map not in repo |
| **Inclination \(i\)** | Deprojection / projection | Corbelli 2014 tilted-ring model | Radial model in extract; **2D warp** partially documented |
| **Position angle PA** | Disk orientation | same | Locked in Phase 4B for **existing** map only |
| **Tilted-ring / warp geometry** | Correct \(R(x,y)\) | `corbelli2014_tilted_ring_geometry_model_shape.csv` | Extend to 2D grid conventions |
| **Uncertainty maps** | Weighting \(\mathcal{L}_{\mathrm{rotation}}\), mass term | Published error models or propagated beams | Partial (radial \(v_{\mathrm{err}}\) only) |

### 2.2 Strongly recommended

| Requirement | Purpose |
|-------------|---------|
| **Velocity field \(v(x,y)\)** (HI moment-1 or tilted-ring 2D) | Azimuthal structure checks; holdout design |
| **Distance scale** | kpc pixel scale (840 kpc assumed in Corbelli 2014) |
| **Mask / coverage map** | Fit domain; avoid extrapolation-dominated regions |

### 2.3 Optional (Phase 6F+ / 2D diagnostics)

| Requirement | Purpose |
|-------------|---------|
| **CO / H₂ map** | Molecular gas geometry |
| **FITS cubes with WCS** | Reproducible reprojection |
| **Bulge/spheroid component map** | Inner dynamics if τ-map extends to center |

---

## 3. What must **not** be done

- Do **not** treat 1D \(\Sigma_{\mathrm{HI}}(r)\) or \(\Sigma_\*(r)\) as if they were already 2D maps.
- Do **not** copy surface density directly into \(v_{\mathrm{gas}}\) or \(v_{\mathrm{disk}}\) without documented disk-gravity derivation (Phase 1D-D1 rule stands).
- Do **not** use ResearchGate figures or unofficial mirrors as primary geometry inputs.
- Do **not** fabricate 2D pixels to unblock implementation.

---

## 4. Provenance and manifest requirements

Each new 2D product must:

1. Register a `source_id` in `data/raw/sources_manifest.yaml`.
2. Log transformation in `docs/data_sources.md` (dated row).
3. Store raw files under `data/raw/downloads/` with checksum.
4. Store processed grids under `data/processed/` or `data/raw/extracted/` with README column definitions.
5. Pass structural validation before entering Phase 6F fit scripts.

Suggested manifest entries to add in implementation phase:

- `corbelli2014_hi_2d_map` (or survey-specific id)
- `corbelli2014_stellar_mass_2d_map`
- `corbelli2014_velocity_field_2d` (if used)

---

## 5. Alignment with \(\mathcal{L}_{\mathrm{mass}}\) (design note)

Mass alignment is **not** the claim that \(\tau \propto \Sigma\). Design intent:

- Penalize τ features **strongly anti-correlated** with total baryonic surface density without rotation justification.
- Allow τ structure where rotation residuals require it, subject to smoothness and rotation terms.
- Weight gas vs stars explicitly; document in gate report.

Requires **2D** baryonic maps on a **common disk-plane grid** aligned with Phase 4B geometry conventions.

---

## 6. Readiness checklist (before Phase 6F implementation)

- [ ] 2D HI map acquired, checksum, documented
- [ ] 2D stellar mass or \(\Sigma_\*\) map acquired, checksum, documented
- [ ] PA, \(i\), warp model consistent with Phase 4B metadata
- [ ] Common grid definition (extent, pixel scale, mask) written to config
- [ ] Uncertainty or weight maps defined
- [ ] `docs/data_sources.md` transformation log updated
- [ ] No fabricated rows or pixels
- [ ] Claim-boundary review (Phase 6A matrix) unchanged for prior results

---

## 7. Relation to SPARC-scale work

M33 Phase 6F data requirements are **stricter per galaxy** than SPARC rotation-curve-only analyses because mass-constrained τ maps require **2D baryonic geometry**. A successful M33 6F gate pass is a **prerequisite design milestone** before exporting the protocol to other galaxies with adequate maps.

See: `docs/phase6f_mass_constrained_tau_map_protocol.md`.
