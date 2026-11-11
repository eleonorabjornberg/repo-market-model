"""#1533's width-or-shape diagnostic by the target day's calendar flag, one tail at a time (#1547, avenue #1546, H5, step 3).

A development study, never a verdict. It reads the candidate's own forecasts and fits, changes and registers nothing. Every choice is in
`metadata/calendar_tail_diagnostic_1547.json`, which `score` refuses to read unless it is committed and unchanged. The forecasts are the walk
extension of `scripts/qe_diagnosis_1533.py` (regenerated bit-identical from the 1363 walk; no new walk). No day after 2026-09-03 and no locked
day is read.

    PYTHONPATH=src python3 -m repo_model.cli build --raw-root tests/fixtures/snapshots/funding_inputs --output PUB.csv \\
        --build-cutoff 2026-09-08T21:31:42+00:00 --decision-time 18:00:00
    for W in development 2026; do
      RMM_DECISION_TIME=18:00 PYTHONPATH=src python3 scripts/qe_diagnosis_1533.py walk --panel PUB.csv --window $W \\
          --output WALK/$W.json --extension EXT/$W.json
    done
    OUT=docs/research/calendar-tail-diagnostic-1547
    PYTHONPATH=src python3 scripts/calendar_tail_diagnostic_1547.py score --walks WALK --extensions EXT --output $OUT/result.json
    PYTHONPATH=src python3 scripts/calendar_tail_diagnostic_1547.py page --score $OUT/result.json \\
        --output docs/research/calendar-tail-diagnostic-1547-result.md

The walks take about three and a half minutes in all, the scoring a few minutes: below the `long-run` line. Stdlib only.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import random
import subprocess
import sys
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Mapping, Optional, Sequence

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))

DECLARATION = REPO / "metadata" / "calendar_tail_diagnostic_1547.json"
RECORD_1363 = REPO / "docs" / "research" / "candidate-calibration-1363" / "result.json"
RECORD_1533 = REPO / "docs" / "research" / "qe-diagnosis-1533" / "result.json"
SEED = 1547
REPS = 1000
MIN_CELLS_TAIL_1 = 500
MIN_CELLS_REGIME = 30
TOLERANCE = 1e-5


def _load(name: str, alias: str):
    spec = importlib.util.spec_from_file_location(alias, REPO / "scripts" / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[alias] = module
    spec.loader.exec_module(module)
    return module


q = _load("qe_diagnosis_1533", "qe_diagnosis_1533_in_1547")

FLAG_GROUPS = ("dom_19_23", "coupon_settlement", "post_month_end_window", "quarter_end_flag", "no_flag")
GROUPS = FLAG_GROUPS + ("quarter_end_group_1533",)
FLAG_OF = {"dom_19_23": "dom_19_23", "coupon_settlement": "coupon_settlement", "post_month_end_window": "post_month_end_window", "quarter_end_flag": "quarter_end"}
PAIRED = ("dcrps_B1p", "dcrps_B2", "dtw_B1p", "dtw_B2", "miss_q05_low", "miss_q95_up")
PAIRED_INDEX = {name: q.METRIC_NAMES.index(name) for name in PAIRED}
TAIL_KEYS = ("0.01", "0.05", "0.95", "0.99")


def committed_declaration(path: Path = DECLARATION) -> dict:
    """The declaration, refused unless it is committed and unchanged since `HEAD`."""

    return q.committed_declaration(path)


def groups_of(types: Sequence[str], pressure: str) -> List[str]:
    """The flag groups a target day belongs to (they overlap), from its calendar flags and its pressure-day type."""

    out = [name for name in ("dom_19_23", "coupon_settlement", "post_month_end_window") if FLAG_OF[name] in types]
    if "quarter_end" in types:
        out.append("quarter_end_flag")
    if list(types) == ["ordinary"] and pressure == "ordinary":
        out.append("no_flag")
    return out


# -- the reading rule (declared in metadata/calendar_tail_diagnostic_1547.json, reading_rule) ------------------------------------------


def tail_call(iv: Sequence[float]) -> str:
    """A tail's call from its ratio and 90% interval ([point, low, high]): too thin above 1, too wide below 1, in line when the interval holds 1."""

    if iv[1] > 1.0:
        return "too thin"
    if iv[2] < 1.0:
        return "too wide"
    return "in line"


def excludes_zero(iv: Sequence[float]) -> bool:
    return iv[1] > 0.0 or iv[2] < 0.0


def reading(s: Mapping[str, object]) -> dict:
    """The width, shape or location reading of one group from its intervals."""

    ratio = s["ratio"]
    c05, c95 = tail_call(ratio["0.05"]), tail_call(ratio["0.95"])
    sides_differ = excludes_zero(s["diff95"])
    level_differs = any(key in s and excludes_zero(s[key]) for key in ("diff01", "diff99"))
    off = [c for c in (c05, c95) if c != "in line"]
    labels: List[str] = []
    if sides_differ or level_differs:
        labels.append("shape")
    elif len(off) == 2 and c05 == c95:
        labels.append("width")
    elif len(off) == 1:
        labels.append("one tail off, not separable from width")
    elif len(off) == 2:
        labels.append("shape")
    if excludes_zero(s["median_z"]):
        labels.append("location")
    if not labels:
        labels.append("in line")
    calls = {tau: tail_call(ratio[tau]) for tau in s["reported"]}
    return {"labels": labels, "tails": calls}


def majority_agrees(values: Sequence[Optional[float]], reference: float, sign: int, minimum: int, counts: Sequence[int]) -> bool:
    """Whether most of the regimes with at least `minimum` cells have their value on the `sign` side of `reference` (sign -1 below, +1 above)."""

    voting = [v for v, n in zip(values, counts) if v is not None and n >= minimum]
    if not voting:
        return False
    return sum(1 for v in voting if (v - reference) * sign > 0) * 2 > len(voting)


def check_reproduction(mine: Mapping[str, object], theirs: Mapping[str, object], tolerance: float = TOLERANCE) -> None:
    """Refuse unless the quarter-end reference equals #1533's section 2b figures (the same forecasts and the same statistic)."""

    pairs = [("median_z", mine["median_z"], theirs["median_z"])]
    pairs += [(f"ratio {k}", mine["ratio"][k], theirs["ratio"][k]) for k in theirs["ratio"]]
    for name, a, b in pairs:
        if abs(a - b) > tolerance:
            raise ValueError(f"the quarter-end reference does not reproduce #1533's {name}: {a} against {b}")


# -- the figures ----------------------------------------------------------------------------------------------------------------------


def usable(cells: Sequence[dict]) -> List[dict]:
    return [c for c in cells if c["raw"][q.G[0.95]] > c["raw"][q.G[0.05]]]


def point(cells: Sequence[dict]) -> dict:
    out = q.shape_ratios(cells)
    out["paired"] = {name: sum(c["vec"][i] for c in cells) / len(cells) for name, i in PAIRED_INDEX.items()}
    return out


def draw_of(sample: Sequence[dict]) -> Dict[str, float]:
    s = q.shape_ratios(sample)
    d = {"median_z": s["median_z"]}
    d.update({tau: s["ratio"][tau] for tau in map(str, q.SHAPE_LEVELS)})
    d["diff95"] = s["ratio"]["0.95"] - s["ratio"]["0.05"]
    d["diff01"] = s["ratio"]["0.01"] - s["ratio"]["0.05"]
    d["diff99"] = s["ratio"]["0.99"] - s["ratio"]["0.95"]
    for name, i in PAIRED_INDEX.items():
        d[name] = sum(c["vec"][i] for c in sample) / len(sample)
    return d


def bootstrap(cells: Sequence[dict], *, reps: int, seed: int, clustered: bool) -> Dict[str, List[float]]:
    """Resampled figures: whole events when `clustered`, else the group's target days in date order by the stationary bootstrap (mean block 10)."""

    rng = random.Random(seed)
    key = "event" if clustered else "t"
    units = sorted({c[key] for c in cells}, key=str)
    by: Dict[object, List[dict]] = defaultdict(list)
    for c in cells:
        by[c[key]].append(c)
    draws: Dict[str, List[float]] = defaultdict(list)
    for _ in range(reps):
        if clustered:
            picked = [c for u in (units[rng.randrange(len(units))] for _ in units) for c in by[u]]
        else:
            picked = [c for i in q.stationary_indices(len(units), q.BLOCK, rng) for c in by[units[i]]]
        for name, value in draw_of(picked).items():
            draws[name].append(value)
    return dict(draws)


def with_interval(point_value: float, draws: Sequence[float]) -> List[float]:
    lo, hi = q.interval_of(draws)
    return [point_value, lo, hi]


def splits(cells: Sequence[dict], key: str) -> dict:
    out = {}
    for value in sorted({c[key] for c in cells}, key=str):
        sub = [c for c in cells if c[key] == value]
        if len(usable(sub)) < MIN_CELLS_REGIME:
            out[str(value)] = {"cells": len(sub), "note": "too few"}
        else:
            s = point(sub)
            out[str(value)] = {"cells": len(sub), "target_days": len({c["t"] for c in sub}), "median_z": s["median_z"], "ratio": s["ratio"], "paired": s["paired"]}
    return out


def group_result(cells: Sequence[dict], *, clustered: bool, reps: int = REPS, seed: int = SEED) -> dict:
    s = point(cells)
    draws = bootstrap(cells, reps=reps, seed=seed, clustered=clustered)
    reported = ["0.05", "0.95"] + (["0.01", "0.99"] if s["cells"] >= MIN_CELLS_TAIL_1 else [])
    out = {
        "cells": len(cells), "usable_cells": s["cells"], "target_days": len({c["t"] for c in cells}), "events": len({c["event"] for c in cells if c["event"]}),
        "reported": reported, "law": s["law"], "realised": s["realised"],
        "median_z": with_interval(s["median_z"], draws["median_z"]),
        "ratio": {tau: with_interval(s["ratio"][tau], draws[tau]) for tau in map(str, q.SHAPE_LEVELS)},
        "diff95": with_interval(s["ratio"]["0.95"] - s["ratio"]["0.05"], draws["diff95"]),
        "paired": {name: with_interval(s["paired"][name], draws[name]) for name in PAIRED},
        "expected_misses": {"0.05": 0.05 * len(cells), "0.95": 0.05 * len(cells)},
        "by_regime": splits(cells, "regime"), "by_lead": splits(cells, "h"), "by_pressure": splits(cells, "pressure"),
    }
    if "0.01" in reported:
        out["diff01"] = with_interval(s["ratio"]["0.01"] - s["ratio"]["0.05"], draws["diff01"])
        out["diff99"] = with_interval(s["ratio"]["0.99"] - s["ratio"]["0.95"], draws["diff99"])
    out["reading"] = reading(out)
    return out


def arm_for(result: Mapping[str, object], later: Optional[Mapping[str, object]]) -> dict:
    """The per-tail arm the development figures support for one group, by the declared arm rule (named, not sized)."""

    regimes = result["by_regime"]
    counts = [r["cells"] for r in regimes.values()]
    supported, reasons = [], []
    for tau in ("0.05", "0.95"):
        call = result["reading"]["tails"][tau]
        if call == "in line":
            reasons.append(f"q{tau[2:]} in line (interval holds 1)")
            continue
        sign = 1 if call == "too thin" else -1
        votes = [r.get("ratio", {}).get(tau) for r in regimes.values()]
        if majority_agrees(votes, 1.0, sign, MIN_CELLS_REGIME, counts):
            entry = {"arm": f"scale q{tau[2:]} by flag", "tail": tau, "call": call, "ratio": result["ratio"][tau][0]}
            if later is not None and later.get("ratio"):
                entry["2026_same_side"] = (later["ratio"][tau] - 1.0) * sign > 0
            supported.append(entry)
        else:
            reasons.append(f"q{tau[2:]} {call} but the regimes do not agree")
    if excludes_zero(result["median_z"]):
        sign = 1 if result["median_z"][1] > 0 else -1
        votes = [r.get("median_z") for r in regimes.values()]
        if majority_agrees(votes, 0.0, sign, MIN_CELLS_REGIME, counts):
            entry = {"arm": "shift by flag", "shift": result["median_z"][0]}
            if later is not None and later.get("median_z") is not None:
                entry["2026_same_side"] = later["median_z"] * sign > 0
            supported.append(entry)
        else:
            reasons.append("location off but the regimes do not agree")
    else:
        reasons.append("location interval holds 0")
    return {"supported": supported, "otherwise": reasons}


def groups_cells(window: "q.Window") -> Dict[str, List[dict]]:
    out: Dict[str, List[dict]] = {name: [] for name in GROUPS}
    for c in window.cells:
        meta = window.doc["targets"][c["t"]]
        for name in groups_of(meta["types"], meta["pressure"]):
            out[name].append(c)
        if c["event"] is not None:
            out["quarter_end_group_1533"].append(c)
    return out


def overlap(window: "q.Window", cells_by_group: Mapping[str, Sequence[dict]]) -> dict:
    out = {}
    for name in FLAG_GROUPS:
        days = {c["t"] for c in cells_by_group[name]}
        others = [n for n in ("dom_19_23", "coupon_settlement", "post_month_end_window", "quarter_end_flag") if n != name]
        shared = {d for d in days for n in others if d in {c["t"] for c in cells_by_group[n]}}
        out[name] = {"target_days": len(days), "share_with_another_flag": len(shared) / len(days) if days else None,
                     "share_of_cells_in_1533_group": sum(1 for c in cells_by_group[name] if c["event"]) / len(cells_by_group[name]) if cells_by_group[name] else None}
    return out


def score_command(args) -> int:
    declared = committed_declaration()
    record = json.loads(RECORD_1363.read_text(encoding="utf-8"))
    ref = json.loads(RECORD_1533.read_text(encoding="utf-8"))
    result: dict = {"issue": 1547, "declaration": "metadata/calendar_tail_diagnostic_1547.json", "label": "development, not a verdict", "seed": SEED,
                    "reps": REPS, "amendments": declared["amendments"], "walk_files": {}, "windows": {}}
    loaded = {}
    for name in q.WINDOWS:
        window = q.load_window(name, Path(args.walks), Path(args.extensions), record)
        if window is None:
            continue
        loaded[name] = window
        result["panel_sha256"] = window.doc["panel_sha256"]
        result["walk_files"][name] = {"sha256": window.ext["walk_sha256"], "refits": window.ext["walk_refits"]}
    dev = loaded["development"]
    mine = q.shape_interval(dev.group(), clustered=True, reps=1000)
    check_reproduction(mine, ref["windows"]["development"]["item2b"]["group"])
    result["reproduces_1533"] = {"group_cells": mine["cells"], "median_z": mine["median_z"], "ratio": mine["ratio"]}
    cells = groups_cells(dev)
    out = {name: group_result(cells[name], clustered=(name == "quarter_end_group_1533")) for name in GROUPS}
    later = {}
    if "2026" in loaded:
        for name, group in groups_cells(loaded["2026"]).items():
            if len(usable(group)) >= MIN_CELLS_REGIME:
                p = point(group)
                later[name] = {"cells": len(group), "median_z": p["median_z"], "ratio": p["ratio"], "paired": p["paired"]}
            else:
                later[name] = {"cells": len(group), "note": "too few"}
    for name in GROUPS:
        out[name]["arm"] = arm_for(out[name], later.get(name))
    result["windows"]["development"] = {"cells": len(dev.cells), "groups": out, "overlap": overlap(dev, cells)}
    result["windows"]["2026"] = later
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    Path(args.output).write_text(json.dumps(q.rounded(result), indent=1, sort_keys=True) + "\n", encoding="utf-8")
    return 0


# -- the page -------------------------------------------------------------------------------------------------------------------------

NAMES = {"dom_19_23": "dom_19_23", "coupon_settlement": "coupon_settlement", "post_month_end_window": "post_month_end_window",
         "quarter_end_flag": "quarter_end (flag, reference)", "quarter_end_group_1533": "quarter-end group of #1533 (reference)", "no_flag": "no calendar flag, no pressure type"}


def iv(x: Sequence[float], d: int = 2) -> str:
    return f"{x[0]:.{d}f} [{x[1]:.{d}f}, {x[2]:.{d}f}]"


def table(headers: Sequence[str], rows: Sequence[Sequence[str]]) -> List[str]:
    return ["| " + " | ".join(headers) + " |", "|" + "---|" * len(headers)] + ["| " + " | ".join(r) + " |" for r in rows]


def page(r: Mapping[str, object]) -> str:
    d = r["windows"]["development"]
    g = d["groups"]
    L: List[str] = []
    w = L.append
    w("# Width, shape or location by the target day's calendar flag, one tail at a time (#1547)")
    w("")
    w("**Development, not a verdict.** H5, step 3 (avenue #1546, first of two steps). No candidate change, no lockbox day, no re-score of a published record, nothing registered. "
      "Every figure is read from `docs/research/calendar-tail-diagnostic-1547/result.json`; the declaration is `metadata/calendar_tail_diagnostic_1547.json`, committed before any figure. "
      "The forecasts are #1533's walk extension, regenerated bit-identical from the 1363 walk; the quarter-end group of #1533 is recomputed here and equals its section 2b to 1e-5.")
    w("")
    w("## Reading")
    w("")
    rows = []
    for name in GROUPS:
        x = g[name]
        tails = ", ".join(f"q{t[2:]} {c}" for t, c in x["reading"]["tails"].items())
        rows.append([NAMES[name], str(x["cells"]), str(x["target_days"]), "; ".join(x["reading"]["labels"]), tails])
    L += table(["group", "cells", "target days", "reading", "tails, one at a time"], rows)
    w("")
    w("The reading rule is this study's operational version of the words in `metadata/qe_diagnosis_1533.json` (a ratio 'common' to both sides is width; ratios that differ by side or level are shape; the median shift is location). "
      "A tail is 'too thin' when the 90% interval of its ratio lies wholly above 1 and 'too wide' when wholly below 1. The pull request marks the rule as a question.")
    w("")
    w("## Ratios by tail")
    w("")
    w("The ratio is the realised distance from the realised median over the forecast law's, on z = (y - q50)/(q95 - q05) of the raw quantiles (#1533 section 2b). Intervals: stationary bootstrap of the group's target days (mean block 10), whole events for the #1533 group; 90%, seed 1547. 'too few': under 500 cells, so under five expected misses at the 1% level.")
    w("")
    rows = []
    for name in GROUPS:
        x = g[name]
        cells = [NAMES[name], iv(x["median_z"])]
        for tau in TAIL_KEYS:
            cells.append(iv(x["ratio"][tau]) if tau in x["reported"] else "too few")
        cells.append(iv(x["diff95"]))
        rows.append(cells)
    L += table(["group", "median z (shift)", "q01", "q05", "q95", "q99", "q95 - q05"], rows)
    w("")
    w("## Paired figures and misses")
    w("")
    w("Candidate minus benchmark on the same cells (negative favours the candidate); B1' and B2 of the 1363 walk. Misses are the strict share below q05 and above q95 against the nominal 0.05.")
    w("")
    rows = []
    for name in GROUPS:
        p = g[name]["paired"]
        rows.append([NAMES[name], iv(p["dcrps_B1p"], 3), iv(p["dcrps_B2"], 3), iv(p["dtw_B1p"], 3), iv(p["dtw_B2"], 3), iv(p["miss_q05_low"], 3), iv(p["miss_q95_up"], 3)])
    L += table(["group", "CRPS - B1'", "CRPS - B2", "twCRPS - B1'", "twCRPS - B2", "below q05", "above q95"], rows)
    w("")
    w("## The splits")
    w("")
    w("Point values; a split with fewer than 30 usable cells is 'too few'. Cells, median shift, ratio at q05 and at q95.")
    w("")
    for split, title in (("by_regime", "regime"), ("by_pressure", "pressure-day type of the target"), ("by_lead", "lead")):
        w(f"### By {title}")
        w("")
        rows = []
        for name in GROUPS:
            for key, v in g[name][split].items():
                rows.append([NAMES[name], key, str(v["cells"])] + (["too few"] * 3 if "note" in v else [f"{v['median_z']:.2f}", f"{v['ratio']['0.05']:.2f}", f"{v['ratio']['0.95']:.2f}"]))
        L += table(["group", title, "cells", "median z", "q05", "q95"], rows)
        w("")
    w("## The 2026 days (shown apart, decide nothing)")
    w("")
    rows = []
    for name in GROUPS:
        v = r["windows"]["2026"].get(name)
        if v is None:
            continue
        rows.append([NAMES[name], str(v["cells"])] + (["too few"] * 3 if "note" in v else [f"{v['median_z']:.2f}", f"{v['ratio']['0.05']:.2f}", f"{v['ratio']['0.95']:.2f}"]))
    L += table(["group", "cells", "median z", "q05", "q95"], rows)
    w("")
    w("## Overlap of the flag groups")
    w("")
    rows = [[NAMES[n], str(v["target_days"]), f"{v['share_with_another_flag']:.2f}", f"{v['share_of_cells_in_1533_group']:.2f}"] for n, v in d["overlap"].items()]
    L += table(["group", "target days", "share of days with another listed flag", "share of cells in the #1533 group"], rows)
    w("")
    w("## The per-tail arm the evidence supports")
    w("")
    w("By the declared arm rule: a scale of one tail where that tail is off, or a shift where the location interval excludes 0, and in either case the point value on the same side in a majority of the regimes with at least 30 cells. No size is chosen here.")
    w("")
    rows = []
    for name in GROUPS:
        a = g[name]["arm"]
        sup = "; ".join(f"{e['arm']} (point {e.get('ratio', e.get('shift')):.2f}; 2026 same side: {e.get('2026_same_side')})" for e in a["supported"]) or "none"
        rows.append([NAMES[name], sup, "; ".join(a["otherwise"])])
    L += table(["group", "supported", "otherwise"], rows)
    w("")
    w("## Limits and what was not checked")
    w("")
    w("- Development data on seen days, never a verdict; the 2026 days decide nothing.")
    w("- The flag groups overlap, so a day in two groups counts in both; the table above gives the share. The groups are not exclusive arms.")
    w("- The ratio is descriptive and is inflated by any location shift the median removes imperfectly. Intervals from a few dozen target days are wide.")
    w("- #1523's hit counts are lead 1 against a regime-expected rate fitted in sample; this study pools five leads at the candidate's own nominal levels, so the two do not compare one to one.")
    w("- No arm is fitted or scored; the size of any scale or shift is the second step's, after review.")
    w("")
    w("## Reproduction")
    w("")
    w("See the header of `scripts/calendar_tail_diagnostic_1547.py`; the test is `tests/test_calendar_tail_diagnostic_1547.py`. Seed 1547 throughout, 1533 for the reproduction check.")
    w("")
    return "\n".join(L)


def page_command(args) -> int:
    r = json.loads(Path(args.score).read_text(encoding="utf-8"))
    Path(args.output).write_text(page(r), encoding="utf-8")
    return 0


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="command", required=True)
    s = sub.add_parser("score", help="the diagnostic from the walk files and their extensions")
    s.add_argument("--walks", required=True)
    s.add_argument("--extensions", required=True)
    s.add_argument("--output", required=True)
    s.set_defaults(func=score_command)
    g = sub.add_parser("page", help="write the result page from a score file")
    g.add_argument("--score", required=True)
    g.add_argument("--output", required=True)
    g.set_defaults(func=page_command)
    args = parser.parse_args(argv)
    return int(args.func(args) or 0)


if __name__ == "__main__":
    raise SystemExit(main())
