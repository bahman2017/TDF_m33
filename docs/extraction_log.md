# M33 data extraction log

Chronological record of official source acquisition and table extraction audits.

## 1. Phase 1C status

**Phase:** 1C — official source acquisition and raw Table 1 extraction audit  
**Date:** 2026-05-23 (repository local audit)  
**Outcome:** Raw directory structure, active manifest, raw Table 1 template, and audit tooling in place. **No model-ready** `data/processed/m33_rotation.csv`. **No fabricated numerical rows.**

### Metadata correction (2026-05-24)

An earlier audit used an **incorrect DOI** (`10.1051/0004-6361/201322790`) and filename stem `aa22790` for the primary Corbelli et al. 2014 M33 paper. The correct bibliographic record is:

| Field | Value |
|-------|--------|
| Title | Dynamical signatures of a ΛCDM-halo and the distribution of the baryons in M33 |
| Journal | Astronomy & Astrophysics **572**, A23 |
| DOI | [10.1051/0004-6361/201424033](https://doi.org/10.1051/0004-6361/201424033) |
| A&A manuscript ID | `aa24033-14` |
| Planned local PDF | `data/raw/downloads/corbelli2014_aa24033_14.pdf` |

Any local files named `corbelli2014_aa22790*` from the wrong DOI fetch should be **discarded** and not used for extraction.

### Phase 1D-A acquisition (2026-05-24)

| Field | Value |
|-------|--------|
| `source_id` | `corbelli_et_al_2014` |
| Title | Dynamical signatures of a ΛCDM-halo and the distribution of the baryons in M33 |
| DOI | `10.1051/0004-6361/201424033` |
| Local file | `data/raw/downloads/corbelli2014_aa24033_14.pdf` |
| Checksum file | `data/raw/downloads/corbelli2014_aa24033_14.pdf.sha256` |
| SHA-256 | `c1d4db5c8c5902cc943533283fcec1700c85655745af56844137faffe4dfbd40` |
| Note | Official A&A PDF acquired and checksum recorded; **no numerical table extraction yet**. |

---

## 2. Source files attempted

| source_id | Action | Result |
|-----------|--------|--------|
| `corbelli_et_al_2014` | Automated fetch via wrong DOI `10.1051/0004-6361/201322790` (pre-2026-05-24) | Obsolete landing HTML only — **not** the M33 paper; see metadata correction above |
| `corbelli_salucci_2000` | Not attempted in automation | Remains `located` |
| `lopez_fune_salucci_corbelli_2017` | arXiv PDF `1611.01409` (2026-05-24) | **documented** — see Phase 5B-C below |

---

## 3. Download status

| Artifact | Path (local) | Committed to git | Notes |
|----------|--------------|------------------|-------|
| Obsolete DOI redirect HTML (wrong DOI) | `data/raw/downloads/corbelli2014_aa22790_doi_redirect.html` | No (gitignored) | **Discard if present** — from incorrect DOI `201322790`, not the M33 paper |
| A&A PDF | `data/raw/downloads/corbelli2014_aa24033_14.pdf` | No (gitignored) | **Acquired 2026-05-24** — official `aa24033-14.pdf`; SHA-256 recorded |
| Machine-readable Table 1 | — | — | **Not yet extracted** |

### Manual acquisition (if automation insufficient)

1. Open [doi.org/10.1051/0004-6361/201424033](https://doi.org/10.1051/0004-6361/201424033) or the [A&A article page](https://www.aanda.org/articles/aa/abs/2014/12/aa24033-14/aa24033-14.html).
2. Download the **official PDF** from the publisher (manuscript `aa24033-14.pdf`; not third-party mirrors).
3. Save as `data/raw/downloads/corbelli2014_aa24033_14.pdf`.
4. Run `sha256sum` (or project `sha256_file`) and write `corbelli2014_aa24033_14.pdf.sha256`.
5. Update `data/raw/sources_manifest.yaml` → `corbelli_et_al_2014.acquisition_status: downloaded`.
6. Add a row to this log with date and checksum.

---

## 4. Checksum status

| File | SHA-256 | Recorded |
|------|---------|----------|
| `corbelli2014_aa22790_doi_redirect.html` (obsolete) | `4dca28603c88e7a7501065c61135943f1b747e70319673950453252b617fbd69` | Wrong-DOI fetch 2026-05-23 — **do not use**; delete if present locally |
| `corbelli2014_aa24033_14.pdf` | `c1d4db5c8c5902cc943533283fcec1700c85655745af56844137faffe4dfbd40` | Phase 1D-A 2026-05-24; sidecar `corbelli2014_aa24033_14.pdf.sha256` (gitignored) |

> The `aa22790` artifact is from an incorrect DOI, not the Corbelli et al. 2014 M33 paper. Record checksums only for the official `corbelli2014_aa24033_14.pdf`.

---

## 5. Table 1 extraction status (Corbelli et al. 2014)

| Item | Status |
|------|--------|
| Raw template CSV | Created: `data/raw/extracted/corbelli2014_table1_raw_template.csv` (headers only) |
| Raw extracted CSV | **Complete** — `data/raw/extracted/corbelli2014_table1_raw.csv` (Phase 1D-C, 2026-05-24) |
| Rows extracted | **58** — matches PDF Table 1 |
| Column audit vs paper | **Complete** — Phase 1D-B (2026-05-24); see §5.1 |
| Published row count (PDF) | **58** radial bins (\(R \approx 0.24\)–\(22.72\) kpc) |
| Model-ready CSV | **Not created** — no `m33_rotation.csv` |

### 5.1 Phase 1D-B — Table 1 column audit (2026-05-24)

**Source PDF:** `data/raw/downloads/corbelli2014_aa24033_14.pdf` (SHA-256 recorded in §4).

| Audit field | Value |
|-------------|--------|
| Table title | Rotation curve, atomic gas, and stellar mass surface densities across the M 33 disk. |
| PDF location | **Page 13 of 18** in the downloaded PDF (`A23, page 13 of 18` footer); PyMuPDF page index **12** (0-based). |
| In-text reference | §6.2 introduces the table; §5 notes the adopted rotation curve is given in Table 1. |
| `raw_table_id` (planned) | `corbelli2014_table1` |

#### Published columns and units (confirmed)

| Published column | Unit | Notes from paper |
|------------------|------|------------------|
| \(R\) | kpc | Galactocentric radius of tilted-ring bins |
| \(V_r\) | km s\(^{-1}\) | Adopted rotation velocity (tilted-ring / deconvolution pipeline) |
| \(\sigma_V\) | km s\(^{-1}\) | Rotation-curve uncertainty (dispersion, deconvolution, finite-disk correction; not a lone statistical error) |
| \(\Sigma_{\mathrm{HI}}\) | M\(_\odot\) pc\(^{-2}\) | Neutral atomic gas surface density perpendicular to the disk |
| \(\Sigma_\*\) | M\(_\odot\) pc\(^{-2}\) | Modelled stellar mass surface density (BVIgi map; “most likely” values per §6 text) |

**Not present in Table 1:** \(\Sigma_{\mathrm{H_2}}\), total gas \(\Sigma_{\mathrm{gas}}\), \(v_{\mathrm{gas}}\), \(v_{\mathrm{disk}}\), \(v_{\mathrm{bulge}}\), inclination, distance.

#### Mapping: published column → raw template column

| Published | Unit | Raw template column | Status |
|-----------|------|---------------------|--------|
| \(R\) | kpc | `r_kpc` | Direct |
| \(V_r\) | km s\(^{-1}\) | `v_rot_kms` | Direct |
| \(\sigma_V\) | km s\(^{-1}\) | `v_err_kms` | Direct (store as rotation-curve uncertainty; document semantics in `raw_notes`) |
| \(\Sigma_{\mathrm{HI}}\) | M\(_\odot\) pc\(^{-2}\) | `sigma_hi` | Direct |
| \(\Sigma_\*\) | M\(_\odot\) pc\(^{-2}\) | `sigma_star` | Direct |
| — | — | `sigma_h2` | **No published column** — leave empty; H\(_2\)/helium enter total baryonic \(\Sigma\) in text/Fig. 10, not Table 1 |
| — | — | `sigma_gas` | **No published column** — leave empty unless later derived (e.g. HI + He) in Phase 1D+ |
| (provenance) | — | `source_id`, `raw_table_id`, `row_id`, `raw_notes`, `extraction_method`, `reference` | Fill on extraction |

#### Mapping: raw template → processed schema (Phase 1D+; not executed yet)

| Raw template | Processed (`m33_rotation.csv`) | Phase 1D-B note |
|--------------|-------------------------------|-----------------|
| `v_rot_kms` | `v_obs_kms` | After unit check only |
| `v_err_kms` | `v_err_kms` | From \(\sigma_V\); document in `notes` |
| `sigma_hi`, `sigma_star` | optional `sigma_gas`, `sigma_star` | **Not** `v_gas_kms` / `v_disk_kms` |
| — | `v_gas_kms`, `v_disk_kms` | **Gap:** require mass-model / dynamical decomposition (paper Figs. 12–13), not Table 1 |

#### Explicit gaps and warnings

1. **Surface densities only:** Table 1 tabulates \(\Sigma_{\mathrm{HI}}\) and \(\Sigma_\*\), not circular-speed components \(v_{\mathrm{gas}}\) or \(v_{\mathrm{disk}}\).
2. **Do not alias densities to velocities:** \(\Sigma_{\mathrm{HI}}\) and \(\Sigma_\*\) must **not** be copied into `v_gas_kms` or `v_disk_kms` in `data/processed/m33_rotation.csv`.
3. **Template sufficiency:** Existing `corbelli2014_table1_raw_template.csv` headers are **sufficient**; optional `sigma_h2` / `sigma_gas` remain for interim fields not in Table 1 (empty unless derived later).
4. **Phase 1D-C complete:** `data/raw/extracted/corbelli2014_table1_raw.csv` created (see §5.2).

### 5.2 Phase 1D-C — Table 1 numerical extraction (2026-05-24)

| Field | Value |
|-------|--------|
| Output file | `data/raw/extracted/corbelli2014_table1_raw.csv` |
| Extraction method | `manual_from_pdf_table1` (reproducible via `scripts/extract_corbelli2014_table1_from_pdf.py` from official PDF) |
| Source PDF | `data/raw/downloads/corbelli2014_aa24033_14.pdf` (page 13 of 18) |
| Row count | **58** |
| `sigma_h2`, `sigma_gas` | Empty for all rows (not tabulated in Table 1) |
| Layer | **Raw/interim only** — not model-ready; no baryonic velocity components |

**Spot checks (first / last row vs PDF Table 1):**

| Row | \(R\) [kpc] | \(V_r\) [km s\(^{-1}\)] | \(\sigma_V\) | \(\Sigma_{\mathrm{HI}}\) | \(\Sigma_\*\) |
|-----|-------------|-------------------------|--------------|--------------------------|----------------|
| 1 | 0.24 | 37.3 | 6.2 | 7.12 | 316.59 |
| 58 | 22.72 | 119.6 | 13.4 | 0.07 | 0.13 |

**Validation:** `python scripts/validate_corbelli2014_table1_raw.py` (and `tests/test_corbelli2014_table1_raw.py`).

**Next step (Phase 2):** NFW/Burkert baselines on canonical processed grid; no TDF yet.

### Phase 1D-D2-B — canonical processed rotation CSV (2026-05-24)

| Field | Value |
|-------|--------|
| Output | `data/processed/m33_rotation.csv` (58 rows) |
| Build | `scripts/build_m33_rotation_processed.py` from D1 audit |
| Observed velocities | Table 1 \(V_r\), \(\sigma_V\) |
| Baryonic velocities | D1 audit (`axisymmetric_disk_gravity_exponential_vertical`) |
| Fig. 12 gate | PASS_WITH_CAVEAT (corrected labels); not used as canonical velocities |
| Manifest | `corbelli_et_al_2014.acquisition_status` → `processed` |
| Validation | `validate_m33_data.py` PASS |

### Phase 1D-D2-A — Fig. 12 baryonic sanity-check (2026-05-24)

| Field | Value |
|-------|--------|
| Spot-check CSV | `data/raw/extracted/corbelli2014_fig12_baryonic_spotcheck.csv` (5 radii: 1, 5, 10, 15, 20 kpc) |
| Method | `visual_from_pdf_fig12_bottom_panel_bvigi`; ±5 km s\(^{-1}\) uncertainty |
| Comparison | `outputs/tables/corbelli2014_baryonic_fig12_comparison.csv` |
| Figure | `outputs/figures/corbelli2014_baryonic_fig12_sanity_check.png` |
| Validation status | **REVIEW_REQUIRED** (later traced to likely label swap — see D2-A2) |
| Model-ready CSV | **Not created** |
| Script | `python scripts/compare_corbelli2014_baryonic_to_fig12.py` |

### Phase 1D-D2-A2 — Fig. 12 label audit (2026-05-24)

| Field | Value |
|-------|--------|
| Label audit | `outputs/tables/corbelli2014_fig12_label_audit.csv` |
| Verdict | **LIKELY_SWAPPED** — caption: red=gas, blue=stellar; D2-A assigned inner blue curve to gas |
| Original spot-check | Retained; **superseded** by corrected file for comparisons |
| Corrected spot-check | `data/raw/extracted/corbelli2014_fig12_baryonic_spotcheck_corrected.csv` |
| Corrected comparison | `outputs/tables/corbelli2014_baryonic_fig12_comparison_corrected.csv` |
| Corrected figure | `outputs/figures/corbelli2014_baryonic_fig12_sanity_check_corrected.png` |
| Validation status | **PASS_WITH_CAVEAT** (corrected labels; D1 still ≠ Casertano) |
| Model-ready CSV | **Not created** |
| Scripts | `audit_corbelli2014_fig12_labels.py`; `compare_corbelli2014_baryonic_to_fig12.py --corrected` |

### Phase 1D-D1 — baryonic velocity derivation audit (2026-05-24)

| Item | Outcome |
|------|---------|
| Method | Axisymmetric disk gravity + exponential vertical profile (`src/tdf_m33/models/disk_gravity.py`) |
| Interim table | `outputs/tables/corbelli2014_baryonic_velocity_derivation_audit.csv` (58 rows) |
| \(\Sigma_{\mathrm{H_2}}\) | \(10\,e^{-R/2.2}\) M\(_\odot\) pc\(^{-2}\); \(\Sigma_{\mathrm{gas}} = 1.33(\Sigma_{\mathrm{HI}}+\Sigma_{\mathrm{H_2}})\) |
| \(v_{\mathrm{bulge}}\) | 0 (documented) |
| Model-ready CSV | **Not created** |
| Validation | `scripts/validate_corbelli2014_baryonic_velocity_derivation.py` PASS |

### Phase 1D-D0 — baryonic velocity strategy audit (2026-05-24)

| Item | Outcome |
|------|---------|
| Planning doc | `docs/baryonic_velocity_derivation_plan.md` |
| Primary path | Option A — Casertano (1983) from Table 1 \(\Sigma_{\mathrm{HI}}\), \(\Sigma_\*\) + Sect. 2.2 H\(_2\)/He |
| Fallback | Option B — Fig. 12 digitization for validation only |
| Bulge | \(v_{\mathrm{bulge}} = 0\) justified (no supported bulge; §5) |
| Model-ready CSV | **Not created** |

### Expected raw/interim columns (template)

`source_id`, `raw_table_id`, `row_id`, `r_kpc`, `v_rot_kms`, `v_err_kms`, `sigma_hi`, `sigma_h2`, `sigma_gas`, `sigma_star`, `raw_notes`, `extraction_method`, `reference`

---

## 6. Table 1 content audit (confirmed against PDF, 2026-05-24)

Supersedes pre-PDF literature expectations. See §5.1 for column mapping.

| Quantity | In Table 1? | Raw / processed handling |
|----------|-------------|---------------------------|
| Adopted rotation \(V_r(R)\) | **Yes** | `v_rot_kms` → later `v_obs_kms` |
| Rotation uncertainty \(\sigma_V\) | **Yes** | `v_err_kms` |
| \(\Sigma_{\mathrm{HI}}\) | **Yes** | `sigma_hi` (raw only) |
| \(\Sigma_\*\) | **Yes** | `sigma_star` (raw only) |
| \(\Sigma_{\mathrm{H_2}}\), total \(\Sigma_{\mathrm{gas}}\) | **No** | Optional empty `sigma_h2` / `sigma_gas`; derive later if needed |
| Baryonic \(v_{\mathrm{gas}}\), \(v_{\mathrm{disk}}\) | **No** | Phase 1D+ decomposition; **not** from Table 1 |

---

## 7. Decision: Phase 1D required before model-ready CSV

**If Table 1 (or supplementary material) provides only surface densities and rotation speeds:**

- Store values in `data/raw/extracted/corbelli2014_table1_raw.csv` (future) with provenance columns.
- **Do not** copy \(\Sigma\) directly into `v_gas_kms` / `v_disk_kms` in `m33_rotation.csv`.
- **Phase 1D** must derive baryonic velocity components from documented mass models (or source explicit \(v_i\) columns if published), with uncertainties and transformation notes in `docs/data_sources.md`.

`configs/m33_default.yaml` sets `allow_creation_without_baryonic_velocity_components: false`.

---

## 8. No-data-fabrication statement

This repository **does not** invent M33 velocities, surface densities, or baryonic components. Phase 1C adds structure and audit tools only. Any row in a processed CSV must trace to an official table, documented transformation, and `source_id` in `data/raw/sources_manifest.yaml`.

---

## 9. Phase 5B-C — López Fune et al. 2017 (2026-05-24)

| Field | Value |
|-------|--------|
| `source_id` | `lopez_fune_salucci_corbelli_2017` |
| DOI | `10.1093/mnras/stx2742` |
| arXiv | `1611.01409` |
| Local PDF | `data/raw/downloads/lopez_fune_salucci_corbelli_2017_m33.pdf` |
| Checksum file | `data/raw/downloads/lopez_fune_salucci_corbelli_2017_m33.pdf.sha256` (tracked in git) |
| SHA-256 | `753c93a49ff56e4c60ea0eed8fe8c4e85ed9fb59880a4d2b11cc84968609d3b4` |
| Provenance | arXiv accepted manuscript (publisher OUP PDF optional) |
| Extraction plan | `docs/lopez_fune_2017_extraction_plan.md` |
| Numerical extraction | **Not performed** — figure digitization deferred to Phase 5C |
