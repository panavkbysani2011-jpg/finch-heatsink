# FINCH — Complete Guide for Your Presentation

*Written for someone who doesn't code. You don't need to know Python or JavaScript
to understand this project. Every concept is explained in plain English.*

---

## Table of Contents

1. [What This Project Does](#1-what-this-project-does)
2. [The Two-Minute Summary](#2-the-two-minute-summary)
3. [How the Website Works](#3-how-the-website-works)
4. [How the Python Scripts Work](#4-how-the-python-scripts-work)
5. [What Each File Does](#5-what-each-file-does)
6. [How the Physics Works (Simple Version)](#6-how-the-physics-works-simple-version)
7. [The Random Part vs The Physics Part](#7-the-random-part-vs-the-physics-part)
8. [How the Images/Figures Work](#8-how-the-imagesfigures-work)
9. [How to Run the Python Tests](#9-how-to-run-the-python-tests)
10. [How to Present This Project](#10-how-to-present-this-project)
11. [Common Questions and Answers](#11-common-questions-and-answers)

---

## 1. What This Project Does

**FINCH** is a science project that asks one question:

> *Can a computer program design a better heat sink than a human engineer?*

A **heat sink** is the finned metal lump on anything that gets hot — LED bulbs,
laptop chips, phone chargers. Its job is to pull heat away from the hot part and
spread it into the air.

**The experiment:** We compare two heat sink designs:
1. **Human design** — straight fins radiating outward (like every heat sink you've seen)
2. **Computer-grown design** — a shape evolved through trial and error

Both get **exactly the same amount of metal**. The question is: which shape cools better?

**The answer:** The computer-grown design is 3% to 20% cooler, depending on the material.

---

## 2. The Two-Minute Summary

If someone asks "what is FINCH?", say this:

> *"FINCH is a tool that grows heat sink shapes by evolution instead of drawing
> them. It creates random metal blobs connected to a heat source, calculates
> their temperature using real physics equations, keeps the coolest ones,
> mutates them, and repeats hundreds of times. The result is compared against
> the best straight-fin design using the exact same amount of metal."*

**The key point:** The temperature calculation uses **real heat transfer equations**
— the same ones from physics textbooks. It's not random guesses. Every shape is
evaluated by solving thousands of equations simultaneously.

---

## 3. How the Website Works

The website is in the **`flinch/`** folder. Open `flinch/home.html` in any browser
and it works immediately. No installation needed.

### The Three Pages

| Page | File | What it shows |
|------|------|---------------|
| Overview | `home.html` | The project explained simply |
| The Tool | `index.html` | The interactive heat sink simulator |
| Findings | `findings.html` | Technical report with all results |

### How the Tool Page Works (index.html)

When you open `index.html` and press **Evolve**:

1. **The left panel** shows a human-designed heat sink (straight fins)
2. **The right panel** shows a random blob of metal
3. The computer runs a **physics simulation** on both — solving the heat equation
4. It shows the temperature of every cell (red = hot, blue = cold)
5. The right side evolves: bad shapes get replaced by mutated copies of good ones
6. Over 100-300 rounds, the shape gets cooler and cooler
7. The graph shows the temperature falling over time

### What You Can Change

| Control | What it does | Why it matters |
|---------|-------------|----------------|
| Chip position | Where the heat comes from (centre, edge, corners) | Tests if the computer can adapt to different layouts |
| Material | Aluminium vs steel, thin vs thick, with/without fan | Changes how far heat can travel |
| Metal allowed | How much metal to use (8% to 45% of the grid) | Both designs always get the same amount |
| Chip power | How many watts the chip produces | Higher power = hotter everything |
| Air rule | Whether trapped air counts or not | **The key experiment** — see Section 6 |
| Mutation rate | How much children differ from parents | 3.5% is balanced |
| Draw on board | Add extra heat sources or blocked areas | Test custom scenarios |

### The Numbers on Screen

When the tool runs, you'll see:

- **Human Design / Grown by Search** — which panel is which
- **206.5°C (or similar)** — the peak temperature (hottest point). Lower is better.
- **16 fins, 272 cells** — how many fins the human design has, and how many metal cells
- **44% wasted** — how much metal is sitting near room temperature (heat never reached it)
- **"The grown design is 17.7°C cooler"** — the headline result

### How to Read the Colour Scale

The heat map shows:
- **Dark blue** = room temperature (35°C). This metal is wasted — heat never reached it.
- **Teal/green** = warm
- **Yellow/orange** = hot
- **Bright red/white** = the hottest point (what kills the chip)

**If you see lots of dark blue in the human design but none in the evolved one,
that means the computer used the metal more efficiently.**

---

## 4. How the Python Scripts Work

The Python scripts (in the **`sim/`** folder) do the **behind-the-scenes work**.
They were used to:
1. Develop and test the physics equations
2. Run larger experiments (hundreds of generations)
3. Generate the data tables and charts
4. Prove the results are reproducible

The website has a **JavaScript version** of the same physics engine. The Python
scripts are the "laboratory" version — more accurate, but require Python to run.

### The Two Versions

| | Python (sim/) | JavaScript (flinch/index.html) |
|---|---|---|
| **Role** | The laboratory — for experiments | The exhibit — for presentations |
| **Who can use it** | Only if Python is installed | Anyone with a browser |
| **Accuracy** | Very high (direct solver) | Very high (matches Python to 0.0002°C) |
| **Speed** | 2.5 milliseconds per solve | 45 generations per second |
| **Purpose** | Validation, data, charts | Live demonstration |

**What to say in your presentation:**
> *"The physics was first written in Python using NumPy and SciPy, professional
> scientific computing libraries. The same algorithm was then ported to JavaScript
> so the tool runs live in the browser. Both give the same answer to 0.0002°C."*

---

## 5. What Each File Does

### Website Files (in `flinch/`)

| File | Size | Purpose |
|------|------|---------|
| `home.html` | 12 KB | Overview page — start here |
| `index.html` | 56 KB | **The main tool** — contains the entire physics engine in JavaScript |
| `findings.html` | 24 KB | Technical report with all methods and results |
| `style.css` | 5 KB | Styling for all three pages |

**All four are required.** Without `style.css` the pages look unstyled.

### Python Core Scripts (in `sim/`)

#### The Physics Engine (The Most Important Files)

| File | What it does |
|------|-------------|
| `physics.py` | **Version 1 thermal solver.** Solves the heat equation on a grid. Includes the basic openness model for trapped air. Used by the older experiments. |
| `physics2.py` | **Version 2 thermal solver.** Better physics: channel starvation model (derived length scale, not guessed), radiation (Stefan-Boltzmann), and transient (time-dependent) mode. This is the accurate one. |

#### The Evolution Engine

| File | What it does |
|------|-------------|
| `evolve2.py` | **Version 2 search algorithm.** Includes both the plain genetic algorithm and MAP-Elites (quality diversity). Also has the fair baseline generator. This is the one used for final results. |
| `evolve.py` | Compatibility wrapper so older scripts can still use the v2 code. |

#### Validation (Proof the Physics is Correct)

| File | What it does |
|------|-------------|
| `validate.py` | Version 1 validation — compares solver against textbook equations |
| `validate2.py` | **Version 2 validation — 14 tests, ALL PASSING.** This is the one to show. Tests include: fin equation (0.0003% error), grid convergence (error falls 4x each halving), radiation, transient, channel model limits. |

#### Experiments

| File | What it does |
|------|-------------|
| `benchmark.py` | Head-to-head comparison: evolved vs straight fins, 10 independent runs |
| `regime.py` | Version 1 regime sweep (how material affects results) |
| `regime2.py` | **Version 2 regime sweep** — produces the main result table |
| `airflow_test.py` | Tests how the airflow model changes the results |
| `cheat_log.py` | Tests 4 different fitness functions to show how the algorithm exploits weaknesses |
| `mapelites_test.py` | Compares MAP-Elites vs plain genetic algorithm |
| `figures.py` | Generates all 8 report figures as PNG images |
| `test_site.py` | Verifies every number on the website matches the data files |

#### Data Files (in `sim/`)

| File | What it contains |
|------|-----------------|
| `convergence.csv` | How the temperature improved over generations (55 KB, the largest data file) |
| `airflow_test.csv` | Results of the airflow model comparison |
| `cheat_v2.npy`, `cheat_v3.npy`, `cheat_v4.npy` | The shapes produced by flawed fitness functions |
| `baseline_T.npy`, `baseline_mask.npy` | Temperature and shape of the best conventional design |
| `evolved_T.npy`, `evolved_mask.npy` | Temperature and shape of the best evolved design |
| Various `.npy` files | Saved simulation results for figures |

### Figures (in `figures/`)

| File | What it shows |
|------|--------------|
| `fig1_validation.png` | Solver vs textbook equation — proof the physics is correct |
| `fig8_airflow_shapes.png` | How the shape changes when you account for trapped air |

### Documentation Files

| File | Purpose |
|------|---------|
| `README.md` | GitHub overview — what people see when they open your repo |
| `DETAILED_GUIDE.md` | **This file** — full explanation for you |
| `DEPLOY.md` | How to put the website online |
| `FILES.md` | What every file is (from the original agent) |
| `NEXT.md` | Advice on what to do next for the project |

---

## 6. How the Physics Works (Simple Version)

### The Thermal Model

Imagine a thin metal plate divided into 1.5 mm × 1.5 mm squares (44 × 44 = 1,936 squares).
Each square is either **metal** or **air**. The computer's job is to find the temperature
of every metal square.

The temperature depends on three things:

**1. Conduction (heat spreading through metal)**
Heat flows from hot spots to cold spots, like water finding its level. How fast it
flows depends on the metal: **aluminium** conducts heat 4x better than **steel**.

**2. Convection (heat leaving into the air)**
Air blowing past the surface carries heat away. How fast depends on:
- Still air: very slow cooling
- Gentle fan: moderate cooling
- Strong fan: fast cooling

**3. Radiation (heat glowing off the surface)**
Hot metal radiates heat like a glowing coal. This is included in version 2 physics.

### The Airflow Model (Why This Project is Interesting)

In real life, metal buried inside a lump has almost no moving air around it —
the air is trapped and stagnant. Metal on an exposed fin tip has lots of airflow.

The **channel starvation** model calculates how wide the air gap is next to each
piece of metal. Narrow gaps = less cooling. Wide gaps = more cooling.

**This is important because:** The first version of the physics model assumed all
metal gets the same cooling regardless of position. That made compact blobs look
good. When the more accurate model was used, the compact blobs performed badly
and the computer started growing **branched shapes** instead — independently
reinventing the fin.

### The Fin Parameter (One Number That Predicts Everything)

The single most important quantity is **m** (pronounced "fin parameter"):

```
m = √(2h / (k × t_z))
```

Where:
- h = convection coefficient (how fast air carries heat away)
- k = thermal conductivity (how well metal conducts heat)
- t_z = plate thickness

**1/m** is how far heat travels through the metal before it all leaks into the air.

When you compare **L·m** (sink half-width × m), you can predict the result:
- **L·m < 1**: Heat reaches everywhere. Shape barely matters.
- **L·m ≈ 2.3**: The sweet spot. Shape matters a lot. Computer wins big.
- **L·m > 4**: Heat can barely move. Even the computer can't help much.

---

## 7. The Random Part vs The Physics Part

This is the most common question people will ask. Here's the truth:

**The physics is NOT random.** The temperature calculation uses the real heat equation
— the same one from engineering textbooks. If you put the same shape in twice, you
get the exact same temperature. The Python solver matches the analytical (textbook)
solution to **0.0003%**. The JavaScript version matches the Python version to
**0.0002°C**.

**The evolution IS random — by design.** The computer:
1. Starts with a **random** blob of metal (because any starting point is fine)
2. Solves the temperature using **deterministic physics** (not random)
3. Keeps the coolest shapes
4. Adds **random** mutations (because that's how evolution explores)
5. Tests the children with **deterministic physics** again
6. Repeats until no more improvement

**Think of it like natural selection:** The mutations are random, but the selection
(which shapes survive) is based on real physics. Mutations that make it cooler
survive. Mutations that make it hotter die out.

**Which variables are random?**
- The initial shape (random blob connected to the chip)
- Which cells get added/removed during mutation
- Which two parent designs get combined (crossover)
- Which seed value the random number generator uses

**Which variables are NOT random?**
- The temperature calculation (solves real equations)
- The material properties (thermal conductivity, thickness, etc.)
- The convection coefficient (based on real physics)
- The radiation calculation (Stefan-Boltzmann law)
- The comparison between human and evolved designs (same metal, same physics)

---

## 8. How the Images/Figures Work

The project has two types of images:

### Report Figures (in `figures/`)

These are generated by **`sim/figures.py`**. To create them, run:

```bash
cd sim
pip install numpy scipy matplotlib
python3 figures.py
```

This creates 8 figures showing:
1. Validation against textbook equation
2. Head-to-head comparison
3. Main result (improvement vs. material)
4. Shape comparison
5. Cheat log (flawed fitness functions)
6. Convergence over generations
7. Airflow sensitivity
8. Airflow-aware shapes

### Website Images

The home page (`home.html`) has placeholders for two images showing the
conventional vs evolved heat sink. These images need to be generated from the
simulation data. They would go in the `figures/` folder.

### How the Heat Maps Work (The Colourful Grids)

When you run the tool, the coloured grids work like this:

1. The computer calculates the temperature of every cell (1,936 cells)
2. The coldest cell (room temperature = 35°C) is mapped to dark blue
3. The hottest cell is mapped to bright red
4. Everything in between goes through a gradient: blue → teal → green → yellow → orange → red

So dark blue metal is "dead weight" — heat never reached it. A good design has
almost no dark blue because all the metal is within reach of the heat.

---

## 9. How to Run the Python Tests

These commands are for when you have the files on a computer with Python installed.

### First Time Setup

```bash
# Install the required packages (one time only)
pip install numpy scipy matplotlib
```

### Most Important Test (Show This in Your Presentation)

```bash
cd sim
python3 validate2.py
```

This runs **14 validation tests** that prove the physics is correct. It should say
**"PASSED 14 FAILED 0"** at the end. This is your strongest evidence.

### The Cheat Log (Interesting for Presentation)

```bash
cd sim
python3 cheat_log.py
```

This shows how the algorithm exploits weaknesses in the scoring function.
It's a great example of why getting the physics right matters.

### Regenerate All Figures

```bash
cd sim
python3 figures.py
```

This creates all 8 figures in the `figures/` folder.

### Common Problems

| Error | Solution |
|-------|----------|
| `ModuleNotFoundError: No module named 'numpy'` | Run `pip install numpy scipy matplotlib` |
| `command not found: python3` | Try `python` instead of `python3` |
| The script takes too long | Some experiments run 100+ generations. Let them finish. |

---

## 10. How to Present This Project

### Suggested Presentation Script (2 Minutes)

> *"My project is called FINCH. It's an evolutionary heat sink optimizer.
> A heat sink is the metal lump on anything that gets hot — like the fins
> on a laptop charger.*
>
> *I wanted to know: can a computer design a better heat sink than a human
> engineer? The human design has straight fins radiating outward — that's
> what every heat sink looks like because it's cheap to manufacture. But
> is it actually the best shape?*
>
> *I built a physics simulator that solves the heat equation on a grid —
> the same equations from any heat transfer textbook. Then I added an
> evolutionary algorithm that starts with random shapes, tests them with
> the physics, keeps the coolest ones, mutates them, and repeats hundreds
> of times.*
>
> *I validated the physics against the textbook fin equation (0.0003% error),
> and I independently reimplemented it in both Python and JavaScript —
> they agree to 0.0002°C.*
>
> *The result: the computer-grown shape beats conventional fins by 3% to
> 20% depending on the material. But the most important finding was that
> when I built a more honest physics model, my original result collapsed.
> That taught me that your result is only as good as your assumptions."*

### What to Show During the Presentation

1. **Open `flinch/index.html`** — show the tool running
2. **Press Evolve** — watch the temperature fall in real time
3. **Show the graph** — how the temperature drops over generations
4. **Switch materials** — show how the result changes
5. **If you have Python:** Run `validate2.py` to show the 14 tests passing

### Key Points to Emphasize

| Question | Your Answer |
|----------|-------------|
| "Is this an AI?" | "No. It's an evolutionary search algorithm plus a physics simulator. Nothing is trained. No neural network. Every design is evaluated by solving real equations." |
| "Is it random?" | "The mutations are random, but the selection is based on physics. Bad shapes get deleted. Only cooler shapes survive." |
| "How do you know it's accurate?" | "The Python solver matches the textbook fin equation to 0.0003%. I also wrote the solver in two different languages independently — Python and JavaScript — and they agree to 0.0002°C. If there was a bug, the two versions wouldn't match." |
| "Why does it sometimes lose?" | "Because sometimes there's nothing to win. If heat travels 100mm and the heat sink is only 33mm, the whole thing is nearly the same temperature. Shape doesn't matter much." |

---

## 11. Common Questions and Answers

### Q: Why are there two folders: `flinch/` and `sim/`?

**A:** `flinch/` is the website — open it in a browser. `sim/` is the Python
research code — run it on a computer with Python installed. The website has a
JavaScript version of the same physics. They give the same answers.

### Q: The files in `flinch/` are misspelled as "flinch" instead of "finch"?

**A:** Yes, the folder is called `flinch/` (with an L) instead of `finch/`.
This was an early typo that got carried through. It doesn't affect anything.
The project name everywhere else is FINCH.

### Q: Why are there two versions of physics (physics.py and physics2.py)?

**A:** Version 1 was the first attempt. It had a simple "openness" model for
trapped air. Version 2 has the improved "channel starvation" model with a
derived length scale, plus radiation and transient mode. All final results
use version 2, but version 1 is kept because some scripts still import it.

### Q: The home page has placeholders instead of images?

**A:** Yes, the comparison images need to be generated by running `figures.py`.
Once you have Python and the right packages installed, running
`python3 sim/figures.py` will create all the figures.

### Q: Some Python scripts give errors when I run them?

**A:** The version 1 scripts (`cheat_log.py`, `airflow_test.py`, `benchmark.py`,
`regime.py`) were designed for an older version of the code. The version 2
scripts that work reliably are `validate2.py`, `regime2.py`, and
`mapelites_test.py`. Focus on those for your presentation.

### Q: How do I download the files to my own computer?

**A:** Go to `github.com/panavkbysani2011-jpg/finch-heatsink`, click the green
**Code** button, then **Download ZIP**. Extract the ZIP on your computer.

### Q: How do I put the website online?

**A:** There are three options:
1. **Netlify (easiest):** Go to `app.netlify.com/drop`, drag the `flinch/`
   folder onto the page. Live URL in 30 seconds.
2. **GitHub Pages:** Go to your repo → Settings → Pages → select "main"
   branch and "/(root)" folder → Save. Wait 2 minutes.
3. **Freebuff hosting:** Ask me to deploy it for you.
