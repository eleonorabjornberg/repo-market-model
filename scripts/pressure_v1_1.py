"""Pressure model v1.1 (#117): score the new inputs against pressure model v1.

A scratch measurement, not a record: it writes pickles, JSON and Markdown to
the paths it is given, and nothing into `docs/runs/`. Every input is off in
every published declaration; this script switches them on for its own run. The
candidates, the primary family and the win rule are `repo_model.pressure_v1_1`'s,
committed before any scoring.

    PYTHONPATH=src python3 scripts/pressure_v1_1.py panel --output AUG.csv
    PYTHONPATH=src python3 scripts/pressure_v1_1.py run --panel AUG.csv --run NAME --horizon H --output OUT/NAME_hH.pickle
    PYTHONPATH=src python3 scripts/pressure_v1_1.py crps --panel AUG.csv --run NAME --output OUT/crps_NAME.json
    PYTHONPATH=src python3 scripts/pressure_v1_1.py pair --panel AUG.csv --runs OUT --run NAME --horizon H
    PYTHONPATH=src python3 scripts/pressure_v1_1.py assemble --panel AUG.csv --runs OUT --output OUT/v1_1.json \\
        --markdown OUT/v1_1.md --splits-markdown OUT/splits.md

* `panel` builds the measurement panel from tracked fixtures, with no network:
  the published panel's inputs (`funding_inputs/`), the Desk's ON RRP
  operation results (`on_rrp_inputs/`, #45), the H.8 first prints
  (`h8_inputs/`, #115) and the New York Fed's EFFR (`nyfed_effr_inputs/`, #98),
  built with the published manifest's columns plus `on_rrp`,
  `bank_total_assets` and `effr`. It checks first that the same build on the
  published columns alone reproduces the published panel's digest. It then adds
  `reserve_scarcity_state` (`scarcity.with_reserve_scarcity_state`) and the two
  announced-IORB columns (`announced_iorb.with_announced_iorb`), and keeps the
  rows up to 2025-12-31 (`docs/decisions/lockbox.md`). The composed (#88, #97)
  and derived (#98) features are formed per forecast by the as-of rule.
* `run` scores one run at one horizon: `control` (pressure model v1 as #124
  published it: `scripts/pressure_model_v1.py`'s gbm on the published funding
  declaration, conformal PID with nested selection, recalibrated out of fold),
  `persistence_logistic`, or a run of `pressure_v1_1.RUNS` (v1 plus its
  columns, the same model otherwise).
* `crps` is the distribution side at horizon 1: `compare --loss crps`, the
  published funding declaration against it plus the run's columns, both
  calibrated by `conformal_pid_nested`, on one fold grid.
* `pair` pairs one run at one horizon with its two benchmarks.
* `assemble` reads every pair, computes the primary family's p-values and the
  Holm correction (`pressure_v1_1.holm`), classifies the primary candidate by
  `pressure_v1_1.classify`, applies Eleonora's `on_rrp` rule
  (`pressure_v1_1.on_rrp_rule`), and writes the tables: Brier with its
  decomposition, average precision, paired differences by regime and
  pressure-day type, onset days, lead time, the October 2025 onset, CRPS, and
  the small-leap targets (#139).
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

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))


def _script(name):
    """A sibling script as a module, without running it: the control and the
    measurement-panel build are theirs, not restated."""

    spec = importlib.util.spec_from_file_location(name, REPO / "scripts" / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


#: Pressure model v1's published code path (#124) and #115's measurement build.
v1 = _script("pressure_model_v1")
sv = _script("scarcity_validation")

from repo_model import announced_iorb, pressure, pressure_v1_1, scarcity  # noqa: E402
from repo_model.data import DailyObservation, write_daily_panel  # noqa: E402

REGISTRY = v1.REGISTRY
SPLITS = v1.SPLITS
END = v1.END
SNAPSHOTS = REPO / "tests" / "fixtures" / "snapshots"
RAW_ROOTS = ("funding_inputs", "on_rrp_inputs", "h8_inputs", "nyfed_effr_inputs")
EXTRA_COLUMNS = ("on_rrp", "bank_total_assets", "effr")
IORB_TABLE = SNAPSHOTS / "fed-iorb-announcements" / "iorb_changes.csv"


def _proxy(mapping):
    return MappingProxyType(mapping)


copyreg.pickle(MappingProxyType, lambda proxy: (_proxy, (dict(proxy),)))


@contextlib.contextmanager
def switched_on():
    """`on_rrp` from the Desk's results, `bank_total_assets` and the state, for this run only."""

    with scarcity.measurement_declaration():
        yield


# -- the measurement panel ------------------------------------------------------


def panel_command(args) -> int:
    with switched_on(), tempfile.TemporaryDirectory() as scratch:
        sv.RAW_ROOTS = RAW_ROOTS
        sv.EXTRA_COLUMNS = EXTRA_COLUMNS
        build, digest, _registry, decision = sv.build_measurement_panel(REGISTRY, Path(scratch))
    rows = [row for row in build.observations if row.date <= END]
    rows = scarcity.with_reserve_scarcity_state(rows)
    rows = announced_iorb.with_announced_iorb(
        rows, announced_iorb.load_announcements(IORB_TABLE), decision_time=decision
    )
    columns = list(build.built_columns) + [scarcity.RESERVE_SCARCITY_STATE, *announced_iorb.FEATURES]
    with args.output.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerow(["date", *columns])
        for row in rows:
            writer.writerow(
                [row.date.isoformat()]
                + ["" if row.values.get(name) is None else repr(row.values[name]) for name in columns]
            )
    summary = {
        "output": str(args.output),
        "sha256": hashlib.sha256(args.output.read_bytes()).hexdigest(),
        "published_columns_digest": digest,
        "rows": len(rows),
        "first": rows[0].date.isoformat(),
        "last": rows[-1].date.isoformat(),
        "missing": {
            name: sum(1 for row in rows if row.values.get(name) is None)
            for name in [*EXTRA_COLUMNS, scarcity.RESERVE_SCARCITY_STATE, *announced_iorb.FEATURES]
        },
    }
    print(json.dumps(summary, indent=1))
    return 0


# -- runs ------------------------------------------------------------------------

CONTROL = "control"
PERSISTENCE_LOGISTIC = "persistence_logistic"
CALENDAR_CLIMATOLOGY = "calendar_climatology"
#: Benchmark name -> run name. The first two are the primary benchmarks; calendar
#: climatology is reported beside them and decides nothing.
BENCH_RUNS = {
    "pressure_model_v1": CONTROL,
    "persistence_logistic": PERSISTENCE_LOGISTIC,
    "calendar_climatology": CALENDAR_CLIMATOLOGY,
}
RUN_NAMES = [run.name for run in pressure_v1_1.RUNS]


def _run(name):
    return {run.name: run for run in pressure_v1_1.RUNS}[name]


def scored_at(name, h):
    """Whether run `name` is scored at horizon `h`: a run whose every column is
    refused there would only repeat the control."""

    return bool(pressure_v1_1.columns_at_horizon(_run(name), h))


def run_command(args) -> int:
    from repo_model import ml
    from repo_model.baseline import calendar_climatology_exceedance
    from repo_model.data import audit_panel, load_daily_panel, load_stress_thresholds
    from repo_model.evaluation_splits import load_split_declaration
    from repo_model.onset import LEAP_JUMP_BP
    from repo_model.recalibration import NestedFoldPid

    h = args.horizon
    if args.run in RUN_NAMES and not scored_at(args.run, h):
        raise SystemExit(f"{args.run} has no column public at horizon {h}; it is not scored there")
    rows = load_daily_panel(args.panel)
    audit_panel(rows)
    splits = load_split_declaration(SPLITS)
    taus = tuple(float(tau) for tau in load_stress_thresholds(v1.THRESHOLDS)["taus_bp"])
    registry = json.loads(REGISTRY.read_text())
    built = []

    def online(rows_, rule):
        built.append(NestedFoldPid(rows_, rule, splits=splits, refit_every=v1.REFIT_EVERY))
        return built[-1]

    def backtest(name, predictor, features, calibration=None, leap=None):
        return v1.rolling_exceedance_backtest(
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
            leap_jump_bp=leap,
            online_calibration=calibration,
        )

    with switched_on():
        if args.run == PERSISTENCE_LOGISTIC:
            features = ("spread_bps",)
            report = backtest(
                args.run, v1.persistence_logistic_exceedance(minimum_history=v1.MINIMUM_HISTORY), features
            )
        elif args.run == CALENDAR_CLIMATOLOGY:
            features = v1.CALENDAR_FEATURES
            report = backtest(
                args.run, calendar_climatology_exceedance(splits, minimum_history=v1.MINIMUM_HISTORY), features
            )
        else:
            extra = () if args.run == CONTROL else pressure_v1_1.columns_at_horizon(_run(args.run), h)
            features = v1._at_horizon(v1.GBM_FEATURES, h) + extra
            raw = backtest(
                args.run,
                ml.gbm_exceedance(
                    tuple(name for name in features if name != "spread_bps"),
                    minimum_history=v1.MINIMUM_HISTORY,
                ),
                features,
                online,
                LEAP_JUMP_BP[h],
            )
            report = v1._rescored(pressure.recalibrated(raw))
    document = {
        "run": args.run,
        "horizon": h,
        "features": list(features),
        "panel_sha256": v1.panel_sha256(args.panel),
        "report": report,
        "calibration_account": built[0].account() if built else None,
    }
    args.output.write_bytes(pickle.dumps(document))
    print(json.dumps({
        "run": args.run, "horizon": h, "first": report.scored_dates[0].isoformat(),
        "last": report.scored_dates[-1].isoformat(), "days": len(report.scored_dates),
    }))
    return 0


def crps_command(args) -> int:
    from repo_model import cli

    columns = _run(args.run).columns

    def side(letter, features):
        out = ["--model-" + letter, "gbm", "--calibration-" + letter, "conformal_pid_nested"]
        for name in features:
            out += ["--feature-" + letter, name]
        return out

    argv = [
        "compare", str(args.panel),
        "--registry", str(REGISTRY), "--decision-time", "16:00",
        "--minimum-history", str(v1.MINIMUM_HISTORY), "--refit-every", str(v1.REFIT_EVERY),
        "--end", END.isoformat(), "--splits", str(SPLITS), "--loss", "crps",
        *side("a", v1.GBM_FEATURES), *side("b", v1.GBM_FEATURES + columns),
        "--report", str(args.output),
    ]
    with switched_on():
        status = cli.main(argv)
    document = json.loads(args.output.read_text())
    document["pressure_v1_1"] = {"run": args.run, "columns": list(columns)}
    args.output.write_text(json.dumps(document, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    return status


# -- pairs -------------------------------------------------------------------------


def _load(directory, name, h):
    return pickle.loads((directory / f"{name}_h{h}.pickle").read_bytes())


def _brier(report, tau):
    position = report.taus.index(tau)
    forecast, _, outcomes = report.at_tau(position)
    return [(p - y) ** 2 for p, y in zip(forecast, outcomes)]


def _interval(values, block, seed):
    from repo_model.metrics import stationary_bootstrap_interval

    lower, upper = stationary_bootstrap_interval(
        lambda idx: sum(values[i] for i in idx) / len(idx),
        len(values), block_length=block, seed=seed,
        replications=INTERVAL_REPLICATIONS, level=INTERVAL_LEVEL,
    )
    return {"lower": lower, "upper": upper, "block_length": block, "seed": seed,
            "replications": INTERVAL_REPLICATIONS, "level": INTERVAL_LEVEL}


INTERVAL_LEVEL = 0.90
INTERVAL_REPLICATIONS = 2000


def _leap_section(report, rows, splits, h, registry, digest):
    """#139's leap targets for one run, against the two leap baselines."""

    from repo_model.asof import TARGET, InformationRule
    from repo_model.baseline import _exceedance_seed, _maximum_horizon_overlap
    from repo_model.onset import leap_document

    if getattr(report, "leap_forecast", None) is None:
        return {"unavailable": "the run did not score the model's leap probability"}
    rule = InformationRule(registry, (TARGET,), decision_time=v1.DECISION, horizon=h)
    return leap_document(
        report, rows, splits, rule,
        block=_maximum_horizon_overlap(report.folds),
        base_seed=_exceedance_seed(report, digest),
    )


def pair_entries(runs, name, h, rows, splits, digest):
    """Every comparison of run `name` at horizon `h` against every benchmark run.

    Brier at +5 and +10 bp on all scored days and on #139's onset days, the
    run's own metrics (`pressure._metrics`) and, for a gbm run, its leap
    targets. Returns `(entries, grid_members, detail)`; `grid_members` carries
    each comparison's daily differences with its grid, for the p-values.
    """

    from repo_model.baseline import benchmark_comparison_document
    from repo_model.data import exceeds_bp

    entries, members = {}, []
    candidate = _load(runs, name, h)["report"]
    onset = pressure_v1_1.onset_positions(rows, candidate.scored_dates)
    detail = {
        "metrics": {
            f"{tau:g}": pressure._metrics(*pressure._columns(candidate, candidate.taus.index(tau)))
            for tau in pressure_v1_1.THRESHOLDS
        },
        "first": candidate.scored_dates[0].isoformat(),
        "last": candidate.scored_dates[-1].isoformat(),
        "days": len(candidate.scored_dates),
        "onset_days": [candidate.scored_dates[i].isoformat() for i in onset],
    }
    for bench_name, run in BENCH_RUNS.items():
        if run == name:
            continue
        bench = _load(runs, run, h)["report"]
        document = benchmark_comparison_document(
            candidate, bench, panel_sha256=digest, rows=rows, declaration=splits
        )
        for tau in pressure_v1_1.THRESHOLDS:
            paired = document["by_tau"][f"{tau:g}"]["paired_brier_difference"]
            differences = [b - c for b, c in zip(_brier(bench, tau), _brier(candidate, tau))]
            if abs(sum(differences) / len(differences) - paired["mean"]) > 1e-12:
                raise SystemExit(f"{name} h{h} {bench_name} {tau}: daily differences disagree")
            block = paired["interval"]["block_length"]
            pooled_key = pressure_v1_1.comparison_key(name, "brier", pressure_v1_1.POOLED, tau, h, bench_name)
            entries[pooled_key] = {
                "mean": paired["mean"],
                "interval": paired["interval"],
                "days": len(differences),
                "events": sum(1 for v in candidate.realized_bps if exceeds_bp(v, tau)),
                "splits": paired["splits"],
                "candidate_brier": sum(_brier(candidate, tau)) / len(differences),
                "benchmark_brier": sum(_brier(bench, tau)) / len(differences),
            }
            members.append([h, pressure_v1_1.POOLED, block, pooled_key, differences])
            onset_differences = [differences[i] for i in onset]
            onset_key = pressure_v1_1.comparison_key(name, "brier", pressure_v1_1.ONSET, tau, h, bench_name)
            entries[onset_key] = {
                "mean": sum(onset_differences) / len(onset_differences),
                "interval": _interval(
                    onset_differences, block, pressure_v1_1.p_value_seed(h, pressure_v1_1.ONSET, "interval")
                ),
                "days": len(onset_differences),
                "events": sum(1 for i in onset if exceeds_bp(candidate.realized_bps[i], tau)),
                "candidate_brier": sum(_brier(candidate, tau)[i] for i in onset) / len(onset),
                "benchmark_brier": sum(_brier(bench, tau)[i] for i in onset) / len(onset),
            }
            members.append([h, pressure_v1_1.ONSET, block, onset_key, onset_differences])
    if name not in (PERSISTENCE_LOGISTIC, CALENDAR_CLIMATOLOGY):
        registry = json.loads(REGISTRY.read_text())
        detail["leap"] = _leap_section(candidate, rows, splits, h, registry, digest)
        if name != CONTROL:
            detail["leap_vs_control"] = _leap_vs_control(
                candidate, _load(runs, CONTROL, h)["report"], rows, h, registry
            )
    return entries, members, detail


def _leap_vs_control(candidate, control, rows, h, registry):
    """The leap targets' Brier, the run paired against the control (control minus run)."""

    from repo_model.asof import TARGET, InformationRule
    from repo_model.baseline import _maximum_horizon_overlap
    from repo_model.onset import LEAP_JUMP_BP, LeapTargets, paired_difference

    if tuple(candidate.scored_dates) != tuple(control.scored_dates):
        raise SystemExit("the run and the control are not on one grid")
    rule = InformationRule(registry, (TARGET,), decision_time=v1.DECISION, horizon=h)
    targets = LeapTargets(rows, rule, LEAP_JUMP_BP[h])
    position_of = {when: index for index, when in enumerate(targets.dates)}
    scored = [position_of[when] for when in candidate.scored_dates]
    block = _maximum_horizon_overlap(candidate.folds)
    out = {"threshold_bp": LEAP_JUMP_BP[h]}
    for target, attribute in (("leap", "leap_forecast"), ("pressure_leap", "pressure_leap_forecast")):
        labels = targets.labels(target)
        outcomes = [1 if labels[index] else 0 for index in scored]
        losses = {
            which: [(p - y) ** 2 for p, y in zip(getattr(report, attribute), outcomes)]
            for which, report in (("run", candidate), ("control", control))
        }
        groups = {
            "all_days": list(range(len(scored))),
            "leap_onset_days": [k for k, index in enumerate(scored) if targets.leap_onset[index]],
        }
        out[target] = {
            group: {
                **paired_difference(
                    losses["control"], losses["run"], positions, block_length=block,
                    seed=pressure_v1_1.p_value_seed(h, target, group, "leap interval"),
                ),
                "events": sum(outcomes[k] for k in positions),
            }
            for group, positions in groups.items()
        }
    return out


def pair_command(args) -> int:
    from repo_model.data import load_daily_panel
    from repo_model.evaluation_splits import load_split_declaration

    rows = load_daily_panel(args.panel)
    with switched_on():
        entries, members, detail = pair_entries(
            args.runs, args.run, args.horizon, rows, load_split_declaration(SPLITS), v1.panel_sha256(args.panel)
        )
    path = args.runs / f"pair_{args.run}_h{args.horizon}.json"
    path.write_text(json.dumps({"entries": entries, "grid_members": members, "detail": detail}), encoding="utf-8")
    print(json.dumps({"pair": str(path)}))
    return 0


# -- assembly ----------------------------------------------------------------------


def _pair_names(h):
    return [CONTROL] + [name for name in RUN_NAMES if scored_at(name, h)]


def assemble_command(args) -> int:
    from repo_model import ml
    from repo_model.data import load_daily_panel

    rows = load_daily_panel(args.panel)
    digest = v1.panel_sha256(args.panel)
    entries, grids, detail = {}, {}, {}
    for h in pressure_v1_1.HORIZONS:
        for name in _pair_names(h):
            path = args.runs / f"pair_{name}_h{h}.json"
            if not path.exists():
                raise SystemExit(f"{path} is missing: run `pair --run {name} --horizon {h}` first")
            paired = json.loads(path.read_text())
            entries.update(paired["entries"])
            for h_, day_set, block, key, differences in paired["grid_members"]:
                grids.setdefault((h_, day_set, block), []).append((key, differences))
            detail.setdefault(name, {})[str(h)] = paired["detail"]

    crps = {}
    for name in RUN_NAMES:
        document = json.loads((args.runs / f"crps_{name}.json").read_text())
        comparison = document["comparison"]
        last = max(origin["scored_date"] for origin in comparison["per_origin"])
        if last > END.isoformat():
            raise SystemExit(f"{name}: CRPS scored a locked day")
        key = pressure_v1_1.comparison_key(name, "crps")
        entries[key] = {
            "mean": comparison["mean_difference_bps"],
            "interval": comparison["mean_difference_interval"],
            "days": comparison["origin_count"],
            "control_crps_bps": comparison["model_a"]["crps_bps"],
            "candidate_crps_bps": comparison["model_b"]["crps_bps"],
            "first": min(origin["scored_date"] for origin in comparison["per_origin"]),
            "last": last,
            "splits": comparison.get("splits"),
        }
        crps[name] = {"onset": document.get("onset")}
        block = comparison["mean_difference_interval"]["block_length"]
        grids.setdefault((1, "crps", block), []).append(
            (key, [origin["difference_bps"] for origin in comparison["per_origin"]])
        )

    for (h, day_set, block), members in sorted(grids.items(), key=lambda item: str(item[0])):
        lengths = {len(values) for _key, values in members}
        if len(lengths) != 1:
            raise SystemExit(f"grid h{h} {day_set}: lengths {sorted(lengths)}")
        p_values = ml.paired_bootstrap_p_values(
            [values for _key, values in members],
            block_length=block,
            seed=pressure_v1_1.p_value_seed(h, day_set),
            replications=pressure_v1_1.P_VALUE_REPLICATIONS,
        )
        for (key, _values), (p_improve, p_worse) in zip(members, p_values):
            entries[key]["p_improve"] = p_improve
            entries[key]["p_worse"] = p_worse

    primary = pressure_v1_1.primary_cells()
    for key in primary:
        block = entries[key]["interval"]["block_length"]
        if block != 2:
            raise SystemExit(f"{key}: block length {block}, the rule states 2 at horizon 1")
    verdict = pressure_v1_1.classify({key: entries[key] for key in primary})

    forms = pressure_v1_1.ON_RRP_FORMS
    form = pressure_v1_1.on_rrp_form(
        {run: entries[pressure_v1_1.comparison_key(run, "crps")]["mean"] for run in forms.values()}
    )
    on_rrp = {
        "form": form,
        "by_form": {
            run: pressure_v1_1.on_rrp_rule(
                crps=entries[pressure_v1_1.comparison_key(run, "crps")],
                brier_5=entries[pressure_v1_1.comparison_key(run, "brier", "all_days", 5.0, 1, "pressure_model_v1")],
                brier_10=entries[pressure_v1_1.comparison_key(run, "brier", "all_days", 10.0, 1, "pressure_model_v1")],
            )
            for run in forms.values()
        },
    }
    on_rrp["met"] = on_rrp["by_form"][form]["met"]

    lead, october = _lead_time(args.runs, rows)
    document = {
        "directive": "#117",
        "status": "scratch measurement; not a record, nothing published moves",
        "panel_sha256": digest,
        "win_rule": verdict,
        "on_rrp_rule": on_rrp,
        "p_value_replications": pressure_v1_1.P_VALUE_REPLICATIONS,
        "comparisons": entries,
        "detail": detail,
        "crps_onset": crps,
        "lead_time": lead,
        "october_2025_onset": october,
    }
    args.output.write_text(json.dumps(document, indent=1, sort_keys=True, default=str) + "\n", encoding="utf-8")
    args.markdown.write_text(_markdown(document), encoding="utf-8")
    if args.splits_markdown is not None:
        args.splits_markdown.write_text(_splits_markdown(document), encoding="utf-8")
    print(json.dumps({"output": str(args.output), "passed": verdict["passed"],
                      "improving": verdict["improving_cells"], "worse": verdict["deteriorating_cells"],
                      "on_rrp": {"form": form, "met": on_rrp["met"]}}))
    return 0


def _lead_time(directory, rows):
    """Lead time to onset (`pressure.onsets`, as #114) and the October 2025 onset.

    Only runs scored at every horizon: the #38 and #97 runs are not."""

    models = [CONTROL, PERSISTENCE_LOGISTIC, CALENDAR_CLIMATOLOGY] + [
        name for name in RUN_NAMES if all(scored_at(name, h) for h in pressure_v1_1.HORIZONS)
    ]
    lead, october = {}, {}
    for tau in pressure_v1_1.THRESHOLDS:
        key = f"{tau:g}"
        forecasts = {}
        for name in models:
            forecasts[name] = {}
            for h in pressure_v1_1.HORIZONS:
                report = _load(directory, name, h)["report"]
                position = report.taus.index(tau)
                forecasts[name][h] = {
                    when: curve[position] for when, curve in zip(report.scored_dates, report.forecast)
                }
        common = sorted(set.intersection(*(set(forecasts[CONTROL][h]) for h in pressure_v1_1.HORIZONS)))
        onset_days = pressure.onsets(rows, tau, common)
        lead[key] = {
            "onsets": [d.isoformat() for d in onset_days],
            "by_model": {
                name: [pressure.lead_times(forecasts[name], onset_days, level) for level in pressure.ALARM_LEVELS]
                for name in models
            },
        }
        october[key] = {
            name: {
                d.isoformat(): {str(h): forecasts[name][h].get(d) for h in pressure_v1_1.HORIZONS}
                for d in onset_days if d.year == 2025 and d.month == 10
            }
            for name in models
        }
    return lead, october


# -- tables ------------------------------------------------------------------------


def _iv(entry, places=4):
    if entry is None or "mean" not in entry:
        return "–"
    interval = entry["interval"]
    return f"{entry['mean']:+.{places}f} [{interval['lower']:+.{places}f}, {interval['upper']:+.{places}f}]"


def _f(value, places=4):
    return "–" if value is None else f"{value:.{places}f}"


def _key(*parts):
    return pressure_v1_1.comparison_key(*parts)


def _markdown(document) -> str:
    entries = document["comparisons"]
    verdict = document["win_rule"]
    out = []
    out.append(
        "Paired difference = benchmark − run (Brier) or control − run (CRPS, bp): **positive favours the run**. "
        "90% stationary-bootstrap intervals. p = one-sided paired stationary-bootstrap p-value "
        f"({document['p_value_replications']} replications). Scored 2018-06-29 to 2025-12-31; no day on or "
        "after 2026-01-01.\n"
    )
    out.append("### The win rule: primary candidate `all_together`, four primary cells (+5 bp, horizon 1)\n")
    out.append("| Cell | Days | Events | Brier run | Brier benchmark | Difference [90%] | p improve | p worse | Holm improve | Holm worse |")
    out.append("|---|---|---|---|---|---|---|---|---|---|")
    for key in pressure_v1_1.primary_cells():
        e = entries[key]
        _run_, _b, day_set, _tau, _h, bench = key.split("|")
        out.append(
            f"| {day_set} vs {bench} | {e['days']} | {e['events']} | {_f(e['candidate_brier'])} | "
            f"{_f(e['benchmark_brier'])} | {_iv(e)} | {e['p_improve']:.4f} | {e['p_worse']:.4f} | "
            f"{'survives' if verdict['holm_improve'][key] else 'no'} | {'survives' if verdict['holm_worse'][key] else 'no'} |"
        )
    out.append("")
    out.append(
        f"**Outcome: {'PASSED' if verdict['passed'] else 'NOT PASSED'}.** Holm at "
        f"{verdict['family_level']:.0%} over {verdict['family_size']} cells. Improving cells surviving: "
        f"{', '.join(verdict['improving_cells']) or 'none'}. Deteriorating cells surviving: "
        f"{', '.join(verdict['deteriorating_cells']) or 'none'}.\n"
    )
    out.append("Everything below is **exploratory** and decides nothing.\n")
    names = [CONTROL] + RUN_NAMES
    out.append("### Horizon 1: Brier, decomposition, average precision\n")
    for tau in pressure_v1_1.THRESHOLDS:
        key = f"{tau:g}"
        out.append(f"**+{key} bp**\n")
        out.append("| Run | Brier | Reliability | Resolution | Uncertainty | AP | Events | Alarms ≥0.5 (hits) |")
        out.append("|---|---|---|---|---|---|---|---|")
        for name in names:
            m = document["detail"][name]["1"]["metrics"][key]
            d = m.get("decomposition", {})
            alarm = m["alarms"][-1]
            out.append(
                f"| {name} | {_f(m['brier'])} | {_f(d.get('reliability'))} | {_f(d.get('resolution'))} | "
                f"{_f(d.get('uncertainty'))} | {_f(m.get('average_precision'), 3)} | {m['events']} | "
                f"{alarm['alarms']} ({alarm['hits']}) |"
            )
        out.append("")
    for day_set, title in (("all_days", "all scored days"), ("onset_days", "onset days (#139)")):
        out.append(f"### Brier, {title}: paired difference [90%], one-sided p for improvement\n")
        out.append("| Run | h | +5 vs v1 | p | +5 vs pers.-logistic | p | +5 vs cal. clim. | +10 vs v1 | p | +10 vs pers.-logistic | +10 vs cal. clim. |")
        out.append("|---|---|---|---|---|---|---|---|---|---|---|")
        for name in RUN_NAMES:
            for h in pressure_v1_1.HORIZONS:
                if not scored_at(name, h):
                    continue
                cells = []
                for tau in pressure_v1_1.THRESHOLDS:
                    v = entries[_key(name, "brier", day_set, tau, h, "pressure_model_v1")]
                    p = entries[_key(name, "brier", day_set, tau, h, "persistence_logistic")]
                    c = entries[_key(name, "brier", day_set, tau, h, "calendar_climatology")]
                    if tau == 5.0:
                        cells += [_iv(v), f"{v['p_improve']:.4f}", _iv(p), f"{p['p_improve']:.4f}", _iv(c)]
                    else:
                        cells += [_iv(v), f"{v['p_improve']:.4f}", _iv(p), _iv(c)]
                out.append(f"| {name} | {h} | " + " | ".join(cells) + " |")
        for h in pressure_v1_1.HORIZONS:
            cells = []
            for tau in pressure_v1_1.THRESHOLDS:
                p = entries[_key(CONTROL, "brier", day_set, tau, h, "persistence_logistic")]
                c = entries[_key(CONTROL, "brier", day_set, tau, h, "calendar_climatology")]
                cells += ["", "", _iv(p), f"{p['p_improve']:.4f}" if tau == 5.0 else _iv(c)]
                if tau == 5.0:
                    cells.append(_iv(c))
            out.append(f"| control (v1) | {h} | " + " | ".join(cells) + " |")
        out.append("")
        if day_set == "onset_days":
            sample = entries[_key(CONTROL, "brier", day_set, 5.0, 1, "persistence_logistic")]
            out.append(f"Onset days at h = 1: {sample['days']}, of which above +5 bp: {sample['events']} (all, by definition).\n")
    out.append("### CRPS, horizon 1: the published funding declaration − the declaration plus the run's columns, bp\n")
    out.append("| Run | Scored | CRPS control | CRPS run | Difference [90%] | p improve | p worse | onset days: difference [90%] |")
    out.append("|---|---|---|---|---|---|---|---|")
    for name in RUN_NAMES:
        e = entries[_key(name, "crps")]
        onset_doc = (document["crps_onset"][name].get("onset") or {}).get("by_series", {}).get("loss", {}).get("onset_days", {})
        out.append(
            f"| {name} | {e['first']} to {e['last']} ({e['days']}) | {e['control_crps_bps']:.4f} | "
            f"{e['candidate_crps_bps']:.4f} | {_iv(e)} | {e['p_improve']:.4f} | {e['p_worse']:.4f} | "
            f"{_iv(onset_doc)} (n={onset_doc.get('days', '–')}) |"
        )
    out.append("")
    on_rrp = document["on_rrp_rule"]
    out.append("### The `on_rrp` rule (Eleonora's ruling of 2 October 2026)\n")
    out.append("| Form | Run | CRPS [90%] | Brier +5 vs v1 [90%] | Brier +10 vs v1 [90%] | Improved | Worse | Rule met |")
    out.append("|---|---|---|---|---|---|---|---|")
    for label, run in pressure_v1_1.ON_RRP_FORMS.items():
        r = on_rrp["by_form"][run]
        out.append(
            f"| {label}{' (best on pooled CRPS: the form the rule reads)' if run == on_rrp['form'] else ''} | {run} | "
            f"{_iv(entries[_key(run, 'crps')])} | {_iv(entries[_key(run, 'brier', 'all_days', 5.0, 1, 'pressure_model_v1')])} | "
            f"{_iv(entries[_key(run, 'brier', 'all_days', 10.0, 1, 'pressure_model_v1')])} | "
            f"{', '.join(r['improved']) or 'none'} | {', '.join(r['worse']) or 'none'} | {'yes' if r['met'] else 'no'} |"
        )
    out.append(f"\n**`on_rrp` rule: {'MET' if on_rrp['met'] else 'NOT MET'}** (form read: `{on_rrp['form']}`).\n")
    out.append("### Small leaps (#139): a different question from a stress warning\n")
    out.append(
        "A leap is an as-of jump in SOFR − IORB above J_h (`onset.LEAP_JUMP_BP`). The run's leap probability is "
        "the uncalibrated model's. Verdict against the two named leap baselines (all days); paired difference "
        "against the control = Brier(control) − Brier(run).\n"
    )
    out.append("| Run | h | Leap events | Verdict vs leap baselines | Leap: vs control, all days | Leap onsets: vs control | Pressure leap: vs control |")
    out.append("|---|---|---|---|---|---|---|")
    for name in [CONTROL] + RUN_NAMES:
        for h in pressure_v1_1.HORIZONS:
            if name != CONTROL and not scored_at(name, h):
                continue
            d = document["detail"][name][str(h)]
            leap = d.get("leap", {})
            target = leap.get("targets", {}).get("leap", {})
            events = target.get("all_days", {}).get("events", "–")
            verdict_leap = target.get("verdict", {}).get("result", leap.get("unavailable", "–"))
            vs = d.get("leap_vs_control")
            cells = ["", "", ""] if vs is None else [
                _iv(vs["leap"]["all_days"]),
                f"{_iv(vs['leap']['leap_onset_days'])} (n={vs['leap']['leap_onset_days'].get('days')})",
                _iv(vs["pressure_leap"]["all_days"]),
            ]
            out.append(f"| {name} | {h} | {events} | {verdict_leap} | " + " | ".join(cells) + " |")
    out.append("")
    out.append("### Lead time to onset (`pressure.onsets`), alarm levels 0.2 and 0.5\n")
    out.append("The #38 and #97 runs are scored at horizon 1 only, so they have no lead time.\n")
    for tau, entry in document["lead_time"].items():
        out.append(f"**+{tau} bp**: {len(entry['onsets'])} onsets\n")
        out.append("| Run | flagged at 0.2 | mean lead at 0.2 | flagged at 0.5 | mean lead at 0.5 |")
        out.append("|---|---|---|---|---|")
        for name, (low, high) in entry["by_model"].items():
            out.append(
                f"| {name} | {low['flagged']}/{low['onsets']} | {_f(low['mean_lead_days'], 2)} | "
                f"{high['flagged']}/{high['onsets']} | {_f(high['mean_lead_days'], 2)} |"
            )
        out.append("")
    out.append("### The October 2025 onset: probability forecast of the onset day, h = 1 to 5\n")
    for tau, by_model in document["october_2025_onset"].items():
        days = sorted({d for model in by_model.values() for d in model})
        if not days:
            out.append(f"**+{tau} bp**: no onset in October 2025 under the onset definition.\n")
        for day in days:
            out.append(f"**+{tau} bp, onset {day}**\n")
            out.append("| Run | h=1 | h=2 | h=3 | h=4 | h=5 |\n|---|---|---|---|---|---|")
            for name, by_day in by_model.items():
                values = by_day.get(day, {})
                out.append(f"| {name} | " + " | ".join(_f(values.get(str(h)), 3) for h in pressure_v1_1.HORIZONS) + " |")
            out.append("")
    return "\n".join(out) + "\n"


def _splits_markdown(document) -> str:
    """Every pooled Brier comparison against v1 by regime and pressure-day type, and CRPS's."""

    entries = document["comparisons"]
    out = []
    for tau in pressure_v1_1.THRESHOLDS:
        for bench in ("pressure_model_v1", "persistence_logistic"):
            out.append(f"### +{tau:g} bp against {bench}: by regime and pressure-day type\n")
            first = entries[_key(pressure_v1_1.PRIMARY, "brier", "all_days", tau, 1, bench)]["splits"]
            columns = [("by_regime", k) for k in first["by_regime"]] + [("by_day_type", k) for k in first["by_day_type"]]
            out.append("| Run | h | " + " | ".join(c for _g, c in columns) + " |")
            out.append("|---|---|" + "---|" * len(columns))
            for name in RUN_NAMES + ([CONTROL] if bench != "pressure_model_v1" else []):
                for h in pressure_v1_1.HORIZONS:
                    if name != CONTROL and not scored_at(name, h):
                        continue
                    s = entries[_key(name, "brier", "all_days", tau, h, bench)]["splits"]
                    out.append(f"| {name} | {h} | " + " | ".join(_iv(s[g].get(c)) for g, c in columns) + " |")
            out.append("")
    out.append("### CRPS (horizon 1), control − run, bp: by regime and pressure-day type\n")
    first = entries[_key(pressure_v1_1.PRIMARY, "crps")]["splits"] or {}
    columns = [(g, k) for g in ("by_regime", "by_day_type") for k in (first.get(g) or {})]
    out.append("| Run | " + " | ".join(c for _g, c in columns) + " |")
    out.append("|---|" + "---|" * len(columns))
    for name in RUN_NAMES:
        s = entries[_key(name, "crps")]["splits"] or {}
        out.append(f"| {name} | " + " | ".join(_iv((s.get(g) or {}).get(c)) for g, c in columns) + " |")
    out.append("")
    return "\n".join(out) + "\n"


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="command", required=True)
    one = sub.add_parser("panel")
    one.add_argument("--output", type=Path, required=True)
    one.set_defaults(handler=panel_command)
    two = sub.add_parser("run")
    two.add_argument("--panel", type=Path, required=True)
    two.add_argument("--run", choices=list(BENCH_RUNS.values()) + RUN_NAMES, required=True)
    two.add_argument("--horizon", type=int, choices=pressure_v1_1.HORIZONS, required=True)
    two.add_argument("--output", type=Path, required=True)
    two.set_defaults(handler=run_command)
    three = sub.add_parser("crps")
    three.add_argument("--panel", type=Path, required=True)
    three.add_argument("--run", choices=RUN_NAMES, required=True)
    three.add_argument("--output", type=Path, required=True)
    three.set_defaults(handler=crps_command)
    four = sub.add_parser("pair")
    four.add_argument("--panel", type=Path, required=True)
    four.add_argument("--runs", type=Path, required=True)
    four.add_argument("--run", choices=[CONTROL] + RUN_NAMES, required=True)
    four.add_argument("--horizon", type=int, choices=pressure_v1_1.HORIZONS, required=True)
    four.set_defaults(handler=pair_command)
    five = sub.add_parser("assemble")
    five.add_argument("--panel", type=Path, required=True)
    five.add_argument("--runs", type=Path, required=True)
    five.add_argument("--output", type=Path, required=True)
    five.add_argument("--markdown", type=Path, required=True)
    five.add_argument("--splits-markdown", type=Path, default=None)
    five.set_defaults(handler=assemble_command)
    args = parser.parse_args(argv)
    return args.handler(args)


if __name__ == "__main__":
    raise SystemExit(main())
