"""(s3c-ann-net-cmb): a separate cash management bill term on the candidate (s3c-ann-net), aimed at its 2020 loss, made at the 18:00 decision instant
(#1356; H5 step 3; avenue #1306; her ruling of 2 November 2026).

A development study, never a verdict. It writes JSON and Markdown to the paths it is given and nothing into `docs/runs/`. Every choice is in
`metadata/s3c_ann_net_cmb_1356.json`, which this script refuses to read unless it is committed and unchanged. The arm is `repo_model.s3c_announced`:
(s3c-ann-net) with the cash management bill (CMB) leg split out of the bill leg and given its own term, read from the announcement at every lead on
direct pairs, in two declared forms: `cmb_flag` (an announced CMB settles on the target day) and `cmb_size` (the announced CMB offering in USD 100 bn).
Each is capped as (s3c) is capped (`repo_model.s3c_candidate`, unchanged). The references (s3c-ann-net) and (s3c), and the benchmarks B1, B1' and B2, are
scored in the same run, at 18:00 (`repo_model.decision_instant`). The frames and machinery are #1255's, #1273's, #1288's and #1321's and are loaded as
they are: the development window of #1145 and #1241 (targets up to 2025-12-31) and the 2026 development days of #1229 (targets 2026-01-02 to
2026-09-03, the near-blind tier open since GO #151). The blind tier and every lockbox day are refused by the frames' own guards.

It measures grid CRPS averaged over h = 1..5 (primary), upper-tail twCRPS (key secondary) and the Brier score of P(> +5 bp)
(`docs/decisions/pressure-probability.md`), on scoring protocol v1's studentized stationary bootstrap read on the bound on mean d (her #1009 ruling)
with the skill interval beside, split by lead, regime (2020, and March to June inside it, on their own), pressure-day type, and the settlement-day type
of the target at each lead, with the CMB settlement days against the other bill days and the immediate-release CMB days on their own; reports the
coverage of the central 90% band and the fitted effect of each settlement term.

Commands, from a clone of the branch (the walks are minutes, the paired tests the longer part; a cloud run unless the measured time says otherwise):

    PYTHONPATH=src python3 -m repo_model.cli build --raw-root tests/fixtures/snapshots/funding_inputs \\
        --output PUB.csv --build-cutoff 2026-09-08T21:31:42+00:00 --decision-time 18:00:00
    PYTHONPATH=src python3 -m repo_model.cli verify-panel PUB.csv --manifest metadata/funding_panel_manifest.json
    PYTHONPATH=src python3 scripts/s3c_ann_net_cmb_1356.py score --panel PUB.csv --output docs/research/s3c-ann-net-cmb-1356/result.json
    PYTHONPATH=src python3 scripts/s3c_ann_net_cmb_1356.py page \\
        --score docs/research/s3c-ann-net-cmb-1356/result.json --output docs/research/s3c-ann-net-cmb-1356-result.md

Stdlib only.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import multiprocessing
import sys
from datetime import date
from pathlib import Path
from typing import Dict, List, Mapping, Optional, Sequence, Tuple

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))


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


from repo_model import announced_iorb, metrics, policy_events, s3c_announced, s3c_candidate, s3c_net  # noqa: E402
from repo_model import scoring_protocol as sp, spread_mr_state_calendar as sc  # noqa: E402
from repo_model.baseline import panel_sha256  # noqa: E402
from repo_model.evaluation_splits import load_split_declaration  # noqa: E402
from repo_model.exploration import EXPLORATORY_END, require_exploratory_window  # noqa: E402
from repo_model import spread_mr_calendar as cal  # noqa: E402

#: #1321's script (and through it #1288's, #1273's, #1255's, #1241's and #1229's), loaded under an alias of its own so that the pickling of the worker
#: pool's tasks does not meet another test module's copy. Its `decision_instant_pinned` runs the chain at the declared 18:00 instant.
m1321 = _load("s3c_flagnet_gross_1321", "s3c_flagnet_gross_1321_in_1356")
m1288, m1273, m1255, k, c, s686, s761 = m1321.m1288, m1321.m1273, m1321.m1255, m1321.k, m1321.c, m1321.s686, m1321.s761
load_daily_panel = m1288.load_daily_panel
decision_instant_pinned = m1321.decision_instant_pinned

DECLARATION = REPO / "metadata" / "s3c_ann_net_cmb_1356.json"
RELEASE_TIMES = REPO / "metadata" / "announcement_release_times_1301.json"
RECORD_1321 = REPO / "docs" / "research" / "s3c-flagnet-gross-1321" / "result.json"
SEED = 1356
LAST_DAY = EXPLORATORY_END
WINDOW_LAST = m1288.WINDOW_LAST
WINDOWS = m1288.WINDOWS
WINDOW_TITLES = m1288.WINDOW_TITLES
S3C, ANNNET, B1P = m1288.S3C, m1288.ANNNET, m1288.B1P
BENCHMARKS = m1288.BENCHMARKS
CMBF, CMBS = "sc_s3c_ann_net_cmbf", "sc_s3c_ann_net_cmbs"
ARMS = (CMBF, CMBS)
MODELS = BENCHMARKS + (S3C, ANNNET, CMBF, CMBS)
LABELS = {"B1": "B1", B1P: "B1' (#960)", "B2": "B2", S3C: "(s3c), the H5 candidate", ANNNET: "(s3c-ann-net), the candidate of #1318",
          CMBF: "(s3c-ann-net-cmb), flag form", CMBS: "(s3c-ann-net-cmb), size form"}
SHORT = {"B1": "B1", B1P: "B1'", "B2": "B2", S3C: "(s3c)", ANNNET: "(s3c-ann-net)", CMBF: "(cmb, flag)", CMBS: "(cmb, size)"}
TESTED = m1288.TESTED
METRIC_NAMES = m1288.METRIC_NAMES
METRIC_TITLES = m1288.METRIC_TITLES
MIN_GROUP_DAYS = m1288.MIN_GROUP_DAYS
BLOCK = float(sp.BLOCK_LENGTH)
EPSILON = 1e-9
LEADS = tuple(sp.HORIZONS)
#: The splits tested against the benchmarks too; the settlement-day-type and immediate-release groups are tested against (s3c-ann-net) and (s3c) only.
FULL_SPLITS = ("pooled", "lead", "regime", "pressure_day_type")
DAY_TYPE = m1288.DAY_TYPE
TYPE_LABELS = m1288.TYPE_LABELS
CMB_DAYS, OTHER_BILL_DAYS = TYPE_LABELS[2], TYPE_LABELS[3]
IMMEDIATE = "immediate_release"
Y2020, Y2020_SPRING, Y2020_REST, Y2020_NO_IMMEDIATE = "2020", "2020: March to June", "2020: other months", "2020: without immediate-release CMB days"
#: The terms of each arm's fitted effect, in the order of the effect tables, and their units.
EFFECT_TERMS: Mapping[str, Tuple[str, ...]] = {
    ANNNET: ("settlement_coupon", "settlement_bill"),
    CMBF: ("settlement_coupon", "settlement_bill", sc.CMB_FLAG),
    CMBS: ("settlement_coupon", "settlement_bill", sc.CMB_SIZE),
}
TERM_TITLES = {"settlement_coupon": "net coupon", "settlement_bill": "net bill", sc.CMB_FLAG: "CMB flag", sc.CMB_SIZE: "CMB offering"}
TERM_UNITS = {"settlement_coupon": "bp per USD 100 bn", "settlement_bill": "bp per USD 100 bn", sc.CMB_FLAG: "bp per flagged day",
              sc.CMB_SIZE: "bp per USD 100 bn"}
REGIME_LEAD = "3"
REPS = 2000
_STATE: Dict = {}


def committed_declaration(path: Path = DECLARATION) -> dict:
    """The declaration, refused unless it is committed and unchanged since `HEAD`."""

    return s686.committed_declaration(path)


def plan(candidate: str, split: str = "pooled") -> List[str]:
    """What a candidate is tested against: a form against (s3c-ann-net) and (s3c), and on the full splits the benchmarks; (s3c-ann-net) against
    (s3c) alone, the baseline of the 2020 question."""

    if candidate == ANNNET:
        return [S3C]
    if candidate in ARMS:
        return [ANNNET, S3C] + (list(BENCHMARKS) if split in FULL_SPLITS else [])
    return []


# -- the walks and the frame ---------------------------------------------------------------------------------------------


def release_days(snapshot_dir: Path = m1288.AUCTIONS, path: Path = RELEASE_TIMES) -> List[str]:
    """The settlement days of a cash management bill whose announcement states no release time ('For Immediate Release', #1301)."""

    stated = json.loads(Path(path).read_text(encoding="utf-8"))["stated"]
    files = sorted(p for p in Path(snapshot_dir).glob("*.json") if not p.name.endswith(".manifest.json"))
    records = json.loads(files[0].read_text(encoding="utf-8"))["data"]
    return sorted({r["issue_date"] for r in records
                   if r["cash_management_bill_cmb"] == "Yes" and stated.get(r["pdf_filenm_announcemt"]) == "immediate"})


def walks_of(window: str, frame, panel, splits, registry, results, auctions, first: Optional[date]):
    """The walks of (s3c-ann-net) and of the two forms over #1255's decision days, with the tables they read.

    Raises:
        ValueError: a scored decision day has no forecast of a walk.
    """

    days = m1288.candidate_days(frame, window, first)
    settings = dict(registry=registry, decision_time=k.DECISION_TIME, splits=splits)
    states = s3c_net.constant_states(panel)
    iorb = announced_iorb.load_announcements(c.IORB_TABLE)
    term_table = s3c_announced.AnnouncedTermTable(panel, iorb, results, decision_time=k.DECISION_TIME)
    net_table = s3c_announced.AnnouncedNetSizeTable(panel, auctions, decision_time=k.DECISION_TIME)
    ex_table = s3c_announced.AnnouncedNetExCmbSizeTable(panel, auctions, decision_time=k.DECISION_TIME)
    cmb = {sc.CMB_FLAG: s3c_announced.AnnouncedCmbTerms(panel, auctions, (sc.CMB_FLAG,), decision_time=k.DECISION_TIME),
           sc.CMB_SIZE: s3c_announced.AnnouncedCmbTerms(panel, auctions, (sc.CMB_SIZE,), decision_time=k.DECISION_TIME)}
    walks = {
        "ref": sc.walk(panel, days, term_table, states, (s3c_announced.ANN_NET_ARM,), sizes=net_table, **settings),
        "flag": sc.walk(panel, days, term_table, states, (s3c_announced.CMB_FLAG_ARM,), sizes=ex_table, iorb=cmb[sc.CMB_FLAG], **settings),
        "size": sc.walk(panel, days, term_table, states, (s3c_announced.CMB_SIZE_ARM,), sizes=ex_table, iorb=cmb[sc.CMB_SIZE], **settings),
    }
    names = {"ref": s3c_announced.ANN_NET_ARM.name, "flag": s3c_announced.CMB_FLAG_ARM.name, "size": s3c_announced.CMB_SIZE_ARM.name}
    for key, walk in walks.items():
        for d in frame.days:
            if d not in walk.forecasts[names[key]]:
                raise ValueError(f"the {key} walk has no forecast of {names[key]} on the scored decision day {d}")
    return walks, names, (term_table, net_table, ex_table, cmb)


def build(window: str, panel, splits, registry, table, register, results, auctions, first: Optional[date]):
    """#1255's frame of `window` with (s3c-ann-net) and the two forms added: `(frame, notes, walks, names, tables, groups_fn)`."""

    frame, notes, _mine, _cells, groups_fn = m1255.build(window, panel, splits, registry, table, register, first)
    walks, names, tables = walks_of(window, frame, panel, splits, registry, results, auctions, first)
    raw = {ANNNET: ("ref", names["ref"]), CMBF: ("flag", names["flag"]), CMBS: ("size", names["size"])}
    forecasts = {name: frame.forecasts[name] for name in BENCHMARKS + (S3C,)}
    for model, (key, arm) in raw.items():
        forecasts[model] = m1255.s3c_forecasts(frame, register, {d: walks[key].forecasts[arm][d] for d in frame.days})
    frame.forecasts = {name: {d: forecasts[name][d] for d in frame.days} for name in MODELS}
    notes = dict(notes, refits_ref=len(walks["ref"].fits), refits_flag=len(walks["flag"].fits), refits_size=len(walks["size"].fits))
    return frame, notes, walks, names, tables, groups_fn


# -- the fitted effect ---------------------------------------------------------------------------------------------------


def effect_values(model: str, lead: int, index: int, tables) -> Dict[str, float]:
    """The value of each of the model's terms on the target of the decision on row `index`, in units of USD 100 bn, or 0/1 for the flag."""

    _term, net_table, ex_table, cmb = tables
    if model == ANNNET:
        sizes = net_table.read(lead, index)
        return {t: sizes[t] / sc.SIZE_UNIT for t in EFFECT_TERMS[model]}
    sizes = ex_table.read(lead, index)
    extra = cmb[sc.CMB_FLAG if model == CMBF else sc.CMB_SIZE].read(lead, index)
    out = {t: sizes[t] / sc.SIZE_UNIT for t in ("settlement_coupon", "settlement_bill")}
    out.update(extra)
    return out


def effects(frame, walk, arm_name: str, terms: Sequence[str], lead: int, read, *, reps: int = REPS) -> Dict[str, dict]:
    """The fitted effect of each term in bp (per flagged day, or per USD 100 bn) at `lead`, by regime of the target day and pooled.

    For each decision day the effect is that of the refit the forecast used at `lead` times the anchor's scale in bp (0 where the term was not in
    the fit, counted). `read(lead, index)` gives the value of every term on the day's target. The shift is the sum of effect times value over the
    terms, so the mean absolute shift on the days some term is non-zero is reported. Each mean carries the 90% stationary-bootstrap interval over
    decision days (an interval over days that share refits, not a sampling interval for a coefficient).
    """

    per_day: Dict[date, dict] = {}
    for d in frame.days:
        estimate = walk.estimates[walk.fit_used[d]][arm_name][lead]
        scale = float(walk.detail[d]["scale"])
        value = read(lead, frame.position[d])
        row = {"regime": frame.regime(frame.target(d, lead))}
        for t in terms:
            row[t] = estimate.effect.get(t, 0.0) * scale
            row[f"in_fit_{t}"] = 1.0 if t in estimate.effect else 0.0
            row[f"value_{t}"] = value.get(t, 0.0)
        row["shift"] = sum(row[t] * row[f"value_{t}"] for t in terms)
        per_day[d] = row
    groups: Dict[str, List[date]] = {"all": list(frame.days)}
    for d, row in per_day.items():
        groups.setdefault(row["regime"], []).append(d)
    out: Dict[str, dict] = {}
    for name, members in groups.items():
        members = sorted(members)
        entry: dict = {"days": len(members)}
        columns = {t: [per_day[d][t] for d in members] for t in terms}
        for t in terms:
            entry[t] = {"mean": sum(columns[t]) / len(members), "share_in_fit": sum(per_day[d][f"in_fit_{t}"] for d in members) / len(members)}
        if len(members) >= MIN_GROUP_DAYS:
            intervals = metrics.stationary_bootstrap_intervals(
                lambda idx: [sum(columns[t][i] for i in idx) / len(idx) for t in terms], len(members),
                block_length=BLOCK, seed=SEED, replications=reps)
            for t, interval in zip(terms, intervals):
                entry[t]["interval"] = [interval[0], interval[1]]
        active = [d for d in members if any(abs(per_day[d][f"value_{t}"]) > EPSILON for t in terms)]
        entry["active_days"] = len(active)
        entry["mean_abs_shift_bp_on_active_days"] = sum(abs(per_day[d]["shift"]) for d in active) / len(active) if active else None
        out[name] = entry
    return out


# -- the checks ----------------------------------------------------------------------------------------------------------


def cmb_check(frame, facts: Mapping[date, dict], tables, immediate: Sequence[str]) -> dict:
    """What the CMB term reads on the scored target days.

    * per lead: the scored CMB settlement target days, those on which a CMB is announced by the decision (the flag is 1), and those that rest on an
      immediate-release announcement;
    * `gate_differs`: per lead, the (decision day, lead) cells on which the bill class is left out by (s3c-ann-net) (partly announced, #679) while a
      CMB is announced, so that the split does not add up to (s3c-ann-net)'s net bill;
    * `split_exact`: the cells on which net bill ex-CMB plus the CMB offering is not (s3c-ann-net)'s net bill, all of them gate cells.
    """

    _term, net_table, ex_table, cmb = tables
    out: Dict[str, dict] = {}
    for lead in LEADS:
        n = {"cmb_days": 0, "cmb_announced": 0, "immediate_days": 0, "gate_differs": 0, "split_not_exact": 0, "cmb_nonzero_cells": 0}
        for d in frame.days:
            i, t = frame.position[d], frame.target(d, lead)
            flag = cmb[sc.CMB_FLAG].read(lead, i)[sc.CMB_FLAG]
            size = cmb[sc.CMB_SIZE].read(lead, i)[sc.CMB_SIZE]
            n["cmb_nonzero_cells"] += 1 if flag else 0
            if facts[t]["cmb"]:
                n["cmb_days"] += 1
                n["cmb_announced"] += 1 if flag else 0
                n["immediate_days"] += 1 if t.isoformat() in immediate else 0
            whole = net_table.read(lead, i)["settlement_bill"]
            ex = ex_table.read(lead, i)["settlement_bill"]
            if abs(ex + size * sc.SIZE_UNIT - whole) > EPSILON:
                n["split_not_exact"] += 1
                n["gate_differs"] += 1 if size > 0 else 0
        out[str(lead)] = n
    return out


def lead_difference(frame, base: str, other: str) -> dict:
    return m1273.lead_difference(frame, base, other)


def _identical(series, candidate: str, reference: str, members: Sequence[date]) -> bool:
    return all(series[candidate][d] == series[reference][d] for d in members)


def unstudentized(series, candidate: str, reference: str, members: Sequence[date], reps: int) -> dict:
    """Mean d and its 90% stationary-bootstrap percentile interval, for a group whose studentized bound cannot be computed. Not the protocol's
    interval; no reading is taken from it. `d = S(reference) - S(candidate)`, positive favours the candidate."""

    d = [series[reference][x] - series[candidate][x] for x in sorted(members)]
    low, high = metrics.stationary_bootstrap_interval(
        lambda idx: sum(d[i] for i in idx) / len(idx), len(d), block_length=BLOCK, seed=SEED, replications=reps)
    return {"mean_d": sum(d) / len(d), "interval": [low, high], "days": len(d)}


def _pairs_task(job):
    split, label, grain, metric, candidate, members = job
    series = _STATE["series"][(grain, metric)]
    out: Dict[str, dict] = {}
    for name in plan(candidate, split):
        days = list(members)
        if _identical(series, candidate, name, days):
            out[name] = {"identical": True, "days": len(days)}
            continue
        out[name] = s761.run_pairs({name: series[name]}, series[candidate], days, seed=SEED, draws=_STATE["draws"], mean_d_fallback=True)[name]
        if "undefined" in out[name]:
            out[name]["unstudentized"] = unstudentized(series, candidate, name, days, _STATE["reps"])
    return (split, label, metric, candidate), out


def run_jobs(jobs, workers: int):
    with multiprocessing.get_context("fork").Pool(workers) as pool:
        return pool.map(_pairs_task, jobs, chunksize=1)


def extra_groups(frame, labels, facts, immediate: Sequence[str]) -> Tuple[List[tuple], Dict[str, int]]:
    """The groups this study adds to #1255's: 2020 by month and without the immediate-release CMB days, the settlement-day types at each lead, and
    the immediate-release CMB days against the other CMB days at each lead."""

    imm = set(immediate)
    y2020 = [t for t in sorted(labels) if frame.regime(t) == Y2020]
    out: List[tuple] = []
    if y2020:
        out += [("regime", Y2020_SPRING, "target", [t for t in y2020 if 3 <= t.month <= 6]),
                ("regime", Y2020_REST, "target", [t for t in y2020 if not 3 <= t.month <= 6]),
                ("regime", Y2020_NO_IMMEDIATE, "target", [t for t in y2020 if t.isoformat() not in imm])]
    counts: Dict[str, int] = {}
    for lead in LEADS:
        for label, members in m1288.day_type_members(frame, facts, lead).items():
            out.append((DAY_TYPE, f"h={lead}: {label}", f"lead{lead}", members))
        on = [d for d in frame.days if frame.target(d, lead).isoformat() in imm]
        other = [d for d in frame.days if facts[frame.target(d, lead)]["cmb"] and frame.target(d, lead).isoformat() not in imm]
        out += [(IMMEDIATE, f"h={lead}: an immediate-release CMB settles on the target", f"lead{lead}", on),
                (IMMEDIATE, f"h={lead}: another CMB settles on the target", f"lead{lead}", other)]
        counts[str(lead)] = len(on)
    return [g for g in out if g[3]], counts


def run_window(window: str, panel, splits, registry, table, register, results, auctions, immediate, args) -> dict:
    frame, notes, walks, names, tables, groups_fn = build(window, panel, splits, registry, table, register, results, auctions, args.first)
    last = WINDOW_LAST[window]
    labels = c.day_labels(frame, table)
    pressure = k.pressure_labels(frame, sorted(labels))
    facts = m1288.settlement_facts(panel, auctions)
    cells = {m: m1288.cell_table(frame, frame.forecasts[m], last) for m in MODELS}
    for m in MODELS:
        official = sp.day_scores(frame.forecasts[m], frame.outcome, frame.dates, score=sp.grid_crps)
        mean = s686.by_decision(cells[m]["grid_crps"])
        if set(official) != set(mean) or any(abs(official[d] - mean[d]) > 1e-9 for d in mean):
            raise SystemExit(f"grid CRPS of {m}: the cell means differ from scoring_protocol.day_scores")
    groups = [g for g in groups_fn(frame, labels, pressure) if g[0] in FULL_SPLITS]
    added, immediate_counts = extra_groups(frame, labels, facts, immediate)
    groups += added
    series: Dict[Tuple[str, str], Dict[str, Dict[date, float]]] = {}
    for _s, _l, grain, _m in groups:
        for metric in METRIC_NAMES:
            if (grain, metric) not in series:
                series[(grain, metric)] = {m: c.series_of(frame, cells[m][metric], grain) for m in MODELS}
    _STATE.update(series=series, draws=args.draws, reps=args.reps)

    jobs, skipped = [], {}
    for split, label, grain, members in groups:
        if len(members) < MIN_GROUP_DAYS:
            skipped[f"{split}/{label}"] = len(members)
            continue
        for metric in TESTED:
            for candidate in ARMS + (ANNNET,):
                jobs.append((split, label, grain, metric, candidate, tuple(members)))
    done = run_jobs(jobs, args.workers)

    reads = {m: (lambda lead, i, m=m: effect_values(m, lead, i, tables)) for m in (ANNNET, CMBF, CMBS)}
    arm_walk = {ANNNET: ("ref", names["ref"]), CMBF: ("flag", names["flag"]), CMBS: ("size", names["size"])}
    result: dict = {
        "notes": notes, "groups": {}, "skipped_groups": skipped, "immediate_release_target_days_by_lead": immediate_counts,
        "cmb_check": cmb_check(frame, facts, tables, immediate),
        "lead_difference": {"cmbf_against_ann_net": lead_difference(frame, ANNNET, CMBF), "cmbs_against_ann_net": lead_difference(frame, ANNNET, CMBS)},
        "effects": {m: {str(h): effects(frame, walks[arm_walk[m][0]], arm_walk[m][1], EFFECT_TERMS[m], h, reads[m], reps=args.reps) for h in LEADS}
                    for m in (ANNNET, CMBF, CMBS)},
    }
    for split, label, grain, members in groups:
        entry = result["groups"].setdefault(split, {}).setdefault(label, {"days": len(members)})
        for metric in METRIC_NAMES:
            ser = series[(grain, metric)]
            entry[metric] = {"means": {m: sum(ser[m][d] for d in members) / len(members) for m in MODELS}, "vs": {}}
    for (split, label, metric, candidate), payload in done:
        result["groups"][split][label][metric]["vs"][candidate] = payload
    result["pressure_day_type_counts"] = {x: sum(1 for t in pressure.values() if t == x) for x in sorted(set(pressure.values()))}
    return result


def against_1321(results: Mapping[str, dict]) -> dict:
    """The pooled means of (s3c) and (s3c-ann-net) here beside #1321's record, made at 18:00 with the same walks: they must agree to 1e-9.

    Raises:
        ValueError: they do not.
    """

    if not RECORD_1321.exists():
        return {}
    there = json.loads(RECORD_1321.read_text(encoding="utf-8"))["windows"]
    out: Dict[str, dict] = {}
    for window, result in results.items():
        a, b = there[window]["groups"]["pooled"]["all decision days"], result["groups"]["pooled"]["all decision days"]
        out[window] = {m: {x: {"now": b[m]["means"][x], "then": a[m]["means"][x], "difference": b[m]["means"][x] - a[m]["means"][x]}
                           for x in (S3C, ANNNET)} for m in ("grid_crps", "upper_tail_twcrps", "brier_gt5")}
        worst = max(abs(v["difference"]) for rows in out[window].values() for v in rows.values())
        if worst > 1e-9:
            raise ValueError(f"the references of the {window} window differ from #1321's record by {worst:.2e}: the walks are not the same")
    return out


def score(args) -> int:
    """Score both windows with every module of the chain at the declared decision instant (`decision_instant_pinned`)."""

    with decision_instant_pinned():
        return _score(args)


def _score(args) -> int:
    declaration = committed_declaration()
    panel_path = Path(args.panel)
    published_sha = panel_sha256(panel_path)
    panel = [row for row in load_daily_panel(panel_path) if row.date <= LAST_DAY]
    require_exploratory_window([row.date for row in panel], where="scripts/s3c_ann_net_cmb_1356")
    splits = load_split_declaration(c.SPLITS)
    registry = json.loads(c.SOURCES.read_text(encoding="utf-8"))
    register = policy_events.load_register()
    table = cal.TermTable(panel, announced_iorb.load_announcements(c.IORB_TABLE), decision_time=c.DECISION_TIME)
    auctions = m1273.load_auctions()
    results = m1288.load_results()
    immediate = release_days()
    result: dict = {
        "issue": 1356, "declaration": str(DECLARATION.relative_to(REPO)), "panel_sha256": published_sha,
        "decision_time": c.DECISION_TIME.strftime("%H:%M"), "subset_from": None if args.first is None else args.first.isoformat(),
        "label": "development, not a verdict", "seed": SEED, "draws": args.draws, "reps": args.reps, "models": list(MODELS),
        "arms": list(ARMS), "references": [ANNNET, S3C] + list(BENCHMARKS), "margin_bp": s3c_candidate.MARGIN_BP,
        "dating": json.loads(m1288.DATING.read_text(encoding="utf-8"))["available_time"],
        "windows": {}, "reading_rules": declaration["reading_rules"],
    }
    for window in WINDOWS:
        result["windows"][window] = run_window(window, panel, splits, registry, table, register, results, auctions, immediate, args)
    result["against_1321"] = against_1321(result["windows"]) if args.first is None else {}
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    Path(args.output).write_text(json.dumps(result, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    return 0


# -- the page ------------------------------------------------------------------------------------------------------------


def cell(row: Optional[dict]) -> str:
    return m1288.cell(row)


def _vs(group: Optional[Mapping[str, object]], metric: str, candidate: str, reference: str) -> Optional[dict]:
    return m1288._vs(group, metric, candidate, reference)


def reading(row: Optional[dict]) -> str:
    """`gain`, `loss`, `undecided`, `identical` or `n/a` on the mean-d bound, for a candidate against a reference."""

    if row is None:
        return "n/a"
    return "identical" if row.get("identical") else k.reading_words(row).split(" ")[0].strip("*")


def mean_table(group: Mapping[str, object]) -> List[str]:
    out = ["| model | " + " | ".join(METRIC_TITLES[m] + " (mean)" for m in METRIC_NAMES) + " |", "|---|" + "---|" * len(METRIC_NAMES)]
    for m in MODELS:
        out.append(f"| {LABELS[m]} | " + " | ".join(
            f"{group[x]['means'][m]:.3f}" if x in ("grid_crps", "upper_tail_twcrps") else f"{group[x]['means'][m]:.4f}" for x in METRIC_NAMES) + " |")
    return out


def against_table(group: Mapping[str, object], candidate: str, split: str = "pooled") -> List[str]:
    out = [f"| {SHORT[candidate]} against | " + " | ".join(METRIC_TITLES[m] for m in TESTED) + " |", "|---|" + "---|" * len(TESTED)]
    for ref in plan(candidate, split):
        out.append(f"| {SHORT[ref]} | " + " | ".join(cell(_vs(group, m, candidate, ref)) for m in TESTED) + " |")
    return out


def split_table(window: Mapping[str, object], split: str, candidate: str, reference: str, order: Optional[Sequence[str]] = None) -> List[str]:
    return m1288.split_table(window, split, candidate, reference, order)


def means_split_table(window: Mapping[str, object], split: str, metric: str, models: Sequence[str] = (S3C, ANNNET, CMBF, CMBS)) -> List[str]:
    labels = window["groups"].get(split, {})
    out = [f"| {split.replace('_', ' ')} | days | " + " | ".join(SHORT[m] for m in models) + " |", "|---|---|" + "---|" * len(models)]
    for label in sorted(labels):
        g = labels[label]
        out.append(f"| {label} | {g['days']} | " + " | ".join(f"{g[metric]['means'][m]:.4f}" for m in models) + " |")
    return out if len(out) > 2 else []


def effect_table(by_lead: Mapping[str, Mapping[str, dict]], terms: Sequence[str]) -> List[str]:
    cols = [f"{TERM_TITLES[t]} ({TERM_UNITS[t]}) [90%]" for t in terms]
    out = ["| lead | regime | days | " + " | ".join(cols) + " | share of days in the fit | mean abs shift on active days (bp) |",
           "|---|---|---|" + "---|" * (len(terms) + 2)]
    for lead in sorted(by_lead, key=int):
        eff = by_lead[lead]
        for name in sorted(eff, key=lambda x: (x != "all", x)):
            if name != "all" and lead != REGIME_LEAD:
                continue
            e = eff[name]
            parts = []
            for t in terms:
                m = e[t]
                parts.append(f"{m['mean']:+.3f}" + (f" [{m['interval'][0]:+.3f}, {m['interval'][1]:+.3f}]" if "interval" in m else " (too few days)"))
            shift = "n/a" if e["mean_abs_shift_bp_on_active_days"] is None else f"{e['mean_abs_shift_bp_on_active_days']:.3f}"
            share = " / ".join(f"{e[t]['share_in_fit']:.2f}" for t in terms)
            out.append(f"| h={lead} | {name} | {e['days']} | " + " | ".join(parts) + f" | {share} | {shift} |")
    return out


def check_table(check: Mapping[str, Mapping[str, int]]) -> List[str]:
    out = ["| lead | CMB settlement target days | CMB announced by the decision | resting on an immediate-release announcement | cells with a CMB announced | cells where the class gate makes the split differ |",
           "|---|---|---|---|---|---|"]
    for lead in LEADS:
        n = check[str(lead)]
        share = f"{n['cmb_announced']} ({n['cmb_announced'] / n['cmb_days']:.0%})" if n["cmb_days"] else "0"
        out.append(f"| h={lead} | {n['cmb_days']} | {share} | {n['immediate_days']} | {n['cmb_nonzero_cells']} | {n['gate_differs']} |")
    return out


def _groups_with(w: Mapping[str, object], split: str) -> Mapping[str, object]:
    return w["groups"].get(split, {})


def answer(r: Mapping[str, object]) -> List[str]:
    """The plain answer to the directive's question, built from the intervals: does the arm remove (s3c-ann-net)'s 2020 loss, and at what cost
    elsewhere. Grid CRPS, the mean-d bound. Nothing here is a verdict."""

    out = ["## Does the arm remove the 2020 loss, and at what cost elsewhere?", "",
           "Read on grid CRPS (primary) on the mean-d bound; the other scores and the full tables follow. A reading of 'undecided' means the 90% interval "
           "of mean d includes zero. Positive d favours the first-named model.", ""]
    for window in WINDOWS:
        w = r["windows"].get(window)
        if w is None:
            continue
        regime = _groups_with(w, "regime")
        out.append(f"**{WINDOW_TITLES[window].split(' (')[0]}.**")
        for label in (Y2020, Y2020_SPRING, Y2020_REST):
            g = regime.get(label)
            if g is None:
                continue
            base = _vs(g, "grid_crps", ANNNET, S3C)
            parts = [f"(s3c-ann-net) against (s3c): {cell(base)}"]
            for form in ARMS:
                parts.append(f"{SHORT[form]} against (s3c): {cell(_vs(g, 'grid_crps', form, S3C))}; against (s3c-ann-net): "
                             f"{cell(_vs(g, 'grid_crps', form, ANNNET))}")
            out.append(f"- {label} ({g['days']} target days): " + "; ".join(parts) + ".")
        for form in ARMS:
            worse, better = [], []
            for split in FULL_SPLITS + (DAY_TYPE, IMMEDIATE):
                for label, g in sorted(_groups_with(w, split).items()):
                    if split in ("pooled",):
                        continue
                    word = reading(_vs(g, "grid_crps", form, ANNNET))
                    (worse if word == "loss" else better if word == "gain" else []).append(f"{split.replace('_', ' ')}: {label}")
            out.append(f"- {SHORT[form]} against (s3c-ann-net), grid CRPS: read worse on {len(worse)} group(s)"
                       + (" (" + "; ".join(worse) + ")" if worse else "") + f"; read better on {len(better)}"
                       + (" (" + "; ".join(better) + ")" if better else "") + ".")
        out.append("")
    return out


def headline(r: Mapping[str, object]) -> str:
    parts = []
    for window, text in (("development", "On the development window"), ("2026", "on the 2026 development days")):
        w = r["windows"].get(window)
        if w is None:
            continue
        g = w["groups"]["pooled"]["all decision days"]
        parts.append(f"{text}, pooled grid CRPS against (s3c-ann-net): " + "; ".join(f"{SHORT[f]} {cell(_vs(g, 'grid_crps', f, ANNNET))}" for f in ARMS))
    return "; ".join(parts) + "."


def render(r: dict) -> str:
    out = [
        "# (s3c-ann-net-cmb): a separate cash management bill term on (s3c-ann-net), at the 18:00 decision (#1356)", "",
        "**Does giving the cash management bill its own term remove (s3c-ann-net)'s 2020 loss against (s3c), and at what cost?** " + headline(r), "",
        "**Hypothesis and step:** H5 (primary goal), step 3, an arm on the candidate (s3c-ann-net); avenue #1306, diagnosis #1320; her ruling of 2 November "
        "2026 (chat, relayed on #1356). **Development data, not a verdict** (scoring protocol v1, #640). **(s3c-ann-net) stays the candidate of avenue #1318 "
        "and (s3c) the H5 candidate; nothing here changes either, and adopting the arm is hers.** Nothing is registered or published and no claim changes. "
        "Generated by `scripts/s3c_ann_net_cmb_1356.py page` from `docs/research/s3c-ann-net-cmb-1356/result.json`, not edited by hand; declared in "
        f"`{r['declaration']}` before any score.", "",
        "**What changed.** In (s3c-ann-net) a cash management bill (CMB) is one of the bill auctions summed into the signed net bill. (s3c-ann-net-cmb) "
        "takes the CMB offerings out of the net bill (**net bill ex-CMB**; the class's maturing amount stays with the regular bills, so the two legs add up "
        "to (s3c-ann-net)'s net bill wherever the bill class is counted) and gives the CMB its own term, read from the announcement "
        f"({r['dating']} New York time on the `announcemt_date`, #541, not in force) at every lead, on direct pairs, at the {r['decision_time']} decision "
        "instant (#1312). Two forms were declared before any score: **flag** (`cmb_flag`, 1 when a CMB announced by the decision settles on the target day, "
        "in bp per flagged day) and **size** (`cmb_size`, the announced CMB offering in USD 100 bn). A CMB announced after the decision instant is not "
        "readable at that lead (finding #1301: one announced and settled inside the lead window is not counted). Everything else is (s3)'s and the SRF cap "
        "is (s3c)'s. The references (s3c-ann-net) and (s3c), and the benchmarks B1, B1' and B2, are scored in the same run.", "",
        "**Lens E's caveat applies in full** (`docs/reviews/2026-10-19-five-lens/lens-E-data-plumbing.md`, item G): Treasury publishes no clock time for "
        "the announcement of a CMB; 153 of the 163 'for immediate release' announcements are CMBs, and the 12:00 instant of those is unverified. If one is "
        "released after the 18:00 decision of its announcement day, the term counts it a decision too early. The immediate-release CMB days are scored on "
        "their own below.", "",
        f"Panel digest `{r['panel_sha256']}`. Studentized stationary bootstrap (ruling 1), mean block {sp.BLOCK_LENGTH} business days, "
        f"{r['draws']:,} draws, seed {r['seed']}, two-sided 90% interval (the lower end is the one-sided 95% bound). Positive mean d favours the model "
        "named first. **A reading (gain, loss, undecided) is taken from the mean-d bound** (her ruling on #1009), with the skill interval beside it; for a "
        "Brier score the skill is the Brier skill score. **Caveat (Lens C, #958):** the lag-10 HAC standard error that studentizes the bound is "
        "understated about 2x after 2020, so an interval that excludes zero is narrower than it should be. The intervals of a group of target days keep the "
        "**current method** (the group's days, scattered, resampled in date order as if consecutive), which #1221 questions and #1228 will decide; no reading "
        "of a day-type group is a finding. Where two models differ on few days of a group the bound may not be computed: the unstudentized interval of mean d "
        "is then given beside it, and no reading is taken from that. Groups of fewer than 20 days are listed with their means and not tested. The "
        "benchmarks are tested on the pooled, lead, regime and pressure-day-type groups only.", "",
        "**What kind of look this is.** The 2026 days were already seen by #845, by the #151 final test, and by #1229, #1255, #1273, #1288 and #1321. The "
        "2026 days are shown separately and decide nothing. This is a check on an arm queued by her ruling, not evidence for a verdict.", ""]
    out += answer(r)
    for window in WINDOWS:
        w = r["windows"].get(window)
        if w is None:
            continue
        n, pooled = w["notes"], w["groups"]["pooled"]["all decision days"]
        ld, chk = w["lead_difference"], w["cmb_check"]
        out += [f"## {WINDOW_TITLES[window]}", "",
                f"Scored decision days: {n['scored_decision_days']:,} ({n['first']} to {n['last']}); {n['refits_ref']} refits of the reference walk and "
                f"{n['refits_flag']} and {n['refits_size']} of the two forms' walks. Cells on which a form is not (s3c-ann-net) element for element, by lead "
                f"(of {ld['cmbf_against_ann_net']['cells_per_lead']:,} each): flag: "
                + ", ".join(f"h={h}: {ld['cmbf_against_ann_net']['differing_cells'][str(h)]:,}" for h in LEADS) + "; size: "
                + ", ".join(f"h={h}: {ld['cmbs_against_ann_net']['differing_cells'][str(h)]:,}" for h in LEADS) + ".", "",
                "### What the CMB term reads on the scored days", ""] + check_table(chk) + [
                "", "The class gate: (s3c-ann-net) reads a bill class that is partly announced as 0.0 (#679), and the CMB term is not gated by it, so on those cells "
                "the two legs do not add up to (s3c-ann-net)'s net bill (the last column).", "",
                "### Mean scores (pooled)", ""] + mean_table(pooled)
        for arm in ARMS:
            out += ["", f"### {LABELS[arm]} against each reference (pooled)", ""] + against_table(pooled, arm) + [""]
        for split, title in (("lead", "By lead"), ("regime", "By regime"), ("pressure_day_type", "By pressure-day type of the target day"),
                             (DAY_TYPE, "By the settlement-day type of the target at each lead"),
                             (IMMEDIATE, "The CMB days that rest on an immediate-release announcement, at each lead")):
            for arm in ARMS:
                for ref in plan(arm, split)[:2]:
                    table = split_table(w, split, arm, ref)
                    if table:
                        out += [f"### {title}: {SHORT[arm]} against {SHORT[ref]}", ""] + table + [""]
        table = split_table(w, "regime", ANNNET, S3C)
        if table:
            out += ["### The baseline: (s3c-ann-net) against (s3c), by regime", ""] + table + [""]
        for split, title in (("regime", "regime"), ("pressure_day_type", "pressure-day type")):
            table = means_split_table(w, split, "b90_closed")
            if table:
                out += [f"### 90% band coverage by {title}", ""] + table + [""]
        out += ["### The fitted effect, by lead and regime of the target day", ""]
        for model in (ANNNET, CMBF, CMBS):
            out += [f"{LABELS[model]}:", ""] + effect_table(w["effects"][model], EFFECT_TERMS[model]) + [""]
        out += ["The effect is the standardised effect of the refit the forecast used times the scale at the anchor in bp. The pooled row is printed at every "
                "lead and the regime rows at h = 3 only (the record holds them all). The interval is a bootstrap interval of the mean over decision days, "
                "which share refits; it is not a sampling interval for the coefficient. A term enters a fit only when at least three training pairs carry it.",
                ""]
        if w["skipped_groups"]:
            out += ["Groups of fewer than 20 days, listed and not tested: " + ", ".join(f"{x} ({n_})" for x, n_ in sorted(w["skipped_groups"].items())) + ".", ""]
    if r.get("against_1321"):
        out += ["## The references against #1321's record (made at 18:00)", "",
                "(s3c) and (s3c-ann-net) are re-run here with the same walks; the pooled means equal #1321's to 1e-9 (the run refuses to write otherwise). "
                "Largest absolute difference: "
                f"{max(abs(v['difference']) for ms in r['against_1321'].values() for rows in ms.values() for v in rows.values()):.1e}.", ""]
    out += question()
    return "\n".join(out).rstrip() + "\n"


def question() -> List[str]:
    return [
        "## Question for Eleonora (marked; the default changes no claim)", "",
        "**Does either form of the CMB term replace (s3c-ann-net) as the candidate of avenue #1318?** The candidate does not change in this directive. "
        "Whether a form should replace it rests on days already seen, split as above, and on an announcement time that is unverified for the "
        "immediate-release CMBs.", "",
        "**Options** (the default applies if you have not answered by the next 5 pm batch):", "",
        "1. **(s3c-ann-net) stays the candidate and nothing changes** (default).",
        "2. **Draft a directive that tests the better form prospectively**, on the confirmation days only, under the scoring protocol.",
        "3. **Ask for a check of the CMB announcement times** against Treasury's files for the immediate-release bills, in a directive of its own.", ""]


def page(args) -> int:
    r = json.loads(Path(args.score).read_text(encoding="utf-8"))
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    Path(args.output).write_text(render(r), encoding="utf-8")
    return 0


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="command", required=True)
    s = sub.add_parser("score", help="walk (s3c-ann-net) and the two forms, cap them as (s3c) is capped, and score on both windows")
    s.add_argument("--panel", required=True)
    s.add_argument("--output", required=True)
    s.add_argument("--draws", type=int, default=sp.DRAWS)
    s.add_argument("--reps", type=int, default=REPS, help="bootstrap resamples of the unstudentized and effect intervals")
    s.add_argument("--workers", type=int, default=4)
    s.add_argument("--first", type=date.fromisoformat, default=None,
                   help="start the walk on this day (a subset, for the script's test only; the declared run omits it)")
    s.set_defaults(func=score)
    g = sub.add_parser("page", help="write the result page from a score file")
    g.add_argument("--score", required=True)
    g.add_argument("--output", required=True)
    g.set_defaults(func=page)
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
