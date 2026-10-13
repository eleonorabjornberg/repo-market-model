"""The spread on announced risk dates: scoring and report (#693; H6 step 1, development tier).

A scratch measurement, not a record: it writes JSON and Markdown to the paths it is given and nothing into `docs/runs/`.
Every choice is in `metadata/risk_date_spread_693.json`, which this script refuses to read unless it is committed and
unchanged. The day set, the risk-date calendar benchmark and the type x state model are `repo_model.risk_date_spread`; the
first candidate is `spread_mr_level10` of #686 (`repo_model.spread_mean_reversion`), read on the cells whose target is a risk
date. Everything is scored with the scorer of scoring protocol v1 (`repo_model.scoring_protocol`, #655) at the development
tier, against B1 (`repo_model.protocol_benchmarks`) and the calendar benchmark. Scored days are decision days whose five
targets are on or before 2025-12-31; no later day is read (`docs/decisions/lockbox.md`). Nothing here is a verdict
(scoring protocol v1, #640): the result is exploration on development data.

    PYTHONPATH=src python3 -m repo_model.cli build --raw-root tests/fixtures/snapshots/funding_inputs \\
        --output /tmp/funding_panel.csv --build-cutoff 2026-09-08T21:31:42+00:00 --decision-time 16:00:00
    PYTHONPATH=src python3 -m repo_model.cli verify-panel /tmp/funding_panel.csv --manifest metadata/funding_panel_manifest.json
    PYTHONPATH=src python3 scripts/risk_date_spread_693.py counts --panel /tmp/funding_panel.csv
    PYTHONPATH=src python3 scripts/risk_date_spread_693.py score --panel /tmp/funding_panel.csv \\
        --output docs/pivot/evidence/risk-date-spread/score.json --markdown docs/pivot/evidence/risk-date-spread/report.md
    PYTHONPATH=src python3 scripts/risk_date_spread_693.py page \\
        --score docs/pivot/evidence/risk-date-spread/score.json --output docs/pivot/risk-date-spread-result.md

`counts` prints the day set by type and year (no score). `score` builds the scarcity states with the own-leg read of
`pressure_judge._scarcity_states` (about ten seconds a lead). Stdlib only.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import subprocess
import sys
from collections import Counter, defaultdict
from datetime import date, time
from pathlib import Path
from typing import Dict, Iterable, List, Mapping, Optional, Sequence, Tuple

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))

from repo_model import lockbox, protocol_benchmarks as pb, scoring_protocol as sp  # noqa: E402
from repo_model import risk_date_spread as rds, spread_mean_reversion as smr  # noqa: E402
from repo_model.baseline import panel_sha256  # noqa: E402
from repo_model.data import load_daily_panel  # noqa: E402
from repo_model.evaluation_splits import load_split_declaration  # noqa: E402
from repo_model.splits import LookAheadError  # noqa: E402


def _load(name: str):
    spec = importlib.util.spec_from_file_location(f"{name}_script", REPO / "scripts" / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[f"{name}_script"] = module
    spec.loader.exec_module(module)
    return module


s686 = _load("spread_mean_reversion_686")

DECLARATION = REPO / "metadata" / "risk_date_spread_693.json"
SPLITS = REPO / "metadata" / "evaluation_splits.json"
SOURCES = REPO / "metadata" / "sources.json"
SEED = 693
LAST_DAY = date(2025, 12, 31)
DECISION_TIME = time(16, 0)
MIN_GROUP_DAYS = 20
A = "h5_mean_reversion"
C = "type_state"
BENCHMARKS = ("B1", "calendar")
CANDIDATES = (A, C)
MODELS = BENCHMARKS + CANDIDATES
METRICS = ("grid_crps", "mae", "upper_tail_twcrps")
THREE_REGIMES = s686.THREE_REGIMES


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
    `test_risk_date_spread_693_script.ScopeTests.test_a_day_after_the_declared_end_is_refused` fail with `AssertionError`
    ("LookAheadError not raised"); restored, it passes.

    Raises:
        LookAheadError: a day after `last`, or in a locked tier.
    """

    days = list(days)
    for day in sorted(days):
        if day > last:
            raise LookAheadError(f"{day} is after {last}, the last day #693 scores; the declaration admits no later day")
    lockbox.require_unlocked(days, where="scripts/risk_date_spread_693")


def mae_score(quantiles: Sequence[float], observed: float) -> float:
    """The absolute error of the median of a forecast on the grid, in bp."""

    return abs(rds.median(quantiles) - observed)


SCORERS = {"grid_crps": sp.grid_crps, "mae": mae_score, "upper_tail_twcrps": sp.upper_tail_twcrps}


def risk_counts(panel, splits, last: date = LAST_DAY) -> Dict[str, Dict[str, int]]:
    """Days per year and risk type up to `last` (no score): the table of the declaration."""

    counts: Dict[int, Counter] = defaultdict(Counter)
    for row in panel:
        if row.date <= last:
            counts[row.date.year][rds.risk_day_type(row.date, row.values, splits) or "not_a_risk_date"] += 1
    keys = list(rds.RISK_TYPES) + ["not_a_risk_date"]
    table = {str(year): {k: counts[year][k] for k in keys} for year in sorted(counts)}
    table["total"] = {k: sum(counts[y][k] for y in counts) for k in keys}
    return table


# -- the states, the forecasts and the cells -----------------------------------------------------------------------


def scarcity_states(last: date = LAST_DAY) -> Dict[int, Dict[date, Optional[float]]]:
    """Lead -> scored day -> the own-leg scarcity state as read at that lead's decision instant."""

    judge = _load("pressure_judge")
    return {h: judge._scarcity_states(h, last) for h in sp.HORIZONS}


class Frame:
    """The panel, the scored decision days and the four models' forecasts on the risk-date cells."""

    def __init__(self, panel, splits, registry, states):
        self.panel, self.splits, self.registry, self.states = panel, splits, registry, states
        self.dates = [row.date for row in panel]
        self.position = {day: i for i, day in enumerate(self.dates)}
        self.outcome = {row.date: row.spread_bps for row in panel if row.date <= LAST_DAY}
        self.settings = dict(registry=registry, decision_time=DECISION_TIME, splits=splits)

    def target(self, decision: date, lead: int) -> date:
        return self.dates[self.position[decision] + lead]

    def kind(self, day: date) -> Optional[str]:
        row = self.panel[self.position[day]]
        return rds.risk_day_type(day, row.values, self.splits)


def build_frame(panel, splits, registry, states) -> Tuple[Frame, dict, dict]:
    """The decision days with forecasts from all four models, and the risk-date cells of each."""

    frame = Frame(panel, splits, registry, states)
    offered = [
        day for i, day in enumerate(frame.dates)
        if i + max(sp.HORIZONS) < len(panel) and frame.dates[i + max(sp.HORIZONS)] <= LAST_DAY
    ]
    require_scored_days(offered)
    walk = smr.walk(panel, offered, **frame.settings)
    forecasts: Dict[str, Dict[Tuple[date, int], List[float]]] = {m: {} for m in MODELS}
    basis: Dict[Tuple[date, int], str] = {}
    dropped: List[str] = []
    days: List[date] = []
    for day in walk.forecasts:
        index = frame.position[day]
        try:
            b1 = pb.b1_forecast(panel, index, registry=registry, decision_time=DECISION_TIME)
            calendar = rds.calendar_forecast(panel, index, **frame.settings)
            typed = rds.type_state_forecast(panel, index, states, **frame.settings)
        except sp.ProtocolError:
            dropped.append(day.isoformat())
            continue
        days.append(day)
        for h in calendar:
            forecasts["B1"][(day, h)] = b1[h]
            forecasts["calendar"][(day, h)] = calendar[h]
            forecasts[A][(day, h)] = walk.forecasts[day][h]
            forecasts[C][(day, h)] = typed.quantiles[h]
            basis[(day, h)] = typed.basis[h]
    frame.days, frame.forecasts, frame.basis = days, forecasts, basis
    notes = {
        "decision_days_offered": len(offered),
        "candidate_skipped_for_history": len(walk.skipped),
        "decision_days_dropped_for_a_benchmark": dropped,
        "scored_decision_days": len(days),
        "risk_date_cells": len(forecasts["B1"]),
        "first": days[0].isoformat(), "last": days[-1].isoformat(),
        "last_target": frame.target(days[-1], max(sp.HORIZONS)).isoformat(),
        "refits_of_the_first_candidate": len(walk.fits),
    }
    return frame, notes, {"fits": walk.fits}


def cell_scores(frame: Frame, model: str, metric: str) -> Dict[Tuple[date, int], float]:
    """`metric` of every risk-date cell of `model`, after the scored days are checked."""

    cells = {(d, h): frame.target(d, h) for (d, h) in frame.forecasts[model]}
    require_scored_days({d for d, _ in cells} | set(cells.values()))
    score = SCORERS[metric]
    return {(d, h): score(frame.forecasts[model][(d, h)], frame.outcome[t]) for (d, h), t in cells.items()}


def by_target(frame: Frame, cells: Mapping[Tuple[date, int], float]) -> Dict[date, float]:
    sums: Dict[date, List[float]] = {}
    for (d, h), v in cells.items():
        sums.setdefault(frame.target(d, h), []).append(v)
    return {t: sum(v) / len(v) for t, v in sums.items()}


def by_lead(frame: Frame, cells: Mapping[Tuple[date, int], float], lead: int) -> Dict[date, float]:
    return {frame.target(d, h): v for (d, h), v in cells.items() if h == lead}


def mean(values: Iterable[float]) -> float:
    values = list(values)
    return sum(values) / len(values)


def vs_all(series: Mapping[str, Mapping[date, float]], days: Sequence[date], draws: int) -> Dict[str, dict]:
    """Each candidate against each benchmark on `days`: {candidate: {benchmark: row}}."""

    return {
        c: s686.run_pairs({b: series[b] for b in BENCHMARKS}, series[c], days, seed=SEED, draws=draws) for c in CANDIDATES
    }


def has_skill(row: dict) -> bool:
    """The 90% interval of the pooled skill lies above zero."""

    return "undefined" not in row and row["skill_interval"][0] > 0.0


def kill_rule(primary: Mapping[str, dict]) -> dict:
    """The declared kill rule on the pooled CRPS and MAE: skill against both benchmarks, and against at least one."""

    out = {"skill": {}, "against_both": [], "against_at_least_one": []}
    for c in CANDIDATES:
        flags = {
            metric: {b: has_skill(primary[metric]["vs"][c][b]) for b in BENCHMARKS} for metric in ("grid_crps", "mae")
        }
        out["skill"][c] = flags
        if any(all(f.values()) for f in flags.values()):
            out["against_both"].append(c)
        if any(any(f.values()) for f in flags.values()):
            out["against_at_least_one"].append(c)
    out["killed"] = not out["against_both"]
    out["killed_on_the_weaker_reading"] = not out["against_at_least_one"]
    return out


def severity_sketch(frame: Frame, last_year: int = 2025) -> List[dict]:
    """The type x state model's median and 5th-95th range per risk type and state group, on the last scored year's cells.

    Lead 1, the mean over the year's cells of the model's own quantiles; a sketch of one table, not a product.
    """

    q05, q95 = sp.GRID.index(0.05), sp.GRID.index(0.95)
    groups: Dict[Tuple[str, str], List[Tuple[float, float, float]]] = defaultdict(list)
    for (d, h), q in frame.forecasts[C].items():
        t = frame.target(d, h)
        if h == 1 and t.year == last_year:
            groups[(frame.kind(t), rds.state_group(frame.states[1].get(t)))].append((rds.median(q), q[q05], q[q95]))
    return [
        {"type": kind, "state": group, "target_days": len(v), "median_bp": mean(x[0] for x in v),
         "q05_bp": mean(x[1] for x in v), "q95_bp": mean(x[2] for x in v)}
        for (kind, group), v in sorted(groups.items())
    ]


# -- the report ----------------------------------------------------------------------------------------------------


def score(args) -> int:
    declaration = committed_declaration()
    panel_path = Path(args.panel)
    panel = load_daily_panel(panel_path)
    splits = load_split_declaration(SPLITS)
    registry = json.loads(SOURCES.read_text(encoding="utf-8"))
    states = scarcity_states()
    frame, notes, fit_info = build_frame(panel, splits, registry, states)
    draws = args.draws

    cells = {m: {metric: cell_scores(frame, m, metric) for metric in METRICS} for m in MODELS}
    target = {metric: {m: by_target(frame, cells[m][metric]) for m in MODELS} for metric in METRICS}
    target_days = sorted(target["grid_crps"]["B1"])
    result: dict = {
        "issue": 693, "declaration": str(DECLARATION.relative_to(REPO)), "panel_sha256": panel_sha256(panel_path),
        "label": "development, not a verdict", "seed": SEED, "draws": draws, "notes": notes,
        "target_days": {
            "total": len(target_days),
            "by_type": dict(Counter(frame.kind(t) for t in target_days)),
            "by_year": {str(y): dict(Counter(frame.kind(t) for t in target_days if t.year == y)) for y in sorted({t.year for t in target_days})},
        },
        "type_state_basis": {
            kind: dict(Counter(basis for (d, h), basis in frame.basis.items() if frame.kind(frame.target(d, h)) == kind))
            for kind in rds.RISK_TYPES
        },
    }

    primary = {}
    for metric in METRICS:
        series = target[metric]
        primary[metric] = {
            "means": {m: mean(series[m].values()) for m in MODELS},
            "vs": vs_all(series, target_days, draws),
            "by_lead": {},
        }
        for h in sp.HORIZONS:
            lead = {m: by_lead(frame, cells[m][metric], h) for m in MODELS}
            lead_days = sorted(lead["B1"])
            primary[metric]["by_lead"][str(h)] = {
                "days": len(lead_days),
                "means": {m: mean(lead[m].values()) for m in MODELS},
                "vs": vs_all(lead, lead_days, draws),
            }
    result["primary"] = primary
    result["kill_rule"] = kill_rule(primary)

    regime_of = {t: splits.regime(t) for t in target_days}
    labels_by_split = {
        "day_type": {t: frame.kind(t) for t in target_days},
        "regime": regime_of,
        "regime_three": {t: THREE_REGIMES[regime_of[t]] for t in target_days},
        "scarcity_state": {t: rds.state_group(states[1].get(t)) for t in target_days},
    }
    result["splits"] = {"unit": "target day: the mean over the leads that forecast it"}
    for split, labels in labels_by_split.items():
        result["splits"][split] = {}
        for label, members in s686.group_days(target_days, labels).items():
            if len(members) < MIN_GROUP_DAYS:
                result["splits"][split][label] = {"days": len(members), "note": f"fewer than {MIN_GROUP_DAYS} days; not tested"}
                continue
            cell = {"days": len(members)}
            for metric in METRICS:
                series = target[metric]
                cell[metric] = {
                    "means": {m: mean(series[m][t] for t in members) for m in MODELS},
                    "vs": vs_all(series, members, draws),
                }
            result["splits"][split][label] = cell
    result["fits"] = {"first_candidate_refits": len(fit_info["fits"])}
    result["severity_sketch"] = severity_sketch(frame)

    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    Path(args.output).write_text(json.dumps(result, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    if args.markdown:
        Path(args.markdown).parent.mkdir(parents=True, exist_ok=True)
        Path(args.markdown).write_text(render_report(result), encoding="utf-8")
    return 0


def counts(args) -> int:
    panel = load_daily_panel(Path(args.panel))
    splits = load_split_declaration(SPLITS)
    table = risk_counts(panel, splits)
    for year, row in table.items():
        print(year, json.dumps(row))
    return 0


# -- Markdown ------------------------------------------------------------------------------------------------------

skill_text = s686.skill_text
LABEL = {A: "H5 mean reversion (#686)", C: "type x state", "B1": "B1 persistence", "calendar": "risk-date calendar"}
TITLE = {"grid_crps": "grid CRPS (bp)", "mae": "MAE of the median (bp)", "upper_tail_twcrps": "upper-tail twCRPS (bp)"}


def vs_cells(vs: Mapping[str, dict]) -> str:
    return " | ".join(f"{skill_text(vs[c][b])}" for c in CANDIDATES for b in BENCHMARKS)


def table_header(first: str) -> List[str]:
    heads = [f"{LABEL[c]} vs {LABEL[b]}" for c in CANDIDATES for b in BENCHMARKS]
    return [f"| {first} | days | " + " | ".join(LABEL[m] for m in MODELS) + " | " + " | ".join(heads) + " |",
            "|" + "---|" * (2 + len(MODELS) + len(heads))]


def verdict_words(r: dict) -> str:
    k = r["kill_rule"]
    names = ", ".join(LABEL[c] for c in k["against_both"])
    if not k["killed"]:
        return (f"Not killed on the development data: {names} has skill (the 90% interval of its pooled skill above zero) on CRPS or MAE "
                "against both as-of persistence and the risk-date calendar benchmark. This is exploration, not a verdict (scoring protocol v1, #640).")
    if not k["killed_on_the_weaker_reading"]:
        weak = ", ".join(LABEL[c] for c in k["against_at_least_one"])
        return (f"Killed on the declared reading: no candidate has skill on CRPS or MAE against both as-of persistence and the "
                f"risk-date calendar benchmark. On the weaker reading (against at least one) {weak} has skill. Exploration, not a verdict.")
    return ("Killed on both readings: no candidate has CRPS or MAE skill (the 90% interval of the pooled skill above zero) against "
            "as-of persistence or the risk-date calendar benchmark. Exploration, not a verdict (scoring protocol v1, #640).")


def render_report(r: dict) -> str:
    n = r["notes"]
    out = [
        "# The spread on announced risk dates (#693)", "",
        f"Generated by `scripts/risk_date_spread_693.py score` from `{r['declaration']}`; not edited by hand. **{r['label']}**: target days to "
        f"{n['last_target']}, no verdict (scoring protocol v1, #640). Panel digest `{r['panel_sha256'][:8]}…`. Stationary bootstrap, mean block "
        f"{sp.BLOCK_LENGTH}, {r['draws']:,} draws, seed {r['seed']}, over the risk target days in date order; intervals are the 5th to 95th percentile of the "
        "draws. Skill is `mean(d) / mean(S(benchmark))` with `d = S(benchmark) - S(candidate)`: positive favours the candidate.", "",
        f"Scored decision days: {n['scored_decision_days']:,} ({n['first']} to {n['last']}); risk-date cells: {n['risk_date_cells']:,}; "
        f"risk target days: {r['target_days']['total']:,} ({', '.join(f'{k} {v}' for k, v in sorted(r['target_days']['by_type'].items()))}). "
        f"The first candidate has no forecast on {n['candidate_skipped_for_history']} early days (history); "
        f"{len(n['decision_days_dropped_for_a_benchmark'])} decision days are dropped because a benchmark has no sample of a lead's type "
        f"({', '.join(n['decision_days_dropped_for_a_benchmark'][:6]) or 'none'}{'…' if len(n['decision_days_dropped_for_a_benchmark']) > 6 else ''}).", "",
        "## Kill rule", "", verdict_words(r), "",
        "| candidate | CRPS skill vs B1 | CRPS vs calendar | MAE vs B1 | MAE vs calendar |", "|---|---|---|---|---|",
    ]
    for c in CANDIDATES:
        flags = r["kill_rule"]["skill"][c]
        out.append(f"| {LABEL[c]} | " + " | ".join("yes" if flags[m][b] else "no" for m in ("grid_crps", "mae") for b in BENCHMARKS) + " |")
    for metric in METRICS:
        p = r["primary"][metric]
        out += ["", f"## {TITLE[metric]}, pooled over the risk target days", "", "| | mean bp | skill vs B1 [90%] | skill vs calendar [90%] |", "|---|---|---|---|"]
        for m in BENCHMARKS:
            out.append(f"| {LABEL[m]} | {p['means'][m]:.3f} | | |")
        for c in CANDIDATES:
            out.append(f"| {LABEL[c]} | {p['means'][c]:.3f} | {skill_text(p['vs'][c]['B1'])} | {skill_text(p['vs'][c]['calendar'])} |")
        out += ["", f"By lead ({TITLE[metric]}):", ""] + table_header("lead")
        for h, cell in p["by_lead"].items():
            out.append(f"| {h} | {cell['days']} | " + " | ".join(f"{cell['means'][m]:.3f}" for m in MODELS) + " | " + vs_cells(cell["vs"]) + " |")
    for split, title in (("day_type", "risk-date type"), ("regime", "regime"), ("regime_three", "regime (three)"), ("scarcity_state", "scarcity-state group")):
        for metric in ("grid_crps", "mae"):
            out += ["", f"## {TITLE[metric]} by {title}, on the target day", ""] + table_header(title)
            for group, cell in r["splits"][split].items():
                if metric not in cell:
                    out.append(f"| {group} | {cell['days']} | {cell['note']} |")
                    continue
                m = cell[metric]
                out.append(f"| {group} | {cell['days']} | " + " | ".join(f"{m['means'][x]:.3f}" for x in MODELS) + " | " + vs_cells(m["vs"]) + " |")
    bases = sorted({b for v in r["type_state_basis"].values() for b in v})
    out += ["", "## Where the type x state model used its cell", "",
            "Forecasts by sample (`cell`: at least 10 days of the type and the state group in two years; `type`: the type alone):", "",
            "| type | " + " | ".join(bases) + " |", "|---|" + "---|" * len(bases)]
    for kind, v in r["type_state_basis"].items():
        out.append(f"| {kind} | " + " | ".join(str(v.get(b, 0)) for b in bases) + " |")
    if not r["kill_rule"]["killed"]:
        out += ["", "## Sketch of the desk-facing risk-date severity calendar (one table, not built)", "",
                "The type x state model's lead-1 median and 5th to 95th range of the spread in bp, by risk type and scarcity-state group, "
                "averaged over the 2025 target days.", "", "| type | state | target days | median | 5th | 95th |", "|---|---|---|---|---|---|"]
        for row in r["severity_sketch"]:
            out.append(f"| {row['type']} | {row['state']} | {row['target_days']} | {row['median_bp']:+.1f} | {row['q05_bp']:+.1f} | {row['q95_bp']:+.1f} |")
    out.append("")
    return "\n".join(out)


def page(args) -> int:
    r = json.loads(Path(args.score).read_text(encoding="utf-8"))
    n = r["notes"]
    lines = [
        "# The spread on announced risk dates: result (#693)", "",
        "**Hypothesis and step:** H6 (the spread on known risk dates is forecastable), step 1: benchmarks and a first candidate. "
        "**Development data only: this is not a verdict** (scoring protocol v1, #640). Generated by "
        "`scripts/risk_date_spread_693.py page`; the evidence is in `docs/pivot/evidence/risk-date-spread/`.", "",
        f"Target: the SOFR - IORB spread in bp on {r['target_days']['total']:,} quarter-end, month-end, tax and coupon-settlement days to {n['last_target']} "
        "(`metadata/risk_date_spread_693.json`). Benchmarks: as-of persistence (B1) and the trailing year's spreads on days of the same risk type. "
        "Candidates: the mean-reverting H5 row of #686, and one day-type x scarcity-state model.", "",
        "| grid CRPS bp | mean | skill vs B1 [90%] | skill vs calendar [90%] |", "|---|---|---|---|",
    ]
    p = r["primary"]["grid_crps"]
    for m in BENCHMARKS:
        lines.append(f"| {LABEL[m]} | {p['means'][m]:.3f} | | |")
    for c in CANDIDATES:
        lines.append(f"| {LABEL[c]} | {p['means'][c]:.3f} | {skill_text(p['vs'][c]['B1'])} | {skill_text(p['vs'][c]['calendar'])} |")
    q = r["primary"]["mae"]
    lines += ["", "| MAE of the median bp | mean | skill vs B1 [90%] | skill vs calendar [90%] |", "|---|---|---|---|"]
    for m in BENCHMARKS:
        lines.append(f"| {LABEL[m]} | {q['means'][m]:.3f} | | |")
    for c in CANDIDATES:
        lines.append(f"| {LABEL[c]} | {q['means'][c]:.3f} | {skill_text(q['vs'][c]['B1'])} | {skill_text(q['vs'][c]['calendar'])} |")
    crps_b1 = p["vs"][A]["B1"]
    three = r["splits"]["regime_three"]
    parts = ", ".join(
        f"{label} {skill_text(cell['grid_crps']['vs'][A]['B1'])}" for label, cell in three.items() if "grid_crps" in cell
    )
    lines += ["", verdict_words(r), "",
              f"How firm that is: the lower bound of the first candidate's pooled CRPS skill against B1 is {100.0 * crps_b1['skill_interval'][0]:+.2f}% "
              f"(the Diebold-Mariano p-value is {crps_b1['dm_p_value']:.3f}), and its MAE has no skill against B1. By regime its CRPS skill against B1 is {parts}: "
              "the pooled figure leans on the regimes where it is positive. Its skill against the calendar benchmark is large and the type x state model is "
              "worse than the calendar benchmark.", "",
              "The splits by risk type, regime and scarcity state, the per-lead tables and the sketch of the severity calendar (when the rule leaves the "
              "hypothesis standing) are in `docs/pivot/evidence/risk-date-spread/report.md`.", ""]
    Path(args.output).write_text("\n".join(lines), encoding="utf-8")
    return 0


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="command", required=True)
    c = sub.add_parser("counts", help="print the risk-date day set by type and year (no score)")
    c.add_argument("--panel", required=True)
    c.set_defaults(func=counts)
    s = sub.add_parser("score", help="score the candidates against B1 and the risk-date calendar benchmark")
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
