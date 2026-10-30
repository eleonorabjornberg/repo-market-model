"""H10 prospective confirmation: the live job's onset step (#1322).

H10, prospective confirmation (milestone M3). Eleonora's ruling of 30 October 2026 (option (a'), ledger item 83): her
14 October ruling on liquidity finding #81 stands. The model repo's live job does the work, and repo-market-liquidity
runs no schedule. The interface is that repository's `docs/research/h10-live-interface.md`.

Each business day, after the day's H5 record is written, `run` does this on the panel the record was built from:

1. cuts the panel at the decision day (a row is real only if it is before it) and finds the onsets with the parent's own
   rule (`repo_model.onset.onset_flags`), cross-checked with `repo_model.pressure.onsets` at the same threshold. Nothing
   here re-implements either; a disagreement between the two raises `ValueError`;
2. attributes every onset from the registration date on that has no row yet, with
   `repo_liquidity.h10_live.attribute_onset(rows, rule, onset, report)` and `h10_apply.real_rule()`, reporting it on the
   last panel day, so an onset is reported as soon as it is flagged (plan Q7: within `report_days` panel days). An onset
   whose window closed without a row stays in the record as a "not attributable" miss, in the denominator;
3. checks every row against the registered values in `metadata/live_h10_pin.json` (the method digest, the parent
   commit, no parent override, a clean parent). A row that differs is refused: nothing is written and the job fails;
4. writes `h10/<day>.json`, labelled prospective, to the add-only `live-h10` branch. A `LookAheadError` (a lockbox tier)
   is recorded in that file and stops the day, with exit code `EXIT_LOOK_AHEAD`; it is never overridden. A day with no
   onset is recorded too, so a missing file means the job did not run.

The registered code is never liquidity's main. The workflow runs this script with `PYTHONPATH` set to a clean checkout
of repo-market-liquidity at `liquidity_commit` and a clean checkout of the model at `parent_commit`, both from the pin
manifest. `allow_unpinned_parent` is never passed. The switch to a later registration is a change of the manifest's
values, made only after her registration comment exists.

This module imports nothing of the model repo's `src/`: under that `PYTHONPATH` the `repo_model` it would find is the
registered parent's, not main's. The backend (`Backend`) is injected so that the tests need no liquidity checkout.

    PYTHONPATH=LIQ/src:PARENT/src python3 scripts/live_h10.py run --day YYYY-MM-DD --panel PANEL.csv --out-dir LIVE_H10
    python3 scripts/live_h10.py check-append --repo LIVE_H10 --day YYYY-MM-DD --base SHA

Standard library only, apart from the registered code it calls.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from datetime import date
from pathlib import Path
from typing import Callable, List, NamedTuple, Optional, Sequence

REPO = Path(__file__).resolve().parents[1]
PIN_PATH = REPO / "metadata" / "live_h10_pin.json"

H10_DIR = "h10"
LABEL = "prospective"
HYPOTHESIS = "H10"
EXIT_LOOK_AHEAD = 3

BOT_NAME = "github-actions[bot]"
BOT_EMAIL = "41898282+github-actions[bot]@users.noreply.github.com"
EMPTY_TREE = "4b825dc642cb6eb9a060e54bf8d69288fbee4904"

_COMMIT = re.compile(r"^[0-9a-f]{40}$")
_DIGEST = re.compile(r"^[0-9a-f]{64}$")


class DigestMismatch(ValueError):
    """A row is not the registered method's: its digest or parent differs, or the parent was overridden or dirty."""


def _look_ahead_error():
    """The registered parent's `LookAheadError`, or the tests' (the same class: they run under the same `repo_model`)."""

    from repo_model.splits import LookAheadError as parent_error

    return parent_error


class Backend(NamedTuple):
    """What the step calls: the panel loader, the onset rule, the as-of rule and `attribute_onset`, all injected."""

    load_rows: Callable
    onset_days: Callable
    rule: Callable
    attribute: Callable


def load_pin(path: Path = PIN_PATH) -> dict:
    pin = json.loads(Path(path).read_text(encoding="utf-8"))
    require_wellformed_pin(pin)
    return pin


def require_wellformed_pin(pin: dict) -> None:
    for key in ("liquidity_commit", "parent_commit"):
        if not _COMMIT.match(str(pin.get(key, ""))):
            raise ValueError(f"the H10 pin's {key} is not a full commit: {pin.get(key)!r}")
    if not _DIGEST.match(str(pin.get("method_digest", ""))):
        raise ValueError(f"the H10 pin's method_digest is not a sha256: {pin.get('method_digest')!r}")
    date.fromisoformat(pin["registered_on"])
    if not isinstance(pin.get("report_days"), int) or pin["report_days"] < 1:
        raise ValueError("the H10 pin's report_days is not a positive integer")


def check_row(row: dict, pin: dict) -> None:
    """A row is the registered method's, made from the registered parent, with no override.

    Raises:
        DigestMismatch: the row's `method_digest` or `parent_commit` is not the pin's, it was made with the
            parent override, or the imported parent was not the pin's commit or not clean.
    """

    if row.get("method_digest") != pin["method_digest"]:
        raise DigestMismatch(
            f"row for {row.get('onset')}: method_digest {row.get('method_digest')!r} is not the registered "
            f"{pin['method_digest']}"
        )
    if row.get("parent_commit") != pin["parent_commit"]:
        raise DigestMismatch(
            f"row for {row.get('onset')}: parent_commit {row.get('parent_commit')!r} is not the registered "
            f"{pin['parent_commit']}"
        )
    if row.get("parent_override") is not False:
        raise DigestMismatch(f"row for {row.get('onset')}: made with the parent override")
    if row.get("imported_parent_commit") != pin["parent_commit"] or row.get("imported_parent_clean") is not True:
        raise DigestMismatch(
            f"row for {row.get('onset')}: the imported parent was {row.get('imported_parent_commit')!r} "
            f"(clean: {row.get('imported_parent_clean')!r}), not a clean checkout of {pin['parent_commit']}"
        )


def agreed_onsets(flagged: Sequence[date], cross_check: Sequence[date]) -> List[date]:
    """The onset days of `repo_model.onset.onset_flags`, after checking `repo_model.pressure.onsets` gives the same.

    Raises:
        ValueError: the two sources disagree. Which one is the source is Eleonora's (the plan's Q6).
    """

    if list(flagged) != list(cross_check):
        raise ValueError(
            f"repo_model.onset and repo_model.pressure.onsets disagree: {sorted(set(flagged) ^ set(cross_check))}"
        )
    return list(flagged)


def report_deadline(dates: Sequence[date], onset: date, report_days: int = 10) -> Optional[date]:
    """The last panel day an onset can be reported on: `report_days` panel days after it. None while it is not yet a
    day of the panel."""

    index = list(dates).index(onset) + report_days
    return dates[index] if index < len(dates) else None


def _reported_onsets(out_dir: Path) -> set:
    reported = set()
    for path in sorted((Path(out_dir) / H10_DIR).glob("*.json")):
        for row in json.loads(path.read_text(encoding="utf-8")).get("rows", []):
            reported.add(row["onset"])
    return reported


def _miss_row(onset: date, report: date, pin: dict) -> dict:
    return {
        "onset": onset.isoformat(), "report_day": report.isoformat(), "status": "not attributable",
        "reason": f"the report window closed: the first panel day this job saw the onset was more than "
                  f"{pin['report_days']} panel days after it (plan Q7)",
        "under_bar": False, "beats_null": False, "counted": False,
    }


def run_day(day: date, panel: Path, out_dir: Path, backend: Backend, pin: dict) -> int:
    """One business day's step. Returns 0, or `EXIT_LOOK_AHEAD` when a lockbox refusal stopped the day.

    Raises:
        DigestMismatch: a row is not the registered method's. Nothing is written.
        ValueError: the day is already recorded, the pin is malformed, or the two onset sources disagree.
    """

    require_wellformed_pin(pin)
    target = Path(out_dir) / H10_DIR / f"{day.isoformat()}.json"
    if target.exists():
        raise ValueError(f"{target} exists: a day is recorded once")
    rows = [row for row in backend.load_rows(panel) if row.date < day]
    if not rows:
        raise ValueError(f"the panel has no row before {day}")
    dates = [row.date for row in rows]
    report = dates[-1]
    registered_on = date.fromisoformat(pin["registered_on"])
    in_scope = [d for d in backend.onset_days(rows) if d >= registered_on]
    reported = _reported_onsets(out_dir)
    todo = [d for d in in_scope if d.isoformat() not in reported]

    made: List[dict] = []
    stopped = None
    for position, onset in enumerate(todo):
        deadline = report_deadline(dates, onset, pin["report_days"])
        if dates.index(report) - dates.index(onset) > pin["report_days"]:
            row = _miss_row(onset, report, pin)
        else:
            try:
                with backend.rule() as rule:
                    row = backend.attribute(rows, rule, onset, report)
            except _look_ahead_error() as error:
                stopped = {
                    "onset": onset.isoformat(), "error": str(error), "type": type(error).__name__,
                    "not_attempted": [d.isoformat() for d in todo[position + 1:]],
                }
                break
            check_row(row, pin)
        made.append({**row, "label": LABEL, "report_deadline": deadline.isoformat() if deadline else None})

    record = {
        "version": 1, "label": LABEL, "hypothesis": HYPOTHESIS, "decision_day": day.isoformat(),
        "status": "look_ahead_error" if stopped else "ok",
        "panel_last_day": report.isoformat(), "panel_rows": len(rows),
        "onsets_found": [d.isoformat() for d in in_scope], "onsets_checked_from": pin["registered_on"],
        "registered": {key: pin[key] for key in ("liquidity_commit", "parent_commit", "method_digest",
                                                  "parent_panel_sha256", "registration", "registered_on",
                                                  "report_days")},
        "rows": made,
    }
    if stopped:
        record["stopped"] = stopped
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(record, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    return EXIT_LOOK_AHEAD if stopped else 0


def real_backend() -> Backend:
    """The registered code, imported from `PYTHONPATH`: liquidity at its commit over the parent at its pin."""

    from repo_liquidity import h10_apply, h10_live
    from repo_model import onset, pressure
    from repo_model.data import load_daily_panel

    def onset_days(rows):
        flags = onset.onset_flags(rows)
        flagged = [row.date for row, flag in zip(rows, flags) if flag]
        cross = pressure.onsets(rows, float(onset.ONSET_THRESHOLD_BP), [row.date for row in rows])
        return agreed_onsets(flagged, cross)

    return Backend(load_rows=load_daily_panel, onset_days=onset_days, rule=h10_apply.real_rule,
                   attribute=h10_live.attribute_onset)


def _git(repo: Path, *argv) -> str:
    done = subprocess.run(["git", *argv], cwd=repo, capture_output=True, text=True)
    if done.returncode != 0:
        raise ValueError(f"git {' '.join(argv)} failed in {repo}: {done.stderr.strip()}")
    return done.stdout.strip()


def require_add_only(repo: Path, base, day: date) -> None:
    """HEAD is one commit on top of `base` (`None`: a new branch), by the bot, that only adds `h10/<day>.json`.

    Raises:
        ValueError: more than one new commit, a merge, another author or committer, or any change other than adding
            that one file.
    """

    head = _git(repo, "rev-parse", "HEAD")
    fields = _git(repo, "show", "-s", "--format=%an%n%ae%n%cn%n%ce%n%P", head).split("\n")
    identity, parents = fields[:4], " ".join(fields[4:]).split()
    if parents != ([base] if base else []):
        raise ValueError(f"HEAD must be one commit on top of {base or 'nothing'}; its parents are {parents}")
    if identity != [BOT_NAME, BOT_EMAIL, BOT_NAME, BOT_EMAIL]:
        raise ValueError(f"{head} was not authored and committed by {BOT_NAME}: {identity}")
    lines = _git(repo, "diff", "--no-renames", "--name-status", base or EMPTY_TREE, head).splitlines()
    changes = [tuple(line.split("\t", 1)) for line in lines if line]
    if changes != [("A", f"{H10_DIR}/{day.isoformat()}.json")]:
        raise ValueError(f"{head} must only add {H10_DIR}/{day.isoformat()}.json; it changes {changes}")


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    commands = parser.add_subparsers(dest="command", required=True)
    run = commands.add_parser("run")
    run.add_argument("--day", required=True)
    run.add_argument("--panel", required=True, type=Path)
    run.add_argument("--out-dir", required=True, type=Path)
    run.add_argument("--pin", type=Path, default=PIN_PATH)
    check = commands.add_parser("check-append")
    check.add_argument("--repo", required=True, type=Path)
    check.add_argument("--day", required=True)
    check.add_argument("--base", default=None)
    args = parser.parse_args(argv)
    if args.command == "check-append":
        require_add_only(args.repo, args.base or None, date.fromisoformat(args.day))
        print(json.dumps({"append_only": True}))
        return 0
    try:
        code = run_day(date.fromisoformat(args.day), args.panel, args.out_dir, real_backend(), load_pin(args.pin))
    except DigestMismatch as error:
        print(f"H10 row refused, nothing written: {error}", file=sys.stderr)
        return 1
    print(json.dumps({"day": args.day, "exit": code}))
    return code


if __name__ == "__main__":
    sys.exit(main())
