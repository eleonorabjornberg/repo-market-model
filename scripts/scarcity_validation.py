#!/usr/bin/env python3
"""Validate the reserve-scarcity state on pressure-day frequency (#115, step 3).

Builds the measurement panel from tracked fixtures only, with no network:

- `tests/fixtures/snapshots/funding_inputs/`, the published panel's inputs,
  built with the published manifest's columns, cutoff and decision time;
- `tests/fixtures/snapshots/on_rrp_inputs/`, the Desk's operation results (#45);
- `tests/fixtures/snapshots/h8_inputs/`, the H.8 first prints
  (`scripts/extract_h8_first_prints.py`).

`on_rrp`, `bank_total_assets` and `reserve_scarcity_state` are off in the
published declaration; the build switches them on for itself
(`scarcity.measurement_declaration`). Before anything is scored the script
checks that the published columns of this build are the published panel: the
same build restricted to `metadata/funding_panel_manifest.json`'s columns must
reproduce its digest, or the script stops.

Then every scored day of the shared fold grid, through `--end`, is paired with
its as-of state and its own SOFR - IORB (`scarcity.pressure_days_by_state`;
the lockbox refuses a scored day on or after 2026-01-01), and
`scarcity.tabulate` reports the frequency of days above +5 and +10 bp per state
and per year, with stationary-bootstrap intervals. The declared cut-points are
scored, and so is each sensitivity variant (`scarcity.SENSITIVITY_VARIANTS`),
side by side; none is chosen by what it scores.

Nothing is published by running it.

    PYTHONPATH=src python3 scripts/scarcity_validation.py --end 2025-12-31 \
        [--json OUT.json] [--markdown OUT.md]

Stdlib only.
"""

from __future__ import annotations

import argparse
import json
import sys
import tempfile
from datetime import date, datetime, time
from pathlib import Path

from repo_model.data import (
    build_daily_panel,
    load_point_in_time_panel,
    verify_daily_panel,
    write_daily_panel,
)
from repo_model.ingest import (
    build_point_in_time_snapshot,
    load_snapshot_manifest,
    load_source_registry,
)
from repo_model.scarcity import (
    STATE_LABELS,
    SENSITIVITY_VARIANTS,
    measurement_declaration,
    pressure_days_by_state,
    tabulate,
    with_reserve_scarcity_state,
)

ROOT = Path(__file__).resolve().parent.parent
SNAPSHOTS = ROOT / "tests/fixtures/snapshots"
RAW_ROOTS = ("funding_inputs", "on_rrp_inputs", "h8_inputs")
PUBLISHED_MANIFEST = ROOT / "metadata/funding_panel_manifest.json"
EXTRA_COLUMNS = ("on_rrp", "bank_total_assets")


def build_measurement_panel(registry_path: Path, workdir: Path):
    """The measurement panel's rows, and the published-columns digest check."""

    manifest = json.loads(PUBLISHED_MANIFEST.read_text(encoding="utf-8"))
    artifacts = [
        load_snapshot_manifest(path)
        for root in RAW_ROOTS
        for path in sorted((SNAPSHOTS / root).glob("*/*.manifest.json"))
    ]
    long_path = workdir / "measurement_point_in_time.csv"
    snapshot = build_point_in_time_snapshot(artifacts, long_path, registry_path=registry_path)
    rows = load_point_in_time_panel(long_path)
    registry = load_source_registry(registry_path)
    cutoff = datetime.fromisoformat(manifest["build_cutoff"])
    decision = time.fromisoformat(manifest["decision_time"])
    retrieved = {artifact.sha256: artifact.retrieved_at for artifact in artifacts}

    published = build_daily_panel(
        rows,
        registry,
        build_cutoff=cutoff,
        decision_time=decision,
        columns=tuple(manifest["built_columns"]),
        snapshot_retrieved_at=retrieved,
    )
    panel_path = workdir / "published_columns.csv"
    write_daily_panel(published, panel_path, source_shas=snapshot.source_shas)
    digest = verify_daily_panel(panel_path, PUBLISHED_MANIFEST)

    build = build_daily_panel(
        rows,
        registry,
        build_cutoff=cutoff,
        decision_time=decision,
        columns=tuple(manifest["built_columns"]) + EXTRA_COLUMNS,
        snapshot_retrieved_at=retrieved,
    )
    if build.refusals:
        raise ValueError(f"the measurement build refused {dict(build.refusals)}")
    if [row.date for row in build.observations] != [row.date for row in published.observations]:
        raise ValueError("the measurement panel's dates are not the published panel's")
    return build, digest, registry, decision


def _markdown(results, variants):
    lines = []
    declared = results["declared"]
    lines.append(
        f"Scored days {declared['first_scored_day']} to {declared['last_scored_day']}; "
        f"{declared['unknown_state_days']} with no state. "
        f"Intervals: stationary bootstrap, mean block {declared['bootstrap']['block_length']} "
        f"business days, {declared['bootstrap']['level']:.0%}, "
        f"{declared['bootstrap']['replications']} replications, seed {declared['bootstrap']['seed']}."
    )
    lines.append("")
    lines.append("By state (declared cut-points):")
    lines.append("")
    lines.append("| State | Days | Days SOFR > IORB | > +5 bp | Frequency [90% interval] | > +10 bp | Frequency [90% interval] |")
    lines.append("|---|---|---|---|---|---|---|")
    for state, cell in declared["by_state"].items():
        five, ten = cell["gt_5bp"], cell["gt_10bp"]
        lines.append(
            f"| {state} {cell['label']} | {cell['days']} | {cell['above_iorb_days']} | "
            f"{five['pressure_days']} | {five['frequency']:.3f} [{five['interval'][0]:.3f}, {five['interval'][1]:.3f}] | "
            f"{ten['pressure_days']} | {ten['frequency']:.3f} [{ten['interval'][0]:.3f}, {ten['interval'][1]:.3f}] |"
        )
    lines.append("")
    lines.append(
        "Rises with the state: "
        + ", ".join(f"{key}: {'yes' if value else 'NO'}" for key, value in declared["rises"].items())
    )
    lines.append("")
    lines.append("By year:")
    lines.append("")
    states = list(declared["by_state"])
    lines.append(
        "| Year | Days | "
        + " | ".join(f"Days in {state} {STATE_LABELS[int(state)]}" for state in states)
        + " | Days SOFR > IORB | > +5 bp [90% interval] | > +10 bp [90% interval] |"
    )
    lines.append("|---|---|" + "---|" * len(states) + "---|---|---|")
    for year, cell in declared["by_year"].items():
        five, ten = cell["gt_5bp"], cell["gt_10bp"]
        lines.append(
            f"| {year} | {cell['days']} | "
            + " | ".join(str(cell["days_by_state"][state]) for state in states)
            + f" | {cell['above_iorb_days']} | "
            f"{five['pressure_days']} ({five['frequency']:.3f} [{five['interval'][0]:.3f}, {five['interval'][1]:.3f}]) | "
            f"{ten['pressure_days']} ({ten['frequency']:.3f} [{ten['interval'][0]:.3f}, {ten['interval'][1]:.3f}]) |"
        )
    lines.append("")
    lines.append("Sensitivity (reported, never selected on): frequency of > +5 bp / > +10 bp days per state.")
    lines.append("")
    lines.append("| Variant | Band | Buffer | " + " | ".join(f"State {s}" for s in range(4)) + " | Rises (+5 / +10) |")
    lines.append("|---|---|---|" + "---|" * 4 + "---|")
    for name, (band, buffer_bn) in variants.items():
        cell = results[name]
        parts = []
        for state in range(4):
            entry = cell["by_state"].get(str(state))
            parts.append(
                "--"
                if entry is None
                else f"{entry['gt_5bp']['frequency']:.3f} / {entry['gt_10bp']['frequency']:.3f} (n={entry['days']})"
            )
        rises = cell["rises"]
        lines.append(
            f"| {name} | {band[0]:.0%}-{band[1]:.0%} | ${buffer_bn:g}bn | " + " | ".join(parts)
            + f" | {'yes' if rises['gt_5bp'] else 'NO'} / {'yes' if rises['gt_10bp'] else 'NO'} |"
        )
    return "\n".join(lines) + "\n"


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--registry", type=Path, default=ROOT / "metadata/sources.json")
    parser.add_argument("--minimum-history", type=int, default=61)
    parser.add_argument(
        "--end",
        type=date.fromisoformat,
        default=None,
        metavar="YYYY-MM-DD",
        help="the last scored day; before 2026-01-01, whose later days are locked",
    )
    parser.add_argument("--json", type=Path)
    parser.add_argument("--markdown", type=Path)
    args = parser.parse_args(argv)

    with measurement_declaration(), tempfile.TemporaryDirectory() as directory:
        build, digest, registry, decision = build_measurement_panel(
            args.registry, Path(directory)
        )
        results = {}
        for name, (band, buffer_bn) in SENSITIVITY_VARIANTS.items():
            rows = with_reserve_scarcity_state(build.observations, band=band, buffer_bn=buffer_bn)
            scored = pressure_days_by_state(
                rows,
                registry=registry,
                decision_time=decision,
                minimum_history=args.minimum_history,
                end=args.end,
            )
            results[name] = tabulate(scored)
    report = {
        "published_columns_digest": digest,
        "measurement_columns": list(build.built_columns),
        "holes": dict(build.holes),
        "carried_forward": dict(build.carried_forward),
        "minimum_history": args.minimum_history,
        "end": None if args.end is None else args.end.isoformat(),
        "variants": {
            name: {"band": list(band), "buffer_bn": buffer_bn}
            for name, (band, buffer_bn) in SENSITIVITY_VARIANTS.items()
        },
        "results": results,
    }
    if args.json:
        args.json.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    if args.markdown:
        args.markdown.write_text(_markdown(results, SENSITIVITY_VARIANTS), encoding="utf-8")
    print(json.dumps({key: report[key] for key in ("published_columns_digest", "end", "holes")}, indent=2))
    print(_markdown(results, SENSITIVITY_VARIANTS))
    return 0


if __name__ == "__main__":
    sys.exit(main())
