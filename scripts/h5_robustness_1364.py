"""A fixed robustness set on the candidate (s3c-ann-net): the length of its history and its refit cadence (#1364, H5, registration design).

A development study, never a verdict. It re-walks (s3c-ann-net), the H5 candidate, at the 18:00 decision instant under a set of choices fixed
in `metadata/h5_robustness_1364.json` before any arm was walked: the candidate as run (a trailing two-year training window, refit every 21
decision days), the same with all history ("expanding"), with a trailing one year and three years, and the as-run window refit every 5 and
every 63 decision days. Nothing else is varied and nothing is searched. Each arm is scored under scoring protocol v1 (grid CRPS averaged over
h = 1..5 primary, upper-tail twCRPS key secondary, the studentized stationary bootstrap) against the candidate as run and against B1, B1' and
B2, pooled and by regime and pressure-day type, development window deciding and the 2026 days apart. The page reports whether any choice
changes a reading; none of them replaces the candidate.

The directive calls the as-run history "expanding". The code does not: every fit takes its training pairs from
`spread_mean_reversion.training_rows`, a trailing window of `TRAIN_YEARS` = 2 years (the whole history before two years exist). The
declaration says so and reads the set both ways (`premise_correction`); the page puts the reading to Eleonora.

A window is set by `training_window(years)`, which sets `spread_mean_reversion.TRAIN_YEARS` for the walk of one arm (in a worker process of its
own) and restores it. No file under `src/` changes. Every arm is a walk of `spread_mr_state_calendar.walk` on direct pairs, so the calendar
columns are read at the target day and the one-step guard is not on the path.

The declaration is refused unless it is committed and unchanged. The only slow step is `walk`: it builds the frame of one window as
`scripts/candidate_calibration_1363.py` does (the frame's own walks, which are only the references), walks the six arms in parallel, and writes
one file per window; `score` scores the windows that exist. No day after 2026-09-03 and no locked day is read.

    PYTHONPATH=src python3 -m repo_model.cli build --raw-root tests/fixtures/snapshots/funding_inputs --output PUB.csv \\
        --build-cutoff 2026-09-08T21:31:42+00:00 --decision-time 18:00:00
    OUT=docs/research/h5-robustness-1364
    RMM_DECISION_TIME=18:00 PYTHONPATH=src python3 scripts/h5_robustness_1364.py walk --panel PUB.csv --window development --output WALK/development.json
    RMM_DECISION_TIME=18:00 PYTHONPATH=src python3 scripts/h5_robustness_1364.py walk --panel PUB.csv --window 2026 --output WALK/2026.json
    PYTHONPATH=src python3 scripts/h5_robustness_1364.py score --walks WALK --output $OUT/result.json
    PYTHONPATH=src python3 scripts/h5_robustness_1364.py page --score $OUT/result.json --output docs/research/h5-robustness-1364-result.md

Stdlib only.
"""

from __future__ import annotations

import argparse
import contextlib
import hashlib
import importlib.util
import json
import multiprocessing
import os
import sys
from datetime import date
from pathlib import Path
from typing import Dict, Iterator, List, Mapping, Optional, Sequence, Tuple

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))

from repo_model import scoring_protocol as sp, spread_mean_reversion as smr  # noqa: E402
from repo_model.exploration import EXPLORATORY_END, require_exploratory_window  # noqa: E402


# Lockbox classification (#1058): tests/test_lockbox.py reads these literals from this file's syntax tree.
LOCKBOX_CRPS = {
    "reproduction_check": (
        "delegates",
        "scores the cells of the walk files `walk_command` wrote; `walk_command` calls `require_exploratory_window` "
        "and `refuse_beyond` on every panel day, decision day and target day before it writes a file, and "
        "`score_command` reads those files back without a second check (#1364, #1568)",
    ),
}


def _load(name: str, alias: str):
    spec = importlib.util.spec_from_file_location(alias, REPO / "scripts" / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[alias] = module
    spec.loader.exec_module(module)
    return module


m1363 = _load("candidate_calibration_1363", "candidate_calibration_1363_in_1364")
s761 = _load("spread_mr_variants_761", "spread_mr_variants_761_in_1364")

DECLARATION = REPO / "metadata" / "h5_robustness_1364.json"
RECORD_1314 = m1363.RECORD_1314
SEED = 1364
MIN_GROUP_DAYS = 20
WINDOWS = m1363.WINDOWS
WINDOW_LAST = m1363.WINDOW_LAST
LEADS = tuple(sp.HORIZONS)
REFERENCE = "as_run"
REFERENCES = ("B1", "B1_prime", "B2")
METRICS = {"grid_crps": sp.grid_crps, "upper_tail_twcrps": sp.upper_tail_twcrps}
METRIC_TITLES = {"grid_crps": "grid CRPS, averaged over h = 1..5 (primary)", "upper_tail_twcrps": "upper-tail twCRPS (key secondary)"}
SPLITS = ("pooled", "lead", "regime", "pressure_day_type")
LABELS = {"as_run": "as run (2 years, every 21)", "expanding": "expanding (all history, every 21)", "rolling_1y": "rolling 1 year, every 21",
          "rolling_3y": "rolling 3 years, every 21", "refit_5": "2 years, refit every 5", "refit_63": "2 years, refit every 63",
          "B1": "B1", "B1_prime": "B1'", "B2": "B2"}
LETTER = {"gain": "G", "loss": "L", "undecided": "U", "identical": "=", "undefined": "?"}


# -- the declaration and the arms ----------------------------------------------------------------------------------------------


def committed_declaration(path: Path = DECLARATION) -> dict:
    """The declaration, refused unless it is committed and unchanged since `HEAD`."""

    return m1363.committed_declaration(path)


def arm_plan(declared: Mapping[str, object]) -> List[Tuple[str, int, int]]:
    """`(name, training years, refit every)` for each declared arm, the reference first.

    The reference must be the candidate as run: the module's own `TRAIN_YEARS` and `REFIT_EVERY`.

    Raises:
        ValueError: the reference is missing, or is not the as-run window and cadence; an arm lacks a window or a cadence.
    """

    arms = declared["arms"]
    if REFERENCE not in arms:
        raise ValueError(f"the declaration has no reference arm {REFERENCE!r}")
    plan: List[Tuple[str, int, int]] = []
    for name, arm in arms.items():
        years = int(arm.get("train_years", smr.TRAIN_YEARS)) if name != REFERENCE else smr.TRAIN_YEARS
        every = int(arm["refit_every"])
        if every < 1 or years < 1:
            raise ValueError(f"arm {name}: a window and a cadence of at least 1 are required")
        plan.append((name, years, every))
    reference = next(p for p in plan if p[0] == REFERENCE)
    if reference[2] != smr.REFIT_EVERY:
        raise ValueError(f"the reference refits every {reference[2]} days; the candidate as run refits every {smr.REFIT_EVERY}")
    plan.sort(key=lambda p: p[0] != REFERENCE)
    return plan


@contextlib.contextmanager
def training_window(years: int) -> Iterator[None]:
    """Set the trailing training window of every mean-reversion fit to `years` for the block, and restore it (also on an error)."""

    if years < 1:
        raise ValueError(f"the training window must be at least 1 year, got {years}")
    before = smr.TRAIN_YEARS
    smr.TRAIN_YEARS = years
    try:
        yield
    finally:
        smr.TRAIN_YEARS = before


# -- the walk ------------------------------------------------------------------------------------------------------------------

_STATE: Dict[str, object] = {}


def _walk_task(job):
    name, years, every = job
    from repo_model import s3c_announced

    s = _STATE
    with training_window(years):
        walk = s["sc"].walk(s["panel"], s["days"], s["both"], s["states"], (s3c_announced.ANN_ARM, s3c_announced.ANN_NET_ARM),
                            sizes=s["net_table"], refit_every=every, **s["settings"])
    found = {d: walk.forecasts[s3c_announced.ANN_NET_ARM.name][d] for d in s["frame_days"]}
    return name, found, len(walk.fits)


def walk_command(args) -> int:
    os.environ["RMM_DECISION_TIME"] = "18:00"
    declared = committed_declaration()
    plan = arm_plan(declared)
    from repo_model import announced_iorb, decision_instant, policy_events, s3c_announced, spread_mr_calendar as cal
    from repo_model.baseline import panel_sha256
    from repo_model.evaluation_splits import load_split_declaration

    m = _load("s3c_announced_settlement_1288", "s3c_announced_settlement_1288_in_1364")
    if decision_instant.DECISION_TIME.isoformat(timespec="minutes") != "18:00" or m.k.DECISION_TIME.isoformat(timespec="minutes") != "18:00":
        raise ValueError("this study is made at the 18:00 decision instant")
    window = args.window
    panel_path = Path(args.panel)
    sha = panel_sha256(panel_path)
    panel = [row for row in m.load_daily_panel(panel_path) if row.date <= m.LAST_DAY]
    require_exploratory_window([row.date for row in panel], where="scripts/h5_robustness_1364")
    splits = load_split_declaration(m.c.SPLITS)
    registry = json.loads(m.c.SOURCES.read_text(encoding="utf-8"))
    register = policy_events.load_register()
    table = cal.TermTable(panel, announced_iorb.load_announcements(m.c.IORB_TABLE), decision_time=m.c.DECISION_TIME)
    auctions = m.m1273.load_auctions()
    results = m.load_results()
    frame, _notes, _mine, _cell_table, _groups = m.m1255.build(window, panel, splits, registry, table, register, args.first)
    days = m.candidate_days(frame, window, args.first)
    iorb = announced_iorb.load_announcements(m.c.IORB_TABLE)
    _STATE.update(
        sc=m.sc, panel=panel, days=days, frame_days=list(frame.days),
        both=s3c_announced.AnnouncedTermTable(panel, iorb, results, decision_time=m.k.DECISION_TIME),
        net_table=s3c_announced.AnnouncedNetSizeTable(panel, auctions, decision_time=m.k.DECISION_TIME),
        states=m.s3c_net.constant_states(panel), settings=dict(registry=registry, decision_time=m.k.DECISION_TIME, splits=splits))
    with multiprocessing.get_context("fork").Pool(min(args.workers, len(plan))) as pool:
        walked = pool.map(_walk_task, plan, chunksize=1)
    models = {"B1": frame.forecasts["B1"], "B1_prime": frame.forecasts[m.B1P], "B2": frame.forecasts["B2"]}
    refits = {}
    for name, found, count in walked:
        models[name] = m.m1255.s3c_forecasts(frame, register, found)
        refits[name] = count
    cells, outcome, targets, regime_of_day = [], {}, {}, {}
    for d in frame.days:
        regime_of_day[d.isoformat()] = frame.regime(d)
        for h in LEADS:
            t = frame.target(d, h)
            cells.append([d.isoformat(), h, t.isoformat()])
            outcome[t.isoformat()] = frame.outcome[t]
            if t.isoformat() not in targets:
                targets[t.isoformat()] = {"regime": frame.regime(t), "types": [], "pressure": frame.day_type(t)}
    m1363.refuse_beyond([date.fromisoformat(c[2]) for c in cells] + list(frame.days), WINDOW_LAST[window], where="h5_robustness_1364")
    doc = {
        "window": window, "instant": "18:00", "panel_sha256": sha, "declaration": declared["issue"],
        "calendar": [row.date.isoformat() for row in panel], "cells": cells, "outcome": outcome, "targets": targets,
        "regime_of_day": regime_of_day, "refits": refits, "arms": {n: {"train_years": y, "refit_every": e} for n, y, e in plan},
        "models": {name: [list(fc[date.fromisoformat(d)][h]) for d, h, _t in cells] for name, fc in models.items()},
    }
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    Path(args.output).write_text(json.dumps(doc, separators=(",", ":")) + "\n", encoding="utf-8")
    print(f"wrote {args.output}: {window}, {len(frame.days)} decision days, {len(cells)} cells, refits {refits}")
    return 0


# -- scoring -------------------------------------------------------------------------------------------------------------------


def reading(row: Optional[Mapping[str, object]]) -> str:
    """'gain' when the 90% studentized interval of mean d lies wholly above zero, 'loss' when wholly below, 'undecided' otherwise;
    'identical' for two series that are the same on every day and 'undefined' for a pair the protocol cannot test. Positive d favours the arm."""

    if row is None:
        return "undefined"
    if row.get("identical"):
        return "identical"
    interval = row.get("difference_interval")
    if "undefined" in row or not interval:
        return "undefined"
    lo, hi = interval
    return "gain" if lo > 0 else "loss" if hi < 0 else "undecided"


def changed(reference: str, arm: str) -> bool:
    """A reading changes when its category differs. A pair that cannot be read ('undefined') is not a change."""

    if "undefined" in (reference, arm):
        return False
    return reference != arm


def cell_scores(window, model: str) -> Dict[str, List[float]]:
    return {metric: [fn(q, y) for q, y in zip(window.q[model], window.y)] for metric, fn in METRICS.items()}


def series_for(window, scores: Sequence[float], grain: str) -> Dict[date, float]:
    """A metric's cell scores as a series: by decision day ('decision'), by target day ('target') or one lead's cells ('leadN')."""

    sums: Dict[date, List[float]] = {}
    for (d, h, t), value in zip(window.cells, scores):
        if grain == "decision":
            key = d
        elif grain == "target":
            key = t
        elif h == int(grain[4:]):
            key = d
        else:
            continue
        sums.setdefault(key, []).append(value)
    return {key: sum(v) / len(v) for key, v in sums.items()}


def groups_of(window) -> List[Tuple[str, str, str, List[date]]]:
    """`(split, label, grain, days)`: pooled and each lead on the decision-day series; regime and pressure-day type on the target-day series."""

    out: List[Tuple[str, str, str, List[date]]] = []
    for split, label, idx in window.groups():
        if split not in SPLITS:
            continue
        if split == "pooled":
            out.append((split, "all decision days", "decision", sorted({window.cells[i][0] for i in idx})))
        elif split == "lead":
            out.append((split, label, f"lead{label[2:]}", sorted({window.cells[i][0] for i in idx})))
        else:
            out.append((split, label, "target", sorted({window.cells[i][2] for i in idx})))
    return out


def _identical(a: Mapping[date, float], b: Mapping[date, float], days: Sequence[date]) -> bool:
    return all(a[d] == b[d] for d in days)


def _pairs_task(job):
    split, label, grain, metric, arm, days = job
    series = _STATE["series"][(grain, metric)]
    out: Dict[str, dict] = {}
    comparators = ([REFERENCE] if arm != REFERENCE else []) + list(REFERENCES)
    for name in comparators:
        if _identical(series[name], series[arm], days):
            out[name] = {"identical": True, "days": len(days)}
            continue
        out[name] = s761.run_pairs({name: series[name]}, series[arm], list(days), seed=SEED, draws=_STATE["draws"], mean_d_fallback=True)[name]
    return (split, label, metric, arm), out


def reproduction_check(window, record: Mapping[str, object]) -> dict:
    """The as-run arm's and the references' mean grid CRPS over all cells against the 1314 record of the same window, to 1e-9; raises `ValueError`
    otherwise. Without it the arms would be compared with something that is not the candidate."""

    group = record["windows"][window.name]["groups"]["pooled"]["all decision days"]["grid_crps"]["means"]
    out = {}
    for model, key in ((REFERENCE, "sc_s3c_ann_net"), ("B1", "B1"), ("B1_prime", "B1_prime"), ("B2", "B2")):
        mine = sum(sp.grid_crps(q, y) for q, y in zip(window.q[model], window.y)) / len(window.cells)
        theirs = group[key]
        theirs = theirs["mean"] if isinstance(theirs, dict) else theirs
        if abs(mine - theirs) > 1e-9:
            raise ValueError(f"{window.name}: mean grid CRPS of {model} is {mine!r} here and {theirs!r} in the 1314 record")
        out[model] = {"mean_grid_crps": mine, "record": theirs}
    return out


def flags(window_result: Mapping[str, object]) -> dict:
    """Every cell (split, group, metric, arm, comparator) of a window whose reading differs from the reference's, or in which the arm's own
    paired difference against the reference is a gain or a loss; and the number of cells examined."""

    listed, examined, same = [], 0, 0
    for split, labels in window_result["groups"].items():
        for label, entry in labels.items():
            if "tested" not in entry:
                continue
            for metric in METRICS:
                vs = entry[metric]["vs"]
                for arm in vs:
                    if arm == REFERENCE:
                        continue
                    own = reading(vs[arm].get(REFERENCE))
                    for b in REFERENCES:
                        examined += 1
                        ref, mine = reading(vs[REFERENCE].get(b)), reading(vs[arm].get(b))
                        if changed(ref, mine):
                            listed.append({"split": split, "group": label, "metric": metric, "arm": arm, "against": b,
                                           "reference_reading": ref, "arm_reading": mine, "days": entry["days"]})
                        else:
                            same += 1
                    examined += 1
                    if own in ("gain", "loss"):
                        listed.append({"split": split, "group": label, "metric": metric, "arm": arm, "against": REFERENCE,
                                       "reference_reading": "-", "arm_reading": own, "days": entry["days"]})
                    else:
                        same += 1
    return {"examined": examined, "unchanged": same, "changed": listed}


def run_window(window, plan: Sequence[Tuple[str, int, int]], args) -> dict:
    names = [name for name, _y, _e in plan]
    cells = {m: cell_scores(window, m) for m in names + list(REFERENCES)}
    groups = groups_of(window)
    series: Dict[Tuple[str, str], Dict[str, Dict[date, float]]] = {}
    for _s, _l, grain, _d in groups:
        for metric in METRICS:
            if (grain, metric) not in series:
                series[(grain, metric)] = {m: series_for(window, cells[m][metric], grain) for m in cells}
    _STATE.update(series=series, draws=args.draws)
    jobs, skipped = [], {}
    for split, label, grain, days in groups:
        if len(days) < MIN_GROUP_DAYS:
            skipped[f"{split}/{label}"] = len(days)
            continue
        for metric in METRICS:
            for arm in names:
                jobs.append((split, label, grain, metric, arm, tuple(days)))
    with multiprocessing.get_context("fork").Pool(args.workers) as pool:
        done = pool.map(_pairs_task, jobs, chunksize=1)
    result: dict = {"groups": {}, "skipped_groups": skipped}
    for split, label, grain, days in groups:
        entry = result["groups"].setdefault(split, {}).setdefault(label, {"days": len(days)})
        if len(days) >= MIN_GROUP_DAYS:
            entry["tested"] = True
        for metric in METRICS:
            ser = series[(grain, metric)]
            entry[metric] = {"means": {m: sum(ser[m][d] for d in days) / len(days) for m in cells}, "vs": {}}
    for (split, label, metric, arm), payload in done:
        result["groups"][split][label][metric]["vs"][arm] = payload
    result["flags"] = flags(result)
    return result


def score_command(args) -> int:
    declared = committed_declaration()
    plan = arm_plan(declared)
    record = json.loads(RECORD_1314.read_text(encoding="utf-8"))
    result: dict = {"issue": 1364, "declaration": "metadata/h5_robustness_1364.json", "label": "development, not a verdict",
                    "seed": SEED, "draws": args.draws, "arms": declared["arms"], "reading_rule": declared["reading"]["rule"],
                    "windows": {}, "reproduction": {}, "walk_files": {}, "b4": declared["b4"], "amendments": declared["amendments"]}
    for name in WINDOWS:
        path = Path(args.walks) / f"{name}.json"
        if not path.exists():
            continue
        raw = path.read_bytes()
        doc = json.loads(raw)
        if result.get("panel_sha256") not in (None, doc["panel_sha256"]):
            raise ValueError("the walk files were made from different panels")
        if set(doc["arms"]) != {n for n, _y, _e in plan} or any(doc["arms"][n] != {"train_years": y, "refit_every": e} for n, y, e in plan):
            raise ValueError(f"{path}: the walk's arms are not the declared arms")
        result["panel_sha256"] = doc["panel_sha256"]
        result["walk_files"][name] = {"sha256": hashlib.sha256(raw).hexdigest(), "refits": doc.get("refits")}
        window = m1363.Window(doc)
        result["reproduction"][name] = reproduction_check(window, record)
        result["windows"][name] = run_window(window, plan, args)
    if not result["windows"]:
        raise SystemExit(f"no walk file in {args.walks}")
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    Path(args.output).write_text(json.dumps(result, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    return 0


# -- the page ------------------------------------------------------------------------------------------------------------------


def _pct(x: Optional[float]) -> str:
    return "n/a" if x is None else f"{100 * x:+.1f}%"


def _vs_cell(row: Optional[Mapping[str, object]]) -> str:
    """Relative skill of the arm against the comparator with its 90% interval and the reading, or the reading alone."""

    word = reading(row)
    if word in ("identical", "undefined") or row is None:
        return word
    iv = row.get("skill_interval")
    if row.get("skill") is None or not iv:
        return f"{word} (mean d {row['difference']:+.4f})"
    return f"{_pct(row['skill'])} [{_pct(iv[0])}, {_pct(iv[1])}] {word}"


def _matrix(window: Mapping[str, object], metric: str, arms: Sequence[str]) -> List[str]:
    """Rows: the groups. Columns: the arms. Each cell: the reading against B1 / B1' / B2 as three letters (G gain, L loss, U undecided)."""

    head = "| group | days | " + " | ".join(LABELS[a] for a in arms) + " |"
    lines = [head, "|---|---:|" + "---|" * len(arms)]
    for split in SPLITS:
        for label, entry in window["groups"].get(split, {}).items():
            if "tested" not in entry:
                lines.append(f"| {split}: {label} | {entry['days']} | " + " | ".join("not tested" for _ in arms) + " |")
                continue
            vs = entry[metric]["vs"]
            cells = ["/".join(LETTER[reading(vs[a].get(b))] for b in REFERENCES) for a in arms]
            lines.append(f"| {split}: {label} | {entry['days']} | " + " | ".join(cells) + " |")
    return lines


def _own_table(window: Mapping[str, object], metric: str, arms: Sequence[str], split_labels: Sequence[Tuple[str, str]]) -> List[str]:
    lines = ["| group | days | " + " | ".join(LABELS[a] for a in arms) + " |", "|---|---:|" + "---|" * len(arms)]
    for split, label in split_labels:
        entry = window["groups"].get(split, {}).get(label)
        if entry is None:
            continue
        if "tested" not in entry:
            lines.append(f"| {split}: {label} | {entry['days']} | " + " | ".join("not tested" for _ in arms) + " |")
            continue
        vs = entry[metric]["vs"]
        lines.append(f"| {split}: {label} | {entry['days']} | " + " | ".join(_vs_cell(vs[a].get(REFERENCE)) for a in arms) + " |")
    return lines


def _means_table(window: Mapping[str, object], metric: str, names: Sequence[str]) -> List[str]:
    entry = window["groups"]["pooled"]["all decision days"][metric]["means"]
    return ["| " + " | ".join(LABELS[n] for n in names) + " |", "|" + "---:|" * len(names), "| " + " | ".join(f"{entry[n]:.4f}" for n in names) + " |"]


def _flag_lines(window: Mapping[str, object]) -> List[str]:
    f = window["flags"]
    lines = [f"{f['examined']} cells examined (group, metric, arm and comparator); {len(f['changed'])} change a reading or show an arm against the "
             f"reference; {f['unchanged']} do not. At 90% intervals some flags are expected by chance."]
    if f["changed"]:
        lines += ["", "| arm | group | metric | against | reference reads | arm reads | days |", "|---|---|---|---|---|---|---:|"]
        for x in f["changed"]:
            lines.append(f"| {LABELS[x['arm']]} | {x['split']}: {x['group']} | {x['metric'].replace('_', ' ')} | {LABELS.get(x['against'], x['against'])} | "
                         f"{x['reference_reading']} | {x['arm_reading']} | {x['days']} |")
    return lines


def answer(r: dict) -> List[str]:
    """The answer to the question asked, from the development window (the 2026 days are mentioned apart): per arm, the pooled reading against the
    candidate as run and the number of cells in which its reading against B1, B1' or B2 differs from the candidate's."""

    out: List[str] = []
    for window, name in (("development", "development window (decides)"), ("2026", "2026 days (decide nothing)")):
        w = r["windows"].get(window)
        if w is None:
            continue
        pooled = w["groups"]["pooled"]["all decision days"]
        rows = ["| arm | pooled grid CRPS against the candidate as run | pooled twCRPS against the candidate as run | cells where the reading against B1, B1' or B2 differs | of which pooled |",
                "|---|---|---|---:|---:|"]
        for arm in [a for a in r["arms"] if a != REFERENCE]:
            bench = [x for x in w["flags"]["changed"] if x["arm"] == arm and x["against"] in REFERENCES]
            rows.append(f"| {LABELS[arm]} | {_vs_cell(pooled['grid_crps']['vs'][arm].get(REFERENCE))} | "
                        f"{_vs_cell(pooled['upper_tail_twcrps']['vs'][arm].get(REFERENCE))} | {len(bench)} | {sum(1 for x in bench if x['split'] == 'pooled')} |")
        same = all(reading(pooled[m]["vs"][a].get(b)) == reading(pooled[m]["vs"][REFERENCE].get(b))
                   for m in METRICS for a in r["arms"] for b in REFERENCES)
        out += [f"**{name}.** " + ("The pooled reading of every arm against B1, B1' and B2, on both metrics, is the candidate's own reading."
                                   if same else "A pooled reading against B1, B1' or B2 differs from the candidate's in the cells listed below."), ""] + rows + [""]
    return out


def render(r: dict) -> str:
    arms = [a for a in r["arms"] if a != REFERENCE]
    allarms = [REFERENCE] + arms
    out = ["# A fixed robustness set on (s3c-ann-net): the length of its history and its refit cadence (#1364)", "",
           "**Development evidence, not a verdict.** H5 (primary goal), registration design, step 3. The declaration "
           "(`metadata/h5_robustness_1364.json`) was committed before any arm was walked. Nothing here is registered, nothing is chosen, and no "
           "arm replaces the candidate. The development window decides what is read; the 2026 days are shown apart and decide nothing. "
           "B4 (#1360) is not on main and is not compared.", ""]
    out += ["## What was measured", "",
            "The candidate (s3c-ann-net) is walked again at the 18:00 decision instant under six settings, all fixed in advance:", "",
            "| arm | training history | refit every |", "|---|---|---:|"]
    for name, arm in r["arms"].items():
        out.append(f"| {LABELS[name]} | {arm['history']} | {arm['refit_every']} decision days |")
    out += ["", "**The premise of the directive is not what the code does.** The directive calls the candidate's history 'expanding, as now'. "
            "Every fit of the candidate takes its training pairs from a trailing window of two years "
            "(`spread_mean_reversion.TRAIN_YEARS`); only in the first two years of the panel is that the whole history. So the candidate as run "
            "is the rolling two-year setting, which is the reference here, and the two contrasts are read both ways: all history (expanding) "
            "and one and three years (the two rolling lengths). **Question 1 for Eleonora, below.**", "",
            "Each arm is compared with the candidate as run, and every arm (the candidate included) with B1, B1' and B2, on grid CRPS averaged over "
            "h = 1..5 and on upper-tail twCRPS, by scoring protocol v1's studentized stationary bootstrap (seed 1364). Positive favours the arm. "
            f"{r['reading_rule']}.", ""]
    out += ["## Answer", "", "Does any choice of history or cadence change a reading of the candidate? The pooled lines first; the groups follow in the "
            "tables below, and the cells that change a reading are listed under each window. The skill and interval printed are those of relative skill; "
            "the reading itself uses the 90% interval of mean d (a group can read 'undecided' on mean d while the skill interval excludes zero).", ""]
    out += answer(r)
    for window, title in (("development", "Development window (targets to 2025-12-31): decides"),
                          ("2026", "2026 days (targets 2026-01-02 to 2026-09-03): shown apart, decides nothing")):
        if window not in r["windows"]:
            continue
        w = r["windows"][window]
        out += [f"## {title}", ""]
        out += ["Reproduction: the mean grid CRPS of the as-run arm and of B1, B1' and B2 equals the 18:00 record of #1314 to 1e-9.", ""]
        for metric in METRICS:
            out += [f"### {METRIC_TITLES[metric]}", "", "Mean over all days, pooled:", ""]
            out += _means_table(w, metric, allarms + list(REFERENCES)) + [""]
            out += ["Each arm against the candidate as run (relative skill, 90% interval, reading), pooled, by lead, by regime and by pressure-day type:", ""]
            labels = [(s, l) for s in SPLITS for l in w["groups"].get(s, {})]
            out += _own_table(w, metric, arms, labels) + [""]
            out += ["Readings against B1 / B1' / B2 (G gain, L loss, U undecided; the interval rule above), the candidate as run beside each arm:", ""]
            out += _matrix(w, metric, allarms) + [""]
        out += ["### Cells that change a reading", ""] + _flag_lines(w) + [""]
        if w["skipped_groups"]:
            out += ["Groups of fewer than 20 days were not tested: " + ", ".join(f"{k} ({v})" for k, v in w["skipped_groups"].items()) + ".", ""]
    out += ["## Questions for Eleonora", "",
            "1. **Which reading of 'expanding' did you mean?** (a) The set as run here: the as-run two-year window is the reference, "
            "with all history, one year and three years as the alternatives (default). (b) Only all-history against two rolling lengths, "
            "leaving the two-year window out of the table. (c) Change the candidate's window itself; that is a different directive and is not "
            "done here.", "",
            "## What this does not show", "",
            "Development data on seen days; the intervals of the regime and day-type groups use the current method (#1221). The window and the "
            "cadence are varied one at a time. No combination, no other term, input, cap or scale window. Five alternatives over many groups "
            "mean some flags are chance flags. Nothing is adopted.", ""]
    return "\n".join(out)


def page_command(args) -> int:
    r = json.loads(Path(args.score).read_text(encoding="utf-8"))
    for name, arm in r["arms"].items():
        arm.setdefault("history", name)
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    Path(args.output).write_text(render(r), encoding="utf-8")
    return 0


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="command", required=True)
    w = sub.add_parser("walk", help="walk the declared arms of (s3c-ann-net) with B1, B1' and B2 over one window")
    w.add_argument("--panel", required=True)
    w.add_argument("--window", choices=WINDOWS, required=True)
    w.add_argument("--output", required=True)
    w.add_argument("--workers", type=int, default=4)
    w.add_argument("--first", type=date.fromisoformat, default=None, help="start the walk on this day (the script's test only)")
    w.set_defaults(func=walk_command)
    s = sub.add_parser("score", help="paired tests and readings from the walk files")
    s.add_argument("--walks", required=True)
    s.add_argument("--output", required=True)
    s.add_argument("--workers", type=int, default=4)
    s.add_argument("--draws", type=int, default=sp.DRAWS)
    s.set_defaults(func=score_command)
    g = sub.add_parser("page", help="write the result page from a score file")
    g.add_argument("--score", required=True)
    g.add_argument("--output", required=True)
    g.set_defaults(func=page_command)
    args = parser.parse_args(argv)
    return int(args.func(args) or 0)


if __name__ == "__main__":
    raise SystemExit(main())
