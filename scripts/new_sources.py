#!/usr/bin/env python3
"""Snapshots, scratch panel and screen for the new data sources (#630).

An exploratory measurement, not a record: nothing is selected, no model changes, no published
figure moves, and no day after 2025-12-31 is read (`docs/decisions/lockbox.md`).

Step 2, the snapshots (each is one plain request per URL, made by the repository's own fetch code):

    PYTHONPATH=src python3 -m repo_model.cli fetch fr2004 --output-root /tmp/pd_export
    PYTHONPATH=src python3 scripts/new_sources.py extract-pd /tmp/pd_export/nyfed_fr2004/<export>.csv
    PYTHONPATH=src python3 scripts/new_sources.py fetch-dts

`extract-pd` cuts the five series `repo_model.new_sources.PD_SERIES` reads, up to 2025-12-31, out of the
26 MB export, copying lines byte for byte, and records the export's digest and size beside the extract
(the posture of `scripts/extract_fr2004.py`). `--check` recomputes the extract from the export and
compares. `fetch-dts` takes the Daily Treasury Statement's debt cash lines for 2018 to 2025.

The auction results and the Desk's operation records are read from snapshots already tracked
(`tests/fixtures/snapshots/treasury_auctions/`, `.../on_rrp_inputs/`); nothing is fetched for them.

Step 3 (the scratch panel and the screen) is in the second half of this file.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import sys
from datetime import date
from pathlib import Path
from typing import Dict, List, Optional

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))

from repo_model import new_sources  # noqa: E402

ROOT = REPO / "tests" / "fixtures" / "snapshots" / "new_sources"
PD_EXTRACT = ROOT / "nyfed_pd_financing" / "pd_financing_extract.csv"
FIRST_DTS_YEAR_START = "2018-01-01"


def cut_pd(raw: bytes) -> bytes:
    """The export's header and the lines of `PD_SERIES` dated up to `END`, byte for byte."""

    lines = raw.decode("utf-8-sig").splitlines(keepends=True)
    wanted = set(new_sources.PD_SERIES.values())
    out = [lines[0]]
    for line in lines[1:]:
        row = next(csv.reader([line]))
        if row[1] in wanted and date.fromisoformat(row[0]) <= new_sources.END:
            out.append(line)
    return "".join(out).encode("utf-8")


def pd_sidecar(export: bytes, export_manifest: dict, extract: bytes) -> dict:
    series: Dict[str, List[str]] = {}
    for row in csv.DictReader(io.StringIO(extract.decode("utf-8"))):
        series.setdefault(row["Time Series"], []).append(row["As Of Date"])
    return {
        "source_id": new_sources.SOURCE_PD,
        "url": new_sources.PD_EXPORT_URL,
        "retrieved_at": export_manifest.get("retrieved_at"),
        "export_sha256": hashlib.sha256(export).hexdigest(),
        "export_byte_count": len(export),
        "extract_sha256": hashlib.sha256(extract).hexdigest(),
        "extract_byte_count": len(extract),
        "kept": "the series of repo_model.new_sources.PD_SERIES, dated up to 2025-12-31, lines copied byte for byte",
        "series": {name: {"first": min(days), "last": max(days), "rows": len(days)} for name, days in sorted(series.items())},
    }


def extract_pd_command(args) -> int:
    export_path = Path(args.export)
    export = export_path.read_bytes()
    manifest_path = export_path.with_name(export_path.name + ".manifest.json")
    export_manifest = json.loads(manifest_path.read_text()) if manifest_path.exists() else {}
    extract = cut_pd(export)
    sidecar = pd_sidecar(export, export_manifest, extract)
    sidecar_path = PD_EXTRACT.with_name(PD_EXTRACT.name + ".manifest.json")
    text = json.dumps(sidecar, indent=2, sort_keys=True) + "\n"
    if args.check:
        committed = json.loads(sidecar_path.read_text())
        same = PD_EXTRACT.read_bytes() == extract and committed["export_sha256"] == sidecar["export_sha256"]
        print("extract matches" if same else "extract DIFFERS")
        return 0 if same else 1
    PD_EXTRACT.parent.mkdir(parents=True, exist_ok=True)
    PD_EXTRACT.write_bytes(extract)
    sidecar_path.write_text(text)
    print(json.dumps({"extract_bytes": len(extract), "export_sha256": sidecar["export_sha256"]}))
    return 0


def fetch_dts_command(args) -> int:
    artifacts = new_sources.fetch_dts_debt_cash(ROOT, args.start, args.end)
    print(json.dumps([{"url": a.url, "sha256": a.sha256, "bytes": a.byte_count} for a in artifacts], indent=1))
    return 0


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = parser.add_subparsers(dest="command", required=True)
    extract = sub.add_parser("extract-pd")
    extract.add_argument("export")
    extract.add_argument("--check", action="store_true")
    extract.set_defaults(func=extract_pd_command)
    fetch = sub.add_parser("fetch-dts")
    fetch.add_argument("--start", default=FIRST_DTS_YEAR_START)
    fetch.add_argument("--end", default=new_sources.END.isoformat())
    fetch.set_defaults(func=fetch_dts_command)
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
