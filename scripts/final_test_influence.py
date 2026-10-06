"""How much of the final test's pass a few days carry (#260, review finding 7).

Read off `docs/runs/final_test_near_blind.json` alone: its per-day paired differences
(`primary.window_per_origin`, persistence minus the published distribution, by CRPS) and
its own bootstrap settings. Nothing is scored again, and nothing here decides: the page
blocks that print these figures label them "post hoc; decides nothing". Both page
generators (`emit_results.py`, `emit_visual.py`) load this module, so the two pages print
the same numbers.

Standard library plus `repo_model.metrics`, like the generators.
"""

from __future__ import annotations

import math
import statistics
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from repo_model.metrics import stationary_bootstrap_interval  # noqa: E402

#: How many top days the table names, and where it drops them.
TOP = 10
DROPS = (1, 5, 10)


def _normal_two_sided(t):
    return 2.0 * (1.0 - 0.5 * (1.0 + math.erf(abs(t) / math.sqrt(2.0))))


def diebold_mariano(diffs, lag):
    """Mean over its Bartlett-weighted long-run standard error, and the two-sided normal p.

    `lag` 0 is the plain statistic; the HAC lag follows Newey-West's `floor(4 (n/100)^(2/9))`.
    """
    n = len(diffs)
    mean = sum(diffs) / n
    centred = [d - mean for d in diffs]

    def autocov(k):
        return sum(centred[i] * centred[i - k] for i in range(k, n)) / n

    variance = autocov(0) + 2.0 * sum((1.0 - k / (lag + 1.0)) * autocov(k) for k in range(1, lag + 1))
    if variance <= 0:
        raise ValueError("the long-run variance of the paired differences is not positive")
    stat = mean / math.sqrt(variance / n)
    return stat, _normal_two_sided(stat)


def influence(record):
    """The influence table's figures, from the record's per-day paired differences.

    Raises ValueError when the window does not average to the cell's own mean, or holds
    too few days to drop the largest ten and still test what is left.
    """
    primary = record["primary"]
    cell, window = primary["cell"], primary["window_per_origin"]
    diffs = [row["difference_bps"] for row in window]
    n = len(diffs)
    if n <= 2 * TOP:
        raise ValueError(f"window_per_origin holds {n} days, too few to drop the top {TOP}")
    mean = sum(diffs) / n
    if abs(mean - cell["mean_difference_bps"]) > 1e-9:
        raise ValueError("window_per_origin does not average to the cell's mean_difference_bps")
    ordered = sorted(range(n), key=lambda i: -diffs[i])
    top = [(window[i]["scored_date"], diffs[i]) for i in ordered[:TOP]]
    drop = {}
    for k in DROPS:
        gone = set(ordered[:k])
        rest = [v for i, v in enumerate(diffs) if i not in gone]
        drop[k] = sum(rest) / len(rest)
    interval = cell["interval"]
    rest2 = [v for i, v in enumerate(diffs) if i not in set(ordered[:2])]
    lower, upper = stationary_bootstrap_interval(
        lambda ix: sum(rest2[i] for i in ix) / len(ix), len(rest2), block_length=interval["block_length"],
        seed=interval["seed"], replications=interval["replications"], level=interval["level"])
    lag = int(math.floor(4.0 * (n / 100.0) ** (2.0 / 9.0)))
    stat, p = diebold_mariano(diffs, lag)
    plain_stat, plain_p = diebold_mariano(diffs, 0)
    return {"n": n, "mean": mean, "median": statistics.median(diffs), "wins": sum(v > 0 for v in diffs),
            "top": top, "drop": drop, "share_top": {k: sum(diffs[i] for i in ordered[:k]) / sum(diffs) for k in (1, 2, 5)},
            "leave_two_out": {"mean": sum(rest2) / len(rest2), "lower": lower, "upper": upper,
                              "block_length": interval["block_length"], "seed": interval["seed"],
                              "replications": interval["replications"], "level": interval["level"]},
            "dm": {"lag": lag, "stat": stat, "p": p, "plain_stat": plain_stat, "plain_p": plain_p},
            "persistence_loss": [(window[i]["scored_date"], window[i]["loss_a_bps"]) for i in ordered[:2]],
            "median_persistence_loss": statistics.median(row["loss_a_bps"] for row in window)}


def leap_against_climatology(record):
    """The plain-leap cell's paired Brier difference against calendar climatology, h = 1.

    The record's reported cell, or None when the record does not carry it (the caller then says
    so rather than computing it).
    """
    for document in record.get("events_reported_only", []):
        if document.get("horizon") != 1:
            continue
        paired = document.get("targets", {}).get("leap", {}).get("all_days", {}).get("paired", {})
        entry = paired.get("leap_calendar_climatology")
        if entry is None or "interval" not in entry:
            return None
        return {"mean": entry["mean"], "lower": entry["interval"]["lower"], "upper": entry["interval"]["upper"],
                "level": entry["interval"]["level"], "label": entry["label"]}
    return None
