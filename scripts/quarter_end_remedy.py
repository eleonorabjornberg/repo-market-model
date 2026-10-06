"""Quarter-end remedies layered on pressure model v2 (#327), reported only.

v2 ships without a quarter-end term (PR #252: the declared rule's choice), and its 50% band covers about
30% of quarter-end days. The trees cannot learn the turn from 23 days (#252), so every remedy here is a
turn layer on v2's own vectors, estimated across every earlier quarter-end, with no trees. A remedy changes
quarter-end days only. It does not change v2 or any published record; whether it joins v2 is Eleonora's
decision (the "Publish?" issue of #327).

Declared in one commit before anything was scored (`CANDIDATES`, `SELECTION`, the blocks). The choice is
made on the inner block, 2018-06-29 to 2022-12-31, and committed as `CHOSEN_REMEDY` before 2023-2025 is
read. No day after 2025-12-31 is read (`docs/decisions/lockbox.md`): `require_read_window` refuses one.

Three subcommands, each writing JSON:

    PYTHONPATH=src python3 scripts/quarter_end_remedy.py diagnose --panel PUB.csv --output OUT/diagnosis.json
    PYTHONPATH=src python3 scripts/quarter_end_remedy.py choose   --panel PUB.csv --output OUT/choice.json
    PYTHONPATH=src python3 scripts/quarter_end_remedy.py report   --panel PUB.csv --output OUT/report.json

`PUB.csv` is the published panel (`docs/pivot/next-session.md`); the script reads v2's per-day vectors from
`docs/runs/pressure_model_v2_distribution_h1.json` through 2025-12-31 and no later row. The script needs
nothing beyond the standard library and `repo_model`.
"""

from __future__ import annotations

import argparse
import json
import statistics
import sys
from datetime import date
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))

from repo_model import interior, onset  # noqa: E402
from repo_model.baseline import _split_labels, panel_sha256  # noqa: E402
from repo_model.data import audit_panel, load_daily_panel  # noqa: E402
from repo_model.evaluation_splits import load_split_declaration  # noqa: E402
from repo_model.metrics import crps_from_quantiles  # noqa: E402
from repo_model.splits import LookAheadError  # noqa: E402

LEVELS = (0.05, 0.25, 0.5, 0.75, 0.95)
RECORD = REPO / "docs" / "runs" / "pressure_model_v2_distribution_h1.json"
SPLITS = REPO / "metadata" / "evaluation_splits.json"
BLOCK_LENGTH = 2  # the stationary bootstrap's mean block length, as the final test and #244
MINIMUM_CELL = 20  # a cell under this has no interval: "too few days" (ruling of 6 October 2026)

#: The blocks. The choice reads the inner block only; the outer block is a labelled look, read after the
#: choice is committed. The lockbox's near-blind tier starts on 2026-01-01.
INNER = (date(2018, 6, 29), date(2022, 12, 31))
OUTER = (date(2023, 1, 1), date(2025, 12, 31))
LAST_READ = date(2025, 12, 31)

#: Declared before scoring. A remedy moves a quarter-end day's vector by an estimate from the quarter-ends
#: whose labels were public at that day's anchor. `MIN_PAST` is the fewest past quarter-ends an estimate
#: needs (one year); with fewer the vector is v2's. `POOL_WEIGHT` is the pseudo-count with which the
#: month-end median is pooled into the quarter-end one.
MIN_PAST = 4
MIN_PAST_EMPIRICAL = 8
POOL_MIN_MONTH_ENDS = 8
POOL_WEIGHT = 4

CANDIDATES = {
    "base": {"what": "v2 as it stands, with no quarter-end remedy", "complexity": 0},
    "qe_shift": {
        "what": ("a location shift: every quantile moves by the median of (y - q50) over the earlier "
                 "quarter-ends"),
        "complexity": 1},
    "turn_pool": {
        "what": ("the shift pooled with the month-end turns: (n_q * median_qe + k * median_me) / (n_q + k) with "
                 f"k = {POOL_WEIGHT}, where median_me is the median of (y - q50) over earlier month-end days "
                 "(not quarter-ends), a size term for the quarter-end's excess"),
        "complexity": 2},
    "qe_shift_width": {
        "what": ("the shift, and a widening of the band about the shifted median by max(1, median |e - shift| / "
                 "median half-IQR) over the earlier quarter-ends, e = y - q50 and half-IQR = (q75 - q25) / 2, "
                 "the factor that would have made the earlier quarter-ends' 50% band right"),
        "complexity": 2},
    "qe_empirical": {
        "what": ("a separate small quarter-end model: every level is v2's q50 plus the empirical quantile, at that "
                 "level, of the earlier quarter-ends' (y - q50), once there are 8"),
        "complexity": 5},
}

#: A remedy that needs a new panel column is a new panel digest, so it is declared and not built.
NOT_BUILT = {
    "days_to_quarter_end_market_calendar": (
        "'days to quarter-end on the market calendar' as a panel column of its own (`metadata/market_holidays.json`) "
        "is a new calendar column in `data.py` and `contract.py` and a new panel digest, which is her decision; "
        "`quarter_end` and `days_to_month_end` are the calendar's columns today"),
}

SELECTION = {
    "window": "2018-06-29 to 2022-12-31 (`INNER`), h = 1",
    "rule": ("every candidate is v2 with one remedy on quarter-end days, so only those days differ from `base`. "
             "The candidate with the lowest pooled inner CRPS among the eligible leads; a simpler eligible "
             "candidate (fewer estimated quantities: `complexity`) is chosen instead when the 90% interval "
             "of its paired CRPS difference against the leader includes 0"),
    "eligible": ("the paired CRPS gain over `base` on the inner block is above 0, and the remedy changed no day "
                 "that is not a quarter-end"),
    "none_eligible": "`base` is chosen: no remedy is adopted, and the look at 2023-2025 reports every candidate",
    "interval": "stationary bootstrap, mean block length 2, 90%",
    "cells": ("quarter-end, year-end, tax-date, month-end and ordinary cells are reported, with an interval "
              f"only from {MINIMUM_CELL} days ('too few days' below)"),
    "outer": ("2023-2025 is read once after the choice is committed as `CHOSEN_REMEDY`, and labelled a look: "
              "the inner block chose, the outer block did not"),
}

#: The remedy the inner block chose (`choose`), committed before 2023-2025 is read. None until the choice is run.
CHOSEN_REMEDY = None

LOOK_LABEL = ("a labelled look at 2023-2025: the remedy was chosen on 2018-2022 and these days chose nothing, "
              "but 2023-2025 was read by every earlier look at v2 and by the diagnosis, so the figures are "
              "exploratory (selection-adjusted uncertainty not computed). Only a live record can show that a "
              "remedy is better")


# ---------------------------------------------------------------------------
# The layer
# ---------------------------------------------------------------------------


def require_read_window(end) -> None:
    """Refuse any day after `LAST_READ`: the lockbox holds those days back from every comparison."""

    if end > LAST_READ:
        raise ValueError(f"{end} is after {LAST_READ}: those days are locked (docs/decisions/lockbox.md)")


def _median(values):
    return statistics.median(values)


def _quantile(values, level):
    """The linear-interpolation (type 7) quantile of `values`."""

    ordered = sorted(values)
    position = level * (len(ordered) - 1)
    low = int(position)
    high = min(low + 1, len(ordered) - 1)
    return ordered[low] + (position - low) * (ordered[high] - ordered[low])


def _residual(day):
    return day["y"] - day["v2"][2]


def _adjusted(day, past, name):
    """`day`'s vector under remedy `name`, from `past`: earlier days whose labels were public at `day`'s anchor.

    Raises:
        LookAheadError: if a past day's label was not public at the anchor.
    """

    for earlier in past:
        if earlier["date"] > day["anchor"]:
            raise LookAheadError(f"{earlier['date']}'s label was not public at the anchor {day['anchor']}")
    vector = list(day["v2"])
    if name == "base" or day["type"] != "quarter_end":
        return vector
    quarter = [_residual(p) for p in past if p["type"] == "quarter_end"]
    if name == "qe_empirical":
        if len(quarter) < MIN_PAST_EMPIRICAL:
            return vector
        return _empirical(vector[2], quarter)
    if len(quarter) < MIN_PAST:
        return vector
    shift = _median(quarter)
    if name == "qe_shift":
        return [q + shift for q in vector]
    if name == "turn_pool":
        month = [_residual(p) for p in past if p["type"] == "month_end"]
        if len(month) < POOL_MIN_MONTH_ENDS:
            return vector
        n = len(quarter)
        shift = (n * shift + POOL_WEIGHT * _median(month)) / (n + POOL_WEIGHT)
        return [q + shift for q in vector]
    if name == "qe_shift_width":
        halves = [(p["v2"][3] - p["v2"][1]) / 2.0 for p in past if p["type"] == "quarter_end"]
        denominator = _median(halves)
        scale = max(1.0, _median([abs(e - shift) for e in quarter]) / denominator) if denominator > 0 else 1.0
        centre = vector[2]
        return [centre + shift + scale * (q - centre) for q in vector]
    raise ValueError(f"unknown remedy {name!r}")


def _empirical(centre, residuals):
    return [centre + _quantile(residuals, level) for level in LEVELS]


def walk(days, name):
    """Every day's vector under remedy `name`, in date order: each from the days its anchor had public.

    `days` carry `date`, `anchor`, `y`, `v2` (v2's vector), `type` (the pressure-day type). The estimate for a
    day reads v2's vectors for the earlier days, never an earlier remedied vector.
    """

    if name not in CANDIDATES:
        raise ValueError(f"unknown remedy {name!r}")
    out = []
    for k, day in enumerate(days):
        past = [p for p in days[:k] if p["date"] <= day["anchor"]]
        out.append(_adjusted(day, past, name))
    return out
