"""Pin the legacy day-type reading (`turn_days.IN_FORCE` and `b2_pool.IN_FORCE` False) for a test module that reproduces legacy figures (#1161).

Once the month-end turn record (#1135) is in force, every reader of `turn_days.reporting_day_type` (B2's pools, the
mean-reversion level, `anchor_day_type`, `ranking_daytype`, B1', the risk dates) labels `turn`, `quarter_end_turn` and
`year_end`. A test module whose oracle or whose recorded figures are the legacy labels (`month_end`, `quarter_end`: the simulator
of `benchmark_simulation`, the hand reproductions of the published panel, the declared counts of a published study) keeps
them by setting this module's two functions as its own `setUpModule` and `tearDownModule`:

    import legacy_day_types
    setUpModule, tearDownModule = legacy_day_types.setUpModule, legacy_day_types.tearDownModule

The in-force reading is tested in `test_month_end_turn_1135.py`, `test_b2_pool_1155.py` and `test_turn_day_labels_959.py`.
"""

from repo_model import turn_days

_readings = []


def setUpModule():
    # `turn_days.legacy_reading` (#1206) turns off both switches: B2's thin-pool fallback (#1155, #1198) is chained over the
    # turn labels, so the legacy reading is plain B2 as well
    reading = turn_days.legacy_reading()
    reading.__enter__()
    _readings.append(reading)


def tearDownModule():
    while _readings:
        _readings.pop().__exit__(None, None, None)
