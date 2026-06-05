# Phase 6F data gate report notes

Documentation for Phase 6F data gates.

## Required for scientific_ready

G1, G2, G3, G4, G5, G7, **G8** must all be **PASS**.

## G6 — diagnostic (mask / uncertainty)

- **Does not block** `scientific_ready` but status is always shown in gate reports.
- HI noise / rms maps should live alongside primary FITS under `data/raw/phase6f/primary/corbelli2014_hi/` when acquired.
- Current status on main repo: **FAIL** (no primary HI).

## G8 — primary map reprojection (alignment)

**PASS** only when:

1. Primary HI and stellar FITS are present (G1, G2),
2. WCS or documented pixel grid metadata exists (G4),
3. A **validated** reprojection path from primary FITS grid to the M33 disk-plane analysis grid is implemented and tested.

**Current status:** **FAIL**. Only `PLACEHOLDER_NOT_SCIENTIFIC_WCS_REPROJECTION` (scipy.ndimage.zoom) exists. Scientific mode raises `RuntimeError` if attempted without validated reprojection.

Config: `reprojection.allow_placeholder_reprojection: false` (default).

## Blocking summary

Phase 6F scientific τ-map reconstruction is blocked because:

1. Primary Corbelli 2014 maps are missing, **and**
2. Validated WCS/disk-plane reprojection is not yet implemented.

Even after primary maps arrive, G8 must pass before any scientific run.

## Reference-only mode

- Gratier reference FITS may use placeholder zoom for smoke tests only.
- All reference outputs must carry `REFERENCE_ONLY_NOT_FOR_SCIENTIFIC_CLAIMS`.
