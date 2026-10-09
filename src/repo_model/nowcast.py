"""A same-day nowcast of the unpublished day (#445).

A forecast for day `T` is made at 16:00 New York time on the panel day before it, `r = T - 1`. At that
instant the latest published SOFR is the day before `r`: the New York Fed publishes each day's rate the
next morning (`nyfed_sofr.release_lag`). The published distribution's median for `T` therefore tracks the
spread of `T - 2`. This module builds, for every panel row `r`, an estimate of the spread of `r` itself
from what is public at the 16:00 decision of `r`, so a forecast of `T` can start from `r`.

**What the nowcast of row `r` may read** (`metadata/nowcast.json`, `metadata/sources_measurement.json`)

* the spread (SOFR - IORB, bp) of row `r - 1` and the one before it: public at 15:00 on `r`;
* the Desk's reverse-repo results for `r` itself, admitted for a day only when every record of the day was
  last written on that date at or before 15:00 New York time (`sameday_on_rrp`): the Desk states no
  publication time, so `lastUpdated`, the last write, is the evidence;
* the day's gross Treasury settlement, a scheduled input already declared in `metadata/sources.json`
  (announced a panel day ahead, at 15:00), and the calendar columns, which are always known.

Same-day Treasury bill rates are *not* read: nothing shows them public before 16:00
(`treasury_bill_rates_sameday` in `metadata/sources_measurement.json`).

**The estimator.** A ridge regression of the spread's one-day change on standardized features, refitted every
`refit_every` rows on an expanding window of pairs `(features of row k, change of row k)` for `k < r`, the
rows whose own spread was public at the decision of `r`. Where the model is not fitted yet, or a feature is
missing, the nowcast is the naive one (the spread of `r - 1`), and the row is counted as a fallback, never
filled. The label guard `check_labels_observable` raises `LookAheadError`.

Standard library only, like the rest of `src/` outside `ml.py`. Off in every published declaration: the
columns are switched on by a track's own run (`scripts/nowcast.py`).
"""

from __future__ import annotations

import hashlib
import json
import math
from dataclasses import dataclass
from datetime import date, datetime, time
from pathlib import Path
from typing import Dict, List, Mapping, Optional, Sequence, Tuple

from .data import DailyObservation
from .splits import LookAheadError

__all__ = [
    "AVAILABLE_BY",
    "COLUMN_FIELDS",
    "FEATURES",
    "NOWCAST_COLUMN",
    "NOWCAST_FIELD",
    "NOWCAST_SOURCE_ID",
    "RRP_COLUMN",
    "SAMEDAY_FIELD",
    "SAMEDAY_SOURCE_ID",
    "Declaration",
    "Ridge",
    "WalkForward",
    "best_lag",
    "check_labels_observable",
    "fit_ridge",
    "lag_correlations",
    "load_declaration",
    "load_operations",
    "parse_declaration",
    "sameday_on_rrp",
    "turning_points",
    "walk_forward",
    "with_nowcast",
]

DEFAULT_DECLARATION = Path(__file__).resolve().parents[2] / "metadata" / "nowcast.json"

SAMEDAY_SOURCE_ID = "nyfed_on_rrp_sameday"
SAMEDAY_FIELD = "reverse_repo_total_accepted_sameday"
NOWCAST_SOURCE_ID = "spread_nowcast"
NOWCAST_FIELD = "spread_nowcast_bps"
#: The panel column of the same-day reverse repo, USD billions; empty where no evidence admits the day.
RRP_COLUMN = "on_rrp_sameday"
#: The panel column the models read: the primary candidate's nowcast, bp.
NOWCAST_COLUMN = "spread_nowcast_bps"
#: The latest `lastUpdated` clock time (New York) that admits a reverse-repo day; also the declared instant.
AVAILABLE_BY = time(15, 0)

#: Each column's source fields, for the as-of rule. **Off**: never part of `contract.FEATURE_FIELDS`.
COLUMN_FIELDS: Mapping[str, Tuple[Tuple[str, str], ...]] = {
    RRP_COLUMN: ((SAMEDAY_SOURCE_ID, SAMEDAY_FIELD),),
    NOWCAST_COLUMN: ((NOWCAST_SOURCE_ID, NOWCAST_FIELD),),
}

_REVERSE_REPO = "Reverse Repo"


# -- the same-day reverse repo ------------------------------------------------


def sameday_on_rrp(operations: Sequence[Mapping[str, object]]) -> Tuple[Dict[date, float], Dict[date, str]]:
    """`({date: USD billions}, {date: reason})` for the Desk's reverse repos, admitted by their last write.

    The value of a date is `totalAmtAccepted` summed over every `Reverse Repo` operation of the
    `operationDate`, in billions, as `ingest._nyfed_on_rrp_rows` sums it. It is admitted only if every
    one of the date's records has a `lastUpdated` on that same date at or before `AVAILABLE_BY`: a
    record cannot have been written later than it was first written, so it was public by then. A date with
    a record written on a later date, after `AVAILABLE_BY`, or with no readable stamp is excluded and
    given a reason; nothing is filled.

    Raises `ValueError` on a reverse-repo operation with no valid date or no numeric amount.
    """

    totals: Dict[date, int] = {}
    reason: Dict[date, str] = {}
    for number, record in enumerate(operations, start=1):
        if record.get("operationType") != _REVERSE_REPO:
            continue
        try:
            day = date.fromisoformat(str(record["operationDate"]))
        except (KeyError, ValueError) as exc:
            raise ValueError(f"reverse-repo operation {number} has no valid operationDate") from exc
        accepted = record.get("totalAmtAccepted")
        if isinstance(accepted, bool) or not isinstance(accepted, (int, float)):
            raise ValueError(f"reverse-repo operation {number} on {day} has no numeric totalAmtAccepted ({accepted!r})")
        totals[day] = totals.get(day, 0) + accepted
        try:
            written = datetime.fromisoformat(str(record["lastUpdated"]))
        except (KeyError, ValueError):
            reason.setdefault(day, "no readable lastUpdated")
            continue
        if written.date() != day:
            reason.setdefault(day, "written again on a later date")
        elif written.time() > AVAILABLE_BY:
            reason.setdefault(day, "written after the declared time")
    values = {day: total / 1e9 for day, total in totals.items() if day not in reason}
    return values, {day: why for day, why in reason.items()}


def load_operations(directory: Path) -> List[Mapping[str, object]]:
    """Every operation in the snapshot payloads under `directory`, each checked against its manifest."""

    out: List[Mapping[str, object]] = []
    for manifest_path in sorted(Path(directory).glob("*.manifest.json")):
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        payload_path = manifest_path.with_name(manifest_path.name[: -len(".manifest.json")])
        payload = payload_path.read_bytes()
        if hashlib.sha256(payload).hexdigest() != manifest["sha256"]:
            raise ValueError(f"{payload_path} does not match its manifest checksum")
        out.extend(json.loads(payload)["repo"]["operations"])
    return out


# -- the ridge ----------------------------------------------------------------


@dataclass(frozen=True)
class Ridge:
    """A fitted ridge on standardized features, intercept unpenalized."""

    means: Tuple[float, ...]
    scales: Tuple[float, ...]
    weights: Tuple[float, ...]
    intercept: float

    def predict(self, features: Sequence[float]) -> float:
        total = self.intercept
        for value, mean, scale, weight in zip(features, self.means, self.scales, self.weights):
            total += weight * (value - mean) / scale
        return total


def _solve(matrix: List[List[float]], rhs: List[float]) -> List[float]:
    """Gauss-Jordan with partial pivoting; the matrix is positive definite here (a penalty on the diagonal)."""

    size = len(rhs)
    a = [row[:] + [rhs[i]] for i, row in enumerate(matrix)]
    for col in range(size):
        pivot = max(range(col, size), key=lambda r: abs(a[r][col]))
        if abs(a[pivot][col]) < 1e-14:
            raise ValueError("the ridge system is singular")
        a[col], a[pivot] = a[pivot], a[col]
        divisor = a[col][col]
        a[col] = [v / divisor for v in a[col]]
        for r in range(size):
            if r != col and a[r][col] != 0.0:
                factor = a[r][col]
                a[r] = [v - factor * w for v, w in zip(a[r], a[col])]
    return [a[i][size] for i in range(size)]


def fit_ridge(x: Sequence[Sequence[float]], y: Sequence[float], *, penalty: float) -> Ridge:
    """Ridge regression of `y` on the columns of `x`, each standardized by its own mean and standard deviation.

    A column with no variance has scale 1 and weight 0. Raises `ValueError` on no rows or rows of unequal
    length.
    """

    n = len(y)
    if n == 0 or len(x) != n:
        raise ValueError("a ridge needs at least one row and one target per row")
    width = len(x[0])
    if any(len(row) != width for row in x):
        raise ValueError("the rows of a ridge differ in length")
    mean_y = sum(y) / n
    means = tuple(sum(row[j] for row in x) / n for j in range(width))
    scales = []
    for j in range(width):
        variance = sum((row[j] - means[j]) ** 2 for row in x) / n
        scales.append(math.sqrt(variance) if variance > 1e-24 else 1.0)
    z = [[(row[j] - means[j]) / scales[j] for j in range(width)] for row in x]
    gram = [[sum(r[i] * r[j] for r in z) + (penalty if i == j else 0.0) for j in range(width)] for i in range(width)]
    moment = [sum(r[j] * (target - mean_y) for r, target in zip(z, y)) for j in range(width)]
    weights = _solve(gram, moment) if width else []
    return Ridge(means, tuple(scales), tuple(weights), mean_y)


# -- the declaration ----------------------------------------------------------

#: The features a candidate may name, with the panel columns each reads (documented in the declaration).
FEATURES = (
    "spread_prev_level_bp",
    "spread_prev_change_bp",
    "rrp_level_tn",
    "rrp_change_tn",
    "settlement_100bn",
    "quarter_end",
    "tax_date",
    "month_end_window",
)


@dataclass(frozen=True)
class Candidate:
    name: str
    role: str
    features: Tuple[str, ...]


@dataclass(frozen=True)
class Declaration:
    candidates: Mapping[str, Candidate]
    primary: str
    penalty: float
    min_pairs: int
    refit_every: int
    minimum_move_bp: float
    raw: Mapping[str, object]


def parse_declaration(document: Mapping[str, object]) -> Declaration:
    """The nowcast declaration, checked. Raises `ValueError` on an undefined feature or an undeclared primary."""

    block = document["nowcast"]
    candidates: Dict[str, Candidate] = {}
    for name, spec in block["candidates"].items():
        features = tuple(spec["features"])
        unknown = [f for f in features if f not in FEATURES]
        if unknown:
            raise ValueError(f"candidate {name} names undefined features {unknown}")
        candidates[name] = Candidate(name, str(spec["role"]), features)
    primary = str(block["primary"])
    if primary not in candidates:
        raise ValueError(f"the primary nowcast {primary!r} is not a declared candidate")
    penalty = float(block["ridge_penalty"])
    if penalty < 0:
        raise ValueError("the ridge penalty is negative")
    return Declaration(
        candidates=candidates,
        primary=primary,
        penalty=penalty,
        min_pairs=int(block["min_pairs"]),
        refit_every=int(block["refit_every"]),
        minimum_move_bp=float(document["turning_points"]["minimum_move_bp"]),
        raw=document,
    )


def load_declaration(path: Path = DEFAULT_DECLARATION) -> Declaration:
    return parse_declaration(json.loads(Path(path).read_text(encoding="utf-8")))


# -- the walk-forward ---------------------------------------------------------


def _number(row: DailyObservation, column: str) -> Optional[float]:
    value = row.values.get(column)
    return None if value is None else float(value)


def _feature_values(rows: Sequence[DailyObservation], spreads: Sequence[float], r: int, names: Sequence[str]) -> Optional[List[float]]:
    """The features of row `r`, or `None` if any is missing. Reads the spreads of `r - 1` and earlier only."""

    if r < 2:
        return None
    row = rows[r]
    out: List[float] = []
    for name in names:
        if name == "spread_prev_level_bp":
            value: Optional[float] = spreads[r - 1]
        elif name == "spread_prev_change_bp":
            value = spreads[r - 1] - spreads[r - 2]
        elif name == "rrp_level_tn":
            level = _number(row, RRP_COLUMN)
            value = None if level is None else level / 1000.0
        elif name == "rrp_change_tn":
            level, before = _number(row, RRP_COLUMN), _number(rows[r - 1], RRP_COLUMN)
            value = None if level is None or before is None else (level - before) / 1000.0
        elif name == "settlement_100bn":
            amount = _number(row, "treasury_settlement")
            value = None if amount is None else amount / 100.0
        elif name == "quarter_end":
            value = _number(row, "quarter_end")
        elif name == "tax_date":
            value = _number(row, "tax_date")
        elif name == "month_end_window":
            days = _number(row, "days_to_month_end")
            value = None if days is None else (1.0 if days <= 2.0 else 0.0)
        else:  # pragma: no cover - parse_declaration refuses it
            raise ValueError(f"undefined feature {name!r}")
        if value is None:
            return None
        out.append(value)
    return out


def check_labels_observable(pair_rows: Sequence[int], *, origin: int) -> None:
    """Raise `LookAheadError` if a training pair's target row is not before `origin`.

    The spread of row `k` is public at 15:00 on the next row, so at the decision of row `origin` the
    targets of rows `k < origin` are known and the target of `origin` itself is not.
    """

    for pair in pair_rows:
        if pair >= origin:
            raise LookAheadError(
                f"the fit for the nowcast of row {origin} uses the target of row {pair}, "
                f"which is not public at that row's decision"
            )


@dataclass(frozen=True)
class WalkForward:
    """`values[r]` is the nowcast of row `r` (`None` for row 0); `status[r]` says what produced it."""

    values: Tuple[Optional[float], ...]
    status: Tuple[str, ...]
    first_fitted: Optional[int]
    refits: Tuple[int, ...]
    counts: Mapping[str, int]


def walk_forward(
    rows: Sequence[DailyObservation],
    features: Sequence[str],
    *,
    penalty: float,
    min_pairs: int,
    refit_every: int,
) -> WalkForward:
    """The nowcast of every row, each from its own decision instant's information.

    The change of the spread of row `k` is regressed on `features` of row `k`. The model in force at row
    `r` was fitted at the last refit row `b <= r` on the pairs of rows `k < b`, with every feature present.
    The first refit is at the first row with `min_pairs` such pairs; later ones follow every `refit_every`
    rows. A row before the first refit, or with a missing feature, gets the naive nowcast, the spread of
    row `r - 1`. With no features the nowcast is the naive one on every row.
    """

    n = len(rows)
    spreads = [row.spread_bps for row in rows]
    names = tuple(features)
    values: List[Optional[float]] = [None] * n
    status: List[str] = ["none"] * n
    refits: List[int] = []
    usable: List[int] = []
    if names:
        usable = [k for k in range(2, n) if _feature_values(rows, spreads, k, names) is not None]
    model: Optional[Ridge] = None
    first_fitted: Optional[int] = None
    next_refit: Optional[int] = None
    cursor = 0
    for r in range(1, n):
        if not names:
            values[r], status[r] = spreads[r - 1], "naive"
            continue
        while cursor < len(usable) and usable[cursor] < r:
            cursor += 1
        if first_fitted is None and cursor >= min_pairs:
            first_fitted, next_refit = r, r
        if next_refit is not None and r == next_refit:
            pairs = usable[:cursor]
            check_labels_observable(pairs, origin=r)
            x = [_feature_values(rows, spreads, k, names) for k in pairs]
            y = [spreads[k] - spreads[k - 1] for k in pairs]
            model = fit_ridge(x, y, penalty=penalty)
            refits.append(r)
            next_refit = r + refit_every
        if model is None:
            values[r], status[r] = spreads[r - 1], "naive: not fitted"
            continue
        x_r = _feature_values(rows, spreads, r, names)
        if x_r is None:
            values[r], status[r] = spreads[r - 1], "naive: input missing"
            continue
        values[r], status[r] = spreads[r - 1] + model.predict(x_r), "model"
    counts: Dict[str, int] = {}
    for label in status:
        counts[label] = counts.get(label, 0) + 1
    return WalkForward(tuple(values), tuple(status), first_fitted, tuple(refits), counts)


def with_nowcast(
    rows: Sequence[DailyObservation],
    reverse_repo: Mapping[date, float],
    declaration: Declaration,
) -> Tuple[List[DailyObservation], Dict[str, WalkForward]]:
    """`rows` with the same-day reverse repo, every candidate's nowcast and the primary as `NOWCAST_COLUMN`.

    The candidates are columns `nowcast_<name>`; `NOWCAST_COLUMN` is the primary's. Returns the rows and
    each candidate's walk.
    """

    seeded = []
    for row in rows:
        values = dict(row.values)
        values[RRP_COLUMN] = reverse_repo.get(row.date)
        seeded.append(DailyObservation(row.date, values))
    walks = {
        name: walk_forward(
            seeded, spec.features, penalty=declaration.penalty, min_pairs=declaration.min_pairs,
            refit_every=declaration.refit_every,
        )
        for name, spec in declaration.candidates.items()
    }
    out = []
    for position, row in enumerate(seeded):
        values = dict(row.values)
        for name, walk in walks.items():
            values[f"nowcast_{name}"] = walk.values[position]
        values[NOWCAST_COLUMN] = walks[declaration.primary].values[position]
        out.append(DailyObservation(row.date, values))
    return out, walks


# -- measures -----------------------------------------------------------------


def turning_points(series: Sequence[float], *, minimum_move: float) -> List[Optional[bool]]:
    """Whether each point is a peak or trough with moves of at least `minimum_move` into and out of it.

    `None` at the first and last point, which have a neighbour missing on one side. The label uses the
    next point, and picks days to score; it is never an input of a forecast.
    """

    out: List[Optional[bool]] = [None] * len(series)
    for t in range(1, len(series) - 1):
        into, out_of = series[t] - series[t - 1], series[t + 1] - series[t]
        out[t] = abs(into) >= minimum_move and abs(out_of) >= minimum_move and into * out_of < 0
    return out


def _correlation(a: Sequence[float], b: Sequence[float]) -> Optional[float]:
    n = len(a)
    if n < 3:
        return None
    ma, mb = sum(a) / n, sum(b) / n
    va = sum((x - ma) ** 2 for x in a)
    vb = sum((y - mb) ** 2 for y in b)
    if va <= 0 or vb <= 0:
        return None
    return sum((x - ma) * (y - mb) for x, y in zip(a, b)) / math.sqrt(va * vb)


def lag_correlations(
    medians: Sequence[float], actual: Sequence[float], days: Sequence[int], *, lags: Sequence[int]
) -> Dict[int, Optional[float]]:
    """`{k: Pearson correlation of the median of day T with the actual spread of day T - k}` over `days`.

    `medians[i]` is the forecast median of `days[i]`, an index into `actual`. A day whose `T - k` falls
    outside `actual` is dropped at that `k`.
    """

    out: Dict[int, Optional[float]] = {}
    for k in lags:
        pairs = [(m, actual[t - k]) for m, t in zip(medians, days) if 0 <= t - k < len(actual)]
        out[k] = _correlation([p[0] for p in pairs], [p[1] for p in pairs])
    return out


def best_lag(table: Mapping[int, Optional[float]]) -> int:
    """The lag with the highest correlation; the smaller lag in a tie."""

    scored = [(corr, -k) for k, corr in table.items() if corr is not None]
    if not scored:
        raise ValueError("no lag has a correlation")
    return -max(scored)[1]
