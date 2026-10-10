"""Back-filled 2014-2018 history for training (#430, track Y of #374).

A scratch measurement, not a record: it writes JSON, CSV and Markdown to the paths it is given and
nothing into `docs/runs/`. No published figure moves.

Eleonora's ruling of 8 October 2026 (#374): the New York Fed's back-filled SOFR, TGCR and BGCR
history (2014-08-22 to 2018-03-29, a workbook published after the fact) may be used as training
history. `repo_model.backfill` holds the rule and its guard; `docs/decisions/information-set.md`
records the ruling (drafted by the pull request that closes #430, for her to merge).

    PYTHONPATH=src python3 scripts/backfill_history.py check
    PYTHONPATH=src python3 scripts/backfill_history.py panel --output EXT.csv --scratch SCRATCH.csv
    PYTHONPATH=src python3 scripts/backfill_history.py run --extended EXT.csv --script scripts/X.py -- \\
        forecasts --panel EXT.csv --horizon H --output OUT/x_hH.json
    PYTHONPATH=src python3 scripts/backfill_history.py augment --extended EXT.csv --augmented AUG.csv --output EXTAUG.csv
    PYTHONPATH=src python3 scripts/backfill_history.py relabel --suffix +history --output NEW.json OLD.json [OLD.json ...]

* `check` verifies the saved workbook against its manifest and prints what it holds.
* `panel` builds the **extended scratch panel**: the scratch panel of `pressure_v1_1.py panel` (the
  published panel's columns, `on_rrp`, `bank_total_assets`, `effr`, the scarcity state), with the
  months before 2018-04-03 added, from the back-filled workbook and from the same sources fetched for
  the earlier years (bill rates, Treasury auctions, the Desk's ON RRP results, the H.8 first prints).
  FRED's reserves, TGA and IOER and the FR 2004 extract already reach back. It refuses to write
  unless the rows from 2018-04-03 reproduce the scratch panel cell for cell.
* `augment` joins the measurement columns of `measurement_fields.py panel` onto the extended panel (#484):
  published rows are the augmented panel's, back-filled rows carry a blank cell in each new column.
* `relabel` renames the forecasts of a horizon document with a suffix, so a with-history file and its
  without-history control can sit in one judge run.
* `run` executes a scoring script **unchanged** on the extended panel. It swaps one function before
  the script is loaded: `baseline.rolling_exceedance_backtest` is called with `minimum_history`
  raised by the number of back-filled rows, so the first scored origin, every refit block and every
  scored day are the ones the script scores without the history, and each fit's training frame also
  holds the back-filled rows. After each backtest the report's folds go through
  `backfill.require_training_only`.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import importlib.util
import json
import sys
import tempfile
from datetime import date, datetime, time
from pathlib import Path
from types import MappingProxyType
from unittest import mock

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))

from repo_model import backfill, ingest  # noqa: E402

SNAPSHOTS = REPO / "tests" / "fixtures" / "snapshots"
BACKFILL_ROOT = SNAPSHOTS / "backfill_2014_2018"
PUBLISHED_MANIFEST = REPO / "metadata" / "funding_panel_manifest.json"
REGISTRY = REPO / "metadata" / "sources.json"


def _script(name):
    spec = importlib.util.spec_from_file_location(name, REPO / "scripts" / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _workbook():
    """The saved workbook's manifest, after its bytes are checked against it."""

    manifests = sorted((BACKFILL_ROOT / backfill.BACKFILL_SOURCE_ID).glob("*.manifest.json"))
    if len(manifests) != 1:
        raise SystemExit(f"expected one back-fill snapshot, found {len(manifests)}")
    artifact = ingest.load_snapshot_manifest(manifests[0])
    payload = artifact.path.read_bytes()
    if hashlib.sha256(payload).hexdigest() != artifact.sha256:
        raise SystemExit("the saved workbook does not match its manifest's checksum")
    return artifact, payload


def check_command(args) -> int:
    artifact, payload = _workbook()
    days = backfill.parse_workbook(payload)
    print(
        json.dumps(
            {
                "url": artifact.url,
                "sha256": artifact.sha256,
                "retrieved_at": artifact.retrieved_at,
                "days": len(days),
                "first": days[0].day.isoformat(),
                "last": days[-1].day.isoformat(),
                "percentiles": "none published in the workbook",
            },
            indent=1,
        )
    )
    return 0


def _derived_artifacts(work: Path, artifact, days):
    """The back-fill as API-shaped snapshots under `work`, each tied to the workbook's checksum."""

    out = []
    first, last = days[0].day.isoformat(), days[-1].day.isoformat()
    for (name, kind), payload in backfill.nyfed_documents(days).items():
        url = (
            f"{ingest.NYFED_BASE}/{name}/search.json?startDate={first}&endDate={last}&type={kind}"
            f"#derived-from-{artifact.sha256[:12]}"
        )
        out.append(
            ingest._save_snapshot(
                source_id=f"nyfed_{name}",
                url=url,
                payload=payload,
                output_root=work,
                suffix="json",
                retrieved_at=datetime.fromisoformat(artifact.retrieved_at),
            )
        )
    return out


def panel_command(args) -> int:
    from repo_model import data, scarcity
    from repo_model.data import (
        build_daily_panel,
        load_daily_panel,
        load_point_in_time_panel,
    )

    v11 = _script("pressure_v1_1")
    artifact, payload = _workbook()
    days = backfill.parse_workbook(payload)
    manifest = json.loads(PUBLISHED_MANIFEST.read_text(encoding="utf-8"))
    cutoff = datetime.fromisoformat(manifest["build_cutoff"])
    decision = time.fromisoformat(manifest["decision_time"])
    columns = tuple(manifest["built_columns"]) + v11.EXTRA_COLUMNS

    scratch_panel = args.scratch
    v11.panel_command(argparse.Namespace(output=scratch_panel))
    published = load_daily_panel(scratch_panel)

    manifests = [
        path
        for root in v11.RAW_ROOTS
        for path in sorted((SNAPSHOTS / root).rglob("*.manifest.json"))
    ]
    manifests += [
        path
        for path in sorted(BACKFILL_ROOT.rglob("*.manifest.json"))
        if path.parent.name != backfill.BACKFILL_SOURCE_ID
    ]
    artifacts = [ingest.load_snapshot_manifest(path) for path in manifests]
    # `data.quarter_end` reads the market holiday table, which starts on 2018-01-01 and is pinned by
    # checksum. For the back-filled rows the business days are the workbook's own dates, the days
    # the Bank computed a rate for, as the table is for the published days.
    publication_days = {day.day for day in days}
    last_of_quarter = {}
    for day in sorted(publication_days):
        last_of_quarter[(day.year, (day.month - 1) // 3)] = day
    original_quarter_end = data.quarter_end

    def quarter_end(day):
        if day >= backfill.FIRST_PUBLISHED:
            return original_quarter_end(day)
        return float(day == last_of_quarter.get((day.year, (day.month - 1) // 3)))

    rules = MappingProxyType({**data.CALENDAR_COLUMN_RULES, "quarter_end": quarter_end})
    with tempfile.TemporaryDirectory() as scratch, scarcity.measurement_declaration(), \
            mock.patch.object(data, "CALENDAR_COLUMN_RULES", rules):
        work = Path(scratch)
        artifacts += _derived_artifacts(work / "derived", artifact, days)
        retrieved = {a.sha256: a.retrieved_at for a in artifacts}
        long_path = work / "point_in_time.csv"
        ingest.build_point_in_time_snapshot(artifacts, long_path, registry_path=REGISTRY)
        rows = load_point_in_time_panel(long_path)
        registry = ingest.load_source_registry(REGISTRY)
        build = build_daily_panel(
            rows, registry, build_cutoff=cutoff, decision_time=decision, columns=columns,
            snapshot_retrieved_at=retrieved,
        )
    if build.refusals:
        raise SystemExit(f"the build refused {dict(build.refusals)}")
    observations = scarcity.with_reserve_scarcity_state(build.observations)
    observations = [row for row in observations if row.date <= published[-1].date]

    prefix = backfill.prefix_length([row.date for row in observations])
    header = next(csv.reader(scratch_panel.open(newline="", encoding="utf-8")))
    announced = [name for name in header if name.startswith("iorb_") and name.endswith(("_bps", "_change"))]
    tail = observations[prefix:]
    if [row.date for row in tail] != [row.date for row in published]:
        raise SystemExit("the extended build's published days are not the scratch panel's days")
    for mine, theirs in zip(tail, published):
        for name in header[1:]:
            if name in announced or name.startswith("iorb_days"):
                continue
            a, b = mine.values.get(name), theirs.values.get(name)
            if (a is None) != (b is None) or (a is not None and abs(a - b) > 1e-9):
                raise SystemExit(f"{mine.date} {name}: extended {a!r} != scratch {b!r}")

    def cell(value):
        return "" if value is None else repr(float(value))

    with args.output.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerow(header)
        for row in observations[:prefix]:
            writer.writerow(
                [row.date.isoformat()]
                + ["" if name in announced or name.startswith("iorb_days") else cell(row.values.get(name))
                   for name in header[1:]]
            )
        for source in published:
            writer.writerow([source.date.isoformat()] + [cell(source.values.get(name)) for name in header[1:]])
    summary = {
        "output": str(args.output),
        "sha256": hashlib.sha256(args.output.read_bytes()).hexdigest(),
        "scratch_panel_sha256": hashlib.sha256(scratch_panel.read_bytes()).hexdigest(),
        "workbook_sha256": artifact.sha256,
        "backfilled_rows": prefix,
        "rows": len(observations),
        "first": observations[0].date.isoformat(),
        "last": observations[-1].date.isoformat(),
        "published_rows_reproduce_scratch_panel": True,
        "missing_in_backfilled_rows": {
            name: sum(1 for row in observations[:prefix] if row.values.get(name) is None)
            for name in header[1:]
            if name not in announced and not name.startswith("iorb_days")
        },
    }
    print(json.dumps(summary, indent=1))
    return 0


def run_command(args) -> int:
    """Run a scoring script unchanged, its backtests trained on the back-filled rows as well.

    `--control` accepts a panel with no back-filled row (the arm without history), read by the same
    recorders. `--folds-output` records the refit blocks (training window and scored days) and
    `--pairs-output` the training pairs that came from back-filled label days, per fit (#484).
    """

    from repo_model import baseline, ml
    from repo_model.data import load_daily_panel

    rows = load_daily_panel(args.extended)
    prefix = backfill.prefix_length([row.date for row in rows])
    if not prefix and not args.control:
        raise SystemExit(f"{args.extended} carries no back-filled row")
    script = args.script.resolve()
    if script.parent != REPO / "scripts":
        raise SystemExit("the script must be one of scripts/*.py")
    original = baseline.rolling_exceedance_backtest
    original_pairs = ml._pressure_pairs

    calls = []
    blocks = {}
    fits = {}

    def with_history(observations, *, minimum_history=20, **kwargs):
        dates = [row.date for row in observations]
        shift = backfill.prefix_length(dates)
        report = original(observations, minimum_history=minimum_history + shift, **kwargs)
        backfill.require_training_only(report.folds, where=script.name)
        calls.append((shift, len(report.folds)))
        for fold in report.folds:
            key = (fold.train_start.isoformat(), fold.train_end.isoformat(), fold.train_rows)
            span = blocks.setdefault(key, [fold.scored_date.isoformat(), fold.scored_date.isoformat()])
            span[1] = fold.scored_date.isoformat()
        return report

    def recording_pairs(design, information, train_rows, cache, positions=None):
        mine = [] if positions is None else positions
        xs, ys = original_pairs(design, information, train_rows, cache, mine)
        back = [k for k, position in enumerate(mine) if train_rows[position].date < backfill.FIRST_PUBLISHED]
        risk = [k for k in back if xs[k] and xs[k][-1] == 1.0]
        fits[train_rows[-1].date.isoformat()] = {
            "train_rows": len(train_rows),
            "pairs": len(xs),
            "backfilled_pairs": len(back),
            "backfilled_risk_date_pairs": len(risk),
        }
        return xs, ys

    baseline.rolling_exceedance_backtest = with_history
    ml._pressure_pairs = recording_pairs
    try:
        module = _script(script.stem)
        status = int(module.main(list(args.rest)) or 0)
        if not calls:
            raise SystemExit(f"{script.name} ran no backtest through the training-history function")
        print(json.dumps({"backtests_with_history": len(calls), "backfilled_rows": calls[0][0]}))
        if args.folds_output:
            document = [
                {"train_start": a, "train_end": b, "train_rows": n, "first_scored": span[0], "last_scored": span[1]}
                for (a, b, n), span in sorted(blocks.items(), key=lambda item: item[1][0])
            ]
            args.folds_output.write_text(json.dumps(document, indent=1) + "\n", encoding="utf-8")
        if args.pairs_output:
            args.pairs_output.write_text(
                json.dumps({"backfilled_rows": prefix, "fits": fits}, indent=1, sort_keys=True) + "\n", encoding="utf-8"
            )
        return status
    finally:
        baseline.rolling_exceedance_backtest = original
        ml._pressure_pairs = original_pairs


def augment_command(args) -> int:
    """The extended panel with the measurement columns joined on (`backfill.augment_rows`)."""

    def read(path):
        with path.open(newline="", encoding="utf-8") as handle:
            reader = csv.DictReader(handle)
            return reader.fieldnames, list(reader)

    extended_header, extended = read(args.extended)
    augmented_header, augmented = read(args.augmented)
    out = backfill.augment_rows(extended, augmented)
    header = list(dict.fromkeys(list(extended_header) + list(augmented_header)))
    with args.output.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=header, lineterminator="\n")
        writer.writeheader()
        writer.writerows(out)
    print(
        json.dumps(
            {
                "output": str(args.output),
                "sha256": hashlib.sha256(args.output.read_bytes()).hexdigest(),
                "rows": len(out),
                "backfilled_rows": backfill.prefix_length([date.fromisoformat(row["date"]) for row in out]),
                "columns_added_blank_in_backfilled_rows": [n for n in augmented_header if n not in extended_header],
            },
            indent=1,
        )
    )
    return 0


def relabel_command(args) -> int:
    """One horizon document from several, every forecast and declaration renamed with `--suffix`."""

    documents = [json.loads(path.read_text(encoding="utf-8")) for path in args.inputs]
    merged = dict(documents[0])
    for key in ("forecasts", "declarations"):
        merged[key] = {}
        for document in documents:
            for name, value in document[key].items():
                merged[key][f"{name}{args.suffix}"] = value
    for document in documents[1:]:
        for key in ("horizon", "panel_sha256", "scratch_panel_sha256"):
            if key in document and document[key] != documents[0][key] and key != "scratch_panel_sha256":
                raise SystemExit(f"the documents disagree on {key}")
    args.output.write_text(json.dumps(merged, indent=1, sort_keys=True, default=str) + "\n", encoding="utf-8")
    return 0


def judge_command(args) -> int:
    """The pressure-day judge on forecast files, and each model's onset recall split by year.

    As `pressure_judge.py judge`, with three differences: a forecast file written on an extended
    panel is accepted (its dates are the judge grid's, which `choose_cutoffs` checks day by day, and
    the judge reads the published panel); the result carries, per model, the onsets and the onsets
    flagged at some horizon h >= 1 for each calendar year of the onset (`onset_recall_by_year`); and,
    per model and year, the false alarms at each horizon, flat and under the weighted miss rule
    (`false_alarms_by_year`, #484). `--rule` is `pressure_judge.py judge`'s.
    """

    from dataclasses import replace

    from repo_model import pressure_judge as pj
    from repo_model.baseline import panel_sha256
    from repo_model.data import audit_panel, load_daily_panel
    from repo_model.evaluation_splits import load_split_declaration

    judge_script = _script("pressure_judge")
    declaration = pj.load_declaration()
    commit = judge_script.require_committed_declaration(pj.DEFAULT_DECLARATION)
    judge_script.require_committed_file(pj.DEFAULT_WEIGHTED_MISS)
    applied = {"declared": None, "weighted": True, "unweighted": False}[args.rule]
    declaration = replace(declaration, weighted_miss=pj.load_weighted_miss(applied=applied))
    rows = load_daily_panel(args.panel)
    audit_panel(rows)
    splits = load_split_declaration(judge_script.SPLITS)
    digest = panel_sha256(args.panel)
    forecasts = []
    for path in args.inputs:
        document = json.loads(Path(path).read_text())
        document["panel_sha256"] = digest
        forecasts.extend(pj.forecasts_from_horizon_document(document))
    states = {h: judge_script._scarcity_states(h, declaration.last_day) for h in declaration.horizons}

    def grids_of(items):
        out = {}
        for horizon in declaration.horizons:
            reference = next(f for f in items if f.horizon == horizon and f.name == declaration.climatology)
            out[horizon] = pj.build_grid(
                declaration, horizon, rows, reference.dates, splits, scarcity_state=states[horizon]
            )
        return out

    calendar = [row.date for row in rows]
    forecasts = pj.choose_cutoffs(declaration, grids_of(forecasts), forecasts, calendar)
    grids = grids_of(forecasts)
    result = pj.judge(
        declaration, grids, forecasts, calendar=calendar, holdouts=judge_script._holdouts(), confirmation=False,
    )
    tau = declaration.primary
    by_name = {}
    for forecast in forecasts:
        by_name.setdefault(forecast.name, {})[forecast.horizon] = forecast
    horizons = list(declaration.horizons)
    common = sorted(set.intersection(*(set(grids[h].dates) for h in horizons)))
    position = {h: {day: k for k, day in enumerate(grids[h].dates)} for h in horizons}
    first = horizons[0]
    onset = [int(grids[first].onset[position[first][day]]) for day in common]
    onset_days = [day for day, flag in zip(common, onset) if flag]
    place = {day: k for k, day in enumerate(calendar)}
    rule = declaration.weighted_miss
    places = [place[day] for day in common]
    by_year, alarms_by_year = {}, {}
    for name, per_horizon in by_name.items():
        years = {}
        for day in onset_days:
            caught = any(
                per_horizon[h].probabilities[tau][position[h][day]] >= per_horizon[h].cutoffs[tau][position[h][day]]
                for h in horizons
            )
            entry = years.setdefault(str(day.year), {"onsets": 0, "flagged": 0})
            entry["onsets"] += 1
            entry["flagged"] += int(caught)
        by_year[name] = years
        alarms = {}
        for h in horizons:
            at = [position[h][day] for day in common]
            pressure = [grids[h].outcomes[tau][k] for k in at]
            chosen = per_horizon[h]
            flags = pj._alarm_flags(
                declaration, name, [1 if chosen.probabilities[tau][k] >= chosen.cutoffs[tau][k] else 0 for k in at], onset
            )
            weights = (
                pj.false_alarm_weights(rule, positions=places, pressure=pressure, known_through=places[-1])
                if rule is not None
                else None
            )
            for day, flag, y, index in zip(common, flags, pressure, range(len(common))):
                if flag and not y:
                    cell = alarms.setdefault(str(day.year), {}).setdefault(str(h), {"flat": 0, "weighted": 0.0})
                    cell["flat"] += 1
                    if weights is not None:
                        cell["weighted"] += weights[index]
        alarms_by_year[name] = alarms
    paired = {}
    suffix = "+history"
    for name in sorted(by_name):
        control = name[: -len(suffix)] if name.endswith(suffix) else None
        if control not in by_name:
            continue
        caught = {}
        for label in (name, control):
            vector = [0.0] * len(common)
            for k, day in enumerate(common):
                if onset[k]:
                    vector[k] = float(
                        any(
                            by_name[label][h].probabilities[tau][position[h][day]]
                            >= by_name[label][h].cutoffs[tau][position[h][day]]
                            for h in horizons
                        )
                    )
            caught[label] = vector
        flat_onset = [float(o) for o in onset]
        cells = {
            "onsets": [flat_onset, caught[name], caught[control]],
        }
        recall = pj._bootstrap(
            declaration, cells, pj._ONSET_STATS, len(common), seed=pj._seed(declaration.seed, name, "history")
        )["onsets"]
        entry = {
            "recall_with": recall["recall"],
            "recall_without": recall["climatology_recall"],
            "recall_difference": recall["recall_difference"],
            "brier_difference_by_horizon": {},
        }
        for h in horizons:
            at = [position[h][day] for day in common]
            outcomes = [grids[h].outcomes[tau][k] for k in at]
            vectors = pj._paired_vectors(
                [by_name[name][h].probabilities[tau][k] for k in at],
                [by_name[control][h].probabilities[tau][k] for k in at],
                [by_name[control][h].probabilities[tau][k] for k in at],
                outcomes,
            )
            cell = pj._bootstrap(
                declaration,
                {"all": vectors},
                {"d": pj._PAIRED_STATS["brier_difference_vs_climatology"]},
                len(common),
                seed=pj._seed(declaration.seed, name, "history", h),
            )["all"]["d"]
            entry["brier_difference_by_horizon"][str(h)] = cell
        paired[control] = entry
    result["paired_history"] = paired
    result["onset_recall_by_year"] = by_year
    result["false_alarms_by_year"] = alarms_by_year
    result["provenance"] = {
        "panel_sha256": digest,
        "declaration_commit": commit,
        "forecast_files": [str(p) for p in args.inputs],
    }
    args.output.write_text(json.dumps(result, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    if args.markdown:
        args.markdown.write_text(judge_script.markdown(result), encoding="utf-8")
    print(json.dumps({"output": str(args.output), "models": sorted(by_year)}))
    return 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("check").set_defaults(func=check_command)
    panel = commands.add_parser("panel")
    panel.add_argument("--output", type=Path, required=True)
    panel.add_argument("--scratch", type=Path, required=True, help="where the unextended scratch panel is written")
    panel.set_defaults(func=panel_command)
    run = commands.add_parser("run")
    run.add_argument("--extended", type=Path, required=True)
    run.add_argument("--script", type=Path, required=True)
    run.add_argument("--control", action="store_true", help="accept a panel with no back-filled row (the arm without history)")
    run.add_argument("--folds-output", type=Path)
    run.add_argument("--pairs-output", type=Path)
    run.add_argument("rest", nargs=argparse.REMAINDER)
    run.set_defaults(func=run_command)
    augment = commands.add_parser("augment")
    augment.add_argument("--extended", type=Path, required=True)
    augment.add_argument("--augmented", type=Path, required=True)
    augment.add_argument("--output", type=Path, required=True)
    augment.set_defaults(func=augment_command)
    relabel = commands.add_parser("relabel")
    relabel.add_argument("--suffix", required=True)
    relabel.add_argument("--output", type=Path, required=True)
    relabel.add_argument("inputs", nargs="+", type=Path)
    relabel.set_defaults(func=relabel_command)
    judge = commands.add_parser("judge")
    judge.add_argument("--panel", type=Path, required=True, help="the published panel")
    judge.add_argument("--output", type=Path, required=True)
    judge.add_argument("--markdown", type=Path)
    judge.add_argument("--rule", choices=("declared", "weighted", "unweighted"), default="declared")
    judge.add_argument("inputs", nargs="+", type=Path)
    judge.set_defaults(func=judge_command)
    args = parser.parse_args(argv)
    if args.command == "run" and args.rest[:1] == ["--"]:
        args.rest = args.rest[1:]
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
