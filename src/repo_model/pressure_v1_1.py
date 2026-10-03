"""Pressure model v1.1 (#117): the candidate inputs and the pre-registered win rule.

Eleonora's ruling of 2 October 2026 on #117: re-score pressure model v1 with
the new inputs as candidate inputs, each as its own paired comparison against
v1 as merged (the control), and then all together. Her rulings of 3 October
2026 on #117 fix the win rule **before any scoring**; this module is that rule,
committed before the first scoring run, and the pull request shows it unchanged
afterwards.

**The candidates** (`CANDIDATES`), each added to pressure model v1's
declaration (`scripts/pressure_model_v1.py`, `publish`: gbm on the published
funding declaration, conformal PID with nested selection, recalibrated out of
fold) and nothing else changed:

* `announced_iorb` (#38): `iorb_announced_change_bps`,
  `iorb_days_to_announced_change`;
* `rrp_conditional` (#88): `on_rrp_depleted`, `reserves_when_depleted`;
* `settlement_onset` (#97): `settlement_day`, `settlement_day_when_depleted`;
* `effr_minus_iorb` (#98): `effr_minus_iorb_bp`;
* `scarcity_state` (#115): `reserve_scarcity_state`, the four-level state.

**The primary candidate** (`PRIMARY`) is all five together: the version that
would be published as v1.1. It is the only candidate that can decide anything.
The five single inputs are exploratory: reported in full, paired against v1
with intervals and splits, so the table shows which input did the work, and
deciding nothing. So is `on_rrp_plain` (v1 plus `on_rrp`), scored for the
`on_rrp` question deferred from #110.

**The primary family** (`primary_cells`, `FAMILY_SIZE` = 4): the primary
candidate's Brier at +5 bp, horizon 1, on all scored days and on onset days
(#139's definition, `onset.onset_flags`: the first day above +5 bp after at
least five panel days at or below it), each paired against pressure model v1 as
merged and against the persistence-logistic.

**The win rule** (`classify`):

1. Each primary cell gets a one-sided paired stationary-bootstrap p-value for
   improvement and one for deterioration (`ml.paired_bootstrap_p_values`, as
   in #187, `P_VALUE_REPLICATIONS` replications, block length 2 as the tables'
   intervals at horizon 1 use; the cells scored on one grid of days share one
   seed, `p_value_seed`, and so their resamples).
2. The improvement p-values are Holm corrected over the four primary cells
   only, at `FAMILY_LEVEL`; so, separately, are the deterioration p-values.
3. The primary candidate **passes** when at least one primary cell survives the
   correction as an improvement and none survives it as a deterioration.

Everything else is labelled "exploratory" and decides nothing: +10 bp,
horizons 2-5, the single inputs, splits, CORP, precision-recall, lead time,
the October 2025 onset, CRPS, the small-leap targets and `on_rrp`. A single
input that helps while the joint candidate fails is said so; any test of it is
a new pre-registered follow-up, not decided here.

**At horizons of 2 or more** `treasury_settlement_coupons` and the announced
IORB columns are not public at the decision instant under their declarations
(`metadata/sources.json`: scheduled one business day ahead), so the as-of rule
refuses them there, as it refuses `treasury_settlement`. `columns_at_horizon`
drops them, as pressure model v1 drops `treasury_settlement` (Eleonora's
ruling on #170, option A): the joint candidate at h >= 2 is v1 plus #88, #98
and #115, and the #38 and #97 runs are not scored there.

**The `on_rrp` rule** (Eleonora's ruling of 2 October 2026 on #117, fixed in
advance): `on_rrp`, in whichever form this directive's evidence reports best on
pooled CRPS (`on_rrp_form`: plain, or conditional below the $100bn buffer,
#88's pair), joins the published declaration without a further question if,
against the published declaration without it, on one fold grid, scoring only
days before 2026-01-01, `on_rrp_rule` holds: pooled paired CRPS improves with
its 90% interval excluding zero, or the Brier at +5 or +10 bp does; and none of
the three gets worse with an interval excluding zero.

**Off.** Nothing here is read by a published declaration, panel or record.

Standard library only, like the rest of `src/` outside `ml.py`.
"""

from __future__ import annotations

import hashlib
from datetime import date
from typing import Dict, List, Mapping, NamedTuple, Sequence, Tuple

from .data import DailyObservation
from .dvp_segment import holm as _holm
from .onset import onset_flags

__all__ = [
    "BENCHMARKS",
    "CANDIDATES",
    "Candidate",
    "DAY_SETS",
    "FAMILY_LEVEL",
    "FAMILY_SIZE",
    "HORIZONS",
    "NOT_PUBLIC_BEYOND_H1",
    "ON_RRP_FORMS",
    "ONSET",
    "POOLED",
    "PRIMARY",
    "PRIMARY_HORIZON",
    "PRIMARY_THRESHOLD",
    "P_VALUE_REPLICATIONS",
    "RUNS",
    "Run",
    "THRESHOLDS",
    "classify",
    "columns_at_horizon",
    "comparison_key",
    "holm",
    "on_rrp_form",
    "on_rrp_rule",
    "onset_positions",
    "p_value_seed",
    "primary_cells",
]


class Candidate(NamedTuple):
    """One new input: its name, the directive that added it, and its columns."""

    name: str
    issue: str
    columns: Tuple[str, ...]


class Run(NamedTuple):
    """One scored run: v1 plus `columns`. Only the primary candidate decides."""

    name: str
    columns: Tuple[str, ...]
    primary: bool = False


#: The five inputs, in the directive's order. Fixed before scoring.
CANDIDATES: Tuple[Candidate, ...] = (
    Candidate("announced_iorb", "#38", ("iorb_announced_change_bps", "iorb_days_to_announced_change")),
    Candidate("rrp_conditional", "#88", ("on_rrp_depleted", "reserves_when_depleted")),
    Candidate("settlement_onset", "#97", ("settlement_day", "settlement_day_when_depleted")),
    Candidate("effr_minus_iorb", "#98", ("effr_minus_iorb_bp",)),
    Candidate("scarcity_state", "#115", ("reserve_scarcity_state",)),
)

#: The one primary candidate (ruling of 3 October 2026): all five together.
PRIMARY = "all_together"

#: Every scored run beside the control and the persistence-logistic.
RUNS: Tuple[Run, ...] = (
    Run(PRIMARY, tuple(column for candidate in CANDIDATES for column in candidate.columns), primary=True),
    *(Run(candidate.name, candidate.columns) for candidate in CANDIDATES),
    Run("on_rrp_plain", ("on_rrp",)),
)

#: The `on_rrp` question's two forms: plain, and conditional below the $100bn
#: buffer, which is #88's pair.
ON_RRP_FORMS: Mapping[str, str] = {"plain": "on_rrp_plain", "conditional": "rrp_conditional"}

#: Inputs whose declaration makes them public one business day ahead only:
#: refused by the as-of rule at horizons of 2 or more.
NOT_PUBLIC_BEYOND_H1 = frozenset(
    {
        "iorb_announced_change_bps",
        "iorb_days_to_announced_change",
        "settlement_day",
        "settlement_day_when_depleted",
    }
)

THRESHOLDS = (5.0, 10.0)
HORIZONS = (1, 2, 3, 4, 5)
BENCHMARKS = ("pressure_model_v1", "persistence_logistic")
POOLED = "all_days"
ONSET = "onset_days"
DAY_SETS = (POOLED, ONSET)

#: The primary family (ruling of 3 October 2026), fixed before scoring.
PRIMARY_THRESHOLD = 5.0
PRIMARY_HORIZON = 1
FAMILY_LEVEL = 0.10
FAMILY_SIZE = 4
#: The smallest attainable p-value is 1 / (replications + 1), well below
#: Holm's smallest threshold, `FAMILY_LEVEL / FAMILY_SIZE`.
P_VALUE_REPLICATIONS = 20000


def columns_at_horizon(run: Run, horizon: int) -> Tuple[str, ...]:
    """The run's columns that are public at `horizon` (module docstring)."""

    if horizon == 1:
        return run.columns
    return tuple(column for column in run.columns if column not in NOT_PUBLIC_BEYOND_H1)


def comparison_key(run: str, *parts: object) -> str:
    """One comparison's name: `run|brier|day set|tau|h|benchmark` or `run|crps`."""

    return "|".join([run, *(f"{part:g}" if isinstance(part, float) else str(part) for part in parts)])


def primary_cells() -> Tuple[str, ...]:
    """The four primary cells, in a fixed order."""

    cells = tuple(
        comparison_key(PRIMARY, "brier", day_set, PRIMARY_THRESHOLD, PRIMARY_HORIZON, bench)
        for day_set in DAY_SETS
        for bench in BENCHMARKS
    )
    if len(cells) != FAMILY_SIZE:
        raise ValueError(f"{len(cells)} primary cells, declared {FAMILY_SIZE}")
    return cells


def onset_positions(rows: Sequence[DailyObservation], scored_dates: Sequence[date]) -> List[int]:
    """Positions into `scored_dates` of #139's onset days (`onset.onset_flags`)."""

    flags = {row.date: flag for row, flag in zip(rows, onset_flags(rows))}
    return [k for k, when in enumerate(scored_dates) if flags.get(when, False)]


def p_value_seed(*parts: object) -> int:
    """The p-value seed of one grid of scored days: a 31-bit digest of its name."""

    material = "\x00".join(["#117 p-values", *(str(part) for part in parts)])
    return int.from_bytes(hashlib.sha256(material.encode("utf-8")).digest()[:8], "big") & 0x7FFFFFFF


def holm(p_values: Mapping[str, float], level: float = FAMILY_LEVEL) -> Dict[str, bool]:
    """Holm's step-down procedure at `level` (`dvp_segment.holm`, #187)."""

    return _holm(p_values, level)


def classify(results: Mapping[str, Mapping[str, float]]) -> dict:
    """The primary candidate's outcome under the win rule (module docstring).

    `results` maps exactly the four `primary_cells` to their `p_improve` and
    `p_worse`. Holm runs over those four only, separately for improvement and
    deterioration.
    """

    cells = primary_cells()
    if set(results) != set(cells):
        raise ValueError(
            f"the win rule reads exactly the {FAMILY_SIZE} primary cells, got {sorted(results)}"
        )
    improve = holm({key: float(results[key]["p_improve"]) for key in cells})
    worse = holm({key: float(results[key]["p_worse"]) for key in cells})
    improving = [key for key in cells if improve[key]]
    deteriorating = [key for key in cells if worse[key]]
    return {
        "candidate": PRIMARY,
        "passed": bool(improving) and not deteriorating,
        "improving_cells": improving,
        "deteriorating_cells": deteriorating,
        "holm_improve": improve,
        "holm_worse": worse,
        "family_size": FAMILY_SIZE,
        "family_level": FAMILY_LEVEL,
    }


def _excludes_zero_above(entry: Mapping[str, object]) -> bool:
    return float(entry["interval"]["lower"]) > 0.0


def _excludes_zero_below(entry: Mapping[str, object]) -> bool:
    return float(entry["interval"]["upper"]) < 0.0


def on_rrp_rule(
    *, crps: Mapping[str, object], brier_5: Mapping[str, object], brier_10: Mapping[str, object]
) -> dict:
    """Eleonora's `on_rrp` rule (ruling of 2 October 2026 on #117).

    Each entry is a paired difference oriented so that a positive mean favours
    the form (control minus form), with its 90% `interval`. Met when CRPS or a
    Brier improves with its interval excluding zero, and none of the three is
    worse with its interval excluding zero.
    """

    entries = {"crps": crps, "brier_5": brier_5, "brier_10": brier_10}
    improved = sorted(name for name, entry in entries.items() if _excludes_zero_above(entry))
    worse = sorted(name for name, entry in entries.items() if _excludes_zero_below(entry))
    return {"met": bool(improved) and not worse, "improved": improved, "worse": worse}


def on_rrp_form(pooled_crps_improvement: Mapping[str, float]) -> str:
    """The form the rule reads: the run with the largest pooled CRPS improvement."""

    names = set(ON_RRP_FORMS.values())
    if set(pooled_crps_improvement) != names:
        raise ValueError(f"need the pooled CRPS of exactly {sorted(names)}")
    return max(sorted(names), key=lambda name: pooled_crps_improvement[name])
