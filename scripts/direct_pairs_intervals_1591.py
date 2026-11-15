"""The direct-pairs variant's excess over the control, by year and by pressure-day type, with intervals (#1591, H5 step 3): a re-read of #1036's walks.

A development re-read, never a claim and never a verdict (scoring protocol v1, #46). It refits nothing, reads the walks #1086's decomposition read
(`~/rmm-1027/WALKS` on Eleonora's Mac), reads no day after 2025-12-31 and no day of a locked tier, and edits nothing in `docs/runs/`. The pairs, the
declaration and the window are #1086's (`metadata/direct_pairs_diagnosis_1086.json`, committed and unchanged); nothing new is declared.

**What is computed.** For a pair (candidate, reference) and each target day, the grid CRPS of every forecast that targets the day, at leads 1 to 5, is averaged over
the leads: one score per target day for each model, the unit the bootstrap resamples. The excess of a group of target days is the mean of candidate minus
reference, so a positive excess is a loss of the candidate (as #1086's page). Its interval is the studentized stationary bootstrap of the scoring protocol
(`scoring_protocol.paired_test`: mean block 10, HAC lag 10), read two-sided at 95%, 10,000 draws, seed 1591. A group is a set of target days that need not be
consecutive, so the blocks run across the gaps of the group; for day types the interval is a description, not a tested difference. A group of no more
than the HAC lag in days carries its excess and no interval.

**Groups.** All target days; 2021-23 against outside it; each calendar year of the target 2018 to 2025; each pressure-day type in force; each year within
ordinary days and within the pressure days (every day that is not ordinary). The pressure-day type is `turn_days.reporting_day_type` as the record of #1135 (in force
since #1161) reads it: `turn`, `quarter_end_turn`, `year_end`, `tax_date`, `ordinary`; not the retired `month_end` and `quarter_end` flags #1086's page groups by.
`require_current_day_types` refuses a run under the retired reading. #1086's page also splits `settlement` out of ordinary; this run does not, so that its
`ordinary` is the record's.

Pieces, one file each (a lost piece costs only itself; `report` assembles the ones that exist):

    PYTHONPATH=src python3 scripts/direct_pairs_intervals_1591.py run --published PUB.csv --panel AUG3.csv --walks ~/rmm-1027/WALKS --pair 0 --output-dir docs/research/direct-pairs-intervals-1591
    PYTHONPATH=src python3 scripts/direct_pairs_intervals_1591.py report --output-dir docs/research/direct-pairs-intervals-1591
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from datetime import date
from pathlib import Path
from typing import Dict, Iterable, List, Mapping, Optional, Sequence, Tuple

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))


def _load(name: str):
    spec = importlib.util.spec_from_file_location(f"{name}_script", REPO / "scripts" / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[f"{name}_script"] = module
    spec.loader.exec_module(module)
    return module


from repo_model import scoring_protocol as sp, turn_days  # noqa: E402
from repo_model.baseline import panel_sha256  # noqa: E402
from repo_model.splits import LookAheadError  # noqa: E402

#: functions that compute a CRPS, classified for tests/test_lockbox.py
LOCKBOX_CRPS = {
    "cell_scores": (
        "delegates",
        "scores the cells of #1036's walks; `run_command` calls `require_study_window` on every decision day and target day before it builds a cell, and refuses any day after 2025-12-31 (#1591)",
    ),
}

LAST_TARGET = date(2025, 12, 31)
WINDOW = (date(2021, 1, 1), date(2023, 12, 31))
HORIZONS = sp.HORIZONS
SEED = 1591
DRAWS = sp.DRAWS
CONFIDENCE = 0.95
CONTROL, ALIGNED, DIRECT = "gbm_funding", "gbm_funding_cal_aligned", "gbm_funding_cal_direct"
#: (candidate, reference), #1086's order: the excess is candidate minus reference
PAIRS = ((DIRECT, CONTROL), (ALIGNED, DIRECT), (ALIGNED, CONTROL))


def require_study_window(days: Sequence[date]) -> None:
    """Refuse a run that would read a day after 2025-12-31: raises `LookAheadError`."""

    late = [day for day in days if day > LAST_TARGET]
    if late:
        raise LookAheadError(f"direct_pairs_intervals_1591 reads no day after {LAST_TARGET}; asked for {min(late)}")


def require_current_day_types() -> None:
    """Refuse a run under the retired month_end and quarter_end reading (`turn_days.legacy_reading`): raises `ValueError`."""

    if not turn_days.in_force():
        raise ValueError("the turn labels of #1135 are not in force; this re-read groups by them, not by the retired month_end and quarter_end flags")


def groups_of(day: date, label: str) -> List[str]:
    """The names of the groups a target day of day-type `label` belongs to."""

    year = f"year {day.year}"
    names = ["all", "2021-23" if WINDOW[0] <= day <= WINDOW[1] else "outside 2021-23", year, f"type {label}"]
    names.append(f"{year} / {'ordinary' if label == turn_days.ORDINARY else 'pressure'}")
    return names


def target_day_scores(cells: Iterable[Tuple[date, float, float]]) -> Dict[date, Tuple[float, float]]:
    """From (target day, reference score, candidate score) cells: each target day's mean over the leads that target it, as (reference, candidate)."""

    sums: Dict[date, List[float]] = {}
    for day, reference, candidate in cells:
        entry = sums.setdefault(day, [0.0, 0.0, 0.0])
        entry[0] += reference
        entry[1] += candidate
        entry[2] += 1.0
    return {day: (r / n, c / n) for day, (r, c, n) in sums.items()}


def _quantile(ordered: Sequence[float], probability: float) -> float:
    position = probability * (len(ordered) - 1)
    lower, upper = int(position // 1), -int(-position // 1)
    weight = position - lower
    return ordered[lower] * (1.0 - weight) + ordered[upper] * weight


def excess_interval(scores: Mapping[date, Tuple[float, float]], *, seed: int = SEED, draws: int = DRAWS) -> dict:
    """The mean excess (candidate minus reference) of a group of target days, with the studentized stationary bootstrap's two-sided interval.

    `scores` maps each target day to (reference, candidate). A group of no more than the HAC lag in days carries its excess and no interval.
    """

    days = sorted(scores)
    excess = sum(scores[d][1] - scores[d][0] for d in days) / len(days)
    out = {"days": len(days), "excess": excess, "lower": None, "upper": None}
    if len(days) <= sp.HAC_LAG:
        out["note"] = f"too few days for a lag-{sp.HAC_LAG} interval"
        return out
    test = sp.paired_test({d: scores[d][0] for d in days}, {d: scores[d][1] for d in days}, seed=seed, draws=draws, with_skill=False)
    tail = (1.0 - CONFIDENCE) / 2.0
    # d = reference - candidate, so excess = -mean(d); t* = (mean* - mean) / se*, hence the excess' bounds are -mean + q * se at the t-draws' tails
    out["lower"] = -test.mean_difference + _quantile(test.t_draws, tail) * test.standard_error
    out["upper"] = -test.mean_difference + _quantile(test.t_draws, 1.0 - tail) * test.standard_error
    out["standard_error"] = test.standard_error
    return out


def cell_scores(reference: Sequence[float], candidate: Sequence[float], observed: float) -> Tuple[float, float]:
    """(reference, candidate) grid CRPS of one cell."""

    return sp.grid_crps(reference, observed), sp.grid_crps(candidate, observed)


def run_command(args) -> int:
    from repo_model.data import load_daily_panel
    from repo_model.evaluation_splits import load_split_declaration

    require_current_day_types()
    m1086 = _load("direct_pairs_diagnosis_1086")
    m1086.committed_declaration()
    ac, b960 = _load("aligned_calendar_1027"), _load("b1_calendar_960")
    s761 = b960.s761
    published, panel_path, walks = Path(args.published), Path(args.panel), Path(args.walks)
    pub = load_daily_panel(published)
    registry = json.loads((REPO / "metadata" / "sources.json").read_text(encoding="utf-8"))
    frame, _notes = b960.build_frame(pub, panel_sha256(published), load_split_declaration(REPO / "metadata" / "evaluation_splits.json"), registry,
                                     s761.committed_declaration(b960.DECLARATION), walks)
    for name in (DIRECT, ALIGNED):
        frame.forecasts[name] = ac.load_walks(walks, name, published, panel_path, frame)
    frame.forecasts[CONTROL] = frame.forecasts.pop(b960.GBM)
    days = [d for d in frame.days if all(d in frame.forecasts[m] for m in (CONTROL, DIRECT, ALIGNED))]
    targets = {(d, h): frame.target(d, h) for d in days for h in HORIZONS}
    require_study_window(set(days) | set(targets.values()))
    candidate, reference = PAIRS[args.pair]
    labels = {t: turn_days.reporting_day_type(frame.splits, t, frame.values[t]) for t in set(targets.values())}
    cells = [(t, *cell_scores(frame.forecasts[reference][d][h], frame.forecasts[candidate][d][h], frame.outcome[t])) for (d, h), t in targets.items()]
    daily = target_day_scores(cells)
    members: Dict[str, Dict[date, Tuple[float, float]]] = {}
    for t, score in daily.items():
        for name in groups_of(t, labels[t]):
            members.setdefault(name, {})[t] = score
    out = {"issue": 1591, "label": "development, not a verdict", "pair": f"{candidate} over {reference}", "panel_sha256": panel_sha256(published),
           "scratch_panel_sha256": panel_sha256(panel_path), "seed": SEED, "draws": DRAWS, "confidence": CONFIDENCE, "block_length": sp.BLOCK_LENGTH, "hac_lag": sp.HAC_LAG,
           "day_types": "turn labels of #1135 (turn_days.reporting_day_type), in force", "groups": {name: excess_interval(m) for name, m in sorted(members.items())}}
    path = Path(args.output_dir) / f"pair{args.pair}.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(out, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    return 0


def _fmt(value: Optional[float]) -> str:
    return "" if value is None else f"{value:+.4f}"


def render(documents: Sequence[dict]) -> List[str]:
    lines: List[str] = []
    for doc in documents:
        lines += [f"### {doc['pair']}", "", "Positive excess = a loss of the candidate. Mean grid CRPS per target day (over leads 1 to 5), bp; 95% studentized stationary bootstrap interval.", "",
                  "| group | target days | excess | lower | upper |", "|---|---|---|---|---|"]
        for name, g in doc["groups"].items():
            lines.append(f"| {name} | {g['days']} | {_fmt(g['excess'])} | {_fmt(g['lower'])} | {_fmt(g['upper'])} |")
        lines.append("")
    return lines


def report_command(args) -> int:
    directory = Path(args.output_dir)
    documents = [json.loads(p.read_text(encoding="utf-8")) for p in sorted(directory.glob("pair[0-9].json"))]
    if not documents:
        raise SystemExit(f"no piece in {directory}")
    (directory / "tables.md").write_text("\n".join(render(documents)) + "\n", encoding="utf-8")
    (directory / "result.json").write_text(json.dumps({"issue": 1591, "label": "development, not a verdict", "pairs": {d["pair"]: d["groups"] for d in documents}},
                                                     indent=1, sort_keys=True) + "\n", encoding="utf-8")
    return 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = parser.add_subparsers(dest="command", required=True)
    run = sub.add_parser("run")
    run.add_argument("--published", type=Path, required=True)
    run.add_argument("--panel", type=Path, required=True)
    run.add_argument("--walks", type=Path, required=True)
    run.add_argument("--pair", type=int, choices=range(len(PAIRS)), required=True)
    run.add_argument("--output-dir", type=Path, required=True)
    run.set_defaults(run=run_command)
    report = sub.add_parser("report")
    report.add_argument("--output-dir", type=Path, required=True)
    report.set_defaults(run=report_command)
    args = parser.parse_args(argv)
    return args.run(args)


if __name__ == "__main__":
    raise SystemExit(main())
