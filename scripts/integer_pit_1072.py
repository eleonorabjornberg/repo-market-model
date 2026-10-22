"""The randomised PIT for a whole-basis-point outcome, beside the PIT of #970 and the midpoint PIT of #707 (#1072, H5 step 3): a correction to a diagnostic.

A scratch measurement, not a record: it fits no model and writes JSON and Markdown to the paths it is given and nothing into `docs/runs/`. Finding #1069:
the outcome is a whole number of basis points, and #970's randomised PIT draws inside the bracket of grid levels around it, so it differs from the midpoint
PIT only when a quantile ties the outcome exactly. The proper PIT for an integer-valued outcome (Czado, Gneiting and Held, 2009) treats the law as a
forecast of the rounded value and draws uniformly in `(F(y - 1/2), F(y + 1/2))`, with `F` the law's distribution function read off its 23 quantiles
(`cdf`). This script reports the three versions side by side at lead 1, by regime, on the walks of `gbm_funding` (#634) and of the two variants of #1027.
Every choice is in `metadata/integer_pit_1072.json`, which `score` refuses to read unless it is committed and unchanged. No day after 2025-12-31 is read
(`docs/decisions/lockbox.md`). Development days give a diagnosis, never a verdict.

The walks are #634's `gbm_funding` at lead 1 and #1027's two variants at lead 1 (the directive's "#1027 candidate"; which of them replaces `gbm_funding` is
Eleonora's decision, so both are read). PUB.csv, AUG3.csv and the walks are built as in the docstrings of `scripts/spread_distribution_634.py`,
`scripts/drivers_audit_951.py` and `scripts/aligned_calendar_1027.py`:

    PYTHONPATH=src python3 scripts/spread_distribution_634.py walk --variant gbm_funding --horizon 1 --published PUB.csv --panel PUB.csv --output WALKS/gbm_funding_h1.json
    for v in gbm_funding_cal_aligned gbm_funding_cal_direct:
        OMP_NUM_THREADS=1 PYTHONPATH=src python3 scripts/aligned_calendar_1027.py walk --variant $v --horizon 1 --published PUB.csv --panel AUG3.csv --output WALKS/${v}_h1.json
    PYTHONPATH=src python3 scripts/integer_pit_1072.py score --published PUB.csv --panel AUG3.csv --walks WALKS --output docs/research/integer-pit-1072/result.json
    PYTHONPATH=src python3 scripts/integer_pit_1072.py report --score docs/research/integer-pit-1072/result.json --output docs/research/integer-pit-1072/report.md
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import random
import sys
from datetime import date
from pathlib import Path
from typing import Dict, List, Mapping, Optional, Sequence, Tuple

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))

from repo_model import scoring_protocol as sp  # noqa: E402
from repo_model.baseline import panel_sha256  # noqa: E402
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
_p970 = _load("randomised_pit_970")
Cell = _h5.Cell
pit = _h5.pit
pit_bin = _h5.pit_bin
committed_declaration = _h5.committed_declaration
randomised_pit_970 = _p970.randomised_pit
read_share = _p970.read_share

DECLARATION = REPO / "metadata" / "integer_pit_1072.json"
LAST_TARGET = _h5.LAST_TARGET
GRID = sp.GRID
PIT_EXPECTED = _h5.PIT_EXPECTED
SEED = 1072
EXTRA_SEEDS = tuple(range(1073, 1093))
LEAD = 1
WINDOW = "2021-23"
CANDIDATES = ("gbm_funding", "gbm_funding_cal_aligned", "gbm_funding_cal_direct")
VERSIONS = ("midpoint", "bracket_970", "integer")


def refuse_locked(days: Sequence[date]) -> None:
    """Refuse a run that would read a day of a locked tier (`docs/decisions/lockbox.md`): raises `LookAheadError`."""

    require_unlocked(list(days), where="integer_pit_1072")


# -- the pure parts ----------------------------------------------------------------------------------------------------


def cdf(law: Sequence[float], x: float) -> float:
    """The law's distribution function at `x`, right-continuous, read off its 23 quantiles.

    Linear between neighbouring quantiles; at a tie the largest level of the tied quantiles; the mass below the first quantile (its level) sits at that
    quantile and the mass above the last quantile sits at the last, so the function is 0 below the first quantile and 1 from the last on.
    """

    if x < law[0]:
        return 0.0
    if x >= law[-1]:
        return 1.0
    i = max(k for k, q in enumerate(law) if q <= x)
    if law[i] == x:
        return GRID[i]
    return GRID[i] + (GRID[i + 1] - GRID[i]) * (x - law[i]) / (law[i + 1] - law[i])


def integer_pit_bounds(law: Sequence[float], outcome: float) -> Tuple[float, float]:
    """`(F(y - 1/2), F(y + 1/2))`: the probability the law gives to the rounded bin of the whole-basis-point outcome `y`."""

    return cdf(law, outcome - 0.5), cdf(law, outcome + 0.5)


def integer_pit(law: Sequence[float], outcome: float, rng: random.Random) -> float:
    """Czado, Gneiting and Held (2009) for an integer-valued outcome: a draw uniform in `(F(y - 1/2), F(y + 1/2))`."""

    lo, hi = integer_pit_bounds(law, outcome)
    return lo + rng.random() * (hi - lo)


def h1_cells(laws: Mapping[date, Optional[Sequence[float]]], calendar: Sequence[date], outcomes: Mapping[date, float]) -> List[Cell]:
    """The lead-1 cells of a walk (`laws[target day]`): the decision day is the business day before the target. A missing law is not a cell."""

    position = {day: index for index, day in enumerate(calendar)}
    cells = []
    for target, law in sorted(laws.items()):
        if target not in position:
            raise ValueError(f"target day {target} is not on the scoring calendar")
        if law is None or position[target] - LEAD < 0:
            continue
        cells.append(Cell(calendar[position[target] - LEAD], target, list(law), list(law), outcomes.get(target)))
    return cells


def pit_shares(cells: Sequence[Cell], *, seed: int) -> Dict[str, object]:
    """The six-bin shares of the three versions of the scored cells, each drawn from its own `random.Random(seed)` in (decision, target) order."""

    scored = sorted((c for c in cells if c.outcome is not None), key=lambda c: (c.decision, c.target))
    rngs = {"bracket_970": random.Random(seed), "integer": random.Random(seed)}
    counts = {key: [0] * len(PIT_EXPECTED) for key in VERSIONS}
    low = {key: 0 for key in VERSIONS}
    for c in scored:
        values = {
            "midpoint": pit(c.law, c.outcome),
            "bracket_970": randomised_pit_970(c.law, c.outcome, rngs["bracket_970"]),
            "integer": integer_pit(c.law, c.outcome, rngs["integer"]),
        }
        for key, value in values.items():
            counts[key][pit_bin(value)] += 1
            low[key] += value <= 0.10
    n = len(scored)
    out: Dict[str, object] = {key: [k / n if n else None for k in counts[key]] for key in VERSIONS}
    out.update({"n": n, "share_at_or_below_0.10": {key: (low[key] / n if n else None) for key in VERSIONS}, "expected": list(PIT_EXPECTED), "seed": seed})
    return out


# -- the walks and the scoring -----------------------------------------------------------------------------------------


def load_h1(walks: Path, name: str, published: Path, panel: Path) -> Dict[date, Optional[List[float]]]:
    """A walk's lead-1 laws by target day, refused unless walked from the declared panels."""

    document = json.loads((walks / f"{name}_h{LEAD}.json").read_text(encoding="utf-8"))
    if document["horizon"] != LEAD or document["variant"] != name:
        raise ValueError(f"{name}_h{LEAD}.json is not the walk of {name} at lead {LEAD}")
    if document.get("panel_sha256") != panel_sha256(published):
        raise ValueError(f"{name}_h{LEAD}.json was walked from published panel {document.get('panel_sha256')}, not {panel_sha256(published)}")
    if name != "gbm_funding" and document.get("scratch_panel_sha256") != panel_sha256(panel):
        raise ValueError(f"{name}_h{LEAD}.json was walked from scratch panel {document.get('scratch_panel_sha256')}, not {panel_sha256(panel)}")
    if len(document["levels"]) != len(GRID):
        raise ValueError(f"{name}_h{LEAD}.json is not on the protocol's 23-level grid")
    return {date.fromisoformat(day): (None if q is None else [float(v) for v in q]) for day, q in document["laws"].items()}


def score_command(args) -> int:
    declared = committed_declaration(DECLARATION)
    refuse_locked([LAST_TARGET])
    if panel_sha256(args.published) != declared["input"]["published_panel_sha256"]:
        raise SystemExit("the published panel is not the declared one")
    rows = load_daily_panel(args.published)
    audit_panel(rows)
    calendar = [row.date for row in rows]
    outcomes = {row.date: row.spread_bps for row in rows}
    splits = load_split_declaration(_h5.SPLITS)
    walked = {name: load_h1(args.walks, name, args.published, args.panel) for name in CANDIDATES}
    # the same cells for every candidate: a target day every walk has a law for, up to the last study day
    common = set.intersection(*({t for t, law in laws.items() if law is not None} for laws in walked.values()))
    common = {t for t in common if t <= LAST_TARGET and t in outcomes}
    refuse_locked(sorted(common))
    document: dict = {
        "declaration": "metadata/integer_pit_1072.json",
        "panel_sha256": declared["input"]["published_panel_sha256"],
        "lead": LEAD,
        "seed": SEED,
        "window": WINDOW,
        "candidates": {},
    }
    for name in CANDIDATES:
        cells = [c for c in h1_cells({t: walked[name][t] for t in common}, calendar, outcomes)]
        by_regime: Dict[str, List[Cell]] = {}
        for c in cells:
            by_regime.setdefault(splits.regime(c.decision), []).append(c)
        window = by_regime.get(WINDOW, [])
        extra = [pit_shares(window, seed=s)["share_at_or_below_0.10"]["integer"] for s in EXTRA_SEEDS]
        main = pit_shares(window, seed=SEED)
        document["candidates"][name] = {
            "all_days": pit_shares(cells, seed=SEED),
            "by_regime": {label: pit_shares(group, seed=SEED) for label, group in sorted(by_regime.items())},
            "extra_seed_integer_shares_at_or_below_0.10": extra,
            "reading": read_share(main["share_at_or_below_0.10"]["integer"], extra) if window else "no cells in the window",
        }
    document["target_days"] = {"n": len(common), "first": min(common).isoformat(), "last": max(common).isoformat()}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(document, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return 0


def _shares(values: Sequence[Optional[float]]) -> str:
    return " ".join("n/a" if v is None else f"{v:.2f}" for v in values)


def report_command(args) -> int:
    doc = json.loads(args.score.read_text(encoding="utf-8"))
    out = [
        "| candidate | cut | cells | midpoint PIT ≤0.10 | PIT of #970 ≤0.10 | proper PIT ≤0.10 | midpoint bins | #970 bins | proper bins |",
        "|---|---|---|---|---|---|---|---|---|",
    ]
    for name, entry in doc["candidates"].items():
        for label, s in [("all days", entry["all_days"])] + list(entry["by_regime"].items()):
            low = s["share_at_or_below_0.10"]
            out.append(
                f"| {name} | {label} | {s['n']} | {low['midpoint']:.3f} | {low['bracket_970']:.3f} | {low['integer']:.3f} | "
                f"{_shares(s['midpoint'])} | {_shares(s['bracket_970'])} | {_shares(s['integer'])} |"
            )
    out += ["", f"Proper share ≤0.10 in {doc['window']} under 20 further seeds (1073 to 1092):", ""]
    for name, entry in doc["candidates"].items():
        x = entry["extra_seed_integer_shares_at_or_below_0.10"]
        out.append(f"- {name}: min {min(x):.3f}, max {max(x):.3f}; reading: **{entry['reading']}**")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text("\n".join(out) + "\n", encoding="utf-8")
    return 0


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="command", required=True)
    score = sub.add_parser("score", help="the three PITs from the lead-1 walks")
    score.add_argument("--published", type=Path, required=True)
    score.add_argument("--panel", type=Path, required=True)
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
