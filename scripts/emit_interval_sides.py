#!/usr/bin/env python3
"""Per-side interval misses for the four calibrations, with bootstrap intervals.

**Why this is a script and not a paragraph.** The question it answers -- does the
asymmetric conformal variant correct the side imbalance it was built to correct --
is answered by four numbers per calibration, and four numbers typed into Markdown
are stale the next time anything is scored. `tests/test_docs_freshness.py` exists
because this repository has published decayed figures before. So the reading is
emitted from the records and `docs/decisions/interval-side-balance.md` cites this
command rather than transcribing its output.

**What it measures.** Every backtest record carries, under
`metrics.interval_calibration`, a per-origin `side` of `inside`, `below` or
`above`. A declared 0.05-0.95 band puts 5% of origins on each side when it is
calibrated. Two-sided coverage cannot distinguish a band that misses 5% a side
from one that misses 9% below and 1% above, and those are different defects: the
second is the one an asymmetric calibration exists to fix.

So for each calibration this prints the realized coverage, each side's miss rate
with a stationary-block-bootstrap interval, and **below minus above from the same
resample** -- the same resample, because the two rates are computed on one set of
origins and resampling them independently would destroy the pairing the
difference is taken across.

**What makes the comparison fair.** `conformal` is scored against
`conformal_asymmetric` at the same calibration share, and `cross_conformal`
against `cross_conformal_asymmetric` at the same fold count. The share moves
coverage by several points on its own, so pairing across shares would attribute
that to the asymmetry. The script asserts that every record's origin sequence is
identical and refuses to print if it is not: an unpaired difference is not a
difference.

Standard library plus the package's own interval, like `emit_results.py`.
"""

from __future__ import annotations

import argparse
import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "src"))

from repo_model.metrics import stationary_bootstrap_interval  # noqa: E402

BLOCK_LENGTH = 5.0
SEED = 20260915
REPLICATIONS = 2000
LEVEL = 0.90
TARGET = 0.05

CELLS = (
    ("conformal", "share .35", "docs/runs/backtest_gbm_conformal_share035_mh61.json"),
    ("conformal_asymmetric", "share .35", "docs/runs/backtest_gbm_conformal_asymmetric_share035_mh61.json"),
    ("cross_conformal", "5 folds", "docs/runs/backtest_gbm_cross_conformal_mh61.json"),
    ("cross_conformal_asymmetric", "5 folds", "docs/runs/backtest_gbm_cross_conformal_asymmetric_mh61.json"),
)


class SidesError(RuntimeError):
    """The records cannot answer the question as asked."""


def _load(root: pathlib.Path, relative: str) -> dict:
    path = root / relative
    if not path.exists():
        raise SidesError(f"{relative} is not in this tree")
    with path.open() as handle:
        return json.load(handle)


def _sides(record: dict, relative: str) -> tuple:
    calibration = record["metrics"].get("interval_calibration")
    if not calibration:
        raise SidesError(f"{relative} carries no interval_calibration block")
    origins = calibration.get("origins")
    if not origins:
        raise SidesError(
            f"{relative} carries no per-origin sides; it predates the per-origin block "
            "and cannot be read per side"
        )
    dates = tuple(origin["scored_date"] for origin in origins)
    below = [1.0 if origin["side"] == "below" else 0.0 for origin in origins]
    above = [1.0 if origin["side"] == "above" else 0.0 for origin in origins]
    return calibration, dates, below, above


def _interval(series):
    rate = sum(series) / len(series)
    low, high = stationary_bootstrap_interval(
        lambda index: sum(series[i] for i in index) / len(index),
        len(series),
        block_length=BLOCK_LENGTH,
        seed=SEED,
        replications=REPLICATIONS,
        level=LEVEL,
    )
    return rate, low, high


def emit(root: pathlib.Path, stream=sys.stdout) -> None:
    rows = []
    reference = None
    for name, arm, relative in CELLS:
        record = _load(root, relative)
        calibration, dates, below, above = _sides(record, relative)
        if reference is None:
            reference = dates
        elif dates != reference:
            raise SidesError(
                f"{relative} does not share its origins with {CELLS[0][2]}; "
                "the cells are not paired and a difference between them is not a difference"
            )
        rows.append((name, arm, calibration, below, above))

    percent = int(LEVEL * 100)
    print(
        f"{len(reference)} origins on every cell, identical by scored date. "
        f"The declared band puts {TARGET * 100:.0f}% on each side.",
        file=stream,
    )
    print(
        f"Intervals: stationary block bootstrap, mean block {BLOCK_LENGTH:g}, "
        f"{REPLICATIONS} replications, seed {SEED}, level {LEVEL:g}.",
        file=stream,
    )
    print(file=stream)
    header = f"{'calibration':30s} {'arm':10s} {'cover':>7s} {'below (CI)':>24s} {'above (CI)':>24s}"
    print(header, file=stream)
    for name, arm, calibration, below, above in rows:
        b, b_low, b_high = _interval(below)
        a, a_low, a_high = _interval(above)
        mark = lambda low, high: "*" if not (low <= TARGET <= high) else " "  # noqa: E731
        print(
            f"{name:30s} {arm:10s} {calibration['realized_coverage'] * 100:6.2f}% "
            f"{b * 100:6.2f}% [{b_low * 100:5.2f}, {b_high * 100:5.2f}]{mark(b_low, b_high)} "
            f"{a * 100:6.2f}% [{a_low * 100:5.2f}, {a_high * 100:5.2f}]{mark(a_low, a_high)}",
            file=stream,
        )
    print(
        f"\n* the {percent}% interval excludes the {TARGET * 100:.0f}% target, "
        "so that side's miss rate is off target.",
        file=stream,
    )

    print("\nimbalance, below minus above, on the same resample:", file=stream)
    for name, arm, _calibration, below, above in rows:
        difference = [x - y for x, y in zip(below, above)]
        point = sum(difference) / len(difference)
        low, high = stationary_bootstrap_interval(
            lambda index: sum(difference[i] for i in index) / len(index),
            len(difference),
            block_length=BLOCK_LENGTH,
            seed=SEED,
            replications=REPLICATIONS,
            level=LEVEL,
        )
        note = "" if low <= 0 <= high else "   <- excludes zero"
        print(
            f"  {name:30s} {arm:10s} {point * 100:+6.2f} pp "
            f"[{low * 100:+6.2f}, {high * 100:+6.2f}]{note}",
            file=stream,
        )


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--root",
        type=pathlib.Path,
        default=pathlib.Path(__file__).resolve().parents[1],
        help="repository root the record paths are relative to",
    )
    arguments = parser.parse_args(argv)
    try:
        emit(arguments.root)
    except SidesError as error:
        print(f"error: {error}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
