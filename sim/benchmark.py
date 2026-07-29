"""
FINCH - SC3 / SC4  HEAD-TO-HEAD
===============================

Baseline: the straight radial fin heat sink used in almost every LED bulb
and small power supply. Straight fins are chosen because they are cheap to
extrude, not because they are thermally optimal.

The evolved design gets exactly the same brief:
    same grid, same chip, same heat load, same material,
    and NO MORE metal than the baseline uses.

Then we run it from 10 different random seeds to check the result is not
a fluke (SC4).
"""

import numpy as np
import sys, os, time, json
sys.path.insert(0, os.path.dirname(__file__))
from physics import Material, solve
from evolve import Problem, evolve, evaluate, largest_connected


def radial_fins(prob, n_fins=8, fin_width=2, hub_r=None):
    """Classic straight radial fins radiating from a hub ON THE CHIP.

    BUG FIXED (Day 6). This used to place the hub at the centre of the GRID
    regardless of where the heat source actually was. With the chip mounted
    at the edge that put the hub 14.8 cells away from the heat, which no
    engineer would ever do. It made the human baseline look far worse than
    it should and inflated the evolved design's apparent advantage.

    The hub now follows the chip's centre of mass, which is what a real
    designer would do: you bolt the sink onto the hot part.
    """
    ny, nx = prob.ny, prob.nx
    ys, xs = np.nonzero(prob.source)
    cy, cx = (ys.mean(), xs.mean()) if len(ys) else (ny/2.0-0.5, nx/2.0-0.5)
    m = prob.source.copy()

    if hub_r is None:
        hub_r = max(3, ny // 10)
    yy, xx = np.indices((ny, nx))
    r = np.sqrt((yy - cy) ** 2 + (xx - cx) ** 2)
    m |= (r <= hub_r)

    R = min(ny, nx) / 2.0 - 1
    for k in range(n_fins):
        a = 2 * np.pi * k / n_fins
        for t in np.linspace(0, R, int(R * 4)):
            pi_, pj_ = cy + t * np.sin(a), cx + t * np.cos(a)
            for wy in range(-(fin_width // 2), fin_width // 2 + 1):
                for wx in range(-(fin_width // 2), fin_width // 2 + 1):
                    i, j = int(round(pi_ + wy)), int(round(pj_ + wx))
                    if 0 <= i < ny and 0 <= j < nx:
                        m[i, j] = True
    return m


def best_baseline(prob):
    """Fairness matters: tune the baseline, don't strawman it.

    Try a range of fin counts and widths, keep whichever performs best
    within the material budget. The evolved design then has to beat the
    BEST conventional design, not a bad one.
    """
    best = None
    for n_fins in (4, 6, 8, 10, 12, 16):
        for w in (1, 2, 3):
            m = radial_fins(prob, n_fins=n_fins, fin_width=w)
            m = largest_connected(m | prob.source, prob.source)
            if m.sum() > prob.max_cells:
                continue
            T = solve(m, prob.mat, prob.dx, Q=prob.Q)
            peak = np.nanmax(T)
            if best is None or peak < best['peak']:
                best = dict(peak=peak, mask=m, n_fins=n_fins,
                            width=w, cells=int(m.sum()), T=T)
    return best


def main():
    prob = Problem(ny=48, nx=48, dx=0.0015, budget=0.22, Q_total=5.0)
    print("=" * 72)
    print("FINCH  -  SC3 / SC4   EVOLVED  vs  STRAIGHT RADIAL FINS")
    print("=" * 72)
    print(f"\n{prob}")
    print(f"{prob.mat}\n")

    # ---------------- baseline ----------------
    print("-" * 72)
    print("BASELINE  (tuned - we try 18 conventional configurations")
    print("           and keep the best one)")
    print("-" * 72)
    base = best_baseline(prob)
    print(f"  best conventional: {base['n_fins']} fins, width {base['width']} cells")
    print(f"  metal used       : {base['cells']} cells "
          f"({base['cells']/(prob.ny*prob.nx):.1%} of grid)")
    print(f"  PEAK TEMPERATURE : {base['peak']:.2f} C")

    # the evolved design may use no more metal than the baseline
    prob.max_cells = base['cells']
    print(f"\n  -> evolved designs are capped at {prob.max_cells} cells, "
          f"identical to the baseline\n")

    # ---------------- evolved, 10 seeds ----------------
    print("-" * 72)
    print("EVOLVED  (10 independent runs, different random seeds)")
    print("-" * 72)
    results = []
    t_start = time.time()
    for seed in range(10):
        t0 = time.time()
        best_mask, hist = evolve(prob, generations=220, pop_size=28, elite=5,
                                 seed=seed, fitness_version=4,
                                 mutation_rate=0.035, verbose=False)
        ev = evaluate(best_mask, prob)
        imp = (base['peak'] - ev['peak']) / (base['peak'] - prob.mat.T_inf) * 100
        results.append(dict(seed=seed, peak=ev['peak'], cells=ev['cells'],
                            improvement=imp, mask=ev['mask'], hist=hist))
        print(f"  seed {seed:2d}   peak={ev['peak']:7.2f}C   "
              f"cells={ev['cells']:4d}   improvement={imp:+6.2f}%   "
              f"({time.time()-t0:.0f}s)")

    peaks = np.array([r['peak'] for r in results])
    imps = np.array([r['improvement'] for r in results])
    best_run = results[int(np.argmin(peaks))]

    print(f"\n  total runtime: {time.time()-t_start:.0f}s")

    # ---------------- verdict ----------------
    print("\n" + "=" * 72)
    print("RESULTS")
    print("=" * 72)
    print(f"  Baseline (best straight fins) : {base['peak']:7.2f} C")
    print(f"  Evolved, best of 10 seeds     : {peaks.min():7.2f} C")
    print(f"  Evolved, mean of 10 seeds     : {peaks.mean():7.2f} C")
    print(f"  Evolved, worst of 10 seeds    : {peaks.max():7.2f} C")
    print(f"  Std deviation across seeds    : {peaks.std():7.2f} C")
    print()
    print(f"  Improvement (best) : {imps.max():+6.2f}%  of temperature rise")
    print(f"  Improvement (mean) : {imps.mean():+6.2f}%")
    spread = (peaks.max() - peaks.min()) / (peaks.mean() - prob.mat.T_inf) * 100
    print(f"  Seed spread        : {spread:6.2f}%   (SC4 target < 10%)")
    print()
    sc3 = imps.max() >= 15.0
    sc4 = spread < 10.0
    print(f"  SC3  (>=15% better than baseline)  : "
          f"{'PASS' if sc3 else 'FAIL'}  [{imps.max():+.2f}%]")
    print(f"  SC4  (seed spread < 10%)           : "
          f"{'PASS' if sc4 else 'FAIL'}  [{spread:.2f}%]")
    print("=" * 72)

    # ---------------- save ----------------
    d = os.path.dirname(__file__)
    np.save(os.path.join(d, "baseline_mask.npy"), base['mask'])
    np.save(os.path.join(d, "evolved_mask.npy"), best_run['mask'])
    np.save(os.path.join(d, "baseline_T.npy"), base['T'])
    ev_best = evaluate(best_run['mask'], prob)
    np.save(os.path.join(d, "evolved_T.npy"), ev_best['T'])

    with open(os.path.join(d, "benchmark.csv"), "w") as f:
        f.write("seed,peak_C,cells,improvement_pct\n")
        for r in results:
            f.write(f"{r['seed']},{r['peak']:.3f},{r['cells']},"
                    f"{r['improvement']:.3f}\n")

    with open(os.path.join(d, "convergence.csv"), "w") as f:
        f.write("seed,generation,best_fitness,mean_fitness\n")
        for r in results:
            for h in r['hist']:
                f.write(f"{r['seed']},{h['gen']},{h['best']:.4f},"
                        f"{h['mean']:.4f}\n")

    summary = dict(
        baseline_peak=float(base['peak']),
        baseline_cells=int(base['cells']),
        baseline_fins=int(base['n_fins']),
        baseline_width=int(base['width']),
        evolved_best=float(peaks.min()),
        evolved_mean=float(peaks.mean()),
        evolved_worst=float(peaks.max()),
        evolved_std=float(peaks.std()),
        improvement_best=float(imps.max()),
        improvement_mean=float(imps.mean()),
        seed_spread_pct=float(spread),
        ambient=float(prob.mat.T_inf),
        Q_total=float(prob.Q_total),
        grid=[prob.ny, prob.nx],
        dx_mm=prob.dx * 1000,
        sc3_pass=bool(sc3), sc4_pass=bool(sc4),
    )
    with open(os.path.join(d, "summary.json"), "w") as f:
        json.dump(summary, f, indent=2)
    print(f"\nSaved: benchmark.csv, convergence.csv, summary.json, *.npy")


if __name__ == "__main__":
    main()
