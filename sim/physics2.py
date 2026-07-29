"""
FINCH physics, version 2
========================

Fixes five of the eight limitations listed in the original write up.

WHAT CHANGED AND WHY
--------------------

L2/L3  The old trapped-air model was a box average of nearby air ("openness")
       multiplied by a guessed 15% floor and a guessed 3 cell radius. Both
       numbers were invented. Replaced with a channel starvation model whose
       only length scale is DERIVED, not guessed:

           s_c = 2 * h_iso * L / (rho * u * cp)

       This is the gap width at which the air flowing through a channel has
       absorbed roughly all the heat it can carry (NTU = 1). Below it the
       channel is thermally starved; above it the surface behaves like an
       isolated plate. It follows the same reasoning as the Bar-Cohen and
       Rohsenow composite treatment of parallel plate channels, which blends
       a fully developed limit with an isolated plate limit.

           h_eff(s) = h_iso * (1 - exp(-s / s_c))

       s -> 0  gives h_eff -> h_iso * s/s_c -> 0   (buried metal, dead air)
       s -> inf gives h_eff -> h_iso              (exposed metal, full cooling)

       The local gap width s is measured properly with a Euclidean distance
       transform of the air region, not a box blur.

L4     Radiation added. Every surface radiates:

           q_rad = eps * sigma * (T^4 - T_inf^4)

       linearised into an equivalent coefficient

           h_rad = eps * sigma * (T^2 + T_inf^2) * (T + T_inf)

       which depends on T, so the solve is iterated to convergence. At 200 C
       with eps = 0.85 this is worth about 10 W/m2K, which is the same order
       as still air convection, so ignoring it was a real error.

L5     Transient mode added. The steady state assumption is kept as the
       default because it is what heat sinks are specified on, but
       solve_transient() integrates the heat equation in time so thermal mass
       and warm up can be shown.

L7     Grid independence is now testable at 32, 44, 64 and 88 cells, and
       validate2.py reports how much the answer moves.

STILL NOT FIXED
---------------
L1     Two dimensional. A real sink is 3D.
L6     Manufacturability is still a soft penalty.
L8     Nothing has been physically built and measured.
"""

import numpy as np
import scipy.sparse as sp
import scipy.sparse.linalg as spla
from scipy.ndimage import distance_transform_edt

SIGMA = 5.670374419e-8      # Stefan Boltzmann, W/(m^2 K^4)


class Air:
    """Properties of air at about 40 C, used for the channel model."""
    rho = 1.13          # kg/m3
    cp = 1006.0         # J/(kg K)
    k = 0.0271          # W/(m K)
    nu = 1.70e-5        # m2/s
    beta = 1.0 / 313.0  # 1/K
    g = 9.81


class Material2:
    """Everything the solver needs to know about the physical setup.

    k      thermal conductivity of the metal, W/(m K)
    t_z    plate thickness, m
    h_iso  convection coefficient for a fully exposed surface, W/(m^2 K)
    T_inf  ambient temperature, degC
    emis   surface emissivity, 0 for none, 0.85 for anodised aluminium
    u_air  air speed past the sink, m/s. 0 means natural convection and the
           speed is then estimated from buoyancy.
    L_flow flow path length through the sink, m
    """

    def __init__(self, k=205.0, t_z=0.001, h_iso=25.0, T_inf=35.0,
                 emis=0.0, u_air=0.0, L_flow=0.033):
        self.k = k
        self.t_z = t_z
        self.h_iso = h_iso
        self.T_inf = T_inf
        self.emis = emis
        self.u_air = u_air
        self.L_flow = L_flow

    @property
    def m(self):
        """Fin parameter, 1/m. 1/m is how far heat usefully travels."""
        return np.sqrt(2.0 * self.h_iso / (self.k * self.t_z))

    def air_speed(self, dT=60.0):
        """Air speed. If no fan, estimate the buoyancy driven speed."""
        if self.u_air > 0:
            return self.u_air
        # free convection scale: u ~ sqrt(g beta dT L)
        return np.sqrt(Air.g * Air.beta * max(dT, 1.0) * self.L_flow)

    def choke_gap(self, dT=60.0):
        """s_c, the gap width at which a channel becomes thermally starved.

        Derived from an energy balance on the channel, NTU = 1:
            h * (2 L)  =  rho * u * s * cp
        so
            s_c = 2 h L / (rho u cp)
        """
        u = self.air_speed(dT)
        return 2.0 * self.h_iso * self.L_flow / (Air.rho * u * Air.cp)

    def __repr__(self):
        return (f"Material2(k={self.k}, t_z={self.t_z*1000:.2f}mm, "
                f"h_iso={self.h_iso}, emis={self.emis}, "
                f"1/m={1000/self.m:.1f}mm, s_c={self.choke_gap()*1000:.2f}mm)")


# ----------------------------------------------------------------------
# Geometry: how wide is the air channel next to each piece of metal
# ----------------------------------------------------------------------

def gap_width(mask, dx):
    """Local air gap width next to every metal cell, in metres.

    Uses a Euclidean distance transform of the air region. For an air cell,
    the transform gives its distance to the nearest metal. The widest point
    of a channel is therefore half the channel width, so gap = 2 * distance.

    For each metal cell we take the largest gap among its touching air cells,
    because that is the channel the metal actually breathes through. Metal
    with no touching air at all is fully interior and gets gap 0.
    """
    ny, nx = mask.shape
    air = ~mask
    if not air.any():
        return np.zeros_like(mask, dtype=float)

    # distance from each air cell to the nearest metal, in cells
    dist = distance_transform_edt(air)

    # a cell outside the plate is open air, so pad generously
    gap = np.zeros((ny, nx), dtype=float)
    for di, dj in ((-1, 0), (1, 0), (0, -1), (0, 1)):
        nb = np.zeros((ny, nx))
        nbair = np.zeros((ny, nx), dtype=bool)
        i0, i1 = max(0, -di), min(ny, ny - di)
        j0, j1 = max(0, -dj), min(nx, nx - dj)
        nb[i0:i1, j0:j1] = dist[i0 + di:i1 + di, j0 + dj:j1 + dj]
        nbair[i0:i1, j0:j1] = air[i0 + di:i1 + di, j0 + dj:j1 + dj]
        # cells that fall off the edge of the grid see open air
        edge = np.ones((ny, nx), dtype=bool)
        edge[i0:i1, j0:j1] = False
        nb = np.where(edge, dist.max() if dist.size else 1.0, nb)
        nbair = nbair | edge
        gap = np.maximum(gap, np.where(nbair, nb, 0.0))

    return 2.0 * gap * dx * mask


def h_convect(mask, mat, dx, dT=60.0):
    """Convection coefficient per cell, reduced where the channel is narrow.

        h_eff(s) = h_iso * (1 - exp(-s / s_c))

    s_c comes from Material2.choke_gap and is a derived length, not a guess.
    """
    s = gap_width(mask, dx)
    s_c = mat.choke_gap(dT)
    return mat.h_iso * (1.0 - np.exp(-s / max(s_c, 1e-9)))


def h_radiate(T, mat):
    """Linearised radiation coefficient, W/(m^2 K).

        q = eps sigma (T^4 - Tinf^4)
          = [eps sigma (T^2 + Tinf^2)(T + Tinf)] * (T - Tinf)
                     ^^^^^^^^^^^^^^^^^^^^^^^^^^ this bracket is h_rad
    """
    if mat.emis <= 0:
        return np.zeros_like(T)
    Tk = np.nan_to_num(T, nan=mat.T_inf) + 273.15
    Ik = mat.T_inf + 273.15
    return mat.emis * SIGMA * (Tk * Tk + Ik * Ik) * (Tk + Ik)


# ----------------------------------------------------------------------
# Steady state solver
# ----------------------------------------------------------------------

def solve2(mask, mat, dx, Q=None, dirichlet=None, T_base=None,
           channel=True, radiation=True, iters=12, tol=1e-3, T0=None,
           h_conv=None):
    """Steady state temperature field.

    Because radiation depends on T^4 the system is non linear, so we solve
    it repeatedly, updating h_rad from the previous temperature, until it
    stops moving. Convection is linear so it only needs computing once.
    """
    ny, nx = mask.shape
    if Q is None:
        Q = np.zeros((ny, nx))

    idx = -np.ones((ny, nx), dtype=np.int64)
    cells = np.argwhere(mask)
    for n, (i, j) in enumerate(cells):
        idx[i, j] = n
    N = len(cells)
    if N == 0:
        return np.full((ny, nx), np.nan)

    G_cond = mat.k * mat.t_z
    G_dir = 2.0 * mat.k * mat.t_z

    if h_conv is None:
        if channel:
            h_conv = h_convect(mask, mat, dx)
        else:
            h_conv = np.full((ny, nx), mat.h_iso)

    # Warm starting from a previous temperature field cuts the number of
    # radiation sweeps from about 12 to about 3, because h_rad is already
    # close to correct on the first pass.
    if T0 is not None:
        T = np.where(mask, np.nan_to_num(T0, nan=mat.T_inf), mat.T_inf)
    else:
        T = np.full((ny, nx), mat.T_inf, dtype=float)

    for sweep in range(iters):
        h_rad = h_radiate(T, mat) if radiation else np.zeros((ny, nx))
        h_tot = h_conv + h_rad
        G_conv = 2.0 * h_tot * dx * dx

        rows, cols, vals = [], [], []
        rhs = np.zeros(N)
        for n, (i, j) in enumerate(cells):
            gc = G_conv[i, j]
            diag = gc
            rhs[n] = gc * mat.T_inf + Q[i, j]
            for di, dj in ((-1, 0), (1, 0), (0, -1), (0, 1)):
                ii, jj = i + di, j + dj
                if 0 <= ii < ny and 0 <= jj < nx and mask[ii, jj]:
                    diag += G_cond
                    rows.append(n); cols.append(idx[ii, jj]); vals.append(-G_cond)
            if dirichlet is not None and dirichlet[i, j]:
                diag += G_dir
                rhs[n] += G_dir * T_base
            rows.append(n); cols.append(n); vals.append(diag)

        A = sp.csr_matrix((vals, (rows, cols)), shape=(N, N))
        x = spla.spsolve(A, rhs)

        Tn = np.full((ny, nx), np.nan)
        for n, (i, j) in enumerate(cells):
            Tn[i, j] = x[n]

        move = np.nanmax(np.abs(Tn - T)[mask]) if mask.any() else 0.0
        T = np.where(mask, Tn, mat.T_inf)
        if not radiation or move < tol:
            break

    out = np.full((ny, nx), np.nan)
    out[mask] = T[mask]
    return out


# ----------------------------------------------------------------------
# Transient solver, fixes limitation 5
# ----------------------------------------------------------------------

def solve_transient(mask, mat, dx, Q, t_end=120.0, dt=None,
                    rho_cp=2.42e6, channel=True, radiation=True, n_out=40):
    """Warm up curve. rho_cp default is aluminium, 2700 * 897 J/(m3 K).

    Explicit Euler with a stability limited step, which is fine here because
    the grid is small and we only need a curve, not production accuracy.
    """
    ny, nx = mask.shape
    C = rho_cp * mat.t_z * dx * dx          # heat capacity of one cell, J/K
    G_cond = mat.k * mat.t_z
    h_conv = (h_convect(mask, mat, dx) if channel
              else np.full((ny, nx), mat.h_iso))

    if dt is None:
        gmax = 4 * G_cond + 2 * (h_conv.max() + 8.0) * dx * dx
        dt = 0.4 * C / max(gmax, 1e-9)

    T = np.full((ny, nx), mat.T_inf, dtype=float)
    steps = max(1, int(t_end / dt))
    every = max(1, steps // n_out)
    times, peaks = [], []

    for s in range(steps + 1):
        h_rad = h_radiate(T, mat) if radiation else 0.0
        h_tot = h_conv + h_rad
        flow = np.zeros((ny, nx))
        for di, dj in ((-1, 0), (1, 0), (0, -1), (0, 1)):
            nb = np.zeros((ny, nx)); nbm = np.zeros((ny, nx), dtype=bool)
            i0, i1 = max(0, -di), min(ny, ny - di)
            j0, j1 = max(0, -dj), min(nx, nx - dj)
            nb[i0:i1, j0:j1] = T[i0 + di:i1 + di, j0 + dj:j1 + dj]
            nbm[i0:i1, j0:j1] = mask[i0 + di:i1 + di, j0 + dj:j1 + dj]
            flow += G_cond * (nb - T) * (nbm & mask)
        loss = 2.0 * h_tot * dx * dx * (T - mat.T_inf) * mask
        T = T + dt / C * (flow - loss + Q * mask)
        T = np.where(mask, T, mat.T_inf)
        if s % every == 0:
            times.append(s * dt)
            peaks.append(float(np.nanmax(np.where(mask, T, np.nan))))

    return np.array(times), np.array(peaks), T


# ----------------------------------------------------------------------
# Analytical references for validation
# ----------------------------------------------------------------------

def analytical_fin(x, L, mat, T_base):
    """Textbook fin, fixed base, adiabatic tip."""
    m = mat.m
    return mat.T_inf + (T_base - mat.T_inf) * np.cosh(m * (L - x)) / np.cosh(m * L)


def analytical_plate_radiation(Q, area, mat, tol=1e-10):
    """An isothermal plate losing heat only by radiation from both faces.

    Solve  Q = 2 A eps sigma (T^4 - Tinf^4)  for T, by bisection.
    """
    Ik = mat.T_inf + 273.15
    lo, hi = Ik, Ik + 5000.0
    for _ in range(300):
        mid = 0.5 * (lo + hi)
        q = 2 * area * mat.emis * SIGMA * (mid ** 4 - Ik ** 4)
        if q < Q:
            lo = mid
        else:
            hi = mid
        if hi - lo < tol:
            break
    return 0.5 * (lo + hi) - 273.15
