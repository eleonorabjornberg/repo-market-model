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

from .contract import CALENDAR_FEATURES

__all__ = ["DOM_TARGET_DAY_COLUMNS", "FOMC_TARGET_DAY_COLUMNS", "TARGET_DAY_COLUMNS"]

#: The FOMC meeting columns of `fomc_calendar.add_columns` (#1038): read at the decision instant, written about the
#: target day, and not in `CALENDAR_FEATURES` (no published panel or declaration reads them).
FOMC_TARGET_DAY_COLUMNS = frozenset({"fomc_meeting_day", "fomc_days_to_next_meeting"})

#: The day-of-month bucket of `dom_calendar.add_columns` (#1032): a function of the date, read at the target day, and not in
#: `CALENDAR_FEATURES` (no published panel or declaration reads it; `dom_calendar.switched_on` serves it for one run).
DOM_TARGET_DAY_COLUMNS = frozenset({"dom_bucket"})

TARGET_DAY_COLUMNS = CALENDAR_FEATURES | FOMC_TARGET_DAY_COLUMNS | DOM_TARGET_DAY_COLUMNS
