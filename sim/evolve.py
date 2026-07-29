"""
FINCH search, version 1 — compatibility wrapper.

Provides the original v1 API (Problem, evolve, evaluate, largest_connected)
by wrapping evolve2.py's implementation. This lets benchmark.py, cheat_log.py,
airflow_test.py, and regime.py run without changes.
"""

import numpy as np
import sys, os
sys.path.insert(0, os.path.dirname(__file__))

from physics import Material, solve
from evolve2 import (
    Problem2,
    evolve_plain,
    largest_connected as _lc,
    fitness2,
    random_design as _rd,
    mutate as _mutate,
    crossover as _crossover,
    best_baseline2,
)


class Problem:
    """v1 Problem class — wraps Problem2 with v1 defaults and extra fields."""

    def __init__(self, ny=44, nx=44, dx=0.0015, mat=None, budget=0.22,
                 Q_total=5.0, min_width=2, width_penalty=0.15):
        self.ny = ny
        self.nx = nx
        self.dx = dx
        self.budget = budget
        self.Q_total = Q_total
        self.min_width = min_width
        self.width_penalty = width_penalty

        if mat is None:
            mat = Material()
        self.mat = mat

        # Source: one chip in the centre by default
        cy, cx = ny // 2, nx // 2
        r = max(2, ny // 14)
        self.source = np.zeros((ny, nx), dtype=bool)
        self.source[cy-r:cy+r+1, cx-r:cx+r+1] = True

        # Heat injection
        self.Q = np.zeros((ny, nx))
        self.Q[self.source] = Q_total / self.source.sum()

        # Budget cap, adjusted after baseline is computed
        self.max_cells = int(budget * ny * nx)

        # Extra fields some experiments expect
        self.h_radius = 3
        self.h_min_frac = 0.15

    def set_source(self, rects):
        """Set heat source from a list of (i0, i1, j0, j1) rectangles."""
        self.source[:] = False
        for (i0, i1, j0, j1) in rects:
            self.source[i0:i1, j0:j1] = True
        self.Q[:] = 0.0
        self.Q[self.source] = self.Q_total / self.source.sum()

    def __repr__(self):
        return (f"Problem({self.ny}x{self.nx}, dx={self.dx*1000:.2f}mm, "
                f"budget={self.budget:.0%}, Q={self.Q_total:.1f}W, "
                f"mat=1/m={1000/self.mat.m:.1f}mm)")


def largest_connected(mask, seed):
    """Largest connected component touching seed."""
    return _lc(mask, seed)


def evaluate(mask, prob):
    """Score a design and return a dict with peak, mean, cells, mask, T.

    Uses the v1 physics (physics.py, constant h with openness model).
    """
    from physics import h_field

    m = _lc(mask | prob.source, prob.source)
    n = m.sum()

    if n == 0:
        return {'peak': 1e9, 'mean': 1e9, 'cells': 0,
                'mask': m, 'T': None}

    # Compute h field for airflow model
    hm = h_field(m, prob.mat, radius=prob.h_radius,
                 h_min_frac=prob.h_min_frac)

    T = solve(m, prob.mat, prob.dx, Q=prob.Q, h_map=hm)
    peak = float(np.nanmax(T)) if T is not None else 1e9
    mean = float(np.nanmean(T)) if T is not None else 1e9

    return {
        'peak': peak,
        'mean': mean,
        'cells': n,
        'mask': m,
        'T': T,
    }


def evolve(prob, generations=120, pop_size=24, elite=4, seed=0,
           fitness_version=4, mutation_rate=0.035, log_every=None,
           verbose=False):
    """v1 evolve wrapper — delegates to evolve2's evolve_plain.

    Returns (best_mask, history) where history is a list of
    {'gen': g, 'best': best_fitness, 'mean': mean_fitness}.
    """
    import random
    random.seed(seed)
    np.random.seed(seed)

    # Convert v1 fitness version to v2 parameters
    # v4 = the "manufacturability penalty" version = channel=False in v2
    # v5 = airflow-aware = channel=True in v2
    use_channel = (fitness_version >= 5)

    # Use evolve2's evolve_plain with v2 physics
    # fitness_version controls channel model
    m, score, hist = evolve_plain(
        prob, generations=generations, pop=pop_size, elite=elite,
        seed=seed, rate=mutation_rate,
        channel=use_channel, radiation=True,
    )

    # Convert history format to v1
    v1_hist = []
    for g, (best_f, mean_f) in enumerate(hist):
        v1_hist.append({'gen': g, 'best': best_f, 'mean': mean_f})

    return m, v1_hist
