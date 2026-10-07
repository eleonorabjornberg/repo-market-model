"""The blind gap (#235): reconstruct its forecasts at the pinned code, at scoring time.

Eleonora's ruling of 5 October 2026 on #235 ("Option 2", and "keep reported
only"). The blind-tier target days after the panel end (2026-09-03) and before
the first target day the live record carries at each horizon were scored by no
record and seen by no model choice, and the live record never backfills. They
are scored once, on the first scoring date (2027-04-01), alongside the live
record's first scoring, reported only (`scripts/live_score.py`, `score_gap`).

This script makes their forecasts. It fetches the inputs once, at scoring time
(the latest vintage), and builds one panel from them. For each decision day
whose forecast reaches a gap day (`live_score.gap_decision_days`), it keeps the
rows dated before that day and runs the declared models, baselines and
distributions exactly as the day's live run does after its build
(`forecast_day`). What each forecast may read is the as-of rule's
(`docs/decisions/information-set.md`): every read is priced at the day's 16:00
ET decision instant, field by field, and a read off a placeholder row is
refused (`require_reads_on_real_rows`), as in the live run and the final test.
The panel is not cut at each decision instant: a latest-vintage source (FRED's
IORB, reserves and TGA) is available only from its snapshot's retrieval, so a
build cut before the fetch has no IORB at all. Every step that touches a model
runs in a subprocess on a worktree at `live_record.py pin`, as the live-log
workflow does. Each forecast is written once, with its inputs' digests, to
`OUT/gap/YYYY-MM-DD.json`, never into the live log (`require_outside_live_log`).

    git -C MAIN worktree add --detach ../pinned \\
        "$(cd MAIN && PYTHONPATH=src python3 -B scripts/live_record.py pin --ref origin/main)"
    PYTHONPATH=src python3 scripts/live_gap.py reconstruct --date 2027-04-01 \\
        --live-dir LIVE-LOG --pinned-root ../pinned --out-dir GAP --work-dir WORK [--raw-root RAW]
    PYTHONPATH=src python3 scripts/live_score.py --date 2027-04-01 --live-dir LIVE-LOG \\
        --gap-dir GAP --pinned-tree ../pinned --panel PANEL --archive-dir LIVE-RAW --output OUT.json

`reconstruct` refuses on any date but the first scoring date
(`live_score.require_gap_scoring`); the gap's days are scored later through the
lockbox guard (`metadata/lockbox.json`, #277). It is resumable: a day already written is
skipped.

The module imports nothing from `repo_model` at its top, so that the `fetch`
and `forecast` subcommands load only the pinned tree's code.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import os
import subprocess
import sys
import time as clock
from datetime import date, datetime, time, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

REPO = Path(__file__).resolve().parents[1]
EASTERN = ZoneInfo("America/New_York")


def _load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def decision_instant(day: date, decision: time = time(16)) -> datetime:
    """`day`'s decision instant, in UTC: what each reconstructed forecast is made as of."""

    return datetime.combine(day, decision, tzinfo=EASTERN).astimezone(timezone.utc)


def require_outside_live_log(out_dir: Path, live_dir: Path) -> None:
    """Refuse an output directory in the live log: a gap forecast is never a live record.

    Raises:
        ValueError: if `out_dir` is `live_dir` or inside it, or inside a
            checkout of the `live-log` branch.
    """

    out = Path(out_dir).resolve()
    log = Path(live_dir).resolve()
    if out == log or log in out.parents:
        raise ValueError(f"{out_dir} is in the live log {live_dir}: gap forecasts are never written there")
    existing = out
    while not existing.exists():
        existing = existing.parent
    branch = subprocess.run(
        ["git", "-C", str(existing), "rev-parse", "--abbrev-ref", "HEAD"],
        capture_output=True, text=True, check=False,
    )
    if branch.returncode == 0 and branch.stdout.strip() == "live-log":
        raise ValueError(f"{out_dir} is in a checkout of live-log: gap forecasts are never written there")


def write_gap_record(root: Path, record, validate) -> Path:
    """Write one gap forecast once, under `root/gap/`. Returns its path.

    Raises:
        ValueError: if `validate` refuses the record, or its file exists.
    """

    validate(record)
    path = Path(root) / "gap" / f"{record['decision_day']}.json"
    if path.exists():
        raise ValueError(f"{path} exists: a gap forecast is written once")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("xb") as handle:
        handle.write((json.dumps(record, indent=1, sort_keys=True) + "\n").encode("utf-8"))
    return path


# -- run under the pinned tree -------------------------------------------------


def _pinned(root: Path):
    """The pinned tree's `live_record.py`, which puts that tree's `src` first on the path."""

    live = _load(Path(root) / "scripts" / "live_record.py", "pinned_live_record")
    import repo_model

    if Path(repo_model.__file__).resolve().parents[1] != (Path(root) / "src").resolve():
        raise ValueError(f"repo_model was loaded from {repo_model.__file__}, not the pinned tree")
    return live


def forecast_day(live, raw_root: Path, panel: Path, day: date) -> dict:
    """`day`'s record, as its live run makes it after the build, from the panel built at scoring time.

    The steps after the build in `live_record.run_command`, in its order, with
    the pinned module `live`: the rows dated before `day`, extended through
    each horizon's target day, and every model, baseline and distribution run
    through the target. Returns the record without `code` and
    `reconstruction`, which the caller adds.
    """

    started = datetime.now(timezone.utc)
    durations = {}
    tick = clock.monotonic()
    manifest = json.loads(Path(f"{panel}.manifest.json").read_text(encoding="utf-8"))
    rows = live.load_daily_panel(panel)
    live.audit_panel(rows)
    real = [row for row in rows if row.date < day]
    pit = panel.with_name(panel.stem + "_point_in_time.csv")
    registry = json.loads(live.REGISTRY.read_text(encoding="utf-8"))
    splits = live.load_split_declaration(live.SPLITS)
    taus = tuple(float(tau) for tau in live.load_stress_thresholds(live.THRESHOLDS)["taus_bp"])
    auctions = live.auction_records(raw_root)
    extended = {h: live.extend_panel(real, day, h, pit, auctions) for h in live.HORIZONS}
    durations["build"] = clock.monotonic() - tick

    targets = []
    for h in live.HORIZONS:
        rows_h, target_days = extended[h]
        last_real = len(real) - 1
        for features in (live.V1_FEATURES[h], live.CALENDAR_FEATURES, ("spread_bps",),
                         live.published_features(h)):
            rule = live.InformationRule(registry, features, decision_time=live.DECISION, horizon=h)
            live.require_reads_on_real_rows(rows_h, rule, len(rows_h) - 1, last_real)
        anchor = live.InformationRule(
            registry, ("spread_bps",), decision_time=live.DECISION, horizon=h
        ).anchor([row.date for row in rows_h], len(rows_h) - 1)
        targets.append(
            {
                "horizon": h,
                "target_date": target_days[-1].isoformat(),
                "anchor_date": rows_h[anchor].date.isoformat(),
                "anchor_spread_bp": live.onset.whole_bp(rows_h[anchor].spread_bps),
                "leap_threshold_bp": live.onset.LEAP_JUMP_BP[h],
            }
        )

    tick = clock.monotonic()
    models = {}
    for model in live.MODELS:
        forecasts, digests = {}, {}
        for h in live.HORIZONS:
            cells, raw = live.v1_forecast(extended[h][0], h, registry, splits, taus)
            live._require_declaration(model, h, raw, taus)
            forecasts[str(h)] = cells
            digests[str(h)] = live._declaration_sha256(model, h)
            targets[h - 1]["train_end"] = raw.folds[-1].train_end.isoformat()
        models[model["name"]] = {
            "published": model["published"], "declaration_sha256": digests, "forecasts": forecasts,
        }
    durations["fit_forecast_models"] = clock.monotonic() - tick

    tick = clock.monotonic()
    baselines = {name: {"forecasts": {}} for name in live.BASELINE_NAMES}
    for h in live.HORIZONS:
        got = live.baseline_forecasts(extended[h][0], h, registry, splits, taus)
        if got.pop("train_end").isoformat() != targets[h - 1]["train_end"]:
            raise ValueError(f"the baselines at h={h} were fitted on another refit block")
        for name in live.BASELINE_NAMES:
            baselines[name]["forecasts"][str(h)] = got[name]
    durations["fit_forecast_baselines"] = clock.monotonic() - tick

    tick = clock.monotonic()
    distributions = {
        "levels": list(live.QUANTILE_LEVELS),
        "published": {
            "records": {str(h): live.published_distribution_record(h) for h in live.HORIZONS},
            "declaration_sha256": {str(h): live.published_declaration_sha256(h) for h in live.HORIZONS},
            "quantiles_bps": {},
        },
        "persistence": {"quantiles_bps": {}},
    }
    for h in live.HORIZONS:
        got = live.distribution_forecasts(extended[h][0], h, registry)
        if got["levels"] != list(live.QUANTILE_LEVELS):
            raise ValueError(f"the distributions at h={h} are on another quantile grid")
        for side in live.DISTRIBUTION_SIDES:
            distributions[side]["quantiles_bps"][str(h)] = got[side]
    durations["fit_forecast_distributions"] = clock.monotonic() - tick

    return {
        "record_version": live.RECORD_VERSION,
        "decision_day": day.isoformat(),
        "decision_instant": datetime.combine(day, live.DECISION, tzinfo=EASTERN).isoformat(),
        "packages": live._packages(),
        "inputs": {
            "snapshots": live.snapshots(raw_root),
            "build_cutoff": manifest["build_cutoff"],
            "decision_instant_utc": decision_instant(day, live.DECISION).isoformat(),
            "panel_sha256": live._sha256(panel),
            "panel_last_date": real[-1].date.isoformat(),
            "registry_sha256": live._sha256(live.REGISTRY),
            "splits_sha256": live._sha256(live.SPLITS),
            "thresholds_sha256": live._sha256(live.THRESHOLDS),
        },
        "targets": targets,
        "models": models,
        "baselines": baselines,
        "distributions": distributions,
        "run": {
            "started_at": started.isoformat(),
            "finished_at": datetime.now(timezone.utc).isoformat(),
            "durations_seconds": {step: round(value, 3) for step, value in durations.items()},
        },
    }


def fetch_command(args) -> int:
    live = _pinned(args.pinned_root)
    live.fetch(Path(args.raw_root), date.fromisoformat(args.date))
    return 0


def build_command(args) -> int:
    live = _pinned(args.pinned_root)
    live.build(Path(args.raw_root), Path(args.panel), datetime.fromisoformat(args.cutoff))
    return 0


def forecast_command(args) -> int:
    live = _pinned(args.pinned_root)
    record = forecast_day(live, Path(args.raw_root), Path(args.panel), date.fromisoformat(args.day))
    Path(args.output).write_text(json.dumps(record, sort_keys=True) + "\n", encoding="utf-8")
    return 0


# -- the orchestration, at the current code ----------------------------------------


def _git(root: Path, *argv) -> str:
    return subprocess.run(
        ["git", "-C", str(root), *argv], check=True, capture_output=True, text=True
    ).stdout.strip()


def _under_pin(pinned_root: Path, *argv) -> None:
    """Run this script's `argv` with the pinned tree's code, from the pinned tree."""

    env = dict(os.environ, PYTHONPATH=str(Path(pinned_root).resolve() / "src"))
    subprocess.run([sys.executable, "-B", str(Path(__file__).resolve()), *argv],
                   cwd=pinned_root, env=env, check=True)


def fetched_at(raw_root: Path, scoring_date: date) -> str:
    """The latest retrieval among the snapshots, refused if before the scoring date."""

    stamps = [
        datetime.fromisoformat(json.loads(path.read_text(encoding="utf-8"))["retrieved_at"])
        for path in sorted(Path(raw_root).glob("*/*.manifest.json"))
    ]
    if not stamps:
        raise ValueError(f"{raw_root} holds no snapshot")
    first = min(stamps)
    if first.astimezone(EASTERN).date() < scoring_date:
        raise ValueError(
            f"a snapshot in {raw_root} was retrieved at {first.isoformat()}, before the "
            f"scoring date {scoring_date}: the gap's inputs are fetched at scoring time"
        )
    return max(stamps).isoformat()


def reconstruct_command(args) -> int:
    score = _load(REPO / "scripts" / "live_score.py", "gap_live_score")
    day = date.fromisoformat(args.date)
    score.require_gap_scoring(day)
    out_dir, live_dir, pinned_root = Path(args.out_dir), Path(args.live_dir), Path(args.pinned_root)
    require_outside_live_log(out_dir, live_dir)
    live = score._live()
    pin = live.resolve_pin(args.ref)
    if _git(pinned_root, "rev-parse", "HEAD") != pin:
        raise ValueError(f"{pinned_root} is not at the pinned code {pin}")
    if _git(pinned_root, "status", "--porcelain", "--untracked-files=no"):
        raise ValueError(f"{pinned_root} has local changes; the gap is reconstructed from the pinned tree")
    first = json.loads(live.record_path(live_dir, score.FIRST_LIVE_DAY).read_text(encoding="utf-8"))
    live.validate_record(first)
    days = score.gap_decision_days(score.first_live_targets(first))

    work = Path(args.work_dir)
    work.mkdir(parents=True, exist_ok=True)
    raw_root = Path(args.raw_root) if args.raw_root else work / "raw"
    if not args.raw_root:
        _under_pin(pinned_root, "fetch", "--pinned-root", str(pinned_root.resolve()),
                   "--raw-root", str(raw_root.resolve()), "--date", day.isoformat())
    stamp = fetched_at(raw_root, day)
    panel = (work / "panel.csv").resolve()
    if not panel.exists():
        cutoff = datetime.now(timezone.utc).replace(microsecond=0)
        _under_pin(pinned_root, "build", "--pinned-root", str(pinned_root.resolve()),
                   "--raw-root", str(raw_root.resolve()), "--panel", str(panel),
                   "--cutoff", cutoff.isoformat())
    written = []
    for decision_day, horizons in days.items():
        if (out_dir / "gap" / f"{decision_day.isoformat()}.json").exists():
            continue
        output = (work / f"{decision_day.isoformat()}.json").resolve()
        _under_pin(pinned_root, "forecast", "--pinned-root", str(pinned_root.resolve()),
                   "--raw-root", str(raw_root.resolve()), "--panel", str(panel),
                   "--day", decision_day.isoformat(), "--output", str(output))
        record = json.loads(output.read_text(encoding="utf-8"))
        record["code"] = {"sha": pin, "pinned_sha": pin}
        record["reconstruction"] = {
            "label": score.GAP_LABEL,
            "scoring_date": day.isoformat(),
            "fetched_at": stamp,
            "gap_horizons": list(horizons),
        }
        written.append(str(write_gap_record(out_dir, record, score.validate_gap_record)))
    print(json.dumps({"gap_decision_days": [d.isoformat() for d in days], "written": written}))
    return 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="command", required=True)
    run = sub.add_parser("reconstruct", help="every gap forecast, at the pinned code")
    run.add_argument("--date", required=True, help="the scoring date")
    run.add_argument("--live-dir", required=True, help="a checkout of live-log")
    run.add_argument("--pinned-root", required=True, help="a worktree at live_record.py pin")
    run.add_argument("--out-dir", required=True)
    run.add_argument("--work-dir", required=True)
    run.add_argument("--raw-root", default=None, help="snapshots fetched at scoring time; skips the fetch")
    run.add_argument("--ref", default="origin/main")
    run.set_defaults(func=reconstruct_command)
    fetch = sub.add_parser("fetch", help="internal: the fetch, under the pinned tree")
    fetch.add_argument("--pinned-root", required=True)
    fetch.add_argument("--raw-root", required=True)
    fetch.add_argument("--date", required=True)
    fetch.set_defaults(func=fetch_command)
    build = sub.add_parser("build", help="internal: the panel, under the pinned tree")
    build.add_argument("--pinned-root", required=True)
    build.add_argument("--raw-root", required=True)
    build.add_argument("--panel", required=True)
    build.add_argument("--cutoff", required=True)
    build.set_defaults(func=build_command)
    forecast = sub.add_parser("forecast", help="internal: one day's forecast, under the pinned tree")
    forecast.add_argument("--pinned-root", required=True)
    forecast.add_argument("--raw-root", required=True)
    forecast.add_argument("--panel", required=True)
    forecast.add_argument("--day", required=True)
    forecast.add_argument("--output", required=True)
    forecast.set_defaults(func=forecast_command)
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
