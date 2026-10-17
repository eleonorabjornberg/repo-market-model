"""Are the recurring ~$0.1 bn Fed repo trades announced test exercises? (#872, finding #860; H3 groundwork).

Development exploration only: nothing here is a verdict (scoring protocol v1, #640). It changes no classification and
no panel. It does three things, on the tracked repo-operation snapshots (`tests/fixtures/snapshots/repo_ops_inputs`):

1. lists every Repo operation with $0.09 to $0.13 bn accepted, with every field the snapshot carries;
2. matches each against the small value exercises the Desk announced beforehand on newyorkfed.org (the statement
   pages saved under `docs/pivot/evidence/repo-test-trades-872/sources/`, checked against `CHECKSUMS.sha256`): by
   operation date and by the announced time window;
3. reports `fed_repo_days_since_positive` by year under three readings of what counts as take-up: the rule in force
   (`ingest.REPO_TAKE_UP_FLOOR`), the rule #826 proposes (a whole number of millions, at most $7 mn, is a test
   trade), and the announcement-keyed rule the directive asks for (an operation announced as a small value
   exercise is not take-up, from the statement's public time). No size threshold is added or changed.

It reads operation amounts only. No spread, no forecast and no score is read, so no locked day counts toward a choice
(`docs/decisions/lockbox.md`); the take-up counts run to 2026-09-03 as the directive asks.

    PYTHONPATH=src python3 scripts/pressure_v1_1.py panel --end 2026-09-03 --output /tmp/AUG.csv
    PYTHONPATH=src python3 scripts/repo_test_trades_872.py --panel /tmp/AUG.csv [--write]

`--write` writes `docs/pivot/evidence/repo-test-trades-872/result.json` and `result.md`.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from collections import Counter, defaultdict
from datetime import date, datetime, time, timezone
from pathlib import Path
from unittest import mock

from repo_model import fed_liquidity, ingest
from repo_model.data import load_daily_panel

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs" / "pivot" / "evidence" / "repo-test-trades-872"
SOURCES = OUT / "sources"
SNAPSHOTS = ROOT / "tests" / "fixtures" / "snapshots" / "repo_ops_inputs"
BUILD_CUTOFF = datetime(2026, 9, 8, 21, 31, 42, tzinfo=timezone.utc)
END = date(2026, 9, 3)
BAND = (90_000_000, 130_000_000)
#: Retrieval time of every page under `sources/` (one request each, 17 October 2026).
RETRIEVED_AT = "2026-10-17T15:52Z to 15:54Z"
BASE = "https://www.newyorkfed.org/markets/opolicy/operating_policy_"

#: Each Repo small value exercise the Desk announced from 2024 on, as the statement page states it:
#: (statement file, statement date, operation date, window start, window end, tenor/type). Read off the pages in
#: `sources/`; `check_sources` confirms each page carries its operation date and window.
ANNOUNCED = (
    ("statement_240502.html", date(2024, 5, 2), date(2024, 5, 9), time(10, 0), time(10, 15), "overnight repo"),
    ("statement_240919.html", date(2024, 9, 19), date(2024, 9, 24), time(10, 30), time(10, 45), "term repo"),
    ("statement_250117.html", date(2025, 1, 17), date(2025, 1, 24), time(10, 0), time(10, 15), "overnight repo"),
    ("statement_250212.html", date(2025, 2, 12), date(2025, 2, 26), time(10, 0), time(10, 15), "overnight repo"),
    ("statement_250220.html", date(2025, 2, 20), date(2025, 3, 5), time(8, 15), time(8, 30), "overnight repo"),
    ("statement_250814.html", date(2025, 8, 14), date(2025, 8, 21), time(10, 30), time(10, 45), "term repo"),
    ("statement_251002.html", date(2025, 10, 2), date(2025, 10, 8), time(10, 15), time(10, 30), "overnight repo"),
    ("statement_251031.html", date(2025, 10, 31), date(2025, 11, 5), time(10, 0), time(10, 15), "overnight repo"),
    ("statement_260211.html", date(2026, 2, 11), date(2026, 2, 18), time(10, 30), time(10, 45), "forward start overnight repo"),
    ("statement_260506.html", date(2026, 5, 6), date(2026, 5, 27), time(10, 15), time(10, 30), "overnight repo"),
    ("statement_261013.html", date(2026, 10, 13), date(2026, 10, 20), time(10, 30), time(10, 45), "forward start term repo"),
)
#: A phrase each page must contain for its operation date, so a mis-typed row above fails `check_sources`.
DATE_PHRASES = {
    "statement_240502.html": "May 9, 2024", "statement_240919.html": "September 24, 2024",
    "statement_250117.html": "January 24, 2025", "statement_250212.html": "February 26, 2025",
    "statement_250220.html": "March 5, 2025", "statement_250814.html": "August 21, 2025",
    "statement_251002.html": "October 8th, 2025", "statement_251031.html": "November 5, 2025",
    "statement_260211.html": "February 18, 2026", "statement_260506.html": "May 27th, 2026",
    "statement_261013.html": "October 20, 2026",
}


def check_sources():
    """The saved pages match `CHECKSUMS.sha256`, and each statement carries its operation date. Raises `ValueError`."""

    for line in (SOURCES / "CHECKSUMS.sha256").read_text(encoding="utf-8").splitlines():
        digest, name = line.split(None, 1)
        if hashlib.sha256((SOURCES / name.strip().lstrip("*")).read_bytes()).hexdigest() != digest:
            raise ValueError(f"{name}: the saved page does not match CHECKSUMS.sha256")
    for name, _stated, _day, _start, _end, _kind in ANNOUNCED:
        text = (SOURCES / name).read_text(encoding="utf-8", errors="ignore").replace("&nbsp;", " ")
        if DATE_PHRASES[name] not in " ".join(text.split()):
            raise ValueError(f"{name}: does not contain {DATE_PHRASES[name]!r}")


def operations():
    """Every Repo operation in the tracked snapshots, once by `operationId`, with its fields."""

    found = {}
    for path in sorted((SNAPSHOTS / "nyfed_repo_ops").glob("*.json")):
        if path.name.endswith(".manifest.json"):
            continue
        for operation in json.loads(path.read_text(encoding="utf-8"))["repo"]["operations"]:
            if operation.get("operationType") == "Repo":
                found[operation["operationId"]] = operation
    return sorted(found.values(), key=lambda op: (op["operationDate"], op.get("releaseTime") or "", op["operationId"]))


def _clock(text):
    hour, minute = str(text).split(":")[:2]
    return time(int(hour), int(minute))


def announcement(operation):
    """The announced exercise this operation is, or None: same operation date, inside the announced window."""

    day = date.fromisoformat(operation["operationDate"])
    for entry in ANNOUNCED:
        if entry[2] != day:
            continue
        start, end = entry[3], entry[4]
        release, close = operation.get("releaseTime"), operation.get("closeTime")
        if release and close and start <= _clock(release) and _clock(close) <= end:
            return entry
        if "term" in entry[5] and operation.get("term") != "Overnight":
            return entry
    return None


def public_before(entry, operation):
    """The statement was public (end of its day) before the operation's own release."""

    return entry[1] < date.fromisoformat(operation["operationDate"])


def listing():
    rows = []
    for operation in operations():
        accepted = operation.get("totalAmtAccepted")
        if not isinstance(accepted, (int, float)) or not BAND[0] <= accepted <= BAND[1]:
            continue
        entry = announcement(operation)
        details = operation.get("details") or []
        rows.append({
            "date": operation["operationDate"], "operationId": operation["operationId"],
            "release": operation.get("releaseTime"), "close": operation.get("closeTime"),
            "term": operation.get("term"), "method": operation.get("operationMethod"),
            "accepted": accepted, "submitted": operation.get("totalAmtSubmitted"),
            "rates": sorted({d.get("percentWeightedAverageRate") for d in details if d.get("amtAccepted")} - {None}),
            "counterparties": [d.get("amtAccepted") for d in details if d.get("amtAccepted")],
            "note": (operation.get("note") or "").replace("<p>", "").replace("</p>", ""),
            "note_says_sve": ingest._is_small_value_exercise(operation),
            "announced": None if entry is None else entry[0],
            "announced_public": None if entry is None else entry[1].isoformat(),
        })
    return rows


_IN_FORCE = ingest._effective_accepted


def _rule_current(_operation, accepted):
    return _IN_FORCE(accepted)


def _rule_826(_operation, accepted):
    return 0 if 0 < accepted <= 7_000_000 and accepted % 1_000_000 == 0 else accepted


def _rule_announced(operation, accepted):
    entry = announcement(operation)
    if entry is not None and public_before(entry, operation):
        return 0
    return _IN_FORCE(accepted)


RULES = (("in force (floor $0.1 bn)", _rule_current), ("#826 (whole $1-7 mn)", _rule_826), ("announcement-keyed", _rule_announced))


def panel_under(rule, published):
    """The assembled panel rows with `ingest._effective_accepted` replaced by `rule` on the operation."""

    original = ingest._kept_repo_operations
    # `_effective_accepted` sees only the amount, so the operation being summed is carried alongside it.
    state = {}

    def effective(accepted):
        return rule(state["op"], accepted)

    def kept_with_state(operations_):
        for number, operation, ref_date in original(operations_):
            state["op"] = operation
            yield number, operation, ref_date

    with mock.patch.object(ingest, "_kept_repo_operations", kept_with_state), mock.patch.object(
        ingest, "_effective_accepted", effective
    ):
        rows, _summary = fed_liquidity.assemble(published, SNAPSHOTS, cutoff=BUILD_CUTOFF, end=END)
    return rows


def by_year(rows):
    out = {}
    for year in sorted({row.date.year for row in rows}):
        sel = [row for row in rows if row.date.year == year]
        gaps = [row.values.get("fed_repo_days_since_positive") for row in sel]
        taken = sum(1 for row in sel if (row.values.get("fed_repo_accepted") or 0) > 0)
        out[year] = {"longest": max(g for g in gaps if g is not None), "take_up_days": taken}
    window = [row for row in rows if date(2024, 1, 1) <= row.date]
    out["2024-01..2026-09"] = {
        "longest": max(row.values["fed_repo_days_since_positive"] for row in window),
        "take_up_days": sum(1 for row in window if (row.values.get("fed_repo_accepted") or 0) > 0),
    }
    return out


#: Declarations that carry H5's candidate inputs (spread distribution, #632 to #761, step 3 and 4, #845, #726).
H5_DECLARATIONS = (
    "spread_distribution_*.json", "h5_step3_*.json", "h5_step4_*.json", "exploration_845.json", "backfill_h5_726.json",
)


def h5_inputs():
    """Which H5 declarations name a `fed_repo` column, by a plain text search of each file."""

    checked = sorted({path for pattern in H5_DECLARATIONS for path in (ROOT / "metadata").glob(pattern)})
    return {
        "declarations_checked": [path.name for path in checked],
        "reading_fed_repo": [path.name for path in checked if "fed_repo" in path.read_text(encoding="utf-8")],
    }


def fed_repo_columns(rows):
    return [{k: v for k, v in row.values.items() if k.startswith("fed_repo")} for row in rows]


def report(panel_path):
    check_sources()
    published = load_daily_panel(panel_path)
    listed = listing()
    panels = {name: panel_under(rule, published) for name, rule in RULES}
    results = {name: by_year(rows) for name, rows in panels.items()}
    same = results[RULES[0][0]] == results[RULES[2][0]]
    columns_identical = fed_repo_columns(panels[RULES[0][0]]) == fed_repo_columns(panels[RULES[2][0]])
    cells = Counter()
    for row in listed:
        cells[("announced" if row["announced"] else "note" if row["note_says_sve"] else "neither")] += 1
    return {
        "retrieved_at": RETRIEVED_AT,
        "announced_exercises": [
            {"statement": f"{BASE}{e[0][10:16]}", "page": e[0], "public": e[1].isoformat(), "operation_date": e[2].isoformat(),
             "window": f"{e[3]:%H:%M}-{e[4]:%H:%M}", "kind": e[5]}
            for e in ANNOUNCED
        ],
        "listed": listed,
        "classes": dict(cells),
        "by_year": results,
        "announcement_rule_equals_in_force": same,
        "fed_repo_columns_identical": columns_identical,
        "h5_inputs": h5_inputs(),
    }


def markdown(result):
    lines = [
        "# Recurring ~$0.1 bn Fed repo trades: announced test exercises? (#872)",
        "",
        "Development data, **not a verdict**. Generated by `scripts/repo_test_trades_872.py`; do not edit by hand.",
        "",
        f"Pages fetched {result['retrieved_at']}, 17 October 2026; checksums in `sources/CHECKSUMS.sha256`.",
        "",
        "## Announced Repo small value exercises, 2024 to 2026 (newyorkfed.org statements)",
        "",
        "| statement public | operation date | window (ET) | kind | page |",
        "|---|---|---|---|---|",
    ]
    for e in result["announced_exercises"]:
        lines.append(f"| {e['public']} | {e['operation_date']} | {e['window']} | {e['kind']} | `sources/{e['page']}` |")
    lines += [
        "",
        "## Operations with $0.09 to $0.13 bn accepted in the tracked snapshots",
        "",
        f"{len(result['listed'])} operations. Classes: {result['classes']}.",
        "",
        "| date | id | release-close | term | method | accepted $ | submitted $ | rate(s) % | accepted per line $ | note | announced |",
        "|---|---|---|---|---|---|---|---|---|---|---|",
    ]
    for r in result["listed"]:
        note = r["note"][:60].replace("|", "/") if r["note"] else ""
        lines.append(
            f"| {r['date']} | {r['operationId']} | {r['release']}-{r['close']} | {r['term']} | {r['method']} | {r['accepted']:,} | "
            f"{r['submitted']:,} | {', '.join(str(x) for x in r['rates'])} | {', '.join(str(x) for x in r['counterparties'])} | {note} | "
            f"{(r['announced'] or '')} |"
        )
    lines += ["", "## `fed_repo_days_since_positive`, longest value and number of take-up days, by year", ""]
    names = list(result["by_year"])
    lines.append("| year | " + " | ".join(f"{n}: longest / take-up days" for n in names) + " |")
    lines.append("|---|" + "---|" * len(names))
    for year in result["by_year"][names[0]]:
        lines.append(f"| {year} | " + " | ".join(
            f"{result['by_year'][n][year]['longest']:.0f} / {result['by_year'][n][year]['take_up_days']}" for n in names
        ) + " |")
    lines += [
        "",
        f"The announcement-keyed reading equals the rule in force in every cell: **{result['announcement_rule_equals_in_force']}**; "
        f"every `fed_repo_*` panel column is identical under the two: **{result['fed_repo_columns_identical']}**.",
        "",
        "## Effect on H5's candidate inputs",
        "",
        "| H5 declarations checked | naming a `fed_repo` column | change in any `fed_repo_*` column under the announcement-keyed rule |",
        "|---|---|---|",
        f"| {', '.join('`' + n + '`' for n in result['h5_inputs']['declarations_checked'])} | "
        f"{', '.join(result['h5_inputs']['reading_fed_repo']) or 'none'} | "
        f"{'none' if result['fed_repo_columns_identical'] else 'some'} |",
        "",
    ]
    return "\n".join(lines)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--panel", type=Path, required=True)
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args(argv)
    result = report(args.panel)
    text = markdown(result)
    if args.write:
        OUT.mkdir(parents=True, exist_ok=True)
        (OUT / "result.json").write_text(json.dumps(result, indent=1, default=str) + "\n", encoding="utf-8")
        (OUT / "result.md").write_text(text, encoding="utf-8")
    print(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
