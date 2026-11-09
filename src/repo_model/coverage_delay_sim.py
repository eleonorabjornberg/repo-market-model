"""Simulated forecasters for the size and power of amendment 4's coverage design under the publication delay (#1528; H5, step M5).

A development tool, never a verdict. The design is the one `scoring_protocol.coverage_cells` and `enforce_coverage_requirement` apply:
Kupiec and Christoffersen independence at q05/q95 and q01/q99, leads h = 1 to 5, each regime, hits read on every s-th decision day, Holm over
the family at 5%. The study asks how often it rejects a forecaster that is correct, and how often one that is not, when the data keep three
features of the real series that the earlier size studies (#1156, #1516, #1525) did not have together:

- the one-day publication delay. The forecast of target D + h is made at the decision on day D, from the last published spread, that of D - 1,
  so it looks n = h + 1 days ahead of the last value it sees (`information-set.md`, rule 1). The forecast's own error for D + h and the error for
  D + 2h therefore share the innovation of D + h, which the second forecast also has not seen: hits h days apart are dependent for a forecaster
  that is correct. Hits h + 1 days apart are not: the target of the first is published when the second is made.
- volatility clustering: the innovations of the latent series have a two-state Markov scale (calm, stress).
- calendar effects: the observed spread is the latent series times a scale that depends on the class of the target day (quarter-end, month-end,
  tax date, settlement, policy day), and the forecaster knows the class of its target day (a scheduled column, `asof` rule 2).

Model. `x[t] = phi * x[t-1] + sigma[z[t]] * e[t]`, `e` standard normal, `z` a Markov chain on {0, 1} with stay probabilities `stay`. The spread
on day t is a level plus `scale[class(t)] * x[t]`; a forecaster that knows the level and the class works in `x`, so every PIT below is a PIT of
`x`, and the levels and class means of the real series, which a correct forecaster has removed, do not enter. The forecaster knows `x[D-1]` and
`z[D-1]` (the volatility state is taken as public, as a volatility index would be) and its distribution of `x[D+h]` is the exact mixture of normals over
the 2^n state paths it cannot see: mean `phi^n x[D-1]`, variance `sum_i phi^(2 (n-i)) sigma[z_i]^2`, weights the path probabilities.

Misspecified forecasters (`Forecaster`): a `scale` on the forecast's standard deviation, on all target days or only on the days of given
classes (`on`), and a `lag`, the number of days by which the volatility state it conditions on is stale.

Stdlib only. Nothing here reads a date after the window's last day (`require_development`).
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from datetime import date
from functools import lru_cache
from itertools import product
from statistics import median
from typing import Dict, FrozenSet, Iterable, List, Mapping, Optional, Sequence, Tuple

from . import coverage_tests as ct
from .exploration import require_exploratory_window
from .splits import LookAheadError

__all__ = [
    "CLASSES", "LEADS", "LEVELS", "RULES", "Calibration", "Forecaster", "Structure", "components", "mixture_cdf", "simulate_latent",
    "pit", "pit_columns", "cell_p_values", "family", "holm_rejected", "fit_calibration", "day_class", "require_development",
]

#: Calendar classes of a target day, by priority (a day with several types takes the first). `ordinary` also holds the days of the
#: panel's pressure windows that are not a scheduled date (19th to 23rd, the week after month-end): they are not a calendar class here.
CLASSES: Tuple[str, ...] = ("ordinary", "quarter_end", "month_end", "tax_date", "settlement", "policy")
_PRIORITY = (
    ("quarter_end", ("quarter_end",)), ("month_end", ("month_end",)), ("tax_date", ("tax_date",)),
    ("settlement", ("coupon_settlement", "bill_settlement")), ("policy", ("fomc_day", "iorb_window")),
)
LEADS: Tuple[int, ...] = (1, 2, 3, 4, 5)
LEVELS: Tuple[float, ...] = (0.05, 0.95, 0.01, 0.99)
ALPHA = 0.05
#: A rule is the pair (Kupiec p, independence p) it reads: the amendment as set (both at spacing h), her ruling of 8 November 2026 on #1525
#: (independence at h + 1, Kupiec as set), and both at h + 1.
RULES: Dict[str, Tuple[str, str]] = {"h": ("kupiec_h", "indep_h"), "indep_h1": ("kupiec_h", "indep_h1"), "h1": ("kupiec_h1", "indep_h1")}

Key = Tuple[int, str, float]


def day_class(types: Iterable[str]) -> str:
    """The class of a target day from the panel's day types, by `CLASSES` priority; any other type is `ordinary`."""

    kinds = set(types)
    for name, members in _PRIORITY:
        if kinds & set(members):
            return name
    return "ordinary"


def require_development(days: Iterable[date], last: date, *, where: str) -> None:
    """Refuse a day after `last` (the development window's last day) and a day of a tier still locked: raises `LookAheadError`."""

    days = sorted(days)
    for day in days:
        if day > last:
            raise LookAheadError(f"{where}: day {day} is after {last}, the last day of the development window")
    require_exploratory_window(days, where=where)


@dataclass(frozen=True)
class Calibration:
    """`phi`, the two innovation scales, the two stay probabilities and the observation scale of each class (ordinary 1)."""

    phi: float
    sigma: Tuple[float, float]
    stay: Tuple[float, float]
    scale: Mapping[str, float]

    def as_dict(self) -> dict:
        return {"phi": self.phi, "sigma": list(self.sigma), "stay": list(self.stay), "scale": dict(self.scale)}

    @classmethod
    def from_dict(cls, doc: Mapping[str, object]) -> "Calibration":
        return cls(float(doc["phi"]), tuple(doc["sigma"]), tuple(doc["stay"]), dict(doc["scale"]))  # type: ignore[arg-type]


@dataclass(frozen=True)
class Forecaster:
    """A forecaster: `scale` multiplies the forecast's standard deviation (on all target days when `on` is None, else on target days whose class is
    in `on`); `lag` is how many days stale the volatility state it conditions on is. The defaults are the true conditional distribution."""

    name: str
    scale: float = 1.0
    on: Optional[FrozenSet[str]] = None
    lag: int = 0


@dataclass
class Structure:
    """The calendar the study reads: its dates, the class of each calendar day, and the decision days.

    `positions[i]` is the calendar position of the i-th decision day (a lead-h target is at `positions[i] + h`, the last published day at
    `positions[i] - 1`), `regimes[i]` its regime. The index i is the order `coverage_cells` thins on.
    """

    calendar: List[date]
    classes: List[str]
    positions: List[int]
    regimes: List[str]

    def __post_init__(self) -> None:
        if len(self.calendar) != len(self.classes) or len(self.positions) != len(self.regimes):
            raise ValueError("calendar and classes, positions and regimes must have equal lengths")
        if not self.positions or min(self.positions) < 1 or max(self.positions) + max(LEADS) >= len(self.calendar):
            raise ValueError("every decision day needs a published day before it and five calendar days after it")

    def by_regime(self) -> Dict[str, List[int]]:
        out: Dict[str, List[int]] = {}
        for i, r in enumerate(self.regimes):
            out.setdefault(r, []).append(i)
        return out


# -- the forecast distribution -----------------------------------------------------------------------------------------------------


@lru_cache(maxsize=None)
def components(phi: float, sigma: Tuple[float, float], stay: Tuple[float, float], z0: int, n: int) -> Tuple[Tuple[float, ...], Tuple[float, ...]]:
    """Weights and variances of the mixture for `x[t+n]` given `x[t]` and the state `z0` at t: one component per state path z_1 .. z_n.

    The mean of every component is `phi**n * x[t]`; the variance of the path is `sum_i phi**(2 (n - i)) * sigma[z_i]**2`.
    """

    weights: List[float] = []
    variances: List[float] = []
    for path in product((0, 1), repeat=n):
        w, previous = 1.0, z0
        for z in path:
            w *= stay[previous] if z == previous else 1.0 - stay[previous]
            previous = z
        weights.append(w)
        variances.append(sum(phi ** (2 * (n - i)) * sigma[z] ** 2 for i, z in enumerate(path, start=1)))
    return tuple(weights), tuple(variances)


_SQRT2 = math.sqrt(2.0)


def mixture_cdf(x: float, mean: float, weights: Sequence[float], variances: Sequence[float], scale: float = 1.0) -> float:
    """P(X <= x) for the normal mixture with common `mean` and standard deviations `scale * sqrt(variance)`."""

    erf = math.erf
    d = x - mean
    return sum(w * 0.5 * (1.0 + erf(d / (scale * math.sqrt(v) * _SQRT2))) for w, v in zip(weights, variances))


def simulate_latent(cal: Calibration, length: int, rng, burn: int = 300) -> Tuple[List[float], List[int]]:
    """`x` and `z` for `length` days after a burn-in, started from the calm state."""

    x, z = 0.0, 0
    xs: List[float] = []
    zs: List[int] = []
    for t in range(burn + length):
        z = z if rng.random() < cal.stay[z] else 1 - z
        x = cal.phi * x + cal.sigma[z] * rng.gauss(0.0, 1.0)
        if t >= burn:
            xs.append(x)
            zs.append(z)
    return xs, zs


def pit(cal: Calibration, x: Sequence[float], z: Sequence[int], position: int, h: int, target_class: str, fc: Forecaster) -> float:
    """The PIT of `x[position + h]` under `fc`'s forecast made at decision day `position`, from the last published day `position - 1`.

    The forecast is `h + 1` steps ahead of the last published value (the publication delay), with the state of `fc.lag` days before it.
    """

    n = h + 1
    last_published = position - 1
    weights, variances = components(cal.phi, tuple(cal.sigma), tuple(cal.stay), z[last_published - fc.lag] if last_published - fc.lag >= 0 else 0, n)
    scale = fc.scale if (fc.on is None or target_class in fc.on) else 1.0
    return mixture_cdf(x[position + h], cal.phi ** n * x[last_published], weights, variances, scale)


def pit_columns(cal: Calibration, x: Sequence[float], z: Sequence[int], structure: Structure, fc: Forecaster) -> Dict[int, List[float]]:
    """The PIT of each decision day at each lead, in decision order."""

    return {
        h: [pit(cal, x, z, p, h, structure.classes[p + h], fc) for p in structure.positions]
        for h in LEADS
    }


# -- the design ---------------------------------------------------------------------------------------------------------------------


def _hits(v: Sequence[float], level: float) -> List[int]:
    return [int(a > level) for a in v] if level > 0.5 else [int(a < level) for a in v]


def cell_p_values(structure: Structure, u: Mapping[int, Sequence[float]]) -> Dict[Key, Dict[str, float]]:
    """Per (lead, regime, level): Kupiec and independence p-values with hits read every h-th decision day (`_h`) and every (h + 1)-th (`_h1`).

    As `scoring_protocol.coverage_cells` with `method="thinned"`: the decision order index thins, within the regime; the independence p is
    None-free here because a regime has far more than two thinned days. A strict hit is a PIT beyond the level.
    """

    out: Dict[Key, Dict[str, float]] = {}
    for h in LEADS:
        for regime, idx in sorted(structure.by_regime().items()):
            kept = {s: [i for i in idx if i % s == 0] for s in (h, h + 1)}
            for level in LEVELS:
                p = min(level, 1.0 - level)
                row: Dict[str, float] = {}
                for tag, s in (("h", h), ("h1", h + 1)):
                    hits = _hits([u[h][i] for i in kept[s]], level)
                    row["kupiec_" + tag] = ct.kupiec(hits, p).p_value if hits else 1.0
                    row["indep_" + tag] = ct.christoffersen_independence(hits).p_value if len(hits) >= 2 else 1.0
                out[(h, regime, level)] = row
    return out


def holm_rejected(ps: Sequence[float], alpha: float = ALPHA) -> List[int]:
    """Indices rejected by Holm's step-down at family level `alpha` (as `scoring_protocol.holm`)."""

    ordered = sorted(range(len(ps)), key=lambda i: ps[i])
    out: List[int] = []
    for rank, i in enumerate(ordered):
        if ps[i] > alpha / (len(ordered) - rank):
            break
        out.append(i)
    return out


def family(table: Mapping[Key, Mapping[str, float]], rule: str) -> Tuple[List[float], List[Tuple[Key, str]]]:
    """The p-values of the family a rule reads (two tests per cell) and who each is (cell, "kupiec" or "independence")."""

    kupiec_name, indep_name = RULES[rule]
    ps: List[float] = []
    who: List[Tuple[Key, str]] = []
    for key in table:
        ps.append(table[key][kupiec_name])
        who.append((key, "kupiec"))
        ps.append(table[key][indep_name])
        who.append((key, "independence"))
    return ps, who


# -- the fit to development data ----------------------------------------------------------------------------------------------------


def _mad_sd(values: Sequence[float]) -> float:
    """The mean absolute deviation about the median, times sqrt(pi / 2): a standard deviation for normal data that stays finite-valued and
    graded on spreads recorded in whole basis points (a median absolute deviation of such data is an integer)."""

    centre = median(values)
    return math.sqrt(math.pi / 2.0) * sum(abs(v - centre) for v in values) / len(values)


def _two_state_scale_mixture(r: Sequence[float], iterations: int = 150) -> Tuple[Tuple[float, float], Tuple[float, float]]:
    """Baum-Welch for zero-mean normals with a two-state Markov scale. Returns (sigma_calm, sigma_stress), (stay_calm, stay_stress)."""

    n = len(r)
    base = max(_mad_sd(r), 1e-9)
    sig = [base * 0.7, base * 2.0]
    stay = [0.95, 0.9]
    pi0 = [0.5, 0.5]
    for _ in range(iterations):
        dens = [[math.exp(-0.5 * (v / sig[k]) ** 2) / (sig[k] * math.sqrt(2 * math.pi)) + 1e-300 for k in (0, 1)] for v in r]
        trans = [[stay[0], 1 - stay[0]], [1 - stay[1], stay[1]]]
        alpha, scale = [], []
        a = [pi0[k] * dens[0][k] for k in (0, 1)]
        for t in range(n):
            if t:
                a = [sum(alpha[-1][j] * trans[j][k] for j in (0, 1)) * dens[t][k] for k in (0, 1)]
            c = a[0] + a[1]
            scale.append(c)
            alpha.append([a[0] / c, a[1] / c])
        beta = [[1.0, 1.0] for _ in range(n)]
        for t in range(n - 2, -1, -1):
            b = [sum(trans[j][k] * dens[t + 1][k] * beta[t + 1][k] for k in (0, 1)) / scale[t + 1] for j in (0, 1)]
            beta[t] = b
        gamma = [[alpha[t][k] * beta[t][k] for k in (0, 1)] for t in range(n)]
        for g in gamma:
            s = g[0] + g[1]
            g[0] /= s
            g[1] /= s
        xi = [[0.0, 0.0], [0.0, 0.0]]
        for t in range(n - 1):
            for j in (0, 1):
                for k in (0, 1):
                    xi[j][k] += alpha[t][j] * trans[j][k] * dens[t + 1][k] * beta[t + 1][k] / scale[t + 1]
        stay = [xi[0][0] / max(xi[0][0] + xi[0][1], 1e-12), xi[1][1] / max(xi[1][0] + xi[1][1], 1e-12)]
        stay = [min(max(s, 0.5), 0.999) for s in stay]
        sig = [math.sqrt(max(sum(gamma[t][k] * r[t] ** 2 for t in range(n)) / max(sum(gamma[t][k] for t in range(n)), 1e-12), 1e-12)) for k in (0, 1)]
        pi0 = gamma[0]
    if sig[0] > sig[1]:
        sig = [sig[1], sig[0]]
        stay = [stay[1], stay[0]]
    return (sig[0], sig[1]), (stay[0], stay[1])


def fit_calibration(series: Sequence[Optional[float]], classes: Sequence[str], regimes: Sequence[Optional[str]]) -> Calibration:
    """Calibrate the model to a spread series (None where unobserved), the class of each day and the regime of each day.

    Steps: remove each regime's median on ordinary days (a level the correct forecaster knows); take each class's scale as the
    mean-absolute-deviation standard deviation of its days over that of ordinary days, after removing the class's median (a class mean); standardise; fit `phi` by least
    squares through the origin on consecutive observed days; fit the two-state scale mixture to the AR(1) residuals by Baum-Welch. A class with
    fewer than 5 days gets scale 1.
    """

    if not (len(series) == len(classes) == len(regimes)):
        raise ValueError("series, classes and regimes must have equal lengths")
    level: Dict[str, float] = {}
    for r in {r for r in regimes if r is not None}:
        vals = [s for s, c, g in zip(series, classes, regimes) if s is not None and g == r and c == "ordinary"]
        pool = vals or [s for s, g in zip(series, regimes) if s is not None and g == r]
        level[r] = median(pool)
    dev = [None if s is None or g is None else s - level[g] for s, g in zip(series, regimes)]
    ordinary = [d for d, c in zip(dev, classes) if d is not None and c == "ordinary"]
    if len(ordinary) < 20:
        raise ValueError("too few ordinary days to calibrate")
    base = median(ordinary)
    base_sd = _mad_sd(ordinary)
    scale: Dict[str, float] = {"ordinary": 1.0}
    centre: Dict[str, float] = {"ordinary": base}
    for name in CLASSES[1:]:
        vals = [d for d, c in zip(dev, classes) if d is not None and c == name]
        if len(vals) < 5:
            scale[name], centre[name] = 1.0, base
        else:
            centre[name] = median(vals)
            scale[name] = max(_mad_sd(vals) / base_sd, 0.2)
    x: List[Optional[float]] = [None if d is None else (d - centre[c]) / scale[c] for d, c in zip(dev, classes)]
    num = den = 0.0
    for a, b in zip(x, x[1:]):
        if a is not None and b is not None:
            num += a * b
            den += a * a
    phi = min(max(num / den, 0.0), 0.98)
    resid = [b - phi * a for a, b in zip(x, x[1:]) if a is not None and b is not None]
    sigma, stay = _two_state_scale_mixture(resid)
    return Calibration(phi, sigma, stay, scale)
