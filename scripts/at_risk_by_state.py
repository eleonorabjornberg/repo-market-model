#!/usr/bin/env python3
"""At-risk days by scarcity state and coupon settlement (#218): onset rates and mean forecasts.

**Descriptive only. No new model, no win rule, no claim; it decides nothing.**
It follows #214's post-mortem (PR #217), which found every scheduled-date
onset also on a coupon settlement day, and most onsets in scarcity states 2-3.
Nothing is written to `docs/runs/`, and no published record, declaration,
page or generated block changes.

The days are every scored day of the published fold grid (through `--end`) in
#209's at-risk group, `onset.GROUP_ONSET` as merged: five calm panel days at
or below +5 bp, read through `onset.day_groups`. Its onsets are the at-risk
days above +5 bp (`data.exceeds_bp(spread, onset.ONSET_THRESHOLD_BP)`), which
are `onset.onset_flags`'s, and the script stops unless they equal
`onset_post_mortem.onset_days`'s primary onsets.

One table, `reserve_scarcity_state` (rows, `scarcity.STATE_LABELS`) by coupon
settlement day (columns, `treasury_settlement_coupons > 0`). Every read is
#214's, through `scripts/onset_post_mortem.py`, at each day's h = 1 decision
instant: the state as-of (`as_of_reads`), the coupon settlement as
`asof._settlement_day` reads it, and the probability of the +5 bp event from
pressure model v1 (`docs/runs/pressure_model_v1_h1.json`'s declaration,
recalibrated out of fold) and from the persistence-logistic on the same fold
grid (`v1_and_persistence`). `onset_post_mortem.load` stops unless those
forecasts reproduce the published record (`check_against_record`). No new
availability rule and no new forecast path.

Each cell gives the at-risk days, the onsets, the onset rate ("k of n" with the
fraction), and the two models' mean probabilities. A cell with no days is
shown empty. A day the state cannot be read on would get its own row.

    PYTHONPATH=src /opt/rmm-venv/bin/python scripts/at_risk_by_state.py --end 2025-12-31 \
        [--forecasts CACHE.json] [--json OUT.json] [--markdown OUT.md]

`--forecasts` is the post-mortem's cache of the two models' probabilities. An
`--end` on or after 2026-01-01 is refused by the lockbox guard
(`lockbox.require_unlocked`), before anything is built.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from datetime import date
from pathlib import Path
from typing import Dict, List, Mapping, Optional, Sequence, Tuple

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))

from repo_model import onset  # noqa: E402
from repo_model.data import exceeds_bp  # noqa: E402
from repo_model.lockbox import require_unlocked  # noqa: E402
from repo_model.scarcity import STATE_LABELS  # noqa: E402


def _script(name: str):
    spec = importlib.util.spec_from_file_location(name, REPO / "scripts" / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


#: #214's post-mortem: its reads, forecasts and record check.
pm = _script("onset_post_mortem")

STATES = tuple(sorted(STATE_LABELS))
COUPON_COLUMNS = (True, False)
FIVE = f"{pm.TAU_BP:g}"


def at_risk_days(rows, scored_dates: Sequence[date], declaration) -> Tuple[List[date], List[date]]:
    """`(days, onsets)`: the scored days in `onset.GROUP_ONSET`, and those above +5 bp."""

    require_unlocked(scored_dates, where="at_risk_by_state.at_risk_days")
    groups = onset.day_groups(rows, scored_dates, declaration)
    position = {row.date: index for index, row in enumerate(rows)}
    days = [scored_dates[k] for k in groups[onset.GROUP_ONSET]]
    onsets = [
        day for day in days
        if exceeds_bp(rows[position[day]].spread_bps, onset.ONSET_THRESHOLD_BP)
    ]
    return days, onsets


def cell_of(read: Mapping) -> Tuple[Optional[int], bool]:
    """The day's as-of state and whether it is a coupon settlement day, as #214 reads them."""

    coupons = read[pm.COUPONS]
    return read["state"], coupons is not None and float(coupons) > 0.0


def _cell(entries: Sequence[dict]) -> dict:
    n = len(entries)
    k = sum(1 for entry in entries if entry["onset"])
    if not n:
        return {"days": 0, "onsets": 0, "rate": None, "v1_mean": None, "persistence_logistic_mean": None}
    return {
        "days": n,
        "onsets": k,
        "rate": k / n,
        "v1_mean": sum(entry["v1"] for entry in entries) / n,
        "persistence_logistic_mean": sum(entry["persistence"] for entry in entries) / n,
    }


def tabulate(days: Sequence[date], onsets: Sequence[date], reads: Mapping[date, dict], forecasts: dict) -> dict:
    """The table: `cells[state][coupon]`, `row_totals`, `column_totals` and `total`."""

    index = {date.fromisoformat(when): k for k, when in enumerate(forecasts["scored_dates"])}
    onset_set = set(onsets)
    entries = []
    for day in days:
        state, coupon = cell_of(reads[day])
        k = index[day]
        entries.append(
            {
                "state": state,
                "coupon": coupon,
                "onset": day in onset_set,
                "v1": forecasts[pm.V1][FIVE][k],
                "persistence": forecasts[pm.PERSISTENCE][FIVE][k],
            }
        )
    states = list(STATES) + ([None] if any(entry["state"] is None for entry in entries) else [])
    cells: Dict[Optional[int], Dict[bool, dict]] = {
        state: {
            coupon: _cell([e for e in entries if e["state"] == state and e["coupon"] == coupon])
            for coupon in COUPON_COLUMNS
        }
        for state in states
    }
    return {
        "cells": cells,
        "row_totals": {state: _cell([e for e in entries if e["state"] == state]) for state in states},
        "column_totals": {
            coupon: _cell([e for e in entries if e["coupon"] == coupon]) for coupon in COUPON_COLUMNS
        },
        "total": _cell(entries),
    }


def _text(cell: dict) -> str:
    if not cell["days"]:
        return "  |  |  |  "
    return (
        f" {cell['days']} | {cell['onsets']} of {cell['days']} ({cell['rate']:.2f}) "
        f"| {cell['v1_mean']:.3f} | {cell['persistence_logistic_mean']:.3f} "
    )


def _label(state: Optional[int]) -> str:
    return "no state" if state is None else f"{state} {STATE_LABELS[state]}"


def markdown(document: dict) -> str:
    groups = ("coupon settlement day", "not a coupon settlement day", "all at-risk days")
    out = [
        "Each group of columns: at-risk days | onsets of days (rate) | v1 mean p(> +5 bp) "
        "| persistence-logistic mean p(> +5 bp). Probabilities are at h = 1, issued at the "
        "day's as-of decision instant. An empty cell has no days.\n",
        "| Scarcity state | " + " | ".join(f"{g}: days | {g}: onsets | {g}: v1 | {g}: persistence-logistic" for g in groups) + " |",
        "|---|" + "---|---|---|---|" * len(groups),
    ]
    for state, row in document["cells"].items():
        parts = [_text(row[coupon]) for coupon in COUPON_COLUMNS]
        parts.append(_text(document["row_totals"][state]))
        out.append(f"| {_label(state)} |" + "|".join(parts) + "|")
    parts = [_text(document["column_totals"][coupon]) for coupon in COUPON_COLUMNS]
    parts.append(_text(document["total"]))
    out.append("| all states |" + "|".join(parts) + "|")
    out.append("")
    return "\n".join(out)


def _json_ready(document: dict) -> dict:
    def coupon_key(coupon):
        return "coupon_settlement" if coupon else "no_coupon_settlement"

    def state_key(state):
        return "no_state" if state is None else str(state)

    return {
        "cells": {
            state_key(s): {coupon_key(c): cell for c, cell in row.items()}
            for s, row in document["cells"].items()
        },
        "row_totals": {state_key(s): cell for s, cell in document["row_totals"].items()},
        "column_totals": {coupon_key(c): cell for c, cell in document["column_totals"].items()},
        "total": document["total"],
    }


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--end", type=date.fromisoformat, required=True, metavar="YYYY-MM-DD")
    parser.add_argument("--forecasts", type=Path, help="the post-mortem's cache of the two models' probabilities")
    parser.add_argument("--json", type=Path)
    parser.add_argument("--markdown", type=Path)
    args = parser.parse_args(argv)
    require_unlocked([args.end], where="at_risk_by_state")

    loaded = pm.load(args.end, args.forecasts)
    rows, scored, declaration = loaded["rows"], loaded["scored"], loaded["declaration"]
    days, onsets = at_risk_days(rows, scored, declaration)
    if onsets != pm.onset_days(rows, scored, declaration)[pm.PRIMARY]:
        raise ValueError("the at-risk group's onsets are not the post-mortem's primary onsets")
    document = tabulate(days, onsets, loaded["reads"], loaded["forecasts"])
    text = markdown(document)
    header = {
        "status": "descriptive only (#218): no model, no win rule, no claim; nothing published moves",
        "published_columns_digest": loaded["published_columns_digest"],
        "end": args.end.isoformat(),
        "first_day": days[0].isoformat(),
        "last_day": days[-1].isoformat(),
        "record_check": loaded["record_check"],
    }
    if args.json:
        args.json.write_text(json.dumps({**header, **_json_ready(document)}, indent=2) + "\n", encoding="utf-8")
    if args.markdown:
        args.markdown.write_text(text, encoding="utf-8")
    print(json.dumps(header, indent=2))
    print(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
