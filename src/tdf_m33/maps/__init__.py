"""Phase 6F non-spherical disk-plane tau-map engine."""

from tdf_m33.maps.gates import GateReport, run_data_gates
from tdf_m33.maps.grid import DiskGrid, build_disk_grid
from tdf_m33.maps.tau_field import TauFieldResult

__all__ = [
    "DiskGrid",
    "GateReport",
    "TauFieldResult",
    "build_disk_grid",
    "run_data_gates",
]
