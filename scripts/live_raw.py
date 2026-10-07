"""Archive the live record's raw inputs, and build the outcome panel only from the archive (#257).

The live record keeps each input's URL, retrieval time and SHA-256, but not its bytes, and
`REPRODUCIBILITY.md` says a later download may differ. So the record alone cannot reproduce
an outcome panel. This script closes that:

* `archive`: copies a day's raw root (the snapshots the day's record was built from, each with
  its `.manifest.json`) into `raw/<day>/` of the `live-raw` branch, after checking that every
  file's bytes equal the digest its manifest records, and writes `raw/<day>/index.json`. A day is
  archived once. `check-append` is the workflow's gate before the push: the new commit only
  adds files under `raw/<day>/`, as `github-actions[bot]`, on top of the branch's last commit.
  `live-raw` is append-only in the same way `live-log` is (`scripts/live_integrity.py`).
* `verify`: every archived file still hashes to its index entry, and nothing else is there.
  `verify-records` checks that every snapshot digest a live record carries is in its day's
  archive. A day with no archive (the log began before this) is listed, never counted as checked.
* `build-panel`: restores one archived day into a scratch raw root and builds the outcome panel
  from it with the repository's own `build`, with the columns and decision time the live
  record builds with. It writes the panel's own manifest (`<panel>.manifest.json`, by `build`)
  and a sidecar, `<panel>.provenance.json`: the build command, the build cutoff (the latest
  retrieval time in the archived day) and each input's path, digest, retrieval time and URL.
* `require_registered_panel`: what `scripts/live_score.py` calls before it reads a panel. A panel
  is registered only if it has its build manifest, its bytes equal the manifest's digest, it has
  its sidecar naming the same digest, and every source digest its manifest and sidecar name is
  an archived file whose bytes still match. Any other panel is refused (`ValueError`).

    PYTHONPATH=src python3 scripts/live_raw.py archive --raw-root RAW --day YYYY-MM-DD --out-dir LIVE_RAW
    PYTHONPATH=src python3 scripts/live_raw.py check-append --repo LIVE_RAW --day YYYY-MM-DD --base SHA
    PYTHONPATH=src python3 scripts/live_raw.py build-panel --archive-dir LIVE_RAW --day YYYY-MM-DD --panel P.csv
"""

from __future__ import annotations

import argparse
import contextlib
import hashlib
import io
import json
import re
import shlex
import shutil
import subprocess
import sys
import tempfile
from datetime import date, datetime
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))

from repo_model.data import verify_daily_panel  # noqa: E402

RAW_DIR = "raw"
INDEX = "index.json"
MANIFEST_SUFFIX = ".manifest.json"
PROVENANCE_SUFFIX = ".provenance.json"
#: The outcome panel is built with the columns and decision time `live_record.build` builds with.
DECISION_TIME = "16:00:00"
RAW_DAY = re.compile(r"^\d{4}-\d{2}-\d{2}(-[a-z]+)?$")


def _script(name):
    spec = spec_from_file_location(f"{name}_for_raw", REPO / "scripts" / f"{name}.py")
    module = module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _sha256(path: Path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def _name(day: date, label=None) -> str:
    """The directory a day's archive lives in: `YYYY-MM-DD`, or `YYYY-MM-DD-<label>` for a second root of that day."""

    return day.isoformat() if label is None else f"{day.isoformat()}-{label}"


def _day_dir(root: Path, day: date, label=None) -> Path:
    return Path(root) / RAW_DIR / _name(day, label)


def _manifests(root: Path) -> list:
    return sorted(Path(root).glob("*/*" + MANIFEST_SUFFIX))


def archive_day(raw_root: Path, out_dir: Path, day: date, label=None) -> Path:
    """Copy `raw_root`'s snapshots into `out_dir/raw/<day>/`, with an index of their digests.

    `label` names a second root fetched for the same day (the blind gap's, fetched at
    scoring time: `raw/<day>-gap/`).

    Every data file's bytes must equal the digest its manifest records; the index is
    written last, so a day with an index is complete.

    Raises:
        ValueError: no manifests under `raw_root`, bytes that differ from a manifest's
            digest, a manifest whose path leaves its source directory, or a day that is
            already archived. Nothing is written in any of these cases.
    """

    manifests = _manifests(raw_root)
    if not manifests:
        raise ValueError(f"no raw snapshot manifests under {raw_root}")
    target = _day_dir(out_dir, day, label)
    if target.exists():
        raise ValueError(f"{target} exists: a day is archived once")
    entries, copies = [], []
    for path in manifests:
        manifest = json.loads(path.read_text(encoding="utf-8"))
        relative = manifest["path"]
        data_path = Path(raw_root) / relative
        if Path(relative).parts[:1] != (path.parent.name,) or ".." in Path(relative).parts:
            raise ValueError(f"{path}: manifest path {relative!r} is not in its source directory")
        data = data_path.read_bytes()
        digest = hashlib.sha256(data).hexdigest()
        if digest != manifest["sha256"]:
            raise ValueError(
                f"{data_path} hashes to {digest}, but its manifest records {manifest['sha256']}"
            )
        entries.append({
            "path": relative, "sha256": digest, "byte_count": len(data),
            "source_id": manifest["source_id"], "retrieved_at": manifest["retrieved_at"],
            "url": manifest["url"],
        })
        copies.append((data_path, relative))
        copies.append((path, relative + MANIFEST_SUFFIX))
    for source, relative in copies:
        destination = target / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, destination)
    entries.sort(key=lambda entry: entry["path"])
    (target / INDEX).write_text(
        json.dumps({"day": day.isoformat(), "label": label, "files": entries}, indent=1,
                   sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return target


def _read_index(directory: Path) -> dict:
    path = Path(directory) / INDEX
    if not path.exists():
        raise ValueError(f"{directory} has no {INDEX}: the day is not archived")
    return json.loads(path.read_text(encoding="utf-8"))


def verify_day(directory: Path) -> list:
    """Every file in an archived day hashes to its index entry, and nothing else is there.

    Returns the index's entries.

    Raises:
        ValueError: a missing, altered or unlisted file.
    """

    directory = Path(directory)
    entries = _read_index(directory)["files"]
    expected = {INDEX}
    for entry in entries:
        expected.add(entry["path"])
        expected.add(entry["path"] + MANIFEST_SUFFIX)
        path = directory / entry["path"]
        if not path.exists():
            raise ValueError(f"{path} is listed in {directory / INDEX} and missing")
        if _sha256(path) != entry["sha256"]:
            raise ValueError(f"{path} no longer hashes to its index digest {entry['sha256']}")
    present = {path.relative_to(directory).as_posix() for path in directory.rglob("*") if path.is_file()}
    if present != expected:
        raise ValueError(f"{directory} holds files its index does not list: {sorted(present - expected)}")
    return entries


def archived_days(archive_dir: Path) -> list:
    root = Path(archive_dir) / RAW_DIR
    return sorted(path.name for path in root.iterdir() if path.is_dir()) if root.is_dir() else []


def verify_archive(archive_dir: Path) -> list:
    """`verify_day` for every archived day. Returns the days, oldest first."""

    days = archived_days(archive_dir)
    for day in days:
        verify_day(Path(archive_dir) / RAW_DIR / day)
    return days


def restore_day(archive_dir: Path, day: date, raw_root: Path, label=None) -> list:
    """Rebuild a raw root from one archived day, after verifying it. Returns the index's entries.

    Raises:
        ValueError: the day is not archived or fails `verify_day`.
    """

    source = _day_dir(archive_dir, day, label)
    if not source.is_dir():
        raise ValueError(f"{_name(day, label)} is not archived under {archive_dir}")
    entries = verify_day(source)
    for entry in entries:
        for relative in (entry["path"], entry["path"] + MANIFEST_SUFFIX):
            destination = Path(raw_root) / relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source / relative, destination)
    return entries


def _git(repo: Path, *argv) -> str:
    done = subprocess.run(["git", *argv], cwd=repo, capture_output=True, text=True)
    if done.returncode != 0:
        raise ValueError(f"git {' '.join(argv)} failed in {repo}: {done.stderr.strip()}")
    return done.stdout.strip()


def require_add_only(repo: Path, base, day: date, label=None) -> None:
    """HEAD is one commit on top of `base` (`None`: a new branch), by the bot, that only adds files under `raw/<day>/`.

    The workflow runs this after committing and before `git push`.

    Raises:
        ValueError: more than one new commit, a merge, another author or committer, or any
            change other than adding files under `raw/<day>/`.
    """

    integrity = _script("live_integrity")
    head = _git(repo, "rev-parse", "HEAD")
    fields = _git(repo, "show", "-s", "--format=%an%n%ae%n%cn%n%ce%n%P", head).split("\n")
    identity, parents = fields[:4], " ".join(fields[4:]).split()
    if parents != ([base] if base else []):
        raise ValueError(f"HEAD must be one commit on top of {base or 'nothing'}; its parents are {parents}")
    if identity != [integrity.BOT_NAME, integrity.BOT_EMAIL, integrity.BOT_NAME, integrity.BOT_EMAIL]:
        raise ValueError(f"{head} was not authored and committed by {integrity.BOT_NAME}: {identity}")
    parent = base or integrity.EMPTY_TREE
    lines = _git(repo, "diff", "--no-renames", "--name-status", parent, head).splitlines()
    changes = [tuple(line.split("\t", 1)) for line in lines if line]
    prefix = f"{RAW_DIR}/{_name(day, label)}/"
    if not changes or any(status != "A" or not path.startswith(prefix) for status, path in changes):
        raise ValueError(f"{head} must only add files under {prefix}; it changes {changes}")


def verify_records(archive_dir: Path, live_dir: Path) -> dict:
    """Every snapshot digest a live record carries is in its day's archive.

    Returns `{"archived": [...], "unarchived": [...]}`, the record days checked and the days
    with no archive (the log began before it; those are listed, not counted as checked).

    Raises:
        ValueError: a record carries a digest its day's archive does not hold.
    """

    archived, unarchived = [], []
    for path in sorted((Path(live_dir) / "live").glob("*.json")):
        record = json.loads(path.read_text(encoding="utf-8"))
        day = record["decision_day"]
        directory = _day_dir(archive_dir, date.fromisoformat(day))
        if not directory.is_dir():
            unarchived.append(day)
            continue
        held = {entry["sha256"] for entry in verify_day(directory)}
        missing = [snap["sha256"] for snap in record["inputs"]["snapshots"] if snap["sha256"] not in held]
        if missing:
            raise ValueError(f"{path.name} carries input digests the archive does not hold: {missing}")
        archived.append(day)
    return {"archived": archived, "unarchived": unarchived}


def build_argv(raw_root: Path, panel: Path, cutoff: str) -> list:
    """`repo_model.cli build`'s arguments: the live record's columns and decision time."""

    live = _script("live_record")
    argv = ["build", "--raw-root", str(raw_root), "--output", str(panel),
            "--build-cutoff", cutoff, "--decision-time", DECISION_TIME]
    for column in live.BUILD_COLUMNS:
        argv += ["--column", column]
    return argv


def build_panel(archive_dir: Path, day: date, panel: Path, label=None) -> dict:
    """Build the outcome panel from one archived day, and write its provenance sidecar.

    The build cutoff is the latest retrieval time in the day: the build sees exactly what
    the archive holds. Returns the sidecar's content.

    Raises:
        ValueError: the day is not archived, or fails verification.
    """

    from repo_model.cli import main as cli_main

    panel = Path(panel)
    with tempfile.TemporaryDirectory() as scratch:
        entries = restore_day(archive_dir, day, Path(scratch) / "raw", label)
        cutoff = max(datetime.fromisoformat(entry["retrieved_at"]) for entry in entries).isoformat()
        argv = build_argv(Path(scratch) / "raw", panel, cutoff)
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            code = cli_main(argv)
        if code != 0:
            raise ValueError(f"repo_model.cli {' '.join(argv)} exited {code}")
    shown = build_argv(Path("RAW_ROOT"), Path("PANEL"), cutoff)
    sidecar = {
        "raw_day": _name(day, label),
        "build_command": "PYTHONPATH=src python3 -m repo_model.cli " + shlex.join(shown),
        "build_cutoff": cutoff,
        "panel_sha256": _sha256(panel),
        "inputs": [{key: entry[key] for key in ("path", "sha256", "retrieved_at", "url")}
                   for entry in entries],
    }
    Path(str(panel) + PROVENANCE_SUFFIX).write_text(
        json.dumps(sidecar, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    return sidecar


def require_registered_panel(panel: Path, archive_dir: Path) -> dict:
    """Refuse any outcome panel that `build_panel` did not build from archived bytes.

    Returns the provenance sidecar. A panel is registered only if all hold: it has its build
    manifest and its bytes equal the manifest's digest; it has its sidecar and the sidecar names
    the same digest; the sidecar's day is archived and verifies; every input digest the sidecar
    names, and every source digest the build manifest names, is an archived file.

    Raises:
        ValueError: any of the above fails (`DataContractError` for the panel's own digest).
    """

    panel = Path(panel)
    manifest_path = Path(str(panel) + MANIFEST_SUFFIX)
    if not manifest_path.exists():
        raise ValueError(f"{panel} has no build manifest {manifest_path.name}: it is not a registered panel")
    verify_daily_panel(panel, manifest_path)
    sidecar_path = Path(str(panel) + PROVENANCE_SUFFIX)
    if not sidecar_path.exists():
        raise ValueError(f"{panel} has no {sidecar_path.name}: it was not built by `live_raw.py build-panel`")
    sidecar = json.loads(sidecar_path.read_text(encoding="utf-8"))
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if sidecar.get("panel_sha256") != manifest["sha256"]:
        raise ValueError(f"{sidecar_path.name} names panel {sidecar.get('panel_sha256')}, not {manifest['sha256']}")
    if not isinstance(sidecar.get("raw_day"), str) or not RAW_DAY.match(sidecar["raw_day"]):
        raise ValueError(f"{sidecar_path.name} names no archived day: {sidecar.get('raw_day')!r}")
    entries = verify_day(Path(archive_dir) / RAW_DIR / sidecar["raw_day"])
    archived = {entry["sha256"] for entry in entries}
    for digest in [item["sha256"] for item in sidecar["inputs"]] + list(manifest.get("source_shas", [])):
        if digest not in archived:
            raise ValueError(f"{panel} was built from {digest}, which the archive of {sidecar['raw_day']} does not hold")
    if not manifest.get("source_shas"):
        raise ValueError(f"{manifest_path.name} names no source digests: there is nothing to check against the archive")
    return sidecar


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    commands = parser.add_subparsers(dest="command", required=True)
    one = commands.add_parser("archive")
    one.add_argument("--raw-root", required=True, type=Path)
    one.add_argument("--day", required=True)
    one.add_argument("--out-dir", required=True, type=Path)
    one.add_argument("--label", default=None, help="a second root of the same day, e.g. gap")
    check = commands.add_parser("check-append")
    check.add_argument("--repo", required=True, type=Path)
    check.add_argument("--day", required=True)
    check.add_argument("--base", default=None)
    check.add_argument("--label", default=None)
    verify = commands.add_parser("verify")
    verify.add_argument("--archive-dir", required=True, type=Path)
    verify.add_argument("--live-dir", type=Path, default=None)
    panel = commands.add_parser("build-panel")
    panel.add_argument("--archive-dir", required=True, type=Path)
    panel.add_argument("--day", required=True)
    panel.add_argument("--panel", required=True, type=Path)
    panel.add_argument("--label", default=None)
    args = parser.parse_args(argv)
    if args.command == "archive":
        path = archive_day(args.raw_root, args.out_dir, date.fromisoformat(args.day), args.label)
        print(json.dumps({"archived": str(path)}))
    elif args.command == "check-append":
        require_add_only(args.repo, args.base or None, date.fromisoformat(args.day), args.label)
        print(json.dumps({"append_only": True}))
    elif args.command == "verify":
        out = {"days": verify_archive(args.archive_dir)}
        if args.live_dir is not None:
            out["records"] = verify_records(args.archive_dir, args.live_dir)
        print(json.dumps(out))
    else:
        sidecar = build_panel(args.archive_dir, date.fromisoformat(args.day), args.panel, args.label)
        print(json.dumps({"panel": str(args.panel), "panel_sha256": sidecar["panel_sha256"]}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
