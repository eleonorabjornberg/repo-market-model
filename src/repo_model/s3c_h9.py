"""A richer target's walk-forward forecast as a continuous input of (s3c-ann-net) (H9 step 3 on the H5 candidate, #1345).

#842 and #932 asked the nested question of H9's kill clause ("no nested gain for H5") of `gbm_funding`, the candidate of the day. The candidate is now
(s3c-ann-net), a Huber fit of calendar and settlement terms on volatility-scaled mean reversion (`repo_model.spread_mr_state_calendar`), which takes
an extra term from a table (`StateArm.extra`, the `iorb` argument of `walk`). `TargetForecastTable` is that table for one target: the median of the
target's lead-h law (`repo_model.target_forecasts.median_of`, #706's walk), in the target's unit over a declared scale, for the target day h business
days after the decision day.

**Alignment.** The value at target row `row` for a lead-`lead` decision is the forecast made on decision row `row - lead` for that target row: the
direct pair of a label day, as `training_pairs="direct"` pairs the flags (the same pairing #932 ordered for the GBM, finding #915). A training pair reads
`at(lead, target_row)`; a forecast reads `read(lead, decision_index)`, the same value for the decision's own target row.

**Availability.** The forecast on decision day d is the walk's, made from a fit at or before d (`fit_dates`, rebuilt from the fold grid by
`target_forecasts.fit_decision_dates`); a value whose recorded fit is after its own decision day raises `LookAheadError`, a value with no recorded fit
too. A decision day on which the walk made no forecast (its first 61 labels, a lead with no law) serves `{}`: the fit centres the term on the pairs that
have it and gives a pair without it the value of its mean (`spread_mr_state_calendar.extra_value`), so a hole is neither a zero forecast nor another
day's forecast. Standard library only.
"""

from __future__ import annotations

from datetime import date
from typing import Dict, Mapping, Optional, Sequence

from . import spread_mr_state_calendar as sc
from .splits import LookAheadError

__all__ = ["TargetForecastTable", "UNITS"]

#: The scale each target's median is divided by before it enters the fit (the fit's own term scale is the volatility-scaled spread, so a term of order
#: 1 is a term of order one scale unit): the dispersions are in bp and stay so; ON RRP's daily change is in USD billions and is read in USD 100 bn,
#: like the settlement sizes (`spread_mr_state_calendar.SIZE_UNIT`).
UNITS: Mapping[str, float] = {"bgcr_dispersion_bps": 1.0, "sofr_dispersion_bps": 1.0, "on_rrp_change_bn": sc.SIZE_UNIT}


class TargetForecastTable:
    """One target's lead-h medians at every panel row, as `spread_mr_state_calendar.walk`'s `iorb` argument reads them.

    `medians[lead]` maps a decision day to the median of the target's law for the target day `lead` rows later (`None` or absent: no forecast), and
    `fit_dates[lead]` maps the same decision day to the decision day of the fit that made it.
    """

    def __init__(
        self,
        dates: Sequence[date],
        medians: Mapping[int, Mapping[date, Optional[float]]],
        fit_dates: Mapping[int, Mapping[date, date]],
        *,
        unit: float,
    ):
        if unit <= 0:
            raise ValueError(f"unit must be positive, got {unit}")
        self.dates = list(dates)
        self.unit = float(unit)
        self._medians = {lead: dict(found) for lead, found in medians.items()}
        self._fits = {lead: dict(found) for lead, found in fit_dates.items()}

    def _value(self, lead: int, decision_row: int) -> Dict[str, float]:
        """The forecast made on `decision_row` for the target row `lead` rows later, or `{}`.

        Raises:
            LookAheadError: the forecast has no recorded fit, or its fit is after its own decision day.

        Mutation record: see `tests/test_s3c_h9.py` (`TargetForecastTable._value`).
        """

        if decision_row < 0 or decision_row >= len(self.dates):
            return {}
        day = self.dates[decision_row]
        value = self._medians.get(lead, {}).get(day)
        if value is None:
            return {}
        fit = self._fits.get(lead, {}).get(day)
        if fit is None:
            raise LookAheadError(f"the lead-{lead} forecast for {day} has no recorded fit, so its instant is not known")
        if fit > day:
            raise LookAheadError(f"the lead-{lead} forecast for {day} comes from a fit made on {fit}, after its own decision instant")
        return {sc.H9_FORECAST: float(value) / self.unit}

    def at(self, lead: int, row: int) -> Dict[str, float]:
        """The term at target row `row` for a decision `lead` rows before (a training row); `{}` where there is no forecast."""

        return self._value(lead, row - lead)

    def read(self, lead: int, decision_index: int) -> Dict[str, float]:
        """The term a forecast of the decision on row `decision_index` at `lead` reads: that decision's own forecast for its target row.

        Raises:
            LookAheadError: see `_value`.
        """

        return self._value(lead, decision_index)
