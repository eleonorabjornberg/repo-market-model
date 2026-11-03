"""B2*, the calendar climatology with frozen pools and a declared fallback, scored with B2 against the candidate (s3c-ann-net) at the 18:00 decision
instant (#1420; H5, registration design, benchmarks; her ruling of 3 November 2026).

A development study, never a verdict. It writes JSON and Markdown to the paths it is given and nothing into `docs/runs/`. Every choice is in
`metadata/b2_star_1420.json`, which this script refuses to read unless it is committed and unchanged. B2* is
`repo_model.protocol_benchmarks.b2_star_forecast`: B2's day types and fallback chain with a two-year lookback and a minimum pool of 10. B2 is the benchmark
in force (#1155: one year, minimum 4). The candidate and B1, B1' and B2 are walked exactly as `scripts/b4_quantile_regression_1360.py` walks them (#1356's
machinery, at 18:00, the development window and the 2026 development days); no candidate arm changes, and no model is fitted for B2*.

It measures grid CRPS averaged over h = 1..5 (primary), upper-tail twCRPS (key secondary) and the Brier score of P(> +5 bp), on scoring protocol v1's
studentized stationary bootstrap read on the bound on mean d, with the skill interval beside; the mean (absolute) loss of every model beside every skill
ratio; pooled and by lead, regime, pressure-day type and the calendar type of the target; the coverage of the central 90% band; and how often each
fallback fired, for B2 and for B2*.

Commands, from a clone of the branch:

    PYTHONPATH=src python3 -m repo_model.cli build --raw-root tests/fixtures/snapshots/funding_inputs \\
        --output PUB.csv --build-cutoff 2026-09-08T21:31:42+00:00 --decision-time 18:00:00
    PYTHONPATH=src python3 -m repo_model.cli verify-panel PUB.csv --manifest metadata/funding_panel_manifest.json
    PYTHONPATH=src python3 scripts/b2_star_1420.py score --panel PUB.csv --output docs/research/b2-star-1420/result.json
    PYTHONPATH=src python3 scripts/b2_star_1420.py page \\
        --score docs/research/b2-star-1420/result.json --output docs/research/b2-star-1420-result.md

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


def _load(name: str, alias: Optional[str] = None):
    """Load `scripts/<name>.py` as a module registered under `alias` (default `name`)."""

    alias = alias or name
    path = REPO / "scripts" / f"{name}.py"
    held = sys.modules.get(alias)
    if held is not None and getattr(held, "__file__", None) == str(path):
        return held
    spec = importlib.util.spec_from_file_location(alias, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[alias] = module
    spec.loader.exec_module(module)
    return module


from repo_model import announced_iorb, b2_pool, policy_events, turn_days  # noqa: E402
from repo_model import protocol_benchmarks as pb  # noqa: E402
from repo_model import scoring_protocol as sp  # noqa: E402
from repo_model import spread_mr_calendar as cal  # noqa: E402
from repo_model.baseline import panel_sha256  # noqa: E402
from repo_model.evaluation_splits import load_split_declaration  # noqa: E402
from repo_model.exploration import EXPLORATORY_END, require_exploratory_window  # noqa: E402

#: #1360's script (and through it #1356's, #1321's, #1288's, #1273's and #1255's): the walks, the frame and the page helpers are loaded as they are.
m1360 = _load("b4_quantile_regression_1360", "b4_quantile_regression_1360_in_1420")
m1356, m1288 = m1360.m1356, m1360.m1288
k, c, s686, s761 = m1360.k, m1360.c, m1360.s686, m1360.s761
load_daily_panel = m1360.load_daily_panel
decision_instant_pinned = m1360.decision_instant_pinned

DECLARATION = REPO / "metadata" / "b2_star_1420.json"
RECORD_1356 = m1360.RECORD_1356
SEED = 1420
LAST_DAY = EXPLORATORY_END
WINDOW_LAST = m1288.WINDOW_LAST
WINDOWS = m1288.WINDOWS
WINDOW_TITLES = m1288.WINDOW_TITLES
B2STAR = "B2_star"
ANNNET, B1P = m1288.ANNNET, m1288.B1P
BENCHMARKS = m1288.BENCHMARKS
MODELS = BENCHMARKS + (B2STAR, ANNNET)
REFERENCES = (ANNNET,) + BENCHMARKS
LABELS = {"B1": "B1", B1P: "B1' (#960)", "B2": "B2 (in force: one year, minimum 4)", B2STAR: "B2* (two years, minimum 10)", ANNNET: "(s3c-ann-net), the candidate"}
SHORT = {"B1": "B1", B1P: "B1'", "B2": "B2", B2STAR: "B2*", ANNNET: "(s3c-ann-net)"}
TESTED = m1288.TESTED
METRIC_NAMES = m1288.METRIC_NAMES
METRIC_TITLES = m1288.METRIC_TITLES
MIN_GROUP_DAYS = m1288.MIN_GROUP_DAYS
LEADS = tuple(sp.HORIZONS)
SPLITS = ("pooled", "lead", "regime", "pressure_day_type", "target_day_type")
TYPES = (turn_days.YEAR_END, turn_days.QUARTER_END_TURN, turn_days.TURN, turn_days.TAX_DATE, turn_days.ORDINARY)
REPS = 2000
_STATE: Dict = {}


def committed_declaration(path: Path = DECLARATION) -> dict:
    """The declaration, refused unless it is committed and unchanged since `HEAD`."""

    return s686.committed_declaration(path)


def plan(candidate: str, split: str = "pooled") -> List[str]:
    """What a model is tested against: the candidate against B2*, B1, B1' and B2; B2* against B2 (the design in force). A benchmark is not a candidate."""

    if candidate == ANNNET:
        return [B2STAR] + list(BENCHMARKS)
    if candidate == B2STAR:
        return ["B2"]
    return []


# -- B2* and the fallback record -----------------------------------------------------------------------------------------


def require_forecasts(frame, forecasts: Mapping[date, object]) -> None:
    """Every scored decision day of the frame has a forecast (`b4_quantile_regression_1360.require_forecasts`).

    Raises:
        ValueError: a scored decision day has none.
    """

    m1360.require_forecasts(frame, forecasts)


def add_b2_star(frame, panel, splits, registry):
    """B2* on the frame's decision days, and the pool each of B2 and B2* read on every cell: `(forecasts, used)`.

    B2 is re-run here with the pool record and must equal the frame's B2.

    Raises:
        ValueError: B2 as re-run differs from the frame's, or a frame day has no B2* forecast.
    """

    base = dict(registry=registry, decision_time=k.DECISION_TIME, splits=splits)
    star: Dict[date, dict] = {}
    used: Dict[str, Dict[date, dict]] = {"B2": {}, B2STAR: {}}
    for day in frame.days:
        i = frame.position[day]
        record: Dict[int, Tuple[str, int]] = {}
        star[day] = pb.b2_star_forecast(panel, i, used=record, **base)
        used[B2STAR][day] = record
        record_b2: Dict[int, Tuple[str, int]] = {}
        two = b2_pool.b2_fallback_forecast(panel, i, pool_min=b2_pool.POOL_MIN, used=record_b2, **base)
        if two != frame.forecasts["B2"][day]:
            raise ValueError(f"B2 re-run for the pool record differs from the frame's B2 on {day}")
        used["B2"][day] = record_b2
    require_forecasts(frame, star)
    return star, used


def firing(frame, panel, used: Mapping[date, Mapping[int, Tuple[str, int]]]) -> dict:
    """How often each fallback fired: for each target type, the cells, the cells per pool read and the range of pool rows."""

    out: Dict[str, dict] = {}
    for day in frame.days:
        i = frame.position[day]
        for h in LEADS:
            target = panel[i + h]
            kind = turn_days.reporting_day_type(frame.splits, target.date, target.values)
            pool, rows = used[day][h]
            e = out.setdefault(kind, {"cells": 0, "pools": {}, "rows_min": rows, "rows_max": rows})
            e["cells"] += 1
            e["pools"][pool] = e["pools"].get(pool, 0) + 1
            e["rows_min"], e["rows_max"] = min(e["rows_min"], rows), max(e["rows_max"], rows)
    return out


def fell_back(kind: str, entry: Mapping[str, object]) -> int:
    """Cells of a type that read a pool other than its own."""

    return entry["cells"] - entry["pools"].get(kind, 0)


# -- the tests, in parallel ----------------------------------------------------------------------------------------------


def _identical(series, candidate: str, reference: str, members: Sequence[date]) -> bool:
    return all(series[candidate][d] == series[reference][d] for d in members)


def _pairs_task(job):
    split, label, grain, metric, candidate, members = job
    series = _STATE["series"][(grain, metric)]
    out: Dict[str, dict] = {}
    for name in plan(candidate, split):
        days = list(members)
        if _identical(series, candidate, name, days):
            out[name] = {"identical": True, "days": len(days)}
            continue
        out[name] = s761.run_pairs({name: series[name]}, series[candidate], days, seed=SEED, draws=_STATE["draws"], mean_d_fallback=True)[name]
        if "undefined" in out[name]:
            out[name]["unstudentized"] = m1356.unstudentized(series, candidate, name, days, _STATE["reps"])
    return (split, label, metric, candidate), out


def run_jobs(jobs, workers: int):
    with multiprocessing.get_context("fork").Pool(workers) as pool:
        return pool.map(_pairs_task, jobs, chunksize=1)


def run_window(window: str, panel, splits, registry, table, register, results, auctions, args) -> dict:
    frame, notes, _walk, _name, groups_fn = m1360.build(window, panel, splits, registry, table, register, results, auctions, args.first)
    frame.splits = splits
    last = WINDOW_LAST[window]
    cells = {m: m1288.cell_table(frame, frame.forecasts[m], last) for m in REFERENCES}
    check = m1360.reference_check(window, frame, cells, args)
    star, used = add_b2_star(frame, panel, splits, registry)
    frame.forecasts = {**frame.forecasts, B2STAR: star}
    cells[B2STAR] = m1288.cell_table(frame, star, last)
    for m in MODELS:
        official = sp.day_scores(frame.forecasts[m], frame.outcome, frame.dates, score=sp.grid_crps)
        mean = s686.by_decision(cells[m]["grid_crps"])
        if set(official) != set(mean) or any(abs(official[d] - mean[d]) > 1e-9 for d in mean):
            raise SystemExit(f"grid CRPS of {m}: the cell means differ from scoring_protocol.day_scores")
    labels = c.day_labels(frame, table)
    pressure = k.pressure_labels(frame, sorted(labels))
    groups = [g for g in groups_fn(frame, labels, pressure) if g[0] in SPLITS]
    series: Dict[Tuple[str, str], Dict[str, Dict[date, float]]] = {}
    for _s, _l, grain, _m in groups:
        for metric in METRIC_NAMES:
            if (grain, metric) not in series:
                series[(grain, metric)] = {m: c.series_of(frame, cells[m][metric], grain) for m in MODELS}
    _STATE.update(series=series, draws=args.draws, reps=args.reps)
    jobs, skipped = [], {}
    for split, label, grain, members in groups:
        if len(members) < MIN_GROUP_DAYS:
            skipped[f"{split}/{label}"] = len(members)
            continue
        for metric in TESTED:
            for candidate in (ANNNET, B2STAR):
                jobs.append((split, label, grain, metric, candidate, tuple(members)))
    done = run_jobs(jobs, args.workers)
    notes = dict(notes, starts_clipped=sum(1 for d in frame.days if _clipped(panel, frame.position[d])))
    result: dict = {"notes": notes, "groups": {}, "skipped_groups": skipped, "against_1356": check,
                    "fallback": {"B2": firing(frame, panel, used["B2"]), B2STAR: firing(frame, panel, used[B2STAR])}}
    for split, label, grain, members in groups:
        entry = result["groups"].setdefault(split, {}).setdefault(label, {"days": len(members)})
        for metric in METRIC_NAMES:
            ser = series[(grain, metric)]
            entry[metric] = {"means": {m: sum(ser[m][d] for d in members) / len(members) for m in MODELS}, "vs": {}}
    for (split, label, metric, candidate), payload in done:
        result["groups"][split][label][metric]["vs"][candidate] = payload
    result["pressure_day_type_counts"] = {x: sum(1 for t in pressure.values() if t == x) for x in sorted(set(pressure.values()))}
    return result


def _clipped(panel, decision_index: int) -> bool:
    """Whether B2*'s two-year window starts at the first row of the panel (clipped), so it holds less than two years."""

    return pb._window_start(panel, decision_index, pb.B2STAR_YEARS) == 0


def score(args) -> int:
    """Score both windows with every module of the chain at the declared decision instant (`decision_instant_pinned`)."""

    with decision_instant_pinned():
        return _score(args)


def _score(args) -> int:
    declaration = committed_declaration()
    panel_path = Path(args.panel)
    published_sha = panel_sha256(panel_path)
    panel = [row for row in load_daily_panel(panel_path) if row.date <= LAST_DAY]
    require_exploratory_window([row.date for row in panel], where="scripts/b2_star_1420")
    splits = load_split_declaration(c.SPLITS)
    registry = json.loads(c.SOURCES.read_text(encoding="utf-8"))
    register = policy_events.load_register()
    table = cal.TermTable(panel, announced_iorb.load_announcements(c.IORB_TABLE), decision_time=c.DECISION_TIME)
    auctions = m1360.m1273.load_auctions()
    results = m1288.load_results()
    result: dict = {
        "issue": 1420, "declaration": str(DECLARATION.relative_to(REPO)), "panel_sha256": published_sha,
        "decision_time": c.DECISION_TIME.strftime("%H:%M"), "subset_from": None if args.first is None else args.first.isoformat(),
        "label": "development, not a verdict", "seed": SEED, "draws": args.draws, "reps": args.reps, "models": list(MODELS),
        "references": list(REFERENCES), "b2_star": {"years": pb.B2STAR_YEARS, "pool_min": pb.B2STAR_POOL_MIN},
        "b2": {"years": pb.B2_YEARS, "pool_min": b2_pool.POOL_MIN},
        "windows": {}, "reading_rules": declaration["reading_rules"], "amendments": declaration["amendments"],
    }
    for window in (getattr(args, "windows", None) or WINDOWS):
        result["windows"][window] = run_window(window, panel, splits, registry, table, register, results, auctions, args)
        Path(args.output).parent.mkdir(parents=True, exist_ok=True)  # a window is kept as soon as it is scored
        Path(args.output).write_text(json.dumps(result, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    return 0


# -- the page ------------------------------------------------------------------------------------------------------------


def cell(row: Optional[dict]) -> str:
    return m1288.cell(row)


def _vs(group: Optional[Mapping[str, object]], metric: str, candidate: str, reference: str) -> Optional[dict]:
    return m1288._vs(group, metric, candidate, reference)


def mean_table(group: Mapping[str, object]) -> List[str]:
    out = ["| model | " + " | ".join(METRIC_TITLES[m] + " (mean loss)" for m in METRIC_NAMES) + " |", "|---|" + "---|" * len(METRIC_NAMES)]
    for m in MODELS:
        out.append(f"| {LABELS[m]} | " + " | ".join(
            f"{group[x]['means'][m]:.3f}" if x in ("grid_crps", "upper_tail_twcrps") else f"{group[x]['means'][m]:.4f}" for x in METRIC_NAMES) + " |")
    return out


def against_table(group: Mapping[str, object], candidate: str, split: str = "pooled") -> List[str]:
    out = [f"| {SHORT[candidate]} against (skill, 90% interval) | " + " | ".join(METRIC_TITLES[m] for m in TESTED) + " |", "|---|" + "---|" * len(TESTED)]
    for ref in plan(candidate, split):
        out.append(f"| {SHORT[ref]} | " + " | ".join(cell(_vs(group, m, candidate, ref)) for m in TESTED) + " |")
    return out


def split_table(window: Mapping[str, object], split: str, candidate: str, reference: str) -> List[str]:
    return m1288.split_table(window, split, candidate, reference)


def means_split_table(window: Mapping[str, object], split: str, metric: str, models: Sequence[str] = MODELS) -> List[str]:
    labels = window["groups"].get(split, {})
    out = [f"| {split.replace('_', ' ')} | days | " + " | ".join(SHORT[m] for m in models) + " |", "|---|---|" + "---|" * len(models)]
    for label in sorted(labels):
        g = labels[label]
        out.append(f"| {label} | {g['days']} | " + " | ".join(f"{g[metric]['means'][m]:.4f}" for m in models) + " |")
    return out if len(out) > 2 else []


def fallback_table(fallback: Mapping[str, dict]) -> List[str]:
    out = ["| target type | model | cells | cells on a fallback pool | pools read (cells) | pool rows (min to max) |", "|---|---|---|---|---|---|"]
    for kind in TYPES:
        for model in ("B2", B2STAR):
            e = fallback[model].get(kind)
            if e is None:
                continue
            pools = ", ".join(f"{p} {n}" for p, n in sorted(e["pools"].items()))
            out.append(f"| {kind} | {SHORT[model]} | {e['cells']} | {fell_back(kind, e)} | {pools} | {e['rows_min']} to {e['rows_max']} |")
    return out


def headline(r: Mapping[str, object]) -> str:
    parts = []
    for window, text in (("development", "On the development window"), ("2026", "on the 2026 development days")):
        g = r["windows"].get(window, {}).get("groups", {}).get("pooled", {}).get("all decision days")
        if g is None:
            continue
        parts.append(f"{text}, pooled grid CRPS: (s3c-ann-net) against B2* {cell(_vs(g, 'grid_crps', ANNNET, B2STAR))} and against B2 "
                     f"{cell(_vs(g, 'grid_crps', ANNNET, 'B2'))}; B2* against B2 {cell(_vs(g, 'grid_crps', B2STAR, 'B2'))}")
    return "; ".join(parts) + "."


def answer(r: Mapping[str, object]) -> List[str]:
    out = ["## The answer, pooled", "",
           "Read on the mean-d bound (the lower end of the 90% interval of mean d above zero is a gain, the upper end below zero a loss, otherwise undecided). "
           "Positive d favours the first-named model. The splits follow; a pooled figure alone is not a result.", ""]
    for window in WINDOWS:
        w = r["windows"].get(window)
        if w is None:
            continue
        g = w["groups"]["pooled"]["all decision days"]
        out.append(f"**{WINDOW_TITLES[window]}.**")
        for metric in TESTED:
            out.append(f"- {METRIC_TITLES[metric]}: (s3c-ann-net) against B2* {cell(_vs(g, metric, ANNNET, B2STAR))}; against B2 "
                       f"{cell(_vs(g, metric, ANNNET, 'B2'))}; B2* against B2 {cell(_vs(g, metric, B2STAR, 'B2'))}")
        out.append("")
    return out


def definition() -> List[str]:
    return [
        "**What B2* is.** B2 (the calendar climatology of protocol section 4) with its pools, lookback and fallback fixed in the declaration, with no search. "
        "**Pools:** the day types of the month-end-turn record in force (`year_end`, `quarter_end_turn`, `turn`, `tax_date`, `ordinary`), each read from the row's "
        "own date and tax-date column, so the target's type is known in advance. **Lookback:** two calendar years before the decision day (B2 in force reads "
        "one), clipped at the start of the panel. **Minimum pool:** 10 rows (B2 in force: 4). **Fallback:** a type with fewer rows reads the next step of its chain "
        "(year end, then quarter-end turn, then turn, then every day; the quarter-end turn, then turn, then every day; the others go straight to every day); "
        "a step replaces the pool, and there is no shrinkage. Same 18:00 decision instant, same eligible origins and same as-of guards as the candidate. "
        "**The numbers (two years, 10) are a proposal, stated and not searched; they are a marked question below.**"]


def render(r: dict) -> str:
    out = [
        "# B2*, the calendar climatology with frozen pools and a declared fallback, against B2 and the candidate, at the 18:00 decision (#1420)", "",
        "**Is the candidate's edge over B2 an artefact of B2's thin pools?** " + headline(r), "",
        "**Hypothesis and step:** H5 (primary goal), registration design (benchmarks); her ruling of 3 November 2026 (chat, relayed on #1420). **Development data, "
        "not a verdict** (scoring protocol v1, #640). Nothing is registered or published, the candidate (s3c-ann-net) does not change, and which benchmark the "
        "confirmation uses is hers. Generated by `scripts/b2_star_1420.py page` from "
        f"`docs/research/b2-star-1420/result.json`, not edited by hand; declared in `{r['declaration']}` before any score.", ""]
    out += definition() + [""]
    out += answer(r)
    out += [
        f"Panel digest `{r['panel_sha256']}`. Studentized stationary bootstrap (ruling 1), mean block {sp.BLOCK_LENGTH} business days, {r['draws']:,} draws, "
        f"seed {r['seed']}, two-sided 90% interval (the lower end is the one-sided 95% bound). Positive mean d favours the model named first. **A reading (gain, "
        "loss, undecided) is taken from the mean-d bound** (her ruling on #1009), with the skill interval beside it; for a Brier score the skill is the Brier "
        "skill score. **Absolute losses sit beside the skill ratios** in the mean tables. **Caveat (Lens C, #958):** the lag-10 HAC standard error that "
        "studentizes the bound is understated about 2x after 2020, so an interval that excludes zero is narrower than it should be. No reading of a day-type "
        "group is a finding. Groups of fewer than 20 days are listed with their means and not tested.", "",
        "**What kind of look this is.** The 2026 days were already seen by #845, #151, #1229, #1255, #1273, #1288, #1321, #1356 and #1360. They are shown "
        "separately and decide nothing. B2* was designed after the development window had been seen, so a result here is exploration.", ""]
    for window in WINDOWS:
        w = r["windows"].get(window)
        if w is None:
            continue
        n, pooled = w["notes"], w["groups"]["pooled"]["all decision days"]
        out += [f"## {WINDOW_TITLES[window]}", "",
                f"Scored decision days: {n['scored_decision_days']:,} ({n['first']} to {n['last']}); on {n['starts_clipped']:,} of them B2*'s two-year window is "
                "clipped at the start of the panel.", "", "### Mean scores (absolute losses, pooled)", ""] + mean_table(pooled)
        for cand in (ANNNET, B2STAR):
            out += ["", f"### {LABELS[cand]} against each reference (pooled)", ""] + against_table(pooled, cand) + [""]
        for split, title in (("lead", "By lead"), ("regime", "By regime"), ("pressure_day_type", "By pressure-day type of the target day"),
                             ("target_day_type", "By calendar day type of the target")):
            for cand, ref in ((ANNNET, B2STAR), (ANNNET, "B2"), (B2STAR, "B2")):
                table = split_table(w, split, cand, ref)
                if table:
                    out += [f"### {title}: {SHORT[cand]} against {SHORT[ref]}", ""] + table + [""]
        for split, title in (("regime", "regime"), ("pressure_day_type", "pressure-day type"), ("target_day_type", "calendar day type of the target"),
                             ("lead", "lead")):
            table = means_split_table(w, split, "grid_crps")
            if table:
                out += [f"### Mean grid CRPS by {title}, every model", ""] + table + [""]
        for split in ("regime", "target_day_type"):
            table = means_split_table(w, split, "b90_closed")
            if table:
                out += [f"### 90% band coverage by {split.replace('_', ' ')}", ""] + table + [""]
        out += ["### How often each fallback fired", "",
                "Cells are (decision day, lead) pairs on the scored days, by the type of the target. A cell is on a fallback pool when the pool it read is not its "
                "own type.", ""] + fallback_table(w["fallback"]) + [""]
        if w["skipped_groups"]:
            out += ["Groups of fewer than 20 days, listed and not tested: " + ", ".join(f"{x} ({n_})" for x, n_ in sorted(w["skipped_groups"].items())) + ".", ""]
    checks = {w: r["windows"][w].get("against_1356") for w in WINDOWS if w in r["windows"] and r["windows"][w].get("against_1356")}
    if checks:
        worst = max(v["difference"] for v in checks.values())
        out += ["## The references against #1356's record (made at 18:00)", "",
                "(s3c-ann-net), B1, B1' and B2 are re-run here with the same frames and walks; the pooled means equal #1356's to 1e-9 (the run stops otherwise). "
                f"Largest absolute difference: {worst:.1e}.", ""]
    out += question()
    return "\n".join(out).rstrip() + "\n"


def question() -> List[str]:
    return [
        "## Question for Eleonora (marked; the default changes no claim)", "",
        "**Are the lookback and the minimum pool of B2* (two years, 10) the ones the confirmation freezes?** The directive asked for them to be stated and fixed "
        "with no search; they are a proposal. B2* is added to `repo_model.protocol_benchmarks` (`b2_star_forecast`), and nothing in the decision rule of "
        "`docs/decisions/scoring-protocol.md` changes in this pull request.", "",
        "**Options** (the default applies if you have not answered by the next 5 pm batch):", "",
        "1. **Two years, minimum 10, hard fallback, as declared** (default): the confirmation design (#1393, #1394) names B2* with these numbers.",
        "2. **Another pair** (name the lookback and the minimum): B2* is re-scored once under the new declaration, as an amendment before its score.",
        "3. **Shrinkage in place of a hard fallback** (a weight on the parent pool by thin-pool size): a new declaration, scored once.", "",
        "**A second question: does B2* replace B2 as the protocol's calendar climatology, or sit beside it?** Default: beside it; B2 in force (#1155) and "
        "section 4 are unchanged until you rule."]


def page(args) -> int:
    r = json.loads(Path(args.score).read_text(encoding="utf-8"))
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    Path(args.output).write_text(render(r), encoding="utf-8")
    return 0


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="command", required=True)
    s = sub.add_parser("score", help="walk (s3c-ann-net) and the benchmarks, add B2*, and score both windows")
    s.add_argument("--panel", required=True)
    s.add_argument("--output", required=True)
    s.add_argument("--draws", type=int, default=sp.DRAWS)
    s.add_argument("--reps", type=int, default=REPS, help="bootstrap resamples of the unstudentized intervals")
    s.add_argument("--workers", type=int, default=4)
    s.add_argument("--windows", nargs="+", choices=WINDOWS, default=None, help="score these windows only (the script's test only; the declared run omits it)")
    s.add_argument("--first", type=date.fromisoformat, default=None,
                   help="start the walk on this day (a subset, for the script's test only; the declared run omits it)")
    s.set_defaults(func=score)
    g = sub.add_parser("page", help="write the result page from a score file")
    g.add_argument("--score", required=True)
    g.add_argument("--output", required=True)
    g.set_defaults(func=page)
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
