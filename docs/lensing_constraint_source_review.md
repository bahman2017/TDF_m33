# M33 lensing / deflection constraint source review (Phase 5B-B)

**Date:** 2026-05-24  
**Scope:** Source discovery and registration only. No observational comparison. No physical conversion of `normalized_proxy` deflection maps. No numerical limits copied into repository tables unless extracted from a cited source file in a later phase.

## Search strategy

1. **In-repo registry** — Start from `docs/data_sources.md`, `data/raw/sources_manifest.yaml`, and Phase 2 halo baselines already tied to M33 dynamics.
2. **Direct M33 weak lensing** — ADS/arXiv keyword searches: “M33” + “weak lensing”, “Triangulum” + “gravitational lensing”, “galaxy-galaxy lensing” + M33. Survey papers (COMBO-17, DES, SDSS) treat statistical samples at $z \sim 0.2$–0.7, not resolved Local Group spirals.
3. **Dynamical mass / rotation** — M33 rotation-curve and halo papers with published enclosed masses or density profiles (independent of τ reconstruction).
4. **Local Group / environment** — Companions, tides, and outer-disk perturbations as **context** or coarse upper-bound checks, not arcsec deflection.
5. **Stellar streams / satellites** — M31–M33 interaction literature; few M33-specific stream mass tables suitable for deflection comparison.

**Outcome:** No M33-specific weak-lensing mass map or deflection-angle catalog was identified for Phase 5C. Dynamical halo/rotation literature provides the strongest **candidate** constraints for enclosed-mass consistency at fixed radii (e.g. 23 kpc), not direct lensing of the τ-proxy field.

## Candidate sources

### 1. `corbelli_et_al_2014` (already in project)

| Field | Value |
|-------|--------|
| Citation | Corbelli et al. 2014, A&A 572, A23; DOI [10.1051/0004-6361/201424033](https://doi.org/10.1051/0004-6361/201424033) |
| Type | Dynamical mass + rotation (primary project data) |
| Physical calibration | **No** — same data branch as τ reconstruction |
| Upper-bound comparison | **No** — circular with Phase 3–5A inputs |
| Context only | **Yes** — geometry, baryonic model, NFW reference |
| Rejection reason for 5C | Not an independent observational check of lensing predictions |

### 2. `lopez_fune_salucci_corbelli_2017` (located)

| Field | Value |
|-------|--------|
| Citation | López Fune, Salucci & Corbelli 2017, MNRAS; DOI [10.1093/mnras/stx2742](https://doi.org/10.1093/mnras/stx2742); arXiv [1611.01409](https://arxiv.org/abs/1611.01409) |
| Type | Dynamical — NFW vs Burkert halo; dark-matter density vs radius |
| Physical calibration | **No** — does not link τ to deflection |
| Upper-bound comparison | **Yes (candidate)** — enclosed mass / halo slope at 0.24–22.72 kpc |
| Context only | **Yes** — cross-check Phase 2 NFW/Burkert baselines |
| Limitations | Halo-centric; not lensing; partial circularity with Corbelli 2014 |
| Phase 5B-C | PDF + checksum acquired; `docs/lopez_fune_2017_extraction_plan.md` |
| Phase 5C | **Candidate (selected)** — pending figure/table extraction to CSV |

### 3. `kam_et_al_2018_m33_hi_masses` (located)

| Field | Value |
|-------|--------|
| Citation | Kam et al. 2018, AJ 156, 14 (arXiv [1706.04248](https://arxiv.org/abs/1706.04248)); DOI [10.3847/1538-3881/aa79f3](https://doi.org/10.3847/1538-3881/aa79f3) |
| Type | Dynamical — hybrid Hα–H i rotation curve; NFW/MOND models |
| Physical calibration | **No** |
| Upper-bound comparison | **Yes (alternate candidate)** — reports total mass enclosed at 23 kpc in abstract (extract from paper in 5C, not copied here) |
| Context only | **Yes** — outer-disk warp, tidal environment |
| Limitations | Overlaps Corbelli et al. 2014 curve; baryonic fraction assumptions |
| Phase 5C | Alternate if López Fune tables unavailable |

### 4. `corbelli_salucci_2000` (located)

| Field | Value |
|-------|--------|
| Citation | Corbelli & Salucci 2000, MNRAS 311, 441; arXiv [astro-ph/9909252](https://arxiv.org/abs/astro-ph/9909252) |
| Type | Dynamical — extended H i rotation curve to 16 kpc |
| Physical calibration | **No** |
| Upper-bound comparison | **Marginal** — older curve; superseded by 2014/2018 |
| Context only | **Yes** |
| Rejection for 5C | Superseded; prefer 2014 or Kam et al. 2018 for same science case |

### 5. `mcconnachie_2012_local_group` (located)

| Field | Value |
|-------|--------|
| Citation | McConnachie 2012, AJ 144, 4; arXiv [1204.1562](https://arxiv.org/abs/1204.1562) |
| Type | Local Group compilation |
| Physical calibration | **No** |
| Upper-bound comparison | **No** — M33 numbers “for completeness only” |
| Context only | **Yes** — distance, environment |
| Rejection for 5C | Not M33-specific dynamical/lensing constraints |

### 6. `putman_et_al_2009_m33_tidal` (located)

| Field | Value |
|-------|--------|
| Citation | Putman et al. 2009 (M31–M33 H i tidal features); see McConnachie et al. 2010 for environment |
| Type | Tidal / outer-disk gas — upper-bound **context** |
| Physical calibration | **No** |
| Upper-bound comparison | **Context only** — outer potential perturbations, not mass at 23 kpc |
| Phase 5C | **No** — qualitative systematics for interpretation |

### 7. `combo17_weak_lensing_statistical` (rejected)

| Field | Value |
|-------|--------|
| Citation | Parker et al. 2007, MNRAS 380, 349 (COMBO-17 weak lensing); arXiv [astro-ph/0412615](https://arxiv.org/abs/astro-ph/0412615) |
| Type | Statistical weak lensing of field galaxies |
| Rejection | No M33 measurement; wrong redshift/population |

### 8. `m33_direct_weak_lensing_gap` (documented review)

| Field | Value |
|-------|--------|
| Type | Literature synthesis (this review) |
| acquisition_status | **documented** |
| Statement | No published M33-specific galaxy-scale weak-lensing mass map or deflection catalog was found in Phase 5B-B search suitable for direct comparison to sky-plane τ-gradient proxies. |
| Physical calibration | **No** |
| Upper-bound comparison | **No** — documents absence, not a numeric limit |
| Context only | **Yes** — justifies deferred lensing comparison and Phase 5B-A planning |

## Phase 5C readiness

| source_id | Ready for Phase 5C? | Role |
|-----------|---------------------|------|
| `lopez_fune_salucci_corbelli_2017` | **Candidate (selected)** | Dynamical enclosed-mass / halo profile upper-bound consistency at documented radii |
| `kam_et_al_2018_m33_hi_masses` | Alternate candidate | Same class; requires PDF/table extraction |
| `m33_direct_weak_lensing_gap` | N/A (context) | Explains why weak-lensing comparison is deferred |
| All others | No | Context, rejected, or circular |

**Comparison mode for 5C (planned):** `upper_bound_consistency` on dynamical mass metrics, **not** arcsec deflection, until physical calibration exists.

## Explicit non-actions (Phase 5B-B)

- No conversion of `normalized_proxy` to arcsec.
- No tuning of `alpha_tau_scale` or τ to match any constraint.
- No separate halo or lensing-only τ fit.
- No claim of lensing detection or dark-matter replacement.
