# Raw / interim extracted tables

Files here are **traceable extractions** from literature tables (header + real rows only).

They are **not** the model-ready `data/processed/m33_rotation.csv`:

- Surface densities (`sigma_*`) are not baryonic velocities (`v_gas_kms`, `v_disk_kms`).
- Phase 1D must derive or source baryonic velocity components before building the processed CSV.

## Corbelli et al. 2014 Table 1

Template (headers only until extraction): `corbelli2014_table1_raw_template.csv`

Create or refresh template:

```bash
python scripts/prepare_corbelli2014_table1_template.py
```
