"""
Does the archive actually help?

Fair comparison: both methods get the SAME number of physics evaluations.
Plain GA:    generations x population
MAP-Elites:  the same total, one evaluation per child

Reported: best temperature found, and for MAP-Elites also how much of the
shape space it filled and its quality-diversity score.
"""
import numpy as np, sys, os, json, time
sys.path.insert(0, os.path.dirname(__file__))
from physics2 import Material2, solve2
from evolve2 import (Problem2, evolve_plain, evolve_mapelites,
                     best_baseline2, fitness2, largest_connected)

def peak_of(mask, prob):
    m = largest_connected(mask | prob.source, prob.source)
    T = solve2(m, prob.mat, prob.dx, Q=prob.Q, channel=True, radiation=True)
    return float(np.nanmax(T))

def main():
    mat = Material2(k=50, t_z=0.0003, h_iso=120, T_inf=35,
                    emis=0.85, u_air=3.0, L_flow=0.066)
    print("=" * 74)
    print("MAP-ELITES vs PLAIN GENETIC ALGORITHM, equal evaluation budget")
    print("=" * 74)
    print(f"\n{mat}\n")

    GENS, POP = 100, 24
    BUDGET = GENS * POP
    print(f"budget = {BUDGET} physics evaluations for both methods\n")

    rows = []
    for seed in range(4):
        prob = Problem2(ny=44, nx=44, dx=0.0015, mat=mat,
                        budget=0.22, Q_total=5.0)
        base = best_baseline2(prob)
        prob.max_cells = base['cells']

        t0 = time.time()
        mg, sg, hg = evolve_plain(prob, generations=GENS, pop=POP,
                                  seed=seed, channel=True, radiation=True)
        tg = time.time() - t0
        pg = peak_of(mg, prob)

        t0 = time.time()
        mm, sm, hm, arch = evolve_mapelites(prob, evaluations=BUDGET,
                                            seed=seed, bins=12,
                                            channel=True, radiation=True)
        tm = time.time() - t0
        pm = peak_of(mm, prob)

        rows.append(dict(seed=seed, base=base['peak'], ga=pg, me=pm,
                         cov=arch.coverage, filled=len(arch.best),
                         tga=tg, tme=tm))
        print(f"  seed {seed}   fins {base['peak']:7.2f}   "
              f"GA {pg:7.2f}   MAP-Elites {pm:7.2f}   "
              f"coverage {arch.coverage:5.1%}   ({tg:.0f}s / {tm:.0f}s)")

    ga = np.array([r['ga'] for r in rows])
    me = np.array([r['me'] for r in rows])
    bs = np.array([r['base'] for r in rows])
    print("\n" + "-" * 74)
    print(f"  baseline mean      {bs.mean():7.2f} C")
    print(f"  plain GA mean      {ga.mean():7.2f} C   "
          f"({(bs.mean()-ga.mean())/(bs.mean()-35)*100:+.1f}% vs fins)")
    print(f"  MAP-Elites mean    {me.mean():7.2f} C   "
          f"({(bs.mean()-me.mean())/(bs.mean()-35)*100:+.1f}% vs fins)")
    print(f"  MAP-Elites is      {ga.mean()-me.mean():+.2f} C better than the GA")
    print(f"  mean coverage      {np.mean([r['cov'] for r in rows]):.1%} "
          f"of the shape space")

    win = (me < ga).sum()
    print(f"  MAP-Elites won     {win} of {len(rows)} seeds")

    d = os.path.dirname(__file__)
    with open(os.path.join(d, "mapelites.csv"), "w") as f:
        f.write("seed,baseline_C,ga_C,mapelites_C,coverage,filled_bins\n")
        for r in rows:
            f.write(f"{r['seed']},{r['base']:.3f},{r['ga']:.3f},{r['me']:.3f},"
                    f"{r['cov']:.4f},{r['filled']}\n")

    # save one archive for the figure
    prob = Problem2(ny=44, nx=44, dx=0.0015, mat=mat, budget=0.22, Q_total=5.0)
    base = best_baseline2(prob); prob.max_cells = base['cells']
    mm, sm, hm, arch = evolve_mapelites(prob, evaluations=BUDGET, seed=0,
                                        bins=12, channel=True, radiation=True)
    np.save(os.path.join(d, "archive_grid.npy"), arch.grid())
    np.save(os.path.join(d, "archive_best.npy"), mm)
    print(f"\n  saved mapelites.csv, archive_grid.npy, archive_best.npy")
    return rows

if __name__ == "__main__":
    main()
