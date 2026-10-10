"""A calibrated stack of the five tier-1 passers (#475, a track of #374).

Two candidates, declared in `metadata/calibrated_stack.json` and in their own files under
`metadata/pressure_judge/candidates/` before any score:

* `calibrated_stack_logistic`: a logistic regression of the pressure day on the logits of the five passers'
  probabilities (`risk_gbm`, `risk_gbm_base`, `risk_logistic`, `risk_logistic_base`, `risk_quantile_skewt_base`)
  and the as-of regime (one indicator per regime label), refitted at each of the judge's refit blocks on the
  block's training window alone.
* `calibrated_stack_isotonic`: the same stack, followed by an isotonic recalibration (`probability_calibration`'s
  CORP isotonic fit) of the outcome on the stack's own probability, also on the training window alone.

**The information set.** A refit at the block starting at scored day `start` reads the members' probabilities and
the outcomes of earlier blocks' days whose outcome was public at the block's first decision instant
(`stacking.training_window`, the judge's own training end). Every member probability it reads was made at that
day's own decision instant by a walk-forward forecast, before the refit, so the stack is fitted on out-of-sample
base forecasts only. The isotonic step is fitted on the stack's *walk-forward* probabilities of those same days (each
made by an earlier refit that could not see the day's outcome), never on the stack's in-sample fit. The regime is a
function of the day's calendar date (`metadata/evaluation_splits.json`), known at the decision instant. A window day
after the training end raises `LookAheadError`; a malformed input raises `ValueError`. Standard library only.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any, Dict, List, Mapping, Optional, Sequence, Tuple

from . import probability_calibration as pc
from . import stacking
from .splits import LookAheadError

DEFAULT_DECLARATION = Path(__file__).resolve().parents[2] / "metadata" / "calibrated_stack.json"


def regime_indicators(labels: Sequence[str], regimes: Sequence[str]) -> List[Tuple[float, ...]]:
    """One 0/1 indicator per declared regime label for each day's regime.

    Raises:
        ValueError: on a regime that is not among the declared labels.
    """

    unknown = sorted({r for r in regimes if r not in labels})
    if unknown:
        raise ValueError(f"regime {unknown[0]!r} is not among the declared labels {list(labels)}")
    return [tuple(1.0 if r == label else 0.0 for label in labels) for r in regimes]


@dataclass(frozen=True)
class Calibrated:
    stacked: Tuple[float, ...]
    recalibrated: Tuple[float, ...]
    trace: Tuple[Dict[str, Any], ...]


def calibrated_stack(
    days: Sequence[date],
    calendar: Sequence[date],
    members: Mapping[str, Sequence[float]],
    regimes: Sequence[str],
    outcomes: Sequence[int],
    *,
    regime_labels: Sequence[str],
    horizon: int,
    step: int,
    ridge: float,
    clip: float,
    fallback: stacking.Fallback,
    iterations: int = 50,
    tolerance: float = 1e-8,
) -> Calibrated:
    """The walk-forward stack and its isotonic recalibration for every scored day.

    `stacked[k]` is the logistic stack of the members' logits and the regime indicators; `recalibrated[k]` is the
    isotonic recalibration of `stacked` fitted on the training window's walk-forward `stacked` values. While the
    window is too thin the stack is the equal-weight logit pool (regime coefficients 0) and the recalibration is the
    identity.

    Raises:
        LookAheadError: if a refit's window would reach past its training end.
        ValueError: if the members, regimes, days and outcomes differ in length, or a day is not a panel day.
    """

    names = list(members)
    if not names:
        raise ValueError("a stack needs members")
    n = len(days)
    if len(outcomes) != n or len(regimes) != n or any(len(members[name]) != n for name in names):
        raise ValueError("every member, the regimes and the outcomes need one value per scored day")
    position = {day: k for k, day in enumerate(calendar)}
    missing = [day for day in days if day not in position]
    if missing:
        raise ValueError(f"scored day {missing[0]} is not a panel day")
    m = len(names)
    indicators = regime_indicators(regime_labels, regimes)
    features = [
        [stacking.clipped_logit(members[name][k], clip) for name in names] + list(indicators[k]) for k in range(n)
    ]
    prior = [1.0 / m] * m + [0.0] * len(regime_labels)
    stacked: List[float] = []
    recalibrated: List[float] = []
    trace: List[Dict[str, Any]] = []
    for start in range(0, n, step):
        block = range(start, min(start + step, n))
        window = stacking.training_window(days, calendar, start=start, horizon=horizon)
        training_end = stacking.training_end_of(days, calendar, start=start, horizon=horizon)
        positives = sum(outcomes[k] for k in window)
        thin = fallback.applies(days=len(window), positives=positives)
        if thin:
            intercept, weights, mode = 0.0, tuple(prior), "equal"
            curve = None
        else:
            intercept, weights = stacking.fit_logit_stack(
                [features[k] for k in window], [outcomes[k] for k in window],
                ridge=ridge, iterations=iterations, tolerance=tolerance, prior=prior,
            )
            mode = "fitted"
            pairs = [(days[k], stacked[k], outcomes[k]) for k in window]
            curve = pc.fit("isotonic", pairs, training_end) if training_end is not None else None
        for k in block:
            p = stacking._sigmoid(intercept + sum(w * x for w, x in zip(weights, features[k])))
            stacked.append(p)
            q = p if curve is None else min(max(curve(p), clip), 1.0 - clip)
            recalibrated.append(q)
        trace.append(
            {
                "first_day": days[start].isoformat(),
                "mode": mode,
                "training_days": len(window),
                "training_pressure_days": positives,
                "intercept": intercept,
                "weights": list(weights[:m]),
                "regime_coefficients": dict(zip(regime_labels, weights[m:])),
            }
        )
    return Calibrated(tuple(stacked), tuple(recalibrated), tuple(trace))


@dataclass(frozen=True)
class Declaration:
    path: str
    sha256: str
    logistic: str
    isotonic: str
    members: Tuple[str, ...]
    regime_labels: Tuple[str, ...]
    thresholds: Tuple[float, ...]
    clip: float
    ridge: float
    iterations: int
    tolerance: float
    step: int
    fallback: stacking.Fallback


def parse_declaration(document: Mapping[str, Any], where: str, digest: str = "") -> Declaration:
    members = tuple(document["members"])
    if len(members) < 2 or len(set(members)) != len(members):
        raise ValueError(f"{where}: members must be at least two distinct names")
    labels = tuple(document["regime_labels"])
    if not labels or len(set(labels)) != len(labels):
        raise ValueError(f"{where}: regime_labels must be distinct and not empty")
    clip = float(document["clip"])
    if not 0.0 < clip < 0.5:
        raise ValueError(f"{where}: clip must be in (0, 0.5)")
    fit, refit, fb = document["fit"], document["refit"], document["fallback"]
    ridge = float(fit["ridge"])
    if ridge < 0:
        raise ValueError(f"{where}: ridge must not be negative")
    return Declaration(
        path=where,
        sha256=digest,
        logistic=str(document["candidates"]["logistic"]),
        isotonic=str(document["candidates"]["isotonic"]),
        members=members,
        regime_labels=labels,
        thresholds=tuple(float(t) for t in document["thresholds_bp"]),
        clip=clip,
        ridge=ridge,
        iterations=int(fit["iterations_at_most"]),
        tolerance=float(fit["tolerance"]),
        step=int(refit["every"]),
        fallback=stacking.Fallback(int(fb["minimum_days"]), int(fb["minimum_each_class"])),
    )


def load_declaration(path: Path = DEFAULT_DECLARATION) -> Declaration:
    raw = Path(path).read_bytes()
    return parse_declaration(json.loads(raw), str(path), hashlib.sha256(raw).hexdigest())
