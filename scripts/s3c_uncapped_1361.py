"""(s3c-ann-net) with and without the Standing Repo Facility cap, scored beside each other (#1361; H5, registration design; development tier).

Her ruling of 2 November 2026 (chat, relayed on #1361), after an outside publication-readiness review: report an uncapped version of the candidate as a
secondary result, so that the cap is not what rules out large upward moves. A development study, never a verdict. It writes JSON and Markdown to the paths it
is given and nothing into `docs/runs/`. Every choice is in `metadata/s3c_uncapped_1361.json`, which this script refuses to read unless it is committed and
unchanged.

The candidate is (s3c-ann-net) as `docs/research/h5-candidate.json` states it: the walk of `repo_model.s3c_announced.ANN_NET_ARM` with every quantile clipped
at the SRF line (margin 0 bp) on target days at full allotment (`repo_model.s3c_candidate`). The uncapped version is the same walk with the cap off and nothing
else changed. The walk, the frames and the machinery are #1288's, #1255's and #1241's, loaded as they are; no module in `src/` is edited. The study refuses to
write a record if the candidate does not reproduce #1288's pooled means, or if the two versions differ on a cell to which no cap applies.

It measures grid CRPS averaged over h = 1..5 (primary), upper-tail twCRPS (key secondary) and the Brier score of P(> +5 bp) on scoring protocol v1's
studentized stationary bootstrap read on the bound on mean d (her #1009 ruling), with the skill interval beside, pooled and split by lead, regime,
pressure-day type of the target day, target month, and full-allotment target days against the others; reports the coverage of the central 90% and 50% bands and
the exceedance rate of q95 of both versions in the same groups (rates, not tested); and reports how often and by how much the cap binds.

Commands, from a clone of the branch:

    PYTHONPATH=src python3 -m repo_model.cli build --raw-root tests/fixtures/snapshots/funding_inputs \\
        --output PUB.csv --build-cutoff 2026-09-08T21:31:42+00:00 --decision-time 16:00:00
    PYTHONPATH=src python3 -m repo_model.cli verify-panel PUB.csv --manifest metadata/funding_panel_manifest.json
    PYTHONPATH=src python3 scripts/s3c_uncapped_1361.py score --panel PUB.csv \\
        --output docs/research/s3c-uncapped-1361/result.json
    PYTHONPATH=src python3 scripts/s3c_uncapped_1361.py page \\
        --score docs/research/s3c-uncapped-1361/result.json --output docs/research/s3c-uncapped-1361-result.md

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
    spec = importlib.util.spec_from_file_location(alias, REPO / "scripts" / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[alias] = module
    spec.loader.exec_module(module)
    return module


from repo_model import announced_iorb, policy_events, s3c_announced, s3c_candidate, s3c_net  # noqa: E402
from repo_model import scoring_protocol as sp, spread_mr_state_calendar as sc  # noqa: E402
from repo_model import spread_mr_calendar as cal  # noqa: E402
from repo_model.baseline import panel_sha256  # noqa: E402
from repo_model.evaluation_splits import load_split_declaration  # noqa: E402
from repo_model.exploration import EXPLORATORY_END, require_exploratory_window  # noqa: E402

#: #1288's script (and through it #1273's, #1255's, #1241's and #1229's), loaded under an alias of its own so that the pickling of the worker pool's tasks
#: does not meet another test module's copy.
m1288 = _load("s3c_announced_settlement_1288", "s3c_announced_settlement_1288_in_1361")
m1273, m1255, k = m1288.m1273, m1288.m1255, m1288.k
c, s686, s761, load_daily_panel = m1288.c, m1288.s686, m1288.s761, m1288.load_daily_panel

DECLARATION = REPO / "metadata" / "s3c_uncapped_1361.json"
RECORD_1288 = REPO / "docs" / "research" / "s3c-announced-settlement-1288" / "result.json"
SEED = 1361
m1273.SEED = SEED  # the unstudentized interval of #1273 reads the seed of its own module
LAST_DAY = EXPLORATORY_END
WINDOW_LAST = m1288.WINDOW_LAST
WINDOWS = m1288.WINDOWS
WINDOW_TITLES = m1288.WINDOW_TITLES
B1P = m1288.B1P
BENCHMARKS = m1288.BENCHMARKS
CAPPED, UNCAPPED = "sc_s3c_ann_net", "sc_s3c_ann_net_uncapped"
MODELS = BENCHMARKS + (CAPPED, UNCAPPED)
LABELS = {"B1": "B1", B1P: "B1' (#960)", "B2": "B2", CAPPED: "(s3c-ann-net), the candidate", UNCAPPED: "(s3c-ann-net-uncapped)"}
TESTED = m1288.TESTED
BAND90 = m1288.BAND90
BAND50 = (sp.GRID.index(0.25), sp.GRID.index(0.75))
Q95 = sp.GRID.index(0.95)
Q99 = sp.GRID.index(0.99)
RATES = ("b90_closed", "b50_closed", "q95_exceed")
METRIC_NAMES = TESTED + RATES
METRIC_TITLES = dict(m1288.METRIC_TITLES, b50_closed="50% band coverage", q95_exceed="q95 exceedance")
MIN_GROUP_DAYS = m1288.MIN_GROUP_DAYS
FULL_SPLIT = "full_allotment"
FULL_LABEL = "target days at full allotment"
OTHER_LABEL = "other target days"
LEADS = tuple(sp.HORIZONS)
DECISION_TIME = k.DECISION_TIME


def committed_declaration(path: Path = DECLARATION) -> dict:
    """The declaration, refused unless it is committed and unchanged since `HEAD`."""

    return s686.committed_declaration(path)


def plan() -> List[str]:
    """What the uncapped version is tested against: the candidate, then the benchmarks."""

    return [CAPPED] + list(BENCHMARKS)


# -- the cells -----------------------------------------------------------------------------------------------------------


def cell_table(frame, forecasts: Mapping[date, Mapping[int, Sequence[float]]], last_day: date) -> Dict[str, Dict[Tuple[date, int], float]]:
    """#1273's cells (both losses, the Brier cell of P(> +5 bp), the closed hit of the central 90% band) with the closed hit of the central 50% band and
    the q95 exceedance (1 when the outcome is strictly above the 0.95 quantile) added."""

    out = m1273.cell_table(frame, forecasts, last_day)
    out["b50_closed"], out["q95_exceed"] = {}, {}
    lo, hi = BAND50
    for d in sorted(forecasts):
        for h in LEADS:
            q, y = forecasts[d][h], frame.outcome[frame.target(d, h)]
            out["b50_closed"][(d, h)] = 1.0 if q[lo] <= y <= q[hi] else 0.0
            out["q95_exceed"][(d, h)] = 1.0 if y > q[Q95] else 0.0
    return out


def cell_lines(frame, register: Sequence[policy_events.PolicyEntry]) -> Dict[Tuple[date, int], Optional[float]]:
    """The line the cap uses in each scored cell (`None` where the cap does not apply), as known at the cell's decision instant."""

    return {(d, h): s3c_candidate.cap_line(register, k.decision_instant(d), frame.target(d, h)) for d in frame.days for h in LEADS}


def allotment_groups(frame, lines: Mapping[Tuple[date, int], Optional[float]]):
    """`(split, label, grain, members)`: the target days with a capped cell (the facility at full allotment as known at the decision) and the others."""

    targets = sorted({frame.target(d, h) for d in frame.days for h in LEADS})
    full = sorted({frame.target(d, h) for (d, h), line in lines.items() if line is not None})
    other = [t for t in targets if t not in set(full)]
    out = []
    if full:
        out.append((FULL_SPLIT, FULL_LABEL, "target", full))
    if other:
        out.append((FULL_SPLIT, OTHER_LABEL, "target", other))
    return out


# -- the checks ----------------------------------------------------------------------------------------------------------


def check_off_cap(frame, capped, uncapped, lines) -> dict:
    """The two versions are cell for cell the same where no cap applies, and the capped one is the uncapped one clipped at the line where it does.

    Raises:
        ValueError: a cell without a line differs between the versions, or a cell with a line is not the uncapped quantiles clipped at it.
    """

    off = on = 0
    for d in frame.days:
        for h in LEADS:
            line = lines[(d, h)]
            a, b = list(capped[d][h]), list(uncapped[d][h])
            if line is None:
                if a != b:
                    raise ValueError(f"the cell ({d}, h={h}) has no cap and the two versions differ")
                off += 1
            else:
                if a != [min(x, line + s3c_candidate.MARGIN_BP) for x in b]:
                    raise ValueError(f"the cell ({d}, h={h}) is not the uncapped quantiles clipped at the line")
                on += 1
    return {"cells_without_a_line": off, "cells_with_a_line": on, "cells_without_a_line_identical": True}


def require_candidate_reproduced(results: Mapping[str, dict], record: Mapping[str, object], tolerance: float = 1e-9) -> dict:
    """The candidate's pooled means here equal #1288's record's: the walk and the cap are the same.

    Raises:
        ValueError: a pooled mean of the candidate differs from the record's by more than `tolerance`.
    """

    out: Dict[str, dict] = {}
    for window, result in results.items():
        a = record["windows"][window]["groups"]["pooled"]["all decision days"]
        b = result["groups"]["pooled"]["all decision days"]
        out[window] = {}
        for m in TESTED:
            here, there = b[m]["means"][CAPPED], a[m]["means"][CAPPED]
            if abs(here - there) > tolerance:
                raise ValueError(f"{window}: the candidate's {m} is {here} here and {there} in #1288's record")
            out[window][m] = {"here": here, "there": there, "difference": here - there}
    return out


def binding(frame, uncapped, capped, lines) -> dict:
    """How often and by how much the cap binds, over all scored cells and by lead.

    A cell binds when the uncapped version has a quantile above the line. For the 0.95 level, the 0.99 level and the largest quantile, the move is the
    uncapped value less the capped one, summarised over the cells in which it is positive. `outcome_above_line` counts the cells at full allotment whose
    outcome is above the line.
    """

    keys = ("all",) + tuple(str(h) for h in LEADS)
    out: Dict[str, dict] = {}
    for key in keys:
        out[key] = {"cells": 0, "at_full_allotment": 0, "binds": 0, "outcome_above_line": 0,
                    **{name: {"moved": 0, "sum": 0.0, "max_move": None} for name in ("q95", "q99", "max_quantile")}}
    for d in frame.days:
        for h in LEADS:
            rows = (out["all"], out[str(h)])
            for r in rows:
                r["cells"] += 1
            line = lines[(d, h)]
            if line is None:
                continue
            u, p = uncapped[d][h], capped[d][h]
            top = max(u)
            moves = {"q95": u[Q95] - p[Q95], "q99": u[Q99] - p[Q99], "max_quantile": top - max(p)}
            above = frame.outcome[frame.target(d, h)] > line
            for r in rows:
                r["at_full_allotment"] += 1
                r["binds"] += 1 if top > line else 0
                r["outcome_above_line"] += 1 if above else 0
                for name, move in moves.items():
                    if move > 0.0:
                        e = r[name]
                        e["moved"] += 1
                        e["sum"] += move
                        e["max_move"] = move if e["max_move"] is None else max(e["max_move"], move)
    for r in out.values():
        r["share_binds"] = r["binds"] / r["at_full_allotment"] if r["at_full_allotment"] else None
        for name in ("q95", "q99", "max_quantile"):
            e = r[name]
            e["mean_move"] = e["sum"] / e["moved"] if e["moved"] else None
            del e["sum"]
    return out


# -- one window ----------------------------------------------------------------------------------------------------------


def candidate_walk(window: str, frame, panel, splits, registry, results, auctions, first: Optional[date]):
    """The walk of `ANN_NET_ARM` over #1255's decision days of `window`: the uncapped forecasts of every scored decision day.

    Raises:
        ValueError: the walk has no forecast of a scored decision day, or it is not (s3c-net) at lead 1.
    """

    days = m1288.candidate_days(frame, window, first)
    settings = dict(registry=registry, decision_time=DECISION_TIME, splits=splits)
    states = s3c_net.constant_states(panel)
    iorb = announced_iorb.load_announcements(c.IORB_TABLE)
    both = s3c_announced.AnnouncedTermTable(panel, iorb, results, decision_time=DECISION_TIME)
    net_table = s3c_announced.AnnouncedNetSizeTable(panel, auctions, decision_time=DECISION_TIME)
    walk = sc.walk(panel, days, both, states, (s3c_announced.ANN_NET_ARM,), sizes=net_table, **settings)
    found = walk.forecasts[s3c_announced.ANN_NET_ARM.name]
    for d in frame.days:
        if d not in found:
            raise ValueError(f"the walk has no forecast of the scored decision day {d}")
    return walk, {d: found[d] for d in frame.days}


def build(window: str, panel, splits, registry, table, register, results, auctions, first: Optional[date]):
    """#1255's frame of `window` with the candidate and its uncapped version: `(frame, notes, lines, groups_fn)`."""

    frame, notes, _mine, _cells, groups_fn = m1255.build(window, panel, splits, registry, table, register, first)
    walk, raw = candidate_walk(window, frame, panel, splits, registry, results, auctions, first)
    capped = m1255.s3c_forecasts(frame, register, raw)
    lines = cell_lines(frame, register)
    check = check_off_cap(frame, capped, raw, lines)
    forecasts = {name: frame.forecasts[name] for name in BENCHMARKS}
    forecasts[CAPPED], forecasts[UNCAPPED] = capped, raw
    frame.forecasts = {name: {d: forecasts[name][d] for d in frame.days} for name in MODELS}
    return frame, dict(notes, refits_candidate=len(walk.fits)), lines, groups_fn, check


_STATE: Dict = {}


def _pairs_task(job):
    split, label, grain, metric, members = job
    series = _STATE["series"][(grain, metric)]
    out: Dict[str, dict] = {}
    for name in plan():
        days = list(members)
        if m1288._identical(series, UNCAPPED, name, days):
            out[name] = {"identical": True, "days": len(days)}
            continue
        out[name] = s761.run_pairs({name: series[name]}, series[UNCAPPED], days, seed=SEED, draws=_STATE["draws"], mean_d_fallback=True)[name]
        if "undefined" in out[name]:
            out[name]["unstudentized"] = m1273.unstudentized(series, UNCAPPED, name, days)
    return (split, label, metric), out


def run_jobs(jobs, workers: int):
    with multiprocessing.get_context("fork").Pool(workers) as pool:
        return pool.map(_pairs_task, jobs, chunksize=1)


def run_window(window: str, panel, splits, registry, table, register, results, auctions, args) -> dict:
    frame, notes, lines, groups_fn, off_cap = build(window, panel, splits, registry, table, register, results, auctions, args.first)
    last = WINDOW_LAST[window]
    labels = c.day_labels(frame, table)
    pressure = k.pressure_labels(frame, sorted(labels))
    cells = {m: cell_table(frame, frame.forecasts[m], last) for m in MODELS}
    for m in MODELS:
        official = sp.day_scores(frame.forecasts[m], frame.outcome, frame.dates, score=sp.grid_crps)
        mean = s686.by_decision(cells[m]["grid_crps"])
        if set(official) != set(mean) or any(abs(official[d] - mean[d]) > 1e-9 for d in mean):
            raise SystemExit(f"grid CRPS of {m}: the cell means differ from scoring_protocol.day_scores")
    groups = list(groups_fn(frame, labels, pressure)) + allotment_groups(frame, lines)
    series: Dict[Tuple[str, str], Dict[str, Dict[date, float]]] = {}
    for _s, _l, grain, _m in groups:
        for metric in METRIC_NAMES:
            if (grain, metric) not in series:
                series[(grain, metric)] = {m: c.series_of(frame, cells[m][metric], grain) for m in MODELS}
    _STATE.update(series=series, draws=args.draws, reps=args.reps)
    m1273._STATE.update(series=series, draws=args.draws, reps=args.reps)

    jobs, skipped = [], {}
    for split, label, grain, members in groups:
        if len(members) < MIN_GROUP_DAYS:
            skipped[f"{split}/{label}"] = len(members)
            continue
        for metric in TESTED:
            jobs.append((split, label, grain, metric, tuple(members)))
    done = run_jobs(jobs, args.workers)

    result: dict = {
        "notes": notes, "refits": notes["refits_candidate"], "groups": {}, "skipped_groups": skipped, "off_cap": off_cap,
        "binding": binding(frame, frame.forecasts[UNCAPPED], frame.forecasts[CAPPED], lines),
        "lead_difference": {"uncapped_against_candidate": m1288.lead_difference(frame, CAPPED, UNCAPPED)},
    }
    for split, label, grain, members in groups:
        entry = result["groups"].setdefault(split, {}).setdefault(label, {"days": len(members)})
        for metric in METRIC_NAMES:
            ser = series[(grain, metric)]
            entry[metric] = {"means": {m: sum(ser[m][d] for d in members) / len(members) for m in MODELS}, "vs": {}}
    for (split, label, metric), payload in done:
        result["groups"][split][label][metric]["vs"][UNCAPPED] = payload
    result["pressure_day_type_counts"] = {x: sum(1 for t in pressure.values() if t == x) for x in sorted(set(pressure.values()))}
    return result


def score(args) -> int:
    declaration = committed_declaration()
    panel_path = Path(args.panel)
    published_sha = panel_sha256(panel_path)
    panel = [row for row in load_daily_panel(panel_path) if row.date <= LAST_DAY]
    require_exploratory_window([row.date for row in panel], where="scripts/s3c_uncapped_1361")
    splits = load_split_declaration(c.SPLITS)
    registry = json.loads(c.SOURCES.read_text(encoding="utf-8"))
    register = policy_events.load_register()
    table = cal.TermTable(panel, announced_iorb.load_announcements(c.IORB_TABLE), decision_time=c.DECISION_TIME)
    auctions = m1273.load_auctions()
    results = m1288.load_results()
    result: dict = {
        "issue": 1361, "declaration": str(DECLARATION.relative_to(REPO)), "panel_sha256": published_sha,
        "subset_from": None if args.first is None else args.first.isoformat(), "label": "development, not a verdict",
        "seed": SEED, "draws": args.draws, "reps": args.reps, "models": list(MODELS), "candidate": CAPPED, "uncapped": UNCAPPED,
        "margin_bp": s3c_candidate.MARGIN_BP, "windows": {}, "reading_rules": declaration["reading_rules"],
    }
    for window in WINDOWS:
        result["windows"][window] = run_window(window, panel, splits, registry, table, register, results, auctions, args)
    if args.first is None:
        record = json.loads(RECORD_1288.read_text(encoding="utf-8"))
        result["candidate_against_1288"] = require_candidate_reproduced(result["windows"], record)
    else:
        result["candidate_against_1288"] = {}
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    Path(args.output).write_text(json.dumps(result, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    return 0


# -- the page ------------------------------------------------------------------------------------------------------------


def _vs(group: Optional[Mapping[str, object]], metric: str, reference: str) -> Optional[dict]:
    return m1288.m1273._vs(group, metric, UNCAPPED, reference)


def cell(row: Optional[dict]) -> str:
    return m1273.cell(row)


def mean_table(group: Mapping[str, object]) -> List[str]:
    """Every model's mean of the three scores and the three rates in one group."""

    out = ["| model | " + " | ".join(METRIC_TITLES[m] for m in METRIC_NAMES) + " |", "|---|" + "---|" * len(METRIC_NAMES)]
    for m in MODELS:
        out.append(f"| {LABELS[m]} | " + " | ".join(f"{group[x]['means'][m]:.3f}" if x in ("grid_crps", "upper_tail_twcrps") else f"{group[x]['means'][m]:.4f}"
                                                     for x in METRIC_NAMES) + " |")
    return out


def against_table(group: Mapping[str, object]) -> List[str]:
    out = [f"| {LABELS[UNCAPPED]} against | " + " | ".join(METRIC_TITLES[m] for m in TESTED) + " |", "|---|" + "---|" * len(TESTED)]
    for ref in plan():
        out.append(f"| {LABELS[ref]} | " + " | ".join(cell(_vs(group, m, ref)) for m in TESTED) + " |")
    return out


def split_table(window: Mapping[str, object], split: str, order: Optional[Sequence[str]] = None) -> List[str]:
    """The uncapped version against the candidate in each group of a split: the three scores, the difference with its interval and the reading."""

    labels = window["groups"].get(split, {})
    out = [f"| {split.replace('_', ' ')} | days | " + " | ".join(METRIC_TITLES[m] for m in TESTED) + " |", "|---|---|" + "---|" * len(TESTED)]
    for label in (order if order is not None else sorted(labels)):
        if label not in labels:
            continue
        g = labels[label]
        skipped = f"{split}/{label}" in window["skipped_groups"]
        out.append(f"| {label} | {g['days']} | " + " | ".join("not tested (fewer than 20 days)" if skipped else cell(_vs(g, m, CAPPED)) for m in TESTED) + " |")
    return out if len(out) > 2 else []


def rate_table(window: Mapping[str, object], split: str) -> List[str]:
    """The three rates of the candidate and of the uncapped version in each group of a split (nominal: 90%, 50%, 5%)."""

    labels = window["groups"].get(split, {})
    cols = [f"{METRIC_TITLES[m]} {LABELS_SHORT[x]}" for m in RATES for x in (CAPPED, UNCAPPED)]
    out = [f"| {split.replace('_', ' ')} | days | " + " | ".join(cols) + " |", "|---|---|" + "---|" * len(cols)]
    for label in sorted(labels):
        g = labels[label]
        vals = [f"{g[m]['means'][x]:.3f}" for m in RATES for x in (CAPPED, UNCAPPED)]
        out.append(f"| {label} | {g['days']} | " + " | ".join(vals) + " |")
    return out if len(out) > 2 else []


LABELS_SHORT = {CAPPED: "(candidate)", UNCAPPED: "(uncapped)"}


def binding_table(bind: Mapping[str, dict]) -> List[str]:
    out = ["| lead | cells | at full allotment | cap binds | share | outcome above the line | q95 moved: mean / largest (bp) | q99 moved: mean / largest (bp) | "
           "largest quantile moved: mean / largest (bp) |", "|---|---|---|---|---|---|---|---|---|"]

    def move(e):
        return "none" if not e["moved"] else f"{e['moved']}: {e['mean_move']:.2f} / {e['max_move']:.2f}"

    for key in ("all",) + tuple(str(h) for h in LEADS):
        b = bind[key]
        share = "n/a" if b["share_binds"] is None else f"{b['share_binds']:.3f}"
        out.append(f"| {'all' if key == 'all' else 'h=' + key} | {b['cells']} | {b['at_full_allotment']} | {b['binds']} | {share} | {b['outcome_above_line']} | "
                   f"{move(b['q95'])} | {move(b['q99'])} | {move(b['max_quantile'])} |")
    return out


def headline(r: Mapping[str, object]) -> str:
    parts = []
    for window, text in (("2026", "On the 2026 development days"), ("development", "on the development window")):
        entry = r["windows"].get(window, {}).get("groups", {}).get("pooled", {}).get("all decision days")
        parts.append(f"{text} the uncapped version against the candidate, grid CRPS: {cell(_vs(entry, 'grid_crps', CAPPED))}")
    return "; ".join(parts) + "."


def question() -> List[str]:
    return [
        "## Questions for Eleonora (marked; defaults change no claim)", "",
        "**Question 1. How the uncapped version is reported in the registration.** The directive says the uncapped version is logged and scored prospectively "
        "beside the candidate, reported and not deciding. The draft of the section is `docs/decisions/drafts/h5-uncapped-secondary.md`. The full-allotment "
        "period holds few days, so a tail rate on it carries a wide interval whichever version is read.", "",
        "**Options** (the default applies if you have not answered by the next 5 pm batch):", "",
        "1. **Report it as drafted: scored beside the candidate on every confirmation day, split by full-allotment and other days, reported only** (default). "
        "Nothing the project claims changes.",
        "2. **Also report the cap's binding frequency and size on the confirmation days** as a standing table next to the score, so that a reader sees when the "
        "cap decided the forecast.",
        "3. **Do not log it**, and report this page's development figures only.", "",
        "**Question 2. What follows from this result.** (s3c-ann-net) stays the H5 candidate. Whether the cap stays in the candidate is a choice for her, "
        "and the figures above rest on days already seen, most of them before the facility was at full allotment.", "",
        "**Options** (the default applies if you have not answered by the next 5 pm batch):", "",
        "1. **The candidate keeps the cap and nothing changes** (default).",
        "2. **Draft a directive that tests the candidate without the cap prospectively**, on the confirmation days only, under the scoring protocol.", ""]


def render(r: dict) -> str:
    out = [
        "# (s3c-ann-net) without the SRF cap: the candidate beside its uncapped version (#1361)", "",
        "**What does the Standing Repo Facility cap do to the candidate, and how often does it bind?** " + headline(r), "",
        "**Hypothesis and step:** H5 (primary goal), registration design. **Development data, not a verdict** (scoring protocol v1, #640). Her ruling of 2 "
        "November 2026 (chat, relayed on #1361): report an uncapped version of the candidate as a secondary result. **(s3c-ann-net) stays the candidate; it does "
        "not change.** Nothing is registered or published and no claim changes. The uncapped version is the candidate's walk with the cap off and nothing "
        "else changed (`metadata/s3c_uncapped_1361.json`, committed before any score); both are read at the 16:00 decision instant of the records of this "
        "family, so the candidate reproduces #1288's record"
        + (" (pooled means equal to 1e-9)." if r.get("candidate_against_1288") else " (not checked in a subset run).") + "", "",
        "**How to read the tables.** A difference is the candidate's loss less the uncapped version's: positive favours the uncapped version. A reading is "
        "taken from the 90% interval of mean d (her #1009 ruling), never from a point estimate. The two windows are kept apart. The cap applies only to target "
        "days at full allotment (from 11 December 2025), so every difference below comes from those days; on all others the two versions are the same "
        "forecast, and a group of such days shows `identical`. The rates are means over cells, not tested: coverage of the central 90% band (nominal 0.90), "
        "of the central 50% band (nominal 0.50) and the exceedance rate of q95 (nominal 0.05).", ""]
    for window in WINDOWS:
        w = r["windows"].get(window)
        if w is None:
            continue
        pooled = w["groups"]["pooled"]["all decision days"]
        out += [f"## {WINDOW_TITLES[window]}", "", f"{pooled['days']} decision days; refits of the candidate's walk: {w['refits']}. "
                f"Cells without a cap that were checked identical between the versions: {w['off_cap']['cells_without_a_line']}; cells with a cap: "
                f"{w['off_cap']['cells_with_a_line']}.", "", "### Pooled", ""]
        out += mean_table(pooled) + [""] + against_table(pooled) + [""]
        out += ["### Full-allotment target days against the others", ""]
        out += (split_table(w, FULL_SPLIT, (FULL_LABEL, OTHER_LABEL)) or ["No target day of this window is at full allotment."]) + [""]
        out += rate_table(w, FULL_SPLIT) + [""]
        out += ["### How often and by how much the cap binds", "",
                "A cell binds when the uncapped version has a quantile above the line (IORB + 10 bp). The moves are the uncapped value less the capped one, "
                "over the cells in which the quantile moves. `outcome above the line` counts the cells at full allotment whose outcome is above the line.", ""]
        out += binding_table(w["binding"]) + [""]
        for split, title in (("lead", "By lead"), ("regime", "By regime"), ("pressure_day_type", "By pressure-day type of the target day"),
                             ("month", "By target month")):
            table = split_table(w, split)
            if table:
                out += [f"### {title}", ""] + table + [""]
        for split in ("regime", "pressure_day_type"):
            table = rate_table(w, split)
            if table:
                out += [f"### Rates by {split.replace('_', ' ')}", ""] + table + [""]
        if w["skipped_groups"]:
            out += ["Groups of fewer than 20 days, not tested: " + "; ".join(f"{x} ({n})" for x, n in sorted(w["skipped_groups"].items())) + ".", ""]
    out += ["## What this does and does not show", "",
            "- It shows what the cap does to the candidate's scores on days already seen, and how often and by how much it moves a quantile.",
            "- It does not show how the uncapped version does when the facility is at full allotment for long: the development window holds only the days of "
            "December 2025 after it, and 2026 holds the rest. A tail rate on so few days is not read.",
            "- It is a development figure on days already seen, not a verdict. The confirmation days give the verdict.",
            "- Both versions are read at the 16:00 instant; the move to 18:00 (#1312) is a separate re-run.", ""]
    out += question()
    return "\n".join(out)


def page(args) -> int:
    r = json.loads(Path(args.score).read_text(encoding="utf-8"))
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    Path(args.output).write_text(render(r), encoding="utf-8")
    return 0


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="command", required=True)
    s = sub.add_parser("score", help="walk the candidate's arm, score it capped and uncapped on both windows")
    s.add_argument("--panel", required=True)
    s.add_argument("--output", required=True)
    s.add_argument("--draws", type=int, default=sp.DRAWS)
    s.add_argument("--reps", type=int, default=2000, help="bootstrap resamples of the unstudentized interval")
    s.add_argument("--workers", type=int, default=4)
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
