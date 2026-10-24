#!/usr/bin/env python3
"""The floor flag as a pool selector: B1's change pool, the mean-reversion residual pool and gbm_funding (#966; H5 step 3).

A development measurement, never a verdict: nothing here supports, kills or registers a candidate, publishes a figure or
moves a declaration (scoring protocol v1, #640; #46 top block). `metadata/floor_flag_966.json` is the declaration; this
script refuses to read it unless it is committed and unchanged. The arms are `repo_model.floor_flag` on the base model
`repo_model.spread_mean_reversion` (#686) and B1 (`repo_model.protocol_benchmarks`). They are scored with the scorer of
scoring protocol v1 (`repo_model.scoring_protocol`) against B1 and B2, arm (ii) also against its own pool
(`spread_mr_level10`), arms (iv) and (v) also against the scaled model (`spread_mr_fhs_mad20_f0.5`) and arm (iii) also
against `gbm_funding`. Scored decision days have their five targets on or before
2025-12-31; no later day is read (`docs/decisions/lockbox.md`).

Arms (i), (ii), (iv) and (v) run in the cloud in minutes: (iv) and (v) put the flag and the two-part rule on the best model,
#941's scaled mean reversion (`repo_model.spread_mr_fhs`, variant "mad window 20 floor 0.5"), as well as on B1 (Eleonora's
ruling of 22 October 2026). Arm (iii) and the reference rows of `gbm_funding` need `gbm_funding`'s walks, which take hours
(#46: not run in the cloud; Eleonora's ruling of 22 October 2026 skips the Mac run, so the committed record has no (iii) section). Build the published panel and the walks as the docstring of `scripts/spread_distribution_634.py`
says, then:

    PYTHONPATH=src python3 scripts/floor_flag_966.py score --panel PUB.csv --output OUT/floor_flag.json
    PYTHONPATH=src python3 scripts/floor_flag_966.py score --panel PUB.csv --walks OUT --output OUT/floor_flag.json
    python3 scripts/floor_flag_966.py report OUT/floor_flag.json
    python3 scripts/floor_flag_966.py check

`score` writes the record; `report` copies it to `docs/research/floor-flag-966/result.json` and writes the page
`docs/research/floor-flag-966-result.md` from it; `check` fails when the page is not what the record gives. With `--walks`
the record carries the (iii) section; without, the page says arm (iii) was not run.
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


def _load(name: str):
    spec = importlib.util.spec_from_file_location(name, REPO / "scripts" / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


from repo_model import floor_flag as ff  # noqa: E402
from repo_model import protocol_benchmarks as pb, scoring_protocol as sp  # noqa: E402
from repo_model import spread_mr_fhs as fhs  # noqa: E402
from repo_model.baseline import panel_sha256  # noqa: E402
from repo_model.data import load_daily_panel  # noqa: E402
from repo_model.evaluation_splits import load_split_declaration  # noqa: E402
from repo_model.policy_events import load_register  # noqa: E402
from repo_model.splits import SplitError  # noqa: E402

s686 = _load("spread_mean_reversion_686")
s761 = _load("spread_mr_variants_761")

DECLARATION = REPO / "metadata" / "floor_flag_966.json"
RESEARCH = REPO / "docs" / "research"
RECORD = RESEARCH / "floor-flag-966" / "result.json"
PAGE = RESEARCH / "floor-flag-966-result.md"
SEED = 966
LAST_DAY = s686.LAST_DAY
DECISION_TIME = s686.DECISION_TIME
MIN_GROUP_DAYS = s686.MIN_GROUP_DAYS
WINDOW_2024 = date(2024, 1, 1)
WINDOW_2021 = date(2021, 1, 1)
BASE = ff.BASE_MR
GBM, FLAG_GBM = "gbm_funding", "flag_gbm"
#: #941's variant "mad window 20 floor 0.5": the best model, the base of arms (iv) and (v) (the amendment of 22 October 2026).
FHS_VARIANT = fhs.VARIANTS[0]
FHS = ff.FHS_NAME
assert FHS_VARIANT.name == FHS
METRICS = (("grid_crps", sp.grid_crps), ("upper_tail_twcrps", sp.upper_tail_twcrps))
LABELS = {"B1": "B1", "B2": "B2", BASE: "mean reversion (#686; arm (ii)'s own pool)", ff.ARM_B1: "(i) flag-restricted B1",
          ff.ARM_MR: "(ii) flag-restricted mean reversion", GBM: "gbm_funding (#634; a reference)",
          FLAG_GBM: "(iii) gbm_funding, two-part (a reference arm)",
          FHS: "scaled mean reversion (#941, mad window 20 floor 0.5; arms (iv) and (v)'s own pool)",
          ff.ARM_FHS: "(iv) flag-restricted scaled mean reversion", ff.ARM_TWO_FHS: "(v) scaled mean reversion, two-part"}
#: Candidate -> the extra references it is also paired against, where the section holds them.
EXTRA_REFERENCE = {ff.ARM_MR: (BASE,), FLAG_GBM: (GBM,), FHS: (GBM,), ff.ARM_FHS: (FHS, GBM), ff.ARM_TWO_FHS: (FHS, GBM)}
FLAG_LABEL = {True: "on", False: "off", None: "undefined"}
paired_row, run_pairs, skill_text, diff_text, pct, excludes_zero = (
    s761.paired_row, s761.run_pairs, s761.skill_text, s761.diff_text, s761.pct, s761.excludes_zero)


def window_label(day: date) -> str:
    if day >= WINDOW_2024:
        return "2024-26"
    return "2021-23" if day >= WINDOW_2021 else "before 2021"


def on_windows(panel, row_flags) -> List[Tuple[str, str]]:
    """The runs of consecutive rows on which the flag is on, as (first, last) dates."""

    out, start = [], None
    for i, state in enumerate(row_flags):
        if state and start is None:
            start = panel[i].date
        if not state and start is not None:
            out.append((start.isoformat(), panel[i - 1].date.isoformat()))
            start = None
    if start is not None:
        out.append((start.isoformat(), panel[-1].date.isoformat()))
    return out


def make_frame(panel, splits, registry, declaration, days, forecasts):
    frame = s686.Frame(panel, splits, registry, declaration)
    frame.days, frame.forecasts = list(days), forecasts
    return frame


def build_base(panel, splits, registry, declaration, row_flags):
    """The decision days with B1, B2, mean reversion and arms (i) and (ii), whose five targets are scored days."""

    frame = s686.Frame(panel, splits, registry, declaration)
    candidate_days = [
        day for i, day in enumerate(frame.dates)
        if i + max(sp.HORIZONS) < len(panel) and frame.dates[i + max(sp.HORIZONS)] <= LAST_DAY
    ]
    s686.require_scored_days(candidate_days, LAST_DAY)
    # the flag is as-of at every row the pools and the anchors read, before any forecast is used
    last_anchor = pb._anchor(panel, frame.position[candidate_days[-1]], registry, DECISION_TIME)
    ff.check_no_future(panel, row_flags, load_register(), DECISION_TIME, indices=range(last_anchor + 1))
    walk = ff.walk(panel, candidate_days, row_flags, registry=registry, decision_time=DECISION_TIME, splits=splits,
                   variant=FHS_VARIANT)
    b1, b2, dropped = {}, {}, []
    for day in walk.forecasts[BASE]:
        index = frame.position[day]
        try:
            b1[day] = pb.b1_forecast(panel, index, registry=registry, decision_time=DECISION_TIME)
            b2[day] = pb.b2_forecast(panel, index, registry=registry, decision_time=DECISION_TIME, splits=splits)
        except (sp.ProtocolError, SplitError):
            dropped.append(day)
    days = [day for day in walk.forecasts[BASE] if day in b1]
    forecasts = {"B1": b1, "B2": b2, **{name: {d: walk.forecasts[name][d] for d in days}
                                         for name in (BASE, ff.ARM_B1, ff.ARM_MR, FHS, ff.ARM_FHS, ff.ARM_TWO_FHS)}}
    flag_of = {d: FLAG_LABEL[walk.anchor_flag[d]] for d in days}
    notes = {
        "decision_days_offered": len(candidate_days), "candidate_skipped_for_history": len(walk.skipped),
        "benchmark_missing": [d.isoformat() for d in dropped], "scored_decision_days": len(days),
        "first": days[0].isoformat(), "last": days[-1].isoformat(),
        "last_target": frame.target(days[-1], max(sp.HORIZONS)).isoformat(), "refits": len(walk.fits),
        "own_pool_share": {
            f"{FLAG_LABEL[state]}": [sum(1 for fit in walk.fits.values() if state in fit.own_pool[h]) for h in sp.HORIZONS]
            for state in (True, False)},
        "refit_count": len(walk.fits),
        "scaled_own_pool_share": {
            f"{FLAG_LABEL[state]}": [sum(1 for fit in walk.scaled_fits.values() if state in fit.own_pool[h]) for h in sp.HORIZONS]
            for state in (True, False)},
    }
    return make_frame(panel, splits, registry, declaration, days, forecasts), notes, flag_of, b1


def build_walks(frame, base_frame, flag_of, b1, walks_dir: Path, row_flags, panel):
    """Section (iii): `gbm_funding` and its two-part wrapper on the days its walks cover."""

    sd = _load("spread_distribution_634")
    calendar = frame.dates
    laws, covered = sd.lead_forecasts(sd.load_laws(walks_dir, GBM), calendar)
    days = [d for d in covered if d in b1 and d in base_frame.forecasts["B2"] and calendar[frame.position[d] + 5] <= LAST_DAY]
    filled = sp.fill_missing({d: laws[d] for d in days}, {d: b1[d] for d in days}, days)
    gbm = {d: filled.forecasts[d] for d in days}
    anchors = {d: row_flags[pb._anchor(panel, frame.position[d], frame.registry, DECISION_TIME)] for d in days}
    flagged = {d: ff.two_part(gbm[d], b1[d], anchors[d]) for d in days}
    forecasts = {"B1": {d: b1[d] for d in days}, "B2": {d: base_frame.forecasts["B2"][d] for d in days}, GBM: gbm, FLAG_GBM: flagged,
                 **{name: {d: base_frame.forecasts[name][d] for d in days} for name in (FHS, ff.ARM_FHS, ff.ARM_TWO_FHS)}}
    notes = {"walk_days": len(days), "first": days[0].isoformat(), "last": days[-1].isoformat(),
             "missing_days": len(filled.missing_days), "missing_share": filled.missing_share,
             "flag_on_days": sum(1 for d in days if anchors[d]), "flag_state_days": {FLAG_LABEL[s]: sum(1 for d in days if anchors[d] == s) for s in (True, False, None)}}
    return make_frame(panel, frame.splits, frame.registry, frame.declaration, days, forecasts), notes, {d: FLAG_LABEL[anchors[d]] for d in days}


# -- the groups and the tests ----------------------------------------------------------------------------------------

_SERIES: Dict = {}


def _task(job):
    key, metric, candidate, members = job
    series = _SERIES[(key[0], metric)]
    names = ["B1", "B2"] + [r for r in EXTRA_REFERENCE.get(candidate, ()) if r in series]
    return job[:3], run_pairs({n: series[n] for n in names}, series[candidate], list(members), seed=SEED, draws=_SERIES["draws"])


def section(frame, flag_of, models, candidates, draws: int, workers: int) -> dict:
    """Every group's paired tests of `candidates` against B1, B2 and their extra reference, and the group means."""

    days = frame.days
    cells = {(metric, m): s686.cell_scores(frame, m, fn) for metric, fn in METRICS for m in models}
    for metric, fn in METRICS:
        for m in models:
            official = sp.day_scores(frame.forecasts[m], frame.outcome, frame.dates, score=fn)
            mine = s686.by_decision(cells[(metric, m)])
            if set(official) != set(mine) or any(abs(official[d] - mine[d]) > 1e-9 for d in mine):
                raise SystemExit(f"{metric} of {m}: the cell means differ from scoring_protocol.day_scores")
    targets = sorted({frame.target(d, h) for d in days for h in sp.HORIZONS})
    labelled = {
        "regime": ("target", {t: frame.regime(t) for t in targets}),
        "window": ("target", {t: window_label(t) for t in targets}),
        "pressure_day_type": ("target", {t: frame.day_type(t) for t in targets}),
        "flag_state": ("decision", {d: flag_of[d] for d in days}),
    }
    groups: Dict[Tuple[str, str], Tuple[str, Sequence[date]]] = {("pooled", "all decision days"): ("decision", list(days))}
    for h in sp.HORIZONS:
        groups[("lead", f"h = {h}")] = (f"lead{h}", list(days))
    for split, (grain, labels) in labelled.items():
        by_label: Dict[str, List[date]] = {}
        for day in sorted(labels):
            by_label.setdefault(labels[day], []).append(day)
        for label, members in by_label.items():
            groups[(split, label)] = (grain, members)
    series: Dict = {}
    for metric, _ in METRICS:
        series[("decision", metric)] = {m: s686.by_decision(cells[(metric, m)]) for m in models}
        series[("target", metric)] = {m: s686.by_target(frame, cells[(metric, m)]) for m in models}
        for h in sp.HORIZONS:
            series[(f"lead{h}", metric)] = {m: s686.by_lead(cells[(metric, m)], h) for m in models}
    jobs, skipped = [], {}
    for (split, label), (grain, members) in groups.items():
        if len(members) < MIN_GROUP_DAYS:
            skipped[f"{split}/{label}"] = len(members)
            continue
        for metric, _ in METRICS:
            for candidate in candidates:
                jobs.append(((grain, f"{split}/{label}"), metric, candidate, tuple(members)))
    _SERIES.clear()
    _SERIES.update({(k[0], metric): series[(k[0], metric)] for k, metric, _, _ in jobs})
    _SERIES["draws"] = draws
    context = multiprocessing.get_context("fork")
    with context.Pool(workers) as pool:
        out = pool.map(_task, [((k[0], k[1]), m, c, mem) for k, m, c, mem in jobs], chunksize=1)
    result: Dict = {"groups": {}, "skipped_groups": skipped, "days": len(days)}
    for ((grain, name), metric, candidate), rows in out:
        split, label = name.split("/", 1)
        members = list(groups[(split, label)][1])
        entry = result["groups"].setdefault(split, {}).setdefault(label, {"days": len(members)})
        ser = series[(grain, metric)]
        cell = entry.setdefault(metric, {"means": {m: sum(ser[m][d] for d in members) / len(members) for m in models}, "vs": {}})
        cell["vs"][candidate] = rows
    return result


def score(args) -> int:
    declaration = s686.committed_declaration(DECLARATION)
    panel_path = Path(args.panel)
    panel = load_daily_panel(panel_path)
    splits = load_split_declaration(s686.SPLITS)
    registry = json.loads(s686.SOURCES.read_text(encoding="utf-8"))
    row_flags = ff.flags(panel, load_register(), DECISION_TIME)
    frame, notes, flag_of, b1 = build_base(panel, splits, registry, declaration, row_flags)
    days = frame.days
    on_share = {}
    for regime in splits.regime_labels:
        members = [d for d in days if frame.regime(d) == regime]
        if not members:
            continue
        on_share[regime] = {"days": len(members), **{FLAG_LABEL[s]: sum(1 for d in members if flag_of[d] == FLAG_LABEL[s]) for s in (True, False, None)}}
    result: dict = {
        "issue": 966, "declaration": str(DECLARATION.relative_to(REPO)), "panel_sha256": panel_sha256(panel_path),
        "label": "development, not a verdict", "seed": SEED, "draws": args.draws, "notes": notes,
        "flag": {"windows": on_windows(panel, row_flags), "anchor_state_by_regime": on_share,
                 "rows_on": sum(1 for s in row_flags if s), "rows_off": sum(1 for s in row_flags if s is False),
                 "rows_undefined": sum(1 for s in row_flags if s is None)},
    }
    scaled = (FHS, ff.ARM_FHS, ff.ARM_TWO_FHS)
    models = ("B1", "B2", BASE, ff.ARM_B1, ff.ARM_MR) + scaled
    result["main"] = section(frame, flag_of, models, (BASE, ff.ARM_B1, ff.ARM_MR) + scaled, args.draws, args.workers)
    if args.walks:
        wframe, wnotes, wflag = build_walks(frame, frame, flag_of, b1, Path(args.walks), row_flags, panel)
        result["walks_notes"] = wnotes
        result["walks"] = section(wframe, wflag, ("B1", "B2", GBM, FLAG_GBM) + scaled, (GBM, FLAG_GBM) + scaled, args.draws, args.workers)
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    Path(args.output).write_text(json.dumps(result, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    return 0


# -- the page --------------------------------------------------------------------------------------------------------


def kill_ii(record) -> Optional[dict]:
    group = record["main"]["groups"].get("window", {}).get("2024-26")
    if group is None:
        return None
    row = group["grid_crps"]["vs"][ff.ARM_MR][BASE]
    if "undefined" in row:
        return {"row": row, "killed": None}
    lo, hi = row["skill_interval"]
    return {"row": row, "killed": lo <= 0.0}


def kill_iv(record) -> Optional[dict]:
    group = record["main"]["groups"].get("window", {}).get("2024-26")
    if group is None:
        return None
    row = group["grid_crps"]["vs"][ff.ARM_FHS][FHS]
    if "undefined" in row:
        return {"row": row, "killed": None}
    lo, hi = row["skill_interval"]
    return {"row": row, "killed": lo <= 0.0}


def kill_v(record) -> Optional[dict]:
    row = record["main"]["groups"]["pooled"]["all decision days"]["grid_crps"]["vs"][ff.ARM_TWO_FHS][FHS]
    if "undefined" in row:
        return {"row": row, "killed": None}
    return {"row": row, "killed": row["skill_interval"][1] < 0.0}


def kill_iii(record) -> Optional[dict]:
    if "walks" not in record:
        return None
    row = record["walks"]["groups"]["pooled"]["all decision days"]["grid_crps"]["vs"][FLAG_GBM][GBM]
    if "undefined" in row:
        return {"row": row, "killed": None}
    return {"row": row, "killed": row["skill_interval"][1] < 0.0}


def _table(cell: dict, order: Sequence[str], benchmarks: Sequence[str]) -> List[str]:
    order = [m for m in order if m in cell["means"]]
    benchmarks = [b for b in benchmarks if b in cell["means"]]
    heads = " | ".join(f"vs {LABELS[b]}" for b in benchmarks)
    out = [f"| | mean bp | {heads} |", "|---|---|" + "---|" * len(benchmarks)]
    for m in order:
        vs = cell["vs"].get(m, {})
        cols = " | ".join(skill_text(vs[b]) if b in vs else "" for b in benchmarks)
        out.append(f"| {LABELS[m]} | {cell['means'][m]:.3f} | {cols} |")
    return out


def _sections(title, sec, order, benchmarks, splits):
    out = []
    for metric, name in (("grid_crps", "grid CRPS"), ("upper_tail_twcrps", "upper-tail twCRPS")):
        pooled = sec["groups"]["pooled"]["all decision days"][metric]
        out += [f"### {title}: {name}, pooled ({sec['days']:,} decision days), skill [90%]", ""]
        out += _table(pooled, order, benchmarks) + [""]
        for split, split_name in splits:
            groups = sec["groups"].get(split, {})
            if not groups:
                continue
            out += [f"#### {name} by {split_name}", ""]
            for label in sorted(groups):
                out += [f"**{label}** ({groups[label]['days']} days)", ""] + _table(groups[label][metric], order, benchmarks) + [""]
    if sec["skipped_groups"]:
        out += ["Groups with fewer than %d days are listed and not tested: %s." % (
            MIN_GROUP_DAYS, ", ".join(f"{k} ({v})" for k, v in sorted(sec["skipped_groups"].items()))), ""]
    return out


def render(record: dict) -> str:
    n, flag = record["notes"], record["flag"]
    k2, k3, k4, k5 = kill_ii(record), kill_iii(record), kill_iv(record), kill_v(record)
    SPLITS = (("lead", "lead"), ("regime", "regime (target day)"), ("window", "window (target day)"),
              ("pressure_day_type", "pressure-day type (target day)"), ("flag_state", "flag state at the anchor"))
    out = [
        "# The floor flag as a pool selector (#966, H5 step 3)", "",
        "**Hypothesis and step:** H5 (primary goal), step 3 (2021-23 and the residual pools). **Development data only: this is not a "
        "verdict** (scoring protocol v1, #640) and nothing here is registered or published. Every figure is read from "
        "`docs/research/floor-flag-966/result.json` by `scripts/floor_flag_966.py report`; the declaration is "
        f"`{record['declaration']}`, committed before any score. Studentized stationary bootstrap (ruling 1), mean block "
        f"{sp.BLOCK_LENGTH} business days, {record['draws']:,} draws, seed {record['seed']}; the interval is a two-sided 90% interval. "
        "Skill is `mean(d) / mean(S(benchmark))` with `d = S(benchmark) - S(candidate)`: positive favours the candidate. "
        f"Panel digest `{record['panel_sha256'][:8]}…`.", "",
        "**Calendar first:** no calendar or scheduled column is trained or read as an input here (the flag is a trailing SOFR-to-floor median), "
        "so the figures are provisional under the calendar-first rule as #941's are; the classification is Eleonora's (the pull request asks).", "",
        "## The flag", "",
        f"On from rows: {flag['rows_on']:,}; off {flag['rows_off']:,}; undefined {flag['rows_undefined']:,}. The runs of consecutive rows "
        "with the flag on: " + "; ".join(f"{a} to {b}" for a, b in flag["windows"]) + ". (Lens B read it on from 2021-04-21 to 2023-12-11 and "
        "from 2024-02-14 to 2024-07-09.)", "",
        "| regime (decision day) | days | flag on | off | undefined |", "|---|---|---|---|---|"]
    for regime, c in flag["anchor_state_by_regime"].items():
        out.append(f"| {regime} | {c['days']} | {c['on']} | {c['off']} | {c['undefined']} |")
    out += ["", "## Kill rules, as declared", ""]
    if k2 is None:
        out.append("- (ii): not evaluated (no 2024-26 group).")
    elif k2["killed"] is None:
        out.append("- (ii) against its own pool on the 2024-26 days: undefined (%s)." % k2["row"]["undefined"])
    else:
        out.append(f"- (ii) against its own pool (mean reversion) on the 2024-26 days: grid CRPS skill {skill_text(k2['row'])}. "
                   + ("**Kill rule met**: the interval covers 0 or lies below it." if k2["killed"] else "Kill rule not met: the interval lies above 0."))
    if k3 is None:
        out.append("- (iii) against `gbm_funding`: **not run**, by Eleonora's ruling of 22 October 2026 on #966 "
                   "(comment 6350221714): the Mac run of `gbm_funding`'s walks is skipped. Kill rule (iii) is not evaluated.")
    elif k3["killed"] is None:
        out.append("- (iii) against `gbm_funding` pooled: undefined (%s)." % k3["row"]["undefined"])
    else:
        out.append(f"- (iii) against `gbm_funding` pooled: grid CRPS skill {skill_text(k3['row'])}. "
                   + ("**Kill rule met**: the upper bound is below 0." if k3["killed"] else "Kill rule not met."))
    if k4 is None:
        out.append("- (iv): not evaluated (no 2024-26 group).")
    elif k4["killed"] is None:
        out.append("- (iv) against its own pool (the scaled mean reversion) on the 2024-26 days: undefined (%s)." % k4["row"]["undefined"])
    else:
        out.append(f"- (iv) against its own pool (the scaled mean reversion, #941) on the 2024-26 days: grid CRPS skill {skill_text(k4['row'])}. "
                   + ("**Kill rule (iv) met**: the interval covers 0 or lies below it." if k4["killed"] else "Kill rule (iv) not met: the interval lies above 0."))
    if k5["killed"] is None:
        out.append("- (v) against the scaled mean reversion pooled: undefined (%s)." % k5["row"]["undefined"])
    else:
        out.append(f"- (v) the two-part rule on the scaled mean reversion, against the scaled mean reversion pooled: grid CRPS skill {skill_text(k5['row'])}. "
                   + ("**Kill rule (v) met**: the upper bound is below 0." if k5["killed"] else "Kill rule (v) not met."))
    out += ["", "A kill is a statement about development days; it neither supports nor kills H5 (the declaration's `kill.reading`).", "",
            "## Arms (iv) and (v): the flag on the best model (#941's scaled mean reversion)", "",
            "Added on Eleonora's ruling of 22 October 2026 (declaration amended before any score of these arms). (iv) restricts the "
            "scaled model's standardised residual pool to the training pairs whose origin has the anchor's flag; (v) is B1 while the flag is on "
            "and the scaled model otherwise. Their own pool and the model they are compared with is the scaled model, `spread_mr_fhs_mad20_f0.5`.", "",
            f"{n['scored_decision_days']:,} decision days, {n['first']} to {n['last']} (the last target is {n['last_target']}). Refits whose own flag "
            f"pool was used for the scaled arm (not the whole-lead fallback), by lead 1 to 5: flag on {n['scaled_own_pool_share']['on']}, "
            f"flag off {n['scaled_own_pool_share']['off']}.", ""]
    out += _sections("Arms (iv) and (v)", record["main"], (FHS, ff.ARM_FHS, ff.ARM_TWO_FHS, "B1", "B2"), ("B1", "B2", FHS), SPLITS)
    out += ["## Arms (i) and (ii)", "",
            f"{n['scored_decision_days']:,} decision days, {n['first']} to {n['last']} (the last target is {n['last_target']}). Mean reversion has no "
            f"forecast on {n['candidate_skipped_for_history']} early days (history), a benchmark is missing on {len(n['benchmark_missing'])}. "
            f"The fit is renewed {n['refits']} times (every 21 decision days). Refits whose own flag pool was used (not the whole-lead fallback), "
            f"by lead 1 to 5: flag on {n['own_pool_share']['on']}, flag off {n['own_pool_share']['off']}.", ""]
    out += _sections("Arms (i) and (ii)", record["main"], (BASE, ff.ARM_B1, ff.ARM_MR, "B1", "B2"), ("B1", "B2", BASE), SPLITS)
    out += ["## Arm (iii)", ""]
    if "walks" not in record:
        out += ["Not run in this record, by Eleonora's ruling of 22 October 2026 on #966 (comment 6350221714, relayed by the "
                "orchestrating session): the Mac run of `gbm_funding`'s walks, which would have scored arm (iii) and the `gbm_funding` "
                "reference rows, is skipped. Nothing is claimed about arm (iii) or those rows.", ""]
    else:
        w = record["walks_notes"]
        out += [f"{w['walk_days']:,} decision days covered by `gbm_funding`'s walks ({w['first']} to {w['last']}); its missing forecasts "
                f"({w['missing_days']} decision days, share {w['missing_share']:.3f}) are filled by B1 as the protocol does. Flag on at "
                f"the anchor on {w['flag_on_days']} of them.", ""]
        out += _sections("Arm (iii) and the reference", record["walks"], (GBM, FLAG_GBM, FHS, ff.ARM_FHS, ff.ARM_TWO_FHS, "B1", "B2"),
                         ("B1", "B2", GBM, FHS), SPLITS)
    out += ["## Variant count", "", "Five arms on one flag (three declared first, (iv) and (v) added on 22 October 2026); no new fit beyond #686's and #941's own refits.", "",
            "## Not checked, or for Eleonora", "",
            "- The flag and its three arms were chosen after the author saw 2018-2025 (Lens B's replication is on the same days), so every figure is "
            "exploration. Whether any arm joins #634's candidates, and the flag's threshold (1 bp) and windows (60 and 40 rows), are hers.",
            "- Calendar first: arms (i), (ii), (iv) and (v) are pool selectors on B1, #686 and #941, none of which reads a calendar column at the target day, "
            "so every figure is provisional under the calendar-first rule as #941's are. Whether that classification stands, and whether a calendar-reading "
            "base is re-run, is hers (the pull request asks); no re-run is asked here.",
            "- The outcome is the panel's `spread_bps`, not the first-published vintage of protocol section 11.",
            "- Lens B's crude replication used its own exact CRPS on B1's change pool; the figures here use the protocol's grid scorer and are not "
            "expected to match it.", ""]
    return "\n".join(out)


def report_command(args) -> int:
    record = json.loads(args.record.read_text(encoding="utf-8"))
    RECORD.parent.mkdir(parents=True, exist_ok=True)
    RECORD.write_text(json.dumps(record, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    PAGE.write_text(render(record), encoding="utf-8")
    print("wrote", PAGE)
    return 0


def check_command(_args) -> int:
    record = json.loads(RECORD.read_text(encoding="utf-8"))
    if not PAGE.exists() or PAGE.read_text(encoding="utf-8") != render(record):
        print("the page is not what the record gives; run `report`", file=sys.stderr)
        return 1
    print("ok")
    return 0


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="command", required=True)
    run = sub.add_parser("score")
    run.add_argument("--panel", type=Path, required=True)
    run.add_argument("--walks", type=Path, default=None)
    run.add_argument("--output", type=Path, required=True)
    run.add_argument("--draws", type=int, default=sp.DRAWS)
    run.add_argument("--workers", type=int, default=4)
    run.set_defaults(func=score)
    rep = sub.add_parser("report")
    rep.add_argument("record", type=Path)
    rep.set_defaults(func=report_command)
    sub.add_parser("check").set_defaults(func=check_command)
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
