# Phase 6F — Data tiers (A / B / C)

Policy for M33 2D inputs to the non-spherical disk-plane τ-map engine.

---

## Tier A — Exact Corbelli 2014 primary (preferred)

**Products:**

- VLA+GBT HI surface-density map (Corbelli et al. 2014 reduction)
- BVIgi stellar surface-density / stellar mass map (pixel-SED)
- HI velocity field, uncertainty maps (if available)

**Gate mapping:** G1, G2, G4, G5, G6 (optional), G7, **G8** (after validated reprojection)

**Acquisition status (2026-05-23):** Author/archive request likely required. No direct public FITS URL confirmed.

**Rule:** Only Tier A products with verified provenance may PASS **G1** and **G2** Corbelli primary gates.

---

## Tier B — Public-data M33 τ-map pilot

**Purpose:** Faster reproducible pilot using **publicly downloadable** M33 maps when Tier A is unavailable.

**Products (examples):**

| Component | Example public source |
|-----------|----------------------|
| HI | LGLBS HI v1.0 (CANFAR); Koch et al. 2018 pipeline |
| Stellar proxy | Spitzer S4G / LVL IRAC 3.6 + 4.5 µm → M_* via M/L prescription |
| H2 / CO | IRAM LP006 CO(2-1) integrated map / cube |

**Gate mapping:** Future **P1–P6** public pilot gates (diagnostic track). **Does not replace G1/G2.**

| Gate | Description |
|------|-------------|
| P1_public_hi_map_available | Public HI moment map or cube staged under `data/raw/phase6f/public/` |
| P2_public_stellar_mass_proxy_available | IRAC-derived M_* proxy map staged |
| P3_public_h2_or_co_available | CO(2-1) or H₂ proxy staged |
| P4_public_wcs_metadata_available | WCS, beam, units verified |
| P5_public_license_and_citation_documented | Registry + extraction log updated |
| P6_public_reprojection_ready | Validated WCS→disk-plane reprojection for Tier B grid |

**Status:** P-gates are evaluated by `scripts/run_phase6f_public_pilot_gates.py` — **separate** from Corbelli G gates.

**Staging layout:** `data/raw/phase6f/public_pilot/` (see `docs/phase6f_public_pilot_download_instructions.md`).

**Labeling rule:** All Tier B τ-map outputs must be marked  
`PUBLIC_DATA_PILOT_NOT_CORBELLI_PRIMARY`.

---

## Tier C — Reference / proxy / synthetic

**Products:**

- Gratier 2010 VLA-only HI moment maps (in repo)
- Synthetic FITS fixtures (tests)

**Gate mapping:** None for scientific mode. Reference-proxy script flag only.

**Marker:** `REFERENCE_ONLY_NOT_FOR_SCIENTIFIC_CLAIMS`

**Rule:** Tier C must **never** PASS G1 or satisfy public pilot scientific claims.

---

## Strict Corbelli scientific mode

Requires **Tier A** + all Corbelli gates (G1, G2, G3, G4, G5, G7, G8 PASS).

Tier B may enable a **separate pilot pipeline** in a future PR — not in this audit PR.

Tier C remains smoke-test only.

---

## Cross-tier prohibitions

| Action | Allowed? |
|--------|----------|
| Mark G1 PASS with LGLBS HI | **No** |
| Mark G2 PASS with S4G-derived M_* | **No** |
| Label Tier B output as Corbelli replication | **No** |
| Use Gratier reference in strict scientific build | **No** |
| Claim dark matter disproven from Tier B pilot | **No** |

---

## Related documents

- `docs/phase6f_public_data_acquisition_audit.md`
- `docs/phase6f_public_pilot_limitations.md`
- `data/raw/phase6f/manifest/phase6f_public_candidate_registry.yaml`
