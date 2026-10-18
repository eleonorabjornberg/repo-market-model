"""The nightly marking of the slowest test classes (#869, from #858).

A class decorated `@nightly` is skipped, with its reason printed, when `REPO_MODEL_SKIP_NIGHTLY`
is set. CI sets it on pull requests only; every push to `main`, the nightly schedule and a
local run leave it unset, so the whole suite still runs on main and a failure there turns main
red. `DECLARED` is the one list of marked classes: `tests/test_nightly_list.py` fails if a class
is marked without being listed here, or listed without being marked.

This is not `expectedFailure` and not a silent skip. No test is marked for being a leakage,
availability or staleness guard by default; adding to the list is a decision for Eleonora.
"""

import os
import unittest

SKIP_NIGHTLY = "REPO_MODEL_SKIP_NIGHTLY"

#: (module, class), the slowest classes named in #858 and `docs/pivot/ci-duration-848.md`, section 5.
DECLARED = (
    ("test_ml", "ScaledCrossConformalTests"),
    ("test_ml", "PartialCrossConformalTests"),
    ("test_power_study", "SimulationTests"),
    ("test_scoring_protocol_synthetic", "RecoveryTests"),
    ("test_cli_eval", "ExceedanceBacktestCommandTests"),
)


def nightly(cls):
    """Skip the class where the job declared it wants the pull-request set only."""
    return unittest.skipIf(
        bool(os.environ.get(SKIP_NIGHTLY)),
        "nightly class (slow); runs on every push to main and on the nightly schedule",
    )(cls)
