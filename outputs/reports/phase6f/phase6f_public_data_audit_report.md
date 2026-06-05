# Phase 6F public M33 data acquisition audit

- Audit date (registry): `2026-05-23`
- Prepared by: `phase6f-public-data-acquisition-audit`
- Candidates catalogued: `15`
- Tier A: `4` | Tier B: `9` | Tier C: `2`

**Claim control:** Tier B products are **not** exact Corbelli 2014 primary maps. They cannot PASS G1/G2 Corbelli gates. Strict Corbelli scientific Phase 6F remains blocked.

## Exact Corbelli 2014 primary FITS (Tier A)

- Direct public Corbelli primary FITS found: **`False`**
- Notes: No Tier A Corbelli 2014 primary HI or BVIgi stellar FITS identified as direct public download. Table-only / author-request routes remain.

## Recommended fastest Tier B public pilot path

1. **HI:** LGLBS HI Data Release v1.0 (CANFAR) — wide-field 21 cm products for M33 (login required; not Corbelli reduction).
2. **Stellar proxy:** Spitzer S4G or LVL IRAC 3.6 + 4.5 µm mosaics (IRSA) → derive M_* surface density via documented M/L prescription (Querejeta/Meidt-style).
3. **H2/CO:** IRAM LP006 CO(2-1) integrated map / cube (`https://www.iram.fr/ILPA/LP006/`).
4. **Future pilot gates P1–P6** (documented only; not active in strict Corbelli pipeline).

## Candidate summary

| id | tier | product | download_status | Corbelli G1/G2? | public pilot? |
|----|------|---------|-----------------|-----------------|---------------|
| corbelli2014_aa_publisher_table1 | Tier_A | hi_stellar_1d_table | table_only | False | False |
| corbelli2014_vizier_catalog | Tier_A | hi_stellar_catalog | table_only | False | False |
| corbelli2014_primary_hi_author_request | Tier_A | hi_surface_density_2d | not_public_direct | True | False |
| corbelli2014_primary_stellar_author_request | Tier_A | stellar_mass_surface_density_2d | not_public_direct | True | False |
| koch2018_mnras_hi_scripts | Tier_B | hi_cube_moment_maps | rebuild_required | False | True |
| koch2018_canfar_archive | Tier_B | hi_cube_archive | login_required | False | True |
| lglbs_hi_v1_canfar | Tier_B | hi_wide_field_21cm | login_required | False | True |
| lockman2012_gbt_hi_short_spacing | Tier_B | hi_gbt_cube | archive_query | False | True |
| spitzer_s4g_irac_m33 | Tier_B | stellar_mass_proxy_irac | direct_download | False | True |
| spitzer_lvl_irac_m33 | Tier_B | stellar_mass_proxy_irac | direct_download | False | True |
| iram_lp006_co21_m33 | Tier_B | h2_co21_map | direct_download | False | True |
| herschel_herm33es_dust | Tier_B | dust_column_proxy | archive_query | False | True |
| nrao_archive_m33_vla | Tier_B | hi_raw_calibrated | login_required | False | True |
| gratier2010_vla_hi_reference | Tier_C | hi_moment_reference | direct_download | False | False |
| synthetic_phase6f_fixtures | Tier_C | synthetic_test_maps | internal | False | False |

## Future public pilot gates (diagnostic only; not active)

| Gate | Description |
|------|-------------|
| P1_public_hi_map_available | Public HI moment map or cube staged |
| P2_public_stellar_mass_proxy_available | IRAC-derived stellar mass proxy map |
| P3_public_h2_or_co_available | CO(2-1) or H2 proxy map staged |
| P4_public_wcs_metadata_available | WCS/units verified on Tier B products |
| P5_public_license_and_citation_documented | License + citations recorded |
| P6_public_reprojection_ready | Validated reprojection for Tier B grid |

See `docs/phase6f_data_tiers.md` and `docs/phase6f_public_pilot_limitations.md`.
