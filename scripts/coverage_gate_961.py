#!/usr/bin/env python3
"""H1 and H5 step 5 (#961): a coverage gate, shown on a simulated world with known dynamics.

The protocol selects by grid CRPS alone. CRPS rewards sharpness, so a narrower, mis-calibrated forecast can outscore a
calibrated one that knows less. This builds a two-regime AR(1) world (`metadata/coverage_gate_961.json`, which `run`
refuses to read unless committed and unchanged), ranks a field of synthetic forecasters by the current rule, applies the
declared gate (Kupiec at q05 and q95, Christoffersen independence at q95, the 98% band; by lead and regime) and measures
how often the gate fails a forecaster that is calibrated by construction. The statistics are `repo_model.coverage_tests`.

Development data in the weakest sense (a simulation), no verdict, nothing in force moves. Standard library only.

    PYTHONPATH=src python3 scripts/coverage_gate_961.py run --output OUT/result.json
    python3 scripts/coverage_gate_961.py report OUT/result.json
    python3 scripts/coverage_gate_961.py check
"""

import argparse
import json
import math
import random
import subprocess
import sys
from datetime import date, timedelta
from pathlib import Path
from statistics import NormalDist

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))

from repo_model import scoring_protocol as sp  # noqa: E402
from repo_model.coverage_tests import (  # noqa: E402
    christoffersen_independence,
    hit_sequence,
    kupiec,
)

RESEARCH = REPO / "docs" / "research"
DECLARATION = REPO / "metadata" / "coverage_gate_961.json"
RECORD = RESEARCH / "coverage-gate-961" / "result.json"
PAGE = RESEARCH / "coverage-gate-961-result.md"

PHI = 0.9
SIGMA_CALM = 1.0
SIGMA_STRESS = 2.5
BLOCK = 250
SIGMA_POOLED = math.sqrt((SIGMA_CALM**2 + SIGMA_STRESS**2) / 2.0)
VAR_POOLED = SIGMA_POOLED**2 / (1.0 - PHI**2)
HORIZONS = sp.HORIZONS
START = date(2001, 1, 2)
SEED = 961
DEMO_DAYS = 5000
DEMO_DRAWS = 2000
SIZE_PATHS = 300
SIZE_DAYS = 2000
ALPHA_GATE = 0.01
BAND_LOW, BAND_HIGH = 0.95, 0.995
NOMINAL = 0.05
NORMAL = NormalDist()
Z = {level: NORMAL.inv_cdf(level) for level in sp.GRID}
REGIMES = ("calm", "stress")


# ---------------------------------------------------------------- the world

def sigma_schedule(days):
    """Innovation sd on each day: calm and stress blocks of `BLOCK` days, calm first."""

    return [SIGMA_CALM if (t // BLOCK) % 2 == 0 else SIGMA_STRESS for t in range(days)]


def regime_of(sigma):
    return "stress" if sigma == SIGMA_STRESS else "calm"


def simulate(days, seed):
    """`days` + max(HORIZONS) values of y; y[t] = PHI y[t-1] + sigma[t] e[t]."""

    total = days + max(HORIZONS)
    sigma = sigma_schedule(total)
    rng = random.Random(seed)
    y = [rng.gauss(0.0, SIGMA_CALM / math.sqrt(1.0 - PHI**2))]
    for t in range(1, total):
        y.append(PHI * y[-1] + sigma[t] * rng.gauss(0.0, 1.0))
    return y


# ------------------------------------------------------------ the forecasters
# Each maps (y[t], t, h, sigma) to (mean, sd) of a Gaussian; the 23 quantiles are mean + sd * z.

def _ahead_sd(t, h, sigma):
    return math.sqrt(sum(PHI ** (2 * (h - j)) * sigma[t + j] ** 2 for j in range(1, h + 1)))


def ideal(y, t, h, sigma):
    return PHI**h * y, _ahead_sd(t, h, sigma)


def pooled(y, t, h, sigma):
    var = SIGMA_POOLED**2 * (1.0 - PHI ** (2 * h)) / (1.0 - PHI**2)
    return PHI**h * y, math.sqrt(var)


def persistence(y, t, h, sigma):
    return y, math.sqrt(2.0 * (1.0 - PHI**h) * VAR_POOLED)


def climatology(y, t, h, sigma):
    return 0.0, math.sqrt(VAR_POOLED)


def dispersed(c):
    def forecast(y, t, h, sigma):
        mean, sd = ideal(y, t, h, sigma)
        return mean, c * sd

    return forecast


FORECASTERS = {
    "ideal": ideal,
    "pooled": pooled,
    "persistence": persistence,
    "climatology": climatology,
    "under_0.5": dispersed(0.5),
    "under_0.75": dispersed(0.75),
    "over_1.5": dispersed(1.5),
}


def quantiles(mean, sd):
    return [mean + sd * Z[level] for level in sp.GRID]


# ------------------------------------------------------------------ the gate

def thin(hits, lead):
    """Every `lead`-th decision day: consecutive h-step errors overlap, so independence is read on a thinned series."""

    return list(hits[::lead])


def gate_cell(q05_miss, q95_miss, band_miss, lead, thin_kupiec=False):
    """The gate on one (lead, regime) cell. Inputs are 0/1 miss sequences in date order for q05, q95 and the 98% band.

    `thin_kupiec` is the post-hoc variant (not declared): Kupiec on every `lead`-th day too, because Kupiec assumes
    independent hits and the hits of h-step forecasts made on consecutive days are not.
    """

    k05 = kupiec(thin(q05_miss, lead) if thin_kupiec else q05_miss, NOMINAL)
    k95 = kupiec(thin(q95_miss, lead) if thin_kupiec else q95_miss, NOMINAL)
    thinned = thin(q95_miss, lead)
    ind = christoffersen_independence(thinned)
    coverage = 1.0 - sum(band_miss) / len(band_miss)
    tests = {
        "kupiec_q05": {"p": k05.p_value, "rate": k05.hits / k05.n, "pass": k05.p_value >= ALPHA_GATE},
        "kupiec_q95": {"p": k95.p_value, "rate": k95.hits / k95.n, "pass": k95.p_value >= ALPHA_GATE},
        "independence_q95": {"p": ind.p_value, "n": ind.n, "pass": ind.p_value >= ALPHA_GATE},
        "band_98": {"coverage": coverage, "pass": BAND_LOW <= coverage <= BAND_HIGH},
    }
    return {"n": len(q05_miss), "tests": tests, "pass": all(t["pass"] for t in tests.values())}


def overall_pass(cells):
    """Every (regime, lead) cell must pass; a pooled pass never substitutes for a failing regime."""

    return all(cell["pass"] for cell in cells.values())


def misses(outcomes, mean_sd):
    """0/1 misses at q05 (y < q05), q95 (y > q95) and the 98% band (outside [q01, q99]) for one lead."""

    q = {level: [m + s * Z[level] for m, s in mean_sd] for level in (0.01, 0.05, 0.95, 0.99)}
    q05 = [1 - h for h in hit_sequence(outcomes, q[0.05], rule="at_or_above")]
    q95 = hit_sequence(outcomes, q[0.95], rule="above")
    low = [1 - h for h in hit_sequence(outcomes, q[0.01], rule="at_or_above")]
    high = hit_sequence(outcomes, q[0.99], rule="above")
    return q05, q95, [a | b for a, b in zip(low, high)]


def gate_forecaster(name, y, days, thin_kupiec=False):
    sigma = sigma_schedule(len(y))
    forecast = FORECASTERS[name]
    cells, pooled_cells = {}, {}
    for h in HORIZONS:
        mean_sd = [forecast(y[t], t, h, sigma) for t in range(days)]
        outcomes = [y[t + h] for t in range(days)]
        q05, q95, band = misses(outcomes, mean_sd)
        # the cell is the decision days whose target falls in the regime, in date order (independence thins it per lead)
        regime = [regime_of(sigma[t + h]) for t in range(days)]
        for r in REGIMES:
            idx = [t for t in range(days) if regime[t] == r]
            cells[(r, h)] = gate_cell([q05[t] for t in idx], [q95[t] for t in idx], [band[t] for t in idx], h,
                                      thin_kupiec)
        pooled_cells[h] = gate_cell(q05, q95, band, h, thin_kupiec)
    return cells, pooled_cells


def mean_crps(name, y, days):
    sigma = sigma_schedule(len(y))
    forecast = FORECASTERS[name]
    daily = {}
    for t in range(days):
        total = 0.0
        for h in HORIZONS:
            mean, sd = forecast(y[t], t, h, sigma)
            total += sp.grid_crps(quantiles(mean, sd), y[t + h])
        daily[START + timedelta(days=t)] = total / len(HORIZONS)
    return daily


def demonstrate(days=DEMO_DAYS, seed=SEED, draws=DEMO_DRAWS):
    y = simulate(days, seed)
    daily = {name: mean_crps(name, y, days) for name in FORECASTERS}
    crps = {name: sum(d.values()) / len(d) for name, d in daily.items()}
    gate = {}
    for name in FORECASTERS:
        cells, pooled_cells = gate_forecaster(name, y, days)
        gate[name] = {
            "pass": overall_pass(cells),
            "pooled_pass": overall_pass(pooled_cells),
            "failing_cells": sorted("%s/lead %d" % (r, h) for (r, h), c in cells.items() if not c["pass"]),
            "cells": {"%s/%d" % (r, h): c for (r, h), c in sorted(cells.items())},
            "pooled_cells": {str(h): c for h, c in sorted(pooled_cells.items())},
        }
    for name in FORECASTERS:
        cells, _ = gate_forecaster(name, y, days, thin_kupiec=True)
        gate[name]["post_hoc_thinned_kupiec"] = {
            "pass": overall_pass(cells),
            "failing_cells": sorted("%s/lead %d" % (r, h) for (r, h), c in cells.items() if not c["pass"]),
        }
    paired = {}
    for benchmark in ("persistence", "climatology", "pooled"):
        test = sp.paired_test(daily[benchmark], daily["under_0.5"], seed=seed, draws=draws, with_skill=False)
        paired[benchmark] = {"mean_difference": test.mean_difference, "lower_95": test.lower_mean_difference()}
    return {"days": days, "seed": seed, "mean_crps": crps, "gate": gate, "paired_under_0.5": paired}


def size_study(paths=SIZE_PATHS, days=SIZE_DAYS):
    """How often the gate fails the ideal forecaster, which is calibrated by construction (declared and post-hoc gate)."""

    out = {"paths": paths, "days": days, "cells_per_path": len(REGIMES) * len(HORIZONS), "tests_per_cell": 4}
    for label, thin_kupiec in (("declared", False), ("post_hoc_thinned_kupiec", True)):
        failed = 0
        by_test = {"kupiec_q05": 0, "kupiec_q95": 0, "independence_q95": 0, "band_98": 0}
        by_lead = {h: 0 for h in HORIZONS}
        for p in range(paths):
            y = simulate(days, SEED + 1 + p)
            cells, _ = gate_forecaster("ideal", y, days, thin_kupiec)
            failed += not overall_pass(cells)
            for test in by_test:
                by_test[test] += any(not c["tests"][test]["pass"] for c in cells.values())
            for h in HORIZONS:
                by_lead[h] += any(not cells[(r, h)]["pass"] for r in REGIMES)
        out[label] = {"fail_share": failed / paths,
                      "fail_share_by_test": {k: v / paths for k, v in by_test.items()},
                      "fail_share_by_lead": {str(h): v / paths for h, v in by_lead.items()}}
    return out


# --------------------------------------------------------------- the commands

def declaration_text():
    relative = str(DECLARATION.relative_to(REPO))
    dirty = subprocess.run(["git", "status", "--porcelain", "--", relative], cwd=REPO, capture_output=True, text=True)
    if dirty.stdout.strip():
        raise ValueError(f"{relative} is not committed and unchanged")
    return DECLARATION.read_text(encoding="utf-8")


def run_command(args):
    declaration_text()
    record = {"declaration": json.loads(DECLARATION.read_text(encoding="utf-8"))["issue"],
              "demonstration": demonstrate(), "size": size_study()}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(record, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    print("wrote", args.output)
    return 0


def pct(v):
    return "%.1f%%" % (100 * v)


def render(record):
    d, s = record["demonstration"], record["size"]
    crps = d["mean_crps"]
    order = sorted(crps, key=crps.get)
    L = ["# A coverage gate on a simulated world (#961)", "",
         "**Development data, not a verdict.** A simulation with known dynamics; nothing here is registered, published or in force, "
         "and the protocol's text and constants are only read. Hypothesis and step: H1 (the synthetic suite) and H5 step 5 (candidate "
         "choice). Declared in `metadata/coverage_gate_961.json`; produced by `scripts/coverage_gate_961.py`; the statistics are "
         "`repo_model.coverage_tests`.", "",
         "## 1. The current rule against calibration", "",
         f"The world is an AR(1) (phi {PHI}) with calm and stress blocks of {BLOCK} days (innovation sd {SIGMA_CALM} and {SIGMA_STRESS}), "
         f"{d['days']} decision days, leads 1-5, seed {d['seed']}. Forecasts are 23 Gaussian quantiles on the protocol's grid. "
         "The rule ranks by mean grid CRPS (smaller is better).", "",
         "| rank | forecaster | mean grid CRPS | passes the gate | passes the pooled cells |", "|---|---|---|---|---|"]
    for i, name in enumerate(order, 1):
        g = d["gate"][name]
        L.append(f"| {i} | {name} | {crps[name]:.4f} | {'yes' if g['pass'] else 'no'} | {'yes' if g['pooled_pass'] else 'no'} |")
    field = [n for n in order if n != "ideal"]
    L += ["", f"With the ideal forecaster in the field the rule ranks it first, as propriety guarantees. A real field never holds the "
          f"true law. Without it the rule ranks `{field[0]}` first, which fails the gate (failing cells: "
          f"{', '.join(d['gate'][field[0]]['failing_cells']) or 'none'}).", "",
          "Paired against `under_0.5` (one-sided 95% lower bound of mean S(benchmark) - S(under_0.5), positive favours the "
          "under-dispersed forecast):", "", "| benchmark (calibrated pooled) | mean difference | lower bound |", "|---|---|---|"]
    for b, p in d["paired_under_0.5"].items():
        L.append(f"| {b} | {p['mean_difference']:+.4f} | {p['lower_95']:+.4f} |")
    L += ["", "## 2. What the declared gate does", "",
          f"Per lead and regime: Kupiec at q05 and at q95 (fail below p = {ALPHA_GATE}), Christoffersen independence at q95 "
          f"(p < {ALPHA_GATE}; decision days thinned to every h-th at lead h), and the 98% band's coverage within [{BAND_LOW}, {BAND_HIGH}]. "
          "A forecaster passes when every cell passes.", "",
          "| forecaster | cells failing |", "|---|---|"]
    for name in order:
        g = d["gate"][name]
        L.append(f"| {name} | {', '.join(g['failing_cells']) or 'none'} |")
    L += ["", "The pooled forecasters (`pooled`, `persistence`, `climatology`) are calibrated over the whole path and fail by regime: "
          "over-wide in calm, too narrow in stress. A pooled pass is reported beside each result and decides nothing.", "",
          "## 3. The gate's own size", "",
          f"The ideal forecaster is calibrated by construction. On {s['paths']} simulated paths of {s['days']} days ({s['cells_per_path']} "
          f"lead-and-regime cells, four tests each, every one at 1%) the declared gate fails it on "
          f"{pct(s['declared']['fail_share'])} of paths. Share of paths on which each test fails at least one cell: "
          + ", ".join(f"{k} {pct(v)}" for k, v in s["declared"]["fail_share_by_test"].items()) + ". By lead (any cell of the lead): "
          + ", ".join(f"lead {k} {pct(v)}" for k, v in s["declared"]["fail_share_by_lead"].items()) + ".", "",
          "The failures are Kupiec's, and they grow with the lead. Kupiec assumes independent hits; the errors of an h-step forecast "
          "made on consecutive days overlap, so their hits are positively dependent, the hit count is more variable than Kupiec assumes, "
          "and a calibrated forecast is rejected too often. Independence is already read on thinned days in the declared gate; Kupiec "
          "is not. **Post hoc (not declared; seen after the first run):** thinning Kupiec to every h-th day as well gives a failure share "
          f"of {pct(s['post_hoc_thinned_kupiec']['fail_share'])} on the same paths ("
          + ", ".join(f"lead {k} {pct(v)}" for k, v in s["post_hoc_thinned_kupiec"]["fail_share_by_lead"].items()) + "), which is "
          "still a family of forty tests at 1% and well above 1%. On the demonstration path the post-hoc variant "
          + "; ".join(f"{n}: {'passes' if d['gate'][n]['post_hoc_thinned_kupiec']['pass'] else 'fails'}" for n in order) + ".", "",
          "## Questions for Eleonora", "",
          "1. Whether a coverage gate becomes a registration requirement is a section 13 kind-(a) amendment, hers to decide. The "
          "demonstration above is the evidence, and it stands on the simulation alone (her #741 ruling).",
          "2. If it does, the gate's size above says two things need deciding: whether Kupiec is read on thinned days at leads above 1, and "
          "whether the per-cell 1% levels get a family-wise correction (or fewer cells). Both are level choices and hers; the declared "
          "gate as written would reject a calibrated candidate about half the time at this sample size.",
          "3. On a whole-bp target, is a hit `y > q` or `y >= q`? The world here is continuous, so the question does not move a number "
          "on this page.", "",
          "## Not done here", "",
          "The directive's criteria 2 and 3 (the candidate's per-day 23-level forecasts, and the gate applied to `gbm_funding`, B3 and the "
          "direct-pairs twin) need walks and are not in this run; see the pull request.", ""]
    return "\n".join(L)


def report_command(args):
    record = json.loads(args.record.read_text(encoding="utf-8"))
    RECORD.parent.mkdir(parents=True, exist_ok=True)
    RECORD.write_text(json.dumps(record, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    PAGE.write_text(render(record), encoding="utf-8")
    print("wrote", PAGE)
    return 0


def check_command(_args):
    if not RECORD.exists():
        print("no record yet: `run` and `report` have not been run", file=sys.stderr)
        return 1
    record = json.loads(RECORD.read_text(encoding="utf-8"))
    if not PAGE.exists() or PAGE.read_text(encoding="utf-8") != render(record):
        print("the page is not what the record gives; run `report`", file=sys.stderr)
        return 1
    print("ok")
    return 0


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="command", required=True)
    run = sub.add_parser("run")
    run.add_argument("--output", type=Path, required=True)
    run.set_defaults(func=run_command)
    rep = sub.add_parser("report")
    rep.add_argument("record", type=Path)
    rep.set_defaults(func=report_command)
    sub.add_parser("check").set_defaults(func=check_command)
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
