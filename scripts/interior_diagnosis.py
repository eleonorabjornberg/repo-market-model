"""Why the published distribution's interior is miscalibrated, and the fix (#247).

Stage 1 of pressure model v2: a diagnosis, descriptive. It changes no model,
no published record and nothing the live record logs. The published
distribution is #169's gbm with nested conformal PID (`live_record._compare_sides`),
walked as the final test walks it (`final_test_opening.distribution_walk`) on
the published panel, every scored day kept with its five quantiles.

Two subcommands:

* `walk`: one walk at one horizon. `--variant v1` is the published
  distribution unchanged; every other variant (`VARIANTS`) holds the features,
  the as-of fold grid, the refit cadence and the nested PID fixed and changes
  one setting of the trees. Each day keeps the trees' own vector (before PID,
  `raw`), the vector PID issued (`issued`), the anchor its labels are observable
  at, the outcome, and whether the five fits crossed before rearrangement. At
  h = 1 each refit also keeps its in-sample tallies: the fitted model read on
  its own training pairs.
* `assemble`: the record, `docs/runs/v1_interior_diagnosis.json`, from the
  walks. It checks first that v1's per-day CRPS at h = 1 reproduces the
  published CRPS record and `final_test_near_blind.json` exactly
  (`reproduction_check`), then answers the directive's seven questions, scores
  the candidates of question 7 and applies the selection rule (`SELECTION_RULE`,
  `select_candidate`), which was declared in this file before any candidate was
  scored.

The diagnosis window is 2018-06-29 to 2025-12-31 (`DIAGNOSIS`). January to
September 2026 is opened history (`docs/decisions/lockbox.md`) and is reported
separately (`OPENED`); nothing is concluded from it alone, and no day after
2026-09-03 is read.

    OMP_NUM_THREADS=1 PYTHONPATH=src /opt/rmm-venv/bin/python scripts/interior_diagnosis.py walk \\
        --panel PUB.csv --horizon H --variant NAME --output OUT/walk_NAME_hH.json
    PYTHONPATH=src python3 scripts/interior_diagnosis.py assemble --panel PUB.csv \\
        --walks OUT/walk_*.json --output docs/runs/v1_interior_diagnosis.json
"""

from __future__ import annotations

import argparse
import bisect
import importlib.util
import json
import math
import random
import statistics
import sys
from datetime import date
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))

from repo_model import onset  # noqa: E402
from repo_model.baseline import _split_labels, panel_sha256, split_document  # noqa: E402
from repo_model.data import audit_panel, load_daily_panel  # noqa: E402
from repo_model.evaluation_splits import load_split_declaration  # noqa: E402
from repo_model.metrics import crps_from_quantiles  # noqa: E402


def _script(name):
    spec = importlib.util.spec_from_file_location(f"diagnosis_{name}", REPO / "scripts" / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


fto = _script("final_test_opening")
fp = fto.fp

HORIZONS = (1, 2, 3, 4, 5)
LEVELS = (0.05, 0.25, 0.5, 0.75, 0.95)
INTERIOR = (1, 2, 3)
DIAGNOSIS = (date(2018, 6, 29), date(2025, 12, 31))
OPENED = (date(2026, 1, 2), date(2026, 9, 3))
LAST_READ = date(2026, 9, 3)
RECORD = REPO / "docs" / "runs" / "v1_interior_diagnosis.json"
BLOCK_LENGTH = fp.CRPS_BLOCK_LENGTH
SIGN = ("paired = CRPS(v1) - CRPS(candidate) per day; a positive mean favours the candidate")

#: Question 4: the trees' settings, one at a time, features held fixed. The
#: published trees are scikit-learn's `HistGradientBoostingRegressor` defaults
#: (learning rate 0.1, 100 iterations, no depth limit, 31 leaves, every feature)
#: with `min_samples_leaf=20`. That estimator has no row subsampling; its
#: subsampling setting is `max_features`, the share of features each split may
#: consider, and that is what "subsampling" varies here.
VARIANTS = {
    "v1": {},
    "min_samples_leaf_50": {"min_samples_leaf": 50},
    "min_samples_leaf_100": {"min_samples_leaf": 100},
    "min_samples_leaf_200": {"min_samples_leaf": 200},
    "max_depth_2": {"max_depth": 2},
    "max_depth_3": {"max_depth": 3},
    "learning_rate_0.05_iter_100": {"learning_rate": 0.05, "max_iter": 100},
    "learning_rate_0.05_iter_200": {"learning_rate": 0.05, "max_iter": 200},
    "learning_rate_0.02_iter_250": {"learning_rate": 0.02, "max_iter": 250},
    "max_features_0.8": {"max_features": 0.8},
    "max_features_0.5": {"max_features": 0.5},
}
SETTING_OF = {
    "min_samples_leaf": "minimum samples per leaf",
    "max_depth": "maximum depth",
    "learning_rate": "learning rate with number of trees",
    "max_features": "subsampling (features per split)",
}

# ---------------------------------------------------------------------------
# The selection rule, declared before question 7 is scored.
# ---------------------------------------------------------------------------

#: Coverage of a quantile is the share of outcomes below it, an outcome exactly
#: on it counting one half ("half-tie"); a band's coverage is the share strictly
#: inside it, an outcome exactly on an edge counting one half. SOFR - IORB
#: prints in whole basis points and the trees' quantiles are often whole basis
#: points too, so "at or below" alone counts every tie as a hit (`coverage`
#: reports both).
SELECTION_RULE = {
    "window": "2018-06-29 to 2025-12-31, h = 1",
    "coverage": "half-tie: an outcome exactly on a quantile counts one half",
    "bar": {
        "levels": [0.25, 0.5, 0.75],
        "tolerance_points": 5.0,
        "band_90": [87.0, 93.0],
    },
    "order": [
        "eligible: coverage at 25, 50 and 75% each within 5 points of target, and the 90% "
        "band's coverage within 87-93%",
        "leader: the eligible candidate with the lowest mean CRPS",
        "a simpler eligible candidate whose paired CRPS difference against the leader has "
        "a 90% interval including 0 is preferred to it; among several, the simplest, then "
        "the lowest CRPS",
        "simplicity ranks by layers added to v1, then fixing the cause (the trees) before "
        "patching the output (`COMPLEXITY`)",
        "if no candidate is eligible, none is recommended and #244 does not start",
    ],
}
#: (layers added to v1, patches the output): lower is simpler.
COMPLEXITY = {
    "ii_regularised_trees": (1, 0),
    "i_interior_tracking": (1, 1),
    "iii_residual_law": (1, 1),
    "iii_residual_law_scaled": (2, 1),
    "iv_regularised_and_tracking": (2, 1),
}
CANDIDATES = tuple(COMPLEXITY)

#: (i): per-level online quantile tracking of the interior levels, its step
#: chosen by nested walk-forward selection as the PID's is (#125): at the first
#: scored day of each block of `REFIT_EVERY` days, the step with the least
#: pooled CRPS over the days whose labels were observable at that day's anchor.
TRACKING_STEPS = (0.01, 0.05, 0.1, 0.2)
TRACKING_FALLBACK = 0.05
REFIT_EVERY = fp.REFIT_EVERY
#: (iii): the centre is v1's median; the quantiles are its trailing out-of-fold
#: residuals' empirical quantiles, `RESIDUAL_WINDOW` labels observable at the
#: anchor, and v1's own vector while fewer than `RESIDUAL_MINIMUM` are.
RESIDUAL_WINDOW = 250
RESIDUAL_MINIMUM = 60
#: (iii, scaled): each residual divided by the trailing root-mean-square of the
#: spread's daily changes over `VOLATILITY_DAYS` observable days, floored.
VOLATILITY_DAYS = 20
VOLATILITY_FLOOR = 0.5


def eligible(summary: dict) -> bool:
    """A candidate meets the bar: interior coverage within tolerance, 90% band in range."""

    bar = SELECTION_RULE["bar"]
    for level in bar["levels"]:
        target = 100.0 * level
        if abs(summary["coverage_half_tie"][str(level)] - target) > bar["tolerance_points"]:
            return False
    low, high = bar["band_90"]
    return low <= summary["band_90_half_edge"] <= high


def select_candidate(summaries: dict, paired_to_leader) -> dict:
    """`SELECTION_RULE`, applied.

    `summaries` maps a candidate to its window summary (`coverage_half_tie`,
    `band_90_half_edge`, `crps`). `paired_to_leader(name, leader)` returns the
    paired CRPS difference of `name` against `leader` (`{"interval": {"lower",
    "upper"}}`). Returns the choice and why.
    """

    unknown = set(summaries) - set(COMPLEXITY)
    if unknown:
        raise ValueError(f"no complexity is declared for {sorted(unknown)}")
    passing = sorted(name for name in summaries if eligible(summaries[name]))
    if not passing:
        return {"recommended": None, "eligible": [], "leader": None,
                "reason": "no candidate meets the bar; #244 does not start"}
    leader = min(passing, key=lambda name: (summaries[name]["crps"], COMPLEXITY[name], name))
    simpler = []
    for name in passing:
        if COMPLEXITY[name] >= COMPLEXITY[leader]:
            continue
        interval = paired_to_leader(name, leader)["interval"]
        if interval["lower"] <= 0.0 <= interval["upper"]:
            simpler.append(name)
    if simpler:
        chosen = min(simpler, key=lambda name: (COMPLEXITY[name], summaries[name]["crps"], name))
        reason = (f"{leader} has the lowest CRPS of the eligible candidates; {chosen} is "
                  f"simpler and its CRPS difference against {leader} has a 90% interval "
                  f"including 0")
    else:
        chosen = leader
        reason = (f"{leader} has the lowest CRPS of the eligible candidates, and no simpler "
                  f"eligible candidate is within its interval")
    return {"recommended": chosen, "eligible": passing, "leader": leader, "reason": reason}


# ---------------------------------------------------------------------------
# Measures
# ---------------------------------------------------------------------------


def below(value: float, quantile: float, *, half_tie: bool) -> float:
    if value < quantile:
        return 1.0
    if value == quantile:
        return 0.5 if half_tie else 1.0
    return 0.0


def inside(value: float, low: float, high: float, *, mode: str) -> float:
    """1 inside the band; an outcome on an edge counts by `mode` (closed, open, half)."""

    if low < value < high:
        return 1.0
    if value == low or value == high:
        if low == high:
            return {"closed": 1.0, "open": 0.0, "half": 0.5}[mode]
        return {"closed": 1.0, "open": 0.0, "half": 0.5}[mode]
    return 0.0


def pit_bins(vector, value):
    """The outcome's place among the five quantiles, as six bin weights.

    Bins are [0, .05), [.05, .25), [.25, .5), [.5, .75), [.75, .95), [.95, 1].
    An outcome strictly between two quantiles falls in one bin. An outcome equal
    to one or more quantiles has a PIT anywhere between the lowest and highest
    of their levels (a single tied quantile: its level exactly), and its weight
    is spread over the bins that range covers in proportion to their width, a
    single level split half and half: the expectation of the randomised PIT.
    """

    edges = (0.0,) + LEVELS + (1.0,)
    lower = sum(1 for q in vector if q < value)
    upper = sum(1 for q in vector if q <= value)
    weights = [0.0] * 6
    if lower == upper:
        weights[lower] = 1.0
        return weights
    a, b = LEVELS[lower], LEVELS[upper - 1]
    if a == b:
        weights[lower] += 0.5
        weights[lower + 1] += 0.5
        return weights
    for k in range(6):
        overlap = max(0.0, min(b, edges[k + 1]) - max(a, edges[k]))
        weights[k] += overlap / (b - a)
    return weights


def pit_draw(vector, value, rng: random.Random) -> int:
    """One randomised PIT bin, drawn from `pit_bins`' weights."""

    weights = pit_bins(vector, value)
    u = rng.random()
    total = 0.0
    for k, w in enumerate(weights):
        total += w
        if u < total:
            return k
    return 5


def coverage(days, field="issued") -> dict:
    """Per-level and band coverage of `days`' `field` vectors, in percent."""

    n = len(days)
    if not n:
        return {"days": 0}
    vectors = [d[field] for d in days]
    ys = [d["y"] for d in days]

    def pct(total):
        return 100.0 * total / n

    out = {
        "days": n,
        "coverage_at_or_below": {str(level): pct(sum(below(y, v[i], half_tie=False)
                                                     for v, y in zip(vectors, ys)))
                                 for i, level in enumerate(LEVELS)},
        "coverage_half_tie": {str(level): pct(sum(below(y, v[i], half_tie=True)
                                                  for v, y in zip(vectors, ys)))
                              for i, level in enumerate(LEVELS)},
        "outcome_equals_quantile": {str(level): pct(sum(1 for v, y in zip(vectors, ys) if y == v[i]))
                                    for i, level in enumerate(LEVELS)},
    }
    for name, (lo, hi) in (("band_50", (1, 3)), ("band_90", (0, 4))):
        for mode in ("closed", "open", "half"):
            out[f"{name}_{'half_edge' if mode == 'half' else mode}"] = pct(
                sum(inside(y, v[lo], v[hi], mode=mode) for v, y in zip(vectors, ys)))
        out[f"{name}_miss_below"] = pct(sum(1 for v, y in zip(vectors, ys) if y < v[lo]))
        out[f"{name}_miss_above"] = pct(sum(1 for v, y in zip(vectors, ys) if y > v[hi]))
        out[f"{name}_mean_width_bps"] = statistics.fmean(v[hi] - v[lo] for v in vectors)
    return out


def jittered_band_50(days, seed) -> float:
    """50% band coverage with each whole-bp outcome spread uniformly over its +-0.5 bp."""

    rng = random.Random(seed)
    hits = 0
    for d in days:
        y = d["y"]
        if y == round(y):
            y = y + rng.random() - 0.5
        hits += 1 if d["issued"][1] <= y <= d["issued"][3] else 0
    return 100.0 * hits / len(days) if days else None


def pit_histogram(days, field, seed) -> dict:
    n = len(days)
    expected = [100.0 * w for w in (0.05, 0.20, 0.25, 0.25, 0.20, 0.05)]
    weights = [0.0] * 6
    rng = random.Random(seed)
    drawn = [0] * 6
    for d in days:
        for k, w in enumerate(pit_bins(d[field], d["y"])):
            weights[k] += w
        drawn[pit_draw(d[field], d["y"], rng)] += 1
    labels = ["0-5", "5-25", "25-50", "50-75", "75-95", "95-100"]
    return {
        "bins": labels,
        "target_percent": expected,
        "expected_randomised_percent": [100.0 * w / n for w in weights] if n else None,
        "one_randomised_draw_percent": [100.0 * c / n for c in drawn] if n else None,
        "seed": seed,
    }


def location_and_spread(days) -> dict:
    """Question 2: is the centre biased, the band too narrow, or both?"""

    residuals = [d["y"] - d["issued"][2] for d in days]
    widths = [d["issued"][3] - d["issued"][1] for d in days]
    shift = statistics.median(residuals)
    recentred = [dict(d, issued=[q + shift if i in INTERIOR else q for i, q in enumerate(d["issued"])])
                 for d in days]
    # The constant factor on each day's half-widths, about its re-centred median,
    # at which the 50% band would cover half the window (descriptive, in-window).
    ratios = []
    for d, r in zip(days, residuals):
        lo, mid, hi = d["issued"][1], d["issued"][2], d["issued"][3]
        e = r - shift
        half = (hi - mid) if e >= 0 else (mid - lo)
        ratios.append(math.inf if half <= 0 and e != 0 else (0.0 if e == 0 else abs(e) / half))
    finite = sorted(ratios)
    factor = finite[len(finite) // 2]
    cov = coverage(days)
    return {
        "days": len(days),
        "mean_outcome_minus_q50_bps": statistics.fmean(residuals),
        "median_outcome_minus_q50_bps": shift,
        "share_outcome_below_q50": cov["coverage_at_or_below"]["0.5"] - cov["outcome_equals_quantile"]["0.5"],
        "share_outcome_equal_q50": cov["outcome_equals_quantile"]["0.5"],
        "share_outcome_above_q50": 100.0 - cov["coverage_at_or_below"]["0.5"],
        "band_50_miss_below": cov["band_50_miss_below"],
        "band_50_miss_above": cov["band_50_miss_above"],
        "miss_asymmetry_points": cov["band_50_miss_below"] - cov["band_50_miss_above"],
        "band_50_mean_width_bps": statistics.fmean(widths),
        "band_50_median_width_bps": statistics.median(widths),
        "share_band_50_zero_width": 100.0 * sum(1 for w in widths if w == 0) / len(widths),
        "outcome_iqr_about_q50_bps": _iqr(residuals),
        "recentred_by_window_median": {
            "shift_bps": shift,
            "band_50_half_edge": coverage(recentred)["band_50_half_edge"],
            "note": "descriptive: the window's own median residual, which no forecast could know",
        },
        "widening_factor_for_50pct_after_recentring": factor,
    }


def _iqr(values):
    ordered = sorted(values)
    q = statistics.quantiles(ordered, n=4, method="inclusive")
    return q[2] - q[0]


# ---------------------------------------------------------------------------
# The walk
# ---------------------------------------------------------------------------

_CROSSINGS = []


def _instrument_rearrangement(ml):
    """Count crossed rows each time the trees' five fits are read (descriptive only)."""

    original = ml._rearranged

    def counted(estimators, design_rows):
        rows = [[float(value) for value in row] for row in design_rows]
        columns = [[float(v) for v in e.predict(rows)] for e in estimators]
        crossed = sum(1 for k in range(len(rows))
                      if any(columns[i][k] > columns[i + 1][k] for i in range(len(columns) - 1)))
        _CROSSINGS.append((len(rows), crossed))
        return original(estimators, design_rows)

    ml._rearranged = counted


def _with_tree_settings(ml, settings):
    if not settings:
        return
    estimator = ml._estimator_class()

    def make(**kwargs):
        kwargs.update(settings)
        return estimator(**kwargs)

    ml._estimator_class = lambda: make


class _Recorder:
    """The nested PID, unchanged, with each day's vector before it is moved."""

    def __init__(self, inner, log):
        self._inner = inner
        self._log = log

    def __getattr__(self, name):
        return getattr(self._inner, name)

    def view(self, view, index, feature_row):
        _CROSSINGS.clear()
        raw = [float(v) for v in view.predict(feature_row)]
        crossed = sum(c for _, c in _CROSSINGS)
        self._log[index] = {"raw": raw, "anchor": feature_row.date.isoformat(),
                            "crossed": bool(crossed)}
        return self._inner.view(view, index, feature_row)

    def label(self, index, value):
        return self._inner.label(index, value)


def _in_sample(fitted, frame) -> dict:
    """The fitted trees read on their own one-step training pairs (h = 1)."""

    tallies = {"pairs": 0, "half_tie": [0.0] * 5, "band_50_half_edge": 0.0, "band_90_half_edge": 0.0,
               "band_50_closed": 0.0}
    for k in range(1, len(frame)):
        y = frame[k].spread_bps
        if y is None:
            continue
        try:
            v = [float(q) for q in fitted.predict(frame[k - 1])]
        except Exception:  # a training row the model cannot read is not a pair it was fitted on
            continue
        tallies["pairs"] += 1
        for i in range(5):
            tallies["half_tie"][i] += below(y, v[i], half_tie=True)
        tallies["band_50_half_edge"] += inside(y, v[1], v[3], mode="half")
        tallies["band_50_closed"] += inside(y, v[1], v[3], mode="closed")
        tallies["band_90_half_edge"] += inside(y, v[0], v[4], mode="half")
    return tallies


def walk_command(args) -> int:
    from repo_model import ml

    h, variant = args.horizon, args.variant
    if variant != "v1" and h != 1:
        raise ValueError("the settings variants are walked at h = 1 only")
    rows = load_daily_panel(args.panel)
    audit_panel(rows)
    if panel_sha256(args.panel) != fp._frozen_panel_sha256():
        raise ValueError("the panel is not the published panel")
    if rows[-1].date > LAST_READ:
        raise ValueError(f"the panel runs past {LAST_READ}")
    lr = fto._script("live_record")
    fto.live_record = lr
    registry = json.loads(fp.REGISTRY.read_text())
    sides, parsed = lr._compare_sides(h)
    name, fit, features, online = sides["published"]
    _instrument_rearrangement(ml)
    _with_tree_settings(ml, VARIANTS[variant])
    log, refits = {}, []

    def recorded(rows_, rule):
        return _Recorder(online(rows_, rule), log)

    def fit_and_keep(train_frame, *, minimum_history, information):
        fitted = fit(train_frame, minimum_history=minimum_history, information=information)
        if h == 1 and not args.no_in_sample:
            refits.append({"train_end": train_frame[-1].date.isoformat(),
                           **_in_sample(fitted, train_frame)})
        return fitted

    walk, levels, settings = fto.distribution_walk(
        rows, fit=fit_and_keep, features=features, online_calibration=recorded,
        registry=registry, horizon=h, minimum_history=parsed.minimum_history,
        refit_every=parsed.refit_every,
    )
    if variant == "v1":
        lr._require_crps_declaration("published", h, name, features, settings)
    if tuple(levels) != LEVELS:
        raise ValueError(f"levels {levels}")
    days = []
    for index, issued in walk:
        entry = log[index]
        days.append({"date": rows[index].date.isoformat(), "anchor": entry["anchor"],
                     "y": rows[index].spread_bps, "raw": entry["raw"], "issued": issued,
                     "crossed": entry["crossed"]})
    document = {"directive": "#247", "variant": variant, "horizon": h,
                "tree_settings": VARIANTS[variant], "panel_sha256": panel_sha256(args.panel),
                "days": days, "refits": refits}
    args.output.write_text(json.dumps(document, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"variant": variant, "horizon": h, "days": len(days)}))
    return 0


# ---------------------------------------------------------------------------
# Question 7's post-hoc candidates, on a walk's days
# ---------------------------------------------------------------------------


def _crps(vector, y):
    return crps_from_quantiles(LEVELS, vector, y)


def interior_tracking(days, *, steps=TRACKING_STEPS, fallback=TRACKING_FALLBACK,
                      refit_every=REFIT_EVERY):
    """(i): the issued vector with each interior level moved by its own online tracker.

    Each step in `steps` runs its own trackers over every day: before a day's
    vector is issued, every earlier day whose label is observable at its anchor
    updates offset `theta_tau += step * (tau - below(y, q_tau))` (half-tie), in
    date order. The vector issued is the chosen step's, rearranged. The step is
    chosen at the first day of each block of `refit_every` days, by least pooled
    CRPS over the observable days, `fallback` while there are none.
    """

    dates = [d["date"] for d in days]
    offsets = {s: [0.0, 0.0, 0.0] for s in steps}
    issued = {s: [] for s in steps}
    losses = {s: [] for s in steps}
    learned = 0
    chosen = fallback
    out, choices = [], []
    for j, d in enumerate(days):
        seen = bisect.bisect_right(dates, d["anchor"], 0, j)
        if seen < learned:
            raise ValueError("an anchor moved back")
        for k in range(learned, seen):
            y = days[k]["y"]
            for s in steps:
                vector = issued[s][k]
                for slot, i in enumerate(INTERIOR):
                    offsets[s][slot] += s * (LEVELS[i] - below(y, vector[i], half_tie=True))
                losses[s].append(_crps(vector, y))
        learned = seen
        if j % refit_every == 0:
            if seen:
                chosen = min(steps, key=lambda s: (sum(losses[s][:seen]) / seen, s))
            else:
                chosen = fallback
            choices.append({"first": d["date"], "step": chosen, "observable": seen})
        for s in steps:
            vector = list(d["issued"])
            for slot, i in enumerate(INTERIOR):
                vector[i] += offsets[s][slot]
            issued[s].append(sorted(vector))
        out.append(issued[chosen][j])
    return out, choices


def _empirical(values, level):
    ordered = sorted(values)
    position = level * (len(ordered) - 1)
    low = math.floor(position)
    high = min(low + 1, len(ordered) - 1)
    return ordered[low] + (position - low) * (ordered[high] - ordered[low])


def residual_law(days, rows_by_date, *, scaled):
    """(iii): v1's median plus trailing out-of-fold residual quantiles (optionally scaled)."""

    dates = [d["date"] for d in days]
    spreads = sorted((when, row.spread_bps) for when, row in rows_by_date.items()
                     if row.spread_bps is not None)
    spread_dates = [when for when, _ in spreads]

    def volatility(anchor):
        end = bisect.bisect_right(spread_dates, anchor)
        window = [b - a for (_, a), (_, b) in zip(spreads[max(0, end - VOLATILITY_DAYS - 1):end - 1],
                                                  spreads[max(1, end - VOLATILITY_DAYS):end])]
        if not window:
            return VOLATILITY_FLOOR
        return max(VOLATILITY_FLOOR, math.sqrt(sum(c * c for c in window) / len(window)))

    scale = [volatility(date.fromisoformat(d["anchor"])) if scaled else 1.0 for d in days]
    out = []
    for j, d in enumerate(days):
        seen = bisect.bisect_right(dates, d["anchor"], 0, j)
        start = max(0, seen - RESIDUAL_WINDOW)
        if seen - start < RESIDUAL_MINIMUM:
            out.append(list(d["issued"]))
            continue
        z = [(days[k]["y"] - days[k]["issued"][2]) / scale[k] for k in range(start, seen)]
        centre = d["issued"][2]
        out.append(sorted(centre + scale[j] * _empirical(z, level) for level in LEVELS))
    return out


# ---------------------------------------------------------------------------
# Assembly
# ---------------------------------------------------------------------------


def in_window(day: str, window) -> bool:
    return window[0] <= date.fromisoformat(day) <= window[1]


def reproduction_check(days) -> dict:
    """v1's per-day CRPS at h = 1 against the two published records, exactly."""

    published = json.loads((REPO / "docs/runs/compare_persistence_vs_gbm_conformal_pid_nested_funding_crps.json")
                           .read_text(encoding="utf-8"))
    final = json.loads((REPO / "docs/runs/final_test_near_blind.json").read_text(encoding="utf-8"))
    expected = {e["scored_date"]: e["loss_b_bps"] for e in published["comparison"]["per_origin"]}
    expected.update({e["scored_date"]: e["loss_b_bps"]
                     for e in final["primary"]["window_per_origin"]})
    ours = {d["date"]: _crps(d["issued"], d["y"]) for d in days}
    if set(ours) != set(expected):
        raise ValueError(f"the walk scores {len(ours)} days, the records {len(expected)}")
    mismatched = sorted(day for day in ours if ours[day] != expected[day])
    if mismatched:
        raise ValueError(f"v1's CRPS differs from the published records on {len(mismatched)} days, "
                         f"first {mismatched[0]}")
    return {
        "records": ["docs/runs/compare_persistence_vs_gbm_conformal_pid_nested_funding_crps.json",
                    "docs/runs/final_test_near_blind.json"],
        "days": len(ours),
        "first": min(ours), "last": max(ours),
        "exact": True,
        "mean_crps_2018_2025_bps": statistics.fmean(v for k, v in ours.items() if in_window(k, DIAGNOSIS)),
        "mean_crps_2026_bps": statistics.fmean(v for k, v in ours.items() if in_window(k, OPENED)),
    }


def _split_coverage(days, rows, splits) -> dict:
    scored = [date.fromisoformat(d["date"]) for d in days]
    regimes, types = _split_labels(splits, rows, scored)
    out = {"by_regime": {}, "by_day_type": {}}
    for key, labels in (("by_regime", regimes), ("by_day_type", types)):
        for label in sorted(set(labels)):
            subset = [d for d, lab in zip(days, labels) if lab == label]
            cov = coverage(subset)
            out[key][label] = {k: cov[k] for k in ("days", "coverage_half_tie", "band_50_half_edge",
                                                   "band_50_closed", "band_50_miss_below",
                                                   "band_50_miss_above", "band_90_half_edge")}
    return out


def _window_days(days, window):
    return [d for d in days if in_window(d["date"], window)]


def paired(days, v1_vectors, model_vectors, rows, splits, window, seed_parts) -> dict:
    """CRPS(v1) - CRPS(model) over the window's days, paired, with a 90% interval and splits."""

    positions = [k for k, d in enumerate(days) if in_window(d["date"], window)]
    base = [_crps(v, d["y"]) for v, d in zip(v1_vectors, days)]
    model = [_crps(v, d["y"]) for v, d in zip(model_vectors, days)]
    seed = onset._seed("#247", *seed_parts)
    out = onset.paired_difference(base, model, positions, block_length=BLOCK_LENGTH, seed=seed)
    out["crps_v1_bps"] = statistics.fmean(base[k] for k in positions)
    out["crps_model_bps"] = statistics.fmean(model[k] for k in positions)
    out["splits"] = split_document(splits, rows, [date.fromisoformat(days[k]["date"]) for k in positions],
                                   [base[k] - model[k] for k in positions],
                                   block_length=BLOCK_LENGTH, seed=seed)
    out["sign_convention"] = SIGN
    return out


def _summary(days, vectors, window):
    sub = [dict(d, issued=v) for d, v in zip(days, vectors) if in_window(d["date"], window)]
    cov = coverage(sub)
    return {
        "days": cov["days"],
        "crps": statistics.fmean(_crps(d["issued"], d["y"]) for d in sub),
        "coverage_half_tie": cov["coverage_half_tie"],
        "coverage_at_or_below": cov["coverage_at_or_below"],
        "band_50_half_edge": cov["band_50_half_edge"],
        "band_50_closed": cov["band_50_closed"],
        "band_90_half_edge": cov["band_90_half_edge"],
        "band_90_closed": cov["band_90_closed"],
        "band_50_mean_width_bps": cov["band_50_mean_width_bps"],
        "band_90_mean_width_bps": cov["band_90_mean_width_bps"],
    }


def _in_sample_summary(refits, window) -> dict:
    chosen = [r for r in refits if r["pairs"] and date.fromisoformat(r["train_end"]) <= window[1]]
    pairs = sum(r["pairs"] for r in chosen)
    return {
        "refits": len(chosen),
        "pairs": pairs,
        "coverage_half_tie": {str(level): 100.0 * sum(r["half_tie"][i] for r in chosen) / pairs
                              for i, level in enumerate(LEVELS)},
        "band_50_half_edge": 100.0 * sum(r["band_50_half_edge"] for r in chosen) / pairs,
        "band_50_closed": 100.0 * sum(r["band_50_closed"] for r in chosen) / pairs,
        "band_90_half_edge": 100.0 * sum(r["band_90_half_edge"] for r in chosen) / pairs,
    }


def assemble_command(args) -> int:
    rows = load_daily_panel(args.panel)
    audit_panel(rows)
    if panel_sha256(args.panel) != fp._frozen_panel_sha256():
        raise ValueError("the panel is not the published panel")
    splits = load_split_declaration(fp.SPLITS)
    rows_by_date = {row.date: row for row in rows}
    walks = {}
    for path in args.walks:
        document = json.loads(path.read_text(encoding="utf-8"))
        if document["panel_sha256"] != panel_sha256(args.panel):
            raise ValueError(f"{path} was walked on another panel")
        walks[(document["variant"], document["horizon"])] = document
    missing = [(v, h) for v in VARIANTS for h in (HORIZONS if v == "v1" else (1,))
               if (v, h) not in walks]
    if missing:
        raise ValueError(f"missing walks: {missing}")
    for document in walks.values():
        if max(d["date"] for d in document["days"]) > LAST_READ.isoformat():
            raise ValueError("a walk scores a day after the opened tier")
    v1 = walks[("v1", 1)]["days"]
    record = {
        "directive": "#247",
        "record": "why the published distribution's interior is miscalibrated (descriptive; decides nothing)",
        "panel_sha256": panel_sha256(args.panel),
        "published_distribution": "docs/runs/compare_persistence_vs_gbm_conformal_pid_nested_funding_crps.json "
                                  "(h = 1); docs/runs/pressure_model_v1_hH.json (h = 2 to 5)",
        "walk": "scripts/final_test_opening.distribution_walk with live_record._compare_sides(h)",
        "windows": {"diagnosis": [d.isoformat() for d in DIAGNOSIS],
                    "opened_2026_reported_separately": [d.isoformat() for d in OPENED]},
        "coverage_definitions": {
            "coverage_at_or_below": "share of outcomes at or below the quantile",
            "coverage_half_tie": "share below the quantile, an outcome exactly on it counting one half",
            "band_closed": "share with q_lo <= y <= q_hi",
            "band_open": "share with q_lo < y < q_hi",
            "band_half_edge": "share strictly inside, an outcome exactly on an edge counting one half",
        },
        "reproduction": reproduction_check(v1),
    }

    # Questions 1, 2, 5 and 6, per horizon and window.
    q1, q2, q5, q6 = {}, {}, {}, {}
    for h in HORIZONS:
        days = walks[("v1", h)]["days"]
        for tag, window in (("2018_2025", DIAGNOSIS), ("2026_opened", OPENED)):
            sub = _window_days(days, window)
            key = f"h{h}_{tag}"
            q1[key] = {"issued": coverage(sub),
                       "pit_issued": pit_histogram(sub, "issued", onset._seed("#247", "pit", h, tag)),
                       "splits": _split_coverage(sub, rows, splits)}
            q2[key] = location_and_spread(sub)
            cov = q1[key]["issued"]
            q5[key] = {
                "band_50_closed": cov["band_50_closed"],
                "band_50_open": cov["band_50_open"],
                "band_50_half_edge": cov["band_50_half_edge"],
                "band_50_outcome_jittered": jittered_band_50(sub, onset._seed("#247", "jitter", h, tag)),
                "share_outcomes_whole_bp": 100.0 * sum(1 for d in sub if d["y"] == round(d["y"])) / len(sub),
                "share_interior_quantiles_whole_bp": 100.0 * sum(
                    1 for d in sub for i in INTERIOR if d["issued"][i] == round(d["issued"][i])) / (3 * len(sub)),
                "share_days_outcome_on_a_50_band_edge": 100.0 * sum(
                    1 for d in sub if d["y"] in (d["issued"][1], d["issued"][3])) / len(sub),
            }
            raw = coverage(sub, "raw")
            q6[key] = {
                "raw_trees": {k: raw[k] for k in ("coverage_half_tie", "band_50_half_edge",
                                                  "band_90_half_edge", "band_50_mean_width_bps",
                                                  "band_90_mean_width_bps")},
                "after_pid": {k: cov[k] for k in ("coverage_half_tie", "band_50_half_edge",
                                                  "band_90_half_edge", "band_50_mean_width_bps",
                                                  "band_90_mean_width_bps")},
                "interior_changed_by_pid_days": sum(
                    1 for d in sub if any(d["raw"][i] != d["issued"][i] for i in INTERIOR)),
                "issued_crossings_days": sum(
                    1 for d in sub if any(d["issued"][i] > d["issued"][i + 1] for i in range(4))),
                "trees_crossed_before_rearrangement_days": sum(1 for d in sub if d["crossed"]),
                "days": len(sub),
            }
    record["q1_calibration"] = q1
    record["q2_location_or_spread"] = q2
    record["q5_discreteness"] = q5
    record["q6_pid_interaction"] = q6

    # Question 3: in-sample against out-of-sample, the trees' own vector, h = 1.
    record["q3_in_sample_vs_out_of_sample"] = {
        "note": "the trees' vector before PID; in-sample is each refit read on its own one-step "
                "training pairs, pooled over the refits whose training ends inside the window",
        "2018_2025": {
            "in_sample": _in_sample_summary(walks[("v1", 1)]["refits"], DIAGNOSIS),
            "out_of_sample": {k: v for k, v in coverage(_window_days(v1, DIAGNOSIS), "raw").items()
                              if k in ("days", "coverage_half_tie", "band_50_half_edge", "band_50_closed",
                                       "band_90_half_edge")},
        },
        "by_variant_2018_2025": {
            name: {"in_sample": _in_sample_summary(walks[(name, 1)]["refits"], DIAGNOSIS),
                   "out_of_sample_band_50_half_edge": coverage(
                       _window_days(walks[(name, 1)]["days"], DIAGNOSIS), "raw")["band_50_half_edge"]}
            for name in VARIANTS
        },
    }

    # Question 4: the trees' settings, one at a time.
    v1_vectors = [d["issued"] for d in v1]
    q4 = {}
    for name in VARIANTS:
        days = walks[(name, 1)]["days"]
        if [d["date"] for d in days] != [d["date"] for d in v1]:
            raise ValueError(f"{name} is not on v1's fold grid")
        vectors = [d["issued"] for d in days]
        q4[name] = {
            "tree_settings": VARIANTS[name],
            "2018_2025": _summary(v1, vectors, DIAGNOSIS),
            "2026_opened": _summary(v1, vectors, OPENED),
        }
        if name != "v1":
            q4[name]["paired_vs_v1_2018_2025"] = paired(v1, v1_vectors, vectors, rows, splits, DIAGNOSIS,
                                                        ("q4", name))
    record["q4_tree_settings"] = {"settings_of": SETTING_OF, "variants": q4}

    # Question 7: the candidates, under the rule declared above.
    variants = [name for name in VARIANTS if name != "v1"]
    passing = [n for n in variants if eligible(q4[n]["2018_2025"])]
    best = min(passing or variants, key=lambda n: (q4[n]["2018_2025"]["crps"], n))
    trees = [d["issued"] for d in walks[(best, 1)]["days"]]
    tracked, choices = interior_tracking(v1)
    tracked_trees, choices_trees = interior_tracking(
        [dict(d, issued=v) for d, v in zip(v1, trees)])
    vectors = {
        "i_interior_tracking": tracked,
        "ii_regularised_trees": trees,
        "iii_residual_law": residual_law(v1, rows_by_date, scaled=False),
        "iii_residual_law_scaled": residual_law(v1, rows_by_date, scaled=True),
        "iv_regularised_and_tracking": tracked_trees,
    }
    candidates = {}
    for name in CANDIDATES:
        candidates[name] = {
            "2018_2025": _summary(v1, vectors[name], DIAGNOSIS),
            "2026_opened": _summary(v1, vectors[name], OPENED),
            "paired_vs_v1_2018_2025": paired(v1, v1_vectors, vectors[name], rows, splits, DIAGNOSIS,
                                             ("q7", name)),
            "paired_vs_v1_2026_opened": paired(v1, v1_vectors, vectors[name], rows, splits, OPENED,
                                               ("q7", name, "2026")),
            "complexity": list(COMPLEXITY[name]),
        }
    summaries = {name: candidates[name]["2018_2025"] for name in CANDIDATES}
    pair_cache = {}

    def paired_to_leader(name, leader):
        if (name, leader) not in pair_cache:
            pair_cache[(name, leader)] = paired(v1, vectors[leader], vectors[name], rows, splits,
                                                DIAGNOSIS, ("q7", name, "vs", leader))
        return pair_cache[(name, leader)]

    selection = select_candidate(summaries, paired_to_leader)
    selection["paired_against_leader"] = {
        f"{a}_vs_{b}": {k: v for k, v in p.items() if k != "splits"} for (a, b), p in pair_cache.items()}
    record["q7_candidates"] = {
        "v1": {"2018_2025": _summary(v1, v1_vectors, DIAGNOSIS), "2026_opened": _summary(v1, v1_vectors, OPENED)},
        "candidates": candidates,
        "ii_setting": {"variant": best, "tree_settings": VARIANTS[best],
                       "chosen_by": "the question 4 variant meeting the bar with the lowest 2018-2025 "
                                    "CRPS, or the lowest CRPS if none meets it"},
        "i_tracking": {"steps": list(TRACKING_STEPS), "fallback": TRACKING_FALLBACK,
                       "refit_every": REFIT_EVERY, "choices": choices},
        "iv_tracking_choices": choices_trees,
        "iii_settings": {"window": RESIDUAL_WINDOW, "minimum": RESIDUAL_MINIMUM,
                         "volatility_days": VOLATILITY_DAYS, "volatility_floor_bps": VOLATILITY_FLOOR},
    }
    record["selection_rule"] = SELECTION_RULE
    record["complexity"] = {name: list(rank) for name, rank in COMPLEXITY.items()}
    record["selection"] = selection
    record["v1_h1_per_day"] = [[d["date"], d["y"], d["issued"]] for d in v1]
    args.output.write_text(json.dumps(record, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"reproduction": record["reproduction"], "selection": {
        k: selection[k] for k in ("recommended", "eligible", "leader", "reason")}}, indent=1))
    return 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="command", required=True)
    wk = sub.add_parser("walk", help="one walk of the published distribution or a variant")
    wk.add_argument("--panel", type=Path, required=True)
    wk.add_argument("--horizon", type=int, choices=HORIZONS, required=True)
    wk.add_argument("--variant", choices=tuple(VARIANTS), default="v1")
    wk.add_argument("--no-in-sample", action="store_true")
    wk.add_argument("--output", type=Path, required=True)
    wk.set_defaults(func=walk_command)
    asm = sub.add_parser("assemble", help="the record from the walks")
    asm.add_argument("--panel", type=Path, required=True)
    asm.add_argument("--walks", type=Path, nargs="+", required=True)
    asm.add_argument("--output", type=Path, required=True)
    asm.set_defaults(func=assemble_command)
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
