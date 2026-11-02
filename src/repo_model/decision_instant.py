"""The decision instant: one declared constant that every reader takes (#1312).

A forecast for scored day `T` is made at this wall-clock time, New York, on the last panel day before `T`
(`docs/decisions/information-set.md`). It was 16:00 until the amendment of 29 October 2026 (her ruling, relayed on
#1312, ledger item 77) moved it to 18:00. Every default, constant and declaration in `src/` that means "the decision
instant" reads `DECISION_TIME` from here and does not restate the clock; `tests/test_decision_instant_1312.py` fails
a module that types `time(16, 0)` for it again.

What this is not:

* It is not a source's own publication instant. `metadata/sources.json` states when a source publishes (H.15 at
  16:15, the secured rates' 15:00 conservative instant, ...); the as-of rule compares that to this constant.
  `DECLARED_AT_DECISION` lists the one declaration that is keyed on the decision instant itself and so must equal it.
* It is not rewritten into a record that was made at an earlier instant. A record, a study declaration or a captured
  file that states `16:00` is a record of that instant: it is labelled, not edited and not provisional (the
  amendment). `LEGACY_DECISION_TIME` names the earlier instant for the readers that must still accept such a record.

Standard library only.
"""

from __future__ import annotations

from datetime import time

__all__ = [
    "DECISION_TIME",
    "DECISION_TIME_TEXT",
    "DECISION_TIME_SECONDS_TEXT",
    "DECISION_TIMEZONE",
    "LEGACY_DECISION_TIME",
    "LEGACY_DECISION_TIME_TEXT",
]

#: The decision instant, wall clock, in `DECISION_TIMEZONE`.
DECISION_TIME = time(18, 0)
#: `HH:MM`, the form a record's `declaration.decision_time` and the CLI's `--decision-time` take.
DECISION_TIME_TEXT = DECISION_TIME.isoformat(timespec="minutes")
#: `HH:MM:SS`, the form the panel build and `metadata/funding_panel_manifest.json` take.
DECISION_TIME_SECONDS_TEXT = DECISION_TIME.isoformat(timespec="seconds")
DECISION_TIMEZONE = "America/New_York"

#: The instant every record made before the amendment of 29 October 2026 was made at. For readers of such records only.
LEGACY_DECISION_TIME = time(16, 0)
LEGACY_DECISION_TIME_TEXT = LEGACY_DECISION_TIME.isoformat(timespec="minutes")
