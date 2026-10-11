"""A calibrated every-day hazard for the risk-date passers: the hurdle model (#539, of #374).

A scratch measurement, not a record: it writes JSON and Markdown to the paths it is given and nothing into
`docs/runs/`. The variants are in `metadata/risk_date_hurdle.json`, which this script refuses to read unless it
is committed and unchanged. P(pressure) = P(risk date) x the passer's own forecast + P(ordinary day) x an
every-day hazard (`ml.pressure_risk_date_hurdle_exceedance`): a risk date keeps the parent's forecast exactly and
any other day is served a walk-forward calibrated ridge logistic on SOFR's 99th and 75th percentiles above IORB
(and, in the `state` variants, the as-of reserve scarcity state). No rule, threshold, onset definition, cut-off
rule or availability time changes: the judge chooses each variant's cut-offs from its own training window, as for
every candidate. No day after 2025-12-31 is read.

    PYTHONPATH=src python3 scripts/risk_date_hurdle.py declare      # once, before any score
    PYTHONPATH=src python3 scripts/risk_date_hurdle.py run --panel AUG2.csv --published PUBLISHED.csv \\
        --horizon H --output OUT/hurdle_hH.json [--candidate PARENT]
    PYTHONPATH=src python3 scripts/pressure_judge.py judge --panel PUBLISHED.csv --rule weighted \\
        --output OUT/judge_weighted.json --markdown OUT/judge_weighted.md OUT/bench_h?.json OUT/risk_h?.json OUT/hurdle_h?.json
    PYTHONPATH=src python3 scripts/risk_date_hurdle.py compare --panel PUBLISHED.csv \\
        --output OUT/compare.json --markdown OUT/compare.md OUT/bench_h?.json OUT/risk_h?.json OUT/hurdle_h?.json
    PYTHONPATH=src python3 scripts/risk_date_hurdle.py readings --panel PUBLISHED.csv \\
        --output OUT/readings.json --markdown OUT/readings.md OUT/bench_h?.json OUT/risk_h?.json OUT/hurdle_h?.json

`run` writes one forecast per parent and variant (`<parent><variant>`). `compare` puts each variant beside its
parent, with intervals, split by regime and pressure-day type, and reports recall by year (2018, 2020 and 2024
called out), the Brier score and the log loss against the parent, and the predicted against the realised
pressure rate in each regime; `readings` reports tier 1 under readings (a), (b) and (e) of
`docs/pivot/judge-readings-result.md`, under both rules.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import math
import sys
from collections import defaultdict
from dataclasses import replace
from datetime import date, time
from pathlib import Path
from typing import Dict, List, Optional, Sequence

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))

from repo_model import measurement_fields, ml  # noqa: E402
from repo_model.baseline import panel_sha256, rolling_exceedance_backtest  # noqa: E402
from repo_model.data import audit_panel, load_daily_panel  # noqa: E402
from repo_model.evaluation_splits import load_split_declaration  # noqa: E402
from repo_model.lockbox import require_unlocked  # noqa: E402

DECLARATION = REPO / "metadata" / "risk_date_hurdle.json"
PARENTS = REPO / "metadata" / "risk_date_severity.json"
CANDIDATES = REPO / "metadata" / "pressure_judge" / "candidates"
EPISODES = REPO / "docs" / "pivot" / "evidence" / "episode-post-mortem" / "episodes.json"
VARIANTS = tuple(ml.HURDLE_VARIANTS)
PARENT_NAMES = ("risk_gbm", "risk_gbm_base", "risk_logistic", "risk_logistic_base", "risk_quantile_skewt_base")


def _load(name: str):
    spec = importlib.util.spec_from_file_location(f"{name}_script", REPO / "scripts" / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


rds = _load("risk_date_severity")




# -- the declaration -------------------------------------------------------------------------------------------

VARIANT_TEXT = {
    "+hurdle_platt": "the hazard on spread_bps, sofr_p75_iorb_bps and sofr_p99_iorb_bps, mapped through a Platt curve fitted walk-forward",
    "+hurdle_isotonic": "the same hazard, mapped through an isotonic curve fitted walk-forward",
    "+hurdle_state_platt": "the hazard on those three and the as-of reserve scarcity state, mapped through a Platt curve fitted walk-forward",
    "+hurdle_state_isotonic": "the same four-input hazard, mapped through an isotonic curve fitted walk-forward",
}


def declaration_document(parents: dict) -> dict:
    return {
        "status": (
            "declared by the pull request that closes #539 before any score was computed; nothing here is tuned on a "
            "scored day; the variants, their inputs and the calibration scheme are the pull request's, stated and not "
            "chosen on a score"
        ),
        "scoring": parents["scoring"],
        "thresholds_bp": parents["thresholds_bp"],
        "horizons": parents["horizons"],
        "parents": {name: parents["candidates"][name] for name in PARENT_NAMES},
        "parents_declaration": "metadata/risk_date_severity.json (unchanged: the risk dates, the features, the estimators)",
        "model": {
            "formula": "P(pressure) = P(risk date) x the passer's own forecast + P(ordinary day) x the every-day hazard",
            "weights": "whether a day is a risk date is a fact about the calendar known in advance (docs/pivot/construction-gaps-result.md), so P(risk date) is 1 on a risk date and 0 on any other day; a risk date keeps the parent's forecast exactly",
            "hazard": "a ridge logistic (ml.PRESSURE_LOGISTIC_SETTINGS) of spread > tau, one per threshold, fitted on the direct pairs of every training day under the as-of rule, mapped through the variant's calibration curve",
            "calibration": {
                "scheme": "walk-forward, refit with the model on the judge's 21-day cut-off cadence: the refit's training pairs, in date order, are cut into ml.HURDLE_CALIBRATION_BLOCKS blocks; the hazard fitted on blocks 0..k-1 forecasts block k (k >= 1) and the curve is fitted on those out-of-sample forecasts and their labels; the final hazard, fitted on every training pair, is mapped through it",
                "blocks": ml.HURDLE_CALIBRATION_BLOCKS,
                "identity_until": "the out-of-sample pairs number probability_calibration.MINIMUM_PAIRS (250) and hold MINIMUM_EVENTS (5) events, as the bake-off's gate (#138)",
                "methods": {"platt": "probability_calibration._platt (a logistic of the label on logit(p))", "isotonic": "probability_calibration._isotonic (the CORP isotonic fit, a right-continuous step function)"},
            },
            "missing_input": "a served day whose hazard inputs are not all public is served the hazard fitted without the missing ones (always including the spread), calibrated the same way, instead of 0",
            "regime_input": "the as-of reserve scarcity state (scarcity.py, 0 to 3) is the regime-like input of the state variants. The regime labels of metadata/evaluation_splits.json are drawn after the fact (metadata/hindsight_regimes.json) and are not an input: whether they may be is Eleonora's decision",
        },
        "variants": {
            name: {"inputs": list(ml.HURDLE_VARIANTS[name][0]), "calibration": ml.HURDLE_VARIANTS[name][1], "reading": VARIANT_TEXT[name]}
            for name in VARIANTS
        },
        "cutoffs": "the judge's cutoff_rule, from each variant's own training window, unchanged: one cut-off per threshold and horizon",
        "judging": "the judge as declared (metadata/pressure_judge.json): tiers 1, 3 and 5, h = 1 to 5, +5 and +10 bp, under the flat and the weighted rule; tier 1 also under readings (b) and (e) of docs/pivot/judge-readings-result.md",
        "log_loss": {"floor": "probability_calibration.PROBABILITY_FLOOR (1e-6): a forecast is clipped to [floor, 1 - floor] before its log loss is taken, so a parent's exact 0 on a pressure day costs ln(1e6)"},
        "published": "nothing: the variants are off in every published declaration; no rule, threshold, definition or availability time changes",
    }


def declare_command(args) -> int:
    parents = json.loads(PARENTS.read_text(encoding="utf-8"))
    document = declaration_document(parents)
    DECLARATION.write_text(json.dumps(document, indent=2) + "\n", encoding="utf-8")
    for parent in document["parents"]:
        base = json.loads((CANDIDATES / f"{parent}.json").read_text(encoding="utf-8"))
        for variant in VARIANTS:
            entry = dict(base)
            entry["track"] = "H (#539)"
            entry["parent"] = parent
            entry["calibration"] = (
                "the parent's risk-date forecast on a risk date; on any other day a walk-forward "
                f"{ml.HURDLE_VARIANTS[variant][1]}-calibrated every-day hazard: {VARIANT_TEXT[variant]}; a day missing an input is served "
                "the hazard fitted without it; metadata/risk_date_hurdle.json"
            )
            (CANDIDATES / f"{parent}{variant}.json").write_text(json.dumps(entry, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"declaration": str(DECLARATION), "candidates": len(document["parents"]) * len(VARIANTS)}))
    return 0


# -- run ----------------------------------------------------------------------------------------------------


def shared(predictor):
    """`predictor` with each fold's fit remembered, so the variants of one parent share it."""

    memo: dict = {}

    def call(train_rows, feature_rows, taus, information=None, histories=None):
        key = (len(train_rows), train_rows[-1].date, feature_rows[0].date, len(feature_rows), tuple(taus))
        if key not in memo:
            memo[key] = predictor(train_rows, feature_rows, taus, information, histories)
        return memo[key]

    return call


def run_command(args) -> int:
    declared = rds.committed_declaration(DECLARATION)
    parents = json.loads(PARENTS.read_text(encoding="utf-8"))
    h = args.horizon
    if h not in declared["horizons"]:
        raise SystemExit(f"horizon {h} is not declared")
    last = date.fromisoformat(declared["scoring"]["last_day"])
    require_unlocked([last], where="risk_date_hurdle")
    rows = load_daily_panel(args.panel)
    audit_panel(rows)
    splits = load_split_declaration(rds.SPLITS)
    registry = measurement_fields.load_registry()
    taus = tuple(float(t) for t in declared["thresholds_bp"])
    minimum = declared["scoring"]["minimum_history"]
    names = [args.candidate] if args.candidate else list(declared["parents"])
    forecasts, settings = {}, {}
    for parent in names:
        spec = declared["parents"][parent]
        parent_features = rds.features_at_horizon(parents, spec, h)
        parent_predictor = shared(ml.pressure_risk_date_exceedance(spec["kind"], parent_features, splits, minimum))
        for variant in VARIANTS:
            inputs = declared["variants"][variant]["inputs"]
            features = tuple(dict.fromkeys(parent_features + tuple(inputs)))
            predictor = ml.pressure_risk_date_hurdle_exceedance(
                spec["kind"], parent_features, splits, minimum, variant=variant, parent_predictor=parent_predictor
            )
            with rds.switched_on():
                report = rolling_exceedance_backtest(
                    rows,
                    predictor=predictor,
                    model_name=parent + variant,
                    features=features,
                    registry=registry,
                    decision_time=time.fromisoformat(declared["scoring"]["decision_time"]),
                    taus=taus,
                    minimum_history=minimum,
                    refit_every=declared["scoring"]["refit_every"],
                    end=last,
                    horizon=h,
                )
            forecasts[parent + variant] = rds.column(report)
            settings[parent + variant] = _settings(report)
            print(json.dumps({"horizon": h, "parent": parent, "variant": variant, "done": True}), flush=True)
    document = {
        "horizon": h,
        "panel_sha256": panel_sha256(args.published),
        "scratch_panel_sha256": panel_sha256(args.panel),
        "declaration": declared,
        "declarations": settings,
        "forecasts": forecasts,
    }
    args.output.write_text(json.dumps(document, indent=1, sort_keys=True, default=str) + "\n", encoding="utf-8")
    print(json.dumps({"horizon": h, "output": str(args.output)}))
    return 0


def _settings(report):
    return {
        "features": list(report.features),
        "model_settings": dict(report.model_settings),
        "ml_libraries": None if report.ml_libraries is None else dict(report.ml_libraries),
    }


# -- compare ------------------------------------------------------------------------------------------------


def _f(value, places=3):
    return "-" if value is None else f"{value:.{places}f}"


def _interval(cell):
    if cell is None or cell.get("mean") is None:
        return "-"
    if "interval" not in cell:
        return f"{cell['mean']:+.4f} (no interval)"
    return f"{cell['mean']:+.4f} [{cell['interval']['lower']:+.4f}, {cell['interval']['upper']:+.4f}]"


def _grids(pj, declaration, rows, splits, states, items):
    out = {}
    for h in declaration.horizons:
        reference = next(f for f in items if f.horizon == h and f.name == declaration.climatology)
        out[h] = pj.build_grid(declaration, h, rows, reference.dates, splits, scarcity_state=states[h])
    return out


def _load_forecasts(pj, digest, inputs):
    forecasts = []
    for path in inputs:
        document = json.loads(Path(path).read_text())
        if document["panel_sha256"] != digest:
            raise SystemExit(f"{path} was scored on another panel ({document['panel_sha256'][:8]})")
        forecasts.extend(pj.forecasts_from_horizon_document(document))
    return forecasts


def log_loss_vectors(probabilities, reference, outcomes, members, floor):
    """Per-day vectors for the paired log loss: inside the cell, and the reference's loss minus the variant's."""

    def loss(p, y):
        q = min(1.0 - floor, max(floor, float(p)))
        return -math.log(q if y else 1.0 - q)

    inside = [1.0 if k in members else 0.0 for k in range(len(outcomes))]
    return [inside, [inside[k] * (loss(reference[k], outcomes[k]) - loss(probabilities[k], outcomes[k])) for k in range(len(outcomes))]]


def compare_command(args) -> int:
    from repo_model import pressure_judge as pj
    from repo_model import probability_calibration

    pj_script = _load("pressure_judge")
    declared = rds.committed_declaration(DECLARATION)
    declaration = replace(pj.load_declaration(), weighted_miss=pj.load_weighted_miss(applied=(args.rule == "weighted")))
    rows = load_daily_panel(args.panel)
    audit_panel(rows)
    splits = load_split_declaration(rds.SPLITS)
    by_date = {row.date: row for row in rows}
    forecasts = _load_forecasts(pj, panel_sha256(args.panel), args.inputs)
    states = {h: pj_script._scarcity_states(h, declaration.last_day) for h in declaration.horizons}
    calendar = [row.date for row in rows]
    chosen = pj.choose_cutoffs(declaration, _grids(pj, declaration, rows, splits, states, forecasts), forecasts, calendar)
    grids = _grids(pj, declaration, rows, splits, states, chosen)
    tau = declaration.primary
    by_name = {}
    for forecast in chosen:
        by_name.setdefault(forecast.name, {})[forecast.horizon] = forecast
    parents = list(declared["parents"])
    variants = [f"{p}{v}" for p in parents for v in VARIANTS]
    parent_of = {f"{p}{v}": p for p in parents for v in VARIANTS}
    for name in variants + parents + [declaration.climatology, declaration.persistence]:
        if name not in by_name:
            raise SystemExit(f"no forecasts for {name!r} in the inputs")
    horizons = list(declaration.horizons)
    seed = declaration.document()["bootstrap"]["seed"]

    common = sorted(set.intersection(*(set(grids[h].dates) for h in horizons)))
    place = {h: {day: k for k, day in enumerate(grids[h].dates)} for h in horizons}
    onset = [float(grids[1].onset[place[1][day]]) for day in common]
    count = len(common)

    def caught(name):
        out = []
        for i, day in enumerate(common):
            hit = 0.0
            for h in horizons:
                f = by_name[name][h]
                k = place[h][day]
                if f.probabilities[tau][k] >= f.cutoffs[tau][k]:
                    hit = 1.0
            out.append(hit * onset[i])
        return out

    everyone = variants + parents
    caught_by = {name: caught(name) for name in everyone}
    years = sorted({day.year for day in common})
    regimes = [grids[1].groups["regime"][place[1][day]] for day in common]
    kinds = [grids[1].groups["day_type"][place[1][day]] for day in common]
    cells_for = {
        "all": [1.0] * count,
        **{f"year {y}": [1.0 if day.year == y else 0.0 for day in common] for y in years},
        **{f"regime {r}": [1.0 if x == r else 0.0 for x in regimes] for r in sorted(set(regimes))},
        **{f"day type {t}": [1.0 if x == t else 0.0 for x in kinds] for t in sorted(set(kinds))},
    }
    recall_stats = {
        "recall": pj._ratio(1, 0),
        "reference_recall": pj._ratio(2, 0),
        "recall_difference": lambda t: (t[1] - t[2]) / t[0] if t[0] else None,
    }
    recall = {}
    for name in variants:
        reference = parent_of[name]
        cells = {
            cell: [
                [m * o for m, o in zip(inside, onset)],
                [m * c for m, c in zip(inside, caught_by[name])],
                [m * c for m, c in zip(inside, caught_by[reference])],
            ]
            for cell, inside in cells_for.items()
        }
        recall[name] = pj._bootstrap(declaration, cells, recall_stats, count, seed=pj._seed(seed, "recall", name, "vs_parent"))
    caught_count = {
        name: {cell: int(sum(m * c for m, c in zip(inside, caught_by[name]))) for cell, inside in cells_for.items()}
        for name in everyone
    }
    onsets_in = {cell: int(sum(m * o for m, o in zip(inside, onset))) for cell, inside in cells_for.items()}

    flags = {}
    for name in everyone:
        flags[name] = {}
        for h in horizons:
            grid = grids[h]
            f = by_name[name][h]
            raised = [1 if q >= c else 0 for q, c in zip(f.probabilities[tau], f.cutoffs[tau])]
            risk = [rds.is_risk_date(splits, by_date[day].values, h) for day in grid.dates]
            outcomes, onsets = grid.outcomes[tau], grid.onset_at(tau, tau)
            n_onsets = sum(onsets)
            cell = {"onsets": n_onsets}
            for label, keep in (("all_days", [True] * len(raised)), ("risk_dates", risk), ("other_days", [not r for r in risk])):
                inside = [k for k, ok in enumerate(keep) if ok]
                flagged = [k for k in inside if raised[k]]
                cell[label] = {
                    "days": len(inside),
                    "flags": len(flagged),
                    "flags_on_a_pressure_day": sum(1 for k in flagged if outcomes[k]),
                    "false_alarms": sum(1 for k in flagged if not outcomes[k]),
                    "onsets_flagged": sum(1 for k in flagged if onsets[k]),
                }
                cell[label]["false_alarms_per_onset"] = cell[label]["false_alarms"] / n_onsets if n_onsets else None
            flags[name][str(h)] = cell

    floor = probability_calibration.PROBABILITY_FLOOR
    brier, log_loss, calibration = {}, {}, {}
    for h in horizons:
        grid = grids[h]
        outcomes = grid.outcomes[tau]
        n = len(outcomes)
        groups = {"all": list(range(n))}
        for dimension in ("regime", "day_type"):
            for label in sorted(set(grid.groups[dimension])):
                groups[f"{dimension} {label}"] = [k for k, x in enumerate(grid.groups[dimension]) if x == label]
        years_of = [day.year for day in grid.dates]
        for year in sorted(set(years_of)):
            groups[f"year {year}"] = [k for k, y in enumerate(years_of) if y == year]
        clim = by_name[declaration.climatology][h].probabilities[tau]
        pers = by_name[declaration.persistence][h].probabilities[tau]
        for name in everyone:
            p = by_name[name][h].probabilities[tau]
            standard = pj._bootstrap(
                declaration,
                {g: pj._paired_vectors(p, clim, pers, outcomes, members) for g, members in groups.items()},
                pj._PAIRED_STATS, n, seed=pj._seed(seed, "brier", name, h, "standard"),
            )
            calibration.setdefault(name, {})[str(h)] = {
                g: {
                    "days": standard[g]["days"],
                    "mean_predicted": sum(p[k] for k in members) / len(members) if members else None,
                    "realised_frequency": sum(outcomes[k] for k in members) / len(members) if members else None,
                    "realised_minus_predicted": standard[g]["realised_minus_predicted"],
                }
                for g, members in groups.items()
            }
            if name in parent_of:
                ref_p = by_name[parent_of[name]][h].probabilities[tau]
                versus = pj._bootstrap(
                    declaration,
                    {g: pj._paired_vectors(p, ref_p, pers, outcomes, members) for g, members in groups.items()},
                    pj._PAIRED_STATS, n, seed=pj._seed(seed, "brier", name, h, "vs_parent"),
                )
                brier.setdefault(name, {})[str(h)] = {
                    g: {
                        "days": standard[g]["days"],
                        "vs_climatology": standard[g]["brier_difference_vs_climatology"],
                        "vs_persistence_logistic": standard[g]["brier_difference_vs_persistence"],
                        "vs_parent": versus[g]["brier_difference_vs_climatology"],
                    }
                    for g in groups
                }
                loss_stats = {"log_loss_difference": pj._ratio(1, 0)}
                paired_loss = pj._bootstrap(
                    declaration,
                    {g: log_loss_vectors(p, ref_p, outcomes, set(members), floor) for g, members in groups.items()},
                    loss_stats, n, seed=pj._seed(seed, "log_loss", name, h),
                )
                log_loss.setdefault(name, {})[str(h)] = {g: paired_loss[g]["log_loss_difference"] for g in groups}

    post_mortem = json.loads(EPISODES.read_text(encoding="utf-8"))["episodes"]
    index = {day.isoformat(): i for i, day in enumerate(common)}
    episodes = []
    for episode in post_mortem:
        i = index.get(episode["start"])
        if i is None or not onset[i]:
            raise SystemExit(f"episode {episode['start']} is not an onset of the judge's grid")
        episodes.append(
            {
                "start": episode["start"],
                "regime": episode["regime"],
                "day_type": episode["day_type"],
                "missed_by_all_five": bool(episode.get("missed_by_all")),
                **{name: bool(caught_by[name][i]) for name in everyone},
            }
        )
    document = {
        "declaration": declared,
        "rule": args.rule,
        "onsets": int(sum(onset)),
        "onsets_in_cell": onsets_in,
        "caught_at_some_lead": caught_count,
        "recall_at_some_lead": recall,
        "flags": flags,
        "brier": brier,
        "log_loss": log_loss,
        "calibration": calibration,
        "episodes": episodes,
    }
    args.output.write_text(json.dumps(document, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    text = markdown(document, parents)
    if args.markdown:
        args.markdown.write_text(text + "\n", encoding="utf-8")
    print(text)
    return 0


def markdown(document: dict, parents) -> str:
    out = []
    names = lambda p: [p] + [f"{p}{v}" for v in VARIANTS]
    out.append("Table 1. +5 bp onsets flagged at some lead 1 to 5, by cell: parent and each variant.\n")
    for p in parents:
        group = names(p)
        out.append(f"\n{p}\n")
        out.append("| cell | onsets | " + " | ".join(n[len(p):] or "parent" for n in group) + " |")
        out.append("|---|---|" + "---|" * len(group))
        for cell, n_onsets in document["onsets_in_cell"].items():
            out.append(f"| {cell} | {n_onsets} | " + " | ".join(f"{document['caught_at_some_lead'][n][cell]}" for n in group) + " |")
    out.append("\nTable 2. Recall difference against the parent, by cell (90% interval).\n")
    for p in parents:
        group = names(p)[1:]
        out.append(f"\n{p}\n")
        out.append("| cell | " + " | ".join(n[len(p):] for n in group) + " |")
        out.append("|---|" + "---|" * len(group))
        for cell in document["onsets_in_cell"]:
            out.append(f"| {cell} | " + " | ".join(_interval(document["recall_at_some_lead"][n][cell]["recall_difference"]) for n in group) + " |")
    out.append("\nTable 3. Flags at +5 bp, by horizon: all days / risk dates / other days (flags, of which false alarms); onsets flagged; false alarms per onset on all days.\n")
    out.append("| model | " + " | ".join(f"h = {h}" for h in (1, 2, 3, 4, 5)) + " |")
    out.append("|---|" + "---|" * 5)
    for p in parents:
        for name in names(p):
            cells = []
            for h in ("1", "2", "3", "4", "5"):
                c = document["flags"][name][h]
                a, r, o = c["all_days"], c["risk_dates"], c["other_days"]
                cells.append(
                    f"{a['flags']}({a['false_alarms']}) / {r['flags']}({r['false_alarms']}) / {o['flags']}({o['false_alarms']}); "
                    f"{a['onsets_flagged']}/{c['onsets']}; {_f(a['false_alarms_per_onset'], 2)}"
                )
            out.append(f"| {name} | " + " | ".join(cells) + " |")
    for h in ("1", "5"):
        out.append(f"\nTable 4 (h = {h}). Brier score and log loss the parent loses to the variant (positive favours the variant), +5 bp, 90% interval.\n")
        out.append("| model | cell | days | Brier vs parent | log loss vs parent | Brier vs climatology | Brier vs persistence-logistic |")
        out.append("|---|---|---|---|---|---|---|")
        for p in parents:
            for name in names(p)[1:]:
                for cell, c in document["brier"][name][h].items():
                    out.append(
                        f"| {name} | {cell} | {int(c['days'])} | {_interval(c['vs_parent'])} | {_interval(document['log_loss'][name][h][cell])} | "
                        f"{_interval(c['vs_climatology'])} | {_interval(c['vs_persistence_logistic'])} |"
                    )
    for h in ("1", "2", "3", "4", "5"):
        out.append(f"\nTable 5 (h = {h}). Mean predicted against realised pressure rate (+5 bp) by regime, year and day type; the realised-minus-predicted gap with its 90% interval.\n")
        out.append("| model | cell | days | mean predicted | realised | realised minus predicted |")
        out.append("|---|---|---|---|---|---|")
        for p in parents:
            for name in names(p):
                for cell, c in document["calibration"][name][h].items():
                    if cell.startswith("day type"):
                        continue
                    out.append(
                        f"| {name} | {cell} | {int(c['days'])} | {_f(c['mean_predicted'], 4)} | {_f(c['realised_frequency'], 4)} | {_interval(c['realised_minus_predicted'])} |"
                    )
    every = [x for p in parents for x in names(p)]
    out.append("\nTable 6. The 26 episodes of the post-mortem (#474): who warns at some lead 1 to 5 (all-five misses marked).\n")
    out.append("| start | type | regime | missed by all five | " + " | ".join(every) + " |")
    out.append("|---|---|---|---|" + "---|" * len(every))
    for e in document["episodes"]:
        out.append(
            f"| {e['start']} | {e['day_type']} | {e['regime']} | {'yes' if e['missed_by_all_five'] else 'no'} | "
            + " | ".join("yes" if e[n] else "no" for n in every) + " |"
        )
    return "\n".join(out)


# -- readings (a), (b), (e) of docs/pivot/judge-readings-result.md ----------------------------------------------


def readings_command(args) -> int:
    from repo_model import pressure_judge as pj

    jr = _load("judge_readings")
    pj_script = _load("pressure_judge")
    declared = rds.committed_declaration(DECLARATION)
    base = pj.load_declaration()
    pj_script.require_committed_declaration(pj.DEFAULT_DECLARATION)
    pj_script.require_committed_file(pj.DEFAULT_WEIGHTED_MISS)
    parents = list(declared["parents"])
    names = []
    for p in parents:
        names += [p] + [f"{p}{v}" for v in VARIANTS]
    names += [base.climatology, base.persistence]
    rows = load_daily_panel(args.panel)
    audit_panel(rows)
    splits = load_split_declaration(rds.SPLITS)
    forecasts = [f for f in _load_forecasts(pj, panel_sha256(args.panel), args.inputs) if f.name in names]
    unique = {}
    for f in forecasts:
        unique.setdefault((f.name, f.horizon), f)
    forecasts = list(unique.values())
    missing = [(n, h) for n in names for h in base.horizons if (n, h) not in unique]
    if missing:
        raise SystemExit(f"no forecast for {missing[:3]}")
    states = {h: pj_script._scarcity_states(h, base.last_day) for h in base.horizons}
    calendar = [row.date for row in rows]
    place = {day: k for k, day in enumerate(calendar)}
    result: Dict[str, object] = {"readings": {}}
    for rule in jr.RULES:
        declaration = replace(base, weighted_miss=pj.load_weighted_miss(applied=(rule == "weighted")))
        chosen = pj.choose_cutoffs(declaration, _grids(pj, declaration, rows, splits, states, forecasts), forecasts, calendar)
        grids = _grids(pj, declaration, rows, splits, states, chosen)
        by_name: Dict[str, dict] = defaultdict(dict)
        for f in chosen:
            by_name[f.name][f.horizon] = f
        result["readings"][rule] = {}
        for name in names:
            series = jr.RowSeries(declaration, grids, by_name, name, place, pj.false_alarm_weights)
            result["readings"][rule][name] = jr.readings_for(declaration, series, limited_weighted=(rule == "weighted"))
    result["provenance"] = {"panel_sha256": panel_sha256(args.panel)}
    args.output.write_text(json.dumps(result, indent=1, sort_keys=True, default=str) + "\n", encoding="utf-8")
    if args.markdown:
        args.markdown.write_text(readings_markdown(result, names, jr), encoding="utf-8")
    print(json.dumps({"output": str(args.output)}))
    return 0


def readings_markdown(result: dict, names, jr) -> str:
    lines = ["# Tier 1 of the hurdle variants under readings (a), (b) and (e) (#539)", ""]
    titles = {"unweighted": "Flat rule", "weighted": "Weighted rule"}
    for rule, rows in result["readings"].items():
        lines += [f"## {titles[rule]}", ""]
        for title, pick in (
            ("(a) as declared", lambda r: r["a"]),
            ("(b2) warnings and false alarms pooled across horizons", lambda r: r["b2"]),
            ("(e) outside 2018-19", lambda r: r["e"]["outside_2018_19"]),
            ("(e) in 2018-19", lambda r: r["e"]["in_2018_19"]),
        ):
            lines += [f"### {title}", "", jr.HEAD]
            lines += [jr._row(n, pick(rows[n])) for n in names]
            lines.append("")
        lines += [
            "### (b1) one horizon alone: onsets warned / false alarms per onset at each horizon",
            "", "| row | h = 1 | h = 2 | h = 3 | h = 4 | h = 5 | passes at some horizon |", "|---|---|---|---|---|---|---|",
        ]
        for n in names:
            b = rows[n]["b1_best"]
            cells = [
                f"{c['onsets_flagged']:g} / {jr._f(c['false_alarms_per_onset_limited'])}" if "onsets_flagged" in c else "–"
                for c in (rows[n]["b1"][str(h)] for h in (1, 2, 3, 4, 5))
            ]
            lines.append(f"| {n} | " + " | ".join(cells) + f" | {jr._v(b['passes'])}" + (f" (h = {b['horizon']})" if b["passes"] else "") + " |")
        lines.append("")
    return "\n".join(lines) + "\n"


def summary_command(args) -> int:
    """The judge's tier 1 row at +5 bp for every parent and variant, under each rule."""

    declared = rds.committed_declaration(DECLARATION)
    judged = {rule: json.loads(Path(path).read_text())["candidates"] for rule, path in (("flat", args.flat), ("weighted", args.weighted))}
    lines = [
        "| model | onsets flagged, flat / weighted rule | recall, flat [90%] | recall, weighted [90%] | worst false alarms per onset, flat | worst weighted false alarms per onset, weighted rule | tiers 1 / 3 / 5, flat | tiers 1 / 3 / 5, weighted | passes the full rule, flat / weighted |",
        "|---|---|---|---|---|---|---|---|---|",
    ]
    yes = lambda x: "yes" if x else "no"
    for parent in declared["parents"]:
        for name in [parent] + [f"{parent}{v}" for v in VARIANTS]:
            cells = {}
            for rule, candidates in judged.items():
                entry = candidates[name]
                tier = entry["tiers"]["onset_warning"]["lead_at_least_1"]
                verdict = entry["verdict"]
                cells[rule] = {
                    "flagged": tier["onsets_flagged"],
                    "onsets": tier["onsets"],
                    "recall": tier["recall"],
                    "flat": tier["worst_false_alarms_per_onset"],
                    "weighted": tier.get("worst_weighted_false_alarms_per_onset"),
                    "tiers": " / ".join(yes(verdict[k]) for k in ("tier_1_onset_warning", "tier_3_no_crying_wolf", "tier_5_week_ahead")),
                    "passes": verdict["passes"],
                }
            f, w = cells["flat"], cells["weighted"]
            ci = lambda c: f"{c['recall']['mean']:.3f} [{c['recall']['interval']['lower']:.3f}, {c['recall']['interval']['upper']:.3f}]"
            lines.append(
                f"| {name} | {f['flagged']:g}/{f['onsets']} / {w['flagged']:g}/{w['onsets']} | {ci(f)} | {ci(w)} | {f['flat']:.2f} | "
                f"{w['weighted']:.2f} | {f['tiers']} | {w['tiers']} | {yes(f['passes'])} / {yes(w['passes'])} |"
            )
    text = "\n".join(lines) + "\n"
    args.output.write_text(text, encoding="utf-8")
    print(text)
    return 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("declare", help="write the declaration and the judge's candidate files").set_defaults(handler=declare_command)
    run = commands.add_parser("run")
    run.add_argument("--panel", type=Path, required=True)
    run.add_argument("--published", type=Path, required=True)
    run.add_argument("--horizon", type=int, required=True)
    run.add_argument("--candidate", help="one parent")
    run.add_argument("--output", type=Path, required=True)
    run.set_defaults(handler=run_command)
    for name, handler in (("compare", compare_command), ("readings", readings_command)):
        sub = commands.add_parser(name)
        if name == "compare":
            sub.add_argument(
                "--rule", choices=("unweighted", "weighted"), default="unweighted",
                help="the miss rule that chooses the cut-offs, as the judge's --rule does",
            )
        sub.add_argument("--panel", type=Path, required=True)
        sub.add_argument("--output", type=Path, required=True)
        sub.add_argument("--markdown", type=Path)
        sub.add_argument("inputs", nargs="+", type=Path)
        sub.set_defaults(handler=handler)
    summary = commands.add_parser("summary", help="the judge's tier 1 row for every row, under both rules")
    summary.add_argument("--flat", type=Path, required=True, help="the judge's report under --rule unweighted")
    summary.add_argument("--weighted", type=Path, required=True, help="the judge's report under --rule weighted")
    summary.add_argument("--output", type=Path, required=True)
    summary.set_defaults(handler=summary_command)
    args = parser.parse_args(argv)
    return args.handler(args)


if __name__ == "__main__":
    raise SystemExit(main())
