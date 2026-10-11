"""Score four model-defect changes on the five risk-date passers, and the capped nowcast (#540).

A scratch measurement, not a record: it writes JSON to the paths it is given and nothing into `docs/runs/`.
The four changes, how each is built and the numbers in them are in `metadata/model_defects_540.json`, which this
script refuses to read unless it is committed and unchanged, as the judge's declaration is. Every input beyond
the published panel is off in every published declaration and switched on for these runs only. Scored days are
2018-06-29 to 2025-12-31 only (`docs/decisions/lockbox.md`): `run` and `nowcast` refuse a later day through
`lockbox.require_unlocked`. No rule, threshold, onset definition or availability time changes.

    # the scratch panel is the one of risk_date_severity.py (AUG2.csv); declared forecasts are its `run` output
    PYTHONPATH=src python3 scripts/model_defects_540.py run --panel AUG2.csv --published PUBLISHED.csv \\
        --variant V --horizon H --declared OUT/risk_hH.json --output OUT/m540_V_hH.json [--candidate PARENT]
    PYTHONPATH=src python3 scripts/model_defects_540.py assemble --output OUT/m540_hH.json OUT/m540_*_hH.json
    PYTHONPATH=src python3 scripts/pressure_judge.py judge --panel PUBLISHED.csv --output OUT/judge.json \\
        --markdown OUT/judge.md OUT/bench_h?.json OUT/risk_h?.json OUT/m540_h?.json
    PYTHONPATH=src python3 scripts/model_defects_540.py compare --panel PUBLISHED.csv --output OUT/compare.json \\
        --markdown OUT/compare.md OUT/bench_h?.json OUT/risk_h?.json OUT/m540_h?.json
    PYTHONPATH=src python3 scripts/model_defects_540.py added --panel PUBLISHED.csv --output OUT/added.json OUT/m540_added_h?.json \\
        OUT/m540_all_h?.json
    PYTHONPATH=src python3 scripts/model_defects_540.py refits --output OUT/refits.json OUT/m540_*_h?.json
    PYTHONPATH=src python3 scripts/model_defects_540.py nowcast --panel AUG2.csv --output OUT/nowcast.json

`run` is `scripts/construction_gaps_485.py`'s predictor with the changes of the declaration switched on one
at a time (`leaf`, `iorb`, `added`) or together (`all`). `assemble` renames each candidate to its judge name
(`<parent>+<variant>_540`, the files in `metadata/pressure_judge/candidates/`) and merges the variants of one
horizon into one file of the judge's shape. `compare` is `scripts/risk_date_every_day.py compare` with this
declaration's variants: each beside its parent, climatology and persistence-logistic under the judge's own
cut-offs, by year, regime and pressure-day type, paired, with a stationary-bootstrap interval.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import random
import sys
from datetime import date, time
from pathlib import Path
from types import MappingProxyType
from unittest import mock

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))
sys.path.insert(0, str(REPO / "scripts"))

from repo_model import measurement_fields, ml, nowcast, pressure  # noqa: E402
from repo_model import pressure_judge as pj  # noqa: E402
from repo_model.baseline import ExceedanceCurves, panel_sha256, rolling_exceedance_backtest  # noqa: E402
from repo_model.data import audit_panel, exceeds_bp, load_daily_panel, quarter_end_window  # noqa: E402
from repo_model.evaluation_splits import load_split_declaration  # noqa: E402
from repo_model.lockbox import require_unlocked  # noqa: E402
from repo_model.metrics import stationary_bootstrap_indices  # noqa: E402

DECLARATION = REPO / "metadata" / "model_defects_540.json"
ANNOUNCED = "iorb_announced_change_bps"
SETTLEMENT = "treasury_settlement"


def _sibling(name: str):
    spec = importlib.util.spec_from_file_location(f"{name}_script", REPO / "scripts" / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[f"{name}_script"] = module
    spec.loader.exec_module(module)
    return module


rds = _sibling("risk_date_severity")
cg = _sibling("construction_gaps_485")
ed = _sibling("risk_date_every_day")

#: variant -> (scaled leaf floor, announced IORB at h = 1, added risk dates modelled apart)
FLAGS = {"leaf": (True, False, False), "iorb": (False, True, False), "added": (False, False, True), "all": (True, True, True)}
GBM = "gbm_classifier"
ORIGINAL, ADDED = 1.0, 2.0


def leaf_floor(pairs: int) -> int:
    """The declared scaled leaf floor: `min(20, max(1, pairs // 4))`."""

    return min(20, max(1, pairs // 4))


def declared_document() -> dict:
    return rds.committed_declaration(DECLARATION)


# --------------------------------------------------------------------------
# The risk-date sets
# --------------------------------------------------------------------------


def added_rule(splits, day: date, values, horizon: int) -> bool:
    """An added risk date (the declaration): a bill-settlement day at h = 1, or the business-day calendar window."""

    if rds.is_risk_date(splits, values, horizon):
        return False
    if horizon == 1 and float(values.get(SETTLEMENT) or 0.0) > 0.0:
        return True
    return splits.reporting_day_type(day, values) != "ordinary" or quarter_end_window(day) == 1.0


def design_for(added: bool, features, splits, calendar, horizon: int):
    """The risk-date design; with `added`, its last element is 1.0 on an original and 2.0 on an added date."""

    index = {day: k for k, day in enumerate(calendar)}

    def scored_day(observation) -> date:
        day = calendar[index[observation.date] + horizon + 1]
        for column in ("days_to_month_end", "quarter_end", "tax_date"):
            if float(observation.values[column]) != float(cg.CALENDAR[day][column]):
                raise ValueError(f"{observation.date}: the scored day is not {day}; {column} differs")
        return day

    class Design(ml._RiskDateDesign):
        def kind_of(self, observation) -> float:
            if ml._RiskDateDesign.member(self, observation):
                return ORIGINAL
            if not added:
                return 0.0
            day = scored_day(observation)
            if horizon == 1 and SETTLEMENT in self.settlements and self._value(observation, SETTLEMENT) > 0.0:
                return ADDED
            if splits.reporting_day_type(day, observation.values) != "ordinary" or quarter_end_window(day) == 1.0:
                return ADDED
            return 0.0

        def member(self, observation) -> bool:
            return bool(self.kind_of(observation))

        def row(self, observation, tga_change):
            kind = self.kind_of(observation)
            if not kind:
                return [0.0] * (len(self.names) + 1)
            try:
                features_ = ml._PressureDesign.row(self, observation, tga_change)
            except ValueError:
                if kind == ORIGINAL:
                    raise
                return [0.0] * (len(self.names) + 1)  # an added date whose input was not public is not served
            return features_ + [kind]

    return Design(features, splits)


# --------------------------------------------------------------------------
# The predictor
# --------------------------------------------------------------------------


def fit_group(kind, xs, spreads, served, taus, leaf: bool, record: dict):
    """One group's fits at every threshold: a list per tau of the probabilities at `served`."""

    if kind == "quantile_skewt":
        law = ml._quantile_exceedance(xs, spreads, served, [float(t) for t in taus], smoother="skew_t")
        return [[curve[k] for curve in law] for k in range(len(taus))]
    fits, fitted = [], {}
    for tau in taus:
        labels = [1 if exceeds_bp(value, float(tau)) else 0 for value in spreads]
        cell = record["taus"].setdefault(f"{float(tau):g}", {})
        cell["pressure_labels"] = sum(labels)
        if len(set(labels)) < 2:
            cell["single_class_fallback"] = True
            fits.append([float(labels[0])] * len(served))
            continue
        key = tuple(labels)
        if key not in fitted:
            floor = leaf_floor(len(xs)) if leaf and kind == GBM else ml.PRESSURE_CLASSIFIER_SETTINGS["min_samples_leaf"]
            settings = MappingProxyType({**ml.PRESSURE_CLASSIFIER_SETTINGS, "min_samples_leaf": floor})
            with mock.patch.object(ml, "PRESSURE_CLASSIFIER_SETTINGS", settings):
                both = ml._fit_classifier(kind, xs, labels, list(xs) + list(served))
            on_training = both[: len(xs)]
            fitted[key] = both[len(xs):]
            cell["min_samples_leaf"] = floor
            cell["constant_on_its_training_pairs"] = max(on_training) - min(on_training) < 1e-12
        fits.append(fitted[key])
    return fits


def variant_predictor(kind, features, splits, minimum_history, flags, trace, calendar, horizon):
    leaf, _iorb, added = flags
    design = design_for(added, features, splits, calendar, horizon)
    cache: dict = {}

    def fit_predict(train_rows, feature_rows, taus, information=None, histories=None):
        if information is None:
            raise ValueError("a risk-date model needs the as-of rule")
        if len(train_rows) < minimum_history:
            raise ValueError(f"needs at least {minimum_history} training rows, got {len(train_rows)}")
        positions: list = []
        pairs, spreads = ml._pressure_pairs(design, information, train_rows, cache, positions)
        kinds = [pair[-1] for pair in pairs]
        served_all = [
            design.row(row, ml._served_tga_change(histories[day], row) if design.needs_history() else None)
            for day, row in enumerate(feature_rows)
        ]
        record = {
            "train_end": train_rows[-1].date.isoformat(),
            "first_served": feature_rows[0].date.isoformat(),
            "training_rows": len(train_rows),
            "pairs": {"original": sum(1 for k in kinds if k == ORIGINAL), "added": sum(1 for k in kinds if k == ADDED)},
            "groups": {},
        }
        trace.append(record)
        columns = [[0.0] * len(feature_rows) for _ in taus]
        for group, name in ((ORIGINAL, "original"), (ADDED, "added")):
            if group == ADDED and not added:
                continue
            members = [day for day, served in enumerate(served_all) if served[-1] == group]
            keep = [k for k, kind_of in enumerate(kinds) if kind_of == group]
            xs = [pairs[k][:-1] for k in keep]
            ys = [spreads[k] for k in keep]
            cell = {"pairs": len(xs), "served": len(members), "taus": {}}
            record["groups"][name] = cell
            if not members:
                continue
            if not xs:
                if group == ORIGINAL:
                    raise ValueError("no risk-date training label has a complete as-of read")
                cell["unserved"] = "no training pair"
                continue
            served = [served_all[day][:-1] for day in members]
            try:
                fits = fit_group(kind, xs, ys, served, taus, leaf, cell)
            except ValueError as error:
                if group == ORIGINAL:
                    raise
                cell["unserved"] = str(error)
                continue
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
            model_settings={"variant": "m540"},
            history_ends=(
                None if histories is None else tuple(history[-1].date if history else None for history in histories)
            ),
        )

    return fit_predict


def run_command(args) -> int:
    declared = declared_document()
    parents = json.loads(rds.DECLARATION.read_text(encoding="utf-8"))
    h = args.horizon
    if h not in declared["horizons"]:
        raise SystemExit(f"horizon {h} is not declared")
    flags = FLAGS[args.variant]
    leaf, iorb, added = flags
    last = date.fromisoformat(declared["scoring"]["last_day"])
    require_unlocked([last], where="model_defects_540")
    rows = load_daily_panel(args.panel)
    audit_panel(rows)
    splits = load_split_declaration(rds.SPLITS)
    registry = measurement_fields.load_registry()
    taus = tuple(float(t) for t in declared["thresholds_bp"])
    minimum = declared["scoring"]["minimum_history"]
    names = [args.candidate] if args.candidate else list(declared["parents"])
    by_date = {row.date: row for row in rows}
    cg.CALENDAR.update({row.date: row.values for row in rows})
    declared_forecasts = json.loads(args.declared.read_text())["forecasts"] if args.declared else {}
    forecasts, settings, traces, members, unserved, added_dates = {}, {}, {}, {}, {}, {}
    for name in names:
        spec = declared["parents"][name]
        if leaf and not iorb and not added and spec["kind"] != GBM:
            # The logistic and the skew-t quantile model have no leaf floor: this variant is the parent, exactly.
            if name not in declared_forecasts:
                raise SystemExit(f"{name}: the parent's declared forecasts are needed (--declared)")
            forecasts[name] = declared_forecasts[name]
            settings[name] = {"features": None, "identical_to_the_parent": "no leaf floor in this estimator"}
            traces[name] = []
            print(json.dumps({"variant": args.variant, "horizon": h, "candidate": name, "copied": True}), flush=True)
            continue
        features = rds.features_at_horizon({"features": parents["features"]}, spec, h)
        if iorb and h == 1:
            features = features + (ANNOUNCED,)
        trace: list = []
        predictor = variant_predictor(
            spec["kind"], features, splits, minimum, flags, trace, [row.date for row in rows], h
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
                day.isoformat(): rds.is_risk_date(splits, by_date[day].values, h)
                or (added and added_rule(splits, day, by_date[day].values, h))
                for day in report.scored_dates
            }
            added_dates = {
                day.isoformat(): bool(added and added_rule(splits, day, by_date[day].values, h))
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
        "added_dates": added_dates,
        "risk_dates_with_zero_forecast": unserved,
        "refits": traces,
    }
    args.output.write_text(json.dumps(document, indent=1, sort_keys=True, default=str) + "\n", encoding="utf-8")
    print(json.dumps({"variant": args.variant, "horizon": h, "output": str(args.output)}))
    return 0


def assemble_command(args) -> int:
    """One judge-shaped file per horizon: every variant's candidates, renamed `<parent>+<variant>_540`."""

    declared = declared_document()
    merged: dict = {}
    horizon = digest = None
    for path in args.inputs:
        document = json.loads(Path(path).read_text())
        horizon = horizon or document["horizon"]
        digest = digest or document["panel_sha256"]
        if document["horizon"] != horizon or document["panel_sha256"] != digest:
            raise SystemExit(f"{path}: another horizon or panel")
        suffix = declared["variants"][document["variant"]]["suffix"]
        for name, columns in document["forecasts"].items():
            merged[name + suffix] = columns
    out = {"horizon": horizon, "panel_sha256": digest, "declaration": declared, "forecasts": merged}
    args.output.write_text(json.dumps(out, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"horizon": horizon, "candidates": sorted(merged)}))
    return 0


# --------------------------------------------------------------------------
# The reading
# --------------------------------------------------------------------------


def compare_command(args) -> int:
    """`risk_date_every_day.compare_command` with this declaration's parents and variants."""

    declared = declared_document()
    ed.DECLARATION = DECLARATION
    ed.VARIANTS = {v["suffix"]: None for v in declared["variants"].values()}
    ed.EPISODES = REPO / "docs" / "pivot" / "evidence" / "episode-post-mortem" / "episodes.json"
    return ed.compare_command(args)


def added_command(args) -> int:
    """For the `added` and `all` variants: the original and the added risk dates, the onsets on each, and the warnings."""

    declaration = pj.load_declaration()
    rows = load_daily_panel(args.panel)
    audit_panel(rows)
    splits = load_split_declaration(rds.SPLITS)
    digest = panel_sha256(args.panel)
    calendar = [row.date for row in rows]
    tau = declaration.primary
    out: dict = {}
    for path in args.inputs:
        document = json.loads(Path(path).read_text())
        if document["panel_sha256"] != digest:
            raise SystemExit(f"{path} was scored on another panel ({document['panel_sha256'][:8]})")
        variant, h = document["variant"], document["horizon"]
        forecasts = pj.forecasts_from_horizon_document(document)
        grid = pj.build_grid(declaration, h, rows, forecasts[0].dates, splits, scarcity_state={})
        chosen = pj.choose_cutoffs(declaration, {h: grid}, forecasts, calendar)
        onset, outcomes = grid.onset_at(tau, tau), grid.outcomes[tau]
        added = [document["added_dates"][day.isoformat()] for day in grid.dates]
        original = [document["risk_dates"][day.isoformat()] and not a for day, a in zip(grid.dates, added)]
        for forecast in chosen:
            p = forecast.probabilities[tau]
            flags = [1 if q >= c else 0 for q, c in zip(p, forecast.cutoffs[tau])]
            cell = {"days": len(flags), "onsets": sum(onset)}
            for label, inside in (("original", original), ("added", added)):
                idx = [k for k, ok in enumerate(inside) if ok]
                cell[label] = {
                    "risk_dates": len(idx),
                    "onsets_on_them": sum(onset[k] for k in idx),
                    "onsets_flagged": sum(1 for k in idx if flags[k] and onset[k]),
                    "flags": sum(flags[k] for k in idx),
                    "false_alarms": sum(1 for k in idx if flags[k] and not outcomes[k]),
                    "flagged_onsets": [grid.dates[k].isoformat() for k in idx if flags[k] and onset[k]],
                }
            cell["onsets_off_every_risk_date"] = sum(
                onset[k] for k in range(len(flags)) if not original[k] and not added[k]
            )
            cell["unserved_added_dates"] = len(
                [d for d in document.get("risk_dates_with_zero_forecast", {}).get(forecast.name, []) if document["added_dates"][d]]
            )
            out.setdefault(variant, {}).setdefault(forecast.name, {})[str(h)] = cell
    args.output.write_text(json.dumps(out, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    for variant in sorted(out):
        for name in sorted(out[variant]):
            for h, c in sorted(out[variant][name].items()):
                print(
                    f"{variant:6s} {name:26s} h={h} original {c['original']['onsets_flagged']}/{c['original']['onsets_on_them']}"
                    f" ({c['original']['risk_dates']} dates), added {c['added']['onsets_flagged']}/{c['added']['onsets_on_them']}"
                    f" ({c['added']['risk_dates']} dates, {c['unserved_added_dates']} unserved), onsets off every date {c['onsets_off_every_risk_date']}"
                )
    return 0


def refits_command(args) -> int:
    """The refits through 2019 whose gradient-boosted fit is constant, per variant, horizon and parent."""

    out: dict = {}
    for path in args.inputs:
        document = json.loads(Path(path).read_text())
        variant, h = document["variant"], str(document["horizon"])
        for name, trace in document["refits"].items():
            if "gbm" not in name or not trace:
                continue
            through = [r for r in trace if r["first_served"] < "2020-01-01"]
            constant = [
                r for r in through
                if any(
                    cell.get("constant_on_its_training_pairs")
                    for group in r["groups"].values() for key, cell in group["taus"].items() if key == "5"
                )
            ]
            out.setdefault(variant, {}).setdefault(name, {})[h] = {
                "refits_through_2019": len(through),
                "constant_at_5bp": len(constant),
                "first_non_constant_served": next(
                    (r["first_served"] for r in through if r not in constant), None
                ),
                "pairs_at_first_refit": through[0]["pairs"] if through else None,
            }
    args.output.write_text(json.dumps(out, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    for variant in sorted(out):
        for name in sorted(out[variant]):
            print(variant, name, {h: (c["constant_at_5bp"], c["refits_through_2019"]) for h, c in sorted(out[variant][name].items())})
    return 0


# --------------------------------------------------------------------------
# The nowcast
# --------------------------------------------------------------------------

NOWCAST_DECLARATION = REPO / "metadata" / "nowcast.json"


def nowcast_command(args) -> int:
    declared = declared_document()
    cap = float(declared["changes"]["nowcast_target_cap"]["target_cap_bp"])
    last = date.fromisoformat(declared["scoring"]["last_day"])
    require_unlocked([last], where="model_defects_540")
    declaration = nowcast.load_declaration(NOWCAST_DECLARATION)
    desk = _sibling("desk_standard_diagnostic")
    operations = nowcast.load_operations(desk.REVERSE_REPO)
    values, _excluded = nowcast.sameday_on_rrp(operations)
    rows = [r for r in load_daily_panel(args.panel) if r.date <= last]
    seeded = []
    for row in rows:
        v = dict(row.values)
        v[nowcast.RRP_COLUMN] = values.get(row.date)
        seeded.append(type(row)(row.date, v))
    spreads = [r.spread_bps for r in seeded]
    index = {r.date.isoformat(): i for i, r in enumerate(seeded)}
    scored = [d["date"] for d in json.loads(desk.PUBLISHED_DAILY.read_text())["days"] if d["date"] <= last.isoformat()]
    positions = [index[d] for d in scored]
    if min(seeded[p].date for p in positions) < date(2018, 6, 29):
        raise SystemExit("a scored day before 2018-06-29")
    pressure_days = [i for i, p in enumerate(positions) if spreads[p] > 5.0]
    quarter_ends = [i for i, p in enumerate(positions) if float(seeded[p].values.get("quarter_end") or 0) == 1.0]
    settings = dict(penalty=declaration.penalty, min_pairs=declaration.min_pairs, refit_every=declaration.refit_every)

    def walk(features, cap_bp):
        return nowcast.walk_forward(seeded, features, target_cap_bp=cap_bp, **settings)

    primary = declaration.candidates[declaration.primary].features
    control = declaration.candidates["published_only"].features
    series = {"naive": [spreads[p - 1] for p in positions]}
    for label, features in (("rrp_settlement", primary), ("published_only", control)):
        series[f"{label}, uncapped (declared)"] = [walk(features, None).values[p] for p in positions]
        for c in (20.0, 10.0, cap):
            series[f"{label}, target capped at {c:g} bp"] = [walk(features, c).values[p] for p in positions]
    truth = [spreads[p] for p in positions]
    error = {name: [abs(v - t) for v, t in zip(values_, truth)] for name, values_ in series.items()}
    n = len(truth)
    bootstrap = pj.load_declaration().document()["bootstrap"]
    block, rng_seed, draws = float(bootstrap["block_length"]), int(bootstrap["seed"]), int(bootstrap["replications"])

    rng = random.Random(rng_seed)
    counts = []
    for _ in range(draws):
        tally = [0] * n
        for pick in stationary_bootstrap_indices(n, block, rng):
            tally[pick] += 1
        counts.append(tally)

    def interval(difference, members):
        """Mean over the group's days and its 90% stationary-bootstrap interval (days resampled jointly)."""

        means = sorted(
            sum(tally[i] * difference[i] for i in members) / sum(tally[i] for i in members) for tally in counts
        )
        return {
            "mean": sum(difference[i] for i in members) / len(members),
            "lower": means[int(0.05 * draws)],
            "upper": means[int(0.95 * draws) - 1],
            "days": len(members),
        }

    groups = {"all days": list(range(n)), "pressure days (> 5 bp)": pressure_days, "quarter-end days": quarter_ends}
    result: dict = {"cap_bp": cap, "scored_days": n, "bootstrap": {"block": block, "draws": draws, "level": 0.90}, "rows": {}}
    for name, e in error.items():
        entry = {"mae": {g: sum(e[i] for i in m) / len(m) for g, m in groups.items()}}
        entry["minus_naive"] = {g: interval([a - b for a, b in zip(e, error["naive"])], m) for g, m in groups.items()}
        for other in ("rrp_settlement, uncapped (declared)",):
            if name != other and name.startswith("rrp_settlement"):
                entry["minus_declared_uncapped"] = {
                    g: interval([a - b for a, b in zip(e, error[other])], m) for g, m in groups.items()
                }
        result["rows"][name] = entry
    args.output.write_text(json.dumps(result, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    for name, entry in result["rows"].items():
        d = entry["minus_naive"]["all days"]
        print(
            f"{name:50s} MAE {entry['mae']['all days']:.3f} pressure {entry['mae']['pressure days (> 5 bp)']:.2f} "
            f"qend {entry['mae']['quarter-end days']:.2f}  minus naive {d['mean']:+.3f} [{d['lower']:+.3f}, {d['upper']:+.3f}]"
        )
    return 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    run = commands.add_parser("run")
    run.add_argument("--panel", type=Path, required=True)
    run.add_argument("--published", type=Path, required=True)
    run.add_argument("--variant", choices=sorted(FLAGS), required=True)
    run.add_argument("--horizon", type=int, required=True)
    run.add_argument("--candidate")
    run.add_argument("--declared", type=Path, help="risk_date_severity.py run output at this horizon (parent forecasts)")
    run.add_argument("--output", type=Path, required=True)
    run.set_defaults(handler=run_command)
    assemble = commands.add_parser("assemble")
    assemble.add_argument("--output", type=Path, required=True)
    assemble.add_argument("inputs", nargs="+", type=Path)
    assemble.set_defaults(handler=assemble_command)
    compare = commands.add_parser("compare")
    compare.add_argument("--panel", type=Path, required=True)
    compare.add_argument("--output", type=Path, required=True)
    compare.add_argument("--markdown", type=Path)
    compare.add_argument("inputs", nargs="+", type=Path)
    compare.set_defaults(handler=compare_command)
    added = commands.add_parser("added")
    added.add_argument("--panel", type=Path, required=True)
    added.add_argument("--output", type=Path, required=True)
    added.add_argument("inputs", nargs="+", type=Path)
    added.set_defaults(handler=added_command)
    refits = commands.add_parser("refits")
    refits.add_argument("--output", type=Path, required=True)
    refits.add_argument("inputs", nargs="+", type=Path)
    refits.set_defaults(handler=refits_command)
    now = commands.add_parser("nowcast")
    now.add_argument("--panel", type=Path, required=True)
    now.add_argument("--output", type=Path, required=True)
    now.set_defaults(handler=nowcast_command)
    args = parser.parse_args(argv)
    return args.handler(args)


if __name__ == "__main__":
    raise SystemExit(main())
