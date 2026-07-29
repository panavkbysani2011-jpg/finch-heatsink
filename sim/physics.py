"""
FINCH - 2D thermal solver
=========================

The physics model, in one paragraph:

We model a THIN FLAT PLATE lying in the x-y plane, of thickness t_z into the
page. Some cells of the grid contain metal, others are empty (air, which we
treat as a perfect insulator - a simplification, see limitations).

Heat moves through the metal by CONDUCTION (in-plane, cell to cell) and leaves
the plate by CONVECTION from its two large faces (front and back) into ambient
air at T_inf.

Steady-state energy balance for one metal cell (i, j):

    sum over metal neighbours:  G_cond * (T_neighbour - T_cell)
      + (if touching a fixed-temperature boundary) G_dir * (T_base - T_cell)
      - 2 * h * dx^2 * (T_cell - T_inf)          <-- convection, 2 faces
      + Q_cell                                    <-- heat injected (watts)
      = 0

Conductance between two adjacent metal cells:
    face area = dx * t_z, distance between centres = dx
    G_cond = k * (dx * t_z) / dx = k * t_z        <-- independent of dx!

Conductance from a cell centre to a Dirichlet boundary on its face:
    distance is only dx/2, so G_dir = 2 * k * t_z

This is the classic "extended surface" / fin model. Its 1D analytical solution
is in every heat transfer textbook, which is exactly why we can validate
against it (see validate.py).
"""

import numpy as np
import scipy.sparse as sp
import scipy.sparse.linalg as spla
from scipy.ndimage import uniform_filter


class Material:
    """Thermal properties. Defaults are aluminium, the usual heat sink metal."""

    def __init__(self, k=205.0, t_z=0.001, h=25.0, T_inf=35.0):
        self.k = k          # thermal conductivity, W/(m.K)   aluminium ~205
        self.t_z = t_z      # plate thickness, m               1 mm
        self.h = h          # convection coefficient, W/(m^2.K)
        self.T_inf = T_inf  # ambient air temperature, degC    35 = Bengaluru summer

    @property
    def m(self):
        """Fin parameter m = sqrt(2h / (k * t_z)), units 1/m.

        1/m is the characteristic length over which a fin cools down.
        If your fin is much shorter than 1/m it is nearly isothermal and
        adding length barely helps.
        """
        return np.sqrt(2.0 * self.h / (self.k * self.t_z))

    def __repr__(self):
        return (f"Material(k={self.k}, t_z={self.t_z*1000:.1f}mm, "
                f"h={self.h}, T_inf={self.T_inf}, 1/m={1000/self.m:.1f}mm)")


def openness(mask, radius=3):
    """How much open air surrounds each cell, 0 (buried) to 1 (fully exposed).

    A box average of the AIR field. A cell deep inside a solid lump sees
    almost no air nearby -> openness ~ 0. A cell on an exposed thin fin has
    air on most sides -> openness ~ 1.
    """
    air = (~mask).astype(float)
    return uniform_filter(air, size=2 * radius + 1, mode="constant", cval=1.0)


def h_field(mask, mat, radius=3, h_min_frac=0.15, power=1.0):
    """Spatially varying convection coefficient - crude airflow occlusion.

    THE PROBLEM THIS ADDRESSES
    --------------------------
    Treating h as one constant everywhere is the single biggest weakness of
    the flat model. It tells the optimiser that metal buried in the middle
    of a solid lump sheds heat exactly as well as metal on an exposed fin.
    That is false: packed geometry chokes the airflow between features, so
    buried surface sits in near-stagnant air.

    THE MODEL
    ---------
        h_local = h * (h_min_frac + (1 - h_min_frac) * openness^power)

    so a fully buried cell keeps only h_min_frac of the nominal coefficient
    and a fully exposed cell keeps all of it.

    HONESTY
    -------
    This is a first-order geometric proxy, not CFD. It has no flow direction,
    no boundary layers, no Reynolds number. Its value is that it lets us ask
    a falsifiable question: does the compact-blob result survive when
    burying metal is penalised? If the answer is no, the blob was an artifact
    of assuming constant h.
    """
    phi = openness(mask, radius=radius)
    return mat.h * (h_min_frac + (1.0 - h_min_frac) * phi ** power)


def solve(mask, mat, dx, Q=None, dirichlet=None, T_base=None, h_map=None):
    """Solve steady-state temperature field.

    Parameters
    ----------
    mask : (ny, nx) bool array
        True where metal is present.
    mat : Material
    dx : float
        Cell size in metres (square cells).
    Q : (ny, nx) float array, optional
        Heat injected into each cell, in watts.
    dirichlet : (ny, nx) bool array, optional
        Cells whose LEFT face touches a fixed-temperature boundary.
        (Used only for validation against the textbook fin.)
    T_base : float, optional
        The fixed boundary temperature, degC.

    Returns
    -------
    T : (ny, nx) float array
        Temperature in degC. NaN where there is no metal.
    """
    ny, nx = mask.shape
    if Q is None:
        Q = np.zeros((ny, nx))

    # Give every metal cell an index in the linear system
    idx = -np.ones((ny, nx), dtype=np.int64)
    cells = np.argwhere(mask)
    for n, (i, j) in enumerate(cells):
        idx[i, j] = n
    N = len(cells)
    if N == 0:
        return np.full((ny, nx), np.nan)

    G_cond = mat.k * mat.t_z            # cell <-> cell
    G_dir = 2.0 * mat.k * mat.t_z       # cell <-> fixed-T boundary
    if h_map is None:
        G_conv_map = np.full(mask.shape, 2.0 * mat.h * dx * dx)
    else:
        G_conv_map = 2.0 * h_map * dx * dx

    rows, cols, vals = [], [], []
    rhs = np.zeros(N)

    for n, (i, j) in enumerate(cells):
        G_conv = G_conv_map[i, j]
        diag = G_conv
        rhs[n] = G_conv * mat.T_inf + Q[i, j]

        # four in-plane neighbours
        for di, dj in ((-1, 0), (1, 0), (0, -1), (0, 1)):
            ii, jj = i + di, j + dj
            if 0 <= ii < ny and 0 <= jj < nx and mask[ii, jj]:
                diag += G_cond
                rows.append(n); cols.append(idx[ii, jj]); vals.append(-G_cond)
            # else: adiabatic edge, contributes nothing

        # fixed-temperature boundary on the left face
        if dirichlet is not None and dirichlet[i, j]:
            diag += G_dir
            rhs[n] += G_dir * T_base

        rows.append(n); cols.append(n); vals.append(diag)

    A = sp.csr_matrix((vals, (rows, cols)), shape=(N, N))
    x = spla.spsolve(A, rhs)

    T = np.full((ny, nx), np.nan)
    for n, (i, j) in enumerate(cells):
        T[i, j] = x[n]
    return T


def solve_iterative(mask, mat, dx, Q=None, dirichlet=None, T_base=None,
                    iters=4000, omega=None, tol=1e-7):
    """Same problem, solved by RED-BLACK SOR.

    This is the method the browser version uses (a direct sparse solve is not
    practical in JavaScript). We check it against solve() so we know the fast
    method and the accurate method agree.

    ---------------------------------------------------------------------
    DEBUG NOTE - 27 Jul, and worth keeping in the journal.

    My first attempt used JACOBI iteration with over-relaxation omega=1.8.
    It diverged spectacularly: 10 sweeps -> 2849 degC, 40 sweeps -> 1e14,
    then NaN.

    Why: over-relaxation (omega > 1) is only stable for GAUSS-SEIDEL, which
    uses already-updated neighbour values within the same sweep. Jacobi uses
    only old values, so omega > 1 overshoots and the error is amplified every
    sweep instead of damped.

    Plain Jacobi (omega = 1) is stable here because the matrix is diagonally
    dominant - but it is far too slow. In this problem
        G_cond / G_conv ~ 10,000
    so conduction dominates and the system is essentially a Laplace equation,
    which Jacobi converges on at a rate ~ 1 - O(1/N^2). Hundreds of thousands
    of sweeps.

    Fix: RED-BLACK ordering. Colour the grid like a chessboard. A red cell's
    four neighbours are all black and vice versa, so all red cells can be
    updated simultaneously using black values, then all black cells using the
    freshly-updated red values. That IS Gauss-Seidel - so omega > 1 is now
    legal - but each half-sweep is a single vectorised array operation, which
    is exactly what numpy and JavaScript typed arrays are good at.
    ---------------------------------------------------------------------
    """
    ny, nx = mask.shape
    if Q is None:
        Q = np.zeros((ny, nx))

    G_cond = mat.k * mat.t_z
    G_dir = 2.0 * mat.k * mat.t_z
    G_conv = 2.0 * mat.h * dx * dx

    # Optimal SOR factor for a Poisson-like problem on an n-cell grid
    if omega is None:
        n_eff = max(nx, ny)
        omega = 2.0 / (1.0 + np.sin(np.pi / max(n_eff, 2)))
        omega = min(omega, 1.99)

    # Diagonal = sum of every conductance leaving the cell
    nbr_count = np.zeros((ny, nx))
    for di, dj in ((-1, 0), (1, 0), (0, -1), (0, 1)):
        shifted = np.zeros((ny, nx), dtype=bool)
        i0, i1 = max(0, -di), min(ny, ny - di)
        j0, j1 = max(0, -dj), min(nx, nx - dj)
        shifted[i0:i1, j0:j1] = mask[i0 + di:i1 + di, j0 + dj:j1 + dj]
        nbr_count += (shifted & mask)

    diag = G_conv + G_cond * nbr_count
    if dirichlet is not None:
        diag = diag + G_dir * dirichlet
    diag = np.where(mask, diag, 1.0)          # avoid divide-by-zero off-metal

    b = G_conv * mat.T_inf + Q
    if dirichlet is not None:
        b = b + G_dir * T_base * dirichlet

    # chessboard colouring
    ii, jj = np.indices((ny, nx))
    red = ((ii + jj) % 2 == 0) & mask
    black = ((ii + jj) % 2 == 1) & mask

    T = np.where(mask, mat.T_inf, 0.0).astype(float)

    def neighbour_sum(Tc):
        acc = np.zeros((ny, nx))
        for di, dj in ((-1, 0), (1, 0), (0, -1), (0, 1)):
            nb_T = np.zeros((ny, nx))
            nb_M = np.zeros((ny, nx), dtype=bool)
            i0, i1 = max(0, -di), min(ny, ny - di)
            j0, j1 = max(0, -dj), min(nx, nx - dj)
            nb_T[i0:i1, j0:j1] = Tc[i0 + di:i1 + di, j0 + dj:j1 + dj]
            nb_M[i0:i1, j0:j1] = mask[i0 + di:i1 + di, j0 + dj:j1 + dj]
            acc += G_cond * nb_T * nb_M
        return acc

    for it in range(iters):
        T_prev = T.copy()
        for colour in (red, black):
            T_star = (b + neighbour_sum(T)) / diag
            T = np.where(colour, T + omega * (T_star - T), T)
        if it % 20 == 0:
            delta = np.max(np.abs(T - T_prev)[mask]) if mask.any() else 0.0
            if delta < tol:
                break

    out = np.full((ny, nx), np.nan)
    out[mask] = T[mask]
    return out


def analytical_fin(x, L, mat, T_base):
    """Textbook 1D fin: fixed base temperature, adiabatic tip.

        theta(x) / theta_base = cosh(m(L - x)) / cosh(mL)

    where theta = T - T_inf. This is the equation our simulator has to
    reproduce before any of its other answers can be trusted.
    """
    m = mat.m
    theta_b = T_base - mat.T_inf
    return mat.T_inf + theta_b * np.cosh(m * (L - x)) / np.cosh(m * L)


def analytical_fin_heat(L, mat, depth, T_base):
    """Total heat dissipated by that same fin, in watts.

        q = sqrt(2 h k t_z) * theta_base * tanh(mL)   per unit depth
    """
    m = mat.m
    theta_b = T_base - mat.T_inf
    q_per_depth = np.sqrt(2.0 * mat.h * mat.k * mat.t_z) * theta_b * np.tanh(m * L)
    return q_per_depth * depth
