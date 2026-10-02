"""Early-warning inputs (#127): score every pre-declared input, on its own and grouped.

A scratch measurement, not a record: it writes JSON and Markdown to the paths
it is given, and nothing into `docs/runs/`. Every input is off in every
published declaration; this script switches `early_warning.COLUMN_FIELDS` on
for its own run, as #45's tests do for `on_rrp`.

    PYTHONPATH=src python3 scripts/early_warning_inputs.py panel --panel PUBLISHED.csv --output AUG.csv
    PYTHONPATH=src python3 scripts/early_warning_inputs.py crps --panel AUG.csv --run NAME --output OUT/crps_NAME.json
    PYTHONPATH=src python3 scripts/early_warning_inputs.py pressure --panel AUG.csv --horizon H --output OUT/hH.json
    PYTHONPATH=src python3 scripts/early_warning_inputs.py assemble --panel AUG.csv --output OUT/ew.json \\
        --markdown OUT/ew.md --crps OUT/crps_*.json --pressure OUT/h1.json ... OUT/h5.json

* `panel` adds to the published panel the raw columns the inputs read (SOFR's
  1st and 99th percentiles and EFFR from the tracked `funding_inputs/`
  snapshots, `on_rrp` from `on_rrp_inputs/`, `srf_take_up` from
  `srf_inputs/`), then every candidate column (`early_warning.build_columns`),
  and keeps the rows up to 2025-12-31 (`docs/decisions/lockbox.md`).
* `crps` is the distribution side: `compare --loss crps`, gbm cross-conformal
  on the published funding declaration (`FF`) against FF plus the run's
  columns, paired on one fold grid, split by regime and pressure-day type.
* `pressure` is the pressure-probability side at one horizon: pressure model
  v1's direct logistic (`ml.pressure_logistic_exceedance` on its #114
  declaration) as the control, and the same model plus each input's columns
  and product terms, every one paired against the control and against the
  persistence-logistic benchmark, at +5 and +10 bp.
* `assemble` merges the runs, adds lead time to onset and the October 2025
  onset, and writes the tables.
"""

from __future__ import annotations

import argparse
import contextlib
import csv
import hashlib
import json
import sys
from datetime import date, datetime, time, timezone
from pathlib import Path
from types import MappingProxyType
from unittest import mock

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))

from repo_model import contract, early_warning, pressure  # noqa: E402
from repo_model.baseline import (  # noqa: E402
    panel_sha256,
    persistence_logistic_exceedance,
    rolling_exceedance_backtest,
)
from repo_model.data import ON_RRP_MAX_GAP_DAYS, DailyObservation, audit_panel, load_daily_panel  # noqa: E402
from repo_model.evaluation_splits import load_split_declaration  # noqa: E402
from repo_model.ingest import load_snapshot_manifest, parse_snapshots  # noqa: E402

REGISTRY = REPO / "metadata" / "sources.json"
SPLITS = REPO / "metadata" / "evaluation_splits.json"
SNAPSHOTS = REPO / "tests" / "fixtures" / "snapshots"
#: The published panel's build cutoff (`metadata/funding_panel_manifest.json`).
BUILD_CUTOFF = datetime(2026, 9, 8, 21, 31, 42, tzinfo=timezone.utc)
TAUS = (5.0, 10.0)
HORIZONS = (1, 2, 3, 4, 5)
MINIMUM_HISTORY = 61
REFIT_EVERY = 21
DECISION = time(16, 0)
#: The last day any comparison may score, or any row of the scratch panel carry
#: (`docs/decisions/lockbox.md`).
END = date(2025, 12, 31)

#: The published distributional declaration (FF), as in `pressure_model_v1.py`.
GBM_FEATURES = (
    "reserve_balances", "sofr_p25", "sofr_p75", "sofr_volume", "spread_bps",
    "tbill_13w", "tbill_4w", "tga", "treasury_settlement",
)
#: Pressure model v1's direct declaration (#114).
DIRECT_FEATURES = (
    "spread_bps", "days_to_month_end", "quarter_end", "tax_date",
    "treasury_settlement", "reserve_balances", "tga",
)
#: Scheduled one business day ahead, so not public at a longer horizon (#114).
SETTLEMENT = "treasury_settlement"
#: The direct design already carries the TGA's change (`ml._PressureDesign`),
#: so the column form of it is read by the gbm only.
DESIGN_HAS = ("tga_change_5d",)

RAW_COLUMNS = ("sofr_p1", "sofr_p99", "effr", "on_rrp", "srf_take_up")
#: Read off SOFR's 1st and 99th percentiles, which have two one-row holes.
CARRIED_ACROSS_ONE_ROW = ("sofr_p1", "sofr_p99", "sofr_p99_p75_bps", "sofr_p99_iorb_bps")
DERIVED_COLUMNS = tuple(early_warning.COLUMN_FIELDS)


def _candidate(name):
    (found,) = [c for c in early_warning.CANDIDATES if c.name == name]
    return found


def runs():
    """Every scored run: each unblocked input, the onset group, and all together."""

    out = {}
    for candidate in early_warning.CANDIDATES:
        if not candidate.blocked:
            out[candidate.name] = (candidate.columns, candidate.products)
    onset = [_candidate(name) for name in early_warning.ONSET_GROUP]
    out["onset_group"] = (
        tuple(dict.fromkeys(c for cand in onset for c in cand.columns)),
        tuple(p for cand in onset for p in cand.products),
    )
    every = [c for c in early_warning.CANDIDATES if not c.blocked]
    out["all_inputs"] = (
        tuple(dict.fromkeys(c for cand in every for c in cand.columns)),
        tuple(dict.fromkeys(p for cand in every for p in cand.products)),
    )
    return out


@contextlib.contextmanager
def switched_on():
    """`early_warning.COLUMN_FIELDS` in the feature map, for this run only."""

    fields = dict(early_warning.COLUMN_FIELDS)
    with mock.patch.multiple(
        contract,
        FEATURE_FIELDS=MappingProxyType({**contract.FEATURE_FIELDS, **fields}),
        FEATURE_SOURCES=MappingProxyType(
            {
                **contract.FEATURE_SOURCES,
                **{
                    column: tuple(sorted({source for source, _f in pairs}))
                    for column, pairs in fields.items()
                },
            }
        ),
    ):
        yield


# -- the scratch panel ----------------------------------------------------------


def _series(directory, wanted):
    """`{series: {ref_date: value}}`, the latest vintage at the build cutoff."""

    artifacts = [load_snapshot_manifest(path) for path in sorted(directory.rglob("*.manifest.json"))]
    best = {}
    for row in parse_snapshots(artifacts).rows:
        if row.series_id not in wanted or row.available_at > BUILD_CUTOFF:
            continue
        key = (row.series_id, row.ref_date)
        if key not in best or row.available_at >= best[key].available_at:
            best[key] = row
    out = {name: {} for name in wanted}
    for (series, ref_date), row in best.items():
        out[series][ref_date] = row.value
    return out


def panel_command(args) -> int:
    rows = load_daily_panel(args.panel)
    funding = _series(SNAPSHOTS / "funding_inputs", {"SOFR", "SOFR_p1", "SOFR_p99", "DFF"})
    # The parsed SOFR must be the panel's own, or the percentiles beside it are not.
    for row in rows:
        if abs(funding["SOFR"][row.date] - row.values["sofr"]) > 1e-12:
            raise SystemExit(f"{row.date}: parsed SOFR differs from the panel's")
    on_rrp = _series(SNAPSHOTS / "on_rrp_inputs", {"reverse_repo_total_accepted"})[
        "reverse_repo_total_accepted"
    ]
    srf = _series(SNAPSHOTS / "srf_inputs", {"srf_total_accepted"})["srf_total_accepted"]

    holes = {name: [] for name in RAW_COLUMNS}
    carried = []
    added = []
    for row in rows:
        values = dict(row.values)
        values["sofr_p1"] = funding["SOFR_p1"].get(row.date)
        values["sofr_p99"] = funding["SOFR_p99"].get(row.date)
        values["effr"] = funding["DFF"].get(row.date)
        # `on_rrp` carries across a day with no operation, no further than the
        # panel's own bound (`data.ON_RRP_MAX_GAP_DAYS`, #45).
        value = on_rrp.get(row.date)
        if value is None:
            prior = [d for d in on_rrp if d < row.date]
            if prior and (row.date - max(prior)).days <= ON_RRP_MAX_GAP_DAYS:
                value = on_rrp[max(prior)]
                carried.append(row.date.isoformat())
        values["on_rrp"] = value
        values["srf_take_up"] = srf.get(row.date)
        for name in RAW_COLUMNS:
            if values[name] is None and not (name == "srf_take_up" and row.date < early_warning.SRF_INCEPTION):
                holes[name].append(row.date.isoformat())
        added.append(DailyObservation(row.date, values))
    built = [row for row in early_warning.build_columns(added) if row.date <= END]
    # SOFR's percentiles have two one-day holes (2019-05-31, 2021-08-05), as
    # the published panel's sofr_p25/sofr_p75 do. The gbm reads a hole as
    # missing; the direct logistic refuses a forecast on one. So in this scratch
    # panel only, a percentile column carries its prior row across a one-row
    # hole: an older value, never a newer one, and every carry is listed.
    percentile_carried = []
    for position in range(1, len(built)):
        for name in CARRIED_ACROSS_ONE_ROW:
            if built[position].values.get(name) is None and built[position - 1].values.get(name) is not None:
                built[position].values[name] = built[position - 1].values[name]
                percentile_carried.append(f"{built[position].date.isoformat()}:{name}")

    header = list(load_header(args.panel)) + list(RAW_COLUMNS) + list(DERIVED_COLUMNS)
    header = list(dict.fromkeys(header))
    with args.output.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerow(header)
        for row in built:
            writer.writerow(
                [row.date.isoformat()]
                + [_cell(row.values.get(name)) for name in header[1:]]
            )
    digest = hashlib.sha256(args.output.read_bytes()).hexdigest()
    summary = {
        "output": str(args.output),
        "sha256": digest,
        "rows": len(built),
        "first": built[0].date.isoformat(),
        "last": built[-1].date.isoformat(),
        "holes": {name: dates for name, dates in holes.items() if dates},
        "on_rrp_carried": carried,
        "percentile_carried": percentile_carried,
        "derived_missing": {
            name: sum(1 for row in built if row.values.get(name) is None) for name in DERIVED_COLUMNS
        },
    }
    print(json.dumps(summary, indent=1))
    return 0


def load_header(path):
    with Path(path).open(newline="", encoding="utf-8") as handle:
        return next(csv.reader(handle))


def _cell(value):
    return "" if value is None else repr(float(value))


# -- distribution: CRPS ------------------------------------------------------------


def crps_command(args) -> int:
    from repo_model import cli

    columns, _products = runs()[args.run]
    extra = [name for name in columns if name not in GBM_FEATURES]

    def side(letter, features):
        out = ["--model-" + letter, "gbm", "--calibration-" + letter, "cross_conformal"]
        for name in features:
            out += ["--feature-" + letter, name]
        return out

    argv = [
        "compare", str(args.panel),
        "--registry", str(REGISTRY), "--decision-time", "16:00",
        "--minimum-history", str(MINIMUM_HISTORY), "--refit-every", str(REFIT_EVERY),
        "--end", END.isoformat(), "--splits", str(SPLITS), "--loss", "crps",
        *side("a", GBM_FEATURES), *side("b", GBM_FEATURES + tuple(extra)),
        "--report", str(args.output),
    ]
    with switched_on():
        return cli.main(argv)


# -- pressure probability ------------------------------------------------------------


def _at_horizon(features, horizon):
    return tuple(name for name in features if horizon == 1 or name != SETTLEMENT)


def _run(rows, name, predictor, features, horizon):
    return rolling_exceedance_backtest(
        rows,
        predictor=predictor,
        model_name=name,
        features=features,
        registry=json.loads(REGISTRY.read_text()),
        decision_time=DECISION,
        taus=TAUS,
        minimum_history=MINIMUM_HISTORY,
        refit_every=REFIT_EVERY,
        end=END,
        horizon=horizon,
    )


def _forecasts(report):
    return {
        f"{tau:g}": {
            when.isoformat(): curve[position]
            for when, curve in zip(report.scored_dates, report.forecast)
        }
        for position, tau in enumerate(report.taus)
    }


def pressure_command(args) -> int:
    from repo_model import ml

    rows = load_daily_panel(args.panel)
    audit_panel(rows)
    splits = load_split_declaration(SPLITS)
    h = args.horizon
    control_features = _at_horizon(DIRECT_FEATURES, h)
    not_public = {}
    with switched_on():
        control = _run(
            rows, "pressure_v1_logistic",
            ml.pressure_logistic_exceedance(control_features, splits, minimum_history=MINIMUM_HISTORY),
            control_features, h,
        )
        benchmarks = {
            "pressure_v1_logistic": control,
            "persistence_logistic": _run(
                rows, "persistence_logistic",
                persistence_logistic_exceedance(minimum_history=MINIMUM_HISTORY),
                ("spread_bps",), h,
            ),
        }
        candidates = {}
        declarations = {}
        for name, (columns, products) in runs().items():
            if h > 1 and any(SETTLEMENT in pair for pair in products):
                products = tuple(pair for pair in products if SETTLEMENT not in pair)
                if name not in ("onset_group", "all_inputs"):
                    not_public[name] = (
                        f"its product reads {SETTLEMENT}, which is not public at a "
                        f"horizon-{h} decision under its declaration"
                    )
                    continue
            features = control_features + tuple(
                column for column in columns
                if column not in control_features and column not in DESIGN_HAS
            )
            if features == control_features and not products:
                not_public[name] = "the direct design already carries it"
                continue
            report = _run(
                rows, name,
                ml.pressure_logistic_exceedance(
                    features, splits, minimum_history=MINIMUM_HISTORY, products=products
                ),
                features, h,
            )
            candidates[name] = report
            declarations[name] = {
                "features": list(features),
                "products": [list(pair) for pair in products],
                "model_settings": dict(report.model_settings),
            }
    digest = panel_sha256(args.panel)
    card = pressure.scorecard(candidates, benchmarks, rows=rows, declaration=splits, panel_sha256=digest)
    document = {
        "horizon": h,
        "panel_sha256": digest,
        "scored_window": {
            "first": control.scored_dates[0].isoformat(),
            "last": control.scored_dates[-1].isoformat(),
            "days": len(control.scored_dates),
        },
        "fold_grid": {
            "walk_forward": "expanding window",
            "refit_every": REFIT_EVERY,
            "minimum_history": MINIMUM_HISTORY,
            "decision_time": DECISION.isoformat(timespec="minutes"),
            "end": END.isoformat(),
        },
        "control": {"features": list(control_features), "model_settings": dict(control.model_settings)},
        "declarations": declarations,
        "not_scored": not_public,
        "splits": splits.document(),
        "scorecard": card,
        "forecasts": {name: _forecasts(report) for name, report in {**candidates, **benchmarks}.items()},
    }
    args.output.write_text(json.dumps(document, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"horizon": h, "output": str(args.output), **document["scored_window"]}))
    return 0


# -- assembly -----------------------------------------------------------------


def _fmt(value, places=4):
    return "–" if value is None else f"{value:+.{places}f}" if places else str(value)


def _iv(entry, places=4):
    """`mean [lower, upper]`, or the reason there is none."""

    if entry is None or "mean" not in entry:
        return "– (n=0)"
    interval = entry.get("interval")
    if not interval:
        return f"{entry['mean']:+.{places}f} (n={entry.get('count')}, no interval)"
    return f"{entry['mean']:+.{places}f} [{interval['lower']:+.{places}f}, {interval['upper']:+.{places}f}]"


def _paired(card, name, bench, key):
    return card["candidates"][name]["paired"][bench]["by_tau"][key]["paired_brier_difference"]


def _split_names(card, name, bench, key):
    splits = _paired(card, name, bench, key)["splits"]
    return [("by_regime", k) for k in splits["by_regime"]] + [("by_day_type", k) for k in splits["by_day_type"]]


def assemble_command(args) -> int:
    rows = load_daily_panel(args.panel)
    crps = {}
    for path in args.crps:
        document = json.loads(Path(path).read_text())
        crps[Path(path).stem.removeprefix("crps_")] = _crps_summary(document)
    parts = sorted((json.loads(Path(p).read_text()) for p in args.pressure), key=lambda d: d["horizon"])
    names = list(runs())

    # Lead time: the longest horizon whose forecast of an onset reached an alarm level.
    common = set.intersection(*(set(part["forecasts"]["persistence_logistic"]["5"]) for part in parts))
    common_dates = sorted(date.fromisoformat(when) for when in common)
    lead, october = {}, {}
    for tau in TAUS:
        key = f"{tau:g}"
        onset_days = pressure.onsets(rows, tau, common_dates)
        lead[key] = {"onsets": [d.isoformat() for d in onset_days], "by_model": {}}
        october[key] = {}
        for name in ["pressure_v1_logistic", "persistence_logistic"] + names:
            if not all(name in part["forecasts"] for part in parts):
                continue
            per_h = {
                part["horizon"]: {date.fromisoformat(w): p for w, p in part["forecasts"][name][key].items()}
                for part in parts
            }
            lead[key]["by_model"][name] = [
                pressure.lead_times(per_h, onset_days, level) for level in pressure.ALARM_LEVELS
            ]
            october[key][name] = {
                d.isoformat(): {str(h): per_h[h].get(d) for h in sorted(per_h)}
                for d in onset_days if d.year == 2025 and d.month == 10
            }
    # Does the input move before the October 2025 onset? Its value on the ten
    # panel days before the +5 bp onset, as each row stands (the as-of rule
    # reads a row only once all its fields are public, so a forecast sees these
    # a few days later).
    onset_rows = {}
    oct_onsets = [date.fromisoformat(d) for d in lead["5"]["onsets"] if d.startswith("2025-10")]
    if oct_onsets:
        index = [row.date for row in rows].index(oct_onsets[0])
        window = rows[index - 10 : index + 1]
        onset_rows = {
            "onset": oct_onsets[0].isoformat(),
            "rows": [
                {"date": row.date.isoformat(), "spread_bps": row.spread_bps,
                 **{c: row.values.get(c) for c in DERIVED_COLUMNS + ("dealer_treasury_position",)}}
                for row in window
            ],
        }
    document = {
        "directive": "#127",
        "status": "scratch measurement; not a record, nothing published moves",
        "candidates": [c._asdict() for c in early_warning.CANDIDATES],
        "crps": crps,
        "pressure": {str(p["horizon"]): {k: v for k, v in p.items() if k != "forecasts"} for p in parts},
        "lead_time": lead,
        "october_2025_onset": october,
        "october_2025_inputs": onset_rows,
    }
    args.output.write_text(json.dumps(document, indent=1, sort_keys=True, default=str) + "\n", encoding="utf-8")
    args.markdown.write_text(_markdown(crps, parts, names, lead, october, onset_rows), encoding="utf-8")
    print(json.dumps({"output": str(args.output), "markdown": str(args.markdown)}))
    return 0


def _crps_summary(document):
    """The pooled and split paired CRPS differences of one `compare` record."""

    comparison = document["comparison"]
    added = [
        name for name in document["declaration"]["model_b"]["features"]
        if name not in document["declaration"]["model_a"]["features"]
    ]
    pooled = {"mean": comparison["mean_difference_bps"], "interval": comparison["mean_difference_interval"]}
    splits = comparison["splits"]
    return {
        "added": added,
        "a": comparison["model_a"]["crps_bps"],
        "b": comparison["model_b"]["crps_bps"],
        "origins": comparison["origin_count"],
        "pooled": pooled,
        "splits": {
            label: splits[group][label]
            for group in ("by_regime", "by_day_type")
            for label in splits[group]
        },
        "declaration": document["declaration"],
    }


def _markdown(crps, parts, names, lead, october, onset_rows) -> str:
    out = []
    window = parts[0]["scored_window"]
    out.append("### Distribution: CRPS, FF against FF plus the input (gbm cross-conformal, horizon 1)\n")
    out.append(
        f"Scored {window['first']} to {END.isoformat()}. Paired difference = CRPS(FF) − CRPS(FF+input), bp; "
        "positive means the input helped. 90% stationary-bootstrap interval.\n"
    )
    split_names = None
    for name in names:
        if name not in crps:
            continue
        summary = crps[name]
        if split_names is None:
            split_names = list(summary["splits"])
            out.append("| Run | Added columns | CRPS FF | CRPS FF+input | Pooled | " + " | ".join(split_names) + " |")
            out.append("|---|---|---|---|---|" + "---|" * len(split_names))
        out.append(
            f"| {name} | {', '.join(summary['added']) or '–'} | {summary['a']:.4f} | {summary['b']:.4f} | "
            f"**{_iv(summary['pooled'])}** | " + " | ".join(_iv(summary["splits"][s]) for s in split_names) + " |"
        )
    out.append("")
    out.append(
        "`issuance_x_dealer_positions` has no row of its own: its gbm declaration is "
        "`dealer_positions`' (FF already carries `treasury_settlement`, and the trees form the "
        "interaction). The product term is scored in the pressure-probability tables.\n"
    )
    for tau in TAUS:
        key = f"{tau:g}"
        out.append(f"### Pressure probability, +{key} bp: Brier, paired\n")
        out.append(
            "Direct logistic (pressure model v1's declaration) plus the input. Paired difference = "
            "Brier(benchmark) − Brier(candidate), 90% stationary-bootstrap interval; positive means "
            "the input helped.\n"
        )
        for part in parts:
            card = part["scorecard"]
            w = part["scored_window"]
            out.append(f"**Horizon {part['horizon']}** (scored {w['first']} to {w['last']}, {w['days']} days)\n")
            out.append("| Run | Brier | AP | vs pressure v1 (logistic) | vs persistence-logistic |")
            out.append("|---|---|---|---|---|")
            for bench in ("pressure_v1_logistic", "persistence_logistic"):
                m = card["benchmarks"][bench][key]
                out.append(f"| {bench} (benchmark) | {m['brier']:.4f} | {m.get('average_precision', 0):.3f} | | |")
            for name in names:
                if name not in card["candidates"]:
                    reason = part["not_scored"].get(name)
                    if reason:
                        out.append(f"| {name} | not scored: {reason} | | | |")
                    continue
                m = card["candidates"][name]["metrics"][key]
                out.append(
                    f"| {name} | {m['brier']:.4f} | {m.get('average_precision', 0):.3f} | "
                    f"{_iv(_paired(card, name, 'pressure_v1_logistic', key))} | "
                    f"{_iv(_paired(card, name, 'persistence_logistic', key))} |"
                )
            out.append("")
    out.append(_split_tables(parts, names))
    out.append(_lead_tables(lead, names))
    out.append(_october_tables(october, onset_rows))
    return "\n".join(out) + "\n"


def _split_tables(parts, names) -> str:
    """Every candidate's paired Brier difference, by regime and by day type."""

    out = []
    for tau in TAUS:
        key = f"{tau:g}"
        for bench, label in (("pressure_v1_logistic", "pressure v1 (logistic)"), ("persistence_logistic", "persistence-logistic")):
            out.append(f"### +{key} bp: paired Brier difference against {label}, by regime and pressure-day type\n")
            for part in parts:
                card = part["scorecard"]
                scored = [n for n in names if n in card["candidates"]]
                if not scored:
                    continue
                columns = _split_names(card, scored[0], bench, key)
                out.append(f"**Horizon {part['horizon']}**\n")
                out.append("| Run | " + " | ".join(c for _g, c in columns) + " |")
                out.append("|---|" + "---|" * len(columns))
                for name in scored:
                    splits = _paired(card, name, bench, key)["splits"]
                    out.append(f"| {name} | " + " | ".join(_iv(splits[g].get(c)) for g, c in columns) + " |")
                out.append("")
    return "\n".join(out)


def _lead_tables(lead, names) -> str:
    out = ["### Lead time to pressure onset\n",
           "Lead time is the longest horizon (1–5 business days) whose forecast of the onset day "
           "reached the alarm level; 0 is a miss.\n"]
    for key, entry in lead.items():
        out.append(f"**+{key} bp**: {len(entry['onsets'])} onsets\n")
        out.append("| Run | flagged at 0.2 | mean lead at 0.2 | flagged at 0.5 | mean lead at 0.5 |")
        out.append("|---|---|---|---|---|")
        for name in ["pressure_v1_logistic", "persistence_logistic"] + names:
            if name not in entry["by_model"]:
                continue
            low, high = entry["by_model"][name]
            out.append(
                f"| {name} | {low['flagged']}/{low['onsets']} | {low['mean_lead_days']:.2f} | "
                f"{high['flagged']}/{high['onsets']} | {high['mean_lead_days']:.2f} |"
            )
        out.append("")
    return "\n".join(out)


def _october_tables(october, onset_rows) -> str:
    out = ["### The October 2025 onset\n"]
    for key, by_model in october.items():
        days = sorted({d for entry in by_model.values() for d in entry})
        for day in days:
            out.append(f"**+{key} bp, onset {day}**: probability forecast of that day at each horizon\n")
            out.append("| Run | h=1 | h=2 | h=3 | h=4 | h=5 |")
            out.append("|---|---|---|---|---|---|")
            for name, entry in by_model.items():
                if day in entry:
                    cells = [entry[day].get(str(h)) for h in HORIZONS]
                    out.append(f"| {name} | " + " | ".join("–" if c is None else f"{c:.3f}" for c in cells) + " |")
            out.append("")
    if onset_rows:
        columns = [c for c in onset_rows["rows"][0] if c != "date"]
        out.append(f"**The inputs before the +5 bp onset of {onset_rows['onset']}**, as each row stands "
                   "(a forecast reads a row only once all its fields are public)\n")
        out.append("| Date | " + " | ".join(columns) + " |")
        out.append("|---|" + "---|" * len(columns))
        for row in onset_rows["rows"]:
            out.append(f"| {row['date']} | " + " | ".join(
                "–" if row[c] is None else f"{row[c]:.3f}" for c in columns) + " |")
        out.append("")
    return "\n".join(out)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="command", required=True)
    one = sub.add_parser("panel")
    one.add_argument("--panel", type=Path, required=True)
    one.add_argument("--output", type=Path, required=True)
    one.set_defaults(handler=panel_command)
    two = sub.add_parser("crps")
    two.add_argument("--panel", type=Path, required=True)
    two.add_argument("--run", choices=tuple(runs()), required=True)
    two.add_argument("--output", type=Path, required=True)
    two.set_defaults(handler=crps_command)
    three = sub.add_parser("pressure")
    three.add_argument("--panel", type=Path, required=True)
    three.add_argument("--horizon", type=int, choices=HORIZONS, required=True)
    three.add_argument("--output", type=Path, required=True)
    three.set_defaults(handler=pressure_command)
    four = sub.add_parser("assemble")
    four.add_argument("--panel", type=Path, required=True)
    four.add_argument("--output", type=Path, required=True)
    four.add_argument("--markdown", type=Path, required=True)
    four.add_argument("--crps", nargs="*", default=[])
    four.add_argument("--pressure", nargs="+", required=True)
    four.set_defaults(handler=assemble_command)
    args = parser.parse_args(argv)
    return args.handler(args)


if __name__ == "__main__":
    raise SystemExit(main())
