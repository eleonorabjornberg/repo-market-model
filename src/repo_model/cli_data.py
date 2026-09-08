"""Track A's command-line surface: the data layer's subcommands.

Owned by **Track A (data layer)**. The ownership gate fails a
`feature/model-eval` branch that touches this file.

`src/repo_model/cli.py` is a dispatcher that names no command. To add one, add
it here: build the subparser and call `set_defaults(handler=...)` on it. Nothing
outside this file changes -- not the dispatcher, not the contract, not the gate.
A handler takes the parsed namespace and returns an exit code; it may raise
`OSError` or any `ValueError` subclass (`DataContractError` is one) and the
dispatcher will print it and exit 2.

Stdlib only, by contract.
"""

from __future__ import annotations

import argparse
import json
import os
from datetime import date, datetime, time
from pathlib import Path

from .data import (
    audit_panel,
    build_daily_panel,
    load_daily_panel,
    load_point_in_time_panel,
    write_daily_panel,
)
from .ingest import (
    DEFAULT_SOURCE_REGISTRY,
    SEC_NMFP_ARCHIVE_MANIFEST,
    build_point_in_time_snapshot,
    fetch_fred_macro,
    fetch_nyfed_reference_rate,
    fetch_sec_nmfp_archives,
    load_snapshot_manifest,
    load_sec_nmfp_archive_manifest,
    load_source_registry,
    write_sec_nmfp_archive_manifest,
)


def _audit(args: argparse.Namespace) -> int:
    report = audit_panel(load_daily_panel(args.path))
    print(
        json.dumps(
            {
                "rows": report.row_count,
                "start_date": report.start_date.isoformat(),
                "end_date": report.end_date.isoformat(),
                "missing_counts": report.missing_counts,
                "warnings": list(report.warnings),
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


def _fetch(args: argparse.Namespace) -> int:
    if args.source == "nyfed-sofr":
        artifacts = fetch_nyfed_reference_rate(
            output_root=args.output_root,
            rate_name="sofr",
            start=args.start,
            end=args.end,
        )
    else:
        artifacts = fetch_fred_macro(output_root=args.output_root)
    print(json.dumps([artifact.as_dict() for artifact in artifacts], indent=2))
    return 0


def _backfill_nmfp(args: argparse.Namespace) -> int:
    """Fetch the declared Form N-MFP archive set and update its manifest.

    The contact email comes from the environment rather than the command line so
    it is not left behind in a shell history or a committed invocation. SEC
    requires a declaring contact in the User-Agent and rejects requests without
    one.
    """

    contact_email = os.environ.get("SEC_CONTACT_EMAIL", "").strip()
    if not contact_email:
        raise ValueError(
            "set SEC_CONTACT_EMAIL to the address SEC should contact about this "
            "traffic; it is sent in the User-Agent and SEC requires it"
        )
    records = load_sec_nmfp_archive_manifest(args.manifest)
    updated = fetch_sec_nmfp_archives(
        args.output_root,
        records,
        contact_email=contact_email,
        recheck=args.recheck,
    )
    write_sec_nmfp_archive_manifest(
        updated,
        args.manifest,
        index_url=json.loads(args.manifest.read_text(encoding="utf-8")).get(
            "index_url", ""
        ),
    )
    admitted = [record for record in updated if record.admitted]
    # `refused` and `short_a_table` are counted separately because they are
    # different claims about a file. An archive short a table is admitted and
    # contributes every field its other tables supply; a refused one contributes
    # nothing. Reporting them as one number was what made fourteen years of
    # balance sheets look like fourteen years of unreadable archives.
    short = [record for record in admitted if record.absent_fields]
    print(
        json.dumps(
            {
                "declared": len(updated),
                "admitted": len(admitted),
                "refused": len(updated) - len(admitted),
                "short_a_table": len(short),
                "absent_fields": sorted(
                    {field for record in short for field in record.absent_fields}
                ),
                "manifest": str(args.manifest),
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


def _build(args: argparse.Namespace) -> int:
    """Build the wide daily panel from the raw snapshots on disk.

    Two hops, in one command, because until now neither end was reachable:
    `build_point_in_time_snapshot` was called only from tests, and nothing at
    all turned its long output into `DailyObservation`.

    The build cutoff is an argument and is recorded in the manifest. It is a
    property of the build -- "what a builder standing here could have known" --
    not of a row and not of the model, so it is declared once, out loud, rather
    than defaulting to the wall clock and making two runs of the same command
    incomparable.

    `--decision-time` is passed straight through to the pricing function, which
    is the only thing that reads it. It does not move a value: the join does
    not subtract the release lag, the purge does.
    """

    manifests = sorted(args.raw_root.glob("*/*.manifest.json"))
    if args.source:
        wanted = set(args.source)
        manifests = [item for item in manifests if item.parent.name in wanted]
    if not manifests:
        raise ValueError(f"no raw snapshot manifests under {args.raw_root}")
    artifacts = [load_snapshot_manifest(item) for item in manifests]

    args.output.parent.mkdir(parents=True, exist_ok=True)
    long_path = args.output.with_name(args.output.stem + "_point_in_time.csv")
    snapshot = build_point_in_time_snapshot(
        artifacts, long_path, registry_path=args.registry
    )
    rows = load_point_in_time_panel(long_path)

    build = build_daily_panel(
        rows,
        load_source_registry(args.registry),
        build_cutoff=datetime.fromisoformat(args.build_cutoff.replace("Z", "+00:00")),
        decision_time=time.fromisoformat(args.decision_time),
    )
    manifest_path = write_daily_panel(
        build, args.output, source_shas=snapshot.source_shas
    )
    dates = [observation.date for observation in build.observations]
    print(
        json.dumps(
            {
                "panel": str(args.output),
                "manifest": str(manifest_path),
                "point_in_time_rows": snapshot.row_count,
                "rows": len(build.observations),
                "start_date": dates[0].isoformat(),
                "end_date": dates[-1].isoformat(),
                "build_cutoff": build.build_cutoff.isoformat(),
                "built_columns": list(build.built_columns),
                "refused_columns": dict(build.refusals),
                "holes": dict(build.holes),
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


def register(subparsers: argparse._SubParsersAction) -> None:
    """Add the data layer's subcommands to the shared parser."""

    audit = subparsers.add_parser("audit", help="validate and summarize a daily panel")
    audit.add_argument("path", type=Path)
    audit.set_defaults(handler=_audit)

    fetch = subparsers.add_parser(
        "fetch", help="download an immutable public-data snapshot"
    )
    fetch.add_argument("source", choices=("nyfed-sofr", "fred-macro"))
    fetch.add_argument("--start", default="2018-04-03", help="effective start date")
    fetch.add_argument(
        "--end", default=date.today().isoformat(), help="effective end date"
    )
    fetch.add_argument("--output-root", type=Path, default=Path("data/raw"))
    fetch.set_defaults(handler=_fetch)

    build = subparsers.add_parser(
        "build",
        help="join the raw snapshots into the wide daily panel and its manifest",
    )
    build.add_argument("--raw-root", type=Path, default=Path("data/raw"))
    build.add_argument("--output", type=Path, default=Path("data/processed/daily_panel.csv"))
    build.add_argument(
        "--registry", type=Path, default=DEFAULT_SOURCE_REGISTRY
    )
    build.add_argument(
        "--source",
        action="append",
        metavar="SOURCE_ID",
        help="build from this raw source only, repeatable; default is every "
        "source with a snapshot on disk",
    )
    build.add_argument(
        "--build-cutoff",
        required=True,
        metavar="ISO8601",
        help="a cell carries the latest vintage available at this instant; "
        "must carry a UTC offset, and is recorded in the manifest",
    )
    build.add_argument(
        "--decision-time",
        required=True,
        metavar="HH:MM",
        help="passed through to registry.max_release_lag_days, which decides "
        "which columns latest vintage may carry; it never moves a value",
    )
    build.set_defaults(handler=_build)


    backfill = subparsers.add_parser(
        "backfill-nmfp",
        help="fetch the declared Form N-MFP archive set, skipping what is present",
    )
    backfill.add_argument("--output-root", type=Path, default=Path("data/raw"))
    backfill.add_argument(
        "--manifest", type=Path, default=SEC_NMFP_ARCHIVE_MANIFEST
    )
    backfill.add_argument(
        "--recheck",
        action="store_true",
        help="re-download and re-judge archives already recorded, for when the "
        "parser's requirements have changed",
    )
    backfill.set_defaults(handler=_backfill_nmfp)
