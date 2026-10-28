"""The candidate (s3c): (s3) capped at the Standing Repo Facility line from full allotment onwards, scored against (s3), (a), B1, B1' and B2
(#1255; H5 step 3, ledger item 61 on #1116).

A development study, never a verdict. It writes JSON and Markdown to the paths it is given and nothing into `docs/runs/`. Every choice is
in `metadata/s3c_candidate_1255.json`, which this script refuses to read unless it is committed and unchanged. The candidate is
`repo_model.s3c_candidate` (the cap at the line on target days at full allotment, margin 0 bp; the line and the clip are #1241's
`repo_model.srf_line`). The frames and the machinery are the predecessors' and are loaded as they are: the development window of #1145 and
#1241 (`scripts/srf_cap_1241.py`: targets up to 2025-12-31) and the 2026 development days of #1229 and #1252 (`scripts/s3_2026_check_1222.py`:
targets 2026-01-02 to 2026-09-03, the near-blind tier open since GO #151). The blind tier and every lockbox
day are refused by the frames' own guards.

It measures (s3c) against (s3), (a), B1, B1' (#960) and B2 on both windows on grid CRPS averaged over h = 1..5 (primary) and upper-tail
twCRPS (key secondary), scoring protocol v1's studentized stationary bootstrap read on the bound on mean d (her #1009 ruling) with the skill
interval beside, split as the predecessors split. It also checks that every forecast cell whose target is before full allotment (before
2025-12-11) is (s3)'s, element for element, and that the decision days all of whose targets are before it score identically.

The walks take minutes and the paired tests are the longer part, so the run is a cloud run unless the measured time says otherwise.
Commands, from a clone of the branch:

    PYTHONPATH=src python3 -m repo_model.cli build --raw-root tests/fixtures/snapshots/funding_inputs \\
        --output PUB.csv --build-cutoff 2026-09-08T21:31:42+00:00 --decision-time 16:00:00
    PYTHONPATH=src python3 -m repo_model.cli verify-panel PUB.csv --manifest metadata/funding_panel_manifest.json
    PYTHONPATH=src python3 scripts/s3c_candidate_1255.py score --panel PUB.csv --output docs/research/s3c-candidate-1255/result.json
    PYTHONPATH=src python3 scripts/s3c_candidate_1255.py page \\
        --score docs/research/s3c-candidate-1255/result.json --output docs/research/s3c-candidate-1255-result.md

Stdlib only.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
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
        return held  # another loader in this process already holds the alias: share it, so pickled task names stay one object (#1294)
    spec = importlib.util.spec_from_file_location(alias, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[alias] = module
    spec.loader.exec_module(module)
    return module


from repo_model import announced_iorb, policy_events, s3c_candidate  # noqa: E402
from repo_model import scoring_protocol as sp, spread_mr_calendar as cal, turn_days  # noqa: E402
from repo_model.baseline import panel_sha256  # noqa: E402
from repo_model.data import load_daily_panel  # noqa: E402
from repo_model.evaluation_splits import load_split_declaration  # noqa: E402
from repo_model.exploration import EXPLORATORY_END, require_exploratory_window  # noqa: E402

#: #1241's script (the line, the paired-test tasks, the format of a cell) and #1229's (the walk and the frame of the 2026 days), each loaded
#: under an alias of its own so that the pickling of the worker pool's tasks does not meet another test module's copy.
k = _load("srf_cap_1241", "srf_cap_1241_in_1255")
d1222 = _load("s3_2026_check_1222", "s3_2026_check_1222_in_1255")
c, s686 = k.c, k.s686
d1145 = k.d1145

DECLARATION = REPO / "metadata" / "s3c_candidate_1255.json"
SEED = 1255
k.SEED = SEED  # the paired-test and interval tasks of #1241 read the seed of their own module
LAST_DAY = EXPLORATORY_END
S3, A, B1P = k.S3, k.A, k.B1P
S3C = "sc_s3c"
BENCHMARKS = ("B1", B1P, "B2")
#: What (s3c) is tested against, (s3) first; and every model whose mean is reported.
REFERENCES = (S3, A) + BENCHMARKS
MODELS = BENCHMARKS + (A, S3, S3C)
METRIC_NAMES, MIN_GROUP_DAYS = k.METRIC_NAMES, k.MIN_GROUP_DAYS
METRIC_TITLES = k.METRIC_TITLES
#: The first target day at full allotment in the register (`standing_repo-20251210`, effective 11 December 2025): used by the checks only,
#: never by the candidate, which reads the register.
FULL_ALLOTMENT_FIRST = date(2025, 12, 11)
WINDOWS = ("development", "2026")
LABELS = {"B1": "B1", B1P: "B1' (#960)", "B2": "B2", A: "(a) (#941)", S3: "(s3)", S3C: "(s3c) the candidate"}
RECORD_1241 = REPO / "docs" / "research" / "srf-cap-1241" / "result.json"
RECORD_1229 = REPO / "docs" / "research" / "s3-2026-check-1222" / "result.json"


def committed_declaration(path: Path = DECLARATION) -> dict:
    """The declaration, refused unless it is committed and unchanged since `HEAD`."""

    return s686.committed_declaration(path)


# -- the candidate's forecasts -----------------------------------------------------------------------------------------


def s3c_forecasts(frame, register: Sequence[policy_events.PolicyEntry], s3: Mapping[date, Mapping[int, Sequence[float]]]):
    """(s3)'s forecasts with each cell's quantiles clipped at the line where its target is at full allotment (as known at the decision)."""

    return {
        d: {h: s3c_candidate.capped_quantiles(q, register, k.decision_instant(d), frame.target(d, h)) for h, q in per_h.items()}
        for d, per_h in s3.items()
    }


def before_full_allotment(frame, s3, s3c) -> dict:
    """The check the directive asks for: every cell with a target before full allotment is (s3)'s, and so is the score of every decision
    day all of whose targets are before it.

    Raises:
        ValueError: a cell before full allotment differs from (s3)'s.
    """

    cells = same = 0
    days = days_same = 0
    for d in frame.days:
        targets = [frame.target(d, h) for h in sp.HORIZONS]
        before = [t < FULL_ALLOTMENT_FIRST for t in targets]
        for h, t, b in zip(sp.HORIZONS, targets, before):
            if b:
                cells += 1
                if list(s3[d][h]) != list(s3c[d][h]):
                    raise ValueError(f"the cell ({d}, h={h}) has a target before full allotment and (s3c) differs from (s3)")
                same += 1
        if all(before):
            days += 1
            a = sp.day_scores({d: s3[d]}, frame.outcome, frame.dates, score=sp.grid_crps)
            b = sp.day_scores({d: s3c[d]}, frame.outcome, frame.dates, score=sp.grid_crps)
            if a != b:
                raise ValueError(f"the decision day {d} has every target before full allotment and (s3c) scores differently from (s3)")
            days_same += 1
    return {"cells_before": cells, "cells_before_identical": same, "decision_days_before": days, "decision_days_before_identical": days_same,
            "first_full_allotment_target": FULL_ALLOTMENT_FIRST.isoformat()}


def binding(frame, register, s3, s3c) -> dict:
    """The cells at full allotment, the cells in which the cap moves a quantile, and those in which it moves the 0.95 and the 0.99 level."""

    q95, q99 = sp.GRID.index(0.95), sp.GRID.index(0.99)
    out: Dict[str, dict] = {x: {"cells": 0, "at_full_allotment": 0, "moved": 0, "moves_q95": 0, "moves_q99": 0} for x in ("all",) + tuple(str(h) for h in sp.HORIZONS)}
    for d in frame.days:
        for h in sp.HORIZONS:
            row = out[str(h)]
            for r in (row, out["all"]):
                r["cells"] += 1
            line = s3c_candidate.cap_line(register, k.decision_instant(d), frame.target(d, h))
            if line is None:
                continue
            a, b = s3[d][h], s3c[d][h]
            for r in (row, out["all"]):
                r["at_full_allotment"] += 1
                r["moved"] += 1 if list(a) != list(b) else 0
                r["moves_q95"] += 1 if a[q95] != b[q95] else 0
                r["moves_q99"] += 1 if a[q99] != b[q99] else 0
    return out


# -- one window ----------------------------------------------------------------------------------------------------------


def build(window: str, panel, splits, registry, table, register, first: Optional[date]):
    """The frame of a window with the models of `MODELS`: returns `(frame, notes, mine, cell_table, groups_fn)`."""

    if window == "development":
        states = d1145.decision_states(c.SOURCES)
        frame, notes, mine, _lines = k.build_frame(panel, splits, registry, table, states, register, first)
        s3 = dict(frame.forecasts[S3])
        a = {d: mine.forecasts[A][d] for d in frame.days}
        cell_table, groups_fn = k.cell_table, lambda fr, labels, pressure: k.groups_of(fr, labels, pressure, {})
    else:
        frame, notes, mine = d1222.build_frame(panel, splits, registry, table, first)
        s3, a = dict(frame.forecasts[S3]), dict(frame.forecasts[A])
        cell_table, groups_fn = d1222.cell_table, groups_2026
    s3c = s3c_forecasts(frame, register, s3)
    keep = {name: frame.forecasts[name] for name in BENCHMARKS}
    frame.forecasts = {**keep, A: a, S3: s3, S3C: s3c}
    for name in list(frame.forecasts):
        frame.forecasts[name] = {d: frame.forecasts[name][d] for d in frame.days}
    return frame, notes, mine, cell_table, groups_fn


def groups_2026(frame, labels, pressure: Mapping[date, str]):
    """#1229's groups (pooled, by lead, by target month, by calendar target-day type) with the pressure-day types of #1241 and #1252."""

    out = d1222.groups_of(frame, labels)
    by_type: Dict[str, List[date]] = {}
    for t in sorted(pressure):
        by_type.setdefault(pressure[t], []).append(t)
    return out + [("pressure_day_type", label, "target", by_type[label]) for label in sorted(by_type)]


def pair_plan(candidate: str) -> List[str]:
    """What (s3c) is tested against; no other model is a candidate here."""

    return list(REFERENCES) if candidate == S3C else []


def block_plan(candidate: str) -> List[str]:
    """The Politis-White block is reported against (s3)."""

    return [S3] if candidate == S3C else []


k.pair_plan, k.block_plan = pair_plan, block_plan


def run_window(window: str, panel, splits, registry, table, register, args) -> dict:
    frame, notes, mine, cell_table, groups_fn = build(window, panel, splits, registry, table, register, args.first)
    labels = c.day_labels(frame, table)
    targets = sorted(labels)
    pressure = k.pressure_labels(frame, targets)
    s3, s3c = frame.forecasts[S3], frame.forecasts[S3C]
    check = before_full_allotment(frame, s3, s3c)
    bind = binding(frame, register, s3, s3c)

    cells = {m: cell_table(frame, frame.forecasts[m]) for m in MODELS}
    for m in MODELS:
        official = sp.day_scores(frame.forecasts[m], frame.outcome, frame.dates, score=sp.grid_crps)
        mean = s686.by_decision(cells[m]["grid_crps"])
        if set(official) != set(mean) or any(abs(official[d] - mean[d]) > 1e-9 for d in mean):
            raise SystemExit(f"grid CRPS of {m}: the cell means differ from scoring_protocol.day_scores")

    groups = groups_fn(frame, labels, pressure)
    series: Dict[Tuple[str, str], Dict[str, Dict[date, float]]] = {}
    for _s, _l, grain, _m in groups:
        for metric in METRIC_NAMES:
            if (grain, metric) not in series:
                series[(grain, metric)] = {m: c.series_of(frame, cells[m][metric], grain) for m in MODELS}
    k._STATE.update(series=series, draws=args.draws, reps=args.reps)

    jobs, skipped = [], {}
    for split, label, grain, members in groups:
        if len(members) < MIN_GROUP_DAYS:
            skipped[f"{split}/{label}"] = len(members)
            continue
        for metric in METRIC_NAMES:
            jobs.append(("pairs", (split, label, grain, metric, S3C, tuple(members))))
            if split == "pooled":
                jobs.append(("block", (split, label, grain, metric, S3C, tuple(members))))
    done = k.run_jobs(jobs, args.workers)

    by_key = {(s_, l_): (g, m) for s_, l_, g, m in groups}
    result: dict = {"notes": notes, "refits": len(mine.fits), "groups": {}, "skipped_groups": skipped, "politis_white": {},
                    "before_full_allotment": check, "binding": bind}
    for kind, (ident, payload) in done:
        split, label, metric, candidate = ident
        if kind == "pairs":
            entry = result["groups"].setdefault(split, {}).setdefault(label, {"days": len(by_key[(split, label)][1])})
            entry.setdefault(metric, {"means": {}, "vs": {}})["vs"][candidate] = payload
        else:
            result["politis_white"].setdefault(split, {}).setdefault(label, {}).setdefault(metric, {})[candidate] = payload
    for split, labels_ in result["groups"].items():
        for label, entry in labels_.items():
            grain, members = by_key[(split, label)]
            for metric in METRIC_NAMES:
                if metric in entry:
                    ser = series[(grain, metric)]
                    entry[metric]["means"] = {m: sum(ser[m][d] for d in members) / len(members) for m in MODELS}
    result["day_type_counts"] = {x: sum(1 for t in labels if x in labels[t]) for x in k.DAY_TYPES + (k.ORDINARY,)}
    result["pressure_day_type_counts"] = {x: sum(1 for t in pressure.values() if t == x) for x in sorted(set(pressure.values()))}
    return result


def against_records(results: Mapping[str, dict]) -> dict:
    """(s3)'s pooled mean scores here against the records of #1241 (development window) and #1229 (2026 days): the walk is the same."""

    out: Dict[str, dict] = {}
    for window, path, issue in (("development", RECORD_1241, 1241), ("2026", RECORD_1229, 1229)):
        if window not in results or not path.exists():
            continue
        there = json.loads(path.read_text(encoding="utf-8"))["groups"]["pooled"]["all decision days"]
        here = results[window]["groups"]["pooled"]["all decision days"]
        out[window] = {"record": str(path.relative_to(REPO)), "issue": issue, "metrics": {
            m: {"here": here[m]["means"][S3], "there": there[m]["means"][S3], "difference": here[m]["means"][S3] - there[m]["means"][S3]}
            for m in METRIC_NAMES}}
    return out


def score(args) -> int:
    declaration = committed_declaration()
    panel_path = Path(args.panel)
    published_sha = panel_sha256(panel_path)
    panel = [row for row in load_daily_panel(panel_path) if row.date <= LAST_DAY]
    require_exploratory_window([row.date for row in panel], where="scripts/s3c_candidate_1255")
    splits = load_split_declaration(c.SPLITS)
    registry = json.loads(c.SOURCES.read_text(encoding="utf-8"))
    register = policy_events.load_register()
    table = cal.TermTable(panel, announced_iorb.load_announcements(c.IORB_TABLE), decision_time=c.DECISION_TIME)
    result: dict = {
        "issue": 1255, "declaration": str(DECLARATION.relative_to(REPO)), "panel_sha256": published_sha,
        "subset_from": None if args.first is None else args.first.isoformat(), "label": "development, not a verdict",
        "seed": SEED, "draws": args.draws, "reps": args.reps, "models": list(MODELS), "candidate": S3C, "margin_bp": s3c_candidate.MARGIN_BP,
        "windows": {}, "reading_rules": declaration["reading_rules"],
    }
    for window in WINDOWS:
        result["windows"][window] = run_window(window, panel, splits, registry, table, register, args)
    result["against_records"] = against_records(result["windows"]) if args.first is None else {}
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    Path(args.output).write_text(json.dumps(result, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    return 0


# -- the page ---------------------------------------------------------------------------------------------------------


WINDOW_TITLES = {"development": "The development window (targets up to 2025-12-31; #1145, #1241)",
                 "2026": "The 2026 development days (targets 2026-01-02 to 2026-09-03; #1229, #1252)"}


def _vs(entry: Mapping[str, object], metric: str, reference: str) -> Optional[dict]:
    if entry is None or metric not in entry:
        return None
    return entry[metric]["vs"].get(S3C, {}).get(reference)


def _cell(row: Optional[dict]) -> str:
    return "n/a" if row is None else f"{k._fmt(row)}: **{k.reading_words(row)}**"


def headline(r: Mapping[str, object]) -> str:
    parts = []
    for window, text in (("2026", "On the 2026 development days"), ("development", "on the development window")):
        entry = r["windows"].get(window, {}).get("groups", {}).get("pooled", {}).get("all decision days")
        row = _vs(entry, "grid_crps", S3)
        parts.append(f"{text} (s3c) against (s3) on grid CRPS: {_cell(row)}")
    return "; ".join(parts) + ". Before full allotment (s3c) is (s3), cell for cell."


def model_table(entry: Mapping[str, object]) -> List[str]:
    out = ["| model | grid CRPS (mean) | upper-tail twCRPS (mean) |", "|---|---|---|"]
    for m in MODELS:
        out.append(f"| {LABELS[m]} | {entry['grid_crps']['means'][m]:.3f} | {entry['upper_tail_twcrps']['means'][m]:.3f} |")
    return out


def against_table(entry: Mapping[str, object]) -> List[str]:
    out = ["| (s3c) against | grid CRPS (skill [90%]; mean d bp [90%]) | upper-tail twCRPS |", "|---|---|---|"]
    for ref in REFERENCES:
        out.append(f"| {LABELS[ref]} | {_cell(_vs(entry, 'grid_crps', ref))} | {_cell(_vs(entry, 'upper_tail_twcrps', ref))} |")
    return out


def split_table(window: dict, split: str, reference: str) -> List[str]:
    labels = window["groups"].get(split, {})
    out = [f"| {split.replace('_', ' ')} | days | grid CRPS | upper-tail twCRPS |", "|---|---|---|---|"]
    for label in sorted(labels):
        entry = labels[label]
        out.append(f"| {label} | {entry['days']} | {_cell(_vs(entry, 'grid_crps', reference))} | {_cell(_vs(entry, 'upper_tail_twcrps', reference))} |")
    return out if len(out) > 2 else []


def binding_table(bind: Mapping[str, dict]) -> List[str]:
    out = ["| lead | cells | at full allotment | cap moves a quantile | moves q95 | moves q99 |", "|---|---|---|---|---|---|"]
    for lead in ("all",) + tuple(str(h) for h in sp.HORIZONS):
        b = bind[lead]
        out.append(f"| {lead} | {b['cells']} | {b['at_full_allotment']} | {b['moved']} | {b['moves_q95']} | {b['moves_q99']} |")
    return out


def render(r: dict) -> str:
    out = [
        "# The candidate (s3c): (s3) capped at the SRF line from full allotment (#1255)", "",
        "**Does the cap, carried from full allotment onwards, improve (s3)?** " + headline(r), "",
        "**Hypothesis and step:** H5 (primary goal), step 3 (the candidate), ledger item 61 on #1116. **Development data, not a verdict** (scoring "
        "protocol v1, #640). Her ruling of 26 October 2026 (chat, relayed on #1255; revises question 1 on #1249): (s3) carries the cap from "
        "full allotment onwards. **(s3c)** is (s3) of #1145, unchanged, with every quantile clipped at `min(q, line + 0 bp)` on target days at "
        "full allotment, and (s3) itself on every other day (`repo_model.s3c_candidate`). Full allotment is read from "
        "`metadata/policy_events.json` as public at the decision instant (the entry of 10 December 2025, effective 11 December, is the "
        "first), and no date is written in the code. The margin of 0 bp is not tuned. Nothing is registered or published and no claim changes. "
        f"Generated by `scripts/s3c_candidate_1255.py page` from `docs/research/s3c-candidate-1255/result.json`, not edited by hand; declared in "
        f"`{r['declaration']}` before any score.", "",
        f"Panel digest `{r['panel_sha256']}`. Studentized stationary bootstrap (ruling 1), mean block {sp.BLOCK_LENGTH} business days, "
        f"{r['draws']:,} draws, seed {r['seed']}, two-sided 90% interval (the lower end is the one-sided 95% bound). Positive mean d favours "
        "(s3c). **A reading (gain, loss, undecided) is taken from the mean-d bound** (her ruling on #1009, 20 October 2026), with the skill "
        "interval beside it. **Caveat (Lens C, #958):** the lag-10 HAC standard error that studentizes the bound is understated about 2x after "
        "2020, so an interval that excludes zero is narrower than it should be. The intervals of a month or a day-type group keep the **current "
        "method** (the group's days, scattered, resampled in date order as if consecutive), which #1221 questions and #1228 will decide; no "
        "pressure-day type is read from them. Where (s3c) differs from (s3) on few days of a group, some resamples have no long-run variance: "
        "the bound is then not computed, the unstudentized interval of mean d is given beside it, and no reading is taken from that.", "",
        "**What kind of look this is.** The 2026 days were already seen by #845, by the #151 final test, by #1229 and by #1252. This is a "
        "check on the candidate she chose, not evidence for a verdict. Before full allotment (s3c) is (s3), so every figure for days before "
        "11 December 2025 is (s3)'s.", ""]
    for window in WINDOWS:
        w = r["windows"].get(window)
        if w is None:
            continue
        n, pooled = w["notes"], w["groups"]["pooled"]["all decision days"]
        chk, bind = w["before_full_allotment"], w["binding"]
        out += [f"## {WINDOW_TITLES[window]}", "",
                f"Scored decision days: {n['scored_decision_days']:,} ({n['first']} to {n['last']}); {w['refits']} refits of (s3). "
                f"Cells with a target before full allotment: {chk['cells_before']:,}, of which identical to (s3): {chk['cells_before_identical']:,}; "
                f"decision days all of whose targets are before it: {chk['decision_days_before']:,}, scoring identically: {chk['decision_days_before_identical']:,}.", "",
                "### Mean scores (pooled)", ""] + model_table(pooled) + ["", "### (s3c) against each reference (pooled)", ""] + against_table(pooled) + [""]
        pw = w["politis_white"].get("pooled", {}).get("all decision days", {}).get("grid_crps", {}).get(S3)
        if pw is not None and "block" in pw:
            out += [f"Politis-White block of the paired differential against (s3), grid CRPS: {pw['block']:.1f} days (the declared block is {sp.BLOCK_LENGTH}).", ""]
        out += ["### Where the cap acts", ""] + binding_table(bind) + [""]
        for split, title in (("regime", "By regime"), ("month", "By target month"), ("pressure_day_type", "By pressure-day type of the target day"),
                             ("lead", "By lead"), ("target_day_type", "By calendar target-day type")):
            table = split_table(w, split, S3)
            if table:
                out += [f"### {title}: (s3c) against (s3)", ""] + table + [""]
        for split, title in (("regime", "By regime"), ("month", "By target month"), ("pressure_day_type", "By pressure-day type")):
            for ref in (A, "B1", B1P, "B2"):
                table = split_table(w, split, ref)
                if table:
                    out += [f"### {title}: (s3c) against {LABELS[ref]}", ""] + table + [""]
        if w["skipped_groups"]:
            out += ["Groups of fewer than 20 days, listed and not tested: " + ", ".join(f"{x} ({n_})" for x, n_ in sorted(w["skipped_groups"].items())) + ".", ""]
    if r.get("against_records"):
        out += ["## Reproduction of the predecessors' (s3)", ""]
        for window, rec in r["against_records"].items():
            out += [f"{WINDOW_TITLES[window].split(' (')[0]}: (s3)'s pooled mean here against `{rec['record']}` (#{rec['issue']}): " + "; ".join(
                f"{METRIC_TITLES[m]} {v['here']:.6f} against {v['there']:.6f} (difference {v['difference']:+.2e})" for m, v in rec["metrics"].items()) + ". The walk is the same one.", ""]
    out += question(r)
    return "\n".join(out).rstrip() + "\n"


def question(r: Mapping[str, object]) -> List[str]:
    return [
        "## Questions for Eleonora (marked; defaults change no claim)", "",
        "**Question 1. Places that still say (s3) where they name the H5 candidate.** A follow-up updates them after she merges this; none is "
        "edited here. In the tree on main: `docs/research/h5-candidate.json` (the one file the results page, the Colab notebooks of #1176 and "
        "`scripts/research_view.py` read the candidate from: `candidate` is `sc_s3_robust`); `docs/research/plan.md` (the H1 freeze condition and "
        "the H5 step lines say \"the H5 candidate\" and point at (s3)'s studies); the module docstrings of `repo_model.spread_mr_state_calendar`, "
        "`spread_mr_dispersion`, `spread_mr_regime` and `spread_mr_s3_v4`, which describe (s3) as the candidate; the rows of "
        "`docs/research/provisional-calendar-register.md` that call (s3) the candidate; and every dated study page and declaration since #1145, "
        "which are records of what ran and stay as they are. The registration draft that names the candidate is not in the tree on main.", "",
        "**Options** (the default applies if you have not answered by the next 5 pm batch):", "",
        "1. **A follow-up directive updates `h5-candidate.json` to (s3c) and the lines that name the candidate, after this merges** (default). "
        "Nothing is edited now; no claim changes until then.",
        "2. **Update only `h5-candidate.json` and the results page, and leave the prose pages to the registration.**",
        "3. **Wait for the registration draft and update everything together.**", "",
        "**Question 2. Where the facility line lives.** It is in the study declaration (`metadata/srf_cap_1241.json`, `metadata/s3c_candidate_1255.json`), "
        "read from `metadata/policy_events.json`. A registered candidate would read it from a registered source. Should it move to "
        "`metadata/sources.json`?", "",
        "**Options** (the default applies if you have not answered by the next 5 pm batch):", "",
        "1. **It stays in the declaration until registration** (default). `metadata/sources.json` is not edited.",
        "2. **Move it to `metadata/sources.json` now**, as a new availability declaration, in a directive of its own.", ""]


def page(args) -> int:
    r = json.loads(Path(args.score).read_text(encoding="utf-8"))
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    Path(args.output).write_text(render(r), encoding="utf-8")
    return 0


@turn_days.with_legacy_flag
def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="command", required=True)
    s = sub.add_parser("score", help="walk (s3), cap it where the facility is at full allotment, and score (s3c) on both windows")
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
