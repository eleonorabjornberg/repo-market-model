"""Ranking the next 20 business days by tail probability combined with the day type: scoring and report (#765; H8 step 2, development tier).

A scratch measurement, not a record: it writes JSON and Markdown to the paths it is given and nothing into `docs/runs/`.
Every choice is in `metadata/ranking_765.json`, which this script refuses to read unless it is committed and unchanged.
The arithmetic is `repo_model.ranking_daytype` on `repo_model.ranking`; the windows, days, outcomes, metrics and bootstrap
are those of `scripts/ranking_694.py` (imported, with the seed set to 765). Scored days are decision days whose 20 targets
are on or before 2025-12-31; no later day is read (`docs/decisions/lockbox.md`). Nothing here is a verdict (scoring protocol
v1, #640): the result is exploration on development data.

    PYTHONPATH=src python3 -m repo_model.cli build --raw-root tests/fixtures/snapshots/funding_inputs \\
        --output /tmp/funding_panel.csv --build-cutoff 2026-09-08T21:31:42+00:00 --decision-time 16:00:00
    PYTHONPATH=src python3 -m repo_model.cli verify-panel /tmp/funding_panel.csv --manifest metadata/funding_panel_manifest.json
    PYTHONPATH=src python3 scripts/ranking_765.py score --panel /tmp/funding_panel.csv \\
        --output docs/pivot/evidence/ranking-924/score.json
    PYTHONPATH=src python3 scripts/ranking_765.py page \\
        --score docs/pivot/evidence/ranking-924/score.json --output docs/pivot/ranking-924-result.md \\
        --title "H8 step 2 re-scored with the calendar read as announced (#924)" --note docs/pivot/evidence/ranking-924/note.md

The scarcity state is read from the measurement panel (`scripts/pressure_judge.py::_scarcity_states`), which builds it from the
tracked fixtures. Stdlib only.
"""

from __future__ import annotations

import argparse
import collections
import importlib.util
import json
import statistics
import sys
from datetime import date, time
from pathlib import Path
from typing import Dict, List, Optional, Sequence

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))

from repo_model import ranking, ranking_daytype as rd, scoring_protocol as sp  # noqa: E402
from repo_model.baseline import panel_sha256  # noqa: E402
from repo_model.data import load_daily_panel  # noqa: E402
from repo_model.evaluation_splits import load_split_declaration  # noqa: E402
from repo_model.scarcity import STATE_LABELS  # noqa: E402


def _load(name: str):
    spec = importlib.util.spec_from_file_location(name, REPO / "scripts" / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


base = _load("ranking_694")
base.SEED = 765  # the declared seed of this step; `base.paired` reads it at call time

DECLARATION = REPO / "metadata" / "ranking_765.json"
SPLITS = REPO / "metadata" / "evaluation_splits.json"
SOURCES = REPO / "metadata" / "sources.json"
SEED = base.SEED
BLOCK = base.BLOCK
SENSITIVITY_BLOCK = base.SENSITIVITY_BLOCK
MIN_GROUP_DAYS = base.MIN_GROUP_DAYS
METRICS = base.METRICS
COMPARED = rd.BENCHMARKS + (rd.REFERENCE,)


def scarcity_by_decision_day(days: Sequence[date], panel_dates: Sequence[date]) -> Dict[date, str]:
    """The as-of scarcity state of each decision day: the state read for the next panel day at horizon 1, whose forecast is
    made at this day's decision instant (each leg at its own latest public row, #586)."""

    pj = _load("pressure_judge")
    states = pj._scarcity_states(1, ranking.LAST_DAY)
    position = {d: i for i, d in enumerate(panel_dates)}
    out = {}
    for day in days:
        state = states.get(panel_dates[position[day] + 1])
        out[day] = "unknown" if state is None else STATE_LABELS[int(state)]
    return out


def score(args) -> int:
    base.committed_declaration(DECLARATION)
    panel_path = Path(args.panel)
    panel = load_daily_panel(panel_path)
    splits = load_split_declaration(SPLITS)
    registry = json.loads(SOURCES.read_text(encoding="utf-8"))
    dates = [row.date for row in panel]
    lead = max(ranking.LEADS)
    offered = [day for i, day in enumerate(dates) if i + lead < len(panel) and dates[i + lead] <= ranking.LAST_DAY]
    ranking.require_scored_days(offered)
    ranking.require_scored_days(dates[dates.index(day) + h] for day in offered for h in ranking.LEADS)
    walk = rd.walk(panel, offered, registry=registry, decision_time=time(16, 0), splits=splits)
    days = sorted(walk.scores)
    position = {day: i for i, day in enumerate(dates)}
    flags = {day: ranking.realised(panel, position[day]) for day in days}
    calendar_flags = {day: [int(v) for v in walk.scores[day]["calendar"]] for day in days}
    scarcity = scarcity_by_decision_day(days, dates)

    cells: Dict[str, Dict[int, Dict[str, Dict[date, Optional[float]]]]] = {
        r: {k: {m: {} for m in METRICS} for k in ranking.TOP_K} for r in rd.RANKERS}
    composition = {r: {k: [] for k in ranking.TOP_K} for r in rd.RANKERS}
    for day in days:
        for r in rd.RANKERS:
            got = ranking.window_metrics(walk.scores[day][r], flags[day], ranking.TOP_K, rd.TIES[r])
            for k in ranking.TOP_K:
                cells[r][k]["precision"][day] = got[k]["precision"]
                cells[r][k]["recall"][day] = got[k]["recall"]
                composition[r][k].append(ranking.top_k_hits(walk.scores[day][r], calendar_flags[day], k, rd.TIES[r]) / k)
    pressured = [d for d in days if sum(flags[d])]
    total_pressure = sum(sum(flags[d]) for d in days)
    on_calendar = sum(f * c for d in days for f, c in zip(flags[d], calendar_flags[d]))
    weights = collections.Counter(w for w, _ in walk.weights.values())

    result: dict = {
        "issue": 765, "declaration": str(DECLARATION.relative_to(REPO)), "panel_sha256": panel_sha256(panel_path),
        "label": "development, not a verdict", "seed": SEED, "block_length": BLOCK, "draws": args.draws,
        "notes": {
            "decision_days_offered": len(offered), "skipped_for_history_or_type": len(walk.skipped),
            "scored_decision_days": len(days), "first": days[0].isoformat(), "last": days[-1].isoformat(),
            "last_target": dates[position[days[-1]] + lead].isoformat(), "refits": len(walk.fits),
        },
        "fit": {"phi": {"min": min(f.phi for f in walk.fits.values()), "median": statistics.median(f.phi for f in walk.fits.values()),
                        "max": max(f.phi for f in walk.fits.values())}},
        "blend": {"weights_chosen": {str(w): n for w, n in sorted(weights.items())},
                  "refits": len(walk.weights),
                  "refits_on_the_default": sum(1 for _, used in walk.weights.values() if used < rd.MIN_TRAILING),
                  "mean_weight_in_force": statistics.fmean(walk.weight_used.values())},
        "tail_by_type": {"share_of_target_leads_on_the_fallback": walk.fallback_share()},
        "base": {
            "windows": len(days), "windows_with_a_pressure_day": len(pressured),
            "share_of_windows_with_a_pressure_day": len(pressured) / len(days),
            "pressure_days_per_window": total_pressure / len(days),
            "share_of_pressure_days_on_a_scheduled_risk_date": on_calendar / total_pressure,
            "share_of_window_days_on_a_scheduled_risk_date": sum(sum(c) for c in calendar_flags.values()) / (len(days) * lead),
        },
        "means": {}, "composition": {}, "paired": {}, "splits": {},
    }
    mean = base.mean
    for r in rd.RANKERS:
        result["means"][r] = {str(k): {
            "precision_all_windows": mean([cells[r][k]["precision"][d] for d in days]),
            "precision_windows_with_a_pressure_day": mean([cells[r][k]["precision"][d] for d in pressured]),
            "recall_windows_with_a_pressure_day": mean([cells[r][k]["recall"][d] for d in pressured]),
        } for k in ranking.TOP_K}
        result["composition"][r] = {str(k): {"share_of_top_k_on_a_scheduled_risk_date": mean(composition[r][k])}
                                    for k in ranking.TOP_K}

    def series(r, k, metric, subset):
        return {d: cells[r][k][metric][d] for d in subset}

    def one(cand, k, label, metric, subset, block=BLOCK):
        return base.paired({b: series(b, k, metric, subset) for b in COMPARED}, series(cand, k, metric, subset), subset,
                           args.draws, block=block)

    def comparisons(subset_all: Sequence[date], subset_pressured: Sequence[date]) -> dict:
        out = {}
        for cand in rd.CANDIDATES:
            out[cand] = {}
            for k in ranking.TOP_K:
                for label, metric, subset in (("precision", "precision", subset_all), ("recall", "recall", subset_pressured)):
                    if len(subset) < MIN_GROUP_DAYS:
                        out[cand][f"{label}@{k}"] = {"days": len(subset), "note": f"fewer than {MIN_GROUP_DAYS} days; not tested"}
                        continue
                    out[cand][f"{label}@{k}"] = one(cand, k, label, metric, subset)
        return out

    result["paired"] = {"all": comparisons(days, pressured)}
    result["sensitivity_block"] = {"block_length": SENSITIVITY_BLOCK, "label": "sensitivity, not the declared block", "paired": {
        cand: {f"{label}@{k}": one(cand, k, label, metric, subset, SENSITIVITY_BLOCK)
               for k in ranking.TOP_K for label, metric, subset in (("precision", "precision", days), ("recall", "recall", pressured))}
        for cand in rd.CANDIDATES}}
    result["paired"]["pressure_windows_precision"] = {
        cand: {f"precision@{k}": one(cand, k, "precision", "precision", pressured) for k in ranking.TOP_K}
        for cand in rd.CANDIDATES}
    groupings: Dict[str, Dict[str, List[date]]] = {"year": {}, "regime": {}, "scarcity": {}}
    for d in days:
        groupings["year"].setdefault(str(d.year), []).append(d)
        groupings["regime"].setdefault(splits.regime(d), []).append(d)
        groupings["scarcity"].setdefault(scarcity[d], []).append(d)
    for split, groups in groupings.items():
        result["splits"][split] = {}
        for label, members in sorted(groups.items()):
            hot = [d for d in members if sum(flags[d])]
            entry = {"days": len(members), "days_with_a_pressure_day": len(hot)}
            if len(members) >= MIN_GROUP_DAYS:
                entry["means"] = {r: {str(k): {"precision": mean([cells[r][k]["precision"][d] for d in members]),
                                               "recall": mean([cells[r][k]["recall"][d] for d in hot]) if hot else None}
                                      for k in ranking.TOP_K} for r in rd.RANKERS}
                entry["paired"] = comparisons(members, hot)
            else:
                entry["note"] = f"fewer than {MIN_GROUP_DAYS} decision days; not tested"
            result["splits"][split][label] = entry
    result["primary"] = {}
    for cand in rd.CANDIDATES:
        cell = result["paired"]["all"][cand]["precision@5"]["calendar"]
        low, high = cell["gain_interval"]
        loses = []
        for split in groupings:
            for label, entry in result["splits"][split].items():
                if "paired" not in entry:
                    continue
                got = entry["paired"][cand]["precision@5"]["calendar"]
                if "gain" in got and got["gain"] < 0:
                    loses.append({"split": split, "group": label, "gain": got["gain"], "interval": got["gain_interval"],
                                  "interval_wholly_below_zero": got["gain_interval"][1] < 0})
        result["primary"][cand] = {**cell, "interval_wholly_above_zero": low > 0.0, "kill_condition_met": not low > 0.0,
                                   "loses": loses}
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    Path(args.output).write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    for cand, p in result["primary"].items():
        print(f"{cand}: P@5 gain over the calendar {p['gain']:+.4f} [{p['gain_interval'][0]:+.4f}, {p['gain_interval'][1]:+.4f}]")
    print(f"scored {len(days)} decision days")
    return 0


pct, pp, gain_text = base.pct, base.pp, base.gain_text
NAMES = {"calendar_then_tail": "(a) calendar first, tail within", "tail_by_type": "(b) tail probability by day type",
         "blend": "(c) blend of calendar and tail ranks", "model_prob": "step 1: model, P(> +5 bp) (reference)",
         "persistence": "persistence", "climatology": "climatology by day type", "calendar": "calendar of risk dates"}
HEAD = "| Ranker | Metric | vs persistence | vs climatology | vs calendar | vs step 1 |"


def row(cand: str, metric: str, cell: dict) -> str:
    return f"| {NAMES[cand]} | {metric} | " + " | ".join(gain_text(cell[b]) for b in COMPARED) + " |"


def render(r: dict, title: Optional[str] = None, note: Optional[str] = None) -> str:
    n, b = r["notes"], r["base"]
    lines = [
        "# " + (title or "Ranking the next 20 business days by tail probability and day type: development result (#765)"), "",
    ] + ([note, ""] if note else []) + [
        "**Hypothesis and step.** H8 (ranking beats calibrating for desk use), step 2: rank by tail probability combined with the day type. "
        "Development data, exploration: not a verdict (scoring protocol v1, #640). Declaration: `metadata/ranking_765.json`, committed before any score. "
        "The +5 bp level is only the ranking quantity carried over from step 1; nothing is fitted to the +5 bp event.", "",
        f"**Days.** {n['scored_decision_days']} decision days, {n['first']} to {n['last']} (targets to {n['last_target']}); "
        f"{n['skipped_for_history_or_type']} offered days skipped for want of history. Panel `{r['panel_sha256'][:8]}…`. "
        f"Bootstrap: stationary, mean block {r['block_length']:.0f} days, {r['draws']:,} draws, seed {r['seed']}; "
        "intervals are the 5th and 95th percentile. A positive gain favours the ranker. Same windows and days as step 1 (#722).", "",
        "## What a window holds", "",
        f"- Windows with at least one pressure day (> +5 bp): {pct(b['share_of_windows_with_a_pressure_day'])}; "
        f"mean {b['pressure_days_per_window']:.2f} pressure days per window.",
        f"- Scheduled risk dates are {pct(b['share_of_window_days_on_a_scheduled_risk_date'])} of window days and "
        f"{pct(b['share_of_pressure_days_on_a_scheduled_risk_date'])} of the pressure days.",
        f"- (b) took the all-type fallback on {pct(r['tail_by_type']['share_of_target_leads_on_the_fallback'])} of target leads (pool under {rd.MIN_POOL}).",
        f"- (c) weights chosen at {r['blend']['refits']} refits ({r['blend']['refits_on_the_default']} on the default 0.5 for want of "
        f"{rd.MIN_TRAILING} trailing windows): " + ", ".join(f"w = {w}: {c}" for w, c in r["blend"]["weights_chosen"].items())
        + f"; mean weight in force {r['blend']['mean_weight_in_force']:.2f}.", "",
        "## Top-k precision and recall (all decision days; recall on windows with a pressure day)", "",
        "| Ranker | P@3 | P@5 | R@3 | R@5 | share of top 5 on a risk date |", "|---|---|---|---|---|---|",
    ]
    for ranker in rd.CANDIDATES + rd.BENCHMARKS + (rd.REFERENCE,):
        m = r["means"][ranker]
        lines.append(f"| {NAMES[ranker]} | {pct(m['3']['precision_all_windows'])} | {pct(m['5']['precision_all_windows'])} | "
                     f"{pct(m['3']['recall_windows_with_a_pressure_day'])} | {pct(m['5']['recall_windows_with_a_pressure_day'])} | "
                     f"{pct(r['composition'][ranker]['5']['share_of_top_k_on_a_scheduled_risk_date'])} |")
    lines += ["", "## Paired gains over each benchmark (all decision days)", "", HEAD, "|---|---|---|---|---|---|"]
    for cand in rd.CANDIDATES:
        for metric, cell in r["paired"]["all"][cand].items():
            lines.append(row(cand, metric, cell))
    sens = r["sensitivity_block"]
    lines += ["", f"## Sensitivity: the protocol's block of {sens['block_length']:.0f} days instead of the declared {r['block_length']:.0f}", "",
              "Same draws and seed, only the mean block changes (ruling on #722, item 2). Labelled a sensitivity.", "", HEAD, "|---|---|---|---|---|---|"]
    for cand in rd.CANDIDATES:
        for metric, cell in sens["paired"][cand].items():
            lines.append(row(cand, metric, cell))
    lines += ["", "Primary under block 10: " + "; ".join(
        f"{NAMES[c]} [{pp(sens['paired'][c]['precision@5']['calendar']['gain_interval'][0])}, "
        f"{pp(sens['paired'][c]['precision@5']['calendar']['gain_interval'][1])}]" for c in rd.CANDIDATES) + ".",
        "", "## Precision on the windows that held a pressure day", "", HEAD, "|---|---|---|---|---|---|"]
    for cand in rd.CANDIDATES:
        for metric, cell in r["paired"]["pressure_windows_precision"][cand].items():
            lines.append(row(cand, metric, cell))
    titles = {"year": "calendar year of the decision day", "regime": "regime of the decision day (2021-23 is the one called out)",
              "scarcity": "as-of reserve scarcity state of the decision day"}
    for split, title in titles.items():
        for cand in rd.CANDIDATES:
            lines += ["", f"## Precision@5 of {NAMES[cand]}, by {title}", "",
                      "| Group | Decision days | Windows with a pressure day | ranker P@5 | calendar P@5 | gain vs calendar | gain vs climatology | gain vs persistence |",
                      "|---|---|---|---|---|---|---|---|"]
            for label, entry in r["splits"][split].items():
                if "paired" not in entry:
                    lines.append(f"| {label} | {entry['days']} | {entry['days_with_a_pressure_day']} | not tested | | | | |")
                    continue
                cell = entry["paired"][cand]["precision@5"]
                means = entry["means"]
                lines.append(f"| {label} | {entry['days']} | {entry['days_with_a_pressure_day']} | "
                             f"{pct(means[cand]['5']['precision'])} | {pct(means['calendar']['5']['precision'])} | "
                             f"{gain_text(cell['calendar'])} | {gain_text(cell['climatology'])} | {gain_text(cell['persistence'])} |")
    lines += [
        "", "## Reading", "",
        "- (a) puts every scheduled risk date above every other day, so its top 5 are the calendar's whenever the window holds five; the tail "
        "probability only chooses among them and fills the places when fewer than five are scheduled. (b) and (c) are the two ways of letting the day type "
        "move the probability or the rank.",
        "- A window with no pressure day scores zero precision for every ranker, so years with none (2021-23) add decision days and no information; "
        "recall is taken on the windows that have one.",
        "- The risk-date definition is `pressure_judge._scheduled_risk_date`, as in step 1. The calendar benchmark breaks its ties by date; the other rankers by their expected value.",
        "- Development data only, nothing registered, no published figure moves. Whether any ranker goes on to registration (step 3) is Eleonora's decision.", "",
        f"Phi across refits: {r['fit']['phi']['min']:.2f} to {r['fit']['phi']['max']:.2f}, median {r['fit']['phi']['median']:.2f}.", "",
        "## Each ranker against the calendar (precision@5, development, not a verdict)", "",
    ]
    for cand in rd.CANDIDATES:
        p = r["primary"][cand]
        worse = [x for x in p["loses"] if x["interval_wholly_below_zero"]]
        point = [x for x in p["loses"] if not x["interval_wholly_below_zero"]]
        text = f"- **{NAMES[cand]}:** {pct(p['candidate_mean'])} against {pct(p['benchmark_mean'])}, gain {gain_text(p)}; "
        text += ("the interval lies wholly above zero." if p["interval_wholly_above_zero"]
                 else "the interval lies wholly below zero (H8's kill condition is met, as exploration)." if p["gain_interval"][1] < 0
                 else "the interval does not lie wholly above zero (H8's kill condition is met, as exploration).")
        if worse:
            text += " Loses (interval wholly below zero): " + ", ".join(f"{x['split']} {x['group']} {pp(x['gain'])}" for x in worse) + "."
        if point:
            text += " Below zero in point estimate only: " + ", ".join(f"{x['split']} {x['group']} {pp(x['gain'])}" for x in point) + "."
        if not p["loses"]:
            text += " Loses in no tested group."
        lines.append(text)
    lines.append("")
    return "\n".join(lines)


def page(args) -> int:
    result = json.loads(Path(args.score).read_text(encoding="utf-8"))
    note = Path(args.note).read_text(encoding="utf-8").strip() if args.note else None
    Path(args.output).write_text(render(result, title=args.title, note=note), encoding="utf-8")
    return 0


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="command", required=True)
    one = sub.add_parser("score")
    one.add_argument("--panel", required=True)
    one.add_argument("--output", required=True)
    one.add_argument("--draws", type=int, default=sp.DRAWS)
    one.set_defaults(func=score)
    two = sub.add_parser("page")
    two.add_argument("--score", required=True)
    two.add_argument("--output", required=True)
    two.add_argument("--title")
    two.add_argument("--note", help="a file whose text goes under the title (a re-score says what it replaces)")
    two.set_defaults(func=page)
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
