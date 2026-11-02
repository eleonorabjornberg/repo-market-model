#!/usr/bin/env python3
"""Fetch and check the New York Fed primary-dealer financing series behind OFR chart 22 (#1296; H5 step 3, ledger item 72 on #1116).

    python3 scripts/fetch_pd_financing_1296.py fetch PDSIRRA-UTSETTOT     # one plain GET of one series, then rewrites the manifest
    python3 scripts/fetch_pd_financing_1296.py fetch release-page        # one plain GET of the page that states the release day and time
    python3 scripts/fetch_pd_financing_1296.py check                     # offline: every tracked byte against the manifest

The four series are the New York Fed Primary Dealer Statistics (FR 2004) totals for reverse repurchase agreements
(`PDSIRRA-`) and for securities borrowed (`PDSIOSB-`) on U.S. Treasury securities, excluding and including TIPS. The
Office of Financial Research's "Primary dealer reverse repo and securities borrowing by tenor" (Short-term Funding Monitor,
market digest chart 22) shows the Treasury ("T") rows of these two financing lines by tenor. Each URL is

    https://markets.newyorkfed.org/api/pd/get/<keyid>.json

and is fetched with one plain GET. The response is stored byte for byte beside `manifest.json`, which records for each file the
URL, the SHA-256, the byte count and the retrieval instant. `fetch` keeps the manifest entry of every other series as it is.
`check` exits 1 when a tracked file differs from its manifest entry or is missing, and does no network I/O. Standard library
only. The release time of the series and the evidence for it are in `metadata/sources_pd_financing_1296.json`.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, Sequence

REPO = Path(__file__).resolve().parents[1]
SNAPSHOT = REPO / "tests" / "fixtures" / "snapshots" / "nyfed-pd-financing"
MANIFEST = SNAPSHOT / "manifest.json"
BASE_URL = "https://markets.newyorkfed.org/api/pd/get/"
SERIES = ("PDSIRRA-UTSETTOT", "PDSIRRA-UTSTTOT", "PDSIOSB-UTSETTOT", "PDSIOSB-UTSTTOT")
PAGE_KEY = "release-page"
KEYS = SERIES + (PAGE_KEY,)
SOURCE_ID = "nyfed_pd_financing"
#: The page that states when the series are released, kept as the evidence for the release time (`metadata/sources_pd_financing_1296.json`).
PAGE_URL = "https://www.newyorkfed.org/markets/counterparties/primary-dealers-statistics"
PAGE_FILE = "primary-dealers-statistics.html"


def file_name(key: str) -> str:
    return PAGE_FILE if key == PAGE_KEY else f"{key}.json"


def url_of(key: str) -> str:
    return PAGE_URL if key == PAGE_KEY else f"{BASE_URL}{key}.json"


def entry_of(key: str, raw: bytes, retrieved_at: str) -> dict:
    return {
        "keyid": key, "path": f"tests/fixtures/snapshots/nyfed-pd-financing/{file_name(key)}", "url": url_of(key),
        "sha256": hashlib.sha256(raw).hexdigest(), "byte_count": len(raw), "retrieved_at": retrieved_at,
    }


def fetch(key: str) -> int:
    if key not in KEYS:
        raise SystemExit(f"{key} is not one of {', '.join(KEYS)}")
    with urllib.request.urlopen(url_of(key), timeout=60) as response:  # one plain GET
        raw = response.read()
    if key == PAGE_KEY:
        if b"Thursdays" not in raw:
            raise SystemExit("the page does not state a release day: it is not the page the evidence rests on")
    else:
        json.loads(raw.decode("utf-8"))["pd"]["timeseries"]  # refuses a body that is not the series
    SNAPSHOT.mkdir(parents=True, exist_ok=True)
    (SNAPSHOT / file_name(key)).write_bytes(raw)
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8")) if MANIFEST.exists() else {"source_id": SOURCE_ID, "files": []}
    stamp = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    files = {item["keyid"]: item for item in manifest["files"]}
    files[key] = entry_of(key, raw, stamp)
    manifest["files"] = [files[k] for k in KEYS if k in files]
    MANIFEST.write_text(json.dumps(manifest, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    return 0


def check(root: Path = REPO, manifest_path: Optional[Path] = None) -> int:
    path = manifest_path or MANIFEST
    manifest = json.loads(path.read_text(encoding="utf-8"))
    bad = []
    seen = {item["keyid"] for item in manifest["files"]}
    for key in KEYS:
        if key not in seen:
            bad.append(f"{key}: not in the manifest")
    for item in manifest["files"]:
        target = root / item["path"]
        if not target.exists():
            bad.append(f"{item['keyid']}: {item['path']} is missing")
            continue
        raw = target.read_bytes()
        if hashlib.sha256(raw).hexdigest() != item["sha256"] or len(raw) != item["byte_count"]:
            bad.append(f"{item['keyid']}: {item['path']} differs from its manifest entry")
    for line in bad:
        print(line, file=sys.stderr)
    if not bad:
        print("ok")
    return 1 if bad else 0


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="command", required=True)
    f = sub.add_parser("fetch", help="one plain GET of one series")
    f.add_argument("key", choices=KEYS)
    sub.add_parser("check", help="offline: tracked bytes against the manifest")
    args = parser.parse_args(argv)
    return fetch(args.key) if args.command == "fetch" else check()


if __name__ == "__main__":
    sys.exit(main())
