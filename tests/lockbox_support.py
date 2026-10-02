"""The lockbox declaration the synthetic-panel test modules score under.

Many test modules build synthetic panels dated in 2026, inside the near-blind
tier of `docs/decisions/lockbox.md`. Those panels are not the published data,
and their dates carry meaning the tests assert on (exact days in messages,
weekdays, month ends), so they are not moved. Instead each such module scores
under `fixtures/lockbox_synthetic.json`: the same schema and loader, with its
locked tiers in 2100, beyond every synthetic panel. The guard still runs on
every scored day of those tests, against a declaration it validates.

The tracked declaration, `metadata/lockbox.json`, is exercised by
`test_lockbox.py`, which does not use this module: there the guard refuses the
same kind of synthetic 2026 panel at every scoring entry point.

A module opts in with

    from lockbox_support import setUpModule, tearDownModule  # noqa: F401

which unittest runs around that module's classes, in a full run and in a
class-targeted one alike. Nothing outside `tests/` reads this.
"""

from pathlib import Path
from unittest import mock

from repo_model import lockbox

SYNTHETIC_LOCKBOX = Path(__file__).resolve().parent / "fixtures" / "lockbox_synthetic.json"

_patch = mock.patch.object(lockbox, "DEFAULT_LOCKBOX", SYNTHETIC_LOCKBOX)


def setUpModule():
    _patch.start()


def tearDownModule():
    _patch.stop()
