"""Directive #98's evidence: the published declaration with and without `effr_minus_iorb_bp`.

Two steps, both run from the repository root.

`score` runs `repo_model.cli exceedance-backtest` exactly as the command line
does, through `cli.main`, for one side of the pair, and also writes the per-day
probabilities the record does not carry: the model's and each benchmark's, at
every threshold, with the realized spread. It wraps the one function the
command calls, `rolling_exceedance_backtest`, to keep the reports it returns;
it changes nothing they contain.

`tables` reads the two exceedance records, their per-day files and the two
`compare --loss crps` records, and prints the PR's Markdown tables: the
next-day distribution against as-of persistence, P(> +5 bp) and P(> +10 bp)
against calendar climatology and the persistence-logistic benchmark, the
paired with-minus-without differences, each split by regime and pressure-day
type, and the onset view (scored days whose previous panel day was not above
+5 bp). Every interval is `metrics.stationary_bootstrap_interval`, with the
block length, level and replication count the records use.

The panel is the experiment panel: the published panel's columns plus `effr`,
built from `tests/fixtures/snapshots/funding_inputs/` and
`tests/fixtures/snapshots/nyfed_effr_inputs/`, and cut at 2025-12-31 so that no
day locked by `docs/decisions/lockbox.md` is scored. The PR description gives
the commands.

Nothing here is a published record, and nothing writes into `docs/runs/`.
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from repo_model import cli, cli_eval  # noqa: E402
from repo_model.evaluation_splits import load_split_declaration  # noqa: E402
from repo_model.metrics import stationary_bootstrap_interval  # noqa: E402

PUBLISHED = (
    "reserve_balances",
    "sofr_p25",
    "sofr_p75",
    "sofr_volume",
    "spread_bps",
    "tbill_13w",
    "tbill_4w",
    "tga",
    "treasury_settlement",
)
FEATURE = "effr_minus_iorb_bp"
BENCHMARKS = ("calendar_climatology", "persistence_logistic")
#: The interval settings every published record uses.
LEVEL = 0.9
BLOCK = 2
REPLICATIONS = 2000
SEED = 98
ONSET_BP = 5.0
LOCKBOX_START = date(2026, 1, 1)


def _score(args):
    features = PUBLISHED + ((FEATURE,) if args.side == "with" else ())
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    record = out / f"exceedance_{args.side}.json"
    argv = [
        "exceedance-backtest",
        "--panel", str(args.panel),
        "--thresholds", "metadata/stress_thresholds.json",
        "--registry", "metadata/sources.json",
        "--decision-time", "16:00",
        "--minimum-history", "61",
        "--refit-every", "21",
        "--splits", "metadata/evaluation_splits.json",
        "--model", "gbm",
        "--calibration", "cross_conformal",
        "--calibration-folds", "5",
        "--report", str(record),
    ]
    for name in features:
        argv += ["--feature", name]
    for name in BENCHMARKS:
        argv += ["--benchmark", name]

    reports = []
    real = cli_eval.rolling_exceedance_backtest

    def keep(*a, **k):
        report = real(*a, **k)
        reports.append(report)
        return report

    cli_eval.rolling_exceedance_backtest = keep
    try:
        code = cli.main(argv)
    finally:
        cli_eval.rolling_exceedance_backtest = real
    if code != 0:
        raise SystemExit(code)
    model, *benchmarks = reports
    days = []
    for index, when in enumerate(model.scored_dates):
        if when >= LOCKBOX_START:
            raise SystemExit(f"{when} is locked by docs/decisions/lockbox.md")
        entry = {
            "date": when.isoformat(),
            "realized_bps": model.realized_bps[index],
            "gbm": list(model.forecast[index]),
        }
        for report in benchmarks:
            if report.scored_dates[index] != when:
                raise SystemExit("benchmark and model are not paired")
            entry[report.model_name] = list(report.forecast[index])
        days.append(entry)
    (out / f"exceedance_{args.side}_per_day.json").write_text(
        json.dumps({"taus": list(model.taus), "days": days}, indent=1) + "\n"
    )
    return 0


def _interval(series, seed_offset=0):
    if len(series) < 2:
        return (float("nan"), float("nan"))
    return stationary_bootstrap_interval(
        lambda idx: sum(series[i] for i in idx) / len(idx),
        len(series),
        block_length=BLOCK,
        seed=SEED + seed_offset,
        replications=REPLICATIONS,
        level=LEVEL,
    )


def _mean(series):
    return sum(series) / len(series) if series else float("nan")


def _row(label, series, seed_offset=0):
    lower, upper = _interval(series, seed_offset)
    return f"| {label} | {len(series)} | {_mean(series):+.4f} | [{lower:+.4f}, {upper:+.4f}] |"


def _split_rows(title, dates, diffs, regimes, day_types):
    lines = [f"**{title}**", "", "| Slice | Days | Mean | 90% interval |", "|---|---|---|---|"]
    lines.append(_row("pooled", diffs))
    labels = sorted(set(regimes.values()))
    for offset, label in enumerate(labels, start=1):
        lines.append(_row(f"regime {label}", [d for w, d in zip(dates, diffs) if regimes.get(w) == label], offset))
    types = [t for t in ("quarter_end", "month_end", "tax_date", "ordinary") if t in set(day_types.values())]
    for offset, label in enumerate(types, start=20):
        lines.append(_row(f"day type {label}", [d for w, d in zip(dates, diffs) if day_types.get(w) == label], offset))
    return lines


def _tables(args):
    out = Path(args.dir)
    panel = {}
    with open(args.panel, newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            panel[date.fromisoformat(row["date"])] = row
    panel_dates = sorted(panel)
    previous = {panel_dates[i]: panel_dates[i - 1] for i in range(1, len(panel_dates))}

    def spread(when):
        row = panel[when]
        return 100.0 * (float(row["sofr"]) - float(row["iorb"]))

    splits = load_split_declaration(ROOT / "metadata" / "evaluation_splits.json")

    def day_type(when):
        values = {
            key: (None if value == "" else float(value))
            for key, value in panel[when].items()
            if key != "date"
        }
        return splits.day_type(values)

    regime = splits.regime

    lines = []
    # --- the next-day distribution, CRPS --------------------------------
    pair = json.loads((out / "cmp_with_vs_without.json").read_text())
    pers = json.loads((out / "cmp_pers_arx.json").read_text())
    p_by_date = {
        date.fromisoformat(o["scored_date"]): o["loss_a_bps"]
        for o in pers["comparison"]["per_origin"]
    }
    per = pair["comparison"]["per_origin"]
    dates = [date.fromisoformat(o["scored_date"]) for o in per]
    if max(dates) >= LOCKBOX_START:
        raise SystemExit("a locked day was scored")
    without = [o["loss_a_bps"] for o in per]
    with_ = [o["loss_b_bps"] for o in per]
    persistence = [p_by_date[w] for w in dates]
    regimes = {w: regime(w) for w in dates}
    types = {w: day_type(w) for w in dates}
    lines += [
        f"Scored window: {dates[0]} to {dates[-1]}, {len(dates)} days. "
        "No scored day is on or after 2026-01-01.",
        "",
        "### Next-day distribution: CRPS (bp), lower is better",
        "",
        "| Model | CRPS |",
        "|---|---|",
        f"| as-of persistence | {_mean(persistence):.4f} |",
        f"| published gbm, without | {_mean(without):.4f} |",
        f"| published gbm, with `{FEATURE}` | {_mean(with_):.4f} |",
        "",
        "Paired differences, positive favours the second-named model:",
        "",
    ]
    lines += _split_rows(
        "CRPS, without minus with", dates,
        [a - b for a, b in zip(without, with_)], regimes, types,
    )
    lines.append("")
    lines += _split_rows(
        "CRPS, persistence minus without", dates,
        [a - b for a, b in zip(persistence, without)], regimes, types,
    )
    lines.append("")
    lines += _split_rows(
        "CRPS, persistence minus with", dates,
        [a - b for a, b in zip(persistence, with_)], regimes, types,
    )
    lines.append("")
    onset = [i for i, w in enumerate(dates) if w in previous and spread(previous[w]) <= ONSET_BP]
    lines += _split_rows(
        f"Onset view (previous panel day not above +{ONSET_BP:g} bp): CRPS, without minus with",
        [dates[i] for i in onset], [without[i] - with_[i] for i in onset], regimes, types,
    )
    lines.append("")

    # --- pressure probabilities, Brier ----------------------------------
    sides = {}
    for side in ("without", "with"):
        sides[side] = json.loads((out / f"exceedance_{side}_per_day.json").read_text())
    taus = sides["without"]["taus"]
    days_without = sides["without"]["days"]
    days_with = sides["with"]["days"]
    edates = [date.fromisoformat(d["date"]) for d in days_without]
    if edates != [date.fromisoformat(d["date"]) for d in days_with]:
        raise SystemExit("the two sides are not on one grid")
    if max(edates) >= LOCKBOX_START:
        raise SystemExit("a locked day was scored")
    eregimes = {w: regime(w) for w in edates}
    etypes = {w: day_type(w) for w in edates}
    eonset = [i for i, w in enumerate(edates) if w in previous and spread(previous[w]) <= ONSET_BP]

    for tau in (5.0, 10.0):
        k = taus.index(tau)
        outcome = [1.0 if d["realized_bps"] > tau else 0.0 for d in days_without]

        def brier(days, key):
            return [(d[key][k] - y) ** 2 for d, y in zip(days, outcome)]

        b_without = brier(days_without, "gbm")
        b_with = brier(days_with, "gbm")
        b_clim = brier(days_without, "calendar_climatology")
        b_plog = brier(days_without, "persistence_logistic")
        lines += [
            f"### P(> +{tau:g} bp): Brier, lower is better",
            "",
            f"Events: {int(sum(outcome))} of {len(outcome)} scored days; "
            f"in the onset view {int(sum(outcome[i] for i in eonset))} of {len(eonset)}.",
            "",
            "| Model | Brier, all days | Brier, onset days |",
            "|---|---|---|",
        ]
        for label, series in (
            ("calendar climatology", b_clim),
            ("persistence-logistic", b_plog),
            ("published gbm, without", b_without),
            (f"published gbm, with `{FEATURE}`", b_with),
        ):
            lines.append(
                f"| {label} | {_mean(series):.5f} | {_mean([series[i] for i in eonset]):.5f} |"
            )
        lines.append("")
        for title, a, b in (
            ("without minus with", b_without, b_with),
            ("calendar climatology minus with", b_clim, b_with),
            ("persistence-logistic minus with", b_plog, b_with),
            ("calendar climatology minus without", b_clim, b_without),
            ("persistence-logistic minus without", b_plog, b_without),
        ):
            diffs = [x - y for x, y in zip(a, b)]
            lines += _split_rows(f"Brier at +{tau:g} bp, {title}", edates, diffs, eregimes, etypes)
            lines.append("")
            lines += _split_rows(
                f"Onset view: Brier at +{tau:g} bp, {title}",
                [edates[i] for i in eonset], [diffs[i] for i in eonset], eregimes, etypes,
            )
            lines.append("")
    print("\n".join(lines))
    return 0


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="step", required=True)
    score = sub.add_parser("score")
    score.add_argument("--side", choices=("with", "without"), required=True)
    score.add_argument("--panel", type=Path, required=True)
    score.add_argument("--out", type=Path, required=True)
    tables = sub.add_parser("tables")
    tables.add_argument("--dir", type=Path, required=True)
    tables.add_argument("--panel", type=Path, required=True)
    args = parser.parse_args(argv)
    return _score(args) if args.step == "score" else _tables(args)


if __name__ == "__main__":
    raise SystemExit(main())
