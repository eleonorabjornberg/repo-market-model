"""The split test-trade rule (#1456, ruling on #916; H9 step 1 data and H5 inputs): which days it reclassifies and what moves.

Development exploration only: nothing here is a verdict (scoring protocol v1, #640). It reads operation amounts and lines only; no spread,
no forecast and no score is read, so no locked day counts toward a choice (`docs/decisions/lockbox.md`). On the tracked repo-operation
snapshots (`tests/fixtures/snapshots/repo_ops_inputs`) it compares the rule in force before this change (the Desk marks of #933, the
whole-million rule of #802, the afternoon pattern of #938) with the same plus `ingest._is_split_test_trade`, and reports

1. every operation the split rule reclassifies, with its release time, lines and whether it is one of the 13 $10 mn / $0 / $10 mn days;
2. the `fed_repo_*` columns: `fed_repo_days_since_positive` (longest value / take-up days) by year, and the panel dates that change;
3. the Standing Repo Facility total (`srf_total_accepted`) dates that move.

    PYTHONPATH=src python3 scripts/pressure_v1_1.py panel --end 2026-09-03 --output /tmp/AUG.csv
    PYTHONPATH=src python3 scripts/split_test_trade_1456.py --panel /tmp/AUG.csv [--write]

`--write` writes `docs/pivot/evidence/split-test-trade-1456/result.json` and `docs/pivot/split-test-trade-1456-result.md`.
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
OUT_JSON = ROOT / "docs" / "pivot" / "evidence" / "split-test-trade-1456" / "result.json"
OUT_MD = ROOT / "docs" / "pivot" / "split-test-trade-1456-result.md"
SNAPSHOTS = ROOT / "tests" / "fixtures" / "snapshots" / "repo_ops_inputs"
BUILD_CUTOFF = datetime(2026, 9, 8, 21, 31, 42, tzinfo=timezone.utc)
END = date(2026, 9, 3)


def _off(_operation):
    return False


def _payloads():
    for path in sorted((SNAPSHOTS / "nyfed_repo_ops").glob("*.json")):
        if path.name.endswith(".manifest.json"):
            continue
        manifest = json.loads((path.parent / (path.name + ".manifest.json")).read_text(encoding="utf-8"))
        yield path, manifest


def _is_ten_zero_ten(operation):
    amounts = sorted(d.get("amtAccepted") for d in operation.get("details") or ())
    return operation.get("totalAmtAccepted") == 20_000_000 and amounts == [0, 10_000_000, 10_000_000]


def reclassified():
    """Every Repo operation the split rule drops that the rule before it did not: date, id, release, lines, shape."""

    seen = {}
    for path, _manifest in _payloads():
        for operation in ingest._nyfed_operations(json.loads(path.read_bytes())):
            if not isinstance(operation, dict) or operation.get("operationType") != "Repo":
                continue
            if ingest._is_small_value_exercise(operation) or ingest._is_afternoon_test_trade(operation):
                continue
            if ingest._is_test_trade(operation.get("totalAmtAccepted") or 0):
                continue
            if ingest._is_split_test_trade(operation):
                seen[(operation["operationDate"], operation["operationId"])] = {
                    "date": operation["operationDate"],
                    "operation_id": operation["operationId"],
                    "term": operation.get("term"),
                    "release_time": operation.get("releaseTime"),
                    "accepted_mn": operation["totalAmtAccepted"] / 1e6,
                    "lines_mn": [d["amtAccepted"] / 1e6 for d in operation["details"]],
                    "ten_zero_ten": _is_ten_zero_ten(operation),
                }
    return [seen[key] for key in sorted(seen)]


def panel_rows(published, *, rule):
    with mock.patch.object(ingest, "_is_split_test_trade", ingest._is_split_test_trade if rule else _off):
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


def srf_totals(*, rule):
    totals = {}
    with mock.patch.object(ingest, "_is_split_test_trade", ingest._is_split_test_trade if rule else _off):
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
    before, after = panel_rows(published, rule=False), panel_rows(published, rule=True)
    differing = sorted(
        a.date.isoformat() for a, b in zip(before, after)
        if (a.values.get("fed_repo_accepted"), a.values.get("fed_repo_days_since_positive"))
        != (b.values.get("fed_repo_accepted"), b.values.get("fed_repo_days_since_positive"))
    )
    srf_old, srf_new = srf_totals(rule=False), srf_totals(rule=True)
    srf_moved = [
        {"date": d.isoformat(), "before_bn": srf_old.get(d), "after_bn": srf_new.get(d)}
        for d in sorted(set(srf_old) | set(srf_new)) if srf_old.get(d) != srf_new.get(d)
    ]
    ops = reclassified()
    return {
        "reclassified_operations": ops,
        "by_year": {"before": by_year(before), "after": by_year(after)},
        "panel_dates": len(after),
        "dates_with_a_changed_fed_repo_column": differing,
        "srf_total_dates_that_move": srf_moved,
        "srf_positive_days_to_2025_12_31": {
            "before": sum(1 for d, v in srf_old.items() if d <= date(2025, 12, 31) and v > 0),
            "after": sum(1 for d, v in srf_new.items() if d <= date(2025, 12, 31) and v > 0),
        },
    }


def markdown(result):
    ops = result["reclassified_operations"]
    ten = [o for o in ops if o["ten_zero_ten"]]
    other = [o for o in ops if not o["ten_zero_ten"]]
    lines = [
        "# The split test-trade rule and the take-up figures (#1456)",
        "",
        "**Serves:** H9 (secondary goal; `srf_total_accepted`) and H5 inputs (the `fed_repo_*` columns). Exploration on development data only: no verdict "
        "(scoring protocol v1, #640). No spread, forecast or score is read; no locked day counts toward a choice. Nothing here edits an earlier record: "
        "`docs/pivot/desk-test-marks-933-result.md` and `docs/pivot/afternoon-test-trade-938-result.md` stand and the figures below are published anew beside them.",
        "",
        "**The rule** (Eleonora, 4 November 2026, option (a) on finding #916): a `Repo` operation that accepted more than nothing and at most USD 35 million "
        "in total (`ingest.SPLIT_TEST_TOTAL_MAX`), split equally across the lines that accepted anything (at least two), is a Desk test trade, not take-up. "
        "It is read after the Desk-test marks and beside the rules of #802 and #938, by `ingest._effective_taken`. The date keeps a row, at zero.",
        "",
        f"## 1. The $10 mn / $0 / $10 mn days ({len(ten)})",
        "",
        "| date | operation | release | lines (mn) |",
        "|---|---|---|---|",
    ]
    for o in ten:
        lines.append(f"| {o['date']} | `{o['operation_id']}` | {o['release_time']} | {', '.join(f'{x:g}' for x in o['lines_mn'])} |")
    lines += [
        "",
        f"## 2. Other equal splits the rule as ruled also reaches ({len(other)}): MARKED QUESTION for Eleonora",
        "",
        "These are not $10 mn / $0 / $10 mn operations, but they meet the ruled wording (total at most $35 mn, equal across the accepted lines). "
        "The rule as written reclassifies them; the earlier finding on #916 counted them as take-up.",
        "",
        "| date | operation | release | total (mn) | lines (mn) |",
        "|---|---|---|---|---|",
    ]
    for o in other:
        lines.append(f"| {o['date']} | `{o['operation_id']}` | {o['release_time']} | {o['accepted_mn']:g} | {', '.join(f'{x:g}' for x in o['lines_mn'])} |")
    lines += [
        "",
        "## 3. `fed_repo_days_since_positive`, longest value / take-up days, by year",
        "",
        "| year | before | after |",
        "|---|---|---|",
    ]
    old, new = result["by_year"]["before"], result["by_year"]["after"]
    for year in old:
        a, b = old[year], new[year]
        mark = "" if a == b else " (moves)"
        lines.append(f"| {year} | {a['longest']:.0f} / {a['take_up_days']} | {b['longest']:.0f} / {b['take_up_days']}{mark} |")
    lines += [
        "",
        f"{len(result['dates_with_a_changed_fed_repo_column'])} of {result['panel_dates']} panel dates change in `fed_repo_accepted` or "
        "`fed_repo_days_since_positive` (the dates are in `result.json`).",
        "",
        "## 4. The Standing Repo Facility total (`srf_total_accepted`, USD bn)",
        "",
        "| date | before | after |",
        "|---|---|---|",
    ]
    for r in result["srf_total_dates_that_move"]:
        lines.append(f"| {r['date']} | {r['before_bn']} | {r['after_bn']} |")
    p = result["srf_positive_days_to_2025_12_31"]
    lines += [
        "",
        f"Operation days with a positive total, 2021-07-29 to 2025-12-31: {p['before']} before, {p['after']} after "
        "(the recount that `docs/DATA_QUALITY_DECISIONS.md` states and `NyFedSrfAdapterTests` checks).",
        "",
        "## Reproduce",
        "",
        "```",
        "PYTHONPATH=src python3 scripts/pressure_v1_1.py panel --end 2026-09-03 --output /tmp/AUG.csv",
        "PYTHONPATH=src python3 scripts/split_test_trade_1456.py --panel /tmp/AUG.csv --write",
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
