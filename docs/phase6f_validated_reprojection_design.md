# Phase 6F — Validated WCS-to-disk-plane reprojection design

**Status:** Design scaffold only. `VALIDATED_WCS_REPROJECTION_AVAILABLE = False` in `src/tdf_m33/maps/reprojection.py`.

**Gate G8 must remain FAIL until this design is implemented and acceptance tests pass in a follow-up PR.**

---

## 1. Why placeholder zoom is not scientific

The current reference path uses `scipy.ndimage.zoom` (`PLACEHOLDER_NOT_SCIENTIFIC_WCS_REPROJECTION`):

- Ignores celestial WCS (RA/Dec), position angle, and disk inclination.
- Does not conserve flux or surface brightness per solid angle.
- Cannot align M33 center, major axis, or tilted-ring geometry to the disk-plane grid.
- Produces smoke-test arrays only; blocked in strict/scientific mode.

**G8 exists specifically to prevent this placeholder from becoming a scientific alignment method.**

---

## 2. Required reprojection pipeline

Target API (stubs in `reprojection.py`):

1. **`validate_wcs_metadata(fits_path)`** — parse FITS WCS; verify celestial axes, `BUNIT`, beam, pixel scale.
2. **`reproject_fits_to_disk_grid(...)`** — map sky-plane primary HDU onto Phase 6F disk-plane `(x, y)` grid [kpc].
3. **`compute_reprojection_validation_metrics(...)`** — flux conservation, radial profile consistency, center alignment.

### Step sequence

```
Primary FITS (sky WCS)
    → validate WCS + units
    → define sky target grid OR sample at disk-plane pixel sky positions
    → apply disk geometry (i(R), PA(R)) from geometry CSV
    → reproject/resample with flux-conserving method (e.g. astropy.reproject, custom area weighting)
    → disk-plane Σ maps on build_disk_grid() coordinates
    → validation metrics + diagnostic plots
```

---

## 3. Sky coordinate frame handling

- Read native WCS from primary FITS (`astropy.wcs.WCS`).
- Confirm coordinate frame (ICRS/FK5/galactic) and north/up convention.
- M33 center: use WCS reference pixel or published center; cross-check against geometry CSV inner ring.
- Convert disk-plane `(x_kpc, y_kpc)` to sky `(RA, Dec)` using:
  - Distance (default 840 kpc from project config),
  - Tilted-ring `inclination_deg(R)` and `position_angle_deg(R)` from `geometry.py`.

---

## 4. Disk inclination and position angle

- Use **Corbelli 2014 tilted-ring table** (`corbelli2014_tilted_ring_geometry_model_shape.csv`), not single global i/PA, when sampling outer disk.
- Interpolate i(R) and PA(R) onto each disk-plane radius bin.
- Document whether reprojection uses ring-averaged geometry per pixel or local R = sqrt(x²+y²).

---

## 5. Pixel area and flux conservation

- Surface-density maps (M_⊙ pc⁻²) require **area weighting** when regridding.
- Account for beam convolution: do not deconvolve unless uncertainty propagation is defined (G6).
- For integrated flux checks: compare azimuthally averaged Σ(R) before/after reprojection against Table 1 tolerances.
- Document handling of masked pixels (NaN propagation, zero vs exclude).

---

## 6. Unit conversion requirements

- Parse `BUNIT`; normalize to project internal units for J_τ source term.
- HI: confirm H+He scaling if map is H i-only.
- Stellar: confirm M/L(BVIgi) assumptions match paper; flag if map is luminosity not mass.
- Record conversion factors in reprojection metadata JSON sidecar.

---

## 7. Validation checks (acceptance suite)

| ID | Check | Criterion |
|----|-------|-----------|
| a | WCS present | `wcs.has_celestial` true on primary HDU |
| b | Center alignment | Sky center of mass within 1 beam of expected M33 center |
| c | Pixel scale documented | `CDELT` or CD matrix recorded in validation report |
| d | Flux / Σ conservation | Azimuthally integrated Σ(R) within tolerance vs pre-reprojection (e.g. ≤5% RMS beyond beam smoothing) |
| e | Radial profile consistency | Pre/post reprojection radial profiles correlated at r > 2 kpc |
| f | Geometry sanity plots | Disk-plane map major axis aligned with PA(R); inclination warp visible where expected |

Implement in `compute_reprojection_validation_metrics(...)` and dedicated test fixtures.

---

## 8. G8 PASS acceptance criteria (future PR)

Set `VALIDATED_WCS_REPROJECTION_AVAILABLE = True` **only when all** of:

1. G1 and G2 primary FITS present and pass `validate_wcs_metadata`.
2. `reproject_fits_to_disk_grid` implemented with flux-conserving method (not zoom).
3. Validation suite (§7) passes on both HI and stellar maps.
4. Unit tests cover round-trip center, flux integral, and radial profile checks.
5. Gate report documents `alignment_method: VALIDATED_WCS_DISK_PLANE_REPROJECTION`.
6. Placeholder zoom remains blocked in scientific mode.

**This PR does not satisfy any of the above implementation criteria.**

---

## 9. Related code and docs

- `src/tdf_m33/maps/geometry.py` — disk↔sky projection helpers
- `src/tdf_m33/maps/grid.py` — disk-plane grid definition
- `src/tdf_m33/maps/gates.py` — G8 gate checker
- `docs/phase6f_nonspherical_tau_map_engine.md`
