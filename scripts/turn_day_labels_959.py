#!/usr/bin/env python3
"""The turn-day labels against the month-end label: B2, the mean-reversion level and the risk-date set (#959; H5 step 2).

A development measurement, never a verdict. Every choice is in `metadata/turn_day_labels_959.json`, which this script
refuses to read unless it is committed and unchanged. The labels are `repo_model.turn_days`; B2 is
`repo_model.protocol_benchmarks.b2_forecast`, the mean-reversion model is `repo_model.spread_mean_reversion` (#686), and the
risk-date calendar benchmark is `repo_model.risk_date_spread` (#693). All three are read unchanged: only the day-type
labels they group by are swapped, through `turn_days.TurnLabels`. Scored by `repo_model.scoring_protocol` (#655) at the
development tier; no day after 2025-12-31 is read (`docs/decisions/lockbox.md`).

    PYTHONPATH=src python3 -m repo_model.cli build --raw-root tests/fixtures/snapshots/funding_inputs \\
        --output PUB.csv --build-cutoff 2026-09-08T21:31:42+00:00 --decision-time 16:00:00
    PYTHONPATH=src python3 -m repo_model.cli verify-panel PUB.csv --manifest metadata/funding_panel_manifest.json
    PYTHONPATH=src python3 scripts/turn_day_labels_959.py run --published PUB.csv --output OUT/score.json
    python3 scripts/turn_day_labels_959.py report OUT/score.json
    python3 scripts/turn_day_labels_959.py check

`run` writes the record; `report` copies it to `docs/research/turn-day-labels-959/result.json` and writes the page
`docs/research/turn-day-labels-959-result.md` from it; `check` fails when the page is not what the record gives.
Stdlib only.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import multiprocessing
import sys
from collections import Counter
from datetime import date, time
from pathlib import Path
from typing import Callable, Dict, List, Mapping, Optional, Sequence, Tuple

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))


def _load(name: str):
    spec = importlib.util.spec_from_file_location(f"{name}_script", REPO / "scripts" / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[f"{name}_script"] = module
    spec.loader.exec_module(module)
    return module


from repo_model import lockbox, protocol_benchmarks as pb, scoring_protocol as sp  # noqa: E402
from repo_model import risk_date_spread as rds, spread_mean_reversion as smr, turn_days as td  # noqa: E402
from repo_model.baseline import panel_sha256  # noqa: E402
from repo_model.data import audit_panel, load_daily_panel  # noqa: E402
from repo_model.evaluation_splits import load_split_declaration  # noqa: E402
from repo_model.splits import LookAheadError, SplitError  # noqa: E402

s693 = _load("risk_date_spread_693")
s634 = _load("spread_distribution_634")

DECLARATION = REPO / "metadata" / "turn_day_labels_959.json"
SPLITS = REPO / "metadata" / "evaluation_splits.json"
SOURCES = REPO / "metadata" / "sources.json"
RESEARCH = REPO / "docs" / "research"
RECORD = RESEARCH / "turn-day-labels-959" / "result.json"
PAGE = RESEARCH / "turn-day-labels-959-result.md"
SEED = 959
LAST_DAY = date(2025, 12, 31)
DECISION_TIME = time(16, 0)
MIN_DAYS = 20
LEVEL = sp.ALPHA
HORIZONS = sp.HORIZONS
LABEL = "development data, not a verdict"
#: The three comparisons of the declaration, each as (key, title).
COMPARISONS = (
    ("a", "(a) B2 relabelled against B2 as is"),
    ("b", "(b) the mean-reversion candidate with its level set excluding only turn days, against itself as is"),
    ("c", "(c) the risk-date calendar benchmark of H6 on the turn set, against the same benchmark as is"),
)


# -- scope ---------------------------------------------------------------------------------------------------------


def require_scored_days(days) -> None:
    """Refuse a day after the declared last day and a locked day.

    Raises:
        LookAheadError: a day after 2025-12-31 or in a locked tier.
    """

    days = list(days)
    for day in sorted(days):
        if day > LAST_DAY:
            raise LookAheadError(f"{day} is after {LAST_DAY}, the last day #959 scores; the declaration admits no later day")
    lockbox.require_unlocked(days, where="scripts/turn_day_labels_959")


# -- intervals -----------------------------------------------------------------------------------------------------


def two_sided(point: float, t_draws: Sequence[float], se: float, draws: int) -> List[float]:
    """The 90% two-sided studentized interval: the point less the 95th and the 5th percentile of the t-draws times `se`."""

    return [point - sp._bound(t_draws, 1.0 - LEVEL, draws) * se, point - sp._bound(t_draws, LEVEL, draws) * se]


def row_of(test: "sp.PairedTest") -> dict:
    """One paired test: positive favours the candidate (d = S(benchmark) - S(candidate)); both intervals studentized."""

    return {
        "days": test.n,
        "benchmark_mean": test.benchmark_mean,
        "candidate_mean": test.benchmark_mean - test.mean_difference,
        "difference": test.mean_difference,
        "difference_interval": two_sided(test.mean_difference, test.t_draws, test.standard_error, test.draws),
        "skill": test.skill,
        "skill_interval": two_sided(test.skill, test.skill_t_draws, test.skill_standard_error, test.draws),
    }


def verdict_words(row: dict) -> str:
    if "undefined" in row:
        return "scores identical" if row["difference"] == 0.0 else "undefined"
    low, high = row["skill_interval"]
    if low > 0.0:
        return "candidate better"
    if high < 0.0:
        return "candidate worse"
    return "no difference"


# -- worker for the paired tests -----------------------------------------------------------------------------------

_SERIES: Dict[str, Dict[str, Dict[date, float]]] = {}


def run_test(task):
    """(comparison, group, [(benchmark, candidate)...], days) -> (comparison, group, {pair: row})."""

    comparison, group, pairs, days = task
    series = _SERIES[comparison]
    chosen = [({d: series[b][d] for d in days}, {d: series[c][d] for d in days}) for b, c in pairs]
    out = {}
    for (b, c), pair in zip(pairs, chosen):
        try:
            out[f"{b} -> {c}"] = row_of(sp.paired_test(pair[0], pair[1], seed=SEED, draws=DRAWS[0]))
        except sp.ProtocolError as error:
            # d is zero on every day (identical forecasts), or a benchmark scores zero: say so, with the means
            mean_b, mean_c = sum(pair[0].values()) / len(days), sum(pair[1].values()) / len(days)
            out[f"{b} -> {c}"] = {"undefined": str(error), "days": len(days), "benchmark_mean": mean_b,
                                  "candidate_mean": mean_c, "difference": mean_b - mean_c}
    return comparison, group, out


DRAWS = [sp.DRAWS]


def run_tests(tasks: Sequence[tuple], processes: int) -> Dict[Tuple[str, str], dict]:
    context = multiprocessing.get_context("fork")
    with context.Pool(processes) as pool:
        done = pool.map(run_test, tasks, chunksize=1)
    return {(comparison, group): rows for comparison, group, rows in done}


# -- groups --------------------------------------------------------------------------------------------------------


class Panel:
    """The published panel, its calendar and the target-day labels."""

    def __init__(self, path: Path):
        self.rows = load_daily_panel(path)
        audit_panel(self.rows)
        self.dates = [r.date for r in self.rows]
        self.position = {d: i for i, d in enumerate(self.dates)}
        self.values = {r.date: r.values for r in self.rows}
        self.outcomes = {r.date: r.spread_bps for r in self.rows}
        self.splits = load_split_declaration(SPLITS)
        self.registry = json.loads(SOURCES.read_text(encoding="utf-8"))
        self.new = td.TurnLabels(self.splits)
        self.settings = dict(registry=self.registry, decision_time=DECISION_TIME)

    def target(self, decision: date, lead: int) -> date:
        return self.dates[self.position[decision] + lead]

    def kind(self, day: date) -> str:
        return self.new.reporting_day_type(day, self.values[day])

    def old_kind(self, day: date) -> str:
        return self.splits.reporting_day_type(day, self.values[day])


def target_groups(panel: Panel) -> Dict[str, Callable[[date], bool]]:
    """The groups by the target day: the five labels, then the three rows alone, each as a predicate on the target day."""

    out: Dict[str, Callable[[date], bool]] = {label: (lambda t, label=label: panel.kind(t) == label) for label in td.LABELS}
    out["turn days (all three labels)"] = lambda t: panel.kind(t) in td.TURN_LABELS
    out["penultimate days"] = td.penultimate_day
    out["december_26"] = td.december_26
    return out


def cell_series(cells: Mapping[Tuple[date, int], float], panel: Panel, include) -> Dict[date, float]:
    """A decision day's mean over its leads whose target `include` admits."""

    return s634.day_means(cells, lambda d, h: include(panel.target(d, h)))


def decision_groups(days: Sequence[date], cells: Mapping[str, Mapping[Tuple[date, int], float]], panel: Panel):
    """Per group: (decision days, number of target cells, {model: {day: score}}), for the pooled days, regimes and types."""

    models = list(cells)
    out = {}
    pooled = {m: cell_series(cells[m], panel, lambda t: True) for m in models}
    out["pooled"] = (sorted(days), len(days) * len(HORIZONS), pooled)
    for label in panel.splits.regime_labels:
        group = [d for d in days if panel.splits.regime(d) == label]
        out[f"regime {label}"] = (group, len(group) * len(HORIZONS), pooled)
    for name, include in target_groups(panel).items():
        series = {m: cell_series(cells[m], panel, include) for m in models}
        group = sorted(set.intersection(*(set(s) for s in series.values())))
        count = sum(1 for d in group for h in HORIZONS if include(panel.target(d, h)))
        out[f"target: {name}"] = (group, count, series)
    return out


def summarise_groups(comparison: str, groups, pairs, tasks: list, series_store: dict) -> dict:
    """The group table of a comparison with its tasks queued; a group of fewer than `MIN_DAYS` days is listed, not tested."""

    table = {}
    for name, (days, cells, series) in groups.items():
        # a group's series are those of its own cells: store them under the group so a worker reads them
        for model, values in series.items():
            series_store.setdefault(f"{comparison}|{name}", {})[model] = values
        table[name] = {"decision_days": len(days), "target_cells": cells,
                       "means": {m: (sum(s[d] for d in days) / len(days) if days else None) for m, s in series.items()},
                       "tested": len(days) >= MIN_DAYS}
        if len(days) >= MIN_DAYS:
            tasks.append((comparison, name, pairs, tuple(days)))
    return table


# -- (a) and (b): the forecasts ------------------------------------------------------------------------------------


def offered_days(panel: Panel) -> List[date]:
    days = [d for i, d in enumerate(panel.dates) if i + max(HORIZONS) < len(panel.dates)
            and panel.dates[i + max(HORIZONS)] <= LAST_DAY]
    require_scored_days(days + [panel.dates[panel.position[d] + max(HORIZONS)] for d in days])
    return days


def build_a(panel: Panel, offered: Sequence[date]):
    old, new, b1 = {}, {}, {}
    dropped = []
    for day in offered:
        i = panel.position[day]
        try:
            one = pb.b1_forecast(panel.rows, i, **panel.settings)
            two = pb.b2_forecast(panel.rows, i, splits=panel.splits, **panel.settings)
            three = pb.b2_forecast(panel.rows, i, splits=panel.new, **panel.settings)
        except (sp.ProtocolError, SplitError):
            dropped.append(day.isoformat())
            continue
        b1[day], old[day], new[day] = one, two, three
    return {"B1": b1, "B2 as is": old, "B2 relabelled": new}, dropped


def build_b(panel: Panel, offered: Sequence[date]):
    walks = {
        "as is": smr.walk(panel.rows, offered, splits=panel.splits, **panel.settings),
        "turn days only excluded": smr.walk(panel.rows, offered, splits=td.TurnLabels(panel.splits, keep_tax_date=False), **panel.settings),
        "turn days and tax dates excluded": smr.walk(panel.rows, offered, splits=panel.new, **panel.settings),
    }
    return {name: walk.forecasts for name, walk in walks.items()}, {name: len(walk.fits) for name, walk in walks.items()}, \
        {name: len(walk.skipped) for name, walk in walks.items()}


def cells_of(panel: Panel, forecasts: Mapping[date, Mapping[int, Sequence[float]]], days: Sequence[date]):
    calendar = panel.dates
    return s634.cell_scores({d: forecasts[d] for d in days}, panel.outcomes, calendar, sp.grid_crps)


# -- (c): the risk-date set ----------------------------------------------------------------------------------------


def risk_type_turn(when: date, values, labels: "td.TurnLabels", *, coupon_clause: bool) -> Optional[str]:
    """H6's risk type of a day on the turn set: a turn label or the tax date, else `settlement`, else `None`."""

    kind = labels.reporting_day_type(when, values)
    if kind != td.ORDINARY:
        return kind
    coupons = values.get("treasury_settlement_coupons")
    return "settlement" if coupon_clause and coupons is not None and float(coupons) > 0.0 else None


def target_type_turn(panel: Panel, i: int, h: int, labels) -> Optional[str]:
    """`risk_date_spread.target_risk_type` with the turn labels: a coupon settlement counts only where it was public."""

    scored = i + h
    public = rds.smv.coupon_public(panel.rows, scored, i, **panel.settings)
    kind = risk_type_turn(panel.dates[scored], panel.rows[scored].values, labels, coupon_clause=public)
    if kind == "settlement":
        rds.require_settlement_public(panel.rows, scored, i, **panel.settings)
    return kind


def calendar_turn(panel: Panel, i: int, labels) -> Dict[int, List[float]]:
    """`risk_date_spread.calendar_forecast` with `labels` giving the day types: the trailing year's spreads of the target's type.

    With the declared `SplitDeclaration` as `labels` it is `calendar_forecast` itself; `build_c` checks that on every day.
    """

    targets = {}
    for h in HORIZONS:
        kind = target_type_turn(panel, i, h, labels)
        if kind is not None:
            targets[h] = kind
    anchor = pb._anchor(panel.rows, i, panel.registry, DECISION_TIME)
    rows = rds.sample_rows(panel.rows, i, anchor, years=rds.CALENDAR_YEARS)
    out = {}
    for h, kind in targets.items():
        same = [s for s in rows if risk_type_turn(panel.dates[s], panel.rows[s].values, labels, coupon_clause=True) == kind]
        rds.require_sample(same, kind, panel.dates[i])
        out[h] = pb.empirical_quantiles(sorted(panel.rows[s].spread_bps for s in same))
    return out


def build_c(panel: Panel, offered: Sequence[date]):
    forecasts = {"B1": {}, "calendar as is": {}, "calendar on the turn set": {}}
    dropped = []
    days = []
    for day in offered:
        i = panel.position[day]
        try:
            one = pb.b1_forecast(panel.rows, i, **panel.settings)
            old = rds.calendar_forecast(panel.rows, i, splits=panel.splits, **panel.settings)
            new = calendar_turn(panel, i, panel.new)
            again = calendar_turn(panel, i, panel.splits)
        except (sp.ProtocolError, SplitError):
            dropped.append(day.isoformat())
            continue
        if again != old:
            raise ValueError(f"the generalised calendar benchmark does not reproduce risk_date_spread.calendar_forecast on {day}")
        days.append(day)
        for h in HORIZONS:
            forecasts["B1"][(day, h)] = one[h]
        for h, quantiles in old.items():
            forecasts["calendar as is"][(day, h)] = quantiles
        for h, quantiles in new.items():
            forecasts["calendar on the turn set"][(day, h)] = quantiles
    return forecasts, days, dropped


def risk_counts(panel: Panel) -> dict:
    """Risk target days per type under each set, to the last scored day: a table of the calendar, no score."""

    out = {"as is": Counter(), "turn set": Counter()}
    for i, day in enumerate(panel.dates):
        if day > LAST_DAY:
            continue
        old = rds.risk_day_type(day, panel.rows[i].values, panel.splits)
        new = risk_type_turn(day, panel.rows[i].values, panel.new, coupon_clause=True)
        out["as is"][old or "not a risk date"] += 1
        out["turn set"][new or "not a risk date"] += 1
    return {k: dict(sorted(v.items())) for k, v in out.items()}


# -- run -----------------------------------------------------------------------------------------------------------


def run_command(args) -> int:
    declaration = s693.committed_declaration(DECLARATION)
    DRAWS[0] = args.draws
    panel = Panel(args.published)
    offered = offered_days(panel)
    record: dict = {"issue": 959, "label": LABEL, "declaration": str(DECLARATION.relative_to(REPO)), "panel_sha256": panel_sha256(args.published),
                    "seed": SEED, "draws": args.draws, "last_day": LAST_DAY.isoformat(), "decision_days_offered": len(offered),
                    "min_days": MIN_DAYS, "comparisons": {}}
    tasks: list = []
    store: dict = {}

    # (a)
    forecasts, dropped = build_a(panel, offered)
    days = sorted(forecasts["B2 relabelled"])
    cells = {name: cells_of(panel, f, days) for name, f in forecasts.items()}
    groups = decision_groups(days, cells, panel)
    pairs = [("B2 as is", "B2 relabelled"), ("B1", "B2 as is"), ("B1", "B2 relabelled")]
    record["comparisons"]["a"] = {"dropped_decision_days": dropped, "scored_decision_days": len(days),
                                  "first": days[0].isoformat(), "last": days[-1].isoformat(), "pairs": [list(p) for p in pairs],
                                  "groups": summarise_groups("a", groups, pairs, tasks, store)}
    print(f"(a) {len(days)} decision days", flush=True)

    # (b)
    walks, fits, skipped = build_b(panel, offered)
    common = sorted(set.intersection(*(set(w) for w in walks.values())))
    cells_b = {name: cells_of(panel, f, common) for name, f in walks.items()}
    groups_b = decision_groups(common, cells_b, panel)
    pairs_b = [("as is", "turn days only excluded"), ("as is", "turn days and tax dates excluded")]
    record["comparisons"]["b"] = {"refits": fits, "skipped_decision_days": skipped, "scored_decision_days": len(common),
                                  "first": common[0].isoformat(), "last": common[-1].isoformat(), "pairs": [list(p) for p in pairs_b],
                                  "groups": summarise_groups("b", groups_b, pairs_b, tasks, store)}
    print(f"(b) {len(common)} decision days", flush=True)

    # (c): the cells whose target is a risk date, by target day
    forecasts_c, days_c, dropped_c = build_c(panel, offered)
    require_scored_days({d for d, _ in forecasts_c["B1"]} | {panel.target(d, h) for d, h in forecasts_c["B1"]})
    def cell_c(model: str, keys) -> Dict[Tuple[date, int], float]:
        return {k: sp.grid_crps(forecasts_c[model][k], panel.outcomes[panel.target(*k)]) for k in keys}
    old_keys, new_keys = set(forecasts_c["calendar as is"]), set(forecasts_c["calendar on the turn set"])
    both = sorted(old_keys & new_keys)

    def by_target(cells: Mapping[Tuple[date, int], float]) -> Dict[date, float]:
        sums: Dict[date, List[float]] = {}
        for (d, h), v in cells.items():
            sums.setdefault(panel.target(d, h), []).append(v)
        return {t: sum(v) / len(v) for t, v in sums.items()}

    sets = {
        "as is": ("calendar as is", sorted(old_keys), lambda t: rds.risk_day_type(t, panel.values[t], panel.splits)),
        "turn set": ("calendar on the turn set", sorted(new_keys), lambda t: risk_type_turn(t, panel.values[t], panel.new, coupon_clause=True)),
    }
    c_record = {"old_set_reproduced_on_every_day": True, "dropped_decision_days": dropped_c, "scored_decision_days": len(days_c), "counts": risk_counts(panel), "sets": {}}
    for set_name, (model, keys, typer) in sets.items():
        b1 = by_target(cell_c("B1", keys))
        cal = by_target(cell_c(model, keys))
        kinds = {t: typer(t) for t in cal}
        groups_c = {"pooled": sorted(cal)}
        for label in panel.splits.regime_labels:
            groups_c[f"regime {label}"] = [t for t in sorted(cal) if panel.splits.regime(t) == label]
        for kind in sorted(set(kinds.values())):
            groups_c[f"type: {kind}"] = [t for t in sorted(cal) if kinds[t] == kind]
        table = {}
        for name, group in groups_c.items():
            table[name] = {"target_days": len(group), "means": {m: (sum(s[t] for t in group) / len(group) if group else None)
                                                                  for m, s in (("B1", b1), ("calendar", cal))},
                           "tested": len(group) >= MIN_DAYS}
            if len(group) >= MIN_DAYS:
                tasks.append(("c", f"{set_name}|{name}", [("B1", "calendar")], tuple(group)))
                store[f"c|{set_name}|{name}"] = {"B1": b1, "calendar": cal}
        c_record["sets"][set_name] = {"cells": len(keys), "target_days": len(cal), "groups": table}
    # each set against the other on the cells both call a risk date
    old_both = by_target(cell_c("calendar as is", both))
    new_both = by_target(cell_c("calendar on the turn set", both))
    cross = {"cells": len(both), "target_days": len(old_both), "groups": {}}
    cross_groups = {"pooled": sorted(old_both)}
    for label in panel.splits.regime_labels:
        cross_groups[f"regime {label}"] = [t for t in sorted(old_both) if panel.splits.regime(t) == label]
    for name, group in cross_groups.items():
        cross["groups"][name] = {"target_days": len(group), "tested": len(group) >= MIN_DAYS,
                                 "means": {"as is": sum(old_both[t] for t in group) / len(group) if group else None,
                                           "turn set": sum(new_both[t] for t in group) / len(group) if group else None}}
        if len(group) >= MIN_DAYS:
            tasks.append(("c", f"cross|{name}", [("as is", "turn set")], tuple(group)))
            store[f"c|cross|{name}"] = {"as is": old_both, "turn set": new_both}
    c_record["cross"] = cross
    record["comparisons"]["c"] = c_record
    print(f"(c) {len(days_c)} decision days; {len(tasks)} tests queued", flush=True)

    # run the tests: a task's series are the group's own
    global _SERIES
    _SERIES = {}
    queued = []
    for comparison, name, pairs_, days_ in tasks:
        key = f"{comparison}|{name}"
        _SERIES[key] = store[key]
        queued.append((key, name, pairs_, days_))
    results = run_tests(queued, args.processes)
    for comparison, name, pairs_, days_ in tasks:
        rows = results[(f"{comparison}|{name}", name)]
        if comparison in ("a", "b"):
            record["comparisons"][comparison]["groups"][name]["tests"] = rows
        elif name.startswith("cross|"):
            record["comparisons"]["c"]["cross"]["groups"][name.split("|", 1)[1]]["tests"] = rows
        else:
            set_name, group = name.split("|", 1)
            record["comparisons"]["c"]["sets"][set_name]["groups"][group]["tests"] = rows
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(record, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    print("wrote", args.output)
    return 0


# -- the page ------------------------------------------------------------------------------------------------------


def pct(value: float) -> str:
    return f"{100 * value:+.1f}%"


def interval(pair: Sequence[float], scale: float = 1.0, digits: int = 3) -> str:
    return f"[{pair[0] * scale:+.{digits}f}, {pair[1] * scale:+.{digits}f}]"


def table(rows: Mapping[str, dict], pair: str, count_key: str, label_head: str) -> List[str]:
    lines = [f"| {label_head} | {count_key.replace('_', ' ')} | benchmark CRPS | candidate CRPS | skill [90%] | mean d [90%] | reading |",
             "|---|---|---|---|---|---|---|"]
    for name, g in rows.items():
        if g[count_key] == 0:
            continue
        test = g.get("tests", {}).get(pair)
        if test is None:
            lines.append(f"| {name} | {g[count_key]} | | | not tested (fewer than {MIN_DAYS}) | | |")
            continue
        if "undefined" in test:
            lines.append(f"| {name} | {g[count_key]} | {test['benchmark_mean']:.3f} | {test['candidate_mean']:.3f} | "
                         f"undefined: {test['undefined']} | {test['difference']:+.4f} | {verdict_words(test)} |")
            continue
        lines.append(f"| {name} | {g[count_key]} | {test['benchmark_mean']:.3f} | {test['candidate_mean']:.3f} | "
                     f"{pct(test['skill'])} {interval(test['skill_interval'], 100, 1)} | {test['difference']:+.4f} "
                     f"{interval(test['difference_interval'], 1, 4)} | {verdict_words(test)} |")
    return lines


def render(record: dict) -> str:
    a, b, c = record["comparisons"]["a"], record["comparisons"]["b"], record["comparisons"]["c"]
    lines = [
        "# Turn-day labels against the month-end label (#959; H5 step 2)", "",
        f"**{LABEL.capitalize()}.** No verdict, no lockbox day scored (decision days with all five targets on or before "
        f"{record['last_day']}), and no published declaration, record or decided value moves. Every figure is read from "
        "`docs/research/turn-day-labels-959/result.json` by `scripts/turn_day_labels_959.py report`. The declaration, "
        "`metadata/turn_day_labels_959.json`, was committed before any number was computed.", "",
        "**Questions for Eleonora (not settled here).** (1) Adopt the turn label for B2, and so for scoring protocol v1's B2 and "
        "its section 13? The definition of the labels is a data meaning. (2) How does the turn label relate to the open #800 "
        "ruling, the two readings of B2's day types?", "",
        "## What was measured", "",
        "The labels are functions of the date and the market holiday table (`repo_model.turn_days`): `turn` (the last business "
        "day of a month that is not a quarter's last month and the first of the next), `quarter_end_turn` (the quarter's last "
        "business day and the first after it), `year_end` (the last business day of December and the first of January), "
        "`tax_date` as the calendar column reads it, and `ordinary`: the penultimate and run-up days return to ordinary. "
        "26 December is its own row and pools as ordinary. B2, the mean-reversion model (#686) and H6's calendar benchmark "
        "(#693) are unchanged: only the labels they group by are swapped. Skill is mean(d) / mean(S(benchmark)) with d = "
        "S(benchmark) − S(candidate), grid CRPS, positive favouring the candidate; the 90% interval is the studentized "
        f"stationary bootstrap of ruling 1 (#739), seed {record['seed']}, {record['draws']:,} draws. A group of fewer than "
        f"{record['min_days']} decision (or target) days is listed and not tested. By day type, a decision day's score is its "
        "mean over the leads whose target is of that type.", "",
        f"## (a) B2 relabelled against B2 as is", "",
        f"{a['scored_decision_days']} decision days ({a['first']} to {a['last']}); {len(a['dropped_decision_days'])} dropped for want "
        "of a sample of some lead's type in the trailing year, from every model.", "",
        "### Relabelled B2 against B2 as is (skill of the relabelled)", ""] + table(a["groups"], "B2 as is -> B2 relabelled", "decision_days", "group") + [
        "", "### Relabelled B2 against B1", ""] + table(a["groups"], "B1 -> B2 relabelled", "decision_days", "group") + [
        "", "### B2 as is against B1, for the size of the gap", ""] + table(a["groups"], "B1 -> B2 as is", "decision_days", "group") + [
        "", f"## (b) The mean-reversion level on the turn labels", "",
        f"{b['scored_decision_days']} decision days ({b['first']} to {b['last']}). Refits: {json.dumps(b['refits'])}; decision days "
        f"skipped for want of history: {json.dumps(b['skipped_decision_days'])}. The candidate is the #686 base model; the #761 variants "
        "pool by the same ordinary set and are not re-walked.", "",
        "### Level set excluding only turn days (tax dates ordinary) against as is", ""] + table(
            b["groups"], "as is -> turn days only excluded", "decision_days", "group") + [
        "", "### Level set excluding turn days and tax dates (the sensitivity) against as is", ""] + table(
            b["groups"], "as is -> turn days and tax dates excluded", "decision_days", "group") + [
        "", "## (c) H6's risk-date set re-read", "",
        "The risk-date calendar benchmark of #693 (the trailing year's spreads of the target's risk type) on the set in which the "
        "quarter-end and month-end types are replaced by the turn labels, against the same benchmark as is. The #693 type × "
        "state model is not re-run (the declaration says why). Counts of days by type, to the last scored day:", "",
        "| set | counts by type |", "|---|---|"] + [f"| {k} | {', '.join(f'{t}: {n}' for t, n in v.items())} |" for k, v in c["counts"].items()] + [
        "", f"{c['scored_decision_days']} decision days. On each set the calendar benchmark is read against B1 on that set's risk "
        "target days (the unit is the target day, as in #693):", ""]
    for set_name, s in c["sets"].items():
        lines += ["", f"### {set_name}: calendar against B1 ({s['cells']} cells, {s['target_days']} target days)", ""] + table(
            s["groups"], "B1 -> calendar", "target_days", "group")
    lines += ["", f"### Turn set against as is, on the {c['cross']['cells']} cells both call a risk date", ""] + table(
        c["cross"]["groups"], "as is -> turn set", "target_days", "group")
    lines += ["", "## What the tables show", "", reading(record), "",
              "B2 samples the trailing year, so by construction the relabelled pools are small: a year holds two `year_end` days "
              "and six `quarter_end_turn` days, against about 16 `turn` days (the as-is pools: four `quarter_end` days and about "
              "24 `month_end` days). The `year_end` rows above are scored on those two days' spreads; read them with that in mind. "
              "Whether a pooled alternative (for example `year_end` with `quarter_end_turn`) is worth a variant is Eleonora's; "
              "it is not run here.", "",
              f"Nothing here is a verdict for a hypothesis; adopting the label is Eleonora's (#959). {LABEL.capitalize()}.", ""]
    return "\n".join(lines)


def reading(record: dict) -> str:
    """The sentences that carry the figures: each is read from the record, so the page cannot drift from it."""

    a, b, c = record["comparisons"]["a"]["groups"], record["comparisons"]["b"]["groups"], record["comparisons"]["c"]

    def line(groups, name, pair, what):
        t = groups[name].get("tests", {}).get(pair)
        if t is None:
            return f"{what}: not tested."
        if "undefined" in t:
            return f"{what}: {verdict_words(t)}."
        return f"{what}: skill {pct(t['skill'])} {interval(t['skill_interval'], 100, 1)}, {verdict_words(t)}."

    lines = [
        "- " + line(a, "pooled", "B2 as is -> B2 relabelled", "(a) pooled, relabelled B2 against B2 as is"),
        "- " + line(a, "target: turn days (all three labels)", "B2 as is -> B2 relabelled", "(a) on the turn days"),
        "- " + line(a, "target: penultimate days", "B2 as is -> B2 relabelled", "(a) on the penultimate days"),
        "- " + line(b, "pooled", "as is -> turn days only excluded", "(b) pooled, the level set excluding only turn days against as is"),
        "- " + line(b, "target: turn days (all three labels)", "as is -> turn days only excluded", "(b) on the turn days"),
        "- " + line(c["sets"]["turn set"]["groups"], "pooled", "B1 -> calendar", "(c) the calendar benchmark on the turn set against B1, pooled"),
        "- " + line(c["cross"]["groups"], "pooled", "as is -> turn set", "(c) the turn set against as is on the common cells, pooled"),
    ]
    return "\n".join(lines)


def report_command(args) -> int:
    record = json.loads(args.record.read_text(encoding="utf-8"))
    RECORD.parent.mkdir(parents=True, exist_ok=True)
    RECORD.write_text(json.dumps(record, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    PAGE.write_text(render(record), encoding="utf-8")
    print("wrote", PAGE)
    return 0


def check_command(_args) -> int:
    record = json.loads(RECORD.read_text(encoding="utf-8"))
    if not PAGE.exists() or PAGE.read_text(encoding="utf-8") != render(record):
        print("the page is not what the record gives; run `report`", file=sys.stderr)
        return 1
    print("ok")
    return 0


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="command", required=True)
    run = sub.add_parser("run")
    run.add_argument("--published", type=Path, required=True)
    run.add_argument("--output", type=Path, required=True)
    run.add_argument("--draws", type=int, default=sp.DRAWS)
    run.add_argument("--processes", type=int, default=4)
    run.set_defaults(func=run_command)
    rep = sub.add_parser("report")
    rep.add_argument("record", type=Path)
    rep.set_defaults(func=report_command)
    sub.add_parser("check").set_defaults(func=check_command)
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
