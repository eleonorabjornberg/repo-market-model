"""Day-type intervals as domain estimates, measured beside the current ones on #1196 (#1228; H5 step 3 reporting; H1 scorer).

A development study, never a verdict. It changes no page's reading, no declaration and nothing in `docs/runs/`; it writes JSON and
Markdown to the paths it is given. Finding #1221: the H5 pages test a pressure-day type by passing the type's own days to
`spread_mr_variants_761.run_pairs`, which sorts them into one short series and draws blocks of mean length 10 over its positions, so
a block joins days that are months apart (quarter-ends are about three months apart). `repo_model.evaluation_splits` says to resample
the whole aligned series and take the mean over the resampled days that belong to the group. Her ruling (26 October 2026, ledger item
54 on #1221, option 1): measure the two beside each other on #1196; the switch is a follow-up directive.

What it does, with #1196's declared settings (`metadata/s3_terms_1196.json`, seed 1196, 10,000 draws, mean block 10, the published
panel): re-scores the arms of #1196 (the walks are the same code), then for every target-day-type row, on grid CRPS and on
upper-tail twCRPS, against B1, B1', B2, (a) and (s3) (the references of `s3_terms_1196.pair_plan`), computes

* the current row: `run_pairs` on the group's days, the studentized interval on mean d (the mean-d fallback of #1215), and
* the domain row: `spread_mr_variants_761.run_domain`, the whole aligned target-day series of `d = benchmark - candidate` resampled
  with the pooled test's block, seed and draw count, the statistic the mean of `d` over the resampled days of the group, the 90%
  percentile interval (its lower end is the one-sided 95% bound).

The two differ in two ways at once: the resampling frame, and that the domain interval is a percentile interval and not studentized
(a studentized domain statistic would need a HAC standard error of the group's mean over the resample, which no module here has; it is
not built). The page says so. It counts the readings (gain, loss, undecided, no reading) that change and names the quarter-end and
IORB-window rows. Floors are not touched: a group of 20 days or more is reported, as on every page.

The current rows are also compared with `docs/research/s3-terms-1196/result.json`: the re-score reproduces them or the run says
which differ.

Commands, from a clone of the branch (the walks take minutes, the tests about half an hour on 4 cores: a cloud run):

    PYTHONPATH=src python3 -m repo_model.cli build --raw-root tests/fixtures/snapshots/funding_inputs \\
        --output PUB.csv --build-cutoff 2026-09-08T21:31:42+00:00 --decision-time 16:00:00
    PYTHONPATH=src python3 -m repo_model.cli verify-panel PUB.csv --manifest metadata/funding_panel_manifest.json
    PYTHONPATH=src python3 scripts/day_type_domain_1228.py score --panel PUB.csv \\
        --output docs/research/day-type-domain-1228/result.json
    PYTHONPATH=src python3 scripts/day_type_domain_1228.py page \\
        --score docs/research/day-type-domain-1228/result.json --output docs/research/day-type-domain-1228-result.md

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
    spec = importlib.util.spec_from_file_location(name, REPO / "scripts" / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


from repo_model import announced_iorb, scoring_protocol as sp  # noqa: E402
from repo_model import spread_mr_calendar as cal  # noqa: E402
from repo_model.baseline import panel_sha256  # noqa: E402
from repo_model.data import load_daily_panel  # noqa: E402
from repo_model.evaluation_splits import load_split_declaration  # noqa: E402

t = _load("s3_terms_1196")
c, s761 = t.c, t.s761

ISSUE = 1228
SEED = t.SEED
COMMITTED = REPO / "docs" / "research" / "s3-terms-1196" / "result.json"
METRICS = t.METRIC_NAMES
ARMS = t.ARMS
#: The day-type rows: the target-day-type split of #1196 (overlapping types, ordinary, and the calendar days together).
SPLIT = "target_day_type"
#: The rows the ruling names.
NAMED = ("quarter_end", "iorb_window")
#: Short names for the tables: the arms and references of #1196.
SHORT = {"B1": "B1", t.B1P: "B1′", "B2": "B2", t.A: "(a)", t.S3: "(s3)", t.S3S: "(s3+state)", t.S3C: "(s3+FOMC/IORB)"}
READINGS = ("gain", "undecided", "loss", "no reading")

_STATE: Dict = {}


def reading(row: Optional[dict]) -> str:
    """gain, loss, undecided or no reading, on the bound on mean d (her #1009 ruling), as every page reads a row."""

    word = t.verdict(row)
    return "no reading" if word.startswith("**no reading") else word


def width(row: Optional[dict]) -> Optional[float]:
    if row is None or "undefined" in row:
        return None
    lo, hi = row["difference_interval"]
    return hi - lo


def compare(current: Optional[dict], domain: Optional[dict]) -> dict:
    """One cell of the comparison: both readings, whether it changes, the widths and the shift of the lower bound."""

    a, b = reading(current), reading(domain)
    wa, wb = width(current), width(domain)
    out = {"current_reading": a, "domain_reading": b, "changes": a != b,
           "width_ratio": None if wa is None or wb is None or wa == 0.0 else wb / wa}
    if wa is not None and wb is not None:
        out["lower_shift"] = domain["difference_interval"][0] - current["difference_interval"][0]
    return out


def tally(cells: Sequence[dict]) -> dict:
    """Counts of the cells by (current reading, domain reading), and how many change."""

    matrix: Dict[str, Dict[str, int]] = {a: {b: 0 for b in READINGS} for a in READINGS}
    for cell in cells:
        matrix[cell["current_reading"]][cell["domain_reading"]] += 1
    return {"cells": len(cells), "changed": sum(1 for cell in cells if cell["changes"]), "matrix": matrix}


def _current_task(job):
    label, metric, candidate, members = job
    series = _STATE["series"][("target", metric)]
    out = {}
    for name in t.pair_plan(candidate, ()):
        out[name] = s761.run_pairs({name: series[name]}, series[candidate], list(members), seed=SEED, draws=_STATE["draws"],
                                   mean_d_fallback=True)[name]
    return (label, metric, candidate), out


def _domain_task(job):
    metric, cells = job
    series = _STATE["series"][("target", metric)]
    all_days = sorted(series["B1"])
    request = {}
    for label, candidate, members in cells:
        for name in t.pair_plan(candidate, ()):
            request[(label, candidate, name)] = (series[name], series[candidate], members)
    rows = s761.domain_rows(request, all_days, seed=SEED, draws=_STATE["draws"])
    out: Dict = {}
    for (label, candidate, name), row in rows.items():
        out.setdefault((label, metric, candidate), {})[name] = row
    return out


def _dispatch(job):
    kind, payload = job
    return kind, (_current_task(payload) if kind == "current" else _domain_task(payload))


def run_jobs(jobs, workers: int):
    with multiprocessing.get_context("fork").Pool(workers) as pool:
        return pool.map(_dispatch, jobs, chunksize=1)


def reproduction(current: Mapping, committed: Mapping) -> dict:
    """Which rows of the re-score differ from `docs/research/s3-terms-1196/result.json`, to the last digit."""

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
    frame, notes, mine = t.build_frame(panel, splits, registry, table, states, args.first)
    published_sha = panel_sha256(panel_path)
    labels = c.day_labels(frame, table)
    cells = {m: t.cell_table(frame, frame.forecasts[m]) for m in t.MODELS}
    series = {("target", metric): {m: c.series_of(frame, cells[m][metric], "target") for m in t.MODELS} for metric in METRICS}
    _STATE.update(series=series, draws=args.draws)

    groups = [(label, tuple(sorted(members))) for split, label, _grain, members in c.groups_of(frame, labels) if split == SPLIT]
    skipped = {label: len(members) for label, members in groups if len(members) < t.MIN_GROUP_DAYS}
    groups = [(label, members) for label, members in groups if len(members) >= t.MIN_GROUP_DAYS]
    jobs = [("current", (label, metric, candidate, members)) for label, members in groups for metric in METRICS for candidate in ARMS]
    jobs += [("domain", (metric, [(label, candidate, members) for label, members in groups for candidate in ARMS])) for metric in METRICS]
    done = run_jobs(jobs, args.workers)

    current: Dict = {}
    domain: Dict = {}
    for kind, payload in done:
        if kind == "current":
            current[payload[0]] = payload[1]
        else:
            domain.update(payload)
    result: dict = {
        "issue": ISSUE, "label": "development, not a verdict", "panel_sha256": published_sha, "seed": SEED, "draws": args.draws,
        "block_length": sp.BLOCK_LENGTH, "level": 0.90, "declaration": str(t.DECLARATION.relative_to(REPO)),
        "reading_rules": declaration["reading_rules"], "notes": notes, "split": SPLIT, "metrics": list(METRICS),
        "arms": list(ARMS), "min_group_days": t.MIN_GROUP_DAYS, "skipped_groups": skipped,
        "target_days": len(series[("target", METRICS[0])]["B1"]), "rows": [],
    }
    for label, members in groups:
        for metric in METRICS:
            for candidate in ARMS:
                now, new = current[(label, metric, candidate)], domain[(label, metric, candidate)]
                for name in t.pair_plan(candidate, ()):
                    result["rows"].append({"group": label, "days": len(members), "metric": metric, "arm": candidate, "reference": name,
                                           "current": now[name], "domain": new[name], **compare(now[name], new[name])})
    result["tally"] = tally(result["rows"])
    result["tally_by_metric"] = {m: tally([r for r in result["rows"] if r["metric"] == m]) for m in METRICS}
    result["tally_by_group"] = {label: tally([r for r in result["rows"] if r["group"] == label]) for label, _ in groups}
    if args.first is None and COMMITTED.exists():
        result["reproduces_1196"] = reproduction(current, json.loads(COMMITTED.read_text(encoding="utf-8")))
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    Path(args.output).write_text(json.dumps(result, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    return 0


# -- the page --------------------------------------------------------------------------------------------------------


def _interval(row: dict) -> str:
    if "undefined" in row:
        return "undefined"
    lo, hi = row["difference_interval"]
    return f"{row['difference']:+.3f} [{lo:+.3f}, {hi:+.3f}]"


def _matrix(m: dict) -> List[str]:
    out = ["| current \\ domain | " + " | ".join(READINGS) + " |", "|---|" + "---|" * len(READINGS)]
    for a in READINGS:
        out.append(f"| {a} | " + " | ".join(str(m[a][b]) for b in READINGS) + " |")
    return out


def _row_table(rows: Sequence[dict]) -> List[str]:
    out = ["| metric | arm | vs | days | current: d [90%] | reading | domain: d [90%] | reading | changes |", "|---|---|---|---|---|---|---|---|---|"]
    for r in rows:
        out.append(f"| {t.METRIC_TITLES[r['metric']].split(' (')[0]} | {SHORT[r['arm']]} | "
                   f"{SHORT[r['reference']]} | {r['days']} | {_interval(r['current'])} | {r['current_reading']} | "
                   f"{_interval(r['domain'])} | {r['domain_reading']} | {'yes' if r['changes'] else ''} |")
    return out


def render(r: dict) -> str:
    n = r["notes"]
    rows = r["rows"]
    total = r["tally"]
    out = [
        "# Day-type intervals as domain estimates, beside the current ones, on #1196 (#1228)", "",
        "**Hypothesis and step:** H5 (primary goal), step 3 (reporting); H1 (the scorer). **Development data, not a verdict** (scoring "
        f"protocol v1, #640): days to {n['last_target']}, no lockbox day. No page's reading, no declaration and no record in `docs/runs/` "
        "changes, and no group floor changes. Generated by `scripts/day_type_domain_1228.py page` from "
        "`docs/research/day-type-domain-1228/result.json`, not edited by hand. This is the measurement step of her ruling of 26 October "
        "2026 (ledger item 54 on #1221, option 1); switching the pages to the domain interval is a follow-up directive.", "",
        f"Panel digest `{r['panel_sha256'][:8]}…`. Settings are #1196's, declared in `{r['declaration']}`: seed {r['seed']}, "
        f"{r['draws']:,} draws, mean block {r['block_length']} business days, 90% two-sided interval (the lower end is the one-sided "
        f"95% bound). Scored decision days {n['scored_decision_days']:,} ({n['first']} to {n['last']}); the aligned target-day series "
        f"has {r['target_days']:,} days.", "",
        "## The two intervals", "",
        "**Current.** The group's own days go to `scoring_protocol.paired_tests` (`run_pairs`): the days are sorted into one short series, "
        "blocks of mean length 10 are drawn over its positions, and the mean difference is studentized by a lag-10 HAC standard error on "
        "that short series. For quarter-ends, whose days are about three months apart, one block joins days years apart.", "",
        "**Domain.** The whole aligned target-day series of `d = benchmark - candidate` is resampled with the same stationary bootstrap, "
        "block, seed and draws as the pooled test (`domain_intervals.domain_estimates`); the statistic is the mean of `d` over the "
        "resampled days that belong to the group; the interval is the 90% percentile interval of that statistic. The point estimate "
        "is the group mean in both. A resample that draws no day of a group would make the row unavailable, with the reason; none did "
        "here unless a row below says `undefined`.", "",
        "**Two things differ at once.** The domain interval is a percentile interval and is not studentized, because no module here "
        "studentizes a domain statistic (it would need a HAC standard error of the group's mean over the resample). So a change "
        "below is the resampling frame and the studentization together; this page does not separate them. A reading is taken from "
        "the bound on mean d for both (gain: lower end above 0; loss: upper end below 0), her #1009 ruling. Lens C's caveat (#958) "
        "applies to the current interval and is not removed by the domain one.", "",
    ]
    if "reproduces_1196" in r:
        rep = r["reproduces_1196"]
        out += [f"**The re-score reproduces #1196.** {rep['identical_rows']} of the current rows below equal `docs/research/s3-terms-1196/result.json` "
                f"to the last digit; {rep['differing_rows']} differ" + (f" (first: {', '.join(rep['first_differing'])})." if rep["differing_rows"] else "."), ""]
    out += [f"## Readings that change", "",
            f"Over every day-type row ({total['cells']} cells: type, metric, arm, reference; types of {r['min_group_days']} days or more), "
            f"{total['changed']} readings change. Rows are (current reading, domain reading).", ""]
    out += _matrix(total["matrix"]) + [""]
    for metric in r["metrics"]:
        by = r["tally_by_metric"][metric]
        out += [f"**{t.METRIC_TITLES[metric]}:** {by['changed']} of {by['cells']} change.", ""]
        out += _matrix(by["matrix"]) + [""]
    out += ["By day type:", "", "| day type | days | cells | change |", "|---|---|---|---|"]
    days = {x["group"]: x["days"] for x in r["rows"]}
    for label, by in r["tally_by_group"].items():
        out.append(f"| {label} | {days[label]} | {by['cells']} | {by['changed']} |")
    ratios = sorted(x["width_ratio"] for x in r["rows"] if x["width_ratio"] is not None)
    if ratios:
        out += ["", f"Width of the domain interval over the current one, over the {len(ratios)} cells with both: median "
                f"{ratios[len(ratios) // 2]:.2f}, 10th percentile {ratios[len(ratios) // 10]:.2f}, 90th percentile {ratios[9 * len(ratios) // 10]:.2f}."]
    changed = [x for x in rows if x["changes"] and x["group"] not in NAMED]
    out += ["", "## The quarter-end and IORB-window rows", ""]
    for label in NAMED:
        sel = [x for x in rows if x["group"] == label]
        if not sel:
            out += [f"`{label}`: below the floor of {r['min_group_days']} days; not reported.", ""]
            continue
        by = r["tally_by_group"][label]
        out += [f"### {label} ({sel[0]['days']} days): {by['changed']} of {by['cells']} readings change", ""]
        out += _row_table(sel) + [""]
    out += ["## Every other row whose reading changes", ""]
    out += (_row_table(changed) if changed else ["None."]) + [""]
    out += [
        "## What this shows and does not show", "",
        "Development data on 2018-2025 for a choice of interval, not a verdict and not a result about the model. It measures how much the "
        "choice of interval moves the day-type readings of #1196; it does not say which interval is right (the simulation in "
        "`tests/test_domain_intervals_1228.py` measures coverage on an AR(1) series with group days 60 apart, beside the current one). Every "
        "row, not only the changed ones, is in `result.json`. Not done: a studentized domain statistic; the same measurement on the other "
        "pages built on `run_pairs` (#1182 and about twenty more); the regime rows (they are contiguous); the minimum group size (the floor "
        "stays 20 for reporting; groups under 60 days are labelled thin in the follow-up, her ruling).", ""]
    return "\n".join(out)


def page(args) -> int:
    result = json.loads(Path(args.score).read_text(encoding="utf-8"))
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    Path(args.output).write_text(render(result), encoding="utf-8")
    return 0


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="command", required=True)
    s = sub.add_parser("score", help="re-score #1196's arms and compare the day-type intervals")
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
