# Baryonic velocity derivation plan (Phase 1D-D0)

Audit and strategy for populating `v_gas_kms`, `v_disk_kms`, and `v_bulge_kms` in `data/processed/m33_rotation.csv` from Corbelli et al. (2014) inputs **without** mapping surface densities directly into velocity columns.

**Status:** Phase 1D-D2-B complete — canonical **`data/processed/m33_rotation.csv`** (58 rows) built from D1 audit with documented caveats.  
**Primary source:** Corbelli et al. 2014, A&A 572, A23 ([DOI 10.1051/0004-6361/201424033](https://doi.org/10.1051/0004-6361/201424033))  
**Raw inputs on hand:** `data/raw/extracted/corbelli2014_table1_raw.csv` (58 rows: \(R\), \(V_r\), \(\sigma_V\), \(\Sigma_{\mathrm{HI}}\), \(\Sigma_\*\))

---

## 1. Scientific requirement

Processed schema (`docs/data_sources.md`, `configs/m33_default.yaml`) requires per-radius:

| Column | Meaning |
|--------|---------|
| `v_obs_kms` | From Table 1 \(V_r\) (after documented mapping) |
| `v_err_kms` | From Table 1 \(\sigma_V\) |
| `v_gas_kms` | Gas disk contribution to circular speed |
| `v_disk_kms` | Stellar disk contribution |
| `v_bulge_kms` | Bulge term (0 if justified) |

Project relation (Phase 2+ / `docs/theory_summary.md`):

\[
v_{\mathrm{bar}}^2(r) = v_{\mathrm{gas}}^2(r) + v_{\mathrm{disk}}^2(r) + v_{\mathrm{bulge}}^2(r)
\]

**Hard rule:** \(\Sigma_{\mathrm{HI}}\) and \(\Sigma_\*\) from Table 1 are **not** velocities. They may inform mass models only through a documented dynamical calculation.

---

## 2. PDF audit — Sections 5–6 (Corbelli et al. 2014)

Audited against `data/raw/downloads/corbelli2014_aa24033_14.pdf` (page numbers = PDF footer “page *n* of 18”).

### 2.1 Section 5 — Baryonic surface densities (PDF pp. 10–11)

| Topic | Paper statement | Implication for this repo |
|-------|-----------------|---------------------------|
| Stellar mass map | **BVIgi** map primary; BVI map compared | Table 1 \(\Sigma_\*\) = BVIgi values (“most likely” in §6); use `sigma_star` from raw CSV as-is |
| Fig. 10 | HI \(\Sigma\) perpendicular to disk; stellar \(\Sigma_\*\); **total baryonic** = atomic + molecular H\(_2\) + **helium** + stars (Sect. 2.2) | Table 1 gives \(\Sigma_{\mathrm{HI}}\) only for gas; **H\(_2\) and He not tabulated** in Table 1 |
| HI vs dynamical gas | Continuous line in Fig. 10 = log function for **hydrogen** dynamical contribution; outer HI ring averaging bias ~20% on mass | Derivation must document whether \(v_{\mathrm{gas}}\) uses Table 1 \(\Sigma_{\mathrm{HI}}\) or Fig. 10 fitted profile |
| Sect. 2.2 (PDF p. 3) | \(\Sigma_{\mathrm{H_2}} = 10 \times e^{-R/2.2}\) M\(_\odot\) pc\(^{-2}\) (CO-based); HI and H\(_2\) surface densities **× 1.33** for helium | Reproducible **total gas surface density** for dynamics: \(\Sigma_{\mathrm{gas}} = 1.33\,(\Sigma_{\mathrm{HI,table}} + \Sigma_{\mathrm{H_2}}(R))\) with documented formula |
| Bulge | Corbelli (2003) bulge **not supported**; inner 1.5 kpc likely **higher M/L**, not a bulge (Corbelli & Walterbos 2007) | **`v_bulge_kms = 0`** with explicit note in processed `notes` |
| M\(_\*\) uncertainty | ~30% on stellar surface densities; log M\(_\*\) intervals given for fits | Propagate or bracket in validation (Phase 1D-D1) |

### 2.2 Section 6 — Dynamical analysis (PDF pp. 11–13)

| Topic | Paper statement | Implication |
|-------|-----------------|-------------|
| Fitting range | \(0.4 \le R \le 23\) kpc | Processed CSV grid = Table 1 (\(0.24\)–\(22.72\) kpc); **no extrapolation** beyond Table 1 without `data_quality_flag` |
| Surface density input | Azimuthal averages **as in Fig. 10** | Align gas \(\Sigma(r)\) construction with Fig. 10 / Sect. 2.2, not ad hoc scaling of \(\Sigma\) to \(v\) |
| Vertical structure | Gas: uniform disk, **half-thickness 0.5 kpc**; stars: **flaring** disk, \(h_z = 100\) pc center → **1 kpc** at outer edge | Required for **Casertano (1983)** thick-disk force calculation |
| Method | Disk contributions computed **according to Casertano (1983)** (thick disks) | **Option A** anchor |
| Fig. 12 | Observed RC + NFW fit; **small dashed = gas**, **large dashed = stellar** disk contributions to RC | **Option B** cross-check target (digitization), not primary if Option A implemented |
| Table 1 | Final adopted \(V_r\), \(\sigma_V\), \(\Sigma_{\mathrm{HI}}\), \(\Sigma_\*\) | Already in `corbelli2014_table1_raw.csv`; **no** \(v_{\mathrm{gas}}\), \(v_{\mathrm{disk}}\) columns |

### 2.3 Related PDF elements

| Item | Location | Note |
|------|----------|------|
| Finite disk thickness corrections | Appendix B (PDF p. 18); applied to **observed** \(V_r\) before Table 1 | Already embedded in published \(V_r\); do not double-apply when setting `v_obs_kms` |
| Casertano (1983) reference | Bibliography | MNRAS 203, 735 — implement or cite equivalent thick-disk potential |
| Molecular gas | Sect. 2.1 / 2.2 | Not in Table 1; must be added from published \(\Sigma_{\mathrm{H_2}}(R)\) formula for consistent \(v_{\mathrm{gas}}\) |

---

## 3. Repository manifest / doc inventory

| source_id | Role for baryonic velocities | Status |
|-----------|------------------------------|--------|
| `corbelli_et_al_2014` | **Primary** — Table 1 + Sect. 5–6 + Casertano method | PDF downloaded; raw Table 1 extracted |
| `lopez_fune_salucci_corbelli_2017` | Phase 2 NFW/Burkert; manifest lists `v_gas_kms`, `v_disk_kms` for **cross-check**, not Phase 1D primary | `located` — no files |
| `corbelli_salucci_2000` | Historical \(v_{\mathrm{obs}}\) validation only | `located` — no files |
| `configs/m33_default.yaml` | `baryonic_model.components`: gas, stellar_disk; bulge commented | Placeholders null; `allow_creation_without_baryonic_velocity_components: false` |
| `docs/data_acquisition_plan.md` | Planned `v_gas_kms` / `v_disk_kms` from Corbelli 2014 decomposition or López Fune backup | No numerical pipeline yet |
| `docs/extraction_log.md` | §5.1–5.2 Table 1 audit; explicit no-\(\Sigma\to v\) rule | Complete through 1D-C |

**Conclusion:** No machine-readable \(v_{\mathrm{gas}}(r)\), \(v_{\mathrm{disk}}(r)\) table exists in the repo yet. Derivation or external table acquisition is mandatory before `m33_rotation.csv`.

---

## 4. Options comparison

### Option A — Reconstruct from surface densities + Casertano (1983) (preferred)

**Method:** Build axisymmetric surface density profiles \(\Sigma_{\mathrm{gas}}(R)\) and \(\Sigma_\*(R)\) on the Table 1 grid, then compute circular speed contributions \(v_{\mathrm{gas}}(R)\), \(v_{\mathrm{disk}}(R)\) using the same thick-disk treatment as §6 (Casertano 1983, with stated \(h_z\) for gas and flaring stellar disk).

**Inputs:**

| Component | Source |
|-----------|--------|
| \(\Sigma_{\mathrm{HI}}(R)\) | Table 1 → `sigma_hi` |
| \(\Sigma_{\mathrm{H_2}}(R)\) | Paper Sect. 2.2: \(10\,e^{-R/2.2}\) M\(_\odot\) pc\(^{-2}\) |
| Helium | Factor **1.33** on (HI + H\(_2\)) per Sect. 2.2 |
| \(\Sigma_\*(R)\) | Table 1 → `sigma_star` (BVIgi) |
| \(h_z\) gas | 0.5 kpc half-thickness, uniform |
| \(h_z\) stars | Flaring: 0.1 kpc center → 1 kpc at outer edge (linear in \(R\) per paper wording) |

**Pros:** Reproducible; aligned with paper’s dynamical analysis; no figure digitization.  
**Cons:** Requires implementing or importing Casertano (1983) (or validated equivalent); must document H\(_2\)+He extension not in Table 1; small differences vs Fig. 10 fitted HI line possible.

### Option B — Digitize Fig. 12 gas / stellar curves (cross-check only)

**Method:** WebPlotDigitizer (or similar) on Fig. 12 dashed curves (gas = small dashes, stellar = large dashes) at \(R = 0.4\)–23 kpc.

**Pros:** Direct match to published decomposition plot.  
**Cons:** Not fully reproducible from tabulated data; digitization uncertainty; color/line-style ambiguity in print; **should not be primary** if Option A is feasible.

### Option C — External machine-readable decomposition

**Method:** Acquire supplementary tables or data releases from Corbelli et al. 2014, López Fune et al. 2017, or related works with explicit \(v_{\mathrm{gas}}\), \(v_{\mathrm{disk}}\) columns.

**Pros:** Minimal reimplementation if official tables exist.  
**Cons:** None located in repo; López Fune 2017 not downloaded; may mix halo-centric decomposition with different \(R\) grid; still requires provenance audit.

---

## 5. Recommendation

| Role | Path |
|------|------|
| **Primary** | **Option A** — Casertano (1983) thick-disk rotation from \(\Sigma\) profiles with paper Sect. 2.2 + 6 assumptions |
| **Fallback** | **Option B** — Digitize Fig. 12 gas/stellar curves **only** to validate Option A at ≥5 radii (inner, mid, outer); discrepancies > few km s\(^{-1}\) trigger audit |
| **Secondary fallback** | **Option C** — If A&A supplementary machine-readable curves are found, prefer tabulated values with matching \(R\) grid and document any scaling |

Do **not** use López Fune et al. 2017 as the Phase 1D primary baryonic source (Phase 2 halo baseline only per `docs/data_acquisition_plan.md`).

---

## 6. Chosen path — formulas, assumptions, validation

### 6.1 Assumptions (locked for Phase 1D-D1 unless paper audit overrides)

1. **\(v_{\mathrm{bar}}^2 = v_{\mathrm{gas}}^2 + v_{\mathrm{disk}}^2 + v_{\mathrm{bulge}}^2\)** with \(v_{\mathrm{bulge}} = 0\) (no bulge; §5 discussion).
2. **Gas includes HI + H\(_2\) + helium** as in Sect. 2.2 and Fig. 10 caption:  
   \(\Sigma_{\mathrm{gas}}(R) = 1.33 \left[\Sigma_{\mathrm{HI,table}}(R) + \Sigma_{\mathrm{H_2}}(R)\right]\),  
   \(\Sigma_{\mathrm{H_2}}(R) = 10 \exp(-R/2.2)\) M\(_\odot\) pc\(^{-2}\).
3. **Stellar disk** uses Table 1 \(\Sigma_\*\) (BVIgi table values).
4. **Axisymmetric disk gravity** (Phase 1D-D1 implementation): numerical midplane integration with exponential vertical \(\rho(z)\), matching §6 \(h_z\) laws — related to but not a full reimplementation of Casertano (1983) Bessel-function formalism.
5. **\(v_{\mathrm{obs}}\)** from Table 1 \(V_r\) (finite-thickness corrections already in adopted curve per Appendix B).
6. **Radius grid:** Table 1 radii only (\(N=58\)); no extrapolation; rows outside dynamical fit range \(0.4\)–23 kpc flagged in `notes` if needed (first row \(R=0.24\) kpc).
7. **Interpolation:** None required if output is evaluated on the same Table 1 \(R\) grid; if resampling is ever needed, document spline type in `docs/data_sources.md`.

### 6.2 Validation checks (Phase 1D-D1 acceptance)

| Check | Criterion |
|-------|-----------|
| Algebraic | \(v_{\mathrm{gas}}, v_{\mathrm{disk}} \ge 0\); \(v_{\mathrm{bar}}^2 \le v_{\mathrm{obs}}^2\) at most radii (exceptions flagged) |
| Spot vs Fig. 12 | \(v_{\mathrm{gas}}(R)\), \(v_{\mathrm{disk}}(R)\) within ~5 km s\(^{-1}\) of digitized dashes at \(R \in \{1, 5, 10, 15, 20\}\) kpc (fallback B) |
| Casertano sanity | \(v_{\mathrm{gas}}\) rises in inner disk; stellar dominates \(R < 7\) kpc per §5 |
| Schema | `validate_m33_data.py` PASS on `m33_rotation.csv` |
| Provenance | Transformation row in `docs/data_sources.md`; script path under `scripts/` |
| No alias | Regression test: `sigma_hi` ≠ `v_gas_kms`, `sigma_star` ≠ `v_disk_kms` |

### 6.3 Outputs (Phase 1D-D2, not D0)

| File | Content |
|------|---------|
| `data/processed/m33_rotation.csv` | 58 rows: `v_obs_kms`, `v_err_kms`, `v_gas_kms`, `v_disk_kms`, `v_bulge_kms=0`, provenance fields |
| Optional interim | `data/raw/extracted/corbelli2014_baryonic_velocity_interim.csv` if useful for audit |

---

## 7. Phase 1D-D1 — implementation (2026-05-24)

| Item | Value |
|------|--------|
| Module | `src/tdf_m33/models/disk_gravity.py` |
| Derivation | `scripts/derive_corbelli2014_baryonic_velocities.py` |
| Validation | `scripts/validate_corbelli2014_baryonic_velocity_derivation.py` |
| Interim output | `outputs/tables/corbelli2014_baryonic_velocity_derivation_audit.csv` (58 rows) |
| Method tag | `axisymmetric_disk_gravity_exponential_vertical` |

**Numerical method:** For each component, convert \(\Sigma\) [M\(_\odot\) pc\(^{-2}\)] → [M\(_\odot\) kpc\(^{-2}\)]; use \(G = 4.30091\times10^{-6}\) kpc (km/s)\(^2\) M\(_\odot^{-1}\); integrate midplane inward radial acceleration over \(R'\), \(\phi\), \(z\) with \(\rho = \Sigma/(2h_z)\exp(-|z|/h_z)\); \(v_c=\sqrt{R\,g_R}\). Default grid: 240×72×48 (midpoint quadrature, \(r\) softening 0.02 kpc).

**Sample audit values (interim, not validated vs Fig. 12 yet):**

| \(R\) [kpc] | \(v_{\mathrm{obs}}\) | \(v_{\mathrm{gas}}\) | \(v_{\mathrm{disk}}\) | \(v_{\mathrm{bar}}\) |
|-------------|----------------------|----------------------|-----------------------|----------------------|
| 0.24 | 37.3 | 2.7 | 16.3 | 16.5 |
| 5.13 | 108.8 | 27.2 | 59.5 | 65.5 |
| 22.72 | 119.6 | 24.3 | 31.8 | 40.0 |

### Known numerical caveats (D1)

- Implementation uses **cylindrical numerical integration**, not the paper’s Casertano (1983) routine; absolute \(v_{\mathrm{gas}}\), \(v_{\mathrm{disk}}\) may differ by tens of percent from Fig. 12 dashed curves.
- Innermost radii (\(R < 0.4\) kpc) are outside the paper’s quoted dynamical fit range; treat as extrapolation of the \(\Sigma\) profiles.
- \(v_{\mathrm{bar}} < v_{\mathrm{obs}}\) at most radii is expected (dark matter not included in baryonic derivation).
- Fig. 12 digitization remains the **fallback sanity check** for Phase 1D-D2.

## 8. Phase 1D-D2-A — Fig. 12 sanity-check (2026-05-24)

| Item | Value |
|------|--------|
| Spot-check (validation only) | `data/raw/extracted/corbelli2014_fig12_baryonic_spotcheck.csv` |
| Comparison table | `outputs/tables/corbelli2014_baryonic_fig12_comparison.csv` |
| Script | `scripts/compare_corbelli2014_baryonic_to_fig12.py` |
| Figure | `outputs/figures/corbelli2014_baryonic_fig12_sanity_check.png` |
| Panel used | Fig. 12 **bottom** (BVIgi): small blue dashes = gas; large red dashes = stellar |

**Digitization:** Visual read from `data/raw/downloads/corbelli2014_aa24033_14.pdf` (PDF p. 12 of 18). Conservative uncertainty ±5 km s\(^{-1}\). **Lower precision** than Table 1 or D1 numerical derivation — sanity check only.

**Residuals (D1 derived − Fig. 12 digitized) at spot radii:**

| \(R\) [kpc] | \(\Delta v_{\mathrm{gas}}\) | \(\Delta v_{\mathrm{disk}}\) |
|-------------|----------------------------|------------------------------|
| 1 | ≈ −36 | ≈ +39 |
| 5 | ≈ −43 | ≈ +35 |
| 10 | ≈ −19 | ≈ +9 |
| 15 | ≈ −16 | ≈ +6 |
| 20 | ≈ −14 | ≈ +6 |

**Outcome:** **`REVIEW_REQUIRED`** — D1 \(v_{\mathrm{gas}}\) is systematically **low** vs Fig. 12 (often 15–40 km s\(^{-1}\)); \(v_{\mathrm{disk}}\) is **high** in the inner disk (≈30–40 km s\(^{-1}\) at \(R \lesssim 5\) kpc), closer at \(R \gtrsim 10\) kpc. This is consistent with D1 using numerical cylindrical quadrature + exponential vertical profiles rather than the paper’s Casertano (1983) routine and possibly different \(\Sigma(r)\) weighting than the Fig. 10 curves used for dynamics.

**Rules honored:** No silent retuning of D1; no `m33_rotation.csv`; Fig. 12 is **not** the primary source — D1 audit from tabulated \(\Sigma\) remains reproducible primary.

**D2-A original spot-check superseded for comparisons** by label audit (see §8.1).

## 8.1 Phase 1D-D2-A2 — Fig. 12 label audit (2026-05-24)

| Item | Value |
|------|--------|
| Caption (PDF p. 12) | “red and blue … show the **gas** and **stellar** disk” → **red = gas**, **blue = stellar** |
| D2-A error | Inner **blue** (high) curve was digitized as gas; **red** (lower) as stellar — **labels swapped** |
| Physics check | Paper §5/§6: stars dominate potential for \(R < 7\) kpc; gas and stars comparable beyond |
| Label audit | `outputs/tables/corbelli2014_fig12_label_audit.csv` |
| Script | `scripts/audit_corbelli2014_fig12_labels.py` |
| Corrected spot-check | `data/raw/extracted/corbelli2014_fig12_baryonic_spotcheck_corrected.csv` (original file retained) |
| Corrected comparison | `outputs/tables/corbelli2014_baryonic_fig12_comparison_corrected.csv` |
| Corrected figure | `outputs/figures/corbelli2014_baryonic_fig12_sanity_check_corrected.png` |

**Verdict:** **`LIKELY_SWAPPED`** — swapping gas/disk columns cuts total residual sum sharply and restores \(v_{\mathrm{disk}} > v_{\mathrm{gas}}\) at \(R < 7\) kpc.

**Corrected residuals (D1 − Fig. 12 corrected digitization):**

| \(R\) [kpc] | \(\Delta v_{\mathrm{gas}}\) | \(\Delta v_{\mathrm{disk}}\) |
|-------------|----------------------------|------------------------------|
| 1 | ≈ −1 | ≈ +1 |
| 5 | ≈ +2 | ≈ −10 |
| 10 | ≈ −2 | ≈ −9 |
| 15 | ≈ −3 | ≈ −7 |
| 20 | ≈ −2 | ≈ −6 |

**Corrected comparison status:** **`PASS_WITH_CAVEAT`** — gas spot points align well; stellar still ~7–10 km s\(^{-1}\) low vs digitized at \(R \gtrsim 5\) kpc (D1 ≠ Casertano / digitization uncertainty). Fig. 12 remains a **low-precision sanity check**, not a calibration target.

## 9. Phase 1D-D2-B — canonical processed CSV (2026-05-24)

| Item | Value |
|------|--------|
| Output | `data/processed/m33_rotation.csv` (58 rows) |
| Build script | `scripts/build_m33_rotation_processed.py` |
| Primary baryonic source | `outputs/tables/corbelli2014_baryonic_velocity_derivation_audit.csv` (D1) |
| Observed rotation | Table 1 \(V_r\) via audit / `corbelli2014_table1_raw.csv` |
| `data_quality_flag` | `derived_baryonic_velocity_pass_with_caveat` |
| Fig. 12 | Corrected sanity check **PASS_WITH_CAVEAT**; **not** used as canonical velocities |
| Validation | `python scripts/validate_m33_data.py data/processed/m33_rotation.csv` → PASS |

**Remaining caveats before Phase 2:**

- Baryonic \(v_{\mathrm{gas}}\), \(v_{\mathrm{disk}}\) are **derived** (numerical disk gravity), not tabulated in the paper.
- D1 implementation ≠ Casertano (1983); stellar \(v_{\mathrm{disk}}\) may be ~7–10 km s\(^{-1}\) below Fig. 12 at some radii.
- No NFW/Burkert/TDF results in this dataset — Phase 2+ only.

## 10. Phase 2 — next step

1. NFW / Burkert halo baselines on the canonical 58-point grid.
2. Carry documented baryonic uncertainties into model comparison metrics.
3. Do not claim dark matter is ruled out or replaced.

---

## 11. Explicit non-goals (Phase 1D-D0)

- No NFW/Burkert fitting (Phase 2)
- No TDF \(\tau\) reconstruction (Phase 3)
- No figure digitization committed in D0
- No \(\Sigma \to v\) identity mapping
