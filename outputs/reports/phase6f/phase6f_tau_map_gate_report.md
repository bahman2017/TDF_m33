# Phase 6F tau-map data gate report

**scientific_ready:** `False`
**reference_only:** `False`

**blocked_message:** `BLOCKED_PENDING_PRIMARY_CORBELLI_MAPS`

## Gates

- **G1_primary_hi_surface_density_map**: `FAIL` — No primary Corbelli 2014 VLA+GBT HI map in data/raw/phase6f/primary/corbelli2014_hi. Gratier 2010 reference FITS present but do NOT satisfy G1.
- **G2_primary_stellar_surface_density_or_mass_map**: `FAIL` — No Corbelli 2014 BVIgi stellar map in data/raw/phase6f/primary/corbelli2014_stellar_mass.
- **G3_disk_geometry**: `PASS` — Parsed tilted-ring geometry (12 rings).
- **G4_wcs_or_grid_metadata**: `FAIL` — WCS/grid metadata cannot be verified without primary maps.
- **G5_units_documented**: `PARTIAL` — Unit documentation exists but primary maps not present to verify headers.
- **G6_mask_or_uncertainty**: `FAIL` — No primary HI map; uncertainty/mask rules not applicable.
- **G7_provenance_and_license**: `PASS` — Source registry, access notes, and citations documented.

## Claim control

Phase 6F-impl scientific tau-map reconstruction requires primary Corbelli 2014 VLA+GBT HI and BVIgi stellar maps. Gratier 2010 reference FITS do not satisfy G1.

No dark-matter-disproof or lensing-confirmation claim is made by this report.
