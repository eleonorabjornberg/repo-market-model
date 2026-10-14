"""Derived features, interactions and lagged pressure from data we hold, screened on ordinary days; one model test (#631).

An exploratory measurement, not a record: nothing is selected, nothing is published, no day after 2026-09-03 (`repo_model.exploration.EXPLORATORY_END`, #684) and no day of a locked tier
is read (`docs/decisions/lockbox.md`; `require_unlocked`). Everything is declared in `metadata/derived_features_631.json`, which this
script refuses to read unless it is committed and unchanged (`risk_date_severity.committed_declaration`); `declare` writes it from the
constants below and was run, and its output committed, before any number was computed.

    PYTHONPATH=src python3 scripts/derived_features_631.py declare
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from pathlib import Path
from typing import Dict, List

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))

from repo_model.exploration import EXPLORATORY_END, NEAR_BLIND_START, panel_end  # noqa: E402

DECLARATION = REPO / "metadata" / "derived_features_631.json"
CANDIDATES = REPO / "metadata" / "pressure_judge" / "candidates"

FIRST_DAY = "2018-06-29"
LAST_DAY = EXPLORATORY_END.isoformat()
#: The model test (`model`, `compare`, `ordinary`) scores through the pressure judge, whose declaration ends 2025-12-31 (#684: not extended here).
MODEL_TEST_LAST_DAY = "2025-12-31"
LEADS = (1, 2, 3, 5, 10)
THRESHOLD_BP = 5.0
#: rates whose own trailing range is read (panel column -> what it is)
RATES = {
    "sofr": "SOFR",
    "sofr_p1": "SOFR 1st percentile",
    "sofr_p25": "SOFR 25th percentile",
    "sofr_p75": "SOFR 75th percentile",
    "sofr_p99": "SOFR 99th percentile",
    "bgcr": "BGCR",
    "tgcr": "TGCR",
    "effr": "EFFR",
    "ofr_tri_rate": "tri-party repo rate (OFR)",
    "ofr_gcf_rate": "GCF repo rate (OFR)",
}
WINDOWS = (20, 60)
VOL_DAYS = (5, 20)
MEDIAN_WINDOW, MEDIAN_MINIMUM = 250, 60
PRESSURE_LAGS = (1, 2, 5)
CALENDAR = ("dow", "bday_of_month", "maint_period_day")
#: the four interactions: name -> (first factor, second factor, what it is)
INTERACTIONS = {
    "tail_x_scarcity": ("sofr_p99_iorb_bps", "reserve_scarcity_state", "tail spread x scarcity state"),
    "tgachg_x_satdist": ("tga_change_5d", "satiation_dist_roll", "TGA change over 5 market days x rolling satiation distance (reserves per release)"),
    "settle_x_scarcity": ("treasury_settlement", "reserve_scarcity_state", "gross Treasury settlement size x scarcity state"),
    "netsettle_x_scarcity": ("net_settlement", "reserve_scarcity_state", "net Treasury settlement size x scarcity state"),
    "tail_x_reservetrend": ("sofr_p99_iorb_bps", "reserve_change_5", "tail spread x reserve balances' change over 5 market days"),
}
#: the model test's added inputs: the last public pressure indicator and the indicator at lags 1, 2 and 5
MODEL_INPUTS = ("pressure_last", "pressure_lag1", "pressure_lag2", "pressure_lag5")
CONTROL = "risk_gbm+settle+h41+dist_roll"
PARENT = CONTROL + "+every_day"
TEST = PARENT + "+lagpress"


def _load(name: str):
    spec = importlib.util.spec_from_file_location(f"{name}_script", REPO / "scripts" / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[f"{name}_script"] = module
    spec.loader.exec_module(module)
    return module


def declaration_document() -> dict:
    return {
        "status": (
            "declared by the pull request that closes #631 before any number was computed; an exploratory screen and one model test, "
            "not a result. Nothing is selected into a model or published: no rule, threshold, onset definition or availability time changes, "
            "the published declaration, the live record and the pin do not move. The screen reads 2018 to " + LAST_DAY + " (the 2026 days are development days, #684) and the model test is one "
            "declared comparison under the judge in force, so a pass is not a confirmation (ruling on #567)"
        ),
        "issue": 631,
        "companions": "#629 (the sources we already hold, screened the same way); #601, PR #609 (the tail spread, the every-day part); #606; #616",
        "scope": {
            "first_day": FIRST_DAY,
            "last_day": LAST_DAY,
            "days": "the lead-1 fold grid of source_screen.py (asof.fold_grid at horizon 1, minimum history 61), restricted to ORDINARY days",
            "ordinary_day": (
                "a scored day for which announcement_dating_rescore.risk_flag(splits, values, True) is false: its pressure-day type is "
                "ordinary (not a quarter-end window, month-end window or tax date) and it settles no coupon. A function of the calendar and "
                "the auction schedule, known in advance, not of any outcome"
            ),
            "no_hindsight_regime_labels": "regimes are metadata/evaluation_splits.json's date ranges; the scarcity state is read as of each decision instant (ruling on #515)",
            "locked_days": "none read: require_unlocked on the last scored day; the panel is cut at " + LAST_DAY,
        },
        "reading": {
            "rule": "every series is read through asof.InformationRule at the decision instant 16:00, at a lead of L panel days (horizon L), L in LEADS, per field, with both guards",
            "timing": (
                "the 'both' arm of #541 (announcement_dating_rescore.arm_inputs): settlements dated from the auction announcement, H.4.1 weeklies per release "
                "(h41_release.release_dating), the OFR repo rates only from their real-time start (dvp_segment.OFR_REAL_TIME_START, #508, #522). The rolling "
                "satiation distance is built under that release dating, the construction #622 asks for; the columns of #598 read the older weekly lag"
            ),
            "kinds": "a calendar feature is a function of the date and is read on the scored day itself; every other column is read at the latest row public at the decision instant",
        },
        "leads": list(LEADS),
        "features": {
            "volatility": {
                "columns": [f"spread_rv{k}" for k in VOL_DAYS],
                "definition": "the sample standard deviation of the last 5 / 20 one-day changes of the spread (bp); needs 6 / 21 consecutive spreads",
            },
            "run_length": {
                "columns": ["above_median_run"],
                "definition": f"the number of consecutive rows, ending at the latest public row, whose spread is strictly above the median of the last {MEDIAN_WINDOW} spreads taken at that row (needs {MEDIAN_MINIMUM}); 0 if the latest spread is not above it",
            },
            "days_since_pressure": {
                "columns": ["days_since_pressure"],
                "definition": f"panel rows from the latest public row back to the latest row whose spread is strictly above +{THRESHOLD_BP:g} bp on whole basis points (data.exceeds_bp); an outcome counts from its own row, the row on which its spread is public; missing until the first pressure day",
            },
            "calendar": {
                "columns": list(CALENDAR) + ["days_to_month_end"],
                "definition": (
                    "dow: weekday 0-4; bday_of_month: the market day of the month (weekdays not in metadata/market_holidays.json); days_to_month_end: the panel's "
                    "calendar column (calendar days to the month's last day, unchanged); maint_period_day: the calendar day 0-13 of the 14-day Thursday-to-Wednesday "
                    "reserve maintenance period, on the grid anchored at the period that began Thursday 2019-04-25 (Federal Reserve Bank of Philadelphia weekly maintenance calendar). "
                    "Reserve requirements were set to zero from 2020-03-26; the grid is kept as a calendar rhythm of bank reporting and settlement, and the feature is read as that, not as a requirement. "
                    "The anchor is read from a calendar listing, not from a tracked Board table: a marked question in the PR"
                ),
            },
            "rate_ranges": {
                "rates": dict(RATES),
                "windows": list(WINDOWS),
                "columns": [f"{r}_{s}_{w}" for r in RATES for w in WINDOWS for s in ("min_dist", "max_dist", "z")],
                "definition": "for each rate and window w of 20 and 60 rows ending at the latest public row, all present: min_dist = value less the window minimum (bp), max_dist = window maximum less the value (bp), z = (value - window mean) / sample sd (missing for a constant window). SOFR percentiles, BGCR, TGCR, EFFR, tri-party and GCF where held",
            },
        },
        "interactions": {
            name: {"first": a, "second": b, "what": what} for name, (a, b, what) in INTERACTIONS.items()
        },
        "interaction_rule": "the product of the two factors, each read as of the decision instant at its own latest public row (so a leg that lags is read stale, never early); missing if either is; the tail spread is sofr_p99_iorb_bps, the scarcity state is reserve_scarcity_state with each leg at its own latest public row (#586), reserve_change_5 is reserve_balances less its value 5 market days earlier (per release), tga_change_5d is the panel's 5-day TGA change",
        "lagged_pressure": {
            "columns": ["pressure_last"] + [f"pressure_lag{k}" for k in PRESSURE_LAGS] + [f"spread_lag{k}" for k in PRESSURE_LAGS],
            "definition": "pressure_last: 1 if the latest public spread is strictly above +5 bp, else 0; pressure_lagK and spread_lagK: the indicator and the spread K panel rows before the latest public row (the persistence benchmark reads the latest public spread; lag K is K rows before it); screened as inputs",
        },
        "tests_per_feature_and_lead": {
            "target": "the +5 bp pressure indicator of the scored day (whole basis points); also the spread level and the one-day change for Spearman only",
            "spearman": "Spearman rank correlation (average ranks) with the three targets; a cell needs 30 days and, for the indicator, 3 pressure days",
            "auroc": "area under the ROC curve of the series for pressure days against the other ordinary days (0.5 none; above 0.5 a higher series goes with pressure); ties count a half; a cell needs 5 pressure days",
            "interval": "90% from 1000 stationary-bootstrap resamples of the days (metrics.stationary_bootstrap_indices, block length 10, seed 631), pooled cells at every lead; split cells only where the pooled |AUROC - 0.5| at that lead is at least 0.05 (so most split cells carry a point estimate only)",
            "pre_onset": "the series at lead L on the 1 to 5 panel days before each +5 bp onset (pressure.onsets, the judge's definition) that falls on an ordinary day, against every other ordinary scored day; AUC of pre-onset against other, with a 90% interval from 1000 resamples, the onsets resampled as clusters and the other days by stationary bootstrap (block 10)",
            "splits": "pooled; the declared regimes of metadata/evaluation_splits.json; the scarcity state read as of the decision instant at the same lead (0 and 1 ample, 2 and 3 scarce, no reading unknown)",
            "exploratory": "the number of cells computed is counted and reported; nothing is corrected for multiplicity",
        },
        "correlation_matrix": {
            "population": "ordinary scored days, every screened series read at lead 1, plus the source series the features are built from (spread, the rates, reserve balances, TGA, settlement, the tail spread, the scarcity state, the satiation distance)",
            "statistic": "Spearman, pooled, on the days where both are present (at least 100)",
            "clusters": "single-linkage: series joined when |rho| >= 0.8; each connected group is one cluster; the representative is the member with the largest sum of |rho| to the other members (ties by name), chosen without the outcome",
            "outputs": "CSV and JSON of the matrix, the clusters, an SVG heatmap in cluster order, under docs/pivot/evidence/derived-features/; the feature-to-source block is read from the same matrix",
        },
        "ranked_leads": {
            "rule": (
                "a series is a candidate lead if its pooled AUROC interval excludes 0.5 at two or more leads. It is ranked by the number of the following checks it passes, then by its largest |AUROC - 0.5|: "
                "(1) the pooled AUROC interval excludes 0.5 at three or more leads; (2) its direction is the same in every regime that holds 5 pressure days and has a point estimate; "
                "(3) its pre-onset AUC interval excludes 0.5 in the same direction at lead 1; (4) it is not in a cluster with a member that passes more checks (a cluster is listed once, by its representative-or-best). "
                "The noise risk is 'low' if 4 checks pass, 'medium' if 3 or 2, 'high' otherwise; the reason column says which checks pass and fail"
            ),
            "note": "a list for the next declared model test, selected on 2018 to " + LAST_DAY + ": nothing in it is selected into a model",
        },
        "model_test": {
            "question": "does lagged pressure added to the every-day part of risk_gbm+settle+h41+dist_roll improve its forecast of pressure days that are not risk dates?",
            "rows": {
                "control": f"{CONTROL}: the best tier-1 row (metadata/pressure_judge/candidates), unchanged; it forecasts exactly 0 on a day that is not a risk date",
                "parent": f"{PARENT}: the control with the every-day component of #506 (a ridge logistic of spread > tau on spread_bps, sofr_p75_iorb_bps and sofr_p99_iorb_bps, ml.EVERY_DAY_COMPONENT_INPUTS), served on every day that is not a risk date, the forecast of a risk date unchanged. No gate. Read: 'the parent' of the test",
                "test": f"{TEST}: the parent with {', '.join(MODEL_INPUTS)} added to the component's inputs and to nothing else",
            },
            "single_test": f"{TEST} against {PARENT}, the only declared model test; the control is reported beside them for reference and is not a second test",
            "added_inputs": list(MODEL_INPUTS),
            "scoring": {"first_day": FIRST_DAY, "last_day": MODEL_TEST_LAST_DAY, "minimum_history": 61, "refit_every": 21, "decision_time": "16:00", "horizons": [1, 2, 3, 4, 5], "thresholds_bp": [5, 10]},
            "judge": "the judge as in force on main (metadata/pressure_judge.json, unchanged), tiers 1, 3 and 5, under the weighted rule in force and, reported beside it, the flat rule; the cut-off rule unchanged",
            "pairing": "test against parent with 90% stationary-bootstrap intervals (the judge's bootstrap): the paired Brier difference at +5 bp (h = 1 to 5) pooled, by regime and by year; onset recall at some lead 1 to 5 (the judge's comparison); flags and false alarms per onset",
            "ordinary_days": "on the ordinary days of the screen, for each row at h = 1 to 5 and +5 bp: AUROC of the forecast for pressure days (ties half), with a 90% interval; and the reliability slope and intercept, from a logistic regression of the outcome on logit(forecast) (forecasts clipped to [1e-4, 1 - 1e-4]; Newton, 50 iterations), reported where the forecast varies and the days hold 5 pressure days (#616)",
            "published": "nothing; the candidates are declared in metadata/pressure_judge/candidates and left off confirmation.candidates",
        },
        "counts": "the number of series x leads x targets cells, AUROC cells, pre-onset cells and intervals computed is counted by the script and printed in the result page",
        "outputs": {
            "result_page": "docs/pivot/derived-features-result.md",
            "evidence": "docs/pivot/evidence/derived-features/",
        },
    }


def candidate_entries() -> Dict[str, dict]:
    base = json.loads((CANDIDATES / f"{CONTROL}.json").read_text(encoding="utf-8"))
    out = {}
    for name, extra, why in (
        (PARENT, (), "the control plus the every-day component of #506 on spread_bps, sofr_p75_iorb_bps and sofr_p99_iorb_bps"),
        (TEST, MODEL_INPUTS, "the parent with the last public pressure indicator and its lags 1, 2 and 5 added to the every-day component"),
    ):
        entry = dict(base)
        entry["track"] = "#631"
        entry["parent"] = CONTROL if name == PARENT else PARENT
        entry["features"] = list(dict.fromkeys(list(base["features"]) + ["spread_bps", "sofr_p75_iorb_bps", "sofr_p99_iorb_bps"] + list(extra)))
        entry["features_at_horizon_2_or_more"] = base.get("features_at_horizon_2_or_more", "") + "; every-day component inputs as at h = 1 (all public at every lead)"
        entry["calibration"] = f"{why}; on a risk date the control's forecast, on any other day the component's; metadata/derived_features_631.json"
        out[name] = entry
    return out


def declare_command(args) -> int:
    DECLARATION.write_text(json.dumps(declaration_document(), indent=2) + "\n", encoding="utf-8")
    for name, entry in candidate_entries().items():
        (CANDIDATES / f"{name}.json").write_text(json.dumps(entry, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"declaration": str(DECLARATION), "candidates": list(candidate_entries())}))
    return 0


# -- the panel -----------------------------------------------------------------------------------------------

ss = None  # source_screen, loaded on first use
ann = None


def _modules():
    global ss, ann
    if ss is None:
        ss = _load("source_screen")
        ann = _load("announcement_dating_rescore")
    return ss, ann


def spec_for():
    from repo_model import derived_features as dfm

    return dfm.columns_for(
        rates=tuple(RATES),
        windows=WINDOWS,
        median_window=MEDIAN_WINDOW,
        median_minimum=MEDIAN_MINIMUM,
        vol_days=VOL_DAYS,
        lags=PRESSURE_LAGS,
        threshold_bp=THRESHOLD_BP,
        changes={"reserve_change_5": ("reserve_balances", 5)},
    )


def _cell(value):
    return "" if value is None else repr(float(value))


def panel_command(args) -> int:
    """SCREEN.csv plus the satiation distance per release, the calendar columns and the causal derived columns."""

    import csv
    import hashlib
    from datetime import date, time

    from repo_model import derived_features as dfm, h41_release, measurement_fields, satiation as sat
    from repo_model.data import load_daily_panel
    from repo_model.lockbox import require_unlocked

    declared = _committed()
    last = date.fromisoformat(declared["scope"]["last_day"])
    require_unlocked([last], where="derived_features_631")
    _ss, _ann = _modules()
    s598 = _load("satiation_distance_598")
    rows = [r for r in load_daily_panel(args.panel) if r.date <= last]
    if rows[-1].date > last:
        raise SystemExit("the panel runs past the last declared day")
    rolling = s598.rolling_constants()
    kw = dict(q=rolling["quantile"], window=rolling["window_rows"], minimum=rolling["minimum_rows"])
    # the distance per release: the H.4.1 weeklies dated by their print, the construction #622 asks for
    _rows0, registry = _ann.arm_inputs("h41", rows, measurement_fields.load_registry(), 1)
    with s598.switched_on(), h41_release.release_dating():
        rule = _ss.InformationRule(registry, sat.READ_FEATURES, decision_time=time(16, 0), horizon=1)
        with_distance = sat.build_distance_columns(rows, rule, last_day=last, **kw)
        sat.check_distance_no_future(rows, with_distance, rule, last_day=last, indices=range(0, len(with_distance), args.check_every), **kw)
    spec = spec_for()
    built = dfm.build_columns(with_distance, spec)
    step = max(1, len(rows) // 12)
    dfm.check_columns_causal(with_distance, spec, built, indices=range(60, len(rows), step))
    holidays_days = [r.date for r in rows]
    calendar = {
        "dow": [float(d.weekday()) for d in holidays_days],
        "bday_of_month": [dfm.bday_of_month(d) for d in holidays_days],
        "maint_period_day": [dfm.maint_period_day(d) for d in holidays_days],
    }
    with args.panel.open(newline="", encoding="utf-8") as handle:
        base = next(csv.reader(handle))
    extra = [sat.DISTANCE_COLUMN] + list(spec) + list(calendar)
    header = list(dict.fromkeys(base + extra))
    with args.output.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerow(header)
        for i, row in enumerate(with_distance):
            out = []
            for name in header[1:]:
                if name in built:
                    out.append(_cell(built[name][i]))
                elif name in calendar:
                    out.append(_cell(calendar[name][i]))
                else:
                    out.append(_cell(row.values.get(name)))
            writer.writerow([row.date.isoformat()] + out)
    print(json.dumps({"output": str(args.output), "sha256": hashlib.sha256(args.output.read_bytes()).hexdigest(), "rows": len(rows), "derived_columns": len(spec), "calendar_columns": len(calendar)}))
    return 0


def _committed() -> dict:
    rds = _load("risk_date_severity")
    return rds.committed_declaration(DECLARATION)


# -- reading -----------------------------------------------------------------------------------------------

DECISION_TIME = (16, 0)
MINIMUM_HISTORY = 61
MINIMUM_DAYS = 30
MINIMUM_PRESSURE = 3
MINIMUM_AUROC_PRESSURE = 5
RESAMPLES = 1000
BLOCK = 10
SEED = 631
INTERVAL_TRIGGER = 0.05
PRE_ONSET_DAYS = (1, 5)
SPREAD = "spread_bps"
STATE = "reserve_scarcity_state"
#: the source series screened beside the features (they are the sources the features are built from)
SOURCES = (
    "sofr_p99_iorb_bps", "sofr_p75_iorb_bps", "reserve_balances", "tga", "tga_change_5d", "satiation_dist_roll", "treasury_settlement",
    "net_settlement", STATE,
)


def derived_names() -> List[str]:
    return list(spec_for())


def series_names() -> List[str]:
    """Every screened series, in table order: the features, the interactions, then the sources."""

    names = [n for n in derived_names() if n != "reserve_change_5"]
    names += list(CALENDAR) + ["days_to_month_end"] + list(INTERACTIONS)
    names += [SPREAD, "reserve_change_5"] + [r for r in RATES] + list(SOURCES)
    return list(dict.fromkeys(names))


def is_feature(name: str) -> bool:
    return name not in set(RATES) | set(SOURCES) | {SPREAD, "reserve_change_5"}


import contextlib


@contextlib.contextmanager
def switched():
    """The columns of the scratch panels, the distance and the derived columns as declared features, for this run only."""

    from types import MappingProxyType
    from unittest import mock

    from repo_model import asof, contract, satiation as sat

    _ss, _ann = _modules()
    fields = dict(_ss.declared_features())
    fields.update(sat.DISTANCE_COLUMN_FIELDS)
    pairs_of = lambda col: tuple(fields["sofr"] + fields["iorb"]) if col == SPREAD else tuple(fields[col])
    for name, (source, _reader) in spec_for().items():
        fields[name] = tuple(sorted(set(pairs_of(source))))
    calendar = frozenset(CALENDAR)
    with mock.patch.multiple(
        contract,
        FEATURE_FIELDS=MappingProxyType(fields),
        FEATURE_SOURCES=MappingProxyType({c: tuple(sorted({s for s, _f in p})) for c, p in fields.items()}),
        CALENDAR_FEATURES=contract.CALENDAR_FEATURES | calendar,
    ), mock.patch.object(asof, "CALENDAR_FEATURES", contract.CALENDAR_FEATURES | calendar):
        yield


def read_all(rows, registry, columns):
    """Each lead's as-of value of each column on each scored day, under the 'both' arm's timing (see the declaration)."""

    from datetime import date, time

    from repo_model import h41_release
    from repo_model.asof import InformationSet, fold_grid
    from repo_model.lockbox import require_unlocked
    from repo_model.splits import LookAheadError

    _ss, _ann = _modules()
    dates = [r.date for r in rows]
    first, last = date.fromisoformat(FIRST_DAY), date.fromisoformat(LAST_DAY)
    scored = [i for i in fold_grid(dates, registry, decision_time=time(*DECISION_TIME), minimum_history=MINIMUM_HISTORY, horizon=1) if first <= dates[i] <= last]
    require_unlocked((dates[i] for i in scored), where="derived_features_631")
    series: Dict[int, Dict[str, list]] = {}
    not_public: Dict[str, Dict[str, int]] = {}
    kinds: Dict[str, str] = {}
    for lead in LEADS:
        trows, treg = _ann.arm_inputs("both", rows, registry, lead)
        values = {c: [] for c in columns}
        values[SPREAD] = []
        with h41_release.release_dating():
            rule = _ss.InformationRule(treg, tuple(columns), decision_time=time(*DECISION_TIME), horizon=lead)
            wanted = {g.feature: k for k, g in enumerate(rule.groups) if k}
            for g in rule.groups:
                if g.feature in wanted:
                    kinds[g.feature] = g.kind
            for index in scored:
                info = rule.information_set(dates, index)
                for c in columns:
                    read = info.reads[wanted[c]]
                    try:
                        rule.check(dates, InformationSet(info.scored_index, info.decision_instant, info.anchor, (read,)))
                    except LookAheadError:
                        values[c].append(None)
                        not_public.setdefault(c, {}).setdefault(str(lead), 0)
                        not_public[c][str(lead)] += 1
                        continue
                    values[c].append(trows[read.row].values.get(c))
                values[SPREAD].append(rows[info.anchor].spread_bps)
        series[lead] = values
    return [dates[i] for i in scored], series, not_public, kinds


def add_interactions(series):
    for lead in LEADS:
        values = series[lead]
        for name, (a, b, _what) in INTERACTIONS.items():
            values[name] = [None if x is None or y is None else float(x) * float(y) for x, y in zip(values[a], values[b])]


# -- statistics --------------------------------------------------------------------------------------------


def auroc(x, y):
    n1 = int(sum(y))
    n0 = len(y) - n1
    if n1 < MINIMUM_AUROC_PRESSURE or n0 < 1:
        return None
    ranks = _ss_ranks(x)
    r1 = sum(r for r, v in zip(ranks, y) if v)
    return (r1 - n1 * (n1 + 1) / 2.0) / (n1 * n0)


def _ss_ranks(x):
    return _modules()[0].average_ranks(x)


def percentile_interval(draws, level=0.90):
    from repo_model.metrics import _quantile

    ordered = sorted(d for d in draws if d is not None)
    if len(ordered) < 0.5 * RESAMPLES:
        return None
    tail = (1.0 - level) / 2.0
    return [_quantile(ordered, tail), _quantile(ordered, 1.0 - tail)]


def auroc_cell(x, y, rng):
    """AUROC and its 90% stationary-bootstrap interval (`None` interval when the point is not formed or not asked)."""

    value = auroc(x, y)
    if value is None:
        return {"auroc": None, "interval": None}
    from repo_model.metrics import stationary_bootstrap_indices

    draws = []
    n = len(x)
    for _ in range(RESAMPLES):
        idx = stationary_bootstrap_indices(n, BLOCK, rng)
        draws.append(auroc([x[i] for i in idx], [y[i] for i in idx]))
    return {"auroc": value, "interval": percentile_interval(draws)}


def pre_onset_cell(clusters, other, rng, with_interval=True):
    """AUC of the pre-onset values against the others', onsets resampled as clusters, the others by stationary bootstrap."""

    pre = [v for c in clusters for v in c]
    contrast = _modules()[0].pre_onset_contrast(pre, other)
    if contrast is None or len(clusters) < 3:
        return {"contrast": contrast, "interval": None, "onsets": len(clusters)}
    interval = None
    if with_interval:
        from repo_model.metrics import stationary_bootstrap_indices

        draws = []
        for _ in range(RESAMPLES):
            picked = [clusters[rng.randrange(len(clusters))] for _ in clusters]
            flat = [v for c in picked for v in c]
            idx = stationary_bootstrap_indices(len(other), BLOCK, rng)
            if not flat:
                draws.append(None)
                continue
            c = _modules()[0].pre_onset_contrast(flat, [other[i] for i in idx])
            draws.append(None if c is None else c["auc"])
        interval = percentile_interval(draws)
    return {"contrast": contrast, "interval": interval, "onsets": len(clusters)}


# -- run -----------------------------------------------------------------------------------------------------

_STATE: dict = {}


def _cell_task(task):
    name, lead = task
    import random

    st = _STATE
    rng = random.Random(f"{SEED}:{name}:{lead}")
    x_all = st["series"][lead][name]
    out = {}
    for split, idx in st["splits"][lead].items():
        pairs = [(x_all[i], i) for i in idx if x_all[i] is not None]
        n = len(pairs)
        entry = {"n": n}
        xs = [p[0] for p in pairs]
        ys = [st["targets"]["pressure"][p[1]] for p in pairs]
        entry["pressure_days"] = int(sum(ys))
        rho = {}
        for target in ("level", "change", "pressure"):
            yt = [st["targets"][target][p[1]] for p in pairs]
            ok = n >= MINIMUM_DAYS
            if target == "pressure":
                ok = ok and sum(ys) >= MINIMUM_PRESSURE and n - sum(ys) >= 1
            rho[target] = _modules()[0].spearman(xs, yt) if ok else None
        entry["rho"] = rho
        entry["auroc"] = None
        entry["interval"] = None
        value = auroc(xs, ys) if n else None
        entry["auroc"] = value
        if split == "pooled" or (st["pooled_auc"].get((name, lead)) is not None and abs(st["pooled_auc"][(name, lead)] - 0.5) >= INTERVAL_TRIGGER):
            if value is not None:
                entry["interval"] = auroc_cell(xs, ys, rng)["interval"]
        out[split] = entry
    # the pre-onset contrast at this lead
    clusters = []
    for cluster in st["pre_clusters"]:
        values = [x_all[i] for i in cluster if x_all[i] is not None]
        if values:
            clusters.append(values)
    other = [x_all[i] for i in st["other_ordinary"] if x_all[i] is not None]
    pre = pre_onset_cell(clusters, other, rng)
    return name, lead, out, pre


def _pooled_task(task):
    name, lead = task
    st = _STATE
    x = st["series"][lead][name]
    idx = st["splits"][lead]["pooled"]
    pairs = [(x[i], st["targets"]["pressure"][i]) for i in idx if x[i] is not None]
    return (name, lead), auroc([p[0] for p in pairs], [p[1] for p in pairs]) if pairs else None


def run_command(args) -> int:
    import csv
    import multiprocessing
    from datetime import date

    from repo_model import pressure
    from repo_model.data import exceeds_bp, load_daily_panel
    from repo_model.evaluation_splits import load_split_declaration
    from repo_model.lockbox import require_unlocked
    from repo_model import measurement_fields

    declared = _committed()
    _ss, _ann = _modules()
    rows = load_daily_panel(args.panel)
    if rows[-1].date > date.fromisoformat(LAST_DAY):
        raise SystemExit(f"the panel runs past {LAST_DAY}; the screen reads no day in a locked tier")
    from repo_model import dvp_segment

    dvp_segment.require_ofr_public(rows)
    registry = measurement_fields.load_registry()
    splits = load_split_declaration(REPO / "metadata" / "evaluation_splits.json")
    names = series_names()
    read_columns = [n for n in names if n not in INTERACTIONS and n != SPREAD]
    with switched():
        scored, series, not_public, kinds = read_all(rows, registry, read_columns)
    add_interactions(series)
    position = {r.date: i for i, r in enumerate(rows)}
    spreads = [r.spread_bps for r in rows]
    targets = {
        "level": [spreads[position[d]] for d in scored],
        "change": [spreads[position[d]] - spreads[position[d] - 1] for d in scored],
        "pressure": [1.0 if exceeds_bp(spreads[position[d]], THRESHOLD_BP) else 0.0 for d in scored],
    }
    ordinary = [i for i, d in enumerate(scored) if not _ann.risk_flag(splits, rows[position[d]].values, True)]
    ordinary_set = set(ordinary)
    regime_of = [splits.regime(d) for d in scored]
    split_idx: Dict[int, Dict[str, List[int]]] = {}
    for lead in LEADS:
        state = series[lead][STATE]
        band = [_ss.band(s) for s in state]
        sp = {"pooled": ordinary}
        for label in splits.regime_labels:
            idx = [i for i in ordinary if regime_of[i] == label]
            if idx:
                sp[f"regime:{label}"] = idx
        # The 2026 column (#684): the days the opened near-blind tier added, beside the days the earlier page read.
        sp["period:2018-2025"] = [i for i in ordinary if scored[i] < NEAR_BLIND_START]
        sp["period:2026"] = [i for i in ordinary if scored[i] >= NEAR_BLIND_START]
        for b in _ss.BANDS:
            idx = [i for i in ordinary if band[i] == b]
            if idx:
                sp[f"state:{b}"] = idx
        split_idx[lead] = sp
    onset_days = pressure.onsets(rows, THRESHOLD_BP, scored)
    scored_index = {d: i for i, d in enumerate(scored)}
    ordinary_onsets = [d for d in onset_days if scored_index[d] in ordinary_set]
    pre_clusters, pre_set = [], set()
    for d in ordinary_onsets:
        at = position[d]
        cluster = [scored_index[rows[at - b].date] for b in range(PRE_ONSET_DAYS[0], PRE_ONSET_DAYS[1] + 1)
                   if rows[at - b].date in scored_index and scored_index[rows[at - b].date] in ordinary_set]
        pre_clusters.append(cluster)
        pre_set.update(cluster)
    other = [i for i in ordinary if i not in pre_set]
    _STATE.update(series=series, targets=targets, splits=split_idx, pre_clusters=pre_clusters, other_ordinary=other, pooled_auc={})
    tasks = [(n, lead) for n in names for lead in LEADS]
    workers = args.workers
    with multiprocessing.get_context("fork").Pool(workers) as pool:
        for key, value in pool.imap_unordered(_pooled_task, tasks, chunksize=8):
            _STATE["pooled_auc"][key] = value
    # the workers fork after the pooled AUROCs are known, so the trigger can read them
    results: Dict[str, dict] = {n: {"leads": {}, "pre_onset": {}} for n in names}
    with multiprocessing.get_context("fork").Pool(workers) as pool:
        for name, lead, cells, pre in pool.imap_unordered(_cell_task, tasks, chunksize=2):
            results[name]["leads"][str(lead)] = cells
            results[name]["pre_onset"][str(lead)] = pre
    cells_computed = sum(len(c) for r in results.values() for c in r["leads"].values())
    document = {
        "scope": {
            "first_day": scored[0].isoformat(),
            "last_day": scored[-1].isoformat(),
            "scored_days": len(scored),
            "ordinary_days": len(ordinary),
            "pressure_days_ordinary": int(sum(targets["pressure"][i] for i in ordinary)),
            "pressure_days_all": int(sum(targets["pressure"])),
            "onsets_all": len(onset_days),
            "onsets_ordinary": [d.isoformat() for d in ordinary_onsets],
            "pre_onset_days": len(pre_set),
            "leads": list(LEADS),
            "regimes": splits.regime_labels,
            "split_days": {str(lead): {k: len(v) for k, v in split_idx[lead].items()} for lead in LEADS},
            "series_screened": len(names),
            "cells": cells_computed,
            "resamples": RESAMPLES,
            "panel_sha256": __import__("hashlib").sha256(args.panel.read_bytes()).hexdigest(),
            "declaration_issue": declared["issue"],
        },
        "series": results,
        "kinds": kinds,
        "not_public_at_lead": not_public,
    }
    # counts of tests
    document["scope"]["spearman_cells"] = 3 * cells_computed
    document["scope"]["auroc_cells"] = sum(1 for r in results.values() for c in r["leads"].values() for e in c.values() if e["auroc"] is not None)
    document["scope"]["auroc_intervals"] = sum(1 for r in results.values() for c in r["leads"].values() for e in c.values() if e["interval"] is not None)
    document["scope"]["pre_onset_cells"] = sum(1 for r in results.values() for p in r["pre_onset"].values() if p["contrast"] is not None)
    # the correlation matrix at lead 1, ordinary days
    matrix = correlation_matrix(series[1], names, ordinary)
    document["matrix"] = matrix
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(document, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({k: v for k, v in document["scope"].items() if k not in ("onsets_ordinary", "split_days")}, indent=1))
    return 0


def correlation_matrix(values: dict, names: List[str], idx: List[int]) -> dict:
    ss_, _ = _modules()
    n = len(names)
    rho = [[None] * n for _ in range(n)]
    counts = [[0] * n for _ in range(n)]
    for a in range(n):
        xa = values[names[a]]
        for b in range(a, n):
            xb = values[names[b]]
            pairs = [(xa[i], xb[i]) for i in idx if xa[i] is not None and xb[i] is not None]
            counts[a][b] = counts[b][a] = len(pairs)
            if a == b:
                value = 1.0 if len(pairs) >= 2 and len({p[0] for p in pairs}) > 1 else None
            elif len(pairs) >= 100:
                value = ss_.spearman([p[0] for p in pairs], [p[1] for p in pairs])
            else:
                value = None
            rho[a][b] = rho[b][a] = value
    return {"names": names, "rho": rho, "n": counts, "threshold": CLUSTER_THRESHOLD, "clusters": clusters_of(names, rho)}


CLUSTER_THRESHOLD = 0.8


def clusters_of(names: List[str], rho) -> List[dict]:
    n = len(names)
    parent = list(range(n))

    def find(a):
        while parent[a] != a:
            parent[a] = parent[parent[a]]
            a = parent[a]
        return a

    for a in range(n):
        for b in range(a + 1, n):
            if rho[a][b] is not None and abs(rho[a][b]) >= CLUSTER_THRESHOLD:
                parent[find(a)] = find(b)
    groups: Dict[int, List[int]] = {}
    for a in range(n):
        groups.setdefault(find(a), []).append(a)
    out = []
    for members in groups.values():
        if len(members) < 2:
            continue
        centrality = {m: sum(abs(rho[m][o]) for o in members if o != m and rho[m][o] is not None) for m in members}
        rep = sorted(members, key=lambda m: (-centrality[m], names[m]))[0]
        out.append({"members": sorted(names[m] for m in members), "representative": names[rep]})
    out.sort(key=lambda c: (-len(c["members"]), c["representative"]))
    return out


# -- the model test ----------------------------------------------------------------------------------------------


@contextlib.contextmanager
def model_switched():
    """`satiation_distance_598.switched_on()` and the four pressure-indicator columns as declared features."""

    from types import MappingProxyType
    from unittest import mock

    from repo_model import contract

    s598 = _load("satiation_distance_598")
    with s598.switched_on():
        fields = dict(contract.FEATURE_FIELDS)
        pairs = tuple(sorted(set(fields["sofr"]) | set(fields["iorb"])))
        for name in MODEL_INPUTS:
            fields[name] = pairs
        with mock.patch.multiple(
            contract,
            FEATURE_FIELDS=MappingProxyType(fields),
            FEATURE_SOURCES=MappingProxyType({c: tuple(sorted({s for s, _f in p})) for c, p in fields.items()}),
        ):
            yield


def model_rows(path):
    """The satiation panel's rows with the four pressure-indicator columns, each from the spread of its own row."""

    from repo_model import derived_features as dfm
    from repo_model.data import DailyObservation, load_daily_panel

    rows = load_daily_panel(path)
    spec = {k: v for k, v in spec_for().items() if k in MODEL_INPUTS}
    built = dfm.build_columns(rows, spec)
    return [DailyObservation(r.date, {**r.values, **{k: built[k][i] for k in spec}}) for i, r in enumerate(rows)]


def model_command(args) -> int:
    from datetime import date, time

    from repo_model import h41_release, measurement_fields, ml
    from repo_model.baseline import panel_sha256, rolling_exceedance_backtest
    from repo_model.data import audit_panel
    from repo_model.evaluation_splits import load_split_declaration
    from repo_model.lockbox import require_unlocked

    declared = _committed()
    scoring = declared["model_test"]["scoring"]
    h = args.horizon
    if h not in scoring["horizons"]:
        raise SystemExit(f"horizon {h} is not declared")
    last = panel_end(args.end, date.fromisoformat(scoring["last_day"]), where="derived_features_631.model")
    require_unlocked([last], where="derived_features_631")
    _ss, _ann = _modules()
    s598 = _load("satiation_distance_598")
    rds, fa = s598.rds, s598.fa
    rows = model_rows(args.panel)
    audit_panel(rows)
    splits = load_split_declaration(rds.SPLITS)
    timed_rows, timed_registry = _ann.arm_inputs("both", rows, measurement_fields.load_registry(), h)
    parent_features = s598.variant_features(CONTROL, h)
    taus = tuple(float(t) for t in scoring["thresholds_bp"])
    parents = json.loads(rds.DECLARATION.read_text(encoding="utf-8"))
    kind = parents["candidates"]["risk_gbm"]["kind"]
    forecasts, settings = {}, {}
    for name, extra in ((PARENT, ()), (TEST, MODEL_INPUTS)):
        component_inputs = ml.EVERY_DAY_COMPONENT_INPUTS + tuple(extra)
        predictor = ml.pressure_risk_date_variant_exceedance(
            kind, parent_features, splits, scoring["minimum_history"], every_day=True, early_prior=False, component_inputs=component_inputs
        )
        features = tuple(dict.fromkeys(tuple(parent_features) + component_inputs))
        with model_switched(), h41_release.release_dating():
            report = rolling_exceedance_backtest(
                timed_rows, predictor=predictor, model_name=name, features=features, registry=timed_registry,
                decision_time=time.fromisoformat(scoring["decision_time"]), taus=taus, minimum_history=scoring["minimum_history"],
                refit_every=scoring["refit_every"], end=last, horizon=h,
            )
        forecasts[name] = rds.column(report)
        settings[name] = fa._settings(report)
        print(json.dumps({"horizon": h, "row": name, "done": True}), flush=True)
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


def compare_command(args) -> int:
    """`announcement_dating_rescore.py compare` with the test against its parent."""

    _ss, _ann = _modules()
    s598 = _load("satiation_distance_598")
    iorb = _load("iorb_every_day_579")
    _ann.DECLARATION = DECLARATION
    _ann.rows_of_pairs = lambda: [("lagpress", TEST, PARENT), ("every_day", PARENT, CONTROL)]
    _ann.markdown = lambda document, pairs: iorb.markdown(document, pairs)
    return _ann.compare_command(args)


# -- the forecasts on ordinary days --------------------------------------------------------------------------


def logistic_calibration(p, y):
    """Intercept and slope of a logistic regression of the outcome on logit(forecast); `None` when it is not formed."""

    import math

    if len(p) < 30 or sum(y) < MINIMUM_AUROC_PRESSURE or len(set(p)) < 3:
        return None
    z = [math.log(min(max(v, 1e-4), 1 - 1e-4) / (1 - min(max(v, 1e-4), 1 - 1e-4))) for v in p]
    a, b = 0.0, 1.0
    for _ in range(50):
        g0 = g1 = h00 = h01 = h11 = 0.0
        for zi, yi in zip(z, y):
            q = 1.0 / (1.0 + math.exp(-(a + b * zi)))
            w = q * (1 - q)
            g0 += yi - q
            g1 += (yi - q) * zi
            h00 += w
            h01 += w * zi
            h11 += w * zi * zi
        det = h00 * h11 - h01 * h01
        if det <= 1e-12:
            return None
        da = (h11 * g0 - h01 * g1) / det
        db = (-h01 * g0 + h00 * g1) / det
        a, b = a + da, b + db
        if abs(da) + abs(db) < 1e-9:
            break
    else:
        return None
    return {"intercept": a, "slope": b} if abs(a) < 30 and abs(b) < 30 else None


def ordinary_command(args) -> int:
    """For each row, horizon and +5 bp: the forecast's AUROC on the ordinary days, its calibration, and the test less the parent."""

    import random
    from datetime import date

    from repo_model.data import exceeds_bp, load_daily_panel
    from repo_model.evaluation_splits import load_split_declaration
    from repo_model.metrics import stationary_bootstrap_indices

    last = panel_end(args.end, date.fromisoformat(MODEL_TEST_LAST_DAY), where="derived_features_631.ordinary")
    declared = _committed()
    _ss, _ann = _modules()
    rows = load_daily_panel(args.panel)
    splits = load_split_declaration(REPO / "metadata" / "evaluation_splits.json")
    by_date = {r.date: r for r in rows}
    out = {"rows": {}, "paired": {}, "scope": {"threshold_bp": 5, "last_day": last.isoformat()}}
    for h in declared["model_test"]["scoring"]["horizons"]:
        docs = [json.loads(Path(str(p).format(h=h)).read_text(encoding="utf-8")) for p in args.inputs]
        forecasts = {}
        for doc in docs:
            for name, column in doc["forecasts"].items():
                forecasts[name] = column["5"]
        names = [CONTROL, PARENT, TEST]
        days = sorted(set.intersection(*(set(forecasts[n]) for n in names)))
        days = [d for d in days if date.fromisoformat(d) <= last and not _ann.risk_flag(splits, by_date[date.fromisoformat(d)].values, True)]
        y = [1 if exceeds_bp(by_date[date.fromisoformat(d)].spread_bps, THRESHOLD_BP) else 0 for d in days]
        out["scope"][f"h{h}"] = {"ordinary_days": len(days), "pressure_days": sum(y)}
        for name in names:
            p = [float(forecasts[name][d]) for d in days]
            rng = random.Random(f"{SEED}:{name}:{h}")
            cell = auroc_cell(p, y, rng)
            out["rows"].setdefault(name, {})[str(h)] = {
                "days": len(days), "pressure_days": sum(y), "mean_forecast": sum(p) / len(p),
                "realised": sum(y) / len(y), "constant": len(set(p)) == 1, **cell, "calibration": logistic_calibration(p, y),
            }
        p_test = [float(forecasts[TEST][d]) for d in days]
        p_par = [float(forecasts[PARENT][d]) for d in days]
        rng = random.Random(f"{SEED}:paired:{h}")
        point = None
        a1, a0 = auroc(p_test, y), auroc(p_par, y)
        if a1 is not None and a0 is not None:
            point = a1 - a0
            draws = []
            for _ in range(RESAMPLES):
                idx = stationary_bootstrap_indices(len(days), BLOCK, rng)
                yy = [y[i] for i in idx]
                u1, u0 = auroc([p_test[i] for i in idx], yy), auroc([p_par[i] for i in idx], yy)
                draws.append(None if u1 is None or u0 is None else u1 - u0)
            out["paired"][str(h)] = {"auroc_difference": point, "interval": percentile_interval(draws)}
    args.output.write_text(json.dumps(out, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(out["scope"]))
    return 0


# -- the report ----------------------------------------------------------------------------------------------


def _fmt(v, digits=3, signed=False):
    if v is None:
        return "-"
    return f"{v:+.{digits}f}" if signed else f"{v:.{digits}f}"


def _auc(entry):
    if entry is None or entry["auroc"] is None:
        return "-"
    text = f"{entry['auroc']:.3f}"
    if entry["interval"]:
        text += f" [{entry['interval'][0]:.2f}, {entry['interval'][1]:.2f}]"
    return text


def _excludes(entry):
    """+1 if the pooled AUROC interval is above 0.5, -1 if below, 0 otherwise."""

    if entry is None or entry["interval"] is None:
        return 0
    if entry["interval"][0] > 0.5:
        return 1
    if entry["interval"][1] < 0.5:
        return -1
    return 0


def ranked_leads(doc: dict) -> List[dict]:
    """The declared rule (`ranked_leads` in the declaration), applied to the screen."""

    leads = [str(l) for l in LEADS]
    clusters = {m: c for c in doc["matrix"]["clusters"] for m in c["members"]}
    names = [n for n in doc["series"] if n not in set(RATES) | set(SOURCES) | {SPREAD, "reserve_change_5"}]
    scored = []
    for name in names:
        series = doc["series"][name]
        pooled = {l: series["leads"][l]["pooled"] for l in leads}
        marks = {l: _excludes(pooled[l]) for l in leads}
        pos = sum(1 for m in marks.values() if m == 1)
        neg = sum(1 for m in marks.values() if m == -1)
        direction = 1 if pos >= neg else -1
        n_excl = pos if direction == 1 else neg
        if n_excl < 2:
            continue
        best_lead = max(leads, key=lambda l: abs((pooled[l]["auroc"] or 0.5) - 0.5) if marks[l] == direction else -1)
        best = pooled[best_lead]["auroc"]
        c1 = n_excl >= 3
        regimes = [
            e for k, e in series["leads"][best_lead].items()
            if k.startswith("regime:") and e["auroc"] is not None and e["pressure_days"] >= MINIMUM_AUROC_PRESSURE
        ]
        c2 = len(regimes) >= 2 and all((e["auroc"] - 0.5) * direction > 0 for e in regimes)
        pre = series["pre_onset"]["1"]
        pre_mark = 0
        if pre["interval"]:
            pre_mark = 1 if pre["interval"][0] > 0.5 else -1 if pre["interval"][1] < 0.5 else 0
        c3 = pre_mark == direction
        scored.append({
            "name": name, "direction": direction, "best_lead": int(best_lead), "auroc": best, "dev": abs(best - 0.5), "leads_excluding": n_excl,
            "checks": {"three_leads": c1, "regimes_agree": c2, "pre_onset": c3}, "cluster": clusters.get(name, {}).get("representative"),
            "regimes_tested": len(regimes),
        })
    # a cluster is listed once: the member with the most checks, then the largest deviation
    keep = []
    by_cluster: Dict[str, List[dict]] = {}
    for item in scored:
        if item["cluster"]:
            by_cluster.setdefault(item["cluster"], []).append(item)
        else:
            item["checks"]["not_redundant"] = True
            keep.append(item)
    for members in by_cluster.values():
        members.sort(key=lambda i: (-sum(i["checks"].values()), -i["dev"], i["name"]))
        members[0]["checks"]["not_redundant"] = True
        members[0]["also_in_cluster"] = [m["name"] for m in members[1:]]
        keep.append(members[0])
    for item in keep:
        passed = sum(item["checks"].values())
        item["passed"] = passed
        item["noise_risk"] = "low" if passed == 4 else "medium" if passed >= 2 else "high"
    keep.sort(key=lambda i: (-i["passed"], -i["dev"], i["name"]))
    return keep


def heatmap(matrix: dict) -> str:
    names, rho = matrix["names"], matrix["rho"]
    order = []
    for c in matrix["clusters"]:
        order += [m for m in c["members"] if m not in order]
    order += [n for n in names if n not in order]
    pos = {n: i for i, n in enumerate(names)}
    cell, left, top = 7, 190, 20
    n = len(order)
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {left + cell * n + 10} {top + cell * n + 10}" role="img" aria-label="Spearman correlation between the screened series on ordinary days, lead 1, clusters first">',
           "<style>text{font:6px sans-serif;fill:#222}@media (prefers-color-scheme:dark){text{fill:#ddd}}</style>"]
    for i, a in enumerate(order):
        out.append(f'<text x="{left - 3}" y="{top + i * cell + 5.5}" text-anchor="end">{a}</text>')
        for j, b in enumerate(order):
            v = rho[pos[a]][pos[b]]
            if v is None:
                continue
            colour = "#c0392b" if v > 0 else "#1f6fb2"
            out.append(f'<rect x="{left + j * cell}" y="{top + i * cell}" width="{cell}" height="{cell}" fill="{colour}" fill-opacity="{min(1.0, abs(v)):.1f}"/>')
    out.append("</svg>")
    return "\n".join(out) + "\n"


def report_command(args) -> int:
    doc = json.loads(args.screen.read_text(encoding="utf-8"))
    out_dir = args.output_dir
    out_dir.mkdir(parents=True, exist_ok=True)
    matrix = doc["matrix"]
    names = matrix["names"]
    with (out_dir / "matrix.csv").open("w", encoding="utf-8", newline="") as handle:
        handle.write("series," + ",".join(names) + "\n")
        for a, row in zip(names, matrix["rho"]):
            handle.write(a + "," + ",".join("" if v is None else f"{v:.4f}" for v in row) + "\n")
    (out_dir / "matrix.json").write_text(json.dumps({"names": names, "rho": [[None if v is None else round(v, 4) for v in r] for r in matrix["rho"]], "n": matrix["n"], "threshold": matrix["threshold"]}) + "\n", encoding="utf-8")
    (out_dir / "screen.json").write_text(json.dumps({k: v for k, v in doc.items() if k != "matrix"}, sort_keys=True, separators=(",", ":")) + "\n", encoding="utf-8")
    (out_dir / "clusters.json").write_text(json.dumps(matrix["clusters"], indent=1) + "\n", encoding="utf-8")
    (out_dir / "matrix.svg").write_text(heatmap(matrix), encoding="utf-8")
    leads = ranked_leads(doc)
    (out_dir / "ranked-leads.json").write_text(json.dumps(leads, indent=1) + "\n", encoding="utf-8")
    scope = doc["scope"]
    lines = [f"Ordinary days {scope['ordinary_days']} of {scope['scored_days']} scored ({scope['pressure_days_ordinary']} pressure days on ordinary days of {scope['pressure_days_all']}); "
             f"ordinary-day onsets {len(scope['onsets_ordinary'])} of {scope['onsets_all']}.", ""]
    lines += ["## Ranked leads", "", "| rank | series | direction | best lead | AUROC at best lead | leads excluding 0.5 | checks passed | noise risk | reason |", "|---|---|---|---|---|---|---|---|---|"]
    for k, item in enumerate(leads, start=1):
        passed = [n for n, ok in item["checks"].items() if ok]
        failed = [n for n, ok in item["checks"].items() if not ok]
        extra = f"; also in its cluster: {', '.join(item['also_in_cluster'])}" if item.get("also_in_cluster") else ""
        lines.append(f"| {k} | `{item['name']}` | {'higher series, more pressure' if item['direction'] == 1 else 'lower series, more pressure'} | {item['best_lead']} | {item['auroc']:.3f} | {item['leads_excluding']} | {item['passed']} of 4 | {item['noise_risk']} | passes {', '.join(passed) or 'none'}; fails {', '.join(failed) or 'none'}{extra} |")
    lines += ["", "## Splits of the ranked leads, and the persistence reference, at lead 1 (AUROC; 90% interval where the declared trigger fired)", "",
              "| series | pooled | 2018-19 | 2025-26 | 2018-2025 | 2026 | scarce state | ample state |", "|---|---|---|---|---|---|---|---|"]
    for name in [item["name"] for item in leads] + [SPREAD, "spread_lag1"]:
        cells = doc["series"][name]["leads"]["1"]
        lines.append(f"| `{name}` | " + " | ".join(_auc(cells.get(k)) for k in ("pooled", "regime:2018-19", "regime:2025-26", "period:2018-2025", "period:2026", "state:scarce", "state:ample")) + " |")
    lines += ["", "Pressure days on ordinary days by split: " + ", ".join(
        f"{k} {v['pressure_days']} of {v['n']}" for k, v in doc["series"][SPREAD]["leads"]["1"].items()) + ".", ""]
    lines += ["", "## Every series: AUROC for pressure days on ordinary days (pooled, 90% interval), by lead", "",
              "| series | " + " | ".join(f"lead {l}" for l in LEADS) + " | Spearman with the indicator, lead 1 | pre-onset AUC, lead 1 |", "|---|" + "---|" * (len(LEADS) + 2)]
    for name, series in doc["series"].items():
        cells = [_auc(series["leads"][str(l)]["pooled"]) for l in LEADS]
        rho = series["leads"]["1"]["pooled"]["rho"]["pressure"]
        pre = series["pre_onset"]["1"]
        pre_text = "-" if not pre["contrast"] else f"{pre['contrast']['auc']:.2f}" + (f" [{pre['interval'][0]:.2f}, {pre['interval'][1]:.2f}]" if pre["interval"] else "")
        lines.append(f"| `{name}` | " + " | ".join(cells) + f" | {_fmt(rho, 3, True)} | {pre_text} |")
    lines += ["", "## Clusters at |rho| >= 0.8 (lead 1, ordinary days)", "", "| representative | members |", "|---|---|"]
    for c in matrix["clusters"]:
        lines.append(f"| `{c['representative']}` | {', '.join('`' + m + '`' for m in c['members'])} |")
    (out_dir / "tables.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps({"leads": len(leads), "clusters": len(matrix["clusters"])}))
    return 0


def model_report_command(args) -> int:
    """The model test's tables: the judge's tiers, then the ordinary-day AUROC and calibration, paired."""

    judged = (
        {rule: json.loads(Path(path).read_text(encoding="utf-8"))["candidates"] for rule, path in (("flat", args.unweighted), ("weighted", args.weighted))}
        if args.weighted and args.unweighted else None
    )
    ordinary = json.loads(args.ordinary.read_text(encoding="utf-8"))
    names = [CONTROL.rsplit("+dist_roll", 1)[0], CONTROL, PARENT, TEST]
    yes = lambda x: "yes" if x else "no"
    ci = lambda r: f"{r['mean']:.3f} [{r['interval']['lower']:.3f}, {r['interval']['upper']:.3f}]"
    lines = [] if judged is None else ["Table M1. The judge in force (tiers 1, 3 and 5; the weighted rule is the one in force, the flat rule is reported beside it). Tier 1: onsets flagged at some lead 1 to 5, recall [90%], the pooled false alarms per onset (a false alarm counted once however many leads flag it; limit 2, #550); tier 1 also needs the recall conditions at each lead.", "",
             "| row | rule | onsets flagged | recall [90%] | pooled false alarms per onset | tier 1 | tier 3 | tier 5 | passes |", "|---|---|---|---|---|---|---|---|---|"]
    for name in names if judged else ():
        for rule in ("weighted", "flat"):
            e = judged[rule][name]
            t = e["tiers"]["onset_warning"]["lead_at_least_1"]
            v = e["verdict"]
            worst = t["pooled_weighted_false_alarms_per_onset"] if rule == "weighted" else t["pooled_false_alarms_per_onset"]
            lines.append(f"| `{name}` | {rule} | {t['onsets_flagged']:g} of {t['onsets']} | {ci(t['recall'])} | {worst:.2f} | {yes(v['tier_1_onset_warning'])} | {yes(v['tier_3_no_crying_wolf'])} | {yes(v['tier_5_week_ahead'])} | {yes(v['passes'])} |")
    lines += ["" if lines else "Table M1 is not made: the judge is not run on days past 2025-12-31 (#684, ruling of 13 October 2026).", "", "Table M2. On ordinary days at +5 bp: the forecast's AUROC for pressure days [90%], and the reliability intercept and slope (logistic of the outcome on logit(forecast); `-` where the forecast is constant or the fit is not formed). The control forecasts exactly 0 there.", "",
              "| row | h | days | pressure days | mean forecast | realised | AUROC [90%] | intercept | slope |", "|---|---|---|---|---|---|---|---|---|"]
    for name in names[1:]:
        for h, c in ordinary["rows"][name].items():
            cal = c["calibration"]
            auc = "0.500 (constant)" if c["constant"] else _auc({"auroc": c["auroc"], "interval": c["interval"]})
            lines.append(f"| `{name}` | {h} | {c['days']} | {c['pressure_days']} | {c['mean_forecast']:.4f} | {c['realised']:.4f} | {auc} | {_fmt(cal and cal['intercept'], 2, True)} | {_fmt(cal and cal['slope'], 2)} |")
    lines += ["", "Table M3. Paired on ordinary days: the AUROC of the test less the parent's, 90% stationary-bootstrap interval.", "", "| h | difference [90%] |", "|---|---|"]
    for h, c in ordinary["paired"].items():
        lines.append(f"| {h} | {c['auroc_difference']:+.3f} [{c['interval'][0]:+.3f}, {c['interval'][1]:+.3f}] |")
    args.output.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(args.output)
    return 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("declare").set_defaults(func=declare_command)
    panel = sub.add_parser("panel")
    panel.add_argument("--panel", type=Path, required=True)
    panel.add_argument("--output", type=Path, required=True)
    panel.add_argument("--check-every", type=int, default=100)
    panel.set_defaults(func=panel_command)
    run = sub.add_parser("run")
    run.add_argument("--panel", type=Path, required=True)
    run.add_argument("--output", type=Path, required=True)
    run.add_argument("--workers", type=int, default=4)
    run.set_defaults(func=run_command)
    model = sub.add_parser("model")
    model.add_argument("--panel", type=Path, required=True)
    model.add_argument("--published", type=Path, required=True)
    model.add_argument("--horizon", type=int, required=True)
    model.add_argument("--output", type=Path, required=True)
    model.add_argument("--end", help="last scored day, ISO; default the declaration's own (at most 2026-09-03, #684: a scratch scored span)")
    model.set_defaults(func=model_command)
    compare = sub.add_parser("compare")
    compare.add_argument("--rule", choices=("unweighted", "weighted"), default="weighted")
    compare.add_argument("--panel", type=Path, required=True)
    compare.add_argument("--output", type=Path, required=True)
    compare.add_argument("--markdown", type=Path)
    compare.add_argument("inputs", nargs="+", type=Path)
    compare.set_defaults(func=compare_command)
    ordinary = sub.add_parser("ordinary")
    ordinary.add_argument("--panel", type=Path, required=True)
    ordinary.add_argument("--output", type=Path, required=True)
    ordinary.add_argument("--end", help="last scored day, ISO; default the declaration's own (at most 2026-09-03, #684: a scratch scored span)")
    ordinary.add_argument("inputs", nargs="+", help="forecast files with {h} for the horizon")
    ordinary.set_defaults(func=ordinary_command)
    report = sub.add_parser("report")
    report.add_argument("screen", type=Path)
    report.add_argument("--output-dir", type=Path, required=True)
    report.set_defaults(func=report_command)
    modelreport = sub.add_parser("model-report")
    modelreport.add_argument("--weighted", type=Path, help="the judge's output under the weighted rule; with --unweighted, Table M1 is made")
    modelreport.add_argument("--unweighted", type=Path)
    modelreport.add_argument("--ordinary", type=Path, required=True)
    modelreport.add_argument("--output", type=Path, required=True)
    modelreport.set_defaults(func=model_report_command)
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
