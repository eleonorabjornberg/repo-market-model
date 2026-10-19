"""Read the pressure-day type under the split declaration's window, for one process (#883, scratch measurement).

Put this directory on `PYTHONPATH` (after `src`) and set `MONTH_END_READING=window`: `SplitDeclaration.reporting_day_type` then returns
`SplitDeclaration.day_type`, so every caller that reports by the business-day reading reads the calendar-day window instead. With the
variable unset or `reporting` nothing changes. It edits no file in `src/` and is not imported by any code.
"""

import os

_reading = os.environ.get("MONTH_END_READING", "reporting")
if _reading not in ("reporting", "window"):
    # `site` prints and ignores an exception raised here, so a wrong setting would run unnoticed under the default.
    os.write(2, f"MONTH_END_READING must be 'reporting' or 'window'; got {_reading!r}\n".encode())
    os._exit(2)
if _reading == "window":
    from repo_model.evaluation_splits import SplitDeclaration

    def _window_reading(self, when, values):
        return self.day_type(values)

    SplitDeclaration.reporting_day_type = _window_reading
