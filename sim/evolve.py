"""
FINCH search, version 1 — compatibility wrapper.

Imports everything from evolve2 and re-exports it with the v1 names
so that figures.py and other scripts written for the original evolve.py
still work without changes.
"""

from evolve2 import (
    Problem as Problem,
    largest_connected as largest_connected,
    random_design as random_design,
    mutate as mutate,
    crossover as crossover,
    fitness2 as fitness,
    best_baseline2 as best_baseline,
)

# The Problem class from v1 had these attribute names
class Problem(Problem):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.h_radius = 3
        self.h_min_frac = 0.15
