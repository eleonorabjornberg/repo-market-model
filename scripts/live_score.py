"""Score the live record (#215), only on its pre-registered dates.

Pre-registered by Eleonora's decision of 3 October 2026 (#215), before any day
was logged:

* **Scoring dates:** 2027-04-01, 2027-10-01, then every 1 October. On each,
  every logged day whose target day is in the outcome panel and before the
  scoring date is scored, cumulatively from the first logged day. On any other
  date this script refuses to run (`ValueError`).
* **Metrics:** Brier for each target, horizon and model, paired against each
  baseline (baseline minus model, a positive mean favouring the model), with a
  90% stationary-bootstrap interval, split by regime and pressure-day type
  where the cells allow.
* **The headline cell** is the plain leap at h = 1 against each baseline.
  Every other cell is reported, not headlined.
* **The minimum-event rule:** a target is scored only if the scored period
  holds at least `onset.MINIMUM_EVENTS` events of it; below that it is
  reported as inconclusive, with no paired figure.
* **The headline verdict** is fixed at the first scoring date at which the
  headline cell meets the minimum. Every later date is an update and never
  replaces it; earlier dates report the cell as inconclusive
  (`headline_status`).
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
from repo_model.baseline import _seed_from  # noqa: E402
from repo_model.data import exceeds_bp, load_daily_panel  # noqa: E402
from repo_model.evaluation_splits import load_split_declaration  # noqa: E402

LOCKBOX = REPO / "docs" / "decisions" / "lockbox.md"
SPLITS = REPO / "metadata" / "evaluation_splits.json"
#: The heading the drafted amendment carries; the guard reads it in lockbox.md.
AMENDMENT_HEADING = "## Amendment: the live record (#215)"
FIRST_SCORING_DATES = (date(2027, 4, 1), date(2027, 10, 1))
HEADLINE = {"target": "leap", "horizon": 1}
HORIZONS = (1, 2, 3, 4, 5)
#: Each target, the baselines it is paired with.
BASELINES = {
    "+5bp": ("persistence_logistic", "calendar_climatology"),
    "+10bp": ("persistence_logistic", "calendar_climatology"),
    "leap": (onset.LEAP_PERSISTENCE_LOGISTIC, onset.LEAP_CALENDAR_CLIMATOLOGY),
}
SIGN = "paired = Brier(baseline) - Brier(model) per day; a positive mean favours the model"


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


def headline_status(day: date, *, events: int, previous) -> str:
    """`inconclusive`, `headline_verdict` or `update`, for the headline cell on `day`.

    `previous` is the earlier scoring results, each with its `date` and
    `headline_status`. The verdict is fixed once, at the first date whose
    headline cell holds `onset.MINIMUM_EVENTS` events; every result after it is
    an update, whatever its events.

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
    if events >= onset.MINIMUM_EVENTS:
        return "headline_verdict"
    return "inconclusive"


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
    """Every cell, cumulatively over `records`, on the outcomes in `rows`."""

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
                    "last": days[-1] if days else None, "models": {}}
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
    result = score(records, load_daily_panel(args.panel), load_split_declaration(SPLITS), day)
    headline = result["cells"][f"{HEADLINE['target']}/h{HEADLINE['horizon']}"]
    result.update(
        {
            "date": day.isoformat(),
            "directive": "#215",
            "logged_days": [record["decision_day"] for record in records],
            "sign_convention": SIGN,
            "minimum_events": onset.MINIMUM_EVENTS,
            "headline": HEADLINE,
            "headline_status": headline_status(day, events=headline["events"], previous=previous),
        }
    )
    args.output.write_text(json.dumps(result, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(args.output), "headline_status": result["headline_status"]}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
