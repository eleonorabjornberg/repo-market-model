"""H.4.1 Wednesday levels beside the week averages, and what they do to the scarcity state (#970, H5 step 3).

A scratch measurement, not a record: it writes JSON and Markdown to the paths it is given and nothing into `docs/runs/`.
Every choice is in `metadata/h41_wednesday_levels_970.json`, which this script refuses to read unless it is committed and
unchanged. The panel's `reserve_balances` is FRED's WRESBAL, the week average, not the Wednesday level (finding #485, item 5).
The measurement builds the measurement panel of `scripts/scarcity_validation.py` twice from the tracked snapshots: as it is, and
with the values of WRESBAL (and WTREGEN) replaced by the Wednesday levels WRBWFRBL (and WDTGAL) of the same weeks. Dates, vintage
ids and the registry's declared instant are the averages' own, so a level is read at the print of its own release and not before.
No day after 2025-12-31 is read (`docs/decisions/lockbox.md`). Development days give a diagnosis, never a verdict.

    PYTHONPATH=src python3 scripts/h41_wednesday_levels_970.py score --output OUT/h41_wednesday_levels_970.json
    PYTHONPATH=src python3 scripts/h41_wednesday_levels_970.py report --score OUT/h41_wednesday_levels_970.json --output OUT/report.md
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import statistics
import subprocess
import sys
import tempfile
from collections import Counter
from datetime import date, datetime, time
from pathlib import Path
from typing import Dict, List, Mapping, Optional, Sequence, Tuple

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))

from repo_model import pressure  # noqa: E402
from repo_model.data import PointInTimeObservation, build_daily_panel, load_point_in_time_panel, verify_daily_panel, write_daily_panel  # noqa: E402
from repo_model.ingest import build_point_in_time_snapshot, load_snapshot_manifest, load_source_registry  # noqa: E402
from repo_model.lockbox import require_unlocked  # noqa: E402
from repo_model.scarcity import measurement_declaration, own_leg_states  # noqa: E402

DECLARATION = REPO / "metadata" / "h41_wednesday_levels_970.json"
SNAPSHOT = REPO / "tests" / "fixtures" / "snapshots" / "h41_wednesday_levels"
REGISTRY = REPO / "metadata" / "sources.json"
LAST_DAY = date(2025, 12, 31)
FIRST_SCORED = date(2018, 6, 29)
MINIMUM_HISTORY = 61
HORIZONS = (1, 2, 3, 4, 5)
#: The panel's value unit is billions; the series are served in millions.
SCALE = 1.0 / 1000.0
#: The measurement's two replacements: the average's series, the level's file.
PAIRS = {"WRESBAL": "WRBWFRBL", "WTREGEN": "WDTGAL"}
ONSET_BP = 5.0


def _load(name: str):
    spec = importlib.util.spec_from_file_location(f"{name}_script", REPO / "scripts" / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[f"{name}_script"] = module
    spec.loader.exec_module(module)
    return module


def refuse_locked(days: Sequence[date]) -> None:
    """Refuse a run that would read a day of a locked tier (`docs/decisions/lockbox.md`): raises `LookAheadError`."""

    require_unlocked(list(days), where="h41_wednesday_levels_970")


def committed_declaration(path: Path = DECLARATION) -> dict:
    """The declaration, refused unless it is committed and unchanged since `HEAD`."""

    relative = str(path.resolve().relative_to(REPO))
    dirty = subprocess.run(
        ["git", "status", "--porcelain", "--", relative], cwd=REPO, capture_output=True, text=True, check=True
    ).stdout.strip()
    if dirty:
        raise SystemExit(f"{relative} is not committed ({dirty}); a declaration is made before any score")
    return json.loads(path.read_text(encoding="utf-8"))


def committed_files() -> Dict[str, str]:
    """The snapshot's files and their declared checksums."""

    return dict(json.loads(DECLARATION.read_text(encoding="utf-8"))["snapshot"]["files"])


def read_levels(path: Path, expected_sha256: str) -> Dict[date, float]:
    """A snapshot as served: `{Wednesday: millions of USD}`, a missing value (`.`) left out. `ValueError` on a changed file."""

    payload = path.read_bytes()
    digest = hashlib.sha256(payload).hexdigest()
    if digest != expected_sha256:
        raise ValueError(f"{path.name} has sha256 {digest[:12]}, not the declared {expected_sha256[:12]}")
    lines = payload.decode("utf-8").splitlines()
    out: Dict[date, float] = {}
    for line in lines[1:]:
        when, _, value = line.partition(",")
        if value.strip() in ("", "."):
            continue
        out[date.fromisoformat(when.strip())] = float(value)
    return out


def substitute(
    rows: Sequence[PointInTimeObservation], series: str, levels: Mapping[date, float], *, last: date = LAST_DAY
) -> Tuple[List[PointInTimeObservation], Dict[str, int]]:
    """The long rows with `series` valued at the Wednesday level of the same week and everything else the row's own.

    A level of a week after `last` is not read: the row keeps its average and no scored decision reads it. A row whose
    Wednesday has no level is dropped, never filled with the average.
    """

    out: List[PointInTimeObservation] = []
    counts = {"replaced": 0, "dropped": 0, "kept_after_end": 0}
    for row in rows:
        if row.series_id != series:
            out.append(row)
        elif row.ref_date > last:
            out.append(row)
            counts["kept_after_end"] += 1
        elif row.ref_date in levels:
            out.append(
                PointInTimeObservation(
                    row.series_id, row.ref_date, row.available_at, levels[row.ref_date] * SCALE, row.vintage_id, row.source_sha
                )
            )
            counts["replaced"] += 1
        else:
            counts["dropped"] += 1
    return out, counts


def movement(old: Mapping[date, Optional[float]], new: Mapping[date, Optional[float]]) -> Dict[str, object]:
    """How the state moves between two reads of the same days."""

    if old.keys() != new.keys():
        raise ValueError("the two reads score different days")
    changed = sorted(d for d in old if old[d] != new[d])
    entered = [d for d in changed if (new[d] or 0) >= 2 > (old[d] or 0)]
    left = [d for d in changed if (old[d] or 0) >= 2 > (new[d] or 0)]
    return {
        "days": len(old),
        "changed": len(changed),
        "up": sum((new[d] or 0) > (old[d] or 0) for d in changed),
        "down": sum((new[d] or 0) < (old[d] or 0) for d in changed),
        "by_year": dict(sorted(Counter(str(d.year) for d in changed).items())),
        "enter_risky_set": len(entered),
        "leave_risky_set": len(left),
        "state_counts_before": dict(sorted(Counter(str(v) for v in old.values()).items())),
        "state_counts_after": dict(sorted(Counter(str(v) for v in new.values()).items())),
        "changed_days": [[d.isoformat(), old[d], new[d]] for d in changed],
    }


def _difference_summary(levels: Mapping[date, float], average: Mapping[date, float]) -> Dict[str, object]:
    """Level less average in billions on the Wednesdays both exist, to the study end."""

    days = sorted(d for d in levels if d in average and d <= LAST_DAY)
    diffs = [levels[d] * SCALE - average[d] for d in days]
    ordered = sorted(diffs)

    def pick(p: float) -> float:
        return ordered[int(p * (len(ordered) - 1))]

    return {
        "n": len(diffs), "mean": statistics.fmean(diffs), "mean_abs": statistics.fmean(abs(x) for x in diffs),
        "p05": pick(0.05), "p50": pick(0.50), "p95": pick(0.95),
        "by_year": {
            str(year): {"n": len(ys), "mean": statistics.fmean(ys), "mean_abs": statistics.fmean(abs(x) for x in ys)}
            for year in sorted({d.year for d in days})
            for ys in [[x for d, x in zip(days, diffs) if d.year == year]]
        },
    }


def _panel_rows(rows: Sequence[PointInTimeObservation], registry, cutoff: datetime, decision: time, columns, retrieved):
    """The measurement panel's observations from long rows, as `scarcity_validation.build_measurement_panel` builds them."""

    build = build_daily_panel(
        rows, registry, build_cutoff=cutoff, decision_time=decision, columns=columns, snapshot_retrieved_at=retrieved
    )
    if build.refusals:
        raise ValueError(f"the measurement build refused {dict(build.refusals)}")
    return build


def score_command(args) -> int:
    declared = committed_declaration()
    refuse_locked([LAST_DAY])
    validation = _load("scarcity_validation")
    levels = {name: read_levels(SNAPSHOT / f"{name}.csv", declared["snapshot"]["files"][f"{name}.csv"]) for name in PAIRS.values()}
    manifest = json.loads(validation.PUBLISHED_MANIFEST.read_text(encoding="utf-8"))
    artifacts = [
        load_snapshot_manifest(path)
        for root in validation.RAW_ROOTS
        for path in sorted((validation.SNAPSHOTS / root).glob("*/*.manifest.json"))
    ]
    cutoff = datetime.fromisoformat(manifest["build_cutoff"])
    decision = time.fromisoformat(manifest["decision_time"])
    retrieved = {artifact.sha256: artifact.retrieved_at for artifact in artifacts}
    columns = tuple(manifest["built_columns"]) + validation.EXTRA_COLUMNS
    document: dict = {
        "declaration": "metadata/h41_wednesday_levels_970.json",
        "snapshot_sha256": declared["snapshot"]["files"],
        "last_day": LAST_DAY.isoformat(),
    }
    with tempfile.TemporaryDirectory() as tmp, measurement_declaration():
        long_path = Path(tmp) / "measurement_point_in_time.csv"
        snapshot = build_point_in_time_snapshot(artifacts, long_path, registry_path=REGISTRY)
        original = load_point_in_time_panel(long_path)
        registry = load_source_registry(REGISTRY)
        # the baseline is the measurement panel, whose published columns must reproduce the published panel's digest
        published = build_daily_panel(
            original, registry, build_cutoff=cutoff, decision_time=decision,
            columns=tuple(manifest["built_columns"]), snapshot_retrieved_at=retrieved,
        )
        panel_path = Path(tmp) / "published_columns.csv"
        write_daily_panel(published, panel_path, source_shas=snapshot.source_shas)
        document["published_panel_sha256"] = verify_daily_panel(panel_path, validation.PUBLISHED_MANIFEST)
        base = _panel_rows(original, registry, cutoff, decision, columns, retrieved)
        rows = list(original)
        counts = {}
        for average, level in PAIRS.items():
            rows, counts[average] = substitute(rows, average, levels[level])
        alt = _panel_rows(rows, registry, cutoff, decision, columns, retrieved)
        document["substitution"] = counts
        if [r.date for r in base.observations] != [r.date for r in alt.observations]:
            # a dropped week can drop a row only if it was a required column; report rather than hide
            document["row_dates_differ"] = True
        by_series: Dict[str, Dict[date, float]] = {}
        for row in original:
            if row.series_id in PAIRS and row.ref_date <= LAST_DAY:
                by_series.setdefault(row.series_id, {})[row.ref_date] = row.value
        document["level_less_average_bn"] = {
            PAIRS[average]: _difference_summary(levels[PAIRS[average]], by_series[average]) for average in PAIRS
        }
        registry_dict = json.loads(REGISTRY.read_text(encoding="utf-8"))
        scored = {}
        document["state"] = {}
        for horizon in HORIZONS:
            old = {e.day: e.state for e in own_leg_states(
                base.observations, registry=registry_dict, decision_time=decision,
                minimum_history=MINIMUM_HISTORY, horizon=horizon, end=LAST_DAY)}
            new = {e.day: e.state for e in own_leg_states(
                alt.observations, registry=registry_dict, decision_time=decision,
                minimum_history=MINIMUM_HISTORY, horizon=horizon, end=LAST_DAY)}
            scored[horizon] = (old, new)
            document["state"][str(horizon)] = movement(old, new)
        old1, new1 = scored[1]
        days = sorted(old1)
        onset_days = pressure.onsets(base.observations, ONSET_BP, days)
        document["onsets"] = {
            "threshold_bp": ONSET_BP,
            "n": len(onset_days),
            "rows": [[d.isoformat(), old1[d], new1[d]] for d in onset_days],
            "changed": sum(old1[d] != new1[d] for d in onset_days),
        }
        document["kill_condition_met"] = (
            all(document["state"][str(h)]["changed"] == 0 for h in HORIZONS) and document["onsets"]["changed"] == 0
        )
    args.output.write_text(json.dumps(document, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    return 0


def report_command(args) -> int:
    doc = json.loads(args.score.read_text(encoding="utf-8"))
    out = ["| series | Wednesdays | mean | mean abs | 5th | median | 95th |", "|---|---|---|---|---|---|---|"]
    for name, s in doc["level_less_average_bn"].items():
        out.append(f"| {name} less its week average (USD bn) | {s['n']} | {s['mean']:.2f} | {s['mean_abs']:.2f} | {s['p05']:.2f} | {s['p50']:.2f} | {s['p95']:.2f} |")
    out += ["", "| horizon | scored days | change state | up | down | enter risky set | leave risky set |", "|---|---|---|---|---|---|---|"]
    for h, m in doc["state"].items():
        out.append(f"| {h} | {m['days']} | {m['changed']} | {m['up']} | {m['down']} | {m['enter_risky_set']} | {m['leave_risky_set']} |")
    out += ["", "Changed days at horizon 1 by year: " + ", ".join(f"{y}: {n}" for y, n in doc["state"]["1"]["by_year"].items()) + ".", ""]
    out += [f"Pressure onsets (> {doc['onsets']['threshold_bp']:.0f} bp, horizon 1): {doc['onsets']['n']}; state changes at {doc['onsets']['changed']}.", "",
            "| onset | state, week average | state, Wednesday level |", "|---|---|---|"]
    for day, before, after in doc["onsets"]["rows"]:
        out.append(f"| {day} | {before} | {after}{' (changed)' if before != after else ''} |")
    out += ["", f"Kill condition (no movement anywhere) met: **{doc['kill_condition_met']}**."]
    args.output.write_text("\n".join(out) + "\n", encoding="utf-8")
    return 0


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="command", required=True)
    score = sub.add_parser("score", help="the state from the week average and from the Wednesday level")
    score.add_argument("--output", type=Path, required=True)
    score.set_defaults(func=score_command)
    report = sub.add_parser("report", help="write the Markdown tables from a score file")
    report.add_argument("--score", type=Path, required=True)
    report.add_argument("--output", type=Path, required=True)
    report.set_defaults(func=report_command)
    args = parser.parse_args(argv)
    return int(args.func(args) or 0)


if __name__ == "__main__":
    raise SystemExit(main())
