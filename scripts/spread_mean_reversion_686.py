"""Persistence with partial mean reversion toward a local level: scoring and report (#686; H5, development tier).

A scratch measurement, not a record: it writes JSON and Markdown to the paths it is given and nothing into `docs/runs/`.
Every choice is in `metadata/spread_distribution_686.json`, which this script refuses to read unless it is committed and
unchanged. The model is `repo_model.spread_mean_reversion`. It is scored with the scorer of scoring protocol v1
(`repo_model.scoring_protocol`, #655) at the development tier, against B1 and B2 (`repo_model.protocol_benchmarks`) and
against the published distribution on the five levels both forecasts have. Scored days are decision days whose five
targets are on or before 2025-12-31; no later day is read (`docs/decisions/lockbox.md`). Nothing here is a verdict
(scoring protocol v1, #640): the result is exploration on development data.

    PYTHONPATH=src python3 -m repo_model.cli build --raw-root tests/fixtures/snapshots/funding_inputs \\
        --output /tmp/funding_panel.csv --build-cutoff 2026-09-08T21:31:42+00:00 --decision-time 16:00:00
    PYTHONPATH=src python3 -m repo_model.cli verify-panel /tmp/funding_panel.csv --manifest metadata/funding_panel_manifest.json
    PYTHONPATH=src python3 scripts/spread_mean_reversion_686.py score --panel /tmp/funding_panel.csv \\
        --output docs/pivot/evidence/spread-mean-reversion/score.json \\
        --markdown docs/pivot/evidence/spread-mean-reversion/report.md
    PYTHONPATH=src python3 scripts/spread_mean_reversion_686.py page \\
        --score docs/pivot/evidence/spread-mean-reversion/score.json --output docs/pivot/spread-mean-reversion-result.md

Stdlib only.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import date, time
from pathlib import Path
from typing import Dict, Iterable, List, Mapping, Optional, Sequence, Tuple

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))

from repo_model import lockbox, protocol_benchmarks as pb, scoring_protocol as sp  # noqa: E402
from repo_model import spread_mean_reversion as smr  # noqa: E402
from repo_model.baseline import panel_sha256  # noqa: E402
from repo_model.data import exceeds_bp, load_daily_panel  # noqa: E402
from repo_model.evaluation_splits import load_split_declaration  # noqa: E402
from repo_model.metrics import _quantile, crps_from_quantiles  # noqa: E402
from repo_model.splits import LookAheadError  # noqa: E402

DECLARATION = REPO / "metadata" / "spread_distribution_686.json"
SPLITS = REPO / "metadata" / "evaluation_splits.json"
SOURCES = REPO / "metadata" / "sources.json"
PUBLISHED = REPO / "docs" / "runs" / "published_distribution_daily_h{h}.json"
RECORD_632 = REPO / "docs" / "pivot" / "evidence" / "spread-distribution" / "distribution.json"
VARIANT_632_B = "spread_q_gbm+two_part+settle+h41+dist_roll"
NAME = "spread_mr_level10"
SEED = 686
LAST_DAY = date(2025, 12, 31)
DECISION_TIME = time(16, 0)
INTERVAL = (0.05, 0.95)
MIN_GROUP_DAYS = 20
FIVE = (0.05, 0.25, 0.5, 0.75, 0.95)
FIVE_AT = tuple(sp.GRID.index(level) for level in FIVE)
THREE_REGIMES = {"2018-19": "2018-19", "2020": "2020-24", "2021-23": "2020-24", "2024": "2020-24", "2025-26": "2025-26"}
MODELS = ("B1", "B2", NAME)


# -- the declaration and the scope ---------------------------------------------------------------------------------


def committed_declaration(path: Path = DECLARATION) -> dict:
    """The declaration, refused unless it is committed and unchanged since `HEAD`."""

    relative = str(path.resolve().relative_to(REPO))
    dirty = subprocess.run(
        ["git", "status", "--porcelain", "--", relative], cwd=REPO, capture_output=True, text=True, check=True
    ).stdout.strip()
    if dirty:
        raise SystemExit(f"{relative} is not committed ({dirty}); a declaration is made before any score")
    return json.loads(path.read_text(encoding="utf-8"))


def require_scored_days(days: Iterable[date], last: date = LAST_DAY) -> None:
    """Refuse a day after `last`, the declared end of the scored days, and a locked day.

    Mutation record: replacing `if day > last:` with `if day > last + timedelta(days=400):` makes
    `test_spread_mean_reversion_686_script.ScopeTests.test_a_day_after_the_declared_end_is_refused` fail with
    `AssertionError` ("LookAheadError not raised"); restored, it passes.

    Raises:
        LookAheadError: a day after `last`, or in a locked tier.
    """

    days = list(days)
    for day in sorted(days):
        if day > last:
            raise LookAheadError(
                f"{day} is after {last}, the last day #686 scores; the declaration admits no later day"
            )
    lockbox.require_unlocked(days, where="scripts/spread_mean_reversion_686")


# -- the statistics ------------------------------------------------------------------------------------------------


def interval(draws: Sequence[float]) -> List[float]:
    """The 5th and 95th percentile of sorted bootstrap draws."""

    return [_quantile(draws, INTERVAL[0]), _quantile(draws, INTERVAL[1])]


def paired_row(test: sp.PairedTest) -> dict:
    """One paired test as the report records it: sign as the protocol's, positive favours the candidate."""

    return {
        "days": test.n,
        "benchmark_mean": test.benchmark_mean,
        "candidate_mean": test.benchmark_mean - test.mean_difference,
        "difference": test.mean_difference,
        "difference_interval": interval(test.mean_difference_draws),
        "skill": test.skill,
        "skill_interval": interval(test.skill_draws),
        "dm_statistic": None if test.dm_statistic != test.dm_statistic else test.dm_statistic,
        "dm_p_value": None if test.dm_p_value != test.dm_p_value else test.dm_p_value,
    }


def run_pairs(benchmarks: Mapping[str, Mapping[date, float]], candidate: Mapping[date, float], days: Sequence[date],
              seed: int = SEED, draws: int = sp.DRAWS) -> Dict[str, dict]:
    """Each benchmark's paired test against the candidate on `days`, on one resample stream."""

    names = list(benchmarks)
    pairs = [({d: benchmarks[n][d] for d in days}, {d: candidate[d] for d in days}) for n in names]
    try:
        return {n: paired_row(t) for n, t in zip(names, sp.paired_tests(pairs, seed=seed, draws=draws))}
    except sp.ProtocolError as error:
        if "scores zero" not in str(error):
            raise
        # Skill is undefined where a benchmark scores zero on a resample (the upper-tail score of a group in which no
        # forecast and no outcome is above 0 bp). Said so, with the means, instead of a number.
        return {n: {"undefined": str(error), "days": len(days),
                    "benchmark_mean": sum(benchmarks[n][d] for d in days) / len(days),
                    "candidate_mean": sum(candidate[d] for d in days) / len(days)} for n in names}


def group_days(series_days: Iterable[date], labels: Mapping[date, str]) -> Dict[str, List[date]]:
    out: Dict[str, List[date]] = {}
    for day in sorted(series_days):
        out.setdefault(labels[day], []).append(day)
    return out


# -- forecasts and scores ------------------------------------------------------------------------------------------


class Frame:
    """The panel, the scored decision days and the three models' forecasts on them."""

    def __init__(self, panel, splits, registry, declaration):
        self.panel, self.splits, self.registry, self.declaration = panel, splits, registry, declaration
        self.dates = [row.date for row in panel]
        self.position = {day: i for i, day in enumerate(self.dates)}
        self.outcome = {row.date: row.spread_bps for row in panel if row.date <= LAST_DAY}
        self.values = {row.date: row.values for row in panel}
        self.settings = dict(registry=registry, decision_time=DECISION_TIME, splits=splits)

    def target(self, decision: date, lead: int) -> date:
        return self.dates[self.position[decision] + lead]

    def regime(self, day: date) -> str:
        return self.splits.regime(day)

    def day_type(self, day: date) -> str:
        return self.splits.reporting_day_type(day, self.values[day])


def build_frame(panel, splits, registry, declaration) -> Tuple[Frame, dict, dict]:
    """The decision days with a forecast from the candidate, B1 and B2, whose five targets are scored days."""

    frame = Frame(panel, splits, registry, declaration)
    candidate_days = [
        day for i, day in enumerate(frame.dates)
        if i + max(sp.HORIZONS) < len(panel) and frame.dates[i + max(sp.HORIZONS)] <= LAST_DAY
    ]
    require_scored_days(candidate_days)
    walk = smr.walk(panel, candidate_days, **frame.settings)
    b1, b2, dropped = {}, {}, []
    for day in walk.forecasts:
        index = frame.position[day]
        try:
            one = pb.b1_forecast(panel, index, registry=registry, decision_time=DECISION_TIME)
            two = pb.b2_forecast(panel, index, registry=registry, decision_time=DECISION_TIME, splits=splits)
        except sp.ProtocolError:
            dropped.append(day)
            continue
        b1[day], b2[day] = one, two
    days = [day for day in walk.forecasts if day in b1]
    frame.days = days
    frame.forecasts = {
        "B1": b1, "B2": b2, NAME: {day: walk.forecasts[day] for day in days},
    }
    notes = {
        "decision_days_offered": len(candidate_days),
        "candidate_skipped_for_history": len(walk.skipped),
        "benchmark_missing": [d.isoformat() for d in dropped],
        "scored_decision_days": len(days),
        "first": days[0].isoformat(), "last": days[-1].isoformat(),
        "last_target": frame.target(days[-1], max(sp.HORIZONS)).isoformat(),
        "refits": len(walk.fits),
    }
    return frame, notes, {"fits": walk.fits, "fit_used": walk.fit_used}


def cell_scores(frame: Frame, model: str, score=sp.grid_crps) -> Dict[Tuple[date, int], float]:
    """`score` of every (decision day, lead) cell, after the scored days are checked."""

    forecasts = frame.forecasts[model]
    cells = {(d, h): frame.target(d, h) for d in frame.days for h in sp.HORIZONS}
    require_scored_days(set(d for d, _ in cells) | set(cells.values()))
    return {(d, h): score(forecasts[d][h], frame.outcome[t]) for (d, h), t in cells.items()}


def five_level_cells(frame: Frame, forecasts: Mapping[date, Mapping[int, Sequence[float]]],
                     days: Sequence[date]) -> Dict[Tuple[date, int], float]:
    """The five-level CRPS of every cell of `forecasts` (23 quantiles are read at the five levels)."""

    targets = {(d, h): frame.target(d, h) for d in days for h in sp.HORIZONS}
    lockbox.require_unlocked(set(days) | set(targets.values()), where="scripts/spread_mean_reversion_686.five_level_cells")
    return {
        (d, h): crps_from_quantiles(FIVE, [forecasts[d][h][i] for i in FIVE_AT], frame.outcome[t])
        for (d, h), t in targets.items()
    }


def by_decision(cells: Mapping[Tuple[date, int], float]) -> Dict[date, float]:
    sums: Dict[date, List[float]] = {}
    for (d, _), v in cells.items():
        sums.setdefault(d, []).append(v)
    return {d: sum(v) / len(v) for d, v in sums.items()}


def by_target(frame: Frame, cells: Mapping[Tuple[date, int], float]) -> Dict[date, float]:
    sums: Dict[date, List[float]] = {}
    for (d, h), v in cells.items():
        sums.setdefault(frame.target(d, h), []).append(v)
    return {t: sum(v) / len(v) for t, v in sums.items()}


def by_lead(cells: Mapping[Tuple[date, int], float], lead: int) -> Dict[date, float]:
    return {d: v for (d, h), v in cells.items() if h == lead}


# -- the tail ------------------------------------------------------------------------------------------------------


def tail_cells(frame: Frame, model: str, tau: float = smr.TAIL_TAU) -> Dict[Tuple[date, int], Tuple[float, float]]:
    """(P(spread > tau), event) of every cell: the probability is read off the model's own distribution."""

    forecasts = frame.forecasts[model]
    out = {}
    for d in frame.days:
        for h in sp.HORIZONS:
            out[(d, h)] = (smr.exceedance(forecasts[d][h], tau),
                           1.0 if exceeds_bp(frame.outcome[frame.target(d, h)], tau) else 0.0)
    return out


def reliability(frame: Frame, tails: Mapping[str, Mapping], select) -> Dict[str, dict]:
    """Mean predicted, realised share and Brier of the cells `select(decision, lead, target)` keeps, by model."""

    out = {}
    for model, cells in tails.items():
        kept = [(p, e) for (d, h), (p, e) in cells.items() if select(d, h, frame.target(d, h))]
        n = len(kept)
        if not n:
            out[model] = None
            continue
        pred, real = sum(p for p, _ in kept) / n, sum(e for _, e in kept) / n
        out[model] = {"cells": n, "predicted": pred, "realised": real, "realised_minus_predicted": real - pred,
                      "brier": sum((p - e) ** 2 for p, e in kept) / n}
    return out


# -- the published distribution ------------------------------------------------------------------------------------


def read_published() -> Dict[int, Dict[date, Tuple[Sequence[float], float]]]:
    """Lead -> target day -> (five quantiles, actual), the published distribution's daily files to LAST_DAY."""

    out = {}
    for h in sp.HORIZONS:
        record = json.loads(Path(str(PUBLISHED).format(h=h)).read_text(encoding="utf-8"))
        if tuple(record["levels"]) != FIVE:
            raise ValueError(f"the published distribution's levels at h = {h} are not the five this script reads")
        out[h] = {
            date.fromisoformat(r["date"]): (r["quantiles_bps"], r["actual_bps"])
            for r in record["days"] if date.fromisoformat(r["date"]) <= LAST_DAY
        }
    return out


def published_cells(frame: Frame, published, days: Sequence[date]) -> Dict[Tuple[date, int], float]:
    targets = {(d, h): frame.target(d, h) for d in days for h in sp.HORIZONS}
    lockbox.require_unlocked(set(targets.values()), where="scripts/spread_mean_reversion_686.published_cells")
    out = {}
    for (d, h), t in targets.items():
        entry = published[h].get(t)
        if entry is not None:
            out[(d, h)] = crps_from_quantiles(FIVE, entry[0], entry[1])
    return out


# -- the report ----------------------------------------------------------------------------------------------------


def score(args) -> int:
    declaration = committed_declaration()
    panel_path = Path(args.panel)
    panel = load_daily_panel(panel_path)
    splits = load_split_declaration(SPLITS)
    registry = json.loads(SOURCES.read_text(encoding="utf-8"))
    frame, notes, fit_info = build_frame(panel, splits, registry, declaration)
    days = frame.days
    draws = args.draws

    crps = {m: cell_scores(frame, m) for m in MODELS}
    tw = {m: cell_scores(frame, m, sp.upper_tail_twcrps) for m in MODELS}
    # the module's own day_scores (which guards every day) must agree with the cell means
    for label, cells, fn in (("grid CRPS", crps, sp.grid_crps), ("upper-tail twCRPS", tw, sp.upper_tail_twcrps)):
        for m in MODELS:
            official = sp.day_scores(frame.forecasts[m], frame.outcome, frame.dates, score=fn)
            mine = by_decision(cells[m])
            if set(official) != set(mine) or any(abs(official[d] - mine[d]) > 1e-9 for d in mine):
                raise SystemExit(f"{label} of {m}: the cell means differ from scoring_protocol.day_scores")

    result: dict = {"issue": 686, "declaration": str(DECLARATION.relative_to(REPO)), "panel_sha256": panel_sha256(panel_path),
                    "label": "development, not a verdict", "seed": SEED, "draws": draws, "notes": notes,
                    "fit": {"refits": [
                        {"fitted_on": day.isoformat(), "phi": fit.phi, "pairs": {str(h): n for h, n in fit.pairs.items()}}
                        for day, fit in sorted(fit_info["fits"].items())]}}

    def bench(table, grain):
        return {m: grain(table[m]) for m in MODELS}

    # primary and key secondary, one number per decision day
    primary = {}
    for label, table in (("grid_crps", crps), ("upper_tail_twcrps", tw)):
        per = bench(table, by_decision)
        primary[label] = {
            "means": {m: sum(per[m].values()) / len(per[m]) for m in MODELS},
            "vs": run_pairs({"B1": per["B1"], "B2": per["B2"]}, per[NAME], days, draws=draws),
        }
        primary[label]["by_lead"] = {}
        for h in sp.HORIZONS:
            lead = {m: by_lead(table[m], h) for m in MODELS}
            primary[label]["by_lead"][str(h)] = {
                "means": {m: sum(lead[m].values()) / len(lead[m]) for m in MODELS},
                "vs": run_pairs({"B1": lead["B1"], "B2": lead["B2"]}, lead[NAME], days, draws=draws),
            }
    result["primary"] = primary

    # splits on the target day
    tgt = {label: bench(table, lambda c: by_target(frame, c)) for label, table in (("grid_crps", crps), ("upper_tail_twcrps", tw))}
    target_days = sorted(tgt["grid_crps"][NAME])
    regime_of = {t: frame.regime(t) for t in target_days}
    result["splits"] = {"unit": "target day: the mean over the leads that forecast it"}
    for split, labels in (("regime", regime_of), ("regime_three", {t: THREE_REGIMES[regime_of[t]] for t in target_days}),
                          ("day_type", {t: frame.day_type(t) for t in target_days})):
        result["splits"][split] = {}
        for label, members in group_days(target_days, labels).items():
            if len(members) < MIN_GROUP_DAYS:
                result["splits"][split][label] = {"days": len(members), "note": f"fewer than {MIN_GROUP_DAYS} days; not tested"}
                continue
            result["splits"][split][label] = {"days": len(members)}
            for metric in ("grid_crps", "upper_tail_twcrps"):
                series = tgt[metric]
                result["splits"][split][label][metric] = {
                    "means": {m: sum(series[m][t] for t in members) / len(members) for m in MODELS},
                    "vs": run_pairs({"B1": series["B1"], "B2": series["B2"]}, series[NAME], members, draws=draws),
                }

    # the tail: reliability of P(spread > +5 bp), and Brier
    tails = {m: tail_cells(frame, m) for m in MODELS}
    ordinary = lambda d, h, t: frame.day_type(t) == "ordinary"  # noqa: E731
    everyday = lambda d, h, t: True  # noqa: E731
    result["tail"] = {"tau_bp": smr.TAIL_TAU, "reading": declaration["tail"]["reading"], "by_regime": {}}
    for scope, select in (("ordinary", ordinary), ("all", everyday)):
        result["tail"]["by_regime"][scope] = {}
        for regime in splits.regime_labels:
            if not any(frame.regime(t) == regime for t in target_days):
                continue
            result["tail"]["by_regime"][scope][regime] = {
                "pooled": reliability(frame, tails, lambda d, h, t, s=select, r=regime: s(d, h, t) and frame.regime(t) == r),
                "by_lead": {str(h): reliability(
                    frame, tails, lambda d, hh, t, s=select, r=regime, h=h: s(d, hh, t) and hh == h and frame.regime(t) == r)
                    for h in sp.HORIZONS},
            }
        result["tail"]["by_regime"][scope]["all regimes"] = {
            "pooled": reliability(frame, tails, select),
            "by_lead": {str(h): reliability(frame, tails, lambda d, hh, t, s=select, h=h: s(d, hh, t) and hh == h)
                        for h in sp.HORIZONS},
        }
    brier = {m: _target_mean(frame, tails[m], lambda p, e: (p - e) ** 2) for m in MODELS}
    result["tail"]["brier_vs"] = {}
    for scope, keep in (("ordinary", lambda t: frame.day_type(t) == "ordinary"), ("all", lambda t: True)):
        result["tail"]["brier_vs"][scope] = {}
        regimes = {t: regime_of[t] for t in target_days if keep(t)}
        for label, members in [("all regimes", [t for t in target_days if keep(t)])] + sorted(group_days(regimes, regimes).items()):
            if len(members) < MIN_GROUP_DAYS:
                continue
            result["tail"]["brier_vs"][scope][label] = {
                "days": len(members),
                "means": {m: sum(brier[m][t] for t in members) / len(members) for m in MODELS},
                "vs": run_pairs({"B1": brier["B1"], "B2": brier["B2"]}, brier[NAME], members, draws=draws),
            }

    # the published distribution, on its five levels
    published = read_published()
    five = {m: five_level_cells(frame, frame.forecasts[m], days) for m in MODELS}
    pub = published_cells(frame, published, days)
    complete = [d for d in days if all((d, h) in pub for h in sp.HORIZONS)]
    pub_decision = by_decision({k: v for k, v in pub.items() if k[0] in set(complete)})
    cand_decision = {d: by_decision(five[NAME])[d] for d in complete}
    b1_decision = {d: by_decision(five["B1"])[d] for d in complete}
    b2_decision = {d: by_decision(five["B2"])[d] for d in complete}
    result["published"] = {
        "levels": list(FIVE), "days": len(complete), "days_without_five_published_leads": len(days) - len(complete),
        "means": {"published": sum(pub_decision.values()) / len(complete),
                  NAME: sum(cand_decision.values()) / len(complete),
                  "B1": sum(b1_decision.values()) / len(complete), "B2": sum(b2_decision.values()) / len(complete)},
        "candidate_vs": run_pairs({"published": pub_decision, "B1": b1_decision, "B2": b2_decision}, cand_decision,
                                  complete, draws=draws),
        "by_lead": {}, "by_regime": {}, "by_day_type": {},
    }
    for h in sp.HORIZONS:
        lead_days = [d for d in days if (d, h) in pub]
        result["published"]["by_lead"][str(h)] = {
            "days": len(lead_days),
            "means": {"published": sum(pub[(d, h)] for d in lead_days) / len(lead_days),
                      NAME: sum(five[NAME][(d, h)] for d in lead_days) / len(lead_days)},
            "candidate_vs": run_pairs({"published": {d: pub[(d, h)] for d in lead_days}},
                                      {d: five[NAME][(d, h)] for d in lead_days}, lead_days, draws=draws),
        }
    pub_target = by_target(frame, {k: v for k, v in pub.items()})
    cand_target = {t: v for t, v in by_target(frame, {k: v for k, v in five[NAME].items() if k in pub}).items()}
    both = sorted(t for t in pub_target if t in cand_target)
    for split, labels in (("by_regime", {t: frame.regime(t) for t in both}), ("by_day_type", {t: frame.day_type(t) for t in both})):
        for label, members in group_days(both, labels).items():
            if len(members) >= MIN_GROUP_DAYS:
                result["published"][split][label] = {
                    "days": len(members),
                    "means": {"published": sum(pub_target[t] for t in members) / len(members),
                              NAME: sum(cand_target[t] for t in members) / len(members)},
                    "candidate_vs": run_pairs({"published": pub_target}, cand_target, members, draws=draws),
                }

    # variant (b) of #632, recorded, set beside this model on the same horizon
    record = json.loads(RECORD_632.read_text(encoding="utf-8"))
    result["variant_b_632"] = {"variant": VARIANT_632_B, "note": "recorded aggregates; the daily quantiles are not committed, so this is not a paired test", "by_lead": {}}
    for h in sp.HORIZONS:
        cell = record["horizons"][str(h)][VARIANT_632_B]
        lead_days = [d for d in days if (d, h) in pub]
        result["variant_b_632"]["by_lead"][str(h)] = {
            "recorded": {
                "days": cell["days"], "first": cell["first"], "last": cell["last"],
                "variant_crps": cell["variant"]["crps_bps"], "published_crps": cell["published_distribution"]["crps_bps"],
                "published_minus_variant": cell["paired"]["published_distribution"]["pooled"],
            },
            "this_model": {
                "days": len(lead_days),
                "candidate_crps": result["published"]["by_lead"][str(h)]["means"][NAME],
                "published_crps": result["published"]["by_lead"][str(h)]["means"]["published"],
                "published_minus_candidate": result["published"]["by_lead"][str(h)]["candidate_vs"]["published"]["difference"],
                "published_minus_candidate_interval": result["published"]["by_lead"][str(h)]["candidate_vs"]["published"]["difference_interval"],
            },
        }

    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    Path(args.output).write_text(json.dumps(result, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    if args.markdown:
        Path(args.markdown).parent.mkdir(parents=True, exist_ok=True)
        Path(args.markdown).write_text(render_report(result), encoding="utf-8")
    return 0


def _target_mean(frame: Frame, cells: Mapping[Tuple[date, int], Tuple[float, float]], loss) -> Dict[date, float]:
    sums: Dict[date, List[float]] = {}
    for (d, h), (p, e) in cells.items():
        sums.setdefault(frame.target(d, h), []).append(loss(p, e))
    return {t: sum(v) / len(v) for t, v in sums.items()}


# -- Markdown ------------------------------------------------------------------------------------------------------


def pct(x: Optional[float], signed: bool = True) -> str:
    return "n/a" if x is None else format(100.0 * x, "+.1f" if signed else ".1f") + "%"


def skill_text(row: dict) -> str:
    if "undefined" in row:
        return "undefined (benchmark scores 0)"
    lo, hi = row["skill_interval"]
    return f"{pct(row['skill'])} [{pct(lo)}, {pct(hi)}]"


def diff_text(row: dict, places: int = 3) -> str:
    if "undefined" in row:
        return "undefined"
    lo, hi = row["difference_interval"]
    return f"{row['difference']:+.{places}f} [{lo:+.{places}f}, {hi:+.{places}f}]"


def render_report(r: dict) -> str:
    p = r["primary"]
    n = r["notes"]
    out = [
        "# Persistence with partial mean reversion toward a local level (#686)", "",
        f"Generated by `scripts/spread_mean_reversion_686.py score` from `{r['declaration']}`; not edited by hand. "
        f"**{r['label']}**: development days to {n['last_target']}, no verdict (scoring protocol v1, #640). Panel digest "
        f"`{r['panel_sha256'][:8]}…`. Stationary bootstrap, mean block {sp.BLOCK_LENGTH} business days, {r['draws']:,} draws, seed {r['seed']}; "
        f"intervals are the 5th to 95th percentile of the draws. Skill is `mean(d) / mean(S(benchmark))` with `d = S(benchmark) - S(candidate)`: "
        "positive favours the candidate.", "",
        f"Scored decision days: {n['scored_decision_days']:,} ({n['first']} to {n['last']}; the last target is {n['last_target']}). "
        f"The candidate has no forecast on {n['candidate_skipped_for_history']} early days (history), and B1 or B2 is missing on "
        f"{len(n['benchmark_missing'])}: {', '.join(n['benchmark_missing']) or 'none'}. The fit is renewed {n['refits']} times "
        f"(every {smr.REFIT_EVERY} decision days).", "",
        "## Grid CRPS (23 levels), mean over leads 1 to 5, one number per decision day", "",
        "| | mean bp | vs B1: skill [90%] | vs B2: skill [90%] |", "|---|---|---|---|",
    ]
    for label, key in (("grid CRPS", "grid_crps"), ("upper-tail twCRPS (weight 1{z > 0 bp})", "upper_tail_twcrps")):
        if key == "upper_tail_twcrps":
            out += ["", "## Upper-tail twCRPS", "", "| | mean bp | vs B1: skill [90%] | vs B2: skill [90%] |", "|---|---|---|---|"]
        m = p[key]["means"]
        out.append("| B1 | %.3f | | |" % m["B1"])
        out.append("| B2 | %.3f | | |" % m["B2"])
        out.append("| candidate | %.3f | %s | %s |" % (m[NAME], skill_text(p[key]["vs"]["B1"]), skill_text(p[key]["vs"]["B2"])))
        out += ["", f"By lead ({label}):", "", "| lead | B1 | B2 | candidate | vs B1 [90%] | vs B2 [90%] |", "|---|---|---|---|---|---|"]
        for h, cell in p[key]["by_lead"].items():
            m = cell["means"]
            out.append("| %s | %.3f | %.3f | %.3f | %s | %s |" % (h, m["B1"], m["B2"], m[NAME], skill_text(cell["vs"]["B1"]), skill_text(cell["vs"]["B2"])))
    for split, title in (("regime", "regime (declared)"), ("regime_three", "regime (the directive's three)"), ("day_type", "pressure-day type")):
        for key, label in (("grid_crps", "grid CRPS"), ("upper_tail_twcrps", "upper-tail twCRPS")):
            out += ["", f"## {label} by {title}, on the target day", "",
                    "| group | days | B1 | B2 | candidate | vs B1 [90%] | vs B2 [90%] |", "|---|---|---|---|---|---|---|"]
            for group, cell in r["splits"][split].items():
                if key not in cell:
                    out.append("| %s | %d | %s | | | | |" % (group, cell["days"], cell["note"]))
                    continue
                m = cell[key]["means"]
                out.append("| %s | %d | %.3f | %.3f | %.3f | %s | %s |" % (
                    group, cell["days"], m["B1"], m["B2"], m[NAME], skill_text(cell[key]["vs"]["B1"]), skill_text(cell[key]["vs"]["B2"])))
    out += ["", "## P(spread > +5 bp): reliability, read off each distribution", "",
            f"Mean predicted probability, realised share of target days above +{r['tail']['tau_bp']:g} bp (whole basis points, strictly above), "
            "and realised minus predicted: negative means the model over-forecasts the tail. Pooled over leads 1 to 5; the per-lead cells are in the JSON. "
            "Avenue #675 quotes B1 at -0.06 to -0.085 in 2018-19 and -0.03 to -0.08 in 2025 on ordinary days."]
    for scope in ("ordinary", "all"):
        out += ["", f"{'Ordinary' if scope == 'ordinary' else 'All'} target days:", "",
                "| regime | cells | B1 pred / real / diff | B2 pred / real / diff | candidate pred / real / diff |", "|---|---|---|---|---|"]
        for regime, cell in r["tail"]["by_regime"][scope].items():
            pooled = cell["pooled"]
            if pooled["B1"] is None:
                continue
            parts = ["%.3f / %.3f / %+.3f" % (pooled[m]["predicted"], pooled[m]["realised"], pooled[m]["realised_minus_predicted"]) for m in MODELS]
            out.append("| %s | %d | %s |" % (regime, pooled["B1"]["cells"], " | ".join(parts)))
    out += ["", "Brier score of P(spread > +5 bp) and its paired difference (positive favours the candidate):", ""]
    for scope in ("ordinary", "all"):
        out += [f"{'Ordinary' if scope == 'ordinary' else 'All'} target days:", "",
                "| regime | days | B1 | B2 | candidate | vs B1 [90%] | vs B2 [90%] |", "|---|---|---|---|---|---|---|"]
        for regime, cell in r["tail"]["brier_vs"][scope].items():
            m = cell["means"]
            out.append("| %s | %d | %.4f | %.4f | %.4f | %s | %s |" % (
                regime, cell["days"], m["B1"], m["B2"], m[NAME], skill_text(cell["vs"]["B1"]), skill_text(cell["vs"]["B2"])))
        out.append("")
    pub = r["published"]
    out += ["## The published distribution, on its five levels", "",
            "The published distribution forecasts five levels (0.05, 0.25, 0.5, 0.75, 0.95). It is not put on the 23-level grid (that is "
            "Eleonora's question, `protocol_benchmarks.b3_forecast`); each side is scored on the five levels both have, `metrics.crps_from_quantiles`, "
            "the candidate (and B1, B2) read at their own quantiles at those levels. Mean over the five leads per decision day, paired.", "",
            f"Decision days with all five published leads: {pub['days']:,}.", "",
            "| | mean bp | candidate vs it: skill [90%] | difference [90%] |", "|---|---|---|---|",
            "| published | %.3f | %s | %s |" % (pub["means"]["published"], skill_text(pub["candidate_vs"]["published"]), diff_text(pub["candidate_vs"]["published"])),
            "| B1 (five levels) | %.3f | %s | %s |" % (pub["means"]["B1"], skill_text(pub["candidate_vs"]["B1"]), diff_text(pub["candidate_vs"]["B1"])),
            "| B2 (five levels) | %.3f | %s | %s |" % (pub["means"]["B2"], skill_text(pub["candidate_vs"]["B2"]), diff_text(pub["candidate_vs"]["B2"])),
            "| candidate | %.3f | | |" % pub["means"][NAME], "",
            "By lead, candidate against the published distribution:", "", "| lead | days | published | candidate | skill [90%] |", "|---|---|---|---|---|"]
    for h, cell in pub["by_lead"].items():
        out.append("| %s | %d | %.3f | %.3f | %s |" % (h, cell["days"], cell["means"]["published"], cell["means"][NAME], skill_text(cell["candidate_vs"]["published"])))
    for split, title in (("by_regime", "regime"), ("by_day_type", "pressure-day type")):
        out += ["", f"By {title} (target day), candidate against the published distribution:", "",
                "| group | days | published | candidate | skill [90%] |", "|---|---|---|---|---|"]
        for group, cell in pub[split].items():
            out.append("| %s | %d | %.3f | %.3f | %s |" % (group, cell["days"], cell["means"]["published"], cell["means"][NAME], skill_text(cell["candidate_vs"]["published"])))
    b = r["variant_b_632"]
    out += ["", "## Variant (b) of #632, recorded, beside this model", "",
            f"`{b['variant']}`. {b['note']}. Five-level CRPS in bp. The published distribution is the common reference: the recorded "
            "difference is published minus variant (b) on its days, the other is published minus this model on this model's days; "
            "the day sets differ slightly. The two columns of differences are not a test of one model against the other.", "",
            "| lead | (b) CRPS | published (on (b)'s days) | published minus (b) [90%] | this model CRPS | published (on its days) | published minus this model [90%] |",
            "|---|---|---|---|---|---|---|"]
    for h, cell in b["by_lead"].items():
        rec, mine = cell["recorded"], cell["this_model"]
        lo, hi = rec["published_minus_variant"]["interval"]
        mlo, mhi = mine["published_minus_candidate_interval"]
        out.append("| %s | %.3f | %.3f | %+.3f [%+.3f, %+.3f] | %.3f | %.3f | %+.3f [%+.3f, %+.3f] |" % (
            h, rec["variant_crps"], rec["published_crps"], rec["published_minus_variant"]["mean"], lo, hi,
            mine["candidate_crps"], mine["published_crps"], mine["published_minus_candidate"], mlo, mhi))
    fits = r["fit"]["refits"]
    phis = [f["phi"] for f in fits]
    out += ["", "## The fit", "",
            f"phi is refitted {len(fits)} times; it ranges from {min(phis):.2f} to {max(phis):.2f} (all refits are in the JSON). "
            "The first refit of each calendar year:", "", "| fitted on | phi | training pairs at lead 1 |", "|---|---|---|"]
    seen = set()
    for fit in fits:
        year = fit["fitted_on"][:4]
        if year not in seen:
            seen.add(year)
            out.append("| %s | %.2f | %d |" % (fit["fitted_on"], fit["phi"], fit["pairs"]["1"]))
    out.append("")
    return "\n".join(out)


def page(args) -> int:
    r = json.loads(Path(args.score).read_text(encoding="utf-8"))
    p = r["primary"]["grid_crps"]
    t = r["primary"]["upper_tail_twcrps"]
    pub = r["published"]
    n = r["notes"]
    lines = [
        "# Mean-reverting spread distribution: result (#686)", "",
        "**Hypothesis and step:** H5 (primary goal), research step 2: a candidate spread distribution beyond the phase 2 models. "
        "**Development data only: this is not a verdict** (scoring protocol v1, #640). Generated by "
        "`scripts/spread_mean_reversion_686.py page`; the evidence is in `docs/pivot/evidence/spread-mean-reversion/`.", "",
        "The model: `level + phi^k * (last - level) + eps`, with `level` the median of the last 10 ordinary days, `phi` fitted on a grid, "
        "`eps` the empirical residual quantiles, refitted every 21 decision days (`metadata/spread_distribution_686.json`).", "",
        f"| grid CRPS, {n['scored_decision_days']:,} decision days to {n['last_target']} | mean bp | skill vs B1 [90%] | skill vs B2 [90%] |", "|---|---|---|---|",
        "| B1 | %.3f | | |" % p["means"]["B1"], "| B2 | %.3f | | |" % p["means"]["B2"],
        "| candidate | %.3f | %s | %s |" % (p["means"][NAME], skill_text(p["vs"]["B1"]), skill_text(p["vs"]["B2"])),
        "| upper-tail twCRPS, candidate | %.3f | %s | %s |" % (t["means"][NAME], skill_text(t["vs"]["B1"]), skill_text(t["vs"]["B2"])),
        "| five-level CRPS vs the published distribution | %.3f against %.3f | %s | |" % (
            pub["means"][NAME], pub["means"]["published"], skill_text(pub["candidate_vs"]["published"])),
        "", "The splits by regime and pressure-day type, the reliability of P(spread > +5 bp) within regimes (against avenue #675's numbers), "
        "the Brier scores and the comparison with variant (b) of #632 are in `docs/pivot/evidence/spread-mean-reversion/report.md`.", "",
    ]
    Path(args.output).write_text("\n".join(lines), encoding="utf-8")
    return 0


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="command", required=True)
    s = sub.add_parser("score", help="score the candidate against B1, B2 and the published distribution")
    s.add_argument("--panel", required=True)
    s.add_argument("--output", required=True)
    s.add_argument("--markdown")
    s.add_argument("--draws", type=int, default=sp.DRAWS)
    s.set_defaults(func=score)
    g = sub.add_parser("page", help="write the short result page from a score file")
    g.add_argument("--score", required=True)
    g.add_argument("--output", required=True)
    g.set_defaults(func=page)
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
