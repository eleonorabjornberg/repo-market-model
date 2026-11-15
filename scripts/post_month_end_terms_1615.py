"""Day-specific location and scale terms for the post-month-end business days 1 to 3 on (s3c-ann-net), fitted walk-forward (#1615, H5, development arm).

A development arm, never a verdict. It reads the candidate's own forecasts and cells (the walk extension of `scripts/qe_diagnosis_1533.py`, regenerated
bit-identical from the 1363 walk; no new walk, no refit) and changes nothing of the candidate. Every choice is in
`metadata/post_month_end_terms_1615.json`, which `score` refuses to read unless it is committed and unchanged. No day after 2026-09-03 and no locked
day is read.

A target day on business day 1, 2 or 3 of its month (`derived_features.bday_of_month`, the count the candidate's `post_month_end_window` term reads) is
in one of six groups: the business day crossed with the kind of the month-end before it (quarter-end when the target falls in January, April, July or
October). Each group has a location shift (bp, the shrunk median of y - q50 over the group's earlier cells) and a lower and an upper scale factor
(#1533's section 2b ratios on those cells, shrunk), the same at every lead. Three arms are scored: `arm` (shift and factors), `location` (shift only) and
`scale` (factors only). Every other target day is the candidate's, the same numbers. No term reads the month-end spread (unpublished before the second
business day, the reason S18 failed to act on business days 1 and 3).

    PYTHONPATH=src python3 -m repo_model.cli build --raw-root tests/fixtures/snapshots/funding_inputs --output PUB.csv \\
        --build-cutoff 2026-09-08T21:31:42+00:00 --decision-time 18:00:00
    for W in development 2026; do
      RMM_DECISION_TIME=18:00 PYTHONPATH=src python3 scripts/qe_diagnosis_1533.py walk --panel PUB.csv --window $W \\
          --output WALK/$W.json --extension EXT/$W.json
    done
    OUT=docs/research/post-month-end-terms-1615
    PYTHONPATH=src python3 scripts/post_month_end_terms_1615.py score --walks WALK --extensions EXT --output $OUT/result.json
    PYTHONPATH=src python3 scripts/post_month_end_terms_1615.py page --score $OUT/result.json \\
        --output docs/research/post-month-end-terms-1615-result.md

The walks take about four minutes and the scoring a few: below the `long-run` line. Stdlib only.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import math
import sys
from collections import defaultdict
from datetime import date
from pathlib import Path
from typing import Callable, Dict, List, Mapping, Optional, Sequence, Tuple

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))

from repo_model import scoring_protocol as sp  # noqa: E402
from repo_model.splits import LookAheadError  # noqa: E402

DECLARATION = REPO / "metadata" / "post_month_end_terms_1615.json"
RECORD_1363 = REPO / "docs" / "research" / "candidate-calibration-1363" / "result.json"
RECORD_1547 = REPO / "docs" / "research" / "calendar-tail-diagnostic-1547" / "result.json"
SEED = 1615
REPS = 1000
DRAWS = 10_000
K = 100
MIN_TRAIN = 50
MIN_CELLS = 30
ARMS = ("arm", "location", "scale")
REFERENCES = ("B1", "B1_prime", "B2")
REFERENCE_NAMES = {"candidate": "candidate", "B1": "B1", "B1_prime": "B1'", "B2": "B2"}


# Lockbox classification (#1058): tests/test_lockbox.py reads these literals from this file's syntax tree.
LOCKBOX_CRPS = {
    "cell_scores": (
        "delegates",
        "the metrics of one cell of a window `qe_diagnosis_1533.load_window` loads, whose `Window.__init__` calls "
        "`refuse_beyond` on every decision and target day; `build_cells` reads no other day (#1615, #1568)",
    ),
}


def _load(name: str, alias: str):
    spec = importlib.util.spec_from_file_location(alias, REPO / "scripts" / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[alias] = module
    spec.loader.exec_module(module)
    return module


q = _load("qe_diagnosis_1533", "qe_diagnosis_1533_in_1615")
prior = _load("post_month_end_split_1611", "post_month_end_split_1611_in_1615")
MEDIAN_INDEX = sp.GRID.index(0.5)
G05, G95 = q.G[0.05], q.G[0.95]
QUARTER_END_TARGET_MONTHS = prior.QUARTER_END_TARGET_MONTHS
BUSINESS_DAYS = prior.BUSINESS_DAYS
GROUPS = tuple(f"bd{b}_{kind}" for kind in ("quarter", "other") for b in BUSINESS_DAYS)


def committed_declaration(path: Path = DECLARATION) -> dict:
    """The declaration, refused unless it is committed and unchanged since `HEAD`."""

    return q.committed_declaration(path)


# -- the groups -----------------------------------------------------------------------------------------------------------------------


def group_of(day: date) -> Optional[str]:
    """The group of a target day: its business day (1 to 3) crossed with the kind of the month-end before it; None outside business days 1 to 3."""

    b = prior.business_day(day)
    if b not in BUSINESS_DAYS:
        return None
    return f"bd{b}_{'quarter' if day.month in QUARTER_END_TARGET_MONTHS else 'other'}"


# -- the terms ------------------------------------------------------------------------------------------------------------------------


def shrunk_shift(median_error: float, n: int, k: float = K, min_train: int = MIN_TRAIN) -> float:
    """The shrunk shift `n / (n + k)` times the median error (bp); 0 with fewer than `min_train` cells or a median that is not finite."""

    if n < min_train or not math.isfinite(median_error):
        return 0.0
    return n / (n + k) * median_error


def shrunk_factor(ratio: float, n: int, k: float = K, min_train: int = MIN_TRAIN) -> float:
    """The shrunk factor `1 + n / (n + k) (ratio - 1)`; 1 with fewer than `min_train` cells or a ratio that is not a positive finite number."""

    if n < min_train or not (isinstance(ratio, float) and math.isfinite(ratio) and ratio > 0.0):
        return 1.0
    return 1.0 + n / (n + k) * (ratio - 1.0)


def arm_terms(arm: str, shift: float, lower: float, upper: float) -> Tuple[float, float, float]:
    """The (shift, lower factor, upper factor) an arm applies: all three, the shift alone, or the two factors alone."""

    if arm == "arm":
        return shift, lower, upper
    if arm == "location":
        return shift, 1.0, 1.0
    if arm == "scale":
        return 0.0, lower, upper
    raise ValueError(f"unknown arm {arm!r}")


def apply_terms(quantiles: Sequence[float], raw: Sequence[float], shift: float, lower: float, upper: float) -> List[float]:
    """The candidate's quantiles with each side scaled about the median by its factor and the whole set shifted by `shift`; the same numbers at (0, 1, 1).

    Where the candidate's cap bound on the cell (a level whose final value differs from its raw one), no quantile ends above the largest capped value.
    """

    out = list(quantiles)
    if shift == 0.0 and lower == 1.0 and upper == 1.0:
        return out
    mid = quantiles[MEDIAN_INDEX]
    for i, value in enumerate(quantiles):
        m = 1.0 if i == MEDIAN_INDEX else (lower if i < MEDIAN_INDEX else upper)
        out[i] = mid + m * (value - mid) + shift
    capped = [quantiles[i] for i in range(len(quantiles)) if quantiles[i] != raw[i]]
    if capped:
        cap = max(capped)
        out = [min(x, cap) for x in out]
    return out


def check_asof(cells: Sequence[Mapping[str, object]], decision_day: str) -> None:
    """Refuse a training cell whose target day is not before the decision day: raises `LookAheadError`."""

    for c in cells:
        if c["t"] >= decision_day:
            raise LookAheadError(f"post_month_end_terms_1615: a training cell targets {c['t']}, not before the decision day {decision_day}")


def training_before(cells: Sequence[Mapping[str, object]], decision_day: str) -> List[Mapping[str, object]]:
    """The cells whose target day is strictly before `decision_day`, checked."""

    out = [c for c in cells if c["t"] < decision_day]
    check_asof(out, decision_day)
    return out


def fit_group(train: Sequence[Mapping[str, object]], k: float = K, min_train: int = MIN_TRAIN) -> Dict[str, float]:
    """One group's terms from its training cells: the shrunk median of y - q50_raw and the two shrunk #1533 ratios; the identity under `min_train` usable cells."""

    usable = [c for c in train if c["raw"][G05] < c["raw"][G95]]
    n = len(usable)
    if n < min_train:
        return {"n": n, "shift": 0.0, "lower": 1.0, "upper": 1.0}
    median_error = q.median([c["y"] - c["raw"][MEDIAN_INDEX] for c in usable])
    ratios = q.shape_ratios(usable)["ratio"]
    return {"n": n, "shift": shrunk_shift(median_error, n, k, min_train), "lower": shrunk_factor(ratios.get("0.05", float("nan")), n, k, min_train),
            "upper": shrunk_factor(ratios.get("0.95", float("nan")), n, k, min_train)}


def walk_forward_terms(cells: Sequence[Mapping[str, object]], decision_days: Sequence[str], group_of_cell: Callable[[Mapping[str, object]], Optional[str]],
                       *, k: float = K, min_train: int = MIN_TRAIN) -> Dict[str, Dict[str, Dict[str, float]]]:
    """For each decision day, the terms of every group fitted on the group's cells with a target day before it.

    `cells` is every cell in the walk (both windows) with `t`, `y` and `raw`; `group_of_cell(cell)` its group or None. Cells are visited in target-day
    order so each group's training list grows only by cells already scored.
    """

    ordered = sorted(cells, key=lambda c: (c["t"], c["d"], c["h"]))
    held: Dict[str, List[Mapping[str, object]]] = {g: [] for g in GROUPS}
    pointer = 0
    out: Dict[str, Dict[str, Dict[str, float]]] = {}
    for day in sorted(decision_days):
        while pointer < len(ordered) and ordered[pointer]["t"] < day:
            g = group_of_cell(ordered[pointer])
            if g is not None:
                held[g].append(ordered[pointer])
            pointer += 1
        terms = {}
        for g in GROUPS:
            check_asof(held[g], day)
            terms[g] = fit_group(held[g], k, min_train)
        out[day] = terms
    return out


def check_outside_identical(days: Sequence[Tuple[str, Sequence[float], Sequence[float], bool]]) -> int:
    """Refuse an arm forecast that differs from the candidate's on a day outside every group. Rows: (cell, candidate, arm, in a group)."""

    checked = 0
    for where, candidate, arm, inside in days:
        if inside:
            continue
        checked += 1
        if list(candidate) != list(arm):
            raise ValueError(f"{where}: the arm differs from the candidate on a day outside every group")
    return checked


# -- the figures ----------------------------------------------------------------------------------------------------------------------

SUFFIX = {"arm": "arm", "location": "loc", "scale": "scl"}
#: The per-cell vector the splits average, in this order: d = reference - arm (positive favours the arm), strict tail misses, and the cell scores.
VEC: Tuple[str, ...] = (
    tuple(f"d_{SUFFIX[a]}_cand_{m}" for m in ("crps", "tw") for a in ARMS)
    + tuple(f"d_arm_{r}_{m}" for m in ("crps", "tw") for r in REFERENCES)
    + tuple(f"{SUFFIX[a]}_miss_{s}" for a in ARMS for s in ("low", "up"))
    + ("cand_miss_low", "cand_miss_up")
)
INDEX = {name: i for i, name in enumerate(VEC)}
SCORE_NAMES = ("candidate", "arm", "location", "scale") + REFERENCES


def cell_scores(quantile_sets: Mapping[str, Sequence[float]], y: float) -> Dict[str, Dict[str, float]]:
    """Grid CRPS and upper-tail twCRPS of each named quantile set at the outcome."""

    return {"crps": {n: sp.grid_crps(v, y) for n, v in quantile_sets.items()}, "tw": {n: sp.upper_tail_twcrps(v, y) for n, v in quantile_sets.items()}}


def cell_vec(arms: Mapping[str, Sequence[float]], cand_q: Sequence[float], y: float, refs: Mapping[str, Sequence[float]]) -> Tuple[List[float], dict]:
    """The numbers one cell contributes (the vector in `VEC`) and its scores by metric and by forecast."""

    sets = {"candidate": cand_q, **arms, **refs}
    sc = cell_scores(sets, y)
    out: List[float] = []
    for m in ("crps", "tw"):
        out += [sc[m]["candidate"] - sc[m][a] for a in ARMS]
    for m in ("crps", "tw"):
        out += [sc[m][r] - sc[m]["arm"] for r in REFERENCES]
    for a in ARMS:
        out += [float(y < arms[a][G05]), float(y > arms[a][G95])]
    out += [float(y < cand_q[G05]), float(y > cand_q[G95])]
    return out, sc


def bootstrap_means(rows: Sequence[Mapping[str, object]], *, reps: int = REPS, seed: int = SEED) -> List[List[float]]:
    """Each coordinate's mean over the rows with a 90% percentile interval: [point, low, high]. Rows are `{"t": target day, "v": vector}`; the target days
    are resampled in date order by the stationary bootstrap (mean block 10) and every row of a drawn day comes with it."""

    import random

    by: Dict[str, List[Sequence[float]]] = defaultdict(list)
    for r in rows:
        by[r["t"]].append(r["v"])
    days = sorted(by)
    width = len(rows[0]["v"])
    sums = {d: [sum(v[j] for v in by[d]) for j in range(width)] for d in days}
    counts = {d: len(by[d]) for d in days}
    total = [sum(sums[d][j] for d in days) for j in range(width)]
    n = sum(counts.values())
    rng = random.Random(seed)
    draws: List[List[float]] = [[] for _ in range(width)]
    for _ in range(reps):
        picked = [days[i] for i in q.stationary_indices(len(days), q.BLOCK, rng)]
        c = sum(counts[d] for d in picked)
        for j in range(width):
            draws[j].append(sum(sums[d][j] for d in picked) / c)
    out = []
    for j in range(width):
        lo, hi = q.interval_of(draws[j])
        out.append([total[j] / n, lo, hi])
    return out


def figures(cells: Sequence[Mapping[str, object]]) -> dict:
    """The paired differences and tail misses of a set of cells, with intervals; 'too few' under `MIN_CELLS` cells."""

    if len(cells) < MIN_CELLS:
        return {"cells": len(cells), "note": "too few"}
    stats = bootstrap_means([{"t": c["t"], "v": c["vec"]} for c in cells])
    out = {"cells": len(cells), "target_days": len({c["t"] for c in cells}), "changed": sum(1 for c in cells if c["changed"]) / len(cells)}
    out.update({name: stats[i] for i, name in enumerate(VEC)})
    return out


# -- the pooled protocol test --------------------------------------------------------------------------------------------------------


def decision_series(cells: Sequence[Mapping[str, object]], metric: str, name: str) -> Dict[date, float]:
    """One score per decision day: the mean over its five leads of forecast `name`'s `metric` score."""

    by: Dict[str, List[float]] = defaultdict(list)
    for c in cells:
        by[c["d"]].append(c["sc"][metric][name])
    for d, v in by.items():
        if len(v) != len(sp.HORIZONS):
            raise ValueError(f"decision day {d} has {len(v)} leads, not {len(sp.HORIZONS)}")
    return {date.fromisoformat(d): sum(v) / len(v) for d, v in by.items()}


def two_sided(test, level: float = 0.90) -> List[float]:
    """The point and the two-sided studentized interval of mean(d): the point less the (1 - a) and a quantiles of the t-draws times the HAC standard error."""

    a = (1.0 - level) / 2.0
    t = test.t_draws
    return [test.mean_difference, test.mean_difference - q.quantile_of_sorted(t, 1.0 - a) * test.standard_error,
            test.mean_difference - q.quantile_of_sorted(t, a) * test.standard_error]


def pooled(cells: Sequence[Mapping[str, object]], *, draws: int = DRAWS) -> dict:
    """Pooled grid CRPS and twCRPS per decision day, on the protocol's studentized stationary bootstrap, one resample stream for every pair.

    The pair is (reference score, arm score), d = reference - arm: positive favours the arm. The candidate against each benchmark is the same pair with
    the candidate's score in place of the arm's.
    """

    out: dict = {}
    for metric in ("crps", "tw"):
        series = {n: decision_series(cells, metric, n) for n in SCORE_NAMES}
        pairs, names = [], []
        for a in ARMS:
            pairs.append((series["candidate"], series[a]))
            names.append(f"{a}_vs_candidate")
        for r in REFERENCES:
            pairs.append((series[r], series["arm"]))
            names.append(f"arm_vs_{r}")
            pairs.append((series[r], series["candidate"]))
            names.append(f"candidate_vs_{r}")
        tests = sp.paired_tests(pairs, seed=SEED, draws=draws, with_skill=False)
        out["grid_crps" if metric == "crps" else "twcrps"] = {
            "days": len(series["arm"]), "means": {n: sum(s.values()) / len(s) for n, s in series.items()},
            "pairs": {name: two_sided(t) for name, t in zip(names, tests)},
        }
    return out


def verdict_of(interval: Sequence[float]) -> str:
    """The declared reading of a candidate - arm grid-CRPS difference: loses at mean d <= 0, wins when the 90% interval is wholly above 0."""

    if interval[0] <= 0.0:
        return "loses"
    return "wins" if interval[1] > 0.0 else "undecided"


# -- the run ---------------------------------------------------------------------------------------------------------------------------


def build_cells(loaded: Mapping[str, "q.Window"], k: float = K) -> Tuple[List[dict], dict]:
    """Every cell of both windows with its three arms' quantiles and per-cell vector, and the terms' path."""

    cells: List[dict] = []
    for name, window in loaded.items():
        for c in window.cells:
            meta = window.doc["targets"][c["t"]]
            refs = {r: window.models[r][c["i"]] for r in REFERENCES}
            cells.append(dict(c, window=name, types=meta["types"], group=group_of(date.fromisoformat(c["t"])), refs=refs))
    decision_days = sorted({c["d"] for c in cells})
    fitted = walk_forward_terms(cells, decision_days, lambda c: c["group"], k=k)
    checks = []
    for c in cells:
        inside = c["group"] is not None
        t = fitted[c["d"]][c["group"]] if inside else {"shift": 0.0, "lower": 1.0, "upper": 1.0}
        arms = {a: apply_terms(c["q"], c["raw"], *arm_terms(a, t["shift"], t["lower"], t["upper"])) for a in ARMS}
        for a in ARMS:
            checks.append((f"{c['d']} lead {c['h']} {a}", c["q"], arms[a], inside))
        c["terms"] = {kk: t[kk] for kk in ("shift", "lower", "upper")}
        c["changed"] = inside and arms["arm"] != list(c["q"])
        c["vec"], c["sc"] = cell_vec(arms, c["q"], c["y"], c["refs"])
    outside = check_outside_identical(checks)
    return cells, {"terms": fitted, "outside_cells_checked_identical": outside}


def split_rows(cells: Sequence[dict]) -> Dict[str, Dict[str, dict]]:
    """The figures of the post-month-end window (the cells in a group) as a whole, by business day, by group, by regime and by lead."""

    inside = [c for c in cells if c["group"] is not None]

    def by(key: Callable[[dict], object]) -> Dict[str, dict]:
        groups: Dict[str, List[dict]] = defaultdict(list)
        for c in inside:
            groups[str(key(c))].append(c)
        return {k: figures(v) for k, v in sorted(groups.items())}

    return {
        "window": {"post_month_end_window": figures(inside), "all days": figures(list(cells))},
        "by_business_day": by(lambda c: c["group"][:3]),
        "by_group": by(lambda c: c["group"]),
        "by_regime": by(lambda c: c["regime"]),
        "by_lead": by(lambda c: c["h"]),
    }


def term_summary(path: Mapping[str, Mapping[str, Mapping[str, float]]], days: Sequence[str]) -> dict:
    """Each group's terms at the first decision day of each calendar year and at the last day of the window, their range and the first day they leave the identity."""

    out: dict = {}
    ordered = sorted(days)
    firsts: Dict[str, str] = {}
    for d in ordered:
        firsts.setdefault(d[:4], d)
    identity = {"shift": 0.0, "lower": 1.0, "upper": 1.0}
    for g in GROUPS:
        for term in ("shift", "lower", "upper"):
            series = [path[d][g][term] for d in ordered]
            out[f"{g} {term}"] = {"first_of_year": {y: path[d][g][term] for y, d in firsts.items()}, "last": series[-1], "min": min(series), "max": max(series),
                                  "first_not_identity": next((d for d in ordered if path[d][g][term] != identity[term]), None),
                                  "training_cells_last": path[ordered[-1]][g]["n"]}
    return out


def score_command(args) -> int:
    declared = committed_declaration()
    record = json.loads(RECORD_1363.read_text(encoding="utf-8"))
    loaded: Dict[str, "q.Window"] = {}
    result: dict = {"issue": 1615, "declaration": "metadata/post_month_end_terms_1615.json", "label": "development, not a verdict", "seed": SEED, "reps": REPS,
                    "draws": DRAWS, "k": K, "min_train": MIN_TRAIN, "amendments": declared["amendments"], "walk_files": {}, "windows": {}}
    for name in q.WINDOWS:
        window = q.load_window(name, Path(args.walks), Path(args.extensions), record)
        if window is None:
            continue
        prior.check_flag_agreement(window.doc["targets"])
        prior.check_unlocked(window.cells)
        loaded[name] = window
        result["panel_sha256"] = window.doc["panel_sha256"]
        result["walk_files"][name] = {"sha256": window.ext["walk_sha256"], "refits": window.ext["walk_refits"]}
    if "development" not in loaded:
        raise SystemExit("the development walk is required")
    cells, info = build_cells(loaded)
    result["outside_cells_checked_identical"] = info["outside_cells_checked_identical"]
    ref = json.loads(RECORD_1547.read_text(encoding="utf-8"))["windows"]["development"]["groups"]["post_month_end_window"]
    result["reproduces_1547_cells"] = prior.check_reproduction([c for c in cells if c["window"] == "development"], ref)
    for name in loaded:
        mine = [c for c in cells if c["window"] == name]
        days = sorted({c["d"] for c in mine})
        entry = {"cells": len(mine), "decision_days": len(days), "cells_in_a_group": sum(1 for c in mine if c["group"] is not None),
                 "cells_changed": sum(1 for c in mine if c["changed"]), "group_cells": {g: sum(1 for c in mine if c["group"] == g) for g in GROUPS},
                 "splits": split_rows(mine)}
        if name == "development":
            entry["terms"] = term_summary(info["terms"], days)
            entry["pooled"] = pooled(mine)
            entry["pooled_reading"] = verdict_of(entry["pooled"]["grid_crps"]["pairs"]["arm_vs_candidate"])
            entry["window_reading"] = verdict_of(entry["splits"]["window"]["post_month_end_window"]["d_arm_cand_crps"])
        result["windows"][name] = entry
        print(f"{name}: done", flush=True)
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    Path(args.output).write_text(json.dumps(q.rounded(result), indent=1, sort_keys=True) + "\n", encoding="utf-8")
    return 0


# -- the page -------------------------------------------------------------------------------------------------------------------------


def iv(x: Sequence[float], d: int = 3) -> str:
    return f"{x[0]:+.{d}f} [{x[1]:+.{d}f}, {x[2]:+.{d}f}]"


def rate(x: Sequence[float]) -> str:
    return f"{x[0]:.3f} [{x[1]:.3f}, {x[2]:.3f}]"


def table(headers: Sequence[str], rows: Sequence[Sequence[str]]) -> List[str]:
    return ["| " + " | ".join(headers) + " |", "|" + "---|" * len(headers)] + ["| " + " | ".join(r) + " |" for r in rows]


def diff_rows(split: Mapping[str, dict], label: str) -> List[List[str]]:
    """Rows of the arms against the candidate and the primary arm against the benchmarks, for grid CRPS and twCRPS."""

    rows = []
    for key, v in split.items():
        if "note" in v:
            rows.append([key, str(v["cells"])] + ["too few"] * 8)
            continue
        rows.append([key, str(v["cells"]), f"{v['changed']:.2f}"] + [iv(v[f"d_{s}_cand_crps"]) for s in ("arm", "loc", "scl")]
                    + [iv(v[f"d_{s}_cand_tw"]) for s in ("arm", "loc", "scl")] + [iv(v["d_arm_B1_prime_crps"]), iv(v["d_arm_B2_crps"])])
    return rows


DIFF_HEADERS = ("cells", "share changed", "CRPS arm vs candidate", "CRPS location", "CRPS scale", "twCRPS arm vs candidate", "twCRPS location", "twCRPS scale",
                "CRPS arm vs B1'", "CRPS arm vs B2")


def page(r: Mapping[str, object]) -> str:
    dev = r["windows"]["development"]
    sp_dev = dev["splits"]
    win = sp_dev["window"]["post_month_end_window"]
    L: List[str] = []
    w = L.append
    w("# Day-specific location and scale terms for the post-month-end business days 1 to 3 (#1615)")
    w("")
    w("**Development, not a verdict.** H5, a development arm on the frozen candidate's known limit (post-month-end band coverage). The arms do not change the frozen candidate (s3c-ann-net); "
      "they are in `not_arms` of the H5 registration manifest until Eleonora rules. No lockbox day, no re-score of a published record, nothing registered or published. Every figure is read "
      "from `docs/research/post-month-end-terms-1615/result.json`; the declaration is `metadata/post_month_end_terms_1615.json`, committed before any score. The forecasts are #1533's walk "
      "extension, regenerated bit-identical from the 1363 walk (no refit). The business-day cells reproduce #1547's `post_month_end_window` group "
      f"({r['reproduces_1547_cells']['cells']} cells).")
    w("")
    w("**Prior work** (`docs/research/settled-questions.md`). S18 (#1275, failed) used a spike-sized carryover term that is non-zero only at lead 1 on business day 2, and names a business-day split "
      "of the misses as what would reopen it; #1611 and #1614 made that split. This arm differs from S18: no term reads the month-end spread (not public before business day 2), the terms are "
      "by calendar position alone and act at every lead, with a location shift and a scale per group. #1555's `post_month_end_window` q95 scale (one group, one tail) lost on this window.")
    w("")
    w("## The arms")
    w("")
    w("A target day is in one of six groups: business day 1, 2 or 3 of its month (`bday_of_month`) crossed with the kind of the month-end before it (quarter-end when the target falls in January, "
      "April, July or October). Each group has a shift in bp (the median of y - q50 on its earlier cells) and a lower and an upper factor (#1533's section 2b ratios on those cells), each "
      f"shrunk by n / (n + {r['k']}) toward 0 or 1 and left at 0 or 1 under {r['min_train']} usable cells, the same at every lead. A cell is a training cell only if its target day is strictly "
      "before the decision day. Three arms: `arm` (shift and factors, the primary), `location` (the shift alone) and `scale` (the factors alone). A quantile set is "
      "`q50 + shift + m (q_i - q50)`; the candidate's cap is not undone. Every other forecast is the candidate's, the same numbers "
      f"({r['outside_cells_checked_identical']} arm cells outside the groups were checked equal). No term reads the month-end spread. The arms call no guarded fitter, so none is a producer for the provisional register.")
    w("")
    w("The terms the walk gave (first decision day of each year, last day of the window, range):")
    w("")
    rows = []
    for name, v in dev["terms"].items():
        years = ", ".join(f"{y}: {m:+.2f}" if name.endswith("shift") else f"{y}: {m:.2f}" for y, m in v["first_of_year"].items())
        rows.append([name, years, f"{v['last']:.2f}", f"{v['min']:.2f} to {v['max']:.2f}", str(v["training_cells_last"])])
    L += table(["group, term", "first decision day of each year", "last day", "range", "training cells at the last day"], rows)
    w("")
    pc, pt = dev["pooled"]["grid_crps"]["pairs"]["arm_vs_candidate"], dev["pooled"]["twcrps"]["pairs"]["arm_vs_candidate"]
    w("## Reading")
    w("")
    w(f"On the post-month-end window ({win['cells']} development cells, {win['target_days']} target days) the primary arm's grid CRPS is {iv(win['d_arm_cand_crps'])} against the candidate and its "
      f"upper-tail twCRPS {iv(win['d_arm_cand_tw'])} (positive favours the arm; 90% interval from the stationary bootstrap of the target days). By the declared rule the window reading is: "
      f"**{dev['window_reading']}**. The location arm alone: grid CRPS {iv(win['d_loc_cand_crps'])}, twCRPS {iv(win['d_loc_cand_tw'])}. The scale arm alone: grid CRPS {iv(win['d_scl_cand_crps'])}, "
      f"twCRPS {iv(win['d_scl_cand_tw'])}.")
    w("")
    w(f"Pooled over all {dev['pooled']['grid_crps']['days']} development decision days, on the protocol's studentized bootstrap, the primary arm's grid CRPS is {iv(pc)} against the candidate and its "
      f"upper-tail twCRPS {iv(pt)}; the pooled reading is **{dev['pooled_reading']}**. The pooled figure is diluted by the days the arms leave alone ({dev['cells_changed']} of {dev['cells']} cells changed).")
    w("")
    w("The rule (loses when the difference candidate - arm is not above 0, wins when its 90% interval lies wholly above 0) is marked as a question in the pull request.")
    w("")
    w("**Where the grid-CRPS difference sits** (the primary arm against the candidate; rows whose 90% interval lies wholly above or wholly below 0, development window):")
    w("")
    for split, title in (("by_business_day", "business day"), ("by_group", "group"), ("by_regime", "regime")):
        better = [k for k, v in sp_dev[split].items() if "note" not in v and v["d_arm_cand_crps"][1] > 0.0]
        worse = [k for k, v in sp_dev[split].items() if "note" not in v and v["d_arm_cand_crps"][2] < 0.0]
        w(f"- By {title}: interval above 0 for {', '.join(better) or 'none'}; below 0 for {', '.join(worse) or 'none'}.")
    later_win = r["windows"].get("2026", {}).get("splits", {}).get("window", {}).get("post_month_end_window")
    if later_win and "note" not in later_win:
        w(f"- The 2026 days, shown apart and deciding nothing: grid CRPS {later_win['d_arm_cand_crps'][0]:+.3f}, twCRPS {later_win['d_arm_cand_tw'][0]:+.3f} on {later_win['cells']} post-month-end cells.")
    w("")
    w("## Pooled, on scoring protocol v1's studentized stationary bootstrap")
    w("")
    w(f"One score per decision day (the mean over h = 1 to 5), development window. d = reference score - arm score: positive favours the arm. Two-sided 90% intervals from the studentized draws of "
      f"`paired_tests` (mean block 10, {r['draws']} draws, HAC lag 10, seed {r['seed']}).")
    w("")
    for metric, title in (("grid_crps", "Grid CRPS (primary)"), ("twcrps", "Upper-tail twCRPS (key secondary)")):
        p = dev["pooled"][metric]
        w(f"### {title}")
        w("")
        w("Mean over the decision days: " + ", ".join(f"{REFERENCE_NAMES.get(n, n)} {m:.3f}" for n, m in p["means"].items()) + ".")
        w("")
        rows = [["arm", iv(p["pairs"]["arm_vs_candidate"]), iv(p["pairs"]["arm_vs_B1"]), iv(p["pairs"]["arm_vs_B1_prime"]), iv(p["pairs"]["arm_vs_B2"])],
                ["location", iv(p["pairs"]["location_vs_candidate"]), "-", "-", "-"],
                ["scale", iv(p["pairs"]["scale_vs_candidate"]), "-", "-", "-"],
                ["candidate (unchanged)", "-", iv(p["pairs"]["candidate_vs_B1"]), iv(p["pairs"]["candidate_vs_B1_prime"]), iv(p["pairs"]["candidate_vs_B2"])]]
        L += table(["", "vs candidate", "vs B1", "vs B1'", "vs B2"], rows)
        w("")
    w("## Splits")
    w("")
    w("Each row's cells, the share of them the primary arm changed, and the paired differences (reference - arm, positive favours the arm) with 90% intervals from the stationary bootstrap of the "
      "row's target days (mean block 10, 1000 resamples, seed 1615). Rows are the post-month-end cells unless named. The three CRPS columns are against the candidate; the last two are the primary arm "
      "against B1' and B2.")
    w("")
    for split, title in (("window", "the window, and all days"), ("by_business_day", "business day"), ("by_group", "business day and kind of month-end"), ("by_regime", "regime (post-month-end cells)"),
                         ("by_lead", "lead (post-month-end cells)")):
        w(f"### By {title}")
        w("")
        L += table([title.split(" (")[0].split(",")[0]] + list(DIFF_HEADERS), diff_rows(sp_dev[split], title))
        w("")
    w("## Coverage of the 90% band, per tail, before and after")
    w("")
    w("Strict share of cells below q05 and above q95 (nominal 0.05 each), the candidate and each arm, with 90% intervals as above.")
    w("")
    for split, title in (("window", "scope"), ("by_business_day", "business day"), ("by_group", "group")):
        rows = []
        for key, v in sp_dev[split].items():
            if "note" in v:
                continue
            rows.append([key, str(v["cells"])] + [rate(v[f"{s}_miss_{t}"]) for t in ("low", "up") for s in ("cand", "arm", "loc", "scl")])
        L += table([title, "cells"] + [f"{t} {n}" for t in ("below q05,", "above q95,") for n in ("candidate", "arm", "location", "scale")], rows)
        w("")
    w("## The 2026 days (shown apart, decide nothing)")
    w("")
    later = r["windows"].get("2026")
    if later:
        w(f"{later['cells_changed']} of {later['cells']} cells changed. Point values of d (positive favours the arm), grid CRPS and twCRPS of the primary arm against the candidate:")
        w("")
        rows = []
        for key, v in list(later["splits"]["window"].items()) + list(later["splits"]["by_group"].items()):
            if "note" in v:
                rows.append([key, str(v["cells"]), "too few", "too few"])
            else:
                rows.append([key, str(v["cells"]), f"{v['d_arm_cand_crps'][0]:+.3f}", f"{v['d_arm_cand_tw'][0]:+.3f}"])
        L += table(["scope", "cells", "CRPS, arm vs candidate", "twCRPS, arm vs candidate"], rows)
        w("")
    w("## What this does and does not show")
    w("")
    w("- It is development evidence on days already seen. The business days and the kind of month-end were chosen by #1611 and #1614 from the same development window, so the arm is scored on the sample that "
      "selected it; the figures flatter it.")
    w("- The terms are walk-forward and as-of, but k = 100 cells, the 50-cell minimum and the six groups are this study's choices, marked as questions in the pull request. No other value was run.")
    w("- The cap is kept only where it bound on a cell (the walk file does not carry the line itself).")
    w("- It does not read the month-end spread, so it does not test S18's carryover again; it tests whether calendar position alone, with a shift and a scale per group, helps.")
    w("- No verdict: only prospective confirmation days give one. The 2026 days are shown apart and decide nothing.")
    w("")
    w("## Reproduction")
    w("")
    w("See the header of `scripts/post_month_end_terms_1615.py`; the test is `tests/test_post_month_end_terms_1615.py`. Seed 1615 throughout.")
    w("")
    return "\n".join(L)


def page_command(args) -> int:
    r = json.loads(Path(args.score).read_text(encoding="utf-8"))
    Path(args.output).write_text(page(r), encoding="utf-8")
    return 0


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="command", required=True)
    s = sub.add_parser("score", help="the arms and their figures from the walk files and their extensions")
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
