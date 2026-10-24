"""(s3) of #1145 against `gbm_funding`, paired on the same days, from the walks on Eleonora's Mac (#1197; H5 step 3, development tier).

A development study, never a verdict (scoring protocol v1, #640). The H5 candidate is (s3) of #1145, #941's scaled mean reversion with
state-scaled calendar terms (standardised units, Huber fit, ridge 5). #1115 compared #941's variant (a) with `gbm_funding` (+6.8%
pooled [+3.3%, +10.1%]); #1145, #1153, #1172 and #1175 all skipped `gbm_funding`, because its walks live only on her Mac. This script
reads those walks, read-only, and scores (s3), (a) and `gbm_funding` on the decision days the walks cover, with B1 and B1' (#960)
beside them. It never rebuilds a walk: a rebuild on another machine does not reproduce the figures the walks were made with (#1169).

Every choice that is not here is in `metadata/state_calendar_1145.json`, which this script refuses to read unless it is committed and
unchanged: the arms, the terms, the state, the last scored day (2025-12-31; no later day is read, no locked day is scored,
`docs/decisions/lockbox.md`). The forecasts of (a) and (s3) are those of `scripts/state_calendar_1145.py` (`build_frame`), whose
helpers this script reuses; the walks are read by `calendar_mr_1115.load_gbm`, which refuses a partly present set of leads and a walk
made from another published panel.

What it scores: grid CRPS averaged over h = 1-5 and upper-tail twCRPS (scoring protocol v1), the studentized stationary bootstrap of
ruling 1 with mean block 10 (Politis-White beside it, pooled and by regime), the paired comparisons (s3) against `gbm_funding`, (a)
against `gbm_funding` and (s3) against (a), and each of the three against B1 and B1'. Pooled, by regime (by target day), by lead and
by target-day type. Every paired row carries the skill interval and the interval on mean d, and is read on the studentized bound on
mean d (Eleonora's ruling on #1009), with Lens C's caveat on the page. The q95 exceedance (both hit rules) and the 50% and 90% band
coverage (closed and open) are reported for each model, pooled and by regime. Not done: the pressure-day type split (as the #1145
page, only the target-day type), the scaled score of #967, B2 and `spread_mr_ctx` as references.

Commands, from a clone of the branch (the Mac paste is `scripts/mac_score_1197.sh`):

    PYTHONPATH=src python3 -m repo_model.cli build --raw-root tests/fixtures/snapshots/funding_inputs \\
        --output PUB.csv --build-cutoff 2026-09-08T21:31:42+00:00 --decision-time 16:00:00
    PYTHONPATH=src python3 -m repo_model.cli verify-panel PUB.csv --manifest metadata/funding_panel_manifest.json
    PYTHONPATH=src python3 scripts/s3_vs_gbm_1197.py check-walks ~/rmm-1027/WALKS
    PYTHONPATH=src python3 scripts/s3_vs_gbm_1197.py score --panel PUB.csv --walks ~/rmm-1027/WALKS \\
        --output docs/research/s3-vs-gbm-1197/result.json
    PYTHONPATH=src python3 scripts/s3_vs_gbm_1197.py page \\
        --score docs/research/s3-vs-gbm-1197/result.json --output docs/research/s3-vs-gbm-1197-result.md
    PYTHONPATH=src python3 scripts/s3_vs_gbm_1197.py log \\
        --score docs/research/s3-vs-gbm-1197/result.json --output docs/research/log/<date>-model-01197-H5-step3.md --date <date>

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


from repo_model import announced_iorb, metrics  # noqa: E402
from repo_model import scoring_protocol as sp  # noqa: E402
from repo_model import spread_mr_calendar as cal  # noqa: E402
from repo_model.baseline import panel_sha256  # noqa: E402
from repo_model.data import load_daily_panel  # noqa: E402
from repo_model.evaluation_splits import load_split_declaration  # noqa: E402

d1145 = _load("state_calendar_1145")
mdr = _load("mean_d_reading_1167")
c, s761, b949 = d1145.c, d1145.s761, d1145.b949

SEED = 1197
LAST_DAY = d1145.LAST_DAY
MIN_GROUP_DAYS = d1145.MIN_GROUP_DAYS
GBM = d1145.GBM
A, S3, B1P = d1145.A, d1145.S3, d1145.B1P
RATES = d1145.RATES
METRICS = d1145.METRIC_NAMES
REGIMES, DAY_TYPES, ORDINARY = d1145.REGIMES, d1145.DAY_TYPES, d1145.ORDINARY
MODELS = ("B1", B1P, A, S3)  # the models walked here; GBM is added from the walks
SCORED = MODELS + (GBM,)
#: The comparisons of the directive, in the order the page gives them: the candidate first, then what it is tested against.
HEADLINE: List[Tuple[str, str]] = [(S3, GBM), (A, GBM), (S3, A)]
COMPARISONS: List[Tuple[str, str]] = HEADLINE + [(m, b) for m in (S3, A, GBM) for b in ("B1", B1P)]
LABELS = {"B1": "B1", B1P: "B1' (#960)", A: "(a) #941", S3: "(s3) #1145", GBM: "gbm_funding (#634)"}
METRIC_TITLES = {"grid_crps": "grid CRPS, h = 1-5 (bp)", "upper_tail_twcrps": "upper-tail twCRPS (bp)"}
DECLARATION = d1145.DECLARATION
reading, skill_reading = mdr.verdict_words, mdr.skill_words


# -- the walks -------------------------------------------------------------------------------------------------------


def require_walks(walks: Path) -> Path:
    """The directory of `gbm_funding` walks, or a stop with a message that names what is missing. It never rebuilds a walk.

    Raises:
        SystemExit: the directory does not exist, or a lead's file is missing.
    """

    if not walks.is_dir():
        raise SystemExit(f"STOP: the walks directory {walks} does not exist; this script never rebuilds the walks "
                         "(a rebuild on another machine does not reproduce the figures they were made with).")
    missing = [f"{GBM}_h{h}.json" for h in sp.HORIZONS if not (walks / f"{GBM}_h{h}.json").is_file()]
    if missing:
        raise SystemExit(f"STOP: {walks} lacks {', '.join(missing)}; walk every lead or none, and this script never rebuilds a walk.")
    return walks


def common_days(days: Sequence[date], walked: Mapping[date, object]) -> List[date]:
    """The decision days both the model walks and the `gbm_funding` walks cover, in order: a paired test needs the same days."""

    return [d for d in days if d in walked]


# -- the tests, in parallel ------------------------------------------------------------------------------------------

_STATE: Dict = {}


def _references(candidate: str) -> List[str]:
    return [ref for cand, ref in COMPARISONS if cand == candidate]


def _pairs_task(job):
    split, label, grain, metric, candidate, members = job
    series = _STATE["series"][(grain, metric)]
    refs = {r: series[r] for r in _references(candidate)}
    return (split, label, metric, candidate), s761.run_pairs(refs, series[candidate], list(members), seed=SEED, draws=_STATE["draws"])


def _block_task(job):
    """The Politis-White block of the paired loss differential of a headline comparison, and the pooled test at that block."""

    split, label, grain, metric, candidate, reference, members = job
    series = _STATE["series"][(grain, metric)]
    ordered = sorted(members)
    d = [series[reference][x] - series[candidate][x] for x in ordered]
    key = (split, label, metric, f"{candidate}|{reference}")
    try:
        block = b949.politis_white(d)
    except ValueError:
        return key, None
    entry = {"block": block, "days": len(ordered)}
    if split == "pooled":
        at = max(1, round(block))
        test = sp.paired_tests([({x: series[reference][x] for x in ordered}, {x: series[candidate][x] for x in ordered})], seed=SEED,
                               draws=_STATE["draws"], block_length=float(at))[0]
        entry["at_block"] = at
        entry["row"] = s761.paired_row(test)
    return key, entry


def _interval_task(job):
    key, values, block = job
    n = len(values)
    low, high = metrics.stationary_bootstrap_interval(
        lambda idx: sum(values[i] for i in idx) / len(idx), n, block_length=block, seed=SEED, replications=_STATE["reps"])
    return key, [low, high]


def _dispatch(job):
    kind, payload = job
    return kind, {"pairs": _pairs_task, "block": _block_task, "interval": _interval_task}[kind](payload)


def run_jobs(jobs, workers: int):
    with multiprocessing.get_context("fork").Pool(workers) as pool:
        return pool.map(_dispatch, jobs, chunksize=1)


# -- the score -------------------------------------------------------------------------------------------------------


def score(args) -> int:
    declaration = d1145.committed_declaration()
    walks = require_walks(Path(args.walks))
    panel_path = Path(args.panel)
    panel = load_daily_panel(panel_path)
    splits = load_split_declaration(c.SPLITS)
    registry = json.loads(c.SOURCES.read_text(encoding="utf-8"))
    table = cal.TermTable(panel, announced_iorb.load_announcements(c.IORB_TABLE), decision_time=d1145.DECISION_TIME)
    states = d1145.decision_states(c.SOURCES)
    frame, notes, mine = d1145.build_frame(panel, splits, registry, table, states, args.first)
    published_sha = panel_sha256(panel_path)
    gbm = c.load_gbm(walks, published_sha, frame, GBM)
    if not gbm:
        raise SystemExit(f"STOP: {walks} holds no {GBM} walk that covers a scored decision day")
    offered = list(frame.days)
    days = common_days(offered, gbm)
    if len(days) < MIN_GROUP_DAYS:
        raise SystemExit(f"STOP: the walks cover {len(days)} scored decision days; fewer than {MIN_GROUP_DAYS}")
    forecasts = {m: {d: frame.forecasts[m][d] for d in days} for m in MODELS}
    forecasts[GBM] = {d: gbm[d] for d in days}
    frame.days = days
    labels = c.day_labels(frame, table)

    cells = {m: d1145.cell_table(frame, forecasts[m]) for m in SCORED}
    groups = c.groups_of(frame, labels)
    series: Dict[Tuple[str, str], Dict[str, Dict[date, float]]] = {}
    for _s, _l, grain, _m in groups:
        for metric in METRICS:
            if (grain, metric) not in series:
                series[(grain, metric)] = {m: c.series_of(frame, cells[m][metric], grain) for m in SCORED}
    _STATE.update(series=series, draws=args.draws, reps=args.reps)

    jobs, skipped = [], {}
    for split, label, grain, members in groups:
        if len(members) < MIN_GROUP_DAYS:
            skipped[f"{split}/{label}"] = len(members)
            continue
        for metric in METRICS:
            for candidate in (S3, A, GBM):
                jobs.append(("pairs", (split, label, grain, metric, candidate, tuple(members))))
            if split in ("pooled", "regime"):
                for candidate, reference in HEADLINE:
                    jobs.append(("block", (split, label, grain, metric, candidate, reference, tuple(members))))
    rate_models = ("B1", A, S3, GBM)
    cell_groups: Dict[Tuple[str, str], List[Tuple[date, int]]] = {}
    for m in rate_models:
        keys = sorted(cells[m]["hit_above"])
        cell_groups[(m, "pooled/all cells")] = keys
        for regime in REGIMES:
            kept = [k for k in keys if frame.regime(frame.target(*k)) == regime]
            if len(kept) >= MIN_GROUP_DAYS:
                cell_groups[(m, f"regime/{regime}")] = kept
    for (m, name), keys in cell_groups.items():
        for rule in RATES:
            jobs.append(("interval", ((rule, name, m), [cells[m][rule][k] for k in keys], c.CELL_BLOCK)))
    done = run_jobs(jobs, args.workers)

    by_key = {(s_, l_): (g, m) for s_, l_, g, m in groups}
    result: dict = {
        "issue": 1197, "declaration": str(DECLARATION.relative_to(REPO)), "panel_sha256": published_sha,
        "subset_from": None if args.first is None else args.first.isoformat(), "label": "development, not a verdict",
        "seed": SEED, "draws": args.draws, "reps": args.reps, "models": list(SCORED),
        "notes": {**notes, "decision_days_in_frame": len(offered), "scored_decision_days": len(days), "first": days[0].isoformat(),
                  "last": days[-1].isoformat(), "last_target": frame.target(days[-1], max(sp.HORIZONS)).isoformat(),
                  "days_without_a_walk": len(offered) - len(days)},
        "comparisons": [list(p) for p in COMPARISONS], "groups": {}, "skipped_groups": skipped, "politis_white": {}, "q95": {},
        "reading_rules": declaration["reading"]["rules"],
    }
    for kind, (ident, payload) in done:
        if kind == "pairs":
            split, label, metric, candidate = ident
            entry = result["groups"].setdefault(split, {}).setdefault(label, {"days": len(by_key[(split, label)][1])})
            entry.setdefault(metric, {"means": {}, "vs": {}})["vs"][candidate] = payload
        elif kind == "block":
            split, label, metric, pair = ident
            result["politis_white"].setdefault(split, {}).setdefault(label, {}).setdefault(metric, {})[pair] = payload
        else:
            rule, name, m = ident
            result["q95"].setdefault(name, {}).setdefault(m, {})[rule] = {"interval": payload}
    for split, labels_ in result["groups"].items():
        for label, entry in labels_.items():
            grain, members = by_key[(split, label)]
            for metric in METRICS:
                if metric in entry:
                    ser = series[(grain, metric)]
                    entry[metric]["means"] = {m: sum(ser[m][d] for d in members) / len(members) for m in SCORED}
    for name, by_model in result["q95"].items():
        for m, rules in by_model.items():
            keys = cell_groups[(m, name)]
            for rule in rules:
                values = [cells[m][rule][k] for k in keys]
                rules[rule]["rate"] = sum(values) / len(values)
                rules[rule]["cells"] = len(values)
    result["day_type_counts"] = {k: sum(1 for t in labels if k in labels[t]) for k in DAY_TYPES + (ORDINARY,)}
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    Path(args.output).write_text(json.dumps(result, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    return 0


# -- the page --------------------------------------------------------------------------------------------------------

def group_order(r: dict) -> List[Tuple[str, str]]:
    """Every group of the record in the order the page gives them: pooled, regimes, target-day types, leads."""

    g = r["groups"]
    order = [("pooled", "all decision days")]
    order += [("regime", x) for x in REGIMES if x in g.get("regime", {})]
    order += [("target_day_type", x) for x in (ORDINARY, "calendar_days") + DAY_TYPES if x in g.get("target_day_type", {})]
    order += [("lead", f"h={h}") for h in sp.HORIZONS if f"h={h}" in g.get("lead", {})]
    return order


def get_row(r: dict, split: str, label: str, metric: str, candidate: str, reference: str) -> Optional[dict]:
    return r["groups"].get(split, {}).get(label, {}).get(metric, {}).get("vs", {}).get(candidate, {}).get(reference)


def fmt(row: Optional[dict]) -> str:
    if row is None:
        return "n/a"
    if "undefined" in row:
        return "undefined"
    return (f"{mdr.pct(row['skill'])} {mdr.interval(row['skill_interval'], 100)} | {row['difference']:+.4f} "
            f"[{row['difference_interval'][0]:+.4f}, {row['difference_interval'][1]:+.4f}]")


def comparison_table(r: dict, metric: str, candidate: str, reference: str) -> List[str]:
    out = [f"**{LABELS[candidate]} against {LABELS[reference]}** (d = S({LABELS[reference]}) − S({LABELS[candidate]}); positive favours {LABELS[candidate]})", "",
           "| group | days | mean "
           f"{LABELS[candidate]} | mean {LABELS[reference]} | skill [90%] | mean d [90%] | on the skill interval | on the mean-d bound |",
           "|---|---|---|---|---|---|---|---|"]
    for split, label in group_order(r):
        entry = r["groups"][split][label]
        row = get_row(r, split, label, metric, candidate, reference)
        if row is None:
            continue
        means = entry[metric]["means"]
        title = label if split in ("pooled", "regime") else f"{label} ({split.replace('_', ' ')})" if split != "lead" else f"{label} (lead)"
        out.append(f"| {title} | {entry['days']} | {means[candidate]:.3f} | {means[reference]:.3f} | {fmt(row)} | "
                   f"{skill_reading(row)} | **{reading(row)}** |")
    out.append("")
    return out


def skill_text(row: Optional[dict]) -> str:
    return "n/a" if row is None or "undefined" in row else mdr.pct(row["skill"])


def regime_tally(r: dict, metric: str, candidate: str, reference: str) -> Dict[str, int]:
    count = {"gain": 0, "loss": 0, "undecided": 0}
    for label in REGIMES:
        row = get_row(r, "regime", label, metric, candidate, reference)
        if row is not None:
            count[reading(row)] += 1
    return count


def calibration_table(r: dict, name: str) -> List[str]:
    out = [f"| model | q95 exceedance, strict (> q95) | q95 exceedance, closed (≥ q95) | 50% band, closed | 90% band, closed | 90% band, open |",
           "|---|---|---|---|---|---|"]
    for m in ("B1", A, S3, GBM):
        e = r["q95"].get(name, {}).get(m)
        if e is None:
            continue

        def cell(rule):
            return f"{e[rule]['rate']:.3f} [{e[rule]['interval'][0]:.3f}, {e[rule]['interval'][1]:.3f}]"

        out.append(f"| {LABELS[m]} | {cell('hit_above')} | {cell('hit_at_or_above')} | {cell('b50_closed')} | {cell('b90_closed')} | "
                   f"{cell('b90_open')} |")
    out.append("")
    return out


def render(r: dict) -> str:
    n = r["notes"]
    head = [(S3, GBM), (A, GBM), (S3, A)]
    out = [
        "# (s3) against gbm_funding, paired on the same days (#1197)", "",
        "**Hypothesis and step:** H5 (primary goal), step 3. **Development data, not a verdict** (scoring protocol v1, #640): days to "
        f"{n['last_target']}, no lockbox day. Nothing is adopted, nothing is registered and no claim changes. Generated by "
        "`scripts/s3_vs_gbm_1197.py page` from `docs/research/s3-vs-gbm-1197/result.json`, not edited by hand. The arms are those of "
        f"`{r['declaration']}`, committed before any score of #1145 and unchanged.", "",
        f"Panel digest `{r['panel_sha256'][:8]}…`. The `gbm_funding` walks are the ones on Eleonora's Mac, read-only and not rebuilt; the "
        f"scoring covers the {n['scored_decision_days']:,} decision days they cover ({n['first']} to {n['last']}) of the "
        f"{n['decision_days_in_frame']:,} the frame offers; the same days for every model. Studentized stationary bootstrap (ruling 1), mean "
        f"block {sp.BLOCK_LENGTH} business days, {r['draws']:,} draws, seed {r['seed']}, two-sided 90% interval (the lower end is the "
        "one-sided 95% bound). Skill is `mean(d) / mean(S(benchmark))`. B1' (Lens C's calendar-aware persistence, #960) is beside B1; B1 "
        "stays the protocol's benchmark.", "",
        "**How the rows are read.** Every paired row shows the skill interval and the interval on mean d. By Eleonora's ruling on #1009 a "
        "row is read on the studentized bound on mean d: **gain** when the lower bound is above zero, **loss** when the upper bound is "
        "below zero, **undecided** otherwise. The reading on the skill interval is shown beside it, because the two intervals are built "
        "from different studentized draws and can fall on different sides of zero.", "",
        "**Caveat (Lens C of the five-lens review, #958).** The lag-10 HAC standard error that studentizes the mean-d bound is understated "
        "about 2× after 2020 (about 2.3× in 2021–23, 1.7× in 2024–26), and the bootstrap block of 10 days is an order of magnitude shorter "
        "than the autocorrelation of d. The bound is therefore optimistic: an interval that excludes zero is narrower than it should be "
        "after 2020. A reading on this page is evidence for a question, not a verdict.", "",
        "The earlier figure for (a) against `gbm_funding` is #1115's: +6.8% pooled [+3.3%, +10.1%], on its own days and its own "
        "(pre-#1135) day types. This page's day types are those of the code on main at the time of the run.", ""]
    out += ["## Head to head, pooled", ""]
    for metric in METRICS:
        out += [f"### {METRIC_TITLES[metric]}", "", "| comparison | days | skill [90%] | mean d [90%] | on the skill interval | on the mean-d bound |",
                "|---|---|---|---|---|---|"]
        for cand, ref in COMPARISONS:
            row = get_row(r, "pooled", "all decision days", metric, cand, ref)
            out.append(f"| {LABELS[cand]} against {LABELS[ref]} | {r['groups']['pooled']['all decision days']['days']} | {fmt(row)} | "
                       f"{skill_reading(row) if row else 'n/a'} | **{reading(row) if row else 'n/a'}** |")
        out.append("")
        means = r["groups"]["pooled"]["all decision days"][metric]["means"]
        out += ["Mean score, lower is better: " + "; ".join(f"{LABELS[m]} {means[m]:.3f}" for m in SCORED) + ".", ""]
    out += ["## By regime, by target-day type and by lead", "",
            "Each table gives one comparison on one score, pooled first, then the regimes (by target day), the target-day types (a day "
            "can carry several; `ordinary` is a day with none, `calendar_days` any calendar day) and the leads.", ""]
    for metric in METRICS:
        out += [f"### {METRIC_TITLES[metric]}", ""]
        for cand, ref in head:
            tally = regime_tally(r, metric, cand, ref)
            out += comparison_table(r, metric, cand, ref)
            out += [f"Regimes read on the mean-d bound: {tally['gain']} gain, {tally['loss']} loss, {tally['undecided']} undecided.", ""]
    out += ["### Against the benchmarks, pooled and by regime", ""]
    for metric in METRICS:
        out += [f"**{METRIC_TITLES[metric]}**", ""]
        for cand in (S3, A, GBM):
            for ref in ("B1", B1P):
                pooled_row = get_row(r, "pooled", "all decision days", metric, cand, ref)
                parts = []
                for label in REGIMES:
                    row = get_row(r, "regime", label, metric, cand, ref)
                    if row is not None:
                        parts.append(f"{label} {skill_text(row)} ({reading(row)})")
                out.append(f"- {LABELS[cand]} against {LABELS[ref]}: pooled {skill_text(pooled_row)} ({reading(pooled_row)}); "
                           f"by regime: {'; '.join(parts)}.")
        out.append("")
    out += ["## Politis-White block beside 10", "",
            "The automatic block length of Politis and White for each headline comparison's loss differential, and the pooled test at that "
            "block (rounded). The block of 10 above is the protocol's; this is beside it, not instead.", "",
            "| score | comparison | group | block | days | skill at that block [90%] | mean d at that block [90%] | on the mean-d bound |",
            "|---|---|---|---|---|---|---|---|"]
    for metric in METRICS:
        for split in ("pooled", "regime"):
            for label, byname in r["politis_white"].get(split, {}).items():
                for pair, entry in byname.get(metric, {}).items():
                    if entry is None:
                        continue
                    cand, ref = pair.split("|")
                    row = entry.get("row")
                    out.append(f"| {METRIC_TITLES[metric]} | {LABELS[cand]} against {LABELS[ref]} | {label} | {entry['block']:.1f} | "
                               f"{entry['days']} | {fmt(row) if row else 'pooled only'} | {reading(row) if row else ''} |")
    out += ["", "## Calibration", "",
            "The share of cells (decision day, lead) in which the outcome is above the 95th percentile, under both hit rules (the nominal "
            "rate is 0.05), and the coverage of the 50% and 90% bands, with an interval over the cells in date order (block "
            f"{c.CELL_BLOCK:g}). Pooled:", ""]
    out += calibration_table(r, "pooled/all cells")
    for regime in REGIMES:
        name = f"regime/{regime}"
        if name in r["q95"]:
            out += [f"{regime}:", ""] + calibration_table(r, name)
    out += ["## What this page does and does not show", "",
            "- It is development data on the days the walks cover. It gives no verdict for a hypothesis, registers nothing and moves no "
            "published figure; the lockbox is untouched.",
            "- Every reading is on the mean-d bound, which Lens C's caveat says is optimistic after 2020. A gain whose lower bound is "
            "close to zero is not a settled gain.",
            "- `gbm_funding` and the (s3) and (a) forecasts are scored on the same decision days and the same five targets each. B2 and "
            "`spread_mr_ctx` are not references here; B1 and B1' are. The benchmark rows of the frame that #1145 dropped for a missing "
            f"benchmark ({len(r['notes']['benchmark_missing'])} days, including any year-end where B2 refuses) are absent here too.",
            "- The pressure-day type split of protocol §7 is not given; the target-day types are (as the #1145 page). The scaled score "
            "of #967 is not given.",
            "- The walks were not rebuilt; they are the ones on her Mac, checked against the published panel's digest by "
            "`calendar_mr_1115.load_gbm`.", ""]
    out += question(r)
    return "\n".join(out) + "\n"


def question(r: dict) -> List[str]:
    """The closing question: which model the page supports as the H5 candidate. Nothing is decided here."""

    pooled = "all decision days"
    lines = []
    for metric in METRICS:
        row = get_row(r, "pooled", pooled, metric, S3, GBM)
        lines.append(f"{METRIC_TITLES[metric]}: (s3) against `gbm_funding` {mdr.pct(row['skill']) if row and 'undefined' not in row else 'n/a'} "
                     f"({reading(row) if row else 'n/a'} on the mean-d bound)")
    return ["## Question for Eleonora: does (s3) stay the H5 candidate?", "",
            "(s3) is the candidate by your ruling of 23 October 2026, on #1145's evidence against (a); this page adds the comparison with "
            "`gbm_funding` that was missing. **Nothing is adopted here and no claim changes.** Pooled: " + "; ".join(lines) + ".", "",
            "**Options** (numbered; the default applies if you have not answered by the next 5 pm batch):", "",
            "1. **Keep (s3) as the H5 candidate** (default). Nothing changes; this page stays a development result.",
            "2. **Re-open the choice between (s3) and `gbm_funding`** on the regimes and day types above where the reading differs; that "
            "is your decision, and would be followed by a registration discussion.",
            "3. **Ask for a further step** before deciding (for example the same comparison with B2 and `spread_mr_ctx` as references, "
            "or on the 2026 development days).", ""]


def page(args) -> int:
    r = json.loads(Path(args.score).read_text(encoding="utf-8"))
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    Path(args.output).write_text(render(r), encoding="utf-8")
    return 0


# -- the log entry ---------------------------------------------------------------------------------------------------


def log_entry(r: dict, when: str) -> str:
    """The research-log entry (`scripts/check_research_log.py`, `ENTRY_FORMAT`), every figure read from the record."""

    n = r["notes"]
    pooled = "all decision days"

    def pair(metric, cand, ref):
        row = get_row(r, "pooled", pooled, metric, cand, ref)
        if row is None or "undefined" in row:
            return f"{LABELS[cand]} against {LABELS[ref]} undefined"
        return (f"{LABELS[cand]} against {LABELS[ref]} {mdr.pct(row['skill'])} {mdr.interval(row['skill_interval'], 100)}, "
                f"{reading(row)} on the mean-d bound")

    regimes = []
    for metric in ("grid_crps",):
        for cand, ref in HEADLINE:
            tally = regime_tally(r, metric, cand, ref)
            regimes.append(f"{LABELS[cand]} against {LABELS[ref]}: {tally['gain']} gain, {tally['loss']} loss, {tally['undecided']} undecided")
    means = r["groups"]["pooled"][pooled]["grid_crps"]["means"]
    return "\n".join([
        f"### {when} [H5] step 3 · eleonorabjornberg/repo-market-model#1197",
        "- Directive: #1197",
        "- Step: 3 (the H5 candidate (s3) of #1145 against gbm_funding on her Mac walks, paired on the same days)",
        "- Tier: development",
        f"- Pins: declaration `{r['declaration']}`, committed and unchanged; seed {r['seed']}; published panel `{r['panel_sha256'][:8]}…`; "
        "gbm_funding walks read-only from her Mac and not rebuilt; scored days to 2025-12-31, no locked day",
        f"- Tried: (s3), (a) and gbm_funding scored on the {n['scored_decision_days']:,} decision days the walks cover ({n['first']} to "
        f"{n['last']}), with B1 and B1' beside them, grid CRPS over h = 1-5 and upper-tail twCRPS, {r['draws']:,} studentized bootstrap "
        "draws at mean block 10 with Politis-White beside, pooled, by regime, by target-day type and by lead, read on the mean-d bound. "
        "Variants: 0 (no new model).",
        f"- Result: grid CRPS {means[S3]:.3f} (s3), {means[A]:.3f} (a), {means[GBM]:.3f} gbm_funding, {means['B1']:.3f} B1, {means[B1P]:.3f} B1'. "
        + "; ".join(pair("grid_crps", cand, ref) for cand, ref in HEADLINE) + ". Upper-tail twCRPS: "
        + "; ".join(pair("upper_tail_twcrps", cand, ref) for cand, ref in HEADLINE) + ". By regime on grid CRPS (mean-d bound): "
        + "; ".join(regimes) + ". Development data; Lens C's caveat applies to every reading.",
        "- Against kill: not tested. This compares two candidates on development data; a development figure never settles a kill (scoring protocol v1).",
        "- Next: whether (s3) stays the H5 candidate is Eleonora's decision on `docs/research/s3-vs-gbm-1197-result.md` (its closing question, "
        "default: keep (s3)). Nothing is registered.",
        ""])


def log_command(args) -> int:
    r = json.loads(Path(args.score).read_text(encoding="utf-8"))
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    Path(args.output).write_text(log_entry(r, args.date), encoding="utf-8")
    return 0


def check_walks_command(args) -> int:
    walks = require_walks(Path(args.walks))
    print(f"walks: present ({', '.join(f'{GBM}_h{h}.json' for h in sp.HORIZONS)}) in {walks}")
    return 0


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="command", required=True)
    w = sub.add_parser("check-walks", help="stop unless every lead's gbm_funding walk is in the directory")
    w.add_argument("walks")
    w.set_defaults(func=check_walks_command)
    s = sub.add_parser("score", help="walk (a) and (s3), read the gbm_funding walks, and score them on the same days")
    s.add_argument("--panel", required=True)
    s.add_argument("--walks", required=True, help="a directory holding gbm_funding_h<lead>.json for all five leads")
    s.add_argument("--output", required=True)
    s.add_argument("--draws", type=int, default=sp.DRAWS)
    s.add_argument("--reps", type=int, default=2000, help="bootstrap resamples of a rate interval")
    s.add_argument("--workers", type=int, default=4)
    s.add_argument("--first", type=date.fromisoformat, default=None,
                   help="start the walk on this day (a subset, for the script's test only; the declared run omits it)")
    s.set_defaults(func=score)
    g = sub.add_parser("page", help="write the result page from a score file")
    g.add_argument("--score", required=True)
    g.add_argument("--output", required=True)
    g.set_defaults(func=page)
    e = sub.add_parser("log", help="write the research-log entry from a score file")
    e.add_argument("--score", required=True)
    e.add_argument("--output", required=True)
    e.add_argument("--date", required=True, help="the entry's date, YYYY-MM-DD, Eastern time")
    e.set_defaults(func=log_command)
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
