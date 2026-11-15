"""The candidate's calibration by period and day type, and whether its misses cluster in time (#1363, H5, registration design).

A development study, never a verdict. It measures (s3c-ann-net), the H5 candidate, at the 18:00 decision instant: the empirical
coverage of the 50% and 90% bands, every grid quantile's hit rate, the randomised PIT of #970, by regime and by day type with each
group's size, and the serial dependence of the hit sequences at each lead (Christoffersen's independence test, its permutation
p-value and the protocol's own thinned reading), beside B1, B1' and B2. Nothing is adopted. B4 (#1360) was not on main when the study ran and is
not compared.

Every choice is in `metadata/candidate_calibration_1363.json`, which `walk` and `score` refuse to read unless it is committed and
unchanged. The only slow step is `walk`: it re-walks (s3c-ann-net) with the code of `scripts/s3c_announced_settlement_1288.py`
unchanged, for the ann arms only, and writes one file per window; `score` scores the windows that exist. No day after 2026-09-03 and
no locked day is read.

    PYTHONPATH=src python3 -m repo_model.cli build --raw-root tests/fixtures/snapshots/funding_inputs --output PUB.csv \\
        --build-cutoff 2026-09-08T21:31:42+00:00 --decision-time 18:00:00
    OUT=docs/research/candidate-calibration-1363
    RMM_DECISION_TIME=18:00 PYTHONPATH=src python3 scripts/candidate_calibration_1363.py walk --panel PUB.csv --window development --output WALK/development.json
    RMM_DECISION_TIME=18:00 PYTHONPATH=src python3 scripts/candidate_calibration_1363.py walk --panel PUB.csv --window 2026 --output WALK/2026.json
    PYTHONPATH=src python3 scripts/candidate_calibration_1363.py score --walks WALK --output $OUT/result.json
    PYTHONPATH=src python3 scripts/candidate_calibration_1363.py page --score $OUT/result.json --output docs/research/candidate-calibration-1363-result.md
"""

from __future__ import annotations

import argparse
import bisect
import hashlib
import importlib.util
import json
import math
import os
import random
import subprocess
import sys
from datetime import date
from multiprocessing import Pool
from pathlib import Path
from typing import Dict, List, Mapping, Optional, Sequence, Tuple

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))

from repo_model import coverage_tests, metrics, scoring_protocol as sp  # noqa: E402
from repo_model.exploration import EXPLORATORY_END, require_exploratory_window  # noqa: E402
from repo_model.splits import LookAheadError  # noqa: E402

DECLARATION = REPO / "metadata" / "candidate_calibration_1363.json"
OUT = REPO / "docs" / "research" / "candidate-calibration-1363"
SEED = 1363
EXTRA_SEEDS = tuple(range(1364, 1384))
REPS = 2000
PERMUTATIONS = 10_000
BLOCK = 10.0
LEVEL = 0.90
MIN_GROUP_DAYS = 20
GRID = sp.GRID
LEADS = tuple(sp.HORIZONS)
KEY_LEVELS = (0.01, 0.05, 0.25, 0.5, 0.75, 0.95, 0.99)
WINDOWS = ("development", "2026")
WINDOW_LAST = {"development": date(2025, 12, 31), "2026": EXPLORATORY_END}
CANDIDATE = "sc_s3c_ann_net"
REFERENCES = ("B1", "B1_prime", "B2")
MODELS = (CANDIDATE,) + REFERENCES
LABELS = {CANDIDATE: "(s3c-ann-net)", "B1": "B1", "B1_prime": "B1'", "B2": "B2"}
BANDS = {"band50": (GRID.index(0.25), GRID.index(0.75), 0.50), "band90": (GRID.index(0.05), GRID.index(0.95), 0.90)}
PIT_EDGES = (0.10, 0.25, 0.50, 0.75, 0.90)
PIT_EXPECTED = (0.10, 0.15, 0.25, 0.25, 0.15, 0.10)
DAY_TYPES = ("quarter_end", "month_end", "tax_date", "coupon_settlement", "bill_settlement", "fomc_day", "iorb_window", "dom_19_23",
             "post_month_end_window", "ordinary")
EVENTS = ("upper", "lower", "band90", "band50")
RULES = ("strict", "weak")
SEQUENCES = tuple(f"{e}/{r}" for e in EVENTS for r in RULES)


# Lockbox classification (#1058): tests/test_lockbox.py reads these literals from this file's syntax tree.
LOCKBOX_CRPS = {
    "reproduction_check": (
        "delegates",
        "scores the cells of the walk files `walk_command` wrote; `walk_command` calls `require_exploratory_window` "
        "and `refuse_beyond` on every panel day, decision day and target day before it writes a file, and "
        "`score_command` reads those files back without a second check (#1363, #1568)",
    ),
}


def refuse_beyond(days: Sequence[date], last: date, *, where: str = "candidate_calibration_1363") -> None:
    """Refuse a day after `last` (the window's declared end) and a day of a tier that is still locked: raises `LookAheadError`."""

    days = sorted(days)
    for day in days:
        if day > last:
            raise LookAheadError(f"{where}: day {day} is after {last}, the last day of the window this study scores")
    require_exploratory_window(days, where=where)


def committed_declaration(path: Path = DECLARATION) -> dict:
    """The declaration, refused unless it is committed and unchanged since `HEAD`."""

    relative = str(path.resolve().relative_to(REPO))
    dirty = subprocess.run(["git", "status", "--porcelain", "--", relative], cwd=REPO, capture_output=True, text=True, check=True).stdout.strip()
    if dirty:
        raise SystemExit(f"{relative} is not committed ({dirty}); a declaration is made before any score")
    return json.loads(path.read_text(encoding="utf-8"))


# -- hits ----------------------------------------------------------------------------------------------------------------------


def level_shares(quantiles: Sequence[float], y: float) -> Tuple[List[int], List[int]]:
    """Per grid level: 1 where `y < q` (strictly below) and 1 where `y <= q` (at or below), as two lists."""

    return [int(y < q) for q in quantiles], [int(y <= q) for q in quantiles]


def band_hits(quantiles: Sequence[float], y: float) -> Dict[str, int]:
    """1 where `y` is inside the band, closed (`lo <= y <= hi`) and open (`lo < y < hi`), for the 50% and the 90% band."""

    out = {}
    for name, (lo, hi, _nominal) in BANDS.items():
        out[f"{name}_closed"] = int(quantiles[lo] <= y <= quantiles[hi])
        out[f"{name}_open"] = int(quantiles[lo] < y < quantiles[hi])
    return out


def event_hits(quantiles: Sequence[float], y: float) -> Dict[str, int]:
    """The eight miss sequences of one cell: upper tail (beyond q95), lower tail (beyond q05), outside the 90% band, outside the 50% band,
    each as a strict miss (clearly beyond) and a weak miss (a tie counts)."""

    q05, q25, q75, q95 = (quantiles[GRID.index(p)] for p in (0.05, 0.25, 0.75, 0.95))
    return {
        "upper/strict": int(y > q95), "upper/weak": int(y >= q95),
        "lower/strict": int(y < q05), "lower/weak": int(y <= q05),
        "band90/strict": int(y < q05 or y > q95), "band90/weak": int(y <= q05 or y >= q95),
        "band50/strict": int(y < q25 or y > q75), "band50/weak": int(y <= q25 or y >= q75),
    }


# -- readings ------------------------------------------------------------------------------------------------------------------


def read_band(interval: Optional[Sequence[float]], nominal: float) -> str:
    if interval is None:
        return "not tested"
    return "over-covers" if interval[0] > nominal else "under-covers" if interval[1] < nominal else "consistent"


def read_level(strict_interval: Optional[Sequence[float]], at_or_below_interval: Optional[Sequence[float]], tau: float) -> str:
    """'quantile too high' when the interval of the strict share lies wholly above tau (too many outcomes below q), 'quantile too low' when the
    interval of the at-or-below share lies wholly below tau, otherwise 'consistent'."""

    if strict_interval is None or at_or_below_interval is None:
        return "not tested"
    if strict_interval[0] > tau:
        return "quantile too high"
    if at_or_below_interval[1] < tau:
        return "quantile too low"
    return "consistent"


def size_of_level(strict: float, at_or_below: float, tau: float) -> float:
    """The signed distance of tau from the nearer end of [strict, at-or-below]: positive when the quantile is too high; zero inside."""

    if strict > tau:
        return strict - tau
    if at_or_below < tau:
        return at_or_below - tau
    return 0.0


# -- the bootstrap -------------------------------------------------------------------------------------------------------------


def series_intervals(series: Mapping[str, Sequence[float]], *, reps: int = REPS, seed: int = SEED) -> Dict[str, Tuple[float, float]]:
    """90% stationary-bootstrap percentile intervals (mean block 10, in the order given) of the mean of each named series, off the same
    resamples (`metrics.stationary_bootstrap_intervals`)."""

    names = list(series)
    if not names:
        return {}
    n = len(series[names[0]])
    columns = [series[k] for k in names]

    def statistic(indices):
        return [sum(map(c.__getitem__, indices)) / n for c in columns]

    found = metrics.stationary_bootstrap_intervals(statistic, n, block_length=BLOCK, seed=seed, replications=reps, level=LEVEL)
    return dict(zip(names, found))


# -- the PIT -------------------------------------------------------------------------------------------------------------------


def _pit_module():
    spec = importlib.util.spec_from_file_location("randomised_pit_970_in_1363", REPO / "scripts" / "randomised_pit_970.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def brackets(cells: Sequence[Tuple[Sequence[float], float]]) -> List[Tuple[float, float]]:
    """The level bracket of each (law, outcome), as #970's `pit_bracket`."""

    m = _pit_module()
    return [m.pit_bracket(q, y) for q, y in cells]


def pit_values(bracket_list: Sequence[Tuple[float, float]], seed: int) -> List[float]:
    """#970's randomised PIT: one uniform draw per cell, in the order given, inside the bracket."""

    rng = random.Random(seed)
    return [lo + rng.random() * (hi - lo) for lo, hi in bracket_list]


def pit_summary(bracket_list: Sequence[Tuple[float, float]]) -> dict:
    """Six-bin shares of the randomised PIT (seed 1363), its shares at or below 0.10 and at or above 0.90, and their range over 20 more seeds."""

    n = len(bracket_list)
    values = pit_values(bracket_list, SEED)
    counts = [0] * len(PIT_EXPECTED)
    for v in values:
        counts[bisect.bisect_right(PIT_EDGES, v)] += 1
    low = [sum(v <= 0.10 for v in pit_values(bracket_list, s)) / n for s in EXTRA_SEEDS]
    high = [sum(v >= 0.90 for v in pit_values(bracket_list, s)) / n for s in EXTRA_SEEDS]
    return {
        "n": n, "bins": [k / n for k in counts], "expected": list(PIT_EXPECTED), "mean": sum(values) / n,
        "at_or_below_0.10": sum(v <= 0.10 for v in values) / n, "at_or_above_0.90": sum(v >= 0.90 for v in values) / n,
        "at_or_below_0.10_other_seeds": [min(low), max(low)], "at_or_above_0.90_other_seeds": [min(high), max(high)],
    }


# -- serial dependence ---------------------------------------------------------------------------------------------------------


def runs_of(positions: Sequence[int], breaks: Optional[Sequence[object]] = None) -> List[int]:
    """Lengths of the runs of consecutive panel positions; a run also ends where `breaks` (one label per element) changes."""

    out, length = [], 0
    for i, p in enumerate(positions):
        if i and (p != positions[i - 1] + 1 or (breaks is not None and breaks[i] != breaks[i - 1])):
            out.append(length)
            length = 0
        length += 1
    if length:
        out.append(length)
    return out


def transition_counts(sequence: Sequence[int], runs: Sequence[int]) -> Tuple[int, int, int, int]:
    """(n00, n01, n10, n11) summed over the runs; no transition is counted across a run boundary."""

    if sum(runs) != len(sequence):
        raise ValueError(f"the runs cover {sum(runs)} elements and the sequence has {len(sequence)}")
    n = [[0, 0], [0, 0]]
    start = 0
    for length in runs:
        part = sequence[start:start + length]
        for prev, today in zip(part, part[1:]):
            n[prev][today] += 1
        start += length
    return n[0][0], n[0][1], n[1][0], n[1][1]


def _ll(zeros: int, ones: int, p: float) -> float:
    return (zeros * math.log(1.0 - p) if zeros else 0.0) + (ones * math.log(p) if ones else 0.0)


def lr_independence(n00: int, n01: int, n10: int, n11: int) -> float:
    """Christoffersen's independence statistic from transition counts (as `coverage_tests.christoffersen_independence`)."""

    total = n00 + n01 + n10 + n11
    if total == 0:
        return 0.0
    pi = (n01 + n11) / total
    pi01 = n01 / (n00 + n01) if n00 + n01 else 0.0
    pi11 = n11 / (n10 + n11) if n10 + n11 else 0.0
    stat = -2.0 * (_ll(n00 + n10, n01 + n11, pi) - (_ll(n00, n01, pi01) + _ll(n10, n11, pi11)))
    return max(0.0, stat)


def permutation_p(sequence: Sequence[int], runs: Sequence[int], *, permutations: int = PERMUTATIONS, seed: int = SEED) -> float:
    """The share of random placements of the same number of misses (the runs kept) whose independence statistic is at least the observed one.

    A placement is drawn by sampling the miss positions; the counts are read off the sample, so a draw costs the number of misses.
    """

    n = len(sequence)
    ok = [False] * n  # ok[p]: p and p + 1 are in the same run
    start = 0
    for length in runs:
        for p in range(start, start + length - 1):
            ok[p] = True
        start += length
    valid = sum(ok)
    k = sum(sequence)
    observed = lr_independence(*transition_counts(sequence, runs))
    if valid == 0 or k == 0 or k == n:
        return 1.0
    rng = random.Random(seed)
    at_least = 0
    for _ in range(permutations):
        chosen = rng.sample(range(n), k)
        members = set(chosen)
        prev1 = sum(1 for p in chosen if ok[p])
        today1 = sum(1 for p in chosen if p and ok[p - 1])
        n11 = sum(1 for p in chosen if ok[p] and p + 1 in members)
        n10, n01 = prev1 - n11, today1 - n11
        n00 = valid - n11 - n10 - n01
        if lr_independence(n00, n01, n10, n11) >= observed - 1e-9:
            at_least += 1
    return (1 + at_least) / (1 + permutations)


def longest_run(sequence: Sequence[int]) -> int:
    best = run = 0
    for v in sequence:
        run = run + 1 if v else 0
        best = max(best, run)
    return best


def sequence_report(sequence: Sequence[int], runs: Sequence[int], *, permutations: int = PERMUTATIONS, seed: int = SEED) -> dict:
    """Independence of one hit sequence: counts, the asymptotic and permutation p-values, and the descriptive rates."""

    n00, n01, n10, n11 = transition_counts(sequence, runs)
    stat = lr_independence(n00, n01, n10, n11)
    after_hit = n11 / (n10 + n11) if n10 + n11 else None
    after_none = n01 / (n00 + n01) if n00 + n01 else None
    return {
        "n": len(sequence), "misses": sum(sequence), "rate": sum(sequence) / len(sequence) if sequence else None,
        "transitions": [n00, n01, n10, n11], "statistic": stat, "p_asymptotic": coverage_tests.chi2_sf(stat, 1),
        "p_permutation": permutation_p(sequence, runs, permutations=permutations, seed=seed),
        "p_miss_after_miss": after_hit, "p_miss_after_hit": after_none, "longest_run": longest_run(sequence), "runs": len(runs),
    }


def holm_flags(p_values: Mapping[str, float], alpha: float = sp.ALPHA) -> Dict[str, bool]:
    return sp.holm(dict(p_values), alpha)


# -- the cells of a window -----------------------------------------------------------------------------------------------------


class Window:
    """One window's walk file, read into arrays: cells in (decision day, lead) order and each model's 23 quantiles per cell."""

    def __init__(self, doc: Mapping[str, object]):
        self.name = doc["window"]
        self.calendar = [date.fromisoformat(x) for x in doc["calendar"]]
        self.position = {d: i for i, d in enumerate(self.calendar)}
        self.cells = [(date.fromisoformat(d), int(h), date.fromisoformat(t)) for d, h, t in doc["cells"]]
        self.outcome = {date.fromisoformat(t): float(y) for t, y in doc["outcome"].items()}
        self.y = [self.outcome[t] for _d, _h, t in self.cells]
        self.q = {m: doc["models"][m] for m in doc["models"]}
        self.target_info = {date.fromisoformat(t): v for t, v in doc["targets"].items()}
        self.regime_of_day = {date.fromisoformat(d): r for d, r in doc["regime_of_day"].items()}
        self.days = sorted({d for d, _h, _t in self.cells})
        for m, rows in self.q.items():
            if len(rows) != len(self.cells):
                raise ValueError(f"model {m} has {len(rows)} forecasts for {len(self.cells)} cells")

    def last_day(self) -> date:
        return max(t for _d, _h, t in self.cells)

    def groups(self) -> List[Tuple[str, str, List[int]]]:
        """(split, label, cell indices): pooled, by lead, regime, target-day type and pressure-day type; target-day types overlap."""

        out: List[Tuple[str, str, List[int]]] = [("pooled", "all cells", list(range(len(self.cells))))]
        for h in LEADS:
            out.append(("lead", f"h={h}", [i for i, (_d, hh, _t) in enumerate(self.cells) if hh == h]))
        by: Dict[Tuple[str, str], List[int]] = {}
        for i, (_d, _h, t) in enumerate(self.cells):
            info = self.target_info[t]
            by.setdefault(("regime", info["regime"]), []).append(i)
            for kind in info["types"]:
                by.setdefault(("target_day_type", kind), []).append(i)
            by.setdefault(("pressure_day_type", info["pressure"]), []).append(i)
        order = {"regime": sorted, "target_day_type": lambda keys: [k for k in DAY_TYPES if k in keys], "pressure_day_type": sorted}
        for split in ("regime", "target_day_type", "pressure_day_type"):
            labels = order[split]([lab for (s, lab) in by if s == split])
            out += [(split, lab, by[(split, lab)]) for lab in labels]
        return out


def target_series(window: Window, indices: Sequence[int], values: Mapping[str, Sequence[float]]) -> Dict[str, List[float]]:
    """Each named per-cell 0/1 list as a series over the group's target days in date order: the mean of the cells that target each day."""

    slots: Dict[date, List[int]] = {}
    for i in indices:
        slots.setdefault(window.cells[i][2], []).append(i)
    ordered = [slots[t] for t in sorted(slots)]
    return {k: [sum(v[i] for i in cell) / len(cell) for cell in ordered] for k, v in values.items()}


def cell_hits(window: Window, model: str) -> Dict[str, List[float]]:
    """Per-cell hit lists for a model: `strict_<level>`, `atbelow_<level>` for the key levels, and the four band flags."""

    out: Dict[str, List[float]] = {}
    shares = [level_shares(q, y) for q, y in zip(window.q[model], window.y)]
    for tau in KEY_LEVELS:
        j = GRID.index(tau)
        out[f"strict_{tau}"] = [s[0][j] for s in shares]
        out[f"atbelow_{tau}"] = [s[1][j] for s in shares]
    bands = [band_hits(q, y) for q, y in zip(window.q[model], window.y)]
    for key in bands[0]:
        out[key] = [b[key] for b in bands]
    return out


def group_report(window: Window, model: str, split: str, label: str, indices: Sequence[int], hits: Mapping[str, Sequence[float]],
                 pit_brackets: Sequence[Tuple[float, float]], *, reps: int = REPS) -> dict:
    """One group of one model: sizes, the rates with intervals (where the group has 20 or more target days), the readings and the PIT."""

    days = sorted({window.cells[i][2] for i in indices})
    n_cells = len(indices)
    row: dict = {"split": split, "label": label, "target_days": len(days), "cells": n_cells, "tested": len(days) >= MIN_GROUP_DAYS}
    mean = lambda name: sum(hits[name][i] for i in indices) / n_cells  # noqa: E731
    intervals: Dict[str, Tuple[float, float]] = {}
    if row["tested"]:
        intervals = series_intervals(target_series(window, indices, {k: hits[k] for k in hits}), reps=reps)
    for name, (_lo, _hi, nominal) in BANDS.items():
        entry = {"nominal": nominal}
        for rule in ("closed", "open"):
            key = f"{name}_{rule}"
            entry[rule] = mean(key)
            entry[f"{rule}_interval"] = list(intervals[key]) if key in intervals else None
        entry["reading"] = read_band(entry["closed_interval"], nominal)
        entry["size"] = entry["closed"] - nominal
        row[name] = entry
    levels = {}
    for tau in KEY_LEVELS:
        s, a = mean(f"strict_{tau}"), mean(f"atbelow_{tau}")
        si, ai = intervals.get(f"strict_{tau}"), intervals.get(f"atbelow_{tau}")
        levels[str(tau)] = {"strict": s, "at_or_below": a, "strict_interval": list(si) if si else None,
                            "at_or_below_interval": list(ai) if ai else None,
                            "reading": read_level(si, ai, tau), "size": size_of_level(s, a, tau)}
    row["levels"] = levels
    row["pit"] = pit_summary([pit_brackets[i] for i in indices])
    return row


def all_level_rates(window: Window, model: str) -> Dict[str, dict]:
    """The strict and at-or-below shares at all 23 grid levels, over all cells (points only)."""

    n = len(window.cells)
    strict = [0] * len(GRID)
    atbelow = [0] * len(GRID)
    for q, y in zip(window.q[model], window.y):
        s, a = level_shares(q, y)
        for j in range(len(GRID)):
            strict[j] += s[j]
            atbelow[j] += a[j]
    return {str(tau): {"strict": strict[j] / n, "at_or_below": atbelow[j] / n} for j, tau in enumerate(GRID)}


def lead_sequences(window: Window, model: str, lead: int) -> Tuple[List[int], Dict[str, List[int]], List[str]]:
    """Positions of the decision days of one lead in order, the eight 0/1 miss sequences, and the regime of each decision day."""

    rows = [i for i, (_d, h, _t) in enumerate(window.cells) if h == lead]
    rows.sort(key=lambda i: window.cells[i][0])
    positions = [window.position[window.cells[i][0]] for i in rows]
    events = [event_hits(window.q[model][i], window.y[i]) for i in rows]
    seqs = {name: [e[name] for e in events] for name in SEQUENCES}
    regimes = [window.regime_of_day[window.cells[i][0]] for i in rows]
    return positions, seqs, regimes


def _sequence_task(job):
    key, sequence, runs, permutations, seed = job
    return key, sequence_report(sequence, runs, permutations=permutations, seed=seed)


def clustering(window: Window, model: str, *, permutations: int = PERMUTATIONS, workers: int = 1, regimes: bool = True) -> dict:
    """The independence tests of every lead's eight sequences, on all days and (for the development window) inside each regime."""

    jobs, meta = [], {}
    for lead in LEADS:
        positions, seqs, regime_labels = lead_sequences(window, model, lead)
        all_runs = runs_of(positions)
        for name, seq in seqs.items():
            jobs.append((("all", lead, name, None), seq, all_runs, permutations, SEED))
        if regimes:
            by_regime = runs_of(positions, regime_labels)
            starts, begin = [], 0
            for length in by_regime:
                starts.append((begin, length))
                begin += length
            for r in sorted(set(regime_labels)):
                parts = [(b, ln) for b, ln in starts if regime_labels[b] == r]
                for name, seq in seqs.items():
                    joined = [v for b, ln in parts for v in seq[b:b + ln]]
                    jobs.append((("regime", lead, name, r), joined, [ln for _b, ln in parts], permutations, SEED))
    if workers > 1:
        with Pool(workers) as pool:
            found = pool.map(_sequence_task, jobs, chunksize=4)
    else:
        found = [_sequence_task(j) for j in jobs]
    out: dict = {"all": {}, "regime": {}}
    for (kind, lead, name, r), rep in found:
        if kind == "all":
            out["all"].setdefault(str(lead), {})[name] = rep
        else:
            out["regime"].setdefault(r, {}).setdefault(str(lead), {})[name] = rep
    family = {f"{lead}/{name}": rep["p_permutation"] for lead, block in out["all"].items() for name, rep in block.items()}
    flagged = holm_flags(family)
    for lead, block in out["all"].items():
        for name, rep in block.items():
            rep["holm_clusters"] = flagged[f"{lead}/{name}"]
    for r, by_lead in out["regime"].items():
        family = {f"{lead}/{name}": rep["p_permutation"] for lead, block in by_lead.items() for name, rep in block.items()}
        flagged = holm_flags(family)
        for lead, block in by_lead.items():
            for name, rep in block.items():
                rep["holm_clusters"] = flagged[f"{lead}/{name}"]
    return out


def protocol_reading(window: Window, model: str) -> List[dict]:
    """The protocol's own thinned Kupiec and Christoffersen reading at q05 and q95 (`scoring_protocol.coverage_cells`), by lead and regime of the decision day."""

    forecasts: Dict[date, Dict[int, Sequence[float]]] = {}
    for (d, h, _t), q in zip(window.cells, window.q[model]):
        forecasts.setdefault(d, {})[h] = q
    cells = sp.coverage_cells(forecasts, window.outcome, window.calendar, window.regime_of_day, method="thinned")
    return [{"level": c.level, "lead": c.lead, "regime": c.regime, "rule": c.rule, "n": c.n, "hits": c.hits, "kupiec_p": c.kupiec_p,
             "independence_p": c.independence_p} for c in cells if c.level in (0.05, 0.95)]


def window_report(window: Window, *, reps: int = REPS, permutations: int = PERMUTATIONS, workers: int = 1) -> dict:
    refuse_beyond(sorted({t for _d, _h, t in window.cells} | set(window.days)), WINDOW_LAST[window.name])
    groups = window.groups()
    out: dict = {"window": window.name, "decision_days": len(window.days), "cells": len(window.cells),
                 "first_decision": window.days[0].isoformat(), "last_decision": window.days[-1].isoformat(),
                 "last_target": window.last_day().isoformat(), "models": {}}
    for model in MODELS:
        hits = cell_hits(window, model)
        pit_b = brackets(list(zip(window.q[model], window.y)))
        out["models"][model] = {
            "groups": [group_report(window, model, s, lab, idx, hits, pit_b, reps=reps) for s, lab, idx in groups],
            "all_levels": all_level_rates(window, model),
            "clustering": clustering(window, model, permutations=permutations, workers=workers, regimes=window.name == "development"),
            "protocol": protocol_reading(window, model),
        }
    return out


# -- the walk ------------------------------------------------------------------------------------------------------------------


def _load(name: str, alias: str):
    spec = importlib.util.spec_from_file_location(alias, REPO / "scripts" / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[alias] = module
    spec.loader.exec_module(module)
    return module


def walk_command(args) -> int:
    os.environ["RMM_DECISION_TIME"] = "18:00"
    declared = committed_declaration()
    from repo_model import announced_iorb, decision_instant, policy_events, s3c_announced, spread_mr_calendar as cal
    from repo_model.baseline import panel_sha256
    from repo_model.evaluation_splits import load_split_declaration

    m = _load("s3c_announced_settlement_1288", "s3c_announced_settlement_1288_in_1363")
    if decision_instant.DECISION_TIME.isoformat(timespec="minutes") != "18:00" or m.k.DECISION_TIME.isoformat(timespec="minutes") != "18:00":
        raise ValueError("this study is made at the 18:00 decision instant")
    window = args.window
    panel_path = Path(args.panel)
    sha = panel_sha256(panel_path)
    panel = [row for row in m.load_daily_panel(panel_path) if row.date <= m.LAST_DAY]
    require_exploratory_window([row.date for row in panel], where="scripts/candidate_calibration_1363")
    splits = load_split_declaration(m.c.SPLITS)
    registry = json.loads(m.c.SOURCES.read_text(encoding="utf-8"))
    register = policy_events.load_register()
    table = cal.TermTable(panel, announced_iorb.load_announcements(m.c.IORB_TABLE), decision_time=m.c.DECISION_TIME)
    auctions = m.m1273.load_auctions()
    results = m.load_results()
    frame, _notes, _mine, _cell_table, _groups = m.m1255.build(window, panel, splits, registry, table, register, args.first)
    days = m.candidate_days(frame, window, args.first)
    settings = dict(registry=registry, decision_time=m.k.DECISION_TIME, splits=splits)
    iorb = announced_iorb.load_announcements(m.c.IORB_TABLE)
    both = s3c_announced.AnnouncedTermTable(panel, iorb, results, decision_time=m.k.DECISION_TIME)
    net_table = s3c_announced.AnnouncedNetSizeTable(panel, auctions, decision_time=m.k.DECISION_TIME)
    walk = m.sc.walk(panel, days, both, m.s3c_net.constant_states(panel), (s3c_announced.ANN_ARM, s3c_announced.ANN_NET_ARM), sizes=net_table, **settings)
    raw = {d: walk.forecasts[s3c_announced.ANN_NET_ARM.name][d] for d in frame.days}
    candidate = m.m1255.s3c_forecasts(frame, register, raw)
    models = {CANDIDATE: candidate, "B1": frame.forecasts["B1"], "B1_prime": frame.forecasts[m.B1P], "B2": frame.forecasts["B2"]}
    cells, outcome, targets, regime_of_day = [], {}, {}, {}
    for d in frame.days:
        regime_of_day[d.isoformat()] = frame.regime(d)
        for h in LEADS:
            t = frame.target(d, h)
            cells.append([d.isoformat(), h, t.isoformat()])
            outcome[t.isoformat()] = frame.outcome[t]
            if t.isoformat() not in targets:
                flags = table.day_types(frame.position[t])
                kinds = [k for k in DAY_TYPES[:-1] if flags.get("settlement_coupon" if k == "coupon_settlement" else "settlement_bill" if k == "bill_settlement" else k)]
                targets[t.isoformat()] = {"regime": frame.regime(t), "types": kinds or ["ordinary"], "pressure": frame.day_type(t)}
    refuse_beyond([date.fromisoformat(c[2]) for c in cells] + list(frame.days), WINDOW_LAST[window])
    doc = {
        "window": window, "instant": "18:00", "panel_sha256": sha, "declaration": declared["issue"],
        "calendar": [row.date.isoformat() for row in panel], "cells": cells, "outcome": outcome, "targets": targets,
        "regime_of_day": regime_of_day, "refits": len(walk.fits),
        "models": {name: [list(fc[date.fromisoformat(d)][h]) for d, h, _t in cells] for name, fc in models.items()},
    }
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    Path(args.output).write_text(json.dumps(doc, separators=(",", ":")) + "\n", encoding="utf-8")
    print(f"wrote {args.output}: {window}, {len(frame.days)} decision days, {len(cells)} cells")
    return 0


# -- score ---------------------------------------------------------------------------------------------------------------------


def reproduction_check(window: Window, record: Mapping[str, object]) -> dict:
    """The mean grid CRPS of each model over all cells against the 1314 record of the same window, to 1e-9; raises `ValueError` otherwise."""

    group = record["windows"][window.name]["groups"]["pooled"]["all decision days"]["grid_crps"]["means"]
    out = {}
    for model, key in ((CANDIDATE, "sc_s3c_ann_net"), ("B1", "B1"), ("B1_prime", "B1_prime"), ("B2", "B2")):
        mine = sum(sp.grid_crps(q, y) for q, y in zip(window.q[model], window.y)) / len(window.cells)
        theirs = group[key]
        theirs = theirs["mean"] if isinstance(theirs, dict) else theirs
        if abs(mine - theirs) > 1e-9:
            raise ValueError(f"{window.name}: mean grid CRPS of {model} is {mine!r} here and {theirs!r} in the 1314 record")
        out[model] = {"mean_grid_crps": mine, "record": theirs}
    return out


RECORD_1314 = REPO / "docs" / "research" / "s3c-ann-net-1800-1314" / "announced-settlement-1800.json"


def score_command(args) -> int:
    declared = committed_declaration()
    record = json.loads(RECORD_1314.read_text(encoding="utf-8"))
    result: dict = {"issue": 1363, "declaration": "metadata/candidate_calibration_1363.json", "label": "development, not a verdict",
                    "seed": SEED, "reps": REPS, "permutations": PERMUTATIONS, "block": BLOCK, "level": LEVEL, "windows": {},
                    "reproduction": {}, "walk_files": {}, "b4": declared["b4"], "amendments": declared["amendments"]}
    for name in WINDOWS:
        path = Path(args.walks) / f"{name}.json"
        if not path.exists():
            continue
        raw = path.read_bytes()
        doc = json.loads(raw)
        if result.get("panel_sha256") not in (None, doc["panel_sha256"]):
            raise ValueError("the walk files were made from different panels")
        result["panel_sha256"] = doc["panel_sha256"]
        result["walk_files"][name] = {"sha256": hashlib.sha256(raw).hexdigest(), "refits": doc.get("refits")}
        window = Window(doc)
        result["reproduction"][name] = reproduction_check(window, record)
        result["windows"][name] = window_report(window, workers=args.workers)
    if not result["windows"]:
        raise SystemExit(f"no walk file in {args.walks}")
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    Path(args.output).write_text(json.dumps(result, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    return 0


# -- the page ------------------------------------------------------------------------------------------------------------------


def _p(x: Optional[float], digits: int = 1) -> str:
    return "n/a" if x is None else f"{100 * x:.{digits}f}%"


def _iv(iv: Optional[Sequence[float]]) -> str:
    return "" if not iv else f" [{100 * iv[0]:.1f}%, {100 * iv[1]:.1f}%]"


def _pp(x: float) -> str:
    return f"{100 * x:+.1f} pp"


def _group(rep: dict, model: str, split: str, label: str) -> Optional[dict]:
    for g in rep["models"][model]["groups"]:
        if g["split"] == split and g["label"] == label:
            return g
    return None


def flagged(rep: dict, model: str) -> List[Tuple[str, str, str, str, float, int]]:
    """Every reading that is not 'consistent' in a tested group: (split, label, what, reading, size, target days)."""

    out = []
    for g in rep["models"][model]["groups"]:
        if not g["tested"]:
            continue
        for band in BANDS:
            if g[band]["reading"] not in ("consistent", "not tested"):
                out.append((g["split"], g["label"], f"{int(BANDS[band][2] * 100)}% band", g[band]["reading"], g[band]["size"], g["target_days"]))
        for tau, lv in g["levels"].items():
            if lv["reading"] not in ("consistent", "not tested"):
                out.append((g["split"], g["label"], f"q{tau}", lv["reading"], lv["size"], g["target_days"]))
    return out


def readings_made(rep: dict, model: str) -> int:
    return sum((len(BANDS) + len(KEY_LEVELS)) for g in rep["models"][model]["groups"] if g["tested"])


def group_table(rep: dict, models: Sequence[str], split: str, labels: Optional[Sequence[str]] = None) -> List[str]:
    labs = labels or [g["label"] for g in rep["models"][models[0]]["groups"] if g["split"] == split]
    out = ["| group | target days | cells | model | 50% band | 90% band | q05 strict / at-or-below | q95 strict / at-or-below |", "|---|---|---|---|---|---|---|---|"]
    for lab in labs:
        for model in models:
            g = _group(rep, model, split, lab)
            if g is None:
                continue
            q05, q95 = g["levels"]["0.05"], g["levels"]["0.95"]
            out.append(
                f"| {lab} | {g['target_days']} | {g['cells']} | {LABELS[model]} | {_p(g['band50']['closed'])}{_iv(g['band50']['closed_interval'])} {g['band50']['reading']} | "
                f"{_p(g['band90']['closed'])}{_iv(g['band90']['closed_interval'])} {g['band90']['reading']} | "
                f"{_p(q05['strict'])} / {_p(q05['at_or_below'])} {q05['reading']} | {_p(q95['strict'])} / {_p(q95['at_or_below'])} {q95['reading']} |"
            )
    return out


def pit_table(rep: dict, model: str, split: str) -> List[str]:
    out = ["| group | cells | bins (≤0.10, ≤0.25, ≤0.50, ≤0.75, ≤0.90, >0.90) | ≤0.10 (20 other seeds) | ≥0.90 (20 other seeds) |", "|---|---|---|---|---|"]
    for g in rep["models"][model]["groups"]:
        if g["split"] != split:
            continue
        p = g["pit"]
        out.append(f"| {g['label']} | {p['n']} | " + " ".join(f"{100 * b:.1f}" for b in p["bins"]) +
                   f" | {_p(p['at_or_below_0.10'])} ({_p(p['at_or_below_0.10_other_seeds'][0])} to {_p(p['at_or_below_0.10_other_seeds'][1])}) | "
                   f"{_p(p['at_or_above_0.90'])} ({_p(p['at_or_above_0.90_other_seeds'][0])} to {_p(p['at_or_above_0.90_other_seeds'][1])}) |")
    return out


def clustering_table(rep: dict, models: Sequence[str], events: Sequence[str] = ("upper/strict", "lower/strict", "band90/strict", "band50/strict")) -> List[str]:
    out = ["| model | lead | sequence | misses (rate) | P(miss after miss) | P(miss after hit) | longest run | LR p (asymptotic) | p (permutation) | clusters (Holm) |",
           "|---|---|---|---|---|---|---|---|---|---|"]
    for model in models:
        for lead in map(str, LEADS):
            block = rep["models"][model]["clustering"]["all"][lead]
            for ev in events:
                r = block[ev]
                out.append(f"| {LABELS[model]} | {lead} | {ev} | {r['misses']} ({_p(r['rate'])}) | {_p(r['p_miss_after_miss'])} | {_p(r['p_miss_after_hit'])} | "
                           f"{r['longest_run']} | {r['p_asymptotic']:.4f} | {r['p_permutation']:.4f} | {'yes' if r['holm_clusters'] else 'no'} |")
    return out


def clustering_counts(rep: dict) -> List[str]:
    out = ["| model | sequences (all days) | clustered by Holm | sequences inside regimes | clustered by Holm |", "|---|---|---|---|---|"]
    for model in MODELS:
        c = rep["models"][model]["clustering"]
        a = [r for block in c["all"].values() for r in block.values()]
        g = [r for by_lead in c["regime"].values() for block in by_lead.values() for r in block.values()]
        out.append(f"| {LABELS[model]} | {len(a)} | {sum(r['holm_clusters'] for r in a)} | {len(g)} | {sum(r['holm_clusters'] for r in g)} |")
    return out


def answer(r: dict) -> List[str]:
    """The reading in a few lines, every figure taken from the record: pooled coverage, the groups whose bands are read off, the clustering counts."""

    dev, y26 = r["windows"]["development"], r["windows"].get("2026")
    cand = lambda rep, split, label: _group(rep, CANDIDATE, split, label)  # noqa: E731
    pooled, ref = cand(dev, "pooled", "all cells"), _group(dev, "B1_prime", "pooled", "all cells")
    verb = {"consistent": "is consistent with its nominal coverage", "under-covers": "covers less than its nominal share",
            "over-covers": "covers more than its nominal share"}
    out = ["## The answer", "",
           f"Over all cells of the development window the candidate's 90% band {verb.get(pooled['band90']['reading'], pooled['band90']['reading'])} and its 50% band "
           f"{verb.get(pooled['band50']['reading'], pooled['band50']['reading'])}. The groups where a band is off are listed below, largest gap first; the last "
           "paragraph says whether a miss makes another miss more likely.", "",
           f"**Development window, all cells ({pooled['target_days']} target days).** The candidate covers the 50% band {_p(pooled['band50']['closed'])}{_iv(pooled['band50']['closed_interval'])} "
           f"({pooled['band50']['reading']}) and the 90% band {_p(pooled['band90']['closed'])}{_iv(pooled['band90']['closed_interval'])} ({pooled['band90']['reading']}); "
           f"B1' covers the 90% band {_p(ref['band90']['closed'])}{_iv(ref['band90']['closed_interval'])}. "
           f"Its q05 sits above {_p(pooled['levels']['0.05']['strict'])} of outcomes (nominal 5.0%; {pooled['levels']['0.05']['reading']}) and its q95 above "
           f"{_p(pooled['levels']['0.95']['at_or_below'])} (nominal 95.0%; {pooled['levels']['0.95']['reading']})."]
    if y26:
        g = cand(y26, "pooled", "all cells")
        out.append(f"On the 2026 days (shown apart, {g['target_days']} target days) the 50% band covers {_p(g['band50']['closed'])}{_iv(g['band50']['closed_interval'])} "
                   f"({g['band50']['reading']}) and the 90% band {_p(g['band90']['closed'])}{_iv(g['band90']['closed_interval'])} ({g['band90']['reading']}).")
    out += ["", "**Where a band is off on the development window** (candidate; the size in brackets is coverage less nominal; groups of 20 or more target days):", ""]
    for split, title in (("regime", "regimes"), ("target_day_type", "day types"), ("pressure_day_type", "pressure-day types")):
        parts = []
        for g in dev["models"][CANDIDATE]["groups"]:
            if g["split"] != split or not g["tested"]:
                continue
            for band in ("band90", "band50"):
                if g[band]["reading"] in ("under-covers", "over-covers"):
                    parts.append((abs(g[band]["size"]), f"{g['label']} {int(BANDS[band][2] * 100)}% band {_p(g[band]['closed'])} ({_pp(g[band]['size'])}, {g['target_days']} days)"))
        parts.sort(reverse=True)
        out.append(f"- {title}: " + ("; ".join(x for _s, x in parts) if parts else "none"))
    c = dev["models"][CANDIDATE]["clustering"]
    a = [x for block in c["all"].values() for x in block.values()]
    g = [x for by_lead in c["regime"].values() for block in by_lead.values() for x in block.values()]
    out += ["", f"**Do misses follow misses?** Of the {len(a)} hit sequences of the candidate (four events, two tie rules, five leads), {sum(x['holm_clusters'] for x in a)} are read as serially dependent "
            f"(Holm-adjusted permutation p below 0.05); inside regimes {sum(x['holm_clusters'] for x in g)} of {len(g)}. "
            f"After a miss of the 90% band the next day's miss chance at lead 1 is {_p(c['all']['1']['band90/strict']['p_miss_after_miss'])} against "
            f"{_p(c['all']['1']['band90/strict']['p_miss_after_hit'])} after a hit; the longest run of band misses at lead 1 is {c['all']['1']['band90/strict']['longest_run']} days. "
            "Sequences read as dependent among the 40 of each reference: " + ", ".join(
                f"{LABELS[m]} {sum(x['holm_clusters'] for block in dev['models'][m]['clustering']['all'].values() for x in block.values())}" for m in REFERENCES) + ".", ""]
    return out


POOLED_GUIDE = ("The table shows, for the candidate and the three benchmarks over all cells, how often each band held the outcome (with its 90% interval and "
                "reading) and the share of outcomes below q05 and q95.")


def render(r: dict) -> str:
    dev, y26 = r["windows"].get("development"), r["windows"].get("2026")
    lines = [
        "# The candidate's calibration by period and day type, and whether its misses cluster in time",
        "",
        "Terms such as candidate, cell, band, regime and B1' are defined in the [glossary](glossary.md). Issue numbers and files are in the Record at the end.",
        "",
        "## The question",
        "",
        "**Do the candidate's bands hold the share of outcomes they name, in every period and on every type of day, and do its misses come in runs?** "
        "The answer is evidence for the known-limits section of the registration and for the validation report.",
        "",
    ]
    if dev is None:
        return "\n".join(lines + ["The development window's walk is not in this record.", ""])
    lines += answer(r)
    lines += [
        "## Data",
        "",
        "The candidate, (s3c-ann-net), at the 18:00 decision instant, walked unchanged, with B1, B1' and B2 beside it. The answer rests on the development "
        "window (decision days whose five targets are on or before 2025-12-31); the 2026 days (targets 2026-01-02 to 2026-09-03) had already been seen by "
        "earlier studies, are shown at the end and decide nothing.",
        "",
        "## Method",
        "",
        "For every group of days, the study counts how often the outcome fell inside the candidate's 50% and 90% bands and below its q05 and q95, and sets "
        "that against the share each one names. A band or quantile is read as off only when the whole 90% interval of its rate lies on one side of that "
        "share. Each sequence of hits and misses is then tested for runs: if misses were independent, a miss would be no more likely after a miss than "
        "after a hit.",
        "",
        "## Result on the development window",
        "",
        f"{dev['decision_days']} decision days ({dev['first_decision']} to {dev['last_decision']}), {dev['cells']} cells, last target {dev['last_target']}.",
        "",
        POOLED_GUIDE,
        "",
    ] + group_table(dev, MODELS, "pooled") + [""]
    details = [
        "## Details",
        "",
        f"**Intervals.** Intervals are 90% stationary-bootstrap percentile intervals of a rate (mean block {int(r['block'])} target days, {r['reps']} resamples, "
        f"seed {r['seed']}) over the group's target days in date order. This is the current method; it has been questioned and a ruling on it is pending, so "
        "no reading of a day-type group is a finding.",
        "",
        f"**Readings.** Groups of fewer than {MIN_GROUP_DAYS} target days are listed with their rates and not read. A band is read 'under-covers' or "
        "'over-covers' when its interval lies wholly below or above the nominal; a quantile is read 'too high' when the interval of the share of outcomes "
        "strictly below it lies wholly above its level and 'too low' when the interval of the share at or below it lies wholly below. Nothing is corrected "
        "for the number of readings.",
        "",
    ]
    other = ["## Other tables", ""]
    for name, rep in (("Development window", dev), ("The 2026 development days (shown apart; decide nothing)", y26)):
        if rep is None:
            continue
        block = []
        if rep is not dev:
            block += [f"{rep['decision_days']} decision days ({rep['first_decision']} to {rep['last_decision']}), {rep['cells']} cells, last target {rep['last_target']}.", "",
                      "### Pooled", "", POOLED_GUIDE, ""] + group_table(rep, MODELS, "pooled") + [""]
        block += ["### By lead", "", "The candidate alone, one row per lead.", ""] + group_table(rep, [CANDIDATE], "lead") + [""]
        block += ["### By regime of the target day", "", "The same columns for all four models, one block per regime.", ""] + group_table(rep, MODELS, "regime") + [""]
        block += ["### By day type of the target day (the types overlap; ordinary is none of them)", "",
                  "These day types are calendar flags, and one day can carry several, so the rows do not add up to the whole. The candidate is shown beside B1'.", ""] + group_table(rep, [CANDIDATE, "B1_prime"], "target_day_type") + [""]
        block += ["### By pressure-day type of the target day", "", "The same comparison on the pressure-day labels the quarter-end studies use.", ""] + group_table(rep, [CANDIDATE, "B1_prime"], "pressure_day_type") + [""]
        block += ["### Every grid quantile, all cells (candidate)", "",
                  "For a calibrated model each share, read as a fraction, equals the level in the first column.", "", "| level | share strictly below | share at or below |", "|---|---|---|"]
        for tau, v in rep["models"][CANDIDATE]["all_levels"].items():
            block.append(f"| {tau} | {_p(v['strict'], 2)} | {_p(v['at_or_below'], 2)} |")
        block += ["", "### Randomized PIT (seed 1363; the range is over seeds 1364 to 1383)", "",
                  "The PIT is the probability the forecast gave to outcomes at or below the one that happened; for a calibrated model the six bins hold ten, "
                  "fifteen, twenty-five, twenty-five, fifteen and ten percent of the cells.", ""]
        for split in ("pooled", "regime", "target_day_type", "pressure_day_type"):
            block += [f"{split}, candidate:", ""] + pit_table(rep, CANDIDATE, split) + [""]
        block += ["pooled, the references:", ""]
        for model in REFERENCES:
            block += [f"{LABELS[model]}:", ""] + pit_table(rep, model, "pooled") + [""]
        block += ["### Readings that are not 'consistent' (candidate)", "",
                  "The full list behind the summary in the answer, largest first.", ""]
        fl = flagged(rep, CANDIDATE)
        block.append(f"{len(fl)} of {readings_made(rep, CANDIDATE)} readings in tested groups. Sizes are observed less nominal for a band, distance of the level from [strict, at-or-below] for a quantile.")
        block += ["", "| split | group | target days | what | reading | size |", "|---|---|---|---|---|---|"]
        for split, lab, what, reading, size, days in sorted(fl, key=lambda x: -abs(x[4])):
            block.append(f"| {split} | {lab} | {days} | {what} | {reading} | {_pp(size)} |")
        block += ["", "### Do the misses cluster in time?", "",
                  "The first table counts, for each model, how many of its hit sequences are read as serially dependent; the second gives the detail.", "",
                  "Christoffersen's independence test on each lead's sequence over the scored decision days (no transition across a gap or, for the regime rows, a regime change); the permutation p is the reading, "
                  "Holm-adjusted at 0.05 over the 40 sequences of a model and window (per regime for the regime rows).", ""]
        block += clustering_counts(rep) + [""] + clustering_table(rep, [CANDIDATE, "B1_prime", "B2"]) + [""]
        block += ["#### The protocol's own reading (thinned: every h-th decision day at lead h; regime of the decision day), q05 and q95, strict rule", "",
                  "These are the two tests the scoring protocol applies: a Kupiec test of the hit rate and an independence test, each with its p-value.", "",
                  "| model | lead | level | regime | n | hits | Kupiec p | independence p |", "|---|---|---|---|---|---|---|---|"]
        for model in (CANDIDATE, "B1_prime"):
            for c in rep["models"][model]["protocol"]:
                if c["rule"] == "strict":
                    ind = "n/a" if c["independence_p"] is None else f"{c['independence_p']:.3f}"
                    block.append(f"| {LABELS[model]} | {c['lead']} | q{c['level']:g} | {c['regime']} | {c['n']} | {c['hits']} | {c['kupiec_p']:.3f} | {ind} |")
        block.append("")
        other += [f"### {name}", ""] + [("#" + line if line.startswith("###") else line) for line in block]
    lines += ["## What it means, and its limits", "",
              "It shows how the candidate's bands and quantiles hold on seen days, by regime and by day type, and whether its tail and band misses are serially dependent. "
              "It does not show that any group is miscalibrated for the next days, nothing here is a verdict, and a miss rate that moves with the regime would also reject independence: "
              "the regime rows and the day-type tables are there to tell the two apart. B4 is not compared.", ""]
    lines += details + other
    lines += ["## Record", "",
              "- Study: #1363. Hypothesis and step: H5 (primary goal), registration design: step 3 evidence for the known-limits section of the registration and the "
              "validation report.",
              "- Status: **development data, not a verdict** (scoring protocol v1, #640). Nothing is registered or published, no record is edited, and nothing is adopted.",
              "- Generated by `scripts/candidate_calibration_1363.py page` from `docs/research/candidate-calibration-1363/result.json`; declared in "
              "`metadata/candidate_calibration_1363.json` before any figure.",
              f"- Panel digest `{r['panel_sha256']}`.",
              "- Reproduction: each walk's mean grid CRPS (candidate, B1, B1' and B2, all cells) equals the 18:00 record of #1314 "
              "(`docs/research/s3c-ann-net-1800-1314/announced-settlement-1800.json`) to 1e-9, or the script refused to write this record.",
              "- B4 (#1360, a plain quantile regression on reserves and calendar days) is not compared on this page: it was not on main when the study "
              "ran. It has merged since, and its own page compares it with the candidate (`docs/research/b4-quantile-regression-1360-result.md`).",
              "- The 2026 days were already seen by #845, #1229, #1255, #1273, #1288 and #1321.",
              "- The interval method: #1221 questions it and #1228 will decide.", ""]
    return "\n".join(lines)


def page_command(args) -> int:
    r = json.loads(Path(args.score).read_text(encoding="utf-8"))
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    Path(args.output).write_text(render(r), encoding="utf-8")
    return 0


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="command", required=True)
    w = sub.add_parser("walk", help="walk (s3c-ann-net) with B1, B1' and B2 over one window and write its forecasts")
    w.add_argument("--panel", required=True)
    w.add_argument("--window", choices=WINDOWS, required=True)
    w.add_argument("--output", required=True)
    w.add_argument("--first", type=date.fromisoformat, default=None, help="start the walk on this day (the script's test only)")
    w.set_defaults(func=walk_command)
    s = sub.add_parser("score", help="calibration, PIT and clustering from the walk files")
    s.add_argument("--walks", required=True)
    s.add_argument("--output", required=True)
    s.add_argument("--workers", type=int, default=4)
    s.set_defaults(func=score_command)
    g = sub.add_parser("page", help="write the result page from a score file")
    g.add_argument("--score", required=True)
    g.add_argument("--output", required=True)
    g.set_defaults(func=page_command)
    args = parser.parse_args(argv)
    return int(args.func(args) or 0)


if __name__ == "__main__":
    raise SystemExit(main())
