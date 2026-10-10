"""The two-of-three alarm (#458, `scripts/vote_2_of_3.py`): a day is flagged when at least two of the three
voters flag it, each at the cut-off the judge chose for that voter."""

import importlib.util
import math
import unittest
from datetime import date
from pathlib import Path

from repo_model import pressure_judge as pj

_spec = importlib.util.spec_from_file_location(
    "vote_2_of_3", Path(__file__).resolve().parents[1] / "scripts" / "vote_2_of_3.py")
vote = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(vote)

DAYS = tuple(date(2020, 1, d) for d in (1, 2, 3, 6))


def forecast(name, probabilities, cutoff, days=DAYS):
    return pj.Forecast(
        name=name, horizon=1, dates=days, probabilities={5.0: tuple(probabilities), 10.0: tuple(probabilities)},
        cutoffs={5.0: (cutoff,) * len(days), 10.0: (cutoff,) * len(days)}, cutoff_rule="x",
    )


class Declared:
    thresholds = (5.0, 10.0)
    sha256 = "x"


class VoteTests(unittest.TestCase):
    def flags(self, parts):
        chosen = {(p.name, 1): p for p in parts}
        made = vote.vote_forecast(Declared, [p.name for p in parts], 1, chosen)
        return [1 if p >= c else 0 for p, c in zip(made.probabilities[5.0], made.cutoffs[5.0])]

    def test_two_of_three_flag_one_of_three_does_not(self):
        # each voter has its own cut-off: a probability at its own cut-off flags, below does not
        a = forecast("a", [0.5, 0.5, 0.1, 0.1], 0.5)
        b = forecast("b", [0.9, 0.1, 0.9, 0.1], 0.9)
        c = forecast("c", [0.1, 0.1, 0.1, 0.1], 0.2)
        self.assertEqual(self.flags([a, b, c]), [1, 0, 0, 0])
        c = forecast("c", [0.3, 0.3, 0.3, 0.1], 0.2)
        self.assertEqual(self.flags([a, b, c]), [1, 1, 1, 0])

    def test_a_voter_that_flags_nothing_cannot_vote(self):
        a = forecast("a", [1.0] * 4, 0.5)
        b = forecast("b", [1.0] * 4, math.inf)
        c = forecast("c", [1.0] * 4, math.inf)
        self.assertEqual(self.flags([a, b, c]), [0, 0, 0, 0])

    def test_voters_on_different_days_are_refused(self):
        a = forecast("a", [1.0] * 4, 0.5)
        b = forecast("b", [1.0] * 4, 0.5)
        c = forecast("c", [1.0] * 3, 0.5, days=DAYS[:3])
        with self.assertRaises(ValueError):
            self.flags([a, b, c])

    def test_the_declaration_names_three_distinct_voters_it_can_load(self):
        voters = vote.voters_of()
        self.assertEqual(voters, ["two_part_gbm", "ngboost_laplace", "hierarchical_logistic"])
        declaration = vote.composed_declaration(voters)
        for name in (*voters, vote.VOTE):
            self.assertEqual(declaration.candidates[name]["role"], "candidate")


if __name__ == "__main__":
    unittest.main()
