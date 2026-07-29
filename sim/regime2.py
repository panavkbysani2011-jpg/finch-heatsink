"""
The L.m sweep, rerun with version 2 physics.

Version 1 used a guessed occlusion model and no radiation. This rerun uses the
derived channel model and full Stefan Boltzmann radiation, so the numbers on
the site come from the same physics the browser runs.
"""
import numpy as np, sys, os
sys.path.insert(0, os.path.dirname(__file__))
from physics2 import Material2, solve2
from evolve2 import Problem2, evolve_plain, best_baseline2, largest_connected

def peak(mask, prob):
    m = largest_connected(mask | prob.source, prob.source)
    T = solve2(m, prob.mat, prob.dx, Q=prob.Q, channel=True, radiation=True)
    return float(np.nanmax(T))

CASES = [
    ("Aluminium 1mm, still air", 205, 0.0010,  10, 0.0),
    ("Aluminium 1mm, fan",       205, 0.0010,  60, 2.0),
    ("Aluminium 0.3mm, fan",     205, 0.0003,  60, 2.0),
    ("Steel 0.5mm, fan",          50, 0.0005,  60, 2.0),
    ("Steel 0.3mm, strong fan",   50, 0.0003, 120, 3.0),
    ("Low-k 1mm, fan",             5, 0.0010,  60, 2.0),
]

def main():
    print("=" * 78)
    print("L.m SWEEP, VERSION 2 PHYSICS (derived channel model + radiation)")
    print("=" * 78)
    print(f"\n{'case':<26}{'L.m':>6}{'s_c mm':>8}{'fins':>9}{'grown':>9}{'gain':>8}")
    print("-" * 78)
    rows = []
    for name, k, tz, h, u in CASES:
        mat = Material2(k=k, t_z=tz, h_iso=h, T_inf=35, emis=0.85,
                        u_air=u, L_flow=0.066)
        p = Problem2(ny=44, nx=44, dx=0.0015, mat=mat, budget=0.22, Q_total=5.0)
        base = best_baseline2(p); p.max_cells = base['cells']
        bp = base['peak']
        m, s, hist = evolve_plain(p, generations=110, pop=24, seed=0,
                                  channel=True, radiation=True)
        ep = peak(m, p)
        lm = (22 * 0.0015) * mat.m
        g = (bp - ep) / (bp - 35) * 100
        rows.append(dict(case=name, lm=lm, sc=mat.choke_gap()*1000,
                         base=bp, evo=ep, gain=g))
        print(f"{name:<26}{lm:>6.2f}{mat.choke_gap()*1000:>8.2f}"
              f"{bp:>9.1f}{ep:>9.1f}{g:>+7.1f}%")

    best = max(rows, key=lambda r: r['gain'])
    print("-" * 78)
    print(f"\npeak gain {best['gain']:+.1f}% at L.m = {best['lm']:.2f} ({best['case']})")

    with open(os.path.join(os.path.dirname(__file__), "regime_v2.csv"), "w") as f:
        f.write("case,Lm,choke_gap_mm,baseline_C,evolved_C,improvement_pct\n")
        for r in rows:
            f.write(f"\"{r['case']}\",{r['lm']:.4f},{r['sc']:.3f},"
                    f"{r['base']:.3f},{r['evo']:.3f},{r['gain']:.3f}\n")
    print("saved regime_v2.csv")
    return rows

if __name__ == "__main__":
    main()
