# Phase 6F-data — Provenance and data readiness checklist

**Purpose:** Gate Phase 6F-impl (mass-constrained τ reconstruction) on traceable, reproducible 2D inputs.

**Phase 6F-data scope:** Checklist definition and **current gate status** only. Filling gates requires real downloads and validation scripts — **not done in this documentation phase**.

**Rule:** Phase 6F-impl is **blocked** until every **required** gate below is `PASS` with logged evidence. Optional gates may remain `N/A` if documented.

---

## Gate summary (required)

| Gate ID | Gate | Required? | Status (2026-05-24) |
|---------|------|-----------|----------------------|
| G1 | Source traceability | Yes | **FAIL** — 2D maps not acquired |
| G2 | Unit conversion path | Yes | **FAIL** — no FITS/products to convert |
| G3 | Coordinate / projection compatibility | Yes | **FAIL** — no aligned 2D grid |
| G4 | M33 disk geometry compatibility | Yes | **PARTIAL** — radial tilted-ring CSV only |
| G5 | Uncertainty handling plan | Yes | **PARTIAL** — radial \(v_{\mathrm{err}}\) only |
| G6 | Reproducible download or manual acquisition note | Yes | **FAIL** — URLs documented; files not in repo |
| G7 | No hidden hand-edited data | Yes | **PASS** — policy documented; no 2D edits |
| G8 | Claim boundary preservation | Yes | **PASS** — no τ/deflection runs in 6F-data |

**Overall readiness:** **NOT READY** for Phase 6F-impl.

---

## G1 — Source traceability

**Requirement:** Every 2D input has a registered `source_id`, bibliographic citation, retrieval URL or DOI, retrieval date, and SHA-256 checksum of raw file(s).

**Evidence required:**

- [ ] Entry in `data/raw/sources_manifest.yaml` for each 2D product
- [ ] Row in `docs/data_sources.md` with transformation chain
- [ ] Raw file under `data/raw/downloads/` (or documented external stable archive with version pin)
- [ ] No ResearchGate / unofficial mirrors as **primary** source

**Current state:** Corbelli 2014 PDF and 1D extracts traceable; **2D HI and stellar maps absent**.

---

## G2 — Unit conversion path

**Requirement:** Documented, testable path from raw FITS/table units to repo standard:

- \(\Sigma_{\mathrm{HI}}\), \(\Sigma_*\) in \(M_\odot\,\mathrm{pc}^{-2}\) (or explicit alternate with conversion formula)
- Velocity in km s\(^{-1}\) with frame documented (helio/bary/LSR)
- Distance scale: \(D = 840\,\mathrm{kpc}\) (Corbelli 2014) unless primary paper update justified

**Evidence required:**

- [ ] `docs/data_sources.md` section with BUNIT / column mapping
- [ ] Validation script or unit test on a known pixel / aperture integral vs Table 1 radial average (tolerance stated)
- [ ] No copying \(\Sigma\) directly into \(v_{\mathrm{gas}}\) without Phase 1D-D1 disk-gravity rule

**Current state:** 1D D1 derivation documented; **no 2D conversion script**.

---

## G3 — Coordinate / projection compatibility

**Requirement:** HI, stellar, and (if used) velocity maps share a common pixel grid or documented reprojection to a Phase 6F analysis grid with WCS logged.

**Evidence required:**

- [ ] FITS WCS headers archived or copied to sidecar JSON
- [ ] Reprojection method named (e.g. `reproject`, `astropy.wcs`) with version pin
- [ ] Maximum alignment error at test points (arcsec or kpc) below pre-registered threshold in 6F-impl protocol
- [ ] Mask / footprint overlap fraction recorded

**Current state:** Phase 4B sky projection uses locked geometry for **axisymmetric τ** only; **no baryonic map grid**.

---

## G4 — M33 disk geometry compatibility

**Requirement:** Tilted-ring / warp model consistent with 2D map alignment and Phase 4B geometry reference.

**Evidence required:**

- [ ] `corbelli2014_tilted_ring_geometry_model_shape.csv` linked to map epoch
- [ ] Center, PA\((R)\), \(i(R)\) applied consistently in deprojection
- [ ] Warp approximation noted (Corbelli 2014 Sect. 4.1) in readiness report
- [ ] Inner/outer radii coverage vs τ-map fit domain documented

**Current state:** **PARTIAL** — 12-ring CSV in repo; 2D warp field not constructed.

---

## G5 — Uncertainty handling plan

**Requirement:** Pre-registered plan for weights in \(\mathcal{L}_{\mathrm{rotation}}\) and \(\mathcal{L}_{\mathrm{mass}}\):

- Radial: `v_err_kms` in `m33_rotation.csv` (existing)
- 2D mass: beam noise map, fractional error, or conservative uniform weight with justification
- Propagation: document if errors are correlated (beam smoothing)

**Evidence required:**

- [ ] Written plan in readiness report § uncertainties
- [ ] Uncertainty arrays stored alongside processed maps (not invented constants)
- [ ] Missing uncertainty → down-weight or exclude region (documented)

**Current state:** Radial rotation errors only.

---

## G6 — Reproducible download or manual acquisition

**Requirement:** Either (a) scripted download with pinned URL and checksum verification, or (b) manual acquisition log with exact file names, contact/email if author-provided, and checksum.

**Evidence required:**

- [ ] `docs/extraction_log.md` or Phase 6F acquisition log entry per file
- [ ] Command or curl/wget recipe in `docs/reproducibility_commands.md` (commented until script exists)
- [ ] License permits repository redistribution or documents keep-local-only policy

**Current state:** Acquisition plan documents DOIs and channels; **no downloaded 2D files**.

---

## G7 — No hidden hand-edited data

**Requirement:** No manually edited pixel values in processed maps except via documented, versioned scripts. Digitized figures are **not** primary 2D inputs.

**Evidence required:**

- [ ] Processed maps produced only by checked-in scripts
- [ ] Git history / script hash referenced in readiness report
- [ ] Explicit statement if any mask is hand-drawn (discouraged; prefer threshold on SNR)

**Current state:** **PASS** (policy); Table 1 extraction was scripted/audited; no 2D maps exist.

---

## G8 — Claim boundary preservation

**Requirement:** Data phase does not run τ fit, deflection, or lensing comparison; does not update Phase 3–5 outputs; manuscript claim matrix unchanged.

**Evidence required:**

- [ ] No new `phase6f_tau_*` or deflection outputs in repo
- [ ] README / project_status state data-readiness only
- [ ] Phase 4A metadata note on axisymmetric scaffold unchanged

**Current state:** **PASS** for Phase 6F-data documentation phase.

---

## Optional gates (CO, THINGS cross-check)

| Gate | When required | Status |
|------|---------------|--------|
| G-OPT-CO | If \(\Sigma_{H_2}\) enters \(\mathcal{L}_{\mathrm{mass}}\) | N/A (optional) |
| G-OPT-THINGS | If THINGS used as primary or validation | N/A (reference catalogued) |
| G-OPT-VEL | 2D velocity holdout | Recommended; not blocking catalog phase |

---

## Sign-off template (future)

When all required gates pass, append to `outputs/reports/phase6f_data_readiness_report.md`:

```
Phase 6F-data sign-off
Date:
Reviewer:
G1–G8: PASS (evidence links)
Approved for Phase 6F-impl branch: yes/no
```

Until sign-off exists, **`run_phase6f_mass_constrained_tau_map.py` must not be executed** (script not yet present).

---

## Related documents

- `docs/phase6f_data_acquisition_plan.md` — candidate sources
- `outputs/reports/phase6f_data_readiness_report.md` — living status
- `docs/phase6f_mass_constrained_tau_map_protocol.md` — hard gates for fit phase (separate from data gates)
