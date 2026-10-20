"""The live-monitoring read (#969): calibration, score and plumbing checks on the live record, reported only.

The live record (`scripts/live_record.py`) is frozen, chained and written before any outcome. Its only scorer,
`scripts/live_score.py`, runs on the pre-registered dates and carries the verdict. This module is the other channel
a model-risk standard separates from it: *monitoring*, which reads outcomes as they print, opens no tier, gives no
verdict and is cited only as a trigger. Nothing here is a comparison in the sense of `docs/decisions/lockbox.md`
**once Eleonora has merged `docs/decisions/live-monitoring.md`**, the decision record that says so. Until then a
read of a locked day refuses (`require_decision_record`, `LookAheadError`); the replay on development days does not
need it, and refuses any day after the study window (`require_development_window`, `LookAheadError`).

A row is one scored target day at one lead: `date`, `outcome` (the realised spread in basis points), `published`
(the five quantiles at `QUANTILE_LEVELS`) and, where the record carries them, `b1` and `b2` on the same levels.
Every statistic is a pure function of rows, so the replay on the tracked development record and a read of a live
record go through the same code. Standard library only.
"""

from __future__ import annotations

import math
from datetime import date, datetime
from pathlib import Path
from typing import Dict, Iterable, List, Mapping, Optional, Sequence

from .contract import QUANTILE_LEVELS
from .metrics import crps_from_quantiles
from .splits import LookAheadError

__all__ = [
    "DECISION_RECORD", "DEV_LAST", "TOO_FEW_DAYS", "band_hits", "chi2_sf", "christoffersen", "crps_ratio",
    "kupiec", "pin_check", "pit_counts", "pit_shares", "report", "require_decision_record",
    "require_development_window", "rolling", "rows_from_records", "staleness", "tail_misses",
]

#: The decision record that opens a read of locked-tier outcomes, a file in `docs/decisions/` and not in `drafts/`.
DECISION_RECORD = "live-monitoring.md"
DECISIONS = Path(__file__).resolve().parents[2] / "docs" / "decisions"
#: The last day the replay reads: the last day before the near-blind tier (`docs/decisions/lockbox.md`).
DEV_LAST = date(2025, 12, 31)
TOO_FEW_DAYS = "too_few_days"
#: What the 6-bin PIT expects in each bin, from the five quantile levels.
PIT_EXPECTED = (0.05, 0.20, 0.25, 0.25, 0.20, 0.05)
THRESHOLDS_STATUS = "proposed thresholds, not decisions (#950 row 8 stays parked for Eleonora)"
STALENESS_SOURCE = "nyfed_sofr"


# -- the gates -----------------------------------------------------------------------------------------------------


def require_decision_record(decisions_dir: Path = DECISIONS) -> None:
    """Refuse a read of live outcomes unless the monitoring decision record is merged.

    The record is the file `DECISION_RECORD` in `docs/decisions/`; a draft under `drafts/` does not count.

    Raises:
        LookAheadError: if the record is not there.
    """

    if not (Path(decisions_dir) / DECISION_RECORD).is_file():
        raise LookAheadError(
            f"the monitoring read of live outcomes needs docs/decisions/{DECISION_RECORD}, merged by Eleonora; "
            f"only a draft under docs/decisions/drafts/ exists, and a draft opens nothing (#969, #256)"
        )


def require_development_window(days: Iterable[date], *, last: date = DEV_LAST) -> None:
    """Refuse a replay day after `last` (2025-12-31): the replay reads development days only.

    Raises:
        LookAheadError: naming the first offending day.
    """

    for day in sorted(days):
        if day > last:
            raise LookAheadError(f"the replay reads no day after {last}; {day} is in a locked tier (#969)")


# -- statistics ----------------------------------------------------------------------------------------------------


def chi2_sf(x: float, df: int) -> float:
    """The chi-square upper tail at `x` for 1 or 2 degrees of freedom."""

    if x <= 0:
        return 1.0
    if df == 1:
        return math.erfc(math.sqrt(x / 2.0))
    if df == 2:
        return math.exp(-x / 2.0)
    raise ValueError("chi2_sf is defined for 1 or 2 degrees of freedom")


def _xlogy(count: float, value: float) -> float:
    return 0.0 if count == 0 else count * math.log(value)


def kupiec(misses: Sequence[bool], expected: float) -> Dict[str, object]:
    """Kupiec's proportion-of-failures test of `misses` against the rate `expected`.

    Raises:
        ValueError: if `expected` is not strictly between 0 and 1, or `misses` is empty.
    """

    if not 0.0 < expected < 1.0:
        raise ValueError("the expected miss rate must be strictly between 0 and 1")
    n = len(misses)
    if n == 0:
        raise ValueError("kupiec needs at least one day")
    x = sum(1 for miss in misses if miss)
    rate = x / n
    ll_null = _xlogy(n - x, 1 - expected) + _xlogy(x, expected)
    ll_alt = _xlogy(n - x, 1 - rate) + _xlogy(x, rate)
    lr = max(0.0, -2.0 * (ll_null - ll_alt))
    return {"n": n, "misses": x, "rate": rate, "expected": expected, "lr": lr, "p_value": chi2_sf(lr, 1)}


def christoffersen(misses: Sequence[bool]) -> Dict[str, object]:
    """Christoffersen's first-order independence test of a miss sequence in date order."""

    counts = {"00": 0, "01": 0, "10": 0, "11": 0}
    for before, after in zip(misses, misses[1:]):
        counts[f"{int(bool(before))}{int(bool(after))}"] += 1
    n00, n01, n10, n11 = counts["00"], counts["01"], counts["10"], counts["11"]
    total = n00 + n01 + n10 + n11
    out = {"transitions": counts, "lr": 0.0, "p_value": 1.0}
    if total == 0 or n01 + n11 == 0 or n01 + n11 == total:
        return out
    pi = (n01 + n11) / total
    ll_null = _xlogy(n00 + n10, 1 - pi) + _xlogy(n01 + n11, pi)
    ll_alt = 0.0
    for stay, move, base in ((n00, n01, n00 + n01), (n10, n11, n10 + n11)):
        if base:
            ll_alt += _xlogy(stay, stay / base) + _xlogy(move, move / base)
    lr = max(0.0, -2.0 * (ll_null - ll_alt))
    out.update(lr=lr, p_value=chi2_sf(lr, 1))
    return out


def band_hits(rows: Sequence[Mapping]) -> List[bool]:
    """Per row, whether the outcome is inside the 90% band: `q05 <= outcome <= q95`."""

    return [row["published"][0] <= row["outcome"] <= row["published"][-1] for row in rows]


def tail_misses(rows: Sequence[Mapping]) -> List[bool]:
    """Per row, whether the outcome is strictly above q95."""

    return [row["outcome"] > row["published"][-1] for row in rows]


def pit_counts(rows: Sequence[Mapping]) -> List[int]:
    """The 6-bin PIT counts: a row's bin is the number of its quantiles strictly below the outcome."""

    counts = [0] * (len(QUANTILE_LEVELS) + 1)
    for row in rows:
        counts[sum(1 for q in row["published"] if q < row["outcome"])] += 1
    return counts


def pit_shares(rows: Sequence[Mapping]) -> Dict[str, object]:
    """The 6-bin PIT as shares, and the share at or below q25 (expected 0.25)."""

    counts = pit_counts(rows)
    total = sum(counts)
    shares = [count / total for count in counts] if total else [None] * len(counts)
    below = (counts[0] + counts[1]) / total if total else None
    return {"days": total, "counts": counts, "shares": shares, "expected": list(PIT_EXPECTED),
            "share_at_or_below_q25": below}


def crps_ratio(rows: Sequence[Mapping], benchmark: str) -> Dict[str, object]:
    """Mean CRPS of the published distribution over the benchmark's mean, on the rows that carry the benchmark.

    `benchmark` is `"b1"` or `"b2"`. Below 1 favours the model. `missing` counts rows without the benchmark.
    """

    model = bench = 0.0
    days = 0
    for row in rows:
        quantiles = row.get(benchmark)
        if quantiles is None:
            continue
        model += crps_from_quantiles(QUANTILE_LEVELS, row["published"], row["outcome"])
        bench += crps_from_quantiles(QUANTILE_LEVELS, quantiles, row["outcome"])
        days += 1
    ratio = model / bench if days and bench > 0 else None
    return {"benchmark": benchmark, "days": days, "missing": len(rows) - days, "ratio": ratio}


# -- the rolling read ----------------------------------------------------------------------------------------------


def _flags(point: Mapping, thresholds: Mapping, coverage_days: int, calibration_days: int) -> List[str]:
    out: List[str] = []
    coverage = point.get(f"coverage_{coverage_days}")
    band = thresholds["band_coverage_60d"]
    if coverage is not None:
        if coverage < band["stop_below"]:
            out.append("band_coverage_stop")
        if coverage < band["amber_below"]:
            out.append("band_coverage_amber")
        elif coverage > band["amber_above"]:
            out.append("band_coverage_amber")
    kupiec_p, christoffersen_p = point.get("kupiec_p"), point.get("christoffersen_p")
    k_limit = thresholds["kupiec_q95_125d"]["amber_p_below"]
    c_limit = thresholds["christoffersen_q95_125d"]["amber_p_below"]
    if kupiec_p is not None and kupiec_p < k_limit:
        out.append("kupiec_amber")
    if christoffersen_p is not None and christoffersen_p < c_limit:
        out.append("christoffersen_amber")
    if kupiec_p is not None and kupiec_p < k_limit and christoffersen_p < c_limit:
        out.append("calibration_stop")
    share = point.get("pit_share_at_or_below_q25")
    low, high = thresholds["pit_share_at_or_below_q25"]["amber_outside"]
    if share is not None and not low <= share <= high:
        out.append("pit_amber")
    ratio = point.get("crps_ratio_b1")
    if ratio is not None:
        if ratio > thresholds["crps_ratio_to_b1_125d"]["stop_above"]:
            out.append("crps_ratio_stop")
        if ratio > thresholds["crps_ratio_to_b1_125d"]["amber_above"]:
            out.append("crps_ratio_amber")
    return out


def rolling(
    rows: Sequence[Mapping], thresholds: Mapping, *, coverage_days: int = 60, calibration_days: int = 125
) -> List[Dict[str, object]]:
    """The read on each day, from the days up to and including it (never a later one).

    A window that is not full leaves its figures `None` and the point labelled `TOO_FEW_DAYS`
    (or `coverage_only` when only the coverage window is full); a point with a window not full is never flagged
    on that window.
    """

    rows = sorted(rows, key=lambda row: row["date"])
    series: List[Dict[str, object]] = []
    for index, row in enumerate(rows):
        point: Dict[str, object] = {"date": row["date"]}
        cover = rows[max(0, index - coverage_days + 1): index + 1]
        calib = rows[max(0, index - calibration_days + 1): index + 1]
        full_cover, full_calib = len(cover) == coverage_days, len(calib) == calibration_days
        point[f"coverage_{coverage_days}"] = sum(band_hits(cover)) / len(cover) if full_cover else None
        if full_calib:
            misses = tail_misses(calib)
            point["kupiec_p"] = kupiec(misses, 0.05)["p_value"]
            point["christoffersen_p"] = christoffersen(misses)["p_value"]
            point["pit_share_at_or_below_q25"] = pit_shares(calib)["share_at_or_below_q25"]
            ratio = crps_ratio(calib, "b1")
            point["crps_ratio_b1"] = ratio["ratio"] if ratio["days"] == calibration_days else None
        else:
            for key in ("kupiec_p", "christoffersen_p", "pit_share_at_or_below_q25", "crps_ratio_b1"):
                point[key] = None
        point["window"] = "full" if full_cover and full_calib else ("coverage_only" if full_cover else TOO_FEW_DAYS)
        point["flags"] = _flags(point, thresholds, coverage_days, calibration_days)
        series.append(point)
    return series


def report(
    rows: Sequence[Mapping], thresholds: Mapping, *, coverage_days: int = 60, calibration_days: int = 125
) -> Dict[str, object]:
    """The read at the newest day, with the series behind it. It decides nothing."""

    series = rolling(rows, thresholds, coverage_days=coverage_days, calibration_days=calibration_days)
    tail = [row for row in sorted(rows, key=lambda row: row["date"])][-calibration_days:]
    return {
        "decides": "nothing",
        "thresholds_status": THRESHOLDS_STATUS,
        "days": len(rows),
        "latest": series[-1] if series else None,
        "calibration_window": {
            "kupiec_q95": kupiec(tail_misses(tail), 0.05) if tail else None,
            "christoffersen_q95": christoffersen(tail_misses(tail)) if tail else None,
            "pit": pit_shares(tail),
            "crps_ratio_b1": crps_ratio(tail, "b1"),
            "crps_ratio_b2": crps_ratio(tail, "b2"),
        },
        "series": series,
    }


# -- the live record -----------------------------------------------------------------------------------------------


def rows_from_records(records: Sequence[Mapping], outcomes: Mapping[date, float], *, lead: int) -> List[Dict]:
    """One row per logged day whose lead-`lead` target day has an outcome in `outcomes`.

    B1 is the record's persistence side; B2 is read from the record's protocol block when it carries one,
    subset to the five levels.

    Raises:
        ValueError: if a record carries no distribution at `lead`.
    """

    rows = []
    for record in records:
        targets = {target["horizon"]: target for target in record["targets"]}
        block = record["distributions"]
        try:
            published = list(block["published"]["quantiles_bps"][str(lead)])
            target = date.fromisoformat(targets[lead]["target_date"])
        except KeyError as error:
            raise ValueError(f"record {record.get('decision_day')} carries no distribution at lead {lead}") from error
        if target not in outcomes:
            continue
        row = {"date": target, "outcome": float(outcomes[target]), "published": published,
               "b1": list(block["persistence"]["quantiles_bps"][str(lead)]), "b2": _b2(record, lead, block["levels"])}
        rows.append(row)
    return rows


def _b2(record: Mapping, lead: int, levels: Sequence[float]) -> Optional[List[float]]:
    protocol = record.get("protocol")
    if not protocol:
        return None
    grid = list(protocol["grid"])
    vector = protocol["benchmarks"]["b2"].get(str(lead), protocol["benchmarks"]["b2"].get(lead))
    if vector is None:
        return None
    return [vector[grid.index(level)] for level in levels]


def _bound(source: Mapping) -> Optional[int]:
    lag = source.get("release_lag")
    if isinstance(lag, Mapping) and "worst_case_calendar_days" in lag:
        return int(lag["worst_case_calendar_days"])
    fields = source.get("field_release_lags")
    if isinstance(fields, Mapping):
        values = [int(v["worst_case_calendar_days"]) for v in fields.values() if "worst_case_calendar_days" in v]
        return max(values) if values else None
    return None


def staleness(record: Mapping, registry: Mapping[str, Mapping]) -> Dict[str, object]:
    """Per source in the record's snapshots, its age at the decision instant against its declared worst-case lag.

    A source with no declared bound is reported with `stale` `None`, not flagged. The panel's last date is read
    against `STALENESS_SOURCE`'s bound.
    """

    instant = datetime.fromisoformat(record["decision_instant"])
    sources = []
    for snapshot in record["inputs"]["snapshots"]:
        retrieved = datetime.fromisoformat(snapshot["retrieved_at"])
        age = (instant.date() - retrieved.astimezone(instant.tzinfo).date()).days
        bound = _bound(registry.get(snapshot["source_id"], {}))
        sources.append({"source_id": snapshot["source_id"], "age_days": age, "bound_days": bound,
                        "stale": None if bound is None else age > bound})
    bound = _bound(registry.get(STALENESS_SOURCE, {}))
    lag = (date.fromisoformat(record["decision_day"]) - date.fromisoformat(record["inputs"]["panel_last_date"])).days
    panel = {"lag_days": lag, "bound_days": bound, "stale": None if bound is None else lag > bound}
    return {"decision_day": record["decision_day"], "sources": sources, "panel": panel}


def pin_check(records: Sequence[Mapping], registered: Iterable[str]) -> Dict[str, object]:
    """The days whose record was made at a code SHA that is not a registered live pin transition."""

    known = set(registered)
    bad = [record["decision_day"] for record in records if record["code"]["pinned_sha"] not in known]
    return {"checked": len(records), "unregistered": bad}
