"""Tau field result container for Phase 6F."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np

from tdf_m33.maps.grid import DiskGrid
from tdf_m33.maps.solver import SolverDiagnostics
from tdf_m33.maps.sources import BaryonicSourceMaps


@dataclass(frozen=True)
class TauFieldResult:
    """Disk-plane tau field and associated metadata."""

    tau: np.ndarray
    grid: DiskGrid
    sources: BaryonicSourceMaps
    solver_diagnostics: SolverDiagnostics
    mode: str
    marker: str | None
    metadata: dict[str, Any]

    @property
    def is_reference_only(self) -> bool:
        return self.marker is not None
