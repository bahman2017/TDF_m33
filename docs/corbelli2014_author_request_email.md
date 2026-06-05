# Draft email — Corbelli et al. 2014 primary M33 map request

**Status:** Draft for human review before sending. Verify recipient addresses from the published paper.

**To:** Elena Corbelli, David A. Thilker (and co-authors as appropriate)  
**Subject:** Request for M33 baryonic map products (Corbelli et al. 2014, A&A 572, A23) — reproducible τ-geometry test case

---

Dear Prof. Corbelli and Prof. Thilker,

I am writing to request access to the two-dimensional baryonic map products used in your M33 dynamical analysis (Corbelli et al. 2014, *A&A* 572, A23; DOI 10.1051/0004-6361/201424033).

I am developing a reproducible computational framework that uses **M33 as a test case** to evaluate whether the missing acceleration normally modeled with a dark-matter halo can be reconstructed as a smooth **τ-geometry field** constrained by observed baryonic structure. This is a methods and reproducibility study: **we do not claim that dark matter is disproven**, and we do not present lensing detections. Our goal is to test whether a mass-constrained, disk-plane field reconstruction can be carried out transparently from published baryonic inputs.

To proceed with validated, gate-controlled analysis, we would be grateful if you could share (or point us to a public archive for) the following products from your 2014 M33 work:

1. **Combined VLA + GBT H i surface-density map** (the primary map used in your dynamical model, not VLA-only products).
2. **BVIgi stellar surface-density or stellar mass map** (the 2D product underlying Figs. 2 and 12 / Table 1 stellar columns).
3. **2D H i velocity field**, if available in FITS form.
4. **Uncertainty maps, masks, or noise images** associated with the above, if available.

For each file, it would help us enormously if you could confirm or provide:

- FITS format with **WCS** (reference pixel, CD matrix, coordinate frame).
- **Units** (`BUNIT` or equivalent), including any H/He or M/L assumptions.
- **Beam size** and native **pixel scale**.
- **Calibration notes** (flux scale, masking philosophy).
- Assumed **distance**, **inclination**, and **position angle** if not fully encoded in the FITS headers.
- **Public download links** if the files are already hosted (CDS, institutional repository, etc.).

We will store received files under version-controlled paths in our open repository, record SHA-256 checksums, document provenance and license terms, and cite your paper in any derived analysis. Files will not be modified in place; any updates will be versioned explicitly.

If sharing the full maps is not possible, we would appreciate guidance on the most appropriate public archive entry or alternative contact for data access.

Thank you for your time and for the extensive M33 dataset your team has published.

Best regards,

[Your name]  
[Affiliation]  
[Contact email]  
[Repository URL: https://github.com/bahman2017/TDF_m33]

---

## Internal notes (do not send)

- Attach or link `docs/phase6f_corbelli_author_request_package.md` internally for tracking.
- Log response in `docs/extraction_log.md`.
- On receipt, follow `docs/phase6f_primary_data_receipt_protocol.md`.
