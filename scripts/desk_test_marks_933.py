"""The Desk-test marks (#933, ruling on #916; H5 inputs and H9 step 1 groundwork): what moves in the take-up figures.

Development exploration only: nothing here is a verdict (scoring protocol v1, #640). It reads operation amounts and
marks only; no spread, no forecast and no score is read, so no locked day counts toward a choice
(`docs/decisions/lockbox.md`). It compares two readings of which Fed repo operations are Desk tests, on the tracked
repo-operation snapshots (`tests/fixtures/snapshots/repo_ops_inputs`):

* `note only`: the rule before #933 (`ingest._is_small_value_exercise` read the Desk's `note` alone);
* `marks` (in force): the note, or, for a `Repo` operation, an id ending " 99" or an `operationLimit` of at most
  $250 mn.

It reports (1) the repo operations whose marks the note lacked, (2) the take-up dates and `fed_repo_days_since_positive`
by year under both readings, (3) the Standing Repo Facility total (`srf_total_accepted`) dates that move, and (4) the
$10 mn / $0 / $10 mn split pattern, which the ruling leaves open and this script leaves unchanged.

    PYTHONPATH=src python3 scripts/pressure_v1_1.py panel --end 2026-09-03 --output /tmp/AUG.csv
    PYTHONPATH=src python3 scripts/desk_test_marks_933.py --panel /tmp/AUG.csv [--write]

`--write` writes `docs/pivot/evidence/desk-test-marks-933/result.json` and `docs/pivot/desk-test-marks-933-result.md`.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from datetime import date, datetime, timezone
from pathlib import Path
from unittest import mock

from repo_model import fed_liquidity, ingest
from repo_model.data import load_daily_panel

ROOT = Path(__file__).resolve().parents[1]
OUT_JSON = ROOT / "docs" / "pivot" / "evidence" / "desk-test-marks-933" / "result.json"
OUT_MD = ROOT / "docs" / "pivot" / "desk-test-marks-933-result.md"
SNAPSHOTS = ROOT / "tests" / "fixtures" / "snapshots" / "repo_ops_inputs"
BUILD_CUTOFF = datetime(2026, 9, 8, 21, 31, 42, tzinfo=timezone.utc)
END = date(2026, 9, 3)


def _note_only(operation):
    """`ingest._is_small_value_exercise` as it read before #933."""

    note = operation.get("note")
    return isinstance(note, str) and "small value exercise" in note.lower()


def _payloads():
    for path in sorted((SNAPSHOTS / "nyfed_repo_ops").glob("*.json")):
        if path.name.endswith(".manifest.json"):
            continue
        manifest = json.loads((path.parent / (path.name + ".manifest.json")).read_text(encoding="utf-8"))
        yield path, manifest


def marked_without_note():
    """Every `Repo` operation the marks drop and the note did not: date, id, limit, accepted, term."""

    out = []
    for path, _manifest in _payloads():
        for operation in ingest._nyfed_operations(json.loads(path.read_bytes())):
            if not isinstance(operation, dict) or operation.get("operationType") != "Repo":
                continue
            if ingest._is_small_value_exercise(operation) and not _note_only(operation):
                out.append(
                    {
                        "date": operation["operationDate"],
                        "operation_id": operation["operationId"],
                        "term": operation.get("term"),
                        "operation_limit": operation.get("operationLimit"),
                        "accepted_mn": operation["totalAmtAccepted"] / 1e6,
                        "mark": "id ends 99" if str(operation["operationId"]).endswith(" 99") else "limit <= 250 mn",
                    }
                )
    return sorted(out, key=lambda row: row["date"])


def panel_rows(published, *, marks):
    with mock.patch.object(ingest, "_is_small_value_exercise", ingest._is_small_value_exercise if marks else _note_only):
        rows, _summary = fed_liquidity.assemble(published, SNAPSHOTS, cutoff=BUILD_CUTOFF, end=END)
    return rows


def by_year(rows):
    out = {}
    for year in sorted({row.date.year for row in rows}):
        sel = [row for row in rows if row.date.year == year]
        gaps = [row.values.get("fed_repo_days_since_positive") for row in sel]
        out[str(year)] = {
            "longest": max(g for g in gaps if g is not None),
            "take_up_days": sum(1 for row in sel if (row.values.get("fed_repo_accepted") or 0) > 0),
        }
    return out


def srf_totals(*, marks):
    totals = {}
    with mock.patch.object(ingest, "_is_small_value_exercise", ingest._is_small_value_exercise if marks else _note_only):
        for path, manifest in _payloads():
            payload = path.read_bytes()
            artifact = ingest.SnapshotArtifact(
                source_id=ingest.NYFED_SRF_SOURCE_ID, path=path, retrieved_at=manifest["retrieved_at"],
                sha256=hashlib.sha256(payload).hexdigest(), url=manifest.get("url", ""), byte_count=len(payload),
            )
            for row in ingest._nyfed_srf_rows(artifact, payload):
                totals[row.ref_date] = row.value
    return totals


def split_pattern():
    """Operations of exactly $20 mn accepted as $10 mn Treasury, $0 agency, $10 mn MBS: counted, not ruled (#916)."""

    days = []
    for path, _manifest in _payloads():
        for operation in ingest._nyfed_operations(json.loads(path.read_bytes())):
            if not isinstance(operation, dict) or operation.get("operationType") != "Repo":
                continue
            if operation.get("totalAmtAccepted") != 20_000_000 or ingest._is_small_value_exercise(operation):
                continue
            amounts = sorted(d.get("amtAccepted") for d in operation.get("details") or ())
            if amounts == [0, 10_000_000, 10_000_000]:
                days.append(operation["operationDate"])
    return sorted(set(days))


def report(panel_path):
    published = load_daily_panel(panel_path)
    note_rows, mark_rows = panel_rows(published, marks=False), panel_rows(published, marks=True)
    differing = sorted(
        a.date.isoformat() for a, b in zip(note_rows, mark_rows)
        if (a.values.get("fed_repo_accepted"), a.values.get("fed_repo_days_since_positive"))
        != (b.values.get("fed_repo_accepted"), b.values.get("fed_repo_days_since_positive"))
    )
    srf_old, srf_new = srf_totals(marks=False), srf_totals(marks=True)
    srf_moved = [
        {"date": d.isoformat(), "note_only_bn": srf_old.get(d), "marks_bn": srf_new.get(d)}
        for d in sorted(set(srf_old) | set(srf_new)) if srf_old.get(d) != srf_new.get(d)
    ]
    return {
        "marked_without_note": marked_without_note(),
        "by_year": {"note only": by_year(note_rows), "marks": by_year(mark_rows)},
        "panel_dates": len(mark_rows),
        "dates_with_a_changed_fed_repo_column": differing,
        "srf_total_dates_that_move": srf_moved,
        "split_pattern_days_unchanged": split_pattern(),
    }


def _by_year_count(days):
    counts = {}
    for day in days:
        counts[day[:4]] = counts.get(day[:4], 0) + 1
    return ", ".join(f"{year}: {n}" for year, n in sorted(counts.items())) or "none"


def markdown(result):
    lines = [
        "# The Desk-test marks and the take-up figures (#933)",
        "",
        "**Serves:** H5 (the test-trade rule on Fed repo take-up as an input, #743) and H9 step 1 (standing repo facility take-up, #659). "
        "Exploration on development data only: no verdict (scoring protocol v1, #640). No spread, forecast or score is read; no locked day "
        "counts toward a choice. Nothing here edits an earlier record: `docs/pivot/test-trade-802-result.md` and the #908 counts stand "
        "and the figures below are published anew beside them.",
        "",
        "**The rule** (Eleonora, 19 October 2026, ruling on #916): a `Repo` operation whose id ends \" 99\", or whose `operationLimit` is at "
        "most $250 mn, is a Desk test (small-value exercise), like one whose `note` says so. It is dropped before the test-trade rule of #802.",
        "",
        "## 1. Repo operations the marks drop and the note did not",
        "",
        "| date | operation | term | limit | accepted | mark |",
        "|---|---|---|---|---|---|",
    ]
    for r in result["marked_without_note"]:
        limit = "none" if r["operation_limit"] is None else f"${r['operation_limit'] / 1e6:,.0f} mn"
        lines.append(f"| {r['date']} | `{r['operation_id']}` | {r['term']} | {limit} | ${r['accepted_mn']:,.0f} mn | {r['mark']} |")
    lines += [
        "",
        "## 2. `fed_repo_days_since_positive`, longest value / take-up days, by year",
        "",
        "| year | note only (before) | marks (in force) |",
        "|---|---|---|",
    ]
    old, new = result["by_year"]["note only"], result["by_year"]["marks"]
    for year in old:
        a, b = old[year], new[year]
        mark = "" if a == b else " (moves)"
        lines.append(f"| {year} | {a['longest']:.0f} / {a['take_up_days']} | {b['longest']:.0f} / {b['take_up_days']}{mark} |")
    lines += [
        "",
        f"{len(result['dates_with_a_changed_fed_repo_column'])} of {result['panel_dates']} panel dates change in `fed_repo_accepted` or "
        "`fed_repo_days_since_positive` (counts by year; the dates are in `result.json`): " + _by_year_count(result["dates_with_a_changed_fed_repo_column"]) + ".",
        "",
        "## 3. The Standing Repo Facility total (`srf_total_accepted`, USD bn)",
        "",
    ]
    if result["srf_total_dates_that_move"]:
        lines += ["| date | before | after |", "|---|---|---|"]
        for r in result["srf_total_dates_that_move"]:
            lines.append(f"| {r['date']} | {r['note_only_bn']} | {r['marks_bn']} |")
    else:
        lines.append("No date moves.")
    lines += [
        "",
        "## 4. Not ruled, unchanged",
        "",
        f"The $10 mn / $0 / $10 mn split pattern (a $20 mn operation) appears on {len(result['split_pattern_days_unchanged'])} days "
        "and is counted as take-up exactly as before; it is open for Eleonora (#916): "
        + ", ".join(result["split_pattern_days_unchanged"]) + ".",
        "",
        "## Reproduce",
        "",
        "```",
        "PYTHONPATH=src python3 scripts/pressure_v1_1.py panel --end 2026-09-03 --output /tmp/AUG.csv",
        "PYTHONPATH=src python3 scripts/desk_test_marks_933.py --panel /tmp/AUG.csv --write",
        "```",
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
        OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
        OUT_JSON.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        OUT_MD.write_text(text, encoding="utf-8")
    else:
        sys.stdout.write(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
