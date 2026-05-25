# Manuscript draft (Phase 6E)

Journal-neutral submission package for the M33 TDF τ-geometry companion project. Science metrics are frozen; author block and journal template remain TODO.

## What this is

- `m33_tdf_tau_geometry_draft.tex` — readable draft with verified `Corbelli2014` / `LopezFune2017` bibliography, submission sections, and `\includefig` (prefers `paper/figures/`, else `outputs/figures/`).
- `figures/` — optional packaged PNGs from `python scripts/prepare_paper_figures.py` (copy only).
- Content aligns with **existing reproducible pipeline outputs** (Phases 1D–6A); numbers match `outputs/tables/phase6a_key_results_table.csv`.

## What this is not

- **No new science results** — packaging phases do not refit models or change metrics.
- **Not journal-formatted** — select template, fill authors/affiliations, acknowledgments, and funding before submission.
- **Not an overclaim** — language follows `docs/manuscript_allowed_language.md` and `outputs/tables/phase6a_claim_traceability_matrix.csv`.

## Claim control

**Do not state** that dark matter is disproven, that TDF replaces ΛCDM, that lensing is confirmed, or that deflection maps are physical arcsecond predictions.

**Do state** (with caveats): low-parameter τ rotation consistency, normalized deflection **proxy** from the same frozen τ-map, and López Fune **dynamical upper-bound** consistency only.

## Build (optional)

Requires a LaTeX distribution (`pdflatex` or `latexmk`).

```bash
python scripts/prepare_paper_figures.py   # optional: copy PNGs to paper/figures/
cd paper
latexmk -pdf m33_tdf_tau_geometry_draft.tex
```

## Audit

```bash
python scripts/run_phase6b_manuscript_audit.py
python scripts/run_phase6c_manuscript_draft_audit.py
python scripts/run_phase6d_manuscript_polish_audit.py
python scripts/run_phase6e_submission_package_audit.py
```

Submission checklist: `docs/manuscript_submission_checklist.md`.  
Drafting log: `docs/manuscript_drafting_notes.md`.  
Bibliography verification: `docs/manuscript_bibliography_verification.md`.
