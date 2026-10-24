"""The equal-weight quantile average of `spread_mr_ctx` and `gbm_funding_cal_aligned`, scored against both parts and the benchmarks (#1123, H5 step 3; avenue #1113).

A development measurement, never a claim and never a verdict (scoring protocol v1, #46). It is a development arm, not a candidate change: under
Eleonora's ruling of 22 October 2026 `gbm_funding` stays the H5 candidate until #1115 reports. It writes JSON and Markdown to the paths it is given and
nothing into `docs/runs/`, registers nothing and changes no rule, no published model and no published figure. Every choice is in
`metadata/quantile_average_1113.json`, which `score` refuses to read unless it is committed and unchanged; `declare` writes it from the constants below
and was run, and its output committed, before any number was computed. No day after 2025-12-31 and no day of a locked tier is read
(`docs/decisions/lockbox.md`).

**The arm.** For each decision day and lead, the forecast is the 0.5 / 0.5 average of the two parts' 23-level laws, level by level, then sorted (the average
of two monotone laws is monotone, so the sort changes nothing unless a part is out of order; it is there so a crossing is never scored). The parts are
`spread_mr_ctx` (#761: stdlib, computed here from the published panel, no walk) and `gbm_funding_cal_aligned` (#1027: its five walks are Eleonora's, in
`~/rmm-1027/WALKS`). A lead a gbm walk does not carry stands in as B1, as #634 and #1027 fill it, so the average is of the forecasts as each part is scored.

**Scored** under protocol v1 against both parts, `gbm_funding` (#634's walks), B1, B1' (#960, reported beside B1, Eleonora 22 October 2026) and B2: grid
CRPS over h = 1 to 5 and upper-tail twCRPS, the studentized stationary bootstrap at the protocol's block 10 with the Politis-White block of each pair's
own loss differential beside it, pooled, by the five regimes (target day) and by target day type (quarter-end, month-end, tax date, settlement, ordinary).
The 95th-percentile exceedance of every model is reported under both hit rules ("above", y > q, and "at_or_above", y >= q: the rule is an open question of
Eleonora's, and she asked for both on 22 October 2026).

The walks are long (`needs-mac`, #46); `score` reads them. Stdlib apart from what #1027's script loads.

    # PUB.csv, AUG3.csv, WALKS/ (gbm_funding_h1..5, gbm_funding_cal_aligned_h1..5): Eleonora's ~/rmm-1027, built as the docstring of
    # scripts/aligned_calendar_1027.py says
    PYTHONPATH=src python3 scripts/quantile_average_1113.py declare            # then commit metadata/quantile_average_1113.json before any score
    PYTHONPATH=src python3 scripts/quantile_average_1113.py score --published PUB.csv --panel AUG3.csv --walks WALKS \\
        --output OUT/score.json --markdown OUT/report.md
    PYTHONPATH=src python3 scripts/quantile_average_1113.py report OUT/score.json --output OUT/report.md
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import math
import multiprocessing
import sys
from datetime import date
from pathlib import Path
from typing import Dict, List, Mapping, Optional, Sequence, Tuple

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))


def _load(name: str):
    spec = importlib.util.spec_from_file_location(f"{name}_script", REPO / "scripts" / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[f"{name}_script"] = module
    spec.loader.exec_module(module)
    return module


from repo_model import coverage_tests, scoring_protocol as sp  # noqa: E402
from repo_model.baseline import panel_sha256  # noqa: E402
from repo_model.data import audit_panel, load_daily_panel  # noqa: E402
from repo_model.evaluation_splits import load_split_declaration  # noqa: E402

a1027 = _load("aligned_calendar_1027")
b960 = _load("b1_calendar_960")
s761 = b960.s761
s686 = b960.s686

DECLARATION = REPO / "metadata" / "quantile_average_1113.json"
SEED = 1123
LAST_TARGET = a1027.LAST_TARGET
HORIZONS = sp.HORIZONS
GRID = sp.GRID
MIN_GROUP_DAYS = s686.MIN_GROUP_DAYS
ORDER_REGIME = a1027.ORDER_REGIME
CALENDAR_TYPES = a1027.CALENDAR_TYPES
PROTOCOL_BLOCK = sp.BLOCK_LENGTH

CTX = "spread_mr_ctx"
ALIGNED = a1027.ALIGNED
CONTROL = a1027.CONTROL
B1P = "B1_prime"
AVG = "quantile_average"
#: the parts' weights, in the order of PARTS
PARTS = (CTX, ALIGNED)
WEIGHTS = (0.5, 0.5)
#: every model scored, in table order; B1' sits beside B1
MODELS = ("B1", B1P, "B2", CTX, CONTROL, ALIGNED, AVG)
#: what the average is tested against, parts first
COMPARATORS = (CTX, ALIGNED, CONTROL, "B1", B1P, "B2")
PAIRS = tuple((AVG, comparator) for comparator in COMPARATORS)
METRICS = a1027.METRICS
HIT_RULES = coverage_tests.HIT_RULES
EXCEED_LEVEL = 0.95
LEVEL_95 = GRID.index(EXCEED_LEVEL)
NOMINAL = 0.05
#: outcomes and quantiles are whole basis points carrying float noise (5.000000000000004), so a tie is decided at this many decimals
TIE_DECIMALS = 9


# -- the declaration and the guards ----------------------------------------------------------------------------------


def committed_declaration(path: Path = DECLARATION) -> dict:
    """The declaration, refused unless it is committed and unchanged since `HEAD`."""

    return a1027.committed_declaration(path)


def require_study_window(days: Sequence[date]) -> None:
    """Refuse a run that would read a day after 2025-12-31: raises `LookAheadError` (#1027's guard)."""

    a1027.require_study_window(days)


# -- the average -----------------------------------------------------------------------------------------------------


def sort_levels(levels: Sequence[float]) -> List[float]:
    return sorted(levels)


def average_laws(first: Sequence[float], second: Sequence[float], weights: Tuple[float, float] = WEIGHTS) -> List[float]:
    """The `weights`-mean of two 23-level laws, level by level, sorted.

    Raises:
        ValueError: a law that is not `len(GRID)` levels long, or holds a value that is not finite.
    """

    for name, law in (("first", first), ("second", second)):
        if len(law) != len(GRID):
            raise ValueError(f"the {name} law has {len(law)} levels, not the {len(GRID)} of the grid")
        if not all(math.isfinite(v) for v in law):
            raise ValueError(f"the {name} law holds a value that is not finite")
    mixed = [weights[0] * a + weights[1] * b for a, b in zip(first, second)]
    return sorted(mixed)


def average_forecasts(first: Mapping[date, Mapping[int, Sequence[float]]], second: Mapping[date, Mapping[int, Sequence[float]]]) -> Dict[date, Dict[int, List[float]]]:
    """The average of two forecast sets on the decision days both carry (`forecasts[day][lead]` a 23-level law).

    Raises:
        ValueError: a day on which the two carry different leads, or a law `average_laws` refuses.
    """

    out: Dict[date, Dict[int, List[float]]] = {}
    for day in sorted(set(first) & set(second)):
        if set(first[day]) != set(second[day]):
            raise ValueError(f"{day}: the parts carry leads {sorted(first[day])} and {sorted(second[day])}")
        out[day] = {h: average_laws(first[day][h], second[day][h]) for h in sorted(first[day])}
    return out


# -- the exceedance and the block --------------------------------------------------------------------------------------


def hits(outcomes: Sequence[float], laws: Sequence[Sequence[float]], *, rule: str) -> List[int]:
    """0/1: the outcome is beyond the law's 95th percentile, by `rule` ("above": y > q; "at_or_above": y >= q; no default).

    Both sides are rounded at `TIE_DECIMALS` first, so a whole-basis-point tie carrying float noise is a tie.
    """

    return coverage_tests.hit_sequence(
        [round(float(y), TIE_DECIMALS) for y in outcomes], [round(float(law[LEVEL_95]), TIE_DECIMALS) for law in laws], rule=rule
    )


def politis_white_block(values: Sequence[float]) -> Optional[float]:
    """The Politis-White automatic mean block of `values` (#949's function), at least 1, or None where it is not defined."""

    try:
        block = _load("block_length_949").politis_white(list(values))
    except (ValueError, ZeroDivisionError):
        return None
    return max(1.0, block) if math.isfinite(block) else None


def paired_at(benchmark: Mapping[date, float], candidate: Mapping[date, float], days: Sequence[date], block: float, draws: int) -> dict:
    """One paired test at mean block `block` (`s761.paired_row`), or an undefined row saying why."""

    pair = ({d: benchmark[d] for d in days}, {d: candidate[d] for d in days})
    try:
        return s761.paired_row(sp.paired_tests([pair], seed=SEED, draws=draws, block_length=block)[0])
    except sp.ProtocolError as error:
        return {"undefined": str(error), "days": len(days), "benchmark_mean": sum(benchmark[d] for d in days) / len(days),
                "candidate_mean": sum(candidate[d] for d in days) / len(days)}


def rate_row(share: Mapping[date, float], days: Sequence[date], draws: int) -> dict:
    """The mean of `share` over `days` against the nominal 0.05, with the studentized interval of its mean (None where undefined)."""

    rate = sum(share[d] for d in days) / len(days)
    out = {"rate": rate, "nominal": NOMINAL, "interval": None}
    try:
        test = sp.paired_tests([({d: NOMINAL for d in days}, {d: share[d] for d in days})], seed=SEED, draws=draws, with_skill=False)[0]
    except sp.ProtocolError:
        return out
    low, high = s761.studentized_interval(test.mean_difference, test.standard_error, test.t_draws)
    out["interval"] = [NOMINAL - high, NOMINAL - low]
    return out


# -- the tests, in parallel ----------------------------------------------------------------------------------------------

_SERIES: Dict = {}


def _pair_task(job):
    key, metric, candidate, benchmark, days = job
    series = _SERIES[(key[0], metric)]
    draws = _SERIES["draws"]
    ordered = sorted(days)
    block = politis_white_block([series[benchmark][d] - series[candidate][d] for d in ordered])
    cell = {"block_10": paired_at(series[benchmark], series[candidate], ordered, PROTOCOL_BLOCK, draws), "politis_white_block": block}
    if block is None:
        cell["block_politis_white"] = {"undefined": "no automatic block is defined for this series", "days": len(ordered)}
    else:
        cell["block_politis_white"] = paired_at(series[benchmark], series[candidate], ordered, block, draws)
    return key, metric, candidate, benchmark, cell


def _exceed_task(job):
    key, model, rule, days = job
    return key, model, rule, rate_row(_SERIES[("exceed", rule)][key[0]][model], sorted(days), _SERIES["draws"])


def _run(function, jobs, workers):
    if workers <= 1:
        return [function(job) for job in jobs]
    with multiprocessing.get_context("fork").Pool(workers) as pool:
        return pool.map(function, jobs, chunksize=1)


# -- the scoring -----------------------------------------------------------------------------------------------------------


def build_groups(frame) -> Dict[Tuple[str, str], Tuple[str, List[date]]]:
    """Each cut: (split, label) -> (grain, days). Pooled is by decision day; the others are by target day."""

    days = frame.days
    targets = sorted({frame.target(d, h) for d in days for h in HORIZONS})
    labels = {"regime": {t: frame.regime(t) for t in targets}, "target_type": {t: a1027.target_type(frame, t) for t in targets}}
    groups: Dict[Tuple[str, str], Tuple[str, List[date]]] = {("pooled", "all decision days"): ("decision", list(days))}
    for split, mapping in labels.items():
        by_label: Dict[str, List[date]] = {}
        for day in sorted(mapping):
            by_label.setdefault(mapping[day], []).append(day)
        for label, members in by_label.items():
            groups[(split, label)] = ("target", members)
    groups[("target_type", "calendar_days")] = ("target", [t for t in targets if labels["target_type"][t] in CALENDAR_TYPES])
    return groups


def compute_result(frame, *, draws: int, workers: int) -> dict:
    """Score every pair and every model's exceedance on `frame` (its `forecasts` hold all of `MODELS`, on `frame.days`)."""

    days = list(frame.days)
    models = [m for m in MODELS if m in frame.forecasts]
    if AVG not in models:
        raise ValueError("the frame holds no quantile average to score")
    cells = {(label, m): s686.cell_scores(frame, m, fn) for label, fn in METRICS for m in models}
    series: Dict = {}
    for label, _ in METRICS:
        series[("decision", label)] = {m: s686.by_decision(cells[(label, m)]) for m in models}
        series[("target", label)] = {m: s686.by_target(frame, cells[(label, m)]) for m in models}
    exceed_cells = {}
    for rule in HIT_RULES:
        def fn(quantiles, outcome, rule=rule):
            return float(hits([outcome], [quantiles], rule=rule)[0])
        exceed_cells[rule] = {m: s686.cell_scores(frame, m, fn) for m in models}
        series[("exceed", rule)] = {
            "decision": {m: s686.by_decision(exceed_cells[rule][m]) for m in models},
            "target": {m: s686.by_target(frame, exceed_cells[rule][m]) for m in models},
        }
    groups = build_groups(frame)
    jobs, exceed_jobs, skipped = [], [], {}
    for (split, label), (grain, members) in groups.items():
        if len(members) < MIN_GROUP_DAYS:
            skipped[f"{split}/{label}"] = len(members)
            continue
        for metric, _ in METRICS:
            for candidate, benchmark in PAIRS:
                jobs.append(((grain, f"{split}/{label}"), metric, candidate, benchmark, tuple(members)))
        for rule in HIT_RULES:
            for m in models:
                exceed_jobs.append(((grain, f"{split}/{label}"), m, rule, tuple(members)))
    _SERIES.update(series)
    _SERIES["draws"] = draws
    out = _run(_pair_task, jobs, workers)
    exceed_out = _run(_exceed_task, exceed_jobs, workers)

    result: dict = {
        "issue": 1123, "label": "development, not a verdict", "seed": SEED, "draws": draws, "models": models,
        "pairs": [list(p) for p in PAIRS],
        "means": {label: {m: sum(series[("decision", label)][m].values()) / len(days) for m in models} for label, _ in METRICS},
        "groups": {}, "skipped_groups": skipped, "exceedance": {},
    }
    for (grain, name), metric, candidate, benchmark, cell in out:
        split, label = name.split("/", 1)
        members = groups[(split, label)][1]
        entry = result["groups"].setdefault(split, {}).setdefault(label, {"days": len(members), "metrics": {}})
        ser = series[(grain, metric)]
        entry["metrics"].setdefault(metric, {"means": {m: sum(ser[m][d] for d in members) / len(members) for m in models}, "pairs": {}})
        entry["metrics"][metric]["pairs"][f"{candidate} vs {benchmark}"] = cell
    for (grain, name), model, rule, row in exceed_out:
        split, label = name.split("/", 1)
        members = groups[(split, label)][1]
        if grain == "decision":
            count = len(members) * len(HORIZONS)
        else:
            wanted = set(members)
            count = sum(1 for d in days for h in HORIZONS if frame.target(d, h) in wanted)
        result["exceedance"].setdefault(split, {}).setdefault(label, {}).setdefault(model, {})[rule] = dict(row, cells=count)
    return result


def reading_rules(rows: Mapping[str, Optional[dict]]) -> List[str]:
    """The declared sentences, from the paired rows (block 10) named in the declaration; a missing or undefined row is said, not read.

    `rows`: vs_ctx and vs_aligned (pooled grid CRPS over each part), calendar_vs_control and ordinary_vs_control (over `gbm_funding` on calendar days and
    on ordinary target days), vs_b1 and vs_b1_prime (pooled, reported with no rule). The lower end of a studentized two-sided 90% interval is the
    one-sided 95% lower bound.
    """

    out = []
    for key, part in (("vs_ctx", CTX), ("vs_aligned", ALIGNED)):
        cell = rows.get(key)
        if cell is None:
            out.append(f"Against {part}: not read (the cut is not scored).")
        elif "undefined" in cell:
            out.append(f"Against {part}: undefined ({cell['undefined']}).")
        else:
            beats = cell["skill_interval"][0] > 0.0
            out.append(
                f"The average {'beats' if beats else 'is not shown to beat'} {part} on the pooled grid CRPS (skill {s761.pct(cell['skill'])}, "
                f"one-sided 95% lower bound {s761.pct(cell['skill_interval'][0])})."
            )
    out += a1027.reading_rules({AVG: {"calendar": rows.get("calendar_vs_control"), "ordinary": rows.get("ordinary_vs_control")}})
    pieces = []
    for key, name in (("vs_b1", "B1"), ("vs_b1_prime", "B1'")):
        cell = rows.get(key)
        if cell is None:
            pieces.append(f"over {name}: not read")
        elif "undefined" in cell:
            pieces.append(f"over {name}: undefined")
        else:
            pieces.append(f"over {name} is {s761.pct(cell['skill'])} (one-sided 95% lower bound {s761.pct(cell['skill_interval'][0])})")
    out.append("Pooled grid-CRPS skill " + ", ".join(pieces) + "; no rule is applied to either.")
    return out


# -- the declaration ------------------------------------------------------------------------------------------------------


def declaration_document() -> dict:
    return {
        "status": "declared by the pull request that closes #1123 before any number was computed; a measurement, not a record. Development arm, not a candidate change: gbm_funding stays the H5 candidate until #1115 reports (Eleonora, 22 October 2026). Nothing is published, no day after 2025-12-31 is scored (docs/decisions/lockbox.md), no rule changes, the live record and pin do not move. Development data gives no verdict (scoring protocol v1, #46).",
        "issue": 1123,
        "avenue": 1113,
        "hypothesis": "H5 step 3 (a development arm)",
        "ruling": "Eleonora, 22 October 2026, relayed by the orchestrating session: queue them now (avenue #1113)",
        "arm": {
            "name": AVG,
            "parts": list(PARTS),
            "weights": dict(zip(PARTS, WEIGHTS)),
            "combination": "the weighted mean of the two parts' 23-level laws, level by level on the protocol grid, at every lead h = 1 to 5, then sorted so the result stays monotone",
            "parts_as_scored": "each part is the forecast as the other scores read it: spread_mr_ctx from scripts/spread_mr_variants_761.py on the published panel, gbm_funding_cal_aligned from #1027's walks, a lead a walk does not carry standing in as B1 (#634, #1027)",
            "decision_days": "the days on which every scored model has a forecast at all five leads and whose fifth target is on or before 2025-12-31",
        },
        "benchmarks": [CTX, ALIGNED, CONTROL, "B1", B1P, "B2"],
        "b1_prime": "reported beside B1 on every table (Eleonora, 22 October 2026, #46); B1 stays the protocol's benchmark",
        "metrics": ["grid_crps", "upper_tail_twcrps"],
        "cuts": {
            "pooled": "all scored decision days",
            "regimes": ORDER_REGIME,
            "target_day_types": ["quarter_end", "month_end", "tax_date", "settlement", "ordinary"],
            "settlement": "a target day whose reporting day type is ordinary and whose treasury_settlement_coupons or treasury_settlement_bills is above 0",
            "calendar_days": "the union of quarter_end, month_end, tax_date and settlement target days",
            "minimum_days": f"a cut of fewer than {MIN_GROUP_DAYS} days is listed and not tested",
        },
        "bootstrap": {
            "kind": "stationary bootstrap, studentized (ruling 1, #739), seed 1123; the lower end of the two-sided 90% interval is the one-sided 95% lower bound",
            "blocks": {"protocol": PROTOCOL_BLOCK, "politis_white": "the automatic block of the pair's own loss differential, at least 1"},
            "politis_white": "scripts/block_length_949.py politis_white (Politis and White 2004 with the correction of Patton, Politis and White 2009); the protocol's block 10 is not changed (Eleonora, 22 October 2026: keep 10, report the Politis-White block beside it)",
        },
        "exceedance": {
            "level": EXCEED_LEVEL,
            "nominal": NOMINAL,
            "hit_rules": list(HIT_RULES),
            "rule_note": "the hit rule (y > q or y >= q) is an open question of Eleonora's; both are reported and neither is chosen here (Eleonora, 22 October 2026). Outcome and quantile are compared after rounding to 9 decimals, so a whole-basis-point tie that carries float noise is a tie",
            "models": list(MODELS),
            "reading": "the share of cells (decision day, lead) whose outcome is beyond the model's 95th percentile, with the studentized interval of the daily share's mean against the nominal 0.05; no rule is attached",
        },
        "caveat": "Lens C of #958: the lag-10 standard error behind the block length is itself noisy on this many days; every interval here is read with that in mind",
        "reading_rules": {
            "beats_a_part": "the average beats a part when the lower end of its pooled grid-CRPS skill interval over that part (block 10) is above 0",
            "reads_calendar_days_and_beats": "the average beats gbm_funding on calendar days when the lower end of its grid-CRPS skill interval over gbm_funding on the calendar_days cut is above 0",
            "without_losing_on_ordinary_days": "and its skill over gbm_funding on ordinary target days has an upper interval end of 0 or more; 'loses' means an interval wholly below 0",
            "b1_and_b1_prime": "pooled skill over B1 and over B1' is reported with its one-sided 95% lower bound; no rule is applied",
            "replacement": "replacing the candidate is hers, and waits for #1115; this page does not decide it",
            "no_verdict": "development data gives no verdict",
        },
        "limits": ["no day after 2025-12-31", "no lockbox day", "no published record is edited", "gbm_funding's declaration and scripts/final_test_preregistration.py are not changed", "no walk is made by this script: the parts' walks are #634's and #1027's"],
    }


def declare_command(args) -> int:
    DECLARATION.write_text(json.dumps(declaration_document(), indent=1, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"written": str(DECLARATION.relative_to(REPO))}))
    return 0


# -- the run -----------------------------------------------------------------------------------------------------------------


def score_command(args) -> int:
    declaration = committed_declaration()
    published, panel_path, walks = Path(args.published), Path(args.panel), Path(args.walks)
    require_study_window([LAST_TARGET])
    pub = load_daily_panel(published)
    audit_panel(pub)
    splits = load_split_declaration(s761.SPLITS)
    registry = json.loads(s761.SOURCES.read_text(encoding="utf-8"))
    missing = [f"{name}_h{h}.json" for name in (CONTROL, ALIGNED) for h in HORIZONS if not (walks / f"{name}_h{h}.json").is_file()]
    if missing:
        raise SystemExit(f"walks missing from {walks}: {', '.join(missing)}; both gbm_funding and {ALIGNED} must be walked at every lead")
    frame, notes = b960.build_frame(pub, panel_sha256(published), splits, registry, s761.committed_declaration(b960.DECLARATION), walks)
    frame.forecasts[ALIGNED] = a1027.load_walks(walks, ALIGNED, published, panel_path, frame)
    days = [d for d in frame.days if all(d in frame.forecasts[m] for m in (m for m in MODELS if m != AVG))]
    frame.days = days
    for name in list(frame.forecasts):
        frame.forecasts[name] = {d: frame.forecasts[name][d] for d in days}
    frame.forecasts[AVG] = average_forecasts(frame.forecasts[CTX], frame.forecasts[ALIGNED])
    if sorted(frame.forecasts[AVG]) != sorted(days):
        raise ValueError("the average does not cover the scored decision days")
    notes["scored_decision_days"] = len(days)
    result = compute_result(frame, draws=args.draws, workers=args.workers)

    def pick(split, label, metric, comparator):
        cell = result["groups"].get(split, {}).get(label, {}).get("metrics", {}).get(metric, {}).get("pairs", {}).get(f"{AVG} vs {comparator}")
        return None if cell is None else cell["block_10"]

    result.update({
        "declaration": str(DECLARATION.relative_to(REPO)), "panel_sha256": panel_sha256(published), "scratch_panel_sha256": panel_sha256(panel_path),
        "notes": notes, "declared_reading_rules": declaration["reading_rules"], "not_run": {},
    })
    pooled = ("pooled", "all decision days", "grid_crps")
    result["reading_rules"] = reading_rules({
        "vs_ctx": pick(*pooled, CTX), "vs_aligned": pick(*pooled, ALIGNED), "vs_b1": pick(*pooled, "B1"), "vs_b1_prime": pick(*pooled, B1P),
        "calendar_vs_control": pick("target_type", "calendar_days", "grid_crps", CONTROL),
        "ordinary_vs_control": pick("target_type", "ordinary", "grid_crps", CONTROL),
    })
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    Path(args.output).write_text(json.dumps(result, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    if args.markdown:
        Path(args.markdown).parent.mkdir(parents=True, exist_ok=True)
        Path(args.markdown).write_text(render_report(result), encoding="utf-8")
    return 0


def report_command(args) -> int:
    result = json.loads(Path(args.result).read_text(encoding="utf-8"))
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    Path(args.output).write_text(render_report(result), encoding="utf-8")
    return 0


# -- Markdown ----------------------------------------------------------------------------------------------------------------

METRIC_TITLES = a1027.METRIC_TITLES
SPLIT_TITLES = {"pooled": "pooled (decision days)", "regime": "regime (target day)", "target_type": "target day type"}


def _order(split: str, labels) -> List[str]:
    if split == "regime":
        return [l for l in ORDER_REGIME if l in labels] + [l for l in labels if l not in ORDER_REGIME]
    return sorted(labels, key=lambda l: (l != "ordinary", l))


def _pct(value: Optional[float]) -> str:
    return "n/a" if value is None else format(100.0 * value, ".1f") + "%"


def render_report(r: dict) -> str:
    n = r["notes"]
    pairs = [f"{c} vs {b}" for c, b in r["pairs"]]
    heads = " | ".join(f"over {b}" for _, b in r["pairs"])
    lines = [
        "# The quantile average of spread_mr_ctx and gbm_funding_cal_aligned (#1123): development data, not a verdict", "",
        f"Published panel `{r['panel_sha256']}`, scratch panel `{r['scratch_panel_sha256']}`. Declaration `{r['declaration']}`. Seed {r['seed']}, {r['draws']} draws, "
        f"the studentized stationary bootstrap. {n['scored_decision_days']} decision days, every pair on the same days. The average is the 0.5 / 0.5 mean of the two "
        "parts' 23-level laws, level by level, sorted. Skill = mean(d) / mean(S(benchmark)); positive favours the average. Intervals: two-sided 90% (the lower end is "
        "the one-sided 95% lower bound). Lens C's caveat applies: the lag-10 standard error behind the block length is noisy on this many days. "
        "`gbm_funding` stays the H5 candidate until #1115 reports.", "",
        "## Mean scores, pooled", "", "| model | " + " | ".join(METRIC_TITLES[m] for m in r["means"]) + " |", "|---|" + "---|" * len(r["means"])]
    for m in r["models"]:
        lines.append(f"| {m} | " + " | ".join(f"{r['means'][label][m]:.4f}" for label in r["means"]) + " |")
    lines += ["", "## Reading (declared rules)", ""] + [f"- {s}" for s in r["reading_rules"]]
    lines += ["", "Replacing the candidate is Eleonora's; this page does not decide it.", ""]
    for metric in METRIC_TITLES:
        lines += [f"## {METRIC_TITLES[metric]}", ""]
        for split in SPLIT_TITLES:
            if split not in r["groups"]:
                continue
            for key, title in (("block_10", "block 10 (the protocol)"), ("block_politis_white", "Politis-White block (beside it)")):
                lines += [f"### {SPLIT_TITLES[split]}, {title}", "", f"| group | days | {heads} |", "|---|---|" + "---|" * len(pairs)]
                for label in _order(split, r["groups"][split]):
                    entry = r["groups"][split][label]
                    cells = entry["metrics"].get(metric, {}).get("pairs", {})
                    texts = []
                    for p in pairs:
                        cell = cells.get(p)
                        if cell is None:
                            texts.append("n/a")
                        elif key == "block_politis_white" and cell.get("politis_white_block") is not None:
                            texts.append(f"{s761.skill_text(cell[key])} (b = {cell['politis_white_block']:.1f})")
                        else:
                            texts.append(s761.skill_text(cell[key]))
                    lines.append(f"| {label} | {entry['days']:,} | " + " | ".join(texts) + " |")
                lines.append("")
    lines += ["## The 95th-percentile exceedance, under both hit rules", "",
              "The share of cells (decision day, lead) whose outcome is beyond the model's 95th percentile; the nominal rate is 5.0%. "
              "\"above\" is y > q, \"at_or_above\" is y >= q (an open question of Eleonora's; both are shown, neither is chosen). Intervals: studentized, two-sided 90%.", ""]
    for split in SPLIT_TITLES:
        if split not in r.get("exceedance", {}):
            continue
        for rule in HIT_RULES:
            lines += [f"### {SPLIT_TITLES[split]}, {rule}", "", "| group | cells | " + " | ".join(r["models"]) + " |", "|---|---|" + "---|" * len(r["models"])]
            for label in _order(split, r["exceedance"][split]):
                by_model = r["exceedance"][split][label]
                first = by_model[r["models"][0]][rule]
                texts = []
                for m in r["models"]:
                    cell = by_model[m][rule]
                    texts.append(_pct(cell["rate"]) + ("" if cell["interval"] is None else f" [{_pct(cell['interval'][0])}, {_pct(cell['interval'][1])}]"))
                lines.append(f"| {label} | {first['cells']:,} | " + " | ".join(texts) + " |")
            lines.append("")
    if r["skipped_groups"]:
        lines += [f"Groups of fewer than {MIN_GROUP_DAYS} days, listed and not tested: " + ", ".join(f"{k} ({v})" for k, v in sorted(r["skipped_groups"].items())) + ".", ""]
    lines += ["Development data, not a verdict (scoring protocol v1).", ""]
    return "\n".join(lines) + "\n"


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("declare").set_defaults(run=declare_command)
    score = sub.add_parser("score")
    score.add_argument("--published", type=Path, required=True)
    score.add_argument("--panel", type=Path, required=True)
    score.add_argument("--walks", type=Path, required=True)
    score.add_argument("--output", type=Path, required=True)
    score.add_argument("--markdown", type=Path)
    score.add_argument("--draws", type=int, default=sp.DRAWS)
    score.add_argument("--workers", type=int, default=4)
    score.set_defaults(run=score_command)
    report = sub.add_parser("report")
    report.add_argument("result", type=Path)
    report.add_argument("--output", type=Path, required=True)
    report.set_defaults(run=report_command)
    args = parser.parse_args(argv)
    return args.run(args)


if __name__ == "__main__":
    raise SystemExit(main())
