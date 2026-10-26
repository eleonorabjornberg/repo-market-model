"""The signed announced IORB change and a technical-adjustment indicator on (s3), scored (#1227; H5 step 3, avenue #1214).

A development study, never a verdict. It writes JSON and Markdown to the paths it is given and nothing into `docs/runs/`. Every
choice is in `metadata/s3_iorbs_1227.json`, which this script refuses to read unless it is committed and unchanged. The arm is
`repo_model.spread_mr_state_calendar.S3_IORBS`: (s3) of #1145 (#941's scaled mean reversion with calendar terms in standardised units,
a Huber fit, ridge 5), with the `iorb_window` flag and, beside it, the signed `iorb_announced_change_bps` of the window (over 25 bp)
and a technical-adjustment indicator (`setup_diagnostic.is_technical`). Both new terms are read from the target row and the two rows
after a change, at the leads the flag reads (1 to 3), on direct pairs. The arm is scored with the scorer of scoring protocol v1
(`repo_model.scoring_protocol`) against (s3), (a), B1, B1' (#960) and B2, with the studentized stationary bootstrap of ruling 1 (read
on the bound on mean d, her #1009 ruling, with the skill interval beside). Scored decision days are those whose five targets are on or
before 2025-12-31; no later day is read and no locked day is scored (`docs/decisions/lockbox.md`). Nothing here is a verdict (scoring
protocol v1, #640). `gbm_funding`, the calibration of the q95 and the bands and the Politis-White block are not part of this study
(the declaration's `not_scored`).

It reuses the helpers of `scripts/calendar_mr_1115.py` and `scripts/s3_terms_1196.py` (the frame, the cells, the groups, the readings).
The arms read no scarcity state, so none is built. The walks take minutes; the paired tests are the long part (well under two hours on
4 cores), so the run is a cloud run. Commands, from a clone of the branch:

    PYTHONPATH=src python3 -m repo_model.cli build --raw-root tests/fixtures/snapshots/funding_inputs \\
        --output PUB.csv --build-cutoff 2026-09-08T21:31:42+00:00 --decision-time 16:00:00
    PYTHONPATH=src python3 -m repo_model.cli verify-panel PUB.csv --manifest metadata/funding_panel_manifest.json
    PYTHONPATH=src python3 scripts/s3_iorbs_1227.py score --panel PUB.csv --output docs/research/s3-iorbs-1227/result.json
    PYTHONPATH=src python3 scripts/s3_iorbs_1227.py page \\
        --score docs/research/s3-iorbs-1227/result.json --output docs/research/s3-iorbs-1227-result.md

The run is scored under the day types and the B2 record in force (a run with `--legacy-day-types` reads the earlier ones, as every
study script that walks B2 does since #1206); the declared run omits the flag.

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


def _load(name: str):
    spec = importlib.util.spec_from_file_location(name, REPO / "scripts" / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


from repo_model import announced_iorb, b1_calendar as b1c  # noqa: E402
from repo_model import protocol_benchmarks as pb, scoring_protocol as sp  # noqa: E402
from repo_model import spread_mr_calendar as cal, spread_mr_state_calendar as sc  # noqa: E402
from repo_model.baseline import panel_sha256  # noqa: E402
from repo_model.data import load_daily_panel  # noqa: E402
from repo_model.evaluation_splits import load_split_declaration  # noqa: E402
from repo_model.splits import SplitError  # noqa: E402

c = _load("calendar_mr_1115")
s686, s761 = c.s686, c.s761
t1196 = _load("s3_terms_1196")

DECLARATION = REPO / "metadata" / "s3_iorbs_1227.json"
SEED = 1227
LAST_DAY = c.LAST_DAY
DECISION_TIME = c.DECISION_TIME
MIN_GROUP_DAYS = c.MIN_GROUP_DAYS
B1P = c.B1P
A = sc.ARM_A
S3 = sc.ARMS[2].name
S3I = sc.S3_IORBS.name
#: The arms scored against the references, (a) first.
ARMS = (A, S3, S3I)
BENCHMARKS = ("B1", B1P, "B2")
MODELS = BENCHMARKS + ARMS
METRIC_NAMES = c.METRIC_NAMES
REGIMES = c.REGIMES
DAY_TYPES = c.DAY_TYPES
ORDINARY = c.ORDINARY
MEDIAN = c.MEDIAN
#: The terms of the arm that concern the IORB, in the order the page lists them.
IORB_TERMS = ("iorb_window",) + sc.IORB_EXTRAS
#: The target-day type the ruling names.
IORB_DAY = "iorb_window"

verdict = t1196.verdict
skill_verdict = t1196.skill_verdict
reading_words = t1196.reading_words
tally = t1196.tally
_bold = t1196._bold
_fmt = t1196._fmt


def committed_declaration(path: Path = DECLARATION) -> dict:
    """The declaration, refused unless it is committed and unchanged since `HEAD`."""

    return s686.committed_declaration(path)


# -- the frame -------------------------------------------------------------------------------------------------------


def build_frame(panel, splits, registry, table, iorb, first: Optional[date] = None):
    """The decision days with a forecast of every model, whose five targets are scored days.

    `first` starts the walk later than the declared study does; it exists for the test of this script, and the declared run never
    passes it.
    """

    frame = s686.Frame(panel, splits, registry, None)
    candidate_days = [
        day for i, day in enumerate(frame.dates)
        if i + max(sp.HORIZONS) < len(panel) and frame.dates[i + max(sp.HORIZONS)] <= LAST_DAY and (first is None or day >= first)
    ]
    s686.require_scored_days(candidate_days, LAST_DAY)
    settings = dict(registry=registry, decision_time=DECISION_TIME, splits=splits)
    b1, b1p, b2, dropped = {}, {}, {}, []
    for day in candidate_days:
        index = frame.position[day]
        try:
            one = pb.b1_forecast(panel, index, registry=registry, decision_time=DECISION_TIME)
            prime = b1c.b1_calendar_forecast(panel, index, **settings)
            two = pb.b2_forecast(panel, index, **settings)
        except (sp.ProtocolError, SplitError):
            dropped.append(day)
            continue
        b1[day], b1p[day], b2[day] = one, prime, two
    # no arm reads the scarcity state: the empty map reads as "unknown", which no arm uses
    mine = sc.walk(panel, candidate_days, table, {}, sc.S3_IORBS_ARMS, **settings, iorb=iorb)
    days = [d for d in candidate_days if d in b1 and all(d in mine.forecasts[a] for a in ARMS)]
    frame.days = days
    frame.forecasts = {"B1": b1, B1P: b1p, "B2": b2, **{a: mine.forecasts[a] for a in ARMS}}
    for name in list(frame.forecasts):
        frame.forecasts[name] = {d: frame.forecasts[name][d] for d in days}
    notes = {
        "decision_days_offered": len(candidate_days), "candidate_skipped_for_history": len(mine.skipped),
        "benchmark_missing": [d.isoformat() for d in dropped], "scored_decision_days": len(days),
        "first": days[0].isoformat(), "last": days[-1].isoformat(),
        "last_target": frame.target(days[-1], max(sp.HORIZONS)).isoformat(), "refits": len(mine.fits),
    }
    return frame, notes, mine


# -- the tests, in parallel ------------------------------------------------------------------------------------------

_STATE: Dict = {}


def pair_plan(candidate: str) -> List[str]:
    """What a candidate is tested against: B1, B1' and B2, (a) for every arm but (a), and (s3) for the arm that adds to it."""

    names = list(BENCHMARKS)
    if candidate != A:
        names.append(A)
    if candidate == S3I:
        names.append(S3)
    return names


def _pairs_task(job):
    split, label, grain, metric, candidate, members = job
    series = _STATE["series"][(grain, metric)]
    out: Dict[str, dict] = {}
    for name in pair_plan(candidate):
        days = list(members)
        if len(days) < MIN_GROUP_DAYS:
            continue
        out[name] = s761.run_pairs({name: series[name]}, series[candidate], days, seed=SEED, draws=_STATE["draws"],
                                  mean_d_fallback=True)[name]
    return (split, label, metric, candidate), out


def run_jobs(jobs, workers: int):
    with multiprocessing.get_context("fork").Pool(workers) as pool:
        return pool.map(_pairs_task, jobs, chunksize=1)


# -- the counts and the window days -----------------------------------------------------------------------------------


def iorb_counts(announcements, iorb: sc.IorbTable, panel, splits) -> dict:
    """The IORB changes of the announcement table: how many, how many technical, by regime of the day they take effect (through the
    last scored day), and how many the column shows a decision. A change is not in the column when it takes effect after the last
    scored day, or when its note was announced after the decision instant of the panel day before it (the Sunday cut of 2020-03-16)."""

    changes = [a for a in announcements if a.kind == "change"]
    out: dict = {
        "changes": len(changes), "technical": sum(1 for a in changes if sc.technical(a.change_bps)),
        "technical_dates": [a.effective.isoformat() for a in changes if sc.technical(a.change_bps)],
        "by_regime": {}, "after_last_scored_day": [], "announced_after_the_decision": [], "in_column": 0, "technical_in_column": 0,
    }
    shown = {panel[i].date for i, value in enumerate(iorb.changes) if value != 0.0}
    for a in changes:
        if a.effective > LAST_DAY:
            out["after_last_scored_day"].append(a.effective.isoformat())
            continue
        entry = out["by_regime"].setdefault(splits.regime(a.effective), {"changes": 0, "technical": 0})
        entry["changes"] += 1
        entry["technical"] += int(sc.technical(a.change_bps))
        if a.effective in shown:
            out["in_column"] += 1
            out["technical_in_column"] += int(sc.technical(a.change_bps))
        else:
            out["announced_after_the_decision"].append(a.effective.isoformat())
    return out


def window_days(frame, table: cal.TermTable, iorb: sc.IorbTable, mine: sc.Walk) -> dict:
    """For each IORB-window target day (the flag at lead 1), the kind of change it carries and, for the arm, the shift the three IORB
    terms added in bp (the mean over the leads that forecast the day and can read the window), the signed change in bp, and what
    (s3) missed (the outcome less its median)."""

    out: Dict[str, dict] = {}
    for d in frame.days:
        used = mine.fit_used[d]
        detail = mine.detail[d]
        for h in sp.HORIZONS:
            day = frame.target(d, h)
            row = frame.position[day]
            if not table.flag(IORB_DAY, h, row):
                continue
            x = iorb.at(h, row)
            estimate = mine.estimates[used][S3I][h]
            shift = {name: estimate.effect.get(name, 0.0) * (1.0 if name == "iorb_window" else x.get(name, 0.0)) for name in IORB_TERMS}
            cell = out.setdefault(day.isoformat(), {"leads": 0, "total": 0.0, "miss": 0.0, "signed_bp": 0.0, "technical": 0.0,
                                                    **{name: 0.0 for name in IORB_TERMS}})
            cell["leads"] += 1
            for name in IORB_TERMS:
                cell[name] += detail["scale"] * shift[name]
            cell["total"] += detail["scale"] * sum(shift.values())
            cell["miss"] += frame.outcome[day] - frame.forecasts[S3][d][h][MEDIAN]
            cell["signed_bp"] += x.get(sc.IORB_SIGNED, 0.0) * sc.IORB_UNIT_BPS
            cell["technical"] += x.get(sc.IORB_TECHNICAL, 0.0)
    final = {}
    for day, cell in sorted(out.items()):
        n = cell["leads"]
        final[day] = {k: (v / n if k != "leads" else v) for k, v in cell.items()}
        final[day]["kind"] = "technical" if final[day]["technical"] > 0.0 else "ordinary change"
    return final


def window_groups(frame, days: dict, series: Mapping[str, Mapping[str, Mapping[date, float]]]) -> dict:
    """By regime and kind of change (technical or not): the days, the mean change and the mean score of (a), (s3) and the arm, and
    the mean shift the arm's IORB terms added. Listed, not tested."""

    out: dict = {}
    for kind in ("technical", "ordinary change", "all"):
        for regime in list(REGIMES) + ["all"]:
            members = [date.fromisoformat(d) for d, cell in days.items()
                       if (kind == "all" or cell["kind"] == kind) and (regime == "all" or frame.regime(date.fromisoformat(d)) == regime)]
            if not members:
                continue
            entry = {"days": len(members), "signed_bp": sum(days[m.isoformat()]["signed_bp"] for m in members) / len(members),
                     "shift_bp": sum(days[m.isoformat()]["total"] for m in members) / len(members),
                     "miss_bp": sum(days[m.isoformat()]["miss"] for m in members) / len(members)}
            for metric in METRIC_NAMES:
                entry[metric] = {a: sum(series[metric][a][m] for m in members) / len(members) for a in ARMS}
            out.setdefault(kind, {})[regime] = entry
    return out


def entering(mine: sc.Walk) -> dict:
    """Per IORB term and lead: the refits in which the term entered the fit and the mean coefficient over them (scale units)."""

    out: dict = {}
    for term in IORB_TERMS:
        per_lead = {}
        for h in sp.HORIZONS:
            values = [est[S3I][h].effect[term] for est in mine.estimates.values() if term in est[S3I][h].effect]
            per_lead[str(h)] = {"refits_entered": len(values), "mean_coefficient": sum(values) / len(values) if values else None,
                                "refits": len(mine.estimates)}
        out[term] = per_lead
    return out


# -- the score -------------------------------------------------------------------------------------------------------


def score(args) -> int:
    declaration = committed_declaration()
    panel_path = Path(args.panel)
    panel = load_daily_panel(panel_path)
    splits = load_split_declaration(c.SPLITS)
    registry = json.loads(c.SOURCES.read_text(encoding="utf-8"))
    announcements = announced_iorb.load_announcements(c.IORB_TABLE)
    table = cal.TermTable(panel, announcements, decision_time=DECISION_TIME)
    iorb = sc.IorbTable(panel, announcements, decision_time=DECISION_TIME)
    frame, notes, mine = build_frame(panel, splits, registry, table, iorb, args.first)
    published_sha = panel_sha256(panel_path)
    days = frame.days
    labels = c.day_labels(frame, table)

    cells = {m: c.cell_table(frame, frame.forecasts[m]) for m in MODELS}
    for m in MODELS:
        official = sp.day_scores(frame.forecasts[m], frame.outcome, frame.dates, score=sp.grid_crps)
        mean = s686.by_decision(cells[m]["grid_crps"])
        if set(official) != set(mean) or any(abs(official[d] - mean[d]) > 1e-9 for d in mean):
            raise SystemExit(f"grid CRPS of {m}: the cell means differ from scoring_protocol.day_scores")

    groups = c.groups_of(frame, labels)
    series: Dict[Tuple[str, str], Dict[str, Dict[date, float]]] = {}
    for _s, _l, grain, _m in groups:
        for metric in METRIC_NAMES:
            if (grain, metric) not in series:
                series[(grain, metric)] = {m: c.series_of(frame, cells[m][metric], grain) for m in MODELS}
    _STATE.update(series=series, draws=args.draws)

    jobs, skipped = [], {}
    for split, label, grain, members in groups:
        if len(members) < MIN_GROUP_DAYS:
            skipped[f"{split}/{label}"] = len(members)
            continue
        for metric in METRIC_NAMES:
            for candidate in ARMS:
                jobs.append((split, label, grain, metric, candidate, tuple(members)))
    done = run_jobs(jobs, args.workers)

    by_key = {(s_, l_): (g, m) for s_, l_, g, m in groups}
    result: dict = {
        "issue": 1227, "declaration": str(DECLARATION.relative_to(REPO)), "panel_sha256": published_sha,
        "subset_from": None if args.first is None else args.first.isoformat(), "label": "development, not a verdict",
        "seed": SEED, "draws": args.draws, "notes": notes, "models": list(MODELS),
        "arms": [{"name": a.name, "role": a.role, "location": list(a.location), "extra": list(a.extra), "robust": a.robust,
                  "ridge": sc.ridge_of(a)} for a in sc.S3_IORBS_ARMS],
        "refits": [{"fitted_on": day.isoformat(), "phi": fit.phi} for day, fit in sorted(mine.fits.items())],
        "groups": {}, "skipped_groups": skipped, "reading_rules": declaration["reading_rules"],
    }
    for ident, payload in done:
        split, label, metric, candidate = ident
        entry = result["groups"].setdefault(split, {}).setdefault(label, {"days": len(by_key[(split, label)][1])})
        entry.setdefault(metric, {"means": {}, "vs": {}})["vs"][candidate] = payload
    for split, labels_ in result["groups"].items():
        for label, entry in labels_.items():
            grain, members = by_key[(split, label)]
            for metric in METRIC_NAMES:
                if metric in entry:
                    ser = series[(grain, metric)]
                    entry[metric]["means"] = {m: sum(ser[m][d] for d in members) / len(members) for m in MODELS}
    result["iorb"] = iorb_counts(announcements, iorb, panel, splits)
    result["window_days"] = window_days(frame, table, iorb, mine)
    target_series = {metric: series[("target", metric)] for metric in METRIC_NAMES}
    result["window_groups"] = window_groups(frame, result["window_days"], target_series)
    result["entering"] = entering(mine)
    result["refit_total"] = len(mine.estimates)
    result["day_type_counts"] = {k: sum(1 for x in labels if k in labels[x]) for k in DAY_TYPES + (ORDINARY,)}
    passes = [est[S3I][h].iterations for est in mine.estimates.values() for h in sp.HORIZONS]
    result["robust_fit"] = {"fits": len(passes), "capped": sum(1 for x in passes if x >= sc.MAX_ITERATIONS),
                            "cap": sc.MAX_ITERATIONS, "mean_passes": sum(passes) / len(passes)}
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    Path(args.output).write_text(json.dumps(result, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    return 0


# -- the page --------------------------------------------------------------------------------------------------------

LABELS = {"B1": "B1", B1P: "B1' (#960)", "B2": "B2", A: "(a) base: #941 mad 20, floor 0.5",
          S3: "(s3) (s1) with a Huber fit and a heavier ridge; the H5 candidate", S3I: sc.S3_IORBS.role}
METRIC_TITLES = {"grid_crps": "grid CRPS (23 levels)", "upper_tail_twcrps": "upper-tail twCRPS (weight 1{z > 0 bp})"}


def model_table(cell: dict) -> List[str]:
    """Mean score of every model in one group, and each arm's skill over B1, B1', B2, (a) and (s3), each with the mean-d bound beside it."""

    out = ["| | mean | skill vs B1 [90%]; mean d (bp) [90%] | vs B1' | vs B2 | vs (a) | vs (s3) |", "|---|---|---|---|---|---|---|"]
    means = cell["means"]
    for name in BENCHMARKS:
        if name in means:
            out.append(f"| {LABELS[name]} | {means[name]:.3f} |" + " |" * 5)
    for name in ARMS:
        vs = cell["vs"].get(name, {})
        cells = ([_fmt(vs.get(b)) for b in ("B1", B1P, "B2")] + ["" if name == A else _fmt(vs.get(A))]
                 + ["" if name in (A, S3) else _fmt(vs.get(S3))])
        out.append(f"| {LABELS[name]} | {means[name]:.3f} | " + " | ".join(cells) + " |")
    return out


def _group(r: dict, split: str, label: str) -> Optional[dict]:
    return r["groups"].get(split, {}).get(label)


def _vs(r: dict, split: str, label: str, metric: str, reference: str) -> Optional[dict]:
    entry = _group(r, split, label)
    return None if entry is None else entry[metric]["vs"].get(S3I, {}).get(reference)


def render(r: dict) -> str:
    n, counts = r["notes"], r["iorb"]
    pooled = r["groups"]["pooled"]["all decision days"]
    tech_regimes = {k: v["technical"] for k, v in counts["by_regime"].items() if v["technical"]}
    out = [
        "# The signed announced IORB change and a technical-adjustment indicator on (s3) (#1227)", "",
        "**Hypothesis and step:** H5 (primary goal), step 3 (fix), avenue #1214. **Development data, not a verdict** (scoring protocol v1, "
        f"#640): days to {n['last_target']}, no lockbox day. Nothing is adopted and no claim changes. Generated by "
        f"`scripts/s3_iorbs_1227.py page` from `docs/research/s3-iorbs-1227/result.json`, not edited by hand; declared in "
        f"`{r['declaration']}` before any number.", "",
        f"**The count is small.** There are {counts['changes']} IORB changes in the announcement table, {counts['technical']} of them "
        "technical (not a multiple of 25 bp, by `setup_diagnostic.is_technical`), "
        + ("and the technical ones fall in " + ", ".join(f"{k} ({v})" for k, v in sorted(tech_regimes.items())) if tech_regimes else "")
        + f". Of the {counts['changes']}, " + (f"{len(counts['after_last_scored_day'])} takes effect after the last scored day "
                                              f"({', '.join(counts['after_last_scored_day'])}) and " if counts["after_last_scored_day"] else "")
        + f"{counts['in_column']} are in the column the model reads (a note is in it only if it was announced before the decision instant "
        "of the panel day before it takes effect)"
        + (f"; {', '.join(counts['announced_after_the_decision'])} was announced after that instant (the Sunday cut of 2020-03-16 was "
           "announced after the Friday decision) and no decision sees it" if counts["announced_after_the_decision"] else "")
        + ". The technical indicator rests on a handful of days; its estimated effect is read with that in mind.", "",
        "**What kind of look this is.** A further look at 2018-2025 after (s3) was chosen on the same days. The arm is one declared variant "
        "and **counts toward the variant count**. A gain here is evidence for a question, with the selection noted, not a result.", "",
        f"Panel digest `{r['panel_sha256'][:8]}…`. Studentized stationary bootstrap (ruling 1), mean block {sp.BLOCK_LENGTH} business days, "
        f"{r['draws']:,} draws, seed {r['seed']}, two-sided 90% interval (the lower end is the one-sided 95% bound). Skill is "
        "`mean(d) / mean(S(benchmark))` with `d = S(benchmark) - S(candidate)`, positive favours the candidate. **Every row shows the skill "
        "interval and, beside it, the studentized interval on mean d (bp); a reading (gain, loss, undecided) is taken from the mean-d bound** "
        "(her ruling on #1009, 20 October 2026), not from the skill interval. **Caveat (Lens C, #958):** the lag-10 HAC standard error that "
        "studentizes the bound is understated about 2x after 2020, so an interval that excludes zero is narrower than it should be; a "
        "reading here is evidence for a question. Where the benchmark scores zero on a resample, skill is undefined but the mean-d bound is "
        "still computed (#1215): the row shows \"skill undefined\" and is read on the bound. A row with no mean-d bound reads \"no reading\" "
        f"with the reason, not \"undecided\". Scored decision days: {n['scored_decision_days']:,} ({n['first']} to {n['last']}); the fit is "
        f"renewed {n['refits']} times. B1' (Lens C's calendar-aware persistence, #960) is reported beside B1 in every table; B1 and B2 stay "
        "the protocol's benchmarks.", "",
        "**The arm.** (s3) of #1145 is #941's scaled mean reversion (a) with calendar terms in standardised units, a Huber fit and a ridge of "
        "5 pseudo-days. **(s3+IORBs)** is (s3) with the `iorb_window` flag (the day an IORB change takes effect and the two panel days after "
        "it) and, beside it, two terms read from the same rows: `iorb_signed`, the signed announced change over 25 bp (a 25 bp cut is -1), "
        "and `iorb_technical`, 1 where the change is a technical adjustment. Same Huber fit, same ridge of 5, no `fomc_day` term, no state. "
        "The terms are scheduled fields of the target row, read on direct pairs where `asof` rule 2 admits them: at leads 1 to 3, absent at "
        "leads 4 and 5, exactly as the flag. A term enters a lead's fit only if at least 3 of its training pairs are non-zero. The benchmarks "
        "and the mean-reversion level read the pressure-day types of the month-end turn record in force since #1161, as #1196's page does. "
        "`gbm_funding`, the calibration of the q95 and the bands, and the Politis-White block are not part of this study.", "",
        "## Does the arm beat (s3)?", "",
        "Pooled and by split, the skill of (s3+IORBs) over (a) and over (s3), each with its 90% interval and, after the semicolon, mean d (bp) "
        "with its 90% interval; the reading is taken on the mean-d bound. Replacing (s3) is Eleonora's decision.", "",
        "| split | days | grid CRPS vs (a) | grid CRPS vs (s3) | twCRPS vs (a) | twCRPS vs (s3) |", "|---|---|---|---|---|---|"]
    rows = [("pooled", "all decision days")] + [("regime", l) for l in REGIMES] + [
        ("target_day_type", l) for l in (IORB_DAY, "fomc_day", ORDINARY, "calendar_days")]
    for split, label in rows:
        entry = _group(r, split, label)
        if entry is None:
            continue
        cells = [f"{_fmt(_vs(r, split, label, m, ref))}: {_bold(reading_words(_vs(r, split, label, m, ref)))}"
                 for m in METRIC_NAMES for ref in (A, S3)]
        out.append(f"| {label} | {entry['days']} | " + " | ".join(cells) + " |")
    out.append("")
    t = tally(r, S3I, S3)
    tw = tally(r, S3I, S3, "upper_tail_twcrps")
    out += [f"Against (s3), by regime on the mean-d bound: grid CRPS {t['gain']} gain / {t['loss']} loss / {t['undecided']} undecided"
            + (f" / {t['no reading']} no reading" if t["no reading"] else "") + f"; upper-tail twCRPS {tw['gain']} / {tw['loss']} / {tw['undecided']}"
            + (f" / {tw['no reading']} no reading" if tw["no reading"] else "") + ".", ""]
    wg = r["window_groups"]
    out += ["## The IORB-window rows", "",
            "The IORB-window target days (the day of a change and the two panel days after it) are the days the new terms act on. Their count by "
            "regime and by the kind of change they carry, with the mean score of (a), (s3) and the arm, the mean signed change, the mean "
            "shift the arm's three IORB terms added (bp, the mean over the leads that forecast the day and can read the window) and what (s3) "
            "missed (the outcome less its median). **These small groups are listed, not tested.**", ""]
    for metric in METRIC_NAMES:
        out += [f"{METRIC_TITLES[metric]} (bp):", "",
                "| kind of change | regime | days | mean change (bp) | shift added (bp) | (s3) missed (bp) | (a) | (s3) | (s3+IORBs) |",
                "|---|---|---|---|---|---|---|---|---|"]
        for kind in ("technical", "ordinary change", "all"):
            for regime in list(REGIMES) + ["all"]:
                e = wg.get(kind, {}).get(regime)
                if e is not None:
                    out.append(f"| {kind} | {regime} | {e['days']} | {e['signed_bp']:+.1f} | {e['shift_bp']:+.3f} | {e['miss_bp']:+.3f} | "
                               f"{e[metric][A]:.3f} | {e[metric][S3]:.3f} | {e[metric][S3I]:.3f} |")
        out.append("")
    iw = _group(r, "target_day_type", IORB_DAY)
    if iw is not None:
        for metric in METRIC_NAMES:
            out += [f"**{IORB_DAY}** ({iw['days']} days), {METRIC_TITLES[metric]}:", ""] + model_table(iw[metric]) + [""]
    out += ["## What the fit estimated", "",
            "Per IORB term and lead, the number of refits (of %d) in which the term entered the fit and the mean coefficient over those refits, "
            "in scale units (`iorb_signed` per 25 bp of change; a negative coefficient on the signed change means a hike lowers the spread "
            "by more than the flag alone, as the mechanical shift of an administered-rate change does). The term is absent at leads 4 and 5." % r["refit_total"], "",
            "| term | " + " | ".join(f"h={h}" for h in sp.HORIZONS) + " |", "|---|" + "---|" * len(sp.HORIZONS)]
    for term in IORB_TERMS:
        cells = []
        for h in sp.HORIZONS:
            e = r["entering"][term][str(h)]
            cells.append("n/a" if e["mean_coefficient"] is None else f"{e['mean_coefficient']:+.3f} ({e['refits_entered']})")
        out.append(f"| {term} | " + " | ".join(cells) + " |")
    out += ["", "The Huber fit took %.1f iterations on average and reached its cap (`MAX_ITERATIONS` = %d) in %d of %d fits (refit by lead)." % (
        r["robust_fit"]["mean_passes"], r["robust_fit"]["cap"], r["robust_fit"]["capped"], r["robust_fit"]["fits"]), ""]
    for split, title in (("pooled", "Pooled"), ("lead", "By lead")):
        for label, entry in r["groups"].get(split, {}).items():
            for metric in METRIC_NAMES:
                out += [f"## {title}: {label}, {METRIC_TITLES[metric]}, mean over leads 1 to 5 (bp)" if split == "pooled"
                        else f"### {label}, {METRIC_TITLES[metric]}", ""] + model_table(entry[metric]) + [""]
    for split, title, order in (("regime", "regime (target day)", REGIMES),
                                ("target_day_type", "target-day type (the groups overlap; FOMC and IORB days named)",
                                 list(DAY_TYPES) + [ORDINARY, "calendar_days"])):
        for metric in METRIC_NAMES:
            out += [f"## {METRIC_TITLES[metric]} by {title}", ""]
            for label in order:
                entry = r["groups"].get(split, {}).get(label)
                if entry is None:
                    continue
                out += [f"**{label}** ({entry['days']} days)", ""] + model_table(entry[metric]) + [""]
    if r["skipped_groups"]:
        out += ["Groups with fewer than %d days are listed and not tested: %s." % (
            MIN_GROUP_DAYS, ", ".join(f"{k} ({v})" for k, v in sorted(r["skipped_groups"].items()))), ""]
    out += ["## Reading under the declared rules (the mean-d bound, with the skill interval's reading beside it)", ""]
    for reference in (A, S3):
        for metric in METRIC_NAMES:
            parts = []
            for split in ("pooled", "regime", "target_day_type"):
                for label, entry in r["groups"].get(split, {}).items():
                    parts.append(f"{label}: {reading_words(entry[metric]['vs'].get(S3I, {}).get(reference))}")
            out.append(f"- **(s3+IORBs)** against {'(a)' if reference == A else '(s3)'}, {METRIC_TITLES[metric]}: " + "; ".join(parts) + ".")
    out.append("")
    out += ["## What this is not", "",
            "Development data from 2018 to 2025, split by regime and target-day type, never a verdict. The arm reads the calendar at the target "
            "day on direct pairs, so its class is not provisional (`docs/research/provisional-calendar-register.md`), but the choices (the ridge "
            "of 5 and Huber's threshold of (s3), the unit of 25 bp for the signed change) are not tuned here and are open to Eleonora's review. "
            "#941's variant was itself chosen after seeing 2018-2025, and (s3) was chosen on the same days. 'The signed change at the target "
            "day' is read as the change over the rows of the window the flag reads (so it has the flag's availability at every lead); the "
            "narrower reading, the target row alone, would be readable at lead 1 only and was not tried. The IORB-window days are few and the "
            "technical changes fewer, so the per-kind groups are listed, not tested, and the intervals on the window rows are wide.", ""]
    out += question(r)
    return "\n".join(out) + "\n"


def question(r: dict) -> List[str]:
    """The closing question for Eleonora (adoption is hers: the arm replaces (s3) only if it beats it)."""

    groups = r["groups"]
    cols = [("pooled", "all decision days", "pooled")] + [("regime", l, l) for l in REGIMES if l in groups.get("regime", {})] + [
        ("target_day_type", l, l) for l in [ORDINARY, "calendar_days", "fomc_day", IORB_DAY] if l in groups.get("target_day_type", {})]
    out = ["## Question for Eleonora: does the arm replace (s3) as the H5 candidate?", "",
           "Adoption is yours, on this page's evidence. **Nothing is adopted here and no claim changes.** The tables give the mean score of (a), "
           "(s3) and the arm, pooled, by regime and by ordinary, calendar, FOMC and IORB-window days (lower is better; B1, B1' and B2 are in "
           "the tables above). The `gbm_funding` comparison was not part of this study.", ""]
    for metric, title in (("grid_crps", "Grid CRPS (bp)"), ("upper_tail_twcrps", "Upper-tail twCRPS (bp)")):
        out += [f"**{title}**", "", "| | " + " | ".join(col[2] for col in cols) + " |", "|---|" + "---|" * len(cols)]
        for m in ARMS:
            cells = []
            for split, label, _name in cols:
                entry = groups.get(split, {}).get(label)
                cells.append("n/a" if entry is None or m not in entry[metric]["means"] else f"{entry[metric]['means'][m]:.3f}")
            out.append(f"| {LABELS[m]} | " + " | ".join(cells) + " |")
        out.append("")
    out += ["**Options** (numbered; the default applies if you have not answered by the next 5 pm batch):", "",
            "1. **Keep (s3) as the H5 candidate** (default). Nothing changes; the arm stays a development result.",
            "2. **Replace (s3) with (s3+IORBs)**, on the evidence above. That is a decision for you and would be followed by a registration "
            "discussion; this page does not pre-empt it.",
            "3. **Ask for a further step** before deciding (for example the narrower reading of the signed change, the target row alone, or "
            "the arm on the 2026 development days).", ""]
    return out


def page(args) -> int:
    r = json.loads(Path(args.score).read_text(encoding="utf-8"))
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    Path(args.output).write_text(render(r), encoding="utf-8")
    return 0


from repo_model import turn_days  # noqa: E402


@turn_days.with_legacy_flag
def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="command", required=True)
    s = sub.add_parser("score", help="walk the arm and score it")
    s.add_argument("--panel", required=True)
    s.add_argument("--output", required=True)
    s.add_argument("--draws", type=int, default=sp.DRAWS)
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
