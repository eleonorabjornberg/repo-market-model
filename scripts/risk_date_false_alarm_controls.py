"""False-alarm controls on the every-day component of the risk-date passers (#532, a track of #374).

A scratch measurement, not a record: it writes JSON and Markdown to the paths it is given and nothing into
`docs/runs/`. The controls are in `metadata/risk_date_false_alarm_controls.json`, which this script refuses to
read unless it is committed and unchanged. The base is the `+every_day` variant of #506/#525, fitted exactly as
there (`ml.pressure_risk_date_variant_exceedance(..., every_day=True)`); a control only changes the forecast it
makes on a day that is not a risk date, from forecasts already issued and from the as-of scarcity state. No rule,
threshold, onset definition, cut-off rule or availability time changes: the judge chooses each variant's cut-offs
from its own training window, as for every candidate. No day after 2025-12-31 is read.

    PYTHONPATH=src python3 scripts/risk_date_false_alarm_controls.py declare      # once, before any score
    PYTHONPATH=src python3 scripts/risk_date_false_alarm_controls.py run --panel AUG2.csv --published PUBLISHED.csv \\
        --horizon H --output OUT/fa_hH.json [--candidate PARENT]
    PYTHONPATH=src python3 scripts/pressure_judge.py judge --panel PUBLISHED.csv --rule weighted \\
        --output OUT/judge_weighted.json --markdown OUT/judge_weighted.md OUT/bench_h?.json OUT/risk_h?.json OUT/fa_h?.json
    PYTHONPATH=src python3 scripts/risk_date_false_alarm_controls.py compare --panel PUBLISHED.csv \\
        --output OUT/compare.json --markdown OUT/compare.md OUT/bench_h?.json OUT/risk_h?.json OUT/fa_h?.json
    PYTHONPATH=src python3 scripts/risk_date_false_alarm_controls.py readings --panel PUBLISHED.csv \\
        --output OUT/readings.json --markdown OUT/readings.md OUT/bench_h?.json OUT/risk_h?.json OUT/fa_h?.json

`run` writes, for each parent, the `+every_day` forecasts (the #525 variant) and one forecast per control
(`<parent>+every_day+<control>`). `compare` puts each control beside its parent and the #525 variant, with
intervals, split by regime and pressure-day type; `readings` reports tier 1 under readings (a), (b) and (e) of
`docs/pivot/judge-readings-result.md`, under both rules.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import math
import sys
from collections import defaultdict
from dataclasses import replace
from datetime import date, time
from pathlib import Path
from typing import Dict, List, Optional, Sequence

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))

from repo_model import measurement_fields, ml  # noqa: E402
from repo_model.baseline import panel_sha256, rolling_exceedance_backtest  # noqa: E402
from repo_model.data import audit_panel, load_daily_panel  # noqa: E402
from repo_model.evaluation_splits import load_split_declaration  # noqa: E402
from repo_model.lockbox import require_unlocked  # noqa: E402

DECLARATION = REPO / "metadata" / "risk_date_false_alarm_controls.json"
PARENTS = REPO / "metadata" / "risk_date_severity.json"
CANDIDATES = REPO / "metadata" / "pressure_judge" / "candidates"
EPISODES = REPO / "docs" / "pivot" / "evidence" / "episode-post-mortem" / "episodes.json"
BASE = "+every_day"
#: the controls, in the order they are reported; the parameters are declared in the metadata file
CONTROLS = {
    "shrunk": {"weight": 0.5},
    "scarce": {"minimum_state": 1},
    "persist": {"days": 2},
    "gate": {"quantile": 0.9, "window": 250, "minimum_earlier": 60},
}
PARENT_NAMES = ("risk_gbm", "risk_gbm_base", "risk_logistic", "risk_logistic_base", "risk_quantile_skewt_base")


def _load(name: str):
    spec = importlib.util.spec_from_file_location(f"{name}_script", REPO / "scripts" / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


rds = _load("risk_date_severity")


# -- the controls ---------------------------------------------------------------------------------------------


def _shrunk(raw, off, state, weight, **_text):
    return [[p * weight if o else p for p, o in zip(row, off)] for row in raw]


def _scarce(raw, off, state, minimum_state, **_text):
    keep = [not o or (s is not None and s >= minimum_state) for o, s in zip(off, state)]
    return [[p if k else 0.0 for p, k in zip(row, keep)] for row in raw]


def _persist(raw, off, state, days, **_text):
    if days != 2:
        raise ValueError(f"persistence is declared for 2 days, got {days}")
    return [
        [min(row[k], row[k - 1]) if o and k > 0 else (0.0 if o else row[k]) for k, o in enumerate(off)]
        for row in raw
    ]


def _gate(raw, off, state, quantile, window, minimum_earlier, **_text):
    out = []
    for row in raw:
        gated = []
        for k, o in enumerate(off):
            if not o:
                gated.append(row[k])
                continue
            earlier = sorted(row[i] for i in range(max(0, k - window), k) if off[i])
            if len(earlier) < minimum_earlier:
                gated.append(0.0)
                continue
            cut = earlier[max(0, math.ceil(quantile * len(earlier)) - 1)]
            gated.append(row[k] if row[k] > cut else 0.0)
        out.append(gated)
    return out


_CONTROL_FUNCTIONS = {"shrunk": _shrunk, "scarce": _scarce, "persist": _persist, "gate": _gate}


def apply_control(name: str, params: dict, raw: Sequence[Sequence[float]], off: Sequence[bool], state: Sequence) -> List[List[float]]:
    """The `+every_day` forecasts `raw[tau][day]` changed on the days `off` marks (not a risk date), by control `name`.

    A risk-date forecast is the parent's and is never changed. Every control reads the day's own forecast, earlier
    days' forecasts and the as-of scarcity state `state[day]` (None if not public), and nothing later. The curve
    across thresholds is made non-increasing afterwards, as the parent's is.
    """

    if name not in _CONTROL_FUNCTIONS:
        raise ValueError(f"unknown control {name!r}; the declared ones are {sorted(_CONTROL_FUNCTIONS)}")
    out = _CONTROL_FUNCTIONS[name](raw, off, state, **params)
    for j in range(1, len(out)):
        out[j] = [min(a, b) for a, b in zip(out[j], out[j - 1])]
    return out


# -- the declaration -------------------------------------------------------------------------------------------


def declaration_document(parents: dict) -> dict:
    return {
        "status": (
            "declared by the pull request that closes #532 before any score was computed; nothing here is tuned on a "
            "scored day; the controls and their parameters are the pull request's, stated and not chosen on a score"
        ),
        "scoring": parents["scoring"],
        "thresholds_bp": parents["thresholds_bp"],
        "horizons": parents["horizons"],
        "parents": {name: parents["candidates"][name] for name in PARENT_NAMES},
        "parents_declaration": "metadata/risk_date_severity.json (unchanged: the risk dates, the features, the estimators)",
        "base": {
            "variant": BASE,
            "reading": "the every-day component of #506 (metadata/risk_date_every_day.json), fitted as there: ml.pressure_risk_date_variant_exceedance with every_day=True and early_prior=False; on a risk date the forecast is the parent's, on any other day the component's",
            "inputs": list(ml.EVERY_DAY_COMPONENT_INPUTS),
        },
        "controls": {
            "shrunk": {
                "weight": CONTROLS["shrunk"]["weight"],
                "rule": "on a day that is not a risk date the component's probability is multiplied by weight, a shrinkage toward the parent's 0; a risk date keeps the parent's forecast. With one cut-off per threshold for all days this is a higher cut-off for the days the component serves, relative to risk dates",
                "reads": "the component's own forecast of the day",
            },
            "scarce": {
                "minimum_state": CONTROLS["scarce"]["minimum_state"],
                "rule": "on a day that is not a risk date the component's probability is kept only if the as-of reserve scarcity state (reserve_scarcity_state, 0 abundant, 1 ample, 2 tight, 3 scarce) is at least minimum_state; below it, or when it is not public, the forecast is 0",
                "reads": "the reserve scarcity state, read as of the forecast's decision instant at its horizon, as the judge's grid reads it",
            },
            "persist": {
                "days": CONTROLS["persist"]["days"],
                "rule": "on a day that is not a risk date the forecast is the smaller of the component's probability today and the variant's forecast on the previous scored day (the parent's, if that was a risk date); the first scored day has no earlier day and is 0",
                "reads": "the day's own forecast and the previous scored day's, each issued at its own decision instant",
            },
            "gate": {
                "quantile": CONTROLS["gate"]["quantile"],
                "window": CONTROLS["gate"]["window"],
                "minimum_earlier": CONTROLS["gate"]["minimum_earlier"],
                "rule": "on a day that is not a risk date the component's probability is kept only if it is strictly above the quantile (nearest rank) of the component's forecasts on the days that were not risk dates among the previous window scored days; with fewer than minimum_earlier such forecasts it is 0. A walk-forward cut-off for the days the component serves, from forecasts already issued",
                "reads": "forecasts issued on earlier scored days, and nothing else",
            },
        },
        "combination": "every control leaves a risk-date forecast as the parent's; the curve across thresholds is made non-increasing afterwards, as the parent's is",
        "cutoffs": "the judge's cutoff_rule, from each variant's own training window, unchanged: one cut-off per threshold and horizon",
        "judging": "the judge as declared (metadata/pressure_judge.json): tiers 1, 3 and 5, h = 1 to 5, +5 and +10 bp, under the flat and the weighted rule; tier 1 also under readings (b) and (e) of docs/pivot/judge-readings-result.md",
        "published": "nothing: the controls are off in every published declaration; no rule, threshold, definition or availability time changes",
    }


def declare_command(args) -> int:
    parents = json.loads(PARENTS.read_text(encoding="utf-8"))
    document = declaration_document(parents)
    DECLARATION.write_text(json.dumps(document, indent=2) + "\n", encoding="utf-8")
    for parent in document["parents"]:
        base = json.loads((CANDIDATES / f"{parent}{BASE}.json").read_text(encoding="utf-8"))
        for control, spec in document["controls"].items():
            entry = dict(base)
            entry["track"] = "F (#532)"
            entry["calibration"] = (
                base["calibration"].split("; metadata/")[0]
                + f"; then the '{control}' false-alarm control on the days that are not risk dates: "
                + spec["rule"].split(";")[0]
                + "; metadata/risk_date_false_alarm_controls.json"
            )
            (CANDIDATES / f"{parent}{BASE}+{control}.json").write_text(json.dumps(entry, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"declaration": str(DECLARATION), "candidates": len(document["parents"]) * len(document["controls"])}))
    return 0


# -- run ----------------------------------------------------------------------------------------------------


def run_command(args) -> int:
    declared = rds.committed_declaration(DECLARATION)
    parents = json.loads(PARENTS.read_text(encoding="utf-8"))
    h = args.horizon
    if h not in declared["horizons"]:
        raise SystemExit(f"horizon {h} is not declared")
    last = date.fromisoformat(declared["scoring"]["last_day"])
    require_unlocked([last], where="risk_date_false_alarm_controls")
    rows = load_daily_panel(args.panel)
    audit_panel(rows)
    by_date = {row.date: row for row in rows}
    splits = load_split_declaration(rds.SPLITS)
    registry = measurement_fields.load_registry()
    taus = tuple(float(t) for t in declared["thresholds_bp"])
    minimum = declared["scoring"]["minimum_history"]
    states = _load("pressure_judge")._scarcity_states(h, last)
    names = [args.candidate] if args.candidate else list(declared["parents"])
    forecasts, settings = {}, {}
    for parent in names:
        spec = declared["parents"][parent]
        parent_features = rds.features_at_horizon(parents, spec, h)
        features = tuple(dict.fromkeys(parent_features + ml.EVERY_DAY_COMPONENT_INPUTS))
        predictor = ml.pressure_risk_date_variant_exceedance(
            spec["kind"], parent_features, splits, minimum, every_day=True, early_prior=False
        )
        with rds.switched_on():
            report = rolling_exceedance_backtest(
                rows,
                predictor=predictor,
                model_name=parent + BASE,
                features=features,
                registry=registry,
                decision_time=time.fromisoformat(declared["scoring"]["decision_time"]),
                taus=taus,
                minimum_history=minimum,
                refit_every=declared["scoring"]["refit_every"],
                end=last,
                horizon=h,
            )
        column = rds.column(report)
        keys = [f"{tau:g}" for tau in taus]
        days = sorted(column[keys[0]])
        raw = [[column[key][day] for day in days] for key in keys]
        off = [not rds.is_risk_date(splits, by_date[date.fromisoformat(day)].values, h) for day in days]
        state = [states.get(date.fromisoformat(day)) for day in days]
        forecasts[parent + BASE] = column
        settings[parent + BASE] = _settings(report)
        for control, params in CONTROLS.items():
            out = apply_control(control, params, raw, off, state)
            name = f"{parent}{BASE}+{control}"
            forecasts[name] = {key: dict(zip(days, out[j])) for j, key in enumerate(keys)}
            settings[name] = settings[parent + BASE]
        print(json.dumps({"horizon": h, "parent": parent, "done": True}), flush=True)
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


def _settings(report):
    return {
        "features": list(report.features),
        "model_settings": dict(report.model_settings),
        "ml_libraries": None if report.ml_libraries is None else dict(report.ml_libraries),
    }


# -- compare ------------------------------------------------------------------------------------------------


def _f(value, places=3):
    return "-" if value is None else f"{value:.{places}f}"


def _interval(cell):
    if cell is None or cell.get("mean") is None:
        return "-"
    if "interval" not in cell:
        return f"{cell['mean']:+.4f} (no interval)"
    return f"{cell['mean']:+.4f} [{cell['interval']['lower']:+.4f}, {cell['interval']['upper']:+.4f}]"


def _grids(pj, declaration, rows, splits, states, items):
    out = {}
    for h in declaration.horizons:
        reference = next(f for f in items if f.horizon == h and f.name == declaration.climatology)
        out[h] = pj.build_grid(declaration, h, rows, reference.dates, splits, scarcity_state=states[h])
    return out


def _load_forecasts(pj, digest, inputs):
    forecasts = []
    for path in inputs:
        document = json.loads(Path(path).read_text())
        if document["panel_sha256"] != digest:
            raise SystemExit(f"{path} was scored on another panel ({document['panel_sha256'][:8]})")
        forecasts.extend(pj.forecasts_from_horizon_document(document))
    return forecasts


def compare_command(args) -> int:
    from repo_model import pressure_judge as pj

    pj_script = _load("pressure_judge")
    declared = rds.committed_declaration(DECLARATION)
    declaration = pj.load_declaration()
    rows = load_daily_panel(args.panel)
    audit_panel(rows)
    splits = load_split_declaration(rds.SPLITS)
    by_date = {row.date: row for row in rows}
    forecasts = _load_forecasts(pj, panel_sha256(args.panel), args.inputs)
    states = {h: pj_script._scarcity_states(h, declaration.last_day) for h in declaration.horizons}
    calendar = [row.date for row in rows]
    chosen = pj.choose_cutoffs(declaration, _grids(pj, declaration, rows, splits, states, forecasts), forecasts, calendar)
    grids = _grids(pj, declaration, rows, splits, states, chosen)
    tau = declaration.primary
    by_name = {}
    for forecast in chosen:
        by_name.setdefault(forecast.name, {})[forecast.horizon] = forecast
    parents = list(declared["parents"])
    controls = list(declared["controls"])
    variants = [f"{p}{BASE}+{c}" for p in parents for c in controls]
    bases = [p + BASE for p in parents]
    parent_of = {**{f"{p}{BASE}+{c}": p for p in parents for c in controls}, **{p + BASE: p for p in parents}}
    base_of = {f"{p}{BASE}+{c}": p + BASE for p in parents for c in controls}
    for name in variants + bases + parents + [declaration.climatology, declaration.persistence]:
        if name not in by_name:
            raise SystemExit(f"no forecasts for {name!r} in the inputs")
    horizons = list(declaration.horizons)
    seed = declaration.document()["bootstrap"]["seed"]

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

    everyone = variants + bases + parents
    caught_by = {name: caught(name) for name in everyone}
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
    recall = {}
    for name in variants + bases:
        recall[name] = {}
        for label, reference in (("vs_parent", parent_of[name]), ("vs_every_day", base_of.get(name))):
            if reference is None or reference == name:
                continue
            cells = {
                cell: [
                    [m * o for m, o in zip(inside, onset)],
                    [m * c for m, c in zip(inside, caught_by[name])],
                    [m * c for m, c in zip(inside, caught_by[reference])],
                ]
                for cell, inside in cells_for.items()
            }
            recall[name][label] = pj._bootstrap(
                declaration, cells, recall_stats, count, seed=pj._seed(seed, "recall", name, label)
            )
    caught_count = {
        name: {cell: int(sum(m * c for m, c in zip(inside, caught_by[name]))) for cell, inside in cells_for.items()}
        for name in everyone
    }
    onsets_in = {cell: int(sum(m * o for m, o in zip(inside, onset))) for cell, inside in cells_for.items()}

    flags = {}
    for name in everyone:
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
                    "flags_on_a_pressure_day": sum(1 for k in flagged if outcomes[k]),
                    "false_alarms": sum(1 for k in flagged if not outcomes[k]),
                    "onsets_flagged": sum(1 for k in flagged if onsets[k]),
                }
                cell[label]["false_alarms_per_onset"] = cell[label]["false_alarms"] / n_onsets if n_onsets else None
            flags[name][str(h)] = cell

    brier = {}
    for name in variants + bases:
        brier[name] = {}
        for h in horizons:
            grid = grids[h]
            outcomes = grid.outcomes[tau]
            n = len(outcomes)
            groups = {"all": list(range(n))}
            for dimension in ("regime", "day_type"):
                for label in sorted(set(grid.groups[dimension])):
                    groups[f"{dimension} {label}"] = [k for k, x in enumerate(grid.groups[dimension]) if x == label]
            p = by_name[name][h].probabilities[tau]
            clim = by_name[declaration.climatology][h].probabilities[tau]
            pers = by_name[declaration.persistence][h].probabilities[tau]
            results = {}
            references = {"standard": None, "vs_parent": parent_of[name], "vs_every_day": base_of.get(name)}
            for label, reference in references.items():
                if label == "vs_every_day" and reference is None:
                    continue
                ref_p = clim if reference is None else by_name[reference][h].probabilities[tau]
                cells = {g: pj._paired_vectors(p, ref_p, pers, outcomes, members) for g, members in groups.items()}
                results[label] = pj._bootstrap(
                    declaration, cells, pj._PAIRED_STATS, n, seed=pj._seed(seed, "brier", name, h, label)
                )
            brier[name][str(h)] = {
                g: {
                    "days": results["standard"][g]["days"],
                    "vs_climatology": results["standard"][g]["brier_difference_vs_climatology"],
                    "vs_persistence_logistic": results["standard"][g]["brier_difference_vs_persistence"],
                    "vs_parent": results["vs_parent"][g]["brier_difference_vs_climatology"],
                    **(
                        {"vs_every_day": results["vs_every_day"][g]["brier_difference_vs_climatology"]}
                        if "vs_every_day" in results else {}
                    ),
                }
                for g in groups
            }

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
                **{name: bool(caught_by[name][i]) for name in everyone},
            }
        )
    document = {
        "declaration": declared,
        "onsets": int(sum(onset)),
        "onsets_in_cell": onsets_in,
        "caught_at_some_lead": caught_count,
        "recall_at_some_lead": recall,
        "flags": flags,
        "brier": brier,
        "episodes": episodes,
    }
    args.output.write_text(json.dumps(document, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    text = markdown(document, parents, controls)
    if args.markdown:
        args.markdown.write_text(text + "\n", encoding="utf-8")
    print(text)
    return 0


def markdown(document: dict, parents, controls) -> str:
    out = []
    names = lambda p: [p, p + BASE] + [f"{p}{BASE}+{c}" for c in controls]
    out.append("Table 1. +5 bp onsets flagged at some lead 1 to 5, by cell: parent, the #525 variant (`+every_day`) and each control.\n")
    for p in parents:
        group = names(p)
        out.append(f"\n{p}\n")
        out.append("| cell | onsets | " + " | ".join(n[len(p):] or "parent" for n in group) + " |")
        out.append("|---|---|" + "---|" * len(group))
        for cell, n_onsets in document["onsets_in_cell"].items():
            out.append(f"| {cell} | {n_onsets} | " + " | ".join(f"{document['caught_at_some_lead'][n][cell]}" for n in group) + " |")
    for label, title in (("vs_parent", "the parent"), ("vs_every_day", "the #525 variant (`+every_day`)")):
        out.append(f"\nTable 2{'a' if label == 'vs_parent' else 'b'}. Recall difference against {title}, by cell (90% interval).\n")
        for p in parents:
            group = [f"{p}{BASE}+{c}" for c in controls]
            if label == "vs_parent":
                group = [p + BASE] + group
            out.append(f"\n{p}\n")
            out.append("| cell | " + " | ".join(n[len(p):] for n in group) + " |")
            out.append("|---|" + "---|" * len(group))
            for cell in document["onsets_in_cell"]:
                out.append(f"| {cell} | " + " | ".join(_interval(document["recall_at_some_lead"][n][label][cell]["recall_difference"]) for n in group) + " |")
    out.append("\nTable 3. Flags at +5 bp, by horizon: all days / risk dates / other days (flags, of which false alarms); onsets flagged; false alarms per onset on all days.\n")
    out.append("| model | " + " | ".join(f"h = {h}" for h in (1, 2, 3, 4, 5)) + " |")
    out.append("|---|" + "---|" * 5)
    for p in parents:
        for name in names(p):
            cells = []
            for h in ("1", "2", "3", "4", "5"):
                c = document["flags"][name][h]
                a, r, o = c["all_days"], c["risk_dates"], c["other_days"]
                cells.append(
                    f"{a['flags']}({a['false_alarms']}) / {r['flags']}({r['false_alarms']}) / {o['flags']}({o['false_alarms']}); "
                    f"{a['onsets_flagged']}/{c['onsets']}; {_f(a['false_alarms_per_onset'], 2)}"
                )
            out.append(f"| {name} | " + " | ".join(cells) + " |")
    for h in ("1", "5"):
        out.append(f"\nTable 4 (h = {h}). Brier score the comparison loses to the variant (positive favours the variant), +5 bp, 90% interval.\n")
        out.append("| model | cell | days | vs parent | vs #525 variant | vs climatology | vs persistence-logistic |")
        out.append("|---|---|---|---|---|---|---|")
        for p in parents:
            for name in names(p)[1:]:
                for cell, c in document["brier"][name][h].items():
                    out.append(
                        f"| {name} | {cell} | {int(c['days'])} | {_interval(c['vs_parent'])} | {_interval(c.get('vs_every_day'))} | "
                        f"{_interval(c['vs_climatology'])} | {_interval(c['vs_persistence_logistic'])} |"
                    )
    every = [x for p in parents for x in names(p)]
    out.append("\nTable 5. The 26 episodes of the post-mortem (#474): who warns at some lead 1 to 5 (all-five misses marked).\n")
    out.append("| start | type | regime | missed by all five | " + " | ".join(every) + " |")
    out.append("|---|---|---|---|" + "---|" * len(every))
    for e in document["episodes"]:
        out.append(
            f"| {e['start']} | {e['day_type']} | {e['regime']} | {'yes' if e['missed_by_all_five'] else 'no'} | "
            + " | ".join("yes" if e[n] else "no" for n in every) + " |"
        )
    return "\n".join(out)


# -- readings (a), (b), (e) of docs/pivot/judge-readings-result.md ----------------------------------------------


def readings_command(args) -> int:
    from repo_model import pressure_judge as pj

    jr = _load("judge_readings")
    pj_script = _load("pressure_judge")
    declared = rds.committed_declaration(DECLARATION)
    base = pj.load_declaration()
    pj_script.require_committed_declaration(pj.DEFAULT_DECLARATION)
    pj_script.require_committed_file(pj.DEFAULT_WEIGHTED_MISS)
    parents = list(declared["parents"])
    controls = list(declared["controls"])
    names = []
    for p in parents:
        names += [p, p + BASE] + [f"{p}{BASE}+{c}" for c in controls]
    names += [base.climatology, base.persistence]
    rows = load_daily_panel(args.panel)
    audit_panel(rows)
    splits = load_split_declaration(rds.SPLITS)
    forecasts = [f for f in _load_forecasts(pj, panel_sha256(args.panel), args.inputs) if f.name in names]
    unique = {}
    for f in forecasts:
        unique.setdefault((f.name, f.horizon), f)
    forecasts = list(unique.values())
    missing = [(n, h) for n in names for h in base.horizons if (n, h) not in unique]
    if missing:
        raise SystemExit(f"no forecast for {missing[:3]}")
    states = {h: pj_script._scarcity_states(h, base.last_day) for h in base.horizons}
    calendar = [row.date for row in rows]
    place = {day: k for k, day in enumerate(calendar)}
    result: Dict[str, object] = {"readings": {}}
    for rule in jr.RULES:
        declaration = replace(base, weighted_miss=pj.load_weighted_miss(applied=(rule == "weighted")))
        chosen = pj.choose_cutoffs(declaration, _grids(pj, declaration, rows, splits, states, forecasts), forecasts, calendar)
        grids = _grids(pj, declaration, rows, splits, states, chosen)
        by_name: Dict[str, dict] = defaultdict(dict)
        for f in chosen:
            by_name[f.name][f.horizon] = f
        result["readings"][rule] = {}
        for name in names:
            series = jr.RowSeries(declaration, grids, by_name, name, place, pj.false_alarm_weights)
            result["readings"][rule][name] = jr.readings_for(declaration, series, limited_weighted=(rule == "weighted"))
    result["provenance"] = {"panel_sha256": panel_sha256(args.panel)}
    args.output.write_text(json.dumps(result, indent=1, sort_keys=True, default=str) + "\n", encoding="utf-8")
    if args.markdown:
        args.markdown.write_text(readings_markdown(result, names, jr), encoding="utf-8")
    print(json.dumps({"output": str(args.output)}))
    return 0


def readings_markdown(result: dict, names, jr) -> str:
    lines = ["# Tier 1 of the false-alarm controls under readings (a), (b) and (e) (#532)", ""]
    titles = {"unweighted": "Flat rule", "weighted": "Weighted rule"}
    for rule, rows in result["readings"].items():
        lines += [f"## {titles[rule]}", ""]
        for title, pick in (
            ("(a) as declared", lambda r: r["a"]),
            ("(b2) warnings and false alarms pooled across horizons", lambda r: r["b2"]),
            ("(e) outside 2018-19", lambda r: r["e"]["outside_2018_19"]),
            ("(e) in 2018-19", lambda r: r["e"]["in_2018_19"]),
        ):
            lines += [f"### {title}", "", jr.HEAD]
            lines += [jr._row(n, pick(rows[n])) for n in names]
            lines.append("")
        lines += [
            "### (b1) one horizon alone: onsets warned / false alarms per onset at each horizon",
            "", "| row | h = 1 | h = 2 | h = 3 | h = 4 | h = 5 | passes at some horizon |", "|---|---|---|---|---|---|---|",
        ]
        for n in names:
            b = rows[n]["b1_best"]
            cells = [
                f"{c['onsets_flagged']:g} / {jr._f(c['false_alarms_per_onset_limited'])}" if "onsets_flagged" in c else "–"
                for c in (rows[n]["b1"][str(h)] for h in (1, 2, 3, 4, 5))
            ]
            lines.append(f"| {n} | " + " | ".join(cells) + f" | {jr._v(b['passes'])}" + (f" (h = {b['horizon']})" if b["passes"] else "") + " |")
        lines.append("")
    return "\n".join(lines) + "\n"


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("declare", help="write the declaration and the judge's candidate files").set_defaults(handler=declare_command)
    run = commands.add_parser("run")
    run.add_argument("--panel", type=Path, required=True)
    run.add_argument("--published", type=Path, required=True)
    run.add_argument("--horizon", type=int, required=True)
    run.add_argument("--candidate", help="one parent")
    run.add_argument("--output", type=Path, required=True)
    run.set_defaults(handler=run_command)
    for name, handler in (("compare", compare_command), ("readings", readings_command)):
        sub = commands.add_parser(name)
        sub.add_argument("--panel", type=Path, required=True)
        sub.add_argument("--output", type=Path, required=True)
        sub.add_argument("--markdown", type=Path)
        sub.add_argument("inputs", nargs="+", type=Path)
        sub.set_defaults(handler=handler)
    args = parser.parse_args(argv)
    return args.handler(args)


if __name__ == "__main__":
    raise SystemExit(main())
