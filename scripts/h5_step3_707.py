"""H5 step 3 (#707): why the gbm loses to persistence in 2021-23, and what the upper tail does.

A scratch measurement, not a record: it fits no model and writes JSON and Markdown to the paths it is given and nothing
into `docs/runs/`. It reads the walk-forward laws of #634 unchanged (`scripts/spread_distribution_634.py walk`) and
scores them with the protocol's scorer. Every choice is in `metadata/h5_step3_707.json`, which this script refuses to read
unless it is committed and unchanged. No day after 2025-12-31 is read (`docs/decisions/lockbox.md`). Development days give a
diagnosis and an interval, never a verdict (scoring protocol v1, #640).

    # PUBLISHED.csv, AUG2D.csv and OUT/*_h*.json are built exactly as in the docstring of scripts/spread_distribution_634.py
    PYTHONPATH=src python3 scripts/h5_step3_707.py score --published PUBLISHED.csv --walks OUT --output OUT/h5_step3_707.json
    PYTHONPATH=src python3 scripts/h5_step3_707.py report --score OUT/h5_step3_707.json --output OUT/h5_step3_707.md
"""

from __future__ import annotations

import argparse
import bisect
import importlib.util
import json
import statistics
import subprocess
import sys
from datetime import date
from pathlib import Path
from typing import Dict, List, Mapping, NamedTuple, Optional, Sequence, Tuple

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))

from repo_model import protocol_benchmarks as pb, scoring_protocol as sp  # noqa: E402
from repo_model.data import audit_panel, load_daily_panel  # noqa: E402
from repo_model.evaluation_splits import load_split_declaration  # noqa: E402
from repo_model.lockbox import require_unlocked  # noqa: E402
from repo_model.scarcity import STATE_LABELS  # noqa: E402
from repo_model.splits import LookAheadError  # noqa: E402

DECLARATION = REPO / "metadata" / "h5_step3_707.json"
SPLITS = REPO / "metadata" / "evaluation_splits.json"
SOURCES = REPO / "metadata" / "sources.json"
LAST_TARGET = date(2025, 12, 31)
SEED = 707
GRID = sp.GRID
HORIZONS = sp.HORIZONS
MEDIAN = GRID.index(0.5)
WINDOW = 250
MINIMUM = 60
SCALE_FACTORS = (0.5, 0.7, 0.85, 1.0)
SHRINK_WEIGHTS = (0.0, 0.25, 0.5, 0.75, 1.0)
SPLIT_FACTORS = (0.25, 0.4, 0.55, 0.7, 0.85, 1.0, 1.2)
KINDS = ("level", "scale", "shrink")
CANDIDATES = ("gbm_funding", "c_two_part_new")
WALKS = ("published", "gbm_funding", "a_published_new", "b_gbm_new", "c_two_part_new")
PIT_EDGES = (0.10, 0.25, 0.50, 0.75, 0.90)
PIT_EXPECTED = (0.10, 0.15, 0.25, 0.25, 0.15, 0.10)
STATES = tuple(STATE_LABELS[k] for k in sorted(STATE_LABELS))


def _load(name: str):
    spec = importlib.util.spec_from_file_location(f"{name}_script", REPO / "scripts" / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[f"{name}_script"] = module
    spec.loader.exec_module(module)
    return module


# -- the guards ------------------------------------------------------------------------------------------------------


def refuse_locked(days: Sequence[date]) -> None:
    """Refuse a run that would read a day of a locked tier (`docs/decisions/lockbox.md`): raises `LookAheadError`."""

    require_unlocked(list(days), where="h5_step3_707")


def require_resolved(target: date, decision: date, *, where: str) -> None:
    """A remedy applied at `decision` may read only outcomes of target days strictly before it (`LookAheadError`)."""

    if target >= decision:
        raise LookAheadError(f"{where}: a cell with target {target} is not resolved before the decision of {decision}")


def committed_declaration(path: Path = DECLARATION) -> dict:
    """The declaration, refused unless it is committed and unchanged since `HEAD`."""

    relative = str(path.resolve().relative_to(REPO))
    dirty = subprocess.run(
        ["git", "status", "--porcelain", "--", relative], cwd=REPO, capture_output=True, text=True, check=True
    ).stdout.strip()
    if dirty:
        raise SystemExit(f"{relative} is not committed ({dirty}); a declaration is made before any score")
    return json.loads(path.read_text(encoding="utf-8"))


# -- the pure parts ------------------------------------------------------------------------------------------------


class Cell(NamedTuple):
    """One (decision day, lead) forecast: its target day, the law, B1's law at the same cell and the outcome."""

    decision: date
    target: date
    law: Sequence[float]
    benchmark: Sequence[float]
    outcome: Optional[float]


def pinball_mean(law: Sequence[float], outcome: float) -> float:
    """Mean pinball loss over the grid; twice this is the grid CRPS."""

    total = 0.0
    for level, q in zip(GRID, law):
        total += level * (outcome - q) if outcome >= q else (1.0 - level) * (q - outcome)
    return total / len(GRID)


def shifted(law: Sequence[float], amount: float) -> List[float]:
    return [q + amount for q in law]


def scale_about_median(law: Sequence[float], factor: float) -> List[float]:
    centre = law[MEDIAN]
    return [centre + factor * (q - centre) for q in law]


def shrink(law: Sequence[float], benchmark: Sequence[float], weight: float) -> List[float]:
    return [weight * q + (1.0 - weight) * b for q, b in zip(law, benchmark)]


def remedy_laws(cells: Sequence[Cell], kind: str) -> Dict[date, List[float]]:
    """The remedied law of each cell at one lead, `{decision day: law}`; causal.

    At a decision day the remedy reads the last `WINDOW` cells whose target day is strictly before it (and the identity
    when fewer than `MINIMUM` are resolved): `level` shifts by the trailing median of y - q50, `scale` takes the factor of
    `SCALE_FACTORS` and `shrink` the weight of `SHRINK_WEIGHTS` with the lowest trailing mean pinball loss.
    """

    if kind not in KINDS:
        raise ValueError(f"unknown remedy {kind!r}; declared: {KINDS}")
    history = sorted((c for c in cells if c.outcome is not None), key=lambda c: c.target)
    targets = [c.target for c in history]
    options: Sequence[float] = {"level": (), "scale": SCALE_FACTORS, "shrink": SHRINK_WEIGHTS}[kind]
    prefix: List[List[float]] = []
    for option in options:
        running, totals = 0.0, [0.0]
        for c in history:
            law = scale_about_median(c.law, option) if kind == "scale" else shrink(c.law, c.benchmark, option)
            running += pinball_mean(law, c.outcome)
            totals.append(running)
        prefix.append(totals)
    out: Dict[date, List[float]] = {}
    for c in cells:
        high = bisect.bisect_left(targets, c.decision)
        low = max(0, high - WINDOW)
        if high > low:
            require_resolved(history[high - 1].target, c.decision, where=f"remedy {kind}")
        if high - low < MINIMUM:
            out[c.decision] = [float(q) for q in c.law]
        elif kind == "level":
            out[c.decision] = shifted(c.law, statistics.median(h.outcome - h.law[MEDIAN] for h in history[low:high]))
        else:
            best = min(range(len(options)), key=lambda k: (prefix[k][high] - prefix[k][low], k))
            option = options[best]
            out[c.decision] = scale_about_median(c.law, option) if kind == "scale" else shrink(c.law, c.benchmark, option)
    return out


def pit(law: Sequence[float], outcome: float) -> float:
    """The outcome's probability-integral value read off the grid: the midpoint of the level bracket it falls in."""

    equal = [level for level, q in zip(GRID, law) if q == outcome]
    if equal:
        return (equal[0] + equal[-1]) / 2.0
    below = [level for level, q in zip(GRID, law) if q < outcome]
    above = [level for level, q in zip(GRID, law) if q > outcome]
    return ((below[-1] if below else 0.0) + (above[0] if above else 1.0)) / 2.0


def pit_bin(value: float) -> int:
    return bisect.bisect_right(PIT_EDGES, value)


def mean_crps(laws_and_outcomes: Sequence[Tuple[Sequence[float], float]]) -> float:
    return 2.0 * sum(pinball_mean(law, y) for law, y in laws_and_outcomes) / len(laws_and_outcomes)


def counterfactuals(cells: Sequence[Cell]) -> Tuple[float, float, List[List[float]], List[List[float]]]:
    """The window's own level shift and scale (hindsight): the shift S1 and the shift-and-scale S2 laws of each cell."""

    scored = [c for c in cells if c.outcome is not None]
    shift = statistics.median(c.outcome - c.law[MEDIAN] for c in scored)
    level = [shifted(c.law, shift) for c in scored]
    factor = min(
        SPLIT_FACTORS,
        key=lambda f: (mean_crps([(scale_about_median(law, f), c.outcome) for law, c in zip(level, scored)]), f),
    )
    return shift, factor, level, [scale_about_median(law, factor) for law in level]


def loss_split(cells: Sequence[Cell]) -> Dict[str, float]:
    """gap = S0 - B1 split into level, dispersion and remainder (see the declaration)."""

    scored = [c for c in cells if c.outcome is not None]
    shift, factor, level, both = counterfactuals(scored)
    s0 = mean_crps([(c.law, c.outcome) for c in scored])
    s1 = mean_crps([(law, c.outcome) for law, c in zip(level, scored)])
    s2 = mean_crps([(law, c.outcome) for law, c in zip(both, scored)])
    b1 = mean_crps([(c.benchmark, c.outcome) for c in scored])
    return {
        "n": len(scored), "shift": shift, "factor": factor, "s0": s0, "s1": s1, "s2": s2, "b1": b1,
        "gap": s0 - b1, "level": s0 - s1, "dispersion": s1 - s2, "remainder": s2 - b1,
    }


def name_component(split: Mapping[str, float]) -> str:
    """The reading rule: the largest of the three parts, named only above half the gap."""

    if split["gap"] <= 0:
        return "no loss"
    parts = {key: split[key] for key in ("level", "dispersion", "remainder")}
    best = max(parts, key=lambda key: parts[key])
    return best if parts[best] > 0.5 * split["gap"] else "no single component"


def read_tail(*, exceed95_lower: float, median_pit: float, beyond_q99: float) -> str:
    """The tail reading rule: U (too narrow) and L (law displaced)."""

    narrow = exceed95_lower > 0.05
    displaced = median_pit >= 0.9 and beyond_q99 > 0.5
    if narrow and displaced:
        return "both"
    if narrow:
        return "under-dispersed"
    if displaced:
        return "mislocated"
    return "neither resolved"


def read_closure(entry: Optional[dict]) -> str:
    """The remedy reading rule on its skill against B1 in the window."""

    if not entry:
        return "not tested"
    if entry["skill_lower_95_one_sided"] > 0:
        return "closed (beats B1)"
    if entry["skill"] >= 0:
        return "closed (level with B1, interval includes 0)"
    return "not closed"


# -- the measurement ---------------------------------------------------------------------------------------------


def _share(values: Sequence[bool]) -> Optional[float]:
    return sum(values) / len(values) if values else None


def window_stats(cells: Sequence[Cell], *, benchmark: bool = False) -> Dict[str, Optional[float]]:
    """The declared 2021-23 summaries of one forecast (or, with `benchmark`, of B1) over its cells."""

    scored = [c for c in cells if c.outcome is not None]
    laws = [(c.benchmark if benchmark else c.law, c.outcome) for c in scored]
    low, high = GRID.index(0.05), GRID.index(0.95)
    quarter, three = GRID.index(0.25), GRID.index(0.75)
    errors = [y - law[MEDIAN] for law, y in laws]
    outcomes = [y for _law, y in laws]
    return {
        "n": len(laws),
        "grid_crps": mean_crps(laws),
        "median_bias": sum(errors) / len(errors),
        "median_mae": sum(abs(e) for e in errors) / len(errors),
        "width90": sum(law[high] - law[low] for law, _y in laws) / len(laws),
        "coverage90": _share([law[low] <= y <= law[high] for law, y in laws]),
        "coverage50": _share([law[quarter] <= y <= law[three] for law, y in laws]),
        "outcome_variance": statistics.pvariance(outcomes),
    }


def pit_histogram(cells: Sequence[Cell]) -> Dict[str, object]:
    counts = [0] * len(PIT_EXPECTED)
    scored = [c for c in cells if c.outcome is not None]
    for c in scored:
        counts[pit_bin(pit(c.law, c.outcome))] += 1
    n = len(scored)
    return {"n": n, "shares": [k / n if n else None for k in counts], "expected": list(PIT_EXPECTED)}


def tail_stats(cells: Sequence[Cell]) -> Dict[str, object]:
    """The declared location measures on the cells whose outcome is above 0 bp."""

    above = [c for c in cells if c.outcome is not None and c.outcome > 0.0]
    q90, q95, q99 = GRID.index(0.9), GRID.index(0.95), GRID.index(0.99)
    pits = [pit(c.law, c.outcome) for c in above]
    spread = sum(c.law[q95] - c.law[MEDIAN] for c in above)
    return {
        "n_above": len(above),
        "coverage_q90": _share([c.outcome <= c.law[q90] for c in above]),
        "coverage_q95": _share([c.outcome <= c.law[q95] for c in above]),
        "median_pit": statistics.median(pits) if pits else None,
        "share_pit_above_half": _share([p > 0.5 for p in pits]),
        "share_beyond_q99": _share([c.outcome > c.law[q99] for c in above]),
        "miss_to_spread": (sum(c.outcome - c.law[MEDIAN] for c in above) / spread) if above and spread > 0 else None,
    }


def score_command(args) -> int:
    declared = committed_declaration()
    refuse_locked([LAST_TARGET])
    sd = _load("spread_distribution_634")
    pj = _load("pressure_judge")
    draws = args.draws
    if sd.panel_sha256(args.published) != declared["input"]["published_panel_sha256"]:
        raise SystemExit("the published panel is not the declared one")
    rows = load_daily_panel(args.published)
    audit_panel(rows)
    calendar = [row.date for row in rows]
    position = {day: index for index, day in enumerate(calendar)}
    outcomes = {row.date: row.spread_bps for row in rows}
    row_of = {row.date: row for row in rows}
    splits = load_split_declaration(SPLITS)
    registry = json.loads(SOURCES.read_text(encoding="utf-8"))
    walks = {name: sd.load_laws(args.walks, name, native=(name == "published")) for name in WALKS}
    decisions, days_by = {}, {}
    for name, laws in walks.items():
        decisions[name], days_by[name] = sd.lead_forecasts(laws, calendar)
    common = sorted(set.intersection(*(set(days) for days in days_by.values())))
    common = [day for day in common if all(calendar[position[day] + h] <= LAST_TARGET for h in HORIZONS)]
    refuse_locked(common + [calendar[position[day] + h] for day in common for h in HORIZONS])
    usable = []
    for day in common:
        try:
            pb.forecasts(pb.b1_forecast, rows, [day], registry=registry, decision_time=sd.DECISION)
            pb.forecasts(pb.b2_forecast, rows, [day], registry=registry, decision_time=sd.DECISION, splits=splits)
            usable.append(day)
        except sp.ProtocolError:
            pass
    common = usable
    b1 = pb.forecasts(pb.b1_forecast, rows, common, registry=registry, decision_time=sd.DECISION)
    b2 = pb.forecasts(pb.b2_forecast, rows, common, registry=registry, decision_time=sd.DECISION, splits=splits)
    forecasts: Dict[str, Dict[date, Dict[int, Sequence[float]]]] = {"B1": b1, "B2": b2}
    for name in CANDIDATES:
        forecasts[name] = sp.fill_missing({day: decisions[name][day] for day in common}, b1, common).forecasts
    states_by_target = pj._scarcity_states(1, LAST_TARGET)

    def state_of(day: date) -> str:
        value = states_by_target.get(calendar[position[day] + 1])
        return STATE_LABELS[int(value)] if value is not None else "unknown"

    def kind_of(day: date) -> str:
        return splits.reporting_day_type(day, row_of[day].values)

    def cells_of(fc: Mapping[date, Mapping[int, Sequence[float]]], lead: int) -> List[Cell]:
        return [
            Cell(d, calendar[position[d] + lead], list(fc[d][lead]), list(b1[d][lead]), outcomes.get(calendar[position[d] + lead]))
            for d in common
        ]

    def score_all(fc, score=sp.grid_crps) -> Dict[date, float]:
        return sp.day_scores(fc, outcomes, calendar, score=score)

    def table(scores, pairs, group):
        return sd.pair_table(scores, pairs, group, draws)

    primary = {name: score_all(forecasts[name]) for name in forecasts}
    days = sorted(primary["B1"])
    window = [d for d in days if splits.regime(d) == "2021-23"]
    state = {d: state_of(d) for d in days}
    document: dict = {
        "declaration": "metadata/h5_step3_707.json",
        "panel_sha256": declared["input"]["published_panel_sha256"],
        "decision_days": {"n": len(days), "first": days[0].isoformat(), "last": days[-1].isoformat()},
        "window_days": len(window),
        "draws": draws,
        "seed": SEED,
        "state_days": {s: sum(1 for d in days if state[d] == s) for s in (*STATES, "unknown")},
        "mean_primary": {name: sum(primary[name].values()) / len(days) for name in primary},
        "sub1": {},
        "sub2": {},
    }
    window_set = set(window)
    window_cells = {name: [c for h in HORIZONS for c in cells_of(forecasts[name], h) if c.decision in window_set] for name in CANDIDATES}
    all_cells = {name: [c for h in HORIZONS for c in cells_of(forecasts[name], h)] for name in CANDIDATES}
    for name in CANDIDATES:
        entry: dict = {}
        cells = window_cells[name]
        entry["stats"] = {"candidate": window_stats(cells), "B1": window_stats(cells, benchmark=True)}
        entry["against_benchmarks"] = table(primary, [("B1", name), ("B2", name)], window)
        entry["pit"] = {
            "pooled_window": pit_histogram(cells),
            "pooled_all": pit_histogram(all_cells[name]),
            "by_state_window": {s: pit_histogram([c for c in cells if state[c.decision] == s]) for s in STATES},
        }
        by_year = {}
        for year in (2021, 2022, 2023):
            group = [d for d in window if d.year == year]
            by_year[str(year)] = {"n": len(group), "tests": table(primary, [("B1", name)], group)}
        entry["by_year"] = by_year
        entry["by_state_window"] = {
            s: {"n": len([d for d in window if state[d] == s]), "tests": table(primary, [("B1", name)], [d for d in window if state[d] == s])}
            for s in STATES
        }
        split = loss_split(cells)
        shift, factor, level_laws, both_laws = counterfactuals(cells)
        scored_cells = [c for c in cells if c.outcome is not None]
        by_cell = {(c.decision, c.target): (a, b) for c, a, b in zip(scored_cells, level_laws, both_laws)}
        fc_s1: Dict[date, Dict[int, Sequence[float]]] = {d: {} for d in window}
        fc_s2: Dict[date, Dict[int, Sequence[float]]] = {d: {} for d in window}
        for d in window:
            for h in HORIZONS:
                a, b = by_cell[(d, calendar[position[d] + h])]
                fc_s1[d][h], fc_s2[d][h] = a, b
        split_scores = {
            "S0": {d: primary[name][d] for d in window},
            "S1": score_all(fc_s1),
            "S2": score_all(fc_s2),
            "B1": {d: primary["B1"][d] for d in window},
        }
        split["tests"] = table(split_scores, [("S0", "S1"), ("S1", "S2"), ("S2", "B1"), ("S0", "B1")], window)
        split["named"] = name_component(split)
        entry["loss_split"] = split
        remedies: dict = {}
        for kind in KINDS:
            fc_r: Dict[date, Dict[int, Sequence[float]]] = {d: {} for d in common}
            for h in HORIZONS:
                for decision, law in remedy_laws(cells_of(forecasts[name], h), kind).items():
                    fc_r[decision][h] = law
            label = f"{name}+{kind}"
            primary[label] = score_all(fc_r)
            remedies[kind] = {
                "mean_pooled": sum(primary[label].values()) / len(days),
                "window_vs_B1": table(primary, [("B1", label)], window),
                "window_vs_unremedied": table(primary, [(name, label)], window),
                "pooled_vs_B1": table(primary, [("B1", label)], days),
                "pooled_vs_unremedied": table(primary, [(name, label)], days),
                "pooled_vs_B2": table(primary, [("B2", label)], days),
            }
            remedies[kind]["reading"] = read_closure(remedies[kind]["window_vs_B1"].get(f"B1 -> {label}"))
        entry["remedies"] = remedies
        document["sub1"][name] = entry
    # the upper tail
    tw = {name: score_all(forecasts[name], sp.upper_tail_twcrps) for name in forecasts}
    cells_tw = {name: sd.cell_scores(forecasts[name], outcomes, calendar, sp.upper_tail_twcrps) for name in forecasts}
    for name in CANDIDATES:
        entry = {"pooled": table(tw, [("B1", name), ("B2", name)], days)}
        entry["by_state"] = {
            s: {"n": len([d for d in days if state[d] == s]), "tests": table(tw, [("B1", name), ("B2", name)], [d for d in days if state[d] == s])}
            for s in STATES
        }
        kinds = sorted({kind_of(calendar[position[d] + h]) for d in days for h in HORIZONS})
        by_type = {}
        for kind in kinds:
            include = lambda d, h, kind=kind: kind_of(calendar[position[d] + h]) == kind
            means = {n: sd.day_means(cells_tw[n], include) for n in ("B1", "B2", name)}
            group = sorted(set.intersection(*(set(m) for m in means.values())))
            by_type[kind] = {"decision_days": len(group), "tests": table(means, [("B1", name), ("B2", name)], group)}
        entry["by_day_type"] = by_type
        cells = all_cells[name]
        entry["tail"] = {"pooled": tail_stats(cells), "by_state": {s: tail_stats([c for c in cells if state[c.decision] == s]) for s in STATES}}
        # unconditional exceedance of q90 and q95: the daily share above the quantile against its nominal rate
        exceed = {}
        for label, level, nominal in (("q90", 0.9, 0.10), ("q95", 0.95, 0.05)):
            index = GRID.index(level)
            share = {
                d: sum(1 for h in HORIZONS if outcomes[calendar[position[d] + h]] > forecasts[name][d][h][index]) / len(HORIZONS)
                for d in days
            }
            nominal_series = {d: nominal for d in days}
            try:
                tested = table({"share": share, "nominal": nominal_series}, [("share", "nominal")], days)
                lower = nominal + tested["share -> nominal"]["mean_difference_lower_95_one_sided"]
            except (sp.ProtocolError, ZeroDivisionError, KeyError):
                lower = None
            exceed[label] = {"rate": sum(share.values()) / len(days), "nominal": nominal, "lower_95_one_sided": lower}
        entry["exceedance"] = exceed
        entry["reading"] = read_tail(
            exceed95_lower=exceed["q95"]["lower_95_one_sided"] if exceed["q95"]["lower_95_one_sided"] is not None else 0.0,
            median_pit=entry["tail"]["pooled"]["median_pit"],
            beyond_q99=entry["tail"]["pooled"]["share_beyond_q99"],
        )
        document["sub2"][name] = entry
    args.output.write_text(json.dumps(document, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    return 0


# -- the report ----------------------------------------------------------------------------------------------------


def f(value, digits: int = 3) -> str:
    return "n/a" if value is None else f"{value:.{digits}f}"


def skill_cell(entry: Optional[dict]) -> str:
    if not entry:
        return "n/a"
    return f"{entry['skill'] * 100:+.1f}% [{entry['skill_lower_95_one_sided'] * 100:+.1f}%, {entry['skill_upper_95_one_sided'] * 100:+.1f}%]"


def diff_cell(entry: Optional[dict]) -> str:
    if not entry:
        return "n/a"
    return f"{entry['mean_difference']:+.3f} (lower bound {entry['mean_difference_lower_95_one_sided']:+.3f})"


def report_command(args) -> int:
    d = json.loads(args.score.read_text(encoding="utf-8"))
    out: List[str] = [
        "# H5 step 3 (#707): the 2021-23 loss and the upper tail",
        "",
        f"Development days only; {d['decision_days']['n']} decision days {d['decision_days']['first']} to {d['decision_days']['last']}, "
        f"{d['window_days']} of them in 2021-23. Declaration: `{d['declaration']}`. Studentized stationary bootstrap, block 10, "
        f"{d['draws']} draws, seed {d['seed']}, one-sided 95%. Skill cells: skill [lower, upper] one-sided bounds. No verdict.",
        "",
        f"Decision days by as-of scarcity state: " + ", ".join(f"{k} {v}" for k, v in d["state_days"].items()),
        "",
        "## Sub-question 1: 2021-23",
    ]
    for name, e in d["sub1"].items():
        out += ["", f"### {name}", "", "| | grid CRPS | median bias | median MAE | width of 90% | coverage 90% | coverage 50% | var(y) |", "|---|---|---|---|---|---|---|---|"]
        for label, s in (("candidate", e["stats"]["candidate"]), ("B1", e["stats"]["B1"])):
            out.append(f"| {label} | {f(s['grid_crps'])} | {f(s['median_bias'])} | {f(s['median_mae'])} | {f(s['width90'])} | {f(s['coverage90'])} | {f(s['coverage50'])} | {f(s['outcome_variance'])} |")
        out += ["", f"Against B1 in 2021-23: {skill_cell(e['against_benchmarks'].get('B1 -> ' + name))}; against B2: {skill_cell(e['against_benchmarks'].get('B2 -> ' + name))}."]
        out += ["", "Skill against B1 by year of the decision day, and by as-of scarcity state:", "", "| cut | days | skill vs B1 |", "|---|---|---|"]
        for year, v in e["by_year"].items():
            out.append(f"| {year} | {v['n']} | {skill_cell(v['tests'].get('B1 -> ' + name))} |")
        for s, v in e["by_state_window"].items():
            out.append(f"| state {s} | {v['n']} | {skill_cell(v['tests'].get('B1 -> ' + name))} |")
        out += ["", "PIT shares (bins ≤0.10, 0.10-0.25, 0.25-0.50, 0.50-0.75, 0.75-0.90, >0.90; expected 0.10 0.15 0.25 0.25 0.15 0.10):", "", "| cut | cells | shares |", "|---|---|---|"]
        for label, h in (("2021-23", e["pit"]["pooled_window"]), ("all days", e["pit"]["pooled_all"]), *((f"2021-23, {s}", v) for s, v in e["pit"]["by_state_window"].items())):
            out.append(f"| {label} | {h['n']} | {' '.join(f(x, 2) for x in h['shares'])} |")
        sp_ = e["loss_split"]
        t = sp_["tests"]
        out += [
            "", f"Loss split on the window (hindsight counterfactuals; shift {f(sp_['shift'])} bp, scale factor {sp_['factor']}):", "",
            "| part | mean CRPS difference (bp) |", "|---|---|",
            f"| gap, S0 - B1 | {diff_cell(t.get('S0 -> B1'))} |",
            f"| level, S0 - S1 | {diff_cell(t.get('S0 -> S1'))} |",
            f"| dispersion, S1 - S2 | {diff_cell(t.get('S1 -> S2'))} |",
            f"| remainder, S2 - B1 | {diff_cell(t.get('S2 -> B1'))} |",
            "", f"S0 {f(sp_['s0'])}, S1 {f(sp_['s1'])}, S2 {f(sp_['s2'])}, B1 {f(sp_['b1'])}. Component named by the reading rule: **{sp_['named']}**.",
            "", "Remedies (post-hoc, causal, declared):", "", "| remedy | window vs B1 | window vs unremedied | pooled vs B1 | pooled vs unremedied | reading |", "|---|---|---|---|---|---|",
        ]
        for kind, r in e["remedies"].items():
            label = f"{name}+{kind}"
            out.append(
                f"| {kind} | {skill_cell(r['window_vs_B1'].get('B1 -> ' + label))} | {skill_cell(r['window_vs_unremedied'].get(name + ' -> ' + label))} | "
                f"{skill_cell(r['pooled_vs_B1'].get('B1 -> ' + label))} | {skill_cell(r['pooled_vs_unremedied'].get(name + ' -> ' + label))} | {r['reading']} |"
            )
    out += ["", "## Sub-question 2: the upper tail (twCRPS above 0 bp)"]
    for name, e in d["sub2"].items():
        out += ["", f"### {name}", "", "| cut | days | vs B1 | vs B2 |", "|---|---|---|---|"]
        out.append(f"| pooled | {d['decision_days']['n']} | {skill_cell(e['pooled'].get('B1 -> ' + name))} | {skill_cell(e['pooled'].get('B2 -> ' + name))} |")
        for s, v in e["by_state"].items():
            out.append(f"| state {s} | {v['n']} | {skill_cell(v['tests'].get('B1 -> ' + name))} | {skill_cell(v['tests'].get('B2 -> ' + name))} |")
        for k, v in e["by_day_type"].items():
            out.append(f"| day type {k} | {v['decision_days']} | {skill_cell(v['tests'].get('B1 -> ' + name))} | {skill_cell(v['tests'].get('B2 -> ' + name))} |")
        out += ["", "| cut | cells above 0 bp | coverage q90 | coverage q95 | median PIT | share PIT > 0.5 | share beyond q99 | (y - q50)/(q95 - q50) |", "|---|---|---|---|---|---|---|---|"]
        for label, s in (("pooled", e["tail"]["pooled"]), *((f"state {k}", v) for k, v in e["tail"]["by_state"].items())):
            out.append(f"| {label} | {s['n_above']} | {f(s['coverage_q90'])} | {f(s['coverage_q95'])} | {f(s['median_pit'])} | {f(s['share_pit_above_half'])} | {f(s['share_beyond_q99'])} | {f(s['miss_to_spread'])} |")
        x = e["exceedance"]
        out += [
            "", f"Unconditional exceedance: q90 {f(x['q90']['rate'])} (nominal 0.10, lower bound {f(x['q90']['lower_95_one_sided'])}); q95 {f(x['q95']['rate'])} (nominal 0.05, lower bound {f(x['q95']['lower_95_one_sided'])}).",
            "", f"Reading rule: **{e['reading']}**.",
        ]
    args.output.write_text("\n".join(out) + "\n", encoding="utf-8")
    return 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="command", required=True)
    score = sub.add_parser("score", help="score the diagnoses and remedies from the #634 walks")
    score.add_argument("--published", type=Path, required=True)
    score.add_argument("--walks", type=Path, required=True)
    score.add_argument("--output", type=Path, required=True)
    score.add_argument("--draws", type=int, default=10000)
    score.set_defaults(func=score_command)
    report = sub.add_parser("report", help="write the Markdown report from a score file")
    report.add_argument("--score", type=Path, required=True)
    report.add_argument("--output", type=Path, required=True)
    report.set_defaults(func=report_command)
    args = parser.parse_args(argv)
    return int(args.func(args) or 0)


if __name__ == "__main__":
    raise SystemExit(main())
