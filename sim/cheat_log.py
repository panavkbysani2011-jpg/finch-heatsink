"""
FINCH - THE CHEAT LOG
=====================

Deliberately run the flawed fitness functions and record exactly how the
optimiser exploits each one. This is not a failure report - it is the
central evidence that the fitness function, not the algorithm, is where
the thinking happens.

Run:  python3 cheat_log.py
"""

import numpy as np
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from physics import Material, solve_iterative
from evolve import Problem, evolve, evaluate, largest_connected


def thin_fraction(mask, source):
    nbr = np.zeros(mask.shape, dtype=int)
    ny, nx = mask.shape
    for di, dj in ((-1, 0), (1, 0), (0, -1), (0, 1)):
        sh = np.zeros(mask.shape, dtype=bool)
        i0, i1 = max(0, -di), min(ny, ny - di)
        j0, j1 = max(0, -dj), min(nx, nx - dj)
        sh[i0:i1, j0:j1] = mask[i0 + di:i1 + di, j0 + dj:j1 + dj]
        nbr += (sh & mask)
    thin = ((nbr < 2) & mask & ~source).sum()
    return thin / max(mask.sum(), 1)


def main():
    prob = Problem(ny=40, nx=40, dx=0.0015, budget=0.25, Q_total=5.0)
    print("=" * 72)
    print("FINCH  -  CHEAT LOG")
    print("=" * 72)
    print(f"\n{prob}")
    print(f"{prob.mat}\n")
    print("Running each fitness version for 60 generations and recording")
    print("what the optimiser does with the loopholes it is given.\n")

    rows = []
    for v in (1, 2, 3, 4):
        print("-" * 72)
        print(f"FITNESS v{v}")
        print("-" * 72)
        best, hist = evolve(prob, generations=60, pop_size=20, elite=4,
                            seed=42, fitness_version=v, log_every=20)
        ev = evaluate(best, prob)
        tf = thin_fraction(ev['mask'], prob.source)
        frac = ev['cells'] / (prob.ny * prob.nx)
        rows.append(dict(v=v, peak=ev['peak'], mean=ev['mean'],
                         cells=ev['cells'], frac=frac, thin=tf))
        print(f"  RESULT  peak={ev['peak']:.2f}C  mean={ev['mean']:.2f}C  "
              f"metal={frac:.1%} of grid  thin cells={tf:.1%}")
        np.save(os.path.join(os.path.dirname(__file__), f"cheat_v{v}.npy"),
                ev['mask'])
        print()

    print("=" * 72)
    print("SUMMARY")
    print("=" * 72)
    print(f"{'ver':<5}{'peak C':>10}{'mean C':>10}{'metal %':>10}"
          f"{'thin %':>10}   what it exploited")
    print("-" * 72)
    notes = {
        1: "grew cool fringe to drag the MEAN down; chip runs hot",
        2: "filled the grid - no budget was enforced",
        3: "one-cell tendrils below the resolution limit",
        4: "(none found - this is the version used for results)",
    }
    for r in rows:
        print(f"v{r['v']:<4}{r['peak']:>10.2f}{r['mean']:>10.2f}"
              f"{r['frac']:>9.1%}{r['thin']:>10.1%}   {notes[r['v']]}")

    print("\nThe headline: v1 produces the LOWEST mean temperature and one of")
    print("the HIGHEST peak temperatures. It optimised the number it was")
    print("given, perfectly, and that number was the wrong one.")

    out = os.path.join(os.path.dirname(__file__), "cheat_log.csv")
    with open(out, "w") as f:
        f.write("version,peak_C,mean_C,metal_fraction,thin_fraction,exploit\n")
        for r in rows:
            f.write(f"{r['v']},{r['peak']:.3f},{r['mean']:.3f},"
                    f"{r['frac']:.4f},{r['thin']:.4f},\"{notes[r['v']]}\"\n")
    print(f"\nSaved: {out}")


if __name__ == "__main__":
    main()
