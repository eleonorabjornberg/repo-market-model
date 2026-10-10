"""Score the all-inputs onset classifiers (#479, a track of #374) for the pressure-day judge.

A scratch measurement, not a record: it writes JSON to the paths it is given and nothing
into `docs/runs/`. One question: is the data we already hold enough? One model reads every
series the source screen (#478) inventories as readable as-of, at once, instead of one input
at a time on a weaker model. The inputs, the two candidates and the penalty and depth grids
are in `metadata/all_inputs.json`, which this script refuses to read unless it is committed
and unchanged, as the judge's declaration is. The inputs are off in every published
declaration and switched on for these runs only. Nothing is dropped or selected by its scored
performance; the screen is used to list the inputs, not to rank them.

    # the scratch panel is the screen's (see docs/pivot/source-screen-result.md, Reproduce)
    PYTHONPATH=src python3 scripts/all_inputs.py declare --output metadata/all_inputs.json
    PYTHONPATH=src python3 scripts/all_inputs.py run --panel SCREEN.csv --published PUBLISHED.csv \\
        --horizon H --output OUT/all_inputs_hH.json
    PYTHONPATH=src python3 scripts/pressure_judge.py judge --panel PUBLISHED.csv \\
        --output OUT/judge.json --markdown OUT/judge.md OUT/bench_h?.json OUT/risk_h?.json OUT/all_inputs_h?.json
    PYTHONPATH=src python3 scripts/all_inputs.py compare --panel PUBLISHED.csv --output OUT/compare.json \\
        OUT/bench_h?.json OUT/risk_h?.json OUT/all_inputs_h?.json

`declare` writes the declaration from the screen's evidence (`docs/pivot/evidence/source-screen/screen.json`):
the readable series, each one's availability kind, and the six scheduled series that are public at a lead
of 1 only. `run` fits both candidates to the onset label (`ml.pressure_all_inputs_exceedance`), walk-forward
on the shared fold grid at +5 and +10 bp, days before 2026-01-01 only, with the penalty or depth chosen on
each refit's training pairs alone, then recalibrates out of fold against the pressure-day outcome
(`pressure.recalibrated`), the judged form of the onset classifiers (#409). `compare` reads the judge's own
cut-offs and reports each candidate beside `risk_gbm`, climatology and persistence-logistic.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import subprocess
import sys
from datetime import date, time
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))

from repo_model import measurement_fields, ml, pressure  # noqa: E402
from repo_model.baseline import panel_sha256, rolling_exceedance_backtest  # noqa: E402
from repo_model.data import audit_panel, load_daily_panel  # noqa: E402
from repo_model.evaluation_splits import load_split_declaration  # noqa: E402
from repo_model.lockbox import require_unlocked  # noqa: E402

SPLITS = REPO / "metadata" / "evaluation_splits.json"
DECLARATION = REPO / "metadata" / "all_inputs.json"
SCREEN = REPO / "docs" / "pivot" / "evidence" / "source-screen" / "screen.json"
JUDGED_FORM = "+recalibrated"
#: The design's own columns (`ml._PressureDesign`): the latest spread, the calendar, the scheduled
#: settlements, reserves and the TGA. Every other input enters as an optional column (a value, zero
#: where not yet public, and an observed indicator).
BASE = (
    "spread_bps",
    "days_to_month_end",
    "quarter_end",
    "tax_date",
    "treasury_settlement",
    "treasury_settlement_coupons",
    "reserve_balances",
    "tga",
)
#: What the screen calls a series that is announced for the scored day, so public at a lead of 1 only.
SCHEDULED = "scheduled"


def _load(name: str):
    spec = importlib.util.spec_from_file_location(name, REPO / "scripts" / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def committed_declaration(path: Path) -> dict:
    """The declaration, refused unless it is committed and unchanged since `HEAD`."""

    relative = str(path.resolve().relative_to(REPO))
    dirty = subprocess.run(
        ["git", "status", "--porcelain", "--", relative], cwd=REPO, capture_output=True, text=True, check=True
    ).stdout.strip()
    if dirty:
        raise SystemExit(f"{relative} is not committed ({dirty}); a declaration is made before any score")
    return json.loads(path.read_text(encoding="utf-8"))


def declaration_document(screen: dict) -> dict:
    """The declaration, from the screen's evidence alone; the screen is the inventory (#478)."""

    series = screen["series"]
    kinds = {name: series[name]["kind"] for name in sorted(series)}
    not_public = sorted(name for name in screen["not_public_at_lead"] if name in kinds)
    for name in BASE:
        if name not in kinds:
            raise ValueError(f"{name!r} is a design column but the screen does not inventory it")
    extra = [name for name in kinds if name not in BASE]
    return {
        "status": (
            "declared by the pull request that closes #479 before any score was computed; the inputs are the "
            "series the screen (#478) inventories as readable as-of, listed here with their availability, and "
            "none is dropped or selected by its scored performance; the grids below are stated, not tuned"
        ),
        "scoring": {"last_day": "2025-12-31", "minimum_history": 61, "refit_every": 21, "decision_time": "16:00"},
        "thresholds_bp": [5, 10],
        "horizons": [1, 2, 3, 4, 5],
        "inventory": {
            "source": "docs/pivot/evidence/source-screen/screen.json",
            "series": len(kinds),
            "note": "76 panel series the as-of rule can read, and the spread's own as-of lag (spread_bps)",
        },
        "availability": kinds,
        "public_at_lead_one_only": not_public,
        "inputs": {
            "base": list(BASE),
            "optional": extra,
            "note": (
                "base: the design of the direct models (ml._PressureDesign: the latest spread, the calendar, the "
                "settlements, reserves and the TGA, each scheduled term also crossed with the reserves state); "
                "optional: every other readable series, each entering as its value, zero where not yet public, and "
                "an observed indicator (ml._OnsetDesign); a series public at a lead of 1 only leaves the inputs at "
                "h >= 2 (a hole by the as-of rule, not a zero)"
            ),
        },
        "target": "an onset at the threshold (pressure.onsets, pressure.ONSET_QUIET_DAYS), read off the training rows alone",
        "selection": {
            "settings": "ml.ALL_INPUTS_SETTINGS",
            "frame": "4 expanding-window blocks over each refit's training pairs, an embargo of 5 pairs, pooled held-out log loss",
            "logistic": {"penalties": list(ml.ALL_INPUTS_SETTINGS["logistic"]["penalties"]), "C": list(ml.ALL_INPUTS_SETTINGS["logistic"]["C"])},
            "gbm": {"max_depth": list(ml.ALL_INPUTS_SETTINGS["gbm"]["max_depth"]), "monotone": "none"},
            "training_windows_only": True,
        },
        "recalibration": "pressure.RECALIBRATION: Platt on the candidate's own earlier forecasts against the pressure-day outcome, out of fold, per threshold (the judged form of the onset classifiers, #409); the raw fits are kept as an ablation",
        "judged_form": JUDGED_FORM,
        "cutoffs": "chosen by the judge's cutoff_rule from each refit's training window alone (pressure_judge.json); none is declared here",
        "reference": "risk_gbm, calendar climatology and persistence-logistic",
        "candidates": {
            "all_inputs_logistic": {"kind": "logistic"},
            "all_inputs_gbm": {"kind": "gbm_classifier"},
        },
    }


def declare_command(args) -> int:
    document = declaration_document(json.loads(SCREEN.read_text(encoding="utf-8")))
    args.output.write_text(json.dumps(document, indent=1) + "\n", encoding="utf-8")
    print(json.dumps({"series": document["inventory"]["series"], "optional": len(document["inputs"]["optional"])}))
    return 0


def features_at_horizon(declared: dict, horizon: int) -> tuple:
    """The declared inputs at `horizon`: the series public at a lead of 1 only leave at h >= 2."""

    names = list(declared["inputs"]["base"]) + list(declared["inputs"]["optional"])
    gone = set(declared["public_at_lead_one_only"])
    return tuple(name for name in names if horizon == 1 or name not in gone)


def optional_at_horizon(declared: dict, horizon: int) -> tuple:
    base = set(declared["inputs"]["base"])
    return tuple(name for name in features_at_horizon(declared, horizon) if name not in base)


def column(version):
    return {
        f"{tau:g}": {when.isoformat(): curve[position] for when, curve in zip(version.scored_dates, version.forecast)}
        for position, tau in enumerate(version.taus)
    }


def run_command(args) -> int:
    declared = committed_declaration(DECLARATION)
    h = args.horizon
    if h not in declared["horizons"]:
        raise SystemExit(f"horizon {h} is not declared")
    last = date.fromisoformat(declared["scoring"]["last_day"])
    require_unlocked([last], where="all_inputs")
    screen = _load("source_screen")
    rows = load_daily_panel(args.panel)
    audit_panel(rows)
    if rows[-1].date > last:
        raise SystemExit(f"the panel runs past {last}; this measurement reads no later day")
    splits = load_split_declaration(SPLITS)
    registry = measurement_fields.load_registry()
    taus = tuple(float(t) for t in declared["thresholds_bp"])
    minimum = declared["scoring"]["minimum_history"]
    names = [args.candidate] if args.candidate else list(declared["candidates"])
    features = features_at_horizon(declared, h)
    forecasts, raw_forecasts, settings = {}, {}, {}
    for name in names:
        spec = declared["candidates"][name]
        predictor = ml.pressure_all_inputs_exceedance(
            spec["kind"], features, splits, minimum_history=minimum, optional=optional_at_horizon(declared, h)
        )
        with screen.Switched():
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
        forecasts[name + declared["judged_form"]] = column(pressure.recalibrated(report))
        raw_forecasts[name] = column(report)
        settings[name] = {
            "features": list(report.features),
            "model_settings": dict(report.model_settings),
            "ml_libraries": None if report.ml_libraries is None else dict(report.ml_libraries),
            "selections": predictor.selections,
        }
        print(json.dumps({"horizon": h, "candidate": name, "done": True}), flush=True)
    document = {
        "horizon": h,
        "panel_sha256": panel_sha256(args.published),
        "scratch_panel_sha256": panel_sha256(args.panel),
        "declaration": declared,
        "declarations": settings,
        "forecasts": forecasts,
        "unrecalibrated_forecasts": raw_forecasts,
    }
    args.output.write_text(json.dumps(document, indent=1, sort_keys=True, default=str) + "\n", encoding="utf-8")
    print(json.dumps({"horizon": h, "output": str(args.output)}))
    return 0


def _f(value, places=3):
    return "-" if value is None else f"{value:.{places}f}"


def _interval(cell):
    """`mean [lower, upper]` of a bootstrap cell, or the reason there is no interval."""

    if cell is None or cell.get("mean") is None:
        return "-"
    if "interval" not in cell:
        return f"{cell['mean']:+.4f} (no interval)"
    low, high = cell["interval"]["lower"], cell["interval"]["upper"]
    return f"{cell['mean']:+.4f} [{low:+.4f}, {high:+.4f}]"


def compare_command(args) -> int:
    """The candidates beside `risk_gbm`, climatology and persistence-logistic, under the judge's own cut-offs."""

    from repo_model import pressure_judge as pj

    pj_script = _load("pressure_judge")
    declared = committed_declaration(DECLARATION)
    declaration = pj.load_declaration()
    rows = load_daily_panel(args.panel)
    audit_panel(rows)
    splits = load_split_declaration(SPLITS)
    digest = panel_sha256(args.panel)
    forecasts = []
    selections = {}
    for path in args.inputs:
        document = json.loads(Path(path).read_text())
        if document["panel_sha256"] != digest:
            raise SystemExit(f"{path} was scored on another panel ({document['panel_sha256'][:8]})")
        forecasts.extend(pj.forecasts_from_horizon_document(document))
        for name, record in document.get("declarations", {}).items():
            if "selections" in record:
                selections.setdefault(name, {})[document["horizon"]] = record["selections"]
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
    candidates = [name + declared["judged_form"] for name in declared["candidates"]]
    reference = "risk_gbm"
    for name in candidates + [reference, declaration.climatology, declaration.persistence]:
        if name not in by_name:
            raise SystemExit(f"no forecasts for {name!r} in the inputs")
    horizons = list(declaration.horizons)
    seed = declaration.document()["bootstrap"]["seed"]

    # -- onsets flagged at some lead 1 to 5 (the judge's tier 1 at lead >= 1) ----------------------------
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

    caught_by = {name: caught(name) for name in candidates + [reference]}
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
    for name in candidates:
        cells = {
            label: [
                [m * o for m, o in zip(inside, onset)],
                [m * c for m, c in zip(inside, caught_by[name])],
                [m * c for m, c in zip(inside, caught_by[reference])],
            ]
            for label, inside in cells_for.items()
        }
        recall[name] = pj._bootstrap(declaration, cells, recall_stats, count, seed=pj._seed(seed, "recall", name))
    reference_recall = {
        label: {
            "onsets": int(sum(m * o for m, o in zip(inside, onset))),
            "caught": int(sum(m * c for m, c in zip(inside, caught_by[reference]))),
        }
        for label, inside in cells_for.items()
    }

    # -- Brier score on the +5 bp outcome, paired --------------------------------------------------------
    brier = {}
    for name in candidates:
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
            ref = by_name[reference][h].probabilities[tau]
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
                    "vs_risk_gbm": vs_ref[label]["brier_difference_vs_climatology"],
                }
                for label in groups
            }

    # -- the post-mortem's episodes ------------------------------------------------------------------------
    episodes_path = REPO / "docs" / "pivot" / "evidence" / "episode-post-mortem" / "episodes.json"
    post_mortem = json.loads(episodes_path.read_text(encoding="utf-8"))["episodes"]
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
                "risk_gbm_warns": bool(caught_by[reference][i]),
                **{name: bool(caught_by[name][i]) for name in candidates},
            }
        )
    document = {
        "declaration": declared,
        "reference": reference,
        "onsets": int(sum(onset)),
        "recall_at_some_lead": recall,
        "reference_recall_at_some_lead": reference_recall,
        "brier": brier,
        "episodes": episodes,
        "selections": {
            name: {
                str(h): {
                    "fits": len(records),
                    "settings": {json.dumps(r["setting"]): sum(1 for q in records if q["setting"] == r["setting"]) for r in records},
                    "default_used": sum(1 for r in records if not r["selected"]),
                }
                for h, records in sorted(per.items())
            }
            for name, per in selections.items()
        },
    }
    args.output.write_text(json.dumps(document, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    print(markdown(document, candidates))
    return 0


def markdown(document: dict, candidates) -> str:
    out = []
    ref = document["reference"]
    out.append(f"Table 1. +5 bp onsets flagged at some lead 1 to 5 / onsets, recall, and the recall difference against {ref} (90% interval).\n")
    out.append("| cell | onsets | " + f"{ref} | " + " | ".join(f"{c} | difference vs {ref}" for c in candidates) + " |")
    out.append("|---|---|---|" + "---|---|" * len(candidates))
    for label, reference_cell in document["reference_recall_at_some_lead"].items():
        row = [label, str(reference_cell["onsets"]), f"{reference_cell['caught']}/{reference_cell['onsets']}"]
        for name in candidates:
            cell = document["recall_at_some_lead"][name][label]
            n = int(cell["days"])
            row.append(f"{_f(cell['recall']['mean'])}")
            row.append(_interval(cell["recall_difference"]))
        out.append("| " + " | ".join(row) + " |")
    for h in ("1", "5"):
        out.append(f"\nTable 2 (h = {h}). Brier score the comparison loses to the candidate (positive favours the candidate), +5 bp, 90% interval.\n")
        out.append("| model | cell | days | vs climatology | vs persistence-logistic | vs " + ref + " |")
        out.append("|---|---|---|---|---|---|")
        for name in candidates:
            for label, cell in document["brier"][name][h].items():
                out.append(
                    f"| {name} | {label} | {int(cell['days'])} | {_interval(cell['vs_climatology'])} | "
                    f"{_interval(cell['vs_persistence_logistic'])} | {_interval(cell['vs_risk_gbm'])} |"
                )
    out.append("\nTable 3. The 26 episodes of the post-mortem (#474): who warns at some lead 1 to 5.\n")
    out.append("| start | type | regime | post-mortem | " + ref + " | " + " | ".join(candidates) + " |")
    out.append("|---|---|---|---|---|" + "---|" * len(candidates))
    for e in document["episodes"]:
        cause = e["cause_best_of_five"] or ("missed by all five" if e["missed_by_all_five"] else "warned by at least one")
        out.append(
            f"| {e['start']} | {e['day_type']} | {e['regime']} | {cause} | {'yes' if e['risk_gbm_warns'] else 'no'} | "
            + " | ".join("yes" if e[name] else "no" for name in candidates)
            + " |"
        )
    out.append("\nTable 4. What each refit chose (fits per setting, per horizon).\n")
    for name, per in document["selections"].items():
        for h, record in per.items():
            out.append(f"* {name}, h = {h}: {record['fits']} fits, {record['settings']}, default used {record['default_used']}")
    return "\n".join(out)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    commands = parser.add_subparsers(dest="command", required=True)
    declare = commands.add_parser("declare", help="write the declaration from the screen's evidence")
    declare.add_argument("--output", type=Path, required=True)
    declare.set_defaults(handler=declare_command)
    run = commands.add_parser("run")
    run.add_argument("--panel", type=Path, required=True)
    run.add_argument("--published", type=Path, required=True)
    run.add_argument("--horizon", type=int, required=True)
    run.add_argument("--candidate")
    run.add_argument("--output", type=Path, required=True)
    run.set_defaults(handler=run_command)
    compare = commands.add_parser("compare", help="the candidates beside risk_gbm, climatology and persistence-logistic")
    compare.add_argument("--panel", type=Path, required=True)
    compare.add_argument("--output", type=Path, required=True)
    compare.add_argument("--markdown", type=Path)
    compare.add_argument("inputs", nargs="+", type=Path)
    compare.set_defaults(handler=compare_command)
    args = parser.parse_args(argv)
    return args.handler(args)


if __name__ == "__main__":
    raise SystemExit(main())
