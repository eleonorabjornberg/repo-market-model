"""How the judge's episodes and passes are defined (#486): four sensitivity readings of tier 1.

A scratch measurement, not a record: it writes JSON and Markdown to the paths it is given, nothing into
`docs/runs/`, and moves no published figure. The judge, the onset rule, the +5 bp threshold, the tiers and the cut-off
rule stay as declared (`metadata/pressure_judge.json`); the declared tier 1 is reproduced first, then re-read four
ways. Scored days are 2018-06-29 to 2025-12-31 only (`docs/decisions/lockbox.md`); the 2026 days are not read.

    PYTHONPATH=src python3 scripts/episode_sensitivity.py report --panel PUB.csv --bench 'OUT/bench_h{h}.json' \\
        --rows 'OUT/risk_h{h}.json' --output OUT/sensitivity.json --markdown OUT/tables.md

The five rows are the tier-1 passers of the risk-date severity model (#428): `risk_gbm`, `risk_gbm_base`,
`risk_logistic`, `risk_logistic_base` and `risk_quantile_skewt_base`. Their forecasts and their cut-offs (chosen
refit by refit by the declared rule, `pressure_judge.choose_cutoffs`) are never re-fitted here: each reading changes
what is counted as the event or how the pass is tested, and nothing else.

1. `events`: tier 1 with the event taken as each episode's largest day, and as every day above +10 bp, beside the
   declared onsets.
2. `margins`: for each onset the model missed, how far under the cut-off its probability was, by year.
3. `pairing`: the tier's "above climatology" test as declared (the candidate's lower bound against climatology's point
   estimate) beside the paired reading (the lower bound of the paired recall difference above zero).
4. `labels`: the number of onsets under other readings of the label (a cut at +4.5 or +5.5 bp, the unrounded float
   spread, one whole basis point higher), and tier 1 under each with the forecasts and cut-offs kept.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from dataclasses import replace
from datetime import date
from pathlib import Path
from typing import Callable, Dict, List, Mapping, Optional, Sequence, Tuple

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))

from repo_model import pressure, pressure_judge as pj  # noqa: E402
from repo_model.baseline import panel_sha256  # noqa: E402
from repo_model.data import audit_panel, exceeds_bp, load_daily_panel  # noqa: E402
from repo_model.evaluation_splits import load_split_declaration  # noqa: E402

SPLITS = REPO / "metadata" / "evaluation_splits.json"
ROWS = (
    "risk_gbm",
    "risk_gbm_base",
    "risk_logistic",
    "risk_logistic_base",
    "risk_quantile_skewt_base",
)
#: Days the judge's text names as absorbed into an episode by the onset rule.
NAMED_DAYS = ("2019-09-16", "2019-09-17", "2019-09-30", "2020-03-16", "2020-03-17")
MARGIN = 0.10
LEAD = 1


def _judge_script():
    spec = importlib.util.spec_from_file_location("pressure_judge_script", REPO / "scripts" / "pressure_judge.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules.setdefault("pressure_judge_script", module)
    spec.loader.exec_module(module)
    return module


# -- label rules -----------------------------------------------------------------------------------------------


def label_rules() -> Dict[str, Tuple[str, Callable[[float], bool]]]:
    """The readings of "a day above the threshold": name -> (description, is_event(spread_bp))."""

    return {
        "declared": ("whole basis points, strictly above +5 (round(spread) > 5)", lambda s: exceeds_bp(s, 5.0)),
        "float_5": ("the unrounded float spread, strictly above +5", lambda s: float(s) > 5.0),
        "cut_4.5": ("the unrounded spread strictly above +4.5", lambda s: float(s) > 4.5),
        "cut_5.5": ("the unrounded spread strictly above +5.5", lambda s: float(s) > 5.5),
        "whole_bp_6": ("whole basis points, strictly above +6 (one whole basis point higher)", lambda s: exceeds_bp(s, 6.0)),
    }


def onset_days(rows: Sequence, scored: Sequence[date], is_event: Callable[[float], bool]) -> Tuple[date, ...]:
    """The scored days that open an episode under `is_event`: the panel's own rule (`pressure.onsets`), any label.

    An event day with no event on the `ONSET_QUIET_DAYS` panel rows before it.
    """

    wanted = set(scored)
    flags = [(row.date, bool(is_event(float(row.spread_bps)))) for row in rows]
    found = []
    for index, (when, event) in enumerate(flags):
        if when not in wanted or not event or index < pressure.ONSET_QUIET_DAYS:
            continue
        if not any(flag for _, flag in flags[index - pressure.ONSET_QUIET_DAYS : index]):
            found.append(when)
    return tuple(found)


def episodes(
    rows: Sequence, scored: Sequence[date], is_event: Callable[[float], bool]
) -> List[dict]:
    """Each episode: an onset and the event days up to the next onset (or the last scored day).

    `peak` is the episode's largest day by the float spread (the earliest on a tie). Event days after the last
    scored day are not read.
    """

    last = max(scored)
    starts = onset_days(rows, scored, is_event)
    dated = [row for row in rows if row.date <= last]
    out = []
    for position, start in enumerate(starts):
        end = starts[position + 1] if position + 1 < len(starts) else None
        days = [
            row for row in dated
            if row.date >= start and (end is None or row.date < end) and is_event(float(row.spread_bps))
        ]
        peak = max(days, key=lambda row: (float(row.spread_bps), -row.date.toordinal()))
        out.append(
            {
                "onset": start.isoformat(),
                "onset_spread_bp": round(float(days[0].spread_bps), 3),
                "days": [row.date.isoformat() for row in days],
                "peak": peak.date.isoformat(),
                "peak_spread_bp": round(float(peak.spread_bps), 3),
            }
        )
    return out


def with_events(
    grid: pj.Grid,
    onset_days_: Sequence[date],
    pressure_of: Optional[Callable[[date], int]] = None,
) -> pj.Grid:
    """`grid` with its onset flags set to `onset_days_`, and its +5 bp outcome to `pressure_of(day)` when given.

    Flags are built on the grid's own days: the grids of the horizons do not start on the same day.
    """

    wanted = set(onset_days_)
    outcomes = dict(grid.outcomes)
    if pressure_of is not None:
        outcomes[5.0] = tuple(pressure_of(day) for day in grid.dates)
    return replace(grid, onset=tuple(1 if day in wanted else 0 for day in grid.dates), outcomes=outcomes)


# -- readings --------------------------------------------------------------------------------------------------


def _tier(declaration, name, grids, by_name, calendar) -> dict:
    scored = list(declaration.horizons)
    return pj._onset_tier(declaration, name, LEAD, scored, grids, by_name, calendar)


def _tier_summary(tier: dict) -> dict:
    recall = tier.get("recall", {})
    difference = tier.get("recall_difference", {})
    interval = recall.get("interval") or {}
    paired = difference.get("interval") or {}
    return {
        "onsets": tier.get("onsets"),
        "onsets_flagged": tier.get("onsets_flagged"),
        "recall": recall.get("mean"),
        "recall_lower": interval.get("lower"),
        "recall_upper": interval.get("upper"),
        "climatology_recall": tier.get("climatology_recall"),
        "recall_difference": difference.get("mean"),
        "recall_difference_lower": paired.get("lower"),
        "recall_difference_upper": paired.get("upper"),
        "worst_false_alarms_per_onset": tier.get("worst_false_alarms_per_onset"),
        "criteria": tier.get("criteria"),
        "passes": tier.get("passes"),
    }


def margin_table(
    declaration, name: str, grids: Mapping[int, pj.Grid], by_name: Mapping[str, Mapping[int, pj.Forecast]]
) -> dict:
    """How far under its cut-off each missed onset's probability was, per horizon and at any horizon, by year.

    The margin of a miss is `(cut-off - probability) / cut-off`. A cut-off of `inf` (the declared rule flagged
    nothing in that refit) is a miss with no margin and is counted apart. At any horizon, an onset is caught if it is
    flagged at some horizon 1 to 5, and its margin is the smallest over the horizons.
    """

    tau = declaration.primary
    horizons = list(declaration.horizons)
    onset = grids[horizons[0]].onset
    dates = grids[horizons[0]].dates
    years = sorted({day.year for day, o in zip(dates, onset) if o})

    def blank():
        return {
            "onsets": 0, "caught": 0, "missed_under_margin": 0, "missed_by_more": 0, "no_cutoff": 0, "missed_at_zero": 0,
        }

    where = {h: {day: k for k, day in enumerate(grids[h].dates)} for h in horizons}
    per = {str(h): {str(y): blank() for y in years} for h in horizons}
    anyh = {str(y): blank() for y in years}
    nearest: List[dict] = []  # onsets missed at every horizon, with the smallest margin
    for day, flag in zip(dates, onset):
        if not flag:
            continue
        year = str(day.year)
        gaps = []
        caught_any = False
        for h in horizons:
            if day not in where[h]:
                continue  # a day the horizon's grid does not score (its first days start later)
            forecast = by_name[name][h]
            index = where[h][day]
            p = forecast.probabilities[tau][index]
            cut = forecast.cutoffs[tau][index]
            cell = per[str(h)][year]
            cell["onsets"] += 1
            if p >= cut:
                cell["caught"] += 1
                caught_any = True
                gaps.append(("caught", 0.0))
            elif cut == float("inf"):
                cell["no_cutoff"] += 1
                gaps.append(("none", float("inf")))
            else:
                gap = (cut - p) / cut
                if p == 0.0:
                    cell["missed_at_zero"] += 1  # also counted below: a risk-date row forecasts 0 off its dates
                cell["missed_under_margin" if gap < MARGIN else "missed_by_more"] += 1
                gaps.append(("miss", gap))
        cell = anyh[year]
        cell["onsets"] += 1
        if caught_any:
            cell["caught"] += 1
        else:
            finite = [g for kind, g in gaps if kind == "miss"]
            if not finite:
                cell["no_cutoff"] += 1
                nearest.append({"onset": day.isoformat(), "margin": None})
            else:
                best = min(finite)
                cell["missed_under_margin" if best < MARGIN else "missed_by_more"] += 1
                nearest.append({"onset": day.isoformat(), "margin": round(best, 4)})
    return {"by_horizon": per, "any_horizon": anyh, "missed_at_every_horizon": nearest}


def run(
    declaration,
    rows: Sequence,
    grids: Mapping[int, pj.Grid],
    by_name: Mapping[str, Mapping[int, pj.Forecast]],
    calendar: Sequence[date],
    names: Sequence[str] = ROWS,
) -> dict:
    """The four readings on the shared grid. `by_name` carries the cut-offs `choose_cutoffs` chose."""

    horizons = list(declaration.horizons)
    first = grids[horizons[0]]
    scored = list(first.dates)
    by_date = {row.date: row for row in rows}
    rules = label_rules()
    declared_is_event = rules["declared"][1]

    # The declared onsets must be the grid's: the readings below start from the judge's own tier.
    if onset_days(rows, scored, declared_is_event) != tuple(d for d, o in zip(scored, first.onset) if o):
        raise ValueError("the declared label rule does not give the grid's onsets")

    # 1. The event.
    eps = episodes(rows, scored, declared_is_event)
    declared_days = onset_days(rows, scored, declared_is_event)
    peak_days = [date.fromisoformat(e["peak"]) for e in eps]
    above_10_days = [day for day in scored if exceeds_bp(by_date[day].spread_bps, 10.0)]
    episode_of: Dict[str, int] = {}
    for number, episode in enumerate(eps):
        for day in episode["days"]:
            episode_of[day] = number
    named = {}
    for text in NAMED_DAYS:
        row = by_date.get(date.fromisoformat(text))
        number = episode_of.get(text)
        named[text] = {
            "spread_bp": None if row is None else round(float(row.spread_bps), 3),
            "is_onset": bool(number is not None and eps[number]["onset"] == text),
            "episode_onset": None if number is None else eps[number]["onset"],
            "is_episode_peak": bool(number is not None and eps[number]["peak"] == text),
        }
    event_readings = {
        "declared_onsets": declared_days,
        "episode_peaks": peak_days,
        "days_above_10bp": above_10_days,
    }

    out: dict = {
        "scored": {"first": scored[0].isoformat(), "last": scored[-1].isoformat(), "days": len(scored)},
        "rows": list(names),
        "events": {
            "episodes": eps,
            "named_days": named,
            "counts": {label: len(days) for label, days in event_readings.items()},
            "tier_1": {},
        },
        "margins": {},
        "pairing": {},
        "labels": {"rules": {k: v[0] for k, v in rules.items()}, "onsets": {}, "tier_1": {}},
    }

    for name in names:
        out["events"]["tier_1"][name] = {
            label: _tier_summary(
                _tier(declaration, name, {h: with_events(grids[h], days) for h in horizons}, by_name, calendar)
            )
            for label, days in event_readings.items()
        }
        out["margins"][name] = margin_table(declaration, name, grids, by_name)

    # 3. The pairing of the "above climatology" test (the declared tier, read both ways).
    for name in names:
        tier = out["events"]["tier_1"][name]["declared_onsets"]
        lower = tier["recall_lower"]
        paired = tier["recall_difference_lower"]
        out["pairing"][name] = {
            "recall": tier["recall"],
            "recall_lower": lower,
            "climatology_recall": tier["climatology_recall"],
            "declared_test_passes": bool(lower is not None and lower > tier["climatology_recall"]),
            "recall_difference": tier["recall_difference"],
            "recall_difference_lower": paired,
            "recall_difference_upper": tier["recall_difference_upper"],
            "paired_test_passes": bool(paired is not None and paired > 0.0),
            "other_criteria": tier["criteria"],
        }

    # 4. The label.
    spreads = [float(by_date[day].spread_bps) for day in scored]
    whole = [round(s) for s in spreads]
    out["labels"]["spreads"] = {
        "not_whole_basis_points": sum(1 for s in spreads if abs(s - round(s)) > 1e-6),
        "exactly_5_bp": sum(1 for w in whole if w == 5),
        "exactly_6_bp": sum(1 for w in whole if w == 6),
        "exactly_5_bp_by_year": _by_year(scored, [w == 5 for w in whole]),
        "exactly_6_bp_by_year": _by_year(scored, [w == 6 for w in whole]),
        "float_noise_days_at_5_bp": sum(1 for s, w in zip(spreads, whole) if w == 5 and s > 5.0),
    }
    declared_set = set(onset_days(rows, scored, declared_is_event))
    for label, (_, is_event) in rules.items():
        found = set(onset_days(rows, scored, is_event))
        out["labels"]["onsets"][label] = {
            "count": len(found),
            "added": sorted(d.isoformat() for d in found - declared_set),
            "dropped": sorted(d.isoformat() for d in declared_set - found),
            "by_year": _by_year(sorted(found), [True] * len(found)),
        }
        if label == "declared":
            continue
        def alt_pressure(day, is_event=is_event):
            return 1 if is_event(float(by_date[day].spread_bps)) else 0

        altered = {h: with_events(grids[h], sorted(found), alt_pressure) for h in horizons}
        out["labels"]["tier_1"][label] = {
            name: _tier_summary(_tier(declaration, name, altered, by_name, calendar)) for name in names
        }
    return out


def _by_year(days: Sequence[date], flags: Sequence[bool]) -> Dict[str, int]:
    counts: Dict[str, int] = {}
    for day, flag in zip(days, flags):
        if flag:
            counts[str(day.year)] = counts.get(str(day.year), 0) + 1
    return dict(sorted(counts.items()))


# -- markdown --------------------------------------------------------------------------------------------------


def _f(value, places=3):
    return "n/a" if value is None else f"{value:.{places}f}"


def _flagged(tier: dict) -> str:
    flagged = tier.get("onsets_flagged")
    return f"{_f(flagged, 0)}/{tier.get('onsets')}"


def markdown(result: dict) -> str:
    lines: List[str] = []
    ev = result["events"]
    lines += [
        "Table 1. What the onset rule treats as the event (tier 1, lead >= 1, +5 bp, forecasts and cut-offs as declared).",
        "Onsets flagged at some horizon 1 to 5 / events; worst false alarms per onset; recall with its 90% interval.",
        "",
        "| model | event | flagged / events | false alarms per onset | recall [90% interval] |",
        "|---|---|---|---|---|",
    ]
    for name in result["rows"]:
        for label, text in (
            ("declared_onsets", "declared onsets"),
            ("episode_peaks", "each episode's largest day"),
            ("days_above_10bp", "every day above +10 bp"),
        ):
            tier = ev["tier_1"][name][label]
            lines.append(
                f"| {name} | {text} | {_flagged(tier)} | {_f(tier['worst_false_alarms_per_onset'], 2)} | "
                f"{_f(tier['recall'])} [{_f(tier['recall_lower'])}, {_f(tier['recall_upper'])}] |"
            )
    lines += ["", "Table 2. Named days of the largest stress, under the declared onset rule.", "",
              "| day | spread (bp) | an onset? | the episode it belongs to opens on | the episode's largest day? |",
              "|---|---|---|---|---|"]
    for day, info in ev["named_days"].items():
        lines.append(
            f"| {day} | {_f(info['spread_bp'], 1)} | {'yes' if info['is_onset'] else 'no'} | "
            f"{info['episode_onset'] or 'n/a'} | {'yes' if info['is_episode_peak'] else 'no'} |"
        )
    lines += ["", "Table 3. The episodes: onset, its spread, the episode's largest day and its spread.", "",
              "| onset | onset spread (bp) | event days | largest day | its spread (bp) |", "|---|---|---|---|---|"]
    for episode in ev["episodes"]:
        lines.append(
            f"| {episode['onset']} | {_f(episode['onset_spread_bp'], 1)} | {len(episode['days'])} | "
            f"{episode['peak']} | {_f(episode['peak_spread_bp'], 1)} |"
        )

    lines += ["", f"Table 4. Missed onsets that fell under the cut-off by less than {int(MARGIN * 100)}% of it, by year "
              "(missed under the margin / missed in all / onsets). Any horizon: caught if flagged at some horizon 1 to 5; "
              "its margin is the smallest.", ""]
    for name in result["rows"]:
        table = result["margins"][name]
        years = sorted(table["any_horizon"])
        lines += [f"{name}", "", "| reading | " + " | ".join(years) + " | all |", "|---|" + "---|" * (len(years) + 1)]
        readings = [("any horizon", table["any_horizon"])] + [
            (f"h = {h}", table["by_horizon"][h]) for h in sorted(table["by_horizon"])
        ]
        for label, cells in readings:
            def show(c):
                missed = c["missed_under_margin"] + c["missed_by_more"] + c["no_cutoff"]
                return f"{c['missed_under_margin']} / {missed} / {c['onsets']}"
            total = {
                k: sum(c[k] for c in cells.values())
                for k in ("onsets", "missed_under_margin", "missed_by_more", "no_cutoff")
            }
            lines.append(f"| {label} | " + " | ".join(show(cells[y]) for y in years) + f" | {show(total)} |")
        zero = sum(c["missed_at_zero"] for cells in table["by_horizon"].values() for c in cells.values())
        misses = sum(
            c["missed_under_margin"] + c["missed_by_more"] + c["no_cutoff"]
            for cells in table["by_horizon"].values() for c in cells.values()
        )
        lines += [f"Of the {misses} misses over the five horizons, {zero} were at a probability of exactly 0.", ""]

    lines += ["Table 5. Tier 1's \"above climatology\" test, as declared and paired (lead >= 1, declared onsets).",
              "Declared: the lower bound of the recall interval above climatology's recall. Paired: the lower bound of the "
              "interval of the paired recall difference above zero.", "",
              "| model | recall [lower] | climatology recall | declared test | recall difference [90% interval] | paired test |",
              "|---|---|---|---|---|---|"]
    for name in result["rows"]:
        p = result["pairing"][name]
        lines.append(
            f"| {name} | {_f(p['recall'])} [{_f(p['recall_lower'])}] | {_f(p['climatology_recall'])} | "
            f"{'passes' if p['declared_test_passes'] else 'fails'} | {_f(p['recall_difference'])} "
            f"[{_f(p['recall_difference_lower'])}, {_f(p['recall_difference_upper'])}] | "
            f"{'passes' if p['paired_test_passes'] else 'fails'} |"
        )

    lab = result["labels"]
    lines += ["", "Table 6. Onsets under other readings of the label.", "",
              "| label | count | added | dropped |", "|---|---|---|---|"]
    for label, info in lab["onsets"].items():
        lines.append(
            f"| {label}: {lab['rules'][label]} | {info['count']} | {', '.join(info['added']) or 'none'} | "
            f"{', '.join(info['dropped']) or 'none'} |"
        )
    spreads = lab["spreads"]
    lines += ["", f"Days not on a whole basis point: {spreads['not_whole_basis_points']}. Days at exactly +5 bp: "
              f"{spreads['exactly_5_bp']} (by year {spreads['exactly_5_bp_by_year']}); at exactly +6 bp: "
              f"{spreads['exactly_6_bp']} (by year {spreads['exactly_6_bp_by_year']}); days at +5 bp whose float spread is "
              f"above 5: {spreads['float_noise_days_at_5_bp']}.", "",
              "Table 7. Tier 1 under each label (forecasts and cut-offs kept; the +5 bp outcome and the onsets re-derived).", "",
              "| model | label | flagged / onsets | false alarms per onset | recall [90% interval] |", "|---|---|---|---|---|"]
    for label, rows in lab["tier_1"].items():
        for name in result["rows"]:
            tier = rows[name]
            lines.append(
                f"| {name} | {label} | {_flagged(tier)} | {_f(tier['worst_false_alarms_per_onset'], 2)} | "
                f"{_f(tier['recall'])} [{_f(tier['recall_lower'])}, {_f(tier['recall_upper'])}] |"
            )
    return "\n".join(lines) + "\n"


# -- commands --------------------------------------------------------------------------------------------------


def _document(template: str, horizon: int) -> dict:
    return json.loads(Path(template.format(h=horizon)).read_text(encoding="utf-8"))


def report_command(args) -> int:
    script = _judge_script()
    declaration = pj.load_declaration()
    commit = script.require_committed_declaration(pj.DEFAULT_DECLARATION)
    script.require_committed_file(pj.DEFAULT_WEIGHTED_MISS)
    declaration = replace(declaration, weighted_miss=pj.load_weighted_miss(applied=None))
    rows = load_daily_panel(args.panel)
    audit_panel(rows)
    splits = load_split_declaration(SPLITS)
    digest = panel_sha256(args.panel)
    forecasts = []
    for horizon in declaration.horizons:
        for template, wanted in ((args.bench, (declaration.climatology, declaration.persistence)), (args.rows, ROWS)):
            document = _document(template, horizon)
            if document["panel_sha256"] != digest and template == args.bench:
                raise SystemExit(f"{template.format(h=horizon)} was scored on another panel")
            document = dict(document)
            document["forecasts"] = {k: v for k, v in document["forecasts"].items() if k in wanted}
            missing = [k for k in wanted if k not in document["forecasts"]]
            if missing:
                raise SystemExit(f"{template.format(h=horizon)} holds no {missing}")
            forecasts.extend(pj.forecasts_from_horizon_document(document))
    calendar = [row.date for row in rows]
    reference = {f.horizon: f for f in forecasts if f.name == declaration.climatology}
    grids = {
        h: pj.build_grid(declaration, h, rows, reference[h].dates, splits, scarcity_state={})
        for h in declaration.horizons
    }
    pj._check_grid(declaration, grids, confirmation=False)
    by_name = pj._check_forecasts(declaration, grids, forecasts, confirmation=False)
    chosen = {(f.name, f.horizon): f for f in pj.choose_cutoffs(declaration, grids, forecasts, calendar)}
    by_name = {
        name: {h: chosen[(name, h)] for h in per_horizon} for name, per_horizon in by_name.items()
    }
    result = run(declaration, rows, grids, by_name, calendar)
    result["provenance"] = {"panel_sha256": digest, "declaration_commit": commit}
    args.output.write_text(json.dumps(result, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    if args.markdown:
        args.markdown.write_text(markdown(result), encoding="utf-8")
    print(json.dumps({"output": str(args.output), "rows": result["rows"], "counts": result["events"]["counts"]}))
    return 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="command", required=True)
    report = sub.add_parser("report", help="the four readings of tier 1")
    report.add_argument("--panel", type=Path, required=True)
    report.add_argument("--bench", required=True, help="pattern with {h}: the benchmark forecast file of each horizon")
    report.add_argument("--rows", required=True, help="pattern with {h}: the risk-date forecast file of each horizon")
    report.add_argument("--output", type=Path, required=True)
    report.add_argument("--markdown", type=Path)
    report.set_defaults(func=report_command)
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
