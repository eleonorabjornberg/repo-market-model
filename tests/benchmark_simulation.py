"""A simulated panel with known dynamics, for the benchmarks of scoring protocol v1 (#762, H1 step 3).

**The process.** Rows are the market calendar's business days (weekdays not in
`metadata/market_holidays.json`), 2018-01-02 to 2021-12-31. The spread in bp is

    y[t] = LEVEL[type of t] + x[t],     x[t] = PHI * x[t-1] + e[t],     e ~ N(0, SIGMA^2),

an AR(1) around a level that depends on the day's type: quarter-end, month-end (the month's
last two business days), tax date or ordinary. The types are assigned here from the rows
themselves, not by the repository's calendar code, so the panel's labels and
`SplitDeclaration.reporting_day_type` are two computations of one definition.

**The known conditional law.** The last public row at the decision on row `t` is `t - 1`, so a
forecast of row `t + h` conditions on `x[t-1]` and is `N(LEVEL[type of t+h] + PHI^(h+1) x[t-1],
V)` with `V = SIGMA^2 (1 - PHI^(2 (h+1))) / (1 - PHI^2)`. Quantiles of it are the "truth" a
benchmark's coverage is measured against.

Stdlib only; the tests import it by its bare name.
"""

from __future__ import annotations

import json
import math
import random
from dataclasses import dataclass, field
from datetime import date, time, timedelta
from pathlib import Path
from statistics import NormalDist
from typing import Dict, List, Sequence

from repo_model import protocol_benchmarks as pb
from repo_model import richer_targets as rt
from repo_model import scoring_protocol as sp
from repo_model.data import DailyObservation, market_holidays
from repo_model.evaluation_splits import load_split_declaration
from repo_model.scoring_protocol import GRID

ROOT = Path(__file__).resolve().parents[1]
#: The registry's own availability declarations, so the benchmarks' as-of guards run as on the real panel.
REGISTRY = json.loads((ROOT / "metadata" / "sources.json").read_text(encoding="utf-8"))
SPLITS = load_split_declaration(ROOT / "metadata" / "evaluation_splits.json")
DECISION = time(16, 0)
FIRST_DAY = date(2018, 1, 2)
LAST_DAY = date(2021, 12, 31)
#: The rate the simulated SOFR is measured against, in percent.
IORB = 2.0
QUARTER_MONTHS = (3, 6, 9, 12)
#: Months in which a tax date falls, on the first row on or after the 15th.
TAX_MONTHS = (1, 4, 6, 9, 12)
EVALUATION_FIRST = date(2020, 1, 2)
LOW, HIGH = GRID.index(0.05), GRID.index(0.95)


@dataclass(frozen=True)
class ProcessSpec:
    phi: float = 0.7
    sigma: float = 1.0
    levels: Dict[str, float] = field(
        default_factory=lambda: {"ordinary": 0.0, "tax_date": 2.0, "month_end": 3.0, "quarter_end": 8.0}
    )


@dataclass
class Sample:
    spec: ProcessSpec
    rows: List[DailyObservation]
    kinds: List[str]
    x: List[float]
    spreads: List[float]


def business_days(first: date = FIRST_DAY, last: date = LAST_DAY) -> List[date]:
    closed = market_holidays().closed
    out, day = [], first
    while day <= last:
        if day.weekday() < 5 and day not in closed:
            out.append(day)
        day += timedelta(days=1)
    return out


def day_kinds(days: Sequence[date]) -> List[str]:
    """The type of each row: quarter-end, month-end, tax date, ordinary, in that precedence."""

    kinds = ["ordinary"] * len(days)
    month_rows: Dict[tuple, List[int]] = {}
    for i, day in enumerate(days):
        month_rows.setdefault((day.year, day.month), []).append(i)
    for (year, month), rows in month_rows.items():
        taxed = next((i for i in rows if days[i].day >= 15), None)
        if month in TAX_MONTHS and taxed is not None:
            kinds[taxed] = "tax_date"
        for i in rows[-2:]:
            kinds[i] = "month_end"
        if month in QUARTER_MONTHS:
            kinds[rows[-1]] = "quarter_end"
    return kinds


def _observation(day: date, kind: str, spread: float) -> DailyObservation:
    next_month = date(day.year + day.month // 12, day.month % 12 + 1, 1)
    return DailyObservation(
        day,
        {
            "sofr": IORB + spread / 100.0,
            "iorb": IORB,
            "quarter_end": 1.0 if kind == "quarter_end" else 0.0,
            "tax_date": 1.0 if kind == "tax_date" else 0.0,
            "days_to_month_end": float((next_month - timedelta(days=1) - day).days),
        },
    )


def _panel(days: Sequence[date], kinds: Sequence[str], spreads: Sequence[float]) -> List[DailyObservation]:
    return [_observation(d, k, s) for d, k, s in zip(days, kinds, spreads)]


def simulate(spec: ProcessSpec, seed: int) -> Sample:
    rng = random.Random(seed)
    days = business_days()
    kinds = day_kinds(days)
    stationary = spec.sigma / math.sqrt(1.0 - spec.phi ** 2)
    x, previous = [], rng.gauss(0.0, stationary)
    for _ in days:
        previous = spec.phi * previous + rng.gauss(0.0, spec.sigma)
        x.append(previous)
    spreads = [spec.levels[k] + v for k, v in zip(kinds, x)]
    return Sample(spec, _panel(days, kinds, spreads), kinds, x, spreads)


def ramp_panel(step: float) -> List[DailyObservation]:
    """A spread that rises `step` bp every row: every h-row change is exactly `h * step`."""

    days = business_days()
    return _panel(days, day_kinds(days), [step * i for i in range(len(days))])


def level_panel(levels: Dict[str, float]):
    """A spread that is the level of the day's type, with no noise, and the rows' types."""

    days = business_days()
    kinds = day_kinds(days)
    return _panel(days, kinds, [levels[k] for k in kinds]), kinds


# -- the hand computation, written without the module ----------------------------------------------------------------


def years_back(day: date, years: int) -> date:
    try:
        return day.replace(year=day.year - years)
    except ValueError:
        return day.replace(year=day.year - years, day=28)


def first_row_after(days: Sequence[date], cutoff: date) -> int:
    return next(i for i, day in enumerate(days) if day > cutoff)


def quantiles_of(values: Sequence[float]) -> List[float]:
    """Linearly interpolated quantiles at the protocol's levels, `low + w (high - low)`."""

    ordered = sorted(values)
    out = []
    for p in GRID:
        pos = p * (len(ordered) - 1)
        low = int(pos)
        w = pos - low
        out.append(ordered[low] if w == 0 else ordered[low] + w * (ordered[low + 1] - ordered[low]))
    return out


def hand_b1(sample: Sample, t: int, h: int) -> List[float]:
    days = [row.date for row in sample.rows]
    anchor = t - 1
    first = first_row_after(days, years_back(days[t], 2))
    changes = [sample.spreads[s] - sample.spreads[s - h] for s in range(max(first, h), anchor + 1)]
    return [sample.spreads[anchor] + q for q in quantiles_of(changes)]


def hand_b2(sample: Sample, t: int, h: int, last: int = None) -> List[float]:
    """The same-type spreads of the trailing year up to row `last` (default: the anchor)."""

    days = [row.date for row in sample.rows]
    last = t - 1 if last is None else last
    first = first_row_after(days, years_back(days[t], 1))
    kind = sample.kinds[t + h]
    return quantiles_of([sample.spreads[s] for s in range(first, last + 1) if sample.kinds[s] == kind])


# -- the known truth -------------------------------------------------------------------------------------------------


def true_sd(spec: ProcessSpec, h: int) -> float:
    d = h + 1
    return spec.sigma * math.sqrt((1.0 - spec.phi ** (2 * d)) / (1.0 - spec.phi ** 2))


def true_mean(sample: Sample, t: int, h: int) -> float:
    return sample.spec.levels[sample.kinds[t + h]] + sample.spec.phi ** (h + 1) * sample.x[t - 1]


def true_quantiles(sample: Sample, t: int, h: int) -> List[float]:
    law = NormalDist(true_mean(sample, t, h), true_sd(sample.spec, h))
    return [law.inv_cdf(p) for p in GRID]


def exact_coverage(sample: Sample, t: int, h: int, quantiles: Sequence[float]) -> float:
    """The true probability that row t + h falls in the forecast's central 90% interval."""

    law = NormalDist(true_mean(sample, t, h), true_sd(sample.spec, h))
    return law.cdf(quantiles[HIGH]) - law.cdf(quantiles[LOW])


def realised_coverage(sample: Sample, t: int, h: int, quantiles: Sequence[float]) -> float:
    return 1.0 if quantiles[LOW] <= sample.spreads[t + h] <= quantiles[HIGH] else 0.0


# -- a forecaster that does not copy a calendar spike (#741) ----------------------------------------------------------


def spike_blind_forecast(panel: Sequence[DailyObservation], t: int, *, splits=None):
    """B1 with the anchor's spread replaced by the last ordinary-day spread at or before the anchor.

    The forecaster of finding #741: no parameter, no model of the ordinary days. On an ordinary anchor it is B1
    exactly; on a quarter-end, tax-date or month-end anchor it declines to carry the spike forward. It reads
    nothing after the anchor (B1's own `_anchor` runs both as-of guards).
    """

    splits = SPLITS if splits is None else splits
    b1 = pb.b1_forecast(panel, t, registry=REGISTRY, decision_time=DECISION)
    anchor = pb._anchor(panel, t, REGISTRY, DECISION)
    last = next(
        s for s in range(anchor, -1, -1) if splits.reporting_day_type(panel[s].date, panel[s].values) == "ordinary"
    )
    shift = panel[last].spread_bps - panel[anchor].spread_bps
    return {h: [q + shift for q in b1[h]] for h in b1}


def _skill(benchmark: Sequence[float], candidate: Sequence[float]) -> float:
    """`mean(d) / mean(benchmark)` with `d = benchmark - candidate`: positive favours the candidate (§5)."""

    return (sum(benchmark) - sum(candidate)) / sum(benchmark)


def spike_blind_replicate(spec: ProcessSpec, seed: int, decision_step: int = 3):
    """One simulated panel: per decision day, B1's and the spike-blind forecaster's mean grid CRPS and the anchor's type.

    Returns `(rows, kinds)` where each row is `(anchor type, B1 score, candidate score)`, over the evaluation
    decisions (every `decision_step`-th row from `EVALUATION_FIRST`), the score being the mean over the five
    leads as in `scoring_protocol.day_scores`.
    """

    sample = simulate(spec, seed)
    days = [row.date for row in sample.rows]
    start = next(i for i, d in enumerate(days) if d >= EVALUATION_FIRST)
    out = []
    for t in range(start, len(days) - 5, decision_step):
        b1 = pb.b1_forecast(sample.rows, t, registry=REGISTRY, decision_time=DECISION)
        mine = spike_blind_forecast(sample.rows, t)
        score = lambda f: sum(sp.grid_crps(f[h], sample.spreads[t + h]) for h in sp.HORIZONS) / len(sp.HORIZONS)  # noqa: E731
        out.append((sample.kinds[t - 1], score(b1), score(mine)))
    return out


def spike_blind_report(replicates: int, seed: int, decision_step: int = 3, spec: ProcessSpec = None):
    """Skill of the spike-blind forecaster against B1, pooled and by the anchor's type, over simulated panels.

    Per replicate the skill is the pooled one of the protocol (`mean(d) / mean(B1)`); a cell is the mean over
    replicates with a normal-approximation 95% interval across them, and `share_at_mme` is the share of
    replicates whose skill is at least `scoring_protocol.MME`.
    """

    spec = ProcessSpec() if spec is None else spec
    groups = ("pooled", "ordinary", "month_end", "tax_date", "quarter_end")
    skills = {g: [] for g in groups}
    days = {g: 0 for g in groups}
    for r in range(replicates):
        rows = spike_blind_replicate(spec, seed + r, decision_step)
        for g in groups:
            kept = [(b, c) for kind, b, c in rows if g in ("pooled", kind)]
            if kept and sum(b for b, _ in kept) > 0:
                skills[g].append(_skill([b for b, _ in kept], [c for _, c in kept]))
                days[g] += len(kept)
    out = {}
    for g in groups:
        mean, interval = _interval(skills[g])
        out[g] = {
            "skill": mean, "interval": interval, "replicates": len(skills[g]),
            "days": days[g] / max(len(skills[g]), 1),
            "share_at_mme": sum(1 for v in skills[g] if v >= sp.MME) / max(len(skills[g]), 1),
        }
    return out


def spike_blind_markdown(report) -> str:
    lines = ["| anchor day type | decision days per panel | skill against B1 | 95% interval | share of panels at or above the MME |", "|---|---|---|---|---|"]
    for group, c in report.items():
        lines.append(
            f"| {group} | {c['days']:.0f} | {c['skill']:+.2%} | [{c['interval'][0]:+.2%}, {c['interval'][1]:+.2%}] | {c['share_at_mme']:.0%} |"
        )
    return "\n".join(lines)


# -- the report ------------------------------------------------------------------------------------------------------


def _interval(values: Sequence[float]):
    """The mean of `values` (one per replicate) and its 95% interval, normal approximation."""

    n = len(values)
    mean = sum(values) / n
    sd = math.sqrt(sum((v - mean) ** 2 for v in values) / (n - 1)) if n > 1 else 0.0
    half = 1.96 * sd / math.sqrt(n)
    return mean, (mean - half, mean + half)


def coverage_report(replicates: int, seed: int, decision_step: int = 5, spec: ProcessSpec = None):
    """Per benchmark and lead, the central 90% coverage over `replicates` simulated panels.

    `exact` is the true probability, under the process's conditional law at each decision,
    that the target falls in the benchmark's 5th to 95th percentile interval; `realised` is
    the share of simulated targets that did. Each is averaged over the evaluation decisions
    (every `decision_step`-th row from 2020-01-02) and then over the replicates; the interval
    is the normal-approximation 95% interval of that mean across replicates.
    """

    spec = ProcessSpec() if spec is None else spec
    names = ("B1", "B2", "richer_targets B1")
    exact = {n: {h: [] for h in sp.HORIZONS} for n in names}
    realised = {n: {h: [] for h in sp.HORIZONS} for n in names}
    for r in range(replicates):
        sample = simulate(spec, seed + r)
        days = [row.date for row in sample.rows]
        spreads = [row.spread_bps for row in sample.rows]
        start = next(i for i, d in enumerate(days) if d >= EVALUATION_FIRST)
        cells = {n: {h: ([], []) for h in sp.HORIZONS} for n in names}
        for t in range(start, len(days) - 5, decision_step):
            forecasts = {
                "B1": pb.b1_forecast(sample.rows, t, registry=REGISTRY, decision_time=DECISION),
                "B2": pb.b2_forecast(sample.rows, t, registry=REGISTRY, decision_time=DECISION, splits=SPLITS),
            }
            first = first_row_after(days, years_back(days[t], 2))
            forecasts["richer_targets B1"] = {
                h: rt.b1_quantiles(spreads, days, t - 1, h, first=first) for h in sp.HORIZONS
            }
            for n in names:
                for h in sp.HORIZONS:
                    q = forecasts[n][h]
                    cells[n][h][0].append(exact_coverage(sample, t, h, q))
                    cells[n][h][1].append(realised_coverage(sample, t, h, q))
        for n in names:
            for h in sp.HORIZONS:
                e, o = cells[n][h]
                exact[n][h].append(sum(e) / len(e))
                realised[n][h].append(sum(o) / len(o))
    out = {}
    for n in names:
        out[n] = {}
        for h in sp.HORIZONS:
            e, e_ci = _interval(exact[n][h])
            o, o_ci = _interval(realised[n][h])
            out[n][h] = {"exact": e, "exact_interval": e_ci, "realised": o, "realised_interval": o_ci}
    return out


def markdown(report) -> str:
    lines = ["| Benchmark | Lead | True coverage | 95% interval | Realised coverage | 95% interval |", "|---|---|---|---|---|---|"]
    for name, leads in report.items():
        for h, c in leads.items():
            lines.append(
                f"| {name} | {h} | {c['exact']:.3f} | [{c['exact_interval'][0]:.3f}, {c['exact_interval'][1]:.3f}] "
                f"| {c['realised']:.3f} | [{c['realised_interval'][0]:.3f}, {c['realised_interval'][1]:.3f}] |"
            )
    return "\n".join(lines)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Simulated-panel reports on the benchmarks of protocol v1 (#762, #741).")
    parser.add_argument("report", nargs="?", choices=("coverage", "spike-blind", "spike-blind-no-spikes"), default="coverage")
    parser.add_argument("--replicates", type=int, default=200)
    parser.add_argument("--seed", type=int, default=None)
    parser.add_argument("--decision-step", type=int, default=3)
    args = parser.parse_args()
    if args.report == "coverage":
        print(markdown(coverage_report(args.replicates, 762000 if args.seed is None else args.seed, args.decision_step)))
    else:
        flat = ProcessSpec(levels={k: 0.0 for k in ProcessSpec().levels}) if args.report.endswith("no-spikes") else None
        print(spike_blind_markdown(spike_blind_report(args.replicates, 741000 if args.seed is None else args.seed, args.decision_step, flat)))
