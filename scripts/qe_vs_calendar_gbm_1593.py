"""The frozen candidate (s3c-ann-net) against `gbm_funding_cal_direct` on quarter-end turns and year-ends (#1593; H5 step 3, development tier; her rulings of 12 and 13 November 2026).

A development comparison, never a verdict and never an adoption (scoring protocol v1). It is the comparison only: no combination arm, no refit, no new forecast.
Nothing is declared again; the candidate is frozen (`docs/research/h5-candidate.json`) and the variant is #1036's.

**Where the two forecasts come from.** The candidate's walk is regenerated as #1548 and #1572 regenerate it (the panel, the refits and the forecasts of
`qe_event_model_1548`'s frame, at the declared 18:00 decision instant), and its figures on the whole group are checked against #1548's record to 1e-9 before
anything is paired (`reproduce_candidate`; the walk regenerates bit-identically, #1533). The direct variant's forecasts are read from #1036's five walks
(`~/rmm-1027/WALKS`, on Eleonora's Mac), by `aligned_calendar_1027.load_walks`, which refuses a walk made from another published or scratch panel. Neither
side fits anything here that its own walk did not.

**The pairing.** The decision days both cover, whose five-day target is no later than 2025-12-31; on each, the same targets and the same outcomes (the two frames are
read from the same published panel; `require_same_outcomes` refuses a difference). A cell is a (decision day, lead h = 1 to 5) whose target day is of type
`quarter_end_turn` or `year_end` as `turn_days.reporting_day_type` reads it (the labels of #1135 in force since #1161; `require_current_day_types` refuses the
retired month_end and quarter_end flags). The regime of a cell is the declared regime of the calendar date of the quarter-end its event is named for (#1572's rule).

**What is reported.** For the candidate and the variant on the same cells, by turn type (quarter-end turns and year-ends apart, and both pooled) and by regime: the 90%
coverage, the miss rates above q95 and below q01 (and the two others #1548 carries), grid CRPS and upper-tail twCRPS, each with the paired difference (the GBM minus the
candidate) and its 90% event-cluster interval (whole events resampled, 2,000 resamples, seed 1593; the method of #1548 and #1572, whose unit is the independent turn).
Beside it, for grid CRPS and upper-tail twCRPS, the studentized stationary bootstrap of scoring protocol v1 on the per-target-day means over the leads (mean block 10, HAC
lag 10, 95%, 10,000 draws; a group of no more than ten days carries its difference and no interval). A cell of fewer than five events is flagged.

**Not done.** No combination arm and no adoption (her ruling). Nothing is scored after 2025-12-31 or on a locked day. The GBM's walks were made at the 16:00 instant of
the published records, the candidate's at the 18:00 of #1312; the page says so, and no refit of the GBM at 18:00 is made here.

Commands, from a clone of the branch (the Mac paste is `scripts/mac_score_1593.sh`; PUB.csv and AUG3.csv are the panels of #1036's paste, digest 4ddc3882... for PUB.csv):

    PYTHONPATH=src python3 scripts/qe_vs_calendar_gbm_1593.py check-walks ~/rmm-1027/WALKS
    PYTHONPATH=src python3 scripts/qe_vs_calendar_gbm_1593.py score --published PUB.csv --panel AUG3.csv --walks ~/rmm-1027/WALKS \\
        --output docs/research/qe-vs-calendar-gbm-1593/result.json
    PYTHONPATH=src python3 scripts/qe_vs_calendar_gbm_1593.py page --score docs/research/qe-vs-calendar-gbm-1593/result.json \\
        --output docs/research/qe-vs-calendar-gbm-1593-result.md
    PYTHONPATH=src python3 scripts/qe_vs_calendar_gbm_1593.py log --score docs/research/qe-vs-calendar-gbm-1593/result.json \\
        --output docs/research/log/<date>-model-01593-H5-step3.md --date <date>

Stdlib only (the walks are read as JSON; nothing is fitted).
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from datetime import date
from pathlib import Path
from types import SimpleNamespace
from typing import Callable, Dict, List, Mapping, Optional, Sequence

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))

#: scripts/ functions that compute a CRPS, classified for tests/test_lockbox.py
LOCKBOX_CRPS = {
    "target_day_rows": (
        "delegates",
        "scores the paired cells of the candidate and of #1036's walks; `_score` calls `require_study_window` on every decision day and target day before it builds a cell, "
        "and refuses any day after 2025-12-31 (#1593)",
    ),
}

def _load(name: str, alias: Optional[str] = None):
    """Load `scripts/<name>.py` as a module registered under `alias` (default `name`)."""

    alias = alias or name
    path = REPO / "scripts" / f"{name}.py"
    held = sys.modules.get(alias)
    if held is not None and getattr(held, "__file__", None) == str(path):
        return held
    spec = importlib.util.spec_from_file_location(alias, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[alias] = module
    spec.loader.exec_module(module)
    return module


from repo_model import scoring_protocol as sp, turn_days  # noqa: E402
from repo_model.baseline import panel_sha256  # noqa: E402
from repo_model.splits import LookAheadError  # noqa: E402

#: #1572's script (and through it #1548's, #1402's and #1321's chain), under an alias of its own; #1591's, for its interval arithmetic.
m1572 = _load("qe_event_regime_1572", "qe_event_regime_1572_in_1593")
m1591 = _load("direct_pairs_intervals_1591", "direct_pairs_intervals_1591_in_1593")
m1548, m1402, m1255, m1321, m1288, m1273, c, k_mod = (m1572.m1548, m1572.m1402, m1572.m1548.m1255, m1572.m1321, m1572.m1288, m1572.m1273, m1572.c, m1572.m1548.k_mod)

LAST_TARGET = m1591.LAST_TARGET  # 2025-12-31: the last target day of #1036's walks
SEED = 1593
EVENT_REPS = m1548.EVENT_REPS
DRAWS = sp.DRAWS
HORIZONS = sp.HORIZONS
CANDIDATE = m1548.ANNNET
DIRECT = "gbm_funding_cal_direct"
MEASURES = m1548.MEASURES
REGIMES, FEW, SPLITS, SCOPES = m1572.REGIMES, m1572.FEW, m1572.SPLITS, m1572.SCOPES
SCOPE_TITLES = m1572.SCOPE_TITLES
GROUP_TYPES = m1548.GROUP_TYPES
TOLERANCE = m1572.TOLERANCE
regime_table = m1572.regime_table
regime_of_event = m1572.regime_of_event
DAY_METRICS = ("grid_crps", "upper_tail_twcrps")
WINDOW = "development"


# -- guards ------------------------------------------------------------------------------------------------------------------


def require_study_window(days: Sequence[date]) -> None:
    """Refuse a run that would read a day after 2025-12-31: raises `LookAheadError`."""

    late = [day for day in days if day > LAST_TARGET]
    if late:
        raise LookAheadError(f"qe_vs_calendar_gbm_1593 reads no day after {LAST_TARGET}; asked for {min(late)}")


def require_current_day_types() -> None:
    """Refuse a run under the retired month_end and quarter_end reading (`turn_days.legacy_reading`): raises `ValueError`."""

    if not turn_days.in_force():
        raise ValueError("the turn labels of #1135 are not in force; this comparison groups by them, not by the retired month_end and quarter_end flags")


def common_days(days: Sequence[date], walked: Mapping[date, object], target: Callable[[date, int], date]) -> List[date]:
    """The decision days of `days` the other side's walks cover and whose target at the longest lead is in the study (the same days for both: a paired test needs them)."""

    return [d for d in days if d in walked and target(d, max(HORIZONS)) <= LAST_TARGET]


def require_same_outcomes(days: Sequence[date], target_a: Callable[[date, int], date], target_b: Callable[[date, int], date],
                          outcome_a: Mapping[date, float], outcome_b: Mapping[date, float]) -> None:
    """Both frames aim every (decision day, lead) at the same target day and observe the same value there.

    Raises:
        ValueError: a target day or an outcome differs, or a target has no outcome in one frame.
    """

    for d in days:
        for h in HORIZONS:
            ta, tb = target_a(d, h), target_b(d, h)
            if ta != tb:
                raise ValueError(f"{d} lead {h}: the walks' frame aims at {ta}, the candidate's at {tb}")
            if ta not in outcome_a or tb not in outcome_b:
                raise ValueError(f"{d} lead {h}: no outcome at {ta} in one of the frames")
            a, b = outcome_a[ta], outcome_b[tb]
            if a != b:
                raise ValueError(f"{d} lead {h}: the outcome at {ta} is {a!r} in the walks' frame and {b!r} in the candidate's")


def reproduce_candidate(rows: Mapping[str, Optional[dict]], group: Mapping[str, object]) -> None:
    """The candidate's figures on the whole group (pooled and by type), regenerated here, against #1548's record: every mean and interval equal. The arm's are not compared.

    Raises:
        ValueError: a count or a figure differs.
    """

    there = {"group": group["pooled"], "quarter_end_turn": group["by_type"]["quarter_end_turn"], "year_end": group["by_type"]["year_end"]}
    for scope, theirs in there.items():
        mine = rows[scope]
        if (mine is None) != (theirs is None):
            raise ValueError(f"{scope}: one of the two is empty")
        if mine is None:
            continue
        if (mine["cells"], mine["events"]) != (theirs["cells"], theirs["events"]):
            raise ValueError(f"{scope}: cells and events differ from #1548's")
        for name in MEASURES:
            a, b = mine["measures"][name]["candidate"], theirs["measures"][name]["candidate"]
            if abs(a - b) > TOLERANCE:
                raise ValueError(f"{scope} {name}: the regenerated candidate gives {a!r} against #1548's {b!r}")
            for x, y in zip(mine["measures"][name]["candidate_interval"], theirs["measures"][name]["candidate_interval"]):
                if abs(x - y) > TOLERANCE:
                    raise ValueError(f"{scope} {name} interval: {x!r} against #1548's {y!r}")


# -- the pairing -------------------------------------------------------------------------------------------------------------


def view_of(frame, days: Sequence[date]):
    """A frame restricted to `days`, with what `qe_event_model_1548.group_cells` reads."""

    return SimpleNamespace(days=list(days), position=frame.position, target=frame.target, outcome=frame.outcome)


def paired_cells(frame, days: Sequence[date], labels: Mapping[int, str], table, candidate, other) -> List[dict]:
    """The group's cells on `days`, #1548's `group_cells` with the candidate as its candidate and the variant as its arm (so a difference is the variant minus the candidate)."""

    return m1548.group_cells(view_of(frame, days), labels, table, candidate, other)


def target_day_rows(frame, days: Sequence[date], labels: Mapping[int, str], candidate, other) -> Dict[date, dict]:
    """Per target day of the group's types: the mean over the leads that aim at it of each model's grid CRPS and upper-tail twCRPS, with the day's type and event."""

    sums: Dict[date, dict] = {}
    for d in days:
        for h in HORIZONS:
            label = labels[frame.position[d] + h]
            if label not in GROUP_TYPES:
                continue
            t = frame.target(d, h)
            y = frame.outcome[t]
            entry = sums.setdefault(t, {"type": label, "event": m1548.event_of(t), "n": 0, "cand": [0.0, 0.0], "arm": [0.0, 0.0]})
            entry["n"] += 1
            for name, forecast in (("cand", candidate), ("arm", other)):
                q = forecast[d][h]
                entry[name][0] += sp.grid_crps(q, y)
                entry[name][1] += sp.upper_tail_twcrps(q, y)
    out = {}
    for t, e in sums.items():
        if e["event"] is None:
            raise ValueError(f"{t}: a {e['type']} day with no turn event")
        out[t] = {"type": e["type"], "event": e["event"], "cand": tuple(v / e["n"] for v in e["cand"]), "arm": tuple(v / e["n"] for v in e["arm"])}
    return out


def _interval(scores: Mapping[date, tuple], seed: int, draws: int) -> dict:
    """`direct_pairs_intervals_1591.excess_interval`, with a difference that is the same on every day (no long-run variance, so nothing to studentize) reported without an interval."""

    try:
        return m1591.excess_interval(scores, seed=seed, draws=draws)
    except sp.ProtocolError:
        days = sorted(scores)
        return {"days": len(days), "excess": sum(scores[d][1] - scores[d][0] for d in days) / len(days), "lower": None, "upper": None,
                "note": "the difference is the same on every day: no long-run variance to studentize"}


def day_level(rows: Mapping[date, dict], *, seed: int = SEED, draws: int = DRAWS) -> dict:
    """`out[scope][regime or "all"]`: `None` for an empty set, else per metric the mean difference (the variant minus the candidate) of the per-target-day means and the
    studentized stationary bootstrap's 95% interval (`direct_pairs_intervals_1591.excess_interval`: no interval for a group of no more than the HAC lag in days)."""

    out: dict = {}
    for scope in SCOPES:
        chosen = {t: r for t, r in rows.items() if scope == "group" or r["type"] == scope}
        out[scope] = {}
        for regime in ("all",) + REGIMES:
            members = {t: r for t, r in chosen.items() if regime == "all" or regime_of_event(r["event"]) == regime}
            if not members:
                out[scope][regime] = None
                continue
            out[scope][regime] = {metric: _interval({t: (r["cand"][i], r["arm"][i]) for t, r in members.items()}, seed, draws) for i, metric in enumerate(DAY_METRICS)}
    return out


# -- the two sides -----------------------------------------------------------------------------------------------------------


def direct_side(published: Path, scratch: Path, walks: Path):
    """The variant's forecast on each decision day its five walks cover, with the frame of the published panel at the walks' own (16:00) instant: `(frame, forecasts)`.

    Raises:
        ValueError: a walk was made from another published or scratch panel, or some but not all leads are present.
    """

    from repo_model.data import load_daily_panel
    from repo_model.evaluation_splits import load_split_declaration

    ac, b960 = _load("aligned_calendar_1027", "aligned_calendar_1027_in_1593"), _load("b1_calendar_960", "b1_calendar_960_in_1593")
    pub = load_daily_panel(published)
    registry = json.loads((REPO / "metadata" / "sources.json").read_text(encoding="utf-8"))
    frame, _notes = b960.build_frame(pub, panel_sha256(published), load_split_declaration(REPO / "metadata" / "evaluation_splits.json"), registry,
                                     b960.s761.committed_declaration(b960.DECLARATION), None)
    return frame, ac.load_walks(walks, DIRECT, published, scratch, frame)


def candidate_side(published: Path, first: Optional[date] = None):
    """The candidate's #1548 frame of the development window, its forecasts and what the cells need (the walk at the declared 18:00 instant; run under `decision_instant_pinned`).

    Returns `(frame, forecasts, labels, table, splits, panel, sha, notes)`.
    """

    from repo_model import announced_iorb, policy_events
    from repo_model import spread_mr_calendar as cal
    from repo_model.evaluation_splits import load_split_declaration
    from repo_model.exploration import require_exploratory_window

    sha = panel_sha256(published)
    panel = [row for row in m1548.load_daily_panel(published) if row.date <= m1548.LAST_DAY]
    require_exploratory_window([row.date for row in panel], where="scripts/qe_vs_calendar_gbm_1593")
    splits = load_split_declaration(c.SPLITS)
    registry = json.loads(c.SOURCES.read_text(encoding="utf-8"))
    register = policy_events.load_register()
    table = cal.TermTable(panel, announced_iorb.load_announcements(c.IORB_TABLE), decision_time=c.DECISION_TIME)
    auctions, results = m1273.load_auctions(), m1288.load_results()
    frame, notes, _mine, _cells, _groups = m1255.build(WINDOW, panel, splits, registry, table, register, first)
    walk = m1402.walks_of(WINDOW, frame, panel, splits, registry, results, auctions, first)
    labels = m1402.type_of_rows(panel, splits)
    forecasts = m1255.s3c_forecasts(frame, register, {d: walk.forecasts[m1402.ARM_NET][d] for d in frame.days})
    return frame, forecasts, labels, table, splits, panel, sha, dict(notes, refits=len(walk.fits))


def group_rows(cells: Sequence[dict], reps: int) -> Dict[str, Optional[dict]]:
    inside = [x for x in cells if x["in_group"]]
    return {"group": m1548.summarise(inside, reps=reps), **{t: m1548.summarise([x for x in inside if x["type"] == t], reps=reps) for t in GROUP_TYPES}}


def summarise_pairs(cells: Sequence[dict], rows: Mapping[date, dict], splits, *, reps: int, draws: int) -> dict:
    return {"table": regime_table(cells, splits, reps=reps), "day_level": day_level(rows, seed=SEED, draws=draws)}


def score(args) -> int:
    published, scratch, walks = Path(args.published), Path(args.panel), Path(args.walks)
    require_current_day_types()
    # the variant first, at the walks' own instant; the candidate then, under the pinned 18:00 (the pin sets module constants and puts them back)
    walk_frame, direct = direct_side(published, scratch, walks)
    with m1321.decision_instant_pinned():
        return _score(args, walk_frame, direct)


def _score(args, walk_frame, direct) -> int:
    frame, candidate, labels, table, splits, _panel, sha, notes = candidate_side(Path(args.published), args.first)
    # the candidate's own regenerated walk, on the whole group, against #1548's record, before anything is paired
    if args.first is None:
        theirs = json.loads(m1572_record().read_text(encoding="utf-8"))
        reproduce_candidate(group_rows(m1548.group_cells(frame, labels, table, candidate, candidate), args.event_reps), theirs["windows"][WINDOW]["group"])
        reproduction = "the candidate's figures on the whole group (pooled and by type, means and intervals) equal #1548's record to 1e-9, so the regenerated walk is the one scored there"
    else:
        reproduction = "not checked: a subset run"
    days = common_days(frame.days, direct, frame.target)
    if not days:
        raise ValueError("no decision day is covered by both the candidate's walk and the variant's walks")
    require_study_window(set(days) | {frame.target(d, h) for d in days for h in HORIZONS})
    require_same_outcomes(days, walk_frame.target, frame.target, walk_frame.outcome, frame.outcome)
    cells = paired_cells(frame, days, labels, table, candidate, direct)
    rows = target_day_rows(frame, days, labels, candidate, direct)
    result = {"issue": 1593, "label": "development, not a verdict", "seed": SEED, "event_reps": args.event_reps, "draws": args.draws, "few_events_below": FEW,
              "panel_sha256": sha, "scratch_panel_sha256": panel_sha256(Path(args.panel)), "regimes": list(REGIMES), "pair": {"candidate": CANDIDATE, "other": DIRECT},
              "subset_from": None if args.first is None else args.first.isoformat(), "notes": notes, "reproduction": reproduction,
              "decision_instants": {"candidate": c.DECISION_TIME.strftime("%H:%M"), "variant": "16:00 (the walks of #1036)"},
              "days": {"candidate_decision_days": len(frame.days), "walked_decision_days": len(direct), "common_decision_days": len(days),
                       "first": days[0].isoformat(), "last": days[-1].isoformat()},
              "cells": {"group": sum(1 for x in cells if x["in_group"]), "target_days": len(rows)}}
    result.update(summarise_pairs(cells, rows, splits, reps=args.event_reps, draws=args.draws))
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    Path(args.output).write_text(json.dumps(result, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    return 0


def m1572_record() -> Path:
    return REPO / "docs" / "research" / "qe-event-model-1548" / "result.json"


# -- the page ----------------------------------------------------------------------------------------------------------------

_f, _siv = m1548._f, m1548._siv


def _signed(x: float, d: int = 3) -> str:
    return f"{x:+.{d}f}"
NAMES = {
    "cover90": "90% coverage: candidate / GBM; d [interval]", "miss_above_q95": "above q95 (5%): candidate / GBM; d [interval]",
    "miss_below_q01": "below q01 (1%): candidate / GBM; d [interval]", "miss_below_q05": "below q05 (5%): candidate / GBM; d [interval]",
    "miss_above_q99": "above q99 (1%): candidate / GBM; d [interval]",
    "grid_crps": "grid CRPS: candidate / GBM; d [interval] (negative favours the GBM)",
    "upper_tail_twcrps": "upper-tail twCRPS: candidate / GBM; d [interval] (negative favours the GBM)",
}


def _rows(table: Mapping[str, Mapping[str, Optional[dict]]], names: Sequence[str]) -> List[str]:
    out = ["| set | regime of the event | events | cells | flag | " + " | ".join(NAMES[n] for n in names) + " |", "|---|---|---|---|---|" + "---|" * len(names)]
    for scope in SCOPES:
        for regime in ("all",) + REGIMES:
            e = table[scope][regime]
            label = "all regimes" if regime == "all" else regime
            if e is None:
                out.append(f"| {SCOPE_TITLES[scope]} | {label} | 0 | 0 | none | " + " | ".join("n/a" for _ in names) + " |")
                continue
            flag = f"**few events ({e['events']})**" if m1572.few_events(e) else ""
            out.append(f"| {SCOPE_TITLES[scope]} | {label} | {e['events']} | {e['cells']} | {flag} | " + " | ".join(m1572._cell(e["measures"], n) for n in names) + " |")
    return out


def _day_rows(level: Mapping[str, Mapping[str, Optional[dict]]]) -> List[str]:
    def one(x: Optional[dict]) -> str:
        if x is None:
            return "n/a"
        if x["lower"] is None:
            return f"{_signed(x['excess'], 4)} (no interval: {x['days']} days)"
        return f"{_signed(x['excess'], 4)} [{x['lower']:+.4f}, {x['upper']:+.4f}]"

    out = ["| set | regime of the event | target days | grid CRPS: d [95% interval] | upper-tail twCRPS: d [95% interval] |", "|---|---|---|---|---|"]
    for scope in SCOPES:
        for regime in ("all",) + REGIMES:
            e = level[scope][regime]
            label = "all regimes" if regime == "all" else regime
            if e is None:
                out.append(f"| {SCOPE_TITLES[scope]} | {label} | 0 | n/a | n/a |")
            else:
                out.append(f"| {SCOPE_TITLES[scope]} | {label} | {e['grid_crps']['days']} | {one(e['grid_crps'])} | {one(e['upper_tail_twcrps'])} |")
    return out


def _pooled_sentence(table: Mapping[str, Mapping[str, Optional[dict]]]) -> List[str]:
    out = []
    for scope in SCOPES:
        e = table[scope]["all"]
        if e is None:
            out.append(f"- {SCOPE_TITLES[scope]}: no cell on the common days.")
            continue
        m = e["measures"]
        out.append(f"- {SCOPE_TITLES[scope]} ({e['events']} events, {e['cells']} cells): the 90% band covers {_f(m['cover90']['candidate'])} for the candidate and {_f(m['cover90']['arm'])} for the GBM "
                   f"(d {_signed(m['cover90']['diff'])} {_siv(m['cover90']['diff_interval'])}); above q95 the candidate is exceeded {_f(m['miss_above_q95']['candidate'])} of the time and the GBM "
                   f"{_f(m['miss_above_q95']['arm'])} (nominal 0.050); grid CRPS {_f(m['grid_crps']['candidate'])} against {_f(m['grid_crps']['arm'])} "
                   f"(d {_signed(m['grid_crps']['diff'])} {_siv(m['grid_crps']['diff_interval'])}); upper-tail twCRPS {_f(m['upper_tail_twcrps']['candidate'])} against "
                   f"{_f(m['upper_tail_twcrps']['arm'])} (d {_signed(m['upper_tail_twcrps']['diff'])} {_siv(m['upper_tail_twcrps']['diff_interval'])}).")
    return out


def render(r: Mapping[str, object]) -> str:
    """The result page, every figure read from the record."""

    t, d = r["table"], r["days"]
    out = [
        "# The frozen candidate against the calendar-aware GBM on quarter-end turns and year-ends (#1593)", "",
        "**Development, not a verdict.** Generated by `scripts/qe_vs_calendar_gbm_1593.py page` from `docs/research/qe-vs-calendar-gbm-1593/result.json`, not edited by hand. "
        "Nothing here is adopted, registered or chosen, and (s3c-ann-net) stays frozen.", "",
        "**Serves:** H5 step 3, on Eleonora's rulings of 12 and 13 November 2026 (#1593): the comparison only, from existing walks, no refit, paired and with intervals, "
        "by turn type (quarter-end turns and year-ends apart, the day types in force since #1161) and by regime, with **no combination arm** and nothing adopted. "
        "Reading it does not resume `gbm_funding` work.", "",
        "**Settled questions** (`docs/research/settled-questions.md`, her rule of 9 November 2026). Q9 (the quarter-end family: #1531, #1548, #1572) holds the repairs of the "
        "candidate's band on these days; no entry compares the candidate with the calendar-aware GBM, so this is a new question beside Q9 and re-runs none of it. S9 (a spread model "
        "reads the calendar at the target day, on direct pairs) is kept: the variant reads the calendar columns at the target day on direct pairs, so it is not provisional under the "
        "calendar rule.", "",
        "## What was compared", "",
        f"`{r['pair']['candidate']}` (the candidate of `docs/research/h5-candidate.json`, regenerated as #1548 and #1572 regenerate it) against `{r['pair']['other']}` (#1036's walks, read from her Mac, "
        f"not refitted), on the {d['common_decision_days']:,} decision days both cover ({d['first']} to {d['last']}; the candidate's development window has {d['candidate_decision_days']:,}, "
        f"the walks {d['walked_decision_days']:,}), {r['cells']['group']:,} cells of h = 1 to 5 aimed at a quarter-end turn or a year-end. {r['reproduction'][0].upper()}{r['reproduction'][1:]}. "
        f"Published panel `{r['panel_sha256']}`, the walks' scratch panel `{r['scratch_panel_sha256']}`. No day after 2025-12-31 and no locked day is read.", "",
        "**Orientation.** d is the GBM minus the candidate on the same cells. For grid CRPS, upper-tail twCRPS and the miss rates a negative d favours the GBM; for coverage a positive d does. "
        f"The interval of d is the 90% event-cluster interval (whole events resampled, {r['event_reps']:,} resamples, seed {r['seed']}, the method of #1548 and #1572; the h = 1 to 5 forecasts aimed at "
        "one turn are one event, so the events column is the number of independent turns behind a cell).", "",
        "**Decision instants.** The candidate's walk is read at the declared 18:00 decision instant (#1312); #1036's walks were made at the 16:00 instant of the published records. The GBM therefore "
        "forecast each day with two hours less of the day's public information than the candidate did. This favours the candidate, by an amount this study does not measure, and a refit of the GBM "
        "at 18:00 is outside the ruling. The decision day, the targets and the outcomes are the same in both (the script refuses a difference).", "",
        "## The figures", "",
        "### Group, quarter-end turns and year-ends, all regimes", ""] + _pooled_sentence(t) + [
        "", "### Coverage and tail misses, by turn type and regime", ""] + _rows(t, ("cover90", "miss_above_q95", "miss_below_q01", "miss_below_q05", "miss_above_q99")) + [
        "", "### Accuracy of the distribution, by turn type and regime", ""] + _rows(t, ("grid_crps", "upper_tail_twcrps")) + [
        "", "### The scoring protocol's interval on the per-target-day means", "",
        "Per target day, the mean over the leads of each model's score; d is the GBM minus the candidate, in bp, with the studentized stationary bootstrap of scoring protocol v1 "
        f"(mean block 10, HAC lag 10, 95%, {r['draws']:,} draws, seed {r['seed']}). A group is a set of target days that need not be consecutive, so the blocks run across its gaps: "
        "here the interval describes, it does not test. A group of no more than ten days carries its difference and no interval.", ""] + _day_rows(r["day_level"]) + [
        "", "## Reading it", "",
        f"Cells resting on few events (under {r['few_events_below']}): {m1572._few_list(t)}.", "",
        f"Regime cells whose grid CRPS interval of d excludes zero: {m1572._excluding_zero(t, 'grid_crps')}. Whose upper-tail twCRPS interval excludes zero: {m1572._excluding_zero(t, 'upper_tail_twcrps')}. "
        f"Whose coverage interval excludes zero: {m1572._excluding_zero(t, 'cover90')}. Whose interval of the miss rate above q95 excludes zero: {m1572._excluding_zero(t, 'miss_above_q95')}. "
        "A cell of a single event resamples to itself, so its interval is a point and it is left out of these lists. With this many cells, several intervals are expected to exclude zero by chance, "
        "and none was chosen in advance.", "",
        "## What this shows and does not show", "",
        "It shows, on the cells both models forecast, how far the calendar-aware GBM's quantiles cover these turns and the year-ends against the candidate's, by turn type and regime, and how many "
        "independent events each figure rests on. It does not show that a combination of the two would do better (none was built), that the GBM would hold up on days after 2025-12-31 or in other regimes, "
        "or that either model's band is right: the quarter-end family (Q9) and the candidate's open failure stand as they did. The GBM's loss to `gbm_funding` outside 2021-23 (#1086, #1591) is a "
        "separate finding on other days. The cells are few and clustered in a handful of turns; the intervals are wide for that reason, and the regimes are not tested against one another. "
        "It is development data (scoring protocol v1): only prospective confirmation days give a verdict. Whether the result opens any further arm is Eleonora's decision.", ""]
    return "\n".join(out)


def log_entry(r: Mapping[str, object], when: str) -> str:
    """The research-log entry (`scripts/check_research_log.py`, `ENTRY_FORMAT`), every figure read from the record."""

    g = r["table"]["group"]["all"]
    d = r["days"]
    if g is None:
        figures = "no cell on the common days"
    else:
        m = g["measures"]
        figures = (f"group ({g['events']} events, {g['cells']} cells): 90% coverage {_f(m['cover90']['candidate'])} candidate, {_f(m['cover90']['arm'])} GBM "
                   f"(d {_signed(m['cover90']['diff'])} {_siv(m['cover90']['diff_interval'])}); exceeded above q95 {_f(m['miss_above_q95']['candidate'])} against {_f(m['miss_above_q95']['arm'])}; "
                   f"grid CRPS d {_signed(m['grid_crps']['diff'])} {_siv(m['grid_crps']['diff_interval'])}; upper-tail twCRPS d {_signed(m['upper_tail_twcrps']['diff'])} "
                   f"{_siv(m['upper_tail_twcrps']['diff_interval'])} (d is the GBM minus the candidate, event-cluster 90% intervals)")
    return "\n".join([
        f"### {when} [H5] step 3 · eleonorabjornberg/repo-market-model#1593",
        "- Directive: #1593 (her rulings of 12 and 13 November 2026: the comparison only, from existing walks, no refit, paired with intervals, by turn type and regime, no combination arm, nothing adopted)",
        "- Step: 3 (the frozen candidate (s3c-ann-net) against `gbm_funding_cal_direct` on quarter-end turns and year-ends; settled-questions: Q9 neighbourhood, no entry compares the two, nothing re-run)",
        "- Tier: development",
        f"- Pins: published panel `{r['panel_sha256'][:8]}...`, scratch panel `{r['scratch_panel_sha256'][:8]}...`; seed {r['seed']}; `scripts/qe_vs_calendar_gbm_1593.py`; the candidate regenerated as #1548 and "
        "checked against its record; #1036's walks read-only from her Mac, not refitted; the candidate at the 18:00 instant and the walks at 16:00; scored days to 2025-12-31, no locked day",
        f"- Tried: the two forecasts on the {d['common_decision_days']:,} common decision days ({d['first']} to {d['last']}), the group's cells by turn type and regime, with event-cluster and "
        "studentized-bootstrap intervals. Variants: 0 (no new model, no combination arm).",
        f"- Result: {figures}. Development data, not a verdict; the cells rest on few events and the regime cells are flagged where under five.",
        "- Against kill: not tested. This compares two models on development data and applies no kill rule; a development figure never settles one (scoring protocol v1).",
        "- Next: what the comparison means for the quarter-end family (Q9) is Eleonora's classification; no arm is built and nothing is adopted.",
        ""])


def page_command(args) -> int:
    record = json.loads(Path(args.score).read_text(encoding="utf-8"))
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    Path(args.output).write_text(render(record), encoding="utf-8")
    return 0


def log_command(args) -> int:
    record = json.loads(Path(args.score).read_text(encoding="utf-8"))
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    Path(args.output).write_text(log_entry(record, args.date), encoding="utf-8")
    return 0


def check_walks_command(args) -> int:
    walks = Path(args.walks)
    if not walks.is_dir():
        raise SystemExit(f"STOP: the walks directory {walks} does not exist; this script never rebuilds the walks.")
    missing = [f"{DIRECT}_h{h}.json" for h in HORIZONS if not (walks / f"{DIRECT}_h{h}.json").is_file()]
    if missing:
        raise SystemExit(f"STOP: {walks} lacks {', '.join(missing)}; walk every lead or none, and this script never rebuilds a walk.")
    print(f"walks: present ({', '.join(f'{DIRECT}_h{h}.json' for h in HORIZONS)}) in {walks}")
    return 0


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="command", required=True)
    w = sub.add_parser("check-walks", help="stop unless every lead's walk of the variant is in the directory")
    w.add_argument("walks")
    w.set_defaults(func=check_walks_command)
    s = sub.add_parser("score", help="regenerate the candidate, read the variant's walks, pair them and write the record")
    s.add_argument("--published", required=True, help="the published panel (digest 4ddc3882...)")
    s.add_argument("--panel", required=True, help="#1036's scratch panel (AUG3.csv)")
    s.add_argument("--walks", required=True)
    s.add_argument("--output", required=True)
    s.add_argument("--event-reps", type=int, default=EVENT_REPS)
    s.add_argument("--draws", type=int, default=DRAWS)
    s.add_argument("--first", type=date.fromisoformat, default=None, help="start the candidate's walk on this day (a subset, for a smoke run only; the declared run omits it)")
    s.set_defaults(func=score)
    g = sub.add_parser("page", help="write the result page from a record")
    g.add_argument("--score", required=True)
    g.add_argument("--output", required=True)
    g.set_defaults(func=page_command)
    g = sub.add_parser("log", help="write the research-log entry from a record")
    g.add_argument("--score", required=True)
    g.add_argument("--output", required=True)
    g.add_argument("--date", required=True)
    g.set_defaults(func=log_command)
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
