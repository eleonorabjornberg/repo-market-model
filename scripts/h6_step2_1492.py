#!/usr/bin/env python3
"""H6 development step 2, re-run on the mean-d bound (#1492): #724's measurement with the fallback for undefined rows, every row read on mean(d).

A development measurement, never a verdict (scoring protocol v1, #640). Nothing is published, no locked day and no day after 2025-12-31 is scored. It replaces
nothing: `scripts/h6_step2_724.py`, `metadata/h6_step2_724.json`, `docs/research/h6-step2-724/result.json` and its page are not edited. Declared in
`metadata/h6_step2_1492.json`, which `run` refuses to read unless it is committed and unchanged.

Eleonora's ruling of 6 November 2026 (option 1, on #1492): re-run H6 step 2 with the fallback for undefined rows, read every row on the mean-d bound (#1009), show
both intervals and the HAC caveat (#1215), publish as a new result, and say which of the disagreeing rows change reading.

The run is #724's `run_command` unchanged (the candidate's walk, the strata, the variant, the benchmarks, seed, draws, block and lag), with two things replaced:

* the paired test keeps the mean-d bound where skill is undefined (#1215), and where a resample has no long-run variance reads the bound with those resamples
  dropped and counted (#1239), as `spread_mr_variants_761.run_pairs` does, with #1131's event block and lag;
* the reading is the lower end of the studentized 90% interval on mean(d), `d = S(benchmark) - S(model)`, not the skill interval.

A row #724 defined is recomputed on the same pair and must equal it; the run refuses to write otherwise.

    PYTHONPATH=src python3 -m repo_model.cli build --raw-root tests/fixtures/snapshots/funding_inputs --output PUB.csv \\
        --build-cutoff 2026-09-08T21:31:42+00:00 --decision-time 18:00:00
    RMM_DECISION_TIME=18:00 PYTHONPATH=src python3 scripts/capped_baselines_b2star_1434.py walk --panel PUB.csv --window development --output WALK/development.json
    RMM_DECISION_TIME=18:00 PYTHONPATH=src python3 scripts/h6_step2_1492.py run --published PUB.csv --walk WALK/development.json
    python3 scripts/h6_step2_1492.py report
    python3 scripts/h6_step2_1492.py check
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import random
import subprocess
import sys
from pathlib import Path
from typing import Callable, Dict, List, Mapping, Optional, Sequence, Tuple

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))

from repo_model import scoring_protocol as sp  # noqa: E402

DECLARATION = REPO / "metadata" / "h6_step2_1492.json"
RECORD = REPO / "docs" / "research" / "h6-step2-1492" / "result.json"
PAGE = REPO / "docs" / "research" / "h6-step2-1492-result.md"
RECORD_724 = REPO / "docs" / "research" / "h6-step2-724" / "result.json"
SCRIPT_724 = REPO / "scripts" / "h6_step2_724.py"

_STATE: Dict = {}


def _load(name: str):
    spec = importlib.util.spec_from_file_location(f"{name}_in_1492", REPO / "scripts" / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[f"{name}_in_1492"] = module
    spec.loader.exec_module(module)
    return module


def _base():
    if "base" not in _STATE:
        _STATE["base"] = _load("h6_step2_724")
    return _STATE["base"]


def _s761():
    if "s761" not in _STATE:
        _STATE["s761"] = _load("spread_mr_variants_761")
    return _STATE["s761"]


SEED = 724
DRAWS = 10_000
EVENT_BLOCK = 3.0
EVENT_LAG = 3
MINIMUM_EVENTS = 30
METRICS = ("grid_crps", "upper_tail_twcrps")
METRIC_TITLES = {"grid_crps": "grid CRPS (primary)", "upper_tail_twcrps": "upper-tail twCRPS (key secondary)"}
MODELS = ("candidate", "variant", "reference")
MODEL_TITLES = {"candidate": "(s3c-ann-net)", "variant": "risk-date variant", "reference": "spread_mr_ctx"}
BENCHMARKS = ("B1", "B1_prime", "B2", "calendar", "B2star_cap", "B1p_star_cap")
BENCH_TITLES = {"B1": "B1", "B1_prime": "B1'", "B2": "B2", "calendar": "risk-date calendar (#693)", "B2star_cap": "B2*-cap", "B1p_star_cap": "B1'*-cap"}
PRIMARY_SET = "union_without_bill"
UNION = "union"
STRATUM_TEXT = {
    "coupon_settlement": "coupon settlement", "bill_settlement_large": "large bill settlement", "month_end_turn": "month-end turn",
    "quarter_end_turn": "quarter-end turn (Mar, Jun, Sep)", "year_end": "year-end", "quarter_and_year_end": "quarter-end and year-end",
    "tax_date": "tax date", "fomc_meeting": "FOMC meeting day", "post_fomc_window": "IORB-change window (two days after a meeting)",
    UNION: "union of the strata", PRIMARY_SET: "union without the bill stratum (primary)",
}

#: Why the HAC standard error that studentizes the bound is not to be trusted at face value (Lens C, #958; her ruling of 20 October 2026 on #1009).
HAC_CAVEAT = ("the HAC standard error that studentizes the bound is understated about 2x after 2020 (Lens C, #958; measured for the daily lag-10 series, "
              "not for this page's event series at lag 3), so an interval that excludes zero is narrower than it should be. A reading here is evidence for a question")


# -- the paired test with the fallback -----------------------------------------------------------------------------------------


def _mean_d_alone(pair, draws: int) -> sp.PairedTest:
    """The paired test with skill left out: the mean-d bound alone (#1215), on #724's seed, block and lag."""

    (test,) = sp.paired_tests([pair], seed=SEED, draws=draws, block_length=EVENT_BLOCK, hac_lag=EVENT_LAG, with_skill=False, inner_draws=0)
    return test



def mean_d_dropping_row(pair: Tuple[Mapping, Mapping], reason: str, seed: int, draws: int, block_length: float, hac_lag: int) -> dict:
    """`spread_mr_variants_761.mean_d_dropping_row` (#1239) with the block and lag as arguments: the bound with no-variance resamples dropped and counted.

    Raises:
        sp.ProtocolError: the series has no long-run variance, too few days, or every resample has none.
    """

    s761 = _s761()
    benchmark, candidate = pair
    days = sorted(benchmark)
    n = len(days)
    if n <= hac_lag:
        raise sp.ProtocolError(f"{n} days cannot carry a lag-{hac_lag} long-run variance")
    bench = [benchmark[d] for d in days]
    diff = [b - candidate[d] for b, d in zip(bench, days)]
    mean = sum(diff) / n
    variance = sp._long_run_variance(diff, hac_lag)
    if variance <= 0.0:
        raise sp.ProtocolError("the daily difference has no long-run variance; it cannot be studentized")
    se = (variance / n) ** 0.5
    rng = random.Random(seed)
    kept: List[float] = []
    for _ in range(draws):
        resample = [diff[i] for i in s761.stationary_bootstrap_indices(n, block_length, rng)]
        resampled_variance = sp._long_run_variance(resample, hac_lag)
        if resampled_variance > 0.0:
            kept.append((sum(resample) / n - mean) / (resampled_variance / n) ** 0.5)
    if not kept:
        raise sp.ProtocolError(f"every one of the {draws} resamples has no long-run variance; it cannot be studentized")
    statistic = mean / se
    return {
        "days": n, "benchmark_mean": sum(bench) / n, "candidate_mean": sum(candidate[d] for d in days) / n, "difference": mean,
        "difference_interval": s761.studentized_interval(mean, se, sorted(kept)), "skill": None, "skill_interval": None, "skill_undefined": reason,
        "dm_statistic": statistic, "dm_p_value": 1.0 - sp._NORMAL.cdf(statistic), "dropped_resamples": draws - len(kept), "draws": draws,
    }


def paired(bench: Mapping, cand: Mapping, events: Sequence, draws: int = DRAWS) -> dict:
    """#724's paired row, and where skill is undefined the mean-d bound alone (#1215, #1239) instead of `undefined`.

    A row that #724 could test is the same call and the same row. Thin (fewer than 30 events) and identical series are left as #724 left them.
    """

    s761 = _s761()
    n = len(events)
    if n < MINIMUM_EVENTS:
        return {"events": n, "thin": True}
    if all(bench[e] == cand[e] for e in events):
        return {"events": n, "identical": True}
    pair = ({e: bench[e] for e in events}, {e: cand[e] for e in events})
    try:
        (test,) = sp.paired_tests([pair], seed=SEED, draws=draws, block_length=EVENT_BLOCK, hac_lag=EVENT_LAG)
        return {**s761.paired_row(test), "events": n}
    except sp.ProtocolError as error:
        reason = str(error)
    try:
        test = _mean_d_alone(pair, draws)
        return {**s761.mean_d_row(test, reason), "events": n}
    except sp.ProtocolError:
        pass
    try:
        return {**mean_d_dropping_row(pair, reason, SEED, draws, EVENT_BLOCK, EVENT_LAG), "events": n}
    except sp.ProtocolError as why:
        return {"undefined": str(why), "events": n}


# -- the reading, on the mean-d bound ---------------------------------------------------------------------------------------


def has_bound(row: Optional[Mapping[str, object]]) -> bool:
    return bool(row) and not row.get("thin") and not row.get("identical") and "undefined" not in row and row.get("difference_interval") is not None


def lower_end(row: Optional[Mapping[str, object]]) -> Optional[float]:
    """The lower end of the mean-d interval (the one-sided 95% bound), the end every reading is taken from (#1009); `None` for a row with no bound."""

    if not has_bound(row):
        return None
    return row["difference_interval"][0]


def skill_lower_end(row: Optional[Mapping[str, object]]) -> Optional[float]:
    """The lower end of the skill interval, which #724 read; `None` where skill is undefined or the row has no bound."""

    if not has_bound(row) or row.get("skill_interval") is None:
        return None
    return row["skill_interval"][0]


def row_reading(row: Optional[Mapping[str, object]]) -> str:
    """`gain` if the mean-d lower end is above zero, `loss` if the upper end is below zero, `undecided` otherwise, `no reading` without a bound."""

    if not has_bound(row):
        return "no reading"
    lo, hi = row["difference_interval"]
    return "gain" if lo > 0.0 else ("loss" if hi < 0.0 else "undecided")


def kill_reading(row_b1: Mapping[str, object], row_b2: Mapping[str, object], lower: Callable = lower_end) -> str:
    """The development reading of the kill rule: skill only if the lower end is above zero against B1 and against B2."""

    lowers = (lower(row_b1), lower(row_b2))
    if any(x is None for x in lowers):
        return "undefined"
    return "skill" if all(x > 0.0 for x in lowers) else "no skill shown"


def variant_adds(row: Mapping[str, object], lower: Callable = lower_end) -> bool:
    """The variant adds skill over the candidate if the lower end of the interval against the candidate is above zero."""

    x = lower(row)
    return x is not None and x > 0.0


def readings(record: Mapping[str, object], set_scope: str, lower: Callable = lower_end) -> Dict[str, object]:
    """The kill and variant readings of `record` on one scope, the lower end taken by `lower`."""

    rows = record["rows"][set_scope]
    grid, tail = rows["grid_crps"], rows["upper_tail_twcrps"]
    return {
        "kill_rule_candidate": kill_reading(grid["candidate"]["B1"], grid["candidate"]["B2"], lower),
        "kill_rule_variant": kill_reading(grid["variant"]["B1"], grid["variant"]["B2"], lower),
        "variant_adds_grid_crps": variant_adds(grid["variant"]["candidate"], lower),
        "variant_adds_twcrps": variant_adds(tail["variant"]["candidate"], lower),
    }


# -- the comparison with #724's record -------------------------------------------------------------------------------------


def _walk(record: Mapping[str, object]):
    for scope, by_metric in record["rows"].items():
        for metric, by_model in by_metric.items():
            for model, by_bench in by_model.items():
                for bench, row in by_bench.items():
                    yield [scope, metric, model, bench], row


def _differs(old_row: Mapping[str, object], new_row: Optional[Mapping[str, object]]) -> bool:
    """Whether `new_row` is not `old_row`: every key of the old row is in the new one and equal (floats within 1e-12)."""

    if new_row is None:
        return True
    for key, value in old_row.items():
        if key not in new_row:
            return True
        other = new_row[key]
        if isinstance(value, (list, tuple)):
            if len(value) != len(other) or any(abs(a - b) > 1e-12 for a, b in zip(value, other)):
                return True
        elif isinstance(value, float):
            if not isinstance(other, (int, float)) or abs(value - other) > 1e-12:
                return True
        elif value != other:
            return True
    return False


def require_defined_rows_reproduce(old: Mapping[str, object], new: Mapping[str, object]) -> None:
    """Every row #724 could compute (a bound, thin or identical) is recomputed unchanged; only its `undefined` rows may differ.

    Raises:
        ValueError: a row moved, or is missing, or is undefined now.
    """

    for key, old_row in _walk(old):
        if "undefined" in old_row:
            continue
        scope, metric, model, bench = key
        new_row = new["rows"].get(scope, {}).get(metric, {}).get(model, {}).get(bench)
        if _differs(old_row, new_row):
            raise ValueError(f"the row {'/'.join(key)} is not what #724 recorded")


def _feeds_reading(key: Sequence[str]) -> bool:
    """Whether the row is one a stated reading is taken from: the kill rule on a union, a regime or a pressure-day type, and the variant rule."""

    scope, metric, model, bench = key
    split = not scope.startswith("set/")
    if scope == f"set/{PRIMARY_SET}":
        return (metric == "grid_crps" and model in ("candidate", "variant") and bench in ("B1", "B2")) or (model == "variant" and bench == "candidate")
    return split and metric == "grid_crps" and model == "candidate" and bench in ("B1", "B2")


def compare(old: Mapping[str, object], new: Mapping[str, object]) -> Dict[str, object]:
    """#724's record against this one: rows whose two lower ends fall on opposite sides of zero, rows #724 left undefined that now have a bound."""

    disagree: List[dict] = []
    newly: List[dict] = []
    still: List[dict] = []
    both = 0
    for key, old_row in _walk(old):
        new_row = new["rows"][key[0]][key[1]][key[2]][key[3]]
        if "undefined" in old_row:
            entry = {"key": key, "events": new_row.get("events"), "reading": row_reading(new_row), "feeds_reading": _feeds_reading(key)}
            if has_bound(new_row):
                newly.append({**entry, "difference": new_row["difference"], "difference_interval": new_row["difference_interval"],
                              "skill_undefined": new_row.get("skill_undefined"), "dropped_resamples": new_row.get("dropped_resamples", 0)})
            else:
                still.append({**entry, "why": new_row.get("undefined")})
            continue
        s_lo, d_lo = skill_lower_end(old_row), lower_end(new_row)
        if s_lo is None or d_lo is None:
            continue
        both += 1
        if (s_lo > 0.0) != (d_lo > 0.0):
            disagree.append({
                "key": key, "events": new_row.get("events"), "skill": old_row["skill"], "skill_interval": old_row["skill_interval"],
                "difference": new_row["difference"], "difference_interval": new_row["difference_interval"], "skill_lower": s_lo, "mean_d_lower": d_lo,
                "skill_reading": "gain" if s_lo > 0.0 else "not shown", "mean_d_reading": row_reading(new_row),
                "direction": "gains on the mean-d bound" if d_lo > 0.0 else "loses on the mean-d bound", "feeds_reading": _feeds_reading(key)})
    return {"disagree": disagree, "newly_defined": newly, "still_undefined": still,
            "counts": {"rows_with_both_intervals": both, "disagree": len(disagree), "disagree_feeding_a_reading": sum(1 for x in disagree if x["feeds_reading"]),
                       "newly_defined": len(newly), "newly_defined_feeding_a_reading": sum(1 for x in newly if x["feeds_reading"]),
                       "still_undefined": len(still)}}


def reading_scopes(record: Mapping[str, object]) -> List[str]:
    return [f"set/{PRIMARY_SET}"] + sorted(s for s in record["scopes"] if not s.startswith("set/"))


# -- the run ---------------------------------------------------------------------------------------------------------------


def committed_declaration(path: Path = DECLARATION) -> dict:
    """The declaration, refused unless it is committed and unchanged since `HEAD`."""

    relative = str(path.resolve().relative_to(REPO))
    dirty = subprocess.run(["git", "status", "--porcelain", "--", relative], cwd=REPO, capture_output=True, text=True, check=True).stdout.strip()
    if dirty:
        raise SystemExit(f"{relative} is not committed ({dirty}); a declaration is made before any score")
    return json.loads(path.read_text(encoding="utf-8"))


def run_command(args) -> int:
    declaration = committed_declaration()
    base = _base()
    old = json.loads(RECORD_724.read_text(encoding="utf-8"))
    # #724's run, its own code, with the paired test replaced and the record written here (the pool forks after these are set)
    base.DECLARATION, base.RECORD = DECLARATION, RECORD
    base.committed_declaration = lambda *a, **k: declaration
    base.paired = paired
    base.run_command(args)
    new = json.loads(RECORD.read_text(encoding="utf-8"))
    require_defined_rows_reproduce(old, new)
    for key in ("panel_sha256", "walk_panel_sha256", "seed", "draws", "event_block", "event_lag", "history", "strata", "variant_scales", "scopes"):
        if old[key] != new[key]:
            raise ValueError(f"{key} differs from #724's record; this is not the same measurement")
    new["declaration_724_sha256"] = base.sha256(SCRIPT_724.parents[1] / "metadata" / "h6_step2_724.json")
    new["record_724_sha256"] = base.sha256(RECORD_724)
    new["reading_724_skill_interval"] = {s: readings(old, s, skill_lower_end) for s in reading_scopes(old)}
    new["reading"] = {s: readings(new, s) for s in reading_scopes(new)}
    new["comparison"] = compare(old, new)
    RECORD.write_text(json.dumps(new, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    print(f"wrote {RECORD}: {new['comparison']['counts']}")
    return 0


# -- the page --------------------------------------------------------------------------------------------------------------


def pct(x: Optional[float]) -> str:
    return "n/a" if x is None else format(100.0 * x, "+.1f") + "%"


def skill_part(row: Mapping[str, object]) -> str:
    if row.get("skill_interval") is None:
        return "skill undefined"
    lo, hi = row["skill_interval"]
    return f"{pct(row['skill'])} [{pct(lo)}, {pct(hi)}]"


def diff_part(row: Mapping[str, object]) -> str:
    lo, hi = row["difference_interval"]
    return f"d {row['difference']:+.3f} [{lo:+.3f}, {hi:+.3f}]"


def cell_text(row: Optional[Mapping[str, object]]) -> str:
    """Both intervals, and the reading taken from the mean-d bound."""

    if row is None:
        return "n/a"
    if row.get("thin"):
        return f"thin ({row['events']})"
    if row.get("identical"):
        return "identical"
    if "undefined" in row:
        return "no bound (undefined)"
    return f"{skill_part(row)}; {diff_part(row)}; **{row_reading(row)}**"


def _title(scope: str) -> str:
    kind, label = scope.split("/", 1)
    return STRATUM_TEXT.get(label, label) if kind == "set" else label


def _key_text(key: Sequence[str]) -> str:
    scope, metric, model, bench = key
    return f"{_title(scope)}, {METRIC_TITLES[metric].split(' (')[0]}, {MODEL_TITLES[model]} vs {BENCH_TITLES.get(bench, MODEL_TITLES.get(bench, bench))}"


def skill_table(r: Mapping[str, object], metric: str, scopes: Sequence[str], benches: Sequence[str]) -> List[str]:
    lines = ["| stratum | benchmark | events | " + " | ".join(MODEL_TITLES[m] for m in MODELS) + " |", "|---|---|---|---|---|---|"]
    for scope in scopes:
        for bench in benches:
            cells = [r["rows"][scope][metric][m][bench] for m in MODELS]
            lines.append(f"| {_title(scope)} | {BENCH_TITLES[bench]} | {cells[0].get('events', 0)} | " + " | ".join(cell_text(c) for c in cells) + " |")
    return lines


def variant_table(r: Mapping[str, object], scopes: Sequence[str]) -> List[str]:
    lines = ["| cut | events | grid CRPS: variant over (s3c-ann-net) | upper-tail twCRPS: variant over (s3c-ann-net) |", "|---|---|---|---|"]
    for scope in scopes:
        g = r["rows"][scope]["grid_crps"]["variant"]["candidate"]
        t = r["rows"][scope]["upper_tail_twcrps"]["variant"]["candidate"]
        lines.append(f"| {_title(scope)} | {g.get('events', 0)} | {cell_text(g)} | {cell_text(t)} |")
    return lines


def render(r: Mapping[str, object]) -> str:
    set_scopes = [f"set/{name}" for name in (PRIMARY_SET, UNION) + tuple(n for n in STRATUM_TEXT if n not in (UNION, PRIMARY_SET))]
    split_scopes = sorted(s for s in r["scopes"] if not s.startswith("set/"))
    regimes = [s for s in split_scopes if s.startswith("regime/")]
    types = [s for s in split_scopes if s.startswith("pressure_day_type/")]
    h = r["history"]
    prim = r["rows"][f"set/{PRIMARY_SET}"]
    now = r["reading"][f"set/{PRIMARY_SET}"]
    was = r["reading_724_skill_interval"][f"set/{PRIMARY_SET}"]
    cmp = r["comparison"]
    n = cmp["counts"]
    out: List[str] = []
    out += ["# H6 development step 2, re-run on the mean-d bound (#1492)", ""]
    out += ["**This page is new.** It does not replace or edit `docs/research/h6-step2-724-result.md` (#724), which reads every row on the skill interval and is kept as "
            "the record of what was run. Where a reading here differs from it, section 2 says so.", ""]
    out += [f"**Hypothesis and step:** H6 (the spread on known risk dates is forecastable), development step 2, re-run under Eleonora's ruling of 6 November 2026 "
            f"(option 1, #1492). **Development data, not a verdict** (scoring protocol v1, #640): the days were seen before, no confirmation day is scored, nothing is "
            f"published and no locked day or day after 2025-12-31 is read. Script `scripts/h6_step2_1492.py`, declared in `metadata/h6_step2_1492.json` before any score; "
            f"every figure below is read from `docs/research/h6-step2-1492/result.json`. Made at the {r['instant']} decision instant on the published panel "
            f"(`{r['panel_sha256'][:12]}...`). H6 step 3 waits on this page.", ""]
    out += ["## 1. What changed against #724", "",
            "Everything is #724's: the candidate (s3c-ann-net) and its walk, the strata, the one declared variant, the benchmarks, the target days "
            f"({h['target_days']} from {h['first_target']} to {h['last_target']}), seed {r['seed']}, {r['draws']} draws, block {r['event_block']:.0f} events, HAC lag "
            f"{r['event_lag']}, two-sided 90% studentized stationary bootstrap. The run recomputes every row #724 could compute and refuses to write unless it is "
            "unchanged; only the rows #724 left `undefined` can differ. Two things changed:", "",
            "- **The fallback (#1215, #1239).** A row whose skill is undefined (the benchmark scores zero on a resample) keeps its mean-d bound, instead of reading "
            "`undefined`. Where a resample has no long-run variance the bound is read with those resamples dropped and counted, as `spread_mr_variants_761.run_pairs` does.",
            "- **The reading (#1009).** Every reading is taken from the lower end of the studentized 90% interval on mean(d), `d = S(benchmark) - S(model)`, positive "
            "favouring the model, so its lower end is the one-sided 95% bound. A row reads `gain` if that lower end is above zero, `loss` if the upper end is below zero, "
            "`undecided` otherwise. Skill and its interval are shown beside it; d is in bp.", "",
            f"**Caveat (Lens C, #958; #1215):** {HAC_CAVEAT}.", ""]
    out += ["## 2. The readings, and which of them move", "",
            "Kill rule, as #724 declared it in words: (s3c-ann-net) shows skill on the union without the bill stratum if the lower end is above zero against B1 and against B2 "
            "both. #724 took the lower end from the skill interval; here it is the mean-d lower end. Development readings, not verdicts.", "",
            "| cut | #724 (skill interval): candidate | now (mean-d bound): candidate | #724: variant | now: variant | #724: variant adds, grid / twCRPS | now: variant adds, grid / twCRPS |",
            "|---|---|---|---|---|---|---|"]
    for scope in reading_scopes(r):
        a, b = r["reading_724_skill_interval"][scope], r["reading"][scope]
        moved = a != b
        out.append(f"| {_title(scope)}{' **(moves)**' if moved else ''} | {a['kill_rule_candidate']} | {b['kill_rule_candidate']} | {a['kill_rule_variant']} | {b['kill_rule_variant']} | "
                   f"{'yes' if a['variant_adds_grid_crps'] else 'no'} / {'yes' if a['variant_adds_twcrps'] else 'no'} | "
                   f"{'yes' if b['variant_adds_grid_crps'] else 'no'} / {'yes' if b['variant_adds_twcrps'] else 'no'} |")
    out += ["", f"On the union without the bill stratum the candidate's grid CRPS skill against B1 is {skill_part(prim['grid_crps']['candidate']['B1'])} with "
            f"{diff_part(prim['grid_crps']['candidate']['B1'])} bp, and against B2 {skill_part(prim['grid_crps']['candidate']['B2'])} with "
            f"{diff_part(prim['grid_crps']['candidate']['B2'])} bp: the reading is **{now['kill_rule_candidate']}** (#724: {was['kill_rule_candidate']}). "
            f"B1' ({cell_text(prim['grid_crps']['candidate']['B1_prime'])}) and B2*-cap ({cell_text(prim['grid_crps']['candidate']['B2star_cap'])}) do not decide. "
            f"The variant against the candidate: grid CRPS {cell_text(prim['grid_crps']['variant']['candidate'])}; twCRPS {cell_text(prim['upper_tail_twcrps']['variant']['candidate'])}.", ""]
    out += ["## 3. The rows that change reading", "",
            "Every row #724 defined whose skill-interval lower end and mean-d lower end fall on opposite sides of zero. Under a lower-bound reading each one reads differently "
            "on the mean-d bound than on the skill interval; the column `feeds a reading` marks those a stated reading in section 2 is taken from (the kill rule on the "
            "union without the bill stratum, on a regime or a pressure-day type, and the variant rule). Skill and mean d are #724's own figures for the row.", "",
            "| row | events | skill (#724) | mean d (bp) | #724 reading | now | feeds a reading |", "|---|---|---|---|---|---|---|"]
    for x in cmp["disagree"]:
        lo, hi = x["skill_interval"]
        dlo, dhi = x["difference_interval"]
        out.append(f"| {_key_text(x['key'])} | {x['events']} | {pct(x['skill'])} [{pct(lo)}, {pct(hi)}] | {x['difference']:+.3f} [{dlo:+.3f}, {dhi:+.3f}] | "
                   f"{x['skill_reading']} | {x['mean_d_reading']} ({x['direction']}) | {'yes' if x['feeds_reading'] else 'no'} |")
    out += ["", "## 4. The rows that have a bound now", "",
            "#724 left these `undefined`: the benchmark scores zero on some resample, so skill has no interval. The mean-d bound is computed (#1215) and the row is read on it. "
            "A row that stays without a bound says why.", "",
            "| row | events | mean d (bp) | reading | feeds a reading | resamples dropped |", "|---|---|---|---|---|---|"]
    for x in cmp["newly_defined"]:
        dlo, dhi = x["difference_interval"]
        out.append(f"| {_key_text(x['key'])} | {x['events']} | {x['difference']:+.3f} [{dlo:+.3f}, {dhi:+.3f}] | {x['reading']} | {'yes' if x['feeds_reading'] else 'no'} | "
                   f"{x['dropped_resamples']} |")
    if cmp["still_undefined"]:
        out += ["", "Still without a bound:", "", "| row | events | why |", "|---|---|---|"]
        out += [f"| {_key_text(x['key'])} | {x['events']} | {x['why']} |" for x in cmp["still_undefined"]]
    out += [""]
    out += ["## 5. The strata", "",
            "| stratum | events | per year | by calendar year | " + " | ".join(BENCH_TITLES[b] for b in BENCHMARKS) + " |", "|---|---|---|---|" + "---|" * len(BENCHMARKS)]
    for name in [s[4:] for s in set_scopes]:
        s = r["strata"][name]
        by_year = ", ".join(f"{y}: {k}" for y, k in s["by_year"].items())
        out.append(f"| {STRATUM_TEXT[name]}{' (thin)' if s['thin'] else ''} | {s['n']} | {s['per_year']:.1f} | {by_year} | " + " | ".join(str(s["covered"][b]) for b in BENCHMARKS) + " |")
    out += ["", "Columns after the year split: events each benchmark covers. The calendar benchmark exists only on a day typed as one of its four risk types at all five leads.", ""]
    for metric in METRICS:
        out += [f"## 6. Skill by stratum: {METRIC_TITLES[metric]}", "",
                "Each cell: skill with its 90% interval; mean d (bp) with its 90% interval; the reading, from the mean-d lower end. Development data, not a verdict.", ""]
        out += skill_table(r, metric, set_scopes, BENCHMARKS) + [""]
    out += ["## 7. The variant against (s3c-ann-net)", "", "Paired on the same events, same bootstrap; positive favours the variant. d is in bp.", ""]
    out += variant_table(r, set_scopes) + [""]
    out += ["## 8. By regime and by pressure-day type (the union without the bill stratum)", "",
            "The pressure-day-type rows bootstrap each group's own days, as #724 did; they are not the studentized domain interval she ruled for H5 day-type rows (#1454). "
            "Whether that ruling also covers H6 pages is for her; this page does not change it (question in the pull request).", ""]
    for title, scopes in (("Regime", regimes), ("Pressure-day type", types)):
        out += [f"### {title}: grid CRPS", ""]
        out += skill_table(r, "grid_crps", scopes, ("B1", "B1_prime", "B2", "B2star_cap")) + [""]
        out += [f"### {title}: the variant against (s3c-ann-net)", ""] + variant_table(r, scopes) + [""]
    out += ["## 9. What the variant did", "", "| label | cells | cells with k not 1 | geometric mean k | cells by k |", "|---|---|---|---|---|"]
    for label, s in sorted(r["variant_scales"].items()):
        out.append(f"| {label} | {s['cells']} | {s['moved']} | {s['geometric_mean_k']:.3f} | " + ", ".join(f"{k}: {c}" for k, c in sorted(s["by_k"].items(), key=lambda kv: float(kv[0]))) + " |")
    out += ["", "A label is the cell's first stratum in the declared order; `none` is a cell in no stratum, which keeps k = 1. Unchanged from #724.", ""]
    out += ["## What this shows, and does not", "",
            "- It shows how the frozen candidate and the declared variant read on #1131's event-day strata on 2020-2025 development days when every row, including the rows "
            "#724 could not bound, is read on the mean-d bound. Nothing about the scores moved: the rows #724 defined are the same rows.",
            f"- It does not show skill on any confirmation day, does not change the candidate and sets no rule. The bound carries the caveat above ({HAC_CAVEAT}).",
            "- The strata overlap and the days within a stratum are dependent; the intervals use #1131's block of 3 events. The reported cuts carry no multiplicity correction "
            "(default 7). One variant was declared and scored.",
            "- Not changed: the pressure-day-type rows still bootstrap their own days (above); the calendar-benchmark cover; the 2026 days (#1394's confirmation, not this step).", ""]
    verdict = "adds skill" if now["variant_adds_grid_crps"] else "adds no skill that this data can show"
    g, t = prim["grid_crps"]["variant"]["candidate"], prim["upper_tail_twcrps"]["variant"]["candidate"]
    out.append(f"**Does the specialised variant add skill over (s3c-ann-net) on the union (without the bill stratum), read on the mean-d bound? It {verdict} on grid CRPS: "
               f"{cell_text(g)} over {g.get('events', 0)} events (twCRPS {cell_text(t)}). Development data, not a verdict.**")
    return "\n".join(out) + "\n"


def report_command(args) -> int:
    PAGE.write_text(render(json.loads(RECORD.read_text(encoding="utf-8"))), encoding="utf-8")
    return 0


def check_command(args) -> int:
    expected = render(json.loads(RECORD.read_text(encoding="utf-8")))
    if PAGE.read_text(encoding="utf-8") != expected:
        print(f"{PAGE} is not what {RECORD} gives; run `report`", file=sys.stderr)
        return 1
    print("ok")
    return 0


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="command", required=True)
    run = sub.add_parser("run", help="re-run #724's measurement with the mean-d fallback and write the record")
    run.add_argument("--published", required=True)
    run.add_argument("--walk", required=True)
    run.add_argument("--workers", type=int, default=4)
    sub.add_parser("report", help="write the page from the record")
    sub.add_parser("check", help="fail if the page is not what the record gives")
    args = parser.parse_args(argv)
    return {"run": run_command, "report": report_command, "check": check_command}[args.command](args)


if __name__ == "__main__":
    raise SystemExit(main())
