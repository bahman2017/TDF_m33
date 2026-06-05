# Phase 6F — Corbelli 2014 author request package

Checklist and supporting materials for requesting primary M33 baryonic maps from the Corbelli et al. 2014 authors.

**Email draft:** `docs/corbelli2014_author_request_email.md`

---

## Request summary

| Product | Target directory | Gate |
|---------|------------------|------|
| VLA+GBT HI surface-density map | `data/raw/phase6f/primary/corbelli2014_hi/` | G1 |
| BVIgi stellar Σ or M_* map | `data/raw/phase6f/primary/corbelli2014_stellar_mass/` | G2 |
| 2D HI velocity field (if available) | `data/raw/phase6f/primary/corbelli2014_velocity_field/` | G4 support |
| Uncertainty / mask maps | `data/raw/phase6f/primary/corbelli2014_uncertainty_masks/` | G6 |

---

## Required metadata to request

Ask authors to confirm or supply:

1. **FITS format** with full WCS (RA/Dec or galactic; CD matrix; reference pixel).
2. **Units** (`BUNIT`): e.g. M_⊙ pc⁻² for surface density; clarify if mass vs luminosity-derived.
3. **Beam** (`BMAJ`, `BMIN`, `BPA`) and native pixel scale.
4. **Calibration notes:** flux scale, H i optically-thin assumption, He correction, stellar M/L (BVIgi).
5. **Masks / noise:** companion FITS or weight maps used in dynamical analysis.
6. **Geometry assumptions:** distance (840 kpc), representative i and PA if global values documented.
7. **Public archive links** if files are already hosted (CDS, author webpage, collaboration share).

---

## What we will **not** claim

Include in correspondence (see email draft):

- M33 is a **reproducible test case** for evaluating whether missing acceleration normally attributed to dark matter can be represented as a smooth τ-geometry field.
- The project does **not** claim dark matter is disproven.
- Requested maps are for **reproducible computational validation** under documented data gates.
- Gratier et al. 2010 VLA-only reference FITS already in the repository are **insufficient** for G1 (no GBT short spacing).

---

## After files are received

Follow `docs/phase6f_primary_data_receipt_protocol.md`:

1. Copy FITS to target directories (no overwrite).
2. Run `python scripts/update_phase6f_primary_checksums.py`.
3. Run `python scripts/validate_phase6f_primary_maps.py`.
4. Update `data/raw/phase6f/manifest/phase6f_source_registry.yaml`.
5. Log receipt in `docs/extraction_log.md`.
6. Re-run gate checker — expect G1/G2 to move toward PASS; **G8 remains FAIL** until validated reprojection is implemented.

---

## Primary contacts (from Corbelli et al. 2014, A&A 572, A23)

- **Elena Corbelli** — INAF Osservatorio Astrofisico di Arcetri
- **David A. Thilker** — Johns Hopkins University

Verify current email addresses from the published paper before sending.

---

## Bibliography (for citation in request)

- Corbelli, E., Thilker, D. A., Zibetti, S., Giovanardi, C., & Salucci, P. 2014, A&A, 572, A23
- DOI: [10.1051/0004-6361/201424033](https://doi.org/10.1051/0004-6361/201424033)
- arXiv: [1409.2665](https://arxiv.org/abs/1409.2665)
