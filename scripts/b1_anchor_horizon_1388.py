"""B1* and B1'*: the persistence benchmarks with the horizon counted from the last public anchor, scored against (s3c-ann-net) (#1388; H5, registration
design; her ruling of 2 November 2026 after the second outside review).

A development study, never a verdict. B1 adds the trailing two years' h-row changes to the last public spread, but the last public row (the anchor) is older
than the decision day, so the elapsed horizon from the anchor to the target is h plus the anchor's lag. B1* and B1'* count that span
(`repo_model.protocol_benchmarks.b1_anchor_forecast`, `repo_model.b1_calendar.b1_calendar_anchor_forecast`). This script scores B1, B1*, B1' and B1'* against
the H5 candidate (s3c-ann-net) at the 18:00 decision instant, on the development window (targets to 2025-12-31) and the 2026 development days (to
2026-09-03), under scoring protocol v1: grid CRPS averaged over h = 1..5, upper-tail twCRPS and the Brier score of P(> +5 bp), pooled and by lead, regime and
day type, with the absolute losses and the bound on mean d beside the skill ratios. Nothing is adopted; the page ends with a marked question.

Every choice is in `metadata/b1_anchor_horizon_1388.json`, which `score` refuses to read unless it is committed and unchanged. The candidate's walk is
`scripts/s3c_announced_settlement_1288.py`'s `build`, unchanged, run at the 18:00 instant. No day after 2026-09-03 and no locked day is read.

Commands, from a clone of the branch (the walks are minutes and the paired tests the longer part):

    PYTHONPATH=src python3 -m repo_model.cli build --raw-root tests/fixtures/snapshots/funding_inputs \\
        --output PUB.csv --build-cutoff 2026-09-08T21:31:42+00:00 --decision-time 18:00:00
    PYTHONPATH=src python3 -m repo_model.cli verify-panel PUB.csv --manifest metadata/funding_panel_manifest.json
    OUT=docs/research/b1-anchor-horizon-1388
    RMM_DECISION_TIME=18:00 PYTHONPATH=src python3 scripts/b1_anchor_horizon_1388.py score --panel PUB.csv --output $OUT/result.json
    PYTHONPATH=src python3 scripts/b1_anchor_horizon_1388.py page --score $OUT/result.json --output docs/research/b1-anchor-horizon-1388-result.md

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


from repo_model import announced_iorb, metrics, policy_events  # noqa: E402
from repo_model import b1_calendar as b1c  # noqa: E402
from repo_model import protocol_benchmarks as pb  # noqa: E402
from repo_model import scoring_protocol as sp, spread_mr_calendar as cal  # noqa: E402
from repo_model.baseline import panel_sha256  # noqa: E402
from repo_model.evaluation_splits import load_split_declaration  # noqa: E402
from repo_model.exploration import EXPLORATORY_END, require_exploratory_window  # noqa: E402

#: #1288's script (and through it #1273's, #1255's, #1241's and #1229's), loaded under an alias of its own so that the pickling of the worker pool's tasks
#: does not meet another module's copy.
m1288 = _load("s3c_announced_settlement_1288", "s3c_announced_settlement_1288_in_1388")
m1273, k, c, s686, s761 = m1288.m1273, m1288.k, m1288.c, m1288.s686, m1288.s761

DECLARATION = REPO / "metadata" / "b1_anchor_horizon_1388.json"
RECORD_1314 = REPO / "docs" / "research" / "s3c-ann-net-1800-1314" / "announced-settlement-1800.json"
SEED = 1388
REPS = 2000
LAST_DAY = EXPLORATORY_END
WINDOW_LAST = m1288.WINDOW_LAST
WINDOWS = m1288.WINDOWS
WINDOW_TITLES = m1288.WINDOW_TITLES
CANDIDATE = m1288.ANNNET
B1, B1P, B1S, B1PS = "B1", m1288.B1P, "B1_star", "B1_prime_star"
REFERENCES = (B1, B1S, B1P, B1PS)
MODELS = (CANDIDATE,) + REFERENCES
LABELS = {CANDIDATE: "(s3c-ann-net)", B1: "B1", B1S: "B1*", B1P: "B1'", B1PS: "B1'*"}
#: (arm, reference): the arm is the one skill above zero favours.
PAIRS = tuple((CANDIDATE, ref) for ref in REFERENCES) + ((B1S, B1), (B1PS, B1P))
TESTED = m1288.TESTED
METRIC_NAMES = m1288.METRIC_NAMES
METRIC_TITLES = m1288.METRIC_TITLES
SPLITS = ("pooled", "lead", "regime", "pressure_day_type", "target_day_type")
MIN_GROUP_DAYS = m1288.MIN_GROUP_DAYS
DECISION_TIME = k.DECISION_TIME
INSTANT = time(18, 0)

_STATE: Dict = {}


def committed_declaration(path: Path = DECLARATION) -> dict:
    """The declaration, refused unless it is committed and unchanged since `HEAD`."""

    return s686.committed_declaration(path)


def require_instant(instant: time = DECISION_TIME) -> None:
    """Refuse a run that is not at the 18:00 decision instant: the study family took 16:00 from a hard-coded value until #1314.

    Raises:
        SystemExit: the family's decision instant is not 18:00.
    """

    if instant != INSTANT:
        raise SystemExit(f"this study is made at {INSTANT:%H:%M}; the family's instant is {instant:%H:%M} (set RMM_DECISION_TIME=18:00)")


def forecasts_of(panel, frame, splits, registry) -> Tuple[Dict[date, dict], Dict[date, dict], Counter]:
    """B1* and B1'* on every scored decision day of `frame`, and the lag (in panel rows) of each decision day.

    Raises:
        ProtocolError: a scored decision day has no forecast.
    """

    settings = dict(registry=registry, decision_time=DECISION_TIME)
    star, prime_star, lags = {}, {}, Counter()
    for day in frame.days:
        index = frame.position[day]
        lags[pb.anchor_lag(panel, index, **settings)] += 1
        star[day] = pb.b1_anchor_forecast(panel, index, **settings)
        prime_star[day] = b1c.b1_calendar_anchor_forecast(panel, index, splits=splits, **settings)
    return star, prime_star, lags


def _identical(series, arm: str, reference: str, members: Sequence[date]) -> bool:
    return all(series[arm][d] == series[reference][d] for d in members)


def unstudentized(series, arm: str, reference: str, members: Sequence[date]) -> dict:
    """Mean d and its 90% stationary-bootstrap percentile interval, for a group whose studentized bound cannot be computed. Not the protocol's
    interval; no reading is taken from it. `d = S(reference) - S(arm)`, positive favours the arm."""

    d = [series[reference][x] - series[arm][x] for x in sorted(members)]
    low, high = metrics.stationary_bootstrap_interval(
        lambda idx: sum(d[i] for i in idx) / len(idx), len(d), block_length=m1273.BLOCK, seed=SEED, replications=REPS)
    return {"mean_d": sum(d) / len(d), "interval": [low, high], "days": len(d)}


def _pairs_task(job):
    split, label, grain, metric, arm, reference, members = job
    series = _STATE["series"][(grain, metric)]
    days = list(members)
    if _identical(series, arm, reference, days):
        return (split, label, metric, arm, reference), {"identical": True, "days": len(days)}
    out = s761.run_pairs({reference: series[reference]}, series[arm], days, seed=SEED, draws=_STATE["draws"], mean_d_fallback=True)[reference]
    if "undefined" in out:
        out["unstudentized"] = unstudentized(series, arm, reference, days)
    return (split, label, metric, arm, reference), out


def run_jobs(jobs, workers: int):
    with multiprocessing.get_context("fork").Pool(workers) as pool:
        return pool.map(_pairs_task, jobs, chunksize=1)


def run_window(window: str, panel, splits, registry, table, register, results, auctions, args) -> dict:
    frame, notes, _walks, _tables, _cells, groups_fn = m1288.build(window, panel, splits, registry, table, register, results, auctions, args.first)
    last = WINDOW_LAST[window]
    star, prime_star, lags = forecasts_of(panel, frame, splits, registry)
    forecasts = {m: frame.forecasts[m] for m in (CANDIDATE, B1, B1P)}
    forecasts[B1S], forecasts[B1PS] = star, prime_star
    frame.forecasts = {m: {d: forecasts[m][d] for d in frame.days} for m in MODELS}
    labels = c.day_labels(frame, table)
    pressure = k.pressure_labels(frame, sorted(labels))
    cells = {m: m1288.cell_table(frame, frame.forecasts[m], last) for m in MODELS}
    for m in MODELS:
        official = sp.day_scores(frame.forecasts[m], frame.outcome, frame.dates, score=sp.grid_crps)
        mean = s686.by_decision(cells[m]["grid_crps"])
        if set(official) != set(mean) or any(abs(official[d] - mean[d]) > 1e-9 for d in mean):
            raise SystemExit(f"grid CRPS of {m}: the cell means differ from scoring_protocol.day_scores")
    groups = [g for g in groups_fn(frame, labels, pressure) if g[0] in SPLITS]
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
            for arm, reference in PAIRS:
                jobs.append((split, label, grain, metric, arm, reference, tuple(members)))
    done = run_jobs(jobs, args.workers)

    differ = {m: sum(1 for d in frame.days for h in sp.HORIZONS if frame.forecasts[m][d][h] != frame.forecasts[b][d][h])
              for m, b in ((B1S, B1), (B1PS, B1P))}
    result: dict = {
        "notes": notes, "groups": {}, "skipped_groups": skipped, "decision_days": len(frame.days), "cells": len(frame.days) * len(sp.HORIZONS),
        "lag_rows": {str(lag): n for lag, n in sorted(lags.items())},
        "cells_differing_from_original": differ,
    }
    for split, label, grain, members in groups:
        entry = result["groups"].setdefault(split, {}).setdefault(label, {"days": len(members)})
        for metric in METRIC_NAMES:
            ser = series[(grain, metric)]
            entry[metric] = {"means": {m: sum(ser[m][d] for d in members) / len(members) for m in MODELS}, "vs": {}}
    for (split, label, metric, arm, reference), payload in done:
        result["groups"][split][label][metric]["vs"].setdefault(arm, {})[reference] = payload
    return result


def against_record(windows: Mapping[str, dict]) -> dict:
    """The pooled means of the candidate, B1 and B1' here against #1314's record (the same walks at 18:00): they must agree."""

    if not RECORD_1314.exists():
        return {}
    there = json.loads(RECORD_1314.read_text(encoding="utf-8"))["windows"]
    out: Dict[str, dict] = {}
    for window, result in windows.items():
        a = there[window]["groups"]["pooled"]["all decision days"]
        b = result["groups"]["pooled"]["all decision days"]
        out[window] = {"record": str(RECORD_1314.relative_to(REPO)), "metrics": {
            metric: {m: {"here": b[metric]["means"][m], "there": a[metric]["means"][m], "difference": b[metric]["means"][m] - a[metric]["means"][m]}
                     for m in (CANDIDATE, B1, B1P)} for metric in ("grid_crps", "upper_tail_twcrps")}}
    return out


def score(args) -> int:
    require_instant()
    declaration = committed_declaration()
    panel_path = Path(args.panel)
    published_sha = panel_sha256(panel_path)
    panel = [row for row in m1273.load_daily_panel(panel_path) if row.date <= LAST_DAY]
    require_exploratory_window([row.date for row in panel], where="scripts/b1_anchor_horizon_1388")
    splits = load_split_declaration(c.SPLITS)
    registry = json.loads(c.SOURCES.read_text(encoding="utf-8"))
    register = policy_events.load_register()
    table = cal.TermTable(panel, announced_iorb.load_announcements(c.IORB_TABLE), decision_time=c.DECISION_TIME)
    auctions = m1273.load_auctions()
    results = m1288.load_results()
    result: dict = {
        "issue": 1388, "declaration": str(DECLARATION.relative_to(REPO)), "panel_sha256": published_sha, "decision_time": f"{DECISION_TIME:%H:%M}",
        "subset_from": None if args.first is None else args.first.isoformat(), "label": "development, not a verdict", "seed": SEED, "draws": args.draws,
        "models": list(MODELS), "pairs": [list(p) for p in PAIRS], "windows": {}, "reading_rules": declaration["reading_rules"],
    }
    for window in WINDOWS:
        result["windows"][window] = run_window(window, panel, splits, registry, table, register, results, auctions, args)
    result["against_record_1314"] = against_record(result["windows"]) if args.first is None else {}
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    Path(args.output).write_text(json.dumps(result, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    return 0


# -- the page ------------------------------------------------------------------------------------------------------------


def vs(group: Optional[Mapping[str, object]], metric: str, arm: str, reference: str) -> Optional[dict]:
    if group is None or metric not in group:
        return None
    return group[metric]["vs"].get(arm, {}).get(reference)


def pair_cells(group: Mapping[str, object], arm: str, reference: str) -> List[str]:
    return [m1288.cell(vs(group, metric, arm, reference)) for metric in TESTED]


def mean_row(label: str, group: Mapping[str, object], models: Sequence[str]) -> str:
    return f"| {label} | {group['days']} | " + " | ".join(f"{group['grid_crps']['means'][m]:.3f}" for m in models) + " |"


def loss_table(window: Mapping[str, object], split: str, metric: str, order: Optional[Sequence[str]] = None) -> List[str]:
    labels = window["groups"].get(split, {})
    out = [f"| {split.replace('_', ' ')} | days | " + " | ".join(LABELS[m] for m in MODELS) + " |", "|---|---|" + "---|" * len(MODELS)]
    for label in (order if order is not None else sorted(labels)):
        if label not in labels:
            continue
        g = labels[label]
        digits = 4 if metric == "brier_gt5" else 3
        out.append(f"| {label} | {g['days']} | " + " | ".join(f"{g[metric]['means'][m]:.{digits}f}" for m in MODELS) + " |")
    return out if len(out) > 2 else []


def pair_table(window: Mapping[str, object], split: str, arm: str, reference: str) -> List[str]:
    labels = window["groups"].get(split, {})
    out = [f"| {split.replace('_', ' ')} | days | " + " | ".join(METRIC_TITLES[m] for m in TESTED) + " |", "|---|---|" + "---|" * len(TESTED)]
    for label in sorted(labels):
        g = labels[label]
        skipped = f"{split}/{label}" in window["skipped_groups"]
        out.append(f"| {label} | {g['days']} | " + " | ".join(
            "not tested (fewer than 20 days)" if skipped else cell for cell in pair_cells(g, arm, reference)) + " |")
    return out if len(out) > 2 else []


def pooled(window: Mapping[str, object]) -> Mapping[str, object]:
    return window["groups"]["pooled"]["all decision days"]


def _skill(row: Optional[dict]) -> str:
    if row is None or row.get("identical") or row.get("skill") is None:
        return "n/a"
    return f"{row['skill'] * 100:+.1f}%"


def headline(r: Mapping[str, object]) -> str:
    parts = []
    for window in WINDOWS:
        g = pooled(r["windows"][window])
        lag = r["windows"][window]["lag_rows"]
        text = (f"{WINDOW_TITLES[window]}: the lag of the last public row is {', '.join(f'{n:,} decision days at {l} row' + ('s' if l != '1' else '') for l, n in lag.items())}; "
                f"mean grid CRPS B1 {g['grid_crps']['means'][B1]:.3f}, B1* {g['grid_crps']['means'][B1S]:.3f}, B1' {g['grid_crps']['means'][B1P]:.3f}, "
                f"B1'* {g['grid_crps']['means'][B1PS]:.3f}, the candidate {g['grid_crps']['means'][CANDIDATE]:.3f}; the candidate's skill on grid CRPS against "
                f"B1 {_skill(vs(g, 'grid_crps', CANDIDATE, B1))}, B1* {_skill(vs(g, 'grid_crps', CANDIDATE, B1S))}, B1' "
                f"{_skill(vs(g, 'grid_crps', CANDIDATE, B1P))}, B1'* {_skill(vs(g, 'grid_crps', CANDIDATE, B1PS))}")
        parts.append(text)
    return "; ".join(parts) + ". **Development data on seen days, not a verdict.**"


def question() -> List[str]:
    return [
        "## Question for Eleonora (marked; the default changes no claim)", "",
        "**Question 1. Do B1* and B1'* replace B1 and B1' in the registered comparison?** B1 counts the change over h rows from a last public row that is one "
        "row older than the decision day; the corrected versions count h plus that lag. This page measures the difference on days already seen and decides "
        "nothing. Changing the registered benchmarks is a change to `docs/decisions/scoring-protocol.md` section 4, and so hers.", "",
        "**Options** (the default applies if you have not answered by the next 5 pm batch):", "",
        "1. **B1'* is the mandatory persistence benchmark; legacy B1 is reported for continuity** (default, and the recommendation). The registered test "
        "is run against B1'*, and B1 stays on the page as the protocol's own v1 benchmark.",
        "2. **B1* and B1'* replace B1 and B1'.** The protocol's section 4 is amended in a decision record for her to merge; B1 and B1' are retired from the "
        "registered comparison.",
        "3. **Keep B1 and B1' as the benchmarks; report B1* and B1'* as secondary.** Nothing in the registered comparison changes.", ""]


def render(r: dict) -> str:
    out = [
        "# B1* and B1'*: the persistence benchmarks with the horizon counted from the last public anchor (#1388)", "",
        "**Does counting the horizon from the last public row, not from the decision day, change how the candidate scores against persistence?** " + headline(r), "",
        "**Hypothesis and step:** H5 (primary goal), registration design (the benchmarks); her ruling of 2 November 2026 (chat, relayed on #1388) after the second "
        "outside review of (s3c-ann-net). **Development data, not a verdict** (scoring protocol v1, #640). Nothing is registered or published and no claim "
        "changes: `docs/decisions/scoring-protocol.md`, B1 and B1' as declared, the candidate and `docs/runs/` are unchanged, no day after 2026-09-03 is "
        f"scored and no locked day is scored. Made at the {r['decision_time']} New York decision instant. Generated by `scripts/b1_anchor_horizon_1388.py page` from "
        f"`docs/research/b1-anchor-horizon-1388/result.json`, not edited by hand; declared in `{r['declaration']}` before any score.", "",
        "**What changed.** B1 adds the trailing two years' h-row changes, `spread[s] - spread[s - h]`, to the last public spread. The last public row, the anchor, "
        "is `lag` panel rows before the decision day (one on every day of these windows), so the elapsed horizon from the anchor to the target is h + lag. "
        "**B1*** is B1 with each change taken over h + lag rows. **B1'*** is B1' (#960) with each change taken from the last ordinary spread h + lag rows "
        "before its end row, the centre, the pool by the target day's type and the floor of 30 unchanged. Both are in `repo_model.protocol_benchmarks` and "
        "`repo_model.b1_calendar`; neither is a benchmark of the protocol. The review called the mismatch a design question to test, not proof that a "
        "corrected B1 scores better.", "",
        f"Panel digest `{r['panel_sha256']}`. Studentized stationary bootstrap (ruling 1), mean block {sp.BLOCK_LENGTH} business days, {r['draws']:,} draws, "
        f"seed {r['seed']}, two-sided 90% interval (the lower end is the one-sided 95% bound). Positive mean d favours the arm named first in a table's "
        "heading. **A reading (gain, loss, undecided) is taken from the mean-d bound** (her ruling on #1009), with the skill interval beside it; for a Brier "
        "score the skill is the Brier skill score. **Caveat (Lens C, #958):** the lag-10 HAC standard error that studentizes the bound is understated "
        "about 2x after 2020, so an interval that excludes zero is narrower than it should be. A skill ratio against a weaker benchmark is larger: the "
        "absolute losses are beside every ratio.", ""]
    for window in WINDOWS:
        w = r["windows"][window]
        g = pooled(w)
        out += [f"## {WINDOW_TITLES[window]}", "",
                f"{w['decision_days']:,} decision days, {w['cells']:,} (decision day, lead) cells. Lag of the last public row, in panel rows: "
                + ", ".join(f"{n:,} decision days at {l}" for l, n in w["lag_rows"].items()) + ". Cells on which the corrected forecast differs from the original: "
                f"B1* {w['cells_differing_from_original'][B1S]:,}, B1'* {w['cells_differing_from_original'][B1PS]:,}.", "",
                "**Absolute losses (pooled means; lower is better)**", "",
                "| model | " + " | ".join(METRIC_TITLES[m] + " (mean)" for m in METRIC_NAMES) + " |", "|---|" + "---|" * len(METRIC_NAMES)]
        for m in MODELS:
            out.append(f"| {LABELS[m]} | " + " | ".join(
                f"{g[x]['means'][m]:.4f}" if x in ("brier_gt5", "b90_closed") else f"{g[x]['means'][m]:.3f}" for x in METRIC_NAMES) + " |")
        out += ["", "**The candidate against each persistence benchmark (pooled)**", "",
                f"| {LABELS[CANDIDATE]} against | " + " | ".join(METRIC_TITLES[m] for m in TESTED) + " |", "|---|" + "---|" * len(TESTED)]
        for ref in REFERENCES:
            out.append(f"| {LABELS[ref]} | " + " | ".join(pair_cells(g, CANDIDATE, ref)) + " |")
        out += ["", "**The corrected benchmark against the original (pooled): does the anchor-to-target window score better by itself?**", "",
                "| arm against reference | " + " | ".join(METRIC_TITLES[m] for m in TESTED) + " |", "|---|" + "---|" * len(TESTED)]
        for arm, ref in PAIRS[len(REFERENCES):]:
            out.append(f"| {LABELS[arm]} against {LABELS[ref]} | " + " | ".join(pair_cells(g, arm, ref)) + " |")
        out.append("")
        for split in SPLITS[1:]:
            if split not in w["groups"]:
                continue
            title = split.replace("_", " ")
            out += [f"### By {title}", "", "**Absolute losses, grid CRPS (mean)**", ""]
            out += loss_table(w, split, "grid_crps") + [""]
            for ref in REFERENCES:
                table = pair_table(w, split, CANDIDATE, ref)
                if table:
                    out += [f"**By {title}: {LABELS[CANDIDATE]} against {LABELS[ref]}**", ""] + table + [""]
            for arm, ref in PAIRS[len(REFERENCES):]:
                table = pair_table(w, split, arm, ref)
                if table:
                    out += [f"**By {title}: {LABELS[arm]} against {LABELS[ref]}**", ""] + table + [""]
        if w["skipped_groups"]:
            out += ["Groups of fewer than 20 days are listed, not tested: " + ", ".join(f"{k} ({n})" for k, n in sorted(w["skipped_groups"].items())) + ".", ""]
    if r.get("against_record_1314"):
        out += ["## Check against the earlier record", "",
                "The candidate's, B1's and B1''s pooled means here against #1314's record at the same instant (`" + RECORD_1314.relative_to(REPO).as_posix()
                + "`); the walks are the same, so the differences are zero.", "",
                "| window | metric | model | here | there | difference |", "|---|---|---|---|---|---|"]
        for window, rec in r["against_record_1314"].items():
            for metric, models in rec["metrics"].items():
                for m, v in models.items():
                    out.append(f"| {window} | {METRIC_TITLES[metric]} | {LABELS[m]} | {v['here']:.6f} | {v['there']:.6f} | {v['difference']:.2e} |")
        out.append("")
    out += ["## What this does not show", "",
            "- It is development data on days already seen; no verdict is read from it, and (s3c-ann-net) is unchanged.",
            "- The review's argument is about the mean reversion that the candidate uses and B1 does not. A corrected benchmark can score worse than B1; the "
            "candidate's skill against it is then larger because the reference is weaker, not because the candidate improved.",
            "- The lag is one row on every decision day of both windows (the table above), so B1* at lead h is B1 at horizon h + 1 and the study cannot show what "
            "a longer lag would do.", ""]
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
    s = sub.add_parser("score", help="walk the candidate, forecast B1* and B1'*, and score on both windows")
    s.add_argument("--panel", required=True)
    s.add_argument("--output", required=True)
    s.add_argument("--draws", type=int, default=sp.DRAWS)
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
