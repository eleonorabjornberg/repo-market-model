"""Pressure model v1.1 (#117): the candidate inputs and the win rule, fixed before scoring.

Eleonora's ruling of 2 October 2026 on #117: once the new-input directives have
merged, re-score pressure model v1 with them as candidate inputs. Pressure
model v1 as merged (#124: `scripts/pressure_model_v1.py`'s gbm on the published
funding declaration, conformal PID with nested selection, recalibrated out of
fold) is the control. Each input below is added to it on its own, and then all
together (`JOINT`). Everything in this module was committed before the first
scoring run.

**The inputs** (`CANDIDATES`), each as its directive declared it:

* `announced_iorb` (#38): `iorb_announced_change_bps` and
  `iorb_days_to_announced_change`, the IORB change announced but not yet
  effective (`repo_model.announced_iorb`).
* `conditional_scarcity` (#88): `on_rrp_depleted` and `reserves_when_depleted`,
  reserves once the ON RRP buffer is below $100bn (`contract.COMPOSED_FEATURES`).
* `depletion_settlement` (#97): `settlement_day` and
  `settlement_day_when_depleted`, the settlement calendar and its product with
  the depleted buffer, the two onset inputs #97 declared.
* `effr_iorb` (#98): `effr_minus_iorb_bp`.
* `scarcity_state` (#115): `reserve_scarcity_state`.

`on_rrp` reads the Desk's operation results (#45) in every run, the control's
included, because the composed inputs and the state read it; no published
declaration reads it. The announced-IORB columns and the settlement calendar
are scheduled one business day ahead (`metadata/sources.json`,
`fed_iorb_announcements` and `treasury_auctions`), so, as v1 drops
`treasury_settlement` at horizons of 2 or more, they leave there
(`columns_at_horizon`).

**The win rule** (Eleonora's rulings of 3 October 2026 on #117, the second
narrowing the first), fixed before scoring:

1. *One primary candidate*: `JOINT`, all five inputs together, the version that
   would be published as v1.1. *Four primary cells* (`PRIMARY_CELLS`): +5 bp,
   horizon 1, on all scored days and on onset days, each paired against
   pressure model v1 (the control) and against the persistence-logistic.
   Onset days are #139's (`onset.onset_flags`): the first day above +5 bp after
   at least five panel days at or below it.
2. *Test*: one-sided paired stationary-bootstrap p-values
   (`ml.paired_bootstrap_p_values`, `P_VALUE_REPLICATIONS`, as #187), Holm at a
   `FAMILY_LEVEL` family-wise level over the four primary cells only, for
   improvement and, separately, for deterioration.
3. *Pass*: at least one primary cell survives Holm as an improvement, and none
   survives as a deterioration (`classify_primary`).
4. *Exploratory, deciding nothing*: the five single inputs, +10 bp, horizons
   2-5, the splits, CORP, precision-recall, lead time, October 2025, the
   small-leap targets, CRPS and `on_rrp`. Reported in full.

**The `on_rrp` rule** (Eleonora's ruling of 2 October 2026 on #117), fixed in
advance and reported with its numbers (`on_rrp_rule`): `on_rrp`, in whichever
form scores the lower pooled CRPS (`ON_RRP_FORMS`: plain, or conditional below
the $100bn buffer, which is #88's input), against the published declaration
without it, on the same fold grid, scoring only days before 2026-01-01, meets
the rule if (1) the pooled paired CRPS improves with its 90% interval
excluding zero, or the Brier at +5 or +10 bp improves with its interval
excluding zero; and (2) none of the three gets worse with an interval
excluding zero. The Brier is pressure model v1's, at horizon 1, the horizon the
CRPS is scored at.

Standard library only, like the rest of `src/` outside `ml.py`.
"""

from __future__ import annotations

import hashlib
from typing import Dict, Mapping, NamedTuple, Tuple

from .dvp_segment import holm

__all__ = [
    "BENCHMARKS",
    "CANDIDATES",
    "Candidate",
    "FAMILY_LEVEL",
    "JOINT",
    "ON_RRP_FORMS",
    "ONE_DAY_AHEAD",
    "P_VALUE_REPLICATIONS",
    "PRIMARY_CELLS",
    "candidate_columns",
    "classify_primary",
    "columns_at_horizon",
    "on_rrp_rule",
    "p_value_seed",
    "primary_key",
]


class Candidate(NamedTuple):
    """One input: its name, the directive that declared it, and its columns."""

    name: str
    directive: str
    columns: Tuple[str, ...]


#: The five inputs, in the directive's order. Fixed before scoring.
CANDIDATES: Tuple[Candidate, ...] = (
    Candidate("announced_iorb", "#38", ("iorb_announced_change_bps", "iorb_days_to_announced_change")),
    Candidate("conditional_scarcity", "#88", ("on_rrp_depleted", "reserves_when_depleted")),
    Candidate("depletion_settlement", "#97", ("settlement_day", "settlement_day_when_depleted")),
    Candidate("effr_iorb", "#98", ("effr_minus_iorb_bp",)),
    Candidate("scarcity_state", "#115", ("reserve_scarcity_state",)),
)

#: All five together: the one primary candidate.
JOINT = "joint"

#: The two forms of `on_rrp` the 2 October ruling names.
ON_RRP_FORMS: Tuple[Tuple[str, Tuple[str, ...]], ...] = (
    ("on_rrp_plain", ("on_rrp",)),
    ("conditional_scarcity", ("on_rrp_depleted", "reserves_when_depleted")),
)

#: Inputs public only one business day ahead (scheduled availability).
ONE_DAY_AHEAD = frozenset(
    {"iorb_announced_change_bps", "iorb_days_to_announced_change", "settlement_day",
     "settlement_day_when_depleted"}
)

FAMILY_LEVEL = 0.10
P_VALUE_REPLICATIONS = 20000
BENCHMARKS = ("pressure_model_v1", "persistence_logistic")
POOLED = "all_days"
ONSET = "onset_days"

#: `(candidate, day set, tau, horizon, benchmark)`: the only cells that decide.
PRIMARY_CELLS: Tuple[Tuple[str, str, float, int, str], ...] = tuple(
    (JOINT, day_set, 5.0, 1, bench) for day_set in (POOLED, ONSET) for bench in BENCHMARKS
)


def candidate_columns(name: str) -> Tuple[str, ...]:
    """The columns a candidate adds to the control, in declared order."""

    if name == JOINT:
        return tuple(column for candidate in CANDIDATES for column in candidate.columns)
    for candidate in CANDIDATES:
        if candidate.name == name:
            return candidate.columns
    forms = dict(ON_RRP_FORMS)
    if name in forms:
        return forms[name]
    raise ValueError(f"unknown candidate {name!r}")


def columns_at_horizon(columns: Tuple[str, ...], horizon: int) -> Tuple[str, ...]:
    """`columns` without the one-day-ahead inputs at a horizon of 2 or more."""

    return tuple(column for column in columns if horizon == 1 or column not in ONE_DAY_AHEAD)


def primary_key(candidate: str, day_set: str, tau: float, horizon: int, benchmark: str) -> str:
    """One comparison's name: `candidate|brier|day set|tau|h|benchmark`."""

    return "|".join([candidate, "brier", day_set, f"{tau:g}", str(horizon), benchmark])


def p_value_seed(*parts: object) -> int:
    """The p-value seed of one grid of scored days: a 31-bit digest of its name."""

    material = "\x00".join(["#117 p-values", *(str(part) for part in parts)])
    return int.from_bytes(hashlib.sha256(material.encode("utf-8")).digest()[:8], "big") & 0x7FFFFFFF


def classify_primary(results: Mapping[str, Mapping[str, float]]) -> dict:
    """The win rule over the primary cells (module docstring, items 2-3).

    `results` maps exactly the four `primary_key`s to entries carrying
    `p_improve` and `p_worse`.
    """

    keys = {primary_key(*cell) for cell in PRIMARY_CELLS}
    if set(results) != keys:
        raise ValueError(
            f"the primary family is {sorted(keys)}, got {sorted(results)}"
        )
    improve = holm({key: float(results[key]["p_improve"]) for key in keys}, FAMILY_LEVEL)
    worse = holm({key: float(results[key]["p_worse"]) for key in keys}, FAMILY_LEVEL)
    improvements = sorted(key for key, rejected in improve.items() if rejected)
    deteriorations = sorted(key for key, rejected in worse.items() if rejected)
    return {
        "passed": bool(improvements) and not deteriorations,
        "family_size": len(keys),
        "family_level": FAMILY_LEVEL,
        "improvements": improvements,
        "deteriorations": deteriorations,
        "holm_improve": improve,
        "holm_worse": worse,
    }


def on_rrp_rule(forms: Mapping[str, Mapping[str, object]]) -> dict:
    """The 2 October ruling's rule for `on_rrp` (module docstring).

    `forms` maps each `ON_RRP_FORMS` name to `candidate_crps_bps` (its pooled
    CRPS) and `crps`, `brier_5`, `brier_10`, each `{"mean", "interval":
    {"lower", "upper"}}` oriented so that a positive value favours the form
    (control minus form). The form is the one with the lower pooled CRPS,
    chosen before its other results are read.
    """

    names = [name for name, _columns in ON_RRP_FORMS]
    if set(forms) != set(names):
        raise ValueError(f"the forms are {names}, got {sorted(forms)}")
    form = min(names, key=lambda name: (float(forms[name]["candidate_crps_bps"]), names.index(name)))
    chosen = forms[form]
    measures = ("crps", "brier_5", "brier_10")
    better = {m: float(chosen[m]["interval"]["lower"]) > 0.0 for m in measures}
    worse = {m: float(chosen[m]["interval"]["upper"]) < 0.0 for m in measures}
    met = (better["crps"] or better["brier_5"] or better["brier_10"]) and not any(worse.values())
    summary: Dict[str, object] = {
        "form": form,
        "met": met,
        "improves_excluding_zero": better,
        "worse_excluding_zero": worse,
        "pooled_crps_by_form": {name: float(forms[name]["candidate_crps_bps"]) for name in names},
    }
    return summary
