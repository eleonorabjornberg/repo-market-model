"""B4, a plain quantile regression on reserves and calendar days, scored beside B1, B1' and B2 and against the candidate (s3c-ann-net) at the 18:00
decision instant (#1360; H5, registration design, step 4 to 5; her ruling of 2 November 2026).

A development study, never a verdict. It writes JSON and Markdown to the paths it is given and nothing into `docs/runs/`. Every choice is in
`metadata/b4_quantile_regression_1360.json`, which this script refuses to read unless it is committed and unchanged. B4 is `repo_model.b4_quantile_regression`
(reached by the protocol as `repo_model.protocol_benchmarks.b4_forecast`): per lead and per level of the protocol's grid, a linear quantile regression of the
target-day spread on the last observed spread, the as-of reserve balances and the calendar terms read at the target day, on direct pairs of an expanding window,
refitted on the candidate's cadence. The candidate (s3c-ann-net) is walked as `scripts/s3c_ann_net_cmb_1356.py` walks its reference, and B1, B1' and B2 are
#1255's, at 18:00 (`repo_model.decision_instant`). The frames and machinery are #1255's, #1273's, #1288's, #1321's and #1356's and are loaded as they are: the
development window of #1145 and #1241 (targets up to 2025-12-31) and the 2026 development days of #1229 (targets 2026-01-02 to 2026-09-03, the near-blind tier
open since GO #151). The blind tier and every lockbox day are refused by the frames' own guards.

It measures grid CRPS averaged over h = 1..5 (primary), upper-tail twCRPS (key secondary) and the Brier score of P(> +5 bp)
(`docs/decisions/pressure-probability.md`), on scoring protocol v1's studentized stationary bootstrap read on the bound on mean d (her #1009 ruling) with the
skill interval beside, split by lead, regime, pressure-day type and the calendar type of the target day; reports the coverage of the central 90% band; and
what B4 fitted (the coefficients by lead and level, averaged over the refits).

Commands, from a clone of the branch:

    PYTHONPATH=src python3 -m repo_model.cli build --raw-root tests/fixtures/snapshots/funding_inputs \\
        --output PUB.csv --build-cutoff 2026-09-08T21:31:42+00:00 --decision-time 18:00:00
    PYTHONPATH=src python3 -m repo_model.cli verify-panel PUB.csv --manifest metadata/funding_panel_manifest.json
    PYTHONPATH=src python3 scripts/b4_quantile_regression_1360.py score --panel PUB.csv --output docs/research/b4-quantile-regression-1360/result.json
    PYTHONPATH=src python3 scripts/b4_quantile_regression_1360.py page \\
        --score docs/research/b4-quantile-regression-1360/result.json --output docs/research/b4-quantile-regression-1360-result.md

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


from repo_model import announced_iorb, b4_quantile_regression as b4, metrics, policy_events, s3c_announced, s3c_candidate, s3c_net  # noqa: E402
from repo_model import scoring_protocol as sp, spread_mr_state_calendar as sc  # noqa: E402
from repo_model import spread_mr_calendar as cal  # noqa: E402
from repo_model.baseline import panel_sha256  # noqa: E402
from repo_model.evaluation_splits import load_split_declaration  # noqa: E402
from repo_model.exploration import EXPLORATORY_END, require_exploratory_window  # noqa: E402

#: #1356's script (and through it #1321's, #1288's, #1273's, #1255's, #1241's and #1229's), loaded under an alias of its own so that the pickling of the worker
#: pool's tasks does not meet another test module's copy. Its `decision_instant_pinned` runs the chain at the declared 18:00 instant.
m1356 = _load("s3c_ann_net_cmb_1356", "s3c_ann_net_cmb_1356_in_1360")
m1321, m1288, m1273, m1255 = m1356.m1321, m1356.m1288, m1356.m1273, m1356.m1255
k, c, s686, s761 = m1356.k, m1356.c, m1356.s686, m1356.s761
load_daily_panel = m1288.load_daily_panel
decision_instant_pinned = m1356.decision_instant_pinned

DECLARATION = REPO / "metadata" / "b4_quantile_regression_1360.json"
RECORD_1321 = m1356.RECORD_1321
SEED = 1360
LAST_DAY = EXPLORATORY_END
WINDOW_LAST = m1288.WINDOW_LAST
WINDOWS = m1288.WINDOWS
WINDOW_TITLES = m1288.WINDOW_TITLES
B4 = "B4"
ANNNET, B1P = m1288.ANNNET, m1288.B1P
BENCHMARKS = m1288.BENCHMARKS
#: Every model of the run, in the order of the declaration; the references are the models that exist in #1321's record too.
MODELS = BENCHMARKS + (B4, ANNNET)
REFERENCES = (ANNNET,) + BENCHMARKS
LABELS = {"B1": "B1", B1P: "B1' (#960)", "B2": "B2", B4: "B4, the plain quantile regression", ANNNET: "(s3c-ann-net), the candidate"}
SHORT = {"B1": "B1", B1P: "B1'", "B2": "B2", B4: "B4", ANNNET: "(s3c-ann-net)"}
TESTED = m1288.TESTED
METRIC_NAMES = m1288.METRIC_NAMES
METRIC_TITLES = m1288.METRIC_TITLES
MIN_GROUP_DAYS = m1288.MIN_GROUP_DAYS
BLOCK = float(sp.BLOCK_LENGTH)
LEADS = tuple(sp.HORIZONS)
SPLITS = ("pooled", "lead", "regime", "pressure_day_type", "target_day_type")
FIT_LEVELS = (0.05, 0.5, 0.95)
REPS = 2000
_STATE: Dict = {}


def committed_declaration(path: Path = DECLARATION) -> dict:
    """The declaration, refused unless it is committed and unchanged since `HEAD`."""

    return s686.committed_declaration(path)


def plan(candidate: str, split: str = "pooled") -> List[str]:
    """What a model is tested against: B4 against B1, B1' and B2; the candidate against B4, B1, B1' and B2. A benchmark is never a candidate."""

    if candidate == B4:
        return list(BENCHMARKS)
    if candidate == ANNNET:
        return [B4] + list(BENCHMARKS)
    return []


# -- the walks and the frame ---------------------------------------------------------------------------------------------


def require_forecasts(frame, forecasts: Mapping[date, object]) -> None:
    """Every scored decision day of the frame has a forecast.

    Raises:
        ValueError: a scored decision day has none.
    """

    for day in frame.days:
        if day not in forecasts:
            raise ValueError(f"the B4 walk has no forecast on the scored decision day {day}: every model is compared on the same days")


def candidate_walk(window: str, frame, panel, splits, registry, results, auctions, first: Optional[date]):
    """The walk of (s3c-ann-net) over #1255's decision days, as `s3c_ann_net_cmb_1356.walks_of` walks its reference."""

    days = m1288.candidate_days(frame, window, first)
    settings = dict(registry=registry, decision_time=k.DECISION_TIME, splits=splits)
    states = s3c_net.constant_states(panel)
    iorb = announced_iorb.load_announcements(c.IORB_TABLE)
    term_table = s3c_announced.AnnouncedTermTable(panel, iorb, results, decision_time=k.DECISION_TIME)
    net_table = s3c_announced.AnnouncedNetSizeTable(panel, auctions, decision_time=k.DECISION_TIME)
    walk = sc.walk(panel, days, term_table, states, (s3c_announced.ANN_NET_ARM,), sizes=net_table, **settings)
    name = s3c_announced.ANN_NET_ARM.name
    for d in frame.days:
        if d not in walk.forecasts[name]:
            raise ValueError(f"the reference walk has no forecast of {name} on the scored decision day {d}")
    return walk, name


def b4_walk(window: str, frame, panel, registry, announcements, first: Optional[date]) -> b4.Walk:
    """B4 over the decision days the candidate is walked over, refitting on the candidate's cadence (`b4_quantile_regression.walk`)."""

    days = m1288.candidate_days(frame, window, first)
    table = cal.TermTable(panel, announcements, decision_time=k.DECISION_TIME)
    reserves = b4.ReserveTable(panel, registry=registry, decision_time=k.DECISION_TIME)
    walked = b4.walk(panel, days, table, reserves, registry=registry, decision_time=k.DECISION_TIME)
    require_forecasts(frame, walked.forecasts)
    return walked


def build(window: str, panel, splits, registry, table, register, results, auctions, first: Optional[date]):
    """#1255's frame of `window` with (s3c-ann-net) and B4 added: `(frame, notes, candidate_walk, b4_walk, groups_fn)`."""

    frame, notes, _mine, _cells, groups_fn = m1255.build(window, panel, splits, registry, table, register, first)
    walk, name = candidate_walk(window, frame, panel, splits, registry, results, auctions, first)
    announcements = announced_iorb.load_announcements(c.IORB_TABLE)
    walked = b4_walk(window, frame, panel, registry, announcements, first)
    forecasts = {m: frame.forecasts[m] for m in BENCHMARKS}
    forecasts[ANNNET] = m1255.s3c_forecasts(frame, register, {d: walk.forecasts[name][d] for d in frame.days})
    forecasts[B4] = {d: walked.forecasts[d] for d in frame.days}
    frame.forecasts = {m: {d: forecasts[m][d] for d in frame.days} for m in MODELS}
    crossed = sum(1 for d in frame.days for h in LEADS if walked.crossed[d][h])
    notes = dict(notes, refits_candidate=len(walk.fits), refits_b4=len(walked.estimates), b4_forecasts_the_sort_changed=crossed,
                 b4_forecasts=len(frame.days) * len(LEADS))
    return frame, notes, walk, walked, groups_fn


def fit_summary(estimates: Mapping[date, Mapping[int, "b4.Estimate"]], levels: Sequence[float] = FIT_LEVELS, leads: Sequence[int] = LEADS) -> dict:
    """What B4 fitted: for each lead and each of `levels`, the mean over the refits of the intercept, the last-spread slope (bp per bp), the reserves slope
    (bp per USD trillion) and each calendar term's effect (bp per flagged day; 0 on a refit where the term did not enter), with the share of refits in which
    it entered; and the count of fits that stopped at `MAX_ITERATIONS`.

    The mean is over refits that share most of their pairs, not a sampling estimate.
    """

    names = ("intercept", "last_spread", "reserves") + tuple(b4.TERMS)
    out: dict = {"fits": 0, "capped_fits": 0}
    for h in leads:
        for tau in levels:
            sums = {n: 0.0 for n in names}
            entered = {n: 0 for n in b4.TERMS}
            for per_lead in estimates.values():
                e = per_lead[h]
                beta = e.coefficients[tau]
                sums["intercept"] += beta[0]
                sums["last_spread"] += beta[1]
                sums["reserves"] += beta[2]
                for name, value in zip(e.terms, beta[3:]):
                    sums[name] += value
                    entered[name] += 1
            refits = len(estimates)
            row = {n: {"mean": sums[n] / refits} for n in names}
            for n in names:
                row[n]["share_of_refits"] = entered[n] / refits if n in entered else 1.0
            out.setdefault(str(h), {})[str(tau)] = row
        for per_lead in estimates.values():
            e = per_lead[h]
            out["fits"] += len(e.levels)
            out["capped_fits"] += sum(1 for v in e.iterations.values() if v >= b4.MAX_ITERATIONS)
    return out


def compare_references(ours: Mapping[str, dict], theirs: Mapping[str, dict]) -> dict:
    """The pooled means of the references here beside #1321's record (made at 18:00 with the same frames and walks): they must agree to 1e-9.

    Raises:
        ValueError: they do not.
    """

    out: dict = {}
    for window, result in ours.items():
        a, b = theirs[window]["groups"]["pooled"]["all decision days"], result["groups"]["pooled"]["all decision days"]
        worst = max(abs(b[m]["means"][x] - a[m]["means"][x]) for m in TESTED for x in REFERENCES)
        if worst > 1e-9:
            raise ValueError(f"the references of the {window} window differ from #1321's record by {worst:.2e}: the frames and walks are not the same")
        out[window] = {"difference": worst, "models": list(REFERENCES), "metrics": list(TESTED)}
    return out


# -- the tests, in parallel ----------------------------------------------------------------------------------------------


def _identical(series, candidate: str, reference: str, members: Sequence[date]) -> bool:
    return all(series[candidate][d] == series[reference][d] for d in members)


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
            out[name]["unstudentized"] = m1356.unstudentized(series, candidate, name, days, _STATE["reps"])
    return (split, label, metric, candidate), out


def run_jobs(jobs, workers: int):
    with multiprocessing.get_context("fork").Pool(workers) as pool:
        return pool.map(_pairs_task, jobs, chunksize=1)


def run_window(window: str, panel, splits, registry, table, register, results, auctions, args) -> dict:
    frame, notes, _walk, walked, groups_fn = build(window, panel, splits, registry, table, register, results, auctions, args.first)
    last = WINDOW_LAST[window]
    labels = c.day_labels(frame, table)
    pressure = k.pressure_labels(frame, sorted(labels))
    cells = {m: m1288.cell_table(frame, frame.forecasts[m], last) for m in MODELS}
    for m in MODELS:
        official = sp.day_scores(frame.forecasts[m], frame.outcome, frame.dates, score=sp.grid_crps)
        mean = s686.by_decision(cells[m]["grid_crps"])
        if set(official) != set(mean) or any(abs(official[d] - mean[d]) > 1e-9 for d in mean):
            raise SystemExit(f"grid CRPS of {m}: the cell means differ from scoring_protocol.day_scores")
    groups = [g for g in groups_fn(frame, labels, pressure) if g[0] in SPLITS]
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
            for candidate in (B4, ANNNET):
                jobs.append((split, label, grain, metric, candidate, tuple(members)))
    done = run_jobs(jobs, args.workers)
    result: dict = {"notes": notes, "groups": {}, "skipped_groups": skipped, "fit": fit_summary(walked.estimates)}
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
    """Score both windows with every module of the chain at the declared decision instant (`decision_instant_pinned`)."""

    with decision_instant_pinned():
        return _score(args)


def _score(args) -> int:
    declaration = committed_declaration()
    panel_path = Path(args.panel)
    published_sha = panel_sha256(panel_path)
    panel = [row for row in load_daily_panel(panel_path) if row.date <= LAST_DAY]
    require_exploratory_window([row.date for row in panel], where="scripts/b4_quantile_regression_1360")
    splits = load_split_declaration(c.SPLITS)
    registry = json.loads(c.SOURCES.read_text(encoding="utf-8"))
    register = policy_events.load_register()
    table = cal.TermTable(panel, announced_iorb.load_announcements(c.IORB_TABLE), decision_time=c.DECISION_TIME)
    auctions = m1273.load_auctions()
    results = m1288.load_results()
    result: dict = {
        "issue": 1360, "declaration": str(DECLARATION.relative_to(REPO)), "panel_sha256": published_sha,
        "decision_time": c.DECISION_TIME.strftime("%H:%M"), "subset_from": None if args.first is None else args.first.isoformat(),
        "label": "development, not a verdict", "seed": SEED, "draws": args.draws, "reps": args.reps, "models": list(MODELS),
        "references": list(REFERENCES), "ridge": b4.RIDGE, "refit_every": b4.REFIT_EVERY, "min_pairs": b4.MIN_PAIRS, "terms": list(b4.TERMS),
        "windows": {}, "reading_rules": declaration["reading_rules"], "amendments": declaration["amendments"],
    }
    for window in (getattr(args, "windows", None) or WINDOWS):
        result["windows"][window] = run_window(window, panel, splits, registry, table, register, results, auctions, args)
    if args.first is None and not getattr(args, "windows", None) and RECORD_1321.exists():
        result["against_1321"] = compare_references(result["windows"], json.loads(RECORD_1321.read_text(encoding="utf-8"))["windows"])
    else:
        result["against_1321"] = {}
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    Path(args.output).write_text(json.dumps(result, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    return 0


# -- the page ------------------------------------------------------------------------------------------------------------


def cell(row: Optional[dict]) -> str:
    return m1288.cell(row)


def _vs(group: Optional[Mapping[str, object]], metric: str, candidate: str, reference: str) -> Optional[dict]:
    return m1288._vs(group, metric, candidate, reference)


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


def means_split_table(window: Mapping[str, object], split: str, metric: str, models: Sequence[str] = MODELS) -> List[str]:
    labels = window["groups"].get(split, {})
    out = [f"| {split.replace('_', ' ')} | days | " + " | ".join(SHORT[m] for m in models) + " |", "|---|---|" + "---|" * len(models)]
    for label in sorted(labels):
        g = labels[label]
        out.append(f"| {label} | {g['days']} | " + " | ".join(f"{g[metric]['means'][m]:.4f}" for m in models) + " |")
    return out if len(out) > 2 else []


def reading_of(row: Optional[dict]) -> str:
    """`gain`, `loss`, `undecided`, `identical` or `n/a` on the mean-d bound, for a model against a reference."""

    if row is None:
        return "n/a"
    return "identical" if row.get("identical") else k.reading_words(row).split(" ")[0].strip("*")


def readings(window: Mapping[str, object], split: str, metric: str, candidate: str, reference: str) -> Dict[str, List[str]]:
    """The groups of a split, sorted by how `candidate` reads against `reference`: `gain`, `loss`, `undecided`."""

    out: Dict[str, List[str]] = {"gain": [], "loss": [], "undecided": []}
    for label, g in sorted(window["groups"].get(split, {}).items()):
        word = reading_of(_vs(g, metric, candidate, reference))
        if word in out:
            out[word].append(label)
    return out


def headline(r: Mapping[str, object]) -> str:
    parts = []
    for window, text in (("development", "On the development window"), ("2026", "on the 2026 development days")):
        g = r["windows"].get(window, {}).get("groups", {}).get("pooled", {}).get("all decision days")
        if g is None:
            continue
        parts.append(
            f"{text}, pooled grid CRPS: (s3c-ann-net) against B4 {cell(_vs(g, 'grid_crps', ANNNET, B4))}; B4 against B1 {cell(_vs(g, 'grid_crps', B4, 'B1'))}")
    return "; ".join(parts) + "."


def definition() -> List[str]:
    return [
        "**What B4 is.** For each lead h = 1..5 and each of the protocol's 23 levels, a linear quantile regression of the spread on the target day (bp) on an "
        "intercept, the last observed spread (the as-of anchor's), the as-of **reserve_balances** (USD trillion, read per field at the decision instant by "
        "`InformationRule`) and the seven calendar terms of the candidate's base (month-end, quarter-end, tax date, the coupon and bill settlement flags, the "
        "19th to 23rd and the first three business days) read at the **target day** on **direct** pairs (`one_step_guard` passes with no allow-list entry; the "
        "two settlement flags are scheduled fields and enter at lead 1 only, where `asof` rule 2 admits them). **Expanding** window, refitted on the candidate's "
        f"21-day cadence, a fixed **ridge** of {b4.RIDGE:g} (a numerical stabiliser against a check loss that is linear in the residual), the 23 quantiles of a "
        "lead sorted so that they never cross. Nothing is tuned and B4 is scored once. **B4 does not read the auction-announcement dating of the candidate** "
        "(the settlement terms of leads 2 to 5, sized by net settlement): that is the candidate's addition, not a plain calendar column, and it is a stated "
        "difference between the two. It does not read the scarcity state either: the state is unknown on every 2026 development day in the measurement panel, "
        "so the benchmark reads the reserves column, which is public throughout (a question below)."]


def fit_table(fit: Mapping[str, object], tau: str) -> List[str]:
    names = ("intercept", "last_spread", "reserves") + tuple(b4.TERMS)
    out = ["| term | " + " | ".join(f"h={h}" for h in LEADS) + " |", "|---|" + "---|" * len(LEADS)]
    for n in names:
        cells = []
        for h in LEADS:
            e = fit[str(h)][tau][n]
            share = "" if e["share_of_refits"] >= 1.0 else f" ({100 * e['share_of_refits']:.0f}% of refits)"
            cells.append(f"{e['mean']:+.3f}{share}")
        out.append(f"| {n.replace('_', ' ')} | " + " | ".join(cells) + " |")
    return out


def render(r: dict) -> str:
    out = [
        "# B4, a plain quantile regression on reserves and calendar days, beside B1, B1' and B2, at the 18:00 decision (#1360)", "",
        "**Does the candidate beat a parsimonious model that reads the same public reserve and calendar information?** " + headline(r), "",
        "**Hypothesis and step:** H5 (primary goal), registration design, step 4 to 5; her ruling of 2 November 2026 (chat, relayed on #1360). **Development data, "
        "not a verdict** (scoring protocol v1, #640). Nothing is registered or published, the candidate (s3c-ann-net) does not change, and whether B4 joins the "
        "protocol's decision rule is hers (the marked question at the end). Generated by `scripts/b4_quantile_regression_1360.py page` from "
        f"`docs/research/b4-quantile-regression-1360/result.json`, not edited by hand; declared in `{r['declaration']}` before any score.", ""]
    out += definition() + [""]
    out += [
        f"Panel digest `{r['panel_sha256']}`. Studentized stationary bootstrap (ruling 1), mean block {sp.BLOCK_LENGTH} business days, {r['draws']:,} draws, "
        f"seed {r['seed']}, two-sided 90% interval (the lower end is the one-sided 95% bound). Positive mean d favours the model named first. **A reading (gain, "
        "loss, undecided) is taken from the mean-d bound** (her ruling on #1009), with the skill interval beside it; for a Brier score the skill is the Brier "
        "skill score. **Caveat (Lens C, #958):** the lag-10 HAC standard error that studentizes the bound is understated about 2x after 2020, so an interval that "
        "excludes zero is narrower than it should be; the intervals of a group of target days keep the current method (#1221, #1228). No reading of a "
        "day-type group is a finding. Groups of fewer than 20 days are listed with their means and not tested.", "",
        "**What kind of look this is.** The 2026 days were already seen by #845, by the #151 final test, and by #1229, #1255, #1273, #1288, #1321 and #1356. "
        "The 2026 days are shown separately and decide nothing. B4 was designed after the development window had been seen, by a review that had seen it, so a "
        "result here is exploration.", ""]
    for window in WINDOWS:
        w = r["windows"].get(window)
        if w is None:
            continue
        n, pooled = w["notes"], w["groups"]["pooled"]["all decision days"]
        out += [f"## {WINDOW_TITLES[window]}", "",
                f"Scored decision days: {n['scored_decision_days']:,} ({n['first']} to {n['last']}); {n['refits_candidate']} refits of the candidate's walk and "
                f"{n['refits_b4']} of B4's. B4's fitted quantiles crossed (and the sort changed them) in {n['b4_forecasts_the_sort_changed']:,} of "
                f"{n['b4_forecasts']:,} lead forecasts; {w['fit']['capped_fits']:,} of {w['fit']['fits']:,} fits stopped at the iteration cap of {b4.MAX_ITERATIONS}.", "",
                "### Mean scores (pooled)", ""] + mean_table(pooled)
        for cand in (ANNNET, B4):
            out += ["", f"### {LABELS[cand]} against each reference (pooled)", ""] + against_table(pooled, cand) + [""]
        for split, title in (("lead", "By lead"), ("regime", "By regime"), ("pressure_day_type", "By pressure-day type of the target day"),
                             ("target_day_type", "By calendar day type of the target")):
            for cand, ref in ((ANNNET, B4), (B4, "B1")):
                table = split_table(w, split, cand, ref)
                if table:
                    out += [f"### {title}: {SHORT[cand]} against {SHORT[ref]}", ""] + table + [""]
        for split, title in (("regime", "regime"), ("pressure_day_type", "pressure-day type"), ("lead", "lead")):
            table = means_split_table(w, split, "grid_crps")
            if table:
                out += [f"### Mean grid CRPS by {title}, every model", ""] + table + [""]
        table = means_split_table(w, "regime", "b90_closed")
        if table:
            out += ["### 90% band coverage by regime", ""] + table + [""]
        out += ["### Where B4 beats or loses to the candidate (grid CRPS)", ""]
        for split in ("lead", "regime", "pressure_day_type", "target_day_type"):
            found = readings(w, split, "grid_crps", ANNNET, B4)
            out.append(f"- {split.replace('_', ' ')}: the candidate is read better than B4 on {len(found['gain'])} group(s) ({', '.join(found['gain']) or 'none'}), "
                       f"worse on {len(found['loss'])} ({', '.join(found['loss']) or 'none'}), undecided on {len(found['undecided'])}.")
        out += ["", "### What B4 fitted (mean over the refits)", "",
                "Coefficients in bp at the 50th percentile (bp per bp for the last spread, bp per USD trillion for reserves, bp per flagged day for a term; a "
                "term that did not enter a refit counts 0 in the mean, with the share of refits in which it entered beside it).", ""]
        out += fit_table(w["fit"], "0.5") + ["", "At the 95th percentile:", ""] + fit_table(w["fit"], "0.95") + [""]
        if w["skipped_groups"]:
            out += ["Groups of fewer than 20 days, listed and not tested: " + ", ".join(f"{x} ({n_})" for x, n_ in sorted(w["skipped_groups"].items())) + ".", ""]
    if r.get("against_1321"):
        worst = max(v["difference"] for v in r["against_1321"].values())
        out += ["## The references against #1321's record (made at 18:00)", "",
                "(s3c-ann-net), B1, B1' and B2 are re-run here with the same frames and walks; the pooled means equal #1321's to 1e-9 (the run refuses to write "
                f"otherwise). Largest absolute difference: {worst:.1e}.", ""]
    out += question()
    return "\n".join(out).rstrip() + "\n"


def question() -> List[str]:
    return [
        "## Question for Eleonora (marked; the default changes no claim)", "",
        "**Does B4 join the protocol's decision rule, or is it reported beside it?** B4 is added to `repo_model.protocol_benchmarks` (`b4_forecast`) so that the "
        "registration and the live record can score it; nothing in the decision rule of `docs/decisions/scoring-protocol.md` changes in this pull request.", "",
        "**Options** (the default applies if you have not answered by the next 5 pm batch):", "",
        "1. **Reported beside; B1 stays the deciding benchmark** (default, and the recommendation): B4 is scored and shown in every registered test and on the "
        "live record, and the verdict rule is unchanged.",
        "2. **B4 joins the decision rule** as a benchmark the candidate must also beat: a decision record to draft, and the power study (#769) and the minimum "
        "meaningful effect re-set against the harder comparison first.",
        "3. **B4 replaces B1 as the deciding benchmark**: a decision record, and the same re-set.", "",
        "**A second, smaller question: the reserve measure.** B4 reads the reserve balances level because the scarcity state (reserves over bank assets, and ON "
        "RRP) is unknown on every 2026 development day in the measurement panel. Options: (a) **keep the level** (default); (b) draft a directive that adds the "
        "ratio to bank total assets once the H.8 legs are on the 2026 days; (c) read the scarcity state where it is known and the level where it is not."]


def page(args) -> int:
    r = json.loads(Path(args.score).read_text(encoding="utf-8"))
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    Path(args.output).write_text(render(r), encoding="utf-8")
    return 0


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="command", required=True)
    s = sub.add_parser("score", help="walk (s3c-ann-net) and B4 and score them with B1, B1' and B2 on both windows")
    s.add_argument("--panel", required=True)
    s.add_argument("--output", required=True)
    s.add_argument("--draws", type=int, default=sp.DRAWS)
    s.add_argument("--reps", type=int, default=REPS, help="bootstrap resamples of the unstudentized intervals")
    s.add_argument("--workers", type=int, default=4)
    s.add_argument("--windows", nargs="+", choices=WINDOWS, default=None, help="score these windows only (the script's test only; the declared run omits it)")
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
