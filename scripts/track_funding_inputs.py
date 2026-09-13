"""Copy the raw inputs of the published persistence run into tracked fixtures.

Milestone A's reproduction clause failed because a clone could not obtain the
bytes the panel was built from: the raw snapshots were gitignored, and a fresh
download returns the latest vintage, not the one the record scored. The user
decided (10 September) to commit the inputs themselves.

This script is the only way those fixtures are made, so what they are is a
command rather than a claim. It refuses unless

* the local panel's SHA-256 is the digest `docs/runs/persistence_funding.json`
  scored, and
* each digest in the record's `build_manifest.source_shas` is carried by
  exactly one raw snapshot under `data/raw/`.

It then copies each snapshot and its retrieval manifest under
`tests/fixtures/snapshots/funding_inputs/`, re-hashes the copy, and writes
`metadata/funding_panel_manifest.json`: the record's build manifest, plus the
panel's `sha256` and the tracked path of every input. Run from the integration
checkout, where the frozen panel lives:

    python3 scripts/track_funding_inputs.py
"""

from __future__ import annotations

import hashlib
import json
import pathlib
import shutil
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
RECORD = ROOT / "docs" / "runs" / "persistence_funding.json"
RAW = ROOT / "data" / "raw"
DEST = ROOT / "tests" / "fixtures" / "snapshots" / "funding_inputs"
OUT = ROOT / "metadata" / "funding_panel_manifest.json"
SIDECAR = ".manifest.json"


def sha256(path: pathlib.Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def sidecar_path_forms(source: pathlib.Path) -> tuple[str, ...]:
    """Every spelling of `source` a sidecar has carried, newest first.

    `ingest._save_snapshot` writes the path relative to the raw root since A32;
    before that it wrote an absolute path, and the sidecars repaired by hand
    after the repository moved carry the repository-relative form. All three
    name the same bytes, and this script must accept any of them or it refuses
    every snapshot fetched after A32. Only the first survives a clone, which is
    why it is the one written into the tracked copy.
    """

    return (
        source.relative_to(RAW).as_posix(),
        source.relative_to(ROOT).as_posix(),
        str(source),
    )


def main() -> int:
    record = json.loads(RECORD.read_text(encoding="utf-8"))
    panel_record = record["panel"]
    build = panel_record["build_manifest"]
    panel = ROOT / build["path"]
    digest = sha256(panel)
    if digest != panel_record["sha256"]:
        sys.exit(
            f"refusing: {build['path']} hashes to {digest}; the record scored "
            f"{panel_record['sha256']}"
        )

    by_digest: dict = {}
    for path in sorted(RAW.rglob("*")):
        if path.is_file() and not path.name.endswith(SIDECAR):
            by_digest.setdefault(sha256(path), []).append(path)

    inputs = []
    for source_digest in build["source_shas"]:
        found = by_digest.get(source_digest, [])
        if len(found) != 1:
            sys.exit(
                f"refusing: {len(found)} raw snapshots carry {source_digest}; "
                "exactly one is required"
            )
        source = found[0]
        target = DEST / source.relative_to(RAW)
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, target)
        sidecar = source.with_name(source.name + SIDECAR)
        # The sidecar's `path` is where `load_snapshot_manifest` reads the bytes
        # from. Copied verbatim it names wherever the original sat, which a
        # clone does not have. The tracked copy names the file beside it --
        # `<source>/<file>`, relative to the raw root the copy sits in -- which
        # is the one spelling that means the same thing in a clone, after a
        # move, and from any working directory. Nothing else in the sidecar
        # changes. See tests/test_snapshot_fixture_paths.py.
        retrieval_text = sidecar.read_text(encoding="utf-8")
        found = [
            form
            for form in sidecar_path_forms(source)
            if retrieval_text.count('"path": "%s"' % form) == 1
        ]
        if not found:
            sys.exit(
                f"refusing: {sidecar} does not name {source.relative_to(ROOT)} once, "
                "in any spelling a sidecar has carried"
            )
        target.with_name(target.name + SIDECAR).write_text(
            retrieval_text.replace(
                '"path": "%s"' % found[0],
                '"path": "%s"' % target.relative_to(DEST).as_posix(),
            ),
            encoding="utf-8",
        )
        if sha256(target) != source_digest:
            sys.exit(f"refusing: the copy at {target} does not hash to {source_digest}")
        retrieval = json.loads(sidecar.read_text(encoding="utf-8"))
        inputs.append(
            {
                "byte_count": target.stat().st_size,
                "path": target.relative_to(ROOT).as_posix(),
                "retrieved_at": retrieval["retrieved_at"],
                "sha256": source_digest,
                "source_id": retrieval["source_id"],
                "url": retrieval["url"],
            }
        )

    manifest = dict(build)
    manifest["sha256"] = digest
    manifest["inputs"] = inputs
    manifest["run_record"] = RECORD.relative_to(ROOT).as_posix()
    OUT.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"{len(inputs)} inputs tracked; panel {digest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
