"""The settlement-timing probit and quantile regression (#379, track S-T of #374).

The closest published method to this project's question: Copeland, Duffie & Yang
(NY Fed SR 974) and Ferris, Rose & Tase (FEDS Note, July 2025) model SOFR - IORB with
a quantile regression and a probit, driven by the timing and size of payments and
settlements. Adrian, Boyarchenko & Giannone (2019) turn a grid of predicted quantiles
into a smooth conditional distribution by fitting a skewed t to it. This module only
*declares* the candidates: which estimator on which inputs. The estimators are
`ml._settlement_timing_predictor`'s, the cut-offs and the bar are
`metadata/pressure_judge.json`'s, and `scripts/settlement_timing.py` runs them.

**Six candidates, two estimators on three nested sets of inputs**

* `probit`: a ridge probit of `spread > tau` at +5 and +10 bp, fitted per threshold
  (`ml.PRESSURE_PROBIT_SETTINGS`).
* `quantile_skewt`: linear quantile regressions of the spread on a 13-quantile grid
  (`ml.PRESSURE_QUANTILE_SKEWT_SETTINGS`), smoothed per day into an Azzalini-Capitanio
  skew-t, from which the exceedance at each threshold is read.

and the inputs, each set contained in the next:

* `timing`: the latest public spread, Treasury settlement size (`treasury_settlement`,
  and its coupon part, `treasury_settlement_coupons`) and the calendar timing (days to
  month end, quarter-end, tax date).
* `scarcity`: `timing` plus the reserve-scarcity state. The design (`ml._PressureDesign`)
  reads the reserves (`reserve_balances`) in USD trillions and multiplies each
  scheduled term (the pressure-day types and the settlements) by it, so a scheduled
  date counts for little when reserves are abundant; it adds #115's state
  (`reserve_scarcity_state`, 0 to 3) as a level, and the TGA (`tga`) as its change over
  the design's window and that change times reserves.
* `tga`: `scarcity` plus track D's daily TGA balance and its change (`tga_daily`,
  `tga_daily_change`, #377), read as of the decision instant at the lag of their own source
  (`metadata/sources_measurement.json`). They are measurement fields, off in every
  published declaration.

A settlement amount is public one business day ahead (`treasury_auctions`), so, as
pressure model v1 does, the two settlement columns leave the inputs at horizons of 2 or
more, and with them their terms times reserves.

Standard library only, like the rest of `src/` outside `ml.py`.
"""

from __future__ import annotations

from typing import NamedTuple, Tuple

__all__ = ["CANDIDATES", "Candidate", "FORMS", "INPUT_SETS", "candidate", "features_at_horizon"]

SETTLEMENTS = ("treasury_settlement", "treasury_settlement_coupons")
CALENDAR = ("days_to_month_end", "quarter_end", "tax_date")

#: The three nested input sets, by name.
INPUT_SETS = {
    "timing": ("spread_bps",) + SETTLEMENTS + CALENDAR,
    "scarcity": ("spread_bps",) + SETTLEMENTS + CALENDAR + ("reserve_balances", "reserve_scarcity_state", "tga"),
    "tga": (
        ("spread_bps",) + SETTLEMENTS + CALENDAR
        + ("reserve_balances", "reserve_scarcity_state", "tga", "tga_daily", "tga_daily_change")
    ),
}

#: The two estimators, by the name `ml.SETTLEMENT_TIMING_KINDS` gives each.
FORMS = {"probit": "probit", "quantile": "quantile_skewt"}


class Candidate(NamedTuple):
    name: str
    form: str
    inputs: str


CANDIDATES: Tuple[Candidate, ...] = tuple(
    Candidate(f"settlement_{form}_{inputs}", form, inputs)
    for form in ("probit", "quantile")
    for inputs in ("timing", "scarcity", "tga")
)


def candidate(name: str) -> Candidate:
    for entry in CANDIDATES:
        if entry.name == name:
            return entry
    raise ValueError(f"unknown settlement-timing candidate {name!r}")


def features_at_horizon(name: str, horizon: int) -> Tuple[str, ...]:
    """The declared features of candidate `name` at `horizon`.

    Raises:
        ValueError: on an unknown candidate or a horizon below 1.
    """

    entry = candidate(name)
    if horizon < 1:
        raise ValueError(f"a horizon is a positive number of business days, got {horizon}")
    return tuple(
        column for column in INPUT_SETS[entry.inputs] if horizon == 1 or column not in SETTLEMENTS
    )
