# What to download, and what each file proves

Every script listed here was executed and confirmed working. Runtimes are
measured, not estimated.

---

## The short answer

Download **three folders**: `finch/`, `sim/`, `figures/`. Total 4.4 MB.

Everything else is optional reference material.

---

## 1. The website, `finch/` - 108 KB

This is the deliverable. Four files, no build step, no dependencies.

| File | Size | Purpose |
|---|---|---|
| `home.html` | 12 KB | Overview page. Open this first. |
| `index.html` | 56 KB | The interactive tool, including the entire physics engine |
| `findings.html` | 24 KB | Technical report, all method and results |
| `style.css` | 5 KB | Shared styling |

Open `home.html` in any browser. It works offline; if fonts cannot load it
falls back to system fonts and remains fully readable.

**All four files are required.** The tool will lose its styling without
`style.css`, and navigation between pages will break if any is missing.

---

## 2. The analysis code, `sim/` - 148 KB

Fourteen Python scripts. This is the evidence that the results are
reproducible rather than asserted.

### Core, download these

| File | Purpose |
|---|---|
| `physics2.py` | The thermal solver. Conduction, channel-limited convection, radiation, transient mode. |
| `evolve2.py` | The search. Objective functions, genetic operators, quality diversity archive, reference generator. |
| `validate2.py` | **The validation suite.** Fourteen assertions against analytical solutions. |
| `regime2.py` | Thermal regime sweep, produces the main result table. |
| `airflow_test.py` | Convective model sensitivity analysis. |
| `mapelites_test.py` | Quality diversity comparison against conventional search. |
| `cheat_log.py` | Objective function development, four formulations. |
| `test_site.py` | Verifies every number on the website traces to a recorded result. |

### Superseded but worth keeping

| File | Why keep it |
|---|---|
| `physics.py`, `evolve.py` | Version one. Kept because `figures.py` and the older experiments still import them. |
| `validate.py` | Version one validation. Independent confirmation that the original solver was also correct. |
| `benchmark.py`, `regime.py` | Version one experiments. Superseded by `regime2.py`. |
| `figures.py` | Generates the eight report figures. |

**Requires:** Python 3 with `numpy`, `scipy` and `matplotlib`.

```bash
pip install numpy scipy matplotlib
```

---

## 3. The evidence files, `sim/*.csv` and `sim/*.json` - 96 KB

These are your raw results. Each is produced by a named script.

| File | Produced by | Contains |
|---|---|---|
| `validation_results.csv` | `validate.py` | Grid convergence data, the proof the solver is second-order accurate |
| `regime_v2.csv` | `regime2.py` | **Main result.** Improvement across six thermal regimes |
| `airflow_test.csv` | `airflow_test.py` | Convective model sensitivity, three treatments compared |
| `mapelites.csv` | `mapelites_test.py` | Quality diversity against conventional search, four seeds |
| `cheat_log.csv` | `cheat_log.py` | Four objective formulations and their outcomes |
| `benchmark.csv` | `benchmark.py` | Ten independent seeds, reproducibility evidence |
| `convergence.csv` | `benchmark.py` | Fitness per generation, all seeds. 55 KB, the largest data file |
| `regime.csv` | `regime.py` | Version one regime sweep |
| `summary.json` | `benchmark.py` | Headline statistics |

---

## 4. Figures, `figures/` - 4.1 MB

### Report figures, cite these

| File | Shows |
|---|---|
| `fig1_validation.png` | Solver against the analytical fin equation, plus convergence order |
| `fig2_head_to_head.png` | Reference and optimised geometry side by side, ten seed consistency |
| `fig3_regime.png` | **The main result.** Improvement against conduction length ratio |
| `fig4_regime_shapes.png` | Geometry comparison in the conduction-limited regime |
| `fig5_cheat_log.png` | Four objective formulations and the geometry each produced |
| `fig6_convergence.png` | Convergence behaviour across ten independent runs |
| `fig7_airflow.png` | Convective model sensitivity |
| `fig8_airflow_shapes.png` | Geometry under each convective treatment |

### Site imagery

| File | Purpose |
|---|---|
| `home_human.png`, `home_grown.png` | Embedded in the overview page. **Required for the site to display correctly.** |
| `final_home.png`, `final_findings.png` | Full-page captures of the finished site |
| `v2_tool.png`, `v2_arch.png` | Tool interface, including the archive view |

---

## 5. Documentation

| File | Keep? |
|---|---|
| `DEPLOY.md` | Yes. GitHub Pages and Netlify instructions. |
| `FILES.md` | This document. |
| `NEXT.md` | Yes. Status summary and suggested next actions. |
| `archive/` | Optional. Earlier drafts and superseded screenshots, retained for reference only. |

---

## Verifying the evidence yourself

This is the section that matters for an assessed project. Every claim can be
regenerated from source.

```bash
cd sim
python3 validate2.py        # 14 assertions           about 2 minutes
python3 cheat_log.py        # objective development   about 1 minute
python3 test_site.py        # site value verification about 1 minute
python3 regime2.py          # main result table       about 10 minutes
python3 mapelites_test.py   # search comparison       about 8 minutes
python3 airflow_test.py     # model sensitivity       about 6 minutes
python3 figures.py          # regenerate all figures  about 10 seconds
```

`test_site.py` additionally requires Playwright for the browser checks:

```bash
pip install playwright
python3 -m playwright install chromium
```

Without Playwright it still runs and performs the data consistency checks,
skipping the browser section.

---

## What the validation actually demonstrates

If asked how the model is known to be correct, these are the specific results.

### Agreement with analytical solutions

| Test | Reference | Result |
|---|---|---|
| Temperature profile along a fin | Analytical fin equation | 0.0003% |
| Radiation in isolation | Stefan-Boltzmann balance | 0.174% |
| Radiation with convection | Closed-form lumped balance | 0.000% |
| Transient at long time | Steady-state solution | 0.00% |

### Convergence order

| Grid cells | Cell size | Maximum error |
|---|---|---|
| 10 | 5.00 mm | 0.0751% |
| 20 | 2.50 mm | 0.0189% |
| 40 | 1.25 mm | 0.0047% |
| 80 | 0.625 mm | 0.0012% |
| 160 | 0.3125 mm | 0.0003% |
| 320 | 0.156 mm | 0.0001% |

The error falls by approximately four for each halving of cell size. This is
the signature of second-order spatial discretisation. It is stronger evidence
than any single small residual, because it shows the solver converges in the
manner the numerical theory predicts rather than merely producing a plausible
number.

### Independent reimplementation

The solver exists twice, in Python and JavaScript, developed separately rather
than translated. Agreement between two independent implementations indicates
that neither contains an undetected error.

| Quantity | Python | JavaScript | Difference |
|---|---|---|---|
| Critical gap | 4.645 mm | 4.645 mm | 0 |
| Enclosed-cell coefficient | 0.000 | 0.000 | 0 |
| Isolated-cell coefficient | 57.097 | 57.097 | 0 |
| Peak temperature, reference case | 123.9503 °C | 123.9501 °C | 0.0002 °C |

### Reproducibility

Results vary by less than 0.1 percentage points across independent random
seeds, confirming that reported improvements reflect the optimisation rather
than a favourable initial condition.

---

## Minimum viable download

If storage is limited, these are sufficient to present and defend the work:

```
finch/             all four files        108 KB
sim/*.py           all scripts           148 KB
sim/*.csv, *.json  all data               96 KB
figures/fig*.png   eight report figures  640 KB
figures/home_*.png site imagery           60 KB
DEPLOY.md, FILES.md, NEXT.md              45 KB
                                        -------
                                     about 1.1 MB
```

Omitting `figures/final_*.png` and `figures/v2_*.png` saves 3.3 MB. Those are
site captures, useful for a presentation but not required.
