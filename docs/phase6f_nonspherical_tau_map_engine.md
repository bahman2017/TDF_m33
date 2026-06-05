# Phase 6F non-spherical disk-plane τ-map engine

**Status:** Implemented with strict data gates. **Scientific M33 τ-map claims blocked** until primary Corbelli 2014 maps are acquired **and** validated WCS reprojection is implemented.

## Scientific model (Phase 6F notation)

- **τ(x,y)** — physical delay-time field on the disk plane (not τ(R) copied to 2D).
- **Kg** — gravitational projection coefficient.
- **κ_τ (`kappa_tau`)** — dynamical field stiffness.
- **g_τ = −Kg ∇τ**
- **κ_τ ∇²τ − m_τ² τ = J_τ**
- **J_τ = α_gas Σ_gas + α_star Σ_star**
- **Σ_gas = f_He (Σ_HI + Σ_H2)**, **Σ_b = Σ_gas + Σ_star**

Do **not** use ambiguous **K_τ** in new Phase 6F code (historical Phase 3 radial notation remains documented separately).

## Modes

| Mode | CLI | Behavior |
|------|-----|----------|
| **Strict (default)** | `build_phase6f_nonspherical_tau_map.py` | Stops with `BLOCKED_PENDING_PRIMARY_CORBELLI_MAPS` if required gates fail |
| **Reference proxy** | `--allow-reference-proxy` | Smoke/diagnostic only; all outputs marked `REFERENCE_ONLY_NOT_FOR_SCIENTIFIC_CLAIMS` |

## Data gates

| Gate | Requirement | Blocks scientific_ready? |
|------|-------------|--------------------------|
| G1 | Primary Corbelli VLA+GBT HI | **Yes** |
| G2 | Primary BVIgi stellar map | **Yes** |
| G3 | Tilted-ring geometry CSV | **Yes** |
| G4 | WCS / grid metadata | **Yes** |
| G5 | Documented units | **Yes** |
| G6 | Uncertainty / mask rules | **No** (diagnostic; status tracked) |
| G7 | Provenance registry | **Yes** |
| G8 | Validated WCS→disk-plane reprojection | **Yes** |

**scientific_ready** = G1, G2, G3, G4, G5, G7, **G8** all PASS.

**G8 note:** Current code only has `PLACEHOLDER_NOT_SCIENTIFIC_WCS_REPROJECTION` (scipy.ndimage.zoom). Scientific mode **cannot** use it. Config flag `reprojection.allow_placeholder_reprojection` defaults to **false**.

Gratier 2010 VLA HI **does not** satisfy G1.

## Boundary conditions

- **Dirichlet** (τ=0): default, supported.
- **Neumann**: raises `NotImplementedError` — not yet scientifically validated.

## Package layout

```
src/tdf_m33/maps/
  grid.py          — disk-plane Cartesian grid (kpc)
  geometry.py      — tilted-ring i(R), PA(R)
  reprojection.py  — WCS alignment readiness flags
  sources.py       — Σ maps and J_τ
  solver.py        — sparse FD field solve
  ...
```

## Relation to Phase 4A

Phase **4A/4B** remain **axisymmetric radial extensions** (`τ_2D = τ_radial(R)`). This engine is the **non-spherical disk-plane** path once primary data **and** validated reprojection pass gates.

## Commands

```bash
python scripts/run_phase6f_tau_map_gates.py
python scripts/build_phase6f_nonspherical_tau_map.py
python scripts/build_phase6f_nonspherical_tau_map.py --allow-reference-proxy
python scripts/plot_phase6f_tau_map_diagnostics.py
```

Config: `configs/phase6f_nonspherical_tau_map.yaml`
