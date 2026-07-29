"""
FINCH - WHEN DOES SHAPE ACTUALLY MATTER?
========================================

The first head-to-head produced +5.3%, short of the 15% target. Rather
than tune the algorithm to chase the number, we asked whether 15% was
physically available at all. It was not:

    baseline (best straight fins)      137.20 C
    isothermal floor (perfect metal)   129.16 C
    -> the entire prize on offer is      8.03 C
    -> evolution captured 5.41 C = 67% of it

So the target was wrong, not the optimiser.

The governing parameter is the ratio of the sink's size to the fin length
scale 1/m, where m = sqrt(2h / (k * t_z)):

    L * m << 1   metal is nearly isothermal; shape is almost irrelevant
    L * m >> 1   heat cannot reach the extremities; shape decides everything

This script sweeps that ratio to find where an evolved shape earns its keep.
That is a far more useful result than a single win, and it is the kind of
answer only a search-based method can give you cheaply.
"""

import numpy as np
import sys, os, json
sys.path.insert(0, os.path.dirname(__file__))
from physics import Material, solve
from evolve import Problem, evolve, evaluate, largest_connected
from benchmark import best_baseline


def run_case(name, mat, dx, ny=44, nx=44, budget=0.22, Q=5.0,
             generations=120, seed=0):
    prob = Problem(ny=ny, nx=nx, dx=dx, mat=mat, budget=budget, Q_total=Q)
    base = best_baseline(prob)
    prob.max_cells = base['cells']

    best_mask, hist = evolve(prob, generations=generations, pop_size=24,
                             elite=4, seed=seed, fitness_version=4,
                             mutation_rate=0.035, verbose=False)
    ev = evaluate(best_mask, prob)

    # isothermal floor with the same amount of metal
    A = base['cells'] * dx * dx
    T_iso = mat.T_inf + Q / (2 * mat.h * A)

    rise_base = base['peak'] - mat.T_inf
    rise_evo = ev['peak'] - mat.T_inf
    imp = (base['peak'] - ev['peak']) / rise_base * 100
    headroom = base['peak'] - T_iso
    captured = (base['peak'] - ev['peak']) / headroom * 100 if headroom > 1e-9 else 0.0

    L = 0.5 * min(ny, nx) * dx          # half-width of the domain
    Lm = L * mat.m

    return dict(name=name, Lm=Lm, base=base['peak'], evo=ev['peak'],
                iso=T_iso, imp=imp, captured=captured,
                headroom=headroom, cells=base['cells'],
                mask=ev['mask'], base_mask=base['mask'], prob=prob)


def main():
    print("=" * 78)
    print("FINCH  -  WHEN DOES SHAPE MATTER?  (sweep of L*m)")
    print("=" * 78)
    print("\n  L*m << 1 : metal nearly isothermal, shape irrelevant")
    print("  L*m >> 1 : heat cannot reach the tips, shape is everything\n")

    cases = [
        # name,                      k,    t_z,     h,   dx
        ("Aluminium 1mm, still air", 205, 0.0010,  10, 0.0015),
        ("Aluminium 1mm, 25 W/m2K",  205, 0.0010,  25, 0.0015),
        ("Aluminium 1mm, forced",    205, 0.0010,  60, 0.0015),
        ("Aluminium 0.3mm, forced",  205, 0.0003,  60, 0.0015),
        ("Steel 0.5mm, forced",       50, 0.0005,  60, 0.0015),
        ("Steel 0.3mm, strong fan",   50, 0.0003, 120, 0.0015),
        ("Plastic-ish 1mm, forced",    5, 0.0010,  60, 0.0015),
    ]

    rows = []
    print(f"{'case':<28}{'L*m':>7}{'base':>9}{'evolved':>9}"
          f"{'floor':>9}{'gain%':>8}{'of max%':>9}")
    print("-" * 78)
    for name, k, t_z, h, dx in cases:
        mat = Material(k=k, t_z=t_z, h=h, T_inf=35.0)
        r = run_case(name, mat, dx)
        rows.append(r)
        print(f"{name:<28}{r['Lm']:>7.2f}{r['base']:>9.1f}{r['evo']:>9.1f}"
              f"{r['iso']:>9.1f}{r['imp']:>+8.2f}{r['captured']:>9.1f}")

    print("-" * 78)
    best = max(rows, key=lambda r: r['imp'])
    print(f"\nLargest improvement: {best['name']}  "
          f"({best['imp']:+.2f}%, L*m = {best['Lm']:.2f})")

    print("\nInterpretation:")
    print("  As L*m grows, conduction can no longer keep the extremities warm,")
    print("  so WHERE the metal goes starts to matter more than how much of it")
    print("  there is. That is exactly the regime where a search-based method")
    print("  beats a human rule of thumb - and exactly the regime real thin,")
    print("  cheap, low-conductivity heat sinks operate in.")

    d = os.path.dirname(__file__)
    with open(os.path.join(d, "regime.csv"), "w") as f:
        f.write("case,Lm,baseline_C,evolved_C,isothermal_floor_C,"
                "improvement_pct,pct_of_available\n")
        for r in rows:
            f.write(f"\"{r['name']}\",{r['Lm']:.4f},{r['base']:.3f},"
                    f"{r['evo']:.3f},{r['iso']:.3f},{r['imp']:.3f},"
                    f"{r['captured']:.2f}\n")

    # save the most dramatic case for the gallery
    np.save(os.path.join(d, "regime_best_evolved.npy"), best['mask'])
    np.save(os.path.join(d, "regime_best_baseline.npy"), best['base_mask'])
    with open(os.path.join(d, "regime_best.json"), "w") as f:
        json.dump(dict(name=best['name'], Lm=best['Lm'],
                       baseline=best['base'], evolved=best['evo'],
                       floor=best['iso'], improvement=best['imp'],
                       captured=best['captured']), f, indent=2)
    print(f"\nSaved: regime.csv, regime_best_*.npy")


if __name__ == "__main__":
    main()
