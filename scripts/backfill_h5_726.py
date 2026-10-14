"""Does the 2014-2018 back-fill move H5's development score? (#726, H4 step 3)

A scratch measurement, not a record: it writes CSV, JSON and Markdown to the paths it is given and nothing into
`docs/runs/`. Exploration on development data: under scoring protocol v1 (#640) such data never gives a verdict.
Every choice is in `metadata/backfill_h5_726.json`, which this script refuses to read unless it is committed and
unchanged. No day after 2025-12-31 is read (`docs/decisions/lockbox.md`; `spread_distribution_634.refuse_locked`, and
`scoring_protocol.day_scores`).

H5's candidate is #634's `gbm_funding` (declared in `metadata/backfill_h5_726.json`). It is walked twice by
`scripts/spread_distribution_634.py`'s own `walk`, unchanged: on the published panel (the `without` arm, #634's control)
and on the published panel with the 899 back-filled rows before it (the `with` arm). A back-filled row carries only the
series #661 established (`ESTABLISHED`); every other cell is blank, which the fitter reads through its fitted imputation.
Every fit of the with arm passes `backfill.require_posting_established` with the instant of
`metadata/backfill_posting.json`, and the scored folds pass `backfill.require_training_only`.

    PYTHONPATH=src python3 -m repo_model.cli build --raw-root tests/fixtures/snapshots/funding_inputs --output PUBLISHED.csv \\
        --build-cutoff 2026-09-08T21:31:42+00:00 --decision-time 16:00:00
    PYTHONPATH=src python3 scripts/backfill_history.py panel --output EXT.csv --scratch SCRATCH.csv
    PYTHONPATH=src python3 scripts/backfill_h5_726.py panel --extended EXT.csv --output EXT_EST.csv
    for h in 1 2 3 4 5:
        PYTHONPATH=src python3 scripts/backfill_h5_726.py forecasts --arm without --panel PUBLISHED.csv --published PUBLISHED.csv \\
            --horizon $h --output OUT/without_h$h.json
        PYTHONPATH=src python3 scripts/backfill_h5_726.py forecasts --arm with --panel EXT_EST.csv --published PUBLISHED.csv \\
            --horizon $h --output OUT/with_h$h.json
    PYTHONPATH=src python3 scripts/backfill_h5_726.py score --published PUBLISHED.csv --runs OUT --output OUT/score.json --markdown OUT/score.md
"""

from __future__ import annotations

import argparse
import csv
import functools
import importlib.util
import json
import math
import random
import sys
from datetime import date, datetime, time
from pathlib import Path
from typing import Dict, List, Mapping, Optional, Sequence, Tuple

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))

from repo_model import backfill, metrics, ml, protocol_benchmarks as pb, scoring_protocol as sp  # noqa: E402
from repo_model.asof import InformationRule  # noqa: E402
from repo_model.baseline import ScoredFold, panel_sha256  # noqa: E402
from repo_model.data import audit_panel, load_daily_panel  # noqa: E402
from repo_model.evaluation_splits import load_split_declaration  # noqa: E402
from repo_model.lockbox import require_unlocked  # noqa: E402

DECLARATION = REPO / "metadata" / "backfill_h5_726.json"
POSTING = REPO / "metadata" / "backfill_posting.json"
SEED = 726
LAST_TARGET = date(2025, 12, 31)
ARMS = ("without", "with")
#: What a back-filled row carries (#661 established the posting of TGCR, BGCR and SOFR; IORB is administered and announced;
#: the calendar columns are functions of the date). Every other cell of such a row is blank.
ESTABLISHED = (
    "date", "sofr", "iorb", "sofr_volume", "tgcr", "bgcr", "quarter_end", "tax_date", "days_to_month_end",
)
LOW90, HIGH90 = sp.GRID.index(0.05), sp.GRID.index(0.95)
LOW50, HIGH50 = sp.GRID.index(0.25), sp.GRID.index(0.75)
CRITICAL_250 = sp.CRITICAL_VALUES[250]


def _load(name: str):
    spec = importlib.util.spec_from_file_location(f"{name}_script", REPO / "scripts" / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[f"{name}_script"] = module
    spec.loader.exec_module(module)
    return module


def committed_declaration() -> dict:
    """The declaration, refused unless it is committed and unchanged since `HEAD`."""

    return _load("spread_distribution_634").committed_declaration(DECLARATION)


# -- the pure parts ------------------------------------------------------------------------------------------------


def established_panel(extended: Path, output: Path) -> int:
    """Write `extended` with every cell of a back-filled row blanked except the established series. Returns the rows blanked."""

    with Path(extended).open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        fields = list(reader.fieldnames or [])
        rows = list(reader)
    if "date" not in fields:
        raise ValueError(f"{extended}: no date column")
    blanked = 0
    for row in rows:
        if date.fromisoformat(row["date"]) < backfill.FIRST_PUBLISHED:
            blanked += 1
            for name in fields:
                if name not in ESTABLISHED:
                    row[name] = ""
    with Path(output).open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    return blanked


def require_arm(arm: str, prefix: int) -> None:
    """The with arm needs back-filled rows, the without arm none."""

    if arm not in ARMS:
        raise ValueError(f"an arm is one of {ARMS}, not {arm!r}")
    if (arm == "with") != (prefix > 0):
        raise ValueError(f"the {arm} arm needs {'a' if arm == 'with' else 'no'} back-filled row ({prefix} found)")


def require_same_published_days(published: Sequence[Tuple[date, Mapping]], extended: Sequence[Tuple[date, Mapping]]) -> None:
    """The extended panel's published days are the published panel's, cell for cell, in the candidate's fields."""

    tail = [item for item in extended if item[0] >= backfill.FIRST_PUBLISHED]
    if [day for day, _ in tail] != [day for day, _ in published]:
        raise ValueError("the extended panel's published days are not the published panel's")
    for (day, left), (_, right) in zip(published, tail):
        for name, value in left.items():
            if right.get(name) != value:
                raise ValueError(f"{day}: {name} is {right.get(name)!r} on the extended panel and {value!r} on the published one")


def guarded_fit(fit, posting: Optional[datetime], *, where: str):
    """`fit`, refusing any training frame that holds back-filled values before the posting instant is established."""

    @functools.wraps(fit)
    def wrapped(train_frame, **kwargs):
        first, last = train_frame[0].date, train_frame[-1].date
        fold = ScoredFold(train_start=first, train_end=last, train_rows=len(train_frame), feature_date=last, scored_date=last)
        backfill.require_posting_established([fold], posting, where=where)
        return fit(train_frame, **kwargs)

    return wrapped


def _interval(differences: Sequence[float], level: float = 0.90, draws: int = sp.DRAWS) -> Tuple[float, float]:
    """A two-sided stationary-bootstrap interval of the mean of `differences` (mean block 10, seed 726)."""

    n = len(differences)
    prefix = [0.0]
    for value in differences:
        prefix.append(prefix[-1] + value)
    rng = random.Random(SEED)
    means = []
    for _ in range(draws):
        starts, ends = sp._segments(metrics.stationary_bootstrap_indices(n, sp.BLOCK_LENGTH, rng), n)
        means.append(sum(prefix[e] - prefix[s] for s, e in zip(starts, ends)) / n)
    means.sort()
    tail = (1.0 - level) / 2.0
    return means[int(math.floor(tail * draws))], means[min(draws - 1, int(math.ceil((1.0 - tail) * draws)) - 1)]


def _coverage(forecasts, outcomes, calendar) -> Dict[str, Dict[date, float]]:
    position = {day: k for k, day in enumerate(calendar)}
    out = {"inside_90": {}, "inside_50": {}, "above_95": {}}
    for day, leads in forecasts.items():
        cells = []
        for h in sp.HORIZONS:
            y = outcomes.get(calendar[position[day] + h])
            if y is not None:
                cells.append((leads[h], y))
        out["inside_90"][day] = sum(q[LOW90] <= y <= q[HIGH90] for q, y in cells) / len(cells)
        out["inside_50"][day] = sum(q[LOW50] <= y <= q[HIGH50] for q, y in cells) / len(cells)
        out["above_95"][day] = sum(y > q[HIGH90] for q, y in cells) / len(cells)
    return out


# -- the walks -----------------------------------------------------------------------------------------------------


def panel_command(args) -> int:
    require_unlocked([LAST_TARGET], where="backfill_h5_726")
    committed_declaration()
    blanked = established_panel(args.extended, args.output)
    print(json.dumps({"blanked_rows": blanked, "panel_sha256": panel_sha256(args.output)}))
    return 0


def forecasts_command(args) -> int:
    declared = committed_declaration()
    sd = _load("spread_distribution_634")
    h = args.horizon
    if h not in sd.HORIZONS:
        raise SystemExit(f"a lead is one of {sd.HORIZONS}")
    require_unlocked([LAST_TARGET], where="backfill_h5_726")
    rows = [row for row in load_daily_panel(args.panel) if row.date <= LAST_TARGET]
    audit_panel([row for row in rows if row.date >= backfill.FIRST_PUBLISHED])
    dates = [row.date for row in rows]
    prefix = backfill.prefix_length(dates)
    require_arm(args.arm, prefix)
    published = [row for row in load_daily_panel(args.published) if row.date <= LAST_TARGET]
    features = tuple(declared["candidate"]["features"])
    require_same_published_days(
        [(row.date, {name: row.values.get(name) for name in features if name != "spread_bps"}) for row in published],
        [(row.date, {name: row.values.get(name) for name in features if name != "spread_bps"}) for row in rows],
    )
    posting = backfill.load_posting_instant(POSTING)
    registry = json.loads(sd.SOURCES.read_text(encoding="utf-8"))
    live = sd._load("live_record")
    lead_features = tuple(live.published_features(h))
    minimum = sd.committed_declaration()["scoring"]["minimum_history"]
    fit = functools.partial(
        ml.fit_gradient_boosted_quantiles, regressors=tuple(f for f in lead_features if f != "spread_bps"), levels=sd.GRID
    )
    fit = guarded_fit(fit, posting, where="backfill_h5_726")
    result, levels, settings = sd.walk(
        rows, fit=fit, features=lead_features, online_calibration=None, registry=registry, horizon=h,
        minimum_history=minimum + prefix, refit_every=21, expected_levels=sd.GRID,
    )
    rule = InformationRule(registry, lead_features, decision_time=sd.DECISION, horizon=h)
    folds = [
        ScoredFold(
            train_start=dates[0], train_end=dates[index], train_rows=index + 1,
            feature_date=dates[rule.information_set(dates, index).anchor], scored_date=dates[index],
        )
        for index, _ in result
    ]
    backfill.require_training_only(folds, where="backfill_h5_726")
    laws = {rows[i].date.isoformat(): q for i, q in result}
    document = {
        "issue": 726, "arm": args.arm, "horizon": h, "levels": levels, "panel_sha256": panel_sha256(args.panel),
        "published_panel_sha256": panel_sha256(args.published), "backfilled_rows": prefix,
        "posting_instant": None if posting is None else posting.isoformat(), "features": list(lead_features),
        "first_scored": min(laws), "settings": json.loads(json.dumps(settings, default=str)), "laws": laws,
    }
    args.output.write_text(json.dumps(document, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"arm": args.arm, "horizon": h, "scored": len(laws), "backfilled_rows": prefix}))
    return 0


# -- scoring -------------------------------------------------------------------------------------------------------


def _load_arm(runs: Path, arm: str) -> Dict[int, Dict[date, Optional[List[float]]]]:
    out = {}
    for h in sp.HORIZONS:
        document = json.loads((runs / f"{arm}_h{h}.json").read_text(encoding="utf-8"))
        if document["arm"] != arm or document["horizon"] != h or tuple(document["levels"]) != sp.GRID:
            raise ValueError(f"{arm}_h{h}.json is not the {arm} arm at lead {h} on the protocol's grid")
        out[h] = {date.fromisoformat(d): (None if q is None else [float(v) for v in q]) for d, q in document["laws"].items()}
    return out


def score_command(args) -> int:
    declared = committed_declaration()
    sd = _load("spread_distribution_634")
    require_unlocked([LAST_TARGET], where="backfill_h5_726")
    rows = [row for row in load_daily_panel(args.published) if row.date <= LAST_TARGET]
    audit_panel(rows)
    calendar = [row.date for row in rows]
    position = {day: k for k, day in enumerate(calendar)}
    outcomes = {row.date: row.spread_bps for row in rows}
    splits = load_split_declaration(sd.SPLITS)
    registry = json.loads(sd.SOURCES.read_text(encoding="utf-8"))
    decisions, day_sets = {}, {}
    for arm in ARMS:
        decisions[arm], day_sets[arm] = sd.lead_forecasts(_load_arm(args.runs, arm), calendar)
    if day_sets["without"] != day_sets["with"]:
        raise ValueError("the arms score different decision days")
    days = [
        day for day in day_sets["without"]
        if all(decisions[a][day][h] is not None for a in ARMS for h in sp.HORIZONS) and calendar[position[day] + 5] <= LAST_TARGET
    ]
    dropped = len(day_sets["without"]) - len(days)
    sd.refuse_locked(days + [calendar[position[d] + h] for d in days for h in sp.HORIZONS])
    b1 = pb.forecasts(pb.b1_forecast, rows, days, registry=registry, decision_time=sd.DECISION)
    forecasts = {arm: {d: decisions[arm][d] for d in days} for arm in ARMS}
    forecasts["B1"] = b1
    crps = {name: sp.day_scores(f, outcomes, calendar) for name, f in forecasts.items()}
    tw = {name: sp.day_scores(f, outcomes, calendar, score=sp.upper_tail_twcrps) for name, f in forecasts.items()}
    cover = {name: _coverage(f, outcomes, calendar) for name, f in forecasts.items() if name != "B1"}

    groups: Dict[str, List[date]] = {"pooled": days}
    for day in days:
        groups.setdefault(f"regime {splits.regime(day)}", []).append(day)
    for day in days:
        target = rows[position[day] + 1]
        groups.setdefault(f"type {splits.reporting_day_type(target.date, target.values)}", []).append(day)

    def paired(test) -> dict:
        draws = test.mean_difference_draws
        return {
            "n": test.n, "mean_d": test.mean_difference, "lower_95_one_sided": test.lower_mean_difference(),
            "lower_with_250_day_critical_value": test.lower_bound(CRITICAL_250),
            "interval_90": [draws[int(0.05 * test.draws)], draws[int(0.95 * test.draws) - 1]],
            "skill": test.skill, "p_value": test.p_value,
        }

    def tests(group: List[date]) -> dict:
        sub = lambda scores: {d: scores[d] for d in group}  # noqa: E731
        main, twc, s_without, s_with = sp.paired_tests(
            [
                (sub(crps["without"]), sub(crps["with"])), (sub(tw["without"]), sub(tw["with"])),
                (sub(crps["B1"]), sub(crps["without"])), (sub(crps["B1"]), sub(crps["with"])),
            ],
            seed=SEED,
        )
        result = {
            "days": len(group),
            "crps": {arm: sum(crps[arm][d] for d in group) / len(group) for arm in ("without", "with", "B1")},
            "crps_without_minus_with": paired(main),
            "twcrps_without_minus_with": paired(twc),
            "skill_vs_B1": {"without": paired(s_without), "with": paired(s_with)},
            "calibration": {},
        }
        for measure in ("inside_90", "inside_50", "above_95"):
            a = [cover["without"][measure][d] for d in group]
            b = [cover["with"][measure][d] for d in group]
            moves = [y - x for x, y in zip(a, b)]
            result["calibration"][measure] = {
                "without": sum(a) / len(a), "with": sum(b) / len(b), "move": sum(moves) / len(moves),
                "interval_90": list(_interval(moves)),
            }
        return result

    table = {name: tests(group) for name, group in groups.items() if len(group) > sp.HAC_LAG}
    headline = table["regime 2018-19"]["crps_without_minus_with"]
    cost = {
        name: entry["crps_without_minus_with"]["interval_90"][1] < 0.0
        for name, entry in table.items() if name != "regime 2018-19"
    }
    document = {
        "issue": 726, "declaration": str(DECLARATION.relative_to(REPO)),
        "published_panel_sha256": panel_sha256(args.published),
        "decision_days": [days[0].isoformat(), days[-1].isoformat(), len(days)], "dropped_decision_days": dropped,
        "reading": {
            "moves_2018_19_beyond_interval": headline["lower_95_one_sided"] > 0.0,
            "costs_elsewhere": sorted(name for name, flag in cost.items() if flag),
        },
        "groups": table,
    }
    args.output.write_text(json.dumps(document, indent=1) + "\n", encoding="utf-8")
    args.markdown.write_text(markdown(document), encoding="utf-8")
    print(json.dumps({"days": len(days), "reading": document["reading"]}))
    return 0


def _f(value: float, digits: int = 3) -> str:
    return f"{value:+.{digits}f}"


def markdown(document: dict) -> str:
    lines = [
        "# H4 step 3: the back-fill against H5's candidate (#726), development days\n",
        f"Decision days {document['decision_days'][0]} to {document['decision_days'][1]} ({document['decision_days'][2]}); "
        f"{document['dropped_decision_days']} dropped. d = CRPS(without) - CRPS(with), positive when the history helps.\n",
        "| group | days | CRPS without | CRPS with | mean d | one-sided 95% lower | lower (c = 5.455) | 90% interval | skill vs B1 without | with |",
        "|---|---|---|---|---|---|---|---|---|---|",
    ]
    for name, e in document["groups"].items():
        m = e["crps_without_minus_with"]
        lines.append(
            f"| {name} | {e['days']} | {e['crps']['without']:.3f} | {e['crps']['with']:.3f} | {_f(m['mean_d'])} | "
            f"{_f(m['lower_95_one_sided'])} | {_f(m['lower_with_250_day_critical_value'])} | "
            f"[{_f(m['interval_90'][0])}, {_f(m['interval_90'][1])}] | {e['skill_vs_B1']['without']['skill']:+.1%} | "
            f"{e['skill_vs_B1']['with']['skill']:+.1%} |"
        )
    lines += ["", "Upper-tail twCRPS d (without - with):", "", "| group | mean d | one-sided 95% lower | 90% interval |", "|---|---|---|---|"]
    for name, e in document["groups"].items():
        m = e["twcrps_without_minus_with"]
        lines.append(f"| {name} | {_f(m['mean_d'], 4)} | {_f(m['lower_95_one_sided'], 4)} | [{_f(m['interval_90'][0], 4)}, {_f(m['interval_90'][1], 4)}] |")
    lines += ["", "Coverage, with minus without (mean of paired daily differences, 90% interval):", "",
              "| group | measure | without | with | move | 90% interval |", "|---|---|---|---|---|---|"]
    for name, e in document["groups"].items():
        for measure, c in e["calibration"].items():
            lines.append(f"| {name} | {measure} | {c['without']:.3f} | {c['with']:.3f} | {_f(c['move'])} | [{_f(c['interval_90'][0])}, {_f(c['interval_90'][1])}] |")
    lines += ["", f"Reading: {json.dumps(document['reading'])}", ""]
    return "\n".join(lines)


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="command", required=True)
    p = sub.add_parser("panel", help="blank every cell of a back-filled row except the established series")
    p.add_argument("--extended", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True)
    p.set_defaults(func=panel_command)
    p = sub.add_parser("forecasts", help="walk the candidate in one arm at one lead")
    p.add_argument("--arm", choices=ARMS, required=True)
    p.add_argument("--panel", type=Path, required=True)
    p.add_argument("--published", type=Path, required=True)
    p.add_argument("--horizon", type=int, required=True)
    p.add_argument("--output", type=Path, required=True)
    p.set_defaults(func=forecasts_command)
    p = sub.add_parser("score", help="pair the arms and report")
    p.add_argument("--published", type=Path, required=True)
    p.add_argument("--runs", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True)
    p.add_argument("--markdown", type=Path, required=True)
    p.set_defaults(func=score_command)
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
