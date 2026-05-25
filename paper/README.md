# Manuscript draft (Phase 6B)

This directory holds a **manuscript draft skeleton** for the M33 TDF τ-geometry companion project. It is **not** a submission-ready paper.

## What this is

- `m33_tdf_tau_geometry_draft.tex` — Phase 6C first readable draft (expanded sections, optional figure placeholders via `\includefig`).
- Content is aligned with **existing reproducible pipeline outputs** (Phases 1D–6A).
- Numerical values in the draft match `outputs/tables/phase6a_key_results_table.csv` and related tables at generation time.

## What this is not

- **No new science results** — the draft does not refit models or add analyses.
- **No invented citations** — bibliography entries are placeholders; replace with verified references before submission.
- **Not an overclaim** — language follows `docs/manuscript_allowed_language.md` and `outputs/tables/phase6a_claim_traceability_matrix.csv`.

## Claim control

**Do not state** that dark matter is disproven, that TDF replaces ΛCDM, that lensing is confirmed, or that deflection maps are physical arcsecond predictions.

**Do state** (with caveats): low-parameter τ rotation consistency, normalized deflection **proxy** from the same frozen τ-map, and López Fune **dynamical upper-bound** consistency only.

## Build (optional)

Requires a LaTeX distribution (`pdflatex` or `latexmk`). Figures are referenced from `outputs/figures/` (generate via pipeline scripts in `docs/manuscript_figures_and_tables.md`).

```bash
cd paper
latexmk -pdf m33_tdf_tau_geometry_draft.tex
```

## Audit

```bash
python scripts/run_phase6b_manuscript_audit.py
python scripts/run_phase6c_manuscript_draft_audit.py
```

Drafting log: `docs/manuscript_drafting_notes.md`.  
Bibliography verification: `docs/manuscript_bibliography_verification.md`.  
Polish audit: `python scripts/run_phase6d_manuscript_polish_audit.py`.
