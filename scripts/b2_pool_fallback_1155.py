"""B2's thin-pool fallback, read on the development data (#1155; H5 step 2, benchmarks; calendar first).

A development study, never a verdict. It writes JSON and Markdown to the paths it is given and nothing into `docs/runs/`.
Every choice is in `metadata/b2_pool_fallback_1155.json`, which this script refuses to read unless it is committed and
unchanged. The arms are B1, B1' (`repo_model.b1_calendar`), B2 as the protocol scores it on the legacy month-end type and on
the turn labels of the draft of #1135 (`repo_model.turn_days.TurnLabels`; that record is not in force), and B2 with the
fallback of the draft of #1155 (`repo_model.b2_pool`) at three pool minimums. Scored decision days are those whose five
targets are on or before 2025-12-31; no later day is read and no locked day is scored (`docs/decisions/lockbox.md`).

Measures: the pool each target type reads; the coverage of the 50% and 90% bands and the exceedance of q95, under both hit
rules (the hit rule is Eleonora's open question, #993), pooled over the five leads, pooled, by regime and by pressure-day type;
grid CRPS and upper-tail twCRPS paired against B2 without the fallback on the studentized stationary bootstrap of ruling 1
(#739). Commands, from a clone of the branch (the score takes minutes):

    PYTHONPATH=src python3 -m repo_model.cli build --raw-root tests/fixtures/snapshots/funding_inputs \\
        --output PUB.csv --build-cutoff 2026-09-08T21:31:42+00:00 --decision-time 16:00:00
    PYTHONPATH=src python3 -m repo_model.cli verify-panel PUB.csv --manifest metadata/funding_panel_manifest.json
    PYTHONPATH=src python3 scripts/b2_pool_fallback_1155.py score --panel PUB.csv \\
        --output docs/research/b2-pool-fallback-1155/result.json
    PYTHONPATH=src python3 scripts/b2_pool_fallback_1155.py page \\
        --score docs/research/b2-pool-fallback-1155/result.json --output docs/research/b2-pool-fallback-1155-result.md

Stdlib only.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import multiprocessing
import sys
from datetime import date
from pathlib import Path
from typing import Dict, List, Mapping, Optional, Sequence, Tuple

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))


def _load(name: str):
    loaded = sys.modules.get(name)
    if loaded is not None and Path(getattr(loaded, "__file__", "")) == REPO / "scripts" / f"{name}.py":
        return loaded
    spec = importlib.util.spec_from_file_location(name, REPO / "scripts" / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


from repo_model import b1_calendar as b1c  # noqa: E402
from repo_model import b2_pool  # noqa: E402
from repo_model import coverage_tests as ct  # noqa: E402
from repo_model import protocol_benchmarks as pb, scoring_protocol as sp, turn_days  # noqa: E402
from repo_model.baseline import panel_sha256  # noqa: E402
from repo_model.data import load_daily_panel  # noqa: E402
from repo_model.evaluation_splits import load_split_declaration  # noqa: E402

s686 = _load("spread_mean_reversion_686")
s761 = _load("spread_mr_variants_761")

DECLARATION = REPO / "metadata" / "b2_pool_fallback_1155.json"
SEED = 1155
LAST_DAY = s686.LAST_DAY
DECISION_TIME = s686.DECISION_TIME
MIN_GROUP_DAYS = s686.MIN_GROUP_DAYS
POOL_MINS = (10, 20, 30)
#: The first scored decision day is the 251st panel row, so B2's trailing year is a whole year of rows.
WARM_UP_ROWS = 250
B1, B1P, B2_LEGACY, B2_TURN = "B1", "B1_prime", "B2_legacy", "B2_turn"
FALLBACK = {f"B2_pool{n}": n for n in POOL_MINS}
MODELS: Tuple[str, ...] = (B1, B1P, B2_LEGACY, B2_TURN) + tuple(FALLBACK)
#: [candidate, benchmark]; positive skill favours the candidate.
PAIRS = tuple((name, B2_TURN) for name in FALLBACK) + (
    (B2_TURN, B2_LEGACY), ("B2_pool10", B1), ("B2_pool10", B1P))
METRICS = (("grid_crps", sp.grid_crps), ("upper_tail_twcrps", sp.upper_tail_twcrps))
#: kind -> (lower level, upper level, nominal miss rate). `q95` has no lower level.
KINDS: Dict[str, Tuple[Optional[float], float, float]] = {
    "q95": (None, 0.95, 0.05), "band90": (0.05, 0.95, 0.10), "band50": (0.25, 0.75, 0.50)}
ORDER_REGIME = ["2018-19", "2020", "2021-23", "2024", "2025-26"]
ORDER_TYPE = [turn_days.YEAR_END, turn_days.QUARTER_END_TURN, turn_days.TURN, turn_days.TAX_DATE, turn_days.ORDINARY]


class Cached:
    """A `reporting_day_type` over `turn_days.TurnLabels` (or the legacy type) that remembers each date's label."""

    def __init__(self, inner):
        self._inner, self._seen = inner, {}

    def reporting_day_type(self, when: date, values) -> str:
        if when not in self._seen:
            self._seen[when] = self._inner.reporting_day_type(when, values)
        return self._seen[when]


class Legacy:
    """`SplitDeclaration.reporting_day_type` itself, so the reference stays legacy whether or not #1135 is in force."""

    def __init__(self, splits):
        self._splits = splits

    def reporting_day_type(self, when: date, values) -> str:
        return self._splits.reporting_day_type(when, values)


def committed_declaration() -> dict:
    return s686.committed_declaration(DECLARATION)


# -- the frame -----------------------------------------------------------------------------------------------------


def build_frame(panel, splits, registry):
    """The decision days on which every arm is defined, and each arm's forecast on them."""

    labels = Cached(turn_days.TurnLabels(splits))
    legacy = Cached(Legacy(splits))
    frame = s686.Frame(panel, splits, registry, {})
    frame.day_type = lambda day: labels.reporting_day_type(day, frame.values[day])
    offered = [d for i, d in enumerate(frame.dates)
               if i >= WARM_UP_ROWS and i + max(sp.HORIZONS) < len(panel) and frame.dates[i + max(sp.HORIZONS)] <= LAST_DAY]
    s686.require_scored_days(offered)
    base = dict(registry=registry, decision_time=DECISION_TIME)
    forecasts: Dict[str, Dict[date, dict]] = {m: {} for m in MODELS}
    used: Dict[str, Dict[date, dict]] = {m: {} for m in FALLBACK}
    dropped: Dict[str, List[str]] = {"B2_turn_empty_pool": [], "B1_or_B1_prime_no_history": []}
    for day in offered:
        i = frame.position[day]
        try:
            two = pb.b2_forecast(panel, i, splits=labels, **base)
        except sp.ProtocolError:
            dropped["B2_turn_empty_pool"].append(day.isoformat())
            continue
        try:
            one = pb.b1_forecast(panel, i, **base)
            prime = b1c.b1_calendar_forecast(panel, i, splits=labels, **base)
        except sp.ProtocolError:
            dropped["B1_or_B1_prime_no_history"].append(day.isoformat())
            continue
        forecasts[B1][day], forecasts[B1P][day], forecasts[B2_TURN][day] = one, prime, two
        forecasts[B2_LEGACY][day] = pb.b2_forecast(panel, i, splits=legacy, **base)
        for name, n in FALLBACK.items():
            record: Dict[int, Tuple[str, int]] = {}
            forecasts[name][day] = b2_pool.b2_fallback_forecast(panel, i, splits=labels, pool_min=n, used=record, **base)
            used[name][day] = record
    frame.days = [d for d in offered if d in forecasts[B2_TURN] and d in forecasts[B1]]
    frame.forecasts = forecasts
    frame.pools = used
    notes = {"decision_days_offered": len(offered), "scored_decision_days": len(frame.days), "dropped": dropped,
             "first": frame.days[0].isoformat(), "last": frame.days[-1].isoformat(),
             "last_target": frame.target(frame.days[-1], max(sp.HORIZONS)).isoformat()}
    return frame, notes


def pool_summary(frame) -> dict:
    """Per arm and target type: the cells, the share on each pool, and the smallest and largest pool read."""

    out: dict = {}
    for name in FALLBACK:
        table: dict = {}
        for day in frame.days:
            for h, (pool, rows) in frame.pools[name][day].items():
                kind = frame.day_type(frame.target(day, h))
                cell = table.setdefault(kind, {"cells": 0, "pools": {}, "rows_min": rows, "rows_max": rows})
                cell["cells"] += 1
                cell["pools"][pool] = cell["pools"].get(pool, 0) + 1
                cell["rows_min"], cell["rows_max"] = min(cell["rows_min"], rows), max(cell["rows_max"], rows)
        out[name] = table
    return out


# -- the hit sequences ---------------------------------------------------------------------------------------------


def hit_sequence(outcomes: Sequence[float], laws: Sequence[Sequence[float]], kind: str, rule: str) -> List[int]:
    """The exceedance of q95, or the miss of a band, under `rule` (`coverage_tests.HIT_RULES`); the lower side is the mirror."""

    low, high, _ = KINDS[kind]
    upper = ct.hit_sequence(outcomes, [q[sp.GRID.index(high)] for q in laws], rule=rule)
    if low is None:
        return upper
    lower = ct.hit_sequence([-y for y in outcomes], [-q[sp.GRID.index(low)] for q in laws], rule=rule)
    return [max(a, b) for a, b in zip(lower, upper)]


def coverage_row(sequence: Sequence[int], p: float) -> dict:
    row = {"n": len(sequence), "hits": sum(sequence), "rate": sum(sequence) / len(sequence), "kupiec_p": None}
    if len(sequence) >= MIN_GROUP_DAYS:
        row["kupiec_p"] = ct.kupiec(sequence, p).p_value
    return row


def hit_tables(frame) -> dict:
    """Per arm, hit rule and kind, the miss/exceedance rate of the cells (day, lead), pooled, by regime and by type."""

    cells = [(d, h, frame.target(d, h)) for d in frame.days for h in sp.HORIZONS]
    outcomes = [frame.outcome[t] for _, _, t in cells]
    groups: Dict[str, List[int]] = {"pooled": list(range(len(cells)))}
    for i, (_, _, t) in enumerate(cells):
        groups.setdefault(f"regime/{frame.regime(t)}", []).append(i)
        groups.setdefault(f"pressure_day_type/{frame.day_type(t)}", []).append(i)
    out: dict = {"kinds": {k: v[2] for k, v in KINDS.items()}, "rules": list(ct.HIT_RULES), "rows": {}}
    for model in MODELS:
        laws = [frame.forecasts[model][d][h] for d, h, _ in cells]
        for rule in ct.HIT_RULES:
            for kind, (_, _, p) in KINDS.items():
                sequence = hit_sequence(outcomes, laws, kind, rule)
                out["rows"].setdefault(model, {}).setdefault(rule, {})[kind] = {
                    name: coverage_row([sequence[i] for i in rows], p) for name, rows in sorted(groups.items())}
    return out


# -- the paired tests ----------------------------------------------------------------------------------------------

_STATE: dict = {}


def _task(job):
    key, metric, candidate, benchmark, days = job
    series = _STATE["series"][(key[0], metric)]
    row = s761.run_pairs({benchmark: series[benchmark]}, series[candidate], days, seed=SEED, draws=_STATE["draws"])[benchmark]
    return key, metric, candidate, benchmark, row


def run_jobs(jobs, workers: int):
    if workers <= 1:
        return [_task(j) for j in jobs]
    with multiprocessing.get_context("fork").Pool(workers) as pool:
        return pool.map(_task, jobs, chunksize=1)


def score(args) -> int:
    committed_declaration()
    panel_path = Path(args.panel)
    panel = load_daily_panel(panel_path)
    splits = load_split_declaration(s686.SPLITS)
    registry = json.loads(s686.SOURCES.read_text(encoding="utf-8"))
    frame, notes = build_frame(panel, splits, registry)
    days = frame.days
    cells = {(label, m): s686.cell_scores(frame, m, fn) for label, fn in METRICS for m in MODELS}
    for label, fn in METRICS:
        for m in MODELS:
            official = sp.day_scores(frame.forecasts[m], frame.outcome, frame.dates, score=fn)
            mine = s686.by_decision(cells[(label, m)])
            if set(official) != set(mine) or any(abs(official[d] - mine[d]) > 1e-9 for d in mine):
                raise SystemExit(f"{label} of {m}: the cell means differ from scoring_protocol.day_scores")
    series = {}
    for label, _ in METRICS:
        series[("decision", label)] = {m: s686.by_decision(cells[(label, m)]) for m in MODELS}
        series[("target", label)] = {m: s686.by_target(frame, cells[(label, m)]) for m in MODELS}
    targets = sorted({frame.target(d, h) for d in days for h in sp.HORIZONS})
    groups: Dict[Tuple[str, str], Tuple[str, List[date]]] = {("pooled", "all decision days"): ("decision", list(days))}
    for split, label_of in (("regime", frame.regime), ("pressure_day_type", frame.day_type)):
        by_label: Dict[str, List[date]] = {}
        for t in targets:
            by_label.setdefault(label_of(t), []).append(t)
        for label, members in by_label.items():
            groups[(split, label)] = ("target", members)
    jobs, skipped = [], {}
    for (split, label), (grain, members) in groups.items():
        if len(members) < MIN_GROUP_DAYS:
            skipped[f"{split}/{label}"] = len(members)
            continue
        for metric, _ in METRICS:
            for candidate, benchmark in PAIRS:
                jobs.append(((grain, f"{split}/{label}"), metric, candidate, benchmark, tuple(members)))
    _STATE.update(series=series, draws=args.draws)
    done = run_jobs(jobs, args.workers)
    result: dict = {
        "issue": 1155, "declaration": str(DECLARATION.relative_to(REPO)), "panel_sha256": panel_sha256(panel_path),
        "label": "development, not a verdict", "seed": SEED, "draws": args.draws, "notes": notes, "models": list(MODELS),
        "pairs": [list(p) for p in PAIRS], "pool_mins": list(POOL_MINS), "pool_min_drafted": b2_pool.POOL_MIN,
        "pools": pool_summary(frame), "hits": hit_tables(frame), "groups": {}, "skipped_groups": skipped,
        "means": {label: {m: sum(series[("decision", label)][m].values()) / len(days) for m in MODELS} for label, _ in METRICS},
    }
    for (grain, name), metric, candidate, benchmark, row in done:
        split, label = name.split("/", 1)
        entry = result["groups"].setdefault(split, {}).setdefault(label, {"days": len(groups[(split, label)][1]), "metrics": {}})
        members = groups[(split, label)][1]
        ser = series[(grain, metric)]
        entry["metrics"].setdefault(metric, {"means": {m: sum(ser[m][d] for d in members) / len(members) for m in MODELS}, "pairs": {}})
        entry["metrics"][metric]["pairs"][f"{candidate} vs {benchmark}"] = row
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    Path(args.output).write_text(json.dumps(result, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    return 0


# -- the page ------------------------------------------------------------------------------------------------------

NAMES = {B1: "B1", B1P: "B1'", B2_LEGACY: "B2 legacy month-end", B2_TURN: "B2 turn labels, no minimum",
         "B2_pool10": "B2 + fallback, min 10", "B2_pool20": "B2 + fallback, min 20", "B2_pool30": "B2 + fallback, min 30"}
RULE_TEXT = {"above": "`y > q`", "at_or_above": "`y >= q`"}
KIND_TEXT = {"q95": "q95 exceedance (nominal 0.050)", "band90": "90% band miss (nominal 0.100)",
             "band50": "50% band miss (nominal 0.500)"}
SPLIT_TEXT = {"regime": "regime (target day)", "pressure_day_type": "pressure-day type (target day, turn labels)"}
METRIC_TEXT = {"grid_crps": "grid CRPS (23 levels)", "upper_tail_twcrps": "upper-tail twCRPS (weight 1{z > 0 bp})"}


def _group_names(result: dict, prefix: str) -> List[str]:
    order = ORDER_REGIME if prefix == "regime" else ORDER_TYPE
    present = {k.split("/", 1)[1] for k in result["hits"]["rows"][B2_TURN]["above"]["q95"] if k.startswith(prefix + "/")}
    return [x for x in order if x in present] + sorted(present - set(order))


def _rate(cell: dict) -> str:
    p = "" if cell["kupiec_p"] is None else f" ({cell['kupiec_p']:.3f})"
    return f"{cell['rate']:.3f}{p} n={cell['n']}"


def render_page(r: dict) -> str:
    n = r["notes"]
    out = [
        "# B2's thin-pool fallback, development reading (#1155): development data, not a verdict", "",
        "H5 step 2 (benchmarks; calendar first). Panel `%s`. Declaration `%s`. Seed %d, %s draws, the studentized stationary "
        "bootstrap (block 10). Decision days %s to %s (last target %s): %s days, every arm on the same days. Skill = mean(d) / "
        "mean(S(benchmark)); positive favours the first model; intervals are two-sided 90%% (the lower end is the one-sided 95%% "
        "lower bound)." % (r["panel_sha256"], r["declaration"], r["seed"], f"{r['draws']:,}", n["first"], n["last"],
                           n["last_target"], f"{n['scored_decision_days']:,}"), "",
        "The turn labels are the draft of #1135 (`turn_days.TurnLabels`), not in force; the fallback is the draft of #1155 "
        "(`b2_pool`), not in force. Nothing here is a verdict, and B2 is a benchmark: no candidate's result chose a number. "
        "The hit rule is Eleonora's open question (#993): both are reported. A rate is pooled over the five leads of the "
        "scored days, so its cells overlap and Kupiec's p-value (in brackets, for 20 or more cells) is read as a guide.", "",
        "Decision days on which B2 without a minimum cannot forecast (an empty pool: the first year-end of the panel) are not "
        "scored in any arm: " + (", ".join(n["dropped"]["B2_turn_empty_pool"]) or "none") + ".", ""]
    out += ["## The pool each target type reads", "",
            "Cells (day, lead) by target type; for each, the pool read (own type or the step of the chain) and the range of rows.", ""]
    for name in FALLBACK:
        out += [f"### {NAMES[name]}", "", "| target type | cells | pools read (cells) | rows in the pool |", "|---|---|---|---|"]
        for kind in ORDER_TYPE:
            c = r["pools"][name].get(kind)
            if c:
                pools = ", ".join(f"{k} {v}" for k, v in sorted(c["pools"].items(), key=lambda kv: -kv[1]))
                out.append(f"| {kind} | {c['cells']:,} | {pools} | {c['rows_min']} to {c['rows_max']} |")
        out.append("")
    out += ["## Coverage and exceedance, under both hit rules", ""]
    for rule in r["hits"]["rules"]:
        for kind in r["hits"]["kinds"]:
            out += [f"### {KIND_TEXT[kind]}, hit rule {RULE_TEXT[rule]}", ""]
            for split in ("pooled", "regime", "pressure_day_type"):
                groups = ["pooled"] if split == "pooled" else [f"{split}/{g}" for g in _group_names(r, split)]
                if split != "pooled":
                    out.append(f"**{SPLIT_TEXT[split]}**")
                    out.append("")
                out += ["| group | " + " | ".join(NAMES[m] for m in MODELS) + " |", "|---|" + "---|" * len(MODELS)]
                for g in groups:
                    out.append(f"| {g.split('/', 1)[-1]} | " + " | ".join(_rate(r["hits"]["rows"][m][rule][kind][g]) for m in MODELS) + " |")
                out.append("")
    out += ["## Scores, paired", "",
            "Mean grid CRPS and upper-tail twCRPS by arm, pooled: " + "; ".join(
                f"{NAMES[m]} {r['means']['grid_crps'][m]:.4f} / {r['means']['upper_tail_twcrps'][m]:.4f}" for m in r["models"]) + ".", ""]
    pairs = [f"{c} vs {b}" for c, b in r["pairs"]]
    for metric in METRIC_TEXT:
        out += [f"### {METRIC_TEXT[metric]}", ""]
        for split in ("pooled", "regime", "pressure_day_type"):
            if split not in r["groups"]:
                continue
            out += [f"**{SPLIT_TEXT.get(split, 'pooled (decision days)')}**", "",
                    "| group | days | " + " | ".join(f"{NAMES[p.split(' vs ')[0]]} over {NAMES[p.split(' vs ')[1]]}" for p in pairs) + " |",
                    "|---|---|" + "---|" * len(pairs)]
            order = ORDER_REGIME if split == "regime" else ORDER_TYPE
            labels = [l for l in order if l in r["groups"][split]] + sorted(set(r["groups"][split]) - set(order))
            for label in labels:
                entry = r["groups"][split][label]
                cells = entry["metrics"].get(metric, {}).get("pairs", {})
                out.append(f"| {label} | {entry['days']:,} | " + " | ".join(
                    s761.skill_text(cells[p]) if p in cells else "n/a" for p in pairs) + " |")
            out.append("")
    out += ["`undefined` is a pair that has no studentized interval: the two arms forecast alike on every day of the group (no variance "
            "of the difference), or the benchmark scores zero on a resample (the upper-tail score of a group in which no forecast "
            "and no outcome is above 0 bp).", ""]
    out += ["## What it shows and does not show", "",
            "- The chain replaces a thin type's pool by the next step's rows; it does not add them. A thin type's own few rows are "
            "dropped, so a target type that runs hotter than the type it falls to is forecast from the cooler one.",
            "- A pool minimum of 20 and one of 30 are the same rule here: no type but ordinary has as many as 20 rows in a year, "
            "so every other type reads every day. Their arms are identical.",
            "- Where a type keeps its own pool the fallback arm is B2 without a minimum, exactly (the paired test of those groups "
            "is `undefined`).", ""]
    for rule in r["hits"]["rules"]:
        for kind in ("q95", "band90"):
            cells = []
            for group in ("year_end", "quarter_end_turn"):
                row = [r["hits"]["rows"][m][rule][kind][f"pressure_day_type/{group}"]["rate"] for m in (B2_TURN, "B2_pool10", "B2_pool20")]
                cells.append(f"{group} {row[0]:.3f} / {row[1]:.3f} / {row[2]:.3f}")
            out.append(f"- {KIND_TEXT[kind]}, hit rule {RULE_TEXT[rule]}, B2 without a minimum / min 10 / min 20: " + "; ".join(cells) + ".")
    out += ["- Every arm is far from nominal on the thin types and on the 90% band of ordinary days: the fallback does not bring "
            "them near it, and at a minimum of 10 it helps the year-end and hurts the quarter-end turn. Development data on 2019-2025, never a verdict; B2 is a benchmark.", ""]
    if r["skipped_groups"]:
        out += ["Groups of fewer than %d target days, listed and not tested: " % MIN_GROUP_DAYS + ", ".join(
            f"{k} ({v})" for k, v in sorted(r["skipped_groups"].items())) + ".", ""]
    return "\n".join(out) + "\n"


def page(args) -> int:
    result = json.loads(Path(args.score).read_text(encoding="utf-8"))
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    Path(args.output).write_text(render_page(result), encoding="utf-8")
    return 0


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="command", required=True)
    one = sub.add_parser("score")
    one.add_argument("--panel", required=True)
    one.add_argument("--output", required=True)
    one.add_argument("--draws", type=int, default=sp.DRAWS)
    one.add_argument("--workers", type=int, default=4)
    one.set_defaults(run=score)
    two = sub.add_parser("page")
    two.add_argument("--score", required=True)
    two.add_argument("--output", required=True)
    two.set_defaults(run=page)
    args = parser.parse_args(argv)
    return args.run(args)


if __name__ == "__main__":
    raise SystemExit(main())
