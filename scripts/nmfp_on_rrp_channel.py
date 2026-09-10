#!/usr/bin/env python3
"""Census the `FEDERAL RESERVE` counterparty in Form N-MFP, and the series it feeds.

`docs/DATA_QUALITY_DECISIONS.md` recorded, under "The ON RRP channel is declared,
empty, and unverified", that `mmf_on_rrp` "has never produced a single row against
real data" and that the substring `FEDERAL RESERVE` "occurs zero times in the
holdings table of the archive held". Both sentences were true of the one archive
held when they were written and are false of the ninety-seven held now. This
script is what says so, and it exists because that section's own open item was
that its claims were prose computed against a gitignored directory and
reproducible by nobody.

**The census is an independent re-derivation.** It does not import the adapter
and does not consult `NMFP_INVESTMENT_CATEGORY_ERAS`: it counts occurrences per
field, and classifies a holding as repo by the loose criterion that its
`INVESTMENTCATEGORY` contains "Repurchase Agreement". Loose on purpose -- the
adapter matches a closed set per era, so agreement between two criteria that
could differ is evidence, and the printed category breakdown is what makes a
vocabulary change visible rather than silently matched.

`--series` is the other thing, and it is *not* independent: it drives
`repo_model.ingest.parse_snapshots` over the same archives and prints the
`mmf_on_rrp` series the adapter actually produces. It is labelled as the
adapter's own output because that is what the panel claim is about.

Neither mode is in `tests/`: both read `data/raw/`, which no clone has, and a
test that cannot run in a clone is worse than no test. Same posture as
`scripts/nmfp_identity_residuals.py`, and the same refusal -- exit 2 if an
archive on disk is not in the declared set by SHA-256, because a count taken over
bytes nobody declared is not evidence about this repository's data.

Usage:

    PYTHONPATH=src python3 scripts/nmfp_on_rrp_channel.py \
        [--raw data/raw/sec_nmfp] \
        [--archives metadata/sec_nmfp_archives.json] \
        [--series] [--json OUT.json]

Stdlib only, like the package.
"""

from __future__ import annotations

import argparse
import collections
import csv
import glob
import io
import json
import os
import sys
import zipfile

HOLDINGS = "NMFP_SCHPORTFOLIOSECURITIES.tsv"
COLLATERAL = "NMFP_COLLATERALISSUERS.tsv"

#: The three fields the adapter joins before matching, in the order it joins
#: them. `src/repo_model/ingest.py` calls the join `counterparty`, and for a
#: repurchase agreement the counterparty *is* the issuer -- which is why two of
#: these three are issuer-identity fields and not description text.
COUNTERPARTY_FIELDS = ("NAMEOFISSUER", "TITLEOFISSUER", "BRIEFDESCRIPTION")

NEEDLE = "FEDERAL RESERVE"


def declared_archives(path):
    with open(path) as handle:
        payload = json.load(handle)
    return {entry["sha256"]: entry["url"].rsplit("/", 1)[-1] for entry in payload["archives"]}


def local_archives(raw_dir, declared):
    """Every archive on disk, checked against the declared set by SHA-256.

    The zip is found beside its manifest rather than at the manifest's recorded
    `path`, which is absolute and resolves only on the machine that fetched it.
    """

    found = []
    undeclared = []
    for manifest_path in sorted(glob.glob(os.path.join(raw_dir, "*.manifest.json"))):
        with open(manifest_path) as handle:
            manifest = json.load(handle)
        sha = manifest.get("sha256", "")
        zip_path = manifest_path[: -len(".manifest.json")]
        if sha not in declared:
            undeclared.append(os.path.basename(zip_path))
            continue
        if os.path.exists(zip_path):
            found.append((declared[sha], zip_path, manifest_path))
    if undeclared:
        sys.stderr.write(
            "refusing: %d archive(s) on disk are not in the declared set: %s\n"
            % (len(undeclared), ", ".join(sorted(undeclared)[:5]))
        )
        raise SystemExit(2)
    return sorted(found)


def census(archives):
    """Occurrences of the needle per field, and the rows the matcher would see."""

    per_field = collections.OrderedDict((name, 0) for name in COUNTERPARTY_FIELDS)
    collateral_hits = 0
    archives_with_hits = 0
    matched_rows = 0
    repo_rows = 0
    categories = collections.Counter()

    for _tag, zip_path, _manifest in archives:
        hit = False
        with zipfile.ZipFile(zip_path) as archive:
            names = set(archive.namelist())
            if HOLDINGS in names:
                with archive.open(HOLDINGS) as handle:
                    reader = csv.reader(
                        io.TextIOWrapper(handle, "utf-8", errors="replace"), delimiter="\t"
                    )
                    header = next(reader)
                    index = {
                        name: header.index(name)
                        for name in COUNTERPARTY_FIELDS + ("INVESTMENTCATEGORY",)
                        if name in header
                    }
                    for row in reader:

                        def cell(name):
                            position = index.get(name, -1)
                            return row[position] if 0 <= position < len(row) else ""

                        joined = " ".join(cell(name) for name in COUNTERPARTY_FIELDS).upper()
                        if NEEDLE not in joined:
                            continue
                        hit = True
                        matched_rows += 1
                        for name in COUNTERPARTY_FIELDS:
                            if NEEDLE in cell(name).upper():
                                per_field[name] += 1
                        category = cell("INVESTMENTCATEGORY")
                        categories[category] += 1
                        if "Repurchase Agreement" in category:
                            repo_rows += 1
            if COLLATERAL in names:
                collateral_hits += archive.read(COLLATERAL).upper().count(NEEDLE.encode())
        archives_with_hits += int(hit)

    return {
        "archives": len(archives),
        "archives_with_hits": archives_with_hits,
        "per_field": dict(per_field),
        "occurrences": sum(per_field.values()),
        "matched_rows": matched_rows,
        "repo_category_rows": repo_rows,
        "collateral_issuer_occurrences": collateral_hits,
        "categories": categories.most_common(),
    }


def series(archives, registry_path):
    """The `mmf_on_rrp` series the adapter produces, by calling the adapter.

    The manifest's `path` is rewritten to the archive beside it, for
    `local_archives`' reason. That cannot smuggle in different bytes:
    `load_snapshot_manifest` verifies the SHA-256 the manifest declares, and the
    declared set was verified before this function was reached.
    """

    import tempfile
    from pathlib import Path

    from repo_model.ingest import load_snapshot_manifest, parse_snapshots

    artifacts = []
    with tempfile.TemporaryDirectory() as scratch:
        for position, (_tag, zip_path, manifest_path) in enumerate(archives):
            with open(manifest_path) as handle:
                manifest = json.load(handle)
            manifest["path"] = os.path.abspath(zip_path)
            rewritten = Path(scratch) / ("%03d.manifest.json" % position)
            rewritten.write_text(json.dumps(manifest), encoding="utf-8")
            artifacts.append(load_snapshot_manifest(rewritten))
        parsed = parse_snapshots(artifacts, registry_path=Path(registry_path))

    rows = [row for row in parsed.rows if row.series_id == "mmf_on_rrp"]
    repo = [row for row in parsed.rows if row.series_id == "mmf_repo_holdings"]

    def latest(observations):
        """One value per reference date: the most recently observed vintage."""

        newest = {}
        for row in observations:
            current = newest.get(row.ref_date)
            if current is None or row.available_at > current.available_at:
                newest[row.ref_date] = row
        return {ref_date: row.value for ref_date, row in newest.items()}

    on_rrp = latest(rows)
    repo_by_date = latest(repo)
    if not on_rrp:
        return {"rows": 0, "ref_dates": 0}
    ordered = sorted(on_rrp)
    peak = max(on_rrp, key=on_rrp.get)
    absent = sorted(set(repo_by_date) - set(on_rrp))
    return {
        "rows": len(rows),
        "ref_dates": len(on_rrp),
        "first": (ordered[0].isoformat(), on_rrp[ordered[0]]),
        "last": (ordered[-1].isoformat(), on_rrp[ordered[-1]]),
        "peak": (peak.isoformat(), on_rrp[peak], 100.0 * on_rrp[peak] / repo_by_date[peak]),
        "repo_months_without_a_row": [ref_date.isoformat() for ref_date in absent],
        "leading": [(day.isoformat(), on_rrp[day]) for day in ordered[:4]],
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--raw", default="data/raw/sec_nmfp")
    parser.add_argument("--archives", default="metadata/sec_nmfp_archives.json")
    parser.add_argument("--registry", default="metadata/sources.json")
    parser.add_argument("--series", action="store_true")
    parser.add_argument("--json", dest="json_out")
    args = parser.parse_args(argv)

    archives = local_archives(args.raw, declared_archives(args.archives))
    if not archives:
        sys.stderr.write("no declared archives found under %s\n" % args.raw)
        raise SystemExit(2)

    report = {"census": census(archives)}
    counted = report["census"]
    print("archives read: %d, of which at least one match: %d"
          % (counted["archives"], counted["archives_with_hits"]))
    print("occurrences of %r in the joined counterparty fields: %d"
          % (NEEDLE, counted["occurrences"]))
    for name, total in counted["per_field"].items():
        print("    %-18s %d" % (name, total))
    print("rows matched: %d, of which repo-category: %d"
          % (counted["matched_rows"], counted["repo_category_rows"]))
    print("occurrences in %s: %d" % (COLLATERAL, counted["collateral_issuer_occurrences"]))
    print("categories carrying the needle:")
    for category, total in counted["categories"]:
        print("    %6d  %s" % (total, category[:72] or "(blank)"))

    if args.series:
        report["series"] = series(archives, args.registry)
        found = report["series"]
        print("")
        print("adapter output: %d mmf_on_rrp rows over %d reference dates"
              % (found["rows"], found["ref_dates"]))
        if found["rows"]:
            print("    first %s at %.2f bn, last %s at %.2f bn"
                  % (found["first"][0], found["first"][1], found["last"][0], found["last"][1]))
            print("    peak  %s at %.1f bn, %.1f%% of mmf_repo_holdings"
                  % (found["peak"][0], found["peak"][1], found["peak"][2]))
            print("    repo report-months carrying no mmf_on_rrp row: %d (%s .. %s)"
                  % (
                      len(found["repo_months_without_a_row"]),
                      found["repo_months_without_a_row"][0],
                      found["repo_months_without_a_row"][-1],
                  ))

    if args.json_out:
        with open(args.json_out, "w") as handle:
            json.dump(report, handle, indent=2, sort_keys=True, default=str)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
