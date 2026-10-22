#!/usr/bin/env python3
"""Which SOFR dates since 2018-04-03 were revised, and what a revision could do to H5's labels (#940, criterion 2).

    PYTHONPATH=src python3 scripts/sofr_revisions_940.py
    PYTHONPATH=src python3 scripts/sofr_revisions_940.py --check

Development data, not a verdict. Reads the tracked current-vintage SOFR snapshot
(`tests/fixtures/snapshots/funding_inputs/nyfed-sofr-rate/`, checked against its manifest) and the tracked IORB
announcement table, and writes `metadata/sofr_revisions_940.json` and `docs/research/sofr-revisions-940.md`.

What it can say and what it cannot:

* **Revised dates.** The API's `revisionIndicator` is the only field that could flag one. It is counted over every
  row. A revision replaces the value, so a date the field does not flag cannot be shown to have been revised.
* **First prints.** The API serves the current vintage only. No tracked snapshot, and no source reachable from the
  cloud environment that runs this directive, holds a SOFR vintage from before a revision (ALFRED is refused by the
  environment's egress proxy). Where the first print cannot be recovered the paired effect on H5's grid CRPS for
  `gbm_funding`, B1 and B2 is not computed, and the figures here are labelled "current vintage".
* **Exposure** (not an effect): the number of days whose label at +0, +5 and +10 bp sits within a revision's reach.
  The New York Fed revises only a change of more than one basis point, and SOFR is quoted to the basis point, so a
  revision moves the spread by at least 2 bp. A day with spread `s` can change label under such a revision only if
  `tau - 1 <= s <= tau + 2` (up from `s <= tau`, down from `s > tau`). The count is an upper bound on the days at
  risk, given that some revision happened that day; it says nothing about how many did.

Correction (#1019): "upper bound" below is wrong. The window is the reach of a 2 bp revision, the smallest the New
York Fed makes; larger revisions reach further. See `docs/research/sofr-revision-exposure-1019-result.md`.

Only days on or before 2025-12-31 are counted (`docs/decisions/lockbox.md` locks every later day).

Stdlib only.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import sys
from collections import Counter
from datetime import date
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))

from repo_model.data import exceeds_bp  # noqa: E402

SNAPSHOT = REPO / "tests" / "fixtures" / "snapshots" / "funding_inputs" / "nyfed-sofr-rate"
IORB_TABLE = REPO / "tests" / "fixtures" / "snapshots" / "fed-iorb-announcements" / "iorb_changes.csv"
FIRST_DAY = date(2018, 4, 3)
LAST_DAY = date(2025, 12, 31)
THRESHOLDS = (0, 5, 10)
OUT_JSON = REPO / "metadata" / "sofr_revisions_940.json"
OUT_MD = REPO / "docs" / "research" / "sofr-revisions-940.md"
#: The 19 October 2026 fetch of the same range with `repo_model.cli fetch nyfed-sofr` returned bytes with this digest.
REFETCH_SHA256 = "3a5e2244641595a89daa35a0643e0d1d5328e9149496d3a172cad784314519e1"


def _snapshot():
    manifests = sorted(SNAPSHOT.glob("*.manifest.json"))
    if len(manifests) != 1:
        raise ValueError(f"{SNAPSHOT}: expected one manifest")
    manifest = json.loads(manifests[0].read_text(encoding="utf-8"))
    data_path = REPO / "tests" / "fixtures" / "snapshots" / "funding_inputs" / manifest["path"]
    raw = data_path.read_bytes()
    if hashlib.sha256(raw).hexdigest() != manifest["sha256"]:
        raise ValueError(f"{data_path} does not match its manifest")
    return manifest, json.loads(raw)["refRates"]


def _iorb_rows():
    manifest = json.loads(IORB_TABLE.with_name(IORB_TABLE.name + ".manifest.json").read_text(encoding="utf-8"))
    if hashlib.sha256(IORB_TABLE.read_bytes()).hexdigest() != manifest["sha256"]:
        raise ValueError(f"{IORB_TABLE} does not match its manifest")
    with IORB_TABLE.open(newline="", encoding="utf-8") as handle:
        return [(date.fromisoformat(r["effective_date"]), float(r["rate_percent"])) for r in csv.DictReader(handle)]


def _iorb_on(rows, day):
    rate = None
    for effective, value in rows:
        if effective <= day:
            rate = value
    if rate is None:
        raise ValueError(f"no IORB rate in force on {day}")
    return rate


def build():
    manifest, rows = _snapshot()
    indicators = Counter(str(r.get("revisionIndicator", "")).strip() for r in rows)
    dates = sorted(date.fromisoformat(r["effectiveDate"]) for r in rows)
    flagged = sorted(r["effectiveDate"] for r in rows if str(r.get("revisionIndicator", "")).strip())
    iorb = _iorb_rows()
    spreads = {}
    for r in rows:
        day = date.fromisoformat(r["effectiveDate"])
        if FIRST_DAY <= day <= LAST_DAY:
            spreads[day] = round((float(r["percentRate"]) - _iorb_on(iorb, day)) * 100)
    exposure = {}
    for tau in THRESHOLDS:
        above = sum(1 for s in spreads.values() if exceeds_bp(s, tau))
        at_risk = sum(1 for s in spreads.values() if tau - 1 <= s <= tau + 2)
        exposure[f"+{tau}"] = {"days_above": above, "days_within_reach_of_a_revision": at_risk}
    return {
        "status": "development data, not a verdict",
        "directive": "eleonorabjornberg/repo-market-model#940",
        "snapshot": {
            "path": manifest["path"],
            "sha256": manifest["sha256"],
            "retrieved_at": manifest["retrieved_at"],
            "url": manifest["url"],
            "refetch_19_october_2026_sha256": REFETCH_SHA256,
            "refetch_identical": REFETCH_SHA256 == manifest["sha256"],
        },
        "rows": len(rows),
        "first_row": dates[0].isoformat(),
        "last_row": dates[-1].isoformat(),
        "revision_indicator_values": dict(sorted(indicators.items())),
        "dates_flagged_revised": flagged,
        "first_prints_recoverable": False,
        "vintage": "current vintage",
        "window": {"first": FIRST_DAY.isoformat(), "last": LAST_DAY.isoformat(), "days": len(spreads)},
        "exposure": exposure,
    }


def render(result):
    ind = ", ".join(f"`{k or 'blank'}`: {v}" for k, v in result["revision_indicator_values"].items())
    lines = [
        "# SOFR revisions and first prints: what the repository can show (#940)",
        "",
        "**Development data, not a verdict.** Generated by `python3 scripts/sofr_revisions_940.py`; never hand-edited.",
        "Serves H5 (primary goal), groundwork for confirmation. All figures are **current vintage**.",
        "",
        "## Which SOFR dates were revised",
        "",
        f"The tracked snapshot (`{result['snapshot']['path']}`, digest `{result['snapshot']['sha256'][:12]}…`,",
        f"retrieved {result['snapshot']['retrieved_at']}) holds {result['rows']} rows from {result['first_row']} to",
        f"{result['last_row']}. The API's `revisionIndicator` is {ind}. "
        f"Dates it flags as revised: {len(result['dates_flagged_revised'])}.",
        "A fetch of the same range with the repository's fetcher on 19 October 2026 returned the same bytes"
        if result["snapshot"]["refetch_identical"]
        else "A fetch of the same range with the repository's fetcher on 19 October 2026 returned different bytes",
        f"(digest `{result['snapshot']['refetch_19_october_2026_sha256'][:12]}…`).",
        "",
        "The field is blank on every row, and a revision replaces the value, so **no date can be shown to have been",
        "revised from this data**. The New York Fed's page states the rule (a same-day revision at about 14:30 ET, only",
        "for a change of more than one basis point) but publishes no list of revised dates that this environment could",
        "reach.",
        "",
        "## First prints for the past",
        "",
        "**Not recoverable here.** The API serves the current vintage only; no tracked snapshot holds a vintage from",
        "before a revision; ALFRED, the one tracked route to vintages, is refused by this environment's egress proxy",
        "(it was not worked around). The paired effect of the first print on H5's grid CRPS for `gbm_funding`, B1 and B2,",
        "by lead, and on the +0, +5 and +10 bp exceedance labels, is therefore **not computed**: there is no revised",
        "date to compute it on. Every earlier H5 figure stays labelled \"current vintage\", as `metadata/spread_distribution_634.json`",
        "already says. First prints from now on are kept by `scripts/sofr_first_print.py` (`.github/workflows/sofr-first-print.yml`).",
        "",
        "## Exposure of the labels (an upper bound, not an effect)",
        "",
        "> **Correction (#1019).** \"Upper bound\" here is wrong: this window is the reach of a 2 bp revision, the",
        "> smallest the New York Fed makes, and larger revisions reach further. The counts by revision size, and the",
        "> corrected wording, are in [`sofr-revision-exposure-1019-result.md`](sofr-revision-exposure-1019-result.md).",
        "> The figures below stand.",
        "",
        f"Days {result['window']['first']} to {result['window']['last']} ({result['window']['days']} days with a SOFR row;",
        "`docs/decisions/lockbox.md` locks every later day). Spread = SOFR less the IOER or IORB in force that day (the",
        "tracked announcement table), on whole basis points, a day above a threshold when strictly above it. A revision",
        "moves the spread by at least 2 bp, so a day can change label only if its spread is within 1 bp below to 2 bp",
        "above the threshold. That bounds the days at risk if a revision happened on them; it does not say any did.",
        "",
        "| Threshold | Days above | Days within reach of a revision |",
        "|---|---|---|",
    ]
    for key, cell in result["exposure"].items():
        lines.append(f"| {key} bp | {cell['days_above']} | {cell['days_within_reach_of_a_revision']} |")
    lines += [
        "",
        "## Not checked",
        "",
        "- The panel's `spread_bps` itself: this page recomputes the spread from the snapshot and the table, which is",
        "  how the panel is built, but does not read the panel.",
        "- Any date's revision status. The decision on how a same-day revision is treated, and which vintage is the",
        "  outcome, is Eleonora's; nothing here settles it.",
        "",
    ]
    return "\n".join(lines)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--check", action="store_true", help="compare with the committed files; write nothing")
    args = parser.parse_args(argv)
    result = build()
    payload = json.dumps(result, indent=1, sort_keys=True) + "\n"
    page = render(result)
    if args.check:
        if OUT_JSON.read_text(encoding="utf-8") != payload or OUT_MD.read_text(encoding="utf-8") != page:
            print("stale: run python3 scripts/sofr_revisions_940.py", file=sys.stderr)
            return 1
        print("ok")
        return 0
    OUT_JSON.write_text(payload, encoding="utf-8")
    OUT_MD.write_text(page, encoding="utf-8")
    print(f"wrote {OUT_JSON.relative_to(REPO)} and {OUT_MD.relative_to(REPO)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
