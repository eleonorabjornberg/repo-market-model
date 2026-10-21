"""Why the direct-pairs variant loses in 2021-23 (#1086, H5 step 3): a decomposition of #1036's walks and three checks on the training pairs.

A development diagnosis, never a claim and never a verdict (scoring protocol v1, #46). It refits nothing, writes JSON and Markdown to the paths it is given,
touches nothing in `docs/runs/`, and reads no day after 2025-12-31 and no day of a locked tier (`docs/decisions/lockbox.md`). Every choice is in
`metadata/direct_pairs_diagnosis_1086.json`, which `decompose` and `training` refuse to read unless it is committed and unchanged; `declare` writes it from the
constants below, and its output was committed before any number was computed.

**Criterion 1, `decompose`.** Reads the ten (and the control's five) walks of #1036 and splits the excess grid CRPS of a candidate over a reference on 2021-23
target days by lead, by target day type and by quantile level. `scoring_protocol.grid_crps` is twice the mean pinball loss over the 23 levels, so a level's
share of a cell is `2 * pinball / 23` and the shares sum to the cell's score. The levels are grouped into the declared bands (`BANDS`) to say whether the
excess sits in the centre or in the tails. Three pairs: `gbm_funding_cal_direct` over `gbm_funding` (the pair of #1036's headline; it differs in the
pairing, the leaf and the inputs), `gbm_funding_cal_aligned` against `gbm_funding_cal_direct` (the pair that differs in the pairing alone), and the aligned
variant over `gbm_funding`. The walks exist on Eleonora's Mac only (`~/rmm-1027/WALKS`); this command takes seconds and needs no model fit.

**Criterion 2, `training`.** For every refit of every lead whose first scored day is in 2021-23, builds the training set the direct variant trains on (the
direct pairs of `ml._direct_pairs`, through the lead's as-of rule) and the one-step set `gbm_funding` trains on (the pairs `(p, p + 1)`), and reports, one
declared check each:

* `effective_sample`: the number of pairs, and `n (1 - r) / (1 + r)` for the lag-1 autocorrelation r of the targets in date order (floored at r = 0).
* `target_variance`: the variance of the targets, of the h-step residual `target - spread at the anchor`, and of the targets of the floor-regime pairs.
* `leaf_size`: the pairs whose target day is in the 2021-23 window, against the leaf (5 for the variants, 20 for `gbm_funding`); a leaf of k needs k pairs
  to make a split, so the ratio says how many splits' worth of floor-regime pairs a tree has.

It fits nothing and needs no walk. Nothing here is a threshold or a rule: the page reads the figures in words.

    # PUB.csv, AUG3.csv: the panels of #1036's paste (digest 4ddc3882... for PUB.csv)
    PYTHONPATH=src python3 scripts/direct_pairs_diagnosis_1086.py declare        # then commit metadata/direct_pairs_diagnosis_1086.json
    PYTHONPATH=src python3 scripts/direct_pairs_diagnosis_1086.py training --published PUB.csv --panel AUG3.csv --output docs/research/direct-pairs-diagnosis-1086/training.json
    PYTHONPATH=src python3 scripts/direct_pairs_diagnosis_1086.py decompose --published PUB.csv --panel AUG3.csv --walks ~/rmm-1027/WALKS \\
        --output docs/research/direct-pairs-diagnosis-1086/decompose.json
    PYTHONPATH=src python3 scripts/direct_pairs_diagnosis_1086.py report --training .../training.json --decompose .../decompose.json \\
        --markdown docs/research/direct-pairs-diagnosis-1086-result.md
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import subprocess
import sys
from datetime import date
from pathlib import Path
from typing import Dict, List, NamedTuple, Optional, Sequence

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))


def _load(name: str):
    spec = importlib.util.spec_from_file_location(f"{name}_script", REPO / "scripts" / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[f"{name}_script"] = module
    spec.loader.exec_module(module)
    return module


from repo_model import metrics, scoring_protocol as sp  # noqa: E402
from repo_model.baseline import panel_sha256  # noqa: E402
from repo_model.splits import LookAheadError  # noqa: E402

DECLARATION = REPO / "metadata" / "direct_pairs_diagnosis_1086.json"
LAST_TARGET = date(2025, 12, 31)
#: the 2021-23 regime window of #1036's report (`evaluation_splits.json`'s regime "2021-23"), by target day
WINDOW = (date(2021, 1, 1), date(2023, 12, 31))
GRID = sp.GRID
HORIZONS = sp.HORIZONS
MINIMUM_HISTORY = 61
REFIT_EVERY = 21
CONTROL, ALIGNED, DIRECT = "gbm_funding", "gbm_funding_cal_aligned", "gbm_funding_cal_direct"
#: (candidate, reference): the excess is candidate minus reference, so a positive excess is a loss of the candidate
PAIRS = ((DIRECT, CONTROL), (ALIGNED, DIRECT), (ALIGNED, CONTROL))
LEAVES = {"variants": 5, "gbm_funding": 20}
#: the declared bands of the 23 levels; a band is a description of where the loss sits, not a threshold
BANDS = {
    "lower_tail": "level <= 0.10",
    "lower_shoulder": "0.10 < level < 0.25",
    "centre": "0.25 <= level <= 0.75",
    "upper_shoulder": "0.75 < level < 0.90",
    "upper_tail": "level >= 0.90",
}


def require_study_window(days: Sequence[date]) -> None:
    """Refuse a run that would read a day after 2025-12-31: raises `LookAheadError`."""

    late = [day for day in days if day > LAST_TARGET]
    if late:
        raise LookAheadError(f"direct_pairs_diagnosis_1086 reads no day after {LAST_TARGET}; asked for {min(late)}")


def in_window(day: date) -> bool:
    return WINDOW[0] <= day <= WINDOW[1]


# -- criterion 1: the decomposition ------------------------------------------------------------------------------------


def band_of(level: float) -> str:
    if level <= 0.10:
        return "lower_tail"
    if level < 0.25:
        return "lower_shoulder"
    if level <= 0.75:
        return "centre"
    if level < 0.90:
        return "upper_shoulder"
    return "upper_tail"


def level_losses(quantiles: Sequence[float], observed: float) -> List[float]:
    """The grid CRPS of one cell split into its 23 levels: twice the pinball loss of each level over the grid size, so the list sums to the score."""

    if len(quantiles) != len(GRID):
        raise ValueError(f"expected {len(GRID)} quantiles, got {len(quantiles)}")
    return [2.0 * metrics.pinball_loss(level, q, observed) / len(GRID) for level, q in zip(GRID, quantiles)]


class Cell(NamedTuple):
    lead: int
    kind: str
    reference: Sequence[float]
    candidate: Sequence[float]
    observed: float


def decompose(cells: Sequence[Cell]) -> Dict[str, dict]:
    """The mean excess (candidate minus reference) of the grid CRPS by level and by band, for all cells, each lead and each target day type."""

    if not cells:
        raise ValueError("nothing to decompose")
    groups: Dict[str, List[Cell]] = {"all": list(cells)}
    for cell in cells:
        groups.setdefault(f"lead {cell.lead}", []).append(cell)
        groups.setdefault(cell.kind, []).append(cell)
    out = {}
    for name, members in groups.items():
        by_level = [0.0] * len(GRID)
        for cell in members:
            mine, theirs = level_losses(cell.candidate, cell.observed), level_losses(cell.reference, cell.observed)
            for k in range(len(GRID)):
                by_level[k] += mine[k] - theirs[k]
        by_level = [v / len(members) for v in by_level]
        by_band = {band: 0.0 for band in BANDS}
        for level, v in zip(GRID, by_level):
            by_band[band_of(level)] += v
        out[name] = {"days": len(members), "total": sum(by_level), "by_level": by_level, "by_band": by_band}
    return out


# -- criterion 2: the training sets -------------------------------------------------------------------------------------


def lag1_autocorrelation(values: Sequence[float]) -> float:
    """The lag-1 autocorrelation about the mean; 0.0 for a constant series."""

    n = len(values)
    if n < 2:
        raise ValueError("an autocorrelation needs at least two values")
    mean = sum(values) / n
    denominator = sum((v - mean) ** 2 for v in values)
    if denominator == 0.0:
        return 0.0
    return sum((values[i] - mean) * (values[i + 1] - mean) for i in range(n - 1)) / denominator


def effective_sample(values: Sequence[float]) -> float:
    """n (1 - r) / (1 + r), with r the lag-1 autocorrelation floored at 0 (a negative r does not enlarge the sample)."""

    r = max(0.0, lag1_autocorrelation(values))
    return len(values) * (1.0 - r) / (1.0 + r)


def _variance(values: Sequence[float]) -> Optional[float]:
    if not values:
        return None
    mean = sum(values) / len(values)
    return sum((v - mean) ** 2 for v in values) / len(values)


def training_summary(targets: Sequence[float], anchor_spreads: Sequence[float], floor: Sequence[bool]) -> dict:
    """One training set's figures: pairs, effective sample, variances and floor-regime pairs against the two leaves. Inputs are in date order."""

    if not (len(targets) == len(anchor_spreads) == len(floor)):
        raise ValueError("targets, anchor spreads and floor flags must line up")
    if len(targets) < 2:
        raise ValueError("a training set needs at least two pairs")
    changes = [t - a for t, a in zip(targets, anchor_spreads)]
    floor_targets = [t for t, f in zip(targets, floor) if f]
    floor_pairs = len(floor_targets)
    return {
        "pairs": len(targets),
        "effective_sample": effective_sample(targets),
        "target_variance": _variance(targets),
        "change_variance": _variance(changes),
        "distinct_targets": len({round(t, 6) for t in targets}),
        "floor_pairs": floor_pairs,
        "floor_target_variance": _variance(floor_targets),
        "floor_pairs_per_leaf_5": floor_pairs / LEAVES["variants"],
        "floor_pairs_per_leaf_20": floor_pairs / LEAVES["gbm_funding"],
    }


def mean_of(blocks: Sequence[dict], key: str) -> Optional[float]:
    values = [b[key] for b in blocks if b.get(key) is not None]
    return sum(values) / len(values) if values else None


# -- the declaration ----------------------------------------------------------------------------------------------------


def committed_declaration(path: Path = DECLARATION) -> dict:
    """The declaration, refused unless it is committed and unchanged since `HEAD`."""

    relative = str(path.resolve().relative_to(REPO))
    dirty = subprocess.run(["git", "status", "--porcelain", "--", relative], cwd=REPO, capture_output=True, text=True, check=True).stdout.strip()
    if dirty:
        raise SystemExit(f"{relative} is not committed ({dirty}); a declaration is made before any score")
    return json.loads(path.read_text(encoding="utf-8"))


def declaration_document() -> dict:
    return {
        "status": "declared by the pull request that closes #1086 before any number was computed; a diagnosis of development data, not a record. No refit, no published figure moves, no day after 2025-12-31 and no locked day is read. Development data gives no verdict (scoring protocol v1, #46).",
        "issue": 1086,
        "hypothesis": "H5 step 3, the 2021-23 diagnosis",
        "ruling": "Eleonora, 21 October 2026, relayed by the orchestrating session: keep gbm_funding as the H5 candidate, adopt nothing, find out why the direct-pairs variant loses in 2021-23",
        "window": [WINDOW[0].isoformat(), WINDOW[1].isoformat()],
        "window_meaning": "the regime '2021-23' of #1036's report, by target day; 'floor-regime pairs' are the training pairs whose target day is in it (a description of the period of the ON RRP floor, not a rule)",
        "decomposition": {
            "walks": "#1036's: gbm_funding (#634's), gbm_funding_cal_direct and gbm_funding_cal_aligned, five leads each, read as they are; nothing is refitted",
            "pairs_candidate_over_reference": [list(p) for p in PAIRS],
            "pairs_note": "direct over gbm_funding differs in the pairing, the leaf (5 against 20) and the inputs (calendar and net-settlement columns added); aligned against direct differs in the pairing alone",
            "excess": "candidate minus reference of the grid CRPS; positive is a loss of the candidate",
            "cuts": ["all cells", "lead 1 to 5", "target day type (ordinary, settlement, month_end, tax_date, quarter_end)", "quantile level (23), grouped into bands"],
            "bands": BANDS,
            "contrast": "the same decomposition on target days outside 2021-23",
        },
        "checks": {
            "effective_sample": "pairs in the training set, and n (1 - r) / (1 + r) with r the lag-1 autocorrelation of the targets in date order, floored at 0",
            "target_variance": "variance of the targets, of target minus the spread at the pair's anchor, and of the floor-regime pairs' targets",
            "leaf_size": "floor-regime pairs divided by the leaf: 5 (the variants) and 20 (gbm_funding)",
            "sets": "direct pairs of ml._direct_pairs through the lead's as-of rule on the direct variant's inputs; one-step pairs (p, p + 1) on the same training frame",
            "refits": f"every refit (every {REFIT_EVERY} scored days, {MINIMUM_HISTORY} days of minimum history, as the walks) whose first scored day is in the window, at each lead 1 to 5",
            "reading": "no threshold: the page reads the figures in words and says which explanation they support; a cause that needs a refit is declared first and goes to the Mac",
        },
        "limits": ["no refit", "no day after 2025-12-31", "no lockbox day", "no published record is edited", "no published declaration is changed"],
    }


def declare_command(args) -> int:
    DECLARATION.write_text(json.dumps(declaration_document(), indent=1, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"written": str(DECLARATION.relative_to(REPO))}))
    return 0


# -- the commands -------------------------------------------------------------------------------------------------------


def training_command(args) -> int:
    from repo_model import measurement_fields, ml
    from repo_model.asof import InformationRule, fold_grid, refit_blocks
    from repo_model.data import audit_panel, load_daily_panel

    committed_declaration()
    sd, ac = _load("spread_distribution_634"), _load("aligned_calendar_1027")
    require_study_window([LAST_TARGET])
    audit_panel(load_daily_panel(args.published))
    rows = [row for row in load_daily_panel(args.panel) if row.date <= LAST_TARGET]
    audit_panel(rows)
    dates = [row.date for row in rows]
    registry = measurement_fields.load_registry()
    out: dict = {"issue": 1086, "label": "development, not a verdict", "declaration": str(DECLARATION.relative_to(REPO)), "panel_sha256": panel_sha256(args.published),
                 "scratch_panel_sha256": panel_sha256(args.panel), "window": [WINDOW[0].isoformat(), WINDOW[1].isoformat()], "leads": {}}
    with ac._load("net_settlement").switched_on():
        for h in HORIZONS:
            features = ac.variant_features(DIRECT, h)
            rule = InformationRule(registry, features, decision_time=sd.DECISION, horizon=h)
            grid = fold_grid(dates, registry, decision_time=sd.DECISION, minimum_history=MINIMUM_HISTORY, horizon=h)
            blocks = []
            for block in refit_blocks(grid, REFIT_EVERY):
                if not in_window(dates[block[0]]):
                    continue
                info = rule.information_set(dates, block[0])
                rule.check(dates, info)
                frame = rule.frame(rows, info)
                fdates = [row.date for row in frame]
                direct, _ = ml._direct_pairs(rule, frame, fdates, range(len(frame)), 0)
                one_step = [(p, frame[p], p + 1) for p in range(len(frame) - 1)]
                entry = {"first_scored_day": dates[block[0]].isoformat(), "frame_rows": len(frame)}
                for name, pairs in (("direct", direct), ("one_step", one_step)):
                    pairs = [(a, t) for a, _, t in pairs if frame[a].spread_bps is not None and frame[t].spread_bps is not None]
                    pairs.sort(key=lambda at: at[1])
                    entry[name] = training_summary(
                        [float(frame[t].spread_bps) for _, t in pairs], [float(frame[a].spread_bps) for a, _ in pairs], [in_window(fdates[t]) for _, t in pairs]
                    )
                    entry[name]["quarter_end_pairs"] = sum(1 for _, t in pairs if (frame[t].values.get("quarter_end") or 0.0) > 0.0)
                blocks.append(entry)
            keys = ("pairs", "effective_sample", "target_variance", "change_variance", "distinct_targets", "floor_pairs", "floor_target_variance",
                    "floor_pairs_per_leaf_5", "floor_pairs_per_leaf_20", "quarter_end_pairs")
            out["leads"][str(h)] = {
                "refits": len(blocks),
                "mean": {name: {k: mean_of([b[name] for b in blocks], k) for k in keys} for name in ("direct", "one_step")},
                "blocks": blocks,
            }
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    Path(args.output).write_text(json.dumps(out, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    return 0


def decompose_command(args) -> int:
    from repo_model.data import load_daily_panel
    from repo_model.evaluation_splits import load_split_declaration

    committed_declaration()
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
    out: dict = {"issue": 1086, "label": "development, not a verdict", "declaration": str(DECLARATION.relative_to(REPO)), "panel_sha256": panel_sha256(published),
                 "scratch_panel_sha256": panel_sha256(panel_path), "decision_days": len(days), "pairs": {}}
    for candidate, reference in PAIRS:
        by_window: Dict[str, List[Cell]] = {"2021-23": [], "outside 2021-23": []}
        for (d, h), t in targets.items():
            cell = Cell(h, ac.target_type(frame, t), frame.forecasts[reference][d][h], frame.forecasts[candidate][d][h], frame.outcome[t])
            by_window["2021-23" if in_window(t) else "outside 2021-23"].append(cell)
        out["pairs"][f"{candidate} over {reference}"] = {name: decompose(cells) for name, cells in by_window.items() if cells}
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    Path(args.output).write_text(json.dumps(out, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    return 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("declare").set_defaults(run=declare_command)
    for name, run in (("training", training_command), ("decompose", decompose_command)):
        p = sub.add_parser(name)
        p.add_argument("--published", type=Path, required=True)
        p.add_argument("--panel", type=Path, required=True)
        p.add_argument("--output", type=Path, required=True)
        if name == "decompose":
            p.add_argument("--walks", type=Path, required=True)
        p.set_defaults(run=run)
    args = parser.parse_args(argv)
    return args.run(args)


if __name__ == "__main__":
    raise SystemExit(main())
