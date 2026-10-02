"""The reserve-scarcity state: a declared regime, from cut-points fixed in advance (#115).

Plan §1, "Scarcity indicator", and deliverable 4. The state is an ordinal score
built from two readings, each against a cut-point taken from outside this
repository's pressure days and declared here before any validation was run:

- **The reserves ratio**, reserve balances over total assets of all commercial
  banks, against the satiation band of Afonso, Giannone, La Spada & Williams
  (`SATIATION_BAND`): 0 at or above the band, 1 inside it, 2 below it.
- **The ON RRP buffer**, the day's accepted reverse repos, against the $100bn
  break (`ON_RRP_BUFFER_BN`): 0 at or above it, 1 below it. A buffer above it
  absorbs a drain before reserves do.

`reserve_scarcity_state` is the sum, 0 (abundant) to 3 (scarce). Nothing here is
fitted: the cut-points are constants, a sensitivity run moves them by a stated
amount (`SENSITIVITY_VARIANTS`) and reports what happens, and no variant is
ever chosen by what it scores.

**Read as-of, never assembled.** `with_reserve_scarcity_state` computes the
state on each panel row from that row's own `reserve_balances`,
`bank_total_assets` and `on_rrp`, and `contract.RESERVE_SCARCITY_STATE_FIELDS`
declares the column over every field those three draw on. `InformationRule`
then reads it at the latest row where all three were public at the decision
instant -- in practice the H.8 sets that row, about ten days back, since the
Board releases a week's bank assets on the second Friday after it, at 16:15,
after the 16:00 decision. The ratio's two legs are the same week's: both are
weekly, dated to the Wednesday, and carried from it.

**Off.** `BANK_TOTAL_ASSETS_FIELDS` and `RESERVE_SCARCITY_STATE_FIELDS` are not
in the published `contract.FEATURE_FIELDS`, so no published declaration, panel
or record reads the state. `measurement_feature_fields` is the map a
measurement run switches on; whether the indicator is published is Eleonora's.

**Validation.** `pressure_days_by_state` walks the shared fold grid through
`baseline._as_of_folds` -- so the lockbox and both read guards apply -- and pairs
each scored day's as-of state with whether that day's SOFR - IORB was above +5
and +10 bp. `tabulate` reports the frequency per state and per year, with
stationary-bootstrap intervals. Pressure-day frequency must rise with the
state; `tabulate` says whether it does, and does not hide it when it does not.

Stdlib only, like the rest of `src/` outside `ml.py`.
"""

from __future__ import annotations

from contextlib import contextmanager
from datetime import date, time
from types import MappingProxyType
from typing import Dict, Iterator, List, Mapping, NamedTuple, Optional, Sequence, Tuple

from . import contract
from .data import DailyObservation
from .metrics import stationary_bootstrap_interval

__all__ = [
    "BOOTSTRAP_BLOCK_LENGTH",
    "BOOTSTRAP_LEVEL",
    "BOOTSTRAP_REPLICATIONS",
    "BOOTSTRAP_SEED",
    "ON_RRP_BUFFER_BN",
    "PRESSURE_THRESHOLDS_BP",
    "RESERVE_SCARCITY_STATE",
    "SATIATION_BAND",
    "SENSITIVITY_VARIANTS",
    "STATE_LABELS",
    "ScoredDay",
    "buffer_level",
    "measurement_declaration",
    "measurement_feature_fields",
    "pressure_days_by_state",
    "ratio_level",
    "reserve_scarcity_state",
    "reserves_ratio",
    "tabulate",
    "with_reserve_scarcity_state",
]

#: The panel column, and the declared feature a model would name.
RESERVE_SCARCITY_STATE = "reserve_scarcity_state"

#: Reserves as a share of commercial-bank total assets at which the reserve
#: demand curve flattens: "satiation at about 12-13% of bank assets".
#:
#: Afonso, G., D. Giannone, G. La Spada and J. C. Williams (2022, revised
#: November 2025), "Scarce, Abundant, or Ample? A Time-Varying Model of the
#: Reserve Demand Curve", Federal Reserve Bank of New York Staff Report 1019,
#: https://www.newyorkfed.org/medialibrary/media/research/staff_reports/sr1019.pdf
#: -- the basis of the New York Fed's Reserve Demand Elasticity, and listed in
#: `docs/pivot/literature.md` and plan §1. The band is taken as stated, both
#: ends: at or above 13% the ratio reads abundant (level 0), from 12% up to 13%
#: it reads at satiation (1), and below 12% below it (2). The ratio is
#: reserves over the H.8's total assets of all commercial banks, the paper's
#: normalisation.
SATIATION_BAND: Tuple[float, float] = (0.12, 0.13)

#: The ON RRP balance, in USD billions, below which the facility no longer
#: buffers a reserve drain: "the operative break is at approximately $100bn".
#:
#: Beroud, N., `docs/advisor/evidence-pack/MEMO.md`, Q4 (PR #87, merged 1
#: October 2026): weekly observations with ON RRP above $100bn show +5 bp
#: pressure on 1.35% ($100-500bn) and 0.00% (above $500bn) of weeks, against
#: 13-15% below it, with no break between the <$10bn and $10-100bn bins. Taken
#: as the directive states it (#115, step 2). Unlike SR 1019's band it was read
#: off 2018-2026 data that overlaps this validation's, which the pull request
#: that introduced it reports among what it did not check.
ON_RRP_BUFFER_BN = 100.0

#: The score's names, for tables. The score is ordinal; the names are labels.
STATE_LABELS = MappingProxyType(
    {
        0: "abundant",
        1: "ample",
        2: "tight",
        3: "scarce",
    }
)

#: The headline pressure events (`docs/decisions/pressure-probability.md`):
#: SOFR - IORB strictly greater than each, in basis points.
PRESSURE_THRESHOLDS_BP: Tuple[float, ...] = (5.0, 10.0)

#: Declared with the state, before any validation was run: one percentage point
#: either way on the satiation band, and half and double the buffer. Each is
#: reported beside the declared state and none replaces it.
SENSITIVITY_VARIANTS = MappingProxyType(
    {
        "declared": (SATIATION_BAND, ON_RRP_BUFFER_BN),
        "band 11-12%": ((0.11, 0.12), ON_RRP_BUFFER_BN),
        "band 13-14%": ((0.13, 0.14), ON_RRP_BUFFER_BN),
        "buffer $50bn": (SATIATION_BAND, 50.0),
        "buffer $200bn": (SATIATION_BAND, 200.0),
    }
)

#: The interval's resampling, declared rather than tuned. Pressure days come in
#: episodes, so a day is resampled with its neighbours: a mean block of ten
#: business days, about two weeks, which spans a month-end or a settlement
#: week. The level and replications are the project's (`baseline`'s 90%, 2000).
BOOTSTRAP_BLOCK_LENGTH = 10
BOOTSTRAP_LEVEL = 0.90
BOOTSTRAP_REPLICATIONS = 2000
BOOTSTRAP_SEED = 115


def reserves_ratio(reserves_bn: float, bank_assets_bn: float) -> float:
    """Reserve balances as a share of commercial-bank total assets."""

    if not bank_assets_bn > 0.0:
        raise ValueError(
            f"bank total assets must be positive to divide by, got {bank_assets_bn!r}"
        )
    if reserves_bn < 0.0:
        raise ValueError(f"reserve balances cannot be negative, got {reserves_bn!r}")
    return reserves_bn / bank_assets_bn


def ratio_level(ratio: float, band: Tuple[float, float] = SATIATION_BAND) -> int:
    """0 at or above the band, 1 inside it, 2 below it."""

    low, high = band
    if not 0.0 < low <= high < 1.0:
        raise ValueError(f"a satiation band is two shares low <= high in (0, 1), got {band!r}")
    if ratio >= high:
        return 0
    if ratio >= low:
        return 1
    return 2


def buffer_level(on_rrp_bn: float, buffer_bn: float = ON_RRP_BUFFER_BN) -> int:
    """0 when the ON RRP balance is at or above the buffer, 1 below it."""

    if on_rrp_bn < 0.0:
        raise ValueError(f"an ON RRP balance cannot be negative, got {on_rrp_bn!r}")
    return 0 if on_rrp_bn >= buffer_bn else 1


def reserve_scarcity_state(
    reserves_bn: Optional[float],
    bank_assets_bn: Optional[float],
    on_rrp_bn: Optional[float],
    *,
    band: Tuple[float, float] = SATIATION_BAND,
    buffer_bn: float = ON_RRP_BUFFER_BN,
) -> Optional[int]:
    """The ordinal state, 0 (abundant) to 3 (scarce); `None` when an input is a hole.

    A hole stays a hole: a state from two of its three readings would be a
    different indicator, and the panel's own carry rules
    (`data.CARRY_FORWARD_COLUMNS`) already say how stale a weekly reading may
    stand before it is absent.
    """

    if reserves_bn is None or bank_assets_bn is None or on_rrp_bn is None:
        return None
    return ratio_level(reserves_ratio(reserves_bn, bank_assets_bn), band) + buffer_level(
        on_rrp_bn, buffer_bn
    )


def with_reserve_scarcity_state(
    rows: Sequence[DailyObservation],
    *,
    band: Tuple[float, float] = SATIATION_BAND,
    buffer_bn: float = ON_RRP_BUFFER_BN,
) -> List[DailyObservation]:
    """The rows with `reserve_scarcity_state` added, each from its own row only.

    A row's state reads that row's `reserve_balances`, `bank_total_assets` and
    `on_rrp` and nothing else -- no other row, no later print -- so the column
    is exactly as old as the three it is made from, and the as-of rule prices it
    by their declarations (`contract.RESERVE_SCARCITY_STATE_FIELDS`).
    """

    out = []
    for row in rows:
        values = dict(row.values)
        for column in ("reserve_balances", "bank_total_assets", "on_rrp"):
            if column not in values:
                raise ValueError(
                    f"the row for {row.date} carries no {column!r}; the state is "
                    f"read from reserve_balances, bank_total_assets and on_rrp"
                )
        state = reserve_scarcity_state(
            values["reserve_balances"],
            values["bank_total_assets"],
            values["on_rrp"],
            band=band,
            buffer_bn=buffer_bn,
        )
        values[RESERVE_SCARCITY_STATE] = None if state is None else float(state)
        out.append(DailyObservation(row.date, values))
    return out


def measurement_feature_fields() -> Mapping[str, Tuple[Tuple[str, str], ...]]:
    """`contract.FEATURE_FIELDS` with the state and its inputs switched on.

    For a measurement run and its tests only; the published map is unchanged.
    `on_rrp` reads the Desk's operation results, `bank_total_assets` the H.8
    first prints, and `reserve_scarcity_state` all of their fields and
    `reserve_balances`'.
    """

    return MappingProxyType(
        {
            **contract.FEATURE_FIELDS,
            "on_rrp": contract.ON_RRP_OPERATION_RESULTS_FIELDS,
            "bank_total_assets": contract.BANK_TOTAL_ASSETS_FIELDS,
            RESERVE_SCARCITY_STATE: contract.RESERVE_SCARCITY_STATE_FIELDS,
        }
    )


@contextmanager
def measurement_declaration() -> Iterator[None]:
    """`measurement_feature_fields` in force, for one measurement run.

    Swaps `contract.FEATURE_FIELDS` and its projection `FEATURE_SOURCES` for the
    duration and restores both on the way out, raise or return. The published
    map is never written: what a published build or record reads is untouched
    outside this block.
    """

    fields = measurement_feature_fields()
    saved = contract.FEATURE_FIELDS, contract.FEATURE_SOURCES
    contract.FEATURE_FIELDS = fields
    contract.FEATURE_SOURCES = MappingProxyType(
        {
            feature: tuple(sorted({source for source, _field in pairs}))
            for feature, pairs in fields.items()
        }
    )
    try:
        yield
    finally:
        contract.FEATURE_FIELDS, contract.FEATURE_SOURCES = saved


class ScoredDay(NamedTuple):
    """One scored day: its as-of state, the row it was read from, and its spread."""

    day: date
    state: Optional[float]
    read_date: date
    spread_bps: float


def pressure_days_by_state(
    rows: Sequence[DailyObservation],
    *,
    registry: Mapping[str, Mapping[str, object]],
    decision_time: time,
    minimum_history: int,
    end: Optional[date] = None,
    feature: str = RESERVE_SCARCITY_STATE,
) -> List[ScoredDay]:
    """Every scored day of the shared fold grid, with its as-of state.

    The grid and the reads are `baseline._as_of_folds`'s: the first scored day
    is the first with `minimum_history` observable labels, whatever the
    declaration, the lockbox is checked before anything is read, and every
    read passes both guards. The state is the one the forecast for that day
    could have read at its decision instant; the spread is the day's own,
    which is the outcome, not an input.
    """

    from .asof import InformationRule
    from .baseline import _as_of_folds

    rule = InformationRule(registry, ("spread_bps", feature), decision_time=decision_time)
    scored = []
    for fold in _as_of_folds(
        rows,
        rule,
        minimum_history=minimum_history,
        refit_every=len(rows),
        entry="scarcity.pressure_days_by_state",
        end=end,
    ):
        (read,) = [item for item in fold.info.reads if item.feature == feature]
        scored.append(
            ScoredDay(
                day=rows[fold.index].date,
                state=fold.feature_row.values.get(feature),
                read_date=rows[read.row].date,
                spread_bps=rows[fold.index].spread_bps,
            )
        )
    return scored


def _frequency_cell(outcomes: Sequence[int], *, seed: int) -> Dict[str, object]:
    count = len(outcomes)
    hits = sum(outcomes)
    lower, upper = stationary_bootstrap_interval(
        lambda indices: sum(outcomes[i] for i in indices) / len(indices),
        count,
        block_length=min(BOOTSTRAP_BLOCK_LENGTH, count),
        seed=seed,
        replications=BOOTSTRAP_REPLICATIONS,
        level=BOOTSTRAP_LEVEL,
    )
    return {
        "days": count,
        "pressure_days": hits,
        "frequency": hits / count,
        "interval": [lower, upper],
    }


def tabulate(
    scored: Sequence[ScoredDay],
    *,
    thresholds: Sequence[float] = PRESSURE_THRESHOLDS_BP,
    seed: int = BOOTSTRAP_SEED,
) -> Dict[str, object]:
    """Pressure-day frequency per state and per year, with intervals.

    Per state, each threshold's frequency is over that state's scored days, in
    date order, and its interval resamples those days in blocks
    (`BOOTSTRAP_BLOCK_LENGTH`), at `BOOTSTRAP_LEVEL`. Days whose state is a
    hole are counted under `unknown` and in no state. `rises` says, per
    threshold, whether the frequency is non-decreasing from each state to the
    next among the states that occur -- the validation's one yes-or-no
    question, answered from the point estimates. Per year: the scored days, the
    days in each state, the days with SOFR above IORB, and each threshold's
    frequency with its interval.
    """

    if not scored:
        raise ValueError("no scored days to tabulate")
    by_state: Dict[str, Dict[str, object]] = {}
    states = sorted({int(day.state) for day in scored if day.state is not None})
    for state in states:
        days = [day for day in scored if day.state is not None and int(day.state) == state]
        by_state[str(state)] = {
            "label": STATE_LABELS.get(state, str(state)),
            "days": len(days),
            "above_iorb_days": sum(day.spread_bps > 0.0 for day in days),
            **{
                f"gt_{threshold:g}bp": _frequency_cell(
                    [int(day.spread_bps > threshold) for day in days], seed=seed
                )
                for threshold in thresholds
            },
        }
    rises = {}
    for threshold in thresholds:
        frequencies = [by_state[str(state)][f"gt_{threshold:g}bp"]["frequency"] for state in states]
        rises[f"gt_{threshold:g}bp"] = all(
            later >= earlier for earlier, later in zip(frequencies, frequencies[1:])
        )
    by_year: Dict[str, Dict[str, object]] = {}
    for year in sorted({day.day.year for day in scored}):
        days = [day for day in scored if day.day.year == year]
        by_year[str(year)] = {
            "days": len(days),
            "days_by_state": {
                str(state): sum(
                    1 for day in days if day.state is not None and int(day.state) == state
                )
                for state in states
            },
            "unknown_state_days": sum(1 for day in days if day.state is None),
            "above_iorb_days": sum(day.spread_bps > 0.0 for day in days),
            **{
                f"gt_{threshold:g}bp": _frequency_cell(
                    [int(day.spread_bps > threshold) for day in days], seed=seed
                )
                for threshold in thresholds
            },
        }
    return {
        "scored_days": len(scored),
        "first_scored_day": scored[0].day.isoformat(),
        "last_scored_day": scored[-1].day.isoformat(),
        "unknown_state_days": sum(1 for day in scored if day.state is None),
        "by_state": by_state,
        "rises": rises,
        "by_year": by_year,
        "bootstrap": {
            "method": "stationary",
            "block_length": BOOTSTRAP_BLOCK_LENGTH,
            "level": BOOTSTRAP_LEVEL,
            "replications": BOOTSTRAP_REPLICATIONS,
            "seed": seed,
        },
    }
