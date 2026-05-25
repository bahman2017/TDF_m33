# Paper figures (Phase 6E packaging)

Copies of pipeline PNGs for journal submission. **Content is unchanged** — sources remain under `outputs/figures/`.

| Manuscript file | Pipeline source |
|-----------------|-----------------|
| `fig1_rotation_baryonic.png` | `outputs/figures/phase2a_baryonic_only_rotation_curve.png` |
| `fig2_model_comparison.png` | `outputs/figures/phase3c_tdf_lowparam_rotation_comparison.png` |
| `fig3_tau_gradient.png` | `outputs/figures/phase3c_tdf_lowparam_tau_gradient.png` |
| `fig4_tau_map.png` | `outputs/figures/phase4b_tau_sky_projected_map.png` |
| `fig4_tau_map_disk.png` | `outputs/figures/phase4a_tau_2d_map.png` |
| `fig4_tau_map_sky.png` | `outputs/figures/phase4b_tau_sky_projected_map.png` |
| `fig5_deflection_proxy.png` | `outputs/figures/phase5a_deflection_magnitude_map.png` |

Regenerate pipeline figures with the commands in `docs/manuscript_figures_and_tables.md`, then re-run:

```bash
python scripts/prepare_paper_figures.py
```

Primary single-panel alias for Fig.~4 in some layouts: `fig4_tau_map_sky.png`.
