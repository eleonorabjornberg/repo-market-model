"""The scarcity-conditioned calendar (#128): score its two forms against v1.1 and both benchmarks.

A scratch measurement, not a record: it writes pickles, JSON and Markdown to
the paths it is given, and nothing into `docs/runs/`. Every input is off in
every published declaration; the state and its inputs are switched on for
these runs only (`scripts/pressure_v1_1.py`'s `switched_on`). The forms, state
mappings, primary family and win rule are `repo_model.scarcity_calendar`'s,
committed before any scoring run.

The panel and the control come from `scripts/pressure_v1_1.py` (#117), run
unchanged into the same directory:

* its `panel` is the scratch panel (published columns verified, rows to
  2025-12-31);
* its `joint` run is the control, pressure model v1.1 (v1 with all five #117
  inputs), because #117 passed its win rule (PR #204);
* its `control` run is pressure model v1, reported as an exploratory
  comparison while #205 asks whether that pass counts;
* its `persistence_logistic` run is the persistence-logistic benchmark.

This script adds:

    PYTHONPATH=src python3 scripts/scarcity_calendar.py run --panel AUG.csv --run NAME --horizon H --output OUT/NAME_hH.pickle
    PYTHONPATH=src python3 scripts/scarcity_calendar.py pair --panel AUG.csv --runs OUT --run NAME --horizon H
    PYTHONPATH=src python3 scripts/scarcity_calendar.py assemble --panel AUG.csv --runs OUT --output OUT/sc.json \\
        --markdown OUT/sc.md --splits-markdown OUT/splits.md

* `run` scores `calendar_climatology` (the benchmark, as pressure model v1 ran
  it) or one `scarcity_calendar.CANDIDATES` at one horizon, recalibrated out
  of fold (`pressure.recalibrated`) as the control is. The two primary
  candidates also score their leap probabilities at `onset.LEAP_JUMP_BP[h]`
  (#139), the uncalibrated model's.
* `pair` pairs one candidate at one horizon with v1.1, the
  persistence-logistic, calendar climatology and v1, pooled and on onset days.
* `assemble` computes the p-values, applies the win rule to the eight primary
  cells, and writes the tables, the 2021-23 quarter-end check and October 2025.

**CRPS is not reported.** Both forms are direct models of the exceedance label
(#114): they have no predictive distribution. Carrying the structure to the
gbm quantile model would need each scheduled term x state declared as a
composed feature in `contract`, an interface change outside this directive.
"""

from __future__ import annotations

import argparse
import copyreg
import dataclasses
import importlib.util
import json
import pickle
import sys
from pathlib import Path
from types import MappingProxyType

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))


def _script(name):
    spec = importlib.util.spec_from_file_location(name, REPO / "scripts" / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


#: #117's script: the panel, the control and the shared helpers.
v11s = _script("pressure_v1_1")
v1 = v11s.v1

from repo_model import onset, pressure, scarcity, scarcity_calendar as sc  # noqa: E402
from repo_model.asof import InformationRule  # noqa: E402
from repo_model.baseline import (  # noqa: E402
    benchmark_comparison_document,
    calendar_climatology_exceedance,
    panel_sha256,
    rolling_exceedance_backtest,
)
from repo_model.data import exceeds_bp, load_daily_panel  # noqa: E402
from repo_model.evaluation_splits import load_split_declaration  # noqa: E402
from repo_model.scarcity_calendar import (  # noqa: E402
    CANDIDATES,
    CONTROL,
    ONSET,
    P_VALUE_REPLICATIONS,
    POOLED,
    PRIMARY_CANDIDATES,
    PRIMARY_CELLS,
    REGIME_CHECK_YEARS,
    primary_key,
)

REGISTRY = v1.REGISTRY
SPLITS = v1.SPLITS
END = v1.END
HORIZONS = v1.HORIZONS
THRESHOLDS = (5.0, 10.0)

#: Benchmark name -> the run file it is read from. v1.1 and v1 are #117's runs.
BENCHMARK_RUNS = {
    CONTROL: "joint",
    "persistence_logistic": "persistence_logistic",
    "calendar_climatology": "calendar_climatology",
    "pressure_model_v1": "control",
}
#: The benchmarks every candidate is paired with, in report order.
BENCHMARK_ORDER = tuple(BENCHMARK_RUNS)


def _proxy(mapping):
    return MappingProxyType(mapping)


copyreg.pickle(MappingProxyType, lambda proxy: (_proxy, (dict(proxy),)))


def candidates():
    return [c.name for c in CANDIDATES]


def _not_blind(name):
    return " (b: not blind, added after #157)" if sc.candidate(name).state == "two_level" else ""


# -- runs ----------------------------------------------------------------------------


def run_command(args) -> int:
    from repo_model import ml
    from repo_model.data import load_stress_thresholds

    rows = v11s._rows(args.panel)
    splits = load_split_declaration(SPLITS)
    taus = tuple(float(tau) for tau in load_stress_thresholds(v1.THRESHOLDS)["taus_bp"])
    h = args.horizon
    registry = json.loads(REGISTRY.read_text())

    def backtest(name, predictor, features, leap=None):
        return rolling_exceedance_backtest(
            rows, predictor=predictor, model_name=name, features=features, registry=registry,
            decision_time=v1.DECISION, taus=taus, minimum_history=v1.MINIMUM_HISTORY,
            refit_every=v1.REFIT_EVERY, end=END, horizon=h, leap_jump_bp=leap,
        )

    raw_brier = None
    with v11s.switched_on():
        if args.run == "calendar_climatology":
            features = v1.CALENDAR_FEATURES
            report = backtest(
                "calendar_climatology",
                calendar_climatology_exceedance(splits, minimum_history=v1.MINIMUM_HISTORY),
                features,
            )
        else:
            entry = sc.candidate(args.run)
            features = sc.features_at_horizon(args.run, h)
            leap = onset.LEAP_JUMP_BP[h] if args.run in PRIMARY_CANDIDATES else None
            raw = backtest(
                args.run,
                ml._scarcity_calendar_predictor(
                    entry.form, features, splits, sc.STATE_FORMS[entry.state],
                    minimum_history=v1.MINIMUM_HISTORY,
                ),
                features,
                leap,
            )
            raw_brier = {f"{tau:g}": v11s._mean(v11s._brier(raw, tau)) for tau in THRESHOLDS}
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
        "raw_brier": raw_brier,
    }
    args.output.write_bytes(pickle.dumps(document))
    print(json.dumps({
        "run": args.run, "horizon": h, "features": list(features),
        "first": report.scored_dates[0].isoformat(), "last": report.scored_dates[-1].isoformat(),
        "days": len(report.scored_dates),
        "brier": {f"{tau:g}": v11s._mean(v11s._brier(report, tau)) for tau in THRESHOLDS},
        "raw_brier": raw_brier,
    }))
    return 0


# -- pairing ---------------------------------------------------------------------------


def _load(runs, name, h):
    return v11s._load(runs, BENCHMARK_RUNS.get(name, name), h)


def pair_entries(runs, name, h, rows, splits, digest):
    """Every Brier comparison of candidate `name` at `h` with the four benchmarks, pooled and on onset days."""

    entries, members, metrics = {}, [], {}
    candidate = _load(runs, name, h)["report"]
    onsets = v11s.onset_positions(rows, candidate.scored_dates)
    for bench_name in BENCHMARK_ORDER:
        bench = _load(runs, bench_name, h)["report"]
        if tuple(bench.scored_dates) != tuple(candidate.scored_dates):
            raise SystemExit(f"{name} h{h}: {bench_name} was scored on another grid")
        document = benchmark_comparison_document(
            candidate, bench, panel_sha256=digest, rows=rows, declaration=splits
        )
        for tau in THRESHOLDS:
            paired = document["by_tau"][f"{tau:g}"]["paired_brier_difference"]
            differences = [b - c for b, c in zip(v11s._brier(bench, tau), v11s._brier(candidate, tau))]
            if abs(v11s._mean(differences) - paired["mean"]) > 1e-12:
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
                "mean": v11s._mean(onset_differences),
                "interval": v11s._interval(onset_differences, block, sc.p_value_seed(h, ONSET, "interval")),
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
    path = args.runs / f"sc_pair_{args.run}_h{args.horizon}.json"
    path.write_text(json.dumps({"entries": entries, "grid_members": members, "metrics": metrics}), encoding="utf-8")
    print(json.dumps({"pair": str(path)}))
    return 0


# -- assembly ----------------------------------------------------------------------------


def _benchmark_metrics(runs):
    out = {}
    for name in BENCHMARK_ORDER:
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
    """The small-leap targets (#139) for the control and the primary forms, against the leap baselines."""

    registry = json.loads(REGISTRY.read_text())
    out = {}
    for name in (CONTROL,) + PRIMARY_CANDIDATES:
        out[name] = {}
        for h in HORIZONS:
            report = _load(runs, name, h)["report"]
            document = onset.exceedance_onset_document(
                report, [], rows, splits, panel_sha256=digest,
                leap_rule=InformationRule(registry, ("spread_bps",), decision_time=v1.DECISION, horizon=h),
            )
            out[name][str(h)] = document["leap"]
    paired = {}
    for name in PRIMARY_CANDIDATES:
        paired[name] = {}
        for h in HORIZONS:
            control = _load(runs, CONTROL, h)["report"]
            form = _load(runs, name, h)["report"]
            targets = onset.LeapTargets(
                rows, InformationRule(registry, ("spread_bps",), decision_time=v1.DECISION, horizon=h),
                control.leap_threshold_bp,
            )
            index = {when: k for k, when in enumerate(targets.dates)}
            labels = targets.labels("leap")
            outcomes = [1 if labels[index[when]] else 0 for when in control.scored_dates]
            differences = [
                (c - y) ** 2 - (f - y) ** 2
                for c, f, y in zip(control.leap_forecast, form.leap_forecast, outcomes)
            ]
            paired[name][str(h)] = {
                "mean": v11s._mean(differences),
                "interval": v11s._interval(differences, h + 1, sc.p_value_seed(h, name, "leap", "interval")),
                "events": sum(outcomes),
                "days": len(outcomes),
            }
    return {"by_run": out, "form_vs_control": paired}


def _forecasts(runs, name, tau):
    out = {}
    for h in HORIZONS:
        report = _load(runs, name, h)["report"]
        position = report.taus.index(tau)
        out[h] = {when: curve[position] for when, curve in zip(report.scored_dates, report.forecast)}
    return out


def _lead_time(runs, rows):
    lead, october = {}, {}
    models = list(BENCHMARK_ORDER) + candidates()
    for tau in THRESHOLDS:
        key = f"{tau:g}"
        forecasts = {name: _forecasts(runs, name, tau) for name in models}
        common = sorted(set.intersection(*(set(forecasts[CONTROL][h]) for h in HORIZONS)))
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


def _regime_check(runs, rows, splits):
    """Item 4: every model's probability on the 2021-23 quarter-ends, with the as-of state.

    The quarter-ends are the scored days whose pressure-day type is
    `quarter_end` under the split declaration. The state is the one a forecast
    of that day read at its decision instant at horizon 1
    (`scarcity.pressure_days_by_state`, the fold grid's own reads).
    """

    registry = json.loads(REGISTRY.read_text())
    with v11s.switched_on():
        scored = scarcity.pressure_days_by_state(
            rows, registry=registry, decision_time=v1.DECISION,
            minimum_history=v1.MINIMUM_HISTORY, end=END,
        )
    state = {day.day: day.state for day in scored}
    by_date = {row.date: row for row in rows}
    models = list(BENCHMARK_ORDER) + candidates()
    out = {}
    for tau in THRESHOLDS:
        key = f"{tau:g}"
        forecasts = {name: _forecasts(runs, name, tau) for name in models}
        days = sorted(
            when for when in forecasts[CONTROL][1]
            if when.year in REGIME_CHECK_YEARS and splits.day_type(by_date[when].values) == "quarter_end"
        )
        table = [
            {
                "date": when.isoformat(),
                "state": state.get(when),
                "spread_bps": by_date[when].spread_bps,
                "event": exceeds_bp(by_date[when].spread_bps, tau),
                "h1": {name: forecasts[name][1].get(when) for name in models},
            }
            for when in days
        ]
        summary = {}
        for name in models:
            summary[name] = {}
            for h in HORIZONS:
                values = [forecasts[name][h][when] for when in days if when in forecasts[name][h]]
                summary[name][str(h)] = {
                    "days": len(values),
                    "mean": v11s._mean(values) if values else None,
                    "max": max(values) if values else None,
                }
        out[key] = {"days": table, "summary": summary, "events": sum(1 for entry in table if entry["event"])}
    return out


def assemble_command(args) -> int:
    from repo_model import ml

    rows = load_daily_panel(args.panel)
    digest = panel_sha256(args.panel)
    splits = load_split_declaration(SPLITS)
    entries, grids, metrics = {}, {}, {}
    for name in candidates():
        metrics[name] = {}
        for h in HORIZONS:
            path = args.runs / f"sc_pair_{name}_h{h}.json"
            if not path.exists():
                raise SystemExit(f"{path} is missing: run `pair --run {name} --horizon {h}` first")
            paired = json.loads(path.read_text())
            entries.update(paired["entries"])
            metrics[name][str(h)] = paired["metrics"]
            for h_, day_set, block, key, differences in paired["grid_members"]:
                grids.setdefault((h_, day_set, block), []).append((key, differences))
    for (h, day_set, block), members in sorted(grids.items(), key=lambda item: str(item[0])):
        lengths = {len(values) for _key, values in members}
        if len(lengths) != 1:
            raise SystemExit(f"grid h{h} {day_set}: lengths {sorted(lengths)}")
        p_values = ml.paired_bootstrap_p_values(
            [values for _key, values in members], block_length=block,
            seed=sc.p_value_seed(h, day_set), replications=P_VALUE_REPLICATIONS,
        )
        for (key, _values), (p_improve, p_worse) in zip(members, p_values):
            entries[key]["p_improve"] = p_improve
            entries[key]["p_worse"] = p_worse

    primary = {primary_key(*cell): entries[primary_key(*cell)] for cell in PRIMARY_CELLS}
    verdict = sc.classify_primary(primary)
    for key in primary:
        entries[key]["primary"] = True
        entries[key]["holm_improve"] = verdict["holm_improve"][key]
        entries[key]["holm_worse"] = verdict["holm_worse"][key]

    raw_brier = {name: {str(h): _load(args.runs, name, h)["raw_brier"] for h in HORIZONS} for name in candidates()}
    lead, october = _lead_time(args.runs, rows)
    document = {
        "directive": "#128",
        "status": "scratch measurement; not a record, nothing published moves",
        "panel_sha256": digest,
        "control": CONTROL,
        "primary": verdict,
        "comparisons": entries,
        "metrics": metrics,
        "raw_brier": raw_brier,
        "benchmark_metrics": _benchmark_metrics(args.runs),
        "leap": _leap(args.runs, rows, splits, digest),
        "lead_time": lead,
        "october_2025_onset": october,
        "regime_check": _regime_check(args.runs, rows, splits),
        "features": {
            name: {str(h): _load(args.runs, name, h)["features"] for h in HORIZONS}
            for name in list(BENCHMARK_ORDER) + candidates()
        },
    }
    args.output.write_text(json.dumps(document, indent=1, sort_keys=True, default=str) + "\n", encoding="utf-8")
    args.markdown.write_text(_markdown(document), encoding="utf-8")
    if args.splits_markdown is not None:
        args.splits_markdown.write_text(_splits_markdown(document), encoding="utf-8")
    print(json.dumps({
        "output": str(args.output),
        "passed": {name: entry["passed"] for name, entry in verdict["by_form"].items()},
    }))
    return 0


# -- tables ------------------------------------------------------------------------------

_iv = v11s._iv
_fmt = v11s._fmt
_split_iv = v11s._split_iv


def _p(entry):
    mark = ""
    if entry.get("primary"):
        mark = " ✓" if entry.get("holm_improve") else (" ✗" if entry.get("holm_worse") else "")
    return f"{entry['p_improve']:.4f}{mark}"


def _markdown(document) -> str:
    entries = document["comparisons"]
    verdict = document["primary"]
    out = []
    out.append("### Primary cells (the only ones that decide): each form with the state alone (a), +5 bp, h = 1\n")
    out.append(
        f"Holm at a {verdict['family_level']:.0%} family-wise level over {verdict['family_size']} cells, "
        f"one-sided paired stationary-bootstrap p-values ({P_VALUE_REPLICATIONS} replications). "
        "Paired difference = benchmark − candidate: positive favours the form. 90% stationary-bootstrap "
        "intervals. The control is pressure model v1.1.\n"
    )
    out.append("| Form | Day set | Against | Days | Events | Paired difference [90%] | p improve | p worse | Holm |")
    out.append("|---|---|---|---|---|---|---|---|---|")
    for cell in PRIMARY_CELLS:
        key = primary_key(*cell)
        e = entries[key]
        holm = "improvement" if e["holm_improve"] else ("deterioration" if e["holm_worse"] else "neither")
        out.append(
            f"| {cell[0]} | {cell[1]} | {cell[4]} | {e['days']} | {e['events']} | {_iv(e)} | "
            f"{e['p_improve']:.4f} | {e['p_worse']:.4f} | {holm} |"
        )
    out.append("")
    for name, entry in verdict["by_form"].items():
        out.append(f"**{name}: win rule {'PASSED' if entry['passed'] else 'NOT PASSED'}.**\n")
    for title, day_set in (("all scored days", POOLED), ("onset days (#139)", ONSET)):
        out.append(f"### Exploratory: Brier, {title}: paired difference [90%], one-sided p for improvement\n")
        out.append("✓ / ✗ marks a primary cell that survives Holm as an improvement / a deterioration.\n")
        for tau in THRESHOLDS:
            out.append(f"**+{tau:g} bp**\n")
            out.append("| Candidate | h | " + " | ".join(f"vs {b} | p" for b in BENCHMARK_ORDER) + " |")
            out.append("|---|---|" + "---|---|" * len(BENCHMARK_ORDER))
            for name in candidates():
                for h in HORIZONS:
                    cells = []
                    for bench in BENCHMARK_ORDER:
                        e = entries[primary_key(name, day_set, tau, h, bench)]
                        cells += [_iv(e), _p(e)]
                    out.append(f"| {name}{_not_blind(name)} | {h} | " + " | ".join(cells) + " |")
            out.append("")
    out.append("### Exploratory: Brier, CORP decomposition and average precision\n")
    out.append(
        "Candidates recalibrated out of fold (`pressure.recalibrated`), as the control is; the raw Brier "
        "before recalibration is the last column.\n"
    )
    out.append("| Run | h | τ | Brier | reliability (MCB) | resolution (DSC) | uncertainty | AP | events/days | raw Brier |")
    out.append("|---|---|---|---|---|---|---|---|---|---|")
    rows_ = [(n, document["benchmark_metrics"][n], None) for n in BENCHMARK_ORDER]
    rows_ += [(n, document["metrics"][n], document["raw_brier"][n]) for n in candidates()]
    for name, by_h, raw in rows_:
        for h in HORIZONS:
            for tau in ("5", "10"):
                m = by_h[str(h)][tau]
                d = m.get("decomposition") or {}
                out.append(
                    f"| {name} | {h} | +{tau} | {_fmt(m['brier'])} | {_fmt(d.get('reliability'))} | "
                    f"{_fmt(d.get('resolution'))} | {_fmt(d.get('uncertainty'))} | "
                    f"{_fmt(m.get('average_precision'), 3)} | {m['events']}/{m['days']} | "
                    f"{_fmt(None if raw is None else raw[str(h)][tau])} |"
                )
    out.append("")
    out.append("### Exploratory: the 2021–23 quarter-ends (item 4), probability of +5 bp\n")
    check = document["regime_check"]["5"]
    out.append(
        f"{len(check['days'])} scored quarter-ends in {REGIME_CHECK_YEARS[0]}–{REGIME_CHECK_YEARS[-1]}; "
        f"{check['events']} above +5 bp. Mean (max) probability across them, by horizon:\n"
    )
    out.append("| Run | " + " | ".join(f"h={h}" for h in HORIZONS) + " |")
    out.append("|---|" + "---|" * len(HORIZONS))
    for name, by_h in check["summary"].items():
        cells = []
        for h in HORIZONS:
            e = by_h[str(h)]
            cells.append("–" if e["mean"] is None else f"{e['mean']:.4f} ({e['max']:.4f})")
        out.append(f"| {name} | " + " | ".join(cells) + " |")
    out.append("\nDay by day, horizon 1:\n")
    models = list(BENCHMARK_ORDER) + candidates()
    out.append("| Date | state | spread (bp) | " + " | ".join(models) + " |")
    out.append("|---|---|---|" + "---|" * len(models))
    for entry in check["days"]:
        out.append(
            f"| {entry['date']} | {_fmt(entry['state'], 0)} | {entry['spread_bps']:.1f} | "
            + " | ".join(_fmt(entry["h1"][name], 3) for name in models) + " |"
        )
    out.append("")
    out.append("### Exploratory: small leaps (#139), h = 1 to 5\n")
    out.append("| h | J_h | run | leap events | Brier vs leap climatology [90%] | vs leap persistence-logistic [90%] | verdict |")
    out.append("|---|---|---|---|---|---|---|")
    for name, by_h in document["leap"]["by_run"].items():
        for h in HORIZONS:
            leap = by_h[str(h)]
            target = leap["targets"]["leap"][onset.GROUP_ALL]
            cells = [_iv(target["paired"][base]) for base in (onset.LEAP_CALENDAR_CLIMATOLOGY, onset.LEAP_PERSISTENCE_LOGISTIC)]
            out.append(
                f"| {h} | {leap['threshold_bp']:.2f} | {name} | {target['events']} | {cells[0]} | {cells[1]} | "
                f"{leap['targets']['leap']['verdict']['result']} |"
            )
    out.append("\n| Form | h | form vs control on the leap target, Brier difference [90%] | events/days |")
    out.append("|---|---|---|---|")
    for name, by_h in document["leap"]["form_vs_control"].items():
        for h in HORIZONS:
            e = by_h[str(h)]
            out.append(f"| {name} | {h} | {_iv(e)} | {e['events']}/{e['days']} |")
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


def _splits_markdown(document) -> str:
    entries = document["comparisons"]
    out = []
    for tau in THRESHOLDS:
        for bench in BENCHMARK_ORDER:
            out.append(f"### +{tau:g} bp against {bench}: by regime and pressure-day type\n")
            first = entries[primary_key(PRIMARY_CANDIDATES[0], POOLED, tau, 1, bench)]["splits"]
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
    run = sub.add_parser("run")
    run.add_argument("--panel", type=Path, required=True)
    run.add_argument("--run", choices=["calendar_climatology"] + candidates(), required=True)
    run.add_argument("--horizon", type=int, choices=HORIZONS, required=True)
    run.add_argument("--output", type=Path, required=True)
    run.set_defaults(handler=run_command)
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
