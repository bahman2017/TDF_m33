# Phase 6F - Public pilot limitations

Explicit limitations for a **Tier B public-data** M33 τ-map pilot.

---

## What a Tier B pilot is

A reproducible computational experiment using **publicly accessible** M33 HI, stellar-mass-proxy, and CO products to test whether the Phase 6F disk-plane field engine can ingest real 2D baryonic structure -  **without** claiming equivalence to Corbelli et al. 2014 primary dynamical maps.

---

## What a Tier B pilot is not

- **Not** exact Corbelli 2014 VLA+GBT HI + BVIgi stellar replication
- **Not** a PASS of G1, G2, or strict Corbelli `scientific_ready`
- **Not** evidence that dark matter is disproven
- **Not** a calibrated lensing or deflection measurement
- **Not** a substitute for author-provided primary FITS when publishing Corbelli-comparable claims

---

## Known differences vs Tier A (Corbelli 2014)

| Aspect | Tier A (Corbelli) | Tier B (public pilot) |
|--------|-------------------|------------------------|
| HI stack | Corbelli VLA+GBT merge for dynamical model | Koch/LGLBS reduction; different pipeline/version |
| Stellar map | BVIgi pixel-SED M_* | IRAC 3.6/4.5 µm + external M/L |
| CO / H2 | As used in Corbelli mass model | IRAM LP006 CO(2-1); separate X_CO assumptions |
| Velocity field | Corbelli tilted-ring HI moments | LGLBS / Koch moments (if used) |
| Provenance | Author-verified primary | Archive download + project derivation log |
| Publication label | Corbelli-constrained τ-map (future) | `PUBLIC_DATA_PILOT_NOT_CORBELLI_PRIMARY` |

---

## Scientific claim ceiling for Tier B

Permitted (with P-gates and explicit labeling):

- Pipeline integration test on real public M33 maps
- Diagnostic τ-field solve under documented proxies
- Comparison of radial baryonic structure vs Table 1 **with stated caveats**
- Method development for WCS→disk-plane reprojection (P6)

Not permitted:

- Stating results match Corbelli 2014 dynamical decomposition
- Using Tier B maps to PASS G1/G2
- Enabling strict Corbelli build without Tier A
- Lensing confirmation or DM replacement language

---

## M/L and unit caveats (stellar Tier B)

IRAC-derived stellar mass requires:

- Documented M/L curve (e.g. Querejeta et al. 2015; Meidt et al. 2014 prescriptions)
- Extinction treatment stated
- Distance and inclination consistent with geometry CSV
- Propagation of M/L uncertainty into J_τ (future G6-style diagnostic)

Corbelli BVIgi map includes pixel-SED history not reproduced by simple IRAC color-M/L.

---

## HI caveats (Tier B)

- LGLBS/Koch products: confirm moment-0 units and He correction vs Corbelli Table 1
- Beam convolution differs from Corbelli merged map
- Outer-disk sensitivity not identical to Corbelli GBT+VLA combination

---

## CO / H2 caveats (Tier B)

- CO(2-1) traces molecular gas via X_CO conversion -  not identical to Corbelli H₂ prescription
- 12″ CO beam vs HI/optical resolution mismatch requires documented smoothing

---

## Required output markers (future pilot PR)

All Tier B τ-map artifacts must include metadata fields:

```yaml
data_tier: Tier_B
corbelli_primary_replication: false
label: PUBLIC_DATA_PILOT_NOT_CORBELLI_PRIMARY
gates_satisfied: [P1, P2, ...]  # never G1/G2
```

---

## Relation to strict mode

`python scripts/build_phase6f_nonspherical_tau_map.py` (strict) remains:

```
BLOCKED_PENDING_PRIMARY_CORBELLI_MAPS
```

until Tier A G1/G2/G8 satisfied. Tier B work proceeds on a **separate track**.

## Staging workflow (this phase)

- Raw folders: `data/raw/phase6f/public_pilot/{hi_lglbs,hi_koch2018,stellar_s4g_irac,stellar_lvl_irac,co_iram_lp006}/`
- No scientific τ-map or lensing/deflection runs during staging.
- Future public-pilot τ-map must wait for P1–P6 PASS and frozen validation.
