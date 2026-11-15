"""The misses of (s3c-ann-net) on the days after a month-end, split by business day 1, 2 and 3 (#1611, H5, known limits).

A development diagnostic, never a verdict. It reads the candidate's existing development walks (the ones #1547 and #1555 read): no refit, no new
fit, no new arm, nothing registered. Her ruling of 14 November 2026 on #1605, option (a): the #1592 item 4 diagnostic is a split of the
post-month-end misses by business day 1, 2 and 3, not a location arm. The forecasts are `scripts/qe_diagnosis_1533.py`'s walk extension,
regenerated bit-identical from the 1363 walk (`load_window` refuses a walk whose sha256 differs from `docs/research/candidate-calibration-1363/
result.json`). No day after 2026-09-03 and no locked day is read (`check_unlocked`, `lockbox.require_unlocked`, on every decision and target day).

What is measured. A target day is "business day b after a month-end" when `derived_features.bday_of_month` is b (b = 1, 2, 3): the same count the
`post_month_end_window` term of the candidate reads, which `check_flag_agreement` checks against the walk file's own flag. Per business day and per
lead (1 to 5, and the five pooled): the number of target days and cells; the strict share of cells below the forecast's q05 and above its q95
(nominal 0.05); the signed error y - q50 (the outcome less the published forecast median, in bp), as a median and as a mean. A month-end that is a
quarter-end (the target falls in January, April, July or October) is shown apart from the others. Regimes are the protocol's (`splits.regime`).

Intervals (90%, seed 1611). Scoring protocol v1's studentized stationary bootstrap, as `scoring_protocol` reads it: mean block 10, 10,000 draws,
each resample's mean studentized by its own Newey-West standard error at lag 10, the interval the observed mean less the 95% and 5% quantiles of the
t-draws times the observed standard error, clipped to [0, 1] for a share. The resampled series is the group's target days in date order (the days
are not consecutive, so the block length is in group days). A series with no variation (no miss at all) has no standard error: it is reported with
no interval and the count. The signed median error has no standard error to studentize by: its interval is the percentile interval of the resampled
medians, on the same resamples. A group with fewer than 20 target days gets no interval.

    PYTHONPATH=src python3 -m repo_model.cli build --raw-root tests/fixtures/snapshots/funding_inputs --output PUB.csv \\
        --build-cutoff 2026-09-08T21:31:42+00:00 --decision-time 18:00:00
    for W in development 2026; do
      RMM_DECISION_TIME=18:00 PYTHONPATH=src python3 scripts/qe_diagnosis_1533.py walk --panel PUB.csv --window $W \\
          --output WALK/$W.json --extension EXT/$W.json
    done
    OUT=docs/research/post-month-end-split-1611
    PYTHONPATH=src python3 scripts/post_month_end_split_1611.py score --walks WALK --extensions EXT --output $OUT/result.json
    PYTHONPATH=src python3 scripts/post_month_end_split_1611.py page --score $OUT/result.json \\
        --output docs/research/post-month-end-split-1611-result.md

The walks take about three and a half minutes in all (#1547); the scoring below the `long-run` line. Stdlib only.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import math
import random
import sys
from collections import defaultdict
from datetime import date
from pathlib import Path
from typing import Dict, List, Mapping, Optional, Sequence

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))

from repo_model import derived_features, lockbox, metrics, scoring_protocol as sp  # noqa: E402

RECORD_1363 = REPO / "docs" / "research" / "candidate-calibration-1363" / "result.json"
RECORD_1547 = REPO / "docs" / "research" / "calendar-tail-diagnostic-1547" / "result.json"
TOLERANCE = 1e-5
WHERE = "post_month_end_split_1611"
SEED = 1611
REPS = sp.DRAWS
BLOCK = sp.BLOCK_LENGTH
LAG = sp.HAC_LAG
LEVEL = 0.90
MIN_DAYS = 20
BUSINESS_DAYS = (1, 2, 3)
NOMINAL = 0.05
QUARTER_END_TARGET_MONTHS = (1, 4, 7, 10)


def _load(name: str, alias: str):
    spec = importlib.util.spec_from_file_location(alias, REPO / "scripts" / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[alias] = module
    spec.loader.exec_module(module)
    return module


q = _load("qe_diagnosis_1533", "qe_diagnosis_1533_in_1611")
G05, G50, G95 = q.G[0.05], q.G[0.5], q.G[0.95]


# -- the calendar -----------------------------------------------------------------------------------------------------------------------


def business_day(day: date) -> int:
    """The market day of the month of `day` (`derived_features.bday_of_month`: 1 for the first market day, 0 on a market holiday)."""

    return int(derived_features.bday_of_month(day))


def month_end_kind(day: date) -> str:
    """'quarter_end' when the month-end before `day` closed a quarter (the target falls in January, April, July or October), else 'other'."""

    return "quarter_end" if day.month in QUARTER_END_TARGET_MONTHS else "other"


# -- the guards -------------------------------------------------------------------------------------------------------------------------


def check_unlocked(cells: Sequence[Mapping[str, object]]) -> None:
    """Refuse (`LookAheadError`) a decision or target day in a locked tier of `metadata/lockbox.json`."""

    days = {date.fromisoformat(c[key]) for c in cells for key in ("d", "t")}
    lockbox.require_unlocked(days, where=WHERE)


def check_flag_agreement(targets: Mapping[str, Mapping[str, object]]) -> None:
    """Refuse (`ValueError`) unless the walk file's `post_month_end_window` flag is exactly 'business day 3 or earlier' on every target day."""

    for t, meta in targets.items():
        flagged = "post_month_end_window" in meta["types"]
        counted = business_day(date.fromisoformat(t)) <= 3
        if flagged != counted:
            raise ValueError(f"{t}: the walk file's post_month_end_window flag is {flagged}, the business-day count says {counted}")


def check_reproduction(cells: Sequence[Mapping[str, object]], reference: Mapping[str, object]) -> dict:
    """Refuse (`ValueError`) unless the cells of business day 1 to 3 give #1547's post_month_end_window group: its cell count and its two miss shares."""

    mine = [c for c in cells if 1 <= business_day(date.fromisoformat(c["t"])) <= 3]
    low = sum(c["y"] < c["q"][G05] for c in mine) / len(mine)
    up = sum(c["y"] > c["q"][G95] for c in mine) / len(mine)
    theirs = {"cells": reference["cells"], "low": reference["paired"]["miss_q05_low"][0], "up": reference["paired"]["miss_q95_up"][0]}
    # the reference stores its shares rounded to 6 places
    if len(mine) != theirs["cells"] or abs(low - theirs["low"]) > TOLERANCE or abs(up - theirs["up"]) > TOLERANCE:
        raise ValueError(f"business days 1 to 3 do not reproduce #1547's post_month_end_window group: {len(mine)} cells, {low}, {up} against {theirs}")
    return {"cells": len(mine), "low": low, "up": up}


# -- the series and the intervals -------------------------------------------------------------------------------------------------------


def day_series(cells: Sequence[Mapping[str, object]]) -> Dict[str, list]:
    """One value per target day (the mean over its cells): the strict miss below q05 and above q95, and the signed error y - q50."""

    by: Dict[str, List[Mapping[str, object]]] = defaultdict(list)
    for c in cells:
        by[c["t"]].append(c)
    days = sorted(by)
    out: Dict[str, list] = {"days": days, "low": [], "up": [], "error": []}
    for t in days:
        group = by[t]
        n = len(group)
        out["low"].append(sum(c["y"] < c["q"][G05] for c in group) / n)
        out["up"].append(sum(c["y"] > c["q"][G95] for c in group) / n)
        out["error"].append(sum(c["y"] - c["q"][G50] for c in group) / n)
    return out


def _percentile(ordered: Sequence[float], p: float) -> float:
    position = p * (len(ordered) - 1)
    lo = int(math.floor(position))
    hi = min(lo + 1, len(ordered) - 1)
    return ordered[lo] + (ordered[hi] - ordered[lo]) * (position - lo)


def _studentized(values: Sequence[float], indices: Sequence[Sequence[int]], bounds: Optional[Sequence[float]]) -> Optional[list]:
    n = len(values)
    mean = sum(values) / n
    variance = sp._long_run_variance(values, LAG)
    if variance <= 0.0:
        return None
    se = math.sqrt(variance / n)
    ts = []
    for picked in indices:
        resample = list(map(values.__getitem__, picked))
        v = sp._long_run_variance(resample, LAG)
        if v > 0.0:
            ts.append((sum(resample) / n - mean) / math.sqrt(v / n))
    if len(ts) < 0.9 * len(indices):
        return None
    ts.sort()
    lo, hi = mean - _percentile(ts, (1 + LEVEL) / 2) * se, mean - _percentile(ts, (1 - LEVEL) / 2) * se
    if bounds is not None:
        lo, hi = max(lo, bounds[0]), min(hi, bounds[1])
    return [mean, lo, hi]


def intervals(series: Mapping[str, Sequence[float]], *, reps: int, seed: int, share: Sequence[str] = ()) -> Dict[str, Optional[list]]:
    """90% intervals, one resample stream shared by every series: the studentized stationary bootstrap of each series' mean ('<name>_mean'; clipped
    to [0, 1] for the names in `share`) and the percentile interval of its median ('<name>_median'). None for a series that cannot carry one."""

    first = next(iter(series.values()))
    n = len(first)
    out: Dict[str, Optional[list]] = {}
    if reps <= 0 or n < MIN_DAYS:
        for name in series:
            out[f"{name}_mean"] = out[f"{name}_median"] = None
        return out
    rng = random.Random(seed)
    indices = [metrics.stationary_bootstrap_indices(n, BLOCK, rng) for _ in range(reps)]
    for name, values in series.items():
        out[f"{name}_mean"] = _studentized(values, indices, (0.0, 1.0) if name in share else None)
        med = sorted(_median(list(map(values.__getitem__, picked))) for picked in indices)
        out[f"{name}_median"] = [_median(values), _percentile(med, (1 - LEVEL) / 2), _percentile(med, (1 + LEVEL) / 2)]
    return out


def _median(values: Sequence[float]) -> float:
    ordered = sorted(values)
    mid = len(ordered) // 2
    return ordered[mid] if len(ordered) % 2 else (ordered[mid - 1] + ordered[mid]) / 2


def studentized_interval(values: Sequence[float], *, reps: int, seed: int) -> Optional[list]:
    """[mean, low, high] of one series by the studentized stationary bootstrap, or None (fewer than 20 values, or no variation)."""

    return intervals({"x": values}, reps=reps, seed=seed)["x_mean"]


def median_interval(values: Sequence[float], *, reps: int, seed: int) -> Optional[list]:
    """[median, low, high] of one series, the percentile interval of the resampled medians, or None (fewer than 20 values)."""

    return intervals({"x": values}, reps=reps, seed=seed)["x_median"]


# -- the split --------------------------------------------------------------------------------------------------------------------------


def entry(cells: Sequence[Mapping[str, object]], *, reps: int, seed: int) -> dict:
    """The figures of one group of cells: counts, the two miss shares and the signed error, with intervals."""

    s = day_series(cells)
    iv = intervals({"low": s["low"], "up": s["up"], "error": s["error"]}, reps=reps, seed=seed, share=("low", "up"))
    n_cells = len(cells)
    out = {"days": len(s["days"]), "cells": n_cells}
    for tail in ("low", "up"):
        misses = sum((c["y"] < c["q"][G05]) if tail == "low" else (c["y"] > c["q"][G95]) for c in cells)
        mean = iv[f"{tail}_mean"]
        out[tail] = {
            "misses": misses, "share": sum(s[tail]) / len(s[tail]), "expected": NOMINAL * n_cells,
            "interval": None if mean is None else mean[1:], "vs_nominal": _versus(mean),
        }
    out["median_error"] = iv["error_median"] or [_median(s["error"]), None, None]
    out["mean_error"] = iv["error_mean"] or [sum(s["error"]) / len(s["error"]), None, None]
    return out


def _versus(mean: Optional[Sequence[float]]) -> str:
    if mean is None:
        return "no interval"
    if mean[1] > NOMINAL:
        return "above 0.05"
    if mean[2] < NOMINAL:
        return "below 0.05"
    return "holds 0.05"


def _cells_of(cells: Sequence[Mapping[str, object]], bday: int) -> List[Mapping[str, object]]:
    return [c for c in cells if business_day(date.fromisoformat(c["t"])) == bday]


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
                | {"low": _point(sub, h, "low"), "up": _point(sub, h, "up")}
                for h in sorted({c["h"] for c in sub})
            }
            out[str(bday)][regime] = e
    return out


def _point(cells: Sequence[Mapping[str, object]], h: int, tail: str) -> dict:
    mine = [c for c in cells if c["h"] == h]
    misses = sum((c["y"] < c["q"][G05]) if tail == "low" else (c["y"] > c["q"][G95]) for c in mine)
    return {"misses": misses, "share": misses / len(mine)}


def score_cells(window_cells: Mapping[str, Sequence[Mapping[str, object]]], *, reps: int = REPS, seed: int = SEED) -> dict:
    """The whole study from the cells of each window: the development window decides the reading, the 2026 days are shown apart as points."""

    out: dict = {"issue": 1611, "label": "development, not a verdict", "seed": seed, "reps": reps, "block": BLOCK, "lag": LAG, "level": LEVEL,
                 "min_days_for_interval": MIN_DAYS, "windows": {}}
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
    later = window_cells.get("2026", [])
    out["windows"]["2026"] = {"scopes": {"all": split(later, reps=0, seed=seed)}}
    return out


# -- the page ---------------------------------------------------------------------------------------------------------------------------

SCOPE_TITLES = {
    "all": "All month-ends",
    "quarter_end": "After a quarter-end month-end (target in January, April, July or October)",
    "other": "After the other month-ends",
}


def iv(x: Optional[Sequence[float]], d: int = 2) -> str:
    if x is None:
        return "no interval"
    return f"{x[0]:.{d}f} (no interval)" if x[1] is None else f"{x[0]:.{d}f} [{x[1]:.{d}f}, {x[2]:.{d}f}]"


def share(tail: Mapping[str, object]) -> str:
    interval = tail["interval"]
    text = f"{tail['misses']} ({tail['share']:.3f})"
    return text if interval is None else f"{text} [{interval[0]:.3f}, {interval[1]:.3f}]"


def table(headers: Sequence[str], rows: Sequence[Sequence[str]]) -> List[str]:
    return ["| " + " | ".join(headers) + " |", "|" + "---|" * len(headers)] + ["| " + " | ".join(r) + " |" for r in rows]


def _split_rows(res: Mapping[str, Mapping[str, dict]]) -> List[List[str]]:
    rows = []
    for bday, leads in res.items():
        for lead, e in leads.items():
            rows.append([f"business day {bday}", "pooled" if lead == "all" else lead, str(e["days"]), str(e["cells"]), share(e["low"]), share(e["up"]),
                         iv(e["median_error"]), iv(e["mean_error"])])
    return rows


SPLIT_HEADERS = ["target", "lead", "days", "cells", "below q05: misses (share) [90%]", "above q95: misses (share) [90%]", "median error, bp [90%]", "mean error, bp [90%]"]


def page(r: Mapping[str, object]) -> str:
    d = r["windows"]["development"]
    L: List[str] = []
    w = L.append
    w("# The misses after a month-end, by business day 1, 2 and 3 (#1611)")
    w("")
    w("**Development, not a verdict.** H5, known limits of the frozen candidate (s3c-ann-net). No refit, no new arm, no change to the candidate or to the text of the known limit, "
      "no lockbox day, no record in `docs/runs/` edited, nothing registered. Implements her ruling of 14 November 2026 on #1605, option (a). Every figure is read from "
      "`docs/research/post-month-end-split-1611/result.json`; the script is `scripts/post_month_end_split_1611.py`, the test `tests/test_post_month_end_split_1611.py`. "
      "The forecasts are the walks of #1547 and #1555 (the 1363 walk, regenerated and checked against its sha256).")
    w("")
    w("**Prior work** (`docs/research/settled-questions.md`, 14 November). #1275 (failed: its location term acts only at lead 1 on business day 2) and #1547 (a level shift: the median interval holds 0) cover location "
      "in aggregate; neither splits the misses by business day. No entry covers this split, so it is a new question.")
    w("")
    w("**What is measured.** A target day is business day b when `derived_features.bday_of_month` is b, the count the candidate's `post_month_end_window` term reads. For each business day and lead: "
      "the cells whose outcome fell below the forecast q05 and above its q95 (the strict miss; nominal share 0.05), and the signed error y - q50 in bp, as a median and as a mean. "
      f"Intervals are 90%, scoring protocol v1's studentized stationary bootstrap ({r['reps']:,} draws, mean block {r['block']}, Newey-West lag {r['lag']}, seed {r['seed']}) on the group's target days "
      "in date order; the share's interval is clipped to [0, 1]. A group with no miss has no standard error, so no studentized interval (shown as 'no interval'); a group under "
      f"{r['min_days_for_interval']} target days has none either. The median error has no standard error to studentize by, so its interval is the percentile interval of the resampled medians. "
      "A pooled figure alone is not a result: the pooled row sits beside the five leads, and every regime is split below.")
    w("")
    w("## Reading, by business day")
    w("")
    w("Mechanical, from the pooled rows of the development window: whether the interval of each miss share excludes the nominal 0.05, and whether the interval of the median error excludes 0.")
    w("")
    rows = []
    for scope in ("all", "quarter_end", "other"):
        for bday, leads in d["scopes"][scope].items():
            e = leads["all"]
            med = e["median_error"]
            where = "no interval" if med[1] is None else ("excludes 0" if med[1] > 0 or med[2] < 0 else "holds 0")
            rows.append([SCOPE_TITLES[scope].split(" (")[0], f"business day {bday}", str(e["days"]), e["low"]["vs_nominal"], e["up"]["vs_nominal"], where])
    L += table(["scope", "target", "days", "below q05 share", "above q95 share", "median error interval"], rows)
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
            rows.append([f"business day {bday}", regime, str(e["days"]), str(e["cells"]), share(e["low"]), share(e["up"]), iv(e["median_error"]), leads])
    L += table(["target", "regime", "days", "cells", "below q05: misses (share) [90%]", "above q95: misses (share) [90%]", "median error, bp [90%]", "low/up misses by lead"], rows)
    w("")
    w("## The 2026 days (shown apart, decide nothing)")
    w("")
    w("Points only: no interval, and no bootstrap is run on these days.")
    w("")
    rows = []
    for bday, leads in r["windows"]["2026"]["scopes"]["all"].items():
        for lead, e in leads.items():
            rows.append([f"business day {bday}", "pooled" if lead == "all" else lead, str(e["days"]), str(e["cells"]), f"{e['low']['misses']} ({e['low']['share']:.3f})",
                         f"{e['up']['misses']} ({e['up']['share']:.3f})", f"{e['median_error'][0]:.2f}"])
    L += table(["target", "lead", "days", "cells", "below q05", "above q95", "median error, bp"], rows)
    w("")
    w("## Limits and what was not checked")
    w("")
    w("- Development data on days already seen, never a verdict; the 2026 days decide nothing.")
    w("- The five leads of one target day are not independent, so the pooled and regime rows count a target day once in the resample and the cell counts are not the effective sample.")
    w("- Per business day and lead a group holds under one hundred target days, so under five expected misses at the 0.05 level in most cells: an interval that holds 0.05 is not evidence that the share is 0.05.")
    w("- The studentized bootstrap is the protocol's interval for a mean of paired daily differences; applied to a rare-event share and to a series of non-consecutive days it is this study's reading, not a calibrated one (the calibration of #656 did not cover it).")
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
    result = score_cells(result_cells)
    ref = json.loads(RECORD_1547.read_text(encoding="utf-8"))["windows"]["development"]["groups"]["post_month_end_window"]
    result["reproduces_1547"] = check_reproduction(result_cells["development"], ref)
    result.update({"panel_sha256": panel, "walk_files": walk_files, "no_refit": True})
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
