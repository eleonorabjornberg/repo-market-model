"""The calendar-aware models scored by the as-of scarcity state of the decision day (#901, H5 step 3, M2 and M4).

A scratch measurement, not a record: it fits no model, writes JSON and Markdown to the paths it is given and nothing into
`docs/runs/`, and changes no rule. Scoring protocol v1 section 7 asks for results "by the as-of scarcity state (public at
the time)"; #634's page and #758's page did not run that split (`docs/model/validation.md` section 4 lists it). This script
reads the walks unchanged and scores them as `scripts/h5_splits_805.py` does, so the pooled figure of `gbm_funding` reproduces the
tracked pages', and adds:

1. each headline against B1, B2 and B1' by the state of the decision day: ample (states 0 and 1) and scarce (2 and 3), the
   grouping ruled on #515 and applied as #706 and #850 apply it. The state is read at the decision instant
   (`richer_targets.as_of_rows`, lead 1: both guards run on every read), each leg at its own latest public row (#586). A
   day whose state is a hole is `unknown` and is reported, not dropped;
2. the same cuts without decision day 2019-09-18 (#798);
3. the paired per-day scores, so later splits need no new walk (`daily.json`).

Narrowed by Eleonora's ruling of 22 October 2026 on #901 (https://github.com/eleonorabjornberg/repo-market-model/issues/901#issuecomment-6343345137):
the calendar-aware models only. The candidates are `gbm_funding` (#634's walk, the control) and #1027's two variants,
`gbm_funding_cal_aligned` and `gbm_funding_cal_direct` (`scripts/aligned_calendar_1027.py`, declared and walked there; no new variant here),
each against B1, B2 and B1'. #634's `a_published_new`, `b_gbm_new` and `c_two_part_new` and B3 (the published declaration) are dropped, not
re-walked: they stay provisional under `docs/research/provisional-calendar-register.md` and the #947 guard refuses their walks. Which variant
replaces `gbm_funding` is Eleonora's decision (ruling of 21 October 2026: keep `gbm_funding` for now), so every one is reported.
`gbm_funding` is provisional (calendar not read at the target day); the page says so.

The decision days are those `gbm_funding`'s walk and the benchmarks cover (`h5_splits_805.prepare`, narrowed to that walk); B1' is absent on some days
(`b1_calendar` raises `ProtocolError`), so the columns against B1' are on the days that have it, with their own day counts, and B1' is never
filled with B1. The pooled column of `gbm_funding` against B1 and B2, for grid CRPS and upper-tail twCRPS, is checked against the tracked figures
of #634 and #805 (`check_pooled`); a column that differs stops the run before anything is written. The variants are new, so their pooled
column is not a reproduction of anything, and the page says so.

No day after 2025-12-31 is read (`docs/decisions/lockbox.md`; `require_unlocked`). Development days give a score and an
interval, never a verdict (scoring protocol v1, #640). Intervals are the studentized stationary bootstrap's (block 10,
one-sided 95%), seed 634, the page being reproduced.

The walks take hours (#898): this goes to the Mac. PUBLISHED.csv and AUG3.csv (#951's scratch panel, which carries
`reserve_scarcity_state`) and the three models' walks in OUT are built as in the docstring of scripts/aligned_calendar_1027.py. Walks #1027
left on the Mac are reused (`finished_walk` skips a walk already written from the same panel bytes). Scoring takes about 12 minutes.

    PYTHONPATH=src python3 scripts/h5_state_splits_901.py score --published PUBLISHED.csv --panel AUG3.csv --walks OUT \\
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
#: the narrowed set (ruling of 22 October 2026): the control and #1027's two variants. B1' is `b1_calendar_960.B1P`.
CONTROL = "gbm_funding"
VARIANTS = ("gbm_funding_cal_aligned", "gbm_funding_cal_direct")
WALKS_NEEDED = (CONTROL, *VARIANTS)
DROPPED = ("a_published_new", "b_gbm_new", "c_two_part_new", "B3")
B1P = "B1_prime"
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


def variant_forecasts(
    name: str,
    decisions: Mapping[date, Mapping[int, Sequence[float]]],
    b1: Mapping[date, Mapping[int, Sequence[float]]],
    common: Sequence[date],
) -> Dict[date, Dict[int, Sequence[float]]]:
    """A #1027 variant's forecast on #634's decision days, a missing lead standing in as B1 (as #634 fills a candidate).

    Raises:
        ValueError: the variant's walks do not cover a decision day of #634's common set (the pooled days would differ).
    """

    missing = [d for d in common if d not in decisions]
    if missing:
        raise ValueError(f"{name} has no walk for {len(missing)} of #634's decision days, the first {missing[0]}")
    return sp.fill_missing({d: decisions[d] for d in common}, b1, list(common)).forecasts


def b1_prime_forecasts(forecast, days: Sequence[date]):
    """B1' on each of `days` it exists on, and the days it does not exist on (a `ProtocolError`; never filled with B1).

    `forecast(day)` is B1' for that decision day. Any other error is raised.
    """

    out, missing = {}, []
    for day in days:
        try:
            out[day] = forecast(day)
        except sp.ProtocolError:
            missing.append(day)
    return out, missing


def reproducible(pooled: Mapping[str, Mapping[str, float]]) -> Dict[str, Mapping[str, float]]:
    """The pooled pairs a tracked page holds: those of the control. The variants are new; there is nothing to reproduce."""

    return {pair: entry for pair, entry in pooled.items() if pair.endswith(f" -> {CONTROL}")}


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


def narrowed_prepare(h805, published: Path, walks: Path):
    """`h805.prepare` on `gbm_funding`'s walk alone: #634's other walks are dropped (ruling of 22 October 2026), so they are neither read nor required."""

    saved = h805.WALKS, h805.CANDIDATES
    h805.WALKS, h805.CANDIDATES = (CONTROL,), (CONTROL,)
    try:
        return h805.prepare(published, walks)
    finally:
        h805.WALKS, h805.CANDIDATES = saved


def score_command(args) -> int:
    h805 = _load("h5_splits_805")
    h707 = _load("h5_step3_707")
    a1027 = _load("aligned_calendar_1027")
    ctx = narrowed_prepare(h805, args.published, args.walks)
    sd = ctx["sd"]
    calendar, outcomes, common, b1, b2 = ctx["calendar"], ctx["outcomes"], ctx["common"], ctx["b1"], ctx["forecasts"]["B2"]
    forecasts = ctx["forecasts"]
    draws = args.draws

    def score_all(fc, score=sp.grid_crps):
        return sp.day_scores(fc, outcomes, calendar, score=score)

    scratch = load_daily_panel(args.panel)
    audit_panel(scratch)
    variants, not_run = a1027.scored_variants(args.walks)
    for variant in variants:
        for h in HORIZONS:
            walked = json.loads((args.walks / f"{variant}_h{h}.json").read_text(encoding="utf-8"))
            if walked.get("scratch_panel_sha256") != sd.panel_sha256(args.panel):
                raise ValueError(f"{variant}_h{h}.json was walked from scratch panel {walked.get('scratch_panel_sha256')}, not {sd.panel_sha256(args.panel)}")
        walk = sd.load_laws(args.walks, variant)
        decisions_v, _ = sd.lead_forecasts(walk, calendar)
        forecasts[variant] = variant_forecasts(variant, decisions_v, b1, common)
    candidates = (CONTROL, *variants)
    # B1': the calendar-aware persistence of #960, on the decision days that have it
    b960 = _load("b1_calendar_960")
    pub_rows, position_p, splits, registry = ctx["rows"], ctx["position"], ctx["splits"], ctx["registry"]
    b1p, b1p_missing = b1_prime_forecasts(
        lambda d: b960.b1c.b1_calendar_forecast(pub_rows, position_p[d], registry=registry, decision_time=sd.DECISION, splits=splits), common
    )
    names = ["B1", "B2", *candidates]
    grid = {n: score_all(forecasts[n]) for n in names}
    tail = {n: score_all(forecasts[n], sp.upper_tail_twcrps) for n in names}
    days = sorted(grid["B1"])
    days_p = sorted(b1p)
    grid_p = {B1P: score_all(b1p)}
    tail_p = {B1P: score_all(b1p, sp.upper_tail_twcrps)}
    for table in (grid, tail):
        for n, scores in table.items():
            if sorted(scores) != days:
                raise SystemExit(f"{n} does not score the same decision days as B1")
    for table in (grid_p, tail_p):
        if sorted(table[B1P]) != days_p:
            raise SystemExit("B1' does not score the decision days it forecasts")
    # the columns against B1' are on the days that have it: the candidates' scores on those days, beside B1' itself
    grid_p.update({n: {d: grid[n][d] for d in days_p} for n in candidates})
    tail_p.update({n: {d: tail[n][d] for d in days_p} for n in candidates})

    position = {row.date: i for i, row in enumerate(scratch)}
    for d in days:
        if d not in position:
            raise ValueError(f"decision day {d} is not a row of {args.panel}")
    states = decision_states(scratch, measurement_fields.load_registry(), days, position, DECISION)
    cuts = state_cuts(days, states)
    cuts_p = state_cuts(days_p, states)

    sd.SEED = SEED

    def headline(scores, benchmarks, candidate, groups):
        out = {}
        for label, group in groups.items():
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
        measure: {c: headline(scores, ("B1", "B2"), c, cuts) for c in candidates}
        for measure, scores in (("grid_crps", grid), ("upper_tail_twcrps", tail))
    }
    headlines_b1p = {
        measure: {c: headline(scores, (B1P,), c, cuts_p) for c in candidates}
        for measure, scores in (("grid_crps", grid_p), ("upper_tail_twcrps", tail_p))
    }

    # the pooled column of gbm_funding is the tracked pages' before anything is split; the variants are new
    t805 = json.loads(TRACKED_805.read_text(encoding="utf-8"))
    t634 = json.loads(TRACKED_634.read_text(encoding="utf-8"))
    for measure, tracked in (("grid_crps", "pooled_primary"), ("upper_tail_twcrps", "pooled_key_secondary")):
        pooled = reproducible(headlines[measure][CONTROL]["pooled"]["tests"])
        check_pooled(pooled, t634[tracked])
        check_pooled(pooled, t805["headlines"][measure][CONTROL]["pooled"]["tests"])

    counts = {label: len(group) for label, group in cuts.items()}
    counts_p = {label: len(group) for label, group in cuts_p.items()}
    document = {
        "panel_sha256": sd.panel_sha256(args.published),
        "scratch_panel_sha256": sd.panel_sha256(args.panel),
        "decision_days": {"n": len(days), "first": days[0].isoformat(), "last": days[-1].isoformat()},
        "decision_days_b1_prime": {"n": len(days_p), "missing": [d.isoformat() for d in b1p_missing]},
        "draws": draws,
        "seed": SEED,
        "excluded_day": EXCLUDED_DAY.isoformat(),
        "min_group_days": MIN_GROUP_DAYS,
        "state_days": counts,
        "state_days_b1_prime": counts_p,
        "candidates": list(candidates),
        "variants_not_run": not_run,
        "dropped": list(DROPPED),
        "provisional": [CONTROL],
        "pooled_reproduces": ["docs/pivot/evidence/spread-distribution-protocol/score.json", "docs/pivot/evidence/h5-splits-805/score.json"],
        "headlines": headlines,
        "headlines_b1_prime": headlines_b1p,
    }
    args.output.write_text(json.dumps(document, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    daily = {
        "panel_sha256": document["panel_sha256"],
        "decision_days": [d.isoformat() for d in days],
        "state": {d.isoformat(): states[d] for d in days},
        "candidates": list(candidates),
        "grid_crps": {n: {d.isoformat(): grid[n][d] for d in days} for n in names},
        "upper_tail_twcrps": {n: {d.isoformat(): tail[n][d] for d in days} for n in names},
        "b1_prime_grid_crps": {d.isoformat(): grid_p[B1P][d] for d in days_p},
        "b1_prime_upper_tail_twcrps": {d.isoformat(): tail_p[B1P][d] for d in days_p},
    }
    args.daily.write_text(json.dumps(daily, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(args.output), "daily": str(args.daily), "decision_days": len(days), "decision_days_b1_prime": len(days_p), "state_days": counts}))
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
}


def report_command(args) -> int:
    document = json.loads(args.score.read_text(encoding="utf-8"))
    p = document["decision_days_b1_prime"]
    out = [
        "# H5 headlines by the as-of scarcity state of the decision day: the calendar-aware models (#901)",
        "",
        f"Decision days {document['decision_days']['first']} to {document['decision_days']['last']} (n = {document['decision_days']['n']}); "
        f"studentized stationary bootstrap, {document['draws']} draws, one-sided 95%, seed {document['seed']}; panel "
        f"`{document['panel_sha256'][:8]}…`. Development data, not a verdict.",
        "",
        "Narrowed to the calendar-aware models by Eleonora's ruling of 22 October 2026 on #901: `gbm_funding` and #1027's two variants, each against "
        "B1, B2 and B1'. #634's `" + "`, `".join(document["dropped"][:-1]) + "` and " + document["dropped"][-1] + " are dropped, not re-walked; they stay "
        "provisional under the [register](provisional-calendar-register.md), and the #947 guard refuses their walks.",
        "",
        "State: ample is states 0 and 1, scarce is 2 and 3 (ruling on #515), public at the decision instant, each leg at its own latest public row. "
        "Decision days by cut (against B1 and B2): " + ", ".join(f"{k} {v}" for k, v in document["state_days"].items()) + ".",
        "",
        "The pooled column of `gbm_funding` against B1 and B2 reproduces the tracked figures of #634 and #805 to the digit (checked by the script before it wrote anything). "
        "`" + "`, `".join(document["provisional"]) + "` is provisional: calendar not read at the target day. The `gbm_funding_cal_*` rows are #1027's variants, "
        "new here, so their pooled column reproduces nothing. "
        + ("Not run: " + "; ".join(f"{k} ({v})" for k, v in document["variants_not_run"].items()) + ". " if document["variants_not_run"] else "")
        + "Which candidate replaces `gbm_funding` is Eleonora's decision, not this page's.",
        "",
        f"B1' is absent on {len(p['missing'])} decision days, so the columns against B1' are on {p['n']} days "
        "(B1' is never filled with B1). Decision days by cut (against B1'): " + ", ".join(f"{k} {v}" for k, v in document["state_days_b1_prime"].items()) + ".",
        "",
    ]
    for measure, title in TITLES.items():
        out += [f"## {title}", ""]
        for candidate, block in document["headlines"][measure].items():
            for benchmark in ("B1", "B2"):
                out += [f"### {candidate} against {benchmark}", "", *_table(block, candidate, benchmark), ""]
        for candidate, block in document["headlines_b1_prime"][measure].items():
            out += [f"### {candidate} against B1' (on the days B1' exists)", "", *_table(block, candidate, "B1_prime"), ""]
    args.output.write_text("\n".join(out) + "\n", encoding="utf-8")
    return 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="command", required=True)
    score = sub.add_parser("score", help="score the walks by the state")
    score.add_argument("--published", type=Path, required=True)
    score.add_argument("--panel", type=Path, required=True, help="the scratch panel (AUG3.csv, #1027's) that carries reserve_scarcity_state")
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
