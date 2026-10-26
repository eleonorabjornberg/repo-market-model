"""B2 with a minimum pool and a declared fallback chain (#1155; H5 step 2, benchmarks). In force since #1198 on her `GO #1155`.

`docs/decisions/b2-thin-pool.md` is the rule; `IN_FORCE` is the switch and is `True` exactly when that record sits there.
`protocol_benchmarks.b2_forecast`, the B2 the protocol scores, calls `b2_fallback_forecast` with `POOL_MIN` while it is on;
the B2 before the rule is `protocol_benchmarks.b2_forecast_no_minimum`. No published record moves (scoring protocol §13).

B2 (`docs/decisions/scoring-protocol.md` section 4) is the trailing year's spreads on days of the target's type. Under the
month-end turn definition (`turn_days`, #1135) the types are `year_end` (about two days in the window), `quarter_end_turn`
(about six), `turn` (about sixteen), `tax_date` (about eleven) and `ordinary`, and the first three are thin: the 23 quantiles
of two to six values are interpolations of them, with 1% and 99% at the sample's minimum and maximum (Lens C, #958; the 90%
band covered 0.50 on quarter-ends, #762), and the first year-end of a panel has no earlier year-end, so B2 refuses it.

**The rule drafted.** A target's chain is its own type followed by the wider types of `CHAINS`; the pool is the first step of
the chain with at least `pool_min` rows in the window, and every day of the window if none has. `POOL_MIN` is 4. Why: it is
at or below the smallest pool of every type but `year_end` (`quarter_end_turn`, 4 to 6; `tax_date`, 10 to 13; `turn`, 12 to 16
in a window), so the fallback touches only `year_end` (1 to 2 rows), which reads the `quarter_end_turn` rows, and leaves the
rest as B2 is. B1' (`b1_calendar`, #960) uses 30, `spread_mr_variants.POOL_MIN`; at 30 every type but `ordinary` falls
to every day, and B2 stops being a calendar climatology. No number is statistically derived (no pool of a year reaches the
tails of a 23-level grid); the choice, and the alternatives, were hers: she ruled 4 on 24 October 2026.

The type of a row is a function of its date and the holiday table, and every row counted or sampled is at or before the
anchor, the last public row (`protocol_benchmarks._anchor`); `protocol_benchmarks._require_public` restates it for the rows
read. Stdlib only.
"""

from __future__ import annotations

from datetime import time
from pathlib import Path
from typing import Dict, List, Mapping, Optional, Sequence, Tuple

from . import protocol_benchmarks as pb
from . import turn_days
from .data import DailyObservation
from .scoring_protocol import HORIZONS, ProtocolError

ROOT = Path(__file__).resolve().parents[2]

#: Whether the record of #1155 is in force: `docs/decisions/b2-thin-pool.md` (moved from the draft by #1198 on her `GO #1155`).
#: `tests/test_b2_pool_1155.py` fails if the record and this switch disagree. `protocol_benchmarks.b2_forecast` reads it.
IN_FORCE = True

#: The pool floor: fewer rows than this in the trailing year, and the next step of the chain is read (see the module text).
#: Her ruling of 24 October 2026 on question 1: 4.
POOL_MIN = 4

#: The pool of "every day of the window", the end of every chain.
ALL_DAYS = "all_days"

#: A target's chain, by its type: the pool is the first step with `pool_min` rows. A type not listed has itself alone.
CHAINS: Mapping[str, Tuple[str, ...]] = {
    turn_days.YEAR_END: (turn_days.YEAR_END, turn_days.QUARTER_END_TURN, turn_days.TURN),
    turn_days.QUARTER_END_TURN: (turn_days.QUARTER_END_TURN, turn_days.TURN),
    turn_days.TURN: (turn_days.TURN,),
    turn_days.TAX_DATE: (turn_days.TAX_DATE,),
    turn_days.ORDINARY: (turn_days.ORDINARY,),
}


def choose_pool(kind: str, counts: Mapping[str, int], pool_min: int = POOL_MIN,
                chains: Mapping[str, Sequence[str]] = CHAINS) -> str:
    """The type whose rows form the pool for a target of `kind`, or `ALL_DAYS`.

    `counts` is the number of rows of each type in the window (a missing type has none). The first step of the chain with at
    least `pool_min` rows wins.

    Raises:
        ValueError: `pool_min` is below 1.
    """

    if pool_min < 1:
        raise ValueError(f"the pool minimum must be at least 1, got {pool_min}")
    for step in chains.get(kind, (kind,)):
        if counts.get(step, 0) >= pool_min:
            return step
    return ALL_DAYS


def b2_fallback_forecast(
    panel: Sequence[DailyObservation],
    decision_index: int,
    *,
    registry: Mapping[str, Mapping[str, object]],
    decision_time: time,
    splits,
    pool_min: int = POOL_MIN,
    chains: Mapping[str, Sequence[str]] = CHAINS,
    used: Optional[Dict[int, Tuple[str, int]]] = None,
) -> Dict[int, List[float]]:
    """§4 B2 with the fallback: the trailing year's spreads on days of the pool `choose_pool` picks, per lead.

    `splits` is whatever `turn_days.reporting_day_type` reads (a `turn_days.TurnLabels` for the turn definition). When `used`
    is given it is filled with `{lead: (pool, rows)}`.

    Raises:
        ProtocolError: as `protocol_benchmarks.b2_forecast`, but only for a window with no row at all.
        LookAheadError: a row read is after the anchor.
        ValueError: `pool_min` is below 1.
    """

    anchor = pb._anchor(panel, decision_index, registry, decision_time)
    dates = [row.date for row in panel]
    first = pb._window_start(panel, decision_index, pb.B2_YEARS)
    kinds = {s: turn_days.reporting_day_type(splits, panel[s].date, panel[s].values) for s in range(first, anchor + 1)}
    counts: Dict[str, int] = {}
    for kind in kinds.values():
        counts[kind] = counts.get(kind, 0) + 1
    out = {}
    for h in HORIZONS:
        target = panel[decision_index + h]
        kind = turn_days.reporting_day_type(splits, target.date, target.values)
        pool = choose_pool(kind, counts, pool_min, chains)
        rows = [s for s, value in kinds.items() if pool == ALL_DAYS or value == pool]
        if not rows:
            raise ProtocolError(f"B2 has no day in the year before {dates[decision_index]} to forecast {target.date} from")
        pb._require_public(rows, anchor, dates, f"B2 pool for {dates[decision_index]}, lead {h}")
        if used is not None:
            used[h] = (pool, len(rows))
        out[h] = pb.empirical_quantiles(sorted(panel[s].spread_bps for s in rows))
    return out
