"""`repo_model.masked_rule`: the mask on undeclared columns and the closed list of frozen exemptions (#1565).

Audit item 1 of #1554 (Eleonora, 11 November 2026, option a "mask") and her ruling of 12 November 2026 on #1579
(option 2): a frozen declaration reads through the old unmasked observation, listed by name in `FROZEN_READ_EXEMPTIONS`;
every other fit is masked; the frozen checksums and the live pin do not move.

Recorded mutations (CPython 3.11, `-B`, disposable copy, each confirmed applied by diff and reverted):

1. The mask removed -- in `MaskedInformationRule.observation`, `return DailyObservation(unmasked.date, values)` ->
   `return unmasked`. Killed by `test_an_undeclared_column_arrives_as_none`:
   `AssertionError: 1010.0 is not None : sofr_volume`.
2. The exemption widened to everything -- in `is_frozen_read`, `any(entry.features == declared ...)` -> `True`. Killed by
   `test_a_declaration_off_the_list_is_masked`: `AssertionError: True is not false`.
3. The exemption removed -- in `MaskedInformationRule.observation`, `if is_frozen_read(self.features):` -> `if False:`.
   Killed by `test_a_frozen_declaration_reads_the_unmasked_observation`:
   `AssertionError: DailyObservation(...) != DailyObservation(...)` (the masked row against the plain one).
"""

from __future__ import annotations

import importlib
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from repo_model import baseline, event_eval, masked_rule
from repo_model.asof import InformationRule
from repo_model.masked_rule import FROZEN_READ_EXEMPTIONS, MaskedInformationRule, is_frozen_read

import test_asof as ta


def masked(features):
    return MaskedInformationRule(ta.REGISTRY, tuple(features), decision_time=ta.DECISION)


class MaskTests(unittest.TestCase):
    def test_an_undeclared_column_arrives_as_none(self):
        """Declared and target columns pass; no other column does (mutation 1)."""

        scored = ta.index_of(ta.date(2026, 1, 22))
        current = masked(["spread_bps", "reserve_balances", "tga"])
        info = current.information_set(ta.DATES, scored)
        observed = current.observation(ta.ROWS, info)
        self.assertEqual(
            observed.values["reserve_balances"],
            ta.ROWS[ta.read_of(info, "reserve_balances").row].values["reserve_balances"],
        )
        self.assertAlmostEqual(observed.spread_bps, float(info.anchor))
        for column in ta.ROWS[info.anchor].values:
            if column in ("sofr", "iorb", "reserve_balances", "tga"):
                self.assertIsNotNone(observed.values[column], column)
            else:
                self.assertIsNone(observed.values[column], column)

    def test_a_declaration_off_the_list_is_masked(self):
        """A declaration that is not frozen is masked (mutation 2)."""

        scored = ta.index_of(ta.date(2026, 1, 22))
        current = masked(["spread_bps", "reserve_balances"])
        self.assertFalse(is_frozen_read(current.features))
        observed = current.observation(ta.ROWS, current.information_set(ta.DATES, scored))
        self.assertIsNone(observed.values["sofr_volume"])

    def test_a_frozen_declaration_reads_the_unmasked_observation(self):
        """A listed declaration is handed exactly what `InformationRule` hands (mutation 3)."""

        scored = ta.index_of(ta.date(2026, 1, 22))
        current = masked(["spread_bps"])
        self.assertTrue(is_frozen_read(current.features))
        info = current.information_set(ta.DATES, scored)
        observed = current.observation(ta.ROWS, info)
        plain = InformationRule(ta.REGISTRY, ("spread_bps",), decision_time=ta.DECISION)
        self.assertEqual(observed, plain.observation(ta.ROWS, info))
        self.assertEqual(observed.values["sofr_volume"], ta.ROWS[info.anchor].values["sofr_volume"])

    def test_order_does_not_matter(self):
        published = tuple(FROZEN_READ_EXEMPTIONS["published_distribution_h1"].features)
        self.assertTrue(is_frozen_read(tuple(reversed(published))))

    def test_the_fits_take_the_masked_rule(self):
        self.assertIs(baseline.InformationRule, MaskedInformationRule)
        self.assertIs(event_eval.InformationRule, MaskedInformationRule)


class FrozenListTests(unittest.TestCase):
    def test_the_list_is_closed_and_pinned(self):
        self.assertEqual(
            sorted(FROZEN_READ_EXEMPTIONS),
            [
                "direct_logistic_sofr_p1", "dynamic_logit", "persistence_and_leap_labels",
                "published_distribution_h1", "published_distribution_h2_5", "scarcity_calendar",
                "stacked_combiner", "v1_1",
            ],
        )
        with self.assertRaises(TypeError):
            FROZEN_READ_EXEMPTIONS["another"] = None  # type: ignore[index]

    def test_every_entry_is_derived_from_the_frozen_declarations(self):
        """The entries equal the feature sets the checksummed declarations carry."""

        ft = importlib.import_module("final_test_preregistration")
        lr = importlib.import_module("live_record")

        wanted = {frozenset(features) for name, features in ft._FEATURES.items()}
        wanted.add(frozenset(ft.CRPS_FEATURES))
        wanted.add(frozenset(("spread_bps",)))
        wanted.update(frozenset(lr.published_features(h)) for h in range(1, 6))
        wanted.add(frozenset(ft._published_distribution()["features"]))
        self.assertEqual({entry.features for entry in FROZEN_READ_EXEMPTIONS.values()}, wanted)


if __name__ == "__main__":
    unittest.main()
