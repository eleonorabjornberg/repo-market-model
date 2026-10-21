#!/usr/bin/env python3
"""H9 step 1, the screen of the richer targets (#639): forecastability, lead and overlap.

An exploratory screen on development data, not a record and not a verdict (scoring protocol v1, `docs/decisions/scoring-protocol.md`
§1: development data never gives a verdict; ruling on #639 of 12 October 2026). It writes JSON and Markdown to the paths it is given
and nothing into `docs/runs/`. Every choice is in `metadata/richer_targets_639.json`, which `run` refuses to read unless it is
committed and unchanged, and which `declare` writes before any score. No day after 2025-12-31 is read (`docs/decisions/lockbox.md`;
`require_unlocked`), no hindsight regime label is used (ruling on #515: the regimes are the as-of scarcity state and the day type),
nothing is published and nothing is fitted: step 2, the model, is a later step.

    # PUB.csv, AUG2.csv, EW.csv: the commands of scripts/source_screen.py's docstring (the published panel, then
    # measurement_fields.py's scratch panel and early_warning_inputs.py's)
    PYTHONPATH=src python3 scripts/richer_targets_639.py panel --panel AUG2.csv --extra EW.csv --output H9.csv
    PYTHONPATH=src python3 scripts/richer_targets_639.py declare --panel H9.csv
    git add metadata/richer_targets_639.json && git commit        # a declaration is made before any score
    PYTHONPATH=src python3 scripts/richer_targets_639.py run --panel H9.csv --output OUT/screen.json
    PYTHONPATH=src python3 scripts/richer_targets_639.py report OUT/screen.json --output OUT/tables.md

* **Targets.** The ten columns of `repo_model.richer_targets.TARGETS`, each read as published (the realised value on the scored day) and
  as of each decision instant through `repo_model.asof.InformationRule` at leads of 1, 2, 3, 5 and 10 panel days.
* **Forecastability.** At each lead the target's as-of persistence B1 (the last public value plus the empirical distribution of the
  lead's own changes over the trailing two years) and its calendar climatology B2 (the trailing year's values on days of the scored
  day's type), the benchmarks of protocol v1 §4 generalised to any series (`richer_targets.b1_quantiles`, `b2_quantiles`), scored by the
  protocol's grid CRPS and by the absolute error of the median; the naive last-value error is reported beside them. B1's skill over B2 is
  `mean(S(B2) - S(B1)) / mean(S(B2))` with a one-sided 95% and a two-sided 90% interval from the protocol's stationary bootstrap
  (`scoring_protocol.paired_test`). A day on which either benchmark or the outcome is missing is dropped for both.
* **Lead.** The target's as-of value at each lead against the +5 bp pressure indicator and the spread level of the scored day: Spearman, with
  an interval from a stationary bootstrap. The pre-onset contrast: the value read at lead 1 on the 1 to 5 panel days before each onset on the
  grid every horizon scores, against every other scored day (the difference in units of the other days' standard deviation and the AUC), with
  an interval from resampling the onsets.
* **Overlap.** Spearman of the target with SOFR − IORB on the same day, in level and in the change from the day before.
* **Regimes.** The as-of scarcity state at the same lead (ample 0 and 1, scarce 2 and 3) and the reporting day type; both known at the decision.

Every number is exploratory and none is corrected for multiplicity. Reads the scratch panels, which are gitignored, so this is not a test.
Stdlib only.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import importlib.util
import json
import math
import multiprocessing
import sys
from datetime import date, datetime, time, timezone
from pathlib import Path
from types import MappingProxyType
from typing import Dict, List, Mapping, Optional, Sequence, Tuple
from unittest import mock

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))

from repo_model import contract, measurement_fields, pressure, richer_targets, scarcity  # noqa: E402
from repo_model.asof import fold_grid  # noqa: E402
from repo_model.data import DailyObservation, exceeds_bp, load_daily_panel  # noqa: E402
from repo_model.evaluation_splits import load_split_declaration  # noqa: E402
from repo_model.lockbox import require_unlocked  # noqa: E402
from repo_model.metrics import _quantile  # noqa: E402
from repo_model.scoring_protocol import BLOCK_LENGTH, DRAWS, paired_test  # noqa: E402

# Lockbox classification (#1058): tests/test_lockbox.py reads these literals from this file's syntax tree.
LOCKBOX_READS = {
    "run_command": (
        "not_entry",
        "the exploratory H9 screen (#639): walks the lead-1 fold grid, calls "
        "lockbox.require_unlocked on every scored day before it reads one, refuses a panel past "
        "2025-12-31 and fits and selects nothing",
    ),
}

DECLARATION = REPO / "metadata" / "richer_targets_639.json"
SPLITS = REPO / "metadata" / "evaluation_splits.json"
SNAPSHOTS = REPO / "tests" / "fixtures" / "snapshots"
BUILD_CUTOFF = datetime(2026, 9, 8, 21, 31, 42, tzinfo=timezone.utc)

FIRST_DAY = date(2018, 6, 29)
FIRST_DAY_EVERY_HORIZON = date(2018, 7, 6)
LAST_DAY = date(2025, 12, 31)
DECISION_TIME = time(16, 0)
MINIMUM_HISTORY = 61
THRESHOLD_BP = 5.0
PRE_ONSET_DAYS = (1, 5)
#: A cell needs this many days, and a pressure correlation this many pressure days.
MINIMUM_DAYS = 30
MINIMUM_PRESSURE = 3
SEED = 639
SCARCITY = scarcity.RESERVE_SCARCITY_STATE
BANDS = ("ample", "scarce")
DAY_TYPES = ("ordinary", "month_end", "tax_date", "quarter_end")
#: The resamples of the intervals other than the paired CRPS test, which uses the protocol's own.
CORRELATION_DRAWS = 1000
ONSET_DRAWS = 2000


def _load(name: str):
    spec = importlib.util.spec_from_file_location(f"{name}_script", REPO / "scripts" / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[f"{name}_script"] = module
    spec.loader.exec_module(module)
    return module


rds = _load("risk_date_severity")


# -- the declaration -----------------------------------------------------------------------------------------------


def declaration_document(panel: Path) -> dict:
    """What is fixed before any score."""

    return {
        "status": (
            "declared by the pull request that closes #639 before any score; step 1 of H9, an exploratory screen on development data, "
            "not a record and not a verdict (scoring protocol v1 section 1; ruling on #639, 12 October 2026). Nothing is fitted, "
            "selected into a model or published, no rule, threshold, onset definition or availability time changes, no day after "
            "2025-12-31 is read, and no hindsight regime label is used (ruling on #515). None of the intervals is corrected for multiplicity"
        ),
        "issue": 639,
        "hypothesis": "H9",
        "step": 1,
        "panel": {
            "sha256": hashlib.sha256(panel.read_bytes()).hexdigest(),
            "built_by": "scripts/richer_targets_639.py panel over measurement_fields.py's scratch panel and early_warning_inputs.py's",
        },
        "days": "the scored days of the lead-1 fold grid, 2018-06-29 to 2025-12-31 (source_screen), the same days at every lead",
        "leads": list(richer_targets.LEADS),
        "targets": [target._asdict() for target in richer_targets.TARGETS],
        "target_reading": (
            "the realised value of the scored day, as the panel holds it; the forecasts' inputs are read as of each decision "
            "instant through repo_model.asof.InformationRule at the declared leads"
        ),
        "benchmarks": {
            "B1": "the last public value plus the empirical distribution of the lead's own changes over the trailing two years "
                  "(protocol v1 section 4, generalised to the series)",
            "B2": "the trailing year's values on days of the scored day's reporting day type (protocol v1 section 4, generalised)",
            "minimum_changes_b1": richer_targets.MINIMUM_CHANGES,
            "minimum_values_b2": richer_targets.MINIMUM_CLIMATOLOGY,
            "dropped": "a day on which the outcome, B1 or B2 is missing is dropped for both benchmarks",
        },
        "scores": {
            "crps": "scoring_protocol.grid_crps on the protocol's 23 quantile levels",
            "mae": "the absolute error of the forecast's median (level 0.5)",
            "naive": "the absolute error of the last public value",
            "skill": "mean(S(B2) - S(B1)) / mean(S(B2)): positive when B1 beats B2",
        },
        "interval": {
            "paired_crps": f"scoring_protocol.paired_test, stationary bootstrap, mean block {BLOCK_LENGTH}, {DRAWS} draws, seed {SEED}, "
                           "one-sided 95% lower bound of mean(d) and a two-sided 90% interval of skill",
            "correlations": f"stationary bootstrap of full-sample ranks, mean block {richer_targets.BLOCK_LENGTH}, {CORRELATION_DRAWS} draws, "
                            f"seed {SEED}, two-sided 90%",
            "pre_onset": f"resampling onsets, {ONSET_DRAWS} draws, seed {SEED}, two-sided 90%",
        },
        "splits": {
            "regime": "the as-of scarcity state at the same lead: ample (0, 1), scarce (2, 3)",
            "day_type": "SplitDeclaration.reporting_day_type of the scored day",
            "minimum_days": MINIMUM_DAYS,
        },
        "lead": {
            "outcomes": ["pressure: the spread strictly above +5 bp on whole basis points (repo_model.data.exceeds_bp)", "level: the spread"],
            "pressure_is_not_a_judge": "the +5 bp indicator is the definition of an episode here, as in the screens of #478 and #629; "
                                       "the judge it served is retired as a decision rule (protocol v1 section 10)",
            "minimum_pressure_days": MINIMUM_PRESSURE,
            "onsets": "repo_model.pressure.onsets at +5 bp over the scored days of the grid every horizon scores (from 2018-07-06)",
            "pre_onset_window_panel_days": list(PRE_ONSET_DAYS),
            "pre_onset_reading_lead": 1,
        },
        "overlap": "Spearman of the target with SOFR - IORB on the same day, in level and in the change from the previous panel day",
        "not_run": "step 2, the model: its targets are chosen from this screen, which is Eleonora's call (see the pull request)",
    }


def declare_command(args) -> int:
    document = declaration_document(args.panel)
    args.output.write_text(json.dumps(document, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"written": str(args.output), "panel_sha256": document["panel"]["sha256"]}, indent=1))
    return 0


# -- the panel -----------------------------------------------------------------------------------------------------


def _cell(value) -> str:
    return "" if value is None else repr(float(value))


def panel_command(args) -> int:
    base = load_daily_panel(args.panel)
    with args.panel.open(newline="", encoding="utf-8") as handle:
        header = next(csv.reader(handle))
    extra: Dict[str, Dict[date, Optional[float]]] = {}
    for path in args.extra:
        for row in load_daily_panel(path):
            for column, value in row.values.items():
                extra.setdefault(column, {})[row.date] = value
    columns = list(header[1:])
    keep = [row for row in base if row.date <= LAST_DAY]
    merged: List[DailyObservation] = []
    for row in keep:
        values = dict(row.values)
        for column, by_day in extra.items():
            if column in values:
                if by_day.get(row.date) != values[column]:
                    raise ValueError(f"{column!r} differs between the panels on {row.date}")
            else:
                values[column] = by_day.get(row.date)
        merged.append(DailyObservation(row.date, values))
    for column in extra:
        if column not in columns:
            columns.append(column)
    built, summary = richer_targets.assemble(merged, SNAPSHOTS, cutoff=BUILD_CUTOFF, end=LAST_DAY)
    written = columns + [c for c in built[0].values if c not in columns and c != "spread_bps"]
    with args.output.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerow(["date"] + written)
        for row in built:
            writer.writerow([row.date.isoformat()] + [_cell(row.values.get(c)) for c in written])
    summary.update(output=str(args.output), rows=len(built), first=built[0].date.isoformat(), last=built[-1].date.isoformat(),
                   sha256=hashlib.sha256(args.output.read_bytes()).hexdigest())
    print(json.dumps(summary, indent=1))
    return 0


# -- the run -------------------------------------------------------------------------------------------------------


def switched():
    """`COLUMN_FIELDS` and the scarcity state's fields in the feature map, for this run only."""

    fields = dict(scarcity.measurement_feature_fields())
    fields.update(richer_targets.COLUMN_FIELDS)
    return mock.patch.multiple(
        contract,
        FEATURE_FIELDS=MappingProxyType({**contract.FEATURE_FIELDS, **fields}),
        FEATURE_SOURCES=MappingProxyType(
            {**contract.FEATURE_SOURCES, **{c: tuple(sorted({s for s, _f in pairs})) for c, pairs in fields.items()}}
        ),
    )


def band(state: Optional[float]) -> str:
    if state is None:
        return "unknown"
    return "ample" if state < 2 else "scarce"


def _mean(values: Sequence[float]) -> float:
    return sum(values) / len(values)


def _skill_cell(b1: Sequence[float], b2: Sequence[float], days: Sequence[date], seed: int) -> dict:
    """Mean scores of both benchmarks and B1's skill over B2, with the protocol's paired test."""

    cell = {"n": len(days), "b1": _mean(b1), "b2": _mean(b2)}
    if len(days) < MINIMUM_DAYS or cell["b2"] == 0.0:
        cell["skill"] = None
        return cell
    test = paired_test(dict(zip(days, b2)), dict(zip(days, b1)), seed=seed)
    draws = test.skill_draws
    tail = int(0.05 * test.draws)
    cell.update(
        skill=test.skill,
        skill_low=draws[tail],
        skill_high=draws[test.draws - tail - 1],
        # Pinned to the percentile bootstrap this screen's figures were made with (PR #660): PR #695 made
        # `lower_mean_difference()` and `p_value` the studentized ones (#655).
        lower_mean_difference=_quantile(test.mean_difference_draws, 0.05),
        p_value=sum(1 for value in test.mean_difference_draws if value <= 0.0) / test.draws,
    )
    return cell


def _score_target(job) -> dict:
    """One target's forecastability at every lead, in all its splits (a worker of `run`)."""

    target, lead_data, scored_days, kinds_of_scored, values, dates, rows_kinds, scored_idx, window = job
    out = {}
    for lead, reads, regime in lead_data:
        days, b1c, b2c, b1m, b2m, naive, regimes, kinds = [], [], [], [], [], [], [], []
        for i, t in enumerate(scored_idx):
            y = values[t]
            r = reads[i]
            if y is None or values[r] is None:
                continue
            decision = t - lead
            first1 = window["b1"][lead][i]
            first2 = window["b2"][lead][i]
            q1 = richer_targets.b1_quantiles(values, dates, r, lead, first=first1)
            q2 = richer_targets.b2_quantiles(values, rows_kinds, dates, r, kinds_of_scored[i], first=first2)
            if q1 is None or q2 is None:
                continue
            days.append(scored_days[i])
            b1c.append(richer_targets.crps(q1, y))
            b2c.append(richer_targets.crps(q2, y))
            b1m.append(richer_targets.median_error(q1, y))
            b2m.append(richer_targets.median_error(q2, y))
            naive.append(abs(values[r] - y))
            regimes.append(regime[i])
            kinds.append(kinds_of_scored[i])
        splits = {"all": list(range(len(days)))}
        for name in BANDS:
            splits[f"regime:{name}"] = [k for k in range(len(days)) if regimes[k] == name]
        for name in DAY_TYPES:
            splits[f"daytype:{name}"] = [k for k in range(len(days)) if kinds[k] == name]
        cells = {}
        for split, idx in splits.items():
            if not idx:
                continue
            sub_days = [days[k] for k in idx]
            cell = _skill_cell([b1c[k] for k in idx], [b2c[k] for k in idx], sub_days, SEED)
            cell["mae_b1"] = _mean([b1m[k] for k in idx])
            cell["mae_b2"] = _mean([b2m[k] for k in idx])
            cell["mae_naive"] = _mean([naive[k] for k in idx])
            cells[split] = cell
        out[str(lead)] = cells
    return {"target": target, "leads": out}


def run_command(args) -> int:
    declared = rds.committed_declaration(DECLARATION)
    panel_sha = hashlib.sha256(args.panel.read_bytes()).hexdigest()
    if panel_sha != declared["panel"]["sha256"]:
        raise SystemExit(f"the panel's digest {panel_sha} is not the declared {declared['panel']['sha256']}")
    rows = load_daily_panel(args.panel)
    if rows[-1].date > LAST_DAY:
        raise SystemExit(f"the panel runs past {LAST_DAY}; a screen reads no day in a locked tier")
    registry = measurement_fields.load_registry()
    splits = load_split_declaration(SPLITS)
    dates = [row.date for row in rows]
    leads = tuple(declared["leads"])
    columns = [t["column"] for t in declared["targets"]]
    with switched():
        grid = [
            i
            for i in fold_grid(dates, registry, decision_time=DECISION_TIME, minimum_history=MINIMUM_HISTORY, horizon=1)
            if FIRST_DAY <= dates[i] <= LAST_DAY
        ]
        require_unlocked((dates[i] for i in grid), where="richer_targets_639")
        every_horizon = {
            dates[i]
            for i in fold_grid(dates, registry, decision_time=DECISION_TIME, minimum_history=MINIMUM_HISTORY, horizon=5)
            if FIRST_DAY_EVERY_HORIZON <= dates[i] <= LAST_DAY
        }
        reads = richer_targets.as_of_rows(rows, registry, columns + [SCARCITY], leads=leads, scored=grid, decision_time=DECISION_TIME)
    scored_days = [dates[i] for i in grid]
    rows_kinds = [splits.reporting_day_type(r.date, r.values) for r in rows]
    kinds_of_scored = [rows_kinds[i] for i in grid]
    series = {c: [None if r.values.get(c) is None else float(r.values[c]) for r in rows] for c in columns}
    spreads = [r.spread_bps for r in rows]
    window = {
        "b1": {lead: [richer_targets.window_first(dates, t - lead, 2) for t in grid] for lead in leads},
        "b2": {lead: [richer_targets.window_first(dates, t - lead, 1) for t in grid] for lead in leads},
    }
    state = {lead: [rows[r].values.get(SCARCITY) for r in reads[lead][SCARCITY]] for lead in leads}
    regime = {lead: [band(s) for s in state[lead]] for lead in leads}

    jobs = [
        (
            column, [(lead, reads[lead][column], regime[lead]) for lead in leads], scored_days, kinds_of_scored,
            series[column], dates, rows_kinds, grid, window,
        )
        for column in columns
    ]
    with multiprocessing.Pool(min(len(jobs), args.workers)) as pool:
        forecastability = {r["target"]: r["leads"] for r in pool.map(_score_target, jobs)}

    # lead: the as-of value at each lead against the pressure indicator and the spread level
    pressure_flag = [1.0 if exceeds_bp(spreads[t], THRESHOLD_BP) else 0.0 for t in grid]
    level = [spreads[t] for t in grid]
    lead_out: Dict[str, dict] = {}
    for column in columns:
        per_lead = {}
        for lead in leads:
            x_all = [series[column][r] for r in reads[lead][column]]
            cells = {}
            for split, keep in _regime_splits(regime[lead]).items():
                idx = [i for i in keep if x_all[i] is not None]
                entry = {}
                for name, outcome in (("pressure", pressure_flag), ("level", level)):
                    x = [x_all[i] for i in idx]
                    y = [outcome[i] for i in idx]
                    events = int(sum(y)) if name == "pressure" else None
                    if len(idx) < MINIMUM_DAYS or (name == "pressure" and (events < MINIMUM_PRESSURE or events == len(idx))):
                        entry[name] = {"n": len(idx), "rho": None, **({"pressure_days": events} if events is not None else {})}
                        continue
                    cell = richer_targets.spearman_interval(x, y, seed=SEED, draws=CORRELATION_DRAWS)
                    if events is not None:
                        cell["pressure_days"] = events
                    entry[name] = cell
                cells[split] = entry
            per_lead[str(lead)] = cells
        lead_out[column] = per_lead

    # lead: the pre-onset contrast at lead 1
    onset_days = pressure.onsets(rows, THRESHOLD_BP, [d for d in scored_days if d in every_horizon])
    position = {d: i for i, d in enumerate(dates)}
    scored_index = {d: i for i, d in enumerate(scored_days)}
    pre_groups: List[List[int]] = []
    for onset in onset_days:
        at = position[onset]
        group = [scored_index[dates[at - back]] for back in range(PRE_ONSET_DAYS[0], PRE_ONSET_DAYS[1] + 1)
                 if dates[at - back] in scored_index]
        pre_groups.append(group)
    pre_set = {i for g in pre_groups for i in g}
    other_idx = [i for i in range(len(grid)) if i not in pre_set]
    pre_out: Dict[str, dict] = {}
    regime1 = regime[1]
    for column in columns:
        x1 = [series[column][r] for r in reads[1][column]]
        cells = {}
        for split, keep_all in (("all", None), ("regime:ample", "ample"), ("regime:scarce", "scarce")):
            def ok(i, keep=keep_all):
                return x1[i] is not None and (keep is None or regime1[i] == keep)

            groups = [[x1[i] for i in g if ok(i)] for g in pre_groups]
            other = [x1[i] for i in other_idx if ok(i)]
            cells[split] = richer_targets.pre_onset_interval(groups, other, seed=SEED, draws=ONSET_DRAWS)
        pre_out[column] = cells

    # overlap with SOFR - IORB on the same day
    overlap: Dict[str, dict] = {}
    for column in columns:
        values = series[column]
        cells = {}
        for split, idx_all in _overlap_splits(grid, regime[1], kinds_of_scored).items():
            for kind in ("level", "change"):
                pairs = []
                for i in idx_all:
                    t = grid[i]
                    if kind == "level":
                        a, b = values[t], spreads[t]
                    else:
                        a = None if values[t] is None or values[t - 1] is None else values[t] - values[t - 1]
                        b = spreads[t] - spreads[t - 1]
                    if a is not None:
                        pairs.append((a, b))
                if len(pairs) < MINIMUM_DAYS:
                    cells[f"{split}:{kind}"] = {"n": len(pairs), "rho": None}
                else:
                    cells[f"{split}:{kind}"] = richer_targets.spearman_interval(
                        [a for a, _b in pairs], [b for _a, b in pairs], seed=SEED, draws=CORRELATION_DRAWS)
        overlap[column] = cells

    result = {
        "scope": {
            "first_day": scored_days[0].isoformat(),
            "last_day": scored_days[-1].isoformat(),
            "scored_days": len(grid),
            "leads": list(leads),
            "pressure_days": int(sum(pressure_flag)),
            "onsets": [d.isoformat() for d in onset_days],
            "pre_onset_days": len(pre_set),
            "regime_days_lead1": {name: regime[1].count(name) for name in BANDS},
            "panel_sha256": panel_sha,
            "declaration_sha256": hashlib.sha256(DECLARATION.read_bytes()).hexdigest(),
        },
        "targets": declared["targets"],
        "forecastability": forecastability,
        "lead": {"correlation": lead_out, "pre_onset": pre_out},
        "overlap": overlap,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({k: v for k, v in result["scope"].items() if k != "onsets"}, indent=1))
    print(f"onsets: {len(onset_days)}")
    return 0


def _regime_splits(regime: Sequence[str]) -> Dict[str, List[int]]:
    out = {"all": list(range(len(regime)))}
    for name in BANDS:
        out[f"regime:{name}"] = [i for i, r in enumerate(regime) if r == name]
    return out


def _overlap_splits(grid, regime, kinds) -> Dict[str, List[int]]:
    out = {"all": list(range(len(grid))), "ordinary": [i for i, k in enumerate(kinds) if k == "ordinary"]}
    for name in BANDS:
        out[f"regime:{name}"] = [i for i, r in enumerate(regime) if r == name]
    return out


# -- the report ----------------------------------------------------------------------------------------------------


def _fmt(value, digits=3, signed=False) -> str:
    if value is None or (isinstance(value, float) and math.isnan(value)):
        return "-"
    return f"{value:+.{digits}f}" if signed else f"{value:.{digits}f}"


def _interval(cell: dict, key: str = "rho", low: str = "low", high: str = "high", digits=2) -> str:
    if cell is None or cell.get(key) is None:
        return "-"
    return f"{cell[key]:+.{digits}f} [{cell[low]:+.{digits}f}, {cell[high]:+.{digits}f}]"


def tables_markdown(result: dict) -> str:
    targets = result["targets"]
    leads = result["scope"]["leads"]
    lines: List[str] = []
    lines += ["Table 1. Forecastability: B1 (as-of persistence) against B2 (calendar climatology), all scored days. Mean grid CRPS in the "
              "target's unit; skill is `mean(S(B2) - S(B1)) / mean(S(B2))` with a two-sided 90% interval; positive means persistence beats "
              "the calendar climatology. The last three columns are the absolute error of B1's median, B2's median and the last value.", ""]
    lines += ["| target | lead | days | CRPS B1 | CRPS B2 | skill of B1 over B2 | MAE B1 | MAE B2 | MAE last value |", "|---|---|---|---|---|---|---|---|---|"]
    for t in targets:
        for lead in leads:
            c = result["forecastability"][t["column"]][str(lead)].get("all")
            if c is None:
                continue
            skill = "-" if c.get("skill") is None else f"{c['skill']:+.3f} [{c['skill_low']:+.3f}, {c['skill_high']:+.3f}]"
            lines.append(f"| `{t['column']}` | {lead} | {c['n']} | {_fmt(c['b1'])} | {_fmt(c['b2'])} | {skill} | "
                         f"{_fmt(c['mae_b1'])} | {_fmt(c['mae_b2'])} | {_fmt(c['mae_naive'])} |")
    lines.append("")
    for lead in (1, 5):
        lines += [f"Table 2 (lead {lead}). B1's skill over B2 by the as-of scarcity state and by day type.", "",
                  "| target | ample | scarce | ordinary | month end | tax date | quarter end |", "|---|---|---|---|---|---|---|"]
        for t in targets:
            cells = result["forecastability"][t["column"]][str(lead)]
            row = []
            for split in ("regime:ample", "regime:scarce", "daytype:ordinary", "daytype:month_end", "daytype:tax_date", "daytype:quarter_end"):
                c = cells.get(split)
                row.append("-" if c is None or c.get("skill") is None
                           else f"{c['skill']:+.2f} [{c['skill_low']:+.2f}, {c['skill_high']:+.2f}] ({c['n']})")
            lines.append(f"| `{t['column']}` | " + " | ".join(row) + " |")
        lines.append("")
    lines += ["Table 3. Lead: Spearman of the target's as-of value at each lead with the +5 bp pressure indicator of the scored day (all scored days), "
              "with a two-sided 90% interval.", "", "| target | " + " | ".join(f"lead {l}" for l in leads) + " | pressure days at lead 1 |",
              "|---|" + "---|" * (len(leads) + 1)]
    for t in targets:
        cells = result["lead"]["correlation"][t["column"]]
        row = [_interval(cells[str(l)]["all"]["pressure"]) for l in leads]
        lines.append(f"| `{t['column']}` | " + " | ".join(row) + f" | {cells['1']['all']['pressure'].get('pressure_days', '-')} |")
    lines.append("")
    lines += ["Table 4. Lead, by the as-of scarcity state: the same correlation at lead 1, and the same with the spread level of the scored day.", "",
              "| target | pressure, ample | pressure, scarce | level, all | level, ample | level, scarce |", "|---|---|---|---|---|---|"]
    for t in targets:
        cells = result["lead"]["correlation"][t["column"]]["1"]
        lines.append(f"| `{t['column']}` | {_interval(cells['regime:ample']['pressure'])} | {_interval(cells['regime:scarce']['pressure'])} | "
                     f"{_interval(cells['all']['level'])} | {_interval(cells['regime:ample']['level'])} | {_interval(cells['regime:scarce']['level'])} |")
    lines.append("")
    lines += [f"Table 5. The pre-onset contrast at lead 1: the target on the {PRE_ONSET_DAYS[0]} to {PRE_ONSET_DAYS[1]} panel days before each of the "
              f"{len(result['scope']['onsets'])} onsets against every other scored day. Standardised difference (in the other days' standard "
              "deviations) and AUC (0.5 is no lead), two-sided 90% intervals from resampling the onsets.", "",
              "| target | split | onsets | std. difference | AUC |", "|---|---|---|---|---|"]
    for t in targets:
        for split in ("all", "regime:ample", "regime:scarce"):
            c = result["lead"]["pre_onset"][t["column"]][split]
            if c is None:
                lines.append(f"| `{t['column']}` | {split} | 0 | - | - |")
                continue
            lines.append(f"| `{t['column']}` | {split} | {c['onsets']} | {_interval(c, 'std_diff', 'std_diff_low', 'std_diff_high')} | "
                         f"{_interval(c, 'auc', 'auc_low', 'auc_high')} |")
    lines.append("")
    lines += ["Table 6. Overlap: Spearman of the target with SOFR − IORB on the same day, in level and in the change from the day before.", "",
              "| target | level, all | level, ordinary days | level, ample | level, scarce | change, all | change, ordinary days |", "|---|---|---|---|---|---|---|"]
    for t in targets:
        o = result["overlap"][t["column"]]
        lines.append(f"| `{t['column']}` | " + " | ".join(_interval(o.get(k)) for k in (
            "all:level", "ordinary:level", "regime:ample:level", "regime:scarce:level", "all:change", "ordinary:change")) + " |")
    lines.append("")
    return "\n".join(lines)


def report_command(args) -> int:
    result = json.loads(args.result.read_text(encoding="utf-8"))
    args.output.write_text(tables_markdown(result), encoding="utf-8")
    print(f"wrote {args.output}")
    return 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    commands = parser.add_subparsers(dest="command", required=True)
    panel = commands.add_parser("panel", help="the scratch panels joined, with the H9 target columns")
    panel.add_argument("--panel", type=Path, required=True)
    panel.add_argument("--extra", type=Path, nargs="*", default=[])
    panel.add_argument("--output", type=Path, required=True)
    panel.set_defaults(handler=panel_command)
    declare = commands.add_parser("declare", help="write the declaration, before any score")
    declare.add_argument("--panel", type=Path, required=True)
    declare.add_argument("--output", type=Path, default=DECLARATION)
    declare.set_defaults(handler=declare_command)
    run = commands.add_parser("run", help="the screen")
    run.add_argument("--panel", type=Path, required=True)
    run.add_argument("--output", type=Path, required=True)
    run.add_argument("--workers", type=int, default=4)
    run.set_defaults(handler=run_command)
    report = commands.add_parser("report", help="the tables")
    report.add_argument("result", type=Path)
    report.add_argument("--output", type=Path, required=True)
    report.set_defaults(handler=report_command)
    args = parser.parse_args(argv)
    return args.handler(args)


if __name__ == "__main__":
    sys.exit(main())
