"""A structural liquidity model of the pressure day (#542, track S of #374).

Twelve model families have been scored on the same inputs and a flexible learner cannot discover
the mechanism from 26 onsets. This model fixes the mechanism's form in advance and fits six
coefficients, as a funding desk would:

    P(pressure on T) = logistic(b0 + b1 * spread_bps
                                   + b2 * e * shortfall + b3 * e * tga_up
                                   + b4 * e * tax_date + b5 * e * window)

a logistic of the expected spread move. Its terms, all public at the decision instant:

* the **elasticity** `e` of the reserve demand curve at the current reserve level, the exponential
  curve of NY Fed Staff Report 1019 (Afonso, Giannone, La Spada and Williams):
  `e = exp(-(reserves / bank_total_assets - SATIATION) / LENGTH)`. It is 1 at satiation
  (`scarcity.SATIATION_BAND`, the lower end), flat-ish above and steep below. Neither constant is
  fitted;
* the **drain**: the announced net Treasury cash settlement of the scored day itself, as announced by the decision
  instant (#568, #618): `net_settlement_ahead_1d` at horizon 1, and at horizon h the difference
  `net_settlement_ahead_{h}d - net_settlement_ahead_{h-1}d` of the cumulative columns of
  `projected_reserves.AHEAD_COLUMNS`, the net of the one business day h rows ahead. Less the ON RRP balance, which absorbs it before reserves do: `shortfall = max(0, max(0, net) - on_rrp)`;
  the TGA's rise over the last five rows; the tax date, whose inflow raises the TGA; and the
  quarter-end and month-end window (balance-sheet window-dressing);
* the as-of spread.

The probability is never 0: it is a logistic on every day, risk date or not. Declared, with every
constant, in `metadata/structural_liquidity.json` before any score. The inputs are off in every
published declaration.

**Time-varying satiation (#587).** `StructuralDesign` takes a satiation form (`satiation.FORMS`): `fixed` (this
page's model), `rolling` (the level at a decision is the panel column `satiation_roll`, built from as-of reads
only) or `fitted` (one level per refit, fitted on that refit's training pairs by `satiation.fit_level`). The
terms are unchanged; only the `SATIATION` in the elasticity moves. One level for a whole refit (`fitted`) multiplies the
four elasticity terms by the constant `exp((level - 0.12) / LENGTH)`, which the logistic's standardisation removes, so
`fitted` forecasts the same as `fixed` here (to rounding); only a level that varies across the rows (`rolling`) moves
the model. Declared in `metadata/satiation_587.json`;
a measurement, off in every published declaration.

Standard library only: the six-coefficient ridge logistic is fitted here by Newton's method; the
as-of pairing of labels with what was public at their own decision instant is `ml._pressure_pairs`,
imported inside the function that needs it (`tests/test_dependency_boundary.py`).
"""

from __future__ import annotations

import json
import math
from dataclasses import dataclass
from pathlib import Path
from types import MappingProxyType
from typing import Any, Dict, List, Mapping, Optional, Sequence, Tuple

from .data import DailyObservation, exceeds_bp
from .projected_reserves import AHEAD_COLUMNS
from .satiation import FIXED, ROLLING_COLUMN, fit_level

__all__ = [
    "COLUMN_NAMES",
    "RAW_NAMES",
    "STRUCTURAL_FORMS",
    "DEFAULT_DECLARATION",
    "LENGTH",
    "RIDGE_C",
    "SATIATION",
    "StructuralDesign",
    "elasticity",
    "features_at_horizon",
    "fit_ridge_logistic",
    "shortfall",
    "structural_exceedance",
]

DEFAULT_DECLARATION = Path(__file__).resolve().parents[2] / "metadata" / "structural_liquidity.json"

#: The reserve-demand curve's reference level and length: the lower end of
#: `scarcity.SATIATION_BAND`, and one percentage point of bank assets. Declared, not fitted.
SATIATION = 0.12
LENGTH = 0.01

#: The ridge logistic's penalty, the direct logistic's (`ml.PRESSURE_LOGISTIC_SETTINGS`).
RIDGE_C = 1.0

COLUMN_NAMES = ("spread_bps", "e_x_shortfall", "e_x_tga_up", "e_x_tax_date", "e_x_window")
#: The `fitted` satiation form's design row before its level is known: the ratio and the four terms before the
#: elasticity multiplies them (`StructuralDesign.finish`).
RAW_NAMES = ("spread_bps", "ratio", "shortfall", "tga_up", "tax_date", "window")
#: The satiation forms the structural model reads (`satiation.FORMS` less the projected model's hinge control).
STRUCTURAL_FORMS = ("fixed", "rolling", "fitted")

_CALENDAR = ("days_to_month_end", "quarter_end", "tax_date")
_BASE = ("spread_bps",) + _CALENDAR + ("reserve_balances", "bank_total_assets", "on_rrp", "tga")
#: The drain's columns: the net announced for the next k business days, cumulative (`projected_reserves.AHEAD_COLUMNS`).
#: The scored day at horizon h is the h-th business day after the decision row, so its own settlement is the h-th
#: column less the (h-1)-th (the first column alone at h = 1), not `net_settlement`, which is the decision day's own
#: (#568), and not the five-day sum `net_settlement_due_5d` (#618).
_DRAIN_COLUMNS = AHEAD_COLUMNS
_EPSILON = 1e-6


def elasticity(ratio: float, satiation: float = SATIATION) -> float:
    """The reserve demand curve's slope at reserves over bank assets `ratio`: 1 at the satiation level (0.12 by default)."""

    return math.exp(-(float(ratio) - float(satiation)) / LENGTH)


def shortfall(net_settlement_bn: float, on_rrp_bn: float) -> float:
    """The announced drain the ON RRP balance has not absorbed, USD billions."""

    return max(0.0, max(0.0, float(net_settlement_bn)) - float(on_rrp_bn))


def drain_columns(horizon: int) -> Tuple[str, ...]:
    """The panel columns whose difference is the scored day's own announced net settlement at `horizon`.

    `(ahead_1d,)` at horizon 1; `(ahead_h, ahead_{h-1})` beyond (#618). The horizon is the number of panel rows
    from the decision row to the scored day.
    """

    if not 1 <= horizon <= len(_DRAIN_COLUMNS):
        raise ValueError(f"horizon must be one of 1 to {len(_DRAIN_COLUMNS)}, got {horizon}")
    return (_DRAIN_COLUMNS[horizon - 1],) + ((_DRAIN_COLUMNS[horizon - 2],) if horizon > 1 else ())


def features_at_horizon(horizon: int, satiation: str = "fixed") -> Tuple[str, ...]:
    """The declared features at `horizon`: the scored day's own announced settlement (#568, #618).

    Under the `rolling` satiation form (#587) the level column is read too.
    """

    if horizon < 1:
        raise ValueError(f"horizon must be positive, got {horizon}")
    drain = drain_columns(horizon)
    if satiation not in STRUCTURAL_FORMS:
        raise ValueError(f"the satiation form is one of {list(STRUCTURAL_FORMS)}, got {satiation!r}")
    extra = (ROLLING_COLUMN,) if satiation == "rolling" else ()
    return _BASE + drain + extra


class StructuralDesign:
    """The five non-constant columns of the mechanism, from one as-of observation."""

    tga = True
    scarcity = False
    products: Tuple[Tuple[str, str], ...] = ()
    monotone = None
    pooling = None
    names = COLUMN_NAMES

    def __init__(self, features: Sequence[str], declaration: Any, satiation: str = "fixed") -> None:
        if satiation not in STRUCTURAL_FORMS:
            raise ValueError(f"the satiation form is one of {list(STRUCTURAL_FORMS)}, got {satiation!r}")
        declared = tuple(dict.fromkeys(str(name) for name in features))
        required_columns = _BASE + ((ROLLING_COLUMN,) if satiation == "rolling" else ())
        for required in required_columns:
            if required not in declared:
                raise ValueError(f"the structural liquidity model reads {required!r}; declare it")
        matches = [
            drain_columns(k) for k in range(1, len(_DRAIN_COLUMNS) + 1) if set(drain_columns(k)) == set(declared) & set(_DRAIN_COLUMNS)
        ]
        if not matches:
            raise ValueError(
                f"declare the scored day's drain, {list(drain_columns(1))} or an adjacent pair of {list(_DRAIN_COLUMNS)}, "
                f"got {[name for name in _DRAIN_COLUMNS if name in declared]}"
            )
        if not hasattr(declaration, "day_type"):
            raise ValueError("the pressure-day type needs the split declaration that defines it")
        self.features = declared
        self.declaration = declaration
        self.drain_columns = matches[0]
        self.satiation = satiation

    def needs_history(self) -> bool:
        return True

    def _value(self, row: DailyObservation, column: str) -> float:
        value = row.values.get(column)
        if value is None or not math.isfinite(float(value)):
            raise ValueError(
                f"{row.date}: the as-of read of {column!r} is missing; the structural model is not "
                f"fitted or served on an unobserved input"
            )
        return float(value)

    def drain(self, observation: DailyObservation) -> float:
        """The scored day's own announced net settlement, USD billions: the horizon's column less the one before it (#618)."""

        values = [self._value(observation, name) for name in self.drain_columns]
        return values[0] - (values[1] if len(values) > 1 else 0.0)

    def row(self, observation: DailyObservation, tga_change: Optional[float]) -> List[float]:
        """The five columns; under `fitted`, the raw row (`RAW_NAMES`) that `finish` completes once the level is fitted."""

        if tga_change is None:
            raise ValueError("the TGA change is required")
        from .scarcity import reserves_ratio

        ratio = reserves_ratio(
            self._value(observation, "reserve_balances"), self._value(observation, "bank_total_assets")
        )
        short = shortfall(self.drain(observation), self._value(observation, "on_rrp"))
        kind = self.declaration.day_type(observation.values)
        raw = [
            float(observation.spread_bps),
            ratio,
            short,
            max(0.0, float(tga_change)),
            1.0 if kind == "tax_date" else 0.0,
            1.0 if kind in ("quarter_end", "month_end") else 0.0,
        ]
        if self.satiation == "fitted":
            return raw
        level = self._value(observation, ROLLING_COLUMN) if self.satiation == "rolling" else SATIATION
        return self.finish(raw, level)

    def finish(self, raw: Sequence[float], level: float) -> List[float]:
        """The five columns from a raw row (`RAW_NAMES`) at satiation `level`: the elasticity multiplies four terms."""

        e = elasticity(raw[1], level)
        return [raw[0], e * raw[2], e * raw[3], e * raw[4], e * raw[5]]


@dataclass(frozen=True)
class RidgeFit:
    """A ridge logistic on standardized columns: `coefficients` = intercept, then one per column."""

    centre: Tuple[float, ...]
    scale: Tuple[float, ...]
    coefficients: Tuple[float, ...]

    def predict(self, xs: Sequence[Sequence[float]]) -> List[float]:
        out = []
        for x in xs:
            z = self.coefficients[0] + sum(
                b * (v - c) / s for b, v, c, s in zip(self.coefficients[1:], x, self.centre, self.scale)
            )
            out.append(_sigmoid(z))
        return out

    def raw_coefficients(self) -> Tuple[float, ...]:
        """The same logistic in the columns' own units (intercept first)."""

        slopes = [b / s for b, s in zip(self.coefficients[1:], self.scale)]
        intercept = self.coefficients[0] - sum(m * c for m, c in zip(slopes, self.centre))
        return (intercept, *slopes)


def _sigmoid(z: float) -> float:
    if z >= 0:
        return 1.0 / (1.0 + math.exp(-z))
    t = math.exp(z)
    return t / (1.0 + t)


def _solve(a: List[List[float]], b: List[float]) -> List[float]:
    """Solve a small symmetric positive-definite system by Gaussian elimination with pivoting."""

    n = len(b)
    m = [row[:] + [b[i]] for i, row in enumerate(a)]
    for col in range(n):
        pivot = max(range(col, n), key=lambda r: abs(m[r][col]))
        m[col], m[pivot] = m[pivot], m[col]
        if abs(m[col][col]) < 1e-14:
            raise ValueError("the Newton system is singular")
        for r in range(col + 1, n):
            f = m[r][col] / m[col][col]
            for k in range(col, n + 1):
                m[r][k] -= f * m[col][k]
    x = [0.0] * n
    for i in range(n - 1, -1, -1):
        x[i] = (m[i][n] - sum(m[i][k] * x[k] for k in range(i + 1, n))) / m[i][i]
    return x


def fit_ridge_logistic(
    xs: Sequence[Sequence[float]], ys: Sequence[int], c: float = RIDGE_C, iterations: int = 100
) -> RidgeFit:
    """Minimise sum of log loss + (1 / 2c) * ||w||^2 on standardized columns; the intercept is free."""

    if not xs or len(xs) != len(ys):
        raise ValueError("fit_ridge_logistic needs one label per row, and at least one row")
    if c <= 0:
        raise ValueError(f"the penalty strength must be positive, got {c}")
    n, d = len(xs), len(xs[0])
    centre = [sum(x[j] for x in xs) / n for j in range(d)]
    scale = []
    for j in range(d):
        var = sum((x[j] - centre[j]) ** 2 for x in xs) / n
        scale.append(math.sqrt(var) if var > 0 else 1.0)
    z = [[(x[j] - centre[j]) / scale[j] for j in range(d)] for x in xs]
    w = [0.0] * (d + 1)
    lam = 1.0 / c

    def objective(weights: List[float]) -> float:
        total = 0.0
        for row, y in zip(z, ys):
            s = weights[0] + sum(weights[j + 1] * row[j] for j in range(d))
            total += max(s, 0.0) - y * s + math.log1p(math.exp(-abs(s)))
        return total + 0.5 * lam * sum(v * v for v in weights[1:])

    current = objective(w)
    for _ in range(iterations):
        grad = [0.0] * (d + 1)
        hess = [[0.0] * (d + 1) for _ in range(d + 1)]
        for row, y in zip(z, ys):
            aug = [1.0] + row
            p = _sigmoid(sum(w[k] * aug[k] for k in range(d + 1)))
            r = p - y
            q = p * (1.0 - p)
            for a_ in range(d + 1):
                grad[a_] += r * aug[a_]
                for b_ in range(a_, d + 1):
                    hess[a_][b_] += q * aug[a_] * aug[b_]
        for k in range(1, d + 1):
            grad[k] += lam * w[k]
            hess[k][k] += lam
        for a_ in range(d + 1):
            for b_ in range(a_):
                hess[a_][b_] = hess[b_][a_]
        hess[0][0] += 1e-9
        step = _solve(hess, grad)
        scale_step = 1.0
        while scale_step > 1e-8:
            trial = [wi - scale_step * si for wi, si in zip(w, step)]
            value = objective(trial)
            if value <= current + 1e-12:
                break
            scale_step /= 2.0
        else:
            break
        improved = current - value
        w, current = trial, value
        if improved < 1e-10:
            break
    return RidgeFit(tuple(centre), tuple(scale), tuple(w))


def structural_exceedance(
    features: Sequence[str], declaration: Any, *, minimum_history: int, satiation: str = "fixed"
) -> Any:
    """The model in the `ExceedancePredictor` shape: P(spread > tau) on every day, per threshold.

    `fit_predict.fits` collects, for every refit, each threshold's coefficients (standardized and in
    the columns' own units) and the training pairs it was fitted on. With `satiation="fitted"` (#587) each
    refit also records the level it fitted on its training pairs.
    """

    from .baseline import ExceedanceCurves

    if minimum_history < 1:
        raise ValueError(f"minimum_history must be positive, got {minimum_history}")
    design = StructuralDesign(features, declaration, satiation)
    cache: dict = {}
    fits: List[Dict[str, Any]] = []

    def fit_predict(
        train_rows: Sequence[DailyObservation],
        feature_rows: Sequence[DailyObservation],
        taus: Sequence[float],
        information: Optional[Any] = None,
        histories: Optional[Sequence[Sequence[DailyObservation]]] = None,
    ) -> Any:
        from . import ml

        if information is None:
            raise ValueError(
                "the structural liquidity model pairs each training label with what was public at "
                "that label's own decision instant, which only the as-of rule can say; it was called "
                "without one"
            )
        if len(train_rows) < minimum_history:
            raise ValueError(
                f"the structural liquidity model needs at least {minimum_history} training rows, "
                f"got {len(train_rows)}"
            )
        if histories is None or len(histories) != len(feature_rows):
            raise ValueError(
                "the TGA change is read off each forecast's own as-of history; one history per "
                "feature row is required"
            )
        xs, spreads = ml._pressure_pairs(design, information, train_rows, cache)
        if not xs:
            raise ValueError("no training label has a complete as-of read")
        served = [
            design.row(row, ml._served_tga_change(histories[day], row)) for day, row in enumerate(feature_rows)
        ]
        level_record: Dict[str, Any] = {}
        if satiation == "fitted":
            # one level for the refit, from its training pairs alone; the pairs' ratios were public at their own
            # decisions and their spreads are labels the training frame covers
            level, level_record = fit_level([x[1] for x in xs], spreads)
            level_record = {"satiation_level": level, **level_record}
            xs = [design.finish(x, level) for x in xs]
            served = [design.finish(x, level) for x in served]
        columns: List[List[float]] = []
        record: Dict[str, Any] = {
            "pairs": len(xs), "last_training_row": train_rows[-1].date.isoformat(), **level_record
        }
        for tau in taus:
            labels = [1 if exceeds_bp(value, float(tau)) else 0 for value in spreads]
            events = sum(labels)
            if events == 0 or events == len(labels):
                # One class: a smoothed rate, never exactly 0 or 1 (the model forecasts every day).
                rate = (events + 0.5) / (len(labels) + 1.0)
                columns.append([rate] * len(served))
                record[f"{tau:g}"] = {"events": events, "coefficients": None, "raw_coefficients": None}
                continue
            fit = fit_ridge_logistic(xs, labels)
            columns.append([min(1.0 - _EPSILON, max(_EPSILON, p)) for p in fit.predict(served)])
            record[f"{tau:g}"] = {
                "events": events,
                "coefficients": list(fit.coefficients),
                "raw_coefficients": list(fit.raw_coefficients()),
            }
        fits.append(record)
        curves = []
        for day in range(len(served)):
            curve: List[float] = []
            for column in columns:
                value = column[day]
                curve.append(value if not curve else min(curve[-1], value))
            curves.append(tuple(curve))
        settings = {
            "estimator": "ridge logistic, Newton's method, standardized columns",
            "C": RIDGE_C,
            "design": ["intercept", *COLUMN_NAMES],
            "drain": list(design.drain_columns),
            "satiation": SATIATION if satiation == "fixed" else satiation,
            "length": LENGTH,
        }
        return ExceedanceCurves(
            tuple(curves),
            design.features,
            ml_libraries=None,
            model_settings=MappingProxyType(settings),
            history_ends=tuple(history[-1].date if history else None for history in histories),
        )

    fit_predict.fits = fits  # type: ignore[attr-defined]
    return fit_predict
