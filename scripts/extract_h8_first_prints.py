#!/usr/bin/env python3
"""Cut the tracked H.8 first-print extract out of the untracked archive snapshots.

`python3 -m repo_model.cli fetch h8` saves the Board's H.8 release-date index
and every archived release page in range, unmodified and checksummed, under the
gitignored `data/raw/frb_h8/` (#115, Eleonora's ruling of 2 October 2026,
option 3). What the model reads from them is one line -- total assets of all
commercial banks in the United States, not seasonally adjusted, USD billions --
and only its **first print**: for each week-ending Wednesday, the value in the
earliest release that carries that week. That is tracked, and only that: the
pages are about 0.7 MB each and several hundred of them.

Written under `tests/fixtures/snapshots/h8_inputs/frb_h8/`:

- `h8_total_assets_first_print.csv`, one row per week: `week_ending`,
  `total_assets`, `release_date`, `release_sha256`;
- its snapshot manifest, `<extract>.manifest.json`, in the shape every raw
  snapshot has, so `build --raw-root tests/fixtures/snapshots/h8_inputs` reads
  it like any other source. Its `retrieved_at` is the latest retrieval of any
  page it was cut from, and its `url` the archive's;
- `h8_total_assets_first_print.releases.json`, the SHA-256 manifest of the
  pages: per release, its date, URL, digest, size, retrieval time and the
  release time the page states (`null` where it states none).

Before writing, the script refuses:

- a release the index lists in range that has no snapshot, or two snapshots of
  one release with different bytes;
- a page that does not parse to exactly one total-assets line
  (`ingest.parse_frb_h8_total_assets`);
- a page that states a release time other than the declared 16:15
  (`ingest.FRB_H8_RELEASE_TIME`), since a later one would make the declaration
  early, which is the direction that leaks;
- a week missing between the first and the last, or a week first printed later
  than `frb_h8.release_lag` declares (`--registry`), for the same reason.

`--check` re-cuts and compares with the committed files, writing nothing.

    PYTHONPATH=src python3 scripts/extract_h8_first_prints.py
    PYTHONPATH=src python3 scripts/extract_h8_first_prints.py --check

Stdlib only.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import sys
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

from repo_model.ingest import (
    FRB_H8_ARCHIVE_URL,
    FRB_H8_EXTRACT_COLUMNS,
    FRB_H8_RELEASE_DATES_URL,
    FRB_H8_RELEASE_TIME,
    FRB_H8_SOURCE_ID,
    SnapshotArtifact,
    frb_h8_first_prints,
    load_snapshot_manifest,
    load_source_registry,
    parse_frb_h8_release_dates,
    parse_frb_h8_total_assets,
)

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data/raw"
OUTPUT = ROOT / "tests/fixtures/snapshots/h8_inputs" / FRB_H8_SOURCE_ID
EXTRACT_NAME = "h8_total_assets_first_print.csv"
RELEASES_NAME = "h8_total_assets_first_print.releases.json"


def _release_date(url: str) -> date:
    if not url.startswith(FRB_H8_ARCHIVE_URL) or not url.endswith("/"):
        raise ValueError(f"{url} is not an H.8 archive release page")
    stamp = url[len(FRB_H8_ARCHIVE_URL):-1]
    return date(int(stamp[:4]), int(stamp[4:6]), int(stamp[6:]))


def _snapshots(raw_root: Path):
    """The index (latest retrieval) and one artifact per release date."""

    index = None
    releases = {}
    for manifest in sorted((raw_root / FRB_H8_SOURCE_ID).glob("*.manifest.json")):
        artifact = load_snapshot_manifest(manifest)
        if artifact.url == FRB_H8_RELEASE_DATES_URL:
            if index is None or artifact.retrieved_at > index.retrieved_at:
                index = artifact
            continue
        day = _release_date(artifact.url)
        earlier = releases.get(day)
        if earlier is not None and earlier.sha256 != artifact.sha256:
            raise ValueError(
                f"two snapshots of the H.8 release of {day} differ: "
                f"{earlier.sha256} and {artifact.sha256}"
            )
        if earlier is None or artifact.retrieved_at < earlier.retrieved_at:
            releases[day] = artifact
    if index is None:
        raise ValueError(f"no H.8 release-date index under {raw_root / FRB_H8_SOURCE_ID}")
    return index, releases


def cut(raw_root: Path, start: date, end: date, declared_days: int):
    index, snapshots = _snapshots(raw_root)
    listed = [
        day
        for day in parse_frb_h8_release_dates(index.path.read_bytes())
        if start <= day <= end
    ]
    # A listed Friday the archive files under the Thursday before it (a Friday
    # holiday; `ingest.fetch_frb_h8_archive`) is that Thursday's snapshot.
    served = {}
    for day in listed:
        thursday = day - timedelta(days=1)
        if day in snapshots:
            served[day] = day
        elif thursday in snapshots and thursday not in listed:
            served[day] = thursday
    missing = [day for day in listed if day not in served]
    if missing:
        raise ValueError(
            f"{len(missing)} H.8 release(s) listed in range have no snapshot, "
            f"first {missing[0]}; run `fetch h8` over the range"
        )
    parsed = []
    records = []
    for listed_day in listed:
        day = served[listed_day]
        artifact = snapshots[day]
        release = parse_frb_h8_total_assets(artifact.path.read_bytes(), day)
        if day != listed_day and release.stated_date != day:
            raise ValueError(
                f"the H.8 index lists {listed_day}; the page under {day} states "
                f"{release.stated_date}"
            )
        if release.stated_time is not None and release.stated_time != FRB_H8_RELEASE_TIME:
            raise ValueError(
                f"the H.8 release of {day} states {release.stated_time}, not the "
                f"declared {FRB_H8_RELEASE_TIME}"
            )
        parsed.append((release, artifact.sha256))
        records.append(
            {
                "release_date": day.isoformat(),
                "listed_date": listed_day.isoformat(),
                "stated_release_date": (
                    None if release.stated_date is None else release.stated_date.isoformat()
                ),
                "public_on": release.public_on.isoformat(),
                "url": artifact.url,
                "sha256": artifact.sha256,
                "byte_count": artifact.byte_count,
                "retrieved_at": artifact.retrieved_at,
                "stated_release_time": (
                    None
                    if release.stated_time is None
                    else release.stated_time.isoformat(timespec="minutes")
                ),
            }
        )
    prints = frb_h8_first_prints(parsed)
    # The earliest release in range also carries three older weeks, whose first
    # prints were in releases before the range; only its newest week is a
    # first print here.
    earliest = max(parsed[0][0].weeks)
    prints = [item for item in prints if item.week_ending >= earliest]
    for earlier, later in zip(prints, prints[1:]):
        if (later.week_ending - earlier.week_ending).days != 7:
            raise ValueError(
                f"H.8 first prints skip from {earlier.week_ending} to {later.week_ending}"
            )
    for item in prints:
        lag = (item.release_date - item.week_ending).days
        if lag > declared_days:
            raise ValueError(
                f"the week ending {item.week_ending} was first printed on "
                f"{item.release_date}, {lag} days on, later than the {declared_days} "
                f"days frb_h8.release_lag declares"
            )
    buffer = io.StringIO(newline="")
    writer = csv.writer(buffer, lineterminator="\n")
    writer.writerow(FRB_H8_EXTRACT_COLUMNS)
    for item in prints:
        writer.writerow(
            (
                item.week_ending.isoformat(),
                format(item.value, ".1f"),
                item.release_date.isoformat(),
                item.release_sha256,
            )
        )
    extract = buffer.getvalue().encode("utf-8")
    retrieved = max(record["retrieved_at"] for record in records)
    manifest = SnapshotArtifact(
        source_id=FRB_H8_SOURCE_ID,
        path=Path(FRB_H8_SOURCE_ID) / EXTRACT_NAME,
        retrieved_at=retrieved,
        sha256=hashlib.sha256(extract).hexdigest(),
        url=FRB_H8_ARCHIVE_URL,
        byte_count=len(extract),
    ).as_dict()
    releases = {
        "index": {
            "url": index.url,
            "sha256": index.sha256,
            "retrieved_at": index.retrieved_at,
        },
        "start": start.isoformat(),
        "end": end.isoformat(),
        "releases": records,
    }
    lags = sorted({(item.release_date - item.week_ending).days for item in prints})
    summary = {
        "releases": len(records),
        "weeks": len(prints),
        "first_week": prints[0].week_ending.isoformat(),
        "last_week": prints[-1].week_ending.isoformat(),
        "first_print_lag_days": lags,
        "stated_release_times": sorted(
            {str(record["stated_release_time"]) for record in records}
        ),
    }
    return {
        EXTRACT_NAME: extract,
        EXTRACT_NAME + ".manifest.json": (
            json.dumps(manifest, indent=2, sort_keys=True) + "\n"
        ).encode("utf-8"),
        RELEASES_NAME: (json.dumps(releases, indent=2, sort_keys=True) + "\n").encode("utf-8"),
    }, summary


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--raw-root", type=Path, default=RAW)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    parser.add_argument("--registry", type=Path, default=ROOT / "metadata/sources.json")
    parser.add_argument("--start", type=date.fromisoformat, default=date(2018, 1, 1))
    parser.add_argument("--end", type=date.fromisoformat, default=date(2026, 9, 30))
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)

    declared = load_source_registry(args.registry)[FRB_H8_SOURCE_ID]["release_lag"]["days"]
    files, summary = cut(args.raw_root, args.start, args.end, int(declared))
    if args.check:
        stale = [
            name
            for name, payload in files.items()
            if not (args.output / name).is_file() or (args.output / name).read_bytes() != payload
        ]
        print(json.dumps({**summary, "stale": stale}, indent=2))
        return 1 if stale else 0
    args.output.mkdir(parents=True, exist_ok=True)
    for name, payload in files.items():
        (args.output / name).write_bytes(payload)
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
