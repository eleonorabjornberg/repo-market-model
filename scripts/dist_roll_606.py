"""The best tier-1 passer's tier 3 and tier 5 failures (#606): step 1, the diagnosis.

A scratch measurement, not a record: it writes JSON and Markdown to the paths it is given and nothing into `docs/runs/`. It reads
forecasts that `scripts/satiation_distance_598.py run` and `scripts/announcement_dating_rescore.py run` already wrote, and the
judge's own output (`scripts/pressure_judge.py judge`), and reports, for `risk_gbm+settle+h41+dist_roll` and its parent
`risk_gbm+settle+h41`:

* per regime and lead: the predicted and realised rate of a pressure day at +5 bp, tier 3's test statistic (realised minus
  predicted, with its 90% stationary-bootstrap interval) and its threshold (the interval covers zero), the margin, and which
  regimes fail (only regimes with at least `calibration_min_pressure_days` pressure days are tested);
* tier 5: which of its two conditions fails (calibration; beating climatology) and by how much;
* how much of the shortfall comes from the risk-date part's exact zero on days that are not risk dates, and how many pressure
  days in each regime fall on such days.

No day after the judge's last scored day (2025-12-31) is read (`docs/decisions/lockbox.md`).

    PYTHONPATH=src python3 scripts/dist_roll_606.py diagnose --panel PUBLISHED.csv --judge OUT/judge_weighted.json \\
        --forecasts OUT/both_h{h}.json OUT/dist_h{h}.json --bench OUT/bench_h{h}.json \\
        --output OUT/diagnosis.json --markdown OUT/diagnosis.md

Step 2 (`declare`, `run`, `compare`, `report`) scores three variants of the best row, chosen from the diagnosis and declared in
`metadata/dist_roll_606.json` before any score; the script refuses an uncommitted declaration. Each variant recalibrates the
best row's own forecasts (no refit of the model), walk-forward on the judge's cadence, from the earlier pairs observable at each
block's fit; the scarcity state is read as of the decision instant (`pressure_judge._scarcity_states`), never a hindsight regime
label (ruling on #515):

* `+floor`: a floor on the days that are not risk dates, the walk-forward rate of pressure days among the earlier such days;
* `+state_floor`: the same floor per as-of scarcity state (the pooled rate while the state holds too few such days);
* `+state_platt`: Platt fitted per as-of scarcity state, the form that took tier 5 from no to yes in #602.

    # the scratch panels, the benchmarks, the parents and the best row: the commands of scripts/satiation_distance_598.py
    PYTHONPATH=src python3 scripts/dist_roll_606.py declare
    for h in 1 2 3 4 5: PYTHONPATH=src python3 scripts/dist_roll_606.py run --panel AUG2.csv --published PUBLISHED.csv \\
        --horizon $h --best OUT/dist_h$h.json --output OUT/v606_h$h.json
    for r in weighted unweighted: PYTHONPATH=src python3 scripts/pressure_judge.py judge --panel PUBLISHED.csv --rule $r \\
        --output OUT/judge2_$r.json --markdown OUT/judge2_$r.md OUT/bench_h?.json OUT/risk_h?.json OUT/ql_h?.json OUT/both_h?.json OUT/v606_h?.json
    PYTHONPATH=src python3 scripts/dist_roll_606.py compare --panel PUBLISHED.csv --bench 'OUT/bench_h{h}.json' \\
        --risk 'OUT/risk_h{h}.json' --reference 'OUT/ql_h{h}.json' --parents 'OUT/both_h{h}.json' --rows 'OUT/v606_h{h}.json' \\
        --output OUT/compare.json --markdown OUT/compare.md
    PYTHONPATH=src python3 scripts/dist_roll_606.py report --compare OUT/compare.json --output OUT/report.md
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from datetime import date, time
from pathlib import Path
from typing import Dict, List, Mapping, Sequence

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))

from repo_model import group_calibration as gc, measurement_fields, probability_calibration as pc, pressure_judge as pj  # noqa: E402
from repo_model.baseline import climatology_exceedance, panel_sha256, rolling_exceedance_backtest  # noqa: E402
from repo_model.lockbox import require_unlocked  # noqa: E402
from repo_model.data import audit_panel, load_daily_panel  # noqa: E402
from repo_model.evaluation_splits import load_split_declaration  # noqa: E402

SPLITS = REPO / "metadata" / "evaluation_splits.json"
DECLARATION = REPO / "metadata" / "dist_roll_606.json"
CANDIDATES = REPO / "metadata" / "pressure_judge" / "candidates"
PARENT = "risk_gbm+settle+h41"
BEST = "risk_gbm+settle+h41+dist_roll"
ROWS = (PARENT, BEST)
VARIANT_NAMES = {"floor": BEST + "+floor", "state_floor": BEST + "+state_floor", "state_platt": BEST + "+state_platt"}


def _load(name: str):
    spec = importlib.util.spec_from_file_location(f"{name}_script", REPO / "scripts" / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[f"{name}_script"] = module
    spec.loader.exec_module(module)
    return module


ann = _load("announcement_dating_rescore")
rds = _load("risk_date_severity")


def require_scored_window(last_day) -> None:
    """Refuse a last scored day after the judge's declared last day, or in a locked tier (`lockbox.md`)."""

    day = last_day if isinstance(last_day, date) else date.fromisoformat(last_day)
    pj.require_scored_days(pj.load_declaration(), [day], where="dist_roll_606")


def risk_date_shortfall(probabilities: Sequence[float], outcomes: Sequence[int], risk: Sequence[bool]) -> dict:
    """Split the mean shortfall (realised minus predicted) between risk dates and the days that are not.

    A risk-date row forecasts exactly 0 off its risk dates (`ml.pressure_risk_date_exceedance`); a non-zero forecast there is a
    defect, refused. All figures are per scored day, so that the two parts add to the total.
    """

    if not (len(probabilities) == len(outcomes) == len(risk)):
        raise ValueError("probabilities, outcomes and risk flags differ in length")
    if any(p != 0.0 for p, r in zip(probabilities, risk) if not r):
        raise ValueError("a risk-date row forecast a non-zero probability on a day that is not a risk date")
    n = len(outcomes)
    total = (sum(outcomes) - sum(probabilities)) / n if n else 0.0
    off = sum(y for y, r in zip(outcomes, risk) if not r) / n if n else 0.0
    return {
        "days": n,
        "risk_dates": sum(1 for r in risk if r),
        "pressure_days": sum(outcomes),
        "pressure_days_not_risk": sum(y for y, r in zip(outcomes, risk) if not r),
        "pressure_days_risk": sum(y for y, r in zip(outcomes, risk) if r),
        "mean_predicted": sum(probabilities) / n if n else None,
        "shortfall_total": total,
        "shortfall_not_risk": off,
        "shortfall_risk": total - off,
        "share_not_risk": (off / total) if total > 1e-12 else None,
    }


def regime_cell(cell: Mapping, *, minimum_events: int) -> dict:
    """Tier 3's reading of one regime cell: the statistic, its interval, whether it covers zero, and the margin.

    The margin is the distance from zero to the nearest end of the interval, positive when the interval covers zero (room to
    spare) and negative when it does not (how far the interval is from passing).
    """

    stat = cell["realised_minus_predicted"]
    lower, upper = stat["interval"]["lower"], stat["interval"]["upper"]
    covers = lower <= 0.0 <= upper
    margin = min(-lower, upper) if covers else -(lower if lower > 0.0 else -upper)
    return {
        "days": cell["days"],
        "events": cell["events"],
        "tested": cell["events"] >= minimum_events,
        "predicted": cell["mean_predicted"],
        "realised": cell["realised_frequency"],
        "difference": stat["mean"],
        "lower": lower,
        "upper": upper,
        "covers_zero": covers,
        "margin": margin,
    }


def _week_split(grids, by_horizon: Mapping[int, "pj.Forecast"], risk_by_h: Mapping[int, List[bool]], calendar: Sequence[date], tau: float, width: int) -> dict:
    """Tier 5's decision days, split by whether the forecast (the maximum over five leads) is exactly zero."""

    position = {h: {day: k for k, day in enumerate(grids[h].dates)} for h in range(1, width + 1)}
    outcomes, combined = [], []
    for i in range(len(calendar) - width):
        targets = [calendar[i + h] for h in range(1, width + 1)]
        if any(day not in position[h] for h, day in zip(range(1, width + 1), targets)):
            continue
        at = [position[h][day] for h, day in zip(range(1, width + 1), targets)]
        outcomes.append(max(grids[h].outcomes[tau][k] for h, k in zip(range(1, width + 1), at)))
        combined.append(max(by_horizon[h].probabilities[tau][k] for h, k in zip(range(1, width + 1), at)))
    zero = [p == 0.0 for p in combined]
    n = len(outcomes)
    return {
        "decision_days": n,
        "weeks_with_pressure": sum(outcomes),
        "weeks_forecast_zero": sum(zero),
        "weeks_with_pressure_forecast_zero": sum(1 for y, z in zip(outcomes, zero) if y and z),
        "mean_predicted": sum(combined) / n,
        "base_rate": sum(outcomes) / n,
        "shortfall_total": (sum(outcomes) - sum(combined)) / n,
        "shortfall_zero_forecast": sum(1 for y, z in zip(outcomes, zero) if y and z) / n,
    }


def diagnose(args) -> dict:
    declaration = pj.load_declaration()
    require_scored_window(declaration.last_day)
    rows = load_daily_panel(args.panel)
    audit_panel(rows)
    splits = load_split_declaration(SPLITS)
    by_date = {row.date: row for row in rows}
    calendar = [row.date for row in rows]
    judge = json.loads(Path(args.judge).read_text())
    digest = panel_sha256(args.panel)
    tau, width = declaration.primary, declaration.week_days
    minimum = declaration.calibration_min_events
    horizons = declaration.horizons

    forecasts: Dict[str, Dict[int, "pj.Forecast"]] = {name: {} for name in ROWS}
    reference = {}
    for h in horizons:
        for template in args.forecasts:
            document = json.loads(Path(template.format(h=h)).read_text())
            if document["panel_sha256"] != digest:
                raise SystemExit(f"{template.format(h=h)} was scored on another panel ({document['panel_sha256'][:8]})")
            for forecast in pj.forecasts_from_horizon_document(document):
                if forecast.name in forecasts:
                    forecasts[forecast.name][h] = forecast
        bench = json.loads(Path(args.bench.format(h=h)).read_text())
        reference[h] = next(f for f in pj.forecasts_from_horizon_document(bench) if f.name == declaration.climatology)
    for name in ROWS:
        missing = [h for h in horizons if h not in forecasts[name]]
        if missing:
            raise SystemExit(f"{name} has no forecast at horizons {missing}")
    grids = {h: pj.build_grid(declaration, h, rows, reference[h].dates, splits, scarcity_state={}) for h in horizons}

    out: Dict[str, dict] = {"panel_sha256": digest, "threshold_bp": tau, "rows": {}}
    for name in ROWS:
        verdict = judge["candidates"][name]["verdict"]
        cell = {"verdict": {k: verdict[k] for k in ("tier_1_onset_warning", "tier_3_no_crying_wolf", "tier_5_week_ahead", "passes")}}
        by_lead = {}
        for h in horizons:
            detail = judge["candidates"][name]["horizons"][str(h)][f"{tau:g}"]
            regimes = {label: regime_cell(c, minimum_events=minimum) for label, c in detail["splits"]["regime"].items()}
            by_lead[str(h)] = {
                "regimes": regimes,
                "failing": sorted(label for label, c in regimes.items() if c["tested"] and not c["covers_zero"]),
                "tier_3_ok": judge["candidates"][name]["tiers"]["no_crying_wolf"][str(h)]["ok"],
            }
        cell["tier_3_by_lead"] = by_lead
        week = judge["candidates"][name]["tiers"]["week_ahead"]
        stat = week["realised_minus_predicted"]
        clim = week["brier_difference_vs_climatology"]
        cell["tier_5"] = {
            "decision_days": week["days"],
            "events": week["events"],
            "base_rate": week["base_rate"],
            "mean_predicted": week["mean_predicted"],
            "criteria": week["criteria"],
            "calibration": {"difference": stat["mean"], "lower": stat["interval"]["lower"], "upper": stat["interval"]["upper"],
                            "covers_zero": stat["interval"]["lower"] <= 0.0 <= stat["interval"]["upper"],
                            "margin": stat["interval"]["lower"] if stat["interval"]["lower"] > 0 else None},
            "beats_climatology": {"difference": clim["mean"], "lower": clim["interval"]["lower"], "upper": clim["interval"]["upper"],
                                  "margin": clim["interval"]["lower"]},
        }
        risk_by_h = {}
        shortfall = {}
        for h in horizons:
            grid = grids[h]
            forecast = forecasts[name][h]
            if tuple(forecast.dates) != tuple(grid.dates):
                raise SystemExit(f"{name} h={h}: forecast days differ from the judge's grid")
            risk = [ann.risk_flag(splits, by_date[day].values, True) for day in grid.dates]
            risk_by_h[h] = risk
            p = forecast.probabilities[tau]
            y = grid.outcomes[tau]
            per = {"all": risk_date_shortfall(p, y, risk)}
            for label in sorted(set(grid.groups["regime"])):
                idx = [k for k, g in enumerate(grid.groups["regime"]) if g == label]
                per[label] = risk_date_shortfall([p[k] for k in idx], [y[k] for k in idx], [risk[k] for k in idx])
            shortfall[str(h)] = per
        cell["shortfall_by_lead"] = shortfall
        cell["week_split"] = _week_split(grids, forecasts[name], risk_by_h, calendar, tau, width)
        out["rows"][name] = cell
    return out


# -- step 2: the declaration --------------------------------------------------------------------------------------


def declaration_document() -> dict:
    sat = json.loads((REPO / "metadata" / "satiation_distance_598.json").read_text(encoding="utf-8"))
    return {
        "status": (
            "declared by the pull request that closes #606 before any score of a variant was computed; a measurement, not a record. "
            "Nothing is published: no variant joins any published declaration, no day after 2025-12-31 is scored, no rule changes and the "
            "live record and pin do not move. The variants were built after seeing 2018-2025, so a pass here is not a confirmation "
            "(ruling on #567)"
        ),
        "issue": 606,
        "ruling": "Eleonora, directive #606: at most 3 variants, chosen from the diagnosis of step 1 (docs/pivot/dist-roll-tier3-tier5-result.md); no hindsight regime labels (ruling on #515)",
        "diagnosis": (
            "step 1, committed before this file: tier 3 fails in 2018-19 and 2025-26 at every lead and tier 5 fails on its calibration "
            "condition, all as under-forecast; about nine tenths of the shortfall is carried by pressure days on days that are not risk "
            "dates, where the row forecasts exactly 0 (82 of 140 pressure days at the first lead). The variants therefore put mass on "
            "those days, or recalibrate by state as #602 did"
        ),
        "parent": {"row": BEST, "from": "metadata/satiation_distance_598.json, variant (a); its forecasts are not changed, only recalibrated"},
        "scoring": sat["scoring"],
        "thresholds_bp": sat["thresholds_bp"],
        "horizons": sat["horizons"],
        "variants": {
            VARIANT_NAMES["floor"]: {
                "label": "(a) floor",
                "parent": BEST,
                "rule": "on a day that is not a risk date the forecast is raised from 0 to the walk-forward rate of pressure days among the earlier days that were not risk dates and whose outcome was observable at the block's fit (group_calibration.walk_forward_floor); nothing is floored until those days number 60; risk dates keep the forecast",
                "implementation": "group_calibration.walk_forward_floor, per threshold, made non-increasing in tau (probability_calibration.monotone_curves)",
            },
            VARIANT_NAMES["state_floor"]: {
                "label": "(b) floor by state",
                "parent": BEST,
                "rule": "as (a), with the rate taken per as-of reserve-scarcity state (0 to 3, or unknown; each leg at its own latest public row, #586) once the state holds 60 such days and 3 pressure days, the pooled rate before",
                "implementation": "group_calibration.walk_forward_floor with the state label as the group",
            },
            VARIANT_NAMES["state_platt"]: {
                "label": "(c) state Platt",
                "parent": BEST,
                "rule": "Platt fitted per as-of scarcity state on the state's earlier observable pairs, the pooled Platt curve while the state holds fewer than 60 pairs or 3 events; the form that took tier 5 from no to yes in #602 (state_recalibration_589 variant a), applied to this row. Fitted on every scored day, so a day that is not a risk date takes the state's curve at the clipped zero",
                "implementation": "group_calibration.walk_forward('group') with the state label as the group, per threshold, made non-increasing in tau",
            },
        },
        "conditioning_variable": (
            "the reserve-scarcity state (0 to 3, or unknown) as of the decision instant of each forecast at its own horizon "
            "(pressure_judge._scarcity_states), for the pair a rate or curve is fitted on as for the day it is applied to; "
            "group_calibration.scarcity_state_label refuses any other value. No hindsight regime label (ruling on #515)"
        ),
        "off_risk_rule": "a scored day for which announcement_dating_rescore.risk_flag(splits, values, True) is false: its pressure-day type is ordinary and the day settles no coupon, as the row's own risk-date rule reads it",
        "cadence": "the judge's: a refit every 21 scored days from 61 days of history; a block's rate or curve is fitted on the pairs whose scored day is at or before its last training label (probability_calibration.past_positions)",
        "constants": {
            "group_minimum_pairs": gc.GROUP_MINIMUM_PAIRS,
            "group_minimum_events": gc.GROUP_MINIMUM_EVENTS,
            "pooled_gate_for_platt": f"{pc.MINIMUM_PAIRS} pairs and {pc.MINIMUM_EVENTS} events (probability_calibration)",
            "searched": "none: every constant is #380's or #589's, declared before any scoring",
        },
        "rows": {
            "controls": [PARENT, BEST],
            "controls_reading": "the parent and the best row as scored on main (the best row is recalibrated, not refitted), re-run in this measurement so that the pairs are on one run",
            "new": list(VARIANT_NAMES.values()),
            "pairs": {name: BEST for name in VARIANT_NAMES.values()},
            "pairs_reading": "each variant is paired with the best row it recalibrates",
        },
        "references": {
            "pair_against": ["risk_gbm", "ngboost_laplace", "calendar_climatology", "persistence_logistic"],
            "controls": [],
            "controls_reading": "the parents are the rows.controls; none is listed twice",
            "risk_date_passers": ["risk_gbm", "risk_logistic", "risk_gbm_base", "risk_logistic_base", "risk_quantile_skewt_base"],
        },
        "reports": {
            "judge": "the judge as declared under the weighted rule in force: tier 1 pooled and per lead, tiers 3 and 5, for every row beside the five risk-date passers, ngboost_laplace and the two benchmarks; each variant paired with the best row at +5 bp: the Brier difference at h = 1 to 5 and the onset recall difference, pooled and by regime and pressure-day type, 90% stationary-bootstrap intervals on shared resamples, the judge's seed",
            "calibration": "predicted against realised rate of a pressure day at +5 bp, by regime and pressure-day type, pooled over h = 1 to 5",
            "recall_by_year": "onset recall by calendar year",
            "gained_and_lost": "the onsets a variant warns and the best row does not, and the reverse, by date",
        },
        "unchanged": "the judge, its bar, its cut-off rule, the weighted miss rule in force, the bootstrap, every published declaration, the information set, the published scarcity indicator, the frozen shortlist of #567 and the lockbox. A measurement only: nothing is published and no day after 2025-12-31 is read (docs/decisions/lockbox.md).",
    }


def candidate_document(name: str) -> dict:
    base = json.loads((CANDIDATES / f"{BEST}.json").read_text(encoding="utf-8"))
    entry = dict(base)
    entry["track"] = "M (#606)"
    entry["parent"] = BEST
    added = {
        VARIANT_NAMES["floor"]: "then a floor on the days that are not risk dates: the walk-forward rate of pressure days among the earlier such days, observable at the block's fit (group_calibration.walk_forward_floor)",
        VARIANT_NAMES["state_floor"]: "then that floor per as-of reserve-scarcity state (each leg at its own latest public row, #586), the pooled floor while the state holds too few such days (group_calibration.walk_forward_floor with the state as the group)",
        VARIANT_NAMES["state_platt"]: "then Platt fitted per as-of reserve-scarcity state on the state's earlier observable pairs, pooled Platt while the state holds fewer than 60 pairs or 3 events (group_calibration.walk_forward('group'))",
    }[name]
    entry["calibration"] = base["calibration"] + "; " + added + "; metadata/dist_roll_606.json"
    entry.pop("inputs_note", None)
    return entry


def declare_command(args) -> int:
    DECLARATION.write_text(json.dumps(declaration_document(), indent=2) + "\n", encoding="utf-8")
    for name in VARIANT_NAMES.values():
        (CANDIDATES / f"{name}.json").write_text(json.dumps(candidate_document(name), indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"declaration": str(DECLARATION), "candidates": [str(CANDIDATES / f"{n}.json") for n in VARIANT_NAMES.values()]}))
    return 0


def declared_document() -> dict:
    return rds.committed_declaration(DECLARATION)


def all_rows() -> List[str]:
    document = declared_document()
    return list(document["rows"]["controls"]) + list(document["rows"]["new"])


def paired_with_model(name: str) -> List[str]:
    parent = declared_document()["rows"]["pairs"].get(name)
    return [parent] if parent else []


# -- step 2: run ---------------------------------------------------------------------------------------------------


def recalibrate(variant: str, forecasts_by_tau, outcomes_by_tau, scored, train_ends, off_risk, labels, taus):
    """{tau: [probability per scored day]} for one variant, non-increasing in tau."""

    columns = []
    for tau in taus:
        forecast, outcomes = list(forecasts_by_tau[tau]), list(outcomes_by_tau[tau])
        if variant == "floor":
            columns.append(gc.walk_forward_floor(forecast, outcomes, scored, train_ends, off_risk))
        elif variant == "state_floor":
            columns.append(gc.walk_forward_floor(forecast, outcomes, scored, train_ends, off_risk, labels))
        elif variant == "state_platt":
            columns.append(gc.walk_forward("group", forecast, outcomes, scored, train_ends, labels))
        else:
            raise ValueError(f"variant {variant!r} is not one of {tuple(VARIANT_NAMES)}")
    curves = pc.monotone_curves(list(zip(*columns)))
    return {tau: [curve[k] for curve in curves] for k, tau in enumerate(taus)}


def run_command(args) -> int:
    declared = declared_document()
    h = args.horizon
    if h not in declared["horizons"]:
        raise SystemExit(f"horizon {h} is not declared")
    last = date.fromisoformat(declared["scoring"]["last_day"])
    require_unlocked([last], where="dist_roll_606")
    require_scored_window(last)
    best_document = json.loads(args.best.read_text(encoding="utf-8"))
    if best_document["horizon"] != h or best_document["panel_sha256"] != panel_sha256(args.published):
        raise SystemExit(f"{args.best} is not the best row's forecasts at h = {h} on this panel")
    if BEST not in best_document["forecasts"]:
        raise SystemExit(f"{args.best} has no {BEST!r} row")
    best = best_document["forecasts"][BEST]
    rows = load_daily_panel(args.panel)
    audit_panel(rows)
    splits = load_split_declaration(SPLITS)
    by_date = {row.date: row for row in rows}
    taus = tuple(float(t) for t in declared["thresholds_bp"])
    minimum = declared["scoring"]["minimum_history"]
    registry = measurement_fields.load_registry()
    # the grid, the training ends and the outcomes: a backtest with the climatology, whose forecasts are not used
    report = rolling_exceedance_backtest(
        rows, predictor=climatology_exceedance(minimum), model_name="grid", features=("spread_bps",), registry=registry,
        decision_time=time.fromisoformat(declared["scoring"]["decision_time"]), taus=taus, minimum_history=minimum,
        refit_every=declared["scoring"]["refit_every"], end=last, horizon=h,
    )
    scored = list(report.scored_dates)
    train_ends = [fold.train_end for fold in report.folds]
    days = [day.isoformat() for day in scored]
    for tau in taus:
        if sorted(best[f"{tau:g}"]) != days:
            raise SystemExit(f"the best row's scored days at +{tau:g} bp are not the grid's at h = {h}")
    outcomes_by_tau = {tau: report.at_tau(report.taus.index(tau))[2] for tau in taus}
    forecasts_by_tau = {tau: [best[f"{tau:g}"][day] for day in days] for tau in taus}
    off_risk = [not ann.risk_flag(splits, by_date[day].values, True) for day in scored]
    for tau in taus:
        if any(p != 0.0 for p, o in zip(forecasts_by_tau[tau], off_risk) if o):
            raise SystemExit("the best row forecast a non-zero probability on a day that is not a risk date")
    states = _load("pressure_judge")._scarcity_states(h, last)
    labels = [gc.scarcity_state_label(states.get(day)) for day in scored]
    forecasts = {BEST: best}
    for variant, name in VARIANT_NAMES.items():
        recalibrated = recalibrate(variant, forecasts_by_tau, outcomes_by_tau, scored, train_ends, off_risk, labels, taus)
        forecasts[name] = {f"{tau:g}": {day: recalibrated[tau][k] for k, day in enumerate(days)} for tau in taus}
    document = {
        "horizon": h,
        "panel_sha256": panel_sha256(args.published),
        "scratch_panel_sha256": panel_sha256(args.panel),
        "declaration": declared,
        "calibration": gc.declaration(),
        "declarations": {
            name: {"parent": BEST, "state_counts": {label: labels.count(label) for label in sorted(set(labels))},
                   "off_risk_days": sum(off_risk)}
            for name in VARIANT_NAMES.values()
        },
        "forecasts": forecasts,
    }
    args.output.write_text(json.dumps(document, indent=1, sort_keys=True, default=str) + "\n", encoding="utf-8")
    print(json.dumps({"horizon": h, "output": str(args.output)}))
    return 0


# -- step 2: compare and report (the machinery of #598, over this declaration) -------------------------------------


def _patched_598():
    s598 = _load("satiation_distance_598")
    s598.DECLARATION = DECLARATION
    s598.declared_document = declared_document
    s598.all_rows = all_rows
    s598.paired_with_model = paired_with_model
    s598.FAMILIES = (("risk_gbm+settle+h41+dist_roll and its three recalibrations (#606)", (BEST,) + tuple(VARIANT_NAMES.values())),)
    return s598


def _retitle(text: str) -> str:
    return text.replace("# The rolling satiation distance in the tier-1 passers (#598)", "# The best tier-1 passer's tier 3 and tier 5 failures (#606)", 1)


def compare_command(args) -> int:
    s598 = _patched_598()
    markdown_path = args.markdown
    args.markdown = None
    status = s598.compare_command(args)
    if markdown_path:
        result = json.loads(Path(args.output).read_text())
        text = s598._markdown(result, declared_document(), list(result["readings"]["weighted"]), all_rows())
        markdown_path.write_text(_retitle(text), encoding="utf-8")
    return status


def report_command(args) -> int:
    s598 = _patched_598()
    compare = json.loads(Path(args.compare).read_text())
    args.output.write_text(_retitle(s598.report_text(compare)).replace("Generated by `scripts/satiation_distance_598.py report`", "Generated by `scripts/dist_roll_606.py report`"), encoding="utf-8")
    print(json.dumps({"output": str(args.output)}))
    return 0


def _pct(x):
    return "–" if x is None else f"{100 * x:.1f}%"


def markdown(result: dict) -> str:
    tau = result["threshold_bp"]
    lines = [
        "# Step 1: the best tier-1 passer's tier 3 and tier 5 failures (#606)", "",
        "Generated by `scripts/dist_roll_606.py diagnose`; not edited by hand.", "",
    ]
    for name, cell in result["rows"].items():
        v = cell["verdict"]
        lines += [f"## `{name}`", "",
                  f"Verdicts: tier 1 {'met' if v['tier_1_onset_warning'] else 'not met'}; tier 3 {'met' if v['tier_3_no_crying_wolf'] else 'not met'}; "
                  f"tier 5 {'met' if v['tier_5_week_ahead'] else 'not met'}; pass: {'yes' if v['passes'] else 'no'}.", "",
                  f"### Tier 3 by regime and lead (+{tau:g} bp): predicted, realised, realised minus predicted [90% interval], margin", "",
                  "A regime is tested when it has at least 20 pressure days; it passes when the interval covers zero. Margin: the distance from "
                  "the nearer end of the interval to zero, negative when the interval excludes zero.", "",
                  "| lead | regime | days | pressure days | predicted | realised | difference [interval] | tested | covers zero | margin |",
                  "|---|---|---|---|---|---|---|---|---|---|"]
        for h, lead in cell["tier_3_by_lead"].items():
            for label, c in lead["regimes"].items():
                lines.append(
                    f"| {h} | {label} | {c['days']} | {c['events']} | {c['predicted']:.4f} | {c['realised']:.4f} | "
                    f"{c['difference']:+.4f} [{c['lower']:+.4f}, {c['upper']:+.4f}] | {'yes' if c['tested'] else 'no'} | "
                    f"{'yes' if c['covers_zero'] else 'no'} | {c['margin']:+.4f} |")
        lines += ["", "Failing regimes by lead: " + "; ".join(f"h = {h}: {', '.join(l['failing']) or 'none'}" for h, l in cell["tier_3_by_lead"].items()) + ".", ""]
        t5 = cell["tier_5"]
        cal, clim = t5["calibration"], t5["beats_climatology"]
        lines += ["### Tier 5 (probability of a pressure day in the next five business days, maximum over the five leads)", "",
                  f"{t5['decision_days']} decision days, {t5['events']} with a pressure day (base rate {t5['base_rate']:.4f}); mean forecast {t5['mean_predicted']:.4f}.", "",
                  f"- Condition 1, calibrated (realised minus predicted, interval covers zero): {cal['difference']:+.4f} [{cal['lower']:+.4f}, {cal['upper']:+.4f}]: "
                  f"**{'holds' if t5['criteria']['calibrated'] else 'fails'}**" + (f", the interval's lower end is {cal['margin']:.4f} above zero." if cal["margin"] is not None else "."),
                  f"- Condition 2, beats climatology on Brier (difference, climatology minus row, interval above zero): {clim['difference']:+.4f} [{clim['lower']:+.4f}, {clim['upper']:+.4f}]: "
                  f"**{'holds' if t5['criteria']['beats_climatology_brier'] else 'fails'}**, margin {clim['margin']:+.4f}.", ""]
        w = cell["week_split"]
        lines += [f"Weeks: {w['weeks_with_pressure']} of {w['decision_days']} have a pressure day; the row forecasts exactly 0 for {w['weeks_forecast_zero']} weeks, "
                  f"and {w['weeks_with_pressure_forecast_zero']} of the weeks with a pressure day are among them. Shortfall per decision day "
                  f"{w['shortfall_total']:+.4f}, of which {w['shortfall_zero_forecast']:.4f} sits on the zero-forecast weeks.", ""]
        lines += [f"### Do the misses come from the exact zero off the risk dates? (+{tau:g} bp, per lead)", "",
                  "Shortfall = mean of realised minus predicted per scored day; 'off' = the part carried by pressure days on days that are not risk dates.", "",
                  "| lead | regime | days | risk dates | pressure days | of which not on a risk date | shortfall | off-risk-date part | share off |",
                  "|---|---|---|---|---|---|---|---|---|"]
        for h, per in cell["shortfall_by_lead"].items():
            for label, s in per.items():
                lines.append(f"| {h} | {label} | {s['days']} | {s['risk_dates']} | {s['pressure_days']} | {s['pressure_days_not_risk']} | "
                             f"{s['shortfall_total']:+.4f} | {s['shortfall_not_risk']:.4f} | {_pct(s['share_not_risk'])} |")
        lines.append("")
    return "\n".join(lines) + "\n"


def diagnose_command(args) -> int:
    result = diagnose(args)
    args.output.write_text(json.dumps(result, indent=1, sort_keys=True, default=str) + "\n", encoding="utf-8")
    if args.markdown:
        args.markdown.write_text(markdown(result), encoding="utf-8")
    print(json.dumps({"output": str(args.output)}))
    return 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    sub = parser.add_subparsers(dest="command", required=True)
    p = sub.add_parser("diagnose")
    p.add_argument("--panel", type=Path, required=True)
    p.add_argument("--judge", type=Path, required=True)
    p.add_argument("--forecasts", nargs="+", required=True)
    p.add_argument("--bench", required=True)
    p.add_argument("--output", type=Path, required=True)
    p.add_argument("--markdown", type=Path)
    sub.add_parser("declare")
    p = sub.add_parser("run")
    p.add_argument("--panel", type=Path, required=True)
    p.add_argument("--published", type=Path, required=True)
    p.add_argument("--horizon", type=int, required=True)
    p.add_argument("--best", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True)
    p = sub.add_parser("compare")
    p.add_argument("--panel", type=Path, required=True)
    for name in ("bench", "risk", "reference", "parents", "rows"):
        p.add_argument(f"--{name}", required=True)
    p.add_argument("--output", type=Path, required=True)
    p.add_argument("--markdown", type=Path)
    p = sub.add_parser("report")
    p.add_argument("--compare", required=True)
    p.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)
    return {"diagnose": diagnose_command, "declare": declare_command, "run": run_command, "compare": compare_command, "report": report_command}[args.command](args)


if __name__ == "__main__":
    sys.exit(main())
