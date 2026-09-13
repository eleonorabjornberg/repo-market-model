"""Reading a `--tail gpd` exceedance record: states, ceilings and zeros (B44).

B43 measured the fitted tail's ceiling over the 2039 folds of a rescore, with
scripts kept in a gitignored folder. This module is that analysis made
importable and tested. It changes nothing a model does and writes no record.

Two inputs:

* **The record**, as `baseline.exceedance_backtest_document` writes it:
  `declaration.taus_bp` and `folds.tail`, one tail account per fold.
* **The per-fold knots**, which the record does not carry: the law's value at
  the top declared quantile, `Q(top)`, and the probabilities the fold scored.
  `refit_knots` gets them by refitting the chosen folds exactly as
  `baseline.rolling_exceedance_backtest` does, with `predict_stress` wrapped
  and not replaced (`capture_knots`). `check_knots` refuses knots whose tail
  accounts are not the record's.

**The ceiling is a level, the excess is not.** `upper_endpoint_excess` is
measured above the threshold the tail is attached at, which is `Q(top)` for
that fold. The ceiling in basis points is `Q(top) + upper_endpoint_excess`.
Comparing the bare excess to a tau compares an excess with a level: B43 found
that it refuses 62 folds at 50 bp where the level comparison refuses 48.

Stdlib only. `repo_model.ml` is reached inside functions, as
`tests/test_dependency_boundary.py` requires of every core module.
"""

from __future__ import annotations

from contextlib import contextmanager
from datetime import time
from typing import Any, Dict, Iterator, List, Mapping, Optional, Sequence

from .baseline import _derive_purge, _feature_index, _reads_purge_days
from .splits import rolling_origin

__all__ = [
    "absolute_ceilings",
    "brier_by_tau",
    "capture_knots",
    "ceilings_at_or_below_taus",
    "check_knots",
    "refit_knots",
    "state_counts",
    "top_quantiles",
    "zero_forecasts_on_events",
]


def _taus(record: Mapping[str, Any]) -> List[float]:
    return [float(tau) for tau in record["declaration"]["taus_bp"]]


def _tail_entries(record: Mapping[str, Any]) -> List[Mapping[str, Any]]:
    """`folds.tail`, refused when absent or not one entry per fold."""

    folds = record["folds"]
    if "tail" not in folds:
        raise ValueError(
            "the record has no folds.tail; it is not a --tail run, or it was "
            "written before tail accounts were recorded"
        )
    entries = folds["tail"]
    if len(entries) != folds["count"]:
        raise ValueError(
            f"folds.tail has {len(entries)} entries for {folds['count']} folds"
        )
    return list(entries)


def state_counts(record: Mapping[str, Any]) -> Dict[str, Any]:
    """Folds per tail state, and how many fitted folds have no endpoint.

    `states` has every one of `ml.TAIL_STATES` as a key, zero where none
    occurred, so a record written before a state existed reads as zero of it.
    `fitted_no_endpoint` counts fitted folds at `xi >= 0`, and
    `fitted_with_endpoint` those that carry `upper_endpoint_excess`.

    Raises:
        ValueError: a state that is not one of `ml.TAIL_STATES`, or a fitted
            entry whose endpoint key does not agree with the sign of its `xi`.
    """

    from . import ml

    states = {state: 0 for state in ml.TAIL_STATES}
    no_endpoint = with_endpoint = 0
    for entry in _tail_entries(record):
        state = entry["state"]
        if state not in states:
            raise ValueError(
                f"{entry['scored_date']}: unknown tail state {state!r}; "
                f"expected one of {ml.TAIL_STATES}"
            )
        states[state] += 1
        if state != "fitted":
            continue
        has_endpoint = "upper_endpoint_excess" in entry
        if has_endpoint != (entry["xi"] < 0.0):
            raise ValueError(
                f"{entry['scored_date']}: xi {entry['xi']!r} and the endpoint "
                f"key disagree; a negative shape has an endpoint and only it does"
            )
        if has_endpoint:
            with_endpoint += 1
        else:
            no_endpoint += 1
    return {
        "states": states,
        "fitted": states["fitted"],
        "fitted_no_endpoint": no_endpoint,
        "fitted_with_endpoint": with_endpoint,
    }


def top_quantiles(knots: Sequence[Mapping[str, Any]]) -> Dict[str, float]:
    """`scored_date -> Q(top)` from `refit_knots`' output."""

    return {knot["scored_date"]: knot["q_top"] for knot in knots}


def absolute_ceilings(
    record: Mapping[str, Any], q_top: Mapping[str, float]
) -> Dict[str, float]:
    """`scored_date -> Q(top) + upper_endpoint_excess` for each fold with an endpoint.

    The level in basis points above which the fold's tail gives probability
    exactly zero. Folds without an endpoint have no ceiling and no key.

    Raises:
        ValueError: `q_top` has no value for a fold that has an endpoint.
    """

    ceilings: Dict[str, float] = {}
    for entry in _tail_entries(record):
        if "upper_endpoint_excess" not in entry:
            continue
        when = entry["scored_date"]
        if when not in q_top:
            raise ValueError(f"{when}: no Q(top) for a fold with an endpoint")
        ceilings[when] = q_top[when] + entry["upper_endpoint_excess"]
    return ceilings


def ceilings_at_or_below_taus(
    record: Mapping[str, Any],
    q_top: Mapping[str, float],
    taus: Optional[Sequence[float]] = None,
) -> Dict[float, int]:
    """Per tau, the folds whose absolute ceiling is at or below it.

    Such a fold gives that tau's exceedance probability exactly zero. `taus`
    defaults to the record's own `declaration.taus_bp`.
    """

    ceilings = absolute_ceilings(record, q_top)
    family = _taus(record) if taus is None else [float(tau) for tau in taus]
    return {
        tau: sum(1 for ceiling in ceilings.values() if ceiling <= tau)
        for tau in family
    }


def zero_forecasts_on_events(
    record: Mapping[str, Any], knots: Sequence[Mapping[str, Any]]
) -> Dict[str, List[Dict[str, Any]]]:
    """Fold-tau cells whose forecast is exactly zero and whose event happened, by state.

    An event is `realized_bps > tau`, the contract's strict inequality. Every
    one of `ml.TAIL_STATES` is a key. Each cell names `scored_date`, `tau_bp`
    and `realized_bps`. Such a cell is where the log score is minus infinity.

    Raises:
        ValueError: the knots are not exactly the record's folds (see
            `check_knots`).
    """

    from . import ml

    check_knots(record, knots, require_all=True)
    taus = _taus(record)
    by_date = {knot["scored_date"]: knot for knot in knots}
    cells: Dict[str, List[Dict[str, Any]]] = {state: [] for state in ml.TAIL_STATES}
    for entry in _tail_entries(record):
        knot = by_date[entry["scored_date"]]
        for tau, probability in zip(taus, knot["probabilities"]):
            if probability == 0.0 and knot["realized_bps"] > tau:
                cells[entry["state"]].append(
                    {
                        "scored_date": entry["scored_date"],
                        "tau_bp": tau,
                        "realized_bps": knot["realized_bps"],
                    }
                )
    return cells


def check_knots(
    record: Mapping[str, Any],
    knots: Sequence[Mapping[str, Any]],
    *,
    require_all: bool = False,
) -> None:
    """Refuse knots that are not the fits the record scored.

    Each knot's `tail_account` must equal its fold's `folds.tail` entry, and
    it must carry one probability per declared tau. With `require_all`, the
    knots must cover exactly the record's folds.

    Raises:
        ValueError: on the first disagreement, naming the fold.
    """

    entries = {entry["scored_date"]: entry for entry in _tail_entries(record)}
    taus = _taus(record)
    seen = set()
    for knot in knots:
        when = knot["scored_date"]
        if when not in entries:
            raise ValueError(f"{when}: a knot for a fold the record does not have")
        if when in seen:
            raise ValueError(f"{when}: two knots for one fold")
        seen.add(when)
        expected = {k: v for k, v in entries[when].items() if k != "scored_date"}
        if dict(knot["tail_account"] or {}) != expected:
            raise ValueError(f"{when}: the refit is not the fit the record scored")
        if len(knot["probabilities"]) != len(taus):
            raise ValueError(
                f"{when}: {len(knot['probabilities'])} probabilities for "
                f"{len(taus)} declared taus"
            )
    if require_all and seen != set(entries):
        raise ValueError(
            f"the knots cover {len(seen)} of the record's {len(entries)} folds"
        )


def brier_by_tau(
    record: Mapping[str, Any], knots: Sequence[Mapping[str, Any]]
) -> Dict[float, float]:
    """Per tau, the Brier score of the knots' probabilities, in fold order.

    Summed the way `metrics.brier_score` sums, in the record's fold order, so
    a refit that is the scored run reproduces `metrics.by_tau[*].brier` to the
    bit.
    """

    check_knots(record, knots, require_all=True)
    by_date = {knot["scored_date"]: knot for knot in knots}
    ordered = [by_date[entry["scored_date"]] for entry in _tail_entries(record)]
    return {
        tau: sum(
            (knot["probabilities"][position] - (1 if knot["realized_bps"] > tau else 0))
            ** 2
            for knot in ordered
        )
        / len(ordered)
        for position, tau in enumerate(_taus(record))
    }


@contextmanager
def capture_knots() -> Iterator[List[Dict[str, Any]]]:
    """Wrap `FittedGradientBoostedQuantiles.predict_stress` and record each call.

    The original runs and its return value is passed through untouched, so
    anything scored inside the block is scored as without it. Each call
    appends `values`, `levels`, `q_top` (`values[-2]`, the knot at the top
    declared level), `tail_account` and `probabilities`. The knots come from
    `law_knots`, which shares `predict_stress`'s memoised evaluation of the
    row, so they are the knots the probabilities were read off. The class
    attribute is restored on exit, including on an exception.
    """

    from . import ml

    captured: List[Dict[str, Any]] = []
    cls = ml.FittedGradientBoostedQuantiles
    original = cls.predict_stress

    def wrapped(self, feature_row, taus=None):
        probabilities = original(self, feature_row, taus)
        values, levels = self.law_knots(feature_row)
        account = self.tail_account
        captured.append(
            {
                "feature_date": feature_row.date.isoformat(),
                "values": list(values),
                "levels": list(levels),
                "q_top": values[-2],
                "tail_account": None if account is None else dict(account),
                "probabilities": list(probabilities),
            }
        )
        return probabilities

    cls.predict_stress = wrapped
    try:
        yield captured
    finally:
        cls.predict_stress = original


def refit_knots(
    record: Mapping[str, Any],
    rows: Sequence[Any],
    *,
    registry: Mapping[str, Mapping[str, object]],
    predictor: Any,
    scored_dates: Optional[Sequence[str]] = None,
) -> List[Dict[str, Any]]:
    """Refit the chosen folds of `record` and return their knots, in fold order.

    The fold loop is `baseline.rolling_exceedance_backtest`'s: the same purge
    from `_derive_purge`, the same `rolling_origin`, the same `_feature_index`
    and the same `purge_days` rule. Only folds whose `scored_date` is in
    `scored_dates` are fitted (all folds when `None`), so a long run can be
    split across processes. `predictor` is the one the record was made with,
    for example `ml.gbm_exceedance(...)`.

    Each knot is `capture_knots`' entry plus `scored_date` and `realized_bps`.

    Raises:
        ValueError: a fit made more or fewer than one `predict_stress` call,
            which means the predictor is not one this wrapper can read.
    """

    declaration = record["declaration"]
    features = tuple(declaration["features"])
    minimum_history = int(declaration["minimum_history"])
    taus = tuple(_taus(record))
    _, _, purge = _derive_purge(
        registry,
        features,
        decision_time=time.fromisoformat(declaration["decision_time"]),
    )
    wanted = None if scored_dates is None else set(scored_dates)
    reads_purge = _reads_purge_days(predictor)
    dates = [row.date for row in rows]
    knots: List[Dict[str, Any]] = []
    for train_indices, test_indices in rolling_origin(dates, minimum_history, 1, purge):
        index = test_indices[0]
        scored = rows[index].date.isoformat()
        if wanted is not None and scored not in wanted:
            continue
        train_rows = tuple(rows[i] for i in train_indices)
        feature_row = rows[_feature_index(dates, train_indices, index, purge)]
        with capture_knots() as captured:
            if reads_purge:
                predictor(train_rows, (feature_row,), taus, purge_days=purge)
            else:
                predictor(train_rows, (feature_row,), taus)
        if len(captured) != 1:
            raise ValueError(
                f"{scored}: the predictor made {len(captured)} predict_stress "
                f"calls; one per fold is what this refit reads"
            )
        knots.append(
            {"scored_date": scored, "realized_bps": rows[index].spread_bps, **captured[0]}
        )
    return knots
