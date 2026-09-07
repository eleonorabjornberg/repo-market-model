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

- Python 3.9 or newer
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
PYTHONPATH=src python3 -m repo_model.cli backtest data/sample/daily_market.csv
```

The sample panel contains 25 synthetic rows. These commands verify parsing,
validation, chronological forecasting, and reporting only. Their numerical output
is not a research result.

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

Generated panels, journals, and model artifacts belong under `data/processed/` or
`artifacts/`; both paths are ignored by Git. Publish compact derived tables and
figures only after checking that their upstream provenance is recorded and that
the relevant data-provider terms permit redistribution.

## Interpretation boundary

Passing tests demonstrates that the declared software properties hold for the
cases exercised. It does not demonstrate forecast skill, economic causality, or
fitness for trading or risk-limit decisions. Those claims require historical
out-of-sample evidence and remain outside the repository's current status.
