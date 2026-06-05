# Phase 6F data gate report notes

Documentation for gate G6 (mask / uncertainty weighting).

## Primary stack (when acquired)

- HI noise / rms maps should live alongside primary FITS under `data/raw/phase6f/primary/corbelli2014_hi/`.
- Stellar mass uncertainty: use published PDF width (~0.06–0.1 dex) or author-provided weight map.
- Document weighting in `docs/data_sources.md` when maps are ingested.

## Reference-only mode

- Gratier `M33_HI_12sec-noise.fits` may inform reference weights only.
- Reference weights must not be used for scientific τ-map claims.

## Current status

Primary Corbelli maps absent — G6 remains FAIL until primary HI and documented weighting exist.
