"""The H9 targets and the as-of benchmarks of the step 1 screen (#639).

H9 (`docs/research/hypotheses/H9.md`): richer, more continuous targets than 26 onsets may carry more learnable signal. Step 1
screens them before any model: how forecastable each is against its own as-of persistence and calendar climatology, whether it
leads the SOFR − IORB pressure episodes, and how much it shares with SOFR − IORB. This module holds what the screen reads and
the pieces it computes; `scripts/richer_targets_639.py` runs it.

**The targets** are panel columns built here from earlier panel columns, each from its own row and earlier rows only
(`build_columns`): the SOFR 99th percentile minus IORB, SOFR's 99th-minus-1st percentile dispersion, TGCR and BGCR each minus IORB
with their dispersion, EFFR minus IORB, ON RRP take-up (level and daily change) and standing repo facility take-up. The
percentiles of TGCR and BGCR are read from the tracked snapshots (`percentile_series`) under the registry's declared lag, which is
the rate's own. Rates are in percent and the targets in bp; take-up is in USD billions.

**Off.** `COLUMN_FIELDS` is not part of `contract.FEATURE_FIELDS`: no published panel, declaration or record reads these columns. The
screen switches them on for its own run. Each column is declared on every source field it draws on, so the as-of rule
(`asof.InformationRule`) reads it at the latest row whose every field was public at the decision instant.

**The benchmarks** are scoring protocol v1 §4's B1 (the last public value plus the empirical distribution of the h-row changes
over the trailing two years) and B2 (the trailing year's values on days of the target day's type), generalised from the spread
to any series and to the leads 1, 2, 3, 5 and 10 (`b1_quantiles`, `b2_quantiles`). They use `protocol_benchmarks`' own window,
interpolation and look-ahead guard (`_require_public`), and score with `scoring_protocol.grid_crps`. They are a screen's yardsticks,
not the protocol's registered benchmarks of H9: the protocol's section 9 applies B1 and B2 to each target prospectively.

Standard library only, like the rest of `src/` outside `ml.py`.
"""

from __future__ import annotations

import math
import random
from contextlib import contextmanager
from bisect import bisect_left, bisect_right
from datetime import date, datetime, time
from pathlib import Path
from types import MappingProxyType
from typing import Dict, List, Mapping, NamedTuple, Optional, Sequence, Tuple

from . import contract
from .asof import InformationRule
from .contract import (
    FEATURE_FIELDS,
    ON_RRP_OPERATION_RESULTS_FIELDS,
    SRF_OPERATION_RESULTS_FIELDS,
)
from .data import DailyObservation
from .measurement_fields import carry_one_row_holes, series_from_snapshots
from .metrics import stationary_bootstrap_indices
from .protocol_benchmarks import _require_public, empirical_quantiles, years_before
from .scoring_protocol import GRID, ProtocolError, _prefix, _resampled_sum, _segments, grid_crps

__all__ = [
    "COLUMN_FIELDS",
    "LEADS",
    "RAW_SERIES",
    "TARGETS",
    "Target",
    "as_of_rows",
    "assemble",
    "b1_quantiles",
    "b2_quantiles",
    "as_target",
    "build_columns",
    "choose_targets",
    "crps",
    "median",
    "median_error",
    "percentile_series",
    "pre_onset_interval",
    "spearman",
    "swap_target_fields",
    "target_fields",
    "spearman_interval",
    "window_first",
]

#: The leads of the screen, in panel days: the decision is made this many panel days before the scored day.
LEADS: Tuple[int, ...] = (1, 2, 3, 5, 10)
#: A benchmark needs this many h-row changes (B1) or same-type values (B2) in its window, or the day is dropped for both.
MINIMUM_CHANGES = 60
MINIMUM_CLIMATOLOGY = 4
#: The stationary bootstrap's mean block length, in panel days (scoring protocol §5), and the two-sided level of the intervals.
BLOCK_LENGTH = 10
INTERVAL = 0.90

_SOFR = "nyfed_sofr"
_IORB = tuple(FEATURE_FIELDS["iorb"])
_SOFR_P99 = ((_SOFR, "SOFR_p99"),)
_SOFR_P1 = ((_SOFR, "SOFR_p1"),)
_TGCR = tuple(FEATURE_FIELDS["tgcr"])
_BGCR = tuple(FEATURE_FIELDS["bgcr"])
_EFFR = tuple(FEATURE_FIELDS["effr"])
_TGCR_P99 = (("nyfed_tgcr", "TGCR_p99"),)
_TGCR_P1 = (("nyfed_tgcr", "TGCR_p1"),)
_BGCR_P99 = (("nyfed_bgcr", "BGCR_p99"),)
_BGCR_P1 = (("nyfed_bgcr", "BGCR_p1"),)
_ON_RRP = tuple(ON_RRP_OPERATION_RESULTS_FIELDS)
_SRF = tuple(SRF_OPERATION_RESULTS_FIELDS)

#: Raw column -> (snapshot directory under the snapshots root, series id): the secured rates' 1st and 99th percentiles.
RAW_SERIES: Mapping[str, Tuple[str, str]] = {
    "tgcr_p1": ("funding_inputs", "TGCR_p1"),
    "tgcr_p99": ("funding_inputs", "TGCR_p99"),
    "bgcr_p1": ("funding_inputs", "BGCR_p1"),
    "bgcr_p99": ("funding_inputs", "BGCR_p99"),
}
#: The percentile series have single-day holes; a one-row hole takes the earlier value (`measurement_fields.carry_one_row_holes`).
ONE_ROW_HOLE_COLUMNS = tuple(RAW_SERIES)


class Target(NamedTuple):
    """One H9 target: the panel column it is, its unit, the group it belongs to and its definition."""

    column: str
    unit: str
    group: str
    definition: str


#: The targets of #639, in the issue's order. Fixed before any score.
TARGETS: Tuple[Target, ...] = (
    Target("sofr_p99_iorb_bps", "bp", "sofr_tail", "SOFR 99th percentile − IORB"),
    Target("sofr_dispersion_bps", "bp", "sofr_tail", "SOFR 99th − 1st percentile"),
    Target("tgcr_iorb_bps", "bp", "tgcr", "TGCR − IORB"),
    Target("tgcr_dispersion_bps", "bp", "tgcr", "TGCR 99th − 1st percentile"),
    Target("bgcr_iorb_bps", "bp", "bgcr", "BGCR − IORB"),
    Target("bgcr_dispersion_bps", "bp", "bgcr", "BGCR 99th − 1st percentile"),
    Target("effr_iorb_bps", "bp", "effr", "EFFR − IORB"),
    Target("on_rrp_bn", "USD bn", "on_rrp", "ON RRP take-up, the day's total accepted"),
    Target("on_rrp_change_bn", "USD bn", "on_rrp", "ON RRP take-up, change from the previous panel day"),
    Target("srf_take_up_bn", "USD bn", "srf", "standing repo facility take-up, the day's total accepted"),
)

#: Every column's source fields, for the as-of rule. **Off**: switched on only by the screen's own run, never part of
#: `contract.FEATURE_FIELDS`.
COLUMN_FIELDS: Mapping[str, Tuple[Tuple[str, str], ...]] = {
    "tgcr_p1": _TGCR_P1,
    "tgcr_p99": _TGCR_P99,
    "bgcr_p1": _BGCR_P1,
    "bgcr_p99": _BGCR_P99,
    "sofr_p1": _SOFR_P1,
    "sofr_p99": _SOFR_P99,
    "sofr_p99_iorb_bps": _SOFR_P99 + _IORB,
    "sofr_dispersion_bps": _SOFR_P99 + _SOFR_P1,
    "tgcr_iorb_bps": _TGCR + _IORB,
    "tgcr_dispersion_bps": _TGCR_P99 + _TGCR_P1,
    "bgcr_iorb_bps": _BGCR + _IORB,
    "bgcr_dispersion_bps": _BGCR_P99 + _BGCR_P1,
    "effr_iorb_bps": _EFFR + _IORB,
    "on_rrp_bn": _ON_RRP,
    "on_rrp_change_bn": _ON_RRP,
    "srf_take_up_bn": _SRF,
}


def _get(row: DailyObservation, column: str) -> Optional[float]:
    value = row.values.get(column)
    return None if value is None else float(value)


def _minus(row: DailyObservation, high: str, low: str) -> Optional[float]:
    a, b = _get(row, high), _get(row, low)
    return None if a is None or b is None else (a - b) * 100.0


def build_columns(rows: Sequence[DailyObservation]) -> List[DailyObservation]:
    """`rows` with the target columns added, each from its own and the previous row only.

    A column whose inputs are missing on a row it needs is `None` there. Rates are in percent on the panel and the targets are in bp.
    """

    out: List[DailyObservation] = []
    for position, row in enumerate(rows):
        values: Dict[str, Optional[float]] = dict(row.values)
        values["sofr_p99_iorb_bps"] = _minus(row, "sofr_p99", "iorb")
        values["sofr_dispersion_bps"] = _minus(row, "sofr_p99", "sofr_p1")
        values["tgcr_iorb_bps"] = _minus(row, "tgcr", "iorb")
        values["tgcr_dispersion_bps"] = _minus(row, "tgcr_p99", "tgcr_p1")
        values["bgcr_iorb_bps"] = _minus(row, "bgcr", "iorb")
        values["bgcr_dispersion_bps"] = _minus(row, "bgcr_p99", "bgcr_p1")
        values["effr_iorb_bps"] = _minus(row, "effr", "iorb")
        level = _get(row, "on_rrp")
        values["on_rrp_bn"] = level
        before = _get(rows[position - 1], "on_rrp") if position else None
        values["on_rrp_change_bn"] = None if level is None or before is None else level - before
        values["srf_take_up_bn"] = _get(row, "srf_take_up")
        out.append(DailyObservation(row.date, values))
    return out


def percentile_series(snapshots: Path, cutoff: datetime) -> Dict[str, Dict[date, float]]:
    """`{column: {ref_date: value}}` for `RAW_SERIES`, from the tracked snapshots, the latest vintage public by `cutoff`."""

    wanted: Dict[str, set] = {}
    for _column, (directory, series) in RAW_SERIES.items():
        wanted.setdefault(directory, set()).add(series)
    parsed = {
        directory: series_from_snapshots(snapshots / directory, names, cutoff) for directory, names in wanted.items()
    }
    return {column: parsed[directory][series] for column, (directory, series) in RAW_SERIES.items()}


def assemble(
    rows: Sequence[DailyObservation], snapshots: Path, *, cutoff: datetime, end: date
) -> Tuple[List[DailyObservation], Dict[str, object]]:
    """`rows` up to `end` with the raw percentile columns and the target columns added.

    Returns the rows and a summary of the holes of each raw column and the one-row holes filled.
    """

    parsed = percentile_series(snapshots, cutoff)
    added: List[DailyObservation] = []
    holes: Dict[str, List[str]] = {name: [] for name in RAW_SERIES}
    for row in rows:
        if row.date > end:
            continue
        values = dict(row.values)
        for column in RAW_SERIES:
            value = parsed[column].get(row.date)
            if value is None:
                holes[column].append(row.date.isoformat())
            values[column] = value
        added.append(DailyObservation(row.date, values))
    filled, carried = carry_one_row_holes(added, ONE_ROW_HOLE_COLUMNS)
    built = build_columns(filled)
    return built, {
        "holes": {name: dates for name, dates in holes.items() if dates},
        "one_row_holes_filled": carried,
        "target_missing": {
            target.column: sum(1 for row in built if row.values.get(target.column) is None) for target in TARGETS
        },
    }


# -- the as-of reads -----------------------------------------------------------------------------------------------


def as_of_rows(
    rows: Sequence[DailyObservation],
    registry: Mapping[str, Mapping[str, object]],
    columns: Sequence[str],
    *,
    leads: Sequence[int],
    scored: Sequence[int],
    decision_time: time = time(16, 0),
) -> Dict[int, Dict[str, List[int]]]:
    """For each lead and column, the latest row public at the decision instant of each scored row.

    The decision is made `lead` panel days before the scored row (`InformationRule(horizon=lead)`); both guards run on every read
    (`InformationRule.check`: nothing newer than the decision instant, nothing older than the latest public value).
    """

    dates = [row.date for row in rows]
    out: Dict[int, Dict[str, List[int]]] = {}
    for lead in leads:
        rule = InformationRule(registry, tuple(columns), decision_time=decision_time, horizon=lead)
        wanted = {group.feature: position for position, group in enumerate(rule.groups) if position}
        per_column: Dict[str, List[int]] = {column: [] for column in columns}
        for index in scored:
            info = rule.information_set(dates, index)
            rule.check(dates, info)
            for column in columns:
                per_column[column].append(info.reads[wanted[column]].row)
        out[lead] = per_column
    return out


# -- the benchmarks ------------------------------------------------------------------------------------------------


def window_first(dates: Sequence[date], decision_index: int, years: int) -> int:
    """The first row strictly after the decision day less `years` years."""

    start = years_before(dates[decision_index], years)
    for index, when in enumerate(dates):
        if when > start:
            return index
    raise ProtocolError(f"no row after {start}")


def b1_quantiles(
    values: Sequence[Optional[float]], dates: Sequence[date], anchor: int, h: int, *, first: int
) -> Optional[List[float]]:
    """B1: the value at the anchor plus the h-row changes of the window `first..anchor`, on the protocol's grid.

    `None` when the anchor has no value or the window holds fewer than `MINIMUM_CHANGES` changes (the day is dropped for both
    benchmarks). Every row read is at or before the anchor (`LookAheadError` otherwise).
    """

    last = values[anchor]
    if last is None:
        return None
    ends = list(range(max(first, h), anchor + 1))
    _require_public(ends, anchor, dates, f"B1 at lead {h}")
    changes = sorted(values[s] - values[s - h] for s in ends if values[s] is not None and values[s - h] is not None)
    if len(changes) < MINIMUM_CHANGES:
        return None
    return empirical_quantiles(changes, last)


def b2_quantiles(
    values: Sequence[Optional[float]],
    kinds: Sequence[str],
    dates: Sequence[date],
    anchor: int,
    kind: str,
    *,
    first: int,
) -> Optional[List[float]]:
    """B2: the values of the window `first..anchor` on days of `kind`, on the protocol's grid.

    `None` when fewer than `MINIMUM_CLIMATOLOGY` such values exist.
    """

    rows = [s for s in range(first, anchor + 1) if kinds[s] == kind and values[s] is not None]
    _require_public(rows, anchor, dates, "B2")
    if len(rows) < MINIMUM_CLIMATOLOGY:
        return None
    return empirical_quantiles(sorted(values[s] for s in rows))


def crps(quantiles: Sequence[float], observed: float) -> float:
    """Twice the mean pinball loss over the protocol's grid (`scoring_protocol.grid_crps`)."""

    return grid_crps(quantiles, observed)


def median(quantiles: Sequence[float]) -> float:
    return quantiles[GRID.index(0.5)]


def median_error(quantiles: Sequence[float], observed: float) -> float:
    """The absolute error of the forecast's median."""

    return abs(median(quantiles) - observed)


# -- rank statistics -----------------------------------------------------------------------------------------------


def _average_ranks(values: Sequence[float]) -> List[float]:
    order = sorted(range(len(values)), key=values.__getitem__)
    ranks = [0.0] * len(values)
    i = 0
    while i < len(order):
        j = i
        while j + 1 < len(order) and values[order[j + 1]] == values[order[i]]:
            j += 1
        for k in range(i, j + 1):
            ranks[order[k]] = (i + j) / 2.0 + 1.0
        i = j + 1
    return ranks


def _pearson(x: Sequence[float], y: Sequence[float]) -> Optional[float]:
    n = len(x)
    if n < 2:
        return None
    mx, my = sum(x) / n, sum(y) / n
    sxx = sum((a - mx) ** 2 for a in x)
    syy = sum((b - my) ** 2 for b in y)
    if sxx <= 0.0 or syy <= 0.0:
        return None
    return sum((a - mx) * (b - my) for a, b in zip(x, y)) / math.sqrt(sxx * syy)


def spearman(x: Sequence[float], y: Sequence[float]) -> Optional[float]:
    """Spearman's rank correlation, with average ranks for ties; `None` when a side is constant or there are under two pairs."""

    if len(x) != len(y):
        raise ValueError("two series of different lengths")
    return _pearson(_average_ranks(list(x)), _average_ranks(list(y)))


def _quantile_of(ordered: Sequence[float], level: float) -> float:
    position = level * (len(ordered) - 1)
    low = int(position)
    weight = position - low
    value = ordered[low]
    return value + weight * (ordered[low + 1] - value) if weight else value


def spearman_interval(
    x: Sequence[float], y: Sequence[float], *, seed: int, draws: int, block: float = BLOCK_LENGTH
) -> Dict[str, Optional[float]]:
    """Spearman's rho with a `INTERVAL` stationary-bootstrap interval over the pairs in the order given.

    The ranks are those of the full sample and each resample takes Pearson's correlation of its ranks, with the sums read off
    prefix sums (`scoring_protocol._resampled_sum`), so a draw costs one pass over its blocks. The interval is an approximation to
    re-ranking each resample, and says so in the screen's tables.
    """

    n = len(x)
    rho = spearman(x, y)
    if rho is None or n < 3:
        return {"n": n, "rho": rho, "low": None, "high": None}
    rx, ry = _average_ranks(list(x)), _average_ranks(list(y))
    prefixes = [_prefix(v) for v in (rx, ry, [a * a for a in rx], [b * b for b in ry], [a * b for a, b in zip(rx, ry)])]
    rng = random.Random(seed)
    found: List[float] = []
    for _ in range(draws):
        starts, ends = _segments(stationary_bootstrap_indices(n, block, rng), n)
        sx, sy, sxx, syy, sxy = (_resampled_sum(p, starts, ends) for p in prefixes)
        denominator = (n * sxx - sx * sx) * (n * syy - sy * sy)
        if denominator > 0.0:
            found.append((n * sxy - sx * sy) / math.sqrt(denominator))
    found.sort()
    if not found:
        return {"n": n, "rho": rho, "low": None, "high": None}
    tail = (1.0 - INTERVAL) / 2.0
    return {"n": n, "rho": rho, "low": _quantile_of(found, tail), "high": _quantile_of(found, 1.0 - tail)}


def pre_onset_interval(
    pre_by_onset: Sequence[Sequence[float]], other: Sequence[float], *, seed: int, draws: int
) -> Optional[Dict[str, Optional[float]]]:
    """The pre-onset values against the other days', with intervals from resampling the onsets.

    `pre_by_onset` holds, for each onset, the series' values on the days before it; `other` the values on every other scored day.
    Reports the means, the difference in units of `other`'s standard deviation (`std_diff`) and the AUC (the share of
    (pre-onset, other) pairs in which the pre-onset value is higher, ties half). The interval resamples whole onsets, since the
    days before one onset are not independent.
    """

    groups = [list(group) for group in pre_by_onset if group]
    if not groups or len(other) < 2:
        return None
    ordered = sorted(other)
    mean_other = sum(other) / len(other)
    sd = math.sqrt(sum((v - mean_other) ** 2 for v in other) / (len(other) - 1))

    def auc_of(values: Sequence[float]) -> float:
        total = 0.0
        for v in values:
            below = bisect_left(ordered, v)
            equal = bisect_right(ordered, v) - below
            total += below + 0.5 * equal
        return total / (len(values) * len(ordered))

    def point(chosen: Sequence[Sequence[float]]) -> Tuple[float, float, float]:
        values = [v for group in chosen for v in group]
        mean = sum(values) / len(values)
        return mean, (None if sd <= 0.0 else (mean - mean_other) / sd), auc_of(values)

    mean_pre, std_diff, auc = point(groups)
    rng = random.Random(seed)
    diffs: List[float] = []
    aucs: List[float] = []
    for _ in range(draws):
        chosen = [groups[rng.randrange(len(groups))] for _ in groups]
        _m, d, a = point(chosen)
        aucs.append(a)
        if d is not None:
            diffs.append(d)
    aucs.sort()
    diffs.sort()
    tail = (1.0 - INTERVAL) / 2.0
    return {
        "onsets": len(groups),
        "n_pre": sum(len(g) for g in groups),
        "n_other": len(other),
        "mean_pre": mean_pre,
        "mean_other": mean_other,
        "std_diff": std_diff,
        "std_diff_low": _quantile_of(diffs, tail) if diffs else None,
        "std_diff_high": _quantile_of(diffs, 1.0 - tail) if diffs else None,
        "auc": auc,
        "auc_low": _quantile_of(aucs, tail),
        "auc_high": _quantile_of(aucs, 1.0 - tail),
    }


# -- step 2 (#706): the choice of targets, and the label swap ------------------------------------------------------

#: Eleonora's rule of 13 October 2026 (comment 6149435134 on #639): drop a target whose rank correlation with SOFR - IORB has
#: this magnitude or more, drop one with fewer onsets than `MINIMUM_ONSETS` in the development sample, take the best `TAKE`.
OVERLAP_LIMIT = 0.8
MINIMUM_ONSETS = 15
TAKE = 3


def _figure(screen: Mapping[str, object], path: Sequence[str], target: str) -> float:
    node: object = screen
    for key in path:
        if not isinstance(node, Mapping) or key not in node:
            raise ValueError(f"step 1's screen has no {'/'.join(path)} for {target}")
        node = node[key]
    if not isinstance(node, Mapping) or target not in node:
        raise ValueError(f"step 1's screen has no {'/'.join(path)} for {target}")
    return node[target]


def choose_targets(
    screen: Mapping[str, object],
    *,
    overlap_limit: float = OVERLAP_LIMIT,
    minimum_onsets: int = MINIMUM_ONSETS,
    take: int = TAKE,
) -> Dict[str, object]:
    """The targets step 2 models, by Eleonora's rule applied to step 1's `screen.json` (#639 ruling, 13 October 2026).

    1. Drop a target whose pooled rank correlation with SOFR - IORB (`overlap[t]["all:level"]["rho"]`) has magnitude
       `overlap_limit` or more.
    2. Drop a target with fewer than `minimum_onsets` onsets (`lead.pre_onset[t]["all"]["onsets"]`).
    3. Rank the rest by the pre-onset AUC at lead 1 within the as-of state, averaged over the ample and scarce states, taken as
       published (a value read high before onsets is above one half). Ties go to the larger of the grid-CRPS skill of B1 over B2
       and of B2 over B1 at lead 1.
    4. Take the best `take`; fewer survivors are all taken (`fewer_than_requested`).

    A figure the screen does not hold is a `ValueError`: a target is never dropped for a missing number.
    """

    targets = sorted(screen["overlap"])
    dropped: Dict[str, Tuple[str, float]] = {}
    ranking: List[Dict[str, object]] = []
    for target in targets:
        rho = _figure(screen, ("overlap",), target)["all:level"]["rho"]
        onsets = _figure(screen, ("lead", "pre_onset"), target)["all"]["onsets"]
        if rho is None:
            raise ValueError(f"step 1's screen holds no pooled correlation for {target}")
        if abs(rho) >= overlap_limit:
            dropped[target] = ("overlap", rho)
            continue
        if onsets < minimum_onsets:
            dropped[target] = ("onsets", onsets)
            continue
        try:
            states = _figure(screen, ("lead", "pre_onset"), target)
            ample, scarce = states["regime:ample"]["auc"], states["regime:scarce"]["auc"]
            cell = _figure(screen, ("forecastability",), target)["1"]["all"]
            b1, b2 = cell["b1"], cell["b2"]
        except KeyError as error:
            raise ValueError(f"step 1's screen holds no {error} for {target}") from error
        if ample is None or scarce is None:
            raise ValueError(f"step 1's screen holds no state AUC for {target}")
        skill = max((b2 - b1) / b2 if b2 else 0.0, (b1 - b2) / b1 if b1 else 0.0)
        ranking.append(
            {"target": target, "auc_ample": ample, "auc_scarce": scarce, "auc_mean": (ample + scarce) / 2.0, "skill_lead_1": skill}
        )
    ranking.sort(key=lambda row: (-row["auc_mean"], -row["skill_lead_1"], row["target"]))
    chosen = [row["target"] for row in ranking[:take]]
    return {"chosen": chosen, "ranking": ranking, "dropped": dropped, "fewer_than_requested": len(ranking) < take}


def target_fields(column: str) -> Tuple[Tuple[str, str], ...]:
    """The source fields a target is read from (`COLUMN_FIELDS`); only the H9 target columns have a swap."""

    if column not in {t.column for t in TARGETS}:
        raise ValueError(f"{column!r} is not an H9 target column")
    return COLUMN_FIELDS[column]


@contextmanager
def swap_target_fields(column: str):
    """For this block, the field map's `sofr` and `iorb` are the target's own sources, so the as-of rule reads `spread_bps` under them.

    The model class of #634 forecasts `spread_bps = 100 * (sofr - iorb)`. `as_target` puts a target in that slot; this puts its
    release lag there too, so its decision-instant reads obey the sources it comes from (the ON RRP operation results, or the
    secured rate's percentiles), not SOFR's and not IORB's. **Off** outside the block: nothing published reads the swapped map.
    """

    fields = target_fields(column)
    sources = tuple(sorted({source for source, _field in fields}))
    saved = (contract.FEATURE_FIELDS, contract.FEATURE_SOURCES)
    contract.FEATURE_FIELDS = MappingProxyType({**saved[0], "sofr": fields, "iorb": fields})
    contract.FEATURE_SOURCES = MappingProxyType({**saved[1], "sofr": sources, "iorb": sources})
    try:
        yield
    finally:
        contract.FEATURE_FIELDS, contract.FEATURE_SOURCES = saved


def as_target(rows: Sequence[DailyObservation], column: str) -> List[DailyObservation]:
    """`rows` with `column` in the slot the model reads as SOFR - IORB: `iorb` is 0 and `sofr` the target, so `spread_bps` equals it.

    A row with no value is a `ValueError`; the caller drops a leading hole (the first ON RRP change) before swapping.
    """

    if column not in {t.column for t in TARGETS}:
        raise ValueError(f"{column!r} is not an H9 target column")
    out: List[DailyObservation] = []
    for row in rows:
        value = row.values.get(column)
        if value is None:
            raise ValueError(f"{column} is missing on {row.date}")
        values = dict(row.values)
        values["iorb"] = 0.0
        values["sofr"] = float(value) / 100.0
        out.append(DailyObservation(row.date, values))
    return out
