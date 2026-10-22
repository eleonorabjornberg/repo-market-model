#!/usr/bin/env python3
"""The confirmation-design study (H1 step 2, #733): size and power of six declared designs.

The rule it follows is `docs/research/confirmation-design-733.md`, committed before this script produced any number.
Development data only: no day after 2025-12-31 (`STUDY_END`) is read, and nothing here is a verdict.

    PYTHONPATH=src python3 scripts/confirmation_design.py describe
    PYTHONPATH=src python3 scripts/confirmation_design.py run --out docs/research/confirmation-design-733 [--workers K]
    PYTHONPATH=src python3 scripts/confirmation_design.py report --out docs/research/confirmation-design-733
    PYTHONPATH=src python3 scripts/confirmation_design.py check --out docs/research/confirmation-design-733

`run` builds the published panel from the tracked fixtures, scores B1, B2 and B3 per lead on the development pool,
calibrates each design's critical values (the ruling of 13 October 2026, item 5, on the design's own pool), simulates
the null and the alternatives, and writes `result.json`. `report` writes the result page from `result.json` alone, so
no figure on the page is typed. `check` refuses a `result.json` made from another text of the rule. Standard library
only.
"""

from __future__ import annotations

import argparse
import contextlib
import hashlib
import io
import json
import math
import multiprocessing
import sys
import tempfile
from dataclasses import dataclass
from datetime import date, time
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Tuple

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))

from repo_model import protocol_benchmarks as pb  # noqa: E402
from repo_model import scoring_protocol as sp  # noqa: E402
from repo_model.cli import main as cli_main  # noqa: E402
from repo_model.confirmation_workers import (  # noqa: E402,F401  (the pooled workers live in src: a spawn pool imports them)
    CALIBRATION_SEED, LOOK_FRACTIONS, POST_2020_FIRST, Design, RuleError, Series, calibrate_design, candidate, checkpoints,
    history_slice, init_worker, pair_series, run_path, window_statistics,
)
from repo_model.data import load_daily_panel  # noqa: E402
from repo_model.evaluation_splits import load_split_declaration  # noqa: E402
from repo_model.splits import LookAheadError  # noqa: E402

RULE = REPO / "docs" / "research" / "confirmation-design-733.md"
PAGE = REPO / "docs" / "research" / "confirmation-design-733-result.md"
FIXTURES = REPO / "tests" / "fixtures" / "snapshots" / "funding_inputs"
REGISTRY = json.loads((REPO / "metadata" / "sources.json").read_text(encoding="utf-8"))
SPLITS = load_split_declaration(REPO / "metadata" / "evaluation_splits.json")
MANIFEST = REPO / "metadata" / "funding_panel_manifest.json"
CUTOFF = "2026-09-08T21:31:42+00:00"
DECISION = time(16, 0)

# The rule's constants (§2 to §6).
STUDY_END = date(2025, 12, 31)
FIRST_DECISION = date(2018, 6, 29)
SCALE_WINDOW = 60
SCALE_LAG = 6
WARMUP = SCALE_WINDOW + SCALE_LAG - 1
WINDOWS = 20_000
PATHS = 2_000
SEED = 733
SCENARIO_STRIDE = 1_000_003
DELTA = 0.03
TARGET_POWER = 0.80
MDE_GRID = (0.03, 0.05, 0.075, 0.10, 0.15, 0.20, 0.30)
SIZE_LIMIT = 0.05


DESIGNS = (
    Design("D0", 250, sp.HORIZONS, False),
    Design("D1", 375, sp.HORIZONS, False),
    Design("D2", 500, sp.HORIZONS, False),
    Design("D3", 250, (1,), False),
    Design("D4", 250, sp.HORIZONS, True),
    Design("D5", 375, sp.HORIZONS, True),
)


#: §6: scenario name, true skill, noise, history. The order fixes each scenario's seed.
SCENARIOS = (
    ("size, full", 0.0, 1.0, "full"),
    ("size, post-2020", 0.0, 1.0, "post-2020"),
    ("3%, full", 0.03, 1.0, "full"),
    ("3%, post-2020", 0.03, 1.0, "post-2020"),
    ("10%, full", 0.10, 1.0, "full"),
    ("10%, post-2020", 0.10, 1.0, "post-2020"),
    ("3%, full, noise 0.5", 0.03, 0.5, "full"),
    ("10%, full, noise 0.5", 0.10, 0.5, "full"),
    ("5%, full", 0.05, 1.0, "full"),
    ("7.5%, full", 0.075, 1.0, "full"),
    ("15%, full", 0.15, 1.0, "full"),
    ("20%, full", 0.20, 1.0, "full"),
    ("30%, full", 0.30, 1.0, "full"),
)


# -- the guard (§2) --------------------------------------------------------------------------------------------------


def require_study_window(days) -> None:
    """§2: the study reads no day after `STUDY_END`.

    Raises:
        LookAheadError: a day is later than `STUDY_END`.
    """

    late = sorted(day for day in days if day > STUDY_END)
    if late:
        raise LookAheadError(f"the confirmation-design study reads no day after {STUDY_END}; got {late[0]}")


# -- the development pool (§2) ---------------------------------------------------------------------------------------


def build_panel(directory: Path) -> Path:
    path = directory / "funding_panel.csv"
    with contextlib.redirect_stdout(io.StringIO()):
        code = cli_main(
            ["build", "--raw-root", str(FIXTURES), "--output", str(path),
             "--build-cutoff", CUTOFF, "--decision-time", "16:00:00"]
        )
        if code == 0:
            code = cli_main(["verify-panel", str(path), "--manifest", str(MANIFEST)])
    if code != 0:
        raise RuleError("the fixture panel did not build to the published digest")
    return path


@dataclass
class Pool:
    """Per decision day and per lead: B1's and B2's grid CRPS; and, on the days B3 covers, B1's and B3's five-level CRPS."""

    dates: List[date]
    s1: Dict[int, List[float]]
    s2: Dict[int, List[float]]
    dates3: List[date]
    f1: Dict[int, List[float]]
    f3: Dict[int, List[float]]


def decision_positions(rows) -> List[int]:
    """§2: the panel positions of the decision days: five targets, all on or before `STUDY_END`, all published."""

    out = []
    for t, row in enumerate(rows):
        if row.date < FIRST_DECISION or t + max(sp.HORIZONS) >= len(rows):
            continue
        if rows[t + max(sp.HORIZONS)].date > STUDY_END:
            continue
        if any(rows[t + h].spread_bps is None for h in sp.HORIZONS):
            continue
        out.append(t)
    return out


def build_pool(rows) -> Pool:
    positions = decision_positions(rows)
    require_study_window(rows[t + h].date for t in positions for h in sp.HORIZONS)
    settings = {"registry": REGISTRY, "decision_time": DECISION}
    decisions = [rows[t].date for t in positions]
    b1 = pb.forecasts(pb.b1_forecast, rows, decisions, **settings)
    b2 = pb.forecasts(pb.b2_forecast, rows, decisions, splits=SPLITS, **settings)
    s1 = {h: [] for h in sp.HORIZONS}
    s2 = {h: [] for h in sp.HORIZONS}
    for t in positions:
        for h in sp.HORIZONS:
            outcome = rows[t + h].spread_bps
            s1[h].append(sp.grid_crps(b1[rows[t].date][h], outcome))
            s2[h].append(sp.grid_crps(b2[rows[t].date][h], outcome))
    # B3: the published declaration's daily forecasts, dated by target day.
    calendar = [row.date for row in rows]
    position = {day: i for i, day in enumerate(calendar)}
    in_pool = {rows[t].date for t in positions}
    leads: Dict[date, Dict[int, List[float]]] = {}
    for h in sp.HORIZONS:
        record = json.loads((REPO / "docs" / "runs" / f"published_distribution_daily_h{h}.json").read_text())
        for entry in record["days"]:
            target = date.fromisoformat(entry["date"])
            if target > STUDY_END:
                continue
            decision = calendar[position[target] - h]
            leads.setdefault(decision, {})[h] = entry["quantiles_bps"]
    levels = pb.incumbent()["levels"]
    five = sp.level_crps(levels)
    dates3 = sorted(day for day, forecast in leads.items() if len(forecast) == len(sp.HORIZONS) and day in in_pool)
    b13 = pb.forecasts(pb.b1_forecast, rows, dates3, **settings)
    f1 = {h: [] for h in sp.HORIZONS}
    f3 = {h: [] for h in sp.HORIZONS}
    for day in dates3:
        t = position[day]
        forecast = pb.b3_forecast(levels, leads[day])
        for h in sp.HORIZONS:
            outcome = rows[t + h].spread_bps
            f1[h].append(five(sp.on_levels(b13[day][h], levels), outcome))
            f3[h].append(five(forecast[h], outcome))
    require_study_window(dates3)
    return Pool([rows[t].date for t in positions], s1, s2, dates3, f1, f3)


# -- the design's series (§3, §4) ------------------------------------------------------------------------------------


def trailing_scale(pooled_b1: Sequence[float]) -> List[Optional[float]]:
    """§4: `m_t`, the mean of B1's pooled score over the `SCALE_WINDOW` days ending `SCALE_LAG` positions before `t`.

    `None` for the first `WARMUP` days, which have no such window.
    """

    out: List[Optional[float]] = [None] * len(pooled_b1)
    for i in range(WARMUP, len(pooled_b1)):
        window = pooled_b1[i - WARMUP: i - SCALE_LAG + 1]
        out[i] = sum(window) / len(window)
    return out


def mean_over(values: Dict[int, List[float]], leads: Sequence[int]) -> List[float]:
    return [sum(values[h][i] for h in leads) / len(leads) for i in range(len(values[leads[0]]))]


def design_series(pool: Pool, design: Design) -> Series:
    b = mean_over(pool.s1, design.leads)
    e = [x - y for x, y in zip(b, mean_over(pool.s2, design.leads))]
    f1, f3 = mean_over(pool.f1, design.leads), mean_over(pool.f3, design.leads)
    e3 = [x - y for x, y in zip(f1, f3)]
    dates = list(pool.dates)
    dates3 = list(pool.dates3)
    if design.standardized:
        scale = trailing_scale(mean_over(pool.s1, sp.HORIZONS))
        by_date = dict(zip(pool.dates, scale))
        keep = [i for i, m in enumerate(scale) if m is not None]
        b, e, dates = [b[i] / scale[i] for i in keep], [e[i] / scale[i] for i in keep], [dates[i] for i in keep]
        keep3 = [i for i, day in enumerate(dates3) if by_date.get(day) is not None]
        e3 = [e3[i] / by_date[dates3[i]] for i in keep3]
        dates3 = [dates3[i] for i in keep3]
    return Series(dates, b, e, dates3, e3)


# -- the calibration (§5): `window_statistics`, `pair_series`, `calibrate_design` are in `repo_model.confirmation_workers` --


# -- the paths (§5, §6): `init_worker`, `history_slice`, `run_path` are there too ----------------------------------------

def simulate(pool_args, critical, *, paths, workers, generator="stationary", scenarios=None):
    histories, designs = pool_args
    out = {design.id: {} for design in designs}
    for s, (name, delta, noise, history) in enumerate(SCENARIOS):
        if scenarios is not None and name not in scenarios:
            continue
        for design in designs:
            jobs = [(design, history, delta, noise, SEED * 100_003 + s * SCENARIO_STRIDE + i, generator)
                    for i in range(paths)]
            if workers > 1:
                with multiprocessing.Pool(workers, initializer=init_worker, initargs=(histories, critical)) as pool:
                    results = pool.map(run_path, jobs, chunksize=max(1, paths // (workers * 8)))
            else:
                init_worker(histories, critical)
                results = [run_path(job) for job in jobs]
            out[design.id][name] = summarize(design, results, paths)
        print("scenario", name, flush=True)
    return out


def summarize(design: Design, results, paths: int) -> Dict[str, object]:
    def share(position, upto):
        return sum(1 for r in results if r[position] is not None and r[position] <= upto) / paths

    looks = design.checkpoints
    out = {"paths": paths}
    for label, position in (("without_the_mme_gate", 0), ("with_the_mme_gate", 1)):
        by_look = {str(n): share(position, n) for n in looks}
        out[label] = by_look
        last = by_look[str(looks[-1])]
        out[label + "_se"] = math.sqrt(last * (1 - last) / paths)
    detected = [r[1] for r in results if r[1] is not None]
    out["mean_days_to_detection"] = sum(detected) / len(detected) if detected else None
    return out


# -- the reading rule (§7) -------------------------------------------------------------------------------------------


def smallest_skill_at_target(design_id: str, scenarios) -> Optional[float]:
    names = {0.03: "3%, full", 0.05: "5%, full", 0.075: "7.5%, full", 0.10: "10%, full",
             0.15: "15%, full", 0.20: "20%, full", 0.30: "30%, full"}
    for delta in MDE_GRID:
        cell = scenarios[design_id][names[delta]]
        if cell["with_the_mme_gate"][str(DESIGN_BY_ID[design_id].days)] >= TARGET_POWER:
            return delta
    return None


DESIGN_BY_ID = {design.id: design for design in DESIGNS}


def reading(scenarios) -> Dict[str, object]:
    """§7: which designs are admissible, which one is recommended, and the trade-off against D0."""

    rows = {}
    for design in DESIGNS:
        last = str(design.days)
        cells = scenarios[design.id]
        size_full = cells["size, full"]["without_the_mme_gate"][last]
        size_post = cells["size, post-2020"]["without_the_mme_gate"][last]
        rows[design.id] = {
            "days": design.days,
            "size_full": size_full, "size_post_2020": size_post,
            "size_upper_95": max(
                size_full + 1.645 * cells["size, full"]["without_the_mme_gate_se"],
                size_post + 1.645 * cells["size, post-2020"]["without_the_mme_gate_se"],
            ),
            "admissible": size_full <= SIZE_LIMIT and size_post <= SIZE_LIMIT,
            "power_3": cells["3%, full"]["with_the_mme_gate"][last],
            "power_3_se": cells["3%, full"]["with_the_mme_gate_se"],
            "power_10": cells["10%, full"]["with_the_mme_gate"][last],
            "power_3_post_2020": cells["3%, post-2020"]["with_the_mme_gate"][last],
            "power_10_post_2020": cells["10%, post-2020"]["with_the_mme_gate"][last],
            "smallest_skill_at_80": smallest_skill_at_target(design.id, scenarios),
        }
    admissible = [d for d in DESIGNS if rows[d.id]["admissible"]]
    recommended = None
    if admissible:
        top = max(rows[d.id]["power_3"] for d in admissible)
        se = next(rows[d.id]["power_3_se"] for d in admissible if rows[d.id]["power_3"] == top)
        tied = [d for d in admissible if rows[d.id]["power_3"] >= top - se]
        recommended = min(tied, key=lambda d: (d.days, d.id)).id
    reaches = [d.id for d in admissible if rows[d.id]["power_3"] >= TARGET_POWER]
    return {"rows": rows, "recommended": recommended, "admissible": [d.id for d in admissible],
            "reach_target_power_at_3": reaches}


# -- the commands ----------------------------------------------------------------------------------------------------


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_pool() -> Tuple[Pool, str]:
    with tempfile.TemporaryDirectory() as tmp:
        panel = build_panel(Path(tmp))
        digest = sha256(panel)
        rows = load_daily_panel(panel)
    return build_pool(rows), digest


def describe_command(args) -> int:
    pool, digest = load_pool()
    print(json.dumps({
        "panel_sha256": digest, "first": pool.dates[0].isoformat(), "last": pool.dates[-1].isoformat(),
        "days": len(pool.dates), "days_b3": len(pool.dates3),
        "post_2020_days": sum(1 for d in pool.dates if d >= POST_2020_FIRST),
        "standardized_days": len(pool.dates) - WARMUP,
    }, sort_keys=True))
    return 0


def run_command(args) -> int:
    out = Path(args.out)
    pool, digest = load_pool()
    series = {design.id: design_series(pool, design) for design in DESIGNS}
    jobs = [(design, series[design.id], args.windows) for design in DESIGNS]
    with multiprocessing.Pool(max(1, args.workers)) as workers:
        calibrated = dict(workers.map(calibrate_design, jobs))
    print("calibrated", json.dumps({k: v["critical_values"] for k, v in calibrated.items()}), flush=True)
    histories = {(design.id, history): history_slice(series[design.id], history)
                 for design in DESIGNS for history in ("full", "post-2020")}
    critical = {k: v["critical_values"] for k, v in calibrated.items()}
    scenarios = simulate((histories, DESIGNS), critical, paths=args.paths, workers=args.workers)
    result = {
        "rule": str(RULE.relative_to(REPO)), "rule_sha256": sha256(RULE), "panel_sha256": digest,
        "study_end": STUDY_END.isoformat(),
        "pool": {"first": pool.dates[0].isoformat(), "last": pool.dates[-1].isoformat(), "days": len(pool.dates),
                 "days_b3": len(pool.dates3),
                 "post_2020_days": sum(1 for d in pool.dates if d >= POST_2020_FIRST)},
        "constants": {"windows": args.windows, "paths": args.paths, "seed": SEED, "calibration_seed": CALIBRATION_SEED,
                      "mme": sp.MME, "target_power": TARGET_POWER, "size_limit": SIZE_LIMIT,
                      "block_length": sp.BLOCK_LENGTH, "hac_lag": sp.HAC_LAG, "alpha": sp.ALPHA},
        "designs": {d.id: {"days": d.days, "leads": list(d.leads), "standardized": d.standardized,
                           "checkpoints": list(d.checkpoints), **calibrated[d.id]} for d in DESIGNS},
        "scenarios": scenarios,
        "reading": reading(scenarios),
    }
    out.mkdir(parents=True, exist_ok=True)
    (out / "result.json").write_text(json.dumps(result, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    print("wrote", out / "result.json")
    return 0


def pct(value: float) -> str:
    return f"{100 * value:.1f}%"


def share_cell(scenarios, design: Design, name: str, key: str = "with_the_mme_gate") -> str:
    """A share at the design's last look with its Monte Carlo standard error."""

    value = scenarios[design.id][name][key][str(design.days)]
    se = scenarios[design.id][name][key + "_se"]
    return f"{pct(value)} ± {pct(se)}"


def render_page(result, add=None) -> str:
    sc = result["scenarios"]
    reading_ = reading(sc)
    rows = reading_["rows"]
    c = result["constants"]
    lines = [
        "# Confirmation design study: result (H1 step 2, #733)",
        "",
        "<!-- generated: scripts/confirmation_design.py report; never hand-edited -->",
        "",
        f"The rule is [`confirmation-design-733.md`](confirmation-design-733.md) (committed before the study ran, "
        f"sha256 `{result['rule_sha256'][:12]}…`). Development data only: {result['pool']['days']} decision days from "
        f"{result['pool']['first']} to {result['pool']['last']} ({result['pool']['post_2020_days']} from 2020-04-03), "
        f"panel `{result['panel_sha256'][:8]}…`; no day after {result['study_end']} is read. It is a design study: "
        f"no verdict, nothing registered. Power figures are upper bounds (the B2 half and futility stopping are not "
        f"simulated). Paths per scenario: {c['paths']}; calibration windows per pair and per N: {c['windows']}.",
        "",
        "## Designs, size and power",
        "",
        "Size is the false-detection share by the last look under no true difference, without the MME gate. Power is "
        "the gated detection share by the last look. Every share is shown with its Monte Carlo standard error.",
        "",
        "| design | days | leads | scale | c at look 2 / 3 | size, full | size, post-2020 | power at 3%, full | power at 10%, full | power at 3%, post-2020 | power at 10%, post-2020 | smallest skill at 80% | admissible |",
        "|---|---|---|---|---|---|---|---|---|---|---|---|---|",
    ]
    for design in DESIGNS:
        r, info = rows[design.id], result["designs"][design.id]
        lead = "1 to 5" if len(design.leads) > 1 else "1"
        cv = info["critical_values"]
        looks = info["checkpoints"]
        lines.append(
            f"| {design.id} | {design.days} | {lead} | {'standardized' if design.standardized else 'raw'} | "
            f"{cv[str(looks[1])]:.2f} / {cv[str(looks[2])]:.2f} | "
            f"{share_cell(sc, design, 'size, full', 'without_the_mme_gate')} | "
            f"{share_cell(sc, design, 'size, post-2020', 'without_the_mme_gate')} | "
            f"{share_cell(sc, design, '3%, full')} | {share_cell(sc, design, '10%, full')} | "
            f"{share_cell(sc, design, '3%, post-2020')} | {share_cell(sc, design, '10%, post-2020')} | "
            f"{'none on the grid' if r['smallest_skill_at_80'] is None else pct(r['smallest_skill_at_80'])} | "
            f"{'yes' if r['admissible'] else 'no'} |"
        )
    lines += ["", "## Power by look", "",
              "Gated detection share by each look (look 1 is never read), with the mean days to first detection.", "",
              "| design | scenario | look 2 | look 3 | mean days to detection |", "|---|---|---|---|---|"]
    for design in DESIGNS:
        looks = result["designs"][design.id]["checkpoints"]
        for name in ("3%, full", "3%, post-2020", "10%, full", "10%, post-2020", "3%, full, noise 0.5",
                     "10%, full, noise 0.5"):
            cell = result["scenarios"][design.id][name]["with_the_mme_gate"]
            mean = result["scenarios"][design.id][name]["mean_days_to_detection"]
            lines.append(f"| {design.id} | {name} | {pct(cell[str(looks[1])])} | {pct(cell[str(looks[2])])} | "
                         f"{'none' if mean is None else f'{mean:.0f}'} |")
    lines += ["", "## Size by look", "", "| design | scenario | gate | look 2 | look 3 |", "|---|---|---|---|---|"]
    for design in DESIGNS:
        looks = result["designs"][design.id]["checkpoints"]
        for name in ("size, full", "size, post-2020"):
            for label, key in (("none", "without_the_mme_gate"), ("MME", "with_the_mme_gate")):
                cell = result["scenarios"][design.id][name][key]
                lines.append(f"| {design.id} | {name} | {label} | {pct(cell[str(looks[1])])} | {pct(cell[str(looks[2])])} |")
    lines += ["", "## Gated power by true skill (Full history, last look); the smallest skill with 80% power is the first cell at or above 80%", "",
              "| design | " + " | ".join(pct(g) for g in MDE_GRID) + " |", "|---|" + "---|" * len(MDE_GRID)]
    names = {0.03: "3%, full", 0.05: "5%, full", 0.075: "7.5%, full", 0.10: "10%, full", 0.15: "15%, full",
             0.20: "20%, full", 0.30: "30%, full"}
    for design in DESIGNS:
        cells = [pct(result["scenarios"][design.id][names[g]]["with_the_mme_gate"][str(design.days)])
                 for g in MDE_GRID]
        lines.append(f"| {design.id} | " + " | ".join(cells) + " |")
    lines += ["", "## Reading (§7)", ""]
    admissible = reading_["admissible"]
    lines.append("Admissible designs (size at most 5% on both histories): " + (", ".join(admissible) or "none") + ".")
    flagged = [d for d in admissible if rows[d]["size_upper_95"] > SIZE_LIMIT]
    if flagged:
        lines.append(f"Flagged, not excluded (a 95% upper bound on size above 5%): {', '.join(flagged)}.")
    reaches = reading_["reach_target_power_at_3"]
    lines.append("Admissible designs with 80% power at 3%: " + (", ".join(reaches) or "none") + ".")
    recommended = reading_["recommended"]
    base = rows["D0"]
    if recommended is None:
        lines += ["", "**Recommended design: none.** No design holds its size on both histories."]
    else:
        r = rows[recommended]
        lines += [
            "",
            f"**Recommended design: {recommended}** ({r['days']} days).",
            "",
            f"Trade-off against D0 (now in force, {base['days']} days): power at 3% {pct(base['power_3'])} → "
            f"{pct(r['power_3'])}, at 10% {pct(base['power_10'])} → {pct(r['power_10'])}; size on the full history "
            f"{pct(base['size_full'])} → {pct(r['size_full'])}; days {base['days']} → {r['days']}.",
        ]
        if not reaches:
            lines += ["", f"**No admissible design reaches {pct(TARGET_POWER)} power at 3%.** The pick above is the "
                      f"highest power among the admissible designs ({pct(r['power_3'])}), not a design with useful power; "
                      f"on the rule's own reading no design on the list can confirm the MME."]
    lines += [
        "",
        "## Rulings on the questions this page asked (this page decides nothing)",
        "",
        "Eleonora ruled on 14 October 2026 on this page's two questions. The reading of the critical value is already "
        "decided: reading (b), the value calibrated on each comparison (her ruling on PR #695, Q-E, 13 October); the "
        "largest-across-comparisons value that `scoring_protocol.CRITICAL_VALUES` holds on main is in force only until "
        "#737 applies reading (b) there. The side-by-side table of the two readings below stays. Whether a design that "
        "does not reach 80% power at 3% is acceptable, and the MME, are superseded: she has asked for power to be "
        "tested a different way, an empirical replay on real forecast pairs with three test families and a matched "
        "null generator, in #754 (H1 step 3). This page remains a study of the six declared designs and answers "
        "neither question.",
        "",
    ]
    if add is not None:
        lines += render_addendum(result, add)
    return "\n".join(lines)


def render_addendum(result, add) -> List[str]:
    sb = add["scenarios_b"]
    reading_b = reading(sb)
    rows = reading_b["rows"]
    lines = [
        "## Post-hoc addendum (written after the figures above were seen)",
        "",
        f"Rule: [`confirmation-design-733-addendum.md`](confirmation-design-733-addendum.md) (sha256 "
        f"`{add['addendum_sha256'][:12]}…`). It changes none of the figures above and not the recommendation above.",
        "",
        "### Reading (b): the critical value calibrated on S(B2) - S(B1) alone",
        "",
        "Same designs, paths, seeds and gate. The value at looks 2 and 3 is the one calibrated on that single comparison "
        "(PR #695, Q-E (b)), not the largest across the four.",
        "",
        "| design | days | c at look 2 / 3 | size, full | size, post-2020 | power at 3%, full | power at 10%, full | power at 3%, post-2020 | power at 10%, post-2020 | smallest skill at 80% | admissible |",
        "|---|---|---|---|---|---|---|---|---|---|---|",
    ]
    for design in DESIGNS:
        r = rows[design.id]
        cv = add["critical_values_b"][design.id]
        looks = result["designs"][design.id]["checkpoints"]
        lines.append(
            f"| {design.id} | {design.days} | {cv[str(looks[1])]:.2f} / {cv[str(looks[2])]:.2f} | "
            f"{share_cell(sb, design, 'size, full', 'without_the_mme_gate')} | "
            f"{share_cell(sb, design, 'size, post-2020', 'without_the_mme_gate')} | "
            f"{share_cell(sb, design, '3%, full')} | {share_cell(sb, design, '10%, full')} | "
            f"{share_cell(sb, design, '3%, post-2020')} | {share_cell(sb, design, '10%, post-2020')} | "
            f"{'none on the grid' if r['smallest_skill_at_80'] is None else pct(r['smallest_skill_at_80'])} | "
            f"{'yes' if r['admissible'] else 'no'} |"
        )
    ref = REFERENCE_695
    own = rows["D0"]
    lines += ["", f"Check against PR #695's Q-E table (reading (b), post-2020 history, 250 days, D0's rule): PR #695 reports "
              f"{pct(ref['power_3'])} power at 3%, {pct(ref['power_10'])} at 10% and {pct(ref['size'])} false detections; "
              f"this study's D0 gives {pct(own['power_3_post_2020'])}, {pct(own['power_10_post_2020'])} and "
              f"{pct(add['scenarios_b']['D0']['size, post-2020']['without_the_mme_gate']['250'])} "
              f"(a different pool: it ends on 2025-12-31 and PR #695's on 2026-09-03). The full-history columns differ "
              f"from the post-2020 ones because the full history holds one September 2019 day that the post-2020 "
              f"history does not.", ""]
    lines += ["Admissible at reading (b): " + (", ".join(reading_b["admissible"]) or "none") + ". "
              "With 80% power at 3%: " + (", ".join(reading_b["reach_target_power_at_3"]) or "none") + ". "
              "The rule of §7 applied to reading (b) recommends: "
              + (reading_b["recommended"] or "none") + ".", ""]
    lines += ["### Size under the calibration's own generator", "",
              "False-detection share by the last look under no true difference, without the MME gate, under the main "
              "study's calibrated values. Stationary: geometric blocks (the paths above). Circular: fixed blocks of 10 "
              "days, as the calibration's windows.", "",
              "| design | stationary, full | circular, full | stationary, post-2020 | circular, post-2020 |",
              "|---|---|---|---|---|"]
    for design in DESIGNS:
        last = str(design.days)
        cells = []
        for name in ("size, full", "size, post-2020"):
            cells.append(pct(result["scenarios"][design.id][name]["without_the_mme_gate"][last]))
            cells.append(pct(add["scenarios_circular"][design.id][name]["without_the_mme_gate"][last]))
        lines.append(f"| {design.id} | " + " | ".join(cells) + " |")
    lines += [
        "",
        "### Ruling on the post-hoc question",
        "",
        "Decided, not asked: reading (b) is the reading confirmation uses (Eleonora's ruling on PR #695, Q-E, 13 "
        "October 2026), and #737 applies it to `CRITICAL_VALUES`; the largest-across-comparisons value is in force on "
        "main only until #737 merges. The first holds size and has almost no power at any skill on the grid; the second "
        "has the power shown above and the size shown above.",
        "",
    ]
    return lines


#: PR #695's Q-E table, reading (b), the post-2020-04 series, 250 days (published figures, quoted for the check).
REFERENCE_695 = {"power_3": 0.14, "power_10": 0.1925, "size": 0.1165}
ADDENDUM = REPO / "docs" / "research" / "confirmation-design-733-addendum.md"
SIZE_SCENARIOS = ("size, full", "size, post-2020")


def reading_b_critical(result) -> Dict[str, Dict[str, float]]:
    """The addendum's reading (b): at each look, the value calibrated on S(B2) - S(B1) alone (the `B1-B2` entry)."""

    return {d: {n: info["per_pair"]["B1-B2"][n] for n in info["critical_values"]}
            for d, info in result["designs"].items()}


def addendum_command(args) -> int:
    out = Path(args.out)
    result = json.loads((out / "result.json").read_text(encoding="utf-8"))
    if result["rule_sha256"] != sha256(RULE):
        raise RuleError("result.json was made under another text of the rule")
    pool, digest = load_pool()
    if digest != result["panel_sha256"]:
        raise RuleError("the panel is not the one result.json was made on")
    series = {design.id: design_series(pool, design) for design in DESIGNS}
    histories = {(design.id, history): history_slice(series[design.id], history)
                 for design in DESIGNS for history in ("full", "post-2020")}
    paths = result["constants"]["paths"]
    critical_b = reading_b_critical(result)
    scenarios_b = simulate((histories, DESIGNS), critical_b, paths=paths, workers=args.workers)
    critical = {d: info["critical_values"] for d, info in result["designs"].items()}
    circular = simulate((histories, DESIGNS), critical, paths=paths, workers=args.workers,
                        generator="circular", scenarios=SIZE_SCENARIOS)
    add = {
        "post_hoc": True, "addendum": str(ADDENDUM.relative_to(REPO)), "addendum_sha256": sha256(ADDENDUM),
        "rule_sha256": result["rule_sha256"], "critical_values_b": critical_b,
        "scenarios_b": scenarios_b, "reading_b": reading(scenarios_b), "scenarios_circular": circular,
    }
    (out / "addendum.json").write_text(json.dumps(add, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    print("wrote", out / "addendum.json")
    return 0


def report_command(args) -> int:
    result = json.loads((Path(args.out) / "result.json").read_text(encoding="utf-8"))
    add_path = Path(args.out) / "addendum.json"
    add = json.loads(add_path.read_text(encoding="utf-8")) if add_path.exists() else None
    PAGE.write_text(render_page(result, add), encoding="utf-8")
    print("wrote", PAGE)
    return 0


def check_command(args) -> int:
    result = json.loads((Path(args.out) / "result.json").read_text(encoding="utf-8"))
    if result["rule_sha256"] != sha256(RULE):
        raise RuleError("result.json was made under another text of the rule")
    if result["pool"]["last"] > STUDY_END.isoformat():
        raise RuleError("the study scored a day after its end")
    add_path = Path(args.out) / "addendum.json"
    add = json.loads(add_path.read_text(encoding="utf-8")) if add_path.exists() else None
    if add is not None and add["addendum_sha256"] != sha256(ADDENDUM):
        raise RuleError("addendum.json was made under another text of the addendum")
    if PAGE.read_text(encoding="utf-8") != render_page(result, add):
        raise RuleError("the result page is not the one result.json renders")
    print("ok")
    return 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="command", required=True)
    describe = sub.add_parser("describe")
    describe.set_defaults(func=describe_command)
    run = sub.add_parser("run")
    run.add_argument("--out", required=True)
    run.add_argument("--paths", type=int, default=PATHS)
    run.add_argument("--windows", type=int, default=WINDOWS)
    run.add_argument("--workers", type=int, default=1)
    run.set_defaults(func=run_command)
    addendum = sub.add_parser("addendum")
    addendum.add_argument("--out", required=True)
    addendum.add_argument("--workers", type=int, default=1)
    addendum.set_defaults(func=addendum_command)
    for name, func in (("report", report_command), ("check", check_command)):
        command = sub.add_parser(name)
        command.add_argument("--out", required=True)
        command.set_defaults(func=func)
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
