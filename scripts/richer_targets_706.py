#!/usr/bin/env python3
"""H9 step 2, the richer targets modelled with #634's model class (#706): walks, scoring and report.

A scratch measurement on development data, not a record and not a verdict (scoring protocol v1, `docs/decisions/scoring-protocol.md`
§1; ruling of Eleonora on #639, 13 October 2026). It writes JSON and Markdown to the paths it is given and nothing into `docs/runs/`.
Every choice is in `metadata/richer_targets_706.json`, which `declare` writes from step 1's screen before any score and which every
other command refuses to read unless it is committed and unchanged. Nothing is published, no day after 2025-12-31 is read
(`docs/decisions/lockbox.md`; `require_unlocked`), and the regimes are the as-of scarcity state and the day type (ruling on #515).

    # PUB.csv, AUG2D.csv: the commands of scripts/spread_distribution_634.py's docstring (the published panel, then the scratch panel
    # with the tax-date window, the measurement fields and the satiation distance)
    PYTHONPATH=src python3 scripts/richer_targets_639.py panel --panel AUG2D.csv --output H9D.csv
    PYTHONPATH=src python3 scripts/richer_targets_706.py declare --panel H9D.csv
    git add metadata/richer_targets_706.json && git commit          # a declaration is made before any score
    for T in <the chosen targets>; for h in 1 2 3 4 5:
        PYTHONPATH=src python3 scripts/richer_targets_706.py walk --target $T --horizon $h --panel H9D.csv --output OUT/${T}_h$h.json
    PYTHONPATH=src python3 scripts/richer_targets_706.py score --panel H9D.csv --walks OUT --output OUT/score.json
    PYTHONPATH=src python3 scripts/richer_targets_706.py report --score OUT/score.json --output OUT/report.md

* **The model** is #634's candidate (b), the gradient-boosted quantile model on the 23 levels of the protocol's grid with the inputs of
  `spread_distribution_634.new_features`, fitted walk-forward on the shared fold grid (minimum history 61, refit every 21 days, leads
  1 to 5). Only the label changes: `richer_targets.as_target` puts the target in the slot the model reads as SOFR - IORB, and
  `richer_targets.swap_target_fields` puts the target's own sources and release lag there too, so the as-of rule reads the label's
  lag under the sources it comes from.
* **Benchmarks** are the target's own B1 (last public value plus the lead's empirical changes over two years) and B2 (a year of values
  on days of the target day's type), `richer_targets.b1_quantiles` and `b2_quantiles`, at each lead. A lead the model has no law for is
  filled by B1 (`scoring_protocol.fill_missing`).
* **Scores** are the protocol's grid CRPS, one number per decision day (the mean over leads 1 to 5), paired against B1 and B2 with the
  stationary bootstrap (`scoring_protocol.paired_tests`), by lead, by the as-of scarcity state of the decision day and by the day type
  of the target day.
"""

from __future__ import annotations

import argparse
import functools
import hashlib
import importlib.util
import json
import subprocess
import sys
from datetime import date, time
from pathlib import Path
from typing import Dict, List, Mapping, Optional, Sequence, Tuple

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))

from repo_model import metrics, ml, pressure, richer_targets, scarcity, scoring_protocol as sp  # noqa: E402
from repo_model.data import audit_panel, exceeds_bp, load_daily_panel  # noqa: E402
from repo_model.evaluation_splits import load_split_declaration  # noqa: E402
from repo_model.lockbox import require_unlocked  # noqa: E402

DECLARATION = REPO / "metadata" / "richer_targets_706.json"
SCREEN = REPO / "docs" / "pivot" / "evidence" / "richer-targets-639" / "screen.json"
SPREAD_SCORE = REPO / "docs" / "pivot" / "evidence" / "spread-distribution-protocol" / "score.json"
SPLITS = REPO / "metadata" / "evaluation_splits.json"
LAST_TARGET = date(2025, 12, 31)
SEED = 706
DRAWS = sp.DRAWS
HORIZONS = sp.HORIZONS
GRID = sp.GRID
DECISION = time(16, 0)
PRE_ONSET_DAYS = (1, 5)
ONSET_DRAWS = 2000
THRESHOLD_BP = 5.0
BANDS = ("ample", "scarce")


def _load(name: str):
    spec = importlib.util.spec_from_file_location(f"{name}_script", REPO / "scripts" / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[f"{name}_script"] = module
    spec.loader.exec_module(module)
    return module


m634 = _load("spread_distribution_634")
s639 = _load("richer_targets_639")


# -- the declaration -----------------------------------------------------------------------------------------------


def declaration_document(panel: Path) -> dict:
    """What is fixed before any score: the choice of targets from step 1's screen, the model, the scoring and the reading rule."""

    screen = json.loads(SCREEN.read_text(encoding="utf-8"))
    choice = richer_targets.choose_targets(screen)
    unsigned = sorted(
        (row for row in choice["ranking"]), key=lambda row: -abs(row["auc_mean"] - 0.5)
    )
    return {
        "status": (
            "declared by the pull request that closes #706 before any score was computed; step 2 of H9, a measurement on development "
            "data, not a record and not a verdict (scoring protocol v1 section 1; ruling on #639, 13 October 2026). Nothing is published: "
            "no target joins any published declaration, no day after 2025-12-31 is read (docs/decisions/lockbox.md), no rule changes, "
            "the live record and pin do not move. A pass is not a confirmation"
        ),
        "issue": 706,
        "hypothesis": "H9 (secondary goal), step 2 of docs/research/hypotheses/H9.md",
        "rulings": [
            "Eleonora, 13 October 2026 (comment 6149435134 on #639): the models and the verdict against H9's kill criterion move to step 2; "
            "step 2's targets are chosen by the four-part rule, applied to step 1's tables and committed before any step 2 score",
            "Eleonora, 12 October 2026: scoring protocol v1 (#640); development data never gives a verdict",
        ],
        "panel": {"sha256": hashlib.sha256(panel.read_bytes()).hexdigest(), "built_by": "scripts/richer_targets_639.py panel over the scratch panel of scripts/spread_distribution_634.py (AUG2D.csv)"},
        "screen": {"path": str(SCREEN.relative_to(REPO)), "sha256": hashlib.sha256(SCREEN.read_bytes()).hexdigest()},
        "choice": {
            "rule": [
                "drop a target whose pooled rank correlation with SOFR - IORB (level, all scored days) has magnitude 0.8 or more",
                "drop a target with fewer than 15 pressure onsets in the development sample",
                "rank the rest by the pre-onset AUC at lead 1 within the as-of scarcity state, averaged over the ample and scarce states, "
                "as step 1 published it (a value read high before onsets is above one half); ties by the larger grid-CRPS skill of B1 over B2 or of B2 over B1 at lead 1",
                "take the top three; fewer survivors are all taken",
            ],
            "chosen": choice["chosen"],
            "ranking": choice["ranking"],
            "dropped": {target: {"reason": reason, "value": value} for target, (reason, value) in sorted(choice["dropped"].items())},
            "readings": {
                "signed": "the AUC as step 1 tabulated it. A target that is low before onsets (the ON RRP level, EFFR) ranks low. This is the "
                          "rule's wording (\"the pre-onset AUC\") and is the one applied",
                "unsigned_order_for_information": [row["target"] for row in unsigned],
                "near_tie": "the third and fourth places differ by less than 0.001 of AUC: a ranking that close is not evidence that one "
                            "target leads more than the other",
            },
        },
        "model": {
            "class": "scripts/spread_distribution_634.py candidate (b): ml.fit_gradient_boosted_quantiles on the 23-level grid, inputs new_features(h)",
            "label": "the target, put in the slot the model reads as SOFR - IORB (richer_targets.as_target); iorb is 0 and the real spread is not an input",
            "availability": "richer_targets.swap_target_fields: the label is read under the release lag of the target's own sources",
            "own_lag_replaces_the_spread_lag": "the model's autoregressive input (spread_bps) is the target's own as-of value; SOFR - IORB itself is not an input",
            "leading_hole": "the first panel day has no ON RRP change; that row is dropped for that target, and the target's walks start with its own fold grid",
            "minimum_history": 61,
            "refit_every": 21,
            "decision_time": "16:00",
            "horizons": list(HORIZONS),
            "seed": SEED,
        },
        "benchmarks": {
            "B1": "richer_targets.b1_quantiles at each lead: the last public value plus the lead's own changes over the trailing two years",
            "B2": "richer_targets.b2_quantiles: the trailing year's values on days of the target day's reporting day type",
            "missing_forecast": "a lead the model has no law for is filled by B1 (scoring_protocol.fill_missing)",
        },
        "scoring": {
            "score": "scoring_protocol.grid_crps on the 23 levels, the mean over leads 1 to 5 per decision day",
            "interval": f"scoring_protocol.paired_tests, stationary bootstrap, mean block {sp.BLOCK_LENGTH}, {DRAWS} draws, seed {SEED}, one-sided 95%",
            "splits": {
                "state": "the as-of scarcity state of the decision day, read as of the decision instant: ample (0, 1) or scarce (2, 3)",
                "day_type": "SplitDeclaration.reporting_day_type of the target day",
            },
            "last_target_day": "2025-12-31",
        },
        "reading": {
            "skill": "a target shows skill over persistence when the one-sided 95% lower bound of mean(S(B1) - S(model)) over all decision days is above zero",
            "skill_over_climatology": "reported beside it against B2, never in its place",
            "lead": (
                "a target shows a lead on the +5 bp episodes when, in every as-of state that holds at least 3 onsets, the lower end of the "
                "two-sided 90% interval of the pre-onset AUC of the model's lead-1 median is above one half (the median of the law for the scored "
                f"day, read on the {PRE_ONSET_DAYS[0]} to {PRE_ONSET_DAYS[1]} panel days before each onset against every other scored day of "
                f"the state; intervals from resampling onsets, {ONSET_DRAWS} draws, seed {SEED}); the as-of value of the target is shown beside it"
            ),
            "kill_criterion": (
                "H9 (docs/research/hypotheses/H9.md, #46): no forecast skill over persistence, or no lead on the +5 bp episodes. "
                "A target meets the criterion when it shows no skill or no lead; H9 is alive on development data only if at least one "
                "target shows both. A reading, labelled development and not a verdict"
            ),
        },
        "nested": (
            "the tables sit beside #634's spread row (docs/pivot/evidence/spread-distribution/score.json, candidate b_gbm_new): the same model "
            "class, the same inputs, the same leads and the same bootstrap, for SOFR - IORB. The units differ, so the comparison is of skill, "
            "not of CRPS. A reading of the directive's wording \"the nested test is against #634's spread row\", put to Eleonora in the pull request"
        ),
    }


def declare_command(args) -> int:
    document = declaration_document(args.panel)
    args.output.write_text(json.dumps(document, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"written": str(args.output), "chosen": document["choice"]["chosen"]}, indent=1))
    return 0


def committed_declaration(path: Path = DECLARATION) -> dict:
    """The declaration, refused unless it is committed and unchanged since `HEAD`."""

    relative = str(path.resolve().relative_to(REPO))
    dirty = subprocess.run(
        ["git", "status", "--porcelain", "--", relative], cwd=REPO, capture_output=True, text=True, check=True
    ).stdout.strip()
    if dirty:
        raise SystemExit(f"{relative} is not committed ({dirty}); a declaration is made before any score")
    return json.loads(path.read_text(encoding="utf-8"))


def refuse_locked(days: Sequence[date]) -> None:
    """Refuse a run that would score a day of a locked tier (`docs/decisions/lockbox.md`): raises `LookAheadError`."""

    require_unlocked(list(days), where="richer_targets_706")


# -- the walks -----------------------------------------------------------------------------------------------------


def panel_rows(panel: Path, target: str):
    """The scratch panel's rows up to the last target day, with the target's leading hole dropped."""

    rows = [row for row in load_daily_panel(panel) if row.date <= LAST_TARGET]
    audit_panel(rows)
    drop = 0
    while drop < len(rows) and rows[drop].values.get(target) is None:
        drop += 1
    if drop > 1 or any(row.values.get(target) is None for row in rows[drop:]):
        raise ValueError(f"{target} has a hole other than the first panel day")
    return rows[drop:]


def walk_command(args) -> int:
    declared = committed_declaration()
    target, h = args.target, args.horizon
    if target not in declared["choice"]["chosen"]:
        raise SystemExit(f"{target!r} is not a chosen target")
    if h not in declared["model"]["horizons"]:
        raise SystemExit(f"horizon {h} is not declared")
    require_unlocked([LAST_TARGET], where="richer_targets_706")
    panel_digest = hashlib.sha256(args.panel.read_bytes()).hexdigest()
    if panel_digest != declared["panel"]["sha256"]:
        raise SystemExit(f"the panel's digest {panel_digest} is not the declared {declared['panel']['sha256']}")
    if finished(args.output, target, h, panel_digest):
        print(json.dumps({"target": target, "horizon": h, "skipped": "finished walk at " + str(args.output)}))
        return 0
    sd = m634._load("satiation_distance_598")
    registry = sd.measurement_fields.load_registry()
    panel = panel_rows(args.panel, target)
    timed_rows, timed_registry = sd.ann.arm_inputs("both", panel, registry, h)
    features = m634.new_features(h)
    fit = functools.partial(
        ml.fit_gradient_boosted_quantiles, regressors=tuple(f for f in features if f != "spread_bps"), levels=GRID
    )
    with sd.switched_on(), sd.h41_release.release_dating(), scarcity.own_leg_composition(), richer_targets.swap_target_fields(target):
        rows = richer_targets.as_target(timed_rows, target)
        result, levels, settings = m634.walk(
            rows, fit=fit, features=features, online_calibration=None, registry=timed_registry, horizon=h,
            minimum_history=declared["model"]["minimum_history"], refit_every=declared["model"]["refit_every"], expected_levels=GRID,
        )
    document = {
        "target": target,
        "horizon": h,
        "levels": levels,
        "panel_sha256": panel_digest,
        "declaration_sha256": hashlib.sha256(DECLARATION.read_bytes()).hexdigest(),
        "features": list(features),
        "settings": json.loads(json.dumps(settings, default=str)),
        "laws": {rows[i].date.isoformat(): q for i, q in result},
    }
    partial = args.output.with_name(args.output.name + ".partial")
    partial.write_text(json.dumps(document, sort_keys=True) + "\n", encoding="utf-8")
    partial.replace(args.output)
    print(json.dumps({"target": target, "horizon": h, "days": len(document["laws"])}))
    return 0


def finished(output: Path, target: str, horizon: int, panel_digest: str) -> bool:
    """Whether `output` already holds this walk: the same target and lead, read from the same panel bytes and declaration."""

    try:
        document = json.loads(output.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return False
    return (
        isinstance(document, dict)
        and isinstance(document.get("laws"), dict)
        and document.get("target") == target
        and document.get("horizon") == horizon
        and document.get("panel_sha256") == panel_digest
        and document.get("declaration_sha256") == hashlib.sha256(DECLARATION.read_bytes()).hexdigest()
    )


# -- scoring -------------------------------------------------------------------------------------------------------


def load_laws(directory: Path, target: str) -> Dict[int, Dict[date, Optional[List[float]]]]:
    out: Dict[int, Dict[date, Optional[List[float]]]] = {}
    for h in HORIZONS:
        document = json.loads((directory / f"{target}_h{h}.json").read_text(encoding="utf-8"))
        if document["horizon"] != h or document["target"] != target:
            raise ValueError(f"{target}_h{h}.json is not the walk of {target} at lead {h}")
        out[h] = {
            date.fromisoformat(day): (None if quantiles is None else [float(v) for v in quantiles])
            for day, quantiles in document["laws"].items()
        }
    return out


def auc_cell(groups: Sequence[Sequence[float]], other: Sequence[float]) -> Optional[dict]:
    pooled = [v for g in groups for v in g]
    if len(groups) < 3 or not pooled or not other:
        return None
    return richer_targets.pre_onset_interval(list(groups), list(other), seed=SEED, draws=ONSET_DRAWS)


def score_target(target: str, args, declared: dict, all_rows, splits, registry) -> dict:
    """One target's decision-day scores against its own B1 and B2, in all its splits, and its lead on the onsets."""

    rows = panel_rows(args.panel, target)
    dates = [row.date for row in rows]
    calendar = dates
    position = {day: index for index, day in enumerate(calendar)}
    values: List[Optional[float]] = [float(row.values[target]) for row in rows]
    outcomes = {row.date: float(row.values[target]) for row in rows}
    kinds = [splits.reporting_day_type(row.date, row.values) for row in rows]
    laws = load_laws(args.walks, target)
    by_decision, decision_days = m634.lead_forecasts(laws, calendar)
    decision_days = [d for d in decision_days if all(calendar[position[d] + h] <= LAST_TARGET for h in HORIZONS)]
    refuse_locked(decision_days + [calendar[position[d] + h] for d in decision_days for h in HORIZONS])
    with s639.switched():
        reads = richer_targets.as_of_rows(
            rows, registry, [target, s639.SCARCITY], leads=(1,), scored=[position[d] + 1 for d in decision_days], decision_time=DECISION
        )
    anchor = dict(zip(decision_days, reads[1][target]))
    state = {d: s639.band(rows[r].values.get(s639.SCARCITY)) for d, r in zip(decision_days, reads[1][s639.SCARCITY])}
    b1: Dict[date, Dict[int, List[float]]] = {}
    b2: Dict[date, Dict[int, List[float]]] = {}
    unbuilt = []
    for d in decision_days:
        i = position[d]
        built1, built2 = {}, {}
        for h in HORIZONS:
            first1 = richer_targets.window_first(dates, i, 2)
            first2 = richer_targets.window_first(dates, i, 1)
            built1[h] = richer_targets.b1_quantiles(values, dates, anchor[d], h, first=first1)
            built2[h] = richer_targets.b2_quantiles(values, kinds, dates, anchor[d], kinds[i + h], first=first2)
        if any(q is None for q in built1.values()) or any(q is None for q in built2.values()):
            unbuilt.append(d.isoformat())
            continue
        b1[d], b2[d] = built1, built2
    days = [d for d in decision_days if d in b1]
    if not days:
        raise SystemExit(f"{target}: no decision day has both benchmarks")
    filled = sp.fill_missing({d: by_decision[d] for d in days}, b1, days)
    forecasts = {"B1": b1, "B2": b2, "model": filled.forecasts}
    primary = {n: sp.day_scores({d: forecasts[n][d] for d in days}, outcomes, calendar) for n in forecasts}
    scored = sorted(primary["B1"])
    for n, scores in primary.items():
        if sorted(scores) != scored:
            raise SystemExit(f"{n} does not score the same decision days as B1")
    pairs = [("B1", "model"), ("B2", "model"), ("B2", "B1")]
    cells = {n: m634.cell_scores({d: forecasts[n][d] for d in scored}, outcomes, calendar, sp.grid_crps) for n in forecasts}
    out: dict = {
        "target": target,
        "decision_days": {"n": len(scored), "first": scored[0].isoformat(), "last": scored[-1].isoformat()},
        "decision_days_without_a_benchmark": unbuilt,
        "missing": {"days": len(filled.missing_days), "share": filled.missing_share},
        "mean": {n: sum(primary[n].values()) / len(scored) for n in primary},
        "pooled": m634.pair_table(primary, pairs, scored, args.draws),
    }
    out["by_lead"] = {}
    for h in HORIZONS:
        means = {n: m634.day_means(cells[n], lambda d, hh, h=h: hh == h) for n in forecasts}
        group = sorted(set.intersection(*(set(m) for m in means.values())))
        out["by_lead"][str(h)] = {
            "n": len(group),
            "mean": {n: sum(means[n][d] for d in group) / len(group) for n in means},
            "tests": m634.pair_table(means, pairs, group, args.draws),
        }
    by_state = {}
    for band in BANDS:
        group = [d for d in scored if state[d] == band]
        if len(group) > sp.HAC_LAG:
            by_state[band] = {
                "n": len(group),
                "mean": {n: sum(primary[n][d] for d in group) / len(group) for n in primary},
                "tests": m634.pair_table(primary, pairs, group, args.draws),
            }
    out["by_state"] = by_state
    by_type = {}
    for kind in sorted({kinds[position[d] + h] for d in scored for h in HORIZONS}):
        include = lambda d, h, kind=kind: kinds[position[d] + h] == kind
        means = {n: m634.day_means(cells[n], include) for n in forecasts}
        group = sorted(set.intersection(*(set(m) for m in means.values())))
        if len(group) > sp.HAC_LAG:
            by_type[kind] = {
                "decision_days": len(group),
                "mean": {n: sum(means[n][d] for d in group) / len(group) for n in means},
                "tests": m634.pair_table(means, pairs, group, args.draws),
            }
    out["by_day_type"] = by_type
    out["lead_on_onsets"] = lead_on_onsets(target, args, all_rows, laws[1], values, position, rows)
    return out


def lead_on_onsets(target, args, all_rows, laws1, values, position, reads, rows) -> dict:
    """The pre-onset AUC of the model's lead-1 median and of the as-of value, within each as-of state (step 1's contrast)."""

    registry = s639.measurement_fields.load_registry()
    splits = load_split_declaration(SPLITS)
    real_dates = [row.date for row in all_rows]
    real_position = {d: i for i, d in enumerate(real_dates)}
    dates = [row.date for row in rows]
    with s639.switched():
        scored_idx = [
            i
            for i in s639.fold_grid(dates, registry, decision_time=DECISION, minimum_history=s639.MINIMUM_HISTORY, horizon=1)
            if s639.FIRST_DAY <= dates[i] <= s639.LAST_DAY
        ]
        every = {
            dates[i]
            for i in s639.fold_grid(dates, registry, decision_time=DECISION, minimum_history=s639.MINIMUM_HISTORY, horizon=5)
            if s639.FIRST_DAY_EVERY_HORIZON <= dates[i] <= s639.LAST_DAY
        }
        lead1 = richer_targets.as_of_rows(rows, registry, [target, s639.SCARCITY], leads=(1,), scored=scored_idx, decision_time=DECISION)[1]
    scored_days = [dates[i] for i in scored_idx]
    onset_days = pressure.onsets(all_rows, THRESHOLD_BP, [d for d in scored_days if d in every])
    state = [s639.band(rows[r].values.get(s639.SCARCITY)) for r in lead1[s639.SCARCITY]]
    median = [None if laws1.get(d) is None else richer_targets.median(laws1[d]) for d in scored_days]
    asof_value = [values[r] for r in lead1[target]]
    index = {d: k for k, d in enumerate(scored_days)}
    groups_idx = []
    for onset in onset_days:
        at = real_position[onset]
        groups_idx.append([index[real_dates[at - back]] for back in range(PRE_ONSET_DAYS[0], PRE_ONSET_DAYS[1] + 1) if real_dates[at - back] in index])
    pre = {k for g in groups_idx for k in g}
    cells = {}
    for name, series in (("model_median", median), ("as_of_value", asof_value)):
        cell = {}
        for band in BANDS:
            usable = lambda k, band=band: series[k] is not None and state[k] == band
            groups = [[series[k] for k in g if usable(k)] for g in groups_idx]
            groups = [g for g in groups if g]
            other = [series[k] for k in range(len(scored_days)) if k not in pre and usable(k)]
            result = auc_cell(groups, other)
            cell[band] = {"onsets": len(groups), **(result if result else {})}
        cells[name] = cell
    return {"onsets": [d.isoformat() for d in onset_days], "scored_days": len(scored_days), "cells": cells}


def score_command(args) -> int:
    declared = committed_declaration()
    require_unlocked([LAST_TARGET], where="richer_targets_706")
    panel_digest = hashlib.sha256(args.panel.read_bytes()).hexdigest()
    if panel_digest != declared["panel"]["sha256"]:
        raise SystemExit(f"the panel's digest {panel_digest} is not the declared {declared['panel']['sha256']}")
    all_rows = [row for row in load_daily_panel(args.panel) if row.date <= LAST_TARGET]
    splits = load_split_declaration(SPLITS)
    registry = s639.measurement_fields.load_registry()
    results = {}
    for target in declared["choice"]["chosen"]:
        results[target] = score_target(target, args, declared, all_rows, splits, registry)
    reference = {}
    if SPREAD_SCORE.exists():
        spread = json.loads(SPREAD_SCORE.read_text(encoding="utf-8"))
        reference = {key: spread["pooled_primary"].get(key) for key in ("B1 -> b_gbm_new", "B2 -> b_gbm_new")}
    document = {
        "declaration": "metadata/richer_targets_706.json",
        "declaration_sha256": hashlib.sha256(DECLARATION.read_bytes()).hexdigest(),
        "panel_sha256": panel_digest,
        "draws": args.draws,
        "seed": SEED,
        "targets": results,
        "spread_reference_634": reference,
    }
    args.output.write_text(json.dumps(document, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(args.output), "targets": list(results)}))
    return 0


# -- the report ----------------------------------------------------------------------------------------------------


def fmt(value: Optional[float], digits: int = 3, signed: bool = False) -> str:
    if value is None:
        return "-"
    return f"{value:+.{digits}f}" if signed else f"{value:.{digits}f}"


def skill_cell(test: Optional[dict]) -> str:
    if not test:
        return "-"
    return f"{fmt(test['skill'], 3, True)} (lower {fmt(test['skill_lower_95_one_sided'], 3, True)})"


def readings(result: dict) -> Tuple[bool, bool]:
    """(skill shown, lead shown) for one target, by the declared reading rule."""

    pooled = result["pooled"].get("B1 -> model")
    skill = bool(pooled and pooled["mean_difference_lower_95_one_sided"] > 0.0)
    cells = result["lead_on_onsets"]["cells"]["model_median"]
    states = [cell for cell in cells.values() if cell["onsets"] >= 3 and "auc_low" in cell]
    lead = bool(states) and all(cell["auc_low"] > 0.5 for cell in states) and all(
        cell["onsets"] < 3 or "auc_low" in cell for cell in cells.values()
    )
    return skill, lead


def report_markdown(document: dict, declared: dict) -> str:
    lines = ["# H9 step 2: the richer targets modelled with #634's model class (#706)", ""]
    lines += [
        "Development data only: **not a verdict** (scoring protocol v1 §1). Declared in `metadata/richer_targets_706.json` before any score.",
        "",
    ]
    lines += ["## Pooled over decision days (grid CRPS, mean over leads 1 to 5)", ""]
    lines += ["| target | decision days | CRPS B1 | CRPS B2 | CRPS model | skill over B1 (lower 95%) | skill over B2 (lower 95%) | B1 over B2 |", "|---|---|---|---|---|---|---|---|"]
    for target, result in document["targets"].items():
        mean = result["mean"]
        lines.append(
            f"| `{target}` | {result['decision_days']['n']} | {fmt(mean['B1'])} | {fmt(mean['B2'])} | {fmt(mean['model'])} | "
            f"{skill_cell(result['pooled'].get('B1 -> model'))} | {skill_cell(result['pooled'].get('B2 -> model'))} | {skill_cell(result['pooled'].get('B2 -> B1'))} |"
        )
    reference = document.get("spread_reference_634") or {}
    if reference.get("B1 -> b_gbm_new"):
        lines.append(
            f"| (for scale) SOFR − IORB, #634 candidate (b) | - | - | - | - | {skill_cell(reference['B1 -> b_gbm_new'])} | {skill_cell(reference.get('B2 -> b_gbm_new'))} | - |"
        )
    lines += ["", "Skill is `mean(S(benchmark) − S(model)) / mean(S(benchmark))`; positive favours the model. The last row is #634's spread row: the same model class, inputs, leads and bootstrap for SOFR − IORB.", ""]
    lines += ["## By lead (skill over B1, lower 95% bound)", "", "| target | " + " | ".join(f"lead {h}" for h in HORIZONS) + " |", "|---|" + "---|" * len(HORIZONS)]
    for target, result in document["targets"].items():
        lines.append(f"| `{target}` | " + " | ".join(skill_cell(result["by_lead"][str(h)]["tests"].get("B1 -> model")) for h in HORIZONS) + " |")
    lines += ["", "## By as-of scarcity state of the decision day (skill over B1)", "", "| target | " + " | ".join(BANDS) + " |", "|---|" + "---|" * len(BANDS)]
    for target, result in document["targets"].items():
        cells = []
        for band in BANDS:
            entry = result["by_state"].get(band)
            cells.append(f"{skill_cell(entry['tests'].get('B1 -> model'))} ({entry['n']} days)" if entry else "-")
        lines.append(f"| `{target}` | " + " | ".join(cells) + " |")
    kinds = sorted({k for r in document["targets"].values() for k in r["by_day_type"]})
    lines += ["", "## By day type of the target day (skill over B1)", "", "| target | " + " | ".join(kinds) + " |", "|---|" + "---|" * len(kinds)]
    for target, result in document["targets"].items():
        cells = []
        for kind in kinds:
            entry = result["by_day_type"].get(kind)
            cells.append(f"{skill_cell(entry['tests'].get('B1 -> model'))} ({entry['decision_days']})" if entry else "-")
        lines.append(f"| `{target}` | " + " | ".join(cells) + " |")
    lines += ["", "## Lead on the +5 bp episodes (pre-onset AUC at lead 1, within the as-of state)", "", "| target | series | state | onsets | AUC | 90% interval |", "|---|---|---|---|---|---|"]
    for target, result in document["targets"].items():
        for series, cells in result["lead_on_onsets"]["cells"].items():
            for band, cell in cells.items():
                lines.append(
                    f"| `{target}` | {series} | {band} | {cell['onsets']} | {fmt(cell.get('auc'))} | "
                    f"{('[' + fmt(cell['auc_low']) + ', ' + fmt(cell['auc_high']) + ']') if 'auc_low' in cell else '-'} |"
                )
    lines += ["", "## Reading against H9's kill criterion (development, not a verdict)", ""]
    shown_both = []
    for target, result in document["targets"].items():
        skill, lead = readings(result)
        lines.append(f"* `{target}`: skill over persistence {'shown' if skill else 'not shown'}; lead on the episodes {'shown' if lead else 'not shown'}.")
        if skill and lead:
            shown_both.append(target)
    lines.append("")
    if shown_both:
        lines.append(f"**Reading.** {', '.join('`' + t + '`' for t in shown_both)} show both; the kill criterion is not met for them on development data. This is not a verdict.")
    else:
        lines.append("**Reading.** No chosen target shows both skill over persistence and a lead on the +5 bp episodes on development data; the kill criterion as worded is met. This is not a verdict, and it rests on days that confirmation will not use.")
    lines.append("")
    return "\n".join(lines)


def report_command(args) -> int:
    declared = committed_declaration()
    document = json.loads(args.score.read_text(encoding="utf-8"))
    args.output.write_text(report_markdown(document, declared) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(args.output)}))
    return 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    commands = parser.add_subparsers(dest="command", required=True)
    declare = commands.add_parser("declare", help="write the declaration, before any score")
    declare.add_argument("--panel", type=Path, required=True)
    declare.add_argument("--output", type=Path, default=DECLARATION)
    declare.set_defaults(handler=declare_command)
    walk = commands.add_parser("walk", help="one target's walk at one lead")
    walk.add_argument("--target", required=True)
    walk.add_argument("--horizon", type=int, required=True)
    walk.add_argument("--panel", type=Path, required=True)
    walk.add_argument("--output", type=Path, required=True)
    walk.set_defaults(handler=walk_command)
    score = commands.add_parser("score", help="score the walks against each target's own B1 and B2")
    score.add_argument("--panel", type=Path, required=True)
    score.add_argument("--walks", type=Path, required=True)
    score.add_argument("--output", type=Path, required=True)
    score.add_argument("--draws", type=int, default=DRAWS)
    score.set_defaults(handler=score_command)
    report = commands.add_parser("report", help="the tables")
    report.add_argument("--score", type=Path, required=True)
    report.add_argument("--output", type=Path, required=True)
    report.set_defaults(handler=report_command)
    args = parser.parse_args(argv)
    return args.handler(args)


if __name__ == "__main__":
    sys.exit(main())
