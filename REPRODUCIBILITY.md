# Reproducibility

This repository separates two kinds of reproducibility:

1. **Code-path reproducibility:** anyone can run the tests, synthetic audit, and
   synthetic baseline from a clean clone.
2. **Empirical reproducibility:** a historical result must additionally identify
   immutable raw snapshots, their manifests, the panel build configuration, the
   Git revision, and the evaluation journal.

The first is available now. The second will accompany the first research results;
the repository does not yet publish those results.

## Environment

- Python 3.9 or Python 3.10, declared as a range in `pyproject.toml` and stated
  nowhere else that is not checked against it. Both were run whole before the
  range was widened to admit them. 3.11 rejects the package at import.
- no third-party Python packages
- commands run from the repository root

Record the code revision before running an experiment:

```bash
git rev-parse HEAD
python3 --version
```

## Verify a clean clone

Run the complete suite with bytecode caching disabled:

```bash
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src \
  python3 -B -m unittest discover -s tests
```

The expected result is `OK`. No test count appears here, and none should: a
number transcribed into prose is stale at the next commit, and a stale count on
the page that tells you how to reproduce the repository is the same failure this
project is about. CI runs the suite with `-v` on every push; that log is the
count.

Two properties of the run are stable and do matter. `unittest` exits non-zero on
an *unexpected success* as well as on a failure, so an `expectedFailure`
placeholder standing in for an unbuilt interface turns the build red the moment
that interface lands, and stays red until the same pull request replaces it with
behavioral conformance tests. There are no such placeholders at present. Skip
counts vary with whether `data/raw/` snapshots are present in the checkout and
carry no information; never write one into an acceptance criterion.

Exercise the public synthetic workflow:

```bash
PYTHONPATH=src python3 -m repo_model.cli audit data/sample/daily_market.csv
PYTHONPATH=src python3 -m repo_model.cli backtest data/sample/daily_market.csv \
  --registry metadata/sources.json \
  --feature spread_bps \
  --decision-time 16:00 \
  --model persistence \
  --report /tmp/persistence_sample.json
```

The sample panel contains 25 synthetic rows. These commands verify parsing,
validation, chronological forecasting, and reporting only. Their numerical output
is not a research result.

`backtest` requires all four arguments and has no defaults for them. That is
deliberate: the registry and the feature set decide the purge, the decision time
decides what a builder could have known, and the report path is where the numbers
go — a default for any of them would be an unstated experimental choice. For real
numbers on a fetched panel rather than on this fixture, see "The published runs"
below.

> This block was wrong from `1cd7a9f` until 8 September 2026: it published a
> command that had not run for four commits, and a reader following this page hit
> an argument error on the second line they were told to type.
> `tests/test_docs_freshness.py` catches a transcribed count or a stale date and
> cannot catch this, because the rot was in a command's arguments rather than in a
> digit. **A published command is a claim, and it decays exactly like a published
> number.** A guard that executes the commands the published documents publish is
> worth a block of its own and does not exist yet.

## Acquire public source snapshots

The current command line exposes New York Fed SOFR and FRED macro downloads:

```bash
PYTHONPATH=src python3 -m repo_model.cli fetch nyfed-sofr
PYTHONPATH=src python3 -m repo_model.cli fetch fred-macro
```

Downloads are written beneath `data/raw/` with a retrieval timestamp, SHA-256
digest, and manifest. The directory is ignored by Git because raw responses may be
large and because provider terms still apply.

Network responses can be revised or republished. Re-running a download later is
therefore not guaranteed to reproduce an earlier byte stream. Exact empirical
reproduction requires the original snapshot and its manifest. In particular, the
FRED adapter currently acquires the latest revised vintage rather than a complete
historical-vintage archive.

## Requirements for a reportable experiment

A result is reportable only when its run record identifies:

- the Git commit;
- every raw snapshot digest and retrieval timestamp;
- the source-registry and stress-threshold versions;
- the point-in-time panel build and quality report;
- the feature set and decision cutoff;
- the model configuration and random seed, where applicable;
- the rolling-origin split and registry-derived purge gap; and
- any event-window checksum and append-only evaluation-journal entry.

## The published runs

`docs/runs/` holds the frozen funding panel's build manifest and the run records
measured on it. The panel itself is derived from gitignored raw snapshots and is
not tracked; the manifest is, so a cloner receives the digests of the snapshots it
was built from, the build cutoff, the columns built and refused, the holes and the
count of reported dates that are not rows.

**No figure from those runs is transcribed here, or into any Markdown page in this
repository.** The record files are the publication. A number typed into a document
is the same drift as a hand-written date, and `tests/test_docs_freshness.py`
refuses both. To see the numbers, read the JSON. To reproduce them, rebuild the
panel from the snapshot digests the manifest names and re-run the command each
record's `declaration` block states.

Generated panels, journals, and model artifacts belong under `data/processed/` or
`artifacts/`; both paths are ignored by Git. Publish compact derived tables and
figures only after checking that their upstream provenance is recorded and that
the relevant data-provider terms permit redistribution.

## Interpretation boundary

Passing tests demonstrates that the declared software properties hold for the
cases exercised. It does not demonstrate forecast skill, economic causality, or
fitness for trading or risk-limit decisions. Those claims require historical
out-of-sample evidence and remain outside the repository's current status.

This is an academic exercise, and the boundary above is the point of it rather than a
disclaimer attached to it. A reader who reproduces the code path has reproduced the
argument this repository is currently making: that the pipeline does not let
information reach a forecast before it was available. Reproducing a *result* is a
different act, and the requirements listed above are what it would take.
