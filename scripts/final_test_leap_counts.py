"""The final test's expected plain-leap count, from pre-2026 days and window dates only (#222).

Eleonora's amendment of 4 October 2026 (second), before any opening, and her
scope comment of the same day on #222. It reads one candidate run from
`final_test_preregistration.py candidate` (the published fold grid at h = 1,
2018-06-29 to 2025-12-31) and the published panel, and prints:

* the pre-2026 plain-leap count at #139's `J_1` and its rate;
* the near-blind window's day count, read from the panel's date column alone
  (`final_test_preregistration.window_dates`);
* the expected leap count on the window at that rate, and the Poisson chance of
  reaching the minimum event count (`onset.MINIMUM_EVENTS`);
* each pre-2026 year's January-August plain-leap count, with the expected
  window count at that year's rate.

A scratch measurement, not a record: it writes nothing. No 2026 outcome is read.
A run whose scored days reach the near-blind tier is refused before any label is
read (`final_test_preregistration._refuse_locked`).

    PYTHONPATH=src python3 -m repo_model.cli build --raw-root tests/fixtures/snapshots/funding_inputs \\
        --output PUB.csv --build-cutoff 2026-09-08T21:31:42+00:00 --decision-time 16:00:00
    OMP_NUM_THREADS=1 PYTHONPATH=src /opt/rmm-venv/bin/python scripts/final_test_preregistration.py candidate \\
        --name dynamic_logit --panel PUB.csv --output OUT/dynamic_logit.pickle
    PYTHONPATH=src python3 scripts/final_test_leap_counts.py --panel PUB.csv --run OUT/dynamic_logit.pickle
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import math
import pickle
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))

from repo_model import onset  # noqa: E402
from repo_model.data import load_daily_panel  # noqa: E402


def _preregistration():
    path = REPO / "scripts" / "final_test_preregistration.py"
    spec = importlib.util.spec_from_file_location("final_test_preregistration", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def january_to_august(scored_dates, labels) -> dict:
    """Each year's scored days and plain leaps from 1 January to 31 August."""

    if len(scored_dates) != len(labels):
        raise ValueError("one label per scored day")
    years: dict = {}
    for when, leap in zip(scored_dates, labels):
        if when.month <= 8:
            cell = years.setdefault(when.year, {"days": 0, "leaps": 0})
            cell["days"] += 1
            cell["leaps"] += leap
    return years


def poisson_at_least(k: int, rate: float) -> float:
    """P(N >= k) for N ~ Poisson(rate)."""

    return 1.0 - sum(math.exp(-rate) * rate ** n / math.factorial(n) for n in range(k))


def summary(scored_dates, labels, window_days: int) -> dict:
    minimum = onset.MINIMUM_EVENTS
    leaps = sum(labels)
    expected = window_days * leaps / len(scored_dates)
    years = {}
    for year, cell in sorted(january_to_august(scored_dates, labels).items()):
        rate = window_days * cell["leaps"] / cell["days"]
        years[str(year)] = {**cell, "expected_leaps": rate,
                            "p_at_least_minimum": poisson_at_least(minimum, rate)}
    return {
        "first": scored_dates[0].isoformat(),
        "last": scored_dates[-1].isoformat(),
        "scored_days": len(scored_dates),
        "plain_leaps": leaps,
        "rate": leaps / len(scored_dates),
        "window_days": window_days,
        "expected_leaps": expected,
        "minimum_events": minimum,
        "p_at_least_minimum": poisson_at_least(minimum, expected),
        "january_to_august": years,
    }


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--panel", type=Path, required=True)
    parser.add_argument("--run", type=Path, required=True,
                        help="a pickle written by final_test_preregistration.py candidate")
    args = parser.parse_args(argv)
    fp = _preregistration()
    run = pickle.loads(args.run.read_bytes())
    scored = run["scored_dates"]
    fp._refuse_locked(scored)
    if run["leap_threshold_bp"] != fp.leap_jump_bp():
        raise ValueError("the run's leap threshold is not J_1")
    labels = fp.leap_labels(load_daily_panel(args.panel), scored)
    document = summary(scored, labels, len(fp.window_dates(args.panel)))
    print(json.dumps(document, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
