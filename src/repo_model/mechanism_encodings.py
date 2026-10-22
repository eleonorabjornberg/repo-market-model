"""Mechanism-consistent encodings of `gbm_funding`'s raw-level inputs (#1029, H5 step 3; Lens D of #958).

A measurement module, not a published declaration: every column here is **off** in every published declaration
(`contract.FEATURE_FIELDS` does not carry them; `switched_on` adds them for one run). A tree fitted on a raw level learns
cut-points of one regime that never recur (the 4-week bill level correlates +0.12 with the next-day spread in 2018-19 and -0.46
in 2024; reserves were $1.4-1.7tn in the 2019 stress and $2.8-3.5tn in the 2025 stress; `sofr_volume` tripled). Each level is
replaced by the quantity the mechanism acts on:

* `tbill_4w_less_iorb_bps`, `tbill_13w_less_iorb_bps`: the bill's coupon-equivalent yield less IORB, in bp. Bill cheapness
  relative to the policy rate is what pulls money-fund cash out of repo.
* `sofr_less_p25_bps`, `p75_less_sofr_bps`: SOFR less its 25th percentile and its 75th percentile less SOFR, in bp, the width of
  the day's distribution either side of the rate; the percentile *levels* track the policy rate.
* `sofr_volume_to_median`: SOFR volume over the median of the last `WINDOW_ROWS` panel rows (a year), at least `MINIMUM_ROWS`
  present, the row itself included.
* `reserves_to_median`: reserve balances over the median of the same window. Reserves as a ratio to their own trailing year
  keeps the publication instant of the reserves; the H7 ratio to commercial banks' total assets would add the H.8 (about ten
  days back) as a slower leg, which the directive's "same publication instants" excludes (marked question on the pull request).

**No new publication instant.** Each column is a function of its own panel row and earlier rows. Its source fields
(`COLUMN_FIELDS`) are the union of the fields its constituents are declared on, so `asof.InformationRule` reads it at the latest
row on which every constituent was public, which is the row of the slowest constituent, and applies both guards. An earlier row
is public before a later one, so the trailing median adds no instant. `InformationRule`, `contract` and the registry are
unchanged. Stdlib only.
"""

from __future__ import annotations

from contextlib import contextmanager
from types import MappingProxyType
from typing import Dict, Iterator, List, Mapping, Optional, Sequence, Tuple

from . import contract
from .data import DailyObservation

__all__ = [
    "COLUMN_FIELDS",
    "ENCODED",
    "MINIMUM_ROWS",
    "WINDOW_ROWS",
    "build_columns",
    "encode_features",
    "switched_on",
]

#: A year of panel rows, and the fewest present values a trailing median may stand on.
WINDOW_ROWS = 250
MINIMUM_ROWS = 20

#: raw level -> its encoding.
ENCODED: Mapping[str, str] = MappingProxyType(
    {
        "tbill_4w": "tbill_4w_less_iorb_bps",
        "tbill_13w": "tbill_13w_less_iorb_bps",
        "sofr_p25": "sofr_less_p25_bps",
        "sofr_p75": "p75_less_sofr_bps",
        "sofr_volume": "sofr_volume_to_median",
        "reserve_balances": "reserves_to_median",
    }
)

_IORB = tuple(contract.FEATURE_FIELDS["iorb"])
_SOFR = tuple(contract.FEATURE_FIELDS["sofr"])
_BILL_4W = tuple(contract.FEATURE_FIELDS["tbill_4w"])
_BILL_13W = tuple(contract.FEATURE_FIELDS["tbill_13w"])
_P25 = tuple(contract.FEATURE_FIELDS["sofr_p25"])
_P75 = tuple(contract.FEATURE_FIELDS["sofr_p75"])
_VOLUME = tuple(contract.FEATURE_FIELDS["sofr_volume"])
_RESERVES = tuple(contract.FEATURE_FIELDS["reserve_balances"])

#: Every column's source fields for the as-of rule: the union of its constituents'. **Off** in every published declaration.
COLUMN_FIELDS: Mapping[str, Tuple[Tuple[str, str], ...]] = MappingProxyType(
    {
        "tbill_4w_less_iorb_bps": _BILL_4W + _IORB,
        "tbill_13w_less_iorb_bps": _BILL_13W + _IORB,
        "sofr_less_p25_bps": _SOFR + _P25,
        "p75_less_sofr_bps": _P75 + _SOFR,
        "sofr_volume_to_median": _VOLUME,
        "reserves_to_median": _RESERVES,
    }
)


def _get(row: DailyObservation, column: str) -> Optional[float]:
    value = row.values.get(column)
    return None if value is None else float(value)


def _bp(upper: Optional[float], lower: Optional[float]) -> Optional[float]:
    return None if upper is None or lower is None else (upper - lower) * 100.0


def _median(values: Sequence[float]) -> float:
    ordered = sorted(values)
    mid = len(ordered) // 2
    return ordered[mid] if len(ordered) % 2 else (ordered[mid - 1] + ordered[mid]) / 2.0


def _causal_median(series: Sequence[Optional[float]], position: int) -> Optional[float]:
    """The median of the present values among the last `WINDOW_ROWS` rows ending at `position`, or `None` with fewer than `MINIMUM_ROWS`."""

    start = max(0, position - WINDOW_ROWS + 1)
    window = [v for v in series[start : position + 1] if v is not None]
    return _median(window) if len(window) >= MINIMUM_ROWS else None


def _ratio(value: Optional[float], median: Optional[float]) -> Optional[float]:
    if value is None or median is None or not median > 0.0:
        return None
    return value / median


def build_columns(rows: Sequence[DailyObservation]) -> List[DailyObservation]:
    """`rows` with the six encoded columns added, each from its own and earlier rows. A column whose inputs are missing on a row is `None` there.

    Reads `sofr`, `iorb`, `sofr_p25`, `sofr_p75`, `sofr_volume`, `reserve_balances`, `tbill_4w` and `tbill_13w`, as the panel carries them (percent;
    volume and reserves in their own units). The rows given are not changed.
    """

    volumes = [_get(r, "sofr_volume") for r in rows]
    reserves = [_get(r, "reserve_balances") for r in rows]
    out: List[DailyObservation] = []
    for position, row in enumerate(rows):
        values: Dict[str, Optional[float]] = dict(row.values)
        sofr, iorb = _get(row, "sofr"), _get(row, "iorb")
        values["tbill_4w_less_iorb_bps"] = _bp(_get(row, "tbill_4w"), iorb)
        values["tbill_13w_less_iorb_bps"] = _bp(_get(row, "tbill_13w"), iorb)
        values["sofr_less_p25_bps"] = _bp(sofr, _get(row, "sofr_p25"))
        values["p75_less_sofr_bps"] = _bp(_get(row, "sofr_p75"), sofr)
        values["sofr_volume_to_median"] = _ratio(volumes[position], _causal_median(volumes, position))
        values["reserves_to_median"] = _ratio(reserves[position], _causal_median(reserves, position))
        out.append(DailyObservation(row.date, values))
    return out


def encode_features(features: Sequence[str]) -> Tuple[str, ...]:
    """`features` with each raw level replaced, in place, by its encoding; every other name is kept."""

    return tuple(ENCODED.get(name, name) for name in features)


@contextmanager
def switched_on() -> Iterator[None]:
    """`COLUMN_FIELDS` added to `contract.FEATURE_FIELDS` and `FEATURE_SOURCES` for one run, restored on the way out (raise or return)."""

    saved = contract.FEATURE_FIELDS, contract.FEATURE_SOURCES
    contract.FEATURE_FIELDS = MappingProxyType({**contract.FEATURE_FIELDS, **COLUMN_FIELDS})
    contract.FEATURE_SOURCES = MappingProxyType(
        {
            **contract.FEATURE_SOURCES,
            **{column: tuple(sorted({source for source, _field in pairs})) for column, pairs in COLUMN_FIELDS.items()},
        }
    )
    try:
        yield
    finally:
        contract.FEATURE_FIELDS, contract.FEATURE_SOURCES = saved
