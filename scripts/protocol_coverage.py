"""H1 check 2: coverage of the protocol's one-sided bound on resampled real series (#655).

Reproduces the coverage figures the pull requests for #655 report (PR #660, PR #695). The real
series is `d_t = S(B2) - S(B1)`, the daily grid-CRPS difference of the protocol's two primary
benchmarks on every development decision day whose five targets fall on or before 2026-09-03,
on the published panel built from the tracked fixtures. Each replication draws `--days` days
from a series by circular blocks of 10 at uniform random starts, runs the scorer's paired test
on it, and records whether the one-sided bound at `--level` is at or below the series' full
mean. It reports the share for the calibrated bound (the double bootstrap, `--inner` > 0) and
for the plain studentized bound read off the same outer draws.

    python3 scripts/protocol_coverage.py coverage --series real --replications 300 --draws 500 --inner 100
    python3 scripts/protocol_coverage.py stability --draws 1000 2000 --inner 100 200
    python3 scripts/protocol_coverage.py calibrate [--seed 1] [--write]
    python3 scripts/protocol_coverage.py check-coverage [--windows 20000] [--seed 2]
    python3 scripts/protocol_coverage.py null [--paths 400] [--history post-2020-04|full]
    python3 scripts/protocol_coverage.py power [--paths 400] [--delta 0.03 0.10] [--noise 1]

`calibrate` computes the critical value at each checkpoint on each benchmark pair (B2 - B1 on the
grid, B3 - B1 on B3's five levels, and each reversed) on the development history, as Eleonora ruled
on 13 October 2026 (PR #695, comment 6149326627), and with `--write` records it in
`docs/research/protocol-calibration/result.json`, which `scoring_protocol.CRITICAL_VALUES` must
equal. `check-coverage` measures each value's coverage on fresh windows. `null` re-runs #699's
post-hoc size check with the calibrated values.

`--series` is `real`, `real-without-2019-09` (the real series less its one most negative day,
a diagnostic only: the protocol never trims) or `control` (iid standard normal, as long as the
real series). `stability` computes the calibrated critical value on one fixed draw from the real
series at each (draws, inner) pair. Writes nothing; prints one JSON object per result.
Standard library only.
"""

from __future__ import annotations

import argparse
import contextlib
import io
import json
import math
import random
import sys
import tempfile
import time
from datetime import date, time as clock, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from repo_model import protocol_benchmarks as pb  # noqa: E402
from repo_model import scoring_protocol as sp  # noqa: E402
from repo_model.cli import main as cli_main  # noqa: E402
from repo_model.data import load_daily_panel  # noqa: E402
from repo_model.evaluation_splits import load_split_declaration  # noqa: E402

FIXTURES = ROOT / "tests" / "fixtures" / "snapshots" / "funding_inputs"
CUTOFF = "2026-09-08T21:31:42+00:00"
DEVELOPMENT_FIRST = date(2018, 6, 29)
DEVELOPMENT_LAST = date(2026, 9, 3)
GENERATOR_BLOCK = 10


_ROWS = []


def published_rows():
    """The published panel, built once from the tracked fixtures."""

    if not _ROWS:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "funding_panel.csv"
            with contextlib.redirect_stdout(io.StringIO()):
                code = cli_main(
                    ["build", "--raw-root", str(FIXTURES), "--output", str(path),
                     "--build-cutoff", CUTOFF, "--decision-time", "16:00:00"]
                )
            if code != 0:
                raise RuntimeError("the fixture panel did not build")
            _ROWS.extend(load_daily_panel(path))
    return _ROWS


REGISTRY = json.loads((ROOT / "metadata" / "sources.json").read_text(encoding="utf-8"))
DECISION = clock(16, 0)


def real_differences():
    """The real B2 - B1 daily differences (d = S(B2) - S(B1), grid CRPS), in decision-day order."""

    rows = published_rows()
    splits = load_split_declaration(ROOT / "metadata" / "evaluation_splits.json")
    days = [row.date for row in rows]
    decisions = [
        day for i, day in enumerate(days)
        if DEVELOPMENT_FIRST <= day and i + 5 < len(days) and days[i + 5] <= DEVELOPMENT_LAST
    ]
    settings = {"registry": REGISTRY, "decision_time": DECISION}
    b1 = pb.forecasts(pb.b1_forecast, rows, decisions, **settings)
    b2 = pb.forecasts(pb.b2_forecast, rows, decisions, splits=splits, **settings)
    outcomes = {row.date: row.spread_bps for row in rows}
    s1 = sp.day_scores(b1, outcomes, days)
    s2 = sp.day_scores(b2, outcomes, days)
    return [s2[day] - s1[day] for day in sorted(s1)]


def b3_differences():
    """The real B3 - B1 daily differences on B3's five levels (d = S(B3) - S(B1)), in decision-day order.

    B3 is the published declaration's daily forecasts (`docs/runs/published_distribution_daily_h*.json`,
    dated by target day); a decision day enters when all five leads are there. B1 is read at the
    same five levels (`scoring_protocol.on_levels`), and both are scored by `level_crps`.
    """

    rows = published_rows()
    days = [row.date for row in rows]
    position = {day: i for i, day in enumerate(days)}
    b3 = {}
    for h in sp.HORIZONS:
        record = json.loads((ROOT / "docs" / "runs" / f"published_distribution_daily_h{h}.json").read_text())
        for entry in record["days"]:
            decision = days[position[date.fromisoformat(entry["date"])] - h]
            b3.setdefault(decision, {})[h] = entry["quantiles_bps"]
    levels = pb.incumbent()["levels"]
    b3 = {day: pb.b3_forecast(levels, leads) for day, leads in b3.items() if len(leads) == len(sp.HORIZONS)}
    b1 = pb.forecasts(pb.b1_forecast, rows, sorted(b3), registry=REGISTRY, decision_time=DECISION)
    five = sp.level_crps(levels)
    outcomes = {row.date: row.spread_bps for row in rows}
    s1 = sp.day_scores(
        {day: {h: sp.on_levels(q, levels) for h, q in leads.items()} for day, leads in b1.items()},
        outcomes, days, score=five,
    )
    s3 = sp.day_scores(b3, outcomes, days, score=five)
    return [s3[day] - s1[day] for day in sorted(set(s1) & set(s3))]


def series(kind):
    real = real_differences()
    if kind == "real":
        return real
    if kind == "real-without-2019-09":
        worst = min(range(len(real)), key=real.__getitem__)
        return real[:worst] + real[worst + 1:]
    if kind == "control":
        noise = random.Random(5)
        return [noise.gauss(0.0, 1.0) for _ in real]
    raise ValueError(f"unknown series {kind!r}")


def draw(values, length, rng):
    out = []
    while len(out) < length:
        start = rng.randrange(len(values))
        out.extend(values[(start + k) % len(values)] for k in range(GENERATOR_BLOCK))
    return out[:length]


def paired(values, *, seed, draws, inner):
    days = [date(2001, 1, 1) + timedelta(days=k) for k in range(len(values))]
    return sp.paired_test(
        {day: 10.0 for day in days},
        {day: 10.0 - value for day, value in zip(days, values)},
        seed=seed, draws=draws, inner_draws=inner, with_skill=False,
    )


def coverage(args):
    values = series(args.series)
    truth = sum(values) / len(values)
    rng = random.Random(args.seed)
    calibrated = plain = 0
    started = time.time()
    for replication in range(args.replications):
        test = paired(draw(values, args.days, rng), seed=replication, draws=args.draws, inner=args.inner)
        plain += test.mean_difference - sp._bound(test.t_draws, 1.0 - args.level, args.draws) * test.standard_error <= truth
        if args.inner:
            calibrated += test.lower_mean_difference(args.level) <= truth
    m = args.replications
    print(json.dumps({
        "series": args.series, "days": args.days, "level": args.level, "replications": m,
        "draws": args.draws, "inner": args.inner, "seed": args.seed,
        "calibrated_coverage": calibrated / m if args.inner else None,
        "studentized_coverage": plain / m,
        "binomial_se_at_nominal": ((1 - args.level) * args.level / m) ** 0.5,
        "seconds": round(time.time() - started),
    }))


def stability(args):
    values = draw(series("real"), args.days, random.Random(args.seed))
    for outer in args.draws:
        for inner in args.inner:
            test = paired(values, seed=args.seed, draws=outer, inner=inner)
            level = test.calibrated_level(args.level)
            print(json.dumps({
                "draws": outer, "inner": inner, "level": args.level,
                "calibrated_level": level,
                "calibrated_critical_value": sp._bound(test.t_draws, 1.0 - level, outer),
                "studentized_critical_value": sp._bound(test.t_draws, 1.0 - args.level, outer),
                "lower_bound": test.lower_mean_difference(args.level),
            }), flush=True)


CALIBRATION = ROOT / "docs" / "research" / "protocol-calibration" / "result.json"
#: Windows per (pair, checkpoint); look 1's diagnostic needs many more to reach its level.
CALIBRATION_WINDOWS = {60: 200_000, 125: 20_000, 250: 20_000}
CALIBRATION_SEED = 1


def calibration(seed=CALIBRATION_SEED, windows=None):
    windows = dict(CALIBRATION_WINDOWS if windows is None else windows)
    d21 = real_differences()
    d31 = b3_differences()
    pairs = {
        "B2-B1": d21, "B3-B1 (five levels)": d31,
        "B1-B2 (reversed, diagnostic)": [-v for v in d21],
        "B1-B3 (reversed, diagnostic)": [-v for v in d31],
    }
    levels = dict(zip(sp.CHECKPOINTS, sp.nominal_levels()))
    values = {}
    for name, series_ in pairs.items():
        values[name] = {
            str(n): sp.calibrate_critical_value(series_, days=n, level=levels[n], windows=windows[n], seed=seed)
            for n in sp.CHECKPOINTS
        }
    protocol = {}
    for n in sp.CHECKPOINTS:
        protocol[str(n)] = None if n == sp.CHECKPOINTS[0] else max(values[name][str(n)] for name in pairs)
    return {
        "ruling": "https://github.com/eleonorabjornberg/repo-market-model/pull/695#issuecomment-6149326627",
        "series_days": {name: len(series_) for name, series_ in pairs.items()},
        "nominal_levels": {str(n): levels[n] for n in sp.CHECKPOINTS},
        "studentized_normal_values": {str(n): sp._NORMAL.inv_cdf(1 - levels[n]) for n in sp.CHECKPOINTS},
        "windows": {str(n): windows[n] for n in sp.CHECKPOINTS},
        "window_block": sp.WINDOW_BLOCK,
        "seed": seed,
        "critical_values": values,
        "protocol_critical_values": protocol,
        "note": "protocol value: the largest across all four orientations; look 1 is left uncalibrated (Q-B)",
    }


def calibrate(args):
    result = calibration(seed=args.seed)
    if args.write:
        CALIBRATION.parent.mkdir(parents=True, exist_ok=True)
        CALIBRATION.write_text(json.dumps(result, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, sort_keys=True))


def check_coverage(args):
    """Out-of-sample coverage of each calibrated value, on fresh windows (another seed)."""

    record = json.loads(CALIBRATION.read_text(encoding="utf-8"))
    d21 = real_differences()
    named = {
        "B2-B1": d21,
        "B2-B1 without its one most negative day (diagnostic)": series("real-without-2019-09"),
        "B3-B1 (five levels)": b3_differences(),
        "control": series("control"),
    }
    levels = dict(zip(sp.CHECKPOINTS, sp.nominal_levels()))
    for name, values in named.items():
        for n in (sp.CHECKPOINTS[-1],) + ((args.level_days,) if args.level_days else ()):
            t = sp.window_t_statistics(values, days=n, windows=args.windows, seed=args.seed)
            protocol = record["protocol_critical_values"][str(n)]
            own = sp.calibrate_critical_value(values, days=n, level=args.level, windows=args.windows, seed=CALIBRATION_SEED)
            print(json.dumps({
                "series": name, "days": n, "level": args.level, "windows": args.windows, "seed": args.seed,
                "own_calibrated_value": own,
                "coverage_at_own_value": sum(1 for v in t if v <= own) / len(t),
                "protocol_value": protocol,
                "coverage_at_protocol_value": sum(1 for v in t if v <= protocol) / len(t),
                "normal_value": sp._NORMAL.inv_cdf(1 - args.level),
                "coverage_at_normal_value": sum(1 for v in t if v <= sp._NORMAL.inv_cdf(1 - args.level)) / len(t),
            }), flush=True)


def development_scores(history):
    """B1's and B2's day scores in decision-day order: `post-2020-04` is #699's series (decision days
    from two years after the panel's first row), `full` the calibration's (from 2018-06-29)."""

    rows = published_rows()
    splits = load_split_declaration(ROOT / "metadata" / "evaluation_splits.json")
    first = pb.years_before(rows[0].date, -pb.B1_YEARS) if history == "post-2020-04" else DEVELOPMENT_FIRST
    days = [row.date for row in rows]
    decisions = [
        row.date for t, row in enumerate(rows)
        if row.date >= first and t + max(sp.HORIZONS) < len(rows) and rows[t + max(sp.HORIZONS)].date <= DEVELOPMENT_LAST
    ]
    settings = {"registry": REGISTRY, "decision_time": DECISION}
    outcomes = {row.date: row.spread_bps for row in rows}
    s1 = sp.day_scores(pb.forecasts(pb.b1_forecast, rows, decisions, **settings), outcomes, days)
    s2 = sp.day_scores(pb.forecasts(pb.b2_forecast, rows, decisions, splits=splits, **settings), outcomes, days)
    ordered = sorted(s1)
    return [s1[d] for d in ordered], [s2[d] for d in ordered]


def readings():
    record = json.loads(CALIBRATION.read_text(encoding="utf-8"))
    return {
        "protocol values": {n: record["protocol_critical_values"][str(n)] for n in sp.CHECKPOINTS},
        "B2-B1 values alone (diagnostic)": {n: record["critical_values"]["B2-B1"][str(n)] for n in sp.CHECKPOINTS},
        "normal values (uncalibrated, diagnostic)": {
            n: sp._NORMAL.inv_cdf(1 - level) for n, level in zip(sp.CHECKPOINTS, sp.nominal_levels())
        },
    }


def detections(s1, s2, *, delta, noise, critical, paths):
    """#699's paths (docs/research/power-study-656.md §3-§4 on that branch), read at calibrated values.

    The candidate's daily difference against B1 is `delta * S1 + noise * (e - mean(e))`, `e = S1 - S2`,
    so its true skill against B1 is `delta`. Each path is the first 250 days of a stationary-bootstrap
    resample (mean block 10) of the series, seeded as #699 seeds them. A path is detected at the
    first of looks 2 and 3 at which `mean - c * se > 0`, with and without the MME gate (point skill
    at least the MME). Look 1 has no calibrated value and is not read.
    """

    from repo_model.metrics import stationary_bootstrap_indices

    e = [a - b for a, b in zip(s1, s2)]
    centre = sum(e) / len(e)
    diff = [delta * a + noise * (x - centre) for a, x in zip(s1, e)]
    seed_base = 656 * 100_003 + (7_000_000 if delta == 0.0 else 0)
    ungated = {n: 0 for n in sp.CHECKPOINTS[1:]}
    gated = {n: 0 for n in sp.CHECKPOINTS[1:]}
    for i in range(paths):
        index = stationary_bootstrap_indices(len(s1), sp.BLOCK_LENGTH, random.Random(seed_base + i))[:sp.CHECKPOINTS[-1]]
        bench = [s1[j] for j in index]
        d = [diff[j] for j in index]
        first_ungated = first_gated = None
        for n in sp.CHECKPOINTS[1:]:
            window = d[:n]
            mean = sum(window) / n
            se = math.sqrt(sp._long_run_variance(window, sp.HAC_LAG) / n)
            if mean - critical[n] * se > 0.0:
                first_ungated = first_ungated or n
                if mean / (sum(bench[:n]) / n) >= sp.MME:
                    first_gated = first_gated or n
        for n in ungated:
            ungated[n] += first_ungated is not None and first_ungated <= n
            gated[n] += first_gated is not None and first_gated <= n
    return {
        "ungated": {str(n): v / paths for n, v in ungated.items()},
        "with_the_mme_gate": {str(n): v / paths for n, v in gated.items()},
    }


def null(args):
    """#699's post-hoc size check re-run at the calibrated values (no true difference)."""

    s1, s2 = development_scores(args.history)
    out = {name: detections(s1, s2, delta=0.0, noise=1.0, critical=critical, paths=args.paths)
           for name, critical in readings().items()}
    print(json.dumps({"history": args.history, "series_days": len(s1), "paths": args.paths, "delta": 0.0,
                      "nominal_overall_level": sp.ALPHA, "false_detection_share": out}, sort_keys=True))


def power(args):
    """#699's power study (true skill `--delta` against B1, noise `--noise`) at the calibrated values."""

    s1, s2 = development_scores(args.history)
    for delta in args.delta:
        out = {name: detections(s1, s2, delta=delta, noise=args.noise, critical=critical, paths=args.paths)
               for name, critical in readings().items()}
        print(json.dumps({"history": args.history, "series_days": len(s1), "paths": args.paths, "delta": delta,
                          "noise": args.noise, "power": out}, sort_keys=True), flush=True)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    commands = parser.add_subparsers(dest="command", required=True)
    one = commands.add_parser("coverage")
    one.add_argument("--series", choices=("real", "real-without-2019-09", "control"), required=True)
    one.add_argument("--replications", type=int, required=True)
    one.add_argument("--draws", type=int, required=True)
    one.add_argument("--inner", type=int, required=True)
    one.add_argument("--days", type=int, default=250)
    one.add_argument("--level", type=float, default=0.05)
    one.add_argument("--seed", type=int, default=42)
    two = commands.add_parser("stability")
    two.add_argument("--draws", type=int, nargs="+", required=True)
    two.add_argument("--inner", type=int, nargs="+", required=True)
    two.add_argument("--days", type=int, default=250)
    two.add_argument("--level", type=float, default=0.05)
    two.add_argument("--seed", type=int, default=42)
    three = commands.add_parser("calibrate")
    three.add_argument("--seed", type=int, default=CALIBRATION_SEED)
    three.add_argument("--write", action="store_true")
    four = commands.add_parser("check-coverage")
    four.add_argument("--windows", type=int, default=20_000)
    four.add_argument("--seed", type=int, default=2)
    four.add_argument("--level", type=float, default=0.05)
    four.add_argument("--level-days", type=int, default=0)
    five = commands.add_parser("null")
    five.add_argument("--paths", type=int, default=400)
    five.add_argument("--history", choices=("post-2020-04", "full"), default="post-2020-04")
    six = commands.add_parser("power")
    six.add_argument("--paths", type=int, default=400)
    six.add_argument("--delta", type=float, nargs="+", default=[0.03, 0.10])
    six.add_argument("--noise", type=float, default=1.0)
    six.add_argument("--history", choices=("post-2020-04", "full"), default="post-2020-04")
    args = parser.parse_args(argv)
    {"coverage": coverage, "stability": stability, "calibrate": calibrate,
     "check-coverage": check_coverage, "null": null, "power": power}[args.command](args)
    return 0


if __name__ == "__main__":
    sys.exit(main())
