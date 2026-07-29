"""
FINCH validation — textbook fin equation and grid convergence.

Provides run_fin_test() used by figures.py to produce the validation
plots. The actual validation suite is in validate2.py.
"""

import numpy as np
from physics import Material, solve, analytical_fin


def run_fin_test(nx, mat=None, verbose=False):
    """Run a single fin validation test at grid resolution nx.

    Builds a straight fin of length L = 20 mm at a fixed base temperature
    and compares the numerical temperature profile to the analytical
    fin equation.

    Returns a dict with keys: nx, x, T_num, T_ana, max_err.
    """
    if mat is None:
        mat = Material()

    L = 0.020                     # fin length, 20 mm
    dx = L / nx
    ny = 4                        # 4 cells tall, one row of metal

    mask = np.zeros((ny, nx), dtype=bool)
    mask[:, :] = True

    dirichlet = np.zeros((ny, nx), dtype=bool)
    dirichlet[:, 0] = True        # left face is fixed-temperature boundary
    T_base = 100.0                # base temperature, degC

    Q = np.zeros((ny, nx))

    T = solve(mask, mat, dx, Q=Q, dirichlet=dirichlet, T_base=T_base)

    x = dx * np.arange(nx)
    T_num = T[ny // 2, :]
    T_ana = analytical_fin(x, L, mat, T_base)

    diff = np.abs(T_num - T_ana)
    excess = T_base - mat.T_inf   # base temperature excess above ambient
    max_err_pct = 100.0 * np.max(diff) / max(excess, 1e-12)

    if verbose:
        print(f"  nx={nx:4d}  dx={dx*1000:.4f} mm  "
              f"max error={max_err_pct:.4f}%")

    return {
        "nx": nx,
        "x": x,
        "T_num": T_num,
        "T_ana": T_ana,
        "max_err": max_err_pct,
        "diff": diff,
    }


def run_validation_suite():
    """Run the full grid convergence test."""
    mat = Material()
    print("Fin validation — grid convergence")
    print(f"{'Cells':>6}  {'dx (mm)':>9}  {'Max error (%)':>14}")
    print("-" * 33)
    results = []
    for nx in (10, 20, 40, 80, 160, 320):
        r = run_fin_test(nx, mat=mat, verbose=False)
        results.append(r)
        print(f"{r['nx']:6d}  {1000*0.020/r['nx']:9.4f}  {r['max_err']:14.4f}")
    # Check order of convergence
    if len(results) >= 2:
        ratios = []
        for i in range(1, len(results)):
            ratio = results[i-1]["max_err"] / max(results[i]["max_err"], 1e-15)
            ratios.append(ratio)
        avg_ratio = np.mean(ratios)
        print(f"\nMean error ratio per halving: {avg_ratio:.2f}  "
              f"(expected ~4 for 2nd-order)")
        if 3.0 <= avg_ratio <= 5.0:
            print("✅  Second-order convergence confirmed")
        else:
            print("⚠️  Convergence rate outside expected range")
    return results


if __name__ == "__main__":
    run_validation_suite()
