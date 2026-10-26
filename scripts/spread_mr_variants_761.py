"""Scoring of the mean-reversion variants of #761: context-pooled residuals and the B2 average (H5 step 2; development tier).

A scratch measurement, not a record: it writes JSON and Markdown to the paths it is given and nothing into `docs/runs/`.
Every choice is in `metadata/spread_distribution_761.json`, which this script refuses to read unless it is committed and
unchanged. The variants are `repo_model.spread_mr_variants`, on the base model `repo_model.spread_mean_reversion` (#686).
They are scored with the scorer of scoring protocol v1 (`repo_model.scoring_protocol`, #655) at the development tier,
against B1 and B2 (`repo_model.protocol_benchmarks`), against mean reversion itself, and against the published
distribution on the five levels both forecasts have. The interval is the studentized stationary bootstrap of ruling 1
(#739), not the percentile interval of #686. Scored days are decision days whose five targets are on or before
2025-12-31; no later day is read (`docs/decisions/lockbox.md`). Nothing here is a verdict (scoring protocol v1, #640).

    PYTHONPATH=src python3 -m repo_model.cli build --raw-root tests/fixtures/snapshots/funding_inputs \\
        --output /tmp/funding_panel.csv --build-cutoff 2026-09-08T21:31:42+00:00 --decision-time 16:00:00
    PYTHONPATH=src python3 -m repo_model.cli verify-panel /tmp/funding_panel.csv --manifest metadata/funding_panel_manifest.json
    PYTHONPATH=src python3 scripts/spread_mr_variants_761.py score --panel /tmp/funding_panel.csv \\
        --output docs/pivot/evidence/spread-mr-variants/score.json \\
        --markdown docs/pivot/evidence/spread-mr-variants/report.md
    PYTHONPATH=src python3 scripts/spread_mr_variants_761.py page \\
        --score docs/pivot/evidence/spread-mr-variants/score.json --output docs/pivot/spread-mr-variants-result.md

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


from repo_model import protocol_benchmarks as pb, scoring_protocol as sp  # noqa: E402
from repo_model import spread_mean_reversion as smr, spread_mr_variants as var  # noqa: E402
from repo_model.baseline import panel_sha256  # noqa: E402
from repo_model.data import load_daily_panel  # noqa: E402
from repo_model.domain_intervals import domain_estimates
from repo_model.evaluation_splits import load_split_declaration  # noqa: E402
from repo_model.metrics import _quantile  # noqa: E402
from repo_model.splits import SplitError  # noqa: E402

s686 = _load("spread_mean_reversion_686")

DECLARATION = REPO / "metadata" / "spread_distribution_761.json"
SPLITS = s686.SPLITS
SOURCES = s686.SOURCES
SEED = 761
LAST_DAY = s686.LAST_DAY
DECISION_TIME = s686.DECISION_TIME
MIN_GROUP_DAYS = s686.MIN_GROUP_DAYS
FIVE, FIVE_AT = s686.FIVE, s686.FIVE_AT
INTERVAL = (0.05, 0.95)
REFERENCE = var.REFERENCE
B1RC = "B1_recentred"
#: Every forecast scored, in table order; the first three are benchmarks and reference rows.
MODELS = ("B1", "B2", B1RC, REFERENCE) + var.NAMES
CANDIDATES = (REFERENCE, B1RC) + var.NAMES
STATE_GROUPS = {0.0: "ample", 1.0: "ample", 2.0: "scarce", 3.0: "scarce"}
CONTEXT_LABELS = {"risk_day": "risk day", "ordinary_after_risk": "ordinary after a risk day",
                  "ordinary_after_ordinary": "ordinary after an ordinary day"}


# -- the declaration -----------------------------------------------------------------------------------------------


def committed_declaration(path: Path = DECLARATION) -> dict:
    """The declaration, refused unless it is committed and unchanged since `HEAD`."""

    return s686.committed_declaration(path)


# -- the statistics ------------------------------------------------------------------------------------------------


def studentized_interval(point: float, standard_error: float, t_draws: Sequence[float]) -> List[float]:
    """The two-sided 90% studentized interval: `point - q95 * se` to `point - q05 * se` (ruling 1)."""

    return [point - _quantile(t_draws, INTERVAL[1]) * standard_error, point - _quantile(t_draws, INTERVAL[0]) * standard_error]


def paired_row(test: sp.PairedTest) -> dict:
    """One paired test as the report records it: positive favours the candidate, intervals studentized."""

    return {
        "days": test.n,
        "benchmark_mean": test.benchmark_mean,
        "candidate_mean": test.benchmark_mean - test.mean_difference,
        "difference": test.mean_difference,
        "difference_interval": studentized_interval(test.mean_difference, test.standard_error, test.t_draws),
        "skill": test.skill,
        "skill_interval": studentized_interval(test.skill, test.skill_standard_error, test.skill_t_draws),
        "dm_statistic": None if test.dm_statistic != test.dm_statistic else test.dm_statistic,
        "dm_p_value": None if test.dm_p_value != test.dm_p_value else test.dm_p_value,
    }


def mean_d_row(test: sp.PairedTest, reason: str) -> dict:
    """A paired test made without skill (#1215): the mean-d bound alone, with the reason skill is undefined."""

    return {
        "days": test.n,
        "benchmark_mean": test.benchmark_mean,
        "candidate_mean": test.benchmark_mean - test.mean_difference,
        "difference": test.mean_difference,
        "difference_interval": studentized_interval(test.mean_difference, test.standard_error, test.t_draws),
        "skill": None,
        "skill_interval": None,
        "skill_undefined": reason,
        "dm_statistic": None if test.dm_statistic != test.dm_statistic else test.dm_statistic,
        "dm_p_value": None if test.dm_p_value != test.dm_p_value else test.dm_p_value,
    }


def run_pairs(benchmarks: Mapping[str, Mapping[date, float]], candidate: Mapping[date, float], days: Sequence[date],
              seed: int = SEED, draws: int = sp.DRAWS, mean_d_fallback: bool = False) -> Dict[str, dict]:
    """Each benchmark's paired test against the candidate on `days`, on one resample stream.

    When the joint call raises: with `mean_d_fallback` False every pair is `undefined`, as before. With it True (#1215) each
    pair is retried alone on the same seed (a pair's draws do not depend on the others), with skill; a pair whose skill is
    undefined is retried with `with_skill=False` and keeps its mean-d bound (`skill_interval` None, `skill_undefined` the
    reason). A pair stays `undefined` only when the mean-d bound itself cannot be computed.
    """

    names = list(benchmarks)
    pairs = [({d: benchmarks[n][d] for d in days}, {d: candidate[d] for d in days}) for n in names]
    try:
        return {n: paired_row(t) for n, t in zip(names, sp.paired_tests(pairs, seed=seed, draws=draws))}
    except sp.ProtocolError as error:
        # Undefined where a benchmark scores zero on a resample, or a resample has no long-run variance (a group in
        # which two forecasts score alike on nearly every day). Said so, with the means, instead of a number.
        def undefined(n: str, why: Exception) -> dict:
            return {"undefined": str(why), "days": len(days),
                    "benchmark_mean": sum(benchmarks[n][d] for d in days) / len(days),
                    "candidate_mean": sum(candidate[d] for d in days) / len(days)}

        if not mean_d_fallback:
            return {n: undefined(n, error) for n in names}
        out: Dict[str, dict] = {}
        for n, pair in zip(names, pairs):
            try:
                out[n] = paired_row(sp.paired_tests([pair], seed=seed, draws=draws)[0])
                continue
            except sp.ProtocolError as why:
                skill_reason = str(why)
            try:
                out[n] = mean_d_row(sp.paired_tests([pair], seed=seed, draws=draws, with_skill=False, inner_draws=0)[0], skill_reason)
            except sp.ProtocolError as why:
                out[n] = undefined(n, why)
        return out


def domain_rows(cells: Mapping[object, Tuple[Mapping[date, float], Mapping[date, float], Sequence[date]]], all_days: Sequence[date],
                seed: int = SEED, draws: int = sp.DRAWS, block_length: float = sp.BLOCK_LENGTH, level: float = 0.90) -> Dict[object, dict]:
    """The domain estimate of each group's mean paired difference (#1228), on one stream of whole-series resamples.

    A day-type group is not contiguous (quarter-ends are about three months apart), so `run_pairs` on the group's own days joins days
    that were months apart into one block. Here each cell is `(benchmark scores, candidate scores, the group's days)`; the whole
    aligned series `all_days` is resampled with the pooled test's block, seed and draws (`domain_intervals.domain_estimates`), and
    the statistic is the mean of `d = benchmark - candidate` over the resampled days that belong to the group. The row carries the
    group mean as `difference` and the percentile interval at `level` as `difference_interval` (its lower end is the one-sided 95%
    bound), like `paired_row`, without skill; `method` says "domain". A group some resample draws no day of reads `undefined` with
    the reason, as `run_pairs` does, and its means.

    Raises:
        ValueError: if a group day is not among `all_days`, or a score is missing on a day of `all_days`.
    """

    days = sorted(all_days)
    position = {day: i for i, day in enumerate(days)}
    prepared, series = {}, {}
    for key, (benchmark, candidate, group) in cells.items():
        missing = [day for day in group if day not in position]
        if missing:
            raise ValueError(f"cell {key!r}: {len(missing)} group days ({missing[0]} first) are not among the {len(days)} aligned days")
        series[key] = [benchmark[day] - candidate[day] for day in days]
        prepared[key] = (series[key], [position[day] for day in group])
    done = domain_estimates(prepared, len(days), block_length=block_length, seed=seed, replications=draws, level=level)
    out: Dict[object, dict] = {}
    for key, (benchmark, candidate, group) in cells.items():
        entry = done[key]
        row = {"days": entry["count"], "method": "domain",
               "benchmark_mean": sum(benchmark[d] for d in group) / len(group) if group else None,
               "candidate_mean": sum(candidate[d] for d in group) / len(group) if group else None}
        if "interval" in entry:
            row["difference"] = entry["mean"]
            row["difference_interval"] = [entry["interval"]["lower"], entry["interval"]["upper"]]
        else:
            row["undefined"] = entry.get("interval_unavailable", "the group has no day")
        out[key] = row
    return out


def run_domain(benchmarks: Mapping[str, Mapping[date, float]], candidate: Mapping[date, float], days: Sequence[date],
               all_days: Sequence[date], seed: int = SEED, draws: int = sp.DRAWS, block_length: float = sp.BLOCK_LENGTH,
               level: float = 0.90) -> Dict[str, dict]:
    """`run_pairs` for a non-contiguous group `days`: the domain estimate on whole-series resamples (`domain_rows`)."""

    return domain_rows({n: (benchmarks[n], candidate, days) for n in benchmarks}, all_days, seed=seed, draws=draws,
                       block_length=block_length, level=level)


def skill_text(row: dict) -> str:
    if "undefined" in row:
        return "undefined"
    if row["skill_interval"] is None:
        return "skill undefined"
    lo, hi = row["skill_interval"]
    return f"{pct(row['skill'])} [{pct(lo)}, {pct(hi)}]"


def pct(x: Optional[float], signed: bool = True) -> str:
    return "n/a" if x is None else format(100.0 * x, "+.1f" if signed else ".1f") + "%"


def diff_text(row: dict, places: int = 3) -> str:
    if "undefined" in row:
        return "undefined"
    lo, hi = row["difference_interval"]
    return f"{row['difference']:+.{places}f} [{lo:+.{places}f}, {hi:+.{places}f}]"


def excludes_zero(row: dict) -> bool:
    return "undefined" not in row and row["skill_interval"] is not None and (row["skill_interval"][0] > 0.0 or row["skill_interval"][1] < 0.0)


# -- the frame -----------------------------------------------------------------------------------------------------


def build_frame(panel, splits, registry, declaration, without_day=None):
    """The decision days with a forecast of every model, whose five targets are scored days."""

    frame = s686.Frame(panel, splits, registry, declaration)
    candidate_days = [
        day for i, day in enumerate(frame.dates)
        if i + max(sp.HORIZONS) < len(panel) and frame.dates[i + max(sp.HORIZONS)] <= LAST_DAY
    ]
    s686.require_scored_days(candidate_days, LAST_DAY)
    settings = dict(registry=registry, decision_time=DECISION_TIME, splits=splits)
    b1, b2, rc, dropped = {}, {}, {}, []
    for day in candidate_days:
        index = frame.position[day]
        try:
            b1[day] = pb.b1_forecast(panel, index, registry=registry, decision_time=DECISION_TIME)
            b2[day] = pb.b2_forecast(panel, index, **settings)
            rc[day] = var.b1_recentred_forecast(panel, index, **settings)
        except (sp.ProtocolError, SplitError):
            b1.pop(day, None), b2.pop(day, None)
            dropped.append(day)
    walk = var.walk(panel, candidate_days, b2=b2, **settings)
    days = [day for day in candidate_days if day in b1 and day in b2 and day in rc
            and all(day in walk.forecasts[name] for name in (REFERENCE,) + var.NAMES)]
    frame.walked_days = days
    if without_day is not None:
        # #882 (finding #798): the same scoring on every decision day but one; the day must be a scored one
        days = _load("h5_splits_805").drop_day(days, without_day)
    frame.days = days
    frame.forecasts = {
        name: {day: forecasts[day] for day in days}
        for name, forecasts in (("B1", b1), ("B2", b2), (B1RC, rc), *((n, walk.forecasts[n]) for n in (REFERENCE,) + var.NAMES))
    }
    notes = {
        "decision_days_offered": len(candidate_days),
        "candidate_skipped_for_history": len(walk.skipped),
        "benchmark_missing": [d.isoformat() for d in dropped if d in walk.forecasts[REFERENCE]],
        "scored_decision_days": len(days),
        "first": days[0].isoformat(), "last": days[-1].isoformat(),
        "last_target": frame.target(days[-1], max(sp.HORIZONS)).isoformat(),
        "refits": len(walk.fits),
    }
    return frame, notes, walk


def groupings(frame, states) -> Dict[str, Tuple[str, Dict]]:
    """Each split: its grain ('target' or 'decision') and its labels, a day -> label map or a cell rule."""

    days = frame.days
    targets = sorted({frame.target(d, h) for d in days for h in sp.HORIZONS})
    anchors = {}
    for d in days:
        a = pb._anchor(frame.panel, frame.position[d], frame.registry, DECISION_TIME)
        anchors[d] = frame.splits.reporting_day_type(frame.panel[a].date, frame.panel[a].values)
    return {
        "regime": ("target", {t: frame.regime(t) for t in targets}),
        "pressure_day_type": ("target", {t: frame.day_type(t) for t in targets}),
        "context": ("target", {t: CONTEXT_LABELS[var.target_context(frame.panel, frame.position[t], frame.splits)] for t in targets}),
        "anchor_day_type": ("decision", anchors),
        "scarcity_state": ("cells", {
            (d, h): STATE_GROUPS.get(states[h].get(frame.target(d, h)), "unknown") for d in days for h in sp.HORIZONS}),
    }


# -- the tests, in parallel ----------------------------------------------------------------------------------------

_SERIES: Dict = {}


def _task(job):
    key, metric, candidate, days = job
    series = _SERIES[(key[0], metric)]
    names = ["B1", "B2"] + ([REFERENCE] if candidate in var.NAMES else [])
    return job[:3], run_pairs({n: series[n] for n in names}, series[candidate], days, draws=_SERIES["draws"])


def run_jobs(jobs, workers: int) -> Dict:
    context = multiprocessing.get_context("fork")
    with context.Pool(workers) as pool:
        out = pool.map(_task, jobs, chunksize=1)
    result: Dict = {}
    for (key, metric, candidate), rows in out:
        result.setdefault(key, {}).setdefault(metric, {})[candidate] = rows
    return result


# -- the report ----------------------------------------------------------------------------------------------------


def score(args) -> int:
    declaration = committed_declaration()
    panel_path = Path(args.panel)
    panel = load_daily_panel(panel_path)
    splits = load_split_declaration(SPLITS)
    registry = json.loads(SOURCES.read_text(encoding="utf-8"))
    frame, notes, walk = build_frame(panel, splits, registry, declaration, args.without_day)
    days = frame.days
    draws = args.draws

    # the base model is #686's, exactly
    base = smr.walk(panel, frame.walked_days, registry=registry, decision_time=DECISION_TIME, splits=splits)
    if any(base.forecasts[d] != frame.forecasts[REFERENCE][d] for d in days):
        raise SystemExit("the reference differs from spread_mean_reversion.walk")

    metrics = (("grid_crps", sp.grid_crps), ("upper_tail_twcrps", sp.upper_tail_twcrps))
    cells = {(label, m): s686.cell_scores(frame, m, fn) for label, fn in metrics for m in MODELS}
    for label, fn in metrics:
        for m in MODELS:
            official = sp.day_scores(frame.forecasts[m], frame.outcome, frame.dates, score=fn)
            mine = s686.by_decision(cells[(label, m)])
            if set(official) != set(mine) or any(abs(official[d] - mine[d]) > 1e-9 for d in mine):
                raise SystemExit(f"{label} of {m}: the cell means differ from scoring_protocol.day_scores")

    states = {h: _load("pressure_judge")._scarcity_states(h, LAST_DAY) for h in sp.HORIZONS}
    splits_of = groupings(frame, states)

    # series and groups
    grain_series: Dict[str, Dict] = {}
    for label, _ in metrics:
        grain_series[("decision", label)] = {m: s686.by_decision(cells[(label, m)]) for m in MODELS}
        grain_series[("target", label)] = {m: s686.by_target(frame, cells[(label, m)]) for m in MODELS}
    groups: Dict[Tuple[str, str], Tuple[str, List[date]]] = {("pooled", "all decision days"): ("decision", list(days))}
    cell_groups: Dict[str, Dict[str, set]] = {}
    for split, (grain, labels) in splits_of.items():
        if grain == "cells":
            by_label: Dict[str, set] = {}
            for (d, h), label in labels.items():
                by_label.setdefault(label, set()).add((d, h))
            cell_groups[split] = by_label
            for label, members in by_label.items():
                groups[(split, label)] = ("cells", sorted({d for d, _ in members}))
            continue
        by_label2: Dict[str, List[date]] = {}
        for day in sorted(labels):
            by_label2.setdefault(labels[day], []).append(day)
        for label, members in by_label2.items():
            groups[(split, label)] = (grain, members)
    # a scarcity group's series is the decision day's mean over its leads in the group
    for label_metric, _ in metrics:
        for (split, label), (grain, members) in groups.items():
            if grain != "cells":
                continue
            member_cells = cell_groups[split][label]
            series = {}
            for m in MODELS:
                sums: Dict[date, List[float]] = {}
                for (d, h) in member_cells:
                    sums.setdefault(d, []).append(cells[(label_metric, m)][(d, h)])
                series[m] = {d: sum(v) / len(v) for d, v in sums.items()}
            grain_series[(f"cells:{split}:{label}", label_metric)] = series

    jobs, skipped = [], {}
    for (split, label), (grain, members) in groups.items():
        if len(members) < MIN_GROUP_DAYS:
            skipped[(split, label)] = len(members)
            continue
        key = (grain if grain != "cells" else f"cells:{split}:{label}", f"{split}/{label}")
        for metric, _ in metrics:
            for candidate in CANDIDATES:
                jobs.append((key, metric, candidate, tuple(members)))
    _SERIES.update({k: v for k, v in grain_series.items()})
    _SERIES["draws"] = draws
    # job keys carry the series key first; results are filed under the group label
    results = run_jobs([((k[0], k[1]), m, c, d) for (k, m, c, d) in jobs], args.workers)

    result: dict = {
        "issue": 761, "declaration": str(DECLARATION.relative_to(REPO)), "panel_sha256": panel_sha256(panel_path),
        "label": "development, not a verdict", "seed": SEED, "draws": draws, "notes": notes,
        "refits": [{"fitted_on": day.isoformat(), "phi": fit.base.phi,
                    "own_pool": {str(h): list(fit.own_pool[h]) for h in sp.HORIZONS},
                    "pool_sizes": {str(h): fit.sizes[h] for h in sp.HORIZONS},
                    "weights": walk.weights[day]} for day, fit in sorted(walk.fits.items())],
        "means": {label: {m: sum(grain_series[("decision", label)][m].values()) / len(days) for m in MODELS} for label, _ in metrics},
        "groups": {}, "skipped_groups": {f"{s}/{l}": n for (s, l), n in skipped.items()},
    }
    for (key, name), by_metric in results.items():
        split, label = name.split("/", 1)
        series_key = key
        entry = {"days": len(groups[(split, label)][1])}
        for metric, per_candidate in by_metric.items():
            ser = _SERIES[(series_key, metric)]
            members = list(groups[(split, label)][1])
            entry[metric] = {"means": {m: sum(ser[m][d] for d in members) / len(members) for m in MODELS},
                             "vs": per_candidate}
        result["groups"].setdefault(split, {})[label] = entry

    # the tail
    tails = {m: s686.tail_cells(frame, m) for m in MODELS}
    contexts = {t: var.target_context(panel, frame.position[t], splits) for t in {frame.target(d, h) for d in days for h in sp.HORIZONS}}
    # the reporting day type, a third population the risk-date reconciliation names and leaves alone
    def reporting_ordinary(t):
        return frame.splits.reporting_day_type(t, frame.values[t]) == "ordinary"

    scopes = {
        "ordinary": lambda d, h, t: reporting_ordinary(t),
        "calm": lambda d, h, t: reporting_ordinary(t) and contexts[t] == "ordinary_after_ordinary",
        "after_risk": lambda d, h, t: reporting_ordinary(t) and contexts[t] == "ordinary_after_risk",
        "risk_day": lambda d, h, t: contexts[t] == "risk_day",
        "all": lambda d, h, t: True,
    }
    result["tail"] = {"tau_bp": smr.TAIL_TAU, "reading": declaration["tail"]["reading"], "by_regime": {}}
    regimes = [r for r in splits.regime_labels if any(frame.regime(t) == r for t in contexts)]
    for scope, select in scopes.items():
        result["tail"]["by_regime"][scope] = {}
        for regime in regimes + ["all regimes"]:
            rule = (lambda d, h, t, s=select, r=regime: s(d, h, t) and (r == "all regimes" or frame.regime(t) == r))
            result["tail"]["by_regime"][scope][regime] = s686.reliability(frame, tails, rule)

    # the published distribution, on its five levels
    published = s686.read_published()
    five = {m: s686.five_level_cells(frame, frame.forecasts[m], days) for m in MODELS}
    pub = s686.published_cells(frame, published, days)
    complete = [d for d in days if all((d, h) in pub for h in sp.HORIZONS)]
    pub_decision = s686.by_decision({k: v for k, v in pub.items() if k[0] in set(complete)})
    result["published"] = {
        "levels": list(FIVE), "days": len(complete), "days_without_five_published_leads": len(days) - len(complete),
        "means": {"published": sum(pub_decision.values()) / len(complete),
                  **{m: sum(s686.by_decision(five[m])[d] for d in complete) / len(complete) for m in CANDIDATES}},
        "candidate_vs": {m: run_pairs({"published": pub_decision}, {d: s686.by_decision(five[m])[d] for d in complete},
                                      complete, draws=draws)["published"] for m in CANDIDATES},
    }

    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    Path(args.output).write_text(json.dumps(result, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    if args.markdown:
        Path(args.markdown).parent.mkdir(parents=True, exist_ok=True)
        Path(args.markdown).write_text(render_report(result), encoding="utf-8")
    return 0


# -- Markdown ------------------------------------------------------------------------------------------------------

LABELS = {REFERENCE: "mean reversion (#686)", B1RC: "B1 recentred (#741; reference)", "spread_mr_ctx": "(i) context-pooled residuals",
          "spread_mr_b2": "(ii) average with B2", "spread_mr_ctx_b2": "(iii) both", "B1": "B1", "B2": "B2"}
SPLIT_TITLES = {"regime": "regime (target day)", "pressure_day_type": "pressure-day type (target day)",
                "context": "context of the target day", "anchor_day_type": "anchor day type (decision)",
                "scarcity_state": "as-of scarcity state (decision, by the leads in the state)"}
ORDER = {"regime": ["2018-19", "2020", "2021-23", "2024", "2025-26"]}


def _ordered(split: str, labels) -> List[str]:
    order = ORDER.get(split, [])
    return [l for l in order if l in labels] + sorted(l for l in labels if l not in order)


def render_report(r: dict) -> str:
    n = r["notes"]
    out = [
        "# Mean-reversion variants: context-pooled residuals and the B2 average (#761)", "",
        f"Generated by `scripts/spread_mr_variants_761.py score` from `{r['declaration']}`; not edited by hand. "
        f"**{r['label']}**: development days to {n['last_target']}, no verdict (scoring protocol v1, #640). Panel digest "
        f"`{r['panel_sha256'][:8]}…`. Studentized stationary bootstrap (ruling 1), mean block {sp.BLOCK_LENGTH} business days, "
        f"{r['draws']:,} draws, seed {r['seed']}; the interval is skill less the 95th and 5th percentile of its studentized draws "
        "times its HAC standard error (a two-sided 90% interval). Skill is `mean(d) / mean(S(benchmark))` with "
        "`d = S(benchmark) - S(candidate)`: positive favours the candidate.", "",
        f"Scored decision days: {n['scored_decision_days']:,} ({n['first']} to {n['last']}; the last target is {n['last_target']}). "
        f"Mean reversion has no forecast on {n['candidate_skipped_for_history']} early days (history), and a benchmark is missing on "
        f"{len(n['benchmark_missing'])}. The fit is renewed {n['refits']} times (every {smr.REFIT_EVERY} decision days).", ""]
    for metric, title in (("grid_crps", "Grid CRPS (23 levels), mean over leads 1 to 5"),
                          ("upper_tail_twcrps", "Upper-tail twCRPS (weight 1{z > 0 bp})")):
        out += [f"## {title}, one number per decision day", "",
                "| | mean bp | vs B1: skill [90%] | vs B2: skill [90%] | vs mean reversion: skill [90%] |", "|---|---|---|---|---|"]
        out += _rows(r["groups"]["pooled"]["all decision days"][metric], ("B1", "B2"))
        out.append("")
    for split in ("regime", "pressure_day_type", "context", "anchor_day_type", "scarcity_state"):
        for metric, title in (("grid_crps", "grid CRPS"), ("upper_tail_twcrps", "upper-tail twCRPS")):
            out += [f"## {title} by {SPLIT_TITLES[split]}", ""]
            for label in _ordered(split, r["groups"].get(split, {})):
                cell = r["groups"][split][label]
                out += [f"**{label}** ({cell['days']} days)", "",
                        "| | mean bp | vs B1 [90%] | vs B2 [90%] | vs mean reversion [90%] |", "|---|---|---|---|---|"]
                out += _rows(cell[metric], ("B1", "B2"))
                out.append("")
    if r["skipped_groups"]:
        out += ["Groups with fewer than %d days are listed and not tested: %s." % (
            MIN_GROUP_DAYS, ", ".join(f"{k} ({v})" for k, v in sorted(r["skipped_groups"].items()))), ""]
    out += ["## P(spread > +5 bp): reliability, read off each distribution", "",
            f"Mean predicted probability, realised share of target days above +{r['tail']['tau_bp']:g} bp (whole basis points, "
            "strictly above) and realised minus predicted: negative means the model over-forecasts the tail. Pooled over leads 1 to 5."]
    titles = {"ordinary": "Ordinary target days", "calm": "Calm: ordinary after an ordinary day",
              "after_risk": "Ordinary after a risk day", "risk_day": "Risk days (context)", "all": "All target days"}
    shown = ("B1", "B2", REFERENCE) + var.NAMES
    for scope, title in titles.items():
        out += ["", f"{title}:", "", "| regime | cells | " + " | ".join(LABELS[m] for m in shown) + " |", "|---|---|" + "---|" * len(shown)]
        for regime, cell in r["tail"]["by_regime"][scope].items():
            if cell["B1"] is None:
                continue
            parts = ["%.3f / %.3f / %+.3f" % (cell[m]["predicted"], cell[m]["realised"], cell[m]["realised_minus_predicted"]) for m in shown]
            out.append("| %s | %d | %s |" % (regime, cell["B1"]["cells"], " | ".join(parts)))
    out += ["", "Each cell is predicted / realised / realised minus predicted.", ""]
    pub = r["published"]
    out += ["## The published distribution, on its five levels", "",
            f"Decision days with all five published leads: {pub['days']:,}. Each side is scored on the five levels both have; "
            "the candidate is read at its own quantiles at those levels. Mean over the five leads per decision day, paired.", "",
            "| | five-level CRPS bp | skill against the published distribution [90%] |", "|---|---|---|",
            "| published | %.3f | |" % pub["means"]["published"]]
    for m in CANDIDATES:
        out.append("| %s | %.3f | %s |" % (LABELS[m], pub["means"][m], skill_text(pub["candidate_vs"][m])))
    out += ["", "## The fit", ""]
    fits = r["refits"]
    phis = [f["phi"] for f in fits]
    out += [f"phi is refitted {len(fits)} times; it ranges from {min(phis):.2f} to {max(phis):.2f}. The weight on mean reversion, "
            "chosen at each refit:", "", "| weight | (ii) average with B2: refits | (iii) both: refits |", "|---|---|---|"]
    for w in var.WEIGHT_GRID:
        a = sum(1 for f in fits if f["weights"]["spread_mr_b2"] == w)
        b = sum(1 for f in fits if f["weights"]["spread_mr_ctx_b2"] == w)
        out.append(f"| {w:.1f} | {a} | {b} |")
    thin = [(f["fitted_on"], h, c) for f in fits for h in map(str, sp.HORIZONS) for c in var.CONTEXTS if c not in f["own_pool"][h]]
    out += ["", f"Context pools that fell back to the pooled residuals (lead, context) over the {len(fits)} refits: {len(thin)} of {len(fits) * 5 * len(var.CONTEXTS)}.", ""]
    return "\n".join(out)


def _rows(cell: dict, benchmarks) -> List[str]:
    out = []
    means = cell["means"]
    for m in ("B1", "B2"):
        out.append("| %s | %.3f | | | |" % (LABELS[m], means[m]))
    for m in CANDIDATES:
        vs = cell["vs"][m]
        ref = skill_text(vs[REFERENCE]) if REFERENCE in vs else ""
        out.append("| %s | %.3f | %s | %s | %s |" % (LABELS[m], means[m], skill_text(vs["B1"]), skill_text(vs["B2"]), ref))
    return out


def loses(r: dict, name: str) -> List[str]:
    """Groups of grid CRPS where a variant's point estimate is below mean reversion's, with the interval's verdict."""

    out = []
    for split in ("regime", "pressure_day_type", "context", "anchor_day_type", "scarcity_state"):
        for label in _ordered(split, r["groups"].get(split, {})):
            row = r["groups"][split][label]["grid_crps"]["vs"][name][REFERENCE]
            if "undefined" in row or row["skill"] is None or row["skill"] >= 0.0:
                continue
            tag = "" if not excludes_zero(row) else ", interval excludes 0"
            out.append(f"{label} ({split.replace('_', ' ')}) {pct(row['skill'])} [{pct(row['skill_interval'][0])}, {pct(row['skill_interval'][1])}]{tag}")
    return out


def page(args) -> int:
    r = json.loads(Path(args.score).read_text(encoding="utf-8"))
    n = r["notes"]
    pooled = r["groups"]["pooled"]["all decision days"]
    g, t = pooled["grid_crps"], pooled["upper_tail_twcrps"]
    lines = [
        "# Mean-reversion variants: result (#761)", "",
        "**Hypothesis and step:** H5 (primary goal), research step 2, the same step as #686. **Development data only: this is not a verdict** "
        "(scoring protocol v1, #640). Generated by `scripts/spread_mr_variants_761.py page`; the evidence is in "
        "`docs/pivot/evidence/spread-mr-variants/`. The interval is the studentized stationary bootstrap (ruling 1, #739), 90% two-sided.", "",
        "Three variants of `spread_mr_level10` (#686): (i) residuals pooled by the target day's context (a risk day; an ordinary day after "
        "a risk day; an ordinary day after an ordinary day); (ii) a quantile average of mean reversion and B2, the weight chosen at each refit on "
        "trailing scored days; (iii) both (`metadata/spread_distribution_761.json`).", "",
        f"| grid CRPS, {n['scored_decision_days']:,} decision days to {n['last_target']} | mean bp | skill vs B1 [90%] | skill vs B2 [90%] | skill vs mean reversion [90%] |",
        "|---|---|---|---|---|"]
    lines += _rows(g, ("B1", "B2"))
    lines += ["", "| upper-tail twCRPS | mean bp | skill vs B1 [90%] | skill vs B2 [90%] | skill vs mean reversion [90%] |", "|---|---|---|---|---|"]
    lines += _rows(t, ("B1", "B2"))
    lines += ["", "The splits (regime with 2021-23 called out, pressure-day type, as-of scarcity state, anchor day type, context), the reliability of "
              "P(spread > +5 bp) on ordinary days (calm and after a risk day), the comparison with the published distribution and the fitted weights "
              "are in `docs/pivot/evidence/spread-mr-variants/report.md`.", "", "## Per variant: gain over mean reversion, and where it loses", ""]
    for name in var.NAMES:
        row = g["vs"][name][REFERENCE]
        lost = loses(r, name)
        lines.append("- **%s**: grid CRPS gain over mean reversion %s. %s" % (
            LABELS[name], skill_text(row), ("Loses (point estimate below mean reversion) in: " + "; ".join(lost) + ".") if lost else "Loses in no group."))
    lines += ["", "Development, not a verdict.", ""]
    Path(args.output).write_text("\n".join(lines), encoding="utf-8")
    return 0


from repo_model import turn_days  # noqa: E402


@turn_days.with_legacy_flag
def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="command", required=True)
    s = sub.add_parser("score", help="score the variants against B1, B2, mean reversion and the published distribution")
    s.add_argument("--panel", required=True)
    s.add_argument("--output", required=True)
    s.add_argument("--markdown")
    s.add_argument("--draws", type=int, default=sp.DRAWS)
    s.add_argument("--without-day", type=date.fromisoformat, default=None, help="leave this decision day out of every window (#882)")
    s.add_argument("--workers", type=int, default=4)
    s.set_defaults(func=score)
    g = sub.add_parser("page", help="write the short result page from a score file")
    g.add_argument("--score", required=True)
    g.add_argument("--output", required=True)
    g.set_defaults(func=page)
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
