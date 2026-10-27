"""The afternoon test-trade rule (#938, ruling on #860; H5 inputs and H3 groundwork G1): overlap and what moves in the take-up figures.

Development exploration only: nothing here is a verdict (scoring protocol v1, #640). It reads operation fields and amounts only; no spread,
no forecast and no score is read, so no locked day counts toward a choice (`docs/decisions/lockbox.md`). On the tracked repo-operation
snapshots (`tests/fixtures/snapshots/repo_ops_inputs`) it reports

1. the 35 un-noted Repo operations of $90-130 mn of PR #884, each with the rule that catches it (`ingest._is_afternoon_test_trade`, this
   change; `ingest._is_small_value_exercise`, the Desk marks of #933) and the ones neither catches;
2. the operations the ruling leaves as marked questions (13:29 releases, a $10 mn side line, Full Allotment lines with no rate, the band edges);
3. `fed_repo_days_since_positive` (longest value / take-up days) by year under three readings: the rule before this change (#933's marks), this
   rule, and the 35 listed operations of #884's table (the 17 October list reading);
4. the Standing Repo Facility total (`srf_total_accepted`) dates that move, and the count of dates with a positive total.

    PYTHONPATH=src python3 scripts/pressure_v1_1.py panel --end 2026-09-03 --output /tmp/AUG.csv
    PYTHONPATH=src python3 scripts/afternoon_test_trade_938.py --panel /tmp/AUG.csv [--write]

`--write` writes `docs/pivot/evidence/afternoon-test-trade-938/result.json` and `docs/pivot/afternoon-test-trade-938-result.md`.
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
OUT_JSON = ROOT / "docs" / "pivot" / "evidence" / "afternoon-test-trade-938" / "result.json"
OUT_MD = ROOT / "docs" / "pivot" / "afternoon-test-trade-938-result.md"
SNAPSHOTS = ROOT / "tests" / "fixtures" / "snapshots" / "repo_ops_inputs"
BUILD_CUTOFF = datetime(2026, 9, 8, 21, 31, 42, tzinfo=timezone.utc)
END = date(2026, 9, 3)
#: PR #884's band: Repo operations accepting $90-130 mn.
LIST_MIN, LIST_MAX = 90_000_000, 130_000_000


def _payloads():
    for path in sorted((SNAPSHOTS / "nyfed_repo_ops").glob("*.json")):
        if path.name.endswith(".manifest.json"):
            continue
        manifest = json.loads((path.parent / (path.name + ".manifest.json")).read_text(encoding="utf-8"))
        yield path, manifest


def _operations():
    seen = {}
    for path, _manifest in _payloads():
        for operation in ingest._nyfed_operations(json.loads(path.read_bytes())):
            if isinstance(operation, dict) and operation.get("operationType") == "Repo":
                seen[(operation["operationDate"], operation["operationId"])] = operation
    return [seen[key] for key in sorted(seen)]


def _lines(operation):
    return [d.get("amtAccepted") for d in operation.get("details") or () if d.get("amtAccepted")]


def listing():
    """The un-noted Repo operations accepting $90-130 mn (PR #884's 35), with the rules that catch each."""

    rows = []
    for operation in _operations():
        accepted = operation["totalAmtAccepted"]
        note = operation.get("note") or ""
        if not LIST_MIN <= accepted <= LIST_MAX or "small value exercise" in note.lower():
            continue
        lines = _lines(operation)
        rows.append(
            {
                "date": operation["operationDate"],
                "operation_id": operation["operationId"],
                "release": operation.get("releaseTime"),
                "method": operation.get("operationMethod"),
                "lines_mn": [line / 1e6 for line in lines],
                "rates": sorted({d.get("percentWeightedAverageRate") for d in operation.get("details") or () if d.get("amtAccepted")} - {None}),
                "accepted_mn": accepted / 1e6,
                "note": note,
                "caught_by_pattern": ingest._is_afternoon_test_trade(operation),
                "caught_by_desk_marks": ingest._is_small_value_exercise(operation),
            }
        )
    return rows


def marked_questions(rows):
    """The operations the ruling leaves as marked questions for Eleonora."""

    caught = [r for r in rows if r["caught_by_pattern"]]
    main = lambda r: max(r["lines_mn"]) * 1e6  # noqa: E731
    return {
        "released_1329": [r["operation_id"] for r in caught if r["release"] == "13:29"],
        "ten_million_side_line": [r["operation_id"] for r in rows if not r["caught_by_pattern"] and r["release"] in ingest.PATTERN_RELEASE_TIMES and sorted(r["lines_mn"])[-2:-1] == [10.0]],
        "full_allotment_no_rate": [r["operation_id"] for r in caught if r["method"] == "Full Allotment"],
        "near_band_edge": [r["operation_id"] for r in rows if min(abs(main(r) - ingest.PATTERN_BAND_MIN), abs(main(r) - ingest.PATTERN_BAND_MAX)) <= 3_000_000],
        "lowest_main_line_caught_mn": min(max(r["lines_mn"]) for r in caught),
        "highest_main_line_caught_mn": max(max(r["lines_mn"]) for r in caught),
    }


def _off(_operation):
    return False


def _listed(ids):
    return lambda operation: operation.get("operationId") in ids


def panel_rows(published, predicate):
    with mock.patch.object(ingest, "_is_afternoon_test_trade", predicate):
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


def srf_totals(*, pattern):
    totals = {}
    with mock.patch.object(ingest, "_is_afternoon_test_trade", ingest._is_afternoon_test_trade if pattern else _off):
        for path, manifest in _payloads():
            payload = path.read_bytes()
            artifact = ingest.SnapshotArtifact(
                source_id=ingest.NYFED_SRF_SOURCE_ID, path=path, retrieved_at=manifest["retrieved_at"],
                sha256=hashlib.sha256(payload).hexdigest(), url=manifest.get("url", ""), byte_count=len(payload),
            )
            for row in ingest._nyfed_srf_rows(artifact, payload):
                totals[row.ref_date] = row.value
    return totals


def report(panel_path):
    published = load_daily_panel(panel_path)
    rows = listing()
    listed_ids = {r["operation_id"] for r in rows}
    before = panel_rows(published, _off)
    after = panel_rows(published, ingest._is_afternoon_test_trade)
    listed = panel_rows(published, _listed(listed_ids))
    differing = sorted(
        a.date.isoformat() for a, b in zip(before, after)
        if (a.values.get("fed_repo_accepted"), a.values.get("fed_repo_days_since_positive"))
        != (b.values.get("fed_repo_accepted"), b.values.get("fed_repo_days_since_positive"))
    )
    srf_old, srf_new = srf_totals(pattern=False), srf_totals(pattern=True)
    srf_moved = [
        {"date": d.isoformat(), "before_bn": srf_old.get(d), "after_bn": srf_new.get(d)}
        for d in sorted(set(srf_old) | set(srf_new)) if srf_old.get(d) != srf_new.get(d)
    ]
    window = [r for r in after if r.date >= date(2024, 1, 1)]
    window_before = [r for r in before if r.date >= date(2024, 1, 1)]
    return {
        "listing": rows,
        "counts": {
            "listed": len(rows),
            "caught_by_pattern": sum(r["caught_by_pattern"] for r in rows),
            "caught_by_desk_marks": sum(r["caught_by_desk_marks"] for r in rows),
            "caught_by_both": sum(r["caught_by_pattern"] and r["caught_by_desk_marks"] for r in rows),
            "caught_by_neither": sum(not r["caught_by_pattern"] and not r["caught_by_desk_marks"] for r in rows),
        },
        "marked_questions": marked_questions(rows),
        "by_year": {"before (#933 marks)": by_year(before), "this rule": by_year(after), "the 35 listed": by_year(listed)},
        "window_2024_01_to_2026_09": {
            "before": {"longest": max(r.values["fed_repo_days_since_positive"] for r in window_before),
                       "take_up_days": sum(1 for r in window_before if (r.values.get("fed_repo_accepted") or 0) > 0)},
            "this rule": {"longest": max(r.values["fed_repo_days_since_positive"] for r in window),
                          "take_up_days": sum(1 for r in window if (r.values.get("fed_repo_accepted") or 0) > 0)},
        },
        "panel_dates": len(after),
        "dates_with_a_changed_fed_repo_column": differing,
        "srf_total_dates_that_move": srf_moved,
        "srf_positive_dates": {
            "before": sum(1 for v in srf_old.values() if v > 0),
            "after": sum(1 for v in srf_new.values() if v > 0),
        },
    }


def _by_year_count(days):
    counts = {}
    for day in days:
        counts[day[:4]] = counts.get(day[:4], 0) + 1
    return ", ".join(f"{year}: {n}" for year, n in sorted(counts.items())) or "none"


def _rule_text(r):
    if r["caught_by_pattern"] and r["caught_by_desk_marks"]:
        return "both"
    if r["caught_by_pattern"]:
        return "pattern (#938)"
    if r["caught_by_desk_marks"]:
        return "Desk marks (#933)"
    return "neither"


def markdown(result):
    c, q = result["counts"], result["marked_questions"]
    lines = [
        "# The afternoon test-trade rule and the take-up figures (#938)",
        "",
        "**Serves:** H5 (the test-trade rule on Fed repo take-up as an input, #743; finding #860) and H3 groundwork G1 (data quality of the Fed repo take-up "
        "recency input, #872 / PR #884). **Development data, not a verdict:** no spread, forecast or score is read; no locked day counts toward a choice "
        "(scoring protocol v1, #640). Nothing here edits an earlier record: `docs/pivot/test-trade-802-result.md`, `docs/pivot/repo-test-trades-872-result.md` "
        "and `docs/pivot/desk-test-marks-933-result.md` stand and the figures below are published anew beside them.",
        "",
        "**The rule** (Eleonora, ruling on #860 of 19 October 2026, read by her ruling on #938 of 20 October 2026). An overnight `Repo` operation with no note "
        "is a test trade, not take-up, if it was released at 13:29 or 13:30, its main line (the largest accepted line) is $90-130 mn, and every other line that "
        "accepted anything is under $10 mn. It reads only the operation's own results release (`ingest._is_afternoon_test_trade`). The two 08:15 operations "
        "are regular operations (#884 section 2) and stay take-up. The operation still happened, so its date keeps a row, at zero.",
        "",
        "## 1. The 35 un-noted operations of PR #884 and what catches them",
        "",
        f"The rule catches {c['caught_by_pattern']} of {c['listed']}. The Desk marks of #933 (id ends \" 99\", or limit at most $250 mn) catch "
        f"{c['caught_by_desk_marks']} of them; both rules catch {c['caught_by_both']}; neither catches {c['caught_by_neither']}.",
        "",
        "| date | id | release | method | lines ($ mn) | rate (%) | accepted ($ mn) | caught by |",
        "|---|---|---|---|---|---|---|---|",
    ]
    for r in result["listing"]:
        lines.append(
            f"| {r['date']} | `{r['operation_id']}` | {r['release']} | {r['method']} | {', '.join(f'{x:g}' for x in r['lines_mn'])} | "
            f"{', '.join(str(x) for x in r['rates']) or 'none stated'} | {r['accepted_mn']:g} | {_rule_text(r)} |"
        )
    lines += [
        "",
        "Not caught by either: " + ", ".join(
            f"`{r['operation_id']}` ({r['date']}, {r['release']}, lines {', '.join(f'{x:g}' for x in r['lines_mn'])})" for r in result["listing"] if _rule_text(r) == "neither"
        ) + ". Two are 08:15 regular operations; the third has a $10 mn accompanying line, which is not under $10 mn.",
        "",
        "## 2. Marked questions for Eleonora",
        "",
        f"* **The count.** The ruling comment says \"31 of 35\"; the rule as the comment words it catches {c['caught_by_pattern']}. Reading \"under $10 mn\" "
        "as \"up to $10 mn\" would catch 33. The rule is implemented as worded (strictly under $10 mn, 13:29 and 13:30 both). Which reading produced 31 is not known here.",
        "* **13:29 releases** (the ruling says 13:29-13:30, so they are caught): " + ", ".join(f"`{x}`" for x in q["released_1329"]) + ".",
        "* **A $10 mn accompanying line** (not caught, being not under $10 mn): " + ", ".join(f"`{x}`" for x in q["ten_million_side_line"]) + ".",
        f"* **\"Single rate\" on Full Allotment rows.** {len(q['full_allotment_no_rate'])} caught operations are Full Allotment and state no rate. The rule counts a main line "
        "with no stated rate as having one rate (only a main line whose own low and high rate differ is excluded). Whether a missing rate should count is hers.",
        f"* **The band edges.** The caught main lines run from ${q['lowest_main_line_caught_mn']:g} mn to ${q['highest_main_line_caught_mn']:g} mn; "
        "operations within $3 mn of $90 mn or $130 mn: " + (", ".join(f"`{x}`" for x in q["near_band_edge"]) or "none") + ".",
        "",
        "## 3. `fed_repo_days_since_positive`, longest value / take-up days, by year",
        "",
        "| year | before (#933 marks) | this rule | the 35 listed (the 17 October list reading, PR #884) |",
        "|---|---|---|---|",
    ]
    old, new, listed = (result["by_year"][k] for k in ("before (#933 marks)", "this rule", "the 35 listed"))
    for year in old:
        a, b, d = old[year], new[year], listed[year]
        mark = "" if a == b else " (moves)"
        lines.append(
            f"| {year} | {a['longest']:.0f} / {a['take_up_days']} | {b['longest']:.0f} / {b['take_up_days']}{mark} | {d['longest']:.0f} / {d['take_up_days']} |"
        )
    w = result["window_2024_01_to_2026_09"]
    lines += [
        f"| 2024-01 to 2026-09 | {w['before']['longest']:.0f} / {w['before']['take_up_days']} | {w['this rule']['longest']:.0f} / {w['this rule']['take_up_days']} | |",
        "",
        f"{len(result['dates_with_a_changed_fed_repo_column'])} of {result['panel_dates']} panel dates change in `fed_repo_accepted` or "
        "`fed_repo_days_since_positive` (counts by year; the dates are in `result.json`): " + _by_year_count(result["dates_with_a_changed_fed_repo_column"]) + ".",
        "",
        "## 4. The Standing Repo Facility total (`srf_total_accepted`, USD bn)",
        "",
    ]
    if result["srf_total_dates_that_move"]:
        lines += ["| date | before | after |", "|---|---|---|"]
        for r in result["srf_total_dates_that_move"]:
            lines.append(f"| {r['date']} | {r['before_bn']} | {r['after_bn']} |")
        s = result["srf_positive_dates"]
        lines += ["", f"Dates with a positive total: {s['before']} before, {s['after']} after."]
    else:
        lines.append("No date moves.")
    lines += [
        "",
        "## Not re-run",
        "",
        "The ordinary-day AUROC and 2018-warning matrices of `docs/pivot/test-trade-802-result.md` (the retired +5 bp judge, the `ml` extra, five horizons by several "
        "arms) are not re-run here; the PR says so and proposes it as a `needs-mac` step if Eleonora wants it.",
        "",
        "## Reproduce",
        "",
        "```",
        "PYTHONPATH=src python3 scripts/pressure_v1_1.py panel --end 2026-09-03 --output /tmp/AUG.csv",
        "PYTHONPATH=src python3 scripts/afternoon_test_trade_938.py --panel /tmp/AUG.csv --write",
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
