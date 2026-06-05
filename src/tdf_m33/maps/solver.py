"""Sparse finite-difference solver for Phase 6F disk-plane tau field."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

import numpy as np
from scipy import sparse
from scipy.sparse.linalg import spsolve

BoundaryCondition = Literal["dirichlet", "neumann"]


@dataclass(frozen=True)
class SolverDiagnostics:
    residual_norm: float
    n_unknowns: int
    boundary_condition: str
    kappa_tau: float
    m_tau: float
    finite_fraction: float
    condition_estimate: float | None
    warning: str | None


def build_laplacian_2d(nx: int, ny: int, dx: float, dy: float) -> sparse.csr_matrix:
    """5-point discrete Laplacian on an nx x ny interior grid (row-major flatten)."""
    n = nx * ny
    rows: list[int] = []
    cols: list[int] = []
    data: list[float] = []

    def idx(i: int, j: int) -> int:
        return j * nx + i

    for j in range(ny):
        for i in range(nx):
            k = idx(i, j)
            rows.append(k)
            cols.append(k)
            data.append(-2.0 / dx**2 - 2.0 / dy**2)
            if i > 0:
                rows.append(k)
                cols.append(idx(i - 1, j))
                data.append(1.0 / dx**2)
            if i < nx - 1:
                rows.append(k)
                cols.append(idx(i + 1, j))
                data.append(1.0 / dx**2)
            if j > 0:
                rows.append(k)
                cols.append(idx(i, j - 1))
                data.append(1.0 / dy**2)
            if j < ny - 1:
                rows.append(k)
                cols.append(idx(i, j + 1))
                data.append(1.0 / dy**2)

    return sparse.csr_matrix((data, (rows, cols)), shape=(n, n))


def _apply_boundary(
    A: sparse.csr_matrix,
    b: np.ndarray,
    nx: int,
    ny: int,
    bc: BoundaryCondition,
) -> tuple[sparse.csr_matrix, np.ndarray]:
    """Apply Dirichlet (tau=0) or Neumann (zero normal gradient) on boundary."""
    A = A.tolil()
    b = b.copy()
    n = nx * ny

    def idx(i: int, j: int) -> int:
        return j * nx + i

    if bc == "dirichlet":
        boundary: set[int] = set()
        for j in range(ny):
            for i in range(nx):
                if i == 0 or i == nx - 1 or j == 0 or j == ny - 1:
                    boundary.add(idx(i, j))
        for k in boundary:
            A.rows[k] = [k]
            A.data[k] = [1.0]
            b[k] = 0.0
    elif bc == "neumann":
        raise NotImplementedError(
            "Neumann boundary condition is not yet scientifically validated for Phase 6F."
        )
    else:
        raise ValueError(f"Unknown boundary condition: {bc}")

    return A.tocsr(), b


def solve_tau_field(
    j_tau: np.ndarray,
    mask: np.ndarray,
    dx_kpc: float,
    dy_kpc: float,
    *,
    kappa_tau: float,
    m_tau: float,
    boundary_condition: BoundaryCondition = "dirichlet",
    boundary_taper: np.ndarray | None = None,
) -> tuple[np.ndarray, SolverDiagnostics]:
    """Solve kappa_tau * Laplacian(tau) - m_tau^2 * tau = J_tau on masked grid."""
    if kappa_tau <= 0:
        raise ValueError("kappa_tau must be positive")

    j = np.where(mask, j_tau, 0.0)
    if boundary_taper is not None:
        j = j * boundary_taper

    ny, nx = j.shape
    L = build_laplacian_2d(nx, ny, dx_kpc, dy_kpc)
    n = nx * ny
    I = sparse.identity(n, format="csr")
    A = kappa_tau * L - (m_tau**2) * I
    b = j.ravel()

    A, b = _apply_boundary(A, b, nx, ny, boundary_condition)

    try:
        tau_flat = spsolve(A, b)
    except Exception as exc:
        raise RuntimeError(f"Linear solve failed: {exc}") from exc

    tau = tau_flat.reshape(ny, nx)
    tau = np.where(mask, tau, np.nan)

    residual = A @ tau_flat - b
    res_norm = float(np.linalg.norm(residual))

    cond_est: float | None = None
    warning: str | None = None
    try:
        s_norm = float(np.linalg.norm(A.toarray(), ord=2))
        if s_norm > 0 and m_tau > 0:
            cond_est = s_norm  # lightweight proxy; full condition number omitted
    except Exception:
        warning = "Condition estimate unavailable"

    finite_frac = float(np.mean(np.isfinite(tau[mask]))) if mask.any() else 0.0

    diag = SolverDiagnostics(
        residual_norm=res_norm,
        n_unknowns=n,
        boundary_condition=boundary_condition,
        kappa_tau=kappa_tau,
        m_tau=m_tau,
        finite_fraction=finite_frac,
        condition_estimate=cond_est,
        warning=warning,
    )
    return tau, diag
