"""The one declaration of the columns written about the target day (#1070, finding #1066).

`asof` rule 2 serves such a column from the scored row itself, so a one-step pair (row `p` against the spread of `p + 1`)
would learn it a row off (#914). `one_step_guard` and `scripts/provisional_register.py` read `TARGET_DAY_COLUMNS`; a later
column-adding module adds its names here, and `tests/test_one_step_guard.py` fails when a module writes a column that is
missing. The fields a source declares in `scheduled_availability` are the other half of the class and come from the
registry (`asof._scheduled_blocks`), not from here.

It lives outside `contract.py` because the final test's pre-registration freezes that file's bytes
(`scripts/final_test_preregistration.py`, `contract.py` with `"*"`). Stdlib only.
"""

from __future__ import annotations

from .balance_sheet_days import CODED_COLUMNS, TURN_COLUMNS
from .contract import CALENDAR_FEATURES
from .tax_date_october import COLUMN as OCTOBER_TAX_COLUMN

__all__ = [
    "BALANCE_SHEET_TARGET_DAY_COLUMNS",
    "DOM_TARGET_DAY_COLUMNS",
    "FOMC_TARGET_DAY_COLUMNS",
    "OCTOBER_TAX_TARGET_DAY_COLUMNS",
    "TARGET_DAY_COLUMNS",
]

#: The FOMC meeting columns of `fomc_calendar.add_columns` (#1038): read at the decision instant, written about the
#: target day, and not in `CALENDAR_FEATURES` (no published panel or declaration reads them).
FOMC_TARGET_DAY_COLUMNS = frozenset({"fomc_meeting_day", "fomc_days_to_next_meeting"})

#: The day-of-month bucket of `dom_calendar.add_columns` (#1032): a function of the date, read at the target day, and not in
#: `CALENDAR_FEATURES` (no published panel or declaration reads it; `dom_calendar.switched_on` serves it for one run).
DOM_TARGET_DAY_COLUMNS = frozenset({"dom_bucket"})

#: The balance-sheet flag columns of `balance_sheet_days.add_columns` (#1031): the as-coded rules and the same rules on the turn days. Each is a
#: function of the row's own date, so a forecast of that day reads it from its row; not in `CALENDAR_FEATURES` (no published panel reads them).
BALANCE_SHEET_TARGET_DAY_COLUMNS = frozenset(CODED_COLUMNS) | frozenset(TURN_COLUMNS)

#: The 15 October tax-date column of `tax_date_october.add_columns` (#1095, finding #1004): the 15th of October rolled off weekends and DC holidays, and the
#: two market days after it. A function of the row's own date, so a forecast of that day reads it from its row; not in `CALENDAR_FEATURES` (no published
#: panel reads it, and `tax_date` itself is unchanged).
OCTOBER_TAX_TARGET_DAY_COLUMNS = frozenset({OCTOBER_TAX_COLUMN})

TARGET_DAY_COLUMNS = (
    CALENDAR_FEATURES
    | FOMC_TARGET_DAY_COLUMNS
    | BALANCE_SHEET_TARGET_DAY_COLUMNS
    | DOM_TARGET_DAY_COLUMNS
    | OCTOBER_TAX_TARGET_DAY_COLUMNS
)
