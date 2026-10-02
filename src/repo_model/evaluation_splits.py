"""The declared evaluation splits: regime, and pressure-day type.

`CLAUDE.md` and `docs/decisions/pressure-probability.md` require every headline
result to be split by regime and by pressure-day type, and a pooled figure
alone is not a result. This module is where the two splits are read from their
declaration, `metadata/evaluation_splits.json`, and where a per-day series is
summarised over them.

**The declaration is a file, not a constant**, because both splits are
judgements about the data's meaning and are Eleonora's to make. The file says
whether it is provisional, and a record that used it carries its digest.

* **Pressure-day type** is a function of the scored day's calendar columns
  alone -- `quarter_end`, `tax_date` and `days_to_month_end` -- which the as-of
  rule reads at the scored day itself (they are always known). One type per
  day, by the declared precedence, so the types partition the scored days.
* **Regime** is a set of contiguous, non-overlapping date ranges, labelled.
* **The quarter-end window** (#140, decided in
  `docs/decisions/quarter-end-window.md`) is reported
  alongside the pressure-day types, not among them: a day is in it or outside
  it, read from its date by `data.quarter_end_window`. The declared types, their
  precedence and the file are unchanged, so no published split moves.

**The interval on a split is a domain estimate on whole-series resamples.**
The scored days of one type are not contiguous, and a block bootstrap run on
the subsequence would join days that were weeks apart into one block. So the
whole aligned series is resampled -- the same stationary bootstrap, the same
block length and the same seed as the pooled interval beside it -- and the
statistic is the mean over the resampled days that belong to the group. A
resample that draws no day of a group has no mean, and
`metrics.stationary_bootstrap_interval` raises rather than drop it; the split
then records the interval as unavailable, with that reason.

Standard library only, like the rest of `src/` outside `ml.py`.
"""

from __future__ import annotations

import hashlib
import json
import math
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any, Dict, Mapping, Optional, Sequence, Tuple

from .metrics import MetricError, stationary_bootstrap_interval

__all__ = [
    "DAY_TYPE_COLUMNS",
    "QUARTER_END_WINDOW_GROUPS",
    "SplitDeclaration",
    "load_split_declaration",
    "quarter_end_window_label",
    "split_summary",
]

#: The calendar columns a pressure-day type is read from.
DAY_TYPE_COLUMNS = ("days_to_month_end", "quarter_end", "tax_date")

#: The types, in precedence order. `ordinary` is every day that is none of the
#: others, so the types partition the scored days.
DAY_TYPES = ("quarter_end", "month_end", "tax_date", "ordinary")

#: The quarter-end window split, reported beside `DAY_TYPES`: every scored day
#: is in exactly one of the two groups.
QUARTER_END_WINDOW_GROUPS = ("quarter_end_window", "outside_quarter_end_window")


def quarter_end_window_label(when: date) -> str:
    """The day's group in the quarter-end window split, from its date alone.

    Raises:
        ValueError: if the market holiday table does not cover the windows
            around `when` (`data.quarter_end_window`).
    """

    from .data import quarter_end_window

    return QUARTER_END_WINDOW_GROUPS[0 if quarter_end_window(when) == 1.0 else 1]


@dataclass(frozen=True)
class SplitDeclaration:
    """`metadata/evaluation_splits.json`, parsed and checked."""

    month_end_window: int
    regimes: Tuple[Tuple[str, date, date], ...]
    status: str
    sha256: str
    path: str

    def day_type(self, values: Mapping[str, Optional[float]]) -> str:
        """The pressure-day type of a row, from its own calendar columns.

        Raises:
            ValueError: if a calendar column is absent or not observed. A
                calendar column is always known, so a hole is a data error.
        """

        read = {}
        for column in DAY_TYPE_COLUMNS:
            value = values.get(column)
            if value is None or not math.isfinite(float(value)):
                raise ValueError(
                    f"the row carries no {column!r}; a pressure-day type is read "
                    f"from the calendar columns, which are always known"
                )
            read[column] = float(value)
        if read["quarter_end"] == 1.0:
            return "quarter_end"
        if read["days_to_month_end"] <= self.month_end_window:
            return "month_end"
        if read["tax_date"] == 1.0:
            return "tax_date"
        return "ordinary"

    def regime(self, when: date) -> str:
        """The declared regime a date falls in.

        Raises:
            ValueError: if no declared range covers the date. A day outside
                every regime would drop out of the split silently.
        """

        for label, first, last in self.regimes:
            if first <= when <= last:
                return label
        raise ValueError(
            f"{when} falls in no regime declared in {self.path}; every scored "
            f"day must belong to one"
        )

    @property
    def regime_labels(self) -> Tuple[str, ...]:
        return tuple(label for label, _, _ in self.regimes)

    def document(self) -> dict:
        """What a record carries about the declaration it was split by."""

        return {
            "path": self.path,
            "sha256": self.sha256,
            "status": self.status,
            "month_end_window_days": self.month_end_window,
            "day_type_precedence": list(DAY_TYPES),
            "regimes": [
                {"label": label, "first": first.isoformat(), "last": last.isoformat()}
                for label, first, last in self.regimes
            ],
        }


def load_split_declaration(path: Path) -> SplitDeclaration:
    """Read and check the split declaration.

    Raises:
        ValueError: on a malformed file: a missing key, a window outside
            0..30, an empty or unlabelled regime, a range that ends before it
            starts, or ranges that are not ascending and disjoint.
    """

    raw = Path(path).read_bytes()
    try:
        document = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError(f"{path} is not JSON: {exc}") from exc
    if not isinstance(document, dict):
        raise ValueError(f"{path} must hold an object")
    for key in ("status", "day_types", "regimes"):
        if key not in document:
            raise ValueError(f"{path} declares no {key!r}")
    precedence = document["day_types"].get("precedence")
    if precedence != list(DAY_TYPES):
        raise ValueError(
            f"{path}: day_types.precedence must be {list(DAY_TYPES)}, the order "
            f"`SplitDeclaration.day_type` applies, got {precedence!r}"
        )
    window = document["day_types"].get("month_end_days_to_month_end_at_most")
    if isinstance(window, bool) or not isinstance(window, int) or not 0 <= window <= 30:
        raise ValueError(
            f"{path}: month_end_days_to_month_end_at_most must be an int in 0..30, "
            f"got {window!r}"
        )
    regimes = []
    for entry in document["regimes"]:
        label = entry.get("label")
        if not isinstance(label, str) or not label:
            raise ValueError(f"{path}: every regime needs a label, got {entry!r}")
        first = date.fromisoformat(entry["first"])
        last = date.fromisoformat(entry["last"])
        if last < first:
            raise ValueError(f"{path}: regime {label!r} ends before it starts")
        if regimes and first <= regimes[-1][2]:
            raise ValueError(
                f"{path}: regime {label!r} starts on or before the end of "
                f"{regimes[-1][0]!r}; regimes are ascending and disjoint"
            )
        regimes.append((label, first, last))
    if not regimes:
        raise ValueError(f"{path} declares no regime")
    if len({label for label, _, _ in regimes}) != len(regimes):
        raise ValueError(f"{path}: regime labels must be distinct")
    return SplitDeclaration(
        month_end_window=window,
        regimes=tuple(regimes),
        status=str(document["status"]),
        sha256=hashlib.sha256(raw).hexdigest(),
        path=str(path),
    )


def split_summary(
    labels: Sequence[str],
    series: Sequence[float],
    order: Sequence[str],
    *,
    block_length: int,
    seed: int,
    replications: int,
    level: float,
) -> Dict[str, Any]:
    """The mean of `series` over each group, with its domain bootstrap interval.

    Args:
        labels: one group label per position, aligned with `series`.
        series: the per-day values: a loss, or a paired loss difference.
        order: the groups to report, in order. A group with no day is reported
            with a count of zero and no mean.
        block_length, seed, replications, level: the pooled interval's, so
            the split and the pooled figure are drawn the same way.

    Raises:
        ValueError: if `labels` and `series` differ in length, or a label is
            not one of `order`.
    """

    if len(labels) != len(series):
        raise ValueError(
            f"{len(labels)} labels for {len(series)} values; they are aligned by "
            f"position"
        )
    unknown = sorted(set(labels) - set(order))
    if unknown:
        raise ValueError(f"labels {unknown} are not among the declared groups {list(order)}")
    values = [float(value) for value in series]
    out: Dict[str, Any] = {}
    for group in order:
        members = [position for position, label in enumerate(labels) if label == group]
        entry: Dict[str, Any] = {"count": len(members)}
        if members:
            entry["mean"] = sum(values[i] for i in members) / len(members)
            member = [label == group for label in labels]

            def statistic(indices: Sequence[int], member=member) -> float:
                drawn = [values[i] for i in indices if member[i]]
                return sum(drawn) / len(drawn) if drawn else math.nan

            try:
                lower, upper = stationary_bootstrap_interval(
                    statistic,
                    len(values),
                    block_length=block_length,
                    seed=seed,
                    replications=replications,
                    level=level,
                )
            except MetricError as exc:
                entry["interval_unavailable"] = str(exc)
            else:
                entry["interval"] = {"lower": lower, "upper": upper}
        out[group] = entry
    return out
