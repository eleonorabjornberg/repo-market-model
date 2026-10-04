"""Score the live record (#215), only on its pre-registered dates.

Pre-registered by Eleonora's decision of 3 October 2026 (#215), before any day
was logged:

* **Scoring dates:** 2027-04-01, 2027-10-01, then every 1 October. On each,
  every logged day whose target day is in the outcome panel and before the
  scoring date is scored, cumulatively from the first logged day. On any other
  date this script refuses to run (`ValueError`).
* **The primary result** (Eleonora's ruling of 4 October 2026 on #215): the
  CRPS of the published distribution (#169's gbm with nested conformal PID)
  against as-of persistence's, at h = 1, both read from each day's file alone
  (`crps_from_record`). The pass rule, its labels and the block-10 sensitivity
  interval are the final test's CRPS cell's (#220, #221): the mean paired
  difference (persistence - published) above 0 and its 90% lower bound above
  0 (`crps_verdict`, `crps_result`, the final test's own functions). CRPS at
  h = 2 to 5 is reported only, and each of its cells carries, next to its
  verdict label, Eleonora's label of 4 October 2026 (#229) verbatim
  (`NOT_EVIDENCE`): "different model from h = 1, and as-of persistence does
  not widen with horizon, so this comparison favours the model; not evidence."
* **Reported only:** Brier for each event target (+5 bp, +10 bp, #139's plain
  leap), horizon and model, paired against each baseline (baseline minus
  model, a positive mean favouring the model), with a 90% stationary-bootstrap
  interval, split by regime and pressure-day type where the cells allow. A
  target is scored only if the scored period holds at least
  `onset.MINIMUM_EVENTS` events of it; below that it is reported as
  inconclusive, with no paired figure.
* **The primary result's verdict** is fixed at the first scoring date that
  scores any day (CRPS has no minimum event count: every day counts). Every
  later date is an update and never replaces it (`headline_status`).
* **The lockbox:** logged days are blind-tier days. Until the drafted amendment
  (`docs/decisions/drafts/lockbox-live-record.md`) is merged into
  `docs/decisions/lockbox.md`, this script refuses to run at all.

Results are published whatever they show, as a new record:

    PYTHONPATH=src python3 scripts/live_score.py --date YYYY-MM-DD --live-dir LIVE \\
        --panel PANEL --output OUT.json [--previous EARLIER.json ...]
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import date
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))

from repo_model import onset  # noqa: E402
from repo_model.metrics import crps_from_quantiles, stationary_bootstrap_interval  # noqa: E402
from repo_model.baseline import _seed_from  # noqa: E402
from repo_model.data import exceeds_bp, load_daily_panel  # noqa: E402
from repo_model.evaluation_splits import load_split_declaration  # noqa: E402

LOCKBOX = REPO / "docs" / "decisions" / "lockbox.md"
SPLITS = REPO / "metadata" / "evaluation_splits.json"
#: The heading the drafted amendment carries; the guard reads it in lockbox.md.
AMENDMENT_HEADING = "## Amendment: the live record (#215)"
FIRST_SCORING_DATES = (date(2027, 4, 1), date(2027, 10, 1))
#: The live record's primary result (ruling of 4 October 2026 on #215).
HEADLINE = {"target": "crps", "horizon": 1}
HORIZONS = (1, 2, 3, 4, 5)
#: Each target, the baselines it is paired with.
BASELINES = {
    "+5bp": ("persistence_logistic", "calendar_climatology"),
    "+10bp": ("persistence_logistic", "calendar_climatology"),
    "leap": (onset.LEAP_PERSISTENCE_LOGISTIC, onset.LEAP_CALENDAR_CLIMATOLOGY),
}
SIGN = "paired = Brier(baseline) - Brier(model) per day; a positive mean favours the model"
#: Eleonora's ruling of 4 October 2026 (#229), verbatim: every h = 2 to 5 CRPS
#: cell carries it, next to its verdict label. At h = 2 to 5 the published
#: distribution is pressure model v1's declaration, not the CRPS record's, and
#: as-of persistence's quantiles are the same at every horizon.
NOT_EVIDENCE = ("different model from h = 1, and as-of persistence does not widen with "
                "horizon, so this comparison favours the model; not evidence.")
CRPS_SIGN = ("paired = CRPS(persistence) - CRPS(published) per day; a positive mean favours "
             "the published distribution")


def _final_test():
    from importlib.util import module_from_spec, spec_from_file_location

    spec = spec_from_file_location("live_score_final_test", REPO / "scripts" / "final_test_preregistration.py")
    module = module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


#: The final test's CRPS cell (#220, #221): its pass rule, labels and settings.
final_test = _final_test()
crps_verdict = final_test.crps_verdict
crps_result = final_test.crps_result


def is_scoring_date(day: date) -> bool:
    if day in FIRST_SCORING_DATES:
        return True
    return day.year >= 2028 and (day.month, day.day) == (10, 1)


def require_scoring_date(day: date) -> None:
    if not is_scoring_date(day):
        raise ValueError(
            f"{day} is not a scoring date: the live record is scored on 2027-04-01, "
            f"2027-10-01 and every 1 October after, and on no other date (#215)"
        )


def require_amendment(path: Path = LOCKBOX) -> None:
    """Refuse to score until the lockbox amendment is merged into `path`."""

    text = Path(path).read_text(encoding="utf-8")
    if AMENDMENT_HEADING not in text.splitlines():
        raise ValueError(
            f"{path} carries no '{AMENDMENT_HEADING}': the live record's days are "
            f"blind-tier days, opened only once Eleonora merges the amendment"
        )


def headline_status(day: date, *, days: int, previous) -> str:
    """`inconclusive`, `headline_verdict` or `update`, for the primary result on `day`.

    `previous` is the earlier scoring results, each with its `date` and
    `headline_status`. The verdict is fixed once, at the first date whose
    primary cell scores any day (CRPS has no minimum event count); every result
    after it is an update, whatever it scores.

    Raises:
        ValueError: if a previous result is dated on or after `day`.
    """

    for result in previous:
        if date.fromisoformat(result["date"]) >= day:
            raise ValueError(
                f"a previous result is dated {result['date']}, not before {day}"
            )
    if any(result["headline_status"] in ("headline_verdict", "update") for result in previous):
        return "update"
    if days > 0:
        return "headline_verdict"
    return "inconclusive"


def crps_from_record(record, side: str, h: int, outcome: float) -> float:
    """One day's CRPS for `side` at horizon `h`, from the day's file alone.

    Raises:
        ValueError: if the file carries no such distribution.
    """

    block = record.get("distributions") or {}
    try:
        levels = block["levels"]
        quantiles = block[side]["quantiles_bps"][str(h)]
    except (KeyError, TypeError) as error:
        raise ValueError(f"the file carries no {side} distribution at h={h}") from error
    return crps_from_quantiles(levels, quantiles, outcome)


def score_crps(records, rows, splits, day: date) -> dict:
    """The CRPS cells, cumulatively over `records`: h = 1 primary, h = 2 to 5 reported only."""

    by_date = {row.date: row for row in rows}
    out = {}
    for h in HORIZONS:
        days, published, persistence, regimes, types = [], [], [], [], []
        for record in records:
            when = date.fromisoformat(record["targets"][h - 1]["target_date"])
            if when >= day or when not in by_date:
                continue
            row = by_date[when]
            days.append(when)
            published.append(crps_from_record(record, "published", h, row.spread_bps))
            persistence.append(crps_from_record(record, "persistence", h, row.spread_bps))
            try:
                regimes.append(splits.regime(when))
            except ValueError:
                regimes.append("undeclared")
            types.append(splits.day_type(row.values))
        primary = h == HEADLINE["horizon"]
        cell = {"days": len(days), "role": "primary" if primary else "reported only",
                "first": days[0].isoformat() if days else None,
                "last": days[-1].isoformat() if days else None,
                "sign_convention": CRPS_SIGN}
        if not primary:
            cell["verdict_label"] = NOT_EVIDENCE
        if not days:
            cell["result" if primary else "note"] = "inconclusive" if primary else "no scored day"
            out[f"crps/h{h}"] = cell
            continue
        differences = [a - b for a, b in zip(persistence, published)]
        seed = _seed_from((str(day), "crps", str(h)))
        block = final_test.CRPS_BLOCK_LENGTH + (h - 1)

        def mean_of(indices):
            return sum(differences[i] for i in indices) / len(indices)

        def interval(block_length):
            lower, upper = stationary_bootstrap_interval(
                mean_of, len(differences), block_length=block_length, seed=seed,
                replications=onset.REPLICATIONS, level=onset.LEVEL,
            )
            return {"lower": lower, "upper": upper, "level": onset.LEVEL,
                    "method": "stationary_bootstrap", "block_length": block_length,
                    "replications": onset.REPLICATIONS, "seed": seed}

        cell.update(
            {
                "crps_persistence_bps": sum(persistence) / len(days),
                "crps_published_bps": sum(published) / len(days),
                "mean_difference_bps": mean_of(range(len(days))),
                "interval": interval(block),
                "sensitivity_interval": interval(final_test.CRPS_SENSITIVITY_BLOCK_LENGTH),
            }
        )
        every = list(range(len(days)))
        for label, keys in (("by_regime", regimes), ("by_day_type", types)):
            cell[label] = {}
            for key in sorted(set(keys)):
                positions = [k for k in every if keys[k] == key]
                cell[label][key] = (
                    onset.paired_difference(persistence, published, positions,
                                            block_length=block, seed=_seed_from((str(day), "crps", str(h), key)))
                    if len(positions) >= 2 else {"days": len(positions), "note": "too few days"}
                )
        cell["verdict"] = crps_verdict(cell)
        if primary:
            cell["result"] = crps_result(cell["verdict"])
        out[f"crps/h{h}"] = cell
    return out


def _outcome(target, cell_name, spread):
    if cell_name == "leap":
        return 1 if onset.whole_bp(spread) - target["anchor_spread_bp"] > target["leap_threshold_bp"] else 0
    return 1 if exceeds_bp(spread, float(cell_name[1:-2])) else 0


def _paired(baseline, model, positions, h, *parts):
    return onset.paired_difference(
        baseline, model, positions, block_length=h,
        seed=_seed_from(tuple(str(part) for part in parts)),
    )


def score(records, rows, splits, day: date) -> dict:
    """Every Brier cell, cumulatively over `records`, on the outcomes in `rows`: reported only."""

    by_date = {row.date: row for row in rows}
    out = {"cells": {}}
    for cell_name, baselines in BASELINES.items():
        for h in HORIZONS:
            days, outcomes, model, bench, regimes, types = [], [], {}, {b: [] for b in baselines}, [], []
            for record in records:
                target = record["targets"][h - 1]
                when = date.fromisoformat(target["target_date"])
                if when >= day or when not in by_date:
                    continue
                row = by_date[when]
                days.append(when.isoformat())
                outcomes.append(_outcome(target, cell_name, row.spread_bps))
                for name, entry in record["models"].items():
                    model.setdefault(name, []).append(entry["forecasts"][str(h)][cell_name])
                for name in baselines:
                    bench[name].append(record["baselines"][name]["forecasts"][str(h)][cell_name])
                try:
                    regimes.append(splits.regime(when))
                except ValueError:
                    regimes.append("undeclared")
                types.append(splits.day_type(row.values))
            events = sum(outcomes)
            cell = {"days": len(days), "events": events, "first": days[0] if days else None,
                    "last": days[-1] if days else None, "models": {}, "role": "reported only"}
            if events < onset.MINIMUM_EVENTS:
                cell["result"] = "inconclusive"
                cell["reason"] = f"{events} events, below the minimum of {onset.MINIMUM_EVENTS}"
                out["cells"][f"{cell_name}/h{h}"] = cell
                continue
            losses = {name: [(p - y) ** 2 for p, y in zip(column, outcomes)]
                      for name, column in {**model, **bench}.items()}
            every = list(range(len(days)))
            for name in model:
                entry = {"brier": sum(losses[name]) / len(days), "paired": {}}
                for b in baselines:
                    paired = {"all_days": _paired(losses[b], losses[name], every, h, day, cell_name, h, name, b)}
                    for label, keys in (("by_regime", regimes), ("by_day_type", types)):
                        paired[label] = {}
                        for key in sorted(set(keys)):
                            positions = [k for k in every if keys[k] == key]
                            paired[label][key] = (
                                _paired(losses[b], losses[name], positions, h, day, cell_name, h, name, b, key)
                                if len(positions) >= 2 else {"days": len(positions), "note": "too few days"}
                            )
                    entry["paired"][b] = paired
                cell["models"][name] = entry
            cell["baseline_brier"] = {b: sum(losses[b]) / len(days) for b in baselines}
            out["cells"][f"{cell_name}/h{h}"] = cell
    return out


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--date", required=True)
    parser.add_argument("--live-dir", required=True, type=Path)
    parser.add_argument("--panel", required=True, type=Path, help="the outcome panel")
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--previous", action="append", default=[], type=Path)
    args = parser.parse_args(argv)
    day = date.fromisoformat(args.date)
    require_scoring_date(day)
    require_amendment(LOCKBOX)
    if args.output.exists():
        raise ValueError(f"{args.output} exists: a result is published as a new record")

    from importlib.util import module_from_spec, spec_from_file_location

    spec = spec_from_file_location("live_record", REPO / "scripts" / "live_record.py")
    live = module_from_spec(spec)
    spec.loader.exec_module(live)
    records = []
    for path in sorted((args.live_dir / "live").glob("*.json")):
        record = json.loads(path.read_text(encoding="utf-8"))
        live.validate_record(record)
        if record.get("dry_run"):
            raise ValueError(f"{path} is a dry run, not a logged day")
        records.append(record)
    previous = [json.loads(path.read_text(encoding="utf-8")) for path in args.previous]
    rows = load_daily_panel(args.panel)
    splits = load_split_declaration(SPLITS)
    result = score(records, rows, splits, day)
    result["crps"] = score_crps(records, rows, splits, day)
    headline = result["crps"][f"{HEADLINE['target']}/h{HEADLINE['horizon']}"]
    result.update(
        {
            "date": day.isoformat(),
            "directive": "#215",
            "logged_days": [record["decision_day"] for record in records],
            "sign_convention": SIGN,
            "minimum_events": onset.MINIMUM_EVENTS,
            "headline": HEADLINE,
            "crps_sign_convention": CRPS_SIGN,
            "primary_result": headline.get("result"),
            "headline_status": headline_status(day, days=headline["days"], previous=previous),
        }
    )
    args.output.write_text(json.dumps(result, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(args.output), "headline_status": result["headline_status"]}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
