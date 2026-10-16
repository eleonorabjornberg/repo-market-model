"""A richer target's walk-forward forecast as an input of H5's candidate (H9 step 3, #842).

H9's second kill reads "no nested gain for H5": does H5's candidate improve when it also reads a forecast of one of the
richer targets? The target forecasts are #706's walks (`scripts/richer_targets_706.py`), each made with a fit that used
only what was public at its own decision instant. This module puts one value of each on the panel, as a column the
as-of rule can read, and refuses a value whose fit came later than the decision it is read at.

**The form.** One value per target and lead: the median (level 0.5 of the protocol's 23-level grid) of the target's
lead-h law for the target day h business days after the decision day, in the target's own unit. A lead-h model reads its
own lead's column only. No other function of the law is declared.

**Availability.** The column on the row of decision day d is public at 16:00 ET on d, the decision instant of d: its
value is the forecast the walk made then (`metadata/sources_measurement.json`, `h9_target_forecasts`, zero lag). The
walk fits once per block of rows, at the decision instant of the block's first row (`asof.refit_blocks`), so the fit
that gave a row's forecast was made at that instant or earlier; `fit_decision_dates` records the instant and `attach`
refuses, with `LookAheadError`, a forecast whose fit is later than its own decision day or has no recorded fit.

**Off.** `COLUMN_FIELDS` is not part of `contract.FEATURE_FIELDS`. A track switches the columns on for its own run
(`switched_on`), as for `projected_reserves`. Standard library only, like the rest of `src/` outside `ml.py`.
"""

from __future__ import annotations

import contextlib
from datetime import date
from types import MappingProxyType
from typing import Dict, Iterator, List, Mapping, Optional, Sequence, Tuple

from . import contract
from .data import DailyObservation
from .lockbox import require_unlocked
from .scoring_protocol import GRID as _GRID
from .scoring_protocol import HORIZONS as _HORIZONS
from .splits import LookAheadError

__all__ = [
    "COLUMNS",
    "COLUMN_FIELDS",
    "GRID",
    "HORIZONS",
    "SOURCE_ID",
    "TARGETS",
    "attach",
    "column",
    "fit_decision_dates",
    "median_of",
    "switched_on",
]

#: The source the as-of rule reads the columns through (`metadata/sources_measurement.json`). Zero lag.
SOURCE_ID = "h9_target_forecasts"
#: The three targets #706 modelled (`metadata/richer_targets_706.json`, `choice.chosen`).
TARGETS: Tuple[str, ...] = ("bgcr_dispersion_bps", "on_rrp_change_bn", "sofr_dispersion_bps")
HORIZONS: Tuple[int, ...] = tuple(_HORIZONS)
GRID: Tuple[float, ...] = tuple(_GRID)
#: The level of the declared form.
MEDIAN_LEVEL = 0.5


def column(target: str, horizon: int) -> str:
    """The column that holds `target`'s lead-`horizon` forecast."""

    return f"h9fc_{target}_h{horizon}"


COLUMNS: Tuple[str, ...] = tuple(column(t, h) for t in TARGETS for h in HORIZONS)
#: Every column's source field, for the as-of rule. **Off**: a track switches them on.
COLUMN_FIELDS: Mapping[str, Tuple[Tuple[str, str], ...]] = {name: ((SOURCE_ID, name),) for name in COLUMNS}


@contextlib.contextmanager
def switched_on() -> Iterator[None]:
    """The columns in the feature map, for the duration of the block only."""

    fields, sources = contract.FEATURE_FIELDS, contract.FEATURE_SOURCES
    contract.FEATURE_FIELDS = MappingProxyType({**fields, **COLUMN_FIELDS})
    contract.FEATURE_SOURCES = MappingProxyType(
        {**sources, **{name: tuple(sorted({source for source, _field in pairs})) for name, pairs in COLUMN_FIELDS.items()}}
    )
    try:
        yield
    finally:
        contract.FEATURE_FIELDS, contract.FEATURE_SOURCES = fields, sources


def median_of(quantiles: Sequence[float], levels: Sequence[float] = GRID) -> float:
    """The law's value at level 0.5.

    Raises:
        ValueError: the law does not have one value per level, or the grid has no level 0.5.
    """

    if len(quantiles) != len(levels):
        raise ValueError(f"a law of {len(quantiles)} values is not on the {len(levels)} levels of the grid")
    matches = [i for i, level in enumerate(levels) if abs(level - MEDIAN_LEVEL) < 1e-9]
    if len(matches) != 1:
        raise ValueError("the grid has no level 0.5")
    return float(quantiles[matches[0]])


def fit_decision_dates(
    dates: Sequence[date], blocks: Sequence[Sequence[int]], *, horizon: int
) -> Dict[date, date]:
    """For each scored row, the decision day of the fit that forecast it, keyed by the row's own decision day.

    `blocks` are the scored rows' indices in refit blocks (`asof.refit_blocks`); a block is fitted at the decision
    instant of its first row. A scored row `s` is forecast from the decision of day `dates[s - horizon]`.
    """

    out: Dict[date, date] = {}
    for block in blocks:
        if not block:
            continue
        fitted = dates[block[0] - horizon]
        for index in block:
            out[dates[index - horizon]] = fitted
    return out


def attach(
    rows: Sequence[DailyObservation],
    forecasts: Mapping[date, Optional[Sequence[float]]],
    fit_dates: Mapping[date, date],
    *,
    target: str,
    horizon: int,
) -> List[DailyObservation]:
    """`rows` with the target's lead-`horizon` forecast on each decision row that has one.

    `forecasts` is keyed by decision day (a missing law is `None` and leaves a hole); `fit_dates` gives the decision
    day of the fit that made each.

    Raises:
        LookAheadError: a forecast has no recorded fit, its fit is after its own decision day, or its decision day
            or the target day it forecasts is in a locked tier.
        ValueError: the target or lead is not declared, or a forecast is for a day that is not on the panel.
    """

    if target not in TARGETS:
        raise ValueError(f"{target!r} is not a declared target")
    if horizon not in HORIZONS:
        raise ValueError(f"lead {horizon} is not declared")
    name = column(target, horizon)
    position = {row.date: index for index, row in enumerate(rows)}
    values: Dict[int, float] = {}
    for decision, law in forecasts.items():
        if decision not in position:
            raise ValueError(f"a forecast is for {decision}, which is not on the panel")
        if law is None:
            continue
        fit_date = fit_dates.get(decision)
        if fit_date is None:
            raise LookAheadError(f"the forecast for {decision} has no recorded fit, so its instant is not known")
        if fit_date > decision:
            raise LookAheadError(
                f"the forecast for {decision} comes from a fit made on {fit_date}, after its own decision instant"
            )
        index = position[decision]
        reached = position[decision] + horizon
        days = [decision] + ([rows[reached].date] if reached < len(rows) else [])
        require_unlocked(days, where="target_forecasts")
        values[index] = median_of(law)
    # every row carries the column: an absent column is an error to the fitter, a `None` is an unobserved value
    return [DailyObservation(row.date, {**row.values, name: values.get(i)}) for i, row in enumerate(rows)]
