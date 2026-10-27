"""Fetch the Wayback captures of SIFMA's agency MBS settlement-date calendars (#1276, H5 step 3).

Evidence for the availability declaration of the MBS settlement-day arm: when was each year's calendar first
public? For each SIFMA URL this lists every capture (CDX index), keeps the earliest capture per calendar year, saves
the captured bytes (raw, `id_` flavour) and writes `manifest.json` with each capture's timestamp and SHA-256.
Publication dates are read from this evidence only, never guessed. No score is computed here.

    python3 scripts/sifma_wayback_fetch_1276.py --out data/sifma-wayback-1276

`--base` replaces https://web.archive.org (used by the smoke test against a local stub). Stdlib only.
"""
import argparse
import hashlib
import json
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

URLS = (
    "https://www.sifma.org/resources/general/mbs-notification-and-settlement-dates/",
    "https://www.sifma.org/wp-content/uploads/2024/08/SIFMASettlementDatesCalendar-2026-2027.xlsx",
    "https://www.sifma.org/wp-content/uploads/2024/04/TBA_Market_Governance-MBS_Notification_Settlement_Dates_.xlsx",
)


def get(url, tries=4):
    for attempt in range(tries):
        try:
            with urllib.request.urlopen(url, timeout=120) as response:
                return response.read()
        except OSError as exc:
            if attempt == tries - 1:
                raise
            print(f"retry {attempt + 1} after {exc!r}", file=sys.stderr)
            time.sleep(2 ** (attempt + 1))


def captures(base, url):
    query = urllib.parse.urlencode(
        {"url": url, "output": "json", "fl": "timestamp,statuscode,digest", "filter": "statuscode:200"}
    )
    rows = json.loads(get(f"{base}/cdx/search/cdx?{query}") or b"[]")
    return [dict(zip(rows[0], row)) for row in rows[1:]]


def earliest_per_year(rows):
    first = {}
    for row in sorted(rows, key=lambda r: r["timestamp"]):
        first.setdefault(row["timestamp"][:4], row)
    return first


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--out", default="data/sifma-wayback-1276")
    parser.add_argument("--base", default="https://web.archive.org")
    args = parser.parse_args(argv)
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    manifest = []
    for url in URLS:
        rows = captures(args.base, url)
        print(f"{len(rows)} captures of {url}")
        for year, row in earliest_per_year(rows).items():
            body = get(f"{args.base}/web/{row['timestamp']}id_/{url}")
            name = f"{row['timestamp']}-{hashlib.sha256(url.encode()).hexdigest()[:8]}-{Path(urllib.parse.urlparse(url).path.rstrip('/')).name}"
            (out / name).write_bytes(body)
            manifest.append(
                {
                    "url": url,
                    "year": year,
                    "capture_timestamp": row["timestamp"],
                    "file": name,
                    "sha256": hashlib.sha256(body).hexdigest(),
                    "bytes": len(body),
                }
            )
            print(f"  {year}: {row['timestamp']} {len(body)} bytes")
    (out / "manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")
    print(f"wrote {len(manifest)} captures and manifest.json to {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
