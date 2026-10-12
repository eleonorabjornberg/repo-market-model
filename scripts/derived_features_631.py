"""Derived features, interactions and lagged pressure from data we hold, screened on ordinary days; one model test (#631).

An exploratory measurement, not a record: nothing is selected, nothing is published, no day after 2025-12-31 and no day of a locked tier
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

DECLARATION = REPO / "metadata" / "derived_features_631.json"
CANDIDATES = REPO / "metadata" / "pressure_judge" / "candidates"

FIRST_DAY = "2018-06-29"
LAST_DAY = "2025-12-31"
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
            "the published declaration, the live record and the pin do not move. The screen reads 2018-2025 and the model test is one "
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
            "locked_days": "none read: require_unlocked on the last scored day; the panel is cut at 2025-12-31",
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
            "note": "a list for the next declared model test, selected on 2018-2025: nothing in it is selected into a model",
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
            "scoring": {"first_day": FIRST_DAY, "last_day": LAST_DAY, "minimum_history": 61, "refit_every": 21, "decision_time": "16:00", "horizons": [1, 2, 3, 4, 5], "thresholds_bp": [5, 10]},
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


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("declare").set_defaults(func=declare_command)
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
