"""Cleared-DVP segment test (#187): score every pre-declared input against pressure model v1.

A scratch measurement, not a record: it writes pickles, JSON and Markdown to
the paths it is given, and nothing into `docs/runs/`. Every input is off in
every published declaration; this script switches `dvp_segment.COLUMN_FIELDS`
(and #127's two spreads) on for its own run. The candidates, groups, windows,
sensitivities and the win rule are `repo_model.dvp_segment`'s, fixed before
any scoring.

    PYTHONPATH=src python3 scripts/dvp_segment_inputs.py panel --panel PUBLISHED.csv --output AUG.csv
    PYTHONPATH=src python3 scripts/dvp_segment_inputs.py check --panel AUG.csv --output OUT/check.json
    PYTHONPATH=src python3 scripts/dvp_segment_inputs.py run --panel AUG.csv --run NAME --horizon H --output OUT/NAME_hH.pickle
    PYTHONPATH=src python3 scripts/dvp_segment_inputs.py crps --panel AUG.csv --run NAME --output OUT/crps_NAME.json
    PYTHONPATH=src python3 scripts/dvp_segment_inputs.py assemble --panel AUG.csv --runs OUT --output OUT/dvp.json \\
        --markdown OUT/dvp.md

* `panel` adds to the published panel BGCR's volume (tracked `funding_inputs/`
  snapshot) and the OFR's preliminary DVP rate (`ofr_inputs/`), then #127's
  SOFR−TGCR and BGCR−TGCR and every `dvp_segment` column, and keeps the rows up
  to 2025-12-31 (`docs/decisions/lockbox.md`).
* `check` rebuilds the orchestrating session's scratch check of 2 October in
  repository code: the DVP volume rebuilt from SOFR and BGCR against the OFR's,
  SOFR−BGCR against the OFR's DVP rate−BGCR, and preliminary against final.
* `run` scores one run at one horizon: `control@full` / `control@ofr` (pressure
  model v1 as #124 published it: `scripts/pressure_model_v1.py`'s gbm on the
  published funding declaration, conformal PID with nested selection,
  recalibrated out of fold), `persistence_logistic@full` / `@ofr`, a group of
  `dvp_segment.GROUPS` (v1 plus the group's columns), or a sensitivity.
* `crps` is the distribution side at horizon 1: `compare --loss crps`, the
  published funding declaration against it plus the run's columns, both
  calibrated by `conformal_pid_nested`, on one fold grid.
* `assemble` pairs every run with its benchmarks, computes the p-values, runs
  the Holm correction over the family, classifies each group by the win rule,
  and writes the tables, lead time and the October 2025 onset.

The runs on the OFR window read a panel that starts on 2020-09-09, theirs and
their control's: a regressor never observed in a training window cannot be
fitted (`baseline`'s imputation refuses it).
"""

from __future__ import annotations

import argparse
import contextlib
import copyreg
import csv
import hashlib
import importlib.util
import json
import pickle
import sys
import tempfile
from datetime import date
from pathlib import Path
from types import MappingProxyType
from unittest import mock

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))


def _script(name):
    """A sibling script as a module, without running it: the control and the
    scratch-panel helpers are theirs, not restated."""

    spec = importlib.util.spec_from_file_location(name, REPO / "scripts" / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


#: Pressure model v1's published code path (#124) and #127's panel helpers.
v1 = _script("pressure_model_v1")
ew = _script("early_warning_inputs")

from repo_model import contract, dvp_segment, early_warning, pressure  # noqa: E402
from repo_model.baseline import (  # noqa: E402
    benchmark_comparison_document,
    panel_sha256,
    persistence_logistic_exceedance,
    rolling_exceedance_backtest,
)
from repo_model.data import DailyObservation, audit_panel, exceeds_bp, load_daily_panel  # noqa: E402
from repo_model.dvp_segment import (  # noqa: E402
    BENCHMARKS,
    FAMILY_LEVEL,
    FULL_WINDOW,
    GROUPS,
    HORIZONS,
    OFR_DVP_RATE_FIELD,
    OFR_WINDOW,
    ONSET,
    ONSET_BP,
    P_VALUE_REPLICATIONS,
    POOLED,
    SENSITIVITIES,
    STRESS_REGIMES,
    THRESHOLDS,
    comparison_key,
)
from repo_model.evaluation_splits import load_split_declaration  # noqa: E402
from repo_model.metrics import stationary_bootstrap_interval  # noqa: E402

REGISTRY = v1.REGISTRY
SPLITS = v1.SPLITS
SNAPSHOTS = ew.SNAPSHOTS
END = v1.END
INTERVAL_LEVEL = 0.90
INTERVAL_REPLICATIONS = 2000

RAW_COLUMNS = ("bgcr_volume", "ofr_dvp_rate")
EW_COLUMNS = ("sofr_tgcr_bps", "bgcr_tgcr_bps")
DVP_COLUMNS = tuple(dvp_segment.COLUMN_FIELDS)
#: Each candidate's columns.
COLUMNS = {candidate.name: candidate.columns for candidate in dvp_segment.CANDIDATES}
WINDOWS = {"full": FULL_WINDOW, "ofr": OFR_WINDOW}


def _proxy(mapping):
    return MappingProxyType(mapping)


copyreg.pickle(MappingProxyType, lambda proxy: (_proxy, (dict(proxy),)))


@contextlib.contextmanager
def switched_on():
    """The candidates' columns in the feature map, for this run only."""

    fields = {
        **{name: early_warning.COLUMN_FIELDS[name] for name in EW_COLUMNS},
        **dvp_segment.COLUMN_FIELDS,
    }
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


# -- runs ------------------------------------------------------------------------


def _window_name(window):
    return "ofr" if window == OFR_WINDOW else "full"


def spec(name):
    """`(columns, window name, release lag days or None)` of one run name."""

    base, _, window = name.partition("@")
    if base in ("control", "persistence_logistic") and window in WINDOWS:
        return (), window, None
    groups = {group.name: group for group in GROUPS}
    if name in groups:
        group = groups[name]
        columns = tuple(c for item in group.inputs for c in COLUMNS[item])
        return columns, _window_name(group.window), None
    sensitivities = {s.name: s for s in SENSITIVITIES}
    if name in sensitivities:
        sensitivity = sensitivities[name]
        columns, _w, _l = spec(sensitivity.group)
        swap = dict(sensitivity.replaces)
        columns = tuple(swap.get(c, c) for c in columns)
        return columns, _window_name(sensitivity.window), sensitivity.release_lag_days
    raise SystemExit(f"unknown run {name!r}")


def run_names():
    return (
        ["control@full", "control@ofr", "persistence_logistic@full", "persistence_logistic@ofr"]
        + [group.name for group in GROUPS]
        + [s.name for s in SENSITIVITIES]
    )


def _rows(panel, window):
    rows = load_daily_panel(panel)
    if window == "ofr":
        rows = [row for row in rows if row.date >= OFR_WINDOW[0]]
    audit_panel(rows)
    return rows


def _registry(lag_days):
    registry = json.loads(REGISTRY.read_text())
    if lag_days is not None:
        registry[dvp_segment.OFR_SOURCE_ID]["release_lag"]["days"] = lag_days
    return registry


def run_command(args) -> int:
    from repo_model import ml
    from repo_model.data import load_stress_thresholds
    from repo_model.recalibration import NestedFoldPid

    columns, window, lag = spec(args.run)
    rows = _rows(args.panel, window)
    splits = load_split_declaration(SPLITS)
    taus = tuple(float(tau) for tau in load_stress_thresholds(v1.THRESHOLDS)["taus_bp"])
    h = args.horizon
    registry = _registry(lag)
    built = []

    def online(rows_, rule):
        built.append(NestedFoldPid(rows_, rule, splits=splits, refit_every=v1.REFIT_EVERY))
        return built[-1]

    def backtest(name, predictor, features, calibration=None):
        return rolling_exceedance_backtest(
            rows,
            predictor=predictor,
            model_name=name,
            features=features,
            registry=registry,
            decision_time=v1.DECISION,
            taus=taus,
            minimum_history=v1.MINIMUM_HISTORY,
            refit_every=v1.REFIT_EVERY,
            end=END,
            horizon=h,
            online_calibration=calibration,
        )

    with switched_on():
        if args.run.startswith("persistence_logistic@"):
            features = ("spread_bps",)
            report = backtest(
                "persistence_logistic",
                persistence_logistic_exceedance(minimum_history=v1.MINIMUM_HISTORY),
                features,
            )
        else:
            features = v1._at_horizon(v1.GBM_FEATURES, h) + columns
            raw = backtest(
                args.run,
                ml.gbm_exceedance(
                    tuple(name for name in features if name != "spread_bps"),
                    minimum_history=v1.MINIMUM_HISTORY,
                ),
                features,
                online,
            )
            report = v1._rescored(pressure.recalibrated(raw))
    document = {
        "run": args.run,
        "horizon": h,
        "window": window,
        "release_lag_days": lag,
        "features": list(features),
        "panel_sha256": panel_sha256(args.panel),
        "panel_first": rows[0].date.isoformat(),
        "report": report,
        "calibration_account": built[0].account() if built else None,
    }
    args.output.write_bytes(pickle.dumps(document))
    print(json.dumps({
        "run": args.run, "horizon": h, "window": window, "first": report.scored_dates[0].isoformat(),
        "last": report.scored_dates[-1].isoformat(), "days": len(report.scored_dates),
    }))
    return 0


def crps_command(args) -> int:
    from repo_model import cli

    columns, window, lag = spec(args.run)

    def side(letter, features):
        out = ["--model-" + letter, "gbm", "--calibration-" + letter, "conformal_pid_nested"]
        for name in features:
            out += ["--feature-" + letter, name]
        return out

    with tempfile.TemporaryDirectory() as scratch:
        panel = args.panel
        if window == "ofr":
            panel = Path(scratch) / "panel.csv"
            with Path(args.panel).open(newline="", encoding="utf-8") as source, panel.open(
                "w", newline="", encoding="utf-8"
            ) as target:
                reader, writer = csv.reader(source), csv.writer(target, lineterminator="\n")
                writer.writerow(next(reader))
                for line in reader:
                    if date.fromisoformat(line[0]) >= OFR_WINDOW[0]:
                        writer.writerow(line)
        registry = Path(scratch) / "sources.json"
        registry.write_text(json.dumps(_registry(lag), indent=2), encoding="utf-8")
        argv = [
            "compare", str(panel),
            "--registry", str(registry), "--decision-time", "16:00",
            "--minimum-history", str(v1.MINIMUM_HISTORY), "--refit-every", str(v1.REFIT_EVERY),
            "--end", END.isoformat(), "--splits", str(SPLITS), "--loss", "crps",
            *side("a", v1.GBM_FEATURES), *side("b", v1.GBM_FEATURES + columns),
            "--report", str(args.output),
        ]
        with switched_on():
            status = cli.main(argv)
    document = json.loads(args.output.read_text())
    document["dvp_segment"] = {"run": args.run, "window": window, "release_lag_days": lag}
    args.output.write_text(json.dumps(document, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    return status


# -- the scratch panel -------------------------------------------------------------


def panel_command(args) -> int:
    rows = load_daily_panel(args.panel)
    funding = ew._series(SNAPSHOTS / "funding_inputs", {"SOFR_volume", "BGCR_volume"})
    ofr = ew._series(SNAPSHOTS / "ofr_inputs", {OFR_DVP_RATE_FIELD})[OFR_DVP_RATE_FIELD]
    for row in rows:
        parsed = funding["SOFR_volume"].get(row.date)
        if parsed is None or abs(parsed - row.values["sofr_volume"]) > 1e-9:
            raise SystemExit(f"{row.date}: parsed SOFR volume differs from the panel's")
    added = []
    holes = {name: [] for name in RAW_COLUMNS}
    for row in rows:
        if row.date > END:
            continue
        values = dict(row.values)
        values["bgcr_volume"] = funding["BGCR_volume"].get(row.date)
        values["ofr_dvp_rate"] = ofr.get(row.date)
        for name in RAW_COLUMNS:
            if values[name] is None:
                holes[name].append(row.date.isoformat())
        added.append(DailyObservation(row.date, values))
    with_ew = early_warning.build_columns(added)
    built = dvp_segment.build_columns(
        [
            DailyObservation(row.date, {**added[i].values, **{c: row.values[c] for c in EW_COLUMNS}})
            for i, row in enumerate(with_ew)
        ]
    )
    header = list(ew.load_header(args.panel)) + list(RAW_COLUMNS) + list(EW_COLUMNS) + list(DVP_COLUMNS)
    header = list(dict.fromkeys(header))
    with args.output.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerow(header)
        for row in built:
            writer.writerow([row.date.isoformat()] + [ew._cell(row.values.get(name)) for name in header[1:]])
    summary = {
        "output": str(args.output),
        "sha256": hashlib.sha256(args.output.read_bytes()).hexdigest(),
        "rows": len(built),
        "first": built[0].date.isoformat(),
        "last": built[-1].date.isoformat(),
        "raw_holes": {
            "bgcr_volume": holes["bgcr_volume"],
            "ofr_dvp_rate_from_2020_09_09": [d for d in holes["ofr_dvp_rate"] if d >= OFR_WINDOW[0].isoformat()],
            "ofr_dvp_rate_before_2020_09_09": len(
                [d for d in holes["ofr_dvp_rate"] if d < OFR_WINDOW[0].isoformat()]
            ),
        },
        "missing": {
            name: sum(1 for row in built if row.values.get(name) is None)
            for name in EW_COLUMNS + DVP_COLUMNS
        },
    }
    print(json.dumps(summary, indent=1))
    return 0


# -- the descriptive check ------------------------------------------------------------


def _correlation(xs, ys):
    pairs = [(x, y) for x, y in zip(xs, ys) if x is not None and y is not None]
    n = len(pairs)
    mx = sum(x for x, _ in pairs) / n
    my = sum(y for _, y in pairs) / n
    sxy = sum((x - mx) * (y - my) for x, y in pairs)
    sxx = sum((x - mx) ** 2 for x, _ in pairs)
    syy = sum((y - my) ** 2 for _, y in pairs)
    return {"correlation": sxy / (sxx * syy) ** 0.5, "days": n}


def check_command(args) -> int:
    rows = load_daily_panel(args.panel)
    ofr = ew._series(
        SNAPSHOTS / "ofr_inputs", {"REPO-DVP_AR_OO-P", "REPO-DVP_AR_OO-F", "REPO-DVP_TV_OO-F"}
    )
    dates = [row.date for row in rows]
    rebuilt = [
        None if row.values.get("bgcr_volume") is None else row.values["sofr_volume"] - row.values["bgcr_volume"]
        for row in rows
    ]
    ofr_volume = [
        None if ofr["REPO-DVP_TV_OO-F"].get(d) is None else ofr["REPO-DVP_TV_OO-F"][d] / 1e9 for d in dates
    ]

    def changes(series):
        return [
            None if a is None or b is None else b - a for a, b in zip(series[:-1], series[1:])
        ]

    def before(series, cut):
        return [value if d < cut else None for d, value in zip(dates, series)]

    sofr_bgcr = [(row.values["sofr"] - row.values["bgcr"]) * 100.0 for row in rows]
    final_minus_bgcr = [
        None if ofr["REPO-DVP_AR_OO-F"].get(d) is None else (ofr["REPO-DVP_AR_OO-F"][d] - row.values["bgcr"]) * 100.0
        for d, row in zip(dates, rows)
    ]
    both = [
        d for d in dates
        if d in ofr["REPO-DVP_AR_OO-P"] and d in ofr["REPO-DVP_AR_OO-F"]
    ]
    identical = sum(
        1 for d in both if abs(ofr["REPO-DVP_AR_OO-P"][d] - ofr["REPO-DVP_AR_OO-F"][d]) < 1e-12
    )
    document = {
        "window": {"first": dates[0].isoformat(), "last": dates[-1].isoformat()},
        "volume": {
            "level": _correlation(rebuilt, ofr_volume),
            "level_before_2020_09_01": _correlation(
                before(rebuilt, date(2020, 9, 1)), before(ofr_volume, date(2020, 9, 1))
            ),
            "daily_change": _correlation(changes(rebuilt), changes(ofr_volume)),
        },
        "rate": {
            "sofr_minus_bgcr_vs_ofr_dvp_final_minus_bgcr": _correlation(sofr_bgcr, final_minus_bgcr),
            "same_2018_19": _correlation(
                [v if d.year <= 2019 else None for d, v in zip(dates, sofr_bgcr)],
                [v if d.year <= 2019 else None for d, v in zip(dates, final_minus_bgcr)],
            ),
        },
        "preliminary_vs_final": {"days_with_both": len(both), "identical": identical},
    }
    args.output.write_text(json.dumps(document, indent=1) + "\n", encoding="utf-8")
    print(json.dumps(document, indent=1))
    return 0


# -- assembly -----------------------------------------------------------------


def _load(directory, name, h):
    return pickle.loads((directory / f"{name}_h{h}.pickle").read_bytes())


def _benches(window):
    return {"pressure_model_v1": f"control@{window}", "persistence_logistic": f"persistence_logistic@{window}"}


def _brier(report, tau):
    position = report.taus.index(tau)
    forecast, _, outcomes = report.at_tau(position)
    return [(p - y) ** 2 for p, y in zip(forecast, outcomes)]


def _interval(values, block, seed):
    lower, upper = stationary_bootstrap_interval(
        lambda idx: sum(values[i] for i in idx) / len(idx),
        len(values), block_length=block, seed=seed,
        replications=INTERVAL_REPLICATIONS, level=INTERVAL_LEVEL,
    )
    return {"lower": lower, "upper": upper, "block_length": block, "seed": seed,
            "replications": INTERVAL_REPLICATIONS, "level": INTERVAL_LEVEL}


def assemble_command(args) -> int:
    from repo_model import ml

    rows = load_daily_panel(args.panel)
    previous = {rows[i].date: rows[i - 1] for i in range(1, len(rows))}
    splits = load_split_declaration(SPLITS)
    digest = panel_sha256(args.panel)
    names = [group.name for group in GROUPS] + [s.name for s in SENSITIVITIES]

    entries = {}  # comparison key -> entry
    grids = {}  # grid -> [(key, daily differences)]
    detail = {}
    for name in names:
        _columns, window, _lag = spec(name)
        detail[name] = {"window": window, "by_horizon": {}}
        for h in HORIZONS:
            candidate = _load(args.runs, name, h)["report"]
            onset = [
                i for i, when in enumerate(candidate.scored_dates)
                if when in previous and not exceeds_bp(previous[when].spread_bps, ONSET_BP)
            ]
            per_h = detail[name]["by_horizon"][str(h)] = {}
            for bench_name, run in _benches(window).items():
                bench = _load(args.runs, run, h)["report"]
                document = benchmark_comparison_document(
                    candidate, bench, panel_sha256=digest, rows=rows, declaration=splits
                )
                per_h[bench_name] = {}
                for tau in THRESHOLDS:
                    paired = document["by_tau"][f"{tau:g}"]["paired_brier_difference"]
                    differences = [
                        b - c for b, c in zip(_brier(bench, tau), _brier(candidate, tau))
                    ]
                    if abs(sum(differences) / len(differences) - paired["mean"]) > 1e-12:
                        raise SystemExit(f"{name} h{h} {bench_name} {tau}: daily differences disagree")
                    block = paired["interval"]["block_length"]
                    pooled_key = comparison_key(name, "brier", POOLED, tau, h, bench_name)
                    entries[pooled_key] = {
                        "mean": paired["mean"],
                        "interval": paired["interval"],
                        "days": len(differences),
                        "regimes": {
                            label: paired["splits"]["by_regime"].get(label, {}).get("mean")
                            for label in STRESS_REGIMES
                        },
                        "splits": paired["splits"],
                    }
                    grids.setdefault((window, h, POOLED, block), []).append((pooled_key, differences))
                    onset_differences = [differences[i] for i in onset]
                    onset_key = comparison_key(name, "brier", ONSET, tau, h, bench_name)
                    entries[onset_key] = {
                        "mean": sum(onset_differences) / len(onset_differences),
                        "interval": _interval(
                            onset_differences, block, dvp_segment.p_value_seed(window, h, ONSET, "interval")
                        ),
                        "days": len(onset_differences),
                        "events": sum(
                            1 for i in onset if exceeds_bp(candidate.realized_bps[i], tau)
                        ),
                    }
                    grids.setdefault((window, h, ONSET, block), []).append((onset_key, onset_differences))
                    per_h[bench_name][f"{tau:g}"] = {
                        "candidate_brier": sum(_brier(candidate, tau)) / len(differences),
                        "benchmark_brier": sum(_brier(bench, tau)) / len(differences),
                        "first": candidate.scored_dates[0].isoformat(),
                        "last": candidate.scored_dates[-1].isoformat(),
                    }
        crps = json.loads((args.runs / f"crps_{name}.json").read_text())["comparison"]
        crps_key = comparison_key(name, "crps")
        per_origin = [origin["difference_bps"] for origin in crps["per_origin"]]
        last = max(origin["scored_date"] for origin in crps["per_origin"])
        if last > END.isoformat():
            raise SystemExit(f"{name}: CRPS scored a locked day")
        entries[crps_key] = {
            "mean": crps["mean_difference_bps"],
            "interval": crps["mean_difference_interval"],
            "days": crps["origin_count"],
            "control_crps_bps": crps["model_a"]["crps_bps"],
            "candidate_crps_bps": crps["model_b"]["crps_bps"],
            "first": min(origin["scored_date"] for origin in crps["per_origin"]),
            "last": last,
            "splits": crps.get("splits"),
        }
        grids.setdefault((window, 1, "crps", crps["mean_difference_interval"]["block_length"]), []).append(
            (crps_key, per_origin)
        )

    for (window, h, day_set, block), members in sorted(grids.items(), key=lambda item: str(item[0])):
        lengths = {len(values) for _key, values in members}
        if len(lengths) != 1:
            raise SystemExit(f"grid {window} h{h} {day_set}: lengths {sorted(lengths)}")
        p_values = ml.paired_bootstrap_p_values(
            [values for _key, values in members],
            block_length=block,
            seed=dvp_segment.p_value_seed(window, h, day_set),
            replications=P_VALUE_REPLICATIONS,
        )
        for (key, _values), (p_improve, p_worse) in zip(members, p_values):
            entries[key]["p_improve"] = p_improve
            entries[key]["p_worse"] = p_worse

    family = {key for key in entries if key.split("|", 1)[0] in {g.name for g in GROUPS}}
    if len(family) != dvp_segment.family_size():
        raise SystemExit(f"family has {len(family)} comparisons, declared {dvp_segment.family_size()}")
    improve = dvp_segment.holm({key: entries[key]["p_improve"] for key in family})
    worse = dvp_segment.holm({key: entries[key]["p_worse"] for key in family})
    for key in entries:
        entries[key]["holm_improve"] = improve.get(key)
        entries[key]["holm_worse"] = worse.get(key)
    outcomes = {
        group.name: dvp_segment.classify(group, {k: entries[k] for k in family})
        for group in GROUPS
    }

    lead, october = _lead_time(args.runs, rows)
    document = {
        "directive": "#187",
        "status": "scratch measurement; not a record, nothing published moves",
        "panel_sha256": digest,
        "family_size": len(family),
        "family_level": FAMILY_LEVEL,
        "p_value_replications": P_VALUE_REPLICATIONS,
        "outcomes": outcomes,
        "comparisons": entries,
        "detail": detail,
        "lead_time": lead,
        "october_2025_onset": october,
    }
    args.output.write_text(json.dumps(document, indent=1, sort_keys=True, default=str) + "\n", encoding="utf-8")
    args.markdown.write_text(_markdown(document), encoding="utf-8")
    print(json.dumps({"output": str(args.output), "markdown": str(args.markdown),
                      "outcomes": {k: v["outcome"] for k, v in outcomes.items()}}))
    return 0


def _lead_time(directory, rows):
    """Lead time to onset (`pressure.onsets`, as #114 and #127) and the October 2025 onset."""

    lead, october = {}, {}
    for window in ("full", "ofr"):
        models = [f"control@{window}", f"persistence_logistic@{window}"] + [
            name for name in [g.name for g in GROUPS] + [s.name for s in SENSITIVITIES]
            if spec(name)[1] == window
        ]
        lead[window], october[window] = {}, {}
        for tau in THRESHOLDS:
            key = f"{tau:g}"
            forecasts = {}
            for name in models:
                forecasts[name] = {}
                for h in HORIZONS:
                    report = _load(directory, name, h)["report"]
                    position = report.taus.index(tau)
                    forecasts[name][h] = {
                        when: curve[position] for when, curve in zip(report.scored_dates, report.forecast)
                    }
            common = sorted(set.intersection(*(set(forecasts[models[0]][h]) for h in HORIZONS)))
            onset_days = pressure.onsets(rows, tau, common)
            lead[window][key] = {
                "onsets": [d.isoformat() for d in onset_days],
                "by_model": {
                    name: [pressure.lead_times(forecasts[name], onset_days, level) for level in pressure.ALARM_LEVELS]
                    for name in models
                },
            }
            october[window][key] = {
                name: {
                    d.isoformat(): {str(h): forecasts[name][h].get(d) for h in HORIZONS}
                    for d in onset_days if d.year == 2025 and d.month == 10
                }
                for name in models
            }
    return lead, october


# -- tables -------------------------------------------------------------------------


def _iv(entry, places=4):
    interval = entry["interval"]
    return f"{entry['mean']:+.{places}f} [{interval['lower']:+.{places}f}, {interval['upper']:+.{places}f}]"


def _p(entry):
    mark = " ✓" if entry.get("holm_improve") else (" ✗" if entry.get("holm_worse") else "")
    return f"{entry['p_improve']:.4f}{mark}"


def _markdown(document) -> str:
    entries = document["comparisons"]
    out = []
    out.append(
        f"Family: {document['family_size']} comparisons; Holm at a {document['family_level']:.0%} "
        f"family-wise level on one-sided paired stationary-bootstrap p-values "
        f"({document['p_value_replications']} replications). ✓ = improvement survives the correction; "
        "✗ = significantly worse after it. Paired difference = benchmark − candidate (Brier) or "
        "control − candidate (CRPS, bp): positive favours the input. 90% stationary-bootstrap intervals.\n"
    )
    out.append("### Outcome, by the win rule fixed before scoring\n")
    out.append("| Group | Window | Outcome | +5 bp | +10 bp |")
    out.append("|---|---|---|---|---|")
    for group in GROUPS:
        verdict = document["outcomes"][group.name]
        cells = []
        for tau in ("5", "10"):
            t = verdict["by_threshold"][tau]
            missed = [k.split("_", 1)[0] for k, v in t["conditions"].items() if not v]
            cells.append(
                f"{t['outcome']}; survives at h={t['horizons_surviving_correction'] or '–'}; "
                f"misses {', '.join(missed) or 'none'}"
            )
        out.append(
            f"| {group.name} | {_window_name(group.window)} | **{verdict['outcome']}** | " + " | ".join(cells) + " |"
        )
    out.append("")
    for day_set, title in ((POOLED, "all scored days"), (ONSET, "onset days (#160)")):
        out.append(f"### Brier, {title}: paired difference [90% interval], one-sided p for improvement\n")
        out.append("| Group | h | +5 vs v1 | p | +5 vs persistence-logistic | p | +10 vs v1 | p | +10 vs persistence-logistic | p |")
        out.append("|---|---|---|---|---|---|---|---|---|---|")
        for name in [g.name for g in GROUPS] + [s.name for s in SENSITIVITIES]:
            for h in HORIZONS:
                cells = []
                for tau in THRESHOLDS:
                    for bench in BENCHMARKS:
                        entry = entries[comparison_key(name, "brier", day_set, tau, h, bench)]
                        cells += [_iv(entry), _p(entry)]
                out.append(f"| {name} | {h} | " + " | ".join(cells) + " |")
        out.append("")
    out.append("### CRPS, horizon 1: control − candidate, bp\n")
    out.append("| Run | Scored | CRPS control | CRPS candidate | Difference | p improve | p worse |")
    out.append("|---|---|---|---|---|---|---|")
    for name in [g.name for g in GROUPS] + [s.name for s in SENSITIVITIES]:
        entry = entries[comparison_key(name, "crps")]
        out.append(
            f"| {name} | {entry['first']} to {entry['last']} ({entry['days']}) | {entry['control_crps_bps']:.4f} | "
            f"{entry['candidate_crps_bps']:.4f} | {_iv(entry)} | {_p(entry)} | {entry['p_worse']:.4f} |"
        )
    out.append("")
    out.append("### Lead time to onset (`pressure.onsets`), alarm levels 0.2 and 0.5\n")
    for window, by_tau in document["lead_time"].items():
        for tau, entry in by_tau.items():
            out.append(f"**{window} window, +{tau} bp**: {len(entry['onsets'])} onsets\n")
            out.append("| Run | flagged at 0.2 | mean lead at 0.2 | flagged at 0.5 | mean lead at 0.5 |")
            out.append("|---|---|---|---|---|")
            for name, (low, high) in entry["by_model"].items():
                out.append(
                    f"| {name} | {low['flagged']}/{low['onsets']} | {low['mean_lead_days']:.2f} | "
                    f"{high['flagged']}/{high['onsets']} | {high['mean_lead_days']:.2f} |"
                )
            out.append("")
    out.append("### The October 2025 onset: probability forecast of the onset day, h = 1 to 5\n")
    for window, by_tau in document["october_2025_onset"].items():
        for tau, by_model in by_tau.items():
            days = sorted({d for model in by_model.values() for d in model})
            for day in days:
                out.append(f"**{window} window, +{tau} bp, onset {day}**\n")
                out.append("| Run | h=1 | h=2 | h=3 | h=4 | h=5 |\n|---|---|---|---|---|---|")
                for name, by_day in by_model.items():
                    values = by_day.get(day, {})
                    out.append(f"| {name} | " + " | ".join(
                        "–" if values.get(str(h)) is None else f"{values[str(h)]:.3f}" for h in HORIZONS) + " |")
                out.append("")
    return "\n".join(out) + "\n"


def splits_markdown(document) -> str:
    """Every pooled Brier comparison by regime and pressure-day type (a separate page: it is long)."""

    entries = document["comparisons"]
    out = []
    for tau in THRESHOLDS:
        for bench in BENCHMARKS:
            out.append(f"### +{tau:g} bp against {bench}: by regime and pressure-day type\n")
            first = entries[comparison_key(GROUPS[0].name, "brier", POOLED, tau, 1, bench)]["splits"]
            columns = [("by_regime", k) for k in first["by_regime"]] + [("by_day_type", k) for k in first["by_day_type"]]
            out.append("| Group | h | " + " | ".join(c for _g, c in columns) + " |")
            out.append("|---|---|" + "---|" * len(columns))
            for name in [g.name for g in GROUPS] + [s.name for s in SENSITIVITIES]:
                for h in HORIZONS:
                    s = entries[comparison_key(name, "brier", POOLED, tau, h, bench)]["splits"]
                    out.append(f"| {name} | {h} | " + " | ".join(ew._iv(s[g].get(c)) for g, c in columns) + " |")
            out.append("")
    return "\n".join(out) + "\n"


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="command", required=True)
    one = sub.add_parser("panel")
    one.add_argument("--panel", type=Path, required=True)
    one.add_argument("--output", type=Path, required=True)
    one.set_defaults(handler=panel_command)
    two = sub.add_parser("check")
    two.add_argument("--panel", type=Path, required=True)
    two.add_argument("--output", type=Path, required=True)
    two.set_defaults(handler=check_command)
    three = sub.add_parser("run")
    three.add_argument("--panel", type=Path, required=True)
    three.add_argument("--run", choices=run_names(), required=True)
    three.add_argument("--horizon", type=int, choices=HORIZONS, required=True)
    three.add_argument("--output", type=Path, required=True)
    three.set_defaults(handler=run_command)
    four = sub.add_parser("crps")
    four.add_argument("--panel", type=Path, required=True)
    four.add_argument("--run", choices=[n for n in run_names() if "@" not in n or n.split("@")[1] in ("lag1", "backfill")], required=True)
    four.add_argument("--output", type=Path, required=True)
    four.set_defaults(handler=crps_command)
    five = sub.add_parser("assemble")
    five.add_argument("--panel", type=Path, required=True)
    five.add_argument("--runs", type=Path, required=True)
    five.add_argument("--output", type=Path, required=True)
    five.add_argument("--markdown", type=Path, required=True)
    five.add_argument("--splits-markdown", type=Path, default=None)
    five.set_defaults(handler=lambda a: _assemble_and_splits(a))
    args = parser.parse_args(argv)
    return args.handler(args)


def _assemble_and_splits(args) -> int:
    status = assemble_command(args)
    if args.splits_markdown is not None:
        document = json.loads(args.output.read_text())
        args.splits_markdown.write_text(splits_markdown(document), encoding="utf-8")
    return status


if __name__ == "__main__":
    raise SystemExit(main())
