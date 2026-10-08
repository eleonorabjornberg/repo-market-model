"""Track H of #374 (#386): a hierarchical logistic of the pressure label.

The direct logistic on #128's scarcity-conditioned calendar design
(`scarcity_calendar`, the four-level state), with the spread and each scheduled
term given a deviation per scarcity regime (the four levels of #115's state),
partially pooled toward the pooled fit. #378's `scarcity_logistic_regime_pooled`
pools by a declared, fixed strength (`ml.REGIME_POOLING_SCALE`); here each fit
estimates it: the prior spread of the deviations is the value of
`ml.REGIME_SHRINKAGE_GRID` whose Laplace-approximated marginal likelihood is
greatest on that fit's own training pairs (empirical Bayes,
`ml._empirical_bayes_scale`). A regime with no training day is served the pooled
fit. numpy and scikit-learn only, in `ml.py`.

Declared in `metadata/pressure_judge.json` before any score. It declares no flag
cut-off: the judge chooses it at each refit from that refit's training window by
the declared `cutoff_rule` (#407). The state is
off in every published declaration and on for these runs only.

Standard library only, like the rest of `src/` outside `ml.py`.
"""

from __future__ import annotations

from typing import Tuple

from . import scarcity_calendar as sc

__all__ = ["CALIBRATION", "NAME", "STATE_FORM", "declaration_entry", "features_at_horizon"]

NAME = "hierarchical_logistic"

#: The state form it reads: #128's form (a), the four levels as #115 built them.
STATE_FORM = "four_level"

CALIBRATION = "recalibrated out of fold (pressure.recalibrated), as #128's forms were"


def features_at_horizon(horizon: int) -> Tuple[str, ...]:
    """#128's state-alone logistic features at `horizon` (the settlement leaves at h >= 2)."""

    return sc.features_at_horizon(f"logistic_{STATE_FORM}", horizon)


def declaration_entry() -> dict:
    """The candidate's entry in `metadata/pressure_judge.json`, as this module defines it."""

    return {
        "role": "candidate",
        "features": sorted(features_at_horizon(1)),
        "calibration": CALIBRATION,
    }
