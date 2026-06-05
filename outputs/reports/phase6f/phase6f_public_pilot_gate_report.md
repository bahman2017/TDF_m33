# Phase 6F public pilot gate report (P1–P6)

**Claim label:** `PUBLIC_DATA_PILOT_NOT_CORBELLI_PRIMARY`
**public_pilot_ready:** `False`

**Not Corbelli 2014 primary reconstruction.** G1/G2/G8 Corbelli gates are separate.

| Gate | Status | Message |
|------|--------|---------|
| P1_public_hi_map_available | PENDING | No public HI FITS in hi_lglbs/ or hi_koch2018/. Manual download required (LGLBS or Koch 2018). |
| P2_public_stellar_irac_available | PENDING | No IRAC FITS staged (need 3.6 and 4.5 µm mosaics). IRAC proxy - not Corbelli BVIgi map. |
| P3_public_co_or_h2_available | PENDING | No CO(2-1) FITS in co_iram_lp006/. IRAM LP006 manual download. |
| P4_public_wcs_metadata_available | PENDING | No staged public pilot maps to verify WCS. |
| P5_public_license_and_citation_documented | PARTIAL | Registry citations and license notes documented; confirm per-file on download. |
| P6_public_reprojection_ready | FAIL | Validated public-pilot reprojection not implemented; PUBLIC_PILOT_REPROJECTION_AVAILABLE=False. |

**Blocked:** `PUBLIC_PILOT_NOT_READY_PENDING_DOWNLOADS_OR_REPROJECTION`
