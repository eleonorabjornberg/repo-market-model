#!/usr/bin/env python3
"""H9 step 2, B1 with h-row and with h + 1-row changes on the richer targets (#850; finding #744, remainder).

A scratch measurement on development data, not a record and not a verdict (scoring protocol v1, `docs/decisions/scoring-protocol.md`
§1). It writes JSON and Markdown to the paths it is given and nothing into `docs/runs/`. Every choice is in
`metadata/b1_alignment_850.json`, which `declare` writes before any score and which `run` refuses to read unless it is committed and
unchanged. No day after 2025-12-31 is read (`docs/decisions/lockbox.md`; `require_unlocked`), and nothing changes in
`richer_targets.b1_quantiles`, the protocol's benchmarks or any published figure.

    # the panel is step 1's: the commands of scripts/source_screen.py's docstring (PUB.csv, AUG2.csv, EW.csv), then
    PYTHONPATH=src python3 scripts/richer_targets_639.py panel --panel AUG2.csv --extra EW.csv --output H9.csv
    PYTHONPATH=src python3 scripts/b1_alignment_850.py declare --panel H9.csv
    git add metadata/b1_alignment_850.json && git commit          # a declaration is made before any score
    PYTHONPATH=src python3 scripts/b1_alignment_850.py run --panel H9.csv --output OUT/alignment.json
    PYTHONPATH=src python3 scripts/b1_alignment_850.py report OUT/alignment.json --output OUT/tables.md

* **Arms.** B1 at lead h as `richer_targets.b1_quantiles` has it (the last public value plus the empirical distribution of the h-row
  changes over the trailing two years: arm `h`), and the same with h + 1-row changes (arm `h1`), at every lead 1 to 10. The window, the
  anchor, the minimum number of changes and the look-ahead guard are the shipped function's. A day on which either arm, B2 or the outcome
  is missing is dropped for both arms.
* **Scores.** The central-90% coverage (the outcome between the forecast's 0.05 and 0.95 quantiles, both included) and the protocol's grid
  CRPS, per arm, and B2's CRPS (the calendar climatology, `richer_targets.b2_quantiles`).
* **Intervals.** Two-sided 90% intervals from the stationary bootstrap, mean block 10 (`metrics.stationary_bootstrap_interval`), with the
  same resamples for every statistic of a cell.
* **Ranking.** `B1` when its mean CRPS is below B2's, `B2` when it is above. A flip is a cell where the two arms rank differently.
* **Splits.** All scored days; the as-of scarcity state at the same lead (ample 0 and 1, scarce 2 and 3); the reporting day type.
* **Control.** On the days step 1 scored (arm `h` and B2 only), arm `h` reproduces `docs/pivot/evidence/richer-targets-639/screen.json`.
* **Gap.** The share of scored days on which the as-of anchor is h, h + 1 or another number of panel days before the scored day.

Stdlib only.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import math
import multiprocessing
import sys
from datetime import date
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Tuple

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))

from repo_model import measurement_fields, richer_targets  # noqa: E402
from repo_model.asof import fold_grid  # noqa: E402
from repo_model.data import load_daily_panel  # noqa: E402
from repo_model.evaluation_splits import load_split_declaration  # noqa: E402
from repo_model.lockbox import require_unlocked  # noqa: E402
from repo_model.metrics import stationary_bootstrap_interval  # noqa: E402
from repo_model.scoring_protocol import BLOCK_LENGTH, GRID  # noqa: E402

# Lockbox classification (#1058): tests/test_lockbox.py reads these literals from this file's syntax tree.
LOCKBOX_READS = {
    "run_command": (
        "not_entry",
        "the B1 alignment measurement on step 1's panel (#850): walks the lead-1 fold grid, calls "
        "lockbox.require_unlocked on every scored day before it reads one, refuses a panel past "
        "2025-12-31 and fits and selects nothing",
    ),
}

DECLARATION = REPO / "metadata" / "b1_alignment_850.json"
SCREEN = REPO / "docs" / "pivot" / "evidence" / "richer-targets-639" / "screen.json"
SEED = 850
DRAWS = 2000
LEADS = tuple(range(1, 11))
LOW, HIGH = GRID.index(0.05), GRID.index(0.95)


def _load(name: str):
    spec = importlib.util.spec_from_file_location(f"{name}_script", REPO / "scripts" / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[f"{name}_script"] = module
    spec.loader.exec_module(module)
    return module


s639 = _load("richer_targets_639")
rds = s639.rds
BANDS = s639.BANDS
DAY_TYPES = s639.DAY_TYPES
FIRST_DAY = s639.FIRST_DAY
LAST_DAY = s639.LAST_DAY
DECISION_TIME = s639.DECISION_TIME
MINIMUM_HISTORY = s639.MINIMUM_HISTORY
MINIMUM_DAYS = s639.MINIMUM_DAYS
SCARCITY = s639.SCARCITY


# -- the pieces ----------------------------------------------------------------------------------------------------


def b1_arms(
    values: Sequence[Optional[float]], dates: Sequence[date], anchor: int, lead: int, *, first: int
) -> Optional[Tuple[List[float], List[float]]]:
    """B1 at `lead` with `lead`-row changes and with `lead + 1`-row changes, or `None` if either cannot be formed."""

    shipped = richer_targets.b1_quantiles(values, dates, anchor, lead, first=first)
    longer = richer_targets.b1_quantiles(values, dates, anchor, lead + 1, first=first)
    if shipped is None or longer is None:
        return None
    return shipped, longer


def covered(quantiles: Sequence[float], observed: float) -> bool:
    """The outcome lies in the forecast's central 90% interval, between its 0.05 and 0.95 quantiles, both included."""

    return quantiles[LOW] <= observed <= quantiles[HIGH]


def ranking(b1: float, b2: float) -> str:
    """`B1` when persistence scores lower (better) than the climatology, `B2` when higher, `tie` when equal."""

    if b1 < b2:
        return "B1"
    if b1 > b2:
        return "B2"
    return "tie"


def _mean(values: Sequence[float]) -> float:
    return sum(values) / len(values)


def _interval(statistic, n: int, seed: int, draws: int) -> Tuple[float, float]:
    return stationary_bootstrap_interval(statistic, n, block_length=BLOCK_LENGTH, seed=seed, replications=draws, level=0.90)


def _pick_mean(values: Sequence[float]):
    return lambda idx: sum(values[i] for i in idx) / len(idx)


def arm_cell(
    *,
    crps_h: Sequence[float],
    crps_h1: Sequence[float],
    crps_b2: Sequence[float],
    covered_h: Sequence[bool],
    covered_h1: Sequence[bool],
    days: Sequence[date],
    seed: int,
    draws: int = DRAWS,
) -> dict:
    """Both arms' coverage and CRPS, B2's CRPS and the two rankings, with 90% intervals on the same resamples.

    `skill_*` is `mean(S(B2) - S(B1)) / mean(S(B2))`: positive when persistence beats the climatology.
    """

    n = len(days)
    cov_h = [1.0 if flag else 0.0 for flag in covered_h]
    cov_h1 = [1.0 if flag else 0.0 for flag in covered_h1]
    m = {
        "crps_h": _mean(crps_h),
        "crps_h1": _mean(crps_h1),
        "crps_b2": _mean(crps_b2),
        "coverage_h": _mean(cov_h),
        "coverage_h1": _mean(cov_h1),
    }
    cell = {"n": n, **m}
    cell["rank_h"] = ranking(m["crps_h"], m["crps_b2"])
    cell["rank_h1"] = ranking(m["crps_h1"], m["crps_b2"])
    cell["flip"] = cell["rank_h"] != cell["rank_h1"]
    cell["crps_change"] = (m["crps_h1"] - m["crps_h"]) / m["crps_h"] if m["crps_h"] else None
    if n < MINIMUM_DAYS:
        return cell
    series = {"coverage_h": cov_h, "coverage_h1": cov_h1, "crps_h": crps_h, "crps_h1": crps_h1, "crps_b2": crps_b2}
    for name, values in series.items():
        cell[f"{name}_ci"] = list(_interval(_pick_mean(values), n, seed, draws))
    diff = [b - a for a, b in zip(crps_h, crps_h1)]
    cell["crps_h1_minus_h_ci"] = list(_interval(_pick_mean(diff), n, seed, draws))

    def skill(values):
        def stat(idx):
            b2 = sum(crps_b2[i] for i in idx)
            return (b2 - sum(values[i] for i in idx)) / b2

        return stat

    cell["skill_h"] = (m["crps_b2"] - m["crps_h"]) / m["crps_b2"]
    cell["skill_h1"] = (m["crps_b2"] - m["crps_h1"]) / m["crps_b2"]
    cell["skill_h_ci"] = list(_interval(skill(crps_h), n, seed, draws))
    cell["skill_h1_ci"] = list(_interval(skill(crps_h1), n, seed, draws))
    return cell


# -- the declaration -----------------------------------------------------------------------------------------------


def declaration_document(panel: Path) -> dict:
    """What is fixed before any score."""

    return {
        "status": (
            "declared by the pull request that closes #850 before any score; step 2 of H9, a measurement on development data, not a "
            "record and not a verdict (scoring protocol v1 section 1). Nothing is published: richer_targets.b1_quantiles, the protocol's "
            "benchmarks and every published figure are unchanged, no day after 2025-12-31 is read (docs/decisions/lockbox.md) and no "
            "hindsight regime label is used (ruling on #515). None of the intervals is corrected for multiplicity"
        ),
        "issue": 850,
        "hypothesis": "H9 (secondary goal), step 2 of docs/research/hypotheses/H9.md",
        "finding": 744,
        "panel": {
            "sha256": hashlib.sha256(panel.read_bytes()).hexdigest(),
            "built_by": "scripts/richer_targets_639.py panel over measurement_fields.py's scratch panel and early_warning_inputs.py's "
                        "(the panel of step 1, metadata/richer_targets_639.json)",
        },
        "targets": [target._asdict() for target in richer_targets.TARGETS],
        "leads": list(LEADS),
        "days": "the scored days of the lead-1 fold grid, 2018-06-29 to 2025-12-31, the same days at every lead",
        "arms": {
            "h": "richer_targets.b1_quantiles at lead h: the last public value plus the empirical distribution of the h-row changes over "
                 "the trailing two years",
            "h1": "the same function called with h + 1: the (h + 1)-row changes over the same window and the same anchor",
            "dropped": "a day on which either arm, B2 or the outcome is missing is dropped for both arms",
        },
        "benchmark_b2": "richer_targets.b2_quantiles: the trailing year's values on days of the scored day's reporting day type",
        "metrics": {
            "coverage": "share of days on which the outcome lies between the forecast's 0.05 and 0.95 quantiles, both included",
            "crps": "scoring_protocol.grid_crps on the protocol's 23 quantile levels, mean over days, in the target's unit",
            "ranking": "B1 if its mean CRPS is below B2's, B2 if above; a flip is a cell where the two arms rank differently",
            "skill": "mean(S(B2) - S(B1)) / mean(S(B2))",
        },
        "interval": f"metrics.stationary_bootstrap_interval, mean block {BLOCK_LENGTH}, {DRAWS} resamples, seed {SEED}, two-sided 90%; "
                    "the same resamples for every statistic of a cell",
        "splits": {
            "regime": "the as-of scarcity state at the same lead: ample (0, 1), scarce (2, 3)",
            "day_type": "SplitDeclaration.reporting_day_type of the scored day",
            "minimum_days": MINIMUM_DAYS,
        },
        "control": "on step 1's day set (arm h and B2 only) arm h reproduces docs/pivot/evidence/richer-targets-639/screen.json at its leads",
        "gap": "the share of scored days on which the as-of anchor is h, h + 1 or another number of panel days before the scored day",
        "not_run": "no model, no change to any benchmark, no ruling; a flip is a marked question for Eleonora",
    }


def declare_command(args) -> int:
    document = declaration_document(args.panel)
    args.output.write_text(json.dumps(document, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"written": str(args.output), "panel_sha256": document["panel"]["sha256"]}, indent=1))
    return 0


# -- the run -------------------------------------------------------------------------------------------------------


def _score_target(job) -> dict:
    """One target at every lead and split (a worker of `run`)."""

    target, lead_data, scored_days, kinds_of_scored, values, dates, rows_kinds, scored_idx, window = job
    out = {}
    for lead, reads, regime in lead_data:
        keep = {k: [] for k in ("day", "h", "h1", "b2", "ch", "ch1", "regime", "kind")}
        screen_b1, screen_b2, gaps = [], [], {"h": 0, "h1": 0, "other": 0}
        for i, t in enumerate(scored_idx):
            y = values[t]
            r = reads[i]
            if y is None or values[r] is None:
                continue
            gap = t - r
            gaps["h" if gap == lead else "h1" if gap == lead + 1 else "other"] += 1
            q2 = richer_targets.b2_quantiles(values, rows_kinds, dates, r, kinds_of_scored[i], first=window["b2"][lead][i])
            q1 = richer_targets.b1_quantiles(values, dates, r, lead, first=window["b1"][lead][i])
            if q1 is not None and q2 is not None:
                screen_b1.append(richer_targets.crps(q1, y))
                screen_b2.append(richer_targets.crps(q2, y))
            arms = b1_arms(values, dates, r, lead, first=window["b1"][lead][i])
            if arms is None or q2 is None:
                continue
            keep["day"].append(scored_days[i])
            keep["h"].append(richer_targets.crps(arms[0], y))
            keep["h1"].append(richer_targets.crps(arms[1], y))
            keep["b2"].append(richer_targets.crps(q2, y))
            keep["ch"].append(covered(arms[0], y))
            keep["ch1"].append(covered(arms[1], y))
            keep["regime"].append(regime[i])
            keep["kind"].append(kinds_of_scored[i])
        n = len(keep["day"])
        splits = {"all": list(range(n))}
        for name in BANDS:
            splits[f"regime:{name}"] = [k for k in range(n) if keep["regime"][k] == name]
        for name in DAY_TYPES:
            splits[f"daytype:{name}"] = [k for k in range(n) if keep["kind"][k] == name]
        cells = {}
        for split, idx in splits.items():
            if not idx:
                continue
            cells[split] = arm_cell(
                crps_h=[keep["h"][k] for k in idx],
                crps_h1=[keep["h1"][k] for k in idx],
                crps_b2=[keep["b2"][k] for k in idx],
                covered_h=[keep["ch"][k] for k in idx],
                covered_h1=[keep["ch1"][k] for k in idx],
                days=[keep["day"][k] for k in idx],
                seed=SEED,
            )
        out[str(lead)] = {
            "cells": cells,
            "control": {"n": len(screen_b1), "b1": _mean(screen_b1) if screen_b1 else None,
                        "b2": _mean(screen_b2) if screen_b2 else None},
            "gap_days": gaps,
        }
    return {"target": target, "leads": out}


def run_command(args) -> int:
    declared = rds.committed_declaration(DECLARATION)
    panel_sha = hashlib.sha256(args.panel.read_bytes()).hexdigest()
    if panel_sha != declared["panel"]["sha256"]:
        raise SystemExit(f"the panel's digest {panel_sha} is not the declared {declared['panel']['sha256']}")
    rows = load_daily_panel(args.panel)
    if rows[-1].date > LAST_DAY:
        raise SystemExit(f"the panel runs past {LAST_DAY}; a measurement reads no day in a locked tier")
    registry = measurement_fields.load_registry()
    splits = load_split_declaration(s639.SPLITS)
    dates = [row.date for row in rows]
    leads = tuple(declared["leads"])
    columns = [t["column"] for t in declared["targets"]]
    with s639.switched():
        grid = [
            i
            for i in fold_grid(dates, registry, decision_time=DECISION_TIME, minimum_history=MINIMUM_HISTORY, horizon=1)
            if FIRST_DAY <= dates[i] <= LAST_DAY
        ]
        require_unlocked((dates[i] for i in grid), where="b1_alignment_850")
        reads = richer_targets.as_of_rows(rows, registry, columns + [SCARCITY], leads=leads, scored=grid, decision_time=DECISION_TIME)
    scored_days = [dates[i] for i in grid]
    rows_kinds = [splits.reporting_day_type(r.date, r.values) for r in rows]
    kinds_of_scored = [rows_kinds[i] for i in grid]
    series = {c: [None if r.values.get(c) is None else float(r.values[c]) for r in rows] for c in columns}
    window = {
        "b1": {lead: [richer_targets.window_first(dates, t - lead, 2) for t in grid] for lead in leads},
        "b2": {lead: [richer_targets.window_first(dates, t - lead, 1) for t in grid] for lead in leads},
    }
    state = {lead: [rows[r].values.get(SCARCITY) for r in reads[lead][SCARCITY]] for lead in leads}
    regime = {lead: [s639.band(s) for s in state[lead]] for lead in leads}
    jobs = [
        (column, [(lead, reads[lead][column], regime[lead]) for lead in leads], scored_days, kinds_of_scored,
         series[column], dates, rows_kinds, grid, window)
        for column in columns
    ]
    with multiprocessing.Pool(min(len(jobs), args.workers)) as pool:
        results = {r["target"]: r["leads"] for r in pool.map(_score_target, jobs)}
    result = {
        "scope": {
            "first_day": scored_days[0].isoformat(),
            "last_day": scored_days[-1].isoformat(),
            "scored_days": len(grid),
            "leads": list(leads),
            "panel_sha256": panel_sha,
            "declaration_sha256": hashlib.sha256(DECLARATION.read_bytes()).hexdigest(),
        },
        "targets": declared["targets"],
        "cells": results,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result["scope"], indent=1))
    return 0


# -- the report ----------------------------------------------------------------------------------------------------


def _fmt(value, digits=3, signed=False) -> str:
    if value is None or (isinstance(value, float) and math.isnan(value)):
        return "-"
    return f"{value:+.{digits}f}" if signed else f"{value:.{digits}f}"


def _ci(cell: dict, key: str, digits=3, signed=False, scale=1.0) -> str:
    interval = cell.get(f"{key}_ci")
    value = cell.get(key)
    if interval is None or value is None:
        return _fmt(None if value is None else value * scale, digits, signed)
    return f"{_fmt(value * scale, digits, signed)} [{_fmt(interval[0] * scale, digits, signed)}, {_fmt(interval[1] * scale, digits, signed)}]"


def tables_markdown(result: dict) -> str:
    targets = [t["column"] for t in result["targets"]]
    leads = result["scope"]["leads"]
    cells = result["cells"]
    lines: List[str] = []
    lines += [
        "Table 1. All scored days: B1's central-90% coverage and grid CRPS with h-row and with h + 1-row changes, and the ranking against "
        "the calendar climatology B2. Brackets are two-sided 90% stationary-bootstrap intervals (block 10). Coverage is in percent. "
        "CRPS is in the target's unit. Rank is B1 (persistence) or B2 (climatology), whichever has the lower mean CRPS.", "",
        "| target | lead | days | coverage h | coverage h+1 | CRPS h | CRPS h+1 | CRPS B2 | rank h | rank h+1 |",
        "|---|---|---|---|---|---|---|---|---|---|",
    ]
    for target in targets:
        for lead in leads:
            c = cells[target][str(lead)]["cells"].get("all")
            if c is None:
                continue
            lines.append(
                f"| `{target}` | {lead} | {c['n']} | {_ci(c, 'coverage_h', 1, scale=100)} | {_ci(c, 'coverage_h1', 1, scale=100)} | "
                f"{_ci(c, 'crps_h')} | {_ci(c, 'crps_h1')} | {_ci(c, 'crps_b2')} | {c['rank_h']} | {c['rank_h1']} |"
            )
    lines += ["", "Table 2. All scored days: the effect of the extra row on B1's CRPS (h + 1 minus h, with its interval) and persistence's "
              "skill over the climatology under each arm (`mean(S(B2) - S(B1)) / mean(S(B2))`; positive means persistence wins).", "",
              "| target | lead | CRPS h+1 − h | change | skill h | skill h+1 | flip |", "|---|---|---|---|---|---|---|"]
    for target in targets:
        for lead in leads:
            c = cells[target][str(lead)]["cells"].get("all")
            if c is None:
                continue
            d = c.get("crps_h1_minus_h_ci")
            diff = f"{c['crps_h1'] - c['crps_h']:+.3f} [{d[0]:+.3f}, {d[1]:+.3f}]" if d else "-"
            lines.append(
                f"| `{target}` | {lead} | {diff} | {_fmt(c['crps_change'] * 100 if c['crps_change'] is not None else None, 1, True)}% | "
                f"{_ci(c, 'skill_h', 3, True)} | {_ci(c, 'skill_h1', 3, True)} | {'**flip**' if c['flip'] else ''} |"
            )
    lines += ["", "Table 3. Every split in which the two arms rank differently (a flip), with the cell's days, coverage and ranking.", "",
              "| target | lead | split | days | coverage h | coverage h+1 | CRPS h | CRPS h+1 | CRPS B2 | rank h | rank h+1 |",
              "|---|---|---|---|---|---|---|---|---|---|---|"]
    count = 0
    for target in targets:
        for lead in leads:
            for split, c in cells[target][str(lead)]["cells"].items():
                if c["flip"]:
                    count += 1
                    lines.append(
                        f"| `{target}` | {lead} | {split} | {c['n']} | {_fmt(c['coverage_h'] * 100, 1)} | {_fmt(c['coverage_h1'] * 100, 1)} | "
                        f"{_fmt(c['crps_h'])} | {_fmt(c['crps_h1'])} | {_fmt(c['crps_b2'])} | {c['rank_h']} | {c['rank_h1']} |"
                    )
    if not count:
        lines.append("| none | | | | | | | | | | |")
    lines += ["", "Table 4. By regime: B1's coverage and CRPS under each arm, by the as-of scarcity state of the decision day.", "",
              "| target | lead | regime | days | coverage h | coverage h+1 | CRPS h | CRPS h+1 | CRPS B2 | rank h | rank h+1 |",
              "|---|---|---|---|---|---|---|---|---|---|---|"]
    for target in targets:
        for lead in leads:
            for split in ("regime:ample", "regime:scarce"):
                c = cells[target][str(lead)]["cells"].get(split)
                if c is None:
                    continue
                lines.append(
                    f"| `{target}` | {lead} | {split.split(':')[1]} | {c['n']} | {_ci(c, 'coverage_h', 1, scale=100)} | "
                    f"{_ci(c, 'coverage_h1', 1, scale=100)} | {_ci(c, 'crps_h')} | {_ci(c, 'crps_h1')} | {_ci(c, 'crps_b2')} | "
                    f"{c['rank_h']} | {c['rank_h1']} |"
                )
    lines += ["", "Table 5. By day type of the scored day (same columns).", "",
              "| target | lead | day type | days | coverage h | coverage h+1 | CRPS h | CRPS h+1 | CRPS B2 | rank h | rank h+1 |",
              "|---|---|---|---|---|---|---|---|---|---|---|"]
    for target in targets:
        for lead in leads:
            for split, c in cells[target][str(lead)]["cells"].items():
                if split.startswith("daytype:"):
                    lines.append(
                        f"| `{target}` | {lead} | {split.split(':')[1]} | {c['n']} | {_ci(c, 'coverage_h', 1, scale=100)} | "
                        f"{_ci(c, 'coverage_h1', 1, scale=100)} | {_ci(c, 'crps_h')} | {_ci(c, 'crps_h1')} | {_ci(c, 'crps_b2')} | "
                        f"{c['rank_h']} | {c['rank_h1']} |"
                    )
    lines += ["", "Table 6. Where the as-of anchor sits: scored days (with a value at the anchor) on which the anchor is h rows, h + 1 rows or "
              "another number of rows before the scored day.", "", "| target | lead | anchor h rows back | h + 1 rows back | other |", "|---|---|---|---|---|"]
    for target in targets:
        for lead in leads:
            g = cells[target][str(lead)]["gap_days"]
            lines.append(f"| `{target}` | {lead} | {g['h']} | {g['h1']} | {g['other']} |")
    return "\n".join(lines) + "\n"


def report_command(args) -> int:
    result = json.loads(args.result.read_text(encoding="utf-8"))
    args.output.write_text(tables_markdown(result), encoding="utf-8")
    print(f"wrote {args.output}")
    return 0


def check_control(result: dict, screen: dict) -> List[str]:
    """Differences between arm `h` on step 1's day set and step 1's screen.json (empty when it reproduces)."""

    problems = []
    for target, per_lead in result["cells"].items():
        for lead, entry in per_lead.items():
            reference = screen["forecastability"].get(target, {}).get(lead, {}).get("all")
            if reference is None:
                continue
            control = entry["control"]
            if control["n"] != reference["n"] or abs(control["b1"] - reference["b1"]) > 1e-9 or abs(control["b2"] - reference["b2"]) > 1e-9:
                problems.append(f"{target} lead {lead}: n {control['n']} vs {reference['n']}, b1 {control['b1']} vs {reference['b1']}")
    return problems


def control_command(args) -> int:
    result = json.loads(args.result.read_text(encoding="utf-8"))
    screen = json.loads(SCREEN.read_text(encoding="utf-8"))
    problems = check_control(result, screen)
    shared = sum(1 for t in result["cells"] for lead in result["cells"][t] if screen["forecastability"].get(t, {}).get(lead))
    print(json.dumps({"checked_cells": shared, "differences": problems}, indent=1))
    return 1 if problems else 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    commands = parser.add_subparsers(dest="command", required=True)
    declare = commands.add_parser("declare", help="write the declaration, before any score")
    declare.add_argument("--panel", type=Path, required=True)
    declare.add_argument("--output", type=Path, default=DECLARATION)
    declare.set_defaults(handler=declare_command)
    run = commands.add_parser("run", help="both arms, every target, lead and split")
    run.add_argument("--panel", type=Path, required=True)
    run.add_argument("--output", type=Path, required=True)
    run.add_argument("--workers", type=int, default=4)
    run.set_defaults(handler=run_command)
    report = commands.add_parser("report", help="the tables")
    report.add_argument("result", type=Path)
    report.add_argument("--output", type=Path, required=True)
    report.set_defaults(handler=report_command)
    control = commands.add_parser("control", help="arm h on step 1's days against step 1's screen.json")
    control.add_argument("result", type=Path)
    control.set_defaults(handler=control_command)
    args = parser.parse_args(argv)
    return args.handler(args)


if __name__ == "__main__":
    sys.exit(main())
