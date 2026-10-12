"""A second gate on the every-day part, by the tail spread's own trailing history (#601, step 2): declaration and scoring.

A scratch measurement, not a record: it writes JSON and Markdown to the paths it is given and nothing into `docs/runs/`.
Step 1 (`scripts/every_day_separation_601.py`, `docs/pivot/evidence/every-day-separation/`) found one input that separates the every-day
part's onset warnings from its false alarms: the tail spread's level, lower for the onset warnings. The two variants condition the part on it
with a cap: on a day the every-day part serves (not a risk date at the lead) the row's forecast is kept only if the tail spread, as read at the
lead's decision instant, is at or below a quantile of the readings of the previous `window` scored days, each read at its own earlier decision
instant. Every choice is in `metadata/every_day_conditioning_601.json` and the candidates in `metadata/pressure_judge/candidates/`, which
this script refuses to read unless they are committed and unchanged. Scored days are 2018-06-29 to 2025-12-31; no day of the 2026 tiers is read
(`docs/decisions/lockbox.md`; `require_unlocked`).

    # AUG2D.csv is the scratch panel of satiation_distance_598.py; OUT holds the forecasts of the row and of its parents (pooled_gate_595.py's docstring)
    PYTHONPATH=src python3 scripts/every_day_conditioning_601.py declare
    PYTHONPATH=src python3 scripts/every_day_conditioning_601.py cap --panel PUBLISHED.csv --scratch AUG2D.csv --output-dir OUT OUT/iorb_h?.json
    # the judge and the comparisons are pooled_gate_595.py's, with this declaration and these two variants:
    PYTHONPATH=src python3 scripts/every_day_conditioning_601.py pg diagnose --row ROW+tailcap75 --panel PUBLISHED.csv --scratch AUG2D.csv --output ... OUT/bench_h?.json OUT/both_h?.json OUT/iorb_h?.json OUT/cap_h?.json
    PYTHONPATH=src python3 scripts/every_day_conditioning_601.py pg compare|onsets|summary ...
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import math
import sys
from datetime import date, time
from pathlib import Path
from typing import List, Mapping, Optional, Sequence

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))

from repo_model import h41_release, measurement_fields  # noqa: E402
from repo_model.asof import InformationRule  # noqa: E402
from repo_model.baseline import _as_of_folds, panel_sha256  # noqa: E402
from repo_model.data import audit_panel, load_daily_panel  # noqa: E402
from repo_model.evaluation_splits import load_split_declaration  # noqa: E402
from repo_model.lockbox import require_unlocked  # noqa: E402
from repo_model.splits import LookAheadError  # noqa: E402


def _load(name: str):
    spec = importlib.util.spec_from_file_location(f"{name}_script", REPO / "scripts" / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[f"{name}_script"] = module
    spec.loader.exec_module(module)
    return module


pg = _load("pooled_gate_595")
sd = _load("satiation_distance_598")
ann = pg.ann
rds = pg.rds

DECLARATION = REPO / "metadata" / "every_day_conditioning_601.json"
STEP_ONE = REPO / "docs" / "pivot" / "evidence" / "every-day-separation" / "separation.json"
CANDIDATES = pg.CANDIDATES
ROW = pg.ROW
TAIL = "sofr_p99_iorb_bps"
GATE = pg.GATE
VARIANTS = {"cap75": ROW + "+tailcap75", "cap50": ROW + "+tailcap50"}
#: the quantiles are round numbers, declared and not read from a score; the window and the minimum are the gate's (#532)
CAPS = {
    "cap75": {"quantile": 0.75, "window": GATE["window"], "minimum_earlier": GATE["minimum_earlier"]},
    "cap50": {"quantile": 0.5, "window": GATE["window"], "minimum_earlier": GATE["minimum_earlier"]},
}


# -- the declaration ---------------------------------------------------------------------------------------


def trigger() -> dict:
    step_one = json.loads(STEP_ONE.read_text(encoding="utf-8"))
    return {
        "inputs": sorted(step_one["triggering_inputs"]),
        "direction": step_one["triggering_inputs"],
        "evidence": "docs/pivot/evidence/every-day-separation/separation.json (committed before this declaration)",
        "rule": "step 1's rule (metadata/every_day_separation_601.json, step_2_trigger): an input that separates in the pooled comparison and again, in the same direction, with the false alarms of the onset years only",
    }


def declaration_document() -> dict:
    parents = json.loads(rds.DECLARATION.read_text(encoding="utf-8"))
    return {
        "status": (
            "declared by the pull request that closes #601 after step 1 was committed and before any step 2 score; a measurement, not a record. Nothing here "
            "is published: no variant joins any published declaration, no 2026 day is scored, no rule changes and the live record and pin do not move. The "
            "variants condition on an input found by reading 2018-2025, so a pass is not a confirmation (ruling of 11 October 2026 on #567)"
        ),
        "issue": 601,
        "step": 2,
        "scoring": parents["scoring"],
        "thresholds_bp": parents["thresholds_bp"],
        "horizons": parents["horizons"],
        "parent": {"row": ROW, "declaration": "metadata/iorb_every_day_579.json (PR #582) and metadata/pooled_gate_595.json: the row as scored, unchanged"},
        "second_parent": "risk_gbm+settle+h41 (the row that passes tier 1 under the pooled count), the pairing reference",
        "trigger": trigger(),
        "variants": {
            key: {
                "name": VARIANTS[key],
                "cap": CAPS[key],
                "rule": (
                    "on a day that is not a risk date at the lead, the row's forecast is kept only if the tail spread (sofr_p99_iorb_bps) read at the lead's decision "
                    "instant is at or below the quantile (nearest rank) of the tail spread read on the days that were not risk dates among the previous window scored "
                    "days, each at its own decision instant; with fewer than minimum_earlier such readings, or when the tail spread is not public, the forecast is 0. "
                    "A risk date keeps the row's forecast. The curve across thresholds is made non-increasing afterwards, as the row's is"
                ),
                "reads": "the tail spread at the decision instants of earlier scored days and of this one (asof.InformationRule, per field), and nothing later",
                "fit": "none: a rule on the row's own gated forecasts at each lead",
            }
            for key in VARIANTS
        },
        "why_a_cap_and_not_a_fitted_term": (
            "step 1 found that the onset warnings sit at a lower tail spread than the false alarms. A term fitted for the probability of a pressure day cannot learn "
            "that: the likelihood rises with the tail spread. The input conditions the part as a gate, as the gate of #532 conditions it on its own forecast. Two "
            "strengths of one rule are declared (the upper quartile and the median of the trailing readings); no other quantile, input or form"
        ),
        "variants_declared": "these two, the row and its parent; no other variant, quantile, input or parent",
        "judge": "the judge as in force on main (metadata/pressure_judge.json, unchanged), under the weighted rule in force and the flat rule beside it",
        "pairing": "each variant against the row and against risk_gbm+settle+h41, with 90% stationary-bootstrap intervals, split by regime and pressure-day type",
        "published": "nothing; no variant joins any published declaration",
    }


def candidate_entries() -> dict:
    base = json.loads((CANDIDATES / f"{ROW}.json").read_text(encoding="utf-8"))
    entries = {}
    for key, name in VARIANTS.items():
        entry = dict(base)
        entry["track"] = "#601"
        entry["parent"] = ROW
        head = base["calibration"].split("; scored under ")[0]
        cap = CAPS[key]
        head += (
            f"; then on a day that is not a risk date the forecast is kept only if the tail spread (sofr_p99_iorb_bps) is at or below the {cap['quantile']} quantile "
            f"of its readings over the previous {cap['window']} scored days (at least {cap['minimum_earlier']}; else 0)"
        )
        tail = "; scored under settlements dated from the auction announcement (metadata/settlement_announcement_dating.json) and the H.4.1 weeklies read per release (metadata/h41_release_dating.json); metadata/every_day_conditioning_601.json"
        entry["calibration"] = head + tail
        entries[name] = entry
    return entries


def declare_command(args) -> int:
    DECLARATION.write_text(json.dumps(declaration_document(), indent=2) + "\n", encoding="utf-8")
    written = [str(DECLARATION)]
    for name, entry in candidate_entries().items():
        path = CANDIDATES / f"{name}.json"
        path.write_text(json.dumps(entry, indent=2) + "\n", encoding="utf-8")
        written.append(str(path))
    print(json.dumps({"written": written}, indent=1))
    return 0


# -- the cap -----------------------------------------------------------------------------------------------


def _read_only_earlier(k: int, window: Sequence[int]) -> None:
    """A day's cut-off is formed from the readings of earlier scored days: the day itself, and any later one, are not in its window."""

    late = [i for i in window if i >= k]
    if late:
        raise LookAheadError(f"the cap of scored day {k} would read the tail spread of scored day(s) {late}, which are not earlier decisions")


def tail_cap(levels: Sequence[Optional[float]], off: Sequence[bool], *, quantile: float, window: int, minimum_earlier: int) -> List[bool]:
    """Whether each scored day's forecast is kept: `levels[k]` is the tail spread read at day `k`'s decision instant (None if not public).

    A risk date (`off[k]` False) is kept. Any other day is kept only if its level is at or below the `quantile` (nearest rank) of the levels of the
    previous `window` scored days that were not risk dates, with at least `minimum_earlier` of them; else it is not kept.
    """

    keep: List[bool] = []
    for k in range(len(levels)):
        if not off[k]:
            keep.append(True)
            continue
        earlier = list(range(max(0, k - window), k))
        _read_only_earlier(k, earlier)
        readings = sorted(levels[i] for i in earlier if off[i] and levels[i] is not None)
        if levels[k] is None or len(readings) < minimum_earlier:
            keep.append(False)
            continue
        cut = readings[max(0, math.ceil(quantile * len(readings)) - 1)]
        keep.append(levels[k] <= cut)
    return keep


def apply_cap(forecasts: Mapping[str, Mapping[str, float]], days: Sequence[str], keep: Sequence[bool]) -> dict:
    """`forecasts[threshold][day]` with the forecast of a day that is not kept set to 0; the curve across thresholds is non-increasing."""

    out = {key: {day: (by_day[day] if keep[i] else 0.0) for i, day in enumerate(days)} for key, by_day in forecasts.items()}
    keys = sorted(out, key=float)
    for earlier, later in zip(keys, keys[1:]):
        out[later] = {day: min(v, out[earlier][day]) for day, v in out[later].items()}
    return out


def read_levels(rows, registry, last: date, horizon: int) -> dict:
    """The tail spread of every scored day, read at the decision instant of `horizon` (the as-of read of the row's own rule)."""

    timed_rows, timed_registry = ann.arm_inputs("both", rows, registry, horizon)
    dates = [row.date for row in timed_rows]
    levels = {}
    with sd.switched_on(), h41_release.release_dating():
        rule = InformationRule(timed_registry, ("spread_bps", TAIL), decision_time=time(16, 0), horizon=horizon)
        for fold in _as_of_folds(
            timed_rows, rule, minimum_history=61, refit_every=len(timed_rows), entry="every_day_conditioning_601", end=last
        ):
            value = fold.feature_row.values.get(TAIL)
            levels[dates[fold.index].isoformat()] = None if value is None else float(value)
    return levels


def cap_command(args) -> int:
    declared = rds.committed_declaration(DECLARATION)
    for name in VARIANTS.values():
        rds.committed_declaration(CANDIDATES / f"{name}.json")
    last = date.fromisoformat(declared["scoring"]["last_day"])
    require_unlocked([last], where="every_day_conditioning_601")
    scratch_rows = load_daily_panel(args.scratch)
    audit_panel(scratch_rows)
    by_date = {row.date: row for row in scratch_rows}
    registry = measurement_fields.load_registry()
    splits = load_split_declaration(rds.SPLITS)
    settle, _h41, _suffix = ann.ARMS["both"]
    documents = {}
    for path in args.inputs:
        document = json.loads(Path(path).read_text(encoding="utf-8"))
        documents[document["horizon"]] = document
    if sorted(documents) != list(pg.LEADS):
        raise SystemExit(f"the row's forecasts are needed at every lead {list(pg.LEADS)}, got {sorted(documents)}")
    if {d["panel_sha256"] for d in documents.values()} != {panel_sha256(args.published)}:
        raise SystemExit("a forecast file was scored on another panel")
    for h in pg.LEADS:
        source = documents[h]
        forecasts = source["forecasts"][ROW]
        days = sorted(forecasts[next(iter(forecasts))])
        levels_by_day = read_levels(scratch_rows, registry, last, h)
        missing = [day for day in days if day not in levels_by_day]
        if missing:
            raise SystemExit(f"lead {h}: {len(missing)} forecast days are not on the fold grid, the first {missing[0]}")
        levels = [levels_by_day[day] for day in days]
        off = [not ann.risk_flag(splits, by_date[date.fromisoformat(day)].values, settle or h == 1) for day in days]
        out = {}
        for key, name in VARIANTS.items():
            out[name] = apply_cap(forecasts, days, tail_cap(levels, off, **CAPS[key]))
        document = {
            "arm": "both",
            "horizon": h,
            "panel_sha256": source["panel_sha256"],
            "scratch_panel_sha256": source["scratch_panel_sha256"],
            "declaration": declared,
            "declarations": {name: {"rule": "tail_cap: the row's forecasts, a day that is not a risk date kept only if its tail spread is at or below the declared quantile of the trailing readings"} for name in VARIANTS.values()},
            "forecasts": out,
        }
        target = args.output_dir / f"cap_h{h}.json"
        target.write_text(json.dumps(document, indent=1, sort_keys=True, default=str) + "\n", encoding="utf-8")
        print(json.dumps({"horizon": h, "output": str(target), "days": len(days), "holes": sum(1 for x in levels if x is None)}))
    return 0


def passthrough_command(args) -> int:
    """`pooled_gate_595.py`'s diagnose, compare, onsets and summary, with this declaration and these variants."""

    pg.VARIANTS = dict(VARIANTS)
    pg.DECLARATION = DECLARATION
    return pg.main(args.rest)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("declare").set_defaults(func=declare_command)
    cap = sub.add_parser("cap")
    cap.add_argument("--panel", type=Path, dest="published", required=True, help="the published panel")
    cap.add_argument("--scratch", type=Path, required=True)
    cap.add_argument("--output-dir", type=Path, required=True)
    cap.add_argument("inputs", nargs="+", type=Path)
    cap.set_defaults(func=cap_command)
    through = sub.add_parser("pg")
    through.add_argument("rest", nargs=argparse.REMAINDER)
    through.set_defaults(func=passthrough_command)
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
