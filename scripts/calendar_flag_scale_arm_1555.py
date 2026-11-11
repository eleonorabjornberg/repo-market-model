"""A per-tail scale of (s3c-ann-net)'s quantiles by the target day's calendar flag, fitted walk-forward (#1555, avenue #1546, H5, step 4).

A development arm, never a verdict. It reads the candidate's own forecasts and cells (the walk extension of `scripts/qe_diagnosis_1533.py`, regenerated
bit-identical from the 1363 walk; no new walk, no refit) and changes nothing of the candidate. Every choice is in
`metadata/calendar_flag_scale_arm_1555.json`, which `score` refuses to read unless it is committed and unchanged. No day after 2026-09-03 and no locked
day is read.

On a target day in an arm group (`dom_19_23`: both tails; `coupon_settlement`, `post_month_end_window`, days with no flag and no pressure type: the q95
side), the candidate's quantiles on that side of the median are scaled about q50 by the factor of the day's flags (geometric mean over overlapping
flags). Each factor is `m = 1 + n / (n + k) * (ratio - 1)`, `ratio` #1533's section 2b statistic on the group's training cells: the cells whose target day
is strictly before the decision day, at every lead. Quarter-end days are in no group. Every other forecast is the candidate's, the same numbers.

    PYTHONPATH=src python3 -m repo_model.cli build --raw-root tests/fixtures/snapshots/funding_inputs --output PUB.csv \\
        --build-cutoff 2026-09-08T21:31:42+00:00 --decision-time 18:00:00
    for W in development 2026; do
      RMM_DECISION_TIME=18:00 PYTHONPATH=src python3 scripts/qe_diagnosis_1533.py walk --panel PUB.csv --window $W \\
          --output WALK/$W.json --extension EXT/$W.json
    done
    OUT=docs/research/calendar-flag-scale-arm-1555
    PYTHONPATH=src python3 scripts/calendar_flag_scale_arm_1555.py score --walks WALK --extensions EXT --output $OUT/result.json
    PYTHONPATH=src python3 scripts/calendar_flag_scale_arm_1555.py page --score $OUT/result.json \\
        --output docs/research/calendar-flag-scale-arm-1555-result.md

The walks take about four minutes and the scoring a few: below the `long-run` line. Stdlib only.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import math
import random
import sys
from collections import defaultdict
from datetime import date
from pathlib import Path
from typing import Callable, Dict, List, Mapping, Optional, Sequence, Tuple

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))

from repo_model import scoring_protocol as sp  # noqa: E402
from repo_model.splits import LookAheadError  # noqa: E402

DECLARATION = REPO / "metadata" / "calendar_flag_scale_arm_1555.json"
RECORD_1363 = REPO / "docs" / "research" / "candidate-calibration-1363" / "result.json"
SEED = 1555
REPS = 1000
DRAWS = 10_000
K = 500
MIN_TRAIN = 100
MIN_CELLS = 30
MEDIAN_INDEX = sp.GRID.index(0.5)


def _load(name: str, alias: str):
    spec = importlib.util.spec_from_file_location(alias, REPO / "scripts" / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[alias] = module
    spec.loader.exec_module(module)
    return module


q = _load("qe_diagnosis_1533", "qe_diagnosis_1533_in_1555")

#: The arm's groups and, for each, the tails (levels of the ratio) it scales.
GROUP_TAILS: Mapping[str, Tuple[str, ...]] = {
    "dom_19_23": ("0.05", "0.95"), "coupon_settlement": ("0.95",), "post_month_end_window": ("0.95",), "no_flag": ("0.95",),
}
ARM_GROUPS = tuple(GROUP_TAILS)
QUARTER_END_PRESSURE = ("quarter_end_turn", "year_end")
REFERENCES = ("B1", "B1_prime", "B2")
REFERENCE_NAMES = {"candidate": "candidate", "B1": "B1", "B1_prime": "B1'", "B2": "B2"}


def committed_declaration(path: Path = DECLARATION) -> dict:
    """The declaration, refused unless it is committed and unchanged since `HEAD`."""

    return q.committed_declaration(path)


# -- the arm -------------------------------------------------------------------------------------------------------------------------


def arm_groups(types: Sequence[str], pressure: str) -> List[str]:
    """The arm groups a target day is in (they overlap); a quarter-end day is in none."""

    if "quarter_end" in types or pressure in QUARTER_END_PRESSURE:
        return []
    out = [name for name in ("dom_19_23", "coupon_settlement", "post_month_end_window") if name in types]
    if list(types) == ["ordinary"] and pressure == "ordinary":
        out.append("no_flag")
    return out


def multiplier(ratio: float, n: int, k: float = K, min_train: int = MIN_TRAIN) -> float:
    """The shrunk factor `1 + n / (n + k) (ratio - 1)`; 1 with fewer than `min_train` cells or a ratio that is not a positive finite number."""

    if n < min_train or not (isinstance(ratio, float) and math.isfinite(ratio) and ratio > 0.0):
        return 1.0
    return 1.0 + n / (n + k) * (ratio - 1.0)


def combine(factors: Sequence[float]) -> float:
    """The geometric mean of the factors of the groups a day is in (1 for none): an overlap neither compounds nor lets one group override another."""

    if not factors:
        return 1.0
    return math.exp(sum(math.log(f) for f in factors) / len(factors))


def scale_quantiles(quantiles: Sequence[float], m_low: float, m_high: float) -> List[float]:
    """The quantiles with each side of the median scaled about q50 by its factor; the identity (the same numbers) at 1 and 1."""

    out = list(quantiles)
    mid = out[MEDIAN_INDEX]
    for i, value in enumerate(quantiles):
        if i < MEDIAN_INDEX and m_low != 1.0:
            out[i] = mid + m_low * (value - mid)
        elif i > MEDIAN_INDEX and m_high != 1.0:
            out[i] = mid + m_high * (value - mid)
    return out


def check_asof(cells: Sequence[Mapping[str, object]], decision_day: str) -> None:
    """Refuse a training cell whose target day is not before the decision day: raises `LookAheadError`."""

    for c in cells:
        if c["t"] >= decision_day:
            raise LookAheadError(f"calendar_flag_scale_arm_1555: a training cell targets {c['t']}, not before the decision day {decision_day}")


def training_before(cells: Sequence[Mapping[str, object]], decision_day: str) -> List[Mapping[str, object]]:
    """The cells whose target day is strictly before `decision_day`, checked."""

    out = [c for c in cells if c["t"] < decision_day]
    check_asof(out, decision_day)
    return out


def walk_forward_factors(cells: Sequence[Mapping[str, object]], decision_days: Sequence[str], groups_of: Callable[[Mapping[str, object]], Sequence[str]],
                         *, k: float = K, min_train: int = MIN_TRAIN) -> Dict[str, Dict[Tuple[str, str], float]]:
    """For each decision day, the factor of every (group, tail) fitted on the group's cells with a target day before it.

    `cells` is every cell in the walk (both windows) with `t`, `y` and `raw`; `groups_of(cell)` its arm groups. Cells are visited in target-day order so each
    group's training list grows only by cells already scored.
    """

    ordered = sorted(cells, key=lambda c: (c["t"], c["d"], c["h"]))
    held: Dict[str, List[Mapping[str, object]]] = {g: [] for g in GROUP_TAILS}
    pointer = 0
    out: Dict[str, Dict[Tuple[str, str], float]] = {}
    for day in sorted(decision_days):
        while pointer < len(ordered) and ordered[pointer]["t"] < day:
            for g in groups_of(ordered[pointer]):
                held[g].append(ordered[pointer])
            pointer += 1
        factors: Dict[Tuple[str, str], float] = {}
        for g, tails in GROUP_TAILS.items():
            train = held[g]
            check_asof(train, day)
            usable = [c for c in train if c["raw"][q.G[0.95]] > c["raw"][q.G[0.05]]]
            ratios = q.shape_ratios(usable)["ratio"] if len(usable) >= min_train else {}
            for tau in tails:
                factors[(g, tau)] = multiplier(ratios.get(tau, float("nan")), len(usable), k, min_train)
        out[day] = factors
    return out


def day_factors(factors: Mapping[Tuple[str, str], float], groups: Sequence[str]) -> Tuple[float, float]:
    """The (lower, upper) factor of a day in `groups`: the geometric mean over its groups that carry each tail."""

    low = combine([factors[(g, "0.05")] for g in groups if "0.05" in GROUP_TAILS[g]])
    high = combine([factors[(g, "0.95")] for g in groups if "0.95" in GROUP_TAILS[g]])
    return low, high


def check_outside_identical(days: Sequence[Tuple[str, Sequence[float], Sequence[float], bool]]) -> int:
    """Refuse an arm forecast that differs from the candidate's on a day outside the arm. Rows: (cell, candidate, arm, in an arm group)."""

    checked = 0
    for where, candidate, arm, inside in days:
        if inside:
            continue
        checked += 1
        if list(candidate) != list(arm):
            raise ValueError(f"{where}: the arm differs from the candidate on a day outside the arm")
    return checked


# -- the figures ----------------------------------------------------------------------------------------------------------------------

#: The per-cell vector the splits average, in this order.
VEC = (
    "d_cand_crps", "d_B1_crps", "d_B1_prime_crps", "d_B2_crps", "d_cand_tw", "d_B1_tw", "d_B1_prime_tw", "d_B2_tw",
    "arm_miss_low", "arm_miss_up", "cand_miss_low", "cand_miss_up", "arm_crps", "cand_crps", "arm_tw", "cand_tw",
)


def cell_vec(arm_q: Sequence[float], cand_q: Sequence[float], y: float, refs: Mapping[str, Sequence[float]]) -> List[float]:
    """The numbers one cell contributes: d = reference - arm for grid CRPS and twCRPS (positive favours the arm), strict tail misses, the scores."""

    ac, at = sp.grid_crps(arm_q, y), sp.upper_tail_twcrps(arm_q, y)
    cc, ct = sp.grid_crps(cand_q, y), sp.upper_tail_twcrps(cand_q, y)
    out = [cc - ac, 0.0, 0.0, 0.0, ct - at, 0.0, 0.0, 0.0]
    for j, name in enumerate(REFERENCES):
        out[1 + j] = sp.grid_crps(refs[name], y) - ac
        out[5 + j] = sp.upper_tail_twcrps(refs[name], y) - at
    out += [float(y < arm_q[q.G[0.05]]), float(y > arm_q[q.G[0.95]]), float(y < cand_q[q.G[0.05]]), float(y > cand_q[q.G[0.95]]), ac, cc, at, ct]
    return out


def bootstrap_means(rows: Sequence[Mapping[str, object]], *, reps: int = REPS, seed: int = SEED) -> List[List[float]]:
    """Each coordinate's mean over the rows with a 90% percentile interval: [point, low, high]. Rows are `{"t": target day, "v": vector}`; the target days
    are resampled in date order by the stationary bootstrap (mean block 10) and every row of a drawn day comes with it."""

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
    out = {"cells": len(cells), "target_days": len({c["t"] for c in cells}), "changed": sum(1 for c in cells if c["inside"]) / len(cells)}
    out.update({name: stats[i] for i, name in enumerate(VEC)})
    return out


# -- the pooled protocol test --------------------------------------------------------------------------------------------------------


def decision_series(cells: Sequence[Mapping[str, object]], index: int) -> Dict[date, float]:
    """One score per decision day: the mean of coordinate `index` of the vector over its five leads."""

    by: Dict[str, List[float]] = defaultdict(list)
    for c in cells:
        by[c["d"]].append(c["vec"][index])
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
    for metric, mi, mine, theirs in (("grid_crps", 0, 12, 13), ("twcrps", 4, 14, 15)):
        arm = decision_series(cells, mine)
        cand = decision_series(cells, theirs)
        pairs, names = [(cand, arm)], ["arm_vs_candidate"]
        for j, ref in enumerate(REFERENCES):
            d_arm = decision_series(cells, mi + 1 + j)  # reference - arm, per day
            ref_score = {k: d_arm[k] + arm[k] for k in arm}
            pairs.append((ref_score, arm))
            names.append(f"arm_vs_{ref}")
            pairs.append((ref_score, cand))
            names.append(f"candidate_vs_{ref}")
        tests = sp.paired_tests(pairs, seed=SEED, draws=draws, with_skill=False)
        out[metric] = {
            "days": len(arm), "arm_mean": sum(arm.values()) / len(arm), "candidate_mean": sum(cand.values()) / len(cand),
            "pairs": {name: two_sided(t) for name, t in zip(names, tests)},
        }
    return out


def verdict_of(interval: Sequence[float]) -> str:
    """The declared reading of the pooled grid-CRPS difference candidate - arm: loses at mean d <= 0, wins when the 90% interval is wholly above 0."""

    if interval[0] <= 0.0:
        return "loses"
    return "wins" if interval[1] > 0.0 else "undecided"


# -- the run ---------------------------------------------------------------------------------------------------------------------------


def build_cells(loaded: Mapping[str, "q.Window"], k: float = K) -> Tuple[List[dict], dict]:
    """Every cell of both windows with its arm quantiles and per-cell vector, and the factor path."""

    cells: List[dict] = []
    for name, window in loaded.items():
        for c in window.cells:
            meta = window.doc["targets"][c["t"]]
            refs = {r: window.models[r][c["i"]] for r in REFERENCES}
            cells.append(dict(c, window=name, types=meta["types"], groups=arm_groups(meta["types"], meta["pressure"]), refs=refs))
    decision_days = sorted({c["d"] for c in cells})
    fitted = walk_forward_factors(cells, decision_days, lambda c: c["groups"], k=k)
    checks = []
    for c in cells:
        low, high = day_factors(fitted[c["d"]], c["groups"])
        c["m"] = (low, high)
        c["arm_q"] = scale_quantiles(c["q"], low, high)
        c["inside"] = bool(c["groups"]) and (low != 1.0 or high != 1.0)
        checks.append((f"{c['d']} lead {c['h']}", c["q"], c["arm_q"], bool(c["groups"])))
        c["vec"] = cell_vec(c["arm_q"], c["q"], c["y"], c["refs"])
    outside = check_outside_identical(checks)
    return cells, {"factors": fitted, "outside_cells_checked_identical": outside}


def split_rows(cells: Sequence[dict]) -> Dict[str, Dict[str, dict]]:
    """The figures by regime, by calendar flag, by pressure-day type and by lead."""

    def by(key: Callable[[dict], Sequence[object]]) -> Dict[str, dict]:
        groups: Dict[str, List[dict]] = defaultdict(list)
        for c in cells:
            for value in key(c):
                groups[str(value)].append(c)
        return {k: figures(v) for k, v in sorted(groups.items())}

    def flags(c: dict) -> List[str]:
        out = list(c["groups"])
        if "quarter_end" in c["types"] or c["pressure"] in QUARTER_END_PRESSURE:
            out.append("quarter_end (reference, in no arm group)")
        if not c["groups"]:
            out.append("in no arm group")
        out.append("all days")
        return out

    return {"by_regime": by(lambda c: [c["regime"]]), "by_flag": by(flags), "by_pressure": by(lambda c: [c["pressure"]]), "by_lead": by(lambda c: [c["h"]])}


def factor_summary(path: Mapping[str, Mapping[Tuple[str, str], float]], days: Sequence[str]) -> dict:
    """The factors of each (group, tail) at the first decision day of each calendar year and at the last day of the window, and their range."""

    out: dict = {}
    keys = sorted({k for v in path.values() for k in v})
    firsts = {}
    for d in sorted(days):
        firsts.setdefault(d[:4], d)
    for g, tau in keys:
        series = [path[d][(g, tau)] for d in sorted(days)]
        out[f"{g} q{tau[2:]}"] = {"first_of_year": {y: path[d][(g, tau)] for y, d in firsts.items()}, "last": series[-1], "min": min(series), "max": max(series),
                                  "first_not_one": next((d for d in sorted(days) if path[d][(g, tau)] != 1.0), None)}
    return out


def score_command(args) -> int:
    declared = committed_declaration()
    record = json.loads(RECORD_1363.read_text(encoding="utf-8"))
    loaded: Dict[str, "q.Window"] = {}
    result: dict = {"issue": 1555, "declaration": "metadata/calendar_flag_scale_arm_1555.json", "label": "development, not a verdict", "seed": SEED, "reps": REPS,
                    "draws": DRAWS, "k": K, "min_train": MIN_TRAIN, "amendments": declared["amendments"], "walk_files": {}, "windows": {}}
    for name in q.WINDOWS:
        window = q.load_window(name, Path(args.walks), Path(args.extensions), record)
        if window is None:
            continue
        loaded[name] = window
        result["panel_sha256"] = window.doc["panel_sha256"]
        result["walk_files"][name] = {"sha256": window.ext["walk_sha256"], "refits": window.ext["walk_refits"]}
    if "development" not in loaded:
        raise SystemExit("the development walk is required")
    cells, info = build_cells(loaded)
    result["outside_cells_checked_identical"] = info["outside_cells_checked_identical"]
    for name, window in loaded.items():
        mine = [c for c in cells if c["window"] == name]
        days = sorted({c["d"] for c in mine})
        entry = {"cells": len(mine), "decision_days": len(days), "arm_cells_changed": sum(1 for c in mine if c["inside"]),
                 "arm_group_cells": {g: sum(1 for c in mine if g in c["groups"]) for g in ARM_GROUPS},
                 "factors": factor_summary(info["factors"], days), "splits": split_rows(mine)}
        if name == "development":
            entry["pooled"] = pooled(mine)
            entry["pooled_reading"] = verdict_of(entry["pooled"]["grid_crps"]["pairs"]["arm_vs_candidate"])
            entry["figures_all"] = figures(mine)
        else:
            entry["pooled_point"] = {"arm_vs_candidate_crps": sum(c["vec"][0] for c in mine) / len(mine), "arm_vs_candidate_tw": sum(c["vec"][4] for c in mine) / len(mine)}
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


def page(r: Mapping[str, object]) -> str:
    dev = r["windows"]["development"]
    L: List[str] = []
    w = L.append
    w("# A per-tail scale by calendar flag, fitted walk-forward (#1555)")
    w("")
    w("**Development, not a verdict.** H5, step 4 (avenue #1546). The arm does not change the frozen candidate (s3c-ann-net); it is in `not_arms` of the H5 registration manifest until Eleonora rules. "
      "No lockbox day, no re-score of a published record, nothing registered or published. Every figure is read from `docs/research/calendar-flag-scale-arm-1555/result.json`; the declaration is "
      "`metadata/calendar_flag_scale_arm_1555.json`, committed before any score. The forecasts are #1533's walk extension, regenerated bit-identical from the 1363 walk (no refit).")
    w("")
    w("## The arm")
    w("")
    w("On a target day in an arm group, the candidate's quantiles on a side of the median are scaled about q50 by that side's factor. Groups and tails: `dom_19_23` q05 and q95, `coupon_settlement` q95, "
      "`post_month_end_window` q95, days with no calendar flag and no pressure-day type q95. Each factor is fitted at each decision day from the group's cells whose target day is strictly before it "
      f"(#1533's ratio at that tail on the raw quantiles), shrunk as `m = 1 + n/(n + {r['k']}) (ratio - 1)`, and 1 with fewer than {r['min_train']} usable training cells. A day in several groups takes the geometric mean "
      "of its flags' factors on each side. Quarter-end days (the flag, or the types quarter_end_turn and year_end) are in no group and keep the candidate's forecast, and their cells are not training cells. "
      "The sizes come from the walk, not from #1547's point values. Every other forecast is the candidate's, the same numbers"
      f" ({r['outside_cells_checked_identical']} cells outside the arm groups were checked equal). The arm trains on no fitter of its own: it reads the candidate's cells, so it is not a producer for the provisional register.")
    w("")
    w("The factors the walk gave (the first decision day of each year, and the last of the window):")
    w("")
    rows = []
    for name, v in dev["factors"].items():
        years = ", ".join(f"{y}: {m:.2f}" for y, m in v["first_of_year"].items())
        rows.append([name, years, f"{v['last']:.2f}", f"{v['min']:.2f} to {v['max']:.2f}"])
    L += table(["group, tail", "first decision day of each year", "last day", "range"], rows)
    w("")
    pc, pt = dev["pooled"]["grid_crps"]["pairs"]["arm_vs_candidate"], dev["pooled"]["twcrps"]["pairs"]["arm_vs_candidate"]
    flag_rows = {k: v for k, v in dev["splits"]["by_flag"].items() if k in ARM_GROUPS}
    w("## Reading")
    w("")
    w(f"Pooled over the development window the arm's grid CRPS is {pc[0]:+.3f} [{pc[1]:+.3f}, {pc[2]:+.3f}] against the candidate and its upper-tail twCRPS {pt[0]:+.3f} [{pt[1]:+.3f}, {pt[2]:+.3f}] "
      f"(positive favours the arm): by the declared rule the pooled reading is: {dev['pooled_reading']}. By flag, grid CRPS against the candidate: "
      + "; ".join(f"{k} {v['d_cand_crps'][0]:+.3f} [{v['d_cand_crps'][1]:+.3f}, {v['d_cand_crps'][2]:+.3f}]" for k, v in flag_rows.items()) + ".")
    w("")
    w("## Pooled, on scoring protocol v1's studentized stationary bootstrap")
    w("")
    w("One score per decision day (the mean over h = 1 to 5), development window. d = reference score - arm score: positive favours the arm. Two-sided 90% intervals read from the studentized draws of "
      f"`paired_tests` (mean block 10, {r['draws']} draws, HAC lag 10, seed {r['seed']}). The candidate against each benchmark is on the same days and resamples.")
    w("")
    for metric, title in (("grid_crps", "Grid CRPS (primary)"), ("twcrps", "Upper-tail twCRPS (key secondary)")):
        p = dev["pooled"][metric]
        w(f"### {title}")
        w("")
        w(f"Mean over {p['days']} decision days: arm {p['arm_mean']:.3f}, candidate {p['candidate_mean']:.3f}.")
        w("")
        rows = [["arm", iv(p["pairs"]["arm_vs_candidate"]), iv(p["pairs"]["arm_vs_B1"]), iv(p["pairs"]["arm_vs_B1_prime"]), iv(p["pairs"]["arm_vs_B2"])],
                ["candidate (unchanged)", "-", iv(p["pairs"]["candidate_vs_B1"]), iv(p["pairs"]["candidate_vs_B1_prime"]), iv(p["pairs"]["candidate_vs_B2"])]]
        L += table(["", "vs candidate", "vs B1", "vs B1'", "vs B2"], rows)
        w("")
    w(f"**Pooled reading by the declared rule: {dev['pooled_reading']}** (loses when the pooled grid-CRPS difference candidate - arm is not above 0, wins when its 90% interval lies wholly above 0). "
      "The rule is marked as a question in the pull request.")
    w("")
    w("## Splits")
    w("")
    w("Each row's cells, the share of them the arm changed, and the paired differences (reference - arm, positive favours the arm) with 90% intervals from the stationary bootstrap of the row's target days "
      "(mean block 10, 1000 resamples, seed 1555). Flag rows overlap.")
    w("")
    for split, title in (("by_regime", "regime"), ("by_flag", "calendar flag of the target day"), ("by_pressure", "pressure-day type of the target"), ("by_lead", "lead")):
        w(f"### By {title}")
        w("")
        for metric, keys, mtitle in (("crps", ("d_cand_crps", "d_B1_crps", "d_B1_prime_crps", "d_B2_crps"), "grid CRPS"), ("tw", ("d_cand_tw", "d_B1_tw", "d_B1_prime_tw", "d_B2_tw"), "upper-tail twCRPS")):
            w(f"{mtitle}:")
            w("")
            rows = []
            for key, v in dev["splits"][split].items():
                if "note" in v:
                    rows.append([key, str(v["cells"])] + ["too few"] * 5)
                else:
                    rows.append([key, str(v["cells"]), f"{v['changed']:.2f}"] + [iv(v[k]) for k in keys])
            L += table([title, "cells", "share changed", "vs candidate", "vs B1", "vs B1'", "vs B2"], rows)
            w("")
    w("## Coverage of the 90% band, per tail and per flag, before and after")
    w("")
    w("Strict share of cells below q05 and above q95 (nominal 0.05 each), the candidate and the arm, with 90% intervals as above.")
    w("")
    for split, title in (("by_flag", "calendar flag"), ("by_regime", "regime")):
        rows = []
        for key, v in dev["splits"][split].items():
            if "note" in v:
                continue
            cov_c = 1.0 - v["cand_miss_low"][0] - v["cand_miss_up"][0]
            cov_a = 1.0 - v["arm_miss_low"][0] - v["arm_miss_up"][0]
            rows.append([key, str(v["cells"]), rate(v["cand_miss_low"]), rate(v["arm_miss_low"]), rate(v["cand_miss_up"]), rate(v["arm_miss_up"]), f"{cov_c:.3f}", f"{cov_a:.3f}"])
        L += table([title, "cells", "below q05, candidate", "below q05, arm", "above q95, candidate", "above q95, arm", "band, candidate", "band, arm"], rows)
        w("")
    w("## The 2026 days (shown apart, decide nothing)")
    w("")
    later = r["windows"].get("2026")
    if later:
        w(f"Pooled point values, arm against candidate (positive favours the arm): grid CRPS {later['pooled_point']['arm_vs_candidate_crps']:+.3f}, upper-tail twCRPS {later['pooled_point']['arm_vs_candidate_tw']:+.3f}; "
          f"{later['arm_cells_changed']} of {later['cells']} cells changed.")
        w("")
        rows = []
        for key, v in later["splits"]["by_flag"].items():
            if "note" in v:
                rows.append([key, str(v["cells"]), "too few", "too few", "too few", "too few"])
            else:
                rows.append([key, str(v["cells"]), f"{v['d_cand_crps'][0]:+.3f}", f"{v['d_cand_tw'][0]:+.3f}",
                             f"{v['cand_miss_low'][0]:.3f} to {v['arm_miss_low'][0]:.3f}", f"{v['cand_miss_up'][0]:.3f} to {v['arm_miss_up'][0]:.3f}"])
        L += table(["flag", "cells", "CRPS, candidate - arm", "twCRPS, candidate - arm", "below q05, candidate to arm", "above q95, candidate to arm"], rows)
        w("")
    w("## What this does and does not show")
    w("")
    w("- It is development evidence on days already seen. The flags and tails were chosen from the whole development window by #1547, so the arm is scored on the sample that selected it; the figures flatter it.")
    w("- The sizes are walk-forward and as-of, but shrinkage k = 500 cells and the 100-cell minimum, the geometric-mean overlap rule and the quarter-end exclusion are this study's choices, marked as questions in the pull request. No other value was run.")
    w("- S13 (partially pooled day-type shapes) is untested; this arm does not settle it. #1402's S2 was a symmetric, unshrunk scale for every pressure-day type; this arm is one tail at a time, by calendar flag, shrunk, and leaves the other flags unchanged. Q3 and the quarter-end studies (#1531, #1548) are different questions.")
    w("- No verdict: only prospective confirmation days give one. The 2026 days are shown apart and decide nothing.")
    w("")
    w("## Reproduction")
    w("")
    w("See the header of `scripts/calendar_flag_scale_arm_1555.py`; the test is `tests/test_calendar_flag_scale_arm_1555.py`. Seed 1555 throughout.")
    w("")
    return "\n".join(L)


def page_command(args) -> int:
    r = json.loads(Path(args.score).read_text(encoding="utf-8"))
    Path(args.output).write_text(page(r), encoding="utf-8")
    return 0


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="command", required=True)
    s = sub.add_parser("score", help="the arm and its figures from the walk files and their extensions")
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
