"""Track S of #374 (#378): the scarcity-conditioned calendar scored under the event bar.

#128's two forms (the direct logistic and the direct gradient-boosted
classifier on the scarcity-conditioned calendar, `scarcity_calendar`) are
re-scored by the pressure-day judge (`pressure_judge`, #375), with two variants
added. Everything here was committed before the first score:
`metadata/pressure_judge.json` carries each candidate's features, calibration
step, and a test pins them to this module.

**The five candidates**, by `CANDIDATES`:

* `scarcity_logistic` and `scarcity_gbm`: #128's primary forms as they are
  (state form (a), four levels, the state alone: no scarcity measures).
* `scarcity_logistic_interactions` and `scarcity_gbm_interactions`: the same
  forms with the scheduled Treasury settlement's size crossed with the state
  and with the quarter-end and with the tax date (settlement x state x
  quarter-end, settlement x state x tax date), the September 2019 pattern.
  The settlement is public one business day ahead, so at horizons of 2 or more
  it is not a feature (`scarcity_calendar.features_at_horizon`) and the variant
  is the base form there: the same probabilities, scored under both names.
* `scarcity_logistic_regime_pooled`: the logistic with the spread and each
  scheduled term given a deviation per scarcity regime (the four levels of
  #115's state), partially pooled toward the pooled fit (`ml.REGIME_POOLING_SCALE`:
  the deviations carry four times the pooled columns' penalty). A regime with no
  training day is served the pooled fit. The gbm has no pooled variant: it
  already splits on the state.

All five are recalibrated out of fold (`pressure.recalibrated`) as #128's
forms were. The state is #115's, with its merged cut-points, read as-of; it is
off in every published declaration and switched on for these runs only.

The flagging cut-off is not declared here: the judge chooses it at each refit
and horizon from the refit's training window alone (`pressure_judge.cutoff_rule`,
#407), for these candidates as for every other.

Standard library only, like the rest of `src/` outside `ml.py`.
"""

from __future__ import annotations

from types import MappingProxyType
from typing import Mapping, NamedTuple, Tuple

from . import scarcity_calendar as sc

__all__ = [
    "CALIBRATION",
    "CANDIDATES",
    "Candidate",
    "STATE_FORM",
    "candidate",
    "declaration_entry",
    "features_at_horizon",
]

#: The state form every candidate reads: #128's form (a), the four levels as #115 built them.
STATE_FORM = "four_level"

CALIBRATION = "recalibrated out of fold (pressure.recalibrated), as #128's forms were"


class Candidate(NamedTuple):
    """One candidate: its name, #128 form, and variant."""

    name: str
    form: str
    variant: str


#: Every candidate, #128's two forms first.
CANDIDATES: Tuple[Candidate, ...] = (
    Candidate("scarcity_logistic", "logistic", "base"),
    Candidate("scarcity_gbm", "gbm", "base"),
    Candidate("scarcity_logistic_interactions", "logistic", "interactions"),
    Candidate("scarcity_gbm_interactions", "gbm", "interactions"),
    Candidate("scarcity_logistic_regime_pooled", "logistic", "regime_pooled"),
)

_BY_NAME: Mapping[str, Candidate] = MappingProxyType({c.name: c for c in CANDIDATES})


def candidate(name: str) -> Candidate:
    """The candidate called `name`.

    Raises:
        ValueError: if there is none.
    """

    try:
        return _BY_NAME[name]
    except KeyError:
        raise ValueError(f"unknown candidate {name!r}; the candidates are {sorted(_BY_NAME)}") from None


def features_at_horizon(name: str, horizon: int) -> Tuple[str, ...]:
    """The features of candidate `name` at `horizon`: #128's state-alone design."""

    entry = candidate(name)
    return sc.features_at_horizon(f"{entry.form}_{STATE_FORM}", horizon)


def declaration_entry(name: str) -> dict:
    """The candidate's entry in `metadata/pressure_judge.json`, as this module defines it."""

    return {
        "role": "candidate",
        "features": sorted(features_at_horizon(name, 1)),
        "calibration": CALIBRATION,
    }
