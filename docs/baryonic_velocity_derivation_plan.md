# Baryonic velocity derivation plan (Phase 1D-D0)

Audit and strategy for populating `v_gas_kms`, `v_disk_kms`, and `v_bulge_kms` in `data/processed/m33_rotation.csv` from Corbelli et al. (2014) inputs **without** mapping surface densities directly into velocity columns.

**Status:** Phase 1D-D0 — planning only (no baryonic velocity numbers committed yet).  
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
4. **Casertano (1983)** for both components with §6 vertical thickness rules.
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

## 7. Phase 1D-D1 — next implementation step

1. Add **`scripts/derive_corbelli2014_baryonic_velocities.py`** (or `src/tdf_m33/data/baryonic_corbelli2014.py`) that:
   - Loads `corbelli2014_table1_raw.csv`
   - Builds \(\Sigma_{\mathrm{gas}}(R)\) with H\(_2\) + He per Sect. 2.2
   - Computes \(v_{\mathrm{gas}}(R)\), \(v_{\mathrm{disk}}(R)\) via Casertano (1983) with §6 \(h_z\) laws
   - Writes interim audit table + proposed `m33_rotation.csv` columns (no commit until validated)
2. Add **`tests/test_baryonic_derivation_corbelli2014.py`** with algebraic checks and first/last row spot checks on \(v_{\mathrm{obs}}\) only (from existing raw CSV).
3. Optional: digitize Fig. 12 at 5 radii for Option B cross-check (document tool and uncertainty).
4. Update `docs/extraction_log.md` and manifest `acquisition_status` → `processed` only after validation PASS.

**Do not create `m33_rotation.csv` in D1 until derivation tests and Fig. 12 spot-check (or documented waiver) pass.**

---

## 8. Explicit non-goals (Phase 1D-D0)

- No NFW/Burkert fitting (Phase 2)
- No TDF \(\tau\) reconstruction (Phase 3)
- No figure digitization committed in D0
- No \(\Sigma \to v\) identity mapping
