# Raw / interim extracted tables

Files here are **traceable extractions** from literature tables (header + real rows only).

They are **not** the model-ready `data/processed/m33_rotation.csv`:

- Surface densities (`sigma_*`) are not baryonic velocities (`v_gas_kms`, `v_disk_kms`).
- Phase 1D must derive or source baryonic velocity components before building the processed CSV.

## Corbelli et al. 2014 Table 1

| File | Role |
|------|------|
| `corbelli2014_table1_raw_template.csv` | Header-only template |
| `corbelli2014_table1_raw.csv` | **58 rows** from A&A Table 1 (Phase 1D-C); raw/interim only |

Validate extracted table:

```bash
python scripts/validate_corbelli2014_table1_raw.py
```

Re-extract from official PDF (requires `pymupdf`):

```bash
python scripts/extract_corbelli2014_table1_from_pdf.py
```
