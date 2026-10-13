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


def real_differences():
    """The real B2 - B1 daily differences, in decision-day order."""

    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "funding_panel.csv"
        with contextlib.redirect_stdout(io.StringIO()):
            code = cli_main(
                ["build", "--raw-root", str(FIXTURES), "--output", str(path),
                 "--build-cutoff", CUTOFF, "--decision-time", "16:00:00"]
            )
        if code != 0:
            raise RuntimeError("the fixture panel did not build")
        rows = load_daily_panel(path)
    registry = json.loads((ROOT / "metadata" / "sources.json").read_text(encoding="utf-8"))
    splits = load_split_declaration(ROOT / "metadata" / "evaluation_splits.json")
    days = [row.date for row in rows]
    decisions = [
        day for i, day in enumerate(days)
        if DEVELOPMENT_FIRST <= day and i + 5 < len(days) and days[i + 5] <= DEVELOPMENT_LAST
    ]
    settings = {"registry": registry, "decision_time": clock(16, 0)}
    b1 = pb.forecasts(pb.b1_forecast, rows, decisions, **settings)
    b2 = pb.forecasts(pb.b2_forecast, rows, decisions, splits=splits, **settings)
    outcomes = {row.date: row.spread_bps for row in rows}
    s1 = sp.day_scores(b1, outcomes, days)
    s2 = sp.day_scores(b2, outcomes, days)
    return [s2[day] - s1[day] for day in sorted(s1)]


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
    args = parser.parse_args(argv)
    (coverage if args.command == "coverage" else stability)(args)
    return 0


if __name__ == "__main__":
    sys.exit(main())
