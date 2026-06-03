# Roadmap — TDF M33 τ-geometry

High-level sequence. Details: `docs/project_plan.md`.

```
Phase 0–1   Scaffold, data schema, provenance, M33 ingestion
Phase 2     Baryonic + NFW + Burkert baselines
Phase 3     Radial τ reconstruction (direct, regularized, low-param, sensitivity)
Phase 4     Axisymmetric 2D map + disk-to-sky projection  [scaffold, not mass-constrained]
Phase 5     Normalized deflection proxy + dynamical limit audits  [not calibrated lensing]
Phase 6A–E  Publication summary, manuscript, submission packaging
Phase 6F    Mass-constrained τ-map protocol (M33 pilot)  [design complete]
Phase 6F-data  Data acquisition & provenance plan  [complete, PR #2]
Phase 6F-source  Verified manifests + reference staging  ← CURRENT
Phase 6F-impl  Mass-constrained τ reconstruction  [blocked — primary HI/stellar missing]
Phase 7     Multi-galaxy extension (e.g. SPARC) — only after M33 6F gates
```

---

## Strategic rationale

1. **One galaxy done right (M33)** before scaling claims.
2. **Separate** rotation success from lensing language until gates pass.
3. **Mass geometry in the objective**, not post-hoc smoothing, is the Phase 6F differentiator from Phase 4A.
4. **Data readiness before fit** — 2D HI/stellar maps must be traceable before Phase 6F-impl.

---

## Out of scope (until explicitly scheduled)

- SPARC-wide τ-map campaign
- Physical arcsec lensing calibration (`alpha_tau_scale` fit)
- Dark-matter replacement claims
- Retroactive changes to Phase 3–5 numerical outputs without new phase tag
- τ reconstruction or deflection re-runs during Phase 6F-data

---

## Key documents by phase

| Phase | Doc |
|-------|-----|
| 6F design | `docs/phase6f_mass_constrained_tau_map_protocol.md` |
| 6F data requirements | `docs/phase6f_data_requirements_for_physical_tau_map.md` |
| 6F-data acquisition | `docs/phase6f_data_acquisition_plan.md` |
| 6F-data gates | `docs/phase6f_data_provenance_checklist.md` |
| 6F-source manifest | `docs/phase6f_source_manifest.md` |
| 6F-source access | `docs/phase6f_dataset_access_notes.md` |
| 6F-source status | `outputs/reports/phase6f_source_acquisition_status.md` |
| Theory | `docs/theory_summary.md` |
| Claims | `docs/manuscript_allowed_language.md` |
| Repro | `docs/reproducibility_commands.md` |
