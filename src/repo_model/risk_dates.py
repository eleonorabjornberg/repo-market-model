"""One place that says whether a day is a risk date (#682, finding #669).

Two definitions were in use, on different pages, so the "ordinary-day" figures of those pages were on different
populations. Both are named here and neither is preferred: which one H2 and H5 read is Eleonora's ruling.

``SCHEDULED``
    The judge's ``risk_date`` grouping (``pressure_judge``): a quarter-end, a tax date, or a day on which coupons settle.
    Calendar facts known ahead of the day.
``NON_ORDINARY``
    The model's own risk-date rule (``ml._RiskDateDesign.member``, ``announcement_dating_rescore.risk_flag``): any
    pressure-day type other than ``ordinary`` (so month-ends too, as the split declaration windows them), or a coupon
    settlement. ``coupon_clause=False`` drops the coupon settlement, as the model does at horizons above 1.

``reporting_on=`` (``NON_ORDINARY`` only) reads the day type as ``SplitDeclaration.reporting_day_type`` does, from the date: a
month-end is one of the month's last two business days, not a calendar-day window. H5's context rule
(``spread_mr_variants.is_risk_day``) and H6's risk dates (``risk_date_spread``) read it so. It is the same rule with the
day type read another way; which reading is the shared definition is Eleonora's open ruling (#800), so each caller keeps its own.

They differ by the month-ends that are not quarter-ends. Month-ends are prone to pressure, so ``NON_ORDINARY`` takes
them out of the "ordinary" set and makes the remaining days easier to rank.

Standard library only. A data hole in a calendar column is a data error (``ValueError``).
"""

from __future__ import annotations

from datetime import date
from typing import List, Mapping, Optional, Sequence

from . import turn_days

SCHEDULED = "scheduled"
NON_ORDINARY = "non_ordinary"
DEFINITIONS = (SCHEDULED, NON_ORDINARY)

COUPONS = "treasury_settlement_coupons"


def _coupon_settles(values: Mapping[str, Optional[float]]) -> bool:
    coupons = values.get(COUPONS)
    return coupons is not None and float(coupons) > 0.0


def non_ordinary_day(day_type: str, coupons: Optional[float], coupon_clause: bool = True) -> bool:
    """``NON_ORDINARY`` from its parts: a day type other than ``ordinary``, or (``coupon_clause``) a coupon settlement."""

    if day_type != "ordinary":
        return True
    return coupon_clause and coupons is not None and float(coupons) > 0.0


def is_risk_date(
    values: Mapping[str, Optional[float]],
    definition: str,
    *,
    splits=None,
    coupon_clause: bool = True,
    reporting_on: Optional[date] = None,
) -> bool:
    """Whether the day whose panel row is ``values`` is a risk date under ``definition``.

    ``splits`` is the parsed ``metadata/evaluation_splits.json`` (``NON_ORDINARY`` reads the day type from it).
    ``coupon_clause`` applies to ``NON_ORDINARY`` only; ``SCHEDULED`` always counts a coupon settlement, as the judge does.
    ``reporting_on`` is the row's date: ``NON_ORDINARY`` then reads the reporting day type of that date (see the module note).

    Raises:
        ValueError: for an unknown definition, for ``NON_ORDINARY`` without ``splits``, for ``reporting_on`` with ``SCHEDULED``,
            or for a missing calendar column.
    """

    if reporting_on is not None and definition != NON_ORDINARY:
        raise ValueError(f"reporting_on reads the day type, which only {NON_ORDINARY!r} uses; got {definition!r}")
    if definition == SCHEDULED:
        return (
            float(values["quarter_end"] or 0.0) == 1.0
            or float(values["tax_date"] or 0.0) == 1.0
            or _coupon_settles(values)
        )
    if definition == NON_ORDINARY:
        if splits is None:
            raise ValueError("the non_ordinary definition reads the day type: pass the split declaration as splits=")
        kind = splits.day_type(values) if reporting_on is None else turn_days.reporting_day_type(splits, reporting_on, values)
        return non_ordinary_day(kind, values.get(COUPONS), coupon_clause)
    raise ValueError(f"unknown risk-date definition {definition!r}; use one of {DEFINITIONS}")


def not_risk_date_mask(
    rows: Sequence[Mapping[str, Optional[float]]],
    definition: str,
    *,
    splits=None,
    coupon_clause: bool = True,
) -> List[bool]:
    """``True`` for each row that is *not* a risk date under ``definition``: the ordinary-day population."""

    return [not is_risk_date(values, definition, splits=splits, coupon_clause=coupon_clause) for values in rows]
