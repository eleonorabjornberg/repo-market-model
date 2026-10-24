"""Size of the coverage requirement under three hit rules, and power against a too-narrow forecaster (#1156).

H1 (scoring protocol synthetic suite) and H5 step 5 (candidate choice). A development study on synthetic data, never a
verdict. It follows Eleonora's ruling of 22 October 2026 on PR #1137 (answers 1, 2, 3 and 5 at their defaults, answer 4
decided by this measurement); every choice is in `metadata/coverage_size_1156.json`, committed before any figure.

The world: a calibrated forecaster of a whole-bp target with mass points. The target is `round(x_t)` for an AR(1) latent
`x_t` with three regimes of unequal length, 2,000 days, leads h = 1 to 5. The forecaster knows `x_t`, the regime schedule
and the law, so its discretised-normal forecast at each lead is the true conditional distribution; its quantiles are the
integer quantiles of that distribution, so outcomes tie them. Kupiec and independence are read on every h-th day at lead
h (`method="thinned"`) by `scoring_protocol.coverage_cells`; Holm over the family of one hit rule's tests at 5% is
`scoring_protocol.enforce_coverage_requirement(..., family="holm", alpha=0.05)`, with
`COVERAGE_REQUIREMENT_IN_FORCE` patched True inside this script only and restored after each call; it is never set in the
tree. The three hit rules are `strict`, `tie_counts` and the randomised tie rule (`coverage_tests.randomised_hit_sequence`,
tie probability `coverage_tests.tie_hit_probability` from the forecast's own distribution, draws seeded and recorded).

Measures: the share of paths on which a calibrated forecaster fails the requirement, per rule, overall and per lead (Holm
over that lead's tests), with a Wilson 95% interval; the lead-1 hit rate per rule and level; and, for each rule whose
size is at most 5%, the share of paths on which a too-narrow forecaster fails it. The size runs in minutes (stdlib only):
below the two-hour line of the `long-run` rule, so it runs here and not on her Mac. Commands, from a clone of the branch:

    PYTHONPATH=src python3 scripts/coverage_size_1156.py run --output docs/research/coverage-size-1156/result.json
    PYTHONPATH=src python3 scripts/coverage_size_1156.py page \\
        --score docs/research/coverage-size-1156/result.json --output docs/research/coverage-size-1156-result.md
"""

from __future__ import annotations

import argparse
import json
import math
import multiprocessing
import platform
import random
import sys
from datetime import date, timedelta
from hashlib import sha256
from pathlib import Path
from statistics import NormalDist
from typing import Dict, List, Mapping, Optional, Sequence, Tuple
from unittest import mock

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))

from repo_model import coverage_tests as ct  # noqa: E402
from repo_model import scoring_protocol as sp  # noqa: E402

DECLARATION_PATH = REPO / "metadata" / "coverage_size_1156.json"
DECLARATION = json.loads(DECLARATION_PATH.read_text(encoding="utf-8"))
DESIGN = DECLARATION["design"]
WORLD = DECLARATION["world"]
RULES = tuple(DESIGN["rules"])
LEVELS = tuple(DESIGN["levels"])
LEADS = tuple(DESIGN["leads"])
ALPHA = DESIGN["alpha"]
PASS_SIZE = 0.05

_N = NormalDist()
_Z = {level: _N.inv_cdf(level) for level in LEVELS}
_SQRT2 = math.sqrt(2.0)


def _cdf(z: float) -> float:
    return 0.5 * math.erfc(-z / _SQRT2)


def discrete_quantile(mean: float, sd: float, level: float) -> Tuple[int, float, float]:
    """The integer quantile of round(N(mean, sd^2)) at `level`, with P(Y < q) and P(Y <= q).

    The smallest integer k with P(Y <= k) >= level, where P(Y <= k) = Phi((k + 1/2 - mean) / sd).
    """

    z = _Z[level] if level in _Z else _N.inv_cdf(level)
    k = math.ceil(mean + sd * z - 0.5)
    while _cdf((k + 0.5 - mean) / sd) < level:
        k += 1
    while _cdf((k - 0.5 - mean) / sd) >= level:
        k -= 1
    return k, _cdf((k - 0.5 - mean) / sd), _cdf((k + 0.5 - mean) / sd)


def tie_probability(cdf_below: float, cdf_at: float, level: float) -> float:
    """The probability that a tie at the quantile of `level` is a hit in that level's own tail."""

    upper = level > 0.5
    return ct.tie_hit_probability(cdf_below, cdf_at, (1.0 - level) if upper else level, upper=upper)


def _business_days(count: int) -> List[date]:
    days, day = [], date(2005, 1, 3)
    while len(days) < count:
        if day.weekday() < 5:
            days.append(day)
        day += timedelta(days=1)
    return days


def _schedule(total: int) -> List[dict]:
    """The regime of each day index; days past the declared blocks keep the last regime."""

    out: List[dict] = []
    for block in WORLD["regimes"]:
        out.extend([block] * block["days"])
    while len(out) < total:
        out.append(WORLD["regimes"][-1])
    return out[:total]


def simulate(seed: int, *, narrow: float, days: Optional[int] = None) -> dict:
    """One path: forecasts (23 quantiles per lead, only the four read levels filled), outcomes, regimes, ties, draws.

    `narrow` multiplies the forecaster's standard deviation (1.0 is the calibrated forecaster); the outcome stream
    depends on `seed` only, so a narrow forecaster is scored on the same outcomes as the calibrated one.
    """

    days = WORLD["days"] if days is None else days
    total = days + max(LEADS)
    schedule = _schedule(total)
    rng = random.Random(seed)
    a = WORLD["a"]
    x = schedule[0]["mu"]
    latent, outcomes = [], {}
    calendar = _business_days(total)
    for t in range(total):
        block = schedule[t]
        x = block["mu"] + a * (x - block["mu"]) + block["s"] * rng.gauss(0.0, 1.0)
        latent.append(x)
        outcomes[calendar[t]] = float(math.floor(x + 0.5))
    draw_rng = random.Random(seed + 50000)
    grid_index = [sp.GRID.index(level) for level in LEVELS]
    forecasts, regimes, ties, draws = {}, {}, {}, {}
    for t in range(days):
        day = calendar[t]
        m, v = latent[t], 0.0
        by_lead, tie_lead, draw_lead = {}, {}, {}
        for k in range(1, max(LEADS) + 1):
            block = schedule[t + k]
            m = block["mu"] + a * (m - block["mu"])
            v = a * a * v + block["s"] ** 2
            sd = narrow * math.sqrt(v)
            quantiles = [0.0] * len(sp.GRID)
            probabilities = [0.0] * len(sp.GRID)
            unifs = [0.0] * len(sp.GRID)
            for level, index in zip(LEVELS, grid_index):
                q, below, at = discrete_quantile(m, sd, level)
                quantiles[index] = float(q)
                probabilities[index] = tie_probability(below, at, level)
                unifs[index] = draw_rng.random()
            by_lead[k], tie_lead[k], draw_lead[k] = quantiles, probabilities, unifs
        forecasts[day], ties[day], draws[day] = by_lead, tie_lead, draw_lead
        regimes[day] = schedule[t]["label"]
    return {
        "forecasts": forecasts, "outcomes": outcomes, "calendar": calendar, "regimes": regimes,
        "ties": ties, "draws": draws,
    }


def _fails(cells: Sequence[sp.CoverageCell], rule: str) -> bool:
    """Whether the requirement fails these cells: Holm over the rule's tests at 5%, the flag patched on in here only."""

    if not [c for c in cells if c.rule == rule]:
        return False
    with mock.patch.object(sp, "COVERAGE_REQUIREMENT_IN_FORCE", True):
        try:
            sp.enforce_coverage_requirement(cells, alpha=ALPHA, family=DESIGN["family"], rule=rule)
        except sp.CoverageRequirementFailed:
            return True
    return False


def path_report(seed: int, *, narrow: float, days: Optional[int] = None) -> dict:
    """Whether each rule's requirement fails on one path, overall and per lead, and the lead-1 hit counts."""

    world = simulate(seed, narrow=narrow, days=days)
    cells = sp.coverage_cells(
        world["forecasts"], world["outcomes"], world["calendar"], world["regimes"],
        method=DESIGN["method"], tie_probabilities=world["ties"], draws=world["draws"],
    )
    fails: Dict[str, Dict[str, bool]] = {}
    for rule in RULES:
        row = {"all": _fails(cells, rule)}
        for h in LEADS:
            row[str(h)] = _fails([c for c in cells if c.lead == h], rule)
        fails[rule] = row
    hits: Dict[str, Dict[str, List[int]]] = {rule: {} for rule in RULES}
    for c in cells:
        if c.lead == 1:
            key = f"{c.level:g}"
            cur = hits[c.rule].setdefault(key, [0, 0])
            cur[0] += c.hits
            cur[1] += c.n
    return {"fails": fails, "hits": hits}


def wilson(fails: int, paths: int, z: float = 1.959964) -> Tuple[float, float]:
    """The Wilson score interval of a share."""

    if paths <= 0:
        raise ValueError("a share needs at least one path")
    p = fails / paths
    denom = 1.0 + z * z / paths
    centre = (p + z * z / (2.0 * paths)) / denom
    half = z * math.sqrt(p * (1.0 - p) / paths + z * z / (4.0 * paths * paths)) / denom
    return max(0.0, centre - half), min(1.0, centre + half)


def rules_named(size: Mapping[str, Mapping[str, Mapping[str, int]]]) -> List[str]:
    """The rules whose overall family-wise size is at most 0.05 (point estimate); all of them, none chosen among them."""

    return [rule for rule in RULES if size[rule]["all"]["fails"] <= PASS_SIZE * size[rule]["all"]["paths"]]


def _job(args: Tuple[int, float]) -> dict:
    seed, narrow = args
    return path_report(seed, narrow=narrow)


def _summarise(reports: Sequence[dict]) -> dict:
    paths = len(reports)
    out: Dict[str, dict] = {}
    for rule in RULES:
        row = {}
        for key in ["all"] + [str(h) for h in LEADS]:
            fails = sum(1 for r in reports if r["fails"][rule][key])
            lo, hi = wilson(fails, paths)
            row[key] = {"fails": fails, "paths": paths, "share": fails / paths, "lo": lo, "hi": hi}
        out[rule] = row
    return out


def _hit_rates(reports: Sequence[dict]) -> dict:
    out: Dict[str, dict] = {}
    for rule in RULES:
        out[rule] = {}
        for level in LEVELS:
            key = f"{level:g}"
            hits = sum(r["hits"][rule][key][0] for r in reports)
            n = sum(r["hits"][rule][key][1] for r in reports)
            out[rule][key] = {"rate": hits / n, "hits": hits, "n": n, "nominal": min(level, 1.0 - level)}
    return out


def run(args) -> int:
    size_paths = args.paths or DECLARATION["size"]["paths"]
    power_paths = args.power_paths or DECLARATION["power"]["paths"]
    base = DECLARATION["size"]["base_seed"]
    workers = args.workers or max(1, multiprocessing.cpu_count() - 1)
    seeds = [base * 100000 + i for i in range(size_paths)]
    with multiprocessing.Pool(workers) as pool:
        reports = pool.map(_job, [(s, 1.0) for s in seeds], chunksize=8)
        size = _summarise(reports)
        named = rules_named(size)
        power: Dict[str, dict] = {}
        for factor in DECLARATION["power"]["factors"]:
            if not named:
                break
            narrow_reports = pool.map(
                _job, [(base * 100000 + 50000 + i, factor) for i in range(power_paths)], chunksize=8
            )
            summary = _summarise(narrow_reports)
            power[f"{factor:g}"] = {rule: summary[rule] for rule in named}
    record = {
        "directive": 1156,
        "declaration_sha256": sha256(DECLARATION_PATH.read_bytes()).hexdigest(),
        "declaration": DECLARATION,
        "environment": {"python": platform.python_version(), "workers": workers},
        "flag_in_tree": sp.COVERAGE_REQUIREMENT_IN_FORCE,
        "paths": {"size": size_paths, "power": power_paths if named else 0},
        "seeds": {"size": f"{base}*100000 + i, i in 0..{size_paths - 1}",
                  "power": f"{base}*100000 + 50000 + i, i in 0..{power_paths - 1}",
                  "draws": "path seed + 50000"},
        "size": size,
        "hit_rates_lead1": _hit_rates(reports),
        "rules_named": named,
        "power": power,
    }
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print("wrote", out)
    return 0


def _pct(x: float) -> str:
    return f"{100.0 * x:.1f}%"


def _cell(c: Mapping) -> str:
    return f"{_pct(c['share'])} [{_pct(c['lo'])}, {_pct(c['hi'])}]"


NAMES = {"strict": "`strict` (y beyond q)", "tie_counts": "`tie_counts` (y at or beyond q)",
         "randomised": "randomised tie rule"}


def render(record: Mapping) -> str:
    """The result page, every figure from the record."""

    size, named = record["size"], record["rules_named"]
    n = record["paths"]["size"]
    lines = [
        "# Size of the coverage requirement under three hit rules (#1156)",
        "",
        "**Hypothesis and step:** H1 (scoring protocol synthetic suite) and H5 step 5 (candidate choice). **Development, "
        "synthetic data, not a verdict.** Follow-up to PR #1137 (#1130) and Eleonora's ruling of 22 October 2026 there "
        "(answers 1, 2, 3 and 5 at their defaults; answer 4, the hit rule, left to this measurement). Generated by "
        "`scripts/coverage_size_1156.py page` from `docs/research/coverage-size-1156/result.json`, not edited by hand; "
        "declared in `metadata/coverage_size_1156.json` before any figure.",
        "",
        "**What was measured.** Calibrated forecasters of a whole-bp target with mass points (an AR(1) latent rounded to "
        "whole bp, three regimes of unequal length, 2,000 days, leads 1 to 5; the forecaster knows the law, so its "
        "integer quantiles tie the outcomes). Kupiec and independence on every h-th day at lead h, at q05/q95 and q01/q99 "
        "by lead and regime; Holm over the family of one hit rule's tests at 5% "
        f"(`enforce_coverage_requirement(..., family=\"holm\", alpha=0.05)`, with the flag patched on inside the script "
        f"only: in the tree `COVERAGE_REQUIREMENT_IN_FORCE` is {record['flag_in_tree']}). A path *fails* when Holm rejects "
        f"anywhere in the family. {n:,} paths; intervals are Wilson 95% intervals of the share of paths.",
        "",
        "## Family-wise size of a calibrated forecaster",
        "",
        "Share of paths on which the requirement fails a *calibrated* forecaster. The nominal level is 5%.",
        "",
        "| Hit rule | overall [95%] | lead 1 | lead 2 | lead 3 | lead 4 | lead 5 |",
        "|---|---|---|---|---|---|---|",
    ]
    for rule in RULES:
        row = size[rule]
        lines.append(
            f"| {NAMES[rule]} | {_cell(row['all'])} | " + " | ".join(_cell(row[str(h)]) for h in (1, 2, 3, 4, 5)) + " |"
        )
    lines += [
        "",
        "Per-lead columns are Holm over that lead's tests alone; the overall column is Holm over all leads and regimes.",
        "",
        "## Hit rate at lead 1",
        "",
        "Pooled over the paths and regimes; the nominal rate is the tail probability.",
        "",
        "| Hit rule | q05 (5%) | q95 (5%) | q01 (1%) | q99 (1%) |",
        "|---|---|---|---|---|",
    ]
    for rule in RULES:
        h = record["hit_rates_lead1"][rule]
        lines.append(f"| {NAMES[rule]} | " + " | ".join(f"{100.0 * h[k]['rate']:.2f}%" for k in ("0.05", "0.95", "0.01", "0.99")) + " |")
    lines += ["", "## The rule the requirement reads", ""]
    if not named:
        lines.append(
            "**None.** No hit rule fails a calibrated forecaster on no more than 5% of paths, so this result does not "
            "choose one. Both deterministic rules and the randomised rule stay reported."
        )
    elif len(named) == 1:
        lines.append(
            f"**{NAMES[named[0]]}.** It is the only hit rule for which a calibrated forecaster fails on no more than 5% of "
            f"paths ({_cell(size[named[0]]['all'])}). The others do not. Both deterministic rules stay reported whatever "
            "this finds. Whether the whole design may be put in force, and the flag, are Eleonora's later steps."
        )
    else:
        lines.append(
            "**More than one rule is at or under 5%:** " + ", ".join(NAMES[r] for r in named) + ". This result does not "
            "choose among them; that is Eleonora's decision."
        )
    lines += ["", "## Power against a too-narrow forecaster", ""]
    if not record["power"]:
        lines.append("No rule passed on size, so power was not measured.")
    else:
        lines += [
            f"Share of paths on which the requirement fails a forecaster whose standard deviation is the factor times the "
            f"true one, for each rule that passed on size ({record['paths']['power']:,} paths per factor; the factors are "
            "the declaration's choice, since #961's forecaster is not on main).",
            "",
            "| Factor | " + " | ".join(NAMES[r] for r in named) + " |",
            "|---|" + "---|" * len(named),
        ]
        for factor, rows in record["power"].items():
            lines.append(f"| {factor} | " + " | ".join(_cell(rows[r]["all"]) for r in named) + " |")
    lines += [
        "",
        "## What this shows and does not show",
        "",
        "- It shows the size of the design on a synthetic world built to be calibrated, with whole-bp mass points. It is "
        "not a result about any candidate, benchmark or published record, and no verdict.",
        "- The forecaster's quantiles are integers, so ties are frequent; a forecaster with continuous quantiles has no "
        "ties and is a different case. The world's regimes are three blocks the declaration fixes, standing for the protocol's "
        "development split (answer 5); the labels' definition is hers.",
        "- The requirement is not in force (`COVERAGE_REQUIREMENT_IN_FORCE` stays False in the tree), no attestation entry "
        "is added and no published record changes. Setting the flag is a later step after her merge of the record and her "
        "own `GO`.",
        "- Not checked: HAC (`method=\"hac\"`) size; other forecasters (a pooled-calibrated or a regime-miscalibrated "
        "one); the real candidates, which need walks on her Mac.",
        "",
        f"Seeds: size `{record['seeds']['size']}`; power `{record['seeds']['power']}`; draws `{record['seeds']['draws']}`. "
        f"Declaration sha256 `{record['declaration_sha256'][:12]}…`. Python {record['environment']['python']}.",
        "",
    ]
    return "\n".join(lines)


def page(args) -> int:
    record = json.loads(Path(args.score).read_text(encoding="utf-8"))
    Path(args.output).write_text(render(record), encoding="utf-8")
    print("wrote", args.output)
    return 0


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="command", required=True)
    r = sub.add_parser("run", help="simulate the size and the power and write the record")
    r.add_argument("--output", required=True)
    r.add_argument("--paths", type=int, default=0, help="override the declared size paths (tests and timing only)")
    r.add_argument("--power-paths", type=int, default=0)
    r.add_argument("--workers", type=int, default=0)
    r.set_defaults(func=run)
    g = sub.add_parser("page", help="write the result page from a record")
    g.add_argument("--score", required=True)
    g.add_argument("--output", required=True)
    g.set_defaults(func=page)
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
