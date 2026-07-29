"""
FINCH search, version 2
=======================

Adds MAP-Elites on top of the plain genetic algorithm.

WHY
---
The user asked for "a thing like NASA's, where it did millions of trials
randomly but kept the best ones saved, so it became smarter".

That is almost exactly MAP-Elites (Mouret and Clune, 2015, "Illuminating
search spaces by mapping elites"). It is not a neural network and nothing is
trained, but it does accumulate knowledge:

  1. Choose two descriptive axes. Here: how COMPACT the design is, and how
     SPREAD OUT it is from the chip.
  2. Divide that 2D space into a grid of bins.
  3. Every design ever evaluated is filed into the bin matching its shape.
  4. A bin only keeps the single best design ever seen for that shape.
  5. New designs are bred by picking a random bin and mutating its occupant.

The archive is the memory. It never forgets a good shape, even a weird one
that is currently losing, so the search cannot collapse onto one idea and get
stuck. In the original paper this both produces a diverse library of designs
AND tends to find a better single best than a plain GA, because unusual
shapes act as stepping stones.

The archive is also directly presentable: it is a picture of every kind of
heat sink that works, not just the winner.
"""

import numpy as np
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from physics2 import Material2, solve2, h_convect


# ----------------------------------------------------------------------
class Problem2:
    def __init__(self, ny=44, nx=44, dx=0.0015, mat=None,
                 source_rect=None, budget=0.22, Q_total=5.0,
                 min_width=2, width_penalty=0.15):
        self.ny, self.nx, self.dx = ny, nx, dx
        self.mat = mat or Material2()
        self.budget = budget
        self.Q_total = Q_total
        self.min_width = min_width
        self.width_penalty = width_penalty

        if source_rect is None:
            cy, cx = ny // 2, nx // 2
            r = max(2, ny // 14)
            source_rect = (cy - r, cy + r + 1, cx - r, cx + r + 1)
        self.source = np.zeros((ny, nx), dtype=bool)
        i0, i1, j0, j1 = source_rect
        self.source[i0:i1, j0:j1] = True
        self.Q = np.zeros((ny, nx))
        self.Q[self.source] = Q_total / self.source.sum()
        self.max_cells = int(budget * ny * nx)

    def set_source(self, rects):
        self.source[:] = False
        for (i0, i1, j0, j1) in rects:
            self.source[i0:i1, j0:j1] = True
        self.Q[:] = 0.0
        self.Q[self.source] = self.Q_total / self.source.sum()


def largest_connected(mask, seed):
    ny, nx = mask.shape
    out = np.zeros_like(mask)
    stack = [tuple(p) for p in np.argwhere(seed & mask)]
    for p in stack:
        out[p] = True
    while stack:
        i, j = stack.pop()
        for di, dj in ((-1, 0), (1, 0), (0, -1), (0, 1)):
            ii, jj = i + di, j + dj
            if 0 <= ii < ny and 0 <= jj < nx and mask[ii, jj] and not out[ii, jj]:
                out[ii, jj] = True
                stack.append((ii, jj))
    return out


def _perimeter(mask):
    ny, nx = mask.shape
    per = np.zeros((ny, nx), dtype=bool)
    for di, dj in ((-1, 0), (1, 0), (0, -1), (0, 1)):
        sh = np.zeros((ny, nx), dtype=bool)
        i0, i1 = max(0, -di), min(ny, ny - di)
        j0, j1 = max(0, -dj), min(nx, nx - dj)
        sh[i0:i1, j0:j1] = mask[i0 + di:i1 + di, j0 + dj:j1 + dj]
        per |= sh
    return per & ~mask


# ----------------------------------------------------------------------
def thin_fraction(mask, source):
    ny, nx = mask.shape
    nbr = np.zeros((ny, nx), dtype=int)
    for di, dj in ((-1, 0), (1, 0), (0, -1), (0, 1)):
        sh = np.zeros((ny, nx), dtype=bool)
        i0, i1 = max(0, -di), min(ny, ny - di)
        j0, j1 = max(0, -dj), min(nx, nx - dj)
        sh[i0:i1, j0:j1] = mask[i0 + di:i1 + di, j0 + dj:j1 + dj]
        nbr += (sh & mask)
    thin = ((nbr < 2) & mask & ~source).sum()
    return thin / max(mask.sum(), 1)


_WARM = {"T": None}

def fitness2(mask, prob, channel=True, radiation=True):
    """Peak temperature plus a manufacturability penalty. Lower is better,
    returned negated so that bigger is better.

    Warm starts the radiation iteration from the last solved field, which is
    6x faster and gives an identical answer to 1e-4 C.
    """
    m = largest_connected(mask | prob.source, prob.source)
    n = m.sum()
    if n == 0 or n > prob.max_cells:
        return -1e9, None
    T = solve2(m, prob.mat, prob.dx, Q=prob.Q,
               channel=channel, radiation=radiation, T0=_WARM["T"])
    _WARM["T"] = T
    peak = float(np.nanmax(T))
    tf = thin_fraction(m, prob.source)
    score = -(peak + prob.width_penalty * tf * (peak - prob.mat.T_inf))
    return score, m


# ----------------------------------------------------------------------
# behaviour descriptors for MAP-Elites
# ----------------------------------------------------------------------
# Descriptor ranges, MEASURED not guessed. A first attempt used arbitrary
# normalisers and every design landed in the same bin: the archive filled
# only 2.1% of its cells and MAP-Elites lost to the plain GA on all four
# seeds. Sampling 150 mutated designs showed the true spans were 0.14 to
# 0.21 and 0.17 to 0.20, so the descriptors were rescaled to the ranges the
# search actually visits.
# Second attempt also failed: I guessed 0.9 to 3.2 and everything clipped to
# zero. These numbers are now MEASURED from 360 sampled designs, taking the
# 2nd and 98th percentile of what the search actually produces.
D0_LO, D0_HI = 0.56, 0.82    # mean air gap next to metal, in cell widths
D1_LO, D1_HI = 5.45, 6.07    # mean distance from the chip, in cells

def descriptors(mask, prob):
    """Two numbers in [0,1] describing the SHAPE, not the quality.

    d0  openness: mean air gap beside the metal, in cell widths.
        0 = one dense lump, 1 = thin open filigree.
    d1  reach: mean distance of metal from the chip, in cells.
        0 = hugging the chip, 1 = flung to the corners.
    """
    from physics2 import gap_width
    n = mask.sum()
    if n == 0:
        return 0.0, 0.0
    g = gap_width(mask, prob.dx)[mask] / prob.dx        # in cells
    d0 = float(np.clip((g.mean() - D0_LO) / (D0_HI - D0_LO), 0, 1))

    ys, xs = np.nonzero(mask)
    sy, sx = np.nonzero(prob.source)
    r = np.hypot(ys - sy.mean(), xs - sx.mean())        # in cells
    d1 = float(np.clip((r.mean() - D1_LO) / (D1_HI - D1_LO), 0, 1))
    return d0, d1


class Archive:
    """The memory. One best design per shape bin, never forgotten."""

    def __init__(self, bins=12):
        self.bins = bins
        self.best = {}          # (i,j) -> (score, mask)
        self.tried = 0
        self.improved = 0

    def key(self, d0, d1):
        i = min(self.bins - 1, int(d0 * self.bins))
        j = min(self.bins - 1, int(d1 * self.bins))
        return (i, j)

    def add(self, score, mask, d0, d1):
        self.tried += 1
        k = self.key(d0, d1)
        cur = self.best.get(k)
        if cur is None or score > cur[0]:
            self.best[k] = (score, mask.copy())
            self.improved += 1
            return True
        return False

    def sample(self, rng):
        if not self.best:
            return None
        ks = list(self.best.keys())
        return self.best[ks[rng.integers(0, len(ks))]][1]

    def champion(self):
        if not self.best:
            return None, -np.inf
        k = max(self.best, key=lambda k: self.best[k][0])
        s, m = self.best[k]
        return m, s

    @property
    def coverage(self):
        return len(self.best) / (self.bins * self.bins)

    def qd_score(self, floor):
        """Sum of (score - floor) over filled bins. The standard
        quality-diversity metric: rewards both filling bins and filling
        them well."""
        return sum(max(0.0, s - floor) for s, _ in self.best.values())

    def grid(self):
        g = np.full((self.bins, self.bins), np.nan)
        for (i, j), (s, _) in self.best.items():
            g[i, j] = s
        return g


# ----------------------------------------------------------------------
def random_design(prob, rng):
    target = int(prob.max_cells * rng.uniform(0.85, 1.0))
    m = prob.source.copy()
    guard = 0
    while m.sum() < target and guard < prob.ny * prob.nx * 3:
        guard += 1
        per = _perimeter(m)
        cand = np.argwhere(per)
        if len(cand) == 0:
            break
        k = max(1, min(len(cand), int(rng.integers(1, 6))))
        for p in np.atleast_1d(rng.choice(len(cand), size=k, replace=False)):
            i, j = cand[p]
            m[i, j] = True
    return m


def mutate(mask, prob, rng, rate=0.035, T=None):
    m = largest_connected(mask | prob.source, prob.source)
    n_ops = max(1, int(rate * prob.ny * prob.nx * 0.5))

    n_prune = int(rng.integers(0, n_ops + 1))
    if n_prune > 0:
        ny, nx = m.shape
        nbr = np.zeros((ny, nx), dtype=int)
        for di, dj in ((-1, 0), (1, 0), (0, -1), (0, 1)):
            sh = np.zeros((ny, nx), dtype=bool)
            i0, i1 = max(0, -di), min(ny, ny - di)
            j0, j1 = max(0, -dj), min(nx, nx - dj)
            sh[i0:i1, j0:j1] = m[i0 + di:i1 + di, j0 + dj:j1 + dj]
            nbr += (sh & m)
        tips = np.argwhere(m & ~prob.source & (nbr <= 2))
        if len(tips) > 0:
            if T is not None and rng.random() < 0.5:
                t = np.nan_to_num(np.array([T[i, j] for i, j in tips]),
                                  nan=prob.mat.T_inf)
                w = (t.max() - t) + 1e-6
                w = w / w.sum()
                pick = rng.choice(len(tips), size=min(n_prune, len(tips)),
                                  replace=False, p=w)
            else:
                pick = rng.choice(len(tips), size=min(n_prune, len(tips)),
                                  replace=False)
            for p in np.atleast_1d(pick):
                i, j = tips[p]
                m[i, j] = False
        m = largest_connected(m | prob.source, prob.source)

    room = prob.max_cells - m.sum()
    for _ in range(max(0, int(min(room, rng.integers(0, n_ops + 1))))):
        per = _perimeter(m)
        cand = np.argwhere(per)
        if len(cand) == 0:
            break
        i, j = cand[rng.integers(0, len(cand))]
        m[i, j] = True

    guard = 0
    while m.sum() < prob.max_cells * 0.97 and guard < 4000:
        guard += 1
        per = _perimeter(m)
        cand = np.argwhere(per)
        if len(cand) == 0:
            break
        i, j = cand[rng.integers(0, len(cand))]
        m[i, j] = True
    return largest_connected(m | prob.source, prob.source)


def crossover(a, b, prob, rng):
    m = a.copy()
    if rng.random() < 0.5:
        c = rng.integers(1, prob.nx); m[:, c:] = b[:, c:]
    else:
        c = rng.integers(1, prob.ny); m[c:, :] = b[c:, :]
    m = largest_connected(m | prob.source, prob.source)
    guard = 0
    while m.sum() < prob.max_cells * 0.97 and guard < 4000:
        guard += 1
        per = _perimeter(m)
        cand = np.argwhere(per)
        if len(cand) == 0:
            break
        i, j = cand[rng.integers(0, len(cand))]
        m[i, j] = True
    over = m.sum() - prob.max_cells
    if over > 0:
        rem = np.argwhere(m & ~prob.source)
        for p in np.atleast_1d(rng.choice(len(rem), size=min(over, len(rem)),
                                          replace=False)):
            i, j = rem[p]
            m[i, j] = False
        m = largest_connected(m | prob.source, prob.source)
    return m


# ----------------------------------------------------------------------
def evolve_plain(prob, generations=150, pop=24, elite=4, seed=0,
                 rate=0.035, channel=True, radiation=True):
    """The original genetic algorithm, kept so the two can be compared."""
    rng = np.random.default_rng(seed)
    P = [random_design(prob, rng) for _ in range(pop)]
    best, bestm = -np.inf, None
    hist = []
    for g in range(generations):
        sc = []
        for m in P:
            s, mm = fitness2(m, prob, channel, radiation)
            sc.append((s, m))
        sc.sort(key=lambda t: -t[0])
        if sc[0][0] > best:
            best, bestm = sc[0][0], sc[0][1].copy()
        hist.append(best)
        r = rate * (1 - 0.55 * min(g / 260, 1))
        nxt = [s[1].copy() for s in sc[:elite]]
        while len(nxt) < pop:
            i, j = rng.integers(0, max(2, pop // 2), size=2)
            nxt.append(mutate(crossover(sc[i][1], sc[j][1], prob, rng),
                              prob, rng, r))
        P = nxt
    return largest_connected(bestm | prob.source, prob.source), best, hist


def evolve_mapelites(prob, evaluations=3600, seed=0, rate=0.035,
                     bins=12, init=64, channel=True, radiation=True,
                     log_every=None):
    """MAP-Elites. Same budget of evaluations, but with a memory."""
    rng = np.random.default_rng(seed)
    arch = Archive(bins=bins)
    hist = []

    for _ in range(init):
        m = random_design(prob, rng)
        s, mm = fitness2(m, prob, channel, radiation)
        if mm is not None:
            d0, d1 = descriptors(mm, prob)
            arch.add(s, mm, d0, d1)
        hist.append(arch.champion()[1])

    while arch.tried < evaluations:
        parent = arch.sample(rng)
        if parent is None:
            parent = random_design(prob, rng)
        # occasionally splice two archive members, which is how stepping
        # stones in different bins get combined
        if rng.random() < 0.25:
            other = arch.sample(rng)
            if other is not None:
                parent = crossover(parent, other, prob, rng)
        # a wider mutation range helps the search reach unfilled bins
        r = rate * rng.uniform(0.4, 2.5)
        child = mutate(parent, prob, rng, r)
        s, mm = fitness2(child, prob, channel, radiation)
        if mm is not None:
            d0, d1 = descriptors(mm, prob)
            arch.add(s, mm, d0, d1)
        hist.append(arch.champion()[1])
        if log_every and arch.tried % log_every == 0:
            print(f"      {arch.tried:5d} evals  coverage {arch.coverage:5.1%}"
                  f"  best {-arch.champion()[1]:7.2f}")

    m, s = arch.champion()
    return largest_connected(m | prob.source, prob.source), s, hist, arch


# ----------------------------------------------------------------------
def radial_fins2(prob, n_fins=8, fin_width=2, hub_r=None):
    """Conventional baseline. Hub follows the chip, not the grid centre."""
    ny, nx = prob.ny, prob.nx
    ys, xs = np.nonzero(prob.source)
    cy, cx = (ys.mean(), xs.mean()) if len(ys) else (ny/2-0.5, nx/2-0.5)
    m = prob.source.copy()
    if hub_r is None:
        hub_r = max(3, ny // 10)
    yy, xx = np.indices((ny, nx))
    m |= (np.hypot(yy - cy, xx - cx) <= hub_r)
    R = max(np.hypot(cy, cx), np.hypot(cy, nx-1-cx),
            np.hypot(ny-1-cy, cx), np.hypot(ny-1-cy, nx-1-cx))
    for k in range(n_fins):
        a = 2 * np.pi * k / n_fins
        for t in np.linspace(0, R, int(R * 4)):
            pi_, pj_ = cy + t*np.sin(a), cx + t*np.cos(a)
            w = fin_width // 2
            for wy in range(-w, w+1):
                for wx in range(-w, w+1):
                    i, j = int(round(pi_+wy)), int(round(pj_+wx))
                    if 0 <= i < ny and 0 <= j < nx:
                        m[i, j] = True
    return largest_connected(m | prob.source, prob.source)


def best_baseline2(prob, channel=True, radiation=True):
    """Best conventional fin design that FITS THE BUDGET.

    BUG FIXED. The old version tried 18 fixed configurations and skipped any
    that exceeded the budget. Those 18 land on discrete cell counts (123, 271,
    504, 640 ...) so with a 425 cell budget the best legal option used only
    124 cells, 29% of what it was allowed, while the evolved design used 100%.
    That is not a fair comparison and it produced a fake +63.5% win.

    Now each configuration is trimmed from its outer tips down to the budget,
    so every candidate spends the full allowance, exactly like the search does.
    """
    ny, nx = prob.ny, prob.nx
    ys, xs = np.nonzero(prob.source)
    cy, cx = (ys.mean(), xs.mean()) if len(ys) else (ny/2-0.5, nx/2-0.5)
    yy, xx = np.indices((ny, nx))
    rad = np.hypot(yy - cy, xx - cx)

    def trim_to_budget(m):
        m = largest_connected(m | prob.source, prob.source)
        over = int(m.sum()) - prob.max_cells
        if over <= 0:
            return m
        # remove the furthest tips first, they are the coldest
        cand = np.argwhere(m & ~prob.source)
        order = np.argsort(-rad[m & ~prob.source])
        removed = 0
        for k in order:
            if removed >= over:
                break
            i, j = cand[k]
            m[i, j] = False
            removed += 1
        return largest_connected(m | prob.source, prob.source)

    best = None
    for nf in (4, 6, 8, 10, 12, 16, 20, 24):
        for w in (1, 2, 3):
            m = trim_to_budget(radial_fins2(prob, nf, w))
            if m.sum() == 0:
                continue
            T = solve2(m, prob.mat, prob.dx, Q=prob.Q,
                       channel=channel, radiation=radiation)
            pk = float(np.nanmax(T))
            if best is None or pk < best['peak']:
                best = dict(peak=pk, mask=m, n_fins=nf, width=w,
                            cells=int(m.sum()), T=T)
    return best
