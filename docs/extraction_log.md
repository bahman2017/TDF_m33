# M33 data extraction log

Chronological record of official source acquisition and table extraction audits.

## 1. Phase 1C status

**Phase:** 1C — official source acquisition and raw Table 1 extraction audit  
**Date:** 2026-05-23 (repository local audit)  
**Outcome:** Raw directory structure, active manifest, raw Table 1 template, and audit tooling in place. **No model-ready** `data/processed/m33_rotation.csv`. **No fabricated numerical rows.**

---

## 2. Source files attempted

| source_id | Action | Result |
|-----------|--------|--------|
| `corbelli_et_al_2014` | Automated fetch via `https://doi.org/10.1051/0004-6361/201322790` | DOI landing HTML saved locally (not committed; see downloads/) |
| `corbelli_salucci_2000` | Not attempted in automation | Remains `located` |
| `lopez_fune_salucci_corbelli_2017` | Not attempted in automation | Remains `located` |

---

## 3. Download status

| Artifact | Path (local) | Committed to git | Notes |
|----------|--------------|------------------|-------|
| DOI redirect HTML | `data/raw/downloads/corbelli2014_aa22790_doi_redirect.html` | No (gitignored) | Publisher landing page, **not** the A&A PDF or Table 1 |
| A&A PDF | — | — | **Manual acquisition required** (institutional access or author copy) |
| Machine-readable Table 1 | — | — | **Not yet extracted** |

### Manual acquisition (if automation insufficient)

1. Open [doi.org/10.1051/0004-6361/201322790](https://doi.org/10.1051/0004-6361/201322790) or the A&A journal page.
2. Download the **official PDF** from the publisher (not third-party figure hosts).
3. Save as `data/raw/downloads/corbelli2014_aa22790.pdf`.
4. Run `sha256sum` (or project `sha256_file`) and write `corbelli2014_aa22790.pdf.sha256`.
5. Update `data/raw/sources_manifest.yaml` → `corbelli_et_al_2014.acquisition_status: downloaded`.
6. Add a row to this log with date and checksum.

---

## 4. Checksum status

| File | SHA-256 | Recorded |
|------|---------|----------|
| `corbelli2014_aa22790_doi_redirect.html` | `4dca28603c88e7a7501065c61135943f1b747e70319673950453252b617fbd69` | Local audit 2026-05-23; companion `.sha256` in downloads/ (gitignored) |

> This file is the DOI publisher **landing page HTML**, not the A&A PDF. Do not treat as table extraction source.

---

## 5. Table 1 extraction status (Corbelli et al. 2014)

| Item | Status |
|------|--------|
| Raw template CSV | Created: `data/raw/extracted/corbelli2014_table1_raw_template.csv` (headers only) |
| Rows extracted | **None** (by design in Phase 1C) |
| Column audit vs paper | **Pending** — requires official PDF/table access |

### Expected raw/interim columns (template)

`source_id`, `raw_table_id`, `row_id`, `r_kpc`, `v_rot_kms`, `v_err_kms`, `sigma_hi`, `sigma_h2`, `sigma_gas`, `sigma_star`, `raw_notes`, `extraction_method`, `reference`

If the published table uses different labels (e.g. \(V_{\mathrm{rot}}\), \(\Sigma_{\mathrm{HI}}\), arcsec), document mappings here before filling rows.

---

## 6. Table 1 content audit (literature expectation — verify against PDF)

Based on the published Corbelli et al. (2014) A&A analysis of M33 baryons and dynamics, **verify on the official table** before extraction:

| Quantity | Expected in Table 1 / paper? | Maps to processed schema |
|----------|------------------------------|---------------------------|
| Observed rotation curve \(V_{\mathrm{rot}}(R)\) | **Likely yes** (tilted-ring / model curve) | `v_obs_kms` |
| Velocity uncertainty | **May be partial** — check columns | `v_err_kms` |
| HI / gas surface density \(\Sigma_{\mathrm{HI}}\), \(\Sigma_{\mathrm{gas}}\) | **Likely yes** | `sigma_gas` (raw), not `v_gas_kms` |
| Stellar surface density \(\Sigma_\*\) | **Likely yes** | `sigma_star` (raw), not `v_disk_kms` |
| Baryonic velocity components \(v_{\mathrm{gas}}\), \(v_{\mathrm{disk}}\) | **Often not tabulated directly** — may require mass-model integration | `v_gas_kms`, `v_disk_kms` |

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
