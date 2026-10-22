#!/usr/bin/env python3
"""H9 step 3 (#842): H5's candidate with and without each richer target's forecast as an input. Walks, scoring and report.

A scratch measurement, not a record: it writes JSON and Markdown to the paths it is given and nothing into `docs/runs/`.
Every choice is in `metadata/h9_nested_842.json`, which this script refuses to read unless it is committed and unchanged.
Scored decision days end where their fifth target day is on or before 2025-12-31 (`docs/decisions/lockbox.md`;
`require_unlocked`, and the scorer's own guard). Development days give a score and an interval, never a verdict (scoring
protocol v1, #640). The candidate is `gbm_funding` (#634's control), its walk, the benchmarks and the scorer are #634's
(`scripts/spread_distribution_634.py`), the target forecasts are #706's walks (`scripts/richer_targets_706.py`), and the
column that carries a forecast into the candidate is `repo_model.target_forecasts`.

    # PUBLISHED.csv, AUG2D.csv: the commands of scripts/spread_distribution_634.py's docstring; H9D.csv:
    PYTHONPATH=src python3 scripts/richer_targets_639.py panel --panel AUG2D.csv --output H9D.csv
    # the target forecasts: #706's walks, unchanged
    for T in bgcr_dispersion_bps on_rrp_change_bn sofr_dispersion_bps: for h in 1 2 3 4 5:
        PYTHONPATH=src python3 scripts/richer_targets_706.py walk --target $T --horizon $h --panel H9D.csv --output TW/${T}_h$h.json
    # the nested walks
    for h in 1 2 3 4 5: for v in base plus_bgcr_dispersion_bps plus_on_rrp_change_bn plus_sofr_dispersion_bps:
        PYTHONPATH=src python3 scripts/h9_nested_842.py walk --variant $v --horizon $h --published PUBLISHED.csv \\
            --panel H9D.csv --target-walks TW --output OUT/${v}_h$h.json
    PYTHONPATH=src python3 scripts/h9_nested_842.py score --published PUBLISHED.csv --panel H9D.csv --walks OUT --output OUT/score.json
    PYTHONPATH=src python3 scripts/h9_nested_842.py report --score OUT/score.json --output OUT/report.md

`walk` is #634's `gbm_funding` walk (the published features, 23 levels, no calibration) with, for a `plus_` variant, the
target's lead-h forecast column added to the features, under a declaration that switches the column on for this run only. The
forecast on the row of decision day d is the median of the law #706's walk gave for the target day h business days later; the
fit that made it is recorded (`target_forecasts.fit_decision_dates`) and `target_forecasts.attach` refuses a forecast whose fit
came after d. A walk whose output already holds the same variant and lead, from the same panel bytes and the same target
walk, is skipped.
"""

from __future__ import annotations

import argparse
import contextlib
import functools
import hashlib
import importlib.util
import json
import sys
from datetime import date
from pathlib import Path
from typing import Dict, List, Mapping, Optional, Sequence, Tuple

# Lockbox classification (#1058): tests/test_lockbox.py reads these literals from this file's syntax tree.
LOCKBOX_READS = {
    "decision_forecasts": (
        "not_entry",
        "rebuilds the fold grid and the fit instants #706's walks used, from dates and the registry "
        "alone, to key a target's laws by decision day (H9 step 3, #842); fits and scores nothing, "
        "and `walk_command` calls require_unlocked, with `target_forecasts.attach` refusing a "
        "locked decision or target day, before any fit (tests/test_h9_nested_842_script.py, "
        "LockedDayTests)",
    ),
}

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))


def _load(name: str):
    spec = importlib.util.spec_from_file_location(f"{name}_script", REPO / "scripts" / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[f"{name}_script"] = module
    spec.loader.exec_module(module)
    return module


m634 = _load("spread_distribution_634")
m706 = _load("richer_targets_706")
s639 = m706.s639

from repo_model import ml, protocol_benchmarks as pb, richer_targets, scoring_protocol as sp, target_forecasts as tf  # noqa: E402
from repo_model.asof import fold_grid, refit_blocks  # noqa: E402
from repo_model.baseline import panel_sha256  # noqa: E402
from repo_model.data import audit_panel, load_daily_panel  # noqa: E402
from repo_model.evaluation_splits import load_split_declaration  # noqa: E402
from repo_model.lockbox import require_unlocked  # noqa: E402

DECLARATION = REPO / "metadata" / "h9_nested_842.json"
SEED = 842
HORIZONS = sp.HORIZONS
GRID = sp.GRID
LAST_TARGET = date(2025, 12, 31)
EXCLUDED_DAY = date(2019, 9, 18)
DECISION = m634.DECISION
SPLITS = m634.SPLITS
SOURCES = m634.SOURCES
TARGETS = tf.TARGETS
VARIANTS = ("base",) + tuple(f"plus_{t}" for t in TARGETS)
#: the recorded score of #634, whose `gbm_funding` the base re-walks.
RECORDED = REPO / "docs" / "pivot" / "evidence" / "spread-distribution-protocol" / "score.json"
MEASUREMENT = REPO / "metadata" / "sources_measurement.json"
#: the as-of scarcity states of a decision day.
#: a plus walk may start at most this many refit blocks after the base's (the target walk starts after 61 labels).
MAX_SKIPPED_BLOCKS = 6
BANDS = ("ample", "scarce", "unknown")


def committed_declaration(path: Path = DECLARATION) -> dict:
    """The declaration, refused unless it is committed and unchanged since `HEAD`."""

    import subprocess

    relative = str(path.resolve().relative_to(REPO))
    dirty = subprocess.run(
        ["git", "status", "--porcelain", "--", relative], cwd=REPO, capture_output=True, text=True, check=True
    ).stdout.strip()
    if dirty:
        raise SystemExit(f"{relative} is not committed ({dirty}); a declaration is made before any score")
    return json.loads(path.read_text(encoding="utf-8"))


def refuse_locked(days: Sequence[date]) -> None:
    """Refuse a run that would score a day of a locked tier (`docs/decisions/lockbox.md`): raises `LookAheadError`."""

    require_unlocked(list(days), where="h9_nested_842")


def variant_target(variant: str) -> Optional[str]:
    """The target a variant adds to the candidate; `None` for the candidate itself."""

    if variant == "base":
        return None
    target = variant[len("plus_"):] if variant.startswith("plus_") else None
    if target not in TARGETS:
        raise ValueError(f"{variant!r} is not a declared variant")
    return target


def holm(p_values: Sequence[float]) -> List[float]:
    """Holm's step-down adjustment, in the input order."""

    order = sorted(range(len(p_values)), key=lambda i: p_values[i])
    adjusted = [0.0] * len(p_values)
    running = 0.0
    for rank, index in enumerate(order):
        running = max(running, min(1.0, (len(p_values) - rank) * p_values[index]))
        adjusted[index] = running
    return adjusted


# -- the target forecasts --------------------------------------------------------------------------------------------


def target_walk_document(directory: Path, target: str, horizon: int, declared_706: dict, scratch_digest: str) -> dict:
    """#706's walk of `target` at `horizon`, refused unless it is that walk, on the declared scratch panel."""

    path = directory / f"{target}_h{horizon}.json"
    document = json.loads(path.read_text(encoding="utf-8"))
    if document.get("target") != target or document.get("horizon") != horizon:
        raise ValueError(f"{path} is not the walk of {target} at lead {horizon}")
    if document.get("panel_sha256") != scratch_digest or scratch_digest != declared_706["panel"]["sha256"]:
        raise ValueError(f"{path} was not walked on the scratch panel the declarations name")
    if document.get("declaration_sha256") != hashlib.sha256(m706.DECLARATION.read_bytes()).hexdigest():
        raise ValueError(f"{path} was walked under another declaration than metadata/richer_targets_706.json")
    if list(document["levels"]) != list(GRID):
        raise ValueError(f"{path} is not on the protocol's grid")
    return document


def decision_forecasts(document: dict, target: str, horizon: int, panel: Path, declared_706: dict):
    """`(forecast by decision day, fit decision day by decision day)` of one target walk.

    The walk keys each law by its target day; its decision day is `horizon` rows earlier on the target's own panel. The fit
    instants are rebuilt from the same fold grid and refit blocks the walk used.
    """

    sd = m634._load("satiation_distance_598")
    registry = sd.measurement_fields.load_registry()
    rows = m706.panel_rows(panel, target)
    timed_rows, timed_registry = sd.ann.arm_inputs("both", rows, registry, horizon)
    dates = [row.date for row in timed_rows]
    position = {day: index for index, day in enumerate(dates)}
    model = declared_706["model"]
    grid = fold_grid(dates, timed_registry, decision_time=DECISION, minimum_history=model["minimum_history"], horizon=horizon)
    fits = tf.fit_decision_dates(dates, refit_blocks(grid, model["refit_every"]), horizon=horizon)
    forecasts: Dict[date, Optional[List[float]]] = {}
    for day, law in document["laws"].items():
        target_day = date.fromisoformat(day)
        if target_day not in position or position[target_day] - horizon < 0:
            raise ValueError(f"{target}: target day {target_day} has no decision day at lead {horizon}")
        forecasts[dates[position[target_day] - horizon]] = None if law is None else [float(v) for v in law]
    if set(forecasts) != set(fits):
        raise ValueError(f"{target} lead {horizon}: the walk's days are not the days of the fold grid it is read against")
    return forecasts, fits


def finished_walk(output: Path, *, variant: str, horizon: int, published: Path, panel: Path, target_walk: Optional[str]) -> bool:
    try:
        document = json.loads(output.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return False
    if not isinstance(document, dict) or not isinstance(document.get("laws"), dict):
        return False
    return (
        document.get("variant") == variant
        and document.get("horizon") == horizon
        and document.get("panel_sha256") == panel_sha256(published)
        and document.get("scratch_panel_sha256") == hashlib.sha256(panel.read_bytes()).hexdigest()
        and document.get("target_walk_sha256") == target_walk
    )


# -- the walks -------------------------------------------------------------------------------------------------------


def walk_command(args) -> int:
    declared = committed_declaration()
    declared_706 = m706.committed_declaration()
    h, variant = args.horizon, args.variant
    if h not in declared["horizons"]:
        raise SystemExit(f"horizon {h} is not declared")
    target = variant_target(variant)
    require_unlocked([LAST_TARGET], where="h9_nested_842")
    scratch_digest = hashlib.sha256(args.panel.read_bytes()).hexdigest()
    target_path = None if target is None else args.target_walks / f"{target}_h{h}.json"
    target_digest = None if target_path is None else hashlib.sha256(target_path.read_bytes()).hexdigest()
    if finished_walk(args.output, variant=variant, horizon=h, published=args.published, panel=args.panel, target_walk=target_digest):
        print(json.dumps({"variant": variant, "horizon": h, "skipped": "finished walk at " + str(args.output)}))
        return 0
    minimum, refit = declared["scoring"]["minimum_history"], declared["scoring"]["refit_every"]
    published = load_daily_panel(args.published)
    audit_panel(published)
    rows = [row for row in published if row.date <= LAST_TARGET]
    live = m634._load("live_record")
    features = tuple(live.published_features(h))
    registry = json.loads(SOURCES.read_text(encoding="utf-8"))
    attached = 0
    if target is None:
        context = contextlib.nullcontext()
    else:
        document = target_walk_document(args.target_walks, target, h, declared_706, scratch_digest)
        forecasts, fits = decision_forecasts(document, target, h, args.panel, declared_706)
        calendar = [row.date for row in rows]
        position = {day: index for index, day in enumerate(calendar)}
        # the published panel's own calendar must give the same target day for each decision day
        kept, kept_fits = {}, {}
        for decision, law in forecasts.items():
            if decision not in position:
                continue
            kept[decision], kept_fits[decision] = law, fits[decision]
        for day, law in document["laws"].items():
            target_day = date.fromisoformat(day)
            if target_day in position and position[target_day] - h >= 0:
                decision_day = calendar[position[target_day] - h]
                if decision_day not in kept:
                    raise ValueError(f"{target}: the panels disagree about the decision day of target {target_day} at lead {h}")
        rows = tf.attach(rows, kept, kept_fits, target=target, horizon=h)
        attached = sum(1 for law in kept.values() if law is not None)
        features = tuple(sorted(set(features) | {tf.column(target, h)}))
        measurement = json.loads(MEASUREMENT.read_text(encoding="utf-8"))
        registry = {**registry, tf.SOURCE_ID: measurement[tf.SOURCE_ID]}
        context = tf.switched_on()
    fit = functools.partial(ml.fit_gradient_boosted_quantiles, regressors=tuple(f for f in features if f != "spread_bps"), levels=GRID)
    blocks_skipped = 0
    with context:
        while True:
            try:
                result, levels, settings = m634.walk(
                    rows, fit=fit, features=features, online_calibration=None, registry=registry, horizon=h,
                    minimum_history=minimum + refit * blocks_skipped, refit_every=refit, expected_levels=GRID,
                )
                break
            except ValueError as error:
                # the first training windows hold no forecast of the target: start at the base's next refit block
                if target is None or "unobserved on every row" not in str(error) or blocks_skipped >= MAX_SKIPPED_BLOCKS:
                    raise
                blocks_skipped += 1
    laws = {rows[i].date.isoformat(): q for i, q in result}
    document_out = {
        "variant": variant, "horizon": h, "levels": levels,
        "panel_sha256": panel_sha256(args.published), "scratch_panel_sha256": scratch_digest,
        "target_walk_sha256": target_digest, "forecasts_attached": attached, "blocks_skipped": blocks_skipped,
        "features": list(features), "settings": json.loads(json.dumps(settings, default=str)), "laws": laws,
    }
    partial = args.output.with_name(args.output.name + ".partial")
    partial.write_text(json.dumps(document_out, sort_keys=True) + "\n", encoding="utf-8")
    partial.replace(args.output)
    print(json.dumps({"variant": variant, "horizon": h, "days": len(laws), "attached": attached, "missing": sum(1 for v in laws.values() if v is None)}))
    return 0


# -- the score -------------------------------------------------------------------------------------------------------


def load_laws(directory: Path) -> Dict[str, Dict[int, Dict[date, Optional[List[float]]]]]:
    return {name: m634.load_laws(directory, name) for name in VARIANTS}


def drop_day(days: Sequence[date]) -> List[date]:
    return [d for d in days if d != EXCLUDED_DAY]


def score_command(args) -> int:
    declared = committed_declaration()
    require_unlocked([LAST_TARGET], where="h9_nested_842")
    m634.SEED = SEED
    draws = args.draws
    rows = load_daily_panel(args.published)
    audit_panel(rows)
    calendar = [row.date for row in rows]
    position = {day: index for index, day in enumerate(calendar)}
    outcomes = {row.date: row.spread_bps for row in rows}
    row_of = {row.date: row for row in rows}
    splits = load_split_declaration(SPLITS)
    registry = json.loads(SOURCES.read_text(encoding="utf-8"))
    walks = load_laws(args.walks)
    decisions, days_by = {}, {}
    for name, laws in walks.items():
        decisions[name], days_by[name] = m634.lead_forecasts(laws, calendar)
    def scorable(candidates: Sequence[date]):
        """The decision days of `candidates` whose five targets are in range, unlocked and with both benchmarks."""

        inside = [day for day in candidates if all(calendar[position[day] + h] <= LAST_TARGET for h in HORIZONS)]
        refuse_locked(inside + [calendar[position[day] + h] for day in inside for h in HORIZONS])
        usable_days, unbuilt_days = [], []
        for day in inside:
            try:
                pb.forecasts(pb.b1_forecast, rows, [day], registry=registry, decision_time=DECISION)
                pb.forecasts(pb.b2_forecast, rows, [day], registry=registry, decision_time=DECISION, splits=splits)
                usable_days.append(day)
            except sp.ProtocolError as error:
                unbuilt_days.append((day.isoformat(), str(error)))
        return usable_days, unbuilt_days

    base_days, _ = scorable(sorted(days_by["base"]))
    common_all = sorted(set.intersection(*(set(days) for days in days_by.values())))
    common, unbuilt = scorable(common_all)
    if not common:
        raise SystemExit("no decision day has both benchmarks")
    base_b1 = pb.forecasts(pb.b1_forecast, rows, base_days, registry=registry, decision_time=DECISION)
    base_filled = sp.fill_missing({day: decisions["base"][day] for day in base_days}, base_b1, base_days)
    base_all = sp.day_scores(base_filled.forecasts, outcomes, calendar)
    b1 = pb.forecasts(pb.b1_forecast, rows, common, registry=registry, decision_time=DECISION)
    b2 = pb.forecasts(pb.b2_forecast, rows, common, registry=registry, decision_time=DECISION, splits=splits)
    forecasts: Dict[str, Dict[date, Dict[int, Sequence[float]]]] = {"B1": b1, "B2": b2}
    missing = {}
    for name in VARIANTS:
        filled = sp.fill_missing({day: decisions[name][day] for day in common}, b1, common)
        forecasts[name] = filled.forecasts
        missing[name] = {"days": len(filled.missing_days), "share": filled.missing_share}
    names = ["B1", "B2", *VARIANTS]
    primary = {n: sp.day_scores(forecasts[n], outcomes, calendar) for n in names}
    secondary = {n: sp.day_scores(forecasts[n], outcomes, calendar, score=sp.upper_tail_twcrps) for n in names}
    days = sorted(primary["B1"])
    for n in names:
        if sorted(primary[n]) != days or sorted(secondary[n]) != days:
            raise SystemExit(f"{n} does not score the same decision days as B1")
    cells = {n: m634.cell_scores(forecasts[n], outcomes, calendar, sp.grid_crps) for n in names}
    candidates = [v for v in VARIANTS if v != "base"]
    nested = [("base", v) for v in candidates]
    versus = [(b, n) for n in VARIANTS for b in ("B1", "B2")]
    pairs = nested + versus
    document: dict = {
        "declaration": "metadata/h9_nested_842.json",
        "panel_sha256": panel_sha256(args.published),
        "decision_days": {"n": len(days), "first": days[0].isoformat(), "last": days[-1].isoformat()},
        "draws": draws, "seed": SEED, "excluded_day": EXCLUDED_DAY.isoformat(),
        "decision_days_without_a_benchmark": unbuilt, "missing": missing, "names": names,
        "mean_primary": {n: sum(primary[n].values()) / len(days) for n in names},
        "mean_key_secondary": {n: sum(secondary[n].values()) / len(days) for n in names},
        "the_day": {n: primary[n][EXCLUDED_DAY] for n in names if EXCLUDED_DAY in primary[n]},
    }
    recorded = json.loads(RECORDED.read_text(encoding="utf-8"))
    document["reproduction"] = {
        "recorded_gbm_funding_mean_primary": recorded["mean_primary"]["gbm_funding"],
        "recorded_days": recorded["decision_days"]["n"],
        "here_base_mean_primary": sum(base_all.values()) / len(base_all),
        "here_days": len(base_all),
        "base_mean_primary_on_the_common_days": document["mean_primary"]["base"],
    }
    # decision-day attributes
    state = as_of_state(args.panel, days)
    kinds = {(d, h): splits.reporting_day_type(calendar[position[d] + h], row_of[calendar[position[d] + h]].values) for d in days for h in HORIZONS}
    always = lambda d, h: True
    groups: Dict[str, Tuple[List[date], object]] = {"pooled": (list(days), always)}
    for label in splits.regime_labels:
        members = [d for d in days if splits.regime(d) == label]
        if members:
            groups[f"regime:{label}"] = (members, always)
    for band in BANDS:
        members = [d for d in days if state[d] == band]
        if members:
            groups[f"state:{band}"] = (members, always)
    for kind in sorted(set(kinds.values())):
        members = sorted({d for (d, h), k in kinds.items() if k == kind})
        groups[f"type:{kind}"] = (members, lambda d, h, kind=kind: kinds[(d, h)] == kind)
    for h in HORIZONS:
        groups[f"lead:{h}"] = (list(days), lambda d, hh, h=h: hh == h)
    table: Dict[str, dict] = {}
    for label, (members, include) in groups.items():
        means = {n: m634.day_means(cells[n], include) for n in names}
        usable_days = sorted(set(members) & set.intersection(*(set(m) for m in means.values())))
        for suffix, group in (("", usable_days), (" without_2019-09-18", drop_day(usable_days))):
            if suffix and EXCLUDED_DAY not in usable_days:
                continue
            table[label + suffix] = {
                "days": len(group),
                "mean": {n: sum(means[n][d] for d in group) / len(group) for n in names} if group else {},
                "tests": m634.pair_table(means, pairs, group, draws),
            }
    document["table"] = table
    document["table_key_secondary"] = {}
    for label, group in (("pooled", days), ("pooled without_2019-09-18", drop_day(days))):
        document["table_key_secondary"][label] = {
            "days": len(group),
            "mean": {n: sum(secondary[n][d] for d in group) / len(group) for n in names},
            "tests": m634.pair_table(secondary, pairs, group, draws),
        }
    # Holm across the three nested tests on the pooled primary score, with and without the day
    document["holm"] = {}
    for label in ("pooled", "pooled without_2019-09-18"):
        tests = table[label]["tests"]
        keys = [f"base -> {v}" for v in candidates]
        adjusted = holm([tests[k]["bootstrap_p"] for k in keys])
        document["holm"][label] = dict(zip(keys, adjusted))
    document["state_counts"] = {band: sum(1 for d in days if state[d] == band) for band in BANDS}
    args.output.write_text(json.dumps(document, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(args.output), "decision_days": len(days)}))
    return 0


def as_of_state(panel: Path, days: Sequence[date]) -> Dict[date, str]:
    """The as-of scarcity state of each decision day (ample, scarce or unknown), read at its decision instant."""

    sd = m634._load("satiation_distance_598")
    registry = sd.measurement_fields.load_registry()
    rows = [row for row in load_daily_panel(panel) if row.date <= LAST_TARGET]
    audit_panel(rows)
    position = {row.date: index for index, row in enumerate(rows)}
    scored = [position[d] + 1 for d in days]
    with s639.switched():
        reads = richer_targets.as_of_rows(rows, registry, [s639.SCARCITY], leads=(1,), scored=scored, decision_time=DECISION)
    return {d: s639.band(rows[r].values.get(s639.SCARCITY)) for d, r in zip(days, reads[1][s639.SCARCITY])}


# -- the report ------------------------------------------------------------------------------------------------------


def fmt(value: Optional[float], digits: int = 3, signed: bool = False) -> str:
    if value is None:
        return "-"
    return f"{value:+.{digits}f}" if signed else f"{value:.{digits}f}"


def skill_cell(test: Optional[dict]) -> str:
    if not test:
        return "-"
    return f"{fmt(test['skill'], 3, True)} (lower {fmt(test['skill_lower_95_one_sided'], 3, True)})"


def difference_cell(test: Optional[dict]) -> str:
    if not test:
        return "-"
    return f"{fmt(test['mean_difference'], 3, True)} (lower {fmt(test['mean_difference_lower_95_one_sided'], 3, True)})"


def improves(test: Optional[dict]) -> bool:
    return bool(test) and test["mean_difference_lower_95_one_sided"] > 0.0


def readings(document: dict) -> Dict[str, dict]:
    """Per target: does its forecast improve the candidate beyond its interval, pooled, with and without 2019-09-18?"""

    out = {}
    cells = [k for k in document["table"] if not k.startswith("lead:") and k not in ("pooled", "pooled without_2019-09-18")]
    for target in TARGETS:
        key = f"base -> plus_{target}"
        pooled = document["table"]["pooled"]["tests"][key]
        without = document["table"]["pooled without_2019-09-18"]["tests"][key] if "pooled without_2019-09-18" in document["table"] else None
        shown = [c for c in cells if improves(document["table"][c]["tests"].get(key))]
        out[target] = {
            "pooled": improves(pooled), "without": improves(without),
            "skill": pooled["skill"], "lower": pooled["mean_difference_lower_95_one_sided"],
            "cells_read": len(cells), "cells_shown": shown,
        }
    return out


def report_markdown(document: dict, declared: dict) -> str:
    table = document["table"]
    read = readings(document)
    names = document["names"]
    lines = [
        "# H9 step 3: the richer targets' forecasts as inputs of H5's candidate (#842)",
        "",
        "A measurement on development data for hypothesis **H9** (the secondary goal), step 3 of `docs/research/hypotheses/H9.md`, "
        "milestone M4. It is not a record and **not a verdict**: development data never gives one "
        "(`docs/decisions/scoring-protocol.md` §1). Nothing is published: no target joins any published declaration, no published figure moves, "
        "nothing is written into `docs/runs/`. No day after 2025-12-31 is read (`docs/decisions/lockbox.md`; the script refuses a locked day). "
        "Every choice is in `metadata/h9_nested_842.json`, committed before any nested score.",
        "",
        "**The test.** H5's candidate `gbm_funding` (the published funding features, 23 levels, no calibration), fitted walk-forward at leads 1 to 5, "
        "with and without one target's forecast as an extra input. The forecast is the median of #706's walk-forward law of the target for the same target day, "
        "made at the same decision instant from a fit that used only what was public before it. One target at a time; no combination.",
        "",
        f"Decision days: {document['decision_days']['n']} ({document['decision_days']['first']} to {document['decision_days']['last']}). "
        f"Intervals: studentized stationary bootstrap, block 10, {document['draws']} draws, seed {document['seed']}, one-sided 95%. "
        "`d = S(base) − S(base + target)`; positive favours the target's forecast; skill = mean(d) / mean(S(base)).",
        "",
        "## Nested difference on the primary score (grid CRPS, mean over leads 1 to 5)",
        "",
        "| target | CRPS base | CRPS with target | d, all days | skill (lower 95%) | Holm p | d, without 2019-09-18 | Holm p, without |",
        "|---|---|---|---|---|---|---|---|",
    ]
    pooled, without = table["pooled"], table.get("pooled without_2019-09-18")
    for target in TARGETS:
        key = f"base -> plus_{target}"
        p = pooled["tests"][key]
        w = without["tests"][key] if without else None
        lines.append(
            f"| `{target}` | {fmt(pooled['mean']['base'])} | {fmt(pooled['mean']['plus_' + target])} | {difference_cell(p)} | {skill_cell(p)} "
            f"| {fmt(document['holm']['pooled'][key], 3)} | {difference_cell(w)} | "
            f"{fmt(document['holm']['pooled without_2019-09-18'][key], 3) if without else '-'} |"
        )
    lines += [
        "",
        "## Against the benchmarks (skill over B1 and over B2, lower 95% bound)",
        "",
        "| model | over B1 | over B2 |",
        "|---|---|---|",
    ]
    for n in [v for v in names if v not in ("B1", "B2")]:
        lines.append(f"| `{n}` | {skill_cell(pooled['tests'].get(f'B1 -> {n}'))} | {skill_cell(pooled['tests'].get(f'B2 -> {n}'))} |")
    lines += ["", "## Nested difference by split (d, lower 95% bound; days in brackets)", ""]
    header = "| split | " + " | ".join(f"`{t}`" for t in TARGETS) + " |"
    lines += [header, "|" + "---|" * (len(TARGETS) + 1)]
    for label, entry in table.items():
        if label in ("pooled", "pooled without_2019-09-18"):
            continue
        cells = [difference_cell(entry["tests"].get(f"base -> plus_{t}")) for t in TARGETS]
        lines.append(f"| {label} ({entry['days']}) | " + " | ".join(cells) + " |")
    key_secondary = document["table_key_secondary"]
    lines += ["", "## Upper-tail twCRPS (weight 1{y > 0 bp}): d, lower 95% bound", "", "| target | all days | without 2019-09-18 |", "|---|---|---|"]
    for t in TARGETS:
        key = f"base -> plus_{t}"
        lines.append(
            f"| `{t}` | {difference_cell(key_secondary['pooled']['tests'].get(key))} | "
            f"{difference_cell(key_secondary['pooled without_2019-09-18']['tests'].get(key))} |"
        )
    reproduction = document["reproduction"]
    lines += [
        "",
        "## Reproduction of the candidate",
        "",
        f"The base re-walks #634's `gbm_funding`: grid CRPS {fmt(reproduction['here_base_mean_primary'], 4)} on {reproduction['here_days']} days here; "
        f"{fmt(reproduction['recorded_gbm_funding_mean_primary'], 4)} on {reproduction['recorded_days']} days recorded in "
        "`docs/pivot/evidence/spread-distribution-protocol/score.json`. On the days every walk covers (the plus walks start at a later refit block) "
        f"the base reads {fmt(reproduction['base_mean_primary_on_the_common_days'], 4)}.",
        "",
        "## Readings (development data, not a verdict)",
        "",
    ]
    for target in TARGETS:
        r = read[target]
        verdict = "improves" if r["pooled"] else "does not improve"
        lines.append(
            f"* `{target}`: {verdict} the candidate beyond its interval (skill {fmt(r['skill'], 3, True)}, lower bound of d {fmt(r['lower'], 3, True)}); "
            f"without 2019-09-18 it {'improves' if r['without'] else 'does not improve'} it. Development data, not a verdict. "
            f"Split cells read: {r['cells_read']}; cells showing a gain: {', '.join(r['cells_shown']) if r['cells_shown'] else 'none'}."
        )
    nested_gain = any(read[t]["pooled"] for t in TARGETS)
    lines += [
        f"* H9 against its kill (\"no nested gain for H5\"): {'a target improves the candidate on development data' if nested_gain else 'no target improves the candidate beyond its interval on development data'}. "
        "Development data, not a verdict. Nothing is registered, and no target joins a published declaration.",
        "",
    ]
    return "\n".join(lines)


def report_command(args) -> int:
    declared = committed_declaration()
    document = json.loads(args.score.read_text(encoding="utf-8"))
    args.output.write_text(report_markdown(document, declared), encoding="utf-8")
    print(json.dumps({"output": str(args.output)}))
    return 0


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = parser.add_subparsers(dest="command", required=True)
    walk = sub.add_parser("walk")
    walk.add_argument("--variant", required=True)
    walk.add_argument("--horizon", type=int, required=True)
    walk.add_argument("--published", type=Path, required=True)
    walk.add_argument("--panel", type=Path, required=True)
    walk.add_argument("--target-walks", type=Path, required=True)
    walk.add_argument("--output", type=Path, required=True)
    walk.set_defaults(func=walk_command)
    score = sub.add_parser("score")
    score.add_argument("--published", type=Path, required=True)
    score.add_argument("--panel", type=Path, required=True)
    score.add_argument("--walks", type=Path, required=True)
    score.add_argument("--output", type=Path, required=True)
    score.add_argument("--draws", type=int, default=sp.DRAWS)
    score.set_defaults(func=score_command)
    report = sub.add_parser("report")
    report.add_argument("--score", type=Path, required=True)
    report.add_argument("--output", type=Path, required=True)
    report.set_defaults(func=report_command)
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
