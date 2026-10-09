"""Track B of #374 (#427): the best classifiers with balance-sheet days and FR 2004 positions.

Two candidates, each an existing declared classifier on its own design plus the
inputs of `balance_sheet_days` and the FR 2004 net Treasury position
(`dealer_treasury_position`, read as-of at its declared release):

* `balance_sheet_hierarchical_logistic`: track H's hierarchical logistic (#386),
  the best classifier on main under the judge when this was declared (#406);
* `balance_sheet_scarcity_gbm`: track S's monotone gradient-boosted classifier
  (#378), the other form of the same design.

The comparison for each is the same classifier without these inputs, which the
declaration already carries (`hierarchical_logistic`, `scarcity_gbm`). #413's
classifiers (track Q) were not on main when this was declared, and the net
Treasury settlement of track N (#426) was not either, so the interaction with
settlement is the gross scheduled settlement's, as in every other track. The
inputs are off in every published declaration and on for these runs only.

Standard library only, like the rest of `src/` outside `ml.py`.
"""

from __future__ import annotations

from typing import Dict, Tuple

from . import scarcity_calendar as sc

__all__ = ["CANDIDATES", "CALIBRATION", "POSITION", "declaration_entry", "features_at_horizon"]

POSITION = "dealer_treasury_position"
CALIBRATION = "recalibrated out of fold (pressure.recalibrated), as #128's forms were"

#: candidate name -> (the scarcity_calendar candidate whose features it extends, the model form)
CANDIDATES: Dict[str, Tuple[str, str]] = {
    "balance_sheet_hierarchical_logistic": ("logistic_four_level", "hierarchical"),
    "balance_sheet_scarcity_gbm": ("gbm_four_level", "gbm"),
}


def features_at_horizon(name: str, horizon: int) -> Tuple[str, ...]:
    """The base classifier's features at `horizon`, plus the FR 2004 position."""

    return sc.features_at_horizon(CANDIDATES[name][0], horizon) + (POSITION,)


def declaration_entry(name: str) -> dict:
    """The candidate's entry in `metadata/pressure_judge.json`, as this module defines it."""

    return {
        "role": "candidate",
        "track": "B (#427)",
        "features": sorted(features_at_horizon(name, 1)),
        "calibration": CALIBRATION,
    }
