"""Does the 2014-2018 back-fill move the 2018-19 spread forecast? (#633, H4 step 2)

A scratch measurement, not a record: it writes JSON and Markdown to the paths it is given and nothing into
`docs/runs/`. Exploration on development data: under scoring protocol v1 (#640) such data never gives a verdict.
Every choice is in `metadata/backfill_spread_633.json`, which this script refuses to read unless it is committed and
unchanged. No day after 2025-12-31 is read (`docs/decisions/lockbox.md`; `scoring_protocol.day_scores` calls
`lockbox.require_unlocked`).

The model is a gradient-boosted quantile regression of the spread at the 23 levels of `scoring_protocol.GRID`, at
leads 1 to 5, on inputs that the back-filled rows carry. It is run twice, unchanged: on the scratch panel (published
days only) and on the extended panel (the same days and the 899 back-filled rows before them). Every fit of the
extended arm passes `backfill.require_training_only` and `backfill.require_posting_established` with the instant
declared in `metadata/backfill_posting.json` (17 May 2018, Eleonora's ruling on PR #661).

    PYTHONPATH=src python3 scripts/backfill_history.py panel --output EXT.csv --scratch SCRATCH.csv
    for arm in without with; for h in 1 2 3 4 5:
        PYTHONPATH=src python3 scripts/backfill_spread_633.py forecasts --panel {SCRATCH,EXT}.csv --arm $arm \\
            --horizon $h --output OUT/${arm}_h$h.json
    PYTHONPATH=src python3 scripts/backfill_spread_633.py score --scratch SCRATCH.csv --runs OUT \\
        --output OUT/score.json --markdown OUT/score.md

The workbook-only sensitivity (declared after the first score): `forecasts ... --inputs workbook --output
OUT/${arm}_h${h}_wb.json`, then `score ... --suffix _wb`.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import math
import random
import sys
from datetime import date, time
from pathlib import Path
from typing import Dict, List, Mapping, Optional, Sequence, Tuple

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))

from repo_model import backfill, metrics, protocol_benchmarks as pb, scoring_protocol as sp  # noqa: E402
from repo_model.asof import InformationRule  # noqa: E402
from repo_model.baseline import ScoredFold, panel_sha256  # noqa: E402
from repo_model.data import load_daily_panel  # noqa: E402
from repo_model.evaluation_splits import load_split_declaration  # noqa: E402
from repo_model.splits import SplitError  # noqa: E402

DECLARATION = REPO / "metadata" / "backfill_spread_633.json"
POSTING = REPO / "metadata" / "backfill_posting.json"
REGISTRY = REPO / "metadata" / "sources.json"
SPLITS = REPO / "metadata" / "evaluation_splits.json"
DECISION = time(16, 0)
FIRST_DECISION = date(2018, 6, 29)
LAST_TARGET = date(2025, 12, 31)
REFIT_EVERY = 21
SEED = 633
OBSERVED = ("tgcr", "bgcr", "reserve_balances", "tga", "tbill_4w")
CALENDAR = ("quarter_end", "tax_date", "days_to_month_end")
FEATURES = OBSERVED + CALENDAR
NAMES = (
    "spread", "spread_change_5", "tgcr_iorb", "bgcr_iorb", "tbill_4w_iorb", "reserve_balances", "tga",
) + CALENDAR
ARMS = ("without", "with")
#: The sensitivity declared after the first score: the inputs the ruled workbook and the calendar carry.
WORKBOOK_ONLY = ("spread", "spread_change_5", "tgcr_iorb", "bgcr_iorb") + CALENDAR
LOW90, HIGH90 = sp.GRID.index(0.05), sp.GRID.index(0.95)
LOW50, HIGH50 = sp.GRID.index(0.25), sp.GRID.index(0.75)


def _committed_declaration() -> dict:
    spec = importlib.util.spec_from_file_location("rds_633", REPO / "scripts" / "risk_date_severity.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.committed_declaration(DECLARATION)


def decision_indices(dates: Sequence[date]) -> List[int]:
    """The declared decision days: from 2018-06-29, with the lead-5 target on or before 2025-12-31."""

    top = max(sp.HORIZONS)
    return [
        index for index, day in enumerate(dates)
        if day >= FIRST_DECISION and index + top < len(dates) and dates[index + top] <= LAST_TARGET
    ]


def features(rows, rule: InformationRule, dates, scored: int) -> Optional[Tuple[List[float], int]]:
    """The declared inputs of the forecast of row `scored` at the rule's lead, and its anchor; `None` if a read is a hole."""

    try:
        info = rule.information_set(dates, scored)
    except SplitError:
        return None
    rule.check(dates, info)
    seen = rule.observation(rows, info)
    anchor = info.anchor
    if anchor < 5:
        return None
    values = seen.values
    iorb = values.get("iorb")
    before = rows[anchor - 5].spread_bps
    cells = [values.get(name) for name in OBSERVED + CALENDAR]
    if iorb is None or any(cell is None for cell in cells) or before is None:
        return None
    spread = seen.spread_bps
    out = [
        spread,
        spread - before,
        100.0 * (values["tgcr"] - iorb),
        100.0 * (values["bgcr"] - iorb),
        100.0 * (values["tbill_4w"] - iorb),
        values["reserve_balances"],
        values["tga"],
    ] + [float(values[name]) for name in CALENDAR]
    if any(not math.isfinite(value) for value in out):
        return None
    return out, anchor


def _select(row: Sequence[float], inputs: str) -> List[float]:
    """The declared inputs (`declared`), or the workbook-only sensitivity's (`workbook`)."""

    if inputs == "declared":
        return list(row)
    return [value for name, value in zip(NAMES, row) if name in WORKBOOK_ONLY]


def forecasts_command(args) -> int:
    from repo_model.ml import PRESSURE_CLASSIFIER_SETTINGS, _estimator_class

    HistGradientBoostingRegressor = _estimator_class()  # the ml extra, imported in ml.py only

    _committed_declaration()
    h = args.horizon
    if h not in sp.HORIZONS:
        raise SystemExit(f"a lead is one of {sp.HORIZONS}")
    rows = load_daily_panel(args.panel)
    dates = [row.date for row in rows]
    prefix = backfill.prefix_length(dates)
    if (args.arm == "with") != (prefix > 0):
        raise SystemExit(f"the {args.arm} arm needs {'a' if args.arm == 'with' else 'no'} back-filled row ({prefix} found)")
    registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
    rule = InformationRule(registry, FEATURES, decision_time=DECISION, horizon=h)
    posting = backfill.load_posting_instant(POSTING)
    settings = {key: value for key, value in PRESSURE_CLASSIFIER_SETTINGS.items() if key != "estimator"}

    pairs: Dict[int, List[float]] = {}
    for label in range(len(rows)):
        if dates[label] > LAST_TARGET:
            break
        read = features(rows, rule, dates, label)
        if read is not None and rows[label].spread_bps is not None:
            pairs[label] = read[0]
    decisions = decision_indices(dates)
    out: Dict[str, List[float]] = {}
    blocks = []
    for start in range(0, len(decisions), REFIT_EVERY):
        block = decisions[start:start + REFIT_EVERY]
        first = rule.information_set(dates, block[0] + h)
        rule.check(dates, first)
        labels = [s for s in sorted(pairs) if s <= first.anchor]
        folds = [
            ScoredFold(
                train_start=dates[labels[0]], train_end=dates[labels[-1]], train_rows=len(labels),
                feature_date=dates[rule.information_set(dates, d + h).anchor], scored_date=dates[d + h],
            )
            for d in block
        ]
        backfill.require_training_only(folds, where="backfill_spread_633")
        backfill.require_posting_established(folds, posting, where="backfill_spread_633")
        xs = [_select(pairs[s], args.inputs) for s in labels]
        ys = [rows[s].spread_bps for s in labels]
        models = [
            HistGradientBoostingRegressor(loss="quantile", quantile=level, **settings).fit(xs, ys) for level in sp.GRID
        ]
        served = []
        for d in block:
            read = features(rows, rule, dates, d + h)
            if read is None:
                continue
            x = [_select(read[0], args.inputs)]
            out[dates[d].isoformat()] = sorted(float(model.predict(x)[0]) for model in models)
            served.append(d)
        blocks.append({
            "train_start": dates[labels[0]].isoformat(), "train_end": dates[labels[-1]].isoformat(),
            "train_rows": len(labels), "backfilled_train_rows": sum(1 for s in labels if dates[s] < backfill.FIRST_PUBLISHED),
            "first_decision": dates[block[0]].isoformat(), "last_decision": dates[block[-1]].isoformat(),
            "served": len(served),
        })
    document = {
        "issue": 633, "arm": args.arm, "horizon": h, "panel_sha256": panel_sha256(args.panel),
        "backfilled_rows": prefix, "posting_instant": None if posting is None else posting.isoformat(),
        "levels": list(sp.GRID), "inputs": [name for name in NAMES if args.inputs == "declared" or name in WORKBOOK_ONLY], "blocks": blocks, "forecasts": out,
    }
    args.output.write_text(json.dumps(document, indent=1) + "\n", encoding="utf-8")
    print(json.dumps({"arm": args.arm, "horizon": h, "blocks": len(blocks), "forecasts": len(out)}))
    return 0


# -- scoring -------------------------------------------------------------------------------------------------------


def _interval(differences: Sequence[float], level: float = 0.90, draws: int = sp.DRAWS) -> Tuple[float, float]:
    """A two-sided stationary-bootstrap interval of the mean of `differences` (mean block 10, seed 633)."""

    n = len(differences)
    prefix = [0.0]
    for value in differences:
        prefix.append(prefix[-1] + value)
    rng = random.Random(SEED)
    means = []
    for _ in range(draws):
        starts, ends = sp._segments(metrics.stationary_bootstrap_indices(n, sp.BLOCK_LENGTH, rng), n)
        means.append(sum(prefix[e] - prefix[s] for s, e in zip(starts, ends)) / n)
    means.sort()
    tail = (1.0 - level) / 2.0
    return means[int(math.floor(tail * draws))], means[min(draws - 1, int(math.ceil((1.0 - tail) * draws)) - 1)]


def _coverage(forecasts: Mapping[date, Mapping[int, Sequence[float]]], outcomes, calendar) -> Dict[str, Dict[date, float]]:
    position = {day: k for k, day in enumerate(calendar)}
    out = {"inside_90": {}, "inside_50": {}, "above_95": {}}
    for day, leads in forecasts.items():
        cells = []
        for h in sp.HORIZONS:
            y = outcomes.get(calendar[position[day] + h])
            if y is not None:
                cells.append((leads[h], y))
        out["inside_90"][day] = sum(q[LOW90] <= y <= q[HIGH90] for q, y in cells) / len(cells)
        out["inside_50"][day] = sum(q[LOW50] <= y <= q[HIGH50] for q, y in cells) / len(cells)
        out["above_95"][day] = sum(y > q[HIGH90] for q, y in cells) / len(cells)
    return out


def _load_arm(runs: Path, arm: str, suffix: str = "") -> Tuple[Dict[date, Dict[int, List[float]]], List[dict]]:
    by_day: Dict[date, Dict[int, List[float]]] = {}
    documents = []
    for h in sp.HORIZONS:
        document = json.loads((runs / f"{arm}_h{h}{suffix}.json").read_text(encoding="utf-8"))
        if document["arm"] != arm or document["horizon"] != h or tuple(document["levels"]) != sp.GRID:
            raise SystemExit(f"{arm}_h{h}.json is not the {arm} arm at lead {h} on the protocol's grid")
        documents.append(document)
        for day, quantiles in document["forecasts"].items():
            by_day.setdefault(date.fromisoformat(day), {})[h] = quantiles
    return {day: leads for day, leads in by_day.items() if set(leads) == set(sp.HORIZONS)}, documents


def score_command(args) -> int:
    declaration = _committed_declaration()
    rows = load_daily_panel(args.scratch)
    if backfill.prefix_length([row.date for row in rows]):
        raise SystemExit("--scratch must be the panel of published days")
    rows = [row for row in rows if row.date <= LAST_TARGET]
    calendar = [row.date for row in rows]
    outcomes = {row.date: row.spread_bps for row in rows}
    splits = load_split_declaration(SPLITS)
    registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
    arms = {}
    documents = {}
    for arm in ARMS:
        arms[arm], documents[arm] = _load_arm(args.runs, arm, args.suffix)
    declared = [calendar[k] for k in decision_indices(calendar)]
    days = [day for day in declared if day in arms["without"] and day in arms["with"]]
    position = {day: k for k, day in enumerate(calendar)}
    b1 = {day: pb.b1_forecast(rows, position[day], registry=registry, decision_time=DECISION) for day in days}
    forecasts = {"without": {d: arms["without"][d] for d in days}, "with": {d: arms["with"][d] for d in days}, "B1": b1}
    crps = {name: sp.day_scores(f, outcomes, calendar) for name, f in forecasts.items()}
    tw = {name: sp.day_scores(f, outcomes, calendar, score=sp.upper_tail_twcrps) for name, f in forecasts.items()}
    cover = {name: _coverage(f, outcomes, calendar) for name, f in forecasts.items() if name != "B1"}

    groups: Dict[str, List[date]] = {"pooled": days}
    for day in days:
        groups.setdefault(f"regime {splits.regime(day)}", []).append(day)
    for day in days:
        target = rows[position[day] + 1]
        groups.setdefault(f"type {splits.reporting_day_type(target.date, target.values)}", []).append(day)

    def tests(group: List[date]) -> dict:
        sub = lambda scores: {d: scores[d] for d in group}  # noqa: E731
        main, twc, s_without, s_with = sp.paired_tests(
            [
                (sub(crps["without"]), sub(crps["with"])),
                (sub(tw["without"]), sub(tw["with"])),
                (sub(crps["B1"]), sub(crps["without"])),
                (sub(crps["B1"]), sub(crps["with"])),
            ],
            seed=SEED,
        )

        def paired(test) -> dict:
            draws = test.mean_difference_draws
            return {
                "n": test.n,
                "mean_d": test.mean_difference,
                "lower_95_one_sided": test.lower_mean_difference(),
                "interval_90": [draws[int(0.05 * test.draws)], draws[int(0.95 * test.draws) - 1]],
                "skill": test.skill,
                "p_value": test.p_value,
                "dm_p_value": None if math.isnan(test.dm_p_value) else test.dm_p_value,
            }

        result = {
            "days": len(group),
            "crps": {arm: sum(crps[arm][d] for d in group) / len(group) for arm in ("without", "with", "B1")},
            "crps_with_vs_without": paired(main),
            "twcrps_with_vs_without": paired(twc),
            "skill_vs_B1": {"without": paired(s_without), "with": paired(s_with)},
            "calibration": {},
        }
        for measure in ("inside_90", "inside_50", "above_95"):
            a = [cover["without"][measure][d] for d in group]
            b = [cover["with"][measure][d] for d in group]
            moves = [y - x for x, y in zip(a, b)]
            result["calibration"][measure] = {
                "without": sum(a) / len(a),
                "with": sum(b) / len(b),
                "move": sum(moves) / len(moves),
                "interval_90": list(_interval(moves)),
            }
        return result

    table = {name: tests(group) for name, group in groups.items() if len(group) > sp.HAC_LAG}
    headline = table["regime 2018-19"]["calibration"]["inside_90"]
    covers_zero = headline["interval_90"][0] <= 0.0 <= headline["interval_90"][1]
    document = {
        "issue": 633,
        "declaration": str(DECLARATION.relative_to(REPO)),
        "kill_rule": declaration["kill_rule_reading"],
        "scratch_panel_sha256": panel_sha256(args.scratch),
        "extended_panel_sha256": documents["with"][0]["panel_sha256"],
        "posting_instant": documents["with"][0]["posting_instant"],
        "first_fit_with_history": documents["with"][0]["blocks"][0],
        "first_fit_without": documents["without"][0]["blocks"][0],
        "decision_days": [days[0].isoformat(), days[-1].isoformat(), len(days)],
        "dropped_decision_days": len(declared) - len(days),
        "h4_killed_as_exploration": covers_zero,
        "groups": table,
    }
    args.output.write_text(json.dumps(document, indent=1) + "\n", encoding="utf-8")
    args.markdown.write_text(markdown(document), encoding="utf-8")
    print(json.dumps({"days": len(days), "h4_killed_as_exploration": covers_zero}))
    return 0


def markdown(document: dict) -> str:
    def f(value, digits=3):
        return f"{value:+.{digits}f}"

    lines = [
        "| group | days | CRPS without | CRPS with | d = without - with, 90% | twCRPS d, 90% | skill vs B1 without | skill vs B1 with |",
        "|---|---|---|---|---|---|---|---|",
    ]
    for name, cell in document["groups"].items():
        main, tw = cell["crps_with_vs_without"], cell["twcrps_with_vs_without"]
        lines.append(
            f"| {name} | {cell['days']} | {cell['crps']['without']:.3f} | {cell['crps']['with']:.3f} | "
            f"{f(main['mean_d'])} [{f(main['interval_90'][0])}, {f(main['interval_90'][1])}] | "
            f"{f(tw['mean_d'])} [{f(tw['interval_90'][0])}, {f(tw['interval_90'][1])}] | "
            f"{f(cell['skill_vs_B1']['without']['skill'])} | {f(cell['skill_vs_B1']['with']['skill'])} |"
        )
    lines += [
        "",
        "| group | inside 90%: without → with, move [90%] | inside 50%: without → with, move [90%] | above q0.95: without → with, move [90%] |",
        "|---|---|---|---|",
    ]
    for name, cell in document["groups"].items():
        parts = []
        for measure in ("inside_90", "inside_50", "above_95"):
            c = cell["calibration"][measure]
            parts.append(
                f"{c['without']:.3f} → {c['with']:.3f}, {f(c['move'])} [{f(c['interval_90'][0])}, {f(c['interval_90'][1])}]"
            )
        lines.append(f"| {name} | " + " | ".join(parts) + " |")
    return "\n".join(lines) + "\n"


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    commands = parser.add_subparsers(dest="command", required=True)
    run = commands.add_parser("forecasts")
    run.add_argument("--panel", type=Path, required=True)
    run.add_argument("--arm", choices=ARMS, required=True)
    run.add_argument("--horizon", type=int, required=True)
    run.add_argument("--output", type=Path, required=True)
    run.add_argument("--inputs", choices=("declared", "workbook"), default="declared")
    run.set_defaults(handler=forecasts_command)
    score = commands.add_parser("score")
    score.add_argument("--scratch", type=Path, required=True)
    score.add_argument("--runs", type=Path, required=True)
    score.add_argument("--output", type=Path, required=True)
    score.add_argument("--markdown", type=Path, required=True)
    score.add_argument("--suffix", default="", help="`_wb` scores the workbook-only sensitivity")
    score.set_defaults(handler=score_command)
    args = parser.parse_args(argv)
    return int(args.handler(args) or 0)


if __name__ == "__main__":
    raise SystemExit(main())
