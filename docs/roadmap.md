# Roadmap — TDF M33 τ-geometry

High-level sequence. Details: `docs/project_plan.md`.

```
Phase 0–1   Scaffold, data schema, provenance, M33 ingestion
Phase 2     Baryonic + NFW + Burkert baselines
Phase 3     Radial τ reconstruction (direct, regularized, low-param, sensitivity)
Phase 4     Axisymmetric 2D map + disk-to-sky projection  [scaffold, not mass-constrained]
Phase 5     Normalized deflection proxy + dynamical limit audits  [not calibrated lensing]
Phase 6A–E  Publication summary, manuscript, submission packaging
Phase 6F    Mass-constrained τ-map protocol (M33 pilot)  ← CURRENT (design)
Phase 6F+   Implementation + gated maps + optional deflection re-compute
Phase 7     Multi-galaxy extension (e.g. SPARC) — only after M33 6F gates
```

---

## Strategic rationale

1. **One galaxy done right (M33)** before scaling claims.
2. **Separate** rotation success from lensing language until gates pass.
3. **Mass geometry in the objective**, not post-hoc smoothing, is the Phase 6F differentiator from Phase 4A.

---

## Out of scope (until explicitly scheduled)

- SPARC-wide τ-map campaign
- Physical arcsec lensing calibration (`alpha_tau_scale` fit)
- Dark-matter replacement claims
- Retroactive changes to Phase 3–5 numerical outputs without new phase tag

---

## Key documents by phase

| Phase | Doc |
|-------|-----|
| 6F design | `docs/phase6f_mass_constrained_tau_map_protocol.md` |
| 6F data | `docs/phase6f_data_requirements_for_physical_tau_map.md` |
| Theory | `docs/theory_summary.md` |
| Claims | `docs/manuscript_allowed_language.md` |
| Repro | `docs/reproducibility_commands.md` |
