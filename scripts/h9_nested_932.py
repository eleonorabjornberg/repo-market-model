#!/usr/bin/env python3
"""H9 step 3, re-run with aligned training pairs (#932; finding #915): walks, scoring and report.

A scratch measurement, not a record: it writes JSON and Markdown to the paths it is given and nothing into `docs/runs/`.
Every choice is in `metadata/h9_nested_932.json`, which this script refuses to read unless it is committed and unchanged.
It re-runs #842's nested test (`scripts/h9_nested_842.py`, PR #856), whose plus walks trained each forecast column against the
wrong day at leads 2 to 5 (finding #915). The candidate, the target forecasts, the panel, the scored days, the scorer and the
interval are #842's. What changes is the pairing the plus walks are fitted on: `training_pairs="direct"`, so training row p of a
lead-h walk holds the forecast of the target for the label day (`target_forecasts.column` on row t - h is the forecast of T for
day t, and the pair for label day t reads it). Scored decision days end where their fifth target day is on or before 2025-12-31
(`docs/decisions/lockbox.md`; `require_unlocked`, and the scorer's own guard). Development days give a score and an interval,
never a verdict (scoring protocol v1, #640); reading H9's kill clause is Eleonora's.

    # PUBLISHED.csv, AUG2D.csv, H9D.csv, TW/ (the target forecasts): the commands of scripts/h9_nested_842.py's docstring. The
    # target walks (scripts/richer_targets_706.py) are fitted on direct pairs under #706's declaration as amended for this
    # directive, and `walk` below refuses a target walk whose recorded fit does not say so (richer_targets_706.check_pairing)
    for h in 1 2 3 4 5: for v in base base_direct plus_direct_bgcr_dispersion_bps plus_direct_on_rrp_change_bn plus_direct_sofr_dispersion_bps:
        PYTHONPATH=src python3 scripts/h9_nested_932.py walk --variant $v --horizon $h --published PUBLISHED.csv \\
            --panel H9D.csv --target-walks TW --output OUT/${v}_h$h.json
    PYTHONPATH=src python3 scripts/h9_nested_932.py score --published PUBLISHED.csv --panel H9D.csv --walks OUT --output OUT/score.json
    PYTHONPATH=src python3 scripts/h9_nested_932.py report --score OUT/score.json --output OUT/report.md

`walk` is #842's walk (`gbm_funding`, the published features, 23 levels, no calibration; for a `plus_direct_` variant the target's
lead-h forecast column added under a declaration that switches it on for this run only), fitted on direct pairs for `base_direct`
and every plus variant, and on one-step pairs for `base`, #842's own candidate. `score` refuses a walk whose recorded fit settings
do not say which pairing it was fitted on (`check_alignment`). A walk whose output already holds the same variant and lead, from
the same panel bytes and the same target walk, is skipped, so a stopped run resumes from the walks it wrote.
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

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))


def _load(name: str):
    spec = importlib.util.spec_from_file_location(f"{name}_script", REPO / "scripts" / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[f"{name}_script"] = module
    spec.loader.exec_module(module)
    return module


m842 = _load("h9_nested_842")
m634, m706 = m842.m634, m842.m706

from repo_model import ml, protocol_benchmarks as pb, scoring_protocol as sp, target_forecasts as tf  # noqa: E402
from repo_model.baseline import panel_sha256  # noqa: E402
from repo_model.data import audit_panel, load_daily_panel  # noqa: E402
from repo_model.evaluation_splits import load_split_declaration  # noqa: E402
from repo_model.lockbox import require_unlocked  # noqa: E402

DECLARATION = REPO / "metadata" / "h9_nested_932.json"
SEED = 932
HORIZONS = sp.HORIZONS
GRID = sp.GRID
LAST_TARGET = m842.LAST_TARGET
EXCLUDED_DAY = m842.EXCLUDED_DAY
DECISION = m842.DECISION
TARGETS = tf.TARGETS
#: `base` is #842's candidate on one-step pairs; `base_direct` is the same candidate on direct pairs; a plus variant adds one
#: target's forecast column and is fitted on direct pairs.
VARIANTS = ("base", "base_direct") + tuple(f"plus_direct_{t}" for t in TARGETS)
PLUS = tuple(v for v in VARIANTS if v.startswith("plus_direct_"))
PRIMARY = tuple(("base_direct", v) for v in PLUS)
SECONDARY = tuple(("base", v) for v in PLUS) + (("base", "base_direct"),)
BANDS = m842.BANDS
MAX_SKIPPED_BLOCKS = m842.MAX_SKIPPED_BLOCKS
RECORDED_842 = REPO / "docs" / "pivot" / "evidence" / "h9-nested-842" / "score.json"

committed_declaration = functools.partial(m842.committed_declaration, DECLARATION)


def refuse_locked(days: Sequence[date]) -> None:
    """Refuse a run that would score a day of a locked tier (`docs/decisions/lockbox.md`): raises `LookAheadError`."""

    require_unlocked(list(days), where="h9_nested_932")


def variant_parts(variant: str) -> Tuple[Optional[str], bool]:
    """`(the target the variant adds, whether it is fitted on direct pairs)`; the target is `None` for the candidate itself."""

    if variant == "base":
        return None, False
    if variant == "base_direct":
        return None, True
    target = variant[len("plus_direct_"):] if variant.startswith("plus_direct_") else None
    if target not in TARGETS:
        raise ValueError(f"{variant!r} is not a declared variant")
    return target, True


def fitter(features: Sequence[str], *, direct: bool):
    """#634's `gbm_funding` fit over `features`, on direct pairs when `direct`, on one-step pairs (#842's) otherwise."""

    extra = {"training_pairs": "direct"} if direct else {}
    return functools.partial(
        ml.fit_gradient_boosted_quantiles, regressors=tuple(f for f in features if f != "spread_bps"), levels=GRID, **extra
    )


def check_alignment(variant: str, settings: Mapping) -> None:
    """A walk is refused unless its recorded fit says it was fitted on the pairing its variant declares.

    Raises:
        ValueError: a direct variant whose fit did not name `training_pairs` `'direct'`, or the one-step base whose fit did.
    """

    _target, direct = variant_parts(variant)
    if isinstance(settings, str):
        raise ValueError(f"{variant}: the walk's fit settings are not a mapping")
    named = settings.get("training_pairs")
    if direct and named != "direct":
        raise ValueError(f"{variant} must be fitted on direct pairs, but its fit names training_pairs {named!r}")
    if not direct and named is not None:
        raise ValueError(f"{variant} is #842's one-step candidate, but its fit names training_pairs {named!r}")


def settings_of(document: Mapping) -> Mapping:
    """A walk's recorded fit settings (`spread_distribution_634.py` writes them with `default=str`; both forms are read)."""

    settings = document.get("settings", {})
    if isinstance(settings, str):
        import ast

        settings = ast.literal_eval(settings)
    if not isinstance(settings, Mapping):
        raise ValueError(f"the walk's settings are not a mapping: {settings!r}")
    return settings


# -- the walks -------------------------------------------------------------------------------------------------------


def walk_command(args) -> int:
    declared = committed_declaration()
    declared_706 = m706.committed_declaration()
    h, variant = args.horizon, args.variant
    if h not in declared["horizons"]:
        raise SystemExit(f"horizon {h} is not declared")
    target, direct = variant_parts(variant)
    require_unlocked([LAST_TARGET], where="h9_nested_932")
    scratch_digest = hashlib.sha256(args.panel.read_bytes()).hexdigest()
    target_path = None if target is None else args.target_walks / f"{target}_h{h}.json"
    target_digest = None if target_path is None else hashlib.sha256(target_path.read_bytes()).hexdigest()
    if m842.finished_walk(args.output, variant=variant, horizon=h, published=args.published, panel=args.panel, target_walk=target_digest):
        print(json.dumps({"variant": variant, "horizon": h, "skipped": "finished walk at " + str(args.output)}))
        return 0
    minimum, refit = declared["scoring"]["minimum_history"], declared["scoring"]["refit_every"]
    published = load_daily_panel(args.published)
    audit_panel(published)
    rows = [row for row in published if row.date <= LAST_TARGET]
    live = m634._load("live_record")
    features = tuple(live.published_features(h))
    registry = json.loads(m842.SOURCES.read_text(encoding="utf-8"))
    attached = 0
    if target is None:
        context = contextlib.nullcontext()
    else:
        document = m842.target_walk_document(args.target_walks, target, h, declared_706, scratch_digest)
        m706.check_pairing(document.get("settings") or {})
        forecasts, fits = m842.decision_forecasts(document, target, h, args.panel, declared_706)
        calendar = [row.date for row in rows]
        position = {day: index for index, day in enumerate(calendar)}
        kept, kept_fits = {}, {}
        for decision, law in forecasts.items():
            if decision in position:
                kept[decision], kept_fits[decision] = law, fits[decision]
        for day in document["laws"]:
            target_day = date.fromisoformat(day)
            if target_day in position and position[target_day] - h >= 0 and calendar[position[target_day] - h] not in kept:
                raise ValueError(f"{target}: the panels disagree about the decision day of target {target_day} at lead {h}")
        rows = tf.attach(rows, kept, kept_fits, target=target, horizon=h)
        attached = sum(1 for law in kept.values() if law is not None)
        features = tuple(sorted(set(features) | {tf.column(target, h)}))
        measurement = json.loads(m842.MEASUREMENT.read_text(encoding="utf-8"))
        registry = {**registry, tf.SOURCE_ID: measurement[tf.SOURCE_ID]}
        context = tf.switched_on()
    fit = fitter(features, direct=direct)
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
    settings = json.loads(json.dumps(settings, default=str))
    check_alignment(variant, settings_of({"settings": settings}))
    laws = {rows[i].date.isoformat(): q for i, q in result}
    document_out = {
        "variant": variant, "horizon": h, "levels": levels,
        "panel_sha256": panel_sha256(args.published), "scratch_panel_sha256": scratch_digest,
        "target_walk_sha256": target_digest, "forecasts_attached": attached, "blocks_skipped": blocks_skipped,
        "features": list(features), "settings": settings, "laws": laws,
    }
    partial = args.output.with_name(args.output.name + ".partial")
    partial.write_text(json.dumps(document_out, sort_keys=True) + "\n", encoding="utf-8")
    partial.replace(args.output)
    print(json.dumps({"variant": variant, "horizon": h, "days": len(laws), "attached": attached, "missing": sum(1 for v in laws.values() if v is None)}))
    return 0


# -- the score -------------------------------------------------------------------------------------------------------


def load_laws(directory: Path) -> Dict[str, Dict[int, Dict[date, Optional[List[float]]]]]:
    """Every variant's walks, each refused unless its recorded fit names the pairing its variant declares."""

    out = {}
    for name in VARIANTS:
        for h in HORIZONS:
            document = json.loads((directory / f"{name}_h{h}.json").read_text(encoding="utf-8"))
            if document.get("variant") != name or document.get("horizon") != h:
                raise ValueError(f"{directory}/{name}_h{h}.json is not the walk of {name} at lead {h}")
            check_alignment(name, settings_of(document))
        out[name] = m634.load_laws(directory, name)
    return out


def score_command(args) -> int:
    declared = committed_declaration()
    require_unlocked([LAST_TARGET], where="h9_nested_932")
    m634.SEED = SEED
    draws = args.draws
    rows = load_daily_panel(args.published)
    audit_panel(rows)
    calendar = [row.date for row in rows]
    position = {day: index for index, day in enumerate(calendar)}
    outcomes = {row.date: row.spread_bps for row in rows}
    row_of = {row.date: row for row in rows}
    splits = load_split_declaration(m842.SPLITS)
    registry = json.loads(m842.SOURCES.read_text(encoding="utf-8"))
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
    versus = [(b, n) for n in VARIANTS for b in ("B1", "B2")]
    pairs = list(PRIMARY) + list(SECONDARY) + versus
    document: dict = {
        "declaration": "metadata/h9_nested_932.json",
        "panel_sha256": panel_sha256(args.published),
        "decision_days": {"n": len(days), "first": days[0].isoformat(), "last": days[-1].isoformat()},
        "draws": draws, "seed": SEED, "excluded_day": EXCLUDED_DAY.isoformat(),
        "decision_days_without_a_benchmark": unbuilt, "missing": missing, "names": names,
        "mean_primary": {n: sum(primary[n].values()) / len(days) for n in names},
        "mean_key_secondary": {n: sum(secondary[n].values()) / len(days) for n in names},
        "the_day": {n: primary[n][EXCLUDED_DAY] for n in names if EXCLUDED_DAY in primary[n]},
    }
    recorded = json.loads(m842.RECORDED.read_text(encoding="utf-8"))
    document["reproduction"] = {
        "recorded_gbm_funding_mean_primary": recorded["mean_primary"]["gbm_funding"],
        "recorded_days": recorded["decision_days"]["n"],
        "here_base_mean_primary": sum(base_all.values()) / len(base_all),
        "here_days": len(base_all),
        "base_mean_primary_on_the_common_days": document["mean_primary"]["base"],
    }
    state = m842.as_of_state(args.panel, days)
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
        groups[f"type:{kind}"] = (members, lambda d, hh, kind=kind: kinds[(d, hh)] == kind)
    for h in HORIZONS:
        groups[f"lead:{h}"] = (list(days), lambda d, hh, h=h: hh == h)
    table: Dict[str, dict] = {}
    for label, (members, include) in groups.items():
        means = {n: m634.day_means(cells[n], include) for n in names}
        usable_days = sorted(set(members) & set.intersection(*(set(m) for m in means.values())))
        for suffix, group in (("", usable_days), (" without_2019-09-18", m842.drop_day(usable_days))):
            if suffix and EXCLUDED_DAY not in usable_days:
                continue
            table[label + suffix] = {
                "days": len(group),
                "mean": {n: sum(means[n][d] for d in group) / len(group) for n in names} if group else {},
                "tests": m634.pair_table(means, pairs, group, draws),
            }
    document["table"] = table
    document["table_key_secondary"] = {}
    for label, group in (("pooled", days), ("pooled without_2019-09-18", m842.drop_day(days))):
        document["table_key_secondary"][label] = {
            "days": len(group),
            "mean": {n: sum(secondary[n][d] for d in group) / len(group) for n in names},
            "tests": m634.pair_table(secondary, pairs, group, draws),
        }
    document["holm"] = {}
    for label in ("pooled", "pooled without_2019-09-18"):
        tests = table[label]["tests"]
        keys = [f"{b} -> {v}" for b, v in PRIMARY]
        document["holm"][label] = dict(zip(keys, m842.holm([tests[k]["bootstrap_p"] for k in keys])))
    document["state_counts"] = {band: sum(1 for d in days if state[d] == band) for band in BANDS}
    document["recorded_842"] = recorded_842_figures()
    args.output.write_text(json.dumps(document, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(args.output), "decision_days": len(days)}))
    return 0


def recorded_842_figures() -> dict:
    """#856's recorded pooled figures, to be read beside the aligned ones: `{target: {skill, lower, d}}` and its decision days."""

    recorded = json.loads(RECORDED_842.read_text(encoding="utf-8"))
    out = {"decision_days": recorded["decision_days"]["n"], "targets": {}}
    for t in TARGETS:
        for label in ("pooled", "pooled without_2019-09-18"):
            test = recorded["table"][label]["tests"][f"base -> plus_{t}"]
            out["targets"].setdefault(t, {})[label] = {
                "skill": test["skill"], "mean_difference": test["mean_difference"],
                "lower": test["mean_difference_lower_95_one_sided"],
            }
    return out


# -- the report ------------------------------------------------------------------------------------------------------

fmt, skill_cell, difference_cell, improves = m842.fmt, m842.skill_cell, m842.difference_cell, m842.improves


def readings(document: dict) -> Dict[str, dict]:
    """Per target: does its forecast improve the candidate beyond its interval, on the like-for-like pairing, with and without 2019-09-18?"""

    out = {}
    cells = [k for k in document["table"] if not k.startswith("lead:") and k not in ("pooled", "pooled without_2019-09-18")]
    for target in TARGETS:
        key = f"base_direct -> plus_direct_{target}"
        pooled = document["table"]["pooled"]["tests"][key]
        without = document["table"].get("pooled without_2019-09-18", {}).get("tests", {}).get(key)
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
    pooled, without = table["pooled"], table.get("pooled without_2019-09-18")
    old = document["recorded_842"]
    lines = [
        "# H9 step 3 re-run with aligned training pairs (#932, finding #915)",
        "",
        "A measurement on development data for hypothesis **H9** (the secondary goal), step 3, milestone M4. It is not a record and "
        "**not a verdict**: development data never gives one (`docs/decisions/scoring-protocol.md` §1). Reading H9's kill clause "
        "(\"no nested gain for H5\") is Eleonora's; this page reads none. Nothing is published, no target joins any published "
        "declaration, nothing is written into `docs/runs/`, and no day after 2025-12-31 is read (`docs/decisions/lockbox.md`). "
        "Every choice is in `metadata/h9_nested_932.json`, committed before any score. #842's page "
        "(`docs/pivot/h9-nested-842-result.md`) stands unedited.",
        "",
        "**What changed.** #842's plus walks fitted on one-step pairs: at a lead h >= 2 the model learned the forecast of T for day p + h "
        "against the spread of day p + 1, and was served the forecast for the day it predicts. Here the plus walks, and the `base_direct` "
        "walks they are compared with, are fitted on direct pairs (`training_pairs=\"direct\"`): each label day t is paired with the row "
        "its own forecast reads, whose column is the forecast of T for day t. The candidate, the targets' forecasts, the panel, the days and "
        "the interval are #842's. `base` is #842's candidate on one-step pairs, re-walked.",
        "",
        f"Decision days: {document['decision_days']['n']} ({document['decision_days']['first']} to {document['decision_days']['last']}). "
        f"Intervals: studentized stationary bootstrap, block 10, {document['draws']} draws, seed {document['seed']}, one-sided 95%. "
        "`d = S(base_direct) − S(plus_direct)`; positive favours the target's forecast; skill = mean(d) / mean(S(base_direct)).",
        "",
        "## Nested difference on the primary score (grid CRPS, mean over leads 1 to 5), pairing held fixed",
        "",
        "| target | CRPS base_direct | CRPS with target | d, all days | skill (lower 95%) | Holm p | d, without 2019-09-18 | Holm p, without |",
        "|---|---|---|---|---|---|---|---|",
    ]
    for target in TARGETS:
        key = f"base_direct -> plus_direct_{target}"
        p = pooled["tests"][key]
        w = without["tests"][key] if without else None
        lines.append(
            f"| `{target}` | {fmt(pooled['mean']['base_direct'])} | {fmt(pooled['mean']['plus_direct_' + target])} | {difference_cell(p)} | {skill_cell(p)} "
            f"| {fmt(document['holm']['pooled'][key], 3)} | {difference_cell(w)} | "
            f"{fmt(document['holm']['pooled without_2019-09-18'][key], 3) if without else '-'} |"
        )
    lines += [
        "",
        "## Beside #856's figures (misaligned pairs; its base was the one-step candidate)",
        "",
        f"#856's decision days: {old['decision_days']}. Its figures are read from `docs/pivot/evidence/h9-nested-842/score.json`, "
        "unedited. The last two columns of this page's table are the same comparison as #856's (the one-step base against the plus "
        "walk), now with the plus walk aligned.",
        "",
        "| target | #856: skill (lower), all days | #856: without 2019-09-18 | here, aligned plus vs one-step `base`: skill (lower) | here, vs `base_direct`: skill (lower) |",
        "|---|---|---|---|---|",
    ]
    for target in TARGETS:
        o, ow = old["targets"][target]["pooled"], old["targets"][target]["pooled without_2019-09-18"]
        cross = pooled["tests"][f"base -> plus_direct_{target}"]
        like = pooled["tests"][f"base_direct -> plus_direct_{target}"]
        lines.append(
            f"| `{target}` | {fmt(o['skill'], 3, True)} (lower {fmt(o['lower'], 3, True)}) | {fmt(ow['skill'], 3, True)} (lower {fmt(ow['lower'], 3, True)}) "
            f"| {skill_cell(cross)} | {skill_cell(like)} |"
        )
    pairing = pooled["tests"]["base -> base_direct"]
    lines += [
        "",
        f"The pairing alone, with no input added (`base` against `base_direct`): skill {skill_cell(pairing)}. A gain of an aligned plus walk "
        "over the one-step base is the pairing and the input together; the like-for-like column separates the input.",
        "",
        "## Against the benchmarks (skill over B1 and over B2, lower 95% bound)",
        "",
        "| model | over B1 | over B2 |",
        "|---|---|---|",
    ]
    for n in VARIANTS:
        lines.append(f"| `{n}` | {skill_cell(pooled['tests'].get(f'B1 -> {n}'))} | {skill_cell(pooled['tests'].get(f'B2 -> {n}'))} |")
    lines += ["", "## Nested difference by split, pairing held fixed (d, lower 95% bound; days in brackets)", ""]
    lines += ["| split | " + " | ".join(f"`{t}`" for t in TARGETS) + " |", "|" + "---|" * (len(TARGETS) + 1)]
    for label, entry in table.items():
        if label in ("pooled", "pooled without_2019-09-18"):
            continue
        lines.append(
            f"| {label} ({entry['days']}) | "
            + " | ".join(difference_cell(entry["tests"].get(f"base_direct -> plus_direct_{t}")) for t in TARGETS) + " |"
        )
    key_secondary = document["table_key_secondary"]
    lines += ["", "## Upper-tail twCRPS (weight 1{y > 0 bp}): d, lower 95% bound", "", "| target | all days | without 2019-09-18 |", "|---|---|---|"]
    for t in TARGETS:
        key = f"base_direct -> plus_direct_{t}"
        lines.append(
            f"| `{t}` | {difference_cell(key_secondary['pooled']['tests'].get(key))} | "
            f"{difference_cell(key_secondary['pooled without_2019-09-18']['tests'].get(key))} |"
        )
    reproduction = document["reproduction"]
    lines += [
        "",
        "## Reproduction of the candidate",
        "",
        f"`base` re-walks #634's `gbm_funding`: grid CRPS {fmt(reproduction['here_base_mean_primary'], 4)} on {reproduction['here_days']} days here; "
        f"{fmt(reproduction['recorded_gbm_funding_mean_primary'], 4)} on {reproduction['recorded_days']} days recorded in "
        "`docs/pivot/evidence/spread-distribution-protocol/score.json`. On the days every walk covers the base reads "
        f"{fmt(reproduction['base_mean_primary_on_the_common_days'], 4)}.",
        "",
        "## Readings (development data, not a verdict; reading H9's kill clause is Eleonora's)",
        "",
    ]
    for target in TARGETS:
        r = read[target]
        lines.append(
            f"* `{target}`: on the like-for-like pairing its forecast {'improves' if r['pooled'] else 'does not improve'} the candidate beyond "
            f"its interval (skill {fmt(r['skill'], 3, True)}, lower bound of d {fmt(r['lower'], 3, True)}); without 2019-09-18 it "
            f"{'improves' if r['without'] else 'does not improve'} it. Split cells read: {r['cells_read']}; cells showing a gain: "
            f"{', '.join(r['cells_shown']) if r['cells_shown'] else 'none'}."
        )
    lines.append("")
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
