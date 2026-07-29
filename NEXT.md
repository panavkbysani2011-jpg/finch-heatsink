# What next

The building is finished. Everything from here is you, not more code.

---

## The honest status

**Done and tested:**
- Three page site: story, tool, findings
- Physics validated 14 ways, including against textbook equations
- Two independent implementations that agree exactly
- Five of eight limitations fixed
- Two headline results that I caught being wrong and corrected
- One negative result reported instead of hidden

**Not done, and only you can do it:**
- Understanding it well enough to defend it
- The process journal
- The report

That second list is what is actually graded. The product is not marked at all.

---

## Stop building. Here is why.

You have asked for improvements eleven times. Each time the app got better and
you understood it slightly less, because I kept adding before you had absorbed
the last thing. The tool is now more capable than your explanation of it, and
that gap is the real risk to your grade, not a missing feature.

An examiner will not ask "did you implement radiation". They will ask
"why did you do this, and what did you learn". Right now the app can answer
the first question better than you can.

---

## Do these three things, in order

### 1. Twenty minutes with the tool, today

Open `finch/index.html`. Run these five, and write one sentence on each in
your own words:

| # | Do this | Watch for |
|---|---|---|
| 1 | Chip at **centre**, press Evolve | A modest win, about 10% |
| 2 | Chip at **the edge**, press Evolve | Still modest, about 8%. The fins move with the chip now. |
| 3 | Air rule to **Ignore trapped air**, Evolve | It builds a dense blob and claims a bigger win |
| 4 | Air rule back to **Trapped air counts**, Evolve | The blob suffocates, arms grow instead |
| 5 | Switch to **Archive of shapes**, run 30 seconds | The map fills with different kinds of shape |

Before each run, glance at the setup bar at the top so you know what state you
are in. Last time steps 3 and 4 gave you the same number because the chip had
quietly reverted to centre.

If you can explain why each of those five happened, you own this project.

### 2. Tell your supervisor the story, out loud

Not the technical detail. This:

> I tested whether a computer searching by trial and error could design a
> better heat sink than a human. It could, by about 8%. Then I realised my
> result depended on a physics assumption I knew was false, so I built a
> better model specifically to attack my own work. My result collapsed to
> minus 6.6%. I rebuilt it honestly and got a smaller, real 7.7%. Later I
> found a second error: I had been placing the human design's fins in the
> wrong spot, which had inflated one result from 8% to a fake 47%. I fixed
> that and re-measured everything.

Then show them the tool. Two minutes.

### 3. Start the process journal properly

You need dated entries with evidence. You already have the evidence, it is
sitting in `sim/*.csv` and `figures/`. What is missing is you writing down
what you were thinking at each point.

Backdating is obvious and dishonest. Start today, write what you remember
honestly as a reconstruction, and label it as one.

---

## What is actually gradeable here

MYP marks three things, eight points each. Your evidence for each:

**A, Planning.** Your goal and success criteria. You have measurable ones
already: solver error under 5%, beat the conventional design, results stable
across random seeds.

**B, Applying skills.** This is where you are strongest and you may not
realise it. The evidence is the failures:

- The solver exploding to 10^14 degrees, and why over relaxation broke it
- The scoring function measuring an unconverged temperature, biased low
- Half the metal budget being thrown away by disconnected designs
- Four separate times the search exploited a badly written score
- Two headline results that turned out to be artifacts
- Three failed attempts at the archive descriptors before measuring instead
  of guessing
- Two validation tests that were themselves wrong

Every one of those is dated, documented, and explainable. That is a stronger
Criterion B file than almost any Grade 10 project will have.

**C, Reflecting.** The honest arc: claim, self imposed falsification, rebuild,
second error found, corrected again. Plus a negative result you chose to
report rather than tune away.

---

## The one thing worth building later

If you have time after the report, and only then:

**Build one.** Cut or 3D print two heat sinks, one straight finned and one
grown. Stick a resistor and a thermocouple on each. Measure.

An afternoon of work. It would turn "a hypothesis about reality" into a
measurement, and it is the only remaining limitation that matters.

---

## Where everything lives

```
finch/home.html       the story, send this link to anyone
finch/index.html      the tool, use it in your presentation
finch/findings.html   every number and every bug, your appendix
sim/                  the Python, 12 scripts, all rerunnable
sim/*.csv             raw data, your evidence
figures/              48 charts and screenshots
archive/              the eight long documents, kept for reference
```

To put it online free, drag the `finch` folder onto
[app.netlify.com/drop](https://app.netlify.com/drop).

If you need to look something up, `archive/V2_CHANGES.md` has every equation
and `archive/EXPLAINED.md` has the full walkthrough. You do not need to read
either of them cover to cover. Use them the way you would use a manual.

---

## If you take one thing from this

The best part of your project is not the algorithm. It is that you kept saying
"this does not look right" and were correct every single time:

- You said the app was incomprehensible. It was.
- You said too much was fixed in advance. It was, and testing that found the
  chip position effect.
- You said the edge layout looked wrong. It was wrong, and it exposed a bug
  that had inflated a headline result by five times.

That instinct is the thing worth writing about.

---

## Correction log, after the baseline fix

Fixing the fin hub (placing it on the chip rather than the centre of the board)
changed every experiment that used the conventional design as a control. All of
them were rerun. The figures and CSV files now agree with each other.

**The L.m story changed shape, and became more interesting.**

| L.m | Old gain | New gain | Change |
|---|---|---|---|
| 0.33 | 1.7% | 1.8% | +0.1 |
| 0.52 | 3.9% | 4.2% | +0.3 |
| 0.80 | 5.2% | 9.2% | +3.9 |
| 1.46 | 12.7% | 21.1% | +8.4 |
| **2.29** | 20.2% | **30.6%** | **+10.4** |
| 4.17 | 24.5% | 20.3% | -4.2 |
| 5.11 | 23.0% | 19.3% | -3.7 |

It used to rise all the way to the right. It now **peaks at L.m about 2.3 and
falls after**, which is physically better sense: at the extreme end the metal is
so conduction limited that even a search cannot move heat far enough to help.
Verified across three random seeds with a spread of only 0.1 percentage points,
so the peak is real and not noise.

**The falsification story got stronger, not weaker.**

| Stage | Old | New |
|---|---|---|
| Claimed with the convenient assumption | +24.5% | +20.2% |
| Same design judged honestly | -6.6% | -6.0% |
| Rebuilt with the honest rule | +7.7% | **+9.1%** |

The airflow aware design is now positive in three of four cases, up from one of
four. The arc you tell in your report is unchanged: claim, self imposed
falsification, rebuild. Only the numbers moved.

**What this means for you:** if you had already written any of these figures
down, use the new ones. Everything on the site and in `sim/*.csv` is now
consistent. Nothing else in the story changed.

---

## The seven limitations: exactly where each one stands

You asked whether these were actually done. Checked against the code, not memory.

| # | Limitation | Status | Evidence |
|---|---|---|---|
| 1 | Two dimensional | **Not fixed** | No 3D solver exists. Out of scope. |
| 2 | Trapped air is geometric, not CFD | **Partly** | Box blur replaced by a derived channel model. Still not CFD: no flow direction, no boundary layers. |
| 3 | Its constants were guesses | **Fixed** | The 15% floor and 3 cell radius are deleted. One length scale remains and it is derived: `s_c = 2hL / (rho u cp)` |
| 4 | No radiation | **Fixed** | Full Stefan Boltzmann, validated to 0.000% against a hand calculation |
| 5 | Steady state only | **Fixed** | `solve_transient` matches the steady answer to 0.00% |
| 6 | Manufacturability is a soft penalty | **Not fixed** | Deliberate. A hard constraint would over restrict the search. |
| 7 | Grid 1.5 mm, fine features not honest | **Tested, not fixed** | 44 / 64 / 88 compared. The two finest agree to 0.90%, but the absolute number does move. |

**Four fixed, one partly, one tested, two open.** The two left open are the two
that need a workshop or a different project, not more code.

### One thing I had wrong

The site said radiation and transients were fixed in one section and still
broken in another. That contradiction is gone.

More seriously: **the Python experiments were still running version one
physics** while the browser ran version two. The published tables came from
the old model. All of them have been rerun.

### And a third unfair baseline

Rerunning under the new physics gave **+63.5%** on still air aluminium, which
contradicted the whole finding. Two previous headlines had already turned out
to be artifacts, so I checked instead of celebrating.

The fin generator only makes eighteen fixed shapes, and their cell counts jump
from 271 to 504. With a 425 cell budget the best legal one used **124 cells,
29% of the allowance**, while the search used 100%. The control group was being
starved.

| | Before | After |
|---|---|---|
| Metal the baseline used | 29% | **100%** |
| Reported gain | +63.5% | **+4.6%** |

Fixed by trimming each fin design down to exactly the budget.

**Three times now** a spectacular number has come from an unfair control group
rather than a clever algorithm. If you write down one engineering lesson from
this project, make it that one.

### The current honest numbers, version two physics

| Material | Heat travels | Search wins by |
|---|---|---|
| Thick aluminium, no fan | 101 mm | 4.6% |
| Thick aluminium, fan | 41 mm | **19.5%** |
| Thin aluminium, fan | 23 mm | 13.3% |
| Thick steel, fan | 14 mm | 12.4% |
| Thin steel, strong fan | 8 mm | 10.0% |

Between 3% and 20%. No miracle, and nothing that needs an asterisk.

### Regression test

`python3 sim/test_site.py` now checks that every number on the site traces back
to a CSV, that the page does not contradict itself, and that all three pages
work at three widths. It lives in the repo rather than a temporary folder, so
you can rerun it any time.
