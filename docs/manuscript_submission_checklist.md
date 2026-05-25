# Manuscript submission checklist (Phase 6E)

Journal-neutral packaging for `paper/m33_tdf_tau_geometry_draft.tex`. This checklist does not add science results or change numerical metrics.

## Author and affiliation

- [ ] **TODO:** Replace `[Author One]` / `[Author Two]` / `[Author Three]` and affiliation lines in the manuscript author block.
- [ ] **TODO:** Set corresponding author email and ORCID if required by target journal.
- [ ] No verified author list exists in `configs/` or project docs — placeholders are intentional.

## Journal target

- [ ] **TODO:** Select journal and download official LaTeX class / bibliography style.
- [ ] **TODO:** Reformat title page, abstract word limit, section numbering, and reference style.
- [ ] **TODO:** Resolve overfull `\hbox` warnings from local `latexmk` build (cosmetic until template is fixed).

## Figure packaging

- [ ] Run `python scripts/prepare_paper_figures.py` to copy PNGs into `paper/figures/` (copy only; no content edits).
- [ ] Confirm manuscript figure names: `fig1_rotation_baryonic.png` … `fig5_deflection_proxy.png` (Fig. 4 uses `fig4_tau_map_disk.png` + `fig4_tau_map_sky.png`).
- [ ] See `paper/figures/README.md` for source mapping from `outputs/figures/`.
- [ ] **Optional:** `fig4_tau_map.png` alias (sky projection) for single-panel layouts.

## Citation verification

| Item | Status |
|------|--------|
| `Corbelli2014` | **Verified** — see `docs/manuscript_bibliography_verification.md` |
| `LopezFune2017` | **Verified** — dynamical upper-bound reference only |
| Additional references | **None added** in Phase 6E |

## LaTeX build

| Item | Status |
|------|--------|
| Source | `paper/m33_tdf_tau_geometry_draft.tex` |
| Local PDF | `paper/m33_tdf_tau_geometry_draft.pdf` (gitignored; regenerate with `latexmk`) |
| Phase 6D audit | `python scripts/run_phase6d_manuscript_polish_audit.py` |
| Phase 6E audit | `python scripts/run_phase6e_submission_package_audit.py` |
| Known warnings | Overfull hbox possible; compile may return non-zero with `-f` while PDF exists |

## Required audits before submission

Run in order (all should report PASS):

```bash
python scripts/run_phase6a_publication_audit.py
python scripts/run_phase6b_manuscript_audit.py
python scripts/run_phase6c_manuscript_draft_audit.py
python scripts/run_phase6d_manuscript_polish_audit.py
python scripts/run_phase6e_submission_package_audit.py
python scripts/validate_m33_data.py data/processed/m33_rotation.csv
python scripts/check_sources_manifest.py data/raw/sources_manifest.yaml
python scripts/audit_m33_sources.py
python -m pytest
```

## Prohibited claims (do not state affirmatively)

- TDF replaces dark matter / no need for dark matter
- M33 proves TDF
- Lensing is confirmed / physical arcsecond prediction without calibration
- Weak-lensing comparison complete
- Dark matter is disproven

Allowed: comparative rotation fit, normalized deflection **proxy**, López Fune **dynamical upper-bound** check with caveats.

## Science caveats (must remain visible)

| Topic | Status / wording |
|-------|------------------|
| D1 baryonic velocities | **PASS_WITH_CAVEAT** — comparative metrics shift if baryons change |
| $K_\tau$ normalization | Convention ($K_\tau=1$); degeneracy documented in Phase 3D |
| Deflection | **`normalized_proxy` only** — no arcsecond calibration |
| Weak lensing | **No M33 weak-lensing comparison** in repository |
| López Fune 2017 | **Dynamical upper-bound only** — not lensing confirmation |

## Submission package sections (Phase 6E)

- [x] Data and code availability (`\section*{Data and Code Availability}`)
- [x] Acknowledgments placeholder
- [x] Conflict of interest placeholder
- [x] Funding placeholder

## Data and code availability text

Repository pipeline, `data/processed/m33_rotation.csv`, and `outputs/reports/phase6a_reproducibility_commands.md` are cited in the manuscript availability section.
