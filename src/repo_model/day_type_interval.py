"""The interval a day-type row reports (#1454; H5, development pages; her ruling of 4 November 2026 on finding #1221, option (a)).

A pressure-day type is not contiguous (quarter-ends are about three months apart), so the interval a page puts on it is the
studentized domain interval of #1266: the whole aligned target-day series is resampled and the mean of the paired difference is
taken over the resampled days that belong to the type (`domain_intervals.studentized_domain_estimates`). The current interval, the
group's own days sorted into one short series, is reported beside it and labelled.

Two floors, hers: a type of fewer than `FLOOR_DAYS` days gets no interval; one of fewer than `THIN_DAYS` days is labelled thin.

Stdlib only.
"""

from __future__ import annotations

from datetime import date
from typing import Any, Dict, Mapping, Optional, Sequence, Tuple

from . import scoring_protocol as sp
from .domain_intervals import studentized_domain_estimates

FLOOR_DAYS = 20
THIN_DAYS = 60
SEED = 1196


def status(days: int) -> str:
    """`none` under the floor (no interval), `thin` under `THIN_DAYS`, `ok` otherwise."""

    if days < FLOOR_DAYS:
        return "none"
    return "thin" if days < THIN_DAYS else "ok"


def cell(days: int, current: Optional[dict], domain: Optional[dict]) -> Dict[str, Any]:
    """One day-type comparison as a page reports it: no interval under the floor, both intervals above it, the status beside them."""

    state = status(days)
    if state == "none":
        return {"days": days, "status": state}
    return {"days": days, "status": state, "current": current, "domain": domain}


def studentized_rows(cells: Mapping[object, Tuple[Mapping[date, float], Mapping[date, float], Sequence[date]]],
                     all_days: Sequence[date], seed: int = SEED, draws: int = sp.DRAWS, block_length: float = sp.BLOCK_LENGTH,
                     level: float = 0.90) -> Dict[object, dict]:
    """The studentized domain estimate of each group's mean paired difference, as `spread_mr_variants_761.domain_rows` makes the
    percentile one: the same cells `(benchmark scores, candidate scores, the group's days)`, the same draws, a row with the group
    mean as `difference` and the interval as `difference_interval`, without skill; `method` says "studentized domain". A group
    whose interval is unavailable reads `undefined` with the reason, as `run_pairs` does; a bound read with resamples left out
    carries `dropped_resamples` and `draws` (#1239).

    Raises:
        ValueError: if a group day is not among `all_days`.
    """

    days = sorted(all_days)
    position = {day: i for i, day in enumerate(days)}
    prepared = {}
    for key, (benchmark, candidate, group) in cells.items():
        missing = [day for day in group if day not in position]
        if missing:
            raise ValueError(f"cell {key!r}: {len(missing)} group days ({missing[0]} first) are not among the {len(days)} aligned days")
        prepared[key] = ([benchmark[day] - candidate[day] for day in days], [position[day] for day in group])
    done = studentized_domain_estimates(prepared, len(days), block_length=block_length, seed=seed, replications=draws, level=level)
    out: Dict[object, dict] = {}
    for key, (benchmark, candidate, group) in cells.items():
        entry = done[key]
        row = {"days": entry["count"], "method": "studentized domain",
               "benchmark_mean": sum(benchmark[d] for d in group) / len(group) if group else None,
               "candidate_mean": sum(candidate[d] for d in group) / len(group) if group else None}
        if "interval" in entry:
            row["difference"] = entry["mean"]
            row["difference_interval"] = [entry["interval"]["lower"], entry["interval"]["upper"]]
            row["standard_error"] = entry["standard_error"]
            if entry["dropped_resamples"]:
                row["dropped_resamples"], row["draws"] = entry["dropped_resamples"], entry["draws"]
        else:
            row["undefined"] = entry.get("interval_unavailable", "the group has no day")
        out[key] = row
    return out
