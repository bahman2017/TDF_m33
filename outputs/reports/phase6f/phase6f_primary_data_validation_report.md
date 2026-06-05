# Phase 6F primary data validation report

**Scope:** Inventory and FITS header inspection for Corbelli 2014 primary products.
**Not a scientific τ-map result.** Strict mode remains blocked until G1, G2, G3, G4, G5, G7, and G8 pass.

- Repository: paths relative to repository root
- Primary root exists: `True`
- FITS files found: `0`
- astropy available: `True`
- G1-ready (HI + WCS): `False`
- G2-ready (stellar): `False`

## Inventory

| product_type | filename | status | gate | WCS | BUNIT | checksum |
|--------------|----------|--------|------|-----|-------|----------|
| corbelli2014_hi | — | MISSING_DIRECTORY | G1_primary_hi_surface_density_map | — | — | — |
| corbelli2014_stellar_mass | — | MISSING_DIRECTORY | G2_primary_stellar_surface_density_or_mass_map | — | — | — |
| corbelli2014_velocity_field | — | MISSING_DIRECTORY | supplementary_velocity_field | — | — | — |
| corbelli2014_uncertainty_masks | — | MISSING_DIRECTORY | G6_mask_or_uncertainty | — | — | — |

## Gate implications (current run)

- **G1:** FAIL until validated HI FITS present under `data/raw/phase6f/primary/corbelli2014_hi/`.
- **G2:** FAIL until stellar FITS present under `data/raw/phase6f/primary/corbelli2014_stellar_mass/`.
- **G8:** FAIL until validated WCS-to-disk-plane reprojection is implemented (see `docs/phase6f_validated_reprojection_design.md`).

Reference-proxy Gratier 2010 FITS do **not** satisfy G1.
