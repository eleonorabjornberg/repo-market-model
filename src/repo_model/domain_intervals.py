"""Domain estimates for groups of days that are far apart (#1228).

The H5 pages' day-type groups (quarter-end, IORB window, month-end, ...) are sparse subsequences of the target days. Resampling the
subsequence itself with a stationary bootstrap of mean block length 10 joins days that are months apart. Here the whole aligned
series is resampled, as the pooled test does, and the statistic is the mean over the resampled days that belong to the group.

This lives beside `evaluation_splits`, not in it: that file is one of the pinned definitions of the final-test pre-registration.
Stdlib only.
"""

from __future__ import annotations

import random
from typing import Any, Dict, Mapping, Sequence, Tuple

from .metrics import MetricError, _quantile, stationary_bootstrap_indices

__all__ = ["domain_estimates", "domain_interval"]


def domain_estimates(
    cells: Mapping[Any, Tuple[Sequence[float], Sequence[int]]],
    n: int,
    *,
    block_length: float,
    seed: int,
    replications: int,
    level: float,
) -> Dict[Any, Dict[str, Any]]:
    """The domain estimate of many groups, possibly overlapping, on one stream of whole-series resamples (#1228).

    Each cell is `(values, members)`: a per-position series of length `n` and the positions of the group's days. The statistic is
    the mean of `values` over the resampled positions that belong to the group, so a block of the stationary bootstrap runs over the
    whole aligned series and never joins two days of a sparse group that are months apart. The draws are those of
    `evaluation_splits.split_summary` and of `scoring_protocol.paired_tests` at the same block length, seed and replication count
    (`random.Random(seed)` through `stationary_bootstrap_indices`), and the interval is the percentile interval at `level`, so its
    lower end is the one-sided bound at `(1 - level) / 2` from the top (0.95 at level 0.90).

    A resample that draws no day of a group has no mean. It is not dropped, which would narrow the interval; the group is recorded
    with `interval_unavailable` and the reason, and the other groups are unaffected.

    Returns:
        per cell, `{"count": k}` (no day: no mean either), or `{"count", "mean", "interval": {"lower", "upper"}}`, or the same
        with `"interval_unavailable"` in place of the interval.

    Raises:
        ValueError: if a cell's series is not of length `n` or a member is outside `range(n)`.
        MetricError: on a bad seed, replication count or level.
    """

    if isinstance(replications, bool) or not isinstance(replications, int) or replications < 2:
        raise MetricError(f"replications must be an int >= 2, got {replications!r}")
    if not 0.0 < level < 1.0:
        raise MetricError(f"level must be in (0, 1), got {level}")
    if isinstance(seed, bool) or not isinstance(seed, int):
        raise MetricError(f"seed must be an int, got {seed!r}; an unseeded interval is not reproducible")
    out: Dict[Any, Dict[str, Any]] = {}
    live: Dict[Any, Tuple[list, list, list]] = {}
    for key, (series, members) in cells.items():
        if len(series) != n:
            raise ValueError(f"cell {key!r}: {len(series)} values for a series of {n}; they are aligned by position")
        positions = sorted(set(int(i) for i in members))
        if positions and (positions[0] < 0 or positions[-1] >= n):
            raise ValueError(f"cell {key!r}: a member lies outside the series of {n} days")
        out[key] = {"count": len(positions)}
        if positions:
            values = [float(series[i]) for i in positions]
            out[key]["mean"] = sum(values) / len(values)
            live[key] = (positions, values, [])
    rng = random.Random(seed)
    for replication in range(replications):
        if not live:
            break
        drawn_count = [0] * n
        for i in stationary_bootstrap_indices(n, block_length, rng):
            drawn_count[i] += 1
        for key in list(live):
            positions, values, draws = live[key]
            drawn = sum(drawn_count[i] for i in positions)
            if drawn == 0:
                out[key]["interval_unavailable"] = (
                    f"resample {replication} drew no day of the group; the mean is undefined there, and discarding "
                    f"such resamples would narrow the interval"
                )
                del live[key]
                continue
            draws.append(sum(drawn_count[i] * v for i, v in zip(positions, values)) / drawn)
    tail = (1.0 - level) / 2.0
    for key, (_positions, _values, draws) in live.items():
        draws.sort()
        out[key]["interval"] = {"lower": _quantile(draws, tail), "upper": _quantile(draws, 1.0 - tail)}
    return out


def domain_interval(
    series: Sequence[float],
    members: Sequence[int],
    n: int,
    *,
    block_length: float,
    seed: int,
    replications: int,
    level: float,
) -> Tuple[float, float]:
    """`domain_estimates` for one group, as `stationary_bootstrap_interval` returns it: `(lower, upper)`.

    Raises:
        MetricError: if the group has no day, or a resample draws none of its days.
    """

    entry = domain_estimates(
        {"group": (series, members)}, n, block_length=block_length, seed=seed, replications=replications, level=level
    )["group"]
    if "interval" not in entry:
        raise MetricError(entry.get("interval_unavailable", "the group has no day"))
    return entry["interval"]["lower"], entry["interval"]["upper"]
