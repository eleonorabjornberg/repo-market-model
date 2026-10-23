#!/usr/bin/env python3
"""H6 step 2 (#1131): the registration design for the event-day strata, and its power on contiguous windows of events.

A design and power page only. No registration is made (registering is Eleonora's own action), no decided value moves,
no day after 2025-12-31 and no lockbox day is scored, and nothing here is a verdict (scoring protocol v1, #640).
Everything it computes is declared in `metadata/h6_design_1131.json`, which `run` refuses to read unless it is committed
and unchanged.

For each stratum of the declaration (every one read from the calendar at the target day) and for their union it
- counts the target days and the events a year, and the days each benchmark covers;
- scores the H5 metric (grid CRPS averaged over leads 1-5, and the upper-tail twCRPS) of B1, B1', B2 and the risk-date
  calendar benchmark (#693) against `spread_mr_ctx` (#761), as a stand-in for a candidate's series, on those days, paired
  by the studentized stationary bootstrap (block 3 events, HAC lag 3, one-sided 95% bounds) with the ACF of d between
  consecutive events;
- computes, by #963's method, the critical value c on every contiguous window of N events (N from 1, 2 and 3 years), the
  size at the normal value, and the power at 3, 5, 10, 15 and 20% skill.

    PYTHONPATH=src python3 -m repo_model.cli build --raw-root tests/fixtures/snapshots/funding_inputs --output PUB.csv \\
        --build-cutoff 2026-09-08T21:31:42+00:00 --decision-time 16:00:00
    PYTHONPATH=src python3 scripts/h6_design_1131.py run --published PUB.csv
    python3 scripts/h6_design_1131.py report
    python3 scripts/h6_design_1131.py check

`run` writes `docs/research/h6-design-1131/result.json` (about two minutes on one core), `report` writes the page
`docs/research/h6-design-1131-result.md` from it alone, and `check` fails when the page is not what the record gives.
Standard library only.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import math
import subprocess
import sys
from collections import Counter
from datetime import date, datetime, time
from pathlib import Path
from typing import Dict, List, Mapping, Optional, Sequence, Set, Tuple

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))

from repo_model import data as rm_data, fomc_calendar as fc, lockbox, scoring_protocol as sp, turn_days  # noqa: E402
from repo_model import risk_date_spread as rds  # noqa: E402

RESEARCH = REPO / "docs" / "research"
DECLARATION = REPO / "metadata" / "h6_design_1131.json"
RECORD = RESEARCH / "h6-design-1131" / "result.json"
PAGE = RESEARCH / "h6-design-1131-result.md"

POST_2020_FIRST = date(2020, 4, 3)
LAST_TARGET = date(2025, 12, 31)
SEED = 1131
DRAWS = 10_000
EVENT_BLOCK = 3.0
EVENT_LAG = 3
ACF_LAGS = 3
LEVEL = 0.05
NORMAL_ONE_SIDED_95 = 1.6448536269514722
MINIMUM_EVENTS = 30
SKILLS = (0.03, 0.05, 0.10, 0.15, 0.20)
WINDOW_YEARS = (1.0, 2.0, 3.0)
TRAILING_ROWS = 252
BILL_QUANTILE = 0.75
DECISION_TIME = time(16, 0)
LONGEST_LEAD = max(sp.HORIZONS)
REPRODUCTION_TOLERANCE = 1e-9

STRATA = ("coupon_settlement", "bill_settlement_large", "month_end_turn", "quarter_end_turn", "year_end",
          "quarter_and_year_end", "tax_date", "fomc_meeting", "post_fomc_window")
UNION = "union"
UNION_EX_BILL = "union_without_bill"
ALL_DAYS = "all_days"
PROTOCOL_LAG = sp.HAC_LAG
BENCHMARKS = ("B1", "B1_prime", "B2", "calendar")
CANDIDATE = "spread_mr_ctx"
LABEL = {"B1": "B1", "B1_prime": "B1'", "B2": "B2", "calendar": "risk-date calendar (#693)"}
STRATUM_TEXT = {
    "coupon_settlement": "coupon settlement",
    "bill_settlement_large": "large bill settlement",
    "month_end_turn": "month-end turn",
    "quarter_end_turn": "quarter-end turn (Mar, Jun, Sep)",
    "year_end": "year-end",
    "quarter_and_year_end": "quarter-end and year-end",
    "tax_date": "tax date",
    "fomc_meeting": "FOMC meeting day",
    "post_fomc_window": "IORB-change window (two days after a meeting)",
    UNION: "union of the strata",
    UNION_EX_BILL: "union without the bill stratum",
    ALL_DAYS: "all target days (H5's unit, lag 10)",
}


def _load(name: str):
    spec = importlib.util.spec_from_file_location(f"{name}_h6script", REPO / "scripts" / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[f"{name}_h6script"] = module
    spec.loader.exec_module(module)
    return module


# -- the scope --------------------------------------------------------------------------------------------------------


def require_scored_days(days, last: date = LAST_TARGET) -> None:
    """Refuse a day after `last`, the declared end of the scored days, and a locked day.

    Raises:
        LookAheadError: a day after `last`, or in a locked tier.
    """

    from repo_model.splits import LookAheadError

    days = list(days)
    for day in sorted(days):
        if day > last:
            raise LookAheadError(f"{day} is after {last}, the last day #1131 scores; the declaration admits no later day")
    lockbox.require_unlocked(days, where="scripts/h6_design_1131")


# -- the strata -------------------------------------------------------------------------------------------------------


def _quantile(sorted_values: Sequence[float], q: float) -> float:
    position = q * (len(sorted_values) - 1)
    low = int(math.floor(position))
    high = min(low + 1, len(sorted_values) - 1)
    return sorted_values[low] + (position - low) * (sorted_values[high] - sorted_values[low])


def bill_threshold(rows: Sequence[Mapping[str, Optional[float]]], index: int, q: float = BILL_QUANTILE) -> Optional[float]:
    """The `q` quantile of the positive bill settlements of the `TRAILING_ROWS` rows strictly before `index`, or `None`.

    The rows are the panel rows' values. A target's own settlement and every later row are never read.
    """

    amounts = sorted(
        float(row.get("treasury_settlement_bills") or 0.0)
        for row in rows[max(0, index - TRAILING_ROWS):index]
        if float(row.get("treasury_settlement_bills") or 0.0) > 0.0
    )
    return _quantile(amounts, q) if amounts else None


def fomc_days(meetings: Sequence[fc.Meeting], as_of: datetime) -> Tuple[Set[date], Set[date]]:
    """The meeting days and the IORB-change window of the meetings visible at `as_of`.

    The window is the first and second business days after a meeting's last day: a change in IORB takes effect on the
    first of them, and is announced only at the meeting, so the window is the scheduled calendar's.

    Raises:
        ValueError: `as_of` is before the first published schedule (the calendar would read as empty, not as unknown).
        LookAheadError: a meeting not public at `as_of` reached a value.
    """

    if meetings and as_of < min(m.public_at for m in meetings):
        raise ValueError(f"decision instant {as_of} is before the first published schedule")
    seen = [m for m in meetings if fc.visible_at(m, as_of)]
    days: Set[date] = set()
    window: Set[date] = set()
    for meeting in seen:
        fc.require_public(meeting, as_of)
        day = meeting.start
        while day <= meeting.end:
            days.add(day)
            day = date.fromordinal(day.toordinal() + 1)
        window.add(rm_data.next_business_day(meeting.end, 1))
        window.add(rm_data.next_business_day(meeting.end, 2))
    return days, window


def membership(day: date, values: Mapping[str, Optional[float]], *, fomc_meeting: bool, post_fomc: bool,
               bill_floor: Optional[float]) -> Set[str]:
    """The strata a target day is in (they are not exclusive); the union is any non-empty set."""

    out: Set[str] = set()
    if float(values.get("treasury_settlement_coupons") or 0.0) > 0.0:
        out.add("coupon_settlement")
    bills = float(values.get("treasury_settlement_bills") or 0.0)
    if bills > 0.0 and bill_floor is not None and bills >= bill_floor:
        out.add("bill_settlement_large")
    label = turn_days.turn_day_type(day, tax_date=float(values.get("tax_date") or 0.0) == 1.0)
    if label == turn_days.TURN:
        out.add("month_end_turn")
    elif label == turn_days.QUARTER_END_TURN:
        out.update({"quarter_end_turn", "quarter_and_year_end"})
    elif label == turn_days.YEAR_END:
        out.update({"year_end", "quarter_and_year_end"})
    elif label == turn_days.TAX_DATE:
        out.add("tax_date")
    if fomc_meeting:
        out.add("fomc_meeting")
    if post_fomc:
        out.add("post_fomc_window")
    return out


# -- the windows ------------------------------------------------------------------------------------------------------


def events_per_year(events: Sequence[date]) -> float:
    ordered = sorted(events)
    return len(ordered) / ((ordered[-1] - ordered[0]).days / 365.25)


def window_events(per_year: float, years: float, *, lag: int = EVENT_LAG) -> int:
    """Events in a window of `years` years: `round(years * per_year)`, at least `lag + 2`."""

    return max(lag + 2, int(round(years * per_year)))


def window_pairs(series: Sequence[float], events: int, *, lag: int = EVENT_LAG) -> List[Tuple[float, float]]:
    """`(mean_w - mean(series), se_w)` of every window of `events` consecutive events, none wrapping.

    `se_w` is the window's Newey-West standard error at `lag` (`scoring_protocol._standard_error`). A window with no
    long-run variance cannot be studentized and is left out; `len(series) - events + 1 - len(result)` counts them.

    Raises:
        ValueError: the series is shorter than the window, or the window cannot carry the lag.
    """

    values = [sp._finite(v, "a difference") for v in series]
    if events > len(values):
        raise ValueError(f"a series of {len(values)} events holds no window of {events} events")
    if events <= lag:
        raise ValueError(f"windows of {events} events cannot carry a lag-{lag} long-run variance")
    truth = sum(values) / len(values)
    out = []
    for start in range(len(values) - events + 1):
        window = values[start:start + events]
        try:
            se = sp._standard_error(window, lag, "a window")
        except sp.ProtocolError:
            continue  # a window with no long-run variance cannot be studentized; the caller counts the ones left out
        out.append((sum(window) / events - truth, se))
    return out


def critical_value(pairs: Sequence[Tuple[float, float]], level: float = LEVEL) -> float:
    """The `1 - level` quantile of the null windows' statistics."""

    ordered = sorted(dev / se for dev, se in pairs)
    return sp._bound(ordered, 1.0 - level, len(ordered))


def share_above(pairs: Sequence[Tuple[float, float]], value: float, shift: float = 0.0) -> float:
    return sum(1 for dev, se in pairs if (dev + shift) / se > value) / len(pairs)


def power(pairs: Sequence[Tuple[float, float]], c: float, shift: float) -> float:
    """The share of windows whose statistic, with the mean moved up by `shift`, exceeds `c`."""

    return share_above(pairs, c, shift)


# -- the data ---------------------------------------------------------------------------------------------------------


def committed_declaration(path: Path = DECLARATION) -> dict:
    """The declaration, refused unless it is committed and unchanged since `HEAD`."""

    relative = str(path.resolve().relative_to(REPO))
    dirty = subprocess.run(["git", "status", "--porcelain", "--", relative], cwd=REPO, capture_output=True, text=True,
                           check=True).stdout.strip()
    if dirty:
        raise SystemExit(f"{relative} is not committed ({dirty}); a declaration is made before any score")
    return json.loads(path.read_text(encoding="utf-8"))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def acf(values: Sequence[float], lags: int) -> Optional[List[float]]:
    try:
        return _load("block_length_949").acf(values, lags)
    except ValueError:
        return None


def build(published: Path):
    """The frame of #960 (B1, B2, B1', `spread_mr_ctx`) and the risk-date calendar benchmark's cells."""

    b1c = _load("b1_calendar_960")
    s686 = b1c.s686
    from repo_model.baseline import panel_sha256
    from repo_model.data import load_daily_panel
    from repo_model.evaluation_splits import load_split_declaration

    panel = load_daily_panel(published)
    splits = load_split_declaration(b1c.s761.SPLITS)
    registry = json.loads(b1c.s761.SOURCES.read_text(encoding="utf-8"))
    declaration = b1c.s761.committed_declaration(b1c.DECLARATION)
    frame, notes = b1c.build_frame(panel, panel_sha256(published), splits, registry, declaration)

    calendar_forecasts: Dict[date, Dict[int, List[float]]] = {}
    for day in frame.days:
        try:
            calendar_forecasts[day] = rds.calendar_forecast(panel, frame.position[day], **frame.settings)
        except sp.ProtocolError:
            continue
    metrics = {"grid_crps": sp.grid_crps, "upper_tail_twcrps": sp.upper_tail_twcrps}
    cells: Dict[str, Dict[str, Dict[Tuple[date, int], float]]] = {}
    for metric, fn in metrics.items():
        cells[metric] = {m: s686.cell_scores(frame, m, fn) for m in ("B1", "B2", "B1_prime", CANDIDATE)}
        per = {}
        for day, leads in calendar_forecasts.items():
            for h, quantiles in leads.items():
                per[(day, h)] = fn(quantiles, frame.outcome[frame.target(day, h)])
        require_scored_days({d for d, _ in per} | {frame.target(d, h) for d, h in per}, LAST_TARGET)
        cells[metric]["calendar"] = per
    return {"frame": frame, "notes": notes, "cells": cells, "metrics": tuple(metrics), "panel": panel,
            "calendar_days": len(calendar_forecasts)}


def target_scores(frame, cells: Mapping[Tuple[date, int], float]) -> Dict[date, float]:
    """`{target day: mean over leads 1-5 of the cells that target it}` where all five exist, from 2020-04-03."""

    out = {}
    for target in frame.dates:
        pos = frame.position[target]
        if target > LAST_TARGET or pos < LONGEST_LEAD or frame.dates[pos - LONGEST_LEAD] < POST_2020_FIRST:
            continue
        parts = []
        for h in sp.HORIZONS:
            cell = (frame.dates[pos - h], h)
            if cell not in cells:
                parts = None
                break
            parts.append(cells[cell])
        if parts:
            out[target] = sum(parts) / len(parts)
    return out


def target_membership(frame, panel, targets: Sequence[date]) -> Dict[date, Set[str]]:
    """Each target day's strata, read from the calendar at the decision instant of the longest lead."""

    meetings = fc.load_calendar()
    values = [row.values for row in panel]
    out = {}
    for target in targets:
        pos = frame.position[target]
        as_of = datetime.combine(frame.dates[pos - LONGEST_LEAD], DECISION_TIME)
        days, window = fomc_days(meetings, as_of)
        out[target] = membership(target, values[pos], fomc_meeting=target in days, post_fomc=target in window,
                                 bill_floor=bill_threshold(values, pos))
    return out


def realized_iorb_in_window(frame, window_days: Set[date]) -> Dict[str, int]:
    """Ex post: of the IORB changes that took effect in the scored years, how many did so inside the window."""

    from repo_model.announced_iorb import load_announcements

    table = REPO / "tests" / "fixtures" / "snapshots" / "fed-iorb-announcements" / "iorb_changes.csv"
    effective = [row.effective for row in load_announcements(table) if row.kind == "change"
                 and POST_2020_FIRST <= row.effective <= LAST_TARGET]
    inside = [e for e in effective if e in window_days]
    return {"changes": len(effective), "inside": len(inside)}


def paired(bench: Mapping[date, float], cand: Mapping[date, float], events: Sequence[date], *, block: float = EVENT_BLOCK,
           lag: int = EVENT_LAG) -> dict:
    s761 = _load("spread_mr_variants_761")
    pair = ({e: bench[e] for e in events}, {e: cand[e] for e in events})
    try:
        (test,) = sp.paired_tests([pair], seed=SEED, draws=DRAWS, block_length=block, hac_lag=lag)
    except sp.ProtocolError as error:
        return {"undefined": str(error), "days": len(events)}
    return s761.paired_row(test)


def power_cells(d: Sequence[float], mean_b: float, per_year: float, lag: int = EVENT_LAG) -> Dict[str, dict]:
    out = {}
    for years in WINDOW_YEARS:
        n_window = window_events(per_year, years, lag=lag)
        if n_window > len(d):
            out[str(years)] = {"events_in_window": n_window, "too_long": True}
            continue
        pairs = window_pairs(d, n_window, lag=lag)
        try:
            c = critical_value(pairs)
        except sp.UnresolvedLevel as error:
            out[str(years)] = {"events_in_window": n_window, "windows": len(pairs), "unresolved": str(error)}
            continue
        left_out = len(d) - n_window + 1 - len(pairs)
        out[str(years)] = {
            "events_in_window": n_window, "windows": len(pairs), "left_out": left_out, "effective_windows": len(d) / n_window, "c": c,
            "size": share_above(pairs, NORMAL_ONE_SIDED_95),
            "power": {str(s): power(pairs, c, s * mean_b) for s in SKILLS},
        }
    return out


# -- the run ----------------------------------------------------------------------------------------------------------


def run_command(args) -> int:
    declaration = committed_declaration()
    data = build(Path(args.published))
    frame, panel = data["frame"], data["panel"]

    record: Dict[str, object] = {
        "declaration_sha256": sha256(DECLARATION), "panel_sha256": sha256(Path(args.published)), "seed": SEED, "draws": DRAWS,
        "event_block": EVENT_BLOCK, "event_lag": EVENT_LAG, "skills": list(SKILLS), "window_years": list(WINDOW_YEARS),
        "minimum_events": MINIMUM_EVENTS, "decision_days": len(frame.days), "calendar_forecast_days": data["calendar_days"],
    }
    # reproduction: the pooled grid CRPS of B1, B2, B1' and spread_mr_ctx equal #960's record (to 1e-9)
    s686 = _load("b1_calendar_960").s686
    prior = json.loads((REPO / "docs/pivot/evidence/b1-calendar-960/score.json").read_text(encoding="utf-8"))
    reproduced = {}
    for model in ("B1", "B2", "B1_prime", CANDIDATE):
        mine = sum(s686.by_decision(data["cells"]["grid_crps"][model]).values()) / len(frame.days)
        recorded = prior["means"]["grid_crps"][model]
        reproduced[model] = {"here": mine, "960": recorded}
        if abs(mine - recorded) > REPRODUCTION_TOLERANCE:
            raise ValueError(f"grid CRPS of {model} is {mine} here and {recorded} in #960's record")
    record["reproduces_960"] = reproduced

    scores = {m: {b: target_scores(frame, data["cells"][m][b]) for b in BENCHMARKS + (CANDIDATE,)} for m in data["metrics"]}
    common = sorted(set.intersection(*(set(scores["grid_crps"][b]) for b in ("B1", "B1_prime", "B2", CANDIDATE))))
    require_scored_days(common)
    members = target_membership(frame, panel, common)
    sets: Dict[str, List[date]] = {s: [t for t in common if s in members[t]] for s in STRATA}
    sets[UNION] = [t for t in common if members[t]]
    sets[UNION_EX_BILL] = [t for t in common if members[t] - {"bill_settlement_large"}]
    years = (common[-1] - common[0]).days / 365.25
    record["history"] = {"first_target": common[0].isoformat(), "last_target": common[-1].isoformat(), "target_days": len(common),
                         "years": years}

    record["iorb_window"] = realized_iorb_in_window(frame, set(
        d for d in (rm_data.next_business_day(m.end, k) for m in fc.load_calendar() for k in (1, 2))))
    strata: Dict[str, dict] = {}
    observed: Dict[str, dict] = {}
    powers: Dict[str, dict] = {}
    for name in STRATA + (UNION, UNION_EX_BILL):
        events = sets[name]
        entry = {"n": len(events), "per_year": events_per_year(events) if len(events) > 1 else None,
                 "by_year": dict(sorted(Counter(str(e.year) for e in events).items())),
                 "thin": len(events) < MINIMUM_EVENTS}
        covered = {}
        for bench in BENCHMARKS:
            covered[bench] = sum(1 for e in events if e in scores["grid_crps"][bench])
        entry["covered"] = covered
        strata[name] = entry
        if entry["thin"]:
            continue
        for metric in data["metrics"]:
            for bench in BENCHMARKS:
                use = [e for e in events if e in scores[metric][bench]]
                if len(use) < MINIMUM_EVENTS:
                    observed.setdefault(metric, {}).setdefault(name, {})[bench] = {"events": len(use), "thin": True}
                    continue
                b = {e: scores[metric][bench][e] for e in use}
                c = {e: scores[metric][CANDIDATE][e] for e in use}
                row = paired(b, c, use)
                d = [b[e] - c[e] for e in use]
                row.update({"events": len(use), "acf": acf(d, ACF_LAGS)})
                observed.setdefault(metric, {}).setdefault(name, {})[bench] = row
                per_year = events_per_year(use)
                powers.setdefault(metric, {}).setdefault(name, {})[bench] = {
                    "events": len(use), "per_year": per_year, "mean_benchmark": sum(b.values()) / len(use),
                    "windows": power_cells(d, sum(b.values()) / len(use), per_year),
                }
    record["strata"] = strata
    record["observed"] = observed
    record["power"] = powers

    # the reference: H5's own unit, every target day, the protocol's lag
    per_year_all = len(common) / years
    reference: Dict[str, dict] = {"target_days": len(common), "per_year": per_year_all, "lag": PROTOCOL_LAG, "benchmarks": {}}
    for bench in ("B1", "B1_prime", "B2"):
        b = {e: scores["grid_crps"][bench][e] for e in common}
        c = {e: scores["grid_crps"][CANDIDATE][e] for e in common}
        d = [b[e] - c[e] for e in common]
        row = paired(b, c, common, block=sp.BLOCK_LENGTH, lag=PROTOCOL_LAG)
        row.update({"events": len(common), "acf": acf(d, ACF_LAGS)})
        reference["benchmarks"][bench] = {"observed": row, "mean_benchmark": sum(b.values()) / len(b),
                                          "windows": power_cells(d, sum(b.values()) / len(b), per_year_all, PROTOCOL_LAG)}
    record["reference_all_days"] = reference

    regimes: Dict[str, dict] = {}
    by_regime: Dict[str, List[date]] = {}
    for e in sets[UNION]:
        by_regime.setdefault(frame.regime(e), []).append(e)
    for regime, events in by_regime.items():
        entry = {"events": len(events), "benchmarks": {}}
        for bench in BENCHMARKS:
            use = [e for e in events if e in scores["grid_crps"][bench]]
            if len(use) < MINIMUM_EVENTS:
                entry["benchmarks"][bench] = {"events": len(use), "thin": True}
                continue
            entry["benchmarks"][bench] = {**paired({e: scores["grid_crps"][bench][e] for e in use},
                                                   {e: scores["grid_crps"][CANDIDATE][e] for e in use}, use), "events": len(use)}
        regimes[regime] = entry
    record["union_by_regime"] = regimes

    RECORD.parent.mkdir(parents=True, exist_ok=True)
    RECORD.write_text(json.dumps(record, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    return 0


# -- the page ---------------------------------------------------------------------------------------------------------


def pct(x: Optional[float], signed: bool = True) -> str:
    return "n/a" if x is None else format(100.0 * x, "+.1f" if signed else ".1f") + "%"


def skill_text(row: Optional[dict]) -> str:
    if row is None or row.get("thin"):
        return "thin"
    if "undefined" in row:
        return "undefined"
    lo, hi = row["skill_interval"]
    return f"{pct(row['skill'])} [{pct(lo)}, {pct(hi)}]"


def acf_text(row: Optional[dict]) -> str:
    if row is None or row.get("thin") or "undefined" in row or not row.get("acf"):
        return ""
    return " / ".join(format(x, "+.2f") for x in row["acf"])


def power_row(label: str, years: float, cell: dict, skills: Sequence[float]) -> str:
    return (f"| {label} | {years:g} y | {cell['events_in_window']} | {cell['windows']} | {cell['effective_windows']:.1f} | "
            f"{cell['c']:.2f} | {pct(cell['size'], False)} | " + " | ".join(pct(cell["power"][str(s)], False) for s in skills) + " |")


def render(r: dict) -> str:
    L: List[str] = []
    add = L.append
    h = r["history"]
    strata = r["strata"]
    add("# H6 registration design and power (#1131, H6 step 2)")
    add("")
    add("**Hypothesis and step:** H6 (the spread on known risk dates is forecastable), step 2, the registration design, ahead of H5 "
        "(Eleonora's ruling of 22 October 2026, option c on #1024). **A design and power page only: no registration is made** "
        "(registering is her own action) and every item under *Questions* is hers. **Development data, not a verdict** "
        "(scoring protocol v1, #640). The declaration is `metadata/h6_design_1131.json`, committed before any score; the "
        "script is `scripts/h6_design_1131.py`; every figure below is read from "
        "`docs/research/h6-design-1131/result.json`. Basis: Lens C of the five-lens review (#958, avenue B) and #963.")
    add("")
    add("The ruling's reason: post-2020 autocorrelation leaves H5's 250-day window with a handful of independent windows "
        "(#963). H6 moves the unit of evidence from a day to an announced event: the strata below hold target days that the "
        "calendar names in advance, so a confirmation window of calendar years holds tens to a few hundred events.")
    add("")
    add("## 1. The strata (all read from the calendar at the target day)")
    add("")
    add(f"Target days: {h['target_days']} from {h['first_target']} to {h['last_target']} ({h['years']:.1f} years), the days all four "
        "forecasts cover with all five leads. A day may be in several strata; the union is the days in at least one. A stratum "
        f"below {r['minimum_events']} events is counted and not tested on its own.")
    add("")
    add("| stratum | rule | events | per year | by calendar year | tested alone |")
    add("|---|---|---|---|---|---|")
    rule = {
        "coupon_settlement": "`treasury_settlement_coupons > 0`",
        "bill_settlement_large": "bill settlement at or above the 75th percentile of the trailing 252 rows' positive settlements",
        "month_end_turn": "last business day of a month that is not a quarter's last, and the first of the next (#959)",
        "quarter_end_turn": "last business day of Mar, Jun, Sep and the first business day after (#959)",
        "year_end": "last business day of December and the first of January (#959)",
        "quarter_and_year_end": "the two rows above together",
        "tax_date": "the `tax_date` column, on a day that is no turn day",
        "fomc_meeting": "both days of a meeting public at the longest lead's decision instant",
        "post_fomc_window": "first and second business day after a meeting's last day",
        UNION: "any of the above",
        UNION_EX_BILL: "any of the above but the large bill settlement",
    }
    for name in STRATA + (UNION, UNION_EX_BILL):
        s = strata[name]
        by_year = ", ".join(f"{y}: {n}" for y, n in s["by_year"].items())
        per = "n/a" if s["per_year"] is None else f"{s['per_year']:.1f}"
        add(f"| {STRATUM_TEXT[name]} | {rule[name]} | {s['n']} | {per} | {by_year} | {'no (thin)' if s['thin'] else 'yes'} |")
    add("")
    w = r["iorb_window"]
    add(f"The IORB-change window is the scheduled calendar's, because a change is announced at the meeting and so cannot define a "
        f"stratum in advance. Ex post, {w['inside']} of the {w['changes']} IORB changes that took effect from "
        f"{POST_2020_FIRST.isoformat()} to {LAST_TARGET.isoformat()} fell in it.")
    add("")
    add("Days each benchmark covers (events with a forecast at all five leads). The risk-date calendar benchmark (#693) exists at a "
        "lead only where the target is a quarter-end, month-end, tax date or announced coupon settlement; the others cover every "
        "event.")
    add("")
    add("| stratum | " + " | ".join(LABEL[b] for b in BENCHMARKS) + " |")
    add("|---|" + "---|" * len(BENCHMARKS))
    for name in STRATA + (UNION, UNION_EX_BILL):
        s = strata[name]
        add(f"| {STRATUM_TEXT[name]} | " + " | ".join(str(s["covered"][b]) for b in BENCHMARKS) + " |")
    add("")

    add("## 2. The candidate, the benchmarks, the score")
    add("")
    add("- **Candidate.** H6 registers one primary candidate. It is not chosen here: H5's best (`gbm_funding` or `spread_mr_ctx`, "
        "step 5 of H5) is the natural one, and a risk-date-specialised variant is H6's own step 2. The power below uses "
        "`spread_mr_ctx` (#761) as a stand-in for the shape of a candidate's d series; `gbm_funding`'s walks are a long run and "
        "are not repeated here.")
    add("- **Benchmarks.** B1 and B1' are both reported (B1' is #960's calendar-aware persistence; B1 stays the protocol's "
        "benchmark), B2, and the risk-date calendar benchmark (#693): the trailing year's spreads of the target's risk type.")
    add("- **Score.** The H5 metric: grid CRPS averaged over leads 1 to 5, on the target day, primary; the upper-tail twCRPS "
        "(weight 1{z > 0 bp}) key secondary. Paired, positive favours the candidate; the interval is the studentized stationary "
        f"bootstrap's (block {r['event_block']:g} events, HAC lag {r['event_lag']}, {r['draws']} draws, seed {r['seed']}), two-sided "
        "90%, so the lower end is the one-sided 95% lower bound.")
    add("")

    metric = "grid_crps"
    add("## 3. Development skill on the strata, grid CRPS (paired, with the interval)")
    add("")
    add("Skill of `spread_mr_ctx` over each benchmark, with ρ(1)/ρ(2)/ρ(3) of d between consecutive events. A stratum is the "
        "day-type split; the union is split by regime in the next table. Development data, not a verdict.")
    add("")
    add("| stratum | benchmark | events | skill [90%] | ACF of d |")
    add("|---|---|---|---|---|")
    for name in STRATA + (UNION, UNION_EX_BILL):
        if strata[name]["thin"]:
            continue
        for bench in BENCHMARKS:
            row = r["observed"].get(metric, {}).get(name, {}).get(bench)
            n = "" if row is None else row.get("events", "")
            add(f"| {STRATUM_TEXT[name]} | {LABEL[bench]} | {n} | {skill_text(row)} | {acf_text(row)} |")
    add("")
    add("Union by regime of the target day:")
    add("")
    add("| regime | events | " + " | ".join(LABEL[b] for b in BENCHMARKS) + " |")
    add("|---|---|" + "---|" * len(BENCHMARKS))
    for regime, entry in r["union_by_regime"].items():
        add(f"| {regime} | {entry['events']} | " + " | ".join(skill_text(entry["benchmarks"].get(b)) for b in BENCHMARKS) + " |")
    add("")

    add("## 4. Power on contiguous windows of events (#963's method)")
    add("")
    add("For a stratum's d series, every window of N consecutive events (none wrapping) gives a statistic: its mean over its "
        f"Newey-West standard error at lag {r['event_lag']}, relative to the series' mean. c is the 0.95 quantile of those "
        "statistics: the value at which the bound covers 95% of windows. *Size* is the share of null windows above the "
        "normal 1.645. *Power* at skill s is the share of windows that exceed c once the mean is moved to s times the "
        "benchmark's mean score on the stratum. N is the stratum's events in the window's years. *Independent* is "
        "n / N, an upper count of windows without overlap: a quantile of contiguous windows rests on that few stretches.")
    add("")
    for metric, title in (("grid_crps", "Grid CRPS (primary)"), ("upper_tail_twcrps", "Upper-tail twCRPS (key secondary), the union only")):
        add(f"### {title}")
        add("")
        names = [n for n in STRATA + (UNION, UNION_EX_BILL) if not strata[n]["thin"]] if metric == "grid_crps" else [UNION, UNION_EX_BILL]
        for bench in BENCHMARKS:
            add(f"**Against {LABEL[bench]}**")
            add("")
            add("| stratum | window | N events | windows | independent | c | size | " + " | ".join(f"power at {pct(s, False)}" for s in r["skills"]) + " |")
            add("|---|---|---|---|---|---|---|" + "---|" * len(r["skills"]))
            for name in names:
                block = r["power"].get(metric, {}).get(name, {}).get(bench)
                if block is None:
                    continue
                for years in r["window_years"]:
                    cell = block["windows"][str(years)]
                    if cell.get("too_long"):
                        add(f"| {STRATUM_TEXT[name]} | {years:g} y | {cell['events_in_window']} | longer than the history | | | | " + " | ".join("" for _ in r["skills"]) + " |")
                    elif "unresolved" in cell:
                        add(f"| {STRATUM_TEXT[name]} | {years:g} y | {cell['events_in_window']} | {cell['windows']} | | too few windows | | " + " | ".join("" for _ in r["skills"]) + " |")
                    else:
                        add(power_row(STRATUM_TEXT[name], years, cell, r["skills"]))
            if metric == "grid_crps" and bench in r["reference_all_days"]["benchmarks"]:
                for years in r["window_years"]:
                    cell = r["reference_all_days"]["benchmarks"][bench]["windows"][str(years)]
                    if "c" in cell:
                        add(power_row(STRATUM_TEXT[ALL_DAYS], years, cell, r["skills"]))
            add("")

    u = {b: r["power"]["grid_crps"][UNION][b]["windows"] for b in BENCHMARKS}
    ux = {b: r["power"]["grid_crps"][UNION_EX_BILL][b]["windows"] for b in BENCHMARKS}
    ref = {b: r["reference_all_days"]["benchmarks"][b] for b in ("B1", "B1_prime", "B2")}
    yrs = [str(y) for y in r["window_years"]]
    uo = r["observed"]["grid_crps"][UNION]
    mme = str(sp.MME)
    add("## 5. Reading")
    add("")
    add(f"- **The strata give more events per window, not more independent windows.** The history is {h['years']:.1f} years, so a "
        f"window of 1, 2 or 3 years leaves {u['B1']['1.0']['effective_windows']:.1f}, {u['B1']['2.0']['effective_windows']:.1f} and "
        f"{u['B1']['3.0']['effective_windows']:.1f} windows without overlap whatever the unit; H5's own unit on the same history "
        f"has the same {ref['B1']['windows']['1.0']['effective_windows']:.1f}, {ref['B1']['windows']['2.0']['effective_windows']:.1f} "
        f"and {ref['B1']['windows']['3.0']['effective_windows']:.1f}. What the union buys is {u['B1']['2.0']['events_in_window']} "
        f"events in a 2-year window, against {ref['B1']['windows']['2.0']['events_in_window']} days.")
    add(f"- **The events are not close to independent.** The ACF of d between consecutive union events is "
        f"{acf_text(uo['B1'])} against B1 and {acf_text(uo['B2'])} against B2 (lags 1, 2, 3). Lens C expected it near zero; it is "
        "not, so the standard error of a window of events has to carry the dependence (the Newey-West lag does), and the "
        "contiguous-window c is what sets the bar.")
    add(f"- **The contiguous c is above the normal value.** Against B1 the union's c is {u['B1']['1.0']['c']:.2f}, "
        f"{u['B1']['2.0']['c']:.2f} and {u['B1']['3.0']['c']:.2f} at 1, 2 and 3 years (size at the normal 1.645: "
        f"{pct(u['B1']['1.0']['size'], False)}, {pct(u['B1']['2.0']['size'], False)}, {pct(u['B1']['3.0']['size'], False)}), "
        f"against {ref['B1']['windows']['1.0']['c']:.2f}, {ref['B1']['windows']['2.0']['c']:.2f} and "
        f"{ref['B1']['windows']['3.0']['c']:.2f} for all days. A test on events needs its own contiguous-calibrated value.")
    add(f"- **Power at the protocol's {pct(sp.MME, False)} MME is low for the union and for all days.** Against B1, "
        f"the union's power at {pct(0.03, False)} is {pct(u['B1']['1.0']['power']['0.03'], False)}, {pct(u['B1']['2.0']['power']['0.03'], False)} "
        f"and {pct(u['B1']['3.0']['power']['0.03'], False)} at 1, 2 and 3 years; at {pct(0.10, False)} it is "
        f"{pct(u['B1']['1.0']['power']['0.1'], False)}, {pct(u['B1']['2.0']['power']['0.1'], False)} and "
        f"{pct(u['B1']['3.0']['power']['0.1'], False)}. All days at the same skill: "
        f"{pct(ref['B1']['windows']['2.0']['power']['0.03'], False)} and {pct(ref['B1']['windows']['2.0']['power']['0.1'], False)} "
        "at 2 years. Against B1' and B2 the power is in the same tables; a skill is a share of the benchmark's own mean score, "
        "so it is a larger shift against B2 than against B1.")
    bill = r["observed"]["grid_crps"][UNION_EX_BILL]["B1"]
    add(f"- **The bill stratum carries part of the union's pooled skill over B1.** With it the union's skill over B1 is "
        f"{skill_text(uo['B1'])}; without it, {skill_text(bill)}. The default below drops the stratum for want of a ruling on its "
        "size rule, not for this; both are in the tables.")
    tw = [c["c"] for name in (UNION, UNION_EX_BILL) for b in BENCHMARKS
          for c in r["power"]["upper_tail_twcrps"].get(name, {}).get(b, {}).get("windows", {}).values() if "c" in c]
    add(f"- **The upper-tail twCRPS studentized on events is unstable.** In its union tables below c runs from "
        f"{min(tw):.2f} to {max(tw):.0f}, with sizes at the normal value of up to "
        f"{pct(max(c['size'] for name in (UNION, UNION_EX_BILL) for b in BENCHMARKS for c in r['power']['upper_tail_twcrps'].get(name, {}).get(b, {}).get('windows', {}).values() if 'c' in c), False)}: "
        "a c of that size is what a window in which the two forecasts score nearly alike gives. The key secondary cannot be confirmed by "
        "this statistic on events as it stands; that is a statement about the statistic, not about the candidate.")
    add(f"- **The stand-in candidate's skill depends on the regime.** Over B1 on the union it is "
        + ", ".join(f"{regime}: {skill_text(entry['benchmarks'].get('B1'))}" for regime, entry in r["union_by_regime"].items())
        + f"; pooled {skill_text(uo['B1'])}. Over B1' it is {skill_text(uo['B1_prime'])} pooled and over B2 {skill_text(uo['B2'])}. "
        "A pooled figure alone is not a result.")
    add("- **Tax dates are B2's own pool.** B2 for a tax date and the risk-date calendar benchmark are the same trailing-year "
        "empirical distribution of tax-date spreads, so the two rows agree and the calendar benchmark adds nothing on that "
        "stratum.")
    add("")

    add("## 6. Questions for Eleonora (marked; none is settled in code)")
    add("")
    add("Each has a default that applies if she has not answered by the next 5 pm batch. No default changes what the project "
        "claims; a default is a draft for the registration PR.")
    add("")
    add("1. **The unit of evidence.** (a) the union of the declared strata, one event per target day; (b) each stratum alone, "
        "with the thin ones pooled; (c) the union as the primary and the strata as reported cuts. **Default: (c).** The "
        "union is the largest sample; the strata say where the skill is.")
    add(f"2. **The strata, and the bill stratum.** Which rows of section 1 are in the union. The large bill stratum "
        f"({strata['bill_settlement_large']['n']} events) rests on a stand-in size rule (the 75th percentile of the trailing 252 "
        f"rows) with no ruling behind it, and it changes the union from {strata[UNION_EX_BILL]['n']} to {strata[UNION]['n']} events. "
        f"**Default: the union without the bill stratum** ({r['power']['grid_crps'][UNION_EX_BILL]['B1']['windows']['2.0']['events_in_window']} "
        "events in a 2-year window against B1), until she rules on a bill-size rule.")
    add("3. **The month-end turn.** The strata use #959's turn label. #1135 drafts it as the one definition; this design "
        "stands on that draft, and the month-end rows are re-cut if she rules otherwise. **Default: #959's label.**")
    add(f"4. **The window length.** Against B1 the union's power at {pct(0.10, False)} skill is "
        f"{pct(u['B1']['1.0']['power']['0.1'], False)}, {pct(u['B1']['2.0']['power']['0.1'], False)} and "
        f"{pct(u['B1']['3.0']['power']['0.1'], False)} at 1, 2 and 3 years (at {pct(0.05, False)} skill: "
        f"{pct(u['B1']['1.0']['power']['0.05'], False)}, {pct(u['B1']['2.0']['power']['0.05'], False)} and "
        f"{pct(u['B1']['3.0']['power']['0.05'], False)}), while the windows left without overlap fall to "
        f"{u['B1']['3.0']['effective_windows']:.1f}. **Default: 2 years.** Windows longer than the history cannot be calibrated here.")
    add(f"5. **The minimum meaningful effect.** The protocol's {pct(sp.MME, False)} against B1 is below what these windows can detect "
        f"(power {pct(u['B1']['2.0']['power'][mme], False)} for the union at 2 years). Either H6's MME is larger, or the 3% stands and "
        "the registration states that it cannot be confirmed in the window. A new MME is a §13 change. **Default: keep "
        "3% and state the power beside it; no new MME is proposed.**")
    add("6. **The benchmarks that must be beaten.** (a) B1 only, as the protocol; (b) B1 and B2; (c) all four, with B1' and the "
        "calendar benchmark reported beside the protocol's. **Default: B1 and B2 decisive, B1' and the calendar benchmark "
        "reported.** A candidate that does not beat B1' has learned nothing the calendar did not already say, so it is in "
        "the table either way.")
    add("7. **Multiplicity.** With the union as the primary, the strata are reported cuts and carry no correction; if she "
        "makes the strata the unit, Holm across them. **Default: none on reported cuts.**")
    add("8. **A stratum benchmark.** #693's calendar benchmark covers four risk types; the FOMC and IORB-change rows would need "
        "their own, a new benchmark (a §13 change). **Default: not added; those rows are compared with B1, B1' and B2 only.**")
    add("9. **The point-in-time reading of the settlement flags.** A coupon settlement is a risk date at a lead only where its "
        "announcement was public (#849). The strata read the panel's flag; the registration must read it as #849 does. "
        "**Default: as #849.**")
    add("10. **The critical value.** The normal 1.645 is not the bar (section 5). The registration would calibrate c on the "
        "contiguous windows of events, as #963 does for days, and print the independent-window count beside it. "
        "**Default: yes, on the final strata and window.**")
    add("")

    add("## What this shows, and does not")
    add("")
    add("- It gives the strata, their event counts, the development skill of one stand-in candidate on each, and the power of "
        "contiguous windows of events. It registers nothing, scores no confirmation day, and sets no rule.")
    add("- The power rests on one stand-in candidate's d, four benchmarks and one history. The d series of a stratum is a few "
        "dozen to a few hundred events, dependent; the windows overlap, so each quantile rests on the independent count shown. "
        "A skill is the share of the benchmark's mean score on the stratum, so the same percentage is a different shift for "
        "each benchmark.")
    add("- The first run of the script produced the strata, the union and the power tables; the union without the bill stratum and "
        "the all-days rows were added to the declaration afterwards and are in this record (the declaration says so).")
    add("- Not checked: `gbm_funding` on the strata (a long run); a stratum-specific calendar benchmark for the turn, FOMC "
        "and IORB rows; the per-lead point-in-time dating of the bill and coupon flags; B1' on a confirmation day; the "
        "fixed-b statistic on events.")
    add("")
    return "\n".join(L)


def report_command(args) -> int:
    record = json.loads(RECORD.read_text(encoding="utf-8"))
    PAGE.write_text(render(record), encoding="utf-8")
    return 0


def check_command(args) -> int:
    record = json.loads(RECORD.read_text(encoding="utf-8"))
    if record["declaration_sha256"] != sha256(DECLARATION):
        print("the record was made from another declaration", file=sys.stderr)
        return 1
    if PAGE.read_text(encoding="utf-8") != render(record):
        print(f"{PAGE.relative_to(REPO)} is not what {RECORD.relative_to(REPO)} gives", file=sys.stderr)
        return 1
    print("ok")
    return 0


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="command", required=True)
    run = sub.add_parser("run", help="score the strata and write the record")
    run.add_argument("--published", required=True, help="the published panel CSV")
    run.set_defaults(func=run_command)
    sub.add_parser("report", help="write the page from the record").set_defaults(func=report_command)
    sub.add_parser("check", help="fail when the page is not what the record gives").set_defaults(func=check_command)
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
