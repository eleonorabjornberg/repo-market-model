"""The combined model (#561, of #374): the risk-date passer, a calibrated ordinary-day logistic and a false-alarm gate.

A scratch measurement, not a record: it writes JSON and Markdown to the paths it is given and nothing into
`docs/runs/`. Every choice is in `metadata/combined_model_561.json`, which this script refuses to read unless it is
committed and unchanged, and in the candidates in `metadata/pressure_judge/candidates/`. Every input beyond the
published panel is off in every published declaration and switched on for these runs only. Scored days are
2018-06-29 to 2025-12-31; no day of the 2026 tiers is read (`docs/decisions/lockbox.md`).

    PYTHONPATH=src python3 scripts/pressure_v1_1.py panel --output AUG.csv
    PYTHONPATH=src python3 scripts/measurement_fields.py panel --panel AUG.csv --output AUG2.csv
    PYTHONPATH=src python3 scripts/net_settlement.py panel --panel AUG2.csv --output AUG3.csv
    PYTHONPATH=src python3 scripts/projected_reserves.py panel --panel AUG3.csv --output AUG4.csv
    PYTHONPATH=src python3 scripts/pressure_judge.py forecasts --panel PUBLISHED.csv --horizon H --output OUT/bench_hH.json
    PYTHONPATH=src python3 scripts/risk_date_severity.py run --panel AUG2.csv --published PUBLISHED.csv --horizon H --output OUT/risk_hH.json
    PYTHONPATH=src python3 scripts/pressure_track_q.py forecasts --panel PUBLISHED.csv --horizon H --output OUT/q_hH.json --distribution OUT/qdist_hH.json
    PYTHONPATH=src python3 scripts/announcement_dating_rescore.py run --arm both --panel AUG2.csv --published PUBLISHED.csv --horizon H --output OUT/both_hH.json
    PYTHONPATH=src python3 scripts/combined_model_561.py run --panel AUG4.csv --published PUBLISHED.csv --horizon H \\
        --parents OUT/both_hH.json --output OUT/cm_hH.json
    PYTHONPATH=src python3 scripts/pressure_judge.py judge --panel PUBLISHED.csv --rule weighted --output OUT/judge_weighted.json \\
        --markdown OUT/judge_weighted.md OUT/bench_h?.json OUT/risk_h?.json OUT/q_h?.json OUT/both_h?.json OUT/cm_h?.json
    PYTHONPATH=src python3 scripts/combined_model_561.py compare --panel PUBLISHED.csv --bench 'OUT/bench_h{h}.json' \\
        --risk 'OUT/risk_h{h}.json' --reference 'OUT/q_h{h}.json' --parents 'OUT/both_h{h}.json' --rows 'OUT/cm_h{h}.json' \\
        --output OUT/compare.json --markdown OUT/compare.md

`run` fits the ordinary-day component (`ml.pressure_combined_ordinary_exceedance`) walk-forward at +5 and +10 bp on the
shared fold grid with all three blocks and with each block dropped in turn, and puts each under the risk-date passer
(the passer's forecast on a risk date, the component's on any other day, the rule of #506), then applies the gate of
#532 to the days that are not risk dates. The passers are those of `announcement_dating_rescore.py --arm both`
(settlements dated from the announcement, the H.4.1 read per release; #541). The component is scored on the published
timing, the one its inputs were built and scored on (#542, #543, #545).

`compare` is the judge's own cut-offs and tiers, tier 1 under readings (a) to (e) of
`docs/pivot/judge-readings-result.md`, onsets warned by calendar year, Brier score and log loss, the paired comparison with
each reference, and the predicted rate against the realised rate by regime.
"""

from __future__ import annotations

import argparse
import contextlib
import importlib.util
import json
import math
import sys
from collections import defaultdict
from dataclasses import replace
from datetime import date, time
from pathlib import Path
from typing import Dict, List, Mapping, Optional, Sequence

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))

from repo_model import measurement_fields, ml, pressure_judge as pj, structural_liquidity as sl  # noqa: E402
from repo_model.baseline import panel_sha256, rolling_exceedance_backtest  # noqa: E402
from repo_model.data import audit_panel, load_daily_panel  # noqa: E402
from repo_model.evaluation_splits import load_split_declaration  # noqa: E402
from repo_model.lockbox import require_unlocked  # noqa: E402

DECLARATION = REPO / "metadata" / "combined_model_561.json"
PARENTS_FILE = REPO / "metadata" / "risk_date_severity.json"
SPLITS = REPO / "metadata" / "evaluation_splits.json"
CANDIDATES = REPO / "metadata" / "pressure_judge" / "candidates"
PARENTS = ("risk_gbm", "risk_logistic")
#: the parent's name under the timing arm the passer runs in (`announcement_dating_rescore.py --arm both`)
TIMING_SUFFIX = "+settle+h41"
#: the control of #541 that the combination is read against: the passer with the three-input every-day component and the gate
CONTROL_SUFFIX = "+every_day+gate" + TIMING_SUFFIX
#: component name -> its blocks. "full" is the model; the others each drop one block (the ablation)
COMPONENTS = {
    "full": ml.COMBINED_BLOCKS,
    "no_factor": ("structural", "projected"),
    "no_structural": ("factor", "projected"),
    "no_projected": ("factor", "structural"),
}
COUPONS = "treasury_settlement_coupons"
RULES = ("unweighted", "weighted", "weighted/before_only")
LOG_LOSS_FLOOR = 1e-6


def _load(name: str):
    spec = importlib.util.spec_from_file_location(f"{name}_script", REPO / "scripts" / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[f"{name}_script"] = module
    spec.loader.exec_module(module)
    return module


rds = _load("risk_date_severity")
fa = _load("risk_date_false_alarm_controls")
ann = _load("announcement_dating_rescore")
prs = _load("projected_reserves")
lf = _load("latent_factor")


# -- names ------------------------------------------------------------------------------------------------


def row_name(parent: str, component: str = "full", gate: bool = True) -> str:
    """The judge's name of a combined row: `risk_gbm+combined`, `risk_gbm+combined_nogate`, `risk_gbm+combined_no_factor`."""

    if component == "full":
        return f"{parent}+combined" + ("" if gate else "_nogate")
    if not gate:
        raise ValueError("an ablation is gated like the model")
    return f"{parent}+combined_{component}"


def variant_names() -> List[str]:
    """The four variants: each parent, with and without the gate."""

    return [row_name(p, gate=g) for p in PARENTS for g in (True, False)]


def ablation_names() -> List[str]:
    """The three ablations: the gated model under `risk_gbm` with a block dropped."""

    return [row_name(PARENTS[0], c) for c in COMPONENTS if c != "full"]


def all_rows() -> List[str]:
    return variant_names() + ablation_names()


def paired_with_model(name: str) -> List[str]:
    """The combined row an ablation is paired against: an ablation or an ungated variant against the gated model of its parent."""

    parent = name.split("+")[0]
    if name in ablation_names() or name == row_name(parent, gate=False):
        return [row_name(parent)]
    return []


# -- the declaration --------------------------------------------------------------------------------------


def declared_document() -> dict:
    return rds.committed_declaration(DECLARATION)


def component_features(horizon: int, blocks: Sequence[str]):
    """`(the design's features, the features the backtest declares)` for the ordinary-day component at `horizon`."""

    design: List[str] = ["spread_bps"]
    if "structural" in blocks:
        design = list(sl.features_at_horizon(horizon))
    if "projected" in blocks:
        design.append(f"proj_dist_h{horizon}")
    backtest = list(design) + (list(ml.LATENT_FACTOR_COLUMNS) if "factor" in blocks else [])
    return tuple(dict.fromkeys(design)), tuple(dict.fromkeys(backtest))


def declaration_document(parents: dict) -> dict:
    controls = json.loads((REPO / "metadata" / "risk_date_false_alarm_controls.json").read_text(encoding="utf-8"))["controls"]
    gate = controls["gate"]
    full_design, full_backtest = component_features(2, ml.COMBINED_BLOCKS)
    return {
        "status": (
            "declared by the pull request that closes #561 before any score was computed; a measurement, not a record. Nothing here is "
            "published: every input is off in every published declaration, no 2026 day is scored, no rule changes and the live record and "
            "pin do not move. The choices below are the directive's, written down once; only the logistic's coefficients, the factor's "
            "parameters and the calibration curve are fitted, on the judge's cadence"
        ),
        "issue": 561,
        "scoring": parents["scoring"],
        "thresholds_bp": parents["thresholds_bp"],
        "horizons": parents["horizons"],
        "parents": {name: parents["candidates"][name] for name in PARENTS},
        "parents_declaration": "metadata/risk_date_severity.json (unchanged: the risk dates, the features, the estimators)",
        "parent_timing": "both",
        "parent_timing_reading": (
            "the passers are scored as in scripts/announcement_dating_rescore.py --arm both (#541): settlements dated from the auction "
            "announcement (metadata/settlement_announcement_dating.json), the settlement columns kept at every horizon and the coupon "
            "clause of the risk-date rule applied at h >= 2, and the H.4.1 weeklies read per release (metadata/h41_release_dating.json). "
            "The ordinary-day component is scored on the published timing, the one its inputs were built and scored on (#542, #543, "
            "#545); the projected-reserves columns are built from the published H.4.1 lag"
        ),
        "ordinary_days": {
            "form": (
                "one walk-forward ridge logistic of spread > tau per threshold (ml.PRESSURE_LOGISTIC_SETTINGS), fitted on the direct pairs of "
                "every training day under the as-of rule, on the spread and the three blocks below, then mapped through a calibration curve"
            ),
            "blocks": list(ml.COMBINED_BLOCKS),
            "block_columns": {
                "factor": [
                    "factor_level: the filtered level of the latent funding-stress factor (#543, metadata/latent_factor.json, fitted on the refit's training frame) at the forecast's anchor row",
                    f"factor_change_{ml.COMBINED_FACTOR_CHANGE_ROWS}: that level less the level {ml.COMBINED_FACTOR_CHANGE_ROWS} rows earlier",
                ],
                "structural": [
                    "e_x_shortfall, e_x_tga_up, e_x_tax_date, e_x_window: the four structural terms of #542 (metadata/structural_liquidity.json), the reserve-demand elasticity times the drain the ON RRP balance has not absorbed, the TGA rise, the tax date and the window",
                ],
                "projected": [
                    "proj_dist_h{h}: the projected reserves over bank assets above the satiation level at the scored day (#545, metadata/projected_reserves.json)",
                ],
            },
            "factor_change_rows": ml.COMBINED_FACTOR_CHANGE_ROWS,
            "inputs_at_horizon_2": {"design": list(full_design), "declared_to_the_backtest": list(full_backtest)},
            "calibration": ml.COMBINED_CALIBRATION,
            "calibration_reading": (
                "Platt, as the headline of the hurdle (#539): walk-forward, refit on the judge's cadence (minimum history 61, refit every "
                "21 scored days), cut into five blocks of the training pairs in date order, the identity until 250 out-of-sample pairs hold "
                "5 events (ml._walk_forward_calibrator). Chosen before any score, not tuned"
            ),
            "conditioning": (
                "on the as-of columns above only. It is never conditioned on a hindsight regime label (metadata/evaluation_splits.json "
                "regimes were drawn after the fact; ruling on #515)"
            ),
            "missing_input": "a served day whose inputs are not all public is refused (ValueError), not forecast 0; the run says how many",
        },
        "gate": {
            "control": "gate",
            "from": "#532 (metadata/risk_date_false_alarm_controls.json, scripts/risk_date_false_alarm_controls.py)",
            "why": (
                "the one of #534's four controls that passed tier 1 under the weighted rule in force (the other that passed tier 1, +shrunk, "
                "passed it under the flat rule only). Declared as #532 declared it, not tuned"
            ),
            "quantile": gate["quantile"],
            "window": gate["window"],
            "minimum_earlier": gate["minimum_earlier"],
            "applies_to": (
                "the ordinary-day component's forecast on a day that is not a risk date, from forecasts already issued on earlier scored "
                "days; a risk date keeps the passer's forecast"
            ),
            "rule": gate["rule"],
        },
        "combination": (
            "on a risk date the passer's forecast, unchanged; on any other day the component's, then the gate; the curve across thresholds is "
            "made non-increasing afterwards. Risk dates are the days whose pressure-day type is not ordinary and any day on which coupons settle "
            "(known h days ahead from the announcement, the arm the passer runs in)"
        ),
        "variants": {
            row_name(p, gate=g): {
                "parent": p,
                "gate": g,
                "blocks": list(ml.COMBINED_BLOCKS),
            }
            for p in PARENTS
            for g in (True, False)
        },
        "ablations": {
            row_name(PARENTS[0], c): {
                "parent": PARENTS[0],
                "gate": True,
                "blocks": list(blocks),
                "dropped": next(b for b in ml.COMBINED_BLOCKS if b not in blocks),
            }
            for c, blocks in COMPONENTS.items()
            if c != "full"
        },
        "ablation_reading": (
            "criterion 3 of #561: each block (factor, structural, projected, gate) dropped in turn from the gated model under risk_gbm. The gate "
            "is dropped by the variant risk_gbm+combined_nogate; the others are the three ablation rows. They are analysis rows of the "
            "criterion, not a fifth variant"
        ),
        "references": {
            "pair_against": ["risk_gbm", "ngboost_laplace", "calendar_climatology", "persistence_logistic"],
            "controls": [name + TIMING_SUFFIX for name in PARENTS] + [name + CONTROL_SUFFIX for name in PARENTS],
            "controls_reading": (
                "the passers with settlement and H.4.1 timing on (the base the combination is built on), and the same with the three-input "
                "every-day component and the gate of #541's table (the best earlier version of this construction). Every row is also paired "
                "against these two"
            ),
            "risk_date_passers": list(PARENTS) + ["risk_gbm_base", "risk_logistic_base", "risk_quantile_skewt_base"],
        },
        "judging": (
            "the judge as declared (metadata/pressure_judge.json), unchanged, under the weighted miss rule in force and beside it the flat rule: "
            "tiers 1, 3 and 5, h = 1 to 5, +5 and +10 bp; tier 1 pooled and per lead; recall by calendar year with 2018, 2020 and 2024 called "
            "out; the predicted rate against the realised rate by regime. Paired against the references with 90% stationary-bootstrap "
            "intervals, split by regime and pressure-day type"
        ),
        "selection": (
            "The combination was chosen after seeing the results of #539, #541, #542, #543, #545 and #534 on these same days (2018-06-29 to "
            "2025-12-31), so a pass here is not a confirmation. Only the 2026 confirmation window can confirm it, and it is not opened here: "
            "no row below is in the confirmation look"
        ),
        "reports": [
            "docs/pivot/combined-model-result.md",
            "docs/pivot/evidence/combined-model/",
        ],
        "unchanged": [
            "the judge's bar, tiers, thresholds, horizons and cut-off rule",
            "the information-set rule, every availability time, and every published declaration",
            "metadata/lockbox.json: no lockbox tier is opened, no 2026 day is scored",
        ],
        "published": "nothing: every input is off in every published declaration; no rule, threshold, definition or availability time changes",
    }


def candidate_entry(name: str, spec: dict) -> dict:
    parent_name = spec["parent"] + TIMING_SUFFIX
    base = json.loads((CANDIDATES / f"{parent_name}.json").read_text(encoding="utf-8"))
    blocks = spec["blocks"]
    extra: List[str] = []
    if "structural" in blocks:
        extra += ["bank_total_assets", "net_settlement"]
    if "projected" in blocks:
        extra += ["proj_dist_h1"]
    if "factor" in blocks:
        extra += list(ml.LATENT_FACTOR_COLUMNS)
    entry = dict(base)
    entry["track"] = "H (#561)"
    entry["parent"] = parent_name
    entry["features"] = list(dict.fromkeys(list(base["features"]) + extra))
    entry["features_at_horizon_2_or_more"] = (
        "with treasury_settlement and treasury_settlement_coupons for the passer; the component reads net_settlement_due_5d in place of "
        "net_settlement and proj_dist_h{h} for the horizon h"
    )
    dropped = spec.get("dropped")
    entry["calibration"] = (
        "the passer's forecast on a risk date, unchanged; on any other day the ordinary-day logistic on "
        + ", ".join(blocks)
        + (f" (the {dropped} block dropped)" if dropped else "")
        + f", {ml.COMBINED_CALIBRATION}-calibrated walk-forward"
        + (", then the '" + "gate" + "' false-alarm control of #532" if spec["gate"] else ", without the gate")
        + "; the passer scored with settlements dated from the announcement and the H.4.1 read per release; metadata/combined_model_561.json"
    )
    return entry


def declare_command(args) -> int:
    parents = json.loads(PARENTS_FILE.read_text(encoding="utf-8"))
    document = declaration_document(parents)
    DECLARATION.write_text(json.dumps(document, indent=2) + "\n", encoding="utf-8")
    made = 0
    for group in ("variants", "ablations"):
        for name, spec in document[group].items():
            (CANDIDATES / f"{name}.json").write_text(json.dumps(candidate_entry(name, spec), indent=2) + "\n", encoding="utf-8")
            made += 1
    print(json.dumps({"declaration": str(DECLARATION), "candidates": made}))
    return 0


# -- combining ---------------------------------------------------------------------------------------------


def combine(parent: Mapping[str, Mapping[str, float]], own: Mapping[str, Mapping[str, float]], off: Mapping[str, bool]):
    """The passer's forecast on a risk date, the component's on any other day (`off`: the day is not a risk date).

    Raises:
        ValueError: if the two cover different thresholds or days, or the passer forecasts above 0 on a day that is not a risk date
            (the rule assumes it is exactly 0 there).
    """

    if set(parent) != set(own):
        raise ValueError("the passer and the component must cover the same thresholds")
    out: Dict[str, Dict[str, float]] = {}
    for tau in parent:
        if set(parent[tau]) != set(own[tau]) or set(off) != set(parent[tau]):
            raise ValueError(f"the passer and the component were not scored on the same days at {tau} bp")
        bad = [when for when, value in parent[tau].items() if off[when] and value != 0.0]
        if bad:
            raise ValueError(f"the passer forecasts {bad[:3]}, which are not risk dates, above 0")
        out[tau] = {when: own[tau][when] if off[when] else value for when, value in parent[tau].items()}
    return out


def apply_gate(column: Mapping[str, Mapping[str, float]], off: Mapping[str, bool]) -> Dict[str, Dict[str, float]]:
    """#532's gate on the days that are not risk dates (`off`), from forecasts already issued."""

    keys = list(column)
    days = sorted(column[keys[0]])
    raw = [[column[key][day] for day in days] for key in keys]
    out = fa.apply_control("gate", fa.CONTROLS["gate"], raw, [off[day] for day in days], [None] * len(days))
    return {key: dict(zip(days, out[j])) for j, key in enumerate(keys)}


# -- run ---------------------------------------------------------------------------------------------------


def _recording(predictor, log: list):
    """The predictor, unchanged, with each call's fit recorded."""

    def fit_predict(train_rows, feature_rows, taus, information=None, histories=None):
        result = predictor(train_rows, feature_rows, taus, information=information, histories=histories)
        settings = dict(result.model_settings)
        settings.pop("filtered_factor", None)
        log.append(
            {
                "first_anchor": feature_rows[0].date.isoformat(),
                "training_rows": len(train_rows),
                "served_days": len(feature_rows),
                **{k: v for k, v in settings.items() if k.startswith("combined_") and k != "combined_columns"},
                **({"persistence": settings["persistence"]} if "persistence" in settings else {}),
            }
        )
        return result

    return fit_predict


def run_command(args) -> int:
    declared = declared_document()
    h = args.horizon
    if h not in declared["horizons"]:
        raise SystemExit(f"horizon {h} is not declared")
    last = date.fromisoformat(declared["scoring"]["last_day"])
    require_unlocked([last], where="combined_model_561")
    rows = load_daily_panel(args.panel)
    audit_panel(rows)
    splits = load_split_declaration(SPLITS)
    registry = measurement_fields.load_registry()
    taus = tuple(float(t) for t in declared["thresholds_bp"])
    minimum = declared["scoring"]["minimum_history"]
    columns, logs, settings = {}, {}, {}
    for component, blocks in COMPONENTS.items():
        design_features, backtest_features = component_features(h, blocks)
        log: list = []
        predictor = _recording(
            ml.pressure_combined_ordinary_exceedance(
                design_features, splits, minimum_history=minimum, blocks=blocks, calibration=declared["ordinary_days"]["calibration"]
            ),
            log,
        )
        with prs.switched_on():
            report = rolling_exceedance_backtest(
                rows,
                predictor=predictor,
                model_name=f"combined_{component}",
                features=backtest_features,
                registry=registry,
                decision_time=time.fromisoformat(declared["scoring"]["decision_time"]),
                taus=taus,
                minimum_history=minimum,
                refit_every=declared["scoring"]["refit_every"],
                end=last,
                horizon=h,
            )
        columns[component] = rds.column(report)
        logs[component] = log
        settings[component] = fa._settings(report)
        print(json.dumps({"horizon": h, "component": component, "refits": len(log), "done": True}), flush=True)
    parents_doc = json.loads(Path(args.parents).read_text())
    if parents_doc["panel_sha256"] != panel_sha256(args.published):
        raise SystemExit(f"{args.parents} was scored on another panel")
    timed_rows, _registry = ann.arm_inputs("both", rows, registry, h)
    by_date = {row.date: row for row in timed_rows}
    days = sorted(columns["full"][f"{taus[0]:g}"])
    off = {day: not ann.risk_flag(splits, by_date[date.fromisoformat(day)].values, True) for day in days}
    forecasts = {}
    for parent in PARENTS:
        passer = parents_doc["forecasts"][parent + TIMING_SUFFIX]
        plain = combine(passer, columns["full"], off)
        forecasts[row_name(parent, gate=False)] = plain
        forecasts[row_name(parent)] = apply_gate(plain, off)
    for component in COMPONENTS:
        if component == "full":
            continue
        passer = parents_doc["forecasts"][PARENTS[0] + TIMING_SUFFIX]
        forecasts[row_name(PARENTS[0], component)] = apply_gate(combine(passer, columns[component], off), off)
    document = {
        "horizon": h,
        "panel_sha256": panel_sha256(args.published),
        "scratch_panel_sha256": panel_sha256(args.panel),
        "declaration": declared,
        "declarations": settings,
        "risk_date_check": {"scored_days": len(days), "risk_dates": sum(1 for v in off.values() if not v)},
        "refits": logs,
        "components": columns,
        "forecasts": forecasts,
    }
    args.output.write_text(json.dumps(document, indent=1, sort_keys=True, default=str) + "\n", encoding="utf-8")
    print(json.dumps({"horizon": h, "output": str(args.output)}))
    return 0


# -- compare -----------------------------------------------------------------------------------------------


def log_loss(probabilities, outcomes):
    return lf.log_loss(probabilities, outcomes)


def brier(probabilities, outcomes):
    return lf.brier(probabilities, outcomes)


def calibration_by_regime(grids, by_name, names, tau, horizons):
    """Predicted against realised rate of `spread > tau`, by regime and for the ordinary-day type, per row."""

    out: Dict[str, dict] = {}
    for n in names:
        cells: Dict[str, List[float]] = defaultdict(lambda: [0.0, 0.0, 0.0])
        for h in horizons:
            grid = grids[h]
            p = by_name[n][h].probabilities[tau]
            y = grid.outcomes[tau]
            for k, (pk, yk) in enumerate(zip(p, y)):
                for key in ("all", "regime " + grid.groups["regime"][k], "day type " + grid.groups["day_type"][k]):
                    cell = cells[key]
                    cell[0] += 1.0
                    cell[1] += pk
                    cell[2] += yk
        out[n] = {key: {"days": c[0], "predicted": c[1] / c[0], "realised": c[2] / c[0]} for key, c in sorted(cells.items())}
    return out


def compare_command(args) -> int:
    ngb = _load("ngboost_laplace_check")
    jr = _load("judge_readings")
    judge_script = _load("pressure_judge")
    document = declared_document()
    judge_commit = judge_script.require_committed_declaration(pj.DEFAULT_DECLARATION)
    judge_script.require_committed_file(pj.DEFAULT_WEIGHTED_MISS)
    base = pj.load_declaration()
    if not pj.load_weighted_miss().in_force:
        raise SystemExit("the weighted miss rule is not in force; this comparison reads the rule in force")
    rows_names = all_rows()
    refs = document["references"]
    passers = refs["risk_date_passers"]
    controls = refs["controls"]
    pair_against = list(refs["pair_against"])
    extra = [n for n in pair_against if n not in (base.climatology, base.persistence, PARENTS[0])]
    benchmarks = [base.climatology, base.persistence]
    names = rows_names + passers + extra + controls + benchmarks
    rows = load_daily_panel(args.panel)
    audit_panel(rows)
    splits = load_split_declaration(SPLITS)
    digest = panel_sha256(args.panel)
    horizons = base.horizons
    if list(horizons) != document["horizons"] or base.last_day != date.fromisoformat(document["scoring"]["last_day"]):
        raise SystemExit("the judge's horizons or last day are not the declared ones")
    forecasts, panels = [], {}
    for h in horizons:
        for label, template in (("bench", args.bench), ("risk", args.risk), ("reference", args.reference), ("parents", args.parents), ("rows", args.rows)):
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
        "cross_check": {}, "scores": {}, "only_row": {}, "calibration": {},
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
                reverse = ngb.only_this_row_warns(days, anchor.onset, lf._any_of(passers_caught), [caught[n]])
                result["only_row"][n] = {
                    "row_only": [
                        {"day": d.isoformat(), "horizons": [h for h in series[n].horizons if series[n].flags[h][days.index(d)]]}
                        for d in only
                    ],
                    "passers_only": [d.isoformat() for d in reverse],
                    "onsets": int(sum(anchor.onset)),
                    "row_warns": int(sum(1 for o, c in zip(anchor.onset, caught[n]) if o and c)),
                    "at_least_one_passer_warns": int(sum(1 for o, c in zip(anchor.onset, lf._any_of(passers_caught)) if o and c)),
                }
            for n in names:
                result["scores"][n] = {}
                for h in horizons:
                    grid = grids[h]
                    p = by_name[n][h].probabilities[tau]
                    y = grid.outcomes[tau]
                    result["scores"][n][str(h)] = {"brier": brier(p, y), "log_loss": log_loss(p, y), "days": len(y)}
            result["calibration"] = calibration_by_regime(grids, by_name, rows_names + controls + [PARENTS[0], "ngboost_laplace"], tau, horizons)
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
                references = pair_against + controls + paired_with_model(n)
                for ref in references:
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
    result["declaration"] = {"path": "metadata/combined_model_561.json", "judge_commit": judge_commit}
    result["provenance"] = {"panel_sha256": digest, "forecast_panels": panels}
    args.output.write_text(json.dumps(result, indent=1, sort_keys=True, default=str) + "\n", encoding="utf-8")
    if args.markdown:
        args.markdown.write_text(markdown(result, document, names, rows_names), encoding="utf-8")
    print(json.dumps({"output": str(args.output)}))
    return 0


# -- the summary ------------------------------------------------------------------------------------------


def markdown(result: dict, document: dict, names: List[str], rows_names: List[str]) -> str:
    text = lf.markdown(result, document, names, rows_names)
    text = text.replace("# The latent funding-stress factor (#543)", "# The combined model (#561)", 1)
    lines = ["## Predicted against realised rate of a pressure day (+5 bp), by regime and day type, pooled over h = 1 to 5", ""]
    for n, cells in result["calibration"].items():
        lines += [f"### {n}", "", "| cell | days | predicted | realised |", "|---|---|---|---|"]
        for key, c in cells.items():
            lines.append(f"| {key} | {c['days']:g} | {c['predicted']:.4f} | {c['realised']:.4f} |")
        lines.append("")
    return text + "\n" + "\n".join(lines) + "\n"


# -- the summary ------------------------------------------------------------------------------------------


def summary_rows(document: dict) -> List[str]:
    """The rows of Table 1: the combined rows, their controls, the references and the benchmarks."""

    refs = document["references"]
    return all_rows() + list(refs["controls"]) + ["risk_gbm", "ngboost_laplace", "calendar_climatology", "persistence_logistic"]


def summary_table(document: dict, flat: Mapping[str, dict], weighted: Mapping[str, dict]) -> str:
    """The judge's tier 1 row at +5 bp for every row, under the flat and the weighted rule."""

    lines = [
        "| model | onsets flagged, flat / weighted rule | recall, flat [90%] | recall, weighted [90%] | worst false alarms per onset, flat | worst weighted false alarms per onset, weighted rule | tiers 1 / 3 / 5, flat | tiers 1 / 3 / 5, weighted | passes the full rule, flat / weighted |",
        "|---|---|---|---|---|---|---|---|---|",
    ]
    yes = lambda x: "yes" if x else "no"
    for name in summary_rows(document):
        cells = {}
        for rule, candidates in (("flat", flat), ("weighted", weighted)):
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
    return "\n".join(lines) + "\n"


def summary_command(args) -> int:
    document = declared_document()
    judged = {rule: json.loads(Path(path).read_text())["candidates"] for rule, path in (("flat", args.flat), ("weighted", args.weighted))}
    text = summary_table(document, judged["flat"], judged["weighted"])
    args.output.write_text(text, encoding="utf-8")
    print(text)
    return 0


def refits_command(args) -> int:
    """Each refit's training pairs and calibrated fits, by horizon and component, from the `run` outputs."""

    out: Dict[str, dict] = {}
    for path in args.inputs:
        doc = json.loads(Path(path).read_text())
        out[str(doc["horizon"])] = {
            "refits": doc["refits"],
            "scored_days": doc["risk_date_check"]["scored_days"],
            "risk_dates": doc["risk_date_check"]["risk_dates"],
        }
    args.output.write_text(json.dumps(out, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(args.output), "horizons": sorted(out)}))
    return 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("declare", help="write the declaration and the judge's candidate files (once, before any score)")
    run = sub.add_parser("run", help="fit the component and combine it with the passers at one horizon")
    run.add_argument("--panel", type=Path, required=True)
    run.add_argument("--published", type=Path, required=True)
    run.add_argument("--horizon", type=int, required=True)
    run.add_argument("--parents", type=Path, required=True, help="announcement_dating_rescore.py --arm both output at this horizon")
    run.add_argument("--output", type=Path, required=True)
    compare = sub.add_parser("compare", help="the judge's tiers, readings, years, scores and pairings")
    compare.add_argument("--panel", type=Path, required=True)
    for name in ("bench", "risk", "reference", "parents", "rows"):
        compare.add_argument(f"--{name}", required=True, help="a template with {h}")
    compare.add_argument("--output", type=Path, required=True)
    compare.add_argument("--markdown", type=Path)
    summary = sub.add_parser("summary", help="the judge's tier 1 row for every row, under both rules")
    summary.add_argument("--flat", type=Path, required=True, help="the judge's report under --rule unweighted")
    summary.add_argument("--weighted", type=Path, required=True, help="the judge's report under --rule weighted")
    summary.add_argument("--output", type=Path, required=True)
    refits = sub.add_parser("refits", help="the refits of each component, from the run outputs")
    refits.add_argument("--output", type=Path, required=True)
    refits.add_argument("inputs", nargs="+", type=Path)
    args = parser.parse_args(argv)
    handlers = {"declare": declare_command, "run": run_command, "compare": compare_command, "summary": summary_command, "refits": refits_command}
    return handlers[args.command](args)


if __name__ == "__main__":
    raise SystemExit(main())
