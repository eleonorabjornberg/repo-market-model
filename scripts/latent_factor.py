"""Score the latent funding-stress factor model under the pressure-day judge (#543, a model variant of #374).

A scratch measurement, not a record: it writes JSON, Markdown and an SVG to the paths it is given and nothing into
`docs/runs/`. The series, the model, the mapping, the settings and what is reported are in `metadata/latent_factor.json`,
which this script refuses to read unless it is committed and unchanged, as the judge's declaration is. Every input beyond
the published panel is off in every published declaration and switched on for these runs only. Scored days are
2018-06-29 to 2025-12-31; no day of the 2026 tiers is read (`docs/decisions/lockbox.md`).

    PYTHONPATH=src python3 scripts/pressure_v1_1.py panel --output AUG.csv
    PYTHONPATH=src python3 scripts/measurement_fields.py panel --panel AUG.csv --output AUG2.csv
    PYTHONPATH=src python3 scripts/pressure_judge.py forecasts --panel PUBLISHED.csv --horizon H --output OUT/bench_hH.json
    PYTHONPATH=src python3 scripts/risk_date_severity.py run --panel AUG2.csv --published PUBLISHED.csv --horizon H --output OUT/risk_hH.json
    PYTHONPATH=src python3 scripts/pressure_track_q.py forecasts --panel PUBLISHED.csv --horizon H --output OUT/q_hH.json --distribution OUT/qdist_hH.json
    PYTHONPATH=src python3 scripts/latent_factor.py run --panel AUG2.csv --published PUBLISHED.csv --horizon H \\
        --risk OUT/risk_hH.json --output OUT/lf_hH.json
    PYTHONPATH=src python3 scripts/pressure_judge.py judge --panel PUBLISHED.csv --rule weighted --output OUT/judge_weighted.json \\
        --markdown OUT/judge_weighted.md OUT/bench_h?.json OUT/risk_h?.json OUT/q_h?.json OUT/lf_h?.json
    PYTHONPATH=src python3 scripts/latent_factor.py compare --panel PUBLISHED.csv --bench 'OUT/bench_h{h}.json' \\
        --risk 'OUT/risk_h{h}.json' --reference 'OUT/q_h{h}.json' --rows 'OUT/lf_h{h}.json' --output OUT/compare.json --markdown OUT/compare.md
    PYTHONPATH=src python3 scripts/latent_factor.py factor --compare-input 'OUT/lf_h{h}.json' --panel PUBLISHED.csv \\
        --output OUT/factor.json --markdown OUT/factor.md --svg OUT/factor.svg

`run` fits the three variants (`ml.latent_factor_exceedance`), walk-forward at +5 and +10 bp on the shared fold grid, and
puts each under the risk-date passer `risk_gbm` as its every-day component (the rule of #506: the passer's forecast on a
risk date, the model's on any other day). `compare` reads the judge's own cut-offs and reports, for each row, the judge's
tiers, tier 1 under readings (a) to (e) of `docs/pivot/judge-readings-result.md`, onsets warned by calendar year, the
degenerate refits, Brier score and log loss, and the paired comparison with `risk_gbm`, `ngboost_laplace`, calendar
climatology and the persistence-logistic. `factor` reports the loadings and persistence by refit and plots the filtered
factor against the onsets.
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
from typing import Dict, List, Mapping, Optional, Sequence, Set

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))

from repo_model import measurement_fields, ml, risk_dates  # noqa: E402
from repo_model import pressure_judge as pj  # noqa: E402
from repo_model.baseline import panel_sha256, rolling_exceedance_backtest  # noqa: E402
from repo_model.data import audit_panel, load_daily_panel  # noqa: E402
from repo_model.evaluation_splits import load_split_declaration  # noqa: E402
from repo_model.lockbox import require_unlocked  # noqa: E402

DECLARATION = REPO / "metadata" / "latent_factor.json"
SPLITS = REPO / "metadata" / "evaluation_splits.json"
#: variant -> (link, residual)
VARIANTS = {"latent_factor": ("gaussian", False), "latent_factor_resid": ("gaussian", True), "latent_factor_logit": ("logit", False)}
PASSER = "risk_gbm"
#: combined row -> the variant that serves the days that are not risk dates
COMBINED = {f"{PASSER}+{name}": name for name in VARIANTS}
COUPONS = "treasury_settlement_coupons"
RULES = ("unweighted", "weighted", "weighted/before_only")
LOG_LOSS_FLOOR = 1e-6


def _script(name: str):
    spec = importlib.util.spec_from_file_location(f"{name}_script", REPO / "scripts" / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


# -- helpers ------------------------------------------------------------------


def is_risk_date(day_type: str, coupons: Optional[float], horizon: int) -> bool:
    """A risk date as `ml._RiskDateDesign.member` reads it: a day type other than ordinary, or, at h = 1, a coupon settlement."""

    return risk_dates.non_ordinary_day(day_type, coupons, coupon_clause=horizon == 1)


def combine(parent: Mapping[str, Mapping[str, float]], own: Mapping[str, Mapping[str, float]], risk_dates: Set[date]):
    """The passer's forecast on a risk date, the model's on any other day, for each threshold and day.

    Raises:
        ValueError: if the two cover different thresholds or days, or the passer forecasts a day that is not a risk date
            (the rule assumes it is exactly 0 there, as the passer of #428 is).
    """

    if set(parent) != set(own):
        raise ValueError("the passer and the model must cover the same thresholds")
    out: Dict[str, Dict[str, float]] = {}
    for tau in parent:
        if set(parent[tau]) != set(own[tau]):
            raise ValueError("the passer and the model must cover the same days")
        column = {}
        for when, value in parent[tau].items():
            member = date.fromisoformat(when) in risk_dates
            if not member and value != 0.0:
                raise ValueError(f"the passer forecasts {when}, which is not a risk date, at {value}")
            column[when] = value if member else own[tau][when]
        out[tau] = column
    return out


def sign_changes(loadings_by_refit: Sequence[Sequence[float]]) -> List[int]:
    """Per series, the number of times its loading changes sign from one refit to the next (a zero has no sign)."""

    if not loadings_by_refit:
        return []
    width = len(loadings_by_refit[0])
    if any(len(row) != width for row in loadings_by_refit):
        raise ValueError("every refit must carry one loading per series")
    out = [0] * width
    last: List[Optional[int]] = [None] * width
    for row in loadings_by_refit:
        for i, value in enumerate(row):
            sign = (value > 0) - (value < 0)
            if sign == 0:
                continue
            if last[i] is not None and sign != last[i]:
                out[i] += 1
            last[i] = sign
    return out


def log_loss(probabilities: Sequence[float], outcomes: Sequence[float]) -> float:
    """Mean negative log likelihood, the probability clipped to [1e-6, 1 - 1e-6]."""

    if len(probabilities) != len(outcomes):
        raise ValueError("one probability per outcome")
    total = 0.0
    for p, y in zip(probabilities, outcomes):
        p = min(1.0 - LOG_LOSS_FLOOR, max(LOG_LOSS_FLOOR, p))
        total -= math.log(p) if y else math.log(1.0 - p)
    return total / len(outcomes)


def brier(probabilities: Sequence[float], outcomes: Sequence[float]) -> float:
    if len(probabilities) != len(outcomes):
        raise ValueError("one probability per outcome")
    return sum((p - y) ** 2 for p, y in zip(probabilities, outcomes)) / len(outcomes)


# -- run ----------------------------------------------------------------------


def _recording(predictor, log: list):
    """The predictor, unchanged, with each call's fit recorded: the first anchor of the block and the fit's settings."""

    def fit_predict(train_rows, feature_rows, taus, information=None, histories=None):
        result = predictor(train_rows, feature_rows, taus, information=information, histories=histories)
        settings = dict(result.model_settings)
        factor = settings.pop("filtered_factor")
        log.append(
            {
                "first_anchor": feature_rows[0].date.isoformat(),
                "training_rows": len(train_rows),
                "anchors": [row.date.isoformat() for row in feature_rows],
                "filtered_factor": factor,
                "settings": settings,
            }
        )
        return result

    return fit_predict


def run_command(args) -> int:
    rds = _script("risk_date_severity")
    declared = rds.committed_declaration(DECLARATION)
    h = args.horizon
    if h not in declared["horizons"]:
        raise SystemExit(f"horizon {h} is not declared")
    last = date.fromisoformat(declared["scoring"]["last_day"])
    require_unlocked([last], where="latent_factor")
    rows = load_daily_panel(args.panel)
    audit_panel(rows)
    splits = load_split_declaration(SPLITS)
    registry = measurement_fields.load_registry()
    taus = tuple(float(t) for t in declared["thresholds_bp"])
    minimum = declared["scoring"]["minimum_history"]
    features = ("spread_bps",) + tuple(declared["columns"])
    forecasts, settings, refits = {}, {}, {}
    for name, (link, residual) in VARIANTS.items():
        log: list = []
        predictor = _recording(ml.latent_factor_exceedance(minimum_history=minimum, residual=residual, link=link), log)
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
        settings[name] = {
            "features": list(report.features),
            "ml_libraries": None if report.ml_libraries is None else dict(report.ml_libraries),
        }
        refits[name] = log
        print(json.dumps({"horizon": h, "candidate": name, "refits": len(log), "done": True}), flush=True)
    check = {}
    if args.risk:
        parent = json.loads(Path(args.risk).read_text())
        if parent["panel_sha256"] != panel_sha256(args.published):
            raise SystemExit(f"{args.risk} was scored on another panel")
        passer = parent["forecasts"][PASSER]
        by_day = {row.date: row for row in rows}
        days = sorted({date.fromisoformat(d) for column in passer.values() for d in column})
        members = {
            day for day in days
            if is_risk_date(splits.day_type(by_day[day].values), by_day[day].values.get(COUPONS), h)
        }
        check = {"risk_dates": len(members), "scored_days": len(days)}
        for combined, variant in COMBINED.items():
            forecasts[combined] = combine(passer, forecasts[variant], members)
    document = {
        "horizon": h,
        "panel_sha256": panel_sha256(args.published),
        "scratch_panel_sha256": panel_sha256(args.panel),
        "declaration": declared,
        "declarations": settings,
        "risk_date_check": check,
        "refits": refits,
        "forecasts": forecasts,
    }
    args.output.write_text(json.dumps(document, indent=1, sort_keys=True, default=str) + "\n", encoding="utf-8")
    print(json.dumps({"horizon": h, "output": str(args.output)}))
    return 0


# -- compare ------------------------------------------------------------------


def _any_of(series: Sequence[Sequence[float]]) -> List[float]:
    return [max(values) for values in zip(*series)]


def compare_command(args) -> int:
    ngb = _script("ngboost_laplace_check")
    jr = _script("judge_readings")
    judge_script = _script("pressure_judge")
    rds = _script("risk_date_severity")
    document = rds.committed_declaration(DECLARATION)
    judge_commit = judge_script.require_committed_declaration(pj.DEFAULT_DECLARATION)
    judge_script.require_committed_file(pj.DEFAULT_WEIGHTED_MISS)
    base = pj.load_declaration()
    if not pj.load_weighted_miss().in_force:
        raise SystemExit("the weighted miss rule is not in force; this comparison reads the rule in force")
    rows_names = list(VARIANTS) + list(COMBINED)
    passers = document["references"]["risk_date_passers"]
    extra = [n for n in document["references"]["pair_against"] if n not in (base.climatology, base.persistence, PASSER)]
    benchmarks = [base.climatology, base.persistence]
    names = rows_names + passers + extra + benchmarks
    rows = load_daily_panel(args.panel)
    audit_panel(rows)
    splits = load_split_declaration(SPLITS)
    digest = panel_sha256(args.panel)
    horizons = base.horizons
    if list(horizons) != document["horizons"] or base.last_day != date.fromisoformat(document["scoring"]["last_day"]):
        raise SystemExit("the judge's horizons or last day are not the declared ones")
    forecasts, panels = [], {}
    for h in horizons:
        for label, template in (("bench", args.bench), ("risk", args.risk), ("reference", args.reference), ("rows", args.rows)):
            doc = jr._load(template, h)
            if label == "bench" and doc["panel_sha256"] != digest:
                raise SystemExit(f"{template.format(h=h)} was scored on another panel")
            panels[f"{label}_h{h}"] = doc["panel_sha256"]
            forecasts.extend(f for f in pj.forecasts_from_horizon_document(doc) if f.name in names)
    unique: Dict[tuple, "pj.Forecast"] = {}
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
    result: Dict[str, object] = {
        "readings": {}, "training_checks": {}, "judge": {}, "judge_tables": {}, "by_year": {}, "blocks": {}, "paired": {},
        "cross_check": {}, "scores": {}, "only_row": {},
    }
    original = pj.false_alarm_weights
    runs = [
        ("unweighted", replace(base, weighted_miss=pj.load_weighted_miss(applied=False)), original),
        ("weighted", replace(base, weighted_miss=pj.load_weighted_miss(applied=True)), original),
        ("weighted/before_only", replace(base, weighted_miss=pj.load_weighted_miss(applied=True)), jr.before_only_weights),
    ]
    for key, declaration, weight_fn in runs:
        pj.false_alarm_weights = weight_fn
        try:
            chosen = pj.choose_cutoffs(declaration, grids, forecasts, calendar)
            by_name: Dict[str, Dict[int, "pj.Forecast"]] = defaultdict(dict)
            for f in chosen:
                by_name[f.name][f.horizon] = f
            series = {n: jr.RowSeries(declaration, grids, by_name, n, place, weight_fn) for n in names}
            result["readings"][key] = {
                n: jr.readings_for(declaration, series[n], limited_weighted=key.startswith("weighted")) for n in names
            }
            result["training_checks"][key] = {
                n: jr.training_checks(declaration, grids, chosen, calendar, n) for n in (rows_names[0], passers[0])
            }
            if key == "weighted/before_only":
                continue
            judged = pj.judge(declaration, grids_of(chosen), chosen, calendar=calendar, holdouts=judge_script._holdouts())
            result["judge"][key] = {
                n: {
                    "verdict": c["verdict"],
                    "onset_warning": c["tiers"]["onset_warning"],
                    "scarce_regime": c["verdict"].get("scarce_regime"),
                }
                for n, c in judged["candidates"].items() if n in names
            }
            result["judge_tables"][key] = judge_script.summary_tables(
                {**judged, "candidates": {n: c for n, c in judged["candidates"].items() if n in names}}
            )
            for n in names:
                near = judged["candidates"][n]["tiers"]["onset_warning"]["lead_at_least_1"]
                mine = result["readings"][key][n]["a"]
                theirs = near["worst_weighted_false_alarms_per_onset" if key == "weighted" else "worst_false_alarms_per_onset"]
                agree = (
                    abs(near["onsets_flagged"] - mine["onsets_flagged"]) < 1e-9
                    and abs(theirs - mine["false_alarms_per_onset_limited"]) < 1e-9
                    and abs(near["recall"]["mean"] - mine["recall"]) < 1e-9
                )
                result["cross_check"].setdefault(key, {})[n] = agree
                if not agree:
                    raise SystemExit(f"reading (a) of {n} under the {key} rule does not match the judge's own row")
            if key != "weighted":
                continue
            first = horizons[0]
            anchor = series[rows_names[0]]
            days = anchor.days
            caught = {n: [max(series[n].flags[h][k] for h in series[n].horizons) for k in range(len(days))] for n in names}
            result["by_year"] = {n: ngb.warned_by_year(days, anchor.onset, caught[n]) for n in names}
            passers_caught = [caught[n] for n in passers]
            for n in rows_names:
                only = ngb.only_this_row_warns(days, anchor.onset, caught[n], passers_caught)
                reverse = ngb.only_this_row_warns(days, anchor.onset, _any_of(passers_caught), [caught[n]])
                result["only_row"][n] = {
                    "row_only": [
                        {"day": d.isoformat(), "horizons": [h for h in series[n].horizons if series[n].flags[h][days.index(d)]]}
                        for d in only
                    ],
                    "passers_only": [d.isoformat() for d in reverse],
                    "onsets": int(sum(anchor.onset)),
                    "row_warns": int(sum(1 for o, c in zip(anchor.onset, caught[n]) if o and c)),
                    "at_least_one_passer_warns": int(sum(1 for o, c in zip(anchor.onset, _any_of(passers_caught)) if o and c)),
                }
            for n in rows_names + passers + extra + benchmarks:
                result["scores"][n] = {}
                for h in horizons:
                    grid = grids[h]
                    p = by_name[n][h].probabilities[tau]
                    y = grid.outcomes[tau]
                    result["scores"][n][str(h)] = {"brier": brier(p, y), "log_loss": log_loss(p, y), "days": len(y)}
            for n in rows_names:
                result["blocks"][n] = {}
                for h in horizons:
                    f = by_name[n][h]
                    blocks = ngb.refit_blocks(f.probabilities[tau], f.cutoffs[tau], f.dates, declaration.cutoff_refit_every)
                    result["blocks"][n][str(h)] = {
                        **ngb.block_summary(blocks),
                        "days_probability_zero": sum(1 for p in f.probabilities[tau] if p == 0.0),
                        "days": len(f.dates),
                        "distinct_probabilities": len(set(f.probabilities[tau])),
                    }
            at_first = {d: k for k, d in enumerate(grids[first].dates)}
            groups = {
                dim: [grids[first].groups[dim][at_first[d]] for d in days]
                for dim in dict.fromkeys(declaration.groupings + ("regime",))
            }
            for n in rows_names:
                result["paired"][n] = {}
                for ref in document["references"]["pair_against"]:
                    result["paired"][n][ref] = {"brier": {}, "recall": {}}
                    for h in horizons:
                        grid = grids[h]
                        row_p, ref_p = (by_name[x][h].probabilities[tau] for x in (n, ref))
                        result["paired"][n][ref]["brier"][str(h)] = ngb.paired_brier(declaration, grid, row_p, ref_p, (n, ref, h))
                    result["paired"][n][ref]["recall"] = ngb.paired_recall(
                        declaration, days, anchor.onset, caught[n], caught[ref], groups, (n, ref)
                    )
        finally:
            pj.false_alarm_weights = original
    result["declaration"] = {"path": "metadata/latent_factor.json", "judge_commit": judge_commit}
    result["provenance"] = {"panel_sha256": digest, "forecast_panels": panels}
    args.output.write_text(json.dumps(result, indent=1, sort_keys=True, default=str) + "\n", encoding="utf-8")
    if args.markdown:
        args.markdown.write_text(markdown(result, document, names, rows_names), encoding="utf-8")
    print(json.dumps({"output": str(args.output)}))
    return 0


# -- the summary --------------------------------------------------------------


def _f(value, places=3):
    return "–" if value is None else f"{value:.{places}f}"


def _iv(cell):
    return f"{_f(cell['mean'])} [{_f(cell['interval'][0])}, {_f(cell['interval'][1])}]" if cell.get("interval") else f"{_f(cell['mean'])} [–]"


def markdown(result: dict, document: dict, names: List[str], rows_names: List[str]) -> str:
    lines = ["# The latent funding-stress factor (#543)", ""]
    for key, rows in result["readings"].items():
        lines += [f"## Tier 1 under {key}", "", "| row | (a) as declared | (b1) best horizon | (b2) pooled | (e) outside 2018-19 |", "|---|---|---|---|---|"]
        for n in names:
            r = rows[n]

            def short(c):
                if "unavailable" in c:
                    return "–"
                return f"{c['onsets_flagged']:g} / {c['false_alarms_per_onset_limited']:.2f} {'pass' if c['passes'] else 'fail'}"

            best = r["b1_best"]
            lines.append(
                f"| {n} | {short(r['a'])} | {'pass (h = ' + str(best['horizon']) + ')' if best['passes'] else 'fail'} "
                f"| {short(r['b2'])} | {short(r['e']['outside_2018_19'])} |"
            )
        lines.append("")
    for key, table in result["judge_tables"].items():
        lines += [f"## The judge's tables under the {key} rule", "", table, ""]
    years = sorted({y for cells in result["by_year"].values() for y in cells}, key=int)
    lines += ["## Onsets warned by calendar year (lead >= 1, any horizon 1 to 5), weighted rule", "",
              "| row | " + " | ".join(("**" + str(y) + "**") if int(y) in (2018, 2020, 2024) else str(y) for y in years) + " |",
              "|---|" + "---|" * len(years)]
    for n, cells in result["by_year"].items():
        lines.append(f"| {n} | " + " | ".join(f"{cells.get(y, [0, 0])[1]} of {cells.get(y, [0, 0])[0]}" for y in years) + " |")
    lines.append("")
    lines += ["## Brier score and log loss at +5 bp, pooled by horizon", "",
              "| row | " + " | ".join(f"h = {h} Brier / log loss" for h in range(1, 6)) + " |", "|---|" + "---|" * 5]
    for n, cells in result["scores"].items():
        lines.append(f"| {n} | " + " | ".join(f"{cells[str(h)]['brier']:.4f} / {cells[str(h)]['log_loss']:.4f}" for h in range(1, 6)) + " |")
    lines.append("")
    for n in rows_names:
        only = result["only_row"][n]
        lines += [
            f"## {n}: onsets only this row warns", "",
            f"{n} warns {only['row_warns']} of {only['onsets']} onsets; at least one of the five passers warns {only['at_least_one_passer_warns']}. "
            f"{len(only['row_only'])} are warned by {n} and by none of the five passers:", "",
        ]
        lines += [f"* {e['day']} (flagged at h = {', '.join(str(h) for h in e['horizons'])})" for e in only["row_only"]]
        lines += ["", f"Warned by a passer and not by {n}: " + (", ".join(only["passers_only"]) or "none"), ""]
        lines += [f"### {n}: constant or degenerate refits", "",
                  "| h | refits | probability constant | all zero | cut-off flags nothing | cut-off flags every day | days at probability 0 | distinct probabilities |",
                  "|---|---|---|---|---|---|---|---|"]
        for h, b in result["blocks"][n].items():
            lines.append(
                f"| {h} | {b['refits']} | {b['constant']} | {b['all_zero']} | {b['never_flag']} | {b['always_flag']} "
                f"| {b['days_probability_zero']} of {b['days']} | {b['distinct_probabilities']} |"
            )
        lines.append("")
    for n in rows_names:
        for ref, doc in result["paired"][n].items():
            lines += [f"## {n} against {ref}", "", "Brier difference, reference minus row (positive: the row is better), 90% interval.", "",
                      "| h | pooled |", "|---|---|"]
            for h, cells in doc["brier"].items():
                lines.append(f"| {h} | {_iv(cells['pooled'])} |")
            lines.append("")
            for dimension in ("regime", "day_type", "scarcity_state"):
                labels = sorted(doc["brier"]["1"].get(dimension, {}))
                if not labels:
                    continue
                lines += [f"By {dimension}, Brier difference at h = 1 / 3 / 5:", "", "| " + dimension + " | days | h = 1 | h = 3 | h = 5 |", "|---|---|---|---|---|"]
                for label in labels:
                    cells = [doc["brier"][h][dimension][label] for h in ("1", "3", "5")]
                    lines.append(f"| {label} | {cells[0]['days']:g} | " + " | ".join(_iv(c) for c in cells) + " |")
                lines.append("")
            rec = doc["recall"]
            lines += [f"Onset recall difference, row minus reference (each at its own cut-offs, any horizon), pooled: {_iv(rec['pooled'])} on {rec['pooled']['onsets']} onsets.", ""]
            for dimension in ("regime", "day_type", "scarcity_state"):
                if dimension not in rec:
                    continue
                lines += [f"| {dimension} | onsets | recall difference [90%] |", "|---|---|---|"]
                lines += [f"| {label} | {c['onsets']} | {_iv(c)} |" for label, c in sorted(rec[dimension].items())]
                lines.append("")
    return "\n".join(lines) + "\n"


# -- the factor ---------------------------------------------------------------


def factor_svg(points: Sequence[tuple], onsets: Sequence[date], title: str) -> str:
    """The filtered factor over time with the onset days marked, as a plain SVG (stdlib only)."""

    if not points:
        raise ValueError("no factor to plot")
    width, height, left, top, bottom = 960, 300, 50, 24, 28
    first, last = points[0][0].toordinal(), points[-1][0].toordinal()
    values = [v for _, v in points]
    low, high = min(values), max(values)
    if high == low:
        high = low + 1.0
    plot_h = height - top - bottom

    def x(d: date) -> float:
        return left + (d.toordinal() - first) / max(last - first, 1) * (width - left - 10)

    def y(v: float) -> float:
        return top + (high - v) / (high - low) * plot_h

    path = " ".join(f"{'M' if k == 0 else 'L'}{x(d):.1f},{y(v):.1f}" for k, (d, v) in enumerate(points))
    marks = "".join(
        f'<line x1="{x(d):.1f}" x2="{x(d):.1f}" y1="{top}" y2="{height - bottom}" stroke="#c0392b" stroke-width="1" opacity="0.55"/>'
        for d in onsets if points[0][0] <= d <= points[-1][0]
    )
    ticks = "".join(
        f'<text x="{x(date(year, 1, 1)):.1f}" y="{height - 8}" font-size="10" text-anchor="middle" fill="#555">{year}</text>'
        for year in range(points[0][0].year + (1 if points[0][0] > date(points[0][0].year, 1, 1) else 0), points[-1][0].year + 1)
    )
    zero = f'<line x1="{left}" x2="{width - 10}" y1="{y(0.0):.1f}" y2="{y(0.0):.1f}" stroke="#999" stroke-dasharray="3,3"/>' if low < 0 < high else ""
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}" role="img" '
        f'aria-label="{title}"><rect width="{width}" height="{height}" fill="white"/>'
        f'<text x="{left}" y="14" font-size="12" fill="#222">{title}</text>{zero}{marks}'
        f'<path d="{path}" fill="none" stroke="#1f4e79" stroke-width="1.2"/>{ticks}'
        f'<text x="6" y="{top + 8}" font-size="10" fill="#555">{high:.1f}</text>'
        f'<text x="6" y="{height - bottom}" font-size="10" fill="#555">{low:.1f}</text></svg>\n'
    )


def factor_command(args) -> int:
    rds = _script("risk_date_severity")
    document = rds.committed_declaration(DECLARATION)
    base = pj.load_declaration()
    rows = load_daily_panel(args.panel)
    audit_panel(rows)
    splits = load_split_declaration(SPLITS)
    out: Dict[str, object] = {"variants": {}}
    series_names = list(ml.LATENT_FACTOR_SERIES)
    lines = ["# The latent factor by refit (#543)", ""]
    horizon1 = None
    for h in base.horizons:
        doc = json.loads(Path(args.compare_input.format(h=h)).read_text())
        for variant in VARIANTS:
            log = doc["refits"][variant]
            loadings = [r["settings"]["loadings"] for r in log]
            persistence = [r["settings"]["persistence"] for r in log]
            fallback = sum(1 for r in log if r["settings"]["fallback"])
            slopes = [r["settings"]["mapping_slope_bp"] for r in log]
            flips = sign_changes(loadings)
            cell = out["variants"].setdefault(variant, {})
            cell[str(h)] = {
                "refits": len(log),
                "fallback_refits": fallback,
                "sign_changes_by_series": dict(zip(series_names, flips)),
                "persistence": {"min": min(persistence), "median": sorted(persistence)[len(persistence) // 2], "max": max(persistence)},
                "loadings": {
                    name: {
                        "min": min(row[i] for row in loadings),
                        "median": sorted(row[i] for row in loadings)[len(loadings) // 2],
                        "max": max(row[i] for row in loadings),
                    }
                    for i, name in enumerate(series_names)
                },
                "mapping_slope_bp": {"min": min(slopes), "max": max(slopes)},
                "em_iterations_max": max(r["settings"]["em_iterations"] for r in log),
            }
            if h == 1 and variant == "latent_factor":
                horizon1 = log
    for variant, cells in out["variants"].items():
        for h, cell in cells.items():
            if h != "1":
                continue
            lines += [f"## {variant}, h = {h}: {cell['refits']} refits, {cell['fallback_refits']} on the training-rate fallback", "",
                      "| series | loading min | median | max | sign changes between refits |", "|---|---|---|---|---|"]
            for name in series_names:
                v = cell["loadings"][name]
                lines.append(f"| {name} | {v['min']:.3f} | {v['median']:.3f} | {v['max']:.3f} | {cell['sign_changes_by_series'][name]} |")
            p = cell["persistence"]
            lines += ["", f"Persistence phi: min {p['min']:.3f}, median {p['median']:.3f}, max {p['max']:.3f}. "
                      f"Mapping slope (bp per factor unit): {cell['mapping_slope_bp']['min']:.3f} to {cell['mapping_slope_bp']['max']:.3f}. "
                      f"Most EM iterations in a refit: {cell['em_iterations_max']}.", ""]
    other = [(h, v, c) for v, cells in out["variants"].items() for h, c in cells.items() if h != "1"]
    lines += ["## Sign changes of any loading between refits, every horizon and variant", "",
              "| variant | h | refits | fallback refits | series with a sign change | phi min–max |", "|---|---|---|---|---|---|"]
    for variant, cells in out["variants"].items():
        for h, c in sorted(cells.items()):
            changed = [n for n, k in c["sign_changes_by_series"].items() if k]
            lines.append(f"| {variant} | {h} | {c['refits']} | {c['fallback_refits']} | {', '.join(changed) or 'none'} | {c['persistence']['min']:.3f}–{c['persistence']['max']:.3f} |")
    lines.append("")
    if horizon1 is not None:
        points = []
        for r in horizon1:
            for anchor, value in zip(r["anchors"], r["filtered_factor"]):
                if value is not None:
                    points.append((date.fromisoformat(anchor), value))
        points.sort()
        # onset days: from the judge's grid at h = 1
        grid_doc = json.loads(Path(args.compare_input.format(h=1)).read_text())
        scored = sorted(date.fromisoformat(d) for d in grid_doc["forecasts"]["latent_factor"]["5"])
        references = [f for f in pj.forecasts_from_horizon_document(grid_doc) if f.name == "latent_factor"]
        reference = references[0]
        grid = pj.build_grid(base, 1, rows, reference.dates, splits, scarcity_state=_script("pressure_judge")._scarcity_states(1, base.last_day))
        onsets = [d for d, o in zip(grid.dates, grid.onset) if o]
        out["onsets"] = [d.isoformat() for d in onsets]
        out["factor_points"] = len(points)
        args.svg.write_text(
            factor_svg(points, onsets, "Filtered latent funding-stress factor at each forecast's anchor (h = 1), onsets marked"),
            encoding="utf-8",
        )
        by_onset = []
        for d in onsets:
            before = [v for day, v in points if day < d][-5:]
            by_onset.append((d, before[-1] if before else None))
        values = [v for _, v in points]
        mean = sum(values) / len(values)
        lines += ["## The filtered factor at the last anchor before each onset (h = 1)", "",
                  f"Mean of the filtered factor over all anchors: {mean:.3f}; standard deviation {math.sqrt(sum((v - mean) ** 2 for v in values) / len(values)):.3f}.", "",
                  "| onset | factor at the last anchor before it |", "|---|---|"]
        lines += [f"| {d} | {'–' if v is None else f'{v:.3f}'} |" for d, v in by_onset]
        lines.append("")
    args.output.write_text(json.dumps(out, indent=1, sort_keys=True, default=str) + "\n", encoding="utf-8")
    if args.markdown:
        args.markdown.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(args.output)}))
    return 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="command", required=True)
    run = sub.add_parser("run", help="fit the two variants at one horizon and put each under the risk-date passer")
    run.add_argument("--panel", type=Path, required=True)
    run.add_argument("--published", type=Path, required=True)
    run.add_argument("--horizon", type=int, required=True)
    run.add_argument("--risk", help="the risk-date severity file of this horizon (for the combined rows)")
    run.add_argument("--output", type=Path, required=True)
    run.set_defaults(func=run_command)
    compare = sub.add_parser("compare", help="the judge's readings, the years, the degenerate refits and the pairing, per row")
    compare.add_argument("--panel", type=Path, required=True)
    compare.add_argument("--bench", required=True)
    compare.add_argument("--risk", required=True)
    compare.add_argument("--reference", required=True)
    compare.add_argument("--rows", required=True)
    compare.add_argument("--output", type=Path, required=True)
    compare.add_argument("--markdown", type=Path)
    compare.set_defaults(func=compare_command)
    factor = sub.add_parser("factor", help="the loadings and persistence by refit, and the filtered factor against the onsets")
    factor.add_argument("--compare-input", required=True, help="the run files, with {h}")
    factor.add_argument("--panel", type=Path, required=True)
    factor.add_argument("--output", type=Path, required=True)
    factor.add_argument("--markdown", type=Path)
    factor.add_argument("--svg", type=Path, required=True)
    factor.set_defaults(func=factor_command)
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
