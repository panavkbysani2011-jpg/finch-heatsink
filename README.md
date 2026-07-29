# FINCH — Evolutionary Heat Sink Optimizer

**Evolutionary optimisation of heat sink geometry against a validated two-dimensional thermal model.**

---

## Overview

FINCH compares **conventional straight-fin heat sinks** (the kind on every LED bulb and laptop chip) against **AI-evolved organic shapes** — all using real physics calculations, running in your browser.

**Key result:** The evolved design beats conventional fins by 3–20% depending on the material and cooling conditions, with the biggest wins in the intermediate range where heat struggles to reach the edges.

---

## Live Demo

Open `flinch/index.html` in any browser. No installation needed — the entire physics engine runs in JavaScript.

- **`flinch/home.html`** — Project overview
- **`flinch/index.html`** — Interactive tool
- **`flinch/findings.html`** — Technical report

---

## Repository Structure

```
finch-heatsink/
├── flinch/               ← Website (opens in browser)
│   ├── home.html         Overview page
│   ├── index.html        Interactive tool
│   ├── findings.html     Technical report
│   └── style.css         Styling
│
├── sim/                  ← Python scripts + data
│   ├── physics.py        Thermal solver (v1)
│   ├── physics2.py       Thermal solver (v2) — channel model + radiation
│   ├── evolve.py         Evolutionary algorithm (v1 adapter)
│   ├── evolve2.py        Evolutionary algorithm (v2) — MAP-Elites
│   ├── validate.py       Validation tests (v1)
│   ├── validate2.py      Validation tests (v2) — 14 assertions, all passing
│   ├── benchmark.py      Head-to-head comparison (10 seeds)
│   ├── regime.py         Thermal regime sweep (v1)
│   ├── regime2.py        Thermal regime sweep (v2)
│   ├── airflow_test.py   Convective model sensitivity
│   ├── cheat_log.py      Fitness function development
│   ├── mapelites_test.py MAP-Elites comparison
│   ├── test_site.py      Site value verification
│   ├── figures.py        Report figure generator
│   └── *.csv, *.npy      Raw experimental data
│
├── figures/              ← Generated report figures
│   ├── fig1_validation.png
│   └── fig8_airflow_shapes.png
│
├── README.md
├── DETAILED_GUIDE.md     ← Full project explanation
├── DEPLOY.md             ← Deployment instructions
└── package.json          ← For web hosting
```

---

## The Physics

The simulator solves the 2D heat equation on a grid of metal cells:

- **Conduction** — heat spreads sideways through the metal
- **Convection** — heat leaves the surfaces into the surrounding air
- **Radiation** — heat radiates from hot surfaces (included in v2)
- **Channel starvation** — airflow is reduced in narrow channels (v2)

The solver was validated against the textbook fin equation to **0.0003% error** and achieves **second-order grid convergence** (error falls ~4× each time the grid is doubled).

---

## How To Run Python Scripts

```bash
cd sim
pip install numpy scipy matplotlib

python3 validate2.py       # Run 14 validation tests
python3 cheat_log.py       # Fitness function experiments
python3 airflow_test.py    # Airflow sensitivity
python3 regime2.py         # Main result table
python3 figures.py         # Generate all figures
```

---

## Key Findings

| Material | Heat travels | Search wins by |
|---|---|---|
| Thick aluminium, no fan | 101 mm | 4.6% |
| Thick aluminium, fan | 41 mm | 19.5% |
| Thin aluminium, fan | 23 mm | 13.3% |
| Thick steel, fan | 14 mm | 12.4% |
| Thin steel, strong fan | 8 mm | 10.0% |

The benefit is largest when heat can travel a useful but incomplete distance through the metal — the sweet spot around L·m = 2.3.

---

## Browserbase Integration

FINCH integrates **Browserbase** — headless browser infrastructure for AI agents —
to run automated benchmark suites that:

1. Launch the tool in a cloud browser
2. Cycle through all material configurations
3. Capture screenshots of the evolved designs
4. Produce a markdown comparison report

### Setup

1. Add your API keys in the Freebuff **Keys** tab:
   - `BROWSERBASE_API_KEY`
   - `BROWSERBASE_PROJECT_ID`

2. Build the site:
   ```bash
   npm run build
   ```

3. Run the benchmark:
   ```bash
   npm run benchmark
   ```
   Or against a deployed URL:
   ```bash
   node scripts/browserbase-benchmark.mjs https://your-site.vercel.app
   ```

Results are saved to `benchmark_output/`.

---

## Built With

- Python 3 (NumPy, SciPy, Matplotlib)
- Vanilla JavaScript (no frameworks)
- HTML + CSS
- [Browserbase](https://www.browserbase.com) — headless browser infrastructure

---

## License

This project is for educational purposes (IB/MYP Personal Project).
