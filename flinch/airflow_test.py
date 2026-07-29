"""
FINCH - THE FALSIFICATION TEST
==============================

RESULTS.md section 10 named the biggest weakness of the project:

    "h is a fixed constant. In reality the convection coefficient varies
     over the surface - and tightly-packed geometry chokes airflow, which
     this model cannot see. This is the biggest single weakness, and it
     likely means the compact blob would do WORSE in reality than predicted."

That is a testable claim, so this script tests it.

Design of the experiment
------------------------
Two optimisers:
    v4  constant h everywhere          (the original assumption)
    v5  h varies with local openness   (buried metal is penalised)

Two scoring models, applied to BOTH designs:
    flat     constant h
    airflow  occlusion-aware h

This gives a 2x2 table. The interesting cell is the one that tests the
prediction: how badly does the v4 blob do when judged by the airflow model?

If v4's design collapses under airflow scoring and v5 finds something
different and better, the original blob was an artifact of the assumption
and the honest headline changes.
"""

import numpy as np
import sys, os, json
sys.path.insert(0, os.path.dirname(__file__))
from physics import Material, solve, h_field, openness
from evolve import Problem, evolve, evaluate, largest_connected
from benchmark import best_baseline, radial_fins


def compactness(mask, source):
    """Mean openness of the metal: 0 = one dense lump, 1 = fully exposed."""
    return float(openness(mask)[mask].mean())


def run(label, mat, dx=0.0015, ny=44, nx=44, budget=0.22, Q=5.0,
        generations=180, seed=0):
    prob = Problem(ny=ny, nx=nx, dx=dx, mat=mat, budget=budget, Q_total=Q)
    base = best_baseline(prob)
    prob.max_cells = base['cells']

    # baseline under both scoring models
    bm = base['mask']
    b_flat = np.nanmax(solve(bm, mat, dx, Q=prob.Q))
    b_air = np.nanmax(solve(bm, mat, dx, Q=prob.Q,
                            h_map=h_field(bm, mat, radius=prob.h_radius,
                                          h_min_frac=prob.h_min_frac)))

    out = dict(label=label, cells=base['cells'],
               base_flat=b_flat, base_air=b_air,
               base_open=compactness(bm, prob.source), base_mask=bm)

    for v in (4, 5):
        best, _ = evolve(prob, generations=generations, pop_size=24, elite=4,
                         seed=seed, fitness_version=v, mutation_rate=0.035,
                         verbose=False)
        ev = evaluate(best, prob)
        out[f"v{v}_flat"] = ev['peak_flat']
        out[f"v{v}_air"] = ev['peak_airflow']
        out[f"v{v}_open"] = compactness(ev['mask'], prob.source)
        out[f"v{v}_mask"] = ev['mask']
    out['prob'] = prob
    return out


def main():
    print("=" * 78)
    print("FINCH  -  DOES THE COMPACT BLOB SURVIVE AIRFLOW OCCLUSION?")
    print("=" * 78)
    print("\nThe project's stated biggest weakness was assuming h is constant.")
    print("This test asks whether the headline result depends on that assumption.\n")

    cases = [
        ("Aluminium 1mm forced (L*m 0.8)", Material(k=205, t_z=0.0010, h=60,  T_inf=35)),
        ("Aluminium 0.3mm forced (L*m 1.5)", Material(k=205, t_z=0.0003, h=60,  T_inf=35)),
        ("Steel 0.5mm forced (L*m 2.3)",   Material(k=50,  t_z=0.0005, h=60,  T_inf=35)),
        ("Steel 0.3mm strong fan (L*m 4.2)", Material(k=50, t_z=0.0003, h=120, T_inf=35)),
    ]

    rows = []
    for label, mat in cases:
        print("-" * 78)
        print(label)
        print("-" * 78)
        r = run(label, mat)
        rows.append(r)

        print(f"  {'design':<26}{'flat-h °C':>12}{'airflow °C':>13}"
              f"{'penalty':>10}{'openness':>11}")
        print(f"  {'straight fins':<26}{r['base_flat']:>12.1f}"
              f"{r['base_air']:>13.1f}{r['base_air']-r['base_flat']:>+10.1f}"
              f"{r['base_open']:>11.2f}")
        print(f"  {'v4 evolved (constant h)':<26}{r['v4_flat']:>12.1f}"
              f"{r['v4_air']:>13.1f}{r['v4_air']-r['v4_flat']:>+10.1f}"
              f"{r['v4_open']:>11.2f}")
        print(f"  {'v5 evolved (airflow)':<26}{r['v5_flat']:>12.1f}"
              f"{r['v5_air']:>13.1f}{r['v5_air']-r['v5_flat']:>+10.1f}"
              f"{r['v5_open']:>11.2f}")

        # honest gains, judged by the airflow model
        g4 = (r['base_air'] - r['v4_air']) / (r['base_air'] - 35) * 100
        g5 = (r['base_air'] - r['v5_air']) / (r['base_air'] - 35) * 100
        g4f = (r['base_flat'] - r['v4_flat']) / (r['base_flat'] - 35) * 100
        print(f"\n  gain vs fins, judged flat-h    : v4 {g4f:+6.1f}%")
        print(f"  gain vs fins, judged airflow   : v4 {g4:+6.1f}%   "
              f"v5 {g5:+6.1f}%")
        r['g4_flat'], r['g4_air'], r['g5_air'] = g4f, g4, g5
        print()

    print("=" * 78)
    print("VERDICT")
    print("=" * 78)
    print(f"{'case':<34}{'v4 flat':>9}{'v4 air':>9}{'v5 air':>9}{'lost':>9}")
    print("-" * 78)
    for r in rows:
        lost = r['g4_flat'] - r['g4_air']
        print(f"{r['label']:<34}{r['g4_flat']:>+8.1f}%{r['g4_air']:>+8.1f}%"
              f"{r['g5_air']:>+8.1f}%{lost:>8.1f}pp")

    print("\nReading this table:")
    print("  'v4 flat'  = the gain originally reported")
    print("  'v4 air'   = that same design, judged with airflow occlusion")
    print("  'v5 air'   = a design that KNEW about occlusion, judged the same way")
    print("  'lost'     = how much of the original claim was an artifact")

    d = os.path.dirname(__file__)
    with open(os.path.join(d, "airflow_test.csv"), "w") as f:
        f.write("case,base_flat,base_air,v4_flat,v4_air,v5_flat,v5_air,"
                "v4_openness,v5_openness,gain_v4_flat,gain_v4_air,gain_v5_air\n")
        for r in rows:
            f.write(f"\"{r['label']}\",{r['base_flat']:.2f},{r['base_air']:.2f},"
                    f"{r['v4_flat']:.2f},{r['v4_air']:.2f},{r['v5_flat']:.2f},"
                    f"{r['v5_air']:.2f},{r['v4_open']:.3f},{r['v5_open']:.3f},"
                    f"{r['g4_flat']:.2f},{r['g4_air']:.2f},{r['g5_air']:.2f}\n")

    hard = rows[-1]
    np.save(os.path.join(d, "airflow_v4_mask.npy"), hard['v4_mask'])
    np.save(os.path.join(d, "airflow_v5_mask.npy"), hard['v5_mask'])
    np.save(os.path.join(d, "airflow_base_mask.npy"), hard['base_mask'])
    with open(os.path.join(d, "airflow_best.json"), "w") as f:
        json.dump({k: (float(v) if isinstance(v, (int, float, np.floating)) else str(v))
                   for k, v in hard.items()
                   if k not in ('v4_mask', 'v5_mask', 'base_mask', 'prob')},
                  f, indent=2)
    print(f"\nSaved: airflow_test.csv, airflow_*.npy")


if __name__ == "__main__":
    main()
