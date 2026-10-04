#!/usr/bin/env python3
"""Onset post-mortem (#214): every pre-2026 onset, its calendar, scarcity state and both forecasts.

**Descriptive only. No new model, no win rule, no claim; it decides nothing.**
It shows what the calendar, the reserve-scarcity gauge and the two forecasts
looked like on the days pressure started. Nothing is written to `docs/runs/`,
and no published record, declaration, page or generated block changes.

The onsets, each #209's definition as merged in `repo_model.onset`:

- **primary:** `onset.onset_flags`, the events of `onset.GROUP_ONSET`: the
  first day above +5 bp after `onset.ONSET_CALM_DAYS` calm panel days at or
  below +5 bp;
- **descriptive:** the events of `onset.GROUP_ONSET_ONE_DAY`
  (`onset.one_day_at_risk_flags`), the first day above +5 bp after one calm
  panel day (#160's definition).

"Above +5 bp" is `data.exceeds_bp(spread, onset.ONSET_THRESHOLD_BP)`, the test
`onset` uses. Onsets are listed on the scored days of the published fold grid
(minimum history 61, through `--end`).

Per onset, every read is the forecast's own, at its h = 1 decision instant,
through `baseline._as_of_folds` (lockbox, leakage and staleness guards):

- the calendar: `quarter_end`, `tax_date` and `days_to_month_end` (calendar
  columns, read at the scored day), with month-end as
  `metadata/evaluation_splits.json`'s window, and the pressure-day type its
  precedence gives (`SplitDeclaration.day_type`); the coupon settlement
  `treasury_settlement_coupons > 0` (a scheduled input, read at the scored day,
  as `asof._settlement_day` reads it);
- `reserve_scarcity_state` (#115, `scarcity.with_reserve_scarcity_state`, its
  merged cut-points), read as-of, with its label (`scarcity.STATE_LABELS`);
- pressure model v1's probability of the +5 bp event, exactly as
  `scripts/pressure_model_v1.py publish --horizon 1` scores
  `docs/runs/pressure_model_v1_h1.json` (#169), recalibrated out of fold, and
  the persistence-logistic's, from the same walk-forward run on the same fold
  grid.

The lead of the gauge is counted on the as-of state of every panel day the rule
can read (`_as_of_folds` from the first day the state is public at a decision,
`gauge_history`, rather than from the first scored day): the
panel days from the first day of the uninterrupted run of states 2-3 that holds
the onset day to the onset day. A day with no state ends a run. A run that
starts on the series' first day, the first day the gauge can be read, is
censored there ("at the panel start").

The panel is built from tracked fixtures only (`scripts/scarcity_validation.py`'s
`build_measurement_panel`, which refuses unless the published columns reproduce
the published digest); v1 and the persistence-logistic read the published
columns only. The run checks that it reproduces the published record (the
+20 and +50 bp event lists' per-day probabilities, both models' +5 bp Brier
score, the fold count) and stops if it does not.

    PYTHONPATH=src /opt/rmm-venv/bin/python scripts/onset_post_mortem.py --end 2025-12-31 \
        [--forecasts CACHE.json] [--json OUT.json] [--markdown OUT.md]

`--forecasts` caches the two models' probabilities (the slow step): read when
the file exists, written when it does not. An `--end` on or after 2026-01-01
is refused by the lockbox guard (`lockbox.require_unlocked`).
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import math
import sys
import tempfile
from datetime import date, time
from pathlib import Path
from typing import Dict, List, Mapping, Optional, Sequence

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))

from repo_model import onset  # noqa: E402
from repo_model.asof import InformationRule  # noqa: E402
from repo_model.baseline import _as_of_folds  # noqa: E402
from repo_model.data import exceeds_bp  # noqa: E402
from repo_model.evaluation_splits import load_split_declaration  # noqa: E402
from repo_model.lockbox import require_unlocked  # noqa: E402
from repo_model.scarcity import (  # noqa: E402
    RESERVE_SCARCITY_STATE,
    STATE_LABELS,
    measurement_declaration,
    with_reserve_scarcity_state,
)

REGISTRY = REPO / "metadata" / "sources.json"
SPLITS = REPO / "metadata" / "evaluation_splits.json"
RECORD = REPO / "docs" / "runs" / "pressure_model_v1_h1.json"
HORIZON = 1
TAU_BP = 5.0
#: The published fold grid's minimum history (`pressure_model_v1.MINIMUM_HISTORY`).
MINIMUM_HISTORY = 61
V1 = "distributional_gbm+recalibrated"
PERSISTENCE = "persistence_logistic"
CALENDAR = ("quarter_end", "tax_date", "days_to_month_end")
COUPONS = "treasury_settlement_coupons"
#: The two episodes whose first onset the gauge's lead is reported for.
EPISODES = (
    ("2018-19", date(2018, 6, 29), date(2019, 12, 31)),
    ("2025", date(2025, 1, 1), date(2025, 12, 31)),
)
PRIMARY = "primary"
DESCRIPTIVE = "descriptive"
DEFINITIONS = {
    PRIMARY: (
        onset.GROUP_ONSET,
        "#209's at-risk definition (onset.onset_flags): the first day above +5 bp "
        "after five calm panel days at or below +5 bp",
    ),
    DESCRIPTIVE: (
        onset.GROUP_ONSET_ONE_DAY,
        "#209's one-day version (onset.one_day_at_risk_flags; #160): the first day "
        "above +5 bp after one calm panel day",
    ),
}


def _script(name: str):
    spec = importlib.util.spec_from_file_location(name, REPO / "scripts" / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


# -- the as-of reads ----------------------------------------------------------


def _rule(registry, decision_time: time) -> InformationRule:
    return InformationRule(
        registry,
        ("spread_bps", RESERVE_SCARCITY_STATE, *CALENDAR, COUPONS),
        decision_time=decision_time,
        horizon=HORIZON,
    )


def gauge_history(rows, registry, *, decision_time: time) -> int:
    """The minimum history at which the fold grid starts on the gauge's first readable day.

    The state is first public about ten panel days into the panel (the H.8
    lag), so the gauge's own series cannot start on its first row. This is the
    smallest minimum history whose grid's first day has every read of
    `as_of_reads` admissible: the first day the gauge can be read as-of.
    """

    from repo_model.asof import fold_grid
    from repo_model.splits import SplitError

    rule = _rule(registry, decision_time)
    dates = [row.date for row in rows]
    history = 1
    while True:
        grid = fold_grid(
            dates, registry, decision_time=decision_time, minimum_history=history, horizon=HORIZON
        )
        try:
            rule.information_set(dates, grid[0])
            return history
        except SplitError:
            history += 1


def as_of_reads(rows, registry, *, decision_time: time, minimum_history: int, end: date) -> Dict[date, dict]:
    """Per scored day, the state, calendar and settlement its h = 1 forecast could read.

    `rows` carry `reserve_scarcity_state` (`with_reserve_scarcity_state`) and the
    measurement declaration is in force. The lockbox is checked on the whole
    grid before anything is read (`_as_of_folds`), so an `end` on or after
    2026-01-01 raises `LookAheadError`.
    """

    rule = _rule(registry, decision_time)
    out: Dict[date, dict] = {}
    for fold in _as_of_folds(
        rows,
        rule,
        minimum_history=minimum_history,
        refit_every=len(rows),
        entry="onset_post_mortem.as_of_reads",
        end=end,
    ):
        (state_read,) = [r for r in fold.info.reads if r.feature == RESERVE_SCARCITY_STATE]
        values = fold.feature_row.values
        state = values.get(RESERVE_SCARCITY_STATE)
        out[rows[fold.index].date] = {
            "index": fold.index,
            "state": None if state is None else int(state),
            "state_read_date": rows[state_read.row].date,
            **{column: values.get(column) for column in (*CALENDAR, COUPONS)},
        }
    return out


# -- the onsets ---------------------------------------------------------------


def onset_days(rows, scored_dates: Sequence[date], declaration) -> Dict[str, List[date]]:
    """The onset days of each definition, on `scored_dates`, as `onset.day_groups` gives them."""

    require_unlocked(scored_dates, where="onset_post_mortem.onset_days")
    groups = onset.day_groups(rows, scored_dates, declaration)
    position = {row.date: index for index, row in enumerate(rows)}
    out = {}
    for name, (group, _text) in DEFINITIONS.items():
        out[name] = [
            scored_dates[k]
            for k in groups[group]
            if exceeds_bp(rows[position[scored_dates[k]]].spread_bps, onset.ONSET_THRESHOLD_BP)
        ]
    primary = set(out[PRIMARY])
    by_flags = {
        scored_dates[k] for k in onset.onset_positions(rows, scored_dates)
    }
    if primary != by_flags:  # pragma: no cover - would be a bug in onset
        raise ValueError("onset.day_groups and onset.onset_positions disagree on the onsets")
    return out


def gauge_lead(series: Sequence[date], reads: Mapping[date, dict], day: date) -> Optional[dict]:
    """The lead of the gauge before `day`: the run of states 2-3 that holds it.

    `series` is every panel day of the gauge's as-of series, in order. `None`
    when the day's state is not 2 or 3.
    """

    if reads[day]["state"] not in (2, 3):
        return None
    at = series.index(day)
    start = at
    while start > 0 and reads[series[start - 1]]["state"] in (2, 3):
        start -= 1
    lead = reads[day]["index"] - reads[series[start]]["index"]
    return {"run_start": series[start], "lead_days": lead, "censored": start == 0}


def _lead_text(lead: Optional[dict]) -> str:
    if lead is None:
        return "--"
    if lead["censored"]:
        return f"at least {lead['lead_days']} days (censored at the panel start)"
    return f"{lead['lead_days']}"


# -- the forecasts ------------------------------------------------------------


def v1_and_persistence(panel_path: Path) -> dict:
    """Pressure model v1 and the persistence-logistic at h = 1, as the record scores them.

    `scripts/pressure_model_v1.py publish --horizon 1`, step for step: the gbm
    on the published funding declaration's features, conformal PID with nested
    selection, recalibrated out of fold; the persistence-logistic on the same
    fold grid. Returns every threshold's probabilities per scored day.
    """

    from repo_model import ml, pressure
    from repo_model.baseline import persistence_logistic_exceedance, rolling_exceedance_backtest
    from repo_model.data import audit_panel, load_daily_panel, load_stress_thresholds
    from repo_model.recalibration import NestedFoldPid

    v1 = _script("pressure_model_v1")
    rows = load_daily_panel(panel_path)
    audit_panel(rows)
    splits = load_split_declaration(v1.SPLITS)
    taus = tuple(float(tau) for tau in load_stress_thresholds(v1.THRESHOLDS)["taus_bp"])
    features = v1._at_horizon(v1.GBM_FEATURES, HORIZON)
    registry = json.loads(v1.REGISTRY.read_text())

    def online(rows_, rule):
        return NestedFoldPid(rows_, rule, splits=splits, refit_every=v1.REFIT_EVERY)

    def run(name, predictor, declared, calibration=None):
        return rolling_exceedance_backtest(
            rows,
            predictor=predictor,
            model_name=name,
            features=declared,
            registry=registry,
            decision_time=v1.DECISION,
            taus=taus,
            minimum_history=v1.MINIMUM_HISTORY,
            refit_every=v1.REFIT_EVERY,
            end=v1.END,
            horizon=HORIZON,
            online_calibration=calibration,
        )

    raw = run(
        v1.PUBLISHED,
        ml.gbm_exceedance(
            tuple(name for name in features if name != "spread_bps"),
            minimum_history=v1.MINIMUM_HISTORY,
        ),
        features,
        online,
    )
    model = v1._rescored(pressure.recalibrated(raw))
    persistence = run(
        PERSISTENCE,
        persistence_logistic_exceedance(minimum_history=v1.MINIMUM_HISTORY),
        ("spread_bps",),
    )
    if model.scored_dates != persistence.scored_dates:
        raise ValueError("v1 and the persistence-logistic were not scored on one fold grid")
    out = {"taus": list(taus), "scored_dates": [d.isoformat() for d in model.scored_dates]}
    for report, name in ((model, V1), (persistence, PERSISTENCE)):
        out[name] = {}
        for position, tau in enumerate(taus):
            forecast, _reference, outcomes = report.at_tau(position)
            out[name][f"{tau:g}"] = [float(p) for p in forecast]
        out.setdefault("outcomes", {})
    for position, tau in enumerate(taus):
        out["outcomes"][f"{tau:g}"] = [int(y) for y in model.at_tau(position)[2]]
    out["model_name"] = model.model_name
    return out


def check_against_record(forecasts: dict, record: dict) -> dict:
    """Refuse unless the run reproduces the published record's figures.

    The per-day probabilities of the +20 and +50 bp event lists (each event and
    the days before it), the +5 bp Brier score of v1 and of the
    persistence-logistic, and the fold count. Returns what was compared.
    """

    if forecasts["model_name"] != V1:
        raise ValueError(f"the run's model is {forecasts['model_name']!r}, not {V1!r}")
    index = {when: k for k, when in enumerate(forecasts["scored_dates"])}
    if len(index) != record["folds"]["count"]:
        raise ValueError(f"{len(index)} scored days, the record has {record['folds']['count']}")
    compared, worst = 0, 0.0
    for key, entry in record["metrics"]["by_tau"].items():
        if entry.get("reporting") != "event_list":
            continue
        for event in entry["events"]:
            for item in event["forecasts"]:
                k = index[item["scored_date"]]
                for name in (V1, PERSISTENCE):
                    published = item["probability"][name]
                    ours = forecasts[name][key][k]
                    worst = max(worst, abs(ours - published))
                    compared += 1
    if worst > 1e-12:
        raise ValueError(f"the event-list probabilities differ from the record by up to {worst}")
    five = f"{TAU_BP:g}"
    outcomes = forecasts["outcomes"][five]

    def brier(p):
        return sum((a - y) ** 2 for a, y in zip(p, outcomes)) / len(outcomes)

    briers = {
        V1: (brier(forecasts[V1][five]), record["metrics"]["by_tau"][five]["brier"]),
        PERSISTENCE: (
            brier(forecasts[PERSISTENCE][five]),
            record["benchmarks"][PERSISTENCE]["by_tau"][five]["benchmark_brier"],
        ),
    }
    for name, (ours, published) in briers.items():
        if not math.isclose(ours, published, rel_tol=0.0, abs_tol=1e-12):
            raise ValueError(f"{name}'s +5 bp Brier is {ours}, the record's {published}")
    return {
        "event_list_probabilities_compared": compared,
        "largest_difference": worst,
        "brier_5bp": {name: {"run": a, "record": b} for name, (a, b) in briers.items()},
        "scored_days": len(index),
    }


# -- the tables ---------------------------------------------------------------


def onset_rows(days, reads, series, forecasts, declaration, both: set) -> List[dict]:
    index = {date.fromisoformat(when): k for k, when in enumerate(forecasts["scored_dates"])}
    five = f"{TAU_BP:g}"
    out = []
    for day in days:
        read = reads[day]
        values = {column: read[column] for column in CALENDAR}
        lead = gauge_lead(series, reads, day)
        k = index[day]
        out.append(
            {
                "date": day.isoformat(),
                "both_definitions": day in both,
                "quarter_end": read["quarter_end"] == 1.0,
                "month_end": read["days_to_month_end"] <= declaration.month_end_window,
                "tax_date": read["tax_date"] == 1.0,
                "coupon_settlement": read[COUPONS] is not None and float(read[COUPONS]) > 0.0,
                "day_type": declaration.day_type(values),
                "state": read["state"],
                "state_label": None if read["state"] is None else STATE_LABELS[read["state"]],
                "state_read_date": read["state_read_date"].isoformat(),
                "v1_probability": forecasts[V1][five][k],
                "persistence_logistic_probability": forecasts[PERSISTENCE][five][k],
                "gauge_tight": read["state"] in (2, 3),
                "lead": None
                if lead is None
                else {**lead, "run_start": lead["run_start"].isoformat()},
            }
        )
    return out


def _scheduled(row) -> bool:
    return row["quarter_end"] or row["month_end"] or row["tax_date"] or row["coupon_settlement"]


def summary(rows_: List[dict], series, reads) -> dict:
    n = len(rows_)
    count = lambda pred: sum(1 for row in rows_ if pred(row))  # noqa: E731
    episodes = {}
    for label, first, last in EPISODES:
        inside = [row for row in rows_ if first <= date.fromisoformat(row["date"]) <= last]
        if not inside:
            episodes[label] = {"first_onset": None}
            continue
        row = inside[0]
        # The run of states 2-3 that holds the onset; when the gauge was not
        # there on the onset, the first run of the episode, said to start after it.
        entered = None if row["lead"] is None else row["lead"]["run_start"]
        if entered is None:
            tight = [day for day in series if first <= day <= last and reads[day]["state"] in (2, 3)]
            if tight:
                run = gauge_lead(series, reads, tight[0])
                entered = run["run_start"].isoformat()
        episodes[label] = {
            "first_onset": row["date"],
            "state": row["state"],
            "gauge_entered_states_2_3": entered,
            "entered_after_the_onset": entered is not None and row["lead"] is None,
            "lead": row["lead"],
        }
    return {
        "onsets": n,
        "scheduled": count(_scheduled),
        "quarter_end": count(lambda r: r["quarter_end"]),
        "month_end": count(lambda r: r["month_end"]),
        "tax_date": count(lambda r: r["tax_date"]),
        "coupon_settlement": count(lambda r: r["coupon_settlement"]),
        "states_2_3": count(lambda r: r["gauge_tight"]),
        "no_state": count(lambda r: r["state"] is None),
        "episodes": episodes,
    }


def _yes(flag: bool) -> str:
    return "yes" if flag else "--"


def _share(k: int, n: int) -> str:
    return f"{k} of {n} ({k / n:.2f})" if n else f"{k} of 0"


def markdown(document: dict) -> str:
    out = []
    for name, (_group, text) in DEFINITIONS.items():
        table = document["definitions"][name]
        out.append(f"### Onsets, {name} definition: {text}\n")
        out.append(
            "`*` marks an onset that is an onset under both definitions. Probabilities are of the "
            "+5 bp event at h = 1, issued at the day's as-of decision instant.\n"
        )
        out.append(
            "| Date | Quarter-end | Month-end | Tax date | Coupon settlement | Day type | State (read from) "
            "| v1 p(> +5 bp) | Persistence-logistic p(> +5 bp) | Gauge in states 2-3 | Lead (panel days) |"
        )
        out.append("|---|---|---|---|---|---|---|---|---|---|---|")
        for row in table["onsets"]:
            state = "none" if row["state"] is None else f"{row['state']} {row['state_label']}"
            out.append(
                f"| {row['date']}{' *' if row['both_definitions'] else ''} | {_yes(row['quarter_end'])} "
                f"| {_yes(row['month_end'])} | {_yes(row['tax_date'])} | {_yes(row['coupon_settlement'])} "
                f"| {row['day_type']} | {state} ({row['state_read_date']}) | {row['v1_probability']:.3f} "
                f"| {row['persistence_logistic_probability']:.3f} | {_yes(row['gauge_tight'])} "
                f"| {_lead_text(row['lead'])} |"
            )
        out.append("")
    out.append("### Summary\n")
    out.append(
        "| Definition | On a scheduled date | Quarter-end | Month-end | Tax date | Coupon settlement "
        "| In states 2-3 | No state |"
    )
    out.append("|---|---|---|---|---|---|---|---|")
    for name in DEFINITIONS:
        s = document["definitions"][name]["summary"]
        n = s["onsets"]
        out.append(
            f"| {name} | {_share(s['scheduled'], n)} | {_share(s['quarter_end'], n)} "
            f"| {_share(s['month_end'], n)} | {_share(s['tax_date'], n)} "
            f"| {_share(s['coupon_settlement'], n)} | {_share(s['states_2_3'], n)} | {_share(s['no_state'], n)} |"
        )
    out.append("")
    out.append("### The gauge's lead before the first onset of each episode\n")
    out.append("| Definition | Episode | First onset | State on it | Gauge entered states 2-3 | Lead (panel days) |")
    out.append("|---|---|---|---|---|---|")
    for name in DEFINITIONS:
        for label, entry in document["definitions"][name]["summary"]["episodes"].items():
            if entry["first_onset"] is None:
                out.append(f"| {name} | {label} | none | -- | -- | -- |")
                continue
            state = "none" if entry["state"] is None else f"{entry['state']} {STATE_LABELS[entry['state']]}"
            entered = entry["gauge_entered_states_2_3"] or "not in the episode"
            if entry["entered_after_the_onset"]:
                entered += " (after the onset)"
            lead = _lead_text(entry["lead"]) if entry["lead"] else "none: not in states 2-3 on the onset"
            out.append(f"| {name} | {label} | {entry['first_onset']} | {state} | {entered} | {lead} |")
    out.append("")
    return "\n".join(out)


def load(end: date, forecasts_path: Optional[Path] = None) -> dict:
    """The panel, the as-of reads and both forecasts through `end`, checked against the record.

    Returns `rows` (with the state), `reads` (the gauge's as-of series),
    `scored` (the published fold grid), `forecasts`, `record_check`,
    `declaration` and `published_columns_digest`. Stops (`ValueError`) unless
    the forecasts reproduce `docs/runs/pressure_model_v1_h1.json`.
    """

    require_unlocked([end], where="onset_post_mortem")
    validation = _script("scarcity_validation")
    declaration = load_split_declaration(SPLITS)
    with tempfile.TemporaryDirectory() as directory:
        # The state and its inputs are switched on for these reads only; v1
        # and the persistence-logistic run under the published declaration.
        with measurement_declaration():
            build, digest, registry, decision = validation.build_measurement_panel(
                REGISTRY, Path(directory)
            )
            rows = with_reserve_scarcity_state(build.observations)
            reads = as_of_reads(
                rows,
                registry,
                decision_time=decision,
                minimum_history=gauge_history(rows, registry, decision_time=decision),
                end=end,
            )
            scored = sorted(
                as_of_reads(
                    rows, registry, decision_time=decision, minimum_history=MINIMUM_HISTORY, end=end
                )
            )
        published_panel = Path(directory) / "published_columns.csv"
        if forecasts_path is not None and forecasts_path.exists():
            forecasts = json.loads(forecasts_path.read_text(encoding="utf-8"))
        else:
            forecasts = v1_and_persistence(published_panel)
            if forecasts_path is not None:
                forecasts_path.write_text(json.dumps(forecasts) + "\n", encoding="utf-8")
    if [d.isoformat() for d in scored] != forecasts["scored_dates"]:
        raise ValueError("the as-of reads and the forecasts are not on one fold grid")
    check = check_against_record(forecasts, json.loads(RECORD.read_text(encoding="utf-8")))
    return {
        "rows": rows,
        "reads": reads,
        "scored": scored,
        "forecasts": forecasts,
        "record_check": check,
        "declaration": declaration,
        "published_columns_digest": digest,
    }


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--end", type=date.fromisoformat, required=True, metavar="YYYY-MM-DD")
    parser.add_argument("--forecasts", type=Path, help="cache of the two models' probabilities")
    parser.add_argument("--json", type=Path)
    parser.add_argument("--markdown", type=Path)
    args = parser.parse_args(argv)
    require_unlocked([args.end], where="onset_post_mortem")

    loaded = load(args.end, args.forecasts)
    rows, reads, scored = loaded["rows"], loaded["reads"], loaded["scored"]
    forecasts, check, declaration = loaded["forecasts"], loaded["record_check"], loaded["declaration"]
    digest = loaded["published_columns_digest"]

    days = onset_days(rows, scored, declaration)
    both = set(days[PRIMARY]) & set(days[DESCRIPTIVE])
    series = sorted(reads)
    document = {
        "status": "descriptive only (#214): no model, no win rule, no claim; nothing published moves",
        "published_columns_digest": digest,
        "end": args.end.isoformat(),
        "record_check": check,
        "definitions": {},
    }
    for name in DEFINITIONS:
        table = onset_rows(days[name], reads, series, forecasts, declaration, both)
        document["definitions"][name] = {"onsets": table, "summary": summary(table, series, reads)}
    document["state_series"] = {"first": series[0].isoformat(), "last": series[-1].isoformat()}
    text = markdown(document)
    if args.json:
        args.json.write_text(json.dumps(document, indent=2) + "\n", encoding="utf-8")
    if args.markdown:
        args.markdown.write_text(text, encoding="utf-8")
    print(json.dumps({k: document[k] for k in ("published_columns_digest", "end", "record_check", "state_series")}, indent=2))
    print(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
