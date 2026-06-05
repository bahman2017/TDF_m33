# Phase 6F — Primary data receipt protocol

**Purpose:** Standard operating procedure for receiving, verifying, and documenting Corbelli et al. 2014 primary 2D maps before any scientific Phase 6F τ-map run.

**Claim control:** This protocol does **not** authorize a scientific τ-map reconstruction. Strict mode remains blocked until gates G1, G2, G3, G4, G5, G7, and **G8** all pass.

---

## 1. Target directory layout

Place received files **only** under these paths (create subdirectories as needed; do not rename products without updating the source registry):

| Path | Product |
|------|---------|
| `data/raw/phase6f/primary/corbelli2014_hi/` | VLA+GBT HI surface-density map (FITS) |
| `data/raw/phase6f/primary/corbelli2014_stellar_mass/` | BVIgi stellar surface-density or mass map (FITS) |
| `data/raw/phase6f/primary/corbelli2014_velocity_field/` | 2D HI velocity field (FITS), if provided |
| `data/raw/phase6f/primary/corbelli2014_uncertainty_masks/` | Noise, uncertainty, or mask maps (FITS) |

Supporting metadata (not FITS):

- Update `data/raw/phase6f/manifest/phase6f_source_registry.yaml` **before** scientific use.
- Record license, access, and citation notes in `docs/extraction_log.md`.
- See `docs/phase6f_corbelli_author_request_package.md` for the author-request checklist.

---

## 2. Immutability rule

**Raw primary FITS files must never be overwritten in place.**

- Copy author-supplied files once into the target directory with original filenames preserved when possible.
- If a corrected file replaces an earlier version, **retire** the old file (move to `data/raw/phase6f/primary/_superseded/` with dated note) rather than overwriting.
- Scripts must be read-only on FITS content (`validate_phase6f_primary_maps.py`, gate checker).

---

## 3. Checksum workflow

After each receipt or file addition:

```bash
python scripts/update_phase6f_primary_checksums.py
cd data/raw/phase6f/primary && shasum -a 256 -c CHECKSUMS.sha256
```

- Every primary FITS file must appear in `data/raw/phase6f/primary/CHECKSUMS.sha256`.
- Also update root `data/raw/phase6f/CHECKSUMS.sha256` if geometry or manifest files change.

---

## 4. Validation workflow

```bash
python scripts/validate_phase6f_primary_maps.py
python scripts/run_phase6f_tau_map_gates.py
```

Review:

- `outputs/tables/phase6f/phase6f_primary_data_inventory.csv`
- `outputs/reports/phase6f/phase6f_primary_data_validation_report.md`
- `outputs/reports/phase6f/phase6f_tau_map_gate_report.md`

Required header/metadata checks (via validation script):

- WCS present (`has_wcs`)
- `BUNIT` documented
- Beam keywords (`BMAJ`, `BMIN`) when applicable
- Pixel scale (`CDELT1` or documented alternative)

---

## 5. Source registry and provenance (G7)

Before marking primary data ready for scientific pipeline review:

1. Set `acquisition_status` and file paths in `phase6f_source_registry.yaml`.
2. Record author email / archive URL / date received in `docs/extraction_log.md`.
3. Document license terms and citation requirements in `docs/phase6f_dataset_access_notes.md`.
4. Confirm Gratier 2010 reference FITS are **not** substituted for Corbelli 2014 primary HI (G1).

---

## 6. Scientific run prohibition

**No scientific τ-map run is allowed until all of the following gates pass:**

| Gate | Requirement |
|------|-------------|
| G1 | Primary Corbelli VLA+GBT HI map present |
| G2 | Primary BVIgi stellar map present |
| G3 | Tilted-ring geometry CSV valid |
| G4 | WCS/grid metadata verified on primary maps |
| G5 | Units documented and header-consistent |
| G7 | Provenance, license, citations recorded |
| G8 | **Validated** WCS-to-disk-plane reprojection implemented and tested |

G6 (uncertainty/masks) is diagnostic but strongly recommended before publication.

`python scripts/build_phase6f_nonspherical_tau_map.py` (strict) must continue to exit with `BLOCKED_PENDING_PRIMARY_CORBELLI_MAPS` until the above pass.

Reference-proxy mode (`--allow-reference-proxy`) remains `REFERENCE_ONLY_NOT_FOR_SCIENTIFIC_CLAIMS`.

---

## 7. Post-receipt checklist

- [ ] Files copied to correct `primary/` subdirectory
- [ ] No raw FITS overwritten
- [ ] SHA-256 recorded (`update_phase6f_primary_checksums.py`)
- [ ] Source registry updated
- [ ] License/citation logged
- [ ] Validation inventory generated
- [ ] Gate report reviewed (G1–G8)
- [ ] Reprojection design PR merged before attempting G8 PASS
- [ ] No scientific τ-map claimed in docs or outputs until all required gates PASS

---

## Related documents

- `docs/phase6f_primary_data_requirements.md`
- `docs/phase6f_corbelli_author_request_package.md`
- `docs/corbelli2014_author_request_email.md`
- `docs/phase6f_validated_reprojection_design.md`
- `docs/phase6f_data_provenance_checklist.md`
