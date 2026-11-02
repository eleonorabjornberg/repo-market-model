"""Does the H5 candidate (s3c-ann-net) see the Wednesday reserve level? (#1146; H5 step 3, scarcity input; Eleonora's ruling of 2 November 2026.)

A development check, never a verdict. It writes JSON and Markdown to the paths it is given and nothing into `docs/runs/`. The first run of #1146
(`scripts/wednesday_scarcity_1146.py`, its record and page, kept as they are) walked #941's scaled mean reversion, which reads only the spread series,
so both readings of the scarcity state gave identical forecasts. The H5 candidate is now (s3c-ann-net) (`docs/research/h5-candidate.json`), and her
ruling of 2 November 2026 asks, before any arm is scored, whether its forecast reads `reserve_balances` (directly or through the scarcity state) at
each lead, and on how many decision days the Wednesday level changes what it reads. If it cannot see the change, the page says so with the evidence
and stops, rather than scoring a no-op. The declaration is `metadata/wednesday_scarcity_1146.json`, `amendments`, committed before any figure.

How the question is answered. (s3c-ann-net) is walked with #1288's own walk (`ANN_NET_ARM` on the announced terms and the announced net sizes, the
state held at its maximum by `s3c_net.constant_states`, direct pairs) and #1255's cap at the Standing Repo Facility line, at the 18:00 decision
instant in force, on three panels: the published panel, the published panel with `reserve_balances` replaced by the Wednesday level (the
substitution of `wednesday_scarcity_1146.py`), and, for the walks themselves, rows that count every lookup of `reserve_balances` while the forecast
code runs (`TrappedValues`). Every quantile of every cell is compared. A control that does read the state, (s2) of #1145 with the as-of states of
the two readings, is walked the same way, so that the comparison is shown able to see a difference where there is one.

Decision days are those whose five targets are on or before 2025-12-31 (the Wednesday-level snapshot ends there); no later day is read and no locked
day is scored (`docs/decisions/lockbox.md`). The walks take a few minutes each. Commands, from a clone of the branch:

    PYTHONPATH=src python3 -m repo_model.cli build --raw-root tests/fixtures/snapshots/funding_inputs \\
        --output PUB.csv --build-cutoff 2026-09-08T21:31:42+00:00 --decision-time 18:00:00
    PYTHONPATH=src python3 -m repo_model.cli verify-panel PUB.csv --manifest metadata/funding_panel_manifest.json
    RMM_DECISION_TIME=18:00 PYTHONPATH=src python3 scripts/wednesday_candidate_check_1146.py check --panel PUB.csv \\
        --output docs/research/wednesday-candidate-check-1146/result.json
    PYTHONPATH=src python3 scripts/wednesday_candidate_check_1146.py page \\
        --check docs/research/wednesday-candidate-check-1146/result.json --output docs/research/wednesday-candidate-check-1146-result.md

Stdlib only.
"""

from __future__ import annotations

import argparse
import contextlib
import importlib.util
import json
import sys
from datetime import date, time
from pathlib import Path
from typing import Dict, Iterator, List, Mapping, Optional, Sequence, Tuple

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))


def _load(name: str, alias: Optional[str] = None):
    alias = alias or name
    spec = importlib.util.spec_from_file_location(alias, REPO / "scripts" / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[alias] = module
    spec.loader.exec_module(module)
    return module


from repo_model import announced_iorb, s3c_announced, s3c_net  # noqa: E402
from repo_model import scoring_protocol as sp, spread_mr_calendar as cal, spread_mr_state_calendar as sc  # noqa: E402
from repo_model import turn_days  # noqa: E402
from repo_model.baseline import panel_sha256  # noqa: E402
from repo_model.data import DailyObservation, load_daily_panel  # noqa: E402
from repo_model.evaluation_splits import load_split_declaration  # noqa: E402

w1146 = _load("wednesday_scarcity_1146", "wednesday_scarcity_1146_in_check_1146")
m1288 = _load("s3c_announced_settlement_1288", "s3c_announced_settlement_1288_in_check_1146")
m1255, k, c = m1288.m1255, m1288.k, m1288.c

DECLARATION = w1146.DECLARATION
LAST_DAY = w1146.LAST_DAY
RESERVES = w1146.RESERVES
INSTANT = time(18, 0)
CANDIDATE = "sc_s3c_ann_net"
CANDIDATE_LABEL = "(s3c-ann-net)"
CONTROL = sc.ARMS[1]
READINGS = ("week_average", "wednesday_level")
LEADS = tuple(sp.HORIZONS)
RECORD_PATH = ("windows", "development", "groups", "pooled", "all decision days", "grid_crps", "means", CANDIDATE)
RECORD_1800 = REPO / "docs" / "research" / "s3c-ann-net-1800-1314" / "announced-settlement-1800.json"


# -- the trap ---------------------------------------------------------------------------------------------------------------------


class Trap:
    """Counts of what the forecast code does with the guarded column while `armed`: `lookups` (a read of that key) and `bulk` (a read of every key)."""

    def __init__(self) -> None:
        self.is_armed = False
        self.lookups = 0
        self.bulk = 0

    @contextlib.contextmanager
    def armed(self) -> Iterator["Trap"]:
        self.is_armed = True
        try:
            yield self
        finally:
            self.is_armed = False


class TrappedValues(dict):
    """A row's values that count a read of `reserve_balances` (`__getitem__`, `get`, `in`) and, apart, a read of every key (`items`, `values`, `keys`).

    `__iter__` is not overridden, so `dict(values)` (a copy of the row, which `fomc_calendar.add_columns` makes of every row) takes the C fast path and counts
    nothing, and the copy is a plain dict. A read through a copy is therefore not counted; the poisoned panels (`poison`) are what shows that no copy's
    `reserve_balances` reaches a forecast.

    Mutation record: see `tests/test_wednesday_candidate_check_1146.py` (`TrappedValues.__getitem__`).
    """

    def __init__(self, values: Mapping[str, Optional[float]], trap: Trap, column: str = RESERVES) -> None:
        super().__init__(values)
        self._trap, self._column = trap, column

    def __getitem__(self, key):
        if self._trap.is_armed and key == self._column:
            self._trap.lookups += 1
        return super().__getitem__(key)

    def get(self, key, default=None):
        if self._trap.is_armed and key == self._column:
            self._trap.lookups += 1
        return super().get(key, default)

    def __contains__(self, key):
        if self._trap.is_armed and key == self._column:
            self._trap.lookups += 1
        return super().__contains__(key)

    def _bulk(self) -> None:
        if self._trap.is_armed:
            self._trap.bulk += 1

    def items(self):
        self._bulk()
        return super().items()

    def values(self):
        self._bulk()
        return super().values()

    def keys(self):
        self._bulk()
        return super().keys()


def trapped_panel(panel: Sequence[DailyObservation]) -> Tuple[List[DailyObservation], Trap]:
    """The same rows with values that count reads of `reserve_balances`; the dates and the values are the rows' own."""

    trap = Trap()
    return [DailyObservation(row.date, TrappedValues(row.values, trap)) for row in panel], trap


POISONS = ("wild", "hole")


def poison(panel: Sequence[DailyObservation], kind: str) -> List[DailyObservation]:
    """The rows with `reserve_balances` replaced by a value no reading could take (`wild`: 1e9 plus 1e6 a row) or by a hole (`hole`).

    Raises:
        ValueError: an unknown kind.
    """

    if kind not in POISONS:
        raise ValueError(f"poison kind {kind!r}: one of {POISONS}")
    out = []
    for i, row in enumerate(panel):
        values = dict(row.values)
        values[RESERVES] = 1.0e9 + 1.0e6 * i if kind == "wild" else None
        out.append(DailyObservation(row.date, values))
    return out


def decide(*, lookups: int, identical: int, cells: int, state_values: Sequence[float]) -> str:
    """`can_see` when the forecast looked up the column, moved with the reading, or read a state that varies; `cannot_see` otherwise.

    Raises:
        ValueError: no cell was compared.
    """

    if cells < 1:
        raise ValueError("no cell was compared")
    if lookups > 0 or identical != cells or len(set(state_values)) > 1:
        return "can_see"
    return "cannot_see"


def require_instant(decision_time: time, *, allow_other: bool = False) -> None:
    """Refuse to run at another decision instant than the one in force (18:00, `repo_model.decision_instant`); the test of this script may allow it.

    Raises:
        ValueError: the family's instant (`RMM_DECISION_TIME`, default 16:00) is not 18:00.
    """

    if decision_time != INSTANT and not allow_other:
        raise ValueError(f"the check is made at {INSTANT:%H:%M}, the decision instant in force; set RMM_DECISION_TIME=18:00 (got {decision_time:%H:%M})")


# -- the walks --------------------------------------------------------------------------------------------------------------------


def decision_days(panel: Sequence[DailyObservation], first: Optional[date]) -> List[date]:
    """Every panel day whose five targets are on or before `LAST_DAY` (from `first` on, for the test of this script only)."""

    dates = [row.date for row in panel]
    days = [
        day for i, day in enumerate(dates)
        if i + max(LEADS) < len(dates) and dates[i + max(LEADS)] <= LAST_DAY and (first is None or day >= first)
    ]
    w1146.s686.require_scored_days(days, LAST_DAY)
    return days


def candidate_walk(panel, days, splits, registry, register, results, auctions):
    """(s3c-ann-net) as #1288 walks it (`extra_walks`, "ann", its arm alone) and #1255 caps it: `(forecasts, walk)`.

    The tables are built from `panel`, so a trapped panel also covers the announced terms and the net sizes.
    """

    settings = dict(registry=registry, decision_time=k.DECISION_TIME, splits=splits)
    states = s3c_net.constant_states(panel)
    iorb = announced_iorb.load_announcements(c.IORB_TABLE)
    both = s3c_announced.AnnouncedTermTable(panel, iorb, results, decision_time=k.DECISION_TIME)
    net_table = s3c_announced.AnnouncedNetSizeTable(panel, auctions, decision_time=k.DECISION_TIME)
    walk = sc.walk(panel, days, both, states, (s3c_announced.ANN_NET_ARM,), sizes=net_table, **settings)
    raw = walk.forecasts[s3c_announced.ANN_NET_ARM.name]
    dates = [row.date for row in panel]
    position = {d: i for i, d in enumerate(dates)}
    capped = {
        d: {h: m1255.s3c_candidate.capped_quantiles(q, register, k.decision_instant(d), dates[position[d] + h]) for h, q in per.items()}
        for d, per in raw.items()
    }
    return capped, walk


def control_walk(panel, days, splits, registry, table, states):
    """(s2) of #1145, which reads the scarcity state, on `panel` with `states` (keyed by decision day)."""

    settings = dict(registry=registry, decision_time=k.DECISION_TIME, splits=splits)
    return sc.walk(panel, days, table, states, (CONTROL,), **settings)


def decision_keyed(grid: Mapping[date, Optional[float]], dates: Sequence[date]) -> Dict[date, Optional[float]]:
    """The state a decision on each panel day could read: the horizon-1 grid, keyed by the scored day, shifted to the decision day before it."""

    return {dates[i]: grid.get(dates[i + 1]) for i in range(len(dates) - 1)}


def mean_grid_crps(forecasts, panel, days) -> float:
    outcome = {row.date: row.spread_bps for row in panel if row.date <= LAST_DAY}
    scores = sp.day_scores(forecasts, outcome, [row.date for row in panel], score=sp.grid_crps)
    return sum(scores[d] for d in days) / len(days)


# -- the check --------------------------------------------------------------------------------------------------------------------


def check(args) -> int:
    declaration = w1146.committed_declaration()
    amended = [a for a in declaration.get("amendments", []) if a["candidate"] == CANDIDATE]
    if len(amended) != 1:
        raise ValueError("the declaration has no amendment for (s3c-ann-net): declare the check before running it")
    require_instant(k.DECISION_TIME, allow_other=args.any_instant)
    panel_path = Path(args.panel)
    published = [row for row in load_daily_panel(panel_path)]
    splits = load_split_declaration(c.SPLITS)
    registry = json.loads(c.SOURCES.read_text(encoding="utf-8"))
    register = m1255.policy_events.load_register()
    auctions = m1288.m1273.load_auctions()
    results = m1288.load_results()
    table = cal.TermTable(published, announced_iorb.load_announcements(c.IORB_TABLE), decision_time=c.DECISION_TIME)

    measurement = w1146.measure()
    base_reserves = {r.date: r.values.get(RESERVES) for r in measurement.base}
    if any(base_reserves.get(r.date) != r.values.get(RESERVES) for r in published if r.date <= LAST_DAY):
        raise ValueError("the measurement panel's week-average reserves are not the published panel's")
    by_alt = {r.date: r for r in measurement.alt}
    if sorted(by_alt) != [r.date for r in published]:
        raise ValueError("the Wednesday-level panel does not have the published panel's dates")
    wednesday = w1146.wednesday_panel(published, [by_alt[r.date] for r in published])
    w1146.require_same_release([r for r in published if r.date <= LAST_DAY], [r for r in wednesday if r.date <= LAST_DAY])

    days = decision_days(published, args.first)
    out: dict = {
        "issue": 1146, "declaration": str(DECLARATION.relative_to(REPO)), "panel_sha256": panel_sha256(panel_path),
        "measurement_panel_published_columns_sha256": measurement.published_sha256, "label": "development, not a verdict",
        "subset_from": None if args.first is None else args.first.isoformat(), "candidate_name": CANDIDATE, "instant": k.DECISION_TIME.isoformat(timespec="minutes"),
        "reading_rule": declaration["reading_rule"], "substitution": measurement.substitution,
    }

    # the candidate, on both panels, on rows that count the reads of the reserve column
    forecasts: Dict[str, dict] = {}
    candidate: Dict[str, dict] = {}
    for reading, rows in (("week_average", published), ("wednesday_level", wednesday)):
        panel, trap = trapped_panel(rows)
        with trap.armed():
            found, walk = candidate_walk(panel, days, splits, registry, register, results, auctions)
        read = sorted({detail["state"] for detail in walk.detail.values() if detail.get("state") is not None})
        forecasts[reading] = found
        candidate[reading] = {"lookups": trap.lookups, "bulk_reads": trap.bulk, "refits": len(walk.fits), "forecast_days": len(found),
                              "skipped": len(walk.skipped), "state_values_read": read,
                              "days_with_unknown_state": sum(1 for d in walk.detail.values() if d.get("state") is None)}
    compared = w1146.compare_forecasts(forecasts["week_average"], forecasts["wednesday_level"])
    # the poisoned panels: if no copy of the column reaches a forecast, a value no reading could take moves nothing either
    poisoned: Dict[str, dict] = {}
    for kind in POISONS:
        try:
            found, _walk = candidate_walk(poison(published, kind), days, splits, registry, register, results, auctions)
            poisoned[kind] = w1146.compare_forecasts(forecasts["week_average"], found)
        except Exception as error:  # a walk that fails on the poisoned column reads it
            poisoned[kind] = {"cells": 0, "identical": 0, "max_abs_difference": None, "error": f"{type(error).__name__}: {error}"}
    candidate["poisoned"] = poisoned
    values = sorted(set(candidate["week_average"]["state_values_read"]) | set(candidate["wednesday_level"]["state_values_read"]))
    candidate.update(compared=compared, state_values_read=values)
    scored_days = sorted(forecasts["week_average"])
    candidate["grid_crps_mean_week_average"] = mean_grid_crps(forecasts["week_average"], published, scored_days)
    if args.first is None and RECORD_1800.exists():
        record = json.loads(RECORD_1800.read_text(encoding="utf-8"))
        for key in RECORD_PATH:
            record = record[key]
        candidate["grid_crps_mean_record_1314"] = record
        candidate["grid_crps_mean_matches_record"] = abs(record - candidate["grid_crps_mean_week_average"]) < 1e-9
    out["candidate"] = candidate
    every = [compared] + [p for p in poisoned.values() if "error" not in p]
    errors = [p for p in poisoned.values() if "error" in p]
    out["answer"] = decide(
        lookups=candidate["week_average"]["lookups"] + candidate["wednesday_level"]["lookups"] + len(errors),
        identical=sum(p["identical"] for p in every), cells=sum(p["cells"] for p in every), state_values=values,
    )

    # where the state differs: the own-leg state of each lead under the two readings, on the decision days
    state_of = {reading: measurement.states[reading] for reading in READINGS}
    out["decision_days_state_differs"] = {}
    differing: set = set()
    for h in LEADS:
        parts = w1146.partition(state_of["week_average"][h], state_of["wednesday_level"][h], scored_days)
        differing.update(parts["differ"])
        out["decision_days_state_differs"][str(h)] = {
            "scored_decision_days": len(scored_days), "differ": len(parts["differ"]), "up": len(parts["up"]), "down": len(parts["down"]),
            "differ_days": [d.isoformat() for d in parts["differ"]],
        }
    out["decision_days_state_differs_at_any_lead"] = len(differing)
    out["decision_days_candidate_forecast_moves"] = sum(
        1 for d in scored_days if any(forecasts["week_average"][d][h] != forecasts["wednesday_level"][d][h] for h in forecasts["week_average"][d])
    )

    # the control: (s2), which reads the state at the decision, with the as-of states of the two readings
    dates = [row.date for row in published]
    control: Dict[str, dict] = {}
    control_forecasts = {}
    for reading, rows in (("week_average", published), ("wednesday_level", wednesday)):
        states = decision_keyed(state_of[reading][1], dates)
        walk = control_walk(rows, days, splits, registry, table, states)
        control_forecasts[reading] = walk.forecasts[CONTROL.name]
        control[reading] = {"refits": len(walk.fits), "forecast_days": len(control_forecasts[reading])}
    moved = w1146.compare_forecasts(control_forecasts["week_average"], control_forecasts["wednesday_level"])
    moved_days = sorted(d for d in control_forecasts["week_average"]
                        if any(control_forecasts["week_average"][d][h] != control_forecasts["wednesday_level"][d][h] for h in LEADS))
    control.update(
        arm=CONTROL.name, cells=moved["cells"], compared=moved, days_moved=len(moved_days),
        state_differs_on_decision_day=sum(
            1 for d in control_forecasts["week_average"]
            if decision_keyed(state_of["week_average"][1], dates).get(d) != decision_keyed(state_of["wednesday_level"][1], dates).get(d)
        ),
    )
    out["control"] = control
    out["notes"] = {"first": days[0].isoformat(), "last": days[-1].isoformat(), "decision_days_offered": len(days),
                    "scored_decision_days": len(scored_days), "last_target": LAST_DAY.isoformat()}
    out["last_target_is_a_development_day"] = LAST_DAY.isoformat()
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    Path(args.output).write_text(json.dumps(out, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    return 0


# -- the page ---------------------------------------------------------------------------------------------------------------------


def render(r: dict) -> str:
    cand, ctl, n = r["candidate"], r["control"], r["notes"]
    cmp_ = cand["compared"]
    out: List[str] = []
    w = out.append
    w("# Does the H5 candidate see the Wednesday reserve level? (#1146)")
    w("")
    w("**Hypothesis and step:** H5 (primary goal), step 3, the scarcity input. **Development data, not a verdict** (scoring protocol v1, #640): "
      f"decision days whose targets fall on or before {n['last_target']}, no lockbox day. Nothing is adopted, nothing is registered, the candidate does not change "
      "and no claim changes. Generated by `scripts/wednesday_candidate_check_1146.py page` from "
      "`docs/research/wednesday-candidate-check-1146/result.json`, not edited by hand; declared in `metadata/wednesday_scarcity_1146.json` (`amendments`) before any figure.")
    w("")
    w(f"Ruling: Eleonora, 2 November 2026 (chat, relayed): test the Wednesday reading on the current candidate, {CANDIDATE_LABEL} "
      "(`docs/research/h5-candidate.json`), at the 18:00 decision instant in force. Check first whether its forecast reads `reserve_balances` (directly or through the "
      "scarcity state) at each lead, and on how many decision days the Wednesday level changes what it reads. If the candidate cannot see the change, say so with the "
      "evidence and stop, rather than score a no-op. The first run of #1146 (its page and record, unchanged) walked #941's scaled mean reversion and is the record of what "
      f"was run on #941. Panel digest `{r['panel_sha256'][:8]}…`. Instant {r['instant']}.")
    w("")
    w("## The answer")
    w("")
    if r["answer"] == "cannot_see":
        w(f"**{CANDIDATE_LABEL} cannot see the change.** On the published panel and on the same panel with `reserve_balances` replaced by the Wednesday level, its "
          "forecast is the same, quantile for quantile, in every cell, and so it is when the column is replaced by a value no reading could take or by a hole; the forecast code "
          "never looks the column up on the panel's own rows; and the scarcity state it reads is one value on every decision day. **No arm is scored.** Scoring the Wednesday reading of this candidate would score a no-op: every table would be the candidate's own, twice.")
    else:
        w(f"**{CANDIDATE_LABEL} can see the change.** The evidence below is the reason; the arm is declared and scored under the amendment's second branch.")
    w("")
    w("| | week average (as now) | Wednesday level |")
    w("|---|---|---|")
    w(f"| direct lookups of `reserve_balances` on the panel's rows while the forecast code ran | {cand['week_average']['lookups']:,} | {cand['wednesday_level']['lookups']:,} |")
    w(f"| whole-row reads (every key; not a read of the column by itself) | {cand['week_average']['bulk_reads']:,} | {cand['wednesday_level']['bulk_reads']:,} |")
    w(f"| refits | {cand['week_average']['refits']:,} | {cand['wednesday_level']['refits']:,} |")
    w(f"| decision days with a forecast | {cand['week_average']['forecast_days']:,} | {cand['wednesday_level']['forecast_days']:,} |")
    w(f"| scarcity state read by the fit or the forecast | {', '.join(f'{v:g}' for v in cand['week_average']['state_values_read'])} | "
      f"{', '.join(f'{v:g}' for v in cand['wednesday_level']['state_values_read'])} |")
    w("")
    w("| | cells (decision day, lead) | identical on both panels | largest absolute difference of any quantile (bp) |")
    w("|---|---|---|---|")
    w(f"| {CANDIDATE_LABEL}, week average against Wednesday level | {cmp_['cells']:,} | {cmp_['identical']:,} | {cmp_['max_abs_difference']:.6f} |")
    w("")
    w("The same walk with the column replaced by a value no reading could take, compared with the week-average walk:")
    w("")
    w("| `reserve_balances` replaced by | cells | identical | largest absolute difference (bp) |")
    w("|---|---|---|---|")
    for kind, text in (("wild", "1e9 plus 1e6 a row"), ("hole", "a hole on every row")):
        p = cand["poisoned"][kind]
        if "error" in p:
            w(f"| {text} | the walk raised | | {p['error']} |")
        else:
            w(f"| {text} | {p['cells']:,} | {p['identical']:,} | {p['max_abs_difference']:.6f} |")
    w("")
    w(f"The candidate's decision days with a forecast: {n['scored_decision_days']:,} (of {n['decision_days_offered']:,} offered, {n['first']} to {n['last']}); the days on which its forecast moves with the reading: "
      f"{r['decision_days_candidate_forecast_moves']:,}.")
    if "grid_crps_mean_matches_record" in cand:
        w("")
        w(f"This is the candidate #1314 scored: its mean grid CRPS here is {cand['grid_crps_mean_week_average']:.6f} bp against "
          f"{cand['grid_crps_mean_record_1314']:.6f} bp in that record ({'equal' if cand['grid_crps_mean_matches_record'] else 'NOT equal'} to 1e-9).")
    w("")
    w("## Why: what it reads")
    w("")
    w("(s3c-ann-net) is (s3) of the state-scaled calendar study with its two settlement terms sized by the announced net settlement, capped at the Standing Repo Facility "
      "line from full allotment (`repo_model.s3c_announced.ANN_NET_ARM`, `repo_model.s3c_candidate`). Its scale and centre come from the spread series. Its calendar "
      "terms are read from the calendar, the announcements and the policy register. The arm is a sized arm, and the sized arms' scarcity state is held at its maximum "
      "(`repo_model.s3c_net.constant_states`), so the state level is 1 on every day under either reading: the Wednesday level cannot reach the fit or the forecast through "
      "the state. The scarcity state exists in the arms that interact it with a term ((s2) and (s3+state) of #1145); this candidate is not one of them, which is the page of "
      "#1314 noting that \"the model's own state is held at its maximum\". The cap reads the policy register, not reserves.")
    w("")
    w("## How many decision days the Wednesday level changes the state, and what the candidate does with it")
    w("")
    w("The own-leg scarcity state (`scarcity.own_leg_states`, each leg at its own latest public row, #586) under each reading, on the candidate's decision days. This is what "
      "a model that read the state would act on; (s3c-ann-net) does not.")
    w("")
    w("| lead | decision days | state differs | up | down | days the candidate's forecast moves |")
    w("|---|---|---|---|---|---|")
    for h in sorted(r["decision_days_state_differs"], key=int):
        row = r["decision_days_state_differs"][h]
        w(f"| {h} | {row['scored_decision_days']:,} | {row['differ']} | {row['up']} | {row['down']} | {r['decision_days_candidate_forecast_moves']} |")
    w("")
    w(f"On {r['decision_days_state_differs_at_any_lead']} decision days the state differs at some lead; the candidate's forecast moves on "
      f"{r['decision_days_candidate_forecast_moves']}. These counts are at the {r['instant']} instant; the first page's, at 16:00, are its own (#1314 found the state label "
      "differs between the two instants on a few decision days and no score does).")
    w("")
    w("## The control: an arm that does read the state")
    w("")
    w(f"The check is shown able to see a difference where there is one. The control is `{ctl['arm']}` (#1145's (s2): (s1) and each calendar term times the as-of scarcity "
      "state), walked on both panels with the as-of states of the two readings (the horizon-1 state, keyed by the decision day, as #1145 keys it).")
    w("")
    w("| | cells | identical on both panels | largest absolute difference (bp) | decision days the forecast moves | decision days the state differs |")
    w("|---|---|---|---|---|---|")
    cc = ctl["compared"]
    w(f"| control, week average against Wednesday level | {cc['cells']:,} | {cc['identical']:,} | {cc['max_abs_difference']:.6f} | {ctl['days_moved']} | {ctl['state_differs_on_decision_day']} |")
    w("")
    w("## What this does and does not show")
    w("")
    w("- It shows that the Wednesday reading, as a replacement of the scarcity state's reserve leg, cannot move (s3c-ann-net)'s forecast, and so cannot move any of its scores, "
      "by lead, regime, scarcity state or on the days the readings differ. It shows this by running the candidate, not by assuming it.")
    w("- It does not show the Wednesday reading to be worse or better as a description of scarcity. The state under each reading is on the first page "
      "(`docs/research/wednesday-scarcity-1146-result.md`), unchanged.")
    w("- It reads the development window only. The Wednesday-level snapshot ends on 2025-12-31, the 2026 days are not substituted, no locked day is read, and nothing "
      "here is a verdict: only prospective confirmation days give one.")
    w("")
    w("## Question for Eleonora")
    w("")
    w("The check says the Wednesday level cannot reach (s3c-ann-net). Nothing is adopted here, nothing is registered, and the candidate does not change.")
    w("")
    w("1. **Close #1146 on this finding (default).** The first run's record (on #941) and this check stand; the Wednesday reading waits for a candidate that reads the state.")
    w("2. **Ask for an arm that reads the state.** A separate directive builds a variant of (s3c-ann-net) whose calendar terms are interacted with the as-of scarcity state "
      "((s2) or (s3+state) of #1145 on top of the announced terms), so that the two readings can differ, and scores that variant under both readings. That is a new candidate "
      "arm, not the H5 candidate, and it is hers to ask for.")
    w("")
    return "\n".join(out) + "\n"


def page(args) -> int:
    result = json.loads(Path(args.check).read_text(encoding="utf-8"))
    Path(args.output).write_text(render(result), encoding="utf-8")
    return 0


@turn_days.with_legacy_flag
def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="command", required=True)
    s = sub.add_parser("check", help="walk (s3c-ann-net) under both readings on rows that count reads of the reserve column")
    s.add_argument("--panel", required=True)
    s.add_argument("--output", required=True)
    s.add_argument("--first", type=date.fromisoformat, default=None, help="start the walk later (the test of this script only)")
    s.add_argument("--any-instant", action="store_true", help="allow a decision instant other than 18:00 (the test of this script only)")
    s.set_defaults(func=check)
    p = sub.add_parser("page", help="write the Markdown page from a check file")
    p.add_argument("--check", required=True)
    p.add_argument("--output", required=True)
    p.set_defaults(func=page)
    args = parser.parse_args(argv)
    return int(args.func(args) or 0)


if __name__ == "__main__":
    raise SystemExit(main())
