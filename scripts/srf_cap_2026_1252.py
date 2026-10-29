"""Does the Standing Repo Facility cap SOFR and its 99th percentile since full allotment? The cap of #1241 on the 2026 development days (#1252;
H5 step 3, ledger item 60 on #1116).

A development study, never a verdict, and no choice is made on it. It writes JSON and Markdown to the paths it is given and nothing into
`docs/runs/`. Every choice is in `metadata/srf_cap_2026_1252.json`, which this script refuses to read unless it is committed and unchanged.
It adds no arm, no line and no cap: `scripts/srf_cap_1241.py` and `repo_model.srf_line` are loaded as they are, with the seed changed to the
declared 1252 (the shared paired-test and interval tasks read it), and the walk and the frame are #1229's (`scripts/s3_2026_check_1222.py`),
which is the only thing that reads the 2026 development days: targets 2 January to 3 September 2026, the near-blind tier open since the ruling
of 5 October 2026 (`metadata/lockbox.json`). The blind tier and every lockbox day are refused.

It measures (1) how often SOFR - IORB and SOFR's 99th percentile - IORB closed above the facility's line in three periods (before full
allotment, 11 to 31 December 2025, the 2026 window) and since full allotment, with exact binomial intervals, the largest exceedances and the
distribution of the gap to the line; (2) how often (s3)'s upper quantile levels sit above the line on the 2026 days, by lead; (3) each cap arm
against (s3), paired, on grid CRPS over h = 1..5 and upper-tail twCRPS (scoring protocol v1, the studentized stationary bootstrap, read on the
bound on mean d, her #1009 ruling, with the skill interval beside); and (4) a cross-check of October 2026 against repo-market-spillovers, which the
panel (built to 2026-09-03) cannot reach: the page says which days are missing and compares nothing.

The walk is minutes and the paired tests are the longer part, so the run is a cloud run (under the two-hour line of `long-run`). Commands, from a
clone of the branch:

    PYTHONPATH=src python3 -m repo_model.cli build --raw-root tests/fixtures/snapshots/funding_inputs \\
        --output PUB.csv --build-cutoff 2026-09-08T21:31:42+00:00 --decision-time 16:00:00
    PYTHONPATH=src python3 -m repo_model.cli verify-panel PUB.csv --manifest metadata/funding_panel_manifest.json
    PYTHONPATH=src python3 scripts/srf_cap_2026_1252.py score --panel PUB.csv --output docs/research/srf-cap-2026-1252/result.json
    PYTHONPATH=src python3 scripts/srf_cap_2026_1252.py page \\
        --score docs/research/srf-cap-2026-1252/result.json --output docs/research/srf-cap-2026-1252-result.md

Stdlib only.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import math
import sys
from datetime import date, datetime, timedelta, timezone
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
        return held  # another loader in this process already holds the alias: share it, so pickled task names stay one object (#1294)
    spec = importlib.util.spec_from_file_location(alias, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[alias] = module
    spec.loader.exec_module(module)
    return module


from repo_model import announced_iorb, measurement_fields as mf, onset, policy_events, srf_line  # noqa: E402
from repo_model import scoring_protocol as sp, spread_mr_calendar as cal, turn_days  # noqa: E402
from repo_model.baseline import panel_sha256  # noqa: E402
from repo_model.data import load_daily_panel  # noqa: E402
from repo_model.evaluation_splits import load_split_declaration  # noqa: E402
from repo_model.exploration import EXPLORATORY_END, require_exploratory_window  # noqa: E402

#: #1241's script, loaded under its own name so that the pickling of its pool tasks does not meet another test module's copy.
k = _load("srf_cap_1241", "srf_cap_1241_in_1252")
#: #1229's script: the walk, the frame and the span guard of the 2026 development days.
d1222 = _load("s3_2026_check_1222", "s3_2026_check_1222_in_1252")
c, s686 = k.c, k.s686

DECLARATION = REPO / "metadata" / "srf_cap_2026_1252.json"
SEED = 1252
k.SEED = SEED  # the paired-test and interval tasks of #1241 read the seed of their own module
LAST_DAY = EXPLORATORY_END
FIRST_TARGET = d1222.FIRST_TARGET
SNAPSHOTS = REPO / "tests" / "fixtures" / "snapshots" / "funding_inputs"
BUILD_CUTOFF = datetime(2026, 9, 8, 21, 31, 42, tzinfo=timezone.utc)
#: The periods of measure 1, in the declaration's order: name, first day, last day (inclusive).
PERIODS: Tuple[Tuple[str, date, date], ...] = (
    ("a", srf_line.FACILITY_EFFECTIVE, date(2025, 12, 10)),
    ("b", date(2025, 12, 11), date(2025, 12, 31)),
    ("c", FIRST_TARGET, LAST_DAY),
)
PERIOD_TITLES = {"a": "before full allotment (2021-07-29 to 2025-12-10)", "b": "full allotment, December 2025 (2025-12-11 to 2025-12-31)",
                 "c": "the 2026 window (2026-01-02 to 2026-09-03)", "since": "since full allotment (2025-12-11 to 2026-09-03)"}
SERIES = ("SOFR", "SOFR_p99")
SERIES_TITLES = {"SOFR": "SOFR - IORB", "SOFR_p99": "SOFR 99th percentile - IORB"}
LARGEST = 10
#: What repo-market-spillovers reports for October 2026 (the issue quotes its study 13 and study 02).
SPILLOVERS = {"peak_bp": 10, "peak_date": "2026-10-23", "mean_bp": 6.6}

MARGINS, PRIMARY, CAPS, ARMS = k.MARGINS, k.PRIMARY, k.CAPS, k.ARMS
S3, A, B1P = k.S3, k.A, k.B1P
BENCHMARKS, MODELS = k.BENCHMARKS, k.MODELS
METRIC_NAMES, DAY_TYPES, ORDINARY = k.METRIC_NAMES, k.DAY_TYPES, k.ORDINARY
MIN_GROUP_DAYS = k.MIN_GROUP_DAYS
KEY_LEVELS = k.KEY_LEVELS
LABELS, METRIC_TITLES = k.LABELS, k.METRIC_TITLES


def committed_declaration(path: Path = DECLARATION) -> dict:
    """The declaration, refused unless it is committed and unchanged since `HEAD`."""

    return s686.committed_declaration(path)


# -- the exact binomial interval ------------------------------------------------------------------------------------


def binom_cdf(x: int, n: int, p: float) -> float:
    """`P(X <= x)` for `X ~ Binomial(n, p)`, summed in logs so that a long series does not underflow."""

    if x < 0:
        return 0.0
    if x >= n:
        return 1.0
    if p <= 0.0:
        return 1.0
    if p >= 1.0:
        return 0.0
    log_p, log_q = math.log(p), math.log1p(-p)
    total = 0.0
    for i in range(x + 1):
        total += math.exp(math.lgamma(n + 1) - math.lgamma(i + 1) - math.lgamma(n - i + 1) + i * log_p + (n - i) * log_q)
    return min(1.0, total)


def clopper_pearson(x: int, n: int, level: float = 0.90) -> Tuple[float, float]:
    """The exact two-sided `level` interval for a share of `x` in `n`: the bounds are the `p` at which the tail probability is `(1-level)/2`.

    Raises:
        ValueError: `n` is not positive, or `x` is outside `0..n`.
    """

    if n <= 0 or not 0 <= x <= n:
        raise ValueError(f"need 0 <= x <= n and n > 0, got x={x}, n={n}")
    tail = (1.0 - level) / 2.0

    def solve(f, target: float) -> float:
        low, high = 0.0, 1.0
        for _ in range(100):
            mid = (low + high) / 2.0
            if f(mid) > target:  # f falls as p rises
                low = mid
            else:
                high = mid
        return (low + high) / 2.0

    lower = 0.0 if x == 0 else solve(lambda p: binom_cdf(x - 1, n, p), 1.0 - tail)  # P(X >= x | p) = tail
    upper = 1.0 if x == n else solve(lambda p: binom_cdf(x, n, p), tail)  # P(X <= x | p) = tail
    return lower, upper


# -- measure 1: the realised series ----------------------------------------------------------------------------------


def realised_days(values: Mapping[date, int], register: Sequence[policy_events.PolicyEntry], first: date, last: date) -> List[dict]:
    """The days of `values` in `first..last` that have a line, each with the line in force that day.

    Every day read passes the scored-days check (the last day 2026-09-03, the lockbox): a realised read is an outcome of the day, but a day
    after the declared end is not read. Mutation record in the module docstring of the test.

    Raises:
        LookAheadError: a day after `LAST_DAY` or in a locked tier.
    """

    days = sorted(t for t in values if first <= t <= last)
    s686.require_scored_days(days, LAST_DAY)
    out = []
    for t in days:
        line = k.realised_line(register, t)
        if line is None:
            continue
        out.append({"date": t, "value": values[t], "line": line})
    return out


def period_stats(days: Sequence[dict]) -> dict:
    """One series in one period: the days above the line, the share with its exact 90% interval, the largest exceedances, the gap to the line.

    `value` is in whole basis points. A day is above when `value` is strictly above `line`. The gap is `value - line`.

    Raises:
        ValueError: `days` is empty.
    """

    if not days:
        raise ValueError("no days")
    gaps = [d["value"] - d["line"] for d in days]
    above = [d for d in days if d["value"] > d["line"]]
    top = sorted(above, key=lambda d: (-(d["value"] - d["line"]), d["date"]))[:LARGEST]
    n = len(days)
    return {
        "days": n, "above": len(above), "share": len(above) / n, "interval": list(clopper_pearson(len(above), n)),
        "largest": [{"date": d["date"].isoformat(), "value": d["value"], "line": d["line"], "excess": d["value"] - d["line"]} for d in top],
        "gap_median": k.quantile7(gaps, 0.5), "gap_p90": k.quantile7(gaps, 0.9), "gap_p99": k.quantile7(gaps, 0.99), "gap_max": max(gaps),
        "within_1bp": sum(1 for g in gaps if abs(g) <= 1.0), "within_1bp_at_or_below": sum(1 for g in gaps if -1.0 <= g <= 0.0),
        "line_min": min(d["line"] for d in days), "line_max": max(d["line"] for d in days),
        "first": days[0]["date"].isoformat(), "last": days[-1]["date"].isoformat(),
    }


def intervals_overlap(a: Sequence[float], b: Sequence[float]) -> bool:
    return not (a[1] < b[0] or b[1] < a[0])


def changed(before: Mapping[str, object], since: Mapping[str, object]) -> bool:
    """The declared rule: full allotment changed how often a series crossed the line only if the exact 90% intervals of its share above before
    and since do not overlap."""

    return not intervals_overlap(before["interval"], since["interval"])


def ceiling_pattern(sofr: Mapping[str, object], p99: Mapping[str, object]) -> bool:
    """The declared rule for the pattern a firm ceiling predicts: no day of the 99th percentile above the line, its maximum gap at least -1 bp
    (it reaches the line), no day of SOFR above, and SOFR's maximum gap below the 99th percentile's."""

    return p99["above"] == 0 and p99["gap_max"] >= -1.0 and sofr["above"] == 0 and sofr["gap_max"] < p99["gap_max"]


def p99_minus_iorb(panel: Mapping[date, object], snapshots: Path, cutoff: datetime) -> Tuple[Dict[date, int], List[date]]:
    """SOFR's 99th percentile less the panel's IORB, in whole basis points, on every panel day that has a percentile; and the days (from the
    facility on) that have none, listed and never filled."""

    series = mf.series_from_snapshots(snapshots, {"SOFR_p99"}, cutoff)["SOFR_p99"]
    values: Dict[date, int] = {}
    missing: List[date] = []
    for day in sorted(panel):
        p99 = series.get(day)
        if p99 is None:
            if day >= srf_line.FACILITY_EFFECTIVE:
                missing.append(day)
            continue
        values[day] = onset.whole_bp(100.0 * (float(p99) - float(panel[day].values["iorb"])))
    return values, missing


def monthly_p99(values: Mapping[date, int]) -> Dict[str, dict]:
    """Per calendar month: the days, the mean, and the maximum with its (first) date."""

    months: Dict[str, List[date]] = {}
    for day in sorted(values):
        months.setdefault(f"{day.year:04d}-{day.month:02d}", []).append(day)
    out = {}
    for month, days in months.items():
        peak = max(days, key=lambda d: (values[d], -d.toordinal()))
        out[month] = {"days": len(days), "mean": sum(values[d] for d in days) / len(days), "max": values[peak], "max_date": peak.isoformat()}
    return out


def cross_check(p99: Mapping[date, int], line_on_23_october: Optional[float]) -> dict:
    """Measure 4: whether the panel reaches the days repo-market-spillovers reports (October 2026), and which days are missing."""

    last = max(p99)
    return {
        "panel_last_day": last.isoformat(), "missing_from": (last + timedelta(days=1)).isoformat(),
        "october_2026_days_in_panel": sum(1 for d in p99 if d.year == 2026 and d.month == 10),
        "spillovers": dict(SPILLOVERS), "register_line_2026_10_23": line_on_23_october,
    }


def answer_sentence(r: Mapping[str, object]) -> str:
    """The one sentence the page opens with, worded by the two declared rules and no stronger."""

    real, rules = r["realised"], r["rules"]

    def share(entry) -> str:
        lo, hi = entry["interval"]
        return f"{entry['above']} of {entry['days']} days ({100 * entry['share']:.1f}%, exact interval [{100 * lo:.1f}%, {100 * hi:.1f}%])"

    names = {"SOFR": "SOFR", "SOFR_p99": "its 99th percentile"}
    moved = [s for s in SERIES if rules["changed"][s]]

    def way(s: str) -> str:
        return "less often" if real[s]["since"]["share"] < real[s]["a"]["share"] else "more often"

    if len(moved) == 2:
        change = f"full allotment changed how often both crossed the line (SOFR {way('SOFR')}, its 99th percentile {way('SOFR_p99')}, since)"
    elif moved:
        s = moved[0]
        other = [x for x in SERIES if x != s][0]
        change = (f"full allotment changed how often {names[s]} crossed the line ({way(s)} since) but the counts do not show a change "
                  f"for {names[other]}")
    else:
        change = "the counts do not show a change in how often either crossed the line"
    if rules["ceiling_pattern"]["since"]:
        pattern = ("the pattern a firm ceiling predicts (the 99th percentile stopping at the line while SOFR stays below it) is present, "
                   "though a series that stays at or below a line is not by that fact capped by it")
    else:
        pattern = "the counts do not show the pattern a firm ceiling predicts (the 99th percentile stopping at the line while SOFR stays below it)"
    return (f"Since full allotment (11 December 2025 to 3 September 2026) SOFR closed above the facility's line on {share(real['SOFR']['since'])} "
            f"and its 99th percentile on {share(real['SOFR_p99']['since'])}, against {share(real['SOFR']['a'])} and {share(real['SOFR_p99']['a'])} "
            f"before (exact 90% intervals); {change}; and {pattern}.")


# -- the score ------------------------------------------------------------------------------------------------------


def build(panel, splits, registry, table, register, first: Optional[date]):
    """#1229's frame with the three cap arms of #1241 added to (s3), and (a) left out: the walk produces it and it is not scored here."""

    frame, notes, mine = d1222.build_frame(panel, splits, registry, table, first)
    lines = k.lines_of(frame, register)
    s3 = frame.forecasts[S3]
    frame.forecasts.pop(A, None)
    for arm in CAPS:
        frame.forecasts[arm] = k.capped(s3, lines, MARGINS[arm])
    return frame, notes, mine, lines


def groups_of(frame, labels, pressure: Mapping[date, str]):
    """`(split, label, grain, members)`: pooled, by lead, by target month, by pressure-day type and by calendar target-day type."""

    out = d1222.groups_of(frame, labels)
    by_type: Dict[str, List[date]] = {}
    for t in sorted(pressure):
        by_type.setdefault(pressure[t], []).append(t)
    for label in sorted(by_type):
        out.append(("pressure_day_type", label, "target", by_type[label]))
    return out


def realised_block(panel_rows: Sequence, register) -> Tuple[dict, dict, Dict[date, int], List[date]]:
    """Measure 1 and the figures the cross-check needs: per series and period, `period_stats`; the rules; the monthly 99th percentile."""

    by_date = {r.date: r for r in panel_rows}
    spread = {r.date: onset.whole_bp(r.spread_bps) for r in panel_rows if r.date >= srf_line.FACILITY_EFFECTIVE}
    p99, missing = p99_minus_iorb(by_date, SNAPSHOTS, BUILD_CUTOFF)
    values = {"SOFR": spread, "SOFR_p99": {d: v for d, v in p99.items() if d >= srf_line.FACILITY_EFFECTIVE}}
    realised: Dict[str, dict] = {}
    for series in SERIES:
        days = {name: realised_days(values[series], register, first, last) for name, first, last in PERIODS}
        days["since"] = days["b"] + days["c"]
        realised[series] = {name: period_stats(rows) for name, rows in days.items()}
    rules = {
        "changed": {s: changed(realised[s]["a"], realised[s]["since"]) for s in SERIES},
        "ceiling_pattern": {name: ceiling_pattern(realised["SOFR"][name], realised["SOFR_p99"][name]) for name in ("a", "b", "c", "since")},
    }
    return realised, rules, p99, missing


def score(args) -> int:
    declaration = committed_declaration()
    panel_path = Path(args.panel)
    published_sha = panel_sha256(panel_path)
    panel = [row for row in load_daily_panel(panel_path) if row.date <= LAST_DAY]
    require_exploratory_window([row.date for row in panel], where="scripts/srf_cap_2026_1252")
    splits = load_split_declaration(c.SPLITS)
    registry = json.loads(c.SOURCES.read_text(encoding="utf-8"))
    register = policy_events.load_register()
    table = cal.TermTable(panel, announced_iorb.load_announcements(c.IORB_TABLE), decision_time=c.DECISION_TIME)
    frame, notes, mine, lines = build(panel, splits, registry, table, register, args.first)
    labels = c.day_labels(frame, table)
    targets = sorted(labels)
    pressure = k.pressure_labels(frame, targets)

    cells = {m: d1222.cell_table(frame, frame.forecasts[m]) for m in MODELS}
    for m in MODELS:
        official = sp.day_scores(frame.forecasts[m], frame.outcome, frame.dates, score=sp.grid_crps)
        mean = s686.by_decision(cells[m]["grid_crps"])
        if set(official) != set(mean) or any(abs(official[d] - mean[d]) > 1e-9 for d in mean):
            raise SystemExit(f"grid CRPS of {m}: the cell means differ from scoring_protocol.day_scores")

    groups = groups_of(frame, labels, pressure)
    series: Dict[Tuple[str, str], Dict[str, Dict[date, float]]] = {}
    for _s, _l, grain, _m in groups:
        for metric in METRIC_NAMES:
            if (grain, metric) not in series:
                series[(grain, metric)] = {m: c.series_of(frame, cells[m][metric], grain) for m in MODELS}
    k._STATE.update(series=series, draws=args.draws, reps=args.reps)

    jobs, skipped = [], {}
    for split, label, grain, members in groups:
        if len(members) < MIN_GROUP_DAYS:
            skipped[f"{split}/{label}"] = len(members)
            continue
        for metric in METRIC_NAMES:
            for candidate in ARMS:
                jobs.append(("pairs", (split, label, grain, metric, candidate, tuple(members))))
                if candidate != S3 and split == "pooled":
                    jobs.append(("block", (split, label, grain, metric, candidate, tuple(members))))
    forecast = k.forecast_tables(k.forecast_cells(frame, lines, pressure), jobs)
    done = k.run_jobs(jobs, args.workers)

    realised, rules, p99, missing = realised_block(panel, register)
    window_p99 = {d: v for d, v in p99.items() if FIRST_TARGET <= d <= LAST_DAY}
    try:
        october_line = k.realised_line(register, date(2026, 10, 23))
    except ValueError:
        october_line = None
    check = cross_check(p99, october_line)
    check["monthly_2026"] = monthly_p99(window_p99)

    by_key = {(s_, l_): (g, m) for s_, l_, g, m in groups}
    result: dict = {
        "issue": 1252, "declaration": str(DECLARATION.relative_to(REPO)), "panel_sha256": published_sha,
        "subset_from": None if args.first is None else args.first.isoformat(), "label": "development, not a verdict",
        "seed": SEED, "draws": args.draws, "reps": args.reps, "notes": notes, "models": list(MODELS), "primary": PRIMARY,
        "arms": [{"name": S3, "margin_bp": None}] + [{"name": a, "margin_bp": MARGINS[a]} for a in CAPS],
        "refits": len(mine.fits), "groups": {}, "skipped_groups": skipped, "politis_white": {}, "forecast": forecast,
        "realised": realised, "rules": rules, "p99_missing_days": [d.isoformat() for d in missing], "cross_check": check,
        "reading_rules": declaration["reading_rules"], "line": k.line_segments(register, frame),
    }
    for kind, (ident, payload) in done:
        if kind == "pairs":
            split, label, metric, candidate = ident
            entry = result["groups"].setdefault(split, {}).setdefault(label, {"days": len(by_key[(split, label)][1])})
            entry.setdefault(metric, {"means": {}, "vs": {}})["vs"][candidate] = payload
        elif kind == "block":
            split, label, metric, candidate = ident
            result["politis_white"].setdefault(split, {}).setdefault(label, {}).setdefault(metric, {})[candidate] = payload
        else:
            tag, key = ident
            name, lead, level = key
            forecast["splits"][name][lead]["interval"][level] = payload
    for split, labels_ in result["groups"].items():
        for label, entry in labels_.items():
            grain, members = by_key[(split, label)]
            for metric in METRIC_NAMES:
                if metric in entry:
                    ser = series[(grain, metric)]
                    entry[metric]["means"] = {m: sum(ser[m][d] for d in members) / len(members) for m in MODELS}
    result["day_type_counts"] = {x: sum(1 for t in labels if x in labels[t]) for x in DAY_TYPES + (ORDINARY,)}
    result["pressure_day_type_counts"] = {x: sum(1 for t in pressure.values() if t == x) for x in sorted(set(pressure.values()))}
    result["month_counts"] = {label: len(members) for split, label, _g, members in groups if split == "month"}
    result["against_1229"] = against_1229(result) if args.first is None else None
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    Path(args.output).write_text(json.dumps(result, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    return 0


RECORD_1229 = REPO / "docs" / "research" / "s3-2026-check-1222" / "result.json"


def against_1229(result: Mapping[str, object]) -> Optional[dict]:
    """(s3)'s pooled mean scores here against #1229's record: the walk is the same, so the figures should agree to the last digits."""

    if not RECORD_1229.exists():
        return None
    there = json.loads(RECORD_1229.read_text(encoding="utf-8"))["groups"]["pooled"]["all decision days"]
    here = result["groups"]["pooled"]["all decision days"]
    out = {}
    for metric in METRIC_NAMES:
        a, b = here[metric]["means"][S3], there[metric]["means"][S3]
        out[metric] = {"here": a, "in_1229": b, "difference": a - b}
    return out


# -- the page -------------------------------------------------------------------------------------------------------


def _share(entry: Mapping[str, object]) -> str:
    return k._pct_ci(entry["share"], entry["interval"])


def realised_table(r: Mapping[str, object], series: str) -> List[str]:
    out = ["| period | days | above the line | share [exact 90%] | gap to the line (bp): median | 90th | 99th | max | within 1 bp (at or below) | line (bp) |",
           "|---|---|---|---|---|---|---|---|---|---|"]
    for name in ("a", "b", "c", "since"):
        e = r["realised"][series][name]
        line = f"{e['line_min']:+.0f}" if e["line_min"] == e["line_max"] else f"{e['line_min']:+.0f} to {e['line_max']:+.0f}"
        out.append(f"| {PERIOD_TITLES[name]} | {e['days']} | {e['above']} | {_share(e)} | {e['gap_median']:+.1f} | {e['gap_p90']:+.1f} | "
                   f"{e['gap_p99']:+.1f} | {e['gap_max']:+.1f} | {e['within_1bp']} ({e['within_1bp_at_or_below']}) | {line} |")
    return out


def largest_table(r: Mapping[str, object], series: str, period: str, count: int) -> List[str]:
    rows = r["realised"][series][period]["largest"][:count]
    if not rows:
        return ["No day above the line.", ""]
    out = ["| date | value (bp) | line (bp) | excess (bp) |", "|---|---|---|---|"]
    out += [f"| {x['date']} | {x['value']:+d} | {x['line']:+.0f} | {x['excess']:+.0f} |" for x in rows]
    return out + [""]


def summary_rows(r: Mapping[str, object]) -> List[str]:
    out = ["| arm | split | grid CRPS vs (s3) | twCRPS vs (s3) |", "|---|---|---|---|"]
    keys = [("pooled", "all decision days", "all decision days")] + [("pressure_day_type", x, f"pressure-day type {x}") for x in sorted(r["groups"].get("pressure_day_type", {}))]
    for arm in CAPS:
        for split, label, text in keys:
            entry = r["groups"].get(split, {}).get(label)
            if entry is None or "grid_crps" not in entry:
                continue
            g, t = entry["grid_crps"]["vs"].get(arm, {}).get(S3), entry["upper_tail_twcrps"]["vs"].get(arm, {}).get(S3)
            out.append(f"| {LABELS[arm]} | {text} ({entry['days']} days) | {k._fmt(g)}: **{k.reading_words(g)}** | {k._fmt(t)}: **{k.reading_words(t)}** |")
    return out


def render(r: dict) -> str:
    n = r["notes"]
    real = r["realised"]
    out = [
        "# Does the Standing Repo Facility cap SOFR since full allotment? (#1252)", "",
        "**Does the facility cap SOFR, and its 99th percentile, since full allotment?** " + answer_sentence(r), "",
        "**Hypothesis and step:** H5 (primary goal), step 3 (the candidate's upper tail), ledger item 60 on #1116. **Development data, not a verdict** "
        f"(scoring protocol v1, #640): target days 2026-01-02 to {n['last_target']} for the scores, no lockbox day (the near-blind tier is open since "
        "5 October 2026, `metadata/lockbox.json`). Nothing is adopted and no claim changes. Generated by `scripts/srf_cap_2026_1252.py page` from "
        f"`docs/research/srf-cap-2026-1252/result.json`, not edited by hand; declared in `{r['declaration']}` before any number.", "",
        "**What kind of look this is.** The 2026 days were already seen by #845, by the #151 final test and by #1229. This is a check, not evidence for a "
        "verdict or a choice, and no arm, line or setting is new: the line, the cap and the three margins are #1241's, run again on the days it did not "
        "reach. On 10 December 2025 (effective 11 December) the Fed removed the facility's aggregate limit and moved it to full allotment at the top of "
        "the range (`metadata/policy_events.json`, `standing_repo-20251210`). Part 1 asks whether SOFR and its 99th percentile have crossed the "
        "facility's line less often since; it is a description of counts, and a series that stays at or below a line is not by that fact capped by it "
        "(there is no counterfactual here).", "",
        f"Panel digest `{r['panel_sha256']}`. Models: (s3) of #1145 refit walk-forward as #1229 did ({r['refits']} refits), the three cap arms "
        "(`min(q, line + margin)` with margins 0, 5 and 10 bp; the primary is the margin of 0, named in #1241's declaration before any score), B1, B1' "
        f"(#960) and B2. Scored decision days: {n['scored_decision_days']:,} ({n['first']} to {n['last']}); B2 refused "
        f"{len(n['benchmark_missing'])} of them. Studentized stationary bootstrap (ruling 1), mean block {sp.BLOCK_LENGTH} business days, "
        f"{r['draws']:,} draws, seed {r['seed']}, two-sided 90% interval (the lower end is the one-sided 95% bound). **A reading (gain, loss, "
        "undecided) is taken from the mean-d bound** (her ruling on #1009, 20 October 2026), with the skill interval beside it. **Caveat (Lens C, "
        "#958):** the lag-10 HAC standard error that studentizes the bound is understated about 2x after 2020, so an interval that excludes zero is "
        "narrower than it should be. The intervals of a month or a day-type group keep the **current method** (the group's days, scattered, "
        "resampled in date order as if consecutive), which #1221 questions and #1228 will decide; no pressure-day type is read from them. Where a cap "
        "changes only a few days of a group, some resamples have no long-run variance; they are dropped from the studentized draws and counted beside "
        "the bound (#1239). The two scores move by the same amount in every group, because a cap acts only above the line, which is above 0 bp, where "
        "the weight of the upper-tail twCRPS is 1.", ""]
    if r.get("against_1229"):
        a = r["against_1229"]
        out += ["(s3)'s pooled mean here and in #1229's record: " + "; ".join(
            f"{METRIC_TITLES[m]} {a[m]['here']:.6f} against {a[m]['in_1229']:.6f} (difference {a[m]['difference']:+.2e})" for m in METRIC_NAMES)
            + ". The walk is the same one, so they agree.", ""]
    out += ["**The line.** `repo_model.srf_line` reads the minimum bid rate less the IORB, in bp, from `metadata/policy_events.json`, as public at "
            "the decision instant (16:00 on the decision day); nothing writes +10 bp into the code. On the scored target days:", "",
            "| from | to | line (bp) | target days |", "|---|---|---|---|"]
    out += [f"| {s['from']} | {s['to']} | {s['bp']:+.1f} | {s['days']} |" for s in r["line"]]
    out += ["", "## 1. Realised: how often SOFR and its 99th percentile closed above the line", "",
            "A day is above the line when the value, read on whole basis points, is strictly above the line in force that day "
            "(docs/decisions/pressure-probability.md, #155). SOFR is the panel's SOFR - IORB. The 99th percentile is the New York Fed's SOFR 99th "
            "percentile from the tracked snapshot (the latest vintage public at the panel's build cutoff) less the panel's IORB; the published panel "
            "has no percentile column. The share carries an **exact (Clopper-Pearson) 90% binomial interval**, which is the figure to read where "
            "the days are few. The gap is the value less the line, in whole basis points.", ""]
    for series in SERIES:
        out += [f"### {SERIES_TITLES[series]}", ""] + realised_table(r, series) + [""]
    out += ["### Did full allotment change how often the line was crossed?", "",
            "Declared before any count: a change is named only if the exact 90% interval of the share above before full allotment and the one since "
            "do not overlap; otherwise the counts do not show a change.", "",
            "| series | before | since | intervals overlap | reading |", "|---|---|---|---|---|"]
    for series in SERIES:
        a, s = real[series]["a"], real[series]["since"]
        ok = intervals_overlap(a["interval"], s["interval"])
        reading = "changed" if r["rules"]["changed"][series] else "the counts do not show a change"
        out.append(f"| {SERIES_TITLES[series]} | {_share(a)} | {_share(s)} | {'yes' if ok else 'no'} | {reading} |")
    out += ["", "### The pattern a firm ceiling predicts", "",
            "Declared before any count: present in a period only if the 99th percentile has no day above the line, its maximum gap is at least -1 bp "
            "(it reaches the line), SOFR has no day above, and SOFR's maximum gap is below the 99th percentile's.", "",
            "| period | SOFR days above / max gap (bp) | 99th percentile days above / max gap (bp) | pattern |", "|---|---|---|---|"]
    for name in ("a", "b", "c", "since"):
        so, p9 = real["SOFR"][name], real["SOFR_p99"][name]
        out.append(f"| {PERIOD_TITLES[name]} | {so['above']} / {so['gap_max']:+.0f} | {p9['above']} / {p9['gap_max']:+.0f} | "
                   f"{'present' if r['rules']['ceiling_pattern'][name] else 'not shown'} |")
    out += ["", "### The largest exceedances, with their dates", ""]
    for series in SERIES:
        out += [f"**{SERIES_TITLES[series]}, since full allotment**", ""] + largest_table(r, series, "since", LARGEST)
        out += [f"**{SERIES_TITLES[series]}, before full allotment (the 5 largest)**", ""] + largest_table(r, series, "a", 5)
    if r["p99_missing_days"]:
        out += ["Days with no 99th percentile in the snapshot, dropped from that series and never filled: " + ", ".join(r["p99_missing_days"]) + ".", ""]
    out += ["## 2. Forecast: how often (s3)'s upper quantile levels sit above the line on the 2026 days", "",
            "Share of the (decision day, lead) cells in which (s3)'s quantile is strictly above the line known at the decision instant. Levels from the "
            "median; an interval (stationary bootstrap over the cells in date order, mean block 10 cells per lead and 50 over all leads) for the five "
            "key levels, the other levels are in `result.json`. The window has one regime, so the regime split is the pooled row.", ""]
    levels = [str(p) for p in KEY_LEVELS]
    out += ["**pooled**", ""] + k.forecast_table(r, "pooled", levels) + [""]
    out += ["By pressure-day type of the target day, all leads:", "", "| type | cells | " + " | ".join(f"q{x}" for x in levels) + " |",
            "|---|---|" + "---|" * len(levels)]
    for split, per_lead in r["forecast"]["splits"].items():
        if split.startswith("pressure_day_type/") and per_lead["all"]["cells"]:
            e = per_lead["all"]
            out.append(f"| {split.split('/')[1]} | {e['cells']} | " + " | ".join(k._pct_ci(e["share_above"][x], e["interval"].get(x)) for x in levels) + " |")
    out += ["", "How often each cap arm changes the forecast, as the share of the same cells in which (s3)'s level is above the ceiling (line plus margin):", "",
            "| leads | cells | " + " | ".join(f"{LABELS[a]}: q95 / q99" for a in CAPS) + " |", "|---|---|" + "---|" * len(CAPS)]
    for lead in ("all",) + tuple(str(h) for h in sp.HORIZONS):
        e = r["forecast"]["splits"]["pooled"][lead]
        out.append(f"| {'all' if lead == 'all' else 'h=' + lead} | {e['cells']} | " + " | ".join(
            f"{k._pct(e['binds'][a]['q95'])} / {k._pct(e['binds'][a]['q99'])}" for a in CAPS) + " |")
    out += ["", "## 3. Score: each cap arm against (s3), paired", "",
            "The pooled row and the pressure-day types first; every group follows. Lower mean is better; skill and mean d are positive when the cap "
            "arm is better than (s3).", ""] + summary_rows(r) + [""]
    entry = r["groups"]["pooled"]["all decision days"]
    for metric in METRIC_NAMES:
        out += [f"### All decision days: {METRIC_TITLES[metric]}, mean over leads 1 to 5 (bp) ({entry['days']} days)", ""] + k.model_table(entry[metric]) + [""]
    for split, order, title in (("pressure_day_type", sorted(r["groups"].get("pressure_day_type", {})), "pressure-day type (turn record in force; target day; current method)"),
                                ("month", sorted(r["groups"].get("month", {})), "target month (current method)"),
                                ("target_day_type", list(DAY_TYPES) + [ORDINARY, "calendar_days"], "calendar target-day type (the groups overlap; current method)"),
                                ("lead", [f"h={h}" for h in sp.HORIZONS], "lead")):
        for metric in METRIC_NAMES:
            out += [f"### {METRIC_TITLES[metric]} by {title}", ""]
            for label in order:
                e = r["groups"].get(split, {}).get(label)
                if e is not None and metric in e:
                    out += [f"**{label}** ({e['days']} days)", ""] + k.model_table(e[metric]) + [""]
    if r["skipped_groups"]:
        out += ["Groups with fewer than %d days are listed and not tested: %s." % (
            MIN_GROUP_DAYS, ", ".join(f"{x} ({v})" for x, v in sorted(r["skipped_groups"].items()))), ""]
    out += ["A group in which a cap arm's score equals (s3)'s on every day reads \"identical\" and is not tested.", "",
            "### The Politis-White block beside the block of 10", "",
            "The automatic block length of the paired loss differential `S((s3)) - S(arm)`, in days, with the pooled skill over (s3) at that block. "
            "Reported, never substituted for 10.", "", "| | grid CRPS: block | pooled skill at that block | twCRPS: block | pooled skill at that block |", "|---|---|---|---|---|"]
    for arm in CAPS:
        cells = []
        for metric in METRIC_NAMES:
            e = (r["politis_white"].get("pooled", {}).get("all decision days", {}).get(metric, {}).get(arm) or {}).get(S3)
            if not e:
                cells += ["n/a", ""]
            elif "row" in e:
                cells += [f"{e['block']:.1f}", f"block {e['at_block']}: {k._fmt(e['row'])}"]
            else:
                cells += [f"{e['block']:.1f}", f"block {e['at_block']}: undefined ({e.get('undefined', 'n/a')})"]
        out.append(f"| {LABELS[arm]} | " + " | ".join(cells) + " |")
    out += ["", "## 4. Cross-check against repo-market-spillovers (October 2026)", ""]
    ch = r["cross_check"]
    sp_ = ch["spillovers"]
    out += [f"repo-market-spillovers (its study 13 and study 02, which read this model's published panel) reports SOFR's 99th percentile minus IORB peaking "
            f"at {sp_['peak_bp']} bp on {sp_['peak_date']}, exactly the facility line, with a mean of {sp_['mean_bp']} bp in October 2026. **This panel cannot "
            f"check that.** It is built with a cutoff of 2026-09-08 and its last day is {ch['panel_last_day']}; it holds {ch['october_2026_days_in_panel']} "
            f"days of October 2026. Every day from {ch['missing_from']} on is missing, including all of October 2026, and no new data was fetched. The "
            "register's line on 2026-10-23 is "
            + ("not available" if ch["register_line_2026_10_23"] is None else f"{ch['register_line_2026_10_23']:+.0f} bp")
            + " (a fact about the line from `metadata/policy_events.json`; no outcome after 2026-09-03 is read). For context, the same statistics "
            "for the days the panel does have:", "", "| month | days | mean (bp) | max (bp) | on |", "|---|---|---|---|---|"]
    out += [f"| {m} | {e['days']} | {e['mean']:.1f} | {e['max']:+d} | {e['max_date']} |" for m, e in ch["monthly_2026"].items()]
    out += ["", "## What this is not", "",
            "A description of the 2026 development days, which three earlier looks had seen, and of the days since the facility's limit was removed; never a "
            "verdict. The exact intervals are wide where the days are few (December 2025 has few), and the counts show how often a series closed above a "
            "line, not why it did not. Whether the facility is the cause of a ceiling needs a counterfactual this study does not have. The wording of the "
            "article is hers; the first sentence above is what the counts allow.", ""]
    out += question(r)
    return "\n".join(out) + "\n"


def question(r: Mapping[str, object]) -> List[str]:
    cols = [("pooled", "all decision days", "all decision days")] + [("pressure_day_type", x, x) for x in sorted(r["groups"].get("pressure_day_type", {}))]
    out = ["## Question for Eleonora", "",
           "Your ruling of 26 October 2026 on #1252 asked for this check and left the decision to you. **Nothing is adopted here and no claim changes.** "
           "Mean score of (s3) and the three cap arms on the 2026 days (lower is better):", ""]
    for metric in METRIC_NAMES:
        out += [f"**{METRIC_TITLES[metric]}**", "", "| | " + " | ".join(col[2] for col in cols) + " |", "|---|" + "---|" * len(cols)]
        for m in ARMS:
            cells = []
            for split, label, _name in cols:
                e = r["groups"].get(split, {}).get(label)
                cells.append("n/a" if e is None or metric not in e or m not in e[metric]["means"] else f"{e[metric]['means'][m]:.3f}")
            out.append(f"| {LABELS[m]} | " + " | ".join(cells) + " |")
        out.append("")
    out += ["**Options** (numbered; the default applies if you have not answered by the next 5 pm batch):", "",
            "1. **Keep (s3) as the H5 candidate, with no cap** (default). Nothing changes; the cap arms stay development results, and the first "
            "sentence of this page is what the counts allow for the article.",
            "2. **Take a cap into the candidate (which margin: your choice)**, on the evidence above and #1241's. That is a decision for you and would be "
            "followed by a registration discussion; this page does not pre-empt it.",
            "3. **Ask for a further step**: repeat part 1 on October 2026 once a panel with a later build cutoff exists (a data decision), so that the "
            "comparison with repo-market-spillovers can be made on the same days.", ""]
    return out


def page(args) -> int:
    r = json.loads(Path(args.score).read_text(encoding="utf-8"))
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    Path(args.output).write_text(render(r), encoding="utf-8")
    return 0


@turn_days.with_legacy_flag
def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="command", required=True)
    s = sub.add_parser("score", help="walk (s3), cap it, score the arms and count the exceedances")
    s.add_argument("--panel", required=True)
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
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
