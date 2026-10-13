"""Ranking the next 20 business days by risk: scoring and report (#694; H8, development tier).

A scratch measurement, not a record: it writes JSON and Markdown to the paths it is given and nothing into `docs/runs/`.
Every choice is in `metadata/ranking_694.json`, which this script refuses to read unless it is committed and unchanged.
The arithmetic is `repo_model.ranking`. Scored days are decision days whose 20 targets are on or before 2025-12-31; no later
day is read (`docs/decisions/lockbox.md`). Nothing here is a verdict (scoring protocol v1, #640): the result is exploration on
development data.

    PYTHONPATH=src python3 -m repo_model.cli build --raw-root tests/fixtures/snapshots/funding_inputs \\
        --output /tmp/funding_panel.csv --build-cutoff 2026-09-08T21:31:42+00:00 --decision-time 16:00:00
    PYTHONPATH=src python3 -m repo_model.cli verify-panel /tmp/funding_panel.csv --manifest metadata/funding_panel_manifest.json
    PYTHONPATH=src python3 scripts/ranking_694.py score --panel /tmp/funding_panel.csv \\
        --output docs/pivot/evidence/ranking/score.json
    PYTHONPATH=src python3 scripts/ranking_694.py page \\
        --score docs/pivot/evidence/ranking/score.json --output docs/pivot/ranking-result.md

Stdlib only.
"""

from __future__ import annotations

import argparse
import json
import statistics
import subprocess
import sys
from datetime import date, time
from pathlib import Path
from typing import Dict, List, Mapping, Optional, Sequence

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))

from repo_model import ranking, scoring_protocol as sp  # noqa: E402
from repo_model.baseline import panel_sha256  # noqa: E402
from repo_model.data import load_daily_panel  # noqa: E402
from repo_model.evaluation_splits import load_split_declaration  # noqa: E402
from repo_model.metrics import _quantile  # noqa: E402

DECLARATION = REPO / "metadata" / "ranking_694.json"
SPLITS = REPO / "metadata" / "evaluation_splits.json"
SOURCES = REPO / "metadata" / "sources.json"
SEED = 694
BLOCK = 20.0
INTERVAL = (0.05, 0.95)
MIN_GROUP_DAYS = 20
METRICS = ("precision", "recall")


def committed_declaration(path: Path = DECLARATION) -> dict:
    """The declaration, refused unless it is committed and unchanged since `HEAD`."""

    relative = str(path.resolve().relative_to(REPO))
    dirty = subprocess.run(
        ["git", "status", "--porcelain", "--", relative], cwd=REPO, capture_output=True, text=True, check=True
    ).stdout.strip()
    if dirty:
        raise SystemExit(f"{relative} is not committed ({dirty}); a declaration is made before any score")
    return json.loads(path.read_text(encoding="utf-8"))


def interval(draws: Sequence[float]) -> List[float]:
    return [_quantile(draws, INTERVAL[0]), _quantile(draws, INTERVAL[1])]


def paired(benchmarks: Mapping[str, Mapping[date, float]], candidate: Mapping[date, float], days: Sequence[date], draws: int) -> dict:
    """The candidate's gain in a metric over each benchmark on `days`: the mean difference and its block-bootstrap interval.

    `scoring_protocol.paired_tests` takes losses (lower is better), so it is run on `1 - metric`: its difference is the
    metric's gain, positive when the candidate ranks better.
    """

    names = list(benchmarks)
    pairs = [({d: 1.0 - benchmarks[n][d] for d in days}, {d: 1.0 - candidate[d] for d in days}) for n in names]
    out = {}
    try:
        tests = sp.paired_tests(pairs, seed=SEED, draws=draws, block_length=BLOCK)
    except sp.ProtocolError as error:
        if "scores zero" not in str(error):
            raise
        return {n: {"days": len(days), "undefined": str(error),
                    "benchmark_mean": sum(benchmarks[n][d] for d in days) / len(days),
                    "candidate_mean": sum(candidate[d] for d in days) / len(days)} for n in names}
    for name, test in zip(names, tests):
        out[name] = {
            "days": test.n,
            "benchmark_mean": 1.0 - test.benchmark_mean,
            "candidate_mean": 1.0 - test.benchmark_mean + test.mean_difference,
            "gain": test.mean_difference,
            "gain_interval": interval(test.mean_difference_draws),
        }
    return out


def mean(values: Sequence[float]) -> float:
    return sum(values) / len(values)


def score(args) -> int:
    declaration = committed_declaration()
    panel_path = Path(args.panel)
    panel = load_daily_panel(panel_path)
    splits = load_split_declaration(SPLITS)
    registry = json.loads(SOURCES.read_text(encoding="utf-8"))
    dates = [row.date for row in panel]
    lead = max(ranking.LEADS)
    offered = [day for i, day in enumerate(dates) if i + lead < len(panel) and dates[i + lead] <= ranking.LAST_DAY]
    ranking.require_scored_days(offered)
    ranking.require_scored_days(dates[dates.index(day) + h] for day in offered for h in ranking.LEADS)
    walk = ranking.walk(panel, offered, registry=registry, decision_time=time(16, 0), splits=splits)
    days = sorted(walk.scores)
    position = {day: i for i, day in enumerate(dates)}
    flags = {day: ranking.realised(panel, position[day]) for day in days}
    calendar_flags = {day: [int(v) for v in walk.scores[day]["calendar"]] for day in days}

    # per decision day, per ranker: precision and recall at each k
    cells: Dict[str, Dict[int, Dict[str, Dict[date, Optional[float]]]]] = {
        r: {k: {m: {} for m in METRICS} for k in ranking.TOP_K} for r in ranking.RANKERS}
    composition = {r: {k: [] for k in ranking.TOP_K} for r in ranking.RANKERS}
    for day in days:
        for r in ranking.RANKERS:
            got = ranking.window_metrics(walk.scores[day][r], flags[day], ranking.TOP_K, ranking.TIES[r])
            for k in ranking.TOP_K:
                cells[r][k]["precision"][day] = got[k]["precision"]
                cells[r][k]["recall"][day] = got[k]["recall"]
                composition[r][k].append(
                    ranking.top_k_hits(walk.scores[day][r], calendar_flags[day], k, ranking.TIES[r]) / k)
    pressured = [d for d in days if sum(flags[d])]
    total_pressure = sum(sum(flags[d]) for d in days)
    on_calendar = sum(f * c for d in days for f, c in zip(flags[d], calendar_flags[d]))

    result: dict = {
        "issue": 694, "declaration": str(DECLARATION.relative_to(REPO)), "panel_sha256": panel_sha256(panel_path),
        "label": "development, not a verdict", "seed": SEED, "block_length": BLOCK, "draws": args.draws,
        "notes": {
            "decision_days_offered": len(offered), "skipped_for_history_or_type": len(walk.skipped),
            "scored_decision_days": len(days), "first": days[0].isoformat(), "last": days[-1].isoformat(),
            "last_target": dates[position[days[-1]] + lead].isoformat(), "refits": len(walk.fits),
        },
        "fit": {"phi": {"min": min(f.phi for f in walk.fits.values()), "median": statistics.median(f.phi for f in walk.fits.values()),
                        "max": max(f.phi for f in walk.fits.values())}},
        "base": {
            "windows": len(days), "windows_with_a_pressure_day": len(pressured),
            "share_of_windows_with_a_pressure_day": len(pressured) / len(days),
            "pressure_days_per_window": total_pressure / len(days),
            "share_of_pressure_days_on_a_scheduled_risk_date": on_calendar / total_pressure,
            "share_of_window_days_on_a_scheduled_risk_date": sum(sum(c) for c in calendar_flags.values()) / (len(days) * lead),
        },
        "means": {}, "composition": {}, "paired": {}, "splits": {},
    }
    for r in ranking.RANKERS:
        result["means"][r] = {str(k): {
            "precision_all_windows": mean([cells[r][k]["precision"][d] for d in days]),
            "precision_windows_with_a_pressure_day": mean([cells[r][k]["precision"][d] for d in pressured]),
            "recall_windows_with_a_pressure_day": mean([cells[r][k]["recall"][d] for d in pressured]),
        } for k in ranking.TOP_K}
        result["composition"][r] = {str(k): {"share_of_top_k_on_a_scheduled_risk_date": mean(composition[r][k])}
                                    for k in ranking.TOP_K}

    def series(r, k, metric, subset):
        return {d: cells[r][k][metric][d] for d in subset}

    def comparisons(subset_all: Sequence[date], subset_pressured: Sequence[date]) -> dict:
        out = {}
        for cand in ranking.CANDIDATES:
            out[cand] = {}
            for k in ranking.TOP_K:
                for label, metric, subset in (("precision", "precision", subset_all), ("recall", "recall", subset_pressured)):
                    if len(subset) < MIN_GROUP_DAYS:
                        out[cand][f"{label}@{k}"] = {"days": len(subset), "note": f"fewer than {MIN_GROUP_DAYS} days; not tested"}
                        continue
                    out[cand][f"{label}@{k}"] = paired(
                        {b: series(b, k, metric, subset) for b in ranking.BENCHMARKS}, series(cand, k, metric, subset),
                        subset, args.draws)
        return out

    result["paired"] = {"all": comparisons(days, pressured)}
    # precision on the windows with a pressure day, as a separate family
    result["paired"]["pressure_windows_precision"] = {}
    for cand in ranking.CANDIDATES:
        result["paired"]["pressure_windows_precision"][cand] = {
            f"precision@{k}": paired({b: series(b, k, "precision", pressured) for b in ranking.BENCHMARKS},
                                     series(cand, k, "precision", pressured), pressured, args.draws)
            for k in ranking.TOP_K}
    by_year: Dict[str, List[date]] = {}
    by_regime: Dict[str, List[date]] = {}
    for d in days:
        by_year.setdefault(str(d.year), []).append(d)
        by_regime.setdefault(splits.regime(d), []).append(d)
    for split, groups in (("year", by_year), ("regime", by_regime)):
        result["splits"][split] = {}
        for label, members in sorted(groups.items()):
            hot = [d for d in members if sum(flags[d])]
            entry = {"days": len(members), "days_with_a_pressure_day": len(hot)}
            if len(members) >= MIN_GROUP_DAYS:
                entry["means"] = {r: {str(k): {"precision": mean([cells[r][k]["precision"][d] for d in members]),
                                               "recall": mean([cells[r][k]["recall"][d] for d in hot]) if hot else None}
                                      for k in ranking.TOP_K} for r in ranking.RANKERS}
                entry["paired"] = comparisons(members, hot)
            else:
                entry["note"] = f"fewer than {MIN_GROUP_DAYS} decision days; not tested"
            result["splits"][split][label] = entry
    # the kill rule, applied to the primary
    primary = result["paired"]["all"]["model_prob"]["precision@5"]["calendar"]
    low, high = primary["gain_interval"]
    result["primary"] = {"comparison": "model_prob precision@5 minus calendar precision@5", **primary,
                         "interval_wholly_above_zero": low > 0.0, "kill_condition_met": not low > 0.0}
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    Path(args.output).write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"scored {len(days)} decision days; primary gain {primary['gain']:+.4f} [{low:+.4f}, {high:+.4f}]")
    return 0


def pct(x: Optional[float]) -> str:
    return "n/a" if x is None else f"{100 * x:.1f}%"


def pp(x: float) -> str:
    return f"{100 * x:+.1f} pp"


def gain_text(cell: dict) -> str:
    if "undefined" in cell:
        return "undefined"
    if "note" in cell:
        return "not tested"
    lo, hi = cell["gain_interval"]
    return f"{pp(cell['gain'])} [{pp(lo)}, {pp(hi)}]"


NAMES = {"model_prob": "model, P(> +5 bp)", "model_median": "model, median", "persistence": "persistence",
         "climatology": "climatology by day type", "calendar": "calendar of risk dates"}


def render(r: dict) -> str:
    n = r["notes"]
    base = r["base"]
    lines = [
        "# Ranking the next 20 business days: development result (#694)", "",
        "**Hypothesis and step.** H8 (ranking beats calibrating for desk use), step 1: the target, the benchmarks and a development score. "
        "Development data, exploration: not a verdict (scoring protocol v1, #640). Declaration: `metadata/ranking_694.json`, committed before any score.", "",
        f"**Days.** {n['scored_decision_days']} decision days, {n['first']} to {n['last']} (targets to {n['last_target']}); "
        f"{n['skipped_for_history_or_type']} offered days skipped for want of history. Panel `{r['panel_sha256'][:8]}…`. "
        f"Bootstrap: stationary, mean block {r['block_length']:.0f} days, {r['draws']:,} draws, seed {r['seed']}; "
        "intervals are the 5th and 95th percentile. A positive gain favours the ranker.", "",
        "## What a window holds", "",
        f"- Windows with at least one pressure day (> +5 bp): {pct(base['share_of_windows_with_a_pressure_day'])}; "
        f"mean {base['pressure_days_per_window']:.2f} pressure days per window.",
        f"- Scheduled risk dates are {pct(base['share_of_window_days_on_a_scheduled_risk_date'])} of window days and "
        f"{pct(base['share_of_pressure_days_on_a_scheduled_risk_date'])} of the pressure days.", "",
        "## Answer against the kill rule", "",
    ]
    p = r["primary"]
    lines += [
        f"Primary: precision@5 of the probability ranker against the calendar of known risk dates: "
        f"{pct(p['candidate_mean'])} against {pct(p['benchmark_mean'])}, gain {gain_text(p)}.",
        "",
        ("The interval does not lie wholly above zero: **no ranking skill beyond the calendar of known risk dates** "
         "on development data (H8's kill condition is met, as exploration, not a verdict)."
         if p["kill_condition_met"] else
         "The interval lies wholly above zero: the ranker shows skill beyond the calendar on development data "
         "(exploration, not a verdict; H8's kill condition is not met here)."), "",
        "## Top-k precision and recall (all decision days; recall on windows with a pressure day)", "",
        "| Ranker | P@3 | P@5 | R@3 | R@5 | share of top 5 on a risk date |", "|---|---|---|---|---|---|",
    ]
    for ranker, name in NAMES.items():
        m = r["means"][ranker]
        lines.append(f"| {name} | {pct(m['3']['precision_all_windows'])} | {pct(m['5']['precision_all_windows'])} | "
                     f"{pct(m['3']['recall_windows_with_a_pressure_day'])} | {pct(m['5']['recall_windows_with_a_pressure_day'])} | "
                     f"{pct(r['composition'][ranker]['5']['share_of_top_k_on_a_scheduled_risk_date'])} |")
    lines += ["", "## Paired gains over each benchmark (all decision days)", "",
              "| Ranker | Metric | vs persistence | vs climatology | vs calendar |", "|---|---|---|---|---|"]
    for cand in ranking.CANDIDATES:
        for metric, cell in r["paired"]["all"][cand].items():
            lines.append(f"| {NAMES[cand]} | {metric} | " + " | ".join(gain_text(cell[b]) for b in ranking.BENCHMARKS) + " |")
    lines += ["", "## Precision on the windows that held a pressure day", "",
              "| Ranker | Metric | vs persistence | vs climatology | vs calendar |", "|---|---|---|---|---|"]
    for cand in ranking.CANDIDATES:
        for metric, cell in r["paired"]["pressure_windows_precision"][cand].items():
            lines.append(f"| {NAMES[cand]} | {metric} | " + " | ".join(gain_text(cell[b]) for b in ranking.BENCHMARKS) + " |")
    for split, title in (("year", "calendar year of the decision day"), ("regime", "regime of the decision day")):
        lines += ["", f"## Precision@5 gain of the probability ranker, by {title}", "",
                  "| Group | Decision days | Windows with a pressure day | model P@5 | calendar P@5 | gain vs calendar | gain vs climatology | gain vs persistence |",
                  "|---|---|---|---|---|---|---|---|"]
        for label, entry in r["splits"][split].items():
            if "paired" not in entry:
                lines.append(f"| {label} | {entry['days']} | {entry['days_with_a_pressure_day']} | not tested | | | | |")
                continue
            cell = entry["paired"]["model_prob"]["precision@5"]
            means = entry["means"]
            lines.append(f"| {label} | {entry['days']} | {entry['days_with_a_pressure_day']} | "
                         f"{pct(means['model_prob']['5']['precision'])} | {pct(means['calendar']['5']['precision'])} | "
                         f"{gain_text(cell['calendar'])} | {gain_text(cell['climatology'])} | {gain_text(cell['persistence'])} |")
    lines += ["", f"Phi across refits: {r['fit']['phi']['min']:.2f} to {r['fit']['phi']['max']:.2f}, median {r['fit']['phi']['median']:.2f}.", ""]
    return "\n".join(lines)


def page(args) -> int:
    result = json.loads(Path(args.score).read_text(encoding="utf-8"))
    Path(args.output).write_text(render(result), encoding="utf-8")
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
    two.set_defaults(func=page)
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
