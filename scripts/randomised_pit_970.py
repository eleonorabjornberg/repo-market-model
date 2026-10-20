"""The randomised PIT beside the midpoint PIT of #707 (#970, H5 step 3): a correction to a diagnostic.

A scratch measurement, not a record: it fits no model and writes JSON and Markdown to the paths it is given and nothing
into `docs/runs/`. It reads the walk-forward laws of #634 unchanged and builds the cells of `scripts/h5_step3_707.py`
exactly as that script does, then reports the 2021-23 share of PIT at or below 0.10 both ways. Every choice is in
`metadata/randomised_pit_970.json`, which this script refuses to read unless it is committed and unchanged. No day after
2025-12-31 is read (`docs/decisions/lockbox.md`). Development days give a diagnosis, never a verdict.

    # PUBLISHED.csv, AUG2D.csv and OUT/*_h*.json are built exactly as in the docstring of scripts/spread_distribution_634.py
    PYTHONPATH=src python3 scripts/randomised_pit_970.py score --published PUBLISHED.csv --walks OUT --output OUT/randomised_pit_970.json
    PYTHONPATH=src python3 scripts/randomised_pit_970.py report --score OUT/randomised_pit_970.json --output OUT/randomised_pit_970.md
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import random
import sys
from datetime import date
from pathlib import Path
from typing import Dict, List, Mapping, Optional, Sequence

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))

from repo_model import protocol_benchmarks as pb, scoring_protocol as sp  # noqa: E402
from repo_model.data import audit_panel, load_daily_panel  # noqa: E402
from repo_model.evaluation_splits import load_split_declaration  # noqa: E402
from repo_model.lockbox import require_unlocked  # noqa: E402


def _load(name: str):
    spec = importlib.util.spec_from_file_location(f"{name}_script", REPO / "scripts" / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[f"{name}_script"] = module
    spec.loader.exec_module(module)
    return module


_h5 = _load("h5_step3_707")
Cell = _h5.Cell
pit = _h5.pit
pit_bin = _h5.pit_bin
committed_declaration = _h5.committed_declaration

DECLARATION = REPO / "metadata" / "randomised_pit_970.json"
LAST_TARGET = _h5.LAST_TARGET
GRID = _h5.GRID
HORIZONS = _h5.HORIZONS
WALKS = _h5.WALKS
CANDIDATES = _h5.CANDIDATES
PIT_EXPECTED = _h5.PIT_EXPECTED
SEED = 970
EXTRA_SEEDS = tuple(range(971, 991))


def refuse_locked(days: Sequence[date]) -> None:
    """Refuse a run that would read a day of a locked tier (`docs/decisions/lockbox.md`): raises `LookAheadError`."""

    require_unlocked(list(days), where="randomised_pit_970")


def pit_bracket(law: Sequence[float], outcome: float):
    """The level bracket `(lo, hi)` the outcome falls in: `lo` the largest level whose quantile is below it (0 if none)
    and `hi` the smallest level whose quantile is above it (1 if none). A tie spans the levels around the tied ones."""

    below = [level for level, q in zip(GRID, law) if q < outcome]
    above = [level for level, q in zip(GRID, law) if q > outcome]
    return (below[-1] if below else 0.0, above[0] if above else 1.0)


def randomised_pit(law: Sequence[float], outcome: float, rng: random.Random) -> float:
    """Czado, Gneiting and Held (2009): a draw uniform in the cell's bracket."""

    lo, hi = pit_bracket(law, outcome)
    return lo + rng.random() * (hi - lo)


def pit_shares(cells: Sequence[Cell], *, seed: int) -> Dict[str, object]:
    """The six-bin shares of the midpoint and the randomised PIT of the scored cells, drawn in (decision, target) order."""

    scored = sorted((c for c in cells if c.outcome is not None), key=lambda c: (c.decision, c.target))
    rng = random.Random(seed)
    counts = {"midpoint": [0] * len(PIT_EXPECTED), "randomised": [0] * len(PIT_EXPECTED)}
    low = {"midpoint": 0, "randomised": 0}
    for c in scored:
        mid, ran = pit(c.law, c.outcome), randomised_pit(c.law, c.outcome, rng)
        counts["midpoint"][pit_bin(mid)] += 1
        counts["randomised"][pit_bin(ran)] += 1
        low["midpoint"] += mid <= 0.10
        low["randomised"] += ran <= 0.10
    n = len(scored)
    return {
        "n": n,
        "midpoint": [k / n if n else None for k in counts["midpoint"]],
        "randomised": [k / n if n else None for k in counts["randomised"]],
        "share_at_or_below_0.10": {key: (low[key] / n if n else None) for key in low},
        "expected": list(PIT_EXPECTED),
        "seed": seed,
    }


def read_share(randomised: float, extra: Sequence[float]) -> str:
    """The declared reading of the 2021-23 low-PIT share (see the declaration)."""

    if randomised > 0.15 and all(x > 0.10 for x in extra):
        return "stands"
    if randomised <= 0.15:
        return "does not stand"
    return "unresolved"


def score_command(args) -> int:
    declared = committed_declaration(DECLARATION)
    refuse_locked([LAST_TARGET])
    sd = _load("spread_distribution_634")
    if sd.panel_sha256(args.published) != declared["input"]["published_panel_sha256"]:
        raise SystemExit("the published panel is not the declared one")
    rows = load_daily_panel(args.published)
    audit_panel(rows)
    calendar = [row.date for row in rows]
    position = {day: index for index, day in enumerate(calendar)}
    outcomes = {row.date: row.spread_bps for row in rows}
    splits = load_split_declaration(_h5.SPLITS)
    registry = json.loads(_h5.SOURCES.read_text(encoding="utf-8"))
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
    window = {d for d in common if splits.regime(d) == "2021-23"}
    document: dict = {
        "declaration": "metadata/randomised_pit_970.json",
        "panel_sha256": declared["input"]["published_panel_sha256"],
        "decision_days": {"n": len(common), "first": common[0].isoformat(), "last": common[-1].isoformat()},
        "window_days": len(window),
        "seed": SEED,
        "candidates": {},
    }
    for name in CANDIDATES:
        fc = sp.fill_missing({day: decisions[name][day] for day in common}, b1, common).forecasts

        def cells_of(days: Sequence[date]) -> List[Cell]:
            return [
                Cell(d, calendar[position[d] + h], list(fc[d][h]), list(b1[d][h]), outcomes.get(calendar[position[d] + h]))
                for d in days for h in HORIZONS
            ]

        in_window, everything = cells_of([d for d in common if d in window]), cells_of(common)
        main = pit_shares(in_window, seed=SEED)
        extra = [pit_shares(in_window, seed=s)["share_at_or_below_0.10"]["randomised"] for s in EXTRA_SEEDS]
        document["candidates"][name] = {
            "window_2021_23": main,
            "all_days": pit_shares(everything, seed=SEED),
            "extra_seed_shares_at_or_below_0.10": extra,
            "reading": read_share(main["share_at_or_below_0.10"]["randomised"], extra),
        }
    args.output.write_text(json.dumps(document, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return 0


def _shares(values: Sequence[Optional[float]]) -> str:
    return " ".join("n/a" if v is None else f"{v:.2f}" for v in values)


def report_command(args) -> int:
    doc = json.loads(args.score.read_text(encoding="utf-8"))
    out = [
        "| candidate | cut | cells | midpoint PIT ≤0.10 | randomised PIT ≤0.10 | midpoint bins | randomised bins |",
        "|---|---|---|---|---|---|---|",
    ]
    for name, e in doc["candidates"].items():
        for label, key in (("2021-23", "window_2021_23"), ("all days", "all_days")):
            s = e[key]
            low = s["share_at_or_below_0.10"]
            out.append(
                f"| {name} | {label} | {s['n']} | {low['midpoint']:.3f} | {low['randomised']:.3f} | "
                f"{_shares(s['midpoint'])} | {_shares(s['randomised'])} |"
            )
    out += ["", "Randomised share ≤0.10 in 2021-23 under 20 further seeds (971 to 990):", ""]
    for name, e in doc["candidates"].items():
        x = e["extra_seed_shares_at_or_below_0.10"]
        out.append(f"- {name}: min {min(x):.3f}, max {max(x):.3f}; reading: **{e['reading']}**")
    args.output.write_text("\n".join(out) + "\n", encoding="utf-8")
    return 0


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="command", required=True)
    score = sub.add_parser("score", help="the PIT both ways from the #634 walks")
    score.add_argument("--published", type=Path, required=True)
    score.add_argument("--walks", type=Path, required=True)
    score.add_argument("--output", type=Path, required=True)
    score.set_defaults(func=score_command)
    report = sub.add_parser("report", help="write the Markdown tables from a score file")
    report.add_argument("--score", type=Path, required=True)
    report.add_argument("--output", type=Path, required=True)
    report.set_defaults(func=report_command)
    args = parser.parse_args(argv)
    return int(args.func(args) or 0)


if __name__ == "__main__":
    raise SystemExit(main())
