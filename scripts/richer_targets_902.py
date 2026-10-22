#!/usr/bin/env python3
"""H9 step 2 redone on #941's scaled mean reversion, with and without decision day 2019-09-18 (#902; H9 secondary goal, step 2).

A development study, never a verdict (scoring protocol v1 §1; Eleonora's rulings on #798, 17 October 2026, option (b), and on #902,
22 October 2026). It writes JSON and Markdown to the paths it is given and nothing into `docs/runs/`. Every choice is in
`metadata/richer_targets_902.json`, which `declare` writes before any score and which `walk` and `score` refuse to read unless it is
committed and unchanged.

The model is the H5 candidate of 22 October 2026, `spread_mr_fhs_mad20_f0.5` (`repo_model.spread_mr_fhs`, #941), unchanged, on the
three targets of #706's declaration. `richer_targets.as_target` puts the target in the slot the model reads as SOFR - IORB and
`richer_targets.swap_target_fields` gives it the release lag of its own sources, exactly as #706 did for the gradient-boosted model.
The walks are stdlib arithmetic and take seconds, not hours: no Mac run is needed. Each walk is written in #706's file format, so
#706's scorer runs on it unchanged (`richer_targets_706.score_target`, with two optional arguments added for this study: the day to
drop and further benchmarks).

Benchmarks are #706's own B1 and B2 for the target, and B1' (#960, `repo_model.b1_calendar`, the calendar-aware persistence) read on
the target's series. B1 stays the protocol's benchmark; B1' is a reference row (the queue's standing order of 22 October 2026).
**Provisional under calendar first:** mean reversion and its scaled variants read no calendar column, so no reading of this page
closes a question in either direction (`docs/research/provisional-calendar-register.md`).

    PYTHONPATH=src python3 -m repo_model.cli build --raw-root tests/fixtures/snapshots/funding_inputs --output PUB.csv \\
        --build-cutoff 2026-09-08T21:31:42+00:00 --decision-time 16:00:00
    PYTHONPATH=src python3 scripts/tax_date_market_days.py scripts/pressure_v1_1.py panel --output AUG.csv
    PYTHONPATH=src python3 scripts/tax_date_market_days.py scripts/measurement_fields.py panel --panel AUG.csv --output AUG2.csv
    PYTHONPATH=src python3 scripts/tax_date_market_days.py scripts/satiation_distance_598.py panel --panel AUG2.csv --output AUG2D.csv
    PYTHONPATH=src python3 scripts/richer_targets_639.py panel --panel AUG2D.csv --output H9D.csv      # digest 26c51093...
    PYTHONPATH=src python3 scripts/richer_targets_902.py declare --panel H9D.csv                     # then commit it
    PYTHONPATH=src python3 scripts/richer_targets_902.py walk --panel H9D.csv --output WALKS
    PYTHONPATH=src python3 scripts/richer_targets_902.py score --panel H9D.csv --walks WALKS \\
        --output docs/research/richer-targets-902/result.json
    PYTHONPATH=src python3 scripts/richer_targets_902.py page \\
        --score docs/research/richer-targets-902/result.json --output docs/research/richer-targets-902-result.md
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import sys
from concurrent.futures import ProcessPoolExecutor
from datetime import date
from pathlib import Path
from typing import Dict, List, Mapping, Optional, Sequence

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))


def _load(name: str):
    spec = importlib.util.spec_from_file_location(f"{name}_script", REPO / "scripts" / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[f"{name}_script"] = module
    spec.loader.exec_module(module)
    return module


from repo_model import b1_calendar as b1c, richer_targets, scoring_protocol as sp, spread_mr_fhs as fhs  # noqa: E402
from repo_model.data import load_daily_panel  # noqa: E402
from repo_model.evaluation_splits import load_split_declaration  # noqa: E402
from repo_model.lockbox import require_unlocked  # noqa: E402
from repo_model.splits import SplitError  # noqa: E402

s706 = _load("richer_targets_706")
s639 = s706.s639

DECLARATION = REPO / "metadata" / "richer_targets_902.json"
OLDER = s706.DECLARATION
FHS_DECLARATION = REPO / "metadata" / "fhs_scale_941.json"
B1P_DECLARATION = REPO / "metadata" / "b1_calendar_960.json"
LAST_TARGET = s706.LAST_TARGET
DROPPED_DAY = date(2019, 9, 18)
VARIANT = fhs.VARIANTS[0]
HORIZONS = sp.HORIZONS
BANDS = s706.BANDS
EXTRA = "B1p"
RULINGS = (
    "Eleonora, 22 October 2026 (relayed by the orchestrating session; comment 6350222095 on #902): the H5 candidate is #941's scaled "
    "mean reversion; #902 is redone on it",
    "Eleonora, 17 October 2026, ruling on #798, option (b): report H5's and H9's figures with and without decision day 2019-09-18",
    "Eleonora, 22 October 2026 (relayed; queue issue #46): every new H5 scoring page reports B1' beside B1, pooled, by regime and by "
    "day type; B1 stays the protocol's benchmark",
    "Eleonora, 21 October 2026: #906 (the same cut on the gradient-boosted walks) closed unmerged as provisional under calendar first",
)


def sha256_of(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


# -- the declaration -----------------------------------------------------------------------------------------------


def declaration_document(panel: Path) -> dict:
    """What is fixed before any score. The targets, the panel and the scoring are #706's, read from its committed declaration."""

    older = json.loads(OLDER.read_text(encoding="utf-8"))
    digest = sha256_of(panel)
    if digest != older["panel"]["sha256"]:
        raise SystemExit(f"the panel's digest {digest} is not the one #706 declared, {older['panel']['sha256']}")
    return {
        "status": (
            "declared by the pull request that closes #902 before any score was computed; step 2 of H9, a sensitivity measurement on "
            "development data, not a record and not a verdict (scoring protocol v1 section 1). Nothing is published, no target joins "
            "any published declaration, no day after 2025-12-31 is read (docs/decisions/lockbox.md), no rule changes, the live record "
            "and pin do not move, and no declaration that moves a published figure is edited"
        ),
        "issue": 902,
        "hypothesis": "H9 (secondary goal), step 2 of docs/research/hypotheses/H9.md",
        "rulings": list(RULINGS),
        "panel": {"sha256": digest, "built_by": "the commands of scripts/richer_targets_902.py's docstring, the panel #706 declared"},
        "targets": older["choice"]["chosen"],
        "targets_from": {"path": str(OLDER.relative_to(REPO)), "sha256": sha256_of(OLDER), "rule": "#706's four-part rule, unchanged"},
        "model": {
            "name": VARIANT.name,
            "class": "repo_model.spread_mr_fhs, the variant of metadata/fhs_scale_941.json: scale estimator mad, window 20 rows, floor 0.5",
            "declaration": {"path": str(FHS_DECLARATION.relative_to(REPO)), "sha256": sha256_of(FHS_DECLARATION)},
            "label": "the target, put in the slot the model reads as SOFR - IORB (richer_targets.as_target) under the release lag of the "
                     "target's own sources (richer_targets.swap_target_fields), as #706 did",
            "refit_every": 21,
            "decision_time": "16:00",
            "horizons": list(HORIZONS),
            "inputs": "the target's own history only: no calendar column, no other input (provisional under calendar first)",
            "units": "the scale floor of 0.5 is #941's, written in bp; for on_rrp_change_bn the target is in USD bn and the floor is 0.5 "
                     "bn. Declared as it is, not tuned (a marked question on the pull request)",
        },
        "benchmarks": {
            "B1": "richer_targets.b1_quantiles, #706's, unchanged",
            "B2": "richer_targets.b2_quantiles, #706's, unchanged",
            "B1p": {
                "what": "B1', repo_model.b1_calendar.b1_calendar_forecast (#960), read on the target's series (as_target); a reference row, not a benchmark of the protocol",
                "declaration": {"path": str(B1P_DECLARATION.relative_to(REPO)), "sha256": sha256_of(B1P_DECLARATION)},
                "missing": "a decision day B1' cannot build is left out of every column and listed",
            },
            "missing_forecast": "a lead the model has no law for is filled by B1 (scoring_protocol.fill_missing)",
        },
        "scoring": {
            "scorer": "scripts/richer_targets_706.py score_target, unchanged in what it computes (two optional arguments added: the day to drop, further benchmarks)",
            "score": "scoring_protocol.grid_crps on the 23 levels, the mean over leads 1 to 5 per decision day",
            "interval": f"scoring_protocol.paired_tests through spread_distribution_634.pair_table: stationary bootstrap, mean block {sp.BLOCK_LENGTH}, "
                        f"{sp.DRAWS} draws, seed {s706.m634.SEED}, one-sided 95% (the lower bound of the two-sided 90% interval); "
                        f"the pre-onset AUC resamples onsets, {s706.ONSET_DRAWS} draws, seed {s706.SEED}. Both are #706's",
            "splits": {
                "state": "the as-of scarcity state of the decision day: ample or scarce",
                "day_type": "SplitDeclaration.reporting_day_type of the target day",
            },
            "last_target_day": LAST_TARGET.isoformat(),
        },
        "dropped_day": DROPPED_DAY.isoformat(),
        "dropped_day_reading": (
            "a decision day, as in #805 (scripts/h5_splits_805.py EXCLUDED_DAY): left out of every cut after the benchmarks are built; "
            "in the pre-onset AUC the day whose decision day it is is the lead-1 target of the next row"
        ),
        "with_column": (
            "the scorer run on the same walks with nothing dropped. `score` also runs the scorer with no extra benchmark and refuses "
            "unless the B1, B2 and model columns of that run are the 'with' column's, so the added benchmark and argument change no figure"
        ),
        "reading": {
            "sign_change": "a cell whose one-sided 95% lower bound of the skill over a benchmark changes sign when the day is dropped, listed one per line",
            "kill_criterion": (
                "any reading against H9's kill criterion (docs/research/hypotheses/H9.md) is a marked question for Eleonora, not a "
                "statement of the page. The model reads no calendar column, so the result is provisional and closes no question"
            ),
        },
    }


def declare_command(args) -> int:
    document = declaration_document(args.panel)
    args.output.write_text(json.dumps(document, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"written": str(args.output), "targets": document["targets"]}))
    return 0


def committed_declaration(path: Path = DECLARATION) -> dict:
    """The declaration, refused unless it is committed and unchanged since `HEAD`."""

    return s706.committed_declaration(path)


def check_inputs(declared: Mapping[str, object], panel_digest: str) -> None:
    """Refuse a panel other than the declared one."""

    if panel_digest != declared["panel"]["sha256"]:
        raise SystemExit(f"the panel's digest {panel_digest} is not the declared {declared['panel']['sha256']}")


def refuse_locked(days: Sequence[date]) -> None:
    """Refuse a run that would read or score a day of a locked tier (`docs/decisions/lockbox.md`): raises `LookAheadError`."""

    require_unlocked(list(days), where="richer_targets_902")


def require_dropped_day(days: Sequence[date], day: date) -> None:
    """The day to drop must be one of the scored decision days, or the 'without' column is the 'with' column under another name."""

    if day not in days:
        raise ValueError(f"{day} is not a scored decision day, so dropping it changes nothing")


# -- the walks -----------------------------------------------------------------------------------------------------


def laws_by_target(
    forecasts: Mapping[date, Mapping[int, Sequence[float]]], calendar: Sequence[date], h: int
) -> Dict[date, List[float]]:
    """A walk's lead-`h` forecasts as #706's walk file holds them: the law of each target day, from the decision `h` rows before it."""

    position = {day: index for index, day in enumerate(calendar)}
    out: Dict[date, List[float]] = {}
    for decision, leads in forecasts.items():
        if decision not in position:
            raise ValueError(f"decision day {decision} is not on the calendar")
        out[calendar[position[decision] + h]] = [float(v) for v in leads[h]]
    return out


def walk_target(target: str, panel: Path, registry, splits):
    """The scaled mean-reversion walk of one target: (the target's rows as the model reads them, the walk).

    Must be called with `s639.switched()` and `richer_targets.swap_target_fields(target)` in force; the rows are the target in the
    slot of SOFR - IORB.
    """

    rows = s706.panel_rows(panel, target)
    swapped = richer_targets.as_target(rows, target)
    days = [
        row.date
        for i, row in enumerate(swapped)
        if i + max(HORIZONS) < len(swapped) and swapped[i + max(HORIZONS)].date <= LAST_TARGET
    ]
    walk = fhs.walk(swapped, days, [VARIANT], registry=registry, decision_time=s706.DECISION, splits=splits)
    return rows, swapped, days, walk


def walk_command(args) -> int:
    declared = committed_declaration()
    refuse_locked([LAST_TARGET])
    digest = sha256_of(args.panel)
    check_inputs(declared, digest)
    registry = s639.measurement_fields.load_registry()
    splits = load_split_declaration(s706.SPLITS)
    args.output.mkdir(parents=True, exist_ok=True)
    summary = {}
    for target in declared["targets"]:
        with s639.switched(), richer_targets.swap_target_fields(target):
            rows, swapped, days, walk = walk_target(target, args.panel, registry, splits)
        calendar = [row.date for row in swapped]
        position = {day: i for i, day in enumerate(calendar)}
        refuse_locked(days + [calendar[position[d] + h] for d in days for h in HORIZONS])
        forecasts = walk.forecasts[VARIANT.name]
        for h in HORIZONS:
            document = {
                "target": target,
                "horizon": h,
                "model": VARIANT.name,
                "panel_sha256": digest,
                "declaration_sha256": sha256_of(DECLARATION),
                "laws": {d.isoformat(): q for d, q in sorted(laws_by_target(forecasts, calendar, h).items())},
            }
            (args.output / f"{target}_h{h}.json").write_text(json.dumps(document, sort_keys=True) + "\n", encoding="utf-8")
        summary[target] = {"decision_days_offered": len(days), "scored": len(forecasts), "skipped_for_history": len(walk.skipped)}
    print(json.dumps(summary))
    return 0


# -- scoring -------------------------------------------------------------------------------------------------------


def benchmark_b1_prime(target: str, rows, registry, splits, days: Sequence[date]):
    """B1' for each of `days` on the target's series: day -> lead -> 23 quantiles, and the days it cannot be built for.

    Call with `s639.switched()` and `richer_targets.swap_target_fields(target)` in force.
    """

    swapped = richer_targets.as_target(rows, target)
    position = {row.date: i for i, row in enumerate(swapped)}
    built: Dict[date, Dict[int, List[float]]] = {}
    unbuilt: List[str] = []
    for day in days:
        try:
            built[day] = b1c.b1_calendar_forecast(
                swapped, position[day], registry=registry, decision_time=s706.DECISION, splits=splits
            )
        except (sp.ProtocolError, SplitError):
            unbuilt.append(day.isoformat())
    return built, unbuilt


def score_one(target: str, args, declared, all_rows, splits, registry) -> dict:
    """One target's 'with' and 'without' scores, the unchanged scorer's own run beside them, and the day's own scores."""

    rows = s706.panel_rows(args.panel, target)
    calendar = [row.date for row in rows]
    laws = s706.load_laws(args.walks, target)
    _by_decision, decision_days = s706.m634.lead_forecasts(laws, calendar)
    require_dropped_day(decision_days, DROPPED_DAY)
    with s639.switched(), richer_targets.swap_target_fields(target):
        refuse_locked(decision_days)
        extra, unbuilt = benchmark_b1_prime(target, rows, registry, splits, decision_days)
    plain = s706.score_target(target, args, declared, all_rows, splits, registry)
    with_day = s706.score_target(target, args, declared, all_rows, splits, registry, extras={EXTRA: extra})
    without = s706.score_target(target, args, declared, all_rows, splits, registry, drop=DROPPED_DAY, extras={EXTRA: extra})
    if with_day["decision_days"] == plain["decision_days"]:
        for key in ("B1 -> model", "B2 -> model", "B2 -> B1"):
            if with_day["pooled"].get(key) != plain["pooled"].get(key):
                raise SystemExit(f"{target}: the 'with' column's {key} is not the unchanged scorer's; nothing written")
    return {
        "with": with_day,
        "without": without,
        "scorer_without_extra_benchmark": {"decision_days": plain["decision_days"], "pooled": plain["pooled"]},
        "b1_prime_unbuilt_days": unbuilt,
        "the_day": the_day(target, args, laws, calendar, extra),
    }


def score_command(args) -> int:
    declared = committed_declaration()
    refuse_locked([LAST_TARGET])
    digest = sha256_of(args.panel)
    check_inputs(declared, digest)
    all_rows = [row for row in load_daily_panel(args.panel) if row.date <= LAST_TARGET]
    splits = load_split_declaration(s706.SPLITS)
    registry = s639.measurement_fields.load_registry()
    with ProcessPoolExecutor(max_workers=max(1, min(args.workers, len(declared["targets"])))) as pool:
        jobs = [pool.submit(score_one, target, args, declared, all_rows, splits, registry) for target in declared["targets"]]
        results = {target: job.result() for target, job in zip(declared["targets"], jobs)}
    document = {
        "issue": 902,
        "label": "development data, not a verdict",
        "provisional": "the model reads no calendar column (calendar first): provisional, closes no question",
        "declaration": str(DECLARATION.relative_to(REPO)),
        "declaration_sha256": sha256_of(DECLARATION),
        "panel_sha256": digest,
        "draws": args.draws,
        "seed": s706.m634.SEED,
        "model": VARIANT.name,
        "dropped_day": DROPPED_DAY.isoformat(),
        "targets": results,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(document, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(args.output), "targets": list(results)}))
    return 0


def the_day(target, args, laws, calendar, extra) -> dict:
    """The decision day's own scores: the figures the 'with' column carries that the 'without' column does not."""

    rows = s706.panel_rows(args.panel, target)
    position = {d: i for i, d in enumerate(calendar)}
    outcomes = {row.date: float(row.values[target]) for row in rows}
    by_decision, _days = s706.m634.lead_forecasts(laws, calendar)
    scores = {"model": sp.day_scores({DROPPED_DAY: by_decision[DROPPED_DAY]}, outcomes, calendar)[DROPPED_DAY]}
    if DROPPED_DAY in extra:
        scores[EXTRA] = sp.day_scores({DROPPED_DAY: extra[DROPPED_DAY]}, outcomes, calendar)[DROPPED_DAY]
    return {"decision_day": DROPPED_DAY.isoformat(), "grid_crps": scores, "row": position[DROPPED_DAY]}


# -- the page ------------------------------------------------------------------------------------------------------

BENCHMARKS = (("B1", "B1"), ("B2", "B2"), (EXTRA, "B1'"))


def _lower(test: Optional[dict]) -> Optional[float]:
    return None if not test else test["skill_lower_95_one_sided"]


def _cuts(result: Mapping) -> Dict[str, Mapping]:
    cuts = {"pooled": result["pooled"]}
    cuts.update({f"lead {h}": result["by_lead"][str(h)]["tests"] for h in HORIZONS})
    cuts.update({f"state {band}": entry["tests"] for band, entry in result["by_state"].items()})
    cuts.update({f"day type {kind}": entry["tests"] for kind, entry in result["by_day_type"].items()})
    return cuts


def sign_changes(document: Mapping) -> List[str]:
    """Every skill cell whose lower 95% bound changes sign when the day is dropped, one line each."""

    out = []
    for target, pair in document["targets"].items():
        with_cuts, without_cuts = _cuts(pair["with"]), _cuts(pair["without"])
        for label in with_cuts:
            if label not in without_cuts:
                continue
            for key, name in BENCHMARKS:
                a = _lower(with_cuts[label].get(f"{key} -> model"))
                b = _lower(without_cuts[label].get(f"{key} -> model"))
                if a is not None and b is not None and (a > 0.0) != (b > 0.0):
                    out.append(
                        f"`{target}`, {label}, over {name}: lower bound {s706.fmt(a, 3, True)} with the day, {s706.fmt(b, 3, True)} without"
                    )
    return out


def _both(entry_with: Optional[dict], entry_without: Optional[dict], key: str) -> List[str]:
    return [s706.skill_cell(e["tests"].get(key)) if e else "-" for e in (entry_with, entry_without)]


def page_markdown(document: Mapping) -> str:
    day = document["dropped_day"]
    lines = [f"# H9 step 2 on #941's scaled mean reversion, with and without decision day {day} (#902)", ""]
    lines += [
        "**Hypothesis and step:** H9 (secondary goal), step 2. **This page is development data, not a verdict** (scoring protocol v1 §1). "
        f"Panel `{document['panel_sha256'][:8]}…`, declared in `{document['declaration']}` before any score.",
        "",
        f"**Provisional.** The model is `{document['model']}`, the H5 candidate of 22 October 2026, fitted on each target's own history. "
        "It reads no calendar column, so under calendar first (`docs/research/provisional-calendar-register.md`) this page closes no "
        "question in either direction.",
        "",
        "Cells are skill over the benchmark, `mean(S(benchmark) − S(model)) / mean(S(benchmark))`, with the one-sided 95% lower bound "
        "(the lower end of the two-sided 90% interval) in brackets; positive favours the model. B1' is #960's calendar-aware persistence, "
        "a reference row beside B1, which stays the protocol's benchmark. 'With' is every scored decision day; "
        f"'without' leaves out decision day {day} from every cut (#798, Eleonora's ruling, option (b)).",
        "",
    ]
    for key, name in BENCHMARKS:
        lines += [f"## Pooled, skill over {name}", "", "| target | days with / without | with | without |", "|---|---|---|---|"]
        for target, pair in document["targets"].items():
            w, wo = pair["with"], pair["without"]
            a, b = (s706.skill_cell(r["pooled"].get(f"{key} -> model")) for r in (w, wo))
            lines.append(f"| `{target}` | {w['decision_days']['n']} / {wo['decision_days']['n']} | {a} | {b} |")
        lines.append("")
    for key, name in BENCHMARKS:
        lines += [f"## By as-of scarcity state, skill over {name}", "", "| target | state | days with / without | with | without |", "|---|---|---|---|---|"]
        for target, pair in document["targets"].items():
            for band in s706.BANDS:
                w, wo = pair["with"]["by_state"].get(band), pair["without"]["by_state"].get(band)
                a, b = _both(w, wo, f"{key} -> model")
                lines.append(f"| `{target}` | {band} | {w['n'] if w else '-'} / {wo['n'] if wo else '-'} | {a} | {b} |")
        lines.append("")
    for key, name in BENCHMARKS:
        lines += [f"## By day type of the target day, skill over {name}", "", "| target | day type | decision days with / without | with | without |", "|---|---|---|---|---|"]
        for target, pair in document["targets"].items():
            kinds = sorted(set(pair["with"]["by_day_type"]) | set(pair["without"]["by_day_type"]))
            for kind in kinds:
                w, wo = pair["with"]["by_day_type"].get(kind), pair["without"]["by_day_type"].get(kind)
                a, b = _both(w, wo, f"{key} -> model")
                lines.append(
                    f"| `{target}` | {kind} | {w['decision_days'] if w else '-'} / {wo['decision_days'] if wo else '-'} | {a} | {b} |"
                )
        lines.append("")
    lines += ["## Pre-onset AUC at lead 1 within the as-of state (90% interval)", "",
              "The AUC of the model's lead-1 median on the 1 to 5 panel days before each +5 bp onset against every other scored day of the state, "
              "and of the target's as-of value beside it.", "",
              "| target | series | state | onsets with / without | with | without |", "|---|---|---|---|---|---|"]
    cell = lambda c: "-" if "auc" not in c else f"{s706.fmt(c['auc'])} [{s706.fmt(c.get('auc_low'))}, {s706.fmt(c.get('auc_high'))}]"
    for target, pair in document["targets"].items():
        for series in ("model_median", "as_of_value"):
            for band in s706.BANDS:
                w = pair["with"]["lead_on_onsets"]["cells"][series][band]
                wo = pair["without"]["lead_on_onsets"]["cells"][series][band]
                lines.append(f"| `{target}` | {series} | {band} | {w['onsets']} / {wo['onsets']} | {cell(w)} | {cell(wo)} |")
    lines += ["", f"## The day, {day}", "", "| target | grid CRPS of the model | grid CRPS of B1' | mean of the model over all days |", "|---|---|---|---|"]
    for target, pair in document["targets"].items():
        scores = pair["the_day"]["grid_crps"]
        lines.append(
            f"| `{target}` | {s706.fmt(scores.get('model'))} | {s706.fmt(scores.get(EXTRA))} | {s706.fmt(pair['with']['mean']['model'])} |"
        )
    lines += ["", "## Interval bounds that change sign", ""]
    changes = sign_changes(document)
    lines += [f"* {c}" for c in changes] if changes else ["None: no lower bound changes sign when the day is dropped."]
    lines += ["", "## What this does not show", "",
              "* It is not a reading against H9's kill criterion; that reading is a question for Eleonora (see the pull request).",
              "* The model is calendar-blind and the scale floor of 0.5 is #941's bp figure, kept as declared for `on_rrp_change_bn` (USD bn).",
              "* It uses development days only and no locked day.", ""]
    return "\n".join(lines)


def page_command(args) -> int:
    committed_declaration()
    document = json.loads(args.score.read_text(encoding="utf-8"))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(page_markdown(document) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(args.output)}))
    return 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    commands = parser.add_subparsers(dest="command", required=True)
    declare = commands.add_parser("declare", help="write the declaration, before any score")
    declare.add_argument("--panel", type=Path, required=True)
    declare.add_argument("--output", type=Path, default=DECLARATION)
    declare.set_defaults(handler=declare_command)
    walk = commands.add_parser("walk", help="the walks of every declared target, five leads each, in #706's file format")
    walk.add_argument("--panel", type=Path, required=True)
    walk.add_argument("--output", type=Path, required=True)
    walk.set_defaults(handler=walk_command)
    score = commands.add_parser("score", help="score the walks with and without the day")
    score.add_argument("--panel", type=Path, required=True)
    score.add_argument("--walks", type=Path, required=True)
    score.add_argument("--output", type=Path, required=True)
    score.add_argument("--draws", type=int, default=sp.DRAWS)
    score.add_argument("--workers", type=int, default=3, help="targets scored in parallel (each is independent)")
    score.set_defaults(handler=score_command)
    page = commands.add_parser("page", help="the tables")
    page.add_argument("--score", type=Path, required=True)
    page.add_argument("--output", type=Path, required=True)
    page.set_defaults(handler=page_command)
    args = parser.parse_args(argv)
    return args.handler(args)


if __name__ == "__main__":
    sys.exit(main())
