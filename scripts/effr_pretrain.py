"""Pre-train on the 2008-2018 EFFR - IOER history, fine-tune on the SOFR era, and re-score (#544, a track of #374).

A scratch measurement, not a record: it writes JSON to the paths it is given and nothing into `docs/runs/`.
The models, the source labels, the source weight, the prior and the combination with the risk-date passer are in
`metadata/effr_pretrain.json`, which this script refuses to read unless it is committed and unchanged, as the
judge's declaration is. The pre-2018 rows are training data only and are never scored. **The fed funds series is
the unsecured market and SOFR is secured Treasury repo: only the pattern transfers** (`src/repo_model/effr_history.py`).
No rule, threshold, onset definition or availability time changes: the judge's cut-off rule chooses each model's
cut-offs from its own training window, as for every candidate.

    PYTHONPATH=src python3 scripts/effr_pretrain.py declare --panel PUBLISHED.csv     # once, before any score
    PYTHONPATH=src python3 scripts/effr_pretrain.py run --panel PUBLISHED.csv --horizon H --output OUT/effr_hH.json
    PYTHONPATH=src python3 scripts/effr_pretrain.py combine --panel PUBLISHED.csv --risk OUT/risk_hH.json \\
        --transfer OUT/effr_hH.json --output OUT/comb_hH.json
    PYTHONPATH=src python3 scripts/pressure_judge.py judge --panel PUBLISHED.csv --rule weighted \\
        --output OUT/judge_weighted.json --markdown OUT/judge_weighted.md OUT/bench_h?.json OUT/risk_h?.json OUT/effr_h?.json OUT/comb_h?.json
    PYTHONPATH=src python3 scripts/effr_pretrain.py compare --panel PUBLISHED.csv --output OUT/compare.json \\
        --markdown OUT/compare.md OUT/bench_h?.json OUT/risk_h?.json OUT/effr_h?.json OUT/comb_h?.json

`declare` writes the declaration and the judge's candidate files (`metadata/pressure_judge/candidates/`), with the
source thresholds derived from the history and the published panel by `derive_source_thresholds`; `run` and
`combine` re-derive them and refuse a panel that gives other numbers. `run` fits the SOFR-era control and both
transfer variants (`ml.pressure_transfer_exceedance`) walk-forward at +5 and +10 bp on the shared fold grid, days
before 2026-01-01 only. `combine` puts a transfer model under the risk-date passer as its every-day component by
the rule of #506: on a risk date the passer's forecast, on any other day the component's. `compare` reads the
judge's own cut-offs and puts each model beside its reference, calendar climatology and persistence-logistic.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import math
import sys
from datetime import date, time
from pathlib import Path
from typing import Dict, List, Mapping, Sequence

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))

from repo_model import effr_history, ingest, ml  # noqa: E402
from repo_model.baseline import panel_sha256, rolling_exceedance_backtest  # noqa: E402
from repo_model.data import audit_panel, exceeds_bp, load_daily_panel  # noqa: E402
from repo_model.evaluation_splits import load_split_declaration  # noqa: E402
from repo_model.lockbox import require_unlocked  # noqa: E402

SPLITS = REPO / "metadata" / "evaluation_splits.json"
REGISTRY = REPO / "metadata" / "sources.json"
DECLARATION = REPO / "metadata" / "effr_pretrain.json"
PARENTS = REPO / "metadata" / "risk_date_severity.json"
CANDIDATES = REPO / "metadata" / "pressure_judge" / "candidates"
EPISODES = REPO / "docs" / "pivot" / "evidence" / "episode-post-mortem" / "episodes.json"
DDP_DIRECTORY = REPO / "tests" / "fixtures" / "snapshots" / ingest.FRB_DDP_SOURCE_ID
FRED_DIRECTORY = REPO / "tests" / "fixtures" / "snapshots" / "funding_inputs" / "fred-macro-latest-vintage"

#: The design every model here reads: pressure model v1's direct design without the Treasury settlement, which
#: the pre-2018 history does not carry (Treasury's auction records in the snapshots begin in 2017).
FEATURES = ("spread_bps", "days_to_month_end", "quarter_end", "tax_date", "reserve_balances", "tga")
CONTROL = "effr_sofr_only"
POOLED = "effr_pooled"
FINE_TUNED = "effr_pretrain_finetune"
TRANSFER_MODELS = (CONTROL, POOLED, FINE_TUNED)
VARIANT_OF = {POOLED: "pooled", FINE_TUNED: "pretrain_finetune"}
RISK_PARENT = "risk_gbm"
COMBINED = {name: f"{RISK_PARENT}+{name}" for name in TRANSFER_MODELS}
#: model -> the model it is paired against
REFERENCE = {
    POOLED: CONTROL,
    FINE_TUNED: CONTROL,
    COMBINED[CONTROL]: RISK_PARENT,
    COMBINED[POOLED]: COMBINED[CONTROL],
    COMBINED[FINE_TUNED]: COMBINED[CONTROL],
}
#: Probabilities are clipped here for the log loss only (the passer forecasts exactly 0 off its risk dates).
LOG_LOSS_CLIP = 1e-6
CALLED_OUT_YEARS = (2018, 2020, 2024)


def _load(name: str):
    spec = importlib.util.spec_from_file_location(f"{name}_script", REPO / "scripts" / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


rds = _load("risk_date_severity")


def derive_source_thresholds(
    source_spreads: Sequence[float], sofr_spreads: Sequence[float], taus: Sequence[float]
) -> Dict[float, float]:
    """The whole-basis-point source threshold for each SOFR threshold, by matched event rate.

    EFFR traded below IOER throughout 2008-12-16 to 2018-04-02, so the SOFR-era threshold has no event in the
    source. For each `tau`: the whole-bp threshold `t` whose share of source rows strictly above it
    (`data.exceeds_bp`, on whole basis points) is closest to the share of `sofr_spreads` strictly above `tau`;
    a tie goes to the higher `t`. Only thresholds below the highest source print are tried. It reads the two spread lists and nothing else.
    """

    if not source_spreads or not sofr_spreads:
        raise ValueError("matching an event rate needs spreads on both sides")
    low = math.floor(min(source_spreads)) - 1
    high = round(max(source_spreads)) - 1  # below the highest print, so the share above is never zero
    out: Dict[float, float] = {}
    for tau in taus:
        target = sum(exceeds_bp(v, float(tau)) for v in sofr_spreads) / len(sofr_spreads)
        best, best_gap = None, None
        for t in range(low, high + 1):
            share = sum(exceeds_bp(v, float(t)) for v in source_spreads) / len(source_spreads)
            gap = round(abs(share - target), 12)
            if best is None or gap < best_gap or gap == best_gap:
                best, best_gap = float(t), gap
        out[float(tau)] = best
    return out


def history_rows():
    return effr_history.load_history_rows(DDP_DIRECTORY, FRED_DIRECTORY)


def derived_thresholds(panel_rows, taus) -> Dict[float, float]:
    """`derive_source_thresholds` on the history and the panel's days before the lockbox."""

    sofr = [row.spread_bps for row in panel_rows if row.date < date(2026, 1, 1)]
    return derive_source_thresholds([row.spread_bps for row in history_rows()], sofr, taus)


def declaration_document(parents: dict, thresholds: Mapping[float, float]) -> dict:
    return {
        "status": (
            "declared by the pull request that closes #544 before any score was computed; nothing here is tuned on a "
            "scored day; the choices below (the design, the source labels, the source weight, the prior, the "
            "combination with the risk-date passer) are the pull request's, listed there for Eleonora's review"
        ),
        "scoring": parents["scoring"],
        "thresholds_bp": parents["thresholds_bp"],
        "horizons": parents["horizons"],
        "design": {
            "features": list(FEATURES),
            "estimator": "a ridge logistic of spread > tau (ml.PRESSURE_LOGISTIC_SETTINGS: L2, C = 1, standardised), one per threshold, the logistic form of risk_logistic, on every day",
            "left_out": "the Treasury settlement columns and every input built after 2018 (the SOFR percentiles, ON RRP, the daily TGA): the pre-2018 history does not carry them, so the two markets share one design",
            "pairs": "the direct pairs of every training day (ml._pressure_pairs); the source's pairs are built by effr_history.history_pairs with the same design, each label paired with what was public at its own decision instant, both under the as-of rule and its independent check",
        },
        "source": {
            "series": "fed funds (EFFR) - IOER, 2008-12-16 to 2018-04-02 (effr_history.HISTORY_START, HISTORY_END)",
            "snapshots": "tests/fixtures/snapshots/frb_ddp and tests/fixtures/snapshots/funding_inputs/fred-macro-latest-vintage (tracked)",
            "role": "training data only; no pre-2018 row is ever scored",
            "caveat": "the fed funds series is the unsecured market and SOFR is secured Treasury repo: only the pattern transfers",
            "thresholds_bp": {f"{tau:g}": value for tau, value in sorted(thresholds.items())},
            "threshold_rule": (
                "for each SOFR threshold the whole-basis-point source threshold whose share of source rows strictly above it "
                "is closest to the share of the published panel's days before 2026-01-01 strictly above the SOFR threshold "
                "(a tie to the higher one; only thresholds below the highest source print are tried): scripts/effr_pretrain.py derive_source_thresholds, re-derived by `run`, which "
                "refuses other numbers. Fed funds traded below IOER throughout, so the +5 bp event does not exist in the source"
            ),
        },
        "variants": {
            POOLED: {
                "variant": "pooled",
                "rule": (
                    "(a) one fit on the SOFR pairs (weight 1) and the source pairs (weight source_weight), with a source indicator "
                    "as the design's last column (0 on every served row); columns standardised on the SOFR pairs alone"
                ),
                "source_weight": ml.PRESSURE_TRANSFER_SOURCE_WEIGHT,
                "why_this_weight": "stated, not tuned: one source row counts a quarter of a SOFR row",
            },
            FINE_TUNED: {
                "variant": "pretrain_finetune",
                "rule": (
                    "(b) a ridge logistic on the source pairs alone; then the SOFR-era refit, walk-forward, whose L2 penalty is centred "
                    "on the pre-trained slopes (converted between the two standardisations through raw units) with the same C = 1 and a "
                    "free intercept. A threshold whose source labels hold one class has no prior (the SOFR-era fit). A refit whose SOFR "
                    "window holds one class is served the pre-trained model: the source thresholds are rate-matched, so its intercept "
                    "is a base rate"
                ),
            },
            CONTROL: {
                "variant": "none",
                "rule": "the parent: the same design and estimator on the SOFR-era pairs alone (ml.pressure_logistic_exceedance), no source rows",
            },
        },
        "combined": {
            "parent": RISK_PARENT,
            "rows": {COMBINED[name]: name for name in TRANSFER_MODELS},
            "rule": (
                "the rule of #506: on a risk date (metadata/risk_date_severity.json) the passer's forecast, unchanged; on any other "
                "day the transfer model's. The hurdle of #539 is not used: its code had not merged. Both transfer variants and the "
                "control are combined, so the row is not chosen on a score"
            ),
        },
        "cutoffs": "the judge's cutoff_rule, from each model's own training window; one cut-off per threshold and horizon",
        "judging": "the judge as declared (metadata/pressure_judge.json): tiers 1, 3 and 5, h = 1 to 5, +5 and +10 bp, under the flat and the weighted rule; the cut-off rule unchanged",
        "log_loss_clip": LOG_LOSS_CLIP,
        "published": "nothing: the models and the source are off in every published declaration",
    }


def candidate_entries(document: dict) -> Dict[str, dict]:
    """The judge's candidate file of each model, keyed by name."""

    base = json.loads((CANDIDATES / f"{RISK_PARENT}.json").read_text(encoding="utf-8"))
    out = {}
    for name in TRANSFER_MODELS:
        spec = document["variants"][name]
        out[name] = {
            "role": "candidate",
            "track": "T (#544)",
            "features": list(FEATURES),
            "features_at_horizon_2_or_more": "unchanged: the design has no settlement column",
            "calibration": f"none: {spec['rule']}; metadata/effr_pretrain.json",
        }
        out[COMBINED[name]] = {
            "role": "candidate",
            "track": "T (#544)",
            "parent": RISK_PARENT,
            "features": list(base["features"]) + [f for f in FEATURES if f not in base["features"]],
            "features_at_horizon_2_or_more": base["features_at_horizon_2_or_more"],
            "calibration": (
                f"none: {RISK_PARENT} on its risk dates, {name} on every other day (the rule of #506); metadata/effr_pretrain.json"
            ),
        }
    return out


def declare_command(args) -> int:
    parents = json.loads(PARENTS.read_text(encoding="utf-8"))
    rows = load_daily_panel(args.panel)
    audit_panel(rows)
    taus = tuple(float(t) for t in parents["thresholds_bp"])
    document = declaration_document(parents, derived_thresholds(rows, taus))
    DECLARATION.write_text(json.dumps(document, indent=2) + "\n", encoding="utf-8")
    entries = candidate_entries(document)
    for name, entry in entries.items():
        (CANDIDATES / f"{name}.json").write_text(json.dumps(entry, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"declaration": str(DECLARATION), "thresholds": document["source"]["thresholds_bp"], "candidates": len(entries)}))
    return 0


def _declared(panel_rows) -> dict:
    declared = rds.committed_declaration(DECLARATION)
    taus = tuple(float(t) for t in declared["thresholds_bp"])
    derived = {f"{tau:g}": value for tau, value in derived_thresholds(panel_rows, taus).items()}
    if derived != declared["source"]["thresholds_bp"]:
        raise SystemExit(
            f"the source thresholds derived from this panel are {derived}, not the declared {declared['source']['thresholds_bp']}"
        )
    return declared


def run_command(args) -> int:
    rows = load_daily_panel(args.panel)
    audit_panel(rows)
    declared = _declared(rows)
    h = args.horizon
    if h not in declared["horizons"]:
        raise SystemExit(f"horizon {h} is not declared")
    last = date.fromisoformat(declared["scoring"]["last_day"])
    require_unlocked([last], where="effr_pretrain")
    splits = load_split_declaration(SPLITS)
    registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
    taus = tuple(float(t) for t in declared["thresholds_bp"])
    minimum = declared["scoring"]["minimum_history"]
    decision = time.fromisoformat(declared["scoring"]["decision_time"])
    thresholds = {float(tau): value for tau, value in declared["source"]["thresholds_bp"].items()}
    history = history_rows()
    rule = effr_history.HistoryRule(registry, decision_time=decision, horizon=h)
    predictors = {CONTROL: ml.pressure_logistic_exceedance(FEATURES, splits, minimum_history=minimum)}
    for name in (POOLED, FINE_TUNED):
        spec = declared["variants"][name]
        options = {"source_weight": spec["source_weight"]} if "source_weight" in spec else {}
        predictors[name] = ml.pressure_transfer_exceedance(
            spec["variant"], FEATURES, splits, (history, rule), thresholds, minimum_history=minimum, **options
        )
    forecasts, settings, coefficients = {}, {}, {}
    for name, predictor in predictors.items():
        report = rolling_exceedance_backtest(
            rows,
            predictor=predictor,
            model_name=name,
            features=FEATURES,
            registry=registry,
            decision_time=decision,
            taus=taus,
            minimum_history=minimum,
            refit_every=declared["scoring"]["refit_every"],
            end=last,
            horizon=h,
        )
        forecasts[name] = rds.column(report)
        settings[name] = {
            "features": list(report.features),
            "model_settings": dict(report.model_settings),
            "ml_libraries": None if report.ml_libraries is None else dict(report.ml_libraries),
        }
        if hasattr(predictor, "coefficients"):
            coefficients[name] = list(predictor.coefficients)
        print(json.dumps({"horizon": h, "model": name, "done": True}), flush=True)
    document = {
        "horizon": h,
        "panel_sha256": panel_sha256(args.panel),
        "declaration": declared,
        "declarations": settings,
        "coefficients": coefficients,
        "forecasts": forecasts,
    }
    args.output.write_text(json.dumps(document, indent=1, sort_keys=True, default=str) + "\n", encoding="utf-8")
    print(json.dumps({"horizon": h, "output": str(args.output)}))
    return 0


def combine_forecasts(passer: Mapping, component: Mapping, risk: Mapping[str, bool]) -> dict:
    """`{tau: {day: p}}`: the passer's forecast on a risk date, the component's on any other day."""

    out = {}
    for tau, column in passer.items():
        if set(column) != set(component[tau]) or set(column) != set(risk):
            raise ValueError("the passer, the component and the risk-date flags must cover the same days")
        out[tau] = {day: (column[day] if risk[day] else component[tau][day]) for day in column}
    return out


def combine_command(args) -> int:
    rows = load_daily_panel(args.panel)
    audit_panel(rows)
    declared = _declared(rows)
    splits = load_split_declaration(SPLITS)
    by_date = {row.date.isoformat(): row for row in rows}
    risk_document = json.loads(args.risk.read_text())
    transfer = json.loads(args.transfer.read_text())
    digest = panel_sha256(args.panel)
    h = transfer["horizon"]
    for document in (risk_document, transfer):
        if document["panel_sha256"] != digest:
            raise SystemExit("an input was scored on another panel")
    if risk_document["horizon"] != h:
        raise SystemExit("the passer and the transfer models are at different horizons")
    passer = risk_document["forecasts"][RISK_PARENT]
    days = sorted(next(iter(passer.values())))
    risk = {day: rds.is_risk_date(splits, by_date[day].values, h) for day in days}
    forecasts = {
        COMBINED[name]: combine_forecasts(passer, transfer["forecasts"][name], risk) for name in TRANSFER_MODELS
    }
    document = {
        "horizon": h,
        "panel_sha256": digest,
        "declaration": declared,
        "risk_dates": sum(risk.values()),
        "forecasts": forecasts,
    }
    args.output.write_text(json.dumps(document, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"horizon": h, "output": str(args.output), "risk_dates": document["risk_dates"], "days": len(days)}))
    return 0


def log_loss(p: float, y: int) -> float:
    q = min(1.0 - LOG_LOSS_CLIP, max(LOG_LOSS_CLIP, p))
    return -math.log(q if y else 1.0 - q)


def _f(value, places=3):
    return "-" if value is None else f"{value:.{places}f}"


def _interval(cell):
    if cell is None or cell.get("mean") is None:
        return "-"
    if "interval" not in cell:
        return f"{cell['mean']:+.4f} (no interval)"
    low, high = cell["interval"]["lower"], cell["interval"]["upper"]
    return f"{cell['mean']:+.4f} [{low:+.4f}, {high:+.4f}]"


def coefficient_report(document: dict) -> dict:
    """How the pre-trained coefficients differ from the SOFR-era fit: the first and the last refit, per threshold.

    Coefficients are in the units of the SOFR window's standardised columns (one unit = one standard deviation of the column
    over that refit's SOFR pairs), so the pre-trained, SOFR-era and fine-tuned columns are comparable.
    """

    out = {}
    for h, entry in document.items():
        trace = entry["coefficients"].get(FINE_TUNED, [])
        pooled_trace = entry["coefficients"].get(POOLED, [])
        out[h] = {"fine_tune": [], "pooled": []}
        for tau in ("5", "10"):
            tuned = [(item["train_end"], item["fits"][tau]) for item in trace if item["fits"].get(tau, {}).get("fine_tuned")]
            if not tuned:
                continue
            columns = [c for c in tuned[0][1]["sofr_era"]]
            gaps = [
                sum(abs(fit["pretrained"][c] - fit["sofr_era"][c]) for c in columns if c != "intercept") / (len(columns) - 1)
                for _day, fit in tuned
            ]
            shifts = [
                sum(abs(fit["fine_tuned"][c] - fit["sofr_era"][c]) for c in columns if c != "intercept") / (len(columns) - 1)
                for _day, fit in tuned
            ]
            out[h]["fine_tune"].append(
                {
                    "tau": tau,
                    "refits": len(tuned),
                    "first": {"train_end": tuned[0][0], **tuned[0][1]},
                    "last": {"train_end": tuned[-1][0], **tuned[-1][1]},
                    "mean_abs_slope_gap_pretrained_vs_sofr_era": sum(gaps) / len(gaps),
                    "mean_abs_slope_shift_fine_tuned_vs_sofr_era": sum(shifts) / len(shifts),
                }
            )
        for tau in ("5", "10"):
            joint = [(item["train_end"], item["fits"][tau]) for item in pooled_trace if tau in item["fits"] and item["fits"][tau].get("sofr_era")]
            if joint:
                out[h]["pooled"].append({"tau": tau, "refits": len(joint), "last": {"train_end": joint[-1][0], **joint[-1][1]}})
    return out


def compare_command(args) -> int:
    """Each model beside its reference, climatology and persistence-logistic, under the judge's own cut-offs."""

    from repo_model import pressure_judge as pj

    pj_script = _load("pressure_judge")
    rows = load_daily_panel(args.panel)
    audit_panel(rows)
    declared = _declared(rows)
    declaration = pj.load_declaration()
    splits = load_split_declaration(SPLITS)
    by_date = {row.date: row for row in rows}
    digest = panel_sha256(args.panel)
    forecasts, documents = [], {}
    for path in args.inputs:
        document = json.loads(Path(path).read_text())
        if document["panel_sha256"] != digest:
            raise SystemExit(f"{path} was scored on another panel ({document['panel_sha256'][:8]})")
        if "coefficients" in document:
            documents[str(document["horizon"])] = document
        forecasts.extend(pj.forecasts_from_horizon_document(document))
    states = {h: pj_script._scarcity_states(h, declaration.last_day) for h in declaration.horizons}

    def grids_of(items):
        out = {}
        for h in declaration.horizons:
            reference = next(f for f in items if f.horizon == h and f.name == declaration.climatology)
            out[h] = pj.build_grid(declaration, h, rows, reference.dates, splits, scarcity_state=states[h])
        return out

    calendar = [row.date for row in rows]
    chosen = pj.choose_cutoffs(declaration, grids_of(forecasts), forecasts, calendar)
    grids = grids_of(chosen)
    tau = declaration.primary
    by_name: Dict[str, Dict[int, object]] = {}
    for forecast in chosen:
        by_name.setdefault(forecast.name, {})[forecast.horizon] = forecast
    models = list(TRANSFER_MODELS) + list(COMBINED.values())
    for name in models + [RISK_PARENT, declaration.climatology, declaration.persistence]:
        if name not in by_name:
            raise SystemExit(f"no forecasts for {name!r} in the inputs")
    horizons = list(declaration.horizons)
    seed = declaration.document()["bootstrap"]["seed"]

    # -- onsets flagged at some lead 1 to 5 --------------------------------------------------------------
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

    caught_by = {name: caught(name) for name in models + [RISK_PARENT]}
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

    def recall_against(name, reference):
        cells = {
            label: [
                [m * o for m, o in zip(inside, onset)],
                [m * c for m, c in zip(inside, caught_by[name])],
                [m * c for m, c in zip(inside, caught_by[reference])],
            ]
            for label, inside in cells_for.items()
        }
        return pj._bootstrap(declaration, cells, recall_stats, count, seed=pj._seed(seed, "recall", name, reference))

    recall = {name: {"vs_reference": recall_against(name, REFERENCE.get(name, RISK_PARENT))} for name in models}
    for name in models:
        recall[name]["vs_risk_gbm"] = recall_against(name, RISK_PARENT)
    caught_counts = {
        name: {label: int(sum(m * c for m, c in zip(inside, caught_by[name]))) for label, inside in cells_for.items()}
        for name in models + [RISK_PARENT]
    }
    onsets_in = {label: int(sum(m * o for m, o in zip(inside, onset))) for label, inside in cells_for.items()}

    # -- flags and false alarms at the primary threshold, on and off the risk dates -------------------------------
    flags = {}
    for name in models + [RISK_PARENT]:
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
                    "false_alarms": sum(1 for k in flagged if not outcomes[k]),
                    "onsets_flagged": sum(1 for k in flagged if onsets[k]),
                }
            cell["false_alarms_per_onset"] = cell["all_days"]["false_alarms"] / n_onsets if n_onsets else None
            flags[name][str(h)] = cell

    # -- Brier score and log loss at the primary threshold, paired --------------------------------------------------
    scores = {}
    for name in models:
        scores[name] = {}
        reference = REFERENCE.get(name, RISK_PARENT)
        for h in horizons:
            grid = grids[h]
            outcomes = grid.outcomes[tau]
            n = len(outcomes)
            groups = {"all": list(range(n))}
            for dimension in ("regime", "day_type"):
                for label in sorted(set(grid.groups[dimension])):
                    groups[f"{dimension} {label}"] = [k for k, x in enumerate(grid.groups[dimension]) if x == label]
            p = by_name[name][h].probabilities[tau]
            references = {
                "vs_reference": by_name[reference][h].probabilities[tau],
                "vs_risk_gbm": by_name[RISK_PARENT][h].probabilities[tau],
                "vs_climatology": by_name[declaration.climatology][h].probabilities[tau],
                "vs_persistence_logistic": by_name[declaration.persistence][h].probabilities[tau],
            }
            keys = list(references)
            for kind, loss in (
                ("brier", lambda q, y: (q - y) ** 2),
                ("log_loss", log_loss),
            ):
                cells = {}
                for label, members in groups.items():
                    inside = [0.0] * n
                    for k in members:
                        inside[k] = 1.0
                    cells[label] = [inside] + [
                        [inside[i] * (loss(references[key][i], outcomes[i]) - loss(p[i], outcomes[i])) for i in range(n)]
                        for key in keys
                    ]
                stats = {key: pj._ratio(1 + position, 0) for position, key in enumerate(keys)}
                result = pj._bootstrap(declaration, cells, stats, n, seed=pj._seed(seed, kind, name, h))
                scores[name].setdefault(str(h), {})[kind] = {
                    label: {"days": result[label]["days"], **{key: result[label][key] for key in keys}} for label in groups
                }

    # -- the post-mortem's episodes -------------------------------------------------------------------------------
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
                **{name: bool(caught_by[name][i]) for name in [RISK_PARENT] + models},
            }
        )
    document = {
        "declaration": declared,
        "onsets": int(sum(onset)),
        "onsets_in": onsets_in,
        "caught_at_some_lead": caught_counts,
        "recall_at_some_lead": recall,
        "flags": flags,
        "scores": scores,
        "episodes": episodes,
        "coefficients": coefficient_report(documents),
    }
    args.output.write_text(json.dumps(document, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    text = markdown(document, models)
    if args.markdown:
        args.markdown.write_text(text + "\n", encoding="utf-8")
    print(text)
    return 0


def markdown(document: dict, models: List[str]) -> str:
    out = []
    cells = list(document["onsets_in"])
    out.append(
        "Table 1. +5 bp onsets flagged at some lead 1 to 5, by cell: the passer, then each model with its recall difference "
        "against its reference (90% interval). Cells for the years 2018, 2020 and 2024 are marked.\n"
    )
    out.append("| cell | onsets | risk_gbm | " + " | ".join(f"{m} | diff vs {REFERENCE.get(m, RISK_PARENT)}" for m in models) + " |")
    out.append("|---|---|---|" + "---|---|" * len(models))
    for label in cells:
        mark = f"**{label}**" if label.startswith("year ") and int(label[5:]) in CALLED_OUT_YEARS else label
        row = [mark, str(document["onsets_in"][label]), f"{document['caught_at_some_lead'][RISK_PARENT][label]}"]
        for m in models:
            row.append(str(document["caught_at_some_lead"][m][label]))
            row.append(_interval(document["recall_at_some_lead"][m]["vs_reference"][label]["recall_difference"]))
        out.append("| " + " | ".join(row) + " |")
    out.append("\nTable 1b. The same, each model against risk_gbm (the combined rows are what replace it).\n")
    out.append("| cell | onsets | " + " | ".join(f"{m}" for m in models) + " |")
    out.append("|---|---|" + "---|" * len(models))
    for label in cells:
        if label != "all" and not (label.startswith("year ") and int(label[5:]) in CALLED_OUT_YEARS):
            continue
        out.append(
            f"| {label} | {document['onsets_in'][label]} | "
            + " | ".join(
                f"{document['caught_at_some_lead'][m][label]} ({_interval(document['recall_at_some_lead'][m]['vs_risk_gbm'][label]['recall_difference'])})"
                for m in models
            )
            + " |"
        )
    out.append("\nTable 2. Flags at +5 bp, by horizon: all days / risk dates / other days (flags, of which false alarms); onsets flagged; false alarms per onset.\n")
    out.append("| model | " + " | ".join(f"h = {h}" for h in (1, 2, 3, 4, 5)) + " |")
    out.append("|---|" + "---|" * 5)
    for name in [RISK_PARENT] + models:
        row = []
        for h in ("1", "2", "3", "4", "5"):
            c = document["flags"][name][h]
            a, r, o = c["all_days"], c["risk_dates"], c["other_days"]
            row.append(
                f"{a['flags']}({a['false_alarms']}) / {r['flags']}({r['false_alarms']}) / {o['flags']}({o['false_alarms']}); "
                f"{a['onsets_flagged']}/{c['onsets']}; {_f(c['false_alarms_per_onset'], 2)}"
            )
        out.append(f"| {name} | " + " | ".join(row) + " |")
    for kind, title in (("brier", "Brier score"), ("log_loss", "log loss")):
        out.append(f"\nTable 3 ({title}, all days, +5 bp). What the comparison loses to the model (positive favours the model), 90% interval.\n")
        out.append("| model | h | vs reference | vs risk_gbm | vs climatology | vs persistence-logistic |")
        out.append("|---|---|---|---|---|---|")
        for name in models:
            for h in ("1", "2", "3", "4", "5"):
                cell = document["scores"][name][h][kind]["all"]
                out.append(
                    f"| {name} | {h} | {_interval(cell['vs_reference'])} | {_interval(cell['vs_risk_gbm'])} | "
                    f"{_interval(cell['vs_climatology'])} | {_interval(cell['vs_persistence_logistic'])} |"
                )
    out.append("\nTable 4. The 26 episodes of the post-mortem (#474): who warns at some lead 1 to 5.\n")
    out.append("| start | type | regime | missed by all five | " + " | ".join([RISK_PARENT] + models) + " |")
    out.append("|---|---|---|---|" + "---|" * (len(models) + 1))
    for e in document["episodes"]:
        out.append(
            f"| {e['start']} | {e['day_type']} | {e['regime']} | {'yes' if e['missed_by_all_five'] else 'no'} | "
            + " | ".join("yes" if e[name] else "no" for name in [RISK_PARENT] + models)
            + " |"
        )
    out.append("\nTable 5. The pre-trained coefficients against the SOFR-era fit, in the SOFR window's standardised units (first and last refit).\n")
    for h, entry in sorted(document["coefficients"].items()):
        for item in entry["fine_tune"]:
            columns = [c for c in item["last"]["sofr_era"]]
            out.append(f"\nh = {h}, +{item['tau']} bp, {item['refits']} refits; mean absolute slope gap pre-trained vs SOFR-era "
                       f"{item['mean_abs_slope_gap_pretrained_vs_sofr_era']:.3f}, fine-tuned vs SOFR-era {item['mean_abs_slope_shift_fine_tuned_vs_sofr_era']:.3f}\n")
            out.append("| column | " + " | ".join(f"{w} {k}" for w in ("first", "last") for k in ("pre-trained", "SOFR-era", "fine-tuned")) + " |")
            out.append("|---|" + "---|" * 6)
            for c in columns:
                cells_ = []
                for w in ("first", "last"):
                    for k in ("pretrained", "sofr_era", "fine_tuned"):
                        cells_.append(_f(item[w][k][c], 3))
                out.append(f"| {c} | " + " | ".join(cells_) + " |")
    return "\n".join(out)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    commands = parser.add_subparsers(dest="command", required=True)
    declare = commands.add_parser("declare", help="write the declaration and the judge's candidate files")
    declare.add_argument("--panel", type=Path, required=True)
    declare.set_defaults(handler=declare_command)
    run = commands.add_parser("run")
    run.add_argument("--panel", type=Path, required=True)
    run.add_argument("--horizon", type=int, required=True)
    run.add_argument("--output", type=Path, required=True)
    run.set_defaults(handler=run_command)
    combine = commands.add_parser("combine", help="put each model under the risk-date passer")
    combine.add_argument("--panel", type=Path, required=True)
    combine.add_argument("--risk", type=Path, required=True)
    combine.add_argument("--transfer", type=Path, required=True)
    combine.add_argument("--output", type=Path, required=True)
    combine.set_defaults(handler=combine_command)
    compare = commands.add_parser("compare", help="each model beside its reference, climatology and persistence-logistic")
    compare.add_argument("--panel", type=Path, required=True)
    compare.add_argument("--output", type=Path, required=True)
    compare.add_argument("--markdown", type=Path)
    compare.add_argument("inputs", nargs="+", type=Path)
    compare.set_defaults(handler=compare_command)
    args = parser.parse_args(argv)
    return args.handler(args)


if __name__ == "__main__":
    raise SystemExit(main())
