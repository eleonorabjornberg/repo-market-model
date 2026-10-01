"""The splits every published result is reported under: regime and pressure-day type (#27).

`docs/pivot/plan.md` §1 and `docs/decisions/pressure-probability.md`: a pooled
figure alone is not a result. Every comparison is split by regime and by
pressure-day type, and each split carries its own paired interval.

**Pressure-day type** is a property of the scored day, read from its date and its
scheduled coupon settlement. One type per day, the first that applies, in the
order of `PRESSURE_DAY_TYPES`: the order and the five types are those of
directive 06's prototype (`docs/pivot/directives/06-prototype/emit_visual.py`).
Month-end and quarter-end are the last business day of the period by the market
holiday table (`data.month_end`, `data.quarter_end`), never by the panel's grid.

**Regime** is provisional. No declared regime state exists yet: the reserve
scarcity indicator of plan §1 is later work. Until it does, a regime is a
calendar period, and the periods are the slices `docs/pivot/lag-assessment.md`
§2 reported the lag on. Whether these are the regimes a result is split by is
Eleonora's to rule; `REGIMES` is the one place to change them.

Standard library only.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from datetime import date
from typing import Callable, Dict, List, Mapping, Optional, Sequence, Tuple

from .data import DailyObservation, month_end, quarter_end, tax_date

#: The pressure-day types, in the order the first applicable one is taken.
PRESSURE_DAY_TYPES: Tuple[str, ...] = (
    "quarter_end",
    "month_end",
    "tax_window",
    "coupon_settlement",
    "other",
)

#: The panel column that marks a coupon settlement day: a settlement amount,
#: USD billions, 0 on a day with none.
COUPON_COLUMN = "treasury_settlement_coupons"

#: The provisional regimes: `(name, first day, last day)`, contiguous and in
#: order. The periods of `docs/pivot/lag-assessment.md` §2.
REGIMES: Tuple[Tuple[str, date, date], ...] = (
    ("2018-19", date(2018, 1, 1), date(2019, 12, 31)),
    ("2020", date(2020, 1, 1), date(2020, 12, 31)),
    ("2021-23", date(2021, 1, 1), date(2023, 12, 31)),
    ("2024", date(2024, 1, 1), date(2024, 12, 31)),
    ("2025-26", date(2025, 1, 1), date(2026, 12, 31)),
)

#: What a regime split is, written into every record that carries one.
REGIME_DEFINITION = (
    "provisional: calendar periods, the slices of docs/pivot/lag-assessment.md "
    "section 2, until a declared regime state exists"
)

#: What a pressure-day type is, written into every record that carries one.
DAY_TYPE_DEFINITION = (
    "the scored day's first applicable type: last business day of a quarter, "
    "of a month, the tax window (data.tax_date), a coupon settlement day "
    "(treasury_settlement_coupons > 0), else other"
)


def pressure_day_type(day: date, coupon_settlement: Optional[float]) -> str:
    """The pressure-day type of `day`, given its scheduled coupon settlement.

    Raises:
        ValueError: `coupon_settlement` is `None` (a day whose settlement is
            unknown is not typed as one without), or the market holiday table
            does not cover `day`'s month.
    """

    if quarter_end(day) == 1.0:
        return "quarter_end"
    if month_end(day) == 1.0:
        return "month_end"
    if tax_date(day) == 1.0:
        return "tax_window"
    if coupon_settlement is None:
        raise ValueError(
            f"{day.isoformat()} has no {COUPON_COLUMN} value, so whether it is a "
            "coupon settlement day is unknown"
        )
    if float(coupon_settlement) > 0.0:
        return "coupon_settlement"
    return "other"


def row_day_type(row: DailyObservation) -> str:
    """`pressure_day_type` of a panel row, read off its date and coupon column."""

    return pressure_day_type(row.date, row.values.get(COUPON_COLUMN))


def regime(day: date) -> str:
    """The provisional regime `day` falls in.

    Raises:
        ValueError: a day outside every period in `REGIMES`.
    """

    for name, first, last in REGIMES:
        if first <= day <= last:
            return name
    raise ValueError(f"{day.isoformat()} falls in no declared regime period")


@dataclass(frozen=True)
class Strata:
    """Each scored day's regime and pressure-day type, aligned with the scored days.

    `unavailable` names why a split could not be made (the panel has no coupon
    column, or a day falls outside the holiday table or the regime periods);
    the split is then `None` and the record says why instead of guessing.
    """

    regimes: Optional[Tuple[str, ...]]
    day_types: Optional[Tuple[str, ...]]
    unavailable: Mapping[str, str]


def scored_strata(scored_rows: Sequence[DailyObservation]) -> Strata:
    """The two splits over the scored rows, each refused whole rather than in part."""

    unavailable: Dict[str, str] = {}
    regimes: Optional[Tuple[str, ...]]
    day_types: Optional[Tuple[str, ...]]
    try:
        regimes = tuple(regime(row.date) for row in scored_rows)
    except ValueError as exc:
        regimes = None
        unavailable["by_regime"] = str(exc)
    try:
        day_types = tuple(row_day_type(row) for row in scored_rows)
    except ValueError as exc:
        day_types = None
        unavailable["by_day_type"] = str(exc)
    return Strata(regimes, day_types, unavailable)


def _order(split: str) -> Tuple[str, ...]:
    if split == "by_regime":
        return tuple(name for name, _first, _last in REGIMES)
    return PRESSURE_DAY_TYPES


def split_seed(seed: int, *parts: str) -> int:
    """A stratum's bootstrap seed: the run's seed and the stratum's name, digested.

    Each stratum draws its own resamples, reproducibly, and no two strata of a
    run share a sequence.
    """

    material = ":".join([str(seed), *parts]).encode("utf-8")
    return int.from_bytes(hashlib.sha256(material).digest()[:4], "big")


def split_document(
    strata: Optional[Strata],
    summary: Callable[[str, str, List[int]], dict],
) -> Dict[str, dict]:
    """`by_regime` and `by_day_type`, each label's entry built by `summary`.

    `summary(split, label, positions)` receives the positions of the scored
    days in that stratum, in scored order. A label with no scored day is left
    out. A split `strata` could not make is absent, with its reason under
    `unavailable`.
    """

    document: Dict[str, dict] = {}
    if strata is None:
        return document
    for split, labels in (("by_regime", strata.regimes), ("by_day_type", strata.day_types)):
        if labels is None:
            continue
        entries = {}
        for label in _order(split):
            positions = [index for index, value in enumerate(labels) if value == label]
            if positions:
                entries[label] = summary(split, label, positions)
        document[split] = entries
    if strata.unavailable:
        document["unavailable"] = dict(sorted(strata.unavailable.items()))
    return document


def split_definitions() -> dict:
    """The definitions a record states beside its splits."""

    return {"by_regime": REGIME_DEFINITION, "by_day_type": DAY_TYPE_DEFINITION}
