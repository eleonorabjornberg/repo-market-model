"""#1228's day-type measurement re-run on main, with the studentized domain interval beside it (#1266; H5 step 3 reporting; H1 scorer).

A development study, never a verdict. It changes no page's reading, no declaration, no group floor and nothing in `docs/runs/`; it
writes JSON and Markdown to the paths it is given. Her ruling of 27 October 2026 (ledger item 63 on #1116, option 1 on finding #1262).

Why a re-run. #1228's page was scored at a56d745d, before #1202 put the B2 thin-pool record in force; its counts are not main's, and
its script checked the current rows against `s3-terms-1196/result.json`, which #1253 has since superseded. This script runs
`scripts/day_type_domain_1228.py`'s measurement on the tree it is run on, with #1196's declared settings (`metadata/s3_terms_1196.json`,
seed 1196, 10,000 draws, mean block 10, the published panel), and checks the current rows against `docs/research/s3-terms-1243/result.json`.

What it adds. For every target-day-type row (grid CRPS and upper-tail twCRPS, four arms against their references) three intervals on the
same days:

* current: the group's own days to `run_pairs` (a studentized interval on a short series of the group's days);
* percentile domain (#1228): the whole aligned target-day series resampled, the mean of d over the resampled days of the group, the 90%
  percentile interval;
* studentized domain (#1266): the same resamples, each resample's group mean studentized by its own HAC standard error
  (`domain_intervals.studentized_domain_estimates`; the delta method on the whole-series frame, Bartlett lag 10).

The three are read by the same rule (her #1009 ruling: the bound on mean d), so the readings that change are counted pair by pair. The
page also reports the coverage of the three one-sided 95% lower bounds on synthetic AR(1) series with group days 60 apart.

Commands, from a clone of the branch (the score takes about half an hour on 4 cores; the coverage a few minutes):

    PYTHONPATH=src python3 -m repo_model.cli build --raw-root tests/fixtures/snapshots/funding_inputs \\
        --output PUB.csv --build-cutoff 2026-09-08T21:31:42+00:00 --decision-time 16:00:00
    PYTHONPATH=src python3 -m repo_model.cli verify-panel PUB.csv --manifest metadata/funding_panel_manifest.json
    PYTHONPATH=src python3 scripts/day_type_domain_1266.py score --panel PUB.csv --output docs/research/day-type-domain-1266/result.json
    PYTHONPATH=src python3 scripts/day_type_domain_1266.py coverage --score docs/research/day-type-domain-1266/result.json
    PYTHONPATH=src python3 scripts/day_type_domain_1266.py page \\
        --score docs/research/day-type-domain-1266/result.json --output docs/research/day-type-domain-1266-result.md

Stdlib only.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import multiprocessing
import random
import sys
from datetime import date, timedelta
from pathlib import Path
from typing import Dict, List, Mapping, Optional, Sequence, Tuple

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))


def _load(name: str):
    spec = importlib.util.spec_from_file_location(name, REPO / "scripts" / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


from repo_model import announced_iorb, scoring_protocol as sp  # noqa: E402
from repo_model import spread_mr_calendar as cal  # noqa: E402
from repo_model.baseline import panel_sha256  # noqa: E402
from repo_model.data import load_daily_panel  # noqa: E402
from repo_model.domain_intervals import domain_estimates, studentized_domain_estimates  # noqa: E402
from repo_model.evaluation_splits import load_split_declaration  # noqa: E402

d1228 = _load("day_type_domain_1228")
t, c, s761 = d1228.t, d1228.c, d1228.s761

ISSUE = 1266
SEED = d1228.SEED
#: The record the current rows are checked against: #1253's re-score of #1196, which supersedes `s3-terms-1196/result.json`.
COMMITTED = REPO / "docs" / "research" / "s3-terms-1243" / "result.json"
#: #1228's own record, kept as the page of what was run on a56d745d; its counts are compared on the page.
OLD_1228 = REPO / "docs" / "research" / "day-type-domain-1228" / "result.json"
METRICS, ARMS, SPLIT, SHORT, READINGS = d1228.METRICS, d1228.ARMS, d1228.SPLIT, d1228.SHORT, d1228.READINGS
NAMED = d1228.NAMED
reading, width, tally = d1228.reading, d1228.width, d1228.tally
#: The three intervals, in the order the page shows them.
KINDS = ("current", "percentile", "studentized")
#: The pairs of intervals whose readings are compared: (from, to).
PAIRS = (("current", "percentile"), ("current", "studentized"), ("percentile", "studentized"))
NAME = {"current": "current", "percentile": "percentile domain", "studentized": "studentized domain"}

_STATE: Dict = {}


def studentized_rows(cells: Mapping[object, Tuple[Mapping[date, float], Mapping[date, float], Sequence[date]]],
                     all_days: Sequence[date], seed: int = SEED, draws: int = sp.DRAWS, block_length: float = sp.BLOCK_LENGTH,
                     level: float = 0.90) -> Dict[object, dict]:
    """The studentized domain estimate of each group's mean paired difference, as `spread_mr_variants_761.domain_rows` makes the
    percentile one: the same cells `(benchmark scores, candidate scores, the group's days)`, the same draws, a row with the group
    mean as `difference` and the interval as `difference_interval`, without skill; `method` says "studentized domain". A group
    whose interval is unavailable reads `undefined` with the reason, as `run_pairs` does; a bound read with resamples left out
    carries `dropped_resamples` and `draws` (#1239)."""

    days = sorted(all_days)
    position = {day: i for i, day in enumerate(days)}
    prepared = {}
    for key, (benchmark, candidate, group) in cells.items():
        missing = [day for day in group if day not in position]
        if missing:
            raise ValueError(f"cell {key!r}: {len(missing)} group days ({missing[0]} first) are not among the {len(days)} aligned days")
        prepared[key] = ([benchmark[day] - candidate[day] for day in days], [position[day] for day in group])
    done = studentized_domain_estimates(prepared, len(days), block_length=block_length, seed=seed, replications=draws, level=level)
    out: Dict[object, dict] = {}
    for key, (benchmark, candidate, group) in cells.items():
        entry = done[key]
        row = {"days": entry["count"], "method": "studentized domain",
               "benchmark_mean": sum(benchmark[d] for d in group) / len(group) if group else None,
               "candidate_mean": sum(candidate[d] for d in group) / len(group) if group else None}
        if "interval" in entry:
            row["difference"] = entry["mean"]
            row["difference_interval"] = [entry["interval"]["lower"], entry["interval"]["upper"]]
            row["standard_error"] = entry["standard_error"]
            if entry["dropped_resamples"]:
                row["dropped_resamples"], row["draws"] = entry["dropped_resamples"], entry["draws"]
        else:
            row["undefined"] = entry.get("interval_unavailable", "the group has no day")
        out[key] = row
    return out


def compare3(rows: Mapping[str, Optional[dict]]) -> dict:
    """One cell: the three readings, the pairs that change, and the widths of the studentized interval over the others."""

    readings = {k: reading(rows[k]) for k in KINDS}
    out = {"readings": readings, "changes": {f"{a}>{b}": readings[a] != readings[b] for a, b in PAIRS}}
    for other in ("current", "percentile"):
        wa, wb = width(rows[other]), width(rows["studentized"])
        out[f"width_ratio_vs_{other}"] = None if wa is None or wb is None or wa == 0.0 else wb / wa
    return out


def tally_pair(cells: Sequence[dict], a: str, b: str) -> dict:
    """The counts of the cells by (reading under a, reading under b), and how many change."""

    return tally([{"current_reading": x["readings"][a], "domain_reading": x["readings"][b], "changes": x["changes"][f"{a}>{b}"]}
                  for x in cells])


def tallies(cells: Sequence[dict]) -> dict:
    return {f"{a}>{b}": tally_pair(cells, a, b) for a, b in PAIRS}


def _current_task(job):
    label, metric, candidate, members = job
    series = _STATE["series"][("target", metric)]
    out = {}
    for name in t.pair_plan(candidate, ()):
        out[name] = s761.run_pairs({name: series[name]}, series[candidate], list(members), seed=SEED, draws=_STATE["draws"],
                                   mean_d_fallback=True)[name]
    return (label, metric, candidate), out


def _cells_of(metric, groups):
    series = _STATE["series"][("target", metric)]
    request = {}
    for label, candidate, members in groups:
        for name in t.pair_plan(candidate, ()):
            request[(label, candidate, name)] = (series[name], series[candidate], members)
    return sorted(series["B1"]), request


def _domain_task(job):
    metric, groups, studentized = job
    all_days, request = _cells_of(metric, groups)
    make = studentized_rows if studentized else s761.domain_rows
    rows = make(request, all_days, seed=SEED, draws=_STATE["draws"])
    out: Dict = {}
    for (label, candidate, name), row in rows.items():
        out.setdefault((label, metric, candidate), {})[name] = row
    return out


def _dispatch(job):
    kind, payload = job
    if kind == "current":
        return kind, _current_task(payload)
    return kind, _domain_task(payload)


def run_jobs(jobs, workers: int):
    with multiprocessing.get_context("fork").Pool(workers) as pool:
        return pool.map(_dispatch, jobs, chunksize=1)


def reproduction(current: Mapping, committed: Mapping) -> dict:
    """Which current rows differ from `docs/research/s3-terms-1243/result.json`, to the last digit."""

    same = differ = 0
    first: List[str] = []
    for (label, metric, candidate), rows in current.items():
        for name, row in rows.items():
            before = committed["groups"][SPLIT][label][metric]["vs"][candidate].get(name)
            if before == json.loads(json.dumps(row)):
                same += 1
            else:
                differ += 1
                if len(first) < 10:
                    first.append(f"{label}/{metric}/{candidate}/{name}")
    return {"identical_rows": same, "differing_rows": differ, "first_differing": first}


def score(args) -> int:
    declaration = t.committed_declaration()
    panel_path = Path(args.panel)
    panel = load_daily_panel(panel_path)
    splits = load_split_declaration(c.SPLITS)
    registry = json.loads(c.SOURCES.read_text(encoding="utf-8"))
    table = cal.TermTable(panel, announced_iorb.load_announcements(c.IORB_TABLE), decision_time=t.DECISION_TIME)
    states = t.decision_states(c.SOURCES)
    frame, notes, _mine = t.build_frame(panel, splits, registry, table, states, args.first)
    published_sha = panel_sha256(panel_path)
    labels = c.day_labels(frame, table)
    cells = {m: t.cell_table(frame, frame.forecasts[m]) for m in t.MODELS}
    series = {("target", metric): {m: c.series_of(frame, cells[m][metric], "target") for m in t.MODELS} for metric in METRICS}
    _STATE.update(series=series, draws=args.draws)

    groups = [(label, tuple(sorted(members))) for split, label, _grain, members in c.groups_of(frame, labels) if split == SPLIT]
    skipped = {label: len(members) for label, members in groups if len(members) < t.MIN_GROUP_DAYS}
    groups = [(label, members) for label, members in groups if len(members) >= t.MIN_GROUP_DAYS]
    request = [(label, candidate, members) for label, members in groups for candidate in ARMS]
    # the studentized jobs are the long ones: one per (metric, group), each regenerating the same resample stream
    jobs = [("domain", (metric, [x for x in request if x[0] == label], True)) for label, _ in groups for metric in METRICS]
    jobs += [("domain", (metric, request, False)) for metric in METRICS]
    jobs += [("current", (label, metric, candidate, members)) for label, members in groups for metric in METRICS for candidate in ARMS]
    done = run_jobs(jobs, args.workers)
    # the percentile and the studentized jobs are told apart by the row's method
    current: Dict = {}
    percentile: Dict = {}
    studentized: Dict = {}
    for kind, payload in done:
        if kind == "current":
            current[payload[0]] = payload[1]
            continue
        for key, rows in payload.items():
            target = studentized if any(r["method"] == "studentized domain" for r in rows.values()) else percentile
            target.setdefault(key, {}).update(rows)

    result: dict = {
        "issue": ISSUE, "label": "development, not a verdict", "panel_sha256": published_sha, "seed": SEED, "draws": args.draws,
        "block_length": sp.BLOCK_LENGTH, "level": 0.90, "hac_lag": sp.HAC_LAG, "declaration": str(t.DECLARATION.relative_to(REPO)),
        "reading_rules": declaration["reading_rules"], "notes": notes, "split": SPLIT, "metrics": list(METRICS),
        "arms": list(ARMS), "min_group_days": t.MIN_GROUP_DAYS, "skipped_groups": skipped,
        "target_days": len(series[("target", METRICS[0])]["B1"]), "rows": [],
    }
    for label, members in groups:
        for metric in METRICS:
            for candidate in ARMS:
                key = (label, metric, candidate)
                for name in t.pair_plan(candidate, ()):
                    three = {"current": current[key][name], "percentile": percentile[key][name], "studentized": studentized[key][name]}
                    result["rows"].append({"group": label, "days": len(members), "metric": metric, "arm": candidate, "reference": name,
                                           **three, **compare3(three)})
    rows = result["rows"]
    result["tally"] = tallies(rows)
    result["tally_by_metric"] = {m: tallies([r for r in rows if r["metric"] == m]) for m in METRICS}
    result["tally_by_group"] = {label: tallies([r for r in rows if r["group"] == label]) for label, _ in groups}
    result["dropped"] = {"rows_with_dropped_resamples": sum(1 for r in rows if "dropped_resamples" in r["studentized"]),
                         "undefined_rows": {k: sum(1 for r in rows if "undefined" in r[k]) for k in KINDS}}
    if args.first is None and COMMITTED.exists():
        result["reproduces_1243"] = reproduction(current, json.loads(COMMITTED.read_text(encoding="utf-8")))
    if args.first is None and OLD_1228.exists():
        old = json.loads(OLD_1228.read_text(encoding="utf-8"))
        result["against_1228"] = {"panel_sha256": old["panel_sha256"], "target_days": old["target_days"], "cells": old["tally"]["cells"],
                                  "changed": old["tally"]["changed"], "matrix": old["tally"]["matrix"],
                                  "by_group": {k: v["changed"] for k, v in old["tally_by_group"].items()},
                                  "scored_decision_days": old["notes"]["scored_decision_days"]}
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    Path(args.output).write_text(json.dumps(result, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    return 0


# -- the synthetic coverage ---------------------------------------------------------------------------------------------


def ar1(n: int, phi: float, mean: float, seed: int) -> List[float]:
    rng = random.Random(seed)
    x, out = 0.0, []
    for _ in range(n):
        x = phi * x + rng.gauss(0.0, 1.0)
        out.append(mean + x)
    return out


def coverage_rep(job):
    """One synthetic series: for each interval, whether its one-sided lower bound lies at or below the known mean, and whether the
    two-sided 90% interval holds it."""

    rep, n, spacing, mean, phi, draws = job
    days = [date(2018, 1, 1) + timedelta(days=i) for i in range(n)]
    group = days[7::spacing]
    positions = list(range(7, n, spacing))
    d = ar1(n, phi, mean, 5000 + rep)
    bench = {day: 10.0 for day in days}
    cand = {day: 10.0 - d[i] for i, day in enumerate(days)}
    kw = dict(block_length=sp.BLOCK_LENGTH, seed=SEED, replications=draws, level=0.90)
    intervals = {
        "current": s761.run_pairs({"B": bench}, cand, group, seed=SEED, draws=draws)["B"]["difference_interval"],
        "percentile": [domain_estimates({"g": (d, positions)}, n, **kw)["g"]["interval"][k] for k in ("lower", "upper")],
        "studentized": [studentized_domain_estimates({"g": (d, positions)}, n, **kw)["g"]["interval"][k] for k in ("lower", "upper")],
    }
    return {k: (lo <= mean, lo <= mean <= hi, hi - lo) for k, (lo, hi) in intervals.items()}


def coverage(reps: int = 1000, n: int = 1200, spacing: int = 60, mean: float = 0.4, phi: float = 0.6, draws: int = 400,
             workers: int = 4) -> dict:
    """The coverage of the three intervals on `reps` AR(1) series of `n` days with a known mean, the group every `spacing`th day."""

    jobs = [(rep, n, spacing, mean, phi, draws) for rep in range(reps)]
    with multiprocessing.get_context("fork").Pool(workers) as pool:
        done = pool.map(coverage_rep, jobs, chunksize=10)
    out = {"reps": reps, "series_days": n, "group_days": len(range(7, n, spacing)), "spacing": spacing, "known_mean": mean, "phi": phi,
           "draws": draws, "nominal_lower_bound": 0.95, "nominal_interval": 0.90, "intervals": {}}
    for k in KINDS:
        out["intervals"][k] = {"lower_bound_covers": sum(x[k][0] for x in done) / reps,
                               "interval_covers": sum(x[k][1] for x in done) / reps,
                               "mean_width": sum(x[k][2] for x in done) / reps}
    return out


def run_coverage(args) -> int:
    path = Path(args.score)
    result = json.loads(path.read_text(encoding="utf-8"))
    result["coverage"] = coverage(reps=args.reps, workers=args.workers)
    path.write_text(json.dumps(result, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    return 0


# -- the page --------------------------------------------------------------------------------------------------------


def _interval(row: dict) -> str:
    if "undefined" in row:
        return "undefined"
    lo, hi = row["difference_interval"]
    text = f"{row['difference']:+.3f} [{lo:+.3f}, {hi:+.3f}]"
    return text + (f" ({row['dropped_resamples']} of {row['draws']:,} dropped)" if "dropped_resamples" in row else "")


def _matrix(m: dict, a: str, b: str) -> List[str]:
    out = [f"| {NAME[a]} \\ {NAME[b]} | " + " | ".join(READINGS) + " |", "|---|" + "---|" * len(READINGS)]
    for x in READINGS:
        out.append(f"| {x} | " + " | ".join(str(m[x][y]) for y in READINGS) + " |")
    return out


def _row_table(rows: Sequence[dict]) -> List[str]:
    out = ["| metric | arm | vs | days | current: d [90%] | percentile domain | studentized domain | readings (cur / pct / stu) |",
           "|---|---|---|---|---|---|---|---|"]
    for r in rows:
        rd = r["readings"]
        flag = " *" if any(r["changes"].values()) else ""
        out.append(f"| {t.METRIC_TITLES[r['metric']].split(' (')[0]} | {SHORT[r['arm']]} | {SHORT[r['reference']]} | {r['days']} | "
                   f"{_interval(r['current'])} | {_interval(r['percentile'])} | {_interval(r['studentized'])} | "
                   f"{rd['current']} / {rd['percentile']} / {rd['studentized']}{flag} |")
    return out


def _quantiles(ratios: Sequence[float]) -> str:
    ratios = sorted(ratios)
    return (f"median {ratios[len(ratios) // 2]:.2f}, 10th percentile {ratios[len(ratios) // 10]:.2f}, "
            f"90th percentile {ratios[9 * len(ratios) // 10]:.2f}")


def render(r: dict) -> str:
    n = r["notes"]
    rows = r["rows"]
    cells = r["tally"]["current>percentile"]["cells"]
    out = [
        "# Day-type intervals on main: current, percentile domain and studentized domain (#1266)", "",
        "**Hypothesis and step:** H5 (primary goal), step 3 (reporting); H1 (the scorer). **Development data, not a verdict** (scoring "
        f"protocol v1, #640): days to {n['last_target']}, no lockbox day. No page's reading, no declaration, no group floor and no record "
        "in `docs/runs/` changes. Generated by `scripts/day_type_domain_1266.py page` from `docs/research/day-type-domain-1266/result.json`, "
        "not edited by hand. This is the re-run of #1228's measurement on main and the studentized domain interval of her ruling of "
        "27 October 2026 (ledger item 63 on #1116, option 1 on finding #1262). It supersedes `docs/research/day-type-domain-1228-result.md`, "
        "which stays as the record of what was run on a56d745d. Switching any page to a new interval is her decision, made after this page.", "",
        f"Panel digest `{r['panel_sha256'][:8]}…`. Settings are #1196's, declared in `{r['declaration']}`: seed {r['seed']}, "
        f"{r['draws']:,} draws, mean block {r['block_length']} business days, Newey-West lag {r['hac_lag']}, 90% two-sided interval "
        f"(the lower end is the one-sided 95% bound). Scored decision days {n['scored_decision_days']:,} ({n['first']} to {n['last']}); "
        f"the aligned target-day series has {r['target_days']:,} days.", "",
        "## The three intervals", "",
        "**Current.** The group's own days go to `scoring_protocol.paired_tests` (`run_pairs`): the days are sorted into one short series, "
        "blocks of mean length 10 are drawn over its positions, and the mean difference is studentized by a lag-10 HAC standard error on "
        "that short series. For quarter-ends, whose days are about three months apart, one block joins days years apart.", "",
        "**Percentile domain** (#1228). The whole aligned target-day series of `d = benchmark - candidate` is resampled with the same "
        "stationary bootstrap, block, seed and draws as the pooled test; the statistic is the mean of `d` over the resampled days that "
        "belong to the group; the interval is the 90% percentile interval of that statistic. Not studentized.", "",
        "**Studentized domain** (#1266). The same resamples and the same statistic. Each resample's group mean is divided by its own HAC "
        "standard error: with `I_t` the indicator that the day at position `t` of the resampled sequence is in the group, `K` the number "
        "of such days and `m` their mean, the series `u_t = I_t (d_t - m)` over all `n` positions has the Newey-West (Bartlett, lag "
        f"{r['hac_lag']}) long-run variance `V`, and the standard error is `sqrt(V / n) * n / K`. The bounds are the group mean less the "
        "95th and 5th percentiles of those t-draws times the same standard error on the original series, as the pooled rows are read. "
        "For a group of every day it is the pooled test's interval to rounding (pinned in `tests/test_studentized_domain_1266.py`). A "
        "resample that draws no day of a group would make the row unavailable, with the reason. A resample with no positive long-run "
        "variance (it drew too few group days to vary) is left out and counted, as #1239 does for the pooled test; the row says how many.", "",
        "The point estimate is the group mean in all three. A reading is taken from the bound on mean d for each (gain: lower end above 0; "
        "loss: upper end below 0), her #1009 ruling. Lens C's caveat (#958) applies to the current interval and is not removed by the domain ones.", "",
    ]
    if "reproduces_1243" in r:
        rep = r["reproduces_1243"]
        out += [f"**The current rows reproduce #1253's record.** {rep['identical_rows']} of the current rows below equal "
                f"`docs/research/s3-terms-1243/result.json` to the last digit; {rep['differing_rows']} differ"
                + (f" (first: {', '.join(rep['first_differing'])})." if rep["differing_rows"] else "."), ""]
    out += ["## Readings that change", "",
            f"Over every day-type row ({cells} cells: type, metric, arm, reference; types of {r['min_group_days']} days or more), rows of "
            "each table are the reading under the first interval and columns under the second."]
    for a, b in PAIRS:
        total = r["tally"][f"{a}>{b}"]
        title = {("current", "percentile"): "#1228's comparison, re-run on main",
                 ("current", "studentized"): "the studentized domain interval against the current one",
                 ("percentile", "studentized"): "the studentization alone (the same resamples)"}[(a, b)]
        out += ["", f"### {NAME[a]} against {NAME[b]}: {total['changed']} of {total['cells']} readings change ({title})", ""]
        out += _matrix(total["matrix"], a, b) + [""]
        for metric in r["metrics"]:
            by = r["tally_by_metric"][metric][f"{a}>{b}"]
            out.append(f"- {t.METRIC_TITLES[metric]}: {by['changed']} of {by['cells']} change.")
        out.append("")
    out += ["### By day type: readings that change", "",
            "| day type | days | cells | current > percentile | current > studentized | percentile > studentized |", "|---|---|---|---|---|---|"]
    days = {x["group"]: x["days"] for x in rows}
    for label, by in r["tally_by_group"].items():
        out.append(f"| {label} | {days[label]} | {by['current>percentile']['cells']} | " + " | ".join(
            str(by[f'{a}>{b}']['changed']) for a, b in PAIRS) + " |")
    out += ["", "### Width", ""]
    for other in ("current", "percentile"):
        ratios = [x[f"width_ratio_vs_{other}"] for x in rows if x[f"width_ratio_vs_{other}"] is not None]
        out.append(f"Width of the studentized domain interval over the {NAME[other]} one, over the {len(ratios)} cells with both: {_quantiles(ratios)}.")
        out.append("")
    ratios = [width(y["percentile"]) / width(y["current"]) for y in rows
              if width(y["percentile"]) is not None and width(y["current"])]
    if ratios:
        out += [f"Width of the percentile domain interval over the current one, over the {len(ratios)} cells with both: {_quantiles(ratios)}.", ""]
    dropped = r["dropped"]
    out += [f"Rows of the studentized domain interval read with resamples left out: {dropped['rows_with_dropped_resamples']}. "
            "Rows with no interval (`undefined`): " + ", ".join(f"{NAME[k]} {v}" for k, v in dropped["undefined_rows"].items()) + ".", ""]
    if "against_1228" in r:
        old = r["against_1228"]
        new = r["tally"]["current>percentile"]
        out += ["## How the re-run moves #1228's counts", "",
                f"#1228's page was scored at a56d745d, before the B2 thin-pool record (#1202) was in force: {old['scored_decision_days']:,} decision "
                f"days, the aligned target-day series of {old['target_days']:,} days, {old['changed']} of {old['cells']} readings changed under "
                f"percentile domain against current. On main, with {n['scored_decision_days']:,} decision days and {r['target_days']:,} target days: "
                f"{new['changed']} of {new['cells']}. The rows that read `no reading` under the current interval on that page now have a bound "
                "(the B2 thin-pool record, and #1239's bound where a resample has no variance).", "",
                "| day type | #1228's page | this page |", "|---|---|---|"]
        for label, by in r["tally_by_group"].items():
            out.append(f"| {label} | {old['by_group'].get(label, 'n/a')} | {by['current>percentile']['changed']} |")
        out.append("")
    if "coverage" in r:
        cov = r["coverage"]
        out += ["## Coverage on a synthetic series", "",
                f"{cov['reps']:,} AR(1) series (phi {cov['phi']}) of {cov['series_days']:,} days with known mean {cov['known_mean']}; the group is "
                f"every {cov['spacing']}th day ({cov['group_days']} days), so its days are far apart, as the quarter-ends are. {cov['draws']} "
                f"draws, mean block {r['block_length']}, seed {r['seed']}. The one-sided 95% lower bound should lie at or below the known mean "
                "in 95% of series, and the two-sided 90% interval should hold it in 90%.", "",
                "| interval | lower bound at or below the mean | 90% interval holds the mean | mean width |", "|---|---|---|---|"]
        for k in KINDS:
            v = cov["intervals"][k]
            out.append(f"| {NAME[k]} | {v['lower_bound_covers']:.3f} | {v['interval_covers']:.3f} | {v['mean_width']:.3f} |")
        out.append("")
    out += ["## The quarter-end and IORB-window rows", ""]
    for label in NAMED:
        if label not in r["tally_by_group"]:
            out += [f"`{label}`: below the floor of {r['min_group_days']} days; not reported.", ""]
            continue
        by = r["tally_by_group"][label]
        out += [f"`{label}` ({days[label]} days): " + "; ".join(
            f"{NAME[a]} against {NAME[b]}: {by[f'{a}>{b}']['changed']} of {by[f'{a}>{b}']['cells']} readings change" for a, b in PAIRS)
            + ". The rows are under 'Every day-type row'.", ""]
    moved = [x for x in rows if any(x["changes"].values())]
    out += ["## Every row whose reading changes", "",
            f"{len(moved)} of {len(rows)} rows read differently under at least one pair of intervals (`*` in the table below). "
            "The quarter-end and IORB-window rows are among them.", ""]
    out += _row_table(moved) + [""] if moved else ["None.", ""]
    out += ["## Every day-type row", "",
            "All rows, by type; `*` marks a row where some pair of readings differs. Intervals are mean d with the 90% interval "
            "(positive favours the arm).", ""]
    for label in dict.fromkeys(x["group"] for x in rows):
        sel = [x for x in rows if x["group"] == label]
        mark = " (named in the ruling)" if label in NAMED else ""
        out += [f"### {label} ({sel[0]['days']} days){mark}", ""] + _row_table(sel) + [""]
    out += [
        "## What this shows and does not show", "",
        "Development data on 2018-2025 for a choice of interval, not a verdict and not a result about the model. It measures how much the "
        "choice of interval moves the day-type readings; the synthetic series says how each interval covers a known mean when the group "
        "days are far apart, not which reading is true. No page is switched; that is her decision after this page. Not done: the same "
        "measurement on the other pages built on `run_pairs`; the regime rows (they are contiguous); a group floor (the floor stays 20 "
        "for reporting); skill intervals on the domain rows.", ""]
    return "\n".join(out)


def page(args) -> int:
    result = json.loads(Path(args.score).read_text(encoding="utf-8"))
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    Path(args.output).write_text(render(result), encoding="utf-8")
    return 0


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="command", required=True)
    s = sub.add_parser("score", help="re-score #1196's arms and compare the three day-type intervals")
    s.add_argument("--panel", required=True)
    s.add_argument("--output", required=True)
    s.add_argument("--draws", type=int, default=sp.DRAWS)
    s.add_argument("--workers", type=int, default=4)
    s.add_argument("--first", type=date.fromisoformat, default=None,
                   help="start the walk on this day (a subset, for the script's test only; the declared run omits it)")
    s.set_defaults(func=score)
    v = sub.add_parser("coverage", help="add the synthetic AR(1) coverage of the three intervals to a score file")
    v.add_argument("--score", required=True)
    v.add_argument("--reps", type=int, default=1000)
    v.add_argument("--workers", type=int, default=4)
    v.set_defaults(func=run_coverage)
    g = sub.add_parser("page", help="write the result page from a score file")
    g.add_argument("--score", required=True)
    g.add_argument("--output", required=True)
    g.set_defaults(func=page)
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
