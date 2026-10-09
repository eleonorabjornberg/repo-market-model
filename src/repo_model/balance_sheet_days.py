"""Balance-sheet days (#427, track B of #374): reporting dates banks manage their balance sheets to.

Three rules, each a function of the scored date alone and known in advance, each
cited to the public source that made it known. Declared before any score; the
window lengths are declared, not tuned.

* `foreign_bank_quarter_end`: the last `RUN_UP_DAYS` business days of March,
  June, September and December. Banks in end-period leverage-ratio regimes
  (the Basel Committee names France, Germany and Switzerland among them; the
  United States and United Kingdom use averages) are measured on the quarter-end
  snapshot, and reduce repo in the days before it. Basel III leverage ratio
  disclosure, quarterly, from 1 January 2015; the Basel Committee's statement of
  October 2018 names the behaviour.
* `foreign_bank_month_end`: the last business day of a month that is not a
  quarter-end. The same framework says some jurisdictions measure on month-end
  values. The weakest of the three: the source does not name which.
* `gsib_year_end`: the last `YEAR_END_DAYS` business days of December. The Board's
  surcharge rule (80 FR 49082, 14 August 2015; clarified in the Federal Register of 16 December 2016, 2016-29966) scores a
  global systemically important bank holding company on its FR Y-15 indicators
  as of 31 December.

A rule is usable only from the day its source was public (`public_from`);
`require_public` raises `LookAheadError` for a decision before it. Business days
are the market holiday table's, as for `data.quarter_end`.

Standard library only.
"""

from __future__ import annotations

from datetime import date
from typing import Dict, Mapping, NamedTuple, Tuple

from .data import (
    days_to_month_end,
    last_business_days_of_month,
    next_business_day,
    quarter_end,
    tax_date,
)
from .splits import LookAheadError

__all__ = ["RULES", "Rule", "RUN_UP_DAYS", "YEAR_END_DAYS", "flags", "require_public", "scored_day"]

#: Business days of the quarter-end run-up, the last business day included.
RUN_UP_DAYS = 3
#: Business days of the December window, the last business day included.
YEAR_END_DAYS = 5
#: How many business days past a decision's anchor row a scored day is searched for.
_SEARCH_DAYS = 12


class Rule(NamedTuple):
    name: str
    description: str
    public_from: date
    sources: Tuple[str, ...]


RULES: Tuple[Rule, ...] = (
    Rule(
        "foreign_bank_quarter_end",
        f"the last {RUN_UP_DAYS} business days of March, June, September, December: end-period leverage-ratio reporting",
        date(2014, 1, 12),
        (
            "https://www.bis.org/publ/bcbs270.pdf",  # Basel III leverage ratio framework and disclosure requirements, Jan 2014
            "https://www.bis.org/publ/bcbs_nl20.htm",  # Statement on leverage ratio window-dressing behaviour (read as evidence of the behaviour, not as the date)
        ),
    ),
    Rule(
        "foreign_bank_month_end",
        "the last business day of a month that is not a quarter-end: month-end leverage-ratio values in some jurisdictions",
        date(2014, 1, 12),
        ("https://www.bis.org/publ/bcbs270.pdf",),
    ),
    Rule(
        "gsib_year_end",
        f"the last {YEAR_END_DAYS} business days of December: G-SIB surcharge indicators are scored as of 31 December",
        date(2015, 8, 14),
        (
            "https://www.federalregister.gov/documents/2015/08/14/2015-18702/regulatory-capital-rules-implementation-of-risk-based-capital-surcharges-for-global-systemically",
            "https://www.govinfo.gov/content/pkg/FR-2016-12-16/pdf/2016-29966.pdf",
        ),
    ),
)

NAMES: Tuple[str, ...] = tuple(rule.name for rule in RULES)


def require_public(rule: Rule, decision: date) -> Rule:
    """`rule`, or `LookAheadError` if its source was not public at `decision`."""

    if decision < rule.public_from:
        raise LookAheadError(
            f"balance-sheet rule {rule.name} became public {rule.public_from}, after the decision on {decision}"
        )
    return rule


def _window(day: date, count: int) -> bool:
    return day in last_business_days_of_month(day.year, day.month, count)


def flags(day: date, decision: date) -> Dict[str, float]:
    """Each rule's 0/1 flag on scored `day`, for a decision made on `decision`."""

    for rule in RULES:
        require_public(rule, decision)
    quarter_month = day.month % 3 == 0
    last_day = _window(day, 1)
    return {
        "foreign_bank_quarter_end": 1.0 if quarter_month and _window(day, RUN_UP_DAYS) else 0.0,
        "foreign_bank_month_end": 1.0 if last_day and not quarter_month else 0.0,
        "gsib_year_end": 1.0 if day.month == 12 and _window(day, YEAR_END_DAYS) else 0.0,
    }


def scored_day(anchor: date, calendar: Mapping[str, float]) -> date:
    """The scored day, from its calendar columns and the anchor row's date.

    A direct model's feature row is dated at the anchor (`asof.InformationRule
    .observation`), while its calendar columns are the scored day's. The scored
    day is the one business day within `_SEARCH_DAYS` after the anchor whose
    `days_to_month_end`, `quarter_end` and `tax_date` are the row's. The three
    columns are the scored day's by construction, so no information is taken
    from outside the row; a row matching none, or two, is refused.
    """

    wanted = (float(calendar["days_to_month_end"]), float(calendar["quarter_end"]), float(calendar["tax_date"]))
    found = []
    day = anchor
    for _ in range(_SEARCH_DAYS):
        day = next_business_day(day, 1)
        if (days_to_month_end(day), quarter_end(day), tax_date(day)) == wanted:
            found.append(day)
    if len(found) != 1:
        raise ValueError(
            f"the calendar columns {wanted} match {len(found)} business days after {anchor}, not one"
        )
    return found[0]
