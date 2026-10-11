"""The projected-reserves model (#545, track S2 of #374): panel columns, forecasts for the judge, and scoring.

A scratch measurement, not a record: it writes CSV, JSON and Markdown to the paths it is given and nothing into
`docs/runs/`. The projection, its flows, the constants and what is reported are in `metadata/projected_reserves.json`,
and the candidates in `metadata/pressure_judge/candidates/`; this script refuses to read either unless it is committed
and unchanged. Every input beyond the published panel is off in every published declaration and switched on for these
runs only. No rule, threshold, onset definition or availability time changes, and no day after 2025-12-31 is read
(`docs/decisions/lockbox.md`).

    PYTHONPATH=src python3 -m repo_model.cli build --raw-root tests/fixtures/snapshots/funding_inputs --output PUBLISHED.csv \\
        --build-cutoff 2026-09-08T21:31:42+00:00 --decision-time 16:00:00
    PYTHONPATH=src python3 scripts/pressure_v1_1.py panel --output AUG.csv
    PYTHONPATH=src python3 scripts/measurement_fields.py panel --panel AUG.csv --output AUG2.csv
    PYTHONPATH=src python3 scripts/net_settlement.py panel --panel AUG2.csv --output AUG3.csv
    PYTHONPATH=src python3 scripts/projected_reserves.py panel --panel AUG3.csv --output AUG4.csv
    PYTHONPATH=src python3 scripts/pressure_judge.py forecasts --panel PUBLISHED.csv --horizon H --published --output OUT/bench_hH.json
    PYTHONPATH=src python3 scripts/risk_date_severity.py run --panel AUG2.csv --published PUBLISHED.csv --horizon H --output OUT/risk_hH.json
    PYTHONPATH=src python3 scripts/pressure_track_q.py forecasts --panel PUBLISHED.csv --horizon H --output OUT/q_hH.json --distribution OUT/qdist_hH.json
    PYTHONPATH=src python3 scripts/projected_reserves.py run --panel AUG4.csv --published PUBLISHED.csv \\
        --risk OUT/risk_hH.json --horizon H --output OUT/pr_hH.json
    PYTHONPATH=src python3 scripts/projected_reserves.py error --panel AUG4.csv --output OUT/error.json
    PYTHONPATH=src python3 scripts/projected_reserves.py score --panel PUBLISHED.csv --bench 'OUT/bench_h{h}.json' \\
        --risk 'OUT/risk_h{h}.json' --ngboost 'OUT/q_h{h}.json' --row 'OUT/pr_h{h}.json' --error OUT/error.json \\
        --output OUT/pr.json --markdown OUT/pr.md

`panel` adds the announced net settlement of the next k days and the projected columns
(`repo_model.projected_reserves`) to the scratch panel, and refuses (`LookAheadError`) a column that differs from
the panel cut at its own row.

`run` scores the model walk-forward at +5 and +10 bp on the shared fold grid (minimum history 61, refit every 21
scored days, scored days through 2025-12-31), and writes the judge's `forecasts` shape with two rows:
`projected_reserves`, and with `--risk` the combined row `risk_gbm+projected`, the risk-date passer's forecast on
every day it is nonzero and the model's probability on every day the passer leaves at 0.

`error` is the projection's error against the reserve level the H.4.1 reports on the Wednesdays that are scored
days, by horizon, beside carrying the as-of level forward unchanged.

`score` is the judge as declared under the weighted rule in force (tiers 1 to 5), the readings of
`docs/pivot/judge-readings-result.md`, onset recall by calendar year and by horizon, Brier score and log loss, and each
row paired against `risk_gbm`, `ngboost_laplace`, calendar climatology and the persistence-logistic. It reuses the
helpers of `scripts/ngboost_laplace_check.py` (#533).
"""

from __future__ import annotations

import argparse
import contextlib
import csv
import hashlib
import importlib.util
import json
import math
import statistics
import sys
from collections import defaultdict
from dataclasses import replace
from datetime import date, time, timedelta
from pathlib import Path
from types import MappingProxyType
from typing import Dict, List
from unittest import mock

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))

from repo_model import contract, measurement_fields, ml, net_settlement as ns, pressure_judge as pj, projected_reserves as pr, scarcity  # noqa: E402
from repo_model.asof import InformationRule  # noqa: E402
from repo_model.baseline import panel_sha256, rolling_exceedance_backtest  # noqa: E402
from repo_model.data import audit_panel, load_daily_panel  # noqa: E402
from repo_model.evaluation_splits import load_split_declaration  # noqa: E402
from repo_model.lockbox import require_unlocked  # noqa: E402

DECLARATION = REPO / "metadata" / "projected_reserves.json"
NET_DECLARATION = REPO / "metadata" / "net_settlement.json"
END = date(2025, 12, 31)
SPLITS = REPO / "metadata" / "evaluation_splits.json"


def _script(name: str):
    spec = importlib.util.spec_from_file_location(f"{name}_script", REPO / "scripts" / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@contextlib.contextmanager
def switched_on():
    """The scarcity state, #377's fields, the net settlement columns and the projected columns in the feature map."""

    fields = {**measurement_fields.COLUMN_FIELDS, **ns.COLUMN_FIELDS, **pr.COLUMN_FIELDS}
    with scarcity.measurement_declaration(), mock.patch.multiple(
        contract,
        FEATURE_FIELDS=MappingProxyType({**contract.FEATURE_FIELDS, **fields}),
        FEATURE_SOURCES=MappingProxyType(
            {
                **contract.FEATURE_SOURCES,
                **{column: tuple(sorted({source for source, _f in pairs})) for column, pairs in fields.items()},
            }
        ),
    ):
        yield


def _cell(value):
    return "" if value is None else repr(float(value))


def _auctions():
    declaration = ns.load_declaration(NET_DECLARATION)
    directory = REPO / declaration["snapshot"]
    manifest = json.loads(next(directory.glob("*.manifest.json")).read_text())
    payload = directory / Path(manifest["path"]).name
    if hashlib.sha256(payload.read_bytes()).hexdigest() != manifest["sha256"]:
        raise SystemExit(f"{payload} does not match its manifest checksum")
    return declaration, ns.load_snapshot(payload, declaration), payload, manifest


# -- panel --------------------------------------------------------------------


def panel_command(args) -> int:
    jr = _script("judge_readings")
    jr.committed_declaration(DECLARATION)
    require_unlocked([END], where="projected_reserves")
    declaration, auctions, _payload, manifest = _auctions()
    rows = [row for row in load_daily_panel(args.panel) if row.date <= END]
    with switched_on():
        rule = InformationRule(
            measurement_fields.load_registry(), pr.READ_FEATURES, decision_time=time(16, 0), horizon=1
        )
        with_ahead = pr.ahead_columns(rows, auctions, declaration)
        built = pr.build_columns(with_ahead, rule, last_day=END)
        pr.check_no_future(with_ahead, built, rule, last_day=END, indices=range(0, len(built), args.check_every))
    with args.panel.open(newline="", encoding="utf-8") as handle:
        base = next(csv.reader(handle))
    header = list(dict.fromkeys(base + list(pr.COLUMNS)))
    with args.output.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerow(header)
        for row in built:
            writer.writerow([row.date.isoformat()] + [_cell(row.values.get(name)) for name in header[1:]])
    present = {name: [r.values[name] for r in built if r.values.get(name) is not None] for name in pr.COLUMNS}
    print(json.dumps({
        "output": str(args.output), "sha256": hashlib.sha256(args.output.read_bytes()).hexdigest(),
        "rows": len(built), "first": built[0].date.isoformat(), "last": built[-1].date.isoformat(),
        "snapshot_sha256": manifest["sha256"], "checked_rows": len(range(0, len(built), args.check_every)),
        "columns": {name: {"rows": len(v), "min": min(v), "median": statistics.median(v), "max": max(v)}
                    for name, v in present.items() if v},
    }, indent=1))
    return 0


# -- run ----------------------------------------------------------------------


def is_risk_date(values, horizon: int, splits) -> bool:
    """Whether the passer serves the day: `ml._RiskDateDesign.member`, which #539's hurdle also uses.

    A day is a risk date when its pressure-day type is not ordinary, or, at h = 1 only (the scored day's own
    settlement is not public earlier, so the passer does not read it), when coupons settle on it.
    """

    if splits.day_type(values) != "ordinary":
        return True
    return horizon == 1 and float(values.get("treasury_settlement_coupons") or 0.0) > 0.0


def combine(
    parent: Dict[str, Dict[str, float]], projected: Dict[str, Dict[str, float]], members: Dict[str, bool]
) -> Dict[str, Dict[str, float]]:
    """#539's hurdle with this model as the every-day hazard: the passer's forecast on a risk date, the model's elsewhere.

    On a risk date the passer's forecast is kept exactly, even where it is 0 (`ml.pressure_risk_date_hurdle_exceedance`
    keeps it). Off a risk date the passer forecasts exactly 0 (checked), and the model is served.
    """

    out: Dict[str, Dict[str, float]] = {}
    for tau, column in projected.items():
        if set(parent[tau]) != set(column) or set(members) != set(column):
            raise SystemExit(f"the parent and the projected model were not scored on the same days at {tau} bp")
        bad = [day for day in column if not members[day] and parent[tau][day] != 0.0]
        if bad:
            raise SystemExit(f"the passer forecasts above 0 on {bad[:3]}, which are not risk dates")
        out[tau] = {day: (parent[tau][day] if members[day] else p) for day, p in column.items()}
    return out


def run_command(args) -> int:
    jr = _script("judge_readings")
    declared = jr.committed_declaration(DECLARATION)
    judge_script = _script("pressure_judge")
    judge_commit = judge_script.require_committed_declaration(pj.DEFAULT_DECLARATION)
    h = args.horizon
    scoring = declared["scoring"]
    if h not in scoring["horizons"]:
        raise SystemExit(f"horizon {h} is not declared")
    last = date.fromisoformat(scoring["last_day"])
    require_unlocked([last], where="projected_reserves")
    rows = load_daily_panel(args.panel)
    audit_panel(rows)
    splits = load_split_declaration(SPLITS)
    registry = measurement_fields.load_registry()
    features = pr.features_at_horizon(h)
    predictor = ml.pressure_logistic_exceedance(features, splits, minimum_history=scoring["minimum_history"])
    with switched_on():
        report = rolling_exceedance_backtest(
            rows, predictor=predictor, model_name=declared["rows"][0], features=features, registry=registry,
            decision_time=time.fromisoformat(scoring["decision_time"]), taus=tuple(float(t) for t in declared["thresholds_bp"]),
            minimum_history=scoring["minimum_history"], refit_every=scoring["refit_every"], end=last, horizon=h,
        )
    by_date = {row.date: row for row in rows}
    forecast = pj.report_forecast(declared["rows"][0], report)
    column = {
        f"{tau:g}": {day.isoformat(): p for day, p in zip(forecast.dates, values)}
        for tau, values in forecast.probabilities.items()
    }
    forecasts = {declared["rows"][0]: column}
    if args.risk:
        parent = json.loads(Path(args.risk).read_text())["forecasts"]["risk_gbm"]
        members = {
            day.isoformat(): is_risk_date(by_date[day].values, h, splits) for day in forecast.dates
        }
        forecasts[declared["rows"][1]] = combine(parent, column, members)
    document = {
        "horizon": h,
        "panel_sha256": panel_sha256(args.published),
        "scratch_panel_sha256": panel_sha256(args.panel),
        "declaration": declared,
        "judge_commit": judge_commit,
        "scored_window": {"first": forecast.dates[0].isoformat(), "last": forecast.dates[-1].isoformat(), "days": len(forecast.dates)},
        "model_settings": {k: v for k, v in report.model_settings.items()},
        "forecasts": forecasts,
    }
    args.output.write_text(json.dumps(document, indent=1, sort_keys=True, default=str) + "\n", encoding="utf-8")
    print(json.dumps({"horizon": h, "output": str(args.output), **document["scored_window"]}))
    return 0


# -- the projection's error -----------------------------------------------------


def _stats(errors: List[float]) -> dict:
    if not errors:
        return {"n": 0}
    return {
        "n": len(errors),
        "mean_error": sum(errors) / len(errors),
        "mean_absolute_error": sum(abs(e) for e in errors) / len(errors),
        "rmse": math.sqrt(sum(e * e for e in errors) / len(errors)),
        "median_absolute_error": statistics.median(abs(e) for e in errors),
    }


def error_command(args) -> int:
    """The projected level against the H.4.1 level of every scored Wednesday, by horizon.

    The scored day T is a Wednesday, so `reserve_balances` on its row is the level the H.4.1 reports for that
    Wednesday. The projection for it was made at the row `h` rows before, from `proj_reserves_h{h}`; the
    comparator carries the level the rule read at that row forward unchanged (the projected level less the
    projected change).
    """

    jr = _script("judge_readings")
    declared = jr.committed_declaration(DECLARATION)
    scoring = declared["scoring"]
    first, last = date.fromisoformat(scoring["first_day"]), date.fromisoformat(scoring["last_day"])
    require_unlocked([last], where="projected_reserves")
    rows = load_daily_panel(args.panel)
    out = {"horizons": {}, "by_year": {}}
    for h in scoring["horizons"]:
        projected, carried, by_year = [], [], defaultdict(list)
        for t in range(h, len(rows)):
            day = rows[t].date
            if day.weekday() != 2 or not first <= day <= last:
                continue
            realised = rows[t].values.get("reserve_balances")
            source = rows[t - h].values
            proj = source.get(f"proj_reserves_h{h}")
            dist = source.get(f"proj_dist_h{h}")
            change = source.get(f"proj_change_h{h}")
            if None in (realised, proj, dist, change):
                continue
            assets = proj / (dist / 100.0 + pr.SATIATION)
            start = proj - change / 100.0 * assets
            projected.append(proj - realised)
            carried.append(start - realised)
            by_year[day.year].append((proj - realised, start - realised))
        out["horizons"][str(h)] = {"projected": _stats(projected), "carried_forward": _stats(carried)}
        out["by_year"][str(h)] = {
            str(year): {"projected": _stats([a for a, _b in pairs]), "carried_forward": _stats([b for _a, b in pairs])}
            for year, pairs in sorted(by_year.items())
        }
    out["panel_sha256"] = panel_sha256(args.panel)
    args.output.write_text(json.dumps(out, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(args.output)}))
    return 0


def error_markdown(error: dict) -> str:
    lines = ["## Projection error against the H.4.1 level of the scored Wednesdays (USD billions)", "",
             "Error is projected (or carried-forward) minus realised. The comparator carries the as-of level forward unchanged.", "",
             "| h | Wednesdays | projected: mean | MAE | RMSE | carried forward: mean | MAE | RMSE |", "|---|---|---|---|---|---|---|---|"]
    for h, cell in error["horizons"].items():
        p, c = cell["projected"], cell["carried_forward"]
        if not p["n"]:
            continue
        lines.append(f"| {h} | {p['n']} | {p['mean_error']:+.1f} | {p['mean_absolute_error']:.1f} | {p['rmse']:.1f} "
                     f"| {c['mean_error']:+.1f} | {c['mean_absolute_error']:.1f} | {c['rmse']:.1f} |")
    lines += ["", "By calendar year (MAE, projected / carried forward):", "", "| h | " + " | ".join(
        sorted({y for h in error["by_year"].values() for y in h})) + " |"]
    years = sorted({y for h in error["by_year"].values() for y in h})
    lines.append("|---|" + "---|" * len(years))
    for h, by_year in error["by_year"].items():
        cells = []
        for y in years:
            c = by_year.get(y)
            cells.append("" if not c or not c["projected"]["n"] else
                         f"{c['projected']['mean_absolute_error']:.0f} / {c['carried_forward']['mean_absolute_error']:.0f}")
        lines.append(f"| {h} | " + " | ".join(cells) + " |")
    lines.append("")
    return "\n".join(lines)


# -- score ------------------------------------------------------------------------


LOG_LOSS_FLOOR = 1e-6


def losses(probabilities, outcomes) -> dict:
    """Pooled Brier score and log loss (probabilities floored at 1e-6, so a probability of 0 is a finite penalty)."""

    count = len(outcomes)
    if count != len(probabilities):
        raise SystemExit("a forecast and its outcomes are not on the same days")
    clipped = [min(1.0 - LOG_LOSS_FLOOR, max(LOG_LOSS_FLOOR, p)) for p in probabilities]
    return {
        "days": count,
        "brier": sum((p - y) ** 2 for p, y in zip(probabilities, outcomes)) / count,
        "log_loss": -sum(math.log(p) if y else math.log(1.0 - p) for p, y in zip(clipped, outcomes)) / count,
    }


def score_command(args) -> int:
    ngc = _script("ngboost_laplace_check")
    jr = _script("judge_readings")
    judge_script = _script("pressure_judge")
    document = jr.committed_declaration(DECLARATION)
    judge_commit = judge_script.require_committed_declaration(pj.DEFAULT_DECLARATION)
    judge_script.require_committed_file(pj.DEFAULT_WEIGHTED_MISS)
    base = pj.load_declaration()
    if not pj.load_weighted_miss().in_force:
        raise SystemExit("the weighted miss rule is not in force; this score reads the rule in force")
    scoring = document["scoring"]
    if list(base.horizons) != scoring["horizons"] or base.last_day != date.fromisoformat(scoring["last_day"]):
        raise SystemExit("the judge's horizons or last day are not the declared ones")
    rows_names = document["rows"]
    passers = document["risk_date_passers"]
    references = [base.climatology, base.persistence, "ngboost_laplace"]
    names = [*rows_names, *passers, *references]
    rows = load_daily_panel(args.panel)
    audit_panel(rows)
    splits = load_split_declaration(SPLITS)
    digest = panel_sha256(args.panel)
    horizons = base.horizons
    forecasts, panels = [], {}
    for h in horizons:
        for label, template in (("bench", args.bench), ("risk", args.risk), ("ngboost", args.ngboost), ("row", args.row)):
            doc = jr._load(template, h)
            if doc["panel_sha256"] != digest and label in ("bench", "row"):
                raise SystemExit(f"{template.format(h=h)} was scored on another panel")
            panels[f"{label}_h{h}"] = doc["panel_sha256"]
            forecasts.extend(f for f in pj.forecasts_from_horizon_document(doc) if f.name in names)
    unique = {}
    for f in forecasts:
        unique.setdefault((f.name, f.horizon), f)
    forecasts = list(unique.values())
    missing = [(n, h) for n in names for h in horizons if (n, h) not in unique]
    if missing:
        raise SystemExit(f"no forecast for {missing[:3]}")
    states = {h: judge_script._scarcity_states(h, base.last_day) for h in horizons}

    def grids_of(items):
        out = {}
        for h in horizons:
            reference = next(f for f in items if f.horizon == h and f.name == base.climatology)
            out[h] = pj.build_grid(base, h, rows, reference.dates, splits, scarcity_state=states[h])
        return out

    calendar = [row.date for row in rows]
    place = {day: k for k, day in enumerate(calendar)}
    grids = grids_of(forecasts)
    tau = base.primary
    shared: Dict[str, object] = {"readings": {}, "training_checks": {}, "judge": {}, "judge_tables": {}}
    per_row: Dict[str, Dict[str, object]] = {r: {"by_year": {}, "only_row": {}, "blocks": {}, "paired": {}} for r in rows_names}
    original = pj.false_alarm_weights
    runs = [
        ("unweighted", replace(base, weighted_miss=pj.load_weighted_miss(applied=False)), original),
        ("weighted", replace(base, weighted_miss=pj.load_weighted_miss(applied=True)), original),
    ]
    for key, declaration, weight_fn in runs:
        pj.false_alarm_weights = weight_fn
        try:
            chosen = pj.choose_cutoffs(declaration, grids, forecasts, calendar)
            by_name: Dict[str, Dict[int, "pj.Forecast"]] = defaultdict(dict)
            for f in chosen:
                by_name[f.name][f.horizon] = f
            series = {n: jr.RowSeries(declaration, grids, by_name, n, place, weight_fn) for n in names}
            shared["readings"][key] = {
                n: jr.readings_for(declaration, series[n], limited_weighted=key.startswith("weighted")) for n in names
            }
            judged = pj.judge(declaration, grids_of(chosen), chosen, calendar=calendar, holdouts=judge_script._holdouts())
            shared["judge"][key] = {
                n: {"verdict": c["verdict"], "onset_warning": c["tiers"]["onset_warning"], "tiers": c["tiers"]}
                for n, c in judged["candidates"].items() if n in names
            }
            shared["judge_tables"][key] = judge_script.summary_tables(
                {**judged, "candidates": {n: c for n, c in judged["candidates"].items() if n in names}}
            )
            for n in names:
                near = judged["candidates"][n]["tiers"]["onset_warning"]["lead_at_least_1"]
                mine = shared["readings"][key][n]["a"]
                theirs = near["worst_weighted_false_alarms_per_onset" if key == "weighted" else "worst_false_alarms_per_onset"]
                agree = (
                    abs(near["onsets_flagged"] - mine["onsets_flagged"]) < 1e-9
                    and abs(theirs - mine["false_alarms_per_onset_limited"]) < 1e-9
                    and abs(near["recall"]["mean"] - mine["recall"]) < 1e-9
                )
                if not agree:
                    raise SystemExit(f"reading (a) of {n} under the {key} rule does not match the judge's own row")
            if key != "weighted":
                continue
            first = horizons[0]
            days = series[rows_names[0]].days
            onset = series[rows_names[0]].onset
            caught = {n: [max(series[n].flags[h][k] for h in series[n].horizons) for k in range(len(days))] for n in names}
            at_first = {d: k for k, d in enumerate(grids[first].dates)}
            groups = {
                dim: [grids[first].groups[dim][at_first[d]] for d in days]
                for dim in dict.fromkeys(declaration.groupings + ("regime",))
            }
            shared["per_horizon"] = {
                n: {str(h): int(sum(1 for o, f in zip(onset, series[n].flags[h]) if o and f)) for h in series[n].horizons}
                for n in names
            }
            for row_name in rows_names:
                cell = per_row[row_name]
                cell["by_year"] = {n: ngc.warned_by_year(days, onset, caught[n]) for n in [row_name, *passers, *references]}
                only = ngc.only_this_row_warns(days, onset, caught[row_name], [caught[n] for n in passers])
                reverse = ngc.only_this_row_warns(days, onset, ngc._any_of([caught[n] for n in passers]), [caught[row_name]])
                cell["only_row"] = {
                    "row_only": [
                        {"day": d.isoformat(), "horizons": [h for h in series[row_name].horizons if series[row_name].flags[h][days.index(d)]]}
                        for d in only
                    ],
                    "passers_only": [d.isoformat() for d in reverse],
                    "onsets": int(sum(onset)),
                    "row_warns": int(sum(1 for o, c in zip(onset, caught[row_name]) if o and c)),
                    "at_least_one_passer_warns": int(sum(1 for o, c in zip(onset, ngc._any_of([caught[n] for n in passers])) if o and c)),
                    "each_passer_warns": {n: int(sum(1 for o, c in zip(onset, caught[n]) if o and c)) for n in passers},
                }
                for h in horizons:
                    f = by_name[row_name][h]
                    blocks = ngc.refit_blocks(f.probabilities[tau], f.cutoffs[tau], f.dates, declaration.cutoff_refit_every)
                    cell["blocks"][str(h)] = {
                        **ngc.block_summary(blocks),
                        "days_probability_zero": sum(1 for p in f.probabilities[tau] if p == 0.0),
                        "days": len(f.dates),
                        "distinct_probabilities": len(set(f.probabilities[tau])),
                        "blocks": blocks,
                    }
                for ref in document["pair_against"]:
                    cell["paired"][ref] = {"brier": {}, "recall": {}}
                    for h in horizons:
                        row_p, ref_p = (by_name[n][h].probabilities[tau] for n in (row_name, ref))
                        cell["paired"][ref]["brier"][str(h)] = ngc.paired_brier(declaration, grids[h], row_p, ref_p, (row_name, ref, h))
                    cell["paired"][ref]["recall"] = ngc.paired_recall(
                        declaration, days, onset, caught[row_name], caught[ref], groups, (row_name, ref)
                    )
        finally:
            pj.false_alarm_weights = original
    shared["loss"] = {
        n: {
            str(h): losses(unique[(n, h)].probabilities[tau], grids[h].outcomes[tau])
            for h in horizons
        }
        for n in names
    }
    error = json.loads(Path(args.error).read_text())
    result = {
        **shared,
        "rows": per_row,
        "projection_error": error,
        "declaration": {"path": "metadata/projected_reserves.json", "judge_commit": judge_commit},
        "provenance": {"panel_sha256": digest, "forecast_panels": panels},
    }
    args.output.write_text(json.dumps(result, indent=1, sort_keys=True, default=str) + "\n", encoding="utf-8")
    if args.markdown:
        args.markdown.write_text(markdown(result, document, ngc), encoding="utf-8")
    print(json.dumps({"output": str(args.output)}))
    return 0


def horizon_markdown(result: dict, document: dict) -> str:
    horizons = sorted({h for cells in result["per_horizon"].values() for h in cells}, key=int)
    lines = ["## Onsets warned at each horizon (weighted rule, 26 onsets)", "",
             f"The ceiling: {document['ceiling']}.", "",
             "| row | " + " | ".join(f"h = {h}" for h in horizons) + " |", "|---|" + "---|" * len(horizons)]
    for n, cells in result["per_horizon"].items():
        lines.append(f"| {n} | " + " | ".join(str(cells.get(h, "")) for h in horizons) + " |")
    lines += ["", "## Brier score and log loss at +5 bp (pooled over the scored days; log loss floors a probability at 1e-6)", "",
              "| row | " + " | ".join(f"h = {h}: Brier / log loss" for h in horizons) + " |", "|---|" + "---|" * len(horizons)]
    for n, cells in result["loss"].items():
        lines.append(f"| {n} | " + " | ".join(
            f"{cells[h]['brier']:.4f} / {cells[h]['log_loss']:.4f}" if h in cells else "" for h in horizons) + " |")
    lines.append("")
    return "\n".join(lines)


def markdown(result: dict, document: dict, ngc) -> str:
    shared = {k: result[k] for k in ("readings", "training_checks", "judge", "judge_tables")}
    out = ["# Reserves projected to the scored day (#545)", ""]
    for index, row_name in enumerate(document["rows"]):
        view = {**shared, **result["rows"][row_name]}
        shown = {**document, "row": row_name, "risk_date_passers": document["risk_date_passers"] + ["ngboost_laplace"]}
        text = ngc.markdown(view, shown).replace("# The ngboost_laplace check (#533)", f"# {row_name}")
        if index:
            # the judge's tables and tier 1 readings are shared: print them once
            text = text.split("## Onsets warned by calendar year", 1)
            text = "# " + row_name + "\n\n## Onsets warned by calendar year" + text[1]
        out.append(text)
    out.append(horizon_markdown(result, document))
    out.append(error_markdown(result["projection_error"]))
    return "\n".join(out)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    commands = parser.add_subparsers(dest="command", required=True)
    panel = commands.add_parser("panel")
    panel.add_argument("--panel", type=Path, required=True)
    panel.add_argument("--output", type=Path, required=True)
    panel.add_argument("--check-every", type=int, default=1)
    panel.set_defaults(run=panel_command)
    error = commands.add_parser("error")
    error.add_argument("--panel", type=Path, required=True)
    error.add_argument("--output", type=Path, required=True)
    error.set_defaults(run=error_command)
    run = commands.add_parser("run")
    run.add_argument("--panel", type=Path, required=True)
    run.add_argument("--published", type=Path, required=True)
    run.add_argument("--risk", type=Path)
    run.add_argument("--horizon", type=int, required=True)
    run.add_argument("--output", type=Path, required=True)
    run.set_defaults(run=run_command)
    score = commands.add_parser("score")
    score.add_argument("--panel", type=Path, required=True)
    for flag in ("bench", "risk", "ngboost", "row", "error"):
        score.add_argument(f"--{flag}", required=True)
    score.add_argument("--output", type=Path, required=True)
    score.add_argument("--markdown", type=Path)
    score.set_defaults(run=score_command)
    args = parser.parse_args(argv)
    return args.run(args)


if __name__ == "__main__":
    raise SystemExit(main())
