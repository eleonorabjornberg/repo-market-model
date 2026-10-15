"""The splits H5's headline claims lacked (#805, finding #798's day, H5 steps 1 to 3): a re-score of #634's and #707's walks.

A scratch measurement, not a record: it fits no model, writes JSON and Markdown to the paths it is given and nothing into
`docs/runs/`, and changes no rule. It reads the walk-forward laws of #634 unchanged (`scripts/spread_distribution_634.py walk`)
and scores them with the protocol's scorer, exactly as #634 and #707 do, so every pooled figure reproduces the page's. It adds:

1. each skill headline against B1 and B2 by the day type of the decision day's anchor (`repo_model.anchor_day_type`, #741),
   beside the pooled figure: grid CRPS and upper-tail twCRPS of #634's four candidates, variant (a) on its own five levels,
   and #707's three remedies of its two candidates;
2. the same headlines without decision day 2019-09-18 (#798). The candidates' scores that day are the walks', not an
   approximation;
3. the upper-tail Brier claims of #634 (P(spread > 0, 2, 5, 10 bp)) by the regime of the decision day and by the pressure-day
   type of the target day, with the number of event cells and event days beside every figure;
4. `sp.calibrate_critical_value`'s c at 125 and 250 days on the 1,868-day pool S(B2) - S(B1), in both orientations, with and
   without 2019-09-18, with the values in force beside them.

No day after 2025-12-31 is read (`docs/decisions/lockbox.md`). Development days give a score and an interval, never a verdict
(scoring protocol v1, #640). Intervals are the studentized stationary bootstrap's (block 10, one-sided 95%), seeded as the page
being reproduced seeds them (634 for #634's tables, 707 for #707's remedies).

    # PUBLISHED.csv, AUG2D.csv and the walks in OUT are built exactly as in the docstring of scripts/spread_distribution_634.py
    PYTHONPATH=src python3 scripts/h5_splits_805.py score --published PUBLISHED.csv --walks OUT --output OUT/h5_splits_805.json
    PYTHONPATH=src python3 scripts/h5_splits_805.py report --score OUT/h5_splits_805.json --output OUT/h5_splits_805.md
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from datetime import date
from pathlib import Path
from typing import Dict, Iterable, List, Mapping, Optional, Sequence, Tuple

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))

from repo_model import protocol_benchmarks as pb, scoring_protocol as sp  # noqa: E402
from repo_model.anchor_day_type import anchor_day_types  # noqa: E402
from repo_model.data import audit_panel, exceeds_bp, load_daily_panel  # noqa: E402
from repo_model.evaluation_splits import load_split_declaration  # noqa: E402
from repo_model.lockbox import require_unlocked  # noqa: E402

SPLITS = REPO / "metadata" / "evaluation_splits.json"
SOURCES = REPO / "metadata" / "sources.json"
LAST_TARGET = date(2025, 12, 31)
#: the one decision day of finding #798.
EXCLUDED_DAY = date(2019, 9, 18)
HORIZONS = sp.HORIZONS
CANDIDATES = ("gbm_funding", "a_published_new", "b_gbm_new", "c_two_part_new")
WALKS = ("published",) + CANDIDATES
#: #707's two candidates and its three remedies.
REMEDIED = ("gbm_funding", "c_two_part_new")
KINDS = ("level", "scale", "shrink")
THRESHOLDS_BP = (0.0, 2.0, 5.0, 10.0)
#: a group of fewer decision days than this is counted but not tested (the floor of #686 and #761).
MIN_GROUP_DAYS = 20
SEED_634, SEED_707 = 634, 707
CALIBRATION_WINDOWS, CALIBRATION_SEED = 20_000, 1
CALIBRATION_CHECKPOINTS = (125, 250)


def _load(name: str):
    spec = importlib.util.spec_from_file_location(f"{name}_script", REPO / "scripts" / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[f"{name}_script"] = module
    spec.loader.exec_module(module)
    return module


# -- the cuts (tested) ---------------------------------------------------------------------------------------------------


def drop_day(days: Iterable[date], day: date) -> List[date]:
    """`days` without `day`.

    Raises:
        ValueError: `day` is not among `days` (the cut would silently be the whole group).
    """

    kept = list(days)
    if day not in kept:
        raise ValueError(f"{day} is not among the {len(kept)} days it is to be dropped from")
    return [d for d in kept if d != day]


def group_by_label(days: Iterable[date], labels: Mapping[date, str]) -> Dict[str, List[date]]:
    """The days carrying each label, in date order. A day without a label raises `KeyError`."""

    out: Dict[str, List[date]] = {}
    for day in sorted(days):
        out.setdefault(labels[day], []).append(day)
    return out


def orientations(series: Sequence[float]) -> Dict[str, List[float]]:
    """The calibration series in both orientations: S(B2) - S(B1) as given, and S(B1) - S(B2)."""

    return {"S(B2) - S(B1)": list(series), "S(B1) - S(B2)": [-v for v in series]}


def event_tally(happened: Mapping[Tuple[date, int], bool], group: Iterable[date]) -> Dict[str, int]:
    """How many (decision day, lead) cells the group holds, how many of them are events, and on how many days."""

    members = set(group)
    cells = [(cell, flag) for cell, flag in happened.items() if cell[0] in members]
    events = [cell for cell, flag in cells if flag]
    return {"cells": len(cells), "event_cells": len(events), "event_days": len({cell[0] for cell in events})}


# -- the scores ----------------------------------------------------------------------------------------------------------


def prepare(published: Path, walks: Path):
    """The panel, the walks' forecasts on the scored decision days, and the benchmarks, as #634 and #707 prepare them."""

    sd = _load("spread_distribution_634")
    require_unlocked([LAST_TARGET], where="h5_splits_805")
    rows = load_daily_panel(published)
    audit_panel(rows)
    calendar = [row.date for row in rows]
    position = {day: index for index, day in enumerate(calendar)}
    outcomes = {row.date: row.spread_bps for row in rows}
    row_of = {row.date: row for row in rows}
    splits = load_split_declaration(SPLITS)
    registry = json.loads(SOURCES.read_text(encoding="utf-8"))
    laws = {name: sd.load_laws(walks, name, native=(name == "published")) for name in WALKS}
    decisions, days_by = {}, {}
    for name, walk in laws.items():
        decisions[name], days_by[name] = sd.lead_forecasts(walk, calendar)
    common = sorted(set.intersection(*(set(days) for days in days_by.values())))
    common = [day for day in common if all(calendar[position[day] + h] <= LAST_TARGET for h in HORIZONS)]
    sd.refuse_locked(common + [calendar[position[day] + h] for day in common for h in HORIZONS])
    usable = []
    for day in common:
        try:
            pb.forecasts(pb.b1_forecast, rows, [day], registry=registry, decision_time=sd.DECISION)
            pb.forecasts(pb.b2_forecast, rows, [day], registry=registry, decision_time=sd.DECISION, splits=splits)
            usable.append(day)
        except sp.ProtocolError:
            pass
    common = usable
    b1 = pb.forecasts(pb.b1_forecast, rows, common, registry=registry, decision_time=sd.DECISION)
    b2 = pb.forecasts(pb.b2_forecast, rows, common, registry=registry, decision_time=sd.DECISION, splits=splits)
    forecasts = {"B1": b1, "B2": b2}
    for name in CANDIDATES:
        forecasts[name] = sp.fill_missing({day: decisions[name][day] for day in common}, b1, common).forecasts
    return {
        "sd": sd, "rows": rows, "calendar": calendar, "position": position, "outcomes": outcomes, "row_of": row_of,
        "splits": splits, "registry": registry, "common": common, "b1": b1, "forecasts": forecasts,
    }


def skill_table(sd, h707, scores, benchmarks: Sequence[str], candidate: str, group: Sequence[date], draws: int) -> dict:
    """Candidate against each benchmark on `group`; empty when the group is too small for the lag."""

    if len(group) <= sp.HAC_LAG:
        return {}
    return h707.paired(sd, scores, [(b, candidate) for b in benchmarks], list(group), draws)


def cuts(days: Sequence[date], anchors: Mapping[date, str]) -> Dict[str, List[date]]:
    """pooled; without the excluded day; each anchor type; each anchor type without the excluded day."""

    out = {"pooled": list(days), "without_2019-09-18": drop_day(days, EXCLUDED_DAY)}
    for label, members in group_by_label(days, anchors).items():
        out[f"anchor:{label}"] = members
        if EXCLUDED_DAY in members:
            out[f"anchor:{label} without_2019-09-18"] = drop_day(members, EXCLUDED_DAY)
    return out


def mean_of(series: Mapping[date, float], group: Sequence[date]) -> Optional[float]:
    return sum(series[d] for d in group) / len(group) if group else None


def score_command(args) -> int:
    ctx = prepare(args.published, args.walks)
    sd = ctx["sd"]
    h707 = _load("h5_step3_707")
    draws = args.draws
    calendar, position, outcomes = ctx["calendar"], ctx["position"], ctx["outcomes"]
    splits, row_of, common = ctx["splits"], ctx["row_of"], ctx["common"]
    forecasts, b1 = ctx["forecasts"], ctx["b1"]

    def score_all(fc, score=sp.grid_crps):
        return sp.day_scores(fc, outcomes, calendar, score=score)

    names = ["B1", "B2", *CANDIDATES]
    grid = {n: score_all(forecasts[n]) for n in names}
    tail = {n: score_all(forecasts[n], sp.upper_tail_twcrps) for n in names}
    days = sorted(grid["B1"])
    for n in names:
        if sorted(grid[n]) != days or sorted(tail[n]) != days:
            raise SystemExit(f"{n} does not score the same decision days as B1")
    five = {n: {d: {h: sd.five_levels(forecasts[n][d][h]) for h in HORIZONS} for d in days} for n in names}
    five_crps = {n: score_all(five[n], sd.five_crps) for n in ("B1", "B2", "a_published_new")}
    five_tw = {n: score_all(five[n], sd.five_twcrps) for n in ("B1", "B2", "a_published_new")}
    anchors = anchor_day_types(
        ctx["rows"], days, registry=ctx["registry"], decision_time=sd.DECISION, splits=splits
    )
    cut = cuts(days, anchors)
    document: dict = {
        "panel_sha256": sd.panel_sha256(args.published),
        "decision_days": {"n": len(days), "first": days[0].isoformat(), "last": days[-1].isoformat()},
        "draws": draws,
        "excluded_day": EXCLUDED_DAY.isoformat(),
        "anchor_day_types": {label: len(members) for label, members in group_by_label(days, anchors).items()},
        "min_group_days": MIN_GROUP_DAYS,
    }
    # the excluded day itself, scored by the walks
    document["the_day"] = {
        "anchor_type": anchors[EXCLUDED_DAY],
        "grid_crps": {n: grid[n][EXCLUDED_DAY] for n in names},
        "b1_mean_all_days": sum(grid["B1"].values()) / len(days),
        "b1_share_of_the_denominator": grid["B1"][EXCLUDED_DAY] / sum(grid["B1"].values()),
    }

    def headline(scores, benchmarks, candidate, seed):
        sd.SEED = seed
        out = {}
        for label, group in cut.items():
            if len(group) < MIN_GROUP_DAYS:
                out[label] = {"days": len(group), "note": f"fewer than {MIN_GROUP_DAYS} days; not tested"}
                continue
            out[label] = {
                "days": len(group),
                "benchmark_mean": {b: mean_of(scores[b], group) for b in benchmarks},
                "candidate_mean": mean_of(scores[candidate], group),
                "tests": skill_table(sd, h707, scores, benchmarks, candidate, group, draws),
            }
        return out

    document["headlines"] = {
        "grid_crps": {c: headline(grid, ("B1", "B2"), c, SEED_634) for c in CANDIDATES},
        "upper_tail_twcrps": {c: headline(tail, ("B1", "B2"), c, SEED_634) for c in CANDIDATES},
        "a_on_its_own_five_levels_crps": {"a_published_new": headline(five_crps, ("B1", "B2"), "a_published_new", SEED_634)},
        "a_on_its_own_five_levels_twcrps": {"a_published_new": headline(five_tw, ("B1", "B2"), "a_published_new", SEED_634)},
    }

    # #707's remedies of its two candidates, pooled against B1 (the table of its sub-question 1)
    def cells_of(fc, lead):
        return [
            h707.Cell(d, calendar[position[d] + lead], list(fc[d][lead]), list(b1[d][lead]), outcomes.get(calendar[position[d] + lead]))
            for d in common
        ]

    remedy_scores = {"B1": grid["B1"]}
    for name in REMEDIED:
        for kind in KINDS:
            fc_r = {d: {} for d in common}
            for h in HORIZONS:
                for decision, law in h707.remedy_laws(cells_of(forecasts[name], h), kind).items():
                    fc_r[decision][h] = law
            remedy_scores[f"{name}+{kind}"] = score_all(fc_r)
    document["remedies"] = {
        label: headline(remedy_scores, ("B1",), label, SEED_707) for label in remedy_scores if label != "B1"
    }

    # the upper-tail Brier of P(spread > tau), by regime and by pressure-day type
    bench_files = {h: json.loads((args.walks / f"exceed_h{h}.json").read_text(encoding="utf-8")) for h in HORIZONS}
    sd.SEED = SEED_634
    kinds = {
        (d, h): splits.reporting_day_type(calendar[position[d] + h], row_of[calendar[position[d] + h]].values)
        for d in days for h in HORIZONS
    }
    brier: dict = {}
    for tau in THRESHOLDS_BP:
        key = f"{tau:g}"
        probability: Dict[str, Dict[Tuple[date, int], float]] = {n: {} for n in CANDIDATES}
        for n in CANDIDATES:
            for decision in days:
                for h in HORIZONS:
                    probability[n][(decision, h)] = sd.exceedance(forecasts[n][decision][h], tau)
        for model in ("persistence_logistic", "calendar_climatology"):
            probability[model] = {}
            for decision in days:
                for h in HORIZONS:
                    value = bench_files[h]["forecasts"][model][key].get(calendar[position[decision] + h].isoformat())
                    if value is not None:
                        probability[model][(decision, h)] = float(value)
        every = list(CANDIDATES) + ["persistence_logistic", "calendar_climatology"]
        cells = set.intersection(*(set(probability[n]) for n in every))
        happened = {cell: exceeds_bp(outcomes[calendar[position[cell[0]] + cell[1]]], tau) for cell in cells}
        score = {n: {cell: sd.brier(probability[n][cell], happened[cell]) for cell in cells} for n in every}
        complete = [d for d in days if all((d, h) in cells for h in HORIZONS)]
        groups: Dict[str, Tuple[List[date], object]] = {
            "pooled": (complete, lambda d, h: True),
            "without_2019-09-18": (drop_day(complete, EXCLUDED_DAY), lambda d, h: True),
        }
        for label in splits.regime_labels:
            members = [d for d in complete if splits.regime(d) == label]
            if members:
                groups[f"regime:{label}"] = (members, lambda d, h: True)
        for kind in sorted(set(kinds.values())):
            groups[f"type:{kind}"] = (complete, lambda d, h, kind=kind: kinds[(d, h)] == kind)
        entry = {}
        for label, (members, include) in groups.items():
            daily = {n: sd.day_means({c: v for c, v in score[n].items() if c[0] in set(members)}, include) for n in every}
            group = sorted(set.intersection(*(set(m) for m in daily.values())) & set(members))
            tally = event_tally({c: f for c, f in happened.items() if include(*c)}, group)
            row = {"days": len(group), **tally, "mean_brier": {n: mean_of(daily[n], group) for n in every}, "tests": {}}
            if tally["event_cells"] and len(group) >= MIN_GROUP_DAYS:
                row["tests"] = h707.paired(
                    sd, daily,
                    [(b, c) for c in CANDIDATES for b in ("persistence_logistic", "calendar_climatology")],
                    group, draws,
                )
            elif tally["event_cells"] and len(group) > 0:
                row["note"] = f"fewer than {MIN_GROUP_DAYS} days; not tested"
            entry[label] = row
        brier[key] = entry
    document["upper_tail_brier"] = brier

    # c at 125 and 250 days, both orientations, with and without the day (#798)
    levels = dict(zip(sp.CHECKPOINTS, sp.nominal_levels()))
    pool = [grid["B2"][d] - grid["B1"][d] for d in days]
    pool_without = [grid["B2"][d] - grid["B1"][d] for d in drop_day(days, EXCLUDED_DAY)]
    calibration: dict = {
        "days": len(pool),
        "windows": CALIBRATION_WINDOWS,
        "seed": CALIBRATION_SEED,
        "in_force_grid_comparison": {str(n): sp.CRITICAL_VALUES[sp.GRID_COMPARISON][n] for n in CALIBRATION_CHECKPOINTS},
        "values": {},
    }
    for pool_label, series in (("all days", pool), ("without 2019-09-18", pool_without)):
        for orientation, values in orientations(series).items():
            calibration["values"][f"{pool_label} | {orientation}"] = {
                str(n): sp.calibrate_critical_value(
                    values, days=n, level=levels[n], windows=CALIBRATION_WINDOWS, seed=CALIBRATION_SEED
                )
                for n in CALIBRATION_CHECKPOINTS
            }
    document["calibration"] = calibration
    args.output.write_text(json.dumps(document, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(args.output), "decision_days": len(days)}))
    return 0


# -- the report ----------------------------------------------------------------------------------------------------------


def _cell(entry: Optional[dict]) -> str:
    if not entry:
        return "n/a"
    if entry.get("identical"):
        return "0.0% (identical forecasts)"
    return f"{entry['skill'] * 100:+.1f}% [{entry['skill_lower_95_one_sided'] * 100:+.1f}%, {entry['skill_upper_95_one_sided'] * 100:+.1f}%]"


def _headline_table(block: Mapping[str, dict], candidate: str, benchmark: str) -> List[str]:
    lines = ["| cut | days | skill against " + benchmark + " |", "|---|---|---|"]
    for label, row in block.items():
        test = row.get("tests", {}).get(f"{benchmark} -> {candidate}")
        lines.append(f"| {label} | {row['days']} | {_cell(test) if test else row.get('note', 'n/a')} |")
    return lines


def report_command(args) -> int:
    document = json.loads(args.score.read_text(encoding="utf-8"))
    out = [
        "# H5 headline splits and the day 2019-09-18 (#805)",
        "",
        f"Decision days {document['decision_days']['first']} to {document['decision_days']['last']} (n = {document['decision_days']['n']}); "
        f"studentized stationary bootstrap, {document['draws']} draws, one-sided 95%; panel `{document['panel_sha256'][:8]}…`. "
        "Development data, not a verdict.",
        "",
        f"Anchor day types (decision days): {', '.join(f'{k} {v}' for k, v in sorted(document['anchor_day_types'].items()))}.",
        "",
        "## The day",
        "",
        f"2019-09-18 (anchor type: {document['the_day']['anchor_type']}). B1's grid CRPS that day is "
        f"{document['the_day']['grid_crps']['B1']:.1f} bp against a mean of {document['the_day']['b1_mean_all_days']:.3f} over all days: "
        f"{document['the_day']['b1_share_of_the_denominator'] * 100:.1f}% of B1's total. Walk scores that day: "
        + ", ".join(f"{n} {v:.2f}" for n, v in document["the_day"]["grid_crps"].items() if n != "B1")
        + ".",
        "",
    ]
    for measure, title in (
        ("grid_crps", "Grid CRPS (the primary score)"),
        ("upper_tail_twcrps", "Upper-tail twCRPS (weight 1{y > 0 bp})"),
        ("a_on_its_own_five_levels_crps", "Variant (a) on its own five levels, CRPS"),
        ("a_on_its_own_five_levels_twcrps", "Variant (a) on its own five levels, twCRPS"),
    ):
        out += [f"## {title}", ""]
        for candidate, block in document["headlines"][measure].items():
            for benchmark in ("B1", "B2"):
                out += [f"### {candidate} against {benchmark}", "", *_headline_table(block, candidate, benchmark), ""]
    out += ["## #707's remedies, grid CRPS against B1", ""]
    for label, block in document["remedies"].items():
        out += [f"### {label}", "", *_headline_table(block, label, "B1"), ""]
    out += ["## Upper-tail Brier of P(spread > tau)", "",
            "Skill is against the benchmark named; events are (decision day, lead) cells whose target exceeds tau.", ""]
    for key, groups in document["upper_tail_brier"].items():
        out += [f"### tau = {key} bp", "", "| group | days | cells | event cells | event days | gbm | (a) | (b) | (c) | pers.-logistic | climatology |",
                "|---|---|---|---|---|---|---|---|---|---|---|"]
        for label, row in groups.items():
            m = row["mean_brier"]
            out.append(
                f"| {label} | {row['days']} | {row['cells']} | {row['event_cells']} | {row['event_days']} | "
                + " | ".join(f"{m[n]:.4f}" for n in (*CANDIDATES, "persistence_logistic", "calendar_climatology")) + " |"
            )
        out += ["", "Skill of (c) in Brier score [one-sided 95% bounds]:", "", "| group | against persistence-logistic | against climatology |", "|---|---|---|"]
        for label, row in groups.items():
            cells = [_cell(row["tests"].get(f"{b} -> c_two_part_new")) if row["tests"] else row.get("note", "no events") for b in ("persistence_logistic", "calendar_climatology")]
            out.append(f"| {label} | {cells[0]} | {cells[1]} |")
        out += [""]
    calibration = document["calibration"]
    out += ["## Calibrated critical value c (`sp.calibrate_critical_value`)", "",
            f"{calibration['days']}-day pool, {calibration['windows']} windows, seed {calibration['seed']}. In force (grid comparison): "
            + ", ".join(f"{n} days {v:.3f}" for n, v in calibration["in_force_grid_comparison"].items()) + ".", "",
            "| pool and orientation | c at 125 days | c at 250 days |", "|---|---|---|"]
    for label, values in calibration["values"].items():
        out.append(f"| {label} | {values['125']:.3f} | {values['250']:.3f} |")
    args.output.write_text("\n".join(out) + "\n", encoding="utf-8")
    return 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="command", required=True)
    score = sub.add_parser("score", help="score the walks")
    score.add_argument("--published", type=Path, required=True)
    score.add_argument("--walks", type=Path, required=True)
    score.add_argument("--output", type=Path, required=True)
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
