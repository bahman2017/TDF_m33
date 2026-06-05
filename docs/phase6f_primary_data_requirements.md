# Phase 6F — Primary data requirements

Minimum products and metadata required before scientific non-spherical τ-map reconstruction.

**Status on main:** Primary Corbelli 2014 FITS **not acquired**. Scientific mode **blocked**.

---

## Required primary products

### G1 — HI surface density (mandatory)

- **Source:** Corbelli et al. 2014 combined **VLA + GBT** H i map used in dynamical modeling.
- **Location:** `data/raw/phase6f/primary/corbelli2014_hi/`
- **Format:** 2D FITS image or primary HDU with surface density in physical units.
- **Not acceptable:** Gratier et al. 2010 VLA-only moment maps (`reference/gratier2010_vla_hi_12sec/`).

### G2 — Stellar surface density or mass (mandatory)

- **Source:** Corbelli et al. 2014 BVIgi-derived stellar product (Fig. 2 / dynamical model).
- **Location:** `data/raw/phase6f/primary/corbelli2014_stellar_mass/`
- **Format:** 2D FITS with documented M/L or direct mass surface density.

### G3 — Disk geometry (present)

- **Location:** `data/raw/phase6f/geometry/corbelli2014_tilted_ring_geometry_model_shape.csv`
- **Columns:** `r_kpc`, `inclination_deg`, `position_angle_deg` (minimum).

### G4 — WCS / grid metadata (mandatory when G1/G2 present)

- Valid celestial WCS on primary FITS **or** documented pixel grid with explicit world-to-pixel mapping.
- Verified by `validate_phase6f_primary_maps.py` and gate G4.

### G5 — Units (mandatory when G1/G2 present)

- `BUNIT` header or equivalent sidecar documentation.
- Consistent with M_⊙ pc⁻² (or documented conversion path to baryonic source term J_τ).

### G7 — Provenance (mandatory)

- Entry in `phase6f_source_registry.yaml` with license and citation.
- Checksums in `data/raw/phase6f/primary/CHECKSUMS.sha256`.

### G8 — Validated reprojection (mandatory for scientific mode)

- Implemented WCS-to-disk-plane reprojection — **not** `scipy.ndimage.zoom` placeholder.
- Design: `docs/phase6f_validated_reprojection_design.md`.

---

## Optional but recommended

| Product | Location | Gate support |
|---------|----------|--------------|
| 2D HI velocity field | `primary/corbelli2014_velocity_field/` | Rotation consistency diagnostics |
| Noise / mask maps | `primary/corbelli2014_uncertainty_masks/` | G6 |

---

## Validation commands

```bash
python scripts/update_phase6f_primary_checksums.py
python scripts/validate_phase6f_primary_maps.py
python scripts/run_phase6f_tau_map_gates.py
```

---

## Scientific run criteria

`scientific_ready = true` requires **G1, G2, G3, G4, G5, G7, G8** all PASS.

Until then:

- Strict build exits with `BLOCKED_PENDING_PRIMARY_CORBELLI_MAPS`.
- Reference-proxy outputs are `REFERENCE_ONLY_NOT_FOR_SCIENTIFIC_CLAIMS`.

---

## Related documents

- `docs/phase6f_primary_data_receipt_protocol.md`
- `docs/phase6f_data_requirements_for_physical_tau_map.md`
- `docs/phase6f_source_manifest.md`
- `docs/phase6f_validated_reprojection_design.md`
