#!/usr/bin/env python3
"""Run the whole pipeline on the shipped sample panel, in one command.

    python3 examples/walkthrough.py

No installation, no arguments, no network, nothing to configure: the package is
standard library only and `data/sample/daily_market.csv` ships in the repository.
The four commands below are **the same four `REPRODUCIBILITY.md` publishes**, run
in-process rather than as subprocesses, so a reader can see the audit, the
backtest, the paired comparison and the exceedance run produce artifacts end to
end before deciding whether any of it is worth reading closely.

**Its numbers are not a result.** The sample panel is twenty-five synthetic rows
and exists to make the workflow executable. The real numbers are in
`docs/runs/`, and the README's Key-findings block is generated from them.

`notebooks/01_portfolio_walkthrough.ipynb` is generated from this file's own
`# %%` cells by `scripts/emit_results.py`, and the suite checks that it still
matches, so the rendered notebook cannot drift from the script that is actually
executed. Edit this file; never the notebook.
"""

# %% [markdown]
# # Repo Market Model — end-to-end walkthrough
#
# This notebook is generated from `examples/walkthrough.py`. Edit the script, not
# the notebook.
#
# It runs four commands against the twenty-five-row synthetic sample panel that
# ships with the repository: an audit, a purged rolling-origin backtest of the
# persistence benchmark, a paired comparison of two models at one set of origins,
# and a threshold-exceedance backtest. Nothing here is a research result — it is
# the machinery, executed, on data chosen to make it executable.

# %%
import json
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent if "__file__" in dir() else Path.cwd()
sys.path.insert(0, str(ROOT / "src"))

from repo_model.cli import main as cli  # noqa: E402

OUT = Path(tempfile.mkdtemp(prefix="repo-model-walkthrough-"))
PANEL = "data/sample/daily_market.csv"
REGISTRY = "metadata/sources.json"


def run(*argv):
    """One CLI invocation, from the repository root, refusing a nonzero exit."""
    import os

    cwd = os.getcwd()
    os.chdir(ROOT)
    try:
        print("$ python3 -m repo_model.cli " + " ".join(argv))
        code = cli(list(argv))
    finally:
        os.chdir(cwd)
    if code != 0:
        raise SystemExit("command exited %d; the walkthrough stops here" % code)
    return code


def report(name):
    with (OUT / name).open(encoding="utf-8") as handle:
        return json.load(handle)


# %% [markdown]
# ## 1. Audit the panel
#
# Validation, missingness and the accounting identities, before anything is
# forecast. An identity a source declares and fails is a refusal, not a warning.

# %%
run("audit", PANEL)

# %% [markdown]
# ## 2. Backtest the persistence benchmark
#
# Purged rolling origin: every forecast is made from rows a builder could have
# held at the declared decision time, and the rows within the purge window of the
# scored date are withheld from training. The registry decides the purge; it is
# not a parameter of this script.

# %%
run("backtest", PANEL,
    "--registry", REGISTRY,
    "--feature", "spread_bps",
    "--decision-time", "16:00",
    "--model", "persistence",
    "--report", str(OUT / "persistence_sample.json"))

persistence = report("persistence_sample.json")
metrics = persistence["metrics"]
print("\nforecast origins        %d" % persistence["folds"]["count"])
print("mean absolute error     %.3f bp" % metrics["mae_bps"])
print("CRPS                    %.3f bp" % metrics["crps_bps"])
print("interval coverage       %.3f at a nominal %.2f"
      % (metrics["interval_coverage"], metrics["interval_probability"]))

# %% [markdown]
# ## 3. Compare two models at one set of origins
#
# Each side is declared separately and neither is defaulted: a defaulted side
# would score persistence against itself under the other model's name and report
# a difference of zero with a degenerate interval, which is the shape of a
# passing sanity check.
#
# `--feature-b sofr_volume` is not decoration. `iorb` is constant across these
# twenty-five rows, so an ARX declared over it is refused for a rank-deficient
# design.

# %%
run("compare", PANEL,
    "--registry", REGISTRY,
    "--model-a", "persistence", "--feature-a", "spread_bps",
    "--model-b", "arx", "--feature-b", "spread_bps", "--feature-b", "sofr_volume",
    "--decision-time", "16:00",
    "--report", str(OUT / "compare_sample.json"))

comparison = report("compare_sample.json")
print("\n" + json.dumps(comparison.get("comparison", comparison), indent=2)[:900])

# %% [markdown]
# ## 4. Score threshold exceedance
#
# The stress thresholds are declared in `metadata/stress_thresholds.json`, not
# chosen here. The model is a climatology, which is the reference every later
# skill score is measured against.

# %%
run("exceedance-backtest",
    "--panel", PANEL,
    "--thresholds", "metadata/stress_thresholds.json",
    "--registry", REGISTRY,
    "--feature", "spread_bps",
    "--decision-time", "16:00",
    "--model", "climatology",
    "--report", str(OUT / "climatology_sample.json"))

exceedance = report("climatology_sample.json")
print("\nthreshold  base rate   Brier  skill")
for key in sorted(exceedance["metrics"]["by_tau"], key=float):
    tau = exceedance["metrics"]["by_tau"][key]
    skill = tau.get("brier_skill_score")
    # A skill score this fixture cannot support is absent from the record rather
    # than reported as zero, and the record says why. Printing "n/a" and the
    # reason is the whole point: on twenty-five rows most of these thresholds are
    # never crossed, and a zero there would read as "no skill" instead of
    # "nothing to score".
    print("%6.0f bp  %9.3f  %6.4f  %s"
          % (tau["tau_bp"], tau["base_rate"], tau["brier"],
             ("%+.3f" % skill) if skill is not None
             else "n/a  " + "; ".join(sorted(tau.get("unavailable") or []))))

# %% [markdown]
# ## What this did and did not show
#
# It showed that the pipeline runs end to end from a clean clone with no
# installation: parsing, validation, chronological forecasting, paired
# comparison, exceedance scoring, and a provenance-carrying report for each run.
#
# It showed nothing about whether the model forecasts anything. Twenty-five
# synthetic rows cannot, and the reports above say so in their own provenance.
# For measured numbers on the real panel see `docs/runs/` and the README's
# Key-findings section, which is generated from those records rather than typed.

# %%
print("\nreports written to %s" % OUT)
