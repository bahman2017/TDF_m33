# Scripts

Command-line entry points for pipelines (data ingest, fit, plot, lensing) will live here in later phases.

Example (future):

```bash
python scripts/fit_rotation.py --config configs/m33_default.yaml
```

**Phase 1A — validate processed CSV:**

```bash
python scripts/validate_m33_data.py data/processed/m33_rotation_schema_template.csv
```

**Phase 1B — validate sources manifest:**

```bash
python scripts/check_sources_manifest.py data/raw/sources_manifest.yaml
```

**Phase 1C — raw Table 1 template and source audit:**

```bash
python scripts/prepare_corbelli2014_table1_template.py
python scripts/audit_m33_sources.py
```

Model-ready ingestion and fit/plot scripts are not implemented yet (Phase 1D+).
