"""The 2018-19 shortfall of `+tailcap75`, and its combination with the off-risk-date floor (#610).

A scratch measurement, not a record: it writes JSON and Markdown to the paths it is given and nothing into `docs/runs/`. Nothing is
published, no day after 2025-12-31 is read (`docs/decisions/lockbox.md`; `require_unlocked`), and the live record and pin do not move.

Step 1 (`diagnose`, committed before any step 2 declaration) states how much of the best row's 2018-19 under-forecast at the first
lead comes from each of three things, from forecasts the repository already scores:

* the length of the training window at each 2018-19 refit: the same row, run again on a later stretch of the panel that holds exactly
  as many scored days (`later_window_start`), so that each refit trains on the same number of days as the 2018-19 refit it matches;
* the floor's own warm-up: the days on which `group_calibration.fit_floor` has too few earlier observable off-risk-date pairs to
  fit (`floor_warmup_blocks`);
* the scarcity state, as of the decision instant (never a hindsight regime label, ruling on #515).

    # the scratch panels and the row's forecasts are those of scripts/every_day_conditioning_601.py (OUT/cap_h?.json)
    # the later window: LATER.csv (scratch) and LATER_PUBLISHED.csv are the panels cut by `slice` at the start `diagnose` names
    PYTHONPATH=src python3 scripts/tailcap_floor_610.py slice --scratch AUG2.csv --published PUBLISHED.csv --output-dir LATER
    PYTHONPATH=src python3 scripts/tailcap_floor_610.py diagnose --panel PUBLISHED.csv --scratch AUG2.csv --cap 'OUT/cap_h{h}.json' \\
        --bench 'OUT/bench_h{h}.json' --later-cap LATER/cap_h1.json --later-scratch LATER/scratch.csv \\
        --output OUT/diagnosis.json --markdown OUT/diagnosis.md
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import random
import sys
from datetime import date, time
from pathlib import Path
from typing import Dict, List, Mapping, Optional, Sequence, Tuple

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))

from repo_model import group_calibration as gc, measurement_fields, probability_calibration as pc, pressure_judge as pj  # noqa: E402
from repo_model.baseline import climatology_exceedance, panel_sha256, rolling_exceedance_backtest  # noqa: E402
from repo_model.data import audit_panel, load_daily_panel  # noqa: E402
from repo_model.evaluation_splits import load_split_declaration  # noqa: E402
from repo_model.lockbox import require_unlocked  # noqa: E402
from repo_model.metrics import stationary_bootstrap_interval  # noqa: E402


def _load(name: str):
    spec = importlib.util.spec_from_file_location(f"{name}_script", REPO / "scripts" / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[f"{name}_script"] = module
    spec.loader.exec_module(module)
    return module


edc = _load("every_day_conditioning_601")
dr = _load("dist_roll_606")
ann = dr.ann
rds = dr.rds

SPLITS = REPO / "metadata" / "evaluation_splits.json"
CANDIDATES = dr.CANDIDATES
PARENT = edc.ROW
BEST = edc.VARIANTS["cap75"]
FIRST_REGIME = "2018-19"
LEADS = (1, 2, 3, 4, 5)
TAU = 5.0
SEED = 610


# -- the later window --------------------------------------------------------------------------------------


def later_window_start(rows: Sequence, scored_days: int, last: date, minimum_history: int) -> int:
    """The index of the first panel row of a later stretch that scores exactly `scored_days` days up to `last`.

    The stretch is cut so that its first scored day follows `minimum_history` rows and its last scored day is the row before `last`
    (the grid's last row has no label one day ahead; checked against the grid by `diagnose`): each refit of the row on it
    then trains on as many days as the refit of the same number it is matched with in 2018-19.

    Raises:
        ValueError: if `last` is not a panel row, or the panel is too short for the stretch.
    """

    dates = [row.date for row in rows]
    if last not in dates:
        raise ValueError(f"{last} is not a row of the panel")
    start = dates.index(last) - scored_days - minimum_history
    if start < 0:
        raise ValueError("the panel is too short for a later stretch of that many scored days")
    return start


def slice_rows_csv(source: Path, target: Path, first_day: date) -> int:
    """Write the panel rows from `first_day` on to `target` (same header); return the row count."""

    lines = source.read_text(encoding="utf-8").splitlines()
    header, body = lines[0], lines[1:]
    column = header.split(",").index("date")
    kept = [line for line in body if date.fromisoformat(line.split(",")[column]) >= first_day]
    target.write_text("\n".join([header] + kept) + "\n", encoding="utf-8")
    return len(kept)


# -- the floor's warm-up -----------------------------------------------------------------------------------


def _training_days_at(dates: Sequence[date], train_end: date) -> int:
    """The panel days a refit trained on: those at or before its last training label (nothing later is read)."""

    return sum(1 for day in dates if day <= train_end)


def floor_warmup_blocks(
    scored: Sequence[date],
    train_ends: Sequence[date],
    forecasts: Sequence[float],
    outcomes: Sequence[int],
    off_risk: Sequence[bool],
    labels: Sequence[str],
    panel_dates: Sequence[date],
) -> List[dict]:
    """Per refit block: the training days, the earlier off-risk pairs the floor could be fitted on, and the floors it would take.

    A block's pairs are the earlier off-risk-date scored days whose outcome was observable at its fit (`pc.past_positions`), as
    `gc.walk_forward_floor` takes them; `gc.fit_floor` returns None while they number fewer than the minimum.
    """

    out = []
    for start, stop, end in pc.blocks(scored, train_ends):
        past = [i for i in pc.past_positions(scored, train_ends, start) if off_risk[i]]
        pairs = [(scored[i], forecasts[i], outcomes[i], labels[i]) for i in past]
        pooled = gc.fit_floor(pairs, end)
        inside = [i for i in range(start, stop)]
        off = [i for i in inside if off_risk[i]]
        out.append({
            "first_day": scored[start].isoformat(),
            "last_day": scored[stop - 1].isoformat(),
            "train_end": end.isoformat(),
            "training_days": _training_days_at(panel_dates, end),
            "earlier_off_risk_pairs": len(pairs),
            "earlier_off_risk_pressure_days": sum(y for _, _, y, _ in pairs),
            "pooled_floor": pooled,
            "scored_days": len(inside),
            "off_risk_days": len(off),
            "off_risk_pressure_days": sum(outcomes[i] for i in off),
            "off_risk_realised": (sum(outcomes[i] for i in off) / len(off)) if off else None,
            "off_risk_predicted": (sum(forecasts[i] for i in off) / len(off)) if off else None,
        })
    return out


# -- the shortfall -----------------------------------------------------------------------------------------


def mean_shortfall(forecasts: Sequence[float], outcomes: Sequence[int]) -> float:
    """Realised minus predicted rate of a pressure day."""

    if not forecasts or len(forecasts) != len(outcomes):
        raise ValueError("forecasts and outcomes must be non-empty and of one length")
    return (sum(outcomes) - sum(forecasts)) / len(outcomes)


def shortfall_cell(forecasts: Sequence[float], outcomes: Sequence[int], *, block_length: float, replications: int, seed: int) -> dict:
    n = len(outcomes)
    diffs = [y - p for p, y in zip(forecasts, outcomes)]
    lower, upper = stationary_bootstrap_interval(
        lambda idx: sum(diffs[i] for i in idx) / len(idx), n, block_length=block_length, seed=seed, replications=replications
    )
    return {
        "days": n,
        "pressure_days": sum(outcomes),
        "predicted": sum(forecasts) / n,
        "realised": sum(outcomes) / n,
        "shortfall": mean_shortfall(forecasts, outcomes),
        "lower": lower,
        "upper": upper,
    }


def difference_interval(a: Sequence[float], b: Sequence[float], *, block_length: float, replications: int, seed: int) -> Tuple[float, float, float]:
    """Mean of `a` less mean of `b` (two independent stretches), with a 90% stationary-bootstrap interval from independent resamples."""

    from repo_model.metrics import stationary_bootstrap_indices

    rng = random.Random(seed)
    draws = []
    for _ in range(replications):
        ia = stationary_bootstrap_indices(len(a), block_length, rng)
        ib = stationary_bootstrap_indices(len(b), block_length, rng)
        draws.append(sum(a[i] for i in ia) / len(ia) - sum(b[i] for i in ib) / len(ib))
    draws.sort()
    point = sum(a) / len(a) - sum(b) / len(b)
    return point, draws[int(0.05 * (len(draws) - 1))], draws[int(round(0.95 * (len(draws) - 1)))]


# -- the grid ----------------------------------------------------------------------------------------------


def grid_and_folds(rows, scoring: Mapping, h: int, last: date):
    """The scored days, each block's last training label and the +5 bp outcomes (a backtest whose forecasts are not used)."""

    registry = measurement_fields.load_registry()
    report = rolling_exceedance_backtest(
        rows, predictor=climatology_exceedance(scoring["minimum_history"]), model_name="grid", features=("spread_bps",), registry=registry,
        decision_time=time.fromisoformat(scoring["decision_time"]), taus=(TAU,), minimum_history=scoring["minimum_history"],
        refit_every=scoring["refit_every"], end=last, horizon=h,
    )
    scored = list(report.scored_dates)
    train_ends = [fold.train_end for fold in report.folds]
    outcomes = list(report.at_tau(report.taus.index(TAU))[2])
    return scored, train_ends, outcomes


def _cap_forecast(path: Path, name: str, panel_digest: Optional[str]) -> Dict[str, float]:
    document = json.loads(Path(path).read_text(encoding="utf-8"))
    if panel_digest is not None and document["panel_sha256"] != panel_digest:
        raise SystemExit(f"{path} was scored on another panel")
    return document["forecasts"][name]["5"]


def regime_of(splits, day: date) -> str:
    return splits.regime(day)


def diagnose_command(args) -> int:
    declaration = pj.load_declaration()
    last = declaration.last_day
    require_unlocked([last], where="tailcap_floor_610")
    dr.require_scored_window(last)
    scoring = json.loads((REPO / "metadata" / "every_day_conditioning_601.json").read_text(encoding="utf-8"))["scoring"]
    rows = load_daily_panel(args.scratch)
    audit_panel(rows)
    splits = load_split_declaration(SPLITS)
    by_date = {row.date: row for row in rows}
    panel_dates = [row.date for row in rows]
    block, reps = declaration.block_length, declaration.replications
    digest = panel_sha256(args.panel)

    out: Dict[str, dict] = {"row": BEST, "panel_sha256": digest, "threshold_bp": TAU, "leads": {}}
    for h in LEADS:
        forecast_by_day = _cap_forecast(Path(str(args.cap).format(h=h)), BEST, digest)
        scored, train_ends, outcomes = grid_and_folds(rows, scoring, h, last)
        days = [d.isoformat() for d in scored]
        if sorted(forecast_by_day) != days:
            raise SystemExit(f"h={h}: the row's scored days are not the grid's")
        p = [forecast_by_day[d] for d in days]
        off = [not ann.risk_flag(splits, by_date[d].values, True) for d in scored]
        regimes = [regime_of(splits, d) for d in scored]
        first = [k for k, r in enumerate(regimes) if r == FIRST_REGIME]
        states = dr._load("pressure_judge")._scarcity_states(h, last)
        labels = [gc.scarcity_state_label(states.get(d)) for d in scored]
        cell: Dict[str, object] = {}
        cell["regime"] = shortfall_cell([p[k] for k in first], [outcomes[k] for k in first], block_length=block, replications=reps, seed=SEED)
        cell["all_regimes"] = {
            label: shortfall_cell([p[k] for k, r in enumerate(regimes) if r == label], [outcomes[k] for k, r in enumerate(regimes) if r == label],
                                  block_length=block, replications=reps, seed=SEED)
            for label in sorted(set(regimes)) if sum(1 for r in regimes if r == label) > 1
        }
        n = len(first)
        total = sum(outcomes[k] - p[k] for k in first)
        by_type = {}
        for name, selector in (("risk_date", lambda k: not off[k]), ("not_risk_date", lambda k: off[k])):
            idx = [k for k in first if selector(k)]
            by_type[name] = {"days": len(idx), "pressure_days": sum(outcomes[k] for k in idx),
                             "contribution": sum(outcomes[k] - p[k] for k in idx) / n,
                             "share": (sum(outcomes[k] - p[k] for k in idx) / total) if total > 1e-12 else None}
        cell["by_day_type"] = by_type
        blocks_ = floor_warmup_blocks(scored, train_ends, p, outcomes, off, labels, panel_dates)
        in_first = [b for b in blocks_ if regime_of(splits, date.fromisoformat(b["first_day"])) == FIRST_REGIME or regime_of(splits, date.fromisoformat(b["last_day"])) == FIRST_REGIME]
        cell["blocks_2018_19"] = in_first
        # (2) the floor's warm-up: days with no floor fitted, and what they carry
        no_floor_days = {k for b, (start, stop, _end) in zip(blocks_, pc.blocks(scored, train_ends)) if b["pooled_floor"] is None for k in range(start, stop)}
        warm = [k for k in first if off[k] and k in no_floor_days]
        fitted = [k for k in first if off[k] and k not in no_floor_days]
        cell["floor_warmup"] = {
            "off_risk_days_without_a_floor": len(warm),
            "off_risk_days_with_a_floor": len(fitted),
            "pressure_days_without_a_floor": sum(outcomes[k] for k in warm),
            "pressure_days_with_a_floor": sum(outcomes[k] for k in fitted),
            "contribution_without_a_floor": sum(outcomes[k] - p[k] for k in warm) / n,
            "contribution_with_a_floor": sum(outcomes[k] - p[k] for k in fitted) / n,
        }
        # (3) the scarcity state, as of the decision instant
        by_state = {}
        for label in sorted(set(labels[k] for k in first)):
            idx = [k for k in first if labels[k] == label]
            by_state[label] = {"days": len(idx), "pressure_days": sum(outcomes[k] for k in idx),
                               "predicted": sum(p[k] for k in idx) / len(idx), "realised": sum(outcomes[k] for k in idx) / len(idx),
                               "contribution": sum(outcomes[k] - p[k] for k in idx) / n,
                               "share": (sum(outcomes[k] - p[k] for k in idx) / total) if total > 1e-12 else None}
        cell["by_state"] = by_state
        out["leads"][str(h)] = cell
        if h == 1:
            first_p, first_y = [p[k] for k in first], [outcomes[k] for k in first]
            n_first = len(first)
            out["scored_days_2018_19_h1"] = n_first
            out["first_scored_day"] = scored[0].isoformat()
            out["first_regime_last_day"] = scored[first[-1]].isoformat()
            # (1) the training window: the same row on a later stretch with exactly as many scored days
            later = None
            if args.later_cap:
                later_rows = load_daily_panel(args.later_scratch)
                audit_panel(later_rows)
                later_scored, later_ends, later_y = grid_and_folds(later_rows, scoring, 1, last)
                later_days = [d.isoformat() for d in later_scored]
                later_p_by_day = _cap_forecast(Path(args.later_cap), BEST, None)
                if sorted(later_p_by_day) != later_days:
                    raise SystemExit("the later stretch's scored days are not its grid's")
                later_p = [later_p_by_day[d] for d in later_days]
                if len(later_days) != n_first:
                    raise SystemExit(f"the later stretch scores {len(later_days)} days, 2018-19 scores {n_first}")
                later_off = [not ann.risk_flag(splits, {r.date: r for r in later_rows}[d].values, True) for d in later_scored]
                later_cell = shortfall_cell(later_p, later_y, block_length=block, replications=reps, seed=SEED)
                later_cell["first_day"], later_cell["last_day"] = later_days[0], later_days[-1]
                later_cell["not_risk_date_pressure_days"] = sum(y for y, o in zip(later_y, later_off) if o)
                diffs_first = [y - q for q, y in zip(first_p, first_y)]
                diffs_later = [y - q for q, y in zip(later_p, later_y)]
                point, lo, hi = difference_interval(diffs_first, diffs_later, block_length=block, replications=reps, seed=SEED)
                later_blocks = floor_warmup_blocks(later_scored, later_ends, later_p, later_y, later_off, ["unknown"] * len(later_days), [r.date for r in later_rows])
                later = {"cell": later_cell, "difference_2018_19_less_later": {"point": point, "lower": lo, "upper": hi},
                         "training_days_first_and_last_block": [later_blocks[0]["training_days"], later_blocks[-1]["training_days"]],
                         "blocks": later_blocks}
                own = [b["training_days"] for b in in_first]
                out["training_days_2018_19_first_and_last_block"] = [own[0], own[-1]]
            out["later_window"] = later
    args.output.write_text(json.dumps(out, indent=1, sort_keys=True, default=str) + "\n", encoding="utf-8")
    if args.markdown:
        args.markdown.write_text(diagnosis_markdown(out), encoding="utf-8")
    print(json.dumps({"output": str(args.output)}))
    return 0


def _f(x, digits=4):
    return "n/a" if x is None else f"{x:+.{digits}f}"


def diagnosis_markdown(result: dict) -> str:
    c = result["leads"]["1"]
    cell = c["regime"]
    lines = [
        "# The 2018-19 shortfall of `+tailcap75`, step 1 (#610)",
        "",
        f"Row `{result['row']}`, +5 bp, h = 1, scored days of {FIRST_REGIME} ({cell['days']} days, {cell['pressure_days']} pressure days). "
        "Generated by `scripts/tailcap_floor_610.py diagnose`.",
        "",
        f"Predicted {cell['predicted']:.4f}, realised {cell['realised']:.4f}, realised minus predicted {_f(cell['shortfall'])} [{_f(cell['lower'])}, {_f(cell['upper'])}].",
        "",
        "## By day type",
        "",
        "| day type | days | pressure days | contribution to the shortfall | share |",
        "|---|---|---|---|---|",
    ]
    for name, t in c["by_day_type"].items():
        share = "n/a" if t["share"] is None else f"{t['share']:.0%}"
        lines.append(f"| {name} | {t['days']} | {t['pressure_days']} | {_f(t['contribution'])} | {share} |")
    w = c["floor_warmup"]
    lines += [
        "",
        "## The floor's own warm-up",
        "",
        f"The floor is fitted from at least {gc.GROUP_MINIMUM_PAIRS} earlier observable off-risk-date days. Off-risk days with no floor yet: {w['off_risk_days_without_a_floor']} "
        f"({w['pressure_days_without_a_floor']} pressure days, contribution {_f(w['contribution_without_a_floor'])}); with a floor: {w['off_risk_days_with_a_floor']} "
        f"({w['pressure_days_with_a_floor']} pressure days, contribution {_f(w['contribution_with_a_floor'])}).",
        "",
        "| block first day | train end | training days | earlier off-risk pairs | of them pressure days | pooled floor | off-risk days | off-risk pressure days | realised | predicted |",
        "|---|---|---|---|---|---|---|---|---|---|",
    ]
    for b in c["blocks_2018_19"]:
        floor = "none" if b["pooled_floor"] is None else f"{b['pooled_floor']:.3f}"
        real = "n/a" if b["off_risk_realised"] is None else f"{b['off_risk_realised']:.3f}"
        pred = "n/a" if b["off_risk_predicted"] is None else f"{b['off_risk_predicted']:.3f}"
        lines.append(f"| {b['first_day']} | {b['train_end']} | {b['training_days']} | {b['earlier_off_risk_pairs']} | {b['earlier_off_risk_pressure_days']} | {floor} | {b['off_risk_days']} | {b['off_risk_pressure_days']} | {real} | {pred} |")
    lines += ["", "## The scarcity state (as of the decision instant)", "", "| state | days | pressure days | predicted | realised | contribution | share |", "|---|---|---|---|---|---|---|"]
    for label, s in c["by_state"].items():
        share = "n/a" if s["share"] is None else f"{s['share']:.0%}"
        lines.append(f"| {label} | {s['days']} | {s['pressure_days']} | {s['predicted']:.4f} | {s['realised']:.4f} | {_f(s['contribution'])} | {share} |")
    later = result.get("later_window")
    lines += ["", "## The length of the training window", ""]
    if later:
        lc, diff = later["cell"], later["difference_2018_19_less_later"]
        lines += [
            f"The same row on a later stretch of exactly {lc['days']} scored days ({lc['first_day']} to {lc['last_day']}), each refit trained on as many days as the "
            f"matching 2018-19 refit (the first block trains on {result['training_days_2018_19_first_and_last_block'][0]} days and the last on "
            f"{result['training_days_2018_19_first_and_last_block'][1]}; the later stretch on {later['training_days_first_and_last_block'][0]} and {later['training_days_first_and_last_block'][1]}).",
            "",
            "| stretch | days | pressure days | predicted | realised | realised minus predicted [90%] |",
            "|---|---|---|---|---|---|",
            f"| {FIRST_REGIME} | {cell['days']} | {cell['pressure_days']} | {cell['predicted']:.4f} | {cell['realised']:.4f} | {_f(cell['shortfall'])} [{_f(cell['lower'])}, {_f(cell['upper'])}] |",
            f"| later ({lc['first_day']} to {lc['last_day']}) | {lc['days']} | {lc['pressure_days']} | {lc['predicted']:.4f} | {lc['realised']:.4f} | {_f(lc['shortfall'])} [{_f(lc['lower'])}, {_f(lc['upper'])}] |",
            "",
            f"{FIRST_REGIME} less later: {_f(diff['point'])} [{_f(diff['lower'])}, {_f(diff['upper'])}] (independent resamples).",
        ]
    else:
        lines.append("No later stretch was run.")
    return "\n".join(lines) + "\n"


def slice_command(args) -> int:
    declaration = pj.load_declaration()
    last = declaration.last_day
    require_unlocked([last], where="tailcap_floor_610")
    scoring = json.loads((REPO / "metadata" / "every_day_conditioning_601.json").read_text(encoding="utf-8"))["scoring"]
    rows = load_daily_panel(args.scratch)
    scored, _ends, _y = grid_and_folds(rows, scoring, 1, last)
    first_regime = sum(1 for d in scored if regime_of(load_split_declaration(SPLITS), d) == FIRST_REGIME)
    start = later_window_start(rows, first_regime, last, scoring["minimum_history"])
    first_day = rows[start].date
    args.output_dir.mkdir(parents=True, exist_ok=True)
    kept = slice_rows_csv(args.scratch, args.output_dir / "scratch.csv", first_day)
    kept_pub = slice_rows_csv(args.published, args.output_dir / "published.csv", first_day)
    print(json.dumps({"scored_days_2018_19": first_regime, "first_row": first_day.isoformat(), "scratch_rows": kept, "published_rows": kept_pub}))
    return 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = parser.add_subparsers(dest="command", required=True)
    s = sub.add_parser("slice")
    s.add_argument("--scratch", type=Path, required=True)
    s.add_argument("--published", type=Path, required=True)
    s.add_argument("--output-dir", type=Path, required=True)
    s.set_defaults(func=slice_command)
    d = sub.add_parser("diagnose")
    d.add_argument("--panel", type=Path, required=True)
    d.add_argument("--scratch", type=Path, required=True)
    d.add_argument("--cap", required=True)
    d.add_argument("--later-cap", type=Path)
    d.add_argument("--later-scratch", type=Path)
    d.add_argument("--output", type=Path, required=True)
    d.add_argument("--markdown", type=Path)
    d.set_defaults(func=diagnose_command)
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
