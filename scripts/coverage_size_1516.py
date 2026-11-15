"""The size of the amendment 4 coverage design on the frozen candidate (s3c-ann-net)'s own forecasts, HAC beside (#1516, H5, step M5).

A development study, never a verdict. Her ruling of 8 November 2026 (docket, 4:46 pm ET) on the coverage failure of PR #1513: "measure". The
design is the one `scoring_protocol.coverage_cells` and `enforce_coverage_requirement` apply for amendment 4 of
`docs/decisions/scoring-protocol.md` (#1130): Kupiec and Christoffersen independence at q05/q95 and q01/q99, leads h = 1 to 5, each regime of
the candidate's development window, every h-th decision day at lead h ("thinned"), Holm over the family of 200 tests at 5%. This study asks how
often that design rejects a forecaster that is calibrated by construction but keeps the candidate's own serial structure, and how a Newey-West
(HAC) Kupiec in place of the iid one (`method="hac"` of `coverage_cells`: Kupiec on every day with a Bartlett variance at lag h - 1,
independence still on every h-th day) changes both that size and the verdict on the candidate.

The null worlds (all seeded; a hit rule is the strict one, since no outcome equals the candidate's quantile at any of the four read levels,
which `score` checks):
- `bootstrap` (primary, mean block 10; sensitivity at 5 and 20): the randomised PIT of every (decision day, lead) forecast, ranked to an exact
  uniform margin within each (lead, regime) (a recentring: the candidate's own miscalibration is removed, its dependence is kept), then a
  stationary bootstrap of whole decision days within each regime, the same days at all five leads (so the serial and the cross-lead structure
  of the candidate's PITs is kept, in blocks). Hits are `v > level` above one half and `v < level` below.
- `iid` (control): independent uniform PITs, no serial or cross-lead structure. This is the design's size as #1156 measured it, for these cell
  sizes. Beside it, the rejection of the independence test in `bootstrap` is power, not size: the world keeps the candidate's dependence.

The fast engine below reads hits through the same `coverage_tests` functions and `scoring_protocol._hac_kupiec_p` as `coverage_cells`; the
test module pins its p-values equal to `coverage_cells` (both methods), and `score` checks them equal on the candidate itself.
`COVERAGE_REQUIREMENT_IN_FORCE` is not touched: it is patched on inside one call to read the verdict the way `enforce_coverage_requirement`
would, and is False in the tree. No 2026 day and no locked day is read.

Commands (a clone of the branch; the walk takes about two minutes and the simulation minutes, below the `long-run` line):

    PYTHONPATH=src python3 -m repo_model.cli build --raw-root tests/fixtures/snapshots/funding_inputs --output PUB.csv \\
        --build-cutoff 2026-09-08T21:31:42+00:00 --decision-time 18:00:00
    RMM_DECISION_TIME=18:00 PYTHONPATH=src python3 scripts/candidate_calibration_1363.py walk --panel PUB.csv --window development --output WALK/development.json
    OUT=docs/research/coverage-size-1516
    PYTHONPATH=src python3 scripts/coverage_size_1516.py score --walk WALK/development.json --output $OUT/result.json
    PYTHONPATH=src python3 scripts/coverage_size_1516.py page --score $OUT/result.json --output docs/research/coverage-size-1516-result.md
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import math
import multiprocessing
import random
import sys
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Dict, List, Mapping, Optional, Sequence, Tuple
from unittest import mock

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))

from repo_model import coverage_tests as ct, scoring_protocol as sp  # noqa: E402


def _load(name: str, alias: str):
    spec = importlib.util.spec_from_file_location(alias, REPO / "scripts" / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[alias] = module
    spec.loader.exec_module(module)
    return module


m63 = _load("candidate_calibration_1363", "candidate_calibration_1363_in_1516")

ISSUE = 1516
SEED = 1516
CANDIDATE = m63.CANDIDATE
WINDOW = "development"
LAST_DAY: date = m63.WINDOW_LAST[WINDOW]
ALPHA = 0.05
REPS = 2000
LEVELS = tuple(sp.COVERAGE_LEVELS)
LEADS = tuple(sp.HORIZONS)
RECORD_1314 = m63.RECORD_1314
#: name -> (kind, mean block length); the first is the primary world.
WORLDS: Dict[str, Tuple[str, float]] = {
    "bootstrap_10": ("bootstrap", 10.0),
    "bootstrap_5": ("bootstrap", 5.0),
    "bootstrap_20": ("bootstrap", 20.0),
    "iid": ("iid", 10.0),
}
PRIMARY = "bootstrap_10"
Key = Tuple[int, str, float]


# -- the walk file -------------------------------------------------------------------------------------------------------------


def load_window_doc(doc: Mapping[str, object]) -> "m63.Window":
    """A walk file as `candidate_calibration_1363.Window`, refused unless it is the development window and ends on or before its last day.

    Raises:
        ValueError: the file is another window, or carries no forecasts of the candidate.
        LookAheadError: a decision or target day is after 2025-12-31 or in a locked tier.
    """

    if doc.get("window") != WINDOW:
        raise ValueError(f"this study reads the {WINDOW!r} window only, got {doc.get('window')!r}")
    window = m63.Window(doc)
    m63.refuse_beyond(list(window.days) + [t for _d, _h, t in window.cells], LAST_DAY, where="coverage_size_1516.load_window")
    if CANDIDATE not in window.q:
        raise ValueError(f"the walk file carries no forecasts of {CANDIDATE}")
    return window


# -- PITs and the sample -------------------------------------------------------------------------------------------------------


def randomised_pit(quantiles: Sequence[float], y: float, r: float) -> float:
    """A PIT of `y` under a 23-quantile forecast, uniform within the level bracket of the outcome for `r` uniform in [0, 1).

    The bracket is (largest level whose quantile is below y, or 0; smallest level whose quantile is above y, or 1); the PIT is the upper end
    less `r` of its width. A strict hit above a level (y beyond that quantile) is a PIT above the level, a strict hit below a PIT under it.
    """

    below = max((l for l, q in zip(sp.GRID, quantiles) if q < y), default=0.0)
    above = min((l for l, q in zip(sp.GRID, quantiles) if q > y), default=1.0)
    return above - r * (above - below)


@dataclass
class Sample:
    """The candidate's decision days in order, with the decision-day regime, the order index of each and the PIT at each lead."""

    days: List[date]
    order: List[int]  # index of the day among all decision days (the index `coverage_cells` thins on)
    regimes: List[str]
    u: Dict[int, List[float]]

    def by_regime(self) -> Dict[str, List[int]]:
        out: Dict[str, List[int]] = {}
        for i, r in enumerate(self.regimes):
            out.setdefault(r, []).append(i)
        return out


def sample_from_forecasts(
    forecasts: Mapping[date, Mapping[int, Sequence[float]]], outcomes: Mapping[date, Optional[float]], calendar: Sequence[date],
    regimes: Mapping[date, str], *, seed: int = SEED,
) -> Sample:
    """The sample of `coverage_cells`' own inputs. A decision day with an unpublished target at some lead is refused (the walk has none).

    Raises:
        ValueError: a day lacks an outcome at some lead (the study's null worlds need all five leads on every day).
    """

    position = {d: i for i, d in enumerate(calendar)}
    rng = random.Random(seed)
    days, order, regs = [], [], []
    u: Dict[int, List[float]] = {h: [] for h in LEADS}
    for index, d in enumerate(sorted(forecasts)):
        row = {}
        for h in LEADS:
            y = outcomes.get(calendar[position[d] + h])
            if y is None:
                raise ValueError(f"decision day {d} has no outcome at lead {h}")
            row[h] = randomised_pit(forecasts[d][h], y, rng.random())
        days.append(d)
        order.append(index)
        regs.append(regimes[d])
        for h in LEADS:
            u[h].append(row[h])
    return Sample(days, order, regs, u)


def sample_from_window(window: "m63.Window") -> Sample:
    """The candidate's sample from a development walk."""

    forecasts: Dict[date, Dict[int, List[float]]] = {}
    for (d, h, t), q in zip(window.cells, window.q[CANDIDATE]):
        if window.position[d] + h >= len(window.calendar) or window.calendar[window.position[d] + h] != t:
            raise ValueError(f"cell ({d}, {h}) targets {t}, not the {h}-th scoring-calendar day after {d}")
        forecasts.setdefault(d, {})[h] = list(q)
    return sample_from_forecasts(forecasts, window.outcome, window.calendar, window.regime_of_day)


# -- the worlds ----------------------------------------------------------------------------------------------------------------


def rank_uniform(values: Sequence[float]) -> List[float]:
    """The ranks of `values` scaled to (0, 1): rank / (n + 1), ties by their order. An exact uniform margin that keeps the order."""

    n = len(values)
    out = [0.0] * n
    for rank, i in enumerate(sorted(range(n), key=lambda j: values[j]), start=1):
        out[i] = rank / (n + 1.0)
    return out


def rank_uniform_of(sample: Sample, h: int) -> List[float]:
    """The sample's PITs at lead h, ranked to a uniform margin within each regime."""

    out = [0.0] * len(sample.days)
    for _regime, idx in sample.by_regime().items():
        for i, v in zip(idx, rank_uniform([sample.u[h][i] for i in idx])):
            out[i] = v
    return out


def stationary_indices(n: int, mean_block: float, rng: random.Random) -> List[int]:
    """Politis-Romano stationary bootstrap indices into 0..n-1: a new random start with probability 1/mean_block, else the next day (circular)."""

    switch = 1.0 / mean_block
    out = [rng.randrange(n)]
    for _ in range(n - 1):
        out.append(rng.randrange(n) if rng.random() < switch else (out[-1] + 1) % n)
    return out


def null_world(sample: Sample, kind: str, mean_block: float, rng: random.Random) -> Dict[int, List[float]]:
    """PITs of a forecaster calibrated by construction: `bootstrap` keeps the candidate's dependence, `iid` has none.

    Raises:
        ValueError: an unknown kind.
    """

    n = len(sample.days)
    if kind == "iid":
        return {h: [rng.random() for _ in range(n)] for h in LEADS}
    if kind != "bootstrap":
        raise ValueError(f"unknown world {kind!r}")
    ranked = {h: rank_uniform_of(sample, h) for h in LEADS}
    out = {h: [0.0] * n for h in LEADS}
    for _regime, idx in sample.by_regime().items():
        pick = stationary_indices(len(idx), mean_block, rng)
        for slot, j in zip(idx, pick):
            for h in LEADS:
                out[h][slot] = ranked[h][idx[j]]
    return out


# -- the design ----------------------------------------------------------------------------------------------------------------


def _hits(v: Sequence[float], level: float) -> List[int]:
    return [int(x > level) for x in v] if level > 0.5 else [int(x < level) for x in v]


def cell_keys(sample: Sample) -> List[Key]:
    """Every (lead, regime, level) cell of the design, in the order `coverage_cells` makes them (lead, regime, level)."""

    regimes = sorted(set(sample.regimes))
    return [(h, r, level) for h in LEADS for r in regimes for level in LEVELS]


def thinned_hit_counts(sample: Sample, v: Mapping[int, Sequence[float]]) -> Dict[Key, int]:
    """Hits in the thinned sample of each cell."""

    out: Dict[Key, int] = {}
    for h in LEADS:
        for regime, idx in sorted(sample.by_regime().items()):
            kept = [i for i in idx if sample.order[i] % h == 0]
            for level in LEVELS:
                out[(h, regime, level)] = sum(_hits([v[h][i] for i in kept], level))
    return out


def cell_p_values(sample: Sample, v: Mapping[int, Sequence[float]]) -> Dict[Key, Tuple[float, float, Optional[float]]]:
    """Per cell: Kupiec p on the thinned days (iid), Kupiec p on every day with a Bartlett variance at lag h - 1 (HAC), independence p.

    The independence test reads the thinned days under both (as `coverage_cells` does); it is None for fewer than two thinned days.
    """

    out: Dict[Key, Tuple[float, float, Optional[float]]] = {}
    for h in LEADS:
        for regime, idx in sorted(sample.by_regime().items()):
            kept = [i for i in idx if sample.order[i] % h == 0]
            for level in LEVELS:
                p = min(level, 1.0 - level)
                thinned = _hits([v[h][i] for i in kept], level)
                full = _hits([v[h][i] for i in idx], level)
                kup_iid = ct.kupiec(thinned, p).p_value if thinned else 1.0
                kup_hac = sp._hac_kupiec_p(full, p, h - 1) if full else 1.0
                ind = ct.christoffersen_independence(thinned).p_value if len(thinned) >= 2 else None
                out[(h, regime, level)] = (kup_iid, kup_hac, ind)
    return out


def holm_rejected(ps: Sequence[float], alpha: float = ALPHA) -> List[int]:
    """Indices rejected by Holm's step-down at family level `alpha` (as `scoring_protocol.holm`)."""

    ordered = sorted(range(len(ps)), key=lambda i: ps[i])
    out: List[int] = []
    for rank, i in enumerate(ordered):
        if ps[i] > alpha / (len(ordered) - rank):
            break
        out.append(i)
    return out


def holm_rejections(ps: Sequence[float], alpha: float = ALPHA) -> int:
    """The number of hypotheses Holm rejects."""

    return len(holm_rejected(ps, alpha))


def families(table: Mapping[Key, Tuple[float, float, Optional[float]]], keys: Sequence[Key]) -> Dict[str, Tuple[List[float], List[Tuple[Key, str]]]]:
    """The two families of tests: `iid` (Kupiec thinned + independence) and `hac` (Kupiec HAC + independence), with each test's (cell, kind)."""

    out: Dict[str, Tuple[List[float], List[Tuple[Key, str]]]] = {}
    for name, col in (("iid", 0), ("hac", 1)):
        ps: List[float] = []
        who: List[Tuple[Key, str]] = []
        for k in keys:
            row = table[k]
            ps.append(row[col])
            who.append((k, "kupiec"))
            if row[2] is not None:
                ps.append(row[2])
                who.append((k, "independence"))
        out[name] = (ps, who)
    return out


# -- the simulation ------------------------------------------------------------------------------------------------------------

_STATE: dict = {}


def _rep(job):
    """One null draw: the family-wise outcome of both families and the per-test rejections. `job` = (world, rep)."""

    world, rep = job
    sample, keys = _STATE["sample"], _STATE["keys"]
    kind, block = WORLDS[world]
    rng = random.Random(_STATE["seed"] * 1_000_003 + rep * 31 + sum(map(ord, world)))
    table = cell_p_values(sample, null_world(sample, kind, block, rng))
    out = {}
    for name, (ps, who) in families(table, keys).items():
        rej = holm_rejected(ps)
        out[name] = {
            "min_p": min(ps),
            "rejected": len(rej),
            "kinds": sorted({who[i][1] for i in rej}),
            "raw": [(who[i][0], who[i][1]) for i in range(len(ps)) if ps[i] < ALPHA],
            "holm": [(who[i][0], who[i][1]) for i in rej],
        }
    return out


def wilson(hits: int, n: int, z: float = 1.959964) -> List[float]:
    """The Wilson score 95% interval of a rate."""

    p = hits / n
    centre = (p + z * z / (2 * n)) / (1 + z * z / n)
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / (1 + z * z / n)
    return [max(0.0, centre - half), min(1.0, centre + half)]


def observed_report(sample: Sample, keys: Sequence[Key]) -> dict:
    """The candidate's own p-values per cell and the Holm verdict of each family."""

    table = cell_p_values(sample, sample.u)
    hits = thinned_hit_counts(sample, sample.u)
    fam = families(table, keys)
    out = {"cells": [], "families": {}}
    for k in keys:
        iid, hac, ind = table[k]
        kept = sum(1 for i, r in enumerate(sample.regimes) if r == k[1] and sample.order[i] % k[0] == 0)
        out["cells"].append({
            "lead": k[0], "regime": k[1], "level": k[2], "nominal": min(k[2], 1.0 - k[2]), "n_thinned": kept, "hits_thinned": hits[k],
            "kupiec_iid_p": iid, "kupiec_hac_p": hac, "independence_p": ind,
        })
    for name, (ps, who) in fam.items():
        rej = holm_rejected(ps)
        out["families"][name] = {
            "tests": len(ps), "rejected": len(rej), "passes": not rej, "min_p": min(ps),
            "failing": sorted(f"lead {who[i][0][0]}, {who[i][0][1]}, q{who[i][0][2]:g} / {who[i][1]}" for i in rej),
        }
    return out


def simulate(sample: Sample, keys: Sequence[Key], world: str, reps: int, workers: int, seed: int, observed_min: Mapping[str, float]) -> dict:
    """Family-wise size of both families in one world, per-test sizes, and the Monte Carlo family p-value of the candidate's smallest p."""

    _STATE.update(sample=sample, keys=keys, seed=seed)
    jobs = [(world, r) for r in range(reps)]
    if workers > 1:
        with multiprocessing.get_context("fork").Pool(workers) as pool:
            results = pool.map(_rep, jobs, chunksize=max(1, reps // (workers * 8)))
    else:
        results = [_rep(j) for j in jobs]
    out: dict = {"world": world, "kind": WORLDS[world][0], "mean_block": WORLDS[world][1], "reps": reps, "families": {}, "cells": []}
    raw: Dict[Tuple[str, Key, str], int] = {}
    holm: Dict[Tuple[str, Key, str], int] = {}
    for name in ("iid", "hac"):
        rs = [r[name] for r in results]
        fw = sum(1 for r in rs if r["rejected"] > 0)
        mc = sum(1 for r in rs if r["min_p"] <= observed_min[name])
        out["families"][name] = {
            "fwer": fw / reps, "fwer_interval": wilson(fw, reps), "mean_rejected": sum(r["rejected"] for r in rs) / reps,
            "any_kupiec": sum(1 for r in rs if "kupiec" in r["kinds"]) / reps,
            "any_independence": sum(1 for r in rs if "independence" in r["kinds"]) / reps,
            "median_min_p": sorted(r["min_p"] for r in rs)[reps // 2],
            "mc_p_of_candidate_min_p": (1 + mc) / (1 + reps),
        }
        for r in rs:
            for cell, kind in r["raw"]:
                raw[(name, cell, kind)] = raw.get((name, cell, kind), 0) + 1
            for cell, kind in r["holm"]:
                holm[(name, cell, kind)] = holm.get((name, cell, kind), 0) + 1
    for k in keys:
        out["cells"].append({
            "lead": k[0], "regime": k[1], "level": k[2],
            "raw_size": {"kupiec_iid": raw.get(("iid", k, "kupiec"), 0) / reps, "kupiec_hac": raw.get(("hac", k, "kupiec"), 0) / reps,
                         "independence": raw.get(("iid", k, "independence"), 0) / reps},
            "holm_size": {"kupiec_iid": holm.get(("iid", k, "kupiec"), 0) / reps, "kupiec_hac": holm.get(("hac", k, "kupiec"), 0) / reps,
                          "independence": holm.get(("iid", k, "independence"), 0) / reps},
        })
    return out


# -- commands ------------------------------------------------------------------------------------------------------------------


def candidate_checks(window: "m63.Window", sample: Sample, keys: Sequence[Key]) -> dict:
    """The engine against `coverage_cells` and `enforce_coverage_requirement` on the candidate itself; ties at the four read levels."""

    forecasts: Dict[date, Dict[int, List[float]]] = {}
    for (d, h, _t), q in zip(window.cells, window.q[CANDIDATE]):
        forecasts.setdefault(d, {})[h] = list(q)
    table = cell_p_values(sample, sample.u)
    verdicts = {}
    for method, col in (("thinned", 0), ("hac", 1)):
        cells = sp.coverage_cells(forecasts, window.outcome, window.calendar, window.regime_of_day, method=method)
        strict = {(c.lead, c.regime, c.level): c for c in cells if c.rule == "strict"}
        if set(strict) != set(keys):
            raise ValueError(f"the engine's cells differ from coverage_cells' ({method})")
        for k, c in strict.items():
            same = abs(c.kupiec_p - table[k][col]) < 1e-12 and (
                (c.independence_p is None and table[k][2] is None) or abs(c.independence_p - table[k][2]) < 1e-12
            )
            if not same:
                raise ValueError(f"engine and coverage_cells disagree at {k} ({method})")
        with mock.patch.object(sp, "COVERAGE_REQUIREMENT_IN_FORCE", True):
            try:
                sp.enforce_coverage_requirement(cells, alpha=ALPHA, family="holm", rule="strict")
                passes = True
            except sp.CoverageRequirementFailed:
                passes = False
        verdicts["iid" if method == "thinned" else "hac"] = passes
    mine = observed_report(sample, keys)["families"]
    for name in ("iid", "hac"):
        if mine[name]["passes"] != verdicts[name]:
            raise ValueError(f"the {name} family verdict differs from enforce_coverage_requirement")
    ties = {f"{lv:g}": sum(1 for q, y in zip(window.q[CANDIDATE], window.y) if q[sp.GRID.index(lv)] == y) for lv in LEVELS}
    if any(ties.values()):
        raise ValueError(f"outcomes equal the candidate's quantile at a read level ({ties}): the strict rule is not the only rule")
    return {"enforce_agrees": True, "enforce_passes": verdicts, "ties_by_level": ties}


def score_command(args) -> int:
    doc = json.loads(Path(args.walk).read_text(encoding="utf-8"))
    window = load_window_doc(doc)
    record = json.loads(RECORD_1314.read_text(encoding="utf-8"))
    reproduction = m63.reproduction_check(window, record)
    sample = sample_from_window(window)
    keys = cell_keys(sample)
    checks = candidate_checks(window, sample, keys)
    observed = observed_report(sample, keys)
    observed_min = {name: observed["families"][name]["min_p"] for name in ("iid", "hac")}
    worlds = {}
    for name in WORLDS:
        worlds[name] = simulate(sample, keys, name, args.reps, args.workers, SEED, observed_min)
        print(f"{name}: iid fwer {worlds[name]['families']['iid']['fwer']:.3f}, hac fwer {worlds[name]['families']['hac']['fwer']:.3f}", flush=True)
    regimes = sorted(set(sample.regimes))
    result = {
        "issue": ISSUE, "label": "development, not a verdict", "candidate": CANDIDATE, "panel_sha256": doc.get("panel_sha256"),
        "window": WINDOW, "decision_days": len(sample.days), "last_target": window.last_day().isoformat(), "alpha": ALPHA, "seed": SEED,
        "reps": args.reps, "design": {"method": "thinned", "family": "holm", "levels": list(LEVELS), "leads": list(LEADS), "rule": "strict"},
        "regimes": regimes, "regime_days": {r: sum(1 for x in sample.regimes if x == r) for r in regimes}, "primary": PRIMARY,
        "worlds_declared": {k: {"kind": v[0], "mean_block": v[1]} for k, v in WORLDS.items()},
        "reproduction": {"against": str(RECORD_1314.relative_to(REPO)), "mean_grid_crps": reproduction[CANDIDATE]},
        "checks": checks, "coverage_requirement_in_force": sp.COVERAGE_REQUIREMENT_IN_FORCE,
        "observed": observed, "worlds": worlds,
    }
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    print(f"wrote {out}")
    return 0


def walk_command(args) -> int:
    """The development walk of `candidate_calibration_1363.py walk`, unchanged."""

    ns = argparse.Namespace(panel=args.panel, window=WINDOW, output=args.output, first=None)
    return m63.walk_command(ns)


# -- the page ------------------------------------------------------------------------------------------------------------------


def _p(x: Optional[float]) -> str:
    return "n/a" if x is None else ("<0.001" if x < 0.001 else f"{x:.3f}")


def _pc(x: float) -> str:
    return f"{100 * x:.1f}%"


def _iv(x: List[float]) -> str:
    return f"[{100 * x[0]:.1f}%, {100 * x[1]:.1f}%]"


def render(r: Mapping[str, object]) -> str:
    L: List[str] = []
    a = L.append
    worlds, obs = r["worlds"], r["observed"]
    prim = worlds[r["primary"]]
    a("# Size of the amendment 4 coverage design on (s3c-ann-net)'s own forecasts, HAC beside (#1516)")
    a("")
    a("**Hypothesis and step:** H5, step M5 (registration). **Development data, not a verdict.** Generated by `scripts/coverage_size_1516.py page` "
      "from `docs/research/coverage-size-1516/result.json`, not edited by hand. It answers her ruling of 8 November 2026 on the coverage failure "
      "of PR #1513 (\"measure\"): registration of #1510 waits on it, and the rule registration applies is hers.")
    a("")
    a("**What was measured.** The design amendment 4 sets (Kupiec and Christoffersen independence at q05/q95 and q01/q99, leads 1 to 5, each regime, "
      "every h-th decision day at lead h, Holm over the family at "
      f"{_pc(r['alpha'])}) was run on {r['reps']} null draws per world. A null draw is a forecaster calibrated by construction, in every (lead, regime) "
      f"cell of the candidate's {r['decision_days']} development decision days (targets to {r['last_target']}). In the `bootstrap` worlds it keeps the "
      "candidate's own serial and cross-lead structure: its randomised PITs are ranked to an exact uniform margin within each lead and regime "
      "(so its own miscalibration is removed) and whole decision days are resampled by a stationary bootstrap within each regime, the same days at all five "
      "leads. In the `iid` control the PITs are independent uniforms. Beside the iid Kupiec, the HAC family replaces it by a Kupiec with a Bartlett "
      "(Newey-West) variance at lag h - 1 on every day (`method=\"hac\"` of `coverage_cells`); the independence test is the same in both. "
      f"Seed {r['seed']}. The strict hit rule is the only rule here: no outcome equals the candidate's quantile at a read level "
      f"(ties by level: {', '.join(f'q{k} {v}' for k, v in r['checks']['ties_by_level'].items())}), so the three rules of #1513 coincide.")
    a("")
    a("The engine's p-values equal `scoring_protocol.coverage_cells`' on the candidate itself under both methods, and the two verdicts equal "
      "`enforce_coverage_requirement(..., family=\"holm\", alpha=0.05, rule=\"strict\")` (flag patched on inside one call; it is False in the tree). "
      "The walk reproduces the 1314 record's mean grid CRPS to 1e-9.")
    a("")
    a("## Family-wise size: how often the design rejects a calibrated forecaster")
    a("")
    a(f"Share of null draws with at least one Holm rejection across the family of {obs['families']['iid']['tests']} cells (nominal {_pc(r['alpha'])}), with a Wilson 95% interval. "
      "In the `bootstrap` worlds the independence test is not at its size: the world keeps the candidate's dependence, so its rejections there are power "
      "against that dependence. The `iid` row is the design's size.")
    a("")
    a("| World | Variance | family-wise rejection | of which a Kupiec test | of which an independence test | mean tests rejected |")
    a("|---|---|---|---|---|---|")
    for name, w in worlds.items():
        label = f"`{name}` ({'primary' if name == r['primary'] else 'sensitivity' if w['kind'] == 'bootstrap' else 'control'})"
        for fam, text in (("iid", "iid Kupiec (amendment 4)"), ("hac", "HAC Kupiec")):
            f = w["families"][fam]
            a(f"| {label} | {text} | {_pc(f['fwer'])} {_iv(f['fwer_interval'])} | {_pc(f['any_kupiec'])} | {_pc(f['any_independence'])} | {f['mean_rejected']:.3f} |")
    a("")
    a("## The candidate under each reading")
    a("")
    a("| Reading | passes | tests | rejected by Holm (5%) | smallest raw p | Monte Carlo p of that smallest p, `" + r["primary"] + "` | `iid` control |")
    a("|---|---|---|---|---|---|---|")
    for fam, text in (("iid", "iid Kupiec (amendment 4 as set)"), ("hac", "HAC Kupiec")):
        o = obs["families"][fam]
        a(f"| {text} | **{'pass' if o['passes'] else 'FAIL'}** | {o['tests']} | {o['rejected']} | {_p(o['min_p'])} | "
          f"{_p(prim['families'][fam]['mc_p_of_candidate_min_p'])} | {_p(worlds['iid']['families'][fam]['mc_p_of_candidate_min_p'])} |")
    a("")
    a("The Monte Carlo p is the share of null draws whose smallest raw p-value in the family is at most the candidate's own: how often a calibrated "
      "forecaster with the candidate's dependence (or none) looks at least as bad as the candidate on the family's most extreme test.")
    a("")
    for fam, text in (("iid", "iid Kupiec"), ("hac", "HAC Kupiec")):
        o = obs["families"][fam]
        if o["failing"]:
            a(f"Rejected under the {text} family ({o['rejected']}): " + "; ".join(f"`{t}`" for t in o["failing"]) + ".")
            a("")
    a("## Per cell: size under each variance and the candidate's p-value")
    a("")
    a(f"World `{r['primary']}`. Raw size is the share of null draws with the test's raw p below {_pc(r['alpha'])} (the test's nominal level); Holm size is the share in which "
      "Holm over the whole family rejects that test. `n` and `hits` are the candidate's thinned sample (the hit rate nominal is the cell's tail level). "
      "Kupiec p is under the iid variance and under HAC; the independence p is the same under both.")
    a("")
    a("| Lead | Regime | Level | n | hits | nominal hit rate | raw size Kupiec iid | raw size Kupiec HAC | raw size indep. | Holm size Kupiec iid | Holm size Kupiec HAC | Holm size indep. | Kupiec p iid | Kupiec p HAC | indep. p |")
    a("|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|")
    for c, w in zip(obs["cells"], prim["cells"]):
        rs, hs = w["raw_size"], w["holm_size"]
        a(f"| {c['lead']} | {c['regime']} | q{c['level']:g} | {c['n_thinned']} | {c['hits_thinned']} | {_pc(c['nominal'])} | {_pc(rs['kupiec_iid'])} | {_pc(rs['kupiec_hac'])} | "
          f"{_pc(rs['independence'])} | {_pc(hs['kupiec_iid'])} | {_pc(hs['kupiec_hac'])} | {_pc(hs['independence'])} | "
          f"{_p(c['kupiec_iid_p'])} | {_p(c['kupiec_hac_p'])} | {_p(c['independence_p'])} |")
    a("")
    a("## What this shows and does not show")
    a("")
    a("- It shows how often this design, as `coverage_cells` and `enforce_coverage_requirement` apply it, rejects a forecaster that is calibrated by "
      "construction in every cell, when that forecaster has the candidate's own dependence from day to day and across leads, and with none; and how "
      "the candidate reads under an iid or a HAC Kupiec. It is development evidence on seen days and no verdict.")
    a("- The world is a resample of the candidate's own PIT ranks. It keeps dependence in blocks of the stated mean length (5, 10 and 20 days), "
      "not any longer-range structure, and it assumes the candidate's dependence is the same under the null as in the data; where the dependence "
      "is the candidate's miscalibration (volatility clustering the forecast fails to follow), a world that keeps it is a world in which the "
      "independence test has power, not size.")
    a("- The hit rule is the strict one: with no ties at the four read levels the deterministic and the randomised tie rules coincide here, "
      "and the size of the randomised rule on a whole-basis-point world is #1156's, not repeated.")
    a("- Why the HAC family over-rejects a calibrated forecaster in the `iid` control: the Bartlett variance is centred at the nominal hit rate, "
      "not at the sample rate, so a cell with no hit at q01 or q99 gets a variance of about p squared and a Kupiec p-value far below any Holm threshold "
      "(pinned in `tests/test_coverage_size_1516.py`, `HacZeroHitTests`). With cells this thin, one zero-hit cell fails the family.")
    a("- A HAC variance changes the Kupiec test only; the independence test and the thinning are the same in both families. It is not tuned: lag h - 1, "
      "as `coverage_cells` sets it.")
    a("- The 2026 days (near-blind tier), B1, B1', B2 and B4, and the uncapped secondary version are not read. Nothing here changes amendment 4, "
      "`COVERAGE_REQUIREMENT_IN_FORCE` or any threshold.")
    a("")
    a(f"Panel sha256 `{r['panel_sha256']}`. Variants run: {len(r['worlds_declared'])} null worlds (one primary, two block-length sensitivities, one control) "
      "and two variances, none tuned on the candidate's verdict.")
    a("")
    return "\n".join(L)


def page_command(args) -> int:
    r = json.loads(Path(args.score).read_text(encoding="utf-8"))
    Path(args.output).write_text(render(r), encoding="utf-8")
    print(f"wrote {args.output}")
    return 0


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="command", required=True)
    w = sub.add_parser("walk")
    w.add_argument("--panel", required=True)
    w.add_argument("--output", required=True)
    w.set_defaults(func=walk_command)
    s = sub.add_parser("score")
    s.add_argument("--walk", required=True)
    s.add_argument("--output", required=True)
    s.add_argument("--reps", type=int, default=REPS)
    s.add_argument("--workers", type=int, default=4)
    s.set_defaults(func=score_command)
    g = sub.add_parser("page")
    g.add_argument("--score", required=True)
    g.add_argument("--output", required=True)
    g.set_defaults(func=page_command)
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
