# Phase 6F — Public M33 data acquisition audit

**Date:** 2026-05-23  
**Scope:** Document public download routes for M33 2D products that could support a **public-data Phase 6F pilot**, without claiming Tier B products are exact Corbelli 2014 primary maps.

**Registry:** `data/raw/phase6f/manifest/phase6f_public_candidate_registry.yaml`  
**Audit script:** `python scripts/audit_phase6f_public_data_sources.py`

---

## Executive summary

| Question | Answer |
|----------|--------|
| Exact Corbelli 2014 primary HI + BVIgi stellar FITS publicly downloadable? | **No** — not identified on A&A, arXiv, or VizieR (2026-05-23 audit) |
| Fastest public Tier B pilot route? | **LGLBS HI v1.0 (CANFAR)** + **Spitzer S4G IRAC 3.6/4.5 µm (IRSA)** + **IRAM LP006 CO(2-1)** |
| Can Tier B PASS G1/G2 Corbelli gates? | **No** |
| Strict Corbelli scientific Phase 6F blocked? | **Yes** — unchanged |

---

## Tier definitions

See `docs/phase6f_data_tiers.md` for full tier policy.

| Tier | Role | Scientific Corbelli mode? |
|------|------|---------------------------|
| **A** | Exact Corbelli 2014 primary products | Required for G1/G2 PASS |
| **B** | Public-data M33 τ-map **pilot** | Separate P1–P6 gates (future); not G1/G2 |
| **C** | Reference/proxy smoke tests | `REFERENCE_ONLY_NOT_FOR_SCIENTIFIC_CLAIMS` |

---

## Candidate source audit

### Tier A — Corbelli et al. 2014 (A&A 572, A23)

| Route | URL / DOI | FITS? | Login? | G1/G2? |
|-------|-----------|-------|--------|--------|
| A&A publisher article + Table 1 | [DOI 10.1051/0004-6361/201424033](https://doi.org/10.1051/0004-6361/201424033) | Table only | No | No (1D) |
| arXiv 1409.2665 | [arxiv.org/abs/1409.2665](https://arxiv.org/abs/1409.2665) | Paper + figures | No | No 2D FITS link |
| CDS/VizieR J/A+A/572/A23 | [VizieR catalog](https://vizier.cds.unistra.fr/viz-bin/VizieR?-source=J/A%2bA/572/A23) | Catalog tables | No | No 2D primary FITS |
| Author request (Corbelli / Thilker) | See `docs/corbelli2014_author_request_email.md` | Expected FITS | N/A | **Yes, if provenance verified** |

**Conclusion:** Exact Corbelli 2014 VLA+GBT HI and BVIgi stellar **2D FITS are not publicly downloadable** via standard archives as of this audit. Author contact remains the preferred Tier A route.

---

### Tier B — Public-data pilot candidates

#### HI — Koch 2018 / LGLBS

| Source | Citation | Access | File type | Units | Login | Pilot? |
|--------|----------|--------|-----------|-------|-------|--------|
| Koch et al. 2018 scripts | MNRAS 479, 2505; [GitHub e-koch/VLA_Lband](https://github.com/e-koch/VLA_Lband) | Public scripts | Rebuild FITS | K, km/s | No | Yes (effort) |
| LGLBS HI v1.0 | ApJS 279, 35 (2025); [CANFAR release](https://www.canfar.net/storage/vault/list/LGLBS/RELEASES/LGLBS-HI-v1.0) | Public vault | FITS HI products | See release | **Yes (CADC)** | **Yes — recommended** |
| Lockman GBT 09A-017 | ApJ 758, 147 | NRAO/archive query | GBT cube | T_ant | Likely | Ancillary |
| NRAO archive VLA | Various PIDs | [archive.nrao.edu](https://archive.nrao.edu/) | UVFITS/MS | Post-imaging | Yes | High effort |

**Note:** Koch/LGLBS products use VLA+GBT mosaics related to the Koch team reduction — **not** the Corbelli 2014 merged HI map used in dynamical modeling.

#### Stellar — Spitzer IRAC

| Source | Citation | Access | File type | Units | Login | Pilot? |
|--------|----------|--------|-----------|-------|-------|--------|
| S4G IRAC 3.6 + 4.5 µm | Sheth+ 2010; Querejeta+ 2015; [IRSA S4G](https://irsa.ipac.caltech.edu/data/SPITZER/S4G/) | IRSA Atlas | FITS mosaics | MJy/sr → M/L | No | **Yes — recommended** |
| LVL IRAC | Dale et al. 2009; [IRSA LVL](https://irsa.ipac.caltech.edu/data/SPITZER/LVL/) | IRSA Atlas | FITS mosaics | MJy/sr | No | Yes (fallback) |

Derive stellar mass surface density using a **documented M/L prescription** (Querejeta/Meidt-style). This is a **proxy**, not Corbelli BVIgi pixel-SED map.

#### H2 / CO — IRAM

| Source | Citation | Access | File type | Units | Login | Pilot? |
|--------|----------|--------|-----------|-------|-------|--------|
| IRAM LP006 CO(2-1) | Druard et al. 2014, A&A 567, A118; [ILPA/LP006](https://www.iram.fr/ILPA/LP006/) | Public archive | FITS cube + moment | K km/s | No | **Yes** |

---

### Tier C — Reference / proxy only

| Source | In repo? | Role |
|--------|----------|------|
| Gratier 2010 VLA HI 12″ moments | Yes (`reference/gratier2010_vla_hi_12sec/`) | `--allow-reference-proxy` smoke test |
| Synthetic test fixtures | Tests only | Gate/plumbing validation |

---

## Public pilot staging (Tier B workflow)

**Registry:** `data/raw/phase6f/public_pilot/manifest/phase6f_public_pilot_source_registry.yaml`  
**Instructions:** `docs/phase6f_public_pilot_download_instructions.md`

```bash
python scripts/inventory_phase6f_public_pilot_data.py
python scripts/run_phase6f_public_pilot_gates.py
```

## Public pilot gates (P1–P6)

Defined in `docs/phase6f_data_tiers.md`. Checked by `run_phase6f_public_pilot_gates.py` — **not** Corbelli G1/G2/G8.

| Gate | Requirement |
|------|-------------|
| P1 | Public HI map/cube staged |
| P2 | IRAC-derived stellar mass proxy staged |
| P3 | CO(2-1) or H2 proxy staged |
| P4 | WCS/units verified on Tier B products |
| P5 | License + citations documented |
| P6 | Validated reprojection for Tier B grid |

---

## Recommended next steps

1. **Tier A:** Send author request (`docs/corbelli2014_author_request_email.md`) — remains gold standard.
2. **Tier B pilot (parallel track):** Register CADC account → download LGLBS HI v1.0 M33 products → IRSA S4G IRAC → IRAM LP006 CO → document in new `tier_b` manifest (future PR).
3. **Do not** mark G1/G2 PASS with Tier B data.
4. **Do not** enable strict Corbelli scientific build until Tier A + G8 satisfied.

---

## Claim boundary

- M33 is a reproducible test case for τ-geometry field reconstruction from baryonic structure.
- **No dark-matter disproof claim.**
- **No lensing/deflection fit.**
- Tier B pilot ≠ exact Corbelli replication.
