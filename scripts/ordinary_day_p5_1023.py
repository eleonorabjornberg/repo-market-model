#!/usr/bin/env python3
"""#934's ordinary-day result restated on the five declared regimes (#1023; H1 regime splits, over H5 step 3 data).

Eleonora's ruling on #1011 (20 October 2026): restate #934 on the five regimes of `metadata/evaluation_splits.json`, paired,
and keep the three-regime table of #683/#934 beside it with its 2020-24 cell marked "cross-regime, not a regime result".
Development data only; this is not a verdict (scoring protocol v1, #640).

It adds no model and no variant: the rows, the persistence-logistic reference, the outcome, the ordinary-day definitions, the
interval (90% stationary-bootstrap percentile, block 10, 2000 replications, paired against persistence-logistic) and the end of
the scored days are #844's, whose declaration `metadata/exploration_844.json` it reads through `ordinary_day_p5_844`. Only the
grouping of days changes: a day's regime is `evaluation_splits.json`'s, not `reliability_regimes.REGIMES`'s. The cells file is
#844's `cells` output; its stored three-regime label is ignored. The regime declared for 2027 holds no scored day (nothing after
2025-12-31 is read), so it has no cell, and the regime labelled 2025-26 holds the days of 2025 only.

The cells need the #634 walks (hours): see `.claude/skills/long-run`. The commands, per lead where a step is per lead:

    PYTHONPATH=src python3 -m repo_model.cli build --raw-root tests/fixtures/snapshots/funding_inputs --output PUBLISHED.csv \\
        --build-cutoff 2026-09-08T21:31:42+00:00 --decision-time 16:00:00
    # the scratch panel AUG2D.csv and the walks into WALKS/ by the docstring of scripts/spread_distribution_634.py
    PYTHONPATH=src python3 scripts/ordinary_day_p5_844.py cells --panel PUBLISHED.csv --walks WALKS --output CELLS.json
    cp CELLS.json docs/research/ordinary-day-p5-1023/cells.json   # kept, so a later score needs no walks
    PYTHONPATH=src python3 scripts/ordinary_day_p5_1023.py score --cells CELLS.json --output docs/research/ordinary-day-p5-1023/result.json
    PYTHONPATH=src python3 scripts/ordinary_day_p5_1023.py page --result docs/research/ordinary-day-p5-1023/result.json \\
        --output docs/research/ordinary-day-p5-1023-result.md

`page` reads the three-regime table from the committed score of #844, `docs/pivot/ordinary-day-p5-844/score.json`; nothing there
is edited.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import random
import sys
from bisect import bisect_left, bisect_right
from concurrent.futures import ProcessPoolExecutor
from datetime import date
from pathlib import Path
from typing import Dict, Optional, Sequence

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from repo_model import scoring_protocol as sp  # noqa: E402
from repo_model.evaluation_splits import load_split_declaration  # noqa: E402
from repo_model.metrics import stationary_bootstrap_indices  # noqa: E402

_spec = importlib.util.spec_from_file_location("ordinary_day_p5_844_for_1023", ROOT / "scripts" / "ordinary_day_p5_844.py")
base = importlib.util.module_from_spec(_spec)
sys.modules[_spec.name] = base
_spec.loader.exec_module(base)

SPLITS_PATH = ROOT / "metadata" / "evaluation_splits.json"
SCORE_934 = ROOT / "docs" / "pivot" / "ordinary-day-p5-844" / "score.json"
SPLITS = load_split_declaration(SPLITS_PATH)
#: The declared regimes that can hold a scored day: those that start on or before the last scored day.
REGIMES = tuple(r for r in SPLITS.regimes if r[1] <= base.LAST_DAY)
LABELS = tuple(label for label, _, _ in REGIMES)
#: The cells of the three-regime table (#683/#934) that span more than one declared regime.
CROSS_REGIME_CELLS = {"2020-24"}
CROSS_REGIME_NOTE = "cross-regime, not a regime result"
CELLS = ("pooled",) + LABELS


def regime_of(day: date) -> str:
    """The declared regime of a scored day; a day outside every scored regime is refused, never given a default."""

    for label, first, last in REGIMES:
        if first <= day <= last:
            return label
    raise ValueError(f"{day} falls in no scored regime declared in {SPLITS_PATH.name} ({REGIMES[0][1]} to {base.LAST_DAY})")


# -- the studentized one-sided bound (scoring protocol section 5; Eleonora's ruling on #1023, comment 6340379028) -----------


def auroc_influence(scores: Sequence[float], outcomes: Sequence[int]) -> Optional[tuple]:
    """AUROC and its per-day influence series (DeLong placement values, ties half), or `None` with no day of either kind.

    The series `psi_t` is scaled so that AUROC is, to first order, `theta + mean(psi)`: a pressure day carries
    `(n / events) * (V10_t - theta)`, any other day `(n / others) * (V01_t - theta)`, where `V10_t` is the share of other days
    it scores above (ties half) and `V01_t` the share of pressure days that score above it. It plays the part the daily score
    difference `d_t` plays for a CRPS: a series whose mean is the statistic and whose Newey-West variance is its variance.
    """

    n = len(outcomes)
    events = sum(outcomes)
    others = n - events
    if events == 0 or others == 0:
        return None
    pos = sorted(s for s, y in zip(scores, outcomes) if y)
    neg = sorted(s for s, y in zip(scores, outcomes) if not y)
    placement = []
    for s, y in zip(scores, outcomes):
        if y:
            placement.append((bisect_left(neg, s) + 0.5 * (bisect_right(neg, s) - bisect_left(neg, s))) / others)
        else:
            placement.append((events - bisect_right(pos, s) + 0.5 * (bisect_right(pos, s) - bisect_left(pos, s))) / events)
    theta = sum(p for p, y in zip(placement, outcomes) if y) / events
    psi = [(n / events if y else n / others) * (p - theta) for p, y in zip(placement, outcomes)]
    return theta, psi


def _difference(model: Sequence[float], reference: Sequence[float], outcomes: Sequence[int]) -> Optional[tuple]:
    a, b = auroc_influence(model, outcomes), auroc_influence(reference, outcomes)
    if a is None or b is None:
        return None
    return a[0] - b[0], [x - y for x, y in zip(a[1], b[1])]


def studentized_bound(
    model: Sequence[float], reference: Sequence[float], outcomes: Sequence[int], *, seed: int, replications: int,
    block_length: float = None, alpha: float = sp.ALPHA, lag: int = sp.HAC_LAG,
) -> Optional[dict]:
    """The protocol's one-sided studentized stationary-bootstrap lower bound of the AUROC difference (model minus reference).

    Section 5 applied to a statistic that is not a mean of daily scores: the unit is the target day (one decision per day, the
    unit the percentile interval resamples), the cell's days in date order. The standard error is the Newey-West (Bartlett)
    long-run standard error at the protocol's lag of the day-level influence series of the difference (`auroc_influence`);
    each resample's difference is studentized by its own such standard error, `t* = (theta* - theta) / se*`, and the bound is
    `theta - q_(1 - alpha)(t*) * se`. The resamples are the stationary bootstrap's (mean block 10 days) from `random.Random(seed)`:
    the stream the percentile interval of the same cell draws, so both read the same resamples. The AUROC difference of a
    resample with no pressure day or no other day, or whose standard error is zero, is left out and counted. Returns `None` where
    the cell has no AUROC or the observed standard error is zero.
    """

    block_length = base.BLOCK if block_length is None else block_length
    observed = _difference(model, reference, outcomes)
    if observed is None:
        return None
    theta, psi = observed
    n = len(outcomes)
    se = (sp._long_run_variance(psi, lag) / n) ** 0.5
    if se == 0.0:
        return None
    rng = random.Random(seed)
    draws = []
    for _ in range(replications):
        idx = stationary_bootstrap_indices(n, block_length, rng)
        again = _difference([model[i] for i in idx], [reference[i] for i in idx], [outcomes[i] for i in idx])
        if again is None:
            continue
        se_star = (sp._long_run_variance(again[1], lag) / n) ** 0.5
        if se_star > 0.0:
            draws.append((again[0] - theta) / se_star)
    if min(alpha, 1.0 - alpha) * len(draws) < 1.0:
        return None
    draws.sort()
    q = sp._quantile(draws, 1.0 - alpha)
    return {"lower_bound": theta - q * se, "standard_error": se, "t": theta / se, "level": 1.0 - alpha,
            "draws_used": len(draws), "draws_dropped": replications - len(draws), "lag": lag}


def _job(job):
    key, columns, outcomes, seed, replications = job
    body = base.cell_result(columns, outcomes, seed=seed, replications=replications)
    if body["pressure_days"] >= base.MINIMUM_PRESSURE_DAYS:
        for name in base.MODEL_ROWS:
            if name in columns and body["rows"][name]["auroc_minus_reference"]["interval"] is not None:
                body["rows"][name]["auroc_minus_reference"]["studentized"] = studentized_bound(
                    columns[name], columns[base.REFERENCE], outcomes, seed=seed, replications=replications)
    return key, body


def score_document(document: dict, *, replications: Optional[int] = None, workers: int = 1) -> dict:
    """Score #844's cells with the days regrouped by the declared regimes; returns the result in #844's shape."""

    replications = replications or base.REPLICATIONS
    jobs = []
    for definition_index, definition in enumerate(base.DEFINITIONS):
        for h in base.HORIZONS:
            rows = document["horizons"].get(str(h), [])
            base.require_scored_days(date.fromisoformat(r["day"]) for r in rows)
            for cell_index, cell in enumerate(CELLS):
                kept = [r for r in rows if r["ordinary"][definition] and (cell == "pooled" or regime_of(date.fromisoformat(r["day"])) == cell)]
                if not kept:
                    continue
                columns = {name: [r["p"][name] for r in kept] for name in sorted(kept[0]["p"])}
                seed = 1023 * 1000 + 100 * h + 10 * cell_index + 5 * definition_index
                jobs.append(((definition, h, cell), columns, [r["y"] for r in kept], seed, replications))
    if workers == 1:
        done = dict(_job(job) for job in jobs)
    else:
        with ProcessPoolExecutor(max_workers=workers) as pool:
            done = dict(pool.map(_job, jobs))
    result: Dict[str, dict] = {}
    for (definition, h, cell), body in done.items():
        result.setdefault(definition, {}).setdefault(str(h), {})[cell] = body
    return {
        "issue": 1023, "level": base.LEVEL, "block_length": base.BLOCK, "replications": replications,
        "panel_sha256": document["panel_sha256"], "decision_days": document["decision_days"], "walks": document["walks"],
        "regimes": [[label, first.isoformat(), last.isoformat()] for label, first, last in REGIMES],
        "definitions": result,
    }


def _entry(result: dict, h: int, cell: str, name: str) -> Optional[dict]:
    body = result["definitions"]["non_ordinary"].get(str(h), {}).get(cell)
    if body is None or body["pressure_days"] < base.MINIMUM_PRESSURE_DAYS:
        return None
    return body["rows"][name]["auroc_minus_reference"]


def _studentized_text(entry: dict) -> str:
    if "studentized" not in entry:
        return "studentized bound: pending the re-score"
    bound = entry["studentized"]
    return "studentized lower bound n/a" if bound is None else f"studentized lower bound {bound['lower_bound']:+.3f}"


def _table(result: dict, name: str, cells: Sequence[str], headers: Sequence[str], studentized: bool = False) -> list:
    out = ["| lead | " + " | ".join(headers) + " |", "|---|" + "---|" * len(cells)]
    for h in base.HORIZONS:
        row = []
        for cell in cells:
            body = result["definitions"]["non_ordinary"].get(str(h), {}).get(cell)
            if body is None or body["pressure_days"] < base.MINIMUM_PRESSURE_DAYS:
                row.append("n/a" if body is None else f"n/a ({body['pressure_days']} pressure days)")
            else:
                entry = body["rows"][name]["auroc_minus_reference"]
                text = f"{base.fmt(entry, signed=True)} ({body['pressure_days']} pressure days)"
                if studentized and entry["interval"] is not None:
                    text += f"; {_studentized_text(entry)}"
                row.append(text)
        out.append(f"| {h} | " + " | ".join(row) + " |")
    return out + [""]


def _tally(result: dict, cells: Sequence[str]) -> list:
    lines = []
    for name in base.MODEL_ROWS:
        tally, counted = {"above": 0, "covers": 0, "below": 0}, 0
        for h in base.HORIZONS:
            for cell in cells:
                verdict = base.sign_of(_entry(result, h, cell, name))
                if verdict is not None:
                    tally[verdict] += 1
                    counted += 1
        lines.append(f"- **{base.LABELS[name]}**: of {counted} regime-by-lead cells with at least {base.MINIMUM_PRESSURE_DAYS} pressure days "
                     f"and an interval, above zero in {tally['above']}, covers zero in {tally['covers']}, below zero in {tally['below']}.")
    return lines


def _studentized_tally(result: dict, cells: Sequence[str]) -> list:
    lines = []
    for name in base.MODEL_ROWS:
        above = counted = 0
        for h in base.HORIZONS:
            for cell in cells:
                entry = _entry(result, h, cell, name)
                if entry is None or entry["interval"] is None or entry.get("studentized") is None:
                    continue
                counted += 1
                above += entry["studentized"]["lower_bound"] > 0
        lines.append(f"- **{base.LABELS[name]}**: the studentized one-sided lower bound is above zero in {above} of {counted} cells that have one."
                     if counted else f"- **{base.LABELS[name]}**: studentized bounds pending the re-score.")
    return lines


PROVISIONAL_NOTE = (
    "**provisional: calendar not read at the target day.** The rows that carry the figures here are the models of #934, whose "
    "result is row 10 of the provisional register (`docs/research/provisional-calendar-register.md`, class b for `gbm_funding`): "
    "the figures below restate #934's cells on the five regimes and stay provisional until #934 is re-run on direct pairs. "
    "The register marks this; no figure here is edited (#1169)."
)


def render(result: dict, three: dict) -> str:
    level = round(result["level"] * 100)
    five_headers = list(LABELS)
    three_cells = [c for c in base.CELLS if c != "pooled"]
    three_headers = [f"{c} ({CROSS_REGIME_NOTE})" if c in CROSS_REGIME_CELLS else c for c in three_cells]
    out = [
        "# The ordinary-day result of #934 on the five declared regimes (#1023)", "",
        "**Hypothesis and step:** H1 (regime splits), applied to the ordinary-day result of H5 step 3 (#844, corrected by #934). "
        "**Development data only: this is not a verdict** (scoring protocol v1, #640). On Eleonora's ruling on #1011 (20 October 2026): "
        "#934 restated on the five regimes of `metadata/evaluation_splits.json`, with the three-regime table kept beside it. "
        "**No pooled gain is claimed.**", "",
        PROVISIONAL_NOTE, "",
        "Nothing new is modelled: the rows, the reference, the outcome and the ordinary-day definition (`risk_dates.NON_ORDINARY`, read at "
        f"the target day) are #844's. Each cell is the paired AUROC difference from persistence-logistic on ordinary target days with its "
        f"{level}% stationary-bootstrap percentile interval (block {result['block_length']}, {result['replications']} replications; the "
        "interval #934 used, so the two tables compare). Above zero is better than persistence-logistic. `n/a`: fewer than "
        f"{base.MINIMUM_PRESSURE_DAYS} pressure days. `†`: no interval. No day after 2025-12-31 is read: the regime labelled 2025-26 "
        "holds the days of 2025, and the declared 2027 regime holds none.", "",
        "**Ruling recorded (Eleonora, 22 October 2026, comment 6340379028 on PR #1103):** read these AUROC differences on the "
        "protocol's studentized one-sided bound as well, beside #934's percentile interval. Each five-regime cell below carries both: "
        "the percentile interval, which compares with #934's table, and the studentized one-sided "
        f"{round(100 * (1 - sp.ALPHA))}% lower bound of the scoring protocol (section 5). "
        "The studentization is over target days, the unit the bootstrap resamples (one decision per day), in date order within "
        "the cell: the standard error is the Newey-West (Bartlett) one at the protocol's lag "
        f"{sp.HAC_LAG}, of the day-level influence series of the AUROC difference (DeLong placement values, so that the AUROC "
        "difference is, to first order, the mean of that series, as `mean(d)` is for a CRPS difference); each resample's "
        "difference is divided by its own such standard error, and the bound is the point value less the "
        f"{round(100 * (1 - sp.ALPHA))}th percentile of those t-draws times the observed standard error. Decision days would be the "
        "same days here: a lead's forecasts are scored on their target days. The resamples are the percentile interval's own "
        "(same seed, block 10). The bound is one-sided at 5%, the level of each tail of the 90% percentile interval, "
        "and a cell with no percentile interval shows no bound.", "",
        "## Five declared regimes", "",
        "Regimes: " + ", ".join(f"{label} ({first} to {last})" if last <= "2025-12-31" else f"{label} ({first} onward, read to 2025-12-31)"
                                        for label, first, last in result["regimes"]) + ".", "",
    ]
    for name in base.MODEL_ROWS:
        out += [f"### {base.LABELS[name]}", "", *_table(result, name, LABELS, five_headers, studentized=True)]
    out += ["### Tally of regime-by-lead cells (five regimes, development)", "", *_tally(result, LABELS), "",
            *_studentized_tally(result, LABELS), "",
            "These lines count cells; they set no threshold.", "",
            "## The three-regime table of #683/#934, kept", "",
            "Read from the committed score of #844 (`docs/pivot/ordinary-day-p5-844/score.json`); nothing is rescored and neither "
            "published page is edited. Its 2020-24 cell pools 2020, 2021-23 and 2024: its pairs cross regimes, so it is "
            f"**{CROSS_REGIME_NOTE}**.", ""]
    for name in base.MODEL_ROWS:
        out += [f"### {base.LABELS[name]}", "", *_table(three, name, three_cells, three_headers)]
    out += ["### Tally of regime-by-lead cells (three regimes, development)", "", *_tally(three, three_cells), "",
            "The 2020-24 cells are counted here as #934 counted them; they are not a regime result.", ""]
    return "\n".join(out)


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="command", required=True)
    s = sub.add_parser("score", help="score #844's cells regrouped by the five declared regimes")
    s.add_argument("--cells", required=True)
    s.add_argument("--output", required=True)
    s.add_argument("--workers", type=int, default=4)
    s.add_argument("--replications", type=int, help="override the declared replications (a smoke run only)")
    p = sub.add_parser("page", help="render the page from the result and the committed score of #844")
    p.add_argument("--result", required=True)
    p.add_argument("--output", required=True)
    args = parser.parse_args(argv)
    if args.command == "score":
        base.committed_declaration()
        document = json.loads(Path(args.cells).read_text(encoding="utf-8"))
        result = score_document(document, replications=args.replications, workers=args.workers)
        Path(args.output).parent.mkdir(parents=True, exist_ok=True)
        Path(args.output).write_text(json.dumps(result, indent=1, sort_keys=True) + "\n", encoding="utf-8")
        return 0
    result = json.loads(Path(args.result).read_text(encoding="utf-8"))
    three = json.loads(SCORE_934.read_text(encoding="utf-8"))
    Path(args.output).write_text(render(result, three), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
