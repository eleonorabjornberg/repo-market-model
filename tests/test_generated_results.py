"""The published results block, the figure and the notebook are generated.

`README.md` now carries a results table, a status sentence and a figure. Every
figure in them comes out of `docs/runs/` and `docs/status.json`; none of it is
typed. That is not a style preference. Three documents in this repository once
published a test count that had been true months earlier, `REPRODUCIBILITY.md`
published a command that had not run for four commits, and Milestone A's exit
criterion was that no figure from a run record is transcribed into any Markdown
page. A results table is the most decay-prone claim a repository can publish: it
is stale the next time anything is scored.

So `scripts/emit_results.py` renders those artifacts and this module asserts that
what is committed is what it renders **now**, from the records as they stand. A
record that moves without the page moving is a red suite rather than a page
nobody re-read.

The notebook is here for the same reason. `notebooks/01_portfolio_walkthrough.ipynb`
is generated from `examples/walkthrough.py`'s own cells: a notebook committed
beside a script is a second copy of it, and the copy nobody executes is the one
that rots.

Mutation record
---------------

Run in a disposable copy under `$HOME`, `-B` with `PYTHONDONTWRITEBYTECODE=1`,
control green before and after all four (693 tests, OK). Every mutation was
confirmed present in the file before its result was read, and each was applied to
a restored copy rather than on top of the last, because two of them touch the
same file and stacking them would have credited a kill to the wrong edit.

1. One digit changed by hand inside the README's generated block, the mean
   absolute error, `3.14 bp` -> `3.15 bp`. Kills
   `test_every_generated_artifact_is_what_the_generator_renders` --
   `AssertionError: Lists differ: [] != ['README.md']`, and nothing else. This is
   the historical failure replayed: an edited number in a published table.
2. One `# %%` cell marker deleted from `examples/walkthrough.py`. Kills the same
   assertion, naming `notebooks/01_portfolio_walkthrough.ipynb` and **not**
   `README.md` -- `AssertionError`. The two artifacts fail independently, which
   is what makes the message worth reading.
3. `--feature` misspelled as `--features` in the walkthrough's `backtest`
   invocation. Kills `test_every_command_the_walkthrough_runs_parses` --
   `AssertionError`, naming the invocation -- and also the render-match
   assertion, because the notebook is generated from the same file. Two
   failures, one edit; the parse assertion is the one that names the defect.
   Recorded because the caught type and the failing type differ: argparse exits
   with `SystemExit(2)` rather than raising something a test can assert on, so
   the assertion converts it, and a test that forgot to convert would pass by
   never running.
4. An `outputs` entry and an `execution_count` added to a notebook code cell.
   Kills `test_the_notebook_stores_no_outputs` --
   `AssertionError: Lists differ: [] != [1]` -- and the render-match assertion
   with it.

**Known-soft, and recorded rather than dressed up.** Mutation 4 shows that the
third assertion is currently *carried* by the first: the generator never emits an
output, so any notebook carrying one already differs from the render, and no
input reaches the no-outputs assertion without tripping render-match first. It is
not wrong and it is not independent. It becomes independent the day the notebook
stops being generated from the script, which is exactly the day someone would
start committing outputs into it.

One mutation was considered and deliberately not run: retyping the generated
table by hand, byte for byte. It cannot fail, because what is checked is that the
committed bytes match the rendered bytes and not that a human did not type them.
That is the stated limit of this guard rather than a kill it can claim.
"""

from __future__ import annotations

import ast
import importlib.util
import json
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent


def load_generator():
    path = REPO_ROOT / "scripts/emit_results.py"
    spec = importlib.util.spec_from_file_location("emit_results", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def walkthrough_invocations():
    """Every `run(...)` call in the walkthrough, as an argv list.

    Read out of the source rather than by executing it: the point is that the
    published commands parse, and executing them to find out would make this a
    slow integration test that also happens to check argument spelling.
    """

    source = (REPO_ROOT / "examples/walkthrough.py").read_text(encoding="utf-8")
    tree = ast.parse(source)
    invocations = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        if not isinstance(node.func, ast.Name) or node.func.id != "run":
            continue
        argv = []
        for argument in node.args:
            if isinstance(argument, ast.Constant) and isinstance(argument.value, str):
                argv.append(argument.value)
            else:
                # A computed argument -- a report path under a temporary
                # directory. Its value cannot matter to whether the command
                # parses, and substituting a placeholder keeps the check on the
                # flags, which is where the rot was last time.
                argv.append("PLACEHOLDER")
        invocations.append(argv)
    return invocations


class GeneratedResultsTests(unittest.TestCase):
    def test_every_generated_artifact_is_what_the_generator_renders(self):
        generator = load_generator()
        artifacts = generator.rendered(
            generator.load(generator.PERSISTENCE),
            generator.load(generator.EXCEEDANCE),
        )
        stale = []
        for path, text in sorted(artifacts.items()):
            current = path.read_text(encoding="utf-8") if path.exists() else None
            if current != text:
                stale.append(str(path.relative_to(REPO_ROOT)))
        self.assertEqual(
            [], stale,
            "these are committed with content the generator no longer renders; "
            "run: python3 scripts/emit_results.py")

    def test_every_command_the_walkthrough_runs_parses(self):
        from repo_model.cli import build_parser

        invocations = walkthrough_invocations()
        self.assertGreater(len(invocations), 0,
                           "the walkthrough runs no commands; this guard would "
                           "pass by having nothing to check")
        broken = []
        for argv in invocations:
            try:
                build_parser().parse_args(argv)
            except SystemExit:
                broken.append(" ".join(argv))
        self.assertEqual([], broken,
                         "examples/walkthrough.py runs commands the parser refuses")

    def test_the_notebook_stores_no_outputs(self):
        generator = load_generator()
        document = json.loads(generator.NOTEBOOK.read_text(encoding="utf-8"))
        carrying = [
            index for index, cell in enumerate(document["cells"])
            if cell.get("outputs") or cell.get("execution_count") is not None
        ]
        self.assertEqual([], carrying,
                         "a committed notebook output is a result nobody re-ran")


if __name__ == "__main__":
    unittest.main()


def load_reproduction():
    path = REPO_ROOT / "scripts/reproduce_milestone_a.py"
    spec = importlib.util.spec_from_file_location("reproduce_milestone_a", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class MilestoneAReproductionTests(unittest.TestCase):
    """Milestone A's reproduction clause, held true on every run of the suite.

    `PLAN.md` may call the clause met only while this passes. It runs
    `scripts/reproduce_milestone_a.py`'s own `reproduce` -- `build` from the
    tracked inputs, `verify-panel` against `metadata/funding_panel_manifest.json`,
    `backtest` under the record's declaration -- in a temporary directory, and
    asserts that no figure the record publishes disagrees. Nothing it reads is
    gitignored, so a clone runs exactly this.

    It is also what keeps a published figure from moving silently: a change to
    the scoring path that alters what the persistence run produces turns this
    red, and the answer is a report and a re-scored record, not a tolerance.

    Mutation record
    ---------------

    Disposable copy under `$HOME`, `-B` with `PYTHONDONTWRITEBYTECODE=1`,
    control green before and after, each applied to a restored copy.

    1. `metrics.mae_bps` in `docs/runs/persistence_funding.json` moved by
       `1e-12`. Kills this test, `AssertionError` naming `metrics.mae_bps`
       with both values.
    2. One tracked input's bytes changed (a trailing newline appended to the
       `nyfed-sofr-rate` JSON). Kills this test, `AssertionError` "the
       reproduction did not run": `build` exits 2, refusing the snapshot
       against its own sidecar before any panel exists.
    3. `sha256` in `metadata/funding_panel_manifest.json` replaced by 64
       zeros. Kills this test at `verify-panel`, whose exit-2 message names
       both digests. The panel was rebuilt byte-identical; only the claim moved.

    When `dealer_treasury_position` gained its FR 2004 source (10 Sep), a
    default `build` gained a ninth, empty column and different bytes. The
    script now passes one `--column` per `built_columns` and does not compare
    `refused_columns` (see `_without_path`). Python 3.10.12, same recipe:

    4. The `--column` loop emptied. Kills this test, `AssertionError` "the
       reproduction did not run": `verify-panel` exits 2 on the digest.
    5. `refused_columns` compared again. Kills this test, `AssertionError`
       listing `panel.build_manifest.refused_columns.*`, present on one side
       only: the published build refused seven columns, a pinned one none.
    6. `built_columns` deleted from `metadata/funding_panel_manifest.json`.
       Kills this test, `AssertionError` "the reproduction did not run", the
       script's own refusal to fall back to a default build.

    **The control was red the first time**, and that was the finding. The
    tracked inputs' sidecars still named `data/raw/...` as the file to read, so
    `build` from the tracked inputs had only ever worked in the integration
    checkout, which also holds the originals. In the disposable copy -- which,
    like a clone, has no `data/raw/` -- it exited on a missing file. The
    sidecars now name their tracked location, and
    `scripts/track_funding_inputs.py` writes them that way.
    """

    def test_the_published_persistence_run_reproduces_from_tracked_inputs(self):
        import tempfile

        script = load_reproduction()
        with tempfile.TemporaryDirectory() as workdir:
            try:
                found = script.reproduce(workdir)
            except script.ReproductionError as exc:
                self.fail(f"the reproduction did not run: {exc}")
        self.assertEqual(
            [],
            found,
            "docs/runs/persistence_funding.json does not reproduce from the "
            "tracked inputs:\n  " + "\n  ".join(found),
        )


class ChallengerTableRefusalTests(unittest.TestCase):
    """The generated challenger table ranks only records scored alike.

    `emit_results.challenger_records` refuses a set of comparison records that
    were not scored on one panel, minimum history, purge and origin count, and
    refuses two records it cannot tell apart by declared settings or features.
    A table that silently mixed origin sets would rank numbers that are not
    comparable; one that silently collapsed two records would drop a row.

    Mutations (11 Sep 2026, each run against this class, then restored):

    1. `if len(keys) != 1:` -> `if False:` in `challenger_records`: the first
       test fails (no `RecordError` raised; the mixed set is ranked).
    2. `if not own:` -> `if False:`: the second test fails (no `RecordError`;
       both rows carry the same label).
    """

    def records_dir(self, mutate):
        import shutil
        import tempfile

        generator = load_generator()
        workdir = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, workdir)
        source = sorted(generator.RUNS.glob(generator.CHALLENGERS))[:2]
        for index, path in enumerate(source):
            record = json.loads(path.read_text(encoding="utf-8"))
            mutate(index, record)
            (workdir / path.name).write_text(json.dumps(record), encoding="utf-8")
        generator.RUNS = workdir
        return generator

    def test_records_scored_on_different_origins_are_refused(self):
        def mutate(index, record):
            if index == 1:
                record["folds"]["count"] += 1

        generator = self.records_dir(mutate)
        with self.assertRaises(generator.RecordError):
            generator.challenger_records()

    def test_two_records_that_cannot_be_told_apart_are_refused(self):
        def mutate(index, record):
            record["declaration"]["model_b"] = {"model": "arx", "features": ["spread_bps"]}

        generator = self.records_dir(mutate)
        with self.assertRaises(generator.RecordError):
            generator.challenger_records()
