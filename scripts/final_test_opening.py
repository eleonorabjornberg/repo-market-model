"""The final test, part 2 (#151): the reported-only cells of the lockbox opening.

The primary cell, CRPS at h = 1, is the frozen command's
(`final_test_preregistration.CRPS_COMMAND`, then its `crps` subcommand), and
nothing here touches it. This script scores every other cell of the test
(`final_test_preregistration.CELLS`, all "reported only"), on the near-blind
tier's scored days, 2026-01-02 to 2026-09-03, with the models and baselines
the pre-registration (`docs/decisions/final-test-preregistration.md`) froze:

* `events --horizon H`: the frozen dynamic logit (`_dynamic_logit`), refitted
  walk-forward on the shared fold grid through 2026-09-03, so the window's
  forecasts continue the pre-2026 walk. Its raw probabilities are recalibrated
  by the frozen calibrator (`CHOSEN_CALIBRATOR`, walk-forward). Scored on the
  plain leap, the leap onset (the leap at-risk group, #209), the pressure leap,
  and +5 and +10 bp (the onsets on #209's at-risk group). Leap targets are
  paired against #139's two named leap baselines; +5 and +10 bp against
  calendar climatology and the persistence-logistic, as
  `docs/decisions/pressure-probability.md` declares them.
* `crps-horizon --horizon H` (H = 2 to 5): the published distribution at H
  (pressure model v1's declaration, `live_record.published_distribution_record`)
  against as-of persistence, by CRPS. No frozen command exists for these cells
  (#223); the walk is `live_record.distribution_run`'s fold loop, kept for every
  scored day. Each cell carries Eleonora's label of 4 October 2026 verbatim
  (`NOT_EVIDENCE`).
* `assemble`: one document from the primary cell and the reported-only cells.

Every comparison is paired (baseline minus model: a positive mean favours the
model), with a 90% stationary-bootstrap interval, split by regime and
pressure-day type. A target with fewer than `onset.MINIMUM_EVENTS` events in the
window is labelled "inconclusive" and still reported with its estimate and
interval. Otherwise each comparison takes one of the three labels of the
second amendment of 4 October 2026 (`label`). Nothing here decides the test.

    PYTHONPATH=src /opt/rmm-venv/bin/python scripts/final_test_opening.py events \\
        --panel PUB.csv --horizon H --output OUT/events_hH.json
    OMP_NUM_THREADS=1 PYTHONPATH=src /opt/rmm-venv/bin/python scripts/final_test_opening.py crps-horizon \\
        --panel PUB.csv --horizon H --output OUT/crps_hH.json
    PYTHONPATH=src python3 scripts/final_test_opening.py assemble --cell OUT/crps_cell.json \\
        --compare OUT/crps.json --events OUT/events_h*.json --crps OUT/crps_h*.json --output RECORD.json
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from datetime import date
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))

from repo_model import lockbox, onset, probability_calibration as pc  # noqa: E402
from repo_model.asof import InformationRule  # noqa: E402
from repo_model.baseline import (  # noqa: E402
    calendar_climatology_exceedance,
    panel_sha256,
    persistence_logistic_exceedance,
    split_document,
)
from repo_model.data import audit_panel, load_daily_panel  # noqa: E402
from repo_model.evaluation_splits import load_split_declaration  # noqa: E402
from repo_model.metrics import crps_from_quantiles  # noqa: E402


def _script(name):
    spec = importlib.util.spec_from_file_location(f"opening_{name}", REPO / "scripts" / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


#: The frozen test: its models, constants, window and cells.
fp = _script("final_test_preregistration")

HORIZONS = (1, 2, 3, 4, 5)
TAUS = (5.0, 10.0)
WINDOW = (fp.CRPS_FIRST, fp.CRPS_LAST)
#: Eleonora's ruling of 4 October 2026 on #151 (#229), verbatim: every CRPS cell
#: at h = 2 to 5 carries it next to its verdict.
NOT_EVIDENCE = ("different model from h = 1, and as-of persistence does not widen with "
                "horizon, so this comparison favours the model; not evidence.")
BRIER_SIGN = "paired = Brier(baseline) - Brier(model) per day; a positive mean favours the model"
CRPS_SIGN = ("paired = CRPS(persistence) - CRPS(published) per day; a positive mean favours "
             "the published distribution")
LEAP_BASELINES = (onset.LEAP_CALENDAR_CLIMATOLOGY, onset.LEAP_PERSISTENCE_LOGISTIC)
TAU_BASELINES = ("calendar_climatology", "persistence_logistic")
#: Calendar climatology's declared inputs, as pressure model v1 declares them.
CALENDAR_FEATURES = ("spread_bps", "days_to_month_end", "quarter_end", "tax_date")


def in_window(day: date) -> bool:
    return WINDOW[0] <= day <= WINDOW[1]


def label(paired: dict, events=None) -> str:
    """The second amendment's labels; "inconclusive" below the minimum event count.

    "shown better" is a pass under the primary cell's rule (mean above 0 and
    90% lower bound above 0); "shown worse" has its 90% upper bound below 0;
    anything else is "not shown".
    """

    if events is not None and events < onset.MINIMUM_EVENTS:
        return "inconclusive"
    interval = paired["interval"]
    if paired["mean"] > 0 and interval["lower"] > 0:
        return "shown better"
    if interval["upper"] < 0:
        return "shown worse"
    return "not shown"


def _window_positions(scored):
    positions = [k for k, when in enumerate(scored) if in_window(when)]
    days = [scored[k] for k in positions]
    lockbox.require_unlocked(days, where="final test opening")
    if len(days) != fp.CRPS_WINDOW_DAYS:
        raise ValueError(f"the run scores {len(days)} window days, not {fp.CRPS_WINDOW_DAYS}")
    return positions


def _paired_cell(baseline_losses, model_losses, positions, *, rows, scored, splits, block, seed):
    paired = onset.paired_difference(baseline_losses, model_losses, positions,
                                     block_length=block, seed=seed)
    differences = [baseline_losses[k] - model_losses[k] for k in positions]
    paired["splits"] = split_document(splits, rows, [scored[k] for k in positions], differences,
                                      block_length=block, seed=seed)
    return paired


def _brier_losses(column, outcomes):
    return [(p - o) ** 2 for p, o in zip(column, outcomes)]


def _mean(values):
    values = list(values)
    return sum(values) / len(values) if values else None


def score_target(columns, outcomes, groups, *, rows, scored, splits, block, seed_parts):
    """One target: each column's Brier per group, and the model paired against each baseline.

    `columns` maps "model" and each baseline to its probabilities over every
    scored day; `groups` maps a group name to its positions (all inside the
    window). The false-alarm level is each column's mean probability on the
    at-risk group's days whose outcome is 0.
    """

    losses = {name: _brier_losses(column, outcomes) for name, column in columns.items()}
    out = {}
    for group, positions in groups.items():
        events = sum(outcomes[k] for k in positions)
        entry = {
            "days": len(positions),
            "events": events,
            "brier": {name: _mean(losses[name][k] for k in positions) for name in columns},
            "paired": {},
        }
        for baseline in columns:
            if baseline == "model" or not positions:
                continue
            paired = _paired_cell(
                losses[baseline], losses["model"], positions, rows=rows, scored=scored,
                splits=splits, block=block, seed=onset._seed("#151", *seed_parts, group, baseline),
            )
            paired["label"] = label(paired, events)
            entry["paired"][baseline] = paired
        out[group] = entry
    # A continuity check, not a cell: the same columns on the pre-2026 days, which
    # the pre-registration's selection table scored at h = 1.
    before = [k for k, when in enumerate(scored) if when < WINDOW[0]]
    out["before_window_check"] = {
        "days": len(before),
        "events": sum(outcomes[k] for k in before),
        "brier": {name: _mean(losses[name][k] for k in before) for name in columns},
    }
    return out


def false_alarm_level(group, positions, outcomes, columns):
    """Each column's mean probability on the at-risk group's days whose outcome is 0.

    `positions` are the group's days, as positions into `outcomes` and every column. The
    live scorer reports the same figure through this function (#363).
    """

    calm = [k for k in positions if outcomes[k] == 0]
    return {
        "group": group,
        "days": len(calm),
        "mean_probability": {name: _mean(column[k] for k in calm) for name, column in columns.items()},
    }


def events_command(args) -> int:
    rows = load_daily_panel(args.panel)
    audit_panel(rows)
    if panel_sha256(args.panel) != fp._frozen_panel_sha256():
        raise ValueError("the panel is not the published panel")
    splits = load_split_declaration(fp.SPLITS)
    h = args.horizon
    window = (h, fp.CRPS_LAST)
    report = fp._dynamic_logit(rows, splits, window)
    scored = list(report.scored_dates)
    ends = [fold.train_end for fold in report.folds]
    positions = _window_positions(scored)
    block = fp._block(report)
    jump = fp.leap_jump_bp(h)
    if report.leap_threshold_bp != jump:
        raise ValueError("the run's leap threshold is not J_h")
    rule = InformationRule(json.loads(fp.REGISTRY.read_text()), ("spread_bps",),
                           decision_time=fp.DECISION, horizon=h)
    targets = onset.LeapTargets(rows, rule, jump)
    index_of = {when: i for i, when in enumerate(targets.dates)}
    in_win = set(positions)
    groups = onset.day_groups(rows, scored, splits)
    leap_at_risk = [k for k in onset.leap_onset_group(targets, scored) if k in in_win]
    scheduled = [k for k in groups[onset.GROUP_SCHEDULED] if k in in_win]
    tau_at_risk = [k for k in groups[onset.GROUP_ONSET] if k in in_win]
    method = fp.CHOSEN_CALIBRATOR
    document = {
        "directive": "#151",
        "cell_role": "reported only",
        "horizon": h,
        "panel_sha256": panel_sha256(args.panel),
        "model": fp.CHOSEN,
        "model_name": report.model_name,
        "features": list(report.features),
        "calibrator": method,
        "declaration_sha256": fp.declaration_checksum(),
        "leap_threshold_bp": jump,
        "block_length": block,
        "window": {"first": scored[positions[0]].isoformat(),
                   "last": scored[positions[-1]].isoformat(), "days": len(positions)},
        "walk": {"first": scored[0].isoformat(), "last": scored[-1].isoformat(),
                 "days": len(scored)},
        "sign_convention": BRIER_SIGN,
        "minimum_events": onset.MINIMUM_EVENTS,
        "targets": {},
    }
    for target, raw in (("leap", report.leap_forecast),
                        ("pressure_leap", report.pressure_leap_forecast)):
        flags = targets.labels(target)
        outcomes = [1 if flags[index_of[when]] else 0 for when in scored]
        columns = {
            "model": list(pc.walk_forward(method, list(raw), outcomes, scored, ends)),
            onset.LEAP_CALENDAR_CLIMATOLOGY: onset.leap_calendar_climatology(
                targets, target, scored, ends, splits),
            onset.LEAP_PERSISTENCE_LOGISTIC: onset.leap_persistence_logistic(
                targets, target, scored, ends),
        }
        group_map = {"all_days": positions, onset.GROUP_SCHEDULED: scheduled}
        if target == "leap":
            group_map[onset.GROUP_LEAP_ONSET] = leap_at_risk
        entry = score_target(columns, outcomes, group_map, rows=rows, scored=scored,
                             splits=splits, block=block, seed_parts=(h, target))
        entry["false_alarm_level"] = false_alarm_level(onset.GROUP_LEAP_ONSET, leap_at_risk,
                                                       outcomes, columns)
        document["targets"][target] = entry
    baselines = {
        "calendar_climatology": fp._backtest(
            rows, "calendar_climatology",
            calendar_climatology_exceedance(splits, minimum_history=fp.MINIMUM_HISTORY),
            CALENDAR_FEATURES, TAUS, window),
        "persistence_logistic": fp._backtest(
            rows, "persistence_logistic",
            persistence_logistic_exceedance(minimum_history=fp.MINIMUM_HISTORY),
            ("spread_bps",), TAUS, window),
    }
    for name, other in baselines.items():
        if list(other.scored_dates) != scored:
            raise ValueError(f"{name} is not on the model's fold grid")
    for tau in TAUS:
        position = report.taus.index(tau)
        outcomes = [o[position] for o in report.outcomes]
        columns = {"model": list(pc.walk_forward(
            method, [curve[position] for curve in report.forecast], outcomes, scored, ends))}
        for name, other in baselines.items():
            columns[name] = [curve[other.taus.index(tau)] for curve in other.forecast]
        group_map = {"all_days": positions, onset.GROUP_SCHEDULED: scheduled,
                     onset.GROUP_ONSET: tau_at_risk}
        entry = score_target(columns, outcomes, group_map, rows=rows, scored=scored,
                             splits=splits, block=block, seed_parts=(h, f"+{tau:g}bp"))
        entry["false_alarm_level"] = false_alarm_level(onset.GROUP_ONSET, tau_at_risk,
                                                       outcomes, columns)
        document["targets"][f"+{tau:g}bp"] = entry
    args.output.write_text(json.dumps(document, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({target: {"events": entry["all_days"]["events"],
                               "brier": entry["all_days"]["brier"],
                               "labels": {b: p["label"] for b, p in entry["all_days"]["paired"].items()}}
                      for target, entry in document["targets"].items()}, indent=1))
    return 0


def distribution_walk(rows, *, fit, features, online_calibration, registry, horizon,
                      minimum_history, refit_every):
    """`live_record.distribution_run`'s fold loop, keeping every scored day's quantiles.

    Returns `[(date, quantiles)]` in fold order, and the levels.
    """

    lr = live_record
    declared = tuple(features)
    _field_sources, sources = lr._resolve_fields(declared)
    rule = lr.InformationRule(registry, declared, decision_time=lr.DECISION, horizon=horizon)
    refit = lr.require_refit_every(refit_every)
    dates = [row.date for row in rows]
    grid = lr.fold_grid(dates, registry, decision_time=lr.DECISION,
                        minimum_history=minimum_history, horizon=horizon)
    lockbox.require_unlocked([dates[index] for index in grid], where="final test opening")
    reads_information = lr._reads_information(fit)
    online = None if online_calibration is None else online_calibration(rows, rule)
    fitted, checked, settings = None, False, {}
    out = []
    levels = None
    for indices in lr.refit_blocks(grid, refit):
        for index in indices:
            info = rule.information_set(dates, index)
            rule.check(dates, info)
            for read in info.reads:
                lr._check_decision_relative_availability(
                    registry, read.fields, dates, read.row, index,
                    decision_time=lr.DECISION, horizon=horizon,
                )
            block_frame = rule.frame(rows, info) if index == indices[0] else None
            if block_frame is not None and len(block_frame) < minimum_history:
                raise lr.SplitError(f"the fit for {dates[index]} has too few labels")
            fold = lr._AsOfFold(index, info, block_frame, rule.observation(rows, info))
            if block_frame is not None:
                fitted = lr._fit_at_origin(
                    fit, block_frame, minimum_history=minimum_history,
                    information=rule, reads_information=reads_information,
                )
                if not checked:
                    lr._check_fitter_stayed_inside(fitted.features_read, declared, sources)
                    settings = lr._with_online_settings(lr._model_settings(fitted), online)
                    checked = True
            view = lr._at_decision(fitted, rows, rule, fold)
            if online is not None:
                view = online.view(view, index, fold.feature_row)
            if tuple(view.levels) != tuple(lr.QUANTILE_LEVELS):
                raise ValueError(f"the model reports quantile levels {tuple(view.levels)}")
            predicted = [float(value) for value in view.predict(fold.feature_row)]
            if online is not None:
                online.label(index, rows[index].spread_bps)
            levels = list(view.levels)
            out.append((index, predicted))
    return out, levels, settings


live_record = None


def crps_horizon_command(args) -> int:
    global live_record
    h = args.horizon
    if h == 1:
        raise ValueError("h = 1 is the primary cell: the frozen command scores it")
    rows = load_daily_panel(args.panel)
    audit_panel(rows)
    if panel_sha256(args.panel) != fp._frozen_panel_sha256():
        raise ValueError("the panel is not the published panel")
    live_record = _script("live_record")
    splits = load_split_declaration(fp.SPLITS)
    registry = json.loads(fp.REGISTRY.read_text())
    sides, parsed = live_record._compare_sides(h)
    walks = {}
    for side, (name, fit, features, online) in sides.items():
        walk, levels, settings = distribution_walk(
            rows, fit=fit, features=features, online_calibration=online, registry=registry,
            horizon=h, minimum_history=parsed.minimum_history, refit_every=parsed.refit_every,
        )
        live_record._require_crps_declaration(side, h, name, features, settings)
        walks[side] = (walk, levels)
    if [i for i, _ in walks["published"][0]] != [i for i, _ in walks["persistence"][0]]:
        raise ValueError("the two sides are not on one fold grid")
    indices = [i for i, _ in walks["published"][0]]
    scored = [rows[i].date for i in indices]
    positions = _window_positions(scored)
    losses = {
        side: [crps_from_quantiles(levels, quantiles, rows[i].spread_bps) for i, quantiles in walk]
        for side, (walk, levels) in walks.items()
    }
    block = fp.CRPS_BLOCK_LENGTH + (h - 1)
    seed = onset._seed("#151", "crps", h)
    paired = _paired_cell(losses["persistence"], losses["published"], positions, rows=rows,
                          scored=scored, splits=splits, block=block, seed=seed)
    differences = [losses["persistence"][k] - losses["published"][k] for k in positions]
    from repo_model.metrics import stationary_bootstrap_interval

    lower, upper = stationary_bootstrap_interval(
        lambda idx: sum(differences[i] for i in idx) / len(idx), len(differences),
        block_length=fp.CRPS_SENSITIVITY_BLOCK_LENGTH, seed=seed,
        replications=onset.REPLICATIONS, level=onset.LEVEL,
    )
    cell = {
        "directive": "#151",
        "cell": "crps, h = 2 to 5",
        "cell_role": "reported only",
        "horizon": h,
        "panel_sha256": panel_sha256(args.panel),
        "published_record": live_record.published_distribution_record(h),
        "published_declaration_sha256": live_record.published_declaration_sha256(h),
        "days": len(positions),
        "first": scored[positions[0]].isoformat(),
        "last": scored[positions[-1]].isoformat(),
        "crps_persistence_bps": _mean(losses["persistence"][k] for k in positions),
        "crps_published_bps": _mean(losses["published"][k] for k in positions),
        "mean_difference_bps": paired["mean"],
        "interval": paired["interval"],
        "sensitivity_interval": {"lower": lower, "upper": upper, "level": onset.LEVEL,
                                 "method": "stationary_bootstrap",
                                 "block_length": fp.CRPS_SENSITIVITY_BLOCK_LENGTH,
                                 "replications": onset.REPLICATIONS, "seed": seed,
                                 "decides": "nothing"},
        "splits": paired["splits"],
        "sign_convention": CRPS_SIGN,
        "verdict": fp.crps_verdict({"mean_difference_bps": paired["mean"],
                                    "interval": paired["interval"]}),
        "verdict_label": NOT_EVIDENCE,
    }
    args.output.write_text(json.dumps(cell, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({key: cell[key] for key in ("horizon", "days", "crps_persistence_bps",
                                                 "crps_published_bps", "mean_difference_bps",
                                                 "interval", "verdict")}, indent=1))
    return 0


def assemble_command(args) -> int:
    cell = json.loads(args.cell.read_text(encoding="utf-8"))
    compare = json.loads(args.compare.read_text(encoding="utf-8"))
    if cell["crps_declaration_sha256"] != fp.crps_declaration_checksum():
        raise ValueError("the primary cell was not scored under the frozen CRPS declaration")
    events = sorted((json.loads(p.read_text(encoding="utf-8")) for p in args.events),
                    key=lambda d: d["horizon"])
    crps = sorted((json.loads(p.read_text(encoding="utf-8")) for p in args.crps),
                  key=lambda d: d["horizon"])
    if [d["horizon"] for d in events] != list(HORIZONS):
        raise ValueError("the event cells need every horizon 1 to 5")
    if [d["horizon"] for d in crps] != list(HORIZONS[1:]):
        raise ValueError("the CRPS cells need every horizon 2 to 5")
    document = {
        "directive": "#151",
        "record": "the final test (#150, #151): the near-blind tier opened once",
        "pre_registration": "docs/decisions/final-test-preregistration.md",
        "opened": json.loads((REPO / "metadata" / "lockbox.json").read_text())["tiers"][0]["opened"],
        "declaration_sha256": fp.declaration_checksum(),
        "crps_declaration_sha256": fp.crps_declaration_checksum(),
        "cells": fp.cells(),
        "primary": {
            "command": list(fp.CRPS_COMMAND),
            "compare_record": {
                "panel": compare["panel"],
                "declaration": compare["declaration"],
                "provenance": compare["provenance"],
            },
            "cell": cell["cell"],
            "window_per_origin": [
                {key: entry[key] for key in ("scored_date", "loss_a_bps", "loss_b_bps",
                                             "difference_bps")}
                for entry in compare["comparison"]["per_origin"]
                if in_window(date.fromisoformat(entry["scored_date"]))
            ],
            "claim_if_pass": fp.CRPS_CLAIM,
            "claim": fp.CRPS_CLAIM if cell["cell"]["result"] == "pass" else None,
        },
        "crps_reported_only": crps,
        "events_reported_only": events,
    }
    args.output.write_text(json.dumps(document, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"primary": {k: cell["cell"][k] for k in (
        "days", "mean_difference_bps", "verdict", "result")}}, indent=1))
    return 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="command", required=True)
    ev = sub.add_parser("events", help="the leap and threshold cells at one horizon")
    ev.add_argument("--panel", type=Path, required=True)
    ev.add_argument("--horizon", type=int, choices=HORIZONS, required=True)
    ev.add_argument("--output", type=Path, required=True)
    ev.set_defaults(func=events_command)
    cr = sub.add_parser("crps-horizon", help="the CRPS cell at one horizon from 2 to 5")
    cr.add_argument("--panel", type=Path, required=True)
    cr.add_argument("--horizon", type=int, choices=HORIZONS[1:], required=True)
    cr.add_argument("--output", type=Path, required=True)
    cr.set_defaults(func=crps_horizon_command)
    asm = sub.add_parser("assemble", help="one document from every cell")
    asm.add_argument("--cell", type=Path, required=True)
    asm.add_argument("--compare", type=Path, required=True)
    asm.add_argument("--events", type=Path, nargs="+", required=True)
    asm.add_argument("--crps", type=Path, nargs="+", required=True)
    asm.add_argument("--output", type=Path, required=True)
    asm.set_defaults(func=assemble_command)
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
