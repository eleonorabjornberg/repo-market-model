"""Pressure model v1.1 (#117): re-score pressure model v1 with the new inputs.

A scratch measurement, not a record: it writes pickles, JSON and Markdown to
the paths it is given, and nothing into `docs/runs/`. Every input is off in
every published declaration; this script switches them on for its own run
(`switched_on`). The inputs, the primary family, the win rule and the `on_rrp`
rule are `repo_model.pressure_v1_1`'s, committed before any scoring run.

    PYTHONPATH=src python3 scripts/pressure_v1_1.py panel --output AUG.csv
    PYTHONPATH=src python3 scripts/pressure_v1_1.py run --panel AUG.csv --run NAME --horizon H --output OUT/NAME_hH.pickle
    PYTHONPATH=src python3 scripts/pressure_v1_1.py crps --panel AUG.csv --run NAME --output OUT/crps_NAME.json
    PYTHONPATH=src python3 scripts/pressure_v1_1.py pair --panel AUG.csv --runs OUT --run NAME --horizon H
    PYTHONPATH=src python3 scripts/pressure_v1_1.py assemble --panel AUG.csv --runs OUT --output OUT/v1_1.json \\
        --markdown OUT/v1_1.md --splits-markdown OUT/splits.md

* `panel` builds the scratch panel from tracked fixtures only, with no
  network: the published panel's inputs (`funding_inputs/`), the Desk's ON RRP
  results (`on_rrp_inputs/`, #45), the H.8 first prints (`h8_inputs/`, #115)
  and the New York Fed's EFFR (`nyfed_effr_inputs/`, #98), built with the
  published manifest's cutoff and decision time. It first checks that the
  published columns of that build reproduce the published digest. It then adds
  `reserve_scarcity_state` (`scarcity.with_reserve_scarcity_state`) and the
  two announced-IORB columns (`announced_iorb.with_announced_iorb`), and keeps
  the rows up to 2025-12-31 (`docs/decisions/lockbox.md`).
* `run` scores one run at one horizon: `control` (pressure model v1 as #124
  published it), `persistence_logistic`, an input of `pressure_v1_1.CANDIDATES`,
  `joint`, or `on_rrp_plain`. The control and `joint` also score their leap
  probabilities at `onset.LEAP_JUMP_BP[h]` (#139).
* `crps` is the distribution side at horizon 1: `compare --loss crps`, the
  published funding declaration against it plus the run's columns, both
  calibrated by `conformal_pid_nested`, on one fold grid.
* `pair` pairs one run at one horizon with its two benchmarks.
* `assemble` computes the p-values, applies the win rule to the four primary
  cells and the `on_rrp` rule, and writes the tables.
"""

from __future__ import annotations

import argparse
import contextlib
import copyreg
import csv
import dataclasses
import hashlib
import importlib.util
import json
import pickle
import sys
import tempfile
from datetime import datetime, time
from pathlib import Path
from types import MappingProxyType

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))


def _script(name):
    spec = importlib.util.spec_from_file_location(name, REPO / "scripts" / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


#: Pressure model v1's published code path (#124).
v1 = _script("pressure_model_v1")

from repo_model import onset, pressure, pressure_v1_1 as v11, scarcity  # noqa: E402
from repo_model.announced_iorb import load_announcements, with_announced_iorb  # noqa: E402
from repo_model.asof import InformationRule  # noqa: E402
from repo_model.baseline import (  # noqa: E402
    benchmark_comparison_document,
    panel_sha256,
    persistence_logistic_exceedance,
    rolling_exceedance_backtest,
)
from repo_model.data import (  # noqa: E402
    DailyObservation,
    audit_panel,
    build_daily_panel,
    exceeds_bp,
    load_daily_panel,
    load_point_in_time_panel,
    verify_daily_panel,
    write_daily_panel,
)
from repo_model.evaluation_splits import load_split_declaration  # noqa: E402
from repo_model.ingest import (  # noqa: E402
    build_point_in_time_snapshot,
    load_snapshot_manifest,
    load_source_registry,
)
from repo_model.metrics import stationary_bootstrap_interval  # noqa: E402
from repo_model.pressure_v1_1 import (  # noqa: E402
    BENCHMARKS,
    CANDIDATES,
    JOINT,
    ON_RRP_FORMS,
    P_VALUE_REPLICATIONS,
    PRIMARY_CELLS,
    candidate_columns,
    columns_at_horizon,
    primary_key,
)

REGISTRY = v1.REGISTRY
SPLITS = v1.SPLITS
END = v1.END
HORIZONS = v1.HORIZONS
THRESHOLDS = (5.0, 10.0)
POOLED, ONSET = v11.POOLED, v11.ONSET
INTERVAL_LEVEL = 0.90
INTERVAL_REPLICATIONS = 2000
SNAPSHOTS = REPO / "tests" / "fixtures" / "snapshots"
RAW_ROOTS = ("funding_inputs", "on_rrp_inputs", "h8_inputs", "nyfed_effr_inputs")
EXTRA_COLUMNS = ("on_rrp", "bank_total_assets", "effr")
PUBLISHED_MANIFEST = REPO / "metadata" / "funding_panel_manifest.json"
IORB_TABLE = SNAPSHOTS / "fed-iorb-announcements" / "iorb_changes.csv"
#: Runs that also score their leap probabilities (#139).
LEAP_RUNS = ("control", JOINT)


def _proxy(mapping):
    return MappingProxyType(mapping)


copyreg.pickle(MappingProxyType, lambda proxy: (_proxy, (dict(proxy),)))


def switched_on():
    """`on_rrp` from the Desk's results, `bank_total_assets` and the state, for this run only."""

    return scarcity.measurement_declaration()


def candidates():
    """Every scored candidate run, in report order: the five inputs, `joint`, `on_rrp_plain`."""

    return [c.name for c in CANDIDATES] + [JOINT, "on_rrp_plain"]


def run_names():
    return ["control", "persistence_logistic"] + candidates()


# -- the scratch panel ---------------------------------------------------------------


def _cell(value):
    return "" if value is None else repr(float(value))


def panel_command(args) -> int:
    manifest = json.loads(PUBLISHED_MANIFEST.read_text(encoding="utf-8"))
    artifacts = [
        load_snapshot_manifest(path)
        for root in RAW_ROOTS
        for path in sorted((SNAPSHOTS / root).rglob("*.manifest.json"))
    ]
    cutoff = datetime.fromisoformat(manifest["build_cutoff"])
    decision = time.fromisoformat(manifest["decision_time"])
    retrieved = {artifact.sha256: artifact.retrieved_at for artifact in artifacts}
    with tempfile.TemporaryDirectory() as scratch, switched_on():
        work = Path(scratch)
        long_path = work / "point_in_time.csv"
        snapshot = build_point_in_time_snapshot(artifacts, long_path, registry_path=REGISTRY)
        rows = load_point_in_time_panel(long_path)
        registry = load_source_registry(REGISTRY)
        published = build_daily_panel(
            rows, registry, build_cutoff=cutoff, decision_time=decision,
            columns=tuple(manifest["built_columns"]), snapshot_retrieved_at=retrieved,
        )
        published_path = work / "published_columns.csv"
        write_daily_panel(published, published_path, source_shas=snapshot.source_shas)
        digest = verify_daily_panel(published_path, PUBLISHED_MANIFEST)
        build = build_daily_panel(
            rows, registry, build_cutoff=cutoff, decision_time=decision,
            columns=tuple(manifest["built_columns"]) + EXTRA_COLUMNS, snapshot_retrieved_at=retrieved,
        )
    if build.refusals:
        raise SystemExit(f"the build refused {dict(build.refusals)}")
    if [r.date for r in build.observations] != [r.date for r in published.observations]:
        raise SystemExit("the scratch panel's dates are not the published panel's")
    observations = scarcity.with_reserve_scarcity_state(build.observations)
    observations = with_announced_iorb(observations, load_announcements(IORB_TABLE), decision_time=decision)
    observations = [row for row in observations if row.date <= END]
    header = ["date"] + list(manifest["built_columns"]) + list(EXTRA_COLUMNS) + [
        scarcity.RESERVE_SCARCITY_STATE, "iorb_announced_change_bps", "iorb_days_to_announced_change",
    ]
    with args.output.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerow(header)
        for row in observations:
            writer.writerow([row.date.isoformat()] + [_cell(row.values.get(name)) for name in header[1:]])
    summary = {
        "output": str(args.output),
        "sha256": hashlib.sha256(args.output.read_bytes()).hexdigest(),
        "published_columns_digest": digest,
        "rows": len(observations),
        "first": observations[0].date.isoformat(),
        "last": observations[-1].date.isoformat(),
        "missing": {
            name: sum(1 for row in observations if row.values.get(name) is None) for name in header[1:]
        },
    }
    print(json.dumps(summary, indent=1))
    return 0


# -- runs ----------------------------------------------------------------------------


def _rows(panel):
    rows = load_daily_panel(panel)
    audit_panel(rows)
    if rows[-1].date > END:
        raise SystemExit(f"{panel} carries {rows[-1].date}, after {END}: a locked day")
    return rows


def run_command(args) -> int:
    from repo_model import ml
    from repo_model.data import load_stress_thresholds
    from repo_model.recalibration import NestedFoldPid

    rows = _rows(args.panel)
    splits = load_split_declaration(SPLITS)
    taus = tuple(float(tau) for tau in load_stress_thresholds(v1.THRESHOLDS)["taus_bp"])
    h = args.horizon
    registry = json.loads(REGISTRY.read_text())
    built = []

    def online(rows_, rule):
        built.append(NestedFoldPid(rows_, rule, splits=splits, refit_every=v1.REFIT_EVERY))
        return built[-1]

    def backtest(name, predictor, features, calibration=None, leap=None):
        return rolling_exceedance_backtest(
            rows, predictor=predictor, model_name=name, features=features, registry=registry,
            decision_time=v1.DECISION, taus=taus, minimum_history=v1.MINIMUM_HISTORY,
            refit_every=v1.REFIT_EVERY, end=END, horizon=h, leap_jump_bp=leap,
            online_calibration=calibration,
        )

    with switched_on():
        if args.run == "persistence_logistic":
            features = ("spread_bps",)
            report = backtest(
                "persistence_logistic", persistence_logistic_exceedance(minimum_history=v1.MINIMUM_HISTORY),
                features,
            )
        else:
            columns = () if args.run == "control" else columns_at_horizon(candidate_columns(args.run), h)
            features = v1._at_horizon(v1.GBM_FEATURES, h) + columns
            leap = onset.LEAP_JUMP_BP[h] if args.run in LEAP_RUNS else None
            raw = backtest(
                args.run,
                ml.gbm_exceedance(
                    tuple(name for name in features if name != "spread_bps"),
                    minimum_history=v1.MINIMUM_HISTORY,
                ),
                features,
                online,
                leap,
            )
            report = v1._rescored(pressure.recalibrated(raw))
            if leap is not None:
                # `pressure.recalibrated` rebuilds the report; the leap
                # probabilities are the uncalibrated model's either way.
                report = dataclasses.replace(
                    report,
                    leap_forecast=raw.leap_forecast,
                    pressure_leap_forecast=raw.pressure_leap_forecast,
                    leap_threshold_bp=raw.leap_threshold_bp,
                )
    document = {
        "run": args.run,
        "horizon": h,
        "features": list(features),
        "panel_sha256": panel_sha256(args.panel),
        "report": report,
        "calibration_account": built[0].account() if built else None,
    }
    args.output.write_bytes(pickle.dumps(document))
    print(json.dumps({
        "run": args.run, "horizon": h, "features": list(features),
        "first": report.scored_dates[0].isoformat(), "last": report.scored_dates[-1].isoformat(),
        "days": len(report.scored_dates),
        "brier": {f"{tau:g}": _mean(_brier(report, tau)) for tau in THRESHOLDS},
    }))
    return 0


def crps_command(args) -> int:
    from repo_model import cli

    columns = candidate_columns(args.run)

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


# -- pairing ---------------------------------------------------------------------------


def _load(directory, name, h):
    return pickle.loads((directory / f"{name}_h{h}.pickle").read_bytes())


def _mean(values):
    return sum(values) / len(values)


def _brier(report, tau):
    forecast, _, outcomes = report.at_tau(report.taus.index(tau))
    return [(p - y) ** 2 for p, y in zip(forecast, outcomes)]


def _interval(values, block, seed):
    lower, upper = stationary_bootstrap_interval(
        lambda idx: sum(values[i] for i in idx) / len(idx),
        len(values), block_length=block, seed=seed,
        replications=INTERVAL_REPLICATIONS, level=INTERVAL_LEVEL,
    )
    return {"lower": lower, "upper": upper, "block_length": block, "seed": seed,
            "replications": INTERVAL_REPLICATIONS, "level": INTERVAL_LEVEL}


def onset_positions(rows, scored_dates):
    """Positions into `scored_dates` of #139's onset days (`onset.onset_flags`)."""

    flags = dict(zip((row.date for row in rows), onset.onset_flags(rows)))
    return [k for k, when in enumerate(scored_dates) if flags[when]]


def pair_entries(runs, name, h, rows, splits, digest):
    """Every Brier comparison of run `name` at horizon `h` with both benchmarks, pooled and on onset days."""

    entries, members, metrics = {}, [], {}
    candidate = _load(runs, name, h)["report"]
    onsets = onset_positions(rows, candidate.scored_dates)
    benches = {"pressure_model_v1": "control", "persistence_logistic": "persistence_logistic"}
    for bench_name, run in benches.items():
        bench = _load(runs, run, h)["report"]
        if tuple(bench.scored_dates) != tuple(candidate.scored_dates):
            raise SystemExit(f"{name} h{h}: {run} was scored on another grid")
        document = benchmark_comparison_document(
            candidate, bench, panel_sha256=digest, rows=rows, declaration=splits
        )
        for tau in THRESHOLDS:
            paired = document["by_tau"][f"{tau:g}"]["paired_brier_difference"]
            differences = [b - c for b, c in zip(_brier(bench, tau), _brier(candidate, tau))]
            if abs(_mean(differences) - paired["mean"]) > 1e-12:
                raise SystemExit(f"{name} h{h} {bench_name} {tau}: daily differences disagree")
            block = paired["interval"]["block_length"]
            key = primary_key(name, POOLED, tau, h, bench_name)
            entries[key] = {
                "mean": paired["mean"], "interval": paired["interval"], "days": len(differences),
                "events": sum(1 for value in candidate.realized_bps if exceeds_bp(value, tau)),
                "splits": paired["splits"],
            }
            members.append([h, POOLED, block, key, differences])
            onset_differences = [differences[k] for k in onsets]
            onset_key = primary_key(name, ONSET, tau, h, bench_name)
            entries[onset_key] = {
                "mean": _mean(onset_differences),
                "interval": _interval(onset_differences, block, v11.p_value_seed(h, ONSET, "interval")),
                "days": len(onset_differences),
                "events": sum(1 for k in onsets if exceeds_bp(candidate.realized_bps[k], tau)),
            }
            members.append([h, ONSET, block, onset_key, onset_differences])
    for tau in THRESHOLDS:
        forecast, _, outcomes = candidate.at_tau(candidate.taus.index(tau))
        metrics[f"{tau:g}"] = pressure._metrics(list(forecast), list(outcomes))
        metrics[f"{tau:g}"]["events"] = sum(outcomes)
        metrics[f"{tau:g}"]["days"] = len(outcomes)
    return entries, members, metrics


def pair_command(args) -> int:
    rows = load_daily_panel(args.panel)
    entries, members, metrics = pair_entries(
        args.runs, args.run, args.horizon, rows, load_split_declaration(SPLITS), panel_sha256(args.panel)
    )
    path = args.runs / f"pair_{args.run}_h{args.horizon}.json"
    path.write_text(json.dumps({"entries": entries, "grid_members": members, "metrics": metrics}), encoding="utf-8")
    print(json.dumps({"pair": str(path)}))
    return 0


# -- assembly ----------------------------------------------------------------------------


def _benchmark_metrics(runs, rows):
    out = {}
    for name in ("control", "persistence_logistic"):
        out[name] = {}
        for h in HORIZONS:
            report = _load(runs, name, h)["report"]
            out[name][str(h)] = {}
            for tau in THRESHOLDS:
                forecast, _, outcomes = report.at_tau(report.taus.index(tau))
                entry = pressure._metrics(list(forecast), list(outcomes))
                entry["events"], entry["days"] = sum(outcomes), len(outcomes)
                out[name][str(h)][f"{tau:g}"] = entry
    return out


def _leap(runs, rows, splits, digest):
    """The small-leap targets (#139) for the control and `joint`, against the two leap baselines."""

    registry = json.loads(REGISTRY.read_text())
    out = {}
    for name in LEAP_RUNS:
        out[name] = {}
        for h in HORIZONS:
            report = _load(runs, name, h)["report"]
            document = onset.exceedance_onset_document(
                report, [], rows, splits, panel_sha256=digest,
                leap_rule=InformationRule(registry, ("spread_bps",), decision_time=v1.DECISION, horizon=h),
            )
            out[name][str(h)] = document["leap"]
    # The candidate against the control on the leap target, paired day by day.
    paired = {}
    for h in HORIZONS:
        control = _load(runs, "control", h)["report"]
        joint = _load(runs, JOINT, h)["report"]
        targets = onset.LeapTargets(
            rows, InformationRule(registry, ("spread_bps",), decision_time=v1.DECISION, horizon=h),
            control.leap_threshold_bp,
        )
        index = {when: k for k, when in enumerate(targets.dates)}
        labels = targets.labels("leap")
        outcomes = [1 if labels[index[when]] else 0 for when in control.scored_dates]
        differences = [
            (c - y) ** 2 - (j - y) ** 2 for c, j, y in zip(control.leap_forecast, joint.leap_forecast, outcomes)
        ]
        paired[str(h)] = {
            "mean": _mean(differences),
            "interval": _interval(differences, h + 1, v11.p_value_seed(h, "leap", "interval")),
            "events": sum(outcomes),
            "days": len(outcomes),
        }
    return {"by_run": out, "joint_vs_control": paired}


def _lead_time(runs, rows):
    lead, october = {}, {}
    models = ["control", "persistence_logistic"] + candidates()
    for tau in THRESHOLDS:
        key = f"{tau:g}"
        forecasts = {}
        for name in models:
            forecasts[name] = {}
            for h in HORIZONS:
                report = _load(runs, name, h)["report"]
                position = report.taus.index(tau)
                forecasts[name][h] = {when: curve[position] for when, curve in zip(report.scored_dates, report.forecast)}
        common = sorted(set.intersection(*(set(forecasts["control"][h]) for h in HORIZONS)))
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
                d.isoformat(): {str(h): forecasts[name][h].get(d) for h in HORIZONS}
                for d in onset_days if d.year == 2025 and d.month == 10
            }
            for name in models
        }
    return lead, october


def assemble_command(args) -> int:
    from repo_model import ml

    rows = load_daily_panel(args.panel)
    digest = panel_sha256(args.panel)
    splits = load_split_declaration(SPLITS)
    entries, grids, metrics = {}, {}, {}
    for name in candidates():
        metrics[name] = {}
        for h in HORIZONS:
            path = args.runs / f"pair_{name}_h{h}.json"
            if not path.exists():
                raise SystemExit(f"{path} is missing: run `pair --run {name} --horizon {h}` first")
            paired = json.loads(path.read_text())
            entries.update(paired["entries"])
            metrics[name][str(h)] = paired["metrics"]
            for h_, day_set, block, key, differences in paired["grid_members"]:
                grids.setdefault((h_, day_set, block), []).append((key, differences))
    crps = {}
    for name in candidates():
        path = args.runs / f"crps_{name}.json"
        comparison = json.loads(path.read_text())["comparison"]
        last = max(origin["scored_date"] for origin in comparison["per_origin"])
        if last > END.isoformat():
            raise SystemExit(f"{name}: CRPS scored a locked day")
        key = f"{name}|crps"
        crps[name] = {
            "mean": comparison["mean_difference_bps"],
            "interval": comparison["mean_difference_interval"],
            "days": comparison["origin_count"],
            "control_crps_bps": comparison["model_a"]["crps_bps"],
            "candidate_crps_bps": comparison["model_b"]["crps_bps"],
            "first": min(origin["scored_date"] for origin in comparison["per_origin"]),
            "last": last,
            "splits": comparison.get("splits"),
            "onset": json.loads(path.read_text()).get("onset"),
        }
        entries[key] = crps[name]
        grids.setdefault((1, "crps", comparison["mean_difference_interval"]["block_length"]), []).append(
            (key, [origin["difference_bps"] for origin in comparison["per_origin"]])
        )
    for (h, day_set, block), members in sorted(grids.items(), key=lambda item: str(item[0])):
        lengths = {len(values) for _key, values in members}
        if len(lengths) != 1:
            raise SystemExit(f"grid h{h} {day_set}: lengths {sorted(lengths)}")
        p_values = ml.paired_bootstrap_p_values(
            [values for _key, values in members], block_length=block,
            seed=v11.p_value_seed(h, day_set), replications=P_VALUE_REPLICATIONS,
        )
        for (key, _values), (p_improve, p_worse) in zip(members, p_values):
            entries[key]["p_improve"] = p_improve
            entries[key]["p_worse"] = p_worse

    primary = {primary_key(*cell): entries[primary_key(*cell)] for cell in PRIMARY_CELLS}
    verdict = v11.classify_primary(primary)
    for key in primary:
        entries[key]["primary"] = True
        entries[key]["holm_improve"] = verdict["holm_improve"][key]
        entries[key]["holm_worse"] = verdict["holm_worse"][key]

    forms = {}
    for form, _columns in ON_RRP_FORMS:
        forms[form] = {
            "candidate_crps_bps": crps[form]["candidate_crps_bps"],
            "crps": crps[form],
            "brier_5": entries[primary_key(form, POOLED, 5.0, 1, "pressure_model_v1")],
            "brier_10": entries[primary_key(form, POOLED, 10.0, 1, "pressure_model_v1")],
        }
    on_rrp = v11.on_rrp_rule(forms)

    lead, october = _lead_time(args.runs, rows)
    document = {
        "directive": "#117",
        "status": "scratch measurement; not a record, nothing published moves",
        "panel_sha256": digest,
        "primary": verdict,
        "on_rrp_rule": on_rrp,
        "comparisons": entries,
        "metrics": metrics,
        "benchmark_metrics": _benchmark_metrics(args.runs, rows),
        "crps": crps,
        "leap": _leap(args.runs, rows, splits, digest),
        "lead_time": lead,
        "october_2025_onset": october,
        "features": {
            name: {str(h): _load(args.runs, name, h)["features"] for h in HORIZONS} for name in run_names()
        },
    }
    args.output.write_text(json.dumps(document, indent=1, sort_keys=True, default=str) + "\n", encoding="utf-8")
    args.markdown.write_text(_markdown(document), encoding="utf-8")
    if args.splits_markdown is not None:
        args.splits_markdown.write_text(_splits_markdown(document), encoding="utf-8")
    print(json.dumps({"output": str(args.output), "passed": verdict["passed"], "on_rrp_met": on_rrp["met"],
                      "on_rrp_form": on_rrp["form"]}))
    return 0


# -- tables ------------------------------------------------------------------------------


def _iv(entry, places=4):
    interval = entry["interval"]
    return f"{entry['mean']:+.{places}f} [{interval['lower']:+.{places}f}, {interval['upper']:+.{places}f}]"


def _p(entry):
    mark = ""
    if entry.get("primary"):
        mark = " ✓" if entry.get("holm_improve") else (" ✗" if entry.get("holm_worse") else "")
    return f"{entry['p_improve']:.4f}{mark}"


def _fmt(value, places=4):
    return "–" if value is None else f"{value:.{places}f}"


def _markdown(document) -> str:
    entries = document["comparisons"]
    verdict = document["primary"]
    out = []
    out.append("### Primary cells (the only ones that decide): joint, +5 bp, h = 1\n")
    out.append(
        f"Holm at a {verdict['family_level']:.0%} family-wise level over {verdict['family_size']} cells, "
        f"one-sided paired stationary-bootstrap p-values ({P_VALUE_REPLICATIONS} replications). "
        "Paired difference = benchmark − candidate: positive favours v1.1. 90% stationary-bootstrap intervals.\n"
    )
    out.append("| Day set | Against | Days | Events | Paired difference [90%] | p improve | p worse | Holm |")
    out.append("|---|---|---|---|---|---|---|---|")
    for cell in PRIMARY_CELLS:
        e = entries[primary_key(*cell)]
        holm = "improvement" if e["holm_improve"] else ("deterioration" if e["holm_worse"] else "neither")
        events = e.get("events")
        out.append(
            f"| {cell[1]} | {cell[4]} | {e['days']} | {'–' if events is None else events} | {_iv(e)} | "
            f"{e['p_improve']:.4f} | {e['p_worse']:.4f} | {holm} |"
        )
    out.append(f"\n**Win rule: {'PASSED' if verdict['passed'] else 'NOT PASSED'}.**\n")
    rule = document["on_rrp_rule"]
    out.append("### `on_rrp` (Eleonora's rule of 2 October 2026)\n")
    out.append("| Form | Pooled CRPS (bp) | CRPS, control − form [90%] | Brier +5, h=1 [90%] | Brier +10, h=1 [90%] |")
    out.append("|---|---|---|---|---|")
    for form, _c in ON_RRP_FORMS:
        out.append(
            f"| {form} | {document['crps'][form]['candidate_crps_bps']:.4f} | {_iv(document['crps'][form])} | "
            f"{_iv(entries[primary_key(form, POOLED, 5.0, 1, 'pressure_model_v1')])} | "
            f"{_iv(entries[primary_key(form, POOLED, 10.0, 1, 'pressure_model_v1')])} |"
        )
    out.append(f"\nForm by pooled CRPS: `{rule['form']}`. **Rule {'met' if rule['met'] else 'not met'}.**\n")
    for day_set, title in ((POOLED, "all scored days"), (ONSET, "onset days (#139)")):
        out.append(f"### Exploratory: Brier, {title}: paired difference [90%], one-sided p for improvement\n")
        out.append("| Candidate | h | +5 vs v1 | p | +5 vs persistence-logistic | p | +10 vs v1 | p | +10 vs persistence-logistic | p |")
        out.append("|---|---|---|---|---|---|---|---|---|---|")
        for name in candidates():
            for h in HORIZONS:
                cells = []
                for tau in THRESHOLDS:
                    for bench in BENCHMARKS:
                        e = entries[primary_key(name, day_set, tau, h, bench)]
                        cells += [_iv(e), _p(e)]
                out.append(f"| {name} | {h} | " + " | ".join(cells) + " |")
        out.append("")
    out.append("### Exploratory: Brier, CORP decomposition and average precision, recalibrated forecasts\n")
    out.append("| Run | h | τ | Brier | MCB | DSC | UNC | AP | events/days |")
    out.append("|---|---|---|---|---|---|---|---|---|")
    rows_ = [(n, document["benchmark_metrics"][n]) for n in ("control", "persistence_logistic")]
    rows_ += [(n, document["metrics"][n]) for n in candidates()]
    for name, by_h in rows_:
        for h in HORIZONS:
            for tau in ("5", "10"):
                m = by_h[str(h)][tau]
                d = m.get("decomposition") or {}
                out.append(
                    f"| {name} | {h} | +{tau} | {_fmt(m['brier'])} | {_fmt(d.get('miscalibration'))} | "
                    f"{_fmt(d.get('discrimination'))} | {_fmt(d.get('uncertainty'))} | "
                    f"{_fmt(m.get('average_precision'), 3)} | {m['events']}/{m['days']} |"
                )
    out.append("")
    out.append("### Exploratory: small leaps (#139), h = 1 to 5\n")
    out.append("| h | J_h | run | leap events | Brier vs leap climatology [90%] | vs leap persistence-logistic [90%] | verdict |")
    out.append("|---|---|---|---|---|---|---|")
    for name, by_h in document["leap"]["by_run"].items():
        for h in HORIZONS:
            leap = by_h[str(h)]
            target = leap["targets"]["leap"][onset.GROUP_ALL]
            cells = []
            for base in (onset.LEAP_CALENDAR_CLIMATOLOGY, onset.LEAP_PERSISTENCE_LOGISTIC):
                cells.append(_iv(target["paired"][base]))
            out.append(
                f"| {h} | {leap['threshold_bp']:.2f} | {name} | {target['events']} | {cells[0]} | {cells[1]} | "
                f"{leap['targets']['leap']['verdict']['result']} |"
            )
    out.append("\n| h | joint vs control on the leap target, Brier difference [90%] | events/days |")
    out.append("|---|---|---|")
    for h in HORIZONS:
        e = document["leap"]["joint_vs_control"][str(h)]
        out.append(f"| {h} | {_iv(e)} | {e['events']}/{e['days']} |")
    out.append("")
    out.append("### Exploratory: CRPS, horizon 1: published declaration − candidate, bp\n")
    out.append("| Candidate | Scored | CRPS control | CRPS candidate | Difference [90%] | p improve | p worse |")
    out.append("|---|---|---|---|---|---|---|")
    for name in candidates():
        e = document["crps"][name]
        out.append(
            f"| {name} | {e['first']} to {e['last']} ({e['days']}) | {e['control_crps_bps']:.4f} | "
            f"{e['candidate_crps_bps']:.4f} | {_iv(e)} | {e['p_improve']:.4f} | {e['p_worse']:.4f} |"
        )
    out.append("")
    out.append("### Exploratory: lead time to onset (`pressure.onsets`), alarm levels 0.2 and 0.5\n")
    for tau, entry in document["lead_time"].items():
        out.append(f"**+{tau} bp**: {len(entry['onsets'])} onsets\n")
        out.append("| Run | flagged at 0.2 | mean lead at 0.2 | flagged at 0.5 | mean lead at 0.5 |")
        out.append("|---|---|---|---|---|")
        for name, (low, high) in entry["by_model"].items():
            out.append(
                f"| {name} | {low['flagged']}/{low['onsets']} | {low['mean_lead_days']:.2f} | "
                f"{high['flagged']}/{high['onsets']} | {high['mean_lead_days']:.2f} |"
            )
        out.append("")
    out.append("### Exploratory: the October 2025 onset, probability on the onset day, h = 1 to 5\n")
    for tau, by_model in document["october_2025_onset"].items():
        days = sorted({d for model in by_model.values() for d in model})
        for day in days:
            out.append(f"**+{tau} bp, onset {day}**\n")
            out.append("| Run | h=1 | h=2 | h=3 | h=4 | h=5 |\n|---|---|---|---|---|---|")
            for name, by_day in by_model.items():
                values = by_day.get(day, {})
                out.append(f"| {name} | " + " | ".join(
                    "–" if values.get(str(h)) is None else f"{values[str(h)]:.3f}" for h in HORIZONS) + " |")
            out.append("")
    return "\n".join(out) + "\n"


def _split_iv(entry):
    if not entry or entry.get("mean") is None:
        return "–"
    interval = entry.get("interval") or {}
    if interval.get("lower") is None:
        return f"{entry['mean']:+.4f}"
    return f"{entry['mean']:+.4f} [{interval['lower']:+.4f}, {interval['upper']:+.4f}]"


def _splits_markdown(document) -> str:
    entries = document["comparisons"]
    out = []
    for tau in THRESHOLDS:
        for bench in BENCHMARKS:
            out.append(f"### +{tau:g} bp against {bench}: by regime and pressure-day type\n")
            first = entries[primary_key(JOINT, POOLED, tau, 1, bench)]["splits"]
            columns = [("by_regime", k) for k in first["by_regime"]] + [("by_day_type", k) for k in first["by_day_type"]]
            out.append("| Candidate | h | " + " | ".join(c for _g, c in columns) + " |")
            out.append("|---|---|" + "---|" * len(columns))
            for name in candidates():
                for h in HORIZONS:
                    s = entries[primary_key(name, POOLED, tau, h, bench)]["splits"]
                    out.append(f"| {name} | {h} | " + " | ".join(_split_iv(s[g].get(c)) for g, c in columns) + " |")
            out.append("")
    return "\n".join(out) + "\n"


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="command", required=True)
    panel = sub.add_parser("panel")
    panel.add_argument("--output", type=Path, required=True)
    panel.set_defaults(handler=panel_command)
    run = sub.add_parser("run")
    run.add_argument("--panel", type=Path, required=True)
    run.add_argument("--run", choices=run_names(), required=True)
    run.add_argument("--horizon", type=int, choices=HORIZONS, required=True)
    run.add_argument("--output", type=Path, required=True)
    run.set_defaults(handler=run_command)
    crps = sub.add_parser("crps")
    crps.add_argument("--panel", type=Path, required=True)
    crps.add_argument("--run", choices=candidates(), required=True)
    crps.add_argument("--output", type=Path, required=True)
    crps.set_defaults(handler=crps_command)
    pair = sub.add_parser("pair")
    pair.add_argument("--panel", type=Path, required=True)
    pair.add_argument("--runs", type=Path, required=True)
    pair.add_argument("--run", choices=candidates(), required=True)
    pair.add_argument("--horizon", type=int, choices=HORIZONS, required=True)
    pair.set_defaults(handler=pair_command)
    assemble = sub.add_parser("assemble")
    assemble.add_argument("--panel", type=Path, required=True)
    assemble.add_argument("--runs", type=Path, required=True)
    assemble.add_argument("--output", type=Path, required=True)
    assemble.add_argument("--markdown", type=Path, required=True)
    assemble.add_argument("--splits-markdown", type=Path, default=None)
    assemble.set_defaults(handler=assemble_command)
    args = parser.parse_args(argv)
    return args.handler(args)


if __name__ == "__main__":
    raise SystemExit(main())
