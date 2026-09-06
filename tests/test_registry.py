import unittest
from datetime import time

from repo_model.registry import RegistryContractError, max_release_lag_days


def source(basis, calendar, days, available_time="12:00:00", **extra):
    return {
        "release_lag": {
            "basis": basis,
            "calendar": calendar,
            "days": days,
            "available_time": available_time,
            **extra,
        }
    }


class MaxReleaseLagDaysTests(unittest.TestCase):
    def test_ref_date_business_days_uses_declared_calendar_bound(self):
        registry = {
            "daily": source(
                "ref_date",
                "business_days",
                1,
                worst_case_calendar_days=6,
            )
        }

        self.assertEqual(
            max_release_lag_days(registry, ["daily"], decision_time=time(8)),
            6,
        )

    def test_record_date_calendar_days_adds_day_after_decision_time(self):
        registry = {
            "auction": source(
                "record_date",
                "calendar_days",
                2,
                available_time="16:00:00",
            )
        }

        self.assertEqual(
            max_release_lag_days(registry, ["auction"], decision_time=time(15)),
            3,
        )
        self.assertEqual(
            max_release_lag_days(registry, ["auction"], decision_time=time(16)),
            2,
        )

    def test_snapshot_retrieved_at_contributes_no_purge_with_available_at(self):
        registry = {
            "snapshot": source(
                "snapshot_retrieved_at",
                "none",
                0,
                available_time="00:00:00",
            ),
            "auction": source(
                "record_date",
                "calendar_days",
                2,
                available_time="10:00:00",
            ),
        }
        selected = {
            "snapshot": [{"available_at": "2026-01-02T12:00:00Z"}],
            "auction": [],
        }

        self.assertEqual(
            max_release_lag_days(registry, selected, decision_time=time(15)),
            2,
        )

    def test_snapshot_retrieved_at_raises_when_available_at_is_absent(self):
        registry = {
            "snapshot": source(
                "snapshot_retrieved_at",
                "none",
                0,
                available_time="00:00:00",
            )
        }

        with self.assertRaisesRegex(RegistryContractError, "available_at"):
            max_release_lag_days(
                registry,
                {"snapshot": [{"ref_date": "2026-01-02"}]},
                decision_time=time(15),
            )

        with self.assertRaisesRegex(RegistryContractError, "available_at"):
            max_release_lag_days(registry, ["snapshot"], decision_time=time(15))

    def test_only_selected_feature_sources_contribute_to_maximum(self):
        registry = {
            "used": source(
                "record_date",
                "calendar_days",
                2,
                available_time="10:00:00",
            ),
            "unused": source(
                "ref_date",
                "business_days",
                30,
                worst_case_calendar_days=35,
            ),
        }

        self.assertEqual(
            max_release_lag_days(registry, ["used"], decision_time=time(15)),
            2,
        )


if __name__ == "__main__":
    unittest.main()
