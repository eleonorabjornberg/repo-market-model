"""Per-quarter peak pressure in the quarter-end window (#140), for the published declarations.

A worked example, not a record: it writes JSON and a Markdown table to the
paths it is given, and nothing into `docs/runs/`.

Each published exceedance declaration in `docs/runs/` is re-run by
`baseline.rolling_exceedance_backtest` on the published panel, walk-forward
with an expanding window, refitted every 21 scored days, at +5 and +10 bp, to
2025-12-31: the published records score into the locked tiers, so their own
window cannot be re-scored (`docs/decisions/lockbox.md`). Then
`quarter_peaks.quarter_peak_table` reads, per quarter from 2018 Q3 to 2025 Q4,
the realised peak of SOFR - IORB in the quarter-end window and the highest
probability each declaration gave on a window day. A window day after
2025-12-31 is not read.

    PYTHONPATH=src /opt/rmm-venv/bin/python scripts/quarter_end_peaks.py run --panel PANEL --model NAME --output OUT/NAME.json
    PYTHONPATH=src python3 scripts/quarter_end_peaks.py assemble --panel PANEL --output OUT/quarter_peaks.json \
        --markdown OUT/quarter_peaks.md OUT/climatology.json OUT/calendar_climatology.json ...

`run` takes one name from `DECLARATIONS`. The three gbm names need the `ml`
extra.
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import date, time
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))

from repo_model.baseline import (  # noqa: E402
    calendar_climatology_exceedance,
    climatology_exceedance,
    panel_sha256,
    persistence_logistic_exceedance,
    rolling_exceedance_backtest,
)
from repo_model.data import audit_panel, load_daily_panel  # noqa: E402
from repo_model.evaluation_splits import load_split_declaration  # noqa: E402
from repo_model.quarter_peaks import quarter_peak_table  # noqa: E402

REGISTRY = REPO / "metadata" / "sources.json"
SPLITS = REPO / "metadata" / "evaluation_splits.json"
TAUS = (5.0, 10.0)
MINIMUM_HISTORY = 61
REFIT_EVERY = 21
DECISION = time(16, 0)
#: The last day any comparison may score (`docs/decisions/lockbox.md`).
END = date(2025, 12, 31)
FIRST_QUARTER = (2018, 3)
LAST_QUARTER = (2025, 4)

_GBM4 = ("sofr_p25", "sofr_p75", "sofr_volume", "spread_bps")
_GBM9 = (
    "reserve_balances", "sofr_p25", "sofr_p75", "sofr_volume", "spread_bps",
    "tbill_13w", "tbill_4w", "tga", "treasury_settlement",
)

#: Name -> (published record, features, settings). The declarations of the
#: records in `docs/runs/`, as their `declaration` blocks state them.
DECLARATIONS = {
    "climatology": ("exceedance_climatology.json", ("spread_bps",), {}),
    "calendar_climatology": (
        "exceedance_calendar_climatology.json",
        ("days_to_month_end", "quarter_end", "spread_bps", "tax_date"),
        {},
    ),
    "persistence_logistic": ("exceedance_persistence_logistic.json", ("spread_bps",), {}),
    "gbm": ("exceedance_gbm.json", _GBM4, {}),
    "gbm_cross_conformal": (
        "exceedance_gbm_cross_conformal.json",
        _GBM4,
        {"calibration": "cross_conformal", "calibration_folds": 5},
    ),
    "gbm_cross_conformal_funding": (
        "exceedance_gbm_cross_conformal_funding.json",
        _GBM9,
        {"calibration": "cross_conformal", "calibration_folds": 5},
    ),
}


def _predictor(name):
    _, features, settings = DECLARATIONS[name]
    if name == "climatology":
        return climatology_exceedance(minimum_history=MINIMUM_HISTORY)
    if name == "calendar_climatology":
        return calendar_climatology_exceedance(
            load_split_declaration(SPLITS), minimum_history=MINIMUM_HISTORY
        )
    if name == "persistence_logistic":
        return persistence_logistic_exceedance(minimum_history=MINIMUM_HISTORY)
    from repo_model import ml

    regressors = tuple(feature for feature in features if feature != "spread_bps")
    return ml.gbm_exceedance(regressors, minimum_history=MINIMUM_HISTORY, **settings)


def _check_declaration(name):
    """Refuse a name whose declaration here differs from its published record's."""

    record, features, settings = DECLARATIONS[name]
    published = json.loads((REPO / "docs" / "runs" / record).read_text())["declaration"]
    if sorted(published["features"]) != sorted(features):
        raise ValueError(f"{name}: features {features} are not {record}'s {published['features']}")
    model = "gbm" if name.startswith("gbm") else name
    if published["model"] != model:
        raise ValueError(f"{name}: {record} declares model {published['model']!r}")
    for key in ("calibration", "calibration_folds"):
        if published.get(key) != settings.get(key):
            raise ValueError(f"{name}: {key} {settings.get(key)!r} is not {record}'s {published.get(key)!r}")
    if published["minimum_history"] != MINIMUM_HISTORY or published["refit_every"] != REFIT_EVERY:
        raise ValueError(f"{name}: {record} is not minimum history 61, refit every 21")


def run(args):
    _check_declaration(args.model)
    rows = load_daily_panel(args.panel)
    audit_panel(rows)
    _, features, _ = DECLARATIONS[args.model]
    report = rolling_exceedance_backtest(
        rows,
        predictor=_predictor(args.model),
        model_name=args.model,
        features=features,
        registry=json.loads(REGISTRY.read_text()),
        decision_time=DECISION,
        taus=TAUS,
        minimum_history=MINIMUM_HISTORY,
        refit_every=REFIT_EVERY,
        end=END,
    )
    document = {
        "model": args.model,
        "record": DECLARATIONS[args.model][0],
        "panel_sha256": panel_sha256(args.panel),
        "end": END.isoformat(),
        "scored_days": len(report.scored_dates),
        "forecasts": {
            f"{tau:g}": {
                when.isoformat(): curve[position]
                for when, curve in zip(report.scored_dates, report.forecast)
            }
            for position, tau in enumerate(report.taus)
        },
    }
    args.output.write_text(json.dumps(document, indent=1, sort_keys=True) + "\n")
    print(f"{args.model}: {len(report.scored_dates)} scored days to {END}")


def _cell(value, digits=3):
    return "–" if value is None else f"{value:.{digits}f}"


def assemble(args):
    rows = load_daily_panel(args.panel)
    digest = panel_sha256(args.panel)
    spreads = {row.date: row.spread_bps for row in rows if row.date <= END}
    forecasts = {}
    for path in args.runs:
        document = json.loads(Path(path).read_text())
        if document["panel_sha256"] != digest:
            raise ValueError(f"{path} was run on panel {document['panel_sha256']}, not {digest}")
        forecasts[document["model"]] = {
            float(tau): {date.fromisoformat(day): p for day, p in by_day.items()}
            for tau, by_day in document["forecasts"].items()
        }
    names = [name for name in DECLARATIONS if name in forecasts]
    table = quarter_peak_table(
        spreads, {name: forecasts[name] for name in names}, first=FIRST_QUARTER,
        last=LAST_QUARTER, end=END, taus=TAUS,
    )
    args.output.write_text(
        json.dumps({"panel_sha256": digest, "end": END.isoformat(), "quarters": table},
                   indent=1, sort_keys=True) + "\n"
    )
    header = ["Quarter", "Window", "Peak (bp)", "Peak day", "> +5", "> +10"]
    for name in names:
        header += [f"{name} P(>5)", f"{name} P(>10)"]
    lines = ["| " + " | ".join(header) + " |", "|" + "---|" * len(header)]
    for row in table:
        window = f"{row['window'][0][5:]} to {row['window'][-1][5:]}"
        if row["window_days_after_end"]:
            window += f" ({row['window_days_after_end']} after {END} not read)"
        cells = [
            row["quarter"], window, _cell(row["peak_bps"], 0), row["peak_day"] or "–",
            "yes" if row["above"]["5"] else "no", "yes" if row["above"]["10"] else "no",
        ]
        for name in names:
            peaks = row["forecast_peaks"][name]
            cells += [_cell(peaks["5"]["max"]), _cell(peaks["10"]["max"])]
        lines.append("| " + " | ".join(cells) + " |")
    args.markdown.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="command", required=True)
    one = sub.add_parser("run")
    one.add_argument("--panel", type=Path, required=True)
    one.add_argument("--model", choices=sorted(DECLARATIONS), required=True)
    one.add_argument("--output", type=Path, required=True)
    one.set_defaults(func=run)
    both = sub.add_parser("assemble")
    both.add_argument("--panel", type=Path, required=True)
    both.add_argument("--output", type=Path, required=True)
    both.add_argument("--markdown", type=Path, required=True)
    both.add_argument("runs", nargs="+")
    both.set_defaults(func=assemble)
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
