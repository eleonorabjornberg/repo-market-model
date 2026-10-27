#!/usr/bin/env python3
"""15 October as a tax date: B2 and H8's calendar ranker with the alternative label, and a coupon control (#965; H5 step 2).

A development measurement, never a verdict. Every choice is in `metadata/tax_date_october_965.json`, which this script
refuses to read unless it is committed and unchanged. The labels are `repo_model.tax_date_october`; B2 is
`repo_model.protocol_benchmarks.b2_forecast` and the ranker's calendar is `repo_model.ranking.calendar`. Both are read
unchanged: B2 only groups by a different label (`tax_date_october.AlternativeLabels`), and the ranker's flag takes the
alternative's days in addition. Scored by `repo_model.scoring_protocol` (#655) at the development tier; no day after
2025-12-31 is read (`docs/decisions/lockbox.md`).

    PYTHONPATH=src python3 -m repo_model.cli build --raw-root tests/fixtures/snapshots/funding_inputs \\
        --output PUB.csv --build-cutoff 2026-09-08T21:31:42+00:00 --decision-time 16:00:00
    PYTHONPATH=src python3 -m repo_model.cli verify-panel PUB.csv --manifest metadata/funding_panel_manifest.json
    PYTHONPATH=src python3 scripts/tax_date_october_965.py run --published PUB.csv --output OUT/score.json
    python3 scripts/tax_date_october_965.py report OUT/score.json
    python3 scripts/tax_date_october_965.py check

`run` writes the record; `report` copies it to `docs/research/tax-date-october-965/result.json` and writes the page
`docs/research/tax-date-october-965-result.md` from it; `check` fails when the page is not what the record gives.
Stdlib only.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import multiprocessing
import random
import statistics
import subprocess
import sys
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


from repo_model import lockbox, protocol_benchmarks as pb, ranking, scoring_protocol as sp  # noqa: E402
from repo_model import tax_date_october as tdo  # noqa: E402
from repo_model.baseline import panel_sha256  # noqa: E402
from repo_model.data import audit_panel, load_daily_panel  # noqa: E402
from repo_model.evaluation_splits import load_split_declaration  # noqa: E402
from repo_model.metrics import _quantile, stationary_bootstrap_indices  # noqa: E402
from repo_model.splits import LookAheadError, SplitError  # noqa: E402

s634 = _load("spread_distribution_634")
s694 = _load("ranking_694")

DECLARATION = REPO / "metadata" / "tax_date_october_965.json"
SPLITS = REPO / "metadata" / "evaluation_splits.json"
SOURCES = REPO / "metadata" / "sources.json"
RESEARCH = REPO / "docs" / "research"
RECORD = RESEARCH / "tax-date-october-965" / "result.json"
PAGE = RESEARCH / "tax-date-october-965-result.md"
SEED = 965
LAST_DAY = date(2025, 12, 31)
DECISION_TIME = time(16, 0)
MIN_DAYS = 20
LEVEL = sp.ALPHA
HORIZONS = sp.HORIZONS
LABEL = "development data, not a verdict"
RANKER_BLOCK = 20.0
METRICS = (("crps", sp.grid_crps, "grid CRPS"), ("twcrps", sp.upper_tail_twcrps, "upper-tail twCRPS"))
ALTERNATIVES = (("october", "B2 october"), ("control", "B2 control"))


# -- the declaration and the scope ---------------------------------------------------------------------------------


def committed_declaration(path: Path = DECLARATION) -> dict:
    """The declaration, refused unless it is committed and unchanged since `HEAD`."""

    relative = str(path.resolve().relative_to(REPO))
    dirty = subprocess.run(["git", "status", "--porcelain", "--", relative], cwd=REPO, capture_output=True, text=True,
                           check=True).stdout.strip()
    if dirty:
        raise SystemExit(f"{relative} is not committed ({dirty}); a declaration is made before any score")
    return json.loads(path.read_text(encoding="utf-8"))


def require_scored_days(days) -> None:
    """Refuse a day after the declared last day and a locked day.

    Raises:
        LookAheadError: a day after 2025-12-31 or in a locked tier.
    """

    days = list(days)
    for day in sorted(days):
        if day > LAST_DAY:
            raise LookAheadError(f"{day} is after {LAST_DAY}, the last day #965 scores; the declaration admits no later day")
    lockbox.require_unlocked(days, where="scripts/tax_date_october_965")


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


def percentile_interval(differences: Sequence[float], draws: int, block: float = 10.0) -> List[float]:
    """The unstudentized 90% percentile interval of the mean of `differences`, for a group the scorer cannot studentize
    (the scorers score alike on nearly every day of it): the same stationary bootstrap, without the studentization."""

    rng = random.Random(SEED)
    n = len(differences)
    means = sorted(sum(differences[j] for j in stationary_bootstrap_indices(n, block, rng)) / n for _ in range(draws))
    return [_quantile(means, LEVEL), _quantile(means, 1.0 - LEVEL)]


_SERIES: Dict[str, Dict[str, Dict[date, float]]] = {}
DRAWS = [sp.DRAWS]


def run_test(task):
    """(key, group, [(benchmark, candidate)...], days) -> (key, group, {pair: row})."""

    key, group, pairs, days = task
    series = _SERIES[key]
    out = {}
    for b, c in pairs:
        benchmark, candidate = {d: series[b][d] for d in days}, {d: series[c][d] for d in days}
        try:
            out[f"{b} -> {c}"] = row_of(sp.paired_test(benchmark, candidate, seed=SEED, draws=DRAWS[0]))
        except sp.ProtocolError as error:
            # d is zero on every day (identical forecasts), or a benchmark scores zero: say so, with the means
            mean_b, mean_c = sum(benchmark.values()) / len(days), sum(candidate.values()) / len(days)
            row = {"undefined": str(error), "days": len(days), "benchmark_mean": mean_b, "candidate_mean": mean_c,
                   "difference": mean_b - mean_c}
            if "long-run variance" in str(error):
                row["difference_interval"] = percentile_interval([benchmark[d] - candidate[d] for d in days], DRAWS[0])
            out[f"{b} -> {c}"] = row
    return key, group, out


def run_tests(tasks: Sequence[tuple], processes: int) -> Dict[Tuple[str, str], dict]:
    context = multiprocessing.get_context("fork")
    with context.Pool(processes) as pool:
        done = pool.map(run_test, tasks, chunksize=1)
    return {(key, group): rows for key, group, rows in done}


# -- the panel and its groups --------------------------------------------------------------------------------------


class Panel:
    """The published panel, its calendar and the three label sets."""

    def __init__(self, path: Path):
        self.rows = load_daily_panel(path)
        audit_panel(self.rows)
        self.dates = [r.date for r in self.rows]
        self.position = {d: i for i, d in enumerate(self.dates)}
        self.values = {r.date: r.values for r in self.rows}
        self.outcomes = {r.date: r.spread_bps for r in self.rows}
        self.splits = load_split_declaration(SPLITS)
        self.registry = json.loads(SOURCES.read_text(encoding="utf-8"))
        self.labels = {"as is": self.splits, **{w: tdo.AlternativeLabels(self.splits, which=w) for w, _ in ALTERNATIVES}}
        self.settings = dict(registry=self.registry, decision_time=DECISION_TIME)

    def target(self, decision: date, lead: int) -> date:
        return self.dates[self.position[decision] + lead]


def target_groups(panel: Panel) -> Dict[str, Callable[[date], bool]]:
    """The groups by the target day, each a predicate on the target day; they partition the days."""

    def published(t: date) -> bool:
        return panel.splits.reporting_day_type(t, panel.values[t]) == "tax_date"

    return {
        "october window": tdo.october_window,
        "control window": tdo.control_window,
        "tax_date as is": published,
        "other days": lambda t: not (tdo.october_window(t) or tdo.control_window(t) or published(t)),
    }


def decision_groups(days: Sequence[date], cells: Mapping[str, Mapping[Tuple[date, int], float]], panel: Panel):
    """Per group: (decision days, number of target cells, {model: {day: score}}), for the pooled days, regimes and targets."""

    models = list(cells)
    out = {}
    pooled = {m: s634.day_means(cells[m], lambda d, h: True) for m in models}
    out["pooled"] = (sorted(days), len(days) * len(HORIZONS), pooled)
    for label in panel.splits.regime_labels:
        group = [d for d in days if panel.splits.regime(d) == label]
        out[f"regime {label}"] = (group, len(group) * len(HORIZONS), pooled)
    for name, include in target_groups(panel).items():
        series = {m: s634.day_means(cells[m], lambda d, h, include=include: include(panel.target(d, h))) for m in models}
        group = sorted(set.intersection(*(set(s) for s in series.values())))
        count = sum(1 for d in group for h in HORIZONS if include(panel.target(d, h)))
        out[f"target: {name}"] = (group, count, series)
    return out


def summarise_groups(key: str, groups, pairs, tasks: list, store: dict) -> dict:
    """The group table of a comparison with its tests queued; a group of fewer than `MIN_DAYS` days is listed, not tested."""

    table = {}
    for name, (days, cells, series) in groups.items():
        store[f"{key}|{name}"] = {m: dict(v) for m, v in series.items()}
        table[name] = {"decision_days": len(days), "target_cells": cells,
                       "means": {m: (sum(s[d] for d in days) / len(days) if days else None) for m, s in series.items()},
                       "tested": len(days) >= MIN_DAYS}
        if len(days) >= MIN_DAYS:
            tasks.append((key, name, pairs, tuple(days)))
    return table


# -- (a): B2 --------------------------------------------------------------------------------------------------------


def offered_days(panel: Panel, lead: int) -> List[date]:
    days = [d for i, d in enumerate(panel.dates) if i + lead < len(panel.dates) and panel.dates[i + lead] <= LAST_DAY]
    require_scored_days(days + [panel.dates[panel.position[d] + lead] for d in days])
    return days


def build_a(panel: Panel, offered: Sequence[date]):
    forecasts: Dict[str, dict] = {"B1": {}, "B2 as is": {}, **{name: {} for _, name in ALTERNATIVES}}
    dropped = []
    for day in offered:
        i = panel.position[day]
        try:
            built = {"B1": pb.b1_forecast(panel.rows, i, **panel.settings),
                     "B2 as is": pb.b2_forecast(panel.rows, i, splits=panel.splits, **panel.settings)}
            for which, name in ALTERNATIVES:
                built[name] = pb.b2_forecast(panel.rows, i, splits=panel.labels[which], **panel.settings)
        except (sp.ProtocolError, SplitError):
            dropped.append(day.isoformat())
            continue
        for name, forecast in built.items():
            forecasts[name][day] = forecast
    return forecasts, dropped


def window_facts(panel: Panel) -> dict:
    """The windows as a calendar of the panel, to the last scored day: no score."""

    def window_rows(inside: Callable[[date], bool]) -> List[int]:
        return [i for i, d in enumerate(panel.dates) if d <= LAST_DAY and inside(d)]

    out = {}
    groups = {name: (lambda d, inside=inside: inside(d)) for name, inside in target_groups(panel).items()}
    for name, inside in groups.items():
        rows = window_rows(inside)
        spreads = [panel.rows[i].spread_bps for i in rows if panel.rows[i].spread_bps is not None]
        out[name] = {"panel_days": len(rows), "pressure_days": sum(1 for s in spreads if s > 5.0),
                     "mean_spread_bp": statistics.fmean(spreads) if spreads else None,
                     "median_spread_bp": statistics.median(spreads) if spreads else None}
    october = {}
    for year in range(2018, 2026):
        days = [d for d in panel.dates if d.year == year and tdo.october_window(d)]
        october[str(year)] = [{"day": d.isoformat(), "spread_bp": panel.outcomes[d]} for d in days]
    out["october_by_year"] = october
    coupons = {}
    for which, months in (("october", (10,)), ("control", tdo.CONTROL_MONTHS)):
        positive = total = 0
        for year in range(2018, 2026):
            for month in months:
                day = tdo.october_deadline(year) if which == "october" else tdo.control_deadline(year, month)
                if day in panel.values and day <= LAST_DAY:
                    total += 1
                    positive += float(panel.values[day].get("treasury_settlement_coupons") or 0.0) > 0.0
        coupons[which] = {"deadlines_on_the_panel": total, "with_a_coupon_settlement": positive}
    out["coupon_settlement_on_the_deadline"] = coupons
    return out


# -- (b): the ranker -----------------------------------------------------------------------------------------------


def ranker_scores(panel: Panel, i: int) -> Dict[str, List[float]]:
    """The calendar ranker's flags per lead as is and with each alternative's days added."""

    base = ranking.calendar(panel.rows, i, ranking.LEADS, **panel.settings)
    out = {"calendar": base}
    for which, _ in ALTERNATIVES:
        out[f"calendar {which}"] = [1.0 if flag or tdo.extra_risk_flag(panel.dates[i + h], which) else 0.0
                                    for flag, h in zip(base, ranking.LEADS)]
    return out


def build_b(panel: Panel, days: Sequence[date], draws: int) -> dict:
    lead = max(ranking.LEADS)
    days = [d for d in days if panel.position[d] + lead < len(panel.dates) and panel.dates[panel.position[d] + lead] <= LAST_DAY]
    ranking.require_scored_days(days)
    ranking.require_scored_days(panel.dates[panel.position[d] + h] for d in days for h in ranking.LEADS)
    names = ["calendar"] + [f"calendar {w}" for w, _ in ALTERNATIVES]
    flags = {d: ranking.realised(panel.rows, panel.position[d]) for d in days}
    scores = {d: ranker_scores(panel, panel.position[d]) for d in days}
    cells = {n: {k: {m: {} for m in s694.METRICS} for k in ranking.TOP_K} for n in names}
    for d in days:
        for n in names:
            got = ranking.window_metrics(scores[d][n], flags[d], ranking.TOP_K, "first")
            for k in ranking.TOP_K:
                cells[n][k]["precision"][d] = got[k]["precision"]
                cells[n][k]["recall"][d] = got[k]["recall"]
    pressured = [d for d in days if sum(flags[d])]

    def holds(d: date, inside: Callable[[date], bool]) -> bool:
        return any(inside(panel.dates[panel.position[d] + h]) for h in ranking.LEADS)

    groups = {"pooled": list(days)}
    for label in panel.splits.regime_labels:
        groups[f"regime {label}"] = [d for d in days if panel.splits.regime(d) == label]
    groups["windows holding an October window day"] = [d for d in days if holds(d, tdo.october_window)]
    groups["windows holding a control window day"] = [d for d in days if holds(d, tdo.control_window)]
    groups["other windows"] = [d for d in days if not holds(d, tdo.october_window) and not holds(d, tdo.control_window)]
    out = {"scored_decision_days": len(days), "first": days[0].isoformat(), "last": days[-1].isoformat(),
           "windows_with_a_pressure_day": len(pressured), "block_length": RANKER_BLOCK, "groups": {}}
    for name, members in groups.items():
        hot = [d for d in members if sum(flags[d])]
        entry = {"decision_days": len(members), "days_with_a_pressure_day": len(hot), "paired": {}}
        for which, _ in ALTERNATIVES:
            candidate = f"calendar {which}"
            for k in ranking.TOP_K:
                for metric, subset in (("precision", members), ("recall", hot)):
                    label = f"{candidate} vs calendar: {metric}@{k}"
                    benchmark_series = {d: cells["calendar"][k][metric][d] for d in subset}
                    candidate_series = {d: cells[candidate][k][metric][d] for d in subset}
                    if len(subset) < MIN_DAYS:
                        entry["paired"][label] = {"days": len(subset), "note": f"fewer than {MIN_DAYS} days; not tested"}
                    elif benchmark_series == candidate_series:
                        entry["paired"][label] = {"days": len(subset), "identical": True,
                                                  "benchmark_mean": s694.mean(list(benchmark_series.values()))}
                    else:
                        entry["paired"][label] = s694.paired({"calendar": benchmark_series}, candidate_series, subset, draws,
                                                             block=RANKER_BLOCK)["calendar"]
        out["groups"][name] = entry
    out["means"] = {n: {str(k): {"precision": s694.mean([cells[n][k]["precision"][d] for d in days]),
                                 "recall": s694.mean([cells[n][k]["recall"][d] for d in pressured])} for k in ranking.TOP_K}
                    for n in names}
    return out


# -- run -----------------------------------------------------------------------------------------------------------


def run_command(args) -> int:
    committed_declaration()
    DRAWS[0] = args.draws
    panel = Panel(args.published)
    offered = offered_days(panel, max(HORIZONS))
    record: dict = {"issue": 965, "label": LABEL, "declaration": str(DECLARATION.relative_to(REPO)),
                    "panel_sha256": panel_sha256(args.published), "seed": SEED, "draws": args.draws,
                    "last_day": LAST_DAY.isoformat(), "decision_days_offered": len(offered), "min_days": MIN_DAYS,
                    "windows": window_facts(panel), "comparisons": {}}
    tasks: list = []
    store: dict = {}

    forecasts, dropped = build_a(panel, offered)
    days = sorted(set.intersection(*(set(f) for f in forecasts.values())))
    pairs = [("B2 as is", name) for _, name in ALTERNATIVES] + [("B1", "B2 as is")] + [("B1", name) for _, name in ALTERNATIVES]
    record["comparisons"]["a"] = {"dropped_decision_days": dropped, "scored_decision_days": len(days),
                                  "first": days[0].isoformat(), "last": days[-1].isoformat(), "pairs": [list(p) for p in pairs],
                                  "metrics": {}}
    for key, score, title in METRICS:
        cells = {n: s634.cell_scores({d: f[d] for d in days}, panel.outcomes, panel.dates, score) for n, f in forecasts.items()}
        groups = decision_groups(days, cells, panel)
        record["comparisons"]["a"]["metrics"][key] = {"title": title,
                                                      "groups": summarise_groups(f"a-{key}", groups, pairs, tasks, store)}
    print(f"(a) {len(days)} decision days; {len(tasks)} tests queued", flush=True)

    record["comparisons"]["b"] = build_b(panel, days, args.draws)
    print(f"(b) {record['comparisons']['b']['scored_decision_days']} decision days", flush=True)

    global _SERIES
    _SERIES = {f"{k}|{g}": store[f"{k}|{g}"] for k, g, _, _ in tasks}
    results = run_tests([(f"{k}|{g}", g, p, d) for k, g, p, d in tasks], args.processes)
    for key, group, _, _ in tasks:
        metric = key.split("-", 1)[1]
        record["comparisons"]["a"]["metrics"][metric]["groups"][group]["tests"] = results[(f"{key}|{group}", group)]
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(record, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    print("wrote", args.output)
    return 0


# -- the page ------------------------------------------------------------------------------------------------------


def pct(value: float) -> str:
    return f"{100 * value:+.1f}%"


def interval(pair: Sequence[float], scale: float = 1.0, digits: int = 3) -> str:
    return f"[{pair[0] * scale:+.{digits}f}, {pair[1] * scale:+.{digits}f}]"


def table(rows: Mapping[str, dict], pair: str, count_key: str) -> List[str]:
    lines = [f"| group | {count_key.replace('_', ' ')} | benchmark | candidate | skill [90%] | mean d [90%] | reading |",
             "|---|---|---|---|---|---|---|"]
    for name, g in rows.items():
        if g[count_key] == 0:
            continue
        test = g.get("tests", {}).get(pair)
        if test is None:
            lines.append(f"| {name} | {g[count_key]} | | | not tested (fewer than {MIN_DAYS}) | | |")
        elif "undefined" in test:
            spread = f" {interval(test['difference_interval'], 1, 4)} (percentile, unstudentized)" if "difference_interval" in test else ""
            lines.append(f"| {name} | {g[count_key]} | {test['benchmark_mean']:.3f} | {test['candidate_mean']:.3f} | "
                         f"undefined: {test['undefined']} | {test['difference']:+.4f}{spread} | {verdict_words(test)} |")
        else:
            lines.append(f"| {name} | {g[count_key]} | {test['benchmark_mean']:.3f} | {test['candidate_mean']:.3f} | "
                         f"{pct(test['skill'])} {interval(test['skill_interval'], 100, 1)} | {test['difference']:+.4f} "
                         f"{interval(test['difference_interval'], 1, 4)} | {verdict_words(test)} |")
    return lines


def ranker_reading(entry: dict) -> str:
    if entry.get("identical"):
        return "identical by construction"
    if "note" in entry:
        return entry["note"]
    if "undefined" in entry:
        return "undefined"
    low, high = entry["gain_interval"]
    return "candidate better" if low > 0.0 else "candidate worse" if high < 0.0 else "no difference"


def ranker_table(groups: Mapping[str, dict], candidate: str) -> List[str]:
    heads = [f"{m}@{k}" for k in ranking.TOP_K for m in ("precision", "recall")]
    lines = ["| group | decision days | " + " | ".join(f"{h} gain [90%]" for h in heads) + " |", "|---|---|" + "---|" * len(heads)]
    for name, g in groups.items():
        if g["decision_days"] == 0:
            continue
        cells = []
        for h in heads:
            entry = g["paired"].get(f"{candidate} vs calendar: {h.replace('@', '@')}", {})
            if entry.get("identical"):
                cells.append(f"identical ({entry['benchmark_mean']:.3f})")
            elif "gain" in entry:
                cells.append(f"{entry['gain']:+.3f} {interval(entry['gain_interval'], 1, 3)} {ranker_reading(entry)}")
            else:
                cells.append(entry.get("note", "undefined"))
        lines.append(f"| {name} | {g['decision_days']} (pressure: {g['days_with_a_pressure_day']}) | " + " | ".join(cells) + " |")
    return lines


def line(groups, name, pair, what):
    t = groups[name].get("tests", {}).get(pair)
    if t is None:
        return f"{what}: not tested."
    if "undefined" in t:
        return f"{what}: {verdict_words(t)}."
    return f"{what}: skill {pct(t['skill'])} {interval(t['skill_interval'], 100, 1)}, {verdict_words(t)}."


def reading(record: dict) -> str:
    metrics = record["comparisons"]["a"]["metrics"]
    lines = []
    for key, m in metrics.items():
        for _, name in ALTERNATIVES:
            pair = f"B2 as is -> {name}"
            lines.append("- " + line(m["groups"], "pooled", pair, f"({m['title']}) pooled, {name} against B2 as is"))
            target = "target: october window" if name == "B2 october" else "target: control window"
            lines.append("- " + line(m["groups"], target, pair, f"({m['title']}) on its own window, {name} against B2 as is"))
    years = record["windows"]["october_by_year"]
    hot = [y for y, entries in years.items() if any(e["spread_bp"] > 5.0 for e in entries)]
    lines.append(f"- The October window holds a pressure day (> +5 bp) in {len(hot)} of its {len(years)} years ({', '.join(hot)}); "
                 "its gain rests on those years.")
    b = record["comparisons"]["b"]["groups"]
    for which, _ in ALTERNATIVES:
        for h in ("precision@5", "recall@5"):
            entry = b["pooled"]["paired"].get(f"calendar {which} vs calendar: {h}", {})
            if "gain" in entry:
                lines.append(f"- (b) pooled, calendar ranker {which} against as is, {h}: gain {entry['gain']:+.4f} "
                             f"{interval(entry['gain_interval'], 1, 4)}, {ranker_reading(entry)}.")
    return "\n".join(lines)


def render(record: dict) -> str:
    a, b, w = record["comparisons"]["a"], record["comparisons"]["b"], record["windows"]
    lines = [
        "# 15 October as a tax date (#965; H5 step 2, H6 step 1, H8)", "",
        f"**{LABEL.capitalize()}.** No verdict, no lockbox day scored (decision days with all targets on or before "
        f"{record['last_day']}), and no published declaration, record or decided value moves. Every figure is read from "
        "`docs/research/tax-date-october-965/result.json` by `scripts/tax_date_october_965.py report`. The declaration, "
        "`metadata/tax_date_october_965.json`, was committed before any number was computed.", "",
        "**Questions for Eleonora (not settled here).** (1) Adopt 15 October in the `tax_date` definition? The definition is a "
        "data meaning (as #538 was), and adopting it for B2 is a section 13 question. (2) If the coupon control below matches "
        "the October result, should the label be a coupon-settlement label and not a tax-date label?", "",
        "## What was measured", "",
        "The alternative adds the 15th of October (rolled forward off weekends and DC holidays) and the two market days after it "
        "to the `tax_date` type (`repo_model.tax_date_october`); the published column is not changed. The control adds, in the "
        "same shape, the 15th of the months the published column leaves alone (January, February, March, May, July, August, "
        "November), rolled on the market calendar, so that a gain in October that the control also shows is the mid-month "
        "coupon settlement and not the tax deadline. B2 and H8's calendar ranker are unchanged apart from that label. Skill is "
        "mean(d) / mean(S(benchmark)) with d = S(benchmark) − S(candidate), positive favouring the candidate; the 90% interval "
        f"is the studentized stationary bootstrap of ruling 1 (#739), seed {record['seed']}, {record['draws']:,} draws. A group "
        f"of fewer than {record['min_days']} decision days is listed and not tested. By target group, a decision day's score is "
        "its mean over the leads whose target is in the group.", "",
        "## The windows as a calendar (no score)", "",
        "| target days to the last scored day | panel days | pressure days (> +5 bp) | mean spread (bp) | median (bp) |",
        "|---|---|---|---|---|"]
    for name in ("october window", "control window", "tax_date as is", "other days"):
        f = w[name]
        lines.append(f"| {name} | {f['panel_days']} | {f['pressure_days']} | {f['mean_spread_bp']:.2f} | {f['median_spread_bp']:.2f} |")
    lines += ["", "The October window by year (SOFR − IORB, bp):", ""]
    lines += [f"- {year}: " + ", ".join(f"{e['day']} {e['spread_bp']:+.1f}" for e in entries) for year, entries in w["october_by_year"].items()]
    c = w["coupon_settlement_on_the_deadline"]
    lines += ["", f"A coupon settlement was positive on the deadline day for {c['october']['with_a_coupon_settlement']} of "
              f"{c['october']['deadlines_on_the_panel']} October deadlines and for {c['control']['with_a_coupon_settlement']} of "
              f"{c['control']['deadlines_on_the_panel']} control deadlines (`treasury_settlement_coupons` on the rolled 15th).", "",
              f"## (a) B2 with the alternative label against B2 as is", "",
              f"{a['scored_decision_days']} decision days ({a['first']} to {a['last']}); {len(a['dropped_decision_days'])} dropped for "
              "want of a sample of some lead's type in the trailing year, from every model."]
    for key, m in a["metrics"].items():
        for _, name in ALTERNATIVES:
            lines += ["", f"### {m['title']}: {name} against B2 as is (skill of {name})", ""] + table(m["groups"], f"B2 as is -> {name}", "decision_days")
        lines += ["", f"### {m['title']}: B2 as is against B1, for the size of the gap", ""] + table(m["groups"], "B1 -> B2 as is", "decision_days")
    lines += ["", f"## (b) H8's calendar ranker with the window in its set", "",
              f"{b['scored_decision_days']} decision days ({b['first']} to {b['last']}), 20 leads each; precision over all windows and "
              f"recall over the {b['windows_with_a_pressure_day']} windows with a pressure day; ties broken by date; mean block "
              f"{b['block_length']:.0f}; the gain is the alternative's less the ranker as is (positive favours the alternative). "
              "The studentized scorer is used where it is defined, the percentile interval of the same draws otherwise."]
    for which, _ in ALTERNATIVES:
        lines += ["", f"### Calendar ranker with the {which} window against as is", ""] + ranker_table(b["groups"], f"calendar {which}")
    lines += ["", "## What the tables show", "", reading(record), "",
              f"Nothing here is a verdict for a hypothesis; adopting the label is Eleonora's (#965). {LABEL.capitalize()}.", ""]
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


from repo_model import turn_days  # noqa: E402


@turn_days.with_legacy_flag
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
