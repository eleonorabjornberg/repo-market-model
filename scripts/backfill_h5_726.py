"""Does the 2014-2018 back-fill move H5's development score? (#726, H4 step 3)

A scratch measurement, not a record: it writes CSV, JSON and Markdown to the paths it is given and nothing into
`docs/runs/`. Exploration on development data: under scoring protocol v1 (#640) such data never gives a verdict.
Every choice is in `metadata/backfill_h5_726.json`, which this script refuses to read unless it is committed and
unchanged. No day after 2025-12-31 is read (`docs/decisions/lockbox.md`; `spread_distribution_634.refuse_locked`, and
`scoring_protocol.day_scores`).

H5's candidate is #634's `gbm_funding` (declared in `metadata/backfill_h5_726.json`). It is walked twice by
`scripts/spread_distribution_634.py`'s own `walk`, unchanged: on the published panel (the `without` arm, #634's control)
and on the published panel with the 899 back-filled rows before it (the `with` arm). A back-filled row carries only the
series `metadata/backfill_posting.json` admits (`kept_columns`; #742); every other cell is blank, which the fitter reads
through its fitted imputation. `forecasts` refuses an extended panel whose back-filled rows carry an unadmitted column
(`require_backfilled_admitted`, #870). Every fit of the with arm passes `backfill.require_posting_established` with the
instant of that file, the scored folds pass `backfill.require_training_only`, and the series the fits read from
back-filled rows pass `backfill.require_series_admitted`.

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
import subprocess
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
from repo_model.splits import LookAheadError  # noqa: E402

DECLARATION = REPO / "metadata" / "backfill_h5_726.json"
REREAD = REPO / "metadata" / "backfill_h5_726_reread.json"
POSTING = REPO / "metadata" / "backfill_posting.json"
SEED = 726
LAST_TARGET = date(2025, 12, 31)
ARMS = ("without", "with")
LOW90, HIGH90 = sp.GRID.index(0.05), sp.GRID.index(0.95)
LOW50, HIGH50 = sp.GRID.index(0.25), sp.GRID.index(0.75)
CRITICAL_250 = sp.CRITICAL_VALUES[sp.GRID_COMPARISON][250]


def _load(name: str):
    spec = importlib.util.spec_from_file_location(f"{name}_script", REPO / "scripts" / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[f"{name}_script"] = module
    spec.loader.exec_module(module)
    return module


def committed_declaration(path: Path = DECLARATION) -> dict:
    """A declaration (default: #759's), refused unless it is committed and unchanged since `HEAD`."""

    relative = str(Path(path).resolve().relative_to(REPO))
    dirty = subprocess.run(
        ["git", "status", "--porcelain", "--", relative], cwd=REPO, capture_output=True, text=True, check=True
    ).stdout.strip()
    if dirty:
        raise SystemExit(f"{relative} is not committed ({dirty}); a declaration is made before any score")
    return json.loads(Path(path).read_text(encoding="utf-8"))


# -- the pure parts ------------------------------------------------------------------------------------------------


def kept_columns(fields: Sequence[str], admitted: Mapping[str, datetime]) -> List[str]:
    """The columns a back-filled row keeps: the date, the calendar, IORB (an administered rate) and every admitted series.

    The admitted list is `metadata/backfill_posting.json`'s (#742), not a copy of it (#862).
    """

    return [
        name for name in fields
        if name == "date" or name in backfill.NOT_A_SERIES or (
            backfill.series_read([name]) and not backfill.unadmitted_columns([name], admitted)
        )
    ]


def require_backfilled_admitted(rows: Sequence, admitted: Mapping[str, datetime], *, where: str) -> None:
    """Refuse an extended panel whose back-filled rows carry a value of a series that is not admitted (#862).

    Raises:
        LookAheadError: a back-filled row holds a non-blank cell of an unadmitted column.
    """

    seen = sorted({name for row in rows if row.date < backfill.FIRST_PUBLISHED for name, value in row.values.items() if value is not None})
    bad = backfill.unadmitted_columns(seen, admitted)
    if bad:
        raise LookAheadError(
            f"{where}: back-filled rows carry values of {bad}, which are not admitted; only {sorted(admitted)} are "
            f"(metadata/backfill_posting.json, #742)"
        )


def series_carried(features: Sequence[str], rows: Sequence) -> Tuple[str, ...]:
    """The back-fill series a model reading `features` draws from the back-filled rows that carry a value of them."""

    carried = {name for row in rows if row.date < backfill.FIRST_PUBLISHED for name, value in row.values.items() if value is not None}
    return backfill.series_read([f for f in features if f in carried or f in backfill.contract.DERIVED_FEATURES])


def established_panel(extended: Path, output: Path, admitted: Mapping[str, datetime]) -> int:
    """Write `extended` with every cell of a back-filled row blanked except the admitted series. Returns the rows blanked."""

    with Path(extended).open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        fields = list(reader.fieldnames or [])
        rows = list(reader)
    if "date" not in fields:
        raise ValueError(f"{extended}: no date column")
    blanked = 0
    kept = set(kept_columns(fields, admitted))
    for row in rows:
        if date.fromisoformat(row["date"]) < backfill.FIRST_PUBLISHED:
            blanked += 1
            for name in fields:
                if name not in kept:
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


def refit_record(train_frame: Sequence, inputs: Sequence[str]) -> dict:
    """What one refit trained on: its rows, the back-filled share of them and the share of its input cells that are blank (#870)."""

    rows = len(train_frame)
    back = sum(1 for row in train_frame if row.date < backfill.FIRST_PUBLISHED)
    blank = sum(1 for row in train_frame for name in inputs if row.values.get(name) is None)
    return {
        "train_start": train_frame[0].date.isoformat(), "train_end": train_frame[-1].date.isoformat(), "train_rows": rows,
        "backfilled_rows": back, "backfilled_share": back / rows,
        "imputed_cells": blank, "imputed_share": blank / (rows * len(inputs)) if inputs else 0.0,
    }


def guarded_fit(fit, posting: Optional[datetime], *, where: str, log: Optional[list] = None, inputs: Sequence[str] = ()):
    """`fit`, refusing any training frame that holds back-filled values before the posting instant is established.

    With `log`, each refit's `refit_record` over `inputs` is appended to it, in fit order.
    """

    @functools.wraps(fit)
    def wrapped(train_frame, **kwargs):
        first, last = train_frame[0].date, train_frame[-1].date
        fold = ScoredFold(train_start=first, train_end=last, train_rows=len(train_frame), feature_date=last, scored_date=last)
        backfill.require_posting_established([fold], posting, where=where)
        if log is not None:
            log.append(refit_record(train_frame, inputs))
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
    blanked = established_panel(args.extended, args.output, backfill.load_admitted_series(POSTING))
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
    admitted = backfill.load_admitted_series(POSTING)
    require_backfilled_admitted(rows, admitted, where="backfill_h5_726")
    registry = json.loads(sd.SOURCES.read_text(encoding="utf-8"))
    live = sd._load("live_record")
    lead_features = tuple(live.published_features(h))
    minimum = json.loads(sd.DECLARATION.read_text(encoding="utf-8"))["scoring"]["minimum_history"]
    regressors = tuple(f for f in lead_features if f != "spread_bps")
    fit = functools.partial(ml.fit_gradient_boosted_quantiles, regressors=regressors, levels=sd.GRID)
    refits: list = []
    fit = guarded_fit(fit, posting, where="backfill_h5_726", log=refits, inputs=regressors)
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
    backfill.require_series_admitted(folds, series_carried(lead_features, rows), admitted, where="backfill_h5_726")
    laws = {rows[i].date.isoformat(): q for i, q in result}
    blocks = list(sd.refit_blocks(sd.fold_grid(dates, registry, decision_time=sd.DECISION, minimum_history=minimum + prefix, horizon=h), 21))
    if len(blocks) != len(refits) or [i for block in blocks for i in block] != [i for i, _ in result]:
        raise ValueError("the refit blocks are not the walk's blocks")
    refit_of_day = {rows[i].date.isoformat(): k for k, block in enumerate(blocks) for i in block}
    document = {
        "issue": 726, "arm": args.arm, "horizon": h, "levels": levels, "panel_sha256": panel_sha256(args.panel),
        "published_panel_sha256": panel_sha256(args.published), "backfilled_rows": prefix,
        "posting_instant": None if posting is None else posting.isoformat(), "features": list(lead_features),
        "first_scored": min(laws), "refits": refits, "refit_of_day": refit_of_day, "settings": json.loads(json.dumps(settings, default=str)), "laws": laws,
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


# -- the re-read (#870) --------------------------------------------------------------------------------------------


def period_label(day: date) -> Optional[str]:
    """The half-year of a decision day inside 2018-19, else `None`."""

    if day.year not in (2018, 2019):
        return None
    return f"{day.year} H{1 if day.month <= 6 else 2}"


def ruled_interval(test, level: float = 0.90) -> Tuple[float, float]:
    """The two-sided studentized interval of mean(d) (ruling 1): `mean - Q_hi(t) * se` to `mean - Q_lo(t) * se`."""

    tail = (1.0 - level) / 2.0
    lower = test.mean_difference - sp._bound(test.t_draws, 1.0 - tail, test.draws) * test.standard_error
    upper = test.mean_difference - sp._bound(test.t_draws, tail, test.draws) * test.standard_error
    return lower, upper


def group_entry(test, shares: Mapping[str, float]) -> dict:
    """One group's figures: the ruled interval, the superseded percentile interval, the reference bounds, the refit shares."""

    draws = test.mean_difference_draws
    lower, upper = ruled_interval(test)
    mean, se = test.mean_difference, test.standard_error
    return {
        "days": test.n, "mean_d": mean, "se": se, "lower_95_one_sided": lower, "interval_90": [lower, upper],
        "percentile_interval_90": [draws[int(0.05 * test.draws)], draws[int(0.95 * test.draws) - 1]],
        "reference_c": CRITICAL_250, "mean_minus_c_se": mean - CRITICAL_250 * se, "mean_plus_c_se": mean + CRITICAL_250 * se,
        "gain": lower > 0.0, "cost": upper < 0.0, "cost_at_c": mean + CRITICAL_250 * se < 0.0,
        "mean_backfilled_share": shares["backfilled"], "mean_imputed_share": shares["imputed"],
    }


def reading(entry: Optional[dict]) -> str:
    """Whether a group shows a gain, a cost or neither on the ruled interval, in words."""

    if entry is None:
        return "not tested (too few decision days)"
    if entry["gain"]:
        return "gain shown"
    if entry["cost"]:
        return "cost shown"
    return "neither shown (the interval covers zero)"


def reread_command(args) -> int:
    declared = committed_declaration(REREAD)
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
    sd.refuse_locked(days + [calendar[position[d] + h] for d in days for h in sp.HORIZONS])
    crps = {arm: sp.day_scores({d: decisions[arm][d] for d in days}, outcomes, calendar) for arm in ARMS}
    documents = {h: json.loads((args.runs / f"with_h{h}.json").read_text(encoding="utf-8")) for h in sp.HORIZONS}
    refit_shares: Dict[date, Dict[str, float]] = {}
    for day in days:
        cells = []
        for h in sp.HORIZONS:
            record = documents[h]["refits"][documents[h]["refit_of_day"][calendar[position[day] + h].isoformat()]]
            cells.append(record)
        refit_shares[day] = {
            "backfilled": max(c["backfilled_share"] for c in cells), "imputed": sum(c["imputed_share"] for c in cells) / len(cells),
        }
    primary = float(declared["mostly_imputed_fits"]["primary_share"])
    ladder = [primary] + [float(x) for x in declared["mostly_imputed_fits"]["sensitivity_shares"]]

    groups: Dict[str, List[date]] = {"pooled": list(days)}
    for day in days:
        groups.setdefault(f"regime {splits.regime(day)}", []).append(day)
        label = period_label(day)
        if label is not None:
            groups.setdefault(f"period {label}", []).append(day)
            groups.setdefault(f"period {day.year}", []).append(day)
    for day in days:
        target = rows[position[day] + 1]
        groups.setdefault(f"type {splits.reporting_day_type(target.date, target.values)}", []).append(day)
    for share in ladder:
        inside = [d for d in days if refit_shares[d]["backfilled"] <= share]
        outside = [d for d in days if refit_shares[d]["backfilled"] > share]
        groups[f"share <= {share:.0%}: pooled"] = inside
        groups[f"share > {share:.0%}: pooled"] = outside
        for day in inside:
            groups.setdefault(f"share <= {share:.0%}: regime {splits.regime(day)}", []).append(day)
    for name in ("period 2018 H1", "period 2018 H2", "period 2019 H1", "period 2019 H2", "period 2018", "period 2019"):
        groups.setdefault(name, [])

    def mean_share(group: List[date], key: str) -> float:
        return sum(refit_shares[d][key] for d in group) / len(group) if group else float("nan")

    table: Dict[str, Optional[dict]] = {}
    sizes: Dict[str, int] = {}
    for name, group in groups.items():
        sizes[name] = len(group)
        if len(group) <= sp.HAC_LAG:
            table[name] = None
            continue
        (test,) = sp.paired_tests(
            [({d: crps["without"][d] for d in group}, {d: crps["with"][d] for d in group})], seed=SEED, with_skill=False
        )
        entry = group_entry(test, {"backfilled": mean_share(group, "backfilled"), "imputed": mean_share(group, "imputed")})
        entry["crps"] = {arm: sum(crps[arm][d] for d in group) / len(group) for arm in ARMS}
        table[name] = entry

    refit_table = [
        dict(record, lead=1) for record in documents[1]["refits"]
    ]
    lines = []
    for label, names in (
        ("2018-19, all days", ["regime 2018-19"]),
        ("2018-19 by half-year", ["period 2018 H1", "period 2018 H2", "period 2019 H1", "period 2019 H2"]),
        ("2019 alone", ["period 2019"]),
        ("2018-19 on days at or under each declared share", [f"share <= {s:.0%}: regime 2018-19" for s in ladder]),
        ("every other regime and the pooled sample, for a cost", [n for n in table if n.startswith("regime ") and n != "regime 2018-19"] + ["pooled"]),
    ):
        lines.append({"reading": label, "groups": {n: reading(table.get(n)) for n in names}})
    document = {
        "issue": 870, "declaration": str(REREAD.relative_to(REPO)), "published_panel_sha256": panel_sha256(args.published),
        "extended_panel_sha256": documents[1]["panel_sha256"], "backfilled_rows": documents[1]["backfilled_rows"],
        "decision_days": [days[0].isoformat(), days[-1].isoformat(), len(days)], "shares_ladder": ladder,
        "group_sizes": sizes, "groups": table, "kill_lines": lines, "refits_lead_1": refit_table,
    }
    args.output.write_text(json.dumps(document, indent=1) + "\n", encoding="utf-8")
    args.markdown.write_text(reread_markdown(document), encoding="utf-8")
    print(json.dumps({"days": len(days), "kill_lines": lines}))
    return 0


def reread_markdown(document: dict) -> str:
    c = CRITICAL_250
    lines = [
        "# H4 step 3 re-read: the back-fill against H5's candidate on the ruled interval (#870), development days, not a verdict\n",
        f"Decision days {document['decision_days'][0]} to {document['decision_days'][1]} ({document['decision_days'][2]}). "
        "d = CRPS(without) - CRPS(with), positive when the back-fill helps. Interval: the studentized stationary bootstrap "
        f"(ruling 1), two-sided 90%. Reference value c = {c:.3f} (the 250-day value of the grid comparison): `mean - c se` and "
        "`mean + c se` carry both orientations of #830 (d = without - with, or the reverse).\n",
        "| group | days | CRPS without | CRPS with | mean d | se | studentized 90% interval | percentile 90% (superseded) | mean - c se | mean + c se | back-filled share | imputed cells | reading |",
        "|---|---|---|---|---|---|---|---|---|---|---|---|---|",
    ]
    for name, entry in document["groups"].items():
        n = document["group_sizes"][name]
        if entry is None:
            lines.append(f"| {name} | {n} | | | | | | | | | | | {reading(None)} |")
            continue
        lo, hi = entry["interval_90"]
        plo, phi = entry["percentile_interval_90"]
        lines.append(
            f"| {name} | {n} | {entry['crps']['without']:.3f} | {entry['crps']['with']:.3f} | {_f(entry['mean_d'])} | {entry['se']:.4f} | "
            f"[{_f(lo)}, {_f(hi)}] | [{_f(plo)}, {_f(phi)}] | {_f(entry['mean_minus_c_se'])} | {_f(entry['mean_plus_c_se'])} | "
            f"{entry['mean_backfilled_share']:.0%} | {entry['mean_imputed_share']:.0%} | {reading(entry)} |"
        )
    lines += ["", "## Training frames of the with arm (lead 1), by half-year of the refit", "",
              "| half-year | refits | back-filled share of rows (min to max) | imputed share of input cells (min to max) |", "|---|---|---|---|"]
    byhalf: Dict[str, List[dict]] = {}
    for r in document["refits_lead_1"]:
        year, month = r["train_end"][:4], int(r["train_end"][5:7])
        byhalf.setdefault(f"{year} H{1 if month <= 6 else 2}", []).append(r)
    for label, rs in sorted(byhalf.items()):
        b = [r["backfilled_share"] for r in rs]
        i = [r["imputed_share"] for r in rs]
        lines.append(f"| {label} | {len(rs)} | {min(b):.0%} to {max(b):.0%} | {min(i):.0%} to {max(i):.0%} |")
    lines += ["", "## Readings against H4's kill clause (development, not a verdict; whether the kill is read is Eleonora's)", ""]
    for line in document["kill_lines"]:
        lines.append(f"- **{line['reading']}.** " + "; ".join(f"{n}: {r}" for n, r in line["groups"].items()))
    lines.append("")
    return "\n".join(lines)


def _f(value: float, digits: int = 3) -> str:
    return f"{value:+.{digits}f}"


def markdown(document: dict) -> str:
    lines = [
        "# H4 step 3: the back-fill against H5's candidate (#726), development days\n",
        f"Decision days {document['decision_days'][0]} to {document['decision_days'][1]} ({document['decision_days'][2]}); "
        f"{document['dropped_decision_days']} dropped. d = CRPS(without) - CRPS(with), positive when the history helps.\n",
        f"| group | days | CRPS without | CRPS with | mean d | one-sided 95% lower | lower (c = {CRITICAL_250:.3f}) | 90% interval | skill vs B1 without | with |",
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
    p = sub.add_parser("reread", help="the re-read of #870: the ruled interval, 2018-19 by half-year, the share of back-filled rows")
    p.add_argument("--published", type=Path, required=True)
    p.add_argument("--runs", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True)
    p.add_argument("--markdown", type=Path, required=True)
    p.set_defaults(func=reread_command)
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
