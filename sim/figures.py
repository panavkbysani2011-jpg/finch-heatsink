"""FINCH - generate all report figures."""

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
import sys, os, csv, json

sys.path.insert(0, os.path.dirname(__file__))
D = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(os.path.dirname(D), "figures")
os.makedirs(OUT, exist_ok=True)

from physics import Material, solve, analytical_fin
from evolve import Problem, largest_connected
from validate import run_fin_test

THERMAL = LinearSegmentedColormap.from_list(
    "thermal", ["#0b1026", "#1b3a6b", "#2e7fb8", "#7fd4c1",
                "#f4e04d", "#f79824", "#e4572e", "#c1121f"])
plt.rcParams.update({
    "figure.facecolor": "white", "axes.facecolor": "white",
    "font.size": 10, "axes.grid": True, "grid.alpha": 0.25,
    "axes.spines.top": False, "axes.spines.right": False,
})


def fig_validation():
    """SC1: simulator vs textbook fin equation."""
    mat = Material()
    fig, ax = plt.subplots(1, 2, figsize=(11, 4.2))

    r = run_fin_test(40, mat=mat, verbose=False)
    x_mm = r['x'] * 1000
    ax[0].plot(x_mm, r['T_ana'], "-", lw=3, color="#c1121f",
               label="Analytical fin equation", zorder=2)
    ax[0].plot(x_mm, r['T_num'], "o", ms=5, color="#1b3a6b", mfc="white",
               mew=1.6, label="FINCH solver (nx=40)", zorder=3)
    ax[0].set_xlabel("Distance from base (mm)")
    ax[0].set_ylabel("Temperature (°C)")
    ax[0].set_title("SC1 · Temperature profile along a straight fin", fontweight="bold")
    ax[0].legend(frameon=False)

    ns, errs = [], []
    for nx in (10, 20, 40, 80, 160, 320):
        rr = run_fin_test(nx, mat=mat, verbose=False)
        ns.append(nx); errs.append(max(rr['max_err'], 1e-7))
    ax[1].loglog(ns, errs, "o-", color="#2e7fb8", lw=2, ms=7)
    ref = [errs[0] * (ns[0] / n) ** 2 for n in ns]
    ax[1].loglog(ns, ref, "--", color="#888", lw=1.5, label="2nd-order reference")
    ax[1].axhline(5.0, color="#c1121f", ls=":", lw=2, label="SC1 target (5%)")
    ax[1].set_xlabel("Grid cells along fin")
    ax[1].set_ylabel("Max error (% of base excess)")
    ax[1].set_title("Grid convergence · error ∝ dx²", fontweight="bold")
    ax[1].legend(frameon=False)

    plt.tight_layout()
    p = os.path.join(OUT, "fig1_validation.png")
    plt.savefig(p, dpi=160); plt.close()
    print("  " + p)


def _draw(ax, mask, T, title, vmin, vmax, prob):
    img = np.where(mask, T, np.nan)
    im = ax.imshow(img, cmap=THERMAL, vmin=vmin, vmax=vmax,
                   interpolation="nearest")
    ax.contour(prob.source.astype(float), levels=[0.5],
               colors="white", linewidths=1.8)
    ax.set_xticks([]); ax.set_yticks([])
    ax.set_title(title, fontweight="bold", fontsize=10)
    return im


def fig_head_to_head():
    """SC3: baseline vs evolved, same metal."""
    with open(os.path.join(D, "summary.json")) as f:
        s = json.load(f)
    prob = Problem(ny=48, nx=48, dx=0.0015, budget=0.22, Q_total=5.0)
    bm = np.load(os.path.join(D, "baseline_mask.npy"))
    em = np.load(os.path.join(D, "evolved_mask.npy"))
    bT = np.load(os.path.join(D, "baseline_T.npy"))
    eT = np.load(os.path.join(D, "evolved_T.npy"))

    vmin = 35
    vmax = max(np.nanmax(bT), np.nanmax(eT))

    fig, ax = plt.subplots(1, 3, figsize=(13.5, 4.6))
    _draw(ax[0], bm, bT,
          f"Straight radial fins (best of 18)\npeak {np.nanmax(bT):.1f}°C · "
          f"{int(bm.sum())} cells", vmin, vmax, prob)
    im = _draw(ax[1], em, eT,
               f"Evolved\npeak {np.nanmax(eT):.1f}°C · {int(em.sum())} cells",
               vmin, vmax, prob)
    cb = fig.colorbar(im, ax=ax[:2], fraction=0.03, pad=0.02)
    cb.set_label("Temperature (°C)")

    # seed consistency
    seeds, peaks = [], []
    with open(os.path.join(D, "benchmark.csv")) as f:
        for row in csv.DictReader(f):
            seeds.append(int(row["seed"])); peaks.append(float(row["peak_C"]))
    ax[2].axhline(s["baseline_peak"], color="#c1121f", lw=2.5,
                  label=f"baseline {s['baseline_peak']:.1f}°C")
    ax[2].bar(seeds, peaks, color="#2e7fb8", alpha=0.85)
    ax[2].set_ylim(min(peaks) - 3, s["baseline_peak"] + 2)
    ax[2].set_xlabel("Random seed"); ax[2].set_ylabel("Peak temperature (°C)")
    ax[2].set_title(f"SC4 · 10 independent runs\nspread "
                    f"{s['seed_spread_pct']:.2f}%", fontweight="bold")
    ax[2].legend(frameon=False, fontsize=9)
    ax[2].set_box_aspect(1)

    p = os.path.join(OUT, "fig2_head_to_head.png")
    plt.savefig(p, dpi=160, bbox_inches="tight"); plt.close()
    print("  " + p)


def fig_regime():
    """The key result: when does shape matter?"""
    rows = []
    with open(os.path.join(D, "regime.csv")) as f:
        for r in csv.DictReader(f):
            rows.append(r)
    Lm = [float(r["Lm"]) for r in rows]
    imp = [float(r["improvement_pct"]) for r in rows]
    names = [r["case"] for r in rows]

    fig, ax = plt.subplots(figsize=(9.5, 5.4))
    ax.plot(Lm, imp, "o-", lw=2.5, ms=10, color="#1b3a6b",
            mfc="#f79824", mew=2, zorder=3)
    ax.axhline(15, color="#c1121f", ls="--", lw=1.6,
               label="15% target set at the start", zorder=1)
    peak_lm = Lm[int(np.argmax(imp))]
    ax.axvspan(0, 1, color="#2e7fb8", alpha=0.09)
    ax.axvspan(1, peak_lm, color="#f4e04d", alpha=0.13)
    ax.axvspan(peak_lm, 5.6, color="#e4572e", alpha=0.11)
    top = max(imp) * 1.18
    ax.text(0.5, top * 0.80, "heat reaches\neverywhere,\nlittle to win",
            ha="center", fontsize=8.5, color="#1b3a6b", style="italic")
    ax.text(peak_lm, max(imp) * 1.07, "sweet spot",
            ha="center", fontsize=9, color="#7a5c00", style="italic", weight="bold")
    ax.text(4.4, top * 0.42, "so conduction limited\nthat even a search\ncannot move heat far",
            ha="center", fontsize=8.5, color="#c1121f", style="italic")
    ax.axvline(peak_lm, color="#7a5c00", ls=":", lw=1.4, alpha=.7)

    for x, y, n in zip(Lm, imp, names):
        short = n.replace("Aluminium", "Al").replace("Plastic-ish", "Low-k")
        ax.annotate(short, (x, y), textcoords="offset points",
                    xytext=(7, -13), fontsize=7.5, color="#444")

    ax.set_xlabel("L·m   (domain half-width ÷ fin length scale)", fontsize=11)
    ax.set_ylabel("Improvement over best straight fins (%)", fontsize=11)
    ax.set_title("The gain peaks in the middle, it does not just keep rising",
                 fontweight="bold", fontsize=12)
    ax.set_xlim(0, 5.6)
    ax.set_ylim(0, max(imp) * 1.18)
    ax.legend(frameon=False, loc="upper left")
    plt.tight_layout()
    p = os.path.join(OUT, "fig3_regime.png")
    plt.savefig(p, dpi=160); plt.close()
    print("  " + p)


def fig_regime_shapes():
    """Visual: the winning shape in the regime where it matters."""
    em = np.load(os.path.join(D, "regime_best_evolved.npy"))
    bm = np.load(os.path.join(D, "regime_best_baseline.npy"))
    with open(os.path.join(D, "regime_best.json")) as f:
        info = json.load(f)

    mat = Material(k=50, t_z=0.0003, h=120, T_inf=35.0)
    prob = Problem(ny=44, nx=44, dx=0.0015, mat=mat, budget=0.22, Q_total=5.0)
    bT = solve(largest_connected(bm | prob.source, prob.source),
               mat, prob.dx, Q=prob.Q)
    eT = solve(largest_connected(em | prob.source, prob.source),
               mat, prob.dx, Q=prob.Q)
    vmin, vmax = 35, max(np.nanmax(bT), np.nanmax(eT))

    fig, ax = plt.subplots(1, 2, figsize=(9.5, 4.8))
    _draw(ax[0], bm, bT, f"Straight fins\npeak {np.nanmax(bT):.1f}°C",
          vmin, vmax, prob)
    im = _draw(ax[1], em, eT, f"Evolved\npeak {np.nanmax(eT):.1f}°C",
               vmin, vmax, prob)
    fig.colorbar(im, ax=ax, fraction=0.035, pad=0.02).set_label("°C")
    fig.suptitle(f"{info['name']}  ·  L·m = {info['Lm']:.2f}  ·  "
                 f"{info['improvement']:+.1f}% improvement",
                 fontweight="bold", y=1.02)
    p = os.path.join(OUT, "fig4_regime_shapes.png")
    plt.savefig(p, dpi=160, bbox_inches="tight"); plt.close()
    print("  " + p)


def fig_cheat_log():
    """The fitness function is the creative act."""
    prob = Problem(ny=40, nx=40, dx=0.0015, budget=0.25, Q_total=5.0)
    rows = []
    with open(os.path.join(D, "cheat_log.csv")) as f:
        for r in csv.DictReader(f):
            rows.append(r)

    fig, axes = plt.subplots(1, 4, figsize=(15, 4.3))
    titles = {
        "1": "v1 · minimise MEAN\ngrew a cool fringe",
        "2": "v2 · minimise PEAK\nno budget enforced",
        "3": "v3 · + hard budget\none-cell tendrils",
        "4": "v4 · + width penalty\nused for all results",
    }
    for ax, r in zip(axes, rows):
        v = r["version"]
        m = np.load(os.path.join(D, f"cheat_v{v}.npy"))
        m = largest_connected(m | prob.source, prob.source)
        T = solve(m, prob.mat, prob.dx, Q=prob.Q)
        _draw(ax, m, T, titles[v], 35, 320, prob)
        ax.set_xlabel(f"peak {float(r['peak_C']):.0f}°C   "
                      f"mean {float(r['mean_C']):.0f}°C",
                      fontsize=9, labelpad=6)
    fig.suptitle("The algorithm optimises exactly what you ask for, "
                 "the fitness function is where the thinking happens",
                 fontweight="bold", fontsize=12, y=1.03)
    plt.tight_layout()
    p = os.path.join(OUT, "fig5_cheat_log.png")
    plt.savefig(p, dpi=160, bbox_inches="tight"); plt.close()
    print("  " + p)


def fig_convergence():
    """SC2: fitness improves over generations."""
    data = {}
    with open(os.path.join(D, "convergence.csv")) as f:
        for row in csv.DictReader(f):
            s = int(row["seed"])
            data.setdefault(s, []).append((int(row["generation"]),
                                           float(row["best_fitness"])))
    fig, ax = plt.subplots(figsize=(9, 5))
    for s, pts in sorted(data.items()):
        g = [p[0] for p in pts]; v = [-p[1] for p in pts]
        ax.plot(g, v, lw=1.4, alpha=0.75, label=f"seed {s}" if s < 3 else None)
    with open(os.path.join(D, "summary.json")) as f:
        summ = json.load(f)
    ax.axhline(summ["baseline_peak"], color="#c1121f", lw=2.5, ls="--",
               label=f"baseline {summ['baseline_peak']:.1f}°C")
    ax.set_xlabel("Generation"); ax.set_ylabel("Best peak temperature (°C)")
    ax.set_title("SC2 · Convergence across 10 independent runs",
                 fontweight="bold")
    ax.set_ylim(125, 260)
    ax.legend(frameon=False, fontsize=9)
    plt.tight_layout()
    p = os.path.join(OUT, "fig6_convergence.png")
    plt.savefig(p, dpi=160); plt.close()
    print("  " + p)


if __name__ == "__main__":
    print("Generating figures...")
    fig_validation()
    fig_head_to_head()
    fig_regime()
    fig_regime_shapes()
    fig_cheat_log()
    fig_convergence()
    print("Done ->", OUT)


def fig_airflow():
    """The falsification test - the most important figure in the project."""
    import csv as _csv
    rows = []
    with open(os.path.join(D, "airflow_test.csv")) as f:
        for r in _csv.DictReader(f):
            rows.append(r)

    labels = [r["case"].split("(")[0].strip() for r in rows]
    lm = [float(r["case"].split("L*m")[1].strip(" )")) for r in rows]
    g4f = [float(r["gain_v4_flat"]) for r in rows]
    g4a = [float(r["gain_v4_air"]) for r in rows]
    g5a = [float(r["gain_v5_air"]) for r in rows]

    fig, ax = plt.subplots(figsize=(10.5, 5.6))
    x = np.arange(len(rows)); w = 0.26
    ax.bar(x - w, g4f, w, label="v4 design, judged constant-h  (original claim)",
           color="#2e7fb8")
    ax.bar(x,     g4a, w, label="same v4 design, judged with airflow",
           color="#c1121f")
    ax.bar(x + w, g5a, w, label="v5 design (airflow-aware), judged with airflow",
           color="#7fd4c1")
    ax.axhline(0, color="#333", lw=1.4)

    for xi, (a, b) in enumerate(zip(g4f, g4a)):
        ax.annotate("", xy=(xi, b + 2), xytext=(xi - w, a - 2),
                    arrowprops=dict(arrowstyle="->", color="#666", lw=1.3))
        ax.text(xi - w/2, (a + b)/2, f"{a-b:.0f}pp\nlost", ha="center",
                va="center", fontsize=7.5, color="#c1121f", fontweight="bold")

    ax.set_xticks(x)
    ax.set_xticklabels([f"{l}\nL·m {v}" for l, v in zip(labels, lm)], fontsize=8.5)
    ax.set_ylabel("Improvement over straight fins (%)")
    ax.set_title("The falsification test: how much of the result was an artifact "
                 "of assuming constant h?", fontweight="bold", fontsize=11.5)
    ax.legend(frameon=False, fontsize=8.5, loc="lower right")
    ax.set_ylim(-90, 40)
    plt.tight_layout()
    p = os.path.join(OUT, "fig7_airflow.png")
    plt.savefig(p, dpi=160); plt.close()
    print("  " + p)


def fig_airflow_shapes():
    """What the airflow-aware optimiser builds instead."""
    from physics import h_field
    mat = Material(k=50, t_z=0.0003, h=120, T_inf=35.0)
    prob = Problem(ny=44, nx=44, dx=0.0015, mat=mat, budget=0.22, Q_total=5.0)

    names = ["Straight fins", "v4 evolved\n(constant h)", "v5 evolved\n(airflow-aware)"]
    files = ["airflow_base_mask.npy", "airflow_v4_mask.npy", "airflow_v5_mask.npy"]
    masks = [np.load(os.path.join(D, f)) for f in files]
    masks = [largest_connected(m | prob.source, prob.source) for m in masks]

    Ts = []
    for m in masks:
        hm = h_field(m, mat, radius=prob.h_radius, h_min_frac=prob.h_min_frac)
        Ts.append(solve(m, mat, prob.dx, Q=prob.Q, h_map=hm))
    vmin, vmax = 35, max(np.nanmax(t) for t in Ts)

    fig, ax = plt.subplots(1, 3, figsize=(13, 4.6))
    for a, m, T, nm in zip(ax, masks, Ts, names):
        im = _draw(a, m, T, f"{nm}\npeak {np.nanmax(T):.1f}°C", vmin, vmax, prob)
    fig.colorbar(im, ax=ax, fraction=0.026, pad=0.02).set_label("°C (airflow model)")
    fig.suptitle("All three scored with airflow occlusion, "
                 "the dense blob suffocates, fins breathe",
                 fontweight="bold", y=1.02, fontsize=12)
    p = os.path.join(OUT, "fig8_airflow_shapes.png")
    plt.savefig(p, dpi=160, bbox_inches="tight"); plt.close()
    print("  " + p)
