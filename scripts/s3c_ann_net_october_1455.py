"""(s3c-ann-net) with the 15 October `tax_date` label at the target day (#1455; H5, registration groundwork: the known-limits list; #1004, #965, #979).

A development study, never a verdict. Her ruling of 4 November 2026 (decision docket, option (a) on finding #1004): test the label as a development arm on
(s3c-ann-net) and record the result under known limits. The frozen candidate does not change and any adoption is hers. Every choice is in
`metadata/s3c_ann_net_october_1455.json`, which this script refuses to read unless it is committed and unchanged.

The control is (s3c-ann-net) as #1288 / #1319 / #1314 walk it (`scripts/s3c_announced_settlement_1288.py`, unchanged) on the published panel at the 18:00 decision
instant. The arm, (s3c-ann-net+oct), is the same model on the same decision days and refit days with one change: the `tax_date` flag of its term table is the
published flag OR-ed with `tax_date_october.october_window` (15 October rolled forward off weekends and DC holidays, and the two market days after it). The flag is
read at the target row, as the published one is, and the fit is on direct pairs (`training_pairs='direct'`, the default of `spread_mr_state_calendar.walk`).
Only the term table changes: the panel, the turn-day labels behind the model's level and the day-type groups are the control's.

What this script adds: the table (`OctoberTermTable`), its guard (`require_only_october`), the walk of the arm over the control's decision days, the paired scores
against the control and B1'* (the studentized stationary bootstrap of `scoring_protocol.paired_tests`, as #1288 and #1444 run it), the split by lead, regime,
pressure-day type and target-day type, and the October tax windows (`october_groups`): all of them, those of the years but 2019 and 2025 (the reading that leaves out
the days that prompted the label), and those of 2019 and 2025.

Commands, from a clone of the branch (about twenty to forty minutes in a cloud session; no step is expected to run over two hours):

    PYTHONPATH=src python3 -m repo_model.cli build --raw-root tests/fixtures/snapshots/funding_inputs --output PUB.csv \\
        --build-cutoff 2026-09-08T21:31:42+00:00 --decision-time 18:00:00
    PYTHONPATH=src python3 -m repo_model.cli verify-panel PUB.csv --manifest metadata/funding_panel_manifest.json
    PYTHONPATH=src python3 scripts/s3c_ann_net_october_1455.py score --panel PUB.csv \\
        --output docs/research/s3c-ann-net-october-1455/result.json
    PYTHONPATH=src python3 scripts/s3c_ann_net_october_1455.py page \\
        --score docs/research/s3c-ann-net-october-1455/result.json --output docs/research/s3c-ann-net-october-1455-result.md

Stdlib only. No gradient-boosted fitter is called.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import multiprocessing
import sys
from datetime import date, time
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


from repo_model import announced_iorb, b1_calendar, policy_events, s3c_announced, s3c_net, tax_date_october  # noqa: E402
from repo_model import scoring_protocol as sp, spread_mr_calendar as cal, spread_mr_state_calendar as sc  # noqa: E402
from repo_model.baseline import panel_sha256  # noqa: E402
from repo_model.data import DailyObservation, load_daily_panel  # noqa: E402
from repo_model.evaluation_splits import load_split_declaration  # noqa: E402
from repo_model.exploration import require_exploratory_window  # noqa: E402
from repo_model.lockbox import require_unlocked  # noqa: E402

#: #1288's script (the walks, the frame, the cell table, the paired tests), under an alias of its own so that the pickling of the worker pool's tasks does not meet
#: another test module's copy.
m1288 = _load("s3c_announced_settlement_1288", "s3c_announced_settlement_1288_in_1455")
m1273, m1255, k, c, s686, s761 = m1288.m1273, m1288.m1255, m1288.k, m1288.c, m1288.s686, m1288.s761

DECLARATION = REPO / "metadata" / "s3c_ann_net_october_1455.json"
SEED = m1288.SEED
LAST_DAY = m1288.LAST_DAY
WINDOWS = m1288.WINDOWS
WINDOW_LAST = m1288.WINDOW_LAST
TESTED = m1288.TESTED
METRIC_NAMES = m1288.METRIC_NAMES
METRIC_TITLES = m1288.METRIC_TITLES
MIN_GROUP_DAYS = m1288.MIN_GROUP_DAYS
LEADS = tuple(sp.HORIZONS)
CONTROL = m1288.ANNNET
ARM = "sc_s3c_ann_net_oct"
REFERENCE = "B1'*"
MODELS = (CONTROL, ARM, REFERENCE)
LABELS = {CONTROL: "(s3c-ann-net)", ARM: "(s3c-ann-net+oct)", REFERENCE: "B1'*"}
NET_ARM = s3c_announced.ANN_NET_ARM

#: The instant this study is made at: the repository's decision instant since #1312.
INSTANT_TIME = time(18, 0)
INSTANT_TEXT = INSTANT_TIME.isoformat(timespec="minutes")
#: The years whose October prompted the label (#965: 2019-10-15, 2019-10-16, 2025-10-15), left out of the reading that can speak to it.
MOTIVATING_YEARS = (2019, 2025)
OCTOBER_SPLIT = "october_window"
ALL_OCTOBER = "all October-window targets"
OTHER_OCTOBER = "October-window targets, not 2019 or 2025"
MOTIVATING_OCTOBER = "October-window targets of 2019 and 2025 (the days that prompted the label)"
#: Two scores that differ by no more than this on every day of a group are one score (#1314's tolerance).
TOLERANCE = 1e-9


# -- the guards ----------------------------------------------------------------------------------------------------------


def require_instant(decision_time: time) -> None:
    """Refuse to make an 18:00 study at another decision instant.

    Raises:
        ValueError: the repository's decision instant is not the declared one.
    """

    if decision_time != INSTANT_TIME:
        raise ValueError(f"this study is made at {INSTANT_TEXT}; the repository's decision instant is {decision_time.isoformat(timespec='minutes')}")


def committed_declaration(path: Path = DECLARATION) -> dict:
    """The declaration, refused unless it is committed and unchanged since `HEAD`."""

    return s686.committed_declaration(path)


def require_only_october(published: Sequence[Optional[int]], arm: Sequence[Optional[int]], dates: Sequence[date]) -> None:
    """The arm's `tax_date` flags differ from the published ones only by adding days of the October window.

    Raises:
        ValueError: a flag that differs anywhere else (one added outside the window, or a published flag cleared).
    """

    for published_flag, arm_flag, day in zip(published, arm, dates):
        if published_flag is None and arm_flag is None:
            continue
        october = tax_date_october.october_window(day)
        if arm_flag != published_flag and not (arm_flag == 1 and not published_flag and october):
            raise ValueError(f"the arm's tax_date flag on {day} is {arm_flag}, the published one {published_flag}: only October-window days may be added")


# -- the term table ------------------------------------------------------------------------------------------------------


class OctoberTermTable(s3c_announced.AnnouncedTermTable):
    """`AnnouncedTermTable` whose `tax_date` flag is the published flag OR-ed with the October window of `tax_date_october`.

    The label is a function of the date and the pinned market holiday table alone, so a decision at any lead can read it at its target row: it is known ahead of
    its date, as a calendar column is. Every other term, and the panel, are the base table's.
    """

    def __init__(self, panel: Sequence[DailyObservation], announcements, results, calendar=None, *, decision_time: time, **kw):
        super().__init__(panel, announcements, results, calendar, decision_time=decision_time, **kw)
        october = [1 if tax_date_october.october_window(day) else 0 for day in self.dates]
        for lead in cal.HORIZONS:
            published = self._flags[("tax_date", lead)]
            arm = [None if p is None else (1 if p or o else 0) for p, o in zip(published, october)]
            require_only_october(published, arm, self.dates)
            self._flags[("tax_date", lead)] = arm


# -- the groups ----------------------------------------------------------------------------------------------------------


def october_groups(targets: Sequence[date]) -> List[Tuple[str, str, str, List[date]]]:
    """The October tax windows as groups of target days: all, those of the years but 2019 and 2025, and those of 2019 and 2025."""

    window = [t for t in sorted(targets) if tax_date_october.october_window(t)]
    other = [t for t in window if t.year not in MOTIVATING_YEARS]
    motivating = [t for t in window if t.year in MOTIVATING_YEARS]
    return [(OCTOBER_SPLIT, ALL_OCTOBER, "target", window), (OCTOBER_SPLIT, OTHER_OCTOBER, "target", other), (OCTOBER_SPLIT, MOTIVATING_OCTOBER, "target", motivating)]


# -- the readings --------------------------------------------------------------------------------------------------------


def reading(row: Optional[Mapping[str, object]]) -> str:
    """`gain` when the studentized interval of the difference (reference less arm; positive favours the arm) is wholly above zero, `cost` when wholly below,
    `undecided` otherwise; `identical` for a group the two score alike on every day, `not read` where the interval is undefined."""

    if row is None:
        return "not read"
    if row.get("identical"):
        return "identical"
    interval = row.get("difference_interval")
    if not interval:
        return "not read"
    if interval[0] > 0.0:
        return "gain"
    if interval[1] < 0.0:
        return "cost"
    return "undecided"


def label_reading(rows: Mapping[str, Optional[Mapping[str, object]]]) -> str:
    """The declared reading of the label from the grid CRPS and the upper-tail twCRPS rows (control less arm) of a group that leaves out the motivating years:
    `supported` (a gain on one and no cost on the other), `not supported` (a cost on either, or an identical score), `not read` where a row is missing (the group is
    below the study's minimum), else `undecided`."""

    a, b = reading(rows.get("grid_crps")), reading(rows.get("upper_tail_twcrps"))
    if "not read" in (a, b):
        return "not read (the group is below the minimum size, or an interval is undefined)"
    if "cost" in (a, b) or (a == "identical" and b == "identical"):
        return "not supported"
    if "gain" in (a, b):
        return "supported"
    return "undecided"


_STATE: Dict = {}


def alike(a: Mapping[date, float], b: Mapping[date, float], days: Sequence[date], tolerance: float = TOLERANCE) -> bool:
    """Whether two daily score series agree within `tolerance` on every one of `days`."""

    return all(abs(a[d] - b[d]) <= tolerance for d in days)


def _task(job):
    split, label, grain, metric, members = job
    series = _STATE["series"][(grain, metric)]
    days = list(members)
    out: Dict[str, dict] = {}
    # d = reference less arm: positive favours the arm (as #1288's paired rows)
    for name, (reference, candidate) in {
        "arm_vs_control": (CONTROL, ARM), "arm_vs_B1star": (REFERENCE, ARM), "control_vs_B1star": (REFERENCE, CONTROL),
    }.items():
        if alike(series[candidate], series[reference], days):
            out[name] = {"identical": True, "days": len(days)}
            continue
        row = s761.run_pairs({reference: series[reference]}, series[candidate], days, seed=SEED, draws=_STATE["draws"], mean_d_fallback=True)[reference]
        row["reading"] = reading(row)
        out[name] = row
    return (split, label, metric), out


def run_jobs(jobs, workers: int):
    with multiprocessing.get_context("fork").Pool(workers) as pool:
        return pool.map(_task, jobs, chunksize=1)


# -- one window ----------------------------------------------------------------------------------------------------------


def tax_record(est: sc.StateEstimate) -> dict:
    """What a refit kept for a lead about `tax_date`: whether it entered, its effect (scale units), its flagged-pair count, and the pairs."""

    return {"entered": "tax_date" in est.terms, "effect": est.effect.get("tax_date"), "flagged": est.flagged.get("tax_date"), "pairs": est.pairs}


def run_window(window: str, ctx: dict, args) -> dict:
    panel = ctx["panel"]
    frame, notes, walks, (_term_table, net_table), _cells, groups_fn = m1288.build(
        window, panel, ctx["splits"], ctx["registry"], ctx["table"], ctx["register"], ctx["results"], ctx["auctions"], None)
    last = WINDOW_LAST[window]
    control_walk = walks["ann"]
    first = min(control_walk.forecasts[NET_ARM.name])
    days = [d for d in m1288.candidate_days(frame, window, None) if d >= first]
    arm_walk = sc.walk(panel, days, ctx["october_table"], ctx["states"], (NET_ARM,), sizes=net_table, registry=ctx["registry"], decision_time=k.DECISION_TIME,
                       splits=ctx["splits"], training_pairs="direct")
    refit_days = sorted(control_walk.fits)
    if refit_days != sorted(arm_walk.fits):
        raise ValueError("the arm's refit days are not the control's: the walks are not the same")
    for d in frame.days:
        if d not in arm_walk.forecasts[NET_ARM.name]:
            raise ValueError(f"the arm's walk has no forecast of the scored decision day {d}")
    positions = {row.date: i for i, row in enumerate(panel)}
    settings = dict(registry=ctx["registry"], decision_time=k.DECISION_TIME, splits=ctx["splits"])
    star = {d: b1_calendar.b1_calendar_anchor_forecast(panel, positions[d], **settings) for d in frame.days}
    forecasts = {
        CONTROL: {d: frame.forecasts[CONTROL][d] for d in frame.days},
        ARM: m1255.s3c_forecasts(frame, ctx["register"], {d: arm_walk.forecasts[NET_ARM.name][d] for d in frame.days}),
        REFERENCE: star,
    }
    cells = {m: m1288.cell_table(frame, forecasts[m], last) for m in MODELS}
    for m in MODELS:
        official = sp.day_scores(forecasts[m], frame.outcome, frame.dates, score=sp.grid_crps)
        mean = s686.by_decision(cells[m]["grid_crps"])
        if set(official) != set(mean) or any(abs(official[d] - mean[d]) > 1e-9 for d in mean):
            raise SystemExit(f"grid CRPS of {m}: the cell means differ from scoring_protocol.day_scores")
    labels = c.day_labels(frame, ctx["table"])
    pressure = k.pressure_labels(frame, sorted(labels))
    groups = list(groups_fn(frame, labels, pressure)) + october_groups(sorted(labels))
    series: Dict[Tuple[str, str], Dict[str, Dict[date, float]]] = {}
    for _s, _l, grain, _m in groups:
        for metric in METRIC_NAMES:
            if (grain, metric) not in series:
                series[(grain, metric)] = {m: c.series_of(frame, cells[m][metric], grain) for m in MODELS}
    _STATE.update(series=series, draws=args.draws)
    jobs, skipped = [], {}
    for split, label, grain, members in groups:
        if len(members) < MIN_GROUP_DAYS:
            skipped[f"{split}/{label}"] = len(members)
            continue
        for metric in TESTED:
            jobs.append((split, label, grain, metric, tuple(members)))
    done = run_jobs(jobs, args.workers)
    result_groups: Dict[str, dict] = {}
    for split, label, grain, members in groups:
        entry = result_groups.setdefault(split, {}).setdefault(label, {"days": len(members)})
        for metric in METRIC_NAMES:
            ser = series[(grain, metric)]
            if members:
                entry[metric] = {"means": {m: sum(ser[m][d] for d in members) / len(members) for m in MODELS}}
                if metric in TESTED:
                    entry[metric]["vs"] = {}
    for (split, label, metric), payload in done:
        result_groups[split][label][metric]["vs"] = payload
    refits = {
        r.isoformat(): {str(h): {"control": tax_record(control_walk.estimates[r][NET_ARM.name][h]), "arm": tax_record(arm_walk.estimates[r][NET_ARM.name][h])}
                        for h in LEADS}
        for r in refit_days
    }
    differing = [d.isoformat() for d in frame.days if forecasts[CONTROL][d] != forecasts[ARM][d]]
    october_days = [t.isoformat() for t in sorted(labels) if tax_date_october.october_window(t)]
    return {
        "notes": notes, "days": len(frame.days), "first_scored": frame.days[0].isoformat(), "last_scored": frame.days[-1].isoformat(),
        "first_forecast_day": first.isoformat(), "refits": {"control": len(control_walk.fits), "arm": len(arm_walk.fits), "days": [r.isoformat() for r in refit_days]},
        "refit_tax_date": refits, "decision_days_with_a_different_forecast": len(differing), "october_window_targets": october_days,
        "groups": result_groups, "skipped_groups": skipped,
        "pressure_day_type_counts": {x: sum(1 for t in pressure.values() if t == x) for x in sorted(set(pressure.values()))},
    }


# -- the commands --------------------------------------------------------------------------------------------------------


def score_command(args) -> int:
    declaration = committed_declaration()
    require_instant(k.DECISION_TIME)
    require_unlocked([LAST_DAY], where="s3c_ann_net_october_1455")
    published_sha = panel_sha256(Path(args.panel))
    panel = [row for row in load_daily_panel(Path(args.panel)) if row.date <= LAST_DAY]
    require_exploratory_window([row.date for row in panel], where="scripts/s3c_ann_net_october_1455")
    splits = load_split_declaration(c.SPLITS)
    registry = json.loads(c.SOURCES.read_text(encoding="utf-8"))
    announcements = announced_iorb.load_announcements(c.IORB_TABLE)
    results = m1288.load_results()
    ctx = {
        "panel": panel, "splits": splits, "registry": registry, "register": policy_events.load_register(), "results": results,
        "auctions": m1273.load_auctions(), "table": cal.TermTable(panel, announcements, decision_time=c.DECISION_TIME),
        "october_table": OctoberTermTable(panel, announcements, results, decision_time=k.DECISION_TIME), "states": s3c_net.constant_states(panel),
    }
    result: dict = {
        "issue": 1455, "declaration": str(DECLARATION.relative_to(REPO)), "label": "development, not a verdict", "instant": INSTANT_TEXT,
        "published_panel_sha256": published_sha, "seed": SEED, "draws": args.draws, "models": list(MODELS), "labels": LABELS,
        "reading_rules": declaration["reading_rules"], "windows": {},
    }
    for window in WINDOWS:
        result["windows"][window] = run_window(window, ctx, args)
    result["label_reading"] = {
        window: {
            label: label_reading({metric: (w["groups"].get(OCTOBER_SPLIT, {}).get(OTHER_OCTOBER, {}).get(metric, {}).get("vs") or {}).get("arm_vs_control") for metric in TESTED})
            for label in (OTHER_OCTOBER,)
        }
        for window, w in result["windows"].items()
    }
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    Path(args.output).write_text(json.dumps(result, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    return 0


# -- the page ------------------------------------------------------------------------------------------------------------


def _iv(interval: Optional[Sequence[float]], digits: int = 3) -> str:
    return "not read" if not interval else f"[{interval[0]:+.{digits}f}, {interval[1]:+.{digits}f}]"


def cell(row: Optional[Mapping[str, object]]) -> str:
    if row is None:
        return "n/a"
    if row.get("identical"):
        return "identical"
    if "difference" not in row:
        return "not read"
    return f"{row['difference']:+.3f} {_iv(row.get('difference_interval'))} **{row.get('reading', reading(row))}**"


def group_table(groups: Mapping[str, dict], split: str, metric: str, key: str, skipped: Mapping[str, int]) -> List[str]:
    out = ["| group | days | " + f"{LABELS[CONTROL]} | {LABELS[ARM]} | {LABELS[REFERENCE]} | d, " + {"arm_vs_control": "control less arm", "arm_vs_B1star": "B1'* less arm",
           "control_vs_B1star": "B1'* less control"}[key] + " |", "|---|---|---|---|---|---|"]
    for label, entry in groups.get(split, {}).items():
        if metric not in entry:
            out.append(f"| {label} | {entry['days']} | | | | no days |")
            continue
        means = entry[metric]["means"]
        row = entry[metric].get("vs", {}).get(key)
        small = f"too small ({skipped.get(f'{split}/{label}', entry['days'])} days, minimum {MIN_GROUP_DAYS})"
        out.append(f"| {label} | {entry['days']} | {means[CONTROL]:.3f} | {means[ARM]:.3f} | {means[REFERENCE]:.3f} | {cell(row) if row else small} |")
    return out


def render(r: dict) -> str:
    lines = [
        "# (s3c-ann-net) with the 15 October tax-date label at the target day (#1455)",
        "",
        "> **Development evidence, not a verdict** (scoring protocol v1: development data never gives one). H5 (primary goal), registration groundwork: the known-limits "
        "list. Her ruling of 4 November 2026 (option (a) on finding #1004): the label is tested as a development arm on (s3c-ann-net). Nothing is adopted, the frozen "
        f"candidate does not change, and the label is a data meaning that stays hers. Made at {r['instant']} New York time. Declaration: "
        f"[`{r['declaration']}`](../../{r['declaration']}), committed before any score.",
        "",
        "## What was measured",
        "",
        "The control is (s3c-ann-net) as #1288, #1319 and #1314 walk it, on the published panel. The arm, (s3c-ann-net+oct), is the same model on the same decision days and "
        "refit days with one change: the `tax_date` flag of its term table is the published flag OR-ed with the October window of #965 (15 October rolled forward off "
        "weekends and DC holidays, and the two market days after it), read at the target row on direct pairs. The panel, the turn-day labels behind the model's "
        "level and the day-type groups are the control's, so the arm tests the label as a fitted term only.",
        "",
        "d is the reference's score less the arm's, so a positive d favours the arm. The interval is the studentized stationary-bootstrap interval of the protocol "
        "(`scoring_protocol.paired_tests`, 90%); *gain* is an interval wholly above zero, *cost* wholly below, *undecided* otherwise. The October tax windows are "
        "scored on their target days, which are not contiguous: days from different years join into blocks. The reading that can speak to the label leaves out "
        "2019 and 2025, the years whose prints prompted it (#965).",
        "",
    ]
    for window in WINDOWS:
        w = r["windows"][window]
        skipped = w["skipped_groups"]
        lines += [
            f"## {m1288.WINDOW_TITLES[window]}",
            "",
            f"{w['days']} decision days, first scored {w['first_scored']}, last {w['last_scored']}; {w['refits']['control']} refits of the control and {w['refits']['arm']} "
            f"of the arm (the same days). The arm's forecast differs from the control's on {w['decision_days_with_a_different_forecast']} scored decision days. "
            f"October-window target days in this window: {len(w['october_window_targets'])}.",
            "",
        ]
        for metric in TESTED:
            lines += [f"### {METRIC_TITLES[metric]}, {window}", "", "The October tax windows", ""]
            lines += group_table(w["groups"], OCTOBER_SPLIT, metric, "arm_vs_control", skipped)
            lines += ["", "Pooled and by lead", ""] + group_table(w["groups"], "pooled", metric, "arm_vs_control", skipped)
            lines += [""] + group_table(w["groups"], "lead", metric, "arm_vs_control", skipped)
            lines += ["", "By regime", ""] + group_table(w["groups"], "regime", metric, "arm_vs_control", skipped)
            lines += ["", "By pressure-day type", ""] + group_table(w["groups"], "pressure_day_type", metric, "arm_vs_control", skipped)
            lines += ["", "By target-day type", ""] + group_table(w["groups"], "target_day_type", metric, "arm_vs_control", skipped)
            lines += ["", "Each against B1'* (the arm, then the control), pooled and by regime", ""]
            lines += group_table(w["groups"], "pooled", metric, "arm_vs_B1star", skipped)
            lines += group_table(w["groups"], "regime", metric, "arm_vs_B1star", skipped)[2:]
            lines += [""] + group_table(w["groups"], "pooled", metric, "control_vs_B1star", skipped)
            lines += group_table(w["groups"], "regime", metric, "control_vs_B1star", skipped)[2:]
            lines += [""]
        last = sorted(w["refit_tax_date"])[-1]
        lines += [f"### The `tax_date` term at the last refit ({last})", "", "| lead | control: effect (flagged pairs) | arm: effect (flagged pairs) |", "|---|---|---|"]

        def eff(x):
            return "not in fit" if not x["entered"] else f"{x['effect']:+.3f} ({x['flagged']})"
        for h, row in w["refit_tax_date"][last].items():
            lines.append(f"| {h} | {eff(row['control'])} | {eff(row['arm'])} |")
        lines.append("")
    lines += [
        "## The reading of the label",
        "",
        "The declared reading uses the October-window targets of the years but 2019 and 2025 (`supported`: a gain on grid CRPS or on upper-tail twCRPS with no cost on the "
        "other; `not supported`: a cost on either, or an identical score; else `undecided`):",
        "",
        "| window | reading |",
        "|---|---|",
    ]
    for window, row in r["label_reading"].items():
        lines.append(f"| {window} | {row[OTHER_OCTOBER]} |")
    lines += [
        "",
        "## What this does and does not show",
        "",
        "It is development data on days already seen. It does not adopt the label, change the frozen candidate or settle the data meaning of `tax_date`. The October windows "
        "are few days (see the group sizes above); a group below the study's minimum is not tested and is listed with its size in `result.json`. The model's level still "
        "counts an October-window day as an ordinary day, as the control does; a level that also skips those days is a different arm and was not run. B2 and the calendar "
        "ranker, which #965 tested, are not re-run. The label changes the fitted `tax_date` term, so the arm's forecast differs from the control's on days far from any October "
        "window (the count is stated under each window's heading); a pooled move is therefore not a move on the October windows, and the October-window rows are the ones "
        "that speak to the label. Where the leave-out reading is below the minimum group size it is not read, and the means beside it are descriptive only.",
        "",
        "Every figure on this page is in [`result.json`](s3c-ann-net-october-1455/result.json).",
        "",
    ]
    return "\n".join(lines)


def page_command(args) -> int:
    r = json.loads(Path(args.score).read_text(encoding="utf-8"))
    Path(args.output).write_text(render(r), encoding="utf-8")
    return 0


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="command", required=True)
    s = sub.add_parser("score")
    s.add_argument("--panel", type=Path, required=True)
    s.add_argument("--output", type=Path, required=True)
    s.add_argument("--draws", type=int, default=sp.DRAWS)
    s.add_argument("--workers", type=int, default=4)
    g = sub.add_parser("page")
    g.add_argument("--score", type=Path, required=True)
    g.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)
    return {"score": score_command, "page": page_command}[args.command](args)


if __name__ == "__main__":
    raise SystemExit(main())
