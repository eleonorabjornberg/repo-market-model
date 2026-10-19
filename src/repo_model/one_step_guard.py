"""Refuse a calendar or scheduled regressor in a one-step pair (#947, Eleonora's ruling of 19 October 2026).

`asof` rule 2 serves the calendar columns (`contract.CALENDAR_FEATURES`) and every field a source declares in
`scheduled_availability` from the scored row `T` itself. A one-step fitter trains each target on the row before it:
row `p` against `spread(p + 1)`. A calendar or scheduled column therefore trains one row off from the row it is
served on (finding #914): the flag that marks a quarter-end learns the reversal the day *after* the turn.

`check_one_step_regressors` raises `ValueError` for such a column, naming it and the two fixes. The only exemptions are
the frozen declarations in `ONE_STEP_ALLOW_LIST`: records that must reproduce as they were made. A fit is exempt when its
fitter and its ordered regressors equal an entry's; there is no switch. `tests/test_one_step_guard.py` pins the list.

Stdlib only, like the rest of `src/` outside `ml.py`.
"""

from __future__ import annotations

import json
from pathlib import Path
from types import MappingProxyType
from typing import Dict, List, Mapping, NamedTuple, Optional, Sequence, Tuple

from .asof import _scheduled_blocks
from .contract import (
    CALENDAR_FEATURES,
    COMPOSED_FEATURES,
    DERIVED_FEATURES,
    FEATURE_FIELDS,
)

__all__ = [
    "FrozenDeclaration",
    "ONE_STEP_ALLOW_LIST",
    "check_one_step_regressors",
    "one_step_refusals",
]

_REGISTRY_PATHS = (
    Path(__file__).parents[2] / "metadata" / "sources.json",
    Path(__file__).parents[2] / "metadata" / "sources_measurement.json",
)


class FrozenDeclaration(NamedTuple):
    """One committed declaration that must reproduce, exempt from the guard."""

    fitter: str
    regressors: Tuple[str, ...]
    reason: str


#: The exemptions, by name. Pinned by `tests/test_one_step_guard.py`.
ONE_STEP_ALLOW_LIST: Mapping[str, FrozenDeclaration] = MappingProxyType({})


def _registry() -> Dict[str, Mapping[str, object]]:
    merged: Dict[str, Mapping[str, object]] = {}
    for path in _REGISTRY_PATHS:
        if path.exists():
            merged.update(json.loads(path.read_text(encoding="utf-8")))
    return merged


def _leaves(name: str, seen: Optional[set] = None) -> List[str]:
    """The calendar columns and source features a regressor is built from."""

    seen = set() if seen is None else seen
    if name in seen:
        return []
    seen.add(name)
    if name in DERIVED_FEATURES:
        parts: Sequence[str] = DERIVED_FEATURES[name]
    elif name in COMPOSED_FEATURES:
        parts = COMPOSED_FEATURES[name]
    else:
        return [name]
    return [leaf for part in parts for leaf in _leaves(part, seen)]


def one_step_refusals(
    regressors: Sequence[str],
    registry: Optional[Mapping[str, Mapping[str, object]]] = None,
) -> Dict[str, str]:
    """Each regressor read from row `T`, not `T - 1`, mapped to why."""

    scheduled = _scheduled_blocks(_registry() if registry is None else registry)
    found: Dict[str, str] = {}
    for name in regressors:
        for leaf in _leaves(str(name)):
            if leaf in CALENDAR_FEATURES:
                found[str(name)] = f"calendar column {leaf!r}"
                break
            pairs = [pair for pair in FEATURE_FIELDS.get(leaf, ()) if pair in scheduled]
            if pairs:
                source, field = pairs[0]
                found[str(name)] = f"scheduled field {source}.{field}"
                break
    return found


def check_one_step_regressors(
    fitter: str,
    regressors: Sequence[str],
    registry: Optional[Mapping[str, Mapping[str, object]]] = None,
) -> None:
    """Raise `ValueError` when a one-step fit is given a calendar or scheduled regressor.

    Exempt: a fit whose fitter and ordered regressors equal an `ONE_STEP_ALLOW_LIST` entry's.
    """

    names = tuple(str(name) for name in regressors)
    for entry in ONE_STEP_ALLOW_LIST.values():
        if entry.fitter == fitter and entry.regressors == names:
            return
    refused = one_step_refusals(names, registry)
    if not refused:
        return
    listed = "; ".join(f"{name!r} ({why})" for name, why in refused.items())
    raise ValueError(
        f"{fitter} trains on one-step pairs (row p against the spread of p + 1), but {listed} is served from the "
        f"scored row itself (asof rule 2), so it would be learned one row off the row it is served on (#914). "
        f"Train on direct (aligned) pairs (training_pairs='direct' where the fitter has it), or drop the column "
        f"from the regressors"
    )
