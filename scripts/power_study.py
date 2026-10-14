#!/usr/bin/env python3
"""The power study of scoring protocol v1 (#656, H5 groundwork G4): the days needed to detect the MME.

The rule it follows is `docs/research/power-study-656.md`, committed before this script ran. Development data only:
no day after 2026-09-03 (`PANEL_END`) is scored, and nothing here is a verdict.

    PYTHONPATH=src python3 scripts/power_study.py run --out docs/research/power-study-656 [--paths N] [--workers K]
    PYTHONPATH=src python3 scripts/power_study.py null --out docs/research/power-study-656 [--paths N] [--workers K]
    PYTHONPATH=src python3 scripts/power_study.py check --out docs/research/power-study-656

`run` builds the published panel from the tracked fixtures, scores B1 and B2 on every development decision day,
constructs the synthetic candidate of the rule (§3), simulates confirmation paths (§4), and writes `result.json`.
`null` is a post-hoc size check (`docs/research/power-study-656-addendum.md`), added after `run`'s figures were seen.
`check` re-reads `result.json` and refuses it if it was made from another rule text. Standard library only.
"""

from __future__ import annotations

import argparse
import contextlib
import hashlib
import io
import json
import math
import multiprocessing
import random
import sys
import tempfile
from datetime import date, time, timedelta
from pathlib import Path
from statistics import NormalDist

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))

from repo_model import onset  # noqa: E402
from repo_model import protocol_benchmarks as pb  # noqa: E402
from repo_model import scoring_protocol as sp  # noqa: E402
from repo_model.cli import main as cli_main  # noqa: E402
from repo_model.data import load_daily_panel  # noqa: E402
from repo_model.evaluation_splits import load_split_declaration  # noqa: E402
from repo_model.metrics import stationary_bootstrap_indices  # noqa: E402

RULE = REPO / "docs" / "research" / "power-study-656.md"
FIXTURES = REPO / "tests" / "fixtures" / "snapshots" / "funding_inputs"
REGISTRY = json.loads((REPO / "metadata" / "sources.json").read_text(encoding="utf-8"))
SPLITS = load_split_declaration(REPO / "metadata" / "evaluation_splits.json")
MANIFEST = REPO / "metadata" / "funding_panel_manifest.json"
#: The published panel's build (`metadata/funding_panel_manifest.json`).
CUTOFF = "2026-09-08T21:31:42+00:00"
DECISION = time(16, 0)
PANEL_END = date(2026, 9, 3)

# The rule's constants (§3 to §5).
DELTA = 0.03
NOISE = 1.0
NOISE_SENSITIVITY = (0.5, 0.25)
DELTA_GRID = (0.04, 0.05, 0.06, 0.08, 0.10)
TARGET_POWER = 0.80
REPLICATIONS = 400
PATH_DAYS = sp.CHECKPOINTS[-1]
LOOK1_DEVIATION_DRAWS = 20_000
NORMAL_APPROX_PATHS = 20_000
SEED = 656


class RuleError(ValueError):
    """The study was asked for something its rule does not say."""


# -- the development series (§2) -------------------------------------------------------------------------------------


def build_panel(directory: Path) -> Path:
    path = directory / "funding_panel.csv"
    with contextlib.redirect_stdout(io.StringIO()):
        code = cli_main(
            ["build", "--raw-root", str(FIXTURES), "--output", str(path),
             "--build-cutoff", CUTOFF, "--decision-time", "16:00:00"]
        )
        if code == 0:
            code = cli_main(["verify-panel", str(path), "--manifest", str(MANIFEST)])
    if code != 0:
        raise RuleError("the fixture panel did not build to the published digest")
    return path


def years_after(day: date, years: int) -> date:
    try:
        return day.replace(year=day.year + years)
    except ValueError:
        return day.replace(year=day.year + years, day=28)


def development_series(rows):
    """Decision days with a full two-year window and five targets on or before `PANEL_END`; and B1's and B2's scores.

    Returns `(days, s1, s2)`, the scores of the primary metric by day.
    """

    first = years_after(rows[0].date, pb.B1_YEARS)
    outcomes = {row.date: row.spread_bps for row in rows}
    calendar = [row.date for row in rows]
    b1, b2 = {}, {}
    for t, row in enumerate(rows):
        if row.date < first or t + max(sp.HORIZONS) >= len(rows):
            continue
        if rows[t + max(sp.HORIZONS)].date > PANEL_END:
            continue
        b1[row.date] = pb.b1_forecast(rows, t, registry=REGISTRY, decision_time=DECISION)
        b2[row.date] = pb.b2_forecast(rows, t, registry=REGISTRY, decision_time=DECISION, splits=SPLITS)
    s1 = sp.day_scores(b1, outcomes, calendar)
    s2 = sp.day_scores(b2, outcomes, calendar)
    days = sorted(s1)
    if days != sorted(s2):
        raise RuleError("B1 and B2 score different days")
    if days[-1] > PANEL_END:
        raise RuleError(f"the study scores {days[-1]}, after {PANEL_END}")
    return days, [s1[d] for d in days], [s2[d] for d in days]


# -- the synthetic candidate (§3) ------------------------------------------------------------------------------------


def candidate_differences(s1, s2, delta: float, noise: float):
    """`d_t = delta * S1_t + noise * (e_t - mean(e))`, `e_t = S1_t - S2_t`. Its mean skill against B1 is `delta`."""

    e = [a - b for a, b in zip(s1, s2)]
    centre = sum(e) / len(e)
    return [delta * a + noise * (x - centre) for a, x in zip(s1, e)]


def weekdays(count: int, start: date = date(2001, 1, 2)):
    out, day = [], start
    while len(out) < count:
        if day.weekday() < 5:
            out.append(day)
        day += timedelta(days=1)
    return out


# -- one simulated path (§4) -----------------------------------------------------------------------------------------

_DATA = {}


def init_worker(s1, d):
    _DATA["s1"], _DATA["d"] = s1, d
    _DATA["days"] = weekdays(PATH_DAYS)


def run_path(job):
    """One path: the first checkpoint at which the candidate is detected, or None; and the look-1 deviation."""

    seed, = job
    s1, d = _DATA["s1"], _DATA["d"]
    rng = random.Random(seed)
    index = stationary_bootstrap_indices(len(s1), sp.BLOCK_LENGTH, rng)[:PATH_DAYS]
    days = _DATA["days"]
    bench = [s1[i] for i in index]
    cand = [s1[i] - d[i] for i in index]
    levels = sp.nominal_levels()
    detected = None
    unresolved = 0
    for k, n in enumerate(sp.CHECKPOINTS):
        test = sp.paired_test(
            dict(zip(days[:n], bench[:n])), dict(zip(days[:n], cand[:n])), seed=seed, draws=sp.DRAWS
        )
        try:
            lower = test.lower_mean_difference(levels[k])
        except sp.UnresolvedLevel:
            unresolved += 1
            continue
        if lower > 0.0 and test.skill >= sp.MME:
            detected = n
            break
    # the deviation: look 1 read with more draws, labelled as such (§4)
    deviation = None
    if detected is None or detected > sp.CHECKPOINTS[0]:
        n = sp.CHECKPOINTS[0]
        test = sp.paired_test(
            dict(zip(days[:n], bench[:n])), dict(zip(days[:n], cand[:n])), seed=seed, draws=LOOK1_DEVIATION_DRAWS
        )
        deviation = bool(test.lower_mean_difference(levels[0]) > 0.0 and test.skill >= sp.MME)
    else:
        deviation = True
    return detected, unresolved, deviation


def cumulative(detections):
    total = len(detections)
    return {n: sum(1 for x in detections if x is not None and x <= n) / total for n in sp.CHECKPOINTS}


def simulate(s1, d, *, paths: int, seed: int, workers: int):
    jobs = [(seed * 100_003 + i,) for i in range(paths)]
    if workers > 1:
        with multiprocessing.Pool(workers, initializer=init_worker, initargs=(s1, d)) as pool:
            results = pool.map(run_path, jobs, chunksize=max(1, paths // (workers * 8)))
    else:
        init_worker(s1, d)
        results = [run_path(job) for job in jobs]
    detections = [r[0] for r in results]
    power = cumulative(detections)
    look1_deviation = sum(1 for r in results if r[2]) / paths
    unresolved_look1 = sum(1 for r in results if r[1] > 0) / paths
    se = {n: math.sqrt(p * (1 - p) / paths) for n, p in power.items()}
    return {
        "paths": paths,
        "power": {str(n): p for n, p in power.items()},
        "monte_carlo_se": {str(n): v for n, v in se.items()},
        "power_look1_deviation_20000_draws": look1_deviation,
        "share_of_paths_with_an_unresolvable_level": unresolved_look1,
    }


def days_needed(power):
    for n in sp.CHECKPOINTS:
        if power[str(n)] >= TARGET_POWER:
            return n
    return None


# -- the post-hoc size check (docs/research/power-study-656-addendum.md) --------------------------------------------------

ADDENDUM = REPO / "docs" / "research" / "power-study-656-addendum.md"


def run_null_path(job):
    """A path under no true difference: whether the lower bound is above zero at look 2 or 3, with and without the MME gate."""

    seed, = job
    s1, d = _DATA["s1"], _DATA["d"]
    rng = random.Random(seed)
    index = stationary_bootstrap_indices(len(s1), sp.BLOCK_LENGTH, rng)[:PATH_DAYS]
    days = _DATA["days"]
    bench = [s1[i] for i in index]
    cand = [s1[i] - d[i] for i in index]
    levels = sp.nominal_levels()
    ungated = gated = None
    for k, n in enumerate(sp.CHECKPOINTS):
        if k == 0:
            continue
        test = sp.paired_test(
            dict(zip(days[:n], bench[:n])), dict(zip(days[:n], cand[:n])), seed=seed, draws=sp.DRAWS
        )
        if test.lower_mean_difference(levels[k]) > 0.0:
            if ungated is None:
                ungated = n
            if gated is None and test.skill >= sp.MME:
                gated = n
    return ungated, gated


def null_command(args) -> int:
    out = Path(args.out)
    with tempfile.TemporaryDirectory() as tmp:
        rows = load_daily_panel(build_panel(Path(tmp)))
    days, s1, s2 = development_series(rows)
    d = candidate_differences(s1, s2, 0.0, NOISE)
    jobs = [(SEED * 100_003 + 7_000_000 + i,) for i in range(args.paths)]
    with multiprocessing.Pool(args.workers, initializer=init_worker, initargs=(s1, d)) as pool:
        results = pool.map(run_null_path, jobs, chunksize=max(1, args.paths // (args.workers * 8)))
    total = len(results)

    def share(position, upto):
        return sum(1 for r in results if r[position] is not None and r[position] <= upto) / total

    result = {
        "post_hoc": True,
        "addendum": str(ADDENDUM.relative_to(REPO)),
        "addendum_sha256": sha256(ADDENDUM),
        "paths": total,
        "nominal_overall_level": sp.ALPHA,
        "false_detection_share_without_the_mme_gate": {"125": share(0, 125), "250": share(0, 250)},
        "false_detection_share_with_the_mme_gate": {"125": share(1, 125), "250": share(1, 250)},
        "monte_carlo_se_at_250": math.sqrt(share(0, 250) * (1 - share(0, 250)) / total),
    }
    (out / "null.json").write_text(json.dumps(result, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, sort_keys=True))
    return 0


# -- the cross-check (§5) --------------------------------------------------------------------------------------------


def long_run_sd(values, lag: int = sp.HAC_LAG) -> float:
    n = len(values)
    mean = sum(values) / n
    c = [v - mean for v in values]
    variance = sum(x * x for x in c) / n
    for k in range(1, lag + 1):
        variance += 2.0 * (1.0 - k / (lag + 1.0)) * sum(c[t] * c[t - k] for t in range(k, n)) / n
    return math.sqrt(variance)


def normal_approximation(s1, d, *, paths: int, seed: int):
    """Group-sequential power under iid normal increments with the series' mean and long-run sd, the protocol's boundaries."""

    mu, sigma = sum(d) / len(d), long_run_sd(d)
    mean_s1 = sum(s1) / len(s1)
    bounds = sp.boundaries()
    rng = random.Random(seed)
    won = {n: 0 for n in sp.CHECKPOINTS}
    for _ in range(paths):
        total, n = 0.0, 0
        done = False
        for k, look in enumerate(sp.CHECKPOINTS):
            while n < look:
                total += rng.gauss(mu, sigma)
                n += 1
            z = (total / n) / (sigma / math.sqrt(n))
            if z > bounds[k] and (total / n) / mean_s1 >= sp.MME:
                won[look] += 1
                done = True
                break
        if done:
            for later in sp.CHECKPOINTS:
                if later > look:
                    won[later] += 1
    return {str(n): won[n] / paths for n in sp.CHECKPOINTS}


# -- the H7m information goalpost (§6) -------------------------------------------------------------------------------


def hanley_mcneil_se(auc: float, positives: int, negatives: int) -> float:
    q1 = auc / (2.0 - auc)
    q2 = 2.0 * auc * auc / (1.0 + auc)
    variance = (
        auc * (1.0 - auc) + (positives - 1) * (q1 - auc * auc) + (negatives - 1) * (q2 - auc * auc)
    ) / (positives * negatives)
    return math.sqrt(variance)


def stress_events(rows, days):
    """Onsets of pressure (`onset.onset_flags`) among the development decision days, and the days they imply."""

    flags = onset.onset_flags(rows)
    wanted = set(days)
    events = sum(1 for row, flag in zip(rows, flags) if flag and row.date in wanted)
    per_day = events / len(days)
    needed = math.ceil(10 / per_day) if per_day else None
    report = {"development_days": len(days), "stress_events": events, "events_per_day": per_day,
              "days_to_expect_10_events": needed}
    if needed:
        for auc in (0.55, 0.65, 0.75):
            report[f"hanley_mcneil_se_at_auc_{auc}_with_10_events"] = hanley_mcneil_se(auc, 10, max(needed - 10, 2))
    return report


# -- the command -----------------------------------------------------------------------------------------------------


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run_command(args) -> int:
    out = Path(args.out)
    with tempfile.TemporaryDirectory() as tmp:
        panel = build_panel(Path(tmp))
        panel_digest = sha256(panel)
        rows = load_daily_panel(panel)
    days, s1, s2 = development_series(rows)
    scenarios = {}
    plan = [(NOISE, DELTA)] + [(n, DELTA) for n in NOISE_SENSITIVITY] + [(NOISE, d) for d in DELTA_GRID]
    for noise, delta in plan:
        d = candidate_differences(s1, s2, delta, noise)
        key = f"noise={noise}, delta={delta}"
        skill = sum(d) / sum(s1)
        result = simulate(s1, d, paths=args.paths, seed=SEED, workers=args.workers)
        result.update({
            "noise": noise, "delta": delta, "series_skill_against_b1": skill, "series_mean_d": sum(d) / len(d),
            "days_with_negative_candidate_score": sum(1 for a, x in zip(s1, d) if a - x < 0.0),
            "days_needed": days_needed(result["power"]),
            "normal_approximation": normal_approximation(s1, d, paths=NORMAL_APPROX_PATHS, seed=SEED),
        })
        scenarios[key] = result
        print(key, json.dumps(result["power"]), "needed", result["days_needed"], flush=True)
    primary = scenarios[f"noise={NOISE}, delta={DELTA}"]
    smallest = None
    for delta in sorted((DELTA,) + DELTA_GRID):
        got = scenarios[f"noise={NOISE}, delta={delta}"]["power"][str(sp.CHECKPOINTS[-1])]
        if got >= TARGET_POWER:
            smallest = delta
            break
    result = {
        "rule": str(RULE.relative_to(REPO)),
        "rule_sha256": sha256(RULE),
        "panel_sha256": panel_digest,
        "development": {"first": days[0].isoformat(), "last": days[-1].isoformat(), "decision_days": len(days),
                        "mean_b1_score": sum(s1) / len(s1), "mean_b2_score": sum(s2) / len(s2)},
        "constants": {"delta": DELTA, "noise": NOISE, "target_power": TARGET_POWER, "paths": args.paths,
                      "draws": sp.DRAWS, "block_length": sp.BLOCK_LENGTH, "mme": sp.MME,
                      "checkpoints": list(sp.CHECKPOINTS), "seed": SEED},
        "nominal_levels": list(sp.nominal_levels()),
        "look1_resolvable_with_10000_draws": sp.nominal_levels()[0] * sp.DRAWS >= 1.0,
        "scenarios": scenarios,
        "primary": primary,
        "days_needed_for_3_percent": primary["days_needed"],
        "smallest_skill_detected_within_250_days_at_target_power": smallest,
        "h7m_information_goalpost": stress_events(rows, days),
    }
    out.mkdir(parents=True, exist_ok=True)
    (out / "result.json").write_text(json.dumps(result, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    print("wrote", out / "result.json")
    return 0


def check_command(args) -> int:
    result = json.loads((Path(args.out) / "result.json").read_text(encoding="utf-8"))
    if result["rule_sha256"] != sha256(RULE):
        raise RuleError("result.json was made under another text of the rule")
    if result["development"]["last"] > PANEL_END.isoformat():
        raise RuleError("the study scored a day after the panel's end")
    print("ok")
    return 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="command", required=True)
    run = sub.add_parser("run")
    run.add_argument("--out", required=True)
    run.add_argument("--paths", type=int, default=REPLICATIONS)
    run.add_argument("--workers", type=int, default=1)
    run.set_defaults(func=run_command)
    null = sub.add_parser("null")
    null.add_argument("--out", required=True)
    null.add_argument("--paths", type=int, default=REPLICATIONS)
    null.add_argument("--workers", type=int, default=1)
    null.set_defaults(func=null_command)
    check = sub.add_parser("check")
    check.add_argument("--out", required=True)
    check.set_defaults(func=check_command)
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
