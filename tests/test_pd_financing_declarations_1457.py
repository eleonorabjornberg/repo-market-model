"""The two declarations of `nyfed_pd_financing` agree on what they share (#1457, her ruling of 4 November 2026, option (a)).

One source id carries two declarations: the measurement registry entry (`metadata/sources_measurement.json`, #630,
corrected by #680) and the #1296 study's copy (`metadata/sources_pd_financing_1296.json`). Both are kept. Each names the
other; `check_declarations_agree` raises `ValueError`, naming both files, when they differ on the release lag, the
publication instant, the provider, a shared series, or the staleness bound.

Recorded mutation (the guard is a data guard, so the exception is `ValueError`): in
`metadata/sources_pd_financing_1296.json`, `proposed_registry_entry.release_lag.days` mutated from `6` to `5` (the same
mutation applied to a copy in `test_a_differing_lag_is_refused`). The test then raised `ValueError` naming both files;
with the check body replaced by `return`, that test failed with `AssertionError: ValueError not raised`.
"""
from __future__ import annotations

import copy
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MEASUREMENT_FILE = "metadata/sources_measurement.json"
STUDY_FILE = "metadata/sources_pd_financing_1296.json"
SOURCE_ID = "nyfed_pd_financing"
LAG_KEYS = ("available_time", "basis", "days", "timezone", "unit", "worst_case_calendar_days")


def _load(rel):
    return json.loads((ROOT / rel).read_text())


def check_declarations_agree(measurement_entry, study):
    """Raise ValueError, naming both files, if the two declarations of one source id disagree on a shared field."""
    from repo_model import data

    both = f"{MEASUREMENT_FILE} and {STUDY_FILE}"
    mine = study["proposed_registry_entry"]

    def refuse(what, a, b):
        raise ValueError(f"{SOURCE_ID} is declared in {both} and they disagree on {what}: {a!r} against {b!r}")

    for key in LAG_KEYS:
        a, b = measurement_entry["release_lag"].get(key), mine["release_lag"].get(key)
        if a != b:
            refuse(f"release_lag.{key} (the publication instant)", a, b)
    if measurement_entry["provider"] != mine["provider"]:
        refuse("provider", measurement_entry["provider"], mine["provider"])
    shared = set(measurement_entry["fields"]) & set(mine["fields"])
    if not shared:
        raise ValueError(f"{SOURCE_ID} is declared in {both} and they share no series")
    for name in shared:
        a, b = measurement_entry["field_frequencies"][name], mine["field_frequencies"][name]
        if a != b:
            refuse(f"the frequency of {name}", a, b)
    bound = f"({data.WEEKLY_CARRY_MAX_STALENESS_DAYS} days)"
    if bound not in measurement_entry["limitation"]:
        raise ValueError(f"{MEASUREMENT_FILE} does not state the staleness bound {bound} that {STUDY_FILE} reads")
    if "data.WEEKLY_CARRY_MAX_STALENESS_DAYS" not in study["same_release_as"]["carry_rule"]:
        raise ValueError(f"{STUDY_FILE} does not name data.WEEKLY_CARRY_MAX_STALENESS_DAYS as its carry rule")


class DeclarationsAgree(unittest.TestCase):

    def setUp(self):
        self.entry = _load(MEASUREMENT_FILE)[SOURCE_ID]
        self.study = _load(STUDY_FILE)

    def test_the_declarations_agree_as_they_stand(self):
        check_declarations_agree(self.entry, self.study)

    def test_each_declaration_names_the_other(self):
        pointer = self.study["same_release_as"]
        self.assertEqual((pointer["registry_file"], pointer["entry"]), (MEASUREMENT_FILE, SOURCE_ID))
        back = self.entry.get("same_release_as")
        self.assertIsNotNone(back, f"{MEASUREMENT_FILE} {SOURCE_ID} names no pointer to {STUDY_FILE}")
        self.assertEqual((back["study_file"], back["issue"]), (STUDY_FILE, 1296))
        self.assertTrue((ROOT / back["study_file"]).exists())

    def test_a_differing_lag_is_refused(self):
        study = copy.deepcopy(self.study)
        study["proposed_registry_entry"]["release_lag"]["days"] = 5
        with self.assertRaises(ValueError) as caught:
            check_declarations_agree(self.entry, study)
        self.assertIn(MEASUREMENT_FILE, str(caught.exception))
        self.assertIn(STUDY_FILE, str(caught.exception))

    def test_a_differing_instant_provider_and_frequency_are_refused(self):
        for path, value in ((("release_lag", "available_time"), "16:00"), (("provider",), "Elsewhere"),
                            (("field_frequencies", "PDSIRRA-UTSETTOT"), "daily")):
            study = copy.deepcopy(self.study)
            node = study["proposed_registry_entry"]
            for key in path[:-1]:
                node = node[key]
            node[path[-1]] = value
            with self.subTest(path=path), self.assertRaises(ValueError):
                check_declarations_agree(self.entry, study)

    def test_a_dropped_staleness_bound_is_refused(self):
        entry = copy.deepcopy(self.entry)
        entry["limitation"] = entry["limitation"].replace("(13 days)", "(90 days)")
        with self.assertRaises(ValueError) as caught:
            check_declarations_agree(entry, self.study)
        self.assertIn(MEASUREMENT_FILE, str(caught.exception))


if __name__ == "__main__":
    unittest.main()
