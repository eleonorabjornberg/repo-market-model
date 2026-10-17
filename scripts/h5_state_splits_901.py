"""#634's walks scored by the as-of scarcity state of the decision day (#901, H5 step 3, milestones M2 and M4).

A scratch measurement, not a record: it fits no model, writes JSON and Markdown to the paths it is given and nothing into
`docs/runs/`, and changes no rule. Scoring protocol v1 section 7 asks for results "by the as-of scarcity state (public at
the time)"; #634's page and #758's page did not run that split (`docs/model/validation.md` section 4 lists it). This script
reads #634's walks unchanged (`scripts/spread_distribution_634.py walk`) and scores them as `scripts/h5_splits_805.py` does,
so every pooled figure reproduces the tracked page's, and adds:

1. each headline against B1 and B2 by the state of the decision day: ample (states 0 and 1) and scarce (2 and 3), the
   grouping ruled on #515 and applied as #706 and #850 apply it. The state is read at the decision instant
   (`richer_targets.as_of_rows`, lead 1: both guards run on every read), each leg at its own latest public row (#586). A
   day whose state is a hole is `unknown` and is reported, not dropped;
2. the same cuts without decision day 2019-09-18 (#798);
3. the paired per-day scores, so later splits need no new walk (`daily.json`).

The headlines are grid CRPS and upper-tail twCRPS of #634's four candidates, each against B1 and B2, and B3 (the published
declaration, on its own five levels, like for like against B1 and B2 read at the same five). Before any split is written the
pooled column is checked against the tracked figures of #634 and #805 (`check_pooled`); a column that differs stops the run.

No day after 2025-12-31 is read (`docs/decisions/lockbox.md`; `require_unlocked`). Development days give a score and an
interval, never a verdict (scoring protocol v1, #640). Intervals are the studentized stationary bootstrap's (block 10,
one-sided 95%), seed 634, the page being reproduced.

The walks take hours (#898): this goes to the Mac. PUBLISHED.csv, AUG2D.csv and the walks in OUT are built exactly as in the
docstring of scripts/spread_distribution_634.py. Scoring takes about 12 minutes.

    PYTHONPATH=src python3 scripts/h5_state_splits_901.py score --published PUBLISHED.csv --panel AUG2D.csv --walks OUT \\
        --output OUT/h5_state_splits_901.json --daily OUT/daily.json
    PYTHONPATH=src python3 scripts/h5_state_splits_901.py report --score OUT/h5_state_splits_901.json --output OUT/h5_state_splits_901.md
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import math
import sys
from datetime import date, time
from pathlib import Path
from typing import Dict, Iterable, List, Mapping, Optional, Sequence

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))

from repo_model import measurement_fields, richer_targets, scarcity, scoring_protocol as sp  # noqa: E402
from repo_model.data import DailyObservation, audit_panel, load_daily_panel  # noqa: E402
from repo_model.lockbox import require_unlocked  # noqa: E402

DECISION = time(16, 0)
LAST_TARGET = date(2025, 12, 31)
EXCLUDED_DAY = date(2019, 9, 18)
HORIZONS = sp.HORIZONS
STATES = ("ample", "scarce")
UNKNOWN = "unknown"
SEED = 634
MIN_GROUP_DAYS = 20
SCARCITY = scarcity.RESERVE_SCARCITY_STATE
TRACKED_805 = REPO / "docs" / "pivot" / "evidence" / "h5-splits-805" / "score.json"
TRACKED_634 = REPO / "docs" / "pivot" / "evidence" / "spread-distribution-protocol" / "score.json"
#: the fields a reproduced figure must match the tracked page's in.
REPRODUCED = ("n", "skill", "skill_lower_95_one_sided", "skill_upper_95_one_sided")


def _load(name: str):
    spec = importlib.util.spec_from_file_location(f"{name}_script", REPO / "scripts" / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[f"{name}_script"] = module
    spec.loader.exec_module(module)
    return module


# -- the state and the cuts (tested) -------------------------------------------------------------------------------------


def band(state: Optional[float]) -> str:
    """Ample for states 0 and 1, scarce for 2 and 3 (ruling on #515); a hole is `unknown`."""

    if state is None:
        return UNKNOWN
    return "ample" if state < 2 else "scarce"


def decision_states(
    rows: Sequence[DailyObservation],
    registry: Mapping[str, Mapping[str, object]],
    days: Sequence[date],
    position: Mapping[date, int],
    decision_time: time,
) -> Dict[date, str]:
    """The band of the scarcity state of each decision day, as public at that day's decision instant.

    The decision for day d is made at `decision_time` on d, so it is the decision for the scored row after d at lead 1:
    `richer_targets.as_of_rows` reads each leg at its own latest public row (#586) and both guards run on every read.

    Raises:
        LookAheadError: a day is in a locked tier, or a read is newer than the decision instant or staler than the latest
            public value.
    """

    require_unlocked(days, where="h5_state_splits_901")
    if not days:
        return {}
    scored = [position[d] + 1 for d in days]
    with scarcity.measurement_declaration():
        reads = richer_targets.as_of_rows(rows, registry, [SCARCITY], leads=(1,), scored=scored, decision_time=decision_time)
    return {d: band(rows[r].values.get(SCARCITY)) for d, r in zip(days, reads[1][SCARCITY])}


def drop_day(days: Iterable[date], day: date) -> List[date]:
    """`days` without `day`.

    Raises:
        ValueError: `day` is not among `days` (the cut would silently be the whole group).
    """

    kept = list(days)
    if day not in kept:
        raise ValueError(f"{day} is not among the {len(kept)} days it is to be dropped from")
    return [d for d in kept if d != day]


def state_cuts(days: Sequence[date], states: Mapping[date, str]) -> Dict[str, List[date]]:
    """pooled; without the excluded day; each state; each state without the excluded day (where it holds that day)."""

    out = {"pooled": list(days), "without_2019-09-18": drop_day(days, EXCLUDED_DAY)}
    labels = [*STATES, UNKNOWN]
    for label in labels:
        members = [d for d in sorted(days) if states[d] == label]
        if not members:
            continue
        out[f"state:{label}"] = members
        if EXCLUDED_DAY in members:
            out[f"state:{label} without_2019-09-18"] = drop_day(members, EXCLUDED_DAY)
    return out


def check_pooled(computed: Mapping[str, Mapping[str, float]], tracked: Mapping[str, Mapping[str, float]]) -> None:
    """The pooled column must be the tracked page's before any split is written.

    Raises:
        ValueError: a pair the tracked page lacks, or a figure that differs from it.
    """

    for pair, entry in computed.items():
        if pair not in tracked:
            raise ValueError(f"the tracked page has no pooled figure for {pair}")
        for field in REPRODUCED:
            if field not in tracked[pair]:
                continue
            if not math.isclose(float(entry[field]), float(tracked[pair][field]), rel_tol=1e-9, abs_tol=1e-12):
                raise ValueError(f"{pair}: pooled {field} {entry[field]} is not the tracked {tracked[pair][field]}")


# -- the scores ----------------------------------------------------------------------------------------------------------


def mean_of(series: Mapping[date, float], group: Sequence[date]) -> Optional[float]:
    return sum(series[d] for d in group) / len(group) if group else None


def score_command(args) -> int:
    h805 = _load("h5_splits_805")
    h707 = _load("h5_step3_707")
    ctx = h805.prepare(args.published, args.walks)
    sd = ctx["sd"]
    calendar, outcomes, common, b1, b2 = ctx["calendar"], ctx["outcomes"], ctx["common"], ctx["b1"], ctx["forecasts"]["B2"]
    forecasts = ctx["forecasts"]
    draws = args.draws

    def score_all(fc, score=sp.grid_crps):
        return sp.day_scores(fc, outcomes, calendar, score=score)

    names = ["B1", "B2", *h805.CANDIDATES]
    grid = {n: score_all(forecasts[n]) for n in names}
    tail = {n: score_all(forecasts[n], sp.upper_tail_twcrps) for n in names}
    days = sorted(grid["B1"])
    # B3, the published declaration, on its own five levels; a missing lead takes B1's, read at the same five
    published = sd.load_laws(args.walks, "published", native=True)
    decisions, _ = sd.lead_forecasts(published, calendar)
    five_b1 = {d: {h: sd.five_levels(b1[d][h]) for h in HORIZONS} for d in days}
    filled = sp.fill_missing({d: decisions[d] for d in days}, five_b1, days)
    five = {n: {d: {h: sd.five_levels(forecasts[n][d][h]) for h in HORIZONS} for d in days} for n in ("B1", "B2")}
    five["B3"] = {d: {h: sd.five_levels(leads[h]) for h in HORIZONS} for d, leads in filled.forecasts.items()}
    five_crps = {n: score_all(five[n], sd.five_crps) for n in five}
    five_tw = {n: score_all(five[n], sd.five_twcrps) for n in five}
    for table in (grid, tail, five_crps, five_tw):
        for n, scores in table.items():
            if sorted(scores) != days:
                raise SystemExit(f"{n} does not score the same decision days as B1")

    scratch = load_daily_panel(args.panel)
    audit_panel(scratch)
    position = {row.date: i for i, row in enumerate(scratch)}
    for d in days:
        if d not in position:
            raise ValueError(f"decision day {d} is not a row of {args.panel}")
    states = decision_states(scratch, measurement_fields.load_registry(), days, position, DECISION)
    cuts = state_cuts(days, states)

    measures = {
        "grid_crps": (grid, ("B1", "B2"), h805.CANDIDATES),
        "upper_tail_twcrps": (tail, ("B1", "B2"), h805.CANDIDATES),
        "b3_five_levels_crps": (five_crps, ("B1", "B2"), ("B3",)),
        "b3_five_levels_twcrps": (five_tw, ("B1", "B2"), ("B3",)),
    }
    sd.SEED = SEED

    def headline(scores, benchmarks, candidate):
        out = {}
        for label, group in cuts.items():
            if len(group) < MIN_GROUP_DAYS:
                out[label] = {"days": len(group), "note": f"fewer than {MIN_GROUP_DAYS} days; not tested"}
                continue
            out[label] = {
                "days": len(group),
                "benchmark_mean": {b: mean_of(scores[b], group) for b in benchmarks},
                "candidate_mean": mean_of(scores[candidate], group),
                "tests": h805.skill_table(sd, h707, scores, benchmarks, candidate, group, draws),
            }
        return out

    headlines = {
        measure: {c: headline(scores, benchmarks, c) for c in candidates}
        for measure, (scores, benchmarks, candidates) in measures.items()
    }

    # the pooled column is the tracked page's before anything is split
    t805 = json.loads(TRACKED_805.read_text(encoding="utf-8"))
    t634 = json.loads(TRACKED_634.read_text(encoding="utf-8"))
    for measure, tracked in (("grid_crps", "pooled_primary"), ("upper_tail_twcrps", "pooled_key_secondary")):
        pooled = {}
        for c in h805.CANDIDATES:
            pooled.update(headlines[measure][c]["pooled"]["tests"])
        check_pooled(pooled, t634[tracked])
        check_pooled(
            pooled,
            {k: v for c in h805.CANDIDATES for k, v in t805["headlines"][measure][c]["pooled"]["tests"].items()},
        )
    for measure, tracked in (("b3_five_levels_crps", "pooled_primary_five"), ("b3_five_levels_twcrps", "pooled_key_secondary_five")):
        check_pooled(headlines[measure]["B3"]["pooled"]["tests"], t634[tracked])

    counts = {label: len(group) for label, group in cuts.items()}
    document = {
        "panel_sha256": sd.panel_sha256(args.published),
        "scratch_panel_sha256": sd.panel_sha256(args.panel),
        "decision_days": {"n": len(days), "first": days[0].isoformat(), "last": days[-1].isoformat()},
        "draws": draws,
        "seed": SEED,
        "excluded_day": EXCLUDED_DAY.isoformat(),
        "min_group_days": MIN_GROUP_DAYS,
        "state_days": counts,
        "pooled_reproduces": ["docs/pivot/evidence/spread-distribution-protocol/score.json", "docs/pivot/evidence/h5-splits-805/score.json"],
        "headlines": headlines,
    }
    args.output.write_text(json.dumps(document, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    daily = {
        "panel_sha256": document["panel_sha256"],
        "decision_days": [d.isoformat() for d in days],
        "state": {d.isoformat(): states[d] for d in days},
        "grid_crps": {n: {d.isoformat(): grid[n][d] for d in days} for n in names},
        "upper_tail_twcrps": {n: {d.isoformat(): tail[n][d] for d in days} for n in names},
        "b3_five_levels_crps": {n: {d.isoformat(): five_crps[n][d] for d in days} for n in five_crps},
        "b3_five_levels_twcrps": {n: {d.isoformat(): five_tw[n][d] for d in days} for n in five_tw},
    }
    args.daily.write_text(json.dumps(daily, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(args.output), "daily": str(args.daily), "decision_days": len(days), "state_days": counts}))
    return 0


# -- the report ----------------------------------------------------------------------------------------------------------


def _cell(entry: Optional[dict]) -> str:
    if not entry:
        return "n/a"
    if entry.get("identical"):
        return "0.0% (identical forecasts)"
    return f"{entry['skill'] * 100:+.1f}% [{entry['skill_lower_95_one_sided'] * 100:+.1f}%, {entry['skill_upper_95_one_sided'] * 100:+.1f}%]"


def _table(block: Mapping[str, dict], candidate: str, benchmark: str) -> List[str]:
    lines = ["| cut | days | skill against " + benchmark + " |", "|---|---|---|"]
    for label, row in block.items():
        test = row.get("tests", {}).get(f"{benchmark} -> {candidate}")
        lines.append(f"| {label} | {row['days']} | {_cell(test) if test else row.get('note', 'n/a')} |")
    return lines


TITLES = {
    "grid_crps": "Grid CRPS (the primary score)",
    "upper_tail_twcrps": "Upper-tail twCRPS (weight 1{y > 0 bp})",
    "b3_five_levels_crps": "B3 on its own five levels, CRPS (B1 and B2 read at the same five)",
    "b3_five_levels_twcrps": "B3 on its own five levels, twCRPS",
}


def report_command(args) -> int:
    document = json.loads(args.score.read_text(encoding="utf-8"))
    out = [
        "# H5 headlines by the as-of scarcity state of the decision day (#901)",
        "",
        f"Decision days {document['decision_days']['first']} to {document['decision_days']['last']} (n = {document['decision_days']['n']}); "
        f"studentized stationary bootstrap, {document['draws']} draws, one-sided 95%, seed {document['seed']}; panel "
        f"`{document['panel_sha256'][:8]}…`. Development data, not a verdict.",
        "",
        "State: ample is states 0 and 1, scarce is 2 and 3 (ruling on #515), public at the decision instant, each leg at its own latest public row. "
        "Decision days by cut: " + ", ".join(f"{k} {v}" for k, v in document["state_days"].items()) + ".",
        "",
        "The pooled column reproduces the tracked figures of #634 and #805 to the digit (checked by the script before it wrote anything).",
        "",
    ]
    for measure, title in TITLES.items():
        out += [f"## {title}", ""]
        for candidate, block in document["headlines"][measure].items():
            for benchmark in ("B1", "B2"):
                out += [f"### {candidate} against {benchmark}", "", *_table(block, candidate, benchmark), ""]
    args.output.write_text("\n".join(out) + "\n", encoding="utf-8")
    return 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="command", required=True)
    score = sub.add_parser("score", help="score the walks by the state")
    score.add_argument("--published", type=Path, required=True)
    score.add_argument("--panel", type=Path, required=True, help="the scratch panel (AUG2D.csv) that carries reserve_scarcity_state")
    score.add_argument("--walks", type=Path, required=True)
    score.add_argument("--output", type=Path, required=True)
    score.add_argument("--daily", type=Path, required=True)
    score.add_argument("--draws", type=int, default=10_000)
    score.set_defaults(func=score_command)
    report = sub.add_parser("report", help="write the tables")
    report.add_argument("--score", type=Path, required=True)
    report.add_argument("--output", type=Path, required=True)
    report.set_defaults(func=report_command)
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
