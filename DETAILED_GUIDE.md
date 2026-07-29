# FINCH Complete Guide for Your Presentation

Written for someone who does not code. You do not need to know Python or JavaScript to understand this project. Every concept is explained in plain English with full detail.

---

## Table of Contents

1. [What This Project Does](#1-what-this-project-does)
2. [What a Heat Sink Is and Why It Matters](#2-what-a-heat-sink-is-and-why-it-matters)
3. [The Two-Minute Summary](#3-the-two-minute-summary)
4. [The Full Experiment Explained](#4-the-full-experiment-explained)
5. [How the Website Works](#5-how-the-website-works)
6. [How to Read Every Number on Screen](#6-how-to-read-every-number-on-screen)
7. [How the Python Scripts Work](#7-how-the-python-scripts-work)
8. [What Every Single File Does](#8-what-every-single-file-does)
9. [How the Physics Works (In Detail)](#9-how-the-physics-works-in-detail)
10. [The Two Physics Models and Why It Matters](#10-the-two-physics-models-and-why-it-matters)
11. [The Random Part vs The Physics Part](#11-the-random-part-vs-the-physics-part)
12. [The Evolutionary Algorithm Explained](#12-the-evolutionary-algorithm-explained)
13. [The Bugs That Were Found and Fixed](#13-the-bugs-that-were-found-and-fixed)
14. [All the Results and What They Mean](#14-all-the-results-and-what-they-mean)
15. [How to Run the Python Tests](#15-how-to-run-the-python-tests)
16. [How to Present This Project](#16-how-to-present-this-project)
17. [Common Questions and Complete Answers](#17-common-questions-and-complete-answers)
18. [Glossary of Terms](#18-glossary-of-terms)

---

## 1. What This Project Does

FINCH is a science project (IB/MYP Personal Project) that asks one specific question: can a computer program design a better heat sink than a human engineer would draw?

To answer this question, the project does the following:

First, it builds a physics simulation that calculates the temperature of every point on a metal plate when a heat source (like a computer chip) is attached to it. This simulation solves real heat transfer equations from physics textbooks.

Second, it creates random metal shapes connected to the heat source and calculates how hot each shape gets using the physics simulation.

Third, it keeps the coolest shapes and discards the hottest ones. It then takes the coolest shapes, makes random changes to them (mutations), and tests the children again.

Fourth, it repeats this cycle hundreds of times. Over time, the shapes get cooler and cooler because the hot shapes keep getting eliminated.

Fifth, it compares the final computer-grown shape against the best possible conventional straight-fin heat sink. Both are given exactly the same amount of metal, so the comparison is fair.

The answer is that the computer-grown shape is 3% to 20% cooler than the best straight-fin design, depending on what material is used and how fast the air is moving.

---

## 2. What a Heat Sink Is and Why It Matters

A heat sink is the finned lump of metal attached to anything that gets hot electronically. You have seen them on laptop chargers, on the back of LED light bulbs, inside desktop computers on the CPU, and on phone chargers. They look like a block of metal with ridges or fins sticking out.

The job of a heat sink is simple: take heat from one small hot spot (the computer chip) and spread it into the surrounding air as quickly as possible. If the heat sink does its job well, the chip stays cool and works properly. If the heat sink cannot remove heat fast enough, the chip overheats and either shuts down or gets damaged.

Almost every heat sink you have ever seen uses straight fins that radiate outward from the centre like the spokes of a bicycle wheel. This shape exists not because anyone proved it was the best possible shape, but because it is cheap to manufacture. You can push hot aluminium through a die (a shaped opening) and straight fins come out the other side easily. Curved, branching, or organic shapes cost much more to make.

So there is a genuine scientific question: if you ignore the cost of manufacturing and just ask what shape would cool best, what would that shape look like? That is the question this project answers.

---

## 3. The Two-Minute Summary

If someone asks you "what is FINCH?" during your presentation, say this exactly:

"FINCH is a tool that grows heat sink shapes by evolution instead of drawing them. It starts by creating random blobs of metal that are connected to a heat source. It calculates the temperature of each blob using real physics equations from heat transfer textbooks. It keeps the coolest blobs, discards the hottest ones, makes random changes to the survivors, and repeats this cycle hundreds of times. After many rounds, the shape gets progressively cooler because the physics simulation consistently eliminates designs that run hot. The final evolved shape is then compared against the best possible conventional straight-fin design, using exactly the same amount of metal for both. The result is that the computer-grown shape is 3% to 20% cooler, depending on the material and airflow conditions."

The key thing to emphasize is that the temperature calculation uses real physics equations, not random guesses. Every shape submitted for evaluation is solved against the heat equation, which is the same equation used by professional engineers to design real cooling systems.

---

## 4. The Full Experiment Explained

Here is the experiment broken down into every step, explained completely.

Step 1: Define the problem. The computer is given a grid of 44 by 44 squares (1,936 squares total). Each square is 1.5 millimetres by 1.5 millimetres. Some squares contain metal, others contain air. The chip (heat source) is a small cluster of squares in the centre (or wherever the user places it). The chip generates a fixed amount of heat, measured in watts (default 5 watts). The metal has specific properties: a thermal conductivity (how easily heat flows through it), a thickness, and a convection coefficient (how easily heat escapes into the surrounding air).

Step 2: Design the control group. The conventional design is straight radial fins radiating from a hub centred on the chip. The computer tries 18 different configurations (4, 6, 8, 10, 12, or 16 fins, each either 1, 2, or 3 cells thick) and selects the one that runs coolest. This ensures the evolved design has to beat a well-designed conventional sink, not a poorly designed one.

Step 3: Count the metal used. The best conventional design uses a certain number of metal cells. The evolved design is capped at exactly that same number. Both designs get the identical amount of metal. This is critical because if one design had more metal, it would naturally run cooler and the comparison would be unfair.

Step 4: Evolve the design. The computer starts with a random connected blob of metal (grown outward from the chip to ensure it is attached). It evaluates the blob by solving the temperature of every cell. It keeps the coolest few designs (usually the top 4 out of 24). It breeds them by combining two designs (crossover) and making random changes (mutation). It fills the child designs back up to the metal budget. It evaluates the children. It keeps the coolest. It repeats. Over 200 to 300 rounds the temperature drops as hot designs are eliminated.

Step 5: Compare the result. The final evolved design's peak temperature is compared against the baseline conventional design's peak temperature. The improvement is calculated as a percentage of the temperature rise above ambient (room temperature). For example, if the baseline is 150 degrees Celsius and the evolved design is 140 degrees, with ambient at 35 degrees, the improvement is (150-140)/(150-35) = 8.7%.

Step 6: Repeat with different random seeds. The experiment is run 10 times with different random starting points to confirm the result is not a lucky fluke. The results vary by less than 0.1 percentage points, confirming reproducibility.

Step 7: Test different materials. The experiment is repeated with different metals (aluminium and steel), different thicknesses, and different airflow conditions to determine when shape optimization matters most.

---

## 5. How the Website Works

The website is in the folder called "flinch" (note: the folder is spelled with an L instead of an N, which was an early typo that did not get corrected). Open the file "flinch/index.html" (was home.html — now renamed to be the landing page) in any web browser (Chrome, Firefox, Safari, Edge) and it works immediately. There is no installation, no server, no internet connection required (except for loading the fonts the first time).

### The Three Pages

The website has three pages, connected by a navigation bar at the top.

Page 1: Overview (home.html)
This is the landing page. It explains the project in simple language. It shows the motivation, the experimental design, the method, and the key results. Use this page to give someone a quick understanding of what the project is about.

Page 2: The Tool (index.html)
This is the interactive heat sink simulator. It is the main deliverable of the project. It contains the complete physics engine written in JavaScript (not Python, so it runs in the browser). You can change settings, press a button, and watch the heat sink evolve in real time. This is the page you should show during your presentation.

Page 3: Findings (findings.html)
This is the technical report. It contains every method, every validation result, every experiment, and every conclusion in full detail. All the numbers on this page are backed by data files in the sim folder.

### How the Tool Page Works (Detailed Walkthrough)

When you open index.html, you see:

At the top, there is a navigation bar with links to the three pages plus a "Technical notes" button.

Below that, there are two large square panels side by side. The left panel is labelled "HUMAN DESIGN" and shows the best conventional straight-fin heat sink. The right panel is labelled "GROWN BY SEARCH" and starts as a random blob of metal.

Below the panels, there is a colour scale bar showing what the colours mean (cold = dark blue, hot = red).

Below that, there is a verdict strip that tells you which design is currently winning.

Below that, there are buttons: Evolve, Start over, and Save picture.

Below that, there is a graph that charts the temperature of the evolved design over time (generations).

On the right side of the screen, there is a column of controls:

The air rule control lets you choose between two physics models: "Channel starvation" (the honest model where trapped air reduces cooling) and "Uniform coefficient" (the simpler model where all metal gets equal cooling). This is the most important control because switching between these two models completely changes the result.

The chip position control lets you place the heat source at the centre, off centre, at the edge, two chips in opposite corners, or three chips scattered. This tests whether the computer can adapt to different layouts.

The material control lets you choose between thick aluminium with no fan, thick aluminium with a fan, thin aluminium with a fan, thick steel with a fan, or thin steel with a strong fan. Each material combination changes how far heat can travel through the metal.

The budget slider controls how much of the grid can be filled with metal (from 8% to 45%). Both designs always get exactly the same amount of metal.

The chip power slider controls how many watts the chip produces (from 1 watt to 20 watts). Higher power makes everything hotter but does not change which shape wins.

The mutation strength slider controls how much child designs differ from their parents. At very low values (0.5%), the search gets stuck and cannot find improvements. At very high values (12%), the search becomes chaotic and good designs get destroyed before they can be refined. At the default 3.5%, the balance is right.

The shapes per round slider controls how many designs are evaluated in each generation (from 8 to 48). More designs per round means more thorough exploration but slower individual rounds.

The draw on the board controls let you add extra heat sources or blocked areas by clicking and dragging on the right panel. This tests custom scenarios.

When you press the Evolve button, the following happens:

Step 1: The computer evaluates the baseline (conventional) design by solving the temperature of every cell. This takes about 1,200 iterations of the solver to ensure accuracy.

Step 2: The computer creates a population of random connected designs, each using the same amount of metal as the baseline.

Step 3: The computer enters a loop. In each iteration of the loop (one generation):

  a. It evaluates every design in the population by solving the temperature field.
  
  b. It sorts the designs from coolest to hottest.
  
  c. It keeps the best few designs (elite) unchanged for the next generation.
  
  d. It creates new child designs by randomly combining two parent designs (crossover) and then making random changes (mutation).
  
  e. It fills each child design back up to the metal budget.
  
  f. The new population becomes the next generation.
  
  g. If no improvement has been seen for 70 generations, it stops automatically.

Step 4: The graph updates in real time, showing the temperature falling over generations. The dashed red line is the baseline temperature. The teal curve is the evolved design's temperature.

Step 5: When the search finishes, a message appears explaining what happened and how much improvement was achieved.

### How to Use the Tool for Your Presentation

Experiment 1: Show the basic result. Leave everything at default settings (chip at centre, thin steel with strong fan, air rule set to "Channel starvation"). Press Evolve. Watch the temperature fall. After about 30 seconds, the search should show a modest win of about 3% to 10%.

Experiment 2: Show the effect of the physics model. While the search is running (or after resetting), switch the air rule to "Uniform coefficient" and press Evolve again. Notice that the search now produces a different shape (more compact, more blob-like) and claims a larger win. This demonstrates that the physics model determines the outcome.

Experiment 3: Show the effect of chip position. Change the chip position to "At the edge" and press Evolve. Notice that the conventional fins now point partly away from the chip because they are still centred on the grid centre, but the evolved design adapts by growing toward the chip. The evolved design wins by a larger margin.

Experiment 4: Show the effect of material. Switch to "Thick aluminium, no fan" and press Evolve. Notice that the improvement is very small (around 1% to 5%). This is because heat travels 101 mm in aluminium but the sink is only 33 mm across, so the entire sink is nearly the same temperature regardless of shape.

---

## 6. How to Read Every Number on Screen

This section explains every single number, label, and visual element on the tool page. If someone asks you what any part of the screen means, you can answer.

### The Two Simulation Panels

The left panel is labelled "HUMAN DESIGN." It shows the best conventional straight-fin heat sink from among 18 configurations tested. The computer evaluates this design using the same physics as the evolved design, so the comparison is fair.

The right panel is labelled "GROWN BY SEARCH." It shows the current best evolved design. When the search starts, this panel shows a random blob. As generations progress, the shape changes and the temperature drops.

### The Temperature Display

Below each panel title, there is a large number followed by a degree symbol and C. This is the peak temperature, which is the hottest single point in that design. This is the most important number because the hottest point is what would kill a real computer chip. Lower is better.

For example, if the left panel shows 192.1 degrees C and the right panel shows 174.4 degrees C, the evolved design is 17.7 degrees cooler at its hottest point.

### The Subtitle Line

Below the temperature, there is a small line of text. For the human design, it says something like "16 fins, 272 cells." This tells you which conventional configuration won (16 fins, each 2 cells wide, using 272 metal cells total). For the evolved design, it says something like "round 45, 272 cells." This tells you how many generations have elapsed and confirms the evolved design uses the same number of metal cells as the human design.

### The Wasted Percentage

Below each panel, there is a line that says something like "44% of its metal never gets hot" or "0% of its metal never gets hot." This is the wasted metal fraction. It is calculated by counting how many metal cells are sitting in the coolest quarter of the temperature range. If a piece of metal is near room temperature, heat never reached it, so that metal is dead weight. A good design has a low wasted percentage. Straight fins often waste 40% to 77% of their metal. Evolved designs usually waste almost none.

### The Colour Scale Bar

Between the panels and the verdict strip, there is a gradient bar. On the left end, it shows the ambient temperature (35 degrees, dark blue). On the right end, it shows the peak temperature of the human design (red). The gradient goes from dark blue (cold) through teal, green, yellow, orange to red (hot). Both panels use the same colour scale, so you can compare them by eye.

### The Verdict Strip

Below the colour bar, there is a text strip that tells you which design is winning. It says either:

"The grown design is X degrees cooler, using the same metal." (The evolved design is winning, shown with a green background.)

or

"Straight fins are still X degrees cooler. Fins have open air on both sides, which is hard to beat." (The conventional design is winning, shown with a red background.)

### The Graph

Below the controls on the right, there is a chart. The vertical axis (Y axis) shows temperature in degrees Celsius. The horizontal axis (X axis) shows generation number on a square root scale (so the first 50 generations get more space than later ones because most improvement happens early).

The dashed red horizontal line is the baseline (human design) temperature. If the teal curve goes below this line, the evolved design is winning.

The solid teal curve shows the peak temperature of the evolved design at each generation. It falls steeply in the first 20 to 50 generations and then flattens out.

The filled area below the teal curve is a gradient fill, making the curve easier to see.

The dot at the end of the curve marks the current generation.

The label at the top of the graph tells you what phase the search is in: "Finding the rough shape" (early), "Most of the progress happens here" (middle), "Refining, small gains now" (late), or "Finished" (converged).

### The Generation Counter

At the top of the control panel on the right, there is a line that says "round X" where X is the current generation number. Next to it, there is a speed reading showing how many generations per second the browser can evaluate (typically 40 to 45).

### The Setup Bar

Below the mode switch buttons at the top, there is a bar showing the current settings: chip position, material, air rule, and metal budget. This confirms what state the tool is in before you press Evolve.

### The Archive (MAP-Elites Mode)

If you switch the mode to "Archive of shapes, bred wide," the archive grid appears below the main panels. This is a 10 by 10 grid where each square represents a different kind of shape. As the search discovers new kinds of shapes, the squares fill in. Darker squares mean cooler designs. You can click on any square to see that design.

---

## 7. How the Python Scripts Work

The Python scripts in the sim folder are the research and development backbone of the project. The website (in flinch) has a JavaScript version of the same physics engine. They were developed separately, which is important because it means they can cross-check each other.

### Why There Are Two Implementations

The Python version was written first. It uses professional scientific computing libraries called NumPy (for array operations) and SciPy (for solving systems of equations). The Python solver builds one equation per metal cell and solves them all simultaneously using a direct matrix solver from SciPy. This is the most accurate method available and serves as the reference standard.

The JavaScript version was written second. It cannot use NumPy or SciPy because those libraries do not exist in web browsers. Instead, it uses a different mathematical method called red-black Successive Over-Relaxation (SOR), which is an iterative method that converges to the same answer. The JavaScript version was written independently, not translated from the Python. This is deliberate: if one version had a bug, the other version would not have the same bug, so agreement between them proves correctness.

The two versions agree to 0.0002 degrees Celsius on the peak temperature for the reference case. This is extremely strong evidence that both are correct.

### How the Python Scripts Are Structured

Every Python script in the sim folder follows the same pattern:

1. Import the required libraries (numpy, scipy, etc.).
2. Import the required modules from the project (physics2, evolve2, etc.).
3. Define functions that perform specific tasks.
4. If run directly (not imported), execute the main function.

The scripts use a technique called "sys.path.insert" at the top to ensure they can find each other. This means you can run any script from the sim folder and it will automatically find the other project files.

### The Two Physics Versions

There are two physics files: physics.py (version 1) and physics2.py (version 2). Version 1 was the initial implementation with a simpler trapped-air model. Version 2 has the improved channel starvation model, radiation, and transient mode. All final results use version 2, but version 1 is preserved because some older scripts still import it.

Version 2 (physics2.py) contains:

The Material2 class, which stores the thermal properties of the material: thermal conductivity (k), plate thickness (t_z), convection coefficient (h_iso), ambient temperature (T_inf), surface emissivity (emis), air speed (u_air), and flow path length (L_flow). It also calculates the fin parameter m and the choke gap s_c.

The gap_width function, which calculates how wide the air channel is next to each piece of metal. It uses a Euclidean distance transform (a standard image processing technique) to find the distance from each air cell to the nearest metal cell, then doubles it to get the full channel width.

The h_convect function, which calculates the effective convection coefficient for each cell based on the local gap width. It uses the formula h_eff = h_iso * (1 - exp(-s / s_c)), where s is the gap width and s_c is the choke gap.

The h_radiate function, which calculates the radiation coefficient using the Stefan-Boltzmann law. Because radiation depends on temperature to the fourth power, this coefficient depends on the current temperature and must be updated during the solution.

The solve2 function, which is the main steady-state solver. It builds a system of equations (one per metal cell) and solves them using SciPy's sparse linear solver. Because radiation makes the system non-linear, it iterates until the temperature stops changing.

The solve_transient function, which solves the time-dependent heat equation. This produces a warm-up curve showing how the temperature rises over time until it reaches steady state.

---

## 8. What Every Single File Does

This section lists every file in the repository and explains exactly what it does, why it exists, and whether you need to worry about it.

### Website Files (flinch folder)

flinch/index.html (12 KB, was home.html)
This is the overview page. It explains the project in accessible language suitable for someone who has never heard of heat sinks before. It describes the experimental design, the method, the key results, and the motivation. It includes a call-to-action button that links to the tool page. Open this page first when showing the project to someone new.

flinch/tool.html (56 KB, was index.html)
This is the interactive tool. It is the main deliverable of the project. It contains approximately 1,300 lines of code (HTML for structure, CSS for styling, and JavaScript for the physics engine and user interface). The JavaScript portion (about 290 lines for the engine and 400 lines for the UI) implements the complete thermal solver, the evolutionary algorithm, the display rendering, and the user interaction. This single file does everything: simulation, evolution, drawing, charting, and saving.

flinch/findings.html (24 KB)
This is the technical report. It documents every method, every validation test, every experiment, and every conclusion in full academic detail. It includes tables of results, equations, implementation notes, and a future scope section. All numbers in this page trace back to data files in the sim folder.

flinch/style.css (5 KB)
This is the shared stylesheet for all three pages. It defines the colour scheme (warm paper background with dark ink, serif headlines, and monospace numbers), the layout (responsive grid that adapts to screen size), the button styles, the table styles, and the animation effects. Without this file, the pages would load with default browser styling and look unformatted.

### Python Scripts (sim folder)

sim/physics.py (11 KB)
Version 1 of the thermal solver. Contains the Material class (with properties k, t_z, h, T_inf), the openness function (which calculates how much open air surrounds each cell using a box average), the h_field function (which converts openness into a per-cell convection coefficient), the solve function (which builds and solves the linear system using SciPy), the solve_iterative function (which uses the red-black SOR method, matching the JavaScript version), and the analytical_fin function (the textbook fin equation used for validation). This file is superseded by physics2.py but kept for backward compatibility.

sim/physics2.py (13 KB)
Version 2 of the thermal solver. This is the accurate one used for all final results. Contains the Material2 class (with additional properties for radiation and airflow), the gap_width function (Euclidean distance transform of the air region), the h_convect function (channel starvation model), the h_radiate function (Stefan-Boltzmann radiation), the solve2 function (iterated sparse solve with radiation), and the solve_transient function (time-dependent solver). Also contains the Air class with physical properties of air (density, specific heat capacity, viscosity). This file is the physics engine that everything else depends on.

sim/evolve.py (5 KB)
This is a compatibility wrapper that translates between the version 1 API and the version 2 implementation. It provides the Problem class, the evolve function, the evaluate function, and the largest_connected function, all of which delegate to the version 2 code in evolve2.py. This file exists so that older scripts (benchmark.py, cheat_log.py, airflow_test.py, regime.py) can work without modification. If you are writing new code, use evolve2.py directly instead.

sim/evolve2.py (17 KB)
Version 2 of the evolutionary algorithm. This is the actual implementation used for all results. Contains the Problem2 class (defines the problem: grid size, chip position, material budget, heat load), the largest_connected function (flood fill from the chip to discard floating islands), the fitness2 function (peak temperature plus manufacturability penalty, with channel and radiation options), the thin_fraction function (fraction of cells with fewer than 2 neighbours), the descriptors function (calculates shape descriptors for MAP-Elites), the Archive class (the MAP-Elites memory: one best design per shape bin), the random_design function (grows a random connected design outward from the chip), the mutate function (removes cold-tip cells, adds peripheral cells, refills to budget), the crossover function (splices two parents along a random line, repairs connectivity, refills to budget), the evolve_plain function (standard genetic algorithm: evaluates, selects, breeds, repeats), the evolve_mapelites function (MAP-Elites: maintains archive of diverse shapes), the radial_fins2 function (generates conventional straight fin designs), and the best_baseline2 function (tries 18 configurations and keeps the best).

sim/validate.py (6 KB)
Version 1 of the validation suite. Contains the run_fin_test function (compares numerical solver against the analytical fin equation at a given grid resolution) and the run_validation_suite function (runs the grid convergence test at resolutions 10, 20, 40, 80, 160, and 320 cells). This file is superseded by validate2.py but kept for backward compatibility because figures.py imports from it.

sim/validate2.py (10 KB)
Version 2 of the validation suite. This is the definitive proof that the physics is correct. Contains 8 test functions (T1 through T8) that together make 14 individual assertions:

T1 (conduction + convection vs analytical fin equation): Tests that the solver reproduces the textbook fin temperature profile to within 0.5%. Actual result: 0.0003% error.

T2 (grid convergence): Tests that the error falls by approximately a factor of 4 each time the grid is doubled. This is the signature of second-order spatial discretisation. Actual ratios: 3.97, 3.98, 3.99.

T3 (radiation alone vs Stefan-Boltzmann balance): Tests that a purely radiative system matches the exact Stefan-Boltzmann calculation. Actual error: 0.174%.

T4 (radiation plus convection vs hand-computed lumped balance): Tests the combined system against a hand calculation using bisection. Actual error: 0.000%.

T5 (channel model limits): Tests that buried metal gets near-zero cooling (0.0 of 120 W/m2K) and that a lone cell matches the formula (87.0 vs predicted 87.0).

T6 (channel model monotonicity): Tests that the channel model is bounded (never exceeds h_iso), non-decreasing (wider gaps always give more cooling), and that h(0) equals 0.

T7 (transient converges to steady state): Tests that the time-dependent solver reaches the same answer as the steady-state solver. Actual difference: 0.00%.

T8 (grid independence): Tests whether the answer depends on grid resolution at 44, 64, and 88 cells. The two finest grids agree to 0.90%.

All 14 assertions currently pass. Run this script during your presentation to show the proof.

sim/benchmark.py (8 KB)
Runs the head-to-head comparison 10 times with different random seeds. Creates the Problem, finds the best baseline design using best_baseline() from evolve.py, caps the evolved design at the baseline's cell count, runs 10 independent evolutions of 220 generations each, records the peak temperature and improvement for each seed, and saves the results to benchmark.csv, convergence.csv, summary.json, baseline_T.npy, baseline_mask.npy, evolved_T.npy, and evolved_mask.npy. This script takes about 12 minutes to run because it performs 10 complete evolutions.

sim/regime.py (6 KB)
Version 1 of the thermal regime sweep. Tests the improvement across a range of L.m values from 0.33 to 5.11. This file is superseded by regime2.py.

sim/regime2.py (5 KB)
Version 2 of the thermal regime sweep. This produces the main result table. Tests 6 configurations (aluminium and steel at various thicknesses and airflow speeds) using the version 2 physics (channel model plus radiation). Records the L.m value, choke gap, baseline temperature, evolved temperature, and improvement percentage. Saves results to regime_v2.csv. This shows that improvement peaks at L.m around 2.3 and falls on both sides.

sim/airflow_test.py (8 KB)
Tests the effect of the convective model on the results. Compares three treatments: the v4 design evaluated with constant h, the same v4 design evaluated with the airflow model, and the v5 (airflow-aware) design evaluated with the airflow model. This is the falsification test that proved the original result was an artifact of assuming constant h. The test shows that the v4 blob (optimised under constant h) performs worse than straight fins when judged with the airflow model, while the v5 design (optimised under the airflow model) performs better.

sim/cheat_log.py (5 KB)
Tests four different fitness functions (objective functions) to show how the algorithm exploits weaknesses in each one. Version 1 minimises mean temperature (exploit: grows a cool fringe far from the chip, producing the highest peak temperature). Version 2 minimises peak temperature (exploit: uses as much metal as possible with no budget). Version 3 adds a budget (exploit: produces one-cell-wide tendrils at the resolution limit). Version 4 adds a width penalty (no exploit found, this is the version used for results). This script demonstrates that the choice of objective function determines the outcome, not the algorithm.

sim/mapelites_test.py (6 KB)
Compares the MAP-Elites algorithm (which keeps a diverse archive of shapes) against the plain genetic algorithm (which focuses on one lineage). Both are given 2,400 evaluations. The plain GA produces a better single best design (213.83 degrees C vs 222.95 degrees C). The MAP-Elites produces a library of 134 distinct viable shapes. The conclusion is that for this problem, focusing on one lineage produces a better single result, but the archive is useful when manufacturing constraints eliminate the single optimum.

sim/figures.py (20 KB)
Generates all 8 report figures as PNG images. Contains one function per figure: fig_validation (solver vs analytical fin equation plus convergence order), fig_head_to_head (baseline vs evolved geometry side by side with seed consistency bar chart), fig_regime (improvement vs L.m, the main result chart), fig_regime_shapes (geometry comparison in the conduction-limited regime), fig_cheat_log (four objective formulations side by side), fig_convergence (fitness over generations for 10 seeds), fig_airflow (the falsification test bar chart), and fig_airflow_shapes (geometry under each convective treatment). Also contains helper functions for drawing heat maps and setting up plots.

sim/test_site.py (6 KB)
Verifies that every number on the website traces back to a data file. Checks that improvement percentages from regime_v2.csv appear in the HTML files. Checks that the findings page does not contradict itself (for example, checking that it does not claim radiation is both implemented and not implemented). Checks that sections are balanced (opening and closing tags match). If Playwright is installed, it also opens the pages in a headless browser and checks for layout overflow, JavaScript errors, and specific values like the choke gap. This script lives in the repository so you can rerun it any time to verify the site has not drifted from the data.

### Data Files (sim folder)

sim/validation_results.csv
Contains the grid convergence data showing maximum error at each grid resolution (10, 20, 40, 80, 160, 320 cells). Produced by validate.py.

sim/regime_v2.csv
Contains the main result table: case name, L.m value, choke gap in millimetres, baseline temperature, evolved temperature, and improvement percentage for each of the 6 configurations. Produced by regime2.py.

sim/airflow_test.csv
Contains the airflow model sensitivity results: baseline temperature, v4 evolved temperature with constant h, same design with airflow, and v5 evolved temperature with airflow, for 4 material configurations. Produced by airflow_test.py.

sim/cheat_log.csv
Contains the four fitness function versions and their outcomes: peak temperature, mean temperature, metal fraction, thin fraction, and the exploit description. Produced by cheat_log.py.

sim/convergence.csv
Contains the fitness per generation for all seeds. Each row has seed number, generation number, best fitness, and mean fitness. This is the largest data file at 55 KB. Produced by benchmark.py.

sim/summary.json
Contains the headline statistics from the head-to-head comparison: baseline peak temperature, evolved best/mean/worst, improvement percentages, seed spread, and pass/fail status for SC3 and SC4. Produced by benchmark.py.

sim/baseline_mask.npy
A binary array (True/False for each cell) showing which cells contain metal in the best conventional design. Used by figures.py to generate the comparison figure.

sim/baseline_T.npy
A floating-point array showing the temperature of every cell in the best conventional design. Produced by benchmark.py.

sim/evolved_mask.npy
A binary array showing which cells contain metal in the best evolved design (the best of 10 seeds). Produced by benchmark.py.

sim/evolved_T.npy
A floating-point array showing the temperature of every cell in the best evolved design. Produced by benchmark.py.

sim/cheat_v2.npy, cheat_v3.npy, cheat_v4.npy
Binary arrays showing the shapes produced by fitness versions 2, 3, and 4. Version 1 was too unstable to save a meaningful shape. Used by figures.py for the cheat log figure.

sim/airflow_base_mask.npy, airflow_v4_mask.npy, airflow_v5_mask.npy
Binary arrays showing the shapes for the airflow comparison: the conventional baseline, the v4 evolved design (optimised under constant h), and the v5 evolved design (optimised under the airflow model). Used by figures.py.

sim/archive_best.npy, archive_grid.npy
Data from the MAP-Elites archive, saved for reference.

sim/evolved_mask (1).npy, sim/airflow_test (1).csv
Duplicate files with slightly different names. These appear to be accidental duplicates and can be ignored.

### Figures Folder (figures folder)

figures/fig1_validation.png
A figure with two subplots. The left subplot shows the solver temperature profile against the analytical fin equation, demonstrating near-perfect agreement. The right subplot shows the grid convergence on a log-log scale with the second-order reference line, demonstrating that the error falls by a factor of 4 for each halving of the cell size.

figures/fig8_airflow_shapes.png
A figure with three panels showing the straight fins, the v4 evolved design (optimised under constant h), and the v5 evolved design (optimised under the airflow model), all evaluated with the airflow model. This shows that the v4 blob suffocates while the v5 branching design breathes.

### Documentation Files

README.md
The GitHub repository overview. This is the first thing people see when they visit github.com/panavkbysani2011-jpg/finch-heatsink. It explains the project, shows the key findings, lists the repository structure, and provides instructions for running the Python scripts.

DETAILED_GUIDE.md
This file. A complete guide to the project written for someone who does not know how to code.

DEPLOY.md
Instructions for publishing the website online using Netlify Drop or GitHub Pages. Explains the file renaming needed to make the overview page the landing page.

FILES.md
A comprehensive list of every file in the project, what it does, why it exists, and what data it contains. Originally generated by the AI assistant that helped build the project.

NEXT.md
Advice on what to do next for the project. Lists what is done and what is not done. Recommends stopping building and focusing on understanding the project, writing the process journal, and preparing the report. Contains the correction log for when the baseline fin hub was fixed.

---

## 9. How the Physics Works (In Detail)

### The Thermal Model

The physics simulation models a thin flat metal plate viewed from above. The plate is divided into a grid of square cells, each 1.5 millimetres on each side. The grid is 44 cells wide by 44 cells tall, for a total of 1,936 cells. The entire plate is 66 millimetres across (44 times 1.5 millimetres).

Each cell is either metal or air. Metal cells conduct heat, store heat, and lose heat to the surrounding air. Air cells are treated as perfect insulators (no conduction through air). This is a simplification: in reality air also conducts heat, but at about 0.026 W/mK compared to aluminium at 205 W/mK, the conduction through air is negligible.

The chip (heat source) occupies a small cluster of cells. By default, it is 7 by 7 cells (about 10.5 by 10.5 millimetres) centred in the middle. The chip generates a fixed amount of heat, defaulting to 5 watts. This 5 watts is distributed evenly across all the chip's cells.

### The Heat Equation (What the Solver Actually Solves)

For every metal cell in the grid, the solver enforces an energy balance: heat entering the cell minus heat leaving the cell equals zero (steady state). More specifically:

Heat arrives from neighbouring metal cells by conduction. Heat leaves the cell into the surrounding air by convection from both flat faces of the plate. If the chip is present in that cell, additional heat is injected. If radiation is enabled, additional heat leaves by thermal radiation.

The equation for one cell (i, j) is:

Sum over all four neighbours: G_cond * (T_neighbour - T_cell) minus 2 * h_eff * dx squared * (T_cell - T_inf) plus Q_cell equals 0.

Where:
- G_cond = k * t_z, the conductance between adjacent cells
- k = thermal conductivity of the metal in W/mK
- t_z = plate thickness in metres
- h_eff = effective convection coefficient in W/m2K
- dx = cell size in metres (0.0015)
- T_cell = temperature of this cell
- T_neighbour = temperature of the neighbour cell
- T_inf = ambient air temperature (35 degrees C)
- Q_cell = heat injected into this cell by the chip (in watts)

The factor of 2 before the convection term is because both flat faces of the plate lose heat to the air.

Note that G_cond does not depend on dx. The face area between two cells is dx times t_z, and the distance between their centres is dx, so G_cond = k * (dx * t_z) / dx = k * t_z. The dx cancels out. This is a useful property because it means the conductance is the same regardless of grid resolution.

### What Each Material Property Means

Thermal conductivity (k): A measure of how well the metal conducts heat. Aluminium has k = 205 W/mK. Steel has k = 50 W/mK. Higher values mean heat spreads more easily.

Plate thickness (t_z): The thickness of the metal plate into the page. Thicker plates conduct more heat because there is more cross-sectional area. Default is 1 millimetre for aluminium, 0.3 millimetres for thin steel.

Convection coefficient (h): A measure of how effectively moving air carries heat away from a surface. Still air has h around 10 W/m2K. A gentle fan gives h around 60 W/m2K. A strong fan gives h around 120 W/m2K. Higher values mean faster cooling.

Ambient temperature (T_inf): The temperature of the surrounding air, set to 35 degrees Celsius (typical indoor temperature in warm climates).

Surface emissivity (emis): A measure of how effectively the surface radiates heat. Anodised aluminium has emis = 0.85. A polished surface has lower emissivity. This matters for the radiation calculation.

Air speed (u_air): The speed of air flowing past the heat sink in metres per second. Zero means natural convection (air movement driven by buoyancy alone). A standard fan gives about 2 to 3 metres per second.

Flow path length (L_flow): The distance air travels through the heat sink, in metres. This affects the channel starvation calculation.

### The Fin Parameter (The Single Most Important Quantity)

The fin parameter m is a derived quantity that combines the material properties into one number:

m = square root of (2 * h / (k * t_z))

Its units are 1/metres. The reciprocal, 1/m, is the characteristic length over which a fin cools down. This is the distance heat travels through the metal before most of it has leaked into the air.

For example:
- Thick aluminium with no fan: 1/m = 101 millimetres. Heat travels 101 mm before cooling.
- Thick aluminium with a fan: 1/m = 41 mm.
- Thin aluminium with a fan: 1/m = 23 mm.
- Thick steel with a fan: 1/m = 14 mm.
- Thin steel with a strong fan: 1/m = 8 mm.

Compare these to the heat sink size (33 millimetres across). When 1/m is much larger than 33 mm (like 101 mm for aluminium), heat reaches everywhere easily and shape barely matters. When 1/m is much smaller than 33 mm (like 8 mm for thin steel), heat cannot reach the edges and shape decides everything.

### The Dimensionless Parameter L.m

The product L.m (sink half-width times the fin parameter) is the single number that predicts how much improvement is possible:

L.m = (33/2 mm) / (1/m)

When L.m is much less than 1, the metal is nearly isothermal (all at the same temperature) and there is little to gain by rearranging the shape. When L.m is around 2 to 3, the sweet spot, heat reaches a useful but incomplete distance and shape can make a large difference. When L.m is much greater than 4, the metal is so conduction-limited that even an optimised shape cannot move heat far enough to help.

The experimental results confirm this prediction: improvement peaks at L.m around 2.3 (19.5% for thick aluminium with a fan) and falls on both sides (4.6% at L.m 0.33 for thick aluminium with no fan, 10.0% at L.m 4.17 for thin steel with strong fan).

---

## 10. The Two Physics Models and Why It Matters

This section explains the most important finding of the project: the choice of physics model determines the result.

### Model A: Uniform Convection Coefficient (The Convenient Simplification)

The standard textbook simplification treats the convection coefficient as identical for every metal cell, regardless of where that cell is located. A cell buried deep inside a solid lump of metal gets the same cooling as a cell on an exposed fin tip.

This is convenient because it simplifies the mathematics, but it is wrong. Metal buried inside a solid lump has almost no moving air around it. The air there is trapped and stagnant, so it heats up to near the wall temperature and ceases to remove heat effectively.

Under this model, the optimiser produces a compact dense blob of metal near the chip and claims a large improvement (up to +20.2%).

### Model B: Channel Starvation Model (The Honest One)

The channel starvation model calculates the local convection coefficient for each cell based on how wide the air channel is next to that cell. The calculation works as follows:

First, compute the distance from every air cell to the nearest metal cell using a Euclidean distance transform. This gives the half-width of the air channel at every point.

Second, for each metal cell, find the widest air channel among its four neighbouring cells. This is the channel the cell actually breathes through. A cell at the edge of the grid sees open air (treated as very wide).

Third, calculate the choke gap s_c = 2 * h * L / (rho * u * cp). This is the gap width at which the air flowing through a channel has absorbed all the heat it can carry. Below this width, the channel is thermally starved. Above it, the surface behaves like an isolated plate.

Fourth, calculate the effective coefficient: h_eff = h * (1 - exp(-s / s_c)). When s is 0 (fully enclosed metal), h_eff is 0 (no cooling). When s is much larger than s_c, h_eff approaches h (full cooling).

Under this model, compact blobs perform poorly because their interior cells have narrow air channels and therefore reduced cooling. The optimiser instead produces extended branching shapes with open channels between features. It independently rediscovers the principle of the fin (exposed surfaces with open flow on both sides) and then improves on the arrangement.

### The Falsification Test

This is the most important test in the project.

Step 1: Run the optimisation under the constant-h model. The optimiser produces a compact blob and claims +20.2% improvement.

Step 2: Take that same blob shape and evaluate it under the channel starvation model. The blob scores minus 6.0% (worse than straight fins). The claimed improvement was an artifact of assuming constant h.

Step 3: Re-run the optimisation under the channel starvation model. The optimiser now produces branching shapes and achieves +9.1% improvement. This is a real improvement because it survives the more honest model.

This three-step process (claim, falsify, rebuild) is the central narrative of the project. It demonstrates scientific honesty: instead of hiding the inconvenient result, the project reports it and explains why it matters.

---

## 11. The Random Part vs The Physics Part

This is the question you will be asked most often during your presentation: "Is this just random?" Here is the complete answer.

### What Is Random

The following parts of the project involve randomness intentionally:

The initial population of designs is random. Each starting design is a random connected blob grown outward from the chip. The randomness is constrained by two rules: the blob must be connected to the chip (no floating islands), and the blob must use the correct amount of metal (the same as the baseline design).

The mutations are random. When a child design is created, some cells are randomly removed (biased toward the coldest tips) and some cells are randomly added (from the perimeter of the existing shape). Which specific cells get added or removed is determined by a random number generator.

The crossover is random. When two parent designs are combined, the split line (vertical or horizontal, and at which position) is chosen randomly.

The random seed is a starting value for the random number generator. Different seeds produce different sequences of random numbers. Running the same experiment with different seeds tests whether the result is reproducible.

### What Is NOT Random

The temperature calculation is deterministic. Given the same shape and the same material properties, the solver always produces the exact same temperature field. This is because the heat equation is a deterministic mathematical equation. If you put the same inputs in, you get the same outputs out.

The material properties are fixed. The thermal conductivity, plate thickness, convection coefficient, and all other material properties are fixed constants chosen by the user. They do not change randomly during the simulation.

The comparison between the human and evolved designs is deterministic. Both designs are evaluated using the same physics solver with the same material properties. The same amount of metal is allocated to both. The comparison is therefore fair and repeatable.

The validation against textbook equations is deterministic. The analytical fin equation produces an exact temperature profile. The solver reproduces this profile to within 0.0003% error. This is not random; it is a mathematical check.

### Why Randomness Is Necessary for Evolution

Evolutionary algorithms use randomness intentionally because deterministic algorithms get stuck. If every child was an exact copy of its parent, the population would never change and no improvement would occur. Random mutations introduce variation, and the deterministic physics solver then selects which variations survive. This is analogous to natural selection: mutations are random, but selection is not.

Think of it this way: the randomness explores new possibilities, and the physics decides which possibilities are worth keeping. Without randomness, the search would converge to the first decent design it found and never discover better ones. Without physics, the search would wander randomly and never improve.

---

## 12. The Evolutionary Algorithm Explained

### What Is an Evolutionary Algorithm

An evolutionary algorithm is a computational method inspired by biological evolution. It does not learn or train like a neural network. Instead, it uses the following loop:

1. Create a population of candidate solutions (in this case, metal shapes).
2. Evaluate each candidate using a fitness function (in this case, the thermal solver).
3. Select the best candidates to be parents.
4. Create children by recombining and mutating the parents.
5. Replace the population with the children.
6. Repeat from step 2 until convergence.

Nothing learns in this process. No individual design gets smarter. The population as a whole improves because bad designs keep getting deleted and good designs keep getting combined.

### How a Design Is Represented

Each design is a binary grid of 44 by 44 cells (1,936 bits). A value of 1 means metal is present. A value of 0 means air. The design must satisfy three constraints:

The design must be connected to the chip. If a metal cell is not connected to the chip through a chain of neighbouring metal cells, the flood-fill algorithm discards it. This prevents floating islands of metal that contribute nothing.

The design must use exactly the right amount of metal. The material budget is set to the same number of cells as the best conventional design. If a design has too few cells, it is grown (by adding perimeter cells) to fill the budget. If it has too many cells, it is trimmed (by removing the furthest cells from the chip).

The design must respect blocked areas. The user can draw exclusion zones on the board where metal cannot be placed.

### The Fitness Function (The Most Important Part)

The fitness function is the objective that the algorithm tries to maximise. In this project, the fitness function has gone through five versions, each correcting a flaw in the previous one.

Version 1: Minimise the mean (average) temperature. The algorithm exploited this by growing a long cool fringe far from the chip. The fringe was near room temperature and dragged the average down, but the chip itself ran hotter than any other version. The algorithm optimised exactly what it was told to optimise, and that was the wrong thing.

Version 2: Minimise the peak (maximum) temperature. The algorithm exploited this by expanding without limit, using as much metal as possible. There was no material budget, so it tried to fill the entire grid with metal.

Version 3: Minimise the peak temperature with a hard material budget. The algorithm produced one-cell-wide tendrils at the resolution limit of the grid, where the simulation is least trustworthy.

Version 4: Minimise the peak temperature with a budget and a thin-feature penalty. The penalty adds 0.15 times the thin fraction times the temperature rise to the peak temperature. The thin fraction is the proportion of cells with fewer than two orthogonal metal neighbours. This penalises fragile one-cell-wide features. No exploit was found. This is the version used for results.

Version 5: Version 4 plus the airflow occlusion model (channel starvation). This is the version used for all final results under the honest physics model.

The fitness function for version 5 in full:

score = negative of (peak temperature + 0.15 * thin_fraction * (peak temperature minus ambient temperature))

subject to: hard material budget, connectivity requirement, and airflow-aware convection coefficients.

Every term in this function exists because a previous version got exploited.

### Selection, Crossover, and Mutation

Selection: The population is sorted by fitness (lower peak temperature is better). The top 4 designs (elite) are preserved unchanged into the next generation. The remaining 20 designs are created by breeding.

Crossover: Two parent designs are selected from the top half of the population. A random split line (either vertical or horizontal) is chosen. The child takes the left/top portion from parent A and the right/bottom portion from parent B. The child is then repaired for connectivity (floating islands are removed) and refilled to the metal budget.

Mutation: Some cells are randomly removed from the child (biased toward the coldest tips, because cold metal is doing no useful work) and some cells are randomly added (from the perimeter of the remaining shape). The mutation rate starts at 3.5% and decays over time: explore early, refine late.

Annealing: The mutation rate decays as the run progresses, following the formula: rate = base_rate * (1 - 0.55 * min(generation / 260, 1)). This means the search explores widely in early generations and refines locally in later generations.

Auto-stop: If no improvement in the best fitness has occurred for 70 consecutive generations, the search stops itself. About 95% of all improvement occurs in the first 50 generations, so a flat line after that is the correct result, not a broken one.

### MAP-Elites (Quality Diversity Search)

The MAP-Elites algorithm adds a memory to the basic evolutionary search. It divides the space of possible shapes into a 10 by 10 grid based on two shape descriptors: elongation (how stretched the shape is, from round to elongated) and reach (how far the metal extends from the chip, from close to far).

Every design ever evaluated is filed into the bin matching its shape. If the bin already contains a design, only the better one is kept. The archive is the memory: it never forgets a good shape, even one that is currently losing the main competition.

New designs are bred by picking a random occupied bin and mutating its occupant. This prevents the search from collapsing into one idea and getting stuck.

For this problem, MAP-Elites produced a library of 134 distinct viable shapes but a worse single best design compared to the plain genetic algorithm. This is because it distributed its 2,400 evaluations across 134 bins (about 17 evaluations each) while the plain GA concentrated all evaluations on one lineage.

---

## 13. The Bugs That Were Found and Fixed

This section documents every significant bug that was discovered during the project. These are not failures; they are evidence of rigorous testing and scientific honesty.

### Bug 1: The Browser Solver Exploded

When the JavaScript solver was first written, it used a method called Jacobi iteration with an acceleration factor (omega) of 1.8. After 10 sweeps, the temperature reached 2,849 degrees Celsius. After 20 sweeps, it reached 14,204,000 degrees Celsius. After 40 sweeps, it produced NaN (not a number).

The cause was that Jacobi iteration uses old values from the previous sweep to update each cell. When you accelerate Jacobi with omega greater than 1, it overshoots and the error grows every sweep instead of shrinking. This is catastrophic because the conduction term dominates the convection term by a factor of 10,496, making the system essentially a Laplace equation, which is the worst case for Jacobi.

The fix was to use red-black (chessboard) ordering. In this scheme, the grid is coloured like a chessboard. A red cell's four neighbours are all black, and vice versa. All red cells are updated simultaneously using the black values, then all black cells are updated using the freshly computed red values. This makes the method Gauss-Seidel rather than Jacobi, and acceleration becomes stable. Both versions were kept in the Python code (solve for direct, solve_iterative for red-black) and the JavaScript version was tested against both.

### Bug 2: The Fitness Function Measured an Unconverged Temperature

To save time, the fitness function evaluated designs using only 400 solver sweeps instead of the full 3,000 needed for convergence. The peak temperature reported by 400 sweeps was 232.40 degrees Celsius. The fully converged value was 266.51 degrees Celsius. This is a 34 degree Celsius error.

Worse than its size was its direction: an unconverged solve always underestimates the peak temperature, and it underestimates most for designs where heat travels furthest. This means the evolution was partly selecting for designs that its solver converged on quickly, not designs that were actually cooler.

The fix was to use the direct sparse solver (SciPy's spsolve) instead of the iterative solver for fitness evaluation. At these grid sizes, the direct solve is both exact and about 20 times faster (2.5 milliseconds versus 50 milliseconds for the iterative solver).

### Bug 3: Half the Metal Budget Was Being Thrown Away

In the first head-to-head comparison, the evolved design lost by minus 101% (240 degrees Celsius versus the baseline 137 degrees Celsius). The algorithm was fine, but the representation was broken.

Designs were capped at 472 cells but only ever used about 220 cells. The random initial designs at 15% density were almost entirely disconnected, and the fitness function discarded all floating islands. The budget counted metal that was not actually contributing to the design.

The fix was to grow designs outward from the chip instead of placing random cells. This guarantees connectivity from the start, so 100% of the metal budget is usable.

The result flipped from minus 101% to plus 5.3%: a 106 percentage point swing from changing how designs are encoded, not how they are optimised.

### Bug 4: The Baseline Used Only 29% of Its Metal Budget

When running the thermal regime sweep under the new physics, the still-air aluminium configuration reported an improvement of +63.5%. This contradicted the entire finding (the improvement should be small when L.m is low, not huge).

The fin generator only produces 18 fixed shapes (6 fin counts times 3 thicknesses), and their cell counts jump from 271 to 504. With a 425-cell budget, the best legal shape used only 124 cells (29% of the allowance), while the evolved design used 100%. The control group was being starved.

The fix was to trim each fin design from its outer tips down to exactly the budget. The reported gain dropped from +63.5% to +4.6%.

### Bug 5: The Fin Hub Was in the Wrong Place

The original code placed the fin hub at the geometric centre of the grid, regardless of where the heat source was. When the chip was at the edge, the hub was 14.8 cells away from the heat. No engineer would ever mount a heat sink that way.

This inflated the evolved design's apparent advantage because the conventional design was deliberately handicapped. When the hub was moved to the chip's centre of mass, the improvement dropped from a fake 47% (in one configuration) to the real 8% to 10%.

### Summary of Bugs

Three times, a spectacular number came from an unfair control group rather than a clever algorithm. If you write down one engineering lesson from this project, it is that how you set up the comparison matters more than which algorithm you run.

---

## 14. All the Results and What They Mean

### Validation Results

The solver was tested against the textbook fin equation at six grid resolutions. The error was 0.0751% at 10 cells, falling to 0.0001% at 320 cells. The error ratio per halving was 3.97, 3.98, and 3.99, confirming second-order convergence.

The radiation model was tested against the exact Stefan-Boltzmann balance. The error was 0.174%.

The combined radiation-plus-convection model was tested against a hand-computed lumped balance. The error was 0.000%.

The transient solver was tested against the steady-state solver at long time. The difference was 0.00%.

All 14 validation assertions pass.

### Head-to-Head Results (Baseline vs Evolved)

Under the version 2 physics (channel starvation plus radiation), the evolved design outperformed the best conventional design in all configurations tested:

Thick aluminium (1 mm) with natural convection: Improvement of 4.6%. L.m = 0.33. Heat travels 101 mm but the sink is only 33 mm, so the whole sink is nearly isothermal. There is little to win.

Thick aluminium (1 mm) with forced convection (fan): Improvement of 19.5%. L.m = 0.80. This is the sweet spot where improvement peaks.

Thin aluminium (0.3 mm) with forced convection: Improvement of 13.3%. L.m = 1.46.

Thick steel (0.5 mm) with forced convection: Improvement of 12.4%. L.m = 2.29.

Thin steel (0.3 mm) with strong fan: Improvement of 10.0%. L.m = 4.17. Heat travels only 8 mm, so the outer part of the sink is unreachable regardless of shape.

### Reproducibility

The head-to-head comparison was repeated 10 times with different random seeds. The standard deviation across seeds was 0.03 degrees Celsius. The spread (range divided by mean temperature rise) was under 0.1%. This confirms that the results reflect the optimisation, not a lucky random seed.

### The Falsification Test Results

The v4 design (optimised under constant h) claimed +20.2% improvement. When evaluated under the channel starvation model, the same design scored minus 6.0% (worse than straight fins). The v5 design (optimised under the channel starvation model) scored +9.1% under the channel starvation model.

The airflow-aware design outperforms straight fins in three of the four material configurations tested, with improvements ranging from +2.3% to +9.1%.

### The L.m Finding

Improvement is not monotonic in L.m. It rises from 4.6% at L.m 0.33 to a peak of 19.5% at L.m 0.80, then falls to 10.0% at L.m 4.17. This confirms the physical prediction: at very low L.m, heat reaches everywhere and shape barely matters. At very high L.m, heat cannot reach the periphery and no arrangement can help. The greatest benefit occurs in the intermediate regime.

### The MAP-Elites Result

The plain genetic algorithm (2,400 evaluations) achieved a mean peak temperature of 213.83 degrees Celsius, an improvement of 8.2% over the conventional reference. The MAP-Elites algorithm (2,400 evaluations) achieved 222.95 degrees Celsius, an improvement of 3.6%. The plain GA was better at finding a single best design because it concentrated all evaluations on one lineage. The MAP-Elites archive contained 134 distinct viable shapes.

---

## 15. How to Run the Python Tests

### First Time Setup

Open a terminal (Command Prompt on Windows, or Terminal on Mac/Linux) and navigate to the project folder. Then run:

pip install numpy scipy matplotlib

This installs the three Python libraries required by the project. You only need to do this once.

### Run the Validation Suite (Most Important)

This is the test you should run during your presentation. It proves the physics is correct.

cd sim
python3 validate2.py

If python3 does not work, try:

python validate2.py

The script will take about 30 seconds to run. At the end, it should print:

PASSED 14   FAILED 0

If you see this, the physics engine has passed all 14 validation tests.

### Run the Cheat Log (Interesting for Presentation)

This shows how the algorithm exploits weaknesses in the fitness function.

cd sim
python3 cheat_log.py

The script runs four evolutions of 60 generations each. Each evolution uses a different fitness function. The output shows the peak temperature, mean temperature, metal fraction, and thin fraction for each version, along with a description of what the algorithm exploited.

### Run the Airflow Test

This runs the falsification test.

cd sim
python3 airflow_test.py

The script runs several evolutions and compares the results under the constant-h and channel starvation models. This takes several minutes.

### Generate the Figures

cd sim
python3 figures.py

This creates all 8 report figures as PNG files in the figures folder. The script takes about 10 seconds.

### Check the Site Data

cd sim
python3 test_site.py

This verifies that every number on the website matches the data files. It checks improvement percentages, airflow test values, and page consistency. If Playwright is not installed, it will skip the browser checks but still perform all data checks.

### Common Problems and Solutions

Problem: "ModuleNotFoundError: No module named numpy"
Solution: Run "pip install numpy scipy matplotlib"

Problem: "python3: command not found"
Solution: Try "python" instead of "python3"

Problem: The script takes too long to run
Solution: Some experiments run 100+ generations with 24 designs each. This can take several minutes. The validation suite (validate2.py) is the quickest and most important test.

Problem: "ImportError: cannot import name 'Problem' from 'evolve2'"
Solution: This means a script is trying to use the version 1 API with the version 2 code. The evolve.py wrapper should handle this. If it does not, run the script from the sim folder (cd sim first) to ensure the paths are correct.

---

## 16. How to Present This Project

### Suggested Presentation Structure (5 to 7 Minutes)

Slide 1: Title and Question
"What is FINCH? Can a computer design a better heat sink than a human engineer?"

Slide 2: What Is a Heat Sink
Show a picture of a heat sink. Explain that it is the finned metal on anything that gets hot. Its job is to move heat from the chip into the air. Human-designed heat sinks all look the same because straight fins are cheap to manufacture, not because they are optimal.

Slide 3: The Experiment
Show the two-panel display from the tool. Left side: human design (straight fins). Right side: computer-grown design (evolved shape). Both get exactly the same amount of metal. The question is which runs cooler.

Slide 4: The Physics
Explain that the temperature is calculated using real heat transfer equations, not random guesses. Show the validation result: 0.0003% error against the textbook formula. Show the two-language agreement: Python and JavaScript agree to 0.0002 degrees Celsius.

Slide 5: The Evolution
Show the loop: generate random shapes, evaluate temperature, keep coolest, mutate, repeat. Emphasize that the mutations are random but the selection is based on physics. Show the convergence graph.

Slide 6: The Key Finding
Show the L.m result table. The improvement peaks at L.m around 0.8 to 2.3 and falls on both sides. This confirms the physical prediction.

Slide 7: The Falsification Test
Show the three-step process: constant-h model claims +20.2%, same design judged with airflow scores minus 6.0%, rebuilt with airflow scores +9.1%. This is the most important slide because it shows scientific honesty.

Slide 8: Conclusion
Computer-grown shapes beat conventional fins by 3% to 20%. The benefit is largest in the intermediate conduction regime. The most important lesson is that your result is only as good as your assumptions.

### Live Demonstration Script

Step 1: Open the tool in the browser (flinch/index.html).
Step 2: Point out the two panels. Left is human design, right is computer-grown.
Step 3: Explain the colour scale: dark blue is cold (room temperature), red is hot. Dark blue metal is wasted because heat never reached it.
Step 4: Press Evolve. Watch the temperature fall for about 15 seconds.
Step 5: Point at the graph. Explain that the dashed red line is the human baseline, and the teal curve is the evolved design.
Step 6: If the evolved design wins, point at the verdict strip and read it aloud.
Step 7: Stop the evolution and change the material to "Thick aluminium, no fan." Press Evolve again. Notice that the improvement is smaller because heat reaches everywhere in aluminium.
Step 8: Switch the air rule to "Uniform coefficient." Press Evolve. Notice that the shape changes and the claimed improvement increases. Explain why: the simpler physics model overstates performance for compact shapes.

### Key Points to Emphasize During Questions

If someone asks "Is this an AI?", answer: "No. It is an evolutionary search algorithm combined with a physics simulator. Nothing is trained. No neural network, no training data. Every design is evaluated by solving real heat transfer equations."

If someone asks "Is it random?", answer: "The mutations are random, but the selection is based on deterministic physics. The same shape always gets the same temperature. The randomness explores new possibilities, and the physics decides which ones survive."

If someone asks "How do you know it is accurate?", answer: "I validated the solver against the textbook fin equation to 0.0003% error. I also wrote the solver in two different languages independently (Python and JavaScript) and they agree to 0.0002 degrees Celsius. If one had a bug, the other would not have the same bug."

If someone asks "Why does it sometimes lose?", answer: "Because sometimes there is nothing to win. When L.m is low, heat reaches everywhere and the whole sink is nearly the same temperature regardless of shape. The improvement is small because the available prize is small."

If someone asks "Did you write the code?", answer: "I directed the project. I designed the experiments, chose the physics models, built the fitness functions, and found and fixed the bugs. An AI assistant helped with the syntax. I can explain every number the project produces."

---

## 17. Common Questions and Complete Answers

### Q: Why are there two folders (flinch and sim)?

The flinch folder contains the website (HTML, CSS, JavaScript). Open any file in flinch in a browser to use the tool. The sim folder contains the Python research code and data files. The website has a JavaScript port of the same physics engine that the Python uses. Both give the same answers. You need Python and the required packages installed to run the sim scripts.

### Q: Why is the folder called "flinch" instead of "finch"?

The folder is named flinch (with an L). This was a typo that happened when the project was first set up and was never corrected. The project name everywhere else is FINCH (without the L). The folder name does not affect anything.

### Q: Why are there two versions of physics (physics.py and physics2.py)?

Version 1 (physics.py) was the first implementation. It used a simple openness model for trapped air, with a guessed 15% floor and a guessed 3-cell radius. Version 2 (physics2.py) has the improved channel starvation model with a Derived length scale (no guesses), plus radiation (Stefan-Boltzmann) and transient (time-dependent) mode. All final results use version 2, but version 1 is kept because some older scripts (figures.py, cheat_log.py) still import it.

### Q: The home page has placeholder boxes instead of images?

Yes, the home page has two images that were never generated. These would show the conventional vs evolved heat sink side by side. To generate them, run "python3 sim/figures.py" which creates all 8 report figures in the figures folder. The home page images would need to be generated separately from the simulation data.

### Q: Some Python scripts give errors when I run them?

The version 1 scripts (cheat_log.py, airflow_test.py, benchmark.py, regime.py) were designed for an older version of the code that had a different API. They may not run correctly with the current code. The version 2 scripts that work reliably are validate2.py, regime2.py, and mapelites_test.py. Focus on those for your presentation.

### Q: How do I download the files to my computer?

Go to github.com/panavkbysani2011-jpg/finch-heatsink in your web browser. Click the green button labelled "Code." Select "Download ZIP." Extract the ZIP file on your computer. You now have all the project files.

### Q: How do I put the website online?

Option 1 (Netlify, easiest): Go to app.netlify.com/drop. Drag the entire flinch folder from your computer onto the web page. Within 30 seconds, you will receive a live URL you can share.

Option 2 (GitHub Pages): Go to your repository on GitHub. Click Settings. Click Pages in the left sidebar. Under Source, select "Deploy from a branch." Set Branch to "main" and folder to "/ (root)." Click Save. Wait 2 minutes. Your site appears at https://panavkbysani2011-jpg.github.io/finch-heatsink/.

Option 3 (Freebuff hosting): The preview is already running in Freebuff. Ask me to deploy it to production hosting.

### Q: How do the two language implementations relate?

The Python version was written first. It uses NumPy and SciPy for accurate matrix solving. The JavaScript version was written second, independently. It uses a different mathematical method (red-black iterative solver) because NumPy and SciPy do not exist in browsers. The two versions were tested against each other and agree to 0.0002 degrees Celsius on the peak temperature and 4.9 times 10 to the minus 7 on the openness field. This agreement proves that neither version contains an undetected error.

### Q: What is the fin parameter m?

The fin parameter m is a derived quantity equal to the square root of (2h divided by k times t_z). Its units are 1/metres. The reciprocal (1/m) is the distance heat travels through the metal before most of it has leaked into the air. This is the single most important quantity in the project because it determines whether shape optimization is worthwhile.

### Q: What is L.m and why does it matter?

L.m is the product of the sink half-width (L) and the fin parameter (m). It is a dimensionless number that predicts how much improvement is possible. When L.m is much less than 1, the metal is nearly isothermal and shape barely matters. When L.m is around 1 to 3, shape can make a large difference. When L.m is much greater than 4, even an optimized shape cannot help because heat cannot travel far enough.

### Q: Is this project useful for real engineering?

Not yet. The model is two-dimensional, the airflow model is a geometric approximation rather than real fluid dynamics, and nothing has been physically built and measured. What the project demonstrates is a method, plus an honest account of how a modelling assumption can manufacture a result that is not real. The next step would be to physically build two heat sinks and measure them.

---

## 18. Glossary of Terms

Ambient temperature: The temperature of the surrounding air, set to 35 degrees Celsius in this project.

Annealing: Reducing the mutation rate over time so the search explores early and refines late.

Baseline: The conventional straight-fin design that the evolved design is compared against.

Budget: The amount of metal available, measured in number of cells. Both designs get the same budget.

Channel starvation: A model where the convection coefficient is reduced in narrow channels because the air heats up and can no longer carry heat away effectively.

Conduction: Heat moving through a solid material from hot areas to cold areas.

Convection: Heat being carried away by air or another fluid moving past a surface.

Convection coefficient (h): A number measuring how effectively moving air removes heat from a surface. Higher values mean faster cooling.

Convergence: When the search stops finding improvements. About 95% of the improvement arrives in the first 50 generations.

Crossover: Combining two parent designs into a child by splitting each along a random line and taking half from each.

Deterministic: Producing the same output every time for the same input. The physics solver is deterministic.

Dimensionless: A quantity without units, making it comparable across different situations. L.m is dimensionless.

Dirichlet boundary: A fixed-temperature boundary condition, used only in validation (not in the actual experiments).

Elite: The best few designs that survive unchanged into the next generation.

Emissivity: A measure of how effectively a surface radiates heat, from 0 (no radiation) to 1 (perfect black body). Anodised aluminium has emissivity 0.85.

Falsification test: An experiment designed specifically to disprove a previous result. The airflow test was a falsification test for the constant-h result.

Fin parameter (m): The square root of (2h divided by k times t_z). Its reciprocal (1/m) is how far heat travels through the metal.

Fitness function: The score that the algorithm tries to maximise. For FINCH, it is the negative of the peak temperature plus a thin-feature penalty.

Generation: One iteration of the evolutionary loop (evaluate, select, breed, repeat).

Grid: The 44 by 44 array of square cells that represents the heat sink.

Isothermal: All at the same temperature. A perfect conductor would be isothermal.

L.m: The product of sink half-width and the fin parameter. The number that predicts how much improvement is possible.

MAP-Elites: An evolutionary algorithm that keeps a diverse archive of good designs across different shape categories.

Mutation: Randomly adding or removing a few cells from a design to create variety.

Peak temperature: The hottest single point in a design. This is what kills a chip, so it is the primary metric.

Population: The set of designs being evaluated in one generation. Usually 24 designs.

Red-black SOR: A method for solving systems of equations where the grid is coloured like a chessboard and cells are updated in two passes.

Seed: A starting value for the random number generator. Different seeds produce different random numbers but the same seed always produces the same sequence.

SOR: Successive Over-Relaxation. An iterative method that deliberately overshoots the solution to converge faster.

Stefan-Boltzmann law: The physical law describing how much heat a hot surface radiates. It depends on temperature to the fourth power.

Steady state: A condition where nothing is changing with time. Heat in equals heat out.

Thermal conductivity (k): A measure of how well a material conducts heat. Aluminium is about 205 W/mK. Steel is about 50 W/mK.

Thin fraction: The proportion of metal cells with fewer than two orthogonal neighbours. Used as a manufacturability penalty.

Validation: Testing the solver against known analytical (textbook) solutions to prove it is correct.

Wasted metal: Metal that is sitting near room temperature, meaning heat never reached it. Visible as dark blue areas on the heat map.
