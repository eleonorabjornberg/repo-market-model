# Reproducibility

This repository separates two kinds of reproducibility:

1. **Code-path reproducibility:** anyone can run the tests, synthetic audit, and
   synthetic baseline from a clean clone.
2. **Empirical reproducibility:** a historical result must additionally identify
   immutable raw snapshots, their manifests, the panel build configuration, the
   Git revision, and the evaluation journal.

The first is available now. The second is available for the persistence benchmark:
its raw inputs are tracked, and one command rebuilds the panel from them, checks the
bytes against the published digest and re-derives every figure in
`docs/runs/persistence_funding.json` exactly — see "Reproduce the published persistence
run" below. The other records in `docs/runs/` were scored on the same panel and are
re-run from their own `declaration` blocks; no script re-checks them yet.

## Environment

- Python 3.9, Python 3.10 or Python 3.11, declared as a range in `pyproject.toml`
  and stated nowhere else that is not checked against it. Each was run whole before
  the range admitted it. 3.12 runs everything except the exact reproduction of the
  published record: its `sum()` rounds floats differently, and the figures move in
  their last digits.
- no third-party Python packages for any published record; the optional `ml` extra
  (numpy, scikit-learn) is needed only by `src/repo_model/ml.py`
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
PYTHONPATH=src python3 -m repo_model.cli compare data/sample/daily_market.csv \
  --registry metadata/sources.json \
  --model-a persistence --feature-a spread_bps \
  --model-b arx --feature-b spread_bps --feature-b sofr_volume \
  --decision-time 16:00 \
  --report /tmp/compare_sample.json
PYTHONPATH=src python3 -m repo_model.cli exceedance-backtest \
  --panel data/sample/daily_market.csv \
  --thresholds metadata/stress_thresholds.json \
  --registry metadata/sources.json \
  --feature spread_bps \
  --decision-time 16:00 \
  --model climatology \
  --report /tmp/climatology_sample.json
```

`compare` declares each side separately and defaults neither: a defaulted side
would score persistence against itself under the other model's name and report a
difference of zero with a degenerate interval, which is the shape of a passing
sanity check. Its record states the sign convention as a sentence, because a
signed difference with no statement of direction is a number half its readers
read as the opposite result. It also carries each origin's two losses and their
difference under `comparison.per_origin`, earliest first, so which days a result
comes from is read off the record rather than re-run.

The paired loss is `--loss absolute-error` unless `--loss crps` is given, and the
record names which. Absolute error reads only each side's centre, so two models
that share a point rule and differ in their intervals score a difference of exactly
zero under it -- the same degenerate shape, reached honestly. `--loss crps` scores
each side's quantile forecast and separates them.

`--feature-b sofr_volume` is not decoration. `iorb` is constant across these
twenty-five rows, and an ARX declared over it is refused for a rank-deficient
design -- correctly, and it is the first thing a reader who swaps the regressor
will hit. The other panel columns draw on sources whose snapshots do not ship,
so the declaration is refused before any fold is built.

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
reproduction requires the original snapshot and its manifest; a manifest's URL
records the request and does not always reproduce the bytes (the Treasury auctions
request has no upper date bound). In particular, the
FRED adapter currently acquires the latest revised vintage rather than a complete
historical-vintage archive.

## Requirements for a reportable experiment

A result is reportable only when its run record identifies:

- the Git commit;
- every raw snapshot digest and retrieval timestamp;
- the source-registry and stress-threshold versions;
- the point-in-time panel build and quality report;
- the feature set and decision cutoff;
- the model configuration and random seed, where applicable, and for a model
  fitted with the `ml` extra the numpy and scikit-learn versions it fitted with.
  A comparison's bootstrap seed is derived from the panel, both models, their
  feature sets and the decision time, not from a model's settings: two records
  that differ only in a setting share a resample stream, and that is decided;
- the rolling-origin split and registry-derived purge gap; and
- any event-window checksum and append-only evaluation-journal entry.

## The published runs

`docs/runs/` holds the frozen funding panel's build manifest and the run records
measured on it. The panel itself is not tracked; the manifest is, so a cloner receives the digests of the snapshots it
was built from, the build cutoff, the columns built and refused, the holes and the
count of reported dates that are not rows. The raw snapshots behind the published
persistence run are tracked under `tests/fixtures/snapshots/funding_inputs/`, and
`metadata/funding_panel_manifest.json` binds them, and the panel's own bytes, by digest.
A run scored on a panel whose manifest carries that digest binds its record to the
manifest by it (`build_manifest_binding.kind` is `digest`); the published records predate
the digest and bind by extent.

**No figure from those runs is transcribed here, or into any Markdown page in this
repository.** The record files are the publication. A number typed into a document
is the same drift as a hand-written date, and `tests/test_docs_freshness.py`
refuses both. To see the numbers, read the JSON. To reproduce them, follow the next
section.

## Reproduce the published persistence run

From a clean clone, with no network and no gitignored file:

```bash
python3 scripts/reproduce_milestone_a.py
```

It exits 0 only if every figure the record publishes is re-derived exactly, and
otherwise names each one that moved. It writes nothing into the checkout.
`tests/test_generated_results.py` runs the same function, so the suite goes red the
day a change to the scoring path moves a published figure. The three steps it runs
are the published commands, and can be typed by hand:

```bash
PYTHONPATH=src python3 -m repo_model.cli build \
  --raw-root tests/fixtures/snapshots/funding_inputs \
  --output /tmp/funding_panel.csv \
  --build-cutoff 2026-09-08T21:31:42+00:00 \
  --decision-time 16:00:00 \
  --column sofr --column iorb --column sofr_volume --column sofr_p25 \
  --column sofr_p75 --column tgcr --column bgcr --column treasury_settlement
PYTHONPATH=src python3 -m repo_model.cli verify-panel /tmp/funding_panel.csv \
  --manifest metadata/funding_panel_manifest.json
PYTHONPATH=src python3 -m repo_model.cli backtest /tmp/funding_panel.csv \
  --registry metadata/sources.json \
  --feature spread_bps \
  --decision-time 16:00 \
  --model persistence \
  --minimum-history 20 \
  --report /tmp/persistence_funding.json
```

The build cutoff, decision time and columns are the ones
`metadata/funding_panel_manifest.json` records, and the columns are the load-bearing one:
a source joining the registry adds a column to a build that names none, and that panel is
different bytes. Flag order does not matter; the panel carries columns in declared order.
The record's refused columns are not compared, since they describe what the original build
was asked for rather than what the panel holds. `verify-panel` has no default manifest on purpose: the panel's own
`.manifest.json` was written by the build being checked, so agreeing with it proves only
that one build agrees with itself.

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
