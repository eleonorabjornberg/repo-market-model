"""The scarcity-conditioned calendar (#128): its forms, state mappings and win rule, fixed before scoring.

Eleonora's request of 2 October 2026 on #128: pressure days come almost
entirely from two scarce-reserve stretches (2018-19 and 2025), while 2021-23 had
almost none. A quarter-end only bites when reserves are scarce. So the
scheduled-pressure terms enter the model *through* the reserve-scarcity state
(#115), not alongside it, and the calm years teach "scheduled pressure +
abundant reserves = no pressure". Everything in this module was committed
before the first scoring run.

**The structure** (`ml.scarcity_calendar_exceedance`), one design read by two
estimators, both direct models of the label `spread > tau` (#114):

* the latest spread public at the decision (`spread_bps`), linearly;
* the reserve-scarcity state, as #115 built it with its merged cut-points
  (`scarcity.SATIATION_BAND`, `scarcity.ON_RRP_BUFFER_BN`; not refitted here),
  read as-of and mapped by the state form (`STATE_FORMS`), linearly;
* with the scarcity measures (`SCARCITY_MEASURES`), each linearly;
* each scheduled-pressure term (`SCHEDULED_TERMS`) **times the mapped state,
  and never on its own**: the scored day's pressure-day type as the split
  declaration defines it (quarter-end, month-end, tax date), and the scheduled
  Treasury settlement size, in USD billions. No scheduled term has a main
  effect, so a quarter-end with the state at 0 adds nothing.

The two forms (`FORMS`):

* `logistic`: the direct logistic of #114 (`ml.PRESSURE_LOGISTIC_SETTINGS`)
  on that design, so its scheduled terms are calendar x state interactions.
* `gbm`: the direct gradient-boosted classifier of #114
  (`ml.PRESSURE_CLASSIFIER_SETTINGS`) on the same design, with scikit-learn's
  monotone constraints (`monotonic_cst`, already in the pinned version, so no
  new package): non-decreasing in the state and in each scheduled term x
  state, so the probability never falls as scarcity rises. The spread and the
  scarcity measures are unconstrained.

Both are recalibrated out of fold (`pressure.recalibrated`), as the control is.

**The state forms** (`STATE_FORMS`), declared with a test pinning each mapping
(Eleonora's scope addition of 2 October 2026 on #128):

* `four_level`: (a), the four-level state as #115 built it, 0 (abundant) to 3
  (scarce), used as is.
* `two_level`: (b), states 0-1 against states 2-3. **(b) was added after
  seeing #157**, where the pressure-day frequency was higher in state 2 than
  in state 3. It is therefore not a blind specification, and every report of
  its result says so.

**The scarcity measures** (`SCARCITY_MEASURES`, item 2 of the directive): #88's
buffer-conditional input (`on_rrp_depleted`, `reserves_when_depleted`) and
#98's EFFR - IORB (`effr_minus_iorb_bp`), the conditional inputs on `main` when
this directive branched. Each form is reported with the state alone and with
them.

**The control** (Eleonora's ruling of 3 October 2026 on #128): pressure model
v1.1 if #117 passed its win rule, else v1. PR #204 (merged) reports that #117
passed its win rule by the letter of the rule, with no gain over v1; so the
control is v1.1, v1 with all five #117 inputs together
(`scripts/pressure_v1_1.py`'s `joint` run). Whether that pass counts is asked
in #205. v1 is therefore also reported as an exploratory comparison, so an
answer either way needs no re-run.

**The win rule** (Eleonora's rulings of 3 October 2026 on #128), fixed before
scoring:

1. *Primary comparisons* (`PRIMARY_CELLS`, the only ones that decide): each
   form with the state alone, +5 bp, horizon 1, on all scored days and on
   onset days, each paired against the control and against the
   persistence-logistic. Two forms x four cells = eight cells. "The state
   alone" is the state as #115 built it, form (a): (b) is not blind, and the
   ruling names one primary candidate per form. Onset days are #139's onset
   group, as #209 amended it (`onset.day_groups`): every day after five calm
   panel days, whatever its outcome, with the onsets as its events.
2. *Test*: one-sided paired stationary-bootstrap p-values
   (`ml.paired_bootstrap_p_values`, `P_VALUE_REPLICATIONS`, as #187), Holm at a
   `FAMILY_LEVEL` family-wise level over the eight primary cells together, for
   improvement and, separately, for deterioration.
3. *Pass*, per form: at least one of its primary cells survives Holm as an
   improvement, and none of its primary cells survives as a deterioration
   (`classify_primary`).
4. *Exploratory, deciding nothing*: form (b), the variants with the scarcity
   measures, +10 bp, horizons 2-5, calendar climatology, v1, CRPS, the splits,
   CORP, precision-recall, lead time, the small-leap targets, the 2021-23
   regime check and October 2025. Reported in full.

Standard library only, like the rest of `src/` outside `ml.py`.
"""

from __future__ import annotations

import hashlib
from types import MappingProxyType
from typing import Mapping, NamedTuple, Tuple

from .dvp_segment import holm

__all__ = [
    "BENCHMARKS",
    "CANDIDATES",
    "CONTROL",
    "Candidate",
    "FAMILY_LEVEL",
    "FORMS",
    "PRIMARY_CANDIDATES",
    "PRIMARY_CELLS",
    "P_VALUE_REPLICATIONS",
    "REGIME_CHECK_YEARS",
    "SCARCITY_MEASURES",
    "SCHEDULED_TERMS",
    "STATE_COLUMN",
    "STATE_FORMS",
    "candidate",
    "classify_primary",
    "features_at_horizon",
    "p_value_seed",
    "primary_key",
]

#: The panel column the state is read from (`scarcity.RESERVE_SCARCITY_STATE`).
STATE_COLUMN = "reserve_scarcity_state"

#: The two state forms: #115's level -> the level the design reads.
#: (b), `two_level`, was added after seeing #157 (module docstring): not blind.
STATE_FORMS: Mapping[str, Mapping[float, float]] = MappingProxyType(
    {
        "four_level": MappingProxyType({0.0: 0.0, 1.0: 1.0, 2.0: 2.0, 3.0: 3.0}),
        "two_level": MappingProxyType({0.0: 0.0, 1.0: 0.0, 2.0: 1.0, 3.0: 1.0}),
    }
)

#: The two estimators on the one design.
FORMS: Tuple[str, ...] = ("logistic", "gbm")

#: The scheduled-pressure terms, each entering only times the state. The three
#: day types are read from the calendar columns through the split declaration.
SCHEDULED_TERMS: Tuple[str, ...] = ("quarter_end", "month_end", "tax_date", "treasury_settlement")

#: The calendar columns the day type is read from, and the settlement column.
_CALENDAR_COLUMNS: Tuple[str, ...] = ("days_to_month_end", "quarter_end", "tax_date")
_SETTLEMENT = "treasury_settlement"

#: #88's buffer-conditional input and #98's EFFR - IORB: the scarcity measures.
SCARCITY_MEASURES: Tuple[str, ...] = ("on_rrp_depleted", "reserves_when_depleted", "effr_minus_iorb_bp")


class Candidate(NamedTuple):
    """One scored candidate: its form, its state form, and whether it reads the measures."""

    name: str
    form: str
    state: str
    measures: bool


def _candidate_name(form: str, state: str, measures: bool) -> str:
    return f"{form}_{state}" + ("_measures" if measures else "")


#: Every candidate, primary first: two forms x two state forms x with or without the measures.
CANDIDATES: Tuple[Candidate, ...] = tuple(
    Candidate(_candidate_name(form, state, measures), form, state, measures)
    for measures in (False, True)
    for state in ("four_level", "two_level")
    for form in FORMS
)

#: One primary candidate per form: the state alone, form (a).
PRIMARY_CANDIDATES: Tuple[str, ...] = tuple(_candidate_name(form, "four_level", False) for form in FORMS)

#: The control, by the 3 October ruling and #117's outcome (module docstring).
CONTROL = "pressure_model_v1_1"
#: The benchmark names the primary cells pair against.
BENCHMARKS: Tuple[str, ...] = (CONTROL, "persistence_logistic")

FAMILY_LEVEL = 0.10
P_VALUE_REPLICATIONS = 20000
POOLED = "all_days"
ONSET = "onset_days"

#: `(candidate, day set, tau, horizon, benchmark)`: the only cells that decide.
PRIMARY_CELLS: Tuple[Tuple[str, str, float, int, str], ...] = tuple(
    (name, day_set, 5.0, 1, bench)
    for name in PRIMARY_CANDIDATES
    for day_set in (POOLED, ONSET)
    for bench in BENCHMARKS
)

#: The regime check (item 4): quarter-ends of these years, where the calendar
#: fired and reserves were abundant.
REGIME_CHECK_YEARS: Tuple[int, ...] = (2021, 2022, 2023)


def candidate(name: str) -> Candidate:
    """The candidate called `name`."""

    for entry in CANDIDATES:
        if entry.name == name:
            return entry
    raise ValueError(f"unknown candidate {name!r}")


def features_at_horizon(name: str, horizon: int) -> Tuple[str, ...]:
    """The declared features of candidate `name` at `horizon`.

    The scheduled settlement is public one business day ahead
    (`metadata/sources.json`, `treasury_auctions`), so, as pressure model v1
    drops `treasury_settlement` at horizons of 2 or more, it leaves there, and
    with it its term x state.
    """

    entry = candidate(name)
    if horizon < 1:
        raise ValueError(f"a horizon is a positive number of business days, got {horizon}")
    features = ("spread_bps", STATE_COLUMN) + _CALENDAR_COLUMNS
    if horizon == 1:
        features += (_SETTLEMENT,)
    if entry.measures:
        features += SCARCITY_MEASURES
    return features


def primary_key(name: str, day_set: str, tau: float, horizon: int, benchmark: str) -> str:
    """One comparison's name: `candidate|brier|day set|tau|h|benchmark`."""

    return "|".join([name, "brier", day_set, f"{tau:g}", str(horizon), benchmark])


def p_value_seed(*parts: object) -> int:
    """The p-value seed of one grid of scored days: a 31-bit digest of its name."""

    material = "\x00".join(["#128 p-values", *(str(part) for part in parts)])
    return int.from_bytes(hashlib.sha256(material.encode("utf-8")).digest()[:8], "big") & 0x7FFFFFFF


def classify_primary(results: Mapping[str, Mapping[str, float]]) -> dict:
    """The win rule over the eight primary cells (module docstring, items 2-3).

    `results` maps exactly the eight `primary_key`s to entries carrying
    `p_improve` and `p_worse`. Holm runs over all eight together; each form
    then passes or not on its own four cells.

    Superseded (Eleonora's ruling of 3 October 2026 on #128): this implements
    the rule as committed before scoring, and it stays as committed. The
    corrected rule of 3 October 2026 makes the all-days cell against the
    control decisive: a form wins only if that cell survives Holm, and the
    control is v1 (#117 failed under the corrected rule). The
    persistence-logistic and onset-day cells are supporting evidence only.
    Under the corrected rule both forms fail (PR #207).
    """

    keys = {primary_key(*cell): cell[0] for cell in PRIMARY_CELLS}
    if set(results) != set(keys):
        raise ValueError(f"the primary family is {sorted(keys)}, got {sorted(results)}")
    improve = holm({key: float(results[key]["p_improve"]) for key in keys}, FAMILY_LEVEL)
    worse = holm({key: float(results[key]["p_worse"]) for key in keys}, FAMILY_LEVEL)
    by_form = {}
    for name in PRIMARY_CANDIDATES:
        own = sorted(key for key, owner in keys.items() if owner == name)
        improvements = [key for key in own if improve[key]]
        deteriorations = [key for key in own if worse[key]]
        by_form[name] = {
            "passed": bool(improvements) and not deteriorations,
            "improvements": improvements,
            "deteriorations": deteriorations,
        }
    return {
        "family_size": len(keys),
        "family_level": FAMILY_LEVEL,
        "by_form": by_form,
        "holm_improve": improve,
        "holm_worse": worse,
    }
