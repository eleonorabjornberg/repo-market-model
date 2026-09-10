#!/usr/bin/env python3
"""Decompose the N-MFP accounting identity residual per reporting entity.

`metadata/sources.json` declares the identity

    mmf_cash + mmf_portfolio_securities + mmf_other_assets
      == mmf_liabilities + mmf_net_assets

and `src/repo_model/data.py` evaluates it on the *aggregated* cross-section: one
verdict per reference date, over sums taken across every reporting series. That
is the right unit for a panel check and the wrong unit for a finding. A defect
worth eight billion dollars in one filer's balance sheet arrives at the verdict
as one number attached to a whole month, indistinguishable from three hundred
funds each rounding in the same direction.

This script evaluates the same identity one filing at a time, so a residual can
be attributed. It exists because the derivations recorded in
`docs/DATA_QUALITY_DECISIONS.md` and in the registry's `tolerance_note` were both
published as prose, computed against a gitignored directory, and reproducible by
nobody -- which that section names as the open item it leaves behind. It is not
in `tests/`: it reads `data/raw/`, which no clone has, and a test that cannot run
in a clone is worse than no test.

**It is an independent re-derivation, not a call into the adapter.** It applies
the same two decisions the adapter applies -- supersession resolved on
`(SERIESID, REPORTDATE)` across every archive by latest `FILING_DATE`, and split
month-ends assembled into one report month -- but it reaches the numbers by its
own path. Agreement with `build`'s quality report is therefore evidence; a
disagreement is a finding about one of the two and is worth chasing rather than
reconciling by hand.

It applies no coverage floor. A cross-section too small for the panel still has
an arithmetic identity, and excluding it here would hide the population the floor
excludes rather than describe it. `--min-entities` filters the *printed* table
only, and says so in the header.

Usage:

    PYTHONPATH=src python3 scripts/nmfp_identity_residuals.py \
        [--raw data/raw/sec_nmfp] \
        [--archives metadata/sec_nmfp_archives.json] \
        [--min-entities 50] [--since 2023-01] [--json OUT.json]

Stdlib only, like the package. Exits 2 if an archive on disk does not match the
declared set by SHA-256, because a residual derived from bytes nobody declared is
not evidence about this repository's data.
"""

from __future__ import annotations

import argparse
import csv
import datetime
import glob
import io
import json
import os
import sys
import zipfile
from collections import defaultdict

SUBMISSION = "NMFP_SUBMISSION.tsv"
SERIESLEVEL = "NMFP_SERIESLEVELINFO.tsv"

#: The identity's terms, in the adapter's own column names. Kept in this order so
#: the printed residual is (assets) - (liabilities + net assets) and its sign
#: means what the tolerance note says it means: positive is assets exceeding.
ASSET_COLUMNS = ("CASH", "TOTALVALUEPORTFOLIOSECURITIES", "TOTALVALUEOTHERASSETS")
CLAIM_COLUMNS = ("TOTALVALUELIABILITIES", "NETASSETOFSERIES")

#: How a filing is classified once its residual is known. The ratio is
#:
#:     r = -((securities + other assets) - (liabilities + net assets)) / cash
#:
#: which is 1 when `CASH` is an additive component of total assets, as the form's
#: instructions define it, and 0 when the filer has already counted cash inside
#: another asset line and reports it again as a memo. Four bands, not two, and
#: the two that are neither answer are declared and printed rather than folded
#: into the nearest one:
#:
#:   |r| < 0.10          the cash line is a memo; the residual *is* that cash
#:   0.10 <= r < 0.90    a partial overlap -- a different finding if it clusters
#:   0.90 <= r <= 1.10   cash is additive, the ordinary case, residual near zero
#:   otherwise           a residual the cash line does not explain at all
#:
#: The band that matters is `cash_partial`. A threshold argument is only worth
#: making if the population is bimodal, and printing the middle is what lets a
#: reader see whether it is.
MEMO_MAX = 0.10
ADDITIVE_MIN = 0.90
ADDITIVE_MAX = 1.10

#: Filings below this are classified but never dominate a month, and including
#: them makes the ratio numerically meaningless -- a fund with two million
#: dollars of cash has a ratio set by rounding. In USD billions.
CASH_FLOOR = 0.05

BILLION = 1e9


def _number(raw, field):
    """The adapter's `_nmfp_number`, restated so this script depends on nothing.

    `"."` is treated as absent alongside `""`/`NA`/`N/A`, which is the adapter's
    behaviour and is undocumented there; it is written out here because a script
    that silently disagreed with the parser about absence would be comparing two
    different populations.
    """

    text = str(raw).strip() if raw is not None else ""
    if text.upper() in {"", "NA", "N/A", "."}:
        return None
    try:
        return float(text.replace(",", ""))
    except ValueError:
        raise SystemExit("%s is not numeric: %r" % (field, raw))


def _reader(archive, name):
    payload = archive.read(name)
    return csv.DictReader(io.StringIO(payload.decode("utf-8-sig")), delimiter="\t")


def _report_month(report_date):
    parsed = datetime.datetime.strptime(report_date, "%d-%b-%Y").date()
    return "%04d-%02d" % (parsed.year, parsed.month)


def declared_archives(path):
    with open(path) as handle:
        payload = json.load(handle)
    return {entry["sha256"]: entry["url"].rsplit("/", 1)[-1] for entry in payload["archives"]}


def local_archives(raw_dir, declared):
    """Every archive on disk, checked against the declared set by SHA-256."""

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
            found.append((declared[sha], zip_path))
    if undeclared:
        sys.stderr.write(
            "refusing: %d archive(s) on disk are not in the declared set: %s\n"
            % (len(undeclared), ", ".join(sorted(undeclared)[:5]))
        )
        raise SystemExit(2)
    return sorted(found)


def collect(archives):
    """Every series-level filing, keyed by `(SERIESID, REPORTDATE)`.

    Supersession is resolved here rather than per archive, because an amendment
    is routinely filed into a later archive than the original -- the decision
    recorded in `docs/DATA_QUALITY_DECISIONS.md` under "A cross-section is not an
    archive". The winner is the latest `FILING_DATE`; the archive order breaks a
    tie, which cannot happen on the declared set and is stated so that it is a
    rule rather than an accident of iteration.
    """

    filings = {}
    for tag, path in archives:
        with zipfile.ZipFile(path) as archive:
            names = set(archive.namelist())
            if SUBMISSION not in names or SERIESLEVEL not in names:
                continue
            submissions = {}
            for row in _reader(archive, SUBMISSION):
                submissions[row["ACCESSION_NUMBER"]] = row
            for row in _reader(archive, SERIESLEVEL):
                submission = submissions.get(row["ACCESSION_NUMBER"])
                if submission is None:
                    continue
                key = (submission["SERIESID"], submission["REPORTDATE"])
                filed = submission["FILING_DATE"]
                if key in filings and filings[key][0] > filed:
                    continue
                filings[key] = (filed, tag, submission, row)
    return filings


def classify(filing):
    """One filing's residual, and what its `CASH` line is doing in it."""

    _, tag, submission, row = filing
    values = [_number(row.get(column), column) for column in ASSET_COLUMNS + CLAIM_COLUMNS]
    if any(value is None for value in values):
        return None
    cash, securities, other, liabilities, net_assets = [value / BILLION for value in values]
    claims = liabilities + net_assets
    residual = (cash + securities + other) - claims
    without_cash = (securities + other) - claims
    kind = "unclassified"
    ratio = None
    if cash > CASH_FLOOR:
        ratio = -without_cash / cash
        if abs(ratio) < MEMO_MAX:
            kind = "cash_memo"
        elif ADDITIVE_MIN <= ratio <= ADDITIVE_MAX:
            kind = "cash_additive"
        elif MEMO_MAX <= ratio < ADDITIVE_MIN:
            kind = "cash_partial"
        else:
            kind = "cash_unexplained"
    return {
        "series_id": submission["SERIESID"],
        "series_name": submission.get("SERIES_NAME", ""),
        "registrant": submission.get("REGISTRANT", ""),
        "report_date": submission["REPORTDATE"],
        "report_month": _report_month(submission["REPORTDATE"]),
        "archive": tag,
        "cash": cash,
        "residual": residual,
        "residual_without_cash": without_cash,
        "assets": cash + securities + other,
        "kind": kind,
        "ratio": ratio,
    }


def by_month(evaluations):
    months = defaultdict(
        lambda: {
            "entities": 0,
            "assets": 0.0,
            "residual": 0.0,
            "memo_cash": 0.0,
            "memo_series": [],
            "partial_series": [],
        }
    )
    for item in evaluations:
        bucket = months[item["report_month"]]
        bucket["entities"] += 1
        bucket["assets"] += item["assets"]
        bucket["residual"] += item["residual"]
        if item["kind"] == "cash_memo":
            bucket["memo_cash"] += item["cash"]
            bucket["memo_series"].append(item["series_id"])
        elif item["kind"] == "cash_partial":
            bucket["partial_series"].append(item["series_id"])
    return months


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--raw", default="data/raw/sec_nmfp")
    parser.add_argument("--archives", default="metadata/sec_nmfp_archives.json")
    parser.add_argument("--min-entities", type=int, default=50)
    parser.add_argument("--since", default="")
    parser.add_argument("--json", default="")
    args = parser.parse_args(argv)

    declared = declared_archives(args.archives)
    archives = local_archives(args.raw, declared)
    if not archives:
        sys.stderr.write("no archives under %s; nothing to derive\n" % args.raw)
        return 2
    filings = collect(archives)
    evaluations = [item for item in (classify(f) for f in filings.values()) if item]
    months = by_month(evaluations)

    print(
        "%d archives, %d resolved filings, %d evaluable, %d report months"
        % (len(archives), len(filings), len(evaluations), len(months))
    )
    print(
        "printing months with at least %d reporting entities; the derivation "
        "applies no coverage floor" % args.min_entities
    )
    print(
        "%-9s %6s %11s %10s %8s %6s %11s %9s"
        % ("month", "n", "assets_bn", "resid_bn", "ppm", "memo_n", "memo_cash_bn", "less_memo")
    )
    for month in sorted(months):
        if args.since and month < args.since:
            continue
        bucket = months[month]
        if bucket["entities"] < args.min_entities:
            continue
        ppm = bucket["residual"] / bucket["assets"] * 1e6 if bucket["assets"] else 0.0
        print(
            "%-9s %6d %11.1f %10.3f %8.0f %6d %11.3f %9.3f"
            % (
                month,
                bucket["entities"],
                bucket["assets"],
                bucket["residual"],
                ppm,
                len(bucket["memo_series"]),
                bucket["memo_cash"],
                bucket["residual"] - bucket["memo_cash"],
            )
        )

    partial = [item for item in evaluations if item["kind"] == "cash_partial"]
    memo = [item for item in evaluations if item["kind"] == "cash_memo"]
    print(
        "\nfilings whose CASH is a memo already inside another asset line: %d, "
        "across %d report months" % (len(memo), len({item["report_month"] for item in memo}))
    )
    unexplained = [item for item in evaluations if item["kind"] == "cash_unexplained"]
    print(
        "filings in the partial band (%.2f <= r < %.2f): %d; filings whose residual the "
        "cash line does not explain at all: %d"
        % (MEMO_MAX, ADDITIVE_MIN, len(partial), len(unexplained))
    )
    worst = sorted(memo, key=lambda item: -item["cash"])[:10]
    for item in worst:
        print(
            "  %s %s  cash=%.3f bn  residual=%.3f bn  %s"
            % (
                item["report_month"],
                item["series_id"],
                item["cash"],
                item["residual"],
                item["series_name"][:44],
            )
        )

    if args.json:
        with open(args.json, "w") as handle:
            json.dump(
                {
                    "archives": [tag for tag, _ in archives],
                    "filings": len(filings),
                    "evaluable": len(evaluations),
                    "months": {
                        month: {
                            key: value
                            for key, value in bucket.items()
                            if key != "partial_series"
                        }
                        for month, bucket in months.items()
                    },
                },
                handle,
                indent=2,
                sort_keys=True,
            )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
