"""(s3c-ann-net-cmb): (s3c-ann-net) with the cash management bills split out of the bill leg and given a term of their own, scored against
(s3c-ann-net), (s3c), B1, B1' and B2 at the 18:00 decision instant (#1356; H5 step 3; avenue #1306, her ruling of 2 November 2026).

A development study, never a verdict. It writes JSON and Markdown to the paths it is given and nothing into `docs/runs/`. Every choice is in
`metadata/s3c_ann_net_cmb_1356.json`, which this script refuses to read unless it is committed and unchanged. The arms are `repo_model.s3c_cmb`:
(s3c-ann-net) with the bill term read net of the cash management bills at leads 2 to 5 and the cash management bill term beside it, as a 0/1 flag
and as a net size, each capped as (s3c) is capped (`repo_model.s3c_candidate`, unchanged), and each also on the prior-day reading that does not
rely on the unverified release time of an announcement made on the decision day (finding #1301). The references (s3c) and (s3c-ann-net) are
re-run in the same run, at 18:00 (`repo_model.decision_instant`). The frames and the machinery are #1255's, #1273's, #1288's and #1321's and are
loaded as they are: the development window (targets up to 2025-12-31) and the 2026 development days (targets 2026-01-02 to 2026-09-03). The blind
tier and every lockbox day are refused by the frames' own guards.

It measures grid CRPS averaged over h = 1..5 (primary), upper-tail twCRPS (key secondary) and the Brier score of P(> +5 bp), on scoring protocol
v1's studentized stationary bootstrap read on the bound on mean d (her #1009 ruling) with the skill interval beside, split by lead, regime (2020,
and March to June 2020 inside it), pressure-day type and the settlement-day type of the target at each lead (bill settlement days with a cash
management bill against the other bill days); reports the coverage of the central 90% band; the fitted effect of the cash management bill term;
and how many cash management bill settlement days each reading can see at each lead.

Commands, from a clone of the branch (the walks are minutes, the paired tests the longer part):

    PYTHONPATH=src python3 -m repo_model.cli build --raw-root tests/fixtures/snapshots/funding_inputs \\
        --output PUB.csv --build-cutoff 2026-09-08T21:31:42+00:00 --decision-time 18:00:00
    PYTHONPATH=src python3 -m repo_model.cli verify-panel PUB.csv --manifest metadata/funding_panel_manifest.json
    PYTHONPATH=src python3 scripts/s3c_ann_net_cmb_1356.py score --panel PUB.csv \\
        --output docs/research/s3c-ann-net-cmb-1356/result.json
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


from repo_model import announced_iorb, metrics, policy_events, s3c_announced, s3c_candidate, s3c_cmb, s3c_net  # noqa: E402
from repo_model import scoring_protocol as sp, spread_mr_state_calendar as sc  # noqa: E402
from repo_model.baseline import panel_sha256  # noqa: E402
from repo_model.evaluation_splits import load_split_declaration  # noqa: E402
from repo_model.exploration import EXPLORATORY_END, require_exploratory_window  # noqa: E402
from repo_model import spread_mr_calendar as cal  # noqa: E402

#: #1321's script (and through it #1288's, #1273's, #1255's, #1241's and #1229's), loaded under an alias of its own so that the pickling of the
#: worker pool's tasks does not meet another test module's copy. It supplies the pin of the decision instant and the frames.
m1321 = _load("s3c_flagnet_gross_1321", "s3c_flagnet_gross_1321_in_1356")
m1288 = m1321.m1288
m1273, m1255, k, c, s686, s761 = m1288.m1273, m1288.m1255, m1288.k, m1288.c, m1288.s686, m1288.s761
load_daily_panel = m1288.load_daily_panel

DECLARATION = REPO / "metadata" / "s3c_ann_net_cmb_1356.json"
SEED = 1356
LAST_DAY = EXPLORATORY_END
WINDOW_LAST = m1288.WINDOW_LAST
WINDOWS = m1288.WINDOWS
WINDOW_TITLES = m1288.WINDOW_TITLES
S3C, ANNNET, B1P = m1288.S3C, m1288.ANNNET, m1288.B1P
BENCHMARKS = m1288.BENCHMARKS
FLAG, SIZE, FLAGP, SIZEP = "sc_s3c_ann_net_cmb_flag", "sc_s3c_ann_net_cmb_size", "sc_s3c_ann_net_cmb_flag_prior", "sc_s3c_ann_net_cmb_size_prior"
FORMS = (FLAG, SIZE)
PRIOR = (FLAGP, SIZEP)
ARMS = FORMS + PRIOR
#: Every model tested as a candidate: the arms, and (s3c-ann-net) against (s3c) for the 2020 question.
CANDIDATES = (ANNNET,) + ARMS
MODELS = BENCHMARKS + (S3C, ANNNET) + ARMS
LABELS = {
    "B1": "B1", B1P: "B1'", "B2": "B2", S3C: "(s3c)", ANNNET: "(s3c-ann-net), the candidate",
    FLAG: "(s3c-ann-net-cmb), flag form", SIZE: "(s3c-ann-net-cmb), net-size form",
    FLAGP: "(s3c-ann-net-cmb), flag form, prior-day reading", SIZEP: "(s3c-ann-net-cmb), net-size form, prior-day reading",
}
SHORT = {"B1": "B1", B1P: "B1'", "B2": "B2", S3C: "(s3c)", ANNNET: "(s3c-ann-net)", FLAG: "(cmb, flag)", SIZE: "(cmb, size)",
         FLAGP: "(cmb, flag, prior-day)", SIZEP: "(cmb, size, prior-day)"}
#: The walk each arm comes from, and its name in `sc.walk`.
ARM_NAMES = {ANNNET: ("ref", s3c_announced.ANN_NET_ARM.name), FLAG: ("main", s3c_cmb.FLAG_ARM.name), SIZE: ("main", s3c_cmb.SIZE_ARM.name),
             FLAGP: ("prior", s3c_cmb.FLAG_PRIOR_ARM.name), SIZEP: ("prior", s3c_cmb.SIZE_PRIOR_ARM.name)}
TESTED = m1288.TESTED
METRIC_NAMES = m1288.METRIC_NAMES
METRIC_TITLES = m1288.METRIC_TITLES
MIN_GROUP_DAYS = m1288.MIN_GROUP_DAYS
BLOCK = float(sp.BLOCK_LENGTH)
EPSILON = 1e-9
LEADS = tuple(sp.HORIZONS)
SPLITS = ("pooled", "lead", "regime", "pressure_day_type")
DAY_TYPE = m1288.DAY_TYPE
TYPE_LABELS = m1288.TYPE_LABELS
REGIME_2020 = "2020"
SPRING = "2020: March to June"
REST_2020 = "2020: rest of the year"
SPRING_FROM, SPRING_TO = date(2020, 3, 1), date(2020, 6, 30)
#: The terms of the effect tables, and the unit of each effect.
EFFECT_ARMS = (ANNNET, FLAG, SIZE)
EFFECT_TERMS: Mapping[str, Tuple[str, ...]] = {
    ANNNET: ("settlement_coupon", "settlement_bill"),
    FLAG: ("settlement_coupon", "settlement_bill", sc.CMB_FLAG),
    SIZE: ("settlement_coupon", "settlement_bill", sc.CMB_NET),
}
TERM_TITLES = {"settlement_coupon": "net coupon", "settlement_bill": "net bill (regular bills for the arms)", sc.CMB_FLAG: "cash management bill flag",
               sc.CMB_NET: "cash management bill net"}
TERM_UNITS = {"settlement_coupon": "bp per USD 100 bn", "settlement_bill": "bp per USD 100 bn", sc.CMB_FLAG: "bp per flagged day",
              sc.CMB_NET: "bp per USD 100 bn"}
REGIME_LEAD = "3"
REPS = 2000


def committed_declaration(path: Path = DECLARATION) -> dict:
    """The declaration, refused unless it is committed and unchanged since `HEAD`."""

    return s686.committed_declaration(path)


def plan(candidate: str) -> List[str]:
    """What a candidate is tested against: a form against (s3c-ann-net), (s3c) and the benchmarks; a prior-day arm against (s3c-ann-net) only;
    (s3c-ann-net) against (s3c), for the 2020 question."""

    if candidate in FORMS:
        return [ANNNET, S3C] + list(BENCHMARKS)
    if candidate in PRIOR:
        return [ANNNET]
    if candidate == ANNNET:
        return [S3C]
    return []


# -- the walks and the frame ---------------------------------------------------------------------------------------------


def walks_of(window: str, frame, panel, splits, registry, results, auctions, first: Optional[date]):
    """The walks of (s3c-ann-net) and of the four arms over #1255's decision days, with the tables they read.

    Raises:
        ValueError: a scored decision day has no forecast of a walk, or an arm is not (s3c-ann-net) at lead 1 on a scored decision day.
    """

    days = m1288.candidate_days(frame, window, first)
    settings = dict(registry=registry, decision_time=k.DECISION_TIME, splits=splits)
    states = s3c_net.constant_states(panel)
    iorb = announced_iorb.load_announcements(c.IORB_TABLE)
    term_table = s3c_announced.AnnouncedTermTable(panel, iorb, results, decision_time=k.DECISION_TIME)
    net_table = s3c_announced.AnnouncedNetSizeTable(panel, auctions, decision_time=k.DECISION_TIME)
    size = s3c_cmb.CmbSizeTable(panel, auctions, decision_time=k.DECISION_TIME)
    size_prior = s3c_cmb.CmbSizeTable(panel, auctions, prior_day_only=True, decision_time=k.DECISION_TIME)
    terms, terms_prior = s3c_cmb.CmbTerms(size), s3c_cmb.CmbTerms(size_prior)
    walks = {
        "ref": sc.walk(panel, days, term_table, states, (s3c_announced.ANN_NET_ARM,), sizes=net_table, **settings),
        "main": sc.walk(panel, days, term_table, states, (s3c_cmb.FLAG_ARM, s3c_cmb.SIZE_ARM), sizes=size, iorb=terms, **settings),
        "prior": sc.walk(panel, days, term_table, states, (s3c_cmb.FLAG_PRIOR_ARM, s3c_cmb.SIZE_PRIOR_ARM), sizes=size_prior, iorb=terms_prior,
                         **settings),
    }
    for model, (key, name) in ARM_NAMES.items():
        for d in frame.days:
            if d not in walks[key].forecasts[name]:
                raise ValueError(f"the {key} walk has no forecast of {name} on the scored decision day {d}")
    for d in frame.days:
        at_one = walks["ref"].forecasts[s3c_announced.ANN_NET_ARM.name][d][1]
        for model in ARMS:
            key, name = ARM_NAMES[model]
            if walks[key].forecasts[name][d][1] != at_one:
                raise ValueError(f"{name} is not (s3c-ann-net) at lead 1 on {d}: the cash management bill term is read at leads 2 to 5")
    return walks, dict(term=term_table, net=net_table, size=size, size_prior=size_prior, terms=terms, terms_prior=terms_prior)


def build(window: str, panel, splits, registry, table, register, results, auctions, first: Optional[date]):
    """#1255's frame of `window` with (s3c-ann-net) and the arms added: `(frame, notes, walks, tables, groups_fn)`."""

    frame, notes, _mine, _cells, groups_fn = m1255.build(window, panel, splits, registry, table, register, first)
    walks, tables = walks_of(window, frame, panel, splits, registry, results, auctions, first)
    forecasts = {name: frame.forecasts[name] for name in BENCHMARKS}
    forecasts[S3C] = frame.forecasts[S3C]
    for model, (key, name) in ARM_NAMES.items():
        raw = {d: walks[key].forecasts[name][d] for d in frame.days}
        forecasts[model] = m1255.s3c_forecasts(frame, register, raw)
    frame.forecasts = {name: {d: forecasts[name][d] for d in frame.days} for name in MODELS}
    notes = dict(notes, refits_ref=len(walks["ref"].fits), refits_main=len(walks["main"].fits), refits_prior=len(walks["prior"].fits))
    return frame, notes, walks, tables, groups_fn


def lead_difference(frame, base: str, other: str) -> dict:
    return m1273.lead_difference(frame, base, other)


# -- the cash management bill days each reading can see ------------------------------------------------------------------


def cmb_coverage(frame, facts: Mapping[date, dict], tables) -> dict:
    """Per lead, over the scored target days: the bill settlement days with a cash management bill, how many the declared reading flags at the
    decision, how many the prior-day reading flags, and how many the declared reading flags only through an announcement made on the decision day;
    and the same for the days with a flag of any cash management bill by regime of the target."""

    out: Dict[str, dict] = {}
    for lead in s3c_cmb.CMB_LEADS:
        counts = {"cmb_days": 0, "flagged": 0, "flagged_prior_day": 0, "flagged_only_same_day": 0, "non_cmb_days_flagged": 0}
        by_regime: Dict[str, Dict[str, int]] = {}
        for d in frame.days:
            t = frame.target(d, lead)
            i = frame.position[d]
            flag = tables["terms"].read(lead, i)[sc.CMB_FLAG]
            prior = tables["terms_prior"].read(lead, i)[sc.CMB_FLAG]
            if facts[t]["cmb"] and facts[t]["bill"]:
                entry = by_regime.setdefault(frame.regime(t), {"cmb_days": 0, "flagged": 0})
                entry["cmb_days"] += 1
                entry["flagged"] += flag
                counts["cmb_days"] += 1
                counts["flagged"] += flag
                counts["flagged_prior_day"] += prior
                counts["flagged_only_same_day"] += flag and not prior
            else:
                counts["non_cmb_days_flagged"] += flag
        out[str(lead)] = dict(counts, by_regime=by_regime)
    return out


# -- the fitted effect ---------------------------------------------------------------------------------------------------


def effect_values(arm: str, lead: int, index: int, tables) -> Dict[str, float]:
    """The value of each of the arm's terms on the target of the decision on row `index`, in units of USD 100 bn (a flag: 0/1)."""

    if arm == ANNNET:
        sizes = tables["net"].read(lead, index)
        return {t: sizes[t] / sc.SIZE_UNIT for t in EFFECT_TERMS[arm]}
    size, terms = (tables["size"], tables["terms"])
    sizes = size.read(lead, index)
    out = {t: sizes[t] / sc.SIZE_UNIT for t in ("settlement_coupon", "settlement_bill")}
    out.update({name: float(v) for name, v in terms.read(lead, index).items()})
    return out


def effects(frame, walk, arm_name: str, terms: Sequence[str], lead: int, read, *, reps: int = REPS) -> Dict[str, dict]:
    """The fitted effect of each term in bp (per flagged day, or per USD 100 bn) at `lead`, by regime of the target day and pooled.

    For each decision day the effect is that of the refit the forecast used at `lead` times the anchor's scale in bp (0 where the term was not in
    the fit, counted). `read(lead, index)` gives the value of every term on the day's target. Each mean carries the 90% stationary-bootstrap interval
    over decision days (an interval over days that share refits, not a sampling interval for a coefficient).
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


# -- the groups and the tests --------------------------------------------------------------------------------------------


_STATE: Dict = {}


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
    for name in plan(candidate):
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


def regime_2020_groups(labels: Mapping[date, Sequence[str]]) -> List[Tuple[str, str, str, List[date]]]:
    """The two target-day groups inside 2020: March to June, and the rest of the year."""

    targets = [t for t in sorted(labels) if t.year == 2020]
    spring = [t for t in targets if SPRING_FROM <= t <= SPRING_TO]
    rest = [t for t in targets if t not in set(spring)]
    return [("regime", label, "target", members) for label, members in ((SPRING, spring), (REST_2020, rest)) if members]


def run_window(window: str, panel, splits, registry, table, register, results, auctions, args) -> dict:
    frame, notes, walks, tables, groups_fn = build(window, panel, splits, registry, table, register, results, auctions, args.first)
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
    groups = [g for g in groups_fn(frame, labels, pressure) if g[0] in SPLITS] + regime_2020_groups(labels)
    for lead in LEADS:
        for label, members in m1288.day_type_members(frame, facts, lead).items():
            groups.append((DAY_TYPE, f"h={lead}: {label}", f"lead{lead}", members))
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
            for candidate in CANDIDATES:
                jobs.append((split, label, grain, metric, candidate, tuple(members)))
    done = run_jobs(jobs, args.workers)

    reads = {arm: (lambda lead, i, arm=arm: effect_values(arm, lead, i, tables)) for arm in EFFECT_ARMS}
    result: dict = {
        "notes": notes, "groups": {}, "skipped_groups": skipped,
        "cmb_coverage": cmb_coverage(frame, facts, tables),
        "lead_difference": {m: lead_difference(frame, ANNNET, m) for m in ARMS},
        "effects": {
            arm: {str(h): effects(frame, walks[ARM_NAMES[arm][0]], ARM_NAMES[arm][1], EFFECT_TERMS[arm], h, reads[arm], reps=args.reps)
                  for h in LEADS}
            for arm in EFFECT_ARMS
        },
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


def score(args) -> int:
    """Score both windows with every module of the chain at the declared decision instant (`m1321.decision_instant_pinned`)."""

    with m1321.decision_instant_pinned():
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
    result: dict = {
        "issue": 1356, "declaration": str(DECLARATION.relative_to(REPO)), "panel_sha256": published_sha,
        "decision_time": c.DECISION_TIME.strftime("%H:%M"), "subset_from": None if args.first is None else args.first.isoformat(),
        "label": "development, not a verdict", "seed": SEED, "draws": args.draws, "reps": args.reps, "models": list(MODELS),
        "arms": list(ARMS), "references": [ANNNET, S3C] + list(BENCHMARKS), "margin_bp": s3c_candidate.MARGIN_BP,
        "dating": json.loads(m1288.DATING.read_text(encoding="utf-8"))["available_time"],
        "windows": {}, "reading_rules": declaration["reading_rules"],
    }
    for window in WINDOWS:
        result["windows"][window] = run_window(window, panel, splits, registry, table, register, results, auctions, args)
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    Path(args.output).write_text(json.dumps(result, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    return 0


# -- the page ------------------------------------------------------------------------------------------------------------


def cell(row: Optional[dict]) -> str:
    return m1288.cell(row)


def _vs(group: Optional[Mapping[str, object]], metric: str, candidate: str, reference: str) -> Optional[dict]:
    return m1288._vs(group, metric, candidate, reference)


def reading(row: Optional[dict]) -> str:
    """`gain`, `loss`, `undecided`, `identical` or `n/a` on the mean-d bound."""

    if row is None:
        return "n/a"
    if row.get("identical"):
        return "identical"
    return m1288.words(row).strip("*").split(" ")[0]


def group_of(window: Mapping[str, object], split: str, label: str) -> Optional[dict]:
    return window["groups"].get(split, {}).get(label)


def mean_table(group: Mapping[str, object]) -> List[str]:
    out = ["| model | " + " | ".join(METRIC_TITLES[m] + " (mean)" for m in METRIC_NAMES) + " |", "|---|" + "---|" * len(METRIC_NAMES)]
    for m in MODELS:
        out.append(f"| {LABELS[m]} | " + " | ".join(
            f"{group[x]['means'][m]:.3f}" if x in ("grid_crps", "upper_tail_twcrps") else f"{group[x]['means'][m]:.4f}" for x in METRIC_NAMES) + " |")
    return out


def against_table(group: Mapping[str, object], candidate: str) -> List[str]:
    out = [f"| {SHORT[candidate]} against | " + " | ".join(METRIC_TITLES[m] for m in TESTED) + " |", "|---|" + "---|" * len(TESTED)]
    for ref in plan(candidate):
        out.append(f"| {SHORT[ref]} | " + " | ".join(cell(_vs(group, m, candidate, ref)) for m in TESTED) + " |")
    return out


def split_table(window: Mapping[str, object], split: str, candidate: str, reference: str, order: Optional[Sequence[str]] = None) -> List[str]:
    return m1288.split_table(window, split, candidate, reference, order)


def means_split_table(window: Mapping[str, object], split: str, metric: str, models: Sequence[str] = (S3C, ANNNET) + FORMS) -> List[str]:
    labels = window["groups"].get(split, {})
    out = [f"| {split.replace('_', ' ')} | days | " + " | ".join(SHORT[m] for m in models) + " |", "|---|---|" + "---|" * len(models)]
    for label in sorted(labels):
        g = labels[label]
        out.append(f"| {label} | {g['days']} | " + " | ".join(f"{g[metric]['means'][m]:.4f}" for m in models) + " |")
    return out if len(out) > 2 else []


def _iv(entry: Mapping[str, float], digits: int = 3) -> str:
    text = f"{entry['mean']:+.{digits}f}"
    if "interval" in entry:
        text += f" [{entry['interval'][0]:+.{digits}f}, {entry['interval'][1]:+.{digits}f}]"
    else:
        text += " (too few days)"
    return text


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
            shift = "n/a" if e["mean_abs_shift_bp_on_active_days"] is None else f"{e['mean_abs_shift_bp_on_active_days']:.3f}"
            share = " / ".join(f"{e[t]['share_in_fit']:.2f}" for t in terms)
            out.append(f"| h={lead} | {name} | {e['days']} | " + " | ".join(_iv(e[t]) for t in terms) + f" | {share} | {shift} |")
    return out


def coverage_table(block: Mapping[str, dict]) -> List[str]:
    out = ["| lead | bill settlement days with a cash management bill | flagged at the decision (declared reading) | flagged on the prior-day reading | "
           "flagged only through the decision day's own announcement | other days flagged |", "|---|---|---|---|---|---|"]
    for lead, e in block.items():
        out.append(f"| h={lead} | {e['cmb_days']} | {e['flagged']} | {e['flagged_prior_day']} | {e['flagged_only_same_day']} | {e['non_cmb_days_flagged']} |")
    return out


def answer(r: Mapping[str, object]) -> List[str]:
    """The plain answer to the directive's third item, from the tables only: for each form and for 2020 and March to June 2020 on grid CRPS and on
    upper-tail twCRPS, (s3c-ann-net)'s own reading against (s3c), the form's against (s3c) and against (s3c-ann-net); 'removes the loss' only if
    (s3c-ann-net) is read worse than (s3c) and the form is not (declaration, `answer`); and the readings elsewhere."""

    window = r["windows"]["development"]
    out = ["## The answer: does the arm remove the 2020 loss, and at what cost elsewhere?", "",
           "Read on the mean-d bound, development window, from the tables below. A form 'removes the loss' here only if (s3c-ann-net) is read worse than "
           "(s3c) in the group and the form is not; nothing else is claimed. These are days already seen.", "",
           "| group | metric | (s3c-ann-net) against (s3c) | " + " | ".join(f"{SHORT[f]} against (s3c)" for f in FORMS) + " | " +
           " | ".join(f"{SHORT[f]} against (s3c-ann-net)" for f in FORMS) + " | loss removed? |", "|---|---|---|" + "---|" * (2 * len(FORMS) + 1)]
    verdicts: Dict[str, Dict[str, str]] = {f: {} for f in FORMS}
    for label in (REGIME_2020, SPRING):
        g = group_of(window, "regime", label)
        for metric in ("grid_crps", "upper_tail_twcrps"):
            base = reading(_vs(g, metric, ANNNET, S3C))
            cells = []
            for f in FORMS:
                cells.append(reading(_vs(g, metric, f, S3C)))
            gone = []
            for f, got in zip(FORMS, cells):
                state = "n/a" if base == "n/a" else ("yes" if base == "loss" and got != "loss" else ("no" if base == "loss" else "no loss to remove"))
                verdicts[f][f"{label}/{metric}"] = state
                gone.append(f"{SHORT[f]}: {state}")
            out.append(f"| {label} | {METRIC_TITLES[metric]} | {cell(_vs(g, metric, ANNNET, S3C))} | " + " | ".join(
                cell(_vs(g, metric, f, S3C)) for f in FORMS) + " | " + " | ".join(cell(_vs(g, metric, f, ANNNET)) for f in FORMS) + " | " +
                "; ".join(gone) + " |")
    out += ["", "**Cost elsewhere (grid CRPS against (s3c-ann-net), the readings by regime):** "]
    parts = []
    for f in FORMS:
        regimes = window["groups"].get("regime", {})
        found = {label: reading(_vs(regimes[label], "grid_crps", f, ANNNET)) for label in sorted(regimes)}
        pooled = reading(_vs(window["groups"]["pooled"]["all decision days"], "grid_crps", f, ANNNET))
        parts.append(f"{SHORT[f]}: pooled {pooled}; " + ", ".join(f"{label} {word}" for label, word in found.items()))
    out[-1] += "; ".join(parts) + ". The leads and the settlement-day types are in the tables."
    out += ["", "**The 2026 development days** (decide nothing): grid CRPS against (s3c-ann-net), pooled: " + "; ".join(
        f"{SHORT[f]} {cell(_vs(r['windows']['2026']['groups']['pooled']['all decision days'], 'grid_crps', f, ANNNET))}" for f in FORMS) + "."
        if "2026" in r["windows"] else "", ""]
    return out


def summary(r: Mapping[str, object]) -> List[str]:
    out = ["## Summary: grid CRPS against (s3c-ann-net), by lead", "",
           "Skill and its 90% interval, the mean difference d and its studentized 90% interval, and the reading on the mean-d bound (positive favours "
           "the arm). The full tables, with the other metrics and references, follow.", ""]
    for window in WINDOWS:
        w = r["windows"].get(window)
        if w is None:
            continue
        out += [f"**{WINDOW_TITLES[window].split(' (')[0]}**", "", "| lead | " + " | ".join(SHORT[x] for x in ARMS) + " |", "|---|" + "---|" * len(ARMS)]
        for lead in LEADS:
            g = w["groups"]["lead"][f"h={lead}"]
            out.append(f"| h={lead} | " + " | ".join(cell(_vs(g, "grid_crps", x, ANNNET)) for x in ARMS) + " |")
        g = w["groups"]["pooled"]["all decision days"]
        out.append("| pooled over h = 1..5 | " + " | ".join(cell(_vs(g, "grid_crps", x, ANNNET)) for x in ARMS) + " |")
        out.append("")
    return out


def headline(r: Mapping[str, object]) -> str:
    parts = []
    for window, text in (("development", "On the development window"), ("2026", "on the 2026 development days")):
        entry = r["windows"].get(window, {}).get("groups", {}).get("pooled", {}).get("all decision days")
        parts.append(f"{text}, grid CRPS against (s3c-ann-net): " + "; ".join(f"{SHORT[f]} {cell(_vs(entry, 'grid_crps', f, ANNNET))}" for f in FORMS))
    return "; ".join(parts) + "."


def render(r: dict) -> str:
    out = [
        "# (s3c-ann-net-cmb): a separate cash management bill term on (s3c-ann-net), at the 18:00 decision (#1356)", "",
        "**Does giving the cash management bills a term of their own remove (s3c-ann-net)'s 2020 loss?** " + headline(r), "",
        "**Hypothesis and step:** H5 (primary goal), step 3, an arm on the candidate (s3c-ann-net); avenue #1306, her ruling of 2 November 2026 (chat, "
        "relayed on #1356). **Development data, not a verdict** (scoring protocol v1, #640). **(s3c-ann-net) stays the candidate of the avenue and "
        "(s3c) the H5 candidate; nothing here changes either.** Nothing is registered or published and no claim changes; adopting the arm is her decision. "
        "Generated by `scripts/s3c_ann_net_cmb_1356.py page` from `docs/research/s3c-ann-net-cmb-1356/result.json`, not edited by hand; declared in "
        f"`{r['declaration']}` before any score.", "",
        "**What changed.** At leads 2 to 5 the bill term of (s3c-ann-net) (the signed announced net bill settlement, USD 100 bn) is read net of the "
        "cash management bills, and the cash management bills get a term of their own, split out of the bill leg: the **flag form** is 1 when an "
        "announced cash management bill settles on the target day, the **net-size form** is what the announced cash management bills add to the bill "
        "net (USD 100 bn). The regular bill net and the size term add up to (s3c-ann-net)'s bill net at every instant, so the arm contains the "
        "candidate. At lead 1 each arm is (s3c-ann-net) exactly. Everything else is (s3)'s and (s3c-ann-net)'s, and the SRF cap is (s3c)'s; the fit is "
        "on direct pairs. The figures are read at the "
        f"{r['decision_time']} decision instant from the announcement ({r['dating']} New York time on the `announcemt_date`), so a bill announced "
        "after that instant is not read at that lead, whether or not it settles inside the lead window (finding #1301). The two **prior-day** arms count "
        "a cash management bill only if it was announced before the decision day; they are the sensitivity of each form to the unverified release time of "
        "an immediate-release announcement made on the decision day, and are tested against (s3c-ann-net) only.", "",
        "**Finding #1301 and Lens E's caveat apply.** Treasury's announcement files state no release time for 163 announcements ('for immediate "
        "release'), 153 of them cash management bills, so the 12:00 time of a cash management bill announced on the decision day is unverified. The "
        "coverage table says how many cash management bill days each reading sees.", "",
        f"Panel digest `{r['panel_sha256']}`. Studentized stationary bootstrap (ruling 1), mean block {sp.BLOCK_LENGTH} business days, "
        f"{r['draws']:,} draws, seed {r['seed']}, two-sided 90% interval (the lower end is the one-sided 95% bound). Positive mean d favours "
        "the model named first in a table's heading. **A reading (gain, loss, undecided) is taken from the mean-d bound** (her ruling on #1009), with the "
        "skill interval beside it; for a Brier score the skill is the Brier skill score. **Caveat (Lens C, #958):** the lag-10 HAC standard error that "
        "studentizes the bound is understated about 2x after 2020, so an interval that excludes zero is narrower than it should be. The intervals "
        "of a group of target days keep the **current method** (the group's days, scattered, resampled in date order as if consecutive), which #1221 "
        "questions and #1228 will decide; no reading of a day-type group is a finding. Where two models differ on few days of a group the bound may "
        "not be computed: the unstudentized interval of mean d is then given beside it, and no reading is taken from that. Groups of fewer than 20 "
        "days are listed with their means and not tested. The benchmarks B1, B1' and B2 are scored beside the forms in the pooled tables and in every "
        "split of the record.", "",
        "**What kind of look this is.** The 2026 days were already seen by #845, by the #151 final test, and by #1229, #1255, #1273, #1288 and #1321. "
        "This is a check on an arm queued by her ruling, not evidence for a verdict. The avenue's own risk stands: most of the cash management bill "
        "days are 2020's, so a split may only re-label a regime effect; the answer table below is read with that in mind.", ""]
    out += answer(r) + [""] + summary(r)
    for window in WINDOWS:
        w = r["windows"].get(window)
        if w is None:
            continue
        n, pooled = w["notes"], w["groups"]["pooled"]["all decision days"]
        ld = w["lead_difference"]
        out += [f"## {WINDOW_TITLES[window]}", "",
                f"Scored decision days: {n['scored_decision_days']:,} ({n['first']} to {n['last']}); {n['refits_ref']} refits of the reference walk, "
                f"{n['refits_main']} of the arms' walk and {n['refits_prior']} of the prior-day walk. Cells on which an arm is not (s3c-ann-net) "
                f"element for element, by lead (of {ld[FLAG]['cells_per_lead']:,} each): " + "; ".join(
                    f"{SHORT[m]}: " + ", ".join(f"h={h}: {ld[m]['differing_cells'][str(h)]:,}" for h in LEADS) for m in ARMS) + ".", "",
                "### Cash management bill settlement days each reading can see", ""] + coverage_table(w["cmb_coverage"]) + [
                "", "### Mean scores (pooled)", ""] + mean_table(pooled) + [""]
        for arm in (ANNNET,) + ARMS:
            out += [f"### {LABELS[arm]} against each reference (pooled)", ""] + against_table(pooled, arm) + [""]
        for split, title in (("lead", "By lead"), ("regime", "By regime (2020 and the two groups inside it)"),
                             ("pressure_day_type", "By pressure-day type of the target day"),
                             (DAY_TYPE, "By the settlement-day type of the target at each lead (bill settlement days with a cash management bill against the others)")):
            for arm, refs in ((ANNNET, (S3C,)), (FLAG, (ANNNET, S3C)), (SIZE, (ANNNET, S3C)), (FLAGP, (ANNNET,)), (SIZEP, (ANNNET,))):
                for ref in refs:
                    table = split_table(w, split, arm, ref)
                    if table:
                        out += [f"### {title}: {SHORT[arm]} against {SHORT[ref]}", ""] + table + [""]
        for split, title in (("regime", "regime"), ("pressure_day_type", "pressure-day type")):
            table = means_split_table(w, split, "b90_closed")
            if table:
                out += [f"### 90% band coverage by {title}", ""] + table + [""]
        out += ["### The fitted effect, by lead and regime of the target day", ""]
        for arm in EFFECT_ARMS:
            out += [f"{LABELS[arm]}:", ""] + effect_table(w["effects"][arm], EFFECT_TERMS[arm]) + [""]
        out += ["The effect is the standardised effect of the refit the forecast used times the scale at the anchor in bp. The pooled row is printed at every "
                "lead and the regime rows at h = 3 only (the record holds them all). The interval is a bootstrap interval of the mean over decision days, "
                "which share refits; it is not a sampling interval for the coefficient. A term enters a fit only when at least three training pairs carry it.", ""]
        if w["skipped_groups"]:
            out += ["Groups of fewer than 20 days, listed and not tested: " + ", ".join(f"{x} ({n_})" for x, n_ in sorted(w["skipped_groups"].items())) + ".", ""]
    out += question(r)
    return "\n".join(out).rstrip() + "\n"


def question(r: Optional[dict] = None) -> List[str]:
    return [
        "## Questions for Eleonora (marked; defaults change no claim)", "",
        "**Question 1. Does a form replace (s3c-ann-net) as the candidate of avenue #1318?** The candidate does not change in this directive. Whether a "
        "form should replace it rests on days already seen, split as above, and on the 2020 reading in particular.", "",
        "**Options** (the default applies if you have not answered by the next 5 pm batch):", "",
        "1. **(s3c-ann-net) stays the candidate and nothing changes** (default).",
        "2. **Draft a directive that tests the better form prospectively**, on the confirmation days only, under the scoring protocol.",
        "3. **Ask for a further arm** from the tables above, in a directive of its own.", "",
        "**Question 2. The release time of an immediate-release announcement (finding #1301).** The cash management bill term reads an announcement "
        "made on the decision day from 12:00; the prior-day arms do not. Verifying the release times is outside this directive.", "",
        "**Options** (the default applies if you have not answered by the next 5 pm batch):", "",
        "1. **Leave the dating as it is** (default). Nothing changes.",
        "2. **Ask for the release times of the immediate-release announcements to be checked** against another source, in a directive of its own.", ""]


def page(args) -> int:
    r = json.loads(Path(args.score).read_text(encoding="utf-8"))
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    Path(args.output).write_text(render(r), encoding="utf-8")
    return 0


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="command", required=True)
    s = sub.add_parser("score", help="walk (s3c-ann-net) and the arms, cap them as (s3c) is capped, and score on both windows")
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
