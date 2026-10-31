"""The Wednesday reserve level as a candidate scarcity input, beside the week average (#1146; H5 step 3, scarcity input).

A development study, never a verdict. It writes JSON and Markdown to the paths it is given and nothing into `docs/runs/`.
Every choice is in `metadata/wednesday_scarcity_1146.json`, which this script refuses to read unless it is committed and
unchanged. Eleonora's ruling of 22 October 2026 (option 2 on #1143): build the scarcity state from the Wednesday level
(`WRBWFRBL`, the same H.4.1 release and instant as the panel's `WRESBAL` week average) as a separate candidate input, run the H5
candidate (#941's scaled mean reversion, `spread_mr_fhs_mad20_f0.5`) with each reading, and score it as protocol v1 by regime and
day type and on the days where the two states differ. The published declaration and `metadata/sources.json` are untouched.

What the candidate reads is the spread series and nothing else (`repo_model.spread_mr_fhs`: "No regime label and no other
column is an input"), so its forecasts cannot move with the scarcity state. The study shows that instead of assuming it: the
candidate is walked on the published panel and on the same panel with `reserve_balances` replaced by the Wednesday level, and
every quantile of every cell is compared. It then splits the candidate's scores by the state under each reading and on the days
where the readings differ, which is where a model that did read the state would move. #1145's state-scaled arms are not merged;
the ruling asks for them "if merged by then", and the arms are data here so that a later directive adds them.

The Wednesday-level states come from `scripts/h41_wednesday_levels_970.py`'s substitution (same release, same declared instant,
same vintage id as the average each level sits beside) and `repo_model.scarcity.own_leg_states`; this script adds
`require_same_release`, which refuses a Wednesday value that steps on a row before its week average does. Scored decision days
are those whose five targets are on or before 2025-12-31; no later day is read and no locked day is scored
(`docs/decisions/lockbox.md`).

The whole study runs in minutes. Commands, from a clone of the branch:

    PYTHONPATH=src python3 -m repo_model.cli build --raw-root tests/fixtures/snapshots/funding_inputs \\
        --output PUB.csv --build-cutoff 2026-09-08T21:31:42+00:00 --decision-time 16:00:00
    PYTHONPATH=src python3 -m repo_model.cli verify-panel PUB.csv --manifest metadata/funding_panel_manifest.json
    PYTHONPATH=src python3 scripts/wednesday_scarcity_1146.py score --panel PUB.csv \\
        --output docs/research/wednesday-scarcity-1146/result.json
    PYTHONPATH=src python3 scripts/wednesday_scarcity_1146.py page \\
        --score docs/research/wednesday-scarcity-1146/result.json --output docs/research/wednesday-scarcity-1146-result.md

Stdlib only.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import sys
import tempfile
from datetime import date, datetime, time, timedelta
from pathlib import Path
from typing import Dict, List, Mapping, Optional, Sequence, Tuple

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))


def _load(name: str):
    spec = importlib.util.spec_from_file_location(name, REPO / "scripts" / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


from repo_model import b1_calendar as b1c, pressure  # noqa: E402
from repo_model import protocol_benchmarks as pb, scoring_protocol as sp  # noqa: E402
from repo_model import spread_mr_fhs as fhs  # noqa: E402
from repo_model import turn_days  # noqa: E402
from repo_model.baseline import panel_sha256  # noqa: E402
from repo_model.data import (  # noqa: E402
    DailyObservation, build_daily_panel, load_daily_panel, load_point_in_time_panel, verify_daily_panel, write_daily_panel,
)
from repo_model.evaluation_splits import load_split_declaration  # noqa: E402
from repo_model.ingest import build_point_in_time_snapshot, load_snapshot_manifest, load_source_registry  # noqa: E402
from repo_model.scarcity import measurement_declaration, own_leg_states  # noqa: E402
from repo_model.splits import LookAheadError, SplitError  # noqa: E402

s686 = _load("spread_mean_reversion_686")
s761 = _load("spread_mr_variants_761")
s941 = _load("fhs_scale_941")
w970 = _load("h41_wednesday_levels_970")

DECLARATION = REPO / "metadata" / "wednesday_scarcity_1146.json"
SPLITS = s686.SPLITS
SOURCES = s686.SOURCES
SEED = 1146
LAST_DAY = s686.LAST_DAY
DECISION_TIME = s686.DECISION_TIME
MIN_GROUP_DAYS = s686.MIN_GROUP_DAYS
CANDIDATE = "spread_mr_fhs_mad20_f0.5"
B1P = "B1_prime"
BENCHMARKS = ("B1", B1P, "B2")
MODELS = BENCHMARKS + (CANDIDATE,)
METRIC_NAMES = ("grid_crps", "upper_tail_twcrps")
READINGS = {"week_average": "state_week_average", "wednesday_level": "state_wednesday_level"}
IDX = {level: sp.GRID.index(level) for level in (0.05, 0.95)}
Q95 = sp.GRID.index(0.95)
RESERVES = "reserve_balances"


def committed_declaration(path: Path = DECLARATION) -> dict:
    """The declaration, refused unless it is committed and unchanged since `HEAD`."""

    return s686.committed_declaration(path)


# -- the Wednesday panel ---------------------------------------------------------------------------------------------


def wednesday_panel(published: Sequence[DailyObservation], level: Sequence[DailyObservation]) -> List[DailyObservation]:
    """The published rows with `reserve_balances` taken from the Wednesday-level rows and everything else the published row's own.

    A hole in the level stays a hole: it is never filled with the average.

    Raises:
        ValueError: the two panels do not have the same dates.
    """

    if [r.date for r in published] != [r.date for r in level]:
        raise ValueError("the Wednesday-level panel and the published panel have different dates")
    out = []
    for row, other in zip(published, level):
        values = dict(row.values)
        values[RESERVES] = other.values.get(RESERVES)
        out.append(DailyObservation(row.date, values))
    return out


def _changes(rows: Sequence[DailyObservation]) -> List[date]:
    return [row.date for prev, row in zip(rows, rows[1:]) if row.values.get(RESERVES) != prev.values.get(RESERVES)]


def require_same_release(average: Sequence[DailyObservation], level: Sequence[DailyObservation]) -> None:
    """A Wednesday level is read at the print of its own release, the week average's: its value may step only on a row where the
    average's does ("same release, same instant", `metadata/h41_wednesday_levels_970.json`).

    Raises:
        LookAheadError: the level steps on a row before (or without) the average stepping.
    """

    average_changes = set(_changes(average))
    for day in _changes(level):
        if day not in average_changes:
            raise LookAheadError(
                f"the Wednesday level steps on {day}, a row on which the week average does not: it would be read before its release"
            )


# -- comparing two walks, and partitioning days ----------------------------------------------------------------------


def compare_forecasts(a: Mapping[date, Mapping[int, Sequence[float]]], b: Mapping[date, Mapping[int, Sequence[float]]]) -> dict:
    """Cells, cells whose 23 quantiles are identical, and the largest absolute difference of any quantile.

    Raises:
        ValueError: the two walks do not forecast the same days.
    """

    if sorted(a) != sorted(b):
        raise ValueError("the two walks forecast different days")
    cells = identical = 0
    largest = 0.0
    for day in sorted(a):
        if sorted(a[day]) != sorted(b[day]):
            raise ValueError(f"the two walks forecast different leads on {day}")
        for lead in sorted(a[day]):
            cells += 1
            gap = max(abs(x - y) for x, y in zip(a[day][lead], b[day][lead]))
            identical += 1 if gap == 0.0 else 0
            largest = max(largest, gap)
    return {"cells": cells, "identical": identical, "max_abs_difference": largest}


def partition(average: Mapping[date, Optional[float]], level: Mapping[date, Optional[float]], days: Sequence[date]) -> Dict[str, List[date]]:
    """The days on which the two readings give a different state, with the direction of the change, and the days on which they agree.

    A state that is a hole under one reading and a number under the other differs; a number that becomes a hole is down.
    """

    out: Dict[str, List[date]] = {"differ": [], "up": [], "down": [], "agree": []}
    for day in sorted(days):
        old, new = average.get(day), level.get(day)
        if old == new:
            out["agree"].append(day)
            continue
        out["differ"].append(day)
        out["up" if new is not None and (old is None or new > old) else "down"].append(day)
    return out


def by_state(states: Mapping[date, Optional[float]], days: Sequence[date]) -> Dict[str, List[date]]:
    """The days grouped by their state (`"0"` to `"3"`), a hole (or a day with no state) under `"hole"`; empty groups are absent."""

    out: Dict[str, List[date]] = {}
    for day in sorted(days):
        state = states.get(day)
        out.setdefault("hole" if state is None else str(int(state)), []).append(day)
    return out


def verdict(row: Optional[dict]) -> str:
    """`gain` when a skill interval is above zero, `loss` when below, `undecided` otherwise (and for a group with no test)."""

    if not row or "skill_interval" not in row:
        return "undecided"
    lo, hi = row["skill_interval"]
    return "gain" if lo > 0.0 else "loss" if hi < 0.0 else "undecided"


# -- the states under both readings ----------------------------------------------------------------------------------


class Measurement:
    """The measurement panel built from the tracked snapshots twice: with the week average and with the Wednesday level."""

    def __init__(self):
        self.states: Dict[str, Dict[int, Dict[date, Optional[float]]]] = {}
        self.base: List[DailyObservation] = []
        self.alt: List[DailyObservation] = []
        self.onsets: List[date] = []
        self.movement: Dict[int, dict] = {}
        self.substitution: dict = {}
        self.published_sha256 = ""


def measure() -> Measurement:
    """The own-leg state of every scored day at each lead from the week average (as now) and from the Wednesday level."""

    declared = w970.committed_declaration()
    w970.refuse_locked([LAST_DAY])
    validation = w970._load("scarcity_validation")
    levels = {name: w970.read_levels(w970.SNAPSHOT / f"{name}.csv", declared["snapshot"]["files"][f"{name}.csv"]) for name in w970.PAIRS.values()}
    manifest = json.loads(validation.PUBLISHED_MANIFEST.read_text(encoding="utf-8"))
    artifacts = [
        load_snapshot_manifest(path)
        for root in validation.RAW_ROOTS
        for path in sorted((validation.SNAPSHOTS / root).glob("*/*.manifest.json"))
    ]
    cutoff = datetime.fromisoformat(manifest["build_cutoff"])
    decision = time.fromisoformat(manifest["decision_time"])
    retrieved = {artifact.sha256: artifact.retrieved_at for artifact in artifacts}
    columns = tuple(manifest["built_columns"]) + validation.EXTRA_COLUMNS
    out = Measurement()
    with tempfile.TemporaryDirectory() as tmp, measurement_declaration():
        long_path = Path(tmp) / "measurement_point_in_time.csv"
        snapshot = build_point_in_time_snapshot(artifacts, long_path, registry_path=w970.REGISTRY)
        original = load_point_in_time_panel(long_path)
        registry = load_source_registry(w970.REGISTRY)
        published = build_daily_panel(
            original, registry, build_cutoff=cutoff, decision_time=decision,
            columns=tuple(manifest["built_columns"]), snapshot_retrieved_at=retrieved,
        )
        panel_path = Path(tmp) / "published_columns.csv"
        write_daily_panel(published, panel_path, source_shas=snapshot.source_shas)
        out.published_sha256 = verify_daily_panel(panel_path, validation.PUBLISHED_MANIFEST)
        base = w970._panel_rows(original, registry, cutoff, decision, columns, retrieved)
        rows = list(original)
        out.substitution = {}
        for average, level in w970.PAIRS.items():
            rows, out.substitution[average] = w970.substitute(rows, average, levels[level])
        alt = w970._panel_rows(rows, registry, cutoff, decision, columns, retrieved)
        out.base, out.alt = list(base.observations), list(alt.observations)
        registry_dict = json.loads(w970.REGISTRY.read_text(encoding="utf-8"))
        for reading, observations in (("week_average", base.observations), ("wednesday_level", alt.observations)):
            out.states[reading] = {}
            for horizon in w970.HORIZONS:
                out.states[reading][horizon] = {
                    e.day: e.state for e in own_leg_states(
                        observations, registry=registry_dict, decision_time=decision,
                        minimum_history=w970.MINIMUM_HISTORY, horizon=horizon, end=LAST_DAY)
                }
        for horizon in w970.HORIZONS:
            m = w970.movement(out.states["week_average"][horizon], out.states["wednesday_level"][horizon])
            out.movement[horizon] = {k: v for k, v in m.items() if k != "changed_days"}
        days = sorted(out.states["week_average"][1])
        out.onsets = pressure.onsets(base.observations, w970.ONSET_BP, days)
    return out


# -- the frame -------------------------------------------------------------------------------------------------------


def build_frame(panel, wed_panel, splits, registry, first: Optional[date] = None):
    """The decision days with a forecast of the candidate (on both panels), B1, B1' and B2, whose five targets are scored days.

    `first` starts the walk later than the declared study does; it exists for the test of this script and the declared run never
    passes it.
    """

    frame = s686.Frame(panel, splits, registry, None)
    candidate_days = [
        day for i, day in enumerate(frame.dates)
        if i + max(sp.HORIZONS) < len(panel) and frame.dates[i + max(sp.HORIZONS)] <= LAST_DAY and (first is None or day >= first)
    ]
    s686.require_scored_days(candidate_days, LAST_DAY)
    variant = [v for v in fhs.VARIANTS if v.name == CANDIDATE]
    walk = fhs.walk(panel, candidate_days, variant, **frame.settings)
    walk_wed = fhs.walk(wed_panel, candidate_days, variant, **frame.settings)
    b1, b1p, b2, dropped = {}, {}, {}, []
    for day in walk.forecasts[CANDIDATE]:
        index = frame.position[day]
        try:
            one = pb.b1_forecast(panel, index, registry=registry, decision_time=DECISION_TIME)
            prime = b1c.b1_calendar_forecast(panel, index, **frame.settings)
            two = pb.b2_forecast(panel, index, **frame.settings)
        except (sp.ProtocolError, SplitError):
            dropped.append(day)
            continue
        b1[day], b1p[day], b2[day] = one, prime, two
    days = [d for d in walk.forecasts[CANDIDATE] if d in b1]
    frame.days = days
    frame.forecasts = {
        "B1": b1, B1P: b1p, "B2": b2, CANDIDATE: {d: walk.forecasts[CANDIDATE][d] for d in days},
    }
    frame.forecasts_wednesday = {d: walk_wed.forecasts[CANDIDATE][d] for d in days if d in walk_wed.forecasts[CANDIDATE]}
    notes = {
        "decision_days_offered": len(candidate_days), "candidate_skipped_for_history": len(walk.skipped),
        "benchmark_missing": [d.isoformat() for d in dropped], "scored_decision_days": len(days),
        "first": days[0].isoformat(), "last": days[-1].isoformat(),
        "last_target": frame.target(days[-1], max(sp.HORIZONS)).isoformat(), "refits": len(walk.fits),
    }
    return frame, notes


def cell_table(frame, forecasts) -> Dict[str, Dict[Tuple[date, int], float]]:
    """Both scores, the 90% interval hit and the two q95 hits of every (decision day, lead) cell, after the scored days are checked."""

    days = sorted(forecasts)
    cells = {(d, h): frame.target(d, h) for d in days for h in sp.HORIZONS}
    s686.require_scored_days(set(d for d, _ in cells) | set(cells.values()), LAST_DAY)
    out: Dict[str, Dict[Tuple[date, int], float]] = {m: {} for m in METRIC_NAMES + ("coverage_90", "hit_above")}
    for (d, h), t in cells.items():
        q, y = forecasts[d][h], frame.outcome[t]
        out["grid_crps"][(d, h)] = sp.grid_crps(q, y)
        out["upper_tail_twcrps"][(d, h)] = sp.upper_tail_twcrps(q, y)
        out["coverage_90"][(d, h)] = 1.0 if q[IDX[0.05]] <= y <= q[IDX[0.95]] else 0.0
        out["hit_above"][(d, h)] = 1.0 if y > q[Q95] else 0.0
    return out


def _mean(values: Sequence[float]) -> Optional[float]:
    return sum(values) / len(values) if values else None


def group_entry(frame, cells, series, days: Sequence[date], *, grain: str, draws: int) -> dict:
    """One group: its decision days, every model's mean score, the candidate's paired test against B1, B1' and B2 (from
    `MIN_GROUP_DAYS` days on), and the candidate's 90% coverage and q95 exceedance on the group's cells."""

    days = sorted(days)
    entry: dict = {"days": len(days)}
    members = set(days)
    for metric in METRIC_NAMES:
        ser = series[(grain, metric)]
        mean = {m: _mean([ser[m][d] for d in days if d in ser[m]]) for m in MODELS}
        row: dict = {"means": mean, "vs": {}}
        if len(days) >= MIN_GROUP_DAYS:
            row["vs"] = s761.run_pairs({b: ser[b] for b in BENCHMARKS}, ser[CANDIDATE], days, seed=SEED, draws=draws)
        else:
            row["too_few_days"] = True
        entry[metric] = row
    if grain.startswith("lead"):
        keys = [(d, int(grain[4:])) for d in days]
    elif grain == "decision":
        keys = [(d, h) for d in days for h in sp.HORIZONS]
    else:
        keys = [(d, h) for d in frame.days for h in sp.HORIZONS if frame.target(d, h) in members]
    entry["cells"] = len(keys)
    entry["coverage_90"] = _mean([cells[CANDIDATE]["coverage_90"][k] for k in keys])
    entry["q95_exceedance"] = _mean([cells[CANDIDATE]["hit_above"][k] for k in keys])
    return entry


def score(args) -> int:
    declaration = committed_declaration()
    panel_path = Path(args.panel)
    panel = load_daily_panel(panel_path)
    splits = load_split_declaration(SPLITS)
    registry = json.loads(SOURCES.read_text(encoding="utf-8"))
    published_sha = panel_sha256(panel_path)
    measurement = measure()

    base_reserves = {r.date: r.values.get(RESERVES) for r in measurement.base}
    if any(base_reserves.get(r.date) != r.values.get(RESERVES) for r in panel if r.date <= LAST_DAY):
        raise ValueError("the measurement panel's week-average reserves are not the published panel's")
    by_alt = {r.date: r for r in measurement.alt}
    if sorted(by_alt) != [r.date for r in panel]:
        raise ValueError("the Wednesday-level panel does not have the published panel's dates")
    wed_panel = wednesday_panel(panel, [by_alt[r.date] for r in panel])
    require_same_release([r for r in panel if r.date <= LAST_DAY], [r for r in wed_panel if r.date <= LAST_DAY])

    frame, notes = build_frame(panel, wed_panel, splits, registry, args.first)
    days = frame.days
    same = compare_forecasts(frame.forecasts[CANDIDATE], frame.forecasts_wednesday)
    cells = {m: cell_table(frame, frame.forecasts[m]) for m in MODELS}
    for m in MODELS:
        official = sp.day_scores(frame.forecasts[m], frame.outcome, frame.dates, score=sp.grid_crps)
        mean = s686.by_decision(cells[m]["grid_crps"])
        if set(official) != set(mean) or any(abs(official[d] - mean[d]) > 1e-9 for d in mean):
            raise SystemExit(f"grid CRPS of {m}: the cell means differ from scoring_protocol.day_scores")

    series: Dict[Tuple[str, str], Dict[str, Dict[date, float]]] = {}

    def need(grain: str) -> None:
        for metric in METRIC_NAMES:
            if (grain, metric) not in series:
                series[(grain, metric)] = {m: _series(frame, cells[m][metric], grain) for m in MODELS}

    groups: Dict[str, Dict[str, dict]] = {}
    for split, label, grain, members in s941.groups_of(frame):
        need(grain)
        groups.setdefault(split, {})[label] = group_entry(frame, cells, series, members, grain=grain, draws=args.draws)
    need("decision")
    state_of = {reading: measurement.states[reading][1] for reading in READINGS}
    for reading, split in READINGS.items():
        groups[split] = {
            label: group_entry(frame, cells, series, members, grain="decision", draws=args.draws)
            for label, members in sorted(by_state(state_of[reading], days).items())
        }
    parts = partition(state_of["week_average"], state_of["wednesday_level"], days)
    groups["readings"] = {
        label: group_entry(frame, cells, series, parts[label], grain="decision", draws=args.draws)
        for label in ("differ", "up", "down", "agree") if label in ("differ", "agree") or parts[label]
    }

    differ = parts["differ"]
    first_target = {d: frame.target(d, 1) for d in days}
    by_regime: Dict[str, List[date]] = {}
    by_type: Dict[str, List[date]] = {}
    for d in differ:
        by_regime.setdefault(frame.regime(d), []).append(d)
        by_type.setdefault(frame.day_type(first_target[d]), []).append(d)
    ser = series[("decision", "grid_crps")]

    def brief(members):
        return {
            "days": len(members), "up": sum(d in set(parts["up"]) for d in members), "down": sum(d in set(parts["down"]) for d in members),
            "grid_crps": {m: _mean([ser[m][d] for d in members]) for m in MODELS},
        }

    onsets = list(measurement.onsets)
    result = {
        "issue": 1146, "declaration": str(DECLARATION.relative_to(REPO)), "panel_sha256": published_sha,
        "measurement_panel_published_columns_sha256": measurement.published_sha256,
        "subset_from": None if args.first is None else args.first.isoformat(), "label": "development, not a verdict",
        "seed": SEED, "draws": args.draws, "notes": notes, "models": list(MODELS), "candidate": CANDIDATE,
        "substitution": measurement.substitution,
        "candidate_under_both_readings": same,
        "state_movement": {str(h): m for h, m in measurement.movement.items()},
        "state_days_in_frame": {
            "scored_decision_days": len(days), "without_a_state": sum(1 for d in days if state_of["week_average"].get(d) is None),
            "differ": len(differ), "up": len(parts["up"]), "down": len(parts["down"]),
            "differ_days": [[d.isoformat(), state_of["week_average"].get(d), state_of["wednesday_level"].get(d)] for d in differ],
        },
        "lead_dependence": {
            reading: sum(1 for d in days if len({measurement.states[reading][h].get(d) for h in w970.HORIZONS if d in measurement.states[reading][h]}) > 1)
            for reading in READINGS
        },
        "groups": groups,
        "differ_by_regime": {k: brief(v) for k, v in sorted(by_regime.items())},
        "differ_by_day_type": {k: brief(v) for k, v in sorted(by_type.items())},
        "onsets": {
            "threshold_bp": w970.ONSET_BP, "n": len(onsets),
            "changed": [[d.isoformat(), state_of["week_average"].get(d), state_of["wednesday_level"].get(d)]
                        for d in onsets if state_of["week_average"].get(d) != state_of["wednesday_level"].get(d)],
        },
        "reading_rules": declaration["reading_rule"],
    }
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    Path(args.output).write_text(json.dumps(result, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    return 0


def _series(frame, cells, grain: str) -> Dict[date, float]:
    if grain == "decision":
        return s686.by_decision(cells)
    if grain == "target":
        return s686.by_target(frame, cells)
    return s686.by_lead(cells, int(grain[4:]))


# -- the page --------------------------------------------------------------------------------------------------------

pct = s761.pct


def skill_text(row: Optional[dict]) -> str:
    if not row:
        return "n/a"
    return s761.skill_text(row)


def _model_label(m: str) -> str:
    return {B1P: "B1' (#960)", CANDIDATE: "H5 candidate (#941 mad 20, floor 0.5)"}.get(m, m)


def _group_rows(groups: Mapping[str, dict], metric: str, *, split_name: str) -> List[str]:
    out = [f"| {split_name} | days | cells | candidate | B1 | B1' | B2 | skill vs B1 [90%] | vs B1' | vs B2 | 90% coverage | q95 exceedance |",
           "|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for label, g in groups.items():
        row = g[metric]
        mean = row["means"]
        vs = row["vs"]
        cov = "n/a" if g["coverage_90"] is None else f"{g['coverage_90']:.3f}"
        q95 = "n/a" if g["q95_exceedance"] is None else f"{g['q95_exceedance']:.3f}"

        def f(x):
            return "n/a" if x is None else f"{x:.3f}"

        out.append(
            f"| {label} | {g['days']} | {g['cells']} | {f(mean[CANDIDATE])} | {f(mean['B1'])} | {f(mean[B1P])} | {f(mean['B2'])} | "
            f"{skill_text(vs.get('B1')) if vs else 'fewer than 20 days'} | {skill_text(vs.get(B1P)) if vs else ''} | "
            f"{skill_text(vs.get('B2')) if vs else ''} | {cov} | {q95} |"
        )
    return out


def render(r: dict) -> str:
    same = r["candidate_under_both_readings"]
    mv = r["state_movement"]
    fd = r["state_days_in_frame"]
    out: List[str] = []
    w = out.append
    w("# The Wednesday reserve level as a candidate scarcity input (#1146)")
    w("")
    w("**Hypothesis and step:** H5 (primary goal), step 3, the scarcity input. **Development data, not a verdict** (scoring protocol v1, #640): "
      "days to 2025-12-31, no lockbox day. Nothing is adopted, nothing is registered and no claim changes. Generated by "
      "`scripts/wednesday_scarcity_1146.py page` from `docs/research/wednesday-scarcity-1146/result.json`, not edited by hand; declared in "
      "`metadata/wednesday_scarcity_1146.json` before any number.")
    w("")
    w(f"Ruling: Eleonora, 22 October 2026, option 2 on #1143. The scarcity state is formed from the Wednesday level (`WRBWFRBL`, the same H.4.1 "
      f"release and instant as `WRESBAL`) as a separate candidate input beside the week average (`WRESBAL`, as now). The published declaration and "
      f"`metadata/sources.json` do not move. Panel digest `{r['panel_sha256'][:8]}…`. Studentized stationary bootstrap (ruling 1), mean block 10 "
      f"business days, {r['draws']:,} draws, seed {r['seed']}, two-sided 90% interval; skill is `mean(d) / mean(S(benchmark))` with "
      f"`d = S(benchmark) - S(candidate)`, positive favours the candidate. Scored decision days: {r['notes']['scored_decision_days']:,} "
      f"({r['notes']['first']} to {r['notes']['last']}). B1' (Lens C's calendar-aware persistence, #960) is reported beside B1; B1 stays the protocol's benchmark.")
    w("")
    w("## What the candidate reads")
    w("")
    w("The H5 candidate (#941's scaled mean reversion) does not read the scarcity state. Its inputs are the spread series: `repo_model.spread_mr_fhs` "
      "says \"no regime label and no other column is an input\". So running it \"with each reading\" cannot move a forecast, and this page shows "
      "that by running it, not by assuming it. The candidate was walked on the published panel, and on the same panel with `reserve_balances` replaced "
      "by the Wednesday level; every quantile of every cell was compared.")
    w("")
    w("| | cells (decision day, lead) | identical on both panels | largest absolute difference of any quantile (bp) |")
    w("|---|---|---|---|")
    w(f"| candidate, week average against Wednesday level | {same['cells']:,} | {same['identical']:,} | {same['max_abs_difference']:.6f} |")
    w("")
    w("The reading of the state therefore changes no score of this candidate. The part of the comparison that can move is the state itself, which "
      "a model that read it would act on. The rest of the page measures that: the state under each reading, the candidate's scores split by it, and "
      "its scores on the days where the readings differ. #1145's state-scaled arms are not merged (the ruling asks for them \"if merged by then\"); "
      "its arm (s2) is the first that reads the scarcity state, and the script takes the arms as data.")
    w("")
    w("## The state under each reading")
    w("")
    w(f"The own-leg state (#586: each leg at its own latest public row; cut-points, H.8 leg and ON RRP leg unchanged), from the week average and from the "
      f"Wednesday level, on every scored day to 2025-12-31 (as #970's page, reproduced here), and on the {fd['scored_decision_days']:,} decision days "
      f"the candidate is scored on.")
    w("")
    w("| lead | scored days | change state | up | down | enter risky set | leave risky set |")
    w("|---|---|---|---|---|---|---|")
    for h in sorted(mv):
        m = mv[h]
        w(f"| {h} | {m['days']:,} | {m['changed']} | {m['up']} | {m['down']} | {m['enter_risky_set']} | {m['leave_risky_set']} |")
    w("")
    w(f"On the candidate's decision days the readings differ on {fd['differ']} ({fd['up']} up, {fd['down']} down) at lead 1; "
      f"{fd['without_a_state']} of the days have no state under the week average (a leg is a hole). The state of a day depends on the lead on "
      f"{r['lead_dependence']['week_average']} days under the week average and {r['lead_dependence']['wednesday_level']} under the Wednesday level; the groups below use the lead-1 state.")
    w("")
    onsets = r["onsets"]
    w(f"Pressure onsets (> {onsets['threshold_bp']:.0f} bp, a descriptive list and not a decision rule): {onsets['n']}; the state changes at {len(onsets['changed'])}.")
    w("")
    if r["differ_by_regime"]:
        w("The days where the readings differ, by regime of the decision day, and the candidate's grid CRPS on them (bp, mean over leads 1 to 5):")
        w("")
        w("| regime | days | up | down | candidate | B1 | B1' | B2 |")
        w("|---|---|---|---|---|---|---|---|")
        for k, v in r["differ_by_regime"].items():
            g = v["grid_crps"]
            w(f"| {k} | {v['days']} | {v['up']} | {v['down']} | {g[CANDIDATE]:.3f} | {g['B1']:.3f} | {g[B1P]:.3f} | {g['B2']:.3f} |")
        w("")
        w("By the pressure-day type of the lead-1 target day:")
        w("")
        w("| day type | days | up | down | candidate | B1 | B1' | B2 |")
        w("|---|---|---|---|---|---|---|---|")
        for k, v in r["differ_by_day_type"].items():
            g = v["grid_crps"]
            w(f"| {k} | {v['days']} | {v['up']} | {v['down']} | {g[CANDIDATE]:.3f} | {g['B1']:.3f} | {g[B1P]:.3f} | {g['B2']:.3f} |")
        w("")
    for metric, title in (("grid_crps", "Grid CRPS (23 levels)"), ("upper_tail_twcrps", "Upper-tail twCRPS (weight 1{z > 0 bp})")):
        w(f"## {title}, mean over leads 1 to 5 (bp)")
        w("")
        w("### Pooled, and by lead")
        w("")
        pooled = {"all decision days": r["groups"]["pooled"]["all decision days"], **r["groups"]["lead"]}
        w("\n".join(_group_rows(pooled, metric, split_name="group")))
        w("")
        w("### By state, under each reading")
        w("")
        w("The candidate is the same under both readings (above), so a difference between the two tables below is a difference in how the state sorts the days, not in a forecast.")
        w("")
        for reading, split in READINGS.items():
            if r["groups"].get(split):
                w(f"**{reading.replace('_', ' ')}**")
                w("")
                w("\n".join(_group_rows(r["groups"][split], metric, split_name="state")))
                w("")
        w("### Where the readings differ, and where they agree")
        w("")
        w("\n".join(_group_rows(r["groups"]["readings"], metric, split_name="readings")))
        w("")
        w("### By regime and pressure-day type (the candidate does not depend on the reading)")
        w("")
        for split in ("regime", "pressure_day_type"):
            if r["groups"].get(split):
                w("\n".join(_group_rows(r["groups"][split], metric, split_name=split.replace("_", " "))))
                w("")
    w("## Reading")
    w("")
    w("- The candidate's forecasts are identical under the two readings on every cell (the first table). With this candidate there is nothing to score "
      "prospectively under the Wednesday level, and a registration of it would register the same forecasts twice.")
    w("- The Wednesday level moves the state on a few dozen of the scored days and on none of the pressure onsets (reproducing #970). No state is called better here.")
    w("- Groups with fewer than 20 decision days carry counts and means only; their intervals are not computed.")
    w("- A figure here is paired and carries an interval where the group allows it, and is split by regime and pressure-day type; a pooled figure alone is not a result.")
    w("")
    w("## Not checked")
    w("")
    w("- **Never revised.** `WRBWFRBL` is the latest FRED vintage; its never-revised status is not re-verified. The check is a short run on Eleonora's Mac "
      "(`scripts/alfred_wednesday_1146.py`, pasted from the `needs-mac:` comment on the pull request).")
    w("- **A model that reads the state.** Neither #1145's arms nor any gradient-boosted model is run under the two readings; the candidate does not read the state.")
    w("- **Calendar first.** The candidate reads no calendar column, so its scores here are provisional under the calendar-first rule "
      "(`docs/research/provisional-calendar-register.md`); this page is not a calendar question and the rule changes none of the counts above.")
    w("")
    w("## Question for Eleonora")
    w("")
    w("The candidate does not read the scarcity state, so the Wednesday level has nothing to act on yet. Nothing is adopted here, nothing is registered and "
      "no claim changes. The registration text is a draft in `docs/decisions/drafts/wednesday-scarcity-registration-1146.md`; registering is your own action.")
    w("")
    w("1. **Wait for a model that reads the state (default).** Keep the candidate as it is. When #1145's arm (s2) merges, run it under each reading in a follow-up "
      "directive; the registration stays a draft until then.")
    w("2. **Ask for a probe now.** A development arm of the candidate that reads the as-of scarcity state (you choose how: location, scale or the residual pool), "
      "declared before any score and run under both readings, so the Wednesday level gets a first test before #1145.")
    w("3. **Register the Wednesday-level reading now for the current candidate.** Not recommended: the forecasts are identical, so prospective days would add no information.")
    return "\n".join(out) + "\n"


def page(args) -> int:
    result = json.loads(Path(args.score).read_text(encoding="utf-8"))
    Path(args.output).write_text(render(result), encoding="utf-8")
    return 0


@turn_days.with_legacy_flag
def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="command", required=True)
    s = sub.add_parser("score", help="run the candidate with each reading of the state and split its scores by the state")
    s.add_argument("--panel", required=True)
    s.add_argument("--output", required=True)
    s.add_argument("--draws", type=int, default=sp.DRAWS)
    s.add_argument("--first", type=date.fromisoformat, default=None, help="start the walk later (the test of this script only)")
    s.set_defaults(func=score)
    p = sub.add_parser("page", help="write the Markdown page from a score file")
    p.add_argument("--score", required=True)
    p.add_argument("--output", required=True)
    p.set_defaults(func=page)
    args = parser.parse_args(argv)
    return int(args.func(args) or 0)


if __name__ == "__main__":
    raise SystemExit(main())
