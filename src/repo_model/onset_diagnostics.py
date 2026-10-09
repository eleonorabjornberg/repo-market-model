"""Two reported-only diagnostics on the onset bar (#429, a track of #374).

Neither changes the bar, the judge's declaration or any published figure; the settings are in
`metadata/onset_diagnostics.json`, committed before anything was computed.

**Where the false alarms fall.** A false alarm is a flag on a day that is not a pressure day, as tier 1 counts
it (`pressure_judge._onset_tier`). `false_alarm_records` lists them with the flagged day's realised spread
(whole basis points), its distance in panel days to the nearest pressure day, its day type and its regime;
`tabulate` counts them by a label list, so the splits sum to the total. `nearest_pressure_distance` reads the
days to the declared last scored day only and raises `LookAheadError` for a day or a pressure day after it
(`docs/decisions/lockbox.md`).

**What a small number of onsets can prove.** `recall_power` asks how often a model whose true onset recall is
`r` would meet tier 1's recall conditions as the judge applies them: the point recall is at least the declared
share and the lower end of the stationary-bootstrap interval on recall is above the climatology recall. The
onsets are the real ones' positions (or evenly spaced, for a window not yet read), each flagged independently
with probability `r`. The resample is the judge's stationary bootstrap (`metrics.stationary_bootstrap_indices`)
drawn as blocks with geometric lengths, which has the same distribution and is counted at the onsets
alone; a resample with no onset leaves the recall undefined, so the interval is unavailable and the condition
is not met, as the judge never drops a replicate.

Standard library only, like the rest of `src/` outside `ml.py`.
"""

from __future__ import annotations

import bisect
import hashlib
import math
import random
from typing import Any, Dict, Iterator, List, Mapping, Optional, Sequence, Tuple

from .splits import LookAheadError

__all__ = [
    "binomial_at_least",
    "block_totals",
    "evenly_spaced",
    "false_alarm_records",
    "in_bucket",
    "nearest_pressure_distance",
    "quantile",
    "recall_interval",
    "recall_power",
    "spread_bucket",
    "stationary_blocks",
    "tabulate",
]


def in_bucket(value: float, bucket: Mapping[str, Any]) -> bool:
    """Whether `value` lies in the declared bucket (`min` and `max` inclusive; null is open)."""

    low, high = bucket.get("min"), bucket.get("max")
    return (low is None or value >= low) and (high is None or value <= high)


def _label(value: float, buckets: Sequence[Mapping[str, Any]], what: str) -> str:
    for bucket in buckets:
        if in_bucket(value, bucket):
            return bucket["label"]
    raise ValueError(f"{what} {value} is in no declared bucket")


def spread_bucket(spread_bps: float, buckets: Sequence[Mapping[str, Any]]) -> str:
    """The bucket of a spread read on whole basis points (the way the event is decided).

    Raises:
        ValueError: if the whole-basis-point spread is in no bucket (a pressure day has none).
    """

    return _label(round(float(spread_bps)), buckets, "spread")


def nearest_pressure_distance(
    position: int, pressure_positions: Sequence[int], last_position: int
) -> Optional[int]:
    """Panel days from `position` to the nearest pressure day, on the days to `last_position` only.

    `pressure_positions` is sorted. None if the window holds no pressure day.

    Raises:
        LookAheadError: if `position` or a pressure day is after `last_position`, the last scored day.
        ValueError: if `position` is itself a pressure day (it is not a false alarm).
    """

    late = [p for p in pressure_positions if p > last_position]
    if position > last_position or late:
        raise LookAheadError(
            f"the distance to a pressure day is read on the scored days to position {last_position}; "
            f"got day {position} and {len(late)} pressure day(s) after it"
        )
    if not pressure_positions:
        return None
    k = bisect.bisect_left(pressure_positions, position)
    if k < len(pressure_positions) and pressure_positions[k] == position:
        raise ValueError(f"day {position} is a pressure day, not a false alarm")
    near = []
    if k > 0:
        near.append(position - pressure_positions[k - 1])
    if k < len(pressure_positions):
        near.append(pressure_positions[k] - position)
    return min(near)


def false_alarm_records(
    *,
    positions: Sequence[int],
    flags: Sequence[int],
    pressure: Sequence[int],
    spreads: Sequence[float],
    day_types: Sequence[str],
    regimes: Sequence[str],
    pressure_positions: Sequence[int],
    last_position: int,
    spread_buckets: Sequence[Mapping[str, Any]],
    distance_buckets: Sequence[Mapping[str, Any]],
) -> List[Dict[str, Any]]:
    """The flagged days that are not pressure days, each with its spread, distance and group.

    `positions[k]` is the panel position of scored day k; the other sequences are aligned to it.
    """

    if not len(positions) == len(flags) == len(pressure) == len(spreads) == len(day_types) == len(regimes):
        raise ValueError("every series needs one value per scored day")
    out = []
    for k, position in enumerate(positions):
        if not flags[k] or pressure[k]:
            continue
        distance = nearest_pressure_distance(position, pressure_positions, last_position)
        out.append(
            {
                "position": position,
                "spread_bp": round(float(spreads[k])),
                "spread_bucket": spread_bucket(spreads[k], spread_buckets),
                "distance": distance,
                "distance_bucket": None if distance is None else _label(distance, distance_buckets, "distance"),
                "day_type": day_types[k],
                "regime": regimes[k],
            }
        )
    return out


def tabulate(records: Sequence[Mapping[str, Any]], key: str, labels: Sequence[str]) -> Dict[str, int]:
    """Count the records by `key` over `labels`, in that order.

    Raises:
        ValueError: if a record's label is not in `labels`, so the counts always sum to the total.
    """

    counts = {label: 0 for label in labels}
    for record in records:
        label = record[key]
        if label not in counts:
            raise ValueError(f"{key} {label!r} is not one of {list(labels)}")
        counts[label] += 1
    return counts


# -- the bootstrap and the power ------------------------------------------------


def quantile(ordered: Sequence[float], probability: float) -> float:
    """The judge's quantile (`pressure_judge._quantile`): linear between order statistics."""

    position = probability * (len(ordered) - 1)
    low = int(math.floor(position))
    high = min(low + 1, len(ordered) - 1)
    return ordered[low] + (ordered[high] - ordered[low]) * (position - low)


def stationary_blocks(n: int, block_length: float, rng: random.Random) -> Iterator[Tuple[int, int]]:
    """The (start, length) blocks of one stationary-bootstrap resample of `range(n)`.

    Geometric block lengths with mean `block_length`, wrapping at the end, cut to `n` days in all: the
    distribution of `metrics.stationary_bootstrap_indices`, drawn a block at a time.
    """

    if n < 1 or block_length < 1:
        raise ValueError("need n >= 1 and a block length of at least 1")
    restart = 1.0 / block_length
    scale = None if restart >= 1.0 else math.log(1.0 - restart)
    remaining = n
    while remaining:
        length = 1 if scale is None else 1 + int(math.log(1.0 - rng.random()) / scale)
        length = min(length, remaining)
        yield rng.randrange(n), length
        remaining -= length


def _counter(positions: Sequence[int], caught: Sequence[int], n: int):
    if len(positions) != len(caught):
        raise ValueError("one caught flag per onset")
    cumulative = [0]
    for c in caught:
        cumulative.append(cumulative[-1] + int(c))
    m = len(positions)

    def count(start: int, length: int) -> Tuple[int, int]:
        end = start + length
        low = bisect.bisect_left(positions, start)
        if end <= n:
            high = bisect.bisect_left(positions, end)
            return high - low, cumulative[high] - cumulative[low]
        wrap = bisect.bisect_left(positions, end - n)
        return (m - low) + wrap, (cumulative[m] - cumulative[low]) + cumulative[wrap]

    return count


def block_totals(
    positions: Sequence[int], caught: Sequence[int], n: int, start: int, length: int
) -> Tuple[int, int]:
    """(onsets, onsets flagged) among the `length` days from `start`, wrapping at day `n`."""

    return _counter(positions, caught, n)(start, length)


def recall_interval(
    positions: Sequence[int],
    caught: Sequence[int],
    n: int,
    *,
    block_length: float,
    replications: int,
    level: float,
    rng: random.Random,
) -> Tuple[float, Optional[float], Optional[float], int]:
    """(point recall, lower, upper, resamples with no onset) by the stationary bootstrap.

    The interval is None when any resample draws no onset: the recall is undefined there and the judge
    never drops a replicate.
    """

    count = _counter(positions, caught, n)
    point = sum(int(c) for c in caught) / len(positions)
    draws, undefined = [], 0
    for _ in range(replications):
        onsets = flagged = 0
        for start, length in stationary_blocks(n, block_length, rng):
            o, f = count(start, length)
            onsets += o
            flagged += f
        if onsets:
            draws.append(flagged / onsets)
        else:
            undefined += 1
    if undefined:
        return point, None, None, undefined
    draws.sort()
    tail = (1.0 - level) / 2.0
    return point, quantile(draws, tail), quantile(draws, 1.0 - tail), 0


def binomial_at_least(n: int, p: float, share: float) -> float:
    """P(Binomial(n, p) >= share * n): the chance the point recall alone reaches `share`."""

    least = math.ceil(share * n - 1e-12)
    return sum(math.comb(n, k) * p**k * (1 - p) ** (n - k) for k in range(least, n + 1))


def evenly_spaced(count: int, days: int) -> List[int]:
    """`count` onset positions evenly spread over `days` days."""

    if count < 1 or count > days:
        raise ValueError("need between 1 and `days` onsets")
    return [int((k + 0.5) * days / count) for k in range(count)]


def _seed(seed: int, *parts: object) -> int:
    material = "\x00".join([str(seed)] + [str(p) for p in parts])
    return int.from_bytes(hashlib.sha256(material.encode("utf-8")).digest()[:4], "big") & 0x7FFFFFFF


def recall_power(
    positions: Sequence[int],
    n: int,
    *,
    true_recalls: Sequence[float],
    climatology_recalls: Sequence[float],
    experiments: int,
    seed: int,
    block_length: float,
    replications: int,
    level: float,
    recall_at_least: float = 0.5,
) -> Dict[str, Dict[str, Any]]:
    """How often tier 1's recall conditions are met by a model with each true recall.

    Per true recall `r` (keyed `f"{r:g}"`): over `experiments` draws of which onsets are flagged (each with
    probability `r`), the share meeting the point condition (`point_at_least`), the share whose interval's
    lower end is above climatology recall `c` (`lower_above[c]`), both (`both[c]`), the share whose interval
    is unavailable, and the mean point recall. Experiment i at recall r is seeded from (seed, r, i), so the
    figures do not depend on which recalls are asked for together.
    """

    positions = sorted(positions)
    out: Dict[str, Dict[str, Any]] = {}
    for r in true_recalls:
        point_ok = 0
        unavailable = 0
        lower_ok = {c: 0 for c in climatology_recalls}
        both_ok = {c: 0 for c in climatology_recalls}
        mean_point = 0.0
        for i in range(experiments):
            rng = random.Random(_seed(seed, f"{r:g}", i))
            caught = [1 if rng.random() < r else 0 for _ in positions]
            point, lower, _, _ = recall_interval(
                positions, caught, n, block_length=block_length, replications=replications, level=level, rng=rng
            )
            mean_point += point
            meets_point = point >= recall_at_least
            point_ok += meets_point
            if lower is None:
                unavailable += 1
            for c in climatology_recalls:
                above = lower is not None and lower > c
                lower_ok[c] += above
                both_ok[c] += above and meets_point
        out[f"{r:g}"] = {
            "experiments": experiments,
            "mean_point_recall": mean_point / experiments,
            "point_at_least": point_ok / experiments,
            "interval_unavailable": unavailable / experiments,
            "lower_above": {f"{c:g}": lower_ok[c] / experiments for c in climatology_recalls},
            "both": {f"{c:g}": both_ok[c] / experiments for c in climatology_recalls},
        }
    return out
