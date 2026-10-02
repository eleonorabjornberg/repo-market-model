"""Early-warning inputs (#127): the pre-declared candidates and their columns.

Eleonora's request of 2 October 2026: test the registered but unused sources
that should move *before* a spike, the onset signals the Fed cited for 2025,
and an issuance × dealer-positions term. The list below is fixed before any
scoring and every item is reported, whatever its result. The onset signals'
definitions are fixed by the issue, because they were chosen with hindsight:
their real test is the 2026 lockbox, opened once.

Each candidate is a set of panel columns a declaration adds, and for the
direct pressure model (`ml.pressure_logistic_exceedance`) a set of product
terms. A column is built by `build_columns` from its own row and earlier rows
only, and is declared in `COLUMN_FIELDS` with every source field it draws on,
so the as-of rule (`asof.InformationRule`) reads it at the latest row whose
every field was public at the decision instant. Every lag here is monotone in
the row, so the earlier rows a window reads were public whenever its last row
was.

**Off.** `COLUMN_FIELDS` is not part of `contract.FEATURE_FIELDS`: no
published panel, declaration or record reads these columns. The scoring
script (`scripts/early_warning_inputs.py`) switches them on for its own run,
as #45's tests do for `on_rrp`. Which inputs, if any, join a published
declaration is Eleonora's to rule.

Standard library only, like the rest of `src/` outside `ml.py`.
"""

from __future__ import annotations

from datetime import date
from typing import Dict, List, Mapping, NamedTuple, Optional, Sequence, Tuple

from .contract import (
    FEATURE_FIELDS,
    ON_RRP_OPERATION_RESULTS_FIELDS,
    SRF_OPERATION_RESULTS_FIELDS,
)
from .data import DailyObservation
from .ingest import SRF_INCEPTION

__all__ = [
    "CANDIDATES",
    "COLUMN_FIELDS",
    "Candidate",
    "ONSET_GROUP",
    "ONSET_WINDOW",
    "ON_RRP_FLAG_BELOW_USD_BN",
    "TGA_CHANGE_ROWS",
    "build_columns",
]

#: The onset signals' window: the last 20 business days, i.e. 20 panel rows
#: ending at the row read (#127).
ONSET_WINDOW = 20

#: The ON RRP flag's threshold, USD billions: a flag, not the level, because
#: the level scored worse as a linear input in #45.
ON_RRP_FLAG_BELOW_USD_BN = 100.0

#: The TGA change's window: the direct pressure models' (`ml.TGA_CHANGE_ROWS`),
#: one week of panel rows. Restated rather than imported, because `ml` needs
#: the extra and this module does not.
TGA_CHANGE_ROWS = 5

_SOFR = "nyfed_sofr"
_IORB_FIELDS = FEATURE_FIELDS["iorb"]
_EFFR = ("fred_macro_latest_vintage", "DFF")


class Candidate(NamedTuple):
    """One pre-declared input.

    `columns` are the panel columns a declaration adds; `products` the
    direct pressure model's product terms (`ml._PressureDesign`), each a pair
    of declared columns or `tga_change`. `blocked` is why the input is not
    scored, or `None`.
    """

    name: str
    group: str
    definition: str
    columns: Tuple[str, ...]
    products: Tuple[Tuple[str, str], ...] = ()
    blocked: Optional[str] = None


_NMFP_BLOCK = (
    "sec.gov is refused by this environment and no tracked fixture carries "
    "sec_nmfp; the published build also refuses it (refused_columns: a "
    "snapshot_retrieved_at source whose field declares no never_revised "
    "revision policy). A permission block for this item only (#127, step 2)"
)

#: The pre-declared candidates, in the issue's order. Fixed before scoring.
CANDIDATES: Tuple[Candidate, ...] = (
    Candidate(
        "sofr_tail", "registered_unused",
        "SOFR tail dispersion: SOFR_p99 − SOFR_p75, in bp",
        ("sofr_p99_p75_bps",),
    ),
    Candidate(
        "sofr_p1", "registered_unused",
        "SOFR_p1, the 1st percentile of SOFR transactions, in percent",
        ("sofr_p1",),
    ),
    Candidate(
        "sofr_tgcr", "registered_unused",
        "SOFR − TGCR, in bp (cleared and bilateral repo against tri-party)",
        ("sofr_tgcr_bps",),
    ),
    Candidate(
        "bgcr_tgcr", "registered_unused",
        "BGCR − TGCR, in bp",
        ("bgcr_tgcr_bps",),
    ),
    Candidate(
        "dealer_positions", "registered_unused",
        "FR2004 primary-dealer net Treasury positions (PDPOSGST-TOT, USD bn), "
        "weekly, read as-of under nyfed_fr2004's declared lag",
        ("dealer_treasury_position",),
    ),
    Candidate(
        "mmf_net_flows", "registered_unused",
        "SEC N-MFP money-fund net flows (daily)",
        (), blocked=_NMFP_BLOCK,
    ),
    Candidate(
        "mmf_repo_holdings", "registered_unused",
        "SEC N-MFP money-fund repo holdings (monthly)",
        (), blocked=_NMFP_BLOCK,
    ),
    Candidate(
        "settlement_x_tga_change", "registered_unused",
        "Treasury settlement size × TGA change (the TGA's change over 5 panel "
        "rows ending at its as-of read)",
        ("tga_change_5d",),
        products=(("treasury_settlement", "tga_change"),),
    ),
    Candidate(
        "sofr_above_effr_share", "onset_signal",
        "the share of the last 20 business days with SOFR > EFFR (EFFR is the "
        "H.15's DFF, under its declared five-day lag)",
        ("sofr_above_effr_share_20",),
    ),
    Candidate(
        "effr_iorb_change", "onset_signal",
        "the 20-business-day change in EFFR − IORB, in bp (the change, not the level)",
        ("effr_iorb_change_20_bps",),
    ),
    Candidate(
        "sofr_p99_iorb", "onset_signal",
        "SOFR_p99 − IORB, in bp",
        ("sofr_p99_iorb_bps",),
    ),
    Candidate(
        "on_rrp_below_100bn", "onset_signal",
        "an ON RRP < $100bn flag, not the level (on_rrp from the Desk's "
        "operation results, #45)",
        ("on_rrp_below_100bn",),
    ),
    Candidate(
        "srf_take_up_positive", "onset_signal",
        "an SRF take-up > 0 flag (nyfed_srf); 0 before the facility's first "
        "operation on 2021-07-29",
        ("srf_take_up_positive",),
    ),
    Candidate(
        "issuance_x_dealer_positions", "issuance_dealer",
        "net Treasury coupon and bill settlement amount × FR2004 net dealer "
        "positions (treasury_settlement is bills plus coupons, SOMA add-ons "
        "outside it)",
        ("dealer_treasury_position",),
        products=(("treasury_settlement", "dealer_treasury_position"),),
    ),
)

#: The onset signals scored together (#127, step 3): those not blocked.
ONSET_GROUP: Tuple[str, ...] = tuple(
    candidate.name
    for candidate in CANDIDATES
    if candidate.group == "onset_signal" and not candidate.blocked
)

#: Every new column's source fields, for the as-of rule. **Off**: switched on
#: only by the scoring script, never part of `contract.FEATURE_FIELDS`. EFFR
#: is FRED's `DFF` (the H.15 effective federal funds rate), declared
#: `never_revised` with a five-calendar-day lag in `fred_macro_latest_vintage`'s
#: `field_release_lags`, so every column that reads it is read at least that late.
COLUMN_FIELDS: Mapping[str, Tuple[Tuple[str, str], ...]] = {
    "sofr_p99_p75_bps": ((_SOFR, "SOFR_p99"), (_SOFR, "SOFR_p75")),
    "sofr_p1": ((_SOFR, "SOFR_p1"),),
    "sofr_tgcr_bps": ((_SOFR, "SOFR"), ("nyfed_tgcr", "TGCR")),
    "bgcr_tgcr_bps": (("nyfed_bgcr", "BGCR"), ("nyfed_tgcr", "TGCR")),
    "tga_change_5d": FEATURE_FIELDS["tga"],
    "sofr_p99_iorb_bps": ((_SOFR, "SOFR_p99"),) + tuple(_IORB_FIELDS),
    "sofr_above_effr_share_20": ((_SOFR, "SOFR"), _EFFR),
    "effr_iorb_change_20_bps": (_EFFR,) + tuple(_IORB_FIELDS),
    "on_rrp_below_100bn": tuple(ON_RRP_OPERATION_RESULTS_FIELDS),
    "srf_take_up_positive": tuple(SRF_OPERATION_RESULTS_FIELDS),
}


def _get(row: DailyObservation, column: str) -> Optional[float]:
    value = row.values.get(column)
    return None if value is None else float(value)


def _difference_bps(row: DailyObservation, a: str, b: str) -> Optional[float]:
    x, y = _get(row, a), _get(row, b)
    return None if x is None or y is None else (x - y) * 100.0


def _share_above(
    rows: Sequence[DailyObservation], position: int, a: str, b: str, window: int
) -> Optional[float]:
    """The share of the `window` rows ending at `position` with `a > b`, strictly."""

    start = position - window + 1
    if start < 0:
        return None
    above = 0
    for row in rows[start : position + 1]:
        x, y = _get(row, a), _get(row, b)
        if x is None or y is None:
            return None
        above += x > y
    return above / window


def _change(values: Sequence[Optional[float]], position: int, window: int) -> Optional[float]:
    """`values[position] - values[position - window]`, or `None`."""

    if position - window < 0:
        return None
    now, then = values[position], values[position - window]
    return None if now is None or then is None else now - then


def build_columns(rows: Sequence[DailyObservation]) -> List[DailyObservation]:
    """`rows` with every candidate column added, each from its own and earlier rows.

    Reads, where present, `sofr`, `iorb`, `effr`, `sofr_p1`, `sofr_p75`,
    `sofr_p99`, `tgcr`, `bgcr`, `tga`, `on_rrp` and `srf_take_up`. A column whose inputs
    are missing on a row it needs is `None` there; the SRF flag is 0.0 before
    `SRF_INCEPTION`, when the facility did not exist.
    """

    effr_spread = [_difference_bps(row, "effr", "iorb") for row in rows]
    out: List[DailyObservation] = []
    for position, row in enumerate(rows):
        values: Dict[str, Optional[float]] = dict(row.values)
        values["sofr_p99_p75_bps"] = _difference_bps(row, "sofr_p99", "sofr_p75")
        values["sofr_p1"] = _get(row, "sofr_p1")
        values["sofr_tgcr_bps"] = _difference_bps(row, "sofr", "tgcr")
        values["bgcr_tgcr_bps"] = _difference_bps(row, "bgcr", "tgcr")
        values["sofr_p99_iorb_bps"] = _difference_bps(row, "sofr_p99", "iorb")
        tga = [_get(r, "tga") for r in rows[max(0, position - TGA_CHANGE_ROWS) : position + 1]]
        values["tga_change_5d"] = (
            None
            if len(tga) <= TGA_CHANGE_ROWS or tga[0] is None or tga[-1] is None
            else tga[-1] - tga[0]
        )
        on_rrp = _get(row, "on_rrp")
        values["on_rrp_below_100bn"] = (
            None if on_rrp is None else float(on_rrp < ON_RRP_FLAG_BELOW_USD_BN)
        )
        values["srf_take_up_positive"] = _srf_flag(row.date, _get(row, "srf_take_up"))
        values["sofr_above_effr_share_20"] = _share_above(
            rows, position, "sofr", "effr", ONSET_WINDOW
        )
        values["effr_iorb_change_20_bps"] = _change(effr_spread, position, ONSET_WINDOW)
        out.append(DailyObservation(row.date, values))
    return out


def _srf_flag(when: date, take_up: Optional[float]) -> Optional[float]:
    if when < SRF_INCEPTION:
        return 0.0
    return None if take_up is None else float(take_up > 0.0)
