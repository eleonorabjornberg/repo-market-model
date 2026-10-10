"""Size six construction gaps in the risk-date models (#485): a sensitivity reading, not a candidate.

A scratch measurement. It writes JSON to the paths it is given and nothing into `docs/runs/`; it changes no
declared candidate and no published figure. Scored days are 2018-06-29 to 2025-12-31 only
(`docs/decisions/lockbox.md`): `run` refuses a later day through `lockbox.require_unlocked`, as
`scripts/risk_date_severity.py` does.

Each variant below is the declared risk-date model of `metadata/risk_date_severity.json` with one thing
changed, fitted on the same shared folds with the same inputs, and judged by the judge's own cut-off rule
(`pressure_judge.choose_cutoffs`). `declared` changes nothing and is checked against the declared run
(`check`), which is what makes the others readable as a change.

    declared       the declared model (the control).
    onset_label    gap 1: the classifier is fitted to "an onset" (`pressure.onsets`: a day above the
                   threshold with no such day on the five panel days before it) instead of to every day
                   above it. The risk dates are unchanged. The skew-t quantile fits the spread itself and
                   has no label to change.
    bill_days      gap 2: at horizon 1 a day with any Treasury settlement (bills as well as coupons) is a
                   risk date. At h >= 2 a settlement is not public (information-set.md), so nothing moves.
    calendar_bd    gap 3: also a risk date when it is one of the month's last two business days
                   (`EvaluationSplits.reporting_day_type`) or inside the quarter-end window of
                   `data.quarter_end_window` (the quarter's last business day and two either side, #140).
    calendar_wide  gap 3, wider: calendar_bd, and also any of the last five business days of March, June,
                   September and December. The five is a size chosen after the onset dates of the
                   directive were listed, so it is a sizing, not a candidate.

Commands (the panels are the scratch panel of `risk_date_severity.py` and the published one):

    PYTHONPATH=src python3 scripts/construction_gaps_485.py run --panel AUG2.csv --published PUB.csv \\
        --variant V --horizon H --output OUT/V_hH.json [--candidate NAME]
    PYTHONPATH=src python3 scripts/construction_gaps_485.py check OUT/declared_hH.json OUT/risk_NAME_hH.json
    PYTHONPATH=src python3 scripts/construction_gaps_485.py report --panel PUB.csv --output OUT/report.json \\
        OUT/declared_h?.json OUT/onset_label_h?.json ...
    PYTHONPATH=src python3 scripts/construction_gaps_485.py onsets --panel AUG2.csv --output OUT/onsets.json
    PYTHONPATH=src python3 scripts/construction_gaps_485.py leaf-floor
    PYTHONPATH=src python3 scripts/construction_gaps_485.py tables --report OUT/report.json \\
        --onsets OUT/onsets.json --output OUT/tables.md OUT/declared_*_h?.json
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import date, time
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))
sys.path.insert(0, str(REPO / "scripts"))

import risk_date_severity as rds  # noqa: E402
from repo_model import ml, measurement_fields, pressure  # noqa: E402
from repo_model import pressure_judge as pj  # noqa: E402
from repo_model.baseline import ExceedanceCurves, panel_sha256, rolling_exceedance_backtest  # noqa: E402
from repo_model.data import (  # noqa: E402
    audit_panel,
    exceeds_bp,
    last_business_days_of_month,
    load_daily_panel,
    quarter_end_window,
)
from repo_model.evaluation_splits import load_split_declaration  # noqa: E402
from repo_model.lockbox import require_unlocked  # noqa: E402

VARIANTS = ("declared", "onset_label", "bill_days", "calendar_bd", "calendar_wide")
QUARTER_MONTHS = (3, 6, 9, 12)
WIDE_BUSINESS_DAYS = 5
SETTLEMENT = "treasury_settlement"
COUPONS = "treasury_settlement_coupons"


# --------------------------------------------------------------------------
# The risk-date sets
# --------------------------------------------------------------------------


def _wide_window(day: date) -> bool:
    return day.month in QUARTER_MONTHS and day in last_business_days_of_month(day.year, day.month, WIDE_BUSINESS_DAYS)


def row_rule(variant: str, splits, day: date, values, horizon: int) -> bool:
    """Whether `day` is a risk date under `variant`, read off the panel row (settlement clauses at h = 1 only)."""

    if rds.is_risk_date(splits, values, horizon):
        return True
    if variant == "bill_days":
        return horizon == 1 and float(values.get(SETTLEMENT) or 0.0) > 0.0
    if variant in ("calendar_bd", "calendar_wide"):
        if splits.reporting_day_type(day, values) != "ordinary" or quarter_end_window(day) == 1.0:
            return True
        return variant == "calendar_wide" and _wide_window(day)
    return False


def design_for(variant: str, features, splits, calendar=(), horizon: int = 1):
    """The risk-date design with `variant`'s membership; the row layout is the declared model's.

    An observation the as-of rule hands the model is dated at its anchor (the latest row whose spread was
    public), not at the day it forecasts; its calendar columns are the scored day's. The calendar variants
    need the scored day's date, which is the `horizon + 1`th panel row after the anchor, and read it from
    `calendar` (the panel's dates) after checking that the row's calendar columns are that day's.
    """

    index = {day: k for k, day in enumerate(calendar)}

    def scored_day(observation) -> date:
        day = calendar[index[observation.date] + horizon + 1]
        for column in ("days_to_month_end", "quarter_end", "tax_date"):
            if float(observation.values[column]) != float(CALENDAR[day][column]):
                raise ValueError(f"{observation.date}: the scored day is not {day}; {column} differs")
        return day

    class Design(ml._RiskDateDesign):
        def member(self, observation) -> bool:
            if ml._RiskDateDesign.member(self, observation):
                return True
            if variant == "bill_days":
                # Bills are the gross settlement less the coupons; both are declared inputs at h = 1.
                return SETTLEMENT in self.settlements and self._value(observation, SETTLEMENT) > 0.0
            if variant in ("calendar_bd", "calendar_wide"):
                day = scored_day(observation)
                if splits.reporting_day_type(day, observation.values) != "ordinary" or quarter_end_window(day) == 1.0:
                    return True
                return variant == "calendar_wide" and _wide_window(day)
            return False

        def row(self, observation, tga_change):
            # An added risk date whose input was not public is not served (forecast 0, noted by `run`); the
            # declared model never reads an input on a day outside its set, and keeps its refusal.
            if variant == "declared":
                return super().row(observation, tga_change)
            try:
                return super().row(observation, tga_change)
            except ValueError:
                return [0.0] * (len(self.names) + 1)

    return Design(features, splits)


#: The panel's calendar columns by date, filled by `run` before any design is built.
CALENDAR: dict = {}


# --------------------------------------------------------------------------
# The predictor: `ml.pressure_risk_date_exceedance` with the one change, and a trace of every refit
# --------------------------------------------------------------------------


def variant_predictor(
    kind: str, features, splits, minimum_history: int, variant: str, trace: list, calendar=(), horizon: int = 1
):
    """`ml.pressure_risk_date_exceedance` line for line, but with `variant`'s risk dates and label.

    `declared` must reproduce the declared model exactly (`check`). `trace` receives one record per refit:
    the training pairs, the risk-date pairs, the pressure and onset counts among them, and whether the
    classifier fell back to a constant because the label had one class.
    """

    design = design_for(variant, features, splits, calendar, horizon)
    cache: dict = {}
    onset_label = variant == "onset_label"
    if onset_label and kind == "quantile_skewt":
        raise ValueError("the skew-t quantile fits the spread, not a label; there is no onset label to fit")

    def fit_predict(train_rows, feature_rows, taus, information=None, histories=None):
        if information is None:
            raise ValueError("a risk-date model needs the as-of rule")
        if len(train_rows) < minimum_history:
            raise ValueError(f"needs at least {minimum_history} training rows, got {len(train_rows)}")
        positions: list = []
        pairs, spreads = ml._pressure_pairs(design, information, train_rows, cache, positions)
        flags = [pair[-1] for pair in pairs]
        all_pairs = len(pairs)
        keep = [k for k, flag in enumerate(flags) if flag]
        xs = [pairs[k][:-1] for k in keep]
        spreads = [spreads[k] for k in keep]
        targets = [positions[k] for k in keep]
        record = {
            "train_end": train_rows[-1].date.isoformat(),
            "first_served": feature_rows[0].date.isoformat(),
            "training_rows": len(train_rows),
            "pairs": all_pairs,
            "risk_date_pairs": len(xs),
            "taus": {},
        }
        trace.append(record)
        if onset_label:
            usable = [k for k, target in enumerate(targets) if target >= pressure.ONSET_QUIET_DAYS]
            xs = [xs[k] for k in usable]
            spreads = [spreads[k] for k in usable]
            targets = [targets[k] for k in usable]
        served_all = [
            design.row(row, ml._served_tga_change(histories[day], row) if design.needs_history() else None)
            for day, row in enumerate(feature_rows)
        ]
        members = [day for day, served in enumerate(served_all) if served[-1]]
        served = [served_all[day][:-1] for day in members]
        columns = [[0.0] * len(feature_rows) for _ in taus]
        if members:
            if not xs:
                raise ValueError("no risk-date training label has a complete as-of read")
            fitted: dict = {}
            if kind == "quantile_skewt":
                law = ml._quantile_exceedance(xs, spreads, served, [float(t) for t in taus], smoother="skew_t")
                fits = [[curve[k] for curve in law] for k in range(len(taus))]
            else:
                fits = []
                for tau in taus:
                    exceeds = [1 if exceeds_bp(value, float(tau)) else 0 for value in spreads]
                    labels = ml._onset_labels(exceeds, targets, train_rows, float(tau)) if onset_label else exceeds
                    only_onsets = ml._onset_labels(exceeds, targets, train_rows, float(tau))
                    record["taus"][f"{float(tau):g}"] = {
                        "pressure_labels": sum(exceeds),
                        "onset_labels": sum(only_onsets),
                        "fitted_labels": sum(labels),
                        "single_class_fallback": len(set(labels)) < 2,
                    }
                    if len(set(labels)) < 2:
                        fits.append([float(labels[0])] * len(served))
                        continue
                    key = tuple(labels)
                    if key not in fitted:
                        fitted[key] = ml._fit_classifier(kind, xs, labels, served)
                    fits.append(fitted[key])
            for position, fit in enumerate(fits):
                for day, value in zip(members, fit):
                    columns[position][day] = value
        curves = []
        for day in range(len(feature_rows)):
            curve: list = []
            for column in columns:
                value = min(1.0, max(0.0, column[day]))
                curve.append(value if not curve else min(curve[-1], value))
            curves.append(tuple(curve))
        return ExceedanceCurves(
            tuple(curves),
            design.features,
            ml_libraries=ml._library_versions(),
            model_settings={"risk_date_training_pairs": len(xs), "variant": variant},
            history_ends=(
                None if histories is None else tuple(history[-1].date if history else None for history in histories)
            ),
        )

    return fit_predict


def run_command(args) -> int:
    declared = rds.committed_declaration(rds.DECLARATION)
    h = args.horizon
    if h not in declared["horizons"]:
        raise SystemExit(f"horizon {h} is not declared")
    last = date.fromisoformat(declared["scoring"]["last_day"])
    require_unlocked([last], where="construction_gaps_485")
    rows = load_daily_panel(args.panel)
    audit_panel(rows)
    splits = load_split_declaration(rds.SPLITS)
    registry = measurement_fields.load_registry()
    taus = tuple(float(t) for t in declared["thresholds_bp"])
    minimum = declared["scoring"]["minimum_history"]
    names = [args.candidate] if args.candidate else list(declared["candidates"])
    if args.variant == "onset_label":
        names = [n for n in names if declared["candidates"][n]["kind"] != "quantile_skewt"]
    by_date = {row.date: row for row in rows}
    CALENDAR.update({row.date: row.values for row in rows})
    forecasts, settings, traces, members, unserved = {}, {}, {}, {}, {}
    for name in names:
        spec = declared["candidates"][name]
        features = rds.features_at_horizon(declared, spec, h)
        trace: list = []
        predictor = variant_predictor(
            spec["kind"], features, splits, minimum, args.variant, trace, [row.date for row in rows], h
        )
        with rds.switched_on():
            report = rolling_exceedance_backtest(
                rows,
                predictor=predictor,
                model_name=name,
                features=features,
                registry=registry,
                decision_time=time.fromisoformat(declared["scoring"]["decision_time"]),
                taus=taus,
                minimum_history=minimum,
                refit_every=declared["scoring"]["refit_every"],
                end=last,
                horizon=h,
            )
        forecasts[name] = rds.column(report)
        settings[name] = {"features": list(report.features)}
        traces[name] = trace
        if not members:
            members = {
                day.isoformat(): row_rule(args.variant, splits, day, by_date[day].values, h)
                for day in report.scored_dates
            }
        outside = [
            day.isoformat()
            for day, curve in zip(report.scored_dates, report.forecast)
            if any(curve) and not members[day.isoformat()]
        ]
        unserved[name] = [
            day.isoformat()
            for day, curve in zip(report.scored_dates, report.forecast)
            if members[day.isoformat()] and not any(curve)
        ]
        if outside:
            raise SystemExit(f"{name} h={h}: a nonzero forecast on {outside[0]}, which is not a risk date")
        print(json.dumps({"variant": args.variant, "horizon": h, "candidate": name, "done": True}), flush=True)
    document = {
        "horizon": h,
        "variant": args.variant,
        "panel_sha256": panel_sha256(args.published),
        "scratch_panel_sha256": panel_sha256(args.panel),
        "declaration": declared,
        "declarations": settings,
        "forecasts": forecasts,
        "risk_dates": members,
        "risk_dates_with_zero_forecast": unserved,
        "refits": traces,
    }
    args.output.write_text(json.dumps(document, indent=1, sort_keys=True, default=str) + "\n", encoding="utf-8")
    print(json.dumps({"variant": args.variant, "horizon": h, "output": str(args.output)}))
    return 0


def check_command(args) -> int:
    """The control reproduces the declared run: every forecast in `ours` equals the one in `theirs`."""

    ours, theirs = (json.loads(Path(p).read_text()) for p in (args.ours, args.theirs))
    bad = 0
    for name, columns in theirs["forecasts"].items():
        if name not in ours["forecasts"]:
            continue
        for tau, series in columns.items():
            for day, value in series.items():
                if ours["forecasts"][name][tau].get(day) != value:
                    bad += 1
    print(json.dumps({"horizon": ours["horizon"], "candidates": sorted(set(theirs["forecasts"]) & set(ours["forecasts"])), "differences": bad}))
    return 1 if bad else 0


# --------------------------------------------------------------------------
# The reading
# --------------------------------------------------------------------------


def report_command(args) -> int:
    declaration = pj.load_declaration()
    rows = load_daily_panel(args.panel)
    audit_panel(rows)
    splits = load_split_declaration(rds.SPLITS)
    digest = panel_sha256(args.panel)
    calendar = [row.date for row in rows]
    rows_by_date = {row.date: row for row in rows}
    tau = declaration.primary
    out: dict = {}
    for path in args.inputs:
        document = json.loads(Path(path).read_text())
        if document["panel_sha256"] != digest:
            raise SystemExit(f"{path} was scored on another panel ({document['panel_sha256'][:8]})")
        variant, h = document["variant"], document["horizon"]
        forecasts = pj.forecasts_from_horizon_document(document)
        reference = forecasts[0]
        grid = pj.build_grid(declaration, h, rows, reference.dates, splits, scarcity_state={})
        chosen = pj.choose_cutoffs(declaration, {h: grid}, forecasts, calendar)
        onset, outcomes = grid.onset_at(tau, tau), grid.outcomes[tau]
        for forecast in chosen:
            p = forecast.probabilities[tau]
            flags = [1 if q >= c else 0 for q, c in zip(p, forecast.cutoffs[tau])]
            risk = [document["risk_dates"][day.isoformat()] for day in grid.dates]
            onsets = sum(onset)
            false = sum(1 for k, f in enumerate(flags) if f and not outcomes[k])
            by_year: dict = {}
            for k, day in enumerate(grid.dates):
                if onset[k]:
                    cell = by_year.setdefault(str(day.year), {"onsets": 0, "flagged": 0})
                    cell["onsets"] += 1
                    cell["flagged"] += flags[k]
            out.setdefault(variant, {}).setdefault(forecast.name, {})[str(h)] = {
                "days": len(flags),
                "risk_dates": sum(risk),
                "onsets": onsets,
                "onsets_on_risk_dates": sum(onset[k] for k in range(len(flags)) if risk[k]),
                "onsets_flagged": sum(flags[k] and onset[k] for k in range(len(flags))),
                "flags": sum(flags),
                "false_alarms": false,
                "false_alarms_per_onset": false / onsets if onsets else None,
                "by_year": by_year,
                "added_risk_dates_unserved": sorted(
                    day
                    for day in document.get("risk_dates_with_zero_forecast", {}).get(forecast.name, [])
                    if not rds.is_risk_date(splits, rows_by_date[date.fromisoformat(day)].values, h)
                ),
                "flagged_onsets": [day.isoformat() for k, day in enumerate(grid.dates) if flags[k] and onset[k]],
                "unreached_onsets": [
                    day.isoformat() for k, day in enumerate(grid.dates) if onset[k] and not risk[k]
                ],
            }
    args.output.write_text(json.dumps(out, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    for variant in sorted(out):
        for name in sorted(out[variant]):
            cells = out[variant][name]
            line = " | ".join(
                f"h={h}: {c['onsets_flagged']}/{c['onsets']}, {c['false_alarms_per_onset']:.2f}"
                for h, c in sorted(cells.items())
            )
            print(f"{variant:14s} {name:26s} {line}")
    return 0


def onsets_command(args) -> int:
    """Every +5 bp onset of the scored days with its calendar, settlement and rate-cut facts."""

    declared = rds.committed_declaration(rds.DECLARATION)
    last = date.fromisoformat(declared["scoring"]["last_day"])
    require_unlocked([last], where="construction_gaps_485")
    rows = load_daily_panel(args.panel)
    splits = load_split_declaration(rds.SPLITS)
    by_date = {row.date: row for row in rows}
    scored = [row.date for row in rows if date(2018, 6, 29) <= row.date <= last]
    result = []
    for day in pressure.onsets(rows, 5.0, scored):
        values = by_date[day].values
        index = rows.index(by_date[day])
        previous = rows[index - 1]
        result.append(
            {
                "date": day.isoformat(),
                "spread_bps": by_date[day].spread_bps,
                "day_type": splits.day_type(values),
                "reporting_day_type": splits.reporting_day_type(day, values),
                "days_to_month_end": values["days_to_month_end"],
                "quarter_end_window": quarter_end_window(day),
                "coupons": values["treasury_settlement_coupons"],
                "bills": values["treasury_settlement_bills"],
                "gross": values["treasury_settlement"],
                "risk_date_h1": rds.is_risk_date(splits, values, 1),
                "risk_date_h2_plus": rds.is_risk_date(splits, values, 2),
                "calendar_bd_h2_plus": row_rule("calendar_bd", splits, day, values, 2),
                "calendar_wide_h2_plus": row_rule("calendar_wide", splits, day, values, 2),
                "bill_days_h1": row_rule("bill_days", splits, day, values, 1),
                "iorb_announced_change_bps": values.get("iorb_announced_change_bps"),
                "sofr": values["sofr"],
                "iorb": values["iorb"],
                "effr": values.get("effr"),
                "previous_date": previous.date.isoformat(),
                "previous_spread_bps": previous.spread_bps,
            }
        )
    march = []
    for row in rows:
        if date(2020, 3, 2) <= row.date <= date(2020, 3, 18):
            v = row.values
            march.append(
                {
                    "date": row.date.isoformat(),
                    "sofr": v["sofr"],
                    "iorb": v["iorb"],
                    "effr": v.get("effr"),
                    "spread_bps": row.spread_bps,
                    "sofr_p75_iorb_bps": v.get("sofr_p75_iorb_bps"),
                    "sofr_p99_iorb_bps": v.get("sofr_p99_iorb_bps"),
                    "iorb_announced_change_bps": v.get("iorb_announced_change_bps"),
                    "onset": row.date in {date.fromisoformat(o["date"]) for o in result},
                }
            )
    args.output.write_text(json.dumps({"onsets": result, "march_2020": march}, indent=1) + "\n", encoding="utf-8")
    print(json.dumps({"onsets": len(result), "output": str(args.output)}))
    return 0


def leaf_floor_command(args) -> int:
    """The smallest training set on which the declared classifier is not a constant (gap 4)."""

    import numpy as np
    from sklearn.ensemble import HistGradientBoostingClassifier

    settings = ml.PRESSURE_CLASSIFIER_SETTINGS
    rng = np.random.default_rng(0)
    rows = []
    for n in range(2 * settings["min_samples_leaf"] - 3, 2 * settings["min_samples_leaf"] + 3):
        x = rng.normal(size=(n, 5))
        y = np.zeros(n, dtype=int)
        y[: max(2, n // 10)] = 1
        model = HistGradientBoostingClassifier(
            learning_rate=settings["learning_rate"],
            max_iter=settings["max_iter"],
            max_leaf_nodes=settings["max_leaf_nodes"],
            min_samples_leaf=settings["min_samples_leaf"],
            random_state=settings["random_state"],
        ).fit(x, y)
        distinct = len(set(np.round(model.predict_proba(rng.normal(size=(50, 5)))[:, 1], 10)))
        rows.append({"training_pairs": n, "distinct_probabilities_on_50_new_rows": distinct})
    print(json.dumps({"min_samples_leaf": settings["min_samples_leaf"], "rows": rows}, indent=1))
    return 0


CANDIDATES = ("risk_gbm", "risk_gbm_base", "risk_logistic", "risk_logistic_base", "risk_quantile_skewt_base")
THROUGH = date(2019, 12, 31)
LEAF_FLOOR = 40  # 2 * min_samples_leaf: below it the declared classifier is a constant (`leaf-floor`)


def _cell(c) -> str:
    return f"{c['onsets_flagged']}/{c['onsets']}, {c['false_alarms_per_onset']:.2f}"


def _comparison(report, variant, names, horizons, title) -> list:
    lines = [f"**{title}**", "", "| model | " + " | ".join(f"h={h} declared | h={h} {variant}" for h in horizons) + " |"]
    lines.append("|---|" + "---|---|" * len(horizons))
    for name in names:
        if name not in report.get(variant, {}):
            continue
        cells = []
        for h in horizons:
            base, new = report["declared"][name].get(str(h)), report[variant][name].get(str(h))
            cells += [_cell(base) if base else "-", _cell(new) if new else "-"]
        lines.append(f"| {name} | " + " | ".join(cells) + " |")
    return lines + [""]


def _by_year(report, variant, names, h, title) -> list:
    years = sorted({y for n in names if n in report.get(variant, {}) for y in report[variant][n][str(h)]["by_year"]})
    lines = [f"**{title}**", "", "| model | variant | " + " | ".join(years) + " |", "|---|---|" + "---|" * len(years)]
    for name in names:
        for v in ("declared", variant):
            if name not in report.get(v, {}) or str(h) not in report[v][name]:
                continue
            by = report[v][name][str(h)]["by_year"]
            lines.append(
                f"| {name} | {v} | "
                + " | ".join(f"{by[y]['flagged']}/{by[y]['onsets']}" if y in by else "-" for y in years)
                + " |"
            )
    return lines + [""]


def tables_command(args) -> int:
    report = json.loads(args.report.read_text())
    onsets = json.loads(args.onsets.read_text())["onsets"]
    docs = [json.loads(Path(p).read_text()) for p in args.inputs]
    out = []
    # Gap 2: the declared forecast on the onsets that are not risk dates
    out += ["### Gap 2: the declared forecast on onsets that are not risk dates", "",
            "| onset | horizons at which it is not a risk date | forecasts read | largest forecast, either threshold |", "|---|---|---|---|"]
    for o in onsets:
        horizons, reads, largest = [], 0, 0.0
        for doc in sorted(docs, key=lambda d: d["horizon"]):
            if o["date"] not in doc["risk_dates"] or doc["risk_dates"][o["date"]]:
                continue
            if doc["horizon"] not in horizons:
                horizons.append(doc["horizon"])
            for columns in doc["forecasts"].values():
                for tau in ("5", "10"):
                    reads += 1
                    largest = max(largest, columns[tau][o["date"]])
        if horizons:
            out.append(f"| {o['date']} | {', '.join(map(str, horizons))} | {reads} | {largest:g} |")
    out.append("")
    # Gap 4: the fits through 2019
    out += ["### Gap 4: the declared fits through 2019", "",
            "Per refit: risk-date training pairs, and the pressure (onset) labels among them at +5 and +10 bp.", ""]
    summary = {}
    for doc in sorted(docs, key=lambda d: d["horizon"]):
        h = doc["horizon"]
        for name, refits in sorted(doc["refits"].items()):
            early = [r for r in refits if date.fromisoformat(r["first_served"]) <= THROUGH]
            summary.setdefault(name, {})[str(h)] = early
    for name in CANDIDATES:
        for h in ("1", "5"):
            early = summary.get(name, {}).get(h)
            if not early or name != "risk_gbm_base":
                continue
            out += [f"{name}, h = {h}", "", "| first served day | pairs | risk-date pairs | +5 bp events (onsets) | +10 bp events (onsets) | classifier |",
                    "|---|---|---|---|---|---|"]
            for r in early:
                t5, t10 = r["taus"].get("5"), r["taus"].get("10")
                def ev(t):
                    return f"{t['pressure_labels']} ({t['onset_labels']})" if t else "-"
                state = "constant (< 2 x min_samples_leaf)" if r["risk_date_pairs"] < LEAF_FLOOR else "can split"
                if t5 and t5["single_class_fallback"]:
                    state = "single class at +5 bp: constant 0"
                out.append(f"| {r['first_served']} | {r['pairs']} | {r['risk_date_pairs']} | {ev(t5)} | {ev(t10)} | {state} |")
            out.append("")
    out += ["Refits through 2019, by candidate and horizon: how many have fewer risk-date pairs than the leaf floor,", "",
            "| model | h | refits | below the floor | first refit at or above it (pairs) | refits with no +5 bp event | refits with no +10 bp event |", "|---|---|---|---|---|---|---|"]
    for name in CANDIDATES:
        for h in ("1", "2", "3", "4", "5"):
            early = summary.get(name, {}).get(h)
            if not early:
                continue
            below = [r for r in early if r["risk_date_pairs"] < LEAF_FLOOR]
            first = next((r for r in early if r["risk_date_pairs"] >= LEAF_FLOOR), None)
            fits_labels = name != "risk_quantile_skewt_base"  # the skew-t fits the spread itself, with no label
            none5 = sum(1 for r in early if r["taus"].get("5", {}).get("pressure_labels", 0) == 0) if fits_labels else "-"
            none10 = sum(1 for r in early if r["taus"].get("10", {}).get("pressure_labels", 0) == 0) if fits_labels else "-"
            out.append(
                f"| {name} | {h} | {len(early)} | {len(below)} | "
                + (f"{first['first_served']} ({first['risk_date_pairs']})" if first else "-")
                + f" | {none5} | {none10} |"
            )
    out.append("")
    # Gaps 1 to 3: the variants
    names = list(CANDIDATES)
    horizons = (1, 2, 3, 4, 5)
    out += ["### Gap 1: the onset label", ""]
    out += _comparison(report, "onset_label", names, horizons, "+5 bp onsets flagged / onsets, false alarms per onset")
    out += _by_year(report, "onset_label", names, 1, "h = 1, onsets flagged by year")
    out += ["### Gap 2: bill settlements as risk dates (h = 1)", ""]
    out += _comparison(report, "bill_days", names, (1,), "+5 bp onsets flagged / onsets, false alarms per onset")
    out += _by_year(report, "bill_days", names, 1, "h = 1, onsets flagged by year")
    out += ["### Gap 3: business-day month-end, quarter-end window", ""]
    for variant in ("calendar_bd", "calendar_wide"):
        out += _comparison(report, variant, names, horizons, f"{variant}: +5 bp onsets flagged / onsets, false alarms per onset")
    out += _by_year(report, "calendar_bd", names, 2, "h = 2, calendar_bd, onsets flagged by year")
    out += ["Risk dates and onsets on them, by variant (h = 2; days scored, risk dates, onsets, onsets on risk dates):", "",
            "| variant | days | risk dates | onsets | onsets on risk dates |", "|---|---|---|---|---|"]
    for v in ("declared", "calendar_bd", "calendar_wide"):
        c = report[v]["risk_gbm_base"]["2"]
        out.append(f"| {v} | {c['days']} | {c['risk_dates']} | {c['onsets']} | {c['onsets_on_risk_dates']} |")
    out.append("")
    args.output.write_text("\n".join(out) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(args.output), "lines": len(out)}))
    return 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    commands = parser.add_subparsers(dest="command", required=True)
    run = commands.add_parser("run")
    run.add_argument("--panel", type=Path, required=True)
    run.add_argument("--published", type=Path, required=True)
    run.add_argument("--variant", choices=VARIANTS, required=True)
    run.add_argument("--horizon", type=int, required=True)
    run.add_argument("--candidate")
    run.add_argument("--output", type=Path, required=True)
    run.set_defaults(handler=run_command)
    check = commands.add_parser("check")
    check.add_argument("ours", type=Path)
    check.add_argument("theirs", type=Path)
    check.set_defaults(handler=check_command)
    report = commands.add_parser("report")
    report.add_argument("--panel", type=Path, required=True)
    report.add_argument("--output", type=Path, required=True)
    report.add_argument("inputs", nargs="+", type=Path)
    report.set_defaults(handler=report_command)
    onsets = commands.add_parser("onsets")
    onsets.add_argument("--panel", type=Path, required=True)
    onsets.add_argument("--output", type=Path, required=True)
    onsets.set_defaults(handler=onsets_command)
    tables = commands.add_parser("tables")
    tables.add_argument("--report", type=Path, required=True)
    tables.add_argument("--onsets", type=Path, required=True)
    tables.add_argument("--output", type=Path, required=True)
    tables.add_argument("inputs", nargs="+", type=Path)
    tables.set_defaults(handler=tables_command)
    floor = commands.add_parser("leaf-floor")
    floor.set_defaults(handler=leaf_floor_command)
    args = parser.parse_args(argv)
    return args.handler(args)


if __name__ == "__main__":
    raise SystemExit(main())
