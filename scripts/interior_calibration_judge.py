#!/usr/bin/env python3
"""Does the published distribution's interior have a fix worth publishing? (#243)

#243 found that the published distribution's 50% band (q25 to q75) covers about a third of
outcomes. #247 diagnosed it and #244/#252 built pressure model v2 around an online interior. The
directive asks for a fix, judged by Eleonora's standing publishing rule: a change to the published
distribution is published only if it improves the model by a test declared before scoring.

The candidates and the test are declared in `docs/declarations/interior_calibration_243.json`,
committed before any candidate was scored; this script reads that file, records its sha256, and
refuses a candidate it does not list.

* **Published side.** The issued vectors of #169's gbm with nested conformal PID at h = 1 (v1), as
  `docs/runs/v1_interior_diagnosis.json` carries them (the record reproduces the published CRPS
  records exactly). Nothing is walked: every candidate here is an online layer on those vectors, or
  (pressure model v2) a record already published.
* **Window.** 2018-06-29 to 2025-12-31 only (`WINDOW`). `check_window` refuses a later day.
* **Conformal candidates.** `conformal_interior`: q25, q50 and q75 each moved by the empirical
  quantile of y - issued q_tau over the trailing `window` scored days whose label is observable at
  the day's anchor. Pooled, or within the day's calendar class.
* **Test.** `verdict`: the pooled paired gain CRPS(published) - CRPS(candidate) has a 90%
  stationary-bootstrap interval above zero, and no regime or day-type cell of at least 20 days has
  an interval wholly below zero.

    PYTHONPATH=src python3 -m repo_model.cli build --raw-root tests/fixtures/snapshots/funding_inputs \\
        --output PUB.csv --build-cutoff 2026-09-08T21:31:42+00:00 --decision-time 16:00:00
    PYTHONPATH=src /opt/rmm-venv/bin/python scripts/interior_calibration_judge.py score \\
        --panel PUB.csv --output docs/runs/interior_calibration_243.json
"""

from __future__ import annotations

import argparse
import bisect
import csv
import hashlib
import importlib.util
import json
import math
import statistics
import sys
from datetime import date
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))

from repo_model import lockbox, metrics, onset  # noqa: E402
from repo_model.baseline import _split_labels, panel_sha256  # noqa: E402
from repo_model.data import audit_panel, load_daily_panel  # noqa: E402
from repo_model.evaluation_splits import DAY_TYPES, load_split_declaration  # noqa: E402
from repo_model.splits import LookAheadError  # noqa: E402

DECLARATION = REPO / "docs" / "declarations" / "interior_calibration_243.json"
ADDENDUM = REPO / "docs" / "declarations" / "interior_calibration_243_addendum.json"
V1_RECORD = REPO / "docs" / "runs" / "v1_interior_diagnosis.json"
V2_RECORD = REPO / "docs" / "runs" / "pressure_model_v2_distribution_h1.json"
MANIFEST = REPO / "metadata" / "funding_panel_manifest.json"
SPLITS = REPO / "metadata" / "evaluation_splits.json"
OUTPUT = REPO / "docs" / "runs" / "interior_calibration_243.json"

LEVELS = (0.05, 0.25, 0.5, 0.75, 0.95)
INTERIOR = (1, 2, 3)
WINDOW = (date(2018, 6, 29), date(2025, 12, 31))
FIRST_CANDIDATES = ("conformal_pooled", "conformal_by_day_type", "interior_tracking", "pressure_model_v2")
ADDENDUM_CANDIDATES = ("conformal_group_regime", "conformal_recency_regime", "conformal_aci", "conformal_pid_calendar")
CANDIDATES = FIRST_CANDIDATES + ADDENDUM_CANDIDATES
TAGS = ("month_end", "quarter_end", "year_end", "tax_date", "coupon_settlement")
TURN = ("month_end", "quarter_end", "tax_date", "coupon_settlement")
MINIMUM_CELL_DAYS = onset.MINIMUM_EVENTS
BLOCK_LENGTH = 2
REPLICATIONS = 2000
LEVEL = 0.90
TIE_BPS = 1e-9
SIGN = "gain = CRPS(published) - CRPS(candidate) per day; a positive mean favours the candidate"


def _script(name):
    spec = importlib.util.spec_from_file_location(f"judge_{name}", REPO / "scripts" / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def declaration() -> dict:
    """The first declaration, with the addendum's candidates added under their own names."""

    first = json.loads(DECLARATION.read_text(encoding="utf-8"))
    added = json.loads(ADDENDUM.read_text(encoding="utf-8"))["candidates"]
    return {**first, "candidates": {**first["candidates"], **added}}


def declaration_sha256() -> str:
    return hashlib.sha256(DECLARATION.read_bytes()).hexdigest()


def addendum_sha256() -> str:
    return hashlib.sha256(ADDENDUM.read_bytes()).hexdigest()


def require_declared(name: str) -> None:
    """Refuse a candidate neither the declaration nor its addendum lists."""

    if name not in declaration()["candidates"]:
        raise ValueError(f"candidate {name!r} is not in the declaration {DECLARATION.name} or {ADDENDUM.name}")


def check_window(dates) -> None:
    """Refuse to score any day after the window's last (2025-12-31), which is before the locked tiers."""

    last = max(date.fromisoformat(d) if isinstance(d, str) else d for d in dates)
    if last > WINDOW[1]:
        raise LookAheadError(f"{last} is after the window's last day {WINDOW[1]}: #243 scores days before 2026-01-01 only")
    lockbox.require_unlocked([last], where="interior_calibration_judge")


def _empirical(values, level):
    ordered = sorted(values)
    position = level * (len(ordered) - 1)
    low = math.floor(position)
    high = min(low + 1, len(ordered) - 1)
    return ordered[low] + (position - low) * (ordered[high] - ordered[low])


def conformal_interior(days, *, window, minimum, by_kind=False, keys=None):
    """Each day's issued vector with q25, q50 and q75 shifted by their residual quantiles.

    `days` are in date order, each with `date`, `anchor`, `y`, `issued` and `kind`. The shift of
    level tau is the tau-quantile (linear interpolation) of `y - issued[tau]` over the last
    `window` earlier days whose label is observable at the day's anchor (`date <= anchor`), 0 while
    fewer than `minimum` are. With `by_kind` the residuals are those of days of the same `kind`,
    or the pooled ones while that kind has fewer than `minimum`. With `keys` (day fields, most
    specific first) the first key whose same-valued residuals number `minimum` or more is used,
    else the pooled ones; `by_kind` is `keys=("kind",)`. The vector is sorted.

    Raises:
        LookAheadError: if a day's anchor is not before the day.
    """

    dates = [d["date"] for d in days]
    out = []
    for j, d in enumerate(days):
        if d["anchor"] >= d["date"]:
            raise LookAheadError(f"{d['date']}: its anchor {d['anchor']} is not before the scored day")
        seen = bisect.bisect_right(dates, d["anchor"], 0, j)
        pool = list(range(max(0, seen - window), seen))
        for key in (("kind",) if by_kind else keys or ()):
            same = [k for k in pool if days[k][key] == d[key]]
            if len(same) >= minimum:
                pool = same
                break
        vector = list(d["issued"])
        if len(pool) >= minimum:
            for i in INTERIOR:
                residuals = [days[k]["y"] - days[k]["issued"][i] for k in pool]
                vector[i] += _empirical(residuals, LEVELS[i])
        out.append(sorted(vector))
    return out


def _observable(days, dates, j):
    """How many earlier days have a label observable at day `j`'s anchor (days `[0, seen)`).

    Raises:
        LookAheadError: if the day's anchor is not before the day.
    """

    d = days[j]
    if d["anchor"] >= d["date"]:
        raise LookAheadError(f"{d['date']}: its anchor {d['anchor']} is not before the scored day")
    return bisect.bisect_right(dates, d["anchor"], 0, j)


def _weighted_quantile(values, weights, level):
    """The weighted `level` quantile: weights at the midpoints of the cumulative weight, linear between."""

    order = sorted(range(len(values)), key=values.__getitem__)
    total = sum(weights)
    cumulative, running = [], 0.0
    for k in order:
        running += weights[k]
        cumulative.append((running - 0.5 * weights[k]) / total)
    ordered = [values[k] for k in order]
    if level <= cumulative[0]:
        return ordered[0]
    if level >= cumulative[-1]:
        return ordered[-1]
    at = bisect.bisect_right(cumulative, level)
    span = cumulative[at] - cumulative[at - 1]
    share = (level - cumulative[at - 1]) / span if span > 0 else 0.0
    return ordered[at - 1] + share * (ordered[at] - ordered[at - 1])


def weighted_conformal(days, *, window, minimum, half_life, off_regime_weight):
    """(b) Recency- and regime-weighted residual quantiles (Barber et al., Beyond exchangeability).

    As the pooled conformal candidate, but each residual in the trailing `window` observable days
    has weight `0.5 ** (age / half_life)`, age counted in observable days back from the latest,
    times `off_regime_weight` when the day is from another regime than the scored day's.
    """

    dates = [d["date"] for d in days]
    out = []
    for j, d in enumerate(days):
        seen = _observable(days, dates, j)
        pool = list(range(max(0, seen - window), seen))
        vector = list(d["issued"])
        if len(pool) >= minimum:
            weights = [0.5 ** ((seen - 1 - k) / half_life) * (1.0 if days[k]["regime"] == d["regime"] else off_regime_weight)
                       for k in pool]
            for i in INTERIOR:
                residuals = [days[k]["y"] - days[k]["issued"][i] for k in pool]
                vector[i] += _weighted_quantile(residuals, weights, LEVELS[i])
        out.append(sorted(vector))
    return out


def aci_conformal(days, *, window, minimum, gamma, clip):
    """(c) Adaptive conformal inference on the interior levels (Gibbs & Candes).

    Level `l_i` starts at `LEVELS[i]`. Before a day is issued, every earlier day whose label
    became observable since the last one updates `l_i += gamma * (LEVELS[i] - 1[y < q_i])`, with
    `q_i` the value issued that day, clipped to `clip`. The shift is the `l_i` quantile of the
    trailing-`window` pooled residuals, 0 until `minimum` are observable.
    """

    dates = [d["date"] for d in days]
    levels = {i: LEVELS[i] for i in INTERIOR}
    issued_q = []
    learned = 0
    out = []
    for j, d in enumerate(days):
        seen = _observable(days, dates, j)
        if seen < learned:
            raise ValueError("an anchor moved back")
        for k in range(learned, seen):
            for i in INTERIOR:
                levels[i] = min(clip[1], max(clip[0], levels[i] + gamma * (LEVELS[i] - (1.0 if days[k]["y"] < issued_q[k][i] else 0.0))))
        learned = seen
        pool = list(range(max(0, seen - window), seen))
        vector = list(d["issued"])
        if len(pool) >= minimum:
            for i in INTERIOR:
                residuals = [days[k]["y"] - days[k]["issued"][i] for k in pool]
                vector[i] += _empirical(residuals, levels[i])
        issued_q.append(list(vector))
        out.append(sorted(vector))
    return out


def pid_calendar(days, *, window, minimum, step):
    """(d) Conformal PID with a calendar scorecaster (Angelopoulos, Candes & Tibshirani).

    Integrator `theta_i += step * (LEVELS[i] - 1[y < final q_i])` over days whose label is
    observable at the anchor. Scorecaster: the `LEVELS[i]` quantile of `y - (issued_i + theta_i as it
    stood that day)` over the trailing-`window` observable days of the day's `kind`, 0 while that
    kind has fewer than `minimum`. The final `q_i` is issued + theta + scorecaster; sorted.
    """

    dates = [d["date"] for d in days]
    theta = {i: 0.0 for i in INTERIOR}
    final_q, net = [], []
    learned = 0
    out = []
    for j, d in enumerate(days):
        seen = _observable(days, dates, j)
        if seen < learned:
            raise ValueError("an anchor moved back")
        for k in range(learned, seen):
            for i in INTERIOR:
                theta[i] += step * (LEVELS[i] - (1.0 if days[k]["y"] < final_q[k][i] else 0.0))
        learned = seen
        pool = [k for k in range(max(0, seen - window), seen) if days[k]["kind"] == d["kind"]]
        vector = list(d["issued"])
        for i in INTERIOR:
            vector[i] += theta[i]
        net.append(list(vector))
        if len(pool) >= minimum:
            for i in INTERIOR:
                residuals = [days[k]["y"] - net[k][i] for k in pool]
                vector[i] += _empirical(residuals, LEVELS[i])
        final_q.append(list(vector))
        out.append(sorted(vector))
    return out


def verdict(pooled: dict, cells: dict) -> dict:
    """The declared test on a candidate's pooled gain and its cells' gains (each with `days`, `interval`)."""

    above = pooled["interval"]["lower"] > 0.0
    worse = sorted(name for name, c in cells.items()
                   if c["days"] >= MINIMUM_CELL_DAYS and c["interval"]["upper"] < 0.0)
    return {"pooled_above_zero": above, "worse_cells": worse, "met": bool(above and not worse)}


def _crps(vector, y):
    return metrics.crps_from_quantiles(LEVELS, vector, y)


def _tied(a, b):
    return abs(a - b) <= TIE_BPS


def coverage(days, vectors):
    """Both bands' half-edge coverage and misses (percent of days), and the 50% band's mean width."""

    n = len(days)
    out = {"days": n}
    for name, (lo, hi) in (("band_50", (1, 3)), ("band_90", (0, 4))):
        below = above = edge = 0
        for d, v in zip(days, vectors):
            y = d["y"]
            if _tied(y, v[lo]) or _tied(y, v[hi]):
                edge += 1
            elif y < v[lo]:
                below += 1
            elif y > v[hi]:
                above += 1
        out[name] = 100.0 * (n - below - above - 0.5 * edge) / n
        out[name + "_miss_below"] = 100.0 * below / n
        out[name + "_miss_above"] = 100.0 * above / n
        out[name + "_mean_width_bps"] = statistics.fmean(v[hi] - v[lo] for v in vectors)
    return out


def cell_intervals(series, masks, seed):
    """Mean of `series` over each mask, with its 90% domain-bootstrap interval, from one set of resamples."""

    live = [k for k, m in enumerate(masks) if sum(m) >= MINIMUM_CELL_DAYS]

    def statistic(indices):
        sums = [0.0] * len(masks)
        counts = [0] * len(masks)
        for i in indices:
            for k in live:
                if masks[k][i]:
                    sums[k] += series[i]
                    counts[k] += 1
        return [sums[k] / counts[k] if counts[k] else math.nan for k in live]

    spans = dict(zip(live, metrics.stationary_bootstrap_intervals(
        statistic, len(series), block_length=BLOCK_LENGTH, seed=seed,
        replications=REPLICATIONS, level=LEVEL)))
    out = []
    for k, mask in enumerate(masks):
        members = [series[i] for i, m in enumerate(mask) if m]
        cell = {"days": len(members)}
        if members:
            cell["mean"] = statistics.fmean(members)
        if k in spans:
            cell["interval"] = {"lower": spans[k][0], "upper": spans[k][1]}
        out.append(cell)
    return out


def load_days(panel_rows, splits, tag_rows):
    """The published side's days: date, anchor, outcome, issued vector, calendar tags, kind, regime and group."""

    v1 = json.loads(V1_RECORD.read_text(encoding="utf-8"))["v1_h1_per_day"]
    anchors = {a[0]: a[1] for a in json.loads(V2_RECORD.read_text(encoding="utf-8"))["anchors"]}
    bc = _script("band_coverage")
    days = []
    for iso, y, vector in v1:
        if iso > WINDOW[1].isoformat():
            continue
        tags = bc.tags_for(tag_rows[iso], date.fromisoformat(iso), splits.month_end_window)
        kind = "turn" if any(t in TURN for t in tags) else "ordinary"
        days.append({"date": iso, "anchor": anchors[iso], "y": y, "issued": list(vector), "tags": tags,
                     "kind": kind})
    regimes, _types = _split_labels(splits, panel_rows, [date.fromisoformat(d["date"]) for d in days])
    for d, regime in zip(days, regimes):
        d["regime"] = regime
        d["group"] = d["kind"] + "|" + regime
    return days


def candidate_vectors(name, days):
    require_declared(name)
    spec = declaration()["candidates"].get(name, {})
    if name == "conformal_pooled":
        return conformal_interior(days, window=spec["window_days"], minimum=spec["minimum_days"])
    if name == "conformal_by_day_type":
        return conformal_interior(days, window=spec["window_days"], minimum=spec["minimum_days"], by_kind=True)
    if name == "conformal_group_regime":
        return conformal_interior(days, window=spec["window_days"], minimum=spec["minimum_days"], keys=("group", "kind"))
    if name == "conformal_recency_regime":
        return weighted_conformal(days, window=spec["window_days"], minimum=spec["minimum_days"],
                                  half_life=spec["half_life_days"], off_regime_weight=spec["off_regime_weight"])
    if name == "conformal_aci":
        return aci_conformal(days, window=spec["window_days"], minimum=spec["minimum_days"],
                             gamma=spec["gamma"], clip=tuple(spec["level_clip"]))
    if name == "conformal_pid_calendar":
        return pid_calendar(days, window=spec["window_days"], minimum=spec["minimum_days"], step=spec["integrator_step"])
    if name == "interior_tracking":
        vectors, _choices = _script("interior_diagnosis").interior_tracking(days)
        return vectors
    if name == "pressure_model_v2":
        rows = {r[0]: r for r in json.loads(V2_RECORD.read_text(encoding="utf-8"))["per_day_h1"]["rows"]}
        out = []
        for d in days:
            row = rows[d["date"]]
            if abs(row[1] - d["y"]) > 1e-9:
                raise ValueError(f"v2 record and v1 record disagree on the outcome of {d['date']}")
            out.append(list(row[4]))
        return out
    raise ValueError(name)


def score_command(args) -> int:
    rows = load_daily_panel(args.panel)
    audit_panel(rows)
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    if panel_sha256(args.panel) != manifest["sha256"]:
        raise ValueError("the panel is not the published panel")
    splits = load_split_declaration(SPLITS)
    with open(args.panel, newline="", encoding="utf-8") as handle:
        tag_rows = {r["date"]: r for r in csv.DictReader(handle)}
    days = load_days(rows, splits, tag_rows)
    check_window([d["date"] for d in days])
    dates = [date.fromisoformat(d["date"]) for d in days]
    regimes, types = _split_labels(splits, rows, dates)
    regime_names = [r for r in splits.regime_labels if r in set(regimes)]

    groups = {}
    for r in regime_names:
        groups["regime:" + r] = [x == r for x in regimes]
    for t in TAGS:
        groups["tag:" + t] = [t in d["tags"] for d in days]
    groups["tag:other"] = [not d["tags"] for d in days]
    for t in DAY_TYPES:
        groups["reporting:" + t] = [x == t for x in types]
    names = list(groups)
    masks = [[True] * len(days)] + [groups[n] for n in names]

    published = [d["issued"] for d in days]
    pub_loss = [_crps(v, d["y"]) for v, d in zip(published, days)]

    def by_group(vectors):
        out = {"all": coverage(days, vectors)}
        for n in names:
            members = [i for i, m in enumerate(groups[n]) if m]
            if members:
                out[n] = coverage([days[i] for i in members], [vectors[i] for i in members])
        return out

    record = {
        "directive": "#243",
        "record": "interior calibration: candidates scored against the published distribution (h = 1)",
        "declaration": str(DECLARATION.relative_to(REPO)),
        "declaration_sha256": declaration_sha256(),
        "addendum": str(ADDENDUM.relative_to(REPO)),
        "addendum_sha256": addendum_sha256(),
        "addendum_candidates": list(ADDENDUM_CANDIDATES),
        "panel_sha256": panel_sha256(args.panel),
        "window": {"first": days[0]["date"], "last": days[-1]["date"], "days": len(days)},
        "sign_convention": SIGN,
        "bootstrap": {"block_length": BLOCK_LENGTH, "replications": REPLICATIONS, "level": LEVEL},
        "published": {"crps_bps": statistics.fmean(pub_loss), "coverage_by_group": by_group(published)},
        "candidates": {},
    }
    for name in CANDIDATES:
        vectors = candidate_vectors(name, days)
        for v in vectors:
            if any(a > b for a, b in zip(v, v[1:])):
                raise ValueError(f"{name} issued a crossing vector")
        loss = [_crps(v, d["y"]) for v, d in zip(vectors, days)]
        gain = [a - b for a, b in zip(pub_loss, loss)]
        cells = cell_intervals(gain, masks, onset._seed("#243", "gain", name))
        pooled, rest = cells[0], dict(zip(names, cells[1:]))
        record["candidates"][name] = {
            "crps_bps": statistics.fmean(loss),
            "pooled_gain": pooled,
            "gain_by_group": rest,
            "coverage_by_group": by_group(vectors),
            "test": verdict(pooled, rest),
        }
    record["publish"] = [n for n, c in record["candidates"].items() if c["test"]["met"]]
    record["outcome"] = (
        "meeting the declared test: %s. Whether and which joins the published declaration is Eleonora's; "
        "this record changes no published figure" % ", ".join(record["publish"]) if record["publish"] else
        "no candidate meets the declared test: report only, the published declaration is unchanged")
    args.output.write_text(json.dumps(record, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    return 0


def _pct(value):
    return "%.1f" % value


def _gain(cell):
    if "interval" not in cell:
        return "%d days: too few" % cell["days"]
    return "%+.3f [%+.3f, %+.3f]" % (cell["mean"], cell["interval"]["lower"], cell["interval"]["upper"])


def render(record) -> str:
    """The results page, from the record alone."""

    sets = [("published", record["published"])] + list(record["candidates"].items())
    names = [n for n, _ in sets]
    lines = ["# Interior calibration: candidates against the published distribution (#243)", "",
             "<!-- generated: interior-calibration -->", "",
             "**Generated by `scripts/interior_calibration_judge.py render` from "
             "`docs/runs/interior_calibration_243.json`; never hand-edited.** Reported, and decides nothing "
             "by itself: the published declaration is unchanged (see the \"Publish?\" issue linked from the pull request).", "",
             "The published distribution at h = 1 (#169's gbm with nested conformal PID), %d days, %s to %s, against each "
             "candidate declared in `%s` (sha256 `%s`) before it was scored. Gain is CRPS(published) - CRPS(candidate) "
             "per day in bp, so a positive mean favours the candidate; intervals are 90%% stationary bootstraps "
             "(block length 2). Days after 2025-12-31 are not read." % (
                 record["window"]["days"], record["window"]["first"], record["window"]["last"],
                 record["declaration"], record["declaration_sha256"][:12]), "",
             "## The declared test", "",
             "| Candidate | CRPS (bp) | Pooled gain | Pooled interval above zero | Cells worse beyond their interval | Test met |",
             "|---|---|---|---|---|---|",
             "| published | %.3f | | | | |" % record["published"]["crps_bps"]]
    for name, c in record["candidates"].items():
        t = c["test"]
        lines.append("| %s | %.3f | %s | %s | %s | %s |" % (
            name, c["crps_bps"], _gain(c["pooled_gain"]), "yes" if t["pooled_above_zero"] else "no",
            ", ".join(t["worse_cells"]) or "none", "**yes**" if t["met"] else "no"))
    lines += ["", "Candidates " + record["outcome"] + ".", "", "## Gain by regime and by day type", "",
              "| Group | " + " | ".join(record["candidates"]) + " |", "|---|" + "---|" * len(record["candidates"])]
    for group in next(iter(record["candidates"].values()))["gain_by_group"]:
        lines.append("| %s | %s |" % (group, " | ".join(
            _gain(c["gain_by_group"][group]) for c in record["candidates"].values())))
    for band, label in (("band_50", "50% band"), ("band_90", "90% band")):
        lines += ["", "## Coverage of the %s by group" % label, "",
                  "Each cell: coverage %, with the share of days the outcome fell below / above the band. "
                  "An outcome on an edge counts half inside. A group of under 20 days is too few to read.", "",
                  "| Group | days | " + " | ".join(names) + " |", "|---|---|" + "---|" * len(names)]
        for group, cell in record["published"]["coverage_by_group"].items():
            row = []
            for _, s in sets:
                g = s["coverage_by_group"][group]
                row.append("%s (%s / %s)" % (_pct(g[band]), _pct(g[band + "_miss_below"]), _pct(g[band + "_miss_above"])))
            lines.append("| %s | %d | %s |" % (group, cell["days"], " | ".join(row)))
    lines += ["", "<!-- end generated: interior-calibration -->", ""]
    return "\n".join(lines)


def render_command(args) -> int:
    record = json.loads(args.record.read_text(encoding="utf-8"))
    args.output.write_text(render(record), encoding="utf-8")
    return 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="command", required=True)
    score = sub.add_parser("score")
    score.add_argument("--panel", type=Path, required=True)
    score.add_argument("--output", type=Path, default=OUTPUT)
    score.set_defaults(func=score_command)
    page = sub.add_parser("render")
    page.add_argument("--record", type=Path, default=OUTPUT)
    page.add_argument("--output", type=Path, default=REPO / "docs" / "interior_calibration_243.md")
    page.set_defaults(func=render_command)
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
