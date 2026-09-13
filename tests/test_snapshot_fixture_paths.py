"""The tracked snapshot fixtures must name their bytes in a portable form.

Milestone A's reproduction clause rests on a clone building the published panel
from `tests/fixtures/snapshots/funding_inputs/`, and that works only if each
fixture's sidecar names its bytes in a spelling that means the same thing in a
clone. Three spellings exist in this repository's history: the absolute path
`ingest._save_snapshot` wrote until A32; the repository-relative
`data/raw/<source>/<file>`, written by hand when the repository moved and by
`scripts/track_funding_inputs.py` into the tracked copy; and the raw-root
relative `<source>/<file>`, which A32 writes and which is the only one that
survives both a move and a clone.

The script accepts any of the three on the way in -- otherwise it would refuse
every sidecar written after A32, which is the defect this module was added for
-- and writes the raw-root relative form into the tracked copy.

Mutations recorded for this module (13 September 2026):

* the script writing `target.relative_to(ROOT)` again, with the fixtures
  re-tracked by it -- `test_every_tracked_sidecar_names_the_file_beside_it`
  fails with `AssertionError`, and
  `test_a_tracked_sidecar_resolves_where_the_tree_has_never_been` with it;
* `sidecar_path_forms` returning only the repository-relative spelling --
  `test_the_script_accepts_every_spelling_a_sidecar_has_carried` fails with
  `AssertionError`.
"""

from __future__ import annotations

import importlib.util
import json
import os
import pathlib
import shutil
import sys
import tempfile
import unittest

REPO_ROOT = pathlib.Path(__file__).resolve().parents[1]
FIXTURES = REPO_ROOT / "tests" / "fixtures" / "snapshots" / "funding_inputs"
SIDECARS = sorted(FIXTURES.glob("*/*.manifest.json"))
SIDECAR_SUFFIX = ".manifest.json"

if str(REPO_ROOT / "src") not in sys.path:
    sys.path.insert(0, str(REPO_ROOT / "src"))


def _script():
    """`scripts/track_funding_inputs.py` as a module, without running it."""

    spec = importlib.util.spec_from_file_location(
        "track_funding_inputs", REPO_ROOT / "scripts" / "track_funding_inputs.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class TrackedSidecarPathTests(unittest.TestCase):
    def test_there_are_fixtures_to_check(self):
        """A guard over a glob that matched nothing is not a guard."""

        self.assertGreater(len(SIDECARS), 0, FIXTURES)

    def test_every_tracked_sidecar_names_the_file_beside_it(self):
        for sidecar in SIDECARS:
            with self.subTest(sidecar=sidecar.relative_to(REPO_ROOT).as_posix()):
                recorded = json.loads(sidecar.read_text(encoding="utf-8"))["path"]
                beside = sidecar.name[: -len(SIDECAR_SUFFIX)]
                self.assertEqual(recorded, f"{sidecar.parent.name}/{beside}")

    def test_a_tracked_sidecar_resolves_where_the_tree_has_never_been(self):
        from repo_model.ingest import load_snapshot_manifest

        with tempfile.TemporaryDirectory() as tmp:
            root = pathlib.Path(tmp) / "elsewhere"
            shutil.copytree(FIXTURES, root)
            cwd = os.getcwd()
            os.chdir(tmp)
            try:
                copied = sorted(root.glob("*/*" + SIDECAR_SUFFIX))
                self.assertEqual(len(copied), len(SIDECARS))
                for sidecar in copied:
                    with self.subTest(sidecar=sidecar.name):
                        artifact = load_snapshot_manifest(sidecar)
                        self.assertEqual(artifact.path.parent, sidecar.parent)
                        self.assertTrue(artifact.path.is_file())
            finally:
                os.chdir(cwd)

    def test_the_script_accepts_every_spelling_a_sidecar_has_carried(self):
        module = _script()
        source = module.RAW / "nyfed_tgcr" / "a.json"
        forms = module.sidecar_path_forms(source)
        self.assertEqual(forms[0], "nyfed_tgcr/a.json")
        self.assertIn("data/raw/nyfed_tgcr/a.json", forms)
        self.assertIn(str(source), forms)
