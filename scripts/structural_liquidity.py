"""The structural liquidity model (#542, track S of #374): forecasts for the judge, and its scoring.

A scratch measurement, not a record: it writes JSON and Markdown to the paths it is given and nothing into
`docs/runs/`. The form, the inputs, the constants and what is reported are in `metadata/structural_liquidity.json`,
and the candidates in `metadata/pressure_judge/candidates/`; this script refuses to read either unless it is
committed and unchanged. Every input beyond the published panel is off in every published declaration and switched
on for these runs only. No rule, threshold, onset definition or availability time changes, and no day after
2025-12-31 is read (`docs/decisions/lockbox.md`).

    PYTHONPATH=src python3 scripts/pressure_v1_1.py panel --output AUG.csv
    PYTHONPATH=src python3 scripts/measurement_fields.py panel --panel AUG.csv --output AUG2.csv
    PYTHONPATH=src python3 scripts/net_settlement.py panel --panel AUG2.csv --output AUG3.csv
    PYTHONPATH=src python3 scripts/projected_reserves.py panel --panel AUG3.csv --output AUG4.csv
    PYTHONPATH=src python3 scripts/pressure_judge.py forecasts --panel PUBLISHED.csv --horizon H --published --output OUT/bench_hH.json
    PYTHONPATH=src python3 scripts/risk_date_severity.py run --panel AUG2.csv --published PUBLISHED.csv --horizon H --output OUT/risk_hH.json
    PYTHONPATH=src python3 scripts/pressure_track_q.py forecasts --panel PUBLISHED.csv --horizon H --output OUT/q_hH.json --distribution OUT/qdist_hH.json
    PYTHONPATH=src python3 scripts/structural_liquidity.py run --panel AUG4.csv --published PUBLISHED.csv \\
        --risk OUT/risk_hH.json --horizon H --output OUT/sl_hH.json
    PYTHONPATH=src python3 scripts/structural_liquidity.py score --panel PUBLISHED.csv --bench 'OUT/bench_h{h}.json' \\
        --risk 'OUT/risk_h{h}.json' --ngboost 'OUT/q_h{h}.json' --row 'OUT/sl_h{h}.json' --output OUT/sl.json --markdown OUT/sl.md

`run` scores the model walk-forward at +5 and +10 bp on the shared fold grid (minimum history 61, refit every 21
scored days, scored days through 2025-12-31), and writes the judge's `forecasts` shape with two rows:
`structural_liquidity`, and with `--risk` the combined row `risk_gbm+structural`, the risk-date passer's forecast
on every day it is nonzero and the model's probability on every day the passer leaves at 0. It also writes each
refit's fitted coefficients.

`score` is the judge as declared under the weighted rule in force (tiers 1 to 5), the readings of
`docs/pivot/judge-readings-result.md`, onset recall by calendar year, the fitted coefficients by refit with their
signs, and each row paired against `risk_gbm`, `ngboost_laplace`, calendar climatology and the persistence-logistic.
It reuses the helpers of `scripts/ngboost_laplace_check.py` (#533).
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from collections import defaultdict
from dataclasses import replace
from datetime import date, time
from pathlib import Path
from typing import Dict, List

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))

from repo_model import measurement_fields, pressure_judge as pj, structural_liquidity as sl  # noqa: E402
from repo_model.baseline import panel_sha256, rolling_exceedance_backtest  # noqa: E402
from repo_model.data import audit_panel, load_daily_panel  # noqa: E402
from repo_model.evaluation_splits import load_split_declaration  # noqa: E402
from repo_model.lockbox import require_unlocked  # noqa: E402

DECLARATION = sl.DEFAULT_DECLARATION
SPLITS = REPO / "metadata" / "evaluation_splits.json"


def _script(name: str):
    spec = importlib.util.spec_from_file_location(f"{name}_script", REPO / "scripts" / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


# -- run ----------------------------------------------------------------------


def combine(parent: Dict[str, Dict[str, float]], structural: Dict[str, Dict[str, float]]) -> Dict[str, Dict[str, float]]:
    """The parent's probability on every day it is nonzero, the structural model's where the parent is 0."""

    out: Dict[str, Dict[str, float]] = {}
    for tau, column in structural.items():
        if set(parent[tau]) != set(column):
            raise SystemExit(f"the parent and the structural model were not scored on the same days at {tau} bp")
        out[tau] = {day: (parent[tau][day] if parent[tau][day] > 0.0 else p) for day, p in column.items()}
    return out


def run_command(args) -> int:
    jr = _script("judge_readings")
    pr_script = _script("projected_reserves")  # the one-day-ahead announced net settlement is its column (#568)
    declared = jr.committed_declaration(DECLARATION)
    judge_script = _script("pressure_judge")
    judge_commit = judge_script.require_committed_declaration(pj.DEFAULT_DECLARATION)
    h = args.horizon
    scoring = declared["scoring"]
    if h not in scoring["horizons"]:
        raise SystemExit(f"horizon {h} is not declared")
    last = date.fromisoformat(scoring["last_day"])
    require_unlocked([last], where="structural_liquidity")
    rows = load_daily_panel(args.panel)
    audit_panel(rows)
    splits = load_split_declaration(SPLITS)
    registry = measurement_fields.load_registry()
    features = sl.features_at_horizon(h)
    predictor = sl.structural_exceedance(features, splits, minimum_history=scoring["minimum_history"])
    with pr_script.switched_on():
        report = rolling_exceedance_backtest(
            rows, predictor=predictor, model_name=declared["rows"][0], features=features, registry=registry,
            decision_time=time.fromisoformat(scoring["decision_time"]), taus=tuple(float(t) for t in declared["thresholds_bp"]),
            minimum_history=scoring["minimum_history"], refit_every=scoring["refit_every"], end=last, horizon=h,
        )
    forecast = pj.report_forecast(declared["rows"][0], report)
    column = {
        f"{tau:g}": {day.isoformat(): p for day, p in zip(forecast.dates, values)}
        for tau, values in forecast.probabilities.items()
    }
    forecasts = {declared["rows"][0]: column}
    if args.risk:
        parent = json.loads(Path(args.risk).read_text())["forecasts"]["risk_gbm"]
        forecasts[declared["rows"][1]] = combine(parent, column)
    document = {
        "horizon": h,
        "panel_sha256": panel_sha256(args.published),
        "scratch_panel_sha256": panel_sha256(args.panel),
        "declaration": declared,
        "judge_commit": judge_commit,
        "scored_window": {"first": forecast.dates[0].isoformat(), "last": forecast.dates[-1].isoformat(), "days": len(forecast.dates)},
        "model_settings": {k: v for k, v in report.model_settings.items()},
        "fits": predictor.fits,
        "forecasts": forecasts,
    }
    args.output.write_text(json.dumps(document, indent=1, sort_keys=True, default=str) + "\n", encoding="utf-8")
    print(json.dumps({"horizon": h, "output": str(args.output), **document["scored_window"]}))
    return 0


# -- the fitted coefficients ------------------------------------------------------


def parameters(documents: List[dict], tau: str = "5") -> dict:
    """Per horizon: each coefficient's value at the first, median and last refit, and the share of refits
    at which it has the sign the mechanism says (positive, for every coefficient but the intercept)."""

    names = ["intercept", *sl.COLUMN_NAMES]
    out = {}
    for document in documents:
        refits = [fit[tau]["raw_coefficients"] for fit in document["fits"] if fit.get(tau, {}).get("raw_coefficients")]
        standardized = [fit[tau]["coefficients"] for fit in document["fits"] if fit.get(tau, {}).get("coefficients")]
        cells = {}
        for k, name in enumerate(names):
            values = sorted(r[k] for r in refits)
            cells[name] = {
                "first": refits[0][k], "median": values[len(values) // 2], "last": refits[-1][k],
                "min": values[0], "max": values[-1],
                "positive_share": sum(1 for r in refits if r[k] > 0) / len(refits),
                "standardized_last": standardized[-1][k],
            }
        out[str(document["horizon"])] = {"refits": len(refits), "of": len(document["fits"]), "coefficients": cells}
    return out


def parameters_markdown(table: dict) -> str:
    lines = ["## Fitted coefficients by refit (+5 bp, in the columns' own units)", "",
             "Positive is the sign the mechanism says for every coefficient but the intercept. `standardized` is the last refit's, on standardized columns (comparable across terms).", ""]
    for h, entry in table.items():
        lines += [f"h = {h}: {entry['refits']} refits with both classes of the label, of {entry['of']}.", "",
                  "| coefficient | first refit | median | last refit | min | max | refits positive | standardized (last) |",
                  "|---|---|---|---|---|---|---|---|"]
        for name, c in entry["coefficients"].items():
            lines.append(
                f"| {name} | {c['first']:.4g} | {c['median']:.4g} | {c['last']:.4g} | {c['min']:.4g} | {c['max']:.4g} "
                f"| {c['positive_share']:.0%} | {c['standardized_last']:.3f} |"
            )
        lines.append("")
    return "\n".join(lines)


# -- score ------------------------------------------------------------------------


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
    forecasts, panels, fit_documents = [], {}, []
    for h in horizons:
        for label, template in (("bench", args.bench), ("risk", args.risk), ("ngboost", args.ngboost), ("row", args.row)):
            doc = jr._load(template, h)
            if doc["panel_sha256"] != digest and label in ("bench", "row"):
                raise SystemExit(f"{template.format(h=h)} was scored on another panel")
            panels[f"{label}_h{h}"] = doc["panel_sha256"]
            if label == "row":
                fit_documents.append(doc)
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
    result = {
        **shared,
        "rows": per_row,
        "parameters": parameters(fit_documents),
        "parameters_at_10bp": parameters(fit_documents, "10"),
        "declaration": {"path": "metadata/structural_liquidity.json", "judge_commit": judge_commit},
        "provenance": {"panel_sha256": digest, "forecast_panels": panels},
    }
    args.output.write_text(json.dumps(result, indent=1, sort_keys=True, default=str) + "\n", encoding="utf-8")
    if args.markdown:
        args.markdown.write_text(markdown(result, document, ngc), encoding="utf-8")
    print(json.dumps({"output": str(args.output)}))
    return 0


def markdown(result: dict, document: dict, ngc) -> str:
    shared = {k: result[k] for k in ("readings", "training_checks", "judge", "judge_tables")}
    out = ["# The structural liquidity model (#542)", ""]
    for index, row_name in enumerate(document["rows"]):
        view = {**shared, **result["rows"][row_name]}
        shown = {**document, "row": row_name, "risk_date_passers": document["risk_date_passers"] + ["ngboost_laplace"]}
        text = ngc.markdown(view, shown).replace("# The ngboost_laplace check (#533)", f"# {row_name}")
        if index:
            # the judge's tables and tier 1 readings are shared: print them once
            text = text.split("## Onsets warned by calendar year", 1)
            text = "# " + row_name + "\n\n## Onsets warned by calendar year" + text[1]
        out.append(text)
    out.append(parameters_markdown(result["parameters"]))
    return "\n".join(out)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    commands = parser.add_subparsers(dest="command", required=True)
    run = commands.add_parser("run")
    run.add_argument("--panel", type=Path, required=True)
    run.add_argument("--published", type=Path, required=True)
    run.add_argument("--risk", type=Path)
    run.add_argument("--horizon", type=int, required=True)
    run.add_argument("--output", type=Path, required=True)
    run.set_defaults(run=run_command)
    score = commands.add_parser("score")
    score.add_argument("--panel", type=Path, required=True)
    for flag in ("bench", "risk", "ngboost", "row"):
        score.add_argument(f"--{flag}", required=True)
    score.add_argument("--output", type=Path, required=True)
    score.add_argument("--markdown", type=Path)
    score.set_defaults(run=score_command)
    args = parser.parse_args(argv)
    return args.run(args)


if __name__ == "__main__":
    raise SystemExit(main())
