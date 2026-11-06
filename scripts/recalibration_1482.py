#!/usr/bin/env python3
"""Recalibrate #878's critical and futility values on the loss differentials of (s3c-ann-net) (H1 step 4, #1482; #1354 Directive A).

A development study, never a verdict. `scoring_protocol.CRITICAL_VALUES`, `FUTILITY_CRITICAL_VALUES`, `B2_LEG_CRITICAL_VALUES` and
`docs/decisions/scoring-protocol.md` are not touched: a different value is her decision under protocol section 13.

#878 and #886 calibrated the values on series of the benchmarks (S(B2) - S(B1), S(B3) - S(B1)), because no candidate stood behind them. This study
calibrates the same values on the candidate's own loss differentials, in the orientation the test applies, d = S(benchmark) - S(candidate):

* the B1 leg, 23-level grid CRPS lead-averaged over h = 1..5 (the efficacy value of `CRITICAL_VALUES[GRID_COMPARISON]`, and, with S(B1), the futility value);
* the B2 leg, the same score (`B2_LEG_CRITICAL_VALUES`, empty today, so the leg reads the grid value);
* the B3 leg, B3's own five levels, h = 1..5, on the decision days where the published record has all five leads (`CRITICAL_VALUES[FIVE_LEVEL_COMPARISON]`).

Windows are drawn as #886 draws them: the stationary bootstrap, mean block `scoring_protocol.BLOCK_LENGTH` (10, her ruling of 22 October 2026 on #1022), on
the post-2020 decision days (from 2020-04-03, which holds no day of 2019-09-18's cut), at #886's looks, windows, levels and seed. The Politis-White
block of each series is reported beside the block in use. Size and power are read as #769 and #886 read them (`scripts/power_study_769.py`'s paths and rule)
on the candidate's own B1 leg, at the values in force and at the new ones. Development data only: the origins end on 2025-12-23; no locked day is read.

    PYTHONPATH=src python3 -m repo_model.cli build --raw-root tests/fixtures/snapshots/funding_inputs --output PUB.csv \\
        --build-cutoff 2026-09-08T21:31:42+00:00 --decision-time 18:00:00
    RMM_DECISION_TIME=18:00 PYTHONPATH=src python3 scripts/recalibration_1482.py extract --panel PUB.csv
    PYTHONPATH=src python3 scripts/recalibration_1482.py calibrate
    PYTHONPATH=src python3 scripts/recalibration_1482.py power
    PYTHONPATH=src python3 scripts/recalibration_1482.py report
    PYTHONPATH=src python3 scripts/recalibration_1482.py draft      # writes draft amendment 6 into the decision record (a draft)
    PYTHONPATH=src python3 scripts/recalibration_1482.py check

Every command runs in a cloud session in well under two hours (`long-run` does not apply). Standard library only.
"""

from __future__ import annotations

import argparse
import contextlib
import hashlib
import importlib.util
import json
import math
import sys
from datetime import date
from pathlib import Path
from typing import Dict, List, Mapping, Optional, Sequence, Tuple

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))

from repo_model import scoring_protocol as sp  # noqa: E402
from repo_model.confirmation_workers import post_2020, stationary_window_indices  # noqa: E402

RESEARCH = REPO / "docs" / "research"
OUT = RESEARCH / "recalibration-1482"
SERIES = OUT / "series.json"
CALIBRATION = OUT / "calibration.json"
POWER = OUT / "power.json"
PAGE = RESEARCH / "recalibration-1482-result.md"
DECISION = REPO / "docs" / "decisions" / "scoring-protocol.md"
DRAFT_HEADING = "## Draft amendment 6: the values are calibrated on the candidate's own loss differentials (#1482)"
#: The draft goes before the "---" that closes the amendments, where the draft protocol begins.
DRAFT_ANCHOR = "\n---\n\n**Draft scoring protocol, v1"
LOSSES_1392 = RESEARCH / "confirmation-size-power-1392" / "losses.json"
CALIBRATION_878 = RESEARCH / "protocol-calibration-873" / "result.json"
CALIBRATION_886 = RESEARCH / "protocol-calibration-886" / "result.json"
B3_DAILY = REPO / "docs" / "runs" / "published_distribution_daily_h{h}.json"

ORIENTATION = "d = S(benchmark) - S(candidate)"
GENERATOR = "stationary bootstrap, mean block length scoring_protocol.BLOCK_LENGTH, on the post-2020 days"
B3_LEVELS = (0.05, 0.25, 0.5, 0.75, 0.95)
#: Windows per look, the seed and the futility windows are #886's.
CALIBRATION_WINDOWS = {125: 20_000, 250: 20_000}
FUTILITY_WINDOWS = 20_000
SEED = 1
LEGS = ("B1", "B2", "B3")
LEG_TITLES = {
    "B1": "B1 leg: d = S(B1) - S(candidate), grid",
    "B2": "B2 leg: d = S(B2) - S(candidate), grid",
    "B3": "B3 leg: d = S(B3) - S(candidate), B3's five levels",
}
#: The constant each leg's value would replace.
IN_FORCE_NAME = {
    "B1": "CRITICAL_VALUES[GRID_COMPARISON]",
    "B2": "B2_LEG_CRITICAL_VALUES (empty, so CRITICAL_VALUES[GRID_COMPARISON])",
    "B3": "CRITICAL_VALUES[FIVE_LEVEL_COMPARISON]",
}
POWER_PATHS = 2000
POWER_SEED = 1482 * 100_003
SKILLS = (0.0, 0.02, 0.03, 0.04, 0.05, 0.06, 0.08, 0.10, 0.15, 0.20, 0.25, 0.30)
TARGET_POWER = 0.80
LOOKS = (125, 250)
READINGS = {
    "a": ("full", "circular"),
    "b": ("post-2020-04", "circular"),
    "c": ("full", "stationary"),
    "d": ("post-2020-04", "stationary"),
}
ROLES = ("in_force", "new")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_script(name: str, filename: str):
    spec = importlib.util.spec_from_file_location(name, REPO / "scripts" / filename)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


# -- the series -------------------------------------------------------------------------------------------------------


def five_level_days(
    decisions: Sequence[date], dates: Sequence[date], daily: Mapping[int, Mapping[str, Sequence[float]]]
) -> List[date]:
    """The decision days (of `decisions`, on the panel calendar `dates`) for which the published record has a forecast for every lead.

    `daily[h]` maps a target day (ISO) to B3's quantiles. A decision day whose target at lead h is past the calendar is dropped.
    """

    position = {d: i for i, d in enumerate(dates)}
    out = []
    for day in decisions:
        i = position[day]
        if all(i + h < len(dates) and dates[i + h].isoformat() in daily[h] for h in sp.HORIZONS):
            out.append(day)
    return out


def differences(benchmark: Sequence[float], candidate: Sequence[float]) -> List[float]:
    """The protocol's orientation: above zero favours the candidate.

    Raises:
        ValueError: the series are not as long as each other.
    """

    if len(benchmark) != len(candidate):
        raise ValueError(f"{len(benchmark)} benchmark scores but {len(candidate)} candidate scores")
    return [b - c for b, c in zip(benchmark, candidate)]


def leg_series(record: Mapping[str, object]) -> Dict[str, dict]:
    """Each leg's days, benchmark scores and candidate scores, read from `series.json`'s record."""

    grid, five = record["grid"], record["five"]
    days_grid = [date.fromisoformat(d) for d in grid["origins"]]
    days_five = [date.fromisoformat(d) for d in five["origins"]]
    return {
        "B1": {"days": days_grid, "benchmark": grid["B1"], "candidate": grid["candidate"]},
        "B2": {"days": days_grid, "benchmark": grid["B2"], "candidate": grid["candidate"]},
        "B3": {"days": days_five, "benchmark": five["B3"], "candidate": five["candidate"]},
    }


def post_2020_leg(leg: Mapping[str, object]) -> Tuple[List[float], List[float]]:
    """The leg's benchmark scores and differences on the post-2020 days."""

    d = differences(leg["benchmark"], leg["candidate"])
    return post_2020(leg["days"], list(leg["benchmark"]))[1], post_2020(leg["days"], d)[1]


@contextlib.contextmanager
def stationary_windows():
    """Within the block, `scoring_protocol`'s calibration draws its windows by the stationary bootstrap."""

    original = sp._window_indices
    sp._window_indices = stationary_window_indices
    try:
        yield
    finally:
        sp._window_indices = original


# -- the walk ---------------------------------------------------------------------------------------------------------


def extract_command(args) -> int:
    """Walk (s3c-ann-net) over the development window as #1392 does, and write the day scores the study reads."""

    losses = load_script("confirmation_losses_1392_in_1482", "confirmation_losses_1392.py")
    m1388, m1288, m1273, c = losses.m1388, losses.m1288, losses.m1273, losses.c
    m1388.require_instant()
    panel_path = Path(args.panel)
    panel = [row for row in m1273.load_daily_panel(panel_path) if row.date <= m1388.LAST_DAY]
    losses.require_exploratory_window([row.date for row in panel], where="scripts/recalibration_1482")
    splits = losses.load_split_declaration(c.SPLITS)
    registry = json.loads(c.SOURCES.read_text(encoding="utf-8"))
    register = losses.policy_events.load_register()
    table = losses.cal.TermTable(panel, losses.announced_iorb.load_announcements(c.IORB_TABLE), decision_time=c.DECISION_TIME)
    auctions, results = m1273.load_auctions(), m1288.load_results()
    window = "development"
    frame, _notes, _walks, _tables, _cells, _groups = m1288.build(window, panel, splits, registry, table, register, results, auctions, None)
    forecasts = {name: frame.forecasts[name] for name in (m1288.ANNNET, "B1", "B2")}
    grid = {name: sp.day_scores({d: forecasts[name][d] for d in frame.days}, frame.outcome, frame.dates, score=sp.grid_crps) for name in forecasts}
    origins = sorted(set.intersection(*(set(s) for s in grid.values())))
    daily = {}
    for h in sp.HORIZONS:
        record = json.loads(Path(str(B3_DAILY).format(h=h)).read_text(encoding="utf-8"))
        daily[h] = {x["date"]: x for x in record["days"]}
    kept = five_level_days(origins, list(frame.dates), {h: {k: v["quantiles_bps"] for k, v in daily[h].items()} for h in daily})
    position = {d: i for i, d in enumerate(frame.dates)}
    five = sp.level_crps(B3_LEVELS)
    b3_scores, b1_scores, cand_scores = [], [], []
    for day in kept:
        total_b3 = total_b1 = total_c = 0.0
        for h in sp.HORIZONS:
            target = frame.dates[position[day] + h]
            entry = daily[h][target.isoformat()]
            observed = frame.outcome[target]
            if abs(float(entry["actual_bps"]) - float(observed)) > 1e-9:
                raise ValueError(f"the published record's outcome for {target} is {entry['actual_bps']}, the panel's is {observed}")
            total_b3 += five([float(x) for x in entry["quantiles_bps"]], observed)
            total_b1 += five(sp.on_levels(forecasts["B1"][day][h], B3_LEVELS), observed)
            total_c += five(sp.on_levels(forecasts[m1288.ANNNET][day][h], B3_LEVELS), observed)
        n = len(sp.HORIZONS)
        b3_scores.append(total_b3 / n)
        b1_scores.append(total_b1 / n)
        cand_scores.append(total_c / n)
    record = {
        "issue": 1482, "label": "development, not a verdict", "decision_time": "18:00",
        "panel_sha256": losses.panel_sha256(panel_path), "window": window,
        "grid": {"score": "grid CRPS (23 quantiles) averaged over h = 1..5", "origins": [d.isoformat() for d in origins],
                 "B1": [grid["B1"][d] for d in origins], "B2": [grid["B2"][d] for d in origins],
                 "candidate": [grid[m1288.ANNNET][d] for d in origins]},
        "five": {"score": "CRPS on B3's five levels averaged over h = 1..5", "levels": list(B3_LEVELS),
                 "origins": [d.isoformat() for d in kept], "B1": b1_scores, "B3": b3_scores, "candidate": cand_scores},
    }
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    Path(args.output).write_text(json.dumps(record, sort_keys=True) + "\n", encoding="utf-8")
    print("wrote", args.output, len(origins), "grid origins,", len(kept), "five-level origins")
    return 0


def load_series() -> dict:
    return json.loads(SERIES.read_text(encoding="utf-8"))


def tie_to_1392(record: Mapping[str, object], losses: Mapping[str, object], tolerance: float = 1e-9) -> None:
    """The grid scores must be the ones #1392's extract holds for the same walk.

    Raises:
        ValueError: an origin set or a score differs.
    """

    old = losses["windows"][record["window"]]
    if old["origins"] != record["grid"]["origins"]:
        raise ValueError("the walk's origins are not the origins of #1392's extract")
    for mine, theirs in (("B1", "B1"), ("B2", "B2"), ("candidate", "candidate")):
        worst = max(abs(a - b) for a, b in zip(record["grid"][mine], old["scores"][theirs]))
        if worst > tolerance:
            raise ValueError(f"{mine}: the walk differs from #1392's extract by {worst}")


# -- the calibration --------------------------------------------------------------------------------------------------


def calibration(record: Mapping[str, object], seed: int = SEED, windows: Optional[Mapping[int, int]] = None,
                futility_windows: int = FUTILITY_WINDOWS) -> dict:
    windows = dict(CALIBRATION_WINDOWS if windows is None else windows)
    levels = dict(zip(sp.CHECKPOINTS, sp.nominal_levels()))
    legs = leg_series(record)
    b1022 = load_script("block_length_1022_in_1482", "block_length_1022.py")
    efficacy, series_days, mean_d, block, skill = {}, {}, {}, {}, {}
    with stationary_windows():
        for name in LEGS:
            bench, d = post_2020_leg(legs[name])
            series_days[name], mean_d[name] = len(d), sum(d) / len(d)
            skill[name] = sum(d) / sum(bench)
            block[name] = b1022.summarize(d)
            efficacy[name] = {"60": None, **{
                str(n): sp.calibrate_critical_value(d, days=n, level=levels[n], windows=windows[n], seed=seed) for n in windows
            }}
        bench, d = post_2020_leg(legs["B1"])
        futility = {str(n): sp.calibrate_futility_value(bench, d, days=n, level=sp.FUTILITY_LEVEL, windows=futility_windows, seed=seed)
                    for n in sp.CHECKPOINTS}
    return {
        "orientation": ORIENTATION, "generator": GENERATOR,
        "directive": "https://github.com/eleonorabjornberg/repo-market-model/issues/1482",
        "history_first_decision_day": "2020-04-03", "series_sha256": sha256(SERIES),
        "series_days": series_days, "mean_d": mean_d, "skill_against_benchmark": skill, "politis_white": block,
        "nominal_levels": {str(n): levels[n] for n in sp.CHECKPOINTS},
        "windows": {str(n): w for n, w in windows.items()}, "futility_windows": futility_windows,
        "window_block": sp.BLOCK_LENGTH, "seed": seed,
        "efficacy_critical_values": efficacy, "futility_critical_values": futility, "futility_level": sp.FUTILITY_LEVEL,
        "in_force": in_force(),
        "compared_with": {"protocol_calibration_873_sha256": sha256(CALIBRATION_878), "protocol_calibration_886_sha256": sha256(CALIBRATION_886)},
        "note": "same looks, windows, level and seed as the records of #695, #873 and #886; the series are the candidate's. Look 1 has no efficacy value (Q-B). Nothing here is in force.",
    }


def in_force() -> dict:
    """The constants as `scoring_protocol` holds them, for the page to print beside the new ones."""

    grid = {str(n): v for n, v in sp.CRITICAL_VALUES[sp.GRID_COMPARISON].items()}
    five = {str(n): v for n, v in sp.CRITICAL_VALUES[sp.FIVE_LEVEL_COMPARISON].items()}
    b2 = {str(n): sp.B2_LEG_CRITICAL_VALUES.get(sp.GRID_COMPARISON, {}).get(n, v) for n, v in sp.CRITICAL_VALUES[sp.GRID_COMPARISON].items()}
    return {
        "efficacy": {"B1": grid, "B2": b2, "B3": five},
        "futility": {str(n): v for n, v in sp.FUTILITY_CRITICAL_VALUES[sp.GRID_COMPARISON].items()},
        "b2_leg_declared": bool(sp.B2_LEG_CRITICAL_VALUES),
    }


def calibrate_command(args) -> int:
    result = calibration(load_series())
    CALIBRATION.parent.mkdir(parents=True, exist_ok=True)
    CALIBRATION.write_text(json.dumps(result, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result["efficacy_critical_values"], sort_keys=True), json.dumps(result["futility_critical_values"], sort_keys=True))
    return 0


# -- size and power ----------------------------------------------------------------------------------------------------


def value_sets(cal: Mapping[str, object]) -> Dict[str, Dict[int, float]]:
    """The B1 leg's efficacy values at looks 2 and 3, in force and new."""

    return {
        "in_force": {n: cal["in_force"]["efficacy"]["B1"][str(n)] for n in LOOKS},
        "new": {n: cal["efficacy_critical_values"]["B1"][str(n)] for n in LOOKS},
    }


def history_scores(leg: Mapping[str, object], history: str) -> Tuple[List[float], List[float]]:
    days, bench, cand = leg["days"], leg["benchmark"], leg["candidate"]
    if history == "post-2020-04":
        return post_2020(days, list(bench))[1], post_2020(days, list(cand))[1]
    if history == "full":
        return list(bench), list(cand)
    raise ValueError(f"unknown history {history!r}")


def power_command(args) -> int:
    study = load_script("power_study_769_in_1482", "power_study_769.py")
    cal = json.loads(CALIBRATION.read_text(encoding="utf-8"))
    if cal["series_sha256"] != sha256(SERIES):
        raise ValueError("calibration.json was made from another series.json")
    sets = value_sets(cal)
    leg = leg_series(load_series())["B1"]
    result = {
        "series_sha256": sha256(SERIES), "calibration_sha256": sha256(CALIBRATION),
        "constants": {"paths": args.paths, "seed": POWER_SEED, "mme": sp.MME, "looks": list(LOOKS), "path_days": study.PATH_DAYS,
                      "block_length": sp.BLOCK_LENGTH, "hac_lag": sp.HAC_LAG, "target_power": TARGET_POWER, "skills": list(SKILLS),
                      "critical_values": {role: {str(n): v for n, v in sets[role].items()} for role in ROLES}},
        "note": "the B1 leg only; the B2 half of Supported is not simulated, so each power is an upper bound",
        "readings": {},
    }
    for name, (history, generator) in READINGS.items():
        s1, cand = history_scores(leg, history)
        cells = {}
        for role in ROLES:
            for delta in SKILLS:
                cell = study.detections(s1, cand, delta=delta, noise=1.0, generator=generator, paths=args.paths, seed=POWER_SEED,
                                        critical=sets[role])
                cells[f"{role}|{delta}"] = cell
                print(name, history, generator, role, delta, json.dumps(cell["gated"]), flush=True)
        result["readings"][name] = {"history": history, "generator": generator, "series_days": len(s1), "cells": cells}
    POWER.parent.mkdir(parents=True, exist_ok=True)
    POWER.write_text(json.dumps(result, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    print("wrote", POWER)
    return 0


def smallest_skill(cells: Mapping[str, dict], role: str, look: str = "250", kind: str = "gated") -> Optional[float]:
    """The smallest skill on the grid whose power at `look` days reaches the target, or None."""

    for delta in SKILLS:
        if delta > 0 and cells[f"{role}|{delta}"][kind][look] >= TARGET_POWER:
            return delta
    return None


# -- the page ----------------------------------------------------------------------------------------------------------


def num(v: Optional[float]) -> str:
    return "n/a" if v is None else f"{v:.3f}"


def pct(p: float, se: Optional[float] = None) -> str:
    return f"{100 * p:.1f}%" if se is None else f"{100 * p:.1f}% ± {196 * se:.1f}"


def share(p: float, paths: int) -> str:
    return pct(p, math.sqrt(p * (1 - p) / paths))


def differs(new: float, old: float, tolerance: float = 0.05) -> bool:
    """Two values are the same for the page's purposes when they agree to within `tolerance` in absolute terms."""

    return abs(new - old) > tolerance


def render(cal: Mapping[str, object], power: Mapping[str, object]) -> str:
    old878 = json.loads(CALIBRATION_878.read_text(encoding="utf-8"))
    old886 = json.loads(CALIBRATION_886.read_text(encoding="utf-8"))
    paths = power["constants"]["paths"]
    new_eff, force = cal["efficacy_critical_values"], cal["in_force"]
    L: List[str] = []
    a = L.append
    a("# Recalibrating the critical and futility values on (s3c-ann-net)'s loss differentials: result (H1 step 4, #1482)")
    a("")
    a("**Development and simulated data, not a verdict.** No locked day is read: the origins end on 2025-12-23. Every figure is read from "
      "`docs/research/recalibration-1482/series.json`, `calibration.json` and `power.json` by `scripts/recalibration_1482.py report` "
      "(with the records of #878 and #886 beside them). `scoring_protocol.CRITICAL_VALUES`, `FUTILITY_CRITICAL_VALUES`, "
      "`B2_LEG_CRITICAL_VALUES` are unchanged by this step, and so is the record in force; `docs/decisions/scoring-protocol.md` gains only a marked draft, "
      "\"Draft amendment 6\", which is not in force until she merges it.")
    a("")
    a("## 1. What was calibrated")
    a("")
    a(f"Series are the candidate's own, in the orientation the test applies, `{cal['orientation']}`, on the post-2020 decision days "
      f"(from {cal['history_first_decision_day']}; the cut of 2019-09-18 of #1022 falls before it, so no day is removed). Windows are drawn by the "
      f"{cal['generator']} (mean block {cal['window_block']}, her ruling of 22 October 2026 on #1022), at #886's looks, levels "
      f"(60 days has no efficacy value, Q-B), windows ({cal['windows']['125']:,} per look; {cal['futility_windows']:,} for futility) and seed {cal['seed']}.")
    a("")
    a("| leg | series | days | mean d | development skill against the benchmark | Politis-White block (in use: " + str(cal["window_block"]) + ") |")
    a("|---|---|---|---|---|---|")
    for name in LEGS:
        pw = cal["politis_white"][name]
        a(f"| {name} | {LEG_TITLES[name]} | {cal['series_days'][name]:,} | {cal['mean_d'][name]:.4f} | {cal['skill_against_benchmark'][name]:.1%} | {'n/a' if pw.get('thin') else format(pw['politis_white'], '.1f')} |")
    a("")
    a("## 2. The values, beside the ones in force")
    a("")
    a("Each cell is the critical value `c` of the one-sided bound `mean - c * se` (efficacy) or `skill + c * se` (futility). "
      "\"In force\" is `scoring_protocol` today; \"#878\" and \"#886\" are the scratch records of those steps (the benchmarks' own series); "
      "\"new\" is this step.")
    a("")
    a("| value | days | in force | #878 (circular, full history) | #886 (stationary, post-2020) | new (candidate's series) | changes? |")
    a("|---|---|---|---|---|---|---|")
    rows = []
    for name in LEGS:
        for n in ("125", "250"):
            if name == "B3":
                prior878 = old878["comparison_critical_values"][sp.FIVE_LEVEL_COMPARISON][n]
                prior886 = old886["comparison_critical_values"][sp.FIVE_LEVEL_COMPARISON][n]
            else:
                prior878 = old878["comparison_critical_values"][sp.GRID_COMPARISON][n]
                prior886 = old886["comparison_critical_values"][sp.GRID_COMPARISON][n]
            rows.append((f"efficacy, {name} leg", n, force["efficacy"][name][n], prior878, prior886, new_eff[name][n]))
    for n in ("60", "125", "250"):
        rows.append(("futility (upper bound of skill, B1 leg)", n, force["futility"][n],
                     old878["futility_critical_values"][sp.GRID_COMPARISON][n], old886["futility_critical_values"][sp.GRID_COMPARISON][n],
                     cal["futility_critical_values"][n]))
    changed = False
    for title, n, f_, o878, o886, new in rows:
        moves = abs(new - f_) > 0.05 * abs(f_)
        changed = changed or moves
        a(f"| {title} | {n} | {num(f_)} | {num(o878)} | {num(o886)} | {num(new)} | {'differs' if moves else 'within 5% of the one in force'} |")
    a("")
    a(f"A value \"differs\" when it is more than 5% from the one in force; that threshold is this page's, not the protocol's. "
      + ("**At least one value differs, so the amendment is drafted for her merge** (section 6)." if changed
         else "No value differs by that reading; the values in force may stand."))
    a("")
    a("## 3. Size and power at the values in force and at the new ones")
    a("")
    a(f"`scripts/power_study_769.py`'s rule and paths ({paths:,} per cell, seed {power['constants']['seed']}), on the candidate's B1 leg: "
      f"a path of {power['constants']['path_days']} days is drawn from the history by the reading's generator, the candidate's skill is set to the stated "
      "value by shifting the mean of d (its noise is the candidate's own), and the bound is read at looks 125 and 250 at each set of values. "
      "Size is the share of null paths (skill 0) detected by that look; power is the MME-gated share (point skill against B1 at least "
      f"{sp.MME:.0%}). The B2 half of Supported is not simulated, so each power is an upper bound. Each figure carries ± 1.96 Monte Carlo standard errors.")
    a("")
    cv = power["constants"]["critical_values"]
    a(f"Values read: in force {num(cv['in_force']['125'])} / {num(cv['in_force']['250'])}, new {num(cv['new']['125'])} / {num(cv['new']['250'])} (125 / 250 days).")
    a("")
    a("| reading | values | size 125 | size 250 | 3% 125 | 3% 250 | 10% 125 | 10% 250 |")
    a("|---|---|---|---|---|---|---|---|")
    for rname, r in power["readings"].items():
        for role, label in (("in_force", "in force"), ("new", "new")):
            cells = r["cells"]
            row = [share(cells[f"{role}|{d}"][kind][str(n)], paths) for d, kind in ((0.0, "ungated"), (0.03, "gated"), (0.1, "gated")) for n in LOOKS]
            a(f"| ({rname}) {r['history']}, {r['generator']} | {label} | " + " | ".join(row) + " |")
    a("")
    a("## 4. Power by skill, and the minimum meaningful effect")
    a("")
    a("MME-gated power by 250 days (the confirmation test's last look) on reading (d), post-2020 days with stationary-bootstrap paths, which is the reading the "
      "confirmation days resemble, at each skill on the grid. The smallest skill that reaches "
      f"{TARGET_POWER:.0%} is shown for every reading.")
    a("")
    a("| skill | power 250, in force | power 250, new | power 125, new |")
    a("|---|---|---|---|")
    d = power["readings"]["d"]["cells"]
    for delta in SKILLS[1:]:
        a(f"| {delta:.0%} | {share(d[f'in_force|{delta}']['gated']['250'], paths)} | {share(d[f'new|{delta}']['gated']['250'], paths)} | "
          f"{share(d[f'new|{delta}']['gated']['125'], paths)} |")
    a("")
    a("| reading | smallest skill on the grid with power at least 80% by 250 days, in force | new |")
    a("|---|---|---|")
    for rname, r in power["readings"].items():
        fi, nw = smallest_skill(r["cells"], "in_force"), smallest_skill(r["cells"], "new")
        a(f"| ({rname}) {r['history']}, {r['generator']} | {'none up to ' + format(SKILLS[-1], '.0%') if fi is None else format(fi, '.0%')} | "
          f"{'none up to ' + format(SKILLS[-1], '.0%') if nw is None else format(nw, '.0%')} |")
    a("")
    a("## 5. Marked question for Eleonora: the minimum meaningful effect (#1354, question 2)")
    a("")
    own = cal["skill_against_benchmark"]["B1"]
    d_new = power["readings"]["d"]["cells"]
    p3, p10 = d_new["new|0.03"]["gated"]["250"], d_new["new|0.1"]["gated"]["250"]
    p20, p25, p30 = (d_new[f"new|{k}"]["gated"]["250"] for k in (0.2, 0.25, 0.3))
    reach = smallest_skill(power["readings"]["d"]["cells"], "new")
    a("**Marked question (protocol section 13; the default applies if she has not answered by the next 5 pm batch).** Her ruling of 6 November 2026 "
      "(#1354, question 2, option 2) sets the MME from the power study once the recalibration is in. The study cannot do that by its own rule: on reading (d) "
      f"with the new values the test's power by 250 days is {share(p3, paths)} at 3%, {share(p10, paths)} at 10%, {share(p20, paths)} at 20%, "
      f"{share(p25, paths)} at 25% and {share(p30, paths)} at 30%, so "
      + ("no skill on the grid reaches 80% power" if reach is None else f"the smallest skill on the grid that reaches 80% power is {reach:.0%}")
      + f". The candidate's own development skill against B1 on these days is {own:.1%}. Options:")
    a("")
    a("1. Keep 3% (protocol decision 5) and record that the recalibrated test, read as protocol v1 reads it, cannot reach 80% power at 3% by 250 days. "
      "Whether the confirmation is longer or read by another test is the confirmation design's (#1394, #1392), not this protocol's. **Recommended and default: changes no claim.**")
    a("2. Set the MME to a value she names from the table in section 4, accepting that its power by 250 days is the figure beside it.")
    a("3. Change the power target or the horizon of the rule (a different section 13 decision), then read the MME from the study again.")
    a("")
    a("## 6. Draft amendment, and what is not decided")
    a("")
    a("Nothing here is in force. Under protocol section 13 a different value is her decision; `scoring_protocol.py` is not edited by "
      "this PR, and the decision record gains only the marked draft below (draft amendment 6). If she adopts the new values, a follow-up directive sets `CRITICAL_VALUES`, `B2_LEG_CRITICAL_VALUES` and `FUTILITY_CRITICAL_VALUES` to the "
      "\"new\" column of section 2, and the amendment below is what she would merge.")
    a("")
    a("> **DRAFT, for Eleonora's merge. Not in force.** Section 5 (critical values): the efficacy and futility values are calibrated on the loss differentials of the "
      "candidate `(s3c-ann-net)` against B1, B2 and B3, in the orientation d = S(benchmark) - S(candidate), on post-2020 stationary-bootstrap windows (mean block 10), "
      "and take the \"new\" column of section 2 of `docs/research/recalibration-1482-result.md`.")
    a("")
    a("## 7. What this does not show")
    a("")
    a("- One candidate, one walk. The candidate may change after the ablations; the values are re-run if it does (#1354, question 1).")
    a("- The B2 half of Supported and futility stopping are not simulated in section 3, as in #769 and #886. The B2 leg's and the B3 leg's values are calibrated, "
      "but their size and power are not simulated.")
    a("- The B3 leg uses the days on which the published record has all five leads, scored on B3's five levels with B1 and the candidate read at those levels.")
    a("- 2026 days are not read; no day of the lockbox is read.")
    a("")
    a("## 8. Ruling recorded, 6 November 2026: the MME stays at 3% (#1498)")
    a("")
    a("**Dated note, 6 November 2026.** Eleonora ruled on the marked question of section 5 (decision docket, 10:12 am ET, card mme-1490, option 1; "
      "relayed on #1482, comment 6688184333): keep the minimum meaningful effect at 3% (protocol decision 5). This note records it and changes nothing else.")
    a("")
    a(f"- **Power at 3% by 250 days.** On reading (d) with the new values the test's power at 3% by 250 days is {share(p3, paths)}, "
      f"and {share(d_new['in_force|0.03']['gated']['250'], paths)} at the values in force (section 4). "
      + ("No skill on the grid reaches 80% power, so 80% power at 3% is out of reach by 250 confirmation days."
         if reach is None else f"The smallest skill on the grid that reaches 80% power is {reach:.0%}, so 80% power at 3% is out of reach by 250 confirmation days."))
    a("- **Length or test.** Whether the confirmation is longer, or read by another test, is left to the confirmation design (#1392, #1394). This ruling does not decide it.")
    a("- **Unchanged.** No threshold, critical value or decision record is changed by this note.")
    a("")
    return "\n".join(L) + "\n"


def draft_text(cal: Mapping[str, object]) -> str:
    """Draft amendment 6 of the decision record: the new values, written from `calibration.json` and nothing else."""

    force, new = cal["in_force"], cal["efficacy_critical_values"]
    rows = []
    for name, title in (("B1", "efficacy, B1 leg (`CRITICAL_VALUES[GRID_COMPARISON]`)"),
                        ("B2", "efficacy, B2 leg (`B2_LEG_CRITICAL_VALUES`; empty today, so the grid value)"),
                        ("B3", "efficacy, B3 against the candidate, five levels (`CRITICAL_VALUES[FIVE_LEVEL_COMPARISON]`)")):
        for n in ("125", "250"):
            rows.append(f"| {title} | {n} | {num(force['efficacy'][name][n])} | {num(new[name][n])} |")
    for n in ("60", "125", "250"):
        rows.append(f"| futility, B1 leg (`FUTILITY_CRITICAL_VALUES[GRID_COMPARISON]`) | {n} | {num(force['futility'][n])} | {num(cal['futility_critical_values'][n])} |")
    return "\n".join([
        DRAFT_HEADING, "",
        "**Status: a draft by the pull request that closes #1482, for Eleonora to merge. Nothing here is in force until she merges it** (§13: this record is merged by her, "
        "not under delegated review). Until then item 5 and Q-C stand as written, `CRITICAL_VALUES`, `FUTILITY_CRITICAL_VALUES` and `B2_LEG_CRITICAL_VALUES` in "
        "`scoring_protocol.py` are unchanged, and `docs/research/milestones.json` does not mark H1.M3. It is an alternative to draft amendments 1 to 3: she merges at most one "
        "set of values. It follows her ruling of 6 November 2026 on #1354 (question 1, option (a)); the values are re-run if the candidate changes.", "",
        "**What it changes.** Draft amendments 1 to 3 calibrated on series of the benchmarks (S(B2) − S(B1), S(B3) − S(B1)) because no candidate stood behind them. "
        "The values below are calibrated on the loss differentials of the current H5 candidate (s3c-ann-net) against B1, B2 and B3, d = S(benchmark) − S(candidate), "
        "on the stationary-bootstrap windows of the post-2020 days (from 2020-04-03; mean block 10, her ruling of 22 October 2026 on #1022), with #886's looks, levels, "
        "windows and seed 1:", "",
        "| value | days | in force | amended |", "|---|---|---|---|", *rows, "",
        "Look 1 still has no efficacy value (Q-B). The windows, the series, each series' Politis-White block, and the size and power at the values in force and at these "
        "(by 125 and 250 days, four readings, with Monte Carlo intervals) are in `docs/research/recalibration-1482-result.md` and `docs/research/recalibration-1482/`.", "",
        "**What she decides.** Whether to merge this amendment as drafted, and the minimum meaningful effect, which the result page puts as a marked question with the power figures.", "",
    ])


def draft_command(args) -> int:
    cal = json.loads(CALIBRATION.read_text(encoding="utf-8"))
    text = DECISION.read_text(encoding="utf-8")
    if DRAFT_HEADING in text:
        start = text.index(DRAFT_HEADING)
        end = text.index(DRAFT_ANCHOR)
        text = text[:start] + draft_text(cal) + text[end:]
    else:
        if text.count(DRAFT_ANCHOR) != 1:
            raise ValueError("the anchor of the draft amendments is not in the decision record exactly once")
        text = text.replace(DRAFT_ANCHOR, "\n" + draft_text(cal) + DRAFT_ANCHOR)
    DECISION.write_text(text, encoding="utf-8")
    print("wrote", DECISION)
    return 0


def report_command(args) -> int:
    cal = json.loads(CALIBRATION.read_text(encoding="utf-8"))
    power = json.loads(POWER.read_text(encoding="utf-8"))
    PAGE.write_text(render(cal, power), encoding="utf-8")
    print("wrote", PAGE)
    return 0


def check_command(args) -> int:
    for path in (SERIES, CALIBRATION, POWER, PAGE):
        if not path.exists():
            print(f"{path.relative_to(REPO)} is missing: run the commands in the script's docstring", file=sys.stderr)
            return 1
    cal = json.loads(CALIBRATION.read_text(encoding="utf-8"))
    power = json.loads(POWER.read_text(encoding="utf-8"))
    if cal["series_sha256"] != sha256(SERIES) or power["series_sha256"] != sha256(SERIES) or power["calibration_sha256"] != sha256(CALIBRATION):
        print("the records were made from other inputs than the ones on disk", file=sys.stderr)
        return 1
    if cal["in_force"] != in_force():
        print("scoring_protocol's values changed since calibration.json was written", file=sys.stderr)
        return 1
    if PAGE.read_text(encoding="utf-8") != render(cal, power):
        print("the page is not what the records give; run `report`", file=sys.stderr)
        return 1
    if draft_text(cal) not in DECISION.read_text(encoding="utf-8"):
        print("the draft amendment in the decision record is not what the records give; run `draft`", file=sys.stderr)
        return 1
    print("ok")
    return 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="command", required=True)
    e = sub.add_parser("extract")
    e.add_argument("--panel", required=True)
    e.add_argument("--output", default=str(SERIES))
    e.set_defaults(func=extract_command)
    sub.add_parser("calibrate").set_defaults(func=calibrate_command)
    p = sub.add_parser("power")
    p.add_argument("--paths", type=int, default=POWER_PATHS)
    p.set_defaults(func=power_command)
    sub.add_parser("report").set_defaults(func=report_command)
    sub.add_parser("draft").set_defaults(func=draft_command)
    sub.add_parser("check").set_defaults(func=check_command)
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
