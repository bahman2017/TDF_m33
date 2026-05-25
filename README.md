# TDF–M33 τ-Geometry: Reconstructing Missing Acceleration as a Time-Delay Field Map

Computational companion repository for a publication-quality study of whether the missing acceleration inferred from M33 rotation dynamics can be represented as a smooth **Time-Delay Field (TDF) / τ-geometry**, and whether the same τ-map yields lensing/deflection predictions consistent with observational limits—**without** introducing an independent dark matter halo in the TDF pathway.

## Scientific objective

M33 is used as an **intermediate-scale test** of whether the missing acceleration inferred from rotation dynamics can be reconstructed as a smooth τ-geometry, and whether the same τ-map produces lensing/deflection predictions consistent with observational limits.

The project compares dynamical explanations of the observed rotation curve against several baselines and a TDF reconstruction:

| Model | Role | Status |
|-------|------|--------|
| Baryonic-only | Minimum baryonic contribution from gas, disk, bulge | Planned (Phase 2) |
| NFW halo | Standard cuspy dark-matter baseline | Planned (Phase 2) |
| Burkert halo | Core-dominated dark-matter baseline | Planned (Phase 2) |
| TDF radial τ-profile | Missing acceleration as τ-gradient / radial profile | Planned (Phase 3) |
| TDF 2D τ-map | Spatial τ-geometry extension | Optional (Phase 4) |
| Lensing / deflection from τ-map | Consistency test using same τ as rotation | Planned (Phase 5) |

Core rotation–τ relations (see `docs/theory_summary.md`):

\[
v_{\mathrm{obs}}^2(r) = v_{\mathrm{bar}}^2(r) + v_\tau^2(r)
\]

\[
v_\tau^2(r) = r\, K_\tau \,\frac{d\tau}{dr}
\]

\[
\frac{d\tau}{dr} = \frac{v_{\mathrm{obs}}^2(r) - v_{\mathrm{bar}}^2(r)}{r\, K_\tau}
\]

## What TDF / τ-geometry is testing here

This repository tests whether the **residual** centripetal support not explained by baryons alone can be encoded as a smooth time-delay field τ(r) (and later τ(x,y)), linked to an effective acceleration through the TDF coupling \(K_\tau\), rather than as a separate halo component in the TDF branch of the analysis.

The τ-field is **reconstructed from rotation data** in early phases; in later phases the **same** τ-map is used to predict lensing/deflection signatures for comparison with limits—without adding a new halo degree of freedom in the TDF pathway.

## What this repository is **not** claiming

- **Dark matter is not disproven.** Competing halo baselines (NFW, Burkert) are retained for comparison.
- A successful rotation-curve fit with τ alone is **not** sufficient evidence against dark matter.
- Weak or absent M33 lensing constraints do not automatically validate τ-geometry; the lensing stage is a **prediction / consistency** exercise unless direct lensing data are incorporated.
- Results here are specific to M33 and the stated assumptions; they are not a universal replacement for ΛCDM.

Controlled framing (also in `docs/paper_notes.md`):

> M33 is used as an intermediate-scale test of whether the missing acceleration inferred from rotation dynamics can be reconstructed as a smooth τ-geometry, and whether the same τ-map produces lensing/deflection predictions consistent with observational limits.

## Current status

| Phase | Status |
|-------|--------|
| **Phase 0** | Complete — repository scaffold, docs, config, minimal tests |
| **Phase 1A** | Complete — canonical CSV schema and processed-data validation |
| **Phase 1B** | Complete — source manifest loader, acquisition plan |
| **Phase 1C** | Complete — raw acquisition layout, Table 1 raw template, source audit |
| **Phase 1D** | Complete — Table 1 extraction, D1 baryonic derivation, Fig. 12 checks |
| **Phase 1D-D2-B** | Complete — canonical `data/processed/m33_rotation.csv` (58 rows) |
| **Phase 2A** | Complete — baryonic-only baseline diagnostics and residuals |
| **Phase 2B** | Complete — NFW and Burkert halo baseline fits (comparison only) |
| **Phase 2C** | Complete — model audit, Burkert boundary flag, Phase 3 residual readiness |
| **Phase 3A** | Complete — direct pointwise τ from baryonic Δv² (unsmoothed) |
| **Phase 3B-A** | Complete — regularized τ-gradient (Gaussian + spline) |
| **Phase 3C** | Complete — low-parameter knot τ; AIC/BIC vs NFW/Burkert |
| **Phase 3D** | Complete — sensitivity audit (K_τ, mask, smoothing) |
| **Phase 4A** | Complete — axisymmetric disk-plane 2D τ map from Phase 3C |
| **Phase 4B-A** | Complete — disk-to-sky τ projection (geometry only) |
| Phase 4B+ / 5 | Not started — morphology-aware τ, lensing |

## Data provenance status

- **Phase 0** completed the publication-oriented repository scaffold.
- **Phase 1A** completed the processed CSV schema (`tdf_m33.data.schema`, `validation`, `io`) and empty template — **no M33 numbers**.
- **Phase 1B** added the literature source registry (`tdf_m33.data.manifest`) and `docs/data_acquisition_plan.md`.
- **Phase 1C** added download/extracted directories, active `sources_manifest.yaml`, raw Table 1 template, `docs/extraction_log.md`, and audit scripts.
- **Phase 1D-D2-B** created **`data/processed/m33_rotation.csv`** (58 rows): observed rotation from Corbelli 2014 Table 1; baryonic \(v_{\mathrm{gas}}\), \(v_{\mathrm{disk}}\) from documented D1 disk-gravity derivation (`derived_baryonic_velocity_pass_with_caveat`). Fig. 12 corrected sanity check is PASS_WITH_CAVEAT; digitized curves are **not** canonical velocities.

Processed-data commands:

```bash
python scripts/build_m33_rotation_processed.py
python scripts/validate_m33_data.py data/processed/m33_rotation.csv
python scripts/run_phase2a_baryonic_only.py
python scripts/run_phase2b_halo_baselines.py
python scripts/run_phase2c_model_audit.py
python scripts/run_phase3a_tdf_radial_reconstruction.py
python scripts/run_phase3b_tdf_regularized_reconstruction.py
python scripts/run_phase3c_tdf_lowparam_model.py
python scripts/run_phase3d_tdf_sensitivity.py
python scripts/run_phase4a_tdf_2d_map.py
python scripts/run_phase4b_tau_projection.py
python scripts/check_sources_manifest.py data/raw/sources_manifest.yaml
python scripts/audit_m33_sources.py
```

See `docs/extraction_log.md` and docs for provenance. Phase 3C fits k=3,4,5 knot τ-gradient models (\(K_\tau=1\) fixed) with AIC/BIC on the Corbelli mask alongside NFW/Burkert. Phase 3A/3B are reconstruction steps, not fair AIC/BIC competitors. No dark-matter replacement claim.

## Expected data sources

Planned inputs (catalogued in `docs/data_sources.md`):

- M33 rotation curve (HI and/or hybrid tracers)
- Gas surface density / contribution to \(v_{\mathrm{bar}}\)
- Stellar disk (and bulge/spheroid if required) mass models
- Distance, inclination, and systemic velocity assumptions
- Lensing / deflection observational limits (where available)

Every transformation from raw to processed data must be documented in `docs/data_sources.md`.

## Reproducibility philosophy

- Configuration-driven runs via `configs/m33_default.yaml` (no hard-coded science parameters in source).
- Versioned dependencies in `pyproject.toml`; install with editable mode for development.
- Raw data live under `data/raw/`; processed tables under `data/processed/`; figures and tables under `outputs/`.
- Scripts under `scripts/` will orchestrate end-to-end pipelines once implemented.
- Tests guard imports and core algebraic identities before full models exist.

## Planned outputs

| Location | Content |
|----------|---------|
| `outputs/figures/` | Rotation curves, τ-profiles, 2D τ-maps, lensing comparison panels |
| `outputs/tables/` | Best-fit parameters, model comparison metrics |
| `outputs/reports/` | Run logs, assumption summaries, reproducibility manifests |

## Quickstart

From the repository root:

```bash
# Create and activate a virtual environment (recommended)
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate

# Install package in editable mode with dependencies
python -m pip install -e .

# Optional: development tools
python -m pip install -e ".[dev]"

# Run tests
python -m pytest

# Validate source manifest and processed CSV template
python scripts/check_sources_manifest.py data/raw/sources_manifest_template.yaml
python scripts/validate_m33_data.py data/processed/m33_rotation_schema_template.csv
```

Install, tests, manifest checks, source audit, and CSV template validation work through Phase 1C. Model-ready ingestion (Phase 1D), fitting, and figures come later (see `docs/project_plan.md`).

## Citation

This repository is intended to be **cited alongside a future peer-reviewed paper**. Until a DOI or Zenodo record exists, cite the repository URL and version tag once released. A formal `CITATION.cff` will be added when the manuscript is submitted.

## Documentation

| Document | Purpose |
|----------|---------|
| [docs/project_plan.md](docs/project_plan.md) | Phased roadmap and acceptance criteria |
| [docs/theory_summary.md](docs/theory_summary.md) | Equations and τ–acceleration mapping |
| [docs/data_sources.md](docs/data_sources.md) | Data provenance and transformations |
| [docs/data_acquisition_plan.md](docs/data_acquisition_plan.md) | How real M33 data will enter the repo |
| [docs/extraction_log.md](docs/extraction_log.md) | Download and Table 1 extraction audit |
| [docs/assumptions_and_limitations.md](docs/assumptions_and_limitations.md) | Scope and caveats |
| [docs/paper_notes.md](docs/paper_notes.md) | Title options, claims, planned figures |

## License

MIT (see repository license file when added).
