"""
FINCH - SC1 VALIDATION
======================

Before claiming any evolved design is "better", the simulator must reproduce
physics that was settled long before I was born.

Test: a plain rectangular fin, held at a fixed temperature at its base,
losing heat by convection along its length. The analytical solution is the
standard fin equation:

    (T(x) - T_inf) / (T_base - T_inf) = cosh(m(L-x)) / cosh(mL),
    m = sqrt(2h / (k * t_z))

If my grid solver cannot match this within 5%, nothing downstream is
trustworthy.
"""

import numpy as np
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from physics import Material, solve, solve_iterative, analytical_fin, analytical_fin_heat


def run_fin_test(nx, L=0.05, width=0.006, mat=None, T_base=100.0, verbose=True):
    """Discretise a straight fin of length L and compare to theory."""
    if mat is None:
        mat = Material()

    dx = L / nx
    ny = max(1, int(round(width / dx)))

    mask = np.ones((ny, nx), dtype=bool)
    dirichlet = np.zeros((ny, nx), dtype=bool)
    dirichlet[:, 0] = True          # base is the left face of column 0

    T = solve(mask, mat, dx, dirichlet=dirichlet, T_base=T_base)

    # cell centres measured from the base plane
    x_centres = (np.arange(nx) + 0.5) * dx
    T_num = T.mean(axis=0)                       # average across the width
    T_ana = analytical_fin(x_centres, L, mat, T_base)

    theta_num = T_num - mat.T_inf
    theta_ana = T_ana - mat.T_inf
    err = np.abs(theta_num - theta_ana) / theta_ana[0] * 100.0   # % of base excess

    max_err = err.max()
    tip_err = abs(theta_num[-1] - theta_ana[-1]) / theta_ana[-1] * 100.0

    if verbose:
        print(f"  nx={nx:4d}  dx={dx*1000:6.3f}mm   "
              f"max_err={max_err:6.3f}%   tip_err={tip_err:6.3f}%")

    return dict(nx=nx, dx=dx, max_err=max_err, tip_err=tip_err,
                T_num=T_num, T_ana=T_ana, x=x_centres, mat=mat)


def run_heat_test(nx, L=0.05, width=0.006, mat=None, T_base=100.0):
    """Check total dissipated heat, not just the temperature profile."""
    if mat is None:
        mat = Material()
    dx = L / nx
    ny = max(1, int(round(width / dx)))
    mask = np.ones((ny, nx), dtype=bool)
    dirichlet = np.zeros((ny, nx), dtype=bool)
    dirichlet[:, 0] = True

    T = solve(mask, mat, dx, dirichlet=dirichlet, T_base=T_base)

    # numerical: total convective loss from both faces
    q_num = np.nansum(2.0 * mat.h * dx * dx * (T - mat.T_inf))
    # analytical: fin of depth = ny*dx
    q_ana = analytical_fin_heat(L, mat, ny * dx, T_base)
    err = abs(q_num - q_ana) / q_ana * 100.0
    return q_num, q_ana, err


def main():
    mat = Material()
    print("=" * 68)
    print("FINCH  -  SC1 SIMULATOR VALIDATION")
    print("=" * 68)
    print(f"\nMaterial: {mat}")
    print(f"Fin parameter m = {mat.m:.2f} 1/m   ->  1/m = {1000/mat.m:.1f} mm")
    print("\nTest case: straight aluminium fin, L=50mm, base held at 100 degC,")
    print("ambient 35 degC, adiabatic tip.\n")

    print("-" * 68)
    print("TEST 1  Temperature profile vs. analytical fin equation")
    print("-" * 68)
    results = []
    for nx in (10, 20, 40, 80, 160, 320):
        results.append(run_fin_test(nx, mat=mat))

    print("\n  Grid convergence (error should fall as dx falls):")
    for a, b in zip(results[:-1], results[1:]):
        ratio = a['max_err'] / b['max_err'] if b['max_err'] > 1e-12 else float('inf')
        print(f"    nx {a['nx']:3d} -> {b['nx']:3d}   "
              f"error {a['max_err']:6.3f}% -> {b['max_err']:6.3f}%   "
              f"reduction x{ratio:.2f}")

    print("\n" + "-" * 68)
    print("TEST 2  Total dissipated heat vs. analytical")
    print("-" * 68)
    for nx in (20, 40, 80, 160):
        q_num, q_ana, err = run_heat_test(nx, mat=mat)
        print(f"  nx={nx:4d}   q_sim={q_num:8.4f} W   "
              f"q_theory={q_ana:8.4f} W   err={err:6.3f}%")

    print("\n" + "-" * 68)
    print("TEST 3  Robustness across different materials and conditions")
    print("-" * 68)
    cases = [
        ("Aluminium, still air",   Material(k=205, t_z=0.001, h=10,  T_inf=35)),
        ("Aluminium, forced air",  Material(k=205, t_z=0.001, h=50,  T_inf=35)),
        ("Copper, still air",      Material(k=400, t_z=0.001, h=10,  T_inf=35)),
        ("Steel, forced air",      Material(k=50,  t_z=0.001, h=50,  T_inf=35)),
        ("Thin aluminium foil",    Material(k=205, t_z=0.0002, h=25, T_inf=35)),
        ("Thick aluminium plate",  Material(k=205, t_z=0.005, h=25,  T_inf=35)),
    ]
    all_ok = True
    for name, m in cases:
        r = run_fin_test(160, mat=m, verbose=False)
        ok = r['max_err'] < 5.0
        all_ok &= ok
        flag = "PASS" if ok else "FAIL"
        print(f"  {flag}  {name:24s}  max_err={r['max_err']:6.3f}%   "
              f"(1/m = {1000/m.m:5.1f}mm)")

    print("\n" + "-" * 68)
    print("TEST 4  Iterative solver (the one used in the browser)")
    print("        must agree with the direct sparse solve")
    print("-" * 68)
    nx, L, width = 80, 0.05, 0.006
    dx = L / nx
    ny = max(1, int(round(width / dx)))
    mask = np.ones((ny, nx), dtype=bool)
    dirichlet = np.zeros((ny, nx), dtype=bool)
    dirichlet[:, 0] = True
    T_direct = solve(mask, mat, dx, dirichlet=dirichlet, T_base=100.0)
    T_iter = solve_iterative(mask, mat, dx, dirichlet=dirichlet, T_base=100.0,
                             iters=6000)
    diff = np.nanmax(np.abs(T_direct - T_iter))
    rel = diff / (100.0 - mat.T_inf) * 100.0
    print(f"  max difference = {diff:.5f} degC   ({rel:.4f}% of base excess)")
    iter_ok = rel < 1.0
    print(f"  {'PASS' if iter_ok else 'FAIL'}  browser solver matches reference solver")

    print("\n" + "=" * 68)
    best = results[-1]
    sc1_ok = best['max_err'] < 5.0 and all_ok and iter_ok
    print(f"SC1 TARGET:  max error < 5%")
    print(f"SC1 RESULT:  {best['max_err']:.3f}% at nx=320   "
          f"->  {'PASS' if sc1_ok else 'FAIL'}")
    print("=" * 68)

    # Save the numbers for the report
    out = os.path.join(os.path.dirname(__file__), "validation_results.csv")
    with open(out, "w") as f:
        f.write("nx,dx_mm,max_err_pct,tip_err_pct\n")
        for r in results:
            f.write(f"{r['nx']},{r['dx']*1000:.4f},"
                    f"{r['max_err']:.4f},{r['tip_err']:.4f}\n")
    print(f"\nSaved: {out}")
    return results, sc1_ok


if __name__ == "__main__":
    main()
