# Manuscript bibliography verification (Phase 6D)

Verified against in-repository `data/raw/sources_manifest.yaml`, `docs/data_sources.md`, and project DOI registry. External DOI resolver fetch was attempted; metadata matched published records already documented in the repo.

| citation_key | verified_title | authors | journal | year | pages / article id | DOI | verification_source | status |
|--------------|----------------|---------|---------|------|-------------------|-----|---------------------|--------|
| `Corbelli2014` | Dynamical signatures of a ΛCDM-halo and the distribution of the baryons in M33 | Corbelli, E.; Thiliker, D. A.; Zschaechner, L.; et al. | Astronomy & Astrophysics | 2014 | Vol. 572, Article A23 | [10.1051/0004-6361/201424033](https://doi.org/10.1051/0004-6361/201424033) | `sources_manifest.yaml` (`corbelli_et_al_2014`); `docs/data_sources.md` | **verified** |
| `LopezFune2017` | The radial dependence of dark matter distribution in M33 | López Fune, M. C.; Salucci, P.; Corbelli, E. | Monthly Notices of the Royal Astronomical Society | 2017 | Vol. 474, p. 4010 (first page) | [10.1093/mnras/stx2742](https://doi.org/10.1093/mnras/stx2742) | `sources_manifest.yaml` (`lopez_fune_salucci_corbelli_2017`); `docs/lopez_fune_2017_extraction_plan.md`; arXiv 1611.01409 (accepted manuscript in repo) | **verified** |

## Notes

- **Corbelli et al. 2014** is the primary rotation/baryonic source for this pipeline (`data/processed/m33_rotation.csv`).
- **López Fune et al. 2017** is the dynamical upper-bound reference only (Phase 5C-B); not a lensing citation.
- Page range for MNRAS 474 is not required for in-text citations in this draft; first page **4010** follows project registry wording.
- No additional references were added in Phase 6D.

## Manuscript update

`paper/m33_tdf_tau_geometry_draft.tex` bibliography entries were updated to remove `placeholder` / open `TODO` markers for these two keys.
