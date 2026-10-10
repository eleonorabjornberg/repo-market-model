"""Score the risk-date passers with an every-day component and without constant early fits (#506, a track of #374).

A scratch measurement, not a record: it writes JSON to the paths it is given and nothing into
`docs/runs/`. The variants, the component's inputs and the rule that combines it with the parent are in
`metadata/risk_date_every_day.json`, which this script refuses to read unless it is committed and unchanged,
as the judge's declaration is. Every input beyond the published panel is off in every published declaration
and switched on for these runs only. No rule, threshold, onset definition or availability time changes: the
judge's cut-off rule chooses each variant's cut-offs from its own training window, as for every candidate.

    # the scratch panel is the one of risk_date_severity.py (AUG2.csv)
    PYTHONPATH=src python3 scripts/risk_date_every_day.py declare
    PYTHONPATH=src python3 scripts/risk_date_every_day.py run --panel AUG2.csv --published PUBLISHED.csv \\
        --horizon H --output OUT/ed_hH.json [--candidate PARENT]
    PYTHONPATH=src python3 scripts/pressure_judge.py judge --panel PUBLISHED.csv --rule weighted \\
        --output OUT/judge_weighted.json --markdown OUT/judge_weighted.md OUT/bench_h?.json OUT/risk_h?.json OUT/ed_h?.json
    PYTHONPATH=src python3 scripts/pressure_judge.py judge --panel PUBLISHED.csv --rule unweighted ...
    PYTHONPATH=src python3 scripts/risk_date_every_day.py compare --panel PUBLISHED.csv --output OUT/compare.json \\
        --markdown OUT/compare.md OUT/bench_h?.json OUT/risk_h?.json OUT/ed_h?.json

`declare` writes the declaration and the judge's candidate files (`metadata/pressure_judge/candidates/`) from the
five parents of `metadata/risk_date_severity.json`; it is run once, before any score, and its output committed.
`run` fits every variant of every parent (`ml.pressure_risk_date_variant_exceedance`), walk-forward at +5 and
+10 bp on the shared fold grid, days before 2026-01-01 only. `compare` reads the judge's own cut-offs and puts each
variant beside its parent, calendar climatology and persistence-logistic: onset recall at some lead 1 to 5 (by
year, regime and pressure-day type), the Brier score on the +5 bp outcome, paired, the flags the variant raises
off the risk dates, and the 26 episodes of the post-mortem (#474).
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from datetime import date, time
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))

from repo_model import measurement_fields, ml  # noqa: E402
from repo_model.baseline import panel_sha256, rolling_exceedance_backtest  # noqa: E402
from repo_model.data import audit_panel, load_daily_panel  # noqa: E402
from repo_model.evaluation_splits import load_split_declaration  # noqa: E402
from repo_model.lockbox import require_unlocked  # noqa: E402

SPLITS = REPO / "metadata" / "evaluation_splits.json"
DECLARATION = REPO / "metadata" / "risk_date_every_day.json"
PARENTS = REPO / "metadata" / "risk_date_severity.json"
CANDIDATES = REPO / "metadata" / "pressure_judge" / "candidates"
EPISODES = REPO / "docs" / "pivot" / "evidence" / "episode-post-mortem" / "episodes.json"
#: variant name suffix -> (every-day component, early-fit prior)
VARIANTS = {"+every_day": (True, False), "+early_prior": (False, True), "+every_day+early_prior": (True, True)}


def _load(name: str):
    spec = importlib.util.spec_from_file_location(f"{name}_script", REPO / "scripts" / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


rds = _load("risk_date_severity")


def declaration_document(parents: dict) -> dict:
    return {
        "status": (
            "declared by the pull request that closes #506 before any score was computed; nothing here is tuned on a "
            "scored day; the choices below (the component's inputs and estimator, the combination rule, the early-fit "
            "minimum and prior) are the pull request's, listed there for Eleonora's review"
        ),
        "scoring": parents["scoring"],
        "thresholds_bp": parents["thresholds_bp"],
        "horizons": parents["horizons"],
        "parents": {
            name: parents["candidates"][name]
            for name in ("risk_gbm", "risk_gbm_base", "risk_logistic", "risk_logistic_base", "risk_quantile_skewt_base")
        },
        "parents_declaration": "metadata/risk_date_severity.json (unchanged: the risk dates, the features, the estimators)",
        "variants": {
            "+every_day": "(a) the parent plus the every-day component",
            "+early_prior": "(b) the parent with the day-type prior on a refit whose risk-date window is too small",
            "+every_day+early_prior": "(c) (a) and (b) together",
        },
        "every_day_component": {
            "inputs": list(ml.EVERY_DAY_COMPONENT_INPUTS),
            "inputs_note": (
                "the previous day's SOFR 75th and 99th percentiles above IORB in basis points (derived by "
                "repo_model.measurement_fields, off in every published declaration) and the latest public spread, "
                "the spread's own state; each read at its declared availability through the information rule and "
                "both of its guards (docs/decisions/information-set.md)"
            ),
            "estimator": "a ridge logistic of spread > tau (ml.PRESSURE_LOGISTIC_SETTINGS: L2, C = 1, standardised), one per threshold",
            "training": "the direct pairs of every training day, risk date or not (ml._pressure_pairs), each label paired with what was public at its own decision instant",
            "combination": (
                "one rule: on a risk date the forecast is the parent's, unchanged; on any other day it is the component's. "
                "The component serves exactly the days the parent leaves at 0. A served day whose component inputs are not "
                "all public is left at 0. The curve across thresholds is made non-increasing, as the parent's is"
            ),
            "cutoffs": "the judge's cutoff_rule, from each variant's own training window; one cut-off per threshold and horizon for risk dates and other days alike",
        },
        "early_fit": {
            "minimum_pairs": ml.EARLY_FIT_MINIMUM_PAIRS,
            "why_this_minimum": "2 * min_samples_leaf of the gradient-boosted classifier (ml.PRESSURE_CLASSIFIER_SETTINGS): below it the classifier cannot split and is a constant (docs/pivot/construction-gaps-result.md, gap 4)",
            "rule": (
                "on a refit whose risk-date training window holds fewer pairs than the minimum, the risk-date forecast is the "
                "day-type prior instead of the parent's estimator, for every estimator: the window's rate of spread > tau among "
                "the pairs of the scored day's type (quarter-end, month-end, tax date, or none of them, the coupon-settlement "
                "risk dates), shrunk toward the window's pooled rate by prior_weight pairs at that rate. At or above the minimum "
                "the parent's estimator is used, unchanged"
            ),
            "prior_weight": ml.EARLY_FIT_PRIOR_WEIGHT,
            "reads": "the refit's own training pairs and nothing else",
        },
        "judging": "the judge as declared (metadata/pressure_judge.json): tiers 1, 3 and 5, h = 1 to 5, +5 and +10 bp, under the flat and the weighted rule; the cut-off rule unchanged",
        "published": "nothing: the variants and the new inputs are off in every published declaration",
    }


def declare_command(args) -> int:
    parents = json.loads(PARENTS.read_text(encoding="utf-8"))
    document = declaration_document(parents)
    DECLARATION.write_text(json.dumps(document, indent=2) + "\n", encoding="utf-8")
    for parent in document["parents"]:
        base = json.loads((CANDIDATES / f"{parent}.json").read_text(encoding="utf-8"))
        for suffix, (every_day, early) in VARIANTS.items():
            features = list(base["features"])
            if every_day:
                features += [name for name in ml.EVERY_DAY_COMPONENT_INPUTS if name not in features]
            parts = []
            if every_day:
                parts.append("a ridge logistic on spread_bps, sofr_p75_iorb_bps and sofr_p99_iorb_bps serves every day that is not a risk date")
            if early:
                parts.append(
                    f"on a refit with fewer than {ml.EARLY_FIT_MINIMUM_PAIRS} risk-date pairs the day-type prior replaces the estimator"
                )
            entry = {
                "role": "candidate",
                "track": "E (#506)",
                "parent": parent,
                "features": features,
                "features_at_horizon_2_or_more": base["features_at_horizon_2_or_more"],
                "calibration": "none: the parent's risk-date forecast (" + base["calibration"].split(";")[0] + "), changed by one thing: "
                + "; ".join(parts)
                + "; metadata/risk_date_every_day.json",
            }
            (CANDIDATES / f"{parent}{suffix}.json").write_text(json.dumps(entry, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"declaration": str(DECLARATION), "candidates": len(document["parents"]) * len(VARIANTS)}))
    return 0


def run_command(args) -> int:
    declared = rds.committed_declaration(DECLARATION)
    parents = json.loads(PARENTS.read_text(encoding="utf-8"))
    h = args.horizon
    if h not in declared["horizons"]:
        raise SystemExit(f"horizon {h} is not declared")
    last = date.fromisoformat(declared["scoring"]["last_day"])
    require_unlocked([last], where="risk_date_every_day")
    rows = load_daily_panel(args.panel)
    audit_panel(rows)
    splits = load_split_declaration(rds.SPLITS)
    registry = measurement_fields.load_registry()
    taus = tuple(float(t) for t in declared["thresholds_bp"])
    minimum = declared["scoring"]["minimum_history"]
    names = [args.candidate] if args.candidate else list(declared["parents"])
    forecasts, settings, early_fits = {}, {}, {}
    for parent in names:
        spec = declared["parents"][parent]
        parent_features = rds.features_at_horizon(parents, spec, h)
        for suffix, (every_day, early) in VARIANTS.items():
            name = parent + suffix
            features = tuple(dict.fromkeys(parent_features + (ml.EVERY_DAY_COMPONENT_INPUTS if every_day else ())))
            predictor = ml.pressure_risk_date_variant_exceedance(
                spec["kind"], parent_features, splits, minimum, every_day=every_day, early_prior=early
            )
            with rds.switched_on():
                report = rolling_exceedance_backtest(
                    rows,
                    predictor=predictor,
                    model_name=name,
                    features=features,
                    registry=registry,
                    decision_time=time.fromisoformat(declared["scoring"]["decision_time"]),
                    taus=taus,
                    minimum_history=minimum,
                    refit_every=declared["scoring"]["refit_every"],
                    end=last,
                    horizon=h,
                )
            forecasts[name] = rds.column(report)
            settings[name] = {
                "features": list(report.features),
                "model_settings": dict(report.model_settings),
                "ml_libraries": None if report.ml_libraries is None else dict(report.ml_libraries),
            }
            print(json.dumps({"horizon": h, "candidate": name, "done": True}), flush=True)
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


def _f(value, places=3):
    return "-" if value is None else f"{value:.{places}f}"


def _interval(cell):
    if cell is None or cell.get("mean") is None:
        return "-"
    if "interval" not in cell:
        return f"{cell['mean']:+.4f} (no interval)"
    low, high = cell["interval"]["lower"], cell["interval"]["upper"]
    return f"{cell['mean']:+.4f} [{low:+.4f}, {high:+.4f}]"


def compare_command(args) -> int:
    """Each variant beside its parent, climatology and persistence-logistic, under the judge's own cut-offs."""

    from repo_model import pressure_judge as pj

    pj_script = _load("pressure_judge")
    declared = rds.committed_declaration(DECLARATION)
    declaration = pj.load_declaration()
    rows = load_daily_panel(args.panel)
    audit_panel(rows)
    splits = load_split_declaration(rds.SPLITS)
    by_date = {row.date: row for row in rows}
    digest = panel_sha256(args.panel)
    forecasts = []
    for path in args.inputs:
        document = json.loads(Path(path).read_text())
        if document["panel_sha256"] != digest:
            raise SystemExit(f"{path} was scored on another panel ({document['panel_sha256'][:8]})")
        forecasts.extend(pj.forecasts_from_horizon_document(document))
    states = {h: pj_script._scarcity_states(h, declaration.last_day) for h in declaration.horizons}

    def grids_of(items):
        out = {}
        for h in declaration.horizons:
            reference = next(f for f in items if f.horizon == h and f.name == declaration.climatology)
            out[h] = pj.build_grid(declaration, h, rows, reference.dates, splits, scarcity_state=states[h])
        return out

    calendar = [row.date for row in rows]
    chosen = pj.choose_cutoffs(declaration, grids_of(forecasts), forecasts, calendar)
    grids = grids_of(chosen)
    tau = declaration.primary
    by_name = {}
    for forecast in chosen:
        by_name.setdefault(forecast.name, {})[forecast.horizon] = forecast
    parents = list(declared["parents"])
    variants = [parent + suffix for parent in parents for suffix in VARIANTS]
    parent_of = {parent + suffix: parent for parent in parents for suffix in VARIANTS}
    for name in variants + parents + [declaration.climatology, declaration.persistence]:
        if name not in by_name:
            raise SystemExit(f"no forecasts for {name!r} in the inputs")
    horizons = list(declaration.horizons)
    seed = declaration.document()["bootstrap"]["seed"]

    # -- onsets flagged at some lead 1 to 5 --------------------------------------------------------------
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

    caught_by = {name: caught(name) for name in variants + parents}
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
        "parent_recall": pj._ratio(2, 0),
        "recall_difference": lambda t: (t[1] - t[2]) / t[0] if t[0] else None,
    }
    recall = {}
    for name in variants:
        parent = parent_of[name]
        cells = {
            label: [
                [m * o for m, o in zip(inside, onset)],
                [m * c for m, c in zip(inside, caught_by[name])],
                [m * c for m, c in zip(inside, caught_by[parent])],
            ]
            for label, inside in cells_for.items()
        }
        recall[name] = pj._bootstrap(declaration, cells, recall_stats, count, seed=pj._seed(seed, "recall", name))
    parent_recall = {
        parent: {
            label: {
                "onsets": int(sum(m * o for m, o in zip(inside, onset))),
                "caught": int(sum(m * c for m, c in zip(inside, caught_by[parent]))),
            }
            for label, inside in cells_for.items()
        }
        for parent in parents
    }
    variant_caught = {
        name: {
            label: int(sum(m * c for m, c in zip(inside, caught_by[name]))) for label, inside in cells_for.items()
        }
        for name in variants
    }

    # -- flags and false alarms at +5 bp, on and off the risk dates --------------------------------------------
    flags = {}
    for name in variants + parents:
        flags[name] = {}
        for h in horizons:
            grid = grids[h]
            f = by_name[name][h]
            p = f.probabilities[tau]
            raised = [1 if q >= c else 0 for q, c in zip(p, f.cutoffs[tau])]
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
                    "onsets": sum(onsets[k] for k in inside),
                    "onsets_flagged": sum(1 for k in flagged if onsets[k]),
                }
                cell[label]["false_alarms_per_onset"] = (
                    cell[label]["false_alarms"] / n_onsets if n_onsets else None
                )
            flags[name][str(h)] = cell

    # -- Brier score on the +5 bp outcome, paired ----------------------------------------------------------------
    brier = {}
    for name in variants:
        brier[name] = {}
        parent = parent_of[name]
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
            ref = by_name[parent][h].probabilities[tau]
            cells_ref, cells_std = {}, {}
            for label, members in groups.items():
                cells_std[label] = pj._paired_vectors(p, clim, pers, outcomes, members)
                cells_ref[label] = pj._paired_vectors(p, ref, pers, outcomes, members)
            std = pj._bootstrap(declaration, cells_std, pj._PAIRED_STATS, n, seed=pj._seed(seed, "brier", name, h))
            vs_ref = pj._bootstrap(declaration, cells_ref, pj._PAIRED_STATS, n, seed=pj._seed(seed, "brier", name, h))
            brier[name][str(h)] = {
                label: {
                    "days": std[label]["days"],
                    "vs_climatology": std[label]["brier_difference_vs_climatology"],
                    "vs_persistence_logistic": std[label]["brier_difference_vs_persistence"],
                    "vs_parent": vs_ref[label]["brier_difference_vs_climatology"],
                }
                for label in groups
            }

    # -- the post-mortem's episodes -----------------------------------------------------------------------------
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
                "cause_best_of_five": episode.get("cause_best_of_five"),
                **{name: bool(caught_by[name][i]) for name in parents + variants},
            }
        )
    document = {
        "declaration": declared,
        "onsets": int(sum(onset)),
        "parent_recall_at_some_lead": parent_recall,
        "variant_caught_at_some_lead": variant_caught,
        "recall_at_some_lead": recall,
        "flags": flags,
        "brier": brier,
        "episodes": episodes,
    }
    args.output.write_text(json.dumps(document, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    text = markdown(document, parents, variants)
    if args.markdown:
        args.markdown.write_text(text + "\n", encoding="utf-8")
    print(text)
    return 0


def markdown(document: dict, parents, variants) -> str:
    out = []
    out.append("Table 1. +5 bp onsets flagged at some lead 1 to 5, by cell: parent, then each variant with its recall difference against the parent (90% interval).\n")
    for parent in parents:
        group = [parent] + [parent + s for s in VARIANTS]
        out.append(f"\n{parent}\n")
        out.append("| cell | onsets | " + parent + " | " + " | ".join(f"{v[len(parent):]} | difference" for v in group[1:]) + " |")
        out.append("|---|---|---|" + "---|---|" * (len(group) - 1))
        for label, ref in document["parent_recall_at_some_lead"][parent].items():
            row = [label, str(ref["onsets"]), f"{ref['caught']}/{ref['onsets']}"]
            for v in group[1:]:
                cell = document["recall_at_some_lead"][v][label]
                row.append(f"{document['variant_caught_at_some_lead'][v][label]}/{ref['onsets']}")
                row.append(_interval(cell["recall_difference"]))
            out.append("| " + " | ".join(row) + " |")
    out.append("\nTable 2. Flags at +5 bp, by horizon: all days / risk dates / other days (flags, of which false alarms), onsets flagged, false alarms per onset on all days.\n")
    out.append("| model | " + " | ".join(f"h = {h}" for h in (1, 2, 3, 4, 5)) + " |")
    out.append("|---|" + "---|" * 5)
    for name in [x for p in parents for x in [p] + [p + s for s in VARIANTS]]:
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
        out.append(f"\nTable 3 (h = {h}). Brier score the comparison loses to the variant (positive favours the variant), +5 bp, 90% interval.\n")
        out.append("| model | cell | days | vs parent | vs climatology | vs persistence-logistic |")
        out.append("|---|---|---|---|---|---|")
        for name in variants:
            for label, cell in document["brier"][name][h].items():
                out.append(
                    f"| {name} | {label} | {int(cell['days'])} | {_interval(cell['vs_parent'])} | "
                    f"{_interval(cell['vs_climatology'])} | {_interval(cell['vs_persistence_logistic'])} |"
                )
    out.append("\nTable 4. The 26 episodes of the post-mortem (#474): who warns at some lead 1 to 5 (all-five misses marked).\n")
    out.append("| start | type | regime | missed by all five | " + " | ".join(parents) + " | " + " | ".join(variants) + " |")
    out.append("|---|---|---|---|" + "---|" * (len(parents) + len(variants)))
    for e in document["episodes"]:
        out.append(
            f"| {e['start']} | {e['day_type']} | {e['regime']} | {'yes' if e['missed_by_all_five'] else 'no'} | "
            + " | ".join("yes" if e[name] else "no" for name in parents + variants)
            + " |"
        )
    return "\n".join(out)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    commands = parser.add_subparsers(dest="command", required=True)
    declare = commands.add_parser("declare", help="write the declaration and the judge's candidate files")
    declare.set_defaults(handler=declare_command)
    run = commands.add_parser("run")
    run.add_argument("--panel", type=Path, required=True)
    run.add_argument("--published", type=Path, required=True)
    run.add_argument("--horizon", type=int, required=True)
    run.add_argument("--candidate", help="one parent")
    run.add_argument("--output", type=Path, required=True)
    run.set_defaults(handler=run_command)
    compare = commands.add_parser("compare", help="each variant beside its parent, climatology and persistence-logistic")
    compare.add_argument("--panel", type=Path, required=True)
    compare.add_argument("--output", type=Path, required=True)
    compare.add_argument("--markdown", type=Path)
    compare.add_argument("inputs", nargs="+", type=Path)
    compare.set_defaults(handler=compare_command)
    args = parser.parse_args(argv)
    return args.handler(args)


if __name__ == "__main__":
    raise SystemExit(main())
