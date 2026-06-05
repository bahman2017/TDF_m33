"""I/O utilities for Phase 6F maps."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import yaml


def load_phase6f_config(path: Path) -> dict[str, Any]:
    """Load Phase 6F YAML configuration."""
    with path.open(encoding="utf-8") as f:
        cfg = yaml.safe_load(f)
    if not isinstance(cfg, dict):
        raise ValueError(f"Invalid config at {path}")
    return cfg


def _parse_fits_header_block(block: bytes) -> dict[str, Any]:
    header: dict[str, Any] = {}
    for i in range(0, len(block), 80):
        card = block[i : i + 80].decode("ascii", errors="replace")
        if card.startswith("END"):
            break
        key = card[:8].strip()
        if not key:
            continue
        if "=" in card:
            val = card[10:].split("/", 1)[0].strip()
            if val.startswith("'") and val.endswith("'"):
                header[key] = val[1:-1].strip()
            else:
                try:
                    if "." in val or "E" in val.upper():
                        header[key] = float(val)
                    else:
                        header[key] = int(val)
                except ValueError:
                    header[key] = val
    return header


def read_fits_2d(path: Path) -> tuple[np.ndarray, dict[str, Any]]:
    """Read a simple 2D FITS image (primary HDU, no astropy dependency).

    Returns data array and metadata dict with WCS-related keys when present.
    """
    with path.open("rb") as f:
        header_blocks = b""
        while True:
            block = f.read(2880)
            if not block:
                raise ValueError(f"Unexpected EOF reading FITS header: {path}")
            header_blocks += block
            if b"END" in block:
                break
        header = _parse_fits_header_block(header_blocks)
        naxis = int(header.get("NAXIS", 0))
        if naxis < 2:
            raise ValueError(f"FITS {path} is not 2D (NAXIS={naxis})")
        shape = tuple(int(header[f"NAXIS{i}"]) for i in range(naxis, 0, -1))
        if len(shape) == 2:
            ny, nx = shape
        else:
            # squeeze leading degenerate axes
            ny, nx = shape[-2], shape[-1]
        bitpix = int(header.get("BITPIX", -32))
        dtype_map = {
            16: ">i2",
            32: ">i4",
            -32: ">f4",
            -64: ">f8",
        }
        if bitpix not in dtype_map:
            raise ValueError(f"Unsupported BITPIX={bitpix} in {path}")
        dtype = dtype_map[bitpix]
        itemsize = np.dtype(dtype).itemsize
        offset = len(header_blocks)
        n_pixels = ny * nx
        raw = f.read(n_pixels * itemsize)
        data = np.frombuffer(raw, dtype=dtype, count=n_pixels).reshape(ny, nx)
        bscale = float(header.get("BSCALE", 1.0))
        bzero = float(header.get("BZERO", 0.0))
        data = data * bscale + bzero
        data = data.astype(np.float64)

    wcs = {
        "has_wcs": all(k in header for k in ("CRVAL1", "CRVAL2", "CDELT1", "CDELT2")),
        "ctype1": header.get("CTYPE1"),
        "ctype2": header.get("CTYPE2"),
        "crval1": header.get("CRVAL1"),
        "crval2": header.get("CRVAL2"),
        "cdelt1": header.get("CDELT1"),
        "cdelt2": header.get("CDELT2"),
        "bunit": header.get("BUNIT"),
        "bmaj": header.get("BMAJ"),
        "bmin": header.get("BMIN"),
        "object": header.get("OBJECT"),
        "path": str(path),
    }
    return data, wcs


def write_gate_status_csv(rows: list[dict[str, Any]], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    df = pd.DataFrame(rows)
    df.to_csv(path, index=False)


def write_markdown_report(lines: list[str], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def save_tau_map_npz(
    path: Path,
    arrays: dict[str, np.ndarray],
    metadata: dict[str, Any],
    *,
    reference_only: bool = False,
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    meta_arr = np.array(
        [
            metadata.get("mode", "unknown"),
            "REFERENCE_ONLY_NOT_FOR_SCIENTIFIC_CLAIMS" if reference_only else "scientific",
        ],
        dtype=object,
    )
    np.savez_compressed(path, **arrays, metadata_json=str(metadata), mode=meta_arr)
