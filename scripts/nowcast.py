"""A same-day nowcast of the unpublished day (#445): the scratch measurement.

A scratch measurement, not a record: it writes CSV and JSON to the paths it is given and nothing into
`docs/runs/`. The candidates, the primary nowcast, the ridge setting, the turning-point definition and the
lag statistic are in `metadata/nowcast.json`, the availability of every input in
`metadata/sources_measurement.json` and the pressure candidate in `metadata/pressure_judge.json`; every
command that scores refuses a declaration that is not committed and unchanged. The columns are off in every
published declaration and switched on for these runs only. Scored days are 2018-06-29 to 2025-12-31
(`docs/decisions/lockbox.md`); the 2026 window is not looked at and the scratch panel stops at 2025-12-31.

    PYTHONPATH=src python3 -m repo_model.cli build --raw-root tests/fixtures/snapshots/funding_inputs \\
        --output PUB.csv --build-cutoff 2026-09-08T21:31:42+00:00 --decision-time 16:00:00
    PYTHONPATH=src python3 scripts/nowcast.py panel --panel PUB.csv --output NC.csv --summary OUT/panel.json
    PYTHONPATH=src python3 scripts/nowcast.py accuracy --panel NC.csv --output OUT/accuracy.json
    for W in persistence control variant: OMP_NUM_THREADS=1 PYTHONPATH=src /opt/rmm-venv/bin/python \\
        scripts/nowcast.py walk --panel NC.csv --which $W --output OUT/walk_$W.json
    PYTHONPATH=src python3 scripts/nowcast.py score --panel NC.csv --output OUT/score.json \\
        OUT/walk_persistence.json OUT/walk_control.json OUT/walk_variant.json
    for H in 1 2 3 4 5: PYTHONPATH=src python3 scripts/pressure_judge.py forecasts --panel NC.csv --horizon $H \\
        --published --output OUT/bench_h$H.json
    for H in 1 2 3 4 5: OMP_NUM_THREADS=1 PYTHONPATH=src /opt/rmm-venv/bin/python scripts/nowcast.py pressure \\
        --panel NC.csv --horizon $H --output OUT/nowcast_h$H.json
    PYTHONPATH=src python3 scripts/pressure_judge.py judge --panel NC.csv --output OUT/judge.json \\
        --markdown OUT/judge.md OUT/bench_h?.json OUT/nowcast_h?.json
    PYTHONPATH=src python3 scripts/nowcast.py pair --panel NC.csv --output OUT/pair.json OUT/bench_h?.json OUT/nowcast_h?.json

* `panel` adds the same-day reverse repo and every candidate's nowcast to the published panel's rows.
* `accuracy` scores each nowcast against the actual spread of its own day and against the naive nowcast.
* `walk` is the published distribution's walk (`final_test_opening.distribution_walk`) at h = 1 for
  the persistence side, the published side (`control`, which reproduces the published record exactly) and the
  published side with one more feature, the primary nowcast (`variant`).
* `score` scores the three walks: the CRPS, the lag, the turning-point days, each paired and split.
* `pressure` is the published pressure classifier (`pressure_judge._published`) with one more feature.
* `pair` is the variant's paired Brier difference against the published classifier.
"""

from __future__ import annotations

import argparse
import contextlib
import csv
import hashlib
import importlib.util
import json
import math
import subprocess
import sys
from datetime import date, time
from operator import itemgetter
from pathlib import Path
from types import MappingProxyType
from unittest import mock

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))

from repo_model import contract, measurement_fields, nowcast  # noqa: E402
from repo_model import pressure, pressure_judge as pj  # noqa: E402
from repo_model.baseline import panel_sha256  # noqa: E402
from repo_model.data import DailyObservation, audit_panel, exceeds_bp, load_daily_panel  # noqa: E402
from repo_model.evaluation_splits import load_split_declaration  # noqa: E402
from repo_model.lockbox import require_unlocked  # noqa: E402
from repo_model.metrics import crps_from_quantiles, stationary_bootstrap_interval  # noqa: E402

DECLARATION = REPO / "metadata" / "nowcast.json"
SPLITS = REPO / "metadata" / "evaluation_splits.json"
SNAPSHOT = REPO / "tests" / "fixtures" / "snapshots" / "on_rrp_inputs" / "nyfed_on_rrp"
DAILY_RECORD = REPO / "docs" / "runs" / "published_distribution_daily_h1.json"
END = date(2025, 12, 31)
MINIMUM_HISTORY, REFIT_EVERY = 61, 21
VARIANT = "published_v1_nowcast"
VARIANT_SUBSTITUTED = "published_v1_nowcast_substituted"
CONTROL = "published_v1"


def _script(name):
    spec = importlib.util.spec_from_file_location(name, REPO / "scripts" / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def committed(path: Path) -> str:
    """The commit that last changed `path`, refused unless it is committed and unchanged since `HEAD`."""

    relative = str(path.resolve().relative_to(REPO))
    dirty = subprocess.run(
        ["git", "status", "--porcelain", "--", relative], cwd=REPO, capture_output=True, text=True, check=True
    ).stdout.strip()
    if dirty:
        raise SystemExit(f"{relative} is not committed ({dirty}); a declaration is made before any score")
    return subprocess.run(
        ["git", "log", "-1", "--format=%H", "--", relative], cwd=REPO, capture_output=True, text=True, check=True
    ).stdout.strip()


def declarations_committed() -> dict:
    return {
        str(p.relative_to(REPO)): committed(p)
        for p in (DECLARATION, REPO / "metadata" / "sources_measurement.json", REPO / "metadata" / "pressure_judge.json")
    }


@contextlib.contextmanager
def switched_on():
    """The nowcast columns in the feature map, for this run only."""

    fields = dict(nowcast.COLUMN_FIELDS)
    with mock.patch.multiple(
        contract,
        FEATURE_FIELDS=MappingProxyType({**contract.FEATURE_FIELDS, **fields}),
        FEATURE_SOURCES=MappingProxyType(
            {
                **contract.FEATURE_SOURCES,
                **{column: tuple(sorted({source for source, _f in pairs})) for column, pairs in fields.items()},
            }
        ),
    ):
        yield


@contextlib.contextmanager
def substituted():
    """The nowcast fed to the unchanged model as its latest spread, for this run only (the amendment).

    Every feature row `InformationRule.observation` hands a model carries, as its SOFR, the IORB it read plus
    the nowcast it read, so the model's latest spread is the nowcast of the day before the target. The
    nowcast is a declared feature of the rule, so its read passes the same guards as every other.
    """

    from repo_model.asof import InformationRule

    original = InformationRule.observation

    def observation(self, rows, info):
        row = original(self, rows, info)
        if any(group.feature == nowcast.NOWCAST_COLUMN for group in self.groups):
            return nowcast.substitute_latest_spread(row)
        return row

    with mock.patch.object(InformationRule, "observation", observation):
        yield


def _cell(value):
    return "" if value is None else repr(float(value))


def _scored_days():
    """The days the published record scores, 2018-06-29 to 2025-12-31, with their actual spreads."""

    document = json.loads(DAILY_RECORD.read_text(encoding="utf-8"))
    return [d for d in document["days"] if d["date"] <= END.isoformat()]


# -- the panel ---------------------------------------------------------------


def panel_command(args) -> int:
    declarations_committed()
    declaration = nowcast.load_declaration(DECLARATION)
    rows = [row for row in load_daily_panel(args.panel) if row.date <= END]
    operations = nowcast.load_operations(SNAPSHOT)
    values, excluded = nowcast.sameday_on_rrp(operations)
    built, walks = nowcast.with_nowcast(rows, values, declaration)
    panel_days = {row.date for row in rows}
    with args.panel.open(newline="", encoding="utf-8") as handle:
        base = next(csv.reader(handle))
    added = [nowcast.RRP_COLUMN] + [f"nowcast_{name}" for name in declaration.candidates] + [nowcast.NOWCAST_COLUMN]
    header = list(dict.fromkeys(base + added))
    with args.output.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerow(header)
        for row in built:
            writer.writerow([row.date.isoformat()] + [_cell(row.values.get(name)) for name in header[1:]])
    scored_first = date.fromisoformat("2018-06-29")
    scored = [r for r in built if r.date >= scored_first]
    summary = {
        "output": str(args.output),
        "sha256": hashlib.sha256(args.output.read_bytes()).hexdigest(),
        "rows": len(built),
        "first": built[0].date.isoformat(),
        "last": built[-1].date.isoformat(),
        "reverse_repo": {
            "panel_days_admitted": sum(1 for r in built if r.values[nowcast.RRP_COLUMN] is not None),
            "panel_days_without_a_value": sum(1 for r in built if r.values[nowcast.RRP_COLUMN] is None),
            "scored_days_without_a_value": sum(1 for r in scored if r.values[nowcast.RRP_COLUMN] is None),
            "excluded_panel_days_by_reason": {
                reason: sorted(d.isoformat() for d, why in excluded.items() if why == reason and d in panel_days)
                for reason in sorted(set(excluded.values()))
            },
        },
        "candidates": {
            name: {
                "first_fitted": None if walk.first_fitted is None else built[walk.first_fitted].date.isoformat(),
                "refits": len(walk.refits),
                "rows_by_status": dict(walk.counts),
                "scored_rows_by_status": {
                    label: sum(
                        1 for i, r in enumerate(built) if r.date >= scored_first and walk.status[i] == label
                    )
                    for label in sorted(set(walk.status))
                },
            }
            for name, walk in walks.items()
        },
    }
    if args.summary:
        args.summary.write_text(json.dumps(summary, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=1, sort_keys=True))
    return 0


# -- shared statistics ---------------------------------------------------------


def _groups(days, rows_by_date, splits):
    """The declared splits of each scored day: regime, pressure-day type, and the +5 bp outcome."""

    regime, day_type, pressure_day = [], [], []
    for d in days:
        when = date.fromisoformat(d)
        row = rows_by_date[when]
        regime.append(splits.regime(when))
        day_type.append(splits.reporting_day_type(when, row.values))
        pressure_day.append("pressure day (> +5 bp)" if exceeds_bp(row.spread_bps, 5) else "other days")
    return {"regime": regime, "day_type": day_type, "outcome": pressure_day}


def _cells(groups, extra=None):
    n = len(next(iter(groups.values())))
    cells = {"all": list(range(n))}
    for dimension, labels in groups.items():
        for label in sorted(set(labels)):
            cells[f"{dimension}: {label}"] = [i for i, g in enumerate(labels) if g == label]
    for label, flags in (extra or {}).items():
        cells[label] = [i for i, flag in enumerate(flags) if flag]
    return cells


def _mean_with_interval(values, interval_spec):
    n = len(values)
    mean = sum(values) / n if n else None
    if n < 2 or not any(v != values[0] for v in values):
        return {"days": n, "mean": mean, "interval": [mean, mean] if n else None}

    def statistic(indices, values=values):
        return sum(values[i] for i in indices) / len(indices)

    low, high = stationary_bootstrap_interval(
        statistic, n, block_length=interval_spec["block_length"], seed=interval_spec["seed"],
        replications=interval_spec["replications"], level=interval_spec["level"],
    )
    return {"days": n, "mean": mean, "interval": [low, high]}


def _paired(gain, cells, interval_spec):
    return {label: _mean_with_interval([gain[i] for i in members], interval_spec) for label, members in cells.items()}


# -- the nowcast's own accuracy ------------------------------------------------


def accuracy_command(args) -> int:
    declarations_committed()
    require_unlocked([END], where="nowcast")
    declaration = nowcast.load_declaration(DECLARATION)
    spec = declaration.raw["distribution"]["interval"]
    rows = load_daily_panel(args.panel)
    audit_panel(rows)
    by_date = {row.date: row for row in rows}
    splits = load_split_declaration(SPLITS)
    days = [d["date"] for d in _scored_days()]
    groups = _groups(days, by_date, splits)
    cells = _cells(groups)
    actual = [by_date[date.fromisoformat(d)].spread_bps for d in days]
    nowcasts = {
        name: [float(by_date[date.fromisoformat(d)].values[f"nowcast_{name}"]) for d in days]
        for name in declaration.candidates
    }
    naive_error = [abs(n - a) for n, a in zip(nowcasts["naive"], actual)]
    naive_square = [(n - a) ** 2 for n, a in zip(nowcasts["naive"], actual)]
    out = {"days": len(days), "first": days[0], "last": days[-1], "candidates": {}}
    for name, series in nowcasts.items():
        error = [abs(n - a) for n, a in zip(series, actual)]
        square = [(n - a) ** 2 for n, a in zip(series, actual)]
        signed = {
            label: sum(n - a for i in members for n, a in [(series[i], actual[i])]) / len(members)
            for label, members in cells.items()
        }
        entry = {
            "mae_bp": sum(error) / len(error),
            "rmse_bp": math.sqrt(sum(square) / len(square)),
            "role": declaration.candidates[name].role,
            "mean_signed_error_bp": signed,
        }
        if name != "naive":
            entry["abs_error_gain_vs_naive"] = _paired([e0 - e for e0, e in zip(naive_error, error)], cells, spec)
            entry["squared_error_gain_vs_naive"] = _paired([s0 - s for s0, s in zip(naive_square, square)], cells, spec)
        out["candidates"][name] = entry
    out["note"] = "gain = the naive nowcast's error minus the candidate's; positive means the candidate is closer"
    args.output.write_text(json.dumps(out, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    for name, e in out["candidates"].items():
        line = f"{name:26s} MAE {e['mae_bp']:.3f} RMSE {e['rmse_bp']:.3f}"
        if "abs_error_gain_vs_naive" in e:
            cell = e["abs_error_gain_vs_naive"]["all"]
            line += f"   |err| gain vs naive {cell['mean']:+.3f} [{cell['interval'][0]:+.3f}, {cell['interval'][1]:+.3f}]"
        print(line)
    return 0


# -- the distribution walks ----------------------------------------------------


def _variant_side(live_record, registry):
    """The published side of `live_record._compare_sides(1)` built with one more feature, the primary nowcast.

    The fitter binds its regressors when it is built, so the feature goes into the command the side is
    parsed from, as `--feature-b`, and nothing else in the command changes: the same model, calibration,
    minimum history, refit cadence, splits and loss. The registry the command names is the published one
    with the measurement sources added, written beside the scratch panel.
    """

    import tempfile

    from repo_model.cli import build_parser
    from repo_model.cli_eval import FITTER_FACTORIES, _online_calibration, _select_fitter, _side

    argv = list(live_record.final_test.CRPS_COMMAND)
    argv[argv.index("--splits") + 1] = str(live_record.SPLITS)
    last = max(i for i, part in enumerate(argv) if part == "--feature-b")
    argv[last + 2 : last + 2] = ["--feature-b", nowcast.NOWCAST_COLUMN]
    with tempfile.TemporaryDirectory() as tmp, switched_on():
        path = Path(tmp) / "registry.json"
        path.write_text(json.dumps(registry), encoding="utf-8")
        argv[argv.index("--registry") + 1] = str(path)
        args = build_parser().parse_args(argv)
        projected, online = _online_calibration(
            _side(args, "b"), FITTER_FACTORIES.get(args.model_b),
            splits=args.splits, refit_every=args.refit_every, side="-b",
        )
        name, fit = _select_fitter(projected, side="-b")
    return f"{name}+{nowcast.NOWCAST_COLUMN}", fit, tuple(args.feature_b), online, args


def walk_command(args) -> int:
    declarations_committed()
    fto = _script("final_test_opening")
    live_record = fto._script("live_record")
    fto.live_record = live_record
    rows = load_daily_panel(args.panel)
    audit_panel(rows)
    if rows[-1].date > END:
        raise SystemExit(f"the scratch panel runs past {END}; a comparison scores only days before 2026-01-01")
    registry = measurement_fields.load_registry()
    if args.which == "oracle":
        # An inadmissible ceiling, never a candidate: the column holds the nowcast row's own actual spread,
        # which is what a perfect nowcast would hold. It shows what closing the lag completely could be worth.
        rows = [DailyObservation(r.date, {**r.values, nowcast.NOWCAST_COLUMN: r.spread_bps}) for r in rows]
    elif args.which == "naive":
        # The check of the substitution: the naive nowcast is the published spread itself.
        rows = [DailyObservation(r.date, {**r.values, nowcast.NOWCAST_COLUMN: r.values["nowcast_naive"]}) for r in rows]
    mode = contextlib.nullcontext()
    if args.which in ("persistence", "control"):
        sides, parsed = live_record._compare_sides(1)
        name, fit, features, online = sides["persistence" if args.which == "persistence" else "published"]
    elif args.design == "feature":
        name, fit, features, online, parsed = _variant_side(live_record, registry)
    else:
        sides, parsed = live_record._compare_sides(1)
        name, fit, base, online = sides["published"]
        features = tuple(base) + (nowcast.NOWCAST_COLUMN,)
        name = f"{name}, latest spread = {nowcast.NOWCAST_COLUMN}"
        mode = substituted()
    with switched_on(), mode:
        walk, levels, settings = fto.distribution_walk(
            rows, fit=fit, features=features, online_calibration=online, registry=registry, horizon=1,
            minimum_history=parsed.minimum_history, refit_every=parsed.refit_every,
        )
    days = [
        {"date": rows[index].date.isoformat(), "quantiles_bps": list(quantiles), "actual_bps": rows[index].spread_bps}
        for index, quantiles in walk
    ]
    document = {
        "which": args.which,
        "design": "published" if args.which in ("persistence", "control") else args.design,
        "model": name,
        "features": list(features),
        "levels": list(levels),
        "panel_sha256": panel_sha256(args.panel),
        "first": days[0]["date"],
        "last": days[-1]["date"],
        "days": days,
    }
    args.output.write_text(json.dumps(document, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"which": args.which, "days": len(days), "first": document["first"], "last": document["last"]}))
    return 0


# -- the distribution score ----------------------------------------------------


def _correlation_from_sums(n, sa, sb, saa, sbb, sab):
    va, vb = saa - sa * sa / n, sbb - sb * sb / n
    if va <= 0 or vb <= 0:
        return None
    return (sab - sa * sb / n) / math.sqrt(va * vb)


class LagTable:
    """The median of each model against the actual spread `k` days earlier, resampled by index.

    One instance holds the arrays for one model and one set of lags; `correlations(indices)` is the
    correlation at every lag on a resample of the days.
    """

    def __init__(self, medians, actual_series, positions, lags):
        self.lags = list(lags)
        self.arrays = {}
        for k in self.lags:
            a = [actual_series[p - k] for p in positions]
            m = list(medians)
            self.arrays[k] = (m, a, [x * x for x in m], [y * y for y in a], [x * y for x, y in zip(m, a)])

    def correlations(self, indices):
        n = len(indices)
        getter = itemgetter(*indices) if n > 1 else (lambda arr: (arr[indices[0]],))
        out = {}
        for k in self.lags:
            m, a, mm, aa, ma = (getter(arr) for arr in self.arrays[k])
            out[k] = _correlation_from_sums(n, sum(m), sum(a), sum(mm), sum(aa), sum(ma))
        return out


def _best(table):
    return nowcast.best_lag(table)


def _lag_block(models, actual_series, positions, lags, interval_spec, members=None):
    """Lag tables, best lags, and the paired intervals of each model against `control`, on `members`."""

    members = list(range(len(positions))) if members is None else members
    pos = [positions[i] for i in members]
    tables = {
        name: LagTable([medians[i] for i in members], actual_series, pos, lags) for name, medians in models.items()
    }
    full = list(range(len(pos)))
    entry = {"days": len(pos), "correlation_by_lag": {}, "best_lag": {}}
    for name, table in tables.items():
        corr = table.correlations(full)
        entry["correlation_by_lag"][name] = {str(k): v for k, v in corr.items()}
        entry["best_lag"][name] = _best(corr)
    entry["paired_vs_control"] = {}
    if len(pos) >= 30:
        for name in models:
            if name == "control":
                continue

            def statistic(indices, name=name):
                a = tables[name].correlations(indices)
                b = tables["control"].correlations(indices)
                return float(_best(a) - _best(b))

            def corr_at(k, name=name):
                def inner(indices):
                    return tables[name].correlations(indices)[k] - tables["control"].correlations(indices)[k]

                return inner

            n = len(pos)
            kw = dict(
                block_length=interval_spec["block_length"], seed=interval_spec["seed"],
                replications=interval_spec["replications"], level=interval_spec["level"],
            )
            lag_interval = stationary_bootstrap_interval(statistic, n, **kw)
            at0 = stationary_bootstrap_interval(corr_at(0), n, **kw)
            at2 = stationary_bootstrap_interval(corr_at(2), n, **kw)
            c = entry["correlation_by_lag"]
            entry["paired_vs_control"][name] = {
                "best_lag_difference": entry["best_lag"][name] - entry["best_lag"]["control"],
                "best_lag_difference_interval": list(lag_interval),
                "correlation_difference_at_lag_0": c[name]["0"] - c["control"]["0"],
                "correlation_difference_at_lag_0_interval": list(at0),
                "correlation_difference_at_lag_2": c[name]["2"] - c["control"]["2"],
                "correlation_difference_at_lag_2_interval": list(at2),
            }
    return entry


def score_command(args) -> int:
    declarations_committed()
    require_unlocked([END], where="nowcast")
    declaration = nowcast.load_declaration(DECLARATION)
    raw = declaration.raw
    spec = raw["distribution"]["interval"]
    levels = tuple(raw["distribution"]["levels"])
    rows = load_daily_panel(args.panel)
    audit_panel(rows)
    by_date = {row.date: row for row in rows}
    position = {row.date: i for i, row in enumerate(rows)}
    splits = load_split_declaration(SPLITS)
    digest = panel_sha256(args.panel)
    walks = {}
    for path in args.inputs:
        document = json.loads(Path(path).read_text())
        if document["panel_sha256"] != digest:
            raise SystemExit(f"{path} was scored on another panel ({document['panel_sha256'][:8]})")
        if tuple(document["levels"]) != levels:
            raise SystemExit(f"{path} has other quantile levels")
        key = document["which"] if document["design"] == "published" else f"{document['design']}_{document['which']}"
        walks[key] = document
    required = {"persistence", "control", "feature_variant", "substitute_variant"}
    optional = {"feature_oracle", "substitute_oracle", "substitute_naive"}
    if not required <= set(walks) <= required | optional:
        raise SystemExit(f"score needs the walks {sorted(required)} and may take {sorted(optional)}")
    published = {d["date"]: d for d in _scored_days()}
    days = sorted(published)
    for which, document in walks.items():
        have = {d["date"]: d for d in document["days"]}
        missing = [d for d in days if d not in have]
        if missing:
            raise SystemExit(f"the {which} walk lacks {missing[0]}")
        walks[which] = {d: have[d] for d in days}
    # The control is the published distribution: reproduce its record, exactly, on every scored day.
    mismatched = [d for d in days if walks["control"][d]["quantiles_bps"] != published[d]["quantiles_bps"]]
    reproduces = {"days": len(days), "differing": len(mismatched), "first_differing": mismatched[:3]}
    if mismatched:
        raise SystemExit(f"the control walk differs from the published record on {len(mismatched)} days")
    checks = {"control_reproduces_the_published_record": reproduces}
    for key, why in (
        ("substitute_naive", "the substituted model fed the naive nowcast"),
        ("feature_oracle", "the declared variant fed the oracle (the diagnosis of the amendment)"),
    ):
        if key in walks:
            differing = [d for d in days if walks[key][d]["quantiles_bps"] != walks["control"][d]["quantiles_bps"]]
            checks[key] = {"what": why, "reproduces_control_exactly": not differing, "days_differing": len(differing)}
    if "substitute_naive" in walks and checks["substitute_naive"]["days_differing"]:
        raise SystemExit("the substitution does not reproduce the published forecasts with the naive nowcast")
    actual = [by_date[date.fromisoformat(d)].spread_bps for d in days]
    groups = _groups(days, by_date, splits)
    turn_series = [row.spread_bps for row in rows]
    flags_all = nowcast.turning_points(turn_series, minimum_move=declaration.minimum_move_bp)
    turning = [flags_all[position[date.fromisoformat(d)]] for d in days]
    classified = [t is not None for t in turning]
    extra = {
        "turning point days": [t is True for t in turning],
        "other classified days": [t is False for t in turning],
    }
    cells = _cells(groups, extra)
    crps = {
        which: [crps_from_quantiles(levels, walks[which][d]["quantiles_bps"], a) for d, a in zip(days, actual)]
        for which in walks
    }
    median_index = levels.index(0.5)
    median = {which: [walks[which][d]["quantiles_bps"][median_index] for d in days] for which in walks}
    abs_error = {which: [abs(m - a) for m, a in zip(median[which], actual)] for which in walks}
    out = {
        "days": len(days), "first": days[0], "last": days[-1], "panel_sha256": digest,
        "checks": checks,
        "turning_points": {
            "minimum_move_bp": declaration.minimum_move_bp,
            "turning_point_days": sum(1 for t in turning if t is True),
            "other_classified_days": sum(1 for t in turning if t is False),
            "unclassified_days": sum(1 for t in turning if t is None),
        },
        "mean_crps_bp": {which: sum(v) / len(v) for which, v in crps.items()},
        "mean_median_abs_error_bp": {which: sum(v) / len(v) for which, v in abs_error.items()},
        "crps_gain": {},
        "median_abs_error_gain": {},
    }
    # gain = the reference's loss minus the model's: positive means the model is better.
    pairs = [
        ("feature_variant", "control"), ("substitute_variant", "control"), ("substitute_variant", "persistence"),
        ("control", "persistence"),
    ]
    for ceiling in ("substitute_oracle", "feature_oracle"):
        if ceiling in walks:
            pairs.append((ceiling, "control"))
    for model, reference in pairs:
        key = f"{model}_vs_{reference}"
        out["crps_gain"][key] = _paired([r - m for r, m in zip(crps[reference], crps[model])], cells, spec)
        out["median_abs_error_gain"][key] = _paired(
            [r - m for r, m in zip(abs_error[reference], abs_error[model])], cells, spec
        )
    # The lag: every scored day with a day 3 ahead inside the scratch panel.
    lags = list(range(-3, 6))
    last_position = len(rows) - 1
    usable = [i for i, d in enumerate(days) if position[date.fromisoformat(d)] + 3 <= last_position]
    positions = [position[date.fromisoformat(days[i])] for i in usable]
    models = {
        which: [median[which][i] for i in usable]
        for which in ("control", "persistence", "feature_variant", "substitute_variant", "substitute_oracle")
        if which in median
    }
    spreads = [row.spread_bps for row in rows]
    out["lag"] = {"all": _lag_block(models, spreads, positions, lags, spec)}
    regime_labels = [groups["regime"][i] for i in usable]
    for label in sorted(set(regime_labels)):
        members = [j for j, g in enumerate(regime_labels) if g == label]
        out["lag"][f"regime: {label}"] = _lag_block(models, spreads, positions, lags, spec, members)
    for label in sorted(set(groups["day_type"])):
        members = [j for j, i in enumerate(usable) if groups["day_type"][i] == label]
        if len(members) >= 60:
            out["lag"][f"day_type: {label}"] = _lag_block(models, spreads, positions, lags, spec, members)
    args.output.write_text(json.dumps(out, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({k: out[k] for k in ("checks", "mean_crps_bp", "mean_median_abs_error_bp", "turning_points")}, indent=1))
    for key, cells_ in out["crps_gain"].items():
        cell = cells_["all"]
        print(f"CRPS gain {key}: {cell['mean']:+.4f} [{cell['interval'][0]:+.4f}, {cell['interval'][1]:+.4f}]")
    print("best lag", out["lag"]["all"]["best_lag"])
    return 0


# -- the pressure classifier ---------------------------------------------------


def _document(horizon, digest, forecasts):
    return {
        "horizon": horizon,
        "panel_sha256": digest,
        "forecasts": {
            forecast.name: {
                f"{tau:g}": {day.isoformat(): p for day, p in zip(forecast.dates, column)}
                for tau, column in forecast.probabilities.items()
            }
            for forecast in forecasts
        },
    }


def pressure_command(args) -> int:
    from repo_model import ml
    from repo_model.baseline import rolling_exceedance_backtest
    from repo_model.recalibration import NestedFoldPid

    commits = declarations_committed()
    require_unlocked([END], where="nowcast")
    declaration = pj.load_declaration()
    rows = load_daily_panel(args.panel)
    audit_panel(rows)
    if rows[-1].date > END:
        raise SystemExit(f"the scratch panel runs past {END}")
    splits = load_split_declaration(SPLITS)
    registry = measurement_fields.load_registry()
    model = _script("pressure_model_v1")
    h = args.horizon
    base = tuple(model._at_horizon(model.GBM_FEATURES, h))
    features = base + (nowcast.NOWCAST_COLUMN,)
    # Declared to the as-of rule either way; the fitter reads the nowcast as a regressor only in the declared
    # variant, and in the substituted one (the amendment) reads the published features and is handed the
    # nowcast as its latest spread.
    regressors = features if args.design == "feature" else base
    name = VARIANT if args.design == "feature" else VARIANT_SUBSTITUTED
    built = []

    def online(rows_, rule):
        built.append(NestedFoldPid(rows_, rule, splits=splits, refit_every=REFIT_EVERY))
        return built[-1]

    with switched_on(), (contextlib.nullcontext() if args.design == "feature" else substituted()):
        raw = rolling_exceedance_backtest(
            rows,
            predictor=ml.gbm_exceedance(
                tuple(n for n in regressors if n != "spread_bps"), minimum_history=MINIMUM_HISTORY
            ),
            model_name="distributional_gbm",
            features=features,
            registry=registry,
            decision_time=time(16, 0),
            taus=declaration.thresholds,
            minimum_history=MINIMUM_HISTORY,
            refit_every=REFIT_EVERY,
            end=declaration.last_day,
            horizon=h,
            online_calibration=online,
        )
    forecast = pj.report_forecast(name, pressure.recalibrated(raw))
    document = _document(h, panel_sha256(args.panel), [forecast])
    document["declaration_commits"] = commits
    document["features"] = list(features)
    args.output.write_text(json.dumps(document, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"horizon": h, "model": name, "output": str(args.output)}))
    return 0


def pair_command(args) -> int:
    declaration = pj.load_declaration()
    judge_script = _script("pressure_judge")
    spec = nowcast.load_declaration(DECLARATION).raw["distribution"]["interval"]
    rows = load_daily_panel(args.panel)
    audit_panel(rows)
    splits = load_split_declaration(SPLITS)
    digest = panel_sha256(args.panel)
    by_name = {}
    for path in args.inputs:
        document = json.loads(Path(path).read_text())
        if document["panel_sha256"] != digest:
            raise SystemExit(f"{path} was scored on another panel ({document['panel_sha256'][:8]})")
        for forecast in pj.forecasts_from_horizon_document(document):
            by_name[(forecast.horizon, forecast.name)] = forecast
    out = {}
    for h in declaration.horizons:
        control = by_name[(h, CONTROL)]
        states = judge_script._scarcity_states(h, declaration.last_day)
        grid = pj.build_grid(declaration, h, rows, control.dates, splits, scarcity_state=states)
        cells = _cells({"regime": list(grid.groups["regime"]), "day_type": list(grid.groups["day_type"])})
        for name in (VARIANT, VARIANT_SUBSTITUTED):
            if (h, name) not in by_name:
                continue
            variant = by_name[(h, name)]
            for tau in declaration.thresholds:
                y = grid.outcomes[tau]
                gain = [(control.probabilities[tau][i] - y[i]) ** 2 - (variant.probabilities[tau][i] - y[i]) ** 2 for i in range(len(y))]
                for label, members in cells.items():
                    cell = _mean_with_interval([gain[i] for i in members], dict(spec, seed=spec["seed"] + h))
                    out.setdefault(name, {}).setdefault(f"+{tau:g}", {}).setdefault(str(h), {})[label] = {
                        "days": cell["days"], "brier_gain_vs_control": cell["mean"], "interval": cell["interval"],
                        "pressure_days": sum(y[i] for i in members),
                    }
    args.output.write_text(json.dumps(out, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    for name, taus in out.items():
        for tau, hs in taus.items():
            for h, cells in sorted(hs.items()):
                c = cells["all"]
                print(f"{name} {tau} h={h}: dBrier {c['brier_gain_vs_control']:+.5f} [{c['interval'][0]:+.5f}, {c['interval'][1]:+.5f}]")
    return 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    commands = parser.add_subparsers(dest="command", required=True)
    panel = commands.add_parser("panel")
    panel.add_argument("--panel", type=Path, required=True)
    panel.add_argument("--output", type=Path, required=True)
    panel.add_argument("--summary", type=Path)
    panel.set_defaults(handler=panel_command)
    accuracy = commands.add_parser("accuracy")
    accuracy.add_argument("--panel", type=Path, required=True)
    accuracy.add_argument("--output", type=Path, required=True)
    accuracy.set_defaults(handler=accuracy_command)
    walk = commands.add_parser("walk")
    walk.add_argument("--panel", type=Path, required=True)
    walk.add_argument("--which", choices=("persistence", "control", "variant", "oracle", "naive"), required=True)
    walk.add_argument("--design", choices=("feature", "substitute"), default="feature")
    walk.add_argument("--output", type=Path, required=True)
    walk.set_defaults(handler=walk_command)
    score = commands.add_parser("score")
    score.add_argument("--panel", type=Path, required=True)
    score.add_argument("--output", type=Path, required=True)
    score.add_argument("inputs", nargs="+", type=Path)
    score.set_defaults(handler=score_command)
    pressure_ = commands.add_parser("pressure")
    pressure_.add_argument("--panel", type=Path, required=True)
    pressure_.add_argument("--horizon", type=int, required=True)
    pressure_.add_argument("--design", choices=("feature", "substitute"), default="feature")
    pressure_.add_argument("--output", type=Path, required=True)
    pressure_.set_defaults(handler=pressure_command)
    pair = commands.add_parser("pair")
    pair.add_argument("--panel", type=Path, required=True)
    pair.add_argument("--output", type=Path, required=True)
    pair.add_argument("inputs", nargs="+", type=Path)
    pair.set_defaults(handler=pair_command)
    args = parser.parse_args(argv)
    return args.handler(args)


if __name__ == "__main__":
    raise SystemExit(main())
