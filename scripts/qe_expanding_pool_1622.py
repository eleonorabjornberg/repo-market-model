"""(s3c-ann-net) with the quarter-end event pool drawn from every past turn up to the anchor, beside the frozen candidate, at the 18:00 decision instant
(#1622; H5 step 3, avenue #1561; her ruling of 16 November 2026, option (a) of card qe-family-1561-1116).

A development study, never a verdict. It writes JSON and Markdown to the paths it is given and nothing into `docs/runs/`. Every choice is in
`metadata/qe_expanding_pool_1622.json`, which this script refuses to read unless it is committed and unchanged. The candidate (s3c-ann-net) stays frozen.

#1548's arm replaced, on a quarter-end or year-end target day, the candidate's pool quantiles by `(1 - w) pool_j + w event_j`, `event_j` the quantiles of the
residuals of the refit's own training pairs whose target is in the event set, `w = n / (n + k)`. The refit trains on a trailing two-year window, which holds at
most eight turns, so `n` stayed under 16 and `w` under 0.44. Here the event residuals come from every direct pair of the lead whose target is at or before
the anchor: the pairs older than the window are standardised under the refit in force (`repo_model.event_conditional.older_residuals`: the refit's own
effects, state slopes and phi, and the scale at each pair's origin) and appended to the refit's own residuals. The candidate's pool, centre, shift, scale and
fit are untouched. Two arms, both with k = 20 and the minimum of 10 pairs:

* (i) expanding pool: one pool of quarter-end turns and year-ends together;
* (ii) separate pools: a year-end target day reads a pool of year-end turns alone, a quarter_end_turn target day a pool of the other quarter-end turns alone.

Both share #1548's walk (the walk is made once per window), frame, kill and event-cluster bootstrap. On every cell outside the event set each arm's quantiles
equal the candidate's, bit for bit, and the walk fails otherwise (`qe_event_model_1548.outside_group_identical`).

Commands, from a clone of the branch:

    PYTHONPATH=src python3 -m repo_model.cli build --raw-root tests/fixtures/snapshots/funding_inputs \\
        --output PUB.csv --build-cutoff 2026-09-08T21:31:42+00:00 --decision-time 18:00:00
    PYTHONPATH=src python3 -m repo_model.cli verify-panel PUB.csv --manifest metadata/funding_panel_manifest.json
    PYTHONPATH=src python3 scripts/qe_expanding_pool_1622.py score --panel PUB.csv \\
        --output docs/research/qe-expanding-pool-1622/result.json
    PYTHONPATH=src python3 scripts/qe_expanding_pool_1622.py page \\
        --score docs/research/qe-expanding-pool-1622/result.json --output docs/research/qe-expanding-pool-1622-result.md

Stdlib only.
"""

from __future__ import annotations

import argparse
import contextlib
import importlib.util
import json
import sys
from datetime import date
from pathlib import Path
from typing import Dict, List, Mapping, Optional, Sequence, Tuple

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))


def _load(name: str):
    path = REPO / "scripts" / f"{name}.py"
    held = sys.modules.get(name)
    if held is not None and getattr(held, "__file__", None) == str(path):
        return held
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module  # the worker pool of the walk pickles by module name
    spec.loader.exec_module(module)
    return module


# Lockbox classification (#1058): tests/test_lockbox.py reads these literals from this file's syntax tree.
LOCKBOX_CRPS = {
    "arm_cells": (
        "delegates",
        "the cells of both arms on the frame's days are scored by `qe_event_model_1548.run_window`; `_score` calls `require_exploratory_window` on every "
        "panel day before any frame is built (#1622)",
    ),
}

m1548 = _load("qe_event_model_1548")
m1572 = _load("qe_event_regime_1572")
from repo_model import announced_iorb, policy_events, s3c_announced, s3c_net  # noqa: E402
from repo_model import event_conditional as ec  # noqa: E402
from repo_model import protocol_benchmarks as pb  # noqa: E402
from repo_model import spread_mean_reversion as smr  # noqa: E402
from repo_model import spread_mr_calendar as cal  # noqa: E402
from repo_model import spread_mr_fhs as fhs  # noqa: E402
from repo_model import spread_mr_state_calendar as sc  # noqa: E402
from repo_model.baseline import panel_sha256  # noqa: E402
from repo_model.evaluation_splits import load_split_declaration  # noqa: E402
from repo_model.exploration import require_exploratory_window  # noqa: E402

c, m1321, m1288, m1273, m1402 = m1548.c, m1548.m1321, m1548.m1288, m1548.m1273, m1548.m1402
DECLARATION = REPO / "metadata" / "qe_expanding_pool_1622.json"
SEED = m1548.SEED
K = 20
EVENT_REPS = m1548.EVENT_REPS
LAST_DAY = m1548.LAST_DAY
WINDOWS = m1548.WINDOWS
ANNNET = m1548.ANNNET
ARM_EXPANDING = "sc_s3c_ann_net_qeexpand"
ARM_SEPARATE = "sc_s3c_ann_net_qesplit"
ARMS = (ARM_EXPANDING, ARM_SEPARATE)
ARM_LABELS = {ARM_EXPANDING: "(s3c-ann-net-x), arm (i), expanding pool", ARM_SEPARATE: "(s3c-ann-net-xs), arm (ii), separate pools"}
QE, YE = "quarter_end_turn", "year_end"
LEADS = m1548.LEADS
GROUP_TYPES = m1548.GROUP_TYPES


def committed_declaration(path: Path = DECLARATION) -> dict:
    """The declaration, refused unless it is committed and unchanged since `HEAD`."""

    return m1548.committed_declaration(path)


def event_sets(arm: str) -> Dict[str, Tuple[str, ...]]:
    """The pressure-day types whose residuals form the event pool a target day of each type reads, per arm.

    Raises:
        ValueError: `arm` is not one of the two.
    """

    if arm == ARM_EXPANDING:
        return {QE: (QE, YE), YE: (QE, YE)}
    if arm == ARM_SEPARATE:
        return {QE: (QE,), YE: (YE,)}
    raise ValueError(f"unknown arm {arm!r}")


# -- the older pairs -----------------------------------------------------------------------------------------------------


class Older:
    """Builds the direct training pairs older than a refit's window, read as `spread_mr_state_calendar.refit` reads its own: the flags and the net
    settlement sizes at the pair's target row, the state of the pair's decision, the scale at its origin, and the raw residual under the refit's phi."""

    def __init__(self, panel, splits, table, net_table):
        self.panel = panel
        self.dates = [row.date for row in panel]
        self.levels = smr.ordinary_levels(panel, splits)
        self.states = s3c_net.constant_states(panel)
        self.table, self.net_table = table, net_table
        self._rows: Dict[Tuple[int, int], tuple] = {}

    def _row(self, h: int, target: int):
        held = self._rows.get((h, target))
        if held is None:
            held = self._rows[(h, target)] = (self.table.flags_at(h, target), self.net_table.sizes_at(h, target))
        return held

    def pairs(self, index: int, anchor: int, phi: float, h: int) -> List[sc.StatePair]:
        """The pairs of lead `h` of the refit on row `index` whose target lies before its training window and at or before `anchor`."""

        lag = index - anchor
        k = h + lag
        first = pb._window_start(self.panel, index, smr.TRAIN_YEARS)
        spreads = [row.spread_bps for row in self.panel[: anchor + 1]]
        reader = fhs.ScaleReader(spreads, sc.BASE_VARIANT)
        out: List[sc.StatePair] = []
        for target in range(k, min(first, anchor + 1)):
            origin = target - k
            if self.levels[origin] is None:
                continue
            scale = reader.at(origin)
            if scale is None:
                continue
            raw = (spreads[target] - self.levels[origin]) - phi**k * (spreads[origin] - self.levels[origin])
            state = sc.level(sc.pair_state(self.states, self.dates, origin, lag, index))
            flags, sizes = self._row(h, target)
            out.append(sc.StatePair(raw, scale, flags, state, sizes, origin, target, {}, False))
        return out


# -- the arms ------------------------------------------------------------------------------------------------------------

_CONTEXT: Dict[str, object] = {}


def arm_forecasts_of(arm: str):
    """The `arm_forecasts` of `qe_event_model_1548` for `arm`: same signature, same return (forecasts by day, and the pool record)."""

    sets = event_sets(arm)

    def arm_forecasts(walk, panel, labels, registry, decision_time, days: Sequence[date], k: float) -> Tuple[Dict[date, dict], dict]:
        older: Older = _CONTEXT["older"]
        position = {row.date: i for i, row in enumerate(panel)}
        estimates = {r: per_arm[m1548.ARM_NET] for r, per_arm in walk.estimates.items()}
        fitted: Dict[str, Dict[date, Dict[int, dict]]] = {t: {} for t in sets}
        for refit, per_lead in estimates.items():
            index = position[refit]
            anchor = pb._anchor(panel, index, registry, decision_time)
            phi = walk.fits[refit].phi
            for t in sets:
                fitted[t][refit] = {}
            for h, est in per_lead.items():
                wide = ec.expand_estimate(est, older.pairs(index, anchor, phi, h), anchor)
                for t, event in sets.items():
                    fitted[t][refit][h] = ec.event_pool(wide, labels, anchor, k=k, event=event)
        out: Dict[date, dict] = {}
        for d in days:
            refit = m1402.refit_for(estimates, d)
            index = position[d]
            scale = walk.detail[d]["scale"]
            day = {}
            for h in LEADS:
                q = walk.forecasts[m1548.ARM_NET][d][h]
                label = labels[index + h]
                if label in GROUP_TYPES:
                    q = ec.conditioned_quantiles(q, estimates[refit][h].pool, fitted[label][refit][h]["pool"], scale)
                day[h] = q
            out[d] = day
        shown = {"all": QE} if arm == ARM_EXPANDING else {QE: QE, YE: YE}
        return out, {name: ec.pool_record(fitted[t], LEADS, k=k) for name, t in shown.items()}

    return arm_forecasts


@contextlib.contextmanager
def arm_running(arm: str, cells: List[dict]):
    """Point `qe_event_model_1548` at `arm`: its arm name and model list, its `arm_forecasts`, and a tap on the group's cells (for the regime table)."""

    saved = {n: getattr(m1548, n) for n in ("ARM", "MODELS", "arm_forecasts", "group_cells")}
    labels = dict(m1548.LABELS)

    def tapped(*args, **kwargs):
        found = saved["group_cells"](*args, **kwargs)
        cells[:] = found
        return found

    m1548.ARM, m1548.MODELS = arm, m1548.REFERENCES + (ANNNET, arm)
    m1548.arm_forecasts, m1548.group_cells = arm_forecasts_of(arm), tapped
    m1548.LABELS[arm] = ARM_LABELS[arm]
    try:
        yield
    finally:
        for n, v in saved.items():
            setattr(m1548, n, v)
        m1548.LABELS.clear()
        m1548.LABELS.update(labels)


@contextlib.contextmanager
def walks_shared():
    """Make each window's walk once: `qe_event_model_1548.build` calls `day_type_scale_1402.walks_of`, which both arms share."""

    held = m1402.walks_of
    seen: Dict[tuple, object] = {}

    def once(window, frame, panel, splits, registry, results, auctions, first):
        key = (window, first)
        if key not in seen:
            seen[key] = held(window, frame, panel, splits, registry, results, auctions, first)
        return seen[key]

    m1402.walks_of = once
    try:
        yield
    finally:
        m1402.walks_of = held


# -- the run -------------------------------------------------------------------------------------------------------------


def score(args) -> int:
    with m1321.decision_instant_pinned():
        return _score(args)


def _score(args) -> int:
    declaration = committed_declaration()
    k = declaration["form"]["k"]
    if k != K:
        raise SystemExit(f"the declaration's k is {k!r}, the script's is {K!r}")
    if [a["name"] for a in declaration["arms"]] != [ANNNET, *ARMS]:
        raise SystemExit("the declaration's arms are not the script's")
    panel_path = Path(args.panel)
    sha = panel_sha256(panel_path)
    panel = [row for row in m1548.load_daily_panel(panel_path) if row.date <= LAST_DAY]
    require_exploratory_window([row.date for row in panel], where="scripts/qe_expanding_pool_1622")
    splits = load_split_declaration(c.SPLITS)
    registry = json.loads(c.SOURCES.read_text(encoding="utf-8"))
    register = policy_events.load_register()
    table = cal.TermTable(panel, announced_iorb.load_announcements(c.IORB_TABLE), decision_time=c.DECISION_TIME)
    auctions = m1273.load_auctions()
    results = m1288.load_results()
    iorb = announced_iorb.load_announcements(c.IORB_TABLE)
    both = s3c_announced.AnnouncedTermTable(panel, iorb, results, decision_time=m1548.k_mod.DECISION_TIME)
    net_table = s3c_announced.AnnouncedNetSizeTable(panel, auctions, decision_time=m1548.k_mod.DECISION_TIME)
    _CONTEXT["older"] = Older(panel, splits, both, net_table)
    result: dict = {
        "issue": 1622, "declaration": str(DECLARATION.relative_to(REPO)), "panel_sha256": sha, "decision_time": c.DECISION_TIME.strftime("%H:%M"),
        "subset_from": None if args.first is None else args.first.isoformat(), "label": "development, not a verdict", "seed": SEED, "draws": args.draws,
        "reps": args.reps, "event_reps": args.event_reps, "k": k, "arms": list(ARMS), "models": [ANNNET, *ARMS],
        "reading_rules": declaration["reading_rules"], "kill_rule": declaration["kill"], "windows": {},
        "regimes": list(m1572.REGIMES), "few_events_below": m1572.FEW,
    }
    with walks_shared():
        for window in WINDOWS:
            per_arm: dict = {}
            for arm in ARMS:
                cells: List[dict] = []
                with arm_running(arm, cells):
                    one = m1548.run_window(window, panel, splits, registry, table, register, results, auctions, args, k)
                one["regime_table"] = m1572.regime_table(cells, splits, reps=args.event_reps)
                per_arm[arm] = one
            result["windows"][window] = per_arm
    if args.first is None:
        first_arm = ARMS[0]
        result["reproduction"] = m1402.reproduction({w: result["windows"][w][first_arm] for w in WINDOWS})
    else:
        result["reproduction"] = {}
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    Path(args.output).write_text(json.dumps(result, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    return 0


# -- the page ------------------------------------------------------------------------------------------------------------

_f, _iv, _signed, _siv = m1548._f, m1548._iv, m1548._signed, m1548._siv


def _demote(lines: Sequence[str], by: int = 1) -> List[str]:
    return [("#" * by + line if line.startswith("#") else line) for line in lines]


def pool_lines(arm: str, pools: Mapping[str, object]) -> List[str]:
    """The weight w reached per lead, and the number of event pairs behind it."""

    out: List[str] = []
    titles = {"all": "one pool of quarter-end turns and year-ends", QE: "pool of quarter-end turns", YE: "pool of year-ends"}
    for name, record in pools.items():
        out += [f"Event pool: {titles[name]}.", ""] + m1548.pool_table(record) + [""]
    return out


def arm_section(window: str, arm: str, w: Mapping[str, object]) -> List[str]:
    g, n = w["group"], w["notes"]
    out = [f"#### {ARM_LABELS[arm]}", ""]
    out += [f"Group cells {w['outside_the_group']['group_cells']:,}, of which the arm changes {w['outside_the_group']['group_cells_changed']:,}; cells outside the "
            f"group {w['outside_the_group']['other_cells']:,}, every one identical to the candidate (the walk fails otherwise). The group holds "
            f"{g['pooled']['events']} turn events. **That is few, so every interval is wide.**", ""]
    out += ["**By regime of the event (read first).** Cells of fewer than "
            f"{m1572.FEW} events are flagged.", ""]
    out += m1572._rows(w["regime_table"], ("cover90", "miss_above_q95", "miss_below_q01", "grid_crps", "upper_tail_twcrps")) + [""]
    out += ["**Coverage and tail misses on the group, candidate against arm.**", ""] + m1548.rates_table(m1548.group_rows(g)) + [""]
    out += [f"**{m1548.short_of_nominal(g)}**", ""]
    out += ["**Accuracy on the group (paired, same cells).** Negative favors the arm.", ""] + m1548.scores_table(m1548.group_rows(g)) + [""]
    out += ["**The weight w the event pool reached, per lead, over the window's refits.**", ""] + pool_lines(arm, w["pools"])
    out += ["**The declared kill (that of #1548, applied to this arm on its own).** "
            + m1548.kill_sentence(g["kill"], events=g["pooled"]["events"], read=window == "development"), ""]
    return out


def against_lines(arm: str, w: Mapping[str, object]) -> List[str]:
    pooled = w["groups"]["pooled"]["all decision days"]
    out = [f"#### {ARM_LABELS[arm]}: pooled, against B1, B1' and B2", "", "Studentized stationary bootstrap. " + m1548.CELL_GUIDE, ""]
    out += m1548.against_table(pooled) + [""]
    for split, title in (("regime", "By regime of the decision day"), ("pressure_day_type", "By pressure-day type of the target day")):
        for ref in m1548.REFERENCES:
            t = m1548.split_table(w, split, arm, ref)
            if t:
                out += [f"##### {title}: {ARM_LABELS[arm]} against {m1548.LABELS[ref]}", ""] + t + [""]
    t = m1548.split_table(w, "pressure_day_type", arm, ANNNET)
    if t:
        out += [f"##### By pressure-day type: {ARM_LABELS[arm]} against the candidate (identical outside the group)", "",
                "The arm scored against the candidate, so a positive d favors the arm.", ""] + t + [""]
    return out


def answer(r: Mapping[str, object]) -> List[str]:
    """The answer on the development window, per arm, from the score file: coverage, the gap to 90%, grid CRPS, the weight reached and the declared kill."""

    out: List[str] = []
    w = r["windows"]["development"]
    for arm in r["arms"]:
        g = w[arm]["group"]
        pools = w[arm]["pools"]
        weights = {name: p["by_lead"]["1"]["w"] for name, p in pools.items()}
        reached = "; ".join(f"{'the pool' if name == 'all' else name.replace('_', ' ') + ' pool'}: mean {x['mean']:.3f}, greatest {x['max']:.3f}" for name, x in weights.items())
        kill = g["kill"]
        out.append(
            f"**{ARM_LABELS[arm]}.** {m1548.short_of_nominal(g)} Coverage gain, arm minus candidate: {_signed(kill['coverage_gain'])} "
            f"{_siv(kill['coverage_gain_interval'])}. Grid CRPS on the group, arm minus candidate: {_signed(kill['group_crps_diff'], 3)} "
            f"{_siv(kill['group_crps_diff_interval'])} bp. Weight w reached (lead 1; every lead reads the same turns): {reached}. "
            f"**Against the declared kill: {'killed' if kill['killed'] else 'not killed'}.**")
        out.append("")
    out.append("The regime table under each arm below is the one to read first: older turns come from other regimes, and a gain that sits in one regime or in a few "
               "events is not one to lean on.")
    return out


def render(r: dict) -> str:
    """The page. Every figure is read from `r` (the score file)."""

    out = [
        "# The quarter-end correction from an expanding pool of past turns", "",
        f"Terms such as arm, cell, kill rule, grid CRPS and B1 are defined in the [glossary]({m1548.GLOSSARY}). Issue numbers and files are in the Record at the end.", "",
        "## The question", "",
        "**Does drawing the quarter-end correction from every past quarter-end turn, instead of only the turns inside the candidate's two-year fit window, repair "
        "the candidate's quarter-end bands?** The earlier quarter-end arms drew on at most eight turns, so the weight they gave the quarter-end evidence stayed "
        "under half. This study gives the same correction the whole public history up to the decision. It is H5, step 3, a development study.", "",
        "Register: settled-questions entry Q9 (the quarter-end family) is the one touched; S5 (a longer history for the whole fit, which lost) is a different "
        "question, because here the fit, the centre and the candidate's own pool keep their two-year window and only the quarter-end residuals reach back.", "",
        "## The answer", ""] + answer(r) + ["",
        "## Method", "",
        "On quarter-end and year-end target days the candidate's band is blended with one built from past quarter-end errors, as in #1548; the weight is "
        f"n / (n + {r['k']}), n the number of past pairs at that lead. What changes is n: every past pair up to the decision counts, and an older pair's error is "
        "measured with the coefficients and scale of the refit in force at the decision. Arm (i) pools the quarter-end turns and the year-ends. Arm (ii) keeps the "
        "year-ends in a pool of their own, apart from the other quarter-ends. Every other forecast is the candidate's, unchanged. Each arm is killed on the rule of "
        "#1548: its 90% band does not cover more of the group's outcomes than the candidate's beyond its interval, or its forecasts on those days score worse.", "",
        f"Intervals on the group are 90% percentile intervals of a cluster bootstrap over turn events ({r['event_reps']:,} resamples, seed {r['seed']}); against the "
        f"benchmarks they are the studentized stationary bootstrap ({r['draws']:,} draws, seed {r['seed']}). The development window is read; the 2026 development "
        "days are shown apart and decide nothing. Nothing here is a verdict, a choice or an adoption, and (s3c-ann-net) stays frozen.", ""]
    for window, title in (("development", "Result on the development window (targets up to 2025-12-31)"),
                          ("2026", "The 2026 development days (targets 2026-01-02 to 2026-09-03; they decide nothing)")):
        if window not in r["windows"]:
            continue
        out += [f"## {title}", ""]
        for arm in r["arms"]:
            out += arm_section(window, arm, r["windows"][window][arm])
    out += ["## Against the benchmarks", ""]
    for window in ("development", "2026"):
        if window not in r["windows"]:
            continue
        out += [f"### {'Development window' if window == 'development' else 'The 2026 development days'}", ""]
        for arm in r["arms"]:
            out += _demote(against_lines(arm, r["windows"][window][arm]), 0)
    out += ["## What it means, and its limits", "",
            "The page shows what a longer quarter-end history does to the candidate's coverage, tail misses and CRPS on days that were already seen. It is development "
            "data: no verdict, no adoption, and no registration follows from it. Older turns come from other regimes, so the table by regime of the event is the "
            "one to read first; a gain that sits in one regime, or in a few events, is not a gain that will recur. The year-ends are too few to decide alone. The two "
            "arms are not tested against each other, and the figures of #1531 and #1548 are not re-run here. What to do with the quarter-end family next is "
            "hers.", "",
            "## Record", "",
            f"Declaration: `{r['declaration']}` (committed before any score). Panel digest: `{r['panel_sha256']}`. Decision instant {r['decision_time']} New York. "
            "Candidate reproduced to 1e-9: "
            + ", ".join(f"{w} ({v['here']:.6f} here, {v['record']:.6f} in the 1314 record)" for w, v in r["reproduction"].items()) + ".", ""]
    return "\n".join(out).rstrip() + "\n"


def page(args) -> int:
    r = json.loads(Path(args.score).read_text(encoding="utf-8"))
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    Path(args.output).write_text(render(r), encoding="utf-8")
    return 0


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="command", required=True)
    s = sub.add_parser("score", help="walk the candidate, make both arms and score on both windows")
    s.add_argument("--panel", required=True)
    s.add_argument("--output", required=True)
    s.add_argument("--draws", type=int, default=m1548.sp.DRAWS)
    s.add_argument("--reps", type=int, default=m1402.REPS, help="bootstrap resamples of the unstudentized intervals")
    s.add_argument("--event-reps", type=int, default=EVENT_REPS, help="event-cluster resamples on the group")
    s.add_argument("--workers", type=int, default=4)
    s.add_argument("--first", type=date.fromisoformat, default=None, help="start the walk on this day (a subset, for the script's test only)")
    s.set_defaults(func=score)
    g = sub.add_parser("page", help="write the result page from a score file")
    g.add_argument("--score", required=True)
    g.add_argument("--output", required=True)
    g.set_defaults(func=page)
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
