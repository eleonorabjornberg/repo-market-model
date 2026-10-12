"""State-conditioned recalibration of the best row (#589): tier 3's remaining failure, on top of #586's own-leg state.

A scratch measurement, not a record: it writes JSON and Markdown to the paths it is given and nothing into `docs/runs/`.
The parent is `risk_gbm+every_day+gate+settle+h41+iorb` (#579, PR #582), refitted with the own-leg scarcity state of #586.
Two variants recalibrate its forecast, walk-forward on the judge's cadence (a refit every 21 scored days, each block from the
earlier pairs whose scored day is at or before the block's last training label), keyed on the scarcity state read as of the
forecast's decision instant (`pressure_judge._scarcity_states`, each leg at its own latest public row; never a hindsight
regime label, #515):

* (a) `+state_platt`: Platt fitted per state, pooled Platt while the state holds fewer than 60 pairs or 3 events
  (`group_calibration.walk_forward('group')`);
* (c) `+state_shrunk`: a pooled Platt slope with one intercept offset per state, shrunk toward zero by a ridge penalty
  (`group_calibration.walk_forward_shrunk`, a hierarchical intercept).

Variant (b), the time-varying satiation distance of #587 as a covariate, is declared and not run: #587 has not merged.
The declaration is `metadata/state_recalibration_589.json`, committed before any score; this script refuses a declaration
that is not committed. Scored days are 2018-06-29 to 2025-12-31; no day of the 2026 tiers is read (`lockbox.md`).

    # AUG2.csv is the scratch panel of risk_date_severity.py (pressure_v1_1.py panel, then measurement_fields.py panel)
    PYTHONPATH=src python3 scripts/state_recalibration_589.py declare
    for h in 1 2 3 4 5:
      PYTHONPATH=src python3 scripts/pressure_judge.py forecasts --panel PUBLISHED.csv --horizon h --output OUT/bench_hh.json
      PYTHONPATH=src python3 scripts/own_leg_rescore.py own_leg announcement_dating_rescore run --arm both --model risk_gbm \\
          --panel AUG2.csv --published PUBLISHED.csv --horizon h --output OUT/both_hh.json
      PYTHONPATH=src python3 scripts/own_leg_rescore.py own_leg iorb_every_day_579 run --panel AUG2.csv --published PUBLISHED.csv \\
          --horizon h --parent OUT/both_hh.json --output OUT/iorb_hh.json
      PYTHONPATH=src python3 scripts/state_recalibration_589.py run --panel AUG2.csv --published PUBLISHED.csv --horizon h \\
          --parent OUT/iorb_hh.json --output OUT/state_hh.json
    PYTHONPATH=src python3 scripts/pressure_judge.py judge --panel PUBLISHED.csv --rule RULE --output OUT/judge_RULE.json \\
        --markdown OUT/judge_RULE.md OUT/bench_h?.json OUT/iorb_h?.json OUT/state_h?.json
    PYTHONPATH=src python3 scripts/pressure_judge.py table OUT/judge_RULE.json --output OUT/tables_RULE.md
    PYTHONPATH=src python3 scripts/state_recalibration_589.py compare --rule RULE --panel PUBLISHED.csv \\
        --output OUT/compare_RULE.json --markdown OUT/compare_RULE.md OUT/bench_h?.json OUT/iorb_h?.json OUT/state_h?.json
    PYTHONPATH=src python3 scripts/own_leg_compare.py years --rule RULE --panel PUBLISHED.csv --output OUT/years_RULE.json \\
        --rows ROW... -- OUT/bench_h?.json OUT/iorb_h?.json OUT/state_h?.json
    PYTHONPATH=src python3 scripts/state_recalibration_589.py summary --flat OUT/judge_unweighted.json \\
        --weighted OUT/judge_weighted.json --output OUT/summary.md

The parent's forecasts are read from the `iorb_every_day_579.py run` output of the same horizon; the grid, the training
ends and the outcomes come from `baseline.rolling_exceedance_backtest` on the same panel with the climatology as the
(unused) predictor, and the run refuses a parent whose scored days differ from that grid.
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

from repo_model import group_calibration as gc, measurement_fields, probability_calibration as pc  # noqa: E402
from repo_model.baseline import climatology_exceedance, panel_sha256, rolling_exceedance_backtest  # noqa: E402
from repo_model.data import audit_panel, load_daily_panel  # noqa: E402
from repo_model.evaluation_splits import load_split_declaration  # noqa: E402
from repo_model.lockbox import require_unlocked  # noqa: E402

DECLARATION = REPO / "metadata" / "state_recalibration_589.json"
CANDIDATES = REPO / "metadata" / "pressure_judge" / "candidates"
PARENT = "risk_gbm+every_day+gate+settle+h41+iorb"
VARIANT_NAMES = {"a": PARENT + "+state_platt", "c": PARENT + "+state_shrunk"}
RUN_VARIANTS = ("a", "c")


def _load(name: str):
    spec = importlib.util.spec_from_file_location(f"{name}_script", REPO / "scripts" / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[f"{name}_script"] = module
    spec.loader.exec_module(module)
    return module


rds = _load("risk_date_severity")
ann = _load("announcement_dating_rescore")


# -- the declaration ---------------------------------------------------------------------------------------


def declaration_document(parents: dict) -> dict:
    return {
        "status": (
            "declared by the pull request that closes #589 before any score was computed; a measurement, not a record. Nothing here is "
            "published: no variant joins any published declaration, no 2026 day is scored, no rule changes and the live record and pin "
            "do not move"
        ),
        "issue": 589,
        "scoring": parents["scoring"],
        "thresholds_bp": parents["thresholds_bp"],
        "horizons": parents["horizons"],
        "parent": {
            "row": PARENT,
            "declaration": "metadata/iorb_every_day_579.json (PR #582), refitted with the own-leg scarcity state of #586 "
            "(scripts/own_leg_rescore.py own_leg); its forecasts are not changed, only recalibrated",
        },
        "conditioning_variable": (
            "the reserve-scarcity state (0 to 3, or unknown), each of its three legs read at its own latest public row as of the "
            "decision instant (scarcity.own_leg_states, #586; pressure_judge._scarcity_states). It is read as of the decision instant "
            "of each forecast at its own horizon, for the pair a curve is fitted on as for the day it is applied to. No hindsight "
            "regime label (ruling on #515) is used, and group_calibration.scarcity_state_label refuses any other value"
        ),
        "cadence": "the judge's: a refit every 21 scored days from 61 days of history; a block's curve is fitted on the pairs whose scored day is at or before its last training label (probability_calibration.past_positions), and is the identity until those pairs number 250 and hold 5 events",
        "variants": [
            {
                "id": "a",
                "row": VARIANT_NAMES["a"],
                "run": True,
                "what": "state-conditioned recalibration: a Platt curve (the published recalibration's family, declared in place of isotonic, which overfits 70 to 160 positive days) per state, per threshold and horizon, on that state's own earlier observable pairs; the pooled Platt curve while the state holds fewer than 60 pairs or 3 events",
                "implementation": "group_calibration.walk_forward('group') with the state label as the group",
            },
            {
                "id": "b",
                "row": PARENT + "+state_satiation",
                "run": False,
                "what": "variant (a) plus the time-varying satiation distance of #587 as a calibration covariate, if #587 has merged",
                "why_not_run": "#587 had not merged when this was declared (its pull request was open); the variant is not scored here and no result is reported for it",
            },
            {
                "id": "c",
                "row": VARIANT_NAMES["c"],
                "run": True,
                "what": "a shrinkage form: the pooled Platt slope with one intercept offset per state, each offset the maximiser of the state's own log likelihood minus (precision / 2) * offset squared, so a thin state keeps the pooled curve and a rich one may depart from it; a state with no pair gets the pooled curve",
                "implementation": "group_calibration.walk_forward_shrunk",
            },
        ],
        "constants": {
            "group_minimum_pairs": gc.GROUP_MINIMUM_PAIRS,
            "group_minimum_events": gc.GROUP_MINIMUM_EVENTS,
            "shrinkage_precision": gc.SHRINKAGE_PRECISION,
            "pooled_gate": f"{pc.MINIMUM_PAIRS} pairs and {pc.MINIMUM_EVENTS} events (probability_calibration)",
            "searched": "none: the first three are #380's, declared before any scoring, and the shrinkage precision (a prior of standard deviation 1 on the log-odds scale) is declared here before any score; no constant was tuned on a scored day",
        },
        "non_risk_days": "the parent's forecast is exactly 0 on a day the gate does not pass; the curve is fitted on all scored days, so a state's curve gives such a day the state's own rate for it, as in metadata/regime_recalibration.json; this is part of the declared remedy",
        "monotone": "the two thresholds' recalibrated columns are made non-increasing in tau (probability_calibration.monotone_curves), as in #471",
        "judge": "the judge as declared (metadata/pressure_judge.json), unchanged, under the flat and the weighted rule in force on main (pooled-horizon false-alarm count for tier 1, tier 3 from 20 pressure days, the split-years line); the benchmarks and the evaluation days, tiers and onsets do not depend on the row",
        "pairing": "each variant against its parent, with 90% stationary-bootstrap intervals (the judge's bootstrap), split by regime and pressure-day type and by year",
        "ruling_567": "these variants were built after seeing 2018 to 2025, so a pass here is not a confirmation; a variant can replace a shortlist slot only by Eleonora's decision, before the 2026 window opens",
        "published": "nothing; no variant joins any published declaration",
    }


def candidate_document(variant: str) -> dict:
    """The judge's candidate file for a variant: the parent's declaration with the calibration it adds."""

    base = json.loads((CANDIDATES / f"{PARENT}.json").read_text(encoding="utf-8"))
    entry = dict(base)
    entry["track"] = "#589"
    entry["parent"] = PARENT
    if variant == "a":
        added = (
            "then Platt fitted per as-of reserve-scarcity state (0 to 3, or none; each leg at its own latest public row, #586), "
            "on that state's earlier observable pairs, pooled Platt while the state holds fewer than 60 pairs or 3 events "
            "(group_calibration.walk_forward('group') with the state as the group)"
        )
    elif variant == "c":
        added = (
            "then the pooled Platt slope with one shrunk intercept offset per as-of reserve-scarcity state (each leg at its own "
            "latest public row, #586; ridge precision 1.0 on the log-odds offset), on the earlier observable pairs "
            "(group_calibration.walk_forward_shrunk)"
        )
    else:
        raise ValueError(f"variant {variant!r} is not one of {RUN_VARIANTS}")
    entry["calibration"] = base["calibration"] + "; " + added + "; metadata/state_recalibration_589.json"
    return entry


def declare_command(args) -> int:
    parents = json.loads(rds.DECLARATION.read_text(encoding="utf-8"))
    DECLARATION.write_text(json.dumps(declaration_document(parents), indent=2) + "\n", encoding="utf-8")
    for variant, name in VARIANT_NAMES.items():
        (CANDIDATES / f"{name}.json").write_text(json.dumps(candidate_document(variant), indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"declaration": str(DECLARATION), "candidates": [str(CANDIDATES / f"{n}.json") for n in VARIANT_NAMES.values()]}))
    return 0


# -- run ---------------------------------------------------------------------------------------------------


def state_labels(scored, states) -> list:
    """The group of each scored day: its as-of scarcity state (`0` to `3`), or `unknown` when it has none (#515).

    Raises:
        ValueError: for a state that is not 0, 1, 2, 3 or None.
    """

    return [gc.scarcity_state_label(states.get(day)) for day in scored]


def recalibrate(variant, forecasts_by_tau, outcomes_by_tau, scored, train_ends, labels, taus):
    """{tau: [probability per scored day]} for one variant, non-increasing in tau."""

    columns = []
    for tau in taus:
        forecast, outcomes = list(forecasts_by_tau[tau]), list(outcomes_by_tau[tau])
        if variant == "a":
            columns.append(gc.walk_forward("group", forecast, outcomes, scored, train_ends, labels))
        elif variant == "c":
            columns.append(gc.walk_forward_shrunk(forecast, outcomes, scored, train_ends, labels))
        else:
            raise ValueError(f"variant {variant!r} is not one of {RUN_VARIANTS}")
    curves = pc.monotone_curves(list(zip(*columns)))
    return {tau: [curve[k] for curve in curves] for k, tau in enumerate(taus)}


def run_command(args) -> int:
    declared = rds.committed_declaration(DECLARATION)
    h = args.horizon
    if h not in declared["horizons"]:
        raise SystemExit(f"horizon {h} is not declared")
    last = date.fromisoformat(declared["scoring"]["last_day"])
    require_unlocked([last], where="state_recalibration_589")
    parent_document = json.loads(args.parent.read_text(encoding="utf-8"))
    if parent_document["horizon"] != h or parent_document["panel_sha256"] != panel_sha256(args.published):
        raise SystemExit(f"{args.parent} is not the parent's forecasts at h = {h} on this panel")
    if PARENT not in parent_document["forecasts"]:
        raise SystemExit(f"{args.parent} has no {PARENT!r} row")
    parent = parent_document["forecasts"][PARENT]
    rows = load_daily_panel(args.panel)
    audit_panel(rows)
    taus = tuple(float(t) for t in declared["thresholds_bp"])
    minimum = declared["scoring"]["minimum_history"]
    registry = measurement_fields.load_registry()
    # the grid, the training ends and the outcomes: a backtest with the climatology, whose forecasts are not used
    report = rolling_exceedance_backtest(
        rows,
        predictor=climatology_exceedance(minimum),
        model_name="grid",
        features=("spread_bps",),
        registry=registry,
        decision_time=time.fromisoformat(declared["scoring"]["decision_time"]),
        taus=taus,
        minimum_history=minimum,
        refit_every=declared["scoring"]["refit_every"],
        end=last,
        horizon=h,
    )
    scored = list(report.scored_dates)
    train_ends = [fold.train_end for fold in report.folds]
    days = [day.isoformat() for day in scored]
    for tau in taus:
        if sorted(parent[f"{tau:g}"]) != days:
            raise SystemExit(f"the parent's scored days at +{tau:g} bp are not the grid's at h = {h}")
    outcomes_by_tau = {tau: report.at_tau(report.taus.index(tau))[2] for tau in taus}
    forecasts_by_tau = {tau: [parent[f"{tau:g}"][day] for day in days] for tau in taus}
    states = _load("pressure_judge")._scarcity_states(h, last)
    labels = state_labels(scored, states)
    forecasts = {}
    for variant in RUN_VARIANTS:
        recalibrated = recalibrate(variant, forecasts_by_tau, outcomes_by_tau, scored, train_ends, labels, taus)
        forecasts[VARIANT_NAMES[variant]] = {
            f"{tau:g}": {day: recalibrated[tau][k] for k, day in enumerate(days)} for tau in taus
        }
    document = {
        "horizon": h,
        "panel_sha256": panel_sha256(args.published),
        "scratch_panel_sha256": panel_sha256(args.panel),
        "declaration": declared,
        "calibration": gc.declaration(),
        "declarations": {
            name: {"parent": PARENT, "state_counts": {label: labels.count(label) for label in sorted(set(labels))}}
            for name in forecasts
        },
        "forecasts": forecasts,
    }
    args.output.write_text(json.dumps(document, indent=1, sort_keys=True, default=str) + "\n", encoding="utf-8")
    print(json.dumps({"horizon": h, "output": str(args.output)}))
    return 0


# -- compare -----------------------------------------------------------------------------------------------


def markdown(document: dict, pairs) -> str:
    out = []
    ref = pairs[0][2]
    names = [name for _arm, name, _ref in pairs]
    out.append(f"Table 1. +5 bp onsets flagged at some lead 1 to 5, by cell: the parent `{ref}` and each variant.\n")
    out.append("| cell | onsets | parent | " + " | ".join(f"{n.split('+')[-1]} (recall difference, 90% interval)" for n in names) + " |")
    out.append("|---|---|---|" + "---|" * len(names))
    for cell, n_onsets in document["onsets_in_cell"].items():
        cells = [
            f"{document['caught_at_some_lead'][name][cell]} ({ann._interval(document['recall_at_some_lead'][name][cell]['recall_difference'])})"
            for name in names
        ]
        out.append(f"| {cell} | {n_onsets} | {document['caught_at_some_lead'][ref][cell]} | " + " | ".join(cells) + " |")
    out.append("\nTable 2. Flags at +5 bp, by horizon: flags (false alarms); onsets flagged of onsets; false alarms per onset.\n")
    out.append("| row | " + " | ".join(f"h = {h}" for h in (1, 2, 3, 4, 5)) + " |")
    out.append("|---|" + "---|" * 5)
    for label in [ref] + names:
        cells = []
        for h in ("1", "2", "3", "4", "5"):
            c = document["flags"][label][h]
            cells.append(f"{c['flags']}({c['false_alarms']}); {c['onsets_flagged']}/{c['onsets']}; {ann._f(c['false_alarms_per_onset'], 2)}")
        out.append(f"| {label} | " + " | ".join(cells) + " |")
    for name in names:
        out.append(f"\nTable 3 ({name.split('+')[-1]}). Paired Brier difference against the parent, +5 bp (negative favours the variant), 90% interval, h = 1: all days, by regime and by pressure-day type.\n")
        out.append("| cell | days | difference |")
        out.append("|---|---|---|")
        for cell, c in document["brier"][name]["1"].items():
            out.append(f"| {cell} | {int(c['days'])} | {ann._interval(c['vs_published'])} |")
    return "\n".join(out)


def compare_command(args) -> int:
    """`announcement_dating_rescore.py compare` with each variant against its parent."""

    ann.DECLARATION = DECLARATION
    ann.rows_of_pairs = lambda: [(variant, VARIANT_NAMES[variant], PARENT) for variant in RUN_VARIANTS]
    ann.markdown = markdown
    return ann.compare_command(args)


def summary_rows(judged: dict) -> list:
    """The judge's tier 1 (pooled over leads 1 to 5, and leads 3 to 5), tier 3 and tier 5 rows for the parent and the variants, per rule."""

    yes = lambda x: "yes" if x else "no"
    lines = [
        "| row | rule | tier 1, leads 1 to 5: onsets flagged, recall [90%], worst false alarms per onset (limit 2) | tier 1 | tier 1, leads 3 to 5: onsets flagged, recall [90%] | tier 3 | tier 5 | passes |",
        "|---|---|---|---|---|---|---|---|",
    ]
    for name in [PARENT] + [VARIANT_NAMES[v] for v in RUN_VARIANTS]:
        for rule, candidates in judged.items():
            entry = candidates[name]
            tier, late = entry["tiers"]["onset_warning"]["lead_at_least_1"], entry["tiers"]["onset_warning"]["lead_at_least_3"]
            key = "worst_weighted_false_alarms_per_onset" if rule == "weighted" else "worst_false_alarms_per_onset"
            worst = tier.get(key, tier["worst_false_alarms_per_onset"])
            cell = lambda t: f"{t['onsets_flagged']:g} of {t['onsets']} , {t['recall']['mean']:.3f} [{t['recall']['interval']['lower']:.3f}, {t['recall']['interval']['upper']:.3f}]"
            verdict = entry["verdict"]
            lines.append(
                f"| {name} | {rule} | {cell(tier)} , {worst:.2f} | {yes(verdict['tier_1_onset_warning'])} | {cell(late)} | {yes(verdict['tier_3_no_crying_wolf'])} | "
                f"{yes(verdict['tier_5_week_ahead'])} | {yes(verdict['passes'])} |"
            )
    return lines


def summary_command(args) -> int:
    judged = {rule: json.loads(Path(path).read_text())["candidates"] for rule, path in (("flat", args.flat), ("weighted", args.weighted))}
    text = "\n".join(summary_rows(judged)) + "\n"
    args.output.write_text(text, encoding="utf-8")
    print(text)
    return 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("declare").set_defaults(func=declare_command)
    run = sub.add_parser("run")
    run.add_argument("--panel", type=Path, required=True)
    run.add_argument("--published", type=Path, required=True)
    run.add_argument("--horizon", type=int, required=True)
    run.add_argument("--parent", type=Path, required=True, help="iorb_every_day_579.py run output at this horizon")
    run.add_argument("--output", type=Path, required=True)
    run.set_defaults(func=run_command)
    compare = sub.add_parser("compare")
    compare.add_argument("--rule", choices=("unweighted", "weighted"), default="unweighted")
    compare.add_argument("--panel", type=Path, required=True)
    compare.add_argument("--output", type=Path, required=True)
    compare.add_argument("--markdown", type=Path)
    compare.add_argument("inputs", nargs="+", type=Path)
    compare.set_defaults(func=compare_command)
    summary = sub.add_parser("summary")
    summary.add_argument("--flat", type=Path, required=True)
    summary.add_argument("--weighted", type=Path, required=True)
    summary.add_argument("--output", type=Path, required=True)
    summary.set_defaults(func=summary_command)
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
