# López Fune, Salucci & Corbelli 2017 — extraction plan (Phase 5B-C)

**Source ID:** `lopez_fune_salucci_corbelli_2017`  
**Title:** The radial dependence of dark matter distribution in M33  
**Journal:** MNRAS **474**, 4010 (2017)  
**DOI:** [10.1093/mnras/stx2742](https://doi.org/10.1093/mnras/stx2742)  
**arXiv:** [1611.01409](https://arxiv.org/abs/1611.01409) (accepted manuscript PDF used for acquisition)

**Local PDF:** `data/raw/downloads/lopez_fune_salucci_corbelli_2017_m33.pdf`  
**Checksum:** `data/raw/downloads/lopez_fune_salucci_corbelli_2017_m33.pdf.sha256`

**Intended use (Phase 5C+):** Dynamical halo / enclosed-mass **upper-bound consistency** — not direct lensing, not τ calibration.

## Paper structure (10 pages, figure-centric)

No numbered data tables were identified in the acquired PDF text layer. Numerical results appear in **figures** and inline best-fit prose. Extraction for Phase 5C will require figure digitization or manual transcription with page/figure citations — not automated CSV from publisher tables.

## Figures and quantities

| Figure | Content | Phase 5C utility |
|--------|---------|------------------|
| **Fig. 1** | Baryonic surface densities (stellar, gas, total) vs radius; schematic NFW/BRK halo context | Context for baryonic–DM split; **not** independent of Corbelli 2014 inputs |
| **Fig. 2** | M33 RC with rational-function fit; comparison to Corbelli et al. 2014 NFW/BRK global fits | **(d)** Outer rotation constraints; overlap with project rotation branch |
| **Fig. 3** | Confidence ellipses for RC fit parameters \((V_0, r_0, d)\) | Uncertainty context only |
| **Fig. 4** | Effective densities vs \(r\); BRK analysis in \(9.53 \le r \le 22.72\) kpc | **(b)** DM density profile; **(a)** enclosed mass via integration (to be derived) |
| **Fig. 5** | Same as Fig. 4 for NFW halo | **(b)** NFW \(\rho(r)\); compare cusp vs core |
| **Fig. 6** | Observed outer-disk DM density (points) vs BRK/NFW fits | **(b)** Primary profile for upper-bound check |

## Methods (two pathways in paper)

1. **Global RC fit** (\(0.24 \le r \le 22.72\) kpc): NFW preferred over Burkert for \(\chi^2\); parameters stated in §2.2 prose (e.g. BRK \(r_c\), \(\rho_c\); NFW \(c\), scale).
2. **Local density estimator** (\(9.53 \le r \le 22.72\) kpc): Salucci et al. (2010) style; BRK and NFW tested on effective densities — **preferred radial range for Phase 5C** (DM-dominated).

## Phase 5C extraction targets (planned, not performed in 5B-C)

| Target | Suitable? | Notes |
|--------|-----------|--------|
| **(a) Enclosed mass \(M(<r)\)** | Yes | Integrate \(\rho_{\mathrm{DM}}(r)\) from Fig. 6 / quoted profiles; compare to τ-based dynamical proxy at same \(r\) with circularity caveat |
| **(b) DM density profile \(\rho(r)\)** | Yes | Fig. 6 data points + BRK/NFW fit parameters in text |
| **(c) NFW / Burkert parameters** | Yes | Global and local fits (pages 5–6, 8–9); map to Phase 2 baseline parameterization |
| **(d) Outer rotation / density constraints** | Partial | Fig. 2 RC — largely shared with Corbelli 2014 pipeline |

## Not suitable for

| Use | Reason |
|-----|--------|
| **Physical lensing calibration** | Rotation/dynamics only; no deflection angle or \(\kappa\) |
| **`alpha_tau_scale` tuning** | Would fit τ branch to same dynamical system |
| **Direct lensing detection claim** | No weak-lensing data |

## Circularity and independence

- Stellar/gas inputs trace **Corbelli et al. 2014** (already the project primary rotation/baryonic source).
- This paper refits NFW/Burkert on related RC data — **not independent** of the TDF τ reconstruction inputs.
- Phase 5C comparisons must be labeled **consistency / upper-bound** against an external halo literature model, not as verification of τ lensing against independent lensing data.

## Phase 5B-C vs 5C-A vs 5C-B

| Phase | Action |
|-------|--------|
| **5B-C** | Acquire PDF + checksum; document extraction plan |
| **5C-A (complete)** | Extract to `lopez_fune_2017_dm_profile_raw.csv` and `lopez_fune_2017_halo_parameters_raw.csv`; audit via `validate_lopez_fune_2017_extracted_constraints.py` |
| **5C-B (complete)** | `run_phase5c_upper_bound_consistency.py` — `M_tau_eff` vs `M_enclosed_23kpc`; no τ tuning; still `normalized_proxy` |
