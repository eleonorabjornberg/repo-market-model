"""The misses of (s3c-ann-net) after a month-end by business day 1, 2 and 3, re-issued with every resample kept (#1614, H5, known limits).

A development diagnostic, never a verdict. It re-issues #1611's page (`scripts/post_month_end_split_1611.py`, merged as #1612) as a new dated
version; the old page, its `result.json` and its figures are not edited. It reads the same walks (#1547 and #1555's, the 1363 walk regenerated and
checked against its sha256): no refit, no new fit, no new arm, nothing registered. Settled-questions: new question (S18 and #1547 cover
location in aggregate; #1611 is the split this corrects; no entry covers miss-share intervals for rows that can draw no miss).

What #1613 found, and what changes. #1611's studentized interval dropped every resample whose daily-share series had no variation (no miss drawn)
and still reported an interval when at least 90% of the resamples were left. Scoring protocol v1's scorer refuses such a resample
(`scoring_protocol._standard_error` raises) instead of skipping it. Here every resample is kept. A resample with no variance has no standard
error; its t-value is -infinity if its mean is below the observed mean, +infinity if above, 0 on a tie (the limit of the t-value as the standard
error goes to 0). A share whose resamples often draw no miss therefore gets an upper end of 1: the interval says only that the share cannot be
bounded from above on so few misses. A series with no variation in the data (no miss at all) still has no studentized interval, as in the
protocol. Where no resample was dropped, the interval is #1611's to the last digit (a test pins this).

The 2026 table. The share printed beside a cell count is misses over cells. #1611 printed the mean of each target day's own share, which differs
when days have different numbers of cells (2026: some days have fewer than five leads). The development windows have five cells on every day
(`check_cells_per_day` refuses a scored window that does not), so there the two agree.

A second interval, exploratory. For a share of rare events the studentized bootstrap is not designed: with few misses the t-distribution has a mass
at the ends. Beside it every share row carries a Wilson score interval on an effective number of cells, N / DEFF, where N is the number of cells
and DEFF is the design effect: the Newey-West (Bartlett, lag 10) variance of the mean of the daily shares divided by the variance of a proportion
of N independent cells, never below 1. DEFF reads both dependences the page names, the five leads of one day and the serial dependence of the
days. A score interval keeps its lower end at 0 and its upper end above 0 when no miss was seen, which the Wald interval cannot. It is marked
exploratory: which interval the project uses for such shares is Eleonora's decision (question in the pull request), not settled here. With no miss
the design effect is not estimable and is held at 1, so that row's score interval is the independent-cells one and is too narrow if misses would
cluster.

    PYTHONPATH=src python3 -m repo_model.cli build --raw-root tests/fixtures/snapshots/funding_inputs --output PUB.csv \\
        --build-cutoff 2026-09-08T21:31:42+00:00 --decision-time 18:00:00
    for W in development 2026; do
      RMM_DECISION_TIME=18:00 PYTHONPATH=src python3 scripts/qe_diagnosis_1533.py walk --panel PUB.csv --window $W \\
          --output WALK/$W.json --extension EXT/$W.json
    done
    OUT=docs/research/post-month-end-corrected-1614
    PYTHONPATH=src python3 scripts/post_month_end_corrected_1614.py score --walks WALK --extensions EXT --output $OUT/result.json
    PYTHONPATH=src python3 scripts/post_month_end_corrected_1614.py page --score $OUT/result.json \\
        --output docs/research/post-month-end-corrected-1614-result.md

Stdlib only.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import math
import random
import statistics
import sys
from collections import defaultdict
from datetime import date
from pathlib import Path
from typing import Dict, List, Mapping, Optional, Sequence

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))

from repo_model import metrics, scoring_protocol as sp  # noqa: E402


def _load(name: str, alias: str):
    spec = importlib.util.spec_from_file_location(alias, REPO / "scripts" / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[alias] = module
    spec.loader.exec_module(module)
    return module


prior = _load("post_month_end_split_1611", "post_month_end_split_1611_in_1614")
q = prior.q
G05, G50, G95 = prior.G05, prior.G50, prior.G95
RECORD_1363 = prior.RECORD_1363
RECORD_1547 = prior.RECORD_1547
RECORD_1611 = REPO / "docs" / "research" / "post-month-end-split-1611" / "result.json"
WHERE = "post_month_end_corrected_1614"
SEED = prior.SEED  # the same resample stream as #1611, so that a changed row changed because of the rule
REPS = sp.DRAWS
BLOCK = sp.BLOCK_LENGTH
LAG = sp.HAC_LAG
LEVEL = prior.LEVEL
MIN_DAYS = prior.MIN_DAYS
BUSINESS_DAYS = prior.BUSINESS_DAYS
NOMINAL = prior.NOMINAL
Z = statistics.NormalDist().inv_cdf((1 + LEVEL) / 2)

business_day = prior.business_day
month_end_kind = prior.month_end_kind
check_unlocked = prior.check_unlocked
check_flag_agreement = prior.check_flag_agreement
check_reproduction = prior.check_reproduction
day_series = prior.day_series
_median = prior._median
_cells_of = prior._cells_of


# -- the guards -------------------------------------------------------------------------------------------------------------------------


def check_cells_per_day(cells: Sequence[Mapping[str, object]]) -> None:
    """Refuse (`ValueError`) a window whose target days on business day 1 to 3 do not all have the same number of cells: its share would not be the mean of its days' shares."""

    counts: Dict[str, int] = defaultdict(int)
    for c in cells:
        if business_day(date.fromisoformat(c["t"])) in BUSINESS_DAYS:
            counts[c["t"]] += 1
    if len(set(counts.values())) > 1:
        raise ValueError(f"target days differ in their number of cells: {sorted(set(counts.values()))}")


# -- the studentized interval, every resample kept ----------------------------------------------------------------------------------------


def percentile(ordered: Sequence[float], p: float) -> float:
    """The linear-interpolation percentile of a sorted list that may hold -inf and +inf; between a finite and an infinite value it is the infinite one."""

    position = p * (len(ordered) - 1)
    lo = int(math.floor(position))
    hi = min(lo + 1, len(ordered) - 1)
    a, b, frac = ordered[lo], ordered[hi], position - lo
    if a == b or frac == 0.0:
        return a
    if math.isinf(a) or math.isinf(b):
        return a if math.isinf(a) and not math.isinf(b) else b if math.isinf(b) and not math.isinf(a) else math.nan
    return a + (b - a) * frac


def t_value(*, resampled_mean: float, mean: float, variance: float, n: int) -> float:
    """The studentized value of one resample. With no variance the standard error is 0: the value is -inf below the observed mean, +inf above, 0 on a tie."""

    if variance > 0.0:
        return (resampled_mean - mean) / math.sqrt(variance / n)
    return math.copysign(math.inf, resampled_mean - mean) if resampled_mean != mean else 0.0


def _studentized(values: Sequence[float], indices: Sequence[Sequence[int]], clip: Optional[Sequence[float]]) -> dict:
    n = len(values)
    mean = sum(values) / n
    variance = sp._long_run_variance(values, LAG)
    if variance <= 0.0:
        return {"interval": None, "resamples": len(indices), "no_variance": None}
    se = math.sqrt(variance / n)
    ts = []
    no_variance = 0
    for picked in indices:
        resample = list(map(values.__getitem__, picked))
        v = sp._long_run_variance(resample, LAG)
        no_variance += v <= 0.0
        ts.append(t_value(resampled_mean=sum(resample) / n, mean=mean, variance=v, n=n))
    ts.sort()
    t_hi, t_lo = percentile(ts, (1 + LEVEL) / 2), percentile(ts, (1 - LEVEL) / 2)
    lo, hi = mean - t_hi * se, mean - t_lo * se
    if clip is not None:
        lo, hi = max(lo, clip[0]), min(hi, clip[1])
    ends = [None if (math.isinf(x) or math.isnan(x)) else x for x in (lo, hi)]
    return {"interval": [mean, *ends], "resamples": len(ts), "no_variance": no_variance}


def studentized(values: Sequence[float], *, reps: int, seed: int, clip: Optional[Sequence[float]]) -> dict:
    """{'interval': [mean, low, high] or None, 'resamples': n kept, 'no_variance': how many of them drew no variation}. None for fewer than 20 days."""

    n = len(values)
    if reps <= 0 or n < MIN_DAYS:
        return {"interval": None, "resamples": 0, "no_variance": None}
    rng = random.Random(seed)
    indices = [metrics.stationary_bootstrap_indices(n, BLOCK, rng) for _ in range(reps)]
    return _studentized(values, indices, clip)


def intervals(series: Mapping[str, Sequence[float]], *, reps: int, seed: int, share: Sequence[str] = ()) -> Dict[str, object]:
    """One resample stream shared by every series (as #1611's): each series' studentized mean, clipped to [0, 1] for the names in `share`, and the
    percentile interval of its median."""

    first = next(iter(series.values()))
    n = len(first)
    out: Dict[str, object] = {}
    if reps <= 0 or n < MIN_DAYS:
        for name in series:
            out[f"{name}_mean"] = {"interval": None, "resamples": 0, "no_variance": None}
            out[f"{name}_median"] = None
        return out
    rng = random.Random(seed)
    indices = [metrics.stationary_bootstrap_indices(n, BLOCK, rng) for _ in range(reps)]
    for name, values in series.items():
        out[f"{name}_mean"] = _studentized(values, indices, (0.0, 1.0) if name in share else None)
        med = sorted(_median(list(map(values.__getitem__, picked))) for picked in indices)
        out[f"{name}_median"] = [_median(values), percentile(med, (1 - LEVEL) / 2), percentile(med, (1 + LEVEL) / 2)]
    return out


# -- the exploratory score interval -----------------------------------------------------------------------------------------------------


def design_effect(series: Sequence[float], *, cells: int) -> float:
    """The variance of the mean of the daily shares (Newey-West, Bartlett, lag 10) over the variance of a proportion of `cells` independent cells; at least 1.

    A series with no variation has no variance to read: the design effect is then held at 1."""

    n = len(series)
    p = sum(series) / n
    long_run = sp._long_run_variance(series, LAG)
    binomial = p * (1.0 - p) / cells
    if long_run <= 0.0 or binomial <= 0.0:
        return 1.0
    return max(1.0, (long_run / n) / binomial)


def score_interval(misses: int, cells: int, deff: float) -> List[float]:
    """The Wilson score interval of misses/cells at 90%, on cells / deff effective cells (so wider by sqrt(deff) than the independent one)."""

    n_eff = cells / deff
    p = misses / cells
    z2 = Z * Z
    denom = 1.0 + z2 / n_eff
    centre = (p + z2 / (2.0 * n_eff)) / denom
    half = Z * math.sqrt(p * (1.0 - p) / n_eff + z2 / (4.0 * n_eff * n_eff)) / denom
    return [max(0.0, centre - half), min(1.0, centre + half)]


# -- the split --------------------------------------------------------------------------------------------------------------------------


def _versus(interval: Optional[Sequence[Optional[float]]]) -> str:
    if interval is None or interval[0] is None:
        return "no interval"
    lo, hi = interval[0], interval[1]
    if lo > NOMINAL:
        return "above 0.05"
    if hi < NOMINAL:
        return "below 0.05"
    return "holds 0.05"


def entry(cells: Sequence[Mapping[str, object]], *, reps: int, seed: int) -> dict:
    """The figures of one group of cells: counts, the two miss shares (misses over cells) with both intervals, and the signed error."""

    s = day_series(cells)
    iv = intervals({"low": s["low"], "up": s["up"], "error": s["error"]}, reps=reps, seed=seed, share=("low", "up"))
    n_cells = len(cells)
    out = {"days": len(s["days"]), "cells": n_cells}
    for tail in ("low", "up"):
        misses = sum((c["y"] < c["q"][G05]) if tail == "low" else (c["y"] > c["q"][G95]) for c in cells)
        boot = iv[f"{tail}_mean"]
        interval = boot["interval"]
        scored = None
        deff = None
        if reps > 0 and len(s["days"]) >= MIN_DAYS:
            deff = design_effect(s[tail], cells=n_cells)
            scored = score_interval(misses, n_cells, deff)
        out[tail] = {
            "misses": misses, "share": misses / n_cells, "day_mean_share": sum(s[tail]) / len(s[tail]), "expected": NOMINAL * n_cells,
            "interval": None if interval is None else interval[1:], "vs_nominal": _versus(None if interval is None else interval[1:]),
            "resamples": boot["resamples"], "no_variance_resamples": boot["no_variance"],
            "design_effect": deff, "score_interval": scored, "score_vs_nominal": _versus(scored),
        }
    mean_error = iv["error_mean"]["interval"]
    out["median_error"] = iv["error_median"] or [_median(s["error"]), None, None]
    out["mean_error"] = mean_error or [sum(s["error"]) / len(s["error"]), None, None]
    return out


def split(cells: Sequence[Mapping[str, object]], *, reps: int, seed: int) -> Dict[str, Dict[str, dict]]:
    """{business day: {lead or 'all': entry}} for the cells whose target is business day 1, 2 or 3 of its month."""

    out: Dict[str, Dict[str, dict]] = {}
    for bday in BUSINESS_DAYS:
        mine = _cells_of(cells, bday)
        if not mine:
            continue
        leads = sorted({c["h"] for c in mine})
        out[str(bday)] = {str(h): entry([c for c in mine if c["h"] == h], reps=reps, seed=seed) for h in leads}
        out[str(bday)]["all"] = entry(mine, reps=reps, seed=seed)
    return out


def by_regime(cells: Sequence[Mapping[str, object]], *, reps: int, seed: int) -> Dict[str, Dict[str, dict]]:
    """{business day: {regime: entry (leads pooled) with a by-lead point table}}."""

    out: Dict[str, Dict[str, dict]] = {}
    for bday in BUSINESS_DAYS:
        mine = _cells_of(cells, bday)
        if not mine:
            continue
        out[str(bday)] = {}
        for regime in sorted({c["regime"] for c in mine}):
            sub = [c for c in mine if c["regime"] == regime]
            e = entry(sub, reps=reps, seed=seed)
            e["by_lead"] = {
                str(h): {k: v for k, v in entry([c for c in sub if c["h"] == h], reps=0, seed=seed).items() if k in ("days", "cells", "median_error")}
                | {"low": prior._point(sub, h, "low"), "up": prior._point(sub, h, "up")}
                for h in sorted({c["h"] for c in sub})
            }
            out[str(bday)][regime] = e
    return out


# -- the comparison with #1611 --------------------------------------------------------------------------------------------------------------


def _rows(result: Mapping[str, object]):
    d = result["windows"]["development"]
    for scope, by_day in d["scopes"].items():
        for bday, leads in by_day.items():
            for lead, e in leads.items():
                yield (f"{scope}", f"business day {bday}", "pooled" if lead == "all" else f"lead {lead}"), e
    for bday, regimes in d["by_regime"].items():
        for regime, e in regimes.items():
            yield ("by regime", f"business day {bday}", regime), e


def _r(interval: Optional[Sequence[Optional[float]]], places: int) -> Optional[list]:
    return None if interval is None else [None if x is None else round(x, places) for x in interval]


def compare(before: Mapping[str, object], after: Mapping[str, object]) -> List[dict]:
    """The development rows whose studentized share interval differs between #1611's figures (stored to 6 places) and these, with the reading before and
    after. `visible` is true when the difference shows at the 3 places the page prints or the reading against 0.05 changes."""

    old = dict(_rows(before))
    out = []
    for key, e in _rows(after):
        prev = old.get(key)
        if prev is None:
            continue
        for tail in ("low", "up"):
            b, a = _r(prev[tail]["interval"], 6), _r(e[tail]["interval"], 6)
            if b == a:
                continue
            changed = prev[tail]["vs_nominal"] != e[tail]["vs_nominal"]
            out.append({
                "scope": key[0], "target": key[1], "group": key[2], "tail": tail, "misses": e[tail]["misses"], "cells": e["cells"], "days": e["days"],
                "before": b, "after": a, "no_variance_resamples": e[tail].get("no_variance_resamples"),
                "reading_before": prev[tail]["vs_nominal"], "reading_after": e[tail]["vs_nominal"],
                "reading_changed": changed, "visible": changed or _r(b, 3) != _r(a, 3),
            })
    return out


def score_cells(window_cells: Mapping[str, Sequence[Mapping[str, object]]], *, reps: int = REPS, seed: int = SEED,
                previous: Optional[Mapping[str, object]] = None) -> dict:
    """The whole study from the cells of each window: the development window decides the reading, the 2026 days are shown apart as points."""

    out: dict = {"issue": 1614, "re_issues": 1611, "label": "development, not a verdict", "seed": seed, "reps": reps, "block": BLOCK, "lag": LAG,
                 "level": LEVEL, "min_days_for_interval": MIN_DAYS, "windows": {}}
    dev = window_cells.get("development", [])
    scopes = {
        "all": dev,
        "quarter_end": [c for c in dev if month_end_kind(date.fromisoformat(c["t"])) == "quarter_end"],
        "other": [c for c in dev if month_end_kind(date.fromisoformat(c["t"])) == "other"],
    }
    out["windows"]["development"] = {
        "scopes": {name: split(cells, reps=reps, seed=seed) for name, cells in scopes.items()},
        "by_regime": by_regime(dev, reps=reps, seed=seed),
    }
    out["windows"]["2026"] = {"scopes": {"all": split(window_cells.get("2026", []), reps=0, seed=seed)}}
    if previous is not None:
        out["changed_from_1611"] = compare(previous, out)
    return out


# -- the page ---------------------------------------------------------------------------------------------------------------------------

SCOPE_TITLES = prior.SCOPE_TITLES
table = prior.table


def _end(x: Optional[float], d: int = 3) -> str:
    return "unbounded" if x is None else f"{x:.{d}f}"


def iv(x: Optional[Sequence[Optional[float]]], d: int = 2) -> str:
    if x is None:
        return "no interval"
    if x[1] is None and x[2] is None:
        return f"{x[0]:.{d}f} (no interval)"
    return f"{x[0]:.{d}f} [{_end(x[1], d)}, {_end(x[2], d)}]"


def share(tail: Mapping[str, object]) -> str:
    text = f"{tail['misses']} ({tail['share']:.3f})"
    interval = tail["interval"]
    return text if interval is None else f"{text} [{_end(interval[0])}, {_end(interval[1])}]"


def score(tail: Mapping[str, object]) -> str:
    interval = tail["score_interval"]
    return "none" if interval is None else f"[{interval[0]:.3f}, {interval[1]:.3f}] (DEFF {tail['design_effect']:.1f})"


def _split_rows(res: Mapping[str, Mapping[str, dict]]) -> List[List[str]]:
    rows = []
    for bday, leads in res.items():
        for lead, e in leads.items():
            rows.append([f"business day {bday}", "pooled" if lead == "all" else lead, str(e["days"]), str(e["cells"]), share(e["low"]), score(e["low"]),
                         share(e["up"]), score(e["up"]), iv(e["median_error"]), iv(e["mean_error"])])
    return rows


SPLIT_HEADERS = ["target", "lead", "days", "cells", "below q05: misses (share) [studentized 90%]", "below q05: score 90% (exploratory)",
                 "above q95: misses (share) [studentized 90%]", "above q95: score 90% (exploratory)", "median error, bp [90%]", "mean error, bp [90%]"]


def page(r: Mapping[str, object]) -> str:
    d = r["windows"]["development"]
    L: List[str] = []
    w = L.append
    w("# The misses after a month-end, by business day 1, 2 and 3: re-issued with every resample kept (#1614)")
    w("")
    w("**Development, not a verdict.** H5, known limits of the frozen candidate (s3c-ann-net). This is a new dated version of the page of #1611 (merged as #1612); the old page and its "
      "`result.json` stand as published, with a dated note pointing here. No refit, no new arm, no change to the candidate, no lockbox day, no record in `docs/runs/` edited, "
      "nothing registered. Implements her docket rulings of 15 November 2026: finding #1613, option (a), with the second interval added in chat, and #1612, option (a). Every figure is read "
      "from `docs/research/post-month-end-corrected-1614/result.json`; the script is `scripts/post_month_end_corrected_1614.py`, the test `tests/test_post_month_end_corrected_1614.py`. "
      "The forecasts are the walks of #1547 and #1555 (the 1363 walk, regenerated and checked against its sha256).")
    w("")
    w("**Prior work** (`docs/research/settled-questions.md`, 15 November). S18 (#1275, failed) and #1547 cover location in aggregate; #1611 is the business-day split this page corrects. "
      "No entry covers miss-share intervals for rows that can draw no miss, so this is a new question.")
    w("")
    changed = r.get("changed_from_1611")
    w("## What changed from #1611")
    w("")
    w("**The rule, stated.** The studentized bootstrap is scoring protocol v1's (10,000 draws, mean block 10, Newey-West lag 10, 90%, seed 1611, the same resample stream as #1611), applied to "
      "the group's target days in date order. **Every resample is kept**, including those that draw no miss. A resample with no variance has no standard error: its studentized value is "
      "-infinity if its mean is below the observed share, +infinity if above, 0 on a tie. So the upper end of a share's interval can reach 1 (the page prints 1.000), and an unclipped end that is "
      "unbounded prints as 'unbounded'. #1611 dropped those resamples and reported an interval while at least 90% remained; the protocol's scorer refuses such a resample instead of skipping it. "
      "A group with no miss in the data has no studentized interval, as in the protocol. A group under "
      f"{r['min_days_for_interval']} target days has none either. The median error's interval is the percentile interval of the resampled medians, as before.")
    w("")
    w("**The share column.** A share printed beside a cell count is misses over cells. #1611's 2026 table printed the mean of each day's own share, which differs when days have unequal numbers "
      "of cells. The development windows have five cells on every day, where the two agree (checked at scoring).")
    w("")
    w("**A second interval, exploratory.** Beside each studentized interval is a Wilson score interval of the share on an effective number of cells, N / DEFF (N the cells; DEFF the Newey-West "
      "variance of the mean of the daily shares at lag 10 over the variance of a proportion of N independent cells, never below 1). It is built for rare events (it keeps a lower end at 0 and an upper "
      "end above 0 with no miss) and corrects for the five leads of a day and for the dependence between days. It is exploratory: it is not the protocol's interval and not a calibrated one, with no "
      "miss DEFF is not estimable and is held at 1 (too narrow if misses would cluster), and lag 10 on non-consecutive monthly days is a choice of this page. Which interval the project uses for "
      "such shares is her decision, put as a question in the pull request; nothing here settles it.")
    w("")
    if changed is not None:
        shown = [c for c in changed if c["visible"]]
        w("**Rows that moved** (development window, against #1611's figures). Listed: every share interval whose printed figures differ or whose reading against 0.05 changes. Every share interval "
          "not listed is as #1611 published it, or differs only beyond the third decimal (all of them are in `result.json`, `changed_from_1611`). A reading of 'holds 0.05' that rests on an upper end of 1.000 carries no information: it says the "
          "share cannot be bounded from above on so few misses.")
        w("")
        rows = []
        for c in shown:
            rows.append([c["scope"], c["target"], c["group"], "below q05" if c["tail"] == "low" else "above q95", f"{c['misses']} of {c['cells']}",
                         "none" if c["before"] is None else f"[{c['before'][0]:.3f}, {c['before'][1]:.3f}]",
                         "none" if c["after"] is None else f"[{_end(c['after'][0])}, {_end(c['after'][1])}]",
                         str(c["no_variance_resamples"]), c["reading_before"], c["reading_after"] + (" (changed)" if c["reading_changed"] else "")])
        L += table(["scope", "target", "group", "tail", "misses", "#1611 interval", "interval here", "resamples with no miss", "reading then", "reading now"], rows)
        w("")
    w("## Note of 15 November 2026 under the post-month-end known limit")
    w("")
    w("For the known limit \"Post-month-end band coverage\" of `docs/model/candidate.json` (the validation report states no figure, so the figures are quoted here and the limit's source list points to this page). "
      "Development data, no change to the candidate.")
    w("")
    pooled = d["scopes"]["all"]
    for bday, tail, name in (("1", "up", "above q95"), ("2", "up", "above q95"), ("3", "low", "below q05")):
        e = pooled.get(bday, {}).get("all", {}).get(tail)
        if e is None or e["interval"] is None:
            continue
        w(f"- Business day {bday}, {name}, all month-ends, leads pooled: {e['misses']} misses in {pooled[bday]['all']['cells']} cells ({e['share']:.3f}); studentized 90% interval "
          f"[{_end(e['interval'][0])}, {_end(e['interval'][1])}]; exploratory score interval {score(e)}.")
    reg = d["by_regime"].get("2", {}).get("2021-23")
    if reg is not None and reg["low"]["interval"] is not None:
        was = next((c for c in (changed or []) if (c["scope"], c["target"], c["group"], c["tail"]) == ("by regime", "business day 2", "2021-23", "low")), None)
        before = "" if was is None or was["before"] is None else f"#1611 showed [{was['before'][0]:.3f}, {was['before'][1]:.3f}] ({was['reading_before']}); "
        w(f"- Business day 2, 2021-23, below q05, leads pooled ({reg['low']['misses']} misses in {reg['cells']} cells): {before}with every resample kept the studentized interval is "
          f"[{_end(reg['low']['interval'][0])}, {_end(reg['low']['interval'][1])}] and the exploratory score interval is {score(reg['low'])}.")
    pooled_moves = [c for c in (changed or []) if c["group"] == "pooled" and c["reading_changed"]]
    if not pooled_moves:
        w("- No pooled row of the by-business-day reading table changes its reading.")
    for c in pooled_moves:
        w(f"- Pooled row that changes its reading: {c['scope']}, {c['target']}, {'below q05' if c['tail'] == 'low' else 'above q95'}: {c['reading_before']} to {c['reading_after']} "
          f"(interval [{_end(c['after'][0])}, {_end(c['after'][1])}]).")
    w("")
    w("## What is measured")
    w("")
    w("A target day is business day b when `derived_features.bday_of_month` is b, the count the candidate's `post_month_end_window` term reads. For each business day and lead: the cells whose outcome "
      "fell below the forecast q05 and above its q95 (the strict miss; nominal share 0.05), and the signed error y - q50 in bp, as a median and as a mean. A pooled figure alone is not a result: the pooled "
      "row sits beside the five leads, and every regime is split below.")
    w("")
    w("## Reading, by business day")
    w("")
    w("Mechanical, from the pooled rows of the development window: whether each interval of the miss share excludes the nominal 0.05, and whether the interval of the median error excludes 0.")
    w("")
    rows = []
    for scope in ("all", "quarter_end", "other"):
        for bday, leads in d["scopes"][scope].items():
            e = leads["all"]
            med = e["median_error"]
            where = "no interval" if med[1] is None else ("excludes 0" if med[1] > 0 or med[2] < 0 else "holds 0")
            rows.append([SCOPE_TITLES[scope].split(" (")[0], f"business day {bday}", str(e["days"]), e["low"]["vs_nominal"], e["low"]["score_vs_nominal"], e["up"]["vs_nominal"],
                         e["up"]["score_vs_nominal"], where])
    L += table(["scope", "target", "days", "below q05, studentized", "below q05, score", "above q95, studentized", "above q95, score", "median error interval"], rows)
    w("")
    for scope in ("all", "quarter_end", "other"):
        w(f"## {SCOPE_TITLES[scope]}")
        w("")
        L += table(SPLIT_HEADERS, _split_rows(d["scopes"][scope]))
        w("")
    w("## By regime (leads pooled)")
    w("")
    w("All month-ends, one row per business day and regime; the lead rows beside are points (misses of cells at that lead). A regime with under "
      f"{r['min_days_for_interval']} target days has no interval.")
    w("")
    rows = []
    for bday, regimes in d["by_regime"].items():
        for regime, e in regimes.items():
            leads = "; ".join(f"h{h}: {v['low']['misses']}/{v['up']['misses']} of {v['cells']}" for h, v in e["by_lead"].items())
            rows.append([f"business day {bday}", regime, str(e["days"]), str(e["cells"]), share(e["low"]), score(e["low"]), share(e["up"]), score(e["up"]), iv(e["median_error"]), leads])
    L += table(["target", "regime", "days", "cells", "below q05: misses (share) [studentized 90%]", "below q05: score 90% (exploratory)", "above q95: misses (share) [studentized 90%]",
                "above q95: score 90% (exploratory)", "median error, bp [90%]", "low/up misses by lead"], rows)
    w("")
    w("## The 2026 days (shown apart, decide nothing)")
    w("")
    w("Points only: no interval, and no bootstrap is run on these days. The share is misses over cells.")
    w("")
    rows = []
    for bday, leads in r["windows"]["2026"]["scopes"]["all"].items():
        for lead, e in leads.items():
            rows.append([f"business day {bday}", "pooled" if lead == "all" else lead, str(e["days"]), str(e["cells"]), f"{e['low']['misses']} ({e['low']['share']:.3f})",
                         f"{e['up']['misses']} ({e['up']['share']:.3f})", f"{e['median_error'][0]:.2f}"])
    L += table(["target", "lead", "days", "cells", "below q05: misses (share)", "above q95: misses (share)", "median error, bp"], rows)
    w("")
    w("## Limits and what was not checked")
    w("")
    w("- Development data on days already seen, never a verdict; the 2026 days decide nothing.")
    w("- The five leads of one target day are not independent, so the pooled and regime rows count a target day once in the resample and the cell counts are not the effective sample.")
    w("- Per business day and lead a group holds under one hundred target days, so under five expected misses at the 0.05 level in most cells: an interval that holds 0.05 is not evidence that the share is 0.05, "
      "and an upper end of 1.000 says only that so few misses cannot bound the share.")
    w("- The studentized bootstrap is the protocol's interval for a mean of paired daily differences; applied to a rare-event share and to a series of non-consecutive days it is this study's reading, not a calibrated one "
      "(the calibration of #656 did not cover it). The score interval is exploratory and has not been calibrated either.")
    w("- The error is the outcome less the published (capped) forecast median; the shape ratios of #1547 are not recomputed here.")
    w("- No arm is fitted or scored. If a figure here pointed at a change to the candidate or its registration (#1511), that goes to Eleonora, not into code.")
    w("")
    return "\n".join(L)


# -- the commands -----------------------------------------------------------------------------------------------------------------------


def score_command(args) -> int:
    record = json.loads(RECORD_1363.read_text(encoding="utf-8"))
    result_cells: Dict[str, list] = {}
    walk_files = {}
    panel = None
    for name in q.WINDOWS:
        window = q.load_window(name, Path(args.walks), Path(args.extensions), record)
        if window is None:
            continue
        check_flag_agreement(window.doc["targets"])
        check_unlocked(window.cells)
        result_cells[name] = window.cells
        panel = window.doc["panel_sha256"]
        walk_files[name] = {"sha256": window.ext["walk_sha256"], "refits": window.ext["walk_refits"]}
    if "development" not in result_cells:
        raise SystemExit("no development walk under --walks")
    check_cells_per_day(result_cells["development"])
    previous = json.loads(RECORD_1611.read_text(encoding="utf-8"))
    result = score_cells(result_cells, previous=previous)
    ref = json.loads(RECORD_1547.read_text(encoding="utf-8"))["windows"]["development"]["groups"]["post_month_end_window"]
    result["reproduces_1547"] = check_reproduction(result_cells["development"], ref)
    result.update({"panel_sha256": panel, "walk_files": walk_files, "no_refit": True, "panel_sha256_1611": previous.get("panel_sha256")})
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    Path(args.output).write_text(json.dumps(q.rounded(result), indent=1, sort_keys=True) + "\n", encoding="utf-8")
    return 0


def page_command(args) -> int:
    r = json.loads(Path(args.score).read_text(encoding="utf-8"))
    Path(args.output).write_text(page(r), encoding="utf-8")
    return 0


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="command", required=True)
    s = sub.add_parser("score", help="the split from the walk files and their extensions")
    s.add_argument("--walks", required=True)
    s.add_argument("--extensions", required=True)
    s.add_argument("--output", required=True)
    s.set_defaults(func=score_command)
    g = sub.add_parser("page", help="write the result page from a score file")
    g.add_argument("--score", required=True)
    g.add_argument("--output", required=True)
    g.set_defaults(func=page_command)
    args = parser.parse_args(argv)
    return int(args.func(args) or 0)


if __name__ == "__main__":
    raise SystemExit(main())
