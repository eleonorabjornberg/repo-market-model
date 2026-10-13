"""The upper-bound study (#635, H2 step 3): how much signal is in the data we hold, for the spread and for ordinary-day pressure.

A development measurement, never a claim and never a verdict (scoring protocol v1, `docs/decisions/scoring-protocol.md` §1, §9 "H2"). It writes JSON
and Markdown to the paths it is given and nothing into `docs/runs/`. Every choice, the reading rule included, is in
`metadata/upper_bound_635.json`, which this script refuses to read unless it is committed and unchanged (`risk_date_severity.committed_declaration`);
`declare` writes it from the constants below and was run, and its output committed, before any number was computed. No day after 2025-12-31 and no
day of a locked tier is read (`docs/decisions/lockbox.md`; `require_unlocked`).

    # PUB.csv is the published panel; DERIV.csv is the scratch panel of docs/pivot/derived-features-result.md (Reproduce)
    PYTHONPATH=src python3 scripts/upper_bound_635.py declare --panel DERIV.csv
    git add metadata/upper_bound_635.json && git commit        # a declaration is made before any score
    PYTHONPATH=src python3 scripts/upper_bound_635.py fit --panel DERIV.csv --output OUT/fits.json
    PYTHONPATH=src python3 scripts/upper_bound_635.py score --published PUB.csv --fits OUT/fits.json --output OUT/score.json
    PYTHONPATH=src python3 scripts/upper_bound_635.py report OUT/score.json --output OUT/report.md

* **Inputs.** Every column of the scratch panel that the as-of rule can read (`source_screen.probe`), the five interactions of #631, and the last
  public spread, each read as of the decision instant at lead h (`derived_features_631.read_all`'s reading, with the anchor kept).
* **Targets.** (1) `spread_bps` at the scored day, as a 23-level quantile law (the grid of protocol v1), led 1 to 5 business days. (2) the +5 bp
  indicator (strictly above on whole basis points, `repo_model.data.exceeds_bp`) on ordinary days, the days the risk-date part does not serve.
* **Fits.** Two families on the same inputs: gradient-boosted (quantile regression, and a classifier) and regularised linear with declared pairwise
  interactions (a ridge location-scale law, and an L2 logistic regression). (i) the **ceiling** is fitted on every scored day and scored on the
  same days, with the generous settings; (ii) the **reachable** line is refitted every 21 scored days on the rows public at the block's first
  decision instant, with the project's settings, and scored on the days after.
* **Scores.** The spread: grid CRPS averaged over leads 1 to 5 per decision day (`scoring_protocol`), against B1 (as-of persistence) and B2 (calendar
  climatology) (`protocol_benchmarks`), the paired stationary bootstrap of protocol v1. Ordinary days: AUROC and Brier skill against walk-forward
  (in-sample, for the ceiling) climatology and a persistence-logistic model.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import multiprocessing
import os
import random
import sys
from datetime import date, time
from pathlib import Path
from typing import Dict, List, Mapping, Optional, Sequence, Tuple

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))

DECLARATION = REPO / "metadata" / "upper_bound_635.json"
SPLITS = REPO / "metadata" / "evaluation_splits.json"
SOURCES = REPO / "metadata" / "sources.json"

FIRST_DAY = "2018-06-29"
LAST_DAY = "2025-12-31"
LEADS = (1, 2, 3, 4, 5)
THRESHOLD_BP = 5.0
DECISION_TIME = (16, 0)
MINIMUM_HISTORY = 61
#: the walk-forward: a refit every 21 scored days (the judge's cadence), no forecast before this many training rows
REFIT_EVERY = 21
MINIMUM_TRAIN = 250
SEED = 635
PROTOCOL_DRAWS = 10_000
SPLIT_DRAWS = 2_000
RESAMPLES = 1_000
BLOCK = 10
INTERVAL = 0.90
#: the rule's two lines (the issue's text, #635): an ordinary-day AUROC under this is "barely above" the benchmark
AUROC_LINE = 0.6
#: the inputs the linear fits interact pairwise (all i <= j, squares included): the structural story's own series, declared
#: before any score and not selected on one
KEY_COLUMNS = (
    "spread_asof",
    "sofr_p99_iorb_bps",
    "sofr_p75_iorb_bps",
    "reserve_scarcity_state",
    "satiation_dist_roll",
    "reserve_change_5",
    "tga_change_5d",
    "treasury_settlement",
    "net_settlement",
    "days_to_month_end",
)
SPREAD_ASOF = "spread_asof"
MODELS = ("gbm", "ridge")
FITS = ("reachable", "ceiling")


def _load(name: str):
    spec = importlib.util.spec_from_file_location(f"{name}_script", REPO / "scripts" / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[f"{name}_script"] = module
    spec.loader.exec_module(module)
    return module


d631 = _load("derived_features_631")
d631.LEADS = LEADS  # `add_interactions` reads the module's leads
ss, ann = d631._modules()
rds = _load("risk_date_severity")


# -- the reading rule, the declaration -----------------------------------------------------------------------------

READING_RULE = {
    "source": "the issue's text (#635, Eleonora, 12 October 2026), made operational here before any number; the scoring sections of the issue are superseded by protocol v1 (ruling on #635)",
    "targets": {
        "primary": "the spread in bp, 23-level grid CRPS averaged over leads 1 to 5 per decision day, on ordinary days (the target day is not a risk date)",
        "secondary": "the +5 bp indicator on ordinary days, AUROC averaged over leads 1 to 5",
    },
    "benchmark_for_the_spread": "B1, as-of persistence (protocol v1 section 4); B2, calendar climatology, reported",
    "benchmark_for_the_indicator": "walk-forward climatology (the training rate) and a persistence-logistic model on the last public spread, reported; the line below is the issue's own absolute line",
    "barely_above": {
        "spread": "the skill against B1 on ordinary days has a 90% stationary-bootstrap interval (5th to 95th percentile of the paired skill draws) whose lower end is at or below 0",
        "indicator": "the ordinary-day AUROC, averaged over leads 1 to 5, is under 0.6",
    },
    "clearly_above": "not barely above",
    "which_model": "for each fit, the better of the two model families on the same days, by the point estimate of the quantity above; the choice is among two, on development data, and is reported as such",
    "verdict": {
        "data problem": "the ceiling is barely above the benchmark",
        "model problem": "the ceiling is clearly above the benchmark and the reachable line is barely above it",
        "partly reached": "both are clearly above the benchmark; the gap between the ceiling and the reachable line is reported, with its paired interval",
    },
    "the_verdict_line": "stated for the spread (the primary target) and for the indicator, each under the rule; if they differ, both are stated and the primary target's decides the one-line verdict",
    "effort_rule": "H2 outcome rule (docs/research/hypotheses/H2.md): a data problem sends effort to H3 and H4, a model problem to H5's development steps",
    "not_a_claim": "the ceiling is fitted and scored in-sample, so it is an upper bound and not a forecast; a reachable figure is development evidence and gives no verdict (protocol v1 section 1)",
}


def declaration_document(inputs: Sequence[str], refused: Mapping[str, str], panel_sha: str) -> dict:
    from repo_model import ml

    settings = ml.UPPER_BOUND_SETTINGS
    return {
        "status": "declared by the pull request that closes #635 before any score was computed; a development measurement (H2, step 3), never a claim or a verdict. Nothing is published, no variant joins a published declaration, no day after 2025-12-31 is read",
        "issue": 635,
        "hypothesis": "H2 (docs/research/plan.md): the data we hold carries signal for the spread and for ordinary-day pressure; step 3, the upper bound",
        "ruling": "the scoring sections of #635 are superseded by scoring protocol v1 (docs/decisions/scoring-protocol.md, #640) wherever they differ: the metric (23-level grid CRPS over leads 1 to 5), the benchmarks (B1, B2) and the interval (stationary bootstrap, mean block 10); development days give no verdict",
        "scope": {"first_day": FIRST_DAY, "last_day": LAST_DAY, "minimum_history": MINIMUM_HISTORY, "leads": list(LEADS), "locked_days": "none read (lockbox.md; require_unlocked)"},
        "panel": {
            "built_by": "docs/pivot/derived-features-result.md (Reproduce): the scratch panel DERIV.csv of #631",
            "sha256": panel_sha,
            "columns_refused_by_the_as_of_rule": dict(refused),
        },
        "inputs": {
            "columns": list(inputs),
            "interactions_of_631": {name: list(spec[:2]) for name, spec in d631.INTERACTIONS.items()},
            "last_public_spread": SPREAD_ASOF,
            "reading": "derived_features_631.read_all's: the 'both' arm (announcement-dated settlements, per-release H.4.1) at the decision instant of lead h, each read checked by the as-of rule; a series not public at the lead is a hole, left missing",
            "excluded": "the six nowcast_* columns, which the as-of rule refuses as undeclared; #630's new sources (H3); nothing is chosen from a score",
        },
        "targets": {
            "spread": "spread_bps at the scored day, in bp, first published, as a 23-level quantile law (scoring_protocol.GRID), led 1 to 5 business days",
            "indicator": "1 if the spread is strictly above +5 bp on whole basis points (repo_model.data.exceeds_bp), on ordinary days: the risk-date rule of the model (announcement_dating_rescore.risk_flag with the coupon clause) is false",
        },
        "models": {
            "gbm": {
                "spread": "ml.grid_quantiles_gbm: HistGradientBoostingRegressor(loss='quantile') per level of the 23-level grid, sorted per day",
                "indicator": "ml.gbm_probabilities: HistGradientBoostingClassifier, ordinary days only",
            },
            "ridge": {
                "spread": "ml.ridge_location_scale_quantiles: ridge location and ridge absolute-residual scale on the standardised inputs (training mean imputed, clipped at +-5) and the products i <= j of the key columns; quantiles from the standardised training residuals",
                "indicator": "ml.l2_logistic_probabilities on the same design, ordinary days only",
            },
            "key_columns_interacted": list(KEY_COLUMNS),
            "settings": {fit: {k: (dict(v) if hasattr(v, "items") else v) for k, v in settings[fit].items()} for fit in FITS},
            "shared": {k: settings[k] for k in ("standardise_clip", "scale_floor_share", "scale_ceiling_share", "logistic_max_iter")},
            "tuning": "none: settings are fixed here; the ceiling's are looser (more rounds, more leaves, a weaker penalty) so that it is the more flexible fit",
            "persistence_logistic": "ml.l2_logistic_probabilities on the last public spread alone, c = 1.0, the reachable fit's rule",
            "climatology": "the training rate of the indicator (the in-sample rate for the ceiling)",
        },
        "fits": {
            "ceiling": "(i) fitted on every scored day with a spread, scored on the same days, at the ceiling settings: what any model could at best extract from these inputs; not a claim",
            "reachable": {
                "refit_every_scored_days": REFIT_EVERY,
                "training_rows": "the scored days whose spread row is at or before the last public row (the anchor) of the block's first decision instant; a row after it raises LookAheadError (training_positions)",
                "minimum_training_rows": MINIMUM_TRAIN,
                "reading": "(ii) the same inputs, read at each row's own decision instant, refitted every 21 scored days at the reachable settings; a day with no fit (fewer than the minimum training rows) is not scored for any line",
            },
        },
        "scoring": {
            "spread": {
                "score": "scoring_protocol.grid_crps, averaged over leads 1 to 5 per decision day (day_scores); MAE of the median beside it",
                "benchmarks": "protocol_benchmarks.b1_forecast and b2_forecast on the published panel cut at 2025-12-31",
                "interval": "scoring_protocol.paired_tests: stationary bootstrap, mean block %d, seed %d, %d draws (%d on the split tables); the 90%% interval is the 5th to 95th percentile of the paired skill draws; the protocol's one-sided 95%% lower bound of mean(d) is reported" % (BLOCK, SEED, PROTOCOL_DRAWS, SPLIT_DRAWS),
                "splits": "all days, ordinary days, risk dates; by regime (metadata/evaluation_splits.json) on all and on ordinary days; by reporting day type; by lead; a split is reported, never a pass requirement",
            },
            "indicator": {
                "metrics": "AUROC, and Brier skill against walk-forward climatology and against persistence-logistic, per lead and averaged over leads 1 to 5",
                "interval": "the stationary bootstrap over the ordinary scored days in date order, mean block %d, %d draws, seed %d, one draw shared by every lead and model; the 90%% interval is the 5th to 95th percentile" % (BLOCK, RESAMPLES, SEED),
                "splits": "by regime and by as-of scarcity state (ample | scarce | unknown)",
            },
        },
        "reading_rule": READING_RULE,
        "variant_count": "four fitted families of two kinds (a quantile law and a classifier, each gradient-boosted and regularised linear), each at two settings (ceiling and reachable) and no other; no input list, setting or interaction was changed after a score",
    }


def committed() -> dict:
    return rds.committed_declaration(DECLARATION)


def declare_command(args) -> int:
    from repo_model import measurement_fields
    from repo_model.data import load_daily_panel

    rows = load_daily_panel(args.panel)
    if rows[-1].date > date.fromisoformat(LAST_DAY):
        raise SystemExit(f"the panel runs past {LAST_DAY}")
    columns = [c for c in rows[0].values if c not in ss.NOT_SCREENED]
    with d631.switched():
        readable, refused = ss.probe(measurement_fields.load_registry(), columns, rows)
    refused = {name: reason.split(":")[0] for name, reason in refused.items()}
    inputs = list(readable) + list(d631.INTERACTIONS) + [SPREAD_ASOF]
    missing = [name for name in KEY_COLUMNS if name not in inputs]
    if missing:
        raise SystemExit(f"key columns that are not inputs: {missing}")
    document = declaration_document(inputs, refused, hashlib.sha256(args.panel.read_bytes()).hexdigest())
    DECLARATION.write_text(json.dumps(document, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"declaration": str(DECLARATION), "inputs": len(inputs), "refused": sorted(refused)}))
    return 0


# -- the walk-forward's embargo --------------------------------------------------------------------------------------


def require_public_labels(label_rows: Sequence[int], chosen: Sequence[int], anchor_row: int) -> None:
    """Refuse a training set that holds a label row after the last public row of the decision instant it is fitted for."""

    from repo_model.splits import LookAheadError

    for position in chosen:
        if label_rows[position] > anchor_row:
            raise LookAheadError(
                f"the training row at position {position} labels panel row {label_rows[position]}, after row {anchor_row}, "
                "the last row public at the decision instant"
            )


def training_positions(label_rows: Sequence[int], anchor_row: int) -> List[int]:
    """Positions of the scored days whose label row is at or before `anchor_row`, in order, checked."""

    chosen = [position for position, row in enumerate(label_rows) if row <= anchor_row]
    require_public_labels(label_rows, chosen, anchor_row)
    return chosen


def blocks(count: int, every: int = REFIT_EVERY) -> List[Tuple[int, int]]:
    """Half-open runs of `every` scored positions, the last one short."""

    return [(start, min(start + every, count)) for start in range(0, count, every)]


# -- reading ---------------------------------------------------------------------------------------------------------


def read_inputs(rows, registry, columns):
    """`derived_features_631.read_all`'s reading at leads 1 to 5, with the anchor row of each read kept.

    Returns the scored days' panel indices, `series[lead][column]` (the as-of value, `None` where not public), the last public spread, and
    `anchors[lead]` (the panel index of the latest row public at the decision instant, per scored day).
    """

    from repo_model import h41_release
    from repo_model.asof import InformationSet, fold_grid
    from repo_model.lockbox import require_unlocked
    from repo_model.splits import LookAheadError

    dates = [r.date for r in rows]
    first, last = date.fromisoformat(FIRST_DAY), date.fromisoformat(LAST_DAY)
    scored = [
        i
        for i in fold_grid(dates, registry, decision_time=time(*DECISION_TIME), minimum_history=MINIMUM_HISTORY, horizon=1)
        if first <= dates[i] <= last
    ]
    require_unlocked((dates[i] for i in scored), where="upper_bound_635")
    series: Dict[int, Dict[str, list]] = {}
    anchors: Dict[int, List[int]] = {}
    for lead in LEADS:
        trows, treg = ann.arm_inputs("both", rows, registry, lead)
        values = {c: [] for c in columns}
        values[d631.SPREAD] = []
        anchors[lead] = []
        with h41_release.release_dating():
            rule = ss.InformationRule(treg, tuple(columns), decision_time=time(*DECISION_TIME), horizon=lead)
            wanted = {g.feature: k for k, g in enumerate(rule.groups) if k}
            for index in scored:
                info = rule.information_set(dates, index)
                for c in columns:
                    read = info.reads[wanted[c]]
                    try:
                        rule.check(dates, InformationSet(info.scored_index, info.decision_instant, info.anchor, (read,)))
                    except LookAheadError:
                        values[c].append(None)
                        continue
                    values[c].append(trows[read.row].values.get(c))
                values[d631.SPREAD].append(rows[info.anchor].spread_bps)
                anchors[lead].append(info.anchor)
        series[lead] = values
    return scored, series, anchors


def design_matrices(series, inputs: Sequence[str]) -> Dict[int, List[List[Optional[float]]]]:
    """Per lead, one row per scored day in the declared input order (interactions and the last public spread included)."""

    out = {}
    for lead in LEADS:
        values = dict(series[lead])
        values[SPREAD_ASOF] = values[d631.SPREAD]
        columns = [values[name] for name in inputs]
        out[lead] = [list(row) for row in zip(*columns)]
    return out


# -- fitting ---------------------------------------------------------------------------------------------------------

_STATE: dict = {}


def _positions_with(values: Sequence[Optional[float]], keep: Sequence[int]) -> List[int]:
    return [p for p in keep if values[p] is not None]


def _spread_block(model: str, settings: Mapping, x, y, served, levels, key_index):
    from repo_model import ml

    if model == "gbm":
        return ml.grid_quantiles_gbm(x, y, served, levels, settings["gbm"])
    return ml.ridge_location_scale_quantiles(x, y, served, levels, key_index, settings["ridge_alpha"])


def _indicator_block(settings: Mapping, x, labels, served, key_index, asof_index):
    from repo_model import ml

    out = {
        "gbm": ml.gbm_probabilities(x, labels, served, settings["gbm"]),
        "ridge": ml.l2_logistic_probabilities(x, labels, served, key_index, settings["logistic_c"]),
        "persistence_logistic": ml.l2_logistic_probabilities(
            [[row[asof_index]] for row in x], labels, [[row[asof_index]] for row in served], (), 1.0
        ),
        "climatology": [sum(labels) / len(labels)] * len(served),
    }
    return out


def _fit_task(task):
    """One lead and one block (reachable) or one lead (ceiling): both targets, both families."""

    from repo_model import ml
    from repo_model.scoring_protocol import GRID

    fit, lead, start, stop = task
    state = _STATE
    x_all, y, valid, ordinary, label, rows_of, anchor = (state[k] for k in ("x", "y", "valid", "ordinary", "label", "rows", "anchors"))
    x_lead, anchor_lead = x_all[lead], anchor[lead]
    settings = ml.UPPER_BOUND_SETTINGS[fit]
    key_index = state["key_index"]
    asof_index = state["asof_index"]
    if fit == "ceiling":
        train = [p for p in range(len(y)) if valid[p]]
        serve = list(train)
    else:
        trainable = training_positions(rows_of, anchor_lead[start])
        train = [p for p in trainable if valid[p]]
        serve = [p for p in range(start, stop) if valid[p]]
        if len(train) < MINIMUM_TRAIN or not serve:
            return task, None
    x_train = [x_lead[p] for p in train]
    y_train = [y[p] for p in train]
    x_serve = [x_lead[p] for p in serve]
    result = {"serve": serve, "train_rows": len(train), "spread": {}}
    for model in MODELS:
        result["spread"][model] = _spread_block(model, settings, x_train, y_train, x_serve, GRID, key_index)
    ordinary_train = [p for p in train if ordinary[p]]
    ordinary_serve = [p for p in serve if ordinary[p]]
    result["indicator_serve"] = ordinary_serve
    result["indicator_train_rows"] = len(ordinary_train)
    result["indicator_train_positives"] = sum(label[p] for p in ordinary_train)
    if ordinary_train and ordinary_serve:
        result["indicator"] = _indicator_block(
            settings, [x_lead[p] for p in ordinary_train], [label[p] for p in ordinary_train], [x_lead[p] for p in ordinary_serve], key_index, asof_index
        )
    else:
        result["indicator"] = None
    return task, result


def fit_command(args) -> int:
    from repo_model import dvp_segment, measurement_fields
    from repo_model.data import exceeds_bp, load_daily_panel
    from repo_model.evaluation_splits import load_split_declaration
    from repo_model.lockbox import require_unlocked

    declared = committed()
    rows = load_daily_panel(args.panel)
    if rows[-1].date > date.fromisoformat(LAST_DAY):
        raise SystemExit(f"the panel runs past {LAST_DAY}; the study reads no day in a locked tier")
    require_unlocked([rows[-1].date], where="upper_bound_635")
    dvp_segment.require_ofr_public(rows)
    registry = measurement_fields.load_registry()
    splits = load_split_declaration(SPLITS)
    inputs = declared["inputs"]["columns"]
    read_columns = [n for n in inputs if n not in d631.INTERACTIONS and n != SPREAD_ASOF]
    with d631.switched():
        scored, series, anchors = read_inputs(rows, registry, read_columns)
    d631.add_interactions(series)
    matrices = design_matrices(series, inputs)
    spreads = [rows[i].spread_bps for i in scored]
    valid = [s is not None for s in spreads]
    y = [float(s) if s is not None else None for s in spreads]
    ordinary = [not ann.risk_flag(splits, rows[i].values, True) for i in scored]
    label = [1 if (s is not None and exceeds_bp(s, THRESHOLD_BP)) else 0 for s in spreads]
    _STATE.update(
        x=matrices,
        y=y,
        valid=valid,
        ordinary=ordinary,
        label=label,
        rows=scored,
        anchors=anchors,
        key_index=[inputs.index(name) for name in KEY_COLUMNS],
        asof_index=inputs.index(SPREAD_ASOF),
    )
    tasks = [("ceiling", lead, 0, len(scored)) for lead in LEADS]
    for lead in LEADS:
        tasks += [("reachable", lead, a, b) for a, b in blocks(len(scored))]
    results = []
    with multiprocessing.get_context("fork").Pool(args.workers) as pool:
        for done, (task, result) in enumerate(pool.imap_unordered(_fit_task, tasks, chunksize=1), 1):
            results.append((task, result))
            if done % 25 == 0 or done == len(tasks):
                print(json.dumps({"fitted": done, "of": len(tasks)}), flush=True)
    document = {
        "declaration": declared,
        "panel_sha256": hashlib.sha256(args.panel.read_bytes()).hexdigest(),
        "scored_days": [rows[i].date.isoformat() for i in scored],
        "scored_rows": scored,
        "ordinary": ordinary,
        "label": label,
        "spread": y,
        "state_band": {str(lead): [ss.band(s) for s in series[lead][d631.STATE]] for lead in LEADS},
        "asof_spread": {str(lead): series[lead][d631.SPREAD] for lead in LEADS},
        "tasks": [
            {"fit": t[0], "lead": t[1], "start": t[2], "stop": t[3], "result": r}
            for t, r in sorted(results, key=lambda tr: (tr[0][0], tr[0][1], tr[0][2]))
        ],
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(document, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(args.output), "tasks": len(tasks), "scored_days": len(scored)}))
    return 0


# -- scoring ---------------------------------------------------------------------------------------------------------


def auroc(scores: Sequence[float], labels: Sequence[int], minimum_positive: int = 5) -> Optional[float]:
    """The probability that a pressure day scores above another ordinary day (ties count half); `None` under `minimum_positive` positives."""

    n1 = int(sum(labels))
    n0 = len(labels) - n1
    if n1 < minimum_positive or n0 < 1:
        return None
    ranks = ss.average_ranks(list(scores))
    return (sum(r for r, v in zip(ranks, labels) if v) - n1 * (n1 + 1) / 2.0) / (n1 * n0)


def brier(probabilities: Sequence[float], labels: Sequence[int]) -> Optional[float]:
    if not labels:
        return None
    return sum((p - y) ** 2 for p, y in zip(probabilities, labels)) / len(labels)


def percentile_interval(draws: Sequence[Optional[float]], level: float = INTERVAL) -> Optional[List[float]]:
    from repo_model.metrics import _quantile

    ordered = sorted(d for d in draws if d is not None)
    if len(ordered) < 0.5 * len(draws):
        return None
    tail = (1.0 - level) / 2.0
    return [_quantile(ordered, tail), _quantile(ordered, 1.0 - tail)]


def mean_of(values: Sequence[Optional[float]]) -> Optional[float]:
    kept = [v for v in values if v is not None]
    return sum(kept) / len(kept) if kept else None


def unpack(fits: Mapping) -> dict:
    """The fit tasks as `forecast[fit][model][lead][position]` quantiles and `prob[fit][model][lead][position]` probabilities."""

    forecast = {f: {m: {h: {} for h in LEADS} for m in MODELS} for f in FITS}
    prob = {f: {m: {h: {} for h in LEADS} for m in MODELS + ("persistence_logistic", "climatology")} for f in FITS}
    train_rows: Dict[str, Dict[int, list]] = {f: {h: [] for h in LEADS} for f in FITS}
    for task in fits["tasks"]:
        result = task["result"]
        if result is None:
            continue
        fit, lead = task["fit"], task["lead"]
        train_rows[fit][lead].append((task["start"], result["train_rows"], result["indicator_train_rows"], result["indicator_train_positives"]))
        for model in MODELS:
            for position, quantiles in zip(result["serve"], result["spread"][model]):
                forecast[fit][model][lead][position] = quantiles
        if result["indicator"] is not None:
            for model in prob[fit]:
                for position, p in zip(result["indicator_serve"], result["indicator"][model]):
                    prob[fit][model][lead][position] = p
    return {"forecast": forecast, "prob": prob, "train_rows": train_rows}


def decision_forecasts(per_lead: Mapping[int, Mapping[int, Sequence[float]]], scored_rows: Sequence[int], dates: Sequence[date]) -> Dict[date, Dict[int, Sequence[float]]]:
    """Per decision day the five leads' quantile vectors, for the decision days that have all five (a lead's target row is `lead` rows on)."""

    by_decision: Dict[int, Dict[int, Sequence[float]]] = {}
    for lead in LEADS:
        for position, quantiles in per_lead[lead].items():
            by_decision.setdefault(scored_rows[position] - lead, {})[lead] = quantiles
    return {dates[d]: leads for d, leads in sorted(by_decision.items()) if len(leads) == len(LEADS)}


def paired_cell(test) -> dict:
    return {
        "n": test.n,
        "benchmark_mean": test.benchmark_mean,
        "candidate_mean": test.benchmark_mean - test.mean_difference,
        "mean_difference": test.mean_difference,
        "skill": test.skill,
        "skill_interval_90": percentile_interval(test.skill_draws),
        "mean_difference_interval_90": percentile_interval(test.mean_difference_draws),
        "lower_mean_difference_one_sided_95": test.lower_mean_difference(),
        "p_value": test.p_value,
        "dm_statistic": test.dm_statistic,
        "dm_p_value": test.dm_p_value,
    }


def score_command(args) -> int:
    from repo_model import protocol_benchmarks as pb, scoring_protocol as sp
    from repo_model.data import load_daily_panel
    from repo_model.evaluation_splits import load_split_declaration
    from repo_model.lockbox import require_unlocked

    declared = committed()
    fits = json.loads(args.fits.read_text(encoding="utf-8"))
    if fits["declaration"] != declared:
        raise SystemExit("the fits were made under a different declaration")
    last = date.fromisoformat(LAST_DAY)
    panel = [r for r in load_daily_panel(args.published) if r.date <= last]
    dates = [r.date for r in panel]
    scored_rows = fits["scored_rows"]
    if [dates[i].isoformat() for i in scored_rows] != fits["scored_days"]:
        raise SystemExit("the published panel's days are not the fit panel's")
    require_unlocked([dates[i] for i in scored_rows], where="upper_bound_635")
    splits = load_split_declaration(SPLITS)
    registry = json.loads(SOURCES.read_text(encoding="utf-8"))
    data = unpack(fits)
    spread = fits["spread"]
    ordinary = fits["ordinary"]
    label = fits["label"]
    target_date = [dates[i] for i in scored_rows]
    regimes = [splits.regime(d) for d in target_date]
    daytypes = [splits.reporting_day_type(d, panel[i].values) for d, i in zip(target_date, scored_rows)]
    ordinary_dates = {d for d, o in zip(target_date, ordinary) if o}
    outcome = {d: spread[p] for p, d in enumerate(target_date) if spread[p] is not None}
    document = {"declaration_sha256": hashlib.sha256(DECLARATION.read_bytes()).hexdigest(), "fits_panel_sha256": fits["panel_sha256"]}

    # -- the spread -----------------------------------------------------------------------------------------------
    models = {(f, m): decision_forecasts(data["forecast"][f][m], scored_rows, dates) for f in FITS for m in MODELS}
    walk_days = sorted(set(models[("reachable", "gbm")]) & set(models[("reachable", "ridge")]))
    full_days = sorted(set(models[("ceiling", "gbm")]) & set(models[("ceiling", "ridge")]))
    if not set(walk_days) <= set(full_days):
        raise SystemExit("a walk-forward decision day has no ceiling forecast")
    b1 = pb.forecasts(pb.b1_forecast, panel, full_days, registry=registry, decision_time=time(*DECISION_TIME))
    # B2 is not formed where the year before the decision day holds no day of the target's type (the first decision days of the panel): those
    # decision days are left out of every window, so that every candidate and both benchmarks score the same days
    b2, b2_missing = {}, []
    for day in full_days:
        try:
            b2.update(pb.forecasts(pb.b2_forecast, panel, [day], registry=registry, decision_time=time(*DECISION_TIME), splits=splits))
        except sp.ProtocolError:
            b2_missing.append(day)
    full_days = [d for d in full_days if d in b2]
    walk_days = [d for d in walk_days if d in b2]
    models = {key: {d: v for d, v in forecasts.items() if d in b2} for key, forecasts in models.items()}
    b1 = {d: v for d, v in b1.items() if d in b2}
    document["spread_scope"] = {
        "decision_days_full": len(full_days),
        "decision_days_walk_forward": len(walk_days),
        "first_walk_forward_decision_day": walk_days[0].isoformat(),
        "last_decision_day": full_days[-1].isoformat(),
        "decision_days_without_b2": [d.isoformat() for d in b2_missing],
        "scored_days": len(scored_rows),
        "ordinary_scored_days": int(sum(ordinary)),
        "pressure_days_ordinary": int(sum(l for l, o in zip(label, ordinary) if o)),
        "pressure_days_all": int(sum(label)),
    }
    median_at = sp.GRID.index(0.5)

    def mae(quantiles, observed):
        return abs(quantiles[median_at] - observed)

    def restrict(forecasts, days):
        keep = set(days)
        return {d: v for d, v in forecasts.items() if d in keep}

    def subsets(window: str) -> Dict[str, set]:
        every = set(outcome)
        out = {"all": every, "ordinary": every & ordinary_dates, "risk dates": every - ordinary_dates}
        if window == "walk":
            for label_ in splits.regime_labels:
                members = {d for d, r in zip(target_date, regimes) if r == label_ and d in every}
                out[f"regime: {label_}"] = members
                out[f"regime: {label_}, ordinary"] = members & ordinary_dates
            for kind in sorted(set(daytypes)):
                out[f"day type: {kind}"] = {d for d, k in zip(target_date, daytypes) if k == kind and d in every}
        return out

    candidates = {
        "walk": {
            "B1": restrict(b1, walk_days),
            "B2": restrict(b2, walk_days),
            **{f"{f} {m}": restrict(models[(f, m)], walk_days) for f in FITS for m in MODELS},
        },
        "full": {
            "B1": b1,
            "B2": b2,
            **{f"ceiling {m}": models[("ceiling", m)] for m in MODELS},
        },
    }
    spread_doc: Dict[str, dict] = {}
    for window, forecasts in candidates.items():
        spread_doc[window] = {}
        for name, members in subsets(window).items():
            outcomes = {d: (outcome[d] if d in members else None) for d in outcome}
            for kind, fn in (("crps", sp.grid_crps), ("mae", mae)):
                if kind == "mae" and name not in ("all", "ordinary"):
                    continue
                scores = {}
                for key, fc in forecasts.items():
                    scores[key] = sp.day_scores(fc, outcomes, dates, score=fn)
                days = set.intersection(*(set(v) for v in scores.values()))
                if len(days) < 30:
                    spread_doc[window].setdefault(name, {})[kind] = {"n": len(days), "note": "fewer than 30 decision days"}
                    continue
                scores = {k: {d: v[d] for d in days} for k, v in scores.items()}
                pairs, keys = [], []
                for bench in ("B1", "B2"):
                    for key in scores:
                        if key.startswith(("reachable", "ceiling")):
                            pairs.append((scores[bench], scores[key]))
                            keys.append((bench, key))
                if window == "walk":
                    for m in MODELS:
                        pairs.append((scores[f"reachable {m}"], scores[f"ceiling {m}"]))
                        keys.append((f"reachable {m}", f"ceiling {m}"))
                draws = PROTOCOL_DRAWS if name in ("all", "ordinary") and kind == "crps" else SPLIT_DRAWS
                tests = sp.paired_tests(pairs, seed=SEED, draws=draws)
                cell = {"n": len(days), "draws": draws, "means": {k: sum(v.values()) / len(v) for k, v in scores.items()}, "tests": {}}
                for (bench, key), test in zip(keys, tests):
                    cell["tests"][f"{bench} -> {key}"] = paired_cell(test)
                spread_doc[window].setdefault(name, {})[kind] = cell
        print(json.dumps({"scored": window}), flush=True)
    # by lead, on the walk-forward days: one cell is a (decision day, lead) forecast of one target day
    by_lead: Dict[str, dict] = {}
    for lead in LEADS:
        cells: Dict[str, Dict[date, float]] = {}
        position_of = {d: i for i, d in enumerate(dates)}
        for name, fc in candidates["walk"].items():
            cells[name] = {}
            for d, leads in fc.items():
                target = dates[position_of[d] + lead]
                if target in outcome:
                    cells[name][target] = sp.grid_crps(leads[lead], outcome[target])
        by_lead[str(lead)] = {}
        for subset_name, members in (("all", set(outcome)), ("ordinary", set(outcome) & ordinary_dates)):
            keep = {k: {d: v for d, v in cells[k].items() if d in members} for k in cells}
            days = sorted(set.intersection(*(set(v) for v in keep.values())))
            keep = {k: {d: v[d] for d in days} for k, v in keep.items()}
            pairs, keys = [], []
            for key in keep:
                if key.startswith(("reachable", "ceiling")):
                    pairs.append((keep["B1"], keep[key]))
                    keys.append(key)
            tests = sp.paired_tests(pairs, seed=SEED, draws=SPLIT_DRAWS)
            by_lead[str(lead)][subset_name] = {"n": len(days), "tests": {k: paired_cell(t) for k, t in zip(keys, tests)}}
    document["spread"] = spread_doc
    document["spread_by_lead"] = by_lead

    # -- the +5 bp indicator on ordinary days ------------------------------------------------------------------------
    document["indicator"] = indicator_document(fits, data, ordinary, label, regimes, splits)
    document["reading"] = reading(document)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(document, indent=1, sort_keys=True, default=str) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(args.output), "verdict": document["reading"]["line"]}))
    return 0


INDICATOR_ROWS = ("gbm", "ridge", "persistence_logistic", "climatology")


def indicator_document(fits, data, ordinary, label, regimes, splits) -> dict:
    from repo_model.metrics import stationary_bootstrap_indices

    positions = [p for p, o in enumerate(ordinary) if o and fits["spread"][p] is not None]
    n = len(positions)
    index_of = {p: k for k, p in enumerate(positions)}
    y = [label[p] for p in positions]
    state = {h: [fits["state_band"][str(h)][p] for p in positions] for h in LEADS}
    regime = [regimes[p] for p in positions]
    prob = data["prob"]
    # availability: the walk-forward window is the reachable line's served ordinary days per lead
    window_positions = {
        ("reachable", "walk"): {h: set(prob["reachable"]["gbm"][h]) for h in LEADS},
        ("ceiling", "walk"): {h: set(prob["reachable"]["gbm"][h]) for h in LEADS},
        ("ceiling", "full"): {h: set(prob["ceiling"]["gbm"][h]) for h in LEADS},
    }
    rng = random.Random(SEED)
    draws = [stationary_bootstrap_indices(n, BLOCK, rng) for _ in range(RESAMPLES)]

    def masks() -> Dict[str, Dict[int, List[bool]]]:
        every = {h: [True] * n for h in LEADS}
        out = {"ordinary, pooled": every}
        for label_ in splits.regime_labels:
            out[f"regime: {label_}"] = {h: [r == label_ for r in regime] for h in LEADS}
        for band in ss.BANDS:
            out[f"state: {band}"] = {h: [s == band for s in state[h]] for h in LEADS}
        return out

    mask_sets = masks()

    def lead_arrays(fit, window, lead, row, idx, mask):
        source = prob[fit][row][lead]
        allowed = window_positions[(fit, window)][lead]
        keep = [k for k in idx if mask[k] and positions[k] in allowed and positions[k] in source]
        return [source[positions[k]] for k in keep], [y[k] for k in keep]

    def metrics_for(fit, window, row, idx, mask_by_lead):
        aurocs, briers = {}, {}
        for lead in LEADS:
            p, labels_ = lead_arrays(fit, window, lead, row, idx, mask_by_lead[lead])
            aurocs[lead] = auroc(p, labels_) if row != "climatology" else None
            briers[lead] = brier(p, labels_)
        return aurocs, briers

    out: Dict[str, dict] = {"ordinary_days": n, "positives": int(sum(y)), "rows": list(INDICATOR_ROWS), "cells": {}}
    identity = list(range(n))
    for (fit, window) in window_positions:
        for split_name, mask_by_lead in mask_sets.items():
            if window == "full" and split_name != "ordinary, pooled":
                continue
            point = {row: metrics_for(fit, window, row, identity, mask_by_lead) for row in INDICATOR_ROWS}
            sample = {row: [] for row in INDICATOR_ROWS}
            use = RESAMPLES if split_name == "ordinary, pooled" else RESAMPLES // 2
            for idx in draws[:use]:
                for row in INDICATOR_ROWS:
                    sample[row].append(metrics_for(fit, window, row, idx, mask_by_lead))
            cell: Dict[str, dict] = {}
            for row in INDICATOR_ROWS:
                aur_by_lead = {h: point[row][0][h] for h in LEADS}
                avg_auc = mean_of(list(aur_by_lead.values())) if row != "climatology" else None
                auc_draws = [mean_of(list(s[0].values())) for s in sample[row]] if row != "climatology" else []
                brier_by_lead = {h: point[row][1][h] for h in LEADS}
                cell[row] = {
                    "auroc_by_lead": {str(h): v for h, v in aur_by_lead.items()},
                    "auroc": avg_auc,
                    "auroc_interval_90": percentile_interval(auc_draws) if auc_draws else None,
                    "brier": mean_of(list(brier_by_lead.values())),
                    "brier_by_lead": {str(h): v for h, v in brier_by_lead.items()},
                }
            for row in ("gbm", "ridge", "persistence_logistic"):
                for ref in ("climatology", "persistence_logistic"):
                    if row == ref:
                        continue
                    skills = []
                    for s_row, s_ref in zip(sample[row], sample[ref]):
                        lead_skill = [1.0 - s_row[1][h] / s_ref[1][h] for h in LEADS if s_row[1][h] is not None and s_ref[1][h]]
                        skills.append(sum(lead_skill) / len(lead_skill) if lead_skill else None)
                    lead_point = [1.0 - point[row][1][h] / point[ref][1][h] for h in LEADS if point[row][1][h] is not None and point[ref][1][h]]
                    cell[row][f"brier_skill_vs_{ref}"] = {
                        "value": sum(lead_point) / len(lead_point) if lead_point else None,
                        "interval_90": percentile_interval(skills),
                    }
                if row != "persistence_logistic":
                    diffs = []
                    for s_row, s_ref in zip(sample[row], sample["persistence_logistic"]):
                        a, b = mean_of(list(s_row[0].values())), mean_of(list(s_ref[0].values()))
                        diffs.append(None if a is None or b is None else a - b)
                    base = cell["persistence_logistic"]["auroc"]
                    cell[row]["auroc_minus_persistence_logistic"] = {
                        "value": None if base is None or cell[row]["auroc"] is None else cell[row]["auroc"] - base,
                        "interval_90": percentile_interval(diffs),
                    }
            cell["n_by_lead"] = {
                str(h): len([k for k in identity if mask_by_lead[h][k] and positions[k] in window_positions[(fit, window)][h] and positions[k] in prob[fit]["gbm"][h]])
                for h in LEADS
            }
            cell["positives_by_lead"] = {
                str(h): sum(y[k] for k in identity if mask_by_lead[h][k] and positions[k] in window_positions[(fit, window)][h] and positions[k] in prob[fit]["gbm"][h])
                for h in LEADS
            }
            out["cells"][f"{fit} | {window} | {split_name}"] = cell
        print(json.dumps({"indicator": fit, "window": window}), flush=True)
    return out


def reading(document: Mapping) -> dict:
    """The pre-registered reading applied to the numbers (`READING_RULE`); every quantity it uses is in the document."""

    spread = document["spread"]
    walk_ord = spread["walk"]["ordinary"]["crps"]
    full_ord = spread["full"]["ordinary"]["crps"]

    def best(cell, fit):
        rows = {m: cell["tests"][f"B1 -> {fit} {m}"] for m in MODELS}
        model = max(rows, key=lambda m: rows[m]["skill"])
        return model, rows[model]

    out: Dict[str, dict] = {"spread": {}, "indicator": {}}
    for fit, cell in (("ceiling", full_ord), ("reachable", walk_ord)):
        model, row = best(cell, fit)
        low, high = row["skill_interval_90"]
        out["spread"][fit] = {
            "model": model,
            "window": "all in-sample scored days" if fit == "ceiling" else "walk-forward days",
            "skill": row["skill"],
            "interval_90": [low, high],
            "barely_above": bool(low <= 0.0),
            "n": row["n"],
        }
    gap = {}
    for m in MODELS:
        gap[m] = walk_ord["tests"][f"reachable {m} -> ceiling {m}"]
    out["spread"]["gap"] = gap
    cells = document["indicator"]["cells"]
    for fit, window in (("ceiling", "full"), ("reachable", "walk")):
        cell = cells[f"{fit} | {window} | ordinary, pooled"]
        rows = {m: cell[m] for m in ("gbm", "ridge")}
        model = max(rows, key=lambda m: rows[m]["auroc"] if rows[m]["auroc"] is not None else -1.0)
        value = rows[model]["auroc"]
        out["indicator"][fit] = {
            "model": model,
            "window": "all in-sample ordinary days" if fit == "ceiling" else "walk-forward ordinary days",
            "auroc": value,
            "interval_90": rows[model]["auroc_interval_90"],
            "persistence_logistic_auroc": cell["persistence_logistic"]["auroc"],
            "barely_above": bool(value is None or value < AUROC_LINE),
        }

    def verdict(target: Mapping) -> str:
        if target["ceiling"]["barely_above"]:
            return "data problem"
        if target["reachable"]["barely_above"]:
            return "model problem"
        return "partly reached"

    out["spread"]["verdict"] = verdict(out["spread"])
    out["indicator"]["verdict"] = verdict(out["indicator"])
    out["line"] = (
        f"spread: {out['spread']['verdict']}; ordinary-day indicator: {out['indicator']['verdict']}; the primary target (the spread) decides: {out['spread']['verdict']}"
    )
    return out


# -- the report ------------------------------------------------------------------------------------------------------


def _f(value, digits=3, signed=False) -> str:
    if value is None:
        return "n/a"
    return f"{value:+.{digits}f}" if signed else f"{value:.{digits}f}"


def _iv(interval, digits=3) -> str:
    return "n/a" if not interval else f"[{interval[0]:+.{digits}f}, {interval[1]:+.{digits}f}]"


def report_command(args) -> int:
    document = json.loads(args.score.read_text(encoding="utf-8"))
    lines: List[str] = []
    spread = document["spread"]
    scope = document["spread_scope"]
    lines += [
        "# Upper-bound study: tables (#635)",
        "",
        f"Scored days {scope['scored_days']} (2018-06-29 to 2025-12-31), of which ordinary {scope['ordinary_scored_days']}; ordinary pressure days {scope['pressure_days_ordinary']} of {scope['pressure_days_all']}.",
        f"Decision days with all five leads: {scope['decision_days_full']} in the ceiling window, {scope['decision_days_walk_forward']} on the walk-forward days (first {scope['first_walk_forward_decision_day']}).",
        "",
    ]

    def spread_table(title, window, name, kind="crps", benches=("B1", "B2")):
        cell = spread[window].get(name, {}).get(kind)
        if not cell or "tests" not in cell:
            return []
        rows = [f"### {title}", "", f"{cell['n']} decision days, {cell['draws']} draws. Skill = (benchmark mean - candidate mean) / benchmark mean; positive favours the candidate. Interval: 5th to 95th percentile of the paired skill draws.", ""]
        rows += ["| candidate | benchmark | benchmark mean | candidate mean | skill [90%] | lower bound of mean difference (one-sided 95%) | bootstrap p | DM p |", "|---|---|---|---|---|---|---|---|"]
        for key, t in cell["tests"].items():
            bench, cand = key.split(" -> ")
            if bench not in benches and not bench.startswith("reachable"):
                continue
            rows.append(
                f"| {cand} | {bench} | {_f(t['benchmark_mean'])} | {_f(t['candidate_mean'])} | {_f(t['skill'], 3, True)} {_iv(t['skill_interval_90'])} | {_f(t['lower_mean_difference_one_sided_95'], 3, True)} | {_f(t['p_value'])} | {_f(t['dm_p_value'])} |"
            )
        rows.append("")
        return rows

    lines += ["## The spread: grid CRPS averaged over leads 1 to 5", ""]
    lines += spread_table("Walk-forward days, ordinary days (the primary cell)", "walk", "ordinary")
    lines += spread_table("Walk-forward days, all days", "walk", "all")
    lines += spread_table("Walk-forward days, risk dates", "walk", "risk dates")
    lines += spread_table("Ceiling window (all in-sample scored days), ordinary days", "full", "ordinary")
    lines += spread_table("Ceiling window (all in-sample scored days), all days", "full", "all")
    lines += ["## Splits (walk-forward days; grid CRPS, 2000 draws)", ""]
    for name in spread["walk"]:
        if name.startswith(("regime", "day type")):
            lines += spread_table(name, "walk", name, benches=("B1",))
    lines += ["## MAE of the median (bp)", ""]
    lines += spread_table("Walk-forward days, ordinary days", "walk", "ordinary", kind="mae", benches=("B1",))
    lines += spread_table("Walk-forward days, all days", "walk", "all", kind="mae", benches=("B1",))
    lines += ["## By lead (walk-forward days; grid CRPS per decision-day cell, against B1)", ""]
    for lead, blocks_ in document["spread_by_lead"].items():
        for subset, cell in blocks_.items():
            lines.append(f"**Lead {lead}, {subset} days ({cell['n']} cells).** " + "; ".join(f"{k}: {_f(t['skill'], 3, True)} {_iv(t['skill_interval_90'])}" for k, t in cell["tests"].items()))
            lines.append("")
    indicator = document["indicator"]
    lines += [
        "## The +5 bp indicator on ordinary days",
        "",
        f"{indicator['ordinary_days']} ordinary scored days, {indicator['positives']} pressure days. AUROC and Brier skill averaged over leads 1 to 5; 90% stationary-bootstrap intervals.",
        "",
        "| fit, window, split | row | AUROC [90%] | AUROC minus persistence-logistic [90%] | Brier | Brier skill vs climatology [90%] | Brier skill vs persistence-logistic [90%] | ordinary days / pressure days by lead |",
        "|---|---|---|---|---|---|---|---|",
    ]
    for key, cell in indicator["cells"].items():
        if not any(cell["n_by_lead"].values()):
            continue  # a split with no ordinary day in the window (a regime label that holds none)
        for row in INDICATOR_ROWS:
            r = cell[row]
            diff = r.get("auroc_minus_persistence_logistic") or {}
            vs_c = r.get("brier_skill_vs_climatology") or {}
            vs_p = r.get("brier_skill_vs_persistence_logistic") or {}
            counts = " / ".join(f"{cell['n_by_lead'][str(h)]}/{cell['positives_by_lead'][str(h)]}" for h in LEADS) if row == "gbm" else ""
            lines.append(
                f"| {key.replace(' | ', ', ')} | {row} | {_f(r['auroc'])} {_iv(r['auroc_interval_90']).replace('+', '')} | {_f(diff.get('value'), 3, True)} {_iv(diff.get('interval_90'))} | {_f(r['brier'], 4)} | "
                f"{_f(vs_c.get('value'), 3, True)} {_iv(vs_c.get('interval_90'))} | {_f(vs_p.get('value'), 3, True)} {_iv(vs_p.get('interval_90'))} | {counts} |"
            )
    reading_ = document["reading"]
    lines += ["", "## The reading", ""]
    for target in ("spread", "indicator"):
        for fit in ("ceiling", "reachable"):
            r = reading_[target][fit]
            if target == "spread":
                lines.append(f"* {target}, {fit} ({r['window']}, {r['model']}): skill against B1 {_f(r['skill'], 3, True)} {_iv(r['interval_90'])}; barely above: {'yes' if r['barely_above'] else 'no'}.")
            else:
                lines.append(f"* {target}, {fit} ({r['window']}, {r['model']}): AUROC {_f(r['auroc'])} {_iv(r['interval_90']).replace('+', '')} (persistence-logistic {_f(r['persistence_logistic_auroc'])}); barely above: {'yes' if r['barely_above'] else 'no'}.")
        lines.append(f"* {target} verdict: **{reading_[target]['verdict']}**.")
    lines += ["", f"**{reading_['line']}**", ""]
    args.output.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(args.output)}))
    return 0


# -- main ------------------------------------------------------------------------------------------------------------


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = parser.add_subparsers(dest="command", required=True)
    p = sub.add_parser("declare")
    p.add_argument("--panel", type=Path, required=True)
    p.set_defaults(func=declare_command)
    p = sub.add_parser("fit")
    p.add_argument("--panel", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True)
    p.add_argument("--workers", type=int, default=min(4, os.cpu_count() or 1))
    p.set_defaults(func=fit_command)
    p = sub.add_parser("score")
    p.add_argument("--published", type=Path, required=True)
    p.add_argument("--fits", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True)
    p.set_defaults(func=score_command)
    p = sub.add_parser("report")
    p.add_argument("score", type=Path)
    p.add_argument("--output", type=Path, required=True)
    p.set_defaults(func=report_command)
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
